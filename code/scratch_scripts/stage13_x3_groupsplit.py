"""X3 follow-ups (user 2026-11-01): (1) G' - G'(L4) at title_last split by target / control with team-cluster CIs and
the difference; (2) distribution of the lexical neighbour D's jaccard2 vs the paraphrase's (why only 66 matched).
Reads summary_x3/x3_cos_per_paper.csv.gz and x3_pairs.csv (no recomputation of cosines). Output reports/x3_groupsplit.md."""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd
R = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); S = R / 'summary_x3'
sp = importlib.util.spec_from_file_location('x3', Path.home() / 'jlens_work/13_stage13/stage13_x3_analyze.py'); x3 = importlib.util.module_from_spec(sp); sp.loader.exec_module(x3)
c = pd.read_csv(S / 'x3_cos_per_paper.csv.gz'); c = c[c.pos == 'title_last']
w = c.pivot_table(index=['paper_id', 'layer'], columns='version', values='cos_with_original').reset_index()
w['gp'] = w['paraphrase'] - w['lexical_neighbour']
g = w.pivot(index='paper_id', columns='layer', values='gp'); g = g.sub(g[4], axis=0)
P = pd.read_csv(S / 'x3_pairs.csv').set_index('paper_id')
L = ['# X3: G\'(l) - G\'(L4) at the last title token by target / control; D overlap distribution', '',
     'G\' = cos(orig, para) - cos(orig, lexical neighbour D). Team-cluster bootstrap (pairs team, 2,000 draws, seed 411). Source: summary_x3/x3_cos_per_paper.csv.gz, x3_pairs.csv.', '']
rows = []
for setname, col in (('primary', 'include_primary'), ('sensitivity', 'include_sensitive')):
    for split in ('test', 'all'):
        q = P[P[col].astype(bool) & ((P.split == split) if split != 'all' else True)]
        q = q[q.index.isin(g.index)]
        W = x3.team_w(q.team.values, 411)
        gt = (q.group == 'target').values.astype(float); gc = 1 - gt
        L += [f'## {setname} / {split} (target n = {int(gt.sum())}, control n = {int(gc.sum())})', '',
              '| layer | target | control | target - control |', '|---|---|---|---|']
        for l in (24, 28, 32, 36, 40, 44, 48):
            v = g.loc[q.index, l].values
            def m(mask, ww=None):
                ww = np.ones(len(v)) if ww is None else ww
                return (ww * mask * v).sum(-1) / (ww * mask).sum(-1)
            t, cc = m(gt), m(gc); bt, bc = m(gt, W), m(gc, W); bd = bt - bc
            f = lambda x, b: f'{x:+.3f} [{np.nanpercentile(b, 2.5):+.3f}, {np.nanpercentile(b, 97.5):+.3f}]'
            L.append(f'| L{l} | {f(t, bt)} | {f(cc, bc)} | {f(t - cc, bd)} |')
            rows.append(dict(set=setname, split=split, layer=l, target=t, control=cc, diff=t - cc, diff_lo=np.nanpercentile(bd, 2.5), diff_hi=np.nanpercentile(bd, 97.5)))
        L.append('')
pd.DataFrame(rows).to_csv(S / 'x3_groupsplit.csv', index=False)
q = P[P.include_primary.astype(bool)]
qs = lambda s: ', '.join(f'{k} {s.quantile(k):.3f}' for k in (0.1, 0.25, 0.5, 0.75, 0.9))
L += ['## Why only 66 primary pairs have a matched D', '',
      f'Primary n = {len(q)}. jaccard2(orig, paraphrase) quantiles: {qs(q.para_jaccard2)}.',
      f'jaccard2(orig, D) quantiles: {qs(q.lexical_jaccard2)}; max {q.lexical_jaccard2.max():.3f}.',
      f'Matched (D >= paraphrase): {int(q.d_matched.sum())}. Paraphrase jaccard2 among matched: median {q[q.d_matched.astype(bool)].para_jaccard2.median():.3f}; among unmatched: median {q[~q.d_matched.astype(bool)].para_jaccard2.median():.3f}.',
      f'Share of paraphrases with jaccard2 > 0.3: {(q.para_jaccard2 > 0.3).mean():.3f}; share of D with jaccard2 > 0.3: {(q.lexical_jaccard2 > 0.3).mean():.3f}.', '']
(R / 'reports/x3_groupsplit.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
