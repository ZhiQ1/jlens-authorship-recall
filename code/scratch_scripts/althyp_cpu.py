"""Exploratory (post hoc) CPU checks for alternative hypotheses, 2026-11-22. Stored data only.
a) wrong names: nearest-title-paper authors (mpnet), field top-50 surname share; target vs control; permuted baselines
b) MC distractors: target share by distractor-answer title similarity (mpnet) and by distractor in-cohort status
d) lens trajectory: rise-then-fall share of surname-first nlr in L40-L62 (logit, jlens_public), target vs control
Usage: althyp_cpu.py [--tiny]"""
import sys, json, re, os, numpy as np, pandas as pd
from pathlib import Path
TINY = '--tiny' in sys.argv
J = Path('/scratch/zhang.zhiqi2/jlens'); OUT = J / ('391_groups/summary_althyp_20261122' + ('_tiny' if TINY else '')); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(30); NB = 200 if TINY else 2000
P = pd.read_parquet(J / '351_stage10/cohort/papers.parquet', columns=['paper_id', 'title', 'authors', 'field', 'citation_bin', 'group_tight', 'year'])
sys.path.insert(0, str(Path.home() / 'jlens_work/13_stage13'))
import importlib.util
sp = importlib.util.spec_from_file_location('c13', Path.home() / 'jlens_work/13_stage13/stage13_cpu.py'); c13 = importlib.util.module_from_spec(sp); sp.loader.exec_module(c13)
_, team = c13.group_folds(P.paper_id.to_numpy()); P['team'] = team
if TINY: P = P.sample(800, random_state=1).reset_index(drop=True)
def key(n):
    w = [x for x in re.split(r'[\s.]+', str(n).lower()) if x]
    return (w[-1] + '|' + w[0][0]) if len(w) >= 2 else None
def sur(n):
    w = [x for x in re.split(r'[\s.]+', str(n).lower()) if x]; return w[-1] if w else None
P['keys'] = P.authors.map(lambda a: {k for k in (key(x) for x in str(a).split(';')) if k})
P['surs'] = P.authors.map(lambda a: {s for s in (sur(x) for x in str(a).split(';')) if s})
idx = {p: i for i, p in enumerate(P.paper_id)}
# --- embeddings
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cpu')
E = m.encode(P.title.tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
S = E @ E.T; np.fill_diagonal(S, -1)
same_team = P.team.to_numpy()[:, None] == P.team.to_numpy()[None, :]; S[same_team] = -1
nn1 = S.argmax(1); nn5 = np.argsort(-S, 1)[:, :5]
def boot_diff(vals, grp, teams):
    """team bootstrap of mean(target) - mean(control); vals per name row"""
    df = pd.DataFrame(dict(v=vals, g=grp, t=teams)).dropna()
    tu = df.t.unique(); ti = {t: i for i, t in enumerate(tu)}; c = df.t.map(ti).to_numpy()
    W = rng.multinomial(len(tu), np.full(len(tu), 1 / len(tu)), size=NB)[:, c].astype(float)
    out = {}
    for g in ('target', 'control'):
        mk = (df.g == g).to_numpy(); v = df.v.to_numpy()[mk]; w = W[:, mk]
        out[g] = (v.mean(), (w @ v) / w.sum(1))
    d = out['target'][1] - out['control'][1]
    return dict(target=out['target'][0], control=out['control'][0], diff=out['target'][0] - out['control'][0],
                lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                t_lo=float(np.percentile(out['target'][1], 2.5)), t_hi=float(np.percentile(out['target'][1], 97.5)))
res = {}
# --- a) wrong names
F = pd.read_parquet(J / '391_groups/summary_fabricated_20261114/fabricated_names.parquet')
F = F[F.paper_id.isin(idx) & F.group_tight.isin(['target', 'control'])].copy()
F['k'] = F.name.map(key); F['s'] = F.name.map(sur); F = F[F.k.notna()]
ii = F.paper_id.map(idx).to_numpy()
F['nn1_author'] = [k in P['keys'].iat[nn1[i]] for k, i in zip(F.k, ii)]
F['nn5_author'] = [any(k in P['keys'].iat[j] for j in nn5[i]) for k, i in zip(F.k, ii)]
# field top-50 surnames (cohort authors, leave-own-paper-in is fine: true authors are excluded from fabricated names by construction)
top = {}
for f, g in P.groupby('field'):
    c = pd.Series([s for ss in g.surs for s in ss]).value_counts(); top[f] = set(c.index[:50])
F['field_top50'] = [s in top.get(f, set()) for s, f in zip(F.s, F.field)]
# permuted baseline: shuffle names across papers within field
perm = F.copy(); perm['k'] = perm.groupby('field').k.transform(lambda x: x.sample(frac=1, random_state=30).to_numpy())
perm['s'] = perm.groupby('field').s.transform(lambda x: x.sample(frac=1, random_state=31).to_numpy())
pii = perm.paper_id.map(idx).to_numpy()
perm['nn1_author'] = [k in P['keys'].iat[nn1[i]] for k, i in zip(perm.k, pii)]
perm['nn5_author'] = [any(k in P['keys'].iat[j] for j in nn5[i]) for k, i in zip(perm.k, pii)]
tm = P.set_index('paper_id').team
rows = []
for col in ('nn1_author', 'nn5_author', 'field_top50'):
    b = boot_diff(F[col].astype(float).to_numpy(), F.group_tight.to_numpy(), F.paper_id.map(tm).to_numpy())
    rows.append(dict(measure=col, **b, perm_baseline=float(perm[col].mean()) if col in perm else np.nan, n_names=len(F)))
# true-author surnames share in field top50 (reference)
ta = [(s, f) for ss, f in zip(P.surs, P.field) for s in ss]
rows.append(dict(measure='true_authors_field_top50', target=np.nan, control=np.nan, diff=np.nan, lo=np.nan, hi=np.nan, perm_baseline=float(np.mean([s in top[f] for s, f in ta])), n_names=len(ta)))
A = pd.DataFrame(rows); A.to_csv(OUT / 'a_wrong_names.csv', index=False); res['a'] = rows
# --- b) MC distractors
mc = [json.loads(l) for l in open(J / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/mc_team.jsonl')]
mc = [r for r in mc if r.get('kind') == 'team' and r['paper_id'] in idx]
sims, incoh, pids = [], [], []
for r in mc:
    i = idx[r['paper_id']]; fs = [idx.get(x) for x in r.get('false_sources', [])]
    js = [j for j in fs if j is not None]; incoh.append(len(js) / max(1, len(fs)))
    sims.append(float(np.mean([E[i] @ E[j] for j in js])) if js else np.nan); pids.append(r['paper_id'])
M = pd.DataFrame(dict(paper_id=pids, sim=sims, incohort=incoh)).merge(P[['paper_id', 'group_tight', 'citation_bin', 'team']], on='paper_id')
M = M[M.group_tight.isin(['target', 'control'])]
M['is_target'] = (M.group_tight == 'target').astype(float)
ok = M.sim.notna(); M.loc[ok, 'sim_q'] = pd.qcut(M.loc[ok, 'sim'], 4, labels=['Q1 low', 'Q2', 'Q3', 'Q4 high'])
bq = M[ok].groupby('sim_q', observed=True).agg(n=('is_target', 'size'), target_share=('is_target', 'mean'), mean_sim=('sim', 'mean')).reset_index()
# within citation bin: logistic-free check: mean within-bin centred target share by quartile
M['ts_c'] = M.is_target - M.groupby('citation_bin').is_target.transform('mean')
bq['within_bin_centred'] = M[ok].groupby('sim_q', observed=True).ts_c.mean().to_numpy()
bq.to_csv(OUT / 'b_mc_by_distractor_similarity.csv', index=False)
res['b'] = dict(n_mc=len(M), share_distractors_in_cohort=float(M.incohort.mean()), n_with_sim=int(ok.sum()), quartiles=bq.to_dict('records'))
# --- d) lens trajectory
T = pd.read_parquet(J / '351_stage10/summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'true_mean_nlr_surname_first'])
T = T[T.paper_id.isin(idx)]
dres = []
for ro in ('logit', 'jlens_public'):
    w = T[(T.readout == ro) & (T.layer >= 40) & (T.layer <= 62)].pivot(index='paper_id', columns='layer', values='true_mean_nlr_surname_first')
    w = w.dropna(axis=1, how='all')
    fin = T[(T.readout == 'final') & (T.layer == 63)].set_index('paper_id').true_mean_nlr_surname_first
    w[63] = fin.reindex(w.index)  # last point = the model's own output (final L63)
    layers = w.columns.to_numpy(); X = w.to_numpy(); pk = np.nanargmax(X, 1); peak = X[np.arange(len(X)), pk]; last = X[:, -1]
    d = peak - last; rf = (layers[pk] < layers[-1]) & (d >= 0.3)
    df = pd.DataFrame(dict(paper_id=w.index, rise_fall=rf.astype(float), drop=d, peak_layer=layers[pk])).merge(P[['paper_id', 'group_tight', 'team']], on='paper_id')
    df = df[df.group_tight.isin(['target', 'control'])]
    b = boot_diff(df.rise_fall.to_numpy(), df.group_tight.to_numpy(), df.team.to_numpy())
    mean_curve = w.join(P.set_index('paper_id').group_tight).groupby('group_tight').mean().loc[['target', 'control']]
    mean_curve.to_csv(OUT / f'd_mean_curve_{ro}.csv')
    dres.append(dict(readout=ro, layers=[int(x) for x in layers], **b, median_peak_layer_target=float(df[df.group_tight == 'target'].peak_layer.median()),
                     median_peak_layer_control=float(df[df.group_tight == 'control'].peak_layer.median())))
pd.DataFrame(dres).to_csv(OUT / 'd_rise_fall.csv', index=False); res['d'] = dres
json.dump(res, open(OUT / 'results.json', 'w'), indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:6000]); print('DONE', OUT)
