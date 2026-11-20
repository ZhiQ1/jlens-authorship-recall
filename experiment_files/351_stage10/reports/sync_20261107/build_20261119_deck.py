"""2026-11-19 rework of the merged HTML deck (user instructions of 2026-11-18, relayed by the coordinator).
Source = merged_deck/stage1_11_deck.html.before_20261119 (= published v39) -> merged_deck/stage1_11_deck.html.
  1. Delete the divider "Added after the defence (2026-11-05)" (v39 slide 85) and every process / patch label
     ("after the defence", "post-defence", "post-hoc" as a chapter label, "CPU leftovers", "redo programme", "since 11-14", ...).
     Statistical status (confirmed / supported / exploratory / descriptive; "rule locked after the data were seen";
     "not pre-registered") stays, phrased as the status of a result.
  2. Every text-only slide from v39 S43 on gets a figure (inline SVG chart in deck style, a schematic, or a crop of an
     existing chart already in the deck), or is rebuilt with one:
       S29 rebuilt (exposure: recognition vs recall rates per citation bin + fitted curves, c50 marks, rho);
       S59 split into S59 (answer format B: corrected writing rate F0 vs F1..F4, A vs B) and S60 (name chain D);
       S82 rebuilt as HTML (what we learned + lens-curve figures); S84 rebuilt as HTML (limits + sample-size chart);
       charts added on S43, S51, S60(v39), S62, S63, S74, S75, S77, S83, S86, S87, S89, S90, S91.
  3. Every new chart carries a small formula and a grey "n = ...".
  4. All visible Chinese translated to English (no speaker-notes mechanism in this deck -> Chinese dropped).
  5. Hard-coded "slide N" references remapped to the new order.
Writes build_20261119_deck.json (order, fate of every v39 slide). Idempotent (always rebuilds from the backup)."""
import re, json, html, base64, io, csv, math
from pathlib import Path
from PIL import Image
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, GR, RD, LIGHT, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
G = Path('/scratch/zhang.zhiqi2/jlens/391_groups')
SRC = D / 'stage1_11_deck.html.before_20261119'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 92, len(ms)
head, tail = s[:ms[0].start()], s[ms[-1].end():]
assert head.count('.lead{position:absolute;left:70px;top:38px;') == 1
head = head.replace('.lead{position:absolute;left:70px;top:38px;', '.lead{position:absolute;left:70px;top:18px;')
S = {k + 1: m.group(0) for k, m in enumerate(ms)}
ORIG = dict(S)
GREY = '#8a8f98'
SERIF = "'STIX Two Math','Cambria Math','DejaVu Serif','Times New Roman',serif"
CJK = re.compile('[　-〿一-鿿＀-￯]')
FATE = {}          # v39 slide -> text
CHANGED = {}


def note(k, msg): CHANGED.setdefault(k, []).append(msg)


def rep(k, a, b, msg, count=1):
    assert S[k].count(a) == count, (k, S[k].count(a), a[:80])
    S[k] = S[k].replace(a, b); note(k, msg)


def ins(k, html_, msg):
    assert S[k].endswith('</section>')
    S[k] = S[k][:-len('</section>')] + html_ + '</section>'; note(k, msg)


def esc(x): return html.escape(str(x), quote=False)


def fmt(v, d=3, sign=True):
    return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')


def cif(lo, hi, d=3, sign=True): return f'[{fmt(lo, d, sign)}, {fmt(hi, d, sign)}]'


def rows(p): return list(csv.DictReader(open(p, encoding='utf-8')))


# ======================================================================= helpers for inline charts
def ovl(left, top, w, h, body, aria):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(aria)}" '
            f'style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;z-index:2;overflow:visible">{body}</svg>')


def ftext(x, y, s_, fs=12.5, anchor='start'):
    """small formula (serif italic, ink)"""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{INK}" font-style="italic" text-anchor="{anchor}" font-family="{SERIF}">{esc(s_)}</text>'


def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'


def fbox(x, y, s_, fs=12.5):
    w = L.width(s_, fs) * 0.82 + 18
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{fs + 9:.1f}" rx="7" fill="#FFF6DC" stroke="{OR}" stroke-width="1.2"/>'
            + ftext(x + 9, y + fs + 2.5, s_, fs)), w


def vbar(ax, x, v, w, col, op=0.85, hollow=False):
    y0, y1 = ax.Y(0), ax.Y(v)
    fill = 'none' if hollow else col
    return f'<rect x="{ax.X(x) - w / 2:.1f}" y="{min(y0, y1):.1f}" width="{w:.1f}" height="{abs(y0 - y1):.1f}" fill="{fill}" fill-opacity="{op}" stroke="{col if hollow else INK}" stroke-width="{1.8 if hollow else 1}"/>'


def hbar(x0, y, wpx, h, col, op=0.85):
    return f'<rect x="{min(x0, x0 + wpx):.1f}" y="{y:.1f}" width="{abs(wpx):.1f}" height="{h:.1f}" fill="{col}" fill-opacity="{op}" stroke="{INK}" stroke-width="1"/>'


def card_img(path_png, box, width_px, caption, fmt_='JPEG'):
    im = Image.open(path_png).convert('RGB').crop(box)
    b = io.BytesIO(); im.save(b, fmt_, quality=86); data = base64.b64encode(b.getvalue()).decode()
    return f'<figure class="card" style="margin:0"><img alt="{esc(caption)}" src="data:image/jpeg;base64,{data}"><figcaption>{esc(caption)}</figcaption></figure>', im.size


def deck_img(k, j=0):
    m = list(re.finditer(r'src="data:image/(\w+);base64,([^"]+)"', ORIG[k]))[j]
    return io.BytesIO(base64.b64decode(m.group(2)))


# ======================================================================= 1. labels
rep(1, 'Stages 10–13 · post-defence additions (2026-11-05) at the end', 'Stages 10–13', 'cover: process label removed')
rep(2, 'new results sit inside their lines: A exposure (add. 19) · D format, chain (add. 16) · 12–13 route, title words, made-up names (add. 18b, C)',
    'also in the lines: A exposure threshold · D answer format, co-author chain · 12–13 route, title words, made-up names', 'roadmap pill reworded')
rep(12, '<b>Order:</b> the small samples now run', '<b>Small samples:</b>', 'opener box reworded')
rep(12, ' (slides 13–16): each slide’s own conclusion leads to the next', ' (slides 13–16), each conclusion leading to the next', 'opener box reworded')
rep(20, '8E external audit (post-hoc)', '8E external audit (not pre-registered)', 'status wording')
rep(20, 'post-hoc only', 'not pre-registered', 'status wording')
rep(33, '<b>Since 11-14 · full cohort</b>', '<b>Exposure and co-author chain · full cohort</b>', 'card header reworded')
rep(44, '<b>Moved:</b> the Stage 4 and 7.2 small-sample slides now sit in Line A (slides 13, 15); the summary (slide 51) still quotes them · Stage 11 design (slide 47) now comes before its method pictures',
    'Stage 4 and 7.2 small-sample results are in Line A (slides 13, 15); the summary (slide 51) quotes them · Stage 11 design: slide 47, then its method pictures', 'opener box reworded')
rep(61, '<b>Since 11-17 (add. 18b):</b> ④ goes on:', '<b>Add. 18b:</b> ④ goes on:', 'box header reworded')
rep(67, '<b>Update 11-17/18</b>', '<b>Latest results</b>', 'box header reworded')
rep(68, '<b>Refined since 11-17:</b>', '<b>Refined:</b>', 'box header reworded')
rep(74, '<b>Retrieval (added 2026-11-05): </b>', '<b>Retrieval: </b>', 'process label removed')
rep(74, '; post-defence', '', 'process label removed')
rep(75, '<b>Post-hoc checks: </b>', '<b>Checks not pre-registered: </b>', 'status wording')
rep(83, 'Stage 12–13 · 2026-11-15/18', 'Stage 12–13', 'tag: date removed')
rep(83, '← slide 82: what we learned up to 11-14. <b>Here:</b> the results of 11-15 to 11-18, each with its status → limits, slide 84',
    '← slide 82: read early, spoken late. <b>Here:</b> who writes it and what it needs, each with its status → limits, slide 84', 'lead reworded')
TAGS = {86: ('Added after the defence · groups', 'Groups · A / B / C / D'), 87: ('Added after the defence · re-runs', 'Groups · Stage 11 E1'),
        88: ('Added after the defence · groups', 'Groups · recognition'), 89: ('Added after the defence · re-runs', 'Groups · Stage 12 P1 / P2'),
        90: ('Added after the defence · CPU', 'Stage 13 · checks'), 91: ('Added after the defence · redo programme', 'Stage 12–13 · replications'),
        92: ('Added after the defence · limits', 'Limits')}
for k, (a, b) in TAGS.items():
    rep(k, f'<span class="tag">{a}</span>', f'<span class="tag">{b}</span>', 'tag reworded')
rep(87, '<h2 style="font-size:52px">Re-runs: numerator and denominator</h2>', '<h2 style="font-size:52px">Recovery by group: numerator and denominator</h2>', 'title reworded')
rep(87, 'aria-label="Re-runs: numerator and denominator"', 'aria-label="Recovery by group: numerator and denominator"', 'aria')
rep(90, '<h2 style="font-size:52px">CPU leftovers on existing data (post-hoc)</h2>', '<h2 style="font-size:52px">Retrieval, behaviour and interval checks</h2>', 'title reworded')
rep(90, 'aria-label="CPU leftovers on existing data (post-hoc)"', 'aria-label="Retrieval, behaviour and interval checks"', 'aria')
rep(90, 'No new GPU runs · descriptive only · not in the pre-registration except the X5 retrieval curve',
    'Existing data, no new GPU runs · descriptive · not pre-registered except the X5 retrieval curve', 'subtitle reworded')
rep(91, '<h2 style="font-size:52px">Redo programme (addenda 10–14)</h2>', '<h2 style="font-size:52px">Replications with rules fixed first (addenda 10–14)</h2>', 'title reworded')
rep(91, 'aria-label="Redo programme (addenda 10–14)"', 'aria-label="Replications with rules fixed first (addenda 10–14)"', 'aria')
rep(91, 'status 2026-11-08', 'status as of 2026-11-08', 'subtitle')
rep(91, 'post-hoc confidence check', 'confidence check, not pre-registered', 'status wording')
rep(92, 'Written 2026-11-06; last three items added 2026-11-08 (v30)', 'Design and data limits that new runs cannot remove', 'subtitle reworded')
rep(92, '<b>Post hoc and single title: </b>parity tolerance 0.25 → 0.5 was used, a post-hoc change',
    '<b>Tolerance and single title: </b>parity tolerance 0.25 → 0.5 was used, a change made after seeing the data', 'status wording')
rep(78, 'positive only post hoc (per-donor)', 'positive only in the per-donor version (not pre-registered)', 'status wording')
S[80] = S[80].replace('(post hoc, corrected)', '(not pre-registered, corrected)').replace('(post hoc)', '(not pre-registered)').replace('(post hoc, generation time)', '(not pre-registered, generation time)'); note(80, 'status wording')
rep(81, 'Exploratory, post hoc (not pre-registered)', 'Exploratory (not pre-registered)', 'status wording')
FATE[85] = 'deleted (divider "Added after the defence"; its list of contents is covered by the slides themselves)'
order = list(range(1, 29)) + ['29n'] + list(range(30, 59)) + ['59f', '59d'] + list(range(60, 82)) + ['82n', 83, '84n'] + list(range(86, 93))
P = {o: i + 1 for i, o in enumerate(order)}

# ======================================================================= 4. Chinese -> English (SVG <text>, badges, .howr, li)
TR = [
 ('怎么算：target = A + C，control = B + D', 'How computed: target = A + C, control = B + D · 9,108 papers; 593 + 593; 1,178 pairs'),
 ('怎么算：nlr = log10(1/rank) = −log10(rank)；spec = true', 'How computed: nlr = log10(1/rank) = −log10(rank); spec = true − mean(false_0..4) · one example paper, L63, 16 tokens · source: paper_title_contrasts.parquet'),
 ('CIs: Stage 10–12 published tables', None),   # handled by suffix replacement below
 ('怎么算：target−control = Σ_b w_b', 'How computed: T − C = Σ_b w_b (mean_t,b − mean_c,b), w_b ∝ n_t n_c / (n_t + n_c) · 10 bins, 7,247 teams'),
 ('怎么算：nlr = log10(1/rank) = −log10(rank)；rank', 'How computed: nlr = log10(1/rank) = −log10(rank); rank = 1 + #(logit > gold logit) · one example paper, “Co”, logit lens · source: raw/logit/L*/shard_011.npz row 25029'),
 ('怎么算：R(l) = mean_papers(nlr_patched@l − nlr_false) / mean_papers(nlr_true − nlr_false)，5 个假标题平均', 'How computed: R(l) = mean_papers(nlr_patched@l − nlr_false) / mean_papers(nlr_true − nlr_false), mean over 5 false titles · 1,186 papers · team cluster · source: x6_recovery.csv'),
 ('锁定规则：部分格子满足', 'Locked rule: met in some cells · small · uncorrected'),
 ('怎么算：T−C = 引用分箱内', 'How computed: T−C = within-citation-bin target − control of spec (spec = true title − mean of 5 false titles, nlr = log10(1/rank), ranked within the 9,137 name-token ids); locked rule: a position group has T−C CI > 0 at some layer L ≤ 48 while the name position (surname first token) at that layer has a CI including 0 → “the shelf is reached at that position first” · 600 papers (Stage 11 subsample) · team cluster, 2,000 draws · 381_stage13/summary_a18b_item1/item1_map.csv, item1_criterion.csv'),
 ('按锁定规则：部分格子满足', 'Under the locked rule some cells meet “reached at that position first” (logit lens, surname first token: year from L40, “:” from L45, “Authors” L36; J-lens first title token L8; probe all title tokens L32, year L32), but the effects are small (+0.008 to +0.049).'),
 ('多重比较：', 'Multiplicity: 672 cells tested at L ≤ 48 (3 readouts × 2 gold tokens × 8 position groups × 14 layers), 60 with CI > 0; with independent cells and no effect about 17 would have CI > 0 by chance at one-sided 2.5% (adjacent layers are highly correlated, so this is only an order of magnitude). Not corrected: position hints only, no conclusion that “the shelf is at the year / title”.'),
 ('前提：规则比较两个 CI', 'Caveats: the rule compares two CIs (position CI > 0, name-position CI includes 0), not a paired difference test; the probe is trained on these 600 papers only, weaker than the 9,108-paper probe of addendum 11; results for the “first” gold token are in the number line above.'),
 ('怎么算：recovery(l) = mean_p[ P̄_p(l) − F̄_p ] / mean_p[ T̄_p − F̄_p ]（P1', 'How computed: recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p] (P1 position subsets / P2 one component in one layer; mean over 5 false titles, thin dashed = false_0 only) · Stage 11 sample, 1,186 papers · team-cluster 95% CI · 391_groups/summary_b1_p12f/p12f_mean5.csv (b1_p12f_report.md)'),
 ('描述性（无锁定判据）', 'Descriptive (no locked criterion)'),
 ('怎么算：R = mean_p[ nlr(替换后)', 'How computed: R = mean_p[nlr(patched) − nlr(false title)] / mean_p[nlr(true title) − nlr(false title)], mean over 5 false titles; over the whole aligned tail (P2 positions) the layer-l MLP or attention output is replaced by out_F + P(out_T − out_F); author subspace = top 512 right singular vectors of the 9,137 name-token lm_head rows × final-norm weights (centred; 0.339 of the variance), control = random 512 dimensions · 600 papers · team cluster, 2,000 draws (paired) · 381_stage13/summary_a18b_item6/item6_patch_mean5.csv, item6_contrasts.csv'),
 ('描述性：替换整个 MLP', 'Descriptive: patching the whole MLP output recovers 0.158–0.275 of the true − false gap (highest at L54), attention 0.055–0.146; the 512 dimensions aligned with author-name output directions recover only 0.022–0.042, slightly above random 512 dimensions (0.014–0.023); most sits in the orthogonal part (0.132–0.229) → these MLPs carry paper information, but not as ready-made “author-name directions”.'),
 ('前提：control 论文的恢复比例', 'Caveats: control papers recover slightly more than target (L52–L54 CI < 0, L55–L56 include 0); the author subspace holds only 0.339 of the name-row variance; self-check WARN: unpatched false_0 ranks match the stored Stage 11 rows in 0.538 of cases (threshold 0.95, bf16 batch-shape differences), continued as the rule says.'),
 ('锁定判据：达成', 'Locked criterion: met (5 / 5 layers)'),
 ('怎么算：loss = S(不消融)', 'How computed: loss = S(no ablation) − S(ablated), S = final-output nlr(true title) − mean of 5 false titles (paper mean); ablation = the layer-l attention or MLP output at the post-title tail (p1..p9) and all name input positions replaced by a reference mean fixed in advance (same position, 586 other papers, 5 false titles); criterion = paired CI of loss(MLP) − loss(attention) > 0 · 600 papers · team cluster, 2,000 draws (same draws → paired) · 381_stage13/summary_a18b_item4/item4_table.csv, item4_criterion.csv'),
 ('按锁定判据：L57–L61', 'Locked criterion met: at every layer L57–L61 ablating the MLP costs more than ablating attention (paired difference +0.037 to +0.046, mean +0.040 [+0.036, +0.045], all CIs > 0) → “the last layers are written by MLPs”. Attention ablation costs ≈ 0 (≤ 0.0012); each MLP layer removes 11–14% of S.'),
 ('前提：均值消融', 'Caveats: mean ablation, one layer and one component at a time; redundancy between layers and joint effects not tested; target papers lose more (T − C of the difference > 0); self-check WARN: unablated ranks match stored Stage 11 E1 rows in true 0.627 / false_0 0.527 of cases (threshold 0.95, bf16 batch-shape differences), continued as the rule says.'),
 ('怎么算：X6：', 'How computed: X6: R(l) = mean_papers(nlr_patched@l − nlr_false) / mean_papers(nlr_true − nlr_false); mean R = simple mean of the 5 titles’ R (same averaging in every bootstrap draw) · X7: T(l) = mean(kT64 − kT_l) / mean(true − false); F(l) = mean(kF64 − kF_l) / mean(true − false); S(l) = T(l) − F(l) (paper-specific loss) · 1,186 papers (593 + 593), all post-title positions, final output · team-cluster 95% CI · summary_x6/x6_recovery.csv; summary_b1_x7f/x7f_knockout.csv'),
 ('怎么算：loss = S(true) − S(替换后)', 'How computed: loss = S(true) − S(variant), S = paper-mean nlr(true title) − mean of 5 false titles; Δ = loss(synonym) − loss(random), paired on the same bootstrap draws; word classes and replacement tables fixed before any GPU output (rare = title document frequency ≤ 5 in the cohort; synonyms = WordNet 3.0; function words = fixed near-synonym table) · 600 papers (Stage 11 subsample); papers without a replaceable word for a variant are left out · team cluster, 2,000 draws · 381_stage13/summary_a18b_item5/item5_table.csv'),
 ('描述性：内容词', 'Descriptive: replacing content words by random tokens costs +0.374 [+0.354, +0.394] (the whole signal; S becomes −0.046); synonyms cost only +0.087; Δ −0.287 [−0.306, −0.269]. Rare words, function words and the first / last token cost much less.'),
 ('局限：WordNet', 'Limits: WordNet synonyms are crude (meaning not guaranteed), so this is only a weak “meaning kept” test; random replacement changes more tokens (content words 12.8 vs 5.6 tokens on average), so part of Δ may come from the amount changed; fewer papers have synonyms (rare words 397 papers); 600-paper subsample, no locked criterion.'),
 ('V5x0 含泄漏', 'V5x0 includes leakage, sensitivity only'),
 ('怎么算：spec(p) = score', 'How computed: spec(p) = score(p, X_true) − score(p, X_false_0), each name token ranked by role → nlr; T − C: target − control = Σ_b w_b [mean_{target,b} − mean_{control,b}], w_b = n_t n_c/(n_t+n_c), normalised · L40; given name 1,706 / surname 1,395 / initial 1,590 papers (V0); Vpd 3,046 / 4,654 / 4,812 papers · team-cluster 95% CI · alltok_controls.csv; perdonor_by_run_layer.csv'),
 ('按补充 11 预注册判据通过', 'Passed the addendum-11 pre-registered criterion (surname first token, L40/L48); a later check found the lens intervals also exclude 0 and the scales differ, so sizes could not be compared → partly supported; after the addendum-17 locked same-scale test: supported on the same scale'),
 ('首字母的对照行', 'The initial’s control row is about half the signal: about half of that signal is not paper-specific'),
 ('怎么算：名字位置 probe', 'How computed: name-position probe: ridge fit from the layer-l residual at the “predict the name token” position to the model’s own L63 state at that position, ranked within the 9,137 name tokens → nlr; spec = probe(true) − probe(false) (methods handbook: name-position probe spec) · T − C: pooled within-bin difference · Vpd 4,654 papers (surname first token), layers L32–L56 · team-cluster 95% CI · summary_b2_np/np_lens_compare_v2.csv; np_role_layer_v2.csv'),
 ('未定（探索性）', 'Undecided (exploratory)'),
 ('怎么算：论文内 AUROC', 'How computed: within-paper AUROC over all M–H name pairs of each target paper (≥ 1 true author M and ≥ 1 fabricated name H): 1 if probe(M) > probe(H), 0.5 for ties, then averaged (methods handbook: 2-11b within-paper AUROC) · 518 target papers, 3,388 M–H pairs, L16–L56 · team-cluster 95% CI · b2_gennames_b/summary/probe_within.csv; robust_posthoc.csv'),
 ('2026-11-15（事后，探索性）', 'Exploratory confidence check (not pre-registered): after a name is written, middle layers separate true from fabricated names (probe 0.72–0.78), but most of this is explained by the model’s own output confidence (baseline 0.711); the part beyond confidence appears only at L40–L52 (+0.050 to +0.062: L40 +0.059 [0.025, 0.094], L48 +0.062 [0.025, 0.100], L52 +0.050 [0.018, 0.084]), matching the hand-over zone.'),
 ('历史：补充 15 预注册判据', 'Pre-registered (add. 15): (ii) above rank and name-feature baselines at all 7 layers L16–L56 (L48 0.782 [0.754, 0.812]); (i) not readable before the name (not above rank baseline).'),
 ('前提：chat 模板', 'Caveats: generated live under the chat template (not teacher forcing); labels from rule matching; control descriptive only; the link to H3 was not pre-registered; the confidence check was not pre-registered; the match between the remaining part and the hand-over zone is an observation, not a test.'),
 ('邻居混淆（C）：不支持', 'Neighbour confusion (C): not supported (exploratory)'),
 ('怎么算：每个编造的名字', 'How computed: each fabricated name (no match to a true author on surname + first initial) is classed in order, first match wins: co-author of a true author → real author in the same field → other cohort author → not in the data; share of classifiable names (pooled ratio); chance = fabricated names shuffled within field and re-classed (20 times); full name / rare surname as sensitivity · 8,872 papers, 40,219 names · team cluster, 2,000 draws · 391_groups/summary_fabricated_20261114/report.md'),
 ('邻居混淆（C）不支持', 'Neighbour confusion (C) not supported (exploratory, not pre-registered): half of the fabricated names are people not in the data (50.4% [49.0, 51.7]), the same as the shuffled same-field baseline 50.5%; co-authors are 4.0% [3.0, 5.2], above the shuffled 1.3%, but with full-name or rare-surname matching the co-author target − control is ≈ 0.'),
 ('前提：只用原 label package', 'Caveats: only the open answers (greedy) of the original label package; “not in the data” means not in the author lists of the 9,108-paper cohort, not that the person does not exist; not pre-registered, descriptive only.'),
 ('怎么算：分母 = mean_p', 'How computed: denominator = mean_p[T̄_p − F̄_p] (the denominator of recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p], false_0) · unwritten authors, Stage 11 sample + addendum 11 B completion (C 462; D 33 papers descriptive only) · team-cluster 95% CI · source: 391_groups/b2_cd/summary/cd_group_values.csv (b2_cd_report.md)'),
]
HOWR = [
 ('prior = m_delete', '<b>How computed: </b>prior = m_delete; topic = m_falsē − m_delete; spec = m_true − m_falsē; each as within-bin T − C · 9,108 papers; 4,621 / 2,220 papers, L63 · paper bootstrap · source: A_prior_decomposition.csv'),
 ('spec = true − mean(false_0..4) 的档内 target − control · 3,734 + 2,182 篇，名字位置', '<b>How computed: </b>within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, name positions · paper bootstrap · source: B_spec_target_vs_control_within_bin.csv'),
 ('spec = true − mean(false_0..4) 的档内 target − control · 3,734 + 2,182 篇，L40', '<b>How computed: </b>within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, L40–L62 (L41–L47, L49 filled by item 3-1, conclusion unchanged) · paper bootstrap · source: B_spec_target_vs_control_within_bin.csv'),
 ('recovery(l) = mean_p[ P̄_p(l) − F̄_p ] / mean_p[ T̄_p − F̄_p ]；loss', '<b>How computed: </b>recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p]; loss(l) = mean_p[K̄_p(64) − K̄_p(l)] / mean_p[T̄_p − F̄_p] · 593 + 593 papers, false_0 · paper bootstrap · source: E1_recovery.csv, E2_knockout.csv'),
 ('spec = true − mean(false_0..4)；recovery', '<b>How computed: </b>spec = true − mean(false_0..4); recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p]; T − C pooled within bin · 9,108 papers (lens) / 1,186 papers (E1, P1, P2; P1/P2 averaged over 5 false titles) · source: X3_means.csv, E1_recovery.csv, p12f_mean5.csv'),
 ('H3 名字位置 probe', '<b>How computed: </b>H3 name-position probe spec = probe(true) − probe(false) (Vpd, 4,654 papers, team cluster); H1 question share · source: b2_np_report_v2.md, x1_similarity.md'),
 ('未写出作者的 spec', '<b>How computed: </b>plain means of the spec of unwritten authors (L63, true − mean of 5 false titles) by recognition level · R0 927–4,105 / R1 15–462 papers · team cluster · source: stage10_curves.csv, rerun_report.md'),
]
USED = set()


def tr_lookup(plain):
    for i, (k, v) in enumerate(TR):
        if plain.startswith(k):
            USED.add(i); return v
    raise KeyError(plain[:60])


def retext(m):
    full = m.group(0)
    open_tag = re.match(r'<text\b[^>]*>', full).group(0)
    spans = re.findall(r'<tspan x="([\d.]+)" dy="([\d.]+)">(.*?)</tspan>', full)
    plain_lines = [html.unescape(re.sub(r'<[^>]+>', '', x[2])) for x in spans] if spans else [html.unescape(re.sub(r'<[^>]+>', '', full))]
    plain = ''.join(plain_lines)
    if not CJK.search(plain): return full
    if plain.startswith('CIs: Stage 10–12'):
        return full.replace('团队级补算后结论不变', 'same conclusions at team level')
    en = tr_lookup(plain)
    fs = float(re.search(r'font-size="([\d.]+)"', open_tag).group(1))
    x = float(re.search(r' x="([\d.]+)"', open_tag).group(1))
    maxw = max(L.width(l, fs) for l in plain_lines)
    maxw = max(maxw, min(1140, 1210 - x)) if x < 200 else max(maxw, 300)
    lh0 = float(spans[1][1]) if len(spans) > 1 else fs * 1.28
    n0 = max(len(spans), 1)
    f2 = fs
    # English is longer than the Chinese it replaces: shrink the font until it fits in the original number of lines
    # (the next element sits at a fixed y), down to 70% of the original size
    while len(L.wrap(en, f2, maxw * 1.04)) > n0 and f2 > max(fs * 0.7, 8.0):
        f2 = round(f2 - 0.25, 2)
    lines = L.wrap(en, f2, maxw * 1.04); lh = lh0 * f2 / fs
    if f2 != fs: open_tag = re.sub(r'font-size="[\d.]+"', f'font-size="{f2}"', open_tag, 1)
    if len(lines) == 1 and not spans:
        return open_tag + esc(en) + '</text>'
    t = ''.join(f'<tspan x="{x:.1f}" dy="{0 if i == 0 else lh:.1f}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    return open_tag + t + '</text>'


def rebadge(m):
    g = m.group(0)
    txt = html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<text\b.*?</text>', g, re.S).group(0)))
    if not CJK.search(txt): return g
    x = float(re.search(r'<rect x="([\d.]+)"', g).group(1)); y = float(re.search(r'<rect x="[\d.]+" y="([\d.]+)"', g).group(1))
    col = re.search(r'stroke="(#[0-9A-Fa-f]{6})"', g).group(1)
    b, _ = L.badge(x, y, tr_lookup(txt), col, 16)
    return b


def translate(k):
    t = S[k]; t0 = t
    t = re.sub(r'<g data-name="badge">.*?</g>', rebadge, t, flags=re.S)
    t = re.sub(r'<text\b[^>]*>.*?</text>', retext, t, flags=re.S)

    def rehowr(m):
        inner = html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
        if not CJK.search(inner): return m.group(0)
        for k2, v in HOWR:
            if inner.replace('怎么算：', '').startswith(k2): return m.group(1) + v + '</div>'
        raise KeyError(inner[:60])
    t = re.sub(r'(<div class="howr"[^>]*>)(.*?)</div>', rehowr, t, flags=re.S)
    t = t.replace('(C24 使用模型自生成文本，非 teacher forcing)', '(C24 uses text the model generated itself, not teacher forcing)')
    if t != t0: S[k] = t; note(k, 'Chinese translated to English')


# ======================================================================= 2a. rebuilt slide 29: exposure threshold
def slide_exposure():
    pid = 'x19b'
    TH = {r['quantity']: r for r in rows(G / 'summary_exposure_prereg19/thresholds_ratio.csv')}
    TB = rows(G / 'summary_exposure_prereg19/trend_by_bin.csv')
    EB = {r['citation_bin']: r for r in rows(G / 'summary_exposure_20261114/exposure_by_bin.csv')}
    rc, rl, rho = TH['c50_recognition'], TH['c50_recall'], TH['rho_recall_over_recognition']
    assert round(float(rho['est'])) == 276 and round(float(rc['est'])) == 40 and round(float(rl['est'])) == 11038
    b = L.frame(pid, 'Exposure: writing needs far more citations than recognising',
                'Addendum 19 (rule locked after the data were seen) · 9,108 papers, 7,247 teams, 2,000 team draws', 'Line A · addendum 19')
    bd, bw = L.badge(70, 124, 'Confirmed (rule locked after the data were seen): every ρ CI > 1', '#B54708', 16); b += bd
    fm, fw = L.formula(1210 - 520, 120, 'ρ = c50(recall) / c50(recognition)', 'p(c) = 1 / (1 + exp(−β1 [log10(1 + c) − log10(1 + c50)])), at the mean year', fs=18, w=520); b += fm
    ax = Ax(120, 214, 470, 250, 0, 4.9, 0, 1)
    b += ax.frame([0, 1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], xlab=lambda v: ['0', '10', '100', '1k', '10k'][int(v)], ylab=lambda v: f'{v:g}',
                  title='Recognition and writing rate by citations', ytitle='share of papers')
    xs = [i / 20 for i in range(0, 99)]
    for q, col in ((rc, BL), (rl, OR)):
        x50, b1 = float(q['log10_1p_est']), float(q['slope_log10cit'])
        b += ax.line(xs, [1 / (1 + math.exp(-b1 * (x - x50))) for x in xs], col, 2.6, pts=False)
    pts_r, pts_w = [], []
    for r in TB:
        e = EB.get(r['citation_bin'])
        if not e: continue
        x = math.log10(1 + float(r['median_citations']))
        for key, col, store in (('recognition_rate', BL, pts_r), ('recall_rate', OR, pts_w)):
            v, lo, hi = float(e[key]), float(e[key + '_lo']), float(e[key + '_hi'])
            b += ax.whisk(x, lo, hi, col, 1.4, 3) + f'<circle cx="{ax.X(x):.1f}" cy="{ax.Y(v):.1f}" r="4" fill="#FFFFFF" stroke="{col}" stroke-width="2"/>'
            store.append((r['citation_bin'], v))
    for q, col, lab, ly in ((rc, BL, 'recognition c50 = 40 [36, 44]', 0.93), (rl, OR, 'writing c50 = 11,038 [8,172, 15,607]', 0.85)):
        x50 = float(q['log10_1p_est']); X = ax.X(x50)
        b += f'<line x1="{X:.1f}" y1="{ax.Y(0):.1f}" x2="{X:.1f}" y2="{ax.Y(0.5):.1f}" stroke="{col}" stroke-width="1.6" stroke-dasharray="5 4"/>'
        b += f'<line x1="{ax.X(float(q["log10_1p_lo"])):.1f}" y1="{ax.Y(0.5):.1f}" x2="{ax.X(float(q["log10_1p_hi"])):.1f}" y2="{ax.Y(0.5):.1f}" stroke="{col}" stroke-width="5" stroke-opacity="0.5"/>'
        b += T(ax.X(0.95), ax.Y(ly), lab, 15, col, 'start', weight=700)
    x1, x2 = ax.X(float(rc['log10_1p_est'])), ax.X(float(rl['log10_1p_est']))
    b += f'<line x1="{x1 + 4:.1f}" y1="{ax.Y(0.62):.1f}" x2="{x2 - 6:.1f}" y2="{ax.Y(0.62):.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#{pid}a)"/>'
    b += T((x1 + x2) / 2 + 20, ax.Y(0.62) + 20, 'ρ = 276 [203, 390]', 17, INK, 'middle', weight=700)
    b += L.legend(130, 500, [('recognised (multiple choice, strong)', BL, 'line'), ('wrote ≥ 1 true author (R1 or R2)', OR, 'line')], fs=13)
    b += ntext(120, 520, 'dots = share per bin (95% CI); lines = logistic fit · n = 9,108 papers')
    # right panel: within-bin T - C by bin
    ax2 = Ax(720, 214, 470, 250, 0, 4.9, 0, 0.5)
    b += ax2.frame([0, 1, 2, 3, 4], [0, 0.1, 0.2, 0.3, 0.4, 0.5], xlab=lambda v: ['0', '10', '100', '1k', '10k'][int(v)], ylab=lambda v: f'{v:g}',
                   title='Within-bin target − control (spec, L63)', ytitle='T − C')
    xs2, ys2 = [], []
    for r in TB:
        if not r['diff']: continue
        x = float(r['x']); v, lo, hi = float(r['diff']), float(r['lo']), float(r['hi'])
        col = OR if r['used_in_slope'] == 'True' else GREY
        b += ax2.whisk(x, lo, hi, col, 1.4, 3) + f'<circle cx="{ax2.X(x):.1f}" cy="{ax2.Y(v):.1f}" r="4" fill="{col}"/>'
        if r['used_in_slope'] == 'True': xs2.append(x); ys2.append(v)
    # WLS line as reported (slope +0.0297 per log10); intercept by weighted mean through the used bins' centroid (display only)
    w = [1 / float(r['var_boot']) for r in TB if r['used_in_slope'] == 'True']
    xb = sum(a * c for a, c in zip(xs2, w)) / sum(w); yb = sum(a * c for a, c in zip(ys2, w)) / sum(w)
    sl = 0.0297
    b += f'<line x1="{ax2.X(0):.1f}" y1="{ax2.Y(yb - sl * xb):.1f}" x2="{ax2.X(3.1):.1f}" y2="{ax2.Y(yb + sl * (3.1 - xb)):.1f}" stroke="{RD}" stroke-width="2" stroke-dasharray="6 4"/>'
    b += T(ax2.X(0.6), ax2.Y(0.47), 'WLS slope +0.030 [+0.014, +0.044] per 10× citations', 14, RD)
    b += ntext(720, 520, 'n = 7,995 papers in the 10 bins used (orange) · grey = < 30 control, not used')
    y = 548
    for kind, txt in (('how', 'How computed: recognised = multiple-choice team result “strong” (uncertain counts as not recognised); written = R1 or R2 (≥ 1 true author written); separate logistic fits y ~ log10(1 + citations) + (year − mean year); c50 = citations at probability 0.5 at the mean year; ρ = c50(written) / c50(recognised), rule: whole CI > 1; secondary: within-bin target − control (spec, L63) regressed on log10(1 + bin median citations) by WLS (weights 1 / bootstrap variance, the 10 bins with ≥ 30 papers per group), rule: slope CI > 0 · 9,108 papers, 7,247 teams · team cluster, 2,000 draws · 391_groups/summary_exposure_prereg19/thresholds_ratio.csv, trend_by_bin.csv; bin shares: summary_exposure_20261114/exposure_by_bin.csv'),
                      ('bold', 'Confirmed under the locked rule (locked after the data were seen): ρ = 276 [203, 390], whole CI > 1 → writing needs far more exposure than recognising; within-bin target − control grows with exposure, WLS slope +0.030 [+0.014, +0.044] per 10× citations (10 bins, +0.175 to +0.298 per bin).'),
                      ('txt', 'Caveats: one model; citations are only a proxy for training exposure; bins are a stratified sample, not population shares; recognition in low bins includes a ~25% guessing floor; the writing threshold is near the top of the observed range (only 16 of 9,108 papers have > 11,038 citations), so it leans on extrapolation; 276× is an estimate; sensitivity (uncertain excluded) ρ 1,184 [851, 1,712].')):
        fs = 10.5 if kind == 'how' else 13
        t, h = para(70, y, txt, fs, 1140, '#4B5363' if kind == 'how' else INK, lh=fs * 1.28)
        if kind == 'bold': t = t.replace('<text ', '<text font-weight="700" ', 1)
        b += t; y += h + 5
    b += L.footer('391_groups/summary_exposure_prereg19/report.md · thresholds_ratio.csv · trend_by_bin.csv · summary_exposure_20261114/exposure_by_bin.csv · config/prereg_addendum19.md (sha256 f6b65072…)')
    return L.section('Exposure threshold (addendum 19)', pid, b)


# ======================================================================= 2b. slide 59 split: answer format (B) and name chain (D)
def slide_format():
    pid = 'a16f'
    R = {(r['group'], r['fa_type'], r['cond'], r['outcome']): r for r in rows(G / 'summary_a16_20261115/b_rates.csv')}
    H = {(r['test'], r['quantity']): r for r in rows(G / 'summary_a16_20261115/holm.csv')}
    b = L.frame(pid, 'Answer format (B): only a given first initial helps',
                'Addendum 16 (pre-registered, Holm over 5 tests) · greedy generation · 600 A + 600 B papers (+ 300 C, descriptive) · team-cluster 95% CI', 'Line D · addendum 16')
    bd, bw = L.badge(70, 124, 'B: supported, through F4 only', '#B54708', 16); b += bd
    fm, fw = L.formula(1210 - 560, 120, 'Δ_g(c) = corr_g(c) − corr_g(F0),   DiD = Δ_A − Δ_B',
                       'corr = rate(true author written) − rate(chance: author of a fixed same-field control paper)', fs=18, w=560); b += fm
    PAN = [('F1', 'any_full', 'F1 “surname, given”', 'any author, full name'), ('F2', 'any_sur', 'F2 surnames only', 'any author, surname'),
           ('F3', 'first_sur', 'F3 first-author surname', 'first author, surname'), ('F4', 'first_sur', 'F4 first initial given', 'first author, surname')]
    for i, (c, out, lab, olab) in enumerate(PAN):
        x0 = 110 + i * 285
        ax = Ax(x0, 226, 230, 210, 0, 4, 0, 0.16)
        b += ax.frame([], [0, 0.04, 0.08, 0.12, 0.16] if i == 0 else [], ylab=lambda v: f'{v:.2f}', grid=True)
        b += T(x0 + 115, 210, lab, 16, INK, 'middle', weight=700)
        for gi, (g, col) in enumerate((('A', OR), ('B', BL))):
            for ci_, cond in enumerate(('F0', c)):
                r = R[(g, 'all', cond, out)]; xc = 0.65 + gi * 2 + ci_ * 0.75
                v, lo, hi = float(r['corrected']), float(r['corr_lo']), float(r['corr_hi'])
                b += vbar(ax, xc, v, 30, col, 0.35 if cond == 'F0' else 0.9) + ax.whisk(xc, lo, hi, INK, 1.2, 3)
                b += T(ax.X(xc), ax.Y(hi) - 4, f'{v:.3f}', 11.5, INK, 'middle')
                b += T(ax.X(xc), ax.Y(0) + 15, cond, 12.5, PEN, 'middle')
            b += T(ax.X(1.02 + gi * 2), ax.Y(0) + 31, f'group {g}', 13.5, col, 'middle', weight=700)
        h = H[(f'B_{c}', 'DiD_A-B')]
        rej = h['rejected_holm'] == 'True'
        b += T(x0 + 115, 488, f'DiD {fmt(float(h["est"]))}', 15, OR if rej else PEN, 'middle', weight=700)
        b += T(x0 + 115, 505, f'Holm CI {cif(float(h["holm_ci_lo"]), float(h["holm_ci_hi"]))}, p {float(h["p_holm"]):.4f}', 12.5, OR if rej else PEN, 'middle')
        b += ntext(x0 + 115, 521, f'outcome: {olab}', 11, 'middle')
    b += T(40, 330, 'corrected rate', 13, PEN, extra=' transform="rotate(-90 40 330)"')
    b += ntext(110, 540, 'n = 600 A + 600 B papers per format (the same papers in F0 and F1–F4) · faded bar = F0 baseline, solid = the format · whisker = 95% CI')
    y = 562
    for kind, txt in (('how', 'How computed: for each format c, corr = rate of writing a true author − chance rate (chance = authors of a same-field control paper fixed in advance; F4 uses a control with the same first initial); Δ_A(c) = group A in c minus the same quantity in F0; DiD = Δ_A − Δ_B · 600 + 600 papers · team cluster, 2,000 draws, Holm over 5 tests · 391_groups/summary_a16_20261115/b_rates.csv, b_main.csv, holm.csv'),
                      ('bold', 'B supported, but only through F4 (the true first author’s initial is given): DiD A − B +0.085 [Holm 0.047, 0.124], p_Holm 0.0025; F4 alone Δ_A +0.103 [Holm 0.072, 0.133]. F1–F3 DiDs are not significant.'),
                      ('txt', 'Caveats: behaviour labels come from another generation run (label package), F0 is the baseline for this prompt; the B stop / truncation rule was changed after shard 0 (deviation D16-4, recorded); greedy decoding only; C has 300 papers and is descriptive.')):
        fs = 10.5 if kind == 'how' else 13
        t, h_ = para(70, y, txt, fs, 1140, '#4B5363' if kind == 'how' else INK, lh=fs * 1.28)
        if kind == 'bold': t = t.replace('<text ', '<text font-weight="700" ', 1)
        b += t; y += h_ + 5
    b += L.footer('391_groups/summary_a16_20261115/report.md · b_rates.csv (corrected = true − chance) · b_main.csv · holm.csv · config/prereg_addendum16.md, prereg_addendum16_deviations.md')
    return L.section('Answer format (B), addendum 16', pid, b)


def slide_chain():
    pid = 'a16d'
    DG = {(r['group'], r['measure'], r['cond']): r for r in rows(G / 'summary_a16_20261115/d_gen.csv')}
    DC = {(r['group'], r['fa_type'], r['version'], r['score']): r for r in rows(G / 'summary_a16_20261115/d_contrasts.csv') if r['contrast'] == 'G1'}
    b = L.frame(pid, 'Name chain (D): a true co-author helps, but not this paper',
                'Addendum 16 (pre-registered) · prefix of one author after “Authors:” · 1,428 papers (A 600, B 600, C 227–228) · team-cluster 95% CI', 'Line D · addendum 16')
    bd, bw = L.badge(70, 124, 'D: the effect exists, but it is not paper-specific', '#B54708', 16); b += bd
    fm, fw = L.formula(1210 - 540, 120, 'G(1) = S(P_true(1)) − S(P_other(1))', 'prefix = the true first author vs the first author of another same-field paper', fs=18, w=540); b += fm
    # left: generation, any further true author (full name)
    ax = Ax(120, 226, 440, 220, 0, 6, 0, 0.6)
    b += ax.frame([], [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], ylab=lambda v: f'{v:.0%}', title='Greedy generation: writes ≥ 1 more true author', ytitle='share of papers')
    for gi, g in enumerate(('A', 'B', 'C')):
        for ci_, (cond, col, lab) in enumerate((('G_true1', OR, 'true'), ('G_other1', LIGHT, 'other'))):
            r = DG[(g, 'any_rest_full', cond)]; xc = 1 + gi * 2 + ci_ * 0.8 - 0.4
            v, lo, hi = float(r['est']), float(r['lo']), float(r['hi'])
            b += vbar(ax, xc, v, 34, col, 0.9) + ax.whisk(xc, lo, hi, INK, 1.2, 3) + T(ax.X(xc), ax.Y(hi) - 5, f'{v:.1%}', 12.5, INK, 'middle')
            b += T(ax.X(xc), ax.Y(0) + 15, lab, 12, PEN, 'middle')
        b += T(ax.X(1 + gi * 2), ax.Y(0) + 32, f'group {g}' + (' (228)' if g == 'C' else ''), 14, INK, 'middle', weight=700)
    b += ntext(120, 520, 'n = 600 A / 600 B / 228 C papers · orange = true first author, grey = another paper’s')
    # right: teacher-forced G(1) (all tokens)
    items = [('A, true title', DC[('A', 'all', 'true', 'all_tokens')], OR), ('A, title-specific', DC[('A', 'all', 'spec', 'all_tokens')], OR),
             ('A, title deleted', DC[('A', 'all', 'delete', 'all_tokens')], OR), ('A − B, true title', DC[('A-B', 'all', 'true', 'all_tokens')], PEN),
             ('B, true title', DC[('B', 'all', 'true', 'all_tokens')], BL), ('C, true title', DC[('C', 'all', 'true', 'all_tokens')], '#E9B27A')]
    x0, y0, rowh = 700, 236, 34
    axh = Ax(x0 + 150, y0, 250, rowh * len(items), -0.06, 0.28, 0, 1)
    b += T(x0 - 20, 212, 'Teacher forcing: G(1), later authors scored', 17, INK, weight=700)
    for v in (0, 0.1, 0.2):
        X = axh.X(v); st_ = 'stroke="#22304A" stroke-width="1.6"' if v == 0 else 'stroke="#E7DADA" stroke-width="1" stroke-dasharray="3 4"'
        b += f'<line x1="{X:.1f}" y1="{y0:.1f}" x2="{X:.1f}" y2="{y0 + axh.h:.1f}" {st_}/>' + T(X, y0 + axh.h + 16, '0' if v == 0 else f'{v:+.1f}', 13, PEN, 'middle')
    for i, (lab, r, col) in enumerate(items):
        yc = y0 + rowh * i + 6; v, lo, hi = float(r['est']), float(r['lo']), float(r['hi'])
        b += T(x0 + 142, yc + 15, lab, 14, INK, 'end') + hbar(axh.X(0), yc, axh.X(v) - axh.X(0), 20, col, 0.85)
        b += f'<line x1="{axh.X(lo):.1f}" y1="{yc + 10:.1f}" x2="{axh.X(hi):.1f}" y2="{yc + 10:.1f}" stroke="{INK}" stroke-width="1.4"/>'
        b += T(x0 + 410, yc + 15, f'{fmt(v)} {cif(lo, hi)}', 12.5, INK)
    b += ntext(700, 520, 'n = 600 A / 600 B / 227 C papers · A − B paired · title-specific = true − mean of 5 false')
    y = 528
    for kind, txt in (('how', 'How computed: generation: greedy answer after the one-author prefix, share of papers with ≥ 1 further true author written in full (d_gen.csv, any_rest_full); teacher forcing: one name given (k = 1), only the remaining authors scored, G(1) = S(true co-author given) − S(another same-field paper’s author given); title-specific = true title − mean of 5 false titles · 1,428 papers · team cluster, 2,000 draws, Holm over 5 tests (G_A(1): Holm CI [0.141, 0.189], p_Holm 0.0025) · 391_groups/summary_a16_20261115/d_gen.csv, d_contrasts.csv'),
                      ('bold', 'D: the effect exists (A writes another true author in 11.8% of papers after the true first author vs 1.5% after another paper’s author; G_A(1) +0.167), but its title-specific part is only +0.012 [−0.001, 0.025], it is larger with the title deleted (+0.223), and A ≈ B (−0.019 [−0.045, 0.007]) → a co-author network association, not memory of this paper.'),
                      ('txt', 'Caveats: teacher-forced scores are preferences, not generation; greedy decoding only; behaviour labels from another run; C (227–228 papers) has low power and is descriptive.')):
        fs = 10.5 if kind == 'how' else 13
        t, h_ = para(70, y, txt, fs, 1140, '#4B5363' if kind == 'how' else INK, lh=fs * 1.28)
        if kind == 'bold': t = t.replace('<text ', '<text font-weight="700" ', 1)
        b += t; y += h_ + 5
    b += L.footer('391_groups/summary_a16_20261115/report.md · d_gen.csv (any_rest_full, G_true1 / G_other1) · d_contrasts.csv (G1, all_tokens) · holm.csv · config/prereg_addendum16.md')
    return L.section('Name chain (D), addendum 16', pid, b)


# ======================================================================= 2c. charts added to existing slides
def fx_move(k, old_style, new_style):
    rep(k, old_style, new_style, 'formula/n line moved for the figure')


# --- split summaries: formula line first, then a card with an existing chart of the deck (dark half)
CROPS = {}


def summary_card(k, src_slide, box, left, top, width, caption, fx_top):
    img, size = card_img(deck_img(src_slide), tuple(int(v * 1.5) for v in box), width, caption)
    rep(k, '<div class="fxn d" style="left:70px;top:430px;width:540px">', f'<div class="fxn d" style="left:70px;top:{fx_top}px;width:540px">', 'formula/n line moved for the figure')
    ins(k, f'<div style="position:absolute;left:{left}px;top:{top}px;width:{width}px;z-index:2">{img}</div>', f'figure: chart of slide {src_slide} (crop)')


summary_card(43, 42, (55, 150, 915, 575), 80, 376, 250, 'Lens vs probe at the title (slide 42)', 314)
summary_card(51, 24, (60, 170, 820, 640), 80, 360, 236, 'Target pulls ahead after L48 (slide 24)', 302)
summary_card(60, 57, (45, 170, 725, 590), 80, 304, 236, 'Surnames carry most (slide 57)', 246)


# --- slide 62: small-sample traps as two mini charts
def ch62():
    o = ''
    ax = Ax(150, 22, 250, 62, 0, 0.008, 0, 2)
    o += T(20, 12, 'Single-paper leverage (Stage 4, L56 mean RR)', 14, INK, weight=700)
    for i, (lab, v, col) in enumerate((('all 20 papers', 0.0070, OR), ('without one paper', 0.0021, LIGHT))):
        y = 30 + i * 28; o += T(140, y + 14, lab, 13, INK, 'end') + hbar(150, y, ax.X(v) - 150, 18, col) + T(ax.X(v) + 6, y + 14, f'{v:.4f}', 13, INK)
    o += ftext(20, 108, 'share = x(1) / Σ x = 71%') + ntext(200, 108, 'n = 20 papers (audit_report.md)')
    ax2 = Ax(520, 24, 250, 66, 0, 10, -1, 6)
    o += T(470, 12, 'Tail-driven contrast (Stage 8D, A − B, L56)', 14, INK, weight=700)
    o += ax2.hline(0, PEN, '3 4', 1)
    o += ax2.line([0, 5, 10], [4.98, 1.9, -0.4], OR, 2.6)
    for x, v in ((0, 4.98), (5, 1.9), (10, -0.4)):
        o += T(ax2.X(x), ax2.Y(v) - 7, f'{v:+.1f} pp'.replace('-', '−'), 12.5, INK, 'middle') + T(ax2.X(x), ax2.Y(-1) + 14, f'top {x}' if x else 'all', 12, PEN, 'middle')
    o += ftext(470, 120, 'A − B after removing the top-k pairs') + ntext(470, 136, 'n = 100 A/B pairs (200 papers)')
    return ovl(70, 552, 840, 140, o, 'Two small-sample traps')


fx_move(62, '<div class="fxn" style="left:120px;top:600px;width:1000px">', '<div class="fxn" style="left:930px;top:590px;width:290px">')
ins(62, ch62(), 'figure: two mini charts (leverage, tail-driven)')


# --- slide 63: sample-size ladder
def ch63():
    o = ''
    lx = lambda n: 40 + (math.log10(n) - 1) / (math.log10(20000) - 1) * 640
    o += f'<line x1="{lx(10):.1f}" y1="44" x2="{lx(20000):.1f}" y2="44" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
    for n_ in (10, 100, 1000, 10000):
        o += f'<line x1="{lx(n_):.1f}" y1="44" x2="{lx(n_):.1f}" y2="50" stroke="{INK}" stroke-width="1.5"/>' + T(lx(n_), 64, f'{n_:,}', 12, PEN, 'middle')
    for n_, lab, col, up in ((20, 'Stage 4', '#1B2230', True), (50, 'Pilot50', '#1B2230', False), (200, 'Stage 8', '#1B2230', True),
                             (600, 'add. 18b', BL, False), (1186, 'Stage 11–12', BL, True), (9108, 'Stage 10', BL, True)):
        o += f'<circle cx="{lx(n_):.1f}" cy="44" r="6" fill="{col}"/>' + T(lx(n_), 30 if up else 82, f'{lab} · {n_:,}', 13, col, 'middle', weight=700)
    o += T(0, 12, 'Papers per analysis (log scale): small samples (dark) vs full cohort (blue)', 14, INK, weight=700)
    return ovl(70, 598, 700, 96, o, 'Sample size per stage')


fx_move(63, '<div class="fxn" style="left:70px;top:630px;width:1100px">', '<div class="fxn" style="left:800px;top:612px;width:420px">')
ins(63, ch63(), 'figure: sample-size ladder')


# --- slide 74: X1 replacement by layer
def ch74():
    o = T(0, 14, 'X1: share recovered by the swap', 15, INK, weight=700)
    ax = Ax(40, 34, 250, 150, 0, 3, 0, 1)
    o += ax.frame([], [0, 0.5, 1], ylab=lambda v: f'{v:g}')
    for i, (lay, v_all, v_old) in enumerate((('L24', 0.996, 0.99), ('L40', 0.933, 0.92), ('L48', 0.455, 0.42))):
        x = 0.5 + i
        o += vbar(ax, x - 0.15, v_all, 26, OR) + vbar(ax, x + 0.17, v_old, 22, BL, hollow=True)
        o += T(ax.X(x - 0.15), ax.Y(v_all) - 4, f'{v_all:.3f}', 11.5, INK, 'middle') + T(ax.X(x), ax.Y(0) + 15, lay, 13, PEN, 'middle')
    o += L.legend(40, 222, [('all authors', OR, 'box'), ('first author (old)', BL, 'box')], fs=12, gap=10)
    o += ftext(0, 244, 'R = (patched − false) / (true − false)') + ntext(0, 262, 'n = 582 test pairs (Stage 13 X1)')
    return ovl(905, 404, 310, 270, o, 'X1 replacement by layer')


fx_move(74, '<div class="fxn" style="left:70px;top:560px;width:1100px">', '<div class="fxn" style="left:70px;top:560px;width:800px">')
ins(74, ch74(), 'figure: X1 bar chart')


# --- slide 75: X4 decodability and X3 behaviour
def ch75():
    o = T(0, 14, 'X4: decodable from the own title state', 15, INK, weight=700)
    ax = Ax(40, 32, 250, 120, 0, 3, 0, 0.06)
    o += ax.frame([], [0, 0.02, 0.04, 0.06], ylab=lambda v: f'{v:.2f}')
    for i, (lab, v, lo, hi, col) in enumerate((('1st author L8', 0.046, 0.035, 0.059, OR), ('all authors L8', 0.048, 0.039, 0.058, OR), ('year L40', 0.013, 0.008, 0.018, BL))):
        x = 0.5 + i; o += vbar(ax, x, v, 34, col) + ax.whisk(x, lo, hi, INK, 1.2, 3) + T(ax.X(x), ax.Y(hi) - 4, f'{v:+.3f}', 11.5, INK, 'middle') + T(ax.X(x), ax.Y(0) + 15, lab, 11.5, PEN, 'middle')
    o += T(0, 196, 'X3: behaviour kept under a paraphrase', 14, INK, weight=700)
    o += f'<rect x="40" y="204" width="250" height="14" fill="#EEF1F5" stroke="{INK}" stroke-width="1"/>' + hbar(40, 204, 250 * 0.897, 14, GR) + T(40 + 250 * 0.897, 232, '0.897 [0.868, 0.926]', 12, INK, 'middle')
    o += ftext(0, 252, 'D = decode(own) − decode(partner)') + ntext(0, 270, 'n = test split, team CI (X4); all tokens (X3)')
    return ovl(905, 430, 310, 278, o, 'X4 and X3')


fx_move(75, '<div class="fxn" style="left:70px;top:560px;width:1100px">', '<div class="fxn" style="left:70px;top:560px;width:800px">')
ins(75, ch75(), 'figure: X4 / X3 bars')


# --- slide 77: X2 moved share
def ch77():
    o = T(0, 14, 'X2: share of the gap moved', 15, INK, weight=700)
    ax = Ax(40, 32, 250, 150, 0, 2, 0, 1)
    o += ax.frame([], [0, 0.5, 1], ylab=lambda v: f'{v:g}')
    for gi, (lab, vals) in enumerate((('S_id at L40', (0.005, 0.003, 0.920)), ('S_auth at L48', (0.018, 0.003, 0.428)))):
        for j, (v, col) in enumerate(zip(vals, (OR, LIGHT, BL))):
            x = 0.25 + gi + j * 0.25; o += vbar(ax, x, v, 18, col) + T(ax.X(x), ax.Y(v) - 4, f'{v:.3f}', 10.5, INK, 'middle')
        o += T(ax.X(0.5 + gi), ax.Y(0) + 15, lab, 12, PEN, 'middle')
    o += L.legend(40, 222, [('subspace', OR, 'box'), ('random', LIGHT, 'box'), ('full', BL, 'box')], fs=12, gap=8)
    o += ftext(0, 244, 'moved = (patched − false) / (true − false)') + ntext(0, 262, 'n = 582 test pairs · fit on 5,041 papers')
    return ovl(905, 436, 310, 268, o, 'X2 moved share')


fx_move(77, '<div class="fxn" style="left:70px;top:520px;width:1100px">', '<div class="fxn" style="left:70px;top:520px;width:800px">')
ins(77, ch77(), 'figure: X2 bars')


# --- slide 83 (what we learned, continued): route schematic
def ch83():
    o = T(0, 14, 'The route through the layers', 16, INK, weight=700)
    Y = lambda l: 470 - l * 6.9
    o += f'<rect x="24" y="{Y(63):.1f}" width="26" height="{Y(0) - Y(63):.1f}" rx="8" fill="#EEF1F5" stroke="{INK}" stroke-width="1.6"/>'
    segs = [(0, 16, GR, '≤ L16: title facts readable at the title (M2)'), (24, 50, BL, 'L24–L50: the title is read (patching R ≥ 0.5 at L48)'),
            (48, 49, BL, 'L48: attention brings the title in (P2 0.237)'), (52, 56, OR, 'L52–L56: MLPs carry paper information (R 0.158–0.275; name directions 0.022–0.042)'),
            (57, 61, OR, 'L57–L61: MLPs write it (MLP − attention loss +0.040)'), (63, 63.6, INK, 'L63: the author is said')]
    ynext = 40
    for a, z, col, lab in sorted(segs, key=lambda q: -q[1]):
        o += f'<rect x="24" y="{Y(z):.1f}" width="26" height="{max(Y(a) - Y(z), 3):.1f}" fill="{col}" fill-opacity="0.8"/>'
        lines = L.wrap(lab, 12.5, 230); ym = (Y(a) + Y(z)) / 2
        yy = max(ym + 4 - (len(lines) - 1) * 7, ynext)
        o += f'<path d="M52 {ym:.1f} L58 {ym:.1f} L64 {yy - 4:.1f}" fill="none" stroke="{col}" stroke-width="1.5"/>'
        for i, l in enumerate(lines): o += T(68, yy + i * 14, l, 12.5, INK)
        ynext = yy + len(lines) * 14 + 8
    for l in (0, 16, 32, 48, 63): o += T(18, Y(l) + 4, f'L{l}', 11, PEN, 'end')
    o += ftext(0, 500, 'loss(c) = S(none) − S(c)') + ntext(0, 518, 'n = 600 (add. 18b) · 1,186 (Stage 11–12)')
    return ovl(930, 110, 300, 530, o, 'Route through the layers')


rep(83, '<div class="wl">', '<div class="wl" style="max-width:820px;grid-template-columns:200px 1fr;row-gap:9px">', 'rows narrowed for the figure')
S[83] = S[83].replace('<div class="v">', '<div class="v" style="font-size:16px">').replace('<div class="k ', '<div style="font-size:28px" class="k ')
ins(83, ch83(), 'figure: route schematic')


# --- slide 86: group comparisons as bars (replaces the fig3 picture)
def ch86():
    rowsx = [('P1 recognition: A − B', 0.200, 0.188, 0.213, BL), ('  + confounders (paper)', 0.173, 0.161, 0.186, LIGHT), ('  author level + position', 0.151, 0.139, 0.163, LIGHT),
             ('P3 per order right', 0.059, 0.056, 0.063, BL), ('  + confounders', 0.046, 0.042, 0.049, LIGHT),
             ('P2 partial recall: C − A, co-authors', 0.061, 0.034, 0.090, BL), ('P2 first author: C − A', 0.031, -0.006, 0.069, LIGHT)]
    o = T(0, 14, 'Group contrasts (output, L63)', 16, INK, weight=700)
    x0, w = 175, 140; X = lambda v: x0 + (v + 0.02) / 0.25 * w
    for v in (0, 0.1, 0.2):
        o += f'<line x1="{X(v):.1f}" y1="26" x2="{X(v):.1f}" y2="{26 + 30 * len(rowsx):.1f}" stroke="{INK if v == 0 else "#E7DADA"}" stroke-width="{1.6 if v == 0 else 1}"/>' + T(X(v), 42 + 30 * len(rowsx), f'{v:g}', 12, PEN, 'middle')
    for i, (lab, v, lo, hi, col) in enumerate(rowsx):
        y = 30 + i * 30
        o += T(x0 - 6, y + 14, lab.strip(), 11.5, INK if col == BL else PEN, 'end') + hbar(X(0), y, X(v) - X(0), 18, col, 0.9)
        o += f'<line x1="{X(lo):.1f}" y1="{y + 9:.1f}" x2="{X(hi):.1f}" y2="{y + 9:.1f}" stroke="{INK}" stroke-width="1.3"/>' + T(X(max(hi, v)) + 4, y + 14, f'{v:+.3f}', 11.5, INK)
    yb = 30 + 30 * len(rowsx) + 26
    o += ftext(0, yb + 4, 'Δ = Σ_b w_b (spec_A,b − spec_B,b)') + ntext(0, yb + 22, 'n = 3,417 / 2,148 (P1) · 8,288 (P3)') + ntext(0, yb + 38, '390 / 2,826 (P2 other) · 292 / 3,199 (P2 first)')
    return f'<div style="width:400px;flex:none">' + ovl(0, 0, 400, yb + 46, o, 'Group contrasts').replace('position:absolute;left:0px;top:0px;', 'position:relative;') + '</div>'


m86 = re.search(r'<div style="width:400px;flex:none"><figure class="card">.*?</figure></div>', S[86], re.S)
assert m86
S[86] = S[86][:m86.start()] + ch86() + S[86][m86.end():]; note(86, 'figure: fig3 picture replaced by a bar chart of the same contrasts')


# --- slide 87: denominators and R(L48) by group
def ch87():
    G_ = [('A', 0.407, 0.386, 0.430, 0.811, 0.790, 0.832, OR), ('B', 0.214, 0.196, 0.234, 0.869, 0.835, 0.906, BL), ('U0', 0.293, 0.271, 0.316, 0.844, 0.814, 0.877, PEN),
          ('C', 0.559, 0.529, 0.590, 0.731, 0.705, 0.757, '#E9B27A'), ('R2', 0.845, 0.798, 0.897, 0.670, 0.630, 0.707, LIGHT)]
    o = ''
    for p, (title, idx, ymax, yt) in enumerate((('Denominator: true − false', 1, 1.0, [0, 0.5, 1]), ('E1 recovery R(L48)', 4, 1.0, [0, 0.5, 1]))):
        ax = Ax(40 + p * 420, 26, 340, 110, 0, 5, 0, ymax)
        o += ax.frame([], yt, ylab=lambda v: f'{v:g}') + T(ax.x0, 14, title, 14, INK, weight=700)
        for i, g in enumerate(G_):
            v, lo, hi = g[idx], g[idx + 1], g[idx + 2]; x = 0.5 + i
            o += vbar(ax, x, v, 34, g[7]) + ax.whisk(x, lo, hi, INK, 1.2, 3) + T(ax.X(x), ax.Y(hi) - 4, f'{v:.3f}', 11, INK, 'middle') + T(ax.X(x), ax.Y(0) + 14, g[0], 12, PEN, 'middle')
    o += ftext(40, 172, 'R = mean(patched − false) / mean(true − false)') + ntext(400, 172, 'n = A 557 · B 586 · U0 599 · C 462 · R2 200 papers')
    return ovl(70, 500, 860, 182, o, 'Denominator and recovery by group')


fx_move(87, '<div class="fxn" style="left:70px;top:560px;width:1100px">', '<div class="fxn" style="left:950px;top:520px;width:270px">')
ins(87, ch87(), 'figure: bar charts')


# --- slide 89: P1 / P2 numerator and ratio B - A
def ch89():
    R_ = [('P1 names L48', -0.105, -0.123, -0.087, 0.052, 0.011, 0.098), ('P1 names L56', -0.183, -0.209, -0.157, -0.050, -0.087, -0.012),
          ('P2 attention L48', -0.029, -0.038, -0.021, 0.057, 0.030, 0.086), ('P2 MLP L56', -0.041, -0.053, -0.029, 0.008, -0.030, 0.044),
          ("P1 ':' L48", -0.000, -0.007, 0.005, 0.050, 0.026, 0.071), ("P1 ':' L52", -0.013, -0.024, -0.002, 0.073, 0.038, 0.106)]
    o = ''
    for p, (title, off, lo_, hi_, col) in enumerate((('numerator B − A', 1, -0.22, 0.02, BL), ('ratio B − A', 4, -0.1, 0.12, OR))):
        x0 = 130 + p * 400; w = 230; X = lambda v: x0 + (v - lo_) / (hi_ - lo_) * w
        o += T(x0, 12, title, 14, INK, weight=700)
        o += f'<line x1="{X(0):.1f}" y1="20" x2="{X(0):.1f}" y2="{20 + 22 * len(R_):.1f}" stroke="{INK}" stroke-width="1.5"/>'
        for i, r in enumerate(R_):
            y = 22 + i * 22; v, lo, hi = r[off], r[off + 1], r[off + 2]
            if p == 0: o += T(x0 - 8, y + 12, r[0], 12, INK, 'end')
            o += f'<line x1="{X(lo):.1f}" y1="{y + 8:.1f}" x2="{X(hi):.1f}" y2="{y + 8:.1f}" stroke="{col}" stroke-width="2.4"/><rect x="{X(v) - 4:.1f}" y="{y + 4:.1f}" width="8" height="8" fill="{col}" stroke="{INK}" stroke-width="1"/>'
            o += T(x0 + w + 8, y + 12, f'{v:+.3f}'.replace('-', '−'), 11.5, INK)
    o += ftext(0, 168, 'ratio = mean(patched − false) / mean(true − false)') + ntext(330, 168, 'n = A 557 / B 586 papers · paired team bootstrap 95% CI')
    return ovl(70, 520, 860, 176, o, 'P1 / P2 numerator and ratio')


fx_move(89, '<div class="fxn" style="left:70px;top:540px;width:1100px">', '<div class="fxn" style="left:950px;top:530px;width:270px">')
ins(89, ch89(), 'figure: forest charts')


# --- slide 90: M5 AUROC and N2 by readout
def ch90():
    o = ''
    ax = Ax(40, 26, 330, 110, 0, 4, 0.4, 1.0)
    o += ax.frame([], [0.5, 0.75, 1.0], ylab=lambda v: f'{v:g}') + T(40, 14, 'M5: true vs false title, AUROC', 14, INK, weight=700)
    for i, (lab, v, col) in enumerate((('logit L24', 0.516, LIGHT), ('logit L62', 0.899, BL), ('output', 0.919, OR), ('probe / colon', 0.51, LIGHT))):
        x = 0.5 + i; y0, y1 = ax.Y(0.4), ax.Y(v)
        o += f'<rect x="{ax.X(x) - 17:.1f}" y="{y1:.1f}" width="34" height="{y0 - y1:.1f}" fill="{col}" fill-opacity="0.85" stroke="{INK}" stroke-width="1"/>'
        o += T(ax.X(x), y1 - 4, '0.50–0.52' if lab.startswith('probe') else f'{v:.3f}', 11, INK, 'middle') + T(ax.X(x), ax.Y(0.4) + 14, lab, 11.5, PEN, 'middle')
    o += ax.hline(0.5, PEN, '3 4', 1)
    ax2 = Ax(470, 26, 330, 110, 0, 3, -0.15, 0.06)
    o += ax2.frame([], [-0.15, -0.1, -0.05, 0, 0.05], ylab=lambda v: f'{v:+.2f}'.replace('+0.00', '0')) + T(470, 14, 'N2: name prior, target − control', 14, INK, weight=700)
    for i, (lab, v, col) in enumerate((('output', 0.047, OR), ('logit L62', 0.039, BL), ('J-lens L48', -0.133, LIGHT))):
        x = 0.5 + i; o += vbar(ax2, x, v, 40, col) + T(ax2.X(x) + (0 if v > 0 else 38), ax2.Y(v) - 4 if v > 0 else ax2.Y(v / 2) + 4, f'{v:+.3f}'.replace('-', '−'), 11, INK, 'middle') + T(ax2.X(x), ax2.Y(-0.15) + 14, lab, 11.5, PEN, 'middle')
    o += ftext(40, 170, 'AUROC = P(score_true > score_false)') + ntext(330, 170, 'n = 9,108 papers × 5 false titles (M5) · 4,621 / 2,220 (N2)')
    return ovl(70, 520, 860, 178, o, 'M5 and N2')


fx_move(90, '<div class="fxn" style="left:70px;top:500px;width:1100px">', '<div class="fxn" style="left:950px;top:530px;width:270px">')
ins(90, ch90(), 'figure: bar charts')


# --- slide 91: replications as a flow (text smaller)
def ch91():
    boxes = [('Done first', 'X7 (5 false titles) · all-token probe (add. 9) · C-1 to C-5', GR),
             ('Batch 1 (add. 10)', 'X1–X4 all authors · E4b per donor · P1 / P2 five titles → conclusions unchanged', GR),
             ('Batch 2 (add. 11, 12)', 'C / D completion · 2-11 → 2-11b (C24) · name-position probe · Patchscope · 2-1 gate', BL),
             ('Batch 3 (add. 14)', '3-1, 3-2 done · 3-3 stopped (D14-1) · 3-4 / 3-5 not run', OR)]
    o, x = '', 0
    for i, (h, t_, col) in enumerate(boxes):
        o += f'<rect x="{x}" y="6" width="250" height="92" rx="12" fill="#FFFFFF" stroke="{col}" stroke-width="2.2"/>' + T(x + 12, 28, h, 15, col, weight=700)
        for j, l in enumerate(L.wrap(t_, 12.5, 228)): o += T(x + 12, 48 + j * 15, l, 12.5, INK)
        if i < 3: o += f'<line x1="{x + 252}" y1="52" x2="{x + 272}" y2="52" stroke="{INK}" stroke-width="2"/><path d="M{x + 272} 46 L{x + 280} 52 L{x + 272} 58z" fill="{INK}"/>'
        x += 284
    o += T(0, 118, 'green = done, conclusions unchanged · blue = done with deviations recorded · orange = partly stopped / not run (status as of 2026-11-08)', 12, PEN)
    return ovl(70, 540, 1140, 124, o, 'Replication batches')


rep(91, '<ul class="t" style="font-size:21.5px;line-height:1.32">', '<ul class="t" style="font-size:16px;line-height:1.28">', 'text smaller for the figure')
ins(91, ch91(), 'figure: flow of replication batches')

# ======================================================================= 2d. rebuilt slides 82 (what we learned) and 84 (limits)
img24, _ = card_img(deck_img(24), tuple(int(v * 1.5) for v in (60, 170, 820, 640)), 380, 'Said late: target − control by layer (slide 24)')
img39, _ = card_img(deck_img(39), tuple(int(v * 1.5) for v in (40, 160, 820, 630)), 380, 'Lens readability by layer: jumps at L62 (slide 39)')
WL1 = f'''<section class="slide lt" aria-label="What we learned: read early, spoken late"><span class="tag">Stage 10–13</span>
<h2 style="font-size:56px">What we learned: read early, spoken late</h2>
<div class="wl" style="max-width:780px;grid-template-columns:190px 1fr;row-gap:10px;margin-top:14px">
<div class="k a" style="font-size:28px">Read early</div><div class="v" style="font-size:17px">Causally the title is read in L24–L50 and gathered at the name positions by L52, then no longer needed. A probe at the title token reads a little of it from L24 (re-checked).</div>
<div class="k g" style="font-size:28px">Spoken late</div><div class="v" style="font-size:17px">At the name positions, paper-specific author knowledge becomes lens-readable only from ~L50, fastest over L57–L61.</div>
<div class="k b" style="font-size:28px">No lens lead</div><div class="v" style="font-size:17px">Read with a lens at the names, target is not ahead of control in middle layers; the +0.21 gap is at the end<span class="src">(Stage 10, final L63, §6.4)</span> (probe at the title: target − control +0.03–0.08, re-checked<span class="src">(Stage 13 E4b, first name token only)</span>).</div>
<div class="k g" style="font-size:28px">Real knowledge</div><div class="v" style="font-size:17px">Name prior is ~1/3 of the gap overall but ~0 on surnames<span class="src">(Stage 12 A, 0.087 / 0.247, §6.12)</span>; the rest is paper-specific and grows with citations.</div>
<div class="k" style="font-size:28px">Lenses agree</div><div class="v" style="font-size:17px">Jacobian lenses read more in middle layers, but nothing target-specific.</div>
<div class="k a" style="font-size:28px">Name format</div><div class="v" style="font-size:17px">Initials carry little; full given names carry as much as surnames and help predict them.</div>
</div>
<div style="position:absolute;left:880px;top:118px;width:340px;z-index:2">{img24}</div>
<div style="position:absolute;left:880px;top:392px;width:340px;z-index:2">{img39}</div>
<div class="fxn" style="left:70px;top:668px;width:780px"><span class="fx">R(l) = mean(patched − false) / mean(true − false)</span><span class="nn">n = 9,108 (readouts) · 1,186 (interventions) · 1,395 (probe)</span></div>
<span class="pg"></span></section>'''
FATE[82] = 'rebuilt as HTML with the same six rows (transcribed from the picture) + two lens-curve figures of slides 24 and 39'


def ch84():
    D_ = [('label package', 9108), ('frozen cohort', 6841), ('probe (Vpd)', 4654), ('Stage 11–12 interventions', 1186), ('add. 18b items', 600), ('Stage 8', 200), ('Pilot50', 50), ('Stage 4', 20)]
    o = T(0, 14, 'Papers behind each analysis (log scale)', 15, INK, weight=700)
    X = lambda n: 180 + (math.log10(n)) / 4.1 * 300
    for n_ in (10, 100, 1000, 10000):
        o += f'<line x1="{X(n_):.1f}" y1="22" x2="{X(n_):.1f}" y2="{22 + 19 * len(D_):.1f}" stroke="#E7DADA" stroke-dasharray="3 4"/>' + T(X(n_), 36 + 19 * len(D_), f'{n_:,}', 11, PEN, 'middle')
    for i, (lab, n_) in enumerate(D_):
        y = 24 + i * 19; col = BL if n_ >= 600 else '#1B2230'
        o += T(172, y + 12, lab, 12, INK, 'end') + hbar(180, y, X(n_) - 180, 14, col, 0.8) + T(X(n_) + 5, y + 12, f'{n_:,}', 11.5, INK)
    o += ftext(0, 206, 'share of cohort = n / 9,108') + ntext(200, 206, 'n = 20 to 9,108 papers per analysis')
    return ovl(690, 452, 530, 214, o, 'Sample sizes')


LIM = f'''<section class="slide lt" aria-label="Limits (Stage 12–13)"><span class="tag">Stage 12–13 · limits</span>
<h2 style="font-size:56px">Limits</h2>
<div class="row" style="gap:30px;margin-top:4px">
<div class="col" style="font-size:16.5px;line-height:1.3"><p class="g" style="font-size:20px;margin-bottom:4px"><b>Done: Stage 12</b></p>
<p>– Single-position patching (P1); attention vs MLP (P2, hook check passed)</p><p>– Name priors (N1, N2); author-prompt lens (F1, F2): middle layers still not readable</p>
<p class="g" style="font-size:20px;margin:8px 0 4px"><b>Done: Stage 13</b></p>
<p>– Probes read year, citations, field at the title from ≤L16 (M2); identity not above the L4 text level (M3)</p>
<p>– Replacement is task-independent (X1); paraphrase meaning beyond wording in L28–L40, not separable from paper identity (X3)</p>
<p>– First author decodable at L8, may be text-explainable (X4); 5 false titles confirm the Stage 11 timing (X6, X7)</p></div>
<div class="col"><div class="note" style="font-size:17px;transform:rotate(.8deg)"><span class="h">Limits</span>– One model (Qwen3-32B)<br>– Teacher-forced preference, not generation<br>– Labels from the team lead’s package; labelling code (elm) not available<br>– H2 (paper identity) partly supported but not established<br>– H3 (hidden author knowledge): first judged insufficient; supported on the same scale after the addendum-17 locked test (slide {P[67]})</div></div>
</div>
<div class="addb" style="left:70px;top:452px;width:590px;font-size:14px"><b>Limits of the newest results:</b> addendum 19: rule locked after the data were seen; recall c50 near the top of the citation range (16 of 9,108 papers above 11,038). Item 1: 672 cells tested, no multiple-comparison correction. Item 5: crude WordNet synonyms. Items 4 / 6: one layer and component at a time, 600-paper subsample, parity WARN (bf16 batch shapes). Addendum 16: teacher-forced preferences, greedy decoding only. C: not pre-registered.</div>
{ch84()}
<span class="pg"></span></section>'''
FATE[84] = 'rebuilt as HTML: the same text (transcribed from the picture; H3 line updated as in its old box) + the limits box + a sample-size chart'

# ======================================================================= assemble + translate + remap slide numbers
NEW29 = slide_exposure(); FATE[29] = 'rebuilt: same numbers and texts (English), left chart now shows observed shares per bin + fitted curves'
NEWF, NEWD = slide_format(), slide_chain(); FATE[59] = 'split into new slides 59 (answer format B) and 60 (name chain D): same numbers, rate charts instead of forest plots'
S['29n'], S['59f'], S['59d'], S['82n'], S['84n'] = NEW29, NEWF, NEWD, WL1, LIM
for k in [o for o in order if isinstance(o, int)]: translate(k)
# slide 6: the translated How-computed line sat on a chart label -> just above the footer strip
_t6 = S[6]; S[6] = re.sub(r'<text x="70.0" y="652.0" font-size="10.5" fill="#4B5363"[^>]*>.*?</text>', lambda m: L.para(70, 662, 'How computed: target = A + C, control = B + D · 9,108 papers; 593 + 593; 1,178 pairs', 10.5, 470, '#4B5363')[0], S[6], count=1, flags=re.S); note(6, 'How computed line moved')
assert S[6] != _t6
rep(47, 'class="lead" style="top:26px"', 'class="lead" style="top:8px"', 'lead line higher')
# keys and shelves (v39 61): the right column ran into the prev / next buttons
S[61] = S[61].replace('style="font-size:18px;line-height:1.35;opacity:.85"', 'style="font-size:15px;line-height:1.25;opacity:.85"').replace('style="font-size:23px"', 'style="font-size:19px"'); note(61, 'right column 2 px smaller (nav collision)')

unused = [TR[i][0] for i in range(len(TR)) if i not in USED and TR[i][1] is not None]
OLD2NEW = {k: P[k] for k in range(1, 93) if k in P}
OLD2NEW.update({29: P['29n'], 82: P['82n'], 84: P['84n']})


def remap_text(txt):
    def one(n): n = int(n); return str(OLD2NEW[n]) if n != 59 else f'{P["59f"]}–{P["59d"]}'

    def sub(m):
        word, a, rest = m.group(1), m.group(2), m.group(3) or ''
        out = one(a)
        rest2 = re.sub(r'\d+', lambda mm: one(mm.group(0)), rest)
        if '–' in out and word == 'slide ': word = 'slides '
        return word + out + rest2
    return re.sub(r'(slides? )(\d+)((?:\s?[–,]\s?\d+)*)', sub, txt)


def remap(sec):
    return re.sub(r'>([^<]+)<', lambda m: '>' + remap_text(m.group(1)) + '<', sec)


import declutter_20261119 as DC
DREPORT = []
body = []
for o in order:
    t = S[o]
    if not (isinstance(o, str)):
        t2 = remap(t)
        if t2 != t: note(o, 'slide numbers remapped')
        t = t2
    t = DC.declutter(t, DREPORT)
    body.append(t)
OUT.write_text(head + '\n'.join(body) + tail, encoding='utf-8')
FINAL = {o: body[i] for i, o in enumerate(order)}
for k in range(1, 93):
    if k in FATE: continue
    if k in FINAL and FINAL[k] != remap(ORIG[k]) and k not in CHANGED: CHANGED[k] = ['footer / number dump decluttered']
    elif k in FINAL and FINAL[k] != ORIG[k] and k in CHANGED and FINAL[k] != remap(S[k]): CHANGED[k].append('footer / number dump decluttered')
    FATE[k] = 'kept' if ORIG[k] == S[k] and k not in CHANGED else 'kept, edited: ' + '; '.join(dict.fromkeys(CHANGED.get(k, ['slide numbers remapped'])))
rec = {'order_new_to_v39': {P[o]: o for o in order}, 'fate_v39': {str(k): FATE[k] for k in range(1, 93)}, 'unused_translations': unused}
(Path(__file__).parent / 'build_20261119_deck.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding='utf-8')
print('slides', len(order), '| unused translations', unused)
print('\n'.join(DREPORT))
