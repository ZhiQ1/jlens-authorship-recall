"""Addendum 13 item C-1 (2026-11-06): Stages 4-7 with a title contrast, from Stage 10 raw.

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-1".
Papers  Benchmark20 (Stage 4: 351_all/351_stage4_artifacts/summary/paper_metrics.csv) and Pilot50 (Stages 5-7:
        351_stage5_crossed_v2/cohort/pilot50_v1.csv; 20 matched A/B pairs: matching/pilot50_ab_pairs.csv).
Measure Stage 10 title-specific signal (true minus mean of the 5 false titles, log10(1/rank), token-weighted paper mean;
        stage13_c13_s10lib): aa_all (all authors, all name tokens), aa_first (first token of every author) and aa_cont
        (continuation tokens), as Stage 7.1; fa_first (Stage 4 primary unit) descriptive. Readouts jlens_public, logit at
        L24, 32, 40, 48, 56, 62 (L16 not stored) + int6 (their mean), final L63.
Tests   Pilot50: A - B over the 20 pairs, paired bootstrap over pairs (Stage 8D bootstrap, 10,000); all-paper mean (team-cluster
        bootstrap 2,000, archived team ids). Benchmark20: all-paper mean (team CI) and group means (descriptive; A8/B8/C3/D1, unmatched).
        Published Stage 7.1 A - B (true-title-only JMRR) shown beside, as reference (different metric).
HARD    stage13_c13_s10lib.identity_check on the union of both lists (first author first token at final == Stage 10 stored value).
Usage   stage13_c13_c1.py [--tiny]   (tiny: first 5 Pilot50 pairs + 5 Benchmark20 papers, separate output dir)
"""
import argparse, json, hashlib, ast, sys, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum13.json'; PLAN_SHA = 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
lib = load(H / '13_stage13/stage13_c13_s10lib.py', 'c13lib')
OUT = R13 / ('summary_c13/c1_tiny' if a.tiny else 'summary_c13/c1'); OUT.mkdir(parents=True, exist_ok=True)
REP = OUT / 'c13_C1.md' if a.tiny else R13 / 'reports/c13_C1.md'

b20 = pd.read_csv(B / '351_all/351_stage4_artifacts/summary/paper_metrics.csv', usecols=['paper_id', 'group']).drop_duplicates('paper_id')
p50 = pd.read_csv(B / '351_stage5_crossed_v2/cohort/pilot50_v1.csv', usecols=['paper_id', 'group'])
pairs = pd.read_csv(B / '351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv')
if a.tiny: pairs = pairs.iloc[:5]; p50 = p50[p50.paper_id.isin(set(pairs.A_id) | set(pairs.B_id))]; b20 = b20.iloc[:5]
assert a.tiny or (len(b20) == 20 and len(p50) == 50 and len(pairs) == 20)
pids = sorted(set(b20.paper_id) | set(p50.paper_id))
cand = pd.read_csv(B / '351_stage7_2/candidates/pilot50_author_candidates.csv', usecols=['paper_id', 'pool', 'gold_first_token_id', 'all_token_ids'])
gold = cand[(cand.pool == 'gold') & cand.paper_id.isin(pids)].drop_duplicates('paper_id').set_index('paper_id')

tok = lib.tokens_for(pids); print('papers', len(pids), 'tokens', len(tok), flush=True)
ranks = lib.load_ranks(tok); print('ranks loaded', flush=True)
HC = lib.identity_check(tok, ranks, pids, gold_first=gold.gold_first_token_id.to_dict(), gold_all={p: ast.literal_eval(s) for p, s in gold.all_token_ids.items()})
(OUT / 'c1_hardcheck.json').write_text(json.dumps(HC, indent=1, default=str)); print('HARD CHECK', HC['status'], flush=True)
if HC['status'] != 'PASS':
    REP.write_text(f'# C-1: HARD CHECK FAILED (item stopped)\n\n```\n{json.dumps(HC, indent=1, default=str)}\n```\n'); sys.exit(2)

P = lib.paper_table(tok, ranks); P.to_csv(OUT / 'c1_paper_values.csv', index=False)
TEAM = lib.team_ids()
VERS = ['aa_all', 'aa_first', 'aa_cont', 'fa_first']
rows = []; seed = 3513100
for s in VERS:
    for (ro, l), g in P[P.subset == s].groupby(['readout', 'layer']):
        g = g.set_index('paper_id'); seed += 10
        gp = g.reindex(p50.paper_id); e = lib.mean_cluster(gp.index.to_numpy(), gp.spec.to_numpy(), TEAM, seed=seed)
        d = g.spec.reindex(pairs.A_id).to_numpy() - g.spec.reindex(pairs.B_id).to_numpy(); ok = ~np.isnan(d)
        e2 = lib.boot8d(d[ok], seed + 1)
        gb = g.reindex(b20.paper_id); eb = lib.mean_cluster(gb.index.to_numpy(), gb.spec.to_numpy(), TEAM, seed=seed + 2)
        gm = gb.assign(group=b20.set_index('paper_id').group).groupby('group').spec.agg(['mean', 'size'])
        rows.append(dict(version=s, readout=ro, layer=l,
                         p50_n=e[3], p50_all=e[0], p50_lo=e[1], p50_hi=e[2], p50_n_pairs=e2[3], p50_AmB=e2[0], p50_AmB_lo=e2[1], p50_AmB_hi=e2[2],
                         p50_npos_pairs=int((d[ok] > 0).sum()), p50_A=g.spec.reindex(pairs.A_id).mean(), p50_B=g.spec.reindex(pairs.B_id).mean(),
                         b20_n=eb[3], b20_all=eb[0], b20_lo=eb[1], b20_hi=eb[2],
                         **{f'b20_{k}': gm['mean'].get(k, np.nan) for k in 'ABCD'}, **{f'b20_n{k}': int(gm['size'].get(k, 0)) for k in 'ABCD'}))
R = pd.DataFrame(rows); R.to_csv(OUT / 'c1_results.csv', index=False)

# published Stage 7.1 (true-title-only JMRR, A - B, 7 layers incl. L16; integrated_7) as reference
pub = pd.read_csv(B / '351_stage7_1/summary/layer_and_integrated_effects.csv')
mm = {'first_jmrr': 'aa_first', 'continuation_jmrr': 'aa_cont', 'all_jmrr': 'aa_all'}; rm = {'jlens': 'jlens_public', 'vanilla': 'logit', 'final': 'final'}
pub = pub[pub.metric.isin(mm)].assign(version=pub.metric.map(mm), readout=pub['mode'].map(rm),
                                      layer=pub.layer.astype(str).replace({'integrated_7': 'int6'}))
R2 = R.merge(pub[['version', 'readout', 'layer', 'A_minus_B_mean', 'bootstrap_ci_low', 'bootstrap_ci_high']], on=['version', 'readout', 'layer'], how='left')
R2.to_csv(OUT / 'c1_results_with_stage71.csv', index=False)

f3 = lambda v, lo, hi: f'{v:+.4f} [{lo:+.4f}, {hi:+.4f}]' if not np.isnan(v) else '-'
cls = lambda lo, hi: 'pos' if lo > 0 else ('neg' if hi < 0 else 'ns')
T = ['# C-1 (addendum 13): Stages 4-7 with a title contrast (Stage 10 raw)', '',
     ('**TINY TEST**\n' if a.tiny else '') +
     'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...). Teacher-forced preference, not generation. '
     'Title-specific = log10(1/rank) under the true title minus the mean under Stage 10\'s 5 matched false titles, token-weighted paper mean. '
     'aa_all = all authors, all name tokens; aa_first = first token of every author; aa_cont = continuation tokens (multi-token names only); fa_first = first author, first token (Stage 4 primary unit). '
     'int6 = mean of L24-L62 (the Stage 4-7 7-layer integration without L16, which Stage 10 did not store). '
     'Stage 7.1 reference: true-title-only JMRR (1/rank, author-mean), A - B, integrated over 7 layers incl. L16: a different metric; compare signs and CI status only.', '',
     f'## Hard check (join identity): {HC["status"]}', '',
     f'- First author first token, true title, final@63, this join vs Stage 10 raw via contexts.parquet: {HC["fa_first_final_true"]["n_papers"]}/{HC["fa_first_final_true"]["n_expected"]} papers, max |diff| {HC["fa_first_final_true"]["max_abs_diff"]:.1e}.',
     f'- All-token value vs Stage 10 paper_title_contrasts: final max |diff| true {HC["aa_all_final_63"]["max_abs_diff_true"]:.1e} / spec {HC["aa_all_final_63"]["max_abs_diff_spec"]:.1e}; public L56 {HC["aa_all_jlens_public_56"]["max_abs_diff_true"]:.1e} / {HC["aa_all_jlens_public_56"]["max_abs_diff_spec"]:.1e}.',
     f'- WARN-only: Stage 10 first-author token 0 == Stage 7.2 gold first token: {HC["warn_gold_first_token_match"]["match"]}/{HC["warn_gold_first_token_match"]["n"]}; all first-author token ids: {HC["warn_gold_all_tokens_match"]["match"]}/{HC["warn_gold_all_tokens_match"]["n"]} (Benchmark20 papers outside Pilot50 have no gold file).',
     f'- Scored: {len(pids)} papers (Benchmark20 {len(b20)}, Pilot50 {len(p50)}, overlap {len(set(b20.paper_id) & set(p50.paper_id))}), {len(tok)} name tokens.', '',
     '## Pilot50: matched A - B (20 pairs) and all-paper title-specific signal', '',
     '| version | readout | layer | A - B [pair CI] (pairs > 0) | Stage 7.1 published A - B, JMRR [CI] | class new / published | all 50 papers [team CI] |', '|---|---|---|---|---|---|---|']
order = {'jlens_public': 0, 'logit': 1, 'final': 2}; vo = {v: i for i, v in enumerate(VERS)}
R2 = R2.sort_values(['version', 'readout', 'layer'], key=lambda c: c.map(vo) if c.name == 'version' else (c.map(order) if c.name == 'readout' else c))
for _, x in R2.iterrows():
    pubs = f3(x.A_minus_B_mean, x.bootstrap_ci_low, x.bootstrap_ci_high) if not pd.isna(x.A_minus_B_mean) else '-'
    cp = cls(x.bootstrap_ci_low, x.bootstrap_ci_high) if not pd.isna(x.A_minus_B_mean) else '-'
    T.append(f'| {x.version} | {x.readout} | {x.layer} | {f3(x.p50_AmB, x.p50_AmB_lo, x.p50_AmB_hi)} ({x.p50_npos_pairs}/{x.p50_n_pairs}) | {pubs} | {cls(x.p50_AmB_lo, x.p50_AmB_hi)} / {cp} | {f3(x.p50_all, x.p50_lo, x.p50_hi)} |')
T += ['', '## Benchmark20 (Stage 4; unmatched, descriptive): all-paper title-specific signal and group means', '',
      '| version | readout | layer | all 20 [team CI] | A (n) | B (n) | C (n) | D (n) |', '|---|---|---|---|---|---|---|---|']
for _, x in R2.iterrows():
    T.append(f'| {x.version} | {x.readout} | {x.layer} | {f3(x.b20_all, x.b20_lo, x.b20_hi)} | ' + ' | '.join(f'{x[f"b20_{k}"]:+.4f} ({x[f"b20_n{k}"]})' for k in 'ABCD') + ' |')
REP.write_text('\n'.join(T) + '\n'); print('wrote', REP)
