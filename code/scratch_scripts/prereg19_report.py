"""Write report.md for addendum 19 from the outputs of prereg19_exposure_ratio.py (job 11951874 computed everything and
wrote the csv/json, then crashed at the report step: pandas.to_markdown needs 'tabulate', which is not installed).
No recomputation; reads thresholds_ratio.csv, trend_by_bin.csv, prereg19_results.json."""
import json
from pathlib import Path
import pandas as pd
OUT = Path('/scratch/zhang.zhiqi2/jlens/391_groups/summary_exposure_prereg19')
if (OUT / 'report.md').exists(): raise SystemExit('report.md exists')
M = pd.read_csv(OUT / 'thresholds_ratio.csv'); B = pd.read_csv(OUT / 'trend_by_bin.csv'); r = json.load(open(OUT / 'prereg19_results.json'))
def md(df, cols):
    f = lambda v: '' if pd.isna(v) else (f'{v:.4g}' if isinstance(v, float) else str(v))
    return '\n'.join(['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)] + ['| ' + ' | '.join(f(x) for x in row) + ' |' for row in df[cols].itertuples(index=False)])
rm, rs, t = r['rho_main'], r['rho_sensitivity'], r['trend']
L = [f"# Addendum 19 results — {r['label']}", '',
     f"Addendum sha256 {r['addendum_sha256']}; {r['n_papers']:,} papers, {r['n_teams']:,} author teams, {r['NB']} team bootstrap draws (seed 391). Computed by job 11951874 (prereg19_exposure_ratio.py); this report written by prereg19_report.py from its saved outputs.", '',
     '## Main comparison: threshold ratio', '', md(M, ['quantity', 'n', 'est', 'lo', 'hi', 'log10_1p_est', 'log10_1p_lo', 'log10_1p_hi']), '',
     f"ρ = c50(recall) / c50(recognition) = {rm['est']:.0f} [{rm['lo']:.0f}, {rm['hi']:.0f}]; log10 ρ = {rm['log10']:.3f} [{rm['log10_lo']:.3f}, {rm['log10_hi']:.3f}] → **{rm['verdict']}** (rule: 95% CI of ρ entirely above 1). Valid draws {rm['n_boot_valid']}.",
     f"Sensitivity (recognition excluding uncertain papers, n 7,046; descriptive): ρ = {rs['est']:.0f} [{rs['lo']:.0f}, {rs['hi']:.0f}].", '',
     '## Secondary comparison: trend of within-bin target − control (spec_all, final L63)', '', md(B, ['citation_bin', 'n_papers', 'n_target', 'n_control', 'median_citations', 'used_in_slope', 'diff', 'lo', 'hi']), '',
     f"WLS slope = {t['slope']:+.4f} [{t['lo']:+.4f}, {t['hi']:+.4f}] {t['unit']}, over {t['n_bins']} bins with ≥ 30 papers per group → **{t['verdict']}** (rule: CI above 0).", '',
     'Labels: confirmatory analysis of already-seen data (point thresholds known since 2026-11-14); single model; bins are stratified samples, not population rates; recognition at the bottom bins includes the ~25% guess floor of the 4-order multiple-choice rule; c50 of recall lies inside the observed citation range but near its upper part.']
(OUT / 'report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L[:12]))
