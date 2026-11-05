"""Addendum 7 'summary table' (rows A, B, C, D, U0, U1, R2s), from primary/stage10/s1113 outputs. Writes OUT/summary_table.{csv,md}."""
import os, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import groups_core as gc

OUT = gc.OUT
NA_GPU = 'not available (not in the Stage 11-13 GPU sample)'
NA_R2 = 'not available (GPU re-run pending, addendum 8)'


def cell(r, d=3, auth=True):
    if r is None or (isinstance(r, pd.DataFrame) and r.empty): return None
    r = r.iloc[0] if isinstance(r, pd.DataFrame) else r
    if not np.isfinite(r.estimate): return None
    n = f"n = {int(r.n_papers)}" + (f" ({int(r.n_authors)} authors)" if auth and 'n_authors' in r and pd.notna(r.n_authors) else '')
    if r.n_papers < 30: return f'{r.estimate:+.{d}f}; {n}; n < 30, descriptive'
    return f'{r.estimate:+.{d}f} [{r.lo:+.{d}f}, {r.hi:+.{d}f}]; {n}'


def main():
    gc.check_plan()
    for f in ('summary_table.csv', 'summary_table.md'):
        if (OUT / f).exists() and os.environ.get('GROUPS_OVERWRITE') != '1': raise SystemExit(f'{OUT / f} exists')
    GM = pd.read_csv(OUT / 'stage10_group_means.csv'); S = pd.read_csv(OUT / 's1113_groups.csv')
    g10 = lambda who, g: GM[(GM.who == who) & (GM.role == 'all') & (GM.measure == 'spec') & (GM.readout == 'final') & (GM.layer == 63) & (GM.group == g)]
    s = lambda meas, item, who, g: S[(S.measure == meas) & (S.item == item) & (S.who == who) & (S.group == g)]
    cols = ['output signal, unwritten authors (L63)', 'output signal, written authors (reference)', 'E1 recovery L48 (unwritten)', 'E1 recovery L52 (unwritten)',
            'E2 knockout loss L52 (unwritten)', 'E4b probe spec L40 (per paper, all authors)', 'M2 recognised AUROC vs B, colon L52 (descriptive)',
            'X3 behaviour recovery, test split (first author not written)']
    rows = []
    for g in gc.GROUPS:
        r = {'group': g}
        r[cols[0]] = cell(g10('unwritten', g)) or 'not available'
        r[cols[1]] = cell(g10('written', g)) or ('none written (R0)' if g in ('A', 'B', 'U0') else 'not available')
        inGPU = g in ('A', 'B', 'C', 'D')
        na = NA_GPU if g in ('U1',) else (NA_R2 if g in ('R2s', 'U0') else NA_GPU)
        r[cols[2]] = (cell(s('E1 recovery', 'L48', 'unwritten', g)) or 'not available') if inGPU else na
        r[cols[3]] = (cell(s('E1 recovery', 'L52', 'unwritten', g)) or 'not available') if inGPU else na
        r[cols[4]] = (cell(s('E2 loss', 'L52', 'unwritten', g)) or 'not available') if inGPU else na
        e4 = s('E4b probe spec (per paper, all authors)', 'L40', 'all authors (incl. written in C/D)', g)
        r[cols[5]] = ((cell(e4, auth=False) or 'not available') + ('; includes written authors' if g in ('C', 'D') and len(e4) else '')) if inGPU else NA_GPU
        if g == 'B': r[cols[6]] = 'reference class (AUROC vs itself = 0.5)'
        else:
            m2 = s('M2 recognised-probe AUROC vs B', 'colon L52', 'per paper', g)
            r[cols[6]] = (f'{m2.estimate.iloc[0]:.3f} [{m2.lo.iloc[0]:.3f}, {m2.hi.iloc[0]:.3f}]; n = {int(m2.n_papers.iloc[0])}; descriptive'
                          if len(m2) and m2.n_papers.iloc[0] >= 30 else (f'{m2.estimate.iloc[0]:.3f}; n = {int(m2.n_papers.iloc[0])}; n < 30, descriptive' if len(m2) else
                                                                     ('not available' if inGPU else NA_GPU)))
        r[cols[7]] = (cell(s('X3 behaviour recovery', 'test split', 'first author (not written)', g), auth=False) or 'not available') if inGPU else NA_GPU
        rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(OUT / 'summary_table.csv', index=False)
    md = ['| group | ' + ' | '.join(cols) + ' |', '|---' * (len(cols) + 1) + '|']
    for r in rows: md.append(f'| {r["group"]} | ' + ' | '.join(str(r[c]) for c in cols) + ' |')
    (OUT / 'summary_table.md').write_text('\n'.join(md) + '\n'); print('\n'.join(md))


if __name__ == '__main__':
    main()
