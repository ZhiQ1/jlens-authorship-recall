"""Stage 13 V42 (handbook G4), M3 part: paper-bootstrap intervals beside the team-cluster ones (addendum 2 asks for both).
Recomputes the M3 quantities with the UNCHANGED functions of stage13_m3_analyze.py (identity, probes, scores; same group
folds, same alpha rule, same team draws seed 31) and adds a paper bootstrap (seed 32, 2,000 draws, each paper its own
cluster). Probes are not refitted per draw (as in M3). Team values are checked against summary_m3/m3_identity.csv and
m3_transfer.csv (WARN only).
Output (new): summary_v42/m3_paper_vs_team.csv.  --test: 3 layers (4, 24, 40), title_last only, 1,500 papers -> summary_v42_test/"""
import importlib.util, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TEST = '--test' in sys.argv; OUT = ROOT / ('summary_v42_test' if TEST else 'summary_v42'); NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def ci(b): return np.percentile(b, [2.5, 97.5])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    argv = sys.argv; sys.argv = [argv[0]]                                  # import M3 functions with TEST off
    m3 = load(H / '13_stage13/stage13_m3_analyze.py', 'm3a'); sys.argv = argv
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    pids = np.load(ROOT / 'summary_m3/resid_cache_pids.npy'); N = len(pids)
    X = np.memmap(ROOT / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=(N, 3, 15, 2, 5120))
    layers = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]; pos = ['title_last', 'colon']
    sel = np.arange(N) if not TEST else np.sort(np.random.default_rng(0).choice(N, 1500, replace=False))
    use_l = [4, 24, 40] if TEST else layers; use_p = ['title_last'] if TEST else pos
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id').loc[pids]
    folds, team = c13.group_folds(pids)
    fields = sorted(papers.field.unique()); F = (papers.field.to_numpy()[:, None] == np.array(fields)[None]).astype(float)
    Y = np.column_stack([papers.year.to_numpy(float), np.log10(1 + papers.citations.to_numpy(float)), F])
    folds, team, Y = folds[sel], team[sel], Y[sel]
    codes, uniq = pd.factorize(pd.Series(team))
    Wt = np.random.default_rng(31).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]   # = M3
    n = len(sel); Wp = np.random.default_rng(32).multinomial(n, np.full(n, 1 / n), size=NB).astype(float)
    rows, Ipp, Tb = [], {}, {}
    for li, l in enumerate(layers):
        if l not in use_l: continue
        for pi, p in enumerate(pos):
            if p not in use_p: continue
            t0 = time.time(); Xs = np.asarray(X[:, :, li, pi, :], dtype=np.float32)[sel]
            d = m3.identity(Xs); Ipp[l, p] = d
            r = dict(measure='I', layer=l, pos=p, est=d.mean())
            for tag, W in (('team', Wt), ('paper', Wp)): r[f'lo_{tag}'], r[f'hi_{tag}'] = ci((W @ d) / W.sum(1))
            rows.append(r)
            P, alpha = m3.probes(Xs, Y, folds)
            for tname, cols, kind in (('year', [0], 'r2'), ('log_citations', [1], 'r2'), ('field', list(range(2, Y.shape[1])), 'acc')):
                y = Y[:, cols] if kind == 'acc' else Y[:, cols[0]]
                pr = lambda a, b: P[a, b][:, cols] if kind == 'acc' else P[a, b][:, cols[0]]
                for tag, W in (('team', Wt), ('paper', Wp)):
                    within = {b: m3.scores(y, pr(b, b), W, kind) for b in range(3)}
                    re_, rb = [], []
                    for a in range(3):
                        for b in range(3):
                            if a == b: continue
                            cr = m3.scores(y, pr(a, b), W, kind); re_.append(cr[0] / within[b][0]); rb.append(cr[1] / within[b][1])
                    Tb[tag, l, p, tname] = np.mean(rb, 0); est = float(np.mean(re_))
                r = dict(measure=f'T_{tname}', layer=l, pos=p, est=est)
                for tag in ('team', 'paper'): r[f'lo_{tag}'], r[f'hi_{tag}'] = ci(Tb[tag, l, p, tname])
                rows.append(r)
            log(f'L{l} {p}: I {d.mean():+.4f} ({time.time() - t0:.0f}s)')
    D = pd.DataFrame(rows); extra = []
    for p in use_p:
        for l in use_l:
            dd = Ipp[l, p] - Ipp[4, p]; r = dict(measure='I_minus_L4', layer=l, pos=p, est=dd.mean())
            for tag, W in (('team', Wt), ('paper', Wp)): r[f'lo_{tag}'], r[f'hi_{tag}'] = ci((W @ dd) / W.sum(1))
            extra.append(r)
            for tname in ('year', 'log_citations', 'field'):
                e = D[(D.measure == f'T_{tname}') & (D.layer == l) & (D.pos == p)].est.iloc[0] - D[(D.measure == f'T_{tname}') & (D.layer == 4) & (D.pos == p)].est.iloc[0]
                r = dict(measure=f'T_{tname}_minus_L4', layer=l, pos=p, est=e)
                for tag in ('team', 'paper'): r[f'lo_{tag}'], r[f'hi_{tag}'] = ci(Tb[tag, l, p, tname] - Tb[tag, 4, p, tname])
                extra.append(r)
    D = pd.concat([D, pd.DataFrame(extra)], ignore_index=True)
    warn = []
    if not TEST:                                                       # parity with the M3 outputs (WARN only)
        try:
            I0 = pd.read_csv(ROOT / 'summary_m3/m3_identity.csv'); T0 = pd.read_csv(ROOT / 'summary_m3/m3_transfer.csv'); T0 = T0[T0.train == 'avg']
            for r in D.itertuples():
                if r.measure == 'I': o = I0[(I0.layer == r.layer) & (I0.pos == r.pos)]; ref = (o.I.iloc[0], o.lo.iloc[0], o.hi.iloc[0])
                elif r.measure == 'I_minus_L4': o = I0[(I0.layer == r.layer) & (I0.pos == r.pos)]; ref = (o.I_minus_L4.iloc[0], o.d_lo.iloc[0], o.d_hi.iloc[0])
                elif r.measure.startswith('T_') and not r.measure.endswith('L4'):
                    o = T0[(T0.layer == r.layer) & (T0.pos == r.pos) & (T0.target == r.measure[2:])]; ref = (o.ratio.iloc[0], o.lo.iloc[0], o.hi.iloc[0])
                else: continue
                dev = max(abs(r.est - ref[0]), abs(r.lo_team - ref[1]), abs(r.hi_team - ref[2]))
                if not dev <= 1e-3 * max(1, abs(ref[0])): warn.append(f'{r.measure} L{r.layer} {r.pos}: team value differs from M3 output by {dev:.2e}')
        except Exception as ex:
            warn.append(f'parity check failed: {ex!r}')
    D['warn'] = '; '.join(warn) if warn else ''
    p = OUT / 'm3_paper_vs_team.csv'
    if p.exists(): p = p.with_name(f'm3_paper_vs_team.{time.strftime("%Y%m%d_%H%M%S")}.csv')
    D.to_csv(p, index=False); print(D.to_string()); print('WARN' if warn else 'parity OK', *warn[:20], sep='\n'); print('\nV42 M3 DONE', p)


if __name__ == '__main__':
    main()
