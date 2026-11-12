"""Round i (2026-11-12, LOCAL only; autonomous changes only, no new conclusions, H1/H2/H3 unchanged). Sources: review_queue.md B2-9, B2-10, B2-11, B3-1;
381_stage13/reports/b2_f1team_report.md (2-2), b3_3_1_report.md (3-1). 1) 2-2 done: C16 premise + L13 limitation; 2) 3-1: L01 updated, C01 premise (logit within ±0.005 at L41-L49,
J-lens T − C negative L41-L56), CI-method note, J-lens vs logit range statement with the new layers; 3) status (2-2, 2-7/2-9, 2-11b done; 2-1 stopped; 3-1 done; 3-2 194/504; x4tok);
4) conclusions_v30_draft.md. Numbers asserted against the reports. Backups *.before_20261112i. K regenerated, handbook + process rebuilt. Manifest section "round i"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'
READ = R / 'github/README_draft_20261106b.md'; T = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']}
K = R / 'methods/parts/K_post_defence.html'; CONC = W / 'conclusions_v30_draft.md'; HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, *T.values(), K, CONC]
SUF = '.before_20261112i'
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
f1 = (R13 / 'reports/b2_f1team_report.md').read_text(encoding='utf-8'); b3 = (R13 / 'reports/b3_3_1_report.md').read_text(encoding='utf-8')
for frag in ['| name | L48 | teamA |', '-0.050 [-0.078, -0.022]', '-0.063 [-0.094, -0.033]', '-0.058 [-0.087, -0.029]', '+0.237 [+0.207, +0.268]', '+0.237 [+0.208, +0.265]', '| L24 | 0.643 |', '| L40 | 0.852 |', '| L48 | 0.940 |', 'Hard check: PASS']:
    assert frag in f1, frag
for frag in ['| L41 | b3_3-1 | +0.008 [+0.001, +0.016] | +0.026 [+0.015, +0.037] | +0.014 [+0.008, +0.020] | -0.017 [-0.032, -0.002] |', '| L47 | b3_3-1 | -0.011 [-0.017, -0.004] | +0.025 [+0.016, +0.034] | +0.001 [-0.005, +0.006] | -0.035 [-0.049, -0.022] |',
             '| L49 | b3_3-1 | +0.010 [+0.002, +0.018] | +0.056 [+0.045, +0.066] | +0.025 [+0.018, +0.031] | -0.043 [-0.059, -0.028] |', '| L47 | b3_3-1 | -0.004 [-0.006, -0.002] | +0.001 [-0.002, +0.004] | -0.003 [-0.004, -0.001] | -0.005 [-0.009, -0.001] |',
             '| L43 | b3_3-1 | -0.003 [-0.010, +0.003] | +0.028 [+0.019, +0.037] | +0.007 [+0.002, +0.012] |']:
    assert frag in b3, frag
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; NJ = json.loads(S[NOTES]); LOG = []
def R_(old, new, files, n=None):
    tot = 0
    for p in files:
        if isinstance(p, tuple): t = NJ[p[1]]['text']
        else: t = S[p]
        c = t.count(old)
        if not c: continue
        t = t.replace(old, new); tot += c
        if isinstance(p, tuple): NJ[p[1]]['text'] = t
        else: S[p] = t
        LOG.append((('notes_zh.json #' + p[1]) if isinstance(p, tuple) else str(p).replace(str(R) + '/', ''), old, new, c))
    assert tot >= 1 and (n is None or tot == n), (old[:70], tot, n)
NK = [('N', k) for k in NJ]
ZH = [REP, ADV, PROCMD, AUD, ADD, *T.values()] + NK
F1T = ('F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L62：+0.237 / +0.237 / +0.238；'
       '中间层在两半都为零或负（7/7 层）；D12-2 硬检查 PASS。局限：中间层 lens 矩阵随拟合集变化大（A–B 余弦 L24 0.64、L40 0.85、L48 0.94；L24 top-10 重合 0.28）')
F1L = 'F1 对半拆分（批次 2 第 2-2 项，已完成）：'
C01N = ('3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L56 为负'
        '（L41 −0.017 [−0.032, −0.002]，L47 −0.035，L49 −0.043）、从 L57 起为正，“中间层没有领先”仍成立（3-1 用团队整群区间，Stage 10 已发表的是论文 bootstrap 区间，点估计相同；381_stage13/reports/b3_3_1_report.md）')
JL = '3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-lens +0.001 [−0.005, +0.006]，logit −0.003）'
# ---- status (zh)
R_('第 0 片已完成，其余分片运行中', '已完成，结论待定', ZH + [CONC], None)
R_('其余各项进行中（含 Stage 9 Fit B 与 holdout、F1 对半拆分、名字位置 probe 等）', '其余各项进行中', [ADV, AUD, ADD], 3)
R_('名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中',
   '名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定）', ZH, None)
R_('名字位置 probe 已完成（H3 部分支持）；Patchscope 的最终分析进行中；2-1 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中；',
   '名字位置 probe 已完成（H3 部分支持）；Patchscope 已完成，结果待写入（描述性）；2-2 已完成；2-1 停止（D12-1，待用户定）；', [T['progress_report_for_advisor_zh']], 1)
R_('名字位置 probe 已完成（H3 部分支持）；Patchscope 最终分析进行中；2-1 门槛重跑中（作业被误杀，已加看护）', '名字位置 probe、2-2 已完成；Patchscope 已完成，结果待写入；2-1 停止（D12-1，待定）', [('N', '81')], 1)
R_('3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中）', '3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504）', ZH, None)
R_('3-1、3-2 编排作业已提交，第二批全部结束后自动开始（进行中）', '3-1 已完成，3-2 运行中（194 / 504）', ZH, None)
# ---- status (en)
EN_OLD = ('shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis running; '
          '2-1 gate re-run (job killed by the cluster epilog, watchdog added); other items in progress;')
EN_NEW = 'done, conclusion pending; 2-2, 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9) done, results to be written (descriptive); 2-1 stopped (D12-1, user to decide);'
R_(EN_OLD, EN_NEW, [DECK, READ], 2)
R_('2-11b: other shards running; 2-3, 2-4, 2-5, 2-8, 2-10 done; Patchscope: final analysis running; 2-1 gate re-run', '2-11b done, conclusion pending; 2-2, 2-3, 2-4, 2-5, 2-7/2-9, 2-8, 2-10 done; 2-1 stopped (D12-1)', [READ], 1)
R_('3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: queued, start after batch 2', '3-1 Stage 10 L41–L47, L49: done · 3-2 L0–L23: running (194/504)', [DECK], 1)
R_('Stage 10 L41–L47, L49 and L0–L23 queued, start after batch 2;', 'Stage 10 L41–L47, L49 done (3-1); L0–L23 running (3-2, 194/504);', [READ], 1)
R_('| 3-1, 3-2 queued (after batch 2);', '| 3-1 done; 3-2 running (194/504);', [READ], 1)
# ---- L01 / C01 / Jacobian range
R_('（补充 14 只补 L41–L47、L49 和 L0–L23，都在排队）', '（补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504）', ZH, None)
R_('“L24–L48 约为 0”在缺口层没有测过', '“L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；' + C01N, ZH, None)
R_('Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道）', 'Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；' + JL + '）', ZH, None)
R_('明显好于 logit lens（约 −3.0）', '明显好于 logit lens（约 −3.0；这是真标题下的读出水平。' + JL + '，381_stage13/reports/b3_3_1_report.md）', [REP], 1)
R_('beat the logit lens from L40 on (the previous measured layer is L32, so the jump lies somewhere in L33–L40; about −3.0)',
   'beat the logit lens from L40 on (the previous measured layer is L32, so the jump lies somewhere in L33–L40; about −3.0; this is the true-title readout level. With the 3-1 layers, the title-specific signal is +0.007 to +0.014 for the J-lens at L41–L46 with logit ≈ 0, and nearly equal at L47: J-lens +0.001 [−0.005, +0.006], logit −0.003; b3_3_1_report.md)', [REP], 1)
R_('Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划；', 'Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划（L41–L47、L49 已由 3-1 补齐）；', [('N', '82')], 1)
R_('(no L25–L31, L33–L39; no plan to fill)', '(no L25–L31, L33–L39; no plan to fill; L41–L47, L49 filled by 3-1)', [DECK], 1)
R_('(no L25–L31, L33–L39) with no plan to fill them', '(no L25–L31, L33–L39) with no plan to fill them (L41–L47, L49 filled by 3-1 on 2026-11-12: logit target − control within ±0.005 there, J-lens negative to L56, no middle-layer lead; L0–L23 running)', [READ], 2)
# ---- 2-2 result item
SRC = '381_stage13/reports/b2_f1team_report.md'
R_('<li id="pd-b2-np">', f'<li id="pd-b2-f1"><b>{F1L}</b>{F1T}<span class="src">（{SRC}）</span>。</li>\n<li id="pd-b2-np">', [REP], 1)
R_('<li><b>名字位置 probe（批次 2 第 2-5 项', f'<li><b>{F1L}</b>{F1T}<span style="color:#8a8f98;font-size:.8em">（{SRC}）</span>。</li><li><b>名字位置 probe（批次 2 第 2-5 项', [ADV, AUD, ADD], 3)
R_('\n- **名字位置 probe（批次 2 第 2-5 项', f'\n- **{F1L}**{F1T}【{SRC}】。\n- **名字位置 probe（批次 2 第 2-5 项', [PROCMD], 1)
R_('作者提示 lens 没做对半拟合。<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：Fit B 与 F1 对半拆分都列入批次 2；见页首更新框〕</span>',
   '作者提示 lens 没做对半拟合。<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：Fit B 与 F1 对半拆分都列入批次 2；2026-11-12 已更新：F1 对半拆分已完成，F2 的结论在两半都成立，中间层 lens 矩阵随拟合集变化大（A–B 余弦 L24 0.64、L40 0.85、L48 0.94）；Fit B（2-1）停止，待定；见页首更新框〕</span>', [ADV], 1)
# ---- conclusions draft
c = S[CONC]
for a, b in [('样本不完整（F1 只用 40 篇拟合；对半拆分 2-2 进行中）', '样本不完整（F1 只用 40 篇拟合；对半拆分 2-2 已完成：' + F1T + '，`R13/reports/b2_f1team_report.md`）'),
             ('事后改判据（一致性容差 0.25 → 0.5，主轮数据靠 0.5 才通过，见 CHK A2）〕', '事后改判据（一致性容差 0.25 → 0.5，主轮数据靠 0.5 才通过，见 CHK A2）；2026-11-12：' + C01N + '〕'),
             ('也没有 L41–L47、L49、L0–L23）', '也没有 L0–L23（3-2 运行中）；L41–L47、L49 已由 3-1 补齐）'),
             ('- **第三批**（3-1 补 L41–L47、L49；3-2 补 L0–L23）：编排作业 b3_orch 等第二批全部结束后自动开始。3-3 已停止（见 L07）。', '- **第三批**：3-1（补 L41–L47、L49）已完成；3-2（补 L0–L23）运行中（194 / 504）。3-3 已停止（见 L07）。'),
             ('- 2-7、2-9（Patchscope）：最终分析进行中。', '- 2-7、2-9（Patchscope）：已完成，结果待写入（描述性）；x4tok 已补全部层。'),
             ('- 2-1：门槛重跑中（集群作业结束脚本误杀，已加看护作业）。2-2：进行中。', '- 2-1：停止（D12-1，待用户定）。2-2：已完成（见 C16、L13）。'),
             ('  - L41–L47、L49 由 3-1 补，排队中。L0–L23 由 3-2 补，排队中，只补 logit 和 public，只补 target + control 6,841 篇。', '  - L41–L47、L49 已由 3-1 补齐（2026-11-12）。L0–L23 由 3-2 补，运行中（194 / 504），只补 logit 和 public，只补 target + control 6,841 篇。'),
             ('  - "L24–L48 约为 0"在缺口层没有测过。', '  - "L24–L48 约为 0"在 L25–L31、L33–L39 没有测过；' + C01N + '。\n  - "Jacobian lens 从 L40 起明显好于 logit"（真标题水平）：' + JL + '。'),
             ('  - F1 作者 lens 只用 40 篇拟合（2-2 进行中）；', '  - F1 作者 lens 只用 40 篇拟合；2-2 对半拆分已完成，F2 结论在两半都成立，但中间层 lens 矩阵随拟合集变化大（A–B 余弦 L24 0.64、L40 0.85、L48 0.94；L24 top-10 重合 0.28）；'),
             ('  - Stage 9 Fit B 停在 66 / 100（2-1 进行中）。', '  - Stage 9 Fit B 停在 66 / 100（2-1 停止，D12-1，待用户定）。')]:
    assert c.count(a) == 1, a[:60]; c = c.replace(a, b); LOG.append(('~/jlens_work/conclusions_v30_draft.md', a, b, 1))
S[CONC] = c
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
S[K] = S[K][:S[K].index(lead) + len(lead)] + makeK(S[REP]).replace('id="pd-b2-np"', 'id="k-b2-np"').replace('id="pd-b2-f1"', 'id="k-b2-f1"') + '\n</section>'
LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + SUF))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round i', '', 'Script `sync_20261107/apply_20261112i.py` (backups `*.before_20261112i`; numbers asserted against 381_stage13/reports/b2_f1team_report.md and b3_3_1_report.md). Autonomous changes only; H1/H2/H3 unchanged; Patchscope and 2-11b numbers not written. '
      'The Stage 10 §6.1 sentence is about the true-title readout LEVEL (−3.0 vs −4.4), which 3-1 does not report; it is kept and the 3-1 title-specific-signal range (J-lens +0.007 to +0.014 at L41–L46, logit ≈ 0, nearly equal at L47) is added beside it.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| i{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round i:', len(LOG))
