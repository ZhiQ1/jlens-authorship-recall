"""Exploratory (post hoc, not pre-registered), 2026-11-21: does the target - control probe signal differ between low- and
high-citation papers?  ("276x gap location", user reading rule: high half stronger at the title-position probe -> the gap is at
recognising; equal -> the gap is at saying.)  CPU only, stored per-paper probe outputs only.

Probes (per paper spec = probe(true) - probe(false)):
  title   E4b title-position probe, first author first token (summary_b1_e4b5/probe/perpaper_e4b_parity_L40.parquet);
          V0 = spec0 on papers with drop0 == False (the confirmed 1,395-paper version, C09); Vpd = mean of spec_k over the
          false titles not dropped (per-donor rule; larger n).
  name    name-position probe, surname first token, Vpd (summary_b2_np/probe_v2/perpaper_surname_first_L{40,48}.parquet;
          the 4,654 papers of the locked H3 test).
Sets: (S11) Stage-11 sample (1,186) intersect available, split at the Stage-11 median (31 citations, ties low);
      (FULL) each probe's full available target+control set, split at its own median (ties low).
Contrast: target - control within citation bins (bins with >= MINB papers per group inside the half; weights n_t n_c/(n_t+n_c));
          low, high, high - low. CI: 2,000 multinomial draws over author teams (stage13_cpu.group_folds), default_rng(1121),
          one draw set per analysis set. Also plain group means per half.
"""
import argparse, importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
KS = [0, 1, 2, 3, 4]; NB = 2000; MINB = 3


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def ci(b): b = b[np.isfinite(b)]; return (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))) if len(b) else (np.nan, np.nan)


def vpd(df):
    s = np.stack([df[f'spec_k{k}'].to_numpy() for k in KS], 1); m = np.stack([~df[f'dropped_{k}'].to_numpy().astype(bool) for k in KS], 1)
    with np.errstate(invalid='ignore'): v = np.where(m, s, 0).sum(1) / m.sum(1)
    return np.where(m.sum(1) > 0, v, np.nan)


def tc_within(y, g, b, W):
    """within-bin T - C; y, g ('target'/'control'), b (bin) arrays; W [NB, n] weights or None -> point"""
    est, num, den = 0.0, 0.0, 0.0; nums = None
    for bb in np.unique(b):
        it, ic = (b == bb) & (g == 'target'), (b == bb) & (g == 'control')
        if it.sum() < MINB or ic.sum() < MINB: continue
        w = it.sum() * ic.sum() / (it.sum() + ic.sum())
        d = y[it].mean() - y[ic].mean(); num += w * d; den += w
        if W is not None:
            wt, wc = W[:, it], W[:, ic]
            with np.errstate(invalid='ignore', divide='ignore'): db = (wt @ y[it]) / wt.sum(1) - (wc @ y[ic]) / wc.sum(1)
            nums = w * db if nums is None else nums + w * db
    if den == 0: return np.nan, None
    return num / den, (nums / den if nums is not None else None)


def analyse(name, P, y, team, tiny):
    """P: frame with paper_id, group, citation_bin, cit, half; y: values"""
    ok = np.isfinite(y) & P.group.isin(['target', 'control']).to_numpy(); P = P[ok].reset_index(drop=True); y = y[ok]
    codes, uniq = pd.factorize(pd.Series([team[p] for p in P.paper_id]))
    W = np.random.default_rng(1121).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=(50 if tiny else NB)).astype(float)[:, codes]
    out = []; boots = {}
    for h in ['low', 'high']:
        m = (P.half == h).to_numpy(); g = P.group.to_numpy()[m]; b = P.citation_bin.to_numpy()[m]
        e, bt = tc_within(y[m], g, b, W[:, m]); boots[h] = bt
        nT, nC = int((g == 'target').sum()), int((g == 'control').sum())
        mt, mc = y[m][g == 'target'].mean() if nT else np.nan, y[m][g == 'control'].mean() if nC else np.nan
        lo, hi = ci(bt) if bt is not None else (np.nan, np.nan)
        out.append(dict(set=name, half=h, n_target=nT, n_control=nC, mean_target=mt, mean_control=mc, tc_within=e, lo=lo, hi=hi,
                        cit_min=float(P.cit[m].min()), cit_max=float(P.cit[m].max())))
    if boots['low'] is not None and boots['high'] is not None:
        d = boots['high'] - boots['low']; lo, hi = ci(d)
        out.append(dict(set=name, half='high - low', tc_within=out[1]['tc_within'] - out[0]['tc_within'], lo=lo, hi=hi))
    return out


def main(a):
    OUT = R13 / ('summary_explore_citesplit_probes_20261121' + ('_tiny' if a.tiny else '')); OUT.mkdir(parents=True, exist_ok=True)
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'citations'])
    papers = papers.rename(columns={'group_tight': 'group'}); papers['cit'] = pd.to_numeric(papers.citations, errors='coerce')
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    s11 = set(pd.read_parquet(R11 / 'config/sample.parquet').paper_id)
    med11 = float(papers[papers.paper_id.isin(s11)].cit.median())
    e4 = pd.read_parquet(R13 / 'summary_b1_e4b5/probe/perpaper_e4b_parity_L40.parquet')
    srcs = {'title E4b V0 (spec0, reuse-free) L40': (e4, np.where(~e4.drop0.to_numpy().astype(bool), e4.spec0.to_numpy(), np.nan)),
            'title E4b Vpd L40': (e4, vpd(e4))}
    for l in (40, 48):
        npp = pd.read_parquet(R13 / f'summary_b2_np/probe_v2/perpaper_surname_first_L{l}.parquet'); srcs[f'name-position Vpd L{l}'] = (npp, vpd(npp))
    rows, info = [], dict(label='exploratory (post hoc, not pre-registered)', median_stage11=med11, minb=MINB)
    for nm, (df, y) in srcs.items():
        P = df[['paper_id']].merge(papers, on='paper_id', how='left')
        if a.tiny: keep = np.arange(len(P)) % 4 == 0; P, y = P[keep].reset_index(drop=True), y[keep]
        okall = np.isfinite(y) & P.group.isin(['target', 'control']).to_numpy()
        n_tc = int(okall.sum())
        if nm == 'title E4b V0 (spec0, reuse-free) L40': info['n_V0_check'] = n_tc
        # FULL
        medf = float(P.cit[okall].median()); Pf = P.copy(); Pf['half'] = np.where(Pf.cit <= medf, 'low', 'high')
        for r in analyse(f'{nm} · FULL (median {medf:g})', Pf, y, TEAM, a.tiny): rows.append(r)
        # S11
        m11 = P.paper_id.isin(s11).to_numpy(); Ps = P[m11].reset_index(drop=True); Ps['half'] = np.where(Ps.cit <= med11, 'low', 'high')
        for r in analyse(f'{nm} · Stage-11 ∩ (median {med11:g})', Ps, y[m11], TEAM, a.tiny): rows.append(r)
        print(nm, 'n T+C', n_tc, flush=True)
    D = pd.DataFrame(rows); D.to_csv(OUT / 'citesplit_probes.csv', index=False); json.dump(info, open(OUT / 'info.json', 'w'), indent=1)
    fmt = lambda r: (f"{r['tc_within']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]" if np.isfinite(r['tc_within']) else 'n/a')
    L = ['# Citation split of the title-position and name-position probes — exploratory (post hoc, not pre-registered)', '', __doc__, '',
         '| set | half | n T / C | citations | mean T | mean C | T − C within bins [95% team CI] |', '|---|---|---|---|---|---|---|']
    for _, r in D.iterrows():
        if r['half'] == 'high - low': L.append(f"| {r['set']} | high − low | | | | | {fmt(r)} |")
        else: L.append(f"| {r['set']} | {r['half']} | {r['n_target']} / {r['n_control']} | {r['cit_min']:g}–{r['cit_max']:g} | {r['mean_target']:+.4f} | {r['mean_control']:+.4f} | {fmt(r)} |")
    L += ['', f"V0 check: target+control papers with drop0 == False = {info.get('n_V0_check')} (published 1,395)."]
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); print('DONE', OUT, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); main(ap.parse_args())
