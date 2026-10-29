"""Stage 13 X7 analysis (CPU), rules from config/prereg_addendum3.json.
The Stage 11 knockout (block attention to the title from layer l on) applied to the false_0 run, scored on the true
paper's authors. With per-paper means of nlr = log10(1/rank) (tokens averaged within paper first, as Stage 11):
  T(l) = mean(kT64 - kT_l) / mean(true - false)      Stage 11 E2 loss on the true run (must reproduce E2_knockout.csv)
  F(l) = mean(kF64 - kF_l) / mean(true - false)      the same knockout on the false_0 run (off-distribution damage)
  S(l) = T(l) - F(l)                                 paper-specific loss
k64 = nothing blocked. Built-in checks (WARN only): kF64 == Stage 11 rank_false row by row; T reproduces Stage 11 E2.
95% team-cluster bootstrap (addendum 2), one team draw shared by T, F and S.
Outputs: summary_x7/x7_knockout.csv, x7_verdict.json, reports/x7_report.md"""
import importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; OUT = ROOT / 'summary_x7'; OUT.mkdir(parents=True, exist_ok=True); NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d, keys):
    fs = sorted(Path(d).glob('shard_*.npz')); zs = [np.load(f) for f in fs]
    return {k: np.concatenate([z[k] for z in zs]) for k in keys}, [int(x) for x in zs[0]['layers']], len(fs)


def main():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    grp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].set_index('paper_id').group
    d, _, _ = load_dir(R11 / 'raw/patch', ['row_id', 'rank_true', 'rank_false'])
    kT, kl, nT = load_dir(R11 / 'raw/knockout', ['row_id', 'rank_ko'])
    kF, klF, nF = load_dir(ROOT / 'raw/ko_false/false_0', ['row_id', 'rank_ko'])
    warn = []
    if kl != klF: warn.append(f'knockout layers differ: {kl} vs {klF}')
    base = pd.DataFrame({'row_id': d['row_id'], 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false']), 'rank_false': d['rank_false']})
    t = pd.DataFrame({'row_id': kT['row_id'], **{f'T{l}': nlr(kT['rank_ko'][:, i]) for i, l in enumerate(kl)}})
    f = pd.DataFrame({'row_id': kF['row_id'], 'kF64_rank': kF['rank_ko'][:, -1], **{f'F{l}': nlr(kF['rank_ko'][:, i]) for i, l in enumerate(klF)}})
    m = base.merge(t, on='row_id').merge(f, on='row_id')
    if len(m) != len(base): warn.append(f'rows: patch {len(base)}, knockout {len(t)}, ko_false {len(f)}, matched {len(m)}')
    eq = float((m.kF64_rank == m.rank_false).mean())
    if eq < 1: warn.append(f'kF64 equals the Stage 11 false run on {eq:.4f} of rows (expected 1; batching may round differently)')
    m['paper_id'] = toks.loc[m.row_id].paper_id.to_numpy()
    pp = m.drop(columns=['row_id', 'rank_false', 'kF64_rank']).groupby('paper_id').mean()
    allp = list(pp.index); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in allp]))
    W = pd.DataFrame(np.random.default_rng(17).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes].T, index=allp)
    e11 = pd.read_csv(R11 / 'summary/E2_knockout.csv'); rows = []
    for g in ('target', 'control', 'all'):
        s = pp if g == 'all' else pp[grp.reindex(pp.index).to_numpy() == g]; w = W.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy(); dw = den @ w
        for l in kl:
            if l == 64: continue
            nt = (s['T64'] - s[f'T{l}']).to_numpy(); nf = (s['F64'] - s[f'F{l}']).to_numpy()
            bt, bf = (nt @ w) / dw, (nf @ w) / dw
            r = dict(group=g, start_layer=l, n_papers=len(s), T=nt.mean() / den.mean(), F=nf.mean() / den.mean())
            r['S'] = r['T'] - r['F']
            for k, b in (('T', bt), ('F', bf), ('S', bt - bf)): r[k + '_lo'], r[k + '_hi'] = np.percentile(b, [2.5, 97.5])
            o = e11[(e11.group == g) & (e11.start_layer == l)]
            r['T_stage11'] = float(o.loss_fraction.iloc[0]) if len(o) else np.nan
            rows.append(r)
    D = pd.DataFrame(rows); D.to_csv(OUT / 'x7_knockout.csv', index=False)
    try:                                          # self-check only: never fatal (rule 3); D.T would be the transpose
        dT = float(np.nanmax(np.abs(D['T'].to_numpy(float) - D['T_stage11'].to_numpy(float))))
        if not dT < 1e-6: warn.append(f'T differs from Stage 11 E2 by up to {dT:.2e}')
    except Exception as ex:
        dT = float('nan'); warn.append(f'T-vs-Stage-11 check failed: {ex!r}')
    fm = lambda r, k: f'{r[k]:+.3f} [{r[k + "_lo"]:+.3f}, {r[k + "_hi"]:+.3f}]'
    L = ['# Stage 13 X7: Stage 11 knockout applied to the false_0 run', '',
         f'Rule: config/prereg_addendum3.json (X7). Shards: Stage 11 knockout {nT}, ko_false {nF}; {len(pp)} papers.',
         'T = loss on the true run (Stage 11 E2), F = the same knockout on the false run, S = T - F (paper-specific loss); all divided by mean(true - false). 95% team-cluster bootstrap.', '',
         f'Self-checks: T vs Stage 11 E2 max |diff| {dT:.1e}; nothing-blocked false element == Stage 11 false run on {eq:.4f} of rows.', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    for g in ('target', 'control', 'all'):
        L += [f'## {g}', '', '| block from | T (true run) | F (false run) | S = T - F |', '|---|---|---|---|']
        for r in D[D.group == g].to_dict('records'): L.append(f'| L{r["start_layer"]} | {fm(r, "T")} | {fm(r, "F")} | {fm(r, "S")} |')
        L.append('')
    L += ['## Pre-registered check (addendum 3)', '', 'Claim holds if S(L52) <= 0.05 and S(L0) >= 0.5. Also reported: the share of the L0 loss that remains after subtracting the false-run loss, S(L0) / T(L0).', '']
    verdict = {}
    for g in ('target', 'control', 'all'):
        x = D[D.group == g].set_index('start_layer'); s52, s0, t0 = x.loc[52, 'S'], x.loc[0, 'S'], x.loc[0, 'T']
        verdict[g] = bool(s52 <= 0.05 and s0 >= 0.5)
        L.append(f'- {g}: S(L52) {s52:+.3f}, S(L0) {s0:+.3f}, T(L0) {t0:.3f}, remaining share {s0 / t0:.2f} -> **{"HOLDS" if verdict[g] else "DOES NOT HOLD"}**')
    (ROOT / 'reports/x7_report.md').write_text('\n'.join(L) + '\n'); json.dump(dict(verdict=verdict, warn=warn), open(OUT / 'x7_verdict.json', 'w'), indent=1)
    print('\n'.join(L)); print('\nX7 ANALYZED')


if __name__ == '__main__':
    main()
