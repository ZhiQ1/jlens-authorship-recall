"""Bottleneck C ("neighbour confusion"): who are the FABRICATED author names in the open-recall answers?
EXPLORATORY (探索性), POST HOC. Not preregistered. CPU only, existing outputs only. 2026-11-14.

Answers: ORIGINAL label package open answers (labels_20261015/.../open_results.jsonl, field `names`; greedy, Qwen3-32B,
system+user chat prompt, run 2026-10-15_qwen3-32b_v3-measure-a100). Not the 2-11b regenerations.
Matcher: Stage 10 R0/R1 reconstruction (10_stage10/stage10_extra_r0r1.py words/same/match: surname + first initial,
given-first pass then surname-first pass, one-to-one), copied verbatim below (importing that module pulls in Stage 10/11
analysis code); equality with 391_groups/data/author_flags.parquet `written` is asserted.

Fabricated name = a generated name not consumed by the one-to-one match. Per paper, fabricated names are de-duplicated
by normalised word tuple. Pre-classes (excluded from the class shares, counted):
  single_token  - fewer than 2 words (cannot carry surname + initial; e.g. "Cumhur", truncated tails)
  repeat_true   - matches a true author of this paper under either order (a repeat/alias the one-to-one match did not use)
Classes (first match wins), name matched to an author by the same key rule (surname + first initial, either order;
an author with a one-word name matches on surname alone):
  1 coauthor     author of another cohort paper that shares an author key with this paper's true authors
  2 same_field   author of another cohort paper of the same field
  3 other_cohort author of any other cohort paper
  4 not_in_data
Sensitivity: identical, with full-name exact keys (normalised words joined, either order of the generated name's words).
Groups: group_tight target = A + C (R0/R1 x tight strong), control = B + D (R0/R1 x tight fail) (groups_core.papers()).
CI: author-team cluster bootstrap, 2,000 multinomial draws over teams of folds_own9108_k5s13.npz, seed 391; pooled
ratio (sum of class counts / sum of fabricated names over papers); 95% percentile interval.
Chance baselines (R draws each, same number of names per paper as its classifiable fabricated names):
  rand_author        random author entries of other cohort papers (uniform over entries)
  rand_author_field  random author entries of other cohort papers of the same field
  perm_fab           random fabricated names of other papers (keeps the model's name popularity)
  perm_fab_field     random fabricated names of other papers of the same field
"""
import os, re, sys, json, unicodedata
from pathlib import Path
from collections import defaultdict
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
LAB = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
OUT = Path(os.environ.get('FAB_OUT', BASE / '391_groups/summary_fabricated_20261114'))
NB = int(os.environ.get('FAB_NB', 2000)); R = int(os.environ.get('FAB_R', 20)); TINY = os.environ.get('FAB_TINY') == '1'
MAXFREQ = int(os.environ.get('FAB_MAXFREQ', 3))
CLASSES = ['coauthor', 'same_field', 'other_cohort', 'not_in_data']
GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s']


# ---------------------------------------------------------------- matcher, verbatim from stage10_extra_r0r1.py
def words(s): return [x for x in re.sub(r'[^a-z \-]', ' ', unicodedata.normalize('NFKD', s.replace('-', ' - ')).encode('ascii', 'ignore').decode().lower()).split() if x != '-']


def same(tw, gw, swap):
    if not tw or len(gw) < 2: return False
    ts, ti = tw[-1], (tw[0][0] if len(tw) > 1 else '')
    for gs, gi in ([(gw[-1], gw[0][0]), (gw[0], gw[1][0])] if swap else [(gw[-1], gw[0][0])]):
        if gs == ts and (not ti or gi == ti): return True
    return False


def match_used(true, gen):
    """match() of stage10_extra_r0r1.py, additionally returning the set of generated indices it consumed."""
    tw = [words(t) for t in true]; gw = [words(g) for g in gen]; used, hit = set(), [False] * len(true)
    for swap in (False, True):
        for i, t in enumerate(tw):
            if hit[i]: continue
            for j, g in enumerate(gw):
                if j not in used and same(t, g, swap): used.add(j); hit[i] = True; break
    return hit, used


# ---------------------------------------------------------------- keys
def akey_si(w):            # an author's key (surname, first initial or '')
    return (w[-1], w[0][0] if len(w) > 1 else '') if w else None


def gkeys_si(w):           # a generated name's candidate keys (given-first, surname-first)
    return {(w[-1], w[0][0]), (w[0], w[1][0])}


def hit_si(gk, S):
    return any(k in S or (k[0], '') in S for k in gk)


def akey_full(w): return ' '.join(w) if len(w) > 1 else None
def gkeys_full(w): return {' '.join(w), ' '.join(w[::-1])}
def hit_full(gk, S): return any(k in S for k in gk)


def build(P, akey, maxfreq=None):
    """per-paper key sets, coauthor key sets, field key sets (with counts so 'other papers' can exclude p).
    maxfreq: keys on more than maxfreq cohort papers are 'common' and dropped from every set (rare-key sensitivity)."""
    K = {}
    for pid, a in zip(P.paper_id, P.authors):
        K[pid] = {k for k in (akey(words(x)) for x in str(a).split('; ')) if k}
    Kown = {p: set(v) for p, v in K.items()}; common = set()
    if maxfreq is not None:
        fq = defaultdict(int)
        for ks in K.values():
            for k in ks: fq[k] += 1
        common = {k for k, c in fq.items() if c > maxfreq}
        K = {p: v - common for p, v in K.items()}
    k2p = defaultdict(set)
    for pid, ks in K.items():
        for k in ks: k2p[k].add(pid)
    CO = {}
    for pid, ks in K.items():
        nb = set().union(*[k2p[k] for k in ks]) - {pid} if ks else set()
        CO[pid] = (set().union(*[K[q] for q in nb]) - ks) if nb else set()
    field = dict(zip(P.paper_id, P.field))
    FK = defaultdict(lambda: defaultdict(int))      # field -> key -> number of papers
    AK = defaultdict(int)
    for pid, ks in K.items():
        for k in ks: FK[field[pid]][k] += 1; AK[k] += 1
    return K, CO, FK, AK, field, Kown, common


def classify(w, pid, K, CO, FK, AK, field, Kown, common, gkeys, hit):
    if len(w) < 2: return 'single_token'
    gk = gkeys(w); own = K[pid]
    if hit(gk, Kown[pid]): return 'repeat_true'
    if common and hit(gk, common): return 'common_key'
    if hit(gk, CO[pid]): return 'coauthor'
    # other papers in field / cohort: key present with count > (1 if own paper has it else 0); own keys never hit here
    fk = FK[field[pid]]
    def other(D):
        for k in gk:
            for kk in (k, (k[0], '')) if isinstance(k, tuple) else (k,):
                c = D.get(kk, 0) - (1 if kk in own else 0)
                if c > 0: return True
        return False
    if other(fk): return 'same_field'
    if other(AK): return 'other_cohort'
    return 'not_in_data'


# ---------------------------------------------------------------- bootstrap
class Boot:
    def __init__(self, pids):
        z = np.load(BASE / '381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz')
        T = dict(zip(z['ids'].astype(str), z['team'].astype(int)))
        codes, uniq = pd.factorize(pd.Series([T[p] for p in pids]))
        self.idx = pd.Series(codes, index=pids); self.nteam = len(uniq)
        self.cnt = np.random.default_rng(391).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)

    def ratio(self, pids, num, den):
        """num [n, k], den [n] -> est [k], lo, hi, boot [NB, k]"""
        W = self.cnt[:, self.idx.loc[pids].to_numpy()]
        with np.errstate(invalid='ignore', divide='ignore'):
            est = num.sum(0) / den.sum(); boot = (W @ num) / (W @ den)[:, None]
        return est, np.nanpercentile(boot, 2.5, 0), np.nanpercentile(boot, 97.5, 0), boot

    def mean(self, pids, v):
        W = self.cnt[:, self.idx.loc[pids].to_numpy()]
        with np.errstate(invalid='ignore', divide='ignore'):
            boot = (W @ v) / W.sum(1)[:, None]
        return v.mean(0), np.nanpercentile(boot, 2.5, 0), np.nanpercentile(boot, 97.5, 0), boot


def md(df):
    cols = list(df.columns)
    fm = lambda v: f'{v:.4g}' if isinstance(v, (float, np.floating)) else str(v)
    return '\n'.join(['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)] + ['| ' + ' | '.join(fm(v) for v in r) + ' |' for r in df.itertuples(index=False)])


def bin_order(b): return int(str(b).split('-')[0].rstrip('+'))


def merge_bins(counts_t, counts_c, bins, min_n=30):
    """walk bins low -> high, merge consecutive bins until both groups have >= min_n papers; leftover joins the last group."""
    out, cur, ct, cc = [], [], 0, 0
    for b in bins:
        cur.append(b); ct += counts_t.get(b, 0); cc += counts_c.get(b, 0)
        if ct >= min_n and cc >= min_n: out.append(cur); cur, ct, cc = [], 0, 0
    if cur:
        if out: out[-1] += cur
        else: out.append(cur)
    lab = {}
    for g in out:
        name = g[0] if len(g) == 1 else (g[0].split('-')[0] + '+' if g[-1].endswith('+') else g[0].split('-')[0] + '-' + g[-1].split('-')[-1])
        for b in g: lab[b] = name
    return lab, out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ['# Fabricated author names in the open-recall answers: neighbour confusion (bottleneck C)', '',
         '**Exploratory (探索性), post hoc. Not preregistered.** Generated by `~/jlens_work/14_groups/fabricated_names_20261114.py`.', '']
    P = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'authors', 'field', 'citation_bin', 'recall_level',
                                                               'mc_team_outcome_tight', 'group_tight', 'm'])
    r, o = P.recall_level, P.mc_team_outcome_tight
    P['grp'] = np.select([(r == 'R0') & (o == 'strong'), (r == 'R0') & (o == 'fail'), (r == 'R1') & (o == 'strong'), (r == 'R1') & (o == 'fail'),
                          (r == 'R0') & (o == 'uncertain'), (r == 'R1') & (o == 'uncertain'), (r == 'R2') & (o == 'strong')], GROUPS, 'other')
    assert ((P.group_tight == 'target') == P.grp.isin(['A', 'C'])).all() and ((P.group_tight == 'control') == P.grp.isin(['B', 'D'])).all()
    ans = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'names', 'parse_class']]
    P = P.merge(ans, on='paper_id', how='left'); assert P.names.notna().all()
    # --- matcher check vs author_flags
    hits, useds = zip(*[match_used(a.split('; '), n) for a, n in zip(P.authors, P.names)])
    au = pd.read_parquet(BASE / '391_groups/data/author_flags.parquet').sort_values(['paper_id', 'author_index'])
    mine = pd.DataFrame({'paper_id': P.paper_id, 'h': hits}).explode('h'); mine['author_index'] = mine.groupby('paper_id').cumcount()
    chk = au.merge(mine, on=['paper_id', 'author_index']); nbad = int((chk.written != chk.h.astype(bool)).sum())
    print('matcher mismatches vs author_flags:', nbad, 'of', len(chk), flush=True); assert nbad == 0 and len(chk) == len(au)
    P['mm'] = [sum(h) for h in hits]; P['consistent'] = P.mm == P.m.astype(int)
    # --- fabricated names
    rows = []
    for pid, n, u in zip(P.paper_id, P.names, useds):
        seen = set()
        for j, g in enumerate(n):
            if j in u: continue
            w = words(g); t = tuple(w)
            dup = t in seen; seen.add(t)
            rows.append((pid, j, g, ' '.join(w), dup))
    F = pd.DataFrame(rows, columns=['paper_id', 'gen_index', 'name', 'norm', 'dup_in_paper'])
    print('fabricated name occurrences', len(F), 'unique per paper', (~F.dup_in_paper).sum(), flush=True)
    if TINY:
        keep = set(P.paper_id.sample(600, random_state=1)); F = F[F.paper_id.isin(keep)]
    MODES = (('si', akey_si, gkeys_si, hit_si, None), ('full', akey_full, gkeys_full, hit_full, None), ('si_rare', akey_si, gkeys_si, hit_si, MAXFREQ))
    TAGS = [m[0] for m in MODES]
    S = {}
    for tag, akey, gk, ht, mf in MODES:
        S[tag] = build(P, akey, mf)
        F['cls_' + tag] = [classify(w.split(), p, *S[tag], gk, ht) for w, p in zip(F.norm, F.paper_id)]
        print(tag, F[~F.dup_in_paper]['cls_' + tag].value_counts().to_dict(), flush=True)
    F = F.merge(P[['paper_id', 'grp', 'group_tight', 'field', 'citation_bin', 'recall_level', 'consistent']], on='paper_id')
    F.to_parquet(OUT / 'fabricated_names.parquet', index=False)
    U = F[~F.dup_in_paper]

    # --- chance baselines (si keys and full keys)
    rng = np.random.default_rng(1114)
    entries = [(pid, x) for pid, a in zip(P.paper_id, P.authors) for x in str(a).split('; ')]
    E = pd.DataFrame(entries, columns=['paper_id', 'name']); E['field'] = E.paper_id.map(dict(zip(P.paper_id, P.field)))
    E['norm'] = [' '.join(words(x)) for x in E.name]; E = E[E.norm.str.count(' ') >= 1]
    def pool_draw(Q, pid, n):
        arr_p, arr_n = Q; out = []
        while len(out) < n:
            i = rng.integers(0, len(arr_p), 2 * n + 4)
            out += [arr_n[k] for k in i if arr_p[k] != pid]
        return out[:n]
    base_rows = []
    for tag, akey, gk, ht, mf in MODES:
        cl = U[U['cls_' + tag].isin(CLASSES)]
        need = cl.groupby('paper_id').size()
        fpool = cl[['paper_id', 'norm', 'field']]
        # pre-split pools by field for speed
        pools = {'rand_author': E, 'perm_fab': fpool}
        for bname in ['rand_author', 'rand_author_field', 'perm_fab', 'perm_fab_field']:
            src = pools['rand_author' if bname.startswith('rand') else 'perm_fab']
            byf = {f: (src[src.field == f].paper_id.to_numpy(), src[src.field == f].norm.to_numpy()) for f in P.field.unique()}
            allp = (src.paper_id.to_numpy(), src.norm.to_numpy())
            for rr in range(R):
                for pid, n in need.items():
                    fld = S[tag][4][pid]
                    Q = byf[fld] if bname.endswith('_field') else allp
                    for nm in pool_draw(Q, pid, n):
                        base_rows.append((tag, bname, rr, pid, classify(nm.split(), pid, *S[tag], gk, ht)))
            print('baseline', tag, bname, flush=True)
    Bdf = pd.DataFrame(base_rows, columns=['keys', 'baseline', 'draw', 'paper_id', 'cls'])
    Bdf = Bdf.merge(P[['paper_id', 'group_tight', 'grp']], on='paper_id')

    # --- tables
    boot = Boot(P.paper_id.to_numpy())
    def table(D, by, labels, tag, extra=None):
        out = []
        D = D[D['cls_' + tag].isin(CLASSES)]
        for lab in labels:
            d = D[D[by] == lab] if by else D
            if extra is not None: d = d[extra(d)]
            if d.empty: continue
            ct = pd.crosstab(d.paper_id, d['cls_' + tag]).reindex(columns=CLASSES, fill_value=0)
            num = ct.to_numpy(float); den = num.sum(1)
            est, lo, hi, _ = boot.ratio(ct.index.to_numpy(), num, den)
            pm, plo, phi, _ = boot.mean(ct.index.to_numpy(), num / den[:, None])
            # conditional on in-dataset (classes 1-3): coauthor share
            inn = num[:, :3].sum(1); ok = inn > 0
            ce, clo, chi, _ = boot.ratio(ct.index.to_numpy()[ok], num[ok][:, :1], inn[ok])
            for k, c in enumerate(CLASSES):
                out.append(dict(keys=tag, group=lab if by else 'all', n_papers=len(ct), n_names=int(den.sum()), cls=c, n=int(num[:, k].sum()),
                                share=est[k], lo=lo[k], hi=hi[k], paper_mean=pm[k], pm_lo=plo[k], pm_hi=phi[k]))
            out.append(dict(keys=tag, group=lab if by else 'all', n_papers=int(ok.sum()), n_names=int(inn.sum()), cls='coauthor|in_data',
                            n=int(num[:, 0].sum()), share=ce[0], lo=clo[0], hi=chi[0]))
        return pd.DataFrame(out)

    def btab(by, labels, tag):
        out = []
        b = Bdf[Bdf['keys'] == tag]
        for bname, d0 in b.groupby('baseline'):
            for lab in labels:
                d = d0[d0[by] == lab] if by else d0
                d = d[d.cls.isin(CLASSES)]
                if d.empty: continue
                per = d.groupby(['draw', 'cls']).size().unstack(fill_value=0).reindex(columns=CLASSES, fill_value=0)
                sh = per.div(per.sum(1), axis=0)
                cin = per['coauthor'] / per[CLASSES[:3]].sum(1)
                for c in CLASSES: out.append(dict(keys=tag, baseline=bname, group=lab if by else 'all', cls=c, share=sh[c].mean(), sd_over_draws=sh[c].std()))
                out.append(dict(keys=tag, baseline=bname, group=lab if by else 'all', cls='coauthor|in_data', share=cin.mean(), sd_over_draws=cin.std()))
        return pd.DataFrame(out)

    res, bres = [], []
    for tag in TAGS:
        res += [table(U, None, [None], tag), table(U, 'group_tight', ['target', 'control', 'guard', 'excluded'], tag), table(U, 'grp', GROUPS, tag)]
        bres += [btab('group_tight', ['target', 'control'], tag), btab('grp', GROUPS, tag)]
        b0 = Bdf[Bdf['keys'] == tag].assign(all='all');
    T1 = pd.concat(res, ignore_index=True); T1.to_csv(OUT / 'class_shares_by_group.csv', index=False)
    Bt = pd.concat(bres, ignore_index=True)
    # all-papers baseline
    ball = []
    for tag in TAGS:
        b = Bdf[(Bdf['keys'] == tag) & Bdf.cls.isin(CLASSES)]
        for bname, d in b.groupby('baseline'):
            per = d.groupby(['draw', 'cls']).size().unstack(fill_value=0).reindex(columns=CLASSES, fill_value=0); sh = per.div(per.sum(1), axis=0)
            cin = per['coauthor'] / per[CLASSES[:3]].sum(1)
            for c in CLASSES: ball.append(dict(keys=tag, baseline=bname, group='all', cls=c, share=sh[c].mean(), sd_over_draws=sh[c].std()))
            ball.append(dict(keys=tag, baseline=bname, group='all', cls='coauthor|in_data', share=cin.mean(), sd_over_draws=cin.std()))
    Bt = pd.concat([pd.DataFrame(ball), Bt], ignore_index=True); Bt.to_csv(OUT / 'chance_baselines.csv', index=False)

    # target - control difference (pooled ratio, paired bootstrap)
    diff = []
    for tag in TAGS:
        D = U[U['cls_' + tag].isin(CLASSES)]
        bs = {}
        for g in ('target', 'control'):
            d = D[D.group_tight == g]; ct = pd.crosstab(d.paper_id, d['cls_' + tag]).reindex(columns=CLASSES, fill_value=0)
            num = ct.to_numpy(float); est, _, _, bt = boot.ratio(ct.index.to_numpy(), num, num.sum(1)); bs[g] = (est, bt)
        de = bs['target'][0] - bs['control'][0]; db = bs['target'][1] - bs['control'][1]
        for k, c in enumerate(CLASSES):
            b = db[:, k]; b = b[np.isfinite(b)]
            diff.append(dict(keys=tag, cls=c, target_minus_control=de[k], lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5),
                             p=max(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / NB)))
    Dt = pd.DataFrame(diff); Dt.to_csv(OUT / 'target_minus_control.csv', index=False)

    # by citation bin (si and full), target vs control, merged bins
    bins = sorted(P.citation_bin.unique(), key=bin_order)
    Dsi = U[U.cls_si.isin(CLASSES)]
    pc = Dsi.drop_duplicates('paper_id').groupby(['group_tight', 'citation_bin']).size()
    lab, groups_b = merge_bins(pc.get('target', pd.Series(dtype=int)).to_dict(), pc.get('control', pd.Series(dtype=int)).to_dict(), bins)
    U2 = U.assign(bin_m=U.citation_bin.map(lab)); mb = list(dict.fromkeys(lab[b] for b in bins))
    bt = []
    for tag in TAGS:
        for b in mb:
            t = table(U2[U2.bin_m == b], 'group_tight', ['target', 'control'], tag); t.insert(1, 'citation_bin', b); bt.append(t)
    Tb = pd.concat(bt, ignore_index=True); Tb.to_csv(OUT / 'class_shares_by_bin.csv', index=False)
    # within-bin weighted target - control (weights n_t n_c / (n_t + n_c) on papers), coauthor and each class, si keys
    wb = []
    for tag in TAGS:
        D = U2[U2['cls_' + tag].isin(CLASSES)]
        est_sum = np.zeros(4); boot_sum = np.zeros((NB, 4)); wsum = 0
        for b in mb:
            parts = {}
            for g in ('target', 'control'):
                d = D[(D.bin_m == b) & (D.group_tight == g)]
                ct = pd.crosstab(d.paper_id, d['cls_' + tag]).reindex(columns=CLASSES, fill_value=0); num = ct.to_numpy(float)
                e, _, _, bb = boot.ratio(ct.index.to_numpy(), num, num.sum(1)); parts[g] = (e, bb, len(ct))
            nt, nc = parts['target'][2], parts['control'][2]; w = nt * nc / (nt + nc)
            est_sum += w * (parts['target'][0] - parts['control'][0]); boot_sum += w * (parts['target'][1] - parts['control'][1]); wsum += w
        e = est_sum / wsum; bb = boot_sum / wsum
        for k, c in enumerate(CLASSES):
            b_ = bb[:, k]; b_ = b_[np.isfinite(b_)]
            wb.append(dict(keys=tag, cls=c, within_bin_target_minus_control=e[k], lo=np.percentile(b_, 2.5), hi=np.percentile(b_, 97.5),
                           p=max(min(1, 2 * min((b_ <= 0).mean(), (b_ >= 0).mean())), 1 / NB), bins=' | '.join(mb)))
    Wt = pd.DataFrame(wb); Wt.to_csv(OUT / 'target_minus_control_within_bin.csv', index=False)

    # pre-class counts
    pre = U.groupby('group_tight').cls_si.value_counts().unstack(fill_value=0); pre.to_csv(OUT / 'preclass_counts_si.csv')
    pre_f = U.groupby('group_tight').cls_full.value_counts().unstack(fill_value=0)

    # --- examples
    ex = U[U.cls_si.isin(CLASSES)].sample(frac=1, random_state=0).groupby('cls_si').head(10)[['paper_id', 'group_tight', 'field', 'name', 'cls_si', 'cls_full', 'cls_si_rare']]
    ex = ex.merge(P[['paper_id', 'authors']], on='paper_id')
    ex.to_csv(OUT / 'examples.csv', index=False)

    # --- figure
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
        for ax, tag in zip(axes, TAGS):
            x = np.arange(4); wdt = 0.2
            for i, (g, col) in enumerate((('target', '#c0392b'), ('control', '#2c7fb8'))):
                t = T1[(T1['keys'] == tag) & (T1.group == g) & T1.cls.isin(CLASSES)].set_index('cls').reindex(CLASSES)
                ax.bar(x + (i - 1.5) * wdt, t.share, wdt, yerr=[t.share - t.lo, t.hi - t.share], color=col, label=f'{g} (observed)', capsize=2)
            for i, (bn, col) in enumerate((('perm_fab', '#999999'), ('rand_author', '#dddddd'))):
                t = Bt[(Bt['keys'] == tag) & (Bt.baseline == bn) & (Bt.group == 'all') & Bt.cls.isin(CLASSES)].set_index('cls').reindex(CLASSES)
                ax.bar(x + (i + 0.5) * wdt, t.share, wdt, color=col, edgecolor='k', lw=0.4, label=f'chance: {bn}')
            ax.set_xticks(x); ax.set_xticklabels(CLASSES); ax.set_ylim(0, 1)
            ax.set_title({'si': 'surname + first initial keys', 'full': 'full-name exact keys', 'si_rare': f'si keys on <= {MAXFREQ} papers'}[tag]); ax.set_ylabel('share of fabricated names')
        axes[0].legend(fontsize=7, frameon=False)
        fig.suptitle('Fabricated names in open answers by class (exploratory, post hoc; team-bootstrap 95% CI)', fontsize=10)
        fig.tight_layout(); fig.savefig(OUT / 'fabricated_classes.png', dpi=140); plt.close(fig)
    except Exception as e:
        print('figure failed (non-fatal):', e, flush=True)

    # --- report
    def f3(v): return f'{100 * v:.1f}%'
    def row(t, g, c, tag='si'):
        x = T1[(T1['keys'] == tag) & (T1.group == g) & (T1.cls == c)]
        return '-' if x.empty else f'{f3(x.share.iloc[0])} [{f3(x.lo.iloc[0])}, {f3(x.hi.iloc[0])}]'
    def brow(bn, g, c, tag='si'):
        x = Bt[(Bt['keys'] == tag) & (Bt.baseline == bn) & (Bt.group == g) & (Bt.cls == c)]
        return '-' if x.empty else f3(x.share.iloc[0])
    nn = lambda g, tag='si': T1[(T1['keys'] == tag) & (T1.group == g) & (T1.cls == 'coauthor')]
    L += ['## Data', '',
          f'- Answers: ORIGINAL label package open answers (`{LAB}/open_results.jsonl`, greedy, run 2026-10-15_qwen3-32b_v3-measure-a100), '
          'not the 2-11b regenerations.',
          '- Matcher: Stage 10 R0/R1 reconstruction (surname + first initial, either order, one-to-one), verbatim; '
          f'per-author hits equal `391_groups/data/author_flags.parquet` (0 mismatches). Papers whose rebuilt count != label m: {int((~P.consistent).sum())} (kept).',
          f'- Fabricated name occurrences: {len(F)}; unique within paper: {len(U)}. Pre-classes (excluded from shares): '
          f'single_token {int((U.cls_si == "single_token").sum())}, repeat_true {int((U.cls_si == "repeat_true").sum())} (si keys).',
          '- Target = group_tight target = A + C (R0/R1 with tight strong team MC); control = B + D (R0/R1, tight fail). Same as Stage 10 / Addendum 7.',
          f'- CI: author-team cluster bootstrap, {NB} draws over {boot.nteam} teams (folds_own9108_k5s13.npz), pooled ratio. Chance baselines: {R} draws each.', '',
          '## Main table (surname + first initial keys; share of classifiable fabricated names, 95% CI)', '',
          '| class | target (A+C) | control (B+D) | all papers | chance: random cohort author | chance: random same-field author | chance: permuted fabricated names | chance: permuted, same field |',
          '|---|---|---|---|---|---|---|---|']
    for c in CLASSES + ['coauthor|in_data']:
        L.append(f'| {c} | {row(T1, "target", c)} | {row(T1, "control", c)} | {row(T1, "all", c)} | {brow("rand_author", "all", c)} | '
                 f'{brow("rand_author_field", "all", c)} | {brow("perm_fab", "all", c)} | {brow("perm_fab_field", "all", c)} |')
    L += ['', f'n: target {int(nn("target").n_papers.iloc[0])} papers / {int(nn("target").n_names.iloc[0])} names; control {int(nn("control").n_papers.iloc[0])} / '
          f'{int(nn("control").n_names.iloc[0])}; all {int(nn("all").n_papers.iloc[0])} / {int(nn("all").n_names.iloc[0])}. '
          '`coauthor|in_data` = coauthor share among names found in the dataset (classes 1-3).', '',
          'Chance baselines restricted to target / control papers are in `chance_baselines.csv`.', '',
          '## Target - control (pooled ratio, paired team bootstrap)', '', md(Dt), '',
          '## Target - control within citation bin (weights n_t n_c / (n_t + n_c), merged bins)', '', md(Wt.drop(columns='bins')), '',
          f'Merged bins (adjacent bins merged until both target and control have >= 30 papers with classifiable fabricated names): {" | ".join(mb)}', '',
          ]
    for tg, ttl in (('full', 'full-name exact keys'), ('si_rare', f'surname + first initial keys, only keys on <= {MAXFREQ} cohort papers (names hitting a commoner key = pre-class common_key, excluded)')):
        x = nn('all', tg)
        L += [f'## Sensitivity: {ttl}', '', f'n all: {int(x.n_papers.iloc[0])} papers / {int(x.n_names.iloc[0])} names; pre-classes: {U["cls_" + tg].value_counts().to_dict()}', '',
              '| class | target | control | all | chance: random cohort author | chance: permuted fabricated | chance: permuted, same field |', '|---|---|---|---|---|---|---|']
        for c in CLASSES + ['coauthor|in_data']:
            L.append(f'| {c} | {row(T1, "target", c, tg)} | {row(T1, "control", c, tg)} | {row(T1, "all", c, tg)} | {brow("rand_author", "all", c, tg)} | {brow("perm_fab", "all", c, tg)} | {brow("perm_fab_field", "all", c, tg)} |')
        L.append('')
    L += ['## By group A/B/C/D (si keys)', '', '| group | n papers | n names | ' + ' | '.join(CLASSES) + ' |', '|---|---|---|' + '---|' * 4]
    for g in GROUPS:
        x = nn(g)
        if x.empty: continue
        L.append(f'| {g} | {int(x.n_papers.iloc[0])} | {int(x.n_names.iloc[0])} | ' + ' | '.join(row(T1, g, c) for c in CLASSES) + ' |')
    L += ['', '## By citation bin (si keys), coauthor share', '', '| bin | target n papers | target coauthor | control n papers | control coauthor | target not_in_data | control not_in_data |', '|---|---|---|---|---|---|---|']
    for b in mb:
        t = Tb[(Tb['keys'] == 'si') & (Tb.citation_bin == b)]
        g = lambda gg, c: t[(t.group == gg) & (t.cls == c)]
        s = lambda x: '-' if x.empty else f'{f3(x.share.iloc[0])} [{f3(x.lo.iloc[0])}, {f3(x.hi.iloc[0])}]'
        npap = lambda gg: '-' if g(gg, 'coauthor').empty else int(g(gg, 'coauthor').n_papers.iloc[0])
        L.append(f'| {b} | {npap("target")} | {s(g("target", "coauthor"))} | {npap("control")} | {s(g("control", "coauthor"))} | {s(g("target", "not_in_data"))} | {s(g("control", "not_in_data"))} |')
    L += ['', '## Caveats', '',
          '- Exploratory, post hoc. Name keys are coarse: surname + first initial collides for common surnames (Wang Y, Smith J), so '
          'coauthor / in-dataset matches include homonyms (e.g. "Xiao-Yan Liu" -> liu x links any paper with a Liu X.; common Chinese and Korean surnames dominate the coauthor class). '
          'The random-author baselines do not carry this paper-specific collision; the permuted-fabricated baselines carry the name popularity but not the '
          'pairing of a paper with same-origin common names; the rare-key sensitivity (si_rare) removes common keys. Full-name exact keys '
          'under-match because many cohort names are initials only (Semantic Scholar "S. Bree").',
          '- The coauthor network is built from the 9,108-paper cohort only (shared author key on another cohort paper), not from the outside literature: '
          '"not_in_data" includes real people outside the cohort.',
          '- Pooled ratio over names: papers with many fabricated names (cut-off loops) weigh more; paper-mean shares are in the csv (`paper_mean`).',
          '- Single-token names and names repeating a true author are excluded from shares (counts above).', '']
    (OUT / 'report.md').write_text('\n'.join(L)); print('\n'.join(L), flush=True)
    json.dump(dict(n_fab_occ=len(F), n_fab_unique=len(U), NB=NB, R=R, tiny=TINY), open(OUT / 'run.json', 'w'))


if __name__ == '__main__':
    main()
