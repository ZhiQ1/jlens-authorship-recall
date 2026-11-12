"""2-11b POST-HOC generation-confidence analysis (事后，探索性). Does NOT change the addendum-15 verdict. CPU.
Reuses (loaded by path, not edited) the locked analysis (stage13_b2_gennames_b_analyze.py: names, M/H filter, folds, V1.fit_oof,
V2.pair_stats / within_auroc with author-team cluster bootstrap, 2,000 draws) and the robust script's fame features
(stage13_b2_gennames_b_robust.py fame_features). Confidence from conf/shard_KKK.parquet (stage13_b2_gennames_b_conf.py).
  1. Confidence alone, within-paper AUROC on target papers: (a) [lp_first, ent_pre] and (b) [lp_mean], each as an out-of-fold
     logistic score (same fit_oof as every baseline); raw scores lp_first and lp_mean (higher = more confident) for reference.
  2. Primary position (ii) name_mean, every layer: probe vs the combined baseline "confidence (a)+(b) + position + string + fame"
     (one logistic model), difference with team-cluster CI.
  3. Pre-name position (i): does confidence (a) alone separate M from H (CI of its within-paper AUROC excluding 0.5)? Probe at
     pred_first beside it.
Outputs: b2_gennames_b/summary/conf_posthoc.csv, reports/b2_gennames_b_conf_posthoc.md. Usage: [--root DIR] [--out MD] [--nb N] [--layers ..] [--allow-partial]
"""
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
_sp = importlib.util.spec_from_file_location('gnb_rob', H / '13_stage13/stage13_b2_gennames_b_robust.py'); RB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RB)
AN = RB.AN; V1, V2, B = AN.V1, AN.V2, AN.B


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(R13 / 'b2_gennames_b')); ap.add_argument('--out'); ap.add_argument('--nb', type=int, default=2000)
    ap.add_argument('--layers'); ap.add_argument('--allow-partial', action='store_true'); a = ap.parse_args()
    root = Path(a.root); layers = [int(x) for x in a.layers.split(',')] if a.layers else AN.LAYERS
    shards = [k for k in range(AN.N_SHARDS) if (root / f'conf/shard_{k:03d}.parquet').exists() and (root / f'raw/shard_{k:03d}.npz').exists()]
    if len(shards) < AN.N_SHARDS and not a.allow_partial: raise SystemExit(f'only {len(shards)}/{AN.N_SHARDS} conf shards')
    if (root / 'conf/REPLAY_STOP').exists(): raise SystemExit('REPLAY_STOP present')
    rep = [json.loads((root / f'conf/replay_{k:03d}.json').read_text()) for k in shards]
    agr = sum(r['agree'] for r in rep) / max(1, sum(r['positions'] for r in rep))
    h2n = sum(r['h2_positions'] for r in rep); agr2 = sum(r['h2_agree'] for r in rep) / h2n if h2n else float('nan')
    NA = pd.concat([pd.read_parquet(root / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    CF = pd.concat([pd.read_parquet(root / f'conf/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    zs = [np.load(root / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str); N = N.reset_index(drop=True)
    CF['key'] = CF.paper_id + '|' + CF.item_index.astype(str); cf = CF.set_index('key')
    miss = (~N.key.isin(cf.index)).sum()
    if miss: raise SystemExit(f'{miss} M/H names without confidence values')
    ix = np.array([kidx[k_] for k_ in N.key]); N = N.join(cf[['lp_first', 'ent_pre', 'lp_mean']], on='key')
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy()
    P, _ = B.load_papers()
    XP = N[['item_index', 'item_rel']].to_numpy(float); XS = np.stack([N.name_len_chars.to_numpy(float), np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1)
    XF = RB.fame_features(N, P); XA = N[['lp_first', 'ent_pre']].to_numpy(float); XB = N[['lp_mean']].to_numpy(float)
    pa_, Ca, _ = V1.fit_oof(XA, y, fold); pb_, Cb, _ = V1.fit_oof(XB, y, fold)
    pc_, Cc, _ = V1.fit_oof(np.concatenate([XA, XB, XP, XS, XF], 1), y, fold)
    raw_a, raw_b = N.lp_first.to_numpy(float), N.lp_mean.to_numpy(float)
    ci = lambda v: tuple(np.percentile(v, [2.5, 97.5]))
    desc = dict(M_lp_first=float(np.median(raw_a[y == 1])), H_lp_first=float(np.median(raw_a[y == 0])), M_lp_mean=float(np.median(raw_b[y == 1])),
                H_lp_mean=float(np.median(raw_b[y == 0])), M_ent=float(np.median(N.ent_pre[y == 1])), H_ent=float(np.median(N.ent_pre[y == 0])))
    # confidence alone (one bootstrap, shared draws)
    base = [V2.pair_stats(paper[tgt], y[tgt], s[tgt]) for s in (pa_, pb_, raw_a, raw_b, pc_)]
    common = set.intersection(*[set(s) for s in base]); est0, bt0, np0, npair0 = V2.within_auroc([{p: s[p] for p in common} for s in base], PT, nb=a.nb)
    alone = {nm: (est0[i], *ci(bt0[:, i])) for i, nm in enumerate(['conf_a_fit', 'conf_b_fit', 'lp_first_raw', 'lp_mean_raw', 'combined'])}
    log('confidence alone', alone)
    rows = []
    for pos in ('name_mean', 'pred_first'):
        for l in layers:
            X = np.concatenate([z[f'{pos}@{l}'] for z in zs])[ix].astype(np.float32); pr, C, _ = V1.fit_oof(X, y, fold)
            st = [V2.pair_stats(paper[tgt], y[tgt], s[tgt]) for s in (pr, pc_, pa_, pb_)]
            cm = set.intersection(*[set(s) for s in st]); est, bt, npap, npair = V2.within_auroc([{p: s[p] for p in cm} for s in st], PT, nb=a.nb)
            r = dict(position=pos, layer=l, C=C, probe=est[0], probe_lo=ci(bt[:, 0])[0], probe_hi=ci(bt[:, 0])[1],
                     combined=est[1], comb_lo=ci(bt[:, 1])[0], comb_hi=ci(bt[:, 1])[1],
                     probe_minus_combined=est[0] - est[1], pmc_lo=ci(bt[:, 0] - bt[:, 1])[0], pmc_hi=ci(bt[:, 0] - bt[:, 1])[1],
                     conf_a=est[2], probe_minus_conf_a=est[0] - est[2], pma_lo=ci(bt[:, 0] - bt[:, 2])[0], pma_hi=ci(bt[:, 0] - bt[:, 2])[1],
                     conf_b=est[3], n_papers=npap, n_pairs=npair)
            rows.append(r); log(pos, f'L{l}', {k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})
    T = pd.DataFrame(rows); (root / 'summary').mkdir(exist_ok=True); T.to_csv(root / 'summary/conf_posthoc.csv', index=False)
    f = lambda e, lo, hi, s='': f'{e:{s}.3f} [{lo:{s}.3f}, {hi:{s}.3f}]'
    sep = lambda t: 'yes (CI excludes 0.5)' if t[1] > 0.5 or t[2] < 0.5 else 'no (CI includes 0.5)'
    L = ['# 2-11b generation-confidence baseline (事后，探索性)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2_gennames_b_conf.py` (GPU replay) and `stage13_b2_gennames_b_conf_analyze.py` (CPU). '
         'Post-hoc, exploratory; does **not** change the addendum-15 verdict. Same names, vectors, folds, probe and team-cluster bootstrap '
         f'({a.nb} draws) as the locked analysis; fame features from the robust script. Shards {len(shards)}/{AN.N_SHARDS}.', '',
         '## Replay check', '',
         f'- teacher-forced (bf16, one forward per paper, use_cache=False) argmax == stored generated token: **{agr:.4f}** over {sum(r["positions"] for r in rep)} positions (stop rule < 0.99)',
         f'- teacher-forced argmax == stored final-layer argmax at the H2 positions: {agr2:.4f} over {h2n} positions', '',
         '## 1. Confidence alone (target papers, within-paper AUROC)', '',
         f'Medians M / H: lp_first {desc["M_lp_first"]:.3f} / {desc["H_lp_first"]:.3f}; entropy before the name {desc["M_ent"]:.3f} / {desc["H_ent"]:.3f}; '
         f'lp_mean {desc["M_lp_mean"]:.3f} / {desc["H_lp_mean"]:.3f}.', '',
         '| score | within AUROC [95% CI] |', '|---|---|',
         f'| (a) first-token log p + entropy (logistic, OOF; C {Ca}) | {f(*alone["conf_a_fit"])} |',
         f'| (b) mean log p over name tokens (logistic, OOF; C {Cb}) | {f(*alone["conf_b_fit"])} |',
         f'| lp_first raw | {f(*alone["lp_first_raw"])} |', f'| lp_mean raw | {f(*alone["lp_mean_raw"])} |',
         f'| combined baseline: (a) + (b) + position + string + fame (C {Cc}) | {f(*alone["combined"])} |', '',
         f'Papers / pairs: {np0} / {npair0}.', '',
         '## 2. Primary position (ii) name_mean: probe increment over the combined baseline', '',
         '| layer | probe | combined baseline | probe - combined | probe - (a) | papers / pairs |', '|---|---|---|---|---|---|']
    for r in T[T.position == 'name_mean'].itertuples():
        L.append(f'| L{r.layer} | {f(r.probe, r.probe_lo, r.probe_hi)} | {f(r.combined, r.comb_lo, r.comb_hi)} | {f(r.probe_minus_combined, r.pmc_lo, r.pmc_hi, "+")} | '
                 f'{f(r.probe_minus_conf_a, r.pma_lo, r.pma_hi, "+")} | {r.n_papers} / {r.n_pairs} |')
    L += ['', '## 3. Pre-name position (i): does confidence (a) alone separate true from fabricated names?', '',
          f'- (a) logistic: {f(*alone["conf_a_fit"])} -> {sep(alone["conf_a_fit"])}; raw lp_first: {f(*alone["lp_first_raw"])} -> {sep(alone["lp_first_raw"])}', '',
          '| layer | probe at pred_first | probe - (a) | probe - combined |', '|---|---|---|---|']
    for r in T[T.position == 'pred_first'].itertuples():
        L.append(f'| L{r.layer} | {f(r.probe, r.probe_lo, r.probe_hi)} | {f(r.probe_minus_conf_a, r.pma_lo, r.pma_hi, "+")} | {f(r.probe_minus_combined, r.pmc_lo, r.pmc_hi, "+")} |')
    L += ['', 'All rows: target papers with >= 1 M and >= 1 H among the papers common to all scores; P and U names excluded (as addendum 15).', '']
    out = Path(a.out) if a.out else R13 / 'reports/b2_gennames_b_conf_posthoc.md'; out.write_text('\n'.join(L) + '\n'); log('wrote', out)


if __name__ == '__main__':
    main()
