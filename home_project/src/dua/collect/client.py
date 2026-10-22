"""Talking to hosted LLM APIs.

One client for both providers, because the archived records need the same
envelope either way. Every call records the request, response, HTTP status,
latency, timestamp, and -- for OpenRouter -- the upstream provider that served
it. That last field matters: OpenRouter routed the DeepSeek-R1 run across eight
providers, so "temperature 0" does not by itself explain a given answer.

**Keys come from the environment, never from a file in this repository.**
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 5


class MissingAPIKeyError(RuntimeError):
    def __init__(self, env_var: str):
        super().__init__(
            f"{env_var} is not set. Copy .env.example to .env and fill it in, "
            f"or export {env_var} in your shell. Keys are never stored in this "
            "repository."
        )


@dataclass
class CallResult:
    """One API call, with everything needed to audit it later."""

    success: bool
    content: str | None
    error: str | None
    status_code: int | None
    latency_ms: int
    timestamp: str
    model_requested: str
    model_served: str | None = None
    provider: str | None = None
    raw_response: dict[str, Any] | None = None
    request_body: dict[str, Any] | None = field(default=None, repr=False)

    def as_record(self) -> dict[str, Any]:
        return {
            "api_success": self.success,
            "llm_answer": self.content,
            "api_error": self.error,
            "api_status_code": self.status_code,
            "api_response_time_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "model_requested": self.model_requested,
            "model_served": self.model_served,
            "api_provider": self.provider,
            "api_response_full": json.dumps(self.raw_response, ensure_ascii=False)
            if self.raw_response else None,
        }


class ResponseCache:
    """Disk cache keyed by a hash of (endpoint, model, request body).

    Every API stage is resumable: re-running a killed job costs nothing for
    the calls that already landed. The cache is under ``data/cache/`` and is
    gitignored -- it is a convenience, not an artifact.
    """

    def __init__(self, root: str | Path, namespace: str):
        self.root = Path(root) / namespace
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(endpoint: str, model: str, body: dict) -> str:
        payload = json.dumps({"endpoint": endpoint, "model": model, "body": body},
                             sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        # Two-level fan-out; a flat directory of 9,108 files is slow to list.
        return self.root / key[:2] / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def put(self, key: str, value: dict) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)


class ChatClient:
    """Minimal OpenAI-compatible chat client with retries and caching."""

    ENDPOINTS = {
        "openai": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY"),
        "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "OPENROUTER_API_KEY"),
    }

    def __init__(self, access: str, *, timeout: int = DEFAULT_TIMEOUT,
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 cache: ResponseCache | None = None):
        if access not in self.ENDPOINTS:
            raise KeyError(f"unknown access path {access!r}; expected one of "
                           f"{sorted(self.ENDPOINTS)}")
        self.access = access
        self.endpoint, self.env_var = self.ENDPOINTS[access]
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache = cache
        self._key: str | None = None

    @property
    def api_key(self) -> str:
        if self._key is None:
            key = os.environ.get(self.env_var)
            if not key:
                raise MissingAPIKeyError(self.env_var)
            self._key = key
        return self._key

    def _headers(self) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.access == "openrouter":
            # Optional attribution headers; harmless if the referer is unset.
            headers["HTTP-Referer"] = os.environ.get("OPENROUTER_REFERER", "")
            headers["X-Title"] = "dreaming-up-authors"
        return headers

    def call(self, prompt: str, model: str, *, temperature: float = 0.0,
             max_tokens: int | None = None, use_cache: bool = True) -> CallResult:
        import requests

        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        cache_key = ResponseCache.key(self.endpoint, model, body)
        if use_cache and self.cache:
            hit = self.cache.get(cache_key)
            if hit is not None:
                return CallResult(**hit)

        last: CallResult | None = None
        for attempt in range(self.max_retries):
            started = time.time()
            now = datetime.now(UTC).isoformat(timespec="seconds")
            try:
                response = requests.post(self.endpoint, headers=self._headers(),
                                         json=body, timeout=self.timeout)
                latency = int((time.time() - started) * 1000)
                if response.status_code == 200:
                    data = response.json()
                    content = (data.get("choices", [{}])[0]
                               .get("message", {}).get("content") or "")
                    result = CallResult(
                        success=True, content=content.strip(), error=None,
                        status_code=200, latency_ms=latency, timestamp=now,
                        model_requested=model, model_served=data.get("model"),
                        provider=data.get("provider"), raw_response=data,
                        request_body=body,
                    )
                    if self.cache:
                        self.cache.put(cache_key, {k: v for k, v in result.__dict__.items()})
                    return result
                last = CallResult(
                    success=False, content=None,
                    error=f"HTTP {response.status_code}: {response.text[:300]}",
                    status_code=response.status_code, latency_ms=latency,
                    timestamp=now, model_requested=model, request_body=body,
                )
                # 4xx other than 429 will not fix themselves.
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    return last
            except Exception as exc:  # noqa: BLE001 - record and retry
                last = CallResult(
                    success=False, content=None, error=f"{type(exc).__name__}: {exc}",
                    status_code=None, latency_ms=int((time.time() - started) * 1000),
                    timestamp=now, model_requested=model, request_body=body,
                )
            time.sleep(min(2**attempt, 30))

        return last  # type: ignore[return-value]
