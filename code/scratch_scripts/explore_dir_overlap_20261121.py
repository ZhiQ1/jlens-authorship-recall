"""Exploratory (post hoc, not pre-registered), 2026-11-21: does the name-position target - control shift point along attribute or
author-probe directions?  CPU only, stored states (raw/b2_npprobe, surname first token rows, L40 / L48).

Delta = mean_T d - mean_C d, d_i = paper mean of [h_true - mean usable h_false] (Vpd rule; = explore_pca_np_20261120.py).
Directions (all in the raw residual space at the name position):
  attribute  ridge on paper-mean TRUE states at the name position (surname first rows): year, log10(1+citations), field
             (one-vs-rest, fields with >= 200 papers). The published M2 probes read the TITLE position and their weights are
             not stored, so these are refits at the name position with the M2-style setup (standardised X, ridge alpha 1.0 x
             tr(G)/d, all 9,108 papers); direction = w / sd, unit-normalised.
  author     Q = diag(1/sd) W diag(norm_w) U_names^T, W = the published name-position ridge map (surname first, refit on all true
             rows, alpha 1.0 x tr(G)/d, target = stored L63 residual), U_names = lm_head rows of the cohort surname-first
             tokens. q_gold(row) = Q[:, gold token] = linear part of the probe's gold-token logit; author_gold = mean over target
             papers of the paper-mean q_gold (also over all papers); author_svd = top-5 left singular vectors of Q.
Reported per layer: cos(Delta, direction); share of each direction's squared norm in the top 10 / 50 PCs of the earlier PCA
(uncentered D_T, Vpd; random baseline k/5120); for subspaces (field one-vs-rest, author_svd top-5): share of Delta inside.
"""
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
RAW = R13 / 'raw/b2_npprobe'; KS = [0, 1, 2, 3, 4]; LAYERS = [40, 48]; T0 = time.monotonic()


def log(*a): print(f'[{time.monotonic() - T0:7.0f}s]', *a, flush=True)


def unit(v): return v / np.linalg.norm(v)


def ridge_dir(X, y, alpha=1.0):
    mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; G = A.T @ A
    w = np.linalg.solve(G + alpha * np.trace(G) / G.shape[0] * np.eye(G.shape[0], dtype=np.float32), A.T @ (y - y.mean()))
    return unit(w / sd)


def main(a):
    OUT = R13 / ('summary_explore_dir_overlap_20261121' + ('_tiny' if a.tiny else '')); OUT.mkdir(parents=True, exist_ok=True)
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'role', 'token_id']).set_index('row_id')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citations', 'year', 'field']).set_index('paper_id')
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); nw = vr['norm_weight'].astype(np.float32)
    sur_ids = np.array(sorted(tok[tok.role == 'surname_first'].token_id.unique()))
    vpos = pd.Series(np.arange(len(vr['token_id'])), index=vr['token_id'])
    keep = vpos.reindex(sur_ids).notna().to_numpy(); sur_ids = sur_ids[keep]
    U = vr['lm_head_rows'][vpos.reindex(sur_ids).astype(int).to_numpy()].astype(np.float32); col = pd.Series(np.arange(len(sur_ids)), index=sur_ids)
    shards = sorted((RAW / 'true').glob('shard_*.npz'))[: (3 if a.tiny else None)]
    Ycache = None; res = dict(label='exploratory (post hoc, not pre-registered)', layers={}); rows = []
    for l in LAYERS:
        pp = pd.read_parquet(R13 / f'summary_b2_np/probe_v2/perpaper_surname_first_L{l}.parquet', columns=['paper_id'] + [f'dropped_{k}' for k in KS]).set_index('paper_id')
        Xs, Ds, PID, GT, Ys = [], [], [], [], []
        for f in shards:
            zt = np.load(f); rid = zt['row_id']; sel = tok.role.reindex(rid).to_numpy() == 'surname_first'; r = rid[sel]
            ht = zt[f'resid_L{l}'][sel].astype(np.float32); pid = tok.paper_id.reindex(r).to_numpy()
            dm = np.stack([~pp[f'dropped_{k}'].reindex(pid).fillna(True).to_numpy().astype(bool) for k in KS], 1); fs = np.zeros_like(ht)
            for k in KS:
                zf = np.load(RAW / f'false_{k}' / f.name)
                if not np.array_equal(zf['row_id'], rid): raise SystemExit('row mismatch')
                fs += zf[f'resid_L{l}'][sel].astype(np.float32) * dm[:, k:k + 1]
            with np.errstate(invalid='ignore', divide='ignore'): Ds.append(ht - fs / dm.sum(1, keepdims=True))
            Xs.append(ht); PID.append(pid); GT.append(tok.token_id.reindex(r).to_numpy())
            if Ycache is None:
                zy = np.load(R13 / 'raw/allTok_L63' / f.name); yp = pd.Series(np.arange(len(zy['row_id'])), index=zy['row_id']).reindex(r).to_numpy().astype(int)
                Ys.append(zy['resid'][yp].astype(np.float32))
        X = np.concatenate(Xs); D = np.concatenate(Ds); PID = np.concatenate(PID); GT = np.concatenate(GT)
        if Ycache is None: Ycache = np.concatenate(Ys)
        Y = Ycache; log(f'L{l}: {len(X)} rows')
        # author probe map
        mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; G = A.T @ A
        Wm = np.linalg.solve(G + np.trace(G) / G.shape[0] * np.eye(G.shape[0], dtype=np.float32), A.T @ (Y - Y.mean(0))); del A, G
        Q = ((Wm / sd[:, None]) * nw[None, :]) @ U.T; del Wm
        gi = col.reindex(GT).to_numpy(); okg = np.isfinite(gi)
        qrow = np.full((len(X), X.shape[1]), np.nan, np.float32); qrow[okg] = Q[:, gi[okg].astype(int)].T
        Us, ss, _ = np.linalg.svd(Q, full_matrices=False); author_svd = Us[:, :5].T; del Q
        # paper means
        dfX = pd.DataFrame(X); dfX['p'] = PID; Xp = dfX.groupby('p').mean(); del dfX
        dfD = pd.DataFrame(D); dfD['p'] = PID; okd = np.isfinite(D).all(1); Dp = dfD[okd].groupby('p').mean(); del dfD
        dfq = pd.DataFrame(qrow); dfq['p'] = PID; qp = dfq[okg].groupby('p').mean(); del dfq, qrow
        g = papers.group_tight.reindex(Dp.index).to_numpy(); T = Dp[g == 'target'].to_numpy(); C = Dp[g == 'control'].to_numpy()
        mC = C.mean(0); Delta = T.mean(0) - mC; DT = T - mC; _, sv, Vt = np.linalg.svd(DT, full_matrices=False); del DT
        gq = papers.group_tight.reindex(qp.index).to_numpy()
        dirs = {'author_gold (target papers)': unit(qp[gq == 'target'].to_numpy().mean(0)), 'author_gold (all papers)': unit(qp.to_numpy().mean(0))}
        for i in range(5): dirs[f'author_svd {i + 1}'] = author_svd[i]
        meta = papers.reindex(Xp.index); Xa = Xp.to_numpy()
        yr = pd.to_numeric(meta.year, errors='coerce').to_numpy(float); lc = np.log10(1 + pd.to_numeric(meta.citations, errors='coerce').to_numpy(float))
        okr = np.isfinite(yr); dirs['attr year'] = ridge_dir(Xa[okr], yr[okr]); okc = np.isfinite(lc); dirs['attr log citations'] = ridge_dir(Xa[okc], lc[okc])
        fc = meta.field.value_counts(); fields = [f for f, n in fc.items() if n >= 200]
        fdirs = []
        for f in fields:
            v = ridge_dir(Xa, (meta.field.to_numpy() == f).astype(np.float32)); dirs[f'attr field={f}'] = v; fdirs.append(v)
        dn = unit(Delta); kk = [10, 50]
        for nm, v in dirs.items():
            rows.append(dict(layer=l, direction=nm, cos_with_Delta=float(dn @ v), share_top10PC=float(((Vt[:10] @ v) ** 2).sum()), share_top50PC=float(((Vt[:50] @ v) ** 2).sum()),
                             random_top10=10 / len(v), random_top50=50 / len(v)))
        def sub_share(M):
            if len(M) == 0: return float('nan'), 0
            Qo, _ = np.linalg.qr(np.asarray(M).T); return float(((Qo.T @ dn) ** 2).sum()), Qo.shape[1]
        sf, nf = sub_share(fdirs); sa, na = sub_share(author_svd); sall, nall = sub_share([v for v in dirs.values()])
        res['layers'][l] = dict(n_target=int(len(T)), n_control=int(len(C)), delta_norm=float(np.linalg.norm(Delta)),
                                Delta_share_field_subspace=sf, field_dims=nf, Delta_share_author_svd5=sa, author_dims=na,
                                Delta_share_all_dirs=sall, all_dims=nall, random_per_dim=1 / len(dn), fields=fields,
                                Delta_share_top10PC=float(((Vt[:10] @ dn) ** 2).sum()), Delta_share_top50PC=float(((Vt[:50] @ dn) ** 2).sum()))
        log(f'L{l} done: nT {len(T)} nC {len(C)}; fields {len(fields)}')
    D = pd.DataFrame(rows); D.to_csv(OUT / 'dir_overlap.csv', index=False); json.dump(res, open(OUT / 'dir_overlap.json', 'w'), indent=1)
    L = ['# Direction overlap at the name positions — exploratory (post hoc, not pre-registered)', '', __doc__, '']
    for l, r in res['layers'].items():
        L += [f'## L{l} · n_T {r["n_target"]} / n_C {r["n_control"]} · |Delta| {r["delta_norm"]:.3f}', '',
              '| direction | cos(Δ, dir) | share in top-10 PCs | share in top-50 PCs |', '|---|---|---|---|']
        for _, x in D[D.layer == l].iterrows(): L.append(f"| {x.direction} | {x.cos_with_Delta:+.3f} | {x.share_top10PC:.3f} | {x.share_top50PC:.3f} |")
        L += [f'| random direction (expected) | ±{1 / np.sqrt(5120):.3f} (1 sd) | {10 / 5120:.4f} | {50 / 5120:.4f} |', '',
              f'Share of Δ inside: field subspace ({r["field_dims"]} dims) {r["Delta_share_field_subspace"]:.3f}; author SVD top-5 {r["Delta_share_author_svd5"]:.3f}; '
              f'all directions above ({r["all_dims"]} dims) {r["Delta_share_all_dirs"]:.3f}; random expectation {r["random_per_dim"]:.5f} per dimension. '
              f'Δ in top-10 / top-50 PCs: {r["Delta_share_top10PC"]:.3f} / {r["Delta_share_top50PC"]:.3f}.', '']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('DONE', OUT)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); main(ap.parse_args())
