"""Batch 3 (addendum 14, items 3-1, 3-2, 3-3): THE column module (fixed rule 4) for every stage13_b3_* file.

Holds paths, layer lists, readouts, conditions, raw npz keys, result-CSV columns and the check thresholds.
No computation. `write_csv` refuses a frame whose columns differ from the declared list.
Plan: 381_stage13/config/prereg_addendum14.json (sha256 below; every b3 script checks it at start).
"""
import hashlib, os
from pathlib import Path

H = Path.home() / 'jlens_work'
BASE = Path('/scratch/zhang.zhiqi2/jlens')
R10 = BASE / '351_stage10'
R13 = BASE / '381_stage13'
R71B = BASE / '351_stage7_1B_terminal'
PLAN = R13 / 'config/prereg_addendum14.json'
PLAN_SHA = '795185e94594a31bf5acc47f49d281c7a28f3251acc6598474b378002e47bf26'


def check_plan():
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED: prereg_addendum14.json sha256 differs')


# ------------------------------------------------------------------ items 3-1 / 3-2 (Stage 10 fast path, new layers)
READOUTS = ['jlens_public', 'logit']                       # plan: logit lens and public J-lens only
CHECK_LAYERS = [24, 48]                                    # recomputed in the same run, hard check vs stored Stage 10
ITEM_LAYERS = {'3-1': [41, 42, 43, 44, 45, 46, 47, 49],
               '3-2': list(range(0, 24))}
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
FALSE = CONDS[1:6]
GROUPS = ['target', 'control']                             # 6,841 papers (group_tight)
N_PAPERS_TC = 6841
STORED_LAYERS = [24, 32, 40, 48] + list(range(50, 63))     # Stage 10 public / logit layers already on disk
FINAL = 63


def item_layers(item): return sorted(set(ITEM_LAYERS[item]) | set(CHECK_LAYERS))
def item_pairs(item): return [(r, l) for r in READOUTS for l in item_layers(item)]
def check_pairs(): return [(r, l) for r in READOUTS for l in CHECK_LAYERS]
def pair_name(r, l): return f'{r}@L{l}'


def s10_roots(item, tiny=False):
    r = R13 / f"b3_tiny{os.environ.get('B3_TINY_SUFFIX', '')}/{item}" if tiny else R13
    tag = item.replace('-', '_')
    return dict(raw=r / f'raw/b3_s10_{tag}', claims=r / f'logs/claims_b3_s10_{tag}', logs=r / 'logs',
                summ=r / f'summary_b3_s10_{tag}', gate=r / f'summary_b3_s10_{tag}/gate.json',
                fail=r / f'summary_b3_s10_{tag}/HARD_CHECK_FAILED', chain=r / f'logs/chain_b3_s10_{tag}',
                report=r / f'reports/b3_{tag}_report.md')


# raw unit file raw/b3_s10_<item>/<cond>/shard_XXX.npz
RAW_S10 = ['row_id', 'rank', 'ties', 'logprob', 'top1',          # [n_pairs, n] in the order of meta['pairs']
           'chk_ref_rank', 'chk_ulps', 'chk_dlogprob',           # [n_check_pairs, n] vs stored Stage 10 (ulps 0 = same rank)
           'meta']

# ------------------------------------------------------------------ check thresholds (plan)
RANK_EXACT_MIN = 0.99         # 3-1/3-2: exact on >= 99% of tokens
ULPS_MAX = 4                  # ... rest within 4 bf16 units of logit
PAPER_SPEC_TOL = 0.005        # L48 paper-level title-specific signal vs published
PAPER_SHARE_WARN = 0.99       # per-paper share within 0.005 (WARN only)
R71B_RANK_MIN = 0.99          # 3-3: 1,166 contexts reproduced, rank match >= 99%

HARDCHECK = ['item', 'check', 'scope', 'value', 'threshold', 'status', 'kind', 'note']
RANK_MATCH = ['item', 'scope', 'readout', 'layer', 'cond', 'n_tokens', 'n_exact', 'share_exact', 'n_mismatch',
              'n_mismatch_le_ulps', 'max_ulps', 'median_ulps_mismatch', 'max_abs_dlogprob', 'max_abs_dlog10rank']

# ------------------------------------------------------------------ 3-1 / 3-2 report tables
POSITIONS = ['all', 'first', 'later']                      # token_index 0 / >= 1
ROLES = ['all', 'initial_first', 'given_first', 'given_cont', 'surname_first', 'surname_cont', 'particle_first', 'punct']
LAYER_SIGNAL = ['readout', 'layer', 'source', 'position', 'role', 'group', 'n_papers', 'spec', 'spec_lo', 'spec_hi',
                'true', 'total', 'topic']
LAYER_TC = ['readout', 'layer', 'source', 'position', 'role', 'n_bins', 'n_target', 'n_control', 'tc_spec', 'tc_lo', 'tc_hi',
            'tc_true', 'tc_true_lo', 'tc_true_hi']
ONSET = ['readout', 'quantity', 'position', 'role', 'group', 'layer_grid', 'onset_excl0', 'onset_sign', 'onset_pos',
         'onset_pos_sustained']

# ------------------------------------------------------------------ item 3-3 (7.1B on the fast path)
R71_LAYERS = [16, 24, 32, 40, 48, 56, 62]
R71_READOUTS = [('final', 63)] + [(m, l) for m in ('jlens', 'vanilla') for l in R71_LAYERS]   # 7.1B names
R71_S10NAME = {'final': 'final', 'jlens': 'jlens_public', 'vanilla': 'logit'}                 # -> Stage 10 readout names
N_TASKS_71B = 15519
N_DONE_71B = 1166
K_WRONG = 20


def r71_roots(tiny=False):
    r = R13 / f"b3_tiny{os.environ.get('B3_TINY_SUFFIX', '')}/3-3" if tiny else R13
    return dict(raw=r / 'raw/b3_71b', claims=r / 'logs/claims_b3_71b', logs=r / 'logs', summ=r / 'summary_b3_71b',
                gate=r / 'summary_b3_71b/gate.json', fail=r / 'summary_b3_71b/HARD_CHECK_FAILED', chain=r / 'logs/chain_b3_71b',
                report=r / 'reports/b3_3_3_report.md')


# raw unit file raw/b3_71b/paper_<paper_id>.npz : one row per (shuffle_index, author_index, token_index)
RAW_71B = ['shuffle_index', 'author_index', 'token_index', 'token_id', 'rank', 'logprob', 'ties', 'top1', 'logit_gold',
           'ref_rank', 'ref_logprob', 'ulps', 'meta']          # [15, n] per readout (R71_READOUTS order); ref_* = old 7.1B (0/NaN = none)
R71_CHECK = ['task_id', 'paper_id', 'shuffle_index', 'author_index', 'token_index', 'token_id', 'mode', 'layer',
             'rank_old', 'rank_new', 'logprob_old', 'logprob_new', 'ulps']
R71_AUTHOR = ['paper_id', 'group', 'author_index', 'mode', 'layer', 'n_tokens', 'true_first_rr', 'wrong_first_rr', 'eff_first_rr',
              'true_cont_rr', 'wrong_cont_rr', 'eff_cont_rr', 'true_all_rr', 'wrong_all_rr', 'eff_all_rr',
              'eff_first_nlr', 'eff_cont_nlr', 'eff_all_nlr', 'eff_first_lp', 'eff_cont_lp', 'eff_all_lp']
R71_PAPER = ['paper_id', 'group', 'mode', 'layer', 'n_authors', 'n_cont_authors', 'eff_first_rr', 'eff_cont_rr', 'eff_all_rr',
             'eff_first_nlr', 'eff_cont_nlr', 'eff_all_nlr', 'eff_first_lp', 'eff_cont_lp', 'eff_all_lp', 'true_all_rr', 'wrong_all_rr']
R71_HC_SUMMARY = ['scope', 'mode', 'layer', 'n_scores', 'n_exact', 'share_exact', 'n_within_4_bf16', 'share_exact_or_within',
                  'max_ulps', 'max_abs_dlogprob', 'max_abs_dlog10rank']
R71_GROUP = ['mode', 'layer', 'metric', 'group', 'n_papers', 'mean', 'lo', 'hi']
R71_PAIRS = ['mode', 'layer', 'metric', 'n_pairs', 'A_minus_B_mean', 'median_difference', 'n_positive', 'lo', 'hi']


def write_csv(df, path, cols):
    if list(df.columns) != list(cols):
        raise ValueError(f'column mismatch for {path}: missing {sorted(set(cols) - set(df.columns))}, extra {sorted(set(df.columns) - set(cols))}')
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp'); df.to_csv(tmp, index=False); tmp.replace(path)
