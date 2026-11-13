"""Round o (2026-11-12, LOCAL only; user decisions on the round-n "需要用户拍板" items).
1) Title-position probe target − control: main = wording B v3 (for_user_2026-11-07.md §f, verbatim); old first-token "target 比 control 高 +0.03 到 +0.08" into
   "（旧版只打首 token：…）". Places: report §6.11 and the §6.11 controls sentence, notes (39-type and 73), walkthrough, walkthrough methods, Keys and shelves (zh + en), talk-doc progress report.
2) C15: main statement unchanged ("第一作者 L8 起可解码"); added right after it: the all-author version is also decodable from L8, +0.048 [0.039, 0.058].
   NOTE: b1_xall_report.md line 179 ("X4 author answer: D = self - partner (test)") and line 203 ("all | L8 (confirmed, test +0.048 [+0.039, +0.058])") show that the
   all-author version WAS tune-selected and confirmed on the test split, so the requested clause "该版本未做调参/测试拆分" would be wrong; written as "按调参集选层、测试集确认" instead (reported to the coordinator).
Backups *.before_20261112o. K regenerated, handbook + process rebuilt. Manifest "round o"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; READ = R / 'github/README_draft_20261106b.md'
T = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']}
F = R / 'methods/parts/F_stage13.html'; K = R / 'methods/parts/K_post_defence.html'; CONC = W / 'conclusions_v30_draft.md'; HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, READ, *T.values(), F, K, CONC]
SUF = '.before_20261112o'
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
fu = (W / 'for_user_2026-11-07.md').read_text(encoding='utf-8')
W3 = ('预注册版中名的第一个 token 在 L24–L48 为正，姓在 L24–L48 不显著（L40 +0.012 [−0.026, +0.048]）；事后的逐个排除版中姓从 L24 起为正（L40 +0.030 [0.013, 0.048]）。名的信号在三版中一致；姓的证据弱，只来自事后版本。'
      '首字母在个别层为正、模式不一致（未做多层校正），不作结论。')
assert W3[:W3.index('首字母')] in fu and '首字母在个别层为正、模式不一致（未做多层校正），不作结论。' in fu
W3E = ('in the pre-registered version the given-name first token is positive at L24–L48 and the surname is not significant at L24–L48 (L40 +0.012 [−0.026, +0.048]); in the post-hoc per-donor version '
       'the surname is positive from L24 (L40 +0.030 [0.013, 0.048]). The given-name signal is consistent across the three versions; the surname evidence is weak and comes only from the post-hoc version. '
       'The initial is positive at some layers with an inconsistent pattern (no multi-layer correction); no conclusion is drawn')
xa = (R13 / 'reports/b1_xall_report.md').read_text(encoding='utf-8').splitlines()
assert xa[172].startswith('## X4 author answer: D = self - partner (test)') and xa[178].startswith('| L8 | +0.048 [+0.039, +0.058]') and 'L8 (confirmed, test +0.048 [+0.039, +0.058])' in xa[202]
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; NJ = json.loads(S[NOTES]); LOG = []
def R_(old, new, files, n=None, regex=False):
    tot = 0
    for p in files:
        if isinstance(p, tuple): t = NJ[p[1]]['text']
        else: t = S[p]
        c = len(re.findall(old, t, flags=re.S)) if regex else t.count(old)
        if not c: continue
        t = re.sub(old, new, t, flags=re.S) if regex else t.replace(old, new); tot += c
        if isinstance(p, tuple): NJ[p[1]]['text'] = t
        else: S[p] = t
        LOG.append((('notes_zh.json #' + p[1]) if isinstance(p, tuple) else str(p).replace(str(R) + '/', ''), ('(regex) ' if regex else '') + old, new if isinstance(new, str) else '(computed)', c))
    assert tot >= 1 and (n is None or tot == n), (old[:70], tot, n)
NK = [('N', k) for k in NJ]
TCZ = 'target − control（同一引用档内，全部作者全部名字 token 按角色，措辞 B 第 3 版）：' + W3
# ---- 1. target − control
R_(r'；旧版（只打首 token）中目标组比对照组高 \+0\.03 到 \+0\.08（L24–L60，置信区间在 0 以上，L44 下界 \+0\.000 在边界上）(<span class="src">.*?</span>)',
   lambda m: '；' + TCZ + '（旧版只打首 token：目标组比对照组高 +0.03 到 +0.08（L24–L60，置信区间在 0 以上，L44 下界 +0.000 在边界上）' + m.group(1) + '）', [REP], 1, regex=True)
R_('，标题最后一个 token 上从 L24 起就有可被线性读出的、属于这篇论文的作者信息（目标组更多），只是现有 lens 读不出来。',
   '，标题最后一个 token 上从 L24 起就有可被线性读出的、属于这篇论文的作者信息，只是现有 lens 读不出来。' + TCZ + '（旧版只打首 token：目标组更多）', [REP], 1)
R_('，目标组更多，只是 lens 读不出来。', '，只是 lens 读不出来。' + TCZ + '（旧版只打首 token：目标组更多。）', NK, 1)
R_('和 probe 的结果（标题 token 上目标组有优势）', '和 probe 的结果（标题 token 上的 ' + TCZ + '旧版只打首 token 时目标组有优势）', NK, 1)
R_('从 L24 起 +0.05 到 +0.08，target 比 control 高 +0.03 到 +0.08。', '全部作者全部名字 token 按角色从 L16 起各角色都为正（L40 名首 token +0.124、姓首 token +0.071、首字母 +0.044）；' + TCZ + '（旧版只打首 token：从 L24 起 +0.05 到 +0.08，target 比 control 高 +0.03 到 +0.08。）',
   [T['experiment_walkthrough_zh'], T['keys_and_shelves_script_zh_en'], T['progress_report_for_advisor_zh']], 3)
R_('；target 比 control 高 +0.03 到 +0.08；两个置换对照', '；target 比 control 高 +0.03 到 +0.08（以上为旧版）。' + TCZ + '旧版的两个置换对照', [T['experiment_walkthrough_methods_zh']], 1)
R_('The probe reads +0.05 to +0.08 from L24 onward, and target exceeds control by +0.03 to +0.08;', 'With all name tokens of all authors by role every role is positive from L16 (L40: given-name first token +0.124, surname first token +0.071, initial +0.044); target − control (wording B v3): '
   + W3E + ' (old first-token version: +0.05 to +0.08 from L24 onward, target exceeds control by +0.03 to +0.08);', [T['keys_and_shelves_script_zh_en']], 1)
# ---- 2. C15 + all-author sentence
ADDZ = '全作者版本同样从 L8 起可解码（测试集 +0.048 [0.039, 0.058]，按调参集选层、测试集确认；381_stage13/reports/b1_xall_report.md 第 179、203 行）。'
ADDS = '（全作者版本同样从 L8 起可解码：测试集 +0.048 [0.039, 0.058]）'
ADDE = ' The all-author version is also decodable from L8 (test +0.048 [0.039, 0.058], tune-selected and confirmed on test; b1_xall_report.md lines 179, 203).'
R_('，而且很弱。也就是说，最早可解码的顺序是', '，而且很弱。' + ADDZ + '也就是说，最早可解码的顺序是', [REP], 1)
R_('(Stage 13 X4, test split, team CI; x4_report.md)</span>', '(Stage 13 X4, test split, team CI; x4_report.md)</span> (all authors also from L8: +0.048 [0.039, 0.058])', [DECK], 1)
R_(r'(第一作者从 L8 起可解码，D = \+0\.046〔[^〕]*〕)', lambda m: m.group(1) + ADDS, NK, 1, regex=True)
R_('第一作者 L8 起可解码（<span class="num">+0.046 [0.035, 0.059]</span>，主要在姓上）', '第一作者 L8 起可解码（<span class="num">+0.046 [0.035, 0.059]</span>，主要在姓上）' + ADDS, [ADV], 1)
R_('X4：第一作者 L8 起可解码（+0.046，主要在姓上 +0.066）', 'X4：第一作者 L8 起可解码（+0.046，主要在姓上 +0.066）' + ADDS, [PROCMD], 1)
R_('X4：第一作者 L8 起可解码，可能来自标题文字；', 'X4：第一作者 L8 起可解码' + ADDS + '，可能来自标题文字；', [PROCMD], 1)
R_('X4: first author decodable at L8 but possibly explained by the title text.', 'X4: first author decodable at L8 (the all-author version also from L8, test +0.048 [0.039, 0.058], tune-selected and confirmed on test) but possibly explained by the title text.', [READ], 1)
R_('第一作者 L8 就能解码出一点（+0.046）', '第一作者 L8 就能解码出一点（+0.046）' + ADDS, [T['experiment_walkthrough_zh']], 1)
R_('第一作者 L8 起可解码（+0.046）', '第一作者 L8 起可解码（+0.046）' + ADDS, [T['experiment_walkthrough_methods_zh']], 1)
R_('第一作者 L8 就能解码，年份要到 L40', '第一作者 L8 就能解码' + ADDS + '，年份要到 L40', [T['methods_handbook_guide_plain_zh']], 1)
R_('；但第一作者（L8）早于年份（L40），与 H2 预测的方向相反。', '；但第一作者（L8）早于年份（L40），与 H2 预测的方向相反。' + ADDZ, [F], 1)
R_('  - 第一作者 L8 +0.046 [0.035, 0.059]；', '  - 第一作者 L8 +0.046 [0.035, 0.059]；全作者版本同样从 L8 起可解码：测试集 +0.048 [0.039, 0.058]（调参集选层、测试集确认；`R13/reports/b1_xall_report.md` 第 179、203 行）；', [CONC], 1)
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
md = ['', '## round o', '', 'Script `sync_20261107/apply_20261112o.py` (backups `*.before_20261112o`). Target − control: wording B v3 main, old first-token in parentheses. C15: all-author sentence added; b1_xall_report.md lines 179/203 show the all-author X4 WAS tune/test-split (confirmed on test), so the requested "未做调参/测试拆分" was not written.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| o{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round o:', len(LOG))
