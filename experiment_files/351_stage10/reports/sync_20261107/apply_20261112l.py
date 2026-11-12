"""Round l (2026-11-12, LOCAL only). User rules 2026-11-12:
1) 2-11b (addendum 15): pre-registered verdict passes at all 7 layers -> NEW independent conclusion C24 (较稳但有前提), user wording + premises; not H3 evidence
   ("与 H3 的关系未预注册，只作讨论"); H1/H2/H3 statuses unchanged; "2-11b 结论待定" removed; L10 updated (2-11 stays stopped).
2) Patchscope 2-7/2-9: description only ("预注册要求报告、无判定规则"; recognition T − C and name_all x4tok block "探索性"); compact table in the report batch-2 section (-> handbook K).
3) Hypothesis tables unchanged (no "其他结论" row).
Also fixes a round-h duplicate: the name-position-probe update paragraph was inserted twice in the two walkthroughs (once before the Stage 8 premises paragraph) -> the misplaced copy removed.
Numbers asserted against 381_stage13/reports/b2_gennames_b_report.md, b2_gennames_b_robust_posthoc.md, b2_ps_report.md. Backups *.before_20261112l. K regenerated, handbook + process rebuilt. Manifest "round l"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'
READ = R / 'github/README_draft_20261106b.md'; T = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'stage13_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']}
K = R / 'methods/parts/K_post_defence.html'; CONC = W / 'conclusions_v30_draft.md'; HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, *T.values(), K, CONC]
SUF = '.before_20261112l'
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
gn = (R13 / 'reports/b2_gennames_b_report.md').read_text(encoding='utf-8'); ph = (R13 / 'reports/b2_gennames_b_robust_posthoc.md').read_text(encoding='utf-8')
ps = (R13 / 'reports/b2_ps_report.md').read_text(encoding='utf-8').splitlines()
for f in ['| L48 | 0.782 [0.754, 0.812] | 0.632 [0.599, 0.666] | 0.549 [0.509, 0.588] | +0.151 [+0.111, +0.190] | +0.234 [+0.186, +0.284] | yes |', '| 0.455 |', '| 0.510 |']: assert f in gn, f
assert gn.count('| yes |') >= 7
for f in ['0.548 [0.519, 0.576]', '+0.045 [+0.008, +0.081]', '+0.104 [+0.067, +0.139]']: assert f in ph, f
rows = {l.split('|')[1].strip(): [c.strip() for c in l.split('|')[2:9]] for l in ps[31:35]}
assert rows['title'][4].startswith('+0.068 [+0.056, +0.080]') and rows['colon'][5].startswith('+0.012 [+0.009, +0.015]') and rows['name_all'][4].startswith('+0.006 [+0.004, +0.008]') and rows['name_all'][5].startswith('+0.014 [+0.011, +0.017]'), rows
assert '+0.124 [+0.099, +0.148]' in ps[124]
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
C24 = ('Qwen3-32B 自己写作者名单时，名字写出之后，名字 token 上的中间层残差能线性区分真作者与编造的名字（补充 15 预注册主分析，名字 token 平均；L16–L56 七层都同时胜过排位基线和名字特征基线，'
       '例如 L48 AUROC 0.782 [0.754, 0.812]，probe − 排位 +0.151 [0.111, 0.190]，probe − 名字特征 +0.234 [0.186, 0.284]；打乱标签 0.455–0.510）；名字写出之前的位置读不出（次分析，AUROC 不高于排位基线）。')
C24P = ('前提：在 chat 模板下现场生成的文本上测得，不是其他实验用的原始提示；标签来自规则匹配（matcher v3b）；control 组只作描述（51 个真名）；“probe 信号可能部分来自输出置信度”这一替代解释尚未排除'
        '（生成时 token 对数概率 / 熵基线未做）；事后的名气基线（事后，探索性）：只用名气 0.548 [0.519, 0.576]，probe −（排位 + 名字特征 + 名气）在每层仍 > 0（L16 +0.045 [0.008, 0.081] … L48 +0.104 [0.067, 0.139]），'
        '名气只覆盖数据集内出现过的情况。补充 15 没有写它与 H3 的关系，不作为 H3 的证据；与 H3 的关系未预注册，只作讨论。')
C24L = 'C24 模型自己写出的名字：真作者与编造的名字可在名字 token 上线性区分（较稳但有前提；补充 15，批次 2 第 2-11b 项）：'
GSRC = '381_stage13/reports/b2_gennames_b_report.md；b2_gennames_b_robust_posthoc.md；团队整群 bootstrap 2,000 次'
PSZ = ('用名字位置作源时，第一作者在 L8–L16 约为 0，L40 +0.006 [0.004, 0.008]，L48 +0.014 [0.011, 0.017]（标题位置作源 L40 +0.068 [0.056, 0.080]）；“:” 位置作源到 L40 约为 0，L48 +0.012 [0.009, 0.015]；'
       'x4tok 标题位置作源、姓的第一个 token 在 L40 最高 +0.124 [0.099, 0.148]（以上为预注册要求报告、无判定规则；认得出的 target − control 与 name_all 源的 x4tok 部分为探索性）。不据此讨论 H3。')
PSL = 'Patchscope（批次 2 第 2-7、2-9 项，补充 12；只作描述）：'
PSRC = '381_stage13/reports/b2_ps_report.md'
def cell(s): return s.replace('*', '').replace('-', '−').strip()
PSTAB = ('<div class="tw"><table><thead><tr><th>源位置（第一作者，D = 自身 − 配对；预注册要求报告、无判定规则）</th><th>L8</th><th>L16</th><th>L40</th><th>L48</th><th>L56</th></tr></thead><tbody>'
         + ''.join(f'<tr><td>{n}</td>' + ''.join(f'<td>{cell(rows[k][i])}</td>' for i in (0, 1, 4, 5, 6)) + '</tr>' for k, n in [('title', '标题最后一个 token'), ('colon', '“:”'), ('name_all', '名字位置（全部）'), ('name_first_author', '名字位置（第一作者的名字）')])
         + f'</tbody></table></div><p class="note">来源：{PSRC} 第 32–35 行（团队整群 95% CI）。</p>')
C24E = ('C24 (fairly solid, with premises; addendum 15, 2-11b): when Qwen3-32B writes the author list itself, the middle-layer residuals on the written name tokens linearly separate true from invented names '
        '(pre-registered primary, name-token mean; all seven layers L16–L56 beat both the position and the name-string baselines, e.g. L48 AUROC 0.782 [0.754, 0.812], probe − position +0.151 [0.111, 0.190], '
        'probe − string +0.234 [0.186, 0.284]; shuffled labels 0.455–0.510); positions before the name is written do not (secondary, AUROC not above the position baseline). Premises: chat-template generation, '
        'not the raw prompt of the other experiments; labels by rule matching (matcher v3b); control group descriptive only (51 true names); output confidence not yet excluded (no generation log-prob / entropy baseline); '
        'post-hoc fame baseline (exploratory): fame alone 0.548 [0.519, 0.576], probe − (position + string + fame) still > 0 at every layer (L16 +0.045 [0.008, 0.081] … L48 +0.104 [0.067, 0.139]), fame covers only in-dataset presence. '
        'Addendum 15 states no relation to H3, so it is not H3 evidence (discussion only)')
PSE = ('Patchscope (2-7, 2-9; descriptive only): from the name-position source the first author is ≈ 0 at L8–L16, +0.006 [0.004, 0.008] at L40, +0.014 [0.011, 0.017] at L48 (title source +0.068 [0.056, 0.080] at L40); '
       'the ":" source is ≈ 0 up to L40, +0.012 [0.009, 0.015] at L48; x4tok title source, surname first token peaks at L40 +0.124 [0.099, 0.148] (pre-registered to report, no decision rule; recognition target − control and the name_all x4tok block exploratory)')
# --- 0. round-h duplicate in the walkthroughs
for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh']:
    s = S[T[k]]; m = re.search(r'<p class="upd">2026-11-09：<b>名字位置 probe.*?</p>\n(?=<p class="upd">2026-11-08（报告第 30 版）：Stage 8 的结论)', s, flags=re.S)
    assert m and s.count('<p class="upd">2026-11-09：<b>名字位置 probe') == 2, k
    S[T[k]] = s[:m.start()] + s[m.end():]; LOG.append((f'talk_docs/{k}.html', '(duplicate name-position-probe paragraph before the Stage 8 premises)', '(removed)', 1))
# --- 1. status
R_('已完成，结论待定', '已完成：预注册判定在 7 层都成立（见 C24）', ZH, None)
R_('Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层', 'Patchscope（2-7、2-9）已完成，只作描述（见下），x4tok 已补全部层', ZH, None)
R_('Patchscope 已完成，结果待写入（描述性）', 'Patchscope 已完成（只作描述）', ZH, None)
R_('Patchscope 已完成，结果待写入', 'Patchscope 已完成（描述）', [('N', '81')], 1)
R_('done, conclusion pending;', 'done: pre-registered verdict passes at all 7 layers (C24);', [DECK, READ], 3)
R_('Patchscope (2-7, 2-9) done, results to be written (descriptive);', 'Patchscope (2-7, 2-9) done (descriptive only);', [DECK, READ], 2)
# --- 2. C24 + Patchscope items
GLI = f'<li id="pd-b2-gn"><b>{C24L}</b>{C24}{C24P}<span class="src">（{GSRC}）</span></li>\n<li id="pd-b2-ps"><b>{PSL}</b>{PSZ}<span class="src">（{PSRC}）</span>{PSTAB}</li>\n'
R_('<li id="pd-b2-f1">', GLI + '<li id="pd-b2-f1">', [REP], 1)
R_('批次 2 中 C / D 组补全已完成：C 的信号更大，但时间点与 A 相同（第五部分）。', '批次 2 中 C / D 组补全已完成：C 的信号更大，但时间点与 A 相同；2-11b 新增一条独立结论 C24：' + C24 + '与 H3 的关系未预注册，只作讨论（第五部分）。', [REP], 1)
BOX = f'<li><b>{C24L}</b>{C24}{C24P}<span style="color:#8a8f98;font-size:.8em">（{GSRC}）</span></li><li><b>{PSL}</b>{PSZ}<span style="color:#8a8f98;font-size:.8em">（{PSRC}）</span></li>'
R_('<li><b>F1 对半拆分（批次 2 第 2-2 项', BOX + '<li><b>F1 对半拆分（批次 2 第 2-2 项', [ADV, AUD, ADD], 3)
R_('\n- **F1 对半拆分（批次 2 第 2-2 项', f'\n- **{C24L}**{C24}{C24P}【{GSRC}】\n- **{PSL}**{PSZ}【{PSRC}】\n- **F1 对半拆分（批次 2 第 2-2 项', [PROCMD], 1)
UPD = f'<p class="upd">2026-11-12：<b>{C24L}</b>{C24}{C24P}<span class="src">（{GSRC}）</span><b>{PSL}</b>{PSZ}<span class="src">（{PSRC}）</span></p>\n'
R_('<p class="upd">2026-11-09：<b>名字位置 probe', UPD + '<p class="upd">2026-11-09：<b>名字位置 probe', [T['experiment_walkthrough_zh'], T['experiment_walkthrough_methods_zh'], T['methods_handbook_guide_plain_zh']], 3)
R_('<li><b>名字位置 probe（批次 2 第 2-5 项', f'<li><b>{C24L}</b>{C24}{C24P}<span class="src">（{GSRC}）</span></li>\n<li><b>{PSL}</b>{PSZ}<span class="src">（{PSRC}）</span></li>\n<li><b>名字位置 probe（批次 2 第 2-5 项', [T['progress_report_for_advisor_zh']], 1)
S13 = T['stage13_script_zh_en']
R_('<b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>', f'<b>{C24L}</b>{C24}{C24P}<span class="src">（{GSRC}）</span><b>{PSL}</b>{PSZ}<span class="src">（{PSRC}）</span><b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>', [S13], 1)
R_('Name-position probe (addendum 11 A), done: ', C24E + '<span class="src">(b2_gennames_b_report.md; b2_gennames_b_robust_posthoc.md)</span>. ' + PSE + '<span class="src">(b2_ps_report.md)</span>. Name-position probe (addendum 11 A), done: ', [S13], 1)
# deck: note 75 (short) carries the full texts; slide 81 status above
NJ['75']['text'] = NJ['75']['text'].rstrip() + ' 2026-11-12：' + C24L + C24 + C24P.replace('（生成时 token 对数概率 / 熵基线未做）', '') + '〔b2_gennames_b_report.md〕' + PSL + PSZ + '〔b2_ps_report.md〕'
LOG.append(('notes_zh.json #75', '(append)', 'C24 + Patchscope', 1))
# README
R_('**Latest (2026-11-09).**', '**Latest (2026-11-12).** ' + C24E + ' <sub>(b2_gennames_b_report.md; b2_gennames_b_robust_posthoc.md)</sub>. ' + PSE + ' <sub>(b2_ps_report.md)</sub>.\n\n**Latest (2026-11-09).**', [READ], 1)
# conclusions draft
c = S[CONC]
add = ('\n### C24 模型自己写出的名字：真作者与编造的名字可在名字 token 上线性区分（2-11b，补充 15）\n\n- **结论**（用户 2026-11-12 确认的措辞）：' + C24 + '\n- **前提**：' + C24P[3:] +
       '\n- **出处**：`R13/reports/b2_gennames_b_report.md` 第 26–36（主分析）、38–48 行（次分析）；`R13/reports/b2_gennames_b_robust_posthoc.md` 第 11–17 行。\n- **相对 v29**：新增（用户 2026-11-12 决定：预注册判定在 7 层都成立，作为独立结论）。\n- 〔前提：只在 chat 模板下现场生成；样本不完整（target 论文，518 / 3,388 名）；事后改判据（名气基线为事后）〕\n')
i = c.index('\n---\n\n## 三、未定'); c = c[:i] + '\n' + add + c[i:]
for a, b in [('- **2-11b**（现场生成名字，补充 15 已锁定）：已完成，结论待定。', '- **2-11b**：已完成，见 C24。'),
             ('- 2-7、2-9（Patchscope）：已完成，结果待写入（描述性）；x4tok 已补全部层。', '- 2-7、2-9（Patchscope）：已完成，只作描述（预注册要求报告、无判定规则；认得出的 target − control 与 name_all 源 x4tok 为探索性）：' + PSZ + '；x4tok 已补全部层。'),
             ('### L10 2-11 已停止；2-11b 只跑第 0 片', '### L10 2-11 已停止；2-11b 已完成（C24）'),
             ('| C22 | 未定 | H3 |', '| C24 | 较稳 | — | 独立结论 | 与 H3 的关系未预注册，只作讨论 |\n| C22 | 未定 | H3 |')]:
    assert c.count(a) == 1, a[:50]; c = c.replace(a, b); LOG.append(('~/jlens_work/conclusions_v30_draft.md', a, b, 1))
S[CONC] = c; LOG.append(('~/jlens_work/conclusions_v30_draft.md', '(new section)', 'C24', 1))
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
md = ['', '## round l', '', 'Script `sync_20261107/apply_20261112l.py` (backups `*.before_20261112l`; numbers asserted against b2_gennames_b_report.md, b2_gennames_b_robust_posthoc.md, b2_ps_report.md). New conclusion C24 (user 2026-11-12); Patchscope descriptive only; H1/H2/H3 and hypothesis tables unchanged.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| l{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round l:', len(LOG))
