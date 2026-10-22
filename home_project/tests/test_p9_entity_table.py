"""Table A24, the P9 entity-level probe.

The data shipped in `data/release/probing/p9_robustness_summary.csv` but no
generator emitted it, so the table was cited and unchecked. These assertions
hardcode the camera-ready's printed cells: the point is to catch the artifact
drifting away from the paper, not to restate the code.
"""

import pytest

from dua.probing.tables import probing_dir, table_p9_entity

# Exactly what latex/camera-ready.tex prints in tab:appendix_p9_entity.
PAPER = {
    "qwen3_32b": {"n_matched": 1286, "n_hallucinated": 46726, "probe_auroc": 0.814,
                  "probe_auprc_lift_over_baseline": 1.019,
                  "centroid_l2_over_pooled_rms": 0.246,
                  "nearest_centroid_balanced_accuracy": 0.760},
    "mistral_small_3_2_24b": {"n_matched": 1303, "n_hallucinated": 49960,
                              "probe_auroc": 0.818,
                              "probe_auprc_lift_over_baseline": 1.018,
                              "centroid_l2_over_pooled_rms": 0.209,
                              "nearest_centroid_balanced_accuracy": 0.743},
}


@pytest.fixture(scope="module")
def values():
    if not (probing_dir() / "p9_robustness_summary.csv").exists():
        pytest.skip("probing artifacts not present in this checkout")
    return table_p9_entity()


@pytest.mark.parametrize("model", sorted(PAPER))
def test_every_printed_cell_reproduces(values, model):
    got = values[model]
    for field, want in PAPER[model].items():
        if isinstance(want, int):
            assert got[field] == want, field
        else:
            assert round(got[field], 3) == want, field


def test_both_models_are_present(values):
    assert sorted(values) == sorted(PAPER)


def test_the_class_imbalance_the_table_exists_to_show(values):
    """AUROC is high while AUPRC lift is ~1.0 because the base rate is ~97%."""
    for model, got in values.items():
        assert got["hallucinated_positive_rate"] > 0.95, model
        assert got["probe_auroc"] > 0.8, model
        assert 1.0 < got["probe_auprc_lift_over_baseline"] < 1.05, model
        assert got["n_matched"] + got["n_hallucinated"] == got["n_names"], model
