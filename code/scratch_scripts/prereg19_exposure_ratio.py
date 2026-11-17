"""Addendum 19 (locked 2026-11-17, config/prereg_addendum19.md sha256 f6b65072...): exposure threshold, bottleneck F.
Confirmatory analysis of already-seen data (post hoc lock). CPU only, existing outputs only.

Main: rho = c50(recall) / c50(recognition), logistic y ~ log10(1+citations) + year_c on all 9,108 papers, c50 at mean year;
      also log10 rho = log10(1+c50_recall) - log10(1+c50_recog). CI: refit both models on the same 2,000 team draws, percentile.
      Rule: CI of rho entirely above 1 -> confirmed.
Sensitivity (descriptive): recognition excluding uncertain papers.
Secondary: per-bin target - control of spec_all (final L63, log10(1/rank), all tokens, true - mean 5 false), bins with >= 30 per
      group; WLS slope on log10(1 + median citations of the bin), weights 1/var (bootstrap variance of each bin estimate, fixed at
      the point-estimate weights); slope recomputed on every draw -> percentile CI. Rule: CI > 0 grows; includes 0 flat; < 0 stated.
Reuses exposure_20261114.py (irls, bin_lo) read-only. Output: 391_groups/summary_exposure_prereg19/ (refuses to overwrite).
"""
import hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
OUT = Path(os.environ.get('P19_OUT', BASE / '391_groups/summary_exposure_prereg19'))
ADD = BASE / '391_groups/config/prereg_addendum19.md'
ADD_SHA = 'f6b650726d75d2a21f42dcaabf539803e074e3070ae09ddb2cdd0285b9cc35a4'
TAG = 'confirmatory analysis of already-seen data (post hoc lock), addendum 19'
MIN_CTRL = 30


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def main():
    h = hashlib.sha256(ADD.read_bytes()).hexdigest()
    if h != ADD_SHA: raise SystemExit(f'ADDENDUM 19 CHANGED {h}')
    if OUT.exists() and any(OUT.iterdir()): raise SystemExit(f'{OUT} not empty; refusing to overwrite')
    OUT.mkdir(parents=True, exist_ok=True)
    ex = load(H / '14_groups/exposure_20261114.py', 'ex')
    gc = load(H / '14_groups/groups_core.py', 'gc'); gc.check_plan()
    P = gc.papers(); E = gc.Engine(P); pids = P.index.to_numpy()
    print('papers', len(P), 'teams', E.nteam, 'NB', gc.NB, flush=True)
    P['recog'] = (P.mc_team_outcome_tight == 'strong').astype(float)
    P['recog_excl_unc'] = np.where(P.mc_team_outcome_tight == 'uncertain', np.nan, P.recog)
    P['recall'] = P.recall_level.isin(['R1', 'R2']).astype(float)
    P['cit'] = pd.to_numeric(P.citations, errors='coerce'); P['lc'] = np.log10(1 + P.cit)
    W = E.W(pids)

    # ---- main: thresholds and ratio
    fits = {}
    for yname, y in [('recognition', P.recog), ('recognition_excl_uncertain', P.recog_excl_unc), ('recall', P.recall)]:
        y = y.to_numpy(float); ok = np.isfinite(y) & np.isfinite(P.lc.to_numpy()) & np.isfinite(P.year_c.to_numpy())
        X = np.column_stack([np.ones(ok.sum()), P.lc.to_numpy()[ok], P.year_c.to_numpy()[ok]]); yy = y[ok]
        b0 = ex.irls(X, yy, np.ones(ok.sum()))
        B = np.array([ex.irls(X, yy, W[i, ok]) for i in range(gc.NB)])
        fits[yname] = dict(n=int(ok.sum()), x50=-b0[0] / b0[1], X50=-B[:, 0] / B[:, 1], slope=b0[1], slopes=B[:, 1])
        print(yname, 'n', ok.sum(), 'c50', 10 ** fits[yname]['x50'] - 1, flush=True)
    ci = gc.Engine.ci
    rows = []
    for yname, f in fits.items():
        lo, hi = ci(f['X50'])
        rows.append(dict(label=TAG, quantity=f'c50_{yname}', n=f['n'], est=10 ** f['x50'] - 1, lo=10 ** lo - 1, hi=10 ** hi - 1,
                         log10_1p_est=f['x50'], log10_1p_lo=lo, log10_1p_hi=hi, slope_log10cit=f['slope'],
                         slope_lo=ci(f['slopes'])[0], slope_hi=ci(f['slopes'])[1],
                         x50_in_observed_range=bool(P.lc.min() <= f['x50'] <= P.lc.max()), n_boot_valid=int(np.isfinite(f['X50']).sum())))
    res = {}
    for gname, tag in [('recognition', 'main'), ('recognition_excl_uncertain', 'sensitivity')]:
        r, g = fits['recall'], fits[gname]
        rho = (10 ** r['x50'] - 1) / (10 ** g['x50'] - 1); RHO = (10 ** r['X50'] - 1) / (10 ** g['X50'] - 1)
        lrho = r['x50'] - g['x50']; LRHO = r['X50'] - g['X50']
        ok = np.isfinite(RHO)
        rlo, rhi = ci(RHO[ok]); llo, lhi = ci(LRHO[ok])
        verdict = 'confirmed' if rlo > 1 else ('not shown' if rhi >= 1 else 'reversed')
        rows.append(dict(label=TAG, quantity=f'rho_recall_over_{gname}', n=r['n'], est=rho, lo=rlo, hi=rhi, log10_1p_est=lrho,
                         log10_1p_lo=llo, log10_1p_hi=lhi, n_boot_valid=int(ok.sum()), role=tag, verdict=verdict if tag == 'main' else 'descriptive'))
        res[f'rho_{tag}'] = dict(est=rho, lo=rlo, hi=rhi, log10=lrho, log10_lo=llo, log10_hi=lhi, verdict=verdict, n_boot_valid=int(ok.sum()))
    M = pd.DataFrame(rows); M.to_csv(OUT / 'thresholds_ratio.csv', index=False)

    # ---- secondary: trend of within-bin target - control
    ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr'])
    ds = ds[(ds.readout == 'final') & (ds.layer == 63)].set_index('paper_id').spec_mean_nlr
    P['spec_all'] = ds.reindex(pids).to_numpy()
    print('spec_all nan', int(np.isnan(P.spec_all).sum()), flush=True)
    bins = sorted(P.citation_bin.unique(), key=ex.bin_lo)
    brow, D, BD = [], [], []
    for b in bins:
        sub = P[P.citation_bin == b]; ip = sub.index.to_numpy()
        it, ic = (sub.group_tight == 'target').to_numpy(), (sub.group_tight == 'control').to_numpy()
        used = it.sum() >= MIN_CTRL and ic.sum() >= MIN_CTRL
        row = dict(citation_bin=b, n_papers=len(sub), n_target=int(it.sum()), n_control=int(ic.sum()),
                   median_citations=float(sub.cit.median()), x=float(np.log10(1 + sub.cit.median())), used_in_slope=bool(used))
        if it.sum() and ic.sum():
            et, bt, _ = E.group_mean(ip[it], sub.loc[it, 'spec_all'].to_numpy(float))
            ec, bc, _ = E.group_mean(ip[ic], sub.loc[ic, 'spec_all'].to_numpy(float))
            d, bd = et[0] - ec[0], bt[:, 0] - bc[:, 0]
            row.update(diff=d, lo=ci(bd)[0], hi=ci(bd)[1], var_boot=float(np.nanvar(bd, ddof=1)))
            if used: D.append((row['x'], d, row['var_boot'])); BD.append(bd)
        brow.append(row)
    Bt = pd.DataFrame(brow); Bt.insert(0, 'label', TAG); Bt.to_csv(OUT / 'trend_by_bin.csv', index=False)
    x = np.array([t[0] for t in D]); d = np.array([t[1] for t in D]); w = 1 / np.array([t[2] for t in D]); BD = np.array(BD).T  # NB x nbins

    def wls(yv):
        xm = np.sum(w * x) / w.sum(); ym = np.sum(w * yv) / w.sum()
        return np.sum(w * (x - xm) * (yv - ym)) / np.sum(w * (x - xm) ** 2)
    s0 = wls(d); S = np.array([wls(BD[i]) if np.all(np.isfinite(BD[i])) else np.nan for i in range(BD.shape[0])])
    ok = np.isfinite(S); slo, shi = ci(S[ok])
    sv = 'grows with exposure' if slo > 0 else ('flat' if shi >= 0 else 'shrinks with exposure')
    res['trend'] = dict(slope=s0, lo=slo, hi=shi, verdict=sv, n_bins=int(len(x)), n_boot_valid=int(ok.sum()),
                        unit='change in target - control per 10x median citations (log10 scale)')
    res['label'] = TAG; res['addendum_sha256'] = h; res['n_papers'] = int(len(P)); res['n_teams'] = int(E.nteam); res['NB'] = int(gc.NB)
    json.dump(res, open(OUT / 'prereg19_results.json', 'w'), indent=1, default=float)
    rep = [f'# Addendum 19 results — {TAG}', '', f'Addendum sha256 {h}; {len(P):,} papers, {E.nteam:,} author teams, {gc.NB} team bootstrap draws (seed 391).', '',
           '## Main comparison: threshold ratio', '', M.to_markdown(index=False, floatfmt='.4g'), '',
           f"rho (recall / recognition) = {res['rho_main']['est']:.1f} [{res['rho_main']['lo']:.1f}, {res['rho_main']['hi']:.1f}]; "
           f"log10 rho = {res['rho_main']['log10']:.3f} [{res['rho_main']['log10_lo']:.3f}, {res['rho_main']['log10_hi']:.3f}] -> **{res['rho_main']['verdict']}** (rule: CI of rho entirely above 1).",
           f"Sensitivity (recognition excluding uncertain): rho = {res['rho_sensitivity']['est']:.1f} [{res['rho_sensitivity']['lo']:.1f}, {res['rho_sensitivity']['hi']:.1f}] (descriptive).", '',
           '## Secondary comparison: trend of within-bin target − control', '', Bt.to_markdown(index=False, floatfmt='.4g'), '',
           f"WLS slope = {s0:+.4f} [{slo:+.4f}, {shi:+.4f}] per 10× median citations over {len(x)} bins -> **{sv}**.", '',
           'Labels: confirmatory analysis of already-seen data (point thresholds known since 2026-11-14); single model; bins are stratified samples, '
           'not population rates; recognition at the bottom bins includes the ~25% guess floor of the 4-order multiple-choice rule.']
    (OUT / 'report.md').write_text('\n'.join(rep) + '\n')
    print(json.dumps(res, indent=1, default=float), flush=True); print('DONE', OUT, flush=True)


if __name__ == '__main__':
    main()
