"""Stage 13 (2026-10-30, review): E4b title-token probe + its controls (report 6.12) with the standardisation fitted
INSIDE the training folds only.

Same as stage13_e4b_group.py (4 configs: paper / team folds x title-reuse exclusion none / dropped; same folds, same
exclusion rule, same alpha grid and alpha rule (fold 0 held-out MSE), same scoring, same controls, same bootstrap seeds).
The only change: in stage10_extra_r0r1.probe (the E4b probe), the line
    mu, sd = X.mean(0), X.std(0) + 1e-6          # all 9,108 papers, test fold included   (r0r1.py:244; stage11_analyze.py:176)
is removed and, per fold k, mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6 is used for the alpha search, the fit and the
held-out predictions (true and false_0 residuals).
stage12_cpu.probe_controls (the X1 controls) already standardises on the training fold (stage12_cpu.py:143); it is re-run
unchanged, so its numbers must reproduce the originals exactly (a check that nothing else changed).

Env: TINY=1 -> first 16 shards (2,048 papers), layer 24 only, outputs under *_tiny.  STD=all -> keep the original
full-sample standardisation (for checks only).
Outputs: 381_stage13/summary_cpu_trainstd/{E4b_4configs.csv, X1controls_4configs.csv, perpaper_probe_spec.parquet,
compare_*.csv}, reports/e4b_trainstd_compare.md
"""
import importlib.util, inspect, os, textwrap, time
from pathlib import Path
import numpy as np, pandas as pd

TINY = os.environ.get('TINY') == '1'; STD = os.environ.get('STD', 'train'); assert STD in ('train', 'all')
sfx = ('_tiny' if TINY else '') + ('' if STD == 'train' else '_stdall')
H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT = B / '381_stage13'
OUT = ROOT / f'summary_cpu_trainstd{sfx}'; OUT.mkdir(parents=True, exist_ok=True); ORIG = ROOT / 'summary_cpu_group'
REPORT = ROOT / f'reports/e4b_trainstd_compare{sfx}.md'
NSH = 16 if TINY else None; KEEP = (lambda l: int(l) == 24) if TINY else (lambda l: True)
T0 = time.time(); log = lambda *a: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)
log('mode', dict(TINY=TINY, STD=STD, OUT=str(OUT)))

def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
ORIG_FOLD = 'fold = np.random.default_rng(11).integers(0, folds, len(pid))'
STD_ALL = 'XF = Xf[:, li].astype(np.float32); mu, sd = X.mean(0), X.std(0) + 1e-6'
STD_FIT = 'A = (X[tr] - mu) / sd; ym = Y[tr].mean(0)'
STD_X1 = 'mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6'
ft = pd.read_parquet(B / '351_stage10/cohort/conditions/false_titles.parquet'); DONOR = ft[ft.k == 0].set_index('paper_id').donor_paper_id
STATE = {}

def fold_fn(split):
    def f(pid, k):
        fo = np.random.default_rng(11).integers(0, k, len(pid)) if split == 'paper' else c13.group_folds(pid, k=k)[0]
        STATE['pid'] = np.asarray(pid); STATE['fold'] = fo; return fo
    return f

def leak_mask(paper_ids, trained_on):
    """True = drop: the probe saw one of this paper's prompt titles (as an input) in its training folds. (verbatim copy)"""
    pid, fo = STATE['pid'], STATE['fold']; F = dict(zip(pid, fo)); don = DONOR.reindex(pid).to_numpy()
    out = []
    for p in paper_ids:
        k = F[p]; d = DONOR.get(p)
        if trained_on == 'true':
            out.append(d in F and F[d] != k)
        else:
            tr = fo != k
            out.append(bool(((don == d) & tr).any()) or bool(((don == p) & tr).any()))
    return np.array(out)

def rep(s, old, new):
    assert s.count(old) == 1, old; return s.replace(old, new)

def patched(module, fname, split, excl, source):
    src = textwrap.dedent(inspect.getsource(getattr(module, fname)))
    new = rep(src, ORIG_FOLD, 'fold = _FOLD(pid, folds)')
    if fname == 'probe':
        anchor = "df['spec'] = df['true'] - df['false']; df = df[df.group_tight.isin(['target', 'control'])]"
        new = rep(new, anchor, anchor + "\n        _HOOK(df, int(l), 'probe (as in Stage 11)')")
        if STD == 'train':                                   # THE change: per-fold training-set standardisation
            new = rep(new, STD_ALL, 'XF = Xf[:, li].astype(np.float32)')
            new = rep(new, STD_FIT, 'mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; ' + STD_FIT)
    else:
        assert new.count(STD_X1) == 1                         # X1 controls: already training-fold standardisation
        anchor = "df['spec'] = df[a] - df[b]; e = strat("
        new = rep(new, anchor, "df['spec'] = df[a] - df[b]; _HOOK(df, int(l), name); e = strat(")
    new = rep(new, ".glob('shard_*.npz'))]", ".glob('shard_*.npz'))[:_NSH]]")                 # tiny: shard subset
    new = rep(new, 'for li, l in enumerate(players):', 'for li, l in [(i_, l_) for i_, l_ in enumerate(players) if _KEEP(l_)]:')
    caps = []
    def hook(df, l, name):
        ids = df['paper_id'].to_numpy() if 'paper_id' in df.columns else df.index.to_numpy()
        drop = leak_mask(ids, 'false' if 'FALSE-title' in name else 'true')
        caps.append(pd.DataFrame(dict(paper_id=ids, layer=l, control=name, spec=df['spec'].to_numpy(), dropped=drop, source=source)))
        if excl == 'title-reuse': df.loc[df.index[drop], 'spec'] = np.nan
    ns = dict(vars(module)); ns.update(_FOLD=fold_fn(split), _HOOK=hook, _NSH=NSH, _KEEP=KEEP)
    exec(compile(new, f'<{fname}:{split}:{excl}:{STD}>', 'exec'), ns); return ns[fname], caps

r0 = load(H / '10_stage10/stage10_extra_r0r1.py', 'r0'); s12c = load(H / '12_stage12/stage12_cpu.py', 's12c')
papers = pd.read_parquet(B / '351_stage10/cohort/papers.parquet')
ds = pd.read_parquet(B / '351_stage10/summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'group_tight', 'recall_level', 'citation_bin']).drop_duplicates('paper_id')
E, X, PP = [], [], []
for split in ('paper', 'group'):
    for excl in ('none', 'title-reuse'):
        tag = f'{split}_{excl}'; S = OUT / f'tmp_{tag}'; S.mkdir(exist_ok=True)
        r0.rng = np.random.default_rng(3513); r0.a11.rng = np.random.default_rng(3611)
        fn, caps = patched(r0, 'probe', split, excl, 'E4b'); fn([], S, ds)
        E.append(pd.read_csv(S / 'E4b_probe_by_recall.csv').assign(split=split, excl=excl))
        s12c.rng = np.random.default_rng(3712); s12c.S = S
        fn2, caps2 = patched(s12c, 'probe_controls', split, excl, 'X1'); fn2(papers)
        X.append(pd.read_csv(S / 'X1_probe_controls.csv').assign(split=split, excl=excl))
        PP.append(pd.concat(caps + caps2).assign(split=split, excl=excl)); log('done', tag)
E, X, PP = pd.concat(E), pd.concat(X), pd.concat(PP)
E.to_csv(OUT / 'E4b_4configs.csv', index=False); X.to_csv(OUT / 'X1controls_4configs.csv', index=False); PP.to_parquet(OUT / 'perpaper_probe_spec.parquet', index=False)
log('saved', OUT)

# ---------------------------------------------------------------- comparison with the original (summary_cpu_group)
E0 = pd.read_csv(ORIG / 'E4b_4configs.csv'); X0 = pd.read_csv(ORIG / 'X1controls_4configs.csv')
P0 = pd.read_parquet(ORIG / 'perpaper_probe_spec.parquet')
# the original parquet has no 'source' column: within (split, excl, layer, control, paper) the E4b rows come first
P0['source'] = np.where(P0.groupby(['split', 'excl', 'layer', 'control', 'paper_id']).cumcount() == 0, 'E4b', 'X1')
P0.loc[P0.control != 'probe (as in Stage 11)', 'source'] = 'X1'

def allpaper(P):
    """E4b probe, title-specific signal over all (target + control) papers; dropped papers excluded in title-reuse configs.
    Bootstrap over papers, B = 2000, the same seed for the original and the new run of each cell."""
    rows = []
    for (s, e, l), g in P[(P.source == 'E4b')].groupby(['split', 'excl', 'layer']):
        v = g.spec.to_numpy(float); v = v[~np.isnan(v) & ~(g.dropped.to_numpy() & (e == 'title-reuse'))]
        bm = v[np.random.default_rng(int(l) * 7 + 1).integers(0, len(v), (2000, len(v)))].mean(1)
        rows.append(dict(split=s, excl=e, layer=l, spec_all=v.mean(), spec_all_lo=np.percentile(bm, 2.5), spec_all_hi=np.percentile(bm, 97.5), n=len(v)))
    return pd.DataFrame(rows)

def cmp(old, new, keys, cols):
    m = old.merge(new, on=keys, suffixes=('_orig', '_new'))
    out = m[keys].copy()
    for c in cols:
        o, n, ol, oh, nl, nh = (m[f'{c}{x}'] for x in ('_orig', '_new', '_lo_orig', '_hi_orig', '_lo_new', '_hi_new'))
        z0 = (ol <= 0) & (oh >= 0); z1 = (nl <= 0) & (nh >= 0)
        out[f'{c}_orig'], out[f'{c}_new'], out[f'{c}_diff'] = o, n, n - o
        out[f'{c}_orig_ci'] = [f'[{a:+.3f}, {b:+.3f}]' for a, b in zip(ol, oh)]; out[f'{c}_new_ci'] = [f'[{a:+.3f}, {b:+.3f}]' for a, b in zip(nl, nh)]
        out[f'{c}_zero_orig'], out[f'{c}_zero_new'] = z0, z1; out[f'{c}_zero_changed'] = z0 != z1
    return out

ce = cmp(E0, E, ['split', 'excl', 'layer'], ['tc_pooled', 'tc_R0', 'tc_R1', 'CA'])
ce = ce.merge(E0[['split', 'excl', 'layer', 'alpha']].rename(columns={'alpha': 'alpha_orig'}), on=['split', 'excl', 'layer']).merge(
    E[['split', 'excl', 'layer', 'alpha']].rename(columns={'alpha': 'alpha_new'}), on=['split', 'excl', 'layer'])
ca = cmp(allpaper(P0), allpaper(PP), ['split', 'excl', 'layer'], ['spec_all'])
cx = cmp(X0, X, ['split', 'excl', 'layer', 'control'], ['spec_all', 'tc'])
ce.to_csv(OUT / 'compare_E4b.csv', index=False); ca.to_csv(OUT / 'compare_E4b_allpapers.csv', index=False); cx.to_csv(OUT / 'compare_X1.csv', index=False)

# per-paper agreement of the E4b probe signal (before any exclusion)
pk = ['split', 'excl', 'layer', 'paper_id']
pj = P0[(P0.source == 'E4b')][pk + ['spec']].merge(PP[(PP.source == 'E4b')][pk + ['spec']], on=pk, suffixes=('_o', '_n')).dropna()
pa = pj.groupby(['split', 'excl', 'layer']).apply(lambda g: pd.Series(dict(r=np.corrcoef(g.spec_o, g.spec_n)[0, 1], mad=(g.spec_n - g.spec_o).abs().mean(), n=len(g)))).reset_index()

F = lambda v: f'{v:+.4f}'
def table(df, c, extra=()):
    h = '| ' + ' | '.join(list(extra) + ['orig', 'new', 'new - orig', 'orig CI', 'new CI', 'CI contains 0: orig -> new']) + ' |'
    L = [h, '|' + '---|' * (len(extra) + 6)]
    for _, r in df.iterrows():
        z = f"{'yes' if r[c + '_zero_orig'] else 'no'} -> {'yes' if r[c + '_zero_new'] else 'no'}" + (' **CHANGED**' if r[c + '_zero_changed'] else '')
        L.append('| ' + ' | '.join([str(r[e]) for e in extra] + [F(r[c + '_orig']), F(r[c + '_new']), F(r[c + '_diff']), r[c + '_orig_ci'], r[c + '_new_ci'], z]) + ' |')
    return L

conf = lambda d: d[(d.split == 'group') & (d.excl == 'title-reuse')].assign(layer=lambda x: 'L' + x.layer.astype(int).astype(str))
L = ['# E4b with training-fold standardisation vs the original (full-sample standardisation)', '',
     ('**TINY TEST RUN (16 shards = 2,048 papers, layer 24 only): numbers are NOT comparable with the full-cohort original.**\n' if TINY else '') +
     ('**STD=all check run (original standardisation).**\n' if STD == 'all' else ''),
     'Change: E4b probe (stage10_extra_r0r1.probe, the version re-run by stage13_e4b_group.py) used mu, sd = X.mean(0), X.std(0) over all '
     '9,108 papers, test folds included (stage10_extra_r0r1.py:244; same line in stage11_analyze.probe_section:176). Here mu, sd are fitted on '
     'the training folds of each fold (also for the fold-0 alpha search). Folds, exclusion rule, alpha grid, scoring and bootstrap seeds unchanged.',
     'The X1 controls (stage12_cpu.probe_controls) already standardised on the training fold (stage12_cpu.py:143); they are re-run unchanged and '
     'should reproduce the original exactly.', '',
     f'Max |new - orig|: E4b pooled target - control {ce.tc_pooled_diff.abs().max():.4f}; E4b all-paper signal {ca.spec_all_diff.abs().max():.4f}; '
     f'X1 spec_all {cx.spec_all_diff.abs().max():.4f}; X1 target - control {cx.tc_diff.abs().max():.4f}.',
     f'Rows where "CI contains 0" changed: E4b tc_pooled {int(ce.tc_pooled_zero_changed.sum())}/{len(ce)}, tc_R0 {int(ce.tc_R0_zero_changed.sum())}, '
     f'tc_R1 {int(ce.tc_R1_zero_changed.sum())}, C - A {int(ce.CA_zero_changed.sum())}; E4b all-paper {int(ca.spec_all_zero_changed.sum())}/{len(ca)}; '
     f'X1 spec_all {int(cx.spec_all_zero_changed.sum())}/{len(cx)}, X1 tc {int(cx.tc_zero_changed.sum())}/{len(cx)}.',
     f'Alpha changed in {int((ce.alpha_orig != ce.alpha_new).sum())}/{len(ce)} (config, layer) cells.', '',
     '## Confirmatory configuration (author-team folds + title-reuse exclusion)', '',
     '### E4b probe: title-specific signal, all papers (target + control; mean of per-paper spec, paper bootstrap)', '']
L += table(conf(ca), 'spec_all', ['layer'])
L += ['', '### E4b probe: target - control within citation bin (pooled)', '']
L += table(conf(ce), 'tc_pooled', ['layer'])
L += ['', '### Controls (X1), all papers: spec_all', '']
L += table(conf(cx), 'spec_all', ['layer', 'control'])
L += ['', '### Controls (X1): target - control within citation bin', '']
L += table(conf(cx), 'tc', ['layer', 'control'])
L += ['', '## All 4 configurations: E4b pooled target - control', '']
L += table(ce.assign(layer=lambda x: 'L' + x.layer.astype(int).astype(str)), 'tc_pooled', ['split', 'excl', 'layer'])
L += ['', '## All 4 configurations: E4b all-paper signal', '']
L += table(ca.assign(layer=lambda x: 'L' + x.layer.astype(int).astype(str)), 'spec_all', ['split', 'excl', 'layer'])
L += ['', '## Per-paper agreement of the E4b spec (before exclusion): Pearson r and mean |new - orig|', '', pa.round(4).to_string(index=False), '',
      f'Full comparison tables: {OUT}/compare_E4b.csv (also tc_R0, tc_R1, C - A, alpha), compare_E4b_allpapers.csv, compare_X1.csv.']
REPORT.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); log('report', REPORT)
