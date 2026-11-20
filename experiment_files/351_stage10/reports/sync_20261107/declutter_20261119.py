"""2026-11-19 declutter pass for the merged HTML deck (used by build_20261119_deck.py at assembly time).
On SVG chart slides: (1) "Plotted — ..." / "Earliest layer ..." number dumps leave the visible slide and go into the
chart's <desc> (+ an HTML comment), so the numbers stay inspectable; (2) the "How computed" block, the bold verdict and the
caveats are replaced by short versions (each <= 2 lines); (3) the footer becomes one short line in a reserved strip
(baseline y 693, x 70-1180) that stays clear of the page number and the prev / next buttons; text below the block moves up."""
import re, html
import apply_20261112r_lib as L

INK, GREYT = '#22304A', '#4B5363'
FOOT_Y = 693
SHORT = {
 'Exposure threshold (addendum 19)': dict(
  how='How computed: recognised = multiple-choice team result “strong”; written = ≥ 1 true author (R1 or R2); logistic fit on log10(1 + citations) + year; c50 = citations at p = 0.5; WLS of within-bin T − C on log citations (10 bins). 9,108 papers, 7,247 teams, team bootstrap ×2,000.',
  verdict='Confirmed (rule locked after the data were seen): ρ = 276 [203, 390], whole CI > 1, so writing needs far more exposure than recognising; within-bin T − C rises +0.030 [+0.014, +0.044] per 10× citations.',
  caveat='Caveats: one model; citations are a proxy for exposure; the writing c50 lies near the top of the range (16 papers above 11,038); ~25% guessing floor in low bins; without “uncertain” ρ = 1,184 [851, 1,712].',
  foot='391_groups/summary_exposure_prereg19/ (thresholds_ratio.csv, trend_by_bin.csv) · summary_exposure_20261114/exposure_by_bin.csv'),
 'Answer format (B), addendum 16': dict(
  how='How computed: corr = rate(true author written) − rate(chance author of a fixed same-field control paper); Δ = format − F0 within a group; DiD = Δ_A − Δ_B. 600 + 600 papers, team bootstrap ×2,000, Holm over 5 tests.',
  verdict='Supported through F4 only (the true first author’s initial is given): DiD A − B +0.085 [Holm 0.047, 0.124], p_Holm 0.0025; F4 alone Δ_A +0.103. F1–F3 not significant.',
  caveat='Caveats: labels come from another generation run; the stop rule was changed after shard 0 (deviation D16-4, recorded); greedy decoding only; C (300 papers) descriptive.',
  foot='391_groups/summary_a16_20261115/ (b_rates.csv, holm.csv) · config/prereg_addendum16.md'),
 'Name chain (D), addendum 16': dict(
  how='How computed: generation = share of papers writing ≥ 1 more true author (full name) after a one-author prefix; teacher forcing G(1) = S(true co-author given) − S(other paper’s author given), later authors scored; title-specific = true − mean of 5 false titles.',
  verdict='The effect exists (A: 11.8% vs 1.5%; G_A(1) +0.167 [0.147, 0.185], Holm p 0.0025) but is not paper-specific: title-specific +0.012 [−0.001, 0.025], larger without a title (+0.223), A ≈ B: a co-author network association.',
  caveat='Caveats: teacher-forced scores are preferences, not generation; greedy decoding only; labels from another run; C (227–228 papers) low power, descriptive.',
  foot='391_groups/summary_a16_20261115/ (d_gen.csv, d_contrasts.csv, holm.csv) · config/prereg_addendum16.md', y0=548),
 'Addendum 18b item 1: readout map': dict(
  how='How computed: within-bin target − control of spec at 9 prompt positions × 20 layers; locked rule: a position has CI > 0 at some L ≤ 48 while the name position’s CI at that layer includes 0. 600 papers, team bootstrap ×2,000.',
  verdict='Locked rule met in some cells (logit lens: year from L40, “:” L45, “Authors” L36; J-lens first title token L8; probe title L32), but the effects are small (+0.008 to +0.049).',
  caveat='Caveats: 672 cells tested, 60 with CI > 0, ~17 expected by chance, no correction, so these are position hints only; the rule compares two CIs, not a paired test; the probe is trained on 600 papers.',
  foot='381_stage13/summary_a18b_item1/ (item1_map.csv, item1_criterion.csv) · config/prereg_addendum18b.md'),
 'Stage 12: where the paper information travels': dict(
  how='How computed: recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄]; P1 = a set of positions, P2 = one component in one layer; mean of 5 false titles (thin dashed = false_0). 1,186 papers, team-cluster 95% CI.',
  foot='391_groups/summary_b1_p12f/p12f_mean5.csv · b1_p12f_report.md · Stage 12 N1 / N2 / F2 reports'),
 'Addendum 18b item 6: MLP memory lookup': dict(
  how='How computed: R = mean_p[nlr(patched) − nlr(false)] / mean_p[nlr(true) − nlr(false)], 5 false titles; the layer-l MLP or attention output over the aligned tail is set to out_F + P(out_T − out_F). 600 papers, paired team bootstrap.',
  verdict='Descriptive: the whole MLP output recovers 0.158–0.275 (peak L54), attention 0.055–0.146; the 512 author-name directions only 0.022–0.042 (random 0.014–0.023): paper information, not ready-made name directions.',
  caveat='Caveats: control papers recover slightly more (L52–L54); the author subspace holds 0.339 of the name-row variance; self-check WARN, rank match 0.538 (bf16 batch shapes), continued by rule.',
  foot='381_stage13/summary_a18b_item6/ (item6_patch_mean5.csv, item6_contrasts.csv) · config/prereg_addendum18b.md'),
 'Addendum 18b item 4: L57–L61 mean ablation': dict(
  how='How computed: loss = S(none) − S(ablated); one layer’s attention or MLP output at the tail and name inputs replaced by a fixed reference mean (586 other papers); criterion: paired CI of loss(MLP) − loss(attention) > 0. 600 papers.',
  verdict='Locked criterion met at all 5 layers: MLP − attention loss +0.037 to +0.046, mean +0.040 [+0.036, +0.045]; attention ≈ 0 (≤ 0.0012); each MLP layer removes 11–14% of S.',
  caveat='Caveats: mean ablation, one layer and component at a time (no joint effects); target papers lose more; self-check WARN, rank match 0.627 / 0.527 (bf16), continued by rule.',
  foot='381_stage13/summary_a18b_item4/ (item4_table.csv, item4_criterion.csv) · config/prereg_addendum18b.md'),
 'The Stage 11 timing holds for all 5 false titles': dict(
  how='How computed: X6 R(l) = mean(patched − false) / mean(true − false) per false title, averaged over 5; X7 S(l) = T(l) − F(l), the knockout loss minus the same knockout on the false-title run. 1,186 papers, team-cluster 95% CI.',
  foot='381_stage13/summary_x6/x6_recovery.csv · summary_b1_x7f/x7f_knockout.csv · x6_report.md, x7_report.md'),
 'Addendum 18b item 5: title-token importance': dict(
  how='How computed: loss = S(true) − S(variant); Δ = loss(synonym) − loss(random), paired on the same draws; word classes and tables fixed before any GPU output. 600 papers (papers without a replaceable word left out), team bootstrap.',
  verdict='Descriptive: random content words cost +0.374 [+0.354, +0.394] (the whole signal), WordNet synonyms only +0.087; Δ −0.287 [−0.306, −0.269]. Rare words, function words and first / last tokens cost much less.',
  caveat='Limits: WordNet synonyms are crude; random replacement changes more tokens (12.8 vs 5.6), so part of Δ may be the amount changed; fewer papers with synonyms (rare words 397); no locked criterion.',
  foot='381_stage13/summary_a18b_item5/ (item5_table.csv) · a18b_config/item5_variants_v3.parquet · config/prereg_addendum18b.md'),
 'The probe on every name token': dict(
  how='How computed: spec = score(true title) − score(false_0) per name token, ranked by role → nlr; T − C pooled within citation bin. L40; V0 1,395–1,706 and Vpd 3,046–4,812 papers; team-cluster 95% CI.',
  foot='381_stage13/summary_alltok/alltok_controls.csv · summary_e4b5/perdonor_by_run_layer.csv · e4b_alltok.md'),
 'Name-position probe: H3 supported on the same scale': dict(
  how='How computed: name-position probe = ridge from the layer-l residual at the name-predicting position to the model’s own L63 state, ranked among 9,137 name tokens; spec = probe(true) − probe(false); within-bin T − C. 4,654 papers, team CI.',
  foot='381_stage13/summary_b2_np/ (np_lens_compare_v2.csv, np_role_layer_v2.csv) · reports/b2_np_report_v2.md'),
 'Names the model writes itself: true vs fabricated (C24)': dict(
  how='How computed: within-paper AUROC over all true (M) vs fabricated (H) name pairs: 1 if probe(M) > probe(H), 0.5 for ties. 518 target papers, 3,388 pairs, L16–L56, team-cluster 95% CI.',
  verdict='Exploratory (not pre-registered): middle layers separate true from fabricated names (0.72–0.78), but output confidence alone gives 0.711; the remainder (+0.050 to +0.062) appears only at L40–L52.',
  caveat='The pre-registered addendum-15 criterion passed at all 7 layers (L48 0.782). Caveats: live generation (chat template); rule-matched labels; the confidence check and the H3 link were not pre-registered.',
  foot='381_stage13/b2_gennames_b/summary/ (probe_within.csv, robust_posthoc.csv) · summary_c24_optB_20261114/report.md'),
 'C: fabricated names (exploratory)': dict(
  how='How computed: each fabricated name is classed (first match): co-author of a true author → same-field author → other cohort author → not in the data; chance = names shuffled within field (20×). 8,872 papers, 40,219 names, team bootstrap.',
  verdict='Not supported (exploratory, not pre-registered): half of the fabricated names are people not in the data (50.4% [49.0, 51.7], shuffled 50.5%); co-authors 4.0% (shuffled 1.3%), but T − C ≈ 0 with full-name matching.',
  caveat='Caveats: only the open answers (greedy) of the original label package; “not in the data” means not in the author lists of the 9,108-paper cohort.',
  foot='391_groups/summary_fabricated_20261114/ (report.md, class_shares_by_group.csv) · 14_groups/fabricated_names_20261114.py'),
}
DUMP = ('Plotted', 'Earliest layer meeting')
ENDKEYS = ('How computed', 'Plotted', 'Earliest', 'Caveats', 'Limits:', 'Neighbour confusion', 'Pre-registered (add', 'Descriptive',
           'Locked criterion met', 'B supported', 'D: the effect', 'Confirmed under', 'Under the locked', 'Multiplicity', 'Exploratory confidence')
TXT = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.S)


def plain(inner): return html.unescape(re.sub(r'<[^>]+>', '', inner))


def info(m):
    a = m.group(1)
    g = lambda k, d=None: (re.search(rf' {k}="([^"]*)"', a) or [None, d])[1]
    inner = m.group(2)
    n = max(1, inner.count('<tspan'))
    dys = [float(x) for x in re.findall(r'dy="([\d.]+)"', inner)]
    lh = max(dys) if dys else float(g('font-size', 12)) * 1.3
    return dict(x=float(g('x', 0)), y=float(g('y', 0)), fs=float(g('font-size', 12)), src='class="src"' in a, txt=plain(inner),
                n=n, lh=lh, bold='font-weight="700"' in a, start=m.start(), end=m.end())


def emit(y, txt, fs, col, bold=False, maxlines=2, minfs=9.5):
    f = fs
    while len(L.wrap(txt, f, 1140)) > maxlines and f > minfs: f = round(f - 0.25, 2)
    t, h = L.para(70, y, txt, f, 1140, col, lh=f * 1.28)
    if bold: t = t.replace('<text ', '<text font-weight="700" ', 1)
    return t, h, len(L.wrap(txt, f, 1140)), f


FOOTX = {'method: Knockout (block)': 385}
FOOTW = {'method: Groups and samples': 470}
FOOTTXT = {'method: Groups and samples': 'Counts: cohort/papers.parquet · Stage 11 sample · X3 pair table'}
# method slides whose one-line How-computed sat on the drawing: the line becomes the footer (the formula box carries the math)
HOW2FOOT = {'method: Replacement (patching)': 'How computed: R(l) = (patched − false) / (true − false), mean of 5 false titles, 1,186 papers, team cluster · 381_stage13/summary_x6/x6_recovery.csv'}


def foot(txt, x=70):
    # class "src" is drawn at 12.5 px by the deck CSS whatever the attribute says: measure at 12.5, cut to stay left of the page number
    f = 11
    while L.width(txt, 12.5) > 1160 - x and ' · ' in txt: txt = txt.rsplit(' · ', 1)[0]
    return f'<text x="{x}" y="{FOOT_Y}" class="src" font-size="{f}" fill="#8a8f98" text-anchor="start">{html.escape(txt, quote=False)}</text>'


def declutter(sec, report):
    if 'class="slide mf"' not in sec: return sec
    lab = re.search(r'aria-label="([^"]*)"', sec).group(1)
    items = [info(m) for m in TXT.finditer(sec)]
    sp = SHORT.get(lab)
    dumps = [it for it in items if it['txt'].startswith(DUMP)]
    rem, add, shift_from, delta = [], [], None, 0.0
    if sp:
        keyed = [it for it in items if 69 <= it['x'] <= 71 and it['txt'].startswith(ENDKEYS)]
        y0 = min(it['y'] for it in keyed); y1 = max(it['y'] for it in keyed)
        block = [it for it in items if 69 <= it['x'] <= 71 and y0 <= it['y'] <= y1 and not (it['src'] and it['y'] >= 690)]
        rem += block
        old_bottom = max(it['y'] + (it['n'] - 1) * it['lh'] for it in block)
        y0 = max(y0, sp.get('y0', 0)); y, last = y0, y0
        for kind in ('how', 'verdict', 'caveat'):
            if kind not in sp: continue
            fs, col, bold = {'how': (10.5, GREYT, False), 'verdict': (13, INK, True), 'caveat': (12, GREYT, False)}[kind]
            t, h, nl, f = emit(y, sp[kind], fs, col, bold)
            add.append(t); last = y + h - f * 1.28; y += h + 6
            report.append(f'{lab[:40]}: {kind} {nl} line(s) at fs {f}')
        delta = old_bottom - last
        shift_from = y1
    # footer: every src text at y >= 690 is replaced by one short line in the reserved strip
    feet = [it for it in items if it['src'] and it['y'] >= 690]
    if feet:
        rem += feet
        ftxt = sp['foot'] if sp else ' · '.join(it['txt'] for it in feet)
        fx = FOOTX.get(lab, 70)
        if lab in HOW2FOOT:
            rem += [it for it in items if it['txt'].startswith('How computed') and it not in rem]
            add.append(foot(HOW2FOOT[lab], fx))
        else:
            add.append(foot(FOOTTXT.get(lab) or (ftxt if sp else shorten_src(ftxt, FOOTW.get(lab, 1110 - fx))), fx))
    rem += [d for d in dumps if d not in rem]
    # other text sitting in the footer strip moves just above it
    low = [it for it in items if not it['src'] and 678 < it['y'] <= 705 and it not in rem and it['txt'].startswith('How computed')]
    fix_low = {(it['start'], it['end']) for it in low}
    if not rem: return sec
    ids = {(it['start'], it['end']) for it in rem}
    out, pos = [], 0
    for it in sorted(rem, key=lambda q: q['start']):
        out.append(sec[pos:it['start']]); pos = it['end']
    out.append(sec[pos:]); s2 = ''.join(out)
    # move text below the block up by delta (bullets / source lines under the block)
    if shift_from is not None and delta > 4:
        def mv(m):
            it = info(m)
            if it['y'] > shift_from and not (it['src'] and it['y'] >= 690) and it['x'] <= 90:
                return re.sub(r' y="([\d.]+)"', f' y="{it["y"] - delta:.1f}"', m.group(0), 1)
            return m.group(0)
        s2 = TXT.sub(mv, s2)
    if low:
        s2 = TXT.sub(lambda m: re.sub(r' y="([\d.]+)"', ' y="678.0"', m.group(0), 1) if (678 < info(m)['y'] <= 705 and 'class="src"' not in m.group(1) and info(m)['txt'].startswith('How computed')) else m.group(0), s2)
    s2 = s2.replace('</svg>', ''.join(add) + '</svg>', 1) if s2.count('</svg>') == 1 else s2.replace('\n</svg>', ''.join(add) + '\n</svg>', 1)
    if dumps:
        d = ' | '.join(x['txt'] for x in dumps)
        s2 = re.sub(r'(<svg\b[^>]*>)', lambda m: m.group(1) + f'<desc>{html.escape(d, quote=False)}</desc>', s2, 1)
        s2 = s2.replace('</section>', f'<!-- plotted numbers: {html.escape(d, quote=False).replace("--", "–")} --></section>', 1)
        report.append(f'{lab[:40]}: {len(dumps)} number dump(s) moved to <desc>')
    return s2


def shorten_src(t, maxw=1090):
    """old method-slide footers: keep each item's label + last path part"""
    parts = [p.strip() for p in t.split(' · ')]
    out = []
    for p in parts:
        p = re.sub(r'[\w./\-\[\]{}*…]+/([\w.\-\[\]{}*…]+)', r'\1', p)
        out.append(p)
    s = ' · '.join(out)
    while L.width(s, 12.5) > maxw and ' · ' in s: s = s.rsplit(' · ', 1)[0]
    return s
