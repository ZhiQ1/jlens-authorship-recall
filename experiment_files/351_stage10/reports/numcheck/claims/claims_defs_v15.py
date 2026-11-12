"""claims_defs v15 (2026-11-12 i): v14 (unchanged file) + the numbers of documents round i (sync_20261108c_manifest.md "round i").
New ids 'A15-'. Sources: 2-2 F1 split-half = 371_stage12/summary/b2_f1team_readout.csv (F2 with each half lens), b2_f1team_matrix.csv
(cosine / top-10 overlap), b2_f1team_hardcheck.json (= 381_stage13/reports/b2_f1team_report.md); 3-1 extra layers =
381_stage13/summary_b3_s10_3_1/layer_signal.csv and layer_tc.csv (= reports/b3_3_1_report.md §3, team-cluster CIs).
Run with:  CLAIMS_DEFS=claims_defs_v15 bash claims_run.sh"""
import json
import pandas as pd
from claims_defs_v14 import *          # noqa: F401,F403
from claims_defs_v14 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, py
from claims_lib import JL


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A15-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
CI_ = r' \[' + NUM + ', ' + NUM + r'\]'
FR, FM, FH = '371_stage12/summary/b2_f1team_readout.csv', '371_stage12/summary/b2_f1team_matrix.csv', '371_stage12/summary/b2_f1team_hardcheck.json'
CF = '2-2 F1 对半拆分（按作者团队）：F2 名字位置 target − control（引用档内），b2_f1team_readout.csv；'


def f1(L, lens, col):
    return csv(FR, col, position='name', layer=L, lens=lens)


PA = r'L48：A 半 '
PB = PA + NUM + CI_ + r'、B 半 '
for cid, lens, lab in [('f1-A48', 'teamA', PA), ('f1-B48', 'teamB', PB)]:
    A(cid, '2-2：%s L48 target − control' % lens, f1(48, lens, 'tc'), CF + 'tc', '1,183 篇', 3, [lab + '#'])
    A(cid + '-lo', '同上下限', f1(48, lens, 'tc_lo'), CF + 'tc_lo', '1,183 篇', 3, [lab + NUM + r' \[#'])
    A(cid + '-hi', '同上上限', f1(48, lens, 'tc_hi'), CF + 'tc_hi', '1,183 篇', 3, [lab + NUM + r' \[' + NUM + ', #\]'])
A('f1-full48', '2-2：全部 40 条拟合的 lens L48 target − control', f1(48, 'full', 'tc'), CF + 'tc', '1,183 篇', 3, [PB + NUM + CI_ + r'、全部 #'])
for k, lens in enumerate(['teamA', 'teamB', 'full']):
    A('f1-L62-%s' % lens, '2-2：L62 target − control（%s）' % lens, f1(62, lens, 'tc'), CF + 'tc', '1,183 篇', 3, [r'L62：' + ''.join(NUM + ' / ' for _ in range(k)) + '#'])


def _mid():
    d = pd.read_csv(JL / FR); d = d[(d.position == 'name') & d.layer.between(24, 56)]
    ok = d[d.lens.isin(['teamA', 'teamB'])].groupby('layer').tc_lo.apply(lambda s: (s <= 0).all())
    return int(ok.sum()), int(len(ok))


A('f1-mid-n', '2-2：中间层（L24–L56）两半都不显著为正的层数', py(lambda: _mid()[0], 'b2_f1team_readout.csv name 位置 L24–L56，teamA / teamB 的 tc_lo ≤ 0 的层数', [FR]), '计数', '—', 0, [r'（#/7 层）'], sign=False)
A('f1-mid-N', '2-2：中间层层数', py(lambda: _mid()[1], '同上层数', [FR]), '计数', '—', 0, [r'（7/# 层）'], sign=False)
for L, lab in [(24, r'A–B 余弦 L24 '), (40, r'A–B 余弦 L24 0\.\d+、L40 '), (48, r'A–B 余弦 L24 0\.\d+、L40 0\.\d+、L48 ')]:
    A('f1-cos%d' % L, '2-2：A、B 两半 lens 矩阵余弦 L%d' % L, csv(FM, 'cos_A_B', layer=L), 'b2_f1team_matrix.csv cos_A_B', '—', 2, [lab + '#', lab.replace('A–B 余弦', 'A–B cosine') + '#'], sign=False)
A('f1-top10', '2-2：L24 top-10 重合', csv(FM, 'top10_A_B', layer=24), 'b2_f1team_matrix.csv top10_A_B', '—', 2, [r'L24 top-10 重合 #', r'L24 top-10 overlap #'], sign=False)

# ---- 3-1 extra layers
LS, LT = '381_stage13/summary_b3_s10_3_1/layer_signal.csv', '381_stage13/summary_b3_s10_3_1/layer_tc.csv'
C31 = '3-1 补测层（补充 14），target + control 6,841 篇，团队整群区间；'


def sig(ro, L, col):
    return csv(LS, col, readout=ro, layer=L, position='all', role='all', group='target+control')


def tc(ro, L, col):
    return csv(LT, col, readout=ro, layer=L, position='all', role='all')


def _rng(f):
    d = pd.read_csv(JL / LS); d = d[(d.readout == 'jlens_public') & (d.position == 'all') & (d.role == 'all') & (d.group == 'target+control') & d.layer.between(41, 46)]
    return f(d.spec)


A('b31-jl-min', '3-1：J-lens 标题特异信号 L41–L46 最小', py(lambda: _rng(min), 'layer_signal.csv jlens_public target+control L41–L46 spec 最小', [LS]), C31, '6,841 篇', 3, [r'J-lens 在 L41–L46 为 #(?= 到)', r'J-lens (?:is )?#(?= to \+0\.\d+ at L41–L46)'])
A('b31-jl-max', '3-1：同上最大', py(lambda: _rng(max), '同上最大', [LS]), C31, '6,841 篇', 3, [r'J-lens 在 L41–L46 为 ' + NUM + ' 到 #', r'J-lens (?:is )?' + NUM + ' to #(?= at L41–L46)'])
A('b31-jl47', '3-1：J-lens 标题特异信号 L47', sig('jlens_public', 47, 'spec'), C31 + 'spec', '6,841 篇', 3, [r'几乎相同（J-lens #', r'nearly equal \(J-lens #'])
A('b31-jl47-lo', '同上下限', sig('jlens_public', 47, 'spec_lo'), C31, '6,841 篇', 3, [r'几乎相同（J-lens ' + NUM + r' \[#'])
A('b31-jl47-hi', '同上上限', sig('jlens_public', 47, 'spec_hi'), C31, '6,841 篇', 3, [r'几乎相同（J-lens ' + NUM + r' \[' + NUM + ', #\]'])
A('b31-lg47', '3-1：logit 标题特异信号 L47', sig('logit', 47, 'spec'), C31 + 'spec', '6,841 篇', 3, [r'几乎相同（J-lens ' + NUM + CI_ + r'，logit #', r'logit #(?=\) at L47)'])


def _lmax():
    d = pd.read_csv(JL / LT); d = d[(d.readout == 'logit') & (d.position == 'all') & (d.role == 'all') & d.layer.between(41, 49)]
    return d.tc_spec.abs().max()


A('b31-lg-tcmax', '3-1：logit target − control L41–L49 绝对值最大（“都在 ±0.005 以内”）', py(_lmax, 'layer_tc.csv logit L41–L49 |tc_spec| 最大', [LT]), C31, '—', 3,
  [r'target − control 都在 ±#(?= 以内、从 L50)', r'logit target − control within ±#'], sign=False)
for L, lab in [(41, r'为负（L41 '), (47, r'为负（L41 ' + NUM + CI_ + r'，L47 '), (49, r'，L47 ' + NUM + r'，L49 ')]:
    A('b31-jltc%d' % L, '3-1：J-lens target − control L%d' % L, tc('jlens_public', L, 'tc_spec'), C31 + 'tc_spec', '3,734 / 2,182 篇（档内）', 3, [lab + '#'])
A('b31-jltc41-lo', '同上下限', tc('jlens_public', 41, 'tc_lo'), C31, '—', 3, [r'为负（L41 ' + NUM + r' \[#'])
A('b31-jltc41-hi', '同上上限', tc('jlens_public', 41, 'tc_hi'), C31, '—', 3, [r'为负（L41 ' + NUM + r' \[' + NUM + ', #\]'])


def _onset(ro):
    d = pd.read_csv(JL / LT); d = d[(d.readout == ro) & (d.position == 'all') & (d.role == 'all') & d.layer.between(41, 62)].sort_values('layer')
    pos = d[d.tc_lo > 0].layer
    return float(pos.min())


A('b31-lg-on', '3-1：logit target − control 区间不含 0 且为正的最早层（≥ L41）', py(lambda: _onset('logit'), 'layer_tc.csv logit tc_lo > 0 的最早层', [LT]), C31, '—', 0, [r'从 L(?P<v>\d+)(?= 起为正（起始层不变）)'], sign=False)
A('b31-jl-on', '3-1：J-lens target − control 区间不含 0 且为正的最早层', py(lambda: _onset('jlens_public'), 'layer_tc.csv jlens_public tc_lo > 0 的最早层', [LT]), C31, '—', 0, [r'从 L(?P<v>\d+)(?= 起为正，“中间层没有领先”)'], sign=False)

def _lastneg():
    d = pd.read_csv(JL / LT); d = d[(d.readout == 'jlens_public') & (d.position == 'all') & (d.role == 'all') & d.layer.between(41, 62)].sort_values('layer')
    return float(d[d.tc_spec < 0].layer.max())


A('b31-jl-lastneg', '3-1：J-lens target − control 点估计为负的最后一层', py(_lastneg, 'layer_tc.csv jlens_public tc_spec < 0 的最大层（L56 为 +0.007 [−0.014, +0.029]）', [LT]), C31, '—', 0,
  [r'target − control 在 L41–L(?P<v>\d+)(?= 为负)', r'J-lens negative to L(?P<v>\d+)'], sign=False)
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
