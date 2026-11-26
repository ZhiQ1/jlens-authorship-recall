# Build the 16:9 deck versions of the six stage-expansion figures (content unchanged). 2026-11-25.
import picto as P0, picto2 as P
from build_stages_v2 import SPECS, B, b, G, g, X, x, Rr, r, S, d, note
from stage_deck import render_deck

# L24–L40: same content as build_stage_L24_L40_v2.py, written as a spec
SPECS['L24_L40'] = dict(
    title='Stage ③ · L24–L40: what is read is meaning and specific words, not paper identity',
    band='L24–L40', loc=(9, 19, 24, 40, '#FFC98A', '#D9772B'), tint='#FFF1DE',
    rows=[
        dict(kind='boxes', lead='it is meaning — but is it also this exact paper?', boxes=[
            dict(pic=P0.words_carry, title='Which title words carry the signal?', det=['swap one word class for random tokens or for WordNet synonyms'],
                 concl=[B('content words carry it by meaning'), d('random −0.37 vs synonym −0.09 of 0.33'), note('descriptive')]),
            dict(pic=P0.paraphrase, title='Paraphrased title', det=['reword the title, keep the meaning; is the state still closer to the original?'],
                 concl=[B('meaning is encoded beyond the words'), d('closeness above L4 peaks at L36, +0.16'), note('pre-registered')])]),
        dict(kind='boxes', boxes=[
            dict(pic=P0.madeup, picw=250, title='Made-up title with the same meaning', stroke=INK if False else '#22304A', sw=2.4,
                 det=['score the true authors under the true title, a same-meaning made-up title and five other papers’ titles; how much of “true − other” does the made-up title bring back?'],
                 concl=[B('a same-meaning made-up title brings back ~75% (0.75 [0.72, 0.78])'), b('the real title adds a small extra, +0.11'), note('locked test')])]),
        dict(kind='pill', text='What is the small extra part?'),
        dict(kind='boxes', boxes=[
            dict(pic=P0.rare_common, title='Rare vs common words', det=['black out only rare (or only common) words of the true title'],
                 concl=[B('sits on specific words'), d('rare −0.16 · common −0.03'), note('locked test')]),
            dict(pic=P0.recog_citation, title='Recognised / citation check', det=['is the extra larger for recognised or much-cited papers?'],
                 concl=[B('not larger if recognised; smaller if much-cited'), note('locked test')]),
            dict(pic=P0.variance_pie, title='Variance split', det=['what explains the title state: words, meaning or identity?'],
                 concl=[B('identity adds ≈ 0'), d('meaning adds 0.17–0.27'), note('locked test')]),
            dict(pic=P0.subspace, title='Paper-facts subspace', det=['swap only the slice of the state that predicts facts'],
                 concl=[B('no author info there'), d('slice 0.004 vs whole 0.93'), note('pre-registered')])]),
        dict(kind='joint', lines=[('The real title’s small extra comes from specific words,', True), ('not from recognising the paper   (only all four together)', False)]),
        dict(kind='over', old=['middle layers store “which paper this is” (partly supported)'], new=['→ not a general paper identity, with one small locked exception']),
        dict(kind='concl', lines=[('Stage conclusion: what is read in L24–L40 is meaning and', True), ('specific words, not paper identity', True)]),
    ],
    side=[
        dict(side='L', row=1, pic=P0.ceiling, pich=70, title='Ceiling audit', arrow='x',
             rows=[('early tests (change the question, copy the state, find the paper again)', 'p'), S('“supports identity”'),
                   ('→ cannot separate: same words, same state', 'x', 'B')]),
        dict(side='L', row=5, title='Ruled out (for the exception)', arrow='r',
             rows=[('surname simply in the title — ruled out by the source check', 'r', 'N'), ('only the field’s common surnames — ruled out by the topic-matched test', 'r', 'N')]),
        dict(side='R', row=1, pic=P0.pipe_dep, pich=56, title='From stage ④ (route)', arrow='p',
             rows=[('the title is read and delivered by L52 (put back 0.995)', 'p')]),
        dict(side='R', row=1, title='Caveat: made-up title', arrow='x', dash='6 4',
             rows=[x('made-up titles are more likely to the model'), x('(log-prob +0.12 higher); closer meaning brings'), x('back more → part of the extra may be closeness'), x('the made-up title missed')]),
        dict(side='R', row=3, title='Caveat: rare vs common words', arrow='x', dash='6 4',
             rows=[x('the two swaps replace unequal counts'), x('(3.4 vs 2.1 words); common words are'), x('frequency-matched, not synonyms'),
                   d('equal counts: the gap remains, +0.07'), note('exploratory', 'x')]),
        dict(side='R', row=5, pic=P0.name_tag, pich=40, title='Small locked exception', arrow='b',
             rows=[B('L8 surname signal beyond topic, +0.05'), ('two of three tests marginal; about half of the raw signal is topic', 'p')]),
    ],
    tex_f='tex_stage_f.png', tex_n='tex_stage_n.png',
    reading='φ ≈ 1: meaning alone is enough; R > 0: the real title adds something',
)
INK = '#22304A'
if __name__ == '__main__':
    import sys
    order = ['L0_L4', 'L4_L24', 'L24_L40', 'L40_L52', 'L48_L56', 'L56_L63']
    for k in (sys.argv[1:] or order):
        sp = SPECS[k]
        sp.setdefault('tex_f', f'tex_{k}_f.png'); sp.setdefault('tex_n', f'tex_{k}_n.png')
        for fn, bot in render_deck(sp, f'stage_{k}'):
            print(fn, int(bot))
