"""E1 target - control timing check (2026-11-13, CPU, read-only on frozen outputs).

R(l) = mean(patched - false) / mean(true - false) at the model output, per group (Stage 11 E1, tail patching true -> false_0).
Team-cluster bootstrap with archived Stage 13 team ids (stage13_c13_s10lib.team_ids = stage13_cpu.group_folds):
  primary : seed 1414, 2,000 multinomial team draws over the 1,186-paper Stage 11 sample (= teamci_s10_12 C02 draws);
            target - control difference computed on the same draws, ratio of means within each draw and group.
  x6-style: seed 13 draws over all papers with X6 data (= stage13_x6_analyze draws), false_0 and the plain 5-title mean.
Parity (WARN only): all-papers R(L48) = 0.825 and team CI vs teamci_s10_12_s11.csv; x6 target false_0 CI vs x6_recovery.csv.
Output: 381_stage13/summary_e1_tc_timing_20261113/{e1_tc_timing.csv, parity.txt}"""
import importlib.util, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R13 = J / '351_stage10', J / '361_stage11', J / '381_stage13'
OUT = R13 / 'summary_e1_tc_timing_20261113'; OUT.mkdir(parents=True, exist_ok=True)
NB = 2000; TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; LAYERS = [40, 48, 50, 52, 54]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
    return {k: np.concatenate([z[k] for z in zs]) for k in ('row_id', 'rank_true', 'rank_false', 'rank_patch')}, [int(x) for x in zs[0]['layers']]


LIB = load(H / '13_stage13/stage13_c13_s10lib.py', 'c13_s10lib'); TEAM = LIB.team_ids()
toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']]
src = {'false_0': R11 / 'raw/patch'} | {t: R13 / 'raw/xf_patch' / t for t in TITLES[1:]}
pp = {}
for t, d in src.items():
    dd, ly = load_dir(d)
    df = pd.DataFrame({'paper_id': toks.loc[dd['row_id']].paper_id.to_numpy(), 'true': nlr(dd['rank_true']), 'false': nlr(dd['rank_false'])})
    for i, l in enumerate(ly): df[f'p{l}'] = nlr(dd['rank_patch'][:, i])
    pp[t] = df.groupby('paper_id').mean()
grp = smp.set_index('paper_id').group


def W_of(pids, seed):
    codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in pids]))
    return pd.DataFrame(np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)[:, codes].T, index=list(pids))


def R_boot(t, g, l, Wall):
    s = pp[t] if g == 'all' else pp[t][grp.reindex(pp[t].index).to_numpy() == g]
    num = (s[f'p{l}'] - s['false']).to_numpy(); den = (s['true'] - s['false']).to_numpy(); W = Wall.loc[s.index].to_numpy()
    return num.mean() / den.mean(), (num @ W) / (den @ W), len(s)


rows, par = [], []
ci = lambda b: np.percentile(b, [2.5, 97.5])
# primary: seed 1414 over the Stage 11 sample (false_0 = Stage 11 E1)
pids0 = pp['false_0'].reset_index().merge(smp, on='paper_id').paper_id.to_numpy()      # same order as patch_section pp
W1 = W_of(pids0, 1414)
# x6-style: seed 13 over sorted union of papers
allp = sorted(set().union(*[set(pp[t].index) for t in TITLES])); W2 = W_of(allp, 13)
for scheme, Wall, titles in (('primary_seed1414_false0', W1, ['false_0']), ('x6_seed13_false0', W2, ['false_0']), ('x6_seed13_mean5', W2, TITLES)):
    for l in LAYERS:
        res = {}
        for g in ('target', 'control', 'all'):
            ests, bs = zip(*[R_boot(t, g, l, Wall)[:2] for t in titles]); res[g] = (np.mean(ests), np.mean(bs, 0))
            lo, hi = ci(res[g][1]); rows.append(dict(scheme=scheme, layer=l, quantity=f'R {g}', estimate=res[g][0], team_lo=lo, team_hi=hi))
        d = res['target'][1] - res['control'][1]; lo, hi = ci(d)
        rows.append(dict(scheme=scheme, layer=l, quantity='R target - control', estimate=res['target'][0] - res['control'][0], team_lo=lo, team_hi=hi,
                         p_two_sided=float(min(1, 2 * min((d <= 0).mean(), (d >= 0).mean())))))
D = pd.DataFrame(rows); D.to_csv(OUT / 'e1_tc_timing.csv', index=False)
# parity (WARN only)
pub = pd.read_csv(R11 / 'summary/E1_recovery.csv'); tci = pd.read_csv(R13 / 'summary_teamci_s10_12/teamci_s10_12_s11.csv'); x6 = pd.read_csv(R13 / 'summary_x6/x6_recovery.csv')
for l in (48, 52):
    a = D[(D.scheme == 'primary_seed1414_false0') & (D.layer == l) & (D.quantity == 'R all')].iloc[0]
    p = pub[(pub.group == 'all') & (pub.layer == l)].iloc[0]; q = tci[tci.quantity.str.contains(f'L{l}') & tci.quantity.str.startswith('E1')].iloc[0]
    par.append(f'L{l} all R {a.estimate:.6f} vs published {p.recovery:.6f}: {"OK" if abs(a.estimate - p.recovery) < 1e-9 else "WARN"}; '
               f'team CI [{a.team_lo:.4f},{a.team_hi:.4f}] vs teamci_s10_12 [{q.team_lo:.4f},{q.team_hi:.4f}]: {"OK" if max(abs(a.team_lo - q.team_lo), abs(a.team_hi - q.team_hi)) < 1e-6 else "WARN"}')
    for g in ('target', 'control'):
        a = D[(D.scheme == 'x6_seed13_false0') & (D.layer == l) & (D.quantity == f'R {g}')].iloc[0]
        q = x6[(x6.group == g) & (x6.false_title == 'false_0') & (x6.layer == l)].iloc[0]
        par.append(f'L{l} {g} x6 false_0 [{a.team_lo:.4f},{a.team_hi:.4f}] vs x6_recovery [{q.lo:.4f},{q.hi:.4f}]: {"OK" if max(abs(a.team_lo - q.lo), abs(a.team_hi - q.hi)) < 1e-6 else "WARN"}')
        a = D[(D.scheme == 'x6_seed13_mean5') & (D.layer == l) & (D.quantity == f'R {g}')].iloc[0]
        q = x6[(x6.group == g) & (x6.false_title == 'average') & (x6.layer == l)].iloc[0]
        par.append(f'L{l} {g} x6 mean5 {a.estimate:.4f} [{a.team_lo:.4f},{a.team_hi:.4f}] vs x6 average {q.R:.4f} [{q.lo:.4f},{q.hi:.4f}]: {"OK" if max(abs(a.team_lo - q.lo), abs(a.team_hi - q.hi)) < 1e-6 else "WARN"}')
(OUT / 'parity.txt').write_text('\n'.join(par) + '\n'); print('\n'.join(par)); print(D.to_string()); print('DONE')
