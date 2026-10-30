"""X4 author patchscope split by first-author name-token role (user request 2026-10-29/30). CPU, reads followup/x4tok2 (b7 = original batch).
D = mean nlr(self source) - mean nlr(partner source) over tokens of that role, per paper; 95% team-cluster bootstrap (2,000, seed 47).
Also compares with the supervised text baseline (summary_x1x4/x4_textbase2_perpaper.csv) on the same papers.
Output: summary_x1x4/x4_rolesplit.csv"""
import glob
import numpy as np, pandas as pd
R = '/scratch/zhang.zhiqi2/jlens/381_stage13/'
T = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(R + 'followup/x4tok2/shard_*.csv'))]); T = T[T.batch == 'b7']
ps = pd.read_csv(R + 'summary_x1x4/x4_textbase2_perpaper.csv').set_index('paper_id')
codes, u = pd.factorize(ps.team); W = np.random.default_rng(47).multinomial(len(u), np.full(len(u), 1 / len(u)), size=2000).astype(float)[:, codes]; idx = {p: i for i, p in enumerate(ps.index)}
rows = []
def add(name, s, layer, role):
    s = s.dropna(); w = W[:, [idx[p] for p in s.index]]; x = s.to_numpy(); b = (w @ x) / w.sum(1)
    rows.append(dict(measure=name, layer=layer, role=role, n=len(x), mean=x.mean(), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5), mean_over_sd=x.mean() / x.std(), win=np.mean(np.where(x > 0, 1, np.where(x < 0, 0, .5)))))
D = {}
for L in (8, 40):
    t = T[T.layer == L]
    for role in ('given_first', 'initial_first', 'surname_first', 'all'):
        tt = t if role == 'all' else t[t.role == role]
        m = tt.groupby(['paper_id', 'source']).nlr.mean().unstack(); D[L, role] = m['self'] - m['partner']; add('qwen', D[L, role], L, role)
for f in ('bert', 'tfidf_svd'):
    for role in ('given_first', 'surname_first'):
        s = ps.loc[D[8, role].index, f'lp_{f}_{role}']; add(f'text_{f}', s, None, role)
        rows[-1]['corr_with_qwen_L8'] = float(np.corrcoef(D[8, role].loc[s.index], s)[0, 1])
pd.DataFrame(rows).to_csv(R + 'summary_x1x4/x4_rolesplit.csv', index=False); print(pd.DataFrame(rows).round(4).to_string())
