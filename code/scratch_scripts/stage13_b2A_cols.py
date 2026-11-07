"""Batch 2, group A (addendum 11 part A; addendum 12 items 2-7 and 2-9): the ONE place where result-file column names, raw-file
keys, layer / condition lists and role names of these items are defined (HANDOFF fixed rule 4). Every b2A script imports from here.

No project-wide column module existed when this was written (2026-11-06); older stage scripts define their columns inline.
This module only covers the new batch-2 group-A files; nothing older imports it.
"""

# ------------------------------------------------------------------ shared
PAPER_ID, ROW_ID, FOLD, N_TOK = 'paper_id', 'row_id', 'fold', 'n_tok'
GROUP, CBIN, GRP4, TEAM = 'group_tight', 'citation_bin', 'grp', 'team'
KS = [0, 1, 2, 3, 4]
CONDS = ['true'] + [f'false_{k}' for k in KS]

# ------------------------------------------------------------------ addendum 11 A: name-position probe
NP_LAYERS = [32, 40, 48, 52, 56]
NP_CHECK_LAYER = 63                                    # recorded for the true title only (hard check 1), not stored
NP_HARD1_TOL = 0.05                                    # relative norm diff vs raw/allTok_L63 (plan)
NP_HARD2_TOL = 0.005                                   # |diff| vs published Stage 10 values at L40 / L48 (plan)
NP_HARD2_LAYERS = [40, 48]
NP_LENS_READOUTS = ['logit', 'jlens_public']
NP_ALPHAS = (0.1, 1.0, 10.0)
NP_RNG_SEED = 3712                                     # permutation controls (as confirmatory E4b)
# probe runs: name -> Stage 10 cohort role (None = token_index 0 rows = the ':' position / first-token run)
NP_RUNS = {'colon_first': None, 'initial': 'initial_first', 'given_first': 'given_first', 'given_cont': 'given_cont',
           'surname_first': 'surname_first', 'surname_cont': 'surname_cont'}
NP_PRIMARY = dict(layers=[40, 48], run_order=['surname_first', 'initial', 'given_first', 'given_cont', 'surname_cont', 'colon_first'])


def np_resid_key(l): return f'resid_L{l}'           # raw npz key, fp16 [n_rows, d]
def np_rank_key(l): return f'rank_logit_L{l}'       # raw npz key, int32: full-vocab logit-lens rank of the gold token (bf16 state)


NP_RAW_KEYS = [ROW_ID] + [np_resid_key(l) for l in NP_LAYERS] + [np_rank_key(l) for l in NP_LAYERS] + ['meta']

# per-paper probe output (perpaper_<run>_L<l>.parquet)
NP_TRUE, NP_FALSE_MEAN5, NP_SPEC5, NP_SPEC0 = 'true', 'false_mean5', 'spec5', 'spec0'
def np_false(k): return f'false_{k}'
def np_spec_k(k): return f'spec_k{k}'
def np_dropped(k): return f'dropped_{k}'
NP_DROP0, NP_DROP5 = 'drop0', 'drop5'
NP_CTRL = ['ctrl_any0', 'ctrl_any5', 'ctrl_field0', 'ctrl_field5']
NP_CEIL = 'ceiling'
NP_PERPAPER_COLS = ([PAPER_ID, FOLD, N_TOK, NP_TRUE] + [np_false(k) for k in KS] + [NP_FALSE_MEAN5, NP_SPEC5, NP_SPEC0]
                    + [np_spec_k(k) for k in KS] + NP_CTRL + [NP_CEIL] + [np_dropped(k) for k in KS] + [NP_DROP0, NP_DROP5, 'self_any', 'self_field'])
# per-token probe output (pertoken_<run>_L<l>.parquet)
NP_PERTOKEN_COLS = [ROW_ID, PAPER_ID, 'nlr_true'] + [f'nlr_false_{k}' for k in KS]
# fit json keys
NP_FIT_KEYS = ['run', 'layer', 'alpha', 'alpha_errs_fold0', 'n_rows', 'n_papers', 'heldout_r2_true', 'n_drop0', 'n_drop5', 'tiny']
# lens per-paper output (lens_perpaper.parquet), long format
NP_LENS_COLS = [PAPER_ID, 'run', 'readout', 'layer', N_TOK, 'true'] + [f'false_{k}' for k in KS] + ['false_mean5', 'spec5', 'spec0']
# report tables
NP_TABLE_COLS = ['version', 'run', 'layer', 'n_tc', 'spec', 'lo', 'hi', 'tc_diff', 'tc_lo', 'tc_hi', 'tc_bins',
                 'any_est', 'any_lo', 'any_hi', 'field_est', 'field_lo', 'field_hi', 'alpha', 'heldout_r2', 'ceiling']
NP_VERSIONS = {'V5': ('spec5', 'drop5', 'ctrl_any5', 'ctrl_field5'), 'V5x0': ('spec5', 'drop0', 'ctrl_any5', 'ctrl_field5'),
               'V0': ('spec0', 'drop0', 'ctrl_any0', 'ctrl_field0')}
NP_GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s']

# ------------------------------------------------------------------ 2-7 / 2-9: patchscope with sources at the name positions
PS_LAYERS = [8, 16, 24, 32, 40, 48, 56]               # = 381_stage13.PS_LAYERS (batch of 7, as the published X4)
PS_TARGETS = ['year', 'author', 'field']
PS_WHO = ['self', 'partner']
PS_SRC_KINDS = ['title', 'colon', 'name']              # title = title-last (published X4); colon = ':' (published X4); name = j >= 1
# token-level output (raw/b2_pscope/shard_XXX.parquet), one row per (paper, source, who, target, layer, answer token)
PS_TOKEN_COLS = [PAPER_ID, 'partner', 'src_kind', 'src_author', 'src_j', 'src_role', 'who', 'target', 'layer', 'ans_j', 'ans_role', 'nlr']
PS_NONE_COLS = [PAPER_ID, 'target', 'ans_j', 'ans_role', 'nlr']        # unpatched target prompt (raw/b2_pscope/none_XXX.parquet)
PS_HARD_TOL = 0.005
PS_HARD_REF = dict(split='test', answer='author', pos='title', layer=8, D=0.04646379836358658)   # published X4 first author L8
X4TOK_HARD_LAYERS = [8, 40]
X4TOK_ROLES = ['given_first', 'initial_first', 'surname_first', 'all']
# analysis outputs
PS_D_COLS = ['split', 'answer', 'src', 'layer', 'n', 'D', 'lo', 'hi', 'self', 'partner', 'none']
X4TOK_COLS = ['measure', 'src', 'layer', 'role', 'n', 'mean', 'lo', 'hi', 'mean_over_sd', 'win']
