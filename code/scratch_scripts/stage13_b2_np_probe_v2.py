"""Batch 2, addendum 11 part A: name-position probe VERSION 2 (CPU), one job per layer. Deviation D11-1 v2
(config/prereg_addendum11_deviations_v2.json, sha256 d6d802fd...): identical to stage13_b2_np_probe.py (not changed) except that the
per-false-title permutation-control scores, which the old probe computed and then collapsed into ctrl_*0 / ctrl_*5, are also stored
per paper (ctrl_any_t, ctrl_any_f0..f4, ctrl_field_t, ctrl_field_f0..f4; stage13_b2A_cols_v2.py), and the output directory is
summary_b2_np/probe_v2. Every other column is computed by the same lines (hard check: equal to the old probe, max |diff| = 0).


Plan (locked): 381_stage13/config/prereg_addendum11.json, part A "probe", "title-specific signal", "controls".
Per layer l in (32, 40, 48, 52, 56) and run (stage13_b2A_cols.NP_RUNS: colon_first = the ':' position / first-token run =
token_index 0 rows; initial = initial_first; given_first; given_cont; surname_first; surname_cont):
  rows    every name-token-predicting position whose predicted token has the run's role (all authors, Stage 10 contexts)
  X       layer-l residual at the position (raw/b2_npprobe/<cond>, fp16)          Y  the L63 residual at the SAME position under
          the true title (raw/allTok_L63, reused as the plan says)
  fit     ridge X -> Y on TRUE-title rows only; folds = archived author-team folds (stage13_cpu.group_folds on the 9,108
          Stage 11 titlepos ids, k = 5; a row inherits its paper's fold); standardisation fitted on the training folds;
          alpha in (0.1, 1, 10) x trace(G)/d chosen on fold-0 held-out MSE (the E4b / addendum-9 code:
          stage13_b1_e4b5_probe.ridge_fold_preds_multi, imported by path, which decodes the false inputs through the same map)
  score   held-out prediction from the true-title and from each false_k-title residual -> final norm + lm_head rows of the
          9,137 name token ids (addendum-9 vocabulary, summary_alltok/vocab_rows.npz) -> log10(1/rank) of the TRUE gold next
          token within those ids; paper score = mean over its rows; spec5 = true - mean_k false_k; spec0 = true - false_0
  reuse   dropped_k: the paper's false_k donor is a paper of this run in another fold (its true-title rows were training rows);
          drop5 = any k (5-donor rule, primary), drop0 = dropped_0 (reported beside it, plan)
  control the E4b permutation controls with default_rng(3712) drawn exactly as stage13_b1_e4b5_probe (over this run's paper
          list): the same predictions scored against the gold tokens of a random other paper (any field / same field);
          paper control score = mean over its rows and over the other paper's gold tokens of the run (interpretation for
          position-level predictions, see the handoff); ctrl_*5 = true - mean_k false_k, ctrl_*0 = true - false_0
  ceiling the actual L63 target decoded the same way
Output: summary_b2_np/probe_v2/perpaper_<run>_L<l>.parquet, pertoken_<run>_L<l>.parquet, fit_<run>_L<l>.json (skip-if-exists).
Usage:  stage13_b2_np_probe.py --layer 40 [--runs surname_first,initial]     |   --tiny --layer 40 (root b2_np_tiny)
"""
import argparse, importlib.util, json, sys, time, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
T0 = time.time()
def log(*a):
    try: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)
    except Exception: pass


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols_v2.py', 'b2A_cols_v2')
P5 = load(H / '13_stage13/stage13_b1_e4b5_probe.py', 'e4b5p'); P9 = P5.P9


def titlepos_pids():
    """the Stage 11 titlepos 'true' paper order (the id list the archived folds were made for)"""
    return np.concatenate([np.load(f)['resid_paper_id'] for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))])


def load_layer(raw, cond, l, rows_ref=None):
    fs = sorted((raw / cond).glob('shard_*.npz'))
    zs = [np.load(f) for f in fs]
    rid = np.concatenate([z[K.ROW_ID] for z in zs]); X = np.concatenate([z[K.np_resid_key(l)] for z in zs])
    o = np.argsort(rid, kind='stable'); rid, X = rid[o], X[o]
    if rows_ref is not None and not np.array_equal(rid, rows_ref): raise SystemExit(f'{cond}: row ids differ from true')
    return rid, X, len(fs)


def rank_rows(lg, gidx):
    """log10(1/rank) of gold column gidx[i] in row i (rank = 1 + number of strictly greater logits)"""
    g = lg[np.arange(len(gidx)), gidx]
    return -np.log10(1 + (lg > g[:, None]).sum(1))


def ctrl_score(lg_rows, gcols):
    """mean over rows and over the other paper's gold columns of log10(1/rank)"""
    v = lg_rows[:, gcols]                                                       # [r, g]
    step = max(1, int(2e7 // max(1, len(gcols) * lg_rows.shape[1])))           # bound the [r, g, V] comparison in memory
    rk = np.concatenate([1 + (lg_rows[i:i + step, None, :] > v[i:i + step, :, None]).sum(-1) for i in range(0, len(lg_rows), step)])
    return float((-np.log10(rk)).mean())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--layer', type=int, required=True); ap.add_argument('--runs', default=','.join(K.NP_RUNS))
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    l = a.layer
    if l not in K.NP_LAYERS: raise SystemExit(f'layer {l} not in plan {K.NP_LAYERS}')
    root = R13 / 'b2_np_tiny' if a.tiny else R13
    if (root / 'summary_b2_np/HARD_CHECK1_FAILED').exists(): raise SystemExit('HARD_CHECK1_FAILED present: stop')
    OUT = root / 'summary_b2_np' / K.NP_PROBE_DIR_V2; OUT.mkdir(parents=True, exist_ok=True)
    runs = a.runs.split(',')
    if all((OUT / f'perpaper_{r}_L{l}.parquet').exists() for r in runs): log('all outputs exist'); return
    raw = root / 'raw/b2_npprobe'
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    pid = titlepos_pids(); fold_full = c13.group_folds(pid, k=5)[0]
    F = dict(zip(pid, fold_full)); pidx = {p: i for i, p in enumerate(pid)}
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet')
    DON = {k: ft[ft.k == k].set_index('paper_id').donor_paper_id.to_dict() for k in K.KS}
    FIELD = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'field']).set_index('paper_id').field.to_dict()
    # residuals of this layer, all conditions, aligned by row_id
    rid, Xt, nt = load_layer(raw, 'true', l)
    if not a.tiny and nt != 72: raise SystemExit(f'true: {nt}/72 shards')
    XF = {}
    for k in K.KS:
        _, XF[k], n = load_layer(raw, f'false_{k}', l, rid)
        if not a.tiny and n != 72: raise SystemExit(f'false_{k}: {n}/72 shards')
    log(f'L{l} residuals: {len(rid)} rows x {Xt.shape[1]} (6 conditions)')
    zs = [np.load(f) for f in sorted((R13 / ('alltok_tiny' if a.tiny else '') / 'raw/allTok_L63').glob('shard_*.npz'))]
    yid = np.concatenate([z['row_id'] for z in zs]); Yall = np.concatenate([z['resid'] for z in zs]); del zs
    ypos = pd.Series(np.arange(len(yid)), index=yid).reindex(rid)
    if ypos.isna().any(): raise SystemExit(f'{int(ypos.isna().sum())} rows have no allTok_L63 target')
    ypos = ypos.to_numpy().astype(int)
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role']).set_index('row_id').loc[rid].reset_index()
    if a.tiny:
        d = Xt.shape[1]; rng0 = np.random.default_rng(0); ids = np.array(sorted(pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['token_id']).token_id.unique()))
        V = P9.Vocab(ids, rng0.standard_normal((len(ids), d)).astype(np.float16), np.ones(d, np.float32), 1e-6)
    else:
        vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); V = P9.Vocab(vr['token_id'], vr['lm_head_rows'], vr['norm_weight'], vr['eps'])
    log('vocab', len(V.vid))
    for run in runs:
        fo = OUT / f'perpaper_{run}_L{l}.parquet'
        if fo.exists(): log('exists', fo.name); continue
        role = K.NP_RUNS[run]
        mk = (tok.token_index.to_numpy() == 0) if role is None else (tok.role.to_numpy() == role)
        mk &= tok.paper_id.isin(pidx).to_numpy()
        ri = np.where(mk)[0]; t = tok.iloc[ri].reset_index(drop=True)
        P = np.array(sorted({pidx[p] for p in t.paper_id})); pp = pid[P]; n = len(P); pnum = {p: i for i, p in enumerate(pp)}
        rpaper = t.paper_id.map(pnum).to_numpy(); fold = fold_full[P][rpaper]          # row fold = paper fold
        gidx = np.array([V.vid[int(x)] for x in t.token_id])
        X = Xt[ri].astype(np.float32); Xf = [XF[k][ri].astype(np.float32) for k in K.KS]; Y = Yall[ypos[ri]].astype(np.float32)
        trainset = set(pp)
        dk = {k: np.array([(DON[k].get(p) in trainset) and (F[DON[k][p]] != F[p]) for p in pp]) for k in K.KS}
        rng = np.random.default_rng(K.NP_RNG_SEED); perm_any = rng.permutation(n); fields = np.array([FIELD[p] for p in pp]); perm_field = np.arange(n)
        for fl in np.unique(fields):
            idx = np.where(fields == fl)[0]; perm_field[idx] = idx[rng.permutation(len(idx))]
        prow = pd.Series(np.arange(len(t))).groupby(rpaper).apply(np.array).to_dict()                     # paper -> its rows
        pgold = {m: gidx[prow[m]] for m in prow}
        log(run, f'L{l}', 'rows', len(t), 'papers', n, 'dropped_0', int(dk[0].sum()), 'dropped any of 5', int(np.any([dk[k] for k in K.KS], 0).sum()))
        PT, PFs, best, errs = P5.ridge_fold_preds_multi(X, Xf, Y, fold, alphas=K.NP_ALPHAS)
        del X, Xf
        tok_true = np.full(len(t), np.nan); tok_false = {k: np.full(len(t), np.nan) for k in K.KS}; ceil_tok = np.full(len(t), np.nan)
        ctrl = {key: np.full(n, np.nan) for key in [f'{c}_t' for c in ('any', 'field')] + [f'{c}_f{k}' for c in ('any', 'field') for k in K.KS]}
        for fk in range(5):
            te = np.where(fold == fk)[0]
            if not len(te): continue
            LT = V.logits(PT[te]); LF = [V.logits(PF[te]) for PF in PFs]; LY = V.logits(Y[te])
            tok_true[te] = rank_rows(LT, gidx[te]); ceil_tok[te] = rank_rows(LY, gidx[te]); del LY
            for k in K.KS: tok_false[k][te] = rank_rows(LF[k], gidx[te])
            loc = {r: j for j, r in enumerate(te)}
            for m in np.unique(rpaper[te]):
                lr = np.array([loc[r] for r in prow[m]])
                for tag, perm in (('any', perm_any), ('field', perm_field)):
                    gc = pgold[perm[m]]
                    ctrl[f'{tag}_t'][m] = ctrl_score(LT[lr], gc)
                    for k in K.KS: ctrl[f'{tag}_f{k}'][m] = ctrl_score(LF[k][lr], gc)
            del LT, LF
        r2 = 1 - ((PT - Y) ** 2).sum() / ((Y - Y.mean(0)) ** 2).sum(); del PT, PFs, Y
        pm = lambda v: pd.Series(v).groupby(rpaper).mean().reindex(range(n)).to_numpy()
        S = {'true': pm(tok_true), **{f'false_{k}': pm(tok_false[k]) for k in K.KS}}; mf = np.mean([S[f'false_{k}'] for k in K.KS], 0)
        df = pd.DataFrame({K.PAPER_ID: pp, K.FOLD: fold_full[P], K.N_TOK: np.bincount(rpaper, minlength=n), K.NP_TRUE: S['true'],
                           **{K.np_false(k): S[f'false_{k}'] for k in K.KS}, K.NP_FALSE_MEAN5: mf, K.NP_SPEC5: S['true'] - mf, K.NP_SPEC0: S['true'] - S['false_0'],
                           **{K.np_spec_k(k): S['true'] - S[f'false_{k}'] for k in K.KS},
                           'ctrl_any0': ctrl['any_t'] - ctrl['any_f0'], 'ctrl_any5': ctrl['any_t'] - np.mean([ctrl[f'any_f{k}'] for k in K.KS], 0),
                           'ctrl_field0': ctrl['field_t'] - ctrl['field_f0'], 'ctrl_field5': ctrl['field_t'] - np.mean([ctrl[f'field_f{k}'] for k in K.KS], 0),
                           K.NP_CEIL: pm(ceil_tok), **{K.np_dropped(k): dk[k] for k in K.KS}, K.NP_DROP0: dk[0], K.NP_DROP5: np.any([dk[k] for k in K.KS], 0),
                           'self_any': perm_any == np.arange(n), 'self_field': perm_field == np.arange(n),
                           **{K.np_ctrl_true(tag): ctrl[f'{tag}_t'] for tag in K.NP_CTRL_TAGS},
                           **{K.np_ctrl_false(tag, k): ctrl[f'{tag}_f{k}'] for tag in K.NP_CTRL_TAGS for k in K.KS}})[K.NP_PERPAPER_COLS_V2]
        pd.DataFrame({K.ROW_ID: t.row_id.to_numpy(), K.PAPER_ID: t.paper_id.to_numpy(), 'nlr_true': tok_true,
                      **{f'nlr_false_{k}': tok_false[k] for k in K.KS}})[K.NP_PERTOKEN_COLS].to_parquet(OUT / f'pertoken_{run}_L{l}.parquet', index=False)
        fit = dict(run=run, layer=l, alpha=best, alpha_errs_fold0=errs, n_rows=int(len(t)), n_papers=int(n), heldout_r2_true=float(r2),
                   n_drop0=int(dk[0].sum()), n_drop5=int(df[K.NP_DROP5].sum()), tiny=a.tiny)
        (OUT / f'fit_{run}_L{l}.json').write_text(json.dumps({k_: fit[k_] for k_ in K.NP_FIT_KEYS}))
        df.to_parquet(fo, index=False)
        try:
            k0 = ~df.drop0; k5 = ~df.drop5
            log(run, f'L{l}', 'alpha', best, f'R2 {r2:.3f}', f'spec5 kept0 {np.nanmean(df.spec5[k0]):+.4f}', f'spec0 kept0 {np.nanmean(df.spec0[k0]):+.4f}',
                f'spec5 kept5 {np.nanmean(df.spec5[k5]) if k5.any() else float("nan"):+.4f} (n {int(k5.sum())})', f'ctrl_any5 {np.nanmean(df.ctrl_any5[k0]):+.4f}',
                f'true {np.nanmean(df["true"]):+.3f} ceiling {np.nanmean(df.ceiling):+.3f}')
        except Exception as e: log('WARN summary print failed', repr(e))


if __name__ == '__main__':
    main()
