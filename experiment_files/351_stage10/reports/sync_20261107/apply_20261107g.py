"""2026-11-07 ~21:00 round (user approved; NO publishing). Sources: ~/jlens_work/for_user_2026-11-07.md (a, b, c, e) and
numcheck/claims/out_20261107_183155/ (v6_all_non_ok.csv, v5_definition_issues.csv).
 1 3-3 stopped (D14-1 draft statement / decision chain / limitation)        2 D13-1 (Stage 8)        3 X4 recognition (test value)
 4 E4b scheme 2 (1,395 papers, X1-pipeline labels, standardisation 0.0007, Vpd wording)             5 report §4 range
 6 rounding        7 definition issues        8 P1/P2 187/194
HELD (coordinator, 2026-11-07): wording B sentence ('按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起…' and its en/deck forms) is NOT changed.
Numbers are re-read from the source files below (asserted). Backups *.before_20261107d.*. Writes sync_20261107/apply_log_20261107g.json."""
import json, re, shutil
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
PARTS = {p.name: p for p in (R / 'methods/parts').glob('*.html') if '.before_' not in p.name and p.name not in ('K_post_defence.html', 'F_stage13.orig.html')}
TD = {p.stem: p for p in (R / 'talk_docs').glob('*.html') if '.before_' not in p.name}
ADV = R / 'advisor/index.html'; PROC = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'
ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'
FILES = [REP, DECK, *PARTS.values(), *TD.values(), ADV, PROC, AUD, ADD, READ]
def bkp(p):
    b = p.with_name(p.stem + '.before_20261107d' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b
S = {p: bkp(p).read_text(encoding='utf-8') for p in FILES}
NJ = json.loads(bkp(NOTES).read_text(encoding='utf-8'))
LOG = []
def where(p): return 'notes_zh.json' if p == 'NOTES' else str(p).replace(str(R) + '/', '')
def R_(old, new, files=None, n_min=1, why='', regex=False):
    tot = 0
    targets = files if files is not None else FILES + ['NOTES']
    for p in targets:
        if p == 'NOTES':
            for k, v in NJ.items():
                t = v['text']; c = len(re.findall(old, t)) if regex else t.count(old)
                if c:
                    v['text'] = re.sub(old, new, t) if regex else t.replace(old, new); tot += c
                    LOG.append((why, 'notes_zh.json #' + k, old if not regex else '(regex) ' + old, new if not callable(new) else '(fn)', c))
        else:
            t = S[p]; c = len(re.findall(old, t)) if regex else t.count(old)
            if c:
                S[p] = re.sub(old, new, t) if regex else t.replace(old, new); tot += c
                LOG.append((why, where(p), old if not regex else '(regex) ' + old, new if not callable(new) else '(fn)', c))
    assert tot >= n_min, ('rule did not apply', why, old[:80])
    return tot
SZ = lambda t: f'<span class="src">（{t}）</span>'; SE = lambda t: f'<span class="src">({t})</span>'

# ---------------- source numbers
d14 = json.load(open(J / '381_stage13/b3_33_v2/prereg_addendum14_deviations_DRAFT.json'))
STMT, CHAIN, LIM = d14['statement_zh'], d14['decision_chain_zh'], d14['limitation_zh']
px = pd.read_csv(J / '381_stage13/c13_C2_followup/c2_followup_proxy.csv'); px = px[px.version == 'aa_all'].set_index('endpoint')
f3 = lambda v: f'{v:+.3f}'.replace('-', '−')
ci = lambda a, b: f'[{f3(a)}, {f3(b)}]'
r2 = lambda e: f'{f3(px.loc[e, "rq2"])} {ci(px.loc[e, "rq2_lo"], px.loc[e, "rq2_hi"])}'
r1 = lambda e: f'{f3(px.loc[e, "rq1"])} {ci(px.loc[e, "rq1_team_lo"], px.loc[e, "rq1_team_hi"])}'
assert r2('L56') == '+0.064 [−0.032, +0.163]' and r2('int7_L16zero') == '+0.046 [+0.007, +0.088]' and r2('int6') == '+0.054 [+0.008, +0.102]'
assert r1('int7_L16zero') == '+0.111 [+0.093, +0.131]' and r1('int7_L16eqL24') == '+0.117 [+0.095, +0.138]'
R2EQ = r2('int7_L16eqL24')   # source: +0.049 [+0.005, +0.094] (for_user_2026-11-07.md writes +0.006; the CSV lower bound is 0.00550 -> +0.005)
v42 = (J / '381_stage13/reports/v42_paper_vs_team.md').read_text()
rows = {m.group(1): m.group(2) for m in re.finditer(r'^\| author, title \| (L\d+) \| [^|]*\| [^|]*\| ([^|]*)\|', v42, re.M)}
assert rows['L8'].strip() == '+0.023 [-0.001, +0.048]'
tst = [float(rows[L].split()[0]) for L in ['L16', 'L24', 'L32', 'L40', 'L48']]
assert (round(min(tst), 3), round(max(tst), 3)) == (0.025, 0.060)

# ---------------- 8 P1/P2
R_('194 个计算单元已完成 116 个，其余 78 个分三条并行的作业链计算；结果经用户确认后补入', '194 个计算单元已完成 187 个，结果尚未出来；结果经用户确认后补入', why='8 P1/P2')
R_('194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算', '194 个计算单元已完成 187 个，结果尚未出来', why='8 P1/P2')
R_('194 个单元已完成 116 个，其余 78 个分三条并行作业链计算', '194 个单元已完成 187 个，结果尚未出来', why='8 P1/P2')
R_('（194 个单元已完成 116 个）', '（194 个单元已完成 187 个，结果尚未出来）', why='8 P1/P2')
R_('116 / 194 units done, 78 left in three parallel chains', '187 / 194 units done, result pending', why='8 P1/P2')
R_('(116 / 194 units done)', '(187 / 194 units done, result pending)', why='8 P1/P2')
R_('running (116 / 194 units)', 'running (187 / 194 units, result pending)', why='8 P1/P2')

# ---------------- 1 3-3 stopped
S33 = f'3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：{STMT.rstrip("。")}。决定过程：{CHAIN.rstrip("。")}'
EV33 = '381_stage13/b3_33_v2/prereg_addendum14_deviations_DRAFT.json；381_stage13/summary_b3_71b/gate.json；381_stage13/b3_33_v2/v2_C1_summary.json'
R_('3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写；', '3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；' + S33 + '；', why='1 3-3 stopped')
R_('批次 3（补充 14）：3-1、3-2、3-3 代码在写；', f'批次 3（补充 14）：3-1、3-2 代码已就绪，第二批之后开始；3-3（7.1B 快路径补完）已停止（偏离 D14-1）：{STMT}决定过程：{CHAIN}〔{EV33}〕；', why='1 3-3 stopped (notes 81)')
R_('批次 3（补充 14）代码在写。', '批次 3（补充 14）：3-1、3-2 代码已就绪，第二批之后开始；3-3（7.1B 快路径补完）已停止（偏离 D14-1）：无法确认与旧逐前缀结果等效（论文级 Welch 95% CI [−0.0207, +0.0324] 超出 ±0.02）。', why='1 3-3 stopped')
R_('批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码在写', '批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码已就绪，第二批之后开始', why='1 batch 3 status')
EN33 = '3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: code ready, after batch 2 · 3-3 Stage 7.1B fast path: stopped (deviation D14-1; equivalence with the old per-prefix results not confirmed)'
R_('3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23 · 3-3 Stage 7.1B fast path: code in progress', EN33, why='1 3-3 stopped (deck slide 81)')
R_('Batch 3 (addendum 14: Stage 10 L41–L47, L49; L0–L23; Stage 7.1B fast path): code in progress.',
   'Batch 3 (addendum 14): Stage 10 L41–L47, L49 and L0–L23 code ready, after batch 2; Stage 7.1B fast path stopped (deviation D14-1: equivalence with the old per-prefix results could not be confirmed, paper-level Welch 95% CI [−0.021, +0.032] exceeds ±0.02).', why='1 3-3 stopped (README)')
R_('| Batch 3 (addendum 14) | 3-1 Stage 10 L41–L47, L49; 3-2 L0–L23; 3-3 Stage 7.1B fast path | — | code in progress |',
   '| Batch 3 (addendum 14) | 3-1 Stage 10 L41–L47, L49; 3-2 L0–L23; 3-3 Stage 7.1B fast path | 3-3: equivalence with the old per-prefix results not confirmed | 3-1, 3-2 code ready (after batch 2); 3-3 stopped (deviation D14-1) |', why='1 3-3 stopped (README table)')
LIMLI = '<li><b>Stage 7.1B 未完成。</b>' + LIM + SZ('补充 14 出入记录 D14-1；' + EV33) + '</li>\n<li><b>Stage 8 L56 的 RQ2 没有用原统计量复核。</b>CPU 代理只在后改的 L56 上区间含 0，按补充 13 触发了 W 的 GPU 重算；用户决定不做（偏离 D13-1，见 Stage 8 节）。</li>\n'
R_('<li><b>标注流程。</b>标注包作者的 elm 代码', LIMLI + '<li><b>标注流程。</b>标注包作者的 elm 代码', files=[REP], why='1+2 limitations (report #pd-limits)')
R_('<li>只用了一个模型（Qwen3-32B，bf16）。</li>', '<li>只用了一个模型（Qwen3-32B，bf16）。</li>\n    <li>' + LIM + '（偏离 D14-1）</li>\n    <li>Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1）。</li>', files=[ADV], why='1+2 limitations (advisor)')
NJ_lim = '82'
assert NJ[NJ_lim]['text'].startswith('不能补做的局限'), NJ[NJ_lim]['text'][:20]
NJ[NJ_lim]['text'] += f' 2026-11-07 补：{LIM}（偏离 D14-1〔{EV33}〕）Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1〔381_stage13/reports/c13_C2.md；381_stage13/c13_C2_followup/c2_followup_proxy.csv〕）。'
LOG.append(('1+2 limitations (deck note 82)', 'notes_zh.json #82', '(append)', LIM[:60], 1))

# ---------------- 2 D13-1
SRC13 = '381_stage13/reports/c13_C2.md；381_stage13/c13_C2_followup/c2_followup_proxy.csv（aa_all 行；RQ1 团队 bootstrap 2,000 次，RQ2 配对 bootstrap 10,000 次，200 篇 / 100 对，种子同 C-2）'
D13 = ('<div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>'
       f'按补充 13 C-2 的判定规则（prereg_addendum13.json 第 18 行），全部作者 CPU 代理（public J-lens 名次、Stage 10 的 5 个假标题，不是原 W）只在 L56 的 RQ2 上与已发表结论不一致：{r2("L56")}，区间含 0' + SZ(SRC13 + '，endpoint=L56') +
       '。因此触发按原 W 在 GPU 上重算；用户 2026-11-06 决定不做，列为偏离。L56 是 10-18 21:14 由 PROTOCOL.md 改定的终点，改动者和依据仍未查清（U28）。'
       f'在 10-18 14:29 锁定计划的 7 层积分终点上（Stage 10 没有 L16，按 L16 = 0 或 L16 = L24 近似），代理 RQ2 为 {r2("int7_L16zero")} 或 {R2EQ}，RQ1 为 {r1("int7_L16zero")} 或 {r1("int7_L16eqL24")}，都与已发表结论同向、区间不含 0'
       + SZ('同上，endpoint=int7_L16zero / int7_L16eqL24') + f'。6 层 int6 的 RQ2 为 {r2("int6")}' + SZ('同上，endpoint=int6；int6 = public J-lens 在 L24、L32、L40、L48、L56、L62 的等权平均，少了 L16，与锁定的 7 层积分不是同一终点（13_stage13/stage13_c13_s10lib.py 第 17、70 行；351_stage8/config/analysis_plan.json 第 14、27、29 行）')
       + '。因此，不一致只出现在后改的 L56 上；在原定的主终点上，代理结果不要求重算。Stage 8 RQ2 在 L56 的结论没有用原统计量复核。'
       '已发表的原 W（按原种子复现）：7 层积分 RQ1 +2.326 [+1.496, +3.192] pp、RQ2 +2.409 [+0.909, +4.003] pp；L56 RQ1 +5.178 [+2.926, +7.476] pp、RQ2 +4.981 [+0.322, +9.915] pp'
       + SZ('351_stage8/recompute_2026-10-30/s8_endpoints.csv 第 2–7 行') + '</div>\n')
R_('GPU 上按原 W 重算没有做（用户 2026-11-06 决定）。</div>\n', 'GPU 上按原 W 重算没有做（用户 2026-11-06 决定，偏离 D13-1，见下框）。</div>\n' + D13, files=[REP], why='2 D13-1 box (report Stage 8)')
R_('<li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做；CPU 代理见 Stage 8 节）。</li>',
   f'<li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做，列为偏离 D13-1：CPU 代理只在后改的 L56 上 RQ2 区间含 0，在原定的 7 层积分终点上同向且区间不含 0，RQ2 {r2("int7_L16zero")}；见 Stage 8 节）。</li>', files=[REP], why='2 D13-1 (report Part 5)')
HS = lambda t: f'<span class="src">{t}</span>'
R_('<tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）</td><td><span class="st st-plan">不做</span></td><td>用户 2026-11-06 决定不做；',
   f'<tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）= 偏离 D13-1</td><td><span class="st st-plan">不做</span>（偏离 D13-1）</td><td>用户 2026-11-06 决定不做。D13-1：CPU 代理只在 L56 的 RQ2 上与已发表结论不一致（{r2("L56")}，区间含 0）；在 10-18 14:29 锁定的 7 层积分终点上（L16 = 0 或 = L24 近似）RQ2 {r2("int7_L16zero")} / {R2EQ}，RQ1 {r1("int7_L16zero")} / {r1("int7_L16eqL24")}，同向且区间不含 0；int6 RQ2 {r2("int6")}。L56 是 21:14 PROTOCOL.md 改定的终点（U28）；Stage 8 RQ2 在 L56 的结论没有用原统计量复核。' + HS(SRC13) + '；',
   files=[PARTS['G_appendix.html']], why='2 D13-1 (handbook V59)')
R_('<tr><td>X1–X4 全部作者（补充 10 第 1 项）</td>',
   f'<tr><td>D13-1（补充 13 C-2）</td><td>代理与已发表结论不一致时按原 W 在 GPU 上重算</td><td>只在后改的 L56 上 RQ2 区间含 0（{r2("L56")}）；用户决定不做；锁定的 7 层积分终点上同向、区间不含 0</td><td><span class="st st-review">偏离</span></td><td>' + HS(SRC13) + '</td></tr>\n'
   f'<tr><td>D14-1（补充 14 第 3-3 项）</td><td>7.1B 用快路径补完，硬检查 ≥ 99% 名次一致</td><td>{STMT} 决定过程：{CHAIN}</td><td><span class="st st-review">偏离（停止）</span></td><td>' + HS(EV33) + '</td></tr>\n'
   '<tr><td>X1–X4 全部作者（补充 10 第 1 项）</td>', files=[PARTS['B_global2.html']], why='1+2 handbook deviation list (B)')
n = R_('按原 W 的 GPU 重算没有做（用户 2026-11-06 决定）。', '按原 W 的 GPU 重算没有做（用户 2026-11-06 决定，偏离 D13-1，见附录 V59）。', files=[PARTS['C_stage1_9.html']], why='2 D13-1 pointer (handbook C)')

# ---------------- 3 X4
X4ZH = ('同一引用档内，target 论文在标题位置读出第一作者的 D 高于 control，方向一致，但测试集不显著：按预注册在调参集选出最早层 L8，测试集 target − control 为 +0.023 [−0.001, +0.048]'
        + SZ('582 篇，10 档，团队整群 95% CI；381_stage13/reports/v42_paper_vs_team.md §3') + '。全部 1,178 篇合并时，L8–L40 为 +0.040 到 +0.060'
        + SZ('381_stage13/summary_x1x4/x4_recognition.csv；v42_paper_vs_team.md §3 Every layer 表 all 列') + '；测试集 L16–L48 也为正（+0.025 到 +0.060），但这些层是事后选的，只作探索。全部作者版本（+0.031 到 +0.052）没有做调参/测试拆分。')
R_(r'在同一引用档内，认得出的论文（target）比 control 更容易读出作者：标题位置 L8–L40 高 \+0\.04 到 \+0\.06，区间都不含 0<span class="src">（[^<]*）</span>', lambda m: X4ZH, files=[REP], regex=True, why='3 X4 (report #m3x1x4-results)')
R_('，认得出的论文在 L8–L40 更高<span class="src">（同节 Recognition 表，引用档内 target − control，全部作者 L8 +0.031 到 L40 +0.052，团队 CI 不含 0）</span>',
   '，认得出的论文方向上更高，但按预注册在测试集上不显著' + SZ('第一作者，调参集选层 L8，测试集 target − control +0.023 [−0.001, +0.048]，582 篇，团队整群 95% CI；v42_paper_vs_team.md §3。全部作者 L8 +0.031 到 L40 +0.052 是全部 1,178 对合并，没有做调参/测试拆分；b1_xall_report.md Recognition 表'), files=[REP], n_min=2, why='3 X4 (report m3x1x4 box + #pd-b1-xall)')
R_('，认得出的论文在 L8–L40 更高<span class="src">同节 Recognition 表：引用档内 target − control，全部作者 L8 +0.031 [0.017, 0.045] 到 L40 +0.052 [0.038, 0.067]</span>',
   '，认得出的论文方向上更高，但按预注册在测试集上不显著' + HS('第一作者，调参集选层 L8，测试集 target − control +0.023 [−0.001, +0.048]（582 篇，团队整群 95% CI；v42_paper_vs_team.md §3）；同节 Recognition 表的全部作者 L8 +0.031 [0.017, 0.045] 到 L40 +0.052 [0.038, 0.067] 是全部 1,178 对合并，没有做调参/测试拆分'),
   files=[PARTS['F_stage13.html']], why='3 X4 (handbook #s13-xall)')
R_('认得出的论文在 L8–L40 更高；', '认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）；', why='3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script)')
R_('认得出：author/title 的 target − control 在 L8–L40 为 +0.040 到 +0.060（区间不含 0），year 都含 0。',
   '认得出：author/title 的 target − control 在全部 1,178 篇合并时 L8–L40 为 +0.040 到 +0.060（区间不含 0），但按预注册（调参集选层 L8、测试集确认）测试集为 +0.023 [−0.001, +0.048]，未确认；测试集 L16–L48 也为正（+0.025 到 +0.060）但为事后选层，只作探索（v42_paper_vs_team.md §3）；year 都含 0。',
   files=[PARTS['F_stage13.html']], why='3 X4 (handbook #s13-x4)')

# ---------------- 4 E4b scheme 2 (+5 report §4 range)
R_('全部论文标题特异信号 L24 0.050、L40 0.061、L56 0.075，标准化只在训练折内拟合（作业 11500917）', 'E4b，target + control 1,395 篇的标题特异信号 L24 0.050、L40 0.061、L56 0.075，训练折标准化（作业 11500917）', files=[REP], why='4 E4b §1 zh')
R_('all papers L24 0.050, L40 0.061, L56 0.075, standardisation fitted on training folds only (job 11500917)', 'E4b, target + control (1,395 papers) L24 0.050, L40 0.061, L56 0.075, train-fold standardisation (job 11500917)', files=[REP], why='4 E4b §1 en')
R_('真标题 − false_0；全部 1,863 篇；论文 bootstrap', '真标题 − false_0；target + control 1,395 篇（剔除标题复用后全部论文 1,863 篇，E4b 只用其中 1,395 篇）；论文 bootstrap', files=[REP], why='4 E4b §6.11 zh')
R_('true − false_0; all 1,863 papers; paper bootstrap', 'true − false_0; target + control, 1,395 papers (1,863 after the title-reuse exclusion; E4b uses 1,395 of them); paper bootstrap', files=[REP], why='4 E4b §6.11 en')
R_('真标题 − false_0，全部 1,863 篇，L24–L60', '真标题 − false_0，target + control 1,395 篇，L24–L60', files=[REP], why='4 E4b §7 zh')
R_('true − false_0, all 1,863 papers, L24–L60', 'true − false_0, target + control, 1,395 papers, L24–L60', files=[REP], why='4 E4b §7 en')
STD = '两种标准化差别最大 0.0007（L24/L40/L56 ≤ 0.0004；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py）'
R_('改后最大变化 0.0075，正则化强度不变', STD + '，正则化强度不变', files=[REP], why='4 standardisation §6.11 zh')
R_('Largest change 0.0075, in the confirmatory configuration', 'The two standardisations differ by at most 0.0007 (≤ 0.0004 at L24/L40/L56; 381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py); in the confirmatory configuration', files=[REP], why='4 standardisation §6.11 en')
R_('381_stage13/reports/e4b_trainstd_compare.md "Max |new - orig|" 行与 All 4 configurations 表', '381_stage13/reports/e4b_trainstd_compare.md All 4 configurations 表', files=[REP], why='4 standardisation tag zh')
R_('381_stage13/reports/e4b_trainstd_compare.md "Max |new - orig|" line and All 4 configurations table', '381_stage13/reports/e4b_trainstd_compare.md, All 4 configurations table', files=[REP], why='4 standardisation tag en')
R_('上面的数字用全部论文（含测试折）算均值和标准差。改为只用训练折后（作业 11500917），全部论文平均 L24 +0.050、L40 +0.061、L56 +0.075',
   '上面“全部论文平均 +0.050 / +0.066 / +0.080”是 X1 对照流程（全部论文 1,863 篇）的数字。E4b（target + control 1,395 篇，训练折标准化，作业 11500917）为 L24 +0.050、L40 +0.061、L56 +0.075', files=[REP], why='4 E4b p4-plan narrative')
R_('。最大变化 0.0075<span class="src">（381_stage13/reports/e4b_trainstd_compare.md “Max |new − orig|” 行）</span>，正则化强度不变，没有结论翻转。',
   '。两种标准化差别最大 0.0007' + SZ('L24/L40/L56 ≤ 0.0004；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py') + '，正则化强度不变，没有结论翻转；0.066 / 0.080 与 0.061 / 0.075 的差别来自论文集合不同（1,863 篇 vs 1,395 篇），不是标准化。', files=[REP], why='4 standardisation p4-plan')
R_('全部论文平均：L24 为 +0.050（原来 +0.045），L40 为 +0.066（原来 +0.062），L56 为 +0.080（原来 +0.081）', 'X1 对照流程，全部论文 1,863 篇平均：L24 为 +0.050（原来 +0.045），L40 为 +0.066（原来 +0.062），L56 为 +0.080（原来 +0.081）', files=[REP], why='4 X1-pipeline label (p4-plan)')
R_('全部论文标题特异信号 L16–L60 +0.042 到 +0.080，按团队分折并剔除标题复用（1,863 篇）', 'L16–L60 +0.041 到 +0.075（E4b，target + control 1,395 篇，训练折标准化），按团队分折并剔除标题复用', files=[REP], why='5 report §4 range')
R_('训练折内标准化，全部 1,863 篇，L40 +0.061', '训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇），L40 +0.061', files=['NOTES'], why='4 E4b notes 24')
R_('训练折内标准化，全部 1,863 篇：L24 +0.050', '训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇）：L24 +0.050', files=['NOTES'], n_min=3, why='4 E4b notes 39/40/73')
R_('all papers (1,863), team folds', 'target + control (1,395), team folds', files=[DECK], why='4 E4b deck method-page footnote')
R_('标准化改为只在训练折内拟合，最大变化 0.0075，无结论翻转。', '标准化改为只在训练折内拟合；两种标准化差别最大 0.0007，无结论翻转（381_stage13/e4b_standardisation_check/）。', files=[ADV], why='4 standardisation (advisor)')
R_('训练折标准化重算 11500917，最大差 0.0075，无翻转', '训练折标准化重算 11500917，两种标准化差别最大 0.0007，无翻转', files=[PROC], why='4 standardisation (process)')
R_('全部论文的标题特异信号最大差 0.0075；', '全部论文的标题特异信号最大差 0.0007（更正：原写 0.0075 来自 e4b_trainstd_compare.md 在 L24/L40/L56 混入 X1 行的标注错误；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py）；', files=[PARTS['D_stage10_11.html']], why='4 standardisation (handbook D)')
R_('全部论文信号 L40 +0.066 → +0.061、L56 +0.080 → +0.075，区间都 &gt; 0；', 'E4b（target + control 1,395 篇）L40 +0.061、L56 +0.075，区间都 &gt; 0（+0.066 / +0.080 是 X1 对照流程全部 1,863 篇的数字，差别来自论文集合，不是标准化）；', files=[PARTS['D_stage10_11.html']], why='4 E4b (handbook D)')
R_('：最大差 0.0075，α 不变', '：两种标准化差别最大 0.0007，α 不变', files=[PARTS['G_appendix.html']], n_min=2, why='4 standardisation (handbook G)')
R_('L24 +0.050，L40 +0.066，L56 +0.080；', 'L24 +0.050，L40 +0.061，L56 +0.075（E4b，target + control 1,395 篇；X1 对照流程全部 1,863 篇为 +0.050 / +0.066 / +0.080）；', files=[TD['experiment_walkthrough_methods_zh']], why='4 E4b (walkthrough methods)')
R_('只在训练折内标准化的重算最大差 0.0075。', '两种标准化差别最大 0.0007（L24/L40/L56 ≤ 0.0004）。', files=[TD['experiment_walkthrough_methods_zh']], why='4 standardisation (walkthrough methods)')
OLDN = '全部论文信号 L40 0.066 → 0.061、L56 0.080 → 0.075'
NEWN = 'E4b（target + control 1,395 篇）为 L40 0.061、L56 0.075；两种标准化差别最大 0.0007，0.066 / 0.080 是 X1 对照流程全部 1,863 篇的数字，差别来自论文集合，不是标准化'
R_(OLDN, NEWN, files=[TD['experiment_walkthrough_methods_zh'], ADD], n_min=2, why='4 E4b narrative (walkthrough methods, addendum)')
R_('剩 1,863 篇（target 896、control 499）。</li>', '剩 1,863 篇（target 896、control 499）；E4b 信号只用其中 target + control 的 1,395 篇。</li>', files=[TD['experiment_walkthrough_methods_zh']], why='4 E4b 1,395 note')
R_('剔除一题两用的论文（剩 1,863 篇）、只在训练折内标准化（最大差 0.0075，结论不变）', '剔除一题两用的论文（剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇）、只在训练折内标准化（两种标准化差别最大 0.0007，结论不变）', files=[TD['methods_handbook_guide_plain_zh']], why='4 E4b (guide)')
R_('剩 1,863 篇。原版标准化用了全部论文（含测试折），复核时改为只在训练折内标准化重算，L40 从 0.066 变为 0.061、L56 从 0.080 变为 0.075，结论不变。',
   '剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075。原版标准化用了全部论文（含测试折），复核时改为只在训练折内标准化；两种标准化差别最大 0.0007，结论不变。', files=[TD['experiment_walkthrough_zh']], why='4 E4b (walkthrough)')
R_('最后剩 1,863 篇。结果从 L24 起', '最后剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇。结果从 L24 起', files=[TD['keys_and_shelves_script_zh_en']], why='4 E4b (keys & shelves zh)')
R_('原版标准化用了全部论文（含测试折），改成只在训练折内标准化重算后，L40 为 +0.061、L56 为 +0.075，结论不变。', '原版标准化用了全部论文（含测试折），改成只在训练折内标准化；两种标准化差别最大 0.0007，L40 为 +0.061、L56 为 +0.075，结论不变。', files=[TD['keys_and_shelves_script_zh_en']], why='4 standardisation (keys & shelves zh)')
R_('That leaves 1,863 papers.', 'That leaves 1,863 papers, of which the E4b signal uses the 1,395 target and control papers.', files=[TD['keys_and_shelves_script_zh_en']], why='4 E4b (keys & shelves en)')
R_('refitting the standardisation on training folds only gives +0.061 at L40 and +0.075 at L56.', 'refitting the standardisation on training folds only changes the values by at most 0.0007 (+0.061 at L40, +0.075 at L56).', files=[TD['keys_and_shelves_script_zh_en']], why='4 standardisation (keys & shelves en)')
R_('在按作者团队分折、剔除标题复用后（1,863 篇）', '在按作者团队分折、剔除标题复用后（1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇）', files=[TD['progress_report_for_advisor_zh']], why='4 E4b (progress talk doc)')
R_('原版标准化用了全部论文，改为只在训练折内标准化重算后，L40 为 0.061、L56 为 0.075，结论不变。', '原版标准化用了全部论文，改为只在训练折内标准化；两种标准化差别最大 0.0007，L40 为 0.061、L56 为 0.075，结论不变。', files=[TD['progress_report_for_advisor_zh']], why='4 standardisation (progress talk doc)')
R_('“全部论文”信号用 1,863 篇，组间比较用 1,395 篇。', 'E4b 的信号和组间比较都用 target + control 的 1,395 篇；1,863 篇是剔除标题复用后的全部论文（X1 对照流程用）。', files=[ADD], why='4 E4b (addendum)')
R_('换成随机论文的作者后约为 0）', '换成随机论文的作者后约为 0；E4b，target + control 1,395 篇，训练折标准化）', files=[ADV], why='4 E4b label (advisor)')
R_('标题位置 probe 少量信号（L24 +0.050、L40 +0.061、L56 +0.075）', '标题位置 probe 少量信号（E4b，target + control 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075）', files=[PROC], why='4 E4b label (process)')
# 'original E4b first token +0.066'
R_('原 E4b 第一个 token +0.066<span class="src">（同节 Vpd 表 e4b_parity 行，L40 [0.059, 0.073]）</span>',
   '逐个排除版（4,654 篇）第一个 token +0.066<span class="src">（同节 Vpd 表 e4b_parity 行，L40 [0.059, 0.073]）</span>；原 E4b（1,395 篇）+0.061' + SZ('同一报告第 2 节 V0 e4b_parity L40'), files=[REP], n_min=2, why='4 原 E4b +0.066 (report)')
R_('原 E4b 第一个 token +0.066', '逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061', why='4 原 E4b +0.066 (others)')
# Vpd described as five-title average
VPZ = 'E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071'
R_('E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题', VPZ, why='4 Vpd wording (d)')
R_('E4b 减 5 个假标题（L40 姓首 token +0.076 [0.068, 0.083]，4,654 篇）', 'E4b 逐个假标题排除版（L40 姓首 token +0.076 [0.068, 0.083]，4,654 篇，每篇平均约 1.5 个可用假标题；预注册版 1,395 篇为 +0.071）', why='4 Vpd wording (progress talk doc)')
R_('减 5 个假标题平均 +0.076', '逐个假标题排除版（4,654 篇，每篇约 1.5 个可用假标题）+0.076', files=[ADV], why='4 Vpd wording (advisor flag)')
R_('E4b minus five false titles: surname L40 +0.076', 'E4b, per-donor exclusion (4,654 papers, ~1.5 false titles each): surname L40 +0.076', files=[DECK], why='4 Vpd wording (deck 81)')
R_('E4b minus five false titles (per-donor exclusion, 4,654 papers)', 'E4b with per-donor exclusion (4,654 papers, ~1.5 usable false titles per paper, 0–4; pre-registered false_0 version: +0.071 on 1,395 papers)', files=[READ, TD['stage13_script_zh_en']], n_min=2, why='4 Vpd wording (README, Stage 13 script en)')
R_('| E4b minus five false titles (per-donor exclusion) |', '| E4b with per-donor exclusion (~1.5 usable false titles per paper) |', files=[READ], why='4 Vpd wording (README table)')
R_('<span class="h">Five false titles (batch 1)</span>', '<span class="h">Per-donor exclusion (batch 1)</span>', files=[DECK], why='4 Vpd wording (deck 72 note title)')

# ---------------- 6 rounding
R_('[4.7, 13.9]', '[4.8, 14.0]', files=['NOTES'], why='6 Pilot50 CI (notes 14)')
R_('[0.047, 0.139]', '[0.048, 0.140]', files=['NOTES'], n_min=3, why='6 Pilot50 CI (notes 14/30/61)')
R_('0.90 [0.87, 0.94]', '0.90 [0.86, 0.94]', n_min=5, why='6 X3 lower bound 0.8647 -> 0.86')
R_('low +6.8 [2.6, 11.6]', 'low +6.8 [2.5, 11.6]', files=[DECK], why='6 deck slide 17')
R_('+0.207 [0.20, 0.22]', '+0.207 [0.195, 0.220]', files=['NOTES'], why='6 notes 30')
R_('年份 R² 从 0.39（L16）', '年份 R² 从 0.38（L16）', files=[REP], why='6 M2 year R² L16 (写法不统一)')

# ---------------- 7 definition issues
R_('名字先验只占目标−对照差的约 1/3', '名字先验只占目标−对照差的约 0.35（约三分之一）', files=[REP, ADV], n_min=2, why='7 约 1/3 -> 0.35')
R_('Name prior is only ~1/3 of the gap', 'Name prior (delete-title condition) is only ~0.35 of the gap', files=[DECK], why='7 ~1/3 -> 0.35 (deck 30)')
R_('→ prior ≈ 19% of the gap', '→ pure name prior ≈ 19% of the gap (delete-title prior of §6.12: 0.35)', files=[DECK], why='7 N2 19% definition (deck 67)')
R_('先验约占 19%〔0.047 ÷ 0.247，由上两数算出〕', '纯名字先验约占 19%〔0.047 ÷ 0.247，由上两数算出；与 §6.12 删标题条件下的先验 0.35 定义不同〕', files=['NOTES'], why='7 N2 19% definition (notes 67)')
R_('领域准确率约 0.70，', '领域准确率约 0.70–0.72，', files=[ADV], why='7 约 0.70 -> 0.70–0.72 (advisor)')
R_('领域约 0.70）', '领域约 0.70–0.72）', files=[PROC], why='7 约 0.70 -> 0.70–0.72 (process)')

for p, s in S.items():
    assert not re.search('minyan', s, re.I), p
    if s != bkp(p).read_text(encoding='utf-8'): p.write_text(s, encoding='utf-8')
NOTES.write_text(json.dumps(NJ, ensure_ascii=False, indent=1))
json.dump(LOG, open(Path(__file__).parent / 'apply_log_20261107g.json', 'w'), ensure_ascii=False, indent=1)
print('rules applied', len(LOG)); print('R2EQ', R2EQ)
