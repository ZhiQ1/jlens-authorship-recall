"""Addendum 7, step 2: primary contrasts P1-P3 (within-bin + confounder regression, Holm), exploratory Stage 10 splits, figures.

Input: OUT/data/{author_flags,paper_signal}.parquet (groups_build.py). Outputs (refuse to overwrite): OUT/primary.csv,
OUT/stage10_group_means.csv, OUT/stage10_contrasts.csv, OUT/stage10_dose.csv, OUT/stage10_curves.csv, OUT/papers_used.csv,
OUT/figures/*.png, OUT/reports/stage10_tables.md.
All comparisons on UNWRITTEN authors of papers whose rebuilt written count equals the label m ('consistent').
"""
import os, sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import groups_core as gc

OUT = gc.OUT; FIG = OUT / 'figures'; REP = OUT / 'reports'
ROLES = ['surname_first', 'surname_cont', 'initial_first', 'given_first', 'given_cont', 'punct']
PRIMARY_RL = ('final', 63)


def guard(p):
    if p.exists() and os.environ.get('GROUPS_OVERWRITE') != '1': raise SystemExit(f'{p} exists; refusing to overwrite')
    return p


def fmt(e, lo, hi, d=3): return f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'
def pfmt(p): return '< 0.0005' if p <= 1 / gc.NB + 1e-12 else f'{p:.4f}'


class Data:
    def __init__(self):
        self.P = gc.papers()
        S = pd.read_parquet(gc.DATA / 'paper_signal.parquet')
        self.S = S
        self.A = pd.read_parquet(gc.DATA / 'author_signal.parquet')                                  # addendum 8
        self.rls = sorted({(r, int(l)) for r, l in S[['readout', 'layer']].drop_duplicates().itertuples(index=False)}, key=lambda x: (x[0], x[1]))
        self.E = gc.Engine(self.P)
        self.ok = self.P[(self.P.consistent == True) & self.P.grp.isin(gc.GROUPS)]          # noqa: E712

    def mat(self, who, role='all', measure='spec'):
        s = self.S[(self.S.who == who) & (self.S.role == role)]
        w = s.pivot_table(index='paper_id', columns=['readout', 'layer'], values=measure, aggfunc='first')
        w.columns = [(r, int(l)) for r, l in w.columns]
        return w.reindex(index=self.ok.index, columns=self.rls)


def author_frame(D, rl=PRIMARY_RL):
    """addendum 8: author-level rows (unwritten authors of consistent papers) at one readout-layer, with paper covariates."""
    A = D.A[(D.A.readout == rl[0]) & (D.A.layer == rl[1]) & (~D.A.written)]
    A = A[A.paper_id.isin(D.ok.index)].copy()
    A = A.join(D.ok, on='paper_id')
    A['position'] = A.author_index + 1; A['first'] = (A.author_index == 0).astype(float); A['other'] = 1 - A['first']
    return A


def primary(D, L):
    """Addendum 7 P1, P3 + addendum 8 P2 (stratified by author position: first vs other; pooled = reference, biased by position)."""
    P, E = D.ok, D.E
    y_all = D.mat('unwritten')[PRIMARY_RL].to_numpy(float)
    y_first = D.mat('unwritten_first')[PRIMARY_RL].to_numpy(float)
    y_other = D.mat('unwritten_other')[PRIMARY_RL].to_numpy(float)
    AU = author_frame(D)
    rows = []; boots = {}

    def add(name, kind, est, boot, n_pap, n_auth, n_bins, bins, note='', primary=False):
        lo, hi = E.ci(boot); rows.append(dict(contrast=name, version=kind, estimate=est, lo=lo, hi=hi, p_raw=E.pval(boot), n_papers=n_pap,
                                              n_authors=n_auth, n_bins=n_bins, bins=bins, boot_valid=int(np.isfinite(boot).sum()), note=note,
                                              primary=primary))
        boots[(name, kind)] = boot

    def author_reg(name, a_mask_fn, paper_ids, gcol, extra, label, n_bins, bins, note, stratum=None):
        Ai = AU[AU.paper_id.isin(paper_ids)]
        if stratum == 'first': Ai = Ai[Ai.author_index == 0]
        if stratum == 'other': Ai = Ai[Ai.author_index >= 1]
        Ai = Ai.assign(g=a_mask_fn(Ai)).set_index('paper_id', drop=False)
        X, names = gc.design(Ai, [gcol] + extra, True)
        est, boot, n = E.wls(Ai.index.to_numpy(), Ai.spec.to_numpy(float), X, names)
        add(name, label, est, boot, int(Ai.paper_id.nunique()), n, n_bins, bins, note)

    def within(name, a, b, y, mina, minb, primary_flag, note):
        sub = P.grp.isin([a, b]).to_numpy(); pids = P.index[sub]
        r = E.within_bin(pids, (P.grp[sub] == a).to_numpy(), (P.grp[sub] == b).to_numpy(), P.citation_bin[sub].to_numpy(), y[sub], mina, minb)
        used = set(r['bins'][0].split(';')) if r['bins'][0] else set()
        inb = sub & P.citation_bin.isin(used).to_numpy() & np.isfinite(y)
        add(name, 'within-bin', r['est'][0], r['boot'][:, 0], f"{int(r['n_a'][0])} / {int(r['n_b'][0])}", '', int(r['n_bins'][0]), r['bins'][0],
            note + f'; bins with >= {mina} {a} and >= {minb} {b} papers', primary_flag)
        return inb, r

    def nauth_au(pids, stratum=None):
        Ai = AU[AU.paper_id.isin(pids)]
        if stratum == 'first': Ai = Ai[Ai.author_index == 0]
        if stratum == 'other': Ai = Ai[Ai.author_index >= 1]
        return Ai.groupby('grp').size().to_dict()

    conf_note = 'bin + field FE, year (centred), n_authors, share initial-first'
    specs = [('P1 A - B', 'A', 'B', y_all, 30, 30, True, None, 'all unwritten authors (R0: all authors)'),
             ('P2-first C - A', 'C', 'A', y_first, 10, 1, True, 'first', 'first author (unwritten) only'),
             ('P2-other C - A', 'C', 'A', y_other, 10, 1, True, 'other', 'unwritten authors at position >= 2 only'),
             ('P2-pooled C - A (reference; biased by author position)', 'C', 'A', y_all, 10, 1, False, None, 'all unwritten authors pooled')]
    for name, a, b, y, mina, minb, pf, stratum, note in specs:
        inb, r = within(name, a, b, y, mina, minb, pf, note)
        na = nauth_au(P.index[inb], stratum); rows[-1]['n_authors'] = f"{na.get(a, 0)} / {na.get(b, 0)}"
        Pi = P[inb].assign(g=(P.grp[inb] == a).astype(float))
        # addendum 7: paper-level regressions
        for conf in (False, True):
            X, names = gc.design(Pi, ['g'], conf)
            est, boot, n = E.wls(Pi.index, y[inb], X, names)
            add(name, 'paper-level regression + confounders (add. 7)' if conf else 'paper-level regression, bin FE only', est, boot, n,
                rows[-1]['n_authors'], int(r['n_bins'][0]), r['bins'][0], 'same papers as within-bin; ' + (conf_note if conf else 'bin FE'))
        # addendum 8: author-level regressions with author position
        gfn = lambda Ai, a=a: (Ai.grp == a).astype(float)
        if stratum is None:
            author_reg(name, gfn, P.index[inb], 'g', ['first'], 'author-level + confounders + first/other (add. 8)', int(r['n_bins'][0]), r['bins'][0],
                       'author rows; ' + conf_note + ' + first-author dummy')
            author_reg(name, gfn, P.index[inb], 'g', ['position'], 'author-level + confounders + numeric position (add. 8 sensitivity)', int(r['n_bins'][0]),
                       r['bins'][0], 'author rows; ' + conf_note + ' + position 1..n')
        elif stratum == 'first':
            author_reg(name, gfn, P.index[inb], 'g', [], 'author-level + confounders (add. 8; first authors only)', int(r['n_bins'][0]), r['bins'][0],
                       'first-author rows; ' + conf_note, 'first')
        else:
            author_reg(name, gfn, P.index[inb], 'g', [], 'author-level + confounders (add. 8; other authors)', int(r['n_bins'][0]), r['bins'][0],
                       'position >= 2 rows; ' + conf_note, 'other')
            author_reg(name, gfn, P.index[inb], 'g', ['position'], 'author-level + confounders + numeric position (add. 8 sensitivity)', int(r['n_bins'][0]),
                       r['bins'][0], 'position >= 2 rows; ' + conf_note + ' + position 2..n', 'other')
        if name.startswith('P1'):
            ra = E.within_bin(P.index[P.grp.isin([a, b])], (P.grp[P.grp.isin([a, b])] == a).to_numpy(), (P.grp[P.grp.isin([a, b])] == b).to_numpy(),
                              P.citation_bin[P.grp.isin([a, b])].to_numpy(), D.mat('all')[PRIMARY_RL].to_numpy(float)[P.grp.isin([a, b]).to_numpy()], 30, 30)
            L.append(f'Check: A - B on all authors (consistent papers) = {ra["est"][0]:+.4f} (published R0 view +0.199 on all papers).')
    # ---------------- P3 slope on mc_team_a within R0 (A + U0 + B)
    sub = (P.grp.isin(['A', 'U0', 'B']) & P.mc_team_a.notna()).to_numpy() & np.isfinite(y_all); Pi = P[sub]
    nb3, b3 = int(Pi.citation_bin.nunique()), ';'.join(sorted(Pi.citation_bin.unique()))
    nau = int(len(AU[AU.paper_id.isin(Pi.index)]))
    for conf in (False, True):
        X, names = gc.design(Pi, ['mc_team_a'], conf)
        est, boot, n = E.wls(Pi.index, y_all[sub], X, names)
        add('P3 slope on mc_team_a (R0)', 'paper-level regression + confounders (add. 7)' if conf else 'regression, bin FE only', est, boot, n, nau, nb3, b3,
            'per one MC order right (0-4); all R0 papers with mc_team_a; ' + (conf_note if conf else 'bin FE'), primary=not conf)
    author_reg('P3 slope on mc_team_a (R0)', lambda Ai: Ai.mc_team_a.astype(float), Pi.index, 'g', ['first'], 'author-level + confounders + first/other (add. 8)',
               nb3, b3, 'author rows; ' + conf_note + ' + first-author dummy')
    author_reg('P3 slope on mc_team_a (R0)', lambda Ai: Ai.mc_team_a.astype(float), Pi.index, 'g', ['position'],
               'author-level + confounders + numeric position (add. 8 sensitivity)', nb3, b3, 'author rows; ' + conf_note + ' + position 1..n')
    R = pd.DataFrame(rows)
    # Holm over the 4 primary tests (P1, P2-first, P2-other, P3)
    pr = R[R.primary].sort_values('p_raw'); m = len(pr); assert m == 4, m; run = 0; R['p_holm'] = np.nan
    for i, (ix, p) in enumerate(pr.p_raw.items()):
        run = max(run, min(1.0, (m - i) * p)); R.loc[ix, 'p_holm'] = run
    R['sign_vs_primary'] = ''
    for c in R.contrast.unique():
        s = R[R.contrast == c]; base = s[s.primary] if s.primary.any() else s[s.version == 'within-bin']
        e0 = base.estimate.iloc[0]
        for ix, e in s.estimate.items():
            R.loc[ix, 'sign_vs_primary'] = 'same sign' if np.sign(e) == np.sign(e0) else 'SIGN DIFFERS (not robust to confounders)'
    # addendum 8 rule: stratified vs pooled direction
    pool = R[(R.contrast.str.startswith('P2-pooled')) & (R.version == 'within-bin')].estimate.iloc[0]
    for st in ['P2-first C - A', 'P2-other C - A']:
        e = R[(R.contrast == st) & R.primary].estimate.iloc[0]
        L.append(f'Addendum 8 direction rule: {st} {e:+.4f} vs pooled {pool:+.4f} -> ' +
                 ('same direction' if np.sign(e) == np.sign(pool) else 'DIRECTION DIFFERS: stratified result is the conclusion; pooled is biased by author position'))
    return R, boots


def group_means(D):
    P, E = D.ok, D.E; rows = []
    for who in ['unwritten', 'written', 'all', 'unwritten_first', 'unwritten_other', 'written_first', 'written_other']:
        for role in (['all'] + ROLES) if who in ('unwritten', 'written', 'all') else ['all']:
            for measure in (['spec', 'true', 'delete'] if role == 'all' else ['spec']):
                Mx = D.mat(who, role, measure)
                for g in gc.GROUPS:
                    sub = (P.grp == g).to_numpy(); V = Mx.to_numpy(float)[sub]
                    if not np.isfinite(V).any(): continue
                    est, boot, n = E.group_mean(P.index[sub], V)
                    nauth_col = {'unwritten': 'n_unwritten_scored', 'written': 'n_written_scored', 'all': 'n_scored'}.get(who)
                    for j, (r, l) in enumerate(D.rls):
                        if n[j] == 0: continue
                        lo, hi = E.ci(boot[:, j]); valid = np.isfinite(V[:, j])
                        rows.append(dict(who=who, role=role, measure=measure, readout=r, layer=l, group=g, n_papers=int(n[j]),
                                         n_authors=(int(P[sub].loc[valid, nauth_col].sum()) if nauth_col else int(valid.sum())) if role == 'all' else np.nan,
                                         n_bins=int(P[sub].loc[valid].citation_bin.nunique()), estimate=est[j], lo=lo, hi=hi,
                                         descriptive_only=n[j] < 30))
    return pd.DataFrame(rows)


EXPL = [('P1 A - B (by layer)', 'A', 'B', [(30, 30)]), ('P2 C - A (by layer)', 'C', 'A', [(10, 1)]),
        ('C - D', 'C', 'D', [(10, 10), (1, 1)]), ('D - B', 'D', 'B', [(10, 10), (1, 1)]), ('U0 - B', 'U0', 'B', [(10, 10)]),
        ('A - U0', 'A', 'U0', [(10, 10)]), ('R2s - C (reference)', 'R2s', 'C', [(10, 10), (1, 1)]), ('R2s - A (reference)', 'R2s', 'A', [(10, 10), (1, 1)])]


def contrasts(D):
    P, E = D.ok, D.E; rows = []
    for who in ['unwritten', 'unwritten_first', 'unwritten_other', 'written']:          # addendum 8: position split beside pooled
        Mx = D.mat(who).to_numpy(float)
        for name, a, b, rules in EXPL:
            if who == 'written' and not name.startswith(('C - D', 'R2s - C')): continue
            sub = P.grp.isin([a, b]).to_numpy()
            for mina, minb in rules:
                r = E.within_bin(P.index[sub], (P.grp[sub] == a).to_numpy(), (P.grp[sub] == b).to_numpy(), P.citation_bin[sub].to_numpy(), Mx[sub], mina, minb)
                if np.isfinite(r['est']).any(): break
            for j, (rd, l) in enumerate(D.rls):
                lo, hi = E.ci(r['boot'][:, j]); nsm = min(r['n_a'][j], r['n_b'][j])
                rows.append(dict(who=who, contrast=name, readout=rd, layer=l, estimate=r['est'][j], lo=lo, hi=hi, p_raw=E.pval(r['boot'][:, j]),
                                 n_a=int(r['n_a'][j]), n_b=int(r['n_b'][j]), n_bins=int(r['n_bins'][j]), bins=r['bins'][j],
                                 bin_rule=f'>= {mina} {a}, >= {minb} {b}', descriptive_only=nsm < 30))
    return pd.DataFrame(rows)


def dose(D):
    """Exploratory: unwritten-author signal vs written proportion M / n_authors within recognised (strong) papers A + C + R2s."""
    P, E = D.ok, D.E; rows = []
    for who in ['unwritten', 'unwritten_first', 'unwritten_other']:
        rows += dose_one(D, who)
    return pd.DataFrame(rows)


def dose_one(D, who):
    P, E = D.ok, D.E; U = D.mat(who); rows = []
    for label, sub in (('recognised A+C+R2s, all', P.grp.isin(['A', 'C', 'R2s'])), ('recognised C+R2s (M >= 1)', P.grp.isin(['C', 'R2s']))):
        sub = sub.to_numpy(); Pi = P[sub]
        for rl in D.rls:
            y = U[rl].to_numpy(float)[sub]
            X, names = gc.design(Pi, ['written_prop'], False)
            est, boot, n = E.wls(Pi.index, y, X, names); lo, hi = E.ci(boot)
            rows.append(dict(who=who, kind='slope (bin FE)', sample=label, readout=rl[0], layer=rl[1], level='', estimate=est, lo=lo, hi=hi,
                             p_raw=E.pval(boot), n_papers=n, n_authors=int(Pi.n_unwritten_scored[np.isfinite(y)].sum()), descriptive_only=n < 30))
    # binned means (no adjustment)
    sub = P.grp.isin(['A', 'C', 'R2s']).to_numpy(); Pi = P[sub]
    lev = pd.cut(Pi.written_prop, [-0.01, 0, 0.25, 0.5, 0.999, 1.0], labels=['0', '(0, 0.25]', '(0.25, 0.5]', '(0.5, 1)', '1'])
    V = U.to_numpy(float)[sub]
    for lv in lev.cat.categories:
        m = (lev == lv).to_numpy()
        if not m.any() or not np.isfinite(V[m]).any(): continue
        est, boot, n = E.group_mean(Pi.index[m], V[m])
        for j, rl in enumerate(D.rls):
            if n[j] == 0: continue
            lo, hi = E.ci(boot[:, j])
            rows.append(dict(who=who, kind='binned mean', sample='recognised A+C+R2s', readout=rl[0], layer=rl[1], level=lv, estimate=est[j], lo=lo, hi=hi,
                             p_raw=np.nan, n_papers=int(n[j]), n_authors=int(Pi[m].n_unwritten_scored[np.isfinite(V[m][:, j])].sum()), descriptive_only=n[j] < 30))
    return rows


def curves(D):
    """Exploratory: unwritten signal by mc_team_a (0-4) and by binned mc_team_p_true, within R0 and within R1 papers (all outcomes)."""
    rows = []
    for who in ['unwritten', 'unwritten_first', 'unwritten_other']: rows += curves_one(D, who)
    return pd.DataFrame(rows)


def curves_one(D, who):
    P, E = D.ok, D.E; U = D.mat(who).to_numpy(float); rows = []
    pb = pd.cut(P.mc_team_p_true, [-0.001, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0001], labels=['<0.1', '0.1-0.25', '0.25-0.5', '0.5-0.75', '0.75-0.9', '>=0.9'])
    for rec in ['R0', 'R1']:
        for var, col in (('mc_team_a', P.mc_team_a), ('mc_team_p_true bin', pb)):
            levels = [0, 1, 2, 3, 4] if var == 'mc_team_a' else list(pb.cat.categories)
            for lv in levels:
                m = ((P.recall_level == rec) & (col == lv)).to_numpy()
                if not m.any(): continue
                est, boot, n = E.group_mean(P.index[m], U[m])
                for j, rl in enumerate(D.rls):
                    if n[j] == 0: continue
                    lo, hi = E.ci(boot[:, j])
                    rows.append(dict(who=who, recall=rec, variable=var, level=str(lv), readout=rl[0], layer=rl[1], estimate=est[j], lo=lo, hi=hi, n_papers=int(n[j]),
                                     n_authors=int(P[m].n_unwritten_scored[np.isfinite(U[m][:, j])].sum()), descriptive_only=n[j] < 30))
    return rows


# ---------------------------------------------------------------- figures
COL = {'A': '#2a78d6', 'B': '#eb6834', 'C': '#1baf7a', 'D': '#eda100', 'U0': '#e87ba4', 'U1': '#008300', 'R2s': '#6250d6'}
MK = {'A': 'o', 'B': 's', 'C': '^', 'D': 'v', 'U0': 'D', 'U1': 'P', 'R2s': 'X'}
NAME = {'A': 'A  R0 x strong', 'B': 'B  R0 x fail', 'C': 'C  R1 x strong', 'D': 'D  R1 x fail', 'U0': 'U0  R0 x uncertain', 'U1': 'U1  R1 x uncertain',
        'R2s': 'R2s  R2 x strong (ref.)'}


def style(plt):
    plt.rcParams.update({'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'axes.edgecolor': '#8a8984', 'axes.labelcolor': '#0b0b0b',
                         'text.color': '#0b0b0b', 'xtick.color': '#52514e', 'ytick.color': '#52514e', 'axes.grid': True, 'grid.color': '#e6e5e0',
                         'grid.linewidth': 0.8, 'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 12, 'lines.linewidth': 2})


def figures(GM, CU, R):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    style(plt); FIG.mkdir(parents=True, exist_ok=True)
    g = GM[(GM.who == 'unwritten') & (GM.role == 'all') & (GM.measure == 'spec')]
    # 1. small multiples: mean per group across layers, one panel per readout
    fig, axs = plt.subplots(2, 2, figsize=(16, 11), sharey=True)
    for ax, rd in zip(axs.flat, ['logit', 'jlens_public', 'jlens_self100', 'jlens_fitA']):
        for grp in gc.GROUPS:
            s = g[(g.readout == rd) & (g.group == grp)].sort_values('layer')
            f = g[(g.readout == 'final') & (g.group == grp)]
            if s.empty: continue
            ls = '--' if s.n_papers.max() < 30 else '-'
            ax.plot(s.layer, s.estimate, ls, color=COL[grp], marker=MK[grp], ms=6, label=NAME[grp] + (' (n<30)' if ls == '--' else ''))
            ax.fill_between(s.layer, s.lo, s.hi, color=COL[grp], alpha=0.10, lw=0)
            if len(f): ax.plot([63], f.estimate, MK[grp], color=COL[grp], ms=9, mec='#fcfcfb', mew=1.5)
        ax.axhline(0, color='#8a8984', lw=1); ax.set_title(f'{rd}  (point at 63 = final output)', fontsize=13)
        ax.set_xlabel('layer'); ax.set_ylabel('title-specific signal, unwritten authors\nlog10(1/rank): true - mean of 5 false titles')
    axs.flat[0].legend(fontsize=10, loc='upper left', frameon=False)
    fig.suptitle('Stage 10 title-specific signal by group (unwritten authors only; plain group means, team-bootstrap 95% band)', fontsize=14)
    fig.tight_layout(); fig.savefig(FIG / 'fig1_group_means_by_layer.png', dpi=120); plt.close(fig)
    # 2. signal vs mc_team_a and p_true bins (final output)
    fig, axs = plt.subplots(1, 2, figsize=(16, 6.5), sharey=True)
    for ax, var in zip(axs, ['mc_team_a', 'mc_team_p_true bin']):
        for rec, c, mk in (('R0', '#2a78d6', 'o'), ('R1', '#1baf7a', '^')):
            s = CU[(CU.who == 'unwritten') & (CU.variable == var) & (CU.recall == rec) & (CU.readout == 'final')]
            if var == 'mc_team_a': s = s.assign(x=s.level.astype(float).astype(int)).sort_values('x'); xs = s.x.to_numpy()
            else: order = ['<0.1', '0.1-0.25', '0.25-0.5', '0.5-0.75', '0.75-0.9', '>=0.9']; s = s.set_index('level').reindex(order).dropna(subset=['estimate']).reset_index(); xs = np.array([order.index(v) for v in s.level])
            ax.errorbar(xs + (0.06 if rec == 'R1' else -0.06), s.estimate, yerr=[s.estimate - s.lo, s.hi - s.estimate], color=c, marker=mk, ms=8, capsize=3,
                        label=f'{rec} papers (unwritten authors)')
            for x, e, n in zip(xs, s.estimate, s.n_papers): ax.annotate(f'n={n}', (x + (0.06 if rec == 'R1' else -0.06), e), textcoords='offset points',
                                                                         xytext=(0, -16 if rec == 'R0' else 9), ha='center', fontsize=9, color='#52514e')
            if var != 'mc_team_a': ax.set_xticks(range(len(order))); ax.set_xticklabels(order)
        ax.axhline(0, color='#8a8984', lw=1)
        ax.set_xlabel('multiple-choice orders right (0-4)' if var == 'mc_team_a' else 'mean probability of the true option (binned)')
        ax.set_ylabel('output (L63) title-specific signal'); ax.legend(frameon=False, fontsize=10)
    fig.suptitle('Graded recognition: output signal of unwritten authors (plain means, team-bootstrap 95% CI; n < 30 = descriptive)', fontsize=13)
    fig.tight_layout(); fig.savefig(FIG / 'fig2_signal_vs_mc.png', dpi=120); plt.close(fig)
    # 3. primary contrasts: every version, one row each
    sty = {'within-bin': ('#2a78d6', 'o'), 'regression, bin FE only': ('#2a78d6', 'o'), 'paper-level regression, bin FE only': ('#52514e', 's'),
           'paper-level regression + confounders (add. 7)': ('#eb6834', 'D')}
    fig, ax = plt.subplots(figsize=(16, 13)); yv = 0; ticks, labs = [], []
    for c in R.contrast.unique():
        for _, r in R[R.contrast == c].iterrows():
            col, mk = sty.get(r.version, ('#1baf7a', '^') if 'first/other' in r.version or 'first authors' in r.version or 'other authors' in r.version else ('#6250d6', 'v'))
            ax.errorbar(r.estimate, yv, xerr=[[r.estimate - r.lo], [r.hi - r.estimate]], color=col, marker=mk, ms=9 if r.primary else 7, capsize=4,
                        lw=3 if r.primary else 1.5)
            ticks.append(yv); labs.append(('[PRIMARY] ' if r.primary else '') + f'{c} | {r.version}'); yv -= 1
        yv -= 0.6
    ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=9); ax.axvline(0, color='#8a8984', lw=1)
    ax.set_xlabel('estimate\nP1, P2: difference in output title-specific signal (unwritten authors); P3: change per MC order right')
    ax.set_title('Primary contrasts and regression versions (team-bootstrap 95% CI)\nblue = primary, grey = paper-level bin FE, orange = paper-level + confounders,\n'
                 'aqua / violet = author-level + confounders + position', fontsize=12, loc='right')
    fig.tight_layout(); fig.savefig(FIG / 'fig3_primary_contrasts.png', dpi=120); plt.close(fig)
    # 4. token roles at output
    r = GM[(GM.who == 'unwritten') & (GM.measure == 'spec') & (GM.readout == 'final')]
    fig, ax = plt.subplots(figsize=(16, 6.5)); roles = ['all'] + ROLES; w = 0.11
    for i, grp in enumerate(gc.GROUPS):
        s = r[r.group == grp].set_index('role').reindex(roles)
        x = np.arange(len(roles)) + (i - 3) * w
        ax.errorbar(x, s.estimate, yerr=[s.estimate - s.lo, s.hi - s.estimate], fmt=MK[grp], color=COL[grp], ms=7, capsize=2, label=NAME[grp])
    ax.set_xticks(range(len(roles))); ax.set_xticklabels(roles); ax.axhline(0, color='#8a8984', lw=1)
    ax.set_ylabel('output title-specific signal, unwritten authors'); ax.legend(frameon=False, fontsize=9, ncol=4)
    ax.set_title('Output (L63) signal by token role and group (plain means, team-bootstrap 95% CI)', fontsize=13)
    fig.tight_layout(); fig.savefig(FIG / 'fig4_roles_output.png', dpi=120); plt.close(fig)


def main():
    gc.check_plan()
    targets = [OUT / f for f in ['primary.csv', 'stage10_group_means.csv', 'stage10_contrasts.csv', 'stage10_dose.csv', 'stage10_curves.csv', 'papers_used.csv']]
    for t in targets: guard(t)
    REP.mkdir(parents=True, exist_ok=True); L = []
    D = Data(); P = D.P
    # exclusions
    ex = P[P.grp.isin(gc.GROUPS)]
    L.append('## Exclusions (rebuilt written count != label m)\n')
    L.append(pd.crosstab(ex.grp, ex.consistent).reindex(gc.GROUPS).to_string())
    L.append('')
    D.ok.reset_index()[['paper_id', 'grp', 'recall_level', 'mc_team_outcome_tight', 'citation_bin', 'field', 'year', 'n_authors', 'M', 'n_scored',
                        'n_unwritten_scored', 'first_written', 'share_initial', 'mc_team_a', 'mc_team_p_true']].to_csv(OUT / 'papers_used.csv', index=False)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        R, boots = primary(D, L); R.to_csv(OUT / 'primary.csv', index=False); np.savez(OUT / 'primary_boot.npz', **{f'{a}|{b}': v for (a, b), v in boots.items()})
        print(R.to_string(), flush=True)
        GM = group_means(D); GM.to_csv(OUT / 'stage10_group_means.csv', index=False); print('group means', len(GM), flush=True)
        CT = contrasts(D); CT.to_csv(OUT / 'stage10_contrasts.csv', index=False); print('contrasts', len(CT), flush=True)
        DO = dose(D); DO.to_csv(OUT / 'stage10_dose.csv', index=False); print('dose', len(DO), flush=True)
        CU = curves(D); CU.to_csv(OUT / 'stage10_curves.csv', index=False); print('curves', len(CU), flush=True)
    figures(GM, CU, R)
    (REP / 'stage10_tables.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    main()
