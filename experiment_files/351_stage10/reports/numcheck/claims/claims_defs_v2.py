"""claims_defs v2 (2026-11-07): v1 (claims_defs.py, unchanged) + changes after the document sync of 2026-11-07.
Run with:  CLAIMS_DEFS=claims_defs_v2 bash claims_run.sh   (claims_run.sh v2 default, see there).
Changes: (1) report §1 E4b numbers now point at the train-fold-standardised source (e4b_trainstd_compare.md 'new' column,
the file §6.11 uses); the v1 claims E4b-all-L40/L56 keep e4b_split_compare.md for the places that still quote the old version.
(2) patterns for the canonical forms written on 2026-11-07. (3) claims for the provenance sentences of no_data_fixes_20261107.md."""
from claims_defs import *          # noqa: F401,F403  (builds the v1 list C)
import claims_defs as v1
from claims_defs import C, add, csv, md, TS, SC, B, X3P, X1F, PRI, F63, N

ALL_L = ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']
byid = {c['id']: c for c in C}


def extend(cid, pats):
    byid[cid]['occ'] = list(byid[cid]['occ']) + pats


# (1) §1 E4b -> train-fold source.  v1 E4b-all-L40/L56 lose the §1 patterns ("L24 0.050、L40 0.066、L56 0.080")
byid['E4b-all-L40']['occ'] = [p for p in byid['E4b-all-L40']['occ'] if 'L24 0\\.050' not in p]
byid['E4b-all-L56']['occ'] = [p for p in byid['E4b-all-L56']['occ'] if 'L40 0\\.066' not in p]
add('E4b-s1-L24', '§1 E4b 全部论文 L24（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': 'L24'}),
    'E4b probe，按团队分折 + 剔除标题复用 + 训练折内标准化（作业 11500917）；论文 bootstrap', '1,863 篇', 3,
    [r'(?:全部论文标题特异信号|all papers) L24 #(?=[、,] ?L40 0\.061)'], where='#p2-1 §1（中、英）')
add('E4b-s1-L40', '§1 E4b 全部论文 L40（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': 'L40'}), '同上', '1,863 篇', 3,
    [r'L24 0\.050[、,] ?L40 #'], where='#p2-1 §1（中、英）')
add('E4b-s1-L56', '§1 E4b 全部论文 L56（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': 'L56'}), '同上', '1,863 篇', 3,
    [r'L40 0\.061[、,] ?L56 #'], where='#p2-1 §1（中、英）')
for c in C[-3:]:
    c['excl'] = None; c['alt'] = []
extend('E4b-ts-L40', [r'L24 \+0\.050[、，,] ?L40 #(?=[、，,] ?L56 \+0\.075)', r'L40 \+0\.066 → #', r'L40 0\.066 → #', r'L40 #(?= \[0\.047, 0\.076\])'])
extend('E4b-ts-L56', [r'L40 \+0\.061[、，,] ?L56 #', r'L56 \+?0\.080 → \+?#'])
extend('E4b-ts-rmax', [r'L24–L60 为 \+0\.047 到 #'])

# (2) canonical forms written on 2026-11-07
extend('E1-L48', [r'L48 (?:已)?恢复 ?#(?!%)', r'recovers #(?= at L48)'])
extend('E1-L52', [r'L52 起(?:恢复)? ?#(?!%)', r'(?P<v>100)%(?= from L52)'])
extend('S10-L63', [r'#(?= (?:到|to) \+0\.231)'])
extend('S10-L62-max', [r'\+0\.207 (?:到|to) #'])
extend('S10-L48-jmax', [r'L48 (?:略为负|is slightly negative) ?[（(]#(?= (?:到|to) −0\.054)'])
extend('S10-L48-jmin', [r'L48 (?:略为负|is slightly negative) ?[（(]−0\.037 (?:到|to) #'])
extend('A-bin-low', [r'#(?= ?\[0\.317, 0\.377\])'])
extend('A-bin-high', [r'#(?= ?\[0\.591, 0\.701\])'])
extend('X6-min', [r'(?:恢复|recovery) #(?=–1\.017)'])
extend('X6-max', [r'(?:恢复|recovery) 0\.984–#'])
extend('S10-R0', [r'R0 时 #(?=（Stage 10 R0)'])

# (3) provenance sentences added on 2026-11-07 (no_data_fixes_20261107.md)
S8D = '351_stage8/stage8D/summary/primary_questions.csv'
add('F2-pos', 'Stage 8D RQ2 A − B 为正的对数', csv(S8D, 'positive', question='RQ2_matched_A_minus_B'), '计数', '100 对', 0, [r'100 对，#(?= 正)'], sign=False)
add('F2-neg', 'Stage 8D RQ2 A − B 为负的对数', csv(S8D, 'negative', question='RQ2_matched_A_minus_B'), '计数', '100 对', 0, [r'#(?= 负)(?<=正 / \d\d)', r'正 / #(?= 负)'], sign=False)
S74F = '351_stage7_4/summary/jlens_increment_bootstrap.csv'
for k, col in [('', 'mean'), ('-lo', 'ci_low'), ('-hi', 'ci_high')]:
    add('F3-S74' + k, 'Stage 7.4 J-Lens − Vanilla 7 层积分（4 位小数写法）' + k, csv(S74F, col, layer='integrated'), '标题优势之差，7 层积分；论文 bootstrap', '50 篇', 4,
        {'': [r'7 层积分 #(?= \[−0\.0075)'], '-lo': [r'\+0\.0022 \[#'], '-hi': [r'\+0\.0022 \[−0\.0075, #\]']}[k])
LV = dict(metric='level', b='logit', layer=[24, 32, 40, 48], a=['jlens_public', 'jlens_self100', 'jlens_fitA'])
SP = dict(metric='spec', b='logit', layer=[24, 32, 40, 48], a=['jlens_public', 'jlens_self100', 'jlens_fitA'])
add('F4a-lv-min', 'Jacobian − logit：名字名次水平差 L24–L48（最小）', csv(X3P, 'diff', 'min', **LV), '逐篇差均值，三种 J-lens × 4 层取最小', '9,108 篇', 3, [r'高 #(?= 到 \+1\.7)', r'#(?= to \+1\.728)'])
add('F4a-lv-max', '同上（最大）', csv(X3P, 'diff', 'max', **LV), '同上取最大', '9,108 篇', 3, [r'\+0\.176 (?:到|to) #'])
add('F4a-sp-min', 'Jacobian − logit：标题特异信号差 L24–L48（最小，3 位）', csv(X3P, 'diff', 'min', **SP), '同上，spec', '9,108 篇', 3, [r'(?:只多|only) #(?= (?:到|to) \+0\.030)'])
add('F4a-sp-max', '同上（最大，3 位）', csv(X3P, 'diff', 'max', **SP), '同上，spec', '9,108 篇', 3, [r'(?:只多|only) \+0\.007 (?:到|to) #'])
TCL = '351_stage10/summary_extra/X3_tc_spec_vs_logit.csv'
TL = dict(layer=[24, 32, 40, 48, 56])
add('F4b-min', '(Jacobian − logit) 标题特异信号的目标−对照 L24–L56（最小）', csv(TCL, 'tc_spec_minus_logit', 'min', **TL), '引用档内目标−对照；三种 lens × 5 层取最小；论文 bootstrap', '目标 / 对照见文件', 3, [r'L24–L56：#(?= 到 \+0\.006)', r'L24–L56: #'])
add('F4b-max', '同上（最大）', csv(TCL, 'tc_spec_minus_logit', 'max', **TL), '同上取最大', '同上', 3, [r'L24–L56[：:] ?−0\.062 (?:到|to) #'])
add('F9-topic', '名字先验拆解：主题项的目标−对照', csv(PRI, 'topic', readout='final', layer=63, role='all_tokens', group='tc_topic'), 'Stage 12 CPU 拆解，最终输出 L63', '9,108 篇', 3, [r'主题 #', r'topic #'])
add('F9-share', '标题特异部分占真标题差的比例', {'t': 'op', 'op': 'div', 'a': csv(PRI, 'spec', readout='final', layer=63, role='all_tokens', group='tc_spec'),
                                              'b': csv(PRI, 'true', readout='final', layer=63, role='all_tokens', group='tc_true')}, 'tc_spec ÷ tc_true', '—', 0,
    [r'(?:约占|about) #(?=%)'], scale=100, sign=False)
BL = dict(readout=['logit', 'jlens_public', 'jlens_self100', 'jlens_fitA'], layer=[24, 32, 40, 48])
add('F14-min', 'L24–L48 四种读出目标−对照（最小）', csv(B, 'spec_mean_nlr_diff', 'min', **BL), v1.B_DESC + '；四种读出 × 4 层取最小', '3,734 / 2,182', 3, [r'#(?= (?:到|to) \+0\.009)'])
add('F14-max', 'L24–L48 四种读出目标−对照（最大）', csv(B, 'spec_mean_nlr_diff', 'max', **BL), '同上取最大', '3,734 / 2,182', 3, [r'−0\.054 (?:到|to) #'])
for L, k in [(24, ''), (32, '')]:
    for part, col in [('', 'spec_mean_nlr_diff'), ('-lo', 'spec_mean_nlr_lo'), ('-hi', 'spec_mean_nlr_hi')]:
        pat = {'': r'logit lens L%d #(?= \[)' % L, '-lo': r'logit lens L%d \+0\.00\d \[#' % L, '-hi': r'logit lens L%d \+0\.00\d \[\+?0\.00\d, #\]' % L}[part]
        add('F14-logit-L%d%s' % (L, part), 'logit lens L%d 目标−对照%s' % (L, part), csv(B, col, readout='logit', layer=L), v1.B_DESC, '3,734 / 2,182', 3, [pat])
CB = '351_stage10/summary_r0r1/tc_R1target_vs_R0control.csv'
add('F15-L59', 'R1 目标 vs R0 对照 public L59', csv(CB, 'spec_mean_nlr_diff', readout='jlens_public', layer=59), v1.B_DESC, 'C 391 / B 885', 3, [r'L59 #(?=）)', r'L59 #(?=\))'])
add('F15-L48', 'R1 目标 vs R0 对照 public L48', csv(CB, 'spec_mean_nlr_diff', readout='jlens_public', layer=48), v1.B_DESC, 'C 391 / B 885', 3, [r'L48 #(?=；logit lens 从 L51)'])
WM = '351_stage10/summary_r0r1/R1_author_written_minus_missed.csv'
for cid, L, col, pat in [('F15-wm-L54', 54, 'spec_diff', r'L54 #(?= \[\+0\.015)'), ('F15-wm-L54-lo', 54, 'spec_lo', r'L54 \+0\.038 \[#'), ('F15-wm-L54-hi', 54, 'spec_hi', r'L54 \+0\.038 \[\+0\.015, #\]'),
                         ('F15-wm-L62', 62, 'spec_diff', r'L62 #(?=）)'), ('F15-wm-63', 63, 'spec_diff', r'最终输出 #(?= \[\+0\.168)'), ('F15-wm-63-lo', 63, 'spec_lo', r'\+0\.199 \[#(?=, \+0\.232)'),
                         ('F15-wm-63-hi', 63, 'spec_hi', r'\+0\.199 \[\+0\.168, #\]')]:
    add(cid, 'R1 论文内 写对 − 未写对（%s）' % col, csv(WM, col, readout='final' if L == 63 else 'jlens_public', layer=L, excl_first_author=False),
        '论文内配对差，标题特异信号；论文 bootstrap', '495 篇', 3, [pat])
add('F15-wm-n', 'R1 论文内比较篇数', csv(WM, 'n_papers', readout='final', layer=63, excl_first_author=False), '计数', '—', 0, [r'#(?= 篇，论文 bootstrap 95% CI；351_stage10/summary_r0r1/R1_author)'], sign=False)
GT = '391_groups/summary_table.md'
for cid, grp, k, part, pat in [('F16-U0', 'U0', 1, 'est', r'U0（R0 × 识别不确定）#'), ('F16-U0-lo', 'U0', 1, 'lo', r'\+0\.287 \[#'), ('F16-U0-hi', 'U0', 1, 'hi', r'\+0\.287 \[\+0\.277, #\]'),
                               ('F16-A', 'A', 1, 'est', r'介于 A #'), ('F16-B', 'B', 1, 'est', r'与 B #'),
                               ('F17-Cw', 'C', 2, 'est', r'已写出作者 #'), ('F17-Cw-lo', 'C', 2, 'lo', r'\+0\.771 \[#'), ('F17-Cw-hi', 'C', 2, 'hi', r'\+0\.771 \[\+0\.743, #\]'),
                               ('F17-Cu', 'C', 1, 'est', r'未写出作者 #(?= \[\+0\.526)'), ('F17-Cu-lo', 'C', 1, 'lo', r'\+0\.550 \[#'), ('F17-Cu-hi', 'C', 1, 'hi', r'\+0\.550 \[\+0\.526, #\]')]:
    NUMR = r'[+\-]\d\.\d+'
    cell = {'est': r'(%s) \[%s, %s\]' % (NUMR, NUMR, NUMR), 'lo': r'%s \[(%s), %s\]' % (NUMR, NUMR, NUMR), 'hi': r'%s \[%s, (%s)\]' % (NUMR, NUMR, NUMR)}[part]
    add(cid, '分组对比 %s 组（%s 列，%s）' % (grp, '未写出' if k == 1 else '已写出', part),
        {'t': 'mdre', 'f': GT, 're': r'^\| %s \| ' % grp + r'[^|]*\| ' * (k - 1) + cell, 'nth': 0},
        '最终输出 L63 标题特异信号简单平均；团队聚类 95% CI', '见同格 n', 3, [pat])
for cid, grp, k, pat in [('F16-U0-n', 'U0', 1, r'n = #(?= \(7298)'), ('F17-Cw-n', 'C', 2, r'n = #(?= \(660)'), ('F17-Cu-n', 'C', 1, r'n = #(?= \(2103)')]:
    add(cid, '分组对比 %s 组篇数' % grp, {'t': 'mdre', 'f': GT, 're': r'^\| %s \|' % grp + r'[^|]*\|' * (k - 1) + r'[^|]*?n = (\d+)', 'nth': 0}, '计数', '—', 0, [pat], sign=False)
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])

# review of the first v2 run (out_20261107_014559): tighten the new patterns
byid = {c['id']: c for c in C}
def _swap(cid, old, new):
    byid[cid]['occ'] = [new if p == old else p for p in byid[cid]['occ']]
_swap('S10-L63', r'#(?= (?:到|to) \+0\.231)', r'(?P<v>\+0\.20\d)(?= (?:到|to) \+0\.231)')
_swap('S10-L62-max', r'\+0\.207 (?:到|to) #', r'\+0\.207 (?:到|to) (?P<v>\+0\.23\d)')
_swap('E1-L48', r'L48 (?:已)?恢复 ?#(?!%)', r'L48 (?:已)?恢复 ?(?P<v>0\.8\d\d)(?![\d%])')
_swap('E1-L52', r'L52 起(?:恢复)? ?#(?!%)', r'L52 起(?:恢复)? ?(?P<v>0\.99\d)(?![\d%–])')
byid['F9-share']['occ'] = [r'标题特异部分约占 #(?=%)', r'title-specific part is about #(?=%)']
byid['F15-wm-L62']['occ'] = [r'L54 \+0\.038 \[\+0\.015, \+0\.060\]，L62 #']
for suf, pat in [('', r'、L32 #(?= \[\+?0\.000)'), ('-lo', r'L32 \+0\.005 \[#'), ('-hi', r'L32 \+0\.005 \[\+?0\.000, #\]')]:
    byid['F14-logit-L32' + suf]['occ'] = [pat]
