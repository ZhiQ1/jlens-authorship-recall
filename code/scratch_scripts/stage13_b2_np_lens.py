"""Batch 2, addendum 11 part A: lens comparison table input + HARD CHECK 2 (CPU, Stage 10 stored ranks only).

Plan (locked): 381_stage13/config/prereg_addendum11.json, part A "lens comparison" and "hard check (2)".
At the same positions, layers and tokens as the probe (every name-token-predicting position of every author context, true and
false_0..4 titles): Stage 10 logit-lens and public J-lens full-vocabulary ranks (351_stage10/raw/[cond_false_k/]<readout>/L<l>),
nlr = log10(1/rank). Per paper and token set: true = mean nlr over the set's tokens, false_k likewise, false_mean5 = mean_k,
spec5 = true - false_mean5 (the Stage 10 title-specific signal), spec0 = true - false_0.
Token sets: the probe runs of stage13_b2A_cols.NP_RUNS (colon_first = token_index 0 = predicted at ':'; initial = initial_first;
given_first; given_cont; surname_first; surname_cont) + 'all' (all name tokens = Stage 10 mean_nlr).
HARD CHECK 2 (plan): the lens title-specific signal used here reproduces the published Stage 10 values at L40 / L48, |diff| <= 0.005:
  (a) group means (group_tight) of spec5 for 'all' and 'surname_first' vs summary_title/A_group_layer.csv
      (spec_mean_nlr_mean, spec_mean_nlr_surname_first_mean)  [full run only: needs all papers]
  (b) target+control means of spec5 per token set vs the same means of the published per-paper values
      (summary_title/paper_title_contrasts.parquet spec_mean_nlr[_<role>]) for every set that has a published column
      (all, initial_first, given_first, surname_first, surname_cont), same paper subset.
  Per-paper max |diff| is logged (WARN if > 1e-9; not part of the hard criterion).
Output: summary_b2_np/lens_perpaper.parquet, summary_b2_np/hardcheck2.json (exit 3 on FAIL).
Usage:  stage13_b2_np_lens.py              (all 72 shards)
        stage13_b2_np_lens.py --tiny        (shards 0,1 only; root b2_np_tiny; check (b) on those papers; (a) skipped)
"""
import argparse, importlib.util, json, sys, time, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
T0 = time.time()
def log(*a):
    try: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)
    except Exception: pass


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols'); CK = load(H / '13_stage13/stage13_b2A_checks.py', 'b2A_checks')
S10L = load(H / '13_stage13/stage13_c13_s10lib.py', 's10lib')
PUB_ROLE_COL = {'all': 'spec_mean_nlr', 'initial': 'spec_mean_nlr_initial_first', 'given_first': 'spec_mean_nlr_given_first',
                'surname_first': 'spec_mean_nlr_surname_first', 'surname_cont': 'spec_mean_nlr_surname_cont'}


def run_mask(tok, run):
    if run == 'all': return np.ones(len(tok), bool)
    r = K.NP_RUNS[run]
    return (tok.token_index.to_numpy() == 0) if r is None else (tok.role.to_numpy() == r)


def lens_table(tok, ranks, layers, readouts):
    out = []
    for run in ['all'] + list(K.NP_RUNS):
        mk = run_mask(tok, run); t = tok[mk]
        for ro in readouts:
            for l in layers:
                nl = {c: -np.log10(ranks[(c, ro, l)][mk].astype(float)) for c in K.CONDS}
                df = pd.DataFrame({K.PAPER_ID: t.paper_id.to_numpy(), **nl})
                g = df.groupby(K.PAPER_ID, sort=True); mm = g.mean(); n = g.size()
                fm = mm[[f'false_{k}' for k in K.KS]].mean(1)
                out.append(pd.DataFrame({K.PAPER_ID: mm.index, 'run': run, 'readout': ro, 'layer': l, K.N_TOK: n.to_numpy(), 'true': mm['true'].to_numpy(),
                                         **{f'false_{k}': mm[f'false_{k}'].to_numpy() for k in K.KS}, 'false_mean5': fm.to_numpy(),
                                         'spec5': (mm['true'] - fm).to_numpy(), 'spec0': (mm['true'] - mm['false_0']).to_numpy()}))
    return pd.concat(out, ignore_index=True)[K.NP_LENS_COLS]


def hard_check2(LT, papers, full):
    parts = []; info = {}
    pub = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet', columns=[K.PAPER_ID, 'readout', 'layer'] + list(PUB_ROLE_COL.values()))
    pids = set(LT.paper_id); pub = pub[pub.paper_id.isin(pids)]
    G = papers.set_index(K.PAPER_ID)[K.GROUP]
    for ro in K.NP_LENS_READOUTS:
        for l in K.NP_HARD2_LAYERS:
            for run, col in PUB_ROLE_COL.items():
                x = LT[(LT.run == run) & (LT.readout == ro) & (LT.layer == l)].set_index(K.PAPER_ID).spec5
                y = pub[(pub.readout == ro) & (pub.layer == l)].set_index(K.PAPER_ID)[col]
                both = x.index.intersection(y.dropna().index)
                info[f'perpaper_maxdiff_{ro}_L{l}_{run}'] = float((x.loc[both] - y.loc[both]).abs().max()) if len(both) else np.nan
                info[f'perpaper_n_{ro}_L{l}_{run}'] = int(len(both)); info[f'perpaper_n_missing_{ro}_L{l}_{run}'] = int(len(y.dropna().index.difference(x.index)))
                tc = [p for p in y.dropna().index if G.get(p) in ('target', 'control')]
                newm = float(x.reindex(tc).mean()) if len(tc) else np.nan
                parts.append(CK.scalar_check(newm, float(y.loc[tc].mean()) if len(tc) else np.nan, K.NP_HARD2_TOL, f'b_tc_mean_{ro}_L{l}_{run}'))
    if full:
        A = pd.read_csv(R10 / 'summary_title/A_group_layer.csv')
        for ro in K.NP_LENS_READOUTS:
            for l in K.NP_HARD2_LAYERS:
                for run, col in (('all', 'spec_mean_nlr_mean'), ('surname_first', 'spec_mean_nlr_surname_first_mean')):
                    x = LT[(LT.run == run) & (LT.readout == ro) & (LT.layer == l)].set_index(K.PAPER_ID).spec5
                    new = x.groupby(G.reindex(x.index).to_numpy()).mean().rename_axis(K.GROUP).reset_index(name='v')
                    ref = A[(A.readout == ro) & (A.layer == l)][[K.GROUP, col]]
                    parts.append(CK.value_table_check(new, ref, [K.GROUP], 'v', K.NP_HARD2_TOL, f'a_group_{ro}_L{l}_{run}', ref_val=col))
    res = CK.combine(*parts, name='hard2_lens_vs_published_stage10'); res['info'] = info
    mx = np.nanmax([v for k, v in info.items() if k.startswith('perpaper_maxdiff')])
    res['perpaper_max_abs_diff'] = float(mx); res['perpaper_status'] = 'OK' if mx <= 1e-9 else 'WARN'
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    root = R13 / 'b2_np_tiny' if a.tiny else R13; OUT = root / 'summary_b2_np'; OUT.mkdir(parents=True, exist_ok=True)
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=[K.PAPER_ID, K.GROUP, K.CBIN, 'shard'])
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'author_index', 'token_index', 'token_id', 'role'])
    if a.tiny: tok = tok[tok.shard.isin([0, 1])].reset_index(drop=True)
    readouts = [(ro, l) for ro in K.NP_LENS_READOUTS for l in K.NP_LAYERS]
    ranks = S10L.load_ranks(tok, readouts=readouts, conds=K.CONDS); log('ranks loaded', len(tok), 'rows x', len(ranks), 'arrays')
    LT = lens_table(tok, ranks, K.NP_LAYERS, K.NP_LENS_READOUTS)
    LT.to_parquet(OUT / 'lens_perpaper.parquet', index=False); log('lens_perpaper', LT.shape)
    res = hard_check2(LT, papers, full=not a.tiny); res['tiny'] = a.tiny
    (OUT / 'hardcheck2.json').write_text(json.dumps(res, indent=1, default=str))
    bad = [p for p in res['parts'] if p['status'] != 'PASS']
    log(f'HARD CHECK 2 {res["status"]}: {len(res["parts"]) - len(bad)}/{len(res["parts"])} parts pass; per-paper max |diff| {res["perpaper_max_abs_diff"]:.2e} ({res["perpaper_status"]})')
    for p in bad[:10]: log('  FAIL part', json.dumps(p, default=str)[:400])
    try:
        s = LT[(LT.run.isin(['all', 'surname_first'])) & LT.layer.isin(K.NP_HARD2_LAYERS)].merge(papers[[K.PAPER_ID, K.GROUP]], on=K.PAPER_ID)
        log('\n' + s[s[K.GROUP].isin(['target', 'control'])].groupby(['run', 'readout', 'layer', K.GROUP]).spec5.mean().unstack().round(4).to_string())
    except Exception as e: log('WARN summary print failed', repr(e))
    if res['status'] != 'PASS': sys.exit(3)


if __name__ == '__main__':
    main()
