"""Round n (2026-11-12, LOCAL only). User rule: where an all-token / all-author version is done, it is the main number; the old first-token / first-author number goes
into "（旧版只打首 token：…）" / "（旧版只看第一作者：…）". Census: ~/jlens_work/review_queue.md "首 token / 第一作者主数字普查（2026-11-12）" (written before these edits).
Edits: deck slide 24 (diagram step 3 + labels + footnote; E4b scored every author's first token, not the first author) + note 24; report §6.11 title-position probe sentence
(zh + en) and notes 39 / 40 / 73, walkthroughs, advisor (addendum 9 by role, V0); X3 behaviour (all authors 0.897); M3 U46 (+0.234). Target − control claims NOT changed
(only labelled as the old version in §6.11) -> 需要用户拍板. New section "仍为首 token / 第一作者的分析" (report limits -> K, README, compact in advisor / audit / addendum / process).
Numbers asserted against e4b_alltok.md, b1_xall_report.md, b2_m3tok.md. Backups *.before_20261112n. K regenerated, handbook + process rebuilt. Manifest "round n"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'
READ = R / 'github/README_draft_20261106b.md'; WZ = R / 'talk_docs/experiment_walkthrough_zh.html'; WM = R / 'talk_docs/experiment_walkthrough_methods_zh.html'
G = R / 'methods/parts/G_appendix.html'; K = R / 'methods/parts/K_post_defence.html'; HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, WZ, WM, G, K]
SUF = '.before_20261112n'
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
at = (R13 / 'reports/e4b_alltok.md').read_text(encoding='utf-8')
for f in ['| given_first | +0.087* | +0.098* | +0.116* | +0.124* | +0.124* | +0.140* | +0.154* | +0.163* |', '| surname_first | +0.056* | +0.058* | +0.068* | +0.071* | +0.076* | +0.091* | +0.097* | +0.098* |',
          '| initial | +0.025* | +0.021* | +0.026* | +0.044* | +0.035* | +0.030* | +0.048* | +0.054* |']: assert f in at, f
xa = (R13 / 'reports/b1_xall_report.md').read_text(encoding='utf-8'); m3 = (R13 / 'reports/b2_m3tok.md').read_text(encoding='utf-8')
for f in ['0.897', '0.868', '0.926', '-0.007', '-0.075', '+0.059']: assert f in xa, f
assert '+0.2342 | [+0.2153, +0.2524]' in m3
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
ROLE = '全部作者、全部名字 token、按角色（补充 9，预注册版 V0，只减 false_0）L24 / L40 / L56：名的第一个 token +0.098 / +0.124 / +0.163，姓的第一个 token +0.058 / +0.071 / +0.098，首字母 +0.021 / +0.044 / +0.054'
ROLE_S = '全部作者全部名字 token 按角色（补充 9，预注册版 V0）：L40 名首 token +0.124、姓首 token +0.071、首字母 +0.044'
ROLE_E = 'all authors, all name tokens by role (addendum 9, pre-registered V0) at L24 / L40 / L56: given-name first token +0.098 / +0.124 / +0.163, surname first token +0.058 / +0.071 / +0.098, initial +0.021 / +0.044 / +0.054'
# ---- 1. E4b / addendum 9
R_('已复核</span>：L24 约 +0.05，L40 约 +0.06，L56 约 +0.08（+0.050 / +0.061 / +0.075）', '已复核</span>：' + ROLE + '<span class="src">（381_stage13/reports/e4b_alltok.md Summary matrix）</span>（旧版只打首 token：L24 约 +0.05，L40 约 +0.06，L56 约 +0.08（+0.050 / +0.061 / +0.075））', [REP], 1)
R_('；目标组比对照组高 +0.03 到 +0.08（L24–L60', '；旧版（只打首 token）中目标组比对照组高 +0.03 到 +0.08（L24–L60', [REP], 1)
R_('about +0.05 at L24, +0.06 at L40 and +0.08 at L56 (+0.050 / +0.061 / +0.075)', ROLE_E + ' (old first-token version: about +0.05 at L24, +0.06 at L40 and +0.08 at L56, +0.050 / +0.061 / +0.075)', [REP], 1)
R_('L24 约 0.05，到 L56 升到约 0.08〔', ROLE.replace('L24 / L40 / L56', 'L24 / L40 / L56 的标题特异信号') + '〔e4b_alltok.md〕（旧版只打首 token：L24 约 0.05，到 L56 约 0.08）〔', [('N', '39')], 1)
R_('复核后为 +0.05 到 +0.08〔', '复核后为 +0.05 到 +0.08（旧版只打首 token）；全部作者全部名字 token 按角色（补充 9）各层都为正，L40 名首 token +0.124、姓首 token +0.071、首字母 +0.044〔e4b_alltok.md〕〔', [('N', '40')], 1)
R_('复核：+0.05 到 +0.08〔', '复核：' + ROLE_S + '〔e4b_alltok.md〕（旧版只打首 token：+0.05 到 +0.08）〔', [('N', '73')], 1)
R_('E4b 信号只用其中 target + control 的 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075。', 'E4b 信号只用其中 target + control 的 1,395 篇。' + ROLE + '（旧版只打首 token：L24 +0.050、L40 +0.061、L56 +0.075）。', [WZ], 1)
R_('<strong>结果</strong>：L24 +0.050，L40 +0.061，L56 +0.075（E4b', '<strong>结果</strong>：' + ROLE + '。旧版只打首 token：L24 +0.050，L40 +0.061，L56 +0.075（E4b', [WM], 1)
R_('（L24 <span class="num">+0.050</span>、L40 <span class="num">+0.061</span>、L56 <span class="num">+0.075</span>，换成随机论文的作者后约为 0；', '（' + ROLE_S + '；旧版只打首 token：L24 <span class="num">+0.050</span>、L40 <span class="num">+0.061</span>、L56 <span class="num">+0.075</span>，换成随机论文的作者后约为 0；', [ADV], 1)
# deck slide 24 (SVG text) + note 24
s24 = re.findall(r'<section class="slide mf" aria-label="method: Probe">.*?</section>', S[DECK], flags=re.S); assert len(s24) == 1; o = s24[0]; nw = o
for a, b, n in [('>first author<', '>all authors<', 2), ('>first author, L40<', '>surname 1st token, L40<', 1), ('>+0.061<', '>+0.071<', 1),
                ('>probe score = log10(1/rank) of the true first-author token<', '>probe score = log10(1/rank) of the true name tokens (every author, by role)<', 1),
                ('>+0.061: Stage 13 E4b re-check, probe scores ONLY THE FIRST NAME TOKEN, target + control (1,395), team folds, title reuse dropped; e4b_trainstd_compare.md<',
                 '>+0.071: addendum 9, all authors, all name tokens by role (surname first token), pre-registered V0, 1,395 papers, team folds, title reuse dropped (old first-token version: +0.061); e4b_alltok.md<', 1)]:
    assert nw.count(a) == n, (a, nw.count(a)); nw = nw.replace(a, b)
S[DECK] = S[DECK].replace(o, nw); LOG.append(('merged_deck/stage1_11_deck.html', 'slide 24 diagram: first author / +0.061 / footnote', 'all authors / surname 1st token +0.071 / addendum-9 footnote (old +0.061)', 6))
R_('预测第一作者的首个 token 或年份。标题特异分数 spec = 真标题的探针分 − 假标题的探针分，L40 为 +0.061 [0.047, 0.076]〔Stage 13 E4b 复核，标题最后一个 token 上的 probe，probe 只打分第一作者名字的第一个 token，',
   '预测每位作者名字的 token（按角色）或年份。标题特异分数 spec = 真标题的探针分 − 假标题的探针分，全部作者全部名字 token 按角色（补充 9，预注册版 V0）L40 姓的第一个 token +0.071 [0.058, 0.085]、名的第一个 token +0.124 [0.108, 0.142]、首字母 +0.044 [0.030, 0.057]〔e4b_alltok.md〕'
   '（旧版只打首 token：L40 +0.061 [0.047, 0.076]〔Stage 13 E4b 复核，标题最后一个 token 上的 probe，probe 只打分每位作者名字的第一个 token，', [('N', '24')], 1)
R_('Confirmatory 表 L40 行 new 列〕。年份的 R²', 'Confirmatory 表 L40 行 new 列〕）。年份的 R²', [('N', '24')], 1)
# ---- 2. X3 behaviour
R_('全部 0.90 [0.86, 0.94]，target 0.90 [0.85, 0.94]，control 0.91 [0.84, 0.98]，两组之差 −0.01 [−0.09, +0.07]',
   '全部作者、全部名字 token 0.897 [0.868, 0.926]，target − control −0.007 [−0.075, +0.059]（补充 10 第 1 项；381_stage13/reports/b1_xall_report.md）（旧版只看第一作者：全部 0.90 [0.86, 0.94]，target 0.90 [0.85, 0.94]，control 0.91 [0.84, 0.98]，两组之差 −0.01 [−0.09, +0.07]）', [REP], 1)
R_('约 90%<span class="src">（Stage 13 X3 行为恢复比例 0.90 [0.86, 0.94]，测试集 552 篇；', '约 90%<span class="src">（Stage 13 X3 行为恢复比例，全部作者全部 token 0.897 [0.868, 0.926]（b1_xall_report.md）；旧版只看第一作者：0.90 [0.86, 0.94]，测试集 552 篇；', [REP], 1)
R_('behaviour keeps ≈ 90% of the first-author preference<span class="src">(same, 0.90 [0.86, 0.94])</span>', 'behaviour keeps ≈ 90% of the author preference<span class="src">(all authors, all tokens 0.897 [0.868, 0.926]; old first-author version 0.90 [0.86, 0.94])</span>', [DECK], 1)
R_('行为上保留约 90% 的第一作者偏好〔同上，教师强制打分，0.90 [0.86, 0.94]〕', '行为上保留约 90% 的作者偏好〔全部作者全部 token 0.897 [0.868, 0.926]，补充 10 第 1 项；旧版只看第一作者：0.90 [0.86, 0.94]〕', [('N', '70')], 1)
R_('行为上保留约 90% 的第一作者偏好（0.90 [0.86, 0.94]）', '行为上保留约 90% 的作者偏好（全部作者全部 token 0.897 [0.868, 0.926]；旧版只看第一作者：0.90 [0.86, 0.94]）', [G], 1)
# ---- 3. M3 behaviour score
R_('，第一作者首 token +0.147 [+0.096, +0.191]<span class="src">（同上，第一作者首 token 分数；m3_scores.md 第 3 节）</span>',
   '，全部作者全部名字 token +0.234 [+0.215, +0.252]<span class="src">（补充 12 第 2-10 项；381_stage13/reports/b2_m3tok.md）</span>（旧版只看第一作者首 token：+0.147 [+0.096, +0.191]<span class="src">（m3_scores.md 第 3 节）</span>）', [REP], 1)
R_('first-author first token +0.147 [0.096, 0.191]<span class="src">(output', 'all authors, all name tokens +0.234 [0.215, 0.252] (2-10; old first-author first-token version +0.147 [0.096, 0.191])<span class="src">(output', [DECK], 1)
R_('第一作者首 token +0.147〔同上，[0.096, 0.191]〕', '全部作者全部名字 token +0.234〔补充 12 第 2-10 项，[0.215, 0.252]；b2_m3tok.md〕（旧版只看第一作者首 token：+0.147〔[0.096, 0.191]〕）', NK := [('N', k) for k in NJ], 1)
# ---- 4. "仍为首 token / 第一作者的分析"
STILL = [('Stage 4–8（含 Stage 8 的 W）', '存储的数据只有候选名字第一个 token 的 logit；GPU 重做即 3-4 / 3-5，用户 2026-11-06 决定不做；C-1 / C-2 是全部作者的代理，指标不同，不能替代'),
         ('X4 认得出对比、x4tok、2-7 Patchscope', '提示按设计问第一作者；全部作者版是新实验，没有计划'),
         ('Stage 11 E4 lens', '只有第一个 token 和姓的第一个 token；全部 token 需要 GPU，审计建议不重做'),
         ('E4b 的 X1 对照流程（1,863 篇）', '只打首 token，没有计划')]
STILL_LI = '<li><b>仍为首 token / 第一作者的分析（2026-11-12）。</b>' + '；'.join(f'{a}：{b}' for a, b in STILL) + '。</li>\n'
i = S[REP].index('<section id="pd-limits">'); j = S[REP].index('</ul>', i)
S[REP] = S[REP][:j] + STILL_LI + S[REP][j:]; LOG.append(('stage1_11/stage1_11_report.html', '(pd-limits list end)', STILL_LI.strip()[:150], 1))
BOXL = '<li><b>仍为首 token / 第一作者的分析（2026-11-12）：</b>' + '；'.join(f'{a}（{b}）' for a, b in STILL) + '。</li>'
R_('<li><b>2026-11-08（报告第 30 版）补充的局限：</b>', BOXL + '<li><b>2026-11-08（报告第 30 版）补充的局限：</b>', [ADV, AUD, ADD], 3)
R_('\n- **2026-11-08（报告第 30 版）补充的局限：**', '\n- **仍为首 token / 第一作者的分析（2026-11-12）：**' + '；'.join(f'{a}（{b}）' for a, b in STILL) + '。\n- **2026-11-08（报告第 30 版）补充的局限：**', [PROCMD], 1)
STILL_E = ('Analyses still on the first token / first author (2026-11-12): Stages 4–8 incl. the Stage 8 W (stored data hold only the candidates’ first-token logits; the GPU redo = 3-4 / 3-5, not done by user decision 2026-11-06; '
           'C-1 / C-2 are all-author proxies with a different metric, not replacements); X4 recognition, x4tok and 2-7 Patchscope (the prompt asks for the first author by design; an all-author version would be a new experiment, not planned); '
           'Stage 11 E4 lens (first token and surname first token only; all tokens need GPU, the audit recommended not to redo); E4b X1-controls pipeline, 1,863 papers (first token only, no plan).')
R_('- Cannot be redone: one model; teacher forcing; label pipeline not on the cluster; the 4097+ citation bin has no B / D papers.', '- Cannot be redone: one model; teacher forcing; label pipeline not on the cluster; the 4097+ citation bin has no B / D papers. ' + STILL_E, [READ], 1)
# write
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
kk = makeK(S[REP])
for x in ['np', 'f1', 'gn', 'ps']: kk = kk.replace(f'id="pd-b2-{x}"', f'id="k-b2-{x}"')
S[K] = S[K][:S[K].index(lead) + len(lead)] + kk + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + SUF))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round n', '', 'Script `sync_20261107/apply_20261112n.py` (backups `*.before_20261112n`; census + 需要用户拍板 in ~/jlens_work/review_queue.md "首 token / 第一作者主数字普查（2026-11-12）"; numbers asserted against e4b_alltok.md, b1_xall_report.md, b2_m3tok.md). Target − control claims and C15 (X4 first author) not changed.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| n{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round n:', len(LOG))
