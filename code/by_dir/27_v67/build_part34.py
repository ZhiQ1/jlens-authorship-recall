"""v67 agent B: Part 3 (H1) + Part 4 (H2) new-page fragments -> fragments/<slot>.html (standalone <section>s).
Data: summary files listed in BRIEF.md; every number is read from those files (see part34_numbers.md)."""
import sys, json, re, csv, html as H
from pathlib import Path
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/normalise_sample_20261122b')
from addonly_lib import tex, fxu, circ_svg, vline_svg, band_svg, INK, PEN, BLUE, ORANGE, RED, GREEN, HAND
import pandas as pd

W = Path('/home/zhang.zhiqi2/jlens_work/27_v67'); FR = W / 'fragments'; FR.mkdir(exist_ok=True, parents=True)
G = Path('/scratch/zhang.zhiqi2/jlens/391_groups'); S13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
TOK = json.load(open(W / 'toks.json'))
GREYC = '#8a8f98'; CTRL = '#6A7385'; GOLD = '#B8860B'
NOTO = "font-family=\"'Noto Sans SC','PingFang SC',system-ui,sans-serif\""
NUM = []   # (number text, source)
def num(x, src, fmt='{:+.3f}'):
    s = fmt.format(x).replace('-', '−'); NUM.append((s, src)); return s
def ci(lo, hi, src, fmt='{:+.3f}'):
    s = '[' + fmt.format(lo).replace('-', '−') + ', ' + fmt.format(hi).replace('-', '−') + ']'; NUM.append((s, src)); return s

# ------------------------------------------------------------------ html helpers
TAGS = {'settled': ('settled', 'settled'), 'lsup': ('lsup', 'locked · supported'), 'lnot': ('lnot', 'locked · not supported'),
        'desc': ('desc', 'descriptive'), 'expl': ('expl', 'exploratory'), 'rev': ('lnot', 'locked · reversed'),
        'marg': (None, 'marginal'), 'lrule': ('lsup', 'locked rule'), 'bord': ('desc', 'borderline')}
def tg(k, txt=None):
    c, t = TAGS[k]
    if c is None: return f'<span class="tg" style="background:{GOLD}">{txt or t}</span>'
    return f'<span class="tg {c}">{txt or t}</span>'
def section(slot, title, part, ask, body, so, so_kind='this slide'):
    plain = re.sub(r'<[^>]+>', '', title)
    return (f'<section class="slide mf" data-slot="{slot}" aria-label="{H.escape(plain)}">'
            f'<span class="tag" style="display:none">{H.escape(plain)}</span>'
            f'<div class="lead">{part}</div>'
            f'<h2 style="position:absolute;left:70px;top:34px;font-size:34px;line-height:1.05;max-width:1140px;color:{INK}">{title}</h2>'
            f'<p class="askl abs" style="left:70px;top:80px;width:1140px;color:#22304A"><b>Now asking:</b> {ask}</p>'
            + body +
            f'<div class="soln" style="left:70px;top:672px;width:1140px"><b>So ({so_kind}):</b> {so}</div>'
            '</section>')
def cats(left, top, width, items, fs=14.5):
    out = f'<div class="cats" style="left:{left}px;top:{top}px;width:{width}px;font-size:{fs}px">'
    for it in items:
        if isinstance(it, tuple): k, v = it; out += f'<div class="it"><span class="k">{k}:</span> {v}</div>'
        else: out += f'<div class="it">{it}</div>'
    return out + '</div>'
def svgwrap(inner, left=0, top=0, w=1280, h=720):
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="position:absolute;left:{left}px;top:{top}px;z-index:2;overflow:visible" '
            f'xmlns="http://www.w3.org/2000/svg">{inner}</svg>')
def T(x, y, s, fs=14, col=INK, anchor='start', bold=False, hand=True, extra=''):
    f = HAND if hand else NOTO; fw = ' font-weight="700"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{col}" text-anchor="{anchor}" {f}{fw} {extra}>{H.escape(s)}</text>'
def q(x, y, n, col=ORANGE):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}"/>'
            f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="12" fill="#fff" text-anchor="middle" font-family="sans-serif" font-weight="700">{n}</text>')
def tokens(x, y, toks, fills=None, outlines=None, fs=11.5, h=24, label=None, gap=2, maxw=None):
    """real Qwen3 tokens as boxes; fills/outlines: {index: colour}. returns (svg, list of (x0,x1) per token, total width)"""
    fills = fills or {}; outlines = outlines or {}; out = []; pos = []; cx = x
    for i, t in enumerate(toks):
        disp = t.replace('\n', '↵').replace(' ', '·') if t.strip() == '' or '\n' in t else t.replace(' ', '·', 1) if t.startswith(' ') else t
        w = max(16, 6.6 * len(disp) * fs / 11.5 + 8)
        f = fills.get(i, '#FFFFFF'); o = outlines.get(i, '#c9ced6'); sw = 2.2 if i in outlines else 1
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="{f}" stroke="{o}" stroke-width="{sw}"/>')
        out.append(f'<text x="{cx+w/2:.1f}" y="{y+h/2+4:.1f}" font-size="{fs}" fill="{INK}" text-anchor="middle" font-family="monospace">{H.escape(disp)}</text>')
        pos.append((cx, cx + w)); cx += w + gap
    if label: out.append(T(x - 8, y + h / 2 + 5, label, 13, PEN, 'end', True))
    return ''.join(out), pos, cx - x

# ------------------------------------------------------------------ chart helpers
class Ax:
    def __init__(s, x0, y0, w, h, xmin, xmax, ymin, ymax): s.__dict__.update(locals())
    def X(s, v): return s.x0 + (v - s.xmin) / (s.xmax - s.xmin) * s.w
    def Y(s, v): return s.y0 + s.h - (v - s.ymin) / (s.ymax - s.ymin) * s.h
    def frame(s, xt, yt, xlab='', ylab='', yfmt='{:g}', xfmt='L{:g}'):
        o = []
        for v in yt:
            o.append(f'<line x1="{s.x0}" y1="{s.Y(v):.1f}" x2="{s.x0+s.w}" y2="{s.Y(v):.1f}" stroke="#E7DADA" stroke-dasharray="3 4"/>')
            o.append(T(s.x0 - 6, s.Y(v) + 4, yfmt.format(v).replace('-', '−'), 12.5, PEN, 'end'))
        for v in xt:
            o.append(f'<line x1="{s.X(v):.1f}" y1="{s.y0+s.h}" x2="{s.X(v):.1f}" y2="{s.y0+s.h+5}" stroke="{INK}" stroke-width="1.4"/>')
            o.append(T(s.X(v), s.y0 + s.h + 18, xfmt.format(v) if isinstance(xfmt, str) else xfmt(v), 12.5, PEN, 'middle'))
        o.append(f'<line x1="{s.x0}" y1="{s.y0+s.h}" x2="{s.x0+s.w}" y2="{s.y0+s.h}" stroke="{INK}" stroke-width="1.8"/>')
        o.append(f'<line x1="{s.x0}" y1="{s.y0}" x2="{s.x0}" y2="{s.y0+s.h}" stroke="{INK}" stroke-width="1.4"/>')
        if xlab: o.append(T(s.x0 + s.w / 2, s.y0 + s.h + 34, xlab, 12.5, PEN, 'middle'))
        if ylab: o.append(f'<text x="{s.x0-40}" y="{s.y0+s.h/2}" font-size="12.5" fill="{PEN}" text-anchor="middle" {HAND} transform="rotate(-90 {s.x0-40} {s.y0+s.h/2})">{H.escape(ylab)}</text>')
        return ''.join(o)
    def line(s, xs, ys, col, lo=None, hi=None, dash='', sw=2.6, mk=True):
        o = []
        if lo is not None:
            pts = [(s.X(x), s.Y(v)) for x, v in zip(xs, hi)] + [(s.X(x), s.Y(v)) for x, v in reversed(list(zip(xs, lo)))]
            o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{col}" fill-opacity="0.15"/>')
        da = f' stroke-dasharray="{dash}"' if dash else ''
        o.append(f'<polyline points="{" ".join(f"{s.X(x):.1f},{s.Y(v):.1f}" for x, v in zip(xs, ys))}" fill="none" stroke="{col}" stroke-width="{sw}"{da}/>')
        if mk: o += [f'<circle cx="{s.X(x):.1f}" cy="{s.Y(v):.1f}" r="3.6" fill="#fff" stroke="{col}" stroke-width="2"/>' for x, v in zip(xs, ys)]
        return ''.join(o)
    def hline(s, v, col=GREYC, lab='', dash='5 4'):
        return (f'<line x1="{s.x0}" y1="{s.Y(v):.1f}" x2="{s.x0+s.w}" y2="{s.Y(v):.1f}" stroke="{col}" stroke-width="1.6" stroke-dasharray="{dash}"/>'
                + (T(s.x0 + s.w - 4, s.Y(v) - 5, lab, 12, col, 'end', True) if lab else ''))

def rd(path): return list(csv.DictReader(open(path)))

# ============================================================== PART 3 · H1
P3 = 'Part 3 · Read early: the question and the title (H1)'
TA = TOK['authors']; TY = TOK['year']; TF = TOK['field']

def h1_question():
    o = []
    # schematic: same title under three questions, ':' highlighted
    qfill = {i: '#EEF1F5' for i in range(8)}; tfill = {i: '#FFF1DE' for i in range(9, 20)}
    y = 150
    for lab, tk, nq in (('authors', TA, 8), ('year', TY, 8), ('field', TF, 8)):
        f = {**{i: '#EEF1F5' for i in range(len(tk)) if i not in range(9, 20)}, **{i: '#FFF1DE' for i in range(9, 20)}}
        f[len(tk) - 1] = '#FBE3E1'
        s, pos, w = tokens(150, y, tk, f, {len(tk) - 1: ORANGE}, fs=10.5, h=22, label=lab)
        o.append(s); y += 34
    o.append(T(150, 142, 'same title, three questions (real Qwen3 tokens) · grey = question words · orange = title · red box = ":" where the answer starts', 12.5, PEN))
    o.append(T(150, 268, 'H1 says: by the middle layers the ":" state already encodes "output an author list".', 15, INK, bold=True))
    sv = svgwrap(''.join(o))
    card = ('<div class="card2" style="position:absolute;left:70px;top:290px;width:540px;z-index:4">'
            '<h4>If H1 holds, we expect</h4>'
            + cats(0, 0, 0, [], 0)[:0] +
            '<div style="font-family:var(--hand);font-size:15px;line-height:1.3;color:#22304A">'
            '<span class="q">1</span> the ":" state moves <b>more</b> when the question changes than when the paper changes<br>'
            '<span class="q">2</span> a knockout of the question words <b>before</b> a middle layer changes the answer type, <b>after</b> it does not<br>'
            '<span class="q">3</span> swapping the ":" state between questions switches the answer type from that middle layer on</div></div>'
            '<div class="card2" style="position:absolute;left:650px;top:290px;width:560px;z-index:4;border-color:#C84A3E">'
            '<h4>If H1 fails, we expect</h4>'
            '<div style="font-family:var(--hand);font-size:15px;line-height:1.3;color:#22304A">'
            '<span class="q">1</span> the ":" state moves as much for a new paper as for a new question<br>'
            '<span class="q">2</span> the answer type can still be changed <b>late</b> (after L48)<br>'
            '<span class="q">3</span> no layer where the format is <span class="mk">locked in</span></div></div>')
    tests = cats(70, 470, 1140, [
        ('Tests in this part', '<span class="q">1</span> distance ratio at ":" → slide {{new:h1-colon-ratio}} · <span class="q">2</span> format-locking knockout '
         '(pre-registered) + supplementary attention-sink checks → slide {{new:h1-format}} · <span class="q">3</span> ":" swap at L56 → slide {{new:h1-format}}'),
        ('Earlier pages', 'same title, different question → slide {{p:81}} · layer order → slide {{p:71}} · ratio curves in full → slide {{p:118}}'),
        ('Caveat', '<span class="ul">only the authors question gives a usable format measure; year/field answers are too often wrong at baseline</span>')], 14.5)
    body = sv + card + tests + f'<div class="note-h" style="left:930px;top:34px">question card · H1 {tg("lrule", "hypothesis")}</div>'
    return section('h1-question', 'Question card · H1: is the answer format set in the middle layers?', P3,
                   'what would we see if the middle layers mainly encode the task ("output an author list")?', body,
                   'three predictions, three tests; the verdict card at the end of this part scores each one.')

def h1_colon_ratio():
    d = pd.read_csv(S13 / 'summary_m3/x1_similarity.csv'); d = d[d.pos == 'colon']
    g = d.groupby('layer')[['reldist_same_paper', 'reldist_diff_paper', 'question_share']].mean().reset_index()
    src = '381_stage13/summary_m3/x1_similarity.csv (colon, mean over 3 question pairs; = slide B22)'
    L = g.layer.tolist(); R = g.question_share.tolist()
    o = []
    # method schematic (top): numerator vs denominator
    s1, p1, _ = tokens(150, 132, TA, {len(TA) - 1: '#FBE3E1', **{i: '#EEF1F5' for i in range(8)}}, {len(TA) - 1: ORANGE}, fs=10, h=20, label='paper A · authors')
    s2, p2, _ = tokens(150, 158, TY, {len(TY) - 1: '#FBE3E1', **{i: '#EEF1F5' for i in range(8)}}, {len(TY) - 1: ORANGE}, fs=10, h=20, label='paper A · year')
    o += [s1, s2, T(p2[-1][1] + 14, 162, 'numerator: same paper, new question', 13.5, BLUE, bold=True)]
    s3, p3, _ = tokens(150, 196, TOK['false0'], {len(TOK['false0']) - 1: '#FBE3E1', **{i: '#EEF1F5' for i in range(8)}}, {len(TOK['false0']) - 1: ORANGE}, fs=10, h=20, label='paper B · authors')
    o += [s3, T(p3[-1][1] + 14, 211, 'denominator: new paper, same question (vs paper A · authors)', 13.5, CTRL, bold=True)]
    o.append(T(150, 238, 'd = ‖state(":") − state′(":")‖ / ‖state(":")‖ at every layer; ratio = mean d(numerator) / mean d(denominator)', 12.5, PEN))
    ax = Ax(130, 268, 560, 300, 0, 63, 0, 5.2)
    o.append(ax.frame([0, 8, 16, 24, 32, 40, 48, 56, 63], [0, 1, 2, 3, 4, 5], 'layer', 'ratio'))
    o.append(band_svg(ax.X(52), ax.X(63), ax.Y(5.2), ax.Y(0), 'denominator grows from L52', ORANGE, 0.10))
    o.append(ax.hline(1, GREYC, '')); o.append(T(ax.X(20), ax.Y(1) - 6, 'ratio = 1: both move the same', 12, GREYC, 'start', True))
    o.append(ax.line(L, R, BLUE))
    marks = [(4, '①'), (40, '②'), (48, '③'), (56, '④')]
    for (l, m), k in zip(marks, range(4)):
        v = float(g[g.layer == l].question_share.iloc[0]); x, y = ax.X(l), ax.Y(v)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="{ORANGE}" stroke-width="3"/>')
        o.append(T(x + 12, y + 22, f'{num(v, src, "{:.1f}")}×', 15, ORANGE, bold=True)); o.append(q(x - 2, y - 24, k + 1))
    o.append(T(ax.X(30), ax.Y(4.6), 'a new question moves ":" more', 13.5, BLUE, 'middle', True))
    sv = svgwrap(''.join(o))
    v4 = g[g.layer == 4].iloc[0]; v56 = g[g.layer == 56].iloc[0]
    c = cats(740, 262, 470, [
        ('Method', 'state at ":" (where the answer starts) for 9,108 papers under three questions; distances relative to the state\'s length'),
        ('Result', f'<span class="q">1</span> at L4 a new question moves ":" <b>{num(v4.question_share, src, "{:.1f}")}×</b> as far as a new paper '
                   f'({num(v4.reldist_same_paper, src, "{:.3f}")} vs {num(v4.reldist_diff_paper, src, "{:.3f}")}); <span class="q">2</span> '
                   f'<b>{num(float(g[g.layer==40].question_share.iloc[0]), src, "{:.1f}")}×</b> at L40, <span class="q">3</span> '
                   f'<b>{num(float(g[g.layer==48].question_share.iloc[0]), src, "{:.1f}")}×</b> at L48'),
        ('Control', 'the denominator (new paper, same question) is the yardstick: ratio = 1 means the question matters no more than the paper'),
        ('Caveat', f'<span class="ul"><span class="q">4</span> from L52 the denominator grows ({num(v56.reldist_diff_paper, src, "{:.3f}")} at L56), so the ratio falls '
                   f'to {num(v56.question_share, src, "{:.1f}")}× although the numerator stays high ({num(v56.reldist_same_paper, src, "{:.3f}")})</span>; '
                   'a distance says the state differs, not what it encodes'),
        ('Fits H1?', '<span class="mk">prediction 1 holds</span>: ":" is organised by the question through L48 ' + tg('desc'))], 14)
    f = fxu(130, 604, 600, [r'$\mathrm{ratio}(l)=\overline{d}_{\,\mathrm{new\ question}}(l)\,/\,\overline{d}_{\,\mathrm{new\ paper}}(l),\ \ d=\Vert a-b\Vert/\Vert a\Vert$'],
            r'$n=\mathrm{9{,}108\ papers\ \times\ 3\ question\ pairs}$', keys=['ratio > 1: a new question moves the ":" state more than a new paper'])
    return section('h1-colon-ratio', 'At ":", a new question moves the state more than a new paper — until L48', P3,
                   'is the ":" state organised by the question (H1, prediction 1)?', sv + c + f,
                   'the ":" state tracks the question 2–5× more than the paper up to L48 (descriptive); whether the format is <i>fixed</i> there is the next test.')

def h1_format():
    a = pd.read_csv(G / 'summary_a23/a23_table.csv'); s = pd.read_csv(G / 'summary_a23_supp/a23_supp_table.csv')
    srcA = '391_groups/summary_a23/a23_table.csv (K_isolated, K2; authors)'; srcS = '391_groups/summary_a23_supp/a23_supp_table.csv'
    ki = a[(a.kind == 'K_isolated') & (a.task == 'authors')].sort_values('layer')
    kg = s[(s.kind == 'K_gentle') & (s.task == 'authors')].sort_values('layer'); ks = s[(s.kind == 'K_sink_only') & (s.task == 'authors')].sort_values('layer')
    o = []
    # schematic: three knockouts on real tokens
    n = len(TA); colon = n - 1; title = list(range(9, 20)); qw = [i for i in range(n) if i not in title and i != colon]
    rows = [('locked test', {colon}, 'from layer l, ":" sees only itself (position 0 cut too)'),
            ('gentle', set(title) | {0, colon}, 'question words blocked; title + position 0 visible'),
            ('sink only', {0, colon}, '":" sees itself + position 0 (the attention sink)')]
    y = 128
    for lab, vis, note in rows:
        f = {i: ('#E8F0FA' if i in vis else '#F3F3F3') for i in range(n)}; f[colon] = '#FBE3E1'
        outl = {i: '#C84A3E' for i in range(n) if i not in vis}; outl[colon] = ORANGE
        sv_, pos, w = tokens(170, y, TA, f, outl, fs=9.5, h=19, label=lab)
        o.append(sv_); o.append(T(170 + w + 10, y + 14, note, 12.5, PEN)); y += 27
    o.append(T(170, 122, 'blue = ":" may attend · red outline = blocked from layer l to the end · position 0 = "Who" (takes 0.62–0.92 of ":" attention from L8)', 12, PEN))
    NUM.append(('0.62–0.92', '391_groups/summary_a23_supp/report.md (sink diagnostic, ":" attention on position 0)'))
    ax = Ax(130, 248, 520, 300, 4, 64, 0, 1.0)
    xt = [4, 8, 16, 24, 32, 40, 48, 56, 64]
    o.append(ax.frame(xt, [0, 0.25, 0.5, 0.75, 1.0], 'knockout from layer (64 = nothing blocked)', 'K: answer type kept', '{:.2f}', lambda v: 'none' if v == 64 else f'L{v}'))
    o.append(band_svg(ax.X(22), ax.X(42), ax.Y(1.0), ax.Y(0), '', RED, 0.08)); o.append(T(ax.X(32), ax.Y(0.04), 'dip only when position 0 is cut', 12.5, RED, 'middle', True))
    o.append(ax.line(ki.layer, ki.est, RED, ki.lo, ki.hi))
    o.append(ax.line(ki.layer, ki.K2, '#B54708', dash='6 4', mk=True))
    o.append(ax.line(kg.layer, kg.est, BLUE, kg.lo, kg.hi))
    o.append(ax.line(ks.layer, ks.est, GREEN, dash='2 3'))
    k56 = ki[ki.layer == 56].iloc[0]
    o.append(circ_svg(ax.X(56), ax.Y(k56.est), '', '1', ORANGE, 4, 40))
    o.append(T(ax.X(50), ax.Y(0.70), 'L56 locked rule', 13.5, ORANGE, 'start', True))
    o.append(T(ax.X(50), ax.Y(0.70) + 17, f'{num(k56.est, srcA, "{:.2f}")} {ci(k56.lo, k56.hi, srcA, "{:.2f}")}', 13.5, ORANGE, 'start', True))
    o.append(T(ax.X(30), ax.Y(0.30), 'locked test', 13.5, RED, 'middle', True))
    o.append(T(ax.X(12), ax.Y(0.52), 'locked secondary', 13, '#B54708', 'start', True))
    o.append(T(ax.X(4) + 4, ax.Y(1.0) - 8, 'gentle ≈ sink only ≈ 1.00 from L4', 13.5, BLUE, 'start', True))
    o.append(q(ax.X(30), ax.Y(0.12), 2))
    sv = svgwrap(''.join(o))
    a26 = pd.read_csv(G / 'summary_a26/a26_primary.csv'); src26 = '391_groups/summary_a26/a26_primary.csv'
    y56 = a26[a26.donor == 'year'].iloc[0]; f56 = a26[a26.donor == 'field'].iloc[0]
    base = s[s.kind == 'content_baseline_acc'].set_index('task')
    sw = a[(a.kind == 'S_switch')]
    sy = sw[(sw.task == 'year>authors') & (sw.layer == 48)].iloc[0]
    c = cats(690, 238, 520, [
        ('Method', 'knock out what ":" may read, from layer l to the end; K = share of papers whose first answer token stays a name (582 papers)'),
        ('Result (locked)', f'<span class="q">1</span> the pre-registered rule gives <b>L56</b> ({num(k56.est, srcA, "{:.2f}")}) ' + tg('lrule')
                            + ' — but the curve is not monotonic: K is 1.00 at L16 and falls to '
                            + f'{num(float(ki[ki.layer==40].est.iloc[0]), srcA, "{:.2f}")} at L40'),
        ('Supplement', '<span class="q">2</span> the dip appears <span class="mk">only when position 0 is cut</span>; keeping it (gentle, sink only) keeps the '
                       'names answer type from L4 ' + tg('expl')),
        ('Patching', f'swap the ":" state: the year prompt switches to names from L48 ({num(sy.est, srcA, "{:.2f}")}), field from L40 → L40–L56'),
        ('Gate (locked)', f'swapping ":" at L56 lowers the author signal: year {num(y56.dspec, src26)} {ci(y56.lo, y56.hi, src26)}, '
                          f'field {num(f56.dspec, src26)} {ci(f56.lo, f56.hi, src26)} ' + tg('lsup')),
        ('Caveat', '<span class="ul">names are the default answer type, so "kept" is partly a default; year/field answers are right too rarely at baseline '
                   f'({num(base.loc["year","est"], srcS, "{:.2f}")} / {num(base.loc["field","est"], srcS, "{:.2f}")} &lt; 0.90) to test</span>')], 13.2)
    f = fxu(130, 600, 520, [r'$K(l)=\frac{1}{n}\sum_i \mathbf{1}[\,\mathrm{first\ answer\ token}_i\in\mathrm{names}\ \mid\ \mathrm{knockout\ from}\ l\,]$'],
            r'$n=\mathrm{582\ papers\ (288\ target,\ 294\ control)}$', keys=['K ≈ 1: the answer type survives the knockout'])
    return section('h1-format', 'When is the answer format fixed? The layer is not pinned down', P3,
                   'from which layer is the "author list" format locked in (H1, predictions 2 and 3)?', sv + c + f,
                   'the locked rule gives L56, but its main test is distorted by cutting the attention sink; with the sink kept the names format holds from L4 — '
                   '<span class="mk">the format layer is not pinned down</span>; the ":" state does gate the author signal at L56.')

def verdict_card(slot, hyp, title, part, ask, rows, verdict_html, open_items, so, schematic=''):
    tbl = ('<table class="hx2" style="position:absolute;left:70px;top:190px;width:700px;border-collapse:collapse;z-index:4;font-family:var(--hand);font-size:14px">'
           '<tr style="border-bottom:2px solid #22304A"><th style="text-align:left;width:34%">Prediction</th><th style="text-align:left;width:36%">Result</th>'
           '<th style="text-align:left">Strength</th><th style="text-align:left">Slides</th></tr>')
    for p, r, st, sl, colr in rows:
        tbl += (f'<tr style="border-bottom:1px solid #E7DADA;background:{colr}"><td>{p}</td><td>{r}</td><td>{st}</td><td>{sl}</td></tr>')
    tbl += '</table>'
    v = (f'<div class="card2" style="position:absolute;left:800px;top:186px;width:410px;z-index:4;border-color:#D9772B">'
         f'<h4>Verdict · {hyp}</h4><div style="font-family:var(--hand);font-size:15px;line-height:1.28;color:#22304A">{verdict_html}</div></div>')
    op = cats(800, 500, 410, [('Open', '<br>'.join(open_items))], 14)
    return section(slot, title, part, ask, tbl + v + op + schematic, so, 'section')

def h1_verdict():
    rows = [('① ":" moves more for a new question than for a new paper', '<b>holds</b> to L48 (4.7× → 2.2×)', tg('desc'), '{{new:h1-colon-ratio}}', '#EAF6EC'),
            ('② knockout before a middle layer changes the answer type', '<b>not shown</b>: locked rule L56, but the test is distorted by cutting the sink; with the sink kept the type holds from L4',
             tg('lrule', 'locked rule') + ' ' + tg('expl', 'supplement: exploratory'), '{{new:h1-format}}', '#FFF1D6'),
            ('③ ":" swap switches the answer type from a middle layer', 'switches from L40–L48; the ":" state gates the author signal at L56', tg('lsup'), '{{new:h1-format}}', '#EAF6EC'),
            ('— question-only tests separate meaning from identity', '<b>no</b>: the title state is the same under every question (ceiling)', tg('expl'), '{{p:81}}, {{new:ceiling}}', '#F3F3F3')]
    for s_ in ('4.7×', '2.2×'): NUM.append((s_, 'slide {{new:h1-colon-ratio}} / B22'))
    vh = ('<b>Revised.</b> The ":" position tracks the question, but <span class="mk">the layer where the answer format is fixed is not pinned down</span>. '
          'The locked rule gives L56; its main test is non-monotonic and likely distorted by cutting attention sinks; the patching test points to L40–L56. '
          'The format gates the author signal at L56.')
    op = ['year / field: a measure the model gets right at baseline', '<span class="ul">"names" is the default answer type — a default, not proof of a set format</span>']
    o = [T(70, 452, 'Where each H1 result sits along the layers', 15, INK, bold=True)]
    ax = Ax(110, 470, 640, 150, 0, 63, 0, 5)
    for l in (0, 8, 16, 24, 32, 40, 48, 56, 63):
        o.append(f'<line x1="{ax.X(l):.1f}" y1="470" x2="{ax.X(l):.1f}" y2="624" stroke="#E7DADA" stroke-dasharray="3 4"/>'); o.append(T(ax.X(l), 640, f'L{l}', 12, PEN, 'middle'))
    bars = [(4, 48, BLUE, '":" tracks the question (ratio > 1)', 1.0, ''), (40, 56, GREEN, 'swap switches the answer type', 1.0, ''),
            (4, 63, GREYC, 'sink kept: names type holds from L4 (exploratory)', 0.6, '5 4')]
    y = 484
    for x0, x1, col, lab, opa, da in bars:
        o.append(f'<rect x="{ax.X(x0):.1f}" y="{y}" width="{ax.X(x1)-ax.X(x0):.1f}" height="16" rx="5" fill="{col}" fill-opacity="{0.8*opa}"' + (f' stroke="{col}" stroke-dasharray="{da}"' if da else '') + '/>')
        o.append(T(ax.X(x0) + 6, y + 13, lab, 12.5, '#fff' if not da else INK, 'start', True)); y += 26
    o.append(f'<line x1="{ax.X(56):.1f}" y1="{y}" x2="{ax.X(56):.1f}" y2="{y+40}" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="5 3"/>')
    o.append(T(ax.X(56) - 6, y + 16, 'locked rule L56 — likely a sink artefact ?', 12.5, ORANGE, 'end', True))
    o.append(T(ax.X(56) - 6, y + 34, 'gate: ":" swap at L56 lowers the author signal (locked)', 12.5, '#2E7D46', 'end', True))
    sch = svgwrap(''.join(o))
    return verdict_card('h1-verdict', 'H1', 'Verdict card · H1: the question is read, the format layer stays open', P3,
                        'what did the H1 tests show, and how strong is each result?', rows, vh, op,
                        'H1 is revised — the question is read at ":", but no middle layer is shown to fix the format. '
                        '<b>Next (Part 4):</b> if the middle layers do not hold the format, do they hold <i>which paper</i> this is?', sch)

MATRIX_COLS = ['Prediction tested', 'Main test', 'Result', 'Strength', 'Slides']
def matrix(slot, title, part, upto, so):
    R = [('H1 · format in the middle layers', '":" tracks the question', 'distance ratio', 'holds to L48', tg('desc'), '{{new:h1-colon-ratio}}', '#EAF6EC', 1),
         ('', 'format fixed at a middle layer', 'format-locking knockout', 'not pinned down (sink artefact)', tg('lrule', 'locked rule') + tg('expl', 'supplement'), '{{new:h1-format}}', '#FFF1D6', 1),
         ('', '":" gates the author signal', '":" swap at L56', 'yes', tg('lsup'), '{{new:h1-format}}', '#EAF6EC', 1),
         ('H2 · paper identity', 'made-up title cannot replace the real one', 'made-up-title test', '75% recovered → mostly meaning', tg('lsup'), '{{p:85}}', '#FBE3E1', 2),
         ('', 'extra larger for recognised / cited papers', 'rewrite test', 'not larger / reversed', tg('lnot') + tg('rev'), '{{new:recog-citations}}', '#FBE3E1', 2),
         ('', 'identity explains the state beyond text', 'variance split', '≈ 0 (meaning does)', tg('lsup', 'locked') , '{{new:variance}}', '#FBE3E1', 2),
         ('', 'extra sits on specific words', 'rare-word test', 'rare 0.162 vs common 0.027', tg('lsup'), '{{new:rare-words}}', '#EAF6EC', 2),
         ('', 'a paper-specific signal beyond topic', 'surname test at L8', 'small exception (T2, T3 marginal)', tg('lsup') + tg('marg'), '{{new:h2-exception}}', '#FFF1D6', 2),
         ('H3 · present, not in vocabulary directions', '→ Part 5', '', '', '', '{{new:h3-question}}', '#FFFFFF', 3),
         ('Writing step (bottleneck)', '→ Part 6', '', '', '', '{{new:w-question}}', '#FFFFFF', 4)]
    t = ('<table class="hx2" style="position:absolute;left:70px;top:130px;width:1140px;border-collapse:collapse;z-index:4;font-family:var(--hand);font-size:14px">'
         '<tr style="border-bottom:2px solid #22304A"><th style="text-align:left;width:19%">Hypothesis</th><th style="text-align:left;width:22%">Prediction tested</th>'
         '<th style="text-align:left;width:16%">Main test</th><th style="text-align:left;width:19%">Result</th><th style="text-align:left;width:15%">Strength</th><th style="text-align:left">Slides</th></tr>')
    for hy, p, te, r, st, sl, col, k in R:
        if k > upto:
            if hy: t += f'<tr style="border-bottom:1px solid #E7DADA;color:#8a8f98"><td><b>{hy}</b></td><td colspan="4">tested in a later part</td><td>{sl}</td></tr>'
            continue
        t += f'<tr style="border-bottom:1px solid #E7DADA;background:{col}"><td><b>{hy}</b></td><td>{p}</td><td>{te}</td><td>{r}</td><td>{st}</td><td>{sl}</td></tr>'
    t += '</table>'
    key = ('<div class="note-h" style="left:70px;top:612px">cell colour: <span style="background:#EAF6EC;padding:0 6px">prediction holds</span> '
           '<span style="background:#FFF1D6;padding:0 6px">partly / not pinned down</span> <span style="background:#FBE3E1;padding:0 6px">prediction fails</span></div>')
    for s_ in ('75%', '0.162', '0.027'): NUM.append((s_, 'slides {{p:85}} / {{new:rare-words}}'))
    return section(slot, title, part, 'which predictions have been tested so far, and what did they show?', t + key, so, 'section')

def matrix_c(slot, upto, title, ask, so, part_tag):
    """agent C's matrix layout (fragments/h3-matrix.html): same columns and rows; rows tested later are greyed out."""
    src = (FR / 'h3-matrix.html').read_text()
    later = {2: 'Part 4', 3: 'Part 5', 4: 'Part 5', 5: 'Part 6', 6: 'Part 6'}
    grey = ('<td style="padding:4px 6px;background:#FFFFFF;border:1px solid #fff;color:#C9CED6;font-size:12px;line-height:1.25;vertical-align:top">{}</td>')
    tb = re.search(r'<table.*?</table>', src, re.S).group(0)
    rows = re.findall(r'<tr>.*?</tr>', tb, re.S); new = [rows[0]]
    for k, r in enumerate(rows[1:], 1):
        tds = re.findall(r'<td.*?</td>', r, re.S)
        if k <= upto:
            hd = re.findall(r'<td.*?</td>', r, re.S)[0]
            r = r.replace(hd, re.sub(r'background:[^;"]+;?', '', hd), 1)
            rr = r if k != upto else r.replace('<tr>', '<tr style="outline:2.5px solid #D9772B;outline-offset:-1px">', 1)
        else:
            nb = lambda s: re.sub(r'background:[^;"]+;?', '', s)
            rr = '<tr style="opacity:.55">' + nb(tds[0]) + nb(tds[1]) + ''.join(grey.format('later part') for _ in tds[2:-1]) + grey.format('tested in ' + later[k]) + '</tr>'
        new.append(rr)
    out = src.replace(tb, tb[:tb.index('<tr>')] + ''.join(new) + '</table>')
    out = re.sub(r'data-slot="h3-matrix"', f'data-slot="{slot}"', out)
    out = out.replace('Evidence matrix after Part 5', title).replace('Evidence so far: H3 and the route are now filled in', title)
    out = out.replace('Part 5 · route + H3', part_tag)
    out = re.sub(r'(<p class="askl abs"[^>]*><b>Now asking:</b>).*?</p>', lambda m: m.group(1) + ' ' + ask + '</p>', out, flags=re.S)
    out = re.sub(r'(<div class="soln"[^>]*><b>So \(section\):</b>).*?</div>', lambda m: m.group(1) + ' ' + so + '</div>', out, flags=re.S)
    out = re.sub(r'id="h3matrix(\w)"', lambda m: f'id="{slot.replace("-","")}{m.group(1)}"', out)
    out = re.sub(r'url\(#h3matrix(\w)\)', lambda m: f'url(#{slot.replace("-","")}{m.group(1)})', out)
    return out

def h1_matrix():
    return matrix_c('h1-matrix', 1, 'Evidence so far: the H1 row is filled in', 'with Part 3 done, where does each hypothesis stand?',
                    'H1 row filled: the question is read at ":", the format layer is not pinned down. <b>Next:</b> H2 — is what the model reads from the title <i>this paper</i>, or its meaning?',
                    'Part 3 · H1')

def h2_matrix():
    return matrix_c('h2-matrix', 2, 'Evidence so far: H1 and H2 are filled in', 'with Part 4 done, where does each hypothesis stand?',
                    'H1 and H2 rows filled: question read, format layer open; meaning and specific words, not identity (one small exception). <b>Next:</b> the route and H3.',
                    'Part 4 · H2')

def _old_h1_matrix():
    return matrix('h1-matrix', 'Evidence matrix, after H1', P3, 1,
                  'H1 row filled: the question is read at ":", the format layer is not pinned down. <b>Next:</b> H2 — is what the model reads from the title <i>this paper</i>, or its meaning?')

# ============================================================== PART 4 · H2
P4 = 'Part 4 · What is read: meaning, not identity (H2)'

def h2_question():
    o = []
    s1, p1, w1 = tokens(170, 140, TOK['authors'], {i: '#FFF1DE' for i in range(9, 20)}, fs=10, h=21, label='real title')
    s2, p2, w2 = tokens(170, 170, TOK['fict'], {i: '#E8F0FA' for i in range(9, 18)}, fs=10, h=21, label='same meaning, made up (example)')
    s3, p3, w3 = tokens(170, 200, TOK['false0'], {i: '#F3F3F3' for i in range(9, 17)}, fs=10, h=21, label='false title')
    o += [s1, s2, s3, T(170, 132, 'three inputs, real Qwen3 tokens · score the true authors at the name positions', 12.5, PEN)]
    o.append(T(170, 250, 'H2 says: by the middle layers the title state encodes WHICH PAPER this is, not just what the title means.', 15, INK, bold=True))
    sv = svgwrap(''.join(o))
    cards = ('<div class="card2" style="position:absolute;left:70px;top:272px;width:540px;z-index:4">'
             '<h4>If H2 holds, we expect</h4><div style="font-family:var(--hand);font-size:15px;line-height:1.3;color:#22304A">'
             '<span class="q">1</span> a made-up title with the same meaning recovers <b>little</b> of the true-title advantage<br>'
             '<span class="q">2</span> the real-title extra is <b>larger</b> for recognised and for more-cited papers<br>'
             '<span class="q">3</span> paper identity explains the title state <b>beyond</b> its text<br>'
             '<span class="q">4</span> a paper-specific answer can be decoded beyond the topic</div></div>'
             '<div class="card2" style="position:absolute;left:650px;top:272px;width:560px;z-index:4;border-color:#C84A3E">'
             '<h4>If H2 fails, we expect</h4><div style="font-family:var(--hand);font-size:15px;line-height:1.3;color:#22304A">'
             '<span class="q">1</span> the made-up title recovers <b>most</b> of the advantage (meaning carries it)<br>'
             '<span class="q">2</span> the extra does not depend on recognition or citations<br>'
             '<span class="q">3</span> text features (meaning, words) explain the state; identity adds ≈ 0<br>'
             '<span class="q">4</span> what remains sits on specific words, not on the paper</div></div>')
    tests = cats(70, 478, 1140, [
        ('Tests in this part', 'why question-only tests cannot decide → slide {{new:ceiling}} · made-up title → slides {{p:85}}, {{p:87}} · '
         'rare vs common words → slide {{new:rare-words}} · recognition and citations → slide {{new:recog-citations}} · variance split → slide {{new:variance}} · '
         'surname signal beyond topic → slide {{new:h2-exception}}'),
        ('Earlier pages', 'small-sample title effect → slides {{p:12}}–{{p:21}} · patchscope and paraphrases → slides {{p:82}}, {{p:83}}'),
        ('Caveat', '<span class="ul">identity and meaning travel together in a real title; only inputs that differ (made-up titles, word swaps) can pull them apart</span>')], 14.5)
    return section('h2-question', 'Question card · H2: does the model hold <i>which paper</i> this is?', P4,
                   'what would we see if the middle layers encode paper identity rather than meaning?', sv + cards + tests
                   + f'<div class="note-h" style="left:930px;top:34px">question card · H2 {tg("lrule", "hypothesis")}</div>',
                   'four predictions; the verdict card scores each, with one locked exception.')

def ceiling():
    A = pd.read_csv(S13 / 'summary_explore_l4audit_20261121/l4audit.csv').set_index('rep')
    src = '381_stage13/summary_explore_l4audit_20261121/l4audit.csv (ret_test)'
    o = []
    y = 132
    for lab, tk in (('authors', TA), ('year', TY), ('field', TF)):
        f = {i: '#FFF1DE' for i in range(9, 20)}; f[19] = '#3C78B4'
        sv_, pos, w = tokens(170, y, tk, f, {19: BLUE}, fs=9.5, h=19, label=lab); o.append(sv_); y += 25
    o.append(T(170, 126, 'the same title under three questions; state at the last title token (blue) → find the same paper among all papers', 12.5, PEN))
    o.append(T(170, 222, 'retrieval: is the nearest state under another question the same paper? (top-1, among all papers)', 13.5, INK, bold=True))
    ax = Ax(130, 248, 520, 290, -0.5, 12.5, 0.6, 1.02)
    bl = [f'bert_last_L{i}' for i in range(13)]
    ys = [float(A.loc[r, 'ret_test']) for r in bl]; lo = [float(A.loc[r, 'ret_test_lo']) for r in bl]; hi = [float(A.loc[r, 'ret_test_hi']) for r in bl]
    o.append(ax.frame(list(range(0, 13, 2)), [0.6, 0.7, 0.8, 0.9, 1.0], 'layer of the text-only model (BERT)', 'retrieval (top-1)', '{:.1f}', 'L{:g}'))
    o.append(band_svg(ax.X(-0.5), ax.X(12.5), ax.Y(1.02), ax.Y(0.985), 'ceiling', ORANGE, 0.12))
    o.append(ax.line(list(range(13)), ys, CTRL, lo, hi))
    o.append(ax.hline(1.0, BLUE, 'Qwen L4–L44: 1.000'))
    NUM.append(('1.000', 'slide {{p:81}} (retrieval across questions at L4–L44)'))
    qL0 = float(A.loc['qwen_L0', 'ret_test'])
    o.append(circ_svg(ax.X(0), ax.Y(qL0), f'Qwen L0 (embeddings only) {num(qL0, src, "{:.2f}")}', '2', ORANGE, 8, 20))
    b1 = float(A.loc['bert_last_L1', 'ret_test'])
    o.append(circ_svg(ax.X(1), ax.Y(b1), f'BERT reaches {num(b1, src, "{:.3f}")} at L1', '1', ORANGE, 10, 26))
    o.append(T(ax.X(8), ax.Y(0.84), 'BERT (text only)', 13.5, CTRL, 'middle', True))
    sv = svgwrap(''.join(o))
    c = cats(690, 236, 520, [
        ('Method', 'change only the question, keep the title: compare the title state across questions (retrieval, cosine, probe transfer, question swap)'),
        ('Result', '<span class="q">1</span> a text-only model already finds the same paper at its first layers; '
                   '<span class="q">2</span> Qwen does so from L4 (1.000) — cosine of the two states 0.9976 at L4'),
        ('Control', 'a text-only model (BERT) has no knowledge of papers, so whatever it reaches is reachable from the words alone'),
        ('So what', '<span class="mk">these tests are at the ceiling</span>: the same words give the same state under every question, so they cannot tell '
                    'meaning from paper identity ' + tg('expl')),
        ('Caveat', '<span class="ul">retrieval on the 582 test papers; Qwen\'s ceiling is from earlier slides, BERT\'s from this check</span>'),
        ('Next', 'make the inputs differ: same meaning with new words → slide {{p:85}}')], 14)
    NUM.append(('0.9976', 'slide {{p:81}} (title-state cosine at L4)'))
    f = fxu(130, 594, 520, [r'$\mathrm{retrieval}=\frac{1}{n}\sum_i \mathbf{1}[\,\mathrm{argmax}_j\ \cos(h_i^{q},h_j^{q^{\prime}})=i\,]$'],
            r'$n=\mathrm{9{,}108\ papers\ (test\ 582)}$', keys=['retrieval ≈ 1: the title finds its own paper — no room left above'])
    return section('ceiling', 'Why tests that change only the question cannot decide H2: the ceiling', P4,
                   'can a question-only test (same title, different question) tell paper identity from meaning?', sv + c + f,
                   'question-only tests hit the ceiling at L4 — identical words, identical state; separating meaning from identity needs different inputs.')

def rare_words():
    r = pd.read_csv(G / 'summary_a24/a24_results.csv'); src = '391_groups/summary_a24/a24_results.csv'
    J = json.load(open(G / 'summary_a24/a24_results.json'))
    def gv(g, qn): x = r[(r.group == g) & (r.quantity == qn)].iloc[0]; return x.est, x.lo, x.hi, int(x.n)
    o = []
    ro, ra, rb = TOK['rare_orig'], TOK['rare_a'], TOK['rare_b']
    ch_a = {i for i, (x, y) in enumerate(zip(ro, ra)) if x != y}; ch_b = {i for i, (x, y) in enumerate(zip(ro, rb)) if x != y}
    s1, _, _ = tokens(190, 134, ro, {}, fs=10, h=20, label='real title')
    s2, _, _ = tokens(190, 160, ra, {i: '#FBE3E1' for i in ch_a}, {i: RED for i in ch_a}, fs=10, h=20, label='(a) rare words swapped')
    s3, _, _ = tokens(190, 186, rb, {i: '#E8F0FA' for i in ch_b}, {i: BLUE for i in ch_b}, fs=10, h=20, label='(b) common words swapped')
    o += [s1, s2, s3]
    o.append(T(190, 126, 'real cohort example (Qwen3 tokens) · (a) each rare word → a rare word from another title · (b) the same number of common content words → frequency-matched words', 12, PEN))
    o.append(T(190, 226, 'score the true authors under each title; R = S(real) − S(variant) = how much of the true-title advantage the swap costs', 12.5, INK))
    ax = Ax(250, 262, 400, 230, 0, 0.2, 0, 1)
    o.append(ax.frame([], [], '', ''))
    xt = [0, 0.05, 0.10, 0.15, 0.20]
    for v in xt:
        o.append(f'<line x1="{ax.X(v):.1f}" y1="{ax.y0}" x2="{ax.X(v):.1f}" y2="{ax.y0+ax.h}" stroke="#E7DADA" stroke-dasharray="3 4"/>')
        o.append(T(ax.X(v), ax.y0 + ax.h + 18, f'{v:.2f}', 12.5, PEN, 'middle'))
    o.append(T(ax.X(0.1), ax.y0 + ax.h + 36, 'mean R = S(real) − S(variant), in log10(1/rank) units', 12.5, PEN, 'middle'))
    yy = ax.y0 + 18
    for g, lab in (('target', 'target'), ('control', 'control')):
        o.append(T(ax.x0 - 10, yy + 34, lab, 16, INK, 'end', True))
        for qn, nm, col in (('Rbar_a', '(a) rare', RED), ('Rbar_b', '(b) common', BLUE), ('Rbar_fict', 'made-up title (all words new)', GREYC)):
            e, lo, hi, n = gv(g, qn)
            o.append(f'<rect x="{ax.X(0):.1f}" y="{yy:.1f}" width="{ax.X(max(e,0))-ax.X(0):.1f}" height="18" fill="{col}" fill-opacity="0.85"/>')
            o.append(f'<line x1="{ax.X(lo):.1f}" y1="{yy+9:.1f}" x2="{ax.X(hi):.1f}" y2="{yy+9:.1f}" stroke="{INK}" stroke-width="1.6"/>')
            o.append(T(ax.X(max(hi, e)) + 6, yy + 14, f'{nm} {num(e, src, "{:.3f}")}', 12.5, col if col != GREYC else PEN, 'start', True))
            yy += 22
        yy += 30
    et = gv('target', 'Rbar_a')
    o.append(circ_svg(ax.X(et[0]), ax.y0 + 27, '', '1', ORANGE, 6, -6))
    sv = svgwrap(''.join(o))
    D = gv('target', 'D = Rbar_a - Rbar_b'); nt = gv('target', 'Rbar_a')[3]; nc = gv('control', 'Rbar_a')[3]
    mr = J['freeze']['mean_replaced']
    new1 = '391_groups/summary_tables_20261122/new1/report.md (paired n_a == n_b, all)'
    c = cats(700, 236, 510, [
        ('Method', 'two word swaps on the true title of each paper; same prompt, same scoring at the final layer'),
        ('Result (locked)', f'<span class="q">1</span> rare-word swap costs <b>{num(et[0], src, "{:.3f}")}</b>, common-word swap <b>{num(gv("target","Rbar_b")[0], src, "{:.3f}")}</b>: '
                            f'D = {num(D[0], src)} {ci(D[1], D[2], src)} ' + tg('lsup')),
        ('Control', 'the common-word swap replaces the same number of words; the made-up title (same meaning, all words new) is shown for scale'),
        ('Caveat', f'<span class="ul">(a) replaces more tokens on average ({num(mr["a"], "391_groups/summary_a24/a24_results.json", "{:.1f}")} vs '
                   f'{num(mr["b"], "391_groups/summary_a24/a24_results.json", "{:.1f}")} words); common words are frequency-matched, not synonyms</span>; '
                   f'with equal counts the gap remains (+0.066 [0.049, 0.082], exploratory)'),
        ('So what', '<span class="mk">the real-title extra sits mainly on rare, specific words</span> — consistent with meaning + specific words, not identity')], 13.8)
    NUM.append(('+0.066 [0.049, 0.082]', new1))
    f = fxu(250, 580, 420, [r'$\bar R_v=\overline{S_{\mathrm{true}}-S_v},\ \ D=\bar R_{\mathrm{rare}}-\bar R_{\mathrm{common}}$'],
            rf'$n=\mathrm{{{nt}\ target\ +\ {nc}\ control\ papers}}$', keys=['R̄ > 0: swapping those words loses part of the true-title advantage'])
    NUM.append((f'{nt} / {nc}', src))
    return section('rare-words', 'Rare, specific words carry the real-title extra; common words barely do', P4,
                   'which words of the real title carry what a same-meaning made-up title misses?', sv + c + f,
                   'swapping rare words costs about 6× more than swapping common ones (locked) — the extra is in specific words.')

def parse_report_block(path, key):
    t = open(path).read(); i = t.index(f'### {key}\n'); j = t.find('\n### ', i + 5); blk = t[i:j if j > 0 else None]
    out = {}
    for m in re.finditer(r'- L(\d+): ([+-]\d\.\d+) \[([+-]\d\.\d+), ([+-]\d\.\d+)\](?: Holm \[([+-]\d\.\d+), ([+-]\d\.\d+)\])?', blk):
        out[int(m.group(1))] = tuple(float(x) if x else None for x in m.groups()[1:])
    return out

def recog_citations():
    rp = G / 'summary_a22_partA/report.md'; src = '391_groups/summary_a22_partA/report.md'
    K4 = parse_report_block(rp, 'K4'); K4c = parse_report_block(rp, 'K4c')
    o = []
    s1, _, _ = tokens(170, 136, TOK['authors_y'], {i: '#FFF1DE' for i in range(9, 20)}, fs=9.5, h=19, label='real title')
    s2, _, _ = tokens(170, 160, TOK['fict_y'], {i: '#E8F0FA' for i in range(9, 18)}, fs=9.5, h=19, label='made-up (example)')
    o += [s1, s2, T(170, 128, 'real-title extra per paper: R_orig − R_fict (both scored at the name positions, layer by layer)', 12.5, PEN)]
    o.append(T(170, 200, 'recognition check: extra(recognised) − extra(not recognised), within citation bins · citation check: extra(more-cited half) − extra(less-cited half), within field', 12.5, INK))
    ax = Ax(130, 236, 520, 300, 4, 60, -0.18, 0.12)
    L = sorted(K4)
    o.append(ax.frame([4, 8, 16, 24, 32, 40, 48, 56, 60], [-0.15, -0.10, -0.05, 0, 0.05, 0.10], 'layer', 'Δ (difference of the extra)', '{:+.2f}'))
    o.append(band_svg(ax.X(24), ax.X(48), ax.Y(0.12), ax.Y(-0.18), 'pre-registered layers L24–L48 (Holm)', GREEN, 0.07))
    o.append(ax.hline(0, INK, '', '0'))
    o.append(ax.line(L, [K4[l][0] for l in L], BLUE, [K4[l][1] for l in L], [K4[l][2] for l in L]))
    o.append(ax.line(L, [K4c[l][0] for l in L], RED, [K4c[l][1] for l in L], [K4c[l][2] for l in L]))
    o.append(circ_svg(ax.X(48), ax.Y(K4[48][0]), f'recognised − not: {num(K4[48][0], src)} {ci(K4[48][3], K4[48][4], src)} Holm', '1', BLUE, -250, -16))
    o.append(circ_svg(ax.X(48), ax.Y(K4c[48][0]), f'more − less cited: {num(K4c[48][0], src)} {ci(K4c[48][3], K4c[48][4], src)} Holm', '2', RED, -270, 30))
    sv = svgwrap(''.join(o))
    c = cats(690, 230, 520, [
        ('Method', 'the same papers scored with the real title and with a same-meaning made-up title; the extra = what only the real title gives'),
        ('Result 1 (locked)', '<span class="q">1</span> the extra is <b>not larger</b> for recognised papers (Holm CI includes 0 at every pre-registered layer) ' + tg('lnot')),
        ('Result 2 (locked)', '<span class="q">2</span> it is <b>smaller</b> for more-cited papers (Holm CI &lt; 0 from L24) ' + tg('rev')),
        ('Control', 'recognised vs not compared within citation bins; more vs less cited compared within field'),
        ('Caveat', f'<span class="ul">without the Holm correction the recognised − not difference is just above 0 at L24 ({num(K4[24][0], src)} {ci(K4[24][1], K4[24][2], src)})</span>'),
        ('So what', '<span class="mk">two identity predictions fail</span>: what the real title adds does not track how well the model knows the paper')], 13.8)
    f = fxu(130, 594, 540, [r'$\Delta_{\mathrm{rec}}(l)=[R_{\mathrm{orig}}-R_{\mathrm{fict}}]_{T}-[\,\cdot\,]_{C},\ \ \Delta_{\mathrm{cit}}(l)=[\,\cdot\,]_{\mathrm{high}}-[\,\cdot\,]_{\mathrm{low}}$'],
            r'$n=\mathrm{1{,}083\ papers\ (554\ target,\ 529\ control)}$', keys=['Δ > 0: the real-title extra is larger for recognised (or more-cited) papers'])
    NUM.append(('1,083 (554/529)', src))
    return section('recog-citations', 'The real-title extra is not larger for recognised papers — and smaller for more-cited ones', P4,
                   'if the extra were paper identity, would it grow with recognition and with citations (H2, prediction 2)?', sv + c + f,
                   'recognition: not supported; citations: reversed (both locked) — the extra is not a "knows this paper" signal.')

def variance():
    rp = open(G / 'summary_a22_partB/report.md').read(); src = '391_groups/summary_a22_partB/report.md (BERT decomposition, residualised = decision version)'
    m = re.search(r'## bert decomposition, residualised[^\n]*\n\s*\|[^\n]*\n\|[^\n]*\n((?:\| L\d+[^\n]*\n)+)', rp)
    rows = []
    for ln in m.group(1).strip().split('\n'):
        c = [x.strip() for x in ln.strip('|').split('|')]
        def p(s): v = re.match(r'([+-]\d\.\d+) \[([+-]\d\.\d+), ([+-]\d\.\d+)\]', s); return tuple(map(float, v.groups()))
        rows.append((int(c[0][1:]), float(c[1]), p(c[2]), p(c[3]), p(c[4])))
    d3 = re.search(r'\*\*D3 identity T-C \(bert\)\*\*[^\n]*\n\s*\|[^\n]*\n\|[^\n]*\n((?:\| \d+[^\n]*\n)+)', rp)
    D3 = {int(x.split('|')[1]): float(x.split('|')[2]) for x in d3.group(1).strip().split('\n')}
    o = []
    # schematic: feature groups -> state
    groups = [('surface (S)', 'word + character n-grams of the title', '#EEF1F5'), ('meaning (M)', 'BERT embedding of the title', '#E8F0FA'),
              ('identity (I)', 'year, citations, field, author names', '#FBE3E1'), ('prior (P)', 'surname frequency in the field', '#F3F3F3')]
    y = 130
    for nm, de, col in groups:
        o.append(f'<rect x="90" y="{y}" width="260" height="26" rx="6" fill="{col}" stroke="#c9ced6"/>')
        o.append(T(100, y + 18, nm, 14, INK, bold=True)); o.append(T(196, y + 18, de, 12, PEN)); y += 31
    o.append(f'<path d="M 360 180 L 430 180" stroke="{INK}" stroke-width="2" marker-end="url(#ar2)"/>')
    o.append('<defs><marker id="ar2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#22304A"/></marker></defs>')
    s_, _, _ = tokens(440, 168, TOK['authors_y'][9:21], {10: '#3C78B4'}, {10: BLUE}, fs=10, h=22)
    o.append(s_); o.append(T(440, 160, 'state at the last title token (top 256 PCs), layer l', 12.5, PEN))
    o.append(T(440, 214, 'unique R² of a group = R²(all four) − R²(all but that group), out of fold', 12.5, INK))
    ax = Ax(130, 290, 520, 250, 0, 7, -0.02, 0.30)
    o.append(ax.frame([], [0, 0.1, 0.2, 0.3], '', 'unique R²', '{:.1f}'))
    o.append(ax.hline(0, INK, '', '0'))
    for k, (l, r2, uS, uM, uI) in enumerate(rows):
        x = ax.X(k + 0.5)
        for dx, v, col in ((-22, uM[0], BLUE), (2, uI[0], RED)):
            y0, y1 = ax.Y(max(v, 0)), ax.Y(min(v, 0))
            o.append(f'<rect x="{x+dx:.1f}" y="{y0:.1f}" width="20" height="{max(y1-y0,1.5):.1f}" fill="{col}" fill-opacity="0.85"/>')
        o.append(T(x, ax.y0 + ax.h + 18, f'L{l}', 12.5, PEN, 'middle'))
    l48 = rows[-1]; l8 = rows[1]
    o.append(circ_svg(ax.X(6.5) - 12, ax.Y(l48[3][0]), f'meaning {num(l48[3][0], src, "{:.3f}")}', '1', BLUE, -150, -6))
    o.append(circ_svg(ax.X(6.5) + 12, ax.Y(0.0) - 2, f'identity {num(l48[4][0], src, "{:+.4f}")}', '2', RED, -120, -40))
    o.append(T(ax.X(1), ax.Y(0.27), 'blue = meaning (M) · red = identity (I)', 13, INK, 'start', True))
    sv = svgwrap(''.join(o))
    c = cats(690, 236, 520, [
        ('Method', 'predict the title-position state of 9,108 papers from four feature groups; ask what each group adds on its own'),
        ('Result 1 (locked)', f'<span class="q">1</span> meaning adds <b>{num(l8[3][0], src, "{:.2f}")}–{num(l48[3][0], src, "{:.2f}")}</b> of the variance beyond the other three groups ' + tg('lsup')),
        ('Result 2 (locked)', f'<span class="q">2</span> identity adds <b>≈ 0</b> ({num(min(r[4][0] for r in rows), src, "{:+.4f}")} to {num(max(r[4][0] for r in rows), src, "{:+.4f}")}); '
                              'positive only at L48 and only with one text model ' + tg('bord')),
        ('Recognition', f'identity adds a little more for recognised papers (target − control {num(min(D3.values()), src, "{:+.4f}")} to {num(max(D3.values()), src, "{:+.4f}")}) ' + tg('lsup', 'locked · supported (tiny)')),
        ('Control', 'two text models (BERT primary, MPNet reported); author features residualised on text so overlap is not double-counted'),
        ('So what', '<span class="mk">the state is explained by meaning; identity adds ≈ 0</span>')], 13.6)
    f = fxu(130, 594, 540, [r'$R^2_{\mathrm{unique}}(G)=R^2(S\cup M\cup I\cup P)-R^2(\mathrm{all\ but}\ G)$'],
            r'$n=\mathrm{9{,}108\ papers,\ out{-}of{-}fold}$', keys=['unique R² > 0: that feature group explains part of the state the others do not'])
    return section('variance', 'What explains the title state? Meaning does; paper identity adds ≈ 0', P4,
                   'does paper identity explain the title-position state beyond its text (H2, prediction 3)?', sv + c + f,
                   'meaning adds 0.17–0.27 of the variance on its own; identity ≈ 0 (borderline at L48) — prediction 3 fails.')

def h2_exception():
    tt = pd.read_csv(G / 'summary_a33/a33_tests.csv'); se = pd.read_csv(G / 'summary_a33/a33_secondary.csv')
    J = json.load(open(G / 'summary_a33/a33_results.json')); src = '391_groups/summary_a33/a33_tests.csv'; srcS = '391_groups/summary_a33/a33_secondary.csv'
    sf = se[se.ans == 'surname_first']
    o = []
    s1, p1, w1 = tokens(170, 132, TOK['authors'], {i: '#FFF1DE' for i in range(9, 20)} | {19: '#3C78B4'}, {19: BLUE}, fs=9.5, h=19, label='own prompt')
    s2, p2, w2 = tokens(170, 166, TOK['ps'], {2: '#E8F0FA'}, {2: BLUE}, fs=10, h=20, label='decode prompt')
    o += [s1, s2]
    o.append(f'<path d="M {p1[19][0]+10:.1f} 152 C {p1[19][0]:.1f} 162, {p2[2][1]+40:.1f} 160, {p2[2][1]-6:.1f} 166" stroke="{BLUE}" stroke-width="2" fill="none"/>')
    o.append(T(p2[-1][1] + 12, 181, '→ score the first author\'s surname (first token)', 12.5, INK))
    o.append(T(170, 124, 'inject the L8 state of the last title token at X; compare three sources of the state', 12.5, PEN))
    o.append(T(170, 210, 'D = score with the own state − score with a partner\'s state · partner: random same-field paper (grey) or topic-matched paper, nearest title in the field (orange)', 12.5, INK))
    # layer profile
    ax = Ax(130, 252, 300, 250, 8, 56, 0, 0.18)
    L = sorted(sf.layer.unique())
    def ser(cn): z = sf[sf.contrast == cn].sort_values('layer'); return z.layer.tolist(), z.est.tolist(), z.lo.tolist(), z.hi.tolist()
    o.append(ax.frame([8, 16, 24, 32, 40, 48, 56], [0, 0.05, 0.10, 0.15], 'layer', 'D (log10 rank units)', '{:.2f}'))
    x, y_, lo, hi = ser('D_partner'); o.append(ax.line(x, y_, CTRL, lo, hi))
    x, y_, lo, hi = ser('D_topic_mpnet'); o.append(ax.line(x, y_, ORANGE, lo, hi))
    x, y_, lo, hi = ser('D_topic_mpnet_L0'); o.append(ax.line(x, y_, GREYC, dash='3 3', mk=False))
    o.append(T(ax.X(30), ax.Y(0.165), 'vs random paper', 12.5, CTRL, 'middle', True)); o.append(T(ax.X(28), ax.Y(0.035), 'vs topic-matched', 12.5, ORANGE, 'middle', True))
    o.append(T(ax.X(26), ax.Y(0.006), 'embeddings-only source (L0) ≈ 0', 12, PEN, 'middle', True))
    t1 = tt.iloc[0]; o.append(circ_svg(ax.X(8), ax.Y(t1.est), '', '1', ORANGE, 6, -6))
    # forest of T1-T3
    fx = Ax(500, 270, 160, 200, -0.01, 0.09, 0, 3)
    o.append(T(580, 262, 'three locked tests (L8)', 13, INK, 'middle', True))
    o.append(f'<line x1="{fx.X(0):.1f}" y1="270" x2="{fx.X(0):.1f}" y2="470" stroke="{INK}" stroke-width="1.4"/>')
    labs = ['T1 beyond topic', 'T2 beyond text model (std.)', 'T3 target − control']
    for k in range(3):
        r_ = tt.iloc[k]; yy = 300 + k * 60
        col = BLUE if k == 0 else GOLD
        o.append(f'<line x1="{fx.X(r_.lo):.1f}" y1="{yy}" x2="{fx.X(r_.hi):.1f}" y2="{yy}" stroke="{col}" stroke-width="3"/>')
        o.append(f'<circle cx="{fx.X(r_.est):.1f}" cy="{yy}" r="6" fill="{col}"/>')
        o.append(T(fx.X(0) + 6, yy - 12, labs[k], 12.5, INK, 'start', True))
        o.append(T(fx.X(0) + 6, yy + 20, f'{num(r_.est, src)} {ci(r_.lo, r_.hi, src)}', 12, col, 'start', True))
    o.append(T(fx.X(0), 488, '0', 12, PEN, 'middle'))
    sv = svgwrap(''.join(o))
    P = sf[sf.contrast.str.startswith('P =') & (sf.layer == 8)].iloc[0]
    fc = J['freeze_counts']['by_group_primary']
    c = cats(700, 230, 510, [
        ('Method', 'decode the first author from the title state at L8 (patchscope); subtract what a <b>topic-matched</b> paper\'s state gives; 6,048 new papers, rules locked before the run'),
        ('Result', f'<span class="q">1</span> T1 beyond topic: <b>{num(t1.est, src)}</b> {ci(t1.lo, t1.hi, src)} ' + tg('lsup')
                   + f'; T2 beyond a text-only model and T3 larger for recognised papers ' + tg('marg') + ' (Holm lower bounds +0.002, +0.003)'),
        ('Control', 'topic-matched and random same-field partners; a BERT text baseline on the same pairs; embeddings-only (L0) source ≈ 0'),
        ('Caveat', f'<span class="ul">about half of the raw surname signal is topic ({num(P.est, srcS, "{:.2f}")} {ci(P.lo, P.hi, srcS, "{:.2f}")} survives topic matching); '
                   'the text baseline failed its own positive control; small effect, not strong evidence</span>'),
        ('So what', '<span class="mk">one small locked exception</span> to "not identity": the L8 title state carries a little paper-specific surname information')], 13.5)
    NUM.extend([('+0.002, +0.003', src + ' (holm_lo T2, T3)'), (f'{fc["target"]} / {fc["control"]}', '391_groups/summary_a33/a33_results.json')])
    f = fxu(130, 594, 540, [r'$D_s(l)=\overline{\log_{10}\frac{1}{\mathrm{rank}}(A\,|\,h_A)-\log_{10}\frac{1}{\mathrm{rank}}(A\,|\,h_s)}$'],
            rf'$n=\mathrm{{6{{,}}048\ papers\ ({fc["target"]//1000}{{,}}{fc["target"]%1000:03d}\ target,\ {fc["control"]//1000}{{,}}{fc["control"]%1000:03d}\ control)}}$', keys=["D_topic > 0: the state names this paper's first author beyond its topic"])
    return section('h2-exception', 'The one locked exception: a small surname signal at L8, beyond topic', P4,
                   'is there any paper-specific signal in the title state that survives topic matching (H2, prediction 4)?', sv + c + f,
                   'T1 robust, T2 and T3 marginal, about half of the raw signal is topic — a small locked exception, not a paper-identity representation.')

def h2_verdict():
    rows = [('① made-up title recovers little', '<b>fails</b>: it recovers 75% (φ = 0.751)', tg('lsup'), '{{p:85}}, {{p:87}}', '#FBE3E1'),
            ('② extra larger for recognised / more-cited', '<b>fails</b>: not larger; smaller for more-cited', tg('lnot') + ' ' + tg('rev'), '{{new:recog-citations}}', '#FBE3E1'),
            ('③ identity explains the state beyond text', '<b>fails</b>: ≈ 0 (meaning does)', tg('lsup', 'locked') + ' ' + tg('bord'), '{{new:variance}}', '#FBE3E1'),
            ('④ paper-specific answer beyond topic', '<b>small exception</b>: L8 surname signal (T1 robust; T2, T3 marginal)', tg('lsup') + ' ' + tg('marg'), '{{new:h2-exception}}', '#FFF1D6'),
            ('— what remains sits on specific words', '<b>holds</b>: rare 0.162 vs common 0.027', tg('lsup'), '{{new:rare-words}}', '#EAF6EC')]
    NUM.append(('φ = 0.751', 'slide {{p:85}}'))
    vh = ('<b>Not supported as a general paper-identity representation, with one locked exception:</b> the title state at L8 carries a small paper-specific surname '
          'signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is '
          'larger for recognised papers (T3, marginal). <span class="mk">Otherwise the real-title advantage is carried mainly by meaning and specific words.</span>')
    op = ['a text-only baseline that passes its positive control (would make T2 decisive)', '<span class="ul">about half of the surname signal is topic</span>',
          'meaning twins (real papers, same meaning): too few pairs so far']
    o = [T(70, 452, 'Scoreboard: the H2 predictions', 15, INK, bold=True)]
    items = [('①', 'made-up title', 'fails', RED), ('②', 'recognition / citations', 'fails', RED), ('③', 'variance split', 'fails', RED),
             ('④', 'beyond topic', 'small exception', GOLD), ('+', 'specific words', 'holds', GREEN)]
    for k, (m, lab, res, col) in enumerate(items):
        cx = 120 + k * 140
        o.append(f'<circle cx="{cx}" cy="520" r="30" fill="{col}" fill-opacity="0.18" stroke="{col}" stroke-width="3"/>')
        o.append(T(cx, 528, m, 22, col, 'middle', True)); o.append(T(cx, 572, lab, 12.5, INK, 'middle', True)); o.append(T(cx, 590, res, 13, col, 'middle', True))
    o.append(T(70, 624, 'three identity predictions fail; one small locked exception; what remains sits on specific words', 13, PEN))
    sch = svgwrap(''.join(o))
    return verdict_card('h2-verdict', 'H2', 'Verdict card · H2: meaning and specific words, one small exception', P4,
                        'what did the H2 tests show, and how strong is each result?', rows, vh, op,
                        'H2 is not supported as paper identity (one small locked exception). <b>Next (Part 5):</b> the meaning reaches the name positions — '
                        'how does it get there, and in what form is the author held?', sch)

def _old_h2_matrix():
    return matrix('h2-matrix', 'Evidence matrix, after H2', P4, 2,
                  'H1 and H2 rows filled: question read, format layer open; meaning and specific words, not identity (one small exception). <b>Next:</b> the route and H3.')

SLOTS = [('h1-question', h1_question), ('h1-colon-ratio', h1_colon_ratio), ('h1-format', h1_format), ('h1-verdict', h1_verdict), ('h1-matrix', h1_matrix),
         ('h2-question', h2_question), ('ceiling', ceiling), ('rare-words', rare_words), ('recog-citations', recog_citations), ('variance', variance),
         ('h2-exception', h2_exception), ('h2-verdict', h2_verdict), ('h2-matrix', h2_matrix)]
if __name__ == '__main__':
    out = []
    for slot, fn in SLOTS:
        h = fn()
        pre = 'p34' + slot.replace('-', '') + '_'
        h = re.sub(r'id="(t\d+_[^"]+)"', lambda m: f'id="{pre}{m.group(1)}"', h)
        h = re.sub(r'href="#(t\d+_[^"]+)"', lambda m: f'href="#{pre}{m.group(1)}"', h)
        (FR / f'{slot}.html').write_text(h); out.append(h); print(slot, len(h))
    seen = set(); lines = ['# Part 3–4 fragments: number → source', '', 'Every number printed on the 13 fragments, with its source file (or earlier slide).', '']
    for s_, src in NUM:
        if (s_, src) in seen: continue
        seen.add((s_, src)); lines.append(f'- `{s_}` — {src}')
    (FR / 'part34_numbers.md').write_text('\n'.join(lines) + '\n')
    # standalone test deck for rendering
    deck = open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html').read()
    i = deck.find('<section class="slide'); j = deck.rfind('</section>', 0, deck.find('<nav class="nav"')) + len('</section>')
    (W / 'test_part34.html').write_text(deck[:i] + '\n'.join(out) + deck[j:])
    print('numbers', len(seen))
