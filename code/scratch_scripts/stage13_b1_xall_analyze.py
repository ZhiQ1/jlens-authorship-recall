"""Stage 13 batch 1 item 1 analysis (CPU; config/prereg_addendum10.json): X1-X4 for all authors, by author position.

Input: raw/b1_xall/{xpatch,x2,pscope,para}/shard_*.npz (one row per (pair, author)), from stage13_b1_xall.py.
Strata (pair level):
  all    : mean over the paper's authors of every score column (primary, addendum 10)
  first  : author_index 0 (the published scoring; HARD CHECK against the published numbers)
  others : mean over authors with author_index >= 1 (pairs with >= 2 authors)
  last   : author_index = n_authors - 1, pairs with n_authors >= 3
Statistics unchanged from the frozen analyses (formulas copied, the same bootstrap seeds and team draws):
  X1 stage13_x1x4_analyze.x1 (R ratio of means, seed 101, addendum-2 verdict at L >= 24 on test);
  X2 stage13_x2_analyze (carry / remove ratios, seed 101, layer chosen on tune, addendum-6 H2/H3 rule), run twice: with
     the old S_auth (first author, first token; summary_x2) and the new S_auth_all (all authors' tokens; summary_b1_xall);
  X3 stage13_x3_recovery.recovery (behaviour recovery, seeds of stage13_x3_analyze) and stage13_x3_analyze.beh_rows;
  X4 stage13_x1x4_analyze.x4, author answer only (D seed 202, earliest layer tune -> test, recognition seed 303 + l).
HARD CHECK (addendum 10): first stratum vs published CSVs, |diff| <= 0.005 on every point estimate compared; plus
per-pair first-author scores vs the frozen raw data. With --partial the frozen raw data are restricted to the shards
present in the new data and the same functions are applied to both (one-shard gate before the remaining jobs).
Usage: python stage13_b1_xall_analyze.py [--tiny] [--partial]
Outputs: summary_b1_xall/*.csv, reports/b1_xall_report.md (partial: summary_b1_xall/partial/, reports/b1_xall_partial_check.md)"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

TINY = '--tiny' in sys.argv; PARTIAL = '--partial' in sys.argv
H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT0 = B / '381_stage13'
ROOT = ROOT0 / 'b1_xall_tiny' if TINY else ROOT0
import os; TAG = os.environ.get('B1_TAG', '') if TINY else ''
RAW = ROOT / ('raw/b1_xall' + (f'_{TAG}' if TAG else '')); OUT = ROOT / 'summary_b1_xall' / ('partial' if PARTIAL else ''); REP = ROOT / 'reports'
TOL = 0.005; NB = 2000
STRATA = ['all', 'first', 'others', 'last']
XL = [0, 1] if TINY else [4, 8, 16, 24, 32, 40, 48]; PL = [0, 1] if TINY else [8, 16, 24, 32, 40, 48, 56]; X2L = [0, 1] if TINY else [16, 24, 32, 40, 48]
RS = ['rand61', 'rand62', 'rand63']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


A14 = load(H / '13_stage13/stage13_x1x4_analyze.py', 'x14a')
X3A = load(H / '13_stage13/stage13_x3_analyze.py', 'x3a')
X3R = load(H / '13_stage13/stage13_x3_recovery.py', 'x3r')
team_w, ci = A14.team_w, A14.ci
fm = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
WARN = []


def warn(m): WARN.append(m); print('WARN', m, flush=True)


def load_dir(d, keys=None, shards=None):
    fs = sorted(Path(d).glob('shard_*.npz'))
    if shards is not None: fs = [f for f in fs if f.stem in shards]
    if not fs: return pd.DataFrame(), []
    zs = [np.load(f) for f in fs]; ks = [k for k in zs[0].files if k != 'meta' and (keys is None or k in keys)]
    ks = [k for k in ks if all(z[k].shape == z['paper_id'].shape for z in zs)]
    return pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in ks}), [f.stem for f in fs]


def strata(df):
    """context rows -> {stratum: pair-level frame}"""
    num = [c for c in df.columns if df[c].dtype.kind == 'f' and c not in ('author_index', 'n_authors', 'n_name_tokens')]
    keep = [c for c in df.columns if c not in num and c not in ('author_index', 'n_name_tokens', 'paper_id')]
    first = lambda d: d.groupby('paper_id', sort=False)[keep].first()
    out = {}
    for s, m in (('all', np.ones(len(df), bool)), ('first', df.author_index == 0), ('others', df.author_index >= 1),
                 ('last', (df.n_authors >= 3) & (df.author_index == df.n_authors - 1))):
        d = df[np.asarray(m)]
        if d.empty: out[s] = pd.DataFrame(columns=df.columns); continue
        g = d.groupby('paper_id', sort=False)[num].mean().join(first(d)).join(d.groupby('paper_id', sort=False).size().rename('n_authors_used')).reset_index()
        out[s] = g
    return out


# ------------------------------------------------------------------ X1 (as stage13_x1x4_analyze.x1)
def x1_stats(df, pairs):
    df = df.merge(pairs[['paper_id', 'team']], on='paper_id'); rows = []
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]
        if len(s) < 2: continue
        W = team_w(s.team, 101); den = (s.clean - s.corrupt).to_numpy(); dw = W @ den; R = {}
        for src in ('authors', 'year', 'field', 'random_c'):
            for l in XL:
                num = (s[f'{src}@{l}'] - s.corrupt).to_numpy(); R[src, l] = (num.mean() / den.mean(), (W @ num) / dw)
        for l in XL:
            r = dict(split=part, layer=l, n=len(s), clean_minus_corrupt=den.mean())
            for src in ('authors', 'year', 'field', 'random_c'):
                r[f'R_{src}'] = R[src, l][0]; r[f'R_{src}_lo'], r[f'R_{src}_hi'] = ci(R[src, l][1])
            for o in ('year', 'field', 'random_c'):
                b = R['authors', l][1] - R[o, l][1]; r[f'a_minus_{o}'] = R['authors', l][0] - R[o, l][0]; r[f'a_minus_{o}_lo'], r[f'a_minus_{o}_hi'] = ci(b)
            if l >= 24 or (TINY and l >= 1):
                ti = all(-0.1 <= r[f'a_minus_{o}_lo'] and r[f'a_minus_{o}_hi'] <= 0.1 for o in ('year', 'field')) and r['a_minus_random_c_lo'] > 0
                ts = r['a_minus_year_lo'] > 0.1
                r['verdict'] = 'task-independent' if ti else ('task-specific' if ts else 'undecided')
            else:
                r['verdict'] = 'text-replacement control (no conclusion)'
            r['null_flag'] = abs(r['R_random_c']) > 0.1
            rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ X2 (as stage13_x2_analyze)
def x2_stats(df, pairs, auth_col):
    df = df.merge(pairs[['paper_id', 'team']], on='paper_id'); curves, diffs = [], []
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]
        if len(s) < 2: continue
        W = team_w(s.team, 101); den = (s.clean - s.corrupt).to_numpy(); dw = W @ den; R = {}
        for arm in ('carry', 'remove'):
            for l in X2L:
                for v, col in [('id', 'id'), ('auth', auth_col), ('full', 'full'), ('zero', 'zero')] + [(r, r) for r in RS]:
                    x = s[f'{arm}_{col}@{l}'].to_numpy()
                    num = x - s.corrupt.to_numpy() if arm == 'carry' else s.clean.to_numpy() - x
                    R[arm, v, l] = (num.mean() / den.mean(), (W @ num) / dw)
                R[arm, 'rand', l] = (np.mean([R[arm, r, l][0] for r in RS]), np.mean([R[arm, r, l][1] for r in RS], 0))
        for (arm, v, l), (e, b) in R.items():
            lo, hi = ci(b); curves.append(dict(split=part, arm=arm, S=v, layer=l, n=len(s), clean_minus_corrupt=den.mean(), value=e, lo=lo, hi=hi))
        for arm in ('carry', 'remove'):
            for l in X2L:
                g = lambda v: R[arm, v, l]
                for nm, (a, b) in {'id - rand': ('id', 'rand'), 'auth - rand': ('auth', 'rand'), 'full - rand': ('full', 'rand'), 'auth - id': ('auth', 'id')}.items():
                    lo, hi = ci(g(a)[1] - g(b)[1]); diffs.append(dict(split=part, arm=arm, layer=l, contrast=nm, value=g(a)[0] - g(b)[0], lo=lo, hi=hi))
                lo, hi = ci(g('id')[1] - 0.5 * g('full')[1]); diffs.append(dict(split=part, arm=arm, layer=l, contrast='id - 0.5 full', value=g('id')[0] - 0.5 * g('full')[0], lo=lo, hi=hi))
    Cv, D = pd.DataFrame(curves), pd.DataFrame(diffs)
    if not {'tune', 'test'} <= set(Cv.split): return Cv, D, dict(verdict='n/a (a split is missing)')
    dd = lambda part, arm, l, c: D[(D.split == part) & (D.arm == arm) & (D.layer == l) & (D.contrast == c)].iloc[0]
    cv = lambda part, arm, l, v: Cv[(Cv.split == part) & (Cv.arm == arm) & (Cv.layer == l) & (Cv.S == v)].iloc[0]
    sel = {S: max(X2L, key=lambda l: dd('tune', 'carry', l, f'{S} - rand').value) for S in ('id', 'auth')}; V = {}
    for S in ('id', 'auth'):
        l = sel[S]; x = dd('test', 'carry', l, f'{S} - rand'); xr = dd('test', 'remove', l, f'{S} - rand')
        V[S] = dict(layer=l, tune_diff=dd('tune', 'carry', l, f'{S} - rand').value, test_diff=x.value, test_lo=x.lo, test_hi=x.hi, carries=bool(x.lo > 0),
                    R_S=cv('test', 'carry', l, S).value, R_rand=cv('test', 'carry', l, 'rand').value, R_full=cv('test', 'carry', l, 'full').value,
                    remove_diff=xr.value, remove_lo=xr.lo, remove_hi=xr.hi)
    h2 = V['id']['carries'] and V['id']['R_S'] >= 0.5 * V['id']['R_full']
    ai = dd('test', 'carry', sel['auth'], 'auth - id'); h3 = V['auth']['carries'] and ai.lo > 0
    anywhere = D[(D.arm == 'carry') & D.split.isin(['tune', 'test']) & D.contrast.isin(['id - rand', 'auth - rand']) & (D.lo > 0)]
    neither = anywhere.empty
    verdict = ('H2 and H3 both supported' if h2 and h3 else 'H2 supported' if h2 else 'H3 supported (S_auth carries more than S_id)' if h3
               else 'neither (S_id and S_auth never exceed S_rand)' if neither else 'no pre-registered support for H2 or H3')
    return Cv, D, dict(verdict=verdict, H2=h2, H3=h3, neither=neither, **{f'id_{k}': v for k, v in V['id'].items()}, **{f'auth_{k}': v for k, v in V['auth'].items()},
                       auth_minus_id=ai.value, auth_minus_id_lo=ai.lo, auth_minus_id_hi=ai.hi)


# ------------------------------------------------------------------ X3 behaviour
def x3_stats(df):
    meta = pd.read_csv(ROOT0 / 'summary_x3/x3_pairs.csv')[['paper_id', 'include_primary', 'include_sensitive', 'd_matched', 'team', 'split', 'group']]
    d = df.drop(columns=[c for c in ('split',) if c in df.columns]).merge(meta, on='paper_id', how='inner')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): d[c] = d[c].astype(bool)
    X3R.WARN.clear(); Rr = X3R.recovery(d); Bh = []
    for setn, col in X3A.SETS.items():
        for sub in X3A.SUBSETS:
            m0 = d[col].to_numpy() & d.team.notna().to_numpy()
            if sub == 'd_matched': m0 &= d.d_matched.to_numpy()
            if sub == 'd_unmatched': m0 &= ~d.d_matched.to_numpy()
            for part in X3A.SPLITS:
                m = m0 if part == 'all' else m0 & (d.split == part).to_numpy(); s = d[m]
                if len(s) < 2: continue
                Bh += X3A.beh_rows(s, X3A.team_w(s.team.to_numpy(), X3A.SEED[part, sub]), part, sub, setn)
    return Rr, pd.DataFrame(Bh)


# ------------------------------------------------------------------ X4 author (as stage13_x1x4_analyze.x4)
def x4_stats(df, pairs, cbin):
    df = df.merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id').merge(cbin, on='paper_id', how='left'); rows = []; a = 'author'
    for part in ('tune', 'test', 'all'):
        s = df if part == 'all' else df[df.split == part]
        if len(s) < 2: continue
        W = team_w(s.team, 202)
        for pos in ('title', 'colon'):
            for l in PL:
                v = (s[f'{a}@self@{pos}@{l}'] - s[f'{a}@partner@{pos}@{l}']).to_numpy(); b = (W @ v) / W.sum(1)
                rows.append(dict(split=part, answer=a, pos=pos, layer=l, n=len(s), D=v.mean(), lo=ci(b)[0], hi=ci(b)[1],
                                 self=s[f'{a}@self@{pos}@{l}'].mean(), partner=s[f'{a}@partner@{pos}@{l}'].mean(), none=s[f'{a}@none'].mean()))
    D = pd.DataFrame(rows); early = []
    for pos in ('title', 'colon'):
        t = D[(D.split == 'tune') & (D.pos == pos) & (D.lo > 0)]; l0 = int(t.layer.min()) if len(t) else None
        te = D[(D.split == 'test') & (D.pos == pos) & (D.layer == l0)] if l0 is not None else None
        ok = l0 is not None and len(te) > 0
        early.append(dict(answer=a, pos=pos, earliest_tune=l0, confirmed_on_test=bool(ok and te.lo.iloc[0] > 0), D_test=float(te.D.iloc[0]) if ok else np.nan,
                          lo_test=float(te.lo.iloc[0]) if ok else np.nan, hi_test=float(te.hi.iloc[0]) if ok else np.nan))
    rec = []
    for pos in ('title', 'colon'):
        for l in PL:
            s = df.assign(v=df[f'{a}@self@{pos}@{l}'] - df[f'{a}@partner@{pos}@{l}'])
            e, lo, hi, nc = A14.strat_diff_team(s[['v', 'group', 'citation_bin']], 'v', s.team.to_numpy(), 303 + l)
            rec.append(dict(answer=a, pos=pos, layer=l, target_minus_control=e, lo=lo, hi=hi, n_bins=nc))
    return D, pd.DataFrame(early), pd.DataFrame(rec)


def all_stats(data, pairs, cbin):
    """data: {comp: pair-level frame} -> {name: frame}"""
    o = {}
    if len(data.get('xpatch', [])): o['x1'] = x1_stats(data['xpatch'], pairs)
    if len(data.get('x2', [])):
        for ver, col in (('old', 'auth'), ('new', 'authall')):
            if f'carry_{col}@{X2L[0]}' not in data['x2']: continue
            Cv, D, V = x2_stats(data['x2'], pairs, col); o[f'x2_curves_{ver}'] = Cv; o[f'x2_diffs_{ver}'] = D; o[f'x2_verdict_{ver}'] = pd.DataFrame([V])
    if len(data.get('para', [])): o['x3_recovery'], o['x3_behaviour'] = x3_stats(data['para'])
    if len(data.get('pscope', [])): o['x4_D'], o['x4_earliest'], o['x4_recognition'] = x4_stats(data['pscope'], pairs, cbin)
    return o


KEYS = {'x1': ['split', 'layer'], 'x2_curves_old': ['split', 'arm', 'S', 'layer'], 'x2_curves_new': ['split', 'arm', 'S', 'layer'],
        'x3_recovery': ['set', 'subset', 'split', 'false', 'group'], 'x3_behaviour': ['set', 'subset', 'split', 'contrast'],
        'x4_D': ['split', 'answer', 'pos', 'layer'], 'x4_recognition': ['answer', 'pos', 'layer']}
VALS = {'x1': ['R_authors', 'R_year', 'R_field', 'R_random_c', 'a_minus_year', 'a_minus_field', 'a_minus_random_c'], 'x2_curves_old': ['value'],
        'x3_recovery': ['ratio'], 'x3_behaviour': ['mean'], 'x4_D': ['D'], 'x4_recognition': ['target_minus_control']}


def compare(new, ref, name, what):
    """max |diff| of the point estimates (and of the CI ends, info) on common keys"""
    k = KEYS[name]; vals = VALS[name]; m = new.merge(ref, on=k, suffixes=('', '_ref'))
    if 'split' in k and name.startswith('x2'): m = m[(m.split == 'test') & (m.arm == 'carry') & m.S.isin(['id', 'auth', 'rand', 'full'])] if what == 'published' else m
    rows = []
    for v in vals:
        if v + '_ref' not in m: continue
        d = (m[v] - m[v + '_ref']).abs(); nanm = m[v].isna() != m[v + '_ref'].isna()   # NaN on both sides = equal
        d = d.where(~(m[v].isna() & m[v + '_ref'].isna()), 0.0).where(~nanm, np.inf); i = d.idxmax() if len(d) and d.notna().any() else None
        lohi = [c for c in (v + '_lo', 'lo') if c in m and c + '_ref' in m][:1]
        dci = float(max((m[c] - m[c + '_ref']).abs().max() for c in (lohi[0], lohi[0].replace('lo', 'hi')))) if lohi else np.nan
        rows.append(dict(item=name, against=what, value=v, n_cells=len(m), max_abs_diff=float(d.max()) if len(d) else np.nan,
                         at=str(m.loc[i, k].to_dict()) if i is not None else '', max_abs_diff_ci=dci, tol=TOL, ok=bool(len(d) and d.max() <= TOL)))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True); REP.mkdir(parents=True, exist_ok=True)
    pairs = pd.read_parquet(ROOT0 / 'config/pairs.parquet')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); cbin = papers[['paper_id', 'citation_bin']]
    ctx = {c: load_dir(RAW / c) for c in ('xpatch', 'x2', 'pscope', 'para')}
    shards = sorted(set().union(*[set(v[1]) for v in ctx.values()]))
    print('new shards per component:', {c: len(v[1]) for c, v in ctx.items()}, flush=True)
    for c, (d, _) in ctx.items():
        if len(d): print(f'{c}: {len(d)} author contexts, {d.paper_id.nunique()} pairs', flush=True)
    S = {c: strata(d) for c, (d, _) in ctx.items() if len(d)}
    res = {s: all_stats({c: S[c][s] for c in S}, pairs, cbin) for s in STRATA}
    for s in STRATA:
        for nm, fr in res[s].items(): fr.assign(stratum=s).to_csv(OUT / f'{nm}__{s}.csv', index=False)

    # ---------------------------------------------------------------- hard check
    HC = []
    # (1) per-pair first-author scores vs the frozen raw data (tiny: the frozen functions on the tiny model)
    ref_raw = {'xpatch': 'raw/xpatch', 'x2': 'raw/x2', 'pscope': 'raw/pscope', 'para': 'raw/para_run'}
    refroot = ROOT / f'raw/ref_first_{TAG}' if TINY else ROOT0
    refdata = {}
    for c in ctx:
        if not len(ctx[c][0]): continue
        rd = refroot / (c if TINY else ref_raw[c])
        ref, _ = load_dir(rd, shards=set(ctx[c][1]) if (PARTIAL or TINY) else None)
        if c == 'pscope': ref = ref[[x for x in ref.columns if not (x.startswith('year@') or x.startswith('field@'))]]
        refdata[c] = ref
        nf = S[c]['first'].set_index('paper_id'); rf = ref.set_index('paper_id'); com = rf.index.intersection(nf.index)
        cols = [k for k in rf.columns if k in nf.columns and rf[k].dtype.kind == 'f' and not k.startswith('cap_') and k not in ('word_jaccard', 'lexical_jaccard')]
        dif = np.abs(nf.loc[com, cols].to_numpy(float) - rf.loc[com, cols].to_numpy(float))
        HC.append(dict(item=f'{c} per-pair first-author scores', against='frozen raw', value=f'{len(cols)} score columns', n_cells=int(dif.size),
                       max_abs_diff=float(dif.max()), at=f'pairs new {len(nf)} / frozen {len(rf)} / common {len(com)}; exact share {(dif == 0).mean():.3f}; mean |diff| {dif.mean():.2e}',
                       max_abs_diff_ci=np.nan, tol=np.nan, ok=bool(len(com) == len(rf) == len(nf))))
    # (2) statistics: first stratum vs published CSVs (full run) / vs the same functions on the frozen raw data (partial, tiny)
    if PARTIAL or TINY:
        refstats = all_stats(refdata, pairs, cbin); what = 'frozen raw, same shards, same code'
    else:
        P = ROOT0
        refstats = {'x1': pd.read_csv(P / 'summary_x1x4/x1_recovery.csv'), 'x2_curves_old': pd.read_csv(P / 'summary_x2/x2_curves.csv'),
                    'x3_recovery': pd.read_csv(P / 'summary_x3/x3_recovery.csv'), 'x3_behaviour': pd.read_csv(P / 'summary_x3/x3_behaviour.csv'),
                    'x4_D': pd.read_csv(P / 'summary_x1x4/x4_decodability.csv').query('answer == "author"'), 'x4_recognition': pd.read_csv(P / 'summary_x1x4/x4_recognition.csv').query('answer == "author"')}
        what = 'published'
        # analysis-code validation: the same functions on the frozen raw data must give the published numbers
        own = all_stats(refdata, pairs, cbin)
        for nm in VALS:
            if nm in own and nm in refstats: HC += [dict(r, item=nm + ' (frozen raw, this code)') for r in compare(own[nm], refstats[nm], nm, 'published')]
        pv = pd.read_csv(P / 'summary_x2/x2_verdict.csv').iloc[0]; nv = res['first'].get('x2_verdict_old')
        if nv is not None:
            nv = nv.iloc[0]
            for k in ('id_layer', 'auth_layer', 'H2', 'H3'):
                HC.append(dict(item='x2 verdict', against='published', value=k, n_cells=1, max_abs_diff=float(abs(float(nv[k]) - float(pv[k]))), at=f'new {nv[k]} vs published {pv[k]}', max_abs_diff_ci=np.nan, tol=0, ok=bool(nv[k] == pv[k])))
        pe = pd.read_csv(P / 'summary_x1x4/x4_earliest.csv').query('answer == "author"').set_index('pos'); ne = res['first'].get('x4_earliest')
        if ne is not None:
            for r in ne.itertuples():
                HC.append(dict(item='x4 earliest author layer', against='published', value=r.pos, n_cells=1, max_abs_diff=np.nan, at=f'new {r.earliest_tune} / confirmed {r.confirmed_on_test} vs published {pe.loc[r.pos].earliest_tune} / {pe.loc[r.pos].confirmed_on_test}',
                               max_abs_diff_ci=np.nan, tol=0, ok=bool((pd.isna(r.earliest_tune) and pd.isna(pe.loc[r.pos].earliest_tune)) or r.earliest_tune == pe.loc[r.pos].earliest_tune)))
    for nm in VALS:
        if nm in res['first'] and nm in refstats: HC += compare(res['first'][nm], refstats[nm], nm, what)
    HCd = pd.DataFrame(HC); HCd.to_csv(OUT / 'hardcheck.csv', index=False)
    stat_rows = HCd[HCd.tol.notna() & ~HCd.item.str.contains('frozen raw, this code', regex=False)]
    passed = bool(stat_rows.ok.all()) and bool(HCd[HCd.item.str.contains('per-pair')].ok.all())
    print(HCd.to_string(), flush=True); print(f'HARD CHECK {"PASS" if passed else "FAIL"}', flush=True)

    # ---------------------------------------------------------------- report
    L = [f'# Stage 13 batch 1 item 1: X1-X4 for all authors (addendum 10)' + ('  **TINY TEST**' if TINY else '') + ('  **PARTIAL (gate)**' if PARTIAL else ''), '',
         f'Shards: {shards}. Contexts: ' + ', '.join(f'{c} {len(d)} ({d.paper_id.nunique()} pairs)' for c, (d, _) in ctx.items() if len(d)) + '.',
         'Pair-level value = mean over the paper\'s authors (all name tokens per author, teacher-forced mean log10(1/rank) at L63). Strata: all (primary), first (published scoring), others (author index >= 1, mean), last (n_authors >= 3). Same pairs, layers, partner B, random C, lexical neighbour D, team-cluster bootstrap (2,000 draws, same seeds) as published. Teacher-forced preference, not generation (addendum 4).', '',
         f'## Hard check ({what}; tolerance |diff| <= {TOL} on every point estimate): **{"PASS" if passed else "FAIL"}**', '',
         '| item | against | value | cells | max abs diff | where / detail | CI ends max diff | ok |', '|---|---|---|---|---|---|---|---|']
    for r in HCd.itertuples():
        L.append(f'| {r.item} | {r.against} | {r.value} | {r.n_cells} | {r.max_abs_diff:.2g} | {r.at} | {r.max_abs_diff_ci:.2g} | {"yes" if r.ok else "NO"} |')
    L.append('')
    n = lambda s, c: (len(S[c][s]) if c in S else 0)
    L += ['## Pairs per stratum', '', '| stratum | X1 | X2 | X3 (para) | X4 |', '|---|---|---|---|---|'] + \
         [f'| {s} | {n(s, "xpatch")} | {n(s, "x2")} | {n(s, "para")} | {n(s, "pscope")} |' for s in STRATA] + ['']
    if all('x1' in res[s] for s in STRATA):
        L += ['## X1: R (test, confirmatory) by stratum', '', '| layer | ' + ' | '.join(f'{s}: R authors / R year / R field / R C / verdict' for s in STRATA) + ' |', '|---' * (1 + len(STRATA)) + '|']
        for l in XL:
            cells = []
            for s in STRATA:
                x = res[s]['x1']; x = x[(x.split == 'test') & (x.layer == l)]
                cells.append('-' if x.empty else f'{x.R_authors.iloc[0]:+.3f} / {x.R_year.iloc[0]:+.3f} / {x.R_field.iloc[0]:+.3f} / {x.R_random_c.iloc[0]:+.3f} / {x.verdict.iloc[0]}')
            L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
        L += ['', 'authors - year on test with CI (task-independence rule: both differences inside [-0.1, 0.1] and authors - C > 0):', '', '| layer | ' + ' | '.join(STRATA) + ' |', '|---' * (1 + len(STRATA)) + '|']
        for l in XL:
            cells = []
            for s in STRATA:
                x = res[s]['x1']; x = x[(x.split == 'test') & (x.layer == l)]
                cells.append('-' if x.empty else fm(x.a_minus_year.iloc[0], x.a_minus_year_lo.iloc[0], x.a_minus_year_hi.iloc[0]))
            L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
        L.append('')
    L += ['## X2: verdict (addendum 6 rule) by stratum and S_auth version', '', '| stratum | S_auth | verdict | S_id layer | test R_id - R_rand | S_auth layer | test R_auth | test R_rand | test R_full | test R_auth - R_rand | test R_auth - R_id | H2 | H3 |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for s in STRATA:
        for ver in ('old', 'new'):
            v = res[s].get(f'x2_verdict_{ver}')
            if v is None or 'id_layer' not in v: continue
            v = v.iloc[0]
            L.append(f'| {s} | {ver} | {v.verdict} | L{v.id_layer} | {fm(v.id_test_diff, v.id_test_lo, v.id_test_hi)} | L{v.auth_layer} | {v.auth_R_S:+.3f} | {v.auth_R_rand:+.3f} | {v.auth_R_full:+.3f} | {fm(v.auth_test_diff, v.auth_test_lo, v.auth_test_hi)} | {fm(v.auth_minus_id, v.auth_minus_id_lo, v.auth_minus_id_hi)} | {v.H2} | {v.H3} |')
    L += ['', 'Table X2.1 analogue (test, carry): R per layer', '', '| stratum | S_auth | layer | R_id | R_auth | R_rand | R_full |', '|---|---|---|---|---|---|---|']
    for s in STRATA:
        for ver in ('old', 'new'):
            Cv = res[s].get(f'x2_curves_{ver}')
            if Cv is None: continue
            for l in X2L:
                g = lambda S_: Cv[(Cv.split == 'test') & (Cv.arm == 'carry') & (Cv.layer == l) & (Cv.S == S_)]
                if g('id').empty: continue
                L.append(f'| {s} | {ver} | L{l} | ' + ' | '.join(fm(g(S_).value.iloc[0], g(S_).lo.iloc[0], g(S_).hi.iloc[0]) for S_ in ('id', 'auth', 'rand', 'full')) + ' |')
    L.append('')
    L += ['## X3 behaviour: recovery (paraphrase - D) / (original - D), primary set, all subset', '', '| stratum | split | group | n | ratio [CI] | para - D [CI] |', '|---|---|---|---|---|---|']
    for s in STRATA:
        Rr = res[s].get('x3_recovery'); Bh = res[s].get('x3_behaviour')
        if Rr is None or Rr.empty: continue
        for part in ('test', 'all'):
            for grp in ('all', 'target', 'control', 'target_minus_control'):
                x = Rr[(Rr.set == 'primary') & (Rr.subset == 'all') & (Rr.split == part) & (Rr.false == 'lexical_neighbour_D') & (Rr.group == grp)]
                if x.empty: continue
                b = Bh[(Bh.set == 'primary') & (Bh.subset == 'all') & (Bh.split == part) & (Bh.contrast == 'para_minus_lex')] if grp == 'all' else None
                L.append(f'| {s} | {part} | {grp} | {int(x.n.iloc[0])} | {fm(x.ratio.iloc[0], x.lo.iloc[0], x.hi.iloc[0])} | ' + (fm(b['mean'].iloc[0], b.lo.iloc[0], b.hi.iloc[0]) if b is not None and len(b) else '') + ' |')
    L.append('')
    L += ['## X4 author answer: D = self - partner (test) by stratum', '']
    for pos in ('title', 'colon'):
        L += [f'### {pos}', '', '| layer | ' + ' | '.join(STRATA) + ' |', '|---' * (1 + len(STRATA)) + '|']
        for l in PL:
            cells = []
            for s in STRATA:
                D = res[s].get('x4_D'); x = None if D is None else D[(D.split == 'test') & (D.pos == pos) & (D.layer == l)]
                cells.append('-' if x is None or x.empty else fm(x.D.iloc[0], x.lo.iloc[0], x.hi.iloc[0]))
            L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
        L.append('')
    L += ['Earliest layer with D > 0 on tune, confirmed on test:', '', '| stratum | title | colon |', '|---|---|---|']
    for s in STRATA:
        E = res[s].get('x4_earliest')
        if E is None: continue
        c = lambda p: (lambda r: 'none' if pd.isna(r.earliest_tune) else f'L{int(r.earliest_tune)} ({"confirmed" if r.confirmed_on_test else "not confirmed"}, test {fm(r.D_test, r.lo_test, r.hi_test)})')(E[E.pos == p].iloc[0])
        L.append(f'| {s} | {c("title")} | {c("colon")} |')
    L += ['', 'Recognition (target - control of self - partner within citation bin, all pairs), title position:', '', '| layer | ' + ' | '.join(STRATA) + ' |', '|---' * (1 + len(STRATA)) + '|']
    for l in PL:
        cells = []
        for s in STRATA:
            Rc = res[s].get('x4_recognition'); x = None if Rc is None else Rc[(Rc.pos == 'title') & (Rc.layer == l)]
            cells.append('-' if x is None or x.empty else fm(x.target_minus_control.iloc[0], x.lo.iloc[0], x.hi.iloc[0]))
        L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
    L += ['', 'Note: the X4 target prompt asks for "the first author" (frozen design); for the other strata the score is the model\'s preference for that author\'s name under the same prompt.', '']
    fit = ROOT / 'summary_b1_xall/fit_authall_sanity.csv'
    if fit.exists():
        F = pd.read_csv(fit); L += ['## New S_auth (all authors\' tokens) fit', '', '```\n' + F.to_string(index=False) + '\n```', '']
    if WARN or X3R.WARN: L += ['## WARN', ''] + [f'- {w}' for w in WARN + X3R.WARN] + ['']
    rep = REP / ('b1_xall_partial_check.md' if PARTIAL else 'b1_xall_report.md'); rep.write_text('\n'.join(L) + '\n')
    print('\n'.join(L)); print('B1 XALL ANALYZED', 'HARD CHECK', 'PASS' if passed else 'FAIL')


if __name__ == '__main__':
    main()
