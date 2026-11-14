"""Plan 2026-11-14b item 2 (H3 same-scale comparison at the name positions) -- post hoc (strengthening 2), descriptive.
CPU analysis step (after stage13_h3_samescale_compute_20261114.py).

Per paper (surname_first rows of all authors, = the probe run 'surname_first'): mean nlr = log10(1/restricted rank) under the
true title and each false_k title, for logit lens and public J-lens (decoders b16 = Stage 10 unembed [main], f32 = probe decoder).
Vpd spec: true - mean over the USABLE false titles (not dropped_k; dropped_k read from the probe's
summary_b2_np/probe_v2/perpaper_surname_first_L<l>.parquet, i.e. exactly the probe's per-donor rule), papers with >= 1 usable
title; target + control papers = the published 4,654 (checked).
Statistics = the published report's functions (stage13_b2_np_report.py, taken by source as stage13_b2_np_report_v2.py does):
  spec   mean_cluster(seed=2) over target+control kept papers
  T - C  strat_cluster(seed=1) within citation bin (min 30 per cell), Stage 10 definition, on the kept papers
  team-cluster bootstrap 2,000 draws on the archived author teams. Because the weights depend only on the paper list and the
  seed, probe, lens and the per-paper difference probe - lens get the SAME draws; the difference CI = CI of the paired
  per-draw difference (the statistics are linear in the paper values).
Also: published full-vocab lens values (summary_b2_np/lens_perpaper.parquet, Stage 10 stored ranks) recomputed with the same
code (parity 3) and the published probe values.
Outputs: summary_h3_samescale_20261114/h3_samescale_table.csv, h3_samescale_paired.csv, parity_summary.json, report.md.
"""
import argparse, ast, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
OUT = R13 / 'summary_h3_samescale_20261114'; PR = R13 / 'summary_b2_np/probe_v2'
NB = 2000; KS = [0, 1, 2, 3, 4]; CONDS = ['true'] + [f'false_{k}' for k in KS]; RUN = 'surname_first'
LENSES = ['jlens_public', 'logit']; DECS = ['b16', 'f32']
LABEL = 'post hoc (strengthening 2), descriptive'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
sfx = '_tiny' if a.tiny else ''
VP = load(H / '13_stage13/stage13_b2_np_vpd.py', 'b2np_vpd'); c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')
src = (H / '13_stage13/stage13_b2_np_report.py').read_text(); tree = ast.parse(src); ns = dict(np=np, pd=pd, NB=NB, TEAM=TEAM)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('team_weights', 'mean_cluster', 'strat_cluster', 'f3')]
exec(compile(ast.Module(body=fn, type_ignores=[]), 'stage13_b2_np_report.py', 'exec'), ns)
team_weights, mean_cluster, strat_cluster, f3 = ns['team_weights'], ns['mean_cluster'], ns['strat_cluster'], ns['f3']


def mean_draws(pids, x, seed=2):
    """same as mean_cluster but returns the per-draw values (for paired differences)."""
    x = np.asarray(x, float); W = team_weights(np.asarray(pids), seed); return x.mean(), (W @ x) / np.maximum(W.sum(1), 1e-9)


def strat_draws(df, col, seed=1, min_n=30):
    """same as strat_cluster(df, col, 'group_tight', 'target', 'control', 'citation_bin') but returns per-draw values."""
    df = df[df.group_tight.isin(['target', 'control'])].dropna(subset=[col]).reset_index(drop=True); cells = []
    for s, ss in df.groupby('citation_bin'):
        ia, ib = ss.index[ss.group_tight == 'target'].to_numpy(), ss.index[ss.group_tight == 'control'].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.full(NB, np.nan), 0
    w = np.array([len(x) * len(y) / (len(x) + len(y)) for x, y in cells]); w /= w.sum()
    x = df[col].to_numpy(float); W = team_weights(df.paper_id.to_numpy(), seed)
    est = sum(wi * (x[ia].mean() - x[ib].mean()) for wi, (ia, ib) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (ia, ib) in zip(w, cells):
        bt += wi * ((W[:, ia] @ x[ia]) / np.maximum(W[:, ia].sum(1), 1e-9) - (W[:, ib] @ x[ib]) / np.maximum(W[:, ib].sum(1), 1e-9))
    return est, bt, len(cells)


ci = lambda bt: tuple(np.percentile(bt, [2.5, 97.5]))
# ---------------------------------------------------------------- restricted ranks -> per paper
tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
RK = {c: pd.read_parquet(OUT / f'ranks{sfx}' / f'{c}.parquet').set_index('row_id') for c in CONDS}
rid = RK['true'].index
for c in CONDS:
    if not RK[c].index.equals(rid): RK[c] = RK[c].reindex(rid)
pid_row = tok.reindex(rid).to_numpy()
layers = sorted({int(col.split('_L')[1]) for col in RK['true'].columns})
PAR = {'label': LABEL}; rows = []; prow = []
pub_role = pd.read_csv(R13 / 'summary_b2_np/np_role_layer_v2.csv'); pub_lens = pd.read_csv(R13 / 'summary_b2_np/np_lens_compare_v2.csv')
LENSFULL = pd.read_parquet(R13 / 'summary_b2_np/lens_perpaper.parquet')
for l in layers:
    pr = pd.read_parquet(PR / f'perpaper_{RUN}_L{l}.parquet').join(META, on='paper_id')
    pr, _ = VP.perdonor(pr); pr['keep'] = pr.n_used >= 1; pr['tc'] = pr.group_tight.isin(['target', 'control'])
    use = VP.use_matrix(pr)
    cols = {'probe': pr.spec_pd.to_numpy()}
    for lens in LENSES:
        for dec in DECS:
            c = f'rr_{lens}_{dec}_L{l}'
            pm = {cd: pd.Series(-np.log10(RK[cd][c].to_numpy(float))).groupby(pid_row).mean().reindex(pr.paper_id).to_numpy() for cd in CONDS}
            cols[f'{lens}_{dec}'] = VP.from_scores(pm['true'], np.stack([pm[f'false_{k}'] for k in KS], 1), use)[0]
        x = LENSFULL[(LENSFULL.run == RUN) & (LENSFULL.readout == lens) & (LENSFULL.layer == l)].set_index('paper_id').reindex(pr.paper_id)
        cols[f'{lens}_fullvocab'] = VP.from_scores(x['true'].to_numpy(), np.stack([x[f'false_{k}'].to_numpy(float) for k in KS], 1), use)[0]
    D = pr[['paper_id', 'group_tight', 'citation_bin', 'tc', 'keep']].assign(**cols)
    K = D[D.keep].reset_index(drop=True)
    if a.tiny: K = K.dropna(subset=[c for c in cols if c.endswith(('b16', 'f32'))]).reset_index(drop=True)
    nan_info = {k: int(K.loc[K.tc, k].isna().sum()) for k in cols}
    PAR[f'nan_kept_tc_L{l}'] = nan_info
    KT = K[K.tc].reset_index(drop=True)
    PAR[f'n_tc_kept_L{l}'] = int(len(KT))
    draws = {}; ests = {}
    for k in cols:
        e, bt = mean_draws(KT.paper_id, KT[k].to_numpy()); t, tb, nb = strat_draws(K, k)
        draws[k] = (bt, tb); ests[k] = (e, t)
        rows.append(dict(layer=l, readout=k, scale='9137 name ids' if k == 'probe' or k.endswith(('b16', 'f32')) else 'full vocabulary',
                         n_tc=len(KT), spec=e, spec_lo=ci(bt)[0], spec_hi=ci(bt)[1], tc=t, tc_lo=ci(tb)[0], tc_hi=ci(tb)[1], tc_bins=nb,
                         true_mean=np.nan, label=LABEL))
        # same numbers via the published functions (sanity: identical)
        ref_e = mean_cluster(KT.paper_id, KT[k]); ref_t = strat_cluster(K, k, 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
        PAR.setdefault('funcs_identical', []).append(bool(np.allclose([e, *ci(bt), t, *ci(tb)], [ref_e[0], ref_e[1], ref_e[2], ref_t[0], ref_t[1], ref_t[2]], equal_nan=True)))
    for k in cols:
        if k == 'probe': continue
        dcol = KT['probe'] - KT[k]; e = float(dcol.mean()); bt = draws['probe'][0] - draws[k][0]
        t = ests['probe'][1] - ests[k][1]
        tb = draws['probe'][1] - draws[k][1]
        # check: strat on the per-paper difference column gives the same point estimate
        t2, tb2, _ = strat_draws(K.assign(_d=K['probe'] - K[k]), '_d')
        prow.append(dict(layer=l, lens=k, contrast='probe - lens', n_tc=len(KT), spec_diff=e, spec_diff_lo=ci(bt)[0], spec_diff_hi=ci(bt)[1],
                         tc_diff=t, tc_diff_lo=ci(tb)[0], tc_diff_hi=ci(tb)[1], tc_diff_check_percol=t2, tc_diff_check_percol_lo=ci(tb2)[0], tc_diff_check_percol_hi=ci(tb2)[1],
                         p_boot_tc_le0=float((tb <= 0).mean()), p_boot_spec_le0=float((bt <= 0).mean()), label=LABEL))
T = pd.DataFrame(rows).drop(columns='true_mean'); P = pd.DataFrame(prow)
T.to_csv(OUT / f'h3_samescale_table{sfx}.csv', index=False); P.to_csv(OUT / f'h3_samescale_paired{sfx}.csv', index=False)

# ---------------------------------------------------------------- parity summary
pj = {c: json.loads((OUT / f'parity{sfx}' / f'{c}.json').read_text()) for c in CONDS}
P1 = []
for c, j in pj.items():
    for k, v in j.items():
        if k.startswith(('p1_full_exact_share_', 'p2_n_violations_', 'p2_restricted_le_storedfull_share_', 'p2_restricted_le_recomputedfull_share_', 'p1_full_within1pct')):
            P1.append(dict(cond=c, key=k, value=v))
P1 = pd.DataFrame(P1); P1.to_csv(OUT / f'parity_rows{sfx}.csv', index=False)
PAR['vocab_rows_vs_hf_maxabs'] = max(j['vocab_rows_vs_hf_maxabs'] for j in pj.values()); PAR['J_dtype'] = pj['true']['J_dtype']
PAR['p2_total_violations_b16'] = int(P1[P1.key.str.startswith('p2_n_violations') & P1.key.str.endswith('b16')].value.sum())
PAR['p2_total_violations_f32'] = int(P1[P1.key.str.startswith('p2_n_violations') & P1.key.str.endswith('f32')].value.sum())
for lens in LENSES:
    for l in layers:
        s = P1[P1.key == f'p1_full_exact_share_{lens}_L{l}']; n = [pj[c][f'p1_n_{lens}_L{l}'] for c in s.cond]
        PAR[f'p1_exact_share_{lens}_L{l}'] = float(np.average(s.value.astype(float), weights=n)) if sum(n) else None
        PAR[f'p1_status_{lens}_L{l}'] = 'OK' if (PAR[f'p1_exact_share_{lens}_L{l}'] or 0) >= 0.95 else 'WARN'
# parity 3: published values
p3 = []
for l in layers:
    pp = pub_role[(pub_role.version == 'Vpd') & (pub_role.run == RUN) & (pub_role.layer == l)]
    mine = T[(T.layer == l) & (T.readout == 'probe')].iloc[0]
    if len(pp):
        pp = pp.iloc[0]
        for a_, b_ in (('spec', 'spec'), ('spec_lo', 'lo'), ('spec_hi', 'hi'), ('tc', 'tc_diff'), ('tc_lo', 'tc_lo'), ('tc_hi', 'tc_hi'), ('n_tc', 'n_tc')):
            p3.append(dict(layer=l, what=f'probe {a_}', mine=float(mine[a_]), published=float(pp[b_]), absdiff=abs(float(mine[a_]) - float(pp[b_]))))
    for lens in LENSES:
        q = pub_lens[(pub_lens.version == 'Vpd') & (pub_lens.run == RUN) & (pub_lens.layer == l) & (pub_lens.readout == lens)]
        m2 = T[(T.layer == l) & (T.readout == f'{lens}_fullvocab')].iloc[0]
        if len(q):
            q = q.iloc[0]
            for a_, b_ in (('spec', 'lens_spec'), ('spec_lo', 'lens_lo'), ('spec_hi', 'lens_hi'), ('tc', 'lens_tc_diff'), ('tc_lo', 'lens_tc_lo'), ('tc_hi', 'lens_tc_hi')):
                p3.append(dict(layer=l, what=f'{lens} fullvocab {a_}', mine=float(m2[a_]), published=float(q[b_]), absdiff=abs(float(m2[a_]) - float(q[b_]))))
P3 = pd.DataFrame(p3); P3.to_csv(OUT / f'parity3_published{sfx}.csv', index=False)
PAR['p3_max_absdiff'] = float(P3.absdiff.max()) if len(P3) else None; PAR['p3_status'] = 'OK' if len(P3) and P3.absdiff.max() <= 1e-9 else 'WARN'
PAR['funcs_identical_all'] = bool(all(PAR.pop('funcs_identical')))
(OUT / f'parity_summary{sfx}.json').write_text(json.dumps(PAR, indent=1, default=str))

# ---------------------------------------------------------------- report
NM = {'probe': 'probe (Vpd)', 'jlens_public_b16': 'public J-lens, restricted (b16, main)', 'logit_b16': 'logit lens, restricted (b16, main)',
      'jlens_public_f32': 'public J-lens, restricted (f32 probe decoder)', 'logit_f32': 'logit lens, restricted (f32 probe decoder)',
      'jlens_public_fullvocab': 'public J-lens, full vocab (published)', 'logit_fullvocab': 'logit lens, full vocab (published)'}
L = [f'# H3 same-scale comparison at the name positions — {LABEL}', '', ('**TINY TEST (shard 0 only): numbers meaningless.**\n' if a.tiny else '') +
     'Plan 2026-11-14b item 2. Name-position probe (addendum 11 A, Vpd per-donor version, surname first token) vs the logit lens and the '
     'public J-lens, with both lenses now ranking the gold token ONLY among the same 9,137 name token ids the probe ranks within '
     '(nlr = log10(1/rank)). Per paper: mean over the surname-first-token positions of all authors; spec = true − mean of the usable false '
     'titles (the probe\'s per-donor rule, same papers); target − control within citation bin (Stage 10 definition, ≥ 30 per cell); '
     'author-team cluster bootstrap 2,000 draws (archived teams). Probe, lenses and probe − lens use the same draws. '
     'Lens decoder: b16 = Stage 10 model.unembed (bf16 final norm + bf16 lm_head, bf16 logits, ties count as not greater) — main; '
     'f32 = the probe\'s own fp32 decoder (sensitivity). * = CI excludes 0.', '']
for l in layers:
    L += [f'## L{l}  (target + control papers kept: {PAR[f"n_tc_kept_L{l}"]})', '', '| readout | scale | spec | target − control |', '|---|---|---|---|']
    for r in T[T.layer == l].itertuples():
        L.append(f'| {NM.get(r.readout, r.readout)} | {r.scale} | {f3(r.spec, r.spec_lo, r.spec_hi)} | {f3(r.tc, r.tc_lo, r.tc_hi)} |')
    L += ['', '| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |', '|---|---|---|---|']
    for r in P[P.layer == l].itertuples():
        if r.lens.endswith('fullvocab'): continue
        L.append(f'| probe − {NM.get(r.lens, r.lens)} | {f3(r.spec_diff, r.spec_diff_lo, r.spec_diff_hi)} | {f3(r.tc_diff, r.tc_diff_lo, r.tc_diff_hi)} | {r.p_boot_tc_le0:.3f} |')
    L.append('')
L += ['## Parity / self-checks (WARN only)', '',
      f'- (1) full-vocab rank recomputed on the parity shard from the stored fp16 residual (b16 decoder) vs stored rank: ' +
      ', '.join(f'{lens} L{l} {PAR[f"p1_exact_share_{lens}_L{l}"]:.4f} ({PAR[f"p1_status_{lens}_L{l}"]})' for lens in LENSES for l in layers) +
      ' (logit: vs stored rank_logit_L; J-lens: vs Stage 10 raw jlens_public rank).',
      f'- (2) restricted rank ≤ stored full-vocab rank, every surname-first row, all conditions/layers/lenses: violations b16 {PAR["p2_total_violations_b16"]}, f32 {PAR["p2_total_violations_f32"]} (details parity_rows.csv).',
      f'- (3) published values reproduced (probe Vpd surname_first spec/T−C/CI/n, full-vocab lens spec/T−C/CI): max |diff| {PAR["p3_max_absdiff"]:.2e} ({PAR["p3_status"]}); details parity3_published.csv.',
      f'- vocab_rows.npz lm_head rows vs HF bf16 lm_head: max |diff| {PAR["vocab_rows_vs_hf_maxabs"]:.2e}; J dtype {PAR["J_dtype"]}; published-function recomputation identical: {PAR["funcs_identical_all"]}.', '']
(OUT / f'report{sfx}.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
