"""Batch 2, group B (addendum 11 B; addendum 12 items 2-3, 2-4, 2-8, 2-10): THE column module (fixed rule 4).

Every group-B script (14_groups/b2_cd.py, 13_stage13/stage13_b2B_gpu.py, 13_stage13/stage13_b2B_analyze.py) imports the
names of raw-file keys and result-file columns from here, and writes CSVs through `write_csv`, which refuses a frame whose
columns differ from the declared list. Nothing else is defined here (no computation).
"""
from pathlib import Path

# ------------------------------------------------------------------ raw GPU outputs (npz keys)
# Stage 11 E1 / E2 / E1t keys are the frozen Stage 11 names (361_stage11.do_patch / do_knockout / do_patch_title).
RAW_E1 = ['row_id', 'rank_true', 'rank_false', 'rank_patch', 'layers']
RAW_E2 = ['row_id', 'rank_ko', 'layers']
RAW_E1T = ['row_id', 'rank_true', 'rank_false', 'rank_patch', 'layers', 'false_condition']
# 2-4 batch noise: b1 = batch size 1, b15 = original E1 batch (len(PATCH_LAYERS) = 15 elements)
NOISE_LAYERS = [40, 48, 52]
RAW_NOISE = ['row_id', 'paper_id', 'rank_true_b1', 'rank_false_b1', 'rank_true_b15', 'rank_false_b15',
             'rank_patch_b15', 'rank_patch_b1', 'layers_b15', 'layers_b1', 'b15_elements_identical_true', 'b15_elements_identical_false']
# 2-3 X3 per token, all authors (versions as stage13_x3_tok_gpu.VERS)
X3_VERS = ['original', 'paraphrase', 'partner', 'lexical']
RAW_X3TOK = ['row_id', 'paper_id', 'author_index', 'n_authors', 'token_index', 'partner', 'lexical_neighbour'] + [f'rank_{v}' for v in X3_VERS]
# 2-10 M3 authors task, every name token of every author
RAW_M3TOK = ['row_id', 'paper_id', 'author_index', 'token_index', 'rank', 'exact_paper_id', 'exact_first_rank']   # exact_* = one per paper (published do_task path)

# ------------------------------------------------------------------ token roles (Stage 10 cohort/name_tokens.parquet `role`)
ROLES = {'ALL': None, 'initial': ['initial_first'], 'given_first': ['given_first'], 'given_cont': ['given_cont'],
         'surname_first': ['surname_first'], 'surname_cont': ['surname_cont']}
STRATA = ['first', 'all', 'others']          # author strata (as stage13_b1_xall_analyze: first = author_index 0)

# ------------------------------------------------------------------ result tables
# item 1 (addendum 11 B): C / D completion of E1 / E2
CD_GROUP_VALUES = ['experiment', 'who', 'layer', 'item', 'group', 'source', 'n_papers', 'estimate', 'lo', 'hi',
                   'numerator', 'num_lo', 'num_hi', 'denominator', 'den_lo', 'den_hi', 'descriptive_only']
CD_CONTRASTS = ['experiment', 'who', 'layer', 'contrast', 'kind', 'n_a', 'n_b', 'n_bins', 'min_a', 'min_b',
                'ratio_diff', 'ratio_lo', 'ratio_hi', 'num_diff', 'num_lo', 'num_hi', 'den_diff', 'den_lo', 'den_hi', 'p', 'descriptive_only']
CD_COUNTS = ['experiment', 'group', 'source', 'design_papers', 'papers_with_rows', 'papers_unwritten', 'authors_unwritten',
             'authors_written', 'inconsistent_papers']
CD_HARDCHECK = ['check', 'value', 'threshold', 'status', 'note']

# 2-4 batch noise (recovery_b15 = original E1: patched in the 15-element batch, true / false batch 1; recovery_b1 = all
# batch 1; recovery_b15_all = patched, true and false all in 15-element batches)
NOISE_TOKEN = ['shard', 'arm', 'n_tokens', 'share_equal', 'mean_abs_dnlr', 'median_abs_dnlr', 'p90_abs_dnlr', 'p99_abs_dnlr', 'max_abs_dnlr']
NOISE_RECOVERY = ['shard', 'group', 'layer', 'n_papers', 'recovery_b15', 'recovery_b1', 'recovery_b15_all', 'diff_b15_minus_b1',
                  'diff_b15all_minus_b1', 'paper_num_mean_abs_diff', 'paper_num_p90_abs_diff', 'paper_num_max_abs_diff',
                  'paper_rec_median_abs_diff', 'paper_rec_p90_abs_diff', 'n_papers_gap_ge_0_1']

# 2-8 E1t five titles
E1T_PER_TITLE = ['title', 'group', 'layer', 'n_papers', 'recovery', 'rec_lo', 'rec_hi', 'rec_lo_team', 'rec_hi_team',
                 'gain', 'true_minus_false']
E1T_MEAN5 = ['group', 'layer', 'n_papers', 'recovery_mean5', 'lo', 'hi', 'lo_team', 'hi_team', 'recovery_false0',
             'mean5_minus_false0', 'diff_lo', 'diff_hi', 'rec_min', 'rec_max', 'rec_sd']
E1T_TC = ['layer', 'tc_mean5', 'lo', 'hi', 'lo_team', 'hi_team', 'tc_false0']

# 2-3 X3 by role (behaviour rows and recovery rows keep the frozen stage13_x3_analyze / stage13_x3_recovery columns
# and get these two keys in front)
X3_KEYS = ['stratum', 'role']

# 2-10 M3 all tokens
M3_PERPAPER = ['paper_id', 'group', 'citation_bin', 'team', 'stage11_group', 'split', 'author_first_nlr_published',
               'm3_first_exact', 'm3_first_first', 'm3_first_alltok', 'm3_alltok', 'm3_authormean', 'm3_firsttok_allauthors', 'n_tokens', 'n_authors',
               'm3_role_initial', 'm3_role_given_first', 'm3_role_given_cont', 'm3_role_surname_first', 'm3_role_surname_cont']
M3_SCORES = ['m3_first_exact', 'm3_first_first', 'm3_first_alltok', 'm3_alltok', 'm3_authormean', 'm3_firsttok_allauthors',
             'm3_role_initial', 'm3_role_given_first', 'm3_role_given_cont', 'm3_role_surname_first', 'm3_role_surname_cont']
M3_SUMMARY = ['table', 'score', 'group', 'n', 'mean', 'share_rank1', 'lo_team', 'hi_team', 'lo_paper', 'hi_paper', 'n_bins']

# generic hard-check record (all items)
HARDCHECK = ['item', 'check', 'value', 'threshold', 'status', 'note']


def write_csv(df, cols, path):
    """write df with exactly the declared columns (order fixed here); raises if a declared column is missing."""
    miss = [c for c in cols if c not in df.columns]
    if miss: raise KeyError(f'{path}: missing declared columns {miss}')
    Path(path).parent.mkdir(parents=True, exist_ok=True); df[cols].to_csv(path, index=False)
    return path
