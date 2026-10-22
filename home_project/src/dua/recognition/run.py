"""Section 6: running the multiple-choice recognition experiment.

Builds items with :mod:`dua.recognition.distractors`, queries the model, and
records the letter it chose. Resumable and cached, like every other API stage.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from dua.collect.client import ChatClient, ResponseCache
from dua.config import load_config, load_models
from dua.recognition.distractors import OPTION_LABELS, DistractorBuilder, MCItem, build_field_pools

_LETTER = re.compile(r"\b([A-D])\b")


def parse_choice(text: str | None) -> str | None:
    """Pull the chosen letter out of a response.

    Accepts a bare letter, a letter with punctuation, or a letter embedded in
    a sentence the model was told not to write. Returns ``None`` when no
    single option can be identified, which is scored as incorrect rather than
    dropped -- silently dropping non-compliant answers would flatter the model.
    """
    if not text:
        return None
    stripped = text.strip()
    if stripped and stripped[0].upper() in OPTION_LABELS:
        return stripped[0].upper()
    found = _LETTER.findall(stripped.upper())
    return found[0] if found else None


def build_items(papers: Iterable[dict], mode: str,
                collaborators: dict[str, list[str]] | None = None) -> list[MCItem]:
    papers = list(papers)
    builder = DistractorBuilder(build_field_pools(papers))
    items = []
    for paper in papers:
        if mode == "random_field":
            items.append(builder.random_field(paper))
        elif mode == "same_field_swap":
            items.append(builder.same_field_swap(paper))
        elif mode == "collaborator_swap":
            first_author = paper["authors"][0] if paper["authors"] else ""
            items.append(builder.collaborator_swap(
                paper, (collaborators or {}).get(first_author)))
        else:
            raise ValueError(f"unknown distractor mode {mode!r}")
    return items


def run(items: Iterable[MCItem], output: str | Path, *, model_key: str = "gpt-4o",
        resume: bool = True, use_cache: bool = True) -> Iterator[dict]:
    cfg = load_config()
    spec = load_models()["recognition"][model_key]
    template = cfg.prompt(spec["prompt"])

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if resume and output.exists():
        with open(output, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["paper_id"])

    client = ChatClient(
        spec["access"],
        cache=ResponseCache(cfg.path("cache"), f"recognition/{model_key}") if use_cache else None,
    )

    with open(output, "a", encoding="utf-8") as sink:
        for item in items:
            if item.paper_id in done:
                continue
            prompt = template.format(
                title=item.title, year=item.year,
                **{f"option_{label.lower()}": ", ".join(opt)
                   for label, opt in zip(OPTION_LABELS, item.options, strict=True)},
            )
            result = client.call(prompt, spec["model_id"],
                                 temperature=spec.get("temperature", 0),
                                 use_cache=use_cache)
            chosen = parse_choice(result.content)
            record = {
                **item.as_record(),
                "chosen_label": chosen,
                "correct": int(chosen == item.correct_label),
                "parse_failed": int(chosen is None),
                **result.as_record(),
            }
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()
            yield record
