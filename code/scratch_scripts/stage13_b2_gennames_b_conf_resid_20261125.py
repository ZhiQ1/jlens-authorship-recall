"""2-11b POST-HOC (事后，探索性), user 2026-11-25: how much of the output-confidence baseline (conf3 = 0.711, slide 124) is left after
removing "how easy the name is to write" (name commonness / string features)? CPU, cached data only; nothing existing is edited.

Data, names, folds, bootstrap: identical to stage13_c24_optB_analyze_20261114.py (loaded by path): generation-time confidence
gen_lp_mean, gen_lp_first, -gen_ent_pre; M/H names with valid generation-time confidence; within-paper AUROC over (M, H) pairs on
target papers; author-team cluster bootstrap 2,000 draws (seed 12), all scores on one draw set.
Name features Z (same as comb_new minus position): name length (chars), log(1 + cohort full-name frequency excluding this paper),
fame (4 cols: robust.fame_features). Sensitivity Z+ = Z + position (item index, relative index).
Residualisation: each confidence feature regressed on Z by OLS, OUT-OF-FOLD on the archived team folds (fit on 4 folds, residual on
the held-out fold); OOF R^2 reported. Scores:
  conf3            fit_oof logistic of the 3 raw features (reproduces 0.711)
  lp_mean_raw      raw mean log-prob of the name (reproduces 0.698)
  lp_mean_resid    its residual on Z (no fitting)
  conf3_resid      fit_oof logistic of the 3 residuals on Z;  conf3_residP: residuals on Z+
  names_Z          fit_oof logistic of Z alone (how far name features alone go)
  probe@L (name_mean, ii) for L16..L56, and probe − conf3_resid.
Outputs: 381_stage13/summary_conf_resid_20261125/{conf_resid.csv, report.md}
"""
import importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('c24b', H / '13_stage13/stage13_c24_optB_analyze_20261114.py'); OBM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(OBM)
RB, AN, V1, V2, B, ROOT = OBM.RB, OBM.AN, OBM.V1, OBM.V2, OBM.B, OBM.ROOT
OUT = OBM.R13 / 'summary_conf_resid_20261125'


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def ci(v): return tuple(np.percentile(v, [2.5, 97.5]))
def fmt(e, lo, hi, s=''): return f'{e:{s}.3f} [{lo:{s}.3f}, {hi:{s}.3f}]'


def resid_oof(c, Z, fold):
    r = np.full(len(c), np.nan); ss_res = ss_tot = 0.0
    for k in np.unique(fold):
        tr, te = fold != k, fold == k
        A = np.c_[np.ones(tr.sum()), Z[tr]]; beta, *_ = np.linalg.lstsq(A, c[tr], rcond=None)
        pred = np.c_[np.ones(te.sum()), Z[te]] @ beta; r[te] = c[te] - pred
        ss_res += ((c[te] - pred) ** 2).sum(); ss_tot += ((c[te] - c[tr].mean()) ** 2).sum()
    return r, 1 - ss_res / ss_tot


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
    tgt = (N.group_tight == 'target').to_numpy()
    RB.V3.patch(); P, _ = B.load_papers(); pool = B.Pool(P)
    exc = np.array([len(pool.full.get(' '.join(B.words(nm)), set()) - {pid}) for nm, pid in zip(N.name, N.paper_id)], float)
    XP = N[['item_index', 'item_rel']].to_numpy(float)
    Z = np.c_[N.name_len_chars.to_numpy(float), np.log1p(exc), RB.fame_features(N, P)]; ZP = np.c_[Z, XP]
    lpm = N.key.map(cm.gen_lp_mean).to_numpy(float); lpf = N.key.map(cm.gen_lp_first).to_numpy(float); nent = -N.key.map(cm.gen_ent_pre).to_numpy(float)
    XC = np.stack([lpm, lpf, nent], 1)
    R, RP, r2 = [], [], {}
    for nm_, c in (('lp_mean', lpm), ('lp_first', lpf), ('neg_entropy', nent)):
        r, q = resid_oof(c, Z, fold); rp, qp = resid_oof(c, ZP, fold); R.append(r); RP.append(rp); r2[nm_] = (q, qp)
        log('R2', nm_, round(q, 4), round(qp, 4))
    R, RP = np.stack(R, 1), np.stack(RP, 1)
    sc = {}
    sc['conf3'], _, _ = V1.fit_oof(XC, y, fold)
    sc['lp_mean_raw'] = lpm; sc['lp_mean_resid'] = R[:, 0]
    sc['conf3_resid'], _, _ = V1.fit_oof(R, y, fold)
    sc['conf3_residP'], _, _ = V1.fit_oof(RP, y, fold)
    sc['names_Z'], _, _ = V1.fit_oof(Z, y, fold)
    for l in AN.LAYERS:
        X = np.concatenate([z[f'name_mean@{l}'] for z in zs])[ix].astype(np.float32)
        sc[f'probe{l}'], _, _ = V1.fit_oof(X, y, fold); log('probe', l)
    names = list(sc)
    st = [V2.pair_stats(paper[tgt], y[tgt], sc[k][tgt]) for k in names]
    common = set.intersection(*[set(s) for s in st]); st = [{p_: s[p_] for p_ in common} for s in st]
    est, bt, npap, npair = V2.within_auroc(st, PT); j = {k: i for i, k in enumerate(names)}
    rows = [dict(score=k, auroc=est[j[k]], lo=ci(bt[:, j[k]])[0], hi=ci(bt[:, j[k]])[1]) for k in names]
    def diff(a, b): d = bt[:, j[a]] - bt[:, j[b]]; return est[j[a]] - est[j[b]], *ci(d)
    D = {'conf3 − conf3_resid': diff('conf3', 'conf3_resid'), 'conf3 − conf3_residP': diff('conf3', 'conf3_residP'),
         'lp_mean_raw − lp_mean_resid': diff('lp_mean_raw', 'lp_mean_resid')}
    for l in AN.LAYERS: D[f'probe{l} − conf3_resid'] = diff(f'probe{l}', 'conf3_resid'); D[f'probe{l} − conf3'] = diff(f'probe{l}', 'conf3')
    T = pd.DataFrame(rows); T.to_csv(OUT / 'conf_resid.csv', index=False)
    pd.DataFrame([dict(diff=k, est=e, lo=a, hi=b) for k, (e, a, b) in D.items()]).to_csv(OUT / 'conf_resid_diffs.csv', index=False)
    L = ['# Output confidence after removing name commonness / string features (POST-HOC, exploratory)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2_gennames_b_conf_resid_20261125.py`. Names used {len(N)}; target papers / pairs {npap} / {npair}.', '',
         '## OOF R² of each confidence feature on name features', '', '| feature | R² on Z (length, frequency, fame) | R² on Z + position |', '|---|---|---|']
    L += [f'| {k} | {a:.3f} | {b:.3f} |' for k, (a, b) in r2.items()]
    L += ['', '## Within-paper AUROC (target papers, team bootstrap 2,000)', '', '| score | AUROC [95% CI] |', '|---|---|']
    L += [f'| {r["score"]} | {fmt(r["auroc"], r["lo"], r["hi"])} |' for r in rows]
    L += ['', '## Paired differences', '', '| difference | est [95% CI] |', '|---|---|'] + [f'| {k} | {fmt(e, a, b, "+")} |' for k, (e, a, b) in D.items()]
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('wrote', OUT / 'report.md')


if __name__ == '__main__':
    main()
