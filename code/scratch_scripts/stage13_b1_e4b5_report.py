"""Addendum 10 item 4 (batch 1): report for stage13_b1_e4b5_probe.py.

Versions (each: all-paper = target + control papers, team-cluster bootstrap 2,000 draws on the archived team ids, as
stage13_alltok_report.py / stage13_alltok_controls_report.py; the estimators are re-implemented here line for line because
that report runs at import):
  V5    spec5 = probe(true) - mean_k probe(false_k), papers dropped under the 5-donor rule (PRIMARY)
  V5x0  spec5, title-reuse exclusion on false_0 only (user rule: reported side by side when V5 keeps < 1,000 target+control papers)
  V0    spec0 = probe(true) - probe(false_0), false_0 exclusion (= published E4b / addendum 9; reproduction check)
Hard check (plan): V0 e4b_parity L40 = +0.061 +- 0.005; GPU false_0 residuals rel. norm diff <= 0.05 (checks/*.json).
Outputs: summary_b1_e4b5/*.csv, reports/b1_e4b5_report.md (tiny: b1_tiny/...).
"""
import argparse, importlib.util, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum10.json'; PLAN_SHA = '8243a4edebcc4da00933c7647eb4e322b0e8831dbac632622e52a8316f9e7e05'
NB = 2000; KS = [0, 1, 2, 3, 4]
RUNS = ['e4b_parity', 'first_alltok', 'initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']
VERS = {'V5': ('spec5', 'drop5', 'ctrl_any5', 'ctrl_field5'), 'V5x0': ('spec5', 'drop0', 'ctrl_any5', 'ctrl_field5'), 'V0': ('spec0', 'drop0', 'ctrl_any0', 'ctrl_field0')}
VDESC = {'V5': 'true - mean of 5 false titles, 5-donor exclusion (primary)', 'V5x0': 'true - mean of 5 false titles, false_0-only exclusion',
         'V0': 'true - false_0, false_0 exclusion (published E4b / addendum 9)'}


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
root = R13 / 'b1_tiny' if a.tiny else R13
PR = root / 'summary_b1_e4b5/probe'; OUT = root / 'summary_b1_e4b5'; REP = root / 'reports/b1_e4b5_report.md'; REP.parent.mkdir(parents=True, exist_ok=True)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')


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


def diff_cluster(p1, x1, p2, x2, seed=4):
    if not len(p1) or not len(p2): return np.nan, np.nan, np.nan
    p1, p2 = np.asarray(p1), np.asarray(p2); allp = np.concatenate([p1, p2]); W = team_weights(allp, seed)
    W1, W2 = W[:, :len(p1)], W[:, len(p1):]
    bt = (W1 @ x1) / np.maximum(W1.sum(1), 1e-9) - (W2 @ x2) / np.maximum(W2.sum(1), 1e-9)
    return x1.mean() - x2.mean(), *np.percentile(bt, [2.5, 97.5])


def f3(v, lo, hi):
    return '-' if v is None or np.isnan(v) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')


def get(run, l):
    f = PR / f'perpaper_{run}_L{l}.parquet'
    if not f.exists(): return None
    d = pd.read_parquet(f).join(META[['group_tight', 'citation_bin']], on='paper_id'); d['tc'] = d.group_tight.isin(['target', 'control']); return d


FIT = pd.DataFrame([json.loads(f.read_text()) for f in sorted(PR.glob('fit_*.json'))])
layers = sorted(FIT.layer.unique()); runs = [r for r in RUNS if r in set(FIT.run)]
PL = 40 if 40 in layers else layers[0]
L = ['# Addendum 10 item 4: E4b and all-token role probes, title-specific signal against the mean of five false titles', '',
     ('**TINY TEST (random model, 2 shards): numbers are meaningless; code path only.**\n' if a.tiny else '') +
     'Teacher-forced preference, not generation (addendum 4). Plan: `381_stage13/config/prereg_addendum10.json` (sha256 8243a4ed...), item 4; '
     'probe definitions of addendum 9 unchanged (fit on true-title residuals, archived team folds, training-fold standardisation, alpha on fold 0). '
     'All-paper = target + control papers; team-cluster bootstrap 2,000 draws; * = CI excludes 0.', '',
     'Versions: ' + '; '.join(f'**{k}** = {v}' for k, v in VDESC.items()) + '.', '']

# ---------------------------------------------------------------- GPU checks
ck = [json.loads(f.read_text()) for f in sorted((OUT / 'checks').glob('*.json'))]
L += ['## 1. Checks', '']
if ck:
    C = pd.DataFrame(ck); C.to_csv(OUT / 'gpu_checks.csv', index=False)
    for c, s in C.groupby('cond'):
        line = f'- {c}: {len(s)} shards, {int(s.n_papers.sum())} papers; rank of first name token at ":" L63 vs Stage 11 final@63@colon: ' \
               f'{int((s.R_status == "OK").sum())}/{len(s)} shards OK'
        if 'R_match' in s: line += f', exact match {np.nansum(s.R_match * s.n_papers) / s.n_papers.sum():.4f}'
        if 'H_status' in s and s.H_status.notna().any():
            h = s[s.H_status.notna()]; g_ = lambda c: h[c].max() if c in h else np.nan
            line += (f'; HARD CHECK residuals vs stored Stage 11: {", ".join(h.H_status)} (rel. norm diff max {g_("H_rel_max"):.2e}; '
                     f'title max {g_("H_resid_title_rel_max"):.2e}, colon max {g_("H_resid_colon_rel_max"):.2e}; bit-exact share title '
                     f'{g_("H_resid_title_bitexact_share"):.3f}, colon {g_("H_resid_colon_bitexact_share"):.3f}; tolerance 0.05)')
        L.append(line + f'; non-finite {int(s.n_nonfinite.sum())}.')
L.append('')

# ---------------------------------------------------------------- main table
rows = []
for run in runs:
    for l in layers:
        d = get(run, l)
        if d is None: continue
        ft = FIT[(FIT.run == run) & (FIT.layer == l)].iloc[0]
        for v, (sc, dc, ca, cf) in VERS.items():
            k = d[d.tc & ~d[dc]]; ka = d[~d[dc]]
            e = mean_cluster(k.paper_id, k[sc]); e9 = mean_cluster(ka.paper_id, ka[sc], seed=5)
            tcd = strat_cluster(d[~d[dc]], sc, 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
            eA = mean_cluster(k.paper_id, k[ca]); eF = mean_cluster(k.paper_id, k[cf])
            rows.append(dict(version=v, run=run, layer=l, n_papers_fit=int(ft.n_papers), alpha=ft.alpha, heldout_r2=ft.heldout_r2_true,
                             n_tc=e[3], spec=e[0], lo=e[1], hi=e[2], all_est=e9[0], all_lo=e9[1], all_hi=e9[2], n_all=e9[3],
                             tc_diff=tcd[0], tc_lo=tcd[1], tc_hi=tcd[2], tc_bins=tcd[3],
                             any_est=eA[0], any_lo=eA[1], any_hi=eA[2], field_est=eF[0], field_lo=eF[1], field_hi=eF[2],
                             true=k['true'].mean(), false_level=k['false_mean5' if sc == 'spec5' else 'false_0'].mean()))
T = pd.DataFrame(rows); T.to_csv(OUT / 'b1_e4b5_role_layer.csv', index=False)

# ---------------------------------------------------------------- hard check + parity with the published runs
L += ['## 2. Reproduction of the published false_0 numbers (hard check: V0 e4b_parity L40 = +0.061 +- 0.005)', '']
hard = None
if 'e4b_parity' in runs:
    ref = pd.read_parquet(R13 / 'summary_cpu_trainstd/perpaper_probe_spec.parquet')
    ref = ref[(ref.split == 'group') & (ref.excl == 'title-reuse') & (ref.source == 'E4b')]
    v0 = T[(T.version == 'V0') & (T.run == 'e4b_parity')].set_index('layer')
    if PL in v0.index:
        val = v0.loc[PL, 'spec']; hard = bool((not a.tiny) and abs(val - 0.061) <= 0.005)
        L.append(f'- V0 e4b_parity L{PL}: {val:+.4f} (n = {int(v0.loc[PL, "n_tc"])}) -> {"PASS" if hard else ("tiny: n/a" if a.tiny else "FAIL")}.')
    L += ['', '| layer | V0 this code | published per-paper mean (trainstd, group / title-reuse) | max per-paper abs diff | drop flags agree |', '|---|---|---|---|---|']
    for l in layers:
        d = get('e4b_parity', l)
        if d is None or l not in v0.index: continue
        m = d.merge(ref[ref.layer == l][['paper_id', 'spec', 'dropped']], on='paper_id')
        kr = ref[(ref.layer == l) & ~ref.dropped]
        L.append(f'| L{l} | {v0.loc[l, "spec"]:+.4f} | {kr.spec.mean():+.4f} | {(m.spec0 - m.spec).abs().max():.2e} | {(m.drop0 == m.dropped).mean():.4f} |')
    L.append('')
par = []
for run in runs:
    for l in layers:
        d = get(run, l); f9 = R13 / f'summary_alltok/probe/perpaper_{run}_L{l}.parquet'; c9 = R13 / f'summary_alltok/controls/perpaper_{run}_L{l}.parquet'
        if d is None or a.tiny: continue
        x = d.set_index('paper_id'); row = dict(run=run, layer=l)
        if f9.exists():
            q = pd.read_parquet(f9).set_index('paper_id'); row['spec_maxdiff_vs_add9'] = float((x.spec0 - q.spec.reindex(x.index)).abs().max()); row['drop_agree'] = float((x.drop0 == q.dropped.reindex(x.index)).mean())
        if c9.exists():
            q = pd.read_parquet(c9).set_index('paper_id'); row['any_maxdiff'] = float((x.ctrl_any0 - q.spec_any.reindex(x.index)).abs().max()); row['field_maxdiff'] = float((x.ctrl_field0 - q.spec_field.reindex(x.index)).abs().max())
        par.append(row)
PAR = pd.DataFrame(par); PAR.to_csv(OUT / 'parity_vs_addendum9.csv', index=False)
if len(PAR):
    L += [f'- Parity of V0 with the addendum-9 outputs (summary_alltok/probe and /controls), all runs x layers: max per-paper |spec diff| '
          f'{PAR.spec_maxdiff_vs_add9.max():.2e}, title-reuse flags agree {PAR.drop_agree.min():.4f}; controls max |diff| any {PAR.get("any_maxdiff", pd.Series([np.nan])).max():.2e}, '
          f'field {PAR.get("field_maxdiff", pd.Series([np.nan])).max():.2e}.', '']

# ---------------------------------------------------------------- 5-donor sample size
nv = T[(T.layer == PL)].pivot(index='run', columns='version', values='n_tc')
L += [f'## 3. Title-reuse exclusion: target + control papers kept (L{PL})', '', '| run | V5 (5-donor rule) | V5x0 / V0 (false_0 rule) | fit papers |', '|---|---|---|---|']
for run in runs:
    if run in nv.index: L.append(f'| {run} | {int(nv.loc[run, "V5"])} | {int(nv.loc[run, "V0"])} | {int(T[(T.run == run) & (T.layer == PL)].n_papers_fit.iloc[0])} |')
need5x0 = bool((nv['V5'] < 1000).any())
L += ['', f'Rule: if V5 keeps fewer than 1,000 target + control papers, V5x0 is reported side by side -> {"YES, V5x0 required" if need5x0 else "not required (shown anyway)"}.', '']

# ---------------------------------------------------------------- per run tables
L += ['## 4. Title-specific signal by run and layer (all papers = target + control; team CI)', '']
for run in runs:
    s = T[T.run == run]
    nm = {'e4b_parity': 'E4b first token (Stage 11 target, 4,314-id vocabulary)', 'first_alltok': 'first token, all-token pipeline'}.get(run, run)
    L += [f'### {nm}', '', '| layer | V5 (n) | V5x0 | V0 | V5x0 all 9,108 | V0 all 9,108 | V5x0 target - control within bin (bins) | V0 target - control within bin |', '|---|---|---|---|---|---|---|---|']
    for l in layers:
        g = s[s.layer == l].set_index('version')
        if not len(g): continue
        L.append(f'| L{l} | {f3(g.loc["V5", "spec"], g.loc["V5", "lo"], g.loc["V5", "hi"])} ({int(g.loc["V5", "n_tc"])}) | {f3(g.loc["V5x0", "spec"], g.loc["V5x0", "lo"], g.loc["V5x0", "hi"])} | '
                 f'{f3(g.loc["V0", "spec"], g.loc["V0", "lo"], g.loc["V0", "hi"])} | {f3(g.loc["V5x0", "all_est"], g.loc["V5x0", "all_lo"], g.loc["V5x0", "all_hi"])} | '
                 f'{f3(g.loc["V0", "all_est"], g.loc["V0", "all_lo"], g.loc["V0", "all_hi"])} | {f3(g.loc["V5x0", "tc_diff"], g.loc["V5x0", "tc_lo"], g.loc["V5x0", "tc_hi"])} ({int(g.loc["V5x0", "tc_bins"])}) | '
                 f'{f3(g.loc["V0", "tc_diff"], g.loc["V0", "tc_lo"], g.loc["V0", "tc_hi"])} |')
    L.append('')
for v in ['V5x0', 'V0']:
    L += [f'### Summary matrix {v}: title-specific signal', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in runs:
        s = T[(T.run == run) & (T.version == v)].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join((f'{s.loc[l, "spec"]:+.3f}' + ('*' if s.loc[l, 'lo'] > 0 or s.loc[l, 'hi'] < 0 else '')) if l in s.index else '-' for l in layers) + ' |')
    L.append('')
L += ['### Summary matrix: V5x0 minus V0 (change from using five false titles instead of false_0)', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
for run in runs:
    a5 = T[(T.run == run) & (T.version == 'V5x0')].set_index('layer').spec; a0 = T[(T.run == run) & (T.version == 'V0')].set_index('layer').spec
    L.append(f'| {run} | ' + ' | '.join(f'{a5.loc[l] - a0.loc[l]:+.3f}' if l in a5.index else '-' for l in layers) + ' |')
L.append('')

# per false title at the primary layer (false_0 exclusion)
pk = []
for run in runs:
    d = get(run, PL)
    if d is None: continue
    k = d[d.tc & ~d.drop0]
    pk.append(dict(run=run, **{f'false_{j}': (k['true'] - k[f'false_{j}']).mean() for j in KS}, mean5=k.spec5.mean()))
PK = pd.DataFrame(pk); PK.to_csv(OUT / 'per_false_title_L40.csv', index=False)
L += [f'### Per false title at L{PL} (true - false_k, target + control, false_0 exclusion)', '', '| run | ' + ' | '.join(f'false_{j}' for j in KS) + ' | mean of 5 |', '|---' * 7 + '|']
for _, x in PK.iterrows(): L.append(f'| {x.run} | ' + ' | '.join(f'{x[f"false_{j}"]:+.3f}' for j in KS) + f' | {x.mean5:+.3f} |')
L.append('')

# ---------------------------------------------------------------- primary contrasts
L += [f'## 5. Addendum-9 primary contrasts at L{PL}', '']
prim = []
ds_, di_ = get('surname_first', PL), get('initial', PL)
if ds_ is not None and di_ is not None:
    L += ['| version | surname_first > 0 | initial | surname_first - initial (joint team draws) | paired within paper |', '|---|---|---|---|---|']
    for v, (sc, dc, _, _) in VERS.items():
        ks, ki = ds_[ds_.tc & ~ds_[dc]], di_[di_.tc & ~di_[dc]]
        e = mean_cluster(ks.paper_id, ks[sc]); e2 = mean_cluster(ki.paper_id, ki[sc])
        dd = diff_cluster(ks.paper_id.to_numpy(), ks[sc].to_numpy(float), ki.paper_id.to_numpy(), ki[sc].to_numpy(float))
        pp = ks[['paper_id', sc]].merge(ki[['paper_id', sc]], on='paper_id', suffixes=('_s', '_i')).dropna()
        ep = mean_cluster(pp.paper_id, pp[sc + '_s'] - pp[sc + '_i'], seed=6)
        prim += [dict(version=v, quantity=q, est=x[0], lo=x[1], hi=x[2], n=nn) for q, x, nn in
                 (('surname_first', e, e[3]), ('initial', e2, e2[3]), ('surname_minus_initial', dd, len(ks) + len(ki)), ('surname_minus_initial_paired', ep, ep[3]))]
        L.append(f'| {v} | {f3(*e[:3])} (n={e[3]}) | {f3(*e2[:3])} (n={e2[3]}) | {f3(*dd)} | {f3(*ep[:3])} (n={ep[3]}) |')
pd.DataFrame(prim).to_csv(OUT / 'primary_L40.csv', index=False)
L.append('')

# ---------------------------------------------------------------- controls
L += ['## 6. Permutation controls (gold tokens of a random other paper / of a random paper of the same field; rng 3712 as addendum 9)', '',
      'A paper-specific signal should vanish (~0).', '']
for v in ['V5x0', 'V0', 'V5']:
    for col, nm in (('any', 'random other paper'), ('field', 'random paper of the same field')):
        L += [f'### {v}, gold = {nm}', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
        for run in runs:
            s = T[(T.run == run) & (T.version == v)].set_index('layer')
            L.append(f'| {run} | ' + ' | '.join(f3(s.loc[l, f"{col}_est"], s.loc[l, f"{col}_lo"], s.loc[l, f"{col}_hi"]) if l in s.index else '-' for l in layers) + ' |')
        L.append('')
json.dump(dict(hard_check_e4b_L40=hard, need_v5x0=need5x0, tiny=a.tiny), open(OUT / 'status.json', 'w'))
REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L))
