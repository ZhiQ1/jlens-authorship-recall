"""Addendum 10 item 4, deviation D1 (config/prereg_addendum10_deviations.md, written before results): per-donor exclusion.
spec_pd = probe(true) - mean over usable k of probe(false_k), usable = donor of false_k not a training-fold paper (dropped_k False);
a paper is kept when >= 1 false title is usable. Controls averaged the same way (per-title control columns ctrl_any_k*, ctrl_field_k*).
Side by side: V5x0 (five-title mean, false_0-only exclusion) and V0 (published E4b reference).
All-paper = target + control; team-cluster bootstrap 2,000 draws (estimators as stage13_b1_e4b5_report.py).
Appends section 'Per-donor exclusion (deviation D1)' to reports/b1_e4b5_report.md and writes summary_b1_e4b5/perdonor*.csv."""
import argparse, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
NB = 2000; KS = [0, 1, 2, 3, 4]
RUNS = ['e4b_parity', 'first_alltok', 'initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
root = R13 / 'b1_tiny' if a.tiny else R13
PR = root / 'summary_b1_e4b5/probe'; OUT = root / 'summary_b1_e4b5'; REP = root / 'reports/b1_e4b5_report.md'
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')


def team_weights(pids, seed):
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    return np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)[:, codes]


def mean_cluster(pids, x, seed=2):
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]
    if len(x) == 0: return np.nan, np.nan, np.nan, 0
    W = team_weights(pids, seed); return x.mean(), *np.percentile((W @ x) / np.maximum(W.sum(1), 1e-9), [2.5, 97.5]), len(x)


def strat_cluster(df, col, gcol, a_, b_, strata, min_n=30, seed=1):
    df = df[df[gcol].isin([a_, b_])].dropna(subset=[col]).reset_index(drop=True); cells = []
    for s, ss in df.groupby(strata):
        ia, ib = ss.index[ss[gcol] == a_].to_numpy(), ss.index[ss[gcol] == b_].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan, 0
    w = np.array([len(x) * len(y) / (len(x) + len(y)) for x, y in cells]); w /= w.sum()
    x = df[col].to_numpy(float); W = team_weights(df.paper_id.to_numpy(), seed)
    est = sum(wi * (x[ia].mean() - x[ib].mean()) for wi, (ia, ib) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (ia, ib) in zip(w, cells):
        bt += wi * ((W[:, ia] @ x[ia]) / np.maximum(W[:, ia].sum(1), 1e-9) - (W[:, ib] @ x[ib]) / np.maximum(W[:, ib].sum(1), 1e-9))
    return est, *np.percentile(bt, [2.5, 97.5]), len(cells)


def f3(v, lo, hi):
    return '-' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')


def perdonor(d):
    use = np.stack([~d[f'dropped_{k}'].to_numpy(bool) for k in KS], 1).astype(float)
    nuse = use.sum(1); safe = np.where(nuse > 0, nuse, np.nan)
    sk = np.stack([d[f'spec_k{k}'].to_numpy(float) for k in KS], 1)
    d['n_used'] = nuse; d['spec_pd'] = np.nansum(sk * use, 1) / safe
    for c in ('any', 'field'):
        ck = np.stack([d[f'ctrl_{c}_k{k}'].to_numpy(float) for k in KS], 1) if f'ctrl_{c}_k0' in d else np.full_like(sk, np.nan)
        d[f'ctrl_{c}_pd'] = np.nansum(ck * use, 1) / safe
    return d


rows, nused = [], []
layers = sorted({int(f.stem.rsplit('_L', 1)[1]) for f in PR.glob('perpaper_*_L*.parquet')})
for run in RUNS:
    for l in layers:
        f = PR / f'perpaper_{run}_L{l}.parquet'
        if not f.exists(): continue
        d = perdonor(pd.read_parquet(f).join(META, on='paper_id')); tc = d.group_tight.isin(['target', 'control'])
        kept = d[tc & (d.n_used >= 1)]
        if l == 40: nused.append(dict(run=run, kept=len(kept), **{f'n_used_{i}': int((d[tc].n_used == i).sum()) for i in range(6)}, mean_used=float(kept.n_used.mean()) if len(kept) else np.nan))
        for v, sub, col, ca, cf in (('Vpd', kept, 'spec_pd', 'ctrl_any_pd', 'ctrl_field_pd'),
                                    ('V5x0', d[tc & ~d.drop0], 'spec5', 'ctrl_any5', 'ctrl_field5'),
                                    ('V0', d[tc & ~d.drop0], 'spec0', 'ctrl_any0', 'ctrl_field0')):
            m, lo, hi, n = mean_cluster(sub.paper_id.to_numpy(), sub[col].to_numpy())
            t, tlo, thi, nb = strat_cluster(sub.reset_index(drop=True), col, 'group_tight', 'target', 'control', 'citation_bin')
            ma = mean_cluster(sub.paper_id.to_numpy(), sub[ca].to_numpy()); mf = mean_cluster(sub.paper_id.to_numpy(), sub[cf].to_numpy())
            rows.append(dict(run=run, layer=l, version=v, spec=m, lo=lo, hi=hi, n=n, tc=t, tc_lo=tlo, tc_hi=thi, tc_bins=nb,
                             ctrl_any=ma[0], ctrl_any_lo=ma[1], ctrl_any_hi=ma[2], ctrl_field=mf[0], ctrl_field_lo=mf[1], ctrl_field_hi=mf[2]))
T = pd.DataFrame(rows); T.to_csv(OUT / 'perdonor_by_run_layer.csv', index=False); NU = pd.DataFrame(nused); NU.to_csv(OUT / 'perdonor_n_used_L40.csv', index=False)
L = ['', '## Per-donor exclusion (deviation D1, primary after the 5-donor rule left 0 papers)', '',
     'spec_pd = probe(true) - mean over the false titles whose donor is not a training-fold paper; kept if >= 1 usable. Target + control papers; team CI; * = CI excludes 0. V5x0 = five-title mean with false_0-only exclusion; V0 = published E4b rule (reference).', '',
     '### Papers kept and false titles used per paper (L40)', '', '| run | kept | papers with 0 / 1 / 2 / 3 / 4 / 5 usable | mean used (kept) |', '|---|---|---|---|']
for _, r in NU.iterrows():
    L.append(f'| {r.run} | {int(r.kept)} | ' + ' / '.join(str(int(r[f"n_used_{i}"])) for i in range(6)) + f' | {r.mean_used:.2f} |')
for v in ['Vpd', 'V5x0', 'V0']:
    s = T[T.version == v]
    L += ['', f'### {v}: title-specific signal (all target + control papers)', '', '| run | ' + ' | '.join(f'L{x}' for x in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in RUNS:
        g = s[s.run == run].set_index('layer')
        if len(g): L.append(f'| {run} | ' + ' | '.join(f3(g.loc[x, 'spec'], g.loc[x, 'lo'], g.loc[x, 'hi']) if x in g.index else '' for x in layers) + ' |')
    L += ['', f'{v}: target - control within citation bin', '', '| run | ' + ' | '.join(f'L{x}' for x in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in RUNS:
        g = s[s.run == run].set_index('layer')
        if len(g): L.append(f'| {run} | ' + ' | '.join(f3(g.loc[x, 'tc'], g.loc[x, 'tc_lo'], g.loc[x, 'tc_hi']) if x in g.index else '' for x in layers) + ' |')
    L += ['', f'{v}: permutation controls at L40 (random other paper / same field)', '']
    for run in RUNS:
        g = s[(s.run == run) & (s.layer == 40)]
        if len(g): r = g.iloc[0]; L.append(f'- {run}: any {f3(r.ctrl_any, r.ctrl_any_lo, r.ctrl_any_hi)}; field {f3(r.ctrl_field, r.ctrl_field_lo, r.ctrl_field_hi)}')
# primary contrasts at L40 under Vpd (joint team draws over the union of the two paper sets)
try:
    a_ = perdonor(pd.read_parquet(PR / 'perpaper_surname_first_L40.parquet').join(META, on='paper_id'))
    b_ = perdonor(pd.read_parquet(PR / 'perpaper_initial_L40.parquet').join(META, on='paper_id'))
    a_ = a_[a_.group_tight.isin(['target', 'control']) & (a_.n_used >= 1)].dropna(subset=['spec_pd'])
    b_ = b_[b_.group_tight.isin(['target', 'control']) & (b_.n_used >= 1)].dropna(subset=['spec_pd'])
    allp = np.concatenate([a_.paper_id.to_numpy(), b_.paper_id.to_numpy()]); W = team_weights(allp, 4); W1, W2 = W[:, :len(a_)], W[:, len(a_):]
    x1, x2 = a_.spec_pd.to_numpy(), b_.spec_pd.to_numpy()
    bt = (W1 @ x1) / np.maximum(W1.sum(1), 1e-9) - (W2 @ x2) / np.maximum(W2.sum(1), 1e-9); lo, hi = np.percentile(bt, [2.5, 97.5])
    s1 = mean_cluster(a_.paper_id.to_numpy(), x1)
    L += ['', '### Addendum-9 primary contrasts at L40 under Vpd', '', f'- surname_first: {f3(s1[0], s1[1], s1[2])} (n = {s1[3]})',
          f'- surname_first - initial: {f3(x1.mean() - x2.mean(), lo, hi)}']
except Exception as e:
    L += ['', f'(primary contrasts not computed: {e})']
txt = REP.read_text() if REP.exists() else ''
if '## Per-donor exclusion (deviation D1' in txt: txt = txt[:txt.index('\n## Per-donor exclusion (deviation D1')]
REP.write_text(txt.rstrip('\n') + '\n' + '\n'.join(L) + '\n'); print('\n'.join(L))
