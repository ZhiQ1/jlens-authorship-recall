"""Addendum 13 item C-3 (2026-11-06): E4b and the all-token probe WITHOUT the title-reuse exclusion.

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-3".
Input  per-paper probe outputs of addendum 9 (381_stage13/summary_alltok/probe/perpaper_<run>_L<l>.parquet; run = e4b_parity,
       first_alltok, initial, given_first, given_cont, surname_first, surname_cont). Nothing is refitted: the probe predictions
       are the same; only the paper set differs (title-reuse papers kept vs dropped).
Output per run x layer, target + control papers: title-specific signal (true - false_0) with team-cluster CI (2,000 draws) for
       (a) false_0-exclusion version (= published addendum 9) and (b) no exclusion; target - control within citation bin for both;
       primary L40 contrasts (surname_first, initial, surname - initial) for both.
       Estimators and seeds are copied verbatim from stage13_alltok_report.py (mean_cluster seed 2, strat_cluster seed 1,
       diff_cluster seed 4, paired seed 6), so (a) must reproduce the published numbers exactly.
HARD CHECK (plan): column (a) reproduces published addendum-9 L40 surname_first +0.071 and initial +0.044
       (summary_alltok/primary_L40.csv, |diff| <= 1e-6 for est, lo, hi).
Also   E4b (parity run) no-exclusion vs summary_cpu_trainstd (split group, excl none) cross-check (WARN only).
Usage  stage13_c13_c3.py [--tiny]   (tiny: layer 40 only, runs surname_first, initial, e4b_parity; separate output dir)
"""
import argparse, importlib.util, json, hashlib, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum13.json'; PLAN_SHA = 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e'
PR = R13 / 'summary_alltok/probe'
NB = 2000
RUNS = ['e4b_parity', 'first_alltok', 'initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']
LAYERS = [16, 24, 32, 40, 44, 48, 52, 56, 60]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
OUT = R13 / ('summary_c13/c3_tiny' if a.tiny else 'summary_c13/c3'); OUT.mkdir(parents=True, exist_ok=True)
REP = R13 / ('summary_c13/c3_tiny/c13_C3.md' if a.tiny else 'reports/c13_C3.md')
runs = ['surname_first', 'initial', 'e4b_parity'] if a.tiny else RUNS
layers = [40] if a.tiny else LAYERS

c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS))
META = papers.set_index('paper_id')


# ---------------- estimators: verbatim copies from stage13_alltok_report.py
def team_weights(pids, seed):
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    cnt = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)
    return cnt[:, codes]


def mean_cluster(pids, x, seed=2):
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]
    if len(x) == 0: return np.nan, np.nan, np.nan, 0
    W = team_weights(pids, seed); return x.mean(), *np.percentile((W @ x) / np.maximum(W.sum(1), 1e-9), [2.5, 97.5]), len(x)


def strat_cluster(df, col, gcol, a_, b_, strata, min_n=30, seed=1):
    df = df[df[gcol].isin([a_, b_])].dropna(subset=[col]).reset_index(drop=True); cells = []
    for s, ss in df.groupby(strata):
        ia, ib = ss.index[ss[gcol] == a_].to_numpy(), ss.index[ss[gcol] == b_].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan, 0
    w = np.array([len(x) * len(y) / (len(x) + len(y)) for x, y in cells]); w /= w.sum()
    x = df[col].to_numpy(float); W = team_weights(df.paper_id.to_numpy(), seed)
    est = sum(wi * (x[ia].mean() - x[ib].mean()) for wi, (ia, ib) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (ia, ib) in zip(w, cells):
        bt += wi * ((W[:, ia] @ x[ia]) / np.maximum(W[:, ia].sum(1), 1e-9) - (W[:, ib] @ x[ib]) / np.maximum(W[:, ib].sum(1), 1e-9))
    return est, *np.percentile(bt, [2.5, 97.5]), len(cells)


def diff_cluster(p1, x1, p2, x2, seed=4):
    p1, p2 = np.asarray(p1), np.asarray(p2); allp = np.concatenate([p1, p2]); W = team_weights(allp, seed)
    W1, W2 = W[:, :len(p1)], W[:, len(p1):]
    bt = (W1 @ x1) / np.maximum(W1.sum(1), 1e-9) - (W2 @ x2) / np.maximum(W2.sum(1), 1e-9)
    return x1.mean() - x2.mean(), *np.percentile(bt, [2.5, 97.5])


f3 = lambda v, lo, hi: f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def get(run, l):
    d = pd.read_parquet(PR / f'perpaper_{run}_L{l}.parquet').join(META[['group_tight', 'citation_bin']], on='paper_id')
    d['tc'] = d.group_tight.isin(['target', 'control']); return d


rows = []
for run in runs:
    for l in layers:
        d = get(run, l)
        for ver, keep in (('excl_false0_reuse', ~d.dropped), ('no_exclusion', pd.Series(True, index=d.index))):
            dd = d[keep]; k = dd[dd.tc]
            e = mean_cluster(k.paper_id, k.spec)
            tcd = strat_cluster(dd, 'spec', 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
            rows.append(dict(run=run, layer=l, version=ver, spec=e[0], lo=e[1], hi=e[2], n_tc=e[3], n_target=int((k.group_tight == 'target').sum()),
                             n_control=int((k.group_tight == 'control').sum()), tc_diff=tcd[0], tc_lo=tcd[1], tc_hi=tcd[2], tc_bins=tcd[3]))
        print(run, l, 'done', flush=True)
T = pd.DataFrame(rows); T.to_csv(OUT / 'c3_role_layer.csv', index=False)

# ---------------- primary L40 contrasts, both versions
prim = []
ds_, di_ = get('surname_first', 40), get('initial', 40)
for ver in ('excl_false0_reuse', 'no_exclusion'):
    ks = ds_[ds_.tc & (~ds_.dropped if ver.startswith('excl') else True)]; ki = di_[di_.tc & (~di_.dropped if ver.startswith('excl') else True)]
    e = mean_cluster(ks.paper_id, ks.spec); e2 = mean_cluster(ki.paper_id, ki.spec)
    dd = diff_cluster(ks.paper_id.to_numpy(), ks.spec.to_numpy(float), ki.paper_id.to_numpy(), ki.spec.to_numpy(float))
    pp = ks[['paper_id', 'spec']].merge(ki[['paper_id', 'spec']], on='paper_id', suffixes=('_s', '_i')).dropna()
    ep = mean_cluster(pp.paper_id, pp.spec_s - pp.spec_i, seed=6)
    for q, v, n in (('surname_first', e[:3], e[3]), ('initial', e2[:3], e2[3]), ('surname_minus_initial', dd, len(ks) + len(ki)),
                    ('surname_minus_initial_paired', ep[:3], ep[3])):
        prim.append(dict(version=ver, quantity=q, est=v[0], lo=v[1], hi=v[2], n=n))
P = pd.DataFrame(prim); P.to_csv(OUT / 'c3_primary_L40.csv', index=False)

# ---------------- HARD CHECK
pub = pd.read_csv(R13 / 'summary_alltok/primary_L40.csv').set_index('quantity')
pe = P[P.version == 'excl_false0_reuse'].set_index('quantity')
hc = {}
for q in ['surname_first', 'initial', 'surname_minus_initial', 'surname_minus_initial_paired']:
    hc[q] = dict(new=[pe.loc[q, c] for c in ('est', 'lo', 'hi')], published=[float(pub.loc[q, c]) for c in ('est', 'lo', 'hi')],
                 max_abs_diff=float(max(abs(pe.loc[q, c] - pub.loc[q, c]) for c in ('est', 'lo', 'hi'))))
ok = all(hc[q]['max_abs_diff'] <= 1e-6 for q in ('surname_first', 'initial'))
ok_round = round(pe.loc['surname_first', 'est'], 3) == 0.071 and round(pe.loc['initial', 'est'], 3) == 0.044
HC = dict(status='PASS' if (ok and ok_round) else 'FAIL', rule='excl column L40 surname_first and initial est/lo/hi == summary_alltok/primary_L40.csv within 1e-6; rounded +0.071 / +0.044',
          detail=hc)
(OUT / 'c3_hardcheck.json').write_text(json.dumps(HC, indent=1))
print('HARD CHECK', HC['status'], flush=True)
if HC['status'] != 'PASS':
    REP.write_text(f'# C-3: HARD CHECK FAILED\n\n```\n{json.dumps(HC, indent=1)}\n```\n'); sys.exit(2)

# ---------------- also full table cross-check vs alltok_role_layer.csv (excl version, all runs except e4b_parity)
xc = []
pub_t = pd.read_csv(R13 / 'summary_alltok/alltok_role_layer.csv')
for _, x in T[T.version == 'excl_false0_reuse'].iterrows():
    m = pub_t[(pub_t.run == x.run) & (pub_t.layer == x.layer)]
    if len(m): xc.append(dict(run=x.run, layer=x.layer, d_spec=abs(x.spec - m.spec.iloc[0]), d_lo=abs(x.lo - m.spec_lo.iloc[0]), d_tc=abs(x.tc_diff - m.tc_diff.iloc[0])))
XC = pd.DataFrame(xc)
# E4b parity no-exclusion vs summary_cpu_trainstd (group / none), target+control mean
ref = pd.read_parquet(R13 / 'summary_cpu_trainstd/perpaper_probe_spec.parquet')
ref = ref[(ref.split == 'group') & (ref.source == 'E4b')].join(META[['group_tight']], on='paper_id')
ref = ref[ref.group_tight.isin(['target', 'control'])]
e4 = []
for l in layers:
    if 'e4b_parity' not in runs: break
    r_none = ref[(ref.layer == l) & (ref.excl == 'none')]; r_tr = ref[(ref.layer == l) & (ref.excl == 'title-reuse') & ~ref.dropped]
    s = T[(T.run == 'e4b_parity') & (T.layer == l)].set_index('version')
    e4.append(dict(layer=l, trainstd_none_mean=r_none.spec.mean(), n_none=len(r_none), this_noexcl=s.loc['no_exclusion', 'spec'],
                   trainstd_reuse_mean=r_tr.spec.mean(), this_excl=s.loc['excl_false0_reuse', 'spec']))
E4 = pd.DataFrame(e4); E4.to_csv(OUT / 'c3_e4b_vs_trainstd.csv', index=False)

# ---------------- report
L = ['# C-3 (addendum 13): E4b and the all-token probe without the title-reuse exclusion', '',
     ('**TINY TEST** (L40, 3 runs).\n' if a.tiny else '') +
     'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...). Same probe predictions as addendum 9 (no refit); only the paper set changes. '
     'All papers = target + control. Title-specific = probe(true) - probe(false_0), mean log10(1/rank) over the role tokens. Team-cluster bootstrap 2,000 draws (archived team ids). '
     'Teacher-forced preference, not generation.', '',
     f'## Hard check: {HC["status"]}', '',
     f'- L40 surname_first (exclusion version): {f3(*hc["surname_first"]["new"])} vs published {f3(*hc["surname_first"]["published"])} (max |diff| {hc["surname_first"]["max_abs_diff"]:.1e}).',
     f'- L40 initial (exclusion version): {f3(*hc["initial"]["new"])} vs published {f3(*hc["initial"]["published"])} (max |diff| {hc["initial"]["max_abs_diff"]:.1e}).',
     f'- Whole exclusion table vs `summary_alltok/alltok_role_layer.csv`: max |diff| spec {XC.d_spec.max():.1e}, CI {XC.d_lo.max():.1e}, target-control {XC.d_tc.max():.1e} ({len(XC)} cells).' if len(XC) else '', '',
     '## Primary contrasts at L40', '', '| quantity | with false_0 title-reuse exclusion | no exclusion |', '|---|---|---|']
for q in ['surname_first', 'initial', 'surname_minus_initial', 'surname_minus_initial_paired']:
    s = P[P.quantity == q].set_index('version')
    L.append(f'| {q} | {f3(*s.loc["excl_false0_reuse", ["est", "lo", "hi"]])} (n {int(s.loc["excl_false0_reuse", "n"])}) | {f3(*s.loc["no_exclusion", ["est", "lo", "hi"]])} (n {int(s.loc["no_exclusion", "n"])}) |')
L += ['', '## Per run and layer', '', '| run | layer | all papers, excl [team CI] (n) | all papers, no excl [team CI] (n) | target - control within bin, excl | target - control, no excl |', '|---|---|---|---|---|---|']
for (run, l), s in T.groupby(['run', 'layer'], sort=False):
    s = s.set_index('version'); x, y = s.loc['excl_false0_reuse'], s.loc['no_exclusion']
    L.append(f'| {run} | L{l} | {f3(x.spec, x.lo, x.hi)} ({int(x.n_tc)}) | {f3(y.spec, y.lo, y.hi)} ({int(y.n_tc)}) | {f3(x.tc_diff, x.tc_lo, x.tc_hi)} ({int(x.tc_bins)}) | {f3(y.tc_diff, y.tc_lo, y.tc_hi)} ({int(y.tc_bins)}) |')
if len(E4):
    L += ['', '## E4b cross-check (WARN only): parity run vs the published trainstd per-paper file (team folds), target + control means', '',
          '| layer | trainstd excl=none | this, no excl | trainstd title-reuse kept | this, excl |', '|---|---|---|---|---|']
    for _, x in E4.iterrows():
        L.append(f'| L{int(x.layer)} | {x.trainstd_none_mean:+.4f} (n {int(x.n_none)}) | {x.this_noexcl:+.4f} | {x.trainstd_reuse_mean:+.4f} | {x.this_excl:+.4f} |')
    L += ['', 'Note: in summary_cpu_trainstd, excl = none is a separately fitted config (no paper dropped at any step); here the probe is the exclusion-config fit and only the scored paper set changes. Small differences are expected.']
L += ['', 'Sign-change / CI-change flags (no exclusion vs exclusion, all-paper signal and target - control):', '']
fl = []
for (run, l), s in T.groupby(['run', 'layer'], sort=False):
    s = s.set_index('version'); x, y = s.loc['excl_false0_reuse'], s.loc['no_exclusion']
    for nm, a1, b1, a2, b2 in (('all-paper', x.lo, x.hi, y.lo, y.hi), ('target-control', x.tc_lo, x.tc_hi, y.tc_lo, y.tc_hi)):
        c1 = 'pos' if a1 > 0 else ('neg' if b1 < 0 else 'n.s.'); c2 = 'pos' if a2 > 0 else ('neg' if b2 < 0 else 'n.s.')
        if c1 != c2: fl.append(f'- {run} L{l} {nm}: excl {c1} -> no excl {c2}')
L += fl if fl else ['- none']
REP.write_text('\n'.join(L) + '\n'); print('wrote', REP)
