"""Batch 3 item 3-3 (addendum 14): hard check + the 7.1B estimands (POST HOC relative to the original Stage 7 analysis), CPU.

1. HARD CHECK (plan): the 1,166 contexts already computed by 7.1B are reproduced, rank match >= 99% over all their scores
   (targets x 15 readouts). Re-run on the saved npz. Exit 3 on FAIL unless HC33_POLICY=warn (then the report carries a banner).
   Beside it (INFO): share exact-or-within-4-bf16-units, and max |d logprob|, per readout.
2. COVERAGE: every one of the 15,519 frozen 7.1B contexts' targets is a scored row (checked per paper in the GPU job; re-checked).
3. ESTIMANDS (07_1_stage7_1/351_stage7_1B_terminal.py plan.json: 'Same gold prefix and next token: true title minus mean of
   20 wrong titles'; aggregation and pairing as 07_1_stage7_1/351_stage7.py): per author token, effect = score(true) - mean over
   the 20 wrong titles; token -> author (first token / continuation tokens / all) -> paper (equal author weights; continuation
   over authors with >= 2 tokens); metrics rr = 1/rank (JMRR, the Stage 7.1 metric), nlr = log10(1/rank), logprob. Groups A/B/C/D
   (Pilot50) means with a paper bootstrap; matched A - B over the 20 Stage 5 pairs with the Stage 7.1 pair bootstrap (10,000
   draws, seed 35171 + layer + len(metric)); 7-layer integrated (equal layer weights) for jlens and vanilla.
Usage: stage13_b3_71b_analyze.py [--tiny]
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b3_cols.py', 'b3_cols')
GP = load(H / '13_stage13/stage13_b3_71b_gpu.py', 'b3_71b_gpu'); log = GP.log
SEED71 = 35171; NBOOT = 10000
PAIRS = K.BASE / '351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv'


def ci71(vals, seed, n=NBOOT):
    """verbatim logic of 351_stage7.ci: resample matched pairs."""
    if not len(vals): return [None, None]
    arr = np.asarray(vals, float); rng = np.random.default_rng(seed); means = np.empty(n)
    for k in range(0, n, 500):
        c = min(500, n - k); means[k:k + c] = arr[rng.integers(0, len(arr), size=(c, len(arr)))].mean(axis=1)
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def main():
    K.check_plan(); ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    R = GP.roots(a.tiny); plan, tasks, authors = GP.frozen_71b(); order = GP.paper_order(tasks)
    have = [p for p in order if GP.unit_path(R, p).exists()]
    if len(have) < len(order) and not a.tiny: log(f'INCOMPLETE: {len(order) - len(have)} papers missing'); sys.exit(2)
    # ---- 1 hard check (re-run on saved files)
    g = GP.gate_check(a.tiny); hard_fail = g['plan_status'] == 'FAIL'
    # ---- 2 coverage
    cov_missing = 0
    for pid in have:
        z = np.load(GP.unit_path(R, pid)); s = set(zip(z['shuffle_index'].tolist(), z['author_index'].tolist(), z['token_index'].tolist(), z['token_id'].tolist()))
        for t in tasks:
            if t['paper_id'] != pid: continue
            for q in t['targets']: cov_missing += (t['shuffle_index'], q['author_index'], q['token_index'], q['token_id']) not in s
    # ---- 3 estimands
    rows = []
    for pid in have:
        z = np.load(GP.unit_path(R, pid)); meta = json.loads(str(z['meta']))
        df = pd.DataFrame(dict(sh=z['shuffle_index'], ai=z['author_index'], j=z['token_index']))
        for pi, (m7, l7) in enumerate(K.R71_READOUTS):
            d = df.assign(rr=1.0 / z['rank'][pi], nlr=-np.log10(z['rank'][pi].astype(float)), lp=z['logprob'][pi].astype(float))
            tr = d[d.sh == 0].set_index(['ai', 'j'])[['rr', 'nlr', 'lp']]
            wr = d[d.sh > 0].groupby(['ai', 'j'])[['rr', 'nlr', 'lp']].mean()
            if d[d.sh > 0].groupby(['ai', 'j']).size().min() != K.K_WRONG: raise RuntimeError(f'{pid}: not 20 wrong titles per token')
            e = (tr - wr.reindex(tr.index)).reset_index(); t_ = tr.reset_index(); w_ = wr.reindex(tr.index).reset_index()
            for ai, ge in e.groupby('ai'):
                gt = t_[t_.ai == ai]; gw = w_[w_.ai == ai]; f = ge.j == 0; c = ge.j > 0
                rows.append(dict(paper_id=pid, group=meta['group'], author_index=int(ai), mode=m7, layer=l7, n_tokens=len(ge),
                                 true_first_rr=float(gt.rr[f.values].mean()), wrong_first_rr=float(gw.rr[f.values].mean()), eff_first_rr=float(ge.rr[f].mean()),
                                 true_cont_rr=float(gt.rr[c.values].mean()) if c.any() else np.nan, wrong_cont_rr=float(gw.rr[c.values].mean()) if c.any() else np.nan,
                                 eff_cont_rr=float(ge.rr[c].mean()) if c.any() else np.nan,
                                 true_all_rr=float(gt.rr.mean()), wrong_all_rr=float(gw.rr.mean()), eff_all_rr=float(ge.rr.mean()),
                                 eff_first_nlr=float(ge.nlr[f].mean()), eff_cont_nlr=float(ge.nlr[c].mean()) if c.any() else np.nan, eff_all_nlr=float(ge.nlr.mean()),
                                 eff_first_lp=float(ge.lp[f].mean()), eff_cont_lp=float(ge.lp[c].mean()) if c.any() else np.nan, eff_all_lp=float(ge.lp.mean())))
    AU = pd.DataFrame(rows)[K.R71_AUTHOR]; K.write_csv(AU, R['summ'] / 'author_effects.csv', K.R71_AUTHOR)
    effc = [c for c in K.R71_PAPER if c.startswith('eff_')] + ['true_all_rr', 'wrong_all_rr']
    PA = AU.groupby(['paper_id', 'group', 'mode', 'layer'], sort=False).agg(n_authors=('author_index', 'size'), n_cont_authors=('eff_cont_rr', lambda v: int(v.notna().sum())),
                                                                       **{c: (c, 'mean') for c in effc}).reset_index()[K.R71_PAPER]
    K.write_csv(PA, R['summ'] / 'paper_effects.csv', K.R71_PAPER)
    METS = ['eff_first_rr', 'eff_cont_rr', 'eff_all_rr', 'eff_first_nlr', 'eff_cont_nlr', 'eff_all_nlr', 'eff_first_lp', 'eff_cont_lp', 'eff_all_lp']
    rng = np.random.default_rng(3713); gr = []
    for (m7, l7), s in PA.groupby(['mode', 'layer']):
        for mt in METS:
            for grp_, ss in list(s.groupby('group')) + [('all', s)]:
                v = ss[mt].dropna().to_numpy()
                lo, hi = (np.percentile(v[rng.integers(0, len(v), (2000, len(v)))].mean(1), [2.5, 97.5]) if len(v) > 1 else (np.nan, np.nan))
                gr.append(dict(mode=m7, layer=l7, metric=mt, group=grp_, n_papers=len(v), mean=float(v.mean()) if len(v) else np.nan, lo=lo, hi=hi))
    GR = pd.DataFrame(gr)[K.R71_GROUP]; K.write_csv(GR, R['summ'] / 'group_effects.csv', K.R71_GROUP)
    pairs = pd.read_csv(PAIRS); lk = PA.set_index(['paper_id', 'mode', 'layer']); pr = []
    for (m7, l7) in K.R71_READOUTS + [('jlens', 'integrated_7'), ('vanilla', 'integrated_7')]:
        for mt in METS:
            dif = []
            for p in pairs.itertuples():
                try:
                    if l7 == 'integrated_7':
                        av = [lk.loc[(p.A_id, m7, l), mt] for l in K.R71_LAYERS]; bv = [lk.loc[(p.B_id, m7, l), mt] for l in K.R71_LAYERS]
                        if any(pd.isna(av)) or any(pd.isna(bv)): continue
                        dif.append(float(np.mean(av)) - float(np.mean(bv)))
                    else:
                        av, bv = lk.loc[(p.A_id, m7, l7), mt], lk.loc[(p.B_id, m7, l7), mt]
                        if pd.isna(av) or pd.isna(bv): continue
                        dif.append(float(av - bv))
                except KeyError: continue
            seed = SEED71 + (l7 if isinstance(l7, int) else len(m7)) + len(mt)
            lo, hi = ci71(dif, seed) if dif else (None, None)
            pr.append(dict(mode=m7, layer=l7, metric=mt, n_pairs=len(dif), A_minus_B_mean=float(np.mean(dif)) if dif else np.nan,
                           median_difference=float(np.median(dif)) if dif else np.nan, n_positive=int(sum(x > 0 for x in dif)), lo=lo, hi=hi))
    PR = pd.DataFrame(pr)[K.R71_PAIRS]; K.write_csv(PR, R['summ'] / 'pair_effects.csv', K.R71_PAIRS)
    report(a, R, g, cov_missing, have, order, GR, PR, hard_fail)
    if hard_fail and GP.POLICY == 'plan': log('HARD CHECK FAILED -> exit 3'); sys.exit(3)
    log('DONE', R['report'])


def report(a, R, g, cov_missing, have, order, GR, PR, hard_fail):
    try:
        f = lambda v, lo, hi: '' if pd.isna(v) else (f'{v:+.4f} [{lo:+.4f}, {hi:+.4f}]' if lo is not None and not pd.isna(lo) else f'{v:+.4f}')
        L = ['# Batch 3 item 3-3: Stage 7.1B completed on the Stage 10 fast path (addendum 14)' + (' — TINY TEST' if a.tiny else ''), '',
             f'Generated {time.ctime()}. **POST HOC** relative to the original Stage 7 analysis. Plan sha256 {K.PLAN_SHA[:12]}…. '
             f'{len(have)}/{len(order)} Pilot50 papers, 21 title conditions (true + 20 wrong), all authors, all name tokens; readouts final L63, '
             'public J-lens and logit (7.1B jlens / vanilla) at L16, 24, 32, 40, 48, 56, 62.', '']
        if hard_fail: L += [f"**HARD CHECK FAILED under the plan rule (policy {GP.POLICY}). Use the numbers only if the user accepts the deviation.**", '']
        L += ['## 1. Hard check: the 1,166 old 7.1B contexts', '', '| check | value | threshold | status | note |', '|---|---|---|---|---|']
        L += [f"| {c['check']} | {c['value']:.6f} | {c['threshold']} | {c['status']} | {c['note']} |" for c in g['checks']]
        L += ['', '| readout | layer | scores | exact | exact or ≤ 4 bf16 | max ulps | max abs Δlogprob |', '|---|---|---|---|---|---|---|']
        L += [f"| {x['mode']} | {x['layer']} | {x['n_scores']} | {x['share_exact']:.4f} | {x['share_exact_or_within']:.4f} | {x['max_ulps']:.2f} | {x['max_abs_dlogprob']:.4f} |" for x in g['per_readout']]
        L += ['', f'Coverage: {cov_missing} frozen 7.1B targets without a scored row (must be 0).', '',
              '## 2. Matched A − B (20 Stage 5 pairs), title effect = true − mean of 20 wrong titles, JMRR (1/rank)', '',
              '| readout | layer | first token | continuation | all tokens |', '|---|---|---|---|---|']
        for (m7, l7), s in PR.groupby(['mode', 'layer'], sort=False):
            c = {mt: s[s.metric == mt].iloc[0] for mt in ['eff_first_rr', 'eff_cont_rr', 'eff_all_rr']}
            L.append(f'| {m7} | {l7} | ' + ' | '.join(f(c[mt].A_minus_B_mean, c[mt].lo, c[mt].hi) for mt in c) + ' |')
        L += ['', '## 3. Group means of the title effect (all tokens, JMRR; paper bootstrap)', '', '| readout | layer | A | B | C | D |', '|---|---|---|---|---|---|']
        s = GR[GR.metric == 'eff_all_rr']
        for (m7, l7), ss in s.groupby(['mode', 'layer'], sort=False):
            c = {x.group: f(x.mean, x.lo, x.hi) for x in ss.itertuples()}
            L.append(f'| {m7} | {l7} | ' + ' | '.join(c.get(k, '') for k in 'ABCD') + ' |')
        L += ['', 'log10(1/rank) and logprob versions: `group_effects.csv`, `pair_effects.csv`; per author / paper: `author_effects.csv`, `paper_effects.csv` '
              f'in `{R["summ"]}`.', '', '## 4. Notes', '',
              '- Fast path = one forward per (paper, condition, author) over prompt + name[:-1]; the old 7.1B ran one per-prefix forward per context with layers '
              '29-63 on the CPU. Rank differences between the two are bf16 rounding (Stage 10 parity: about 1-1.5 bf16 units).',
              '- Pair bootstrap and seeds as 351_stage7.ci (pairs resampled, 10,000 draws); group CIs: paper bootstrap 2,000 draws (seed 3713).']
        R['report'].parent.mkdir(parents=True, exist_ok=True); R['report'].write_text('\n'.join(L) + '\n'); log('report', R['report'])
    except Exception as e: log('WARNING report writing failed (CSVs saved):', repr(e))


if __name__ == '__main__':
    main()
