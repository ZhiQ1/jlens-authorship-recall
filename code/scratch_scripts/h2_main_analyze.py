#!/usr/bin/env python3
"""Addendum 20 (LOCKED 2026-11-20) main experiment, step 3 (CPU): analysis exactly as locked.

Inputs: a20_freeze/fict_titles.parquet; raw/a20_score, a20_patch, a20_titlepos, a20_parity (this run);
Stage 10 stored raw (true, false_0..4: final L63, logit / jlens_public L24..62), Stage 11 stored E1 patch (true run)
and titlepos (true residuals, 9,108 papers) + probe_vocab; selected_v3b.csv (cosines, Crossref overlap, word counts).

Per paper i, readout r, layer l, condition c: S_c = mean over all scored name tokens of log10(1/rank) (Stage 10 mean_nlr).
  F = mean(S_false_0..4); G = S_true - F; A = S_fict - F; R = S_true - S_fict.
Primary (target, final L63): phi_T = sum A / sum G (ratio of sums, recomputed on every draw), Rbar_T = mean R.
CIs: author-team cluster bootstrap, 2,000 draws (groups_core.Engine: team ids from the archived folds_own9108_k5s13.npz;
multinomial over teams; seed 20261120), percentile 95 %.
Decision rule: addendum 20 section 3 (verdict from the point estimate phi_T, read only when the Rbar_T CI is entirely above 0;
"borderline" when the phi_T CI crosses 0.3 or 0.5).
Secondaries 1-7 and sensitivity analyses a-f as in sections 4-5. Output: summary_a20/ (CSVs + a20_report.md).

--synthetic --out DIR: CPU test of the whole analysis on synthetic fict / patch / titlepos inputs (written into DIR/raw),
with real Stage 10/11 inputs; probe sections restricted to one layer.
"""
import argparse, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens')
R10 = B / '351_stage10'; R11 = B / '361_stage11'; G391 = B / '391_groups'
FREEZE = G391 / 'raw/a20v2_freeze'; TITLES = G391 / 'h2_fictitious/v3/selected_v3b.csv'
ADD = G391 / 'config/prereg_addendum20.md'; ADD_SHA = 'fee691de801c7c0eb6c6dad42ec7681d8297c2308c425cffdec1a9592274454a'
TITLES_SHA = '7b8dd31da3611359f8922f3a90e9f33a7c6301985563514ae88a73de7cb68586'
LAYERS = [24, 32, 40, 48, 56, 62]
PAIRS = [('final', 63)] + [('logit', l) for l in LAYERS] + [('jlens_public', l) for l in LAYERS]
CONDS = ['true'] + [f'false_{k}' for k in range(5)]
PATCH_LAYERS = [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63]
PROBE_LAYERS = [16, 24, 32, 40, 44, 48, 52, 56, 60]
SEED = 20261120
T0 = time.time()
def log(*x): print(f'[{time.time() - T0:7.0f}s]', *x, flush=True)
def nl(r): return -np.log10(np.asarray(r, float))
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 24), b''): h.update(c)
    return h.hexdigest()
def load_mod(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# ------------------------------------------------------------------ data
def load_stage10(rows_needed, pairs=PAIRS):
    """{(cond, readout, layer): Series row_id -> rank} for the needed rows (Stage 10 stored files)."""
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'shard'])
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'shard'])
    shards = sorted(toks[toks.row_id.isin(rows_needed)].shard.unique())
    out = {}
    for c in CONDS:
        base = R10 / 'raw' if c == 'true' else R10 / 'raw' / f'cond_{c}'
        for r, l in pairs:
            parts = []
            for k in shards:
                z = np.load(base / r / f'L{l:02d}' / f'shard_{k:03d}.npz')
                m = np.isin(z['row_id'], rows_needed); parts.append(pd.Series(z['rank'][m], index=z['row_id'][m]))
            out[(c, r, l)] = pd.concat(parts)
        log('stage10 loaded', c)
    return out


def load_units(raw, unit, shards):
    zs = {}
    for k in shards:
        f = raw / f'a20v2_{unit}' / f'shard_{k:03d}.npz'
        if f.exists(): zs[k] = np.load(f, allow_pickle=False)
    return zs


def token_table(F):
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'role'])
    return toks[toks.paper_id.isin(F.paper_id)].set_index('row_id').sort_index()


def paper_means(tok, rank, mask=None):
    """paper-level mean of log10(1/rank) over the tokens (rank: Series row_id -> rank)."""
    t = tok if mask is None else tok[mask]
    v = nl(rank.reindex(t.index).to_numpy())
    return pd.Series(v, index=t.index).groupby(t.paper_id).mean()


# ------------------------------------------------------------------ estimators
class Boot:
    def __init__(self):
        gc = load_mod(H / '14_groups/groups_core.py', 'groups_core'); gc.SEED = SEED
        allp = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id']).set_index('paper_id')
        self.E = gc.Engine(allp); self.NB = gc.NB
        log('engine', self.E.nteam, 'teams', self.NB, 'draws, seed', SEED)

    def W(self, pids): return self.E.W(list(pids))

    def ratio(self, pids, A, G):
        W = self.W(pids); est = A.sum() / G.sum(); b = (W @ A) / (W @ G); return est, b

    def mean(self, pids, V):
        W = self.W(pids); est = V.mean(); b = (W @ V) / W.sum(1); return est, b

    def ci(self, b): return self.E.ci(np.asarray(b, float))


def fmt(est, lo, hi, d=3): return f'{est:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]' if np.isfinite(est) else 'n/a'


def verdict(phi, phi_lo, phi_hi, r_lo, r_hi):
    if r_lo > 0:
        if phi < 0.3: v = 'H2 strongly supported'; row = 'Rbar_T CI > 0 and phi_T < 0.3'
        elif phi < 0.5: v = 'H2 partly supported (limited weight: phi near the meaning-similarity prediction ~0.6)'; row = 'Rbar_T CI > 0 and 0.3 <= phi_T < 0.5'
        else: v = 'H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal'; row = 'Rbar_T CI > 0 and phi_T >= 0.5'
        border = any(phi_lo < x < phi_hi for x in (0.3, 0.5))
    elif r_hi < 0: v = 'H2 refuted by a reversed result'; row = 'Rbar_T CI entirely below 0'; border = False
    else: v = 'H2 not supported'; row = 'Rbar_T CI includes 0'; border = False
    return dict(verdict=v, row=row, borderline=bool(border))


def phi_R(BT, D, pids, label, extra=None):
    """D: DataFrame indexed by paper with A, G, R. Returns dict with phi, Rbar and CIs + verdict."""
    d = D.loc[pids].dropna(subset=['A', 'G', 'R']); p = d.index.to_numpy()
    if len(d) < 5: return dict(label=label, n=len(d))
    phi, bphi = BT.ratio(p, d.A.to_numpy(), d.G.to_numpy()); r, br = BT.mean(p, d.R.to_numpy())
    g, bg = BT.mean(p, d.G.to_numpy()); a, ba = BT.mean(p, d.A.to_numpy())
    plo, phi_hi = BT.ci(bphi); rlo, rhi = BT.ci(br)
    out = dict(label=label, n=len(d), phi=phi, phi_lo=plo, phi_hi=phi_hi, Rbar=r, R_lo=rlo, R_hi=rhi,
               Gbar=g, G_lo=BT.ci(bg)[0], G_hi=BT.ci(bg)[1], Abar=a, A_lo=BT.ci(ba)[0], A_hi=BT.ci(ba)[1])
    out |= verdict(phi, plo, phi_hi, rlo, rhi)
    if extra: out |= extra
    return out


def within_bin_tc(BT, D, F, col):
    """within-bin target - control of the paper mean of `col` (Engine.within_bin, weights n_t n_c/(n_t+n_c))."""
    d = D[[col]].join(F.set_index('paper_id')[['group', 'citation_bin']]).dropna(subset=[col])
    r = BT.E.within_bin(list(d.index), (d.group == 'target').to_numpy(), (d.group == 'control').to_numpy(), d.citation_bin.to_numpy(), d[col].to_numpy(), 1, 1)
    lo, hi = BT.ci(r['boot'][:, 0]); return r['est'][0], lo, hi, int(r['n_a'][0]), int(r['n_b'][0])


def within_bin_phi(BT, D, F):
    """within-bin target - control of phi (per-bin ratio of sums; weights n_t n_c/(n_t+n_c) fixed at the point counts)."""
    d = D[['A', 'G']].join(F.set_index('paper_id')[['group', 'citation_bin']]).dropna()
    W = BT.W(d.index); est, boot, wsum = 0.0, np.zeros(BT.NB), 0.0
    for b, g in d.groupby('citation_bin'):
        t = (g.group == 'target').to_numpy(); c = (g.group == 'control').to_numpy()
        if t.sum() < 1 or c.sum() < 1: continue
        idx = d.index.get_indexer(g.index); Wb = W[:, idx]; A = g.A.to_numpy(); G = g.G.to_numpy()
        w = t.sum() * c.sum() / (t.sum() + c.sum()); wsum += w
        est += w * (A[t].sum() / G[t].sum() - A[c].sum() / G[c].sum())
        with np.errstate(invalid='ignore', divide='ignore'):
            boot += w * ((Wb[:, t] @ A[t]) / (Wb[:, t] @ G[t]) - (Wb[:, c] @ A[c]) / (Wb[:, c] @ G[c]))
    est /= wsum; boot /= wsum; lo, hi = BT.ci(boot); return est, lo, hi


# ------------------------------------------------------------------ probes (secondaries 5, 6)
def load_true_titlepos(players_idx):
    zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))]
    Xt = np.concatenate([z['resid_title'][:, players_idx] for z in zs]); Yc = np.concatenate([z['resid_colon'][:, -1] for z in zs])
    pid = np.concatenate([z['resid_paper_id'] for z in zs])
    gold = pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zs])
    return Xt, Yc, pid, gold


def ridge_folds(X, targets, folds, extras):
    """stage13_cpu.ridge_cv for each (Y, alphas) in targets (standardise on the training folds; alpha x trace/d picked on
    fold 0, per target), with one shared Gram matrix per fold. extras: {tag: [(idx_in_X, x_row)]}; each extra row is
    predicted by the model of the fold that holds idx_in_X out. Returns P[j] (held-out predictions), E[j][tag][idx], best[j]."""
    P = [np.zeros_like(Y, dtype=np.float64) for Y, _ in targets]; E = [{t: {} for t in extras} for _ in targets]; best = [None] * len(targets)
    for k in np.unique(folds):
        tr, te = folds != k, folds == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; A = ((X[tr] - mu) / sd).astype(np.float64)
        G = A.T @ A; I = np.eye(G.shape[0]); sc = np.trace(G) / G.shape[0]; Xt = (X[te] - mu) / sd
        sel = {t: [(i, xe) for i, xe in v if folds[i] == k] for t, v in extras.items()}
        Xe = {t: ((np.stack([xe for _, xe in v]) - mu) / sd) for t, v in sel.items() if v}
        for j, (Y, alphas) in enumerate(targets):
            ym = Y[tr].mean(0); Bm = A.T @ (Y[tr] - ym)
            if best[j] is None:
                errs = [(((Xt @ np.linalg.solve(G + a * sc * I, Bm) + ym) - Y[te]) ** 2).mean() for a in alphas]; best[j] = alphas[int(np.argmin(errs))]
            Wp = np.linalg.solve(G + best[j] * sc * I, Bm); P[j][te] = Xt @ Wp + ym
            for t, xe in Xe.items():
                pe = xe @ Wp + ym
                for n, (i, _) in enumerate(sel[t]): E[j][t][i] = pe[n]
        log('  fold', k, 'done')
    return P, E, best


def probe_sections(BT, F, TP, raw_layers, out_dir):
    """E4b (secondary 5) and M2 (secondary 6) with the published setup refitted on the 9,108 true runs (team folds)."""
    c13 = load_mod(H / '13_stage13/stage13_cpu.py', 'c13')
    li = [PROBE_LAYERS.index(l) for l in raw_layers]
    Xt, Yc, pid, gold = load_true_titlepos(li); log('true titlepos', Xt.shape)
    folds, _ = c13.group_folds(pid, k=5)                     # archived folds_own9108_k5s13 (team folds)
    pos = {p: i for i, p in enumerate(pid)}
    fict_res = {}; true_res_new = {}
    for z in TP.values():
        for n, p in enumerate(z['paper_id']): fict_res[str(p)] = z['resid_title_fict'][n][li]; true_res_new[str(p)] = z['resid_title_true'][n][li]
    f0 = {}
    zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos/false_0').glob('shard_*.npz'))]
    for z in zs:
        for n, p in enumerate(z['resid_paper_id']):
            if str(p) in fict_res: f0[str(p)] = z['resid_title'][n][li]
    subj = [p for p in F.paper_id if p in fict_res and p in pos]
    pv = np.load(sorted((R11 / 'raw/probe_vocab').glob('shard_*.npz'))[0])
    Wv = pv['lm_head_rows'].astype(np.float32); nw = pv['norm_weight'].astype(np.float32); eps = float(pv['eps']); vid = {int(t): i for i, t in enumerate(pv['token_id'])}
    g1 = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict()
    def pscore(pred, p):
        pred = np.asarray(pred, np.float32); h = pred / np.sqrt((pred ** 2).mean() + eps) * nw; lg = h @ Wv.T
        gi = [vid[x] for x in g1.get(p, []) if x in vid]
        return np.mean([-np.log10(1 + (lg > lg[j]).sum()) for j in gi]) if gi else np.nan
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
    fields = sorted(papers.field.unique()); L = papers.loc[pid]
    y_field = np.eye(len(fields))[[fields.index(f) for f in L.field]]
    y_year = pd.to_numeric(L.year, errors='coerce').to_numpy(float)[:, None]
    y_cit = np.log10(pd.to_numeric(L.citations, errors='coerce').fillna(0).to_numpy(float) + 1)[:, None]
    e4, m2 = [], []
    for j, l in enumerate(raw_layers):
        X = Xt[:, j].astype(np.float32)
        extras = {'fict': [(pos[p], fict_res[p][j].astype(np.float32)) for p in subj], 'false0': [(pos[p], f0[p][j].astype(np.float32)) for p in subj if p in f0]}
        yr_ok = ~np.isnan(y_year[:, 0])
        # E4b: ridge title residual -> true L63 ':' residual (alphas 0.1, 1, 10), training-fold standardisation, team folds;
        # M2: field (acc), year (r2), log citations (r2) with the ridge_cv alpha grid; scored against the TRUE paper's labels
        log('E4b + M2 layer', l)
        A2 = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)
        P, E, best = ridge_folds(X, [(Yc.astype(np.float32), (0.1, 1.0, 10.0)), (y_field, A2), (np.where(yr_ok[:, None], y_year, np.nanmean(y_year)), A2), (y_cit, A2)], folds, extras)
        for p in subj:
            i = pos[p]
            e4.append(dict(layer=l, paper_id=p, alpha=best[0], probe_true=pscore(P[0][i], p), probe_fict=pscore(E[0]['fict'][i], p),
                           probe_false0=pscore(E[0]['false0'][i], p) if i in E[0]['false0'] else np.nan))
            m2.append(dict(layer=l, paper_id=p, field_true=int(np.argmax(P[1][i]) == np.argmax(y_field[i])), field_fict=int(np.argmax(E[1]['fict'][i]) == np.argmax(y_field[i])),
                           year_y=y_year[i, 0], year_true=P[2][i, 0], year_fict=E[2]['fict'][i][0], cit_y=y_cit[i, 0], cit_true=P[3][i, 0], cit_fict=E[3]['fict'][i][0],
                           alpha_field=best[1], alpha_year=best[2], alpha_cit=best[3]))
        pd.DataFrame(e4).to_csv(out_dir / 'E4b_perpaper.csv', index=False); pd.DataFrame(m2).to_csv(out_dir / 'M2_perpaper.csv', index=False)
    return pd.DataFrame(e4), pd.DataFrame(m2)


def r2_boot(W, y, p):
    """team-weighted R^2 per draw: 1 - sum w (y-p)^2 / sum w (y - ybar_w)^2."""
    ybar = (W @ y) / W.sum(1)
    return 1 - (W @ (y - p) ** 2) / ((W * (y[None, :] - ybar[:, None]) ** 2).sum(1))


# ------------------------------------------------------------------ synthetic inputs (CPU test)
def make_synthetic(raw, F, tok):
    rng = np.random.default_rng(0)
    s10 = load_stage10(tok.index.to_numpy(), pairs=PAIRS)
    for k, g in F.groupby('shard'):
        rows = tok[tok.paper_id.isin(g.paper_id)].index.to_numpy()
        d = dict(row_id=rows)
        for r, l in PAIRS:
            t = s10[('true', r, l)].reindex(rows).to_numpy(); f = s10[('false_0', r, l)].reindex(rows).to_numpy()
            mix = np.where(rng.random(len(rows)) < 0.6, f, t); d[f'rank@{r}@{l}'] = mix.astype(np.int32)
        (raw / 'a20v2_score').mkdir(parents=True, exist_ok=True); np.savez(raw / 'a20v2_score' / f'shard_{k:03d}.npz', meta=np.array('{}'), **d)
        z = np.load(R11 / f'raw/patch/shard_{k:03d}.npz'); m = np.isin(z['row_id'], rows)
        fx = d['rank@final@63'][np.searchsorted(rows, z['row_id'][m])] if False else s10[('false_0', 'final', 63)].reindex(z['row_id'][m]).to_numpy()
        rf = d['rank@final@63']; ref = dict(zip(rows, rf)); rfi = np.array([ref[x] for x in z['row_id'][m]])
        rp = np.where(rng.random((m.sum(), 15)) < np.linspace(0, 1, 15), rfi[:, None], z['rank_false'][m][:, None]); rp[:, -1] = rfi
        (raw / 'a20v2_patch').mkdir(parents=True, exist_ok=True)
        np.savez(raw / 'a20v2_patch' / f'shard_{k:03d}.npz', meta=np.array('{}'), row_id=z['row_id'][m], rank_fict=rfi, rank_false=z['rank_false'][m], rank_patch=rp, layers=np.array(PATCH_LAYERS))
        n = len(g); tp = dict(paper_id=g.paper_id.to_numpy().astype(str), probe_layers=np.array(PROBE_LAYERS))
        for c in ['fict'] + CONDS: tp[f'tlp_mean_{c}'] = rng.normal(-3, 1, n); tp[f'tlp_n_{c}'] = np.full(n, 10)
        tp['resid_title_fict'] = rng.normal(0, 1, (n, len(PROBE_LAYERS), 5120)).astype(np.float16); tp['resid_title_true'] = tp['resid_title_fict']
        (raw / 'a20v2_titlepos').mkdir(parents=True, exist_ok=True); np.savez(raw / 'a20v2_titlepos' / f'shard_{k:03d}.npz', meta=np.array('{}'), **tp)
    log('synthetic inputs written', raw)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--raw', default=str(G391 / 'raw')); ap.add_argument('--out', default=str(G391 / 'summary_a20'))
    ap.add_argument('--synthetic', action='store_true'); ap.add_argument('--probe-layers', default=None); ap.add_argument('--skip-probes', action='store_true')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); raw = Path(a.raw)
    if sha(ADD) != ADD_SHA: raise SystemExit('ADDENDUM 20 CHANGED')
    if sha(TITLES) != TITLES_SHA: raise SystemExit('TITLE SET CHANGED')
    F = pd.read_parquet(FREEZE / 'fict_titles.parquet'); fz = json.loads((FREEZE / 'h2_main_freeze.json').read_text())
    sel = pd.read_csv(TITLES, dtype={'paper_id': str}).set_index('paper_id')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'recall_level', 'group_tight', 'citation_bin', 'title']).set_index('paper_id')
    tok = token_table(F)
    probe_layers = [int(x) for x in a.probe_layers.split(',')] if a.probe_layers else PROBE_LAYERS
    if a.synthetic:
        raw = out / 'raw'; make_synthetic(raw, F, tok); probe_layers = [int(x) for x in (a.probe_layers or '48').split(',')]
    shards = sorted(F.shard.unique())
    SC = load_units(raw, 'score', shards); PT = load_units(raw, 'patch', shards); TP = load_units(raw, 'titlepos', shards)
    log('units', len(SC), len(PT), len(TP), 'of', len(shards))
    # ---------------- exclusions at run time
    excl = pd.read_csv(FREEZE / 'exclusions.csv'); excl_rt = []
    fict = {}
    for r, l in PAIRS:
        parts = [pd.Series(z[f'rank@{r}@{l}'], index=z['row_id']) for z in SC.values()]
        fict[(r, l)] = pd.concat(parts) if parts else pd.Series(dtype=float)
    s10 = load_stage10(tok.index.to_numpy())
    # paper-level S per condition / pair
    S = {}
    for r, l in PAIRS:
        d = pd.DataFrame({c: paper_means(tok, s10[(c, r, l)]) for c in CONDS})
        d['fict'] = paper_means(tok, fict[(r, l)]) if len(fict[(r, l)]) else np.nan
        S[(r, l)] = d.reindex(F.paper_id)
    # hard check: every token of every paper scored in fict, same token set as true
    fr = fict[('final', 63)]; have = tok.index.isin(fr.index.to_numpy()) & np.isin(tok.index, fr.dropna().index.to_numpy())
    for p, g in pd.Series(have, index=tok.index).groupby(tok.paper_id):
        miss = int((~g).sum())
        if miss: excl_rt.append(dict(paper_id=p, reason=f'scoring failure / missing fict rows ({miss} of {len(g)} tokens)'))
    bad = {x['paper_id'] for x in excl_rt}
    keep = F[~F.paper_id.isin(bad)].copy()
    keep['recall_level'] = keep.paper_id.map(papers.recall_level)
    T = keep[keep.group == 'target'].paper_id.to_numpy(); Cc = keep[keep.group == 'control'].paper_id.to_numpy()
    log('papers kept', len(keep), 'target', len(T), 'control', len(Cc), 'run-time exclusions', len(excl_rt))
    BT = Boot()

    def ARG(Sd, fbar=None):
        Fm = Sd[[f'false_{k}' for k in range(5)]].mean(1) if fbar is None else Sd[fbar]
        return pd.DataFrame(dict(A=Sd.fict - Fm, G=Sd.true - Fm, R=Sd.true - Sd.fict, S_true=Sd.true, S_fict=Sd.fict, F=Fm))
    D0 = ARG(S[('final', 63)])
    D0.join(keep.set_index('paper_id')[['group', 'citation_bin', 'recall_level']]).to_csv(out / 'perpaper_final63.csv')
    res = {}
    # ---------------- primary
    prim = phi_R(BT, D0, T, 'PRIMARY target final L63'); res['primary'] = prim
    log('PRIMARY', json.dumps({k: prim[k] for k in ('n', 'phi', 'phi_lo', 'phi_hi', 'Rbar', 'R_lo', 'R_hi', 'verdict', 'borderline')}, default=float))
    rows = [prim]
    # ---------------- secondary 1: control
    rows.append(phi_R(BT, D0, Cc, 'S1 control final L63'))
    # ---------------- secondary 2: within-bin T - C of R and phi
    tcR = within_bin_tc(BT, D0, keep, 'R'); tcPhi = within_bin_phi(BT, D0, keep)
    tcG = within_bin_tc(BT, D0, keep, 'G'); tcA = within_bin_tc(BT, D0, keep, 'A')
    # plain phi_T - phi_C (descriptive)
    WT, WC = BT.W(T), BT.W(Cc); dT, dC = D0.loc[T], D0.loc[Cc]
    pd_b = (WT @ dT.A.to_numpy()) / (WT @ dT.G.to_numpy()) - (WC @ dC.A.to_numpy()) / (WC @ dC.G.to_numpy())
    pd_e = dT.A.sum() / dT.G.sum() - dC.A.sum() / dC.G.sum(); pd_ci = BT.ci(pd_b)
    # ---------------- secondary 3: layer profile
    prof = []
    for r, l in PAIRS:
        Dl = ARG(S[(r, l)])
        for grp, ids in (('target', T), ('control', Cc)): prof.append(phi_R(BT, Dl, ids, f'{r} L{l} {grp}', dict(readout=r, layer=l, group=grp)))
    prof = pd.DataFrame(prof); prof.to_csv(out / 'S3_layer_profile.csv', index=False)
    # ---------------- secondary 4: E1 patch with the fict donor
    e1 = []
    if PT:
        pz = {k: z for k, z in PT.items()}
        rowid = np.concatenate([z['row_id'] for z in pz.values()]); rp = np.concatenate([z['rank_patch'] for z in pz.values()])
        rfx = np.concatenate([z['rank_fict'] for z in pz.values()]); rfl = np.concatenate([z['rank_false'] for z in pz.values()])
        s11 = [np.load(R11 / f'raw/patch/shard_{k:03d}.npz') for k in pz]
        st = pd.DataFrame(dict(row_id=np.concatenate([z['row_id'] for z in s11]), t=nl(np.concatenate([z['rank_true'] for z in s11])),
                               f=nl(np.concatenate([z['rank_false'] for z in s11])))).set_index('row_id')
        st_p = pd.DataFrame(nl(np.concatenate([z['rank_patch'] for z in s11])), index=st.index, columns=[f'tp{l}' for l in PATCH_LAYERS])
        dd = pd.DataFrame(nl(rp), index=rowid, columns=[f'p{l}' for l in PATCH_LAYERS]); dd['x'] = nl(rfx); dd['f'] = nl(rfl)
        dd = dd.join(st, rsuffix='_s11').join(st_p); dd['paper_id'] = tok.paper_id.reindex(dd.index).to_numpy()
        pm = dd.groupby('paper_id').mean()
        sanity = float(np.abs(pm['p63'] - pm['x']).max())
        for grp, ids in (('target', T), ('control', Cc)):
            q = pm.reindex([p for p in ids if p in pm.index]); p_ = q.index.to_numpy(); W = BT.W(p_)
            den = (q.t - q.f_s11).to_numpy()
            for l in PATCH_LAYERS:
                num = (q[f'p{l}'] - q.f).to_numpy(); numt = (q[f'tp{l}'] - q.f_s11).to_numpy()
                e = num.mean() / den.mean(); b = (W @ num) / (W @ den); et = numt.mean() / den.mean(); bt = (W @ numt) / (W @ den)
                e1.append(dict(group=grp, layer=l, n=len(q), rec_fict=e, rec_fict_lo=BT.ci(b)[0], rec_fict_hi=BT.ci(b)[1],
                               rec_true=et, rec_true_lo=BT.ci(bt)[0], rec_true_hi=BT.ci(bt)[1], diff=et - e, diff_lo=BT.ci(bt - b)[0], diff_hi=BT.ci(bt - b)[1]))
            # L63 identity: rec_fict(63) == (fict - false_0)/(true - false_0) with this run's false_0 and the Stage 11 true - false_0
            e1[-1]['L63_identity_value'] = float(((q.x - q.f).mean()) / den.mean())
        e1 = pd.DataFrame(e1); e1['L63_patch_vs_fict_max_abs_paper_diff'] = sanity; e1.to_csv(out / 'S4_E1_fict_donor.csv', index=False)
    # ---------------- secondary 5 + 6: probes
    e4s, m2s = pd.DataFrame(), pd.DataFrame()
    if TP and not a.skip_probes:
        e4, m2 = probe_sections(BT, keep, TP, probe_layers, out)
        e4rows, m2rows = [], []
        for l, g in e4.groupby('layer'):
            g = g.set_index('paper_id')
            g['d_true_fict'] = g.probe_true - g.probe_fict; g['d_true_f0'] = g.probe_true - g.probe_false0
            for grp, ids in (('target', T), ('control', Cc)):
                q = g.reindex([p for p in ids if p in g.index]).dropna(subset=['d_true_fict'])
                row = dict(layer=l, group=grp, n=len(q), alpha=g.alpha.iloc[0])
                for c in ('probe_true', 'probe_fict', 'probe_false0', 'd_true_fict', 'd_true_f0'):
                    v = q[c].dropna(); e, b = BT.mean(v.index.to_numpy(), v.to_numpy()); lo, hi = BT.ci(b); row |= {c: e, f'{c}_lo': lo, f'{c}_hi': hi}
                e4rows.append(row)
            tc = within_bin_tc(BT, g[['d_true_fict']], keep, 'd_true_fict'); e4rows.append(dict(layer=l, group='T-C within bin', d_true_fict=tc[0], d_true_fict_lo=tc[1], d_true_fict_hi=tc[2], n=tc[3] + tc[4]))
        e4s = pd.DataFrame(e4rows); e4s.to_csv(out / 'S5_E4b_probe.csv', index=False)
        for l, g in m2.groupby('layer'):
            g = g.set_index('paper_id')
            for grp, ids in (('target', T), ('control', Cc), ('all', np.concatenate([T, Cc]))):
                q = g.reindex([p for p in ids if p in g.index]); W = BT.W(q.index)
                row = dict(layer=l, group=grp, n=len(q))
                for c in ('field_true', 'field_fict'):
                    e = q[c].mean(); b = (W @ q[c].to_numpy()) / W.sum(1); row |= {c: e, f'{c}_lo': BT.ci(b)[0], f'{c}_hi': BT.ci(b)[1]}
                bd = (W @ (q.field_true - q.field_fict).to_numpy()) / W.sum(1); row |= dict(field_diff=q.field_true.mean() - q.field_fict.mean(), field_diff_lo=BT.ci(bd)[0], field_diff_hi=BT.ci(bd)[1])
                for t in ('year', 'cit'):
                    qq = q.dropna(subset=[f'{t}_y']); Wq = BT.W(qq.index); y = qq[f'{t}_y'].to_numpy()
                    r2 = {}
                    for c in ('true', 'fict'):
                        p_ = qq[f'{t}_{c}'].to_numpy(); e = 1 - ((y - p_) ** 2).sum() / ((y - y.mean()) ** 2).sum(); b = r2_boot(Wq, y, p_); r2[c] = (e, b)
                        row |= {f'{t}_r2_{c}': e, f'{t}_r2_{c}_lo': BT.ci(b)[0], f'{t}_r2_{c}_hi': BT.ci(b)[1]}
                    row |= {f'{t}_r2_diff': r2['true'][0] - r2['fict'][0], f'{t}_r2_diff_lo': BT.ci(r2['true'][1] - r2['fict'][1])[0], f'{t}_r2_diff_hi': BT.ci(r2['true'][1] - r2['fict'][1])[1]}
                m2rows.append(row)
        m2s = pd.DataFrame(m2rows); m2s.to_csv(out / 'S6_M2_attributes.csv', index=False)
    # ---------------- secondary 7: meaning dose (tertiles of fict cosine, cut on target papers)
    keep['cos_true'] = keep.paper_id.map(sel.cos_true)
    cuts = np.quantile(keep[keep.group == 'target'].cos_true, [1 / 3, 2 / 3])
    keep['cos_tert'] = np.digitize(keep.cos_true, cuts)
    dose = []
    for t_ in range(3):
        ids = keep[(keep.group == 'target') & (keep.cos_tert == t_)].paper_id.to_numpy()
        cs = keep.set_index('paper_id').cos_true.loc[ids]
        dose.append(phi_R(BT, D0, ids, f'S7 target cos tertile {t_ + 1}', dict(cos_lo=float(cs.min()), cos_hi=float(cs.max()), cos_median=float(cs.median()))))
    # dose trend: phi(tertile 3) - phi(tertile 1)
    i1 = keep[(keep.group == 'target') & (keep.cos_tert == 0)].paper_id.to_numpy(); i3 = keep[(keep.group == 'target') & (keep.cos_tert == 2)].paper_id.to_numpy()
    e1_, b1_ = BT.ratio(i1, D0.loc[i1].A.to_numpy(), D0.loc[i1].G.to_numpy()); e3_, b3_ = BT.ratio(i3, D0.loc[i3].A.to_numpy(), D0.loc[i3].G.to_numpy())
    dose_trend = (e3_ - e1_, *BT.ci(b3_ - b1_))
    # ---------------- sensitivity
    sens = []
    sens.append(phi_R(BT, ARG(S[('final', 63)], fbar='false_0'), T, '(a) false_0 instead of the 5-title mean'))
    ok_b = keep[(keep.group == 'target') & (keep.paper_id.map(sel.ext_j2) < 0.4)].paper_id.to_numpy()
    sens.append(phi_R(BT, D0, ok_b, '(b) without fict titles with Crossref jaccard2 >= 0.4'))
    ok_c = keep[(keep.group == 'target') & (keep.paper_id.map(sel.true_words) >= 6)].paper_id.to_numpy()
    sens.append(phi_R(BT, D0, ok_c, '(c) true titles >= 6 words'))
    # (d) first author only; surname first token only
    for lab, mask in (('(d1) first author only', tok.author_index == tok.groupby('paper_id').author_index.transform('min')),
                      ('(d2) surname first token only', tok.role == 'surname_first')):
        Sd = pd.DataFrame({c: paper_means(tok, s10[(c, 'final', 63)], mask) for c in CONDS}); Sd['fict'] = paper_means(tok, fict[('final', 63)], mask)
        sens.append(phi_R(BT, ARG(Sd.reindex(F.paper_id)), T, lab))
    ok_e = keep[(keep.group == 'target') & (keep.recall_level == 'R0')].paper_id.to_numpy()
    sens.append(phi_R(BT, D0, ok_e, '(e) R0 papers only'))
    # (f) title likelihood
    tl = pd.DataFrame()
    if TP:
        tl = pd.concat([pd.DataFrame({'paper_id': z['paper_id'], **{c: z[f'tlp_mean_{c}'] for c in ['fict'] + CONDS}}) for z in TP.values()]).set_index('paper_id')
        tl['false_mean'] = tl[[f'false_{k}' for k in range(5)]].mean(1); tl['true_minus_fict'] = tl.true - tl.fict
        tl.to_csv(out / 'title_logprob_perpaper.csv')
        tlrows = []
        for grp, ids in (('target', T), ('control', Cc)):
            q = tl.reindex([p for p in ids if p in tl.index]); W = BT.W(q.index)
            row = dict(group=grp, n=len(q))
            for c in ('true', 'fict', 'false_0', 'false_mean', 'true_minus_fict'):
                b = (W @ q[c].to_numpy()) / W.sum(1); row |= {c: q[c].mean(), f'{c}_lo': BT.ci(b)[0], f'{c}_hi': BT.ci(b)[1]}
            tlrows.append(row)
        tlsum = pd.DataFrame(tlrows); tlsum.to_csv(out / 'Sf_title_logprob.csv', index=False)
        tt = tl.reindex(T).true_minus_fict; cuts_f = np.quantile(tt.dropna(), [1 / 3, 2 / 3])
        for t_ in range(3):
            ids = tt[np.digitize(tt, cuts_f) == t_].dropna().index.to_numpy()
            sens.append(phi_R(BT, D0, ids, f'(f) title log-prob true - fict, target tertile {t_ + 1}', dict(dlp_lo=float(tt.loc[ids].min()), dlp_hi=float(tt.loc[ids].max()))))
    allrows = pd.DataFrame(rows + dose + sens); allrows.to_csv(out / 'primary_secondary_sensitivity.csv', index=False)
    # ---------------- parity
    par = None; pf = raw / 'a20v2_checks' / 'parity_000.json'
    if pf.exists(): par = json.loads(pf.read_text())
    checks = {}
    for f in sorted((raw / 'a20v2_checks').glob('*.json')) if (raw / 'a20v2_checks').exists() else []:
        m = json.loads(f.read_text()); checks[f.stem] = dict(status=m.get('checks', {}).get('status'), seconds=m.get('seconds'), gpu=m.get('gpu'), job=m.get('job'), checks=m.get('checks'))
    json.dump(dict(primary=prim, tc_R=tcR, tc_phi=tcPhi, phi_T_minus_phi_C=(pd_e, *pd_ci), dose_trend=dose_trend, run_time_exclusions=excl_rt),
              open(out / 'a20_results.json', 'w'), indent=1, default=float)
    write_report(out, a, F, keep, excl, excl_rt, prim, rows, tcR, tcPhi, tcG, tcA, (pd_e, *pd_ci), prof, e1, e4s, m2s, dose, dose_trend, sens,
                 tl, par, checks, fz, probe_layers)
    log('done', out)


def gpu_hours_jobs(jobs):
    tot, det = 0.0, []
    for j in jobs:
        try:
            o = subprocess.run(['sacct', '-j', j, '-X', '-n', '-P', '-o', 'JobID,ElapsedRaw'], capture_output=True, text=True, timeout=60).stdout.strip().split('\n')[0]
            el = int(o.split('|')[1] or 0); tot += el / 3600; det.append(f'{j} {el / 60:.1f} min')
        except Exception as e: det.append(f'{j}: sacct failed {e!r}')
    return tot, det


def gpu_hours(raw):
    jobs = sorted({str(m.get('job')) for f in (raw / 'a20v2_checks').glob('*.json') for m in [json.loads(f.read_text())] if m.get('job')}) if (raw / 'a20v2_checks').exists() else []
    jf = G391 / 'logs/a20/gpu_jobs_v2.txt'
    if jf.exists(): jobs = sorted(set(jobs) | {l.split()[0] for l in jf.read_text().split('\n') if l.strip()})
    tot, det = 0.0, []
    for j in jobs:
        try:
            o = subprocess.run(['sacct', '-j', j, '-X', '-n', '-P', '-o', 'JobID,Partition,ElapsedRaw,AllocTRES,State,NodeList'], capture_output=True, text=True, timeout=60).stdout.strip().split('\n')[0]
            jid, part, el, tres, state, node = o.split('|'); el = int(el or 0)
            ng = 1
            for x in tres.split(','):
                if x.startswith('gres/gpu='): ng = int(x.split('=')[1])
            tot += el * ng / 3600; det.append(f'{jid} {part} {node} {state} {el / 60:.1f} min x {ng} GPU')
        except Exception as e: det.append(f'{j}: sacct failed {e!r}')
    return tot, det


def write_report(out, a, F, keep, excl, excl_rt, prim, rows, tcR, tcPhi, tcG, tcA, phidiff, prof, e1, e4s, m2s, dose, dose_trend, sens, tl, par, checks, fz, probe_layers):
    L = []; P = L.append
    f = lambda d, k: fmt(d[k], d[f'{k}_lo'], d[f'{k}_hi'])
    fr = lambda d: f"phi = {fmt(d['phi'], d['phi_lo'], d['phi_hi'])}; Rbar = {fmt(d['Rbar'], d['R_lo'], d['R_hi'])}; n = {d['n']}"
    P('# Addendum 20 (LOCKED) — H2 test with fictitious titles: main result' + (' [SYNTHETIC TEST — NOT A RESULT]' if a.synthetic else ''))
    P('')
    P(f'Generated {time.strftime("%Y-%m-%d %H:%M")} by `~/jlens_work/15_h2fict/h2_main_analyze.py` (sha256 {sha(__file__)[:16]}…). '
      f'Addendum: `391_groups/config/prereg_addendum20.md` (sha256 {ADD_SHA[:16]}…, verified); title set `h2_fictitious/v3/selected_v3b.csv` (sha256 {TITLES_SHA[:16]}…, verified). '
      'Exploratory status: none — this is the locked confirmatory analysis; everything outside §3 of the addendum is secondary / descriptive.')
    P('')
    P('## 1. Primary result (target group, `final` L63, mean log10(1/rank) per name token)')
    P('')
    P('| quantity | estimate [95 % team-bootstrap CI] |'); P('|---|---|')
    P(f"| φ_T = ΣA / ΣG (fictitious share of the true − false gap) | **{fmt(prim['phi'], prim['phi_lo'], prim['phi_hi'])}** |")
    P(f"| R̄_T = mean(S_true − S_fict) | **{fmt(prim['Rbar'], prim['R_lo'], prim['R_hi'])}** |")
    P(f"| Ḡ_T = mean(S_true − F̄) | {fmt(prim['Gbar'], prim['G_lo'], prim['G_hi'])} |")
    P(f"| Ā_T = mean(S_fict − F̄) | {fmt(prim['Abar'], prim['A_lo'], prim['A_hi'])} |")
    P(f"| n target papers | {prim['n']} |")
    P('')
    P(f"**Decision-rule row:** {prim['row']} → **{prim['verdict']}**" + (' — **borderline** (φ_T CI crosses ' + ' and '.join(str(x) for x in (0.3, 0.5) if prim['phi_lo'] < x < prim['phi_hi']) + ')' if prim['borderline'] else ' (not borderline: φ_T CI does not cross 0.3 or 0.5)') + '.')
    P('')
    P('Rule (addendum 20 §3, fixed before the run): verdict by the point estimate φ̂_T, read only when R̄_T\'s 95 % CI lies entirely above 0; '
      'φ̂_T < 0.3 → strongly supported; 0.3 ≤ φ̂_T < 0.5 → partly supported (limited weight); φ̂_T ≥ 0.5 → partly supported (meaning explains most); '
      'R̄_T CI includes 0 → not supported; R̄_T CI entirely below 0 → refuted (reversed). Borderline = φ_T CI crosses 0.3 or 0.5.')
    P('')
    changed = [s for s in sens if 'verdict' in s and s['verdict'] != prim['verdict']]
    P('**Sensitivity analyses that would change the verdict:** ' + ('; '.join(f"{s['label']} → {s['verdict']}" for s in changed) if changed else 'none (the verdict is unchanged in every sensitivity analysis a–f).'))
    P('')
    P('## 2. Secondary comparisons (CIs; no verdict of their own)')
    P('')
    c = rows[1]
    P(f"**S1 control group:** φ_C = {fmt(c['phi'], c['phi_lo'], c['phi_hi'])}, R̄_C = {fmt(c['Rbar'], c['R_lo'], c['R_hi'])}, Ḡ_C = {fmt(c['Gbar'], c['G_lo'], c['G_hi'])}, n = {c['n']}.")
    P('')
    P(f"**S2 recognition and identity (within-bin target − control, weights n_t·n_c/(n_t+n_c)):** R_T − R_C = {fmt(*tcR[:3])} (n {tcR[3]} T / {tcR[4]} C); "
      f"φ_T − φ_C (per-bin ratio of sums, bin-weighted) = {fmt(*tcPhi)}; plain φ_T − φ_C (pooled ratios, descriptive) = {fmt(*phidiff)}; "
      f"G_T − G_C = {fmt(*tcG[:3])}; A_T − A_C = {fmt(*tcA[:3])}. H2 predicts R_T − R_C > 0.")
    P('')
    P('**S3 layer profile (name positions):**'); P('')
    P('| readout | layer | φ target | R̄ target | φ control | R̄ control |'); P('|---|---|---|---|---|---|')
    for (r, l), g in prof.groupby(['readout', 'layer'], sort=False):
        t = g[g.group == 'target'].iloc[0]; cc = g[g.group == 'control'].iloc[0]
        P(f"| {r} | L{l} | {fmt(t.phi, t.phi_lo, t.phi_hi)} | {fmt(t.Rbar, t.R_lo, t.R_hi)} | {fmt(cc.phi, cc.phi_lo, cc.phi_hi)} | {fmt(cc.Rbar, cc.R_lo, cc.R_hi)} |")
    P('')
    P('φ at early layers is a ratio of small numbers (Ḡ near 0) and can be unstable; see S3_layer_profile.csv for Ḡ and Ā.')
    P('')
    if len(e1):
        P('**S4 E1 tail patching, fict donor (false_0 run, aligned post-title tail replaced by the fict run at layer l):** rec_fict(l) = mean(patched − false_0) / mean(true − false_0) '
          '(denominator and rec_true(l) from the stored Stage 11 E1 run on the same papers; numerator baseline = this run\'s false_0).'); P('')
        P('| layer | rec_fict target | rec_true target | rec_true − rec_fict target | rec_fict control | rec_true control |'); P('|---|---|---|---|---|---|')
        for l, g in e1.groupby('layer'):
            t = g[g.group == 'target'].iloc[0]; cc = g[g.group == 'control'].iloc[0]
            P(f"| L{l} | {fmt(t.rec_fict, t.rec_fict_lo, t.rec_fict_hi)} | {fmt(t.rec_true, t.rec_true_lo, t.rec_true_hi)} | {fmt(t['diff'], t.diff_lo, t.diff_hi)} | {fmt(cc.rec_fict, cc.rec_fict_lo, cc.rec_fict_hi)} | {fmt(cc.rec_true, cc.rec_true_lo, cc.rec_true_hi)} |")
        t63 = e1[(e1.group == 'target') & (e1.layer == 63)].iloc[0]
        P(''); P(f"L63 sanity: rec_fict(63) = {t63.rec_fict:.4f} vs (fict − false_0)/(true − false_0) = {t63.L63_identity_value:.4f} (target); max |paper mean patched L63 − fict| = {t63.L63_patch_vs_fict_max_abs_paper_diff:.2e}.")
        P('')
    if len(e4s):
        P(f'**S5 title-position probe (E4b setup refitted on the 9,108 true runs: ridge title residual → true L63 ":" residual, team folds (archived folds_own9108_k5s13), training-fold standardisation, alpha ∈ {{0.1, 1, 10}} on fold 0; '
          'each held-out paper\'s fold model applied to its fict (and stored false_0) title residual; gold author first tokens ranked among the cohort name-first-token vocabulary):**'); P('')
        P('| layer | group | probe(true) | probe(fict) | true − fict | true − false_0 |'); P('|---|---|---|---|---|---|')
        for _, x in e4s.iterrows():
            if x.group == 'T-C within bin': P(f"| L{int(x.layer)} | T − C (within bin) | | | {fmt(x.d_true_fict, x.d_true_fict_lo, x.d_true_fict_hi)} | |"); continue
            P(f"| L{int(x.layer)} | {x.group} | {fmt(x.probe_true, x.probe_true_lo, x.probe_true_hi)} | {fmt(x.probe_fict, x.probe_fict_lo, x.probe_fict_hi)} | {fmt(x.d_true_fict, x.d_true_fict_lo, x.d_true_fict_hi)} | {fmt(x.d_true_f0, x.d_true_f0_lo, x.d_true_f0_hi)} |")
        P('')
    if len(m2s):
        P('**S6 M2 attribute readouts (ridge probes refitted on the 9,108 true title-position residuals with the published setup: team folds, ridge_cv alpha grid; applied to the fict residual; scored against the TRUE paper\'s labels; all 1,127 papers unless stated):**'); P('')
        P('| layer | group | field acc true | field acc fict | year R² true | year R² fict | log-cit R² true | log-cit R² fict | Δ cit R² (true − fict) |'); P('|---|---|---|---|---|---|---|---|---|')
        for _, x in m2s.iterrows():
            P(f"| L{int(x.layer)} | {x.group} | {x.field_true:.3f} | {x.field_fict:.3f} | {x.year_r2_true:.3f} | {x.year_r2_fict:.3f} | {x.cit_r2_true:.3f} | {x.cit_r2_fict:.3f} | {fmt(x.cit_r2_diff, x.cit_r2_diff_lo, x.cit_r2_diff_hi)} |")
        P(''); P('CIs for every cell: S6_M2_attributes.csv. R² is computed on the subset (1 − SS_res/SS_tot within the subset).'); P('')
    P('**S7 meaning dose (target, tertiles of the fict–true mpnet cosine, cut points on target papers):**'); P('')
    P('| tertile | cosine range | φ_T | R̄_T | n |'); P('|---|---|---|---|---|')
    for d_ in dose: P(f"| {d_['label'][-1]} | {d_['cos_lo']:.2f}–{d_['cos_hi']:.2f} | {fmt(d_['phi'], d_['phi_lo'], d_['phi_hi'])} | {fmt(d_['Rbar'], d_['R_lo'], d_['R_hi'])} | {d_['n']} |")
    P(''); P(f"φ(tertile 3) − φ(tertile 1) = {fmt(*dose_trend)}. Title-text similarity predicts φ rising with cosine; H2 predicts a low, flat φ."); P('')
    P('## 3. Sensitivity analyses (verdict by the same rule)'); P('')
    P('| analysis | φ_T | R̄_T | n | verdict (rule) | borderline |'); P('|---|---|---|---|---|---|')
    P(f"| primary | {fmt(prim['phi'], prim['phi_lo'], prim['phi_hi'])} | {fmt(prim['Rbar'], prim['R_lo'], prim['R_hi'])} | {prim['n']} | {prim['verdict']} | {prim['borderline']} |")
    for s in sens:
        if 'phi' not in s: P(f"| {s['label']} | n/a | n/a | {s['n']} | too few papers | |"); continue
        P(f"| {s['label']} | {fmt(s['phi'], s['phi_lo'], s['phi_hi'])} | {fmt(s['Rbar'], s['R_lo'], s['R_hi'])} | {s['n']} | {s['verdict']} | {s['borderline']} |")
    P('')
    if len(tl):
        P('**(f) Title likelihood** (mean per-token log-probability of the title tokens under the model, prompt prefix only):'); P('')
        P('| group | true | fict | false_0 | mean false_0..4 | true − fict |'); P('|---|---|---|---|---|---|')
        for grp in ('target', 'control'):
            q = tl.reindex(keep[keep.group == grp].paper_id); P(f"| {grp} | {q.true.mean():.3f} | {q.fict.mean():.3f} | {q.false_0.mean():.3f} | {q.false_mean.mean():.3f} | {q.true_minus_fict.mean():+.3f} |")
        P(''); P('CIs: Sf_title_logprob.csv. φ_T by tertile of (true − fict) title log-prob: rows (f) above.'); P('')
    P('## 4. Exclusions'); P('')
    P(f"- Fixed by the generation rule (before the run): {len(excl)} papers without a valid fictitious title ({(excl.group == 'target').sum()} target, {(excl.group == 'control').sum()} control); reasons: {excl.reason.value_counts().to_dict()}. List: raw/a20v2_freeze/exclusions.csv (= h2_fictitious/v3/excluded.csv).")
    P(f"- Prompt context > 512 tokens (or aligned tail < 3): {int(excl.reason.str.startswith(('context', 'aligned')).sum())} (max context of the kept fict prompts {fz.get('max_context')} tokens).")
    P(f"- Run-time (scoring failure / missing rows): {len(excl_rt)}" + (': ' + '; '.join(f"{x['paper_id'][:10]} {x['reason']}" for x in excl_rt[:20]) if excl_rt else '.'))
    P(f"- Analysed: {len(keep)} papers ({(keep.group == 'target').sum()} target, {(keep.group == 'control').sum()} control); within-bin weights use these papers.")
    P('')
    P('## 5. Parity and in-job self-checks (WARN = threshold missed; work continued under the project tolerance rule)'); P('')
    if par:
        pc = par.get('checks', par)
        P(f"Parity (shard 0, {pc.get('n_papers')} papers, GPU {pc.get('gpu')}; true and false_0..4 re-scored with the Stage 10 code vs the stored Stage 10 files; thresholds {pc.get('thresholds')}): **{pc.get('status')}**.")
        P(''); P('| condition | readout@layer | tokens | rank equal | mean abs Δlog10 rank | max abs Δlogprob | max abs Δ paper mean_nlr |'); P('|---|---|---|---|---|---|---|')
        for k_, v in pc.get('pairs', {}).items():
            cnd, rl = k_.split('|')
            if rl.startswith(('final', 'logit@56', 'jlens_public@56')) or cnd == 'true':
                P(f"| {cnd} | {rl} | {v['n_tokens']} | {v['rank_equal_share']:.3f} | {v['mean_abs_dlog10rank']:.4f} | {v['max_abs_dlogprob']:.3f} | {v['paper_mean_nlr_max_abs_diff']:.4f} |")
        P(''); P(f"WARN pairs: {pc.get('warn_pairs') or 'none'} (all pairs in raw/a20v2_checks/parity_000.json)."); P('')
    else: P('Parity: not available.'); P('')
    warns = {k: v for k, v in checks.items() if v.get('status') == 'WARN'}
    P(f"Unit self-checks: {len(checks)} units, {len(warns)} WARN." + ('' if not warns else ' WARN units: ' + '; '.join(f"{k}: " + json.dumps({kk: vv for kk, vv in (v['checks'] or {}).items() if kk not in ('pairs',)}, default=str)[:300] for k, v in list(warns.items())[:12])))
    pchk = [v['checks'] for k, v in checks.items() if k.startswith('patch_') and v.get('checks')]
    if pchk:
        P(f"Patch checks over {len(pchk)} shards: L63 == fict share min {min(c_['L63_equals_fict_share'] for c_ in pchk):.4f} (threshold 0.99); "
          f"false_0 rank equal to stored Stage 11 E1 min {min(c_.get('false_vs_stage11_rank_equal_share', np.nan) for c_ in pchk):.3f} (threshold 0.75), "
          f"mean abs Δlog10 rank max {max(c_.get('false_vs_stage11_mean_abs_dlog10rank', np.nan) for c_ in pchk):.4f} (threshold 0.05); "
          f"fict rank (patch run) = score unit final@63 share min {min(c_.get('fict_vs_score_final_equal_share', np.nan) for c_ in pchk):.3f}.")
    tchk = [v['checks'] for k, v in checks.items() if k.startswith('titlepos_') and v.get('checks')]
    if tchk:
        P(f"Titlepos checks over {len(tchk)} shards: true title residual vs stored Stage 11 (fp16) relative L2 max {max((c_.get('true_resid_title_rel_l2_vs_stage11_max') or np.nan) for c_ in tchk):.4f} (threshold 0.05).")
    P('')
    gh, det = gpu_hours(Path(a.raw))
    P('## 6. GPU cost'); P('')
    P(f"Measured: **{gh:.2f} GPU-h** (sacct ElapsedRaw × GPUs, all addendum-20 main-run GPU jobs). Addendum estimate ≈ 1.2–1.8 GPU-h (allocated ≤ 3; hard cap 5).")
    for d_ in det: P(f'- {d_}')
    gv1, dv1 = gpu_hours_jobs(['12014065', '12014453', '12014454'])
    P(f'- Plus the INVALID v1 run (freeze bug: fict prompt = true title; outputs raw/a20_*, summary_a20_INVALID_v1_fict_eq_true/): {gv1:.2f} GPU-h ({"; ".join(dv1)}). Total addendum-20 main-run GPU incl. v1: {gh + gv1:.2f} GPU-h.')
    P('')
    P('## 7. Implementation notes (choices the addendum did not spell out)'); P('')
    P('- S_true and S_false_k are the stored Stage 10 values (A100); S_fict is from this run (see §5 for the hardware parity of re-scored true/false_k).')
    P('- φ within-bin T − C (S2): per-bin ratio of sums, bin weights n_t·n_c/(n_t+n_c) fixed at the point counts; the plain pooled φ_T − φ_C is shown beside it.')
    P('- S4: rec_fict numerator uses this run\'s false_0 baseline (same forward pass as the patched runs); denominator (true − false_0) and rec_true(l) come from the stored Stage 11 E1 run (paper means of token log10(1/rank), then mean over papers).')
    P('- S5/S6: the published probes were not stored as weights, so they are refitted with the published setup on the 9,108 true runs (team folds; training-fold standardisation; same alpha grids); the fict residual of a paper is scored by the model of the fold that held that paper out. S5 probe(false_0) uses the stored Stage 11 false_0 residual.')
    P('- S7 and (f): tertile cut points on the target papers.')
    P(f'- (d1) first author = the lowest scored author index of the paper. Probe layers used: {probe_layers}.')
    P('')
    P('Files: ' + ', '.join(sorted(x.name for x in out.glob('*.csv'))) + ', a20_results.json.')
    (out / 'a20_report.md').write_text('\n'.join(L) + '\n')


if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning); main()
