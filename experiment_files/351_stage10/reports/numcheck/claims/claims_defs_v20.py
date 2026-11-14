"""claims_defs v20 (2026-11-14 h3): v19 (unchanged file) + the H3 same-scale numbers (addendum 17 item 2, locked confirmatory test)
written into report / handbook / advisor / Stage 13 script / deck / process report / walkthroughs: probe(T−C) − J-lens(T−C) and
probe − logit lens on the same 9,137 name tokens (L40, L48), and the exploratory side finding (J-lens full-vocabulary vs restricted
target − control at L48). Sources: 381_stage13/summary_h3_samescale_20261114/h3_samescale_paired.csv (tc_diff, tc_diff_lo, tc_diff_hi;
b16 decoder = main) and h3_samescale_table.csv (tc, tc_lo, tc_hi). New ids 'A20-'.
Run with:  CLAIMS_DEFS=claims_defs_v20 bash claims_run.sh"""
from claims_defs_v19 import *          # noqa: F401,F403
from claims_defs_v19 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A20-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
PA = '381_stage13/summary_h3_samescale_20261114/h3_samescale_paired.csv'
TB = '381_stage13/summary_h3_samescale_20261114/h3_samescale_table.csv'
CP = '补充 17 第 2 项 H3 同尺度比较，同一套 9,137 个名字 token，Vpd 姓首 token，4,654 篇，团队聚类 bootstrap 2,000 次（同一组抽样）；'


def T(cid, stmt, f, sel, cols, labs):
    e, lo, hi = cols
    A(cid, stmt, csv(f, e, **sel), CP, '4,654 篇', 3, [l + '#(?= \\[)' for l in labs], sign=True)
    A(cid + '-lo', stmt + '（下限）', csv(f, lo, **sel), CP, '4,654 篇', 3, [l + NUM + r' \[#' for l in labs], sign=False)
    A(cid + '-hi', stmt + '（上限）', csv(f, hi, **sel), CP, '4,654 篇', 3, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=False)


D = ('tc_diff', 'tc_diff_lo', 'tc_diff_hi')
J40 = r'(?:个名字 token 下，|name tokens:? )L40 '
J48 = r'L40 \+0\.\d+ \[' + NUM + ', ' + NUM + r'\](?:、|, )L48 '
T('h3ss-jl40', 'H3 同尺度：probe − J-lens 的 T − C，L40', PA, dict(layer=40, lens='jlens_public_b16'), D, [J40])
T('h3ss-jl48', 'H3 同尺度：probe − J-lens 的 T − C，L48', PA, dict(layer=48, lens='jlens_public_b16'), D, [r'(?:个名字 token 下，|name tokens:? )' + J48])
T('h3ss-lg40', 'H3 同尺度（次要）：probe − logit lens 的 T − C，L40', PA, dict(layer=40, lens='logit_b16'), D, [r'probe − logit lens L40 '])
T('h3ss-lg48', 'H3 同尺度（次要）：probe − logit lens 的 T − C，L48', PA, dict(layer=48, lens='logit_b16'), D, [r'(?:（区间触及 0）、|\(CI touches 0\), )L48 '])
TC = ('tc', 'tc_lo', 'tc_hi')
T('h3ss-jfull48', '探索性：J-lens 全词表 T − C，L48', TB, dict(layer=48, readout='jlens_public_fullvocab'), TC,
  [r'target − control 在 L48 为 ', r'full[- ]vocabulary (?:T − C )?at L48 (?:is )?'])
T('h3ss-jres48', '探索性：J-lens 只在 9,137 个名字 token 内排名的 T − C，L48', TB, dict(layer=48, readout='jlens_public_b16'), TC,
  [r'排名后变为 ', r'name tokens it becomes ', r'9,137 name tokens\) '])
