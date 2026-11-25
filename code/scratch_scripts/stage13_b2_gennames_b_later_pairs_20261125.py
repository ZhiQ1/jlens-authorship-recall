"""2-11b POST-HOC (事后，探索性), user 2026-11-25: confidence baseline on the SAME pair subsets as the probe-(i) split.
Within-paper (M, H) pairs on target papers (>= 1 M and >= 1 H) are split into
   mixed = pairs that contain the 1st written name (item 0)   |   later = both names item >= 1.
Scores (fits identical to the published ones: V1.fit_oof, archived team folds, one pooled fit over target + control names):
   conf3 (generation-time confidence, = 0.711 on all pairs), conf3_resid (on name features, as stage13_b2_gennames_b_conf_resid_20261125),
   position, probe (ii) name_mean and probe (i) pred_first at L16..L56.
Sensitivity: conf3 and probe (ii) refit on item >= 1 names only (as B_later of the split script), evaluated on later pairs.
CI: author-team cluster bootstrap over papers, 2,000 draws (seed 12), one draw set for all scores and subsets (paired differences).
Outputs: 381_stage13/summary_later_pairs_20261125/{later_pairs.csv, diffs.csv, report.md}
"""
import importlib.util, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('cr', H / '13_stage13/stage13_b2_gennames_b_conf_resid_20261125.py'); CR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CR)
OBM, RB, AN, V1, V2, B, ROOT = CR.OBM, CR.RB, CR.AN, CR.V1, CR.V2, CR.B, CR.ROOT
OUT = OBM.R13 / 'summary_later_pairs_20261125'; NB = 2000


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def main():
    import pandas as pd
    OUT.mkdir(parents=True, exist_ok=True)
    v, _ = OBM.load_conf(False)
    shards = list(range(AN.N_SHARDS))
    NA = pd.concat([pd.read_parquet(ROOT / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    zs = [np.load(ROOT / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    v = v.copy(); v['key'] = v.paper_id + '|' + v.item_index.astype(str); cm = v.set_index('key')
    N = N[N.key.isin(cm.index)].reset_index(drop=True); ix = np.array([kidx[k_] for k_ in N.key])
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy(); first = (N.item_index == 0).to_numpy(); later = ~first
    RB.V3.patch(); P, _ = B.load_papers(); pool = B.Pool(P)
    exc = np.array([len(pool.full.get(' '.join(B.words(nm)), set()) - {pid}) for nm, pid in zip(N.name, N.paper_id)], float)
    XP = N[['item_index', 'item_rel']].to_numpy(float)
    Z = np.c_[N.name_len_chars.to_numpy(float), np.log1p(exc), RB.fame_features(N, P)]
    XC = np.stack([N.key.map(cm.gen_lp_mean).to_numpy(float), N.key.map(cm.gen_lp_first).to_numpy(float), -N.key.map(cm.gen_ent_pre).to_numpy(float)], 1)
    R = np.stack([CR.resid_oof(XC[:, j], Z, fold)[0] for j in range(3)], 1)
    sc = {}
    sc['conf3'], _, _ = V1.fit_oof(XC, y, fold); sc['conf3_resid'], _, _ = V1.fit_oof(R, y, fold); sc['position'], _, _ = V1.fit_oof(XP, y, fold)
    # later-only refits (scores only defined on item >= 1 names)
    def refit(X):
        s = np.full(len(y), np.nan); s[later] = V1.fit_oof(X[later], y[later], fold[later])[0]; return s
    sc['conf3_refit_later'] = refit(XC)
    for l in AN.LAYERS:
        for pos, tag in (('name_mean', 'ii'), ('pred_first', 'i')):
            X = np.concatenate([z[f'{pos}@{l}'] for z in zs])[ix].astype(np.float32)
            sc[f'probe_{tag}_L{l}'], _, _ = V1.fit_oof(X, y, fold)
            if tag == 'ii': sc[f'probe_ii_refit_later_L{l}'] = refit(X)
        log('layer', l)
    # per-paper concordance sums per subset
    q = N[tgt].groupby('paper_id').status.agg(lambda s: (s == 'M').any() and (s == 'H').any()); qual = sorted(q[q].index)
    m = tgt & N.paper_id.isin(set(qual)).to_numpy()
    names = list(sc); S = np.stack([sc[k] for k in names], 1)
    pm = pd.Series(np.where(m)[0]).groupby(paper[m]).apply(list)
    C = {s: np.zeros((len(pm), len(names))) for s in ('all', 'mixed', 'later')}; Np = {s: np.zeros(len(pm)) for s in C}
    for i, (p_, rows) in enumerate(pm.items()):
        rows = np.array(rows); Mi, Hi = rows[y[rows] == 1], rows[y[rows] == 0]
        mix = first[Mi][:, None] | first[Hi][None, :]
        for s, mask in (('all', np.ones_like(mix)), ('mixed', mix), ('later', ~mix)):
            Np[s][i] = mask.sum()
            a, b = S[Mi][:, None, :], S[Hi][None, :, :]
            g = (a > b) + 0.5 * (a == b)
            C[s][i] = (g * mask[:, :, None]).sum((0, 1))
    teams = np.array([PT[p_] for p_ in pm.index]); uniq, codes = np.unique(teams, return_inverse=True)
    W = np.random.default_rng(12).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB)[:, codes].astype(float)
    rows, est, bt = [], {}, {}
    for s in C:
        est[s] = C[s].sum(0) / Np[s].sum(); bt[s] = (W @ C[s]) / (W @ Np[s])[:, None]
        for j, k in enumerate(names):
            lo, hi = np.percentile(bt[s][:, j], [2.5, 97.5]); rows.append(dict(subset=s, score=k, auroc=est[s][j], lo=lo, hi=hi, pairs=int(Np[s].sum())))
    T = pd.DataFrame(rows); T.to_csv(OUT / 'later_pairs.csv', index=False)
    jj = {k: i for i, k in enumerate(names)}; drows = []
    for s in C:
        for l in AN.LAYERS:
            for a_, b_ in ((f'probe_ii_L{l}', 'conf3'), (f'probe_ii_L{l}', 'conf3_resid'), (f'probe_i_L{l}', 'conf3'), (f'probe_ii_refit_later_L{l}', 'conf3_refit_later')):
                d = bt[s][:, jj[a_]] - bt[s][:, jj[b_]]; lo, hi = np.percentile(d, [2.5, 97.5])
                drows.append(dict(subset=s, diff=f'{a_} − {b_}', est=est[s][jj[a_]] - est[s][jj[b_]], lo=lo, hi=hi))
    Dd = pd.DataFrame(drows); Dd.to_csv(OUT / 'diffs.csv', index=False)
    f = lambda e, lo, hi, sg='': f'{e:{sg}.3f} [{lo:{sg}.3f}, {hi:{sg}.3f}]'
    L = ['# Confidence baseline and probes on mixed vs later-only within-paper pairs (POST-HOC, exploratory)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2_gennames_b_later_pairs_20261125.py`. Papers {len(pm)}; pairs all/mixed/later = '
         f'{int(Np["all"].sum())}/{int(Np["mixed"].sum())}/{int(Np["later"].sum())}.', '', '| score | all pairs | mixed (contain 1st name) | later only |', '|---|---|---|---|']
    for k in names:
        r = {s: T[(T.subset == s) & (T.score == k)].iloc[0] for s in C}
        L.append(f'| {k} | ' + ' | '.join(f(r[s].auroc, r[s].lo, r[s].hi) for s in C) + ' |')
    L += ['', '| difference | all pairs | mixed | later only |', '|---|---|---|---|']
    for dname in Dd['diff'].unique():
        r = {s: Dd[(Dd.subset == s) & (Dd['diff'] == dname)].iloc[0] for s in C}
        L.append(f'| {dname} | ' + ' | '.join(f(r[s].est, r[s].lo, r[s].hi, '+') for s in C) + ' |')
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('done')


if __name__ == '__main__':
    main()
