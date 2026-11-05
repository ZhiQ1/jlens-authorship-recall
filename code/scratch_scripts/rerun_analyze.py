"""Addendum 8 GPU re-runs: analysis (CPU). Same estimands as Stage 11 / 12, on UNWRITTEN authors (addendum 7), team CIs.

Groups: A, B, C, D = Stage 11 sample papers (E1/E2: 361_stage11/raw; P1/P2: 371_stage12/raw), split by papers.parquet
recall_level x mc_team_outcome_tight; R2 = R2 x strong re-run; U0 = 600 R0 x uncertain re-run (391_groups/raw).
Estimands (per name token log10(1/rank); author tokens -> paper means over the selected authors' tokens; group = ratio of
paper means, as stage11_analyze / stage12_analyze):
  E1 recovery R(l) = mean(patched_l - false) / mean(true - false)
  E2 loss(l)       = mean(k64 - k_l) / mean(true - false_0)      (true / false_0 from the same rows' E1 run)
  P1 recovery      = mean(item_l - none_l) / mean(true - none_l)  (tokens whose tail has the offset only)
  P2 recovery      = mean(comp - none) / mean(true - none)
Author sets: unwritten (primary; addendum 7 circularity rule; papers whose rebuilt written count != m are dropped),
unwritten_first / unwritten_other (addendum 8 author position), written (reference only, never a conclusion).
Intervals: 95% percentile, 2,000 draws of ONE multinomial draw over author teams (groups_core.Engine, seed 391: the same
draw as the addendum-7 analysis), shared by all groups -> paired contrasts. Contrasts (all descriptive / reference; R2 is a
reference group; U0 descriptive vs A and B): plain difference of group ratios, and a within-bin version (bin-standardised
ratio sum_b w_b mean_b(num) / sum_b w_b mean_b(den), w_b = n_a n_b / (n_a + n_b), bins with >= 10 papers in both).
n rule: n < 30 papers -> 'descriptive only' (interval reported but flagged). Continuous recognition: E1/E2 by mc_team_a
(0-4) and by mc_team_p_true band within R0 papers (A + U0 + B).
Outputs (OUT = 391_groups, or RERUN_OUT): reports/rerun_report.md, summary_rerun/*.csv
"""
import importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
R11 = BASE / '361_stage11'; R12 = BASE / '371_stage12'
OUT = Path(os.environ.get('RERUN_OUT', BASE / '391_groups')); TINY = os.environ.get('RERUN_TINY') == '1'
CFG = OUT / 'config' if TINY else BASE / '391_groups/config'
S = OUT / 'summary_rerun'; REP = OUT / 'reports'
sys.path.insert(0, str(H / '14_groups'))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))
def fmt(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def load_dir(d, scalar=('layers', 'items', 'comps')):
    fs = sorted(Path(d).glob('shard_*.npz'))
    if not fs: return None
    zs = [np.load(f, allow_pickle=True) for f in fs]
    return {k: (zs[0][k] if k in scalar else np.concatenate([z[k] for z in zs])) for k in zs[0].files if k != 'meta'}


# ------------------------------------------------------------------ data
def author_table():
    """paper_id, author_index, written, consistent (Stage 10 R0/R1 reconstruction via groups_build.author_flags)."""
    f = BASE / '391_groups/data/author_flags.parquet'
    if f.exists(): au = pd.read_parquet(f)
    else:
        gb = load(H / '14_groups/groups_build.py', 'gb'); r01 = load(H / '10_stage10/stage10_extra_r0r1.py', 'r01'); au = gb.author_flags(r01)
    return au[['paper_id', 'author_index', 'written', 'consistent']]


def setup():
    P = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'recall_level', 'mc_team_outcome_tight', 'citation_bin', 'mc_team_a', 'mc_team_p_true', 'm'])
    r, o = P.recall_level, P.mc_team_outcome_tight
    P['grp'] = np.select([(r == 'R0') & (o == 'strong'), (r == 'R0') & (o == 'fail'), (r == 'R1') & (o == 'strong'), (r == 'R1') & (o == 'fail'),
                          (r == 'R0') & (o == 'uncertain'), (r == 'R2') & (o == 'strong')], ['A', 'B', 'C', 'D', 'U0', 'R2'], 'other')
    P = P.set_index('paper_id')
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index']).set_index('row_id')
    au = author_table().set_index(['paper_id', 'author_index'])
    gc = load(H / '14_groups/groups_core.py', 'gc_core')
    E = gc.Engine(pd.DataFrame(index=P.index))
    return P, tk, au, E


def token_frame(row_id, tk, au, P):
    t = tk.loc[row_id]; k = pd.MultiIndex.from_arrays([t.paper_id.to_numpy(), t.author_index.to_numpy()])
    a = au.reindex(k)
    df = pd.DataFrame({'paper_id': t.paper_id.to_numpy(), 'author_index': t.author_index.to_numpy(),
                       'written': a.written.to_numpy(), 'consistent': a.consistent.to_numpy()})
    return df


WHO = {'unwritten': lambda d: (d.written == False) & (d.consistent == True),                       # noqa: E712
       'unwritten_first': lambda d: (d.written == False) & (d.consistent == True) & (d.author_index == 0),
       'unwritten_other': lambda d: (d.written == False) & (d.consistent == True) & (d.author_index > 0),
       'written': lambda d: (d.written == True) & (d.consistent == True)}


def paper_means(base, cols, who, valid=None):
    """base: token frame + value columns; returns paper-level means of cols over tokens of the author set."""
    sel = WHO[who](base).to_numpy()
    out = {}
    for c in cols:
        ok = sel & np.isfinite(base[c].to_numpy()) & (valid[c] if valid is not None and c in valid else True)
        out[c] = pd.Series(base[c].to_numpy()[ok]).groupby(base.paper_id.to_numpy()[ok]).mean()
    return pd.DataFrame(out)


# ------------------------------------------------------------------ estimators
class Est:
    def __init__(self, P, E): self.P, self.E = P, E

    def ratio(self, pp, num, den):
        """pp: paper frame; returns est, lo, hi, n, boot."""
        ok = pp[num].notna() & pp[den].notna(); x = pp[ok]
        if len(x) == 0: return np.nan, np.nan, np.nan, 0, np.full(self.E.cnt.shape[0], np.nan)
        W = self.E.W(x.index.to_numpy()); a, b = x[num].to_numpy(), x[den].to_numpy()
        with np.errstate(invalid='ignore', divide='ignore'): boot = (W @ a) / (W @ b)
        lo, hi = self.E.ci(boot); return a.mean() / b.mean(), lo, hi, len(x), boot

    def mean(self, pp, col):
        x = pp[col].dropna()
        if len(x) == 0: return np.nan, np.nan, np.nan, 0, np.full(self.E.cnt.shape[0], np.nan)
        W = self.E.W(x.index.to_numpy()); boot = (W @ x.to_numpy()) / W.sum(1); lo, hi = self.E.ci(boot)
        return x.mean(), lo, hi, len(x), boot

    def within_bin_ratio(self, ppa, ppb, num, den, min_n=10):
        xa = ppa[ppa[num].notna() & ppa[den].notna()]; xb = ppb[ppb[num].notna() & ppb[den].notna()]
        ba = self.P.citation_bin.reindex(xa.index); bb = self.P.citation_bin.reindex(xb.index)
        bins = [b for b in sorted(set(ba) & set(bb)) if (ba == b).sum() >= min_n and (bb == b).sum() >= min_n]
        if not bins: return np.nan, np.nan, np.nan, 0
        w = np.array([(ba == b).sum() * (bb == b).sum() / ((ba == b).sum() + (bb == b).sum()) for b in bins]); w = w / w.sum()
        def std(x, bx, boot):
            nu = de = 0
            for wi, b in zip(w, bins):
                s = x[(bx == b).to_numpy()]
                if boot:
                    W = self.E.W(s.index.to_numpy()); c = W.sum(1)
                    with np.errstate(invalid='ignore', divide='ignore'): nu = nu + wi * (W @ s[num].to_numpy()) / c; de = de + wi * (W @ s[den].to_numpy()) / c
                else: nu += wi * s[num].mean(); de += wi * s[den].mean()
            return nu / de
        est = std(xa, ba, False) - std(xb, bb, False)
        with np.errstate(invalid='ignore', divide='ignore'): boot = std(xa, ba, True) - std(xb, bb, True)
        lo, hi = self.E.ci(boot); return est, lo, hi, len(bins)


# ------------------------------------------------------------------ build per-experiment paper tables
def e1_tokens(d, tk, au, P):
    base = token_frame(d['row_id'], tk, au, P); base['row_id'] = d['row_id']
    base['true'] = nlr(d['rank_true']); base['false'] = nlr(d['rank_false'])
    for i, l in enumerate(d['layers']): base[f'p{int(l)}'] = nlr(d['rank_patch'][:, i])
    return base, [int(l) for l in d['layers']]


def e2_tokens(k, e1base, tk, au, P):
    base = token_frame(k['row_id'], tk, au, P); base['row_id'] = k['row_id']
    for i, l in enumerate(k['layers']): base[f'k{int(l)}'] = nlr(k['rank_ko'][:, i])
    tf = e1base.set_index('row_id')[['true', 'false']]
    base['true'] = tf['true'].reindex(base.row_id).to_numpy(); base['false'] = tf['false'].reindex(base.row_id).to_numpy()
    return base, [int(l) for l in k['layers']]


def sources():
    """{exp: {group: dict}} for the original (A-D) and re-run (R2, U0) outputs."""
    src = {}
    for e, root in (('patch', R11), ('knockout', R11), ('patch_pos', R12), ('patch_comp', R12)):
        src[e] = {'orig': load_dir(root / 'raw' / e)}
        for g in ('R2', 'U0'):
            src[e][g] = load_dir(OUT / 'raw' / e / g)
    return src


def main():
    t0 = time.time(); S.mkdir(parents=True, exist_ok=True); REP.mkdir(parents=True, exist_ok=True)
    P, tk, au, E = setup(); X = Est(P, E); src = sources()
    smp11 = pd.read_parquet(R11 / 'config/sample.parquet'); lists = {g: pd.read_parquet(CFG / f) for g, f in (('R2', 'rerun_R2.parquet'), ('U0', 'rerun_U0_600.parquet'))}
    groups_of = {}                                                        # group -> paper ids (design list)
    for g in ('A', 'B', 'C', 'D'): groups_of[g] = set(smp11.paper_id[P.grp.reindex(smp11.paper_id).to_numpy() == g])
    for g in ('R2', 'U0'): groups_of[g] = set(lists[g].paper_id)
    rows, curves, counts = [], [], []
    boots = {}

    def add(exp, who, layer, item, g, pp, num, den, key):
        e, lo, hi, n, b = X.ratio(pp, num, den); boots[(exp, who, layer, item, g)] = (b, pp)
        rows.append(dict(experiment=exp, who=who, layer=layer, item=item, group=g, n_papers=n, estimate=e, lo=lo, hi=hi,
                         den_mean=pp[den].dropna().mean() if n else np.nan, descriptive_only=n < 30))

    # ---------------- E1 / E2
    e1 = {}; e2 = {}
    for g in ('orig', 'R2', 'U0'):
        if src['patch'][g] is not None: e1[g] = e1_tokens(src['patch'][g], tk, au, P)
        if src['knockout'][g] is not None and g in e1: e2[g] = e2_tokens(src['knockout'][g], e1[g][0], tk, au, P)
    PL = next(iter(e1.values()))[1]; KL = next(iter(e2.values()))[1] if e2 else []
    tabs = {}
    for who in WHO:
        for exp, data, LL in (('E1', e1, PL), ('E2', e2, KL)):
            for g in ('A', 'B', 'C', 'D', 'U0', 'R2'):
                s = 'orig' if g in 'ABCD' else g
                if s not in data: continue
                base = data[s][0]; base = base[base.paper_id.isin(groups_of[g])]
                cols = ['true', 'false'] + ([f'p{l}' for l in LL] if exp == 'E1' else [f'k{l}' for l in LL])
                pp = paper_means(base, cols, who)
                pp['gap'] = pp['true'] - pp['false']
                if exp == 'E1':
                    for l in LL: pp[f'num{l}'] = pp[f'p{l}'] - pp['false']
                    for l in LL: add('E1', who, l, 'recovery', g, pp, f'num{l}', 'gap', None)
                    m = X.mean(pp, 'gap'); rows.append(dict(experiment='E1', who=who, layer=-1, item='true_minus_false', group=g, n_papers=m[3], estimate=m[0], lo=m[1], hi=m[2], descriptive_only=m[3] < 30))
                else:
                    for l in LL:
                        if l == 64: continue
                        pp[f'num{l}'] = pp['k64'] - pp[f'k{l}']; add('E2', who, l, 'loss', g, pp, f'num{l}', 'gap', None)
                tabs[(exp, who, g)] = pp
                if who == 'unwritten': counts.append(dict(experiment=exp, group=g, design_papers=len(groups_of[g]), papers_with_rows=base.paper_id.nunique(),
                                                          papers_unwritten=len(pp.dropna(subset=['gap'])), authors_unwritten=int(base[WHO[who](base)].groupby(['paper_id', 'author_index']).ngroups),
                                                          authors_written=int(base[WHO['written'](base)].groupby(['paper_id', 'author_index']).ngroups),
                                                          inconsistent_papers=int(base[base.consistent == False].paper_id.nunique())))   # noqa: E712
    # ---------------- P1 / P2 (R2 + A-D)
    for exp, key in (('P1', 'patch_pos'), ('P2', 'patch_comp')):
        for s in ('orig', 'R2'):
            d = src[key][s]
            if d is None: continue
            base = token_frame(d['row_id'], tk, au, P); base['true'] = nlr(d['rank_true']); R = nlr(d['rank_patch'])
            if exp == 'P1':
                items = list(d['items']); layers = [int(l) for l in d['layers']]; valid = d['valid'] if 'valid' in d else np.ones((R.shape[0], R.shape[2]), bool)
                cols = ['true']; vmask = {}
                for li, l in enumerate(layers):
                    for ii, it in enumerate(items):
                        c = f'{it}@{l}'; base[c] = R[:, li, ii]; cols.append(c)
                        if it != 'none': vmask[c] = valid[:, ii]
                labs = [(it, l) for l in layers for it in items if it != 'none']
            else:
                comps = list(d['comps']); vmask = None; cols = ['true']
                for ci, c in enumerate(comps): base[c] = R[:, ci]; cols.append(c)
                labs = [(c, None) for c in comps if c != 'none']
            for who in WHO:
                for g in (['A', 'B', 'C', 'D'] if s == 'orig' else ['R2']):
                    b = base[base.paper_id.isin(groups_of[g])].reset_index(drop=True)
                    vm = {k: v[base.paper_id.isin(groups_of[g]).to_numpy()] for k, v in vmask.items()} if vmask else None
                    if exp == 'P1':
                        # numerator and denominator over the same valid tokens per item: paper means of (item - none) and (true - none)
                        for it, l in labs:
                            c = f'{it}@{l}'; nb = b.assign(num=b[c] - b[f'none@{l}'], den=b['true'] - b[f'none@{l}'])
                            pp = paper_means(nb, ['num', 'den'], who, valid={'num': vm[c], 'den': vm[c]})
                            add('P1', who, l, it, g, pp, 'num', 'den', None)
                    else:
                        nb = b.copy(); ncols = []
                        for c, _ in labs: nb[f'n_{c}'] = nb[c] - nb['none']; ncols.append(f'n_{c}')
                        nb['den'] = nb['true'] - nb['none']; pp = paper_means(nb, ncols + ['den'], who)
                        for c, _ in labs:
                            kind = c.rstrip('0123456789'); add('P2', who, int(c[len(kind):]), kind, g, pp, f'n_{c}', 'den', None)
    G = pd.DataFrame(rows); G.to_csv(S / 'rerun_group_values.csv', index=False)
    C = pd.DataFrame(counts); C.to_csv(S / 'rerun_counts.csv', index=False)
    # ---------------- contrasts (descriptive / reference), paired team bootstrap
    CON = [('U0', 'A'), ('U0', 'B'), ('A', 'B'), ('R2', 'A'), ('R2', 'C'), ('C', 'A')]
    crow = []
    for (exp, who, layer, item, g), (b, pp) in boots.items():
        for a_, b_ in CON:
            if g != a_ or (exp, who, layer, item, b_) not in boots: continue
            ba, ppa = boots[(exp, who, layer, item, a_)]; bb, ppb = boots[(exp, who, layer, item, b_)]
            ra = G[(G.experiment == exp) & (G.who == who) & (G.layer == layer) & (G['item'] == item)].set_index('group')
            est = ra.estimate[a_] - ra.estimate[b_]; d = ba - bb; lo, hi = E.ci(d)
            num, den = ('num', 'den') if exp == 'P1' else (None, None)
            if exp in ('E1', 'E2'): num, den = f'num{layer}', 'gap'
            elif exp == 'P2': num, den = f'n_{item}{layer}', 'den'
            wb = X.within_bin_ratio(ppa, ppb, num, den) if num in ppa else (np.nan,) * 4
            crow.append(dict(experiment=exp, who=who, layer=layer, item=item, contrast=f'{a_} - {b_}', n_a=int(ra.n_papers[a_]), n_b=int(ra.n_papers[b_]),
                             diff=est, lo=lo, hi=hi, p=E.pval(d), within_bin=wb[0], wb_lo=wb[1], wb_hi=wb[2], wb_n_bins=wb[3],
                             descriptive_only=min(ra.n_papers[a_], ra.n_papers[b_]) < 30))
    CC = pd.DataFrame(crow); CC.to_csv(S / 'rerun_contrasts.csv', index=False)
    # ---------------- continuous recognition within R0 (A + U0 + B), E1 / E2 unwritten (= all authors in R0)
    for exp in ('E1', 'E2'):
        parts = [tabs[(exp, 'unwritten', g)] for g in ('A', 'U0', 'B') if (exp, 'unwritten', g) in tabs]
        if not parts: continue
        pp = pd.concat(parts); pp = pp.join(P[['mc_team_a', 'mc_team_p_true', 'grp']])
        pp['a'] = pd.to_numeric(pp.mc_team_a, errors='coerce'); pp['pt'] = pd.to_numeric(pp.mc_team_p_true, errors='coerce')
        pp['ptb'] = pd.cut(pp.pt, [0, .2, .4, .6, .8, 1.0001], right=False, labels=['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1'])
        LL = [24, 32, 40, 48, 52] if exp == 'E1' else [0, 32, 40, 48, 52]
        for var in ('a', 'ptb'):
            for lev, s in pp.groupby(var, observed=True):
                for l in LL:
                    e, lo, hi, n, _ = X.ratio(s, f'num{l}', 'gap'); m = X.mean(s, 'gap')
                    curves.append(dict(experiment=exp, by='mc_team_a' if var == 'a' else 'mc_team_p_true band', level=str(lev), layer=l, n_papers=n, estimate=e, lo=lo, hi=hi,
                                       gap=m[0], gap_lo=m[1], gap_hi=m[2], share_U0=float((s.grp == 'U0').mean()), descriptive_only=n < 30))
    CV = pd.DataFrame(curves); CV.to_csv(S / 'rerun_curves_R0.csv', index=False)
    report(G, CC, CV, C, PL, KL)
    num_den(tabs, X, E, PL, KL)
    print(f'RERUN ANALYZED in {time.time() - t0:.0f}s', flush=True)


ND_LAYERS = [24, 32, 40, 48, 52, 56]


def num_den(tabs, X, E, PL, KL):
    """user addition 2026-11-05: numerator, denominator and ratio per group and layer, team CIs (E1 and E2)."""
    rows = []; bt = {}
    for exp in ('E1', 'E2'):
        for g in ('A', 'B', 'C', 'D', 'U0', 'R2'):
            for who in (['unwritten', 'written'] if g in ('C', 'R2') else ['unwritten']):
                if (exp, who, g) not in tabs: continue
                pp = tabs[(exp, who, g)]
                for l in ND_LAYERS:
                    if f'num{l}' not in pp: continue
                    x = pp.dropna(subset=[f'num{l}', 'gap'])
                    if not len(x): continue
                    n_ = X.mean(x, f'num{l}'); d_ = X.mean(x, 'gap'); r_ = X.ratio(x, f'num{l}', 'gap')
                    bt[(exp, who, g, l)] = (n_[4], d_[4], r_[4])
                    rows.append(dict(experiment=exp, who=who, group=g, layer=l, n_papers=len(x),
                                     numerator=n_[0], num_lo=n_[1], num_hi=n_[2], denominator=d_[0], den_lo=d_[1], den_hi=d_[2],
                                     ratio=r_[0], ratio_lo=r_[1], ratio_hi=r_[2], descriptive_only=len(x) < 30))
    D = pd.DataFrame(rows); D.to_csv(S / 'e1_e2_num_den.csv', index=False)
    # B - A paired (shared team draw): numerator, denominator, ratio
    crow = []
    for exp in ('E1', 'E2'):
        for l in ND_LAYERS:
            if (exp, 'unwritten', 'A', l) not in bt or (exp, 'unwritten', 'B', l) not in bt: continue
            a = D[(D.experiment == exp) & (D.who == 'unwritten') & (D.group == 'A') & (D.layer == l)].iloc[0]
            b = D[(D.experiment == exp) & (D.who == 'unwritten') & (D.group == 'B') & (D.layer == l)].iloc[0]
            r = dict(experiment=exp, layer=l)
            for j, k in enumerate(('numerator', 'denominator', 'ratio')):
                d = bt[(exp, 'unwritten', 'B', l)][j] - bt[(exp, 'unwritten', 'A', l)][j]; lo, hi = E.ci(d)
                r |= {f'B_minus_A_{k}': b[k] - a[k], f'{k}_lo': lo, f'{k}_hi': hi}
            r['B_over_A_numerator'] = b.numerator / a.numerator; r['B_over_A_denominator'] = b.denominator / a.denominator
            crow.append(r)
    BA = pd.DataFrame(crow); BA.to_csv(S / 'e1_e2_num_den_B_minus_A.csv', index=False)
    L = ['# E1 / E2: numerator, denominator and ratio by group (addendum 8 re-runs + Stage 11 originals)', '',
         'E1: numerator = mean over papers of (patched_l - false_0), denominator = mean(true - false_0), R = ratio. '
         'E2: numerator = mean(clean - knocked from l) (clean = explicit-mask baseline k64), same denominator, loss = ratio. '
         'log10(1/rank) per name token, paper means over the author set; 95% team-cluster bootstrap (2,000, seed 391, shared draw). '
         'Unwritten authors (primary); written authors for C and R2 are a reference only. A/B/C/D: Stage 11 sample (original raw); U0, R2: re-runs. '
         'R2 is an upper reference only (no conclusion is drawn from it); ceiling reference: the written-author title-specific signal at the output, +0.844 (group analysis). n < 30: descriptive only.', '']
    for exp in ('E1', 'E2'):
        L += [f'## {exp}', '', '| layer | group | authors | n | numerator [CI] | denominator [CI] | ' + ('R' if exp == 'E1' else 'loss') + ' [CI] |', '|---|---|---|---|---|---|---|']
        for l in ND_LAYERS:
            for r in D[(D.experiment == exp) & (D.layer == l)].itertuples():
                tag = ' (reference)' if r.group == 'R2' or r.who == 'written' else ''
                L.append(f'| L{l} | {r.group}{tag} | {r.who} | {r.n_papers}{" (n<30)" if r.descriptive_only else ""} | {fmt(r.numerator, r.num_lo, r.num_hi)} | '
                         f'{fmt(r.denominator, r.den_lo, r.den_hi)} | {fmt(r.ratio, r.ratio_lo, r.ratio_hi)} |')
        L.append('')
    L += ['## B - A (unwritten; paired team bootstrap)', '', '| exp | layer | numerator B - A | denominator B - A | ratio B - A | B/A numerator | B/A denominator |', '|---|---|---|---|---|---|---|']
    for r in BA.itertuples():
        L.append(f'| {r.experiment} | L{r.layer} | {fmt(r.B_minus_A_numerator, r.numerator_lo, r.numerator_hi)} | {fmt(r.B_minus_A_denominator, r.denominator_lo, r.denominator_hi)} | '
                 f'{fmt(r.B_minus_A_ratio, r.ratio_lo, r.ratio_hi)} | {r.B_over_A_numerator:.2f} | {r.B_over_A_denominator:.2f} |')
    L += ['', '<!--NOTE-->', '']
    (REP / 'e1_num_den.md').write_text('\n'.join(L) + '\n'); print('wrote', REP / 'e1_num_den.md')


def md_table(df):
    return '\n'.join(['| ' + ' | '.join(map(str, df.columns)) + ' |', '|' + '---|' * df.shape[1]] + ['| ' + ' | '.join(map(str, r)) + ' |' for r in df.itertuples(index=False)])


def report(G, CC, CV, C, PL, KL):
    L = ['# Addendum 8 GPU re-runs: R2 x strong and R0 x uncertain (U0, 600) - E1, E2, P1, P2', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `14_groups/rerun_analyze.py`. Spec: `config/prereg_addendum8_groups.json` (GPU re-runs) + addendum 7. '
         'Estimands as Stage 11/12 (ratio of paper means; log10(1/rank) per name token). All values on UNWRITTEN authors (papers with an inconsistent '
         'written-count rebuild dropped); written-author values in the CSVs are a reference only. 95% intervals: team-cluster bootstrap (2,000; seed 391, shared draw). '
         'A/B/C/D = Stage 11 sample papers (original E1/E2 and Stage 12 P1/P2 runs). R2 = reference group, never a conclusion; U0 vs A/B is descriptive. '
         'n < 30 papers: descriptive only.', '',
         'R2 is an upper reference only: R2 numbers are shown as a reference column and no R2 contrast is a conclusion. Ceiling reference: the written-author title-specific signal at the output, +0.844 (group analysis).', '']
    L += ['## Counts (E1 rows)', '', md_table(C), '']
    def val(exp, who, layer, item, g):
        r = G[(G.experiment == exp) & (G.who == who) & (G.layer == layer) & (G['item'] == item) & (G.group == g)]
        if not len(r): return 'n/a'
        r = r.iloc[0]; s = fmt(r.estimate, r.lo, r.hi) if np.isfinite(r.lo) else f'{r.estimate:+.3f}'
        return s + (' (n<30)' if r.descriptive_only else '')
    gs = ['A', 'B', 'C', 'D', 'U0', 'R2']
    for who in ('unwritten', 'unwritten_first', 'unwritten_other'):
        L += [f'## E1 recovery R(l) - {who} authors', '', '| layer | ' + ' | '.join(gs) + ' |', '|---|' + '---|' * len(gs)]
        L.append('| true - false | ' + ' | '.join(val('E1', who, -1, 'true_minus_false', g) for g in gs) + ' |')
        for l in PL: L.append(f'| L{l} | ' + ' | '.join(val('E1', who, l, 'recovery', g) for g in gs) + ' |')
        L += ['', f'## E2 knockout loss(l) - {who} authors', '', '| from layer | ' + ' | '.join(gs) + ' |', '|---|' + '---|' * len(gs)]
        for l in KL:
            if l != 64: L.append(f'| L{l} | ' + ' | '.join(val('E2', who, l, 'loss', g) for g in gs) + ' |')
        L.append('')
    g4 = ['A', 'B', 'C', 'D', 'R2']
    for who in ('unwritten', 'unwritten_first', 'unwritten_other'):
        L += [f'## P1 single positions - {who} authors (items p1 = ":", names, all)', '', '| item | layer | ' + ' | '.join(g4) + ' |', '|---|---|' + '---|' * len(g4)]
        for it in ('p1', 'p5', 'names', 'all'):
            for l in sorted(G[(G.experiment == 'P1')].layer.unique()):
                L.append(f'| {it} | L{l} | ' + ' | '.join(val('P1', who, l, it, g) for g in g4) + ' |')
        L += ['', f'## P2 attention vs MLP - {who} authors', '', '| comp | layer | ' + ' | '.join(g4) + ' |', '|---|---|' + '---|' * len(g4)]
        for c in ('attn', 'mlp'):
            for l in sorted(G[(G.experiment == 'P2')].layer.unique()):
                L.append(f'| {c} | L{l} | ' + ' | '.join(val('P2', who, l, c, g) for g in g4) + ' |')
        L.append('')
    if len(CC):
        L += ['## Contrasts (descriptive; R2 rows are reference values, not conclusions), unwritten authors, selected layers', '',
              '| exp | layer/item | contrast | n_a / n_b | difference [CI] | within-bin [CI] (bins) |', '|---|---|---|---|---|---|']
        sel = CC[(CC.who == 'unwritten') & (((CC.experiment == 'E1') & CC.layer.isin([40, 48, 52])) | ((CC.experiment == 'E2') & CC.layer.isin([32, 40, 48, 52])) |
                                            ((CC.experiment == 'P1') & CC['item'].isin(['p1', 'names']) & CC.layer.isin([48, 52])) |
                                            ((CC.experiment == 'P2') & CC.layer.isin([48, 52, 56])))]
        for r in sel.itertuples():
            wb = fmt(r.within_bin, r.wb_lo, r.wb_hi) + f' ({r.wb_n_bins})' if np.isfinite(r.within_bin) else 'n/a'
            L.append(f'| {r.experiment} | L{r.layer} {r.item} | {r.contrast}{" (reference only)" if "R2" in r.contrast else ""} | {r.n_a} / {r.n_b} | {fmt(r.diff, r.lo, r.hi)}{" (n<30)" if r.descriptive_only else ""} | {wb} |')
        L.append('')
    if len(CV):
        L += ['## Continuous recognition within R0 (A + U0 + B): E1 recovery / E2 loss by MC orders right (mc_team_a) and p_true band', '',
              '| exp | by | level | n | ' + ' | '.join(f'L{l}' for l in [24, 32, 40, 48, 52]) + ' | true - false |', '|---|---|---|---|' + '---|' * 6]
        for (exp, by, lev), s in CV.groupby(['experiment', 'by', 'level'], sort=False):
            s = s.set_index('layer'); n = int(s.n_papers.iloc[0])
            cells = [(fmt(s.estimate[l], s.lo[l], s.hi[l]) if l in s.index else '') for l in ([24, 32, 40, 48, 52] if exp == 'E1' else [0, 32, 40, 48, 52])]
            L.append(f'| {exp} | {by} | {lev} | {n}{" (n<30)" if n < 30 else ""} | ' + ' | '.join(cells) + f' | {s.gap.iloc[0]:+.3f} |')
        L.append('\nE2 columns are L0, L32, L40, L48, L52 (start layer).')
    (REP / 'rerun_report.md').write_text('\n'.join(L) + '\n'); print('wrote', REP / 'rerun_report.md')


if __name__ == '__main__':
    main()
