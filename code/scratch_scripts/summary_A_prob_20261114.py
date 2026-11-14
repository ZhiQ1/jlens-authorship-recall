"""Item 5a (plan_batch_20261114b.md): E1 recovery vs MC true-option probability WITHIN GROUP A only. CPU, 2026-11-14.
POST HOC, DESCRIPTIVE (no trend test for E1 pre-specified in addendum 7 / 8).

New file; logic copied from 14_groups/rerun_plot_summary_20261112.py (same data loading, same unwritten-author paper means,
same team-cluster bootstrap: groups_core.Engine, 2,000 draws, seed 391, archived author teams), frozen modules loaded unchanged.
Predictor: mc_team_p_true (351_stage10/cohort/papers.parquet), continuous mean probability of the true option.
Bins: probability deciles with FIXED cut points from the full group-A sample (557 papers); if any decile has < 30 papers,
merge to quintiles (stated in report). Within every team draw: R_k(l) = sum_i w_i num_i / sum_i w_i den_i over papers in bin k;
slope = WLS slope of R_k on the bin's (full-sample) median probability, weights n_k = sum_i w_i in that draw.
Same for R(L52) and the denominator mean(true - false_0). 95% percentile CI over the 2,000 draws.
Outputs: 391_groups/summary_A_prob_20261114/{bins.csv, slopes.csv, parity.csv, report.md}.
"""
import importlib.util, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'; R11 = BASE / '361_stage11'
OUT = Path(os.environ.get('APROB_OUT', G / 'summary_A_prob_20261114'))
os.environ.setdefault('RERUN_OUT', str(G))
sys.path.insert(0, str(H / '14_groups'))
WARN = []
LR = [24, 32, 40, 48, 52]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def wslope(k, y, w):
    """weighted LS slope of y on k (arrays [..., K]); nan cells dropped per row (copied from rerun_plot_summary_20261112.py)."""
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0); w = np.where(ok, w, 0.0); y0 = np.where(ok, y, 0.0)
    sw = w.sum(-1, keepdims=True); kb = (w * k).sum(-1, keepdims=True) / sw; yb = (w * y0).sum(-1, keepdims=True) / sw
    return ((w * (k - kb) * (y0 - yb)).sum(-1) / (w * (k - kb) ** 2).sum(-1))


def f3(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def main():
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    ra = load(H / '14_groups/rerun_analyze.py', 'ra_aprob20261114')
    P, tk, au, E = ra.setup(); X = ra.Est(P, E); NB = E.cnt.shape[0]; log('setup done; teams', E.nteam, 'draws', NB)
    smp11 = pd.read_parquet(R11 / 'config/sample.parquet')
    idsA = set(smp11.paper_id[P.grp.reindex(smp11.paper_id).to_numpy() == 'A'])
    bases, PL = [], None
    for d in (R11 / 'raw/patch', G / 'raw/patch/U0', G / 'raw/patch/R2', G / 'b2_cd/raw/patch/C', G / 'b2_cd/raw/patch/D'):
        z = ra.load_dir(d)
        if z is None: WARN.append(f'no data in {d}'); continue
        b, L = ra.e1_tokens(z, tk, au, P); b = b[b.paper_id.isin(idsA)]
        if len(b): bases.append(b); log(d, 'A token rows', len(b))
        PL = PL or L
        if L != PL: WARN.append(f'layer list differs in {d}: {L}')
    base = pd.concat(bases, ignore_index=True)
    dup = base.duplicated(['row_id']).sum()
    if dup: WARN.append(f'{dup} duplicated E1 token rows across sources (kept all, as rerun_plot_summary)')
    cols = ['true', 'false'] + [f'p{l}' for l in PL]
    pp = ra.paper_means(base, cols, 'unwritten'); pp['gap'] = pp['true'] - pp['false']
    for l in PL: pp[f'num{l}'] = pp[f'p{l}'] - pp['false']
    A = pp.dropna(subset=['gap'] + [f'num{l}' for l in LR]).copy()
    if len(A) != len(pp): WARN.append(f'{len(pp) - len(A)} A papers dropped for missing layer values')

    # ---- parity: overall A R(L48) = 0.811 [0.790, 0.832]
    par = []
    r48 = X.ratio(A, 'num48', 'gap')
    for lab, v, s in (('n_papers', len(A), 557), ('R(L48)', r48[0], 0.811), ('R(L48) lo', r48[1], 0.790), ('R(L48) hi', r48[2], 0.832)):
        ok = (v == s) if lab == 'n_papers' else abs(round(v, 3) - s) < 1e-9
        par.append(dict(check='group A overall E1 R(L48) vs rerun_plot_summary_20261112 curves.csv', item=lab, value=v, expected=s, status='OK' if ok else 'WARN'))
    try:
        cv = pd.read_csv(G / 'summary_rerun_plot_20261112/curves.csv'); c = cv[(cv.group == 'A') & (cv.layer == 48)].iloc[0]
        d = max(abs(r48[0] - c.R), abs(r48[1] - c.R_lo), abs(r48[2] - c.R_hi))
        par.append(dict(check='exact vs stored curves.csv (A, L48)', item='max|diff| R, lo, hi', value=d, expected=0.0, status='OK' if d < 1e-9 else 'WARN'))
    except Exception as e: WARN.append(f'stored curves.csv compare failed: {e}')
    PAR = pd.DataFrame(par); PAR.to_csv(OUT / 'parity.csv', index=False)
    for r in PAR[PAR.status == 'WARN'].itertuples(): WARN.append(f'parity WARN: {r.item} value {r.value:.4f} expected {r.expected}')

    # ---- predictor and fixed bins
    A['p'] = pd.to_numeric(P.mc_team_p_true.reindex(A.index), errors='coerce')
    nna = int(A.p.isna().sum())
    if nna: WARN.append(f'{nna} A papers without mc_team_p_true (dropped)')
    A = A[A.p.notna()]
    binning = 'deciles'
    for nq in (10, 5):
        cuts = np.unique(np.quantile(A.p.to_numpy(), np.linspace(0, 1, nq + 1)))
        if len(cuts) - 1 < nq: WARN.append(f'{nq}-quantile cut points not unique (ties): {len(cuts) - 1} bins')
        k = np.clip(np.searchsorted(cuts, A.p.to_numpy(), side='right') - 1, 0, len(cuts) - 2)
        cnt = np.bincount(k, minlength=len(cuts) - 1)
        if cnt.min() >= 30 or nq == 5: break
        WARN.append(f'decile sizes {cnt.tolist()} include < 30 papers -> merged to quintiles'); binning = 'quintiles (merged: a decile had < 30 papers)'
    if cnt.min() < 30: WARN.append(f'{binning}: a bin still has < 30 papers ({cnt.tolist()}); descriptive only')
    A['bin'] = k; K = len(cnt)
    log('binning', binning, 'cuts', np.round(cuts, 4).tolist(), 'n', cnt.tolist())

    xmed = np.zeros(K); nK = np.zeros(K); nB = np.full((NB, K), np.nan)
    bootR = {l: np.full((NB, K), np.nan) for l in LR}; ptR = {l: np.full(K, np.nan) for l in LR}
    bootD = np.full((NB, K), np.nan); ptD = np.full(K, np.nan); rows = []
    for j in range(K):
        s = A[A.bin == j]; xmed[j] = s.p.median(); nK[j] = len(s); nB[:, j] = E.W(s.index.to_numpy()).sum(1)
        d_ = X.mean(s, 'gap'); bootD[:, j] = d_[4]; ptD[j] = d_[0]
        r = dict(bin=j + 1, lo_cut=cuts[j], hi_cut=cuts[j + 1], n_papers=len(s), median_p_true=xmed[j], min_p=s.p.min(), max_p=s.p.max(),
                 denominator=d_[0], den_lo=d_[1], den_hi=d_[2])
        for l in LR:
            e_ = X.ratio(s, f'num{l}', 'gap'); bootR[l][:, j] = e_[4]; ptR[l][j] = e_[0]
            r |= {f'R_L{l}': e_[0], f'R_L{l}_lo': e_[1], f'R_L{l}_hi': e_[2]}
        n_ = X.mean(s, 'num48'); r |= dict(numerator_L48=n_[0], num48_lo=n_[1], num48_hi=n_[2], descriptive_only=len(s) < 30)
        rows.append(r)
    BT = pd.DataFrame(rows); BT.to_csv(OUT / 'bins.csv', index=False)

    tr = []
    def add(q, definition, est, boot):
        lo, hi = E.ci(boot)
        tr.append(dict(quantity=q, definition=definition, estimate=est, lo=lo, hi=hi, p_two_sided=E.pval(boot), ci_includes_0=bool(lo <= 0 <= hi),
                       n_papers=int(nK.sum()), binning=binning, n_per_bin='/'.join(str(int(x)) for x in nK),
                       status='post hoc, descriptive (no trend test for E1 pre-specified in addendum 7 / 8)'))
    for l in (48, 52):
        add(f'slope R(L{l}) per unit mc_team_p_true', 'WLS slope of R_k on bin median p, weights n_k, per team draw', float(wslope(xmed, ptR[l], nK)), wslope(xmed, bootR[l], nB))
    add('slope denominator (true - false_0) per unit mc_team_p_true', 'WLS slope of per-bin mean on bin median p, weights n_k, per team draw', float(wslope(xmed, ptD, nK)), wslope(xmed, bootD, nB))
    for l in (24, 32, 40):
        add(f'slope R(L{l}) per unit mc_team_p_true (extra layer)', 'as above', float(wslope(xmed, ptR[l], nK)), wslope(xmed, bootR[l], nB))
    for l in (48, 52):
        add(f'slope R(L{l}) unweighted (sensitivity)', 'OLS slope of R_k on bin median p, equal weights', float(wslope(xmed, ptR[l], np.ones(K))), wslope(xmed, bootR[l], np.ones((NB, K))))
        add(f'R(L{l}) top bin minus bottom bin (sensitivity)', 'R_K - R_1, paired team draw', float(ptR[l][-1] - ptR[l][0]), bootR[l][:, -1] - bootR[l][:, 0])
    add('denominator top bin minus bottom bin (sensitivity)', 'den_K - den_1, paired team draw', float(ptD[-1] - ptD[0]), bootD[:, -1] - bootD[:, 0])
    TR = pd.DataFrame(tr); TR.to_csv(OUT / 'slopes.csv', index=False)
    report(BT, TR, PAR, r48, binning, cuts, NB, A)
    log(f'DONE in {time.time() - t0:.0f}s; WARN={WARN}')


def report(BT, TR, PAR, r48, binning, cuts, NB, A):
    L = ['# Group A: E1 recovery vs MC true-option probability (item 5a, 2026-11-14)', '',
         '**Post hoc, descriptive.** Addendum 7 / 8 pre-specify no trend test for E1 recovery; no multiplicity correction.', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `~/jlens_work/14_groups/summary_A_prob_20261114.py` (CPU; stored per-paper outputs; logic copied from '
         '`rerun_plot_summary_20261112.py`; frozen `rerun_analyze.py` / `groups_core.py` loaded unchanged). E1 = Stage 11 title patching true -> false_0, '
         'unwritten authors, final output; R(l) = mean(patched_l - false_0) / mean(true - false_0). Predictor: `mc_team_p_true` (mean probability of the true '
         f'option over MC orders). 95% team-cluster bootstrap ({NB:,} draws, seed 391, archived author teams).', '',
         f'Binning: **{binning}** of `mc_team_p_true`, fixed cut points from the full group-A sample (n = {len(A)}); cut points '
         + ', '.join(f'{c:.4f}' for c in cuts) + '. Within each team draw: R_k per bin (ratio of weighted sums), slope = WLS slope of R_k on the bin\'s '
         'full-sample median probability with weights n_k (team-draw paper count). Note group A = MC "strong" by definition, so p_true is concentrated near the top '
         f'(range {A.p.min():.3f} to {A.p.max():.3f}); the slope is per unit probability, extrapolated far beyond the observed spread - read it with the bin table.', '',
         '## Parity (WARN only)', '']
    for r in PAR.itertuples():
        L.append(f'- {r.check}: {r.item} = {r.value:.4g} (expected {r.expected}) {r.status}')
    if WARN: L += ['', 'WARN: ' + '; '.join(WARN)]
    L += ['', '## Slopes', '', '| quantity | estimate [95% CI] | p | CI includes 0 |', '|---|---|---|---|']
    for r in TR.itertuples():
        L.append(f'| {r.quantity} | {f3(r.estimate, r.lo, r.hi)} | {r.p_two_sided:.4f} | {"yes" if r.ci_includes_0 else "no"} |')
    L += ['', '## Per bin', '', '| bin | p range | n | median p | R(L48) [CI] | R(L52) [CI] | denominator [CI] |', '|---|---|---|---|---|---|---|']
    for r in BT.itertuples():
        L.append(f'| {r.bin} | {r.min_p:.3f}-{r.max_p:.3f} | {r.n_papers}{" (n<30)" if r.descriptive_only else ""} | {r.median_p_true:.4f} | '
                 f'{f3(r.R_L48, r.R_L48_lo, r.R_L48_hi)} | {f3(r.R_L52, r.R_L52_lo, r.R_L52_hi)} | {f3(r.denominator, r.den_lo, r.den_hi)} |')
    L += ['', '## Files', '', '- `bins.csv`: per bin n, cut points, median p, R at L24/32/40/48/52 [CI], numerator L48 [CI], denominator [CI]',
          '- `slopes.csv`: slopes (L48, L52, denominator; extra layers; sensitivities) with CI, p, CI-includes-0', '- `parity.csv`']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('wrote', OUT / 'report.md')


if __name__ == '__main__':
    main()
