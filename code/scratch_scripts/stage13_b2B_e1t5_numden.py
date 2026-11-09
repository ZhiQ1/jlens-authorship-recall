"""Addendum 12 item 2-8 follow-up (user request 2026-11-09, exploratory): target - control of the E1t recovery split into
numerator mean(patched - false) and denominator mean(true - false), every layer, five-title mean and false_0.

New file; reuses stage13_b2B_analyze.py (loaded by path, unchanged) for data loading and the per-paper frame
(e1t_frame), the same paper set (papers present in all five titles), the same team-cluster draws (groups_core.Engine,
seed 391, W restricted per group) and the same paper bootstrap (default_rng(3611) per group). Team-bootstrap means are
weighted means (W @ x) / W.sum(1), the same weighting the recovery ratio uses in its numerator and denominator.
Self-check (WARN only): the recovery target - control recomputed here must equal summary_b2B/e1t5_tc.csv.
Outputs: summary_b2B/e1t5_numden_tc.csv, reports/b2_e1t5_numden.md
"""
import importlib.util, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


A = load(H / '13_stage13/stage13_b2B_analyze.py', 'b2B_an')
OUT = A.P_['out'] / 'e1t5_numden_tc.csv'; REP = A.P_['rep'] / 'b2_e1t5_numden.md'


def main():
    gcm = load(H / '14_groups/groups_core.py', 'gc_b2B_nd'); tk = A.tokens()
    smp = pd.read_parquet(A.R11 / 'config/sample.parquet').set_index('paper_id')[['group']]
    src = {'false_0': A.R11 / 'raw/patch_title'} | {t: A.P_['raw'] / 'b2_e1t5' / t for t in A.TITLES[1:]}
    frames = {}
    for t in A.TITLES:
        d, sh = A.load_dir(src[t]); pp, layers = A.e1t_frame(d, tk); frames[t] = pp.join(smp)
    common = sorted(set.intersection(*[set(f.index) for f in frames.values()]))
    E = gcm.Engine(pd.DataFrame(index=pd.read_parquet(A.R10 / 'cohort/papers.parquet', columns=['paper_id']).paper_id))
    gidx = {}
    for g in ('target', 'control'):
        ids = [p for p in common if frames['false_0'].loc[p, 'group'] == g]
        gidx[g] = (ids, np.random.default_rng(3611).integers(0, len(ids), (A.NB, len(ids))), E.W(np.array(ids)))
    S = {}   # (t, g, l) -> dict(num, den, rec) each (est, paper boot, team boot)
    for t in A.TITLES:
        f = frames[t]
        for g, (ids, ix, W) in gidx.items():
            s = f.loc[ids]; den = (s['true'] - s['false']).to_numpy(); ws = W.sum(1)
            for l in layers:
                num = (s[f'p{l}'] - s['false']).to_numpy()
                with np.errstate(invalid='ignore', divide='ignore'):
                    S[(t, g, l)] = dict(
                        num=(num.mean(), num[ix].mean(1), (W @ num) / ws),
                        den=(den.mean(), den[ix].mean(1), (W @ den) / ws),
                        rec=(num.mean() / den.mean(), num[ix].mean(1) / den[ix].mean(1), (W @ num) / (W @ den)))
    rows = []
    for l in layers:
        for q in ('num', 'den', 'rec'):
            for ver, ts in (('mean5', A.TITLES), ('false_0', ['false_0'])):
                est = np.mean([S[(t, 'target', l)][q][0] - S[(t, 'control', l)][q][0] for t in ts])
                bp = np.mean([S[(t, 'target', l)][q][1] - S[(t, 'control', l)][q][1] for t in ts], 0)
                bt = np.nanmean([S[(t, 'target', l)][q][2] - S[(t, 'control', l)][q][2] for t in ts], 0)
                tgt = np.mean([S[(t, 'target', l)][q][0] for t in ts]); ctl = np.mean([S[(t, 'control', l)][q][0] for t in ts])
                lo, hi = A.pci(bp); lt, ht = E.ci(bt)
                rows.append(dict(layer=l, quantity=q, version=ver, target=tgt, control=ctl, tc=est, lo=lo, hi=hi, lo_team=lt, hi_team=ht,
                                 n_target=len(gidx['target'][0]), n_control=len(gidx['control'][0])))
    D = pd.DataFrame(rows); D.to_csv(OUT, index=False)
    pub = pd.read_csv(A.P_['out'] / 'e1t5_tc.csv').set_index('layer'); r = D[(D.quantity == 'rec') & (D.version == 'mean5')].set_index('layer')
    sc = float(max((r.tc - pub.tc_mean5).abs().max(), (r.lo_team - pub.lo_team).abs().max(), (r.hi_team - pub.hi_team).abs().max(), (r.lo - pub.lo).abs().max()))
    chk = 'OK' if sc <= 1e-9 else 'WARN'
    L = ['# Addendum 12 item 2-8 follow-up: E1t target - control, numerator and denominator (exploratory)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2B_e1t5_numden.py` (CPU, stored raw only). User request 2026-11-09. '
         'Not pre-registered (addendum 12 item 2-8 asks only for the five-title recovery; Stage 11 protocol_amendment_1 predictions concern E1t recovery > 0 only) -> exploratory.', '',
         'recovery = num / den; num = mean(patched - false), den = mean(true - false) (false = L63 element of the batch), paper means, all authors. '
         f'Papers in all five titles: target {len(gidx["target"][0])}, control {len(gidx["control"][0])}. mean5 = average over the five titles of the per-title target - control. '
         'CIs: team-cluster 2,000 (groups_core seed 391; primary) and paper bootstrap 2,000 (rng 3611), as b2_e1t5.md.', '',
         f'Self-check (recovery mean5 target - control incl. paper and team CI vs summary_b2B/e1t5_tc.csv): max |diff| {sc:.1e} -> {chk}.', '']
    for ver in ('mean5', 'false_0'):
        L += [f'## {ver}', '', '| layer | num T | num C | num T - C [team CI] (paper CI) | den T | den C | den T - C [team CI] (paper CI) | recovery T - C [team CI] |', '|---|---|---|---|---|---|---|---|']
        for l in layers:
            g = {q: D[(D.layer == l) & (D.quantity == q) & (D.version == ver)].iloc[0] for q in ('num', 'den', 'rec')}
            f3 = lambda x: f'{x.tc:+.4f} [{x.lo_team:+.4f}, {x.hi_team:+.4f}] ({x.lo:+.4f}, {x.hi:+.4f})'
            L.append(f'| L{l} | {g["num"].target:+.4f} | {g["num"].control:+.4f} | {f3(g["num"])} | {g["den"].target:+.4f} | {g["den"].control:+.4f} | {f3(g["den"])} | '
                     f'{g["rec"].tc:+.3f} [{g["rec"].lo_team:+.3f}, {g["rec"].hi_team:+.3f}] |')
        L.append('')
    L += [f'Full table: {OUT}', '']
    REP.write_text('\n'.join(L) + '\n'); print('wrote', REP, OUT, 'selfcheck', chk, sc)


if __name__ == '__main__':
    main()
