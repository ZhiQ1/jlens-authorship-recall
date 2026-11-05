"""Stage 13 V42 (handbook G4): paper-bootstrap intervals beside the team-cluster ones (prereg.json general rule: bootstrap over
papers; addendum 2: team-cluster too, both shown, team primary, list every place where 'interval excludes 0' changes),
for X1, X4, X6, X7 (this script) and M3 (stage13_v42_m3_paperboot.py -> summary_v42/m3_paper_vs_team.csv, merged here),
plus the X4 recognition contrast on the tune / test split (prereg.json general rule: X4 uses the pairs.parquet split; the
existing x4_recognition.csv is all papers only).

Estimators are re-implemented line by line from stage13_x1x4_analyze.py, stage13_x6_analyze.py, stage13_x7_analyze.py
(unchanged definitions, same team seeds 101 / 202 / 303+l / 13 / 17); the team values are compared with the existing CSVs
(WARN only). Paper bootstrap: 2,000 draws, each paper its own cluster (seed = team seed + 5000).
X4 recognition on tune/test: target - control of (self - partner) within citation bin, min_n = 10 per group and bin (as
before); layer chosen on tune = first layer with team interval > 0 (the X4 earliest-layer rule), confirmed on test.
Outputs (new, never overwritten): summary_v42/v42_paper_vs_team.csv, summary_v42/x4_recognition_split.csv,
  reports/v42_paper_vs_team.md.  --test: X1/X4 on 4 shards, X6/X7 on 200 papers, output summary_v42_test/."""
import importlib.util, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; TEST = '--test' in sys.argv
OUT = ROOT / ('summary_v42_test' if TEST else 'summary_v42'); REP = OUT if TEST else ROOT / 'reports'
NB = 2000; XL = [4, 8, 16, 24, 32, 40, 48]; PL = [8, 16, 24, 32, 40, 48, 56]; TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']
ROWS, WARN = [], []


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def ci(b): return np.percentile(b, [2.5, 97.5])
def nlr(r): return -np.log10(np.asarray(r, float))


def cw(clusters, seed):
    codes, uniq = pd.factorize(pd.Series(clusters))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def safe(p):
    p = Path(p)
    if not p.exists(): return p
    q = p.with_name(f'{p.stem}.{time.strftime("%Y%m%d_%H%M%S")}{p.suffix}'); WARN.append(f'{p} exists; wrote {q}'); return q


def add(analysis, split, quantity, layer, est, bt, bp, **kw):
    lt, ht = ci(bt); lp, hp = ci(bp)
    ROWS.append(dict(analysis=analysis, split=split, quantity=quantity, layer=layer, est=est, lo_team=lt, hi_team=ht, lo_paper=lp, hi_paper=hp,
                     width_ratio_paper_over_team=(hp - lp) / (ht - lt) if ht > lt else np.nan, **kw))


def check(name, est, lo, hi, ref):
    """team value vs the existing CSV row (WARN only)"""
    if ref is None: return
    dev = max(abs(est - ref[0]), abs(lo - ref[1]), abs(hi - ref[2]))
    if not dev <= 1e-6 * max(1, abs(ref[0])): WARN.append(f'{name}: team value differs from the existing CSV by {dev:.2e}')


def load_dir(d, n=None):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))[:n]]
    keys = [k for k in zs[0].files if k != 'meta']
    return pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in keys}), len(zs)


def x1(pairs):
    df, _ = load_dir(ROOT / 'raw/xpatch', 4 if TEST else None); df = df.merge(pairs[['paper_id', 'team']], on='paper_id')
    old = pd.read_csv(ROOT / 'summary_x1x4/x1_recovery.csv')
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]
        Wt, Wp = cw(s.team, 101), cw(s.paper_id, 5101); den = (s.clean - s.corrupt).to_numpy(); R = {}
        for src in ('authors', 'year', 'field', 'random_c'):
            for l in XL:
                num = (s[f'{src}@{l}'] - s.corrupt).to_numpy(); R[src, l] = (num.mean() / den.mean(), (Wt @ num) / (Wt @ den), (Wp @ num) / (Wp @ den))
        for l in XL:
            o = old[(old.split == part) & (old.layer == l)]
            for src in ('authors', 'year', 'field', 'random_c'):
                add('X1', part, f'R_{src}', l, R[src, l][0], R[src, l][1], R[src, l][2])
                if not TEST and len(o): check(f'X1 {part} L{l} R_{src}', R[src, l][0], *ci(R[src, l][1]), (o[f'R_{src}'].iloc[0], o[f'R_{src}_lo'].iloc[0], o[f'R_{src}_hi'].iloc[0]))
            for oo in ('year', 'field', 'random_c'):
                e = R['authors', l][0] - R[oo, l][0]; bt = R['authors', l][1] - R[oo, l][1]
                add('X1', part, f'authors_minus_{oo}', l, e, bt, R['authors', l][2] - R[oo, l][2])
                if not TEST and len(o): check(f'X1 {part} L{l} a-{oo}', e, *ci(bt), (o[f'a_minus_{oo}'].iloc[0], o[f'a_minus_{oo}_lo'].iloc[0], o[f'a_minus_{oo}_hi'].iloc[0]))
    log('X1 done')


def strat(df, col, Ws, min_n=10):
    """Stage 10 estimator (stage13_x1x4_analyze.strat_diff_team) with a list of weight matrices"""
    df = df.reset_index(drop=True); cells = []
    for _, ss in df.groupby('citation_bin'):
        ia, ib = ss.index[ss.group == 'target'].to_numpy(), ss.index[ss.group == 'control'].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, [np.full(NB, np.nan) for _ in Ws], 0
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum(); x = df[col].to_numpy(float)
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); bts = []
    for W in Ws:
        bt = np.zeros(NB)
        for wi, (a, b) in zip(w, cells):
            bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
        bts.append(bt)
    return est, bts, len(cells)


def x4(pairs, cbin):
    df, _ = load_dir(ROOT / 'raw/pscope', 4 if TEST else None)
    df = df.merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id').merge(cbin, on='paper_id', how='left')
    old = pd.read_csv(ROOT / 'summary_x1x4/x4_decodability.csv'); oldr = pd.read_csv(ROOT / 'summary_x1x4/x4_recognition.csv')
    for part in ('tune', 'test', 'all'):
        s = df if part == 'all' else df[df.split == part]; Wt, Wp = cw(s.team, 202), cw(s.paper_id, 5202)
        for a in ('year', 'author', 'field'):
            for pos in ('title', 'colon'):
                for l in PL:
                    v = (s[f'{a}@self@{pos}@{l}'] - s[f'{a}@partner@{pos}@{l}']).to_numpy(); bt = (Wt @ v) / Wt.sum(1)
                    add('X4 D', part, f'D_{a}_{pos}', l, v.mean(), bt, (Wp @ v) / Wp.sum(1))
                    o = old[(old.split == part) & (old.answer == a) & (old.pos == pos) & (old.layer == l)]
                    if not TEST and len(o): check(f'X4 D {part} {a} {pos} L{l}', v.mean(), *ci(bt), (o.D.iloc[0], o.lo.iloc[0], o.hi.iloc[0]))
    rec = []
    for part in ('all', 'tune', 'test'):
        s0 = df if part == 'all' else df[df.split == part]
        for a in ('year', 'author'):
            for pos in ('title', 'colon'):
                for l in PL:
                    s = s0.assign(v=s0[f'{a}@self@{pos}@{l}'] - s0[f'{a}@partner@{pos}@{l}'])
                    seed = 303 + l if part == 'all' else (404 + l if part == 'tune' else 505 + l)
                    e, (bt, bp), nc = strat(s[['v', 'group', 'citation_bin']], 'v', [cw(s.team.to_numpy(), seed), cw(s.paper_id.to_numpy(), seed + 5000)])
                    add('X4 recognition', part, f'tc_{a}_{pos}', l, e, bt, bp, n_bins=nc, n=len(s))
                    lt, ht = ci(bt); lp, hp = ci(bp)
                    rec.append(dict(split=part, answer=a, pos=pos, layer=l, n=len(s), n_bins=nc, target_minus_control=e, lo_team=lt, hi_team=ht, lo_paper=lp, hi_paper=hp))
                    o = oldr[(oldr.answer == a) & (oldr.pos == pos) & (oldr.layer == l)]
                    if part == 'all' and not TEST and len(o): check(f'X4 recognition all {a} {pos} L{l}', e, lt, ht, (o.target_minus_control.iloc[0], o.lo.iloc[0], o.hi.iloc[0]))
    Rc = pd.DataFrame(rec); E = []
    for a in ('year', 'author'):
        for pos in ('title', 'colon'):
            t = Rc[(Rc.split == 'tune') & (Rc.answer == a) & (Rc.pos == pos) & (Rc.lo_team > 0)]; l0 = int(t.layer.min()) if len(t) else None
            te = Rc[(Rc.split == 'test') & (Rc.answer == a) & (Rc.pos == pos) & (Rc.layer == l0)] if l0 else None
            E.append(dict(answer=a, pos=pos, layer_tune=l0, test_est=te.target_minus_control.iloc[0] if l0 else np.nan,
                          test_lo_team=te.lo_team.iloc[0] if l0 else np.nan, test_hi_team=te.hi_team.iloc[0] if l0 else np.nan,
                          test_lo_paper=te.lo_paper.iloc[0] if l0 else np.nan, test_hi_paper=te.hi_paper.iloc[0] if l0 else np.nan,
                          confirmed_team=bool(l0 and te.lo_team.iloc[0] > 0), confirmed_paper=bool(l0 and te.lo_paper.iloc[0] > 0)))
    log('X4 done'); return Rc, pd.DataFrame(E)


def x6(team_of, grp):
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    src = {'false_0': R11 / 'raw/patch'} | {t: ROOT / 'raw/xf_patch' / t for t in TITLES[1:]}; pp, layers = {}, None
    for t, d in src.items():
        zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]; dd = {k: np.concatenate([z[k] for z in zs]) for k in ('row_id', 'rank_true', 'rank_false', 'rank_patch')}
        ly = [int(x) for x in zs[0]['layers']]; layers = layers or ly
        df = pd.DataFrame({'paper_id': toks.loc[dd['row_id']].paper_id.to_numpy(), 'true': nlr(dd['rank_true']), 'false': nlr(dd['rank_false'])})
        for i, l in enumerate(ly): df[f'p{l}'] = nlr(dd['rank_patch'][:, i])
        pp[t] = df.groupby('paper_id').mean()
    allp = sorted(set().union(*[set(pp[t].index) for t in TITLES]))
    if TEST: allp = allp[:200]; pp = {t: v.loc[v.index.intersection(allp)] for t, v in pp.items()}
    codes, uniq = pd.factorize(pd.Series([team_of[p] for p in allp]))
    Wt = pd.DataFrame(np.random.default_rng(13).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(np.float64)[:, codes].T, index=allp)
    Wp = pd.DataFrame(cw(np.array(allp), 5013).T, index=allp)
    old = pd.read_csv(ROOT / 'summary_x6/x6_recovery.csv')
    for g in ('target', 'control', 'all'):
        bt_, bp_, est_ = {}, {}, {}
        for t in TITLES:
            s = pp[t] if g == 'all' else pp[t][grp.reindex(pp[t].index).to_numpy() == g]
            wt, wp = Wt.loc[s.index].to_numpy(), Wp.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy()
            for l in layers:
                num = (s[f'p{l}'] - s['false']).to_numpy(); est_[t, l] = num.mean() / den.mean()
                bt_[t, l] = (num @ wt) / (den @ wt); bp_[t, l] = (num @ wp) / (den @ wp)
        for l in layers:
            for t in TITLES: add('X6', g, f'R_{t}', l, est_[t, l], bt_[t, l], bp_[t, l])
            e = np.mean([est_[t, l] for t in TITLES]); bt = np.mean([bt_[t, l] for t in TITLES], 0)
            add('X6', g, 'R_average', l, e, bt, np.mean([bp_[t, l] for t in TITLES], 0))
            o = old[(old.group == g) & (old.false_title == 'average') & (old.layer == l)]
            if not TEST and len(o): check(f'X6 {g} average L{l}', e, *ci(bt), (o.R.iloc[0], o.lo.iloc[0], o.hi.iloc[0]))
    log('X6 done')


def x7(team_of, grp):
    def ld(d, keys):
        zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
        return {k: np.concatenate([z[k] for z in zs]) for k in keys}, [int(x) for x in zs[0]['layers']]
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    d, _ = ld(R11 / 'raw/patch', ['row_id', 'rank_true', 'rank_false']); kT, kl = ld(R11 / 'raw/knockout', ['row_id', 'rank_ko']); kF, _ = ld(ROOT / 'raw/ko_false/false_0', ['row_id', 'rank_ko'])
    base = pd.DataFrame({'row_id': d['row_id'], 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])})
    t = pd.DataFrame({'row_id': kT['row_id'], **{f'T{l}': nlr(kT['rank_ko'][:, i]) for i, l in enumerate(kl)}})
    f = pd.DataFrame({'row_id': kF['row_id'], **{f'F{l}': nlr(kF['rank_ko'][:, i]) for i, l in enumerate(kl)}})
    m = base.merge(t, on='row_id').merge(f, on='row_id'); m['paper_id'] = toks.loc[m.row_id].paper_id.to_numpy()
    pp = m.drop(columns=['row_id']).groupby('paper_id').mean()
    if TEST: pp = pp.iloc[:200]
    allp = list(pp.index); codes, uniq = pd.factorize(pd.Series([team_of[p] for p in allp]))
    Wt = pd.DataFrame(np.random.default_rng(17).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes].T, index=allp)
    Wp = pd.DataFrame(cw(np.array(allp), 5017).T, index=allp); old = pd.read_csv(ROOT / 'summary_x7/x7_knockout.csv')
    for g in ('target', 'control', 'all'):
        s = pp if g == 'all' else pp[grp.reindex(pp.index).to_numpy() == g]; den = (s['true'] - s['false']).to_numpy()
        wt, wp = Wt.loc[s.index].to_numpy(), Wp.loc[s.index].to_numpy()
        for l in kl:
            if l == 64: continue
            nt = (s['T64'] - s[f'T{l}']).to_numpy(); nf = (s['F64'] - s[f'F{l}']).to_numpy()
            B_ = {tag: ((nt @ w) / (den @ w), (nf @ w) / (den @ w)) for tag, w in (('team', wt), ('paper', wp))}
            Te, Fe = nt.mean() / den.mean(), nf.mean() / den.mean()
            add('X7', g, 'T', l, Te, B_['team'][0], B_['paper'][0]); add('X7', g, 'F', l, Fe, B_['team'][1], B_['paper'][1])
            add('X7', g, 'S', l, Te - Fe, B_['team'][0] - B_['team'][1], B_['paper'][0] - B_['paper'][1])
            o = old[(old.group == g) & (old.start_layer == l)]
            if not TEST and len(o): check(f'X7 {g} S L{l}', Te - Fe, *ci(B_['team'][0] - B_['team'][1]), (o.S.iloc[0], o.S_lo.iloc[0], o.S_hi.iloc[0]))
    log('X7 done')


def fm(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet'); papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    cbin = papers[['paper_id', 'citation_bin']]
    _, team = c13.group_folds(papers.paper_id.to_numpy()); team_of = dict(zip(papers.paper_id, team))
    grp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].set_index('paper_id').group
    for name, fn in (('X1', lambda: x1(pairs)), ('X4', lambda: x4(pairs, cbin)), ('X6', lambda: x6(team_of, grp)), ('X7', lambda: x7(team_of, grp))):
        try:
            r = fn()
            if name == 'X4': Rc, E = r
        except Exception:
            import traceback; traceback.print_exc(); WARN.append(f'{name} FAILED (see log)')
    m3p = ROOT / ('summary_v42_test' if TEST else 'summary_v42') / 'm3_paper_vs_team.csv'
    if m3p.exists():
        M = pd.read_csv(m3p)
        for r in M.itertuples():
            lt, ht, lp, hp = r.lo_team, r.hi_team, r.lo_paper, r.hi_paper
            ROWS.append(dict(analysis='M3', split=r.pos, quantity=r.measure, layer=r.layer, est=r.est, lo_team=lt, hi_team=ht, lo_paper=lp, hi_paper=hp,
                             width_ratio_paper_over_team=(hp - lp) / (ht - lt) if ht > lt else np.nan))
        if isinstance(M.warn.iloc[0], str) and M.warn.iloc[0]: WARN.append('M3 parity: ' + M.warn.iloc[0][:500])
    else: WARN.append(f'M3 paper-bootstrap file missing ({m3p}); M3 rows not included')
    rp = ROOT / 'summary_x5/x5_retrieval.csv'
    if rp.exists() and not TEST:
        Rt = pd.read_csv(rp)
        for r in Rt.itertuples():
            for q, e, a, b, c, d in (('top1', r.top1, r.top1_lo_team, r.top1_hi_team, r.top1_lo_paper, r.top1_hi_paper),
                                     ('top1_minus_L4', r.top1_minus_L4, r.dL4_lo_team, r.dL4_hi_team, r.dL4_lo_paper, r.dL4_hi_paper)):
                ROWS.append(dict(analysis='M3 retrieval (V56)', split=f'{r.set}/{r.pos}', quantity=q, layer=r.layer, est=e, lo_team=a, hi_team=b, lo_paper=c, hi_paper=d,
                                 width_ratio_paper_over_team=(d - c) / (b - a) if b > a else np.nan))
    D = pd.DataFrame(ROWS)
    D['excl0_team'] = np.sign(D.lo_team).where(D.lo_team > 0, -1 * (D.hi_team < 0)).astype(int)     # +1 above 0, -1 below 0, 0 includes 0
    D['excl0_paper'] = np.sign(D.lo_paper).where(D.lo_paper > 0, -1 * (D.hi_paper < 0)).astype(int)
    D['changes'] = D.excl0_team != D.excl0_paper
    p_csv = safe(OUT / 'v42_paper_vs_team.csv'); D.to_csv(p_csv, index=False)
    p_rc = safe(OUT / 'x4_recognition_split.csv'); Rc.to_csv(p_rc, index=False)
    lab = {1: '> 0', -1: '< 0', 0: 'includes 0'}
    L = ['# Stage 13 V42: paper-bootstrap vs team-cluster intervals (X1, X4, X6, X7, M3) and X4 recognition on tune / test', '',
         f'Scripts `~/jlens_work/13_stage13/stage13_v42_paper_vs_team.py` and `stage13_v42_m3_paperboot.py`, run {time.strftime("%Y-%m-%d %H:%M")}' + (' **TEST RUN**' if TEST else '') + '. CPU only, existing raw outputs.',
         'Rules: prereg.json general rule (95% bootstrap over papers, 2,000 draws) and addendum 2 (team-cluster bootstrap too; both shown; team is primary; list every place where "interval excludes 0" changes). Estimators and team seeds unchanged from the original analysis scripts; the paper bootstrap treats each paper as its own cluster.',
         f'Combined table: `{p_csv}` ({len(D)} rows: analysis, split / group / position, quantity, layer, estimate, team CI, paper CI, width ratio paper/team, excludes-0 flags). X4 recognition by split: `{p_rc}`.', '']
    L += ['## 1. Width of the intervals (paper CI width / team CI width)', '', '| analysis | rows | median ratio | min | max | rows where "excludes 0" changes |', '|---|---|---|---|---|---|']
    for a, g in D.groupby('analysis', sort=False):
        w = g.width_ratio_paper_over_team.dropna()
        L.append(f'| {a} | {len(g)} | {w.median():.2f} | {w.min():.2f} | {w.max():.2f} | {int(g.changes.sum())} |')
    L += ['', 'Team intervals are wider than paper intervals when papers of one author team are correlated (ratio < 1); a ratio near 1 means team clustering hardly matters.', '',
          '## 2. Every place where "interval excludes 0" changes (team is primary)', '']
    ch = D[D.changes]
    if ch.empty: L.append('None.')
    else:
        L += ['| analysis | split / group / pos | quantity | layer | estimate | team CI | paper CI | team | paper |', '|---|---|---|---|---|---|---|---|---|']
        for r in ch.itertuples():
            L.append(f'| {r.analysis} | {r.split} | {r.quantity} | L{r.layer} | {r.est:+.4f} | [{r.lo_team:+.4f}, {r.hi_team:+.4f}] | [{r.lo_paper:+.4f}, {r.hi_paper:+.4f}] | {lab[r.excl0_team]} | {lab[r.excl0_paper]} |')
    L += ['', '## 3. X4 recognition on the tune / test split (target - control of self - partner, within citation bin; min_n = 10)', '',
          'Prereg X4: "D_year and D_author larger for target than control within citation bin (interval excludes 0)"; prereg general rule: layer chosen on tune, confirmatory number on test. Layer on tune = first layer with team interval > 0 (the X4 earliest-layer rule; the prereg does not name a layer rule for this contrast, so this choice is the X4 analogue).', '',
          '| answer | pos | layer chosen on tune | test estimate | test team CI | test paper CI | confirmed (team) | confirmed (paper) |', '|---|---|---|---|---|---|---|---|']
    for r in E.itertuples():
        if pd.isna(r.layer_tune): L.append(f'| {r.answer} | {r.pos} | none on tune | - | - | - | - | - |'); continue
        L.append(f'| {r.answer} | {r.pos} | L{int(r.layer_tune)} | {r.test_est:+.4f} | [{r.test_lo_team:+.4f}, {r.test_hi_team:+.4f}] | [{r.test_lo_paper:+.4f}, {r.test_hi_paper:+.4f}] | {"yes" if r.confirmed_team else "no"} | {"yes" if r.confirmed_paper else "no"} |')
    L += ['', '### Every layer', '', '| answer, pos | layer | all (team CI) | tune (team CI) | test (team CI) | test (paper CI) | bins all/tune/test |', '|---|---|---|---|---|---|---|']
    for a in ('year', 'author'):
        for pos in ('title', 'colon'):
            for l in PL:
                f = lambda sp: Rc[(Rc.split == sp) & (Rc.answer == a) & (Rc.pos == pos) & (Rc.layer == l)].iloc[0]
                L.append(f'| {a}, {pos} | L{l} | {fm(f("all").target_minus_control, f("all").lo_team, f("all").hi_team)} | {fm(f("tune").target_minus_control, f("tune").lo_team, f("tune").hi_team)} | '
                         f'{fm(f("test").target_minus_control, f("test").lo_team, f("test").hi_team)} | {fm(f("test").target_minus_control, f("test").lo_paper, f("test").hi_paper)} | {f("all").n_bins}/{f("tune").n_bins}/{f("test").n_bins} |')
    L += ['', '## 4. Key rows side by side', '']
    key = [('X1', 'test', 'authors_minus_year', (24, 32, 40, 48)), ('X1', 'test', 'authors_minus_random_c', (24, 48)), ('X4 D', 'test', 'D_author_title', (8, 40, 48)),
           ('X4 D', 'test', 'D_year_title', (8, 40)), ('X6', 'all', 'R_average', (24, 48, 52)), ('X7', 'all', 'S', (0, 48, 52, 54, 56)),
           ('M3', 'title_last', 'I_minus_L4', (8, 24, 40)), ('M3', 'title_last', 'T_year', (16, 24, 40)), ('M3', 'title_last', 'T_year_minus_L4', (16, 24, 40))]
    L += ['| analysis | split | quantity | layer | estimate | team CI | paper CI |', '|---|---|---|---|---|---|---|']
    for a, sp, q, ls in key:
        for l in ls:
            g = D[(D.analysis == a) & (D.split == sp) & (D.quantity == q) & (D.layer == l)]
            if len(g): r = g.iloc[0]; L.append(f'| {a} | {sp} | {q} | L{l} | {r.est:+.4f} | [{r.lo_team:+.4f}, {r.hi_team:+.4f}] | [{r.lo_paper:+.4f}, {r.hi_paper:+.4f}] |')
    L += ['', '## Notes', '', '- Team values reproduce the existing CSVs (x1_recovery, x4_decodability, x4_recognition, x6_recovery average, x7_knockout S, m3_identity / m3_transfer) unless listed under WARN.',
          '- M3 transfer ratios: probes are fitted once (5 group folds) and the held-out predictions are resampled; the paper interval does not include probe refitting variance.',
          '- X4 recognition on tune / test halves each citation bin; bins with < 10 target or < 10 control papers are dropped (n_bins column).',
          '- X6 / X7 group = Stage 11 sample group (target / control); "all" = both.']
    L += ['', '## WARN', ''] + ([f'- {w}' for w in WARN] or ['- none'])
    p_md = safe(REP / 'v42_paper_vs_team.md'); p_md.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nV42 DONE')


if __name__ == '__main__':
    main()
