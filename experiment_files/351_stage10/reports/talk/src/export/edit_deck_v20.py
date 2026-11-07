"""2026-11-06: deck v20 = deck v19 build + deck_v20_new (all-token probe, Stage 8 CPU proxy, redo programme, limits; X7 five titles) + talk pages re-rendered (v20_inputs/pages_v20: probe caveat, E4b range) + slide 52 C-1 line + probe caveat pointer on slide 23 + notes caveat pointer. Copy of edit_deck_v19.py; its docstring follows."""
"""2026-11-05 evening: deck v19 = the v18 build (same v17 base and helper inputs) + deck_v19_new (X2 slide, group results / re-runs)
+ method slide 26 with real numbers (method_slides.COMPARE_REAL_NUMBERS = True) + slide 64 hypotheses table v28 + X2 line.
Current v18 files are copied to *.before_20261105c.* first. Writes deck HTML, slides.json, notes_zh.json, v19_order.json."""
"""2026-11-05 deck v18 = v17 (as re-exported with the schematic group-comparison method page) +
 - grey source tags on the HTML slides (TAGS_HTML, keyed by v17 slide number; method SVG pages get a footnote line),
 - image pages (talk deck build) re-rendered with tags + probe caveat (PAGES_DIR/pNN.jpg, built from build_v18.py),
 - first-token caveat on the probe method page,
 - Stage 1–13 naming, 4 new Stage 12/13 result slides after the X5 page, post-defence section at the end (deck_v18_new.py),
 - Chinese notes with full 〔…〕 source tags (NOTES_TAGGED, keyed by v17 slide number; slide 26 note taken from the current v17).
Backups *.before_20261105b.* are made first and are always the input (idempotent). Writes deck HTML, slides.json, notes_zh.json,
and v18_order.json (v18 position -> ('old', v17 number) | ('new', key)) for the pptx patch and the page map."""
import base64, json, re, shutil, sys
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import deck_v20_new as N
SCR = Path('/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/deck')
SRC_DIR = HERE / 'v18_inputs'          # copies of the helper outputs, kept with the scripts
SRC_DIR.mkdir(exist_ok=True)
for f in ['html_tags.json', 'notes_v18_tagged.json']:
    if (SCR / f).exists() and not (SRC_DIR / f).exists(): shutil.copy2(SCR / f, SRC_DIR / f)
PAGES = HERE / 'v20_inputs' / 'pages_v20'
assert PAGES.exists()

import os
DECK = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html'); OUTD = HERE
if os.environ.get('V18_TEST'):   # dry run: inputs = read-only v17 copies, outputs in the test dir
    T_ = Path(os.environ['V18_TEST']); OUTD = T_; DECK = T_ / 'deck.html'
    for f, g in [('deck_v17_readonly.html', 'deck.before_20261105b.html'), ('slides_v17_readonly.json', 'slides.before_20261105b.json'), ('notes_v17_readonly.json', 'notes_zh.before_20261105b.json')]:
        if not (T_ / g).exists(): shutil.copy2(SCR / f, T_ / g)
BK = {DECK: DECK.with_name('stage1_11_deck.before_20261105b.html') if not os.environ.get('V18_TEST') else OUTD / 'deck.before_20261105b.html',
      OUTD / 'slides.json': OUTD / 'slides.before_20261105b.json', OUTD / 'notes_zh.json': OUTD / 'notes_zh.before_20261105b.json'}
for src, bk in BK.items():
    if not bk.exists(): shutil.copy2(src, bk)

for f in [DECK, OUTD / 'slides.json', OUTD / 'notes_zh.json']:
    c = f.with_name(f.stem + '.before_20261106' + f.suffix)
    if f.exists() and not c.exists() and not os.environ.get('V18_TEST'): shutil.copy2(f, c)
h = BK[DECK].read_text(encoding='utf-8')
head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 67, len(secs)
meta = json.loads(BK[OUTD / 'slides.json'].read_text()); notes = json.loads(BK[OUTD / 'notes_zh.json'].read_text())
assert len(meta) == len(notes) == 67

CSS = ('.src{font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;font-size:12.5px;line-height:1.25;font-weight:400;'
       'color:#8a8f98;opacity:1;letter-spacing:0;font-style:normal;white-space:normal}\n.dk .src{color:#9aa3b2}\n'
       'svg text.src{font-size:12.5px;fill:#8a8f98}\n.cavd{position:absolute;left:70px;right:70px;font-family:var(--hand);font-size:17px;color:#B54708}\n')
if '.src{' not in head: head = head.replace('</style>', CSS + '</style>', 1)
head = head.replace('<title>Stages 1–11: where Qwen3-32B holds a paper’s authors</title>', '<title>Stages 1–13: where Qwen3-32B holds a paper’s authors</title>')
assert 'Stages 1–13' in head

# 1. tags on HTML slides (v17 numbering)
tags = json.loads((SRC_DIR / 'html_tags.json').read_text(encoding='utf-8')); nt = 0
for e in tags:
    k = e['slide'] - 1; assert e['slide'] != 26
    c = secs[k].count(e['old']); assert c == 1, (e['slide'], c, e['old'][:60])
    secs[k] = secs[k].replace(e['old'], e['new']); nt += e['new'].count('class="src"')
print('html tags', nt)

# 1b. corrections made on the live published deck (merged_deck/live_edits_20261105.json), applied by content, sources checked
def sub1(k, o, n):
    c = secs[k - 1].count(o); assert c == 1, (k, c, o[:60]); secs[k - 1] = secs[k - 1].replace(o, n)
sub1(14, '[4.7, 13.9], 35/50 papers positive', '[4.8, 14.0], 35/50 papers positive')        # 351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv: [+4.77, +14.00]
sub1(17, 'Stage 8D frozen estimates, 95% CI (pp)</figcaption>',
     'Stage 8D L56 estimates (PROTOCOL.md), 95% CI (pp)<span class="src">\u200b(primary_questions.csv)</span></figcaption>')
sub1(17, '<td class="a">RQ1 title<span class="src">', '<td class="a">RQ1 title, L56<span class="src">')
i0 = secs[16].index('<td class="a">RQ2 A−B<span class="src">'); i1 = secs[16].index('</tr>', i0) + 5
secs[16] = (secs[16][:i0].replace('<td class="a">RQ2 A−B', '<td class="a">RQ2 A−B') + secs[16][i0:i1].replace('RQ2 A−B<span', 'RQ2 A−B, L56<span', 1)
            + '<tr><td class="a">RQ2 A−B, 7-layer (frozen primary)<span class="src">\u200b(100 pairs; s8_endpoints.csv)</span></td><td>+2.41 pp</td><td>[+0.91, +4.00]</td></tr>'
            + secs[16][i1:])                                                                       # 351_stage8/recompute_2026-10-30/s8_endpoints.csv: +2.409 [+0.909, +4.003]
sub1(18, 'Scripts not yet archived: <span class="r">not a completed experiment</span>',
     'Original scripts missing; recomputed from raw logits (30 Oct), same estimates<span class="src">\u200b(351_stage8/recompute_2026-10-30/)</span>: <span class="r">post-hoc only</span>')
assert '+0.229]' in secs[41] and '+0.228]' not in secs[41]                                         # e. done by the tag helper (fix)

# 1c. user wording decisions (2026-11-05 afternoon): L48 recovery 82%; "middle layers ≈ 0" -> L24–L40 ≈ 0, L48 slightly negative
TG = '<span class="src">\u200b(§6.4; J-lens L48 −0.037 to −0.054, CI below 0; B_spec_target_vs_control_within_bin.csv)</span>'
sub1(58, 'Whole prompt: 0.83 at L48', 'Whole prompt: 0.82 at L48')
sub1(29, 'target − control ≈0 in middle layers,', 'target − control ≈0 at L24–L40, slightly negative at L48 (−0.04 to −0.05)<span class="src">\u200b(§6.4)</span>,')
sub1(58, 'Target − control ≈ 0 in middle layers,', 'Target − control ≈ 0 at L24–L40, slightly negative at L48 (−0.04 to −0.05),')
sub1(60, '≈0 middle</td>', '≈0 at L24–L40, slightly negative at L48 (−0.04 to −0.05)</td>')
sub1(60, '≈0 middle; R1', '≈0 at L24–L40, slightly negative at L48; R1')

# 1d. method slide 26 with real numbers (user 2026-11-05 ~17:20) and slide 64: hypotheses table v28 + X2 line
sys.path.insert(0, '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/method_figs')
import method_slides as MS, build_method_figs as BMF
from method_lib import svg_of
assert MS.COMPARE_REAL_NUMBERS, 'set COMPARE_REAL_NUMBERS = True in method_figs/method_slides.py'
items = next(it for k, t, it in BMF.slides() if k == 'compare')
svg = svg_of(items, 'Group comparisons', uid='mcomp')
svg = svg.replace('</svg>', '<text x="70" y="712" class="src" font-size="12.5" fill="#8a8f98" text-anchor="start">P1 +0.200 [0.188, 0.213]: A − B, 3,417 / 2,148 papers; P2 co-authors +0.061, first author +0.031: C − A; dose 0.17 → 0.46: R0 by orders right; 391_groups/primary.csv, stage10_curves.csv</text></svg>', 1)
assert meta[25].get('method') == 'compare'
secs[25] = re.sub(r'<svg.*</svg>', lambda m: svg, secs[25], count=1, flags=re.S)
import base64 as _b64
HYP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/Stage13_hypotheses_table_v28_tableonly.png'
secs[63], c = re.subn(r'(<img alt="Hypotheses H1–H3 against readouts M1–M3 and the current results" src=")data:image/png;base64,[A-Za-z0-9+/=]+"',
                      lambda m: m.group(1) + 'data:image/png;base64,' + _b64.b64encode(open(HYP, 'rb').read()).decode() + '"', secs[63]); assert c == 1
sub1(64, 'Hypotheses H1–H3 × readouts M1–M3 and current results (report, 2026-11-01)', 'Hypotheses H1–H3 × readouts M1–M3 and current results (report v28, 2026-11-05)')
sub1(64, 'H3 (hidden author knowledge): insufficient evidence</p>',
     'H3 (hidden author knowledge): insufficient evidence · X2 (2026-11-05): H2 not supported; H3 passes by rule but the author subspace decodes nothing → still insufficient</p>')

# 1e. Stage 7.1 slide (v17 52): title-contrast line (addendum 13 C-1)
sub1(52, '\n </div>\n</div>\n<div class="note" style="position:absolute;left:90px;bottom:62px;width:620px">Completing',
     '<p style="margin-top:10px;font-size:18px;line-height:1.3" class="g">With a title contrast (addendum 13 C-1): holds at the output (+0.244) and at L62 (+0.278 logit, +0.317 public J-lens); the public J-lens 6-layer mean is not significant (+0.077 [−0.021, +0.180])<span class="src">\u200b(20 pairs, rest of the name; c13_C1.md)</span></p>'
     '\n </div>\n</div>\n<div class="note" style="position:absolute;left:90px;bottom:62px;width:620px">Completing')

# 2. image pages from the v18 talk build
ni = 0
def img_repl(m):
    global ni
    n = int(m.group(2)); ni += 1
    return f'{m.group(1)}data:image/jpeg;base64,' + base64.b64encode((PAGES / f'p{n:02d}.jpg').read_bytes()).decode() + '"'
for k, s in enumerate(secs):
    if meta[k]['kind'] == 'deck':
        secs[k], c = re.subn(r'(<img alt="Stage 10-11 slide (\d+)" src=")data:image/jpeg;base64,[A-Za-z0-9+/=]+"', img_repl, s)
        assert c == 1 and int(re.search(r'alt="Stage 10-11 slide (\d+)"', s).group(1)) == meta[k]['deck'], (k + 1, c)
print('image pages replaced', ni)

# 3. probe method page caveat (v17 slide 23)
assert meta[22].get('method') == 'probe'
secs[22] = secs[22].replace('<span class="pg"></span></section>',
    '<div class="cavd" style="top:96px;text-align:right">⚠ E4b scores only the first name token (mostly an initial) · all tokens by role: see the addendum-9 slide (surname first token L40 +0.071<span class="src">\u200b(1,395 papers; e4b_alltok.md)</span>)</div>'
    '<span class="pg"></span></section>', 1)
assert 'cavd' in secs[22]

# 4. cover: Stage 1–13
c0 = secs[0].count('<p class="m" style="font-size:22px">Stages 10–11</p>'); assert c0 == 1
secs[0] = secs[0].replace('<p class="m" style="font-size:22px">Stages 10–11</p>', '<p class="m" style="font-size:22px">Stages 10–13 · post-defence additions (2026-11-05) at the end</p>')

# 5. order with new slides
G = {'after_summary': [s for s in N.SLIDES if s['where'] == 'after_summary'], 'end': [s for s in N.SLIDES if s['where'] == 'end'], 'after18': [s for s in N.SLIDES if s['where'] == 'after18']}
order = []
for i in range(1, 68):
    order.append(('old', i))
    if i == 65: order += [('new', s['key']) for s in G['after_summary']]   # after the X5 layer-order page (incl. X2, addendum 9)
    if i == 18: order += [('new', s['key']) for s in G['after18']]   # Stage 8 CPU proxy after the Stage 8D-8E page
order += [('new', s['key']) for s in G['end']]
BYKEY = {s['key']: s for s in N.SLIDES}

def img_uri(p): return 'data:image/png;base64,' + base64.b64encode(Path(p).read_bytes()).decode()
tagged = json.loads((SRC_DIR / 'notes_v18_tagged.json').read_text(encoding='utf-8'))
old_notes_ro = json.loads((SCR / 'notes_v17_readonly.json').read_text(encoding='utf-8'))
out, nm, nn = [], [], {}
for k, (kind, v) in enumerate(order, 1):
    if kind == 'old':
        out.append(secs[v - 1]); e = dict(meta[v - 1]); e['i'] = k; nm.append(e)
        cur = notes[str(v)]
        if v == 26 or cur['text'] != old_notes_ro[str(v)]['text']:
            nn[str(k)] = cur                                  # changed in the v17 re-export: keep as is
            if v != 26: print('WARN note changed since tagging, kept untagged: v17', v)
        else:
            nn[str(k)] = tagged[str(v)]
    else:
        sp = BYKEY[v]
        out.append(N.html_section(sp, img_uri(sp['img']) if sp.get('img') else None))
        nm.append({'i': k, 'kind': 'html', 'text': N.slide_text(sp), 'figs': [], 'added': '2026-11-05', 'new18': v})
        nn[str(k)] = {'new': True, 'text': sp['notes']}
import method_pages_v17 as MP17
NOTE26 = (MP17.NOTE_COMPARE_REAL.replace('+0.200 [0.188, 0.213]', '+0.200 [0.188, 0.213]〔分组对比 P1 A − B，未写出作者，最终输出 L63，A 3,417 / B 2,148 篇，引用档内差，团队聚类 95% CI；391_groups/primary.csv〕')
          .replace('+0.061 [0.034, 0.090]', '+0.061 [0.034, 0.090]〔P2-other C − A，C 390 / A 2,826 篇；primary.csv〕')
          .replace('+0.031 [−0.006, 0.069]', '+0.031 [−0.006, 0.069]〔P2-first C − A，C 292 / A 3,199 篇，Holm p 0.112；primary.csv〕')
          .replace('从 0.17 升到 0.46。', '从 0.17 升到 0.46〔R0 未写出作者，0 种对 927 篇 0.170、4 种对 4,105 篇 0.463；391_groups/stage10_curves.csv〕。'))
assert NOTE26.count('〔') == 4
k26 = next(k for k, (kind, v) in enumerate(order, 1) if kind == 'old' and v == 26)
nn[str(k26)] = {'new': True, 'text': NOTE26}
k64 = next(k for k, (kind, v) in enumerate(order, 1) if kind == 'old' and v == 64)
nn[str(k64)]['text'] += ' X2（2026-11-05）：按预注册判据 H2 不支持、H3 通过，但作者子空间几乎解码不出作者，H3 证据仍不足；总体判断不变。'
NOTE_FIX_ALLTOK = ('注意：这个 probe 只给每位作者名字的第一个 token 打分（73% 的名字以首字母开头，多数时候是首字母）；给全部名字 token 打分、按首字母/名/姓分开的版本按补充 9 进行中，尚无结果。',
                   '注意：这个 probe 只给每位作者名字的第一个 token 打分（73% 的名字以首字母开头，多数时候是首字母）；给全部名字 token 打分、按首字母 / 名 / 姓分开的版本（补充 9）已完成，见 Stage 13 部分的补充 9 页：L40 姓的第一个 token +0.071 [0.058, 0.085]〔补充 9，目标 + 对照 1,395 篇，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md〕。')
nfa = 0
for v in nn.values():
    if NOTE_FIX_ALLTOK[0] in v['text']: v['text'] = v['text'].replace(*NOTE_FIX_ALLTOK); nfa += 1
assert nfa == 8, nfa
k52 = next(k for k, (kind, v) in enumerate(order, 1) if kind == 'old' and v == 52)
nn[str(k52)]['text'] += ' 2026-11-06 补（补充 13 C-1，事后）：加上标题对照（真标题 − Stage 10 的 5 个假标题）后，A−B 的差别在模型输出和 L62 上成立，public J-lens 多层平均不显著：名字其余 token 上输出 +0.244 [0.087, 0.398]、logit L62 +0.278 [0.088, 0.483]、public J-lens L62 +0.317 [0.145, 0.506]，public J-lens 6 层平均 +0.077 [−0.021, +0.180]〔补充 13 C-1，Pilot50 20 对 A−B，配对 bootstrap 95% CI；381_stage13/reports/c13_C1.md aa_cont 行〕。'
NOTE_FIX = [('L48 恢复 83%〔', 'L48 恢复 82%〔'), ('（四舍五入为 82%–83%）', ''), ('在 L48 恢复 0.83〔', '在 L48 恢复 0.82〔'),
            ('目标−对照在中间层约为 0，', '目标−对照在 L24–L40 约为 0、L48 略为负（−0.04 到 −0.05，区间不含 0〔Stage 10，引用档内目标−对照，三种 Jacobian lens L48 −0.037 到 −0.054；351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv〕），'),
            ('、中间层约 0，', '、L24–L40 约为 0、L48 略为负（−0.04 到 −0.05，区间不含 0），')]
for a_, b_ in NOTE_FIX:
    c_ = sum(v['text'].count(a_) for v in nn.values()); assert c_ >= 1, a_
    for v in nn.values(): v['text'] = v['text'].replace(a_, b_)
DECK.write_text(head + ''.join(out) + tail, encoding='utf-8')
(OUTD / 'slides.json').write_text(json.dumps(nm, ensure_ascii=False, indent=1))
(OUTD / 'notes_zh.json').write_text(json.dumps(nn, ensure_ascii=False, indent=1))
(OUTD / 'v20_order.json').write_text(json.dumps(order))
assert not re.search('minyan', DECK.read_text(encoding='utf-8') + json.dumps(nn, ensure_ascii=False), re.I)
print('v18 slides', len(out), '| new at', [k for k, (kind, v) in enumerate(order, 1) if kind == 'new'])
