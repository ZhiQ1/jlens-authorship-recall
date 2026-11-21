"""Exploratory (post hoc, not pre-registered), 2026-11-20: how many directions carry the name-position target - control difference?

CPU only, stored states only (raw/b2_npprobe, the addendum-11 name-position probe inputs; L40, L48; surname first token rows).
Per paper i: d_i = mean over its surname_first rows of [h_true - mean_{k usable} h_false_k], usable = not dropped under the
published per-donor rule (summary_b2_np/probe_v2/perpaper_surname_first_L<l>.parquet dropped_k; = Vpd). Papers with no usable
false title are left out (as Vpd). Sensitivity: d5 = h_true - mean of all 5 false titles.
Groups: papers.parquet group_tight (target / control).
Main: uncentered second-moment PCA of D_T = d_i(target) - mean_C d (rows = target papers), so the mean shift counts.
(a) centered PCA of pooled d (target + control). (c) centered PCA of D_T.
(b) share of Delta = mean_T d - mean_C d, and of the probe read-out matrix Q = diag(1/sd) W diag(norm_w) U_names^T
    (W = ridge map refit on all true surname_first rows as published: standardised X, alpha 1.0 * tr(G)/d, target = stored
    allTok_L63 residual), captured by the top-k PCs (energy share; random-subspace expectation k/5120).
Bootstrap: author-team multinomial weights (stage13_cpu.group_folds teams), eigenvalues only, for #PCs to 50% / 80% (main).
Usage: explore_pca_np_20261120.py [--tiny] [--nb 200] [--budget-min 32]
"""
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
RAW = R13 / 'raw/b2_npprobe'; KS = [0, 1, 2, 3, 4]; LAYERS = [40, 48]; KLIST = [1, 5, 10, 50, 100, 512]
T0 = time.monotonic()


def log(*a): print(f'[{time.monotonic() - T0:7.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def n_to(ev, q):
    c = np.cumsum(ev) / ev.sum(); return int(np.searchsorted(c, q) + 1)


def main(a):
    OUT = R13 / ('summary_explore_pca_np_20261120' + ('_tiny' if a.tiny else '')); OUT.mkdir(parents=True, exist_ok=True)
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'role', 'token_id']).set_index('row_id')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight'])
    grp = papers.set_index('paper_id').group_tight
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz')
    sur_ids = np.array(sorted(tok[tok.role == 'surname_first'].token_id.unique()))
    vpos = pd.Series(np.arange(len(vr['token_id'])), index=vr['token_id'])
    U = vr['lm_head_rows'][vpos.reindex(sur_ids).dropna().astype(int).to_numpy()].astype(np.float32)   # name-token unembedding rows
    nw = vr['norm_weight'].astype(np.float32)
    shards = sorted((RAW / 'true').glob('shard_*.npz'))[: (3 if a.tiny else None)]
    y63 = {}
    res = dict(label='exploratory (post hoc, not pre-registered)', layers={}, definition=__doc__.split('\n\n')[0])
    rows_out = []
    for l in LAYERS:
        pp = pd.read_parquet(R13 / f'summary_b2_np/probe_v2/perpaper_surname_first_L{l}.parquet', columns=['paper_id'] + [f'dropped_{k}' for k in KS]).set_index('paper_id')
        Xs, D1, D5, PID, Ys = [], [], [], [], []
        for f in shards:
            zt = np.load(f); rid = zt['row_id']
            sel = (tok.role.reindex(rid).to_numpy() == 'surname_first'); r = rid[sel]
            ht = zt[f'resid_L{l}'][sel].astype(np.float32)
            pid = tok.paper_id.reindex(r).to_numpy()
            dmask = np.stack([~pp[f'dropped_{k}'].reindex(pid).fillna(True).to_numpy().astype(bool) for k in KS], 1)   # usable
            fs = np.zeros_like(ht); f5 = np.zeros_like(ht)
            for k in KS:
                zf = np.load(RAW / f'false_{k}' / f.name)
                if not np.array_equal(zf['row_id'], rid): raise SystemExit(f'row_id mismatch {f.name} false_{k}')
                hf = zf[f'resid_L{l}'][sel].astype(np.float32); f5 += hf; fs += hf * dmask[:, k:k + 1]
            nu = dmask.sum(1, keepdims=True)
            with np.errstate(invalid='ignore', divide='ignore'): d1 = ht - fs / nu
            D1.append(d1); D5.append(ht - f5 / 5); Xs.append(ht); PID.append(pid)
            if l not in y63:
                zy = np.load(R13 / 'raw/allTok_L63' / f.name)
                yp = pd.Series(np.arange(len(zy['row_id'])), index=zy['row_id']).reindex(r)
                if yp.isna().any(): raise SystemExit('missing L63 rows')
                Ys.append(zy['resid'][yp.to_numpy().astype(int)].astype(np.float32))
        X = np.concatenate(Xs); D1 = np.concatenate(D1); D5 = np.concatenate(D5); PID = np.concatenate(PID)
        Y = np.concatenate(Ys) if Ys else y63['Y']
        y63['Y'] = Y
        log(f'L{l}: {len(X)} surname_first rows')
        # ridge map as published (single full fit)
        mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; G = A.T @ A; Bm = A.T @ (Y - Y.mean(0))
        W = np.linalg.solve(G + 1.0 * np.trace(G) / G.shape[0] * np.eye(G.shape[0], dtype=np.float32), Bm); del A, G, Bm
        Q = (W / sd[:, None]) * nw[None, :] @ U.T                                                   # 5120 x n_names
        del X, W
        out = {}
        for vname, D in [('Vpd (usable false titles)', D1), ('all 5 false titles', D5)]:
            df = pd.DataFrame(D); df['paper_id'] = PID
            ok = np.isfinite(D).all(1); dp = df[ok].groupby('paper_id').mean()
            g = grp.reindex(dp.index).to_numpy(); T = dp[g == 'target'].to_numpy(); C = dp[g == 'control'].to_numpy()
            pT, pC = dp.index[g == 'target'], dp.index[g == 'control']
            mC = C.mean(0); Delta = T.mean(0) - mC; DT = T - mC
            # main: uncentered second moment of DT
            Uu, s, Vt = np.linalg.svd(DT, full_matrices=False); ev = s ** 2
            # (a) pooled centered, (c) DT centered
            Pd = np.vstack([T, C]); Pd = Pd - Pd.mean(0); _, sa, Vta = np.linalg.svd(Pd, full_matrices=False); eva = sa ** 2
            DTc = DT - DT.mean(0); _, sc, _ = np.linalg.svd(DTc, full_matrices=False); evc = sc ** 2
            def share(vec_or_mat, V, k):
                M = vec_or_mat[:, None] if vec_or_mat.ndim == 1 else vec_or_mat
                P = V[:k] @ M; return float((P ** 2).sum() / (M ** 2).sum())
            r = dict(n_target=int(len(T)), n_control=int(len(C)),
                     main_ev10=[float(x) for x in ev[:10] / ev.sum()], main_cum10=[float(x) for x in np.cumsum(ev[:10]) / ev.sum()],
                     main_n50=n_to(ev, .5), main_n80=n_to(ev, .8), main_pr=float(ev.sum() ** 2 / (ev ** 2).sum()),
                     pooled_ev10=[float(x) for x in eva[:10] / eva.sum()], pooled_n50=n_to(eva, .5), pooled_n80=n_to(eva, .8), pooled_pr=float(eva.sum() ** 2 / (eva ** 2).sum()),
                     dtc_ev10=[float(x) for x in evc[:10] / evc.sum()], dtc_n50=n_to(evc, .5), dtc_n80=n_to(evc, .8),
                     delta_norm=float(np.linalg.norm(Delta)), dt_rms_norm=float(np.sqrt((DT ** 2).sum(1).mean())),
                     delta_share_mainPC={k: share(Delta, Vt, k) for k in KLIST}, delta_share_pooledPC={k: share(Delta, Vta, k) for k in KLIST},
                     probeQ_share_mainPC={k: share(Q, Vt, k) for k in KLIST}, probeQ_share_pooledPC={k: share(Q, Vta, k) for k in KLIST},
                     random_expect={k: k / D.shape[1] for k in KLIST})
            if vname.startswith('Vpd'):
                # team bootstrap of main n50 / n80 (eigenvalues of weighted gram)
                tT = pd.factorize(pd.Series([TEAM[p] for p in list(pT) + list(pC)]))[0]; nTe = tT.max() + 1
                Gt = T @ T.T; rng = np.random.default_rng(1120); n50, n80 = [], []
                tb = time.monotonic()
                for b in range(a.nb):
                    if time.monotonic() - tb > a.budget_min * 60: break
                    cnt = rng.multinomial(nTe, np.full(nTe, 1 / nTe)).astype(np.float64); w = cnt[tT]; wT, wC = w[:len(T)], w[len(T):]
                    if wC.sum() == 0 or wT.sum() == 0: continue
                    m = (wC @ C) / wC.sum(); v = T @ m; K = Gt - v[:, None] - v[None, :] + m @ m
                    sq = np.sqrt(wT); e = np.linalg.eigvalsh(K * sq[:, None] * sq[None, :]); e = np.clip(e[::-1], 0, None)
                    n50.append(n_to(e, .5)); n80.append(n_to(e, .8))
                r['boot_draws'] = len(n50)
                if n50: r['main_n50_ci'] = [float(np.percentile(n50, 2.5)), float(np.percentile(n50, 97.5))]; r['main_n80_ci'] = [float(np.percentile(n80, 2.5)), float(np.percentile(n80, 97.5))]
                log(f'L{l} boot {len(n50)} draws')
            out[vname] = r
            for i in range(10): rows_out.append(dict(layer=l, version=vname, pc=i + 1, main_var=r['main_ev10'][i], main_cum=r['main_cum10'][i], pooled_var=r['pooled_ev10'][i], dtc_var=r['dtc_ev10'][i]))
            log(f'L{l} {vname}: nT {len(T)} nC {len(C)} n50 {r["main_n50"]} n80 {r["main_n80"]} PR {r["main_pr"]:.1f}')
        res['layers'][l] = out
    json.dump(res, open(OUT / 'pca_results.json', 'w'), indent=1)
    pd.DataFrame(rows_out).to_csv(OUT / 'pca_top10.csv', index=False)
    L = [f'# Name-position PCA of target − control differences — exploratory (post hoc, not pre-registered)', '', res['definition'], '']
    for l, out in res['layers'].items():
        for vname, r in out.items():
            L += [f'## L{l} · {vname} · n_T {r["n_target"]} / n_C {r["n_control"]}', '',
                  'PC 1–10 variance share (main, uncentered D_T): ' + ', '.join(f'{x:.3f}' for x in r['main_ev10']),
                  'cumulative: ' + ', '.join(f'{x:.3f}' for x in r['main_cum10']),
                  f'#PCs to 50% / 80%: {r["main_n50"]} / {r["main_n80"]}' + (f' (team bootstrap {r["boot_draws"]} draws: 50% {r.get("main_n50_ci")}, 80% {r.get("main_n80_ci")})' if 'boot_draws' in r else '') + f'; participation ratio {r["main_pr"]:.1f}',
                  f'(c) centered D_T: PC1–10 ' + ', '.join(f'{x:.3f}' for x in r['dtc_ev10']) + f'; 50%/80% {r["dtc_n50"]}/{r["dtc_n80"]}',
                  f'(a) pooled centered d: PC1–10 ' + ', '.join(f'{x:.3f}' for x in r['pooled_ev10']) + f'; 50%/80% {r["pooled_n50"]}/{r["pooled_n80"]}; PR {r["pooled_pr"]:.1f}',
                  f'|Delta| {r["delta_norm"]:.3f} vs RMS |D_T row| {r["dt_rms_norm"]:.3f}',
                  '(b) share in top-k PCs (k = ' + ', '.join(map(str, KLIST)) + '): Delta/main ' + ', '.join(f'{r["delta_share_mainPC"][k]:.3f}' for k in KLIST)
                  + ' · Delta/pooled ' + ', '.join(f'{r["delta_share_pooledPC"][k]:.3f}' for k in KLIST)
                  + ' · probe Q/main ' + ', '.join(f'{r["probeQ_share_mainPC"][k]:.3f}' for k in KLIST)
                  + ' · probe Q/pooled ' + ', '.join(f'{r["probeQ_share_pooledPC"][k]:.3f}' for k in KLIST)
                  + ' · random ' + ', '.join(f'{r["random_expect"][k]:.4f}' for k in KLIST), '']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('DONE', OUT)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); ap.add_argument('--nb', type=int, default=200)
    ap.add_argument('--budget-min', type=float, default=32); main(ap.parse_args())
