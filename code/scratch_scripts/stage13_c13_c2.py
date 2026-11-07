"""Addendum 13 item C-2 (2026-11-06): Stage 8 CPU proxy from Stage 10 raw (title-specific rank signal).

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-2".
Papers  the 200 Stage 8 papers and their 100 frozen A/B pairs (351_stage8/cohort/stage8_papers.csv, matching/stage8_ab_pairs.csv).
Measure Stage 10 title-specific signal spec = nlr(true) - mean_k nlr(false_k), nlr = log10(1/rank), token-weighted paper mean
        (stage13_c13_s10lib). Versions: fa_first (first author, first token; closest to W), fa_all (first author, all tokens),
        aa_all (all authors, all tokens); aa_first / aa_cont descriptive. Readouts jlens_public (Stage 8 primary), logit, final.
        Layers: L56 and int6 (mean of L24, 32, 40, 48, 56, 62 = the 7-layer endpoint without L16); all 6 layers descriptive.
Tests   RQ1 analogue: all-paper mean spec > 0, team-cluster bootstrap (2,000, archived team ids; primary per plan general rules),
        iid paper bootstrap as Stage 8D (10,000) as reference. RQ2 analogue: A - B over the 100 pairs, paired bootstrap over pairs
        (Stage 8D bootstrap, 10,000). Leave-one-pair-out (as the 2026-10-30 Stage 8 recompute) for jlens_public L56 / int6.
Decision (plan, batch 3 item 3-4): GPU re-run of the true W is triggered if, in the aa_all version (jlens_public, L56 or int6), the
        RQ1 or RQ2 conclusion (sign or CI excluding 0) differs from the published Stage 8 conclusion (all four: positive, CI > 0).
HARD    stage13_c13_s10lib.identity_check (join identity; first author first token at final == Stage 10 stored value).
Usage   stage13_c13_c2.py [--tiny]   (tiny: first 20 pairs, separate output dir)
"""
import argparse, json, hashlib, ast, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R8 = B / '351_stage8'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum13.json'; PLAN_SHA = 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e'
L = None


def load(path, name):
    import importlib.util
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
lib = load(H / '13_stage13/stage13_c13_s10lib.py', 'c13lib')
OUT = R13 / ('summary_c13/c2_tiny' if a.tiny else 'summary_c13/c2'); OUT.mkdir(parents=True, exist_ok=True)
REP = OUT / 'c13_C2.md' if a.tiny else R13 / 'reports/c13_C2.md'

pairs = pd.read_csv(R8 / 'matching/stage8_ab_pairs.csv')
papers = pd.read_csv(R8 / 'cohort/stage8_papers.csv')
if a.tiny: pairs = pairs.iloc[:20]
pids = sorted(set(pairs.A_id) | set(pairs.B_id)); papers = papers[papers.paper_id.isin(pids)]
assert len(pids) == (40 if a.tiny else 200) and len(pairs) == (20 if a.tiny else 100)
cand = pd.read_csv(R8 / 'controls/stage8_author_candidates.csv', usecols=['paper_id', 'pool', 'gold_first_token_id', 'all_token_ids'])
gold = cand[cand.pool == 'gold'].drop_duplicates('paper_id').set_index('paper_id')
gold = gold[gold.index.isin(pids)]

tok = lib.tokens_for(pids); print('tokens', len(tok), 'authors', tok.groupby(['paper_id', 'author_index']).ngroups, flush=True)
ranks = lib.load_ranks(tok); print('ranks loaded', len(ranks), flush=True)

# ---------------- HARD CHECK
HC = lib.identity_check(tok, ranks, pids, gold_first=gold.gold_first_token_id.to_dict(),
                        gold_all={p: ast.literal_eval(s) for p, s in gold.all_token_ids.items()})
(OUT / 'c2_hardcheck.json').write_text(json.dumps(HC, indent=1, default=str)); print('HARD CHECK', HC['status'], flush=True)
if HC['status'] != 'PASS':
    REP.write_text(f'# C-2: HARD CHECK FAILED (item stopped)\n\n```\n{json.dumps(HC, indent=1, default=str)}\n```\n'); sys.exit(2)

P = lib.paper_table(tok, ranks); P.to_csv(OUT / 'c2_paper_values.csv', index=False)
TEAM = lib.team_ids()
VERS = ['fa_first', 'fa_all', 'aa_all', 'aa_first', 'aa_cont']
rows = []; seed = 3513200
for s in VERS:
    for (ro, l), g in P[P.subset == s].groupby(['readout', 'layer']):
        g = g.set_index('paper_id'); seed += 10
        e = lib.mean_cluster(g.index.to_numpy(), g.spec.to_numpy(), TEAM, seed=seed)
        ei = lib.boot8d(g.spec.to_numpy(), seed + 1)
        d = (g.spec.reindex(pairs.A_id).to_numpy() - g.spec.reindex(pairs.B_id).to_numpy())
        okd = ~np.isnan(d); e2 = lib.boot8d(d[okd], seed + 2)
        rows.append(dict(version=s, readout=ro, layer=l, n_papers=e[3], rq1=e[0], rq1_team_lo=e[1], rq1_team_hi=e[2], rq1_iid_lo=ei[1], rq1_iid_hi=ei[2],
                         n_pairs=e2[3], rq2=e2[0], rq2_lo=e2[1], rq2_hi=e2[2], mean_true=g['true'].mean(), mean_false=g['false'].mean(),
                         A_mean=g.spec.reindex(pairs.A_id).mean(), B_mean=g.spec.reindex(pairs.B_id).mean()))
R = pd.DataFrame(rows); R.to_csv(OUT / 'c2_rq.csv', index=False)

# ---------------- LOPO (as stage8_frozen_plan_recompute: RQ2 drops the pair; RQ1 drops both papers of the pair)
LO = []; LS = []
for s in ['fa_first', 'fa_all', 'aa_all']:
    for l in ['56', 'int6']:
        g = P[(P.subset == s) & (P.readout == 'jlens_public') & (P.layer == l)].set_index('paper_id').spec
        d = g.reindex(pairs.A_id).to_numpy() - g.reindex(pairs.B_id).to_numpy(); full2, full1 = d.mean(), g.mean()
        reps = []
        for q, x in enumerate(pairs.itertuples()):
            keep = np.arange(len(pairs)) != q
            m2 = lib.boot8d(d[keep], 20261106 + q)
            v1 = g.drop([x.A_id, x.B_id]); m1 = lib.mean_cluster(v1.index.to_numpy(), v1.to_numpy(), TEAM, seed=20261606 + q)
            reps.append(dict(version=s, layer=l, dropped_pair=x.pair_id, rq2=m2[0], rq2_lo=m2[1], rq2_hi=m2[2], rq1=m1[0], rq1_lo=m1[1], rq1_hi=m1[2]))
        LO += reps; rr = pd.DataFrame(reps)
        for rq, full in (('RQ2', full2), ('RQ1', full1)):
            c = rq.lower()
            LS.append(dict(version=s, layer=l, question=rq, full=full, lopo_min=rr[c].min(), lopo_max=rr[c].max(), sign_flip=bool((np.sign(rr[c]) != np.sign(full)).any()),
                           n_ci_excl_0_pos=int((rr[f'{c}_lo'] > 0).sum()), n_ci_excl_0_neg=int((rr[f'{c}_hi'] < 0).sum()), n_rep=len(rr)))
pd.DataFrame(LO).to_csv(OUT / 'c2_lopo_by_pair.csv', index=False); LSd = pd.DataFrame(LS); LSd.to_csv(OUT / 'c2_lopo_summary.csv', index=False)

# ---------------- decision
pub = pd.read_csv(R8 / 'recompute_2026-10-30/s8_endpoints.csv')
cls = lambda lo, hi: 'pos' if lo > 0 else ('neg' if hi < 0 else 'ns')
PUB = {('RQ1', 'int6'): ('pos', '+2.326 pp [+1.496, +3.192] (7-layer integrated)'), ('RQ2', 'int6'): ('pos', '+2.409 pp [+0.909, +4.003] (7-layer integrated)'),
       ('RQ1', '56'): ('pos', '+5.178 pp [+2.926, +7.476]'), ('RQ2', '56'): ('pos', '+4.981 pp [+0.322, +9.915]')}
DEC = []
for s in ['fa_first', 'fa_all', 'aa_all']:
    for l in ['56', 'int6']:
        x = R[(R.version == s) & (R.readout == 'jlens_public') & (R.layer == l)].iloc[0]
        for rq, est, lo, hi, alt in (('RQ1', x.rq1, x.rq1_team_lo, x.rq1_team_hi, cls(x.rq1_iid_lo, x.rq1_iid_hi)), ('RQ2', x.rq2, x.rq2_lo, x.rq2_hi, None)):
            c = cls(lo, hi); DEC.append(dict(version=s, layer=l, question=rq, est=est, lo=lo, hi=hi, cls=c, cls_iid_paper=alt, published=PUB[(rq, l)][0],
                                             published_value=PUB[(rq, l)][1], same=(c == PUB[(rq, l)][0]) and (np.sign(est) > 0)))
DEC = pd.DataFrame(DEC); DEC.to_csv(OUT / 'c2_decision_table.csv', index=False)
aa = DEC[DEC.version == 'aa_all']; trig = bool((~aa.same).any())
decision = dict(gpu_rerun_triggered=trig, rule='aa_all, jlens_public, L56 and int6: RQ1 (team CI) or RQ2 (pair bootstrap) class differs from published (pos)',
                cells=aa.to_dict('records'), tiny=a.tiny)
(OUT / 'c2_decision.json').write_text(json.dumps(decision, indent=1, default=str))

# ---------------- report
f3 = lambda v, lo, hi: f'{v:+.4f} [{lo:+.4f}, {hi:+.4f}]'
T = ['# C-2 (addendum 13): Stage 8 CPU proxy from Stage 10 raw', '',
     ('**TINY TEST (first 20 pairs)**\n' if a.tiny else '') +
     'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...). Teacher-forced preference, not generation. '
     'Metric: Stage 10 title-specific signal = log10(1/rank) of the gold name tokens under the true title minus the mean under Stage 10\'s 5 matched false titles '
     '(token-weighted paper mean). This is a proxy: a different metric (rank against the full vocabulary, not W against 100 false names) and different false titles (5 Stage 10 donors, not the 20 Stage 8 titles), on the same 200 papers / 100 pairs. '
     'Units: log10(1/rank) (Stage 8 W is in percentage points; compare signs and CI status, not sizes). int6 = mean of L24, 32, 40, 48, 56, 62 (Stage 8 7-layer endpoint minus L16, not stored).', '',
     f'## Hard check (join identity): {HC["status"]}', '',
     f'- First author first token, true title, final@63: this join vs Stage 10 raw via contexts.parquet: {HC["fa_first_final_true"]["n_papers"]}/{HC["fa_first_final_true"]["n_expected"]} papers, max |diff| {HC["fa_first_final_true"]["max_abs_diff"]:.1e}.',
     f'- All-token paper value vs Stage 10 paper_title_contrasts: final 63 max |diff| true {HC["aa_all_final_63"]["max_abs_diff_true"]:.1e}, spec {HC["aa_all_final_63"]["max_abs_diff_spec"]:.1e}; '
     f'public L56 true {HC["aa_all_jlens_public_56"]["max_abs_diff_true"]:.1e}, spec {HC["aa_all_jlens_public_56"]["max_abs_diff_spec"]:.1e}.',
     f'- WARN-only: Stage 10 first-author token 0 == Stage 8 gold_first_token_id for {HC["warn_gold_first_token_match"]["match"]}/{HC["warn_gold_first_token_match"]["n"]} papers; '
     f'all first-author token ids == Stage 8 all_token_ids for {HC["warn_gold_all_tokens_match"]["match"]}/{HC["warn_gold_all_tokens_match"]["n"]}.',
     f'- Scored: {len(pids)} papers, {tok.groupby(["paper_id", "author_index"]).ngroups} author contexts, {len(tok)} name tokens.', '',
     '## Decision for batch 3 item 3-4 (GPU re-run of the true W)', '',
     f'**GPU re-run triggered: {"YES" if trig else "NO"}.** Rule: aa_all version, public J-lens, at L56 and int6, RQ1 (team CI) and RQ2 (pairs) must keep the published conclusion (positive, CI excluding 0).', '',
     '| version | layer | question | proxy estimate [95% CI] | class | iid-paper class (RQ1) | published Stage 8 (W, pp) | same conclusion |', '|---|---|---|---|---|---|---|---|']
for _, x in DEC.iterrows():
    T.append(f'| {x.version} | {"L56" if x.layer == "56" else "int6"} | {x.question} | {f3(x.est, x.lo, x.hi)} | {x.cls} | {x.cls_iid_paper or "-"} | {x.published_value} | {"yes" if x.same else "**no**"} |')
T += ['', '## Leave-one-pair-out (public J-lens)', '', '| version | layer | question | full | LOPO min | LOPO max | sign flip | replicates with CI > 0 | CI < 0 |', '|---|---|---|---|---|---|---|---|---|']
for _, x in LSd.iterrows():
    T.append(f'| {x.version} | {x.layer} | {x.question} | {x.full:+.4f} | {x.lopo_min:+.4f} | {x.lopo_max:+.4f} | {x.sign_flip} | {x.n_ci_excl_0_pos}/{x.n_rep} | {x.n_ci_excl_0_neg}/{x.n_rep} |')
T += ['', '## All versions, readouts and layers', '', 'RQ1 = all-paper mean spec (team CI; iid paper CI); RQ2 = A - B over pairs (pair bootstrap). A / B = group means of spec.', '',
      '| version | readout | layer | RQ1 [team CI] | iid CI | RQ2 A - B [pair CI] | A mean | B mean | true / false level |', '|---|---|---|---|---|---|---|---|---|']
order = {'jlens_public': 0, 'logit': 1, 'final': 2}
for _, x in R.sort_values(['version', 'readout', 'layer'], key=lambda c: c.map(order) if c.name == 'readout' else c).iterrows():
    T.append(f'| {x.version} | {x.readout} | {x.layer} | {f3(x.rq1, x.rq1_team_lo, x.rq1_team_hi)} | [{x.rq1_iid_lo:+.4f}, {x.rq1_iid_hi:+.4f}] | {f3(x.rq2, x.rq2_lo, x.rq2_hi)} | {x.A_mean:+.4f} | {x.B_mean:+.4f} | {x.mean_true:+.3f} / {x.mean_false:+.3f} |')
REP.write_text('\n'.join(T) + '\n'); print('wrote', REP, 'GPU rerun triggered:', trig)
