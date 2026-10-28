"""Stage 13 (2026-10-28, review): re-run the Stage 11 title-token probe E4b and its controls (report 6.12, Stage 12 X1)
under 4 configurations, without touching any other line of their code (the original function sources are loaded;
only the fold line is replaced, and two lines are injected after the per-paper 'spec' is formed):
  split  = paper (original seed-11 folds; must reproduce the published numbers) | group (author-team folds)
  excl   = none | title-reuse: drop a test paper A from scoring when the probe saw one of A's prompt titles in training:
           * probe trained on true runs  : A's false title is the TRUE title of a training paper (donor D in training)
           * probe trained on false runs : A's false title is the FALSE title of a training paper (same donor), or
                                           A's true title is the FALSE title of a training paper (A lent its title)
Per-paper results are saved (for the team-cluster bootstrap) and leak diagnostics are reported.
Outputs: 381_stage13/summary_cpu_group/E4b_*.csv, X1controls_*.csv, perpaper_*.parquet, reports/e4b_split_compare.md
"""
import importlib.util, inspect, textwrap
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT = B / '381_stage13'; OUT = ROOT / 'summary_cpu_group'; OUT.mkdir(parents=True, exist_ok=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
ORIG_FOLD = 'fold = np.random.default_rng(11).integers(0, folds, len(pid))'
ft = pd.read_parquet(B / '351_stage10/cohort/conditions/false_titles.parquet'); DONOR = ft[ft.k == 0].set_index('paper_id').donor_paper_id
STATE = {}

def fold_fn(split):
    def f(pid, k):
        fo = np.random.default_rng(11).integers(0, k, len(pid)) if split == 'paper' else c13.group_folds(pid, k=k)[0]
        STATE['pid'] = np.asarray(pid); STATE['fold'] = fo; return fo
    return f

def leak_mask(paper_ids, trained_on):
    """True = drop: the probe saw one of this paper's prompt titles (as an input) in its training folds."""
    pid, fo = STATE['pid'], STATE['fold']; F = dict(zip(pid, fo)); don = DONOR.reindex(pid).to_numpy()
    out = []
    for p in paper_ids:
        k = F[p]; d = DONOR.get(p)
        if trained_on == 'true':
            out.append(d in F and F[d] != k)                                         # A's false title = a training paper's true title
        else:
            tr = fo != k
            out.append(bool(((don == d) & tr).any()) or bool(((don == p) & tr).any()))
    return np.array(out)

def patched(module, fname, split, excl, tag):
    src = textwrap.dedent(inspect.getsource(getattr(module, fname))); assert src.count(ORIG_FOLD) == 1, fname
    new = src.replace(ORIG_FOLD, 'fold = _FOLD(pid, folds)')
    if fname == 'probe':
        anchor = "df['spec'] = df['true'] - df['false']; df = df[df.group_tight.isin(['target', 'control'])]"
        assert new.count(anchor) == 1
        new = new.replace(anchor, anchor + "\n        _HOOK(df, int(l), 'probe (as in Stage 11)')")
    else:
        anchor = "df['spec'] = df[a] - df[b]; e = strat("
        assert new.count(anchor) == 1
        new = new.replace(anchor, "df['spec'] = df[a] - df[b]; _HOOK(df, int(l), name); e = strat(")
    caps = []
    def hook(df, l, name):
        ids = df['paper_id'].to_numpy() if 'paper_id' in df.columns else df.index.to_numpy()
        drop = leak_mask(ids, 'false' if 'FALSE-title' in name else 'true')
        caps.append(pd.DataFrame(dict(paper_id=ids, layer=l, control=name, spec=df['spec'].to_numpy(), dropped=drop)))
        if excl == 'title-reuse': df.loc[df.index[drop], 'spec'] = np.nan
    ns = dict(vars(module)); ns['_FOLD'] = fold_fn(split); ns['_HOOK'] = hook
    exec(compile(new, f'<{fname}:{split}:{excl}>', 'exec'), ns); return ns[fname], caps

r0 = load(H / '10_stage10/stage10_extra_r0r1.py', 'r0'); s12c = load(H / '12_stage12/stage12_cpu.py', 's12c')
papers = pd.read_parquet(B / '351_stage10/cohort/papers.parquet')
ds = pd.read_parquet(B / '351_stage10/summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'group_tight', 'recall_level', 'citation_bin']).drop_duplicates('paper_id')
E, X, PP = [], [], []
for split in ('paper', 'group'):
    for excl in ('none', 'title-reuse'):
        tag = f'{split}_{excl}'; S = OUT / f'tmp_{tag}'; S.mkdir(exist_ok=True)
        r0.rng = np.random.default_rng(3513); r0.a11.rng = np.random.default_rng(3611)
        fn, caps = patched(r0, 'probe', split, excl, tag); fn([], S, ds)
        E.append(pd.read_csv(S / 'E4b_probe_by_recall.csv').assign(split=split, excl=excl))
        s12c.rng = np.random.default_rng(3712); s12c.S = S
        fn2, caps2 = patched(s12c, 'probe_controls', split, excl, tag); fn2(papers)
        X.append(pd.read_csv(S / 'X1_probe_controls.csv').assign(split=split, excl=excl))
        PP.append(pd.concat(caps + caps2).assign(split=split, excl=excl)); print('done', tag, flush=True)
E, X, PP = pd.concat(E), pd.concat(X), pd.concat(PP)
E.to_csv(OUT / 'E4b_4configs.csv', index=False); X.to_csv(OUT / 'X1controls_4configs.csv', index=False); PP.to_parquet(OUT / 'perpaper_probe_spec.parquet', index=False)
f = lambda v, lo, hi: f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
L = ['# E4b and its controls (report 6.12): per-paper vs author-team folds, with and without the title-reuse exclusion', '']
dg = PP[(PP.excl == 'none')].groupby(['split', 'control']).dropped.mean().unstack(0).round(3)
L += ['Share of test papers whose prompt title was seen by the probe in training (title reuse):', '', dg.to_string(), '']
L += ['## E4b: title-specific probe signal, target - control within bin (pooled)', '', '| layer | paper / none | paper / title-reuse dropped | group / none | group / title-reuse dropped |', '|---|---|---|---|---|']
for l in sorted(E.layer.unique()):
    g = lambda s, e: E[(E.layer == l) & (E.split == s) & (E.excl == e)].iloc[0]
    L.append(f'| L{int(l)} | ' + ' | '.join(f(g(s, e).tc_pooled, g(s, e).tc_pooled_lo, g(s, e).tc_pooled_hi) for s, e in (('paper', 'none'), ('paper', 'title-reuse'), ('group', 'none'), ('group', 'title-reuse'))) + ' |')
L += ['', '## Controls: title-specific signal, all papers (spec_all)', '', '| layer | control | paper / none | paper / dropped | group / none | group / dropped |', '|---|---|---|---|---|---|']
for (l, c), _ in X.groupby(['layer', 'control']):
    g = lambda s, e: X[(X.layer == l) & (X.control == c) & (X.split == s) & (X.excl == e)].iloc[0]
    L.append(f'| L{int(l)} | {c} | ' + ' | '.join(f(g(s, e).spec_all, g(s, e).spec_all_lo, g(s, e).spec_all_hi) for s, e in (('paper', 'none'), ('paper', 'title-reuse'), ('group', 'none'), ('group', 'title-reuse'))) + ' |')
pub = pd.read_csv(B / '371_stage12/summary_cpu/X1_probe_controls.csv'); xp = X[(X.split == 'paper') & (X.excl == 'none')].merge(pub, on=['layer', 'control'], suffixes=('', '_pub'))
pe = pd.read_csv(B / '361_stage11/summary_r0r1/E4b_probe_by_recall.csv'); ep = E[(E.split == 'paper') & (E.excl == 'none')].merge(pe, on='layer', suffixes=('', '_pub'))
L += ['', f'Sanity: paper/none controls vs published 6.12, max |diff| spec_all = {np.abs(xp.spec_all - xp.spec_all_pub).max():.4f}; '
          f'paper/none E4b vs published, max |diff| pooled target - control = {np.abs(ep.tc_pooled - ep.tc_pooled_pub).max():.4f}']
(ROOT / 'reports/e4b_split_compare.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
