"""Stage 13 batch 1 item 1 (config/prereg_addendum10.json, 'X2 subspace'): refit S_auth on ALL authors' name tokens.

Same rule as addendum 6 / stage13_x2_fit.py (functions loaded from that frozen file by path, not edited): M3 residual
cache (authors prompt without year, title_last) at L16/24/32/40/48; training papers = cohort papers whose archived team
contains none of the 1,178 pair papers' A, B, C; 5-fold group CV on the archived team folds; ridge with alpha from
ALPHAS by pooled held-out 1 - R^2; refit on all training papers; S_auth_all = top-10 left singular vectors of the
5120 x 5120 raw-coordinate map (input = residual side), k = 10.
Target (the only change): per paper, the mean over its authors of the mean W_U row over that author's name tokens (all
roles, cohort/name_tokens). With the same X for every token of a paper, regressing on the per-author-mean target is the
"all authors, equal weight per author" version of the stacked-token ridge.
Sanity (summary_b1_xall/fit_authall_sanity.csv): held-out R^2 of the map, principal-angle cosines with the old S_auth and
with S_id, share of ||h_A - h_B||^2 (pair A vs partner B, title_last) captured.
Usage: python stage13_b1_xall_fit.py [--tiny]
Outputs: summary_b1_xall/subspaces_authall_L{l}.npz (S_auth_all [5120, 10] fp32, ...)."""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT0 = B / '381_stage13'
TINY = '--tiny' in sys.argv
ROOT = ROOT0 / 'b1_xall_tiny' if TINY else ROOT0
OLD_SUB = (ROOT0 / 'x2_tiny/summary_x2') if TINY else (ROOT0 / 'summary_x2')
OUT = ROOT / 'summary_b1_xall'
K = 10


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


x2f = load(H / '13_stage13/stage13_x2_fit.py', 'x2f')          # TINY flag inside it is read from sys.argv too
LAYERS = x2f.LAYERS; CACHE_LAYERS = x2f.CACHE_LAYERS
log = x2f.log


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    z = np.load(ROOT0 / 'summary_cpu_teamci/folds_own9108_k5s13.npz'); ids = z['ids'].astype(str); team = z['team']; fold = z['fold']
    pairs = pd.read_parquet(ROOT0 / 'config/pairs.parquet')
    used = set(pairs.paper_id) | set(pairs.partner) | set(pairs.random_c); T = dict(zip(ids, team)); bad = {T[x] for x in used}
    tr = np.array([T[x] not in bad for x in ids]); tr_idx = np.where(tr)[0]
    log(f'pair papers (A, B, C) {len(used)} in {len(bad)} teams; training papers {tr.sum()} of {len(ids)}')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index', 'token_id'])
    pa = pairs[pairs.paper_id.isin(ids)]; ia = pd.Index(ids).get_indexer(pa.paper_id); ib = pd.Index(ids).get_indexer(pa.partner)
    if TINY:
        x2 = load(H / '13_stage13/stage13_x2.py', 'x2'); C = x2.tiny_ctx(); s13 = x2.s13
        tr_idx = tr_idx[:400]; ia, ib = ia[:30], ib[:30]
        need = sorted(set(tr_idx) | set(ia) | set(ib)); Xall = {}
        for i in need:
            full, it, _ = s13.build(C.tok, papers.loc[ids[i]].title, 'authors', []); a = C.record(full, LAYERS)
            Xall[i] = np.stack([a[l][it].float().numpy() for l in LAYERS])
        get = lambda idx, li: np.stack([Xall[i][li] for i in idx]).astype(np.float64)
        WU = C.hf.lm_head.weight.detach().float().numpy()
    else:
        shp = (len(ids), 3, len(CACHE_LAYERS), 2, 5120)
        mm = np.memmap(ROOT0 / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=shp)
        assert (np.load(ROOT0 / 'summary_m3/resid_cache_pids.npy', allow_pickle=True).astype(str) == ids).all()
        get = lambda idx, li: np.asarray(mm[np.sort(idx), 0, CACHE_LAYERS.index(LAYERS[li]), 0, :], np.float64)[np.argsort(np.argsort(idx))]
        from safetensors import safe_open
        wm = json.load(open(x2f.SNAP / 'model.safetensors.index.json'))['weight_map']
        with safe_open(x2f.SNAP / wm['lm_head.weight'], 'pt') as f: WU = f.get_tensor('lm_head.weight').float().numpy()
        log('W_U', WU.shape)
    tids = ids[tr_idx]
    sub = nt[nt.paper_id.isin(set(tids))]
    # per paper: mean over authors of (mean W_U row over the author's tokens)
    Y = np.zeros((len(tids), WU.shape[1])); pos = {p: i for i, p in enumerate(tids)}; nauth = np.zeros(len(tids)); ntok = np.zeros(len(tids))
    for (pid, ai), g in sub.groupby(['paper_id', 'author_index']):
        i = pos[pid]; Y[i] += WU[g.token_id.to_numpy()].astype(np.float64).mean(0); nauth[i] += 1; ntok[i] += len(g)
    assert (nauth > 0).all(), 'training paper without name tokens'
    Y /= nauth[:, None]
    log(f'targets: {len(tids)} papers, authors per paper mean {nauth.mean():.2f}, name tokens per paper mean {ntok.mean():.2f}')
    fam = dict(auth=list(range(Y.shape[1]))); folds = fold[tr_idx]; rows = []
    for li, l in enumerate(LAYERS):
        t0 = time.time(); X = get(tr_idx, li); log(f'L{l}: X {X.shape}')
        best, Pb, cv = x2f.ridge_cv_svd(X, Y, folds, fam)
        Wr, mu, sd = x2f.ridge_full(X, Y, fam, best)
        U, sv, _ = np.linalg.svd(Wr, full_matrices=False); S_new = U[:, :K]
        old = np.load(OLD_SUB / f'subspaces_L{l}.npz')
        cos_old = np.linalg.svd(old['S_auth'].astype(np.float64).T @ S_new, compute_uv=False)
        cos_id = np.linalg.svd(old['S_id'].astype(np.float64).T @ S_new, compute_uv=False)
        D = get(ia, li) - get(ib, li); e2 = (D ** 2).sum(1)
        cap = {nm: float(np.mean(((D @ S) ** 2).sum(1) / e2)) for nm, S in (('auth_all', S_new), ('auth_old', old['S_auth'].astype(np.float64)))}
        np.savez(OUT / f'subspaces_authall_L{l}.npz', S_auth_all=S_new.astype(np.float32), layer=l, alpha=best['auth'], train_ids=tids,
                 auth_singular_values=sv[:50], cos_with_old_auth=cos_old, cos_with_id=cos_id, cv_nmse=json.dumps({f'{f}@{a}': v for (f, a), v in cv.items()}),
                 capture_pairs=json.dumps(cap), target='mean over authors of mean W_U row over the author name tokens (all roles)')
        r = dict(layer=l, n_train=len(tids), alpha_auth=best['auth'], authall_r2=1 - cv['auth', best['auth']], cos_old_max=float(cos_old.max()),
                 cos_old_mean=float(cos_old.mean()), cos_id_max=float(cos_id.max()), sv_top10_share=float((sv[:K] ** 2).sum() / (sv ** 2).sum()),
                 **{f'capture_{k}': v for k, v in cap.items()})
        rows.append(r); log(f'L{l} done ({time.time() - t0:.0f}s): ' + json.dumps(r))
    pd.DataFrame(rows).to_csv(OUT / 'fit_authall_sanity.csv', index=False); log('FIT AUTHALL DONE', OUT)


if __name__ == '__main__':
    main()
