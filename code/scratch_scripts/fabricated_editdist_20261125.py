"""Slide 125 follow-up (user 2026-11-25; POST-HOC, exploratory; CPU, existing data only; nothing existing is edited).
Are the "not in the data" fabricated names (cls_si == not_in_data, de-duplicated per paper; 20,286 of 40,219) misspelled true names?

Input: 391_groups/summary_fabricated_20261114/fabricated_names.parquet (fabricated_names_20261114.py) + cohort papers.parquet.
Normalisation for distances: words() of that script (= Stage 10 matcher: NFKD, accents dropped, lower case, non-letters -> space,
hyphen splits words). Library = every author entry of the 9,108 cohort papers.
Generated name w (>= 2 words) is read in both orders, as the matcher does: given-first (surname w[-1], initial w[0][0],
full = w) and surname-first (surname w[0], initial w[1][0], full = w[1:] + w[:1]); a one-letter word is never read as a surname
(fix after the tiny run: 'M. J. van Spronsen' read surname-first gave surname 'm' -> spurious neighbours 'ma', 'e', 'o').
Distances (Levenshtein, minimum over both orders):
  D_full   full normalised name string vs author full string
  D_si     surname vs author surname, only authors whose first initial agrees (or who have no given name) = matcher key + edits
  D_sur    surname vs author surname, initial ignored
  D_given  given-name distance to the nearest-by-D_full author (descriptive; initials vs full names make it noisy)
Bucket 0 "normalisation difference": the name matches a library author's key (surname + initial, either order) or full string
  under the stronger 2-11b rev3 normalisation (words3: ae/oe/ue folding, ss/ae/o transliteration, Jr/Sr/II-IV dropped,
  hyphen groups) although it does not under words().
Exact search for distance <= 2 by symmetric deletion (every pair within 2 edits shares a <= 2-deletion variant), verified by DP.
Item 2 ("misspelled true name"): d_own <= 2 AND d_own == D (a true author of THIS paper is among the nearest library names).
Item 3 (chance): paper labels permuted (each paper's names compared with another paper's true authors), R draws, global and
within field; same statistic. Team-cluster bootstrap CI (folds_own9108_k5s13 teams, 2,000 draws, seed 391) for the observed shares.
Outputs: 391_groups/summary_fabricated_editdist_20261125/{names_editdist.parquet, report.md, shares.csv, examples_own_near.csv}
"""
import os, sys, json, time, importlib.util
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); H = Path.home() / 'jlens_work'
SRC = BASE / '391_groups/summary_fabricated_20261114'; OUT = Path(os.environ.get('ED_OUT', BASE / '391_groups/summary_fabricated_editdist_20261125'))
R = int(os.environ.get('ED_R', 200)); NB = int(os.environ.get('ED_NB', 2000)); TINY = os.environ.get('ED_TINY') == '1'


def load(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


FN = load(H / '14_groups/fabricated_names_20261114.py', 'fab')     # words() of the slide-125 classification
words = FN.words
V3 = load(H / '13_stage13/stage13_b2_gennames_b_v3.py', 'gnv3')     # words3 (rev3 normalisation)
words3 = V3.words3


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def lev(a, b):
    if a == b: return 0
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def dels(s, k=2):
    out = {s}
    for d in range(1, min(k, len(s)) + 1):
        for ix in combinations(range(len(s)), d):
            out.add(''.join(c for i, c in enumerate(s) if i not in ix))
    return out


class Index:
    """symmetric-deletion index over a set of strings; near(q) -> {string: distance} for distance <= 2."""
    def __init__(self, strings):
        self.idx = defaultdict(set)
        for s in strings:
            for v in dels(s): self.idx[v].add(s)
    def near(self, q):
        cand = set()
        for v in dels(q): cand |= self.idx.get(v, set())
        out = {}
        for c in cand:
            d = lev(q, c)
            if d <= 2: out[c] = d
        return out


def orients(w):
    """both readings as in the matcher, but a one-letter word (an initial) is never read as a surname; if neither reading has a
    surname of >= 2 letters, both are kept."""
    o = [(w[-1], w[0][0], ' '.join(w)), (w[0], w[1][0], ' '.join(w[1:] + w[:1]))]
    k = [x for x in o if len(x[0]) >= 2]
    return k or o


def akey(w): return (w[-1], w[0][0] if len(w) > 1 else '')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    P = pd.read_parquet(BASE / '351_stage10/cohort/papers.parquet', columns=['paper_id', 'authors', 'field', 'group_tight'])
    F = pd.read_parquet(SRC / 'fabricated_names.parquet'); F = F[~F.dup_in_paper]
    N = F[F.cls_si == 'not_in_data'].reset_index(drop=True)
    if TINY: N = N.sample(400, random_state=1).reset_index(drop=True)
    log('not_in_data names', len(N), 'of classifiable', int(F.cls_si.isin(FN.CLASSES).sum()))
    # ---- library
    A = {pid: [w for w in (words(x) for x in str(a).split('; ')) if w] for pid, a in zip(P.paper_id, P.authors)}
    full_lib = {' '.join(w) for ws in A.values() for w in ws}
    sur_lib = {w[-1] for ws in A.values() for w in ws if len(w[-1]) >= 2}   # one-letter surnames (initials only) not indexed
    sur_inits = defaultdict(set)                         # surname -> initials present ('' = author without given name)
    for ws in A.values():
        for w in ws: sur_inits[w[-1]].add(w[0][0] if len(w) > 1 else '')
    full_to_given = defaultdict(set)
    for ws in A.values():
        for w in ws: full_to_given[' '.join(w)].add(w[0] if len(w) > 1 else '')
    A3 = {pid: [w for w in (words3(x) for x in str(a).split('; ')) if w] for pid, a in zip(P.paper_id, P.authors)}
    key3 = {akey(w) for ws in A3.values() for w in ws}; key3s = {k for k in key3 if k[1] == ''}; full3 = {' '.join(w) for ws in A3.values() for w in ws}
    log('library: full', len(full_lib), 'surnames', len(sur_lib))
    IF, IS = Index(full_lib), Index(sur_lib); log('indexes built')
    own_full = {pid: {' '.join(w) for w in ws} for pid, ws in A.items()}
    own_key = {pid: {akey(w) for w in ws} for pid, ws in A.items()}
    own_sur = {pid: {w[-1] for w in ws} for pid, ws in A.items()}
    rows = []
    for t, r in enumerate(N.itertuples()):
        w = r.norm.split(); o = orients(w)
        # bucket 0: rev3 normalisation hit
        w3 = words3(r.name); n0 = False
        if len(w3) >= 2:
            ks = {(w3[-1], w3[0][0]), (w3[0], w3[1][0])}
            n0 = any(k in key3 or (k[0], '') in key3s for k in ks) or ' '.join(w3) in full3 or ' '.join(w3[1:] + w3[:1]) in full3
        # D_full + nearest set
        nf = {}
        for _, _, f in o:
            for s, d in IF.near(f).items(): nf[s] = min(d, nf.get(s, 9))
        Dfull = min(nf.values()) if nf else 3
        near_full = {s for s, d in nf.items() if d == Dfull} if nf else set()
        within_full = set(nf)
        # D_si / D_sur + nearest key sets
        nsi, nsu = {}, {}
        for su, ini, _ in o:
            for s, d in IS.near(su).items():
                nsu[s] = min(d, nsu.get(s, 9))
                for i_ in sur_inits[s]:
                    if i_ == '' or i_ == ini: nsi[(s, i_)] = min(d, nsi.get((s, i_), 9))
        Dsi = min(nsi.values()) if nsi else 3; Dsu = min(nsu.values()) if nsu else 3
        near_si = {k for k, d in nsi.items() if d == Dsi} if nsi else set(); within_si = set(nsi)
        near_su = {s for s, d in nsu.items() if d == Dsu} if nsu else set(); within_su = set(nsu)
        # own paper
        def own_d(near_d, ownset): return min([near_d[x] for x in ownset if x in near_d], default=3)
        do_full = own_d(nf, own_full[r.paper_id]); do_si = own_d(nsi, own_key[r.paper_id] | {(k[0], '') for k in own_key[r.paper_id] if k[1] == ''}); do_su = own_d(nsu, own_sur[r.paper_id])
        g = np.nan
        if near_full:
            s0 = sorted(near_full)[0]; gg = [x for x in full_to_given[s0] if x]
            gen_g = [w[0], w[1]]
            g = float(min([lev(a, b) for a in gen_g for b in gg])) if gg else np.nan
        rows.append(dict(paper_id=r.paper_id, name=r.name, norm=r.norm, group_tight=r.group_tight, field=r.field, norm0_rev3=n0,
                         D_full=Dfull, D_si=Dsi, D_sur=Dsu, D_given_at_nearest_full=g,
                         own_full=do_full, own_si=do_si, own_sur=do_su,
                         near_full=sorted(near_full), near_si=sorted('|'.join(k) for k in near_si), near_sur=sorted(near_su),
                         within_full=sorted(within_full), within_si=sorted('|'.join(k) for k in within_si), within_sur=sorted(within_su)))
        if t % 2000 == 0: log(t)
    D = pd.DataFrame(rows); D.to_parquet(OUT / 'names_editdist.parquet', index=False)
    # ---- statistics
    own_sets = {'full': {p: own_full[p] for p in A}, 'si': {p: {'|'.join(k) for k in own_key[p]} for p in A}, 'sur': own_sur}
    def stat(df, owner):            # owner: paper_id -> paper whose authors are "own"
        res = {}
        for m in ('full', 'si', 'sur'):
            os_ = own_sets[m]; nn = df['near_' + m]; ww = df['within_' + m]; Dm = df['D_' + m].to_numpy()
            own_near = np.array([bool(set(a) & os_[owner[p]]) for a, p in zip(nn, df.paper_id)]) & (Dm <= 2)
            own_within = np.array([bool(set(a) & os_[owner[p]]) for a, p in zip(ww, df.paper_id)])
            res[m] = (own_near, own_within)
        return res
    ident = {p: p for p in A}; obs = stat(D, ident)
    # team bootstrap over papers
    z = np.load(BASE / '381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz'); T = dict(zip(z['ids'].astype(str), z['team'].astype(int)))
    codes, uniq = pd.factorize(D.paper_id.map(T)); W = np.random.default_rng(391).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB)[:, codes].astype(float)
    def bci(v): b = (W @ v) / W.sum(1); return float(v.mean()), *np.percentile(b, [2.5, 97.5])
    # permutations
    pids = np.array(sorted(D.paper_id.unique())); fld = dict(zip(P.paper_id, P.field)); rng = np.random.default_rng(1125)
    perm = {'global': [], 'field': []}
    for rr in range(R):
        g = dict(zip(pids, rng.permutation(pids)))
        byf = defaultdict(list)
        for p in pids: byf[fld[p]].append(p)
        f_ = {}
        for f, ps in byf.items(): f_.update(dict(zip(ps, rng.permutation(ps))))
        for nm, owner in (('global', g), ('field', f_)):
            s = stat(D, owner); perm[nm].append({m: (s[m][0].mean(), s[m][1].mean()) for m in s})
    rows = []
    for m in ('full', 'si', 'sur'):
        e, lo, hi = bci(obs[m][0].astype(float)); e2, lo2, hi2 = bci(obs[m][1].astype(float))
        for nm in perm:
            a = np.array([x[m][0] for x in perm[nm]]); b = np.array([x[m][1] for x in perm[nm]])
            rows.append(dict(measure=m, perm=nm, own_nearest_le2=e, lo=lo, hi=hi, perm_mean=a.mean(), perm_p95=np.percentile(a, 95), perm_max=a.max(),
                             p_perm=float((a >= e).mean()), own_within2=e2, lo_w=lo2, hi_w=hi2, perm_within2_mean=b.mean(), perm_within2_max=b.max()))
    S = pd.DataFrame(rows); S.to_csv(OUT / 'shares.csv', index=False)
    # distributions
    dist = {}
    for m in ('full', 'si', 'sur'):
        v = D['D_' + m].to_numpy(); n0 = D.norm0_rev3.to_numpy()
        dist[m] = {'0 (rev3 normalisation)': float(n0.mean()), '0 (words())': float(((v == 0) & ~n0).mean()), '1': float(((v == 1) & ~n0).mean()),
                   '2': float(((v == 2) & ~n0).mean()), '>=3': float(((v >= 3) & ~n0).mean())}
    by_grp = {g: {m: float(obs[m][0][(D.group_tight == g).to_numpy()].mean()) for m in obs} for g in ('target', 'control')}
    ex = D[obs['si'][0] | obs['full'][0]].copy(); ex['own_authors'] = ex.paper_id.map(dict(zip(P.paper_id, P.authors)))
    ex.sample(min(60, len(ex)), random_state=0)[['paper_id', 'name', 'D_full', 'D_si', 'D_sur', 'own_full', 'own_si', 'near_full', 'near_si', 'own_authors']].to_csv(OUT / 'examples_own_near.csv', index=False)
    J = dict(n=len(D), dist=dist, by_group=by_grp, R=R)
    (OUT / 'summary.json').write_text(json.dumps(J, indent=1))
    L = ['# Not-in-data fabricated names: nearest cohort author by edit distance (POST-HOC, exploratory)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `14_groups/fabricated_editdist_20261125.py`. Names: {len(D)}. Permutations: {R}.', '',
         '## Distance distribution (share of not-in-data names)', '', '| measure | ' + ' | '.join(dist['full']) + ' |', '|---|' + '---|' * len(dist['full'])]
    L += [f'| {m} | ' + ' | '.join(f'{x:.3f}' for x in dist[m].values()) + ' |' for m in dist]
    L += ['', '## Own true author among the nearest library names, distance <= 2', '', FN.md(S), '',
          '## By group (observed own-nearest share)', '', json.dumps(by_grp, indent=1)]
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); log('done')


if __name__ == '__main__':
    main()
