"""Batch 2, addendum 12 items 2-7 and 2-9: analysis of stage13_b2_ps_gpu.py (CPU).

Plan (locked): 381_stage13/config/prereg_addendum12.json, items 2-7 and 2-9; X4 statistics unchanged (stage13_x1x4_analyze.x4 and
stage13_x4_rolesplit.py, re-implemented line for line here because those scripts write the published files / run at import).
  2-7  D(answer, src, layer) = mean over papers of score(self source) - score(partner source); paper score = mean over answer
       tokens (= published pscope value); src = title (published), colon (published ':'), name_all (mean over the paper's
       name-predicting sources), name_<role> (sources predicting a token of that role: initial_first, given_first, given_cont,
       surname_first, surname_cont), name_first_author / name_other_authors. tune / test / all; 95% team-cluster bootstrap
       (pairs.parquet team, 2,000 draws, seed 202, as X4); earliest layer with D > 0 on tune confirmed on test; recognition =
       target - control within citation bin (seed 303 + l, >= 10 per cell, as X4). Text baseline (X4 v2,
       summary_x1x4/x4_textbase2_perpaper.csv) shown beside the author rows (it does not depend on the source position).
  2-9  x4tok: first-author target per token role (given_first, initial_first, surname_first, all) at every PS layer for the
       title, ':' and name_all sources; D per paper = mean nlr(self) - mean nlr(partner) over the role's tokens; team-cluster
       bootstrap on x4_textbase2_perpaper team ids (2,000, seed 47), mean / sd, win share (as stage13_x4_rolesplit.py).
HARD CHECKS (exit 3 on failure):
  2-7  the title-source D of this code reproduces the published summary_x1x4/x4_decodability.csv for every split x answer x layer
       (|D diff| <= 0.005), in particular test / first author / L8 = +0.046.          (colon rows: compared, WARN only)
  2-9  x4tok L8 and L40 (title source) reproduce summary_x1x4/x4_rolesplit.csv (qwen rows, mean, |diff| <= 0.005, same n).
  --partial (one-shard gate): the same comparisons restricted to the finished shards, against the published raw files
       (raw/pscope per-paper values, followup/x4tok2 b7 per token) on the same papers: shard-level D and role means |diff| <= 0.005.
Outputs: summary_b2_ps/{ps_D.csv, ps_earliest.csv, ps_recognition.csv, x4tok_layers.csv, hardcheck.json}, reports/b2_ps_report.md.
Usage: stage13_b2_ps_analyze.py [--partial] | --tiny (reads the tiny raw dir written by stage13_b2_ps_gpu.py --tiny; reference =
       the frozen x1x4 analysis code run on the frozen do_pscope / x4tok outputs of the same tiny model)
"""
import argparse, importlib.util, json, sys, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum12.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols'); CK = load(H / '13_stage13/stage13_b2A_checks.py', 'b2A_checks')
ROLES = ['initial_first', 'given_first', 'given_cont', 'surname_first', 'surname_cont']


def team_w(teams, seed):
    codes, uniq = pd.factorize(pd.Series(teams))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi): return '-' if e is None or np.isnan(e) else f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')


def strat_diff_team(df, col, teams, seed, min_n=10):
    df = df.reset_index(drop=True); cells = []
    for _, ss in df.groupby('citation_bin'):
        ia, ib = ss.index[ss.group == 'target'].to_numpy(), ss.index[ss.group == 'control'].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan, 0
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum(); x = df[col].to_numpy(float); W = team_w(teams, seed)
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (a, b) in zip(w, cells):
        bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
    return est, *ci(bt), len(cells)


def load_tokens(raw):
    fs = sorted(raw.glob('shard_*.parquet')); fs = [f for f in fs if '.tmp' not in f.name]
    T = pd.concat([pd.read_parquet(f).assign(shard=int(f.stem.split('_')[1])) for f in fs], ignore_index=True)
    N = pd.concat([pd.read_parquet(raw / f'none_{int(f.stem.split("_")[1]):03d}.parquet') for f in fs], ignore_index=True)
    return T, N, [int(f.stem.split('_')[1]) for f in fs]


def paper_values(T, N):
    """wide per-paper table, columns '<target>@<who>@<src>@<layer>' (published naming for title / colon) and '<target>@none';
    papers in shard order, first appearance (= the published load_dir order)."""
    order = pd.unique(T.sort_values('shard', kind='stable').paper_id)
    g = T.groupby(['paper_id', 'src_kind', 'src_author', 'src_j', 'src_role', 'who', 'target', 'layer'], sort=False).nlr.mean().reset_index()
    parts = [g[g.src_kind == 'title'].assign(src='title'), g[g.src_kind == 'colon'].assign(src='colon')]
    nm = g[g.src_kind == 'name']
    parts += [nm.assign(src='name_all'), nm[nm.src_author == 0].assign(src='name_first_author'), nm[nm.src_author > 0].assign(src='name_other_authors')]
    parts += [nm[nm.src_role == r].assign(src=f'name_{r}') for r in ROLES]
    a = pd.concat(parts).groupby(['paper_id', 'target', 'who', 'src', 'layer']).nlr.mean()
    W = a.unstack(['target', 'who', 'src', 'layer']); W.columns = [f'{t}@{w}@{s}@{l}' for t, w, s, l in W.columns]
    nn = N.groupby(['paper_id', 'target']).nlr.mean().unstack('target'); nn.columns = [f'{c}@none' for c in nn.columns]
    return W.join(nn).loc[order].reset_index().rename(columns={'index': 'paper_id'})


def srcs_of(df):
    return [s for s in ['title', 'colon', 'name_all', 'name_first_author', 'name_other_authors'] + [f'name_{r}' for r in ROLES]
            if any(c.split('@')[2:3] == [s] for c in df.columns if c.count('@') == 3)]


def d_table(df, layers):
    rows = []
    for part in ('tune', 'test', 'all'):
        s = df if part == 'all' else df[df.split == part]
        if not len(s): continue
        for a in K.PS_TARGETS:
            for src in srcs_of(df):
                for l in layers:
                    cs, cp = f'{a}@self@{src}@{l}', f'{a}@partner@{src}@{l}'
                    if cs not in s: continue
                    ss = s.dropna(subset=[cs, cp])
                    if not len(ss): continue
                    W = team_w(ss.team, 202)
                    v = (ss[cs] - ss[cp]).to_numpy(); b = (W @ v) / W.sum(1)
                    rows.append(dict(split=part, answer=a, src=src, layer=l, n=len(ss), D=v.mean(), lo=ci(b)[0], hi=ci(b)[1],
                                     self=ss[cs].mean(), partner=ss[cp].mean(), none=ss[f'{a}@none'].mean()))
    return pd.DataFrame(rows, columns=K.PS_D_COLS)


def earliest(D):
    out = []
    for (a, src), g in D.groupby(['answer', 'src']):
        t = g[(g.split == 'tune') & (g.lo > 0)]; l0 = int(t.layer.min()) if len(t) else None
        te = g[(g.split == 'test') & (g.layer == l0)] if l0 is not None else g.iloc[:0]
        out.append(dict(answer=a, src=src, earliest_tune=l0, confirmed_on_test=bool(len(te) and te.lo.iloc[0] > 0),
                        D_test=float(te.D.iloc[0]) if len(te) else np.nan, lo_test=float(te.lo.iloc[0]) if len(te) else np.nan, hi_test=float(te.hi.iloc[0]) if len(te) else np.nan))
    return pd.DataFrame(out)


def recognition(df, layers):
    rec = []
    for a in ('year', 'author'):
        for src in srcs_of(df):
            for l in layers:
                cs, cp = f'{a}@self@{src}@{l}', f'{a}@partner@{src}@{l}'
                if cs not in df: continue
                s = df.dropna(subset=[cs, cp]).assign(v=lambda x: x[cs] - x[cp])
                if not len(s): continue
                e, lo, hi, nc = strat_diff_team(s[['v', 'group', 'citation_bin']], 'v', s.team.to_numpy(), 303 + l)
                rec.append(dict(answer=a, src=src, layer=l, target_minus_control=e, lo=lo, hi=hi, n_bins=nc))
    return pd.DataFrame(rec)


def x4tok(T, ps, layers, srcs=('title', 'colon', 'name_all')):
    """stage13_x4_rolesplit.py logic (one W for all calls: x4_textbase2_perpaper teams, seed 47) for every layer and source."""
    codes, u = pd.factorize(ps.team); W = np.random.default_rng(47).multinomial(len(u), np.full(len(u), 1 / len(u)), size=2000).astype(float)[:, codes]
    idx = {p: i for i, p in enumerate(ps.index)}; rows = []
    A = T[T.target == 'author']
    for src in srcs:
        S = A[A.src_kind == src] if src != 'name_all' else A[A.src_kind == 'name']
        if src == 'name_all':                                   # mean over name sources first (per paper, who, layer, token), then as below
            S = S.groupby(['paper_id', 'who', 'layer', 'ans_j', 'ans_role'], as_index=False).nlr.mean()
        for L in layers:
            t = S[S.layer == L]
            for role in K.X4TOK_ROLES:
                tt = t if role == 'all' else t[t.ans_role == role]
                if not len(tt): continue
                m = tt.groupby(['paper_id', 'who']).nlr.mean().unstack(); s = (m['self'] - m['partner']).dropna()
                s = s[s.index.isin(idx)]
                if not len(s): continue
                w = W[:, [idx[p] for p in s.index]]; x = s.to_numpy(); b = (w @ x) / w.sum(1)
                rows.append(dict(measure='qwen', src=src, layer=L, role=role, n=len(x), mean=x.mean(), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5),
                                 mean_over_sd=x.mean() / x.std() if x.std() > 0 else np.nan, win=np.mean(np.where(x > 0, 1, np.where(x < 0, 0, .5)))))
    return pd.DataFrame(rows, columns=K.X4TOK_COLS)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--partial', action='store_true'); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    root = R13 / 'b2_ps_tiny' if a.tiny else R13
    OUT = root / 'summary_b2_ps'; OUT.mkdir(parents=True, exist_ok=True); REP = root / 'reports' / ('b2_ps_partial_check.md' if a.partial else 'b2_ps_report.md'); REP.parent.mkdir(parents=True, exist_ok=True)
    raw = Path((OUT / 'tiny_raw_dir.txt').read_text().strip()) if a.tiny else R13 / 'raw/b2_pscope'
    layers = [0, 1] if a.tiny else K.PS_LAYERS
    T, N, shards = load_tokens(raw)
    if not a.tiny and not a.partial and len(shards) != 24: raise SystemExit(f'{len(shards)}/24 shards; use --partial for the gate')
    pairs = pd.read_parquet(R13 / 'config/pairs.parquet')
    cbin = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'citation_bin'])
    df = paper_values(T, N).merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id').merge(cbin, on='paper_id', how='left')
    ps = pd.read_csv(R13 / 'summary_x1x4/x4_textbase2_perpaper.csv').set_index('paper_id')
    D = d_table(df, layers); D.to_csv(OUT / ('ps_D_partial.csv' if a.partial else 'ps_D.csv'), index=False)
    XT = x4tok(T, ps, layers); XT.to_csv(OUT / ('x4tok_layers_partial.csv' if a.partial else 'x4tok_layers.csv'), index=False)
    L = ['# Addendum 12 items 2-7 / 2-9: patchscope with the source at the name positions; x4tok at every layer', '',
         ('**TINY TEST (random 2-layer model, 3 papers): numbers are meaningless; code path only.**\n' if a.tiny else '') +
         ('**ONE-SHARD GATE (--partial): shards ' + ', '.join(map(str, shards)) + '.**\n' if a.partial else '') +
         f'Plan `381_stage13/config/prereg_addendum12.json` (sha256 {PLAN_SHA[:8]}...). Papers: {df.paper_id.nunique()} (tune {int((df.split == "tune").sum())}, test {int((df.split == "test").sum())}). '
         'D = mean score(self source) - mean score(partner source), log10(1/rank) of the answer tokens at the output; 95% team-cluster bootstrap; * = CI excludes 0.', '']
    # ------------------------------------------------ hard checks
    parts = []
    if a.tiny:
        ref_root = Path(str(raw).replace('raw/b2_pscope_', 'ref_'))
        xa = load(H / '13_stage13/stage13_x1x4_analyze.py', 'x1x4'); xa.ROOT = ref_root; xa.OUT = ref_root / 'summary_x1x4'; xa.PL = layers; xa.OUT.mkdir(parents=True, exist_ok=True)
        xa.x4(pairs, cbin, []); pubD = pd.read_csv(xa.OUT / 'x4_decodability.csv')
        x4ref = pd.read_csv(ref_root / 'x4tok_b7.csv')
        R4 = x4ref.rename(columns={'source': 'who', 'token_j': 'ans_j', 'role': 'ans_role'}).assign(target='author', src_kind='title')
        pubR = x4tok(R4, ps, layers, srcs=('title',)); pubR = pubR[pubR.layer.isin(layers)]
        hl = layers
    elif a.partial:
        zs = [np.load(R13 / f'raw/pscope/shard_{k:03d}.npz') for k in shards]
        ref = pd.concat([pd.DataFrame({c: z[c] for c in z.files if c != 'meta'}) for z in zs]).merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id')
        ref = ref[ref.paper_id.isin(set(df.paper_id))]
        pubD = d_table(ref.merge(cbin, on='paper_id', how='left'), layers).rename(columns={'src': 'pos'})
        x4o = pd.concat([pd.read_csv(R13 / f'followup/x4tok2/shard_{k:03d}.csv') for k in shards]); x4o = x4o[x4o.batch == 'b7']
        R4 = x4o.rename(columns={'source': 'who', 'token_j': 'ans_j', 'role': 'ans_role'}).assign(target='author', src_kind='title')
        pubR = x4tok(R4, ps, K.X4TOK_HARD_LAYERS, srcs=('title',)); hl = K.X4TOK_HARD_LAYERS
        # per-paper exactness (info)
        m = df.set_index('paper_id'); rr = ref.set_index('paper_id'); cols = [c for c in rr.columns if c.count('@') == 3 or c.endswith('@none')]
        dd = np.abs(m.loc[rr.index, cols].to_numpy(float) - rr[cols].to_numpy(float))
        L.append(f'- Per-paper published raw/pscope values (title + colon + none, {dd.size} cells): max |diff| {np.nanmax(dd):.2e}, exact share {(dd < 1e-12).mean():.4f}.')
    else:
        pubD = pd.read_csv(R13 / 'summary_x1x4/x4_decodability.csv')
        pubR = pd.read_csv(R13 / 'summary_x1x4/x4_rolesplit.csv'); pubR = pubR[pubR.measure == 'qwen'].assign(src='title'); pubR['layer'] = pubR.layer.astype(int); hl = K.X4TOK_HARD_LAYERS
    newD = D.rename(columns={'src': 'pos'})
    for pos, hard in (('title', True), ('colon', False)):
        c = CK.value_table_check(newD[newD.pos == pos], pubD[pubD.pos == pos], ['split', 'answer', 'pos', 'layer'], 'D', K.PS_HARD_TOL, f'2-7_D_{pos}')
        c['hard'] = hard; parts.append(c)
        L.append(f'- {"HARD" if hard else "WARN-only"} 2-7 {pos}-source D vs published ({c["n"]} cells): max |diff| {c["max_abs_diff"]:.2e} (tol {K.PS_HARD_TOL}) -> {c["status"]}.')
    if not a.tiny:
        r = K.PS_HARD_REF; row = newD[(newD.split == r['split']) & (newD.answer == r['answer']) & (newD.pos == r['pos']) & (newD.layer == r['layer'])]
        refv = r['D'] if not a.partial else pubD[(pubD.split == r['split']) & (pubD.answer == r['answer']) & (pubD.pos == r['pos']) & (pubD.layer == r['layer'])].D
        refv = float(refv) if np.ndim(refv) == 0 else (float(refv.iloc[0]) if len(refv) else np.nan)
        if len(row):
            c = CK.scalar_check(float(row.D.iloc[0]), refv, K.PS_HARD_TOL, '2-7_named_test_author_title_L8'); c['hard'] = True; parts.append(c)
            L.append(f'- HARD 2-7 named value (test, first author, title, L8): {c["new"]:+.4f} vs {c["ref"]:+.4f} -> {c["status"]}.')
        elif not a.partial:
            parts.append(dict(check='2-7_named', status='FAIL', reason='row missing', hard=True))
    nx = XT[(XT.src == 'title') & XT.layer.isin(hl)]
    c = CK.value_table_check(nx, pubR[pubR.layer.isin(hl)], ['layer', 'role'], 'mean', K.PS_HARD_TOL, '2-9_x4tok_title'); c['hard'] = True; parts.append(c)
    cn = CK.value_table_check(nx, pubR[pubR.layer.isin(hl)], ['layer', 'role'], 'n', 0, '2-9_x4tok_title_n'); cn['hard'] = True; parts.append(cn)
    L.append(f'- HARD 2-9 x4tok (title source, L{"/L".join(map(str, hl))}) vs published ({c["n"]} cells): max |diff| {c["max_abs_diff"]:.2e} -> {c["status"]}; n equal -> {cn["status"]}.')
    hard = CK.combine(*[p for p in parts if p.get('hard')], name='b2_ps_hard'); hard['warn_parts'] = [p for p in parts if not p.get('hard')]
    hard['partial'] = a.partial; hard['tiny'] = a.tiny; hard['shards'] = shards
    (OUT / ('hardcheck_partial.json' if a.partial else 'hardcheck.json')).write_text(json.dumps(hard, indent=1, default=str))
    L += [f'- Hard checks: **{hard["status"]}**', '']
    # ------------------------------------------------ results (full / tiny)
    if not a.partial:
        E = earliest(D); E.to_csv(OUT / 'ps_earliest.csv', index=False)
        Rc = recognition(df, layers); Rc.to_csv(OUT / 'ps_recognition.csv', index=False)
        L += ['## 2-7: D on test (confirmatory split of X4) by source position', '']
        for a_ in K.PS_TARGETS:
            L += [f'### answer = {a_}', '', '| source | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
            for src in srcs_of(df):
                s = D[(D.split == 'test') & (D.answer == a_) & (D.src == src)].set_index('layer')
                L.append(f'| {src} | ' + ' | '.join(fm(s.loc[l, 'D'], s.loc[l, 'lo'], s.loc[l, 'hi']) if l in s.index else '-' for l in layers) + ' |')
            L.append('')
        L += ['### Earliest layer with D > 0 (tune), confirmed on test', '', '| answer | source | earliest (tune) | D test | confirmed |', '|---|---|---|---|---|']
        for r in E.itertuples():
            L.append(f'| {r.answer} | {r.src} | ' + (f'L{int(r.earliest_tune)} | {fm(r.D_test, r.lo_test, r.hi_test)} | {"yes" if r.confirmed_on_test else "no"}' if pd.notna(r.earliest_tune) else 'none | - | -') + ' |')
        L += ['', '### Recognition: target - control of (self - partner) within citation bin (all papers), first author', '', '| source | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
        for src in srcs_of(df):
            s = Rc[(Rc.answer == 'author') & (Rc.src == src)].set_index('layer')
            L.append(f'| {src} | ' + ' | '.join(fm(s.loc[l, 'target_minus_control'], s.loc[l, 'lo'], s.loc[l, 'hi']) if l in s.index else '-' for l in layers) + ' |')
        # text baseline (X4 v2) beside the author rows
        tb = []
        codes, u = pd.factorize(ps.team); Wt = np.random.default_rng(47).multinomial(len(u), np.full(len(u), 1 / len(u)), size=2000).astype(float)[:, codes]
        for f_ in ('bert', 'tfidf_svd'):
            for role in ('given_first', 'surname_first'):
                s = ps[f'lp_{f_}_{role}'].dropna(); w = Wt[:, ps.index.get_indexer(s.index)]
                b = (w @ s.to_numpy()) / w.sum(1); tb.append(dict(features=f_, role=role, n=len(s), mean=s.mean(), lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5)))
        TB = pd.DataFrame(tb); TB.to_csv(OUT / 'ps_textbaseline.csv', index=False)
        L += ['', '### Text baseline (X4 v2, source-independent; summary_x1x4/x4_textbase2_perpaper.csv)', '', '| features | role | n | log-prob gain |', '|---|---|---|---|']
        L += [f'| {r.features} | {r.role} | {r.n} | {fm(r.mean, r.lo, r.hi)} |' for r in TB.itertuples()]
        L += ['', '## 2-9: x4tok (first author, per token role): D per source and layer (all papers)', '']
        for src in ('title', 'colon', 'name_all'):
            L += [f'### source = {src}', '', '| role | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---' * (len(layers) + 1) + '|']
            for role in K.X4TOK_ROLES:
                s = XT[(XT.src == src) & (XT.role == role)].set_index('layer')
                L.append(f'| {role} | ' + ' | '.join(fm(s.loc[l, 'mean'], s.loc[l, 'lo'], s.loc[l, 'hi']) + f' (n={int(s.loc[l, "n"])})' if l in s.index else '-' for l in layers) + ' |')
            L.append('')
    REP.write_text('\n'.join(L) + '\n'); print('\n'.join(L), flush=True)
    sys.exit(0 if hard['status'] == 'PASS' else 3)


if __name__ == '__main__':
    main()
