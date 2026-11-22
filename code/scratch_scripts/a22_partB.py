#!/usr/bin/env python3
"""Addendum 22 Part B (LOCKED 2026-11-21, 391_groups/config/prereg_addendum22.md): variance decomposition of the
last-title-token state (authors prompt) into surface S / meaning M / identity I / topic prior P, CPU only, existing cache.

Stages:  embed            text-model embeddings (bert-base-uncased, all-mpnet-base-v2; title and author string),
                          Qwen surname-first token ids -> OUT/features.npz
         layer L          ridge decomposition at layer L (5 outer team folds) -> OUT/layer_L.npz (per-paper SSE / SST)
         combine          team bootstrap (2,000, seed 22), Holm over B = {8,16,24,32,40,48}, D1-D3 -> OUT/report.md + CSVs
Options: --test (600 papers, 2 layers) --out DIR
Locked definitions (§3): input = AUTHORS question, last title token, one row per paper; y = top 256 PCs of the state
(PCA on training folds); out-of-fold R² variance-weighted over the 256 targets; folds = stage13_cpu.group_folds (team
folds); unique R²(G) = R²(S∪M∪I∪P) − R²(without G); I = year, log citations, field one-hot, author-name embedding, Qwen
surname-token one-hot (tokens with ≥ 20 papers + other); P = field-level surname-frequency prior (2 cols, out of fold);
version a (decision) = I and P residualised on S∪M out of fold; version b (descriptive) = raw.
"""
import argparse, hashlib, importlib.util, json, os, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); R10 = J / '351_stage10'; R13 = J / '381_stage13'
LOCK = J / '391_groups/config/prereg_addendum22.md'; LOCK_SHA = 'd648ef11fe9bad02277ae495db86f56c4ee8e9d9d0758ebd1f890418a63bc79c'
HF = Path(os.environ.get('HF_HOME', '/scratch/zhang.zhiqi2/hf'))
LAYERS_ALL = [4, 8, 16, 24, 32, 40, 48]; FAMILY = [8, 16, 24, 32, 40, 48]
NPC, NB, SEED, MIN_TOK = 256, 2000, 22, 20
ALPHAS = [0.1, 1.0, 10.0, 100.0, 1000.0]   # relative to trace(A'A)/p; grid widened after the tiny test hit the top value 10


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def load(path, name):
    argv = sys.argv; sys.argv = [argv[0]]
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    sys.argv = argv; return m


def check_lock():
    h = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if h != LOCK_SHA: raise SystemExit(f'LOCK CHANGED {h}')


def snapshot(repo):
    d = HF / 'hub' / ('models--' + repo.replace('/', '--')) / 'snapshots'; return sorted(d.iterdir())[-1]


def cohort(test):
    pids = np.load(R13 / 'summary_m3/resid_cache_pids.npy')
    P = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id').loc[pids]
    idx = np.arange(len(pids))
    if test: idx = np.sort(np.random.default_rng(0).choice(len(pids), 600, replace=False))
    return pids, P, idx


def surname(a):
    w = [x for x in re.split(r'\s+', str(a).strip()) if x]; return w[-1] if w else ''


# ------------------------------------------------------------------ embed
def embed(a):
    pids, P, idx = cohort(a.test); P = P.iloc[idx]
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.set_num_threads(int(os.environ.get('SLURM_CPUS_PER_TASK', 8)))
    titles = list(P.title.astype(str)); authors = [str(x) for x in P.authors]
    out = {}
    for repo, tag in (('bert-base-uncased', 'bert'), ('sentence-transformers/all-mpnet-base-v2', 'mpnet')):
        d = snapshot(repo); tk = AutoTokenizer.from_pretrained(d); md = AutoModel.from_pretrained(d).eval()
        for kind, txt in (('title', titles), ('auth', authors)):
            E = np.zeros((len(txt), md.config.hidden_size), np.float32)
            for s in range(0, len(txt), 64):
                enc = tk(txt[s:s + 64], padding=True, truncation=True, max_length=128, return_tensors='pt')
                with torch.no_grad(): h = md(**enc).last_hidden_state
                m = enc['attention_mask'].unsqueeze(-1).float(); E[s:s + 64] = ((h * m).sum(1) / m.sum(1)).numpy()
            out[f'{tag}_{kind}'] = E; log(tag, kind, E.shape)
    qtok = AutoTokenizer.from_pretrained(snapshot('Qwen/Qwen3-32B'))
    first_tok = np.array([qtok.encode(' ' + surname(str(au).split('; ')[0]), add_special_tokens=False)[0] for au in authors])
    all_toks = [[qtok.encode(' ' + surname(x), add_special_tokens=False)[0] for x in str(au).split('; ') if surname(x)] for au in authors]
    L = max(len(t) for t in all_toks); T = np.full((len(authors), L), -1, np.int64)
    for i, t in enumerate(all_toks): T[i, :len(t)] = t
    np.savez(Path(a.out) / 'features.npz', pid=P.index.to_numpy(), first_tok=first_tok, all_toks=T, **out)
    log('embed done', len(P))


# ------------------------------------------------------------------ ridge helpers
def std(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6; return (Xtr - mu) / sd, (Xte - mu) / sd


def ridge(A, Y, alpha):
    G = A.T @ A; sc = np.trace(G) / G.shape[0]
    return np.linalg.solve(G + alpha * sc * np.eye(G.shape[0]), A.T @ Y)


def inner_folds(teams, k=5):
    u, inv = np.unique(teams, return_inverse=True)
    return (np.random.default_rng(SEED).permutation(len(u))[inv]) % k


def residualise(Ztr, Zte, Btr, Bte, teams_tr, alpha=1.0):
    """Z on basis B: out-of-fold residuals for train rows (inner team folds), residual for test rows from all-train fit."""
    Btr_s, Bte_s = std(Btr, Bte); Ztr_c = Ztr - Ztr.mean(0); Rtr = np.zeros_like(Ztr)
    f = inner_folds(teams_tr)
    for k in range(5):
        tr, te = f != k, f == k
        if tr.sum() == 0 or te.sum() == 0: continue
        mu = Ztr[tr].mean(0); W = ridge(Btr_s[tr], Ztr[tr] - mu, alpha); Rtr[te] = Ztr[te] - (Btr_s[te] @ W + mu)
    W = ridge(Btr_s, Ztr_c, alpha); Rte = Zte - (Bte_s @ W + Ztr.mean(0))
    return Rtr, Rte


# ------------------------------------------------------------------ layer
def layer(a):
    check_lock()
    L = int(a.layer); pids, P, idx = cohort(a.test)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    F = np.load(Path(a.out) / 'features.npz', allow_pickle=True)
    assert (F['pid'] == pids[idx]).all()
    Pp = P.iloc[idx]; n = len(idx)
    folds, team = c13.group_folds(pids[idx])
    mm = np.memmap(R13 / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=(len(pids), 3, 15, 2, 5120))
    li = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63].index(L)
    X = np.asarray(mm[idx, 0, li, 0], dtype=np.float32)                       # authors task, title_last
    log('layer', L, 'X', X.shape)
    titles = list(Pp.title.astype(str))
    fields = sorted(Pp.field.unique()); FLD = (Pp.field.to_numpy()[:, None] == np.array(fields)[None]).astype(np.float32)
    ATTR = np.column_stack([Pp.year.to_numpy(float), np.log10(1 + Pp.citations.to_numpy(float)), FLD]).astype(np.float32)
    ft = F['first_tok']; vc = pd.Series(ft).value_counts(); keep = vc[vc >= MIN_TOK].index.to_numpy()
    OH = np.zeros((n, len(keep) + 1), np.float32); pos = {t: j for j, t in enumerate(keep)}
    for i, t in enumerate(ft): OH[i, pos.get(t, len(keep))] = 1
    AT = F['all_toks']; fld = Pp.field.to_numpy()
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD, PCA
    from scipy.sparse import hstack
    res = {}; meta = dict(layer=L, n=n, n_onehot_cols=int(OH.shape[1]), pca_var_share=[])
    alpha_sel = {}
    for k in np.unique(folds):
        tr, te = folds != k, folds == k
        # y: top-256 PCs fitted on train
        pca = PCA(NPC, svd_solver='randomized', random_state=SEED).fit(X[tr])
        Ytr, Yte = pca.transform(X[tr]), pca.transform(X[te]); meta['pca_var_share'].append(float(pca.explained_variance_ratio_.sum()))
        ymu = Ytr.mean(0); sst = ((Yte - ymu) ** 2).sum(1)
        # S: tf-idf word 1-2 + char 3-5, SVD 256 on train
        vw = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True); vc_ = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=3, sublinear_tf=True)
        ttr = [titles[i] for i in np.where(tr)[0]]; tte = [titles[i] for i in np.where(te)[0]]
        Mtr = hstack([vw.fit_transform(ttr), vc_.fit_transform(ttr)]).tocsr(); Mte = hstack([vw.transform(tte), vc_.transform(tte)]).tocsr()
        svd = TruncatedSVD(256, random_state=SEED).fit(Mtr); Str, Ste = svd.transform(Mtr), svd.transform(Mte)
        # P: field-level surname-frequency prior, out of fold (train rows leave-one-out)
        cnt = {}
        for i in np.where(tr)[0]:
            for t in AT[i][AT[i] >= 0]: cnt[(fld[i], t)] = cnt.get((fld[i], t), 0) + 1
        def prior(i, self_in):
            toks = AT[i][AT[i] >= 0]
            c = [cnt.get((fld[i], t), 0) - (1 if self_in else 0) for t in toks]
            return [np.mean(np.log1p(np.maximum(c, 0))), np.log1p(max(c[0], 0)) if c else 0.0]
        PRtr = np.array([prior(i, True) for i in np.where(tr)[0]], np.float32); PRte = np.array([prior(i, False) for i in np.where(te)[0]], np.float32)
        for dec in ('bert', 'mpnet'):
            Mt, Me = F[f'{dec}_title'][tr], F[f'{dec}_title'][te]; Atr, Ate = F[f'{dec}_auth'][tr], F[f'{dec}_auth'][te]
            Itr_raw = np.hstack([ATTR[tr], Atr, OH[tr]]); Ite_raw = np.hstack([ATTR[te], Ate, OH[te]])
            n_attr, n_auth = ATTR.shape[1], Atr.shape[1] + OH.shape[1]
            Btr, Bte = np.hstack([Str, Mt]), np.hstack([Ste, Me])
            Ir_tr, Ir_te = residualise(Itr_raw, Ite_raw, Btr, Bte, team[tr]); Pr_tr, Pr_te = residualise(PRtr, PRte, Btr, Bte, team[tr])
            for ver, (Itr, Ite, Ptr, Pte) in (('a', (Ir_tr, Ir_te, Pr_tr, Pr_te)), ('b', (Itr_raw, Ite_raw, PRtr, PRte))):
                blocks_tr = dict(S=Str, M=Mt, I_attr=Itr[:, :n_attr], I_auth=Itr[:, n_attr:], P=Ptr)
                blocks_te = dict(S=Ste, M=Me, I_attr=Ite[:, :n_attr], I_auth=Ite[:, n_attr:], P=Pte)
                models = {'full': ['S', 'M', 'I_attr', 'I_auth', 'P'], '-S': ['M', 'I_attr', 'I_auth', 'P'], '-M': ['S', 'I_attr', 'I_auth', 'P'],
                          '-I': ['S', 'M', 'P'], '-P': ['S', 'M', 'I_attr', 'I_auth'], '-I_auth': ['S', 'M', 'I_attr', 'P'], '-I_attr': ['S', 'M', 'I_auth', 'P']}
                for mname, bl in models.items():
                    Atr_, Ate_ = std(np.hstack([blocks_tr[b] for b in bl]), np.hstack([blocks_te[b] for b in bl]))
                    key = (dec, ver)
                    if key not in alpha_sel:                                         # alpha by inner CV on fold-0 train, full model
                        f2 = inner_folds(team[tr]); errs = []
                        for al in ALPHAS:
                            e = 0.0
                            for kk in range(5):
                                a_, b_ = f2 != kk, f2 == kk; mu = Ytr[a_].mean(0)
                                W = ridge(Atr_[a_], Ytr[a_] - mu, al); e += ((Atr_[b_] @ W + mu - Ytr[b_]) ** 2).sum()
                            errs.append(e)
                        alpha_sel[key] = ALPHAS[int(np.argmin(errs))]; log('alpha', key, alpha_sel[key])
                    W = ridge(Atr_, Ytr - ymu, alpha_sel[key]); sse = ((Ate_ @ W + ymu - Yte) ** 2).sum(1)
                    r = res.setdefault(f'{dec}|{ver}|{mname}', np.full(n, np.nan)); r[te] = sse
        res.setdefault('sst', np.full(n, np.nan))[te] = sst
        log('fold', k, 'done')
    meta['alpha'] = {f'{k[0]}|{k[1]}': v for k, v in alpha_sel.items()}
    np.savez(Path(a.out) / f'layer_{L}.npz', **res, folds=folds, team=team, pid=pids[idx], grp=Pp.group_tight.to_numpy(), meta=json.dumps(meta))
    log('layer done', L, meta['pca_var_share'])


# ------------------------------------------------------------------ combine
def holm_alpha(ps, alpha=0.05):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); a_i = np.empty(m); run = 0
    for r, i in enumerate(order): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run; a_i[i] = alpha / (m - r)
    return adj, a_i


def combine(a):
    check_lock(); out = Path(a.out); rows = []; boots = {}
    layers = [L for L in LAYERS_ALL if (out / f'layer_{L}.npz').exists()]
    for L in layers:
        Z = np.load(out / f'layer_{L}.npz', allow_pickle=True); sst = Z['sst']; grp = Z['grp']; team = Z['team']
        codes, uniq = pd.factorize(pd.Series(team))
        W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
        masks = dict(all=np.ones(len(sst), bool), target=grp == 'target', control=grp == 'control')
        def r2(sse, m): return 1 - sse[m].sum() / sst[m].sum(), 1 - (W[:, m] @ sse[m]) / (W[:, m] @ sst[m])
        for dec in ('bert', 'mpnet'):
            for ver in ('a', 'b'):
                g = lambda mn: Z[f'{dec}|{ver}|{mn}']
                for gname, mn in (('S', '-S'), ('M', '-M'), ('I', '-I'), ('P', '-P'), ('I_auth', '-I_auth'), ('I_attr', '-I_attr')):
                    est, bs = {}, {}
                    for mk, m in masks.items():
                        e1, b1 = r2(g('full'), m); e0, b0 = r2(g(mn), m); est[mk] = e1 - e0; bs[mk] = b1 - b0
                    est['T-C'] = est['target'] - est['control']; bs['T-C'] = bs['target'] - bs['control']
                    for mk in est:
                        b = bs[mk]; p = float(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean())))
                        rows.append(dict(layer=L, dec=dec, ver=ver, group=gname, set=mk, est=est[mk], lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5), p=p))
                        boots[(L, dec, ver, gname, mk)] = b
                ef, _ = r2(g('full'), masks['all']); rows.append(dict(layer=L, dec=dec, ver=ver, group='R2_full', set='all', est=ef, lo=np.nan, hi=np.nan, p=np.nan))
        meta = json.loads(str(Z['meta'])); rows.append(dict(layer=L, dec='', ver='', group='pca_var_share_mean', set='all', est=float(np.mean(meta['pca_var_share'])), lo=np.nan, hi=np.nan, p=np.nan))
    D = pd.DataFrame(rows); D.to_csv(out / 'partB_unique_r2.csv', index=False)
    fam = [L for L in FAMILY if L in layers]
    def holm_test(dec, ver, gname, mk):
        sub = [D[(D.layer == L) & (D.dec == dec) & (D.ver == ver) & (D.group == gname) & (D.set == mk)].iloc[0] for L in fam]
        ps = np.array([r.p for r in sub]); adj, a_i = holm_alpha(ps); res = []
        for r, L, pa, ai in zip(sub, fam, adj, a_i):
            b = boots[(L, dec, ver, gname, mk)]; res.append(dict(layer=L, est=r.est, holm_lo=np.percentile(b, 100 * ai / 2), holm_hi=np.percentile(b, 100 * (1 - ai / 2)), p_holm=pa))
        return pd.DataFrame(res)
    tests = {'D1 meaning beyond surface (bert)': holm_test('bert', 'a', 'M', 'all'), 'D1 (mpnet, reported)': holm_test('mpnet', 'a', 'M', 'all'),
             'D2 identity (bert)': holm_test('bert', 'a', 'I', 'all'), 'D2 identity (mpnet)': holm_test('mpnet', 'a', 'I', 'all'),
             'D3 identity T-C (bert)': holm_test('bert', 'a', 'I', 'T-C'), 'D3 identity T-C (mpnet)': holm_test('mpnet', 'a', 'I', 'T-C')}
    pos = {k: bool((v.holm_lo > 0).any()) for k, v in tests.items()}; neg = {k: bool((v.holm_hi < 0).any()) for k, v in tests.items()}
    unadj = lambda dec, g, mk: any(D[(D.dec == dec) & (D.ver == 'a') & (D.group == g) & (D.set == mk) & D.layer.isin(fam)].lo > 0)
    verdict = dict(
        D1='supported' if pos['D1 meaning beyond surface (bert)'] else 'not supported',
        D2='supported' if (pos['D2 identity (bert)'] and pos['D2 identity (mpnet)']) else ('borderline' if (pos['D2 identity (bert)'] or unadj('bert', 'I', 'all')) else 'not supported'),
        D3='supported' if (pos['D3 identity T-C (bert)'] and pos['D3 identity T-C (mpnet)']) else ('borderline' if (pos['D3 identity T-C (bert)'] or unadj('bert', 'I', 'T-C')) else 'not supported'),
        reversed=bool(neg['D3 identity T-C (bert)'] or neg['D3 identity T-C (mpnet)']))
    json.dump(dict(verdict=verdict, layers=layers, family=fam, lock_sha256=LOCK_SHA, test=bool(a.test)), open(out / 'partB_verdict.json', 'w'), indent=1)
    def tab(dec, ver, groups=('S', 'M', 'I', 'P', 'I_auth', 'I_attr')):
        t = ['| layer | R² full | ' + ' | '.join(f'u{g} (all)' for g in groups) + ' | uI target | uI control | uI T−C |', '|' + '---|' * (len(groups) + 5)]
        for L in layers:
            q = lambda g, mk: D[(D.layer == L) & (D.dec == dec) & (D.ver == ver) & (D.group == g) & (D.set == mk)].iloc[0]
            f = lambda r: f'{r.est:+.4f} [{r.lo:+.4f}, {r.hi:+.4f}]'
            t.append(f'| L{L} | {q("R2_full", "all").est:.3f} | ' + ' | '.join(f(q(g, "all")) for g in groups) + f' | {f(q("I", "target"))} | {f(q("I", "control"))} | {f(q("I", "T-C"))} |')
        return t
    rep = ['# Addendum 22 Part B — variance decomposition (LOCKED rule)', '',
           f'Lock sha256 {LOCK_SHA}; layers {layers}; Holm family {fam}; team bootstrap {NB}, seed {SEED}; test run: {bool(a.test)}.', '',
           f'**Verdicts:** D1 {verdict["D1"]} · D2 {verdict["D2"]} · D3 {verdict["D3"]} · reversed {verdict["reversed"]}', '']
    def md(df): return '\n'.join(['| ' + ' | '.join(df.columns) + ' |', '|' + '---|' * len(df.columns)] + ['| ' + ' | '.join(f'{x:+.4f}' if isinstance(x, float) else str(x) for x in r) + ' |' for r in df.itertuples(index=False)])
    for k, v in tests.items(): rep += [f'**{k}** (Holm over {fam})', '', md(v), '']
    for dec in ('bert', 'mpnet'):
        for ver, lab in (('a', 'residualised author/attribute/prior features (decision version)'), ('b', 'not residualised (descriptive)')):
            rep += [f'## {dec} decomposition, {lab}', '', *tab(dec, ver), '']
    rep += ['uG = unique R² of group G (full − without G), out of fold, variance-weighted over the top-256 PCs; I = I_attr (year, log citations, field) + I_auth (author-name embedding + Qwen surname-token one-hot); P = field-level surname-frequency prior.']
    (out / 'report.md').write_text('\n'.join(rep) + '\n'); log('combine done', verdict)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('stage', choices=['embed', 'layer', 'combine']); ap.add_argument('--layer')
    ap.add_argument('--test', action='store_true'); ap.add_argument('--out', default=str(J / '391_groups/summary_a22_partB'))
    a = ap.parse_args(); Path(a.out).mkdir(parents=True, exist_ok=True)
    {'embed': embed, 'layer': layer, 'combine': combine}[a.stage](a)
