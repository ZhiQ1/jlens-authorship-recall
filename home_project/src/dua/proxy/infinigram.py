"""Stage C3: corpus occurrence via Infini-gram (Section 3.2).

Infini-gram answers n-gram count queries against trillion-token pretraining
corpora, which is as close as an outsider gets to measuring prevalence in
training data directly. The query joins the capitalized title with the first
author only, since author order and formatting vary between sources.

Both corpora and both capitalization variants are collected, because the
paper's conclusion is that the counts are *sensitive* to capitalization --
which is the evidence for preferring citation count as the proxy.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Iterable, Iterator
from pathlib import Path

from dua.config import load_config

CORPORA = {"olmo2": "infinigram_index_olmo", "redpajama": "infinigram_index_redpajama"}
VARIANTS = ("capitalize", "camel")


def capitalize_variant(text: str) -> str:
    """Sentence case: first letter upper, the rest untouched."""
    return text[:1].upper() + text[1:] if text else text


def camel_variant(text: str) -> str:
    """Title case on every word, the second variant reported in Appendix A3.2."""
    return " ".join(w[:1].upper() + w[1:] if w else w for w in text.split())


def build_query(title: str, first_author: str, variant: str = "capitalize") -> str:
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {VARIANTS}")
    transform = capitalize_variant if variant == "capitalize" else camel_variant
    return f"{transform(title)} AND {transform(first_author)}"


class InfiniGramClient:
    """Infini-gram API client with an on-disk response cache."""

    def __init__(self, cache_dir: str | Path | None = None, *, timeout: int = 60,
                 max_retries: int = 4):
        cfg = load_config()
        self.endpoint = cfg["proxy"]["infinigram_endpoint"]
        self.indexes = {name: cfg["proxy"][key] for name, key in CORPORA.items()}
        self.cache_dir = Path(cache_dir or (cfg.path("cache") / "infinigram"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_retries = max_retries

    def _path(self, index: str, query: str) -> Path:
        digest = hashlib.sha256(f"{index}||{query}".encode()).hexdigest()
        return self.cache_dir / digest[:2] / f"{digest}.json"

    def cached(self, corpus: str, query: str) -> dict | None:
        path = self._path(self.indexes[corpus], query)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def fetch(self, corpus: str, query: str) -> dict:
        hit = self.cached(corpus, query)
        if hit is not None:
            return hit

        import requests

        index = self.indexes[corpus]
        body = {"index": index, "query_type": "count", "query": query}
        headers = {"Content-Type": "application/json"}
        if os.environ.get("INFINIGRAM_API_KEY"):
            headers["Authorization"] = f"Bearer {os.environ['INFINIGRAM_API_KEY']}"

        record: dict = {"corpus": corpus, "index": index, "query": query}
        for attempt in range(self.max_retries):
            response = requests.post(self.endpoint, json=body, headers=headers,
                                     timeout=self.timeout)
            if response.status_code == 200:
                payload = response.json()
                record.update({
                    "ok": "error" not in payload,
                    "count": payload.get("count"),
                    "raw": payload,
                })
                break
            record.update({"ok": False, "status": response.status_code,
                           "error": response.text[:300]})
            time.sleep(min(2**attempt, 30))

        path = self._path(index, query)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        return record


def collect(papers: Iterable[dict], client: InfiniGramClient | None = None, *,
            corpora: Iterable[str] = tuple(CORPORA), variants: Iterable[str] = VARIANTS,
            offline: bool = False) -> Iterator[dict]:
    """Yield one record per (paper, corpus, variant)."""
    client = client or InfiniGramClient()
    for paper in papers:
        first_author = paper["authors"][0] if paper.get("authors") else ""
        for corpus in corpora:
            for variant in variants:
                query = build_query(paper["title"], first_author, variant)
                response = client.cached(corpus, query) if offline else client.fetch(corpus, query)
                yield {
                    "paper_id": paper["paper_id"],
                    "citations": paper["citations"],
                    "citation_bin": paper["citation_bin"],
                    "corpus": corpus,
                    "variant": variant,
                    "query": query,
                    "count": (response or {}).get("count"),
                    "cached": response is not None,
                }
