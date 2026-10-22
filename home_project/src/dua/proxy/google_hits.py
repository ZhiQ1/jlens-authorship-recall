"""Stage C2: web presence via Google search hit counts (Section 3.1).

Builds a quoted query of the title and every author name, and records what
BrightData's Google Search API reports.

**The cached responses are the artifact, not the code.** Hit counts drift daily
and the API is paid and rate limited, so nobody re-running this gets the
paper's numbers; the cache under ``data/cache/google/`` is what makes Section
3.1 checkable.

Short titles match unrelated content -- ``"Is this tragic or comic" "H. White"``
returns 49,300,000 hits for a zero-citation paper -- so papers above the 80th
percentile of hits *within their own citation bin* are dropped, taking 6,048
down to 4,185.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Iterable, Iterator
from pathlib import Path

from dua.config import load_config


def build_query(title: str, authors: list[str]) -> str:
    """Quoted title followed by each quoted author name."""
    parts = [f'"{title}"'] + [f'"{a}"' for a in authors if a]
    return " ".join(parts)


def query_length(query: str) -> int:
    """Character length of the query, the sensitivity measure of Section 3.1."""
    return len(query)


_HITS = re.compile(r"(?:About\s+)?([\d,.  ]+)\s+results", re.I)


def parse_hit_count(payload: dict | str) -> int | None:
    """Pull a result count out of a BrightData SERP response.

    BrightData returns either parsed JSON with a numeric total or raw HTML,
    depending on the request. Both shapes are handled; an unparseable response
    returns ``None`` and is recorded as a failure rather than as zero hits,
    because zero is a meaningful value here.
    """
    if isinstance(payload, dict):
        for key in ("total_results", "results_count", "total", "number_of_results"):
            value = payload.get(key)
            if isinstance(value, int | float):
                return int(value)
        general = payload.get("general")
        if isinstance(general, dict):
            for key in ("results_cnt", "total_results"):
                if isinstance(general.get(key), int | float):
                    return int(general[key])
        payload = json.dumps(payload)
    match = _HITS.search(str(payload))
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


class GoogleHitsClient:
    """BrightData SERP client with a mandatory on-disk response cache."""

    def __init__(self, cache_dir: str | Path | None = None, *, zone: str | None = None,
                 timeout: int = 60, max_retries: int = 4):
        cfg = load_config()
        self.endpoint = cfg["proxy"]["brightdata_endpoint"]
        self.cache_dir = Path(cache_dir or (cfg.path("cache") / "google"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.zone = zone or os.environ.get("BRIGHTDATA_ZONE", "serp")
        self.timeout = timeout
        self.max_retries = max_retries

    def _path(self, query: str) -> Path:
        digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
        return self.cache_dir / digest[:2] / f"{digest}.json"

    def cached(self, query: str) -> dict | None:
        path = self._path(query)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def fetch(self, query: str) -> dict:
        """Return the cached response, or call the API and cache it."""
        hit = self.cached(query)
        if hit is not None:
            return hit

        import requests

        token = os.environ.get("BRIGHTDATA_TOKEN")
        if not token:
            raise RuntimeError(
                "BRIGHTDATA_TOKEN is not set. Section 3.1 cannot be re-collected "
                "without it; the shipped cache under data/cache/google/ is the "
                "reproducible artifact."
            )

        from urllib.parse import quote_plus

        body = {
            "zone": self.zone,
            "url": f"https://www.google.com/search?q={quote_plus(query)}&brd_json=1",
            "format": "raw",
        }
        record: dict = {"query": query, "query_length": query_length(query)}
        for attempt in range(self.max_retries):
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=body, timeout=self.timeout,
            )
            if response.status_code == 200:
                try:
                    payload = response.json()
                except ValueError:
                    payload = response.text
                record.update({"ok": True, "hits": parse_hit_count(payload), "raw": payload})
                break
            record.update({"ok": False, "status": response.status_code,
                           "error": response.text[:300]})
            time.sleep(min(2**attempt, 30))

        path = self._path(query)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        return record


def collect(papers: Iterable[dict], client: GoogleHitsClient | None = None,
            *, offline: bool = False) -> Iterator[dict]:
    """Yield one hit-count record per paper.

    ``offline=True`` reads only the cache and yields ``hits=None`` for misses,
    so the analysis can run on the shipped cache without a token.
    """
    client = client or GoogleHitsClient()
    for paper in papers:
        query = build_query(paper["title"], paper["authors"])
        response = client.cached(query) if offline else client.fetch(query)
        yield {
            "paper_id": paper["paper_id"],
            "citations": paper["citations"],
            "citation_bin": paper["citation_bin"],
            "field": paper.get("field"),
            "query": query,
            "query_length": query_length(query),
            "hits": (response or {}).get("hits"),
            "cached": response is not None,
        }
