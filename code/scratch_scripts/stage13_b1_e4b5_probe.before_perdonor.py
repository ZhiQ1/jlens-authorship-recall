"""Addendum 10 item 4 (batch 1), CPU probe: E4b first-token probe and addendum-9 all-token role probes, title-specific signal
against the MEAN of five false titles.

Plan (locked): 381_stage13/config/prereg_addendum10.json (sha256 8243a4ed...), item 4; probe definitions: addendum 9 (a9896357...).
The fit is unchanged (13_stage13/stage13_alltok_probe.py, imported by path and not edited: Vocab, the same ridge code with
training-fold standardisation and alpha on fold 0, the same targets, gold tokens and rank vocabularies, archived team folds).
The one change: each held-out paper's prediction is decoded from the true-title residual and from EACH of the five false-title
residuals (false_0 = stored Stage 11 titlepos; false_1..4 = 381_stage13/raw/b1_titlepos5), and
    spec5 = probe(true) - mean_k probe(false_k)      (primary)        spec0 = probe(true) - probe(false_0)   (addendum 9 / E4b)
Title reuse (probe trained on true runs): dropped_k = the true title of the paper's false_k donor is in this probe's training
folds (donor in the run's paper set, in another fold). drop5 = any k (primary 5-donor rule); drop0 = dropped_0 (E4b rule).
Permutation controls (stage13_alltok_controls.py definitions, rng default_rng(3712), same permutations): the same predictions
scored against the gold tokens of a random other paper (any / same field), for spec0 and spec5.
Output: summary_b1_e4b5/probe/perpaper_<run>_L<l>.parquet + fit_<run>_L<l>.json (skip-if-exists).
Usage:  stage13_b1_e4b5_probe.py --runs e4b_parity,surname_first [--layers 40] | --tiny (b1_tiny root)
"""
import argparse, importlib.util, json, time, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum10.json'; PLAN_SHA = '8243a4edebcc4da00933c7647eb4e322b0e8831dbac632622e52a8316f9e7e05'
KS = [0, 1, 2, 3, 4]
T0 = time.time(); log = lambda *a: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


P9 = load(H / '13_stage13/stage13_alltok_probe.py', 'p9')


def ridge_fold_preds_multi(X, XFs, Y, fold, alphas=P9.ALPHAS):
    """P9.ridge_fold_preds (line for line) with several false-title inputs decoded through the same fitted map."""
    best = None; errs_out = None; PT = np.zeros_like(Y); PFs = [np.zeros_like(Y) for _ in XFs]
    for k in range(5):
        tr, te = fold != k, np.where(fold == k)[0]
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


def load_cond(d, nsh=None):
    fs = sorted(d.glob('shard_*.npz'))[:nsh]; zs = [np.load(f) for f in fs]
    return np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]), zs, len(fs)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=','.join(P9.ALL_RUNS)); ap.add_argument('--layers', default=None)
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    root = R13 / 'b1_tiny' if a.tiny else R13
    if (root / 'summary_b1_e4b5/HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    OUT = root / 'summary_b1_e4b5/probe'; OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    new = root / 'raw/b1_titlepos5'
    src = {'true': (new / 'true') if a.tiny else (R11 / 'raw/titlepos/true'), 0: (new / 'false_0') if a.tiny else (R11 / 'raw/titlepos/false_0')}
    src |= {k: new / f'false_{k}' for k in KS[1:]}
    Xt, Ct, pid, zt, nt = load_cond(src['true'])
    if not a.tiny and nt != 72: raise SystemExit(f'true: {nt}/72 shards')
    if 'kind' in zt[0].files:
        gold = pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zt])
    else:
        gold = pd.concat([pd.DataFrame({'paper_id': z['gold_paper_id'], 'kind': 'first', 'gold': z['gold']}) for z in zt])
    players = zt[0]['probe_layers']; del zt
    Xf = {}
    for k in KS:
        x, _, pk, _, n = load_cond(src[k])
        if not a.tiny and n != 72: raise SystemExit(f'false_{k}: {n}/72 shards')
        if set(pk) != set(pid): raise SystemExit(f'false_{k}: paper set differs from true')
        o = {p: i for i, p in enumerate(pk)}; Xf[k] = x[[o[p] for p in pid]]; log(f'false_{k}', x.shape)
    fold_full = c13.group_folds(pid, k=5)[0]
    F = dict(zip(pid, fold_full)); pidx = {p: i for i, p in enumerate(pid)}
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet')
    DON = {k: ft[ft.k == k].set_index('paper_id').donor_paper_id.to_dict() for k in KS}
    FIELD = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'field']).set_index('paper_id').field.to_dict()
    layers = [int(l) for l in players] if not a.layers else [int(x) for x in a.layers.split(',')]
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
    aroot = (R13 / 'alltok_tiny') if a.tiny else R13
    if any(r != 'e4b_parity' for r in a.runs.split(',')):
        rf = sorted((aroot / 'raw/allTok_L63').glob('shard_*.npz'))
        if not a.tiny and len(rf) != 72: raise SystemExit(f'allTok_L63 incomplete: {len(rf)}/72 shards')
        zs = [np.load(f) for f in rf]; rid = np.concatenate([z['row_id'] for z in zs]); RES = np.concatenate([z['resid'] for z in zs])
        rpos = pd.Series(np.arange(len(rid)), index=rid); toks = toks[toks.row_id.isin(rid)]
    pv = np.load(R11 / 'raw/probe_vocab/shard_000.npz')
    if a.tiny:
        d = Ct.shape[-1]; rng0 = np.random.default_rng(0)
        V_e4b = P9.Vocab(pv['token_id'], rng0.standard_normal((len(pv['token_id']), d)).astype(np.float16), np.ones(d, np.float32), 1e-6)
        ids = np.array(sorted(toks.token_id.unique())); V_all = P9.Vocab(ids, rng0.standard_normal((len(ids), d)).astype(np.float16), np.ones(d, np.float32), 1e-6)
    else:
        V_e4b = P9.Vocab(pv['token_id'], pv['lm_head_rows'], pv['norm_weight'], pv['eps'])
        vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); V_all = P9.Vocab(vr['token_id'], vr['lm_head_rows'], vr['norm_weight'], vr['eps'])
    for run in a.runs.split(','):
        if run == 'e4b_parity':
            P = np.arange(len(pid)); Y = Ct[:, -1].astype(np.float32)
            g = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict(); golds = [g.get(p, []) for p in pid]; V = V_e4b
        else:
            t = toks[toks.token_index == 0] if run == 'first_alltok' else toks[toks.role == P9.ROLE_RUNS[run]]
            t = t[t.paper_id.isin(pidx)].sort_values('row_id'); grp = t.groupby('paper_id', sort=False)
            P = np.array(sorted(pidx[p] for p in grp.groups)); pp = pid[P]
            Y = np.zeros((len(P), RES.shape[1]), np.float32); golds = []
            for n, p in enumerate(pp):
                s = t.iloc[grp.indices[p]]; Y[n] = RES[rpos.loc[s.row_id].to_numpy()].astype(np.float32).mean(0); golds.append(s.token_id.tolist())
            V = V_all
        fold = fold_full[P]; trainset = set(pid[P]); n = len(P)
        dk = {k: np.array([(DON[k].get(p) in trainset) and (F[DON[k][p]] != F[p]) for p in pid[P]]) for k in KS}
        lgY = V.logits(Y); ceil = np.array([np.mean(V.nlr(lgY[i], golds[i])) if golds[i] else np.nan for i in range(n)]); del lgY
        rng = np.random.default_rng(3712); perm_any = rng.permutation(n); fields = np.array([FIELD[p] for p in pid[P]]); perm_field = np.arange(n)
        for fl in np.unique(fields):
            idx = np.where(fields == fl)[0]; perm_field[idx] = idx[rng.permutation(len(idx))]
        log(run, 'papers', n, 'dropped_0', int(dk[0].sum()), 'dropped any of 5', int(np.any([dk[k] for k in KS], 0).sum()))
        for l in layers:
            fo = OUT / f'perpaper_{run}_L{l}.parquet'
            if fo.exists(): log('exists', fo.name); continue
            li = [int(x) for x in players].index(l)
            PT, PFs, best, errs = ridge_fold_preds_multi(Xt[P, li].astype(np.float32), [Xf[k][P, li].astype(np.float32) for k in KS], Y, fold)
            S = {key: np.full(n, np.nan) for key in ['true'] + [f'false_{k}' for k in KS] + [f'{c}_{w}_{k}' for c in ('any', 'field') for w in ('t', 'f') for k in (['t'] if w == 't' else KS)]}
            for fk in range(5):
                te = np.where(fold == fk)[0]
                if not len(te): continue
                LT = V.logits(PT[te]); LF = [V.logits(PF[te]) for PF in PFs]
                for j, m in enumerate(te):
                    for tag, sidx in (('', m), ('any', perm_any[m]), ('field', perm_field[m])):
                        gl = golds[sidx]
                        if not gl: continue
                        a1 = V.nlr(LT[j], gl)
                        if not len(a1): continue
                        if tag == '':
                            S['true'][m] = a1.mean()
                            for k in KS: S[f'false_{k}'][m] = V.nlr(LF[k][j], gl).mean()
                        else:
                            S[f'{tag}_t_t'][m] = a1.mean()
                            for k in KS: S[f'{tag}_f_{k}'][m] = V.nlr(LF[k][j], gl).mean()
            mf = np.mean([S[f'false_{k}'] for k in KS], 0)
            df = pd.DataFrame({'paper_id': pid[P], 'fold': fold, 'n_tok': [len(x) for x in golds], 'true': S['true'],
                               **{f'false_{k}': S[f'false_{k}'] for k in KS}, 'false_mean5': mf,
                               'spec0': S['true'] - S['false_0'], 'spec5': S['true'] - mf, **{f'spec_k{k}': S['true'] - S[f'false_{k}'] for k in KS},
                               'ctrl_any0': S['any_t_t'] - S['any_f_0'], 'ctrl_any5': S['any_t_t'] - np.mean([S[f'any_f_{k}'] for k in KS], 0),
                               'ctrl_field0': S['field_t_t'] - S['field_f_0'], 'ctrl_field5': S['field_t_t'] - np.mean([S[f'field_f_{k}'] for k in KS], 0),
                               'ceiling': ceil, **{f'dropped_{k}': dk[k] for k in KS}, 'drop0': dk[0], 'drop5': np.any([dk[k] for k in KS], 0),
                               'self_any': perm_any == np.arange(n), 'self_field': perm_field == np.arange(n)})
            r2 = 1 - ((PT - Y) ** 2).sum() / ((Y - Y.mean(0)) ** 2).sum()
            (OUT / f'fit_{run}_L{l}.json').write_text(json.dumps(dict(run=run, layer=l, alpha=best, alpha_errs_fold0=errs, n_papers=int(n), heldout_r2_true=float(r2),
                                                                      n_drop0=int(dk[0].sum()), n_drop5=int(df.drop5.sum()), tiny=a.tiny)))
            df.to_parquet(fo, index=False)
            log(run, f'L{l}', 'alpha', best, f'R2 {r2:.3f}', f'spec0 kept0 {np.nanmean(df.spec0[~df.drop0]):+.4f}', f'spec5 kept0 {np.nanmean(df.spec5[~df.drop0]):+.4f}',
                f'spec5 kept5 {np.nanmean(df.spec5[~df.drop5]) if (~df.drop5).any() else float("nan"):+.4f} (n {int((~df.drop5).sum())})')


if __name__ == '__main__':
    main()
