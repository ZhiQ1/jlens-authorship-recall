#!/usr/bin/env python3
"""H2 fictitious titles: automatic checks + selection (CPU). Exploratory quality sample.

Input : OUT/sample_papers.parquet, OUT/candidates.jsonl (h2fict_gen.py)
Output: OUT/candidates_checked.csv (every candidate, all metrics), OUT/selected.csv (one title per paper),
        OUT/corpus_mpnet.npy (cache of the 9,108 cohort title embeddings)

Metrics per candidate (vs the paper's true title T, the cohort corpus of 9,108 titles, and references):
  ntok / ntok_true / rel_len : Qwen3 tokens (same tokenizer as the Stage 10 prompts)
  j2_true                    : jaccard2 (Stage 13 X3 definition: stop words removed, light stemming)
  cos_true                   : all-mpnet-base-v2 cosine with T; references cos(T, paraphrase X3) and cos(T, false_0)
  nli_fwd / nli_bwd          : p(entailment) T->cand and cand->T (cross-encoder/nli-deberta-v3-large)
  exact_corpus               : normalized (lowercase alnum) exact match with any cohort title (incl. T)
  nn_j2_title / nn_j2        : most-overlapping OTHER cohort title by jaccard2
  nn_cos_title / nn_cos      : most similar OTHER cohort title by mpnet cosine
  rank_true                  : rank of T among all 9,108 cohort titles by mpnet cosine to the candidate (1 = T nearest)
  ext_title / ext_j2         : best Crossref bibliographic match for the SELECTED title (external existence check)
Filters (auto_ok): not exact; nn_j2 < 0.5; j2_true < 0.3; |rel_len| <= 0.30; nli_fwd < 0.5 and nli_bwd < 0.5;
  0.40 <= cos_true < min(0.90, cos(T, paraphrase)).  Selection: highest cos_true among auto_ok candidates
  (closest meaning that is not a paraphrase); if none pass, the candidate with fewest failed filters (flagged).
"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path.home() / 'jlens_work/13_stage13'))
from stage13_para_nli import words2, jac   # noqa: E402  (same jaccard2 as X3)

ROOT = Path('/scratch/zhang.zhiqi2/jlens')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / '391_groups/h2_fictitious'
NO_EXT = '--no-ext' in sys.argv
PAPERS = ROOT / '351_stage10/cohort/papers.parquet'
FALSE = ROOT / '351_stage10/cohort/conditions/false_titles.parquet'
PARA = ROOT / '381_stage13/summary_x3/para_nli.csv'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())


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


def crossref(title):
    url = 'https://api.crossref.org/works?rows=3&select=title&query.bibliographic=' + urllib.parse.quote(title)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'title-novelty-check/0.1'})
        items = json.load(urllib.request.urlopen(req, timeout=20))['message']['items']
        ts = [it['title'][0] for it in items if it.get('title')]
        if not ts: return '', 0.0
        best = max(ts, key=lambda t: jac(words2(t), words2(title)))
        return best, jac(words2(best), words2(title))
    except Exception as e:
        return f'ERR {type(e).__name__}', float('nan')


def main():
    from transformers import AutoTokenizer
    from sentence_transformers import SentenceTransformer
    s = pd.read_parquet(OUT / 'sample_papers.parquet')
    corpus = pd.read_parquet(PAPERS, columns=['paper_id', 'title', 'field'])
    cand = [json.loads(l) for l in (OUT / 'candidates.jsonl').open()]
    rows = [dict(paper_id=c['paper_id'], k=k, cand=t) for c in cand for k, t in enumerate(c['cands'])]
    d = pd.DataFrame(rows).merge(s[['paper_id', 'title', 'field', 'year', 'group', 's11_bin', 'citations']], on='paper_id')
    f0 = pd.read_parquet(FALSE).query('k == 0')[['paper_id', 'donor_title']].rename(columns={'donor_title': 'false0'})
    para = pd.read_csv(PARA)[['paper_id', 'paraphrase']]
    d = d.merge(f0, on='paper_id', how='left').merge(para, on='paper_id', how='left')
    print(f'{d.paper_id.nunique()} papers, {len(d)} candidates', flush=True)

    tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
    ntok = lambda t: len(tok(t, add_special_tokens=False).input_ids)
    d['ntok'] = d.cand.map(ntok); d['ntok_true'] = d.title.map(ntok); d['ntok_false0'] = d.false0.map(ntok)
    d['rel_len'] = (d.ntok - d.ntok_true) / d.ntok_true
    d['j2_true'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.cand)]
    d['j2_false0'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.false0)]
    d['j2_para'] = [jac(words2(a), words2(b)) for a, b in zip(d.title, d.paraphrase.fillna(''))]

    st = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cpu')
    cache = OUT / 'corpus_mpnet.npy'
    if cache.exists(): E = np.load(cache)
    else: E = emb(st, corpus.title); np.save(cache, E)
    assert len(E) == len(corpus)
    Ec = emb(st, d.cand); Et = emb(st, d.title); Ef = emb(st, d.false0); Ep = emb(st, d.paraphrase.fillna(''))
    d['cos_true'] = (Ec * Et).sum(1); d['cos_false0'] = (Et * Ef).sum(1); d['cos_para'] = (Et * Ep).sum(1)
    S = Ec @ E.T
    pid = corpus.paper_id.to_numpy(); own = (pid[None, :] == d.paper_id.to_numpy()[:, None])
    d['rank_true'] = [(S[i] > S[i][own[i]].max()).sum() + 1 for i in range(len(d))]
    So = np.where(own, -9, S); j = So.argmax(1)
    d['nn_cos_title'] = corpus.title.to_numpy()[j]; d['nn_cos'] = So[np.arange(len(d)), j]
    W = [words2(t) for t in corpus.title]; normset = {norm(t): i for i, t in enumerate(corpus.title)}
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
    print('embeddings + overlap done', flush=True)
    d['nli_fwd'] = nli_probs(d.title.tolist(), d.cand.tolist()); d['nli_bwd'] = nli_probs(d.cand.tolist(), d.title.tolist())

    upper = np.minimum(0.90, d.cos_para.fillna(0.90))
    fl = pd.DataFrame({'f_exact': d.exact_corpus, 'f_corpus_j2': d.nn_j2 >= 0.5, 'f_j2_true': d.j2_true >= 0.3,
                       'f_len': d.rel_len.abs() > 0.30, 'f_nli': (d.nli_fwd >= 0.5) | (d.nli_bwd >= 0.5),
                       'f_cos_low': d.cos_true < 0.40, 'f_cos_high': d.cos_true >= upper, 'f_empty': d.cand.str.len() < 5})
    d = pd.concat([d, fl], axis=1); d['n_fail'] = fl.sum(1); d['auto_ok'] = d.n_fail == 0
    d['fails'] = fl.apply(lambda r: ','.join(c[2:] for c in fl.columns if r[c]), axis=1)
    d.to_csv(OUT / 'candidates_checked.csv', index=False)

    sel = (d.assign(_o=~d.auto_ok).sort_values(['paper_id', '_o', 'n_fail', 'cos_true'], ascending=[True, True, True, False])
             .groupby('paper_id').head(1).drop(columns='_o'))
    sel = sel.merge(d.groupby('paper_id').auto_ok.sum().rename('n_cand_ok'), on='paper_id')
    if not NO_EXT:
        ext = []
        for t in sel.cand:
            ext.append(crossref(t)); time.sleep(1.0)
        sel['ext_title'] = [e[0] for e in ext]; sel['ext_j2'] = [e[1] for e in ext]
    sel.to_csv(OUT / 'selected.csv', index=False)
    print(f'candidates auto_ok {d.auto_ok.mean():.2%}; papers with >=1 ok {(sel.n_cand_ok > 0).sum()}/{len(sel)}')
    print('fail counts (candidates):', fl.sum().to_dict())
    print(sel[['cos_true', 'cos_false0', 'cos_para', 'j2_true', 'j2_false0', 'rel_len', 'nn_j2', 'nn_cos', 'rank_true']].describe().round(3).to_string())


if __name__ == '__main__':
    main()
