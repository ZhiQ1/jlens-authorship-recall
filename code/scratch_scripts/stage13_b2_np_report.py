"""Batch 2, addendum 11 part A: report for the name-position probe (stage13_b2_np_probe.py) and the lens comparison
(stage13_b2_np_lens.py). CPU.

Plan (locked): 381_stage13/config/prereg_addendum11.json, part A. Teacher-forced preference, not generation (addendum 4).
Versions (as addendum 10 item 4): V5 = spec5 with the 5-donor title-reuse exclusion (primary); V5x0 = spec5 with the false_0-only
exclusion (reported beside V5 when V5 keeps < 1,000 target + control papers; always written to the csv); V0 = spec0 (true - false_0)
with the false_0 exclusion (descriptive bridge to addendum 9 / E4b).
Statistics (as stage13_b1_e4b5_report.py, re-implemented line for line because that report runs at import): all-paper =
target + control papers, team-cluster bootstrap 2,000 draws on the archived team ids; target - control within citation bin
(bins with >= 30 papers in both groups, weights n_t n_c / (n_t + n_c)); permutation controls; group split on unwritten authors
(addendum 7: consistent papers, authors not written in the open answer; n < 30 descriptive).
Lens comparison: Stage 10 logit lens / public J-lens spec5 at the same tokens and layers, on the SAME kept papers, side by side;
full-vocabulary ranks (lens) vs ranks within the 9,137 name tokens (probe): compared on sign and CI, not size.
Primary H3 contrast (plan): per run at L40 and L48, probe spec > 0 (team CI) while the lens spec at the same layer has a CI
including 0 or is smaller than the probe's; surname_first first. L52-L56 expected to agree with the output (stated in advance).
Hard checks: (1) GPU true-title L63 vs raw/allTok_L63 (summary_b2_np/checks/true_*.json, every true shard PASS);
(2) summary_b2_np/hardcheck2.json PASS. The report exits 3 if either is missing or failed.
Outputs: summary_b2_np/np_*.csv, reports/b2_np_report.md (tiny: b2_np_tiny/...).
"""
import argparse, importlib.util, json, sys, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols')
ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
root = R13 / 'b2_np_tiny' if a.tiny else R13
OUT = root / 'summary_b2_np'; PR = OUT / 'probe'; REP = root / 'reports/b2_np_report.md'; REP.parent.mkdir(parents=True, exist_ok=True)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'recall_level', 'mc_team_outcome_tight'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS))
r_, o_ = papers.recall_level, papers.mc_team_outcome_tight
papers['grp'] = np.select([(r_ == 'R0') & (o_ == 'strong'), (r_ == 'R0') & (o_ == 'fail'), (r_ == 'R1') & (o_ == 'strong'), (r_ == 'R1') & (o_ == 'fail'),
                           (r_ == 'R0') & (o_ == 'uncertain'), (r_ == 'R1') & (o_ == 'uncertain'), (r_ == 'R2') & (o_ == 'strong')], K.NP_GROUPS, 'other')
META = papers.set_index('paper_id')


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


def f3(v, lo, hi):
    return '-' if v is None or np.isnan(v) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')


def get(run, l):
    f = PR / f'perpaper_{run}_L{l}.parquet'
    if not f.exists(): return None
    d = pd.read_parquet(f).join(META[['group_tight', 'citation_bin', 'grp']], on='paper_id'); d['tc'] = d.group_tight.isin(['target', 'control']); return d


L = ['# Addendum 11 A: name-position probe (H3) and lens comparison', '',
     ('**TINY TEST (random 64-layer model, 2 shards, random vocabulary rows): numbers are meaningless; code path only.**\n' if a.tiny else '') +
     'Teacher-forced preference, not generation (addendum 4). Plan: `381_stage13/config/prereg_addendum11.json` (sha256 ' + PLAN_SHA[:8] + '...), part A. '
     'Ridge from the layer-l residual at each name-token-predicting position to the model\'s own L63 state at the same position, trained on true-title rows, '
     'archived author-team folds, training-fold standardisation, alpha on fold 0; decoded within the 9,137 name token ids. '
     'All-paper = target + control papers; team-cluster bootstrap 2,000 draws; * = CI excludes 0.', '',
     'Versions: **V5** = true - mean of 5 false titles, 5-donor title-reuse exclusion (primary); **V5x0** = same, false_0-only exclusion; '
     '**V0** = true - false_0, false_0 exclusion.', '',
     '_Stated in advance (plan): as l approaches 63 the probe approaches the identity map, so L52-L56 are expected to agree with the output; '
     'the H3 evidence is weighted on L32-L48._', '']

# ---------------------------------------------------------------- hard checks
hard_ok = True
ck = [json.loads(f.read_text()) for f in sorted((OUT / 'checks').glob('*.json'))]
L += ['## 1. Checks', '']
if ck:
    C = pd.DataFrame([{k: v for k, v in c.items() if k != 'H1'} | {f'H1_{k}': v for k, v in (c.get('H1') or {}).items()} for c in ck]); C.to_csv(OUT / 'np_gpu_checks.csv', index=False)
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

# ---------------------------------------------------------------- main table
FIT = pd.DataFrame([json.loads(f.read_text()) for f in sorted(PR.glob('fit_*.json'))])
if FIT.empty: REP.write_text('\n'.join(L + ['No probe output.'])); print('\n'.join(L)); sys.exit(3)
layers = sorted(FIT.layer.unique()); runs = [r for r in K.NP_PRIMARY['run_order'] if r in set(FIT.run)]
LENS = pd.read_parquet(OUT / 'lens_perpaper.parquet') if (OUT / 'lens_perpaper.parquet').exists() else None
rows, lrows = [], []
for run in runs:
    for l in layers:
        d = get(run, l)
        if d is None: continue
        ft = FIT[(FIT.run == run) & (FIT.layer == l)].iloc[0]
        for v, (sc, dc, ca, cf) in K.NP_VERSIONS.items():
            k = d[d.tc & ~d[dc]]
            e = mean_cluster(k.paper_id, k[sc]); tcd = strat_cluster(d[~d[dc]], sc, 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
            eA = mean_cluster(k.paper_id, k[ca]); eF = mean_cluster(k.paper_id, k[cf])
            rows.append(dict(version=v, run=run, layer=l, n_tc=e[3], spec=e[0], lo=e[1], hi=e[2], tc_diff=tcd[0], tc_lo=tcd[1], tc_hi=tcd[2], tc_bins=tcd[3],
                             any_est=eA[0], any_lo=eA[1], any_hi=eA[2], field_est=eF[0], field_lo=eF[1], field_hi=eF[2],
                             alpha=ft.alpha, heldout_r2=ft.heldout_r2_true, ceiling=k.ceiling.mean()))
            if LENS is not None:
                for ro in K.NP_LENS_READOUTS:
                    x = LENS[(LENS.run == run) & (LENS.readout == ro) & (LENS.layer == l)].set_index('paper_id')
                    s5 = x.spec5.reindex(k.paper_id)
                    el = mean_cluster(k.paper_id.to_numpy(), s5.to_numpy(), seed=2)
                    xx = d[~d[dc]][['paper_id', 'group_tight', 'citation_bin']].assign(ls=x.spec5.reindex(d[~d[dc]].paper_id).to_numpy())
                    tl = strat_cluster(xx, 'ls', 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
                    lrows.append(dict(version=v, run=run, layer=l, readout=ro, n_tc=el[3], lens_spec=el[0], lens_lo=el[1], lens_hi=el[2],
                                      lens_tc_diff=tl[0], lens_tc_lo=tl[1], lens_tc_hi=tl[2], probe_spec=e[0], probe_lo=e[1], probe_hi=e[2]))
T = pd.DataFrame(rows)[K.NP_TABLE_COLS]; T.to_csv(OUT / 'np_role_layer.csv', index=False)
LC = pd.DataFrame(lrows); LC.to_csv(OUT / 'np_lens_compare.csv', index=False)
nV5 = T[(T.version == 'V5')].n_tc.min() if len(T) else 0
show = ['V5'] + (['V5x0'] if nV5 < 1000 else [])
L += [f'## 2. Probe title-specific signal (all-paper, kept papers) and target - control within bin', '',
      f'V5 keeps at least {int(nV5)} target + control papers per cell' + (' (< 1,000: V5x0 shown beside it, plan rule).' if nV5 < 1000 else '.'), '']
for v in show + ['V0']:
    L += [f'### {v}', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in runs:
        s = T[(T.version == v) & (T.run == run)].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join(f3(s.loc[l, 'spec'], s.loc[l, 'lo'], s.loc[l, 'hi']) + f' (n={int(s.loc[l, "n_tc"])})' if l in s.index else '-' for l in layers) + ' |')
    L += ['', f'target - control within bin ({v}):', '', '| run | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in runs:
        s = T[(T.version == v) & (T.run == run)].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join(f3(s.loc[l, 'tc_diff'], s.loc[l, 'tc_lo'], s.loc[l, 'tc_hi']) if l in s.index else '-' for l in layers) + ' |')
    L.append('')
L += ['### Permutation controls (gold tokens of a random other paper: any field / same field), V5' + ('x0' if nV5 < 1000 else ''), '',
      '| run | layer | any | same field | heldout R2 | alpha | ceiling (target decoded) |', '|---|---|---|---|---|---|---|']
vv = 'V5x0' if nV5 < 1000 else 'V5'
for r in T[T.version == vv].itertuples():
    L.append(f'| {r.run} | L{r.layer} | {f3(r.any_est, r.any_lo, r.any_hi)} | {f3(r.field_est, r.field_lo, r.field_hi)} | {r.heldout_r2:.3f} | {r.alpha} | {r.ceiling:+.3f} |')
L.append('')

# ---------------------------------------------------------------- lens comparison + primary H3 contrast
prim = []
if len(LC):
    L += ['## 3. Lens comparison (same kept papers, tokens and layers)', '',
          'Stage 10 stored full-vocabulary ranks only: the lens ranks over the whole vocabulary, the probe within the 9,137 name tokens. '
          'The comparison is on the sign and CI of each signal, not on its size (plan).', '']
    for v in show:
        L += [f'### {v}', '', '| run | layer | probe | logit lens | public J-lens | probe t-c | logit t-c | J-lens t-c |', '|---|---|---|---|---|---|---|---|']
        for run in runs:
            for l in layers:
                s = LC[(LC.version == v) & (LC.run == run) & (LC.layer == l)].set_index('readout'); t_ = T[(T.version == v) & (T.run == run) & (T.layer == l)]
                if s.empty or t_.empty: continue
                t_ = t_.iloc[0]; g = lambda ro, c: (s.loc[ro, c], s.loc[ro, c.replace('spec', 'lo').replace('tc_diff', 'tc_lo')], s.loc[ro, c.replace('spec', 'hi').replace('tc_diff', 'tc_hi')])
                L.append(f'| {run} | L{l} | {f3(t_.spec, t_.lo, t_.hi)} | {f3(*g("logit", "lens_spec"))} | {f3(*g("jlens_public", "lens_spec"))} | '
                         f'{f3(t_.tc_diff, t_.tc_lo, t_.tc_hi)} | {f3(*g("logit", "lens_tc_diff"))} | {f3(*g("jlens_public", "lens_tc_diff"))} |')
        L.append('')
    for v in show:
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
    PRIM = pd.DataFrame(prim); PRIM.to_csv(OUT / 'np_h3_primary.csv', index=False)
    if len(PRIM):
        L += ['## 4. Primary H3 contrast (plan): probe > 0 (team CI) and the lens CI includes 0 or the lens value is smaller; L40 and L48; surname_first first', '',
              '| version | run | layer | readout | probe | lens | probe > 0 | lens CI incl. 0 | lens smaller | contrast met |', '|---|---|---|---|---|---|---|---|---|---|']
        for r in PRIM.itertuples():
            L.append(f'| {r.version} | {r.run} | L{r.layer} | {r.readout} | {f3(r.probe, r.probe_lo, r.probe_hi)} | {f3(r.lens, r.lens_lo, r.lens_hi)} | '
                     f'{"yes" if r.probe_pos else "no"} | {"yes" if r.lens_ci_includes_0 else "no"} | {"yes" if r.lens_smaller else "no"} | **{"yes" if r.h3_contrast_met else "no"}** |')
        L += ['', '_"lens smaller" compares values on different rank scales (full vocabulary vs 9,137 name tokens); it is the plan\'s literal wording and is shown beside the CI criterion._', '']

# ---------------------------------------------------------------- group split on unwritten authors (addendum 7)
fl = B / '391_groups/data/author_flags.parquet'
if fl.exists():
    au = pd.read_parquet(fl)[['paper_id', 'author_index', 'written', 'consistent']]
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index']).merge(au, on=['paper_id', 'author_index'], how='left')
    grow = []; dc = 'drop0' if vv == 'V5x0' else 'drop5'
    for run in runs:
        for l in layers:
            f = PR / f'pertoken_{run}_L{l}.parquet'
            if not f.exists(): continue
            pt = pd.read_parquet(f).merge(tk[['row_id', 'written', 'consistent']], on='row_id'); pt = pt[(pt.consistent == True) & (pt.written == False)]
            pt['false_mean5'] = pt[[f'nlr_false_{k}' for k in K.KS]].mean(1)
            pp = pt.groupby('paper_id')[['nlr_true', 'false_mean5']].mean(); pp['spec'] = pp.nlr_true - pp.false_mean5
            d = get(run, l).set_index('paper_id'); pp = pp.join(d[[dc, 'grp', 'group_tight', 'citation_bin']]); pp = pp[~pp[dc].astype(bool)].reset_index()
            for g in K.NP_GROUPS:
                s = pp[pp.grp == g]
                if not len(s): continue
                e = mean_cluster(s.paper_id, s.spec, seed=7)
                grow.append(dict(run=run, layer=l, group=g, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=e[3] < 30))
            for nm, ga, gb, mn in (('A-B', 'A', 'B', 30), ('C-A', 'C', 'A', 10)):
                e = strat_cluster(pp, 'spec', 'grp', ga, gb, 'citation_bin', min_n=mn, seed=8)
                grow.append(dict(run=run, layer=l, group=nm, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=False))
    GS = pd.DataFrame(grow); GS.to_csv(OUT / 'np_groups_unwritten.csv', index=False)
    if len(GS):
        PL = 40 if 40 in layers else layers[0]
        L += [f'## 5. By behaviour group, unwritten authors only (addendum 7; spec5, {vv} exclusion), L{PL} (all layers in np_groups_unwritten.csv)', '',
              'n < 30: descriptive only. A-B within bin (>= 30 per group); C-A (>= 10).', '', '| run | ' + ' | '.join(K.NP_GROUPS + ['A-B', 'C-A']) + ' |', '|---' * (len(K.NP_GROUPS) + 3) + '|']
        for run in runs:
            s = GS[(GS.run == run) & (GS.layer == PL)].set_index('group')
            cell = lambda g: '-' if g not in s.index or np.isnan(s.loc[g, 'est']) else (f'{s.loc[g, "est"]:+.3f} (n={int(s.loc[g, "n"])}, descr.)' if s.loc[g, 'descriptive_only'] else f'{f3(s.loc[g, "est"], s.loc[g, "lo"], s.loc[g, "hi"])} (n={int(s.loc[g, "n"])})')
            L.append(f'| {run} | ' + ' | '.join(cell(g) for g in K.NP_GROUPS + ['A-B', 'C-A']) + ' |')
        L.append('')

L += [f'Hard checks overall: **{"PASS" if hard_ok else "FAIL"}**.']
REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)
sys.exit(0 if hard_ok else 3)
