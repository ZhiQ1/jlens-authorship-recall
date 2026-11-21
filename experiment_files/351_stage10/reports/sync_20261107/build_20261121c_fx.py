"""2026-11-21c: formula / n audit of the merged HTML deck (v48 build b -> final v48). Adds a small grey formula line (.fxn: formula box + 'n = …')
next to the chart on every chart / numeric method slide that lacked one (positions from fxpos.json, checked by screenshots), plus per-chart
formula lines on the two new exploratory slides. Formulas restate how the source scripts compute the plotted quantity (as given in each slide's
'How computed' line / source report). Source = stage1_11_deck.html.after_20261121b -> stage1_11_deck.html. Writes build_20261121c_fx.json."""
import re, json, html
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
SRC = D / 'stage1_11_deck.html.after_20261121b'; OUT = D / 'stage1_11_deck.html'
POS = {int(k): v['best'] for k, v in json.load(open(D / 'expl_20261121/fxpos.json')).items()}
e = lambda s: html.escape(s, quote=False)
# slide: (formula or None, n line, width)
FX = {
 6: (None, 'n = 9,108 papers (A 4,110 · U0 2,002 · B 2,186 · C 511 · D 34 …) · Stages 11–13: 593 + 593 · X3: 1,178 pairs', 520),
 18: (None, 'n = 200 new papers (100 A/B pairs), Stage 8D', 520),
 22: (None, 'n = 1 example paper (Coifman, Bonanno, Rafaeli 2007), author 1 · the method is applied to all 9,108 papers', 560),
 25: ('prior = nlr(delete),  topic = mean₅ nlr(false) − nlr(delete),  spec = nlr(true) − mean₅ nlr(false);  each T − C within citation bins', 'n = 9,108 papers (4,621 target + 2,220 control), L63', 700),
 26: (None, 'n = 9,108 papers (probe fit, 5 author-team folds) · 1,395 reuse-free papers (V0 main number)', 620),
 30: (None, 'n = P1: A 3,417 + B 2,148 papers · P2: C − A (co-authors, first author) · dose: R0 papers by orders right', 640),
 38: (None, 'n = 1 example paper (author 1, token “Co”), true title vs false_0', 560),
 45: ('y = T − C within citation bins of spec,  spec = nlr(true) − mean₅ nlr(false),  nlr = log₁₀(1/rank)', 'n = 3,734 target + 2,182 control papers, name positions', 700),
 46: ('y = T − C within citation bins of spec,  spec = nlr(true) − mean₅ nlr(false),  nlr = log₁₀(1/rank)', 'n = 3,734 target + 2,182 control papers, L40–L62', 700),
 48: (None, 'n = 1,186 papers (593 target + 593 control), mean of 5 false titles', 520),
 49: (None, 'n = 1,186 papers (593 target + 593 control)', 520),
 50: ('R(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p];   loss(l) = mean_p[K̄_p(64) − K̄_p(l)] / mean_p[T̄_p − F̄_p]', 'n = 1,186 papers (593 + 593), false_0', 760),
 65: (None, 'n = 582 test papers (team folds)', 480),
 66: (None, 'n = 1,110 papers (primary set; 552 test papers)', 480),
 67: (None, 'n = 582 test papers (596 tune), team CI', 480),
 71: ('recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄],  mean of 5 false titles', 'n = 1,186 papers (593 + 593)', 660),
 76: ('R(l) = mean(patched − false) / mean(true − false), mean of 5;   S(l) = T(l) − F(l)', 'n = 1,186 papers (593 + 593)', 700),
 84: ('spec = nlr(true) − nlr(false₀) per name token, ranked by role;  T − C within citation bins', 'n = V0 1,395–1,706 · Vpd 3,046–4,812 papers (L40)', 660),
 85: (None, 'n = 4,654 papers (3,130 target + 1,524 control), surname first token', 420),
 87: ('AUROC = mean over (true M, fabricated H) pairs of 1[probe(M) > probe(H)]  (ties 0.5)', 'n = 518 target papers, 3,388 pairs', 640),
 95: ('y = mean over unwritten authors of spec,  spec = nlr(true) − mean₅ nlr(false),  L63', 'n = R0 927–4,105 · R1 15–462 papers per level', 700),
 99: ('denominator = mean_p[T̄_p − F̄_p]  (false_0)', 'n = A 557 · B 586 · C 462 · D 33 papers (D descriptive)', 520),
}
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 99
SL = [m.group(0) for m in ms]
REC = {}
# manual positions after the screenshot check (finder ignored image charts on these slides)
OVR = {25: (70, 596, 1140), 45: (70, 596, 1140), 46: (70, 596, 1140), 50: (70, 592, 1140), 95: (70, 671, 1140), 99: (760, 664, 420)}
for n, (fx, nn, w) in FX.items():
    x, y = POS[n][:2]
    if n in OVR: x, y, w = OVR[n]
    if n == 99: fx = None  # the formula already sits beside the chart ('How computed: denominator = …')
    inner = (f'<span class="fx">{e(fx)}</span>' if fx else '') + f'<span class="nn">{e(nn)}</span>'
    div = f'<div class="fxn" style="left:{x}px;top:{y}px;width:{w}px">{inner}</div>'
    sec = SL[n - 1]; assert 'class="fxn' not in sec or n in (6, 18, 22, 26, 30, 38, 48, 49, 65, 66, 67, 85), n
    i = sec.rindex('</section>'); SL[n - 1] = sec[:i] + div + sec[i:]
    REC[n] = dict(x=x, y=y, w=w, formula=fx, n=nn)
# per-chart formula lines on the two new exploratory slides (svg text, grey)
GREY = '#8a8f98'; SANS = "'Noto Sans SC','PingFang SC','Droid Sans Fallback',system-ui,sans-serif"
def gt(x, y, t, fs=11.5): return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{GREY}" font-family="{SANS}">{e(t)}</text>'
add = {81: gt(640, 452, 'y = (T̄ − C̄)_high − (T̄ − C̄)_low, T − C within citation bins of the probe spec = probe(true) − probe(false)'),
       86: gt(130, 466, 'y = λ_k / Σ_j λ_j (eigenvalues of the target rows d − mean_C d)', 11) + gt(650, 488, 'x = cos(Δ, v) = Δ·v / (‖Δ‖ ‖v‖), v = unit probe direction', 11)}
for n, t in add.items():
    sec = SL[n - 1]; i = sec.rindex('</svg>'); SL[n - 1] = sec[:i] + t + sec[i:]; REC[f'{n}_svg'] = t
o = s[:ms[0].start()] + '\n'.join(SL) + s[ms[-1].end():]
OUT.write_text(o, encoding='utf-8')
json.dump(REC, open(Path(__file__).with_suffix('.json'), 'w'), indent=1, ensure_ascii=False)
print('ok', len(FX), 'fxn added')
