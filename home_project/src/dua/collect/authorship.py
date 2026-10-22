"""Stage D: collecting open-ended authorship attributions (Section 4.2).

Replaces six near-duplicate collectors from the original tree, which had
drifted onto different model lists -- the committed one still queried
``claude-3.5-sonnet`` and ``gpt-4o-mini``, so anyone running it reproduced a
different experiment. The model list, prompt, and decoding parameters now come
from ``config/models.yaml``.

Output is resumable NDJSON: re-running skips papers already present.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from dua.collect.client import ChatClient, ResponseCache
from dua.config import load_config, load_models

QUESTION = "Who are the authors of the paper titled '{title}' which was published in {year}?"


def build_question(title: str, year) -> str:
    return QUESTION.format(title=title, year=year)


def already_done(output: Path) -> set[str]:
    """Paper ids already present in the output file, for resumption."""
    if not output.exists():
        return set()
    done = set()
    with open(output, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                done.add(json.loads(line)["paper_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def collect(
    papers: Iterable[dict],
    model_key: str,
    output: str | Path,
    *,
    limit: int | None = None,
    resume: bool = True,
    use_cache: bool = True,
) -> Iterator[dict]:
    """Query one model over ``papers`` and stream records to ``output``.

    ``papers`` yields dicts with ``paper_id``, ``title``, ``year``, and
    whatever metadata should be carried through (``field``, ``citations``,
    ``citation_bin``, ``authors``).
    """
    cfg = load_config()
    spec = load_models()["behavioral"][model_key]
    template = cfg.prompt(spec["prompt"])

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = already_done(output) if resume else set()

    client = ChatClient(
        spec["access"],
        cache=ResponseCache(cfg.path("cache"), f"authorship/{model_key}") if use_cache else None,
    )

    written = 0
    with open(output, "a", encoding="utf-8") as sink:
        for paper in papers:
            if limit is not None and written >= limit:
                break
            if paper["paper_id"] in done:
                continue

            question = build_question(paper["title"], paper["year"])
            result = client.call(
                template.format(question=question),
                spec["model_id"],
                temperature=spec.get("temperature", 0),
                max_tokens=spec.get("max_tokens"),
                use_cache=use_cache,
            )
            record = {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "year": paper["year"],
                "field": paper.get("field"),
                "citations": paper.get("citations"),
                "citation_bin": paper.get("citation_bin"),
                "ground_truth_authors": paper.get("authors"),
                "question": question,
                "model": model_key,
                "prompt_file": spec["prompt"],
                **result.as_record(),
            }
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()
            written += 1
            yield record
