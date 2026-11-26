# The five other stage-expansion figures on the L24–L40 v2 template. Content from 27_v67/experiment_tree.md
# (trees 1–7 and "The full story" bands); no new numbers. 2026-11-25.
import sys
import picto as P0, picto2 as P
from stage_engine import render
from mk_latex import render as tex

def B(t): return (t, 'b', 'B')
def b(t): return (t, 'b')
def G(t): return (t, 'g', 'B')
def g(t): return (t, 'g')
def X(t): return (t, 'x', 'B')
def x(t): return (t, 'x')
def Rr(t): return (t, 'r', 'B')
def r(t): return (t, 'r')
def S(t): return (t, 'p', 'S')
def d(t): return (t, 'd')
def note(t, k='b'): return (t, k, 'I')

SPECS = {}

# =========================== L0–L4 ===========================
SPECS['L0_L4'] = dict(
    title='Stage ① · L0–L4: the input words decide almost everything',
    band='L0–L4', loc=(0, 47, 0, 4, '#DDE2E8', '#6A7385'), tint='#EEF1F5',
    rows=[
        dict(kind='boxes', lead='both near the ceiling — why?', boxes=[
            dict(pic=P.colon_move, title='":" new question vs new paper',
                 det=['move only the question, or only the paper; how far does the ":" state move?'],
                 concl=[B('":" follows the question from the start'), d('L4: new question 0.443, new paper 0.094 (4.7×)'),
                        x('much of it is just different words'), note('descriptive')]),
            dict(pic=P0.ceiling, title='Same title under another question',
                 det=['keep the title, change the question; compare the title states'],
                 concl=[B('same title, same state'), d('cos 0.9976 at L4 (two papers: 0.45); retrieval 1.000 at L4–L44'),
                        note('exploratory')])]),
        dict(kind='pill', text='Where does the ceiling come from?'),
        dict(kind='boxes', boxes=[
            dict(pic=P.layer0_same, title='Layer 0 of the three prompts',
                 det=['authors / year / field prompt: compare the last token'],
                 concl=[B('identical at layer 0 (1.0)'), note('exploratory')]),
            dict(pic=P.embed_only, title='Embedding alone',
                 det=['last title token, no forward pass'],
                 concl=[B('identity index 0.998'), d('[0.998, 0.999]'), note('exploratory')]),
            dict(pic=P.bert_find, title='A model that knows no papers',
                 det=['BERT retrieves the same title across questions'],
                 concl=[B('retrieval 1.000 from its layer 1'), note('exploratory')])]),
        dict(kind='joint', lines=[('The ceiling comes from identical input words,', True), ('not from knowing the paper   (all three together)', False)]),
        dict(kind='over', old=['“the title state does not change across questions” supports paper identity'],
             new=['→ cannot separate meaning from identity']),
        dict(kind='concl', lines=[('Stage conclusion: at L0–L4 the input words set the states;', True),
                                  ('L4 is the literal baseline for every "beyond the words" test', True)]),
    ],
    side=[
        dict(side='L', row=2, pic=P0.ceiling, pich=70, title='Rescue: L4 baseline audit', arrow='p',
             rows=[d('run to find where the ceiling comes from;'), d('without it "same state" could still be'), d('read as identity')]),
        dict(side='L', row=4, title='Early reading withdrawn', arrow='r',
             rows=[S('“change-the-question test'), S('supports identity”'), Rr('→ withdrawn by the ceiling audit')]),
        dict(side='R', row=0, title='Cannot be decided here', arrow='x',
             rows=[x('a distance says the states differ,'), x('not what they encode')]),
        dict(side='R', row=5, pic=P.paraphrase if hasattr(P, 'paraphrase') else P0.paraphrase, pich=128, title='Hands on to L4–L40', arrow='p',
             rows=[d('paraphrase closeness is measured'), d('above its L4 level: G′ − G′(L4)'), x('every question-only test is at the'), x('ceiling from L4 on')]),
    ],
    tex=(r"$\mathrm{ratio}=d_{\mathrm{new\ question}}(:)\ /\ d_{\mathrm{new\ paper}}(:),\quad \cos(h^{q_1}_{\mathrm{title}},h^{q_2}_{\mathrm{title}})$",
         r"$n=9{,}108\ \mathrm{papers}\ (\mathrm{colon\ distances,\ ceiling\ audit})$"),
    reading='ratio > 1: the ":" state moves more with the question than with the paper',
)

# =========================== L4–L24 ===========================
SPECS['L4_L24'] = dict(
    title='Stage ② · L4–L24: early read-in; first traces of the title and of the first author',
    band='L4–L24', loc=(9, 28, 5, 23, '#FFF6E8', '#B8601A'), tint='#FFF6E8',
    rows=[
        dict(kind='boxes', lead='":" carries the question — and the title?', boxes=[
            dict(pic=P.probe_transfer, title='Does a ":" probe survive a new question?',
                 det=['train a field probe at ":" under one question, test it under another'],
                 concl=[B('":" keeps following the question'), d('transfer only 0.24–0.41 (L4–L52)'), note('descriptive')]),
            dict(pic=P.sink, title='Where ":" looks (format supplement)',
                 det=['measure ":" attention; cut gently, keeping position 0'],
                 concl=[B('62–92% goes to position 0'), b('keeping it, the names answer type holds from L4'), note('exploratory')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P.timeline, title='Layer order',
                 det=['line up results by the earliest layer each kind of information appears'],
                 concl=[B('title facts and the first-author token first appear at L8–L16'), note('descriptive')]),
            dict(pic=P.probe_attr, title='Paper attributes at the title',
                 det=['a probe on the last title token reads the year'],
                 concl=[X('year R² rises from 0.38 at L16,'), x('but it can be inferred from the title words'), note('descriptive', 'x')]),
            dict(pic=P0.paraphrase, title='Paraphrased title',
                 det=['reword the title; is its state still closer to the original than to other papers?'],
                 concl=[B('closeness rises above its L4 level from L8'), d('meaning beyond the words starts here'), note('pre-registered + exploratory')])]),
        dict(kind='joint', lead='anything beyond meaning this early?', lines=[('Early read-in: the title starts to be encoded beyond its words', True), ('from L8–L16   (only layer order and paraphrase together)', False)]),
        dict(kind='boxes', boxes=[
            dict(pic=P.surname_l8, title='L8 surname confirmatory test (6,048 new papers)',
                 det=['move the L8 title state into "Paper: X / The first author of the paper is"; subtract a topic-matched partner; three tests fixed before the run'],
                 concl=[B('beyond topic: +0.046 [+0.035, +0.056]'), x('beats text alone? marginal · larger if recognised? marginal'),
                        x('about half of the raw signal is topic'), note('locked test')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P.probe_groups, title='Probe at the title, recognised vs not',
                 det=['train a probe at the title to read the true author; compare groups within citation bins'],
                 concl=[B('already separates a little at L24: +0.052 [+0.018, +0.086]'), note('descriptive')])]),
        dict(kind='concl', lines=[('Stage conclusion: L4–L24 is read-in only; meaning beyond the words', True),
                                  ('starts at L8, with one small locked surname exception', True)]),
    ],
    side=[
        dict(side='L', row=3, pic=P.source_check, pich=80, title='Ruled out: literal overlap', arrow='r',
             rows=[r('source check: the surname is not'), r('simply in the title (≈ 0)')]),
        dict(side='L', row=3, pic=P.topic_pair, pich=80, title='Rescue: topic-matched test too small', arrow='p',
             rows=[S('“mixed” (1,178 papers)'), Rr('→ confirmatory test on 6,048'), Rr('new papers: small locked exception')]),
        dict(side='R', row=0, title='Hands on to L48–L56', arrow='p',
             rows=[d('the ":" state still matters at L56;'), x('the format layer is not pinned down')]),
        dict(side='R', row=1, title='Top lens word: cannot decide', arrow='x', dash='6 4',
             rows=[d('at L24–L48 the top lens word is mostly'), d('punctuation or format,'), x('but it changes with the title for'), x('28–64% of name tokens')]),
        dict(side='R', row=3, title='Cannot be decided', arrow='x', dash='6 4',
             rows=[x('the text baseline failed its own'), x('positive control; locked test only at L8'),
                   d('later layers larger (peak +0.093 at L40),'), d('≈ 0 again by L56 (descriptive)')]),
    ],
    tex=(r"$T_1=s_{\mathrm{own}}-s_{\mathrm{topic\ partner}},\quad G'-G'(L4)=\mathrm{closeness}(\mathrm{paraphrase})-\mathrm{closeness\ at\ }L4$",
         r"$n=6{,}048\ \mathrm{new\ papers\ (surname\ test)}\ \cdot\ 9{,}108\ \mathrm{(probes,\ paraphrase)}$"),
    reading='T1 > 0: the L8 title state carries surname information beyond its topic',
)

# =========================== L40–L52 ===========================
SPECS['L40_L52'] = dict(
    title='Stage ④ · L40–L52: the title reaches the names over several layers in parallel; read by L52',
    band='L40–L52', loc=(9, 47, 41, 52, '#FBEAA0', '#1F6F8B'), tint='#FBF3CF',
    rows=[
        dict(kind='boxes', xcheck=True, boxes=[
            dict(pic=P.putback, title='Put back (gives it back)',
                 det=['copy the true-title states of the 15 after-title positions into the false-title run at one layer'],
                 concl=[B('restores 0.821 at L48, 0.995 at L52'), d('half-way at L45'), note('settled')]),
            dict(pic=P.takeaway, title='Take away (cuts it off)',
                 det=['from a layer to L63, block those positions from reading any title token'],
                 concl=[B('loss ≤ 0.05 from L52 on'), note('settled')])]),
        dict(kind='joint', lead='where does it land, and by which route?', lines=[('The title is read and has reached the after-title positions by L52', True), ('(opposite directions agree: a cross-check)', False)]),
        dict(kind='boxes', boxes=[
            dict(pic=P.position_copy, title='Position by position',
                 det=['copy one position group at a time (600 papers)'],
                 concl=[B('lands mainly on the names'), d('names alone 0.176 (L40) → 0.605 (L48) → 0.835 (L52); ":" 0.073 → 0.177'), note('descriptive')]),
            dict(pic=P.edge_block, title='Windowed attention-edge blocking',
                 det=['cut one attention edge in one 4-layer window'],
                 concl=[B('name ← title carries the delivery in L44–L55'), d('L48–51 loss +0.0112 [+0.0084, +0.0138]'), note('locked test')]),
            dict(pic=P.layer_sweep, title='Single-layer sweep',
                 det=['cut one edge at one layer at a time, L40–L56'],
                 concl=[B('no single-layer bottleneck'), d('name ← title at L44, L48, L52, L54; any one cut ≤ 1.25%'), note('locked test')])]),
        dict(kind='joint', lines=[('Delivered over the name ← title edge,', True), ('through several layers in parallel   (only all three together)', False)]),
        dict(kind='over', old=['one route, one layer'], new=['→ several layers in parallel']),
        dict(kind='concl', lines=[('Stage conclusion: by L52 the title has reached the name positions,', True),
                                  ('through several layers in parallel', True)]),
    ],
    side=[
        dict(side='L', row=0, pic=P.five_titles, pich=100, title='Ruled out: a lucky false title', arrow='r',
             rows=[r('same timing for all five false titles'), d('R(L52) 0.994–0.997')]),
        dict(side='L', row=2, pic=P.groups_timing, pich=112, title='Ruled out: recognised papers read earlier', arrow='r',
             rows=[r('recognition changes size, not timing'), d('R(L48) 0.90 vs 0.81; group differences'), d('are a small-denominator effect')]),
        dict(side='R', row=0, title='From stage ① (phenomenon)', arrow='p',
             rows=[d('groups (target / control) and scoring'), d('(true − five false titles)')]),
        dict(side='R', row=2, pic=P.probe_groups, pich=124, title='Name-position probe', arrow='b',
             rows=[B('separates recognised from not at L40:'), b('+0.031 [+0.019, +0.044]'), note('pre-registered'), d('→ the form of what arrives: L48–L56')]),
        dict(side='R', row=4, title='Cannot be decided', arrow='x', dash='6 4',
             rows=[x('a single-layer cut is only a lower bound;'), x('600-paper sub-sample')]),
    ],
    tex=(r"$R(l)=\frac{S_{\mathrm{patched}}(l)-S_{\mathrm{false}}}{S_{\mathrm{true}}-S_{\mathrm{false}}},\quad \mathrm{loss}=S_{\mathrm{true}}-S_{\mathrm{cut}}$",
         r"$n=1{,}186\ \mathrm{papers\ (put\ back\ /\ take\ away)}\ \cdot\ 600\ \mathrm{(positions,\ edges,\ sweep)}$"),
    reading='R ≈ 1: the copied state restores all of the true-title advantage',
)

# =========================== L48–L56 ===========================
SPECS['L48_L56'] = dict(
    title='Stage ⑤ · L48–L56: the probe reads it, the lens does not; paper information, not ready-made names',
    band='L48–L56', loc=(29, 47, 48, 56, '#C9DAF0', '#3C78B4'), tint='#E8F0FA',
    rows=[
        dict(kind='boxes', boxes=[
            dict(pic=P.lens_cannot, title='Lens fitted on author prompts',
                 det=['do the name positions read the true author in vocabulary directions?'],
                 concl=[B('lens cannot read it'), d('target − control ≤ 0 at L24–L56 (−0.058 at L48)'), note('pre-registered')]),
            dict(pic=P.probe_can, title='Probe at the name positions',
                 det=['train a probe at the name positions; recognised vs not'],
                 concl=[B('probe can'), d('L40 +0.031, L48 +0.053 [+0.038, +0.067]'), note('pre-registered')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P.same_scale, title='Same-scale test',
                 det=['exactly the same 9,137 name tokens, probe and lens on one rank scale'],
                 concl=[B('the probe reads more: +0.062 [+0.041, +0.081] at L48'), note('locked test')])]),
        dict(kind='joint', lead='held where, and in what form?', lines=[('Author information is linearly readable at the names,', True), ('not in vocabulary directions   (only the three together)', False)]),
        dict(kind='boxes', boxes=[
            dict(pic=P0.subspace, title='Swap only the author subspace',
                 det=['swap the probe’s author slice vs the whole state'],
                 concl=[B('carries only ~7%'), d('0.032 vs 0.457'), note('pre-registered')]),
            dict(pic=P.spread, title='Direction analysis',
                 det=['directions along which recognised and unrecognised differ'],
                 concl=[B('no component above 7%'), note('exploratory')]),
            dict(pic=P.readout_map, title='Readout map',
                 det=['every position before the names × every layer, three readouts'],
                 concl=[B('no earlier shelf'), d('only scattered weak traces in 672 cells'), note('exploratory')])]),
        dict(kind='joint', lead='what do the late layers do with it?', lines=[('Spread out: not one clean subspace, not one direction,', True), ('no earlier shelf   (each rules out one alternative)', False)]),
        dict(kind='boxes', boxes=[
            dict(pic=P.mlp_swap, title='What the L52–L56 MLPs carry',
                 det=['swap in the true-title MLP output, or only its 512 author-name directions'],
                 concl=[B('paper information, not ready-made names'), d('whole 0.158–0.275 vs names 0.022–0.042'), note('descriptive')]),
            dict(pic=P.inject, title='Injecting the author direction',
                 det=['add the probe’s author direction at L48–L52; control: another author’s direction'],
                 concl=[X('2.5% → 9.7%, but another author is written too:'), x('mainly a write channel; cannot show stored-but-unused'), note('locked test', 'x')])]),
        dict(kind='over', old=['author information is already in the middle layers'],
             new=['→ linearly readable: small effect, correlational evidence']),
        dict(kind='concl', lines=[('Stage conclusion: at the names the probe reads it and the lens does not;', True),
                                  ('what arrives is paper information, spread out, not ready-made names', True)]),
    ],
    side=[
        dict(side='L', row=1, title='Rescue: different scales', arrow='r',
             rows=[S('“partly supported”'), S('(sizes not comparable)'), Rr('→ supported on the same scale')]),
        dict(side='L', row=5, pic=P.colon_swap, pich=104, title='Rewritten: the format layer', arrow='r',
             rows=[S('“the format is fixed only at L56'), S('(locked)”'), Rr('→ the locked rule gives L56 but is'), Rr('distorted by cutting the sink;'), Rr('the layer is not pinned down')]),
        dict(side='R', row=0, title='Cannot be decided', arrow='x', dash='6 4',
             rows=[x('at L48 the lens is negative (−0.058)'), x('while the probe is positive (+0.053):'), x('no explanation yet')]),
        dict(side='R', row=3, title='From stage ④ (route)', arrow='p',
             rows=[d('delivered to the name positions'), d('by L52 (names alone 0.835)')]),
        dict(side='R', row=5, title='Dependencies that end here', arrow='p',
             rows=[b('swap ":" at L56 for the year or field'), b('prompt’s: author signal −0.03'), note('locked test'),
                   d('real-title extra above 0 only from L56;'), d('L8 surname signal ≈ 0 by L56')]),
    ],
    tex=(r"$\Delta=\mathrm{score}_{\mathrm{probe}}-\mathrm{score}_{\mathrm{lens}}\ (\mathrm{same\ tokens,\ one\ rank\ scale}),\quad \mathrm{share}=\mathrm{moved}_{\mathrm{slice}}/\mathrm{moved}_{\mathrm{whole}}$",
         r"$n=9{,}137\ \mathrm{name\ tokens\ (same\ scale)}\ \cdot\ 9{,}108\ \mathrm{papers}\ \cdot\ 600\ \mathrm{(MLP\ swap,\ injection)}$"),
    reading='Δ > 0: the probe reads more author information than the lens at the same positions',
)

# =========================== L56–L63 ===========================
SPECS['L56_L63'] = dict(
    title='Stage ⑥ · L56–L63: the late MLPs write the name; it gets stuck at writing',
    band='L56–L63', loc=(29, 47, 57, 63, '#F6B8B0', '#C0392B'), tint='#FBE3E1',
    rows=[
        dict(kind='boxes', boxes=[
            dict(pic=P.mean_ablate, title='Mean ablation at L57–L61',
                 det=['replace one layer’s MLP or attention with its average over other papers (600 papers)'],
                 concl=[B('the late MLPs, not attention, write the name'), d('MLP − attention +0.040 [+0.036, +0.045]; each MLP layer removes 11–14%'), note('settled')])]),
        dict(kind='boxes', lead='which part of the name is hard?', boxes=[
            dict(pic=P.gap_grows, title='Group comparison',
                 det=['recognised − unrecognised at each layer'],
                 concl=[B('builds over the last dozen layers'), d('steepest at L57–L61; +0.207 [0.195, 0.220] at the output'), note('settled')]),
            dict(pic=P.rank_late, title='Names become readable late',
                 det=['rank of the true name over the vocabulary'],
                 concl=[B('about rank 10 only at L62'), note('settled')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P.token_parts, title='Which tokens carry the signal',
                 det=['signal by token type'],
                 concl=[B('surname 1st +0.68, rest +0.58, initial +0.13'), note('full cohort, descriptive')]),
            dict(pic=P.first_rest, title='First token or the rest',
                 det=['split by name format'],
                 concl=[B('initials: first ~0.1 vs later ~0.45'), note('descriptive')]),
            dict(pic=P.given_helps, title='Given name helps the surname',
                 det=['is the surname stronger when the given name is in the top 10?'],
                 concl=[B('full given name +0.22; initial only ≈ 0'), note('full cohort, descriptive')])]),
        dict(kind='joint', lines=[('The signal sits on surnames and full given names;', True), ('the start of the name is hardest   (the three together)', False)]),
        dict(kind='boxes', lead='too weak, or something else?', boxes=[
            dict(pic=P.initial_given, title='Giving the first initial',
                 det=['add the first author’s initial to the prompt; 600 + 600 papers per format'],
                 concl=[B('stuck at the first piece; supplying it helps'), d('recognised papers with a full correct author 4.0% → 15.2%'), note('locked test')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P.amplify, title='Strengthening the arrived signal',
                 det=['amplify the paper’s own arrived signal at L48–L56'],
                 concl=[B('does not help: 2.5% → 2.8%'), note('locked test')]),
            dict(pic=P.dir_len, title='Why pushing hurts',
                 det=['push only length, or only direction'],
                 concl=[B('direction-only pushes hurt in 9 of 9 cells'), d('length-only only near the writer'), note('locked test')]),
            dict(pic=P.rise_fall, title='Late suppression',
                 det=['papers whose name rises after L56, then falls'],
                 concl=[B('12.8% recognised vs 9.1% not'), x('+0.037 [+0.002, +0.073]: just past the bound'), note('locked test')])]),
        dict(kind='joint', lines=[('The bottleneck is the late writing step,', True), ('not signal strength   (only all of them together)', False)]),
        dict(kind='over', old=['the signal is too weak'], new=['→ strengthening does not help; the harm comes from direction']),
        dict(kind='concl', lines=[('Stage conclusion: the late MLPs write the name, and it gets stuck', True),
                                  ('at writing, hardest at the start of the name', True)]),
    ],
    side=[
        dict(side='L', row=2, title='Rescue: small samples (20 pairs)', arrow='r',
             rows=[S('“the gap sits on the rest of the name”'), Rr('→ it was initials vs full given names')]),
        dict(side='L', row=5, pic=P.reversal, pich=96, title='Ruled out: reversal curse', arrow='r',
             rows=[r('title from the authors is slightly harder:'), d('−0.032 [−0.047, −0.016]')]),
        dict(side='L', row=6, pic=P.fabricated, pich=96, title='Ruled out: mixed-up names', arrow='r',
             rows=[r('fabricated names are not neighbours;'), r('about half are not in the data at all')]),
        dict(side='R', row=0, title='From stages ④ and ⑤', arrow='p',
             rows=[d('delivered before L52; paper'), d('information, not ready-made names')]),
        dict(side='R', row=2, title='Exception: co-authors help', arrow='b',
             rows=[b('given the true first author, more'), b('are written (11.8% vs 1.5%), but via the'), b('co-author network, not this paper'), note('pre-registered')]),
        dict(side='R', row=4, pic=P.realfake, pich=118, title='Real vs made-up names', arrow='x',
             rows=[x('states AUROC 0.72–0.78, only +0.05–0.06'), x('above output confidence (0.711), L40–L52'), note('exploratory', 'x')]),
        dict(side='R', row=6, pic=P.gap_icon, pich=60, title='Known gap ①', arrow='x', dash='7 5',
             rows=[x('do the late MLPs hold this paper’s'), x('author knowledge? Not tested directly;'), x('only indirect evidence')]),
    ],
    tex=(r"$\mathrm{MLP}-\mathrm{attn}=\Delta S(\mathrm{mean\ ablate\ MLP}_l)-\Delta S(\mathrm{mean\ ablate\ attn}_l),\quad l\in[57,61]$",
         r"$n=600\ \mathrm{papers\ (ablation,\ writing\ tests)}\ \cdot\ 9{,}108\ \mathrm{(group\ comparison,\ token\ types)}$"),
    reading='MLP − attention > 0: the MLPs, not attention, write the name',
)

if __name__ == '__main__':
    keys = sys.argv[1:] or list(SPECS)
    for k in keys:
        sp = SPECS[k]
        tex(sp['tex'][0], f'tex_{k}_f.png'); tex(sp['tex'][1], f'tex_{k}_n.png')
        sp['tex_f'], sp['tex_n'] = f'tex_{k}_f.png', f'tex_{k}_n.png'
        print(k, render(sp, f'stage_{k}_v2.svg'))
