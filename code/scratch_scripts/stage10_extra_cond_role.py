"""Follow-up to stage10_extra.py X1_cond (2026-10-26): the first-word conditional split by the first token's role
(initial_first vs given_first), true title, readouts final@63, logit@62, jlens_public@62; clustered bootstrap by paper."""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd
DIR = Path(__file__).parent
sp = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s10)
ROOT = s10.ROOT; rng = np.random.default_rng(3513); B = 2000
m, lenses = s10.verify(ROOT)
toks = pd.read_parquet(ROOT / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'word_index', 'role'])
papers = pd.read_parquet(ROOT / 'cohort/papers.parquet', columns=['paper_id', 'group_tight'])
raw = s10.load_raw(ROOT, m, lenses, require_complete=True, cond='true')
pidx = {p: i for i, p in enumerate(papers.paper_id)}; P = len(papers)
cid, cinv = np.unique(toks.context_id.to_numpy(), return_inverse=True); NC = len(cid)
cpaper = np.zeros(NC, int); cpaper[cinv] = toks.paper_id.map(pidx).to_numpy()
frole = np.empty(NC, object); f0 = toks.token_index.to_numpy() == 0; frole[cinv[f0]] = toks.role.to_numpy()[f0]
fw = toks.word_index.to_numpy() == 0
W = rng.multinomial(P, np.full(P, 1 / P), size=B).astype(np.float32)[:, cpaper]
rows = []
for r, l in [('final', 63), ('logit', 62), ('jlens_public', 62)]:
    rk = np.zeros(len(toks), np.int64); s = raw[(raw.readout == r) & (raw.layer == l)]; rk[s.row_id.to_numpy()] = s['rank'].to_numpy()
    nlr = -np.log10(rk.astype(float))
    ftop = np.ones(NC, bool); np.logical_and.at(ftop, cinv[fw], rk[fw] <= 10)
    nl = np.bincount(cinv[~fw], minlength=NC); later = np.bincount(cinv[~fw], weights=nlr[~fw], minlength=NC) / np.maximum(nl, 1)
    for role in ['initial_first', 'given_first']:
        ok = (nl > 0) & (frole == role)
        yes, no = ok & ftop, ok & ~ftop
        my = (W[:, yes] * later[yes]).sum(1) / W[:, yes].sum(1); mn = (W[:, no] * later[no]).sum(1) / W[:, no].sum(1)
        rows.append(dict(readout=r, layer=l, first_role=role, n_contexts=int(ok.sum()), share_first_word_top10=ftop[ok].mean(),
                         later_if_top10=later[yes].mean(), later_if_not=later[no].mean(), diff=later[yes].mean() - later[no].mean(),
                         lo=np.percentile(my - mn, 2.5), hi=np.percentile(my - mn, 97.5), n_top10=int(yes.sum()), n_not=int(no.sum())))
out = pd.DataFrame(rows); out.to_csv(ROOT / 'summary_extra/X1_cond_by_first_role.csv', index=False); print(out.round(3).to_string())
