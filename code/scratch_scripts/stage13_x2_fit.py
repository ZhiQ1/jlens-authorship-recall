"""Stage 13 X2 step (a): fit the subspaces per layer (rules: config/prereg_addendum6.json, 'subspaces').

Data: M3 residual cache summary_m3/resid_cache.f16 [9108, task, layer, pos, 5120] fp16, task = authors (prompt without
year), pos = title_last, at the same layer l in [16, 24, 32, 40, 48].
Training papers: all cohort papers whose author team (archived 9,108-paper team ids, summary_cpu_teamci/
folds_own9108_k5s13.npz; papers sharing any full author name = one team) contains none of the 1,178 X1 pair papers'
A, B or C papers. 5-fold group CV = the archived team folds restricted to the training papers (whole teams per fold).
Ridge (as stage13_cpu / M3: features standardised on the training rows, penalty alpha * trace(A'A)/d, intercept), alpha
per target family chosen by the pooled 5-fold held-out normalised MSE from ALPHAS, then refitted on all training papers.
Directions are expressed in raw residual coordinates (w_raw = w_std / sd: the readout direction, which is what a patch
along it changes) before orthonormalisation.
  S_id  : ridge weight vectors for year, log10(1 + citations), field (8 one-vs-rest, one alpha) -> QR. The 8 field
          weights of a one-hot ridge with a shared alpha sum to exactly 0 (centred one-hot rows sum to 0), so the 10
          vectors have rank 9: S_id keeps the 9 independent QR directions (deviation from k = 10, recorded).
  S_auth: ridge map residual -> W_U row (lm_head) of the paper's first-author first name token (cohort/name_tokens,
          author_index 0, token_index 0), 5120 -> 5120; S_auth = top-10 singular directions of the map on the INPUT
          (residual) side (with y = x M: left singular vectors of M = right singular vectors of the operator x -> M'x).
  S_rand: 3 random Gaussian 10-dim subspaces (seeds 61, 62, 63) -> QR.
  mu    : mean title-last state of the training papers (raw, fp32).
Sanity (printed + summary_x2/fit_sanity.csv): held-out R^2 (year, log citations), field accuracy, author-map R^2 and
top-1 accuracy of the predicted W_U row among the candidate first tokens; principal-angle cosines S_id vs S_auth; share
of ||h_A - h_B||^2 (pair papers A vs partner B, title_last, from the cache) captured by each subspace.
Usage: python stage13_x2_fit.py [--tiny]  (--tiny: 2-layer random Qwen3, states recorded on CPU for 400 training
papers + 30 pairs, W_U from the tiny model; writes x2_tiny/summary_x2)"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TINY = '--tiny' in sys.argv
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
LAYERS = [0, 1] if TINY else [16, 24, 32, 40, 48]
CACHE_LAYERS = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]
SNAP = Path('/scratch/zhang.zhiqi2/hf/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137')
K = 10


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def ridge_cv_svd(X, Y, folds, fam, alphas=ALPHAS):
    """X [n, d] fp64, Y [n, q], fam: {family: column indices}. Returns {family: alpha}, held-out predictions per
    family at its alpha [n, q], and the CV table (normalised MSE per family and alpha)."""
    n, q = Y.shape; P = {a: np.zeros((n, q)) for a in alphas}
    for k in np.unique(folds):
        tr, te = folds != k, folds == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; A = (X[tr] - mu) / sd; ym = Y[tr].mean(0)
        U, s, Vt = np.linalg.svd(A, full_matrices=False); sc = (s ** 2).sum() / A.shape[1]
        UtY = U.T @ (Y[tr] - ym); Z = ((X[te] - mu) / sd) @ Vt.T
        for a in alphas: P[a][te] = (Z * (s / (s ** 2 + a * sc))) @ UtY + ym
        log(f'  fold {k}: train {tr.sum()}, test {te.sum()}')
    var = Y.var(0) + 1e-12; cv = {}; best = {}; Pb = np.zeros((n, q))
    for f, cols in fam.items():
        for a in alphas:
            e = ((P[a][:, cols] - Y[:, cols]) ** 2).mean(0)
            cv[f, a] = float((e / var[cols]).mean()) if f != 'auth' else float(e.sum() / var[cols].sum())   # auth: pooled 1 - R^2
        best[f] = min(alphas, key=lambda a: cv[f, a]); Pb[:, cols] = P[best[f]][:, cols]
    return best, Pb, cv


def ridge_full(X, Y, fam, best):
    mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; ym = Y.mean(0)
    U, s, Vt = np.linalg.svd(A, full_matrices=False); sc = (s ** 2).sum() / A.shape[1]; UtY = U.T @ (Y - ym)
    W = np.zeros((X.shape[1], Y.shape[1]))
    for f, cols in fam.items(): W[:, cols] = Vt.T @ ((s / (s ** 2 + best[f] * sc))[:, None] * UtY[:, cols])
    return W / sd[:, None], mu, sd                                              # raw-coordinate weights


def orthonormal(M, tol=1e-6):
    Q, R = np.linalg.qr(M / np.linalg.norm(M, axis=0, keepdims=True)); d = np.abs(np.diag(R))
    keep = d > tol * d.max(); return Q[:, keep], d


def r2(y, p): return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main():
    sys.path.insert(0, str(H / '13_stage13'))
    if TINY:
        import stage13_x2 as x2
        OUT = x2.roots(True)['sub']
    else:
        OUT = ROOT / 'summary_x2'
    OUT.mkdir(parents=True, exist_ok=True)
    z = np.load(ROOT / 'summary_cpu_teamci/folds_own9108_k5s13.npz'); ids = z['ids'].astype(str); team = z['team']; fold = z['fold']
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')
    used = set(pairs.paper_id) | set(pairs.partner) | set(pairs.random_c); T = dict(zip(ids, team)); bad = {T[x] for x in used}
    tr = np.array([T[x] not in bad for x in ids])
    log(f'pair papers (A, B, C) {len(used)} in {len(bad)} teams; training papers {tr.sum()} of {len(ids)}')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index', 'token_id'])
    first_tok = nt[(nt.author_index == 0) & (nt.token_index == 0)].set_index('paper_id').token_id
    tr_idx = np.where(tr)[0]
    pa = pairs[pairs.paper_id.isin(ids)]; ia = pd.Index(ids).get_indexer(pa.paper_id); ib = pd.Index(ids).get_indexer(pa.partner)
    if TINY:
        C = x2.tiny_ctx(); s13 = x2.s13; torch = C.torch
        tr_idx = tr_idx[:400]; ia, ib = ia[:30], ib[:30]
        bad_ctx = [p for p in pa.paper_id[:30] if p in C.ctx and C.ctx[p][0][2][0] != first_tok[p]]
        log(('OK' if not bad_ctx else 'WARN') + f' name_tokens first token == C.ctx first author first token for {30 - len(bad_ctx)}/30 pair papers')
        need = sorted(set(tr_idx) | set(ia) | set(ib)); Xall = {}
        for i in need:
            pid = ids[i]; full, it, _ = s13.build(C.tok, papers.loc[pid].title, 'authors', []); a = C.record(full, LAYERS)
            Xall[i] = np.stack([a[l][it].float().numpy() for l in LAYERS])
        get = lambda idx, li: np.stack([Xall[i][li] for i in idx]).astype(np.float64)
        WU = C.hf.lm_head.weight.detach().float().numpy()
    else:
        shp = (len(ids), 3, len(CACHE_LAYERS), 2, 5120)
        mm = np.memmap(ROOT / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=shp)
        assert (np.load(ROOT / 'summary_m3/resid_cache_pids.npy', allow_pickle=True).astype(str) == ids).all()
        get = lambda idx, li: np.asarray(mm[np.sort(idx), 0, CACHE_LAYERS.index(LAYERS[li]), 0, :], np.float64)[np.argsort(np.argsort(idx))]
        from safetensors import safe_open
        wm = json.load(open(SNAP / 'model.safetensors.index.json'))['weight_map']
        with safe_open(SNAP / wm['lm_head.weight'], 'pt') as f: WU = f.get_tensor('lm_head.weight').float().numpy()
        log('W_U', WU.shape)
    tids = ids[tr_idx]; P = papers.loc[tids]
    fields = sorted(papers.field.unique()); F = (P.field.to_numpy()[:, None] == np.array(fields)[None]).astype(float)
    tokv = first_tok.loc[tids].to_numpy()
    Yid = np.column_stack([P.year.to_numpy(float), np.log10(1 + P.citations.to_numpy(float)), F])
    Yau = WU[tokv].astype(np.float64); Y = np.hstack([Yid, Yau]); q0 = Yid.shape[1]
    fam = dict(year=[0], logcit=[1], field=list(range(2, q0)), auth=list(range(q0, Y.shape[1])))
    folds = fold[tr_idx]; log('training folds', np.bincount(folds), 'fields', fields)
    cand = np.unique(tokv); Wc = WU[cand].astype(np.float64); true_c = np.searchsorted(cand, tokv)
    rows = []
    for li, l in enumerate(LAYERS):
        t0 = time.time(); X = get(tr_idx, li); log(f'L{l}: X {X.shape}')
        best, Pb, cv = ridge_cv_svd(X, Y, folds, fam)
        sc = dict(year_r2=r2(Y[:, 0], Pb[:, 0]), logcit_r2=r2(Y[:, 1], Pb[:, 1]), field_acc=float((Pb[:, 2:q0].argmax(1) == F.argmax(1)).mean()),
                  auth_r2=1 - cv['auth', best['auth']], auth_top1=float(((Pb[:, q0:] @ Wc.T).argmax(1) == true_c).mean()),
                  auth_top1_majority=float(np.bincount(true_c).max() / len(true_c)), n_candidates=len(cand))
        Wr, mu, sd = ridge_full(X, Y, fam, best)
        S_id, rdiag = orthonormal(Wr[:, :q0])
        U, sv, _ = np.linalg.svd(Wr[:, q0:], full_matrices=False); S_auth = U[:, :K]
        S_rand = np.stack([np.linalg.qr(np.random.default_rng(s).standard_normal((X.shape[1], K)))[0] for s in (61, 62, 63)])
        ang = np.linalg.svd(S_id.T @ S_auth, compute_uv=False)
        D = get(ia, li) - get(ib, li); e2 = (D ** 2).sum(1)
        cap = {nm: float(np.mean(((D @ S) ** 2).sum(1) / e2)) for nm, S in [('id', S_id), ('auth', S_auth)] + [(f'rand{s}', S_rand[i]) for i, s in enumerate((61, 62, 63))]}
        np.savez(OUT / f'subspaces_L{l}.npz', S_id=S_id.astype(np.float32), S_auth=S_auth.astype(np.float32), S_rand=S_rand.astype(np.float32),
                 mu=mu.astype(np.float32), sd=sd.astype(np.float32), train_ids=tids, train_folds=folds, layer=l, rank_id=S_id.shape[1], id_qr_rdiag=rdiag,
                 auth_singular_values=sv[:50], id_auth_cosines=ang, alphas=json.dumps(best), cv_nmse=json.dumps({f'{f}@{a}': v for (f, a), v in cv.items()}),
                 cv_scores=json.dumps(sc), capture_pairs=json.dumps(cap), fields=np.array(fields))
        rows.append(dict(layer=l, n_train=len(tids), rank_id=S_id.shape[1], **{f'alpha_{k}': v for k, v in best.items()}, **sc,
                         id_auth_cos_max=float(ang.max()), id_auth_cos_mean=float(ang.mean()), **{f'capture_{k}': v for k, v in cap.items()},
                         auth_sv_top10_share=float((sv[:K] ** 2).sum() / (sv ** 2).sum())))
        log(f'L{l} done ({time.time() - t0:.0f}s): alphas {best}; held-out year R2 {sc["year_r2"]:.3f}, log cit R2 {sc["logcit_r2"]:.3f}, field acc {sc["field_acc"]:.3f}, '
            f'author map R2 {sc["auth_r2"]:.4f}, author top-1 {sc["auth_top1"]:.3f} (majority {sc["auth_top1_majority"]:.3f}, {len(cand)} candidates); '
            f'rank S_id {S_id.shape[1]} (QR |R_ii| {np.round(rdiag, 4).tolist()}); cos(S_id, S_auth) max {ang.max():.3f}; '
            f'capture of ||h_A - h_B||^2: ' + ', '.join(f'{k} {v:.4f}' for k, v in cap.items()) + f' (random expectation {K / X.shape[1]:.4f})')
    pd.DataFrame(rows).to_csv(OUT / 'fit_sanity.csv', index=False); log('FIT DONE', OUT)


if __name__ == '__main__':
    main()
