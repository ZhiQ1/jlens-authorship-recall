"""Direction 3 (user 2026-11-20): citation median split of the Stage 11 sample. EXPLORATORY (post hoc, not pre-registered). CPU only.

A. Replacement recovery (E1 false_0 + X6 false_1..4, stored raw only): per paper means of nlr = log10(1/rank) over name tokens;
   R_k(l) = mean(p_l - false) / mean(true - false); 5-title average = mean of R_0..R_4. Layers 48, 52 (also 40, 50, 56 for shape).
   Groups target / control / all and target - control (plain, as published for E1), per citation half; high - low.
B. Lens readout target - control on the same 1,186 papers: paper_title_contrasts.parquet, readouts logit / jlens_public,
   layers 40, 48, 50-56; spec_mean_nlr (primary, true - mean 5 false) and true_mean_nlr (secondary); within citation bins
   (strata = citation_bin within each half), stratum weight n_t*n_c/(n_t+n_c) fixed at the point estimate; high - low.
Split: median citations of the 1,186 papers; papers with citations <= median -> low half (ties go low).
CI: one draw set, 2,000 multinomial draws over author teams (stage13_cpu.group_folds), numpy default_rng(13) over the sorted
   papers (identical to stage13_x6_analyze.py / e1x6), ratio of weighted sums per draw; 95% percentile.
Parity (WARN only): all-papers 5-title R(L48), R(L52) vs the published 0.821 / 0.995 (summary_x6/x6_recovery.csv) within 0.001.
Supplement: lens T - C split on the full 9,108 cohort at its own median (draws over its teams, default_rng(13)).
Usage: explore_citesplit_20261120.py [--out DIR] [--tiny]   (--tiny: synthetic inputs, pipeline test)
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R13 = J / '351_stage10', J / '361_stage11', J / '381_stage13'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; NB = 2000
RL = [40, 48, 50, 52, 56]; LL = [40, 48, 50, 51, 52, 53, 54, 55, 56]; READ = ['logit', 'jlens_public']
TAG = 'exploratory (post hoc, not pre-registered)'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def ci(b):
    b = np.asarray(b, float); b = b[np.isfinite(b)]; return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def draws(pids, team_of, seed=13):
    codes, uniq = pd.factorize(pd.Series([team_of[p] for p in pids]))
    cnt = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)
    return cnt[:, codes]                                   # NB x npapers


def recovery_part(pp, meta, W, pos):
    """pp[t]: per-paper frame (index paper_id) with true, false, p{l}. meta: paper_id -> group, half."""
    rows, boots = [], {}
    sets = {}
    for half in ('low', 'high', 'both'):
        for g in ('target', 'control', 'all'):
            m = meta.copy()
            if half != 'both': m = m[m.half == half]
            if g != 'all': m = m[m.group == g]
            sets[(half, g)] = m.index
    for (half, g), idx in sets.items():
        for l in RL:
            bs, es = [], []
            for t in TITLES:
                s = pp[t].reindex(idx).dropna(subset=['true', 'false', f'p{l}'])
                num = (s[f'p{l}'] - s['false']).to_numpy(); den = (s['true'] - s['false']).to_numpy()
                Wt = W[:, pos.loc[s.index].to_numpy()]
                b = (Wt @ num) / (Wt @ den); e = num.mean() / den.mean()
                boots[(half, g, t, l)] = b; bs.append(b); es.append(e)
                if t == 'false_0':
                    lo, hi = ci(b); rows.append(dict(half=half, group=g, title='false_0', layer=l, n_papers=len(s), R=e, lo=lo, hi=hi))
            b = np.mean(bs, 0); boots[(half, g, 'avg', l)] = b; lo, hi = ci(b)
            rows.append(dict(half=half, group=g, title='average', layer=l, n_papers=len(s), R=float(np.mean(es)), lo=lo, hi=hi))
    D = pd.DataFrame(rows)
    est = lambda half, g, t, l: D[(D.half == half) & (D.group == g) & (D.title == t) & (D.layer == l)].R.iloc[0]
    extra = []
    for t in ('average', 'false_0'):
        k = 'avg' if t == 'average' else 'false_0'
        for l in RL:
            for half in ('low', 'high', 'both'):                                           # target - control per half
                d = boots[(half, 'target', k, l)] - boots[(half, 'control', k, l)]; lo, hi = ci(d)
                extra.append(dict(half=half, group='target - control', title=t, layer=l, R=est(half, 'target', t, l) - est(half, 'control', t, l), lo=lo, hi=hi))
            for g in ('target', 'control', 'all'):                                          # high - low per group
                d = boots[('high', g, k, l)] - boots[('low', g, k, l)]; lo, hi = ci(d)
                extra.append(dict(half='high - low', group=g, title=t, layer=l, R=est('high', g, t, l) - est('low', g, t, l), lo=lo, hi=hi))
            d = (boots[('high', 'target', k, l)] - boots[('high', 'control', k, l)]) - (boots[('low', 'target', k, l)] - boots[('low', 'control', k, l)])
            lo, hi = ci(d)
            e = (est('high', 'target', t, l) - est('high', 'control', t, l)) - (est('low', 'target', t, l) - est('low', 'control', t, l))
            extra.append(dict(half='high - low', group='target - control', title=t, layer=l, R=e, lo=lo, hi=hi))
    return pd.concat([D, pd.DataFrame(extra)], ignore_index=True)


def lens_part(L, meta, W, pos, label):
    """L: rows paper_id, readout, layer, spec_mean_nlr, true_mean_nlr. Within-bin T - C per half, high - low."""
    rows = []
    for rd in READ:
        for l in LL:
            sub = L[(L.readout == rd) & (L.layer == l)].set_index('paper_id')
            for meas in ('spec_mean_nlr', 'true_mean_nlr'):
                res = {}
                for half in ('low', 'high', 'both'):
                    m = meta if half == 'both' else meta[meta.half == half]
                    x = sub[meas].reindex(m.index); ok = x.notna()
                    m, x = m[ok], x[ok].to_numpy()
                    strata = m.citation_bin.astype(str) + '|' + m.half
                    est, bnum, wsum, ns = 0.0, np.zeros(NB), 0.0, [0, 0]
                    for s_, mm in m.groupby(strata):
                        it = (mm.group == 'target').to_numpy(); ic = (mm.group == 'control').to_numpy()
                        nt, nc = it.sum(), ic.sum()
                        if nt == 0 or nc == 0: continue
                        w = nt * nc / (nt + nc); xi = x[m.index.get_indexer(mm.index)]
                        Wi = W[:, pos.loc[mm.index].to_numpy()]
                        with np.errstate(invalid='ignore', divide='ignore'):
                            bt = (Wi[:, it] @ xi[it]) / Wi[:, it].sum(1); bc = (Wi[:, ic] @ xi[ic]) / Wi[:, ic].sum(1)
                        est += w * (xi[it].mean() - xi[ic].mean()); bnum += w * (bt - bc); wsum += w; ns[0] += nt; ns[1] += nc
                    res[half] = (est / wsum, bnum / wsum, ns)
                for half in ('low', 'high', 'both'):
                    e, b, ns = res[half]; lo, hi = ci(b)
                    rows.append(dict(sample=label, readout=rd, layer=l, measure=meas, half=half, n_target=ns[0], n_control=ns[1], tc=e, lo=lo, hi=hi))
                d = res['high'][1] - res['low'][1]; lo, hi = ci(d)
                rows.append(dict(sample=label, readout=rd, layer=l, measure=meas, half='high - low', n_target=np.nan, n_control=np.nan, tc=res['high'][0] - res['low'][0], lo=lo, hi=hi))
    return pd.DataFrame(rows)


def split(meta):
    med = float(meta.citations.median()); meta['half'] = np.where(meta.citations > med, 'high', 'low'); return med


def fmt(v, lo, hi): return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def main(a):
    OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
    if a.tiny:
        rng = np.random.default_rng(0); n = 200; pids = [f'p{i}' for i in range(n)]
        meta = pd.DataFrame(dict(group=np.where(np.arange(n) % 2, 'target', 'control'), citation_bin=rng.choice(['b1', 'b2', 'b3'], n),
                                 citations=rng.integers(1, 1000, n)), index=pids)
        team = {p: f't{i // 2}' for i, p in enumerate(pids)}
        pp = {}
        for t in TITLES:
            tr = rng.normal(1, .3, n); fa = rng.normal(0, .3, n); df = pd.DataFrame(dict(true=tr, false=fa), index=pids)
            for l in RL: df[f'p{l}'] = fa + (tr - fa) * min(1, (l - 30) / 22) + rng.normal(0, .05, n)
            pp[t] = df
        L = pd.DataFrame([dict(paper_id=p, readout=r, layer=l, spec_mean_nlr=rng.normal(.05 * (meta.group[p] == 'target'), .1),
                               true_mean_nlr=rng.normal(.1, .1)) for p in pids for r in READ for l in LL])
        full_meta, full_team, Lfull = meta.copy(), team, L
    else:
        c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); e1 = load(H / '13_stage13/stage13_e1x6_extra_analyze_20261114.py', 'e1x6')
        papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
        _, tm = c13.group_folds(papers.paper_id.to_numpy()); team = dict(zip(papers.paper_id, tm))
        smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']].set_index('paper_id')
        cit = pd.to_numeric(papers.set_index('paper_id').citations, errors='coerce')
        meta = smp.assign(citations=cit.reindex(smp.index).to_numpy())
        toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
        src = {'false_0': R11 / 'raw/patch'} | {t: R13 / 'raw/xf_patch' / t for t in TITLES[1:]}
        pp = {}
        for t in TITLES:
            d = e1.load_dir(src[t]); tf = e1.token_frame(d)
            pp[t] = tf.assign(paper_id=toks.loc[tf.index].to_numpy()).groupby('paper_id').mean()
            print(t, 'papers', len(pp[t]), 'layers', d['layers'], flush=True)
        L = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet',
                            columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr', 'true_mean_nlr', 'group_tight', 'citation_bin', 'citations'])
        L = L[L.readout.isin(READ) & L.layer.isin(LL)]
        full_meta = L.drop_duplicates('paper_id').set_index('paper_id')[['group_tight', 'citation_bin', 'citations']].rename(columns={'group_tight': 'group'})
        full_meta['citations'] = pd.to_numeric(full_meta.citations, errors='coerce'); full_team = team
    med = split(meta)
    pids = sorted(meta.index); pos = pd.Series(np.arange(len(pids)), index=pids); W = draws(pids, team)
    REC = recovery_part(pp, meta, W, pos); REC.insert(0, 'label', TAG); REC.to_csv(OUT / 'recovery_by_half.csv', index=False)
    LEN = lens_part(L[L.paper_id.isin(meta.index)], meta, W, pos, 'stage11_1186'); LEN.insert(0, 'label', TAG)
    # supplement: full cohort at its own median (target / control only)
    fm = full_meta[full_meta.group.isin(['target', 'control'])].copy(); fmed = split(fm)
    fp = sorted(fm.index); fpos = pd.Series(np.arange(len(fp)), index=fp); FW = draws(fp, full_team)
    LENF = lens_part(L[L.paper_id.isin(fm.index)], fm, FW, fpos, f'supplement_full_cohort'); LENF.insert(0, 'label', TAG + '; supplement')
    pd.concat([LEN, LENF]).to_csv(OUT / 'lens_tc_by_half.csv', index=False)
    # parity
    par = {}
    if not a.tiny:
        x6 = pd.read_csv(R13 / 'summary_x6/x6_recovery.csv')
        for l, pub in ((48, 0.821), (52, 0.995)):
            mine = REC[(REC.half == 'both') & (REC.group == 'all') & (REC.title == 'average') & (REC.layer == l)].R.iloc[0]
            row = x6[(x6.group == 'all') & (x6.false_title == 'average') & (x6.layer == l)] if 'false_title' in x6 else x6.iloc[0:0]
            ref = float(row.R.iloc[0]) if len(row) else pub
            par[f'R_L{l}'] = dict(mine=mine, published=ref, rounded_published=pub, diff=mine - ref, status='OK' if abs(mine - ref) <= 0.001 else 'WARN')
    nt = meta.groupby(['half', 'group']).size().to_dict()
    info = dict(label=TAG, median_citations=med, ties='papers with citations <= median go to the low half',
                n=dict((f'{h}/{g}', int(v)) for (h, g), v in nt.items()), full_cohort_median=fmed,
                full_n=dict((f'{h}/{g}', int(v)) for (h, g), v in fm.groupby(['half', 'group']).size().to_dict().items()),
                cit_range={h: [float(meta[meta.half == h].citations.min()), float(meta[meta.half == h].citations.max())] for h in ('low', 'high')},
                parity=par, NB=NB, seed=13)
    json.dump(info, open(OUT / 'info.json', 'w'), indent=1, default=float)
    # report
    q = lambda half, g, t, l: REC[(REC.half == half) & (REC.group == g) & (REC.title == t) & (REC.layer == l)].iloc[0]
    rep = [f'# Citation median split of the Stage 11 sample — {TAG}', '',
           f'Median citations of the {len(meta):,} papers = {med:g} (ties go to the low half). n: ' + ', '.join(f'{k} {v}' for k, v in info['n'].items()) +
           f'. Citation ranges: low {info["cit_range"]["low"]}, high {info["cit_range"]["high"]}. Team bootstrap, {NB} draws, default_rng(13), one draw set for all comparisons.', '',
           '## A. Replacement recovery R(l) (5-title average; false_0 in recovery_by_half.csv)', '',
           '| layer | group | low | high | high − low |', '|---|---|---|---|---|']
    for l in (48, 52):
        for g in ('target', 'control', 'all', 'target - control'):
            lo_, hi_ = q('low', g, 'average', l), q('high', g, 'average', l); d = q('high - low', g, 'average', l)
            rep.append(f'| L{l} | {g} | {fmt(lo_.R, lo_.lo, lo_.hi)} | {fmt(hi_.R, hi_.lo, hi_.hi)} | {fmt(d.R, d.lo, d.hi)} |')
    rep += ['', '## B. Lens readout target − control within citation bins (spec_mean_nlr, title-specific)', '',
            '| readout | layer | low | high | high − low |', '|---|---|---|---|---|']
    for rd in READ:
        for l in LL:
            s = LEN[(LEN.readout == rd) & (LEN.layer == l) & (LEN.measure == 'spec_mean_nlr')].set_index('half')
            rep.append(f'| {rd} | L{l} | ' + ' | '.join(fmt(s.loc[h].tc, s.loc[h].lo, s.loc[h].hi) for h in ('low', 'high', 'high - low')) + ' |')
    rep += ['', f'## Supplement: full cohort (target/control, median {fmed:g}), spec_mean_nlr', '', '| readout | layer | low | high | high − low |', '|---|---|---|---|---|']
    for rd in READ:
        for l in (40, 48, 52, 56):
            s = LENF[(LENF.readout == rd) & (LENF.layer == l) & (LENF.measure == 'spec_mean_nlr')].set_index('half')
            rep.append(f'| {rd} | L{l} | ' + ' | '.join(fmt(s.loc[h].tc, s.loc[h].lo, s.loc[h].hi) for h in ('low', 'high', 'high - low')) + ' |')
    rep += ['', f'Parity (WARN only): {json.dumps(par, default=float)}', '',
            'true_mean_nlr (secondary) and all layers / readouts / false_0 are in the CSVs. Labels: exploratory, post hoc; single model; '
            'halves of a sample stratified by citation bin, not population rates; target − control for R is plain (as published for E1), '
            'lens target − control is within citation bins.']
    (OUT / 'report.md').write_text('\n'.join(rep) + '\n'); print('\n'.join(rep)); print('DONE', OUT, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', default=str(R13 / 'summary_explore_citesplit_20261120')); p.add_argument('--tiny', action='store_true')
    main(p.parse_args())
