"""Stage 13 X6 / X7 by name-token role (handbook V41; prereg addendum 4 "token_roles"). CPU, read-only on raw data.
Same estimands, bootstrap seeds and layers as stage13_x6_analyze.py (seed 13) and stage13_x7_analyze.py (seed 17):
the team-cluster weight matrix is drawn over the full paper set exactly as in the originals and then restricted to
the papers that have tokens of the role (so role 'ALL' reproduces the original CSVs, checked below, WARN only).
Per role: rows of that role only, tokens averaged within paper first, then ratio of means.
Roles (name_tokens.parquet 'role'): name_first = initial_first + given_first (first token of the name, predicted at ':'),
surname_first, surname_cont (the 3 pre-registered roles); also initial_first, given_first, given_cont, punct,
particle_first. Gap rule (addendum 4): R / T / F / S are not reported (NaN) where mean(true - false) < 0.05.
X6 verdict (addendum 3) per role: average R(L48) in [0.70, 0.95], average R(L52) >= 0.95, every title |R48 - R48(false_0)| <= 0.10
and R52 >= 0.90. X7 verdict per role: S(L52) <= 0.05 and S(L0) >= 0.5. Also paired role - ALL differences.
Usage: stage13_x6x7_roles.py [--tiny OUTDIR]  (tiny: first 2 shards per source, outputs to OUTDIR)
Outputs: summary_x6/x6_roles.csv, summary_x7/x7_roles.csv, reports/x6x7_roles.md"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; NB = 2000; GAP = 0.05
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']
ROLES = {'ALL': None, 'name_first': ['initial_first', 'given_first'], 'surname_first': ['surname_first'], 'surname_cont': ['surname_cont'],
         'initial_first': ['initial_first'], 'given_first': ['given_first'], 'given_cont': ['given_cont'], 'punct': ['punct'],
         'particle_first': ['particle_first']}
PRIMARY = ['name_first', 'surname_first', 'surname_cont']
GROUPS = ('target', 'control', 'all')


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d, keys, nmax=None):
    fs = sorted(Path(d).glob('shard_*.npz'))[:nmax]
    if not fs: return None, None, 0
    zs = [np.load(f) for f in fs]
    return {k: np.concatenate([z[k] for z in zs]) for k in keys}, [int(x) for x in zs[0]['layers']], len(fs)


def team_weights(papers_sorted, TEAM, seed):
    codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in papers_sorted]))
    return pd.DataFrame(np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)[:, codes].T, index=papers_sorted)


def subset(df, role):
    return df if ROLES[role] is None else df[df.role.isin(ROLES[role])]


def gsel(pp, grp, g):
    return pp if g == 'all' else pp[grp.reindex(pp.index).to_numpy() == g]


def main():
    tiny = '--tiny' in sys.argv; nmax = 2 if tiny else None
    OUT6, OUT7, REP = (ROOT / 'summary_x6', ROOT / 'summary_x7', ROOT / 'reports') if not tiny else (Path(sys.argv[sys.argv.index('--tiny') + 1]),) * 3
    for o in (OUT6, OUT7, REP): o.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'role']).set_index('row_id')
    grp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].set_index('paper_id').group
    warn = []

    # ---------------- X6 ----------------
    src = {'false_0': R11 / 'raw/patch'} | {t: ROOT / 'raw/xf_patch' / t for t in TITLES[1:]}
    rowdf, layers, nshard = {}, None, {}
    for t, d in src.items():
        dd, ly, n = load_dir(d, ('row_id', 'rank_true', 'rank_false', 'rank_patch'), nmax); nshard[t] = n
        if dd is None: warn.append(f'X6 {t}: no shards'); continue
        if layers is None: layers = ly
        elif ly != layers: warn.append(f'X6 {t}: layers differ')
        df = pd.DataFrame({'paper_id': toks.loc[dd['row_id']].paper_id.to_numpy(), 'role': toks.loc[dd['row_id']].role.to_numpy(),
                           'true': nlr(dd['rank_true']), 'false': nlr(dd['rank_false'])})
        for i, l in enumerate(ly): df[f'p{l}'] = nlr(dd['rank_patch'][:, i])
        rowdf[t] = df
    have = [t for t in TITLES if t in rowdf]
    allp = sorted(set().union(*[set(rowdf[t].paper_id) for t in have])); Wall = team_weights(allp, TEAM, 13)
    rows, boots = [], {}
    for role in ROLES:
        pp = {t: subset(rowdf[t], role).drop(columns='role').groupby('paper_id').mean() for t in have}
        for g in GROUPS:
            ok_all = True
            for t in have:
                s = gsel(pp[t], grp, g); W = Wall.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy(); gap = den.mean() if len(s) else np.nan
                ok = bool(len(s) and gap >= GAP); ok_all &= ok
                for l in layers:
                    num = (s[f'p{l}'] - s['false']).to_numpy()
                    b = (num @ W) / (den @ W) if ok else np.full(NB, np.nan); boots[(role, g, t, l)] = b
                    rows.append(dict(role=role, group=g, false_title=t, layer=l, n_papers=len(s), n_rows=int(subset(rowdf[t], role).paper_id.isin(s.index).sum()),
                                     true_minus_false=gap, reportable=ok, R=num.mean() / den.mean() if ok else np.nan,
                                     lo=np.percentile(b, 2.5) if ok else np.nan, hi=np.percentile(b, 97.5) if ok else np.nan))
            for l in layers:
                Rs = [r['R'] for r in rows if r['role'] == role and r['group'] == g and r['layer'] == l and r['false_title'] in have]
                b = np.mean([boots[(role, g, t, l)] for t in have], 0); boots[(role, g, 'average', l)] = b
                rows.append(dict(role=role, group=g, false_title='average', layer=l, n_papers=np.nan, n_rows=np.nan, true_minus_false=np.nan, reportable=ok_all,
                                 R=np.mean(Rs) if ok_all else np.nan, lo=np.percentile(b, 2.5) if ok_all else np.nan, hi=np.percentile(b, 97.5) if ok_all else np.nan))
                if role != 'ALL':      # paired difference from the pooled (ALL) average
                    est = lambda rl: [r['R'] for r in rows if r['role'] == rl and r['group'] == g and r['false_title'] == 'average' and r['layer'] == l][0]
                    d = b - boots[('ALL', g, 'average', l)]
                    rows.append(dict(role=role, group=g, false_title='average - ALL', layer=l, n_papers=np.nan, n_rows=np.nan, true_minus_false=np.nan, reportable=ok_all,
                                     R=est(role) - est('ALL') if ok_all else np.nan, lo=np.percentile(d, 2.5) if ok_all else np.nan, hi=np.percentile(d, 97.5) if ok_all else np.nan))
    D6 = pd.DataFrame(rows); D6.to_csv(OUT6 / 'x6_roles.csv', index=False)
    if not tiny:   # self-check: ALL == original x6_recovery.csv
        try:
            o = pd.read_csv(ROOT / 'summary_x6/x6_recovery.csv'); o = o[o.false_title.isin(TITLES + ['average'])]
            m = D6[D6.role == 'ALL'].merge(o, on=['group', 'false_title', 'layer'], suffixes=('', '_o'))
            d6 = float(np.abs(m[['R', 'lo', 'hi']].to_numpy() - m[['R_o', 'lo_o', 'hi_o']].to_numpy()).max())
            if not (d6 < 1e-9 and len(m) == len(o)): warn.append(f'X6 ALL vs x6_recovery.csv: max|diff| {d6:.2e} over {len(m)}/{len(o)} rows')
        except Exception as ex: d6 = np.nan; warn.append(f'X6 self-check failed: {ex!r}')
    else: d6 = np.nan

    # ---------------- X7 ----------------
    d, _, _ = load_dir(R11 / 'raw/patch', ['row_id', 'rank_true', 'rank_false'], nmax)
    kT, kl, nT = load_dir(R11 / 'raw/knockout', ['row_id', 'rank_ko'], nmax)
    kF, klF, nF = load_dir(ROOT / 'raw/ko_false/false_0', ['row_id', 'rank_ko'], nmax)
    if kl != klF: warn.append(f'X7 knockout layers differ: {kl} vs {klF}')
    base = pd.DataFrame({'row_id': d['row_id'], 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])})
    tt = pd.DataFrame({'row_id': kT['row_id'], **{f'T{l}': nlr(kT['rank_ko'][:, i]) for i, l in enumerate(kl)}})
    ff = pd.DataFrame({'row_id': kF['row_id'], **{f'F{l}': nlr(kF['rank_ko'][:, i]) for i, l in enumerate(klF)}})
    m = base.merge(tt, on='row_id').merge(ff, on='row_id')
    if len(m) != len(base): warn.append(f'X7 rows: patch {len(base)}, knockout {len(tt)}, ko_false {len(ff)}, matched {len(m)}')
    m['paper_id'] = toks.loc[m.row_id].paper_id.to_numpy(); m['role'] = toks.loc[m.row_id].role.to_numpy()
    pall = m.drop(columns=['row_id', 'role']).groupby('paper_id').mean()
    W7 = team_weights(list(pall.index), TEAM, 17)
    rows, bS = [], {}
    for role in ROLES:
        pp = subset(m, role).drop(columns=['row_id', 'role']).groupby('paper_id').mean()
        for g in GROUPS:
            s = gsel(pp, grp, g); w = W7.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy(); dw = den @ w
            gap = den.mean() if len(s) else np.nan; ok = bool(len(s) and gap >= GAP)
            for l in kl:
                if l == 64: continue
                nt = (s['T64'] - s[f'T{l}']).to_numpy(); nf = (s['F64'] - s[f'F{l}']).to_numpy()
                r = dict(role=role, group=g, start_layer=l, n_papers=len(s), n_rows=int(subset(m, role).paper_id.isin(s.index).sum()), true_minus_false=gap, reportable=ok)
                if ok:
                    bt, bf = (nt @ w) / dw, (nf @ w) / dw; bS[(role, g, l)] = bt - bf
                    r.update(T=nt.mean() / den.mean(), F=nf.mean() / den.mean()); r['S'] = r['T'] - r['F']
                    for k, b in (('T', bt), ('F', bf), ('S', bt - bf)): r[k + '_lo'], r[k + '_hi'] = np.percentile(b, [2.5, 97.5])
                    if role != 'ALL' and ('ALL', g, l) in bS:
                        dS = bS[(role, g, l)] - bS[('ALL', g, l)]; r['S_minus_ALL_lo'], r['S_minus_ALL_hi'] = np.percentile(dS, [2.5, 97.5])
                rows.append(r)
    D7 = pd.DataFrame(rows)
    a = D7[D7.role == 'ALL'].set_index(['group', 'start_layer']).S
    D7['S_minus_ALL'] = [r.S - a.loc[(r.group, r.start_layer)] if r.role != 'ALL' else np.nan for r in D7.itertuples()]
    D7.to_csv(OUT7 / 'x7_roles.csv', index=False)
    if not tiny:
        try:
            o = pd.read_csv(ROOT / 'summary_x7/x7_knockout.csv'); mm = D7[D7.role == 'ALL'].merge(o, on=['group', 'start_layer'], suffixes=('', '_o'))
            cols = ['T', 'F', 'S', 'S_lo', 'S_hi']; d7 = float(np.abs(mm[cols].to_numpy() - mm[[c + '_o' for c in cols]].to_numpy()).max())
            if not (d7 < 1e-9 and len(mm) == len(o)): warn.append(f'X7 ALL vs x7_knockout.csv: max|diff| {d7:.2e} over {len(mm)}/{len(o)} rows')
        except Exception as ex: d7 = np.nan; warn.append(f'X7 self-check failed: {ex!r}')
    else: d7 = np.nan

    # ---------------- report ----------------
    fm = lambda R, lo, hi: '--' if pd.isna(R) else f'{R:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    def x6(role, g, t, l):
        r = D6[(D6.role == role) & (D6.group == g) & (D6.false_title == t) & (D6.layer == l)]; return r.iloc[0] if len(r) else None
    def x7(role, g, l):
        r = D7[(D7.role == role) & (D7.group == g) & (D7.start_layer == l)]; return r.iloc[0] if len(r) else None
    KL6 = [l for l in (44, 48, 52, 56) if l in layers]; KL7 = [l for l in (0, 44, 48, 52, 56) if l in kl]
    L = ['# Stage 13 X6 / X7 by name-token role (V41, prereg addendum 4 "token_roles")', '',
         f'Script `13_stage13/stage13_x6x7_roles.py`{" (TINY: 2 shards per source)" if tiny else ""}. X6 shards: ' + ', '.join(f'{t} {nshard[t]}' for t in TITLES)
         + f'; X7 shards: knockout {nT}, ko_false {nF}.',
         'Same estimands, layers and team-cluster bootstrap as x6_report.md (seed 13) and x7_report.md (seed 17); the original draws are restricted to the papers that have tokens of the role. '
         'Per role, a paper\'s tokens of that role are averaged first, then R = mean(patched - false)/mean(true - false) (X6) and T, F, S as in X7.',
         f'Roles: **name_first** = first token of the name (initial_first + given_first, predicted at ":"), **surname_first**, **surname_cont** (pre-registered); also initial_first, given_first, given_cont, punct, particle_first. '
         f'Gap rule: no ratio where mean(true - false) < {GAP} ("--").',
         f'Note: L44 is not among the stored layers (X6 layers {layers}; X7 start layers {[l for l in kl if l != 64]}); tables show L48/L52/L56 (and L0 for X7).', '',
         f'Self-checks (WARN only): role ALL vs original CSVs: X6 max|diff| {d6:.1e}, X7 max|diff| {d7:.1e}.', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    # gaps
    L += ['## Gap true - false per role (nlr units; X6 false_0..false_4, X7 = false_0)', '', '| role | group | n papers | gap false_0..4 | reportable |', '|---|---|---|---|---|']
    for role in ROLES:
        for g in GROUPS:
            gs = [x6(role, g, t, layers[0]) for t in have]
            L.append(f'| {role} | {g} | {gs[0].n_papers} | ' + ' / '.join(f'{x.true_minus_false:.3f}' for x in gs) + f' | {"yes" if x6(role, g, "average", layers[0]).reportable else "no"} |')
    L += ['', '## X6: recovery R averaged over the 5 false titles (95% team CI)', '']
    for g in GROUPS:
        L += [f'### {g}', '', '| role | ' + ' | '.join(f'L{l}' for l in KL6) + ' | L48 role - ALL | L52 role - ALL |', '|---|' + '---|' * (len(KL6) + 2)]
        for role in ROLES:
            c = [x6(role, g, 'average', l) for l in KL6]; dd = [x6(role, g, 'average - ALL', l) for l in (48, 52)]
            L.append(f'| {role} | ' + ' | '.join(fm(x.R, x.lo, x.hi) for x in c) + ' | ' + ' | '.join('' if x is None else fm(x.R, x.lo, x.hi) for x in dd) + ' |')
        L.append('')
    L += ['### X6 per false title, R(L48) / R(L52), group all', '', '| role | ' + ' | '.join(have) + ' |', '|---|' + '---|' * len(have)]
    for role in ROLES:
        L.append(f'| {role} | ' + ' | '.join('--' if pd.isna(x6(role, 'all', t, 48).R) else f'{x6(role, "all", t, 48).R:.3f} / {x6(role, "all", t, 52).R:.3f}' for t in have) + ' |')
    L += ['', '## X7: knockout on true (T), false_0 (F) runs, S = T - F (95% team CI)', '']
    for g in GROUPS:
        L += [f'### {g}', '', '| role | ' + ' | '.join(f'S from L{l}' for l in KL7) + ' | T(L0) | F(L0) | S(L52) role - ALL |', '|---|' + '---|' * (len(KL7) + 3)]
        for role in ROLES:
            c = [x7(role, g, l) for l in KL7]; z = x7(role, g, 0); s52 = x7(role, g, 52)
            dd = '' if role == 'ALL' or pd.isna(s52.get('S_minus_ALL', np.nan)) else fm(s52.S_minus_ALL, s52.S_minus_ALL_lo, s52.S_minus_ALL_hi)
            L.append(f'| {role} | ' + ' | '.join(fm(x.get('S'), x.get('S_lo'), x.get('S_hi')) for x in c) + f' | {fm(z.get("T"), z.get("T_lo"), z.get("T_hi"))} | {fm(z.get("F"), z.get("F_lo"), z.get("F_hi"))} | {dd} |')
        L.append('')
    # verdicts
    L += ['## Pre-registered verdicts (addendum 3) within each role', '',
          'X6 holds if average R(L48) in [0.70, 0.95], average R(L52) >= 0.95, and each false title has |R(L48) - R_false_0(L48)| <= 0.10 and R(L52) >= 0.90. X7 holds if S(L52) <= 0.05 and S(L0) >= 0.5.', '',
          '| role | group | X6 avg R48 / R52 | X6 max |R48 - false_0| / min R52 | X6 | X7 S(L52) / S(L0) | X7 |', '|---|---|---|---|---|---|---|']
    V = {}
    for role in ROLES:
        for g in GROUPS:
            a48, a52 = x6(role, g, 'average', 48), x6(role, g, 'average', 52)
            if not a48.reportable: v6 = 'not reported (gap)'; s6 = s6b = '--'
            else:
                r0 = x6(role, g, 'false_0', 48).R; dev = max(abs(x6(role, g, t, 48).R - r0) for t in have); mn = min(x6(role, g, t, 52).R for t in have)
                v6 = 'HOLDS' if (0.70 <= a48.R <= 0.95 and a52.R >= 0.95 and dev <= 0.10 and mn >= 0.90 and len(have) == 5) else 'DOES NOT HOLD'
                if v6 != 'HOLDS':
                    why = [w for w, c in (('avg R48 < 0.70', a48.R < 0.70), ('avg R48 > 0.95', a48.R > 0.95), ('avg R52 < 0.95', a52.R < 0.95), ('title spread at L48 > 0.10', dev > 0.10), ('a title R52 < 0.90', mn < 0.90)) if c]
                    v6 += ' (' + ', '.join(why) + ')'
                s6, s6b = f'{a48.R:.3f} / {a52.R:.3f}', f'{dev:.3f} / {mn:.3f}'
            z, s52 = x7(role, g, 0), x7(role, g, 52)
            if not z.reportable: v7 = 'not reported (gap)'; s7 = '--'
            else:
                v7 = 'HOLDS' if (s52.S <= 0.05 and z.S >= 0.5) else 'DOES NOT HOLD'; s7 = f'{s52.S:+.3f} / {z.S:+.3f}'
            V[f'{role}|{g}'] = dict(X6=v6, X7=v7)
            L.append(f'| {role} | {g} | {s6} | {s6b} | {v6} | {s7} | {v7} |')
    L += ['', '## Short conclusion', '', '(filled in by hand after the full run; see PROGRESS.md)']
    (REP / 'x6x7_roles.md').write_text('\n'.join(L) + '\n'); json.dump(dict(verdicts=V, warn=warn), open(REP / 'x6x7_roles_verdict.json', 'w'), indent=1)
    print('\n'.join(L)); print('\nX6X7 ROLES DONE')


if __name__ == '__main__':
    main()
