"""Report for plan 2026-11-14b item 3 (post hoc, descriptive): clean donor set vs V0 / Vpd. Reads summary_clean_donor_20261114/*,
per-paper parity of the original fit against summary_b1_e4b5/probe (spec0, dropped_k) and the published perdonor_by_run_layer.csv."""
from pathlib import Path
import numpy as np, pandas as pd

R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); OUT = R13 / 'summary_clean_donor_20261114'
T = pd.read_csv(OUT / 'clean_vs_v0_vpd.csv'); S = pd.read_csv(OUT / 'train_sizes.csv'); U = pd.read_csv(OUT / 'usable_false_titles.csv')
PUB = pd.read_csv(R13 / 'summary_b1_e4b5/perdonor_by_run_layer.csv')
RUNS = ['surname_first', 'given_first', 'initial', 'given_cont', 'surname_cont', 'all_tokens']
NAME = {'surname_first': 'surname first token', 'given_first': 'given first token', 'initial': 'initial', 'given_cont': 'given rest',
        'surname_cont': 'surname rest', 'all_tokens': 'all tokens pooled (new run)'}
f3 = lambda v, lo, hi: '-' if pd.isna(v) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')

# parity
par = []
for run in RUNS:
    for l in (40, 48):
        f = OUT / f'probe/perpaper_{run}_L{l}.parquet'; g = R13 / f'summary_b1_e4b5/probe/perpaper_{run}_L{l}.parquet'
        if not f.exists(): continue
        a = pd.read_parquet(f).set_index('paper_id')
        r = dict(run=run, layer=l)
        if g.exists():
            b = pd.read_parquet(g).set_index('paper_id').loc[a.index]
            r |= dict(max_abs_spec0_diff=float(np.nanmax(np.abs(a.spec0 - b.spec0))), mean_abs_spec0_diff=float(np.nanmean(np.abs(a.spec0 - b.spec0))),
                      dropped_agree=float(np.mean([(a[f'dropped_{k}'] == b[f'dropped_{k}']).mean() for k in range(5)])))
        for v in ('V0', 'Vpd'):
            m = T[(T.run == run) & (T.layer == l) & (T.version == v)]; p = PUB[(PUB.run == run) & (PUB.layer == l) & (PUB.version == v)]
            if len(m) and len(p):
                r |= {f'{v}_spec_diff': float(m.spec.iloc[0] - p.spec.iloc[0]), f'{v}_tc_diff': float(m.tc.iloc[0] - p.tc.iloc[0]),
                      f'{v}_tclo_diff': float(m.tc_lo.iloc[0] - p.tc_lo.iloc[0]), f'{v}_tchi_diff': float(m.tc_hi.iloc[0] - p.tc_hi.iloc[0])}
        par.append(r)
PAR = pd.DataFrame(par); PAR.to_csv(OUT / 'parity.csv', index=False)

L = ['# Title-position probe with a fully clean donor set (plan 2026-11-14b item 3)', '', '**Post hoc, descriptive.**', '',
     'Method: addendum-9 probe (title-last residual -> ridge -> own L63 state at the name-token positions -> final norm + lm_head rows of 9,137 name token ids -> log10(1/rank)); archived author-team folds; training-fold standardisation; alpha on fold 0. '
     '**clean**: when testing fold f, every paper that donates any of the 5 false titles of any paper in fold f is removed from the training set; ridge refit; spec = probe(true) - mean of the 5 false titles; every target / control paper kept. '
     '**randsize** (added after the tiny run): same number of training papers per fold as clean, drawn at random from the original training set (donors may remain), so it separates the effect of training-set size from leakage. '
     'V0 / Vpd / V5x0 come from the original fit, rerun in the same job (parity below). target - control: within citation bin (bins >= 30 per group, weights n_t n_c/(n_t+n_c)); team-cluster bootstrap 95% CI, 2,000 draws; * = CI excludes 0. '
     'all_tokens = a new run: all tokens of the five roles in one target / gold set per paper (punctuation and particles excluded); its V0 / Vpd are computed here and have no published counterpart.', '']
L += ['## Training-set sizes per fold', '', '| run | fold | test papers | train original | train clean | removed |', '|---|---|---|---|---|---|']
for _, r in S.iterrows(): L.append(f'| {r.run} | {r.fold} | {r.n_test} | {r.n_train_orig} | {r.n_train_clean} | {r.n_removed} |')
L += ['', '## Usable (clean) false titles per test paper', '', '| run | papers | 0 / 1 / 2 / 3 / 4 / 5 usable |', '|---|---|---|']
for _, r in U.iterrows(): L.append(f'| {r.run} | {r.papers} | ' + ' / '.join(str(r[f"n_usable_{i}"]) for i in range(6)) + ' |')
for l in (40, 48):
    L += ['', f'## L{l}: spec and target - control', '', '| role | version | n (T / C) | spec | target - control (bins) |', '|---|---|---|---|---|']
    for run in RUNS:
        for v in ('clean', 'randsize_5mean', 'Vpd', 'V0', 'V5x0', 'clean_f0only'):
            m = T[(T.run == run) & (T.layer == l) & (T.version == v)]
            if not len(m): continue
            r = m.iloc[0]
            L.append(f'| {NAME[run]} | {v} | {r.n} ({r.n_target} / {r.n_control}) | {f3(r.spec, r.lo, r.hi)} | {f3(r.tc, r.tc_lo, r.tc_hi)} ({r.tc_bins}) |')
L += ['', '## Parity (original fit rerun vs stored addendum-10 per-paper files and published perdonor_by_run_layer.csv; WARN only)', '', PAR.round(5).to_markdown(index=False)]
sf = T[(T.run == 'surname_first') & (T.layer == 40) & (T.version == 'clean')].iloc[0]
L += ['', '## Key answer', '', f'surname first token, L40, clean: target - control {f3(sf.tc, sf.tc_lo, sf.tc_hi)} -> CI ' + ('excludes 0.' if sf.tc_lo > 0 or sf.tc_hi < 0 else 'includes 0.')]
(OUT / 'report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
