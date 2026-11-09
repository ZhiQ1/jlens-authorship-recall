"""Round f (2026-11-09, LOCAL only): M2 with five false titles (user rule 2026-11-09: false_1..4 clean, exclusion audit 0 rows; 381_stage13/summary_m2_f5/exclusion_audit.csv,
job 11747064). Five-title mean shown as main value with false_0 beside ("5 个假标题平均 X（false_0 版 Y）"); H2 verdict and tiers unchanged; true-title numbers unchanged.
M2 removed from the "false_0 only, no plan" limitation (L05) and replaced by the premise sentence. Numbers asserted against summary_m2_f5/M2_f5_mean.csv and exclusion_audit.csv.
Backups *.before_20261109f; K regenerated, handbook + process page rebuilt; manifest section "round f"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'
ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'; P = R / 'methods/parts'
TDs = [R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']]
B2, F13, G, K = P / 'B_global2.html', P / 'F_stage13.html', P / 'G_appendix.html', P / 'K_post_defence.html'; CONC = W / 'conclusions_v30_draft.md'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, ADV, PROCMD, AUD, ADD, READ, *TDs, B2, F13, G, K, CONC]
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + '.before_20261109f').exists(), p
m = pd.read_csv(J / '381_stage13/summary_m2_f5/M2_f5_mean.csv')
def v(tgt, L, col='false_mean5'):
    return round(float(m[(m.position == 'title') & (m.layer == L) & (m.target == tgt)][col].iloc[0]), 3)
CHK = {('year', 48): (0.527, 0.535), ('log citations', 48): (0.507, 0.488), ('log citations | year removed', 48): (0.491, 0.471), ('field', 48): (0.712, 0.716),
       ('year', 16): (0.341, 0.353), ('year', 52): (0.529, 0.538)}
for (t, L), (a, b) in CHK.items(): assert (v(t, L), v(t, L, 'false_0')) == (a, b), (t, L, v(t, L), v(t, L, 'false_0'))
assert (v('log citations | year removed', 48, 'min5'), v('log citations | year removed', 48, 'max5')) == (0.471, 0.506)
ea = pd.read_csv(J / '381_stage13/summary_m2_f5/exclusion_audit.csv')
assert (ea[['a_title_reuse', 'b_donor_label_in_train', 'b2_donor_team_in_train', 'd_true_title_in_train']].to_numpy() == 0).all()
c = ea[ea.group == 'all'].c_donor_as_target_in_train; assert c.min() >= 7200 and c.max() <= 7400, c.tolist()
rep5 = (J / '381_stage13/reports/m2_f5_report.md').read_text(); assert '| 7 |' in rep5 and '| 0.051 | 0.049 |' in rep5 and '36/36 rows above null for all titles' in rep5
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; LOG = []
def R_(old, new, files, n):
    tot = 0
    for p in files:
        k = S[p].count(old)
        if k: S[p] = S[p].replace(old, new); tot += k; LOG.append((str(p).replace(str(R) + '/', ''), old, new, k))
    assert tot == n, (old[:70], tot, n)
PREM = ('M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中'
        '（显示另一篇论文的标题和标签，只有年份在 \':\' 之后进入提示），未作为泄漏处理。')
NUM = ('5 个假标题平均 L48 读借出论文的年份 R² 0.527（false_0 版 0.535），引用数 0.507（false_0 版 0.488），去掉年份后的引用数 0.491（5 个假标题 0.471–0.506；false_0 版 0.471），'
       '领域准确率 0.712（false_0 版 0.716）；年份 L16 0.341（false_0 版 0.353），L52 0.529（false_0 版 0.538）；标题位置各行真 − 假的最大差 0.049（false_0 版 0.051）；'
       '36 个标题位置的行对 5 个假标题都高于随机')
SRC = '381_stage13/reports/m2_f5_report.md；381_stage13/summary_m2_f5/M2_f5_mean.csv、exclusion_audit.csv（作业 11747064）'
# report M2 split-audit item and experiment description
R_('但仍然读得出，与真标题运行相当：表示仍然跟着提示里的标题走。</li>', '但仍然读得出，与真标题运行相当：表示仍然跟着提示里的标题走。<b>2026-11-09 补（M2 用 5 个假标题，团队分折）：</b>' + NUM
   + f'<span class="src">（{SRC}）</span>。前提：' + PREM + '</li>', [REP], 1)
R_('假标题 false_0 的运行用标题所属论文的标签，检验 probe 读的是标题对应的论文。', '假标题 false_0 的运行用标题所属论文的标签，检验 probe 读的是标题对应的论文（2026-11-09 补做 false_1..4，见第四部分切分审计）。', [REP], 1)
# L05 limitation: remove M2 from "false_0 only, no plan"
L05_OLD = 'M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定'
L05_NEW = 'M2 已不在此列：' + PREM.rstrip('。')
tags = {'rep': ('<span class="src">（conclusions_v30_checks.md A3）</span>', f'<span class="src">（{SRC}）</span>'),
        'box': ('<span style="color:#8a8f98;font-size:.8em">（conclusions_v30_checks.md A3）</span>', f'<span style="color:#8a8f98;font-size:.8em">（{SRC}）</span>'),
        'md': ('【conclusions_v30_checks.md A3】', f'【{SRC}】')}
n = 0
for p in [REP, ADV, PROCMD, AUD, ADD, *TDs]:
    for st, (a, b) in tags.items():
        k = S[p].count(L05_OLD + a)
        if k: S[p] = S[p].replace(L05_OLD + a, L05_NEW + b); n += k; LOG.append((str(p).replace(str(R) + '/', ''), L05_OLD + a, L05_NEW + b, k))
assert n == 10, n
R_('(M2 with five titles needs CPU only, decision pending)', '(M2 has since been redone with five false titles: five-title mean primary, false_0 beside; the title-reuse / donor-in-training-fold exclusion is 0 rows for every title; '
   'about 7,240–7,370 rows per title have the donor paper as a target row in a training fold, showing another paper’s title and labels with only the year after the colon, not treated as leakage)', [READ], 2)
# handbook parts
HBTXT = '5 个假标题（2026-11-09，团队分折）：' + NUM + f'<span class="src">{SRC}</span>。前提：' + PREM
R_('R13/reports/split_compare.md 第 119-152 行</span></p>', 'R13/reports/split_compare.md 第 119-152 行</span></p>\n<div class="fix"><b>2026-11-09 补：</b>' + HBTXT + '</div>', [F13], 1)
R_('paper-split 的 false_0 数字被 addendum 1 判为无效。', 'paper-split 的 false_0 数字被 addendum 1 判为无效。2026-11-09：5 个假标题平均 L48 year 0.527（false_0 版 0.535）、log citations 0.507（false_0 版 0.488）、citations|year 0.491（false_0 版 0.471）、'
   'field acc 0.712（false_0 版 0.716）；false_1..4 的标题复用 / 供体在训练折排除均为 0 行（381_stage13/summary_m2_f5/exclusion_audit.csv）。', [B2], 1)
R_('区间平均宽 1.15 倍（true 1.02、false_0 1.32），0 个翻转。', '区间平均宽 1.15 倍（true 1.02、false_0 1.32），0 个翻转。2026-11-09 补做 5 个假标题：5 个假标题平均 L48 donor 年份 R² 0.527（false_0 版 0.535）、log 引用 0.507（false_0 版 0.488）；'
   'false_1..4 的标题复用 / 供体在训练折排除均为 0 行（381_stage13/reports/m2_f5_report.md；summary_m2_f5/exclusion_audit.csv）。', [G], 1)
# conclusions draft C13 + L05 + section 6
R_('  - false_0 运行读借出论文的年份：L48 R² 改为团队分折后从 0.623 降到 0.535，仍读得出。',
   '  - 假标题运行读借出论文的年份（团队分折）：5 个假标题平均 L48 R² 0.527（false_0 版 0.535；按论文分折的 0.623 作废），仍读得出；其余见 `R13/reports/m2_f5_report.md`（引用数 0.507（false_0 版 0.488），去掉年份后 0.491（0.471），领域 0.712（0.716），L16 年份 0.341（0.353），L52 0.529（0.538），真 − 假最大差 0.049（0.051），36 行对 5 个假标题都高于随机）。', [CONC], 1)
R_('只用 false_0（假标题运行；用 5 个假标题重做只需 CPU，约 3 小时，见 CHK A3）', PREM.rstrip('。') + '（`R13/summary_m2_f5/exclusion_audit.csv`，作业 11747064；用户 2026-11-09 判定干净）', [CONC], 1)
R_('  - M2 的假标题运行也只用 false_0。按 CHK A3，5 个假标题的残差已在 `R13/raw/b1_titlepos5/false_1..4`，只需 CPU（M2 约 3 小时 × 16 核，M5 B 部分 < 1 小时），但尚未排入计划。',
   '  - M2 已不在此列：2026-11-09 已补 5 个假标题（见 C13 前提）。M5 B 部分补做只需 CPU（< 1 小时，CHK A3），尚未排入计划。', [CONC], 1)
R_('M2 的 5 个假标题重做只需 CPU。', 'M2 已补 5 个假标题（2026-11-09，5 个假标题平均为主值、false_0 并列；排除审计 0 行）。', [CONC], 1)
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
S[K] = S[K][:S[K].index(lead) + len(lead)] + makeK(S[REP]) + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + '.before_20261109f'))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round f', '', 'Script `sync_20261107/apply_20261109f.py` (backups `*.before_20261109f`; numbers asserted against 381_stage13/summary_m2_f5/M2_f5_mean.csv and exclusion_audit.csv). H2 verdict and tiers unchanged; deck / notes / pptx contain no M2 false-title numbers or M2 in the false_0-only list → unchanged.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| f{i} | {cut(f, 70)} | {cut(o)} | {cut(nw)} | {c} |' for i, (f, o, nw, c) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round f:', len(LOG))
