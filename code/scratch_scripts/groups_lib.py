"""POST-HOC group comparisons (advisor request 2026-11-05; NOT pre-registered). Shared engine.

Groups (cohort papers.parquet: recall_level x mc_team_outcome_tight):
    A  = R0 strong   B  = R0 fail   U0 = R0 uncertain
    C  = R1 strong   D  = R1 fail   U1 = R1 uncertain
    R2s = R2 strong (R2 uncertain 9 / fail 1 are left out)
    target = A + C, control = B + D (the existing pooled groups; reference only)
Dose levels (recognised papers = strong: A, C, R2s): m = 0, 1, 2, 3+ correct authors written; hr2 bands.

Estimators
  group mean   plain mean over the group's papers (descriptive, no citation adjustment); ratio measures: ratio of means.
  contrast a-b within citation bin, weights n_a n_b / (n_a + n_b) (the Stage 10 target - control estimator).
               Bins: the 13 fine citation bins with >= MIN_FINE (10) valid papers in both groups. If that keeps < 50% of the
               smaller group's papers, the column falls back to 4 coarse bins (0-8, 9-64, 65-512, 513+) with >= MIN_COARSE (5)
               per group. Ratio measures (recovery / loss): bin-standardised ratio per group,
               sum_b w_b mean_b(num) / sum_b w_b mean_b(den), and the contrast is the difference of these ratios.
  dose slope   OLS slope of the measure on m (0..3, 3 = 3+) or on hr2, with citation-bin fixed effects (bins with >= 10 papers).
  intervals    95% percentile bootstrap, 2,000 draws, resampling author TEAMS (stage13_cpu.group_folds team ids; archived
               folds for the 9,108 cohort ids). ONE team draw is shared by every measure and group, so contrasts are paired.
"""
import importlib.util, os
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
OUT = Path(os.environ.get('GROUPS_OUT', BASE / '391_groups'))
NB = int(os.environ.get('GROUPS_NB', 2000)); SEED = 391
MIN_FINE, MIN_COARSE, FALLBACK_SHARE = 10, 5, 0.5
GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s', 'target', 'control']
CONTRASTS = [('A', 'B'), ('C', 'A'), ('R2s', 'C'), ('R2s', 'A'), ('C', 'D'), ('D', 'B'), ('U0', 'B'), ('A', 'U0'), ('target', 'control')]
CONTRAST_MIN = {('target', 'control'): (30, None)}          # reference contrast: exactly the original rule (fine bins, >= 30, no fallback)
MLEV = ['m0', 'm1', 'm2', 'm3+']; HLEV = ['hr2=1', 'hr2 0.8-<1', 'hr2 0.5-<0.8', 'hr2<=0.5']
COARSE = {'0-2': '0-8', '3-4': '0-8', '5-8': '0-8', '9-16': '9-64', '17-32': '9-64', '33-64': '9-64', '65-128': '65-512',
          '129-256': '65-512', '257-512': '65-512'}
META = ['measure', 'stage', 'readout', 'layer', 'position', 'role']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def papers():
    p = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'recall_level', 'mc_team_outcome_tight', 'group_tight', 'm', 'hr2',
                                                               'citation_bin', 'citations', 'field', 'year', 'authors'])
    r, o = p.recall_level, p.mc_team_outcome_tight
    p['grp'] = np.select([(r == 'R0') & (o == 'strong'), (r == 'R0') & (o == 'fail'), (r == 'R1') & (o == 'strong'), (r == 'R1') & (o == 'fail'),
                          (r == 'R0') & (o == 'uncertain'), (r == 'R1') & (o == 'uncertain'), (r == 'R2') & (o == 'strong')],
                         ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s'], 'other')
    p['tc'] = p.group_tight.where(p.group_tight.isin(['target', 'control']), 'other')
    assert ((p.tc == 'target') == p.grp.isin(['A', 'C'])).all() and ((p.tc == 'control') == p.grp.isin(['B', 'D'])).all()
    p['m'] = p.m.astype(int); p['hr2'] = p.hr2.astype(float); p['recog'] = p.mc_team_outcome_tight == 'strong'
    p['mclip'] = p.m.clip(upper=3).astype(float)
    p['mlev'] = np.where(p.recog, p.m.clip(upper=3).map({0: 'm0', 1: 'm1', 2: 'm2', 3: 'm3+'}), 'other')
    h = p.hr2
    p['hlev'] = np.where(~p.recog, 'other', np.select([h >= 1, h >= 0.8, h > 0.5], HLEV[:3], HLEV[3]))
    p['bin_f'] = p.citation_bin; p['bin_c'] = p.citation_bin.map(COARSE).fillna('513+')
    return p.set_index('paper_id')


class Engine:
    def __init__(self):
        self.P = papers()
        c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
        _, team = c13.group_folds(self.P.index.to_numpy())                    # archived folds_own9108_k5s13 (team ids)
        codes, uniq = pd.factorize(pd.Series(team)); self.code = pd.Series(codes, index=self.P.index); self.nteam = len(uniq)
        self.cnt = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float32)

    # ------------------------------------------------------------------ core
    def analyze(self, meta, pids, num, den=None, contrasts=CONTRASTS, dose=True):
        """meta: list of dicts (META keys) per column; num/den [n, k] arrays aligned to pids. Returns tidy DataFrame."""
        pids = np.asarray(pids); P = self.P.loc[pids]; num = np.asarray(num, np.float64)
        if num.ndim == 1: num = num[:, None]
        ratio = den is not None
        if ratio:
            den = np.asarray(den, np.float64); den = den[:, None] if den.ndim == 1 else den
            M = ~(np.isnan(num) | np.isnan(den)); D0 = np.where(M, den, 0).astype(np.float32)
        else:
            M = ~np.isnan(num); D0 = None
        X0 = np.where(M, num, 0).astype(np.float32); Mf = M.astype(np.float32)
        W = self.cnt[:, self.code.loc[pids].to_numpy()]                        # [NB, n]
        cache = {}

        def cell(col, val, bcol, b):
            key = (col, val, bcol, b)
            if key not in cache:
                ix = np.where(((P[col] == val) if val not in ('target', 'control') or col != 'grp' else (P.tc == val)).to_numpy() & (P[bcol] == b).to_numpy())[0]
                if len(ix) == 0: cache[key] = None
                else:
                    Wi = W[:, ix]; c = dict(n=Mf[ix].sum(0), sx=X0[ix].sum(0, dtype=np.float64), bx=Wi @ X0[ix], bc=Wi @ Mf[ix])
                    if ratio: c['sd'] = D0[ix].sum(0, dtype=np.float64); c['bd'] = Wi @ D0[ix]
                    cache[key] = c
            return cache[key]

        def bins(bcol): return sorted(P[bcol].unique())

        def pooled(col, val):
            cs = [c for b in bins('bin_f') if (c := cell(col, val, 'bin_f', b)) is not None]
            if not cs: return None
            n = sum(c['n'] for c in cs); sx = sum(c['sx'] for c in cs); bx = sum(c['bx'] for c in cs); bc = sum(c['bc'] for c in cs)
            with np.errstate(divide='ignore', invalid='ignore'):
                if ratio:
                    sd = sum(c['sd'] for c in cs); bd = sum(c['bd'] for c in cs); return n, sx / sd, bx / bd
                return n, sx / n, bx / bc

        def strat(col, a, b, mn_f, mn_c):
            """returns est [k], boot [NB,k], n_a, n_b, n_bins, scheme"""
            res = {}
            for bcol, mn in (('bin_f', mn_f), ('bin_c', mn_c)):
                if mn is None: continue
                ws, ma, mb, bma, bmb, na, nb = [], [], [], [], [], 0, 0
                for bb in bins(bcol):
                    ca, cb = cell(col, a, bcol, bb), cell(col, b, bcol, bb)
                    if ca is None or cb is None: continue
                    ok = (ca['n'] >= mn) & (cb['n'] >= mn)
                    w = np.where(ok, ca['n'] * cb['n'] / np.maximum(ca['n'] + cb['n'], 1), 0.0)
                    ws.append(w); na = na + np.where(ok, ca['n'], 0); nb = nb + np.where(ok, cb['n'], 0)
                    with np.errstate(divide='ignore', invalid='ignore'):
                        if ratio:
                            ma.append((ca['sx'] / ca['n'], ca['sd'] / ca['n'])); mb.append((cb['sx'] / cb['n'], cb['sd'] / cb['n']))
                            bma.append((ca['bx'] / ca['bc'], ca['bd'] / ca['bc'])); bmb.append((cb['bx'] / cb['bc'], cb['bd'] / cb['bc']))
                        else:
                            ma.append(ca['sx'] / ca['n']); mb.append(cb['sx'] / cb['n']); bma.append(ca['bx'] / ca['bc']); bmb.append(cb['bx'] / cb['bc'])
                if not ws: continue
                Wb = np.array(ws); tot = Wb.sum(0); nbin = (Wb > 0).sum(0)
                with np.errstate(divide='ignore', invalid='ignore'):
                    Wn = Wb / tot
                    z = np.nan_to_num                                            # bins with weight 0 may hold nan means
                    def comb(lst, j=None):                                       # weighted sum over bins; nan if a USED bin is nan
                        tot_, bad = 0.0, False
                        for w, x in zip(Wn, lst):
                            x = x if j is None else x[j]
                            tot_ = tot_ + w * z(x); bad = bad | ((w > 0) & np.isnan(x))
                        return np.where(bad, np.nan, tot_)
                    if ratio:
                        est = comb(ma, 0) / comb(ma, 1) - comb(mb, 0) / comb(mb, 1)
                        boot = comb(bma, 0) / comb(bma, 1) - comb(bmb, 0) / comb(bmb, 1)
                    else:
                        est = comb(ma) - comb(mb); boot = comb(bma) - comb(bmb)
                est = np.where(tot > 0, est, np.nan)
                res[bcol] = (est, boot, na, nb, nbin)
            # choose per column
            k = X0.shape[1]; nA = pooled_n(col, a); nB = pooled_n(col, b); small = np.minimum(nA, nB)
            out = dict(est=np.full(k, np.nan), boot=np.full((NB, k), np.nan), na=np.zeros(k), nb=np.zeros(k), nbin=np.zeros(k), scheme=np.array(['none'] * k, dtype=object))
            f = res.get('bin_f'); c = res.get('bin_c')
            for j in range(k):
                use = None
                if f is not None and np.isfinite(f[0][j]):
                    sm_kept = f[2][j] if nA[j] <= nB[j] else f[3][j]
                    if mn_c is None or sm_kept >= FALLBACK_SHARE * small[j]: use = 'bin_f'
                if use is None and c is not None and np.isfinite(c[0][j]): use = 'bin_c'
                if use is None and f is not None and np.isfinite(f[0][j]): use = 'bin_f'
                if use:
                    r = res[use]; out['est'][j] = r[0][j]; out['boot'][:, j] = r[1][:, j]; out['na'][j] = r[2][j]; out['nb'][j] = r[3][j]; out['nbin'][j] = r[4][j]
                    out['scheme'][j] = {'bin_f': 'fine', 'bin_c': 'coarse'}[use]
            return out

        def pooled_n(col, val):
            cs = [c for b in bins('bin_f') if (c := cell(col, val, 'bin_f', b)) is not None]
            return sum(c['n'] for c in cs) if cs else np.zeros(X0.shape[1])

        rows = []
        def emit(kind, label, n, est, boot, extra=None):
            with np.errstate(invalid='ignore'):
                lo, hi = np.nanpercentile(boot, 2.5, axis=0), np.nanpercentile(boot, 97.5, axis=0)
                nanshare = np.isnan(boot).mean(0)
            for j, m in enumerate(meta):
                r = dict(m, kind=kind, group_or_contrast=label, n=float(n[j]) if np.ndim(n) else float(n), estimate=float(est[j]), lo=float(lo[j]), hi=float(hi[j]),
                         boot_nan_share=float(nanshare[j]))
                if extra:
                    for kk, v in extra.items(): r[kk] = v[j] if np.ndim(v) else v
                rows.append(r)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            present = set(P.grp) | ({'target'} if (P.tc == 'target').any() else set()) | ({'control'} if (P.tc == 'control').any() else set())
            for g in GROUPS:
                if g not in present: continue
                r = pooled('grp', g)
                if r is not None: emit('group_mean', g, r[0], r[1], r[2])
            for a, b in contrasts:
                if a not in present or b not in present: continue
                mn_f, mn_c = CONTRAST_MIN.get((a, b), (MIN_FINE, MIN_COARSE))
                o = strat('grp', a, b, mn_f, mn_c)
                emit('contrast', f'{a} - {b}', np.minimum(o['na'], o['nb']), o['est'], o['boot'],
                     dict(n_a=o['na'], n_b=o['nb'], n_bins=o['nbin'], strata=o['scheme']))
            if dose:
                for col, levs in (('mlev', MLEV), ('hlev', HLEV)):
                    for lv in levs:
                        r = pooled(col, lv)
                        if r is not None: emit('dose_level_mean', f'{col}:{lv}', r[0], r[1], r[2])
                    for lv in levs[1:]:
                        o = strat(col, lv, levs[0], MIN_FINE, MIN_COARSE)
                        if np.isfinite(o['est']).any():
                            emit('dose_contrast', f'{lv} - {levs[0]}', np.minimum(o['na'], o['nb']), o['est'], o['boot'],
                                 dict(n_a=o['na'], n_b=o['nb'], n_bins=o['nbin'], strata=o['scheme']))
                if not ratio:
                    for zname, zcol, sub in (('slope on m (0..3+), recognised', 'mclip', P.recog.to_numpy()),
                                             ('slope on m (1..3+), recognised with m>=1', 'mclip', (P.recog & (P.m >= 1)).to_numpy()),
                                             ('slope on hr2, recognised', 'hr2', P.recog.to_numpy()),
                                             ('slope on hr2, recognised with m>=1', 'hr2', (P.recog & (P.m >= 1)).to_numpy())):
                        o = self._slope(P, W, X0, Mf, sub, P[zcol].to_numpy(float))
                        if o is not None: emit('dose_slope', zname, o[0], o[1], o[2])
        return pd.DataFrame(rows)

    def _slope(self, P, W, X0, Mf, sub, z):
        """OLS slope with citation-bin fixed effects; bins with >= 10 papers in the subset and spread in z."""
        num_e = den_e = 0; num_b = den_b = 0; n = 0
        for b in sorted(P.bin_f.unique()):
            ix = np.where(sub & (P.bin_f == b).to_numpy())[0]
            if len(ix) < 10 or np.ptp(z[ix]) == 0: continue
            zz = z[ix].astype(np.float32)[:, None]; Wi = W[:, ix]; X = X0[ix]; Mm = Mf[ix]
            def S(w):                                             # sums with weights w (vector or matrix)
                return (w @ Mm, w @ X, w @ (Mm * zz), w @ (X * zz), w @ (Mm * zz * zz))
            for wt, tgt in ((np.ones(len(ix), np.float64), 'e'), (Wi, 'b')):
                sw, sx, sz, sxz, szz = S(wt)
                with np.errstate(divide='ignore', invalid='ignore'):
                    nu = sxz - sx * sz / sw; de = szz - sz * sz / sw
                nu, de = np.nan_to_num(nu), np.nan_to_num(de)
                if tgt == 'e': num_e = num_e + nu; den_e = den_e + de
                else: num_b = num_b + nu; den_b = den_b + de
            n = n + Mf[ix].sum(0)
        if np.ndim(den_e) == 0: return None
        with np.errstate(divide='ignore', invalid='ignore'):
            return n, num_e / den_e, num_b / den_b


def meta_rows(**kw):
    return {k: kw.get(k, '') for k in META}


def write(df, name):
    OUT.mkdir(parents=True, exist_ok=True)
    df['flag_n_lt_30'] = df.n < 30
    df['post_hoc'] = True
    cols = META + ['kind', 'group_or_contrast', 'n', 'estimate', 'lo', 'hi', 'flag_n_lt_30', 'n_a', 'n_b', 'n_bins', 'strata', 'boot_nan_share', 'post_hoc']
    for c in cols:
        if c not in df: df[c] = np.nan
    p = OUT / f'{name}.csv'
    if p.exists() and os.environ.get('GROUPS_OVERWRITE') != '1':
        raise FileExistsError(f'{p} exists; refusing to overwrite (set GROUPS_OVERWRITE=1 only for test roots)')
    df[cols].to_csv(p, index=False); print('wrote', p, len(df), flush=True)
