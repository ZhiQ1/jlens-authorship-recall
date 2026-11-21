"""2026-11-20d style alignment of 10 newer slides of the Stage 1–13 HTML deck (user request 2026-11-20, step 1).
(Named 20261120d because .before_20261120c is already used by the v45 build.)

usage: build_20261120d_style.py SRC.html OUT.html
Slides are found by aria-label (robust to renumbering). Per slide:
  1. title  -> a conclusion sentence (verified wording; no code prefix; status stays in the badge), Caveat, size fitted to width
  2. bottom text blocks (How computed / bold conclusion / caveats) re-wrapped to 760 px so the right-hand corner is free
  3. a key-number sticky note (old 'note' style: yellow card, Caveat number) in the bottom-right corner; the number and caption
     repeat numbers already on the slide (verify script checks no number is added or lost)
  4. palette: target = blue, control = grey, conclusion = orange (only where the slide colours groups / the finding)
Contents-menu entries of these slides get the new titles. Nothing else changes.
"""
import re, sys, json, html
from pathlib import Path

BLUE, GREY, ORANGE, DGREY = '#3C78B4', '#8A94A6', '#D9772B', '#5B6474'

S = {  # aria-label: (new title, key number, caption, palette rule)
 'Exposure threshold (addendum 19)': (
   'Writing an author needs about 276× the exposure that recognising does',
   '276×', 'writing c50 ÷ recognition c50 · ρ = 276 [203, 390]', None),
 'Answer format (B), addendum 16': (
   'Only giving the first initial unlocks the name — format locks the rest',
   '+0.085', 'DiD A − B with the first initial (F4), Holm CI [+0.047, +0.124]; F1–F3 not significant', 'B'),
 'Name chain (D), addendum 16': (
   'A true co-author helps — through the co-author network, not this paper',
   '+0.167', 'G_A(1) with a true co-author; title-specific only +0.012 [−0.001, 0.025]', 'D'),
 'C: fabricated names (exploratory)': (
   'Made-up names are not confused neighbours: half are not in the data',
   '50.4%', 'not in the data, vs 50.5% for the shuffled baseline', 'C'),
 'Addendum 18b item 1: readout map': (
   'No clear earlier shelf: only small, scattered early traces',
   '+0.008 to +0.049', 'size of the cells that meet the rule (no multiplicity correction)', None),
 'Addendum 18b item 3: per-cell patching': (
   'By L52 the name positions carry most of the title’s signal',
   '0.835', 'carried by the name positions at L52 (0.605 at L48; whole tail 0.988)', 'I3'),
 'Addendum 18b item 2: windowed attention blocking': (
   'Name ← title carries the arrival in L44–L55; each cut costs ≤ 3.5%',
   '≤ 3.5%', 'of S per single edge cut; robust: 7 of 11 windows, same edge', None),
 'Addendum 18b item 6: MLP memory lookup': (
   'In L52–L56 the MLPs carry the paper, not yet the author’s name',
   '0.022–0.042', 'recovered by the 512 author-name directions vs 0.158–0.275 by the whole MLP', None),
 'Addendum 18b item 4: L57–L61 mean ablation': (
   'The MLPs, not attention, write the author signal in L57–L61',
   '+0.040', 'MLP − attention loss, mean L57–L61 [+0.036, +0.045]; attention ≤ 0.0012', 'I4'),
 'Addendum 18b item 5: title-token importance': (
   'Content words carry the signal by meaning: synonyms keep most of it',
   '0.374 vs 0.087', 'loss with random vs synonym content words (all of the signal: S = 0.328)', None),
}

CSS = """<style>
/* key-number note (2026-11-20d style alignment) */
.keyn{position:absolute;z-index:4;left:860px;width:340px;background:var(--note);color:var(--note-ink);padding:8px 16px 10px;
  box-shadow:2px 4px 10px rgba(0,0,0,.22);transform:rotate(-1deg);font-family:var(--hand)}
.keyn .kn{display:block;font-family:var(--title);font-weight:700;font-size:40px;line-height:1;color:#B54708;white-space:nowrap}
.keyn .kc{display:block;font-size:14px;line-height:1.22;margin-top:2px}
</style>"""

PX = {10.5: 5.35, 11.0: 5.6, 11.5: 5.9, 12.0: 6.4, 12.5: 6.7, 13.0: 7.4}   # px per char (13 = bold)
WRAP_W = 750


def mask(svg, names=('section tag', 'formula', 'badge')):
    keep = []
    def sub(m):
        keep.append(m.group(0)); return f'\x00{len(keep) - 1}\x00'
    for n in names:
        svg = re.sub(r'<g data-name="%s">.*?</g>' % re.escape(n), sub, svg, flags=re.S)
    return svg, keep


def unmask(svg, keep):
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], svg)


def recolor(svg, rule):
    body, keep = mask(svg)
    if rule == 'B':   # group A (target) orange -> blue, group B (control) blue -> grey; DiD / Holm labels stay orange (finding)
        def el(m):
            e = m.group(0)
            if e.startswith('<text') and re.search(r'>(DiD|Holm)', e): return e
            return e.replace(f'"{BLUE}"', '"@G@"').replace(f'"{ORANGE}"', f'"{BLUE}"').replace('"@G@"', f'"{GREY}"')
        body = re.sub(r'<(rect|text|line|circle|path)\b[^>]*>(?:[^<]*</text>)?', el, body)
    elif rule == 'D':   # A, C (target side) -> blue; B (control) -> grey; caption word follows
        body = body.replace(f'"{BLUE}"', '"@G@"').replace(f'"{ORANGE}"', f'"{BLUE}"').replace('"@G@"', f'"{GREY}"')
        body = body.replace('"#E9B27A"', '"#9DBBDD"')   # group C (target side, R1) light orange -> light blue
        body = body.replace('orange = true first author', 'blue = true first author')
    elif rule == 'C':   # chance markers -> grey (baseline)
        body = body.replace(f'"{BLUE}"', f'"{GREY}"')
    elif rule == 'I3':  # names (the finding) -> orange; ':' -> dark grey
        body = body.replace(f'"{ORANGE}"', '"@D@"').replace(f'"{BLUE}"', f'"{ORANGE}"').replace('"@D@"', f'"{DGREY}"')
        body = body.replace('rgba(60,120,180', 'rgba(@@').replace('rgba(217,119,43', 'rgba(91,100,116').replace('rgba(@@', 'rgba(217,119,43')
    elif rule == 'I4':  # attention (comparison) -> grey; MLP (finding) stays orange
        body = body.replace(f'"{BLUE}"', f'"{GREY}"')
    return unmask(body, keep)


def retitle(svg, title):
    m = re.search(r'(<text x="70\.0" y="\d+\.0" font-size=")(\d+)("[^>]*font-family="Caveat[^>]*font-weight="700">)(.*?)(</text>)', svg)
    assert m, 'title not found'
    old = html.unescape(m.group(4)); fs = int(m.group(2))
    fs_new = min(fs, int(1140 / (0.37 * len(title))))
    return svg[:m.start()] + m.group(1) + str(fs_new) + m.group(3) + html.escape(title, quote=False) + m.group(5) + svg[m.end():], old, fs, fs_new


def wrap(words, n):
    lines, cur = [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > n: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w) if cur else w
    if cur: lines.append(cur)
    return lines


def rewrap_bottom(svg):
    """re-wrap the multi-line bottom blocks (x=70, tspans) to WRAP_W and restack them; returns svg, bottom y."""
    pat = re.compile(r'<text(?P<a>[^>]*?) x="70\.0" y="(?P<y>[\d.]+)" font-size="(?P<fs>[\d.]+)"(?P<b>[^>]*)>(?P<inner>(?:<tspan[^>]*>.*?</tspan>)+)</text>', re.S)
    blocks = [m for m in pat.finditer(svg) if float(m.group('y')) >= 440]
    if not blocks: return svg, None
    out, pos, ycur, prev_end = [], 0, None, None
    for m in blocks:
        fs = float(m.group('fs')); spans = re.findall(r'<tspan x="70\.0" dy="([\d.]+)">(.*?)</tspan>', m.group('inner'), re.S)
        dys = [float(d) for d, _ in spans]; dy = max(dys[1:]) if len(dys) > 1 else round(fs * 1.28, 1)
        text = ' '.join(t for _, t in spans)
        bold = 'font-weight="700"' in (m.group('a') + m.group('b'))
        n = int(WRAP_W / (PX.get(13.0 if bold else fs, 0.47 * fs)))
        lines = wrap(text.split(' '), n)
        y0 = float(m.group('y'))
        if prev_end is not None:   # keep the original gap between blocks
            y0 = ycur + (y0 - prev_end)
        tsp = ''.join(f'<tspan x="70.0" dy="{0.0 if i == 0 else dy}">{l}</tspan>' for i, l in enumerate(lines))
        new = f'<text{m.group("a")} x="70.0" y="{y0:.1f}" font-size="{m.group("fs")}"{m.group("b")}>{tsp}</text>'
        out.append(svg[pos:m.start()]); out.append(new); pos = m.end()
        prev_end = float(m.group('y')) + (len(spans) - 1) * dy
        ycur = y0 + (len(lines) - 1) * dy
    out.append(svg[pos:])
    return ''.join(out), ycur


def main(src, dst):
    t = Path(src).read_text()
    rec = {'src': src, 'slides': {}}
    t = t.replace('</head>', CSS + '</head>', 1)
    for lab, (title, num, cap, rule) in S.items():
        m = re.search(r'<section class="slide mf" aria-label="%s">.*?</section>' % re.escape(lab), t, re.S)
        assert m, lab
        sec = m.group(0)
        sv = re.search(r'<svg .*?</svg>', sec, re.S); svg = sv.group(0)
        svg, old, fs, fs2 = retitle(svg, title)
        if rule: svg = recolor(svg, rule)
        svg, ybot = rewrap_bottom(svg)
        top = 574
        note = f'<div class="keyn" style="top:{top}px"><span class="kn">{html.escape(num)}</span><span class="kc">{html.escape(cap)}</span></div>'
        sec2 = sec[:sv.start()] + svg + note + sec[sv.end():]
        t = t[:m.start()] + sec2 + t[m.end():]
        # contents menu
        n_menu = t.count(f'<span class="toc-t">{html.escape(old, quote=False)}</span>')
        t = t.replace(f'<span class="toc-t">{html.escape(old, quote=False)}</span>', f'<span class="toc-t">{html.escape(title, quote=False)}</span>')
        rec['slides'][lab] = dict(old_title=old, new_title=title, font=[fs, fs2], palette=rule, key=num, bottom_y=ybot, menu_hits=n_menu)
        print(lab, '|', old, '->', title, '| font', fs, '->', fs2, '| bottom', ybot, '| menu', n_menu)
    Path(dst).write_text(t)
    json.dump(rec, open(Path(__file__).with_suffix('.json'), 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main(*sys.argv[1:3])
