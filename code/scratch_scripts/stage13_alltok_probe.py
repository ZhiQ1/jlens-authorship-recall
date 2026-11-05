"""Addendum 9 (2026-11-05), CPU probe: title-position probe on ALL name tokens, by token role (extends Stage 11 E4b).

Plan (frozen): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum9.json (sha256 a9896357...).
Inputs  title-last residual at L16..L60 (Stage 11 raw/titlepos/{true,false_0}); targets from 381_stage13/raw/allTok_L63
        (the model's own L63 state at the position predicting each name token); lm_head rows + final norm from
        381_stage13/summary_alltok/vocab_rows.npz (all name token ids).
Runs    one probe per (run, layer); run = a token role or a parity run:
  initial        role initial_first   (the first token of an initial word; 'initial' in the plan)
  given_first, given_cont, surname_first, surname_cont      (Stage 10 cohort roles; punct and particle_* excluded)
  e4b_parity     EXACT E4b (confirmatory version: team folds, training-fold standardisation, title-reuse exclusion):
                 target = Stage 11 titlepos resid_colon L63, gold = titlepos 'first' tokens, rank vocabulary = Stage 11
                 probe_vocab (4,314 ids). Must reproduce summary_cpu_trainstd (group / title-reuse) per paper.
  first_alltok   first name token of every author, but with the all-token pipeline (target = recorded L63 state at the
                 token_index-0 rows, rank vocabulary = all name token ids): bridges E4b and the role runs.
Fit     per (run, layer): papers having >= 1 token of the role; target = MEAN recorded L63 state over that paper's tokens of
        the role (all authors); ridge, alpha in (0.1, 1, 10) x trace(G)/d chosen on fold 0 held-out MSE (as E4b), mu/sd from the
        training folds only; folds = archived author-team folds (stage13_cpu.group_folds on the 9,108 titlepos ids, k=5).
Score   decode (RMS final norm + lm_head rows) the held-out prediction from the true-title and the false_0-title residual; for
        EACH gold token of the role, log10(1/rank) within the rank vocabulary; paper score = mean over its tokens; spec =
        true - false_0. Title-reuse flag (as E4b, probe trained on true runs): drop test paper A when the true title of A's
        false_0 donor is in this probe's training folds. Also stored: 'ceiling' = the same score for the actual target state.
Output  OUT/perpaper_<run>_L<l>.parquet, OUT/pertoken_<run>_L<l>.parquet (role runs; row_id-level true/false scores),
        OUT/fit_<run>_L<l>.json.  Skip-if-exists.
Usage   stage13_alltok_probe.py --runs initial,surname_first [--layers 40]  |  --tiny (alltok_tiny root, random d=64 vocab)
"""
import argparse, importlib.util, json, os, time, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum9.json'; PLAN_SHA = 'a98963579aa2c4af0e0f266a97407c8f171d9dd47116ca7d1cac90e198d262c7'
ROLE_RUNS = {'initial': 'initial_first', 'given_first': 'given_first', 'given_cont': 'given_cont', 'surname_first': 'surname_first', 'surname_cont': 'surname_cont'}
ALL_RUNS = ['e4b_parity', 'first_alltok'] + list(ROLE_RUNS)
ALPHAS = (0.1, 1.0, 10.0)
T0 = time.time(); log = lambda *a: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def loadc(c, nsh=None):
    """as stage10_extra_r0r1.probe.loadc"""
    fs = sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))[:nsh]; zs = [np.load(f) for f in fs]
    return (np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]),
            pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zs]), zs[0]['probe_layers'])


class Vocab:
    def __init__(self, ids, W, nw, eps):
        self.W = W.astype(np.float32); self.nw = nw.astype(np.float32); self.eps = float(eps); self.vid = {int(t): i for i, t in enumerate(ids)}

    def logits(self, pred):
        """as E4b score(): RMS norm with the final-norm weight, then lm_head rows"""
        h = pred / np.sqrt((pred ** 2).mean(1, keepdims=True) + self.eps) * self.nw; return h @ self.W.T

    def nlr(self, lg_row, gold_ids):
        """log10(1/rank) of each gold token; rank = 1 + number of vocab logits strictly greater (E4b)"""
        gi = np.array([self.vid[x] for x in gold_ids if x in self.vid], int)
        if not len(gi): return np.array([])
        return -np.log10(1 + (lg_row[None, :] > lg_row[gi][:, None]).sum(1))


def ridge_fold_preds(X, XF, Y, fold, alphas=ALPHAS):
    """E4b fit with training-fold standardisation (stage13_e4b_trainstd): alpha from fold 0 held-out MSE, then per fold."""
    best = None; errs_out = None; PT = np.zeros_like(Y); PF = np.zeros_like(Y)
    for k in range(5):
        tr, te = fold != k, np.where(fold == k)[0]
        if not len(te): continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        A = (X[tr] - mu) / sd; ym = Y[tr].mean(0); G = A.T @ A; Bm = A.T @ (Y[tr] - ym)
        if best is None:
            errs = [((((X[te] - mu) / sd) @ np.linalg.solve(G + a_ * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm) + ym - Y[te]) ** 2).mean() for a_ in alphas]
            best = alphas[int(np.argmin(errs))]; errs_out = [float(e) for e in errs]
        Wp = np.linalg.solve(G + best * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm)
        PT[te] = (X[te] - mu) / sd @ Wp + ym; PF[te] = (XF[te] - mu) / sd @ Wp + ym
    return PT, PF, best, errs_out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=','.join(ALL_RUNS)); ap.add_argument('--layers', default=None)
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    root = R13 / 'alltok_tiny' if a.tiny else R13
    OUT = root / 'summary_alltok/probe'; OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    # ---------------- inputs (all 9,108 papers; folds on the full id set -> archived folds)
    Xt, Ct, pid, gold, players = loadc('true'); Xf, _, pidf, _, _ = loadc('false_0')
    order = {p: i for i, p in enumerate(pidf)}; Xf = Xf[[order[p] for p in pid]]
    fold_full = c13.group_folds(pid, k=5)[0]
    F = dict(zip(pid, fold_full)); pidx = {p: i for i, p in enumerate(pid)}
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); DONOR = ft[ft.k == 0].set_index('paper_id').donor_paper_id.to_dict()
    layers = [int(l) for l in players] if not a.layers else [int(x) for x in a.layers.split(',')]
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
    # recorded L63 states
    rf = sorted((root / 'raw/allTok_L63').glob('shard_*.npz'))
    need_alltok = any(r != 'e4b_parity' for r in a.runs.split(','))
    if need_alltok:
        if not a.tiny and len(rf) != 72: raise SystemExit(f'allTok_L63 incomplete: {len(rf)}/72 shards')
        zs = [np.load(f) for f in rf]; rid = np.concatenate([z['row_id'] for z in zs]); RES = np.concatenate([z['resid'] for z in zs])
        rpos = pd.Series(np.arange(len(rid)), index=rid); log('allTok rows', len(rid), RES.shape)
        toks = toks[toks.row_id.isin(rid)]
    # vocabularies
    pv = np.load(R11 / 'raw/probe_vocab/shard_000.npz')
    V_e4b = Vocab(pv['token_id'], pv['lm_head_rows'], pv['norm_weight'], pv['eps'])
    if a.tiny:
        ids = np.array(sorted(toks.token_id.unique())); rng = np.random.default_rng(0); d = RES.shape[1]
        V_all = Vocab(ids, rng.standard_normal((len(ids), d)).astype(np.float16), np.ones(d, np.float32), 1e-6)
    else:
        vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); V_all = Vocab(vr['token_id'], vr['lm_head_rows'], vr['norm_weight'], vr['eps'])
    log('vocab sizes: e4b', len(V_e4b.vid), 'all', len(V_all.vid))

    for run in a.runs.split(','):
        # ---------------- per-run target, gold, vocab
        if run == 'e4b_parity':
            P = np.arange(len(pid)); Y = Ct[:, -1].astype(np.float32)
            g = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict()
            golds = [g.get(p, []) for p in pid]; grows = None; V = V_e4b
        else:
            t = toks[toks.token_index == 0] if run == 'first_alltok' else toks[toks.role == ROLE_RUNS[run]]
            t = t[t.paper_id.isin(pidx)].sort_values('row_id')
            grp = t.groupby('paper_id', sort=False)
            P = np.array(sorted(pidx[p] for p in grp.groups)); pp = pid[P]
            Y = np.zeros((len(P), RES.shape[1]), np.float32); golds, grows = [], []
            for n, p in enumerate(pp):
                s = t.iloc[grp.indices[p]]; Y[n] = RES[rpos.loc[s.row_id].to_numpy()].astype(np.float32).mean(0)
                golds.append(s.token_id.tolist()); grows.append(s.row_id.to_numpy())
            V = V_all
        fold = fold_full[P]; trainset = set(pid[P])
        dropped = np.array([(DONOR.get(p) in trainset) and (F[DONOR[p]] != F[p]) for p in pid[P]])
        # ceiling: the actual target state, decoded the same way (layer independent)
        lgY = V.logits(Y); ceil = np.array([np.mean(V.nlr(lgY[n], golds[n])) if golds[n] else np.nan for n in range(len(P))]); del lgY
        log(run, 'papers', len(P), 'tokens', sum(map(len, golds)), 'dropped (title reuse)', int(dropped.sum()))
        for l in layers:
            fo = OUT / f'perpaper_{run}_L{l}.parquet'
            if fo.exists(): log('exists', fo.name); continue
            li = [int(x) for x in players].index(l)
            X = Xt[P, li].astype(np.float32); XF = Xf[P, li].astype(np.float32)
            PT, PF, best, errs = ridge_fold_preds(X, XF, Y, fold)
            st, sf, tok_rows = np.full(len(P), np.nan), np.full(len(P), np.nan), []
            for k in range(5):
                te = np.where(fold == k)[0]
                if not len(te): continue
                LT, LF = V.logits(PT[te]), V.logits(PF[te])
                for j, n in enumerate(te):
                    if not golds[n]: continue
                    a1, a2 = V.nlr(LT[j], golds[n]), V.nlr(LF[j], golds[n]); st[n], sf[n] = a1.mean(), a2.mean()
                    if grows is not None: tok_rows.append(pd.DataFrame({'row_id': grows[n], 'nlr_true': a1, 'nlr_false': a2}))
            r2 = 1 - ((PT - Y) ** 2).sum() / ((Y - Y.mean(0)) ** 2).sum()
            df = pd.DataFrame({'paper_id': pid[P], 'fold': fold, 'n_tok': [len(x) for x in golds], 'true': st, 'false': sf, 'spec': st - sf,
                               'ceiling': ceil, 'dropped': dropped})
            if tok_rows: pd.concat(tok_rows).to_parquet(OUT / f'pertoken_{run}_L{l}.parquet', index=False)
            (OUT / f'fit_{run}_L{l}.json').write_text(json.dumps(dict(run=run, layer=l, alpha=best, alpha_errs_fold0=errs, n_papers=int(len(P)),
                                                                      heldout_r2_true=float(r2), n_dropped=int(dropped.sum()), tiny=a.tiny)))
            df.to_parquet(fo, index=False)
            log(run, f'L{l}', 'alpha', best, f'R2 {r2:.3f}', f'spec all {np.nanmean(df.spec):+.4f}', f'kept {np.nanmean(df.spec[~df.dropped]):+.4f}',
                f'true {np.nanmean(df["true"]):+.3f} ceiling {np.nanmean(ceil):+.3f}')


if __name__ == '__main__':
    main()
