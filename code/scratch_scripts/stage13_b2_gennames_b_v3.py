"""Item 2-11b, DRAFT addendum 15 rev3 (NOT locked): matcher v3 on top of stage13_b2_gennames_b_pipeline.py (rev2 file, used by
job 11734448; not edited, imported by path and its matcher functions replaced in the imported module only).

Matcher v3 (rules N1-N12 in prereg_addendum15_DRAFT.json rev3):
  normalisation: lower case; special letters ß->ss, æ->ae, œ->oe, ø->o, ł->l, đ/ð->d, þ->th, ı->i; NFKD; non-ASCII dropped
    (accents removed: ç->c, é->e, ü->u); then inside every word 'ae'->'a', 'oe'->'o', 'ue'->'u' (so Müller = Mueller = Muller);
    non [a-z space -] -> space; words keep their hyphen group (García-López = one group of two parts).
  suffix: trailing jr / sr / ii / iii / iv removed (with or without '.' or ','), both sides, only while >= 2 words remain.
  M: initial rule as Stage 10 (first letter of the first word outside the surname group; none if the true name has no such word),
     either order (pass 1 given-first, pass 2 surname-first), and the generated surname group == the true surname group (the full
     hyphen group; a space-written hyphen compound 'Garcia Lopez' also counts).
  P (partial, '部分匹配'): not M, initial rule holds, and the generated surname group shares a part with the true surname group or
     equals the true word just before the surname (space-separated double surname, only if that word is not an initial or particle).
     Writing only the LAST word of a space-separated name stays M (cannot be told apart from middle names).
  one-to-one: M passes first (both orders), then P passes over the still unmatched true authors and generated names.
  P is excluded from the M-vs-H analysis (proposal) and reported separately.
Commands: examples --root | compare --root | tiny --root
"""
import argparse, importlib.util, json, re, sys, unicodedata
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('gnb', H / '13_stage13/stage13_b2_gennames_b_pipeline.py'); B = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(B)
_W2, _P2, _L2 = B.words, B.parse_items, B.label_items


def _rev2_parse(text, eos):
    cur = B.words; B.words = _W2
    try: return _P2(text, eos)
    finally: B.words = cur


REV2 = dict(parse_items=_rev2_parse, label_items=_L2, words=_W2)   # rev2 label_items uses V1.match_gen (V1 namespace, untouched)
SPECIAL = str.maketrans({'ß': 'ss', 'æ': 'ae', 'œ': 'oe', 'ø': 'o', 'ł': 'l', 'đ': 'd', 'ð': 'd', 'þ': 'th', 'ı': 'i'})
SUFFIX = {'jr', 'sr', 'ii', 'iii', 'iv'}
PARTICLES = {'de', 'da', 'di', 'do', 'dos', 'das', 'del', 'della', 'der', 'den', 'van', 'von', 'le', 'la', 'du', 'ten', 'ter', 'bin', 'al', 'el', 'y'}


def fold(w): return w.replace('ae', 'a').replace('oe', 'o').replace('ue', 'u')


def groups(s):
    """list of hyphen groups, each a list of normalised parts; suffixes stripped while >= 2 words remain."""
    s = unicodedata.normalize('NFKD', s.lower().translate(SPECIAL)).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z \-]', ' ', s)
    G = []
    for tok in s.split():
        parts = [fold(p) for p in tok.split('-') if p]
        if parts: G.append(parts)
    while sum(len(g) for g in G) > 2 and len(G[-1]) == 1 and G[-1][0] in SUFFIX: G.pop()
    return G


def words3(s): return [p for g in groups(s) for p in g]


def tinfo(t):
    G = groups(t)
    if not G: return None
    sg = G[-1]; rest = [p for g in G[:-1] for p in g]
    ti = rest[0][0] if rest else ''
    x = G[-2][-1] if len(G) >= 3 and len(G[-1]) == 1 and len(G[-2]) == 1 and len(G[-2][0]) > 1 and G[-2][0] not in PARTICLES else None
    return dict(sg=sg, ti=ti, x=x)


def gcands(g, swap):
    G = groups(g)
    if sum(len(x) for x in G) < 2: return []
    flat = [p for x in G for p in x]
    if not swap:
        c = [(G[-1], flat[0][0] if len(G) > 1 else '')]
        if len(G) >= 3 and len(G[-1]) == 1 and len(G[-2]) == 1: c.append((G[-2] + G[-1], flat[0][0]))   # space-written compound
        return c
    return [(G[0], G[1][0][0])] if len(G) >= 2 else []


def rel(t, g, swap):
    """'M', 'P' or None for true-author info t and generated name g."""
    if t is None: return None
    best = None
    for sg, gi in gcands(g, swap):
        if t['ti'] and gi != t['ti']: continue
        if sg == t['sg']: return 'M'
        if set(sg) & (set(t['sg']) | ({t['x']} if t['x'] else set())): best = 'P'
    return best


def match3(true, gen):
    T = [tinfo(t) for t in true]; lab = [None] * len(gen); hit = [False] * len(true)
    for want in ('M', 'P'):
        for swap in (False, True):
            for i, t in enumerate(T):
                if hit[i]: continue
                for j, g in enumerate(gen):
                    if lab[j] is None and rel(t, g, swap) == want: lab[j] = want; hit[i] = True; break
    return [l or 'H' for l in lab], sum(hit)


def label_items3(true, items):
    ok = [i for i, it in enumerate(items) if it['status'] == 'ok']
    lab, nhit = match3(true, [items[i]['name'] for i in ok])
    res = [it['status'] for it in items]
    for i, l in zip(ok, lab): res[i] = l
    return res, nhit


# ------------------------------------------------------------------ examples: rev2 cases + new cases, rev2 and rev3 labels
NEW = [
    ('N1 transliteration', ['Jürgen Müller'], 'Jurgen Muller'),
    ('N1 transliteration', ['Jurgen Muller'], 'Jürgen Mueller'),
    ('N1 eszett', ['Hans Strauss'], 'Hans Strauß'),
    ('N1 cedilla', ['Ana Gonçalves'], 'Ana Goncalves'),
    ('N1 slash-o', ['Søren Kierkegaard'], 'Soren Kierkegaard'),
    ('N3 hyphen compound written in full', ['María García-López'], 'Maria Garcia-Lopez'),
    ('N3 hyphen compound written with a space', ['María García-López'], 'Maria Garcia Lopez'),
    ('N4 space double surname, first part', ['María García López'], 'María García'),
    ('N4 space double surname, last part', ['María García López'], 'María López'),
    ('N4 middle name looks like first surname part', ['John Ronald Tolkien'], 'John Ronald'),
    ('N4 generated adds a surname part', ['María López'], 'María García-López'),
    ('N5 particle written as separate words', ['Hans Vanderberg'], 'Hans Van der Berg'),
    ('N5 apostrophe', ["Seán O'Brien"], "Sean O'Brien"),
    ('N6 suffix in generated name', ['John Smith'], 'John Smith Jr.'),
    ('N6 suffix with comma in truth', ['John Smith, Jr.'], 'J. Smith'),
    ('N6 roman suffix', ['John Henry III'], 'J. Henry'),
    ('N6 roman suffix, two-word name kept', ['Henry III'], 'Henry III'),
    ('N9 two names in one item', ['Jane Doe', 'Bob Brown'], 'Jane Doe, Bob Brown'),
    ('N8 one-to-one: M before P', ['María García-López', 'Pedro López'], 'Pedro Lopez; Maria Lopez'),
]


def examples(root):
    import pandas as pd
    rows = []
    for k, (topic, true, text) in enumerate([(f'rev2 #{i}: {t}', tr, g) for i, (t, tr, g) in enumerate(B.EXAMPLES, 1)] + NEW, 1):
        it2 = REV2['parse_items'](text, eos=True); l2, _ = REV2['label_items'](true, it2)
        it3 = B.parse_items(text, eos=True); l3, _ = label_items3(true, it3)
        for a, b, x, y in zip(it2, it3, l2, l3):
            rows.append(dict(ex=k, rule=topic, generated=text, parsed_item=b['name'], true_authors='; '.join(true), rev2_label=x, rev3_label=y,
                             words_rev3=' '.join(words3(b['name']))))
    D = pd.DataFrame(rows); root.mkdir(parents=True, exist_ok=True); D.to_csv(root / 'matcher_examples.csv', index=False)
    L = ['| # | generated (item) | true author(s) | rev2 | rev3 | rule |', '|---|---|---|---|---|---|']
    for r in D.itertuples():
        L.append(f'| {r.ex} | {r.parsed_item}{"" if r.parsed_item == r.generated else f" (from: {r.generated})"} | {r.true_authors} | {r.rev2_label} | **{r.rev3_label}** | {r.rule} |')
    (root / 'matcher_examples.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True); return D


# ------------------------------------------------------------------ stored texts: rev2 vs rev3 label counts
def compare(root):
    import pandas as pd
    _, d = B.load_papers()
    o = pd.read_json(B.LAB / 'open_results.jsonl', lines=True)[['paper_id', 'generated_text', 'finish_reason']]
    x = d.merge(o, on='paper_id'); rows = []
    for r in x.itertuples():
        true = str(r.authors).split('; '); eos = r.finish_reason == 'stop'
        i2 = REV2['parse_items'](r.generated_text, eos); l2, _ = REV2['label_items'](true, i2)
        i3 = B.parse_items(r.generated_text, eos); l3, _ = label_items3(true, i3)
        for j, (a, b) in enumerate(zip(l2, l3)):
            rows.append(dict(paper_id=r.paper_id, group_tight=r.group_tight, item=j, name=i3[j]['name'], rev2=a, rev3=b))
    D = pd.DataFrame(rows); D.to_parquet(root / 'stored_rev2_vs_rev3.parquet', index=False)
    ct = pd.crosstab(D.rev2, D.rev3, margins=True); ct.to_csv(root / 'stored_rev2_vs_rev3_crosstab.csv')
    by = D.groupby('group_tight').rev3.value_counts().unstack(fill_value=0); by.to_csv(root / 'stored_rev3_by_group.csv')
    def prim(lab):
        g = D[D.group_tight == 'target'].groupby('paper_id')[lab].agg(lambda s: (s == 'M').any() and (s == 'H').any()); return int(g.sum())
    res = dict(papers=int(x.paper_id.nunique()), items=len(D), rev2=D.rev2.value_counts().to_dict(), rev3=D.rev3.value_counts().to_dict(),
               changed=int((D.rev2 != D.rev3).sum()), transitions=D[D.rev2 != D.rev3].groupby(['rev2', 'rev3']).size().to_dict().__repr__(),
               primary_target_papers=dict(rev2=prim('rev2'), rev3=prim('rev3')))
    (root / 'stored_rev2_vs_rev3.json').write_text(json.dumps(res, indent=1, default=str)); print(ct.to_string()); print(json.dumps(res, indent=1, default=str), flush=True)
    ex = D[D.rev2 != D.rev3].groupby(['rev2', 'rev3']).head(8)
    ex.to_csv(root / 'stored_changed_examples.csv', index=False); return res


def patch():
    B.words = words3; B.label_items = label_items3; B.examples = examples   # B.parse_items (rev2 code) now counts / dedups with words3


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['examples', 'compare', 'tiny']); ap.add_argument('--root', required=True); a = ap.parse_args()
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True)
    patch()
    if a.cmd == 'examples': examples(root); return
    if a.cmd == 'compare': compare(root); return
    if a.cmd == 'tiny':
        ok = B.tiny(root); compare(root); sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
