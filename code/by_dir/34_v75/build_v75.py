"""2026-11-25 coordinator: HTML v74 -> v75 (user-approved items, slide 124 + 125 only).
124: chart 2 gets two added curves (add-only; original (i), (ii), baseline untouched):
     (i) later names only, within-paper (original probe, pairs with both names item >= 1)      — dashed blue, open circles
     (i) 1st name only, pooled AUROC (probe refit on item-0 names; NOT comparable)             — dotted purple, squares
     + second legend row; cats block: Result clause (later-name pairs), 2 Caveat lines (post-hoc token mix; fit/eval + prompt format).
125: bottom sticky note (div.keyn "50.4% … vs 50.5% …") deleted (user-approved); Caveat line + misspelling share.
Sources: 381_stage13/b2_gennames_b/summary_predfirst_split_20261125/split_all.csv, 381_stage13/summary_later_pairs_20261125/report.md,
391_groups/summary_fabricated_editdist_20261125/report.md."""
import re
W = '/home/zhang.zhiqi2/jlens_work/'
t = open(W + '33_v73/deck_v74.html').read()
S = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, re.S))
assert len(S) == 184


def Y(v): return round(420 - (v - 0.4) * 466.6667, 1)


XS = [720.0, 820.0, 920.0, 1020.0, 1120.0, 1170.0, 1220.0]
LATER = [0.545, 0.542, 0.556, 0.510, 0.542, 0.598, 0.586]      # A_later_within (original probe), split_all.csv
FIRST = [0.659, 0.696, 0.695, 0.707, 0.784, 0.771, 0.736]      # B_first_pooled (refit, pooled), split_all.csv
F = "font-family=\"'Patrick Hand',Caveat,cursive\""


def curves():
    out = ['<g data-name="added 2026-11-25: (i) split by pre-name token">']
    pl = ' '.join(f'{x},{Y(v)}' for x, v in zip(XS, LATER))
    out.append(f'<polyline points="{pl}" fill="none" stroke="#3C78B4" stroke-width="2.4" stroke-dasharray="7 4" stroke-linejoin="round"/>')
    out += [f'<circle cx="{x}" cy="{Y(v)}" r="3.6" fill="#fff" stroke="#3C78B4" stroke-width="1.8"/>' for x, v in zip(XS, LATER)]
    pf = ' '.join(f'{x},{Y(v)}' for x, v in zip(XS, FIRST))
    out.append(f'<polyline points="{pf}" fill="none" stroke="#7A5FA8" stroke-width="2.4" stroke-dasharray="2 4" stroke-linecap="round" stroke-linejoin="round"/>')
    out += [f'<rect x="{x-3.2}" y="{Y(v)-3.2}" width="6.4" height="6.4" fill="#7A5FA8"/>' for x, v in zip(XS, FIRST)]
    # direct labels
    out.append(f'<text x="1020.0" y="{Y(0.510)+17}" font-size="12.5" fill="#3C78B4" text-anchor="middle" {F} font-weight="700">③ later names only: 0.51–0.60</text>')
    out.append(f'<text x="905.0" y="226.0" font-size="12.5" fill="#7A5FA8" text-anchor="middle" {F} font-weight="700">④ 1st name only · pooled AUROC (not comparable)</text>')
    # legend row 2
    out.append(f'<line x1="720.0" y1="476.0" x2="742.0" y2="476.0" stroke="#3C78B4" stroke-width="2.4" stroke-dasharray="7 4"/>')
    out.append(f'<text x="748.0" y="480.0" font-size="12.5" fill="#22304A" text-anchor="start" {F}>③ (i) later names only, within-paper</text>')
    out.append(f'<line x1="955.6" y1="476.0" x2="977.6" y2="476.0" stroke="#7A5FA8" stroke-width="2.4" stroke-dasharray="2 4" stroke-linecap="round"/>')
    out.append(f'<text x="983.6" y="480.0" font-size="12.5" fill="#22304A" text-anchor="start" {F}>④ (i) 1st name only, pooled (not comparable)</text>')
    out.append('</g>')
    return ''.join(out)


# ---------------- slide 124
m = S[123]; s = m.group(0); assert 'Names the model writes itself' in s
anchor = '<text x="963.6" y="462.0" font-size="12.5" fill="#22304A" text-anchor="start" font-family="\'Patrick Hand\',Caveat,cursive">(i) position before the name (secondary)</text>'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + curves())
old_cats = '<div class="cats" style="left:70px;top:488px;width:1150px;font-size:12.5px;line-height:1.22">'
assert s.count(old_cats) == 1
s = s.replace(old_cats, '<div class="cats" style="left:70px;top:488px;width:1150px;font-size:12px;line-height:1.17">')
old_res = '<span class="mk">the remainder (+0.050 to +0.062) appears only at L40–L52</span>.</div>'
assert s.count(old_res) == 1
s = s.replace(old_res, '<span class="mk">the remainder (+0.050 to +0.062) appears only at L40–L52</span> (same on later-name pairs only: +0.066 to +0.070).</div>')
old_cav = 'the confidence check and the H3 link were not pre-registered</span>.</div>'
assert s.count(old_cav) == 1
new_lines = ('the confidence check and the H3 link were not pre-registered; probe fitted on target + control names, tested on target papers only (not written in the pre-registration); its own chat prompt, so numbers are not comparable with other pages</span>.</div>'
             '</div><div class="cats" style="left:70px;top:626px;width:660px;font-size:12px;line-height:1.17"><div class="it"><span class="k"><span class="q">3</span><span class="q">4</span> Caveat (post hoc, not pre-registered):</span> <span class="ul">curve (i) mixed two pre-name tokens (a line break before the 1st name, “;” before later names)</span>; '
             '③ later names only <b>0.51–0.60</b> (above 0.5 only at L52–L56); ④ 1st name only = pooled AUROC, <span class="ul">not comparable</span>.</div>')
s = s.replace(old_cav, new_lines)
add_num = (' | (i) split (post hoc): later names only, within-paper: L16 0.545 [0.502, 0.585]; L24 0.542 [0.499, 0.584]; L32 0.556 [0.517, 0.595]; L40 0.510 [0.467, 0.549]; '
           'L48 0.542 [0.496, 0.584]; L52 0.598 [0.551, 0.641]; L56 0.586 [0.540, 0.626] | (i) 1st name only, pooled AUROC (refit): L16 0.659 [0.625, 0.694]; L24 0.696 [0.661, 0.730]; '
           'L32 0.695 [0.660, 0.730]; L40 0.707 [0.672, 0.740]; L48 0.784 [0.755, 0.815]; L52 0.771 [0.743, 0.799]; L56 0.736 [0.705, 0.767] | later-name pairs: confidence 0.681 [0.640, 0.718]; '
           '(ii) − confidence L40 +0.070 [+0.025, +0.121], L48 +0.069 [+0.020, +0.123], L52 +0.066 [+0.020, +0.115] -->')
c = s.index('<!-- plotted numbers:'); e = s.index('-->', c)
s = s[:e] + add_num + s[e + 3:]
t = t[:m.start()] + s + t[m.end():]

# ---------------- slide 125
S = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, re.S))
m = S[124]; s = m.group(0); assert 'Made-up names are not confused neighbours' in s
note = '<div class="keyn" style="top:574px"><span class="kn">50.4%</span><span class="kc">not in the data, vs 50.5% for the shuffled baseline</span></div>'
assert s.count(note) == 1
s = s.replace(note, '')
old = '“not in the data” means not in the author lists of the 9,108-paper cohort.</div></div>'
assert s.count(old) == 1
s = s.replace(old, '“not in the data” means not in the author lists of the 9,108-paper cohort; <span class="ul">a small share (≤ 0.6%) look like misspellings of a true author</span>.</div></div>')
t = t[:m.start()] + s + t[m.end():]
open(W + '34_v75/deck_v75.html', 'w').write(t)
print('ok', len(t))
