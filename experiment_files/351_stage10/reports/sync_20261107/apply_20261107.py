"""2026-11-07 (user decisions ~01:30): apply the strict-check fixes to ALL current local documents.
 1  five real mismatches (S10 L63 CI, #ov n, E4b trainstd range max, R0 CI, report section 1 old E4b values)
 2  all 108 '写法不统一' -> canonical form of the check table (claims_check.csv of the given out_ dir)
 3  report conclusions without data: verified sources added (or the sentence weakened) -> numcheck/claims/no_data_fixes_20261107.md
 A  Stage 8 endpoint wording unified;  B  NOT applied (initial-token target - control CI contains 0 at L40: see report);  C  deck slide 64 English table image
Backups *.before_20261107.* (always the input -> idempotent). Writes unify_summary_20261107.md and no_data_fixes_20261107.md.
Usage: python apply_20261107.py OUT_DIR_OF_CHECK"""
import json, re, shutil, sys, base64, collections
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; NC = R / 'numcheck/claims'
CHK = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(NC.glob('out_*'))[-1]

# ------------------------------------------------------------------ targets (editable sources)
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
PARTS = sorted(p for p in (R / 'methods/parts').glob('*.html') if '.before_' not in p.name and p.name != 'K_post_defence.html')
TALK = sorted(p for p in (R / 'talk_docs').glob('*.html') if '.before_' not in p.name)
ADV = R / 'advisor/index.html'; PROC = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'
ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'
PLAN_MD = R / 'plan/plan_master_queue_20261106b.md'; PLAN_HTML = R / 'plan/plan_master_queue_20261106b.html'
TEXT_FILES = [REP, DECK, *PARTS, *TALK, ADV, PROC, AUD, ADD, READ, PLAN_MD, PLAN_HTML]
def bkp(p):
    b = p.with_name(p.stem + '.before_20261107' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b
S = {p: bkp(p).read_text(encoding='utf-8') for p in TEXT_FILES}
NJ = json.loads(bkp(NOTES).read_text(encoding='utf-8'))
LOG = []                     # (kind, claim, doc_file, old, new, where)

def target_files(check_file):
    f = str(check_file)
    if f.endswith('methods_handbook.html'): return PARTS
    if f.endswith('process_report/index.html'): return [PROC]
    if f.endswith('plan_master_queue_20261106b.md'): return [PLAN_MD, PLAN_HTML]
    if f.endswith('notes_zh.json'): return ['NOTES']
    p = Path(f); return [p] if p in S else []

SEP = r'(?:<[^>]*>|\*\*|\s)*'
ENT = {'<': '(?:<|&lt;)', '>': '(?:>|&gt;)', '&': '(?:&|&amp;)', '"': '(?:"|&quot;)', "'": "(?:'|&#x27;|&#39;)"}
def cre(txt):
    out = []
    for ch in txt:
        if ch.isspace(): out.append(r'(?:\s|<[^>]*>)*'); continue
        out.append(ENT.get(ch, re.escape(ch)))
    return SEP.join(out)
def adapt(old, can):
    if old.endswith('%'): return can.lstrip('+')
    if old[0] not in '+−-' and can.startswith('+'): return can[1:]
    if old[0] == '+' and can[0] not in '+−-': return '+' + can
    return can

# ------------------------------------------------------------------ 1 + 2: check-driven number fixes
cc = pd.read_csv(CHK / 'claims_check.csv')
todo = cc[cc.status.isin(['不一致', '写法不统一'])].copy()
groups = todo.groupby(['file', 'context', 'text_as_written'], sort=False)
unresolved = []; PEND = []
for (f, ctx, old), g in groups:
    can = g.canonical.iloc[0]; new = adapt(old, can); k = len(g)
    p0 = ctx.find(old); best = None
    for m in re.finditer(re.escape(old), ctx):
        if best is None or abs(m.start() - 90) < abs(best - 90): best = m.start()
    p0 = best
    tg = target_files(f); done = False
    for L, Rr in [(12, 4), (8, 3), (5, 2), (3, 1), (20, 8), (30, 12), (45, 20), (60, 30)]:
        left = ctx[max(0, p0 - L):p0]; right = ctx[p0 + len(old):p0 + len(old) + Rr]
        rx = re.compile('(' + cre(left) + SEP + ')(' + re.escape(old) + r')(?![\d])(' + SEP + cre(right) + ')')
        hits = []
        for t in tg:
            if t == 'NOTES':
                for key, v in NJ.items():
                    hits += [('NOTES', key, m) for m in rx.finditer(v['text'])]
            else:
                hits += [(t, None, m) for m in rx.finditer(S[t])]
        if len(hits) == k or (len(hits) > k and L >= 60 and len({(h[0], h[1]) for h in hits}) >= 1 and False):
            for t, key, m in hits:
                PEND.append((t, key, m.start(2), m.end(2), new))
                LOG.append(('num', g.claim_id.iloc[0], str(t) + (' #' + key if key else ''), old, new, g.location.iloc[0], g.status.iloc[0]))
            done = True; break
        if len(hits) == 0 and L <= 3: break
    if not done: unresolved.append((g.claim_id.iloc[0], f, old, can, ctx[:160]))
seen = set()
for t, key, a, b, new in sorted(PEND, key=lambda x: -x[2]):
    if (t, key, a) in seen: continue
    seen.add((t, key, a))
    if t == 'NOTES': v = NJ[key]['text']; NJ[key]['text'] = v[:a] + new + v[b:]
    else: S[t] = S[t][:a] + new + S[t][b:]
print('number fixes', len(LOG), 'unresolved', len(unresolved))
for u in unresolved: print('UNRES', u[0], Path(u[1]).name, repr(u[2]), '->', u[3], '|', u[4][:150])

# ------------------------------------------------------------------ literal edits
def rep(p, a, b, n=1, why=''):
    if p == 'NOTES':
        c = sum(v['text'].count(a) for v in NJ.values()); assert c == n, (c, a[:60])
        for v in NJ.values(): v['text'] = v['text'].replace(a, b)
    else:
        c = S[p].count(a); assert c == n, (p.name, c, a[:60]); S[p] = S[p].replace(a, b)
    LOG.append(('text', why, str(p), a, b, '', ''))
SRC = lambda t: f'<span class="src">（{t}）</span>'
SRCE = lambda t: f'<span class="src">({t})</span>'

# 1 #ov n separator
# 1 #ov n: numbers replaced by the check-driven step; separator '+' kept (the report writes '目标 3,734 + 对照 2,182 篇' in 9 other places)
# 1 report section 1 old E4b values -> train-fold standardisation (as section 6.11)
rep(REP, '全部论文标题特异信号 L24 0.050、L40 0.066、L56 0.080；381_stage13/reports/e4b_split_compare.md（group / title-reuse dropped）',
    '全部论文标题特异信号 L24 0.050、L40 0.061、L56 0.075，标准化只在训练折内拟合（作业 11500917）；381_stage13/reports/e4b_trainstd_compare.md Confirmatory configuration 表 new 列', why='1 §1 E4b old values')
rep(REP, 'all papers L24 0.050, L40 0.066, L56 0.080; 381_stage13/reports/e4b_split_compare.md',
    'all papers L24 0.050, L40 0.061, L56 0.075, standardisation fitted on training folds only (job 11500917); 381_stage13/reports/e4b_trainstd_compare.md, confirmatory table, new column', why='1 §1 E4b old values (en)')

# A Stage 8 endpoint wording
A_ZH = '分析计划在 10-18 14:29 写定锁定（主终点为 7 层积分），同日 21:14 的 PROTOCOL 改为 L56，两者都早于 8C 打分；改动人和理由待查（U28）'
A_EN = 'the analysis plan was written and locked on 10-18 at 14:29 (primary endpoint: 7-layer integral); the PROTOCOL of 21:14 the same day switched to L56, both before 8C scoring; who made the change and why is still open (U28)'
rep(REP, '当天 21:14 的 PROTOCOL.md 改成以 L56 为主终点；这份文件是从聊天窗口粘贴生成的，改动由谁、依据什么做出，尚待确认。',
    '同日 21:14 的 PROTOCOL（PROTOCOL.md，从聊天窗口粘贴生成）改为 L56，两者都早于 8C 打分；改动人和理由待查（U28）。', why='A Stage 8 endpoint')
rep(ADV, 'Stage 8 主终点在冻结前从 7 层积分改为 L56，git 中没有改动记录，决定依据待确认（见下）。', 'Stage 8：' + A_ZH + '；git 中没有改动记录。', why='A Stage 8 endpoint')
rep(ADV, 'Stage 8 主终点在冻结后被改成 L56', 'Stage 8 ' + A_ZH, why='A Stage 8 endpoint (merged table)')
T_ADV = R / 'talk_docs/progress_report_for_advisor_zh.html'
rep(T_ADV, 'Stage 8 主终点在冻结后被改成 L56', 'Stage 8 ' + A_ZH, why='A Stage 8 endpoint')
T_WM = R / 'talk_docs/experiment_walkthrough_methods_zh.html'; T_W = R / 'talk_docs/experiment_walkthrough_zh.html'; T_G = R / 'talk_docs/methods_handbook_guide_plain_zh.html'
rep(T_WM, '当时一份文件把主终点改成 L56，我们两种都报告。', A_ZH + '；两种都报告。', why='A Stage 8 endpoint')
rep(T_W, '要主动说明：当时有一份文件把主终点改成了 L56，我们把原定主终点和 L56 都报告了。', '要主动说明：' + A_ZH + '；我们把原定主终点和 L56 都报告了。', why='A Stage 8 endpoint')
rep(T_G, '冻结计划写 7 层积分，当晚 PROTOCOL 改成 L56；谁改的待查', A_ZH, why='A Stage 8 endpoint')
rep(DECK, 'Protocol drift</b>: primary endpoint changed between README and run', 'Protocol drift</b>: plan locked 10-18 14:29 (7-layer integral primary); the 21:14 PROTOCOL switched to L56, both before 8C scoring; who and why open (U28)', why='A Stage 8 endpoint (deck)')
rep('NOTES', '协议漂移，主终点在 README 和实际运行之间改过。', '协议漂移：' + A_ZH + '。', why='A Stage 8 endpoint (notes)')

# 3 report conclusions without data (numbers below were re-read from the source CSVs by verify_no_data_20261107.py)
V = json.loads((Path(__file__).parent / 'no_data_values_20261107.json').read_text())
rep(REP, '小样本的 A−B 不确定（依赖少数几对）。', '小样本的 A−B 不确定（依赖少数几对）' + SRC(V['F2']) + '。', why='3 F2')
rep(REP, '<li><b>Jacobian lens 没有显示额外的论文信息。</b>小样本中 J-Lens 相对 Vanilla 没有增量；全量中它在中间层多读出的是“名字形状”，不区分论文，也不偏向目标组。</li>',
    '<li><b>Jacobian lens 没有显示额外的论文信息。</b>小样本中 J-Lens 相对 Vanilla 没有增量' + SRC(V['F3']) + '；全量中它在中间层多读出的是“名字形状”（名字名次整体更高，但标题特异信号只多一点）' + SRC(V['F4a']) + '，不区分论文，也不偏向目标组' + SRC(V['F4b']) + '。</li>', why='3 F3/F4')
rep(REP, '<b>第一个 token 与名字其余部分的差别由名字格式解释</b>：首字母开头时，姓落在后续 token 上；完整名开头时名本身就带信号。</li>',
    '<b>第一个 token 与名字其余部分的差别由名字格式解释</b>：首字母开头时，姓落在后续 token 上；完整名开头时名本身就带信号' + SRC(V['F5']) + '。</li>', why='3 F5')
n9 = S[REP].count('几乎全部是标题特异的')
rep(REP, '），而且几乎全部是标题特异的，不能用名字好猜来解释。', '），而且主要是标题特异的，不能用名字好猜来解释' + SRC(V['F9']) + '。', why='3 F9 weakened (几乎全部 -> 主要)')
if '目标组的优势真实存在、几乎全部是标题特异的' in S[REP]:
    rep(REP, '目标组的优势真实存在、几乎全部是标题特异的', '目标组的优势真实存在、主要是标题特异的', why='3 F9 same claim (R0/R1 box)')
for a, b in [(') and is almost entirely title-specific, so', ') and is mostly title-specific, so'), ('is therefore almost entirely title-specific.', 'is therefore mostly title-specific.'),
             ('That advantage is almost entirely title-specific and', 'That advantage is mostly title-specific and')]:
    if S[REP].count(a) == 1: rep(REP, a, b, why='3 F9 same claim (en)')
rep(REP, '），而且这部分信息不偏向目标组。</p>', '），而且这部分信息不偏向目标组' + SRC(V['F4b']) + '。</p>', why='3 F10')
rep(REP, 'Jacobian lens 能让中间层读出更多与名字相关的信息，但这部分信息不区分论文；三种 Jacobian lens 的结论一致。<span class="src">（Stage 10 X3：',
    'Jacobian lens 能让中间层读出更多与名字相关的信息，但这部分信息不区分论文；三种 Jacobian lens 的结论一致。' + SRC(V['F4a']) + '<span class="src">（Stage 10 X3：', why='3 F12')
rep(REP, '标题特异信号在名字里的分布取决于格式：首字母几乎不带信号，信号集中在后面的姓上；完整的名本身就带有和姓相当的信号。',
    '标题特异信号在名字里的分布取决于格式：首字母几乎不带信号，信号集中在后面的姓上；完整的名本身就带有和姓相当的信号' + SRC(V['F5']) + '。', why='3 F13')
rep(REP, '<span>没有哪种 lens 能在中间层读出偏向目标组的论文信息；Jacobian lens 在中间层多出的那点标题特异信号很小，对照组反而略多。</span>',
    '<span>中间层（L24–L48）各种 lens 的目标−对照都很小或为负，没有看到明显偏向目标组的论文信息（logit lens 在 L24–L32 有很小的正值）' + SRC(V['F14a']) + '；Jacobian lens 在中间层多出的那点标题特异信号很小，对照组反而略多' + SRC(V['F4b']) + '。</span>', why='3 F14 weakened ("没有哪种 lens" -> small / logit tiny positive)')
rep(REP, '<span class="en">No lens reads target-favouring paper information in middle layers; the small extra title-specific signal of the Jacobian lenses there is, if anything, larger for control papers.</span>',
    '<span class="en">In middle layers (L24–L48) every lens shows a small or negative target − control, so no clear target-favouring paper information (the logit lens has a tiny positive value at L24–L32); the small extra title-specific signal of the Jacobian lenses there is, if anything, larger for control papers.</span>', why='3 F14 weakened (en)')
rep(REP, 'R1 论文让优势更大，但不改变时间点；在 R1 论文内部，模型写对的作者也是在最后几层才领先。',
    'R1 论文让优势更大，但不改变时间点' + SRC(V['F15a']) + '；在 R1 论文内部，模型写对的作者也是在最后几层才领先' + SRC(V['F15b']) + '。', why='3 F15')
rep(REP, '；识别不确定的论文落在两组之间。</p>', '；识别不确定的论文落在两组之间' + SRC(V['F16']) + '。</p>', why='3 F16')
rep(REP, '，主要是因为模型已经写出的作者分数本来就高（循环论证）。</p>', '，主要是因为模型已经写出的作者分数本来就高（循环论证）' + SRC(V['F17']) + '。</p>', why='3 F17')

# C deck slide 64: English hypothesis table
EN = R / 'downloads/Stage13_hypotheses_table_v28_en_tableonly.png'
S[DECK], c = re.subn(r'(<img alt="Hypotheses H1–H3 against readouts M1–M3 and the current results" src=")data:image/png;base64,[A-Za-z0-9+/=]+"',
                     lambda m: m.group(1) + 'data:image/png;base64,' + base64.b64encode(EN.read_bytes()).decode() + '"', S[DECK]); assert c == 1
LOG.append(('text', 'C slide 64 image', str(DECK), 'Stage13_hypotheses_table_v28_tableonly.png (zh)', EN.name, 'slide 64', ''))

# ------------------------------------------------------------------ write
for p, s in S.items():
    assert not re.search('minyan', s, re.I), p
    if s != bkp(p).read_text(encoding='utf-8'): p.write_text(s, encoding='utf-8')
NOTES.write_text(json.dumps(NJ, ensure_ascii=False, indent=1))
json.dump({'log': LOG, 'unresolved': unresolved}, open(Path(__file__).parent / 'apply_log_20261107.json', 'w'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ summaries
num = [l for l in LOG if l[0] == 'num']
G = collections.defaultdict(lambda: collections.Counter())
for _, cid, f, old, new, loc, st in num: G[(cid, st, new)][(old, Path(f.split(' #')[0]).name + (' 备注' if '#' in f else ''))] += 1
L = ['# Unify summary 2026-11-07 (写法不统一 + 不一致 → canonical form of the strict check)', '',
     f'Check table: `{CHK}/claims_check.csv`. Script: `351_stage10/reports/sync_20261107/apply_20261107.py` (backups `*.before_20261107.*`). '
     'Each written form was replaced at its location (anchor = surrounding visible text), sign style kept; percentages written as the canonical ratio. '
     'Handbook: edited in methods/parts/*.html (part K regenerated from the report); process report: in draft_zh.md.', '',
     f'Total replacements: {len(num)}; unresolved: {len(unresolved)}.', '', '| claim | status | canonical | old form → file (count) |', '|---|---|---|---|']
for (cid, st, new), cnt in sorted(G.items()):
    L.append(f'| {cid} | {st} | {new} | ' + '; '.join(f'{o} → {fn} ×{n}' for (o, fn), n in sorted(cnt.items())) + ' |')
if unresolved:
    L += ['', '## Unresolved (anchor not found; fix by hand)', ''] + [f'- {u[0]} `{u[2]}` → {u[3]} in {u[1]}: …{u[4]}…' for u in unresolved]
(NC / 'unify_summary_20261107.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('wrote', NC / 'unify_summary_20261107.md')
