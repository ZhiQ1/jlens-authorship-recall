"""Batch 3 (addendum 14): pure check / estimator functions shared by the b3 GPU and analysis scripts (unit-tested in
stage13_b3_unittest.py). No file I/O except where a function says so.

bf16 unit ("ulp") of a logit value x: 2**(floor(log2|x|) - 7) (bf16 keeps 8 significant bits); |x| in [32, 64) -> 0.25.
ulps_to_rank: the smallest shift of the gold logit, in bf16 units of the gold logit, that turns the new rank into the stored
rank (rank = 1 + number of vocabulary logits strictly greater than the gold logit, as 351_stage10.score). 0 = same rank;
inf = the stored rank cannot be reached by moving the gold logit alone (tied competitors).
"""
import math
import numpy as np


def bf16_ulp(x):
    x = np.abs(np.asarray(x, np.float64)); x = np.where(x < 2.0 ** -126, 2.0 ** -126, x)
    return np.exp2(np.floor(np.log2(x)) - 7)


def ulps_to_rank_np(row, gold, target_rank):
    """numpy version (tests / CPU). row: [V] float logits; gold: token id; target_rank: stored rank (>= 1)."""
    row = np.asarray(row, np.float64); g = row[gold]
    o = np.sort(np.delete(row, gold))[::-1]                    # other logits, descending; o[i-1] = i-th largest
    r = int(target_rank); V = len(row)
    upper = o[r - 2] if r >= 2 else math.inf                   # need g' <  upper (exactly r-1 others strictly greater)
    lower = o[r - 1] if r - 1 < len(o) else -math.inf          # need g' >= lower
    if not lower < upper: return math.inf
    if lower <= g < upper: return 0.0
    u = float(bf16_ulp(g))
    if g < lower: return float((lower - g) / u)
    return float((g - upper) / u + 1.0)                        # move strictly below 'upper': one more unit


def ulps_to_rank_torch(logits, gold, target_rank, torch):
    """torch version for the GPU jobs. logits [n, V] float; gold [n] long; target_rank [n] long. Returns float64 numpy [n]."""
    out = np.zeros(len(gold), np.float64)
    for i in range(len(gold)):
        row = logits[i]; gi = int(gold[i]); r = int(target_rank[i])
        g = float(row[gi])
        o = torch.sort(torch.cat([row[:gi], row[gi + 1:]]), descending=True).values
        upper = float(o[r - 2]) if r >= 2 else math.inf
        lower = float(o[r - 1]) if r - 1 < o.numel() else -math.inf
        if not lower < upper: out[i] = math.inf; continue
        if lower <= g < upper: out[i] = 0.0; continue
        u = float(bf16_ulp(g))
        out[i] = (lower - g) / u if g < lower else (g - upper) / u + 1.0
    return out


def rank_match(new_rank, ref_rank, ulps=None, dlogprob=None, ulps_max=4, exact_min=0.99):
    """Plan 3-1/3-2: exact on >= exact_min of tokens AND every other token within ulps_max bf16 units. Returns dict."""
    new_rank = np.asarray(new_rank); ref_rank = np.asarray(ref_rank)
    n = len(new_rank); ex = new_rank == ref_rank; nm = int((~ex).sum())
    u = np.zeros(n) if ulps is None else np.asarray(ulps, np.float64)
    um = u[~ex]
    within = int(np.sum(um <= ulps_max)) if nm else 0
    share = float(ex.mean()) if n else float('nan')
    d10 = np.abs(np.log10(new_rank.astype(float)) - np.log10(ref_rank.astype(float))) if n else np.array([0.0])
    res = dict(n_tokens=int(n), n_exact=int(ex.sum()), share_exact=share, n_mismatch=nm, n_mismatch_le_ulps=within,
               max_ulps=float(np.max(um)) if nm else 0.0, median_ulps_mismatch=float(np.median(um)) if nm else 0.0,
               max_abs_dlogprob=float(np.nanmax(np.abs(dlogprob))) if dlogprob is not None and len(dlogprob) else float('nan'),
               max_abs_dlog10rank=float(d10.max()) if n else 0.0)
    ok = n > 0 and share >= exact_min and within == nm
    res['status'] = 'PASS' if ok else 'FAIL'
    return res


# ---------------------------------------------------------------- paper-level title-specific signal (Stage 10 definitions)
def paper_means(pid_codes, n_papers, values, mask=None):
    """token-weighted per-paper mean (351_stage10.paper_scores mean_nlr); NaN for papers without tokens in mask."""
    m = np.ones(len(values), bool) if mask is None else mask
    cnt = np.bincount(pid_codes[m], minlength=n_papers).astype(float)
    s = np.bincount(pid_codes[m], weights=np.asarray(values, float)[m], minlength=n_papers)
    with np.errstate(invalid='ignore', divide='ignore'): return s / cnt


def nlr(rank): return -np.log10(np.asarray(rank, np.float64))


def spec_total_topic(level):
    """level: {cond: [P] paper means}. spec = true - mean(false_k); total = true - delete; topic = mean false - delete."""
    f = np.mean([level[f'false_{k}'] for k in range(5)], 0)
    out = dict(true=level['true'], spec=level['true'] - f, false=f)
    if 'delete' in level: out['total'] = level['true'] - level['delete']; out['topic'] = f - level['delete']
    return out


def within_bin_point(v, grp, cbin, a='target', b='control', min_n=30):
    """point estimate of 351_stage10.stratified_diff (bins with >= min_n papers in both groups; weights n_a n_b/(n_a+n_b))."""
    v = np.asarray(v, float); cells = []
    for s in sorted(set(cbin)):
        A = v[(cbin == s) & (grp == a)]; B = v[(cbin == s) & (grp == b)]
        A = A[~np.isnan(A)]; B = B[~np.isnan(B)]
        if len(A) >= min_n and len(B) >= min_n: cells.append((A, B))
    if not cells: return float('nan'), 0
    w = np.array([len(A) * len(B) / (len(A) + len(B)) for A, B in cells]); w = w / w.sum()
    return float(sum(wi * (np.nanmean(A) - np.nanmean(B)) for wi, (A, B) in zip(w, cells))), len(cells)


def scalar_check(name, value, ref, tol, kind='HARD', scope='', note=''):
    d = abs(value - ref) if np.isfinite(value) and np.isfinite(ref) else float('inf')
    return dict(check=name, scope=scope, value=float(d), threshold=float(tol), status='PASS' if d <= tol else ('FAIL' if kind == 'HARD' else 'WARN'),
                kind=kind, note=note or f'new {value:.6f} vs published {ref:.6f}')


# ---------------------------------------------------------------- team-cluster bootstrap (as stage13_alltok_report)
def team_weights(team_codes, NB, seed):
    codes, uniq = team_codes
    n = len(uniq)
    return np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)[:, codes]


def factor_teams(pids, TEAM):
    import pandas as pd
    codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in pids])); return codes, uniq


def mean_cluster_w(x, W):
    """mean of x and percentile CI from team weights W [NB, n] (NaN entries dropped)."""
    x = np.asarray(x, float); ok = ~np.isnan(x)
    if ok.sum() == 0: return float('nan'), float('nan'), float('nan'), 0
    Wk = W[:, ok]; xk = x[ok]
    bt = (Wk @ xk) / np.maximum(Wk.sum(1), 1e-9)
    lo, hi = np.percentile(bt, [2.5, 97.5]); return float(xk.mean()), float(lo), float(hi), int(ok.sum())


def strat_cluster_w(x, grp, cbin, W, a='target', b='control', min_n=30):
    """within-bin a - b with the same team draws (as stage13_alltok_report.strat_cluster)."""
    x = np.asarray(x, float); cells = []
    for s in sorted(set(cbin)):
        ia = np.nonzero((cbin == s) & (grp == a) & ~np.isnan(x))[0]; ib = np.nonzero((cbin == s) & (grp == b) & ~np.isnan(x))[0]
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return float('nan'), float('nan'), float('nan'), 0, 0, 0
    w = np.array([len(p) * len(q) / (len(p) + len(q)) for p, q in cells]); w /= w.sum()
    est = sum(wi * (x[p].mean() - x[q].mean()) for wi, (p, q) in zip(w, cells)); bt = np.zeros(W.shape[0])
    for wi, (p, q) in zip(w, cells):
        bt += wi * ((W[:, p] @ x[p]) / np.maximum(W[:, p].sum(1), 1e-9) - (W[:, q] @ x[q]) / np.maximum(W[:, q].sum(1), 1e-9))
    lo, hi = np.percentile(bt, [2.5, 97.5])
    return float(est), float(lo), float(hi), len(cells), int(sum(len(p) for p, _ in cells)), int(sum(len(q) for _, q in cells))


def onset(layers, lo, hi):
    """first layer (in the given grid order) whose CI excludes 0; its sign; first layer with lo > 0; first layer from which
    lo > 0 holds at every later grid layer (sustained)."""
    layers = list(layers); lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    ex = [i for i in range(len(layers)) if lo[i] > 0 or hi[i] < 0]
    pos = [i for i in range(len(layers)) if lo[i] > 0]
    sus = next((i for i in range(len(layers)) if all(lo[j] > 0 for j in range(i, len(layers)))), None)
    return (layers[ex[0]] if ex else None, ('+' if lo[ex[0]] > 0 else '-') if ex else '', layers[pos[0]] if pos else None,
            layers[sus] if sus is not None else None)
