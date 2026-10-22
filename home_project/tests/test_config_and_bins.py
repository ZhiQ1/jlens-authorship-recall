"""Configuration, binning, and seeding invariants.

These are cheap and they catch the class of bug that silently shifts every
downstream number: a bin edge that moved, a field key that stopped matching,
a draw that is not actually reproducible.
"""

import pytest

from dua.bins import bin_index, bin_label, field_label, normalize_field
from dua.config import load_config
from dua.seeds import rng, set_all_seeds


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def test_thirteen_bins_in_paper_order(cfg):
    assert cfg.bin_labels == [
        "0-2", "3-4", "5-8", "9-16", "17-32", "33-64", "65-128", "129-256",
        "257-512", "513-1024", "1025-2048", "2049-4096", "4097+",
    ]


def test_bins_are_contiguous_and_exhaustive(cfg):
    """No citation count may fall between two bins or into two at once."""
    bins = cfg.citation_bins
    for previous, current in zip(bins[:-1], bins[1:], strict=True):
        assert previous.hi is not None
        assert current.lo == previous.hi + 1, f"gap between {previous} and {current}"
    assert bins[0].lo == 0
    assert bins[-1].hi is None, "the final bin must be open-ended"


@pytest.mark.parametrize(
    "citations,label",
    [(0, "0-2"), (2, "0-2"), (3, "3-4"), (32, "17-32"), (33, "33-64"),
     (4096, "2049-4096"), (4097, "4097+"), (10_000_000, "4097+")],
)
def test_bin_label(citations, label):
    assert bin_label(citations) == label


def test_bin_label_rejects_negative():
    with pytest.raises(ValueError):
        bin_label(-1)


def test_bin_index_orders_bins(cfg):
    indices = [bin_index(b) for b in cfg.bin_labels]
    assert indices == sorted(indices) == list(range(len(cfg.bin_labels)))


def test_eight_fields(cfg):
    assert len(cfg.fields) == 8
    assert set(cfg.field_keys) == {
        "medicine", "biology", "chemistry", "computer science",
        "materials science", "physics", "psychology", "mathematics",
    }


@pytest.mark.parametrize(
    "raw,expected",
    [("Computer Science", "computer science"), ("  MEDICINE  ", "medicine"),
     ("Computer  Science", "computer science"), ("Geology", None),
     ("", None), (None, None)],
)
def test_normalize_field(raw, expected):
    assert normalize_field(raw) == expected


def test_field_label_round_trips(cfg):
    for key in cfg.field_keys:
        assert normalize_field(key) == key
        assert field_label(key)


def test_seed_is_the_only_source_of_randomness(cfg):
    assert cfg.seed == 42


def test_named_streams_are_independent_and_reproducible():
    a1 = rng(42, "distractors", "medicine").random(5).tolist()
    a2 = rng(42, "distractors", "medicine").random(5).tolist()
    b = rng(42, "bootstrap").random(5).tolist()
    assert a1 == a2, "the same name must give the same stream"
    assert a1 != b, "different names must give different streams"


def test_named_streams_do_not_depend_on_interpreter_hash_seed():
    """rng() salts with SHA-256, not hash(), so streams survive a restart."""
    import subprocess
    import sys

    code = (
        "import sys; sys.path.insert(0, 'src');"
        "from dua.seeds import rng; print(rng(42, 'x').random())"
    )
    outputs = {
        subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, env={"PYTHONHASHSEED": str(s), "PATH": ""}).stdout
        for s in (0, 1, 12345)
    }
    assert len(outputs) == 1, f"stream varied with PYTHONHASHSEED: {outputs}"


def test_set_all_seeds_returns_the_seed():
    assert set_all_seeds(7) == 7


def test_prompt_templates_have_their_placeholders(cfg):
    assert "{question}" in cfg.prompt("authorship_fewshot_paper.txt")
    assert "{question}" in cfg.prompt("authorship_fewshot_openrouter.txt")
    mc = cfg.prompt("mc_recognition.txt")
    for field in ("{title}", "{year}", "{option_a}", "{option_d}"):
        assert field in mc
    self_eval = cfg.prompt("self_eval.txt")
    for field in ("{question}", "{reference}", "{generated}"):
        assert field in self_eval


def test_no_credential_is_committed():
    """A live OpenRouter key was committed across 51 files in the source tree."""
    import re
    from pathlib import Path

    from dua.config import REPO_ROOT

    patterns = [re.compile(p) for p in (
        r"sk-or-v1-[A-Za-z0-9]{16}",
        r"sk-proj-[A-Za-z0-9]{16}",
        r"sk-ant-[A-Za-z0-9]{16}",
        r"AKIA[0-9A-Z]{16}",
    )]
    skip = {".git", ".venv", "venv", "__pycache__", "data", "results", ".pytest_cache"}
    offenders = []
    for path in Path(REPO_ROOT).rglob("*"):
        if not path.is_file() or set(path.parts) & skip:
            continue
        if path.suffix not in {".py", ".sh", ".yaml", ".yml", ".txt", ".md", ".toml", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(p.search(text) for p in patterns):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, f"credential-shaped strings found in: {offenders}"


def test_citation_count_does_not_fall_back_to_oag():
    """Falling back to OAG's stale n_citation breaks all 13 bins in Table 1.

    An earlier collector did exactly that. Using the Semantic Scholar count
    alone reproduces every bin count exactly over the full corpus; the
    fallback moves 9,975 papers out of the 0-2 bin. See
    the paper.
    """
    from dua.sampling.stratified import citation_count

    record = {
        "source": "semantic",
        "semantic_scholar": {"citationCount": 0},
        "original": {"n_citation": "37"},
    }
    assert citation_count(record) == 0, "OAG's n_citation must not be consulted"

    record["semantic_scholar"]["citationCount"] = 12
    assert citation_count(record) == 12
    assert citation_count({"source": "semantic", "semantic_scholar": {}}) == 0


def test_the_two_field_rules_are_distinct_and_correct():
    """Stratification and corpus statistics use different rules, on purpose.

    ``paper_field`` reproduces the released sample's stored field for 100% of
    the papers locatable in the corpus; ``primary_field`` reproduces the 76.95%
    coverage figure and Tables A8/A9. Collapsing them into one rule breaks one
    or the other.
    """
    from dua.sampling.stratified import paper_field, primary_field

    def record(fields):
        return {"source": "semantic", "semantic_scholar": {"fieldsOfStudy": fields}}

    # Primary field outside the eight, a later one inside: the two disagree.
    r = record(["Political Science", "Medicine"])
    assert primary_field(r) == "political science"
    assert paper_field(r) == "medicine"

    # Neither may consult config order: Biology is listed after Medicine in
    # config.yaml, but it is this paper's field under both rules.
    r = record(["Biology", "Medicine"])
    assert primary_field(r) == "biology"
    assert paper_field(r) == "biology"

    # Nothing among the eight.
    r = record(["Geology", "Engineering"])
    assert primary_field(r) == "geology"
    assert paper_field(r) is None

    for empty in ([], None):
        assert primary_field(record(empty)) is None
        assert paper_field(record(empty)) is None
