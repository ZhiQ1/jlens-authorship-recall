"""Plot-ready tidy summary of Stage 11 E1 recovery for the group re-runs (addendum 8 / addendum 11 B), CPU only, 2026-11-12.

New file; reads stored per-paper outputs only (no GPU), and reuses the frozen analysis functions by path, unchanged:
  14_groups/rerun_analyze.py  (setup, token tables, unwritten-author paper means, Est.ratio / Est.mean)
  groups_core.Engine          (team-cluster bootstrap: ONE multinomial draw over archived author teams, 2,000 draws, seed 391)
Data: A, B, C36, D5 = Stage 11 originals (361_stage11/raw/patch); U0 (600) and R2 (204) = addendum-8 re-runs
(391_groups/raw/patch/{U0,R2}); C (511 design, = 36 + 475) and D (34 = 5 + 29) = addendum 11 B (391_groups/b2_cd/raw/patch/{C,D}).
Estimand (as Stage 11 / rerun_report.md): per name token log10(1/rank); paper mean over UNWRITTEN authors (addendum 7 rule;
papers with an inconsistent written-count rebuild dropped); R(l) = mean_papers(patched_l - false_0) / mean_papers(true - false_0).
Outputs (OUT, default 391_groups/summary_rerun_plot_20261112): curves.csv, numden.csv, recog.csv, trend.csv, parity.csv,
report.md.
Trend (POST HOC, DESCRIPTIVE - neither addendum 7 nor 8 pre-specifies a trend test for E1 recovery): within R0 papers
(A + U0 + B), per MC orders right k = 0..4, R_k = sum_i w_i num_i / sum_i w_i den_i over papers with mc_team_a = k (w = team
multiplicity in the draw, 1 at the point estimate); slope = weighted least-squares slope of the five R_k on k with weights
n_k = sum_i w_i (number of papers in cell k in that draw); recomputed in every one of the 2,000 team draws -> 95% percentile
interval and two-sided percentile p. Same for the denominator (per-k mean of true - false_0; with n_k weights this equals the
paper-level OLS slope). Sensitivities: unweighted slope of R_k; R_4 - R_0; denominator slope with citation-bin fixed effects
(addendum 7 P3 regression form, groups_core.Engine.wls).
"""
import importlib.util, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'; R11 = BASE / '361_stage11'
OUT = Path(os.environ.get('PLOT_OUT', G / 'summary_rerun_plot_20261112'))
os.environ.setdefault('RERUN_OUT', str(G))
sys.path.insert(0, str(H / '14_groups'))
WARN = []


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def wslope(k, y, w):
    """weighted LS slope of y on k (arrays [..., K]); nan cells dropped per row."""
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0); w = np.where(ok, w, 0.0); y0 = np.where(ok, y, 0.0)
    sw = w.sum(-1, keepdims=True); kb = (w * k).sum(-1, keepdims=True) / sw; yb = (w * y0).sum(-1, keepdims=True) / sw
    return ((w * (k - kb) * (y0 - yb)).sum(-1) / (w * (k - kb) ** 2).sum(-1))


def main():
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    ra = load(H / '14_groups/rerun_analyze.py', 'ra_plot20261112')
    gc = load(H / '14_groups/groups_core.py', 'gc_plot20261112')
    P, tk, au, E = ra.setup(); X = ra.Est(P, E); NB = E.cnt.shape[0]; log('setup done; teams', E.nteam, 'draws', NB)
    smp11 = pd.read_parquet(R11 / 'config/sample.parquet')
    gs11 = {g: set(smp11.paper_id[P.grp.reindex(smp11.paper_id).to_numpy() == g]) for g in 'ABCD'}
    lists = {'U0': pd.read_parquet(G / 'config/rerun_U0_600.parquet'), 'R2': pd.read_parquet(G / 'config/rerun_R2.parquet'),
             'C': pd.read_parquet(G / 'config/b2_cd_C.parquet'), 'D': pd.read_parquet(G / 'config/b2_cd_D.parquet')}
    design = {'A': gs11['A'], 'B': gs11['B'], 'C': gs11['C'] | set(lists['C'].paper_id), 'D': gs11['D'] | set(lists['D'].paper_id),
              'U0': set(lists['U0'].paper_id), 'R2': set(lists['R2'].paper_id), 'C_stage11': gs11['C'], 'D_stage11': gs11['D']}
    bases, PL = [], None
    for d in (R11 / 'raw/patch', G / 'raw/patch/U0', G / 'raw/patch/R2', G / 'b2_cd/raw/patch/C', G / 'b2_cd/raw/patch/D'):
        z = ra.load_dir(d)
        if z is None: WARN.append(f'no data in {d}'); continue
        b, L = ra.e1_tokens(z, tk, au, P); bases.append(b); PL = PL or L
        if L != PL: WARN.append(f'layer list differs in {d}: {L}')
    base = pd.concat(bases, ignore_index=True)
    dup = base.duplicated(['row_id']).sum()
    if dup: WARN.append(f'{dup} duplicated E1 token rows across sources (kept all)')
    log('tokens', len(base), 'layers', PL)
    cols = ['true', 'false'] + [f'p{l}' for l in PL]
    tabs, rows = {}, []
    for g, ids in design.items():
        pp = ra.paper_means(base[base.paper_id.isin(ids)], cols, 'unwritten'); pp['gap'] = pp['true'] - pp['false']
        for l in PL: pp[f'num{l}'] = pp[f'p{l}'] - pp['false']
        tabs[g] = pp
        for l in PL:
            x = pp.dropna(subset=[f'num{l}', 'gap'])
            r_ = X.ratio(x, f'num{l}', 'gap'); n_ = X.mean(x, f'num{l}'); d_ = X.mean(x, 'gap')
            rows.append(dict(group=g, layer=l, n_papers=len(x), R=r_[0], R_lo=r_[1], R_hi=r_[2], numerator=n_[0], num_lo=n_[1], num_hi=n_[2],
                             denominator=d_[0], den_lo=d_[1], den_hi=d_[2], descriptive_only=len(x) < 30,
                             role='reference only (upper reference, never a conclusion)' if g == 'R2' else ('Stage 11 subset (parity)' if g.endswith('_stage11') else '')))
    GV = pd.DataFrame(rows)
    GV[['group', 'layer', 'n_papers', 'R', 'R_lo', 'R_hi', 'descriptive_only', 'role']].to_csv(OUT / 'curves.csv', index=False)
    GV[['group', 'layer', 'n_papers', 'numerator', 'num_lo', 'num_hi', 'denominator', 'den_lo', 'den_hi', 'R', 'descriptive_only', 'role']].to_csv(OUT / 'numden.csv', index=False)
    log('curves/numden written')

    # ---------------- parity vs stored summaries (WARN only)
    par = []
    def cmp(label, new, old, keys, pairs):
        m = new.merge(old, on=keys, suffixes=('', '_old'))
        for a, b in pairs:
            d = float(np.nanmax(np.abs(m[a] - m[b]))) if len(m) else np.nan
            par.append(dict(check=label, column=a, cells=len(m), max_abs_diff=d, status='OK' if d < 1e-9 else 'WARN'))
    cd = pd.read_csv(G / 'b2_cd/summary/cd_group_values.csv'); cd = cd[(cd.experiment == 'E1') & (cd.who == 'unwritten')]
    cmp('cd_group_values.csv (A, B, C, D, C_stage11, D_stage11)', GV, cd.rename(columns={'estimate': 'R_o', 'lo': 'Rlo_o', 'hi': 'Rhi_o', 'n_papers': 'n_o'}),
        ['group', 'layer'], [('R', 'R_o'), ('R_lo', 'Rlo_o'), ('R_hi', 'Rhi_o'), ('numerator', 'numerator_old'), ('num_lo', 'num_lo_old'), ('num_hi', 'num_hi_old'),
                             ('denominator', 'denominator_old'), ('den_lo', 'den_lo_old'), ('den_hi', 'den_hi_old'), ('n_papers', 'n_o')])
    rg = pd.read_csv(G / 'summary_rerun/rerun_group_values.csv'); rg = rg[(rg.experiment == 'E1') & (rg.who == 'unwritten') & (rg['item'] == 'recovery') & rg.group.isin(['U0', 'R2'])]
    cmp('rerun_group_values.csv (U0, R2)', GV, rg.rename(columns={'estimate': 'R_o', 'lo': 'Rlo_o', 'hi': 'Rhi_o', 'n_papers': 'n_o'}), ['group', 'layer'],
        [('R', 'R_o'), ('R_lo', 'Rlo_o'), ('R_hi', 'Rhi_o'), ('n_papers', 'n_o')])
    nd = pd.read_csv(G / 'summary_rerun/e1_e2_num_den.csv'); nd = nd[(nd.experiment == 'E1') & (nd.who == 'unwritten') & nd.group.isin(['U0', 'R2'])]
    cmp('e1_e2_num_den.csv (U0, R2)', GV, nd, ['group', 'layer'], [('numerator', 'numerator_old'), ('num_lo', 'num_lo_old'), ('num_hi', 'num_hi_old'),
                                                                  ('denominator', 'denominator_old'), ('den_lo', 'den_lo_old'), ('den_hi', 'den_hi_old')])

    # ---------------- continuous recognition within R0 (A + U0 + B)
    R0 = pd.concat([tabs[g].assign(grp=g) for g in ('A', 'U0', 'B')])
    R0['k'] = pd.to_numeric(P.mc_team_a.reindex(R0.index), errors='coerce')
    if R0.index.duplicated().any(): WARN.append(f'{R0.index.duplicated().sum()} R0 papers in more than one group')
    nok = R0.k.isna().sum()
    if nok: WARN.append(f'{nok} R0 papers without mc_team_a (dropped from recog)')
    R0 = R0[R0.k.notna()]
    KS = [0, 1, 2, 3, 4]; LR = [24, 32, 40, 48, 52]
    rec, bootR, bootD, nB = [], {l: np.full((NB, 5), np.nan) for l in LR}, np.full((NB, 5), np.nan), np.full((NB, 5), np.nan)
    ptR, ptD, nK = {l: np.full(5, np.nan) for l in LR}, np.full(5, np.nan), np.zeros(5)
    for j, k in enumerate(KS):
        s = R0[R0.k == k].dropna(subset=['gap'] + [f'num{l}' for l in LR])
        if len(s) != (R0.k == k).sum(): WARN.append(f'k={k}: {(R0.k == k).sum() - len(s)} papers dropped for missing layer values')
        W = E.W(s.index.to_numpy()); nB[:, j] = W.sum(1); nK[j] = len(s)
        d_ = X.mean(s, 'gap'); bootD[:, j] = d_[4]; ptD[j] = d_[0]
        r = dict(k=k, n_papers=len(s), n_A=int((s.grp == 'A').sum()), n_U0=int((s.grp == 'U0').sum()), n_B=int((s.grp == 'B').sum()),
                 denominator=d_[0], den_lo=d_[1], den_hi=d_[2])
        for l in LR:
            e_ = X.ratio(s, f'num{l}', 'gap'); bootR[l][:, j] = e_[4]; ptR[l][j] = e_[0]
            if l in (48, 52): r |= {f'R_L{l}': e_[0], f'R_L{l}_lo': e_[1], f'R_L{l}_hi': e_[2]}
            else: r |= {f'R_L{l}': e_[0]}
        r['descriptive_only'] = len(s) < 30
        rec.append(r)
    RC = pd.DataFrame(rec); RC.to_csv(OUT / 'recog.csv', index=False); log('recog written')
    # parity vs rerun_curves_R0.csv and the slide
    cv = pd.read_csv(G / 'summary_rerun/rerun_curves_R0.csv'); cv = cv[(cv.experiment == 'E1') & (cv.by == 'mc_team_a')]; cv['k'] = cv.level.astype(float).astype(int)
    for l in (48, 52):
        c = cv[cv.layer == l].set_index('k')
        for a, b in ((f'R_L{l}', 'estimate'), (f'R_L{l}_lo', 'lo'), (f'R_L{l}_hi', 'hi')):
            d = float(np.nanmax(np.abs(RC.set_index('k')[a] - c[b]))); par.append(dict(check=f'rerun_curves_R0.csv E1 L{l}', column=a, cells=5, max_abs_diff=d, status='OK' if d < 1e-9 else 'WARN'))
    c = cv[cv.layer == 48].set_index('k')
    for a, b in (('denominator', 'gap'), ('den_lo', 'gap_lo'), ('den_hi', 'gap_hi'), ('n_papers', 'n_papers')):
        d = float(np.nanmax(np.abs(RC.set_index('k')[a] - c[b]))); par.append(dict(check='rerun_curves_R0.csv E1 denominator / n', column=a, cells=5, max_abs_diff=d, status='OK' if d < 1e-9 else 'WARN'))
    slide = {'denominator k=0': (ptD[0], 0.185), 'denominator k=4': (ptD[4], 0.407), 'R(L48) k=0': (ptR[48][0], 0.90), 'R(L48) k=4': (ptR[48][4], 0.81),
             'n k=0': (nK[0], 241), 'n k=4': (nK[4], 557)}
    for lab, (v, s) in slide.items():
        tol = 0 if lab.startswith('n') else (0.0005 if lab.startswith('den') else 0.005)
        ok = abs(round(v, 3 if lab.startswith('den') else 2) - s) <= 1e-9 if not lab.startswith('n') else v == s
        par.append(dict(check='slide numbers (rounded as on slide)', column=lab, cells=1, max_abs_diff=abs(v - s), status='OK' if ok else 'WARN', value=v, slide=s))
    PAR = pd.DataFrame(par); PAR.to_csv(OUT / 'parity.csv', index=False)
    for r in PAR[PAR.status == 'WARN'].itertuples(): WARN.append(f'parity WARN: {r.check} {r.column} max|diff| {r.max_abs_diff:.3g}')

    # ---------------- trend (post hoc, descriptive)
    kk = np.array(KS, float); tr = []
    def add(quantity, definition, est, boot):
        lo, hi = E.ci(boot); tr.append(dict(quantity=quantity, definition=definition, estimate=est, lo=lo, hi=hi, p_two_sided=E.pval(boot),
                                            ci_includes_0=bool(lo <= 0 <= hi), n_papers=int(nK.sum()), n_per_k='/'.join(str(int(x)) for x in nK),
                                            status='post hoc, descriptive (no trend test for E1 pre-specified in addendum 7 / 8)'))
    for l in LR:
        add(f'slope R(L{l}) per MC order right', 'WLS slope of R_k on k, weights n_k, recomputed per team draw', float(wslope(kk, ptR[l], nK)), wslope(kk, bootR[l], nB))
    add('slope denominator (true - false_0) per MC order right', 'WLS slope of per-k mean on k, weights n_k (= paper-level OLS), per team draw', float(wslope(kk, ptD, nK)), wslope(kk, bootD, nB))
    for l in (48, 52):
        add(f'slope R(L{l}) unweighted (sensitivity)', 'OLS slope of the five R_k on k, equal weights', float(wslope(kk, ptR[l], np.ones(5))), wslope(kk, bootR[l], np.ones((NB, 5))))
        add(f'R(L{l}) k=4 minus k=0 (sensitivity)', 'R_4 - R_0, paired team draw', float(ptR[l][4] - ptR[l][0]), bootR[l][:, 4] - bootR[l][:, 0])
    add('denominator k=4 minus k=0 (sensitivity)', 'den_4 - den_0, paired team draw', float(ptD[4] - ptD[0]), bootD[:, 4] - bootD[:, 0])
    # addendum 7 P3 regression form (paper-level, citation-bin FE) for the denominator (a paper-level quantity)
    Pi = P.reindex(R0.index).copy(); Pi['k'] = R0.k.to_numpy(float)
    Xd, names = gc.design(Pi, ['k'], False); est, boot, n = E.wls(R0.index.to_numpy(), R0.gap.to_numpy(float), Xd, names)
    add('slope denominator, paper-level WLS with citation-bin FE (sensitivity; addendum 7 P3 form)', 'gap ~ k + citation-bin FE, team-draw weights', est, boot)
    TR = pd.DataFrame(tr); TR.to_csv(OUT / 'trend.csv', index=False); log('trend written')
    report(GV, RC, TR, PAR, PL, NB)
    log(f'DONE in {time.time() - t0:.0f}s; WARN={WARN}')


def f3(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def report(GV, RC, TR, PAR, PL, NB=2000):
    L = ['# E1 recovery by group and by MC orders right: plot-ready summary (2026-11-12)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `~/jlens_work/14_groups/rerun_plot_summary_20261112.py` (CPU; stored per-paper outputs; frozen '
         '`rerun_analyze.py` / `groups_core.py` functions loaded unchanged). E1 = Stage 11 title patching true -> false_0; '
         'R(l) = mean(patched_l - false_0) / mean(true - false_0) over papers, unwritten authors (addendum 7). 95% team-cluster bootstrap '
         f'({NB:,} draws, seed 391, archived author teams, one shared draw). n < 30 papers: descriptive only. R2 = upper reference only.', '',
         '## Pre-specification', '',
         '- Addendum 8 (`config/prereg_addendum8_groups.json` line 24): "same estimands as Stage 11/12 ... with team-cluster CIs; R2 is a reference (addendum 7); '
         'R0-uncertain is compared with A and B descriptively and through the continuous-recognition curves". No test, trend or decision rule for E1.',
         '- Addendum 7 line 18 defines a trend test (P3: slope on mc_team_a within R0, regression with citation-bin FE, Holm) only for the primary measure '
         '(Stage 10 output title-specific signal, line 14). Line 23 lists "Stage 11 E1/E2 ... split by A/B/C/D" and "signal curves against mc_team_a" as exploratory, '
         'no multiplicity correction.',
         '- Therefore every slope below is **post hoc, descriptive**.', '',
         '## Parity', '']
    bad = PAR[PAR.status == 'WARN']
    L.append(f'{len(PAR)} checks vs stored summaries (cd_group_values.csv, rerun_group_values.csv, e1_e2_num_den.csv, rerun_curves_R0.csv) and the slide numbers: '
             + ('all OK.' if not len(bad) else f'{len(bad)} WARN (see parity.csv).'))
    L.append('Max |diff| vs stored CSVs: ' + f'{PAR[~PAR.check.str.startswith("slide")].max_abs_diff.max():.1e}. Slide: ' +
             ', '.join(f'{r.column} {r.value:.4g} ({r.status})' for r in PAR[PAR.check.str.startswith('slide')].itertuples()))
    if WARN: L += ['', 'WARN: ' + '; '.join(WARN)]
    L += ['', '## Per MC orders right (R0 = A + U0 + B)', '', '| k | n (A / U0 / B) | denominator [CI] | R(L48) [CI] | R(L52) [CI] |', '|---|---|---|---|---|']
    for r in RC.itertuples():
        L.append(f'| {r.k} | {r.n_papers} ({r.n_A} / {r.n_U0} / {r.n_B}) | {f3(r.denominator, r.den_lo, r.den_hi)} | {f3(r.R_L48, r.R_L48_lo, r.R_L48_hi)} | {f3(r.R_L52, r.R_L52_lo, r.R_L52_hi)} |')
    L += ['', 'Note: k is fully nested in group here: k = 0, 1 are all B, k = 2, 3 all U0, k = 4 all A (by the strong / uncertain / fail '
          'definition from MC orders). The "curve" is therefore also a B -> U0 -> A comparison, and the three groups were sampled at different rates '
          '(A 557 of 4,110; U0 600 of 2,002; B 588 of 2,186) and U0 came from a separate GPU run (same driver). Not a within-group dose-response.', '',
          '## Trend (post hoc, descriptive)', '',
          'Definition: R_k = ratio of paper means within cell k; slope = weighted least-squares slope of the five R_k on k with weights n_k (cell paper count '
          'in that draw); recomputed in every team draw. Denominator slope with n_k weights = paper-level OLS slope.', '',
          '| quantity | estimate [95% CI] | p | CI includes 0 |', '|---|---|---|---|']
    for r in TR.itertuples():
        L.append(f'| {r.quantity} | {f3(r.estimate, r.lo, r.hi)} | {r.p_two_sided:.4f} | {"yes" if r.ci_includes_0 else "no"} |')
    L += ['', '## Group curves at selected layers (unwritten authors)', '', '| group | n | L40 R | L48 R [CI] | L52 R [CI] | denominator [CI] |', '|---|---|---|---|---|---|']
    for g in ['A', 'B', 'U0', 'C', 'D', 'R2']:
        s = GV[GV.group == g].set_index('layer')
        if 48 not in s.index: continue
        a = s.loc[48]; b = s.loc[52]; c = s.loc[40]
        L.append(f'| {g}{" (reference)" if g == "R2" else ""} | {int(a.n_papers)}{" (n<30)" if a.descriptive_only else ""} | {c.R:+.3f} | {f3(a.R, a.R_lo, a.R_hi)} | {f3(b.R, b.R_lo, b.R_hi)} | {f3(a.denominator, a.den_lo, a.den_hi)} |')
    L += ['', '## Files', '', '- `curves.csv`: group x layer -> R, R_lo, R_hi, n_papers (groups A, B, C, D, U0, R2, plus C_stage11 / D_stage11 parity subsets)',
          '- `numden.csv`: group x layer -> numerator, denominator with CIs (and R)', '- `recog.csv`: k = 0..4 -> n (and group split), denominator [CI], R(L48), R(L52) [CI], point R at L24/32/40',
          '- `trend.csv`: slopes and sensitivities with CI, p, CI-includes-0', '- `parity.csv`: reproduction checks']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('wrote', OUT / 'report.md')


if __name__ == '__main__':
    main()
