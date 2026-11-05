"""Stage 13 V56 (handbook G4): the pre-registered X5 curve "paper identity retrievable across tasks"
(prereg.json X5: "M3, top-1 retrieval among the test papers"), computed from the EXISTING M3 residual cache. CPU only.

Data: summary_m3/resid_cache.f16 (memmap [9108, task(authors, year, field), layer(15), pos(title_last, colon), 5120] fp16),
      ids summary_m3/resid_cache_pids.npy (same order; see stage13_m3_analyze.cache()).
Retrieval at (layer, pos), for a set P of papers (the gallery):
  states centred per task over P (mean over P of that task), unit-normalised;
  for each ordered task pair (a, b) and each query paper i in P: S_i = cos(u_i^a, v_j^b) over all j in P;
  top-1 hit = argmax_j S_i == i (ties: first index; with fp32 cosines ties are not expected); also rank of i (1 = best).
  Per paper: hit averaged over the 6 ordered pairs (paper as query). Retrieval = mean over P. Chance = 1/|P|.
Sets: 'test' / 'tune' = config/pairs.parquet split (the prereg wording "among the test papers"; teams = pairs.parquet team);
      'all' = all 9,108 cohort papers (teams = stage13_cpu.group_folds team ids).
Addendum 2 logic: judged relative to the text level, D(l) = retrieval(l) - retrieval(L4), per-paper paired differences.
Intervals: 95% bootstrap, 2,000 draws, over author teams (primary, addendum 2) AND over papers (shown beside it).
  The gallery is NOT re-formed per draw (per-paper hits are resampled), as for the M3 identity index.
Earliest layer (same logic as X3/X4): first layer > L4 with D's team interval above 0, chosen on 'tune', confirmed on
'test' at that layer; for 'all' the first layer with D's team interval above 0.
Outputs (new files, never overwritten): summary_x5/x5_retrieval.csv, summary_x5/x5_retrieval_earliest.csv,
  reports/x5_retrieval.md.  --test: 2 layers, 600 papers, output to summary_x5_test/ (whole pipeline).
"""
import importlib.util, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TEST = '--test' in sys.argv
OUT = ROOT / ('summary_x5_test' if TEST else 'summary_x5'); REP = OUT if TEST else ROOT / 'reports'
NB = 2000; PAIRS = [(a, b) for a in range(3) for b in range(3) if a != b]


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi, d=3): return f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'


def safe(p):
    p = Path(p)
    if not p.exists(): return p
    q = p.with_name(f'{p.stem}.{time.strftime("%Y%m%d_%H%M%S")}{p.suffix}'); print('WARN', p, 'exists; writing', q); return q


def weights(clusters, seed):
    codes, uniq = pd.factorize(pd.Series(clusters))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float32)[:, codes]


def retrieve(Xs):
    """Xs [n, 3, d] float32 -> per-paper mean top-1 hit and mean reciprocal rank over the 6 ordered task pairs"""
    n = len(Xs); C = []
    for t in range(3):
        Z = Xs[:, t] - Xs[:, t].mean(0); C.append(Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9))
    hit = np.zeros(n); rr = np.zeros(n); ch = 2048
    for a, b in PAIRS:
        for s in range(0, n, ch):
            S = C[a][s:s + ch] @ C[b].T; idx = np.arange(s, min(s + ch, n)); own = S[np.arange(len(idx)), idx]
            hit[idx] += (S.argmax(1) == idx); rr[idx] += 1.0 / ((S > own[:, None]).sum(1) + 1)
    return hit / len(PAIRS), rr / len(PAIRS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    pids = np.load(ROOT / 'summary_m3/resid_cache_pids.npy'); N = len(pids)
    X = np.memmap(ROOT / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=(N, 3, 15, 2, 5120))
    layers = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]; pos = ['title_last', 'colon']
    z0 = np.load(ROOT / 'raw/task/shard_000.npz')
    assert [int(x) for x in z0['layers']] == layers and list(z0['positions']) == pos and list(z0['tasks']) == ['authors', 'year', 'field']
    _, team_all = c13.group_folds(pids)
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet'); ix = {p: i for i, p in enumerate(pids)}
    sets = {'all': (np.arange(N), team_all)}
    for sp in ('tune', 'test'):
        q = pairs[pairs.split == sp]; sets[sp] = (np.array([ix[p] for p in q.paper_id]), q.team.to_numpy())
    use_layers = [4, 24] if TEST else layers
    if TEST:
        r = np.random.default_rng(0); sel = np.sort(r.choice(N, 600, replace=False)); sets['all'] = (sel, team_all[sel])
    Wt = {k: weights(v[1], 561) for k, v in sets.items()}; Wp = {k: weights(np.arange(len(v[0])), 562) for k, v in sets.items()}
    per = {}; rows = []
    for li, l in enumerate(layers):
        if l not in use_layers: continue
        for pi, p in enumerate(pos):
            t0 = time.time(); Xall = np.asarray(X[:, :, li, pi, :], dtype=np.float32)
            for k, (idx, _) in sets.items():
                h, rr = retrieve(Xall[idx]); per[k, l, p] = (h, rr)
                r = dict(set=k, layer=l, pos=p, n=len(idx), chance=1 / len(idx), top1=h.mean(), mrr=rr.mean())
                for tag, W in (('team', Wt[k]), ('paper', Wp[k])):
                    b = (W @ h) / W.sum(1); r[f'top1_lo_{tag}'], r[f'top1_hi_{tag}'] = ci(b)
                rows.append(r)
            log(f'L{l} {p}: ' + ', '.join(f'{k} {per[k, l, p][0].mean():.4f}' for k in sets) + f' ({time.time() - t0:.0f}s)')
            del Xall
    D = pd.DataFrame(rows)
    for k in sets:                                             # relative to the text level L4 (addendum 2 logic)
        for p in pos:
            for l in use_layers:
                m = (D.set == k) & (D.layer == l) & (D.pos == p)
                d = per[k, l, p][0] - per[k, 4, p][0]; dm = per[k, l, p][1] - per[k, 4, p][1]
                D.loc[m, 'top1_minus_L4'] = d.mean(); D.loc[m, 'mrr_minus_L4'] = dm.mean()
                for tag, W in (('team', Wt[k]), ('paper', Wp[k])):
                    b = (W @ d) / W.sum(1); lo, hi = ci(b); D.loc[m, f'dL4_lo_{tag}'] = lo; D.loc[m, f'dL4_hi_{tag}'] = hi
    p_csv = safe(OUT / 'x5_retrieval.csv'); D.to_csv(p_csv, index=False)
    E = []
    for p in pos:
        f = lambda k, l: D[(D.set == k) & (D.layer == l) & (D.pos == p)].iloc[0]
        tu = [l for l in use_layers if l > 4 and f('tune', l).dL4_lo_team > 0]
        l0 = tu[0] if tu else None
        conf = bool(l0 is not None and f('test', l0).dL4_lo_team > 0)
        al = [l for l in use_layers if l > 4 and f('all', l).dL4_lo_team > 0]
        neg = [l for l in use_layers if l > 4 and f('all', l).dL4_hi_team < 0]
        E.append(dict(pos=p, earliest_tune=l0, confirmed_on_test=conf,
                      test_dL4=f('test', l0).top1_minus_L4 if l0 else np.nan, test_lo=f('test', l0).dL4_lo_team if l0 else np.nan,
                      test_hi=f('test', l0).dL4_hi_team if l0 else np.nan, earliest_all=al[0] if al else None,
                      layers_all_above_L4=','.join(map(str, al)), layers_all_below_L4=','.join(map(str, neg))))
    E = pd.DataFrame(E); p_e = safe(OUT / 'x5_retrieval_earliest.csv'); E.to_csv(p_e, index=False)
    Lm = ['# Stage 13 V56: X5 pre-registered curve, cross-task top-1 retrieval of the paper (M3 cache)', '',
          f'Script `~/jlens_work/13_stage13/stage13_v56_retrieval.py`, run {time.strftime("%Y-%m-%d %H:%M")}' + (' **TEST RUN**' if TEST else '') + '. CPU only, existing M3 residual cache (no model runs).',
          'Definition (prereg.json X5: "paper identity retrievable across tasks (M3, top-1 retrieval among the test papers)"): query = paper i under prompt a (authors / year / field), gallery = all papers of the set under prompt b; cosine after centring each prompt over the set; hit if paper i is the nearest; average of the 6 ordered prompt pairs. Chance = 1/n.',
          'Judged as in addendum 2 (M3 identity index): only retrieval(l) - retrieval(L4) counts, because identical title tokens already make the title states similar across prompts. Earliest layer: first layer with the team interval of retrieval(l) - retrieval(L4) above 0 on tune, confirmed on test (prereg general rule); for all 9,108 papers, the first such layer.',
          'Intervals: 95% bootstrap, 2,000 draws, over author teams (primary) and over papers; the gallery is fixed and per-paper hits are resampled. MRR = mean reciprocal rank (reference).', '',
          f'CSV: `{p_csv}`; earliest: `{p_e}`.', '']
    for p in pos:
        Lm += [f'## {p}', '', '| layer | set | n | top-1 (team CI) | top-1 (paper CI) | top-1 - L4 (team CI) | top-1 - L4 (paper CI) | MRR |', '|---|---|---|---|---|---|---|---|']
        for l in use_layers:
            for k in ('test', 'tune', 'all'):
                r = D[(D.set == k) & (D.layer == l) & (D.pos == p)].iloc[0]
                Lm.append(f'| L{l} | {k} | {r.n} | {fm(r.top1, r.top1_lo_team, r.top1_hi_team)} | {fm(r.top1, r.top1_lo_paper, r.top1_hi_paper)} | '
                          f'{fm(r.top1_minus_L4, r.dL4_lo_team, r.dL4_hi_team)} | {fm(r.top1_minus_L4, r.dL4_lo_paper, r.dL4_hi_paper)} | {r.mrr:.3f} |')
        Lm.append('')
    Lm += ['## Earliest layer above the L4 text level', '', '| pos | earliest (tune) | test at that layer: top-1 - L4 | confirmed | all papers: earliest | all papers: layers above L4 | all papers: layers below L4 |', '|---|---|---|---|---|---|---|']
    for r in E.itertuples():
        Lm.append(f'| {r.pos} | ' + (f'L{int(r.earliest_tune)} | {fm(r.test_dL4, r.test_lo, r.test_hi)} | {"yes" if r.confirmed_on_test else "no"}' if pd.notna(r.earliest_tune) else 'none | - | -')
                  + f' | {("L" + str(int(r.earliest_all))) if pd.notna(r.earliest_all) else "none"} | {r.layers_all_above_L4 or "-"} | {r.layers_all_below_L4 or "-"} |')
    p_md = safe(REP / 'x5_retrieval.md'); p_md.write_text('\n'.join(Lm) + '\n'); print('\n'.join(Lm)); print('\nV56 RETRIEVAL DONE')


if __name__ == '__main__':
    main()
