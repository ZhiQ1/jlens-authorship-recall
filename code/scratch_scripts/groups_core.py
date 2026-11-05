"""Addendum 7 (group comparisons), shared engine: groups, covariates, team-cluster bootstrap, estimators.

Plan (frozen): /scratch/zhang.zhiqi2/jlens/391_groups/config/prereg_addendum7_groups.json (sha256 621525e4...).
Reviewed from the earlier helper groups_lib.py (kept, unused): its group definitions and the shared multinomial team draw are reused;
its coarse-bin fallback, dose levels on m and the min-10 bins for every contrast are NOT in the plan and are not used here.

Estimators
  group mean     plain mean over the group's papers (no citation adjustment), team-bootstrap 95% interval.
  within-bin     a - b = sum_b w_b (mean_a,b - mean_b,b), w_b = n_a n_b / (n_a + n_b) normalised, over bins with >= min_a papers
                 in a and >= min_b papers in b (Stage 10 stratified_diff; there the bootstrap resamples papers inside bin x group,
                 so weights stay fixed - here weights are also fixed at the point-estimate counts and the means are re-weighted by
                 the team draw).
  slope / reg    weighted least squares (weights = team-draw multiplicity), coefficient of interest; citation-bin fixed effects
                 (+ confounders for the regression versions).
  bootstrap      2,000 draws; ONE multinomial draw over author teams (stage13_cpu.group_folds team ids, archived folds for the
                 9,108 cohort ids) shared by every estimate, so contrasts are paired. 95% percentile interval; two-sided
                 percentile p = min(1, 2 min(share <= 0, share >= 0)), floor 1/2000 (reported as p < 0.0005).
"""
import importlib.util, os, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
OUT = Path(os.environ.get('GROUPS_OUT', BASE / '391_groups'))
DATA = Path(os.environ.get('GROUPS_DATA', OUT / 'data'))
PLAN = BASE / '391_groups/config/prereg_addendum7_groups.json'; PLAN_SHA = '621525e4360f09bda8d7290b204ddc3e6bbed5c0ab3ddf6aedc8db50dd2da7de'
NB = int(os.environ.get('GROUPS_NB', 2000)); SEED = 391
GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


PLAN8 = BASE / '391_groups/config/prereg_addendum8_groups.json'; PLAN8_SHA = 'c29bbe09b938f46e899a63f1436f7cdeee2cd27090ece725f98672296a880810'


def check_plan():
    h = hashlib.sha256(PLAN.read_bytes()).hexdigest(); h8 = hashlib.sha256(PLAN8.read_bytes()).hexdigest()
    if h != PLAN_SHA or h8 != PLAN8_SHA: raise SystemExit(f'PLAN CHANGED {h} {h8}')
    return h, h8


def papers():
    p = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'recall_level', 'mc_team_outcome_tight', 'group_tight', 'm', 'citation_bin',
                                                               'citations', 'field', 'year', 'n_authors', 'mc_team_a', 'mc_team_p_true'])
    r, o = p.recall_level, p.mc_team_outcome_tight
    p['grp'] = np.select([(r == 'R0') & (o == 'strong'), (r == 'R0') & (o == 'fail'), (r == 'R1') & (o == 'strong'), (r == 'R1') & (o == 'fail'),
                          (r == 'R0') & (o == 'uncertain'), (r == 'R1') & (o == 'uncertain'), (r == 'R2') & (o == 'strong')],
                         GROUPS, 'other')
    assert ((p.group_tight == 'target') == p.grp.isin(['A', 'C'])).all() and ((p.group_tight == 'control') == p.grp.isin(['B', 'D'])).all()
    for c in ['m', 'n_authors', 'mc_team_a', 'mc_team_p_true', 'year']: p[c] = pd.to_numeric(p[c], errors='coerce')
    # author flags (written / consistent) from groups_build
    au = pd.read_parquet(DATA / 'author_flags.parquet')
    g = au.groupby('paper_id').agg(consistent=('consistent', 'first'), M=('mm', 'first'), n_listed=('written', 'size'))
    sc = au[au.scored].groupby('paper_id').agg(n_scored=('scored', 'size'), n_written_scored=('written', 'sum'))
    p = p.join(g, on='paper_id').join(sc, on='paper_id')
    p['n_unwritten_scored'] = p.n_scored - p.n_written_scored
    fa = au[au.author_index == 0].set_index('paper_id').written; p['first_written'] = p.paper_id.map(fa)
    # share of (scored) authors whose name starts with an initial
    t = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index', 'role'])
    t0 = t[t.token_index == 0]; p['share_initial'] = p.paper_id.map((t0.role == 'initial_first').groupby(t0.paper_id).mean())
    p['year_c'] = p.year - p.year.mean()
    p['written_prop'] = p.M / p.n_authors
    return p.set_index('paper_id')


class Engine:
    def __init__(self, P):
        self.P = P
        c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
        _, team = c13.group_folds(P.index.to_numpy())                 # archived folds_own9108_k5s13 -> team ids
        codes, uniq = pd.factorize(pd.Series(team)); self.team = pd.Series(codes, index=P.index); self.nteam = len(uniq)
        self.cnt = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)

    def W(self, pids): return self.cnt[:, self.team.loc[pids].to_numpy()]   # [NB, n]

    @staticmethod
    def pval(boot):
        b = boot[np.isfinite(boot)]
        if len(b) == 0: return np.nan
        return max(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / NB)

    @staticmethod
    def ci(boot):
        b = boot[np.isfinite(boot)]
        return (np.nan, np.nan) if len(b) < 0.5 * len(boot) else tuple(np.percentile(b, [2.5, 97.5]))

    # ------------------------------------------------------------------ means
    def group_mean(self, pids, V):
        """V [n, k] (nan allowed) -> est [k], boot [NB, k], n [k]."""
        V = np.asarray(V, float); V = V[:, None] if V.ndim == 1 else V
        M = ~np.isnan(V); V0 = np.where(M, V, 0); W = self.W(pids)
        with np.errstate(invalid='ignore', divide='ignore'):
            est = V0.sum(0) / M.sum(0); boot = (W @ V0) / (W @ M)
        return est, boot, M.sum(0)

    # ------------------------------------------------------------------ within-bin difference
    def within_bin(self, pids, isa, isb, bins, V, min_a, min_b):
        """a - b within citation bin, column by column (bins chosen per column on non-missing counts)."""
        V = np.asarray(V, float); V = V[:, None] if V.ndim == 1 else V
        isa, isb, bins = np.asarray(isa), np.asarray(isb), np.asarray(bins)
        M = ~np.isnan(V); V0 = np.where(M, V, 0); W = self.W(pids); k = V.shape[1]
        ests, boots, na, nb, nbin, used = np.zeros(k), np.zeros((NB, k)), np.zeros(k), np.zeros(k), np.zeros(k, int), [[] for _ in range(k)]
        wsum = np.zeros(k)
        cells = []
        for b in sorted(set(bins)):
            ia = isa & (bins == b); ib = isb & (bins == b)
            ca, cb = M[ia].sum(0), M[ib].sum(0)
            ok = (ca >= min_a) & (cb >= min_b)
            if not ok.any(): continue
            w = np.where(ok, ca * cb / np.maximum(ca + cb, 1), 0.0)
            with np.errstate(invalid='ignore', divide='ignore'):
                ma = V0[ia].sum(0) / ca; mb = V0[ib].sum(0) / cb
                bma = (W[:, ia] @ V0[ia]) / (W[:, ia] @ M[ia]); bmb = (W[:, ib] @ V0[ib]) / (W[:, ib] @ M[ib])
            cells.append((b, w, np.where(ok, ma - mb, 0), np.where(ok, bma - bmb, 0)))
            wsum += w; na += np.where(ok, ca, 0); nb += np.where(ok, cb, 0); nbin += ok
            for j in np.where(ok)[0]: used[j].append(str(b))
        if not cells:
            return dict(est=np.full(k, np.nan), boot=np.full((NB, k), np.nan), n_a=na, n_b=nb, n_bins=nbin, bins=[''] * k)
        for b, w, d, bd in cells:
            wn = np.where(wsum > 0, w / np.maximum(wsum, 1e-12), 0)
            ests += wn * d; boots += wn * bd                       # nan in a draw (empty cell) propagates -> draw dropped
        ests = np.where(wsum > 0, ests, np.nan); boots[:, wsum == 0] = np.nan
        return dict(est=ests, boot=boots, n_a=na, n_b=nb, n_bins=nbin, bins=[';'.join(u) for u in used])

    # ------------------------------------------------------------------ weighted least squares, coefficient on column 0
    def wls(self, pids, y, X, names):
        """y [n]; X [n, p] design (no intercept column needed if FE dummies span it; an intercept is added and FE drop one level).
        Returns est, boot of the coefficient for X[:, 0]."""
        y = np.asarray(y, float); X = np.asarray(X, float)
        ok = np.isfinite(y) & np.isfinite(X).all(1); y, X = y[ok], X[ok]; pids = np.asarray(pids)[ok]
        X = np.column_stack([X, np.ones(len(y))])
        keep = self._independent(X); X = X[:, keep]
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        W = self.W(pids); boot = np.full(NB, np.nan)
        for i in range(NB):
            w = W[i]; Xw = X * w[:, None]
            G = Xw.T @ X
            try: boot[i] = np.linalg.solve(G, Xw.T @ y)[0]
            except np.linalg.LinAlgError: pass
        return beta[0], boot, int(ok.sum())

    @staticmethod
    def _independent(X, tol=1e-9):
        keep = []
        for j in range(X.shape[1]):
            cand = keep + [j]
            if np.linalg.matrix_rank(X[:, cand], tol=tol * max(1, np.abs(X[:, cand]).max())) == len(cand): keep.append(j)
        assert keep and keep[0] == 0, 'coefficient of interest not identified'
        return keep


def dummies(s, prefix):
    d = pd.get_dummies(s.astype(str), prefix=prefix, dtype=float)
    return d.iloc[:, 1:] if d.shape[1] > 1 else d.iloc[:, :0]


def design(P, main_cols, confounders):
    """main columns first, then citation-bin FE, and (if confounders) field FE + year_c + n_authors + share_initial."""
    parts = [P[main_cols].astype(float), dummies(P.citation_bin, 'bin')]
    if confounders:
        parts += [dummies(P.field, 'field'), P[['year_c', 'n_authors', 'share_initial']].astype(float)]
    D = pd.concat(parts, axis=1)
    return D.to_numpy(float), list(D.columns)
