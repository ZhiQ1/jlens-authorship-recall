#!/usr/bin/env python3
"""H2 fictitious titles, checks v3 (CPU; user decision 2026-11-19). Changes vs v2 (h2fict_check_v2.py, kept):
  1. Short true titles (<= 5 words): Crossref top 10, reject if any hit has normalized equality or jaccard2 >= 0.4
     (other papers: top 3, >= 0.5, as v2).
  2. NLI near-paraphrase rule: one-way p(entail) > 0.9 now rejects when cos_true >= 0.70 (v2: 0.75); two-way
     entailment (both >= 0.5) rejects as before.
  3. Fast mode: local filters first (cheap ones, then NLI only on candidates that passed the cheap ones); Crossref only
     for candidates that pass ALL local filters, per paper in descending cos_true order, stopping at the first that
     passes. The selection rule (highest cos_true among passing candidates) gives the same title as querying all.
     Unqueried candidates have ext = NaN ("not needed"). 1 request/s, generic User-Agent, cache.
  4. Overlap with the 9,108 cohort titles vectorised (sparse binary matrix), same jaccard2 values as v2.
Other filters unchanged from v2 (exact, corpus_j2 >= 0.5, j2_true >= 0.3, length max(30 %, 3 tok), cos band
0.30 .. min(0.85, cos_para - 0.1), first word). Exclusion rule unchanged: no passing candidate after round 2 -> excluded.

  python h2fict_check_v3.py --round R [--out OUT]        (H2F_SAMPLE=s11 default | s60)
  python h2fict_check_v3.py --final [--out OUT]
  python h2fict_check_v3.py --refilter-v2 [--out OUT]    quick check: v3 rules applied to the v2 60-paper candidates
"""
import argparse, difflib, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path.home() / 'jlens_work/13_stage13')); sys.path.insert(0, str(Path(__file__).parent))
from stage13_para_nli import words2, jac          # noqa: E402
from h2fict_gen_v3 import first_word, load_sample  # noqa: E402
from h2fict_check_v2 import skeleton, emb, nli_probs  # noqa: E402

ROOT = Path('/scratch/zhang.zhiqi2/jlens'); V1 = ROOT / '391_groups/h2_fictitious'
PAPERS = ROOT / '351_stage10/cohort/papers.parquet'
FALSE = ROOT / '351_stage10/cohort/conditions/false_titles.parquet'
PARA = ROOT / '381_stage13/summary_x3/para_nli.csv'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())
LOCAL = ['exact', 'corpus_j2', 'j2_true', 'len', 'cos_low', 'cos_high', 'first', 'nli']
FAILS = LOCAL + ['ext', 'ext_err']
SHORT_WORDS = 5; COS_ONEWAY = 0.70


class Crossref:
    def __init__(self, path):
        self.path = path; self.c = {}; self.last = 0.0; self.n_query = 0
        if path.exists():
            for l in path.open():
                x = json.loads(l); self.c[x['key']] = x
        self.f = path.open('a')

    def get(self, title, rows):
        key = f'{norm(title)}|{rows}'
        if key in self.c and self.c[key].get('ok'): return self.c[key]
        url = f'https://api.crossref.org/works?rows={rows}&select=title&query.bibliographic=' + urllib.parse.quote(title)
        rec = dict(key=key, ok=False, hits=[])
        for attempt in range(4):
            wait = 1.0 - (time.time() - self.last)
            if wait > 0: time.sleep(wait)
            self.last = time.time(); self.n_query += 1
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'title-novelty-check/0.1'})
                items = json.load(urllib.request.urlopen(req, timeout=30))['message']['items']
                rec = dict(key=key, ok=True, hits=[it['title'][0] for it in items if it.get('title')]); break
            except Exception as e:
                rec['err'] = f'{type(e).__name__}: {e}'[:200]; time.sleep(5 * (attempt + 1))
        self.c[key] = rec; self.f.write(json.dumps(rec) + '\n'); self.f.flush()
        return rec


def ext_eval(cr, cand, short):
    rows, thr = (10, 0.4) if short else (3, 0.5)
    r = cr.get(cand, rows); hits = r['hits']
    if hits:
        b = max(hits, key=lambda h: jac(words2(h), words2(cand))); bj = jac(words2(b), words2(cand))
    else: b, bj = '', 0.0
    eq = any(norm(h) == norm(cand) for h in hits)
    return dict(ext_title=b, ext_j2=bj, ext_equal=eq, ext_ok=r['ok'], ext_rows=rows, ext_thr=thr,
                f_ext=bool(eq or bj >= thr), f_ext_err=not r['ok'])


def corpus_overlap(cands, own_ids, corpus):
    from sklearn.preprocessing import MultiLabelBinarizer
    W = [words2(t) for t in corpus.title]; Cw = [words2(c) for c in cands]
    mlb = MultiLabelBinarizer(sparse_output=True).fit(W + Cw)
    A = mlb.transform(W).astype(np.float32).tocsr(); B = mlb.transform(Cw).astype(np.float32).tocsr()
    la = np.asarray(A.sum(1)).ravel(); lb = np.asarray(B.sum(1)).ravel()
    pid = corpus.paper_id.to_numpy(); best, bt = [], []
    for i0 in range(0, B.shape[0], 512):
        I = (B[i0:i0 + 512] @ A.T).toarray()
        J = I / np.maximum(1, lb[i0:i0 + 512, None] + la[None, :] - I)
        J[pid[None, :] == np.asarray(own_ids[i0:i0 + 512])[:, None]] = -1
        j = J.argmax(1); best += list(J[np.arange(len(j)), j]); bt += list(corpus.title.to_numpy()[j])
    return np.array(best), bt


def local_metrics(d):
    from transformers import AutoTokenizer
    from sentence_transformers import SentenceTransformer
    corpus = pd.read_parquet(PAPERS, columns=['paper_id', 'title'])
    f0 = pd.read_parquet(FALSE).query('k == 0')[['paper_id', 'donor_title']].rename(columns={'donor_title': 'false0'})
    d = d.merge(f0, on='paper_id', how='left').merge(pd.read_csv(PARA)[['paper_id', 'paraphrase']], on='paper_id', how='left')
    tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-32B'); ntok = lambda t: len(tok(t, add_special_tokens=False).input_ids)
    d['ntok'] = d.cand.map(ntok); d['ntok_true'] = d.title.map(ntok); d['rel_len'] = (d.ntok - d.ntok_true) / d.ntok_true
    d['len_tol'] = np.maximum(0.30 * d.ntok_true, 3); d['true_words'] = d.title.str.split().str.len()
    d['short_true'] = d.true_words <= SHORT_WORDS
    d['j2_true'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.cand)]
    d['pattern'] = [difflib.SequenceMatcher(None, skeleton(a), skeleton(b)).ratio() for a, b in zip(d.title, d.cand)]
    d['first_true'] = d.title.map(first_word); d['first_cand'] = d.cand.map(first_word)
    st = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cpu')
    E = np.load(V1 / 'corpus_mpnet.npy'); assert len(E) == len(corpus)
    Ec = emb(st, d.cand); Et = emb(st, d.title); Ef = emb(st, d.false0.fillna('')); Ep = emb(st, d.paraphrase.fillna(''))
    d['cos_true'] = (Ec * Et).sum(1); d['cos_false0'] = (Et * Ef).sum(1); d['cos_para'] = (Et * Ep).sum(1)
    pid = corpus.paper_id.to_numpy(); rk, nnc, nnt = [], [], []
    for i0 in range(0, len(d), 1024):
        S = Ec[i0:i0 + 1024] @ E.T; own = pid[None, :] == d.paper_id.to_numpy()[i0:i0 + 1024, None]
        rk += [int((S[i] > S[i][own[i]].max()).sum() + 1) for i in range(len(S))]
        So = np.where(own, -9, S); j = So.argmax(1); nnc += list(So[np.arange(len(j)), j]); nnt += list(corpus.title.to_numpy()[j])
    d['rank_true'] = rk; d['nn_cos'] = nnc; d['nn_cos_title'] = nnt
    normset = {norm(t) for t in corpus.title}; d['exact_corpus'] = [norm(c) in normset for c in d.cand]
    d['nn_j2'], d['nn_j2_title'] = corpus_overlap(d.cand.tolist(), d.paper_id.tolist(), corpus)
    return d


def apply_local(d):
    upper = np.minimum(0.85, d.cos_para.fillna(0.95) - 0.1)
    d['f_exact'] = d.exact_corpus; d['f_corpus_j2'] = d.nn_j2 >= 0.5; d['f_j2_true'] = d.j2_true >= 0.3
    d['f_len'] = (d.ntok - d.ntok_true).abs() > d.len_tol; d['f_cos_low'] = d.cos_true < 0.30; d['f_cos_high'] = d.cos_true >= upper
    d['f_first'] = d.first_true.str.lower() == d.first_cand.str.lower()
    cheap = ~d[['f_exact', 'f_corpus_j2', 'f_j2_true', 'f_len', 'f_cos_low', 'f_cos_high', 'f_first']].any(axis=1)
    if 'nli_fwd' not in d or d.loc[cheap, 'nli_fwd'].isna().any():
        if 'nli_fwd' not in d: d['nli_fwd'] = np.nan; d['nli_bwd'] = np.nan
        m = cheap & d.nli_fwd.isna()
        if m.any():
            d.loc[m, 'nli_fwd'] = nli_probs(d.loc[m, 'title'].tolist(), d.loc[m, 'cand'].tolist())
            d.loc[m, 'nli_bwd'] = nli_probs(d.loc[m, 'cand'].tolist(), d.loc[m, 'title'].tolist())
    two = (d.nli_fwd >= 0.5) & (d.nli_bwd >= 0.5); one = (np.maximum(d.nli_fwd, d.nli_bwd) > 0.9) & (d.cos_true >= COS_ONEWAY)
    d['f_nli'] = (two | one).fillna(False).astype(bool)
    d['local_ok'] = cheap & ~d.f_nli
    return d


def apply_ext(d, out):
    cr = Crossref(out / 'crossref_cache.jsonl')
    for c in ['ext_title', 'ext_j2', 'ext_equal', 'ext_ok', 'ext_rows', 'ext_thr', 'f_ext', 'f_ext_err']:
        d[c] = np.nan if c not in ('ext_title',) else ''
    d = d.astype({'f_ext': object, 'f_ext_err': object, 'ext_equal': object, 'ext_ok': object})
    t0 = time.time()
    for p, g in d[d.local_ok].sort_values('cos_true', ascending=False).groupby('paper_id', sort=False):
        for i, r in g.iterrows():
            e = ext_eval(cr, r.cand, bool(r.short_true))
            for k, v in e.items(): d.at[i, k] = v
            if not (e['f_ext'] or e['f_ext_err']): break
    print(f'Crossref: {cr.n_query} new requests, {time.time() - t0:.0f}s', flush=True)
    queried = d.ext_ok.notna()
    d['auto_ok'] = d.local_ok & queried & (d.f_ext == False) & (d.f_ext_err == False)  # noqa: E712
    fl = d[[f'f_{f}' for f in FAILS]].fillna(False).astype(bool)
    d['n_fail'] = fl.sum(1); d['fails'] = fl.apply(lambda r: ','.join(c[2:] for c in fl.columns if r[c]), axis=1)
    d['ext_queried'] = queried; d['pattern_flag'] = d.pattern >= 0.8
    return d


def check_round(out, rnd):
    s = load_sample()
    cand = [json.loads(l) for l in (out / f'candidates_r{rnd}.jsonl').open()]
    rows = [dict(paper_id=c['paper_id'], round=rnd, k=k, cand=t) for c in cand for k, t in enumerate(c['cands'])]
    if not rows: d = pd.DataFrame(columns=['paper_id', 'auto_ok']); print(f'round {rnd}: no candidates')
    else:
        d = pd.DataFrame(rows).merge(s[['paper_id', 'title', 'field', 'year', 'group', 's11_bin', 'citations']], on='paper_id')
        print(f'round {rnd}: {d.paper_id.nunique()} papers, {len(d)} candidates', flush=True); t0 = time.time()
        d = apply_local(local_metrics(d)); print(f'local filters {time.time() - t0:.0f}s; local ok {d.local_ok.mean():.1%}', flush=True)
        d = apply_ext(d, out)
        print(f'candidates ok {d.auto_ok.mean():.1%}; fail counts '
              f'{d[[f"f_{f}" for f in FAILS]].fillna(False).astype(bool).sum().to_dict()}', flush=True)
    d.to_csv(out / f'checked_r{rnd}.csv', index=False)
    allc = pd.concat([pd.read_csv(out / f'checked_r{q}.csv') for q in range(rnd + 1) if (out / f'checked_r{q}.csv').exists()])
    n_ok = allc.groupby('paper_id').auto_ok.sum().astype(int)
    st = s[['paper_id']].copy(); st['n_ok'] = st.paper_id.map(n_ok).fillna(0).astype(int)
    st.to_csv(out / f'round{rnd}_status.csv', index=False)
    print(f'after round {rnd}: papers with >=1 ok {(st.n_ok > 0).sum()}/{len(st)}; need regeneration {(st.n_ok == 0).sum()}')


def final(out):
    s = load_sample()
    allc = pd.concat([pd.read_csv(f) for f in sorted(out.glob('checked_r*.csv')) if f.stat().st_size > 30], ignore_index=True)
    allc.to_csv(out / 'all_checked.csv', index=False)
    ok = allc[allc.auto_ok.astype(bool)]
    sel = ok.sort_values(['paper_id', 'cos_true'], ascending=[True, False]).groupby('paper_id').head(1)
    agg = allc.groupby('paper_id').agg(n_cand=('cand', 'size'), n_local_ok=('local_ok', 'sum'), rounds=('round', 'max')).reset_index()
    sel = sel.merge(agg, on='paper_id'); sel.to_csv(out / 'selected.csv', index=False)
    ex = s[~s.paper_id.isin(sel.paper_id)][['paper_id', 'title', 'field', 'year', 'group', 's11_bin']]
    fc = allc[allc.paper_id.isin(ex.paper_id)].copy()
    fc[[f'f_{f}' for f in FAILS]] = fc[[f'f_{f}' for f in FAILS]].fillna(False).astype(bool)
    ex = ex.merge(fc.groupby('paper_id')[[f'f_{f}' for f in FAILS]].sum().reset_index(), on='paper_id', how='left')
    ex.to_csv(out / 'excluded.csv', index=False)
    tab = s.assign(selected=s.paper_id.isin(sel.paper_id)).groupby(['s11_bin', 'group']).agg(n=('paper_id', 'size'), selected=('selected', 'sum'))
    tab['excluded'] = tab.n - tab.selected
    order = sorted(s.s11_bin.unique(), key=lambda b: int(b.split('-')[0]))
    tab = tab.reset_index().assign(_o=lambda x: x.s11_bin.map(order.index)).sort_values(['_o', 'group']).drop(columns='_o')
    tab.to_csv(out / 'exclusions_by_bin_group.csv', index=False)
    print(f'selected {len(sel)}/{len(s)}; excluded {len(ex)}; by group {ex.group.value_counts().to_dict()}; selected by round {sel["round"].value_counts().to_dict()}')
    print(tab.to_string(index=False))
    print('candidate fail counts (all rounds):', allc[[f'f_{f}' for f in FAILS]].fillna(False).astype(bool).sum().to_dict())
    print(sel[['cos_true', 'cos_false0', 'cos_para', 'j2_true', 'rel_len', 'nn_j2', 'ext_j2', 'pattern', 'rank_true']].describe().round(3).to_string())


def refilter_v2(out):
    """Quick check: v3 local rules + v3 Crossref rule on the v2 candidates (no new generation)."""
    v2 = pd.read_csv(V1 / 'v2/all_checked.csv'); v2sel = pd.read_csv(V1 / 'v2/selected.csv')
    d = v2.copy(); d['true_words'] = d.title.str.split().str.len(); d['short_true'] = d.true_words <= SHORT_WORDS
    keep = [c for c in d.columns if not c.startswith('f_') and not c.startswith('ext_') and c not in ('auto_ok', 'n_fail', 'fails', 'pattern_flag')]
    d = apply_local(d[keep].copy()); d = apply_ext(d, out)
    sel = d[d.auto_ok].sort_values(['paper_id', 'cos_true'], ascending=[True, False]).groupby('paper_id').head(1)
    m = v2sel[['paper_id', 'cand']].merge(sel[['paper_id', 'cand']], on='paper_id', how='outer', suffixes=('_v2', '_v3'))
    m['same'] = m.cand_v2 == m.cand_v3
    d.to_csv(out / 'refilter_v2_checked.csv', index=False); m.to_csv(out / 'refilter_v2_selected_compare.csv', index=False)
    print(f'v2 candidates {len(d)}: v3 local ok {d.local_ok.sum()}, auto ok (queried) {d.auto_ok.sum()}')
    print(f'papers selected v2 {v2sel.paper_id.nunique()} -> v3 rules {sel.paper_id.nunique()}; same title {int(m.same.sum())}; changed {int((~m.same & m.cand_v2.notna() & m.cand_v3.notna()).sum())}; lost {int(m.cand_v3.isna().sum())}')
    print('short true titles:', d[d.short_true].paper_id.nunique(), 'papers;', 'new nli rejections (one-way, 0.70<=cos<0.75):',
          int((((np.maximum(d.nli_fwd, d.nli_bwd) > 0.9) & (d.cos_true >= 0.70) & (d.cos_true < 0.75))).sum()))
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90)
    print(m[~m.same].merge(d[['paper_id', 'title']].drop_duplicates(), on='paper_id').to_string())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--round', type=int); ap.add_argument('--final', action='store_true')
    ap.add_argument('--refilter-v2', action='store_true'); ap.add_argument('--out', default=str(V1 / 'v3'))
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.refilter_v2: refilter_v2(out)
    elif a.final: final(out)
    else: check_round(out, a.round)
