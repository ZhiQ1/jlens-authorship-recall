"""Plan batch 2026-11-14b item 3 (post hoc, descriptive): addendum-9 title-position probe with a fully CLEAN donor set.

Probe as addendum 9 / addendum 10 item 4 (13_stage13/stage13_alltok_probe.py = P9, imported by path, not edited: Vocab,
targets = mean recorded L63 state over the paper's tokens of the role, gold tokens, 9,137-id rank vocabulary, archived team
folds, ridge with alpha in (0.1,1,10) x trace(G)/d chosen on fold 0 held-out MSE, mu/sd from the training papers only).
False titles: false_0 = Stage 11 titlepos, false_1..4 = 381_stage13/raw/b1_titlepos5 (as stage13_b1_e4b5_probe.py).
Donors: 351_stage10/cohort/conditions/false_titles.parquet (k = 0..4).

Two fits per (run, layer):
  orig   the original fit (training = run papers in the other 4 folds), via stage13_b1_e4b5_probe.ridge_fold_preds_multi
         (unchanged) -> V0 (spec0, drop0 papers excluded), Vpd (per-donor), V5x0; serves as the parity re-run.
  clean  when testing fold f, every paper that is the donor of ANY of the 5 false titles of ANY paper in fold f is removed
         from the training set; ridge refit (same alpha rule: alpha chosen on fold 0 with the clean fold-0 training set;
         mu/sd from the clean training set); spec_clean = probe(true) - mean_k probe(false_k), all test papers kept.
randsize (added after the tiny run, descriptive): per fold the same NUMBER of training papers as 'clean', drawn at random
         from the original training set (rng 1114; donors may remain) -> spec = true - mean of 5 false; separates training size from leakage.
Runs: initial, given_first, given_cont, surname_first, surname_cont (P9 roles) + all_tokens (NEW: all tokens of these
five roles pooled into one target/gold set per paper; punct and particle_* excluded as in addendum 9).
Summary: spec (team-cluster bootstrap mean) and within-citation-bin target - control (Stage 10 definition, bins >= 30 per
group, weights n_t n_c/(n_t+n_c)), 2,000 team draws; estimators copied from stage13_b1_e4b5_perdonor.py (same seeds).
Usage: stage13_clean_donor_20261114.py [--runs surname_first] [--layers 40] [--nb 2000] [--out DIR]
"""
import argparse, importlib.util, json, time, glob
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
KS = [0, 1, 2, 3, 4]
RUNS = ['surname_first', 'given_first', 'initial', 'given_cont', 'surname_cont', 'all_tokens']
T0 = time.time(); log = lambda *a: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


P9 = load(H / '13_stage13/stage13_alltok_probe.py', 'p9')
PB1 = load(H / '13_stage13/stage13_b1_e4b5_probe.py', 'pb1')
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')


def load_resid(d, lidx):
    fs = sorted(Path(d).glob('shard_*.npz')); X, P = [], []
    for f in fs:
        z = np.load(f); X.append(z['resid_title'][:, lidx]); P.append(z['resid_paper_id'])
    return np.concatenate(X), np.concatenate(P), len(fs)


def ridge_clean(X, XFs, Y, fold, trmask, alphas=P9.ALPHAS):
    """P9.ridge_fold_preds with an explicit training mask per test fold (trmask[k] boolean over rows)."""
    best = None; errs_out = None; PT = np.zeros_like(Y); PFs = [np.zeros_like(Y) for _ in XFs]
    for k in range(5):
        tr, te = trmask[k], np.where(fold == k)[0]
        if not len(te): continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        A = (X[tr] - mu) / sd; ym = Y[tr].mean(0); G = A.T @ A; Bm = A.T @ (Y[tr] - ym)
        if best is None:
            errs = [((((X[te] - mu) / sd) @ np.linalg.solve(G + a_ * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm) + ym - Y[te]) ** 2).mean() for a_ in alphas]
            best = alphas[int(np.argmin(errs))]; errs_out = [float(e) for e in errs]
        Wp = np.linalg.solve(G + best * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm)
        PT[te] = (X[te] - mu) / sd @ Wp + ym
        for XF, PF in zip(XFs, PFs): PF[te] = (XF[te] - mu) / sd @ Wp + ym
    return PT, PFs, best, errs_out


def score(PT, PFs, golds, fold, V):
    n = len(golds); st = np.full(n, np.nan); sf = np.full((n, len(PFs)), np.nan)
    for fk in range(5):
        te = np.where(fold == fk)[0]
        if not len(te): continue
        LT = V.logits(PT[te]); LF = [V.logits(PF[te]) for PF in PFs]
        for j, m in enumerate(te):
            if not golds[m]: continue
            a1 = V.nlr(LT[j], golds[m])
            if not len(a1): continue
            st[m] = a1.mean()
            for k in range(len(PFs)): sf[m, k] = V.nlr(LF[k][j], golds[m]).mean()
    return st, sf


# ---------------- estimators (copied from stage13_b1_e4b5_perdonor.py)
def team_weights(pids, seed, NB, TEAM):
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    return np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)[:, codes]


def mean_cluster(pids, x, NB, TEAM, seed=2):
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]
    if len(x) == 0: return np.nan, np.nan, np.nan, 0
    W = team_weights(pids, seed, NB, TEAM); return x.mean(), *np.percentile((W @ x) / np.maximum(W.sum(1), 1e-9), [2.5, 97.5]), len(x)


def strat_cluster(df, col, NB, TEAM, gcol='group_tight', a_='target', b_='control', strata='citation_bin', min_n=30, seed=1):
    df = df[df[gcol].isin([a_, b_])].dropna(subset=[col]).reset_index(drop=True); cells = []
    for s, ss in df.groupby(strata):
        ia, ib = ss.index[ss[gcol] == a_].to_numpy(), ss.index[ss[gcol] == b_].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan, 0
    w = np.array([len(x) * len(y) / (len(x) + len(y)) for x, y in cells]); w /= w.sum()
    x = df[col].to_numpy(float); W = team_weights(df.paper_id.to_numpy(), seed, NB, TEAM)
    est = sum(wi * (x[ia].mean() - x[ib].mean()) for wi, (ia, ib) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (ia, ib) in zip(w, cells):
        bt += wi * ((W[:, ia] @ x[ia]) / np.maximum(W[:, ia].sum(1), 1e-9) - (W[:, ib] @ x[ib]) / np.maximum(W[:, ib].sum(1), 1e-9))
    return est, *np.percentile(bt, [2.5, 97.5]), len(cells)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=','.join(RUNS)); ap.add_argument('--layers', default='40,48')
    ap.add_argument('--nb', type=int, default=2000); ap.add_argument('--out', default=str(R13 / 'summary_clean_donor_20261114')); a = ap.parse_args()
    OUT = Path(a.out); (OUT / 'probe').mkdir(parents=True, exist_ok=True); NB = a.nb
    layers = [int(x) for x in a.layers.split(',')]
    players = [int(x) for x in np.load(sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))[0])['probe_layers']]
    lidx = [players.index(l) for l in layers]
    Xt, pid, nt = load_resid(R11 / 'raw/titlepos/true', lidx)
    if nt != 72: raise SystemExit(f'true {nt}/72')
    src = {0: R11 / 'raw/titlepos/false_0', **{k: R13 / f'raw/b1_titlepos5/false_{k}' for k in KS[1:]}}
    Xf = {}
    for k in KS:
        x, pk, n = load_resid(src[k], lidx)
        if n != 72 or set(pk) != set(pid): raise SystemExit(f'false_{k}: {n} shards / paper set differs')
        o = {p: i for i, p in enumerate(pk)}; Xf[k] = x[[o[p] for p in pid]]
    log('resid loaded', Xt.shape)
    fold_full = c13.group_folds(pid, k=5)[0]; F = dict(zip(pid, fold_full)); pidx = {p: i for i, p in enumerate(pid)}
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet')
    DON = {k: ft[ft.k == k].set_index('paper_id').donor_paper_id.to_dict() for k in KS}
    # donors of any false title of any paper in fold f (paper ids)
    DONF = {f: set(DON[k][p] for k in KS for p in pid[fold_full == f]) for f in range(5)}
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
    rf = sorted((R13 / 'raw/allTok_L63').glob('shard_*.npz'))
    if len(rf) != 72: raise SystemExit(f'allTok_L63 {len(rf)}/72')
    zs = [np.load(f) for f in rf]; rid = np.concatenate([z['row_id'] for z in zs]); RES = np.concatenate([z['resid'] for z in zs]); del zs
    rpos = pd.Series(np.arange(len(rid)), index=rid); toks = toks[toks.row_id.isin(rid)]
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); V = P9.Vocab(vr['token_id'], vr['lm_head_rows'], vr['norm_weight'], vr['eps'])
    log('allTok rows', len(rid), 'vocab', len(V.vid))
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
    _, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')

    rows, sizes, usable = [], [], []
    for run in a.runs.split(','):
        roles = list(P9.ROLE_RUNS.values()) if run == 'all_tokens' else [P9.ROLE_RUNS[run]]
        t = toks[toks.role.isin(roles)]; t = t[t.paper_id.isin(pidx)].sort_values('row_id'); grp = t.groupby('paper_id', sort=False)
        P = np.array(sorted(pidx[p] for p in grp.groups)); pp = pid[P]; n = len(P)
        Y = np.zeros((n, RES.shape[1]), np.float32); golds = []
        for i, p in enumerate(pp):
            s = t.iloc[grp.indices[p]]; Y[i] = RES[rpos.loc[s.row_id].to_numpy()].astype(np.float32).mean(0); golds.append(s.token_id.tolist())
        fold = fold_full[P]; trainset = set(pp)
        dk = {k: np.array([(DON[k].get(p) in trainset) and (F[DON[k][p]] != F[p]) for p in pp]) for k in KS}
        trmask = {f: (fold != f) & ~np.isin(pp, list(DONF[f])) for f in range(5)}
        # usable false titles per test paper under the clean fit: donor not among that fold's clean training papers
        trids = {f: set(pp[trmask[f]]) for f in range(5)}
        # size-matched comparison (added after the tiny run): remove the SAME number of training papers at random (donors may stay)
        rs = np.random.default_rng(1114); trmask_r = {}
        for f in range(5):
            idx = np.where(fold != f)[0]; keep = rs.choice(idx, int(trmask[f].sum()), replace=False)
            trmask_r[f] = np.zeros(n, bool); trmask_r[f][keep] = True
        nuse_clean = np.array([sum(DON[k][p] not in trids[F[p]] for k in KS) for p in pp])
        for f in range(5):
            sizes.append(dict(run=run, fold=f, n_test=int((fold == f).sum()), n_train_orig=int((fold != f).sum()), n_train_clean=int(trmask[f].sum()),
                              n_removed=int((fold != f).sum() - trmask[f].sum())))
        usable.append(dict(run=run, papers=n, **{f'n_usable_{i}': int((nuse_clean == i).sum()) for i in range(6)}))
        log(run, 'papers', n, 'train orig/clean per fold', [(int((fold != f).sum()), int(trmask[f].sum())) for f in range(5)], 'usable==5', float((nuse_clean == 5).mean()))
        for l, li in zip(layers, range(len(layers))):
            fo = OUT / 'probe' / f'perpaper_{run}_L{l}.parquet'
            if fo.exists():
                log('exists', fo.name); df = pd.read_parquet(fo)
            else:
                X = Xt[P, li].astype(np.float32); XFs = [Xf[k][P, li].astype(np.float32) for k in KS]
                PT, PFs, b_o, e_o = PB1.ridge_fold_preds_multi(X, XFs, Y, fold); st_o, sf_o = score(PT, PFs, golds, fold, V); del PT, PFs
                PT, PFs, b_c, e_c = ridge_clean(X, XFs, Y, fold, trmask); st_c, sf_c = score(PT, PFs, golds, fold, V)
                r2c = float(1 - ((PT - Y) ** 2).sum() / ((Y - Y.mean(0)) ** 2).sum()); del PT, PFs
                PT, PFs, b_r, e_r = ridge_clean(X, XFs, Y, fold, trmask_r); st_r, sf_r = score(PT, PFs, golds, fold, V); del PT, PFs
                df = pd.DataFrame({'paper_id': pp, 'fold': fold, 'n_tok': [len(g) for g in golds],
                                   'true_o': st_o, **{f'false_o{k}': sf_o[:, k] for k in KS}, 'true_c': st_c, **{f'false_c{k}': sf_c[:, k] for k in KS},
                                   'true_r': st_r, **{f'false_r{k}': sf_r[:, k] for k in KS},
                                   **{f'dropped_{k}': dk[k] for k in KS}, 'n_usable_clean': nuse_clean})
                use = np.stack([~dk[k] for k in KS], 1).astype(float); nu = use.sum(1)
                sko = st_o[:, None] - sf_o
                df['spec0'] = sko[:, 0]; df['spec5_o'] = sko.mean(1); df['n_used_pd'] = nu
                df['spec_pd'] = np.where(nu > 0, np.nansum(sko * use, 1) / np.where(nu > 0, nu, 1), np.nan)
                df['spec_clean'] = st_c - sf_c.mean(1); df['spec_clean0'] = st_c - sf_c[:, 0]; df['spec_rand5'] = st_r - sf_r.mean(1)
                df.to_parquet(fo, index=False)
                (OUT / 'probe' / f'fit_{run}_L{l}.json').write_text(json.dumps(dict(run=run, layer=l, n_papers=int(n), alpha_orig=b_o, alpha_errs_orig=e_o,
                                                                                   alpha_clean=b_c, alpha_errs_clean=e_c, alpha_rand=b_r, alpha_errs_rand=e_r, heldout_r2_clean=r2c)))
                log(run, f'L{l}', 'alpha orig/clean', b_o, b_c, f'spec0 kept {np.nanmean(df.spec0[~df.dropped_0]):+.4f}', f'clean {np.nanmean(df.spec_clean):+.4f}')
            d = df.join(META, on='paper_id'); tc = d.group_tight.isin(['target', 'control'])
            for v, sub, col in (('clean', d[tc], 'spec_clean'), ('clean_f0only', d[tc], 'spec_clean0'), ('randsize_5mean', d[tc], 'spec_rand5'), ('Vpd', d[tc & (d.n_used_pd >= 1)], 'spec_pd'),
                                ('V0', d[tc & ~d.dropped_0], 'spec0'), ('V5x0', d[tc & ~d.dropped_0], 'spec5_o')):
                sub = sub.reset_index(drop=True)
                m, lo, hi, nn = mean_cluster(sub.paper_id.to_numpy(), sub[col].to_numpy(), NB, TEAM)
                tt, tlo, thi, nb = strat_cluster(sub, col, NB, TEAM)
                rows.append(dict(run=run, layer=l, version=v, spec=m, lo=lo, hi=hi, n=nn, tc=tt, tc_lo=tlo, tc_hi=thi, tc_bins=nb,
                                 n_target=int((sub.group_tight == 'target').sum()), n_control=int((sub.group_tight == 'control').sum())))
            log(pd.DataFrame(rows[-6:]).round(4).to_string())
    T = pd.DataFrame(rows); S = pd.DataFrame(sizes); U = pd.DataFrame(usable)
    T.to_csv(OUT / 'clean_vs_v0_vpd.csv', index=False); S.to_csv(OUT / 'train_sizes.csv', index=False); U.to_csv(OUT / 'usable_false_titles.csv', index=False)
    log('done')


if __name__ == '__main__':
    main()
