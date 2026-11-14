"""Bottleneck F, "exposure threshold" -- EXPLORATORY (探索性), POST HOC. Not preregistered. CPU only, existing outputs only.

Per Stage 10 citation bin (13 bins, cohort 9,108 papers):
  n papers; recognition = share mc_team_outcome_tight == 'strong' (the pass rule behind groups A/C vs B/D; uncertain counts as
  not passed; also share among strong+fail) and mean orders right mc_team_a (0-4); recall = share recall_level in {R1, R2}
  (>= 1 correct author written); output-layer title-specific signal spec = true - mean(5 false titles), readout 'final' L63,
  log10(1/rank): (a) all authors all name tokens (= Stage 10 spec_mean_nlr), (b) first author all tokens, (c) first author
  first token (token_index 0), for target / control (group_tight) and target - control within bin.
CI: author-team cluster bootstrap (groups_core.Engine: archived folds_own9108_k5s13 team ids, one multinomial team draw,
2,000 draws, seed 391), percentile 95%.
Extra: logistic fits recognition / recall ~ log10(1+citations) + year_c; 50% threshold at mean year, same team draws.
Output: OUT (default /scratch/zhang.zhiqi2/jlens/391_groups/summary_exposure_20261114/); refuses to overwrite.
"""
import importlib.util, os, glob, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
OUT = Path(os.environ.get('EXPO_OUT', BASE / '391_groups/summary_exposure_20261114'))
TAG = 'exploratory (探索性), post hoc'
MIN_CTRL = 30


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def bin_lo(b): return int(str(b).split('-')[0].rstrip('+'))


def first_token_spec(pids):
    """final L63, author 0 token 0: true - mean of false_0..4 (log10(1/rank)); also author 0 all tokens."""
    t = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    t = t[t.author_index == 0]
    def nlr(cond):
        d = R10 / 'raw' / ('' if cond == 'true' else f'cond_{cond}') / 'final/L63'
        fs = sorted(glob.glob(str(d / 'shard_*.npz'))); assert len(fs) == 72, (cond, len(fs))
        parts = [];
        for f in fs:
            z = np.load(f); parts.append(pd.Series(-np.log10(z['rank'].astype(np.float64)), index=z['row_id']))
        s = pd.concat(parts); assert s.index.is_unique; return s
    conds = ['true'] + [f'false_{k}' for k in range(5)]
    for c in conds: t[c] = t.row_id.map(nlr(c))
    print('first-author token rows', len(t), 'nan share', t[conds].isna().mean().round(5).to_dict(), flush=True)
    t['spec'] = t['true'] - t[[f'false_{k}' for k in range(5)]].mean(1)
    tok0 = t[t.token_index == 0].set_index('paper_id').spec
    fa_all = t.groupby('paper_id').spec.apply(lambda s: s.mean())
    # note: author-level mean of per-token spec == true_mean - false_mean (linear), same as groups_build author_signal
    return tok0.reindex(pids), fa_all.reindex(pids)


def irls(X, y, w, it=50):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        eta = X @ b; p = 1 / (1 + np.exp(-eta)); v = np.maximum(p * (1 - p), 1e-10)
        z = eta + (y - p) / v; Xw = X * (w * v)[:, None]
        try: nb = np.linalg.solve(Xw.T @ X, Xw.T @ z)
        except np.linalg.LinAlgError: return np.full(X.shape[1], np.nan)
        if np.max(np.abs(nb - b)) < 1e-9: b = nb; break
        b = nb
    return b


def main():
    if OUT.exists() and any(OUT.iterdir()): raise SystemExit(f'{OUT} not empty; refusing to overwrite')
    OUT.mkdir(parents=True, exist_ok=True)
    gc = load(H / '14_groups/groups_core.py', 'gc'); gc.check_plan()
    P = gc.papers()
    print('papers', len(P), 'NB', gc.NB, flush=True)
    E = gc.Engine(P); print('teams', E.nteam, flush=True)
    pids = P.index.to_numpy()
    # signals
    ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr'])
    ds = ds[(ds.readout == 'final') & (ds.layer == 63)].set_index('paper_id').spec_mean_nlr
    sg = pd.read_parquet(BASE / '391_groups/data/paper_signal.parquet', filters=[('readout', '==', 'final'), ('layer', '==', 63), ('who', '==', 'all'), ('role', '==', 'all')])
    sg = sg.set_index('paper_id').spec
    chk = (ds.reindex(pids) - sg.reindex(pids)).abs().max(); print('check spec_all: stage10 vs groups_build max|diff|', chk, flush=True)
    if not chk < 1e-4: print('WARN spec_all mismatch', chk, flush=True)
    tok0, fa_all = first_token_spec(pids)
    asig = pd.read_parquet(BASE / '391_groups/data/author_signal.parquet', filters=[('readout', '==', 'final'), ('layer', '==', 63), ('author_index', '==', 0)])
    chk2 = (asig.set_index('paper_id').spec.reindex(pids) - fa_all).abs().max(); print('check first-author all tokens vs author_signal max|diff|', chk2, flush=True)
    if not chk2 < 1e-4: print('WARN first-author mismatch', chk2, flush=True)
    P['spec_all'] = ds.reindex(pids).to_numpy(); P['spec_fa_all'] = fa_all.to_numpy(); P['spec_fa_tok0'] = tok0.to_numpy()
    P['recog'] = (P.mc_team_outcome_tight == 'strong').astype(float)
    P['recog_excl_unc'] = np.where(P.mc_team_outcome_tight == 'uncertain', np.nan, P.recog)
    P['recall'] = P.recall_level.isin(['R1', 'R2']).astype(float)
    assert ((P.recall == 1) == (P.m >= 1)).all()
    P['cit'] = pd.to_numeric(P.citations, errors='coerce'); P['lc'] = np.log10(1 + P.cit)
    P['bin_lo'] = P.citation_bin.map(bin_lo)
    bins = sorted(P.citation_bin.unique(), key=bin_lo)
    SIG = ['spec_all', 'spec_fa_all', 'spec_fa_tok0']
    rows, boots = [], {}
    def put(row, name, est, boot):
        row[name] = est; lo, hi = gc.Engine.ci(boot); row[name + '_lo'] = lo; row[name + '_hi'] = hi
    for b in bins:
        sub = P[P.citation_bin == b]; ip = sub.index.to_numpy()
        row = dict(citation_bin=b, n_papers=len(sub), cit_min=int(sub.cit.min()), cit_max=int(sub.cit.max()),
                   n_strong=int((sub.mc_team_outcome_tight == 'strong').sum()), n_fail=int((sub.mc_team_outcome_tight == 'fail').sum()),
                   n_uncertain=int((sub.mc_team_outcome_tight == 'uncertain').sum()), n_recall=int(sub.recall.sum()))
        V = sub[['recog', 'recog_excl_unc', 'mc_team_a', 'recall']].to_numpy(float)
        est, boot, _ = E.group_mean(ip, V)
        for j, nm in enumerate(['recognition_rate', 'recognition_rate_excl_uncertain', 'mean_orders_right', 'recall_rate']):
            put(row, nm, est[j], boot[:, j]); boots[(b, nm)] = boot[:, j]
        it, ic = sub.group_tight == 'target', sub.group_tight == 'control'
        row['n_target'] = int(it.sum()); row['n_control'] = int(ic.sum()); row['control_lt30_descriptive_only'] = bool(ic.sum() < MIN_CTRL)
        for s in SIG:
            et, bt, _ = E.group_mean(ip[it.to_numpy()], sub.loc[it, s].to_numpy(float))
            if ic.sum() > 0:
                ec, bc, _ = E.group_mean(ip[ic.to_numpy()], sub.loc[ic, s].to_numpy(float))
            else:
                ec, bc = np.array([np.nan]), np.full((gc.NB, 1), np.nan)
            put(row, f'{s}_target', et[0], bt[:, 0]); put(row, f'{s}_control', ec[0], bc[:, 0])
            put(row, f'{s}_diff', et[0] - ec[0], bt[:, 0] - bc[:, 0]); boots[(b, f'{s}_diff')] = bt[:, 0] - bc[:, 0]
            ea, ba, _ = E.group_mean(ip, sub[s].to_numpy(float)); put(row, f'{s}_allpapers', ea[0], ba[:, 0])
        rows.append(row)
    T = pd.DataFrame(rows)
    # pooled within-bin target - control (bins with >= 30 in both groups; Stage 10 weights n_a n_b/(n_a+n_b))
    pool = E.within_bin(pids, (P.group_tight == 'target').to_numpy(), (P.group_tight == 'control').to_numpy(), P.citation_bin.to_numpy(),
                        P[SIG].to_numpy(float), MIN_CTRL, MIN_CTRL)
    prow = dict(citation_bin='pooled within-bin (bins with >=30 per group)', n_papers=int(pool['n_a'][0] + pool['n_b'][0]),
                n_target=int(pool['n_a'][0]), n_control=int(pool['n_b'][0]))
    for j, s in enumerate(SIG): put(prow, f'{s}_diff', pool['est'][j], pool['boot'][:, j])
    prow['bins_used'] = pool['bins'][0]
    T = pd.concat([T, pd.DataFrame([prow])], ignore_index=True)
    T.insert(0, 'label', TAG)
    T.to_csv(OUT / 'exposure_by_bin.csv', index=False); print('wrote exposure_by_bin.csv', flush=True)

    # logistic fits + thresholds
    W = E.W(pids); lrows = []
    for yname, y in [('recognition', P.recog), ('recognition_excl_uncertain', P.recog_excl_unc), ('recall', P.recall)]:
        y = y.to_numpy(float); ok = np.isfinite(y) & np.isfinite(P.lc.to_numpy()) & np.isfinite(P.year_c.to_numpy())
        X = np.column_stack([np.ones(ok.sum()), P.lc.to_numpy()[ok], P.year_c.to_numpy()[ok]]); yy = y[ok]
        b0 = irls(X, yy, np.ones(ok.sum()))
        B = np.array([irls(X, yy, W[i, ok]) for i in range(gc.NB)])
        x50 = -b0[0] / b0[1]; X50 = -B[:, 0] / B[:, 1]
        # threshold only meaningful if slope > 0 and inside observed range
        r = dict(label=TAG, outcome=yname, n=int(ok.sum()), year_mean=float(P.year.mean()))
        for j, nm in enumerate(['intercept', 'slope_log10cit', 'slope_year']):
            r[nm] = b0[j]; r[nm + '_lo'], r[nm + '_hi'] = gc.Engine.ci(B[:, j])
        r['odds_ratio_per_10x_citations'] = float(np.exp(b0[1]))
        r['x50_log10_1p_cit'] = x50; r['x50_lo'], r['x50_hi'] = gc.Engine.ci(X50)
        r['cit50'] = 10 ** x50 - 1; r['cit50_lo'], r['cit50_hi'] = 10 ** r['x50_lo'] - 1, 10 ** r['x50_hi'] - 1
        r['x50_in_observed_range'] = bool(P.lc.min() <= x50 <= P.lc.max())
        r['n_boot_valid'] = int(np.isfinite(X50).sum())
        r['p_at_0_cit_mean_year'] = float(1 / (1 + np.exp(-b0[0])))
        r['p_at_max_cit_mean_year'] = float(1 / (1 + np.exp(-(b0[0] + b0[1] * P.lc.max()))))
        lrows.append(r); print(yname, {k: r[k] for k in ['slope_log10cit', 'cit50', 'cit50_lo', 'cit50_hi']}, flush=True)
    L = pd.DataFrame(lrows); L.to_csv(OUT / 'logistic_thresholds.csv', index=False)
    # also the empirical bin where the rate first crosses 50%
    figure(T.iloc[:-1], L, P)
    report(T, L, chk, chk2, E.nteam)
    print('DONE', OUT, flush=True)


def figure(T, L, P):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    x = np.arange(len(T)); lab = T.citation_bin.tolist()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 7.2), sharex=True, gridspec_kw=dict(height_ratios=[1.15, 1]))
    c1, c2, c3 = '#2b6cb0', '#c05621', '#2f855a'
    for nm, c, t in [('recognition_rate', c1, 'recognition (multiple-choice pass, strong)'), ('recall_rate', c2, 'open recall (>=1 correct author written)')]:
        a1.fill_between(x, T[nm + '_lo'], T[nm + '_hi'], color=c, alpha=.18, lw=0); a1.plot(x, T[nm], 'o-', color=c, label=t, ms=4)
    a1.axhline(.5, color='grey', lw=.7, ls=':'); a1.set_ylim(0, 1); a1.set_ylabel('share of papers'); a1.grid(alpha=.2)
    a1.legend(loc='upper left', fontsize=8.5, frameon=False)
    a1.set_title('Exposure threshold by citation bin (Stage 10 cohort, n=9,108) -- exploratory, post hoc', fontsize=10)
    d = T['spec_all_diff'].to_numpy(float); lo, hi = T['spec_all_diff_lo'].to_numpy(float), T['spec_all_diff_hi'].to_numpy(float)
    small = T['control_lt30_descriptive_only'].to_numpy(bool)
    a2.fill_between(x[~np.isnan(d)], lo[~np.isnan(d)], hi[~np.isnan(d)], color=c3, alpha=.18, lw=0)
    a2.plot(x, d, '-', color=c3, lw=1.2)
    a2.plot(x[~small], d[~small], 'o', color=c3, ms=5, label='target - control (control n >= 30)')
    a2.plot(x[small], d[small], 'o', mfc='white', mec=c3, ms=5, label='control n < 30: descriptive only')
    a2.axhline(0, color='k', lw=.7); a2.grid(alpha=.2)
    a2.set_ylabel('spec target - control\n(final L63, log10(1/rank), all name tokens)', fontsize=9)
    a2.legend(loc='upper left', fontsize=8.5, frameon=False)
    for i, (nt, nc) in enumerate(zip(T.n_target, T.n_control)): a2.text(i, 0.03, f'{nt}/{nc}', transform=a2.get_xaxis_transform(), ha='center', va='bottom', fontsize=6.5, color='grey')
    a2.set_xticks(x); a2.set_xticklabels(lab, rotation=40, ha='right', fontsize=8); a2.set_xlabel('citation bin  (grey: n target / n control)')
    fig.text(.01, .005, 'Bands: author-team cluster bootstrap 95% CI (2,000 draws). 4097+ bin has no control papers.', fontsize=7, color='grey')
    fig.tight_layout(rect=(0, .02, 1, 1))
    for ext in ('png', 'svg'): fig.savefig(OUT / f'exposure_curves.{ext}', dpi=160)
    print('wrote figure', flush=True)


def f3(v): return 'NA' if pd.isna(v) else f'{v:.3f}'


def report(T, L, chk, chk2, nteam):
    B = T.iloc[:-1]
    lines = ['# Exposure threshold by citation bin -- exploratory (探索性), post hoc', '',
             'Not preregistered. CPU only, existing Stage 10 outputs. Script: ~/jlens_work/14_groups/exposure_20261114.py.', '',
             f'Cohort 9,108 papers, 13 Stage 10 citation bins. CI = author-team cluster bootstrap 95% (2,000 draws, {nteam} teams, '
             'archived folds_own9108_k5s13 team ids, groups_core.Engine, seed 391).', '',
             'Definitions: recognition = mc_team_outcome_tight == strong (pass rule behind A/C vs B/D; uncertain counted as not passed); '
             'recall = recall_level R1 or R2 (>=1 correct author written, m >= 1); spec = true - mean of 5 false titles, readout final L63, '
             'log10(1/rank); target/control = Stage 10 group_tight.', '',
             '| bin | n | recognition [95% CI] | recog. excl. uncertain | mean orders right (0-4) | recall [95% CI] | n tgt/ctl | spec tgt | spec ctl | spec tgt-ctl [95% CI] | 1st-author tok0 tgt-ctl |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for _, r in B.iterrows():
        flag = ' (ctl<30, descr.)' if r.control_lt30_descriptive_only else ''
        lines.append(f'| {r.citation_bin} | {r.n_papers} | {f3(r.recognition_rate)} [{f3(r.recognition_rate_lo)}, {f3(r.recognition_rate_hi)}] | '
                     f'{f3(r.recognition_rate_excl_uncertain)} | {r.mean_orders_right:.2f} [{r.mean_orders_right_lo:.2f}, {r.mean_orders_right_hi:.2f}] | '
                     f'{f3(r.recall_rate)} [{f3(r.recall_rate_lo)}, {f3(r.recall_rate_hi)}] | {r.n_target}/{r.n_control} | {f3(r.spec_all_target)} | {f3(r.spec_all_control)} | '
                     f'{f3(r.spec_all_diff)} [{f3(r.spec_all_diff_lo)}, {f3(r.spec_all_diff_hi)}]{flag} | {f3(r.spec_fa_tok0_diff)} [{f3(r.spec_fa_tok0_diff_lo)}, {f3(r.spec_fa_tok0_diff_hi)}] |')
    p = T.iloc[-1]
    lines += ['', f'Pooled within-bin target - control (bins with >= 30 per group: {p.bins_used}): all tokens {f3(p.spec_all_diff)} '
              f'[{f3(p.spec_all_diff_lo)}, {f3(p.spec_all_diff_hi)}]; first author all tokens {f3(p.spec_fa_all_diff)} [{f3(p.spec_fa_all_diff_lo)}, {f3(p.spec_fa_all_diff_hi)}]; '
              f'first author first token {f3(p.spec_fa_tok0_diff)} [{f3(p.spec_fa_tok0_diff_lo)}, {f3(p.spec_fa_tok0_diff_hi)}].', '',
              '## Logistic fits (outcome ~ log10(1+citations) + year centred), 50% threshold at mean year', '',
              '| outcome | n | slope per log10 [95% CI] | year slope | citations at 50% [95% CI] | in observed range |', '|---|---|---|---|---|---|']
    for _, r in L.iterrows():
        lines.append(f'| {r.outcome} | {r.n} | {r.slope_log10cit:.3f} [{r.slope_log10cit_lo:.3f}, {r.slope_log10cit_hi:.3f}] | {r.slope_year:.3f} [{r.slope_year_lo:.3f}, {r.slope_year_hi:.3f}] | '
                     f'{r.cit50:.0f} [{r.cit50_lo:.0f}, {r.cit50_hi:.0f}] | {r.x50_in_observed_range} |')
    lines += ['', '## Checks', '', f'- spec all tokens: Stage 10 summary_title vs 391_groups paper_signal max |diff| = {chk:.2e}.',
              f'- first author all tokens: recomputed from raw vs 391_groups author_signal max |diff| = {chk2:.2e}.', '',
              '## Caveats', '',
              '- Exploratory (探索性), post hoc; not preregistered; descriptive.',
              '- Bins were built by stratified sampling (800 per bin, fewer at the top); rates are per-bin, not population rates.',
              '- Group (target/control) is defined by recognition + recall, so recognition and target share move together by construction; '
              'spec target - control within a bin is the only group comparison.',
              '- Control has < 30 papers in 1025-2048, 2049-4096 and 4097+ (none in 4097+): descriptive only.',
              '- Recognition at the bottom bins includes the ~25% fixed-preference/guess floor of the 4-order multiple-choice rule.',
              '- Logistic fit assumes a monotone logit-linear trend in log10 citations; thresholds outside the observed range are extrapolation.',
              '', 'Files: exposure_by_bin.csv, logistic_thresholds.csv, exposure_curves.png/.svg, run log in ~/jlens_work/14_groups/logs/.']
    (OUT / 'report.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
