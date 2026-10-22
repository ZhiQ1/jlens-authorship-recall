"""Fetching real collaborators for the hardest distractor control (A7.3).

For each paper's true first author, we need other real people that author has
published with. Semantic Scholar exposes this in two hops: resolve the author
to an ``authorId``, then list their papers' co-authors.

Every response is cached to disk keyed by the query, so the control is
re-runnable without re-hitting the API and the shipped cache *is* the
reproducible artifact. Semantic Scholar's author records change over time;
without the cache this control is not reproducible at all.
"""

from __future__ import annotations

import json
import os
import time
from collections import Counter
from pathlib import Path

S2_BASE = "https://api.semanticscholar.org/graph/v1"
MIN_COLLABORATORS = 3


class CollaboratorIndex:
    """Author name -> collaborator names, cached on disk."""

    def __init__(self, cache_dir: str | Path, papers_per_author: int = 20):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.papers_per_author = papers_per_author
        self._session = None

    # -- cache ------------------------------------------------------------
    @staticmethod
    def _slug(name: str) -> str:
        import hashlib

        return hashlib.sha256(name.strip().lower().encode("utf-8")).hexdigest()[:24]

    def _path(self, name: str) -> Path:
        return self.cache_dir / f"{self._slug(name)}.json"

    def cached(self, name: str) -> list[str] | None:
        path = self._path(name)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))["collaborators"]
        except (json.JSONDecodeError, KeyError):
            return None

    # -- network ----------------------------------------------------------
    def _get(self, url: str, params: dict) -> dict | None:
        import requests

        if self._session is None:
            self._session = requests.Session()
            key = os.environ.get("S2_API_KEY")
            if key:
                self._session.headers["x-api-key"] = key

        for attempt in range(5):
            response = self._session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            if response.status_code in (429, 503):
                # Semantic Scholar is aggressively rate limited without a key.
                time.sleep(min(2**attempt, 30))
                continue
            return None
        return None

    def fetch(self, name: str) -> list[str]:
        """Collaborators of ``name``, most frequent first. Cached."""
        hit = self.cached(name)
        if hit is not None:
            return hit

        collaborators: list[str] = []
        search = self._get(f"{S2_BASE}/author/search", {"query": name, "limit": 1,
                                                        "fields": "authorId,name"})
        author_id = None
        if search and search.get("data"):
            author_id = search["data"][0].get("authorId")

        if author_id:
            papers = self._get(
                f"{S2_BASE}/author/{author_id}/papers",
                {"limit": self.papers_per_author, "fields": "authors"},
            )
            counts: Counter[str] = Counter()
            for paper in (papers or {}).get("data", []):
                for coauthor in paper.get("authors", []):
                    coauthor_name = (coauthor or {}).get("name")
                    if coauthor_name and coauthor.get("authorId") != author_id:
                        counts[coauthor_name] += 1
            collaborators = [n for n, _ in counts.most_common()]

        self._path(name).write_text(
            json.dumps({"query": name, "author_id": author_id,
                        "collaborators": collaborators}, ensure_ascii=False),
            encoding="utf-8",
        )
        return collaborators

    def build(self, first_authors: list[str], *, offline: bool = False) -> dict[str, list[str]]:
        """Index every first author. ``offline=True`` uses only the cache.

        Returns the mapping and prints nothing; the caller reports coverage,
        which the paper quotes as 96.7% of first authors having at least three
        usable collaborators.
        """
        index: dict[str, list[str]] = {}
        for name in first_authors:
            if name in index:
                continue
            index[name] = self.cached(name) or ([] if offline else self.fetch(name))
        return index


def coverage(index: dict[str, list[str]]) -> dict:
    """Fraction of authors with enough collaborators to avoid the fallback."""
    total = len(index) or 1
    enough = sum(1 for v in index.values() if len(v) >= MIN_COLLABORATORS)
    return {"n_authors": len(index), "n_with_enough": enough,
            "fraction_with_enough": enough / total,
            "min_required": MIN_COLLABORATORS}
