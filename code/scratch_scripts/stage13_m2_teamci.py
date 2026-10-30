"""Stage 13 M2: team-cluster bootstrap intervals (prereg addendum 2, "intervals"; user decision U45, 2026-10-30).

stage13_cpu.m2() did not save the held-out predictions, so they are recomputed here with exactly the same setup
(same residuals, targets, folds, alpha grid, ridge_cv; SPLIT=group by default = summary_cpu_group/M2_probes.csv) and
saved this time (preds/*.npz). The label-shuffle control is not rerun (its value is copied from the original table).
Point estimates are checked against the original table (abs diff reported for every row; any diff > 1e-6 is flagged).

Interval: whole author teams (the same groups as the probe folds: stage13_cpu.group_folds(lab_ids)[1]) are drawn with
replacement (multinomial, as stage13_cluster_ci.team_weights), each paper enters as many times as its team was drawn,
and the original metric() is recomputed; NB=2000, fixed seed (same draws for every layer/position of one sample).
Original interval: per-paper bootstrap, 200 draws (stage13_cpu.boot).

Null level for "above chance": R^2 -> 0; AUROC within bin -> 0.5; field accuracy -> majority-class share of the labels.

Env: SPLIT=group|paper (default group), TINY=1 (first layer per position, NB=50, output to summary_cpu_teamci_tiny2/; folds from folds_group.npz, made by the 'folds' mode).
Outputs: 381_stage13/summary_cpu_teamci/M2_teamci.csv, preds/, reports/m2_teamci.md (tiny: ..._tiny2)
"""
import importlib.util, os, time
from pathlib import Path
import numpy as np, pandas as pd

SPLIT = os.environ.get('SPLIT', 'group'); TINY = os.environ.get('TINY') == '1'
NB = 50 if TINY else 2000; SEED = 20261030
H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
ROOT = BASE / '381_stage13'
ORIG = ROOT / ('summary_cpu_group' if SPLIT == 'group' else 'summary_cpu') / 'M2_probes.csv'
OUT = ROOT / ('summary_cpu_teamci' + ('' if SPLIT == 'group' else '_papersplit') + ('_tiny2' if TINY else ''))
REP = ROOT / 'reports' / ('m2_teamci' + ('' if SPLIT == 'group' else '_papersplit') + ('_tiny2' if TINY else '') + '.md')
(OUT / 'preds').mkdir(parents=True, exist_ok=True)


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


os.environ['SPLIT'] = SPLIT                                    # c13 reads SPLIT at import (only to name its own output dir)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')


def team_index_draws(g, seed):
    """list of NB index arrays: teams drawn with replacement (multinomial), each paper repeated by its team's count."""
    codes, uniq = pd.factorize(pd.Series(g)); n = len(uniq)
    cnt = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB)
    base = np.arange(len(g))
    return [np.repeat(base, c[codes]) for c in cnt]


def team_ci(kind, y, p, extra, draws):
    v = [c13.metric(kind, y[i], p[i], None if extra is None else extra[i]) for i in draws]
    return np.percentile(v, [2.5, 97.5])


def null_level(kind, Y):
    if kind == 'r2': return 0.0
    if kind == 'auc_bin': return 0.5
    return float(Y.mean(0).max())                               # majority-class share


FOLDS = BASE / '381_stage13/summary_cpu_teamci/folds_group.npz'


def export_folds():
    """group_folds() breaks ties between equal-size groups with an unstable sort (pandas value_counts), whose order
    differs between CPU types (tiny test on d0026/cascadelake gave a different fold assignment with the same team
    partition). The original group run (d0139) is reproduced on c0622 (E5-2680 v4): run `... stage13_m2_teamci.py folds`
    on such a node; the job then loads these folds. Checked: year-only baseline R^2 equals the original table exactly."""
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); donor = ft[ft.k == 0].set_index('paper_id').donor_paper_id
    out = {}
    for cond in ('true', 'false_0'):
        pid = np.concatenate([np.load(f)['resid_paper_id'] for f in sorted((R11 / 'raw/titlepos' / cond).glob('shard_*.npz'))])
        lab = pid if cond == 'true' else np.array([donor[p] for p in pid])
        f, g = c13.group_folds(lab); out[cond + '_pid'] = pid; out[cond + '_fold'] = f; out[cond + '_team'] = g
    FOLDS.parent.mkdir(parents=True, exist_ok=True); np.savez(FOLDS, **out); log('folds saved', FOLDS)


def load_folds(cond, pid, lab_ids):
    if SPLIT == 'paper':
        return np.random.default_rng(13).integers(0, 5, len(pid)), c13.group_folds(lab_ids)[1]
    z = np.load(FOLDS); assert (z[cond + '_pid'] == pid).all(), 'paper order differs from saved folds'
    return z[cond + '_fold'], z[cond + '_team']


def run():
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); P = papers.set_index('paper_id')
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); donor = ft[ft.k == 0].set_index('paper_id').donor_paper_id
    def loadc(c):
        zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))]
        return np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]), zs[0]['probe_layers']
    fields = sorted(papers.field.unique()); rows = []
    for cond in ('true', 'false_0'):
        Xt, Xc, pid, pl = loadc(cond); log('loaded', cond, Xt.shape, Xc.shape)
        lab_ids = pid if cond == 'true' else np.array([donor[p] for p in pid])
        L = P.loc[lab_ids]; T = P.loc[pid]
        y_field = np.eye(len(fields))[[fields.index(f) for f in L.field]]
        y_year = pd.to_numeric(L.year, errors='coerce').to_numpy(float)[:, None]
        y_cit = np.log10(pd.to_numeric(L.citations, errors='coerce').fillna(0).to_numpy(float) + 1)[:, None]
        grp = T.group_tight.to_numpy(); keep_r = np.isin(grp, ['target', 'control'])
        y_rec = (grp == 'target').astype(float)[:, None]; bins = T.citation_bin.to_numpy()
        folds, teams = load_folds(cond, pid, lab_ids)
        yr_t = pd.to_numeric(T.year, errors='coerce').to_numpy(float)
        Yd = np.eye(40)[np.clip(((np.nan_to_num(yr_t, nan=2000) - 1820) // 5).astype(int), 0, 39)]
        def resid_on_year(Y):
            f = np.random.default_rng(13).integers(0, 5, len(Y)); p, _ = c13.ridge_cv(Yd, Y, f); return Y - p
        targets = [('field', 'acc', y_field, None, slice(None)), ('year', 'r2', y_year, None, ~np.isnan(y_year[:, 0])),
                   ('log citations', 'r2', y_cit, None, slice(None)), ('log citations | year removed', 'r2', resid_on_year(y_cit), None, slice(None))]
        if cond == 'true': targets.append(('recognised (target vs control)', 'auc_bin', y_rec, bins, keep_r))
        draws = {}
        def get_draws(name, sel):
            k = 'all' if isinstance(sel, slice) else name
            if k not in draws: draws[k] = team_index_draws(teams[sel], SEED)
            return draws[k]
        def do(pos, l, name, kind, Y, extra, sel, Xs):
            f = OUT / 'preds' / f"{cond}__{pos.replace(' ', '_')}__L{l}__{name.split(' ')[0]}{'_resid' if 'removed' in name else ''}.npz"
            Ys = Y[sel]; ex = None if extra is None else extra[sel]
            if f.exists(): p = np.load(f)['pred']; a = float(np.load(f)['alpha'])
            else:
                p, a = c13.ridge_cv(Xs, Ys, folds[sel]); np.savez(f, pred=p, y=Ys, paper_id=pid[sel], label_paper_id=lab_ids[sel], fold=folds[sel], team=teams[sel], alpha=np.nan if a is None else a)
            yv = Ys if kind == 'acc' else Ys[:, 0]; pv = p if kind == 'acc' else p[:, 0]
            v = c13.metric(kind, yv, pv, ex); lo, hi = team_ci(kind, yv, pv, ex, get_draws(name, sel))
            rows.append(dict(condition=cond, position=pos, layer=int(l), target=name, metric=kind, value_new=v, lo_team=lo, hi_team=hi,
                             null=null_level(kind, Ys), n=len(Ys), n_teams=len(np.unique(teams[sel])), alpha_new=a))
        for name, kind, Y, extra, sel in targets[2:]:
            do('year-only baseline', -1, name, kind, Y, extra, sel, Yd[sel])
        for pos, X, layers in (('title', Xt, list(pl)), ('colon', Xc, list(pl) + [63])):
            if TINY: layers = layers[:1]
            for li, l in enumerate(layers):
                Xl = X[:, li].astype(np.float32)
                for name, kind, Y, extra, sel in targets: do(pos, l, name, kind, Y, extra, sel, Xl[sel])
                log(cond, pos, l, ' '.join(f"{r['target'][:6]}={r['value_new']:.3f}[{r['lo_team']:.3f},{r['hi_team']:.3f}]" for r in rows[-len(targets):]))
                pd.DataFrame(rows).to_csv(OUT / 'M2_teamci_partial.csv', index=False)
        del Xt, Xc
    return pd.DataFrame(rows)


def compare(N):
    O = pd.read_csv(ORIG); k = ['condition', 'position', 'layer', 'target']
    D = N.merge(O[k + ['value', 'lo', 'hi', 'shuffled', 'alpha', 'n', 'note']].rename(columns={'n': 'n_orig', 'lo': 'lo_paper', 'hi': 'hi_paper', 'value': 'value_orig'}), on=k, how='left')
    D['value_diff'] = D.value_new - D.value_orig
    D['width_paper'] = D.hi_paper - D.lo_paper; D['width_team'] = D.hi_team - D.lo_team; D['width_ratio'] = D.width_team / D.width_paper
    def ex(lo, hi, ref): return (lo > ref) | (hi < ref)
    D['excl0_paper'] = ex(D.lo_paper, D.hi_paper, 0.0); D['excl0_team'] = ex(D.lo_team, D.hi_team, 0.0)
    D['above_null_paper'] = D.lo_paper > D.null; D['above_null_team'] = D.lo_team > D.null
    has = D.lo_paper.notna()
    D['flip_excl0'] = has & (D.excl0_paper != D.excl0_team); D['flip_above_null'] = has & (D.above_null_paper != D.above_null_team)
    D.to_csv(OUT / 'M2_teamci.csv', index=False)
    mx = D.value_diff.abs().max(); bad = D[D.value_diff.abs() > 1e-6]
    f = lambda x: f'{x:.3f}' if pd.notna(x) else '-'
    L = ['# Stage 13 M2: team-cluster bootstrap vs per-paper bootstrap' + (' (TINY TEST)' if TINY else ''), '',
         f'Folds/table: {"team (summary_cpu_group)" if SPLIT == "group" else "per-paper (summary_cpu)"}; original: {ORIG}', '',
         f'Team interval: author teams (= probe fold groups) resampled with replacement, NB={NB}, seed {SEED}; original: per-paper bootstrap, 200 draws. '
         'Held-out predictions recomputed with the same folds/alpha grid/features and saved under preds/. Null level: R^2 0, AUROC 0.5, field accuracy = majority-class share.', '',
         f'## Point-estimate check: {len(D)} rows, max |new - original| = {mx:.2e}; rows with |diff| > 1e-6: {len(bad)}' + ('  **MISMATCH: see table**' if len(bad) else ' (all match)'), '']
    if len(bad): L += [bad[['condition', 'position', 'layer', 'target', 'value_orig', 'value_new', 'value_diff', 'alpha', 'alpha_new']].to_string(index=False), '']
    W = D[has]
    L += ['## Interval width ratio (team / paper)', '', f'Over all {len(W)} rows with an original interval: mean {W.width_ratio.mean():.2f}, median {W.width_ratio.median():.2f}, min {W.width_ratio.min():.2f}, max {W.width_ratio.max():.2f}.', '',
          W.groupby(['condition', 'position', 'target']).width_ratio.agg(['count', 'mean', 'min', 'max']).round(2).to_string(), '',
          f'## Flips: "interval excludes 0": {int(D.flip_excl0.sum())} rows; "interval above chance (null level)": {int(D.flip_above_null.sum())} rows', '']
    fl = D[D.flip_excl0 | D.flip_above_null]
    if len(fl): L += [fl[['condition', 'position', 'layer', 'target', 'value_new', 'null', 'lo_paper', 'hi_paper', 'lo_team', 'hi_team', 'flip_excl0', 'flip_above_null', 'note']].round(3).to_string(index=False), '']
    else: L += ['None.', '']
    L += ['## All rows', '', '| condition | position | layer | target | metric | value | null | paper CI (200) | team CI (2000) | width ratio | excl 0 paper/team | > null paper/team | flip |', '|---' * 13 + '|']
    for r in D.itertuples():
        L.append(f'| {r.condition} | {r.position} | {r.layer} | {r.target.replace("|", "&#124;")} | {r.metric} | {r.value_new:.3f} | {r.null:.3f} | [{f(r.lo_paper)}, {f(r.hi_paper)}] | [{r.lo_team:.3f}, {r.hi_team:.3f}] | {f(r.width_ratio)} | '
                 f'{"-" if pd.isna(r.lo_paper) else ("Y" if r.excl0_paper else "N")}/{"Y" if r.excl0_team else "N"} | {"-" if pd.isna(r.lo_paper) else ("Y" if r.above_null_paper else "N")}/{"Y" if r.above_null_team else "N"} | '
                 f'{"**FLIP**" if (r.flip_excl0 or r.flip_above_null) else ""} |')
    L += ['', 'Rows marked LEAK in the original note (year at the colon position) are positive controls only. Year-only baseline rows had no original interval.']
    REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L[:40]), flush=True)
    return len(bad)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'folds': export_folds(); raise SystemExit
    log('SPLIT', SPLIT, 'TINY', TINY, 'NB', NB, 'out', OUT)
    nbad = compare(run())
    log('done; point-estimate mismatches:', nbad)
