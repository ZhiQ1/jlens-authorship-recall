"""Stage 13 U46 (handbook G4), POST-HOC: describe the two behaviour scores the M3 task runs saved but no analysis used.
raw/task/shard_*.npz (written by 381_stage13.py do_task) hold, per paper:
  year_nlr          mean over the year's answer tokens of log10(1/rank) at the model OUTPUT (layer-63 state -> unembed),
                    teacher-forced after 'In what year was the research paper titled "{t}" published?\\nYear:'
  author_first_nlr  log10(1/rank) of the FIRST token of the first author's name at the output, after
                    'Who are the authors of the paper titled "{t}"?\\nAuthors:' (NaN if the paper has no scored first author)
They have no layer / position dimension (only the output was scored), so per-layer / per-position means do not exist.
Reported: means by cohort group and citation bin, share at rank 1 (nlr = 0), target - control within citation bin
(Stage 10 estimator, bins with >= 10 per group), 95% team-cluster (primary) and paper bootstrap (2,000 draws).
Not pre-registered (prereg.json and addenda do not mention these scores): every number is post-hoc.
Outputs (new): summary_m3/m3_scores_perpaper.csv, summary_m3/m3_scores_summary.csv, reports/m3_scores.md"""
import importlib.util, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; ROOT = B / '381_stage13'; NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def ci(b): return np.nanpercentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.4f} [{lo:+.4f}, {hi:+.4f}]'
def safe(p):
    p = Path(p)
    return p if not p.exists() else p.with_name(f'{p.stem}.{time.strftime("%Y%m%d_%H%M%S")}{p.suffix}')


def cw(cl, seed):
    codes, uniq = pd.factorize(pd.Series(cl))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def strat(x, grp, cbin, Ws, min_n=10):
    cells = []
    for b in np.unique(cbin):
        ia = np.where((cbin == b) & (grp == 'target') & np.isfinite(x))[0]; ib = np.where((cbin == b) & (grp == 'control') & np.isfinite(x))[0]
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum()
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); out = []
    for W in Ws:
        bt = np.zeros(NB)
        for wi, (a, b) in zip(w, cells): bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
        out.append(ci(bt))
    return est, out, len(cells)


def main():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    fs = sorted((ROOT / 'raw/task').glob('shard_*.npz')); rows = []
    for f in fs:
        z = np.load(f); rows.append(pd.DataFrame({'paper_id': z['paper_id'], 'year_nlr': z['year_nlr'], 'author_first_nlr': z['author_first_nlr']}))
    d = pd.concat(rows, ignore_index=True)
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); papers['team'] = team
    d = d.merge(papers.assign(group=papers.group_tight)[['paper_id', 'group', 'citation_bin', 'field', 'year', 'citations', 'team']], on='paper_id', how='left')
    s11 = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].rename(columns={'group': 'stage11_group'})
    d = d.merge(s11, on='paper_id', how='left')
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')[['paper_id', 'split']]; d = d.merge(pairs, on='paper_id', how='left')
    warn = []
    if len(d) != len(papers) or d.paper_id.duplicated().any(): warn.append(f'{len(d)} rows vs {len(papers)} cohort papers; duplicates {int(d.paper_id.duplicated().sum())}')
    p_pp = safe(ROOT / 'summary_m3/m3_scores_perpaper.csv'); d.to_csv(p_pp, index=False)
    S = []; L = ['# Stage 13 U46: the M3 behaviour scores year_nlr and author_first_nlr (POST-HOC)', '',
                 f'Script `~/jlens_work/13_stage13/stage13_m3_scores.py`, run {time.strftime("%Y-%m-%d %H:%M")}. CPU only. **Post-hoc: these scores are not in prereg.json or addenda 1-6; nothing here is confirmatory.**', '',
                 'What was saved (381_stage13.py do_task, M3 task runs, 72 shards): per paper, the teacher-forced score log10(1/rank) at the model OUTPUT of (a) the year tokens after the year prompt (mean over the year\'s tokens), (b) the first token of the first author\'s name after the authors prompt. Rank 1 gives 0; rank 10 gives -1.',
                 'There is no layer or position dimension (only the output was scored), so the requested per-layer / per-position means cannot be given; the task dimension is one score per prompt (no score was saved for the field prompt).',
                 f'Per-paper table: `{p_pp}`.', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    L += ['## 1. Means by cohort group', '', '| score | group | n | mean | share rank 1 | median |', '|---|---|---|---|---|---|']
    for sc in ('year_nlr', 'author_first_nlr'):
        for g, x in [('all', d)] + list(d.groupby('group')):
            v = x[sc].dropna(); S.append(dict(table='by_group', score=sc, group=g, n=len(v), mean=v.mean(), share_rank1=(v == 0).mean(), median=v.median()))
            L.append(f'| {sc} | {g} | {len(v)} | {v.mean():+.4f} | {(v == 0).mean():.3f} | {v.median():+.4f} |')
    L += ['', f'author_first_nlr missing (no scored first author): {int(d.author_first_nlr.isna().sum())} papers.', '',
          '## 2. Means by citation bin, target vs control', '', '| citation bin | year: target | year: control | author: target | author: control | n target / control |', '|---|---|---|---|---|---|']
    for b, x in d.groupby('citation_bin'):
        t, c = x[x.group == 'target'], x[x.group == 'control']
        for sc in ('year_nlr', 'author_first_nlr'):
            S.append(dict(table='by_bin', score=sc, group='target', citation_bin=b, n=t[sc].notna().sum(), mean=t[sc].mean()))
            S.append(dict(table='by_bin', score=sc, group='control', citation_bin=b, n=c[sc].notna().sum(), mean=c[sc].mean()))
        L.append(f'| {b} | {t.year_nlr.mean():+.4f} | {c.year_nlr.mean():+.4f} | {t.author_first_nlr.mean():+.4f} | {c.author_first_nlr.mean():+.4f} | {len(t)} / {len(c)} |')
    L += ['', '## 3. Target - control within citation bin (Stage 10 estimator; bins with >= 30 papers per group for the cohort, >= 10 for the 1,186-paper Stage 11 sample and its tune / test halves)', '',
          '| score | papers | estimate | team CI (primary) | paper CI | bins |', '|---|---|---|---|---|---|']
    subsets = [('all cohort target/control', d)]
    sub11 = d[d.stage11_group.notna()].assign(group=lambda x: x.stage11_group); subsets.append(('Stage 11 sample (1,186)', sub11))
    for sp in ('tune', 'test'): subsets.append((f'pairs.parquet {sp}', sub11[sub11.split == sp]))
    for name, x in subsets:
        x = x.reset_index(drop=True)
        for sc in ('year_nlr', 'author_first_nlr'):
            mn = 30 if name.startswith('all cohort') else 10            # Stage 10 bin rule for the cohort; X4's min_n = 10 for the 1,186 sample
            e, (ct, cp), nb = strat(x[sc].to_numpy(float), x.group.to_numpy(), x.citation_bin.to_numpy(), [cw(x.team.to_numpy(), 461), cw(x.paper_id.to_numpy(), 462)], min_n=mn)
            S.append(dict(table='target_minus_control', score=sc, group=name, n=len(x), mean=e, lo_team=ct[0], hi_team=ct[1], lo_paper=cp[0], hi_paper=cp[1], n_bins=nb))
            L.append(f'| {sc} | {name} | {e:+.4f} | [{ct[0]:+.4f}, {ct[1]:+.4f}] | [{cp[0]:+.4f}, {cp[1]:+.4f}] | {nb} |')
    L += ['', '## 4. Relations (Spearman, all papers)', '']
    from scipy.stats import spearmanr
    lc = np.log10(1 + d.citations.astype(float))
    for a, b, la in (('year_nlr', 'author_first_nlr', 'year score vs author score'), ('year_nlr', None, 'year score vs log citations'), ('author_first_nlr', None, 'author score vs log citations'), ('year_nlr', 'year', 'year score vs publication year')):
        y = lc if b is None else d[b].astype(float); m = d[a].notna() & y.notna(); r = spearmanr(d[a][m], y[m]).statistic
        S.append(dict(table='spearman', score=a, group=la, n=int(m.sum()), mean=r)); L.append(f'- {la}: rho = {r:+.3f} (n = {int(m.sum())})')
    L += ['', '## Reading (post-hoc)', '',
          '- These are output-level behaviour scores under the two M3 prompts; they say how well the model completes the year / first-author token for each title, not where in the layers the information sits.',
          '- Groups (cohort `group_tight`, as Stage 10 uses): target = cannot write the authors (R0/R1) but picks the true author list in 4 of 4 multiple-choice orders; control = R0/R1 and at most 1 of 4 right; guard = writes the authors (R2). An author-score difference is therefore related to how the groups were defined (recognition of the author list), and is a description, not new evidence.',
          '- The groups were not defined from the year, so year target - control is the less circular number; it is still post-hoc.',
          '- Teacher-forced output scores, not generation (addendum 4 wording).']
    p_s = safe(ROOT / 'summary_m3/m3_scores_summary.csv'); pd.DataFrame(S).to_csv(p_s, index=False)
    L.insert(7, f'Summary table: `{p_s}`.')
    p_md = safe(ROOT / 'reports/m3_scores.md'); p_md.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nU46 DONE', p_md)


if __name__ == '__main__':
    main()
