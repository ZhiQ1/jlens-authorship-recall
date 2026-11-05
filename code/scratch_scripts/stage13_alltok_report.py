"""Addendum 9 (2026-11-05): report for the all-token title-position probe (stage13_alltok_probe.py outputs).

Plan (frozen): 381_stage13/config/prereg_addendum9.json (sha256 a9896357...).
'All-paper' signal = mean per-paper spec over target + control papers (6,841; the E4b definition behind +0.050/+0.061/+0.075),
title-reuse papers dropped; the mean over all 9,108 papers is given beside it. Intervals: team-cluster bootstrap
(teams = stage13_cpu.group_folds team ids, archived; 2,000 draws; same estimators as stage13_cluster_ci.py).
Primary (plan): surname_first title-specific signal at L40 > 0; surname_first - initial at L40 (difference of the two all-paper
means, both from the same team draws; the paired within-paper difference is a sensitivity check).
Gap rule (addendum 4): the model's own output gap per role (Stage 10 final@63, true - false_0 title, mean log10(1/rank) over the
role's tokens, target + control papers); ratios are given only where that gap >= 0.05 (and only as indicative: the probe ranks within
the name vocabulary, the output within the full vocabulary).
Group split (addendum 7, exploratory): per role, the same probe predictions scored on UNWRITTEN authors' tokens only (consistent papers).
Outputs: OUT/*.csv, report 381_stage13/reports/e4b_alltok.md (tiny: alltok_tiny/...).
"""
import argparse, importlib.util, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum9.json'; PLAN_SHA = 'a98963579aa2c4af0e0f266a97407c8f171d9dd47116ca7d1cac90e198d262c7'
NB = 2000
ROLES = ['initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']
ROLE_OF = {'initial': 'initial_first', 'given_first': 'given_first', 'given_cont': 'given_cont', 'surname_first': 'surname_first', 'surname_cont': 'surname_cont'}
GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
root = R13 / 'alltok_tiny' if a.tiny else R13
PR = root / 'summary_alltok/probe'; OUT = root / 'summary_alltok'; REP = root / 'reports/e4b_alltok.md'; REP.parent.mkdir(parents=True, exist_ok=True)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'recall_level', 'mc_team_outcome_tight'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS))
r, o = papers.recall_level, papers.mc_team_outcome_tight
papers['grp'] = np.select([(r == 'R0') & (o == 'strong'), (r == 'R0') & (o == 'fail'), (r == 'R1') & (o == 'strong'), (r == 'R1') & (o == 'fail'),
                           (r == 'R0') & (o == 'uncertain'), (r == 'R1') & (o == 'uncertain'), (r == 'R2') & (o == 'strong')], GROUPS, 'other')
META = papers.set_index('paper_id')


# ---------------------------------------------------------------- team bootstrap (as stage13_cluster_ci.py)
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
    """mean(x1) - mean(x2) over two paper sets, both from the same team draws (teams of the union)."""
    p1, p2 = np.asarray(p1), np.asarray(p2); allp = np.concatenate([p1, p2]); W = team_weights(allp, seed)
    W1, W2 = W[:, :len(p1)], W[:, len(p1):]
    bt = (W1 @ x1) / np.maximum(W1.sum(1), 1e-9) - (W2 @ x2) / np.maximum(W2.sum(1), 1e-9)
    return x1.mean() - x2.mean(), *np.percentile(bt, [2.5, 97.5])


f3 = lambda v, lo, hi: f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
nl = lambda r_: -np.log10(np.asarray(r_, float))


def get(run, l):
    f = PR / f'perpaper_{run}_L{l}.parquet'
    if not f.exists(): return None
    d = pd.read_parquet(f).join(META[['group_tight', 'citation_bin', 'grp']], on='paper_id')
    d['tc'] = d.group_tight.isin(['target', 'control']); return d


fits = [json.loads(f.read_text()) for f in sorted(PR.glob('fit_*.json'))]
FIT = pd.DataFrame(fits); layers = sorted(FIT.layer.unique()); runs = [x for x in ['e4b_parity', 'first_alltok'] + ROLES if x in set(FIT.run)]
L = ['# Addendum 9: title-position probe on all name tokens, by token role', '',
     ('**TINY TEST (random model, 2 shards): numbers are meaningless; code path only.**\n' if a.tiny else '') +
     'Teacher-forced preference, not generation (addendum 4). Plan: `381_stage13/config/prereg_addendum9.json` (sha256 a9896357...).',
     'Probe: title-last residual (true / false_0 title) -> ridge -> the model\'s own L63 state at the positions predicting the role\'s tokens '
     '(mean per paper) -> final norm + lm_head rows of all 9,137 name token ids -> log10(1/rank) of each gold token of the role. '
     'Author-team folds (archived), training-fold standardisation, alpha on fold 0, title-reuse papers dropped. '
     'All-paper = target + control papers (E4b definition); team-cluster bootstrap intervals (2,000 draws).', '']

# ---------------------------------------------------------------- checks
L += ['## 1. Checks (WARN only)', '']
ck = [json.loads(f.read_text()) for f in sorted((OUT / 'checks').glob('shard_*.json'))]
if ck:
    C = pd.DataFrame(ck)
    for c_ in ['C1_rel_norm_max', 'C1_rel_norm_mean', 'C1_max_abs']:
        if c_ not in C: C[c_] = np.nan
    C.to_csv(OUT / 'gpu_checks.csv', index=False)
    L += [f'GPU data step: {len(C)} shards, {int(C.n_rows.sum())} name-token rows.',
          f'- C1 (":" state of token 0 vs Stage 11 titlepos resid_colon L63): {int((C.C1_status == "OK").sum())}/{len(C)} shards OK; '
          f'relative norm diff max {C.C1_rel_norm_max.max():.2e}, mean {C.C1_rel_norm_mean.mean():.2e}; max |diff| {C.C1_max_abs.max():.3g} (n = {int(C.C1_n.sum())} rows).',
          f'- C2 (gold rank decoded from the stored fp16 state vs Stage 10 final@63): {int((C.C2_status == "OK").sum())}/{len(C)} shards OK; exact match '
          f'{(C.C2_rank_fp16_match * C.n_rows).sum() / C.n_rows.sum():.4f} (from the unrounded bf16 state: {(C.C2_rank_bf16_match * C.n_rows).sum() / C.n_rows.sum():.4f}); '
          f'mean |d log10 rank| {(C.C2_rank_fp16_mean_abs_dlog10 * C.n_rows).sum() / C.n_rows.sum():.4f}; fp16 vs bf16 rank match {(C.C2_fp16_vs_bf16_match * C.n_rows).sum() / C.n_rows.sum():.4f}.',
          f'- fp16 storage: non-finite {int(C.n_nonfinite.sum())}, |x| >= 65504: {int(C.n_fp16_overflow_risk.sum())}; max |resid| {C.max_abs_resid.max():.1f}.']
    w = C[(C.C1_status != 'OK') | (C.C2_status != 'OK') | (C.fp16_status != 'OK')]
    if len(w): L.append(f'- WARN shards: {", ".join(str(int(s)) for s in w.shard)}')
vc = OUT / 'vocab_rows_check.json'
if vc.exists():
    v = json.loads(vc.read_text()); L.append(f'- Vocabulary rows: {v["n_ids"]} name token ids; the 4,314 Stage 11 probe_vocab rows equal bit for bit: {v["rows_equal_probe_vocab"]}, norm weight equal: {v["norm_equal"]} ({v["status"]}).')
L.append('')

# ---------------------------------------------------------------- E4b parity
if 'e4b_parity' in runs:
    ref = pd.read_parquet(R13 / 'summary_cpu_trainstd/perpaper_probe_spec.parquet')
    ref = ref[(ref.split == 'group') & (ref.excl == 'title-reuse') & (ref.source == 'E4b')]
    rows = []
    for l in layers:
        d = get('e4b_parity', l)
        if d is None: continue
        m = d.merge(ref[ref.layer == l][['paper_id', 'spec', 'dropped']], on='paper_id', suffixes=('', '_ref'))
        k = d[d.tc & ~d.dropped]; e = mean_cluster(k.paper_id, k.spec)
        kr = ref[(ref.layer == l) & ~ref.dropped]
        rows.append(dict(layer=l, n_matched=len(m), max_abs_spec_diff=float((m.spec - m.spec_ref).abs().max()), dropped_flag_agree=float((m.dropped == m.dropped_ref).mean()),
                         allpaper_new=e[0], lo=e[1], hi=e[2], allpaper_published=kr.spec.mean(), n=e[3]))
    PA = pd.DataFrame(rows); PA.to_csv(OUT / 'e4b_parity.csv', index=False)
    ok = (PA.max_abs_spec_diff <= 0.01).all() and (PA.dropped_flag_agree == 1).all()
    L += ['## 2. E4b parity (first name token only, Stage 11 target and 4,314-id vocabulary, recomputed in this code)', '',
          f'Status: {"OK" if ok else "WARN"} (rule: per-paper |spec diff| <= 0.01 and identical title-reuse flags vs summary_cpu_trainstd, group / title-reuse).', '',
          '| layer | all-paper signal, this code [team CI] | published (trainstd, group / title-reuse) | max per-paper abs diff | title-reuse flags agree | n |', '|---|---|---|---|---|---|']
    for _, x in PA.iterrows():
        L.append(f'| L{int(x.layer)} | {f3(x.allpaper_new, x.lo, x.hi)} | {x.allpaper_published:+.4f} | {x.max_abs_spec_diff:.2e} | {x.dropped_flag_agree:.4f} | {int(x.n)} |')
    L.append('')

# ---------------------------------------------------------------- main table per run x layer
rows = []
for run in runs:
    if run == 'e4b_parity': continue
    for l in layers:
        d = get(run, l)
        if d is None: continue
        k = d[d.tc & ~d.dropped]; ka = d[~d.dropped]; ft = FIT[(FIT.run == run) & (FIT.layer == l)].iloc[0]
        e = mean_cluster(k.paper_id, k.spec); e9 = mean_cluster(ka.paper_id, ka.spec, seed=5)
        tcd = strat_cluster(d[~d.dropped], 'spec', 'group_tight', 'target', 'control', 'citation_bin', min_n=30)
        rows.append(dict(run=run, layer=l, n_papers_fit=int(ft.n_papers), alpha=ft.alpha, heldout_r2=ft.heldout_r2_true, n_tc=e[3], n_tok_tc=int(k.n_tok.sum()),
                         spec=e[0], spec_lo=e[1], spec_hi=e[2], spec_all9108=e9[0], spec_all9108_lo=e9[1], spec_all9108_hi=e9[2], n_all=e9[3],
                         true=k['true'].mean(), false=k['false'].mean(), ceiling=k.ceiling.mean(),
                         tc_diff=tcd[0], tc_lo=tcd[1], tc_hi=tcd[2], tc_bins=tcd[3], n_dropped=int(d.dropped.sum())))
T = pd.DataFrame(rows); T.to_csv(OUT / 'alltok_role_layer.csv', index=False)

# ---------------------------------------------------------------- output gap per role (Stage 10 final@63, true - false_0)
toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'role'])
def raw_rank(sub):
    zs = [np.load(f) for f in sorted((R10 / 'raw' / sub / 'final/L63').glob('shard_*.npz'))]
    return pd.Series(np.concatenate([z['rank'] for z in zs]), index=np.concatenate([z['row_id'] for z in zs]))
gt, gf = raw_rank(''), raw_rank('cond_false_0')
tk = toks.assign(t=nl(gt.reindex(toks.row_id).to_numpy()), f=nl(gf.reindex(toks.row_id).to_numpy())).join(META[['group_tight']], on='paper_id')
tk = tk[tk.group_tight.isin(['target', 'control'])]
gap = {}
for role in ROLES + ['first_alltok']:
    s = tk[tk.token_index == 0] if role == 'first_alltok' else tk[tk.role == ROLE_OF[role]]
    pm = s.groupby('paper_id')[['t', 'f']].mean(); gap[role] = dict(out_true=pm.t.mean(), out_false0=pm.f.mean(), out_gap=(pm.t - pm.f).mean(), n=len(pm))
G = pd.DataFrame(gap).T.reset_index().rename(columns={'index': 'run'}); G.to_csv(OUT / 'output_gap_by_role.csv', index=False)
T = T.merge(G[['run', 'out_gap']], on='run', how='left')
T['ratio_indicative'] = np.where(T.out_gap >= 0.05, T.spec / T.out_gap, np.nan); T.to_csv(OUT / 'alltok_role_layer.csv', index=False)

L += ['## 3. Title-specific probe signal per role and layer (all papers = target + control, title reuse dropped; team CI)', '',
      'spec = probe(true title) - probe(false_0 title), mean log10(1/rank) over the role\'s tokens, name vocabulary (9,137 ids). '
      '"first token" = the first name token of every author (E4b gold) with the all-token pipeline.', '']
for run in [x for x in runs if x != 'e4b_parity']:
    s = T[T.run == run]
    if not len(s): continue
    nm = 'first token (bridge to E4b)' if run == 'first_alltok' else run
    L += [f'### {nm}: {int(s.n_tc.iloc[0])} target+control papers, {int(s.n_tok_tc.iloc[0])} tokens (fit on {int(s.n_papers_fit.iloc[0])} papers)', '',
          '| layer | alpha | held-out R2 | title-specific, all papers [team CI] | all 9,108 papers | target - control within bin [team CI] (bins) | true / false_0 level | ceiling (target state) |',
          '|---|---|---|---|---|---|---|---|']
    for _, x in s.iterrows():
        L.append(f'| L{int(x.layer)} | {x.alpha:g} | {x.heldout_r2:.3f} | {f3(x.spec, x.spec_lo, x.spec_hi)} | {f3(x.spec_all9108, x.spec_all9108_lo, x.spec_all9108_hi)} | '
                 f'{f3(x.tc_diff, x.tc_lo, x.tc_hi)} ({int(x.tc_bins)}) | {x["true"]:+.3f} / {x["false"]:+.3f} | {x.ceiling:+.3f} |')
    L.append('')

# compact role x layer matrix
if len(T):
    L += ['### Summary matrix: title-specific signal (all papers) by role x layer', '', '| role | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in [x for x in runs if x != 'e4b_parity']:
        s = T[T.run == run].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join((f'{s.loc[l, "spec"]:+.3f}' + ('*' if s.loc[l, 'spec_lo'] > 0 or s.loc[l, 'spec_hi'] < 0 else '')) if l in s.index else '-' for l in layers) + ' |')
    L += ['', '\\* team CI excludes 0.', '',
          '### Target - control within citation bin, by role x layer', '', '| role | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in [x for x in runs if x != 'e4b_parity']:
        s = T[T.run == run].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join((f'{s.loc[l, "tc_diff"]:+.3f}' + ('*' if s.loc[l, 'tc_lo'] > 0 or s.loc[l, 'tc_hi'] < 0 else '')) if l in s.index else '-' for l in layers) + ' |')
    L.append('')

L += ['## 4. Gap rule (addendum 4): the model\'s own output gap per role (Stage 10 final@63, true - false_0, target + control papers)', '',
      '| role | output true | output false_0 | gap | papers | ratios reported? |', '|---|---|---|---|---|---|']
for _, x in G.iterrows():
    L.append(f'| {x.run} | {x.out_true:+.3f} | {x.out_false0:+.3f} | {x.out_gap:+.3f} | {int(x.n)} | {"yes" if x.out_gap >= 0.05 else "no (gap < 0.05)"} |')
if len(T):
    L += ['', 'Indicative ratio probe signal / output gap (different rank vocabularies: name vocabulary vs full vocabulary; not a recovery share):', '',
          '| role | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
    for run in [x for x in runs if x != 'e4b_parity']:
        s = T[T.run == run].set_index('layer')
        L.append(f'| {run} | ' + ' | '.join(f'{s.loc[l, "ratio_indicative"]:.2f}' if l in s.index and not np.isnan(s.loc[l, 'ratio_indicative']) else '-' for l in layers) + ' |')
L.append('')

# ---------------------------------------------------------------- primary contrast
PL = 40 if 40 in layers else layers[0]
L += [f'## 5. Primary question (plan): is the probe signal carried by surnames? (L{PL})', '']
prim = {}
ds_, di_ = get('surname_first', PL), get('initial', PL)
if ds_ is not None:
    ks = ds_[ds_.tc & ~ds_.dropped]; e = mean_cluster(ks.paper_id, ks.spec)
    prim['surname_first'] = dict(est=e[0], lo=e[1], hi=e[2], n=e[3])
    L.append(f'- P1 surname_first title-specific signal at L{PL}: {f3(*e[:3])} (n = {e[3]} papers) -> {"> 0 (team CI excludes 0)" if e[1] > 0 else ("< 0" if e[2] < 0 else "CI includes 0")}.')
    if di_ is not None:
        ki = di_[di_.tc & ~di_.dropped]; e2 = mean_cluster(ki.paper_id, ki.spec)
        dd = diff_cluster(ks.paper_id.to_numpy(), ks.spec.to_numpy(float), ki.paper_id.to_numpy(), ki.spec.to_numpy(float))
        pp = ks[['paper_id', 'spec']].merge(ki[['paper_id', 'spec']], on='paper_id', suffixes=('_s', '_i')).dropna()
        ep = mean_cluster(pp.paper_id, pp.spec_s - pp.spec_i, seed=6)
        prim |= {'initial': dict(est=e2[0], lo=e2[1], hi=e2[2], n=e2[3]), 'surname_minus_initial': dict(est=dd[0], lo=dd[1], hi=dd[2], n=len(ks) + len(ki)),
                 'surname_minus_initial_paired': dict(est=ep[0], lo=ep[1], hi=ep[2], n=ep[3])}
        L += [f'- initial at L{PL}: {f3(*e2[:3])} (n = {e2[3]}).',
              f'- P2 surname_first - initial at L{PL}: {f3(*dd)} (difference of the two all-paper means, joint team draws).',
              f'- sensitivity, paired within paper (papers with both roles): {f3(*ep[:3])} (n = {ep[3]}).']
pd.DataFrame(prim).T.reset_index().rename(columns={'index': 'quantity'}).to_csv(OUT / 'primary_L40.csv', index=False)
L.append('')

# ---------------------------------------------------------------- group split on unwritten authors (addendum 7, exploratory)
fl = Path(B / '391_groups/data/author_flags.parquet')
if fl.exists():
    au = pd.read_parquet(fl)[['paper_id', 'author_index', 'written', 'consistent']]
    tk2 = toks[['row_id', 'paper_id', 'author_index']].merge(au, on=['paper_id', 'author_index'], how='left')
    grow = []
    for run in [x for x in ROLES if x in runs]:
        for l in layers:
            f = PR / f'pertoken_{run}_L{l}.parquet'
            if not f.exists(): continue
            pt = pd.read_parquet(f).merge(tk2, on='row_id'); pt = pt[(pt.consistent == True) & (pt.written == False)]
            pp = pt.groupby('paper_id')[['nlr_true', 'nlr_false']].mean(); pp['spec'] = pp.nlr_true - pp.nlr_false
            d = get(run, l).set_index('paper_id'); pp = pp.join(d[['dropped', 'grp', 'group_tight', 'citation_bin']]); pp = pp[~pp.dropped].reset_index()
            for g in GROUPS:
                s = pp[pp.grp == g]
                if not len(s): continue
                e = mean_cluster(s.paper_id, s.spec, seed=7)
                grow.append(dict(run=run, layer=l, group=g, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=e[3] < 30))
            for nm, ga, gb, mn in (('A-B', 'A', 'B', 30), ('C-A', 'C', 'A', 10)):
                e = strat_cluster(pp, 'spec', 'grp', ga, gb, 'citation_bin', min_n=mn, seed=8)
                grow.append(dict(run=run, layer=l, group=nm, est=e[0], lo=e[1], hi=e[2], n=e[3], descriptive_only=False))
    GS = pd.DataFrame(grow); GS.to_csv(OUT / 'groups_unwritten_by_role.csv', index=False)
    if len(GS):
        L += ['## 6. Exploratory: by behaviour group, unwritten authors only (addendum 7; same probe predictions, gold tokens of unwritten authors, '
              'consistent papers, title reuse dropped)', '', f'Layer L{PL} (all layers in groups_unwritten_by_role.csv). n < 30: descriptive only. '
              'A-B: within bin, >= 30 per group; C-A: >= 10 (n = bins used).', '',
              '| role | ' + ' | '.join(GROUPS + ['A-B', 'C-A']) + ' |', '|---' * (len(GROUPS) + 3) + '|']
        for run in [x for x in ROLES if x in runs]:
            s = GS[(GS.run == run) & (GS.layer == PL)].set_index('group')
            cell = lambda g: '-' if g not in s.index or np.isnan(s.loc[g, 'est']) else (f'{s.loc[g, "est"]:+.3f} (n={int(s.loc[g, "n"])}, descr.)' if s.loc[g, 'descriptive_only'] else f'{f3(s.loc[g, "est"], s.loc[g, "lo"], s.loc[g, "hi"])} (n={int(s.loc[g, "n"])})')
            L.append(f'| {run} | ' + ' | '.join(cell(g) for g in GROUPS + ['A-B', 'C-A']) + ' |')
        L.append('')

# ---------------------------------------------------------------- plain summary
if 'surname_first' in prim and len(T):
    s = prim['surname_first']; ini = prim.get('initial'); dd = prim.get('surname_minus_initial')
    best = T[T.run != 'first_alltok'].sort_values('spec', ascending=False).iloc[0]
    L += ['## Plain summary', '',
          f'- Surname first tokens: the probe from the title position gives a title-specific signal of {f3(s["est"], s["lo"], s["hi"])} at L{PL} '
          f'({"above 0" if s["lo"] > 0 else "not distinguishable from 0"}).',
          (f'- Initials: {f3(ini["est"], ini["lo"], ini["hi"])}; surname minus initial {f3(dd["est"], dd["lo"], dd["hi"])} '
           f'({"surnames carry more" if dd["lo"] > 0 else ("initials carry more" if dd["hi"] < 0 else "no clear difference")}).') if ini else '',
          f'- Largest role x layer signal: {best.run} at L{int(best.layer)} ({best.spec:+.3f}).',
          f'- Parity: the first-token E4b recomputed in this code {"matches" if "e4b_parity" in runs and ok else "see section 2 for"} the published confirmatory E4b.',
          '- These are teacher-forced preferences for the correct author tokens, decoded from a linear map of the title position, not generation.', '']
REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L))
