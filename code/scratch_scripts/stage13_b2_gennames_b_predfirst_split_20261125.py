"""2-11b POST-HOC (事后，探索性；预注册 addendum 15 未涵盖), user 2026-11-25.
Finding: probe (i) pred_first falls on two different token types: for the 1st written name it is the last prompt token ("\\n\\n" after
</think>), for the 2nd+ names it is the ';' separator. Split (i) by item position, using the cached residuals only (no GPU).

Per layer (L16..L56), positions pred_first (i) and name_mean (ii, reference):
 A  original pooled probe (same fit as stage13_b2_gennames_b_analyze.py; reproduction checked against summary/probe_within.csv):
    within-paper (M, H) pairs on qualifying target papers split into  A_mixed = pairs containing the 1st name (item 0)  and
    A_later = both names item >= 1.
 B  probes refit on each subset alone (same fit_oof, archived team folds, target + control names):
    B_first  = item-0 names only. Each paper has one item-0 name, so no within-paper pairs exist: POOLED AUROC (target papers,
               M vs H item-0 names) with author-team cluster bootstrap.
    B_later  = item >= 1 names only: WITHIN-paper AUROC (target papers with >= 1 M and >= 1 H among item >= 1 names) + POOLED AUROC.
    shuffled-label control (rng 1212, within training folds) for every B fit.
CIs: author-team cluster bootstrap, 2,000 draws. Reads b2_gennames_b/{names,raw}; writes summary_predfirst_split_20261125/.
Usage: --layers 16 [--nb 2000] [--out DIR]
"""
import argparse, hashlib, importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); ROOT = R13 / 'b2_gennames_b'
_sp = importlib.util.spec_from_file_location('gnb_v3b', H / '13_stage13/stage13_b2_gennames_b_v3b.py'); V3B = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V3B)
B = V3B.V3.B; V1, V2 = B.V1, B.V2
N_SHARDS = 48


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def pooled_ci(y, p, team, nb, seed=5):
    """pooled AUROC + team-cluster bootstrap (rank-based, ties 0.5)."""
    ok = ~np.isnan(p); y, p, team = y[ok].astype(float), p[ok], team[ok]
    if len(np.unique(y)) < 2: return np.nan, np.nan, np.nan, int(y.sum()), int((1 - y).sum())
    o = np.argsort(p, kind='mergesort'); p, y, team = p[o], y[o], team[o]
    _, start = np.unique(p, return_index=True)                         # tie groups (sorted)
    def auc(Wm):                                                        # Wm: [k, n] weights -> [k] weighted Mann-Whitney (ties 0.5)
        pos = np.add.reduceat(Wm * y, start, axis=1); neg = np.add.reduceat(Wm * (1 - y), start, axis=1)
        below = np.cumsum(neg, 1) - neg
        return (pos * (below + 0.5 * neg)).sum(1) / np.maximum(pos.sum(1) * neg.sum(1), 1e-12)
    est = float(auc(np.ones((1, len(y))))[0])
    uniq, codes = np.unique(team, return_inverse=True); rng = np.random.default_rng(seed)
    W = rng.multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=nb)
    bt = np.concatenate([auc(W[i:i + 200][:, codes].astype(float)) for i in range(0, nb, 200)])
    lo, hi = np.nanpercentile(bt, [2.5, 97.5]); return est, lo, hi, int(y.sum()), int((1 - y).sum())


def within_ci(paper, y, s, PT, nb):
    st = V2.pair_stats(paper, y, s)
    if not st: return np.nan, np.nan, np.nan, 0, 0
    est, bt, npap, npair = V2.within_auroc([st], PT, nb=nb); lo, hi = np.percentile(bt[:, 0], [2.5, 97.5])
    return float(est[0]), lo, hi, npap, npair


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--layers', required=True); ap.add_argument('--nb', type=int, default=2000)
    ap.add_argument('--out', default=str(ROOT / 'summary_predfirst_split_20261125')); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); layers = [int(x) for x in a.layers.split(',')]
    NA = pd.concat([pd.read_parquet(ROOT / f'names/shard_{k:03d}.parquet') for k in range(N_SHARDS)], ignore_index=True)
    zs = [np.load(ROOT / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in range(N_SHARDS)]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    N = N.reset_index(drop=True); ix = np.array([kidx[k_] for k_ in N.key])
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); team = N.team.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy(); first = (N.item_index == 0).to_numpy(); later = ~first
    q = N[tgt].groupby('paper_id').status.agg(lambda s: (s == 'M').any() and (s == 'H').any()); qual = N.paper_id.isin(set(q[q].index)).to_numpy()
    ref = pd.read_csv(ROOT / 'summary/probe_within.csv').set_index(['layer', 'position'])
    rows = []
    for l in layers:
        for pos in ('pred_first', 'name_mean'):
            t0 = time.time()
            X = np.concatenate([z[f'{pos}@{l}'] for z in zs])[ix].astype(np.float32)
            # ---- A: original pooled probe
            pr, C, _ = V1.fit_oof(X, y, fold)
            full = within_ci(paper[tgt], y[tgt], pr[tgt], PT, a.nb)
            refv = ref.loc[(l, pos), 'auroc_within']
            # pair decomposition on qualifying target papers
            m = tgt & qual; d = pd.DataFrame(dict(p=paper[m], y=y[m], s=pr[m], f=first[m]))
            cm = nm = cl = nl = 0.0
            for _, g in d.groupby('p', sort=False):
                M, Hh = g[g.y == 1], g[g.y == 0]
                if not len(M) or not len(Hh): continue
                gt = (M.s.to_numpy()[:, None] > Hh.s.to_numpy()[None, :]) + 0.5 * (M.s.to_numpy()[:, None] == Hh.s.to_numpy()[None, :])
                mix = M.f.to_numpy()[:, None] | Hh.f.to_numpy()[None, :]
                cm += gt[mix].sum(); nm += mix.sum(); cl += gt[~mix].sum(); nl += (~mix).sum()
            # mixed-pair AUROC CI via pair_stats on a recoded problem is not direct -> bootstrap by team over per-paper sums
            per = []
            for p_, g in d.groupby('p', sort=False):
                M, Hh = g[g.y == 1], g[g.y == 0]
                if not len(M) or not len(Hh): continue
                gt = (M.s.to_numpy()[:, None] > Hh.s.to_numpy()[None, :]) + 0.5 * (M.s.to_numpy()[:, None] == Hh.s.to_numpy()[None, :])
                mix = M.f.to_numpy()[:, None] | Hh.f.to_numpy()[None, :]
                per.append((p_, gt[mix].sum(), mix.sum(), gt[~mix].sum(), (~mix).sum()))
            P_ = pd.DataFrame(per, columns=['p', 'cm', 'nm', 'cl', 'nl']); tm = P_.p.map(PT).to_numpy()
            uniq, codes = np.unique(tm, return_inverse=True)
            W = np.random.default_rng(12).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=a.nb)[:, codes].astype(float)
            bm = (W @ P_.cm.to_numpy()) / np.maximum(W @ P_.nm.to_numpy(), 1e-12); bl = (W @ P_.cl.to_numpy()) / np.maximum(W @ P_.nl.to_numpy(), 1e-12)
            # pooled AUROC of the original probe restricted to item 0 / item >= 1 (target)
            A_first_pooled = pooled_ci(y[tgt & first], pr[tgt & first], team[tgt & first], a.nb)
            A_later_pooled = pooled_ci(y[tgt & later], pr[tgt & later], team[tgt & later], a.nb)
            row = dict(layer=l, position=pos, C_full=C, A_full_within=full[0], A_full_lo=full[1], A_full_hi=full[2], ref_probe_within=refv,
                       repro_diff=abs(full[0] - refv),
                       A_mixed_within=cm / nm if nm else np.nan, A_mixed_lo=np.percentile(bm, 2.5), A_mixed_hi=np.percentile(bm, 97.5), A_mixed_pairs=int(nm),
                       A_later_within=cl / nl if nl else np.nan, A_later_lo=np.percentile(bl, 2.5), A_later_hi=np.percentile(bl, 97.5), A_later_pairs=int(nl),
                       A_first_pooled=A_first_pooled[0], A_first_pooled_lo=A_first_pooled[1], A_first_pooled_hi=A_first_pooled[2],
                       A_later_pooled=A_later_pooled[0], A_later_pooled_lo=A_later_pooled[1], A_later_pooled_hi=A_later_pooled[2])
            # ---- B: refit on each subset alone
            for nm_, sub in (('first', first), ('later', later)):
                Xs, ys, fs = X[sub], y[sub], fold[sub]
                ps, Cs, _ = V1.fit_oof(Xs, ys, fs); psh, _, ysh = V1.fit_oof(Xs, ys, fs, seed_shuffle=1212)
                ts = tgt[sub]; pa, te = paper[sub], team[sub]
                pl = pooled_ci(ys[ts], ps[ts], te[ts], a.nb); sh = pooled_ci(ysh[ts], psh[ts], te[ts], 200)
                row.update({f'B_{nm_}_C': Cs, f'B_{nm_}_pooled': pl[0], f'B_{nm_}_pooled_lo': pl[1], f'B_{nm_}_pooled_hi': pl[2],
                            f'B_{nm_}_nM_target': pl[3], f'B_{nm_}_nH_target': pl[4], f'B_{nm_}_shuffled_pooled': sh[0]})
                if nm_ == 'later':
                    w = within_ci(pa[ts], ys[ts], ps[ts], PT, a.nb); wsh = within_ci(pa[ts], ysh[ts], psh[ts], PT, 200)
                    row.update(B_later_within=w[0], B_later_within_lo=w[1], B_later_within_hi=w[2], B_later_within_papers=w[3], B_later_within_pairs=w[4],
                               B_later_shuffled_within=wsh[0])
            rows.append(row); log(f'L{l} {pos}: repro {row["A_full_within"]:.4f} vs {refv:.4f}; Bfirst {row["B_first_pooled"]:.3f} Blater-within {row["B_later_within"]:.3f} ({time.time()-t0:.0f}s)')
    pd.DataFrame(rows).to_csv(out / f'split_L{"_".join(map(str, layers))}.csv', index=False)


if __name__ == '__main__':
    main()
