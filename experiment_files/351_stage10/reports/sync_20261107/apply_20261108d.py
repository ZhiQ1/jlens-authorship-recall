"""Sync 2026-11-08 d: fix round for v30 after the step-4 checker (out_20261108_192440/wording_v30/). LOCAL only.
Items 1-9 of the coordinator's list: L02 wording (attribution: 10 of 25 Stage 10 pairs > 0.25, max 0.367; 99.81% is 3-3), deck version label on the advisor page,
v30 numbers registered (claims_defs_v9), D13-1 passage version labels (report v30 / PPT v21), deck slides 77/81/82 (p9, 258/462, L01 consequences, 2-11 stop),
note 82 (no redo plan; L33-L40) and shorter notes 72/81 (overflow), talk-doc progress report C04/C08/2-11, README X4 sentence, 2,103.
Fresh backups *.before_20261108d (asserted unused). Handbook = build_methods.py(parts) with K regenerated from the report (same conversion as apply_20261108c.py);
process index = build_process_report.py. Log appended to sync_20261108c_manifest.md under "round d (after checks)"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; PROCH = R / 'process_report/index.html'
AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'
HB = R / 'methods/methods_handbook.html'; K = R / 'methods/parts/K_post_defence.html'
TD = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'keys_and_shelves_script_zh_en',
                                            'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']}
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, K, *TD.values()]
SUF = '.before_20261108d'
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
S = {p: p.read_text(encoding='utf-8') for p in EDIT}
NJ = json.loads(S[NOTES]); LOG = []
def rel(p): return str(p).replace(str(R) + '/', '')
def R_(old, new, files, n=None, why=''):
    tot = 0
    for p in files:
        if isinstance(p, tuple): t = NJ[p[1]]['text']
        else: t = S[p]
        c = t.count(old)
        if not c: continue
        t = t.replace(old, new)
        if isinstance(p, tuple): NJ[p[1]]['text'] = t
        else: S[p] = t
        tot += c; LOG.append((why, ('notes_zh.json #' + p[1]) if isinstance(p, tuple) else rel(p), old, new, c))
    assert tot >= 1 and (n is None or tot == n), (why, tot, n, old[:80])
ZH = [REP, ADV, PROCMD, AUD, ADD, TD['experiment_walkthrough_zh'], TD['experiment_walkthrough_methods_zh'], TD['methods_handbook_guide_plain_zh'], TD['progress_report_for_advisor_zh']]
# 1. L02 wording
L02 = ('原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment.json）；'
       '3-3 在 7 篇论文的 23,280 行上按 0.25 计 99.81% 在容差内。这一量级与 3-3 查明的 bf16 舍入随前向长度变化（最大约 0.46）一致，但容差是在看到数据后放宽到 0.5 的，属于事后修改。')
L02_EN = ('With the original 0.25, 10 of the 25 lens × layer pairs of the Stage 10 main-round parity check (12 contexts, 52 token positions) exceeded 0.25, max 0.367 (parity_before_tol05_amendment.json); '
          'in 3-3, 99.81% of 23,280 rows (7 papers) were within 0.25. This size matches the bf16 rounding that changes with forward length found in 3-3 (up to about 0.46), '
          'but the tolerance was relaxed to 0.5 after seeing the data, a post-hoc change.')
R_('最多变 0.070。保留在事后改动清单里', '最多变 0.070。' + L02 + '保留在事后改动清单里', ZH, 10, '1 L02 attribution')
R_('只有按 0.5 才通过。</p>', '只有按 0.5 才通过。' + L02 + '</p>', [TD['keys_and_shelves_script_zh_en']], 1, '1 L02 attribution (keys zh)')
R_('passes only at 0.5.</p>', 'passes only at 0.5. ' + L02_EN + '</p>', [TD['keys_and_shelves_script_zh_en']], 1, '1 L02 attribution (keys en)')
R_('post-hoc change, kept listed);', 'post-hoc change, kept listed; ' + L02_EN + ');', [READ], 2, '1 L02 attribution (README)')
R_('parity tolerance 0.25 → 0.5 was used (Stage 10 main round, max 0.367);', 'parity tolerance 0.25 → 0.5 was used, a post-hoc change (main round: 10 of 25 pairs above 0.25, max 0.367; size matches bf16 rounding, up to ~0.46);',
   [DECK], 1, '1 L02 attribution (slide 82)')
R_('容差 0.25 → 0.5 已用于 Stage 10 主轮（最大差 0.367）', '容差 0.25 → 0.5 已用于 Stage 10 主轮（原定 0.25 时 25 个组合有 10 个超出，最大差 0.367；3-3 按 0.25 有 99.81% 在容差内；量级与 bf16 舍入随前向长度变化（最大约 0.46）一致，但放宽属事后修改）',
   [('N', '82')], 1, '1 L02 attribution (note 82)')
# 2. advisor deck label
R_('〔2026-11-06 已更新：当前为 v20（本地已备，待发布）；见页首更新框〕', '〔2026-11-08 已更新：当前为 v21；见页首更新框〕', [ADV], 1, '2 advisor deck label')
# 3. v30 numbers registered
R_('；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记',
   '；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数）', ZH, 10, '3 v30 numbers registered')
R_('数字核对已登记 680 个、4,307 处全部一致，约 1,024 个未登记', '第 30 版的数字已登记进严格核对（claims_defs_v9），另约 1,024 个结论性数字未登记', [('N', '82')], 1, '3 v30 numbers registered (note 82)')
R_('about 1,024 conclusion-like numbers not registered (count from 2026-11-07).', 'the v30 numbers are registered in the strict checker (claims_defs_v9); about 1,024 conclusion-like numbers are not registered (count from 2026-11-07).', [READ], 2, '3 v30 numbers registered (README)')
# 4. D13-1 passage version labels
R_('报告 v29 和 PPT v20 都以锁定计划的', '报告 v30 和 PPT v21 都以锁定计划的', [REP], 1, '4 D13-1 version labels')
# 5. deck slides
R_('within bin same timing as A, larger gap', 'within bin (258 of 462 C papers, 6 bins) same timing as A, larger gap', [DECK], 1, '5 slide 77 258/462')
R_('colon numerator B/A 0.72–0.87<span class="src">(b1_p12f_report.md)</span>', 'colon numerator B/A 0.72–0.87; p9: 694–711 papers per false title, different sets, unweighted<span class="src">(b1_p12f_report.md)</span>', [DECK], 1, '5 slide 81 p9')
R_('C / D completion done (C 462 papers: same timing as A)', 'C / D completion done (C 462 papers; within bin 258 of 462 vs A: same timing)', [DECK], 1, '5 slide 81 258/462')
R_('Written 2026-11-06; last two items added 2026-11-08 (v30)', 'Written 2026-11-06; last three items added 2026-11-08 (v30)', [DECK], 1, '5 slide 82 subtitle')
R_('pipeline use false_0 only, no plan</li></ul>', 'pipeline use false_0 only, no plan</li><li><b>Layer gap, stopped item: </b>X4 year onset somewhere in L33–L40; Jacobian vs logit jump between L32 and L40; '
   'X4 first-author peak could be L33–L47 · 2-11 stopped (first-name reproduction 0.880 &lt; 0.90)</li></ul>', [DECK], 1, '5 slide 82 L01 consequences + 2-11')
# 6. notes
R_('M5 B 部分和 E4b 的 X1 对照流程只用 false_0；', 'M5 B 部分和 E4b 的 X1 对照流程只用 false_0，没有补做计划；落在层缺口里的只有描述：X4 年份起点在 L33–L40 之间，Jacobian 对 logit 的跳变在 L32–L40 之间，X4 第一作者峰值可能在 L33–L47；',
   [('N', '82')], 1, '6 note 82 no plan + L33-L40')
R_('（2-1、2-2 用较省但包含原始提示逐位复现重拟合的硬检查；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述）', '', [('N', '81')], 1, '6 note 81 shortened (overflow)')
R_('批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；', '批次 1 结束后已由编排作业开始运行；', [('N', '81')], 1, '6 note 81 shortened (duplicate C/D clause)')
R_('，逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061；置换对照首字母仍 +0.018，其余 ≈ 0', '', [('N', '81')], 1, '6 note 81 shortened (E4b detail, in note 72)')
R_('〔381_stage13/config/prereg_addendum14_deviations.json；381_stage13/summary_b3_71b/gate.json；381_stage13/b3_33_v2/v2_C1_summary.json〕；3-4', '〔381_stage13/config/prereg_addendum14_deviations.json〕；3-4', [('N', '81')], 1, '6 note 81 shortened (sources)')
R_('probe 的定义：输入是第 l 层标题最后一个 token 的残差；目标是模型自己在 L63、在预测该角色名字 token 的位置上的状态，按论文平均；ridge，按作者团队分折；在 9,137 个名字 token 的词表里解码；标题特异 = 真标题 − false_0。', '',
   [('N', '72')], 1, '6 note 72 shortened (probe definition is in report / handbook)')
R_('〔381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv（version = V0 / Vpd / V5x0，列 tc / tc_lo / tc_hi；引用档内 target − control，团队整群 bootstrap 2,000 次 95% CI）；381_stage13/reports/e4b_alltok.md；b1_e4b5_report.md〕',
   '〔381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv；b1_e4b5_report.md〕', [('N', '72')], 1, '6 note 72 shortened (source)')
R_('〔381_stage13/reports/b1_e4b5_report.md 第 2 节与 “Per-donor exclusion” 节，目标 + 对照，团队聚类 95% CI〕', '〔381_stage13/reports/b1_e4b5_report.md〕', [('N', '72')], 1, '6 note 72 shortened (source 2)')
# 7. talk-doc progress report
PRD = [TD['progress_report_for_advisor_zh']]
o = ('；P1/P2 五个假标题也已完成（5 个假标题平均为主结果，与 false_0 版的差别区间都含 0，结论不变）<span class="src">（b1_p12f_report.md）</span>。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）'
     '已开始：C / D 组补全已完成（C 的信号更大，但时间点与 A 相同）<span class="src">（b2_cd_report.md）</span>；2-11 按预注册停止，改为 2-11b（补充 15），只跑第 0 个分片；')
nw = ('；P1/P2 五个假标题也已完成：按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列，两版之差的区间都含 0，结论不变；“:” 位置分子 B/A 5 个假标题版 0.72–0.87，false_0 版 0.78–0.99'
      '（B 的比例高只因分母约为 A 的一半）；p9 各假标题 694–711 篇，集合不同，未加权<span class="src">（391_groups/reports/b1_p12f_report.md）</span>。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）'
      '已开始：C / D 组补全已完成——C 组未写出作者 462 篇，同一引用档内与 A 比较只用到其中 258 篇（6 个引用档，A 323 篇），时间点与 A 相同；C 的真假标题差距更大（分母 C 0.559、A 0.407，'
      '比例差主要反映分母不同）；D 33 篇按补充 11 只作描述<span class="src">（391_groups/reports/b2_cd_report.md）</span>；2-11 模型自生成名字的首名复现率 0.880 &lt; 0.90，按预注册停止，'
      '改为 2-11b（补充 15），只跑第 0 个分片；')
R_(o, nw, PRD, 1, '7 talk-doc progress report C04/C08/2-11')
# 8. README X4 sentence
R_('In X4, the X4 recognised − control difference is no longer counted as H2 evidence (text-only BERT baseline +0.088 not weaker than Qwen L8 +0.018).',
   'In X4, the recognised − control difference (test set L8 +0.023 [−0.001, +0.048], not significant) is no longer counted as H2 evidence (text-only BERT baseline +0.088 not weaker than Qwen L8 +0.018).', [READ], 1, '8 README X4 sentence')
# 9. thousands separator
R_('n = 462 (2103 authors)', 'n = 462 (2,103 authors)', [REP], 5, '9 2,103')

# write; K regenerated from the report (conversion of apply_20261108c.py)
sys.argv = [sys.argv[0], '--dry']
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8')
mk = src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')]
exec(mk)
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
head = S[K][:S[K].index(lead) + len(lead)]
S[K] = head + makeK(S[REP]) + '\n</section>'; LOG.append(('K regenerated from the report', rel(K), '(part 5 of the report)', '(regenerated)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + SUF))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ⏎ ')
md = ['', '## round d (after checks)', '', 'Script `sync_20261107/apply_20261108d.py` (checker out_20261108_192440/wording_v30/; backups `*.before_20261108d`). Handbook and process page rebuilt; K regenerated from the report.', '',
      '| # | rule | file | before | after | count |', '|---|---|---|---|---|---|']
md += [f'| d{i} | {cut(w, 60)} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {c} |' for i, (w, f, o, n, c) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
(R / 'sync_20261107/apply_log_20261108d.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=1), encoding='utf-8')
print('round d:', len(LOG), 'changes')
