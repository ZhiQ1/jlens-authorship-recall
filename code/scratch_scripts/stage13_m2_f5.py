"""Stage 13 M2 with all 5 false titles (2026-11-08, user approval; CHK A3 in ~/jlens_work/conclusions_v30_checks.md).

The published M2 false-title parts used false_0 only:
  summary_cpu_group/M2_probes.csv  (stage13_cpu.m2(), SPLIT=group, condition = false_0 rows; job 11443403)
  summary_cpu_teamci/M2_teamci.csv (stage13_m2_teamci.py, false_0 rows; job 11503585)
This NEW file (frozen scripts are not edited) redoes both for one false title per call, with exactly the same setup:
same targets, labels = the donor paper (the paper whose title is in the prompt; false_titles.parquet k), folds =
stage13_cpu.group_folds(donor ids), ridge_cv / metric / boot from stage13_cpu, per-paper bootstrap (200 draws) from the
module rng (seed 3813) in the state it had when the original run reached false_0 (the 'true' run's 95 boot calls are
replayed with the same n, no residuals needed), label-shuffle control (permutation seed = layer index), team-cluster
bootstrap (NB=2000, seed 20261030, as stage13_m2_teamci). Every false_k gets the same rng state as false_0 had.

Residuals: false_0 = 361_stage11/raw/titlepos/false_0 (the published input); false_1..4 = 381_stage13/raw/b1_titlepos5/false_k.
Folds: false_0 = archived folds (stage13_cpu._archived_folds, folds_donor9108_false0_k5s13.npz); false_1..4 have no
archive, so group_folds computes them (JLENS_FOLDS_ARCHIVE=off for that call only; tie order may depend on the CPU) and
they are saved to folds_<title>.npz and reused on any rerun.

Usage:
  stage13_m2_f5.py run --title false_k [--tiny]   -> summary_m2_f5/M2_probes_<title>.csv, M2_teamci_<title>.csv (skip if both exist)
  stage13_m2_f5.py check [--tiny]                  -> hard check: false_0 output vs published rows; reports/m2_f5_hardcheck.md; exit 1 on mismatch
  stage13_m2_f5.py analyse [--tiny]                -> M2_f5_all.csv, M2_f5_mean.csv, reports/m2_f5_report.md
--tiny: first 2 shards, first layer per position, NB=50, outputs to summary_m2_f5_tiny/ and reports/*_tiny.md.
"""
import argparse, importlib.util, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
ROOT = BASE / '381_stage13'
PUB_PROBES = ROOT / 'summary_cpu_group/M2_probes.csv'; PUB_TEAMCI = ROOT / 'summary_cpu_teamci/M2_teamci.csv'
SEED_TEAM = 20261030


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


os.environ['SPLIT'] = 'group'                                     # c13 reads SPLIT at import (only names its own output dir)
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
COLS = load(H / '13_stage13/stage13_b2A_cols_v2.py', 'b2A_cols_v2')   # project column module: KS, CONDS ('false_k'), NP_FALSE_MEAN5
TITLES = [c for c in COLS.CONDS if c != 'true']
PROBE_COLS = list(pd.read_csv(PUB_PROBES, nrows=1).columns)          # same columns as the published tables (+ 'title')
TEAMCI_COLS = list(pd.read_csv(PUB_TEAMCI, nrows=1).columns)
KEY = ['condition', 'position', 'layer', 'target']


def outdir(tiny): d = ROOT / ('summary_m2_f5' + ('_tiny' if tiny else '')); (d / 'preds').mkdir(parents=True, exist_ok=True); return d


def repfile(name, tiny): return ROOT / 'reports' / (name + ('_tiny' if tiny else '') + '.md')


# ---------------------------------------------------------------- copied from stage13_m2_teamci.py (importing it would run its own setup)
def team_index_draws(g, seed, NB):
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
    return float(Y.mean(0).max())


# ---------------------------------------------------------------- inputs
def shard_dir(title):
    return R11 / 'raw/titlepos/false_0' if title == 'false_0' else ROOT / 'raw/b1_titlepos5' / title


def load_resid(title, tiny):
    fs = sorted(shard_dir(title).glob('shard_*.npz'))
    if tiny: fs = fs[:2]
    zs = [np.load(f) for f in fs]
    pid = np.concatenate([z['resid_paper_id'] for z in zs])
    return np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), pid, zs[0]['probe_layers'], len(fs)


def advance_rng_as_true_run(P, n_layers):
    """replay the per-paper bootstrap draws that stage13_cpu.m2() made in the 'true' run before it reached false_0:
    for each of the n_layers (title 9 + colon 10) x 5 targets (field, year, log cit, log cit | year, recognised):
    200 x rng.integers(0, n, n). Only n matters."""
    pid = np.concatenate([np.load(f)['resid_paper_id'] for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))])
    T = P.loc[pid]
    n_all = len(pid); n_year = int((~np.isnan(pd.to_numeric(T.year, errors='coerce').to_numpy(float))).sum())
    n_rec = int(np.isin(T.group_tight.to_numpy(), ['target', 'control']).sum())
    ns = [n_all, n_year, n_all, n_all, n_rec]
    for _ in range(n_layers):
        for n in ns:
            for _ in range(200): c13.rng.integers(0, n, n)
    log('rng advanced as the true run:', n_layers, 'layers x', ns)


def get_folds(title, pid, lab_ids, f_npz, tiny):
    if f_npz.exists():
        z = np.load(f_npz, allow_pickle=True); assert (z['pid'] == pid).all() and (z['lab'] == lab_ids).all(), 'saved folds: row order differs'
        log('folds loaded', f_npz.name); return z['fold'], z['team']
    if title == 'false_0' and not tiny:
        fold, team = c13.group_folds(lab_ids)                         # archive (same folds as the published run)
    else:
        old = os.environ.get('JLENS_FOLDS_ARCHIVE'); os.environ['JLENS_FOLDS_ARCHIVE'] = 'off'
        try: fold, team = c13.group_folds(lab_ids)
        finally:
            if old is None: del os.environ['JLENS_FOLDS_ARCHIVE']
            else: os.environ['JLENS_FOLDS_ARCHIVE'] = old
    np.savez(f_npz, pid=pid, lab=lab_ids, fold=fold, team=team); log('folds computed and saved', f_npz.name, 'teams', len(np.unique(team)))
    return fold, team


# ---------------------------------------------------------------- run one false title
def run(title, tiny):
    D = outdir(tiny); fp, ft_ = D / f'M2_probes_{title}.csv', D / f'M2_teamci_{title}.csv'
    if fp.exists() and ft_.exists(): log('SKIP (done):', fp.name, ft_.name); return
    k = int(title.split('_')[1]); NB = 50 if tiny else 2000
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); P = papers.set_index('paper_id')
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); donor = ft[ft.k == k].set_index('paper_id').donor_paper_id
    Xt, Xc, pid, pl, nsh = load_resid(title, tiny); log('loaded', title, shard_dir(title), nsh, 'shards', Xt.shape, Xc.shape)
    assert len(np.unique(pid)) == len(pid), 'duplicate paper ids in residual shards'
    if not tiny: assert len(pid) == len(papers), f'expected {len(papers)} rows, got {len(pid)}'
    layers_pos = [('title', Xt, list(pl)), ('colon', Xc, list(pl) + [63])]
    advance_rng_as_true_run(P, sum(len(l) for _, _, l in layers_pos))
    if tiny: layers_pos = [(a, b, c[:1]) for a, b, c in layers_pos]
    cond = title
    lab_ids = np.array([donor[p] for p in pid])                           # the paper whose title is in the prompt
    L = P.loc[lab_ids]; T = P.loc[pid]
    fields = sorted(papers.field.unique())
    y_field = np.eye(len(fields))[[fields.index(f) for f in L.field]]
    y_year = pd.to_numeric(L.year, errors='coerce').to_numpy(float)[:, None]
    y_cit = np.log10(pd.to_numeric(L.citations, errors='coerce').fillna(0).to_numpy(float) + 1)[:, None]
    folds, teams = get_folds(title, pid, lab_ids, D / f'folds_{title}.npz', tiny)
    yr_t = pd.to_numeric(T.year, errors='coerce').to_numpy(float)                   # year shown in the prompt (target paper's)
    Yd = np.eye(40)[np.clip(((np.nan_to_num(yr_t, nan=2000) - 1820) // 5).astype(int), 0, 39)]
    def resid_on_year(Y):
        f = np.random.default_rng(13).integers(0, 5, len(Y)); p, _ = c13.ridge_cv(Yd, Y, f); return Y - p
    targets = [('field', 'acc', y_field, None, slice(None)), ('year', 'r2', y_year, None, ~np.isnan(y_year[:, 0])),
               ('log citations', 'r2', y_cit, None, slice(None)), ('log citations | year removed', 'r2', resid_on_year(y_cit), None, slice(None))]
    rows, trows, draws = [], [], {}
    pdir = D / 'preds' / title; pdir.mkdir(parents=True, exist_ok=True)
    def get_draws(name, sel):
        kk = 'all' if isinstance(sel, slice) else name
        if kk not in draws: draws[kk] = team_index_draws(teams[sel], SEED_TEAM, NB)
        return draws[kk]
    def fit(tag, Xs, Ys, fs, shuffle_seed=None):
        """held-out predictions (+ label-shuffled predictions), cached per unit so a rerun skips finished fits."""
        f = pdir / f'{tag}.npz'
        if f.exists():
            z = np.load(f); return z['pred'], (None if np.isnan(z['alpha']) else float(z['alpha'])), (z['pred_sh'] if shuffle_seed is not None else None)
        p, a = c13.ridge_cv(Xs, Ys, fs); ps = None
        if shuffle_seed is not None:
            sh = np.random.default_rng(shuffle_seed).permutation(len(Ys)); ps, _ = c13.ridge_cv(Xs, Ys[sh], fs)
        np.savez(f, pred=p, alpha=np.nan if a is None else a, pred_sh=ps if ps is not None else np.zeros(0))
        return p, a, ps
    def team_row(pos, l, name, kind, Ys, yv, pv, ex, sel, a, v):
        lo, hi = team_ci(kind, yv, pv, ex, get_draws(name, sel))
        trows.append(dict(condition=cond, position=pos, layer=int(l), target=name, metric=kind, value_new=v, lo_team=lo, hi_team=hi,
                          null=null_level(kind, Ys), n=len(Ys), n_teams=len(np.unique(teams[sel])), alpha_new=a))
    for name, kind, Y, extra, sel in targets[2:]:                         # year-only baseline (no per-paper interval in the original)
        Ys = Y[sel]; ex = None if extra is None else extra[sel]
        p, a, _ = fit(f"baseline__{name.split(' ')[0]}{'_resid' if 'removed' in name else ''}", Yd[sel], Ys, folds[sel])
        v = c13.metric(kind, Ys[:, 0], p[:, 0], ex)
        rows.append(dict(condition=cond, position='year-only baseline', layer=-1, target=name, metric=kind, value=v,
                         lo=np.nan, hi=np.nan, shuffled=np.nan, alpha=np.nan, n=len(Ys), year_in_context=True, note='predictor = 5-year bin of the year in the prompt'))
        team_row('year-only baseline', -1, name, kind, Ys, Ys[:, 0], p[:, 0], ex, sel, a, v)
    for pos, X, layers in layers_pos:
        for li, l in enumerate(layers):
            Xl = X[:, li].astype(np.float32)
            for name, kind, Y, extra, sel in targets:
                Ys, Xs = Y[sel], Xl[sel]; ex = None if extra is None else extra[sel]; fs = folds[sel]
                p, a, ps = fit(f"{pos}__L{l}__{name.split(' ')[0]}{'_resid' if 'removed' in name else ''}", Xs, Ys, fs, shuffle_seed=li)
                yv = Ys if kind == 'acc' else Ys[:, 0]; pv = p if kind == 'acc' else p[:, 0]
                v = c13.metric(kind, yv, pv, ex); lo, hi = c13.boot(kind, yv, pv, ex)
                sh = np.random.default_rng(li).permutation(len(Ys))
                vs = c13.metric(kind, yv[sh], ps if kind == 'acc' else ps[:, 0], ex)
                leak = pos == 'colon' and name == 'year'
                rows.append(dict(condition=cond, position=pos, layer=int(l), target=name, metric=kind, value=v, lo=lo, hi=hi, shuffled=vs, alpha=a, n=len(Ys),
                                 year_in_context=(pos == 'colon'), note='LEAK: year is in the prompt before this position (positive control)' if leak else ''))
                team_row(pos, l, name, kind, Ys, yv, pv, ex, sel, a, v)
            log(title, pos, l, ' '.join(f"{r['target'][:6]}={r['value']:.3f}" for r in rows[-len(targets):]),
                '| team', ' '.join(f"[{r['lo_team']:.3f},{r['hi_team']:.3f}]" for r in trows[-len(targets):]))
            pd.DataFrame(rows).to_csv(D / f'M2_probes_{title}.partial.csv', index=False)
    del Xt, Xc
    O = pd.DataFrame(rows)[PROBE_COLS]; O.insert(0, 'title', title)
    N = pd.DataFrame(trows)
    # same derived columns as stage13_m2_teamci.compare(); the "original" is this title's own per-paper table
    Dd = N.merge(O[KEY + ['value', 'lo', 'hi', 'shuffled', 'alpha', 'n', 'note']].rename(columns={'n': 'n_orig', 'lo': 'lo_paper', 'hi': 'hi_paper', 'value': 'value_orig'}), on=KEY, how='left')
    Dd['value_diff'] = Dd.value_new - Dd.value_orig
    Dd['width_paper'] = Dd.hi_paper - Dd.lo_paper; Dd['width_team'] = Dd.hi_team - Dd.lo_team; Dd['width_ratio'] = Dd.width_team / Dd.width_paper
    def ex_(lo, hi, ref): return (lo > ref) | (hi < ref)
    Dd['excl0_paper'] = ex_(Dd.lo_paper, Dd.hi_paper, 0.0); Dd['excl0_team'] = ex_(Dd.lo_team, Dd.hi_team, 0.0)
    Dd['above_null_paper'] = Dd.lo_paper > Dd.null; Dd['above_null_team'] = Dd.lo_team > Dd.null
    has = Dd.lo_paper.notna()
    Dd['flip_excl0'] = has & (Dd.excl0_paper != Dd.excl0_team); Dd['flip_above_null'] = has & (Dd.above_null_paper != Dd.above_null_team)
    Dd = Dd[TEAMCI_COLS]; Dd.insert(0, 'title', title)
    tmp = fp.with_suffix('.tmp'); O.to_csv(tmp, index=False); tmp.rename(fp)
    tmp = ft_.with_suffix('.tmp'); Dd.to_csv(tmp, index=False); tmp.rename(ft_)
    log('saved', fp, ft_, len(O), 'probe rows', len(Dd), 'team rows; max |value_new - value_orig|', float(Dd.value_diff.abs().max()))


# ---------------------------------------------------------------- hard check: false_0 vs published
def check(tiny):
    D = outdir(tiny); tol = 1e-9; L = ['# M2 five false titles: hard check (false_0 recomputed vs published)' + (' (TINY: mismatches expected)' if tiny else ''), '']
    ok = True
    for name, pub, new, num, txt in (
            ('M2_probes', PUB_PROBES, D / 'M2_probes_false_0.csv', ['value', 'lo', 'hi', 'shuffled', 'alpha', 'n'], ['metric', 'year_in_context', 'note']),
            ('M2_teamci', PUB_TEAMCI, D / 'M2_teamci_false_0.csv',
             ['value_new', 'lo_team', 'hi_team', 'null', 'n', 'n_teams', 'alpha_new', 'value_orig', 'lo_paper', 'hi_paper', 'shuffled', 'alpha', 'n_orig',
              'width_paper', 'width_team', 'width_ratio'],
             ['metric', 'note', 'excl0_paper', 'excl0_team', 'above_null_paper', 'above_null_team', 'flip_excl0', 'flip_above_null'])):
        O = pd.read_csv(pub); O = O[O.condition == 'false_0']; N = pd.read_csv(new).drop(columns='title')
        M = O.merge(N, on=KEY, how='outer', suffixes=('_pub', '_new'), indicator=True)
        miss = int((M._merge != 'both').sum()); L += [f'## {name}: published false_0 rows {len(O)}, recomputed {len(N)}, unmatched keys {miss}', '']
        if miss: ok = False
        M = M[M._merge == 'both']
        L += ['| column | max abs diff | rows equal bit-for-bit | rows > 1e-9 |', '|---|---|---|---|']
        for c in num:
            a, b = M[c + '_pub'].astype(float).to_numpy(), M[c + '_new'].astype(float).to_numpy()
            both_nan = np.isnan(a) & np.isnan(b); one_nan = np.isnan(a) ^ np.isnan(b)
            d = np.where(both_nan, 0.0, np.abs(a - b)); d[one_nan] = np.inf
            nbad = int((d > tol).sum()); ok &= nbad == 0
            L.append(f'| {c} | {np.nanmax(d) if len(d) else 0:.3e} | {int(((a == b) | both_nan).sum())}/{len(d)} | {nbad} |')
        for c in txt:
            a, b = M[c + '_pub'].astype(str).replace('nan', ''), M[c + '_new'].astype(str).replace('nan', '')
            nbad = int((a != b).sum()); ok &= nbad == 0; L.append(f'| {c} (text) | - | {len(M) - nbad}/{len(M)} | {nbad} |')
        L.append('')
    L += [f'**Result: {"PASS" if ok else "FAIL"}** (tolerance {tol} on every numeric column, exact on text/boolean columns).']
    repfile('m2_f5_hardcheck', tiny).write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)
    return ok


# ---------------------------------------------------------------- analysis over the 5 titles
TOL_SAME = 0.02      # written rule for the report: |five-title mean - false_0| <= 0.02 -> unchanged


def analyse(tiny):
    D = outdir(tiny)
    have = [t for t in TITLES if (D / f'M2_probes_{t}.csv').exists() and (D / f'M2_teamci_{t}.csv').exists()]
    if not tiny: assert have == TITLES, f'missing titles: {sorted(set(TITLES) - set(have))}'
    A = pd.concat([pd.read_csv(D / f'M2_probes_{t}.csv') for t in have]); Tm = pd.concat([pd.read_csv(D / f'M2_teamci_{t}.csv') for t in have])
    A.to_csv(D / 'M2_probes_f5_all.csv', index=False); Tm.to_csv(D / 'M2_teamci_f5_all.csv', index=False)
    J = A.merge(Tm[['title'] + KEY + ['lo_team', 'hi_team', 'null', 'n_teams', 'above_null_team', 'excl0_team']], on=['title'] + KEY)
    k = ['position', 'layer', 'target', 'metric']
    W = J.pivot_table(index=k, columns='title', values='value').reindex(columns=have)
    M = W.copy(); M[COLS.NP_FALSE_MEAN5] = W.mean(1); M['min5'] = W.min(1); M['max5'] = W.max(1); M['sd5'] = W.std(1, ddof=1)
    M['mean5_minus_false_0'] = M[COLS.NP_FALSE_MEAN5] - W['false_0']
    M['titles_lo_team_above_null'] = J.assign(a=J.lo_team > J.null).groupby(k).a.sum()
    M['n_titles'] = W.notna().sum(1)
    tr = pd.read_csv(PUB_PROBES); tr = tr[tr.condition == 'true'].set_index(k).value.rename('true_published')
    M = M.join(tr); M['true_minus_mean5'] = M.true_published - M[COLS.NP_FALSE_MEAN5]; M['true_minus_false_0'] = M.true_published - W['false_0']
    M = M.reset_index(); M.to_csv(D / 'M2_f5_mean.csv', index=False)
    def verdict(d, higher_is_stronger=True):
        if pd.isna(d): return 'n/a'
        if abs(d) <= TOL_SAME: return 'unchanged'
        return 'stronger' if (d > 0) == higher_is_stronger else 'weaker'
    def g(pos, l, t): r = M[(M.position == pos) & (M.layer == l) & (M.target == t)]; return None if r.empty else r.iloc[0]
    f3 = lambda x: f'{x:.3f}'
    L = ['# M2 with five false titles (false_0 … false_4)' + (' — TINY TEST' if tiny else ''), '',
         f'Titles: {", ".join(have)}. Labels = the paper whose title is in the prompt (donor of false_k). Same probes, folds rule, intervals as the published false_0 run '
         '(stage13_m2_f5.py; hard check: reports/m2_f5_hardcheck.md). Five-title mean = plain mean of the 5 per-title values (each title has its own donor-team folds and intervals).',
         f'Rule used for "unchanged / weaker / stronger": |five-title mean − false_0| ≤ {TOL_SAME} → unchanged; otherwise stronger if the readout is higher '
         '(more readable), weaker if lower. For "above chance" claims: count of titles whose team-cluster interval lower bound is above the null level.', '',
         'Tables: summary_m2_f5/M2_f5_mean.csv (per title, mean, min, max, true-title value), M2_probes_f5_all.csv, M2_teamci_f5_all.csv.', '',
         '## Published conclusions vs five-title mean', '',
         '| # | published conclusion (false_0) | false_0 | five-title mean [min, max] | titles with team CI above null | verdict |', '|---|---|---|---|---|---|']
    checks = [('false-title runs read the donor (title paper) year: title L48 R² 0.535', 'title', 48, 'year'),
              ('donor citations: title L48 R² 0.488', 'title', 48, 'log citations'),
              ('donor citations with year removed: title L48', 'title', 48, 'log citations | year removed'),
              ('donor year, title L16', 'title', 16, 'year'),
              ('donor field accuracy, title L48', 'title', 48, 'field'),
              ('donor year, title L52 (true-title peak layer)', 'title', 52, 'year')]
    for i, (txt, pos, l, t) in enumerate(checks, 1):
        r = g(pos, l, t)
        if r is None: L.append(f'| {i} | {txt} | - | (layer not run) | - | n/a |'); continue
        L.append(f'| {i} | {txt} | {f3(r.false_0)} | {f3(r[COLS.NP_FALSE_MEAN5])} [{f3(r.min5)}, {f3(r.max5)}] | {int(r.titles_lo_team_above_null)}/{int(r.n_titles)} | {verdict(r.mean5_minus_false_0)} |')
    Ti = M[(M.position == 'title') & (M.target != 'recognised (target vs control)')]
    if len(Ti):
        gap0, gap5 = Ti.true_minus_false_0.abs().max(), Ti.true_minus_mean5.abs().max()
        L.append(f'| {len(checks) + 1} | "still readable, comparable to the true-title run": max |true − false| over title-position rows | {f3(gap0)} | {f3(gap5)} | - | '
                 f'{verdict(-(gap5 - gap0))} (smaller gap = stronger) |')
        allin = int((Ti.titles_lo_team_above_null == Ti.n_titles).sum())
        L.append(f'| {len(checks) + 2} | all title-position false rows above chance (team CI) | {int((J[(J.title == "false_0") & (J.position == "title")].lo_team > J[(J.title == "false_0") & (J.position == "title")].null).sum())}/{int((J[(J.title == "false_0") & (J.position == "title")]).shape[0])} rows | {allin}/{len(Ti)} rows above null for all titles | - | {"unchanged" if allin == len(Ti) else "weaker"} |')
    L += ['', 'True-title conclusions are not recomputed here (true-title runs only): year R² 0.56 (Qwen) vs 0.24 (BERT), recognisable AUROC 0.67 vs 0.63 (BERT), '
          'field accuracy 0.69–0.72, citations 0.28–0.53 → **unchanged by construction**. The M2c BERT baseline and M2b use true-title text only.', '',
          '## Title position: five-title mean (false_0) per layer', '']
    for t in ['field', 'year', 'log citations', 'log citations | year removed']:
        h = M[(M.position == 'title') & (M.target == t)].sort_values('layer')
        if len(h): L.append(f'- {t}: ' + '; '.join(f'L{int(r.layer)} {f3(getattr(r, COLS.NP_FALSE_MEAN5))} ({f3(r.false_0)})' for r in h.itertuples(index=False)))
    L += ['', '## Colon position (year is in the prompt; year row = positive control only)', '']
    for t in ['field', 'year', 'log citations', 'log citations | year removed']:
        h = M[(M.position == 'colon') & (M.target == t)].sort_values('layer')
        if len(h): L.append(f'- {t}: ' + '; '.join(f'L{int(r.layer)} {f3(getattr(r, COLS.NP_FALSE_MEAN5))} ({f3(r.false_0)})' for r in h.itertuples(index=False)))
    L += ['', '## Year-only baseline', '']
    h = M[M.position == 'year-only baseline']
    L += [f'- {r.target}: {f3(getattr(r, COLS.NP_FALSE_MEAN5))} ({f3(r.false_0)})' for r in h.itertuples(index=False)]
    fl = Tm[Tm.flip_excl0 | Tm.flip_above_null]
    L += ['', f'## Team vs per-paper interval flips (all titles): {len(fl)} rows' + (' (false_0 published: 0)' if True else ''), '']
    if len(fl): L.append(fl[['title'] + KEY + ['value_new', 'null', 'lo_paper', 'hi_paper', 'lo_team', 'hi_team']].round(3).to_string(index=False))
    L += ['', 'No interpretation beyond unchanged / weaker / stronger (user instruction 2026-11-08).']
    repfile('m2_f5_report', tiny).write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['run', 'check', 'analyse']); ap.add_argument('--title', choices=TITLES)
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    log('mode', a.mode, 'title', a.title, 'tiny', a.tiny, 'threads', os.environ.get('OMP_NUM_THREADS'), 'host', os.uname().nodename)
    if a.mode == 'run': run(a.title, a.tiny)
    elif a.mode == 'check': sys.exit(0 if check(a.tiny) else 1)
    else: analyse(a.tiny)
