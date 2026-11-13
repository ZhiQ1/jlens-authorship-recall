"""Round q (2026-11-12, LOCAL only). 1) 2-1 status -> deviation D12-5 (381_stage13/config/prereg_addendum12_deviations_D12-5.json, sha256 68fa74cd…; b2_fitb_D12-1_outcome.md superseded):
gate reference in the wrong precision (f64 vs the fp32 log; not a relaxed criterion), gate fixed to fp32 vs fp32 and resumed, gate v4 queued.
2) Deck diagram slides: slide 62 X1 step 4 and R table -> all authors (b1_xall_report.md lines 61/63/64), old first-author values in the footnote; slide 63 X3 label -> all authors
(+0.229 [0.208, 0.250], b1_xall_report.md "X3 behaviour"), old +0.239 in the footnote; slide 64 X4 footnote: "first author by design". Notes 62 / 63 / 64 accordingly.
Other diagram slides checked: 16 (Stage 8 W, first author by design — in the "仍为首 token / 第一作者" list), 20 / 35 (worked examples of author 1), 24 (fixed in round n), 27 (P2 split by author position) — unchanged.
Backups *.before_20261112q. K regenerated, handbook + process rebuilt. Manifest "round q"."""
import json, re, shutil, subprocess, sys, hashlib
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable; W = Path.home() / 'jlens_work'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'
READ = R / 'github/README_draft_20261106b.md'; PRD = R / 'talk_docs/progress_report_for_advisor_zh.html'; K = R / 'methods/parts/K_post_defence.html'; CONC = W / 'conclusions_v30_draft.md'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, DECK, NOTES, ADV, PROCMD, AUD, ADD, READ, PRD, K, CONC]
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + '.before_20261112q').exists(), p
assert hashlib.sha256((R13 / 'config/prereg_addendum12_deviations_D12-5.json').read_bytes()).hexdigest().startswith('68fa74cd')
xa = (R13 / 'reports/b1_xall_report.md').read_text(encoding='utf-8').splitlines()
assert xa[60].startswith('| L24 | +0.996 / +0.990 / +0.992') and xa[62].startswith('| L40 | +0.933 / +0.928 / +0.929') and xa[63].startswith('| L48 | +0.455 / +0.431 / +0.444')
assert '| all | test | all | 552 | +0.897 [+0.868, +0.926] | +0.229 [+0.208, +0.250] |' in xa
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
ST = '2-1：出入记录 D12-5（gate 参照值用错精度：f64 对 fp32 日志；不是放宽判据），gate 已改为 fp32 对 fp32 并恢复运行，gate v4 排队中'
STE = '2-1: deviation D12-5 (gate reference computed in the wrong precision, f64 vs the fp32 log; not a relaxed criterion); gate fixed to fp32 vs fp32 and resumed, gate v4 queued'
# ---- 1. 2-1 status
R_('2-1 停止（D12-1，待用户定）', ST, [REP, ADV, PROCMD, AUD, ADD, PRD], 6)
R_('2-1 停止（D12-1，待定）', '2-1：出入记录 D12-5（gate 精度修正），gate v4 排队中', [('N', '81')], 1)
R_('Fit B（2-1）停止，待定', 'Fit B（2-1）：出入记录 D12-5（gate 参照值用错精度，已改为 fp32 对 fp32），gate v4 排队中', [ADV], 1)
R_('2-1 stopped (D12-1, user to decide);', STE + ';', [DECK, READ], 2)
R_('2-1 stopped (D12-1)', '2-1: D12-5, gate v4 queued', [READ], 1)
R_('- 2-1：停止（D12-1，待用户定）。', '- ' + ST + '（`R13/config/prereg_addendum12_deviations_D12-5.json`，sha256 68fa74cd…；`b2_fitb_D12-1_outcome.md` 已被取代）。', [CONC], 1)
R_('（2-1 停止，D12-1，待用户定）', '（2-1：出入记录 D12-5，gate 已改为 fp32 对 fp32 并恢复运行，gate v4 排队中）', [CONC], 1)
# ---- 2. deck diagram slides
def slide(label):
    m = re.search(r'<section class="slide mf" aria-label="' + re.escape(label) + r'">.*?</section>', S[DECK], flags=re.S); assert m, label; return m
m = slide('method: Changing the question'); x = m.group(0); y = x
assert y.count('>score first author<') == 1; y = y.replace('>score first author<', '>score all authors<')
i = y.index('>R from<'); head, tail = y[:i], y[i:]
OLD = ['0.99', '0.98', '0.99', '0.92', '0.92', '0.92', '0.42', '0.41', '0.42']; NEW = ['0.996', '0.990', '0.992', '0.933', '0.928', '0.929', '0.455', '0.431', '0.444']
it = iter(zip(OLD, NEW)); cnt = [0]
def sub(mm):
    try: o, nw = next(it)
    except StopIteration: return mm.group(0)
    assert mm.group(1) == o, (mm.group(1), o); cnt[0] += 1; return '>' + nw + '<'
tail = re.sub(r'>(0\.\d\d)<', sub, tail); assert cnt[0] == 9
y = head + tail
a = '>R: Stage 13 X1, test set 582 papers; 381_stage13/reports/x1_report.md<'; assert y.count(a) == 1
y = y.replace(a, '>R: Stage 13 X1, all authors (batch 1 item 1), test 582 papers; b1_xall_report.md (old first-author: 0.99 / 0.92 / 0.42)<')
S[DECK] = S[DECK].replace(x, y); LOG.append(('merged_deck/stage1_11_deck.html', 'slide 62: score first author; R table first author; footnote', 'score all authors; R table all authors (9 cells); footnote with old values', 11))
m = slide('method: Paraphrased title'); x = m.group(0); y = x
for a, b in [('>first-author score, paraphrase − D: +0.239<', '>all-author score, paraphrase − D: +0.229<'),
             ('>+0.239: Stage 13 X3 behaviour, test, 552 papers; x3_textbase_recovery.md<', '>+0.229: Stage 13 X3 behaviour, all authors (batch 1 item 1), test, 552 papers; b1_xall_report.md (old first-author: +0.239)<')]:
    assert y.count(a) == 1, a; y = y.replace(a, b)
S[DECK] = S[DECK].replace(x, y); LOG.append(('merged_deck/stage1_11_deck.html', 'slide 63: first-author score +0.239', 'all-author score +0.229 (old +0.239 in footnote)', 2))
m = slide('method: Patchscope'); x = m.group(0); y = x
a = '>D: Stage 13 X4, test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; 381_stage13/reports/x4_report.md<'; assert y.count(a) == 1
y = y.replace(a, '>D: Stage 13 X4 (prompt asks for the first author by design), test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; x4_report.md<')
S[DECK] = S[DECK].replace(x, y); LOG.append(('merged_deck/stage1_11_deck.html', 'slide 64 footnote', '+ "prompt asks for the first author by design"', 1))
R_('再给本篇第一作者打分：', '再给本篇全部作者打分（旧版只看第一作者）：', [('N', '62')], 1)
R_(r'第一作者分数改写 − D 为 \+0\.239(〔[^〕]*〕)', lambda mm: '全部作者分数改写 − D 为 +0.229 [0.208, 0.250]〔补充 10 第 1 项；381_stage13/reports/b1_xall_report.md “X3 behaviour” 表〕（旧版只看第一作者：+0.239' + mm.group(1) + '）', [('N', '63')], 1, regex=True)
R_('第一作者从 L8 起可以解码（+0.046）', '第一作者从 L8 起可以解码（+0.046；提示按设计问第一作者；全作者版本同样从 L8 起可解码，测试集 +0.048 [0.039, 0.058]）', [('N', '64')], 1)
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
kk = makeK(S[REP])
for z in ['np', 'f1', 'gn', 'ps']: kk = kk.replace(f'id="pd-b2-{z}"', f'id="k-b2-{z}"')
S[K] = S[K][:S[K].index(lead) + len(lead)] + kk + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + '.before_20261112q'))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round q', '', 'Script `sync_20261107/apply_20261112q.py` (backups `*.before_20261112q`). 2-1 -> D12-5 status; deck diagram slides 62/63/64 (other diagram slides checked: 16, 20, 24, 27, 35 unchanged, see docstring).', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| q{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round q:', len(LOG))
