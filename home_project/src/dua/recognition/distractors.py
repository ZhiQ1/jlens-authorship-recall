"""Building multiple-choice items (Appendix A7.1).

Three distractor constructions of increasing difficulty, with the model,
papers, prompt, and scoring held fixed so only plausibility varies.

``random_field`` draws 3k names from the field pool, excluding anything that
fuzzy-matches a true author. ``same_field_swap`` replaces one position in the
true list, so each distractor shares k-1 true authors and recognising one
familiar name is not enough. ``collaborator_swap`` replaces one position with a
real collaborator of the true first author, making every option a plausible
subfield-matched team; it falls back to ``same_field_swap`` when the first
author has fewer than three usable collaborators.

Exclusion uses the evaluation pipeline's matcher, so "does not overlap a true
author" means the same thing here as everywhere else.
"""

from __future__ import annotations

import string
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field

from dua.config import load_config
from dua.evaluate.matcher import NameMatcher
from dua.seeds import rng

OPTION_LABELS = tuple(string.ascii_uppercase[:4])


@dataclass
class MCItem:
    """One multiple-choice question."""

    paper_id: str
    title: str
    year: int | str
    field: str
    citations: int
    citation_bin: str
    options: list[list[str]]          # four author lists, in presentation order
    correct_index: int                # 0..3
    mode: str
    fell_back: bool = False
    _meta: dict = dataclass_field(default_factory=dict)

    @property
    def correct_label(self) -> str:
        return OPTION_LABELS[self.correct_index]

    def as_record(self) -> dict:
        return {
            "paper_id": self.paper_id, "title": self.title, "year": self.year,
            "field": self.field, "citations": self.citations,
            "citation_bin": self.citation_bin, "mode": self.mode,
            "fell_back": self.fell_back,
            "correct_label": self.correct_label,
            **{f"option_{label.lower()}": ", ".join(opt)
               for label, opt in zip(OPTION_LABELS, self.options, strict=True)},
        }


def _normalise(name: str) -> str:
    """Cheap key for exact-string deduplication of the field pool."""
    return " ".join(name.strip().split())


def build_field_pools(papers: Iterable[dict]) -> dict[str, list[str]]:
    """Field -> sorted list of unique author names appearing in that field.

    Sorted, not insertion-ordered, so the pool does not depend on row order
    and the draw is reproducible from the seed alone.
    """
    pools: dict[str, set[str]] = defaultdict(set)
    for paper in papers:
        for author in paper["authors"]:
            cleaned = _normalise(author)
            if cleaned:
                pools[paper["field"]].add(cleaned)
    return {field: sorted(names) for field, names in pools.items()}


class DistractorBuilder:
    """Draws distractor teams. One instance per run; the RNG is seeded per paper."""

    def __init__(self, field_pools: dict[str, list[str]], seed: int | None = None):
        self.field_pools = field_pools
        self.seed = load_config().seed if seed is None else seed
        self.matcher = NameMatcher()

    # -- helpers ---------------------------------------------------------
    def _key(self, name: str) -> tuple[str, str]:
        """(particle-stripped surname, first initial) -- the Section 4.5 identity.

        Two names collide exactly when the pipeline would match them at L4 or
        better. Computing the key directly is hundreds of times faster than
        running the full matcher over every candidate.
        """
        parsed = self.matcher._parse_single_name(name)["parsed_alpha"]
        surname = parsed["last_stripped"] or parsed["last"]
        first = parsed["first"]
        return surname, (first[0] if first else "")

    def _conflicts(self, candidate: str, true_surnames: set[str]) -> bool:
        """True if the candidate could be confused with any true author.

        Deliberately stricter than Section 4.5: exclusion is on surname alone,
        because the matcher's weakest level pairs on surname alone. That
        guarantees no distractor intersects the truth at any match level.
        """
        surname, _ = self._key(candidate)
        return (not surname) or surname in true_surnames

    def _draw(self, pool: list[str], n: int, exclude: list[str], gen) -> list[str]:
        """Draw n names without replacement, skipping conflicts.

        Names sharing a (surname, initial) key are skipped too, so no two
        options hold names the scorer would treat as the same person.
        """
        true_surnames = {self._key(a)[0] for a in exclude}
        picked, used_keys = [], set()
        for idx in gen.permutation(len(pool)):
            if len(picked) == n:
                break
            candidate = pool[idx]
            key = self._key(candidate)
            if key in used_keys or self._conflicts(candidate, true_surnames):
                continue
            used_keys.add(key)
            picked.append(candidate)
        if len(picked) < n:
            raise ValueError(
                f"field pool exhausted: needed {n} distractor names, found "
                f"{len(picked)} in a pool of {len(pool)}. Build the pools from "
                "the full evaluation sample, not a subset."
            )
        return self._repair(picked, pool, exclude, used_keys, gen)

    def _repair(self, picked: list[str], pool: list[str], exclude: list[str],
                used_keys: set, gen) -> list[str]:
        """Replace any name the full matcher still pairs with a true author.

        The surname key misses the first/last-swap and bibliographic rescues,
        so a few candidates per thousand slip through. Running the matcher over
        the drawn set only keeps this exact without a quadratic draw.
        """
        for i, name in enumerate(picked):
            if not self.matcher.find_matches(exclude, name)["matches"]:
                continue
            for idx in gen.permutation(len(pool)):
                candidate = pool[idx]
                key = self._key(candidate)
                if key in used_keys or not key[0]:
                    continue
                if self.matcher.find_matches(exclude, candidate)["matches"]:
                    continue
                used_keys.add(key)
                picked[i] = candidate
                break
        return picked

    def _assemble(self, paper: dict, distractors: list[list[str]], mode: str,
                  gen, fell_back: bool = False) -> MCItem:
        """Place the correct option uniformly at random among the four."""
        correct_index = int(gen.integers(0, len(OPTION_LABELS)))
        options = list(distractors)
        options.insert(correct_index, list(paper["authors"]))
        return MCItem(
            paper_id=paper["paper_id"], title=paper["title"], year=paper["year"],
            field=paper["field"], citations=paper["citations"],
            citation_bin=paper["citation_bin"], options=options,
            correct_index=correct_index, mode=mode, fell_back=fell_back,
        )

    # -- the three constructions ------------------------------------------
    def random_field(self, paper: dict) -> MCItem:
        gen = rng(self.seed, "mc", "random_field", paper["paper_id"])
        true = list(paper["authors"])
        k = len(true)
        drawn = self._draw(self.field_pools[paper["field"]], 3 * k, true, gen)
        distractors = [drawn[i * k:(i + 1) * k] for i in range(3)]
        return self._assemble(paper, distractors, "random_field", gen)

    def same_field_swap(self, paper: dict) -> MCItem:
        gen = rng(self.seed, "mc", "same_field_swap", paper["paper_id"])
        true = list(paper["authors"])
        k = len(true)
        replacements = self._draw(self.field_pools[paper["field"]], 3, true, gen)
        distractors = []
        for repl in replacements:
            option = list(true)
            option[int(gen.integers(0, k))] = repl
            distractors.append(option)
        return self._assemble(paper, distractors, "same_field_swap", gen)

    def collaborator_swap(self, paper: dict, collaborators: list[str] | None) -> MCItem:
        """Substitute a real collaborator of the true first author.

        Falls back to ``same_field_swap`` below three usable collaborators, and
        records the fallback on the item.
        """
        gen = rng(self.seed, "mc", "collaborator_swap", paper["paper_id"])
        true = list(paper["authors"])
        k = len(true)
        true_surnames = {self._key(a)[0] for a in true}
        usable = [c for c in (collaborators or []) if not self._conflicts(c, true_surnames)]
        # Deduplicate while keeping the order the API returned.
        seen, unique = set(), []
        for c in usable:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        if len(unique) < 3:
            item = self.same_field_swap(paper)
            item.mode = "collaborator_swap"
            item.fell_back = True
            return item

        chosen = [unique[i] for i in gen.permutation(len(unique))[:3]]
        distractors = []
        for repl in chosen:
            option = list(true)
            # Keep the true first author fixed; swap one of the rest.
            position = 0 if k == 1 else int(gen.integers(1, k))
            option[position] = repl
            distractors.append(option)
        return self._assemble(paper, distractors, "collaborator_swap", gen)


def verify_items(items: list[MCItem]) -> dict:
    """The integrity checks Appendix A7.1 reports.

    Returns duplicate counts, overlap counts, and the empirical distribution
    of the correct option's position (the paper reports A/B/C/D within 2pp of
    uniform).
    """
    matcher = NameMatcher()
    duplicates = overlaps = 0
    positions = dict.fromkeys(OPTION_LABELS, 0)
    for item in items:
        positions[item.correct_label] += 1
        true = item.options[item.correct_index]
        truth_has_duplicates = len(set(true)) != len(true)
        for i, option in enumerate(item.options):
            # The correct option is the published author list; if it repeats a
            # name, that is the record, not a construction error -- and the
            # swap constructions inherit that repetition by design.
            if i == item.correct_index or truth_has_duplicates:
                continue
            if len(set(option)) != len(option):
                duplicates += 1
            # Only the random-field construction promises zero overlap; the two
            # swap constructions deliberately share k-1 true authors.
            if i != item.correct_index and item.mode == "random_field":
                if any(matcher.find_matches(true, name)["matches"] for name in option):
                    overlaps += 1
    total = len(items) or 1
    return {
        "n_items": len(items),
        "n_fell_back": sum(1 for i in items if i.fell_back),
        # Duplicates inside a distractor group. The correct option is excluded:
        # a published author list that repeats a name is the record itself.
        "options_with_duplicate_names": duplicates,
        # Only meaningful for random_field; the swap constructions share k-1
        # true authors on purpose.
        "distractor_groups_overlapping_truth": overlaps,
        "correct_position_distribution": {k: v / total for k, v in positions.items()},
    }
