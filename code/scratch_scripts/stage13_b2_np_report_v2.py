"""Batch 2, addendum 11 part A: report v2 for the name-position probe, implementing deviation record D11-1
(381_stage13/config/prereg_addendum11_deviations.json, sha256-checked at run time; written 2026-11-08 00:13:52 EST, before any
probe or report result). The original stage13_b2_np_report.py is NOT changed (frozen-script rule); this file replaces it as
the final step.

Versions (D11-1):
  Vpd  (PRIMARY) per-donor exclusion: per paper, mean over the false titles whose donor is not a training-fold paper of the run
       (not dropped_k) of spec_k = true - false_k; papers with no usable false title dropped (stage13_b2_np_vpd.py).
  V0   true - false_0, false_0 title-reuse rule (clean single comparison) - identical to V0 of the original report.
  V5x0 mean of false_0..4, false_0-only paper rule - "含泄漏，仅敏感性" (contains leakage, sensitivity only) - identical to V5x0
       of the original report.
Unchanged (D11-1): positions, layers, ridge probe, folds, controls, lens comparison, primary H3 contrast (now on Vpd), hard checks.
Statistics: the original report's functions team_weights / mean_cluster / strat_cluster / f3 are taken from
stage13_b2_np_report.py by source (ast; that script runs at import, so it cannot be imported), same seeds.
Controls: the probe stores the per-paper controls only as ctrl_*0 (true - false_0) and ctrl_*5 (true - mean of 5); per-title
control scores are not stored, so the Vpd control row is ctrl_*5 on the Vpd-kept papers (stated in the report).
Lens: logit / public J-lens on the SAME kept papers and the SAME usable titles (Vpd: lens true - mean of usable false_k;
V0: lens spec0; V5x0: lens spec5).
Hard checks as the original (exit 3 if either is missing or failed).
Outputs: summary_b2_np/np_*_v2.csv, reports/b2_np_report_v2.md (tiny: root b2_np_tiny).

REVISION 2026-11-08 (before this report ever ran on real data; D11-1 version 2, config/prereg_addendum11_deviations_v2.json,
sha256 d6d802fd..., user option b): reads the v2 probe (summary_b2_np/probe_v2, stage13_b2_np_probe_v2.py), which stores the
per-false-title control scores; the Vpd control rows are now averaged over the SAME usable-title mask as the Vpd main result
(stage13_b2_np_vpd.perdonor_ctrl) instead of ctrl_*5; the report lists the per-paper count of titles entering the Vpd main result
and the Vpd control rows separately and checks they are identical (a further hard check, exit 3). Verifies both record versions.
--root / --probe-dir exist only for the 1-real-shard equality check (stage13_b2_np_v2_check.py); production uses neither.
"""
import argparse, ast, importlib.util, json, sys, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
DEV = R13 / 'config/prereg_addendum11_deviations.json'
DEV_SHA_LOCKED = '7685cfc52a361747028be9b6829a37778fa39dcb5de200bd60a375da23b449eb'
DEV2 = R13 / 'config/prereg_addendum11_deviations_v2.json'
DEV2_SHA_LOCKED = 'd6d802fd5a503f9e4387ff766fd08026095bb400f14c5523a3d03e266c1fdcc9'
ORIG = H / '13_stage13/stage13_b2_np_report.py'
NB = 2000
VERS = ['Vpd', 'V0', 'V5x0']
VLAB = {'Vpd': 'Vpd (primary, D11-1)', 'V0': 'V0 (true - false_0)', 'V5x0': 'V5x0 (含泄漏，仅敏感性 / contains leakage, sensitivity only)'}


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def orig_funcs(path, names, ns):
    """exec only the named top-level function definitions of the original report in namespace ns (no top-level code runs)."""
    tree = ast.parse(Path(path).read_text()); got = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if sorted(n.name for n in got) != sorted(names): raise SystemExit(f'original report functions missing: {names}')
    exec(compile(ast.Module(body=got, type_ignores=[]), str(path), 'exec'), ns); return ns


K = load(H / '13_stage13/stage13_b2A_cols_v2.py', 'b2A_cols_v2')
VP = load(H / '13_stage13/stage13_b2_np_vpd.py', 'b2np_vpd')
ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); ap.add_argument('--root'); ap.add_argument('--probe-dir', default=K.NP_PROBE_DIR_V2)
a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
DEV_SHA = hashlib.sha256(DEV.read_bytes()).hexdigest()
if DEV_SHA != open(str(DEV) + '.sha256').read().split()[0] or DEV_SHA != DEV_SHA_LOCKED: raise SystemExit('DEVIATION RECORD D11-1 CHANGED')
DEV2_SHA = hashlib.sha256(DEV2.read_bytes()).hexdigest()
if DEV2_SHA != open(str(DEV2) + '.sha256').read().split()[0] or DEV2_SHA != DEV2_SHA_LOCKED: raise SystemExit('DEVIATION RECORD D11-1 v2 CHANGED')
DEVJ = json.loads(DEV.read_text()); DEV2J = json.loads(DEV2.read_text())
ORIG_SHA = hashlib.sha256(ORIG.read_bytes()).hexdigest()
root = Path(a.root) if a.root else (R13 / 'b2_np_tiny' if a.tiny else R13)
OUT = root / 'summary_b2_np'; PR = OUT / a.probe_dir; REP = root / 'reports/b2_np_report_v2.md'; REP.parent.mkdir(parents=True, exist_ok=True)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'recall_level', 'mc_team_outcome_tight'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS))
r_, o_ = papers.recall_level, papers.mc_team_outcome_tight
papers['grp'] = np.select([(r_ == 'R0') & (o_ == 'strong'), (r_ == 'R0') & (o_ == 'fail'), (r_ == 'R1') & (o_ == 'strong'), (r_ == 'R1') & (o_ == 'fail'),
                           (r_ == 'R0') & (o_ == 'uncertain'), (r_ == 'R1') & (o_ == 'uncertain'), (r_ == 'R2') & (o_ == 'strong')], K.NP_GROUPS, 'other')
META = papers.set_index('paper_id')
NS = orig_funcs(ORIG, ['team_weights', 'mean_cluster', 'strat_cluster', 'f3'], dict(np=np, pd=pd, NB=NB, TEAM=TEAM))
mean_cluster, strat_cluster, f3 = NS['mean_cluster'], NS['strat_cluster'], NS['f3']
NAN_USABLE = {}


def get(run, l):
    f = PR / f'perpaper_{run}_L{l}.parquet'
    if not f.exists(): return None
    d = pd.read_parquet(f).join(META[['group_tight', 'citation_bin', 'grp']], on='paper_id'); d['tc'] = d.group_tight.isin(['target', 'control'])
    d, bad = VP.perdonor(d); NAN_USABLE[(run, l)] = bad; d = VP.perdonor_ctrl(d)
    d['keep_Vpd'] = d.n_used >= 1; d['keep_V0'] = ~d.drop0.astype(bool); d['keep_V5x0'] = d['keep_V0']
    return d


# version -> (score col, keep col, ctrl any, ctrl field)
VDEF = {'Vpd': ('spec_pd', 'keep_Vpd', 'ctrl_any_pd', 'ctrl_field_pd'), 'V0': ('spec0', 'keep_V0', 'ctrl_any0', 'ctrl_field0'),
        'V5x0': ('spec5', 'keep_V5x0', 'ctrl_any5', 'ctrl_field5')}

L = ['# Addendum 11 A: name-position probe (H3) and lens comparison — report v2 (deviation D11-1)', '',
     ('**TINY TEST (random 64-layer model, 2 shards, random vocabulary rows): numbers are meaningless; code path only.**\n' if a.tiny else '') +
     f'**Deviation D11-1** (`381_stage13/config/prereg_addendum11_deviations.json`, sha256 `{DEV_SHA}`, verified at run time; '
     f'written {DEVJ["written"]}, **before any probe or report result**: {DEVJ["state_when_written"]["note"]}; approved: {DEVJ["approved_by_user"]}). '
     'Primary analysis switched from the 5-donor title-reuse rule to **per-donor exclusion (Vpd)**: per paper, average only the false titles whose '
     'donor is not a paper of the run in another training fold; papers with no usable false title are dropped. Reason (record): the 5-donor rule keeps '
     '0 papers in E4b and its fallback V5x0 leaves about 79% of false_1..4 title-reuse-leaked. '
     f'Original plan `prereg_addendum11.json` (sha256 {PLAN_SHA[:8]}...) unchanged; original report `stage13_b2_np_report.py` (sha256 {ORIG_SHA[:8]}...) unchanged, '
     'its statistics functions are reused by source. '
     f'**D11-1 version 2** (`prereg_addendum11_deviations_v2.json`, sha256 `{DEV2_SHA}`, verified; written {DEV2J["written"]}, before any probe result; '
     f'{DEV2J["approved_by_user"]}): the Vpd control rows use the SAME usable false titles per paper as the Vpd main result (per-title control scores '
     'stored by probe v2); checked in section 2.', '',
     'Teacher-forced preference, not generation (addendum 4). Ridge from the layer-l residual at each name-token-predicting position to the model\'s own '
     'L63 state at the same position, trained on true-title rows, archived author-team folds, training-fold standardisation, alpha on fold 0; decoded within '
     'the 9,137 name token ids. All-paper = target + control papers; team-cluster bootstrap 2,000 draws; * = CI excludes 0.', '',
     'Versions: **Vpd** = per-donor (primary); **V0** = true - false_0, false_0 rule (clean single comparison); '
     '**V5x0** = mean of 5 false titles, false_0-only paper rule — **含泄漏，仅敏感性** (contains leakage, sensitivity only).', '',
     '_Stated in advance (plan): as l approaches 63 the probe approaches the identity map, so L52-L56 are expected to agree with the output; '
     'the H3 evidence is weighted on L32-L48._', '']

# ---------------------------------------------------------------- hard checks (as the original report)
hard_ok = True
ck = [json.loads(f.read_text()) for f in sorted((OUT / 'checks').glob('*.json'))]
L += ['## 1. Checks', '']
if ck:
    C = pd.DataFrame([{k: v for k, v in c.items() if k != 'H1'} | {f'H1_{k}': v for k, v in (c.get('H1') or {}).items()} for c in ck])
    for c, s in C.groupby('cond'):
        L.append(f'- {c}: {len(s)} shards, {int(s.n_rows.sum())} rows; logit-lens rank vs Stage 10 (WARN < 0.95): ' +
                 ', '.join(f'L{l} {np.nansum(s[f"R_match_L{l}"] * s.n_rows) / s.n_rows.sum():.4f}' for l in K.NP_LAYERS if f'R_match_L{l}' in s) +
                 f'; fp16 WARN shards {int((s.fp16_status != "OK").sum())}.')
    t = C[C.cond == 'true']
    n_true = len(t); n_pass = int((t.get('H1_status', pd.Series(dtype=str)) == 'PASS').sum())
    need = 2 if a.tiny else 72
    h1 = n_true >= need and n_pass == n_true
    L.append(f'- **HARD CHECK 1** (true-title L63 recomputed vs raw/allTok_L63, relative norm diff <= {K.NP_HARD1_TOL}): {n_pass}/{n_true} true shards PASS '
             f'(need {need}); max rel diff {t.get("H1_rel_max", pd.Series([np.nan])).max():.2e}, bit-exact share min {t.get("H1_bitexact_share", pd.Series([np.nan])).min():.3f} -> **{"PASS" if h1 else "FAIL"}**.')
    hard_ok &= h1
else:
    L.append('- **HARD CHECK 1**: no GPU check files -> FAIL'); hard_ok = False
h2f = OUT / 'hardcheck2.json'
if h2f.exists():
    h2 = json.loads(h2f.read_text()); bad = [p for p in h2['parts'] if p['status'] != 'PASS']
    worst = max((p.get('abs_diff', p.get('max_abs_diff', 0)) for p in h2['parts']), default=np.nan)
    L.append(f'- **HARD CHECK 2** (Stage 10 lens spec at L40 / L48 vs published values, |diff| <= {K.NP_HARD2_TOL}): {len(h2["parts"]) - len(bad)}/{len(h2["parts"])} parts PASS, '
             f'largest |diff| {worst:.2e}; per-paper max |diff| vs paper_title_contrasts {h2["perpaper_max_abs_diff"]:.2e} -> **{h2["status"]}**.')
    hard_ok &= h2['status'] == 'PASS'
else:
    L.append('- **HARD CHECK 2**: hardcheck2.json missing -> FAIL'); hard_ok = False
L.append('')

FIT = pd.DataFrame([json.loads(f.read_text()) for f in sorted(PR.glob('fit_*.json'))])
if FIT.empty: REP.write_text('\n'.join(L + ['No probe output.'])); print('\n'.join(L)); sys.exit(3)
layers = sorted(FIT.layer.unique()); runs = [r for r in K.NP_PRIMARY['run_order'] if r in set(FIT.run)]
LENS = pd.read_parquet(OUT / 'lens_perpaper.parquet') if (OUT / 'lens_perpaper.parquet').exists() else None
D = {(run, l): get(run, l) for run in runs for l in layers}

# ---------------------------------------------------------------- usable false titles per paper (D11-1)
urows = []
for run in runs:
    l = 40 if 40 in layers else layers[0]; d = D[(run, l)]
    if d is None: continue
    for g in ['target', 'control', 'target+control']:
        s = d[d.tc] if g == 'target+control' else d[d.group_tight == g]; kp = s[s.n_used >= 1]
        urows.append(dict(run=run, layer=l, group=g, n_papers=len(s), kept_Vpd=len(kp), kept_V0=int((~s.drop0.astype(bool)).sum()), kept_V5=int((~s.drop5.astype(bool)).sum()),
                          mean_used_all=float(s.n_used.mean()) if len(s) else np.nan, median_used_all=float(s.n_used.median()) if len(s) else np.nan,
                          mean_used_kept=float(kp.n_used.mean()) if len(kp) else np.nan, median_used_kept=float(kp.n_used.median()) if len(kp) else np.nan,
                          **{f'n_used_{i}': int((s.n_used == i).sum()) for i in range(6)},
                          **{f'usable_k{k}': int((~s[f'dropped_{k}'].astype(bool)).sum()) for k in K.KS}))
U = pd.DataFrame(urows); U.to_csv(OUT / 'np_usable_titles_v2.csv', index=False)
nanu = sum(NAN_USABLE.values())
L += ['## 2. Usable false titles per paper (D11-1; dropped_k depends on the run only, shown at L40)', '',
      'usable = the false_k donor is not a paper of this run in another training fold. Kept: Vpd = >= 1 usable; V0 / V5x0 = false_0 usable; '
      'V5 = all 5 usable (old primary, not used).', '',
      '| run | group | papers | kept Vpd | kept V0/V5x0 | kept V5 | papers with 0 / 1 / 2 / 3 / 4 / 5 usable | usable mean / median (all) | (kept) | usable false_0 / 1 / 2 / 3 / 4 |',
      '|---|---|---|---|---|---|---|---|---|---|']
for r in U.itertuples():
    L.append(f'| {r.run} | {r.group} | {r.n_papers} | {r.kept_Vpd} | {r.kept_V0} | {r.kept_V5} | ' + ' / '.join(str(getattr(r, f"n_used_{i}")) for i in range(6)) +
             f' | {r.mean_used_all:.2f} / {r.median_used_all:.1f} | {r.mean_used_kept:.2f} / {r.median_used_kept:.1f} | ' +
             ' / '.join(str(getattr(r, f"usable_k{k}")) for k in K.KS) + ' |')
L += ['', f'Usable (run, layer, paper, k) cells with a NaN probe score: {nanu} (left out of the per-paper mean; 0 = identical to the E4b nansum / n_used formula).', '']

# D11-1 v2: titles entering the Vpd main result vs the Vpd control rows, per paper, every (run, layer); must be identical
irows = []
for (run, l), d in D.items():
    if d is None: continue
    s = d[d.tc & d.keep_Vpd]
    for nm, col in (('main', 'n_eff_main'), ('ctrl_any', 'n_eff_ctrl_any'), ('ctrl_field', 'n_eff_ctrl_field')):
        irows.append(dict(run=run, layer=l, rows=nm, n_papers=len(s), mean=float(s[col].mean()) if len(s) else np.nan, median=float(s[col].median()) if len(s) else np.nan,
                          **{f'n_{i}': int((s[col] == i).sum()) for i in range(6)}))
    irows[-1]['identical'] = irows[-2]['identical'] = irows[-3]['identical'] = bool(len(s) and (s.n_eff_main == s.n_eff_ctrl_any).all() and (s.n_eff_main == s.n_eff_ctrl_field).all()
                                                                                     and (~s[[f'dropped_{k}' for k in K.KS]].astype(bool)).sum(1).eq(s.n_eff_main).all())
ID = pd.DataFrame(irows); ID.to_csv(OUT / 'np_vpd_title_identity_v2.csv', index=False)
id_ok = bool(len(ID) and ID.identical.all()); hard_ok &= id_ok
L += ['### False titles entering the Vpd main result vs the Vpd control rows (D11-1 v2; target + control, Vpd-kept papers)', '',
      '| run | layer | rows | papers | 0 / 1 / 2 / 3 / 4 / 5 titles | mean / median | identical per paper |', '|---|---|---|---|---|---|---|']
for r in ID.itertuples():
    if r.layer == (40 if 40 in layers else layers[0]):
        L.append(f'| {r.run} | L{r.layer} | {r.rows} | {r.n_papers} | ' + ' / '.join(str(getattr(r, f"n_{i}")) for i in range(6)) + f' | {r.mean:.2f} / {r.median:.1f} | {"yes" if r.identical else "**NO**"} |')
L += ['', f'All (run, layer) cells in np_vpd_title_identity_v2.csv (also equal to the usable-title count): **{"PASS" if id_ok else "FAIL"}** (hard check D11-1 v2).', '']

# ---------------------------------------------------------------- main table
rows, lrows = [], []
for run in runs:
    for l in layers:
        d = D[(run, l)]
        if d is None: continue
        ft = FIT[(FIT.run == run) & (FIT.layer == l)].iloc[0]
        use = VP.use_matrix(d)
        for v in VERS:
            sc, kc, ca, cf = VDEF[v]
            k = d[d.tc & d[kc]]
            e = mean_cluster(k.paper_id, k[sc]); tcd = strat_cluster(d[d[kc]], sc, 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
            eA = mean_cluster(k.paper_id, k[ca]); eF = mean_cluster(k.paper_id, k[cf])
            rows.append(dict(version=v, run=run, layer=l, n_tc=e[3], spec=e[0], lo=e[1], hi=e[2], tc_diff=tcd[0], tc_lo=tcd[1], tc_hi=tcd[2], tc_bins=tcd[3],
                             any_est=eA[0], any_lo=eA[1], any_hi=eA[2], field_est=eF[0], field_lo=eF[1], field_hi=eF[2],
                             alpha=ft.alpha, heldout_r2=ft.heldout_r2_true, ceiling=k.ceiling.mean()))
            if LENS is not None:
                for ro in K.NP_LENS_READOUTS:
                    x = LENS[(LENS.run == run) & (LENS.readout == ro) & (LENS.layer == l)].set_index('paper_id').reindex(d.paper_id)
                    if v == 'Vpd':
                        ls_all = VP.from_scores(x['true'].to_numpy(), np.stack([x[f'false_{kk}'].to_numpy(float) for kk in K.KS], 1), use)[0]
                    else:
                        ls_all = x['spec0' if v == 'V0' else 'spec5'].to_numpy(float)
                    dd = d[['paper_id', 'group_tight', 'citation_bin', 'tc', kc]].assign(ls=ls_all)
                    kk_ = dd[dd.tc & dd[kc]]
                    el = mean_cluster(kk_.paper_id.to_numpy(), kk_.ls.to_numpy(), seed=2)
                    tl = strat_cluster(dd[dd[kc]].drop(columns=['tc', kc]), 'ls', 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
                    lrows.append(dict(version=v, run=run, layer=l, readout=ro, n_tc=el[3], lens_spec=el[0], lens_lo=el[1], lens_hi=el[2],
                                      lens_tc_diff=tl[0], lens_tc_lo=tl[1], lens_tc_hi=tl[2], probe_spec=e[0], probe_lo=e[1], probe_hi=e[2]))
T = pd.DataFrame(rows)[K.NP_TABLE_COLS]; T.to_csv(OUT / 'np_role_layer_v2.csv', index=False)
LC = pd.DataFrame(lrows); LC.to_csv(OUT / 'np_lens_compare_v2.csv', index=False)
L += ['## 3. Probe title-specific signal (all-paper, kept papers) and target - control within bin', '']
for v in VERS:
    L += [f'### {VLAB[v]}', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in runs:
        s = T[(T.version == v) & (T.run == run)].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join(f3(s.loc[l, 'spec'], s.loc[l, 'lo'], s.loc[l, 'hi']) + f' (n={int(s.loc[l, "n_tc"])})' if l in s.index else '-' for l in layers) + ' |')
    L += ['', f'target - control within bin ({v}):', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in runs:
        s = T[(T.version == v) & (T.run == run)].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join(f3(s.loc[l, 'tc_diff'], s.loc[l, 'tc_lo'], s.loc[l, 'tc_hi']) if l in s.index else '-' for l in layers) + ' |')
    L.append('')
for v in VERS:
    L += [f'### Permutation controls (gold tokens of a random other paper: any field / same field), {VLAB[v]}' +
          (' — averaged over the same usable false titles per paper as the Vpd main result' if v == 'Vpd' else ''), '',
          '| run | layer | any | same field | heldout R2 | alpha | ceiling (target decoded) |', '|---|---|---|---|---|---|---|']
    for r in T[T.version == v].itertuples():
        L.append(f'| {r.run} | L{r.layer} | {f3(r.any_est, r.any_lo, r.any_hi)} | {f3(r.field_est, r.field_lo, r.field_hi)} | {r.heldout_r2:.3f} | {r.alpha} | {r.ceiling:+.3f} |')
    L.append('')

# ---------------------------------------------------------------- lens comparison + primary H3 contrast
prim = []
if len(LC):
    L += ['## 4. Lens comparison (same kept papers, tokens, layers and usable false titles)', '',
          'Stage 10 stored full-vocabulary ranks only: the lens ranks over the whole vocabulary, the probe within the 9,137 name tokens. '
          'The comparison is on the sign and CI of each signal, not on its size (plan). Lens per version: Vpd = lens true - mean of the usable false titles; '
          'V0 = lens spec0; V5x0 = lens spec5.', '']
    for v in VERS:
        L += [f'### {VLAB[v]}', '', '| run | layer | probe | logit lens | public J-lens | probe t-c | logit t-c | J-lens t-c |', '|---|---|---|---|---|---|---|---|']
        for run in runs:
            for l in layers:
                s = LC[(LC.version == v) & (LC.run == run) & (LC.layer == l)].set_index('readout'); t_ = T[(T.version == v) & (T.run == run) & (T.layer == l)]
                if s.empty or t_.empty: continue
                t_ = t_.iloc[0]; g = lambda ro, c: (s.loc[ro, c], s.loc[ro, c.replace('spec', 'lo').replace('tc_diff', 'tc_lo')], s.loc[ro, c.replace('spec', 'hi').replace('tc_diff', 'tc_hi')])
                L.append(f'| {run} | L{l} | {f3(t_.spec, t_.lo, t_.hi)} | {f3(*g("logit", "lens_spec"))} | {f3(*g("jlens_public", "lens_spec"))} | '
                         f'{f3(t_.tc_diff, t_.tc_lo, t_.tc_hi)} | {f3(*g("logit", "lens_tc_diff"))} | {f3(*g("jlens_public", "lens_tc_diff"))} |')
        L.append('')
    for v in VERS:
        for run in runs:
            for l in K.NP_PRIMARY['layers']:
                t_ = T[(T.version == v) & (T.run == run) & (T.layer == l)]
                if t_.empty: continue
                t_ = t_.iloc[0]
                for ro in K.NP_LENS_READOUTS:
                    s = LC[(LC.version == v) & (LC.run == run) & (LC.layer == l) & (LC.readout == ro)]
                    if s.empty: continue
                    s = s.iloc[0]; probe_pos = bool(t_.lo > 0); lens_incl0 = bool(s.lens_lo <= 0 <= s.lens_hi); lens_smaller = bool(s.lens_spec < t_.spec)
                    prim.append(dict(version=v, run=run, layer=l, readout=ro, probe=t_.spec, probe_lo=t_.lo, probe_hi=t_.hi, lens=s.lens_spec, lens_lo=s.lens_lo, lens_hi=s.lens_hi,
                                     probe_pos=probe_pos, lens_ci_includes_0=lens_incl0, lens_smaller=lens_smaller, h3_contrast_met=probe_pos and (lens_incl0 or lens_smaller)))
    PRIM = pd.DataFrame(prim); PRIM.to_csv(OUT / 'np_h3_primary_v2.csv', index=False)
    if len(PRIM):
        L += ['## 5. Primary H3 contrast (plan; evaluated on Vpd per D11-1, V0 / V5x0 beside): probe > 0 (team CI) and the lens CI includes 0 or the lens value is smaller; L40 and L48; surname_first first', '',
              '| version | run | layer | readout | probe | lens | probe > 0 | lens CI incl. 0 | lens smaller | contrast met |', '|---|---|---|---|---|---|---|---|---|---|']
        for r in PRIM.itertuples():
            L.append(f'| {r.version}{" (primary)" if r.version == "Vpd" else " (含泄漏，仅敏感性)" if r.version == "V5x0" else ""} | {r.run} | L{r.layer} | {r.readout} | '
                     f'{f3(r.probe, r.probe_lo, r.probe_hi)} | {f3(r.lens, r.lens_lo, r.lens_hi)} | '
                     f'{"yes" if r.probe_pos else "no"} | {"yes" if r.lens_ci_includes_0 else "no"} | {"yes" if r.lens_smaller else "no"} | **{"yes" if r.h3_contrast_met else "no"}** |')
        L += ['', '_"lens smaller" compares values on different rank scales (full vocabulary vs 9,137 name tokens); it is the plan\'s literal wording and is shown beside the CI criterion._', '']

# ---------------------------------------------------------------- group split on unwritten authors (addendum 7)
fl = B / '391_groups/data/author_flags.parquet'
if fl.exists():
    au = pd.read_parquet(fl)[['paper_id', 'author_index', 'written', 'consistent']]
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index']).merge(au, on=['paper_id', 'author_index'], how='left')
    grow = []
    for run in runs:
        for l in layers:
            f = PR / f'pertoken_{run}_L{l}.parquet'
            if not f.exists() or D[(run, l)] is None: continue
            pt = pd.read_parquet(f).merge(tk[['row_id', 'written', 'consistent']], on='row_id'); pt = pt[(pt.consistent == True) & (pt.written == False)]
            pt['false_mean5'] = pt[[f'nlr_false_{k}' for k in K.KS]].mean(1)
            pp = pt.groupby('paper_id')[['nlr_true', 'false_mean5'] + [f'nlr_false_{k}' for k in K.KS]].mean()
            d = D[(run, l)].set_index('paper_id'); pp = pp.join(d[['keep_Vpd', 'keep_V0'] + [f'dropped_{k}' for k in K.KS] + ['grp', 'group_tight', 'citation_bin']])
            pp['spec_V5x0'] = pp.nlr_true - pp.false_mean5
            pp['spec_V0'] = pp.nlr_true - pp.nlr_false_0
            pp['spec_Vpd'] = VP.from_scores(pp.nlr_true.to_numpy(), np.stack([pp[f'nlr_false_{k}'].to_numpy(float) for k in K.KS], 1),
                                            np.stack([~pp[f'dropped_{k}'].astype(bool).to_numpy() for k in K.KS], 1))[0]
            for v in VERS:
                kc = 'keep_V0' if v != 'Vpd' else 'keep_Vpd'
                q = pp[pp[kc].fillna(False).astype(bool)].reset_index()
                for g in K.NP_GROUPS:
                    s = q[q.grp == g]
                    if not len(s): continue
                    e = mean_cluster(s.paper_id, s[f'spec_{v}'], seed=7)
                    grow.append(dict(version=v, run=run, layer=l, group=g, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=e[3] < 30))
                for nm, ga, gb, mn in (('A-B', 'A', 'B', 30), ('C-A', 'C', 'A', 10)):
                    e = strat_cluster(q, f'spec_{v}', 'grp', ga, gb, 'citation_bin', min_n=mn, seed=8)
                    grow.append(dict(version=v, run=run, layer=l, group=nm, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=False))
    GS = pd.DataFrame(grow); GS.to_csv(OUT / 'np_groups_unwritten_v2.csv', index=False)
    if len(GS):
        PL = 40 if 40 in layers else layers[0]
        L += [f'## 6. By behaviour group, unwritten authors only (addendum 7), L{PL} (all layers and versions in np_groups_unwritten_v2.csv)', '',
              'n < 30: descriptive only. A-B within bin (>= 30 per group); C-A (>= 10).', '']
        for v in VERS:
            L += [f'### {VLAB[v]}', '', '| run | ' + ' | '.join(K.NP_GROUPS + ['A-B', 'C-A']) + ' |', '|---' * (len(K.NP_GROUPS) + 3) + '|']
            for run in runs:
                s = GS[(GS.version == v) & (GS.run == run) & (GS.layer == PL)].set_index('group')
                cell = lambda g: '-' if g not in s.index or np.isnan(s.loc[g, 'est']) else (f'{s.loc[g, "est"]:+.3f} (n={int(s.loc[g, "n"])}, descr.)' if s.loc[g, 'descriptive_only'] else f'{f3(s.loc[g, "est"], s.loc[g, "lo"], s.loc[g, "hi"])} (n={int(s.loc[g, "n"])})')
                L.append(f'| {run} | ' + ' | '.join(cell(g) for g in K.NP_GROUPS + ['A-B', 'C-A']) + ' |')
            L.append('')

L += [f'Hard checks overall: **{"PASS" if hard_ok else "FAIL"}**.']
REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)
sys.exit(0 if hard_ok else 3)
