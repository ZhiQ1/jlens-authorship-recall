"""The prompt CSV the Section 7 GPU stages read.

`papers_9108.csv` is not shipped; it is rebuilt from the released evaluation
sample. If the template or the author join drifts, every stage silently
prompts the model with something the paper did not.
"""

import pandas as pd
import pytest

from dua.config import load_config
from dua.probing.prompts import PROMPT_COLUMNS, build_prompt_frame


@pytest.fixture(scope="module")
def prompts():
    sample = load_config().path("release") / "eval_sample_9108.csv.gz"
    if not sample.exists():
        pytest.skip("evaluation sample not present in this checkout")
    return build_prompt_frame(pd.read_csv(sample))


def test_columns_and_row_count(prompts):
    assert list(prompts.columns) == PROMPT_COLUMNS
    assert len(prompts) == 9108


def test_question_template_is_exact(prompts):
    q = prompts["question"].iloc[0]
    assert q.startswith("Who are the authors of the paper titled '")
    assert q.endswith("?")


def test_every_question_parses_back_through_the_stage_regex(prompts):
    """The stages recover title and year from the question by regex.

    Importing the stage pulls in torch, which the no-GPU reproduction path does
    not install -- hence the skip. Where torch is present, this is the check
    that matters: a template change that the regex cannot parse would leave
    every title and year empty downstream.
    """
    pytest.importorskip("torch", reason="stage modules import torch")
    from dua.probing.stages.stage1_generate import _QUESTION_RE

    parsed = prompts["question"].map(lambda s: bool(_QUESTION_RE.search(s)))
    assert parsed.all(), f"{(~parsed).sum()} questions do not match _QUESTION_RE"


def test_answers_are_comma_joined_names(prompts):
    assert not prompts["answer"].str.contains(r"[\[\]\"]", regex=True).any()
    assert prompts["answer"].str.len().gt(0).all()


def test_no_missing_ids(prompts):
    assert prompts["paperId"].is_unique
    assert prompts["paperId"].notna().all()
