"""Stage 13 X6 analysis (CPU), rules from config/prereg_addendum3.json.
Stage 11 E1 tail patching (true -> false) with the 5 false titles: false_0 = Stage 11 raw/patch (reproduced exactly by
xf_patch false_0 shard 0), false_1..false_4 = 381_stage13/raw/xf_patch/false_j.
R(l) = mean over papers (patched - false) / mean (true - false) at the model output, per false title and the plain average
of the 5; target / control / all; 95% team-cluster bootstrap (addendum 2; the same team draws for all 5 titles, so the
average and the per-title differences are paired). Per token nlr = log10(1/rank), averaged within paper first (as Stage 11).
Outputs: summary_x6/x6_recovery.csv, reports/x6_report.md"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; OUT = ROOT / 'summary_x6'; OUT.mkdir(parents=True, exist_ok=True); NB = 2000
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d):
    fs = sorted(Path(d).glob('shard_*.npz'))
    if not fs: return None, None, 0
    zs = [np.load(f) for f in fs]
    return {k: np.concatenate([z[k] for z in zs]) for k in ('row_id', 'rank_true', 'rank_false', 'rank_patch')}, zs[0]['layers'], len(fs)


def main(test_root=None):
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']]
    src = {'false_0': R11 / 'raw/patch'} | {t: ROOT / 'raw/xf_patch' / t for t in TITLES[1:]}
    if test_root: src = {t: Path(test_root) / t for t in TITLES}
    pp, layers, nshard, warn = {}, None, {}, []
    for t, d in src.items():
        dd, ly, n = load_dir(d); nshard[t] = n
        if dd is None: warn.append(f'{t}: no shards'); continue
        if layers is None: layers = [int(x) for x in ly]
        elif [int(x) for x in ly] != layers: warn.append(f'{t}: layers {list(ly)} differ from {layers}')
        df = pd.DataFrame({'paper_id': toks.loc[dd['row_id']].paper_id.to_numpy(), 'true': nlr(dd['rank_true']), 'false': nlr(dd['rank_false'])})
        for i, l in enumerate(ly): df[f'p{int(l)}'] = nlr(dd['rank_patch'][:, i])
        pp[t] = df.groupby('paper_id').mean()
    have = [t for t in TITLES if t in pp]
    # one team draw shared by every title and group
    allp = sorted(set().union(*[set(pp[t].index) for t in have])); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in allp]))
    cnt = np.random.default_rng(13).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)
    Wall = pd.DataFrame(cnt[:, codes].T, index=allp)                     # [paper, draw]
    grp = smp.set_index('paper_id').group
    rows, boots = [], {}
    for g in ('target', 'control', 'all'):
        for t in have:
            s = pp[t] if g == 'all' else pp[t][grp.reindex(pp[t].index).to_numpy() == g]
            W = Wall.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy()
            for l in layers:
                num = (s[f'p{l}'] - s['false']).to_numpy()
                b = (num @ W) / (den @ W); boots[(g, t, l)] = b
                rows.append(dict(group=g, false_title=t, layer=l, n_papers=len(s), R=num.mean() / den.mean(), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5),
                                 true_minus_false=den.mean()))
        for l in layers:
            est = np.mean([r['R'] for r in rows if r['group'] == g and r['layer'] == l]); b = np.mean([boots[(g, t, l)] for t in have], 0)
            rows.append(dict(group=g, false_title='average', layer=l, n_papers=np.nan, R=est, lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5), true_minus_false=np.nan))
            for t in have[1:]:
                d = boots[(g, t, l)] - boots[(g, 'false_0', l)]
                rows.append(dict(group=g, false_title=f'{t} - false_0', layer=l, n_papers=np.nan, R=[r['R'] for r in rows if r['group'] == g and r['false_title'] == t and r['layer'] == l][0]
                                 - [r['R'] for r in rows if r['group'] == g and r['false_title'] == 'false_0' and r['layer'] == l][0], lo=np.percentile(d, 2.5), hi=np.percentile(d, 97.5), true_minus_false=np.nan))
    D = pd.DataFrame(rows); D.to_csv(OUT / 'x6_recovery.csv', index=False)
    f = lambda g, t, l: D[(D.group == g) & (D.false_title == t) & (D.layer == l)].iloc[0]
    fm = lambda r: f'{r.R:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}]'
    L = ['# Stage 13 X6: Stage 11 tail patching with all 5 false titles', '',
         f'Rule: config/prereg_addendum3.json (X6). Shards: ' + ', '.join(f'{t} {nshard[t]}' for t in TITLES) + '.',
         'R(l) = mean(patched - false) / mean(true - false) at the output; papers first averaged over their name tokens; 95% team-cluster bootstrap (2,000 draws, shared across titles).', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    for g in ('target', 'control', 'all'):
        L += [f'## {g}', '', '| layer | ' + ' | '.join(have) + ' | average |', '|---|' + '---|' * (len(have) + 1)]
        for l in layers: L.append(f'| L{l} | ' + ' | '.join(fm(f(g, t, l)) for t in have) + f' | {fm(f(g, "average", l))} |')
        L += ['', 'true - false (denominator): ' + ', '.join(f'{t} {f(g, t, layers[0]).true_minus_false:.3f}' for t in have), '']
    L += ['## Pre-registered check (addendum 3)', '',
          'Claim holds if: average R(L48) in [0.70, 0.95] and average R(L52) >= 0.95, and every false title has R(L48) within 0.10 of false_0 and R(L52) >= 0.90.', '']
    verdict = {}
    for g in ('target', 'control', 'all'):
        if 48 not in layers or 52 not in layers: L.append(f'- {g}: L48 or L52 missing'); continue
        a48, a52 = f(g, 'average', 48).R, f(g, 'average', 52).R
        per = [(t, f(g, t, 48).R, f(g, t, 52).R) for t in have]; r0 = f(g, 'false_0', 48).R
        c = [0.70 <= a48 <= 0.95, a52 >= 0.95] + [abs(x48 - r0) <= 0.10 and x52 >= 0.90 for t, x48, x52 in per]
        verdict[g] = all(c) and len(have) == 5
        L.append(f'- {g}: average R(L48) {a48:.3f}, R(L52) {a52:.3f}; per title L48/L52: ' + '; '.join(f'{t} {x48:.3f}/{x52:.3f}' for t, x48, x52 in per)
                 + f' -> **{"HOLDS" if verdict[g] else "DOES NOT HOLD"}**')
    if not all(verdict.values()):
        L += ['', 'Where it does not hold, the spread across false titles is the uncertainty of the timing and the 6.11 numbers are quoted as false_0-specific (addendum 3, "otherwise").']
    rep = (ROOT / 'reports/x6_report.md') if not test_root else Path(test_root) / 'x6_report.md'
    rep.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); json.dump(verdict, open(OUT / 'x6_verdict.json', 'w') if not test_root else sys.stdout)
    print('\nX6 ANALYZED')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
