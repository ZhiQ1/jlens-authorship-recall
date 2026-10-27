"""Stage 10 + Stage 11 — R0-only sensitivity (2026-10-27, review request; CPU, existing outputs only).

group_tight target/control pool R0 (no true author written) and R1 (some written, HR2 > 0.5). 511 of 4,621 targets
are R1 but only 34 of 2,220 controls, so part of the target advantage could come from papers whose authors the model
can partly write. Here both groups keep R0 papers only and the main contrasts are recomputed with the frozen
Stage 10 / Stage 11 analysis functions (same strata, weights, bootstrap):
  Stage 10  - title-specific target - control within citation bin, every readout x layer (+ output), R0 only,
              also without bins 0-4; true-title-only target - control (paper_scores); R1 vs R0 within target.
  Stage 11  - E1 / E1t patching and E2 / E2n knockout curves on the R0 papers of the Stage 11 sample.
Outputs: 351_stage10/summary_r0/, 361_stage11/summary_r0/, report 351_stage10/reports/r0_sensitivity.md.
"""
import importlib.util, sys
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


s10 = load(H / '10_stage10/351_stage10.py', 's10')
sys.path.insert(0, str(H / '11_stage11')); import stage11_analyze as a11


def fmt(r, m): return f'{r[m + "_diff"]:+.3f} [{r[m + "_lo"]:+.3f}, {r[m + "_hi"]:+.3f}]'


def main():
    S = R10 / 'summary_r0'; S.mkdir(exist_ok=True); L = ['# R0-only sensitivity (Stage 10 and Stage 11)', '']
    ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet')
    ct = pd.crosstab(ds.drop_duplicates('paper_id').group_tight, ds.drop_duplicates('paper_id').recall_level)
    L += ['Papers by group and recall level:', '', ct.to_string(), '']
    mets = ['spec_mean_nlr', 'spec_author_mean_nlr', 'spec_mean_nlr_surname_first', 'total_mean_nlr', 'topic_mean_nlr']
    rng = np.random.default_rng(3512)
    full = pd.read_csv(R10 / 'summary_title/B_spec_target_vs_control_within_bin.csv')
    r0 = s10.stratified_diff(ds[ds.recall_level == 'R0'], 'group_tight', 'target', 'control', 'citation_bin', mets, rng)
    r0.to_csv(S / 'B_spec_target_vs_control_within_bin_R0.csv', index=False)
    r0l = s10.stratified_diff(ds[(ds.recall_level == 'R0') & ~ds.citation_bin.isin(s10.LOW_BINS)], 'group_tight', 'target', 'control', 'citation_bin', mets[:3], rng)
    r0l.to_csv(S / 'B_sens_drop_low_bins_R0.csv', index=False)
    # within target: R1 - R0 (same strata rule)
    tg = ds[ds.group_tight == 'target']
    r1 = s10.stratified_diff(tg, 'recall_level', 'R1', 'R0', 'citation_bin', mets[:3], rng, min_n=10)
    r1.to_csv(S / 'target_R1_minus_R0_within_bin.csv', index=False)
    L += ['## Stage 10: title-specific target - control within citation bin (mean over name tokens, log10(1/rank))', '',
          '| readout | layer | all (R0+R1) | R0 only | R0 only, bins 0-4 dropped | R0 only, surname first token | n target / control (R0) |', '|---|---|---|---|---|---|---|']
    for _, r in r0.sort_values(['readout', 'layer']).iterrows():
        f = full[(full.readout == r.readout) & (full.layer == r.layer)]; g = r0l[(r0l.readout == r.readout) & (r0l.layer == r.layer)]
        L.append(f'| {r.readout} | {r.layer} | {fmt(f.iloc[0], "spec_mean_nlr") if len(f) else "-"} | {fmt(r, "spec_mean_nlr")} | '
                 f'{fmt(g.iloc[0], "spec_mean_nlr") if len(g) else "-"} | {fmt(r, "spec_mean_nlr_surname_first")} | {r.n_a} / {r.n_b} |')
    L += ['', '## Within target: R1 - R0 papers, title-specific (within citation bin, min 10 per cell)', '', '| readout | layer | R1 - R0 | n R1 / R0 |', '|---|---|---|---|']
    for _, r in r1[r1.layer.isin([48, 56, 62, 63])].sort_values(['readout', 'layer']).iterrows():
        L.append(f'| {r.readout} | {r.layer} | {fmt(r, "spec_mean_nlr")} | {r.n_a} / {r.n_b} |')
    # true title only (no false-title subtraction)
    ps = pd.read_parquet(R10 / 'summary/paper_scores.parquet')
    tm = [m for m in ('mean_nlr', 'author_mean_nlr') if m in ps.columns]
    tt = s10.stratified_diff(ps[ps.recall_level == 'R0'], 'group_tight', 'target', 'control', 'citation_bin', tm, rng)
    tt.to_csv(S / 'B_true_target_vs_control_within_bin_R0.csv', index=False)
    ft = pd.read_csv(R10 / 'summary/B_target_vs_control_within_bin.csv')
    L += ['', '## Stage 10: true title only, target - control within bin', '', '| readout | layer | all | R0 only |', '|---|---|---|---|']
    for _, r in tt[tt.layer.isin([48, 56, 62, 63])].sort_values(['readout', 'layer']).iterrows():
        f = ft[(ft.readout == r.readout) & (ft.layer == r.layer)]
        L.append(f'| {r.readout} | {r.layer} | {fmt(f.iloc[0], "mean_nlr") if len(f) else "-"} | {fmt(r, "mean_nlr")} |')

    # ---------------- Stage 11 on the R0 papers of its sample
    S11 = R11 / 'summary_r0'; S11.mkdir(exist_ok=True)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    rl = ds.drop_duplicates('paper_id').set_index('paper_id').recall_level
    smp['recall_level'] = smp.paper_id.map(rl)
    L += ['', '## Stage 11 sample by recall level', '', pd.crosstab(smp.group, smp.recall_level).to_string(), '']
    s0 = smp[smp.recall_level == 'R0'][['paper_id', 'group', 'citation_bin']]
    d = None
    for name, sub, title in (('E1', 'patch', 'patching of the tokens after the title, R0 papers only'),
                             ('E1t', 'patch_title', 'patching of the last title token, R0 papers only')):
        dd, layers = a11.load_unit_dir(R11 / 'raw' / sub)
        if name == 'E1': d = dd
        L += a11.patch_section(name, title, dd, layers, toks, s0, S11)
    for name, sub, title in (('E2', 'knockout', 'knockout of all positions after the title, R0 papers only'),
                             ('E2n', 'knockout_name', 'knockout of ":" and the name positions, R0 papers only')):
        k, kl = a11.load_unit_dir(R11 / 'raw' / sub)
        L += a11.ko_section(name, title, k, kl, d, toks, s0, S11)
    (R10 / 'reports/r0_sensitivity.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    main()
