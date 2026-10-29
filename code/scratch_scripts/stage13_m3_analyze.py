"""Stage 13 M3 analysis (CPU): does the state at the title / colon encode the PAPER, independent of the question asked?
Rules: config/prereg.json (M3) as replaced by addendum 2; group folds (addendum 1); team-cluster intervals (addendum 2).
Data: raw/task shards, resid [paper, task(authors/year/field), layer, pos(title_last/colon), 5120] (fp16).

I(l,pos): residuals centred per task and layer; for each task pair (a,b) and paper i,
          d_i = cos(u_i, v_i) - mean_{j != i} cos(u_i, v_j)   (u = task a, v = task b, unit vectors)
          I = mean_i d_i averaged over the 3 pairs. Judged ONLY as I(l) - I(L4) (interval excludes 0).
T(l,pos): PRIMARY. Ridge probe trained on task a states, tested on task b states of held-out papers (5 group folds,
          alpha picked on fold 0 of task a), divided by the probe trained and tested on task b. Targets: year (R^2),
          log10(1 + citations) (R^2), field (accuracy of a one-hot ridge). Averaged over the 6 ordered pairs.
          H2 (paper identity) predicts T >= 0.8 at L16-L40; H1 (task) predicts T < 0.5; also T(l) - T(L4).
Intervals: team bootstrap (2,000 draws) over per-paper quantities / held-out predictions (probes are not refitted).
Usage: python stage13_m3_analyze.py [--test]   (--test: 3 shards, layers 4 and 24, temp cache; whole pipeline)"""
import importlib.util, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TEST = '--test' in sys.argv; OUT = ROOT / ('summary_m3_test' if TEST else 'summary_m3'); NB = 2000
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
PAIRS = [(0, 1), (0, 2), (1, 2)]


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def cache():
    """one pass over the shards -> memmap [n, task, layer, pos, d] fp16 + paper ids"""
    fs = sorted((ROOT / 'raw/task').glob('shard_*.npz'))[:3 if TEST else None]
    z0 = np.load(fs[0]); tasks, layers, pos = list(z0['tasks']), [int(x) for x in z0['layers']], list(z0['positions'])
    ns = [len(np.load(f)['paper_id']) for f in fs]; n = sum(ns); shp = (n,) + z0['resid'].shape[1:]
    mm_path = OUT / 'resid_cache.f16'; pid_path = OUT / 'resid_cache_pids.npy'
    if not (mm_path.exists() and pid_path.exists() and mm_path.stat().st_size == np.prod(shp) * 2):
        mm = np.memmap(mm_path, np.float16, 'w+', shape=shp); pids = []; o = 0
        for f, k in zip(fs, ns):
            z = np.load(f); mm[o:o + k] = z['resid']; pids += list(z['paper_id']); o += k; log('cached', f.name)
        mm.flush(); np.save(pid_path, np.array(pids))
    return np.memmap(mm_path, np.float16, 'r', shape=shp), np.load(pid_path), tasks, layers, pos


def unit(X): return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)


def identity(Xs):
    """Xs: [n, 3, d] float32 for one (layer, pos) -> per-paper d_i averaged over the 3 task pairs"""
    C = [unit(Xs[:, t] - Xs[:, t].mean(0)) for t in range(3)]; n = len(Xs); out = np.zeros(n)
    for a, b in PAIRS:
        U, V = C[a], C[b]; same = (U * V).sum(1)
        diff_ab = (U @ V.sum(0) - same) / (n - 1); diff_ba = (V @ U.sum(0) - same) / (n - 1)
        out += same - 0.5 * (diff_ab + diff_ba)
    return out / len(PAIRS)


def fit(A, Y, a):
    G = A.T @ A; sc = np.trace(G) / G.shape[0]
    return np.linalg.solve(G + a * sc * np.eye(G.shape[0]), A.T @ Y)


def probes(Xs, Y, folds):
    """Xs [n, 3, d]; Y [n, q] -> held-out predictions P[a][b] [n, q] (train on task a, test on task b)"""
    n = len(Xs); P = {(a, b): np.zeros_like(Y) for a in range(3) for b in range(3)}; alpha = {}
    for k in np.unique(folds):
        tr, te = folds != k, folds == k; ym = Y[tr].mean(0)
        for a in range(3):
            mu, sd = Xs[tr, a].mean(0), Xs[tr, a].std(0) + 1e-6; A = (Xs[tr, a] - mu) / sd
            if a not in alpha:                                  # alpha picked on the first fold, within task a
                Xt = (Xs[te, a] - mu) / sd
                errs = [(((Xt @ fit(A, Y[tr] - ym, al) + ym) - Y[te]) ** 2 / Y.var(0)).mean() for al in ALPHAS]; alpha[a] = ALPHAS[int(np.argmin(errs))]
            Wt = fit(A, Y[tr] - ym, alpha[a])
            for b in range(3): P[a, b][te] = ((Xs[te, b] - mu) / sd) @ Wt + ym
    return P, alpha


def scores(y, p, W, kind):
    """point estimate and team-bootstrap draws of R^2 (kind 'r2') or accuracy ('acc')"""
    if kind == 'acc':
        hit = (p.argmax(1) == y.argmax(1)).astype(float); return hit.mean(), (W @ hit) / W.sum(1)
    e2 = (y - p) ** 2; sw = W.sum(1); ybar = (W @ y) / sw
    sst = W @ (y ** 2) - sw * ybar ** 2
    return 1 - e2.sum() / ((y - y.mean()) ** 2).sum(), 1 - (W @ e2) / sst


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    X, pids, tasks, layers, pos = cache(); n = len(pids); log('papers', n, 'tasks', tasks, 'layers', layers)
    use_layers = [4, 24] if TEST else layers
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id').loc[pids]
    folds, team = c13.group_folds(pids)
    fields = sorted(papers.field.unique()); F = (papers.field.to_numpy()[:, None] == np.array(fields)[None]).astype(float)
    Y = np.column_stack([papers.year.to_numpy(float), np.log10(1 + papers.citations.to_numpy(float)), F])
    codes, uniq = pd.factorize(pd.Series(team)); W = np.random.default_rng(31).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    Irows, Trows, Ipp, Tb = [], [], {}, {}
    for li, l in enumerate(layers):
        if l not in use_layers: continue
        for pi, p in enumerate(pos):
            Xs = np.asarray(X[:, :, li, pi, :], dtype=np.float32); t0 = time.time()
            d = identity(Xs); Ipp[l, p] = d; b = (W @ d) / W.sum(1)
            Irows.append(dict(layer=l, pos=p, I=d.mean(), lo=ci(b)[0], hi=ci(b)[1]))
            P, alpha = probes(Xs, Y, folds)
            for tname, cols, kind in (('year', [0], 'r2'), ('log_citations', [1], 'r2'), ('field', list(range(2, Y.shape[1])), 'acc')):
                y = Y[:, cols] if kind == 'acc' else Y[:, cols[0]]
                within = {bb: scores(y, P[bb, bb][:, cols] if kind == 'acc' else P[bb, bb][:, cols[0]], W, kind) for bb in range(3)}
                ratios_e, ratios_b = [], []
                for a in range(3):
                    for bb in range(3):
                        if a == bb: continue
                        cr = scores(y, P[a, bb][:, cols] if kind == 'acc' else P[a, bb][:, cols[0]], W, kind)
                        ratios_e.append(cr[0] / within[bb][0]); ratios_b.append(cr[1] / within[bb][1])
                        Trows.append(dict(layer=l, pos=p, target=tname, train=tasks[a], test=tasks[bb], cross=cr[0], within=within[bb][0], ratio=cr[0] / within[bb][0]))
                tb = np.mean(ratios_b, 0); Tb[l, p, tname] = tb
                Trows.append(dict(layer=l, pos=p, target=tname, train='avg', test='avg', cross=np.nan, within=np.mean([w[0] for w in within.values()]),
                                  ratio=float(np.mean(ratios_e)), lo=ci(tb)[0], hi=ci(tb)[1], alpha=str(alpha)))
            log(f'L{l} {p}: I {d.mean():+.4f}; T ' + ', '.join(f'{r["target"]} {r["ratio"]:.2f}' for r in Trows[-3:] if r['train'] == 'avg') + f' ({time.time() - t0:.0f}s)')
    I = pd.DataFrame(Irows); T = pd.DataFrame(Trows)
    for p in pos:                                                # relative to the text-only level L4
        for l in use_layers:
            dd = Ipp[l, p] - Ipp[4, p]; b = (W @ dd) / W.sum(1); m = (I.layer == l) & (I.pos == p)
            I.loc[m, ['I_minus_L4', 'd_lo', 'd_hi']] = [dd.mean(), *ci(b)]
            for tname in ('year', 'log_citations', 'field'):
                m2 = (T.layer == l) & (T.pos == p) & (T.target == tname) & (T.train == 'avg'); bb = Tb[l, p, tname] - Tb[4, p, tname]
                T.loc[m2, ['T_minus_L4', 'td_lo', 'td_hi']] = [T[m2].ratio.iloc[0] - T[(T.layer == 4) & (T.pos == p) & (T.target == tname) & (T.train == 'avg')].ratio.iloc[0], *ci(bb)]
    I.to_csv(OUT / 'm3_identity.csv', index=False); T.to_csv(OUT / 'm3_transfer.csv', index=False)
    A = T[T.train == 'avg']
    L = ['# Stage 13 M3: is the title / colon state about the paper or about the question?', '',
         f'{n} papers, 3 prompts per paper ({", ".join(tasks)}), 5 group folds; 95% team-cluster bootstrap.' + (' **TEST RUN (3 shards, 2 layers)**' if TEST else ''),
         'Rule (addendum 2): PRIMARY = transfer ratio T at L16-L40, also relative to T(L4); the identity index counts only as I(l) - I(L4).', '',
         '## Transfer ratio T (train on one prompt, test on another, / within-prompt); average of 6 ordered pairs', '']
    for p in pos:
        L += [f'### {p}', '', '| layer | year | log citations | field | year: T - T(L4) | field: T - T(L4) | within-prompt year R², field acc |', '|---|---|---|---|---|---|---|']
        for l in use_layers:
            f = lambda t: A[(A.layer == l) & (A.pos == p) & (A.target == t)].iloc[0]
            L.append(f'| L{l} | ' + ' | '.join(fm(f(t).ratio, f(t).lo, f(t).hi) for t in ('year', 'log_citations', 'field'))
                     + f' | {fm(f("year").T_minus_L4, f("year").td_lo, f("year").td_hi)} | {fm(f("field").T_minus_L4, f("field").td_lo, f("field").td_hi)} | {f("year").within:.3f}, {f("field").within:.3f} |')
        L.append('')
    L += ['## Identity index (judged only relative to L4)', '', '| layer | pos | I | I - I(L4) |', '|---|---|---|---|']
    for r in I.to_dict('records'): L.append(f'| L{r["layer"]} | {r["pos"]} | {fm(r["I"], r["lo"], r["hi"])} | {fm(r["I_minus_L4"], r["d_lo"], r["d_hi"])} |')
    L += ['', '## Pre-registered reading (L16-L40)', '']
    for p in pos:
        for t in ('year', 'log_citations', 'field'):
            s = A[(A.pos == p) & (A.target == t) & (A.layer.between(16, 40))]
            if s.empty: continue
            h2 = (s.lo >= 0.8).all(); h1 = (s.hi < 0.5).all()
            L.append(f'- {p}, {t}: T at L16-L40 = ' + ', '.join(f'L{r.layer} {r.ratio:.2f}' for r in s.itertuples())
                     + f' -> {"H2 (paper identity, T >= 0.8 throughout)" if h2 else ("H1 (task-specific, T < 0.5 throughout)" if h1 else "neither threshold met throughout (mixed)")}')
    rep = ROOT / ('reports/m3_report_test.md' if TEST else 'reports/m3_report.md'); rep.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nM3 ANALYZED')


if __name__ == '__main__':
    main()
