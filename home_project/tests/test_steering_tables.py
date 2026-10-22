"""Appendix A8.8 / Table A25 invariants.

Table A25 is generated from Stage 24, not Stage 15 -- a distinction that cost
three review passes when the Stage 24 artifact was missing from the release
These tests fail loudly if that artifact goes away
again, or if the table quietly falls back to Stage 15's single control.
"""

import json

import pytest

from dua.probing.tables import _position_probe_summary, probing_dir

MODELS = ("qwen3_32b", "mistral_small_3_2_24b")

# The values the camera-ready prints. Hardcoding them here is the point: the
# test asserts the artifact still backs the paper, not that the code is
# self-consistent.
PAPER = {
    "qwen3_32b": {"baseline": 10.0, "steered": 70.0, "probe": 58.0, "control": (30.0, 48.0)},
    "mistral_small_3_2_24b": {"baseline": 36.0, "steered": 82.0, "probe": 64.0,
                              "control": (48.0, 52.0)},
}


@pytest.fixture(scope="module", params=MODELS)
def summary(request):
    base = probing_dir() / "steering" / request.param
    if not (base / "steering_results.csv").exists():
        pytest.skip("probing artifacts not present in this checkout")
    s = _position_probe_summary(base)
    assert s is not None, f"Stage 24 artifact missing for {request.param}"
    return request.param, s


def test_five_control_seeds_are_shipped(summary):
    model, s = summary
    assert s["n_control_seeds"] == 5, "Appendix A8.8 describes five random directions"
    assert sorted(s["random_pct_by_seed"]) == [542, 543, 544, 545, 546]


def test_arms_match_the_published_table(summary):
    model, s = summary
    want = PAPER[model]
    assert s["baseline_pct"] == want["baseline"]
    assert s["steered_pct"] == want["steered"]
    assert s["probe_pct"] == want["probe"]
    assert (s["random_pct_min"], s["random_pct_max"]) == want["control"]


def test_the_direction_beats_every_random_control(summary):
    """A8.8's actual claim: not just above baseline, above the whole spread."""
    _, s = summary
    assert s["steered_pct"] > s["random_pct_max"]


def test_stage15_control_agrees_with_the_stage24_spread(summary):
    """The two controls are independent runs; they must not contradict."""
    model, s = summary
    meta = json.loads(
        (probing_dir() / "steering" / model / "steering_meta.json").read_text(encoding="utf-8"))
    assert meta["n_control_shuffles"] == 1, "Stage 15 is the single-direction control"

    import pandas as pd
    c = pd.read_csv(probing_dir() / "steering" / model
                    / "steering_results_norm_matched_control.csv")
    at_alpha2 = c[(c["pool"] == "eval_high") & (c["direction"] == "random") & (c["alpha"] == 2.0)]
    stage15 = float(at_alpha2["hallucination_rate_pct"].iloc[0])
    assert s["random_pct_min"] <= stage15 <= s["random_pct_max"], (
        f"Stage 15 control {stage15}% falls outside Stage 24's "
        f"{s['random_pct_min']}--{s['random_pct_max']}% spread")


def test_release_inputs_reproduce_the_stage24_eval_pool(tmp_path):
    """The shipped inputs must select the same 50 papers the numbers came from.

    Everything a Stage 24 re-run does before the first forward pass -- unpack
    the scores, load the pool ids, sample at seed 42, norm-match the vectors --
    is deterministic and checkable without a GPU. The Stage 24 meta records
    which papers the shipped rates were computed on, so this is an exact test
    that `data/release/` carries enough to re-derive Table A25.
    """
    import numpy as np
    import pandas as pd

    from dua.config import load_config
    from dua.probing.rundir import materialize_run_dir

    release = load_config().path("release")
    for model in MODELS:
        steer = release / "probing" / "steering" / model
        s24_meta = steer / "position_probe" / "position_probe_meta_eval_high.json"
        if not s24_meta.exists():
            pytest.skip("probing artifacts not present in this checkout")

        scored_path = materialize_run_dir(release, model, tmp_path / model)
        scored = pd.read_csv(scored_path, sep="\t")

        meta = json.loads((steer / "steering_meta.json").read_text(encoding="utf-8"))
        ids = {str(x) for x in meta["pool_paper_ids"]["eval_high"]}
        eval_all = scored[scored["paper_id"].astype(str).isin(ids)].reset_index(drop=True)
        pool = eval_all.sample(n=min(50, len(eval_all)), random_state=42).reset_index(drop=True)

        s24 = json.loads(s24_meta.read_text(encoding="utf-8"))
        assert [str(x) for x in pool["paper_id"]] == [str(x) for x in s24["eval_pool_paper_ids"]]

        vector = np.load(steer / "steering_vector.npy")
        assert (steer / "probe_direction.npy").exists(), "probe arm needs the probe vector"
        assert np.isclose(np.linalg.norm(vector), s24["reference_norm"], atol=1e-4)
