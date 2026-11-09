"""claims_defs v10 (2026-11-08 d): v9 (unchanged file) + the numbers of documents round d (sync_20261108c_manifest.md "round d (after checks)").
New ids 'A10-'. Sources: 351_stage10/reports/parity_before_tol05_amendment.json runs[1] (main round before the amendment: pairs, pairs > 0.25,
max, contexts, token positions); 381_stage13/b3_33_option2/T_tolerance_pass_rates.csv scope = ALL (rows, share within 0.25 = pre_025_lp, max_adlp);
381_stage13/b3_33_option2/G_per_paper.csv (3-3 papers = rows); 2-11 gate = 381_stage13/b2_gennames_v2/summary/repro_check.json (already v9 A9-B2-11-*,
extra English pattern here); C / D 258 / 462 / 6 bins and 2,103 = v9 sources, extra patterns for the round-d wording.
Run with:  CLAIMS_DEFS=claims_defs_v10 bash claims_run.sh"""
import json
import pandas as pd
from claims_defs_v9 import *          # noqa: F401,F403
from claims_defs_v9 import C, csv, MANUAL, ct, cnt, gv
from claims_defs_v5 import A as _A5, py, jsn
from claims_lib import JL


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A10-' + cid; MANUAL[-1] = c['id']


PB = '351_stage10/reports/parity_before_tol05_amendment.json'


def _run1():
    d = json.loads((JL / PB).read_text())
    return [r for r in d['runs'] if r['created'] == '2026-10-24T23:48:37'][0]


A('L02-pairs', '主轮一致性检查的 lens × 层组合数（修订前）', py(lambda: len(_run1()['max_abs_logit_diff']), 'parity_before_tol05_amendment.json runs[2026-10-24T23:48:37] max_abs_logit_diff 键数', [PB]), '计数', '—', 0,
  [r'# 个 lens × 层组合', r'10 of the # lens × layer pairs', r'10 of # pairs', r'原定 0\.25 时 # 个组合'], sign=False)
A('L02-over', '主轮超过 0.25 的组合数', py(lambda: sum(v > 0.25 for v in _run1()['max_abs_logit_diff'].values()), '同上，max_abs_logit_diff > 0.25 的个数', [PB]), '计数', '—', 0,
  [r'组合中有 # 个超出', r'# of the 25 lens', r'# of 25 pairs', r'25 个组合有 # 个超出'], sign=False)
A('L02-max', '主轮最大差（修订前）', py(lambda: max(_run1()['max_abs_logit_diff'].values()), '同上 max', [PB]), '—', '25 个组合', 3,
  [r'超出 ?0\.25，最大差 #', r'个超出，最大差 #', r'exceeded 0\.25, max #', r'above 0\.25, max #'], sign=False)
A('L02-ctx', '主轮上下文数', py(lambda: _run1()['n_contexts'], '同上 n_contexts', [PB]), '计数', '—', 0, [r'（# 个上下文', r'\(# contexts'], sign=False)
A('L02-pos', '主轮 token 位置数', py(lambda: _run1()['n_token_positions'], '同上 n_token_positions', [PB]), '计数', '—', 0, [r'个上下文、# 个 token 位置', r'contexts, # token positions'], sign=False)
TT = '381_stage13/b3_33_option2/T_tolerance_pass_rates.csv'
A('D14-tol025', '3-3：0.25 容差内比例', csv(TT, 'pre_025_lp', scope='ALL'), 'T_tolerance_pass_rates.csv scope = ALL pre_025_lp', '23,280 行', 2,
  [r'按 0\.25 计 #(?=%)', r'按 0\.25 有 #(?=%)', r'in 3-3, #(?=%)'], sign=False, scale=100)
A('D14-rows', '3-3：比较行数', csv(TT, 'n', scope='ALL'), '同上 n', '—', 0, [r'篇论文的 # 行', r'% of # rows'], sign=False)
GP = '381_stage13/b3_33_option2/G_per_paper.csv'
A('D14-papers', '3-3：论文数', py(lambda: len(pd.read_csv(JL / GP)), 'G_per_paper.csv 行数', [GP]), '计数', '—', 0, [r'3-3 在 # 篇论文', r'rows \(# papers\)'], sign=False)
A('D14-maxadlp', '3-3：bf16 舍入随前向长度变化的最大差', csv(TT, 'max_adlp', scope='ALL'), '同上 max_adlp', '23,280 行', 2,
  [r'最大约 #', r'up to about #', r'up to ~#'], sign=False)
A('B2-11-share-en', '2-11 首名复现率（英文）', jsn('381_stage13/b2_gennames_v2/summary/repro_check.json', ['share']), 'repro_check.json share', '50 篇', 3,
  [r'reproduction # <'], sign=False)
A('R4-nC-deck', 'C 同档篇数（第 77 / 81 页、讲稿）', ct(48, 'n_a'), 'cd_contrasts.csv n_a', '—', 0,
  [r'\(# of 462 C papers', r'within bin # of 462', r'只用到其中 # 篇'], sign=False)
A('R4-nCall-deck', 'C 篇数（第 77 / 81 页）', cnt('C', 'papers_unwritten'), 'cd_counts.csv', '—', 0, [r'258 of # C papers', r'258 of # vs A'], sign=False)
A('R4-bins-deck', '同档引用档数（第 77 页、讲稿）', ct(48, 'n_bins'), 'cd_contrasts.csv n_bins', '—', 0, [r'462 C papers, # bins', r'（# 个引用档，A 323'], sign=False)
A('R4-nA-talk', 'A 同档篇数（讲稿）', ct(48, 'n_b'), 'cd_contrasts.csv n_b', '—', 0, [r'个引用档，A # 篇'], sign=False)
A('R4-denC-talk', 'C 分母（讲稿简写）', gv('E1', 'C', 48, 'denominator'), 'cd_group_values.csv', 'C 462 篇', 3, [r'分母 C #(?=、A)'], sign=False)
A('R4-denA-talk', 'A 分母（讲稿简写）', gv('E1', 'A', 48, 'denominator'), 'cd_group_values.csv', 'A 557 篇', 3, [r'分母 C 0\.\d+、A #(?![\d.]* \[)'], sign=False)
# table P5.1 C row after "2103" -> "2,103": the v9 E2 L52 pattern contained "(2103 authors)"
from claims_defs_v9 import gvs, NUM, CIR
_s = gvs('E2', 'C', 52)
_p = r'n = 507 \(660 authors\) ' + NUM + ' ' + CIR + r'; n = 462 \(2,?103 authors\) ' + NUM + ' ' + CIR + r'; n = 462 \(2,?103 authors\) '
A('R4-C-E2L52', 'C / D 组补全：C 的 E2 阻断损失 L52（表 P5.1）', _s[''], 'cd_group_values.csv', 'C 462 篇', 3, [_p + r'#(?= \[)'])
A('R4-C-E2L52-lo', '同上下限', _s['-lo'], 'cd_group_values.csv', 'C 462 篇', 3, [_p + NUM + r' \[#'])
A('R4-C-E2L52-hi', '同上上限', _s['-hi'], 'cd_group_values.csv', 'C 462 篇', 3, [_p + NUM + r' \[' + NUM + r', #\]'])
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
