"""2-11b POST-HOC robustness (事后，探索性; user question 2026-11-12). Does NOT change the addendum-15 verdict. CPU only.

New file; stage13_b2_gennames_b_analyze.py is loaded by path and not edited. Same name table, same M/H filter, same vectors,
same folds, same probe (V1.fit_oof), same within-paper AUROC and team-cluster bootstrap (V2.within_auroc, 2,000 draws).
Primary position (ii) name_mean only, all 7 layers.
  1. Shuffled-label control with a team-cluster CI (the report gives a point value only): within-paper AUROC of the shuffled-
     label probe against the shuffled labels (as the report), on the papers qualifying under the shuffled labels.
  2. Fame baseline (author fame in the dataset), symmetric for M and H: for each written name, the cohort papers OTHER than the
     current paper that have an author with (a) the same normalised full name (v3 words3; 2-word names also reversed) and
     (b) the same surname + first initial (either order); features log1p(n papers) and log1p(sum of citations) for (a) and (b).
     Fitted with the same V1.fit_oof. Reported: fame baseline alone, probe - fame, and probe vs a combined baseline
     (position + string + fame in one logistic model).
  (The other requested baseline, the model's own token log-probability / entropy, is NOT computable from disk: only L16-L56
   residuals at three positions and the final-layer argmax were stored, no logits; it needs a GPU replay.)
Outputs: b2_gennames_b/summary/robust_posthoc.csv, reports/b2_gennames_b_robust_posthoc.md
"""
import importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); ROOT = R13 / 'b2_gennames_b'
_sp = importlib.util.spec_from_file_location('gnb_an', H / '13_stage13/stage13_b2_gennames_b_analyze.py'); AN = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AN)
V1, V2, B, V3 = AN.V1, AN.V2, AN.B, AN.V3B.V3


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def fame_features(N, P):
    words = V3.words3
    full, rule = {}, {}
    cit = dict(zip(P.paper_id, P.citations.fillna(0).astype(float)))
    for pid, al in zip(P.paper_id, P.authors):
        for a in str(al).split('; '):
            w = words(a)
            if not w: continue
            full.setdefault(' '.join(w), set()).add(pid)
            if len(w) > 1: rule.setdefault((w[-1], w[0][0]), set()).add(pid)
    F = np.zeros((len(N), 4))
    for i, (nm, pid) in enumerate(zip(N.name, N.paper_id)):
        g = words(nm)
        sa = set(full.get(' '.join(g), set()))
        if len(g) == 2: sa |= full.get(' '.join(g[::-1]), set())
        sb = set()
        if len(g) >= 2:
            for k in ((g[-1], g[0][0]), (g[0], g[1][0])): sb |= rule.get(k, set())
        sa.discard(pid); sb.discard(pid)
        F[i] = [len(sa), sum(cit.get(p, 0) for p in sa), len(sb), sum(cit.get(p, 0) for p in sb)]
    return np.log1p(F)


def main():
    import pandas as pd
    shards = list(range(AN.N_SHARDS))
    NA = pd.concat([pd.read_parquet(ROOT / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    zs = [np.load(ROOT / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    N = N.reset_index(drop=True); ix = np.array([kidx[k_] for k_ in N.key])
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy()
    P, _ = B.load_papers()
    XP = N[['item_index', 'item_rel']].to_numpy(float); XS = np.stack([N.name_len_chars.to_numpy(float), np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1)
    XF = fame_features(N, P)
    pp_, _, _ = V1.fit_oof(XP, y, fold); ps_, _, _ = V1.fit_oof(XS, y, fold); pf_, Cf, _ = V1.fit_oof(XF, y, fold)
    pc_, _, _ = V1.fit_oof(np.concatenate([XP, XS, XF], 1), y, fold)
    desc = dict(M_fame_exact_any=float((XF[y == 1, 0] > 0).mean()), H_fame_exact_any=float((XF[y == 0, 0] > 0).mean()),
                M_fame_rule_any=float((XF[y == 1, 2] > 0).mean()), H_fame_rule_any=float((XF[y == 0, 2] > 0).mean()))
    log('fame share > 0', desc)
    ref = pd.read_csv(ROOT / 'summary/probe_within.csv'); ref = ref[ref.position == 'name_mean'].set_index('layer')
    rows = []; ci = lambda v: tuple(np.percentile(v, [2.5, 97.5]))
    for l in AN.LAYERS:
        X = np.concatenate([z[f'name_mean@{l}'] for z in zs])[ix].astype(np.float32)
        pr, C, _ = V1.fit_oof(X, y, fold); psh, _, ysh = V1.fit_oof(X, y, fold, seed_shuffle=1212)
        st = [V2.pair_stats(paper[tgt], y[tgt], sc[tgt]) for sc in (pr, pp_, ps_, pf_, pc_)]
        common = set.intersection(*[set(s) for s in st]); st = [{p: s[p] for p in common} for s in st]
        est, bt, npap, npair = V2.within_auroc(st, PT)
        sh = V2.pair_stats(paper[tgt], ysh[tgt], psh[tgt]); e_sh, b_sh, n_sh, _ = V2.within_auroc([sh], PT)
        r = dict(layer=l, C=C, probe=est[0], probe_lo=ci(bt[:, 0])[0], probe_hi=ci(bt[:, 0])[1],
                 check_vs_report=abs(est[0] - ref.loc[l, 'auroc_within']),
                 fame=est[3], fame_lo=ci(bt[:, 3])[0], fame_hi=ci(bt[:, 3])[1],
                 probe_minus_fame=est[0] - est[3], pmf_lo=ci(bt[:, 0] - bt[:, 3])[0], pmf_hi=ci(bt[:, 0] - bt[:, 3])[1],
                 combined=est[4], comb_lo=ci(bt[:, 4])[0], comb_hi=ci(bt[:, 4])[1],
                 probe_minus_combined=est[0] - est[4], pmc_lo=ci(bt[:, 0] - bt[:, 4])[0], pmc_hi=ci(bt[:, 0] - bt[:, 4])[1],
                 shuffled=e_sh[0], sh_lo=ci(b_sh[:, 0])[0], sh_hi=ci(b_sh[:, 0])[1], shuffled_report=ref.loc[l, 'shuffled_within'],
                 n_papers=npap, n_pairs=npair, n_papers_shuffled=n_sh)
        rows.append(r); log(f'L{l}', {k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})
    T = pd.DataFrame(rows); T.to_csv(ROOT / 'summary/robust_posthoc.csv', index=False)
    f = lambda e, lo, hi, s='': f'{e:{s}.3f} [{lo:{s}.3f}, {hi:{s}.3f}]'
    L = ['# 2-11b post-hoc robustness (事后，探索性) — primary position (ii) name_mean', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2_gennames_b_robust.py` (CPU). Does not change the addendum-15 verdict. '
         'Same names, vectors, folds, probe and team-cluster bootstrap (2,000 draws) as the locked analysis.', '',
         f'Probe reproduction vs summary/probe_within.csv: max |diff| {T.check_vs_report.max():.1e}.', '',
         'Fame baseline = log1p(number of OTHER cohort papers with an author of the same full name / same surname + initial) and log1p(their summed citations); '
         f'C = {Cf}. Share of names with >= 1 other paper (exact / rule): M {desc["M_fame_exact_any"]:.3f} / {desc["M_fame_rule_any"]:.3f}, H {desc["H_fame_exact_any"]:.3f} / {desc["H_fame_rule_any"]:.3f}. '
         'Combined = position + string + fame features in one logistic model.', '',
         '| layer | probe | fame baseline | probe - fame | combined baseline | probe - combined | shuffled (CI) | papers / pairs |', '|---|---|---|---|---|---|---|---|']
    for r in T.itertuples():
        L.append(f'| L{r.layer} | {f(r.probe, r.probe_lo, r.probe_hi)} | {f(r.fame, r.fame_lo, r.fame_hi)} | {f(r.probe_minus_fame, r.pmf_lo, r.pmf_hi, "+")} | '
                 f'{f(r.combined, r.comb_lo, r.comb_hi)} | {f(r.probe_minus_combined, r.pmc_lo, r.pmc_hi, "+")} | {f(r.shuffled, r.sh_lo, r.sh_hi)} ({r.n_papers_shuffled} papers) | {r.n_papers} / {r.n_pairs} |')
    L += ['', 'Shuffled: labels permuted within training folds (rng 1212, as the locked analysis); AUROC against the shuffled labels on the papers that qualify under them.',
          'Generation log-probability / entropy baseline: not computable from stored data (no logits or final-layer states saved); needs a GPU replay.', '']
    (R13 / 'reports/b2_gennames_b_robust_posthoc.md').write_text('\n'.join(L) + '\n'); log('wrote report')


if __name__ == '__main__':
    main()
