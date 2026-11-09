"""Round g (2026-11-09, LOCAL only): batch-2 results approved by the user (review_queue.md "第二批结果（2026-11-09，待审阅）" B2-1..B2-7):
2-4 batch rounding noise as a premise (C08 L56, C04, C02, L02); 2-8 E1t five titles (published values stand) + exploratory T − C sentence (denominator effect);
2-3 X3 by token role (C14 unchanged; "cannot split by role" limitation removed); 2-10 M3 all-token behaviour score in U46 (not H2 evidence; C06 unchanged);
status (2-3/2-4/2-8/2-10 done; ps, np final analysis running; 2-1 gate re-run; 2-11b 47 shards running); conclusions_v30_draft.md. Numbers asserted against the item reports.
Backups *.before_20261109g (stage13_script_zh_en: .before_20261109g2). K regenerated, handbook + process rebuilt; manifest section "round g"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'
READ = R / 'github/README_draft_20261106b.md'; T = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'stage13_script_zh_en', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']}
P = R / 'methods/parts'; B2, D11, F13, G, K = [P / f'{x}.html' for x in ['B_global2', 'D_stage10_11', 'F_stage13', 'G_appendix', 'K_post_defence']]; CONC = W / 'conclusions_v30_draft.md'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, *T.values(), B2, D11, F13, G, K, CONC]
def bk(p): return Path(str(p) + ('.before_20261109g2' if p == T['stage13_script_zh_en'] else '.before_20261109g'))
for p in EDIT + [HB, PROCH]: assert not bk(p).exists(), p
# --- source checks
rd = lambda f: (R13 / 'reports' / f).read_text(encoding='utf-8')
nz, e5, nd, x3, m3 = rd('b2_e1noise.md'), rd('b2_e1t5.md'), rd('b2_e1t5_numden.md'), rd('b2_x3role.md'), rd('b2_m3tok.md')
for f, s in [('+0.0148', nz), ('+0.136 [+0.125, +0.147]', e5), ('+0.134', e5), ('+0.067', e5), ('+0.026', e5), ('+0.0187 [+0.0108, +0.0269]', nd), ('+0.0215 [+0.0141, +0.0296]', nd),
             ('+0.0037 [+0.0025, +0.0050]', nd), ('+0.2114 [+0.1859, +0.2353]', nd), ('+0.4258', nd), ('+0.2144', nd), ('-0.035 [-0.060, -0.011]', nd),
             ('0.851', x3), ('0.900', x3), ('0.806', x3), ('0.924', x3), ('+0.2342 | [+0.2153, +0.2524]', m3), ('+0.3617', m3), ('+0.0283', m3), ('+0.1470', m3), ('+0.2251', m3), ('+0.2713', m3)]:
    assert f in s, f
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
ZH = [REP, ADV, PROCMD, AUD, ADD, *T.values(), CONC] + NK
NOISE = '批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md'
# 1. noise premise
R_('个别层差异极小，不作解释', '个别层差异极小，不作解释（小于' + NOISE + '）', ZH, None)
R_('两版所有“5 个假标题平均 − false_0”的区间都含 0', '两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148）', ZH, None)
R_('属于事后修改。', '属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。', ZH, None)
R_('这一时间对 5 个假标题都成立<span class="src">（Stage 13 X6', '这一时间对 5 个假标题都成立（5 个标题之间 L52 的差别在批量舍入噪声的量级内：组级最大 0.0148，补充 12 第 2-4 项）<span class="src">（Stage 13 X6', [REP], 1)
# 2. E1t five titles
E1T = ('E1t 用 5 个假标题（补充 12 第 2-8 项，已完成）：5 个假标题平均与 false_0 版一致——全部论文 L24 +0.136 [+0.125, +0.147]（false_0 版 +0.142）、L40 +0.134（+0.139）、L48 +0.067（+0.069）、'
       'L52 +0.026（+0.027），各层 mean5 − false_0 的区间都含 0，已发表值不变。恢复比例 target − control 为负，来自分母效应（target 的分子更高，但分母约为 control 的两倍；探索性）：'
       '分母 T − C +0.211 [+0.186, +0.235]（target 0.426、control 0.214）；分子 T − C L24 +0.0187 [+0.0108, +0.0269]、L40 +0.0215 [+0.0141, +0.0296]、L52 +0.0037 [+0.0025, +0.0050]；'
       '比例 T − C L24 −0.035 [−0.060, −0.011]（团队区间；381_stage13/reports/b2_e1t5.md、b2_e1t5_numden.md；summary_b2B/e1t5_numden_tc.csv）。')
R_('：标题最后一个 token 本身携带的信息很少。</p>', '：标题最后一个 token 本身携带的信息很少。' + E1T + '</p>', [REP], 1)
R_('target 与 control 形状相同（control 略高，例如 L24 0.175 vs 0.125）。', 'target 与 control 形状相同（control 略高，例如 L24 0.175 vs 0.125）。2026-11-09 补：' + E1T, [D11], 1)
# 3. X3 by role
X3R = ('X3 行为按 token 角色拆开后（补充 12 第 2-3 项，全部作者，测试集），恢复比在 0.806–0.924 之间（首字母 0.851 [0.723, 0.978]，姓的第一个 token 0.900 [0.863, 0.935]），'
       '各角色、各分层 target − control 的区间都含 0；与全部 token 的结果（0.897 [0.868, 0.926]）一致，C14 不变（381_stage13/reports/b2_x3role.md）')
R_('② 补充 5 要求“按 token 角色”报告，但 para_run 只存了每个名字的平均分，无法按角色拆分。', '② 补充 5 要求“按 token 角色”报告；原 para_run 只存了每个名字的平均分，已由补充 12 第 2-3 项用逐 token 打分补做：' + X3R + '。', [REP], 1)
R_('① 补充 4/5 要求所有 X3 结果也按 token 角色报告，但 para_run 只存了每个名字的平均分，<b>做不到</b>；', '① 补充 4/5 要求所有 X3 结果也按 token 角色报告，但 para_run 只存了每个名字的平均分，<b>做不到</b>（2026-11-09：已由补充 12 第 2-3 项补做；' + X3R + '）；', [F13], 1)
R_('偏离：按 token 角色报告做不到（para_run 只存每个名字的平均分）；', '偏离：按 token 角色报告做不到（para_run 只存每个名字的平均分；2026-11-09 已由补充 12 第 2-3 项补做，C14 不变）；', [B2], 1)
R_('<td><span class="st st-plan">计划未做</span>（做不到）</td><td>para_run 只存了每个名字的平均分，没有逐 token 分数，无法按角色拆分；不补跑。',
   '<td><span class="st st-done">已完成（2026-11-09，补充 12 第 2-3 项）</span></td><td>原 para_run 只存了每个名字的平均分；已用批次 1 全部作者的逐 token 打分补做：' + X3R + '。', [G], 1)
R_('按 token 角色报告做不到（V51）', '按 token 角色报告做不到（V51；2026-11-09 已由补充 12 第 2-3 项补做，C14 不变）', [PROCMD], 1)
R_('V51 X3 按 token 角色；', 'V51 X3 按 token 角色（2026-11-09 已完成）；', [PROCMD], 1)
R_('<b>X3 by token role</b> (V51)', '<b>X3 by token role</b> (V51; 2026-11-09: done in addendum 12 item 2-3, all roles 0.806–0.924, target − control includes 0, C14 unchanged; b2_x3role.md)', [AUD], 1)
# 4. M3 all-token behaviour score (U46)
M3T = ('2026-11-09 补（补充 12 第 2-10 项）：对全部作者的全部名字 token 打分，引用档内 target − control 为 +0.234 [+0.215, +0.252]（团队区间，10 档），姓的第一个 token +0.362，首字母 +0.028；'
       '只看第一作者首 token 的已发表值为 +0.147 [+0.096, +0.191]；调参集、测试集两半都为正（+0.225 [+0.177, +0.273]、+0.271 [+0.225, +0.319]）（381_stage13/reports/b2_m3tok.md）。'
       '这是输出层行为分数，不是分层表征指标，不作为 H2 证据；C06 不变。')
R_('作者差与分组的定义（认得出作者名单）有关，只是描述。', '作者差与分组的定义（认得出作者名单）有关，只是描述。' + M3T, [REP], 1)
# 5. status
R_('只跑第 0 个分片，排队中', '第 0 片已完成，其余 47 片运行中', ZH, None)
R_('名字位置 probe 等其余各项进行中，没有可报告的结果', 'X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；'
   '2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中', ZH, None)
R_('改为 2-11b（补充 15），只跑第 0 个分片；其余各项进行中；', '改为 2-11b（补充 15），第 0 片已完成，其余 47 片运行中；2-3、2-4、2-8、2-10 已完成；Patchscope 和名字位置 probe 的最终分析进行中；2-1 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中；', [T['progress_report_for_advisor_zh']], 1)
EN_ST = ('2-11b (addendum 15): shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis running; '
         '2-1 gate re-run (job killed by the cluster epilog, watchdog added); other items in progress;')
R_('2-11b (addendum 15), shard 0 only, queued; other items in progress;', EN_ST, [DECK, READ], 2)
R_('2-11 stopped → 2-11b shard 0 queued; other items in progress', '2-11 stopped → 2-11b: 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope and name-position probe: final analysis running; 2-1 gate re-run', [READ], 1)
# 6. conclusions draft
R_('全部 token 版 2-10 进行中〕', '全部 token 版 2-10 已完成：+0.234 [+0.215, +0.252]，姓的第一个 token +0.362，首字母 +0.028（`R13/reports/b2_m3tok.md`），是输出层行为分数，不是分层表征指标，不作为 H2 证据，C06 不变〕', [CONC], 1)
R_('  - M3 行为分数只有第一作者的第一个 token（2-10 进行中）。', '  - （M3 行为分数已由 2-10 补全部 token，不再属于此项；C06 的 T / I 指标不变。）', [CONC], 1)
R_('- 第二批其余项（2-1、2-2、2-3、2-4、2-7、2-8、2-9、2-10）：运行中，没有可报告的结果。',
   '- 2-3、2-4、2-8、2-10：已完成（2026-11-09，结果写进 C02、C04、C08、C14、L02、U46，见 RQ "第二批结果"）。\n- 2-7、2-9（Patchscope）和名字位置 probe：最终分析进行中。\n- 2-1：门槛重跑中（集群作业结束脚本误杀，已加看护作业）。2-2：进行中。', [CONC], 1)
R_('- **2-11b**（现场生成名字，补充 15 已锁定）：只跑第 0 个分片，GPU 作业 11736874 排队中；其余 47 片要另行决定（PG 2026-11-08 ~18:15 条）。', '- **2-11b**（现场生成名字，补充 15 已锁定）：第 0 片已完成，其余 47 片运行中。', [CONC], 1)
R_('- **名字位置 probe**（2-5，补充 11 A，主结果按 D11-1 第 2 版用逐个排除版）：GPU 单元还在跑。编排状态 np = rest（`R13/orch_b2/state.json`），2026-11-08 13:30 时为 240 / 432 个单元（RQ R3）。',
   '- **名字位置 probe**（2-5，补充 11 A，主结果按 D11-1 第 2 版用逐个排除版）：GPU 单元已齐，最终分析进行中。', [CONC], 1)
c14 = S[CONC].index('### C14'); i = S[CONC].index('- **相对 v29**：不变。', c14)
S[CONC] = S[CONC][:i] + '- **补充（2026-11-09，2-3）**：' + X3R + '。\n' + S[CONC][i:]; LOG.append(('~/jlens_work/conclusions_v30_draft.md', '(C14)', X3R, 1))
c02 = S[CONC].index('### C02'); i = S[CONC].index('- 〔前提：', c02)
S[CONC] = S[CONC][:i] + '- 〔前提（2026-11-09 补）：' + NOISE + '；X6 L52 的 0.984–1.017 在这个量级内〕\n' + S[CONC][i:]; LOG.append(('~/jlens_work/conclusions_v30_draft.md', '(C02)', NOISE, 1))
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
S[K] = S[K][:S[K].index(lead) + len(lead)] + makeK(S[REP]) + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, bk(p))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round g', '', 'Script `sync_20261107/apply_20261109g.py` (backups `*.before_20261109g`, stage13_script_zh_en `.before_20261109g2`; numbers asserted against 381_stage13/reports/b2_e1noise.md, b2_e1t5.md, b2_e1t5_numden.md, b2_x3role.md, b2_m3tok.md). No tier change; H2 status unchanged.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| g{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {c} |' for i, (f, o, n, c) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round g:', len(LOG))
