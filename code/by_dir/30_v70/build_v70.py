#!/usr/bin/env python3
"""HTML v70: close the loop on the hypothesis tables (slides 35-37) and the four evidence-matrix pages (54, 83, 108, 127)
from the user's canonical matrix (~/jlens_work/27_v67/canonical_matrix.md, user 2026-11-23). Add-only: the replaced old
matrix tables go to a new backup slide at the end (no renumbering)."""
import re, sys, html as H
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/tools')
from prepublish_check import html_slides

SRC = '/home/zhang.zhiqi2/jlens_work/30_v70/deck_v69_base.html'
OUT = '/home/zhang.zhiqi2/jlens_work/30_v70/deck_v70.html'
t = open(SRC, encoding='utf-8').read()

# ---------------- canonical rows (display form; numbers verified against v69, R_id 0.004 per the deck) ----------------
# (test label, verdict, key number, strength, slide)
BLOCKS = [
 ('H1', 'H1 · does the middle know "what is asked"?', [
   ('“:” new question vs paper', '(✓)', '4.7× (L4) → 2.2× (L48)', 'descriptive', '51'),
   ('probe after the question change', '(✓)', 'T 0.24–0.41', 'descriptive', '49'),
   ('top lens word', '~', 'format words; title-dependent 28–64%', 'descriptive', '37'),
   ('format locking (+ checks)', '~', 'L56 = sink artefact; names default', 'locked + exploratory', '52'),
   ('swap “:” at L56', '(✓)', 'author signal −0.03', 'locked', '52'),
  ], 'downgraded: “:” follows the question; the format layer is not pinned down', '53', 'part'),
 ('H2', 'H2 · does the middle know "which paper"?', [
   ('paper facts at the title', '~', 'readable, inferable from text', 'descriptive', '16'),
   ('same title, other question · copy', '~', 'ceiling: L4 cosine 0.998', 'exploratory', '77'),
   ('paraphrased title', '~', 'text-only model reaches 60%', 'pre-registered', '71'),
   ('made-up title', '✗', 'meaning 75%; real title +0.106', 'locked', '73'),
   ('rare vs common words', '✗', '0.162 vs 0.027', 'locked', '80'),
   ('recognised / citation check', '✗', 'not larger; smaller if cited more', 'locked', '78'),
   ('variance split', '✗', 'identity ≈ 0', 'locked', '79'),
   ('"paper facts" subspace swap', '✗', 'R_id 0.004', 'pre-registered', '101'),
   ('L8 surname test', '(✓)', 'T1 +0.046; T2/T3 marginal; ½ topic', 'locked', '81'),
  ], 'not a general paper identity, with one small locked exception', '82', 'weak'),
 ('H3', 'H3 · author info in the middle, not in vocabulary directions?', [
   ('author-prompt lens, mid layers', '✗', '−0.058 at L48', 'pre-registered', '94'),
   ('probe at the title', '(✓)', '+0.052 at L24', 'descriptive', '93'),
   ('same-scale probe vs lens', '✓', 'L40 +0.021, L48 +0.062', 'locked', '99'),
   ('"author" subspace swap', '~', 'passes, moves only ≈ 7%', 'pre-registered', '101'),
   ('direction of the difference', '~', 'spread; not on author axes', 'exploratory', '100'),
   ('inject the author direction', '(✓)', '2.5% → 9.7%; mainly write channel', 'locked', '105'),
  ], 'supported; small effect; correlational evidence', '107', 'sup'),
 ('W', 'Writing step (the bottleneck)', [
   ('L57–L61 MLPs write', '✓', 'MLP − attention +0.040', 'settled', '122'),
   ('strengthen the arrived signal', '✗', 'unchanged ("too weak" refuted)', 'locked', '123'),
   ('give the first initial', '✓', '4.0% → 15.2%', 'locked', '33'),
   ('late suppression', '(✓)', 'about 1 in 8 papers', 'locked (just past bound)', '124'),
   ('reversal curse (direction)', '✗', '−0.032 (refuted)', 'locked', '125'),
  ], 'the bottleneck is the late writing step, not signal strength', '126', 'sup'),
]
VCLS = {'✓': 'sup', '(✓)': 'part', '✗': 'weak', '~': 'neu', '—': ''}
VBG = {'sup': '#e7f1fb', 'part': '#f9eeda', 'weak': '#fbebeb', 'neu': '#f0efec', '': '#ffffff'}
VFG = {'sup': '#2E5E8C', 'part': '#8A5A12', 'weak': '#A23A30', 'neu': '#5A6170', '': '#C9CED6'}


def scol(strength):
    s = strength.lower()
    if 'settled' in s: return ('#2E7D46', '#E3F1E7')
    if 'exploratory' in s and 'locked' in s: return ('#3C78B4', '#E6EFF8')
    if 'locked' in s: return ('#3C78B4', '#E6EFF8')
    if 'pre-registered' in s: return ('#5B4BA6', '#ECE9F7')
    if 'exploratory' in s: return ('#B54708', '#FCEBDD')
    return ('#6A7385', '#EEF0F3')


def stag(strength):
    fg, bg = scol(strength)
    return (f'<span style="display:inline-block;padding:0 5px;border-radius:4px;background:{bg};color:{fg};'
            f'border:1px solid {fg};font-size:11px;line-height:1.3;white-space:nowrap">{H.escape(strength)}</span>')


def block_html(key, title, rows, verdict, vslide, vcls, filled, later_note):
    head = (f'<div style="font-weight:700;font-size:14px;padding:2px 6px;border-bottom:2px solid #22304A;'
            f'{"background:rgba(255,228,94,.35);" if filled == "new" else ""}">{H.escape(title)}</div>')
    if not filled:
        return (f'<div style="border:1.5px dashed #C9CED6;border-radius:8px;background:#fff;padding:0 0 4px;color:#9AA3B2">'
                + head.replace('#22304A', '#C9CED6') +
                f'<div style="padding:8px 8px;font-size:14px">{H.escape(later_note)}</div></div>')
    trs = []
    for (lab, v, num, st, sl) in rows:
        c = VCLS[v]
        trs.append(
            f'<tr><td style="width:30px;text-align:center;font-weight:700;font-size:13.5px;background:{VBG[c]};color:{VFG[c]};'
            f'border:1px solid #fff">{H.escape(v)}</td>'
            f'<td style="padding:1px 5px;font-size:12.5px;line-height:1.15">{H.escape(lab)}</td>'
            f'<td style="padding:1px 5px;font-size:12.5px;line-height:1.15;background:{VBG[c]}">{H.escape(num)}</td>'
            f'<td style="padding:1px 3px">{stag(st)}</td>'
            f'<td style="padding:2px 4px;font-size:12px;color:#6A7385;white-space:nowrap">s. {sl}</td></tr>')
    trs.append(f'<tr><td colspan="5" style="padding:2px 6px;font-size:13px;background:{VBG[vcls]};color:#22304A;'
               f'border-top:1.5px solid #22304A"><b>Verdict:</b> {H.escape(verdict)} <span style="color:#6A7385;font-size:12px">→ s. {vslide}</span></td></tr>')
    border = '2.5px solid #D9772B' if filled == 'new' else '1.5px solid #C9CED6'
    return (f'<div style="border:{border};border-radius:8px;background:rgba(255,255,255,.92);overflow:hidden">{head}'
            f'<table style="border-collapse:collapse;width:100%">{"".join(trs)}</table></div>')


LEGEND = ('<div style="font-size:11.5px;margin-top:3px;color:#22304A">'
          '<span style="background:#e7f1fb;padding:0 4px">✓ supports</span> '
          '<span style="background:#f9eeda;padding:0 4px">(✓) partly</span> '
          '<span style="background:#fbebeb;padding:0 4px">✗ weakens</span> '
          '<span style="background:#f0efec;padding:0 4px">~ cannot separate</span> &nbsp;strength: '
          + ' '.join(stag(x) for x in ('settled', 'locked', 'pre-registered', 'descriptive', 'exploratory')) +
          ' &nbsp;s. = slide</div>')


def grid(filled_keys, new_key):
    b = {k: (k, title, rows, v, vs, vc) for (k, title, rows, v, vs, vc) in BLOCKS}
    later = {'H2': 'tested in Part 4', 'H3': 'tested in Part 5', 'W': 'tested in Part 6', 'H1': 'tested in Part 3'}
    def cell(k):
        k_, title, rows, v, vs, vc = b[k]
        f = ('new' if k == new_key else 'old') if k in filled_keys else None
        return block_html(k, title, rows, v, vs, vc, f, later[k])
    # left column: H1 over H3; right column: H2 over Writing step
    return ('<div style="display:grid;grid-template-columns:545px 595px;column-gap:12px;row-gap:0;align-items:start">'
            f'<div style="display:flex;flex-direction:column;gap:5px">{cell("H1")}{cell("H3")}</div>'
            f'<div style="display:flex;flex-direction:column;gap:5px">{cell("H2")}{cell("W")}</div></div>' + LEGEND)


# ---------------- slide edits ----------------
slides = html_slides(t)  if False else None
def get_sections(t):
    return list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))

secs = get_sections(t)
def sec_text(n): return secs[n - 1].group(0)

new = {}
backup_parts = []

# --- slide 35 ---
s = sec_text(35)
s = s.replace('paper facts are readable at the title early (attribute probe)',
              'paper facts inferable from the title text are readable early (attribute probe)')
s = s.replace(' · <span style="color:#C84A3E">⚠ = known issue, marked for confirmation, not yet changed</span>', '')
s = s.replace('Current result (2026-11-21)', 'Current result (2026-11-23)')
old = ('<td class="sup"><span class="cl"><span class="k">Verdict:</span> <span class="mk"><b>Supported at “:” and the name positions</b></span> '
       '<span class="pm"><span class="st c2">fairly solid</span></span><span class="pmn">⚠ strength tag to confirm</span></span>')
assert old in s, 'H1 verdict cell'
s = s.replace(old, '<td class="part"><span class="cl"><span class="k">Verdict:</span> <span class="mk"><b>Downgraded: “:” follows the question; '
                   'the format layer is not pinned down</b></span> <span class="tg desc">descriptive</span> <span class="tg lsup">locked rule downgraded</span> → slide 53</span>')
old = ('<td class="weak pm2"><span class="cl"><span class="k">Prediction:</span> the same paper under different questions is close in the middle layers and separates by task only late</span>'
       '<span class="cl"><span class="k"><b>Result</b>:</span> <span class="ul">not above the L4 text level, not supported</span></span><span class="pmn">⚠ cell colour to confirm</span></td>')
assert old in s, 'H2 question-swap cell'
s = s.replace(old, '<td class="neu pm2"><span class="cl"><span class="k">Prediction:</span> the same paper under different questions is close in the middle layers and separates by task only late</span>'
                   '<span class="cl"><span class="k"><b>Result</b>:</span> <span class="ul">cannot separate — ceiling: the same title text gives cosine 0.998 already at L4</span> → slide 77</span></td>')
assert '⚠' not in s
new[35] = s

# --- slide 36 ---
s = sec_text(36)
s = s.replace('Current result (2026-11-21)', 'Current result (2026-11-23)')
old = '<span class="mk"><b>Supported on the same scale</b></span> (same-scale test, pre-registered) <span class="st c2">fairly solid</span></span>'
assert old in s, 'H3 verdict'
s = s.replace(old, '<span class="mk"><b>Supported on the same scale</b></span> (same-scale test, pre-registered) <span class="tg lsup">locked · supported</span> '
                   '<span class="ul">small effect; correlational evidence</span></span>')
old = '<span class="cl"><span class="k">Page:</span> → slide 99</span>'
assert old in s
s = s.replace(old, '<span class="cl"><span class="k">Injection:</span> <b>2.5% → 9.7%</b> correct surnames, mainly a write channel <span class="tg lsup">locked</span> → slide 105 · <span class="k">Page:</span> → slide 99</span>', 1)
new[36] = s

# --- slide 37: corrections + canonical full matrix replaces the old sample matrix (old table -> backup) ---
s = sec_text(37)
i = s.find('<div style="position:absolute;left:70px;top:458px;width:1140px">')
j = s.find('</table>', i) + len('</table>')
assert i > 0 and j > i
old_matrix = s[i:j] + '</div>'
k = j
# the old wrapper div closes right after </table>
assert s[k:k + 6] == '</div>', s[k:k + 40]
backup_parts.append(('Slide 37 · earlier evidence matrix (sample mapping, superseded by the canonical matrix)', old_matrix.replace(
    'position:absolute;left:70px;top:458px;width:1140px', 'position:relative;width:1140px')))
# full canonical matrix: rows H1/H2/H3/W, columns = all 25 tests grouped by block, symbols in their own block
cols = []
for (k_, title, rows, v, vs, vc) in BLOCKS:
    for r in rows: cols.append((k_, r))
def short(lbl):
    m = {'“:” new question vs new paper': '“:” new Q vs paper', 'probe after the question changes at “:”': 'probe after Q change',
         'top lens word': 'top lens word', 'format-locking test (+ checks)': 'format locking', 'swap the “:” state at L56': '“:” swap L56',
         'paper facts at the title': 'paper facts', 'same title, other question · copy · find again': 'ceiling tests',
         'paraphrased title': 'paraphrase', 'made-up title': 'made-up title', 'rare vs common words': 'rare words',
         'recognised / citation check': 'recog. / citations', 'variance split': 'variance split', 'swap only the "paper facts" subspace': 'facts subspace',
         'L8 surname test': 'L8 surname', 'author-prompt lens, middle layers': 'author lens', 'probe at the title': 'title probe',
         'same-scale probe vs lens': 'probe vs lens', 'swap only the "author" subspace': 'author subspace', 'direction of the difference': 'directions',
         'inject the author direction': 'injection', 'L57–L61 MLPs write': 'MLP writing', 'strengthen the arrived signal': 'strengthen',
         'give the first initial': 'first initial', 'late suppression': 'late suppression', 'direction asymmetry (reversal curse)': 'reversal curse'}
    return m[lbl]
GRP = {'H1': 'H1 tests', 'H2': 'H2 tests', 'H3': 'H3 tests', 'W': 'writing-step tests'}
SH = {'“:” new question vs paper': '“:” new Q<br>vs paper', 'probe after the question change': 'probe<br>after Q',
      'top lens word': 'top lens<br>word', 'format locking (+ checks)': 'format<br>locking', 'swap “:” at L56': '“:” swap<br>L56',
      'paper facts at the title': 'paper<br>facts', 'same title, other question · copy': 'ceiling<br>tests', 'paraphrased title': 'para-<br>phrase',
      'made-up title': 'made-up<br>title', 'rare vs common words': 'rare<br>words', 'recognised / citation check': 'recog. /<br>citations',
      'variance split': 'variance<br>split', '"paper facts" subspace swap': 'facts<br>subspace', 'L8 surname test': 'L8<br>surname',
      'author-prompt lens, mid layers': 'author<br>lens', 'probe at the title': 'title<br>probe', 'same-scale probe vs lens': 'probe vs<br>lens',
      '"author" subspace swap': 'author<br>subspace', 'direction of the difference': 'direc-<br>tions', 'inject the author direction': 'inject-<br>ion',
      'L57–L61 MLPs write': 'MLP<br>writing', 'strengthen the arrived signal': 'streng-<br>then', 'give the first initial': 'first<br>initial',
      'late suppression': 'late<br>suppr.', 'reversal curse (direction)': 'reversal<br>curse'}
GRP = {'H1': 'H1 tests', 'H2': 'H2 tests', 'H3': 'H3 tests', 'W': 'writing-step tests'}
GCOL = {'H1': '#f9eeda', 'H2': '#fbebeb', 'H3': '#e7f1fb', 'W': '#e3f1e7'}
hdr1 = ''
hdr2 = ('<tr><th style="width:96px;font-size:9.5px;font-weight:400;text-align:left;color:#6A7385;line-height:1.05">Result per test → (predictions: cards)</th>'
        + ''.join(f'<th style="font-size:9.5px;font-weight:400;line-height:1.05;padding:1px 0;text-align:center;border-top:3px solid {GCOL[k_].replace("#f9eeda","#D9A441").replace("#fbebeb","#C84A3E").replace("#e7f1fb","#3C78B4").replace("#e3f1e7","#2E7D46")}">{SH[r[0]]}</th>' for (k_, r) in cols) + '</tr>')
rowlab = {'H1': 'H1 question', 'H2': 'H2 identity', 'H3': 'H3 held', 'W': 'writing step'}
body = ''
for (k_, title, rows, v, vs, vc) in BLOCKS:
    tds = ''
    for (kk, r) in cols:
        if kk != k_:
            tds += '<td style="background:#fff;color:#D5D9E0;text-align:center;font-size:10px;border:1px solid #EEF0F3;line-height:1.1">—</td>'
        else:
            c = VCLS[r[1]]; fg, bg = scol(r[3])
            tds += (f'<td style="background:{VBG[c]};color:{VFG[c]};text-align:center;border:1px solid #fff;'
                    f'border-bottom:3px solid {fg};padding:0;line-height:1.1;white-space:nowrap"><b style="font-size:11px">{H.escape(r[1])}</b>'
                    f'<span style="font-size:9.5px;color:#6A7385"> {r[4]}</span></td>')
    body += (f'<tr><td style="font-size:10.5px;font-weight:700;padding:0 3px;background:{VBG[vc]};line-height:1.15">{rowlab[k_]}</td>{tds}</tr>')
canon = ('<div style="position:absolute;left:70px;top:465px;width:1140px;background:rgba(255,255,255,.9)">'
         '<div style="font-family:\'Noto Sans SC\',sans-serif;font-size:11px;font-weight:700;color:#22304A;margin-bottom:0">'
         'Evidence matrix (canonical, 2026-11-23) · top bar = H1 / H2 / H3 / writing tests · colour = effect · bottom bar = strength (legend: slide 127) · number = slide</div>'
         f'<table style="border-collapse:collapse;font-family:\'Noto Sans SC\',sans-serif;width:100%;table-layout:fixed">{hdr1}{hdr2}{body}</table></div>')
pointer = ('<div style="position:absolute;left:70px;top:478px;width:1140px;font-family:\'Noto Sans SC\',sans-serif;font-size:16px;'
           'font-weight:700;color:#22304A">Full evidence matrix → slide 127 <span style="font-weight:400;font-size:13px;color:#6A7385">'
           '(one canonical matrix: H1, H2, H3 and the writing step × every test; also filled step by step on slides 54, 83, 108)</span></div>')
s = s[:i] + pointer + s[k + 6:]
# alignment of the emphasis cards with the canonical matrix (wording / tags only)
rep37 = [
 ('more for a new question than for a new paper <span class="tg solid">fairly solid</span>', 'more for a new question than for a new paper <span class="tg desc">descriptive</span> · verdict: downgraded, format layer not pinned down'),
 ('<span class="k" style="color:#3C78B4">Supports:</span> a same-meaning made-up title recovers <b>75%</b>; the real title adds R̄ <b>+0.106</b>',
  '<span class="k" style="color:#C84A3E">Weakens (identity):</span> a same-meaning made-up title recovers <b>75%</b>; the real title adds only R̄ <b>+0.106</b>'),
 ('· question swap ≤ L4 text level', '· question swap: cannot separate (ceiling)'),
 ('(same-scale test, pre-registered) <span class="tg solid">fairly solid</span> → slide 99', '(same-scale test, pre-registered) <span class="tg lsup">locked · supported</span> → slide 99; injection 2.5% → 9.7%, mainly a write channel → slide 105'),
]
for a, b2 in rep37:
    if a in s: s = s.replace(a, b2)
    else: print('WARN slide 37 text not found:', a[:60])
new[37] = s

# --- slides 54 / 83 / 108 / 127: canonical progressive matrix replaces the old table (old 127 table -> backup) ---
PAGES = {54: (['H1'], 'H1'), 83: (['H1', 'H2'], 'H2'), 108: (['H1', 'H2', 'H3'], 'H3'), 127: (['H1', 'H2', 'H3', 'W'], 'W')}
for n, (keys, newk) in PAGES.items():
    s = sec_text(n)
    i = s.find('<div style="position:absolute;z-index:4;left:70px;top:112px;width:1150px;')
    assert i > 0, n
    # the table wrapper ends right before the So line
    j = s.find('<div class="soln"', i)
    assert j > i, n
    if n == 127:
        backup_parts.append(('Slide 127 · earlier evidence-matrix layout (columns by method; superseded by the canonical matrix)',
                             s[i:j].replace('position:absolute;z-index:4;left:70px;top:112px;width:1150px;', 'position:relative;width:1150px;')))
    blk = (f'<div style="position:absolute;z-index:4;left:70px;top:100px;width:1152px;font-family:\'Noto Sans SC\',\'PingFang SC\','
           f'\'Droid Sans Fallback\',system-ui,sans-serif;color:#22304A">{grid(keys, newk)}</div>')
    s = s[:i] + blk + s[j:]
    new[n] = s


# --- coordinator fixes 2026-11-24 ---
new[35] = new[35].replace('(surname at L8,', '(surname from L8,').replace('Current result (2026-11-23)', 'Current result (2026-11-24)')
new[36] = new[36].replace('Current result (2026-11-23)', 'Current result (2026-11-24)')
new[37] = (new[37].replace('L8 surname signal beyond topic', 'surname signal from L8 beyond topic')
           .replace('Evidence matrix (canonical, 2026-11-23)', 'Evidence matrix (canonical, 2026-11-24)')
           .replace('<div class="fxu" style="left:70px;top:628px;width:1140px">', '<div class="fxu" style="left:70px;top:628px;width:600px">')
           .replace('<div class="soln covso" style="left:384px;top:662px;width:760px;', '<div class="soln covso" style="left:690px;top:640px;width:520px;'))
# --- backup slide (appended at the end; no renumbering) ---
bk = ('<section class="slide lt" aria-label="Backup B23 · earlier evidence matrices">'
      '<span class="tag">Backup B23</span><h2 style="font-size:34px">B23 · Earlier evidence-matrix layouts (superseded)</h2>'
      '<p class="sub" style="font-size:15px;margin-bottom:4px">Kept unchanged for reference; every matrix in the deck is now drawn from one canonical matrix (slides 37, 54, 83, 108, 127).</p>'
      + ''.join(f'<div style="margin:2px 0 8px;font-size:13px;font-weight:700;color:#6A7385">{H.escape(tt)}</div>'
                f'<div style="transform:scale(.86);transform-origin:left top;margin-bottom:-8px">{body_}</div>' for tt, body_ in backup_parts) +
      '<span class="pg"></span></section>')

# reassemble
out = []
last = 0
for idx, m in enumerate(secs, 1):
    out.append(t[last:m.start()])
    out.append(new.get(idx, m.group(0)))
    last = m.end()
tail = t[last:]
out.append(bk if False else '')
res = ''.join(out)
# insert backup after the last section
res = res + bk + tail
open(OUT, 'w', encoding='utf-8').write(res)
print('slides edited', sorted(new), 'backup parts', len(backup_parts))
