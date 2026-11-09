"""Batch 2 group A column module, version 2 (D11-1 v2, config/prereg_addendum11_deviations_v2.json): everything of
stage13_b2A_cols.py (re-exported unchanged) plus the per-false-title permutation-control columns stored by
stage13_b2_np_probe_v2.py. stage13_b2A_cols.py itself is not changed."""
import importlib.util as _u
from pathlib import Path as _P
_sp = _u.spec_from_file_location('b2A_cols_v1', _P(__file__).with_name('stage13_b2A_cols.py')); _m = _u.module_from_spec(_sp); _sp.loader.exec_module(_m)
globals().update({k: v for k, v in vars(_m).items() if not k.startswith('__')})

NP_CTRL_TAGS = ['any', 'field']                       # random other paper / random same-field paper (E4b controls)
def np_ctrl_true(tag): return f'ctrl_{tag}_t'          # paper control score of the true-title prediction
def np_ctrl_false(tag, k): return f'ctrl_{tag}_f{k}'   # ... of the false_k-title prediction (control spec_k = t - f_k)
NP_CTRL_PERTITLE = [c for tag in NP_CTRL_TAGS for c in [np_ctrl_true(tag)] + [np_ctrl_false(tag, k) for k in KS]]
NP_PERPAPER_COLS_V2 = NP_PERPAPER_COLS + NP_CTRL_PERTITLE
NP_PROBE_DIR_V2 = 'probe_v2'                           # summary_b2_np/probe_v2 (the old probe/ directory is left to the old probe)
