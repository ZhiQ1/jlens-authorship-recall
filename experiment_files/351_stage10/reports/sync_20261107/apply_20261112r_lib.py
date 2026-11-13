"""Round r (2026-11-12) shared library: hand-drawn-style SVG chart slides for the merged deck (same conventions as the
method slides 62-64: 1280x720 .slide.mf, #FFFBFB + #FAEEEE 32px grid, Caveat titles, Patrick Hand labels, ink #22304A,
pen #6A7385, orange #D9772B, blue #3C78B4, green #3E8E4E, red #C84A3E, formula box #FFF6DA / #D9772B).
Every plotted number is written as SVG <text>; the source file(s) go under each chart (class src).
"怎么算" five-line blocks use WORDING (same quantity -> same wording everywhere); formulas are verbatim handbook quotes
(checked by check_verbatim() against methods_handbook.html)."""
import csv, html, re
from pathlib import Path

INK, PEN, OR, BL, GR, RD, PINK = '#22304A', '#6A7385', '#D9772B', '#3C78B4', '#3E8E4E', '#C84A3E', '#B0566F'
LIGHT = '#C3C9D2'
HAND = "'Patrick Hand',Caveat,cursive"; TITLE = "Caveat,'Patrick Hand',cursive"
SANS = "'Noto Sans SC','PingFang SC','Droid Sans Fallback',system-ui,sans-serif"
HB = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/methods_handbook.html')
R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); G391 = Path('/scratch/zhang.zhiqi2/jlens/391_groups')

def esc(s): return html.escape(str(s), quote=True)
def f3(v, sign=False): return (f'{v:+.3f}' if sign else f'{v:.3f}').replace('-', '−')
def ci(lo, hi, sign=False): return f'[{f3(lo, sign)}, {f3(hi, sign)}]'
def rows(path): return list(csv.DictReader(open(path, encoding='utf-8')))

def width(s, fs):
    w = 0.0
    for ch in s:
        o = ord(ch)
        w += fs * (1.0 if (0x2E80 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or 0x3000 <= o <= 0x303F) else 0.58)
    return w

def wrap(s, fs, maxw):
    """greedy wrap; breaks at spaces or between CJK chars"""
    out, cur = [], ''
    tokens = re.findall(r'[⺀-鿿　-〿＀-￯]|[^\s⺀-鿿　-〿＀-￯]+|\s+', s)
    for t in tokens:
        if width(cur + t, fs) > maxw and cur.strip():
            out.append(cur.rstrip()); cur = t.lstrip()
        else: cur += t
    if cur.strip(): out.append(cur.rstrip())
    return out

def T(x, y, s, fs=15, fill=PEN, anchor='start', font=HAND, weight=None, extra=''):
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}" font-family="{font}"{w}{extra}>{esc(s)}</text>'

def para(x, y, s, fs, maxw, fill=PEN, font=SANS, lh=None, cls=''):
    lh = lh or fs * 1.3; lines = wrap(s, fs, maxw); c = f' class="{cls}"' if cls else ''
    t = ''.join(f'<tspan x="{x:.1f}" dy="{0 if i == 0 else lh:.1f}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    return f'<text{c} x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{fill}" font-family="{font}">{t}</text>', len(lines) * lh

# ---------------------------------------------------------------- slide frame
def frame(pid, title, sub, tag, tagcol=BL, title_fs=50):
    tw = width(tag, 18) * 0.92 + 30
    return (f'<defs><pattern id="{pid}g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#FAEEEE" stroke-width="1"/></pattern>'
            f'<marker id="{pid}a" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker></defs>'
            f'<rect width="1280" height="720" fill="#FFFBFB"/><rect width="1280" height="720" fill="url(#{pid}g)"/>'
            + T(70, 84, title, title_fs, INK, font=TITLE, weight=700) + (T(72, 112, sub, 18, PEN) if sub else '')
            + f'<g data-name="section tag"><rect x="{1254 - tw:.1f}" y="22" width="{tw:.1f}" height="30" rx="10" fill="none" stroke="{tagcol}" stroke-width="2"/>'
            + T(1254 - tw / 2, 43, tag, 18, tagcol, 'middle') + '</g>')

def section(aria, pid, body):
    return (f'<section class="slide mf" aria-label="{esc(aria)}"><span class="tag" style="display:none">{esc(aria)}</span>'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" role="img" aria-label="{esc(aria)}">\n{body}\n</svg><span class="pg"></span></section>')

def footer(s, y=712, x=70):
    lines = wrap(s, 11, 1140)
    t = ''.join(f'<tspan x="{x}" dy="{0 if i == 0 else 13}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    return f'<text x="{x}" y="{y - 13 * (len(lines) - 1)}" class="src" font-size="11" fill="#8a8f98" text-anchor="start">{t}</text>'

def src_under(x, y, s, maxw=540):
    t, h = para(x, y, s, 10.5, maxw, '#8a8f98', cls='src'); return t, h

def node(pid, x, y, step, label, fs=17):
    w = 44 + width(label, fs) * 0.80 + 10
    return (f'<g data-name="flow node {step}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="36" rx="12" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{x + 20:.1f}" cy="{y + 18:.1f}" r="11" fill="{INK}"/>' + T(x + 20, y + 24, str(step), 16, '#FFFFFF', 'middle')
            + T(x + 38, y + 24, label, fs, INK) + '</g>'), w

def flow(pid, x, y, labels, gap=26, fs=17):
    out, cx = '', x
    for i, l in enumerate(labels, 1):
        g, w = node(pid, cx, y, i, l, fs); out += g
        if i < len(labels): out += f'<line x1="{cx + w + 3:.1f}" y1="{y + 18}" x2="{cx + w + gap - 9:.1f}" y2="{y + 18}" stroke="{INK}" stroke-width="2.2" marker-end="url(#{pid}a)"/>'
        cx += w + gap
    return out, cx - gap

def formula(x, y, main, sub='', fs=22, w=None):
    w = w or max(width(main, fs) * 0.95, width(sub, 14) * 0.95) + 40
    h = 56 if sub else 42
    return (f'<g data-name="formula"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="#FFF6DA" stroke="{OR}" stroke-width="2.5"/>'
            + T(x + w / 2, y + 28, main, fs, INK, 'middle', weight=700) + (T(x + w / 2, y + 47, sub, 14, PEN, 'middle') if sub else '') + '</g>'), w

def badge(x, y, s, col='#B54708', fs=17):
    w = width(s, fs) + 26
    return f'<g data-name="badge"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="28" rx="8" fill="#FFF4D6" stroke="{col}" stroke-width="2"/>' + T(x + 13, y + 20, s, fs, col, font=SANS, weight=700) + '</g>', w

# ---------------------------------------------------------------- charts
class Ax:
    def __init__(self, x0, y0, w, h, xmin, xmax, ymin, ymax):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h; self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
    def X(self, v): return self.x0 + (v - self.xmin) / (self.xmax - self.xmin) * self.w
    def Y(self, v): return self.y0 + self.h - (v - self.ymin) / (self.ymax - self.ymin) * self.h
    def frame(self, xt, yt, xlab=lambda v: f'L{v}', ylab=lambda v: f'{v:g}'.replace('-', '−'), title=None, ytitle=None, grid=True):
        o = f'<g data-name="axes">'
        for v in yt:
            y = self.Y(v)
            if grid: o += f'<line x1="{self.x0:.1f}" y1="{y:.1f}" x2="{self.x0 + self.w:.1f}" y2="{y:.1f}" stroke="#E7DADA" stroke-width="1" stroke-dasharray="3 4"/>'
            o += f'<line x1="{self.x0 - 5:.1f}" y1="{y:.1f}" x2="{self.x0:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.6"/>' + T(self.x0 - 8, y + 5, ylab(v), 14, PEN, 'end')
        for v in xt:
            x = self.X(v); o += f'<line x1="{x:.1f}" y1="{self.y0 + self.h:.1f}" x2="{x:.1f}" y2="{self.y0 + self.h + 5:.1f}" stroke="{INK}" stroke-width="1.6"/>' + T(x, self.y0 + self.h + 19, xlab(v), 14, PEN, 'middle')
        o += (f'<line x1="{self.x0:.1f}" y1="{self.y0 + self.h:.1f}" x2="{self.x0 + self.w:.1f}" y2="{self.y0 + self.h:.1f}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
              f'<line x1="{self.x0:.1f}" y1="{self.y0 + self.h:.1f}" x2="{self.x0:.1f}" y2="{self.y0:.1f}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
        if title: o += T(self.x0 - 40, self.y0 - 14, title, 17, INK, weight=700)
        if ytitle: o += T(self.x0 + 6, self.y0 + 4, ytitle, 13, PEN)
        return o + '</g>'
    def hline(self, v, col=PEN, dash='6 5', w=1.6, label=None, lab_anchor='end', lab_dy=-5, lab_fs=13):
        y = self.Y(v); o = f'<line x1="{self.x0:.1f}" y1="{y:.1f}" x2="{self.x0 + self.w:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>'
        if label: o += T(self.x0 + self.w - 4 if lab_anchor == 'end' else self.x0 + 6, y + lab_dy, label, lab_fs, col, lab_anchor)
        return o
    def band(self, xs, lo, hi, col, op=0.18):
        pts = [f'{self.X(x):.1f},{self.Y(v):.1f}' for x, v in zip(xs, hi)] + [f'{self.X(x):.1f},{self.Y(v):.1f}' for x, v in zip(xs[::-1], lo[::-1])]
        return f'<polygon points="{" ".join(pts)}" fill="{col}" fill-opacity="{op}" stroke="none"/>'
    def line(self, xs, ys, col, w=3, dash=None, pts=True, r=4, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        o = f'<polyline points="{" ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in zip(xs, ys))}" fill="none" stroke-linejoin="round" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d} stroke-opacity="{op}"/>'
        if pts: o += ''.join(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{col}" fill-opacity="{op}"/>' for x, y in zip(xs, ys))
        return o
    def whisk(self, x, lo, hi, col, w=1.8, cap=4):
        X = self.X(x); return (f'<line x1="{X:.1f}" y1="{self.Y(lo):.1f}" x2="{X:.1f}" y2="{self.Y(hi):.1f}" stroke="{col}" stroke-width="{w}"/>'
                               f'<line x1="{X - cap:.1f}" y1="{self.Y(lo):.1f}" x2="{X + cap:.1f}" y2="{self.Y(lo):.1f}" stroke="{col}" stroke-width="{w}"/><line x1="{X - cap:.1f}" y1="{self.Y(hi):.1f}" x2="{X + cap:.1f}" y2="{self.Y(hi):.1f}" stroke="{col}" stroke-width="{w}"/>')

def legend(x, y, items, fs=14, gap=18):
    """items: (label, col, kind) kind in line/dash/thin/box"""
    o, cx = '<g data-name="legend">', x
    for lab, col, kind in items:
        if kind == 'box': o += f'<rect x="{cx:.1f}" y="{y - 10:.1f}" width="14" height="12" fill="{col}" stroke="{INK}" stroke-width="1"/>'
        else:
            dash = ' stroke-dasharray="5 4"' if kind == 'dash' else ''; w = 1.4 if kind in ('thin', 'dash') else 3
            o += f'<line x1="{cx:.1f}" y1="{y - 4:.1f}" x2="{cx + 22:.1f}" y2="{y - 4:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{dash}/>'
        cx += 28 if kind != 'box' else 20
        o += T(cx, y, lab, fs, INK, font=HAND); cx += width(lab, fs) * 0.9 + gap
    return o + '</g>'

def forest(x0, y0, w, rows_, xmin, xmax, ticks, rowh=22, labw=170, fs=14, zero=0.0, dec=None):
    """rows_: (label, est, lo, hi, col, opacity, valtext). returns svg, height"""
    ax = Ax(x0 + labw, y0, w - labw - 150, rowh * len(rows_), xmin, xmax, 0, 1)
    o = '<g data-name="forest">'
    for v in ticks:
        X = ax.X(v); o += f'<line x1="{X:.1f}" y1="{y0:.1f}" x2="{X:.1f}" y2="{y0 + ax.h:.1f}" stroke="#E7DADA" stroke-width="1" stroke-dasharray="3 4"/>' + T(X, y0 + ax.h + 16, f'{v:+.2f}'.replace('-', '−') if v else '0', 13, PEN, 'middle')
    X0 = ax.X(zero); o += f'<line x1="{X0:.1f}" y1="{y0 - 4:.1f}" x2="{X0:.1f}" y2="{y0 + ax.h + 2:.1f}" stroke="{INK}" stroke-width="1.8"/>'
    if dec is not None:
        Xd = ax.X(dec); o += f'<line x1="{Xd:.1f}" y1="{y0 - 4:.1f}" x2="{Xd:.1f}" y2="{y0 + ax.h + 2:.1f}" stroke="{RD}" stroke-width="1.6" stroke-dasharray="6 4"/>'
    for i, (lab, est, lo, hi, col, op, vt) in enumerate(rows_):
        y = y0 + rowh * (i + 0.5)
        o += T(x0 + labw - 8, y + 5, lab, fs, INK if op > 0.6 else PEN, 'end', font=SANS if re.search('[一-鿿]', lab) else HAND)
        o += (f'<line x1="{ax.X(lo):.1f}" y1="{y:.1f}" x2="{ax.X(hi):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.6" stroke-opacity="{op}" stroke-linecap="round"/>'
              f'<rect x="{ax.X(est) - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="{col}" fill-opacity="{op}" stroke="{INK}" stroke-width="1" stroke-opacity="{op}"/>')
        o += T(x0 + w - 145, y + 5, vt, 13, INK if op > 0.6 else PEN, font=HAND)
    return o + '</g>', ax.h + 22

# ---------------------------------------------------------------- "怎么算" wording (same quantity -> same wording)
F = {  # verbatim handbook formulas (checked)
 'nlr': 'nlr = log10(1/rank) = −log10(rank)',
 'rank': 'rank = 1 + #(logit > gold logit)',
 'spec': 'spec = true − mean(false_0..4)',
 'tc': 'target−control = Σ_b w_b [mean_{target,b} − mean_{control,b}]，w_b = n_t n_c/(n_t+n_c) 归一化',
 'rec': 'recovery(l) = mean_p[ P̄_p(l) − F̄_p ] / mean_p[ T̄_p − F̄_p ]',
 'loss': 'loss(l) = mean_p[ K̄_p(64) − K̄_p(l) ] / mean_p[ T̄_p − F̄_p ]',
 'x6': 'R(l) = mean_papers(nlr_patched@l − nlr_false) / mean_papers(nlr_true − nlr_false)；平均 R = 5 个标题 R 的简单平均（bootstrap 同样逐次平均）',
 'S': 'T(l) = mean(kT64 − kT_l) / mean(true − false)；F(l) = mean(kF64 − kF_l) / mean(true − false)；S(l) = T(l) − F(l)（论文特有损失）',
 'probe_x1': 'spec = 探针(true 标题残差) − 探针(false_0 标题残差)',
 'prior': 'prior = m_delete；topic = m_false\u0304 − m_delete；spec = m_true − m_false\u0304',
}
NOTE = {  # non-verbatim explanatory additions (marked as such where needed)
 'auroc': '论文内 AUROC：每篇 target 论文（≥ 1 个真作者 M 且 ≥ 1 个编造名字 H）内的全部 M–H 名字对，probe 分数 M > H 记 1、并列记 0.5，取平均（方法手册 定义：2-11b 论文内 AUROC）',
 'np': '名字位置 probe：ridge 从第 l 层"预测名字 token 的位置"的残差拟合到同一位置模型自己的 L63 状态，在 9,137 个名字 token 内求名次 → nlr；spec = probe(true) − probe(false)（方法手册 定义：名字位置 probe spec）',
}
CI = {'team': '团队整群 bootstrap 2,000 次（按作者团队重抽，2.5/97.5 百分位）',
      'paper': '论文 bootstrap 2,000 次（在"档 × 组"内对论文有放回重抽，2.5/97.5 分位）',
      'none': '无区间（单篇示例）'}

def check_verbatim():
    t = HB.read_text(encoding='utf-8'); t = html.unescape(re.sub(r'<[^>]+>', '', t)); t = re.sub(r'\s+', ' ', t)
    bad = [k for k, v in F.items() if re.sub(r'\s+', ' ', v) not in t]
    assert not bad, ('not verbatim in handbook', bad)
    return True

def how(qty_formula, data, ctrl, ci_, src):
    """five lines (label, text)"""
    return [('怎么算', qty_formula), ('数据', data), ('对照', ctrl), ('区间', ci_), ('出处', src)]

def howblock(x, y, lines, maxw, fs=10.5, title=True):
    """renders the five lines as SVG text; returns svg, height"""
    o, cy = '<g data-name="how computed">', y
    for lab, txt in lines:
        lw = width(lab + '：', fs) + 2
        o += T(x, cy, lab + '：', fs, PINK, font=SANS, weight=700)
        t, h = para(x + lw, cy, txt, fs, maxw - lw, '#4B5363', lh=fs * 1.28)
        o += t; cy += h + 1
    return o + '</g>', cy - y

def howtext(lines):
    """notes form: one paragraph, '怎么算：…；数据：…' """
    return ' '.join(f'【{lab}】{txt}' for lab, txt in lines)

def oneliner(lines):
    d = dict(lines); return f'怎么算：{d["怎么算"]} · {d["数据"]} · 出处：{d["出处"]}'

def bullets(x, y, items, fs=16, maxw=1140, lh=21):
    """items: (bold head, text, src); text wrapped in HAND font; all srcs combined in one small line after"""
    o, cy = '', y
    for h1, txt, src in items:
        lines = wrap(h1 + txt, fs * 0.82, maxw)
        first = True; rest = h1 + txt
        for k, l in enumerate(lines):
            if k == 0 and l.startswith(h1):
                o += f'<text x="{x}" y="{cy:.1f}" font-size="{fs}" fill="{INK}" font-family="{HAND}"><tspan font-weight="700">{esc(h1)}</tspan>{esc(l[len(h1):])}</text>'
            else:
                o += f'<text x="{x + (14 if k else 0)}" y="{cy:.1f}" font-size="{fs}" fill="{INK}" font-family="{HAND}">{esc(l)}</text>'
            cy += lh
    srcs = ' · '.join(f'{h1.strip(": ")}: {src.strip("()")}' for h1, _, src in items if src)
    if srcs:
        t, h = para(x, cy - 4, srcs, 10.5, maxw, '#8a8f98', cls='src'); o += t; cy += h
    return o, cy - y
