"""E1 + X6 at the missing layers: analysis (CPU, 2026-11-14). Reads stored + new raw files, never writes into raw.

Inputs
  stored  E1 false_0      361_stage11/raw/patch/                 (layers 24 32 40 48 50 52 54 56 57-63)
          X6 false_1..4   381_stage13/raw/xf_patch/false_k/       (same layers)
          U0 (false_0)    391_groups/raw/patch/U0/               (600-paper R0 x uncertain re-run; same layers)
  new     381_stage13/raw/e1x6_extra_20261114/false_k/  (+ U0/false_0/ if that optional run exists)
Merge: per title, rows joined on row_id; new-only layers (41-47, 49, 51) are added to the stored columns. For layers in both,
the STORED value is used in every estimate (the new value is used only by the hard check), so all previously published
numbers stay exactly as they were.

Estimand (exactly as stage13_x6_analyze.py / Stage 11): per name token nlr = log10(1/rank); token values are averaged within
paper first; then for a set of papers S and false title k
    R_k(l) = mean_S(nlr_patched_l - nlr_false) / mean_S(nlr_true - nlr_false)
  false_0 version = R_0(l); 5-title mean = plain average of R_0..R_4 (bootstrap: average of the 5 per-title bootstrap ratios
  computed on the SAME team draw).
CI (target / control / all): 95% percentile, 2,000 multinomial draws over author teams (team ids = stage13_cpu.group_folds),
  numpy default_rng(13), drawn once over the sorted union of papers -> identical to summary_x6/x6_recovery.csv
  (stage13_x6_analyze.py); ratio of weighted sums within each draw.
Group split (as groups_s1113.py, the published by-group E1 / X6 numbers in 391_groups/s1113_groups.csv): groups from
  papers.parquet recall_level x mc_team_outcome_tight (A = R0 strong, B = R0 fail, C = R1 strong, D = R1 fail, U0 = R0
  uncertain); only papers with consistent author flags; primary author set = UNWRITTEN authors (written == False in
  391_groups/data/author_flags.parquet), also 'all authors'; CI = groups_core.Engine (team draws, default_rng(391), 2,000),
  shared by all groups. The Stage 11 sample holds A, B, C, D only (C = 32, D = 5 papers -> D descriptive, n < 30 flagged).
  U0 comes only from the re-run list (false_0 only) and appears at the new layers only if the optional U0 run exists.
Hard check (WARN only): overlap layers present in both new and stored rows (default 40, 48, 50, 52, 54, 56):
  per title exact-equality share of rank_true, rank_false, rank_patch (threshold 0.99) and max |d log10 rank|; R_k(l) on all
  papers from new rows vs stored rows (|diff| <= 0.005); 5-title mean R(L48), R(L52) on all papers from NEW rows vs the
  published x6 averages (0.821 / 0.995, read from summary_x6/x6_recovery.csv; |diff| <= 0.005).
Parity (WARN only): stored-layer rows of the merged tables reproduce x6_recovery.csv (R, lo, hi to 1e-9) and
  s1113_groups.csv E1 / X6 by-group rows (estimate, lo, hi to 1e-9) and, if present, rerun_group_values.csv U0 rows.
Outputs: 381_stage13/summary_e1x6_extra_20261114/{e1x6_recovery.csv, e1x6_by_group.csv, hardcheck.json, parity.txt, report.md}
Usage: analyze [--new DIR] [--out DIR] [--stored-e1 DIR --stored-x6 DIR --stored-u0 DIR] (test overrides)
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R13, R391 = J / '351_stage10', J / '361_stage11', J / '381_stage13', J / '391_groups'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; NB = 2000; TOL_R = 0.005; TOL_EQ = 0.99
G5 = ['A', 'B', 'C', 'D', 'U0']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d):
    fs = sorted(Path(d).glob('shard_*.npz'))
    if not fs: return None
    zs = [np.load(f) for f in fs]; ly = [int(x) for x in zs[0]['layers']]
    for z in zs[1:]:
        if [int(x) for x in z['layers']] != ly: raise RuntimeError(f'{d}: layer lists differ between shards')
    return {k: np.concatenate([z[k] for z in zs]) for k in ('row_id', 'rank_true', 'rank_false', 'rank_patch')} | {'layers': ly, 'n_shards': len(fs)}


def token_frame(d, prefix=''):
    df = pd.DataFrame({'row_id': d['row_id'], f'{prefix}true': nlr(d['rank_true']), f'{prefix}false': nlr(d['rank_false'])})
    for i, l in enumerate(d['layers']): df[f'{prefix}p{l}'] = nlr(d['rank_patch'][:, i])
    return df.set_index('row_id')


def merge(stored, new):
    """token frame: stored columns + new-only layer columns (stored value wins on overlap). Rows: stored rows."""
    s = token_frame(stored); layers = list(stored['layers'])
    if new is not None:
        n = token_frame(new); add = [l for l in new['layers'] if l not in layers]
        miss = ~s.index.isin(n.index)
        if miss.any(): print(f'WARN {miss.sum()} stored rows have no new row (new-layer values NaN)')
        s = s.join(n[[f'p{l}' for l in add]], how='left'); layers = sorted(layers + add)
    return s, layers


def hardcheck(stored, new, pid_of):
    if new is None: return None
    s, n = token_frame(stored), token_frame(new); common = s.index.intersection(n.index)
    ov = [l for l in new['layers'] if l in stored['layers']]
    s, n = s.loc[common], n.loc[common]
    r = dict(rows_stored=int(len(stored['row_id'])), rows_new=int(len(new['row_id'])), rows_common=int(len(common)), overlap_layers=ov, per_layer={})
    rt_s, rt_n = stored['rank_true'], new['rank_true']
    so = pd.Series(np.arange(len(stored['row_id'])), index=stored['row_id']).loc[common].to_numpy()
    no = pd.Series(np.arange(len(new['row_id'])), index=new['row_id']).loc[common].to_numpy()
    r['eq_true'] = float((stored['rank_true'][so] == new['rank_true'][no]).mean()); r['eq_false'] = float((stored['rank_false'][so] == new['rank_false'][no]).mean())
    r['max_dnlr_true'] = float(np.abs(s['true'] - n['true']).max()); r['max_dnlr_false'] = float(np.abs(s['false'] - n['false']).max())
    pid = pid_of(common)
    def R(df, l):
        pp = df.assign(paper_id=pid).groupby('paper_id').mean(); return float((pp[f'p{l}'] - pp['false']).mean() / (pp['true'] - pp['false']).mean())
    for l in ov:
        a = stored['rank_patch'][so, stored['layers'].index(l)]; b = new['rank_patch'][no, new['layers'].index(l)]
        r['per_layer'][l] = dict(eq_patch=float((a == b).mean()), max_dnlr=float(np.abs(nlr(a) - nlr(b)).max()), R_stored=R(s, l), R_new=R(n, l))
        r['per_layer'][l]['dR'] = r['per_layer'][l]['R_new'] - r['per_layer'][l]['R_stored']
    ok = r['eq_true'] >= TOL_EQ and r['eq_false'] >= TOL_EQ and all(v['eq_patch'] >= TOL_EQ and abs(v['dR']) <= TOL_R for v in r['per_layer'].values())
    r['status'] = 'OK' if ok else 'WARN'; return r


def main(a):
    new_root = Path(a.new or R13 / 'raw/e1x6_extra_20261114'); OUT = Path(a.out or R13 / 'summary_e1x6_extra_20261114'); OUT.mkdir(parents=True, exist_ok=True)
    src_st = {'false_0': Path(a.stored_e1 or R11 / 'raw/patch')} | {t: Path(a.stored_x6 or R13 / 'raw/xf_patch') / t for t in TITLES[1:]}
    u0_st = Path(a.stored_u0 or R391 / 'raw/patch/U0')
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index']).set_index('row_id')
    pid_of = lambda rows: toks.loc[rows].paper_id.to_numpy()
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']]; grp = smp.set_index('paper_id').group
    warn, hc, tok_tabs, pp, layers_of, nsh = [], {}, {}, {}, {}, {}
    for t in TITLES:
        st = load_dir(src_st[t]); nw = load_dir(new_root / t)
        if st is None: warn.append(f'{t}: no stored shards'); continue
        if nw is None: warn.append(f'{t}: no new shards')
        nsh[t] = (st['n_shards'], nw['n_shards'] if nw else 0)
        tt, ly = merge(st, nw); tok_tabs[t] = tt; layers_of[t] = ly
        try: hc[t] = hardcheck(st, nw, pid_of)
        except Exception as ex: hc[t] = dict(status='WARN', note=f'hardcheck crashed: {ex!r}')
        pp[t] = tt.assign(paper_id=pid_of(tt.index)).groupby('paper_id').mean()
    have = [t for t in TITLES if t in pp]
    layers = sorted(set.intersection(*[set(layers_of[t]) for t in have]))
    for t in have:
        if set(layers_of[t]) != set(layers): warn.append(f'{t}: layers {layers_of[t]} (common set used: {layers})')
    # ---------------- target / control / all, x6 bootstrap (seed 13 over the sorted union of papers)
    allp = sorted(set().union(*[set(pp[t].index) for t in have])); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in allp]))
    cnt = np.random.default_rng(13).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)
    Wall = pd.DataFrame(cnt[:, codes].T, index=allp)
    rows, boots = [], {}
    for g in ('target', 'control', 'all'):
        for t in have:
            s = pp[t] if g == 'all' else pp[t][grp.reindex(pp[t].index).to_numpy() == g]
            W = Wall.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy()
            for l in layers:
                num = (s[f'p{l}'] - s['false']).to_numpy(); ok = np.isfinite(num)
                b = (num[ok] @ W[ok]) / (den[ok] @ W[ok]); boots[(g, t, l)] = b
                rows.append(dict(group=g, false_title=t, layer=l, n_papers=int(ok.sum()), R=num[ok].mean() / den[ok].mean(), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5),
                                 true_minus_false=den[ok].mean(), source='new' if l not in [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63] else 'stored'))
        for l in layers:
            r_t = {r['false_title']: r['R'] for r in rows if r['group'] == g and r['layer'] == l}
            b = np.mean([boots[(g, t, l)] for t in have], 0)
            rows.append(dict(group=g, false_title='average', layer=l, n_papers=np.nan, R=np.mean([r_t[t] for t in have]), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5),
                             true_minus_false=np.nan, source=rows[-1]['source']))
            for t in have[1:]:
                d = boots[(g, t, l)] - boots[(g, 'false_0', l)]
                rows.append(dict(group=g, false_title=f'{t} - false_0', layer=l, n_papers=np.nan, R=r_t[t] - r_t['false_0'], lo=np.percentile(d, 2.5), hi=np.percentile(d, 97.5),
                                 true_minus_false=np.nan, source=rows[-1]['source']))
        # target - control on the same draws
    for t in have + ['average']:
        for l in layers:
            bt = np.mean([boots[('target', x, l)] for x in have], 0) if t == 'average' else boots[('target', t, l)]
            bc = np.mean([boots[('control', x, l)] for x in have], 0) if t == 'average' else boots[('control', t, l)]
            f = lambda g: [r['R'] for r in rows if r['group'] == g and r['false_title'] == t and r['layer'] == l][0]
            d = bt - bc
            rows.append(dict(group='target - control', false_title=t, layer=l, n_papers=np.nan, R=f('target') - f('control'), lo=np.percentile(d, 2.5), hi=np.percentile(d, 97.5),
                             true_minus_false=np.nan, source='', p_two_sided=float(min(1, 2 * min((d <= 0).mean(), (d >= 0).mean())))))
    D = pd.DataFrame(rows); D.to_csv(OUT / 'e1x6_recovery.csv', index=False)
    # ---------------- group split (groups_s1113 conventions)
    gc = load(H / '14_groups/groups_core.py', 'gc_core_e1x6')
    try: gc.check_plan()
    except SystemExit as ex: warn.append(f'groups plan sha check: {ex}')
    GP = gc.papers(); E = gc.Engine(GP)
    au = pd.read_parquet(gc.DATA / 'author_flags.parquet')[['paper_id', 'author_index', 'written']]
    okp = GP[(GP.consistent == True) & GP.grp.isin(G5)]                                     # noqa: E712
    def per_paper(tt, who):
        t = toks.loc[tt.index]; k = pd.MultiIndex.from_arrays([t.paper_id.to_numpy(), t.author_index.to_numpy()])
        w = au.set_index(['paper_id', 'author_index']).written.reindex(k).to_numpy()
        df = tt.copy(); df['paper_id'] = t.paper_id.to_numpy()
        sel = (w == False) if who == 'unwritten' else pd.notna(w)                                # noqa: E712  (rows without author flags dropped, as s1113's inner merge)
        df = df[sel]; p = df.groupby('paper_id').mean(); return p[p.index.isin(okp.index)]
    u0_new = load_dir(new_root / 'U0/false_0'); u0_st_d = load_dir(u0_st)
    if u0_st_d is not None:
        tt, ly = merge(u0_st_d, u0_new); tok_tabs['U0'] = tt; layers_of['U0'] = ly
        if u0_new is not None: hc['U0 false_0'] = hardcheck(u0_st_d, u0_new, pid_of)
    grows, gboot = [], {}
    for who in ('unwritten', 'all authors'):
        ppg = {t: per_paper(tok_tabs[t], who) for t in have}
        ppu = per_paper(tok_tabs['U0'], who) if 'U0' in tok_tabs else None
        for l in layers:
            for g in G5:
                srcs = [(t, ppg[t]) for t in have] if g != 'U0' else ([('false_0', ppu)] if ppu is not None and f'p{l}' in ppu else [])
                ests, bs, n = [], [], 0
                for t, p in srcs:
                    s = p[okp.grp.reindex(p.index).to_numpy() == g]
                    s = s[np.isfinite(s[f'p{l}'])]
                    if len(s) == 0: continue
                    W = E.W(s.index); nu = (s[f'p{l}'] - s['false']).to_numpy(); de = (s['true'] - s['false']).to_numpy()
                    with np.errstate(invalid='ignore', divide='ignore'): b = (W @ nu) / (W @ de)
                    e = nu.mean() / de.mean(); gboot[(who, g, t, l)] = b; n = len(s)
                    lo, hi = E.ci(b); grows.append(dict(who=who, group=g, false_title=t, layer=l, n_papers=n, R=e, lo=lo, hi=hi, descriptive_only=n < 30)); ests.append(e); bs.append(b)
                if g != 'U0' and len(ests) == len(have) == 5:
                    b = np.mean(bs, 0); lo, hi = E.ci(b)
                    grows.append(dict(who=who, group=g, false_title='average', layer=l, n_papers=n, R=float(np.mean(ests)), lo=lo, hi=hi, descriptive_only=n < 30))
            for a_, b_ in (('A', 'B'), ('C', 'A'), ('U0', 'A'), ('U0', 'B')):
                for t in ['false_0'] + (['average'] if 'U0' not in (a_, b_) else []):
                    ka = [gboot.get((who, a_, x, l)) for x in (have if t == 'average' else ['false_0'])]
                    kb = [gboot.get((who, b_, x, l)) for x in (have if t == 'average' else ['false_0'])]
                    if any(x is None for x in ka + kb): continue
                    d = np.mean(ka, 0) - np.mean(kb, 0); lo, hi = E.ci(d)
                    ea = [r['R'] for r in grows if r['who'] == who and r['group'] == a_ and r['false_title'] == t and r['layer'] == l][0]
                    eb = [r['R'] for r in grows if r['who'] == who and r['group'] == b_ and r['false_title'] == t and r['layer'] == l][0]
                    grows.append(dict(who=who, group=f'{a_} - {b_} (unadjusted)', false_title=t, layer=l, n_papers=np.nan, R=ea - eb, lo=lo, hi=hi, descriptive_only=False, p_raw=E.pval(d)))
    G = pd.DataFrame(grows); G.to_csv(OUT / 'e1x6_by_group.csv', index=False)
    # ---------------- hard check (5-title mean from NEW rows vs published x6 averages) + parity
    par = []; x6p = R13 / 'summary_x6/x6_recovery.csv'
    if x6p.exists() and not a.test:
        x6 = pd.read_csv(x6p)
        for l in (48, 52):
            pub = x6[(x6.group == 'all') & (x6.false_title == 'average') & (x6.layer == l)]
            Rn = [hc[t]['per_layer'][l]['R_new'] for t in have if hc.get(t) and l in hc[t].get('per_layer', {})]
            if len(Rn) == 5 and len(pub):
                v = float(np.mean(Rn)); dv = v - float(pub.R.iloc[0])
                hc[f'mean5_L{l}_new_vs_published'] = dict(new=v, published=float(pub.R.iloc[0]), diff=dv, tol=TOL_R, status='OK' if abs(dv) <= TOL_R else 'WARN')
            else: hc[f'mean5_L{l}_new_vs_published'] = dict(status='INCOMPLETE', n_titles=len(Rn))
        m = D.merge(x6, on=['group', 'false_title', 'layer'], suffixes=('', '_pub'))
        dm = float(np.nanmax(np.abs(m[['R', 'lo', 'hi']].to_numpy() - m[['R_pub', 'lo_pub', 'hi_pub']].to_numpy()))) if len(m) else np.nan
        par.append(f'x6_recovery.csv: {len(m)} rows compared, max |diff| R/lo/hi = {dm:.2e} -> {"OK" if len(m) and dm < 1e-9 else "WARN"}')
        sg = pd.read_csv(R391 / 's1113_groups.csv')
        for meas, ft in (('E1 recovery', 'false_0'), ('X6 recovery (mean of 5 false titles)', 'average')):
            q = sg[(sg.measure == meas) & sg.who.isin(['unwritten', 'all authors']) & sg.group.isin(G5)].copy(); q['layer'] = q['item'].str[1:].astype(int)
            mm = G[G.false_title == ft].merge(q, on=['who', 'group', 'layer'], suffixes=('', '_pub'))
            dm = float(np.nanmax(np.abs(mm[['R', 'lo', 'hi']].to_numpy() - mm[['estimate', 'lo_pub', 'hi_pub']].to_numpy()))) if len(mm) else np.nan
            par.append(f's1113_groups.csv {meas}: {len(mm)} rows, max |diff| est/lo/hi = {dm:.2e} -> {"OK" if len(mm) and dm < 1e-9 else "WARN"}')
        rg = R391 / 'summary_rerun/rerun_group_values.csv'
        if rg.exists():
            q = pd.read_csv(rg); q = q[(q.experiment == 'E1') & (q.who == 'unwritten') & (q['item'] == 'recovery') & (q.group == 'U0')]
            mm = G[(G.false_title == 'false_0') & (G.group == 'U0') & (G.who == 'unwritten')].merge(q, on=['layer'], suffixes=('', '_pub'))
            dm = float(np.nanmax(np.abs(mm.R - mm.estimate))) if len(mm) else np.nan
            par.append(f'rerun_group_values.csv U0 E1 unwritten: {len(mm)} rows, max |diff| est = {dm:.2e} -> {"OK" if len(mm) and dm < 1e-9 else "WARN"} (CI: rerun used rerun_analyze paper filter consistent==True as here)')
    (OUT / 'hardcheck.json').write_text(json.dumps(hc, indent=1, default=float)); (OUT / 'parity.txt').write_text('\n'.join(par + warn) + '\n')
    # ---------------- report
    fm = lambda r: f'{r.R:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}]'
    def f(g, t, l):
        x = D[(D.group == g) & (D.false_title == t) & (D.layer == l)]; return fm(x.iloc[0]) if len(x) else '—'
    show = [l for l in layers if 40 <= l <= 52] + [l for l in layers if l < 40 or l > 52]
    L = ['# E1 + X6 at the missing layers (L41–47, 49, 51), merged with the stored layers', '',
         f'Shards (stored, new): ' + ', '.join(f'{t} {nsh[t]}' for t in have) + '.',
         'R(l) = mean over papers (patched_l − false) / mean (true − false), name-token log10(1/rank) averaged within paper first; '
         '95% team-cluster bootstrap, 2,000 draws, default_rng(13), shared across titles (= x6_recovery.csv). Stored values are used on overlap layers.', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    L += ['## Hard check (WARN only)', '']
    for k, v in hc.items():
        if v is None: L.append(f'- {k}: no new rows'); continue
        if 'per_layer' in v:
            L.append(f'- {k}: **{v["status"]}**; rows common {v.get("rows_common")}; eq true {v.get("eq_true", float("nan")):.4f}, eq false {v.get("eq_false", float("nan")):.4f}; '
                     + '; '.join(f'L{l} eq {p["eq_patch"]:.4f} max|dnlr| {p["max_dnlr"]:.3g} dR {p["dR"]:+.5f}' for l, p in v['per_layer'].items()))
        else: L.append(f'- {k}: {json.dumps(v, default=float)}')
    L += ['', '## Parity with published summaries', ''] + [f'- {p}' for p in par] + ['']
    for g in ('all', 'target', 'control', 'target - control'):
        L += [f'## {g}', '', '| layer | false_0 | 5-title mean | ' + ' | '.join(have[1:]) + ' |', '|---|---|---|' + '---|' * (len(have) - 1)]
        for l in show: L.append(f'| L{l}{"*" if l in [41, 42, 43, 44, 45, 46, 47, 49, 51] else ""} | {f(g, "false_0", l)} | {f(g, "average", l)} | ' + ' | '.join(f(g, t, l) for t in have[1:]) + ' |')
        L.append('')
    L += ['\\* = new layer.', '', '## By group (unwritten authors; groups_s1113 conventions; team draws default_rng(391))', '',
          '| layer | ' + ' | '.join(f'{g} false_0' for g in G5) + ' | ' + ' | '.join(f'{g} mean5' for g in G5[:4]) + ' |', '|---|' + '---|' * 9]
    def fg(g, t, l):
        x = G[(G.who == 'unwritten') & (G.group == g) & (G.false_title == t) & (G.layer == l)]
        return (fm(x.iloc[0]) + (f' n={int(x.iloc[0].n_papers)}' + (' (descr.)' if x.iloc[0].descriptive_only else ''))) if len(x) else '—'
    for l in show: L.append(f'| L{l} | ' + ' | '.join(fg(g, 'false_0', l) for g in G5) + ' | ' + ' | '.join(fg(g, 'average', l) for g in G5[:4]) + ' |')
    L += ['', 'U0: only from the 600-paper re-run list (false_0); new layers for U0 exist only if the optional U0 run was done. Group differences are unadjusted (Stage 11 sample is bin-balanced only for target vs control).', '']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('E1X6 ANALYZED')
    return D, G, hc


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', nargs='?', default='analyze')
    for k in ('--new', '--out', '--stored-e1', '--stored-x6', '--stored-u0'): ap.add_argument(k)
    ap.add_argument('--test', action='store_true', help='skip parity with published summaries (tiny run)')
    main(ap.parse_args())
