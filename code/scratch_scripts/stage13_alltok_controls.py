"""Addendum 9 follow-up (user request 2026-11-05 ~18:00): the two E4b permutation controls for the all-token probe.

For each run (e4b_parity, first_alltok, 5 roles) and layer, the probe is refit exactly as stage13_alltok_probe.py
(same inputs, archived team folds, training-fold standardisation, alpha on fold 0) and each paper's predictions
(true-title and false_0-title residual) are scored against the gold tokens of
  (1) a random other paper  (perm_any),
  (2) a random other paper of the same field (perm_field),
as in stage12_cpu.probe_controls (the confirmatory E4b controls; rng default_rng(3712) as in stage13_split_compare).
spec_ctrl = nlr(pred_true, gold_other) - nlr(pred_false, gold_other). A paper-specific signal should vanish (~0).
Also stores the real spec so the parity with stage13_alltok_probe.py can be checked (WARN only).
Writes summary_alltok/controls/perpaper_{run}_L{l}.parquet (skip if exists). CPU only.
"""
import argparse, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


P9 = load(H / '13_stage13/stage13_alltok_probe.py', 'p9')
R10, R11, R13 = P9.R10, P9.R11, P9.R13


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=','.join(P9.ALL_RUNS)); ap.add_argument('--layers', default=None)
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    root = R13 / 'alltok_tiny' if a.tiny else R13
    OUT = root / 'summary_alltok/controls'; OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    Xt, Ct, pid, gold, players = P9.loadc('true'); Xf, _, pidf, _, _ = P9.loadc('false_0')
    order = {p: i for i, p in enumerate(pidf)}; Xf = Xf[[order[p] for p in pid]]
    fold_full = c13.group_folds(pid, k=5)[0]
    F = dict(zip(pid, fold_full)); pidx = {p: i for i, p in enumerate(pid)}
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); DONOR = ft[ft.k == 0].set_index('paper_id').donor_paper_id.to_dict()
    FIELD = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'field']).set_index('paper_id').field.to_dict()
    layers = [int(l) for l in players] if not a.layers else [int(x) for x in a.layers.split(',')]
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
    rf = sorted((root / 'raw/allTok_L63').glob('shard_*.npz'))
    if any(r != 'e4b_parity' for r in a.runs.split(',')):
        if not a.tiny and len(rf) != 72: raise SystemExit(f'allTok_L63 incomplete: {len(rf)}/72 shards')
        zs = [np.load(f) for f in rf]; rid = np.concatenate([z['row_id'] for z in zs]); RES = np.concatenate([z['resid'] for z in zs])
        rpos = pd.Series(np.arange(len(rid)), index=rid); toks = toks[toks.row_id.isin(rid)]
    pv = np.load(R11 / 'raw/probe_vocab/shard_000.npz'); V_e4b = P9.Vocab(pv['token_id'], pv['lm_head_rows'], pv['norm_weight'], pv['eps'])
    if a.tiny:
        ids = np.array(sorted(toks.token_id.unique())); rng0 = np.random.default_rng(0); d = RES.shape[1]
        V_all = P9.Vocab(ids, rng0.standard_normal((len(ids), d)).astype(np.float16), np.ones(d, np.float32), 1e-6)
    else:
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
        fold = fold_full[P]; trainset = set(pid[P])
        dropped = np.array([(DONOR.get(p) in trainset) and (F[DONOR[p]] != F[p]) for p in pid[P]])
        rng = np.random.default_rng(3712); n = len(P)
        perm_any = rng.permutation(n); fields = np.array([FIELD[p] for p in pid[P]]); perm_field = np.arange(n)
        for fl in np.unique(fields):
            idx = np.where(fields == fl)[0]; perm_field[idx] = idx[rng.permutation(len(idx))]
        for l in layers:
            fo = OUT / f'perpaper_{run}_L{l}.parquet'
            if fo.exists(): print('exists', fo.name, flush=True); continue
            li = [int(x) for x in players].index(l)
            PT, PF, best, _ = P9.ridge_fold_preds(Xt[P, li].astype(np.float32), Xf[P, li].astype(np.float32), Y, fold)
            res = {k: np.full(n, np.nan) for k in ['spec', 'spec_any', 'spec_field']}
            for k in range(5):
                te = np.where(fold == k)[0]
                if not len(te): continue
                LT, LF = V.logits(PT[te]), V.logits(PF[te])
                for j, m in enumerate(te):
                    for key, src in (('spec', m), ('spec_any', perm_any[m]), ('spec_field', perm_field[m])):
                        gl = golds[src]
                        if not gl: continue
                        a1, a2 = V.nlr(LT[j], gl), V.nlr(LF[j], gl)
                        if len(a1): res[key][m] = a1.mean() - a2.mean()
            pd.DataFrame({'paper_id': pid[P], 'fold': fold, 'dropped': dropped, **res,
                          'self_any': perm_any == np.arange(n), 'self_field': perm_field == np.arange(n)}).to_parquet(fo, index=False)
            print(run, f'L{l}', 'alpha', best, 'spec', np.nanmean(res['spec'][~dropped]), 'any', np.nanmean(res['spec_any'][~dropped]),
                  'field', np.nanmean(res['spec_field'][~dropped]), flush=True)


if __name__ == '__main__':
    main()
