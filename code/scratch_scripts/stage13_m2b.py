"""Stage 13 M2b (CPU): is "year / citations from the title" lexical or knowledge?
(a) word baseline: TF-IDF of the title words (uni+bigrams) -> ridge, same 5 folds by paper as M2;
(b) residual probe: the residual probe's prediction compared with the word baseline on the same papers;
(c) by group: probe accuracy separately for target and control papers (recognised vs not), within citation bin
    (absolute error of the year, squared error of log citations); knowledge predicts target > control after words.
Last title token only (the year is not yet in context there). True-title runs.
"""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'; ROOT = BASE / '381_stage13'
sp = importlib.util.spec_from_file_location('m', Path.home() / 'jlens_work/13_stage13/stage13_cpu.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))]
Xt = np.concatenate([z['resid_title'] for z in zs]); pid = np.concatenate([z['resid_paper_id'] for z in zs]); pl = list(zs[0]['probe_layers'])
P = papers.loc[pid]; folds = np.random.default_rng(13).integers(0, 5, len(pid)) if m.SPLIT == 'paper' else m.group_folds(pid)[0]
y = dict(year=pd.to_numeric(P.year, errors='coerce').to_numpy(float), cit=np.log10(pd.to_numeric(P.citations, errors='coerce').fillna(0).to_numpy(float) + 1))
ok = ~np.isnan(y['year']); grp = P.group_tight.to_numpy(); bins = P.citation_bin.to_numpy()
rows = []
def evaluate(name, pred, layer):
    for t in ('year', 'cit'):
        yy, pp = y[t][ok], pred[t][ok]; r2 = 1 - ((yy - pp) ** 2).sum() / ((yy - yy.mean()) ** 2).sum()
        e = np.abs(yy - pp); row = dict(model=name, layer=layer, target=t, r2=r2, mae_all=e.mean())
        g = grp[ok]; b = bins[ok]
        # within-bin target - control difference of the absolute error (negative = better for target)
        cells = []
        for bb in np.unique(b):
            i = b == bb; a, c = e[i & (g == 'target')], e[i & (g == 'control')]
            if len(a) >= 30 and len(c) >= 30: cells.append((len(a) * len(c) / (len(a) + len(c)), a.mean() - c.mean()))
        w = np.array([x[0] for x in cells]); row['abs_err_target_minus_control'] = float((w * np.array([x[1] for x in cells])).sum() / w.sum())
        rows.append(row)
# (a) words
titles = P.title.astype(str).to_numpy(); pw = {t: np.zeros(len(pid)) for t in y}
for k in range(5):
    tr, te = folds != k, folds == k
    v = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True); A = v.fit_transform(titles[tr]); Bm = v.transform(titles[te])
    for t in y:
        tt = tr & (~np.isnan(y[t]) if t == 'year' else True)
        mdl = Ridge(alpha=1.0).fit(v.transform(titles[tt]), y[t][tt]); pw[t][te] = mdl.predict(Bm)
evaluate('title words (TF-IDF)', pw, -1)
# (b) residual probes per layer, alone and on top of words (residual target = y - word prediction)
for li, l in enumerate(pl):
    X = Xt[:, li].astype(np.float32); pr, prw = {}, {}
    for t in y:
        Y = np.nan_to_num(y[t], nan=np.nanmean(y[t]))[:, None]
        pr[t] = m.ridge_cv(X, Y, folds)[0][:, 0]
        prw[t] = pw[t] + m.ridge_cv(X, (Y[:, 0] - pw[t])[:, None], folds)[0][:, 0]
    evaluate('residual probe', pr, int(l)); evaluate('words + residual probe', prw, int(l)); print('layer', l, flush=True)
d = pd.DataFrame(rows); d.to_csv(m.S / 'M2b_words_vs_probe.csv', index=False)
print(d.round(3).to_string(index=False))
