"""Addendum 13 item C-3b (batch 2, group C; CPU): the C-3 sensitivity (no title-reuse exclusion) for the FIVE-false-title
version of E4b / the addendum-9 all-token probe (addendum 10 item 4, batch-1 item E4b5).

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-3b": "after addendum 10 item 4
finishes: the per-donor (deviation D1) and V5x0 versions without any exclusion."
Input  per-paper outputs of addendum 10 item 4: 381_stage13/summary_b1_e4b5/probe/perpaper_<run>_L<l>.parquet (nothing refitted;
       the probe predictions are the same, only the scored paper set / the false titles averaged change).
Versions (target + control papers; team-cluster bootstrap 2,000 draws; estimators and seeds copied verbatim from
       stage13_b1_e4b5_perdonor.py, which wrote the published numbers):
   with exclusion (published, = hard check):  Vpd (per-donor, D1), V5x0 (five-title mean, false_0-only exclusion), V0 (E4b rule)
   without any exclusion (new):              Vpd_noexcl (per-donor with every false title usable = mean of all 5),
                                             V5x0_noexcl (five-title mean, every paper), V0_noexcl (true - false_0, every paper)
   NOTE: without exclusion Vpd and V5x0 are the same quantity (mean of all 5 false titles over all papers); both are computed
   through their own code path and their agreement is checked (WARN if max |diff| > 1e-9).
Primary L40 contrasts (addendum 9): surname_first, initial, surname - initial (unpaired, joint team draw, seed 4) and paired (seed 6).
HARD CHECK: the exclusion versions reproduce summary_b1_e4b5/perdonor_by_run_layer.csv for every run x layer x version x
       column (|diff| <= 1e-9); exits 2 and writes no result report if not.
Other checks (WARN, value + threshold): V0_noexcl vs C-3 (summary_c13/c3/c3_role_layer.csv, no_exclusion; that table uses the
       addendum-9 probe outputs, which differ per paper by up to 6.7e-2 from the e4b5 refit, so only a WARN at |diff| > 0.005).
Output summary_c13/c3b/{c3b_role_layer.csv, c3b_primary_L40.csv, c3b_hardcheck.csv}; report reports/c13_C3b.md (only).
Usage  stage13_b2_c3b.py [--tiny] [--selftest]
       --tiny: layer 40, runs surname_first / initial / e4b_parity, output summary_c13/c3b_tiny (report inside it)
       --selftest: unit test of the hard-check comparator (identical -> PASS, perturbed -> FAIL), no data written
"""
import argparse, importlib.util, json, hashlib, sys, traceback
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum13.json'; PLAN_SHA = 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e'
PR = R13 / 'summary_b1_e4b5/probe'; PUB = R13 / 'summary_b1_e4b5/perdonor_by_run_layer.csv'
NB = 2000; KS = [0, 1, 2, 3, 4]; TOL = 1e-9
RUNS = ['e4b_parity', 'first_alltok', 'initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']
VALCOLS = ['spec', 'lo', 'hi', 'n', 'tc', 'tc_lo', 'tc_hi', 'tc_bins', 'ctrl_any', 'ctrl_any_lo', 'ctrl_any_hi', 'ctrl_field', 'ctrl_field_lo', 'ctrl_field_hi']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load(H / '13_stage13/b2c_columns.py', 'b2c_columns')
WARN = []


def warn(msg):
    WARN.append(msg)
    try: print('WARN', msg, flush=True)
    except Exception: pass


def hardcheck(new, pub, tol=TOL):
    """new/pub: DataFrames with run, layer, version + VALCOLS. Returns (status, rows). Missing rows/cells count as FAIL."""
    rows, ok = [], True
    key = ['run', 'layer', 'version']
    m = pub.merge(new, on=key, how='left', suffixes=('_pub', '_new'), indicator=True)
    if (m._merge != 'both').any(): ok = False
    for _, r in m.iterrows():
        for c in VALCOLS:
            a, b = r.get(f'{c}_new', np.nan), r[f'{c}_pub']
            both_nan = pd.isna(a) and pd.isna(b)
            d = 0.0 if both_nan else (abs(float(a) - float(b)) if not (pd.isna(a) or pd.isna(b)) else np.inf)
            if d > tol: ok = False
            rows.append(dict(run=r.run, layer=int(r.layer), version=r.version, column=c, new=a, published=b, abs_diff=d))
    return ('PASS' if ok else 'FAIL'), pd.DataFrame(rows, columns=COLS.C3B_HARDCHECK)


def selftest():
    pub = pd.read_csv(PUB)
    pub = pub[pub.version.isin(['Vpd', 'V5x0', 'V0'])].head(30).reset_index(drop=True)
    s1, _ = hardcheck(pub.copy(), pub)
    pert = pub.copy(); pert.loc[3, 'spec'] += 1e-4
    s2, _ = hardcheck(pert, pub)
    miss = pub.drop(index=5)
    s3, _ = hardcheck(miss, pub)
    ok = (s1, s2, s3) == ('PASS', 'FAIL', 'FAIL')
    print(f'SELFTEST identical -> {s1}; perturbed spec +1e-4 -> {s2}; missing row -> {s3}: {"OK" if ok else "BROKEN"}', flush=True)
    sys.exit(0 if ok else 1)


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); ap.add_argument('--selftest', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
if a.selftest: selftest()
OUT = R13 / ('summary_c13/c3b_tiny' if a.tiny else 'summary_c13/c3b'); OUT.mkdir(parents=True, exist_ok=True)
REP = OUT / 'c13_C3b.md' if a.tiny else R13 / 'reports/c13_C3b.md'
runs = ['surname_first', 'initial', 'e4b_parity'] if a.tiny else RUNS

c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')


# ---------------- estimators: verbatim copies from stage13_b1_e4b5_perdonor.py
def team_weights(pids, seed):
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    return np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)[:, codes]


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


def perdonor(d, all_usable=False):
    """stage13_b1_e4b5_perdonor.perdonor; all_usable=True treats every false title as usable (no exclusion)."""
    use = np.stack([np.ones(len(d), bool) if all_usable else ~d[f'dropped_{k}'].to_numpy(bool) for k in KS], 1).astype(float)
    nuse = use.sum(1); safe = np.where(nuse > 0, nuse, np.nan)
    sk = np.stack([d[f'spec_k{k}'].to_numpy(float) for k in KS], 1)
    d['n_used'] = nuse; d['spec_pd'] = np.nansum(sk * use, 1) / safe
    for c in ('any', 'field'):
        ck = np.stack([d[f'ctrl_{c}_k{k}'].to_numpy(float) for k in KS], 1) if f'ctrl_{c}_k0' in d else np.full_like(sk, np.nan)
        d[f'ctrl_{c}_pd'] = np.nansum(ck * use, 1) / safe
    return d


def f3(v, lo, hi):
    return '-' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')


def versions(f):
    """(version, paper subset, spec col, ctrl any col, ctrl field col) for one perpaper file."""
    d0 = pd.read_parquet(f).join(META, on='paper_id'); tc = d0.group_tight.isin(['target', 'control'])
    d = perdonor(d0.copy()); dn = perdonor(d0.copy(), all_usable=True)
    return d, dn, tc, [('Vpd', d[tc & (d.n_used >= 1)], 'spec_pd', 'ctrl_any_pd', 'ctrl_field_pd'),
                       ('V5x0', d[tc & ~d.drop0], 'spec5', 'ctrl_any5', 'ctrl_field5'),
                       ('V0', d[tc & ~d.drop0], 'spec0', 'ctrl_any0', 'ctrl_field0'),
                       ('Vpd_noexcl', dn[tc], 'spec_pd', 'ctrl_any_pd', 'ctrl_field_pd'),
                       ('V5x0_noexcl', d[tc], 'spec5', 'ctrl_any5', 'ctrl_field5'),
                       ('V0_noexcl', d[tc], 'spec0', 'ctrl_any0', 'ctrl_field0')]


rows, layers_seen = [], set()
layers = [40] if a.tiny else sorted({int(f.stem.rsplit('_L', 1)[1]) for f in PR.glob('perpaper_*_L*.parquet')})
for run in runs:
    for l in layers:
        f = PR / f'perpaper_{run}_L{l}.parquet'
        if not f.exists(): warn(f'missing {f.name}'); continue
        layers_seen.add(l)
        d, dn, tc, V = versions(f)
        dpd = np.nanmax(np.abs(dn[tc].spec_pd.to_numpy() - d[tc].spec5.to_numpy()))
        if not dpd <= 1e-9: warn(f'{run} L{l}: Vpd_noexcl vs V5x0_noexcl per-paper max |diff| {dpd:.2e} (threshold 1e-9)')
        for v, sub, col, ca, cf in V:
            m, lo, hi, n = mean_cluster(sub.paper_id.to_numpy(), sub[col].to_numpy())
            t, tlo, thi, nb = strat_cluster(sub.reset_index(drop=True), col, 'group_tight', 'target', 'control', 'citation_bin')
            ma = mean_cluster(sub.paper_id.to_numpy(), sub[ca].to_numpy()); mf = mean_cluster(sub.paper_id.to_numpy(), sub[cf].to_numpy())
            rows.append(dict(run=run, layer=l, version=v, spec=m, lo=lo, hi=hi, n=n, tc=t, tc_lo=tlo, tc_hi=thi, tc_bins=nb,
                             ctrl_any=ma[0], ctrl_any_lo=ma[1], ctrl_any_hi=ma[2], ctrl_field=mf[0], ctrl_field_lo=mf[1], ctrl_field_hi=mf[2]))
        try: print(run, f'L{l}', 'done', flush=True)
        except Exception: pass
T = COLS.check(pd.DataFrame(rows)[COLS.C3B_ROLE_LAYER], 'C3B_ROLE_LAYER'); T.to_csv(OUT / 'c3b_role_layer.csv', index=False)

# ---------------- HARD CHECK: exclusion versions == published perdonor_by_run_layer.csv
pub = pd.read_csv(PUB); pub = pub[pub.run.isin(runs) & pub.layer.isin(layers_seen)]
status, HC = hardcheck(T[T.version.isin(['Vpd', 'V5x0', 'V0'])], pub)
HC.to_csv(OUT / 'c3b_hardcheck.csv', index=False)
print('HARD CHECK', status, f'({len(pub)} published rows, {len(HC)} cells, max |diff| {HC.abs_diff.max():.2e}, tolerance {TOL})', flush=True)
if status != 'PASS':
    (OUT / 'HARD_CHECK_FAILED').write_text(json.dumps(dict(max_abs_diff=float(HC.abs_diff.max()), tol=TOL)))
    sys.exit(2)

# ---------------- primary L40 contrasts for every version
prim = []
if 40 in layers_seen and {'surname_first', 'initial'} <= set(runs):
    _, _, _, VS = versions(PR / 'perpaper_surname_first_L40.parquet'); _, _, _, VI = versions(PR / 'perpaper_initial_L40.parquet')
    for (v, ks, col, _, _), (v2, ki, col2, _, _) in zip(VS, VI):
        ks = ks.dropna(subset=[col]); ki = ki.dropna(subset=[col2])
        e = mean_cluster(ks.paper_id.to_numpy(), ks[col].to_numpy()); e2 = mean_cluster(ki.paper_id.to_numpy(), ki[col2].to_numpy())
        allp = np.concatenate([ks.paper_id.to_numpy(), ki.paper_id.to_numpy()]); W = team_weights(allp, 4); W1, W2 = W[:, :len(ks)], W[:, len(ks):]
        x1, x2 = ks[col].to_numpy(float), ki[col2].to_numpy(float)
        bt = (W1 @ x1) / np.maximum(W1.sum(1), 1e-9) - (W2 @ x2) / np.maximum(W2.sum(1), 1e-9); lo, hi = np.percentile(bt, [2.5, 97.5])
        pp = ks[['paper_id', col]].merge(ki[['paper_id', col2]], on='paper_id', suffixes=('_s', '_i')).dropna()
        cs, ci = (col + '_s', col2 + '_i') if col == col2 else (col, col2)
        ep = mean_cluster(pp.paper_id.to_numpy(), (pp[cs] - pp[ci]).to_numpy(), seed=6)
        for q, val, n in (('surname_first', e[:3], e[3]), ('initial', e2[:3], e2[3]), ('surname_minus_initial', (x1.mean() - x2.mean(), lo, hi), len(ks) + len(ki)),
                          ('surname_minus_initial_paired', ep[:3], ep[3])):
            prim.append(dict(version=v, quantity=q, est=val[0], lo=val[1], hi=val[2], n=n))
P = COLS.check(pd.DataFrame(prim, columns=COLS.C3B_PRIMARY), 'C3B_PRIMARY'); P.to_csv(OUT / 'c3b_primary_L40.csv', index=False)
# published primary (V5x0 / V0 with exclusion) cross-check, WARN only (the e4b5 report script used its own estimator calls)
try:
    pp_ = pd.read_csv(R13 / 'summary_b1_e4b5/primary_L40.csv')
    for v in ('V5x0', 'V0'):
        for q in ('surname_first', 'initial'):
            x = P[(P.version == v) & (P.quantity == q)]; y = pp_[(pp_.version == v) & (pp_.quantity == q)]
            if len(x) and len(y):
                dd = float(max(abs(x[c].iloc[0] - y[c].iloc[0]) for c in ('est', 'lo', 'hi')))
                if dd > 1e-6: warn(f'primary L40 {v} {q}: max |diff| vs summary_b1_e4b5/primary_L40.csv {dd:.2e} (threshold 1e-6)')
except Exception as e:
    warn(f'primary cross-check not run: {e!r}')
# V0_noexcl vs C-3 no_exclusion (different probe outputs: addendum 9 vs e4b5 refit) -> WARN only
try:
    c3 = pd.read_csv(R13 / 'summary_c13/c3/c3_role_layer.csv'); c3 = c3[c3.version == 'no_exclusion']
    for _, x in T[T.version == 'V0_noexcl'].iterrows():
        y = c3[(c3.run == x.run) & (c3.layer == x.layer)]
        if len(y) and abs(x.spec - y.spec.iloc[0]) > 0.005: warn(f'{x.run} L{x.layer}: V0_noexcl {x.spec:+.4f} vs C-3 no_exclusion {y.spec.iloc[0]:+.4f} (|diff| > 0.005)')
except Exception as e:
    warn(f'C-3 cross-check not run: {e!r}')

# ---------------- report (errors here are WARN only)
try:
    lay = sorted(layers_seen)
    L = ['# C-3b (addendum 13): five-false-title E4b / all-token probe without any title-reuse exclusion', '',
         ('**TINY TEST** (L40, 3 runs).\n\n' if a.tiny else '') +
         'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...), item C-3b. Script `13_stage13/stage13_b2_c3b.py`. Input: the addendum 10 item 4 per-paper '
         'probe outputs (`summary_b1_e4b5/probe/`), nothing refitted. All papers = target + control; team-cluster bootstrap 2,000 draws (archived team ids); '
         'estimators and seeds copied from `stage13_b1_e4b5_perdonor.py`; * = CI excludes 0. Teacher-forced preference, not generation.', '',
         '**What "no exclusion" means.** The probe is fitted on true-title residuals; a paper whose false-title donor is a training-fold paper can reuse that donor\'s '
         'true title. The published versions drop such papers (V5x0, V0) or such false titles (Vpd). Here every paper and every false title is kept, so these numbers '
         '**include that leakage** and are a sensitivity check, not a replacement of the published values. Without exclusion the per-donor version (Vpd_noexcl) '
         'and the five-title version (V5x0_noexcl) are the same quantity (true minus the mean of all five false titles); both were computed through their own code path '
         'and agree.', '',
         f'## Hard check: {status}', '',
         f'- Exclusion versions (Vpd, V5x0, V0) re-computed here vs published `summary_b1_e4b5/perdonor_by_run_layer.csv`: {len(pub)} rows x {len(VALCOLS)} columns, '
         f'max |diff| {HC.abs_diff.max():.1e} (tolerance {TOL:g}).', '',
         '## Checks (WARN = value and threshold; the run continued)', '', *(['- ' + w for w in WARN] or ['- No WARN.']), '',
         '## Primary contrasts at L40 (addendum 9 quantities)', '', '| quantity | ' + ' | '.join(v for v in ['Vpd', 'V5x0', 'V0', 'V5x0_noexcl', 'V0_noexcl']) + ' |', '|---' * 6 + '|']
    for q in ['surname_first', 'initial', 'surname_minus_initial', 'surname_minus_initial_paired']:
        s = P[P.quantity == q].set_index('version')
        if len(s): L.append(f'| {q} | ' + ' | '.join(f'{f3(*s.loc[v, ["est", "lo", "hi"]])} (n {int(s.loc[v, "n"])})' if v in s.index else '-' for v in ['Vpd', 'V5x0', 'V0', 'V5x0_noexcl', 'V0_noexcl']) + ' |')
    for v in ['V5x0_noexcl', 'V0_noexcl']:
        s = T[T.version == v]
        L += ['', f'## {v}: title-specific signal (all target + control papers)', '', '| run | ' + ' | '.join(f'L{x}' for x in lay) + ' |', '|---' * (len(lay) + 1) + '|']
        for run in runs:
            g = s[s.run == run].set_index('layer')
            if len(g): L.append(f'| {run} | ' + ' | '.join(f3(g.loc[x, 'spec'], g.loc[x, 'lo'], g.loc[x, 'hi']) if x in g.index else '' for x in lay) + ' |')
        L += ['', f'{v}: target - control within citation bin', '', '| run | ' + ' | '.join(f'L{x}' for x in lay) + ' |', '|---' * (len(lay) + 1) + '|']
        for run in runs:
            g = s[s.run == run].set_index('layer')
            if len(g): L.append(f'| {run} | ' + ' | '.join(f3(g.loc[x, 'tc'], g.loc[x, 'tc_lo'], g.loc[x, 'tc_hi']) if x in g.index else '' for x in lay) + ' |')
        L += ['', f'{v}: permutation controls at L40 (random other paper / same field)', '']
        for run in runs:
            g = s[(s.run == run) & (s.layer == 40)]
            if len(g): r = g.iloc[0]; L.append(f'- {run}: any {f3(r.ctrl_any, r.ctrl_any_lo, r.ctrl_any_hi)}; field {f3(r.ctrl_field, r.ctrl_field_lo, r.ctrl_field_hi)}')
    L += ['', '## Side by side per run (L40): n and signal', '', '| run | Vpd | V5x0 | V0 | V5x0_noexcl (= Vpd_noexcl) | V0_noexcl |', '|---|---|---|---|---|---|']
    for run in runs:
        g = T[(T.run == run) & (T.layer == 40)].set_index('version')
        if len(g): L.append(f'| {run} | ' + ' | '.join(f'{f3(g.loc[v, "spec"], g.loc[v, "lo"], g.loc[v, "hi"])} (n {int(g.loc[v, "n"])})' for v in ['Vpd', 'V5x0', 'V0', 'V5x0_noexcl', 'V0_noexcl']) + ' |')
    L += ['', 'Sign / CI-call changes, no exclusion vs the published versions (all-paper signal and target - control):', '']
    fl = []
    call = lambda lo, hi: 'pos' if lo > 0 else ('neg' if hi < 0 else 'n.s.')
    for (run, l), s in T.groupby(['run', 'layer'], sort=False):
        s = s.set_index('version')
        for ref, new in (('Vpd', 'Vpd_noexcl'), ('V5x0', 'V5x0_noexcl'), ('V0', 'V0_noexcl')):
            x, y = s.loc[ref], s.loc[new]
            for nm, a1, b1, a2, b2 in (('all-paper', x.lo, x.hi, y.lo, y.hi), ('target-control', x.tc_lo, x.tc_hi, y.tc_lo, y.tc_hi)):
                if pd.isna(a1) or pd.isna(a2): continue
                if call(a1, b1) != call(a2, b2): fl.append(f'- {run} L{l} {nm}: {ref} {call(a1, b1)} -> {new} {call(a2, b2)}')
    L += fl if fl else ['- none']
    REP.write_text('\n'.join(L) + '\n'); print('wrote', REP, flush=True)
except Exception:
    warn('report writing failed: ' + traceback.format_exc().splitlines()[-1]); traceback.print_exc()
print('C-3b done; WARN count', len(WARN), flush=True)
