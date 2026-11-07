"""Hand-curated claims registry for the strict check.

Each claim = one result number used in a CONCLUSION of the Stage 1-13 report (overview 主要结论 + 对照表, Part 1 摘要/综合,
Part 2 §1 摘要 / §7 结论, Part 3 三种口径表, Part 4 预注册/假设表, Part 5 分组主要发现), with:
  sel   explicit selector (claims_lib.select reads the value from the result file; nothing typed by hand)
  comp  how the number was computed
  n     sample size (as stated by the source)
  dec   decimals of the proposed canonical form; scale 100 for pp / %
  occ   regexes that find every place the number is written, in every document.  '#' = the captured number.
        An entry may be (regex, near_regex, window): the match only counts if near_regex occurs within +-window chars.
Values in 'stmt' are descriptions only; the check never uses them.
"""
import pandas as pd
from claims_lib import JL

B = '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'
BR0 = '351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv'
CA = '351_stage10/summary_r0/target_R1_minus_R0_within_bin.csv'
CB = '351_stage10/summary_r0r1/tc_R1target_vs_R0control.csv'
X1F = '351_stage10/summary_extra/X1_by_format.csv'
X3M = '351_stage10/summary_extra/X3_means.csv'
X3P = '351_stage10/summary_extra/X3_pairwise.csv'
E1 = '361_stage11/summary/E1_recovery.csv'
E2 = '361_stage11/summary/E2_knockout.csv'
P1 = '371_stage12/summary/P1_patch_pos.csv'
PRI = '371_stage12/summary_cpu/A_prior_decomposition.csv'
GP = '391_groups/primary.csv'
TS = '381_stage13/reports/e4b_trainstd_compare.md'
SC = '381_stage13/reports/e4b_split_compare.md'
AT = '381_stage13/reports/e4b_alltok.md'
X7 = '381_stage13/reports/x7_report.md'
X6 = '381_stage13/reports/x6_report.md'
S8 = '351_stage8/stage8D/summary/primary_questions.csv'
AUD = '351_all/351_audit.json'

N = r'(?<![A-Za-z0-9_.])(?P<v>[+−\-]?\d[\d,]*(?:\.\d+)?)(?![\d])'
SIG = r'[+−\-]?'

B_DESC = '真标题 − 5 个假标题平均的标题特异信号；引用档内 目标−对照 之差（10 档，档内篇数加权）；论文 bootstrap 95% CI（351_stage10.py stratified_diff）'


def csv(f, col, agg=None, **w):
    return {'t': 'csv', 'f': f, 'col': col, 'where': w, 'agg': agg}


def md(f, head, col=None, part='est', row=None, cols=None, agg=None, nth=0):
    return {'t': 'mdcell', 'f': f, 'head': head, 'col': col, 'cols': cols, 'part': part, 'row': row or {}, 'agg': agg, 'nth': nth}


# --------------------------------------------------------------------- small documented computations
def _e4b_counts(group=None, recall=None):
    d = pd.read_parquet(JL / '381_stage13/summary_cpu_trainstd/perpaper_probe_spec.parquet')
    d = d[(d.source == 'X1') & (d.split == 'group') & (d.excl == 'title-reuse') & (d.layer == 24) & (~d.dropped)]
    d = d[d.control == d.control.iloc[0]].drop_duplicates('paper_id')
    p = pd.read_parquet(JL / '351_stage10/cohort/papers.parquet')[['paper_id', 'group_tight']]
    d = d.merge(p, on='paper_id', how='left')
    if group:
        d = d[d.group_tight.isin(group)]
    return len(d)


E4B_FILES = ['381_stage13/summary_cpu_trainstd/perpaper_probe_spec.parquet', '351_stage10/cohort/papers.parquet']
E4B_DESC = ('perpaper_probe_spec.parquet 行 source=X1, split=group, excl=title-reuse, layer=24, dropped=False（去重 paper_id）'
            '，并按 paper_id 连 cohort/papers.parquet 的 group_tight 计数')


def _s73(stat):
    d = pd.read_csv(JL / '351_stage7_3/summary/paper_null_distribution.csv')
    d = d[(d.pool == 'combined') & (d['mode'] == 'jlens_L56')]
    assert len(d) == 50, len(d)
    return d.title_advantage.mean() if stat == 'mean' else (d.title_advantage > 0).sum()


def _s8_drop10():
    d = pd.read_csv(JL / '351_stage8/stage8D/summary/matched_pair_differences.csv')
    d = d[d['mode'] == 'jlens_L56'].sort_values('A_minus_B', ascending=False)
    assert len(d) == 100, len(d)
    return d.A_minus_B.iloc[10:].mean()


C = []


def add(id, stmt, sel, comp, n, dec, occ, scale=1, sign=True, where='', canon=None, note=''):
    C.append(dict(id=id, stmt=stmt, sel=sel, comp=comp, n=n, dec=dec, occ=occ, scale=scale, sign=sign, where=where,
                  canon=canon, note=note))


# ===================================================================== Stage 10 main result (B_spec, final L63)
F63 = dict(readout='final', layer=63)
add('S10-L63', '输出处（L63）目标−对照标题特异差', csv(B, 'spec_mean_nlr_diff', **F63), B_DESC, '目标 3,734 / 对照 2,182 篇（引用档内可用）', 3,
    [r'#(?= ?\[\+?0\.19\d, ?\+?0\.220\])', r'(?:输出|output|final|L63)[^\d\[]{0,12}#(?=（|\(|，|,|；| 到 \+0\.23)',
     r'(?:从 |from )#(?: 变为| to \+0\.199)', r'(?:输出处|在输出层|输出层)(?:约|为|是)? ?#'],
    where='#ov 主要结论；#p2-1 §1；#p2-7 §7；#p3-r0r1 表')
add('S10-L63-lo', '同上 95% CI 下限', csv(B, 'spec_mean_nlr_lo', **F63), B_DESC, '同上', 3,
    [r'\+?0\.207 ?\[\+?#, ?\+?0\.220\]'])
add('S10-L63-hi', '同上 95% CI 上限', csv(B, 'spec_mean_nlr_hi', **F63), B_DESC, '同上', 3,
    [r'\+?0\.207 ?\[\+?0\.19\d, ?\+?#\]'])
add('S10-L63-na', '该比较的目标组篇数', csv(B, 'n_a', **F63), '引用档内目标组篇数（列 n_a）', '—', 0,
    [(r'目标 ?#(?: 篇)? ?(?:\+|vs|、|/) ?对照', r'B_spec_target_vs_control_within_bin\.csv|0\.207', 260),
     (r'#(?: 篇)? ?(?:\+|vs) ?(?:对照 ?)?2,1\d\d', None, 0), (r'#(?: target)? ?\+ ?2,182', None, 0)], sign=False)
add('S10-L63-nb', '该比较的对照组篇数', csv(B, 'n_b', **F63), '引用档内对照组篇数（列 n_b）', '—', 0,
    [(r'目标 ?[\d,]+(?: 篇)? ?(?:\+|vs|、|/) ?对照 ?#', r'B_spec_target_vs_control_within_bin\.csv|0\.207', 260),
     (r'3,734(?: target)? ?(?:\+|vs) ?(?:对照 ?)?#', None, 0)], sign=False)
add('S10-L62-min', 'L62 四种读出目标−对照（最小）', csv(B, 'spec_mean_nlr_diff', 'min', readout=['logit', 'jlens_public', 'jlens_self100', 'jlens_fitA'], layer=62),
    B_DESC + '；四种读出取最小', '3,734 / 2,182', 3, [r'(?<![\d.])#(?=[–\-]0\.23\d)', r'#(?= 到 \+0\.23(?!\d))'])
add('S10-L62-max', 'L62 四种读出目标−对照（最大）', csv(B, 'spec_mean_nlr_diff', 'max', readout=['logit', 'jlens_public', 'jlens_self100', 'jlens_fitA'], layer=62),
    B_DESC + '；四种读出取最大', '3,734 / 2,182', 3, [r'0\.22\d[–\-]#', r'\+0\.21 到 #', r'\+0\.21 to #'])
add('S10-L48-jmax', 'L48 三种 J-lens 目标−对照（离 0 最近）', csv(B, 'spec_mean_nlr_diff', 'max', readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=48),
    B_DESC + '；三种 J-lens 取最大', '3,734 / 2,182', 3, [r'L48 为 #(?= 到 −0\.05)', r'#(?= 到 −0\.05)', r'(?:L48 |L48 is )#(?= to −0\.05)'], sign=True)
add('S10-L48-jmin', 'L48 三种 J-lens 目标−对照（最负）', csv(B, 'spec_mean_nlr_diff', 'min', readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=48),
    B_DESC + '；三种 J-lens 取最小', '3,734 / 2,182', 3, [r'−0\.0[34]\d? (?:到|to) #'])
add('S10-logit-L56', 'logit lens L56 目标−对照', csv(B, 'spec_mean_nlr_diff', readout='logit', layer=56), B_DESC, '3,734 / 2,182', 3,
    [r'(?:L56 已有|L56 \+0\.0\d\d|already (?:shows|gives) |logit L50 \+0\.007，L56 |logit L50 \+0\.007, L56 )#', r'#(?= ?\[0\.050, 0\.080\])'])
add('S10-logit-L50', 'logit lens L50 目标−对照', csv(B, 'spec_mean_nlr_diff', readout='logit', layer=50), B_DESC, '3,734 / 2,182', 3, [r'logit L50 #'])
add('S10-logit-L60', 'logit lens L60 目标−对照', csv(B, 'spec_mean_nlr_diff', readout='logit', layer=60), B_DESC, '3,734 / 2,182', 3, [r'L60 #(?=，L62 \+0\.229|, L62 \+0\.229)'])
add('S10-logit-L62', 'logit lens L62 目标−对照', csv(B, 'spec_mean_nlr_diff', readout='logit', layer=62), B_DESC, '3,734 / 2,182', 3, [r'L62 #(?=，输出 \+0\.207|, output \+0\.207)', r'#(?=\[0\.213, 0\.245\])'])
add('S10-J-L56-min', '三种 J-lens L56 目标−对照（最小）', csv(B, 'spec_mean_nlr_diff', 'min', readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=56), B_DESC, '3,734 / 2,182', 3, [r'L56 约为 0（#', r'about 0 at L56 \(#'])
add('S10-J-L56-max', '三种 J-lens L56 目标−对照（最大）', csv(B, 'spec_mean_nlr_diff', 'max', readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=56), B_DESC, '3,734 / 2,182', 3, [r'L56 约为 0（\+0\.00\d 到 #', r'about 0 at L56 \(\+0\.00\d to #'])

# ===================================================================== R0 / R1 views
add('S10-R0', '只用 R0：A − B 输出处', csv(BR0, 'spec_mean_nlr_diff', **F63), B_DESC + '；两组都只保留 R0', 'A 3,423 / B 2,151 篇', 3,
    [r'#(?= ?\[\+?0\.18\d, ?\+?0\.21\d\])', r'(?:变为|to|→ ?)#(?=，|,|（| at| the)', r'R0[^\d]{0,12}#(?=（|\()'])
add('S10-R0-lo', '同上下限', csv(BR0, 'spec_mean_nlr_lo', **F63), B_DESC, '同上', 3, [r'\+?0\.199 ?\[\+?#, ?\+?0\.21\d\]'])
add('S10-R0-hi', '同上上限', csv(BR0, 'spec_mean_nlr_hi', **F63), B_DESC, '同上', 3, [r'\+?0\.199 ?\[\+?0\.18\d, ?\+?#\]'])
add('S10-R0-na', '只用 R0 的 A 篇数', csv(BR0, 'n_a', **F63), '列 n_a', '—', 0, [r'#(?: 篇)? ?(?:\+|vs|/) ?(?:B ?)?2,15\d'], sign=False)
add('S10-R0-nb', '只用 R0 的 B 篇数', csv(BR0, 'n_b', **F63), '列 n_b', '—', 0, [r'3,42\d(?: 篇)? ?(?:\+|vs|/) ?(?:B ?)?#'], sign=False)
add('S10-CB', 'R1 口径（C − B，R1 target vs R0 control）输出处', csv(CB, 'spec_mean_nlr_diff', **F63), B_DESC + '；R1 目标 vs R0 对照，7 档', 'C 391 / B 885 篇', 3,
    [r'#(?= ?\[\+?0\.34\d, ?\+?0\.40\d\])'])
add('S10-CB-lo', '同上下限', csv(CB, 'spec_mean_nlr_lo', **F63), B_DESC, '同上', 3, [r'\+?0\.372 ?\[\+?#, ?\+?0\.40\d\]'])
add('S10-CB-hi', '同上上限', csv(CB, 'spec_mean_nlr_hi', **F63), B_DESC, '同上', 3, [r'\+?0\.372 ?\[\+?0\.34\d, ?\+?#\]'])
add('S10-CA', 'C − A（认得出论文里 R1 − R0）输出处', csv(CA, 'spec_mean_nlr_diff', **F63), B_DESC + '；目标组内 R1 − R0，9 档', 'C 485 / A 3,204 篇', 3,
    [r'#(?= ?\[\+?0\.08\d, ?\+?0\.13\d\])', r'C 比 A 强（#', r'约 #(?=（Stage 10 R0/R1 分析 C − A)'])
add('S10-CA-lo', '同上下限', csv(CA, 'spec_mean_nlr_lo', **F63), B_DESC, '同上', 3, [r'\+?0\.110 ?\[\+?#, ?\+?0\.13\d\]'])
add('S10-CA-hi', '同上上限', csv(CA, 'spec_mean_nlr_hi', **F63), B_DESC, '同上', 3, [r'\+?0\.110 ?\[\+?0\.08\d, ?\+?#\]'])
add('S10-pool-R0', '合并口径 − R0 口径（约 0.01）', {'t': 'op', 'op': 'sub', 'a': csv(B, 'spec_mean_nlr_diff', **F63), 'b': csv(BR0, 'spec_mean_nlr_diff', **F63)},
    '两个点估计之差', '—', 2, [r'只差约 #'], sign=False)

# ===================================================================== Stage 10 follow-ups X1 / X2 / X3 / citations
add('X3-L62-pub', 'L62 public J-lens 标题特异信号（全部论文均值）', csv(X3M, 'mean', layer=62, metric='spec', readout='jlens_public'),
    '真标题 − 5 个假标题平均，逐篇均值；论文 bootstrap', '9,108 篇', 3, [r'(?:L62 ?约|约|均值) ?#(?=（|\(|）)', r'全部 9,108 篇均值 #'], sign=False)
add('X3-L62-min', '三种 J-lens L62 标题特异信号（最小）', csv(X3M, 'mean', 'min', layer=62, metric='spec', readout=['jlens_public', 'jlens_self100', 'jlens_fitA']),
    '同上，三种 J-lens 取最小', '9,108 篇', 3, [r'#(?=[–\-]0\.44\d)'], sign=False)
add('X3-L62-max', '三种 J-lens L62 标题特异信号（最大）', csv(X3M, 'mean', 'max', layer=62, metric='spec', readout=['jlens_public', 'jlens_self100', 'jlens_fitA']),
    '同上，三种 J-lens 取最大', '9,108 篇', 3, [r'0\.43\d[–\-]#'], sign=False)
add('X3-JmL-min', 'J-lens − logit lens 标题特异信号 L24–L48（最小）', csv(X3P, 'diff', 'min', metric='spec', b='logit', layer=[24, 32, 40, 48], a=['jlens_public', 'jlens_self100', 'jlens_fitA']),
    'Jacobian lens − logit lens 的逐篇差均值，L24–L48 四层 × 三种 J-lens 取最小', '9,108 篇', 2, [r'#(?= 到 \+0\.03（Stage 10 补充 X3| to \+0\.03\(Stage 10 follow-up X3)'])
add('X3-JmL-max', '同上（最大）', csv(X3P, 'diff', 'max', metric='spec', b='logit', layer=[24, 32, 40, 48], a=['jlens_public', 'jlens_self100', 'jlens_fitA']),
    '同上取最大', '9,108 篇', 2, [r'\+0\.01 (?:到|to) #(?=（Stage 10 补充 X3|\(Stage 10 follow-up X3)'])
add('X1-init-later', '首字母开头：后续 token 的目标−对照', csv(X1F, 'spec_tc', format='initial_first', position='later_tokens', readout='final', layer=63),
    '真标题 − 5 个假标题平均，最终输出 L63，引用档内目标−对照', '8,275 篇', 3,
    [r'目标−对照 #(?=，首字母)', r'target − control #(?= versus)', r'#(?= ?\[0\.237, 0\.269\])'])
add('X1-init-first', '首字母开头：首字母 token 的目标−对照', csv(X1F, 'spec_tc', format='initial_first', position='first_token', readout='final', layer=63), '同上', '8,275 篇', 3,
    [r'首字母本身 #', r'versus #(?= on the initial)'])
add('X1-given-first', '名开头：名 token 的目标−对照', csv(X1F, 'spec_tc', format='given_first', position='first_token', readout='final', layer=63), '同上', '4,157 篇', 3,
    [r'#(?= 与 \+0\.202| and \+0\.202)'])
add('X1-given-later', '名开头：后续 token 的目标−对照', csv(X1F, 'spec_tc', format='given_first', position='later_tokens', readout='final', layer=63), '同上', '4,157 篇', 3,
    [r'\+0\.174 (?:与|and) #'])
add('X2-rho', '标题特异信号与引用数的 Spearman ρ（最终输出）', csv('351_stage10/summary_extra/X2_spearman.csv', 'spearman_rho', readout='final', layer=63, group='all', metric='spec'),
    'Spearman 秩相关；论文 bootstrap 95% CI', '9,108 篇', 3, [r'ρ ?(?:=|＝) ?#', r'ρ #(?= ?\[)', r'Spearman ρ #'], sign=False)
add('X2-rho-lo', '同上下限', csv('351_stage10/summary_extra/X2_spearman.csv', 'rho_lo', readout='final', layer=63, group='all', metric='spec'), '同上', '9,108 篇', 3,
    [r'0\.451 ?\[#, 0\.46\d\]'], sign=False)
add('X2-rho-hi', '同上上限', csv('351_stage10/summary_extra/X2_spearman.csv', 'rho_hi', readout='final', layer=63, group='all', metric='spec'), '同上', '9,108 篇', 3,
    [r'0\.451 ?\[0\.43\d, #\]'], sign=False)
add('X1c-all', '第 1 个 token 进前 10 与否，后续 token 均值差（全部）', csv('351_stage10/summary_extra/X1_cond.csv', 'later_level_diff', unit='token', readout='final', layer=63, group='all'),
    '后续 token log10(1/rank) 均值：首 token 进前 10 − 未进；论文 bootstrap', '33,780 个作者上下文', 3, [r'#(?= ?\[0\.02\d, 0\.05\d\])', r'只容易一点（#', r'slightly easier overall \(#'])
add('X1c-given', '完整名进前 10 时姓更容易', csv('351_stage10/summary_extra/X1_cond_by_first_role.csv', 'diff', readout='final', layer=63, first_role='given_first'),
    '同上，名开头的上下文', '8,876 个上下文', 3, [r'#(?= ?\[0\.16\d, 0\.27\d\])', r'明显更容易（#', r'clearly easier \(#'])
add('X1c-init', '首字母开头时的同一差值', csv('351_stage10/summary_extra/X1_cond_by_first_role.csv', 'diff', readout='final', layer=63, first_role='initial_first'),
    '同上，首字母开头', '24,739 个上下文', 3, [r'(?:首字母开头|initial first) #'])
AG = '351_stage10/summary_title/A_group_bin_layer.csv'
add('A-bin-low', '目标组 0-2 引用档标题特异信号', csv(AG, 'spec_mean_nlr_mean', group_tight='target', citation_bin='0-2', readout='final', layer=63),
    '目标组该档逐篇均值（真标题 − 5 假标题平均，最终输出）', '该档目标篇数见同行 n_papers', 3, [r'(?:从|from) #(?= 到 \+0\.64| to \+0\.64)', r'0-2 档 #', r'#(?= in 0-2)'])
add('A-bin-high', '目标组 4097+ 引用档标题特异信号', csv(AG, 'spec_mean_nlr_mean', group_tight='target', citation_bin='4097+', readout='final', layer=63),
    '同上，4097+ 档', '同上', 3, [r'\+0\.3\d (?:到|to) #', r'4097\+ 档 #', r'#(?= in 4097\+)'])

# ===================================================================== Stage 11-13 interventions
add('E1-L48', 'E1 替换 L48 恢复比例（全部）', csv(E1, 'recovery', group='all', layer=48),
    'R = mean(替换 − 假) ÷ mean(真 − 假)，最终输出名字 token；真标题→false_0，标题后全部位置；论文 bootstrap', '目标 593 + 对照 593 篇', 3,
    [r'L48 #(?= ?\[)', r'L48 (?:已)?恢复 ?#(?=%)', r'recovers #(?=% at L48)'], scale=1, sign=False, note='“82%”按 ×100 比较')
add('E1-L48-lo', '同上下限', csv(E1, 'rec_lo', group='all', layer=48), '同上', '同上', 3, [r'L48 0\.825 \[#'], sign=False)
add('E1-L48-hi', '同上上限', csv(E1, 'rec_hi', group='all', layer=48), '同上', '同上', 3, [r'L48 0\.825 \[0\.80\d, #\]'], sign=False)
add('E1-L52', 'E1 替换 L52 恢复比例（全部）', csv(E1, 'recovery', group='all', layer=52), '同上', '同上', 3, [r'L52 #(?=；|;|）|\))'], sign=False)
add('E2-L52', 'E2 从 L52 起阻断对标题注意力的损失比例', csv(E2, 'loss_fraction', group='all', start_layer=52),
    '损失比例 = (真 − 阻断) ÷ (真 − 假)，标题后全部位置不看标题，从 L52 到末层；论文 bootstrap', '593 + 593 篇', 3,
    [r'损失比例 #', r'loss fraction #'])
add('E2-L52-lo', '同上下限', csv(E2, 'lo', group='all', start_layer=52), '同上', '同上', 3, [r'0\.007 \[#, 0\.01\d\]'])
add('E2-L52-hi', '同上上限', csv(E2, 'hi', group='all', start_layer=52), '同上', '同上', 3, [r'0\.007 \[0\.00\d, #\]'])
add('P1-names', 'P1 只换名字位置 L52 恢复', csv(P1, 'recovery', layer=52, item='names', group='all'), 'Stage 12 P1 逐位置替换，真标题→false_0，最终输出恢复比例', 'Stage 11 样本 1,186 篇', 3,
    [r'名字位置 L52 #', r'names L52 #', r'L52 恢复 #(?=，只换)', r'recover #(?= at L52)'], sign=False)
add('P1-colon', 'P1 单个位置最大（":" L52）', csv(P1, 'recovery', 'max', layer=52, group='all', item=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9']),
    '同上，p1–p9 单个位置取最大（p1 = ":"，见 371_stage12/reports/stage12_report.md 第 5 行）', '同上', 3,
    [r'":" L52 #', r'最多 #', r'at most #'], sign=False)
add('X7-c-L52', 'X7 对照组论文特有阻断损失 S(L52)', md(X7, r'^## control', cols=[3], row={'block from': 'L52'}),
    'S = 真标题运行损失 − false_0 运行损失；团队聚类 95% CI', '对照 593 篇', 3, [r'(?:control 593 (?:篇|papers)：?:? ?L52 |对照 \+?)#(?=、对照 S\(L54\)|，L54|, L54)'])
add('X7-c-L54', 'X7 对照组 S(L54)', md(X7, r'^## control', cols=[3], row={'block from': 'L54'}), '同上', '同上', 3, [r'(?:L54 |S\(L54\) )#'])
add('X7-c-L56', 'X7 对照组 S(L56)', md(X7, r'^## control', cols=[3], row={'block from': 'L56'}), '同上', '同上', 3, [r'(?:L56 |S\(L56\) )#(?=；|;|，|\)|）)'])
add('X7-t-L52', 'X7 目标组 S(L52)', md(X7, r'^## target', cols=[3], row={'block from': 'L52'}), '同上', '目标 593 篇', 3, [r'目标 #(?=、对照)', r'target #(?=, control \+0\.051)'])
add('X6-min', 'X6 五个假标题 R(L52) 最小（目标、对照）', md(X6, r'^## (target|control)', cols=['false_0', 'false_1', 'false_2', 'false_3', 'false_4'], row={'layer': 'L52'}, agg='min'),
    'E1 替换分别用 false_0–false_4；目标与对照两张表取最小（取第 1 张匹配表 = target）', '593 + 593 篇', 3, [r'R\(L52\) #(?=–)', r'恢复 #(?=–1\.0)', r'recovery #(?=–1\.0)'], sign=False,
    note='选择器只读第一张匹配表（target）；control 表最小值另列 X6-min-c')
add('X6-min-c', 'X6 对照组五个假标题 R(L52) 最小', md(X6, r'^## control', cols=['false_0', 'false_1', 'false_2', 'false_3', 'false_4'], row={'layer': 'L52'}, agg='min'), '同上', '593 篇', 3, [], sign=False)
add('X6-max', 'X6 五个假标题 R(L52) 最大（对照表）', md(X6, r'^## control', cols=['false_0', 'false_1', 'false_2', 'false_3', 'false_4'], row={'layer': 'L52'}, agg='max'),
    '同上；control 表取最大', '593 篇', 3, [r'R\(L52\) 0\.98\d–#', r'0\.98–#', r'恢复 0\.98–#'], sign=False)

# ===================================================================== Stage 13 E4b probe (title position)
add('E4b-all-L24', 'E4b probe 全部论文标题特异信号 L24（复核，全样本标准化版）', md(SC, r'^## Controls', col='group / dropped', row={'layer': 'L24', 'control': 'probe (as in Stage 11)'}),
    '标题最后一个 token 的线性 probe，只打分第一个名字 token，真标题 − false_0；按作者团队分折 + 剔除标题复用；论文 bootstrap', '1,863 篇', 3,
    [r'L24 #(?=、L40 \+?0\.06\d、L56|, L40 \+?0\.06\d, L56| / L40)', r'L24 为 #(?=（原来)'])
add('E4b-all-L40', '同上 L40（全样本标准化版）', md(SC, r'^## Controls', col='group / dropped', row={'layer': 'L40', 'control': 'probe (as in Stage 11)'}), '同上', '1,863 篇', 3,
    [r'L40 (?:为 )?#(?=（原来 \+0\.062)', r'L24 0\.050、L40 #', r'L24 0\.050, L40 #'])
add('E4b-all-L56', '同上 L56（全样本标准化版）', md(SC, r'^## Controls', col='group / dropped', row={'layer': 'L56', 'control': 'probe (as in Stage 11)'}), '同上', '1,863 篇', 3,
    [r'L56 (?:为 )?#(?=（原来 \+0\.081)', r'L40 0\.066、L56 #', r'L40 0\.066, L56 #'])
add('E4b-ts-L40', 'E4b 全部论文 L40（训练折标准化，正文 §6.11 采用的新值）', md(TS, r'all papers', col='new', row={'layer': 'L40'}), '同上 + 标准化只在训练折内拟合（作业 11500917）', '1,863 篇', 3,
    [r'L24 \+0\.050、L40 #(?=、L56 \+0\.075)', r'L40 \+?#(?=, L56 \+0\.075)', r'L40 #(?=、L56 \+0\.07)'])
add('E4b-ts-L56', 'E4b 全部论文 L56（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': 'L56'}), '同上', '1,863 篇', 3,
    [r'L40 \+0\.061、L56 #', r'L40 \+0\.061, L56 #'])
add('E4b-ts-rmin', 'E4b 全部论文 L24–L60 最小（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='min'), '同上，L24–L60 取最小', '1,863 篇', 3,
    [r'L24–L60 为 #(?= 到 \+0\.0[78])', r'#(?= to \+0\.080\)?)'])
add('E4b-ts-rmax', 'E4b 全部论文 L24–L60 最大（训练折标准化）', md(TS, r'all papers', col='new', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='max'), '同上，L24–L60 取最大', '1,863 篇', 3,
    [r'(?:L24–L60 为 |全部论文标题特异信号 )\+0\.047 到 #', r'\+0\.047 to #'],
    note='orig（全样本标准化）同一范围是 0.0467–0.0802；文中 +0.080 与 trainstd 标签并列时即混用两版')
add('E4b-tc-min', 'E4b 引用档内目标−对照 L24–L60 最小（全样本标准化版）', md(SC, r'^## E4b: title-specific', col='group / title-reuse dropped', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='min'),
    '标题位置 probe，引用档内 target − control 合并；论文 bootstrap', '目标 896 / 对照 499 篇', 3, [r'(?:L24–L60 (?:为 )?|L24–L60 0\.0\d\d）?)#(?=[–\- ]+\+?0\.078| 到 \+0\.078|–\+0\.078)', r'#(?=–0\.078)'])
add('E4b-tc-ts-min', 'E4b 引用档内目标−对照 L24–L60 最小（训练折标准化）', md(TS, r'target - control within citation bin', col='new', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='min'),
    '同上，训练折标准化', '896 / 499', 3, [r'\+0\.035[–\-]', r'L24–L60 为 #(?= 到 \+0\.078，L44)']
    if False else [r'(?:为 |\+)#(?=(?:–\+| 到 \+| to \+)0\.078)'], note='与 E4b-tc-min 共用写法；按 0.035 / 0.036 判定哪一版')
add('E4b-tc-max', 'E4b 引用档内目标−对照 L24–L60 最大', md(TS, r'target - control within citation bin', col='new', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='max'),
    '同上', '896 / 499', 3, [r'0\.03[56] ?(?:[–\-]|到|to) ?\+?#'])
add('E4b-n-all', 'E4b 剔除标题复用后的篇数', {'t': 'py', 'fn': lambda: _e4b_counts(), 'desc': E4B_DESC + '：全部', 'files': E4B_FILES},
    '计数', '—', 0, [r'#(?= 篇)(?=.{0,40}(?:目标|target))', r'剩 ?#', r'全部 #(?= 篇)', r'(?:all |remaining )#(?= papers)'], sign=False)
add('E4b-n-t', 'E4b 目标组篇数', {'t': 'py', 'fn': lambda: _e4b_counts(['target']), 'desc': E4B_DESC + '：group_tight=target', 'files': E4B_FILES},
    '计数', '—', 0, [r'目标(?:组)? ?#(?=、|，|,| \+| vs)(?=.{0,30}(?:499|对照 ?499))', r'#(?= target vs 499)', r'#(?= \+ 499)'], sign=False)
add('E4b-n-c', 'E4b 对照组篇数', {'t': 'py', 'fn': lambda: _e4b_counts(['control']), 'desc': E4B_DESC + '：group_tight=control', 'files': E4B_FILES},
    '计数', '—', 0, [r'(?:目标(?:组)? ?896[、，, ]*(?:对照(?:组)?)? ?|896 \+ |896 target vs )#'], sign=False)
add('E4b-n-x', 'E4b excluded 篇数', {'t': 'py', 'fn': lambda: _e4b_counts(['excluded']), 'desc': E4B_DESC + '：group_tight=excluded', 'files': E4B_FILES},
    '计数', '—', 0, [r'excluded #'], sign=False)
add('E4b-n-g', 'E4b guard 篇数', {'t': 'py', 'fn': lambda: _e4b_counts(['guard']), 'desc': E4B_DESC + '：group_tight=guard', 'files': E4B_FILES},
    '计数', '—', 0, [r'guard #'], sign=False)
add('E4b-n-tc', 'E4b 目标 + 对照篇数', {'t': 'py', 'fn': lambda: _e4b_counts(['target', 'control']), 'desc': E4B_DESC + '：target+control', 'files': E4B_FILES},
    '计数', '—', 0, [r'#(?= 篇)(?=（896)', r'共 #', r'(?:目标 ?\+ ?对照|target ?\+ ?control) #', r'#(?= (?:篇|target ?\+ ?control|papers))(?=.{0,80}(?:团队|team))'], sign=False)
add('AT-sur-L40', '全部名字 token probe：L40 姓的第一个 token', md(AT, r'^### surname_first', col='title-specific, all papers [team CI]', row={'layer': 'L40'}),
    '补充 9：标题最后一个 token probe 打分姓的第一个 token，真标题 − false_0，剔除标题复用；团队聚类 95% CI', '目标 + 对照 1,395 篇', 3,
    [r'#(?= ?\[\+?0\.05\d, ?\+?0\.08\d\])', r'(?:姓的第一个 token|surname first token at L40|surname_first L40) #'])
add('AT-sur-L40-lo', '同上下限', md(AT, r'^### surname_first', col='title-specific, all papers [team CI]', part='lo', row={'layer': 'L40'}), '同上', '同上', 3, [r'0\.071 ?\[\+?#'])
add('AT-sur-L40-hi', '同上上限', md(AT, r'^### surname_first', col='title-specific, all papers [team CI]', part='hi', row={'layer': 'L40'}), '同上', '同上', 3, [r'0\.071 ?\[\+?0\.05\d, ?\+?#\]'])
add('AT-ini-L40', '全部名字 token probe：L40 首字母', md(AT, r'^### initial', col='title-specific, all papers [team CI]', row={'layer': 'L40'}), '同上，首字母 token', '1,590 篇', 3,
    [r'#(?= ?\[\+?0\.03\d, ?\+?0\.05\d\])'])
add('AT-giv-L40', '全部名字 token probe：L40 名的第一个 token', md(AT, r'^### given_first', col='title-specific, all papers [team CI]', row={'layer': 'L40'}), '同上，名的第一个 token', '1,706 篇', 3,
    [r'名的第一个 token #', r'given[- ]name first token (?:at L40 )?#'])

# ===================================================================== Stage 12 name prior
add('PR-prior', '名字先验的目标−对照（全部名字 token）', csv(PRI, 'prior', readout='final', layer=63, role='all_tokens', group='tc_prior'),
    'Stage 12 CPU 名字先验拆解：删标题条件下的引用档内目标−对照（最终输出 L63）', '9,108 篇（目标 4,621 / 对照 2,220）', 3, [r'先验 #(?= ?/)', r'prior #(?= ?/)'])
add('PR-true', '真标题条件下的目标−对照（全部名字 token）', csv(PRI, 'true', readout='final', layer=63, role='all_tokens', group='tc_true'), '同上，真标题', '同上', 3,
    [r'真标题差 #', r'true-title (?:difference |gap )?#', r'/ #(?=；371_stage12)'])
add('PR-share', '先验占目标−对照差的比例（约 1/3）', {'t': 'op', 'op': 'div', 'a': csv(PRI, 'prior', readout='final', layer=63, role='all_tokens', group='tc_prior'),
                                                 'b': csv(PRI, 'true', readout='final', layer=63, role='all_tokens', group='tc_true')},
    '先验 ÷ 真标题差', '—', 2, [], sign=False, note='文中写“约 1/3”（=0.33），源比值见右；不是十进制数字，未自动匹配')
add('PR-sur', '姓的第一个 token 上名字先验的目标−对照', csv(PRI, 'prior', readout='final', layer=63, role='surname_first', group='tc_prior'), '同上，姓的第一个 token', '同上', 3,
    [r'先验目标−对照 #', r'#(?= ?\[−0\.019, \+0\.063\])'])

# ===================================================================== Part 5 group comparisons (391_groups/primary.csv)
def gp(contrast, version, col='estimate'):
    return csv(GP, col, contrast=contrast, version=version)


GD = '引用档内差，真标题 − 5 个假标题平均，最终输出 L63，未写出作者；团队聚类 bootstrap 2,000 次'
add('G-P1', 'P1 A − B（认得出 − 认不出，R0）', gp('P1 A - B', 'within-bin'), GD, 'A 3,417 / B 2,148 篇（13,141 / 6,752 位作者）', 3,
    [r'#(?= ?\[0\.188, 0\.21\d\])', r'#(?= ?\[0\.18\d, 0\.213\])'])
add('G-P1-lo', '同上下限', gp('P1 A - B', 'within-bin', 'lo'), GD, '同上', 3, [r'\+0\.200 ?\[#'])
add('G-P1-hi', '同上上限', gp('P1 A - B', 'within-bin', 'hi'), GD, '同上', 3, [r'\+0\.200 ?\[0\.18\d, #\]'])
add('G-P1-conf', 'P1 论文层面回归 + 混杂', gp('P1 A - B', 'paper-level regression + confounders (add. 7)'), '论文层面回归：引用档 + 领域固定效应、年份、作者数、首字母开头比例；团队聚类', '5,565 篇', 3,
    [r'#(?= ?\[0\.16\d, 0\.18\d\])'])
add('G-P1-auth', 'P1 作者层面 + 混杂 + 首位/其他', gp('P1 A - B', 'author-level + confounders + first/other (add. 8)'), '作者层面回归 + 混杂 + 首位/其他；团队聚类', '19,893 位作者', 3,
    [r'#(?= ?\[0\.13\d, 0\.16\d\])'])
add('G-P3', 'P3 每多答对一种选项顺序的斜率', gp('P3 slope on mc_team_a (R0)', 'regression, bin FE only'), '论文层面回归，引用档固定效应；团队聚类', 'R0 论文 8,288 篇', 3,
    [r'#(?= ?\[0\.05\d, 0\.06\d\])'])
add('G-P3-auth', 'P3 作者层面 + 混杂', gp('P3 slope on mc_team_a (R0)', 'author-level + confounders + first/other (add. 8)'), '作者层面回归 + 混杂；团队聚类', '30,060 位作者', 3,
    [r'#(?= ?\[0\.042, 0\.049\])'])
add('G-P2o', 'P2-other C − A（未写出的合作者）', gp('P2-other C - A', 'within-bin'), GD + '（第 2 位及以后作者）', 'C 390 / A 2,826 篇', 3,
    [r'#(?= ?\[0\.03\d, 0\.09\d\])'])
add('G-P2f', 'P2-first C − A（未写出的第一作者）', gp('P2-first C - A', 'within-bin'), GD + '（第一作者）', 'C 292 / A 3,199 篇', 3,
    [r'#(?= ?\[−0\.00\d, 0\.06\d\])'])
add('G-P2f-holm', 'P2-first Holm p', gp('P2-first C - A', 'within-bin', 'p_holm'), 'Holm 校正 p（团队 bootstrap）', '同上', 3, [r'Holm p #'], sign=False)
EN = '391_groups/reports/e1_num_den.md'
add('G-E1den-B', 'E1 分母（真假差距）B', md(EN, r'^## E1$', col='denominator [CI]', row={'layer': 'L24', 'group': 'B', 'authors': 'unwritten'}), 'E1 分母 = mean(真 − 假)，最终输出；团队 bootstrap', 'B 586 篇', 3,
    [r'(?:真假差距 )?B #(?=、A)', r'B #(?= vs A)'], sign=False)
add('G-E1den-A', 'E1 分母（真假差距）A', md(EN, r'^## E1$', col='denominator [CI]', row={'layer': 'L24', 'group': 'A', 'authors': 'unwritten'}), '同上', 'A 557 篇', 3,
    [r'B 0\.214、A #', r'vs A #'], sign=False)
add('G-curve0', 'mc_team_a = 0 时的平均信号', csv('391_groups/stage10_curves.csv', 'estimate', who='unwritten', recall='R0', variable='mc_team_a', level='0', readout='final', layer=63),
    'R0 论文未写出作者，最终输出 L63 平均信号（简单平均）', '927 篇', 3, [r'全错时约 #', r'= 0：#'], sign=False)
add('G-curve4', 'mc_team_a = 4 时的平均信号', csv('391_groups/stage10_curves.csv', 'estimate', who='unwritten', recall='R0', variable='mc_team_a', level='4', readout='final', layer=63),
    '同上', '4,105 篇', 3, [r'全对时约 #', r'= 4：#'], sign=False)
add('G-R2s', 'R2s 写出的作者输出层信号（上限参照）', md('391_groups/summary_table.md', r'.', col=2, row={}, nth=0) if False else
    {'t': 'mdre', 'f': '391_groups/summary_table.md', 're': r'^\| R2s \|[^|]*\| ([+\-]\d\.\d+) \[', 'nth': 0},
    '简单平均，团队聚类 95% CI', '200 篇 / 412 位作者', 3, [r'为 #(?=（R2s)', r'#(?= ?\[\+?0\.807)'])

# ===================================================================== Stage 1-9
add('S73', 'Pilot50 L56 真标题比 20 个错误标题平均高', {'t': 'py', 'fn': lambda: _s73('mean'), 'desc': 'paper_null_distribution.csv 行 pool=combined, mode=jlens_L56（50 行）列 title_advantage 取均值',
                                                        'files': ['351_stage7_3/summary/paper_null_distribution.csv']},
    '逐篇 真标题胜率 − 20 个错误标题平均，50 篇均值', '50 篇', 1, [r'#(?= ?(?:pp|个百分点))(?=.{0,80}(?:Pilot|7\.3|50 篇))', r'Pilot(?:50)? #(?= ?pp)', r'L56 真标题比错误标题高 #'], scale=100)
add('S73-pos', '同上为正的篇数', {'t': 'py', 'fn': lambda: _s73('pos'), 'desc': '同上 title_advantage > 0 的行数', 'files': ['351_stage7_3/summary/paper_null_distribution.csv']},
    '计数', '50 篇', 0, [r'#(?=/50 篇为正| 篇为正)'], sign=False)
add('S8-RQ1', 'Stage 8D RQ1：200 篇新论文 L56 真标题 − 20 错误标题', csv(S8, 'mean', question='RQ1_L56_replication'), '逐篇差均值；论文 bootstrap 95% CI', '200 篇', 2,
    [r'#(?= ?pp ?\[\+?2\.9\d)', r'200 篇新论文(?:上)?(?:为)? ?#(?= ?pp)', r'(?:新 200 篇|new 200 papers) #'], scale=100)
add('S8-RQ1-lo', '同上下限', csv(S8, 'ci_low', question='RQ1_L56_replication'), '同上', '200 篇', 2, [r'5\.18 ?(?:pp )?\[\+?#'], scale=100)
add('S8-RQ1-hi', '同上上限', csv(S8, 'ci_high', question='RQ1_L56_replication'), '同上', '200 篇', 2, [r'5\.18 ?(?:pp )?\[\+?2\.9\d, ?\+?#\]'], scale=100)
add('S8-RQ2', 'Stage 8D RQ2：匹配 A − B', csv(S8, 'mean', question='RQ2_matched_A_minus_B'), '100 对配对差均值；配对 bootstrap', '100 对', 2,
    [r'#(?= ?pp ?\[\+?0\.3\d)', r'Stage 8 为 #'], scale=100)
add('S8-RQ2-lo', '同上下限', csv(S8, 'ci_low', question='RQ2_matched_A_minus_B'), '同上', '100 对', 2, [r'4\.98 ?(?:pp )?\[\+?#'], scale=100)
add('S8-RQ2-hi', '同上上限', csv(S8, 'ci_high', question='RQ2_matched_A_minus_B'), '同上', '100 对', 2, [r'4\.98 ?(?:pp )?\[\+?0\.3\d, ?\+?#\]'], scale=100)
add('S8-drop10', '去掉最大的 10 对后 A − B', {'t': 'py', 'fn': _s8_drop10, 'desc': 'matched_pair_differences.csv 行 mode=jlens_L56（100 对）按 A_minus_B 降序去掉前 10 对后取均值',
                                              'files': ['351_stage8/stage8D/summary/matched_pair_differences.csv']},
    '事后诊断', '90 对', 2, [r'降为 #(?= ?pp)', r'#(?= ?pp)(?=.{0,40}去掉)'], scale=100)
add('S74', 'Stage 7.4 J-Lens − Vanilla 7 层积分', csv('351_stage7_4/summary/jlens_increment_bootstrap.csv', 'mean', layer='integrated'), '标题优势之差，7 层积分；论文 bootstrap', '50 篇', 3,
    [r'Stage 7\.4 为 #', r'#(?= ?\[−0\.008, \+0\.012\])'])
add('S8-JV', 'Stage 8 L56 J-Lens − Vanilla', csv('351_stage8/stage8D/summary/jlens_minus_vanilla.csv', 'mean', mode='L56_JLens_minus_Vanilla'), '标题优势之差；论文 bootstrap', '200 篇', 2,
    [r'#(?= ?pp ?\[−3\.4\d)'], scale=100)
add('S71-cont', 'Stage 7.1 后续 token JMRR 匹配 A − B（7 层积分）', csv('351_stage7_1/summary/layer_and_integrated_effects.csv', 'A_minus_B_mean', mode='jlens', layer='integrated_7', metric='continuation_jmrr'),
    '20 对配对差均值；bootstrap', '20 对', 4, [r'#(?= ?\[\+0\.0022)', r'后续 token（#'])
add('S71-first', 'Stage 7.1 第一个 token 匹配 A − B', csv('351_stage7_1/summary/layer_and_integrated_effects.csv', 'A_minus_B_mean', mode='jlens', layer='integrated_7', metric='first_jmrr'),
    '同上', '20 对', 4, [r'#(?= ?\[−0\.0114)'])

# ===================================================================== cohort counts
for k, nm in [('A', 'A 认得出·R0'), ('B', 'B 认不出·R0'), ('C', 'C 认得出·R1'), ('D', 'D 认不出·R1')]:
    add('N-' + k, '分组篇数 ' + nm, {'t': 'json', 'f': AUD, 'path': ['group_counts', k]}, '标注包计数', '—', 0,
        [r'%s ?= ?#' % k, r'%s ?#(?=）|\)|，|、| 篇)' % ('认得出·R0（' if k == 'A' else '认不出·R0（' if k == 'B' else '认得出·R1（' if k == 'C' else '认不出·R1（')], sign=False)
add('N-T', 'target 篇数 = A + C', {'t': 'op', 'op': 'add', 'a': {'t': 'json', 'f': AUD, 'path': ['group_counts', 'A']}, 'b': {'t': 'json', 'f': AUD, 'path': ['group_counts', 'C']}},
    'A + C', '—', 0, [r'target ?= ?A ?\+ ?C ?(?:= ?|（)#', r'target（#'], sign=False)
add('N-Ctl', 'control 篇数 = B + D', {'t': 'op', 'op': 'add', 'a': {'t': 'json', 'f': AUD, 'path': ['group_counts', 'B']}, 'b': {'t': 'json', 'f': AUD, 'path': ['group_counts', 'D']}},
    'B + D', '—', 0, [r'control ?= ?B ?\+ ?D ?(?:= ?|（)#'], sign=False)
add('N-all', '标注包全部论文', {'t': 'json', 'f': AUD, 'path': ['total']}, '标注包计数', '—', 0, [r'(?<![\d,])(?P<v>9,?1\d\d)(?= 篇| papers)', r'全部 (?P<v>9,?1\d\d)'], sign=False)

# ===================================================================== Stage 13 M2 / M2c (hypothesis table and prereg results)
M2C = '381_stage13/summary_cpu/M2c_bert_baseline.csv'
for cid, tg, lab, pat in [('year', 'year', '年份 R²', r'年份 R² #(?=，引用数 0\.19)'), ('cit', 'log citations', '引用数 R²', r'引用数 #(?=（去掉年份后)'),
                     ('cit-yr', 'log citations | year removed', '去掉年份后的引用数 R²', r'去掉年份后 #(?=）)'), ('auc', 'recognised (target vs control)', '“是否认得出”AUROC', r'AUROC #(?=（Stage 13 M2c)')]:
    add('M2c-' + cid, 'BERT 最好一层 ' + lab, csv(M2C, 'value', 'max', model='bert-base-uncased', target=tg), 'bert-base-uncased 各层取最大；按论文 5 折', '9,108 篇', 2, [pat], sign=False)
CR = '381_stage13/reports/stage13_cpu_report.md'
LAY = ['L16', 'L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']
for tg, lab, pat in [('year (r2)', '年份 R²', r'分别是 #'), ('log citations (r2)', '引用数 R²', r'分别是 0\.56、#'),
                     ('recognised (target vs control) (auc_bin)', '“是否认得出”AUROC', r'0\.52、#')]:
    add('M2-' + tg.split()[0], 'Qwen 标题最后一个 token 各层最高 ' + lab,
        md(CR, r'true title run, title position', cols=LAY, row={'target': tg}, agg='max'), 'Stage 13 M2 probe，按论文 5 折，L16–L60 取最大', '9,108 篇', 2, [pat], sign=False)


# ===================================================================== tightened occurrence patterns (after review of the first runs)
# '#' = any number; '(?P<v>...)' written out = number of a fixed shape. Each list REPLACES the one given above.
BSP = r'B_spec_target_vs_control_within_bin(?:\.csv)?'
OCC = {
    'S10-L63': [r'#(?= ?\[\+?0\.19\d, ?\+?0\.220\])', r'#(?= (?:到|to) \+0\.23(?!\d))', r'(?:从 |from )#(?: 变为| to \+0\.199)',
                r'(?:输出处|在输出层|输出层|输出|output|final|L63) ?(?:约|为|是)? ?(?P<v>\+0\.2[01]\d?)(?![\d\[ ]*\[0\.188)(?=（|\(|，|,|；|;| |$)',
                r'versus (?P<v>\+0\.207)', r'输出 (?P<v>\+0\.207)'],
    'S10-L63-na': [(r'目标 ?#(?: 篇)? ?(?:\+|vs|、|/) ?对照', BSP, 140), (r'#(?: 篇)? ?(?:\+|vs) ?(?:对照 ?)?(?P<w>2,1\d\d|2,2\d\d)', BSP, 140),
                   (r'#(?: target)? ?\+ ?2,182', None, 0)],
    'S10-L63-nb': [(r'目标 ?[\d,]+(?: 篇)? ?(?:\+|vs|、|/) ?对照 ?#', BSP, 140), (r'3,734(?: target)? ?(?:\+|vs) ?(?:对照 ?)?#', None, 0)],
    'S10-L62-min': [r'(?<![\d.])#(?=[–\-]0\.23\d)'],
    'S10-L62-max': [r'0\.22\d[–\-]#', r'\+0\.21 (?:到|to) #'],
    'S10-L48-jmax': [r'L48 (?:略为负|is slightly negative) ?[（(]#(?= 到| to|–)', r'三种 Jacobian lens L48 为 #(?= 到)', r'three J-lenses at L48 #'],
    'S10-L48-jmin': [r'L48 (?:略为负|is slightly negative) ?[（(]−0\.0\d (?:到|to) #', r'三种 Jacobian lens L48 为 −0\.0\d\d 到 #'],
    'S10-R0': [r'#(?= ?\[\+?0\.18\d, ?\+?0\.212\])', r'(?:变为|to|→ ?)(?P<v>\+0\.199)', r'R0[^\d]{0,12}(?P<v>\+0\.20?\d?)(?=（|\()', r'gap is (?P<v>\+0\.199)'],
    'S10-R0-lo': [r'\+?0\.199 ?\[\+?#, ?\+?0\.21\d\]'],
    'S10-R0-hi': [r'\+?0\.199 ?\[\+?0\.18\d, ?\+?#\]'],
    'AT-sur-L40': [r'#(?= ?\[\+?0\.05\d, ?\+?0\.085\])', r'(?:姓的第一个 token|surname first token at L40|surname_first L40) #(?= ?\[\+?0\.058)'],
    'AT-ini-L40': [r'#(?= ?\[\+?0\.030, ?\+?0\.057\])', r'#(?= ?\[\+?0\.03\d, ?\+?0\.057\])'],
    'G-R2s': [r'为 #(?=（R2s)', r'#(?= ?\[\+?0\.807, ?\+?0\.887\])'],
    'E1-L52': [r'L52 #(?=；593|; paper|；论文 bootstrap|；593 ?\+ ?593|，目标|；§6\.11)', r'L52 起(?:恢复 ?)? ?#(?=%)', r'100% from L52|(?P<v>100)% from L52'],
    'E4b-n-all': [r'(?:剩|共|全部) ?(?P<v>1,8\d\d)(?= 篇)', r'(?P<v>1,8\d\d)(?= papers)'],
    'E4b-n-tc': [r'(?:共|目标 ?\+ ?对照|target ?\+ ?control) ?(?P<v>1,[23]\d\d)', r'(?P<v>1,[23]\d\d)(?= (?:篇|papers))(?=.{0,60}(?:目标 ?\+ ?对照|target ?\+ ?control|896))'],
    'E4b-tc-min': [(r'#(?=(?:[–\-]| 到 | to )\+?0\.078)', r'e4b_split_compare', 300)],
    'E4b-tc-ts-min': [(r'#(?=(?:[–\-]| 到 | to )\+?0\.078)', r'trainstd|训练折', 300)],
    'E4b-ts-rmin': [r'#(?= (?:到|to) \+0\.0(?:80|75)\b)'],
    'S8-RQ1-lo': [r'5\.18 ?(?:pp )?\[\+?#, ?\+?7\.48\]'],
    'S8-RQ1-hi': [r'5\.18 ?(?:pp )?\[\+?2\.93, ?\+?#\]'],
    'S8-RQ2-lo': [r'4\.98 ?(?:pp )?\[\+?#, ?\+?9\.91\]'],
    'S8-RQ2-hi': [r'4\.98 ?(?:pp )?\[\+?0\.32, ?\+?#\]'],
    'N-A': [r'A ?= ?(?P<v>4,1\d\d)', r'认得出·R0（(?P<v>4,1\d\d)'], 'N-B': [r'B ?= ?(?P<v>2,1\d\d)', r'认不出·R0（(?P<v>2,1\d\d)'],
    'N-C': [r'C ?= ?(?P<v>5\d\d)(?!\d)', r'认得出·R1（(?P<v>5\d\d)'], 'N-D': [r'D ?= ?(?P<v>3\d)(?![\d.])', r'认不出·R1（(?P<v>3\d)'],
    'N-T': [r'target ?= ?A ?\+ ?C ?(?:= ?|（)(?P<v>4,\d\d\d)', r'target（(?P<v>4,\d\d\d)'],
    'N-C': [r'C ?= ?(?P<v>5\d\d)(?!\d)', r'认得出·R1（(?P<v>5\d\d)'],
}
for c in C:
    if c['id'] in OCC:
        c['occ'] = OCC[c['id']]

# second round of tightening (review of run out_20261107_004453)
OCC2 = {
    'S10-L63': [r'#(?= ?\[\+?0\.19\d, ?\+?0\.220\])', r'(?P<v>\+0\.2[01]\d?)(?= (?:到|to) \+0\.23(?!\d))', r'(?:从 |from )(?P<v>\+0\.20\d)(?: 变为| to \+0\.199)',
                r'(?:输出处|在输出层|输出层|输出|output|final|L63) ?(?:约|为|是)? ?(?P<v>\+0\.2[01]\d?)(?![\d\[ ]*\[0\.188)(?! ?\[0\.199)(?=（|\(|，|,|；|;| |$)',
                r'versus (?P<v>\+0\.207)', r'输出 (?P<v>\+0\.207)'],
    'S10-L63-hi': [r'\+?0\.207 ?\[\+?0\.19[3-7], ?\+?#\]'],
    'S10-L63-na': [r'目标 #(?: 篇)? ?(?:\+|、) ?对照 [\d,]+ 篇[）)]?；351_stage10/summary_title/B_spec', r'#(?: 篇)? ?(?:\+|vs) ?(?:对照 ?)?2,182', r'共有引用档 目标 #'],
    'S10-L63-nb': [r'目标 [\d,]+(?: 篇)? ?(?:\+|、) ?对照 #(?= 篇[）)]?；351_stage10/summary_title/B_spec)', r'3,734(?: target)? ?(?:\+|vs) ?(?:对照 ?)?#'],
    'P1-colon': [r'":" L52 #', r'只换 “:” 最多 #', r'(?:最多|at most) #(?=（Stage 12 P1|\(Stage 12 P1)'],
    'S73': [r'(?P<v>\+?9\.3\d?)(?= ?(?:pp|个百分点))'],
    'X3-L62-max': [r'0\.43\d[–\-](?P<v>0\.44\d)'],
    'X3-L62-pub': [r'(?:L62 ?约|约|均值) ?(?P<v>0\.44\d?)(?=（|\(|）)', r'全部 9,108 篇均值 (?P<v>0\.44\d)'],
    'AT-ini-L40': [r'#(?= ?\[\+?0\.030, ?\+?0\.057\])'],
    'E4b-ts-L40': [r'L24 \+0\.050、L40 #(?=、L56 \+0\.075)', r'L40 \+?#(?=, L56 \+0\.075)'],
    'X2-rho': [r'ρ ?(?:=|＝) ?(?P<v>0\.4[45]\d?)', r'ρ (?P<v>0\.45\d)(?= ?\[)'],
}
EXCL = {'S10-L62-max': r'去掉 ?0-4|bins 0-4|去掉低档|drop', 'E4b-ts-rmin': r'L16–L60', 'S10-L63': r'去掉 ?0-4|E3|连写|chain'}
for c in C:
    if c['id'] in OCC2:
        c['occ'] = OCC2[c['id']]
    c['excl'] = EXCL.get(c['id'])
add('X3-L62-4max', '四种读出 L62 标题特异信号（最大，含 logit）', csv(X3M, 'mean', 'max', layer=62, metric='spec', readout=['jlens_public', 'jlens_self100', 'jlens_fitA', 'logit']),
    '真标题 − 5 个假标题平均，逐篇均值；四种读出取最大', '9,108 篇', 3, [r'0\.436[–\-](?P<v>0\.46\d)'], sign=False)
C[-1]['excl'] = None

# third round: alternative source files (a written number that equals an OTHER result file of the same quantity is
# flagged 写法不统一 with that file named, not 不一致) and the last pattern fixes.
ALT = {
    'S10-L63-lo': [('351_stage10/reports/stage10_title_summary.md 第 25 行（2026-10-26 03:13 生成，早于现 CSV 06:39 重写；旧一次 bootstrap）',
                    {'t': 'mdre', 'f': '351_stage10/reports/stage10_title_summary.md', 're': r'^\| final \|[^\n]*\+0\.207 \[\+(0\.\d+),'}),
                   ('351_stage10/summary_r0r1/tc_pooled.csv（另一次 bootstrap）', csv('351_stage10/summary_r0r1/tc_pooled.csv', 'spec_mean_nlr_lo', **F63))],
    'S10-R0-lo': [('351_stage10/summary_r0r1/tc_R0.csv（作业 11429580 的另一次 bootstrap；r0_r1_analysis.md 用它）', csv('351_stage10/summary_r0r1/tc_R0.csv', 'spec_mean_nlr_lo', **F63))],
    'S10-R0-hi': [('351_stage10/summary_r0r1/tc_R0.csv（另一次 bootstrap）', csv('351_stage10/summary_r0r1/tc_R0.csv', 'spec_mean_nlr_hi', **F63))],
    'S10-CA-hi': [('351_stage10/summary_r0r1/C_minus_A.csv（另一次 bootstrap）', csv('351_stage10/summary_r0r1/C_minus_A.csv', 'spec_mean_nlr_hi', **F63))],
    'S10-CA-lo': [('351_stage10/summary_r0r1/C_minus_A.csv（另一次 bootstrap）', csv('351_stage10/summary_r0r1/C_minus_A.csv', 'spec_mean_nlr_lo', **F63))],
    'E4b-ts-rmax': [('e4b_trainstd_compare.md 同表 orig 列（全样本标准化，旧版）L24–L60 最大',
                     md(TS, r'all papers', col='orig', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='max'))],
    'E4b-tc-ts-min': [('e4b_split_compare.md（全样本标准化，旧版）', md(SC, r'^## E4b: title-specific', col='group / title-reuse dropped', row={'layer': ['L24', 'L32', 'L40', 'L44', 'L48', 'L52', 'L56', 'L60']}, agg='min'))],
}
OCC3 = {
    'G-P1': [r'#(?= ?\[0\.188, 0\.213\])'],
    'A-bin-high': [r'\+0\.3\d (?:到|to) #', r'4097\+ 档 (?P<v>\+?0\.6\d\d)', r'(?P<v>\+?0\.6\d\d)(?= in 4097\+)'],
    'E4b-tc-min': [(r'#(?=(?:[–\-]| 到 | to )\+?0\.078)', r'e4b_split_compare', 160)],
    'E4b-tc-ts-min': [(r'#(?=(?:[–\-]| 到 | to )\+?0\.078)', r'trainstd|训练折', 160)],
}
for c in C:
    c['alt'] = ALT.get(c['id'], [])
    if c['id'] in OCC3:
        c['occ'] = OCC3[c['id']]
    if c['id'] == 'E4b-tc-ts-min':
        c['excl'] = r'e4b_split_compare'

# fourth round: stale-file matches stay 不一致 (third tuple element), notes, PR-share pattern
ALT['S10-L63-lo'][0] = ALT['S10-L63-lo'][0] + ('不一致',)
ALT['E4b-ts-rmax'][0] = ALT['E4b-ts-rmax'][0] + ('不一致',)
NOTES = {
    'E4b-all-L40': '同一量的训练折标准化新值是 E4b-ts-L40（0.061）；报告 §6.11 写明“已改用新值”，而 §1 摘要仍用此旧值 0.066（e4b_split_compare.md）',
    'E4b-all-L56': '新值见 E4b-ts-L56（0.075）；§1 摘要仍用旧值 0.080',
    'S10-L63-lo': '0.196 来自 351_stage10/reports/stage10_title_summary.md（2026-10-26 03:13 生成），之后 06:39 CSV 被重写，现 CSV 下限 0.19535 → 0.195',
    'S10-R0-lo': '0.187 来自 summary_r0r1/tc_R0.csv（作业 11429580 另一次 bootstrap，r0_r1_analysis.md 第 21 行）；0.188 来自 summary_r0/…_R0.csv（r0_sensitivity.md）',
    'E4b-ts-rmax': '+0.080 是全样本标准化旧版（orig 列）L56 的值；训练折标准化新版 L24–L60 最大为 0.075',
    'M2c-year': '报告同段仍写“按团队分折的版本还在跑”，但 summary_cpu_group/M2c_bert_baseline.csv 已存在（年份 0.240、引用数 0.188、AUROC 0.632，四舍五入后与按论文分折相同）',
}
for c in C:
    if c['id'] in NOTES:
        c['note'] = NOTES[c['id']]
    if c['id'] == 'PR-share':
        c['occ'] = [r'真标题差 \+0\.247 = #', r'= (?P<v>0\.35)(?=；报告 §6\.12)']

# reviewed judgement for the automatically screened "conclusion sentences without number or source" (report only).
# key = start of the sentence; value = (判定, 可支撑它的已登记数据)
NODATA_REVIEW = {
    '真标题有帮助，而且是针对这篇论文的': ('标题句，同段后文有数据', 'S73、S8-RQ1、X3-L62-pub'),
    '“认得出”组的优势是真的': ('标题句，同段后文有数据', 'S10-L48-*、S10-L63、S10-R0'),
    '小样本的 A−B 不确定': ('此处无数字也无出处；数据只在第一部分', 'S8-RQ2 +4.98 [0.32, 9.91]、S8-drop10 −0.39 pp'),
    'Jacobian lens 没有显示额外的论文信息': ('整条要点无数字、无出处', 'S74 +0.002 [−0.008, 0.012]、S8-JV −1.38 pp、X3-JmL +0.01 到 +0.03'),
    '小样本中 J-Lens 相对 Vanilla 没有增量': ('整条要点无数字、无出处（“名字形状”“不偏向目标组”在本句没有数据）', 'S74、S8-JV；目标组：351_stage10/summary_extra/X3_tc_spec_vs_logit.csv（未登记）'),
    '：首字母开头时，姓落在后续 token 上': ('整条要点无数字、无出处', 'X1-init-later +0.253、X1-init-first +0.048、X1-given-first +0.174、X1-given-later +0.202'),
    '下一步需要全部作者': ('不是结论（计划）', ''),
    '我们比较了两组论文': ('不是结论（设计说明）', ''),
    '主要结论：针对具体论文的作者信息只在最后几层': ('标题句，同段后文有数据', 'S10-L63、S10-L62-*'),
    '），而且几乎全部是标题特异的': ('“几乎全部”没有给出比例或数字', 'PR-true +0.247 与 S10-L63 +0.207（或 PR-prior +0.087）'),
    '），而且这部分信息不偏向目标组': ('只有出处文件名，没有数字', 'X3_tc_spec_vs_logit.csv（未登记，需补）'),
    '（按作者团队分折、剔除标题复用后复核）': ('不是独立结论（括注）', ''),
    'Jacobian lens 能让中间层读出更多与名字相关的信息': ('有出处、无数字', 'X3-JmL +0.01 到 +0.03（X3_pairwise.csv）'),
    '标题特异信号在名字里的分布取决于格式': ('§7 这一句无数字；同条后文只给 X1_cond 的数字', 'X1-init-later、X1-init-first、X1-given-*'),
    '没有哪种 lens 能在中间层读出偏向目标组的论文信息': ('无数字、无出处', 'X3_tc_spec_vs_logit.csv（未登记，需补）；S10-J-L56 +0.003 到 +0.009'),
    'R1 论文让优势更大，但不改变时间点': ('“不改变时间点”本句无数字；表中只有输出处大小', 'S10-CB +0.372；层级曲线见 summary_r0r1/tc_R1target_vs_R0control.csv（未登记）'),
    '；识别不确定的论文落在两组之间': ('无数字', '391_groups/summary_table.md U0 行 +0.287（未登记）'),
    '，主要是因为模型已经写出的作者分数本来就高': ('解释句无数字', '391_groups/summary_table.md C 行 written +0.771 vs unwritten +0.550（未登记）'),
    '蓝 = R0 论文': ('不是结论（图例）', ''),
}
