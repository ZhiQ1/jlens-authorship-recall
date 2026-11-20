#!/usr/bin/env python3
"""H2 fictitious titles, checks v2 (CPU; user-approved filter changes 2026-11-18). Exploratory quality sample.

  python h2fict_check_v2.py --round R [--out OUT]   -> OUT/checked_r{R}.csv, OUT/round{R}_status.csv
  python h2fict_check_v2.py --final  [--out OUT]    -> OUT/selected.csv, OUT/excluded.csv, OUT/all_checked.csv

Filters (a candidate passes only if all hold):
  exact     : normalized (lowercase alnum) equality with any of the 9,108 cohort titles
  corpus_j2 : jaccard2 with any other cohort title >= 0.5
  j2_true   : jaccard2 with the true title >= 0.3
  len       : |ntok - ntok_true| > max(0.30 * ntok_true, 3)               (Qwen3 tokens)
  nli       : two-way entailment (p_fwd >= 0.5 and p_bwd >= 0.5), or max(p_fwd, p_bwd) > 0.9 with cos_true >= 0.75
  cos_low   : cos_true < 0.30            cos_high : cos_true >= min(0.85, cos_para - 0.1)   (all-mpnet-base-v2)
  first     : same first word as the true title (articles a/an/the skipped)
  ext       : Crossref top-3 (query.bibliographic): any hit with normalized equality or jaccard2 >= 0.5
  ext_err   : Crossref did not answer after 4 tries (conservative: counts as a failure)
Flag only (not a filter): pattern = similarity of the function-word skeletons (content words -> X), >= 0.8 flagged.
Crossref: every candidate, 1 request/s, generic User-Agent, cached in OUT/crossref_cache.jsonl.
Selection (--final): highest cos_true among passing candidates of all rounds. Exclusion rule: a paper with no passing
candidate after round 2 is excluded from the H2 set (listed in excluded.csv with its failure counts).
"""
import argparse, difflib, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path.home() / 'jlens_work/13_stage13')); sys.path.insert(0, str(Path(__file__).parent))
from stage13_para_nli import words2, jac   # noqa: E402  (X3 jaccard2)
from h2fict_gen_v2 import first_word       # noqa: E402

ROOT = Path('/scratch/zhang.zhiqi2/jlens'); V1 = ROOT / '391_groups/h2_fictitious'
PAPERS = ROOT / '351_stage10/cohort/papers.parquet'
FALSE = ROOT / '351_stage10/cohort/conditions/false_titles.parquet'
PARA = ROOT / '381_stage13/summary_x3/para_nli.csv'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())
FAILS = ['exact', 'corpus_j2', 'j2_true', 'len', 'nli', 'cos_low', 'cos_high', 'first', 'ext', 'ext_err']


def skeleton(s):
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    toks = re.findall(r"[a-z0-9]+|[:;,?\-–—()]", str(s).lower())
    return [t if (t in ENGLISH_STOP_WORDS or not t[0].isalnum()) else 'X' for t in toks]


def emb(model, texts):
    return model.encode(list(texts), batch_size=64, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)


def nli_probs(prem, hyp):
    import torch, transformers
    M = 'cross-encoder/nli-deberta-v3-large'
    tok = transformers.AutoTokenizer.from_pretrained(M); m = transformers.AutoModelForSequenceClassification.from_pretrained(M).eval()
    ie = {v.lower(): k for k, v in m.config.id2label.items()}['entailment']; out = []
    with torch.inference_mode():
        for i in range(0, len(prem), 16):
            e = tok(prem[i:i + 16], hyp[i:i + 16], padding=True, truncation=True, max_length=256, return_tensors='pt')
            out.append(torch.softmax(m(**e).logits.float(), -1)[:, ie].numpy())
    return np.concatenate(out)


class Crossref:
    def __init__(self, path):
        self.path = path; self.c = {}; self.last = 0.0
        if path.exists():
            for l in path.open():
                x = json.loads(l); self.c[x['key']] = x
        self.f = path.open('a')

    def get(self, title):
        key = norm(title)
        if key in self.c and self.c[key].get('ok'): return self.c[key]
        url = 'https://api.crossref.org/works?rows=3&select=title&query.bibliographic=' + urllib.parse.quote(title)
        rec = dict(key=key, ok=False, hits=[])
        for attempt in range(4):
            wait = 1.0 - (time.time() - self.last)
            if wait > 0: time.sleep(wait)
            self.last = time.time()
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'title-novelty-check/0.1'})
                items = json.load(urllib.request.urlopen(req, timeout=30))['message']['items']
                rec = dict(key=key, ok=True, hits=[it['title'][0] for it in items if it.get('title')]); break
            except Exception as e:
                rec['err'] = f'{type(e).__name__}: {e}'[:200]; time.sleep(5 * (attempt + 1))
        self.c[key] = rec; self.f.write(json.dumps(rec) + '\n'); self.f.flush()
        return rec


def check_round(out, rnd):
    from transformers import AutoTokenizer
    from sentence_transformers import SentenceTransformer
    s = pd.read_parquet(V1 / 'sample_papers.parquet')
    corpus = pd.read_parquet(PAPERS, columns=['paper_id', 'title'])
    cand = [json.loads(l) for l in (out / f'candidates_r{rnd}.jsonl').open()]
    rows = [dict(paper_id=c['paper_id'], round=rnd, k=k, cand=t) for c in cand for k, t in enumerate(c['cands'])]
    if not rows:
        print(f'round {rnd}: no candidates'); d = pd.DataFrame(columns=['paper_id', 'auto_ok'])
    else:
        d = pd.DataFrame(rows).merge(s[['paper_id', 'title', 'field', 'year', 'group', 's11_bin', 'citations']], on='paper_id')
        f0 = pd.read_parquet(FALSE).query('k == 0')[['paper_id', 'donor_title']].rename(columns={'donor_title': 'false0'})
        d = d.merge(f0, on='paper_id', how='left').merge(pd.read_csv(PARA)[['paper_id', 'paraphrase']], on='paper_id', how='left')
        print(f'round {rnd}: {d.paper_id.nunique()} papers, {len(d)} candidates', flush=True)
        tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-32B'); ntok = lambda t: len(tok(t, add_special_tokens=False).input_ids)
        d['ntok'] = d.cand.map(ntok); d['ntok_true'] = d.title.map(ntok); d['rel_len'] = (d.ntok - d.ntok_true) / d.ntok_true
        d['len_tol'] = np.maximum(0.30 * d.ntok_true, 3)
        d['j2_true'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.cand)]
        d['pattern'] = [difflib.SequenceMatcher(None, skeleton(a), skeleton(b)).ratio() for a, b in zip(d.title, d.cand)]
        d['first_true'] = d.title.map(first_word); d['first_cand'] = d.cand.map(first_word)
        st = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cpu')
        E = np.load(V1 / 'corpus_mpnet.npy'); assert len(E) == len(corpus)
        Ec = emb(st, d.cand); Et = emb(st, d.title); Ef = emb(st, d.false0); Ep = emb(st, d.paraphrase.fillna(''))
        d['cos_true'] = (Ec * Et).sum(1); d['cos_false0'] = (Et * Ef).sum(1); d['cos_para'] = (Et * Ep).sum(1)
        S = Ec @ E.T; pid = corpus.paper_id.to_numpy(); own = pid[None, :] == d.paper_id.to_numpy()[:, None]
        d['rank_true'] = [(S[i] > S[i][own[i]].max()).sum() + 1 for i in range(len(d))]
        So = np.where(own, -9, S); j = So.argmax(1)
        d['nn_cos_title'] = corpus.title.to_numpy()[j]; d['nn_cos'] = So[np.arange(len(d)), j]
        W = [words2(t) for t in corpus.title]; normset = {norm(t) for t in corpus.title}
        d['exact_corpus'] = [norm(c) in normset for c in d.cand]
        nnj, nnt = [], []
        for c, p in zip(d.cand, d.paper_id):
            wc = words2(c); best, bi = -1, -1
            for i, w in enumerate(W):
                if pid[i] == p: continue
                v = len(wc & w) / max(1, len(wc | w))
                if v > best: best, bi = v, i
            nnj.append(best); nnt.append(corpus.title[bi])
        d['nn_j2'] = nnj; d['nn_j2_title'] = nnt
        d['nli_fwd'] = nli_probs(d.title.tolist(), d.cand.tolist()); d['nli_bwd'] = nli_probs(d.cand.tolist(), d.title.tolist())
        print('local metrics done; Crossref ...', flush=True)
        cr = Crossref(out / 'crossref_cache.jsonl'); et, ej, eq, eok = [], [], [], []
        t0 = time.time()
        for c in d.cand:
            r = cr.get(c); hits = r['hits']
            if hits:
                b = max(hits, key=lambda h: jac(words2(h), words2(c))); et.append(b); ej.append(jac(words2(b), words2(c)))
            else: et.append(''); ej.append(0.0)
            eq.append(any(norm(h) == norm(c) for h in hits)); eok.append(r['ok'])
        print(f'Crossref {len(d)} queries/cached in {time.time() - t0:.0f}s', flush=True)
        d['ext_title'] = et; d['ext_j2'] = ej; d['ext_equal'] = eq; d['ext_ok'] = eok
        upper = np.minimum(0.85, d.cos_para.fillna(0.95) - 0.1)
        fl = pd.DataFrame({'f_exact': d.exact_corpus, 'f_corpus_j2': d.nn_j2 >= 0.5, 'f_j2_true': d.j2_true >= 0.3,
                           'f_len': (d.ntok - d.ntok_true).abs() > d.len_tol,
                           'f_nli': ((d.nli_fwd >= 0.5) & (d.nli_bwd >= 0.5)) | ((np.maximum(d.nli_fwd, d.nli_bwd) > 0.9) & (d.cos_true >= 0.75)),
                           'f_cos_low': d.cos_true < 0.30, 'f_cos_high': d.cos_true >= upper,
                           'f_first': d.first_true.str.lower() == d.first_cand.str.lower(),
                           'f_ext': d.ext_equal | (d.ext_j2 >= 0.5), 'f_ext_err': ~d.ext_ok.astype(bool)})
        d = pd.concat([d, fl], axis=1); d['n_fail'] = fl.sum(1); d['auto_ok'] = d.n_fail == 0
        d['fails'] = fl.apply(lambda r: ','.join(c[2:] for c in fl.columns if r[c]), axis=1)
        d['pattern_flag'] = d.pattern >= 0.8
        print(f'candidates ok {d.auto_ok.mean():.1%}; fail counts {fl.sum().to_dict()}', flush=True)
    d.to_csv(out / f'checked_r{rnd}.csv', index=False)
    # cumulative status over rounds 0..rnd
    allc = pd.concat([pd.read_csv(out / f'checked_r{q}.csv') for q in range(rnd + 1) if (out / f'checked_r{q}.csv').exists()])
    st = s[['paper_id']].merge(allc.groupby('paper_id').auto_ok.sum().rename('n_ok').reset_index(), on='paper_id', how='left').fillna({'n_ok': 0})
    st['n_ok'] = st.n_ok.astype(int); st.to_csv(out / f'round{rnd}_status.csv', index=False)
    print(f'after round {rnd}: papers with >=1 ok {(st.n_ok > 0).sum()}/{len(st)}; need regeneration {(st.n_ok == 0).sum()}')


def final(out):
    s = pd.read_parquet(V1 / 'sample_papers.parquet')
    allc = pd.concat([pd.read_csv(f) for f in sorted(out.glob('checked_r*.csv')) if f.stat().st_size > 30], ignore_index=True)
    allc.to_csv(out / 'all_checked.csv', index=False)
    ok = allc[allc.auto_ok.astype(bool)]
    sel = ok.sort_values(['paper_id', 'cos_true'], ascending=[True, False]).groupby('paper_id').head(1)
    sel = sel.merge(allc.groupby('paper_id').agg(n_cand=('cand', 'size'), n_cand_ok=('auto_ok', 'sum'), rounds=('round', 'max')).reset_index(), on='paper_id')
    sel.to_csv(out / 'selected.csv', index=False)
    ex = s[~s.paper_id.isin(sel.paper_id)][['paper_id', 'title', 'field', 'year', 'group', 's11_bin']]
    fc = allc[allc.paper_id.isin(ex.paper_id)].groupby('paper_id')[[f'f_{f}' for f in FAILS]].sum().reset_index()
    ex = ex.merge(fc, on='paper_id', how='left'); ex.to_csv(out / 'excluded.csv', index=False)
    print(f'selected {len(sel)}/{len(s)}; excluded {len(ex)}; selected by round {sel["round"].value_counts().to_dict()}')
    print('candidate fail counts (all rounds):', allc[[f'f_{f}' for f in FAILS]].sum().to_dict())
    print(sel[['cos_true', 'cos_false0', 'cos_para', 'j2_true', 'rel_len', 'nn_j2', 'ext_j2', 'pattern', 'rank_true']].describe().round(3).to_string())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--round', type=int); ap.add_argument('--final', action='store_true')
    ap.add_argument('--out', default=str(V1 / 'v2')); a = ap.parse_args(); out = Path(a.out)
    final(out) if a.final else check_round(out, a.round)
