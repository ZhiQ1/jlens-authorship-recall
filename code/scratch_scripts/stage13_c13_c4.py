"""Addendum 13 item C-4 (2026-11-06): M1 'top-1 token changes with the title' with false_1..false_4.

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-4".
Published M1 (stage13_cpu.m1): per (readout, layer), share of name-token rows whose stored Stage 10 top-1 token differs between
the true-title run and the false_0 run (inner join on row_id; all name tokens). Here the same statistic for each false_k (k = 0..4),
read directly from 351_stage10/raw/[cond_false_k/]<readout>/L<l>/shard_*.npz (top1, row_id), for every (readout, layer) of the
published table; plus mean / min / max over k = 0..4 and the share of rows whose top-1 changes under at least one / all five false titles.
Also split: first token of each name vs later tokens (descriptive).
HARD    the false_0 column reproduces summary_cpu(_group)/M1_title_sensitivity.csv (|diff| <= 1e-12 in every cell).
Usage   stage13_c13_c4.py [--tiny]   (tiny: 3 readout-layers, 4 shards; hard check on the shard subset is not possible, so the
        tiny run checks the code path only and recomputes false_0 on the subset)
"""
import argparse, json, hashlib, sys
from pathlib import Path
import numpy as np, pandas as pd

B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum13.json'; PLAN_SHA = 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e'
ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
OUT = R13 / ('summary_c13/c4_tiny' if a.tiny else 'summary_c13/c4'); OUT.mkdir(parents=True, exist_ok=True)
REP = OUT / 'c13_C4.md' if a.tiny else R13 / 'reports/c13_C4.md'

pub = pd.read_csv(R13 / 'summary_cpu_group/M1_title_sensitivity.csv')
plan = list(pub[['readout', 'layer']].itertuples(index=False, name=None))
shards = range(72)
if a.tiny: plan = [('final', 63), ('jlens_public', 56), ('logit', 24)]; shards = range(4)
nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'token_index']).set_index('row_id').token_index


def top1(cond, ro, l):
    d = R10 / 'raw' / ('' if cond == 'true' else f'cond_{cond}') / ro / f'L{l}'; rid, t = [], []
    for s in shards:
        f = d / f'shard_{s:03d}.npz'
        if not f.exists(): continue
        z = np.load(f); rid.append(z['row_id']); t.append(z['top1'])
    return pd.Series(np.concatenate(t), index=np.concatenate(rid))


rows = []
for ro, l in plan:
    T = top1('true', ro, l); ch = {}
    for k in range(5):
        F = top1(f'false_{k}', ro, l); j = T.to_frame('t').join(F.rename('f'), how='inner')     # as m1(): inner join
        ch[k] = (j.t != j.f)
    C = pd.concat(ch, axis=1, join='inner'); first = (nt.reindex(C.index) == 0).to_numpy()
    r = dict(readout=ro, layer=int(l), n_rows=len(C), **{f'false_{k}': float(ch[k].mean()) for k in range(5)})
    v = np.array([r[f'false_{k}'] for k in range(5)]); r |= dict(mean_0_4=v.mean(), min_0_4=v.min(), max_0_4=v.max(), mean_1_4=v[1:].mean(),
                                                                any_of_5=float(C.any(axis=1).mean()), all_of_5=float(C.all(axis=1).mean()),
                                                                first_tok_mean_0_4=float(C[first].mean().mean()), later_tok_mean_0_4=float(C[~first].mean().mean()),
                                                                n_rows_per_k=[int(len(ch[k])) for k in range(5)])
    rows.append(r); print(ro, l, f'{r["false_0"]:.4f}', f'{r["mean_0_4"]:.4f}', flush=True)
R = pd.DataFrame(rows); R.to_csv(OUT / 'c4_m1_title_sensitivity_5false.csv', index=False)

# HARD CHECK
m = R.merge(pub, on=['readout', 'layer'], how='left'); diff = (m.false_0 - m.share_top1_changes_true_vs_false).abs()
if a.tiny:
    HC = dict(status='TINY (code path only; shard subset cannot equal the published full-cohort value)', max_abs_diff_vs_published=float(diff.max()))
else:
    HC = dict(status='PASS' if (len(m) == len(pub) and diff.max() <= 1e-12) else 'FAIL', n_cells=int(len(m)), n_published=int(len(pub)), max_abs_diff=float(diff.max()),
              published_range=[float(pub.share_top1_changes_true_vs_false.min()), float(pub.share_top1_changes_true_vs_false.max())],
              published_range_L24_48=[float(pub[pub.layer <= 48].share_top1_changes_true_vs_false.min()), float(pub[pub.layer <= 48].share_top1_changes_true_vs_false.max())])
(OUT / 'c4_hardcheck.json').write_text(json.dumps(HC, indent=1)); print('HARD CHECK', HC['status'], flush=True)
if HC['status'] == 'FAIL':
    REP.write_text(f'# C-4: HARD CHECK FAILED (item stopped)\n\n```\n{json.dumps(HC, indent=1)}\n```\n'); sys.exit(2)

pc = lambda x: f'{100 * x:.1f}%'
T = ['# C-4 (addendum 13): M1 top-1 title sensitivity with all five false titles', '',
     ('**TINY TEST (4 shards, 3 readout-layers)**\n' if a.tiny else '') +
     'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...). Share of name-token rows (all 149,999 tokens, all authors) whose stored Stage 10 top-1 token '
     'differs between the true-title run and the false_k run. Published M1 used false_0 only.', '',
     f'## Hard check: {HC["status"]}', '',
     (f'- false_0 column vs published `summary_cpu_group/M1_title_sensitivity.csv` (identical to `summary_cpu/`): {HC["n_cells"]}/{HC["n_published"]} cells, max |diff| {HC["max_abs_diff"]:.1e}. '
      f'Published range {pc(HC["published_range"][0])}-{pc(HC["published_range"][1])} over all cells; {pc(HC["published_range_L24_48"][0])}-{pc(HC["published_range_L24_48"][1])} at L24-L48 (the quoted "28-64%").'
      if not a.tiny else f'- tiny: {HC["status"]}'), '',
     '## Per readout and layer', '',
     '| readout | layer | false_0 (published) | false_1 | false_2 | false_3 | false_4 | mean of 5 | range over 5 | changes under >= 1 of 5 | under all 5 | first token / later tokens (mean of 5) |',
     '|---|---|---|---|---|---|---|---|---|---|---|---|']
for _, x in R.iterrows():
    T.append(f'| {x.readout} | {x.layer} | {pc(x.false_0)} | {pc(x.false_1)} | {pc(x.false_2)} | {pc(x.false_3)} | {pc(x.false_4)} | {pc(x.mean_0_4)} | '
             f'{pc(x.min_0_4)}-{pc(x.max_0_4)} | {pc(x.any_of_5)} | {pc(x.all_of_5)} | {pc(x.first_tok_mean_0_4)} / {pc(x.later_tok_mean_0_4)} |')
dd = (R.mean_1_4 - R.false_0)
T += ['', f'Across the {len(R)} readout-layers: mean of false_1..4 minus false_0 = {dd.mean() * 100:+.2f} pp on average (range {dd.min() * 100:+.2f} to {dd.max() * 100:+.2f} pp); '
      f'largest spread over the 5 titles {(R.max_0_4 - R.min_0_4).max() * 100:.2f} pp.']
REP.write_text('\n'.join(T) + '\n'); print('wrote', REP)
