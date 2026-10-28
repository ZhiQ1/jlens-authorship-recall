"""Stage 10 + Stage 11 — R0 / R1 stratified analysis (2026-10-27, user request; CPU, existing outputs only).

Recall levels from the open answer (label package): R0 = no true author written (m = 0); R1 = some written but HR2 > 0.5.
Behaviour groups of Stages 4-8: A = target R0, B = control R0, C = target R1, D = control R1 (34 papers).
  1. R0 main view: target R0 vs control R0 (A vs B) — Stage 10 title-specific within bin (every readout x layer + output),
     Stage 11 patching (E1, E1t), knockout (E2, E2n) and the title-position probe (E4b).
  2. C vs A: target R1 vs target R0 within citation bin (min 10 per cell), every readout x layer; Stage 11 curves by subgroup.
  3. D (control R1): descriptive means only.
  4. Per author inside R1 papers: the label package stores only the count m of matched authors, not which ones. We rebuild
     the match (surname + first initial, either name order, one-to-one) and keep papers whose rebuilt count equals m;
     then compare the authors the model wrote correctly with the ones it did not, paired within paper.
  5. Three views side by side: R0 (A - B), R1 (C - B; control R1 is too small, so R0 controls are the reference), pooled.
Outputs: 351_stage10/summary_r0r1/, 361_stage11/summary_r0r1/, report 351_stage10/reports/r0_r1_analysis.md.
"""
import importlib.util, re, sys, unicodedata, warnings
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
LAB = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
H = Path.home() / 'jlens_work'
B = 2000; rng = np.random.default_rng(3513)
KEY_LAYERS = [24, 32, 40, 48, 56, 62, 63]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


s10 = load(H / '10_stage10/351_stage10.py', 's10')
sys.path.insert(0, str(H / '11_stage11')); import stage11_analyze as a11


def fmt(v, lo, hi): return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
def fr(r, m): return fmt(r[m + '_diff'], r[m + '_lo'], r[m + '_hi'])


def boot_mean(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    if len(v) == 0: return np.nan, np.nan, np.nan, 0
    mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1); return v.mean(), *np.percentile(mm, [2.5, 97.5]), len(v)


# ---------------------------------------------------------------- per-author match of the open answer
def words(s): return [x for x in re.sub(r'[^a-z \-]', ' ', unicodedata.normalize('NFKD', s.replace('-', ' - ')).encode('ascii', 'ignore').decode().lower()).split() if x != '-']


def same(tw, gw, swap):
    if not tw or len(gw) < 2: return False
    ts, ti = tw[-1], (tw[0][0] if len(tw) > 1 else '')
    for gs, gi in ([(gw[-1], gw[0][0]), (gw[0], gw[1][0])] if swap else [(gw[-1], gw[0][0])]):
        if gs == ts and (not ti or gi == ti): return True
    return False


def match(true, gen):
    """One-to-one: first pass given-name-first order, second pass surname-first order ("Sakaguchi Shimon", "Tounsi A")."""
    tw = [words(t) for t in true]; gw = [words(g) for g in gen]; used, hit = set(), [False] * len(true)
    for swap in (False, True):
        for i, t in enumerate(tw):
            if hit[i]: continue
            for j, g in enumerate(gw):
                if j not in used and same(t, g, swap): used.add(j); hit[i] = True; break
    return hit


# ---------------------------------------------------------------- Stage 10
def stage10(L, S):
    ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet')
    ds['bg'] = ds.group_tight.map({'target': 'T', 'control': 'C'}).fillna('') + ds.recall_level.map({'R0': '0', 'R1': '1'}).fillna('')
    pp = ds.drop_duplicates('paper_id')
    L += ['## 0. Papers by group and recall level', '', pd.crosstab(pp.group_tight, pp.recall_level).to_string(), '',
          'A = target R0, B = control R0, C = target R1, D = control R1.', '']
    mets = ['spec_mean_nlr', 'spec_mean_nlr_surname_first', 'true_mean_nlr', 'delete_mean_nlr']
    full = s10.stratified_diff(ds, 'group_tight', 'target', 'control', 'citation_bin', mets, rng)
    v0 = s10.stratified_diff(ds[ds.recall_level == 'R0'], 'group_tight', 'target', 'control', 'citation_bin', mets, rng)
    tc = ds[ds.group_tight.isin(['target', 'control'])]
    v1 = s10.stratified_diff(tc[tc.bg.isin(['T1', 'C0'])], 'bg', 'T1', 'C0', 'citation_bin', mets, rng, min_n=10)
    ca = s10.stratified_diff(tc[tc.bg.isin(['T1', 'T0'])], 'bg', 'T1', 'T0', 'citation_bin', mets, rng, min_n=10)
    for n, t in (('tc_pooled', full), ('tc_R0', v0), ('tc_R1target_vs_R0control', v1), ('C_minus_A', ca)): t.to_csv(S / f'{n}.csv', index=False)
    get = lambda t, r, l: t[(t.readout == r) & (t.layer == l)]
    L += ['## 1. Stage 10 title-specific signal, target - control within citation bin: three views', '',
          'R0 view = A - B (bins with >= 30 per group). R1 view = C - B (target R1 vs control R0, >= 10 per cell; control R1 has only 34 papers).',
          'Pooled = target - control as in report section 6.4. Mean over name tokens, log10(1/rank).', '',
          '| readout | layer | R0 view (A - B) | R1 view (C - B) | pooled | n A / B | n C / B |', '|---|---|---|---|---|---|---|']
    for _, r in v0.sort_values(['readout', 'layer']).iterrows():
        f, g = get(full, r.readout, r.layer), get(v1, r.readout, r.layer)
        L.append(f'| {r.readout} | {r.layer} | {fr(r, "spec_mean_nlr")} | {fr(g.iloc[0], "spec_mean_nlr") if len(g) else "-"} | '
                 f'{fr(f.iloc[0], "spec_mean_nlr") if len(f) else "-"} | {r.n_a} / {r.n_b} | {g.n_a.iloc[0] if len(g) else "-"} / {g.n_b.iloc[0] if len(g) else "-"} |')
    L += ['', '## 2. C vs A: target R1 - target R0 within citation bin (>= 10 per cell)', '',
          'title-specific (true - mean of 5 false), surname first token, true title level, no-title level (name prior).', '',
          '| readout | layer | title-specific | surname first token | true title | no title | n C / A |', '|---|---|---|---|---|---|---|']
    for _, r in ca.sort_values(['readout', 'layer']).iterrows():
        L.append(f'| {r.readout} | {r.layer} | {fr(r, "spec_mean_nlr")} | {fr(r, "spec_mean_nlr_surname_first")} | {fr(r, "true_mean_nlr")} | {fr(r, "delete_mean_nlr")} | {r.n_a} / {r.n_b} |')
    # D descriptive: plain means per subgroup (no bin adjustment) + citation profile
    rows = []
    for (bg, r, l), s in tc[tc.bg.isin(['T0', 'C0', 'T1', 'C1'])].groupby(['bg', 'readout', 'layer']):
        m = boot_mean(s.spec_mean_nlr); rows.append(dict(sub=bg, readout=r, layer=l, mean=m[0], lo=m[1], hi=m[2], n=m[3], true=s.true_mean_nlr.mean(), delete=s.delete_mean_nlr.mean()))
    dm = pd.DataFrame(rows); dm.to_csv(S / 'subgroup_means.csv', index=False)
    name = {'T0': 'A target R0', 'C0': 'B control R0', 'T1': 'C target R1', 'C1': 'D control R1'}
    L += ['', '## 3. Descriptive means by subgroup (title-specific, no citation adjustment; D = control R1 is description only)', '',
          '| readout | layer | ' + ' | '.join(name.values()) + ' |', '|---|---|---|---|---|---|']
    for r in ['logit', 'jlens_public', 'final']:
        for l in KEY_LAYERS:
            s = dm[(dm.readout == r) & (dm.layer == l)].set_index('sub')
            if len(s): L.append(f'| {r} | {l} | ' + ' | '.join(fmt(s.loc[k, 'mean'], s.loc[k, 'lo'], s.loc[k, 'hi']) + f' (n={int(s.loc[k, "n"])})' for k in name) + ' |')
    cit = pp[pp.group_tight.isin(['target', 'control'])].assign(bg=lambda x: x.bg.map(name))
    cit['c'] = pd.to_numeric(cit.citations, errors='coerce')
    L += ['', 'Citations by subgroup (median; share in bins >= 1025):', '']
    for k, s in cit.groupby('bg'): L.append(f'- {k}: n = {len(s)}, median citations {s.c.median():.0f}, share >= 1025 citations {(s.c >= 1025).mean():.2f}')
    return ds


# ---------------------------------------------------------------- per author inside R1 papers
def per_author(L, S, ds):
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'names']]
    p = pd.read_parquet(R10 / 'cohort/papers.parquet')[['paper_id', 'authors', 'm', 'recall_level', 'group_tight', 'citation_bin']].merge(o, on='paper_id')
    p['m'] = p.m.astype(int); p['hits'] = [match(a.split('; '), n) for a, n in zip(p.authors, p.names)]; p['mm'] = p.hits.map(sum)
    L += ['', '## 4. Per author inside R1 papers (which authors the open answer got right)', '',
          'The label package stores only m (number of matched authors) per paper, not which authors. Rebuilt match: surname + first initial,',
          'given-name-first then surname-first order, one-to-one. Agreement of the rebuilt count with m:', '']
    for lv in ['R0', 'R1', 'R2']:
        s = p[p.recall_level == lv]; L.append(f'- {lv}: {len(s)} papers, rebuilt count = m for {(s.mm == s.m).mean():.1%} (over {(s.mm > s.m).sum()}, under {(s.mm < s.m).sum()})')
    r1 = p[(p.recall_level == 'R1') & (p.mm == p.m) & p.group_tight.isin(['target', 'control'])]
    au = r1[['paper_id', 'hits', 'group_tight']].explode('hits').assign(author_index=lambda x: x.groupby('paper_id').cumcount()).rename(columns={'hits': 'hit'})
    au['hit'] = au.hit.astype(bool)
    ctx = pd.read_parquet(R10 / 'cohort/contexts.parquet', columns=['paper_id', 'author_index'])
    au = au.merge(ctx, on=['paper_id', 'author_index'])                                                 # scored authors only
    au.to_csv(S / 'R1_author_hits.csv', index=False)
    both = au.groupby('paper_id').hit.agg(['any', 'all']); keep = both[both['any'] & ~both['all']].index
    L += ['', f'R1 target/control papers with a consistent rebuild: {r1.paper_id.nunique()}; scored authors {len(au)} ({au.hit.sum()} written correctly); '
          f'papers with both a correct and a missed scored author: {len(keep)}. Correct authors are first author in {(au[au.hit].author_index == 0).mean():.0%} of cases '
          f'(all authors: {(au.author_index == 0).mean():.0%}).', '']
    # author-level scores under every condition, R1 papers only
    root = R10; m, lenses = s10.verify(root); cm = s10.verify_conditions(root)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index'])
    toks = toks[toks.paper_id.isin(keep)]
    per = {}
    for cond in cm['conditions']:
        raw = s10.load_raw(root, m, lenses, require_complete=True, cond=cond)
        d = raw.merge(toks, on='row_id'); d['nlr'] = -np.log10(d['rank'].astype(float))
        per[cond] = d.groupby(['paper_id', 'author_index', 'readout', 'layer']).nlr.mean(); del raw, d
    fk = [f'false_{k}' for k in range(cm['K'])]
    A = pd.DataFrame({'true': per['true'], 'delete': per['delete'], 'false': pd.concat([per[c] for c in fk], axis=1).mean(1)}).dropna().reset_index()
    A['spec'] = A['true'] - A['false']
    A = A.merge(au[['paper_id', 'author_index', 'hit', 'group_tight']], on=['paper_id', 'author_index'])
    A.to_parquet(S / 'R1_author_scores.parquet', index=False)
    rows = []
    for (r, l), s in A.groupby(['readout', 'layer']):
        for excl_first in (False, True):
            t = s[s.author_index > 0] if excl_first else s
            g = t.groupby(['paper_id', 'hit'])[['spec', 'true', 'delete']].mean().unstack('hit').dropna()
            if g.empty: continue
            row = dict(readout=r, layer=l, excl_first_author=excl_first, n_papers=len(g))
            for mt in ['spec', 'true', 'delete']:
                dv = (g[(mt, True)] - g[(mt, False)]).to_numpy(); e = boot_mean(dv); row |= {f'{mt}_diff': e[0], f'{mt}_lo': e[1], f'{mt}_hi': e[2]}
                row[f'{mt}_hit'] = g[(mt, True)].mean(); row[f'{mt}_miss'] = g[(mt, False)].mean()
            rows.append(row)
    pa = pd.DataFrame(rows); pa.to_csv(S / 'R1_author_written_minus_missed.csv', index=False)
    L += ['Written - missed author, paired within paper (bootstrap over papers). title-specific = true - mean of 5 false titles; no title = name prior.', '',
          '| readout | layer | n papers | title-specific: written / missed | written - missed | true title: written - missed | no title: written - missed | written - missed, first authors dropped |',
          '|---|---|---|---|---|---|---|---|']
    for _, r in pa[~pa.excl_first_author].sort_values(['readout', 'layer']).iterrows():
        x = pa[pa.excl_first_author & (pa.readout == r.readout) & (pa.layer == r.layer)]
        L.append(f'| {r.readout} | {r.layer} | {r.n_papers} | {r.spec_hit:+.3f} / {r.spec_miss:+.3f} | {fr(r, "spec")} | {fr(r, "true")} | {fr(r, "delete")} | '
                 f'{(fr(x.iloc[0], "spec") + f" (n={x.n_papers.iloc[0]})") if len(x) else "-"} |')
    return pa


# ---------------------------------------------------------------- Stage 11
def ratio_ci(num, den):
    if len(num) < 3: return np.nan, np.nan, np.nan, len(num)
    return a11.boot_ratio(num, den)


def stage11(L, S, ds):
    a11.rng = np.random.default_rng(3611)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    rl = ds.drop_duplicates('paper_id').set_index('paper_id').recall_level; smp['recall_level'] = smp.paper_id.map(rl)
    smp['sub'] = smp.group.map({'target': 'T', 'control': 'C'}) + smp.recall_level.str[1]
    L += ['', '## 5. Stage 11 sample by recall level', '', pd.crosstab(smp.group, smp.recall_level).to_string(), '']
    views = {'A target R0': ['T0'], 'C target R1': ['T1'], 'target pooled': ['T0', 'T1'], 'B control R0': ['C0'], 'D control R1': ['C1'], 'control pooled': ['C0', 'C1']}
    d, layers = a11.load_unit_dir(R11 / 'raw/patch')
    def pmean(dd, cols):
        t = toks.set_index('row_id').loc[dd['row_id']].reset_index()
        df = pd.DataFrame({'paper_id': t.paper_id, 'true': a11.nlr(dd['rank_true']), 'false': a11.nlr(dd['rank_false'])})
        for c, arr in cols.items(): df[c] = arr
        return df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    out = []
    for nm, sub, title in (('E1', 'patch', 'patching of the tokens after the title (recovery)'), ('E1t', 'patch_title', 'patching of the last title token (recovery)')):
        dd, ly = (d, layers) if sub == 'patch' else a11.load_unit_dir(R11 / 'raw' / sub)
        pp = pmean(dd, {f'p{l}': a11.nlr(dd['rank_patch'][:, i]) for i, l in enumerate(ly)})
        if nm == 'E1t' and 63 in list(ly): pp['false'] = pp['p63']                                          # same in-batch baseline as stage11_analyze
        L += [f'### {nm}. {title}', '', '| layer | ' + ' | '.join(f'{k} (n={int(smp["sub"].isin(v).sum())})' for k, v in views.items()) + ' |', '|---' * (len(views) + 1) + '|']
        for l in ly:
            if l == 63: continue
            cells = []
            for k, v in views.items():
                s = pp[pp['sub'].isin(v)]; r = ratio_ci((s[f'p{l}'] - s['false']).to_numpy(), (s['true'] - s['false']).to_numpy())
                cells.append(fmt(*r[:3]) if r[3] >= 3 else '-'); out.append(dict(exp=nm, layer=int(l), view=k, value=r[0], lo=r[1], hi=r[2], n=r[3]))
            L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
        L.append('')
    for nm, sub, title in (('E2', 'knockout', 'knockout of all positions after the title (loss)'), ('E2n', 'knockout_name', 'knockout of ":" and the names (loss)')):
        k, kl = a11.load_unit_dir(R11 / 'raw' / sub)
        t = toks.set_index('row_id').loc[k['row_id']].reset_index()
        kd = pd.DataFrame({'row_id': k['row_id'], 'paper_id': t.paper_id})
        for i, l in enumerate(kl): kd[f'k{l}'] = a11.nlr(k['rank_ko'][:, i])
        kd = kd.merge(pd.DataFrame({'row_id': d['row_id'], 'true': a11.nlr(d['rank_true']), 'false': a11.nlr(d['rank_false'])}), on='row_id')
        kp = kd.drop(columns='row_id').groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
        L += [f'### {nm}. {title}', '', '| from layer | ' + ' | '.join(views) + ' |', '|---' * (len(views) + 1) + '|']
        for l in kl:
            if l == 64: continue
            cells = []
            for kk, v in views.items():
                s = kp[kp['sub'].isin(v)]; r = ratio_ci((s['k64'] - s[f'k{l}']).to_numpy(), (s['true'] - s['false']).to_numpy())
                cells.append(fmt(*r[:3]) if r[3] >= 3 else '-'); out.append(dict(exp=nm, layer=int(l), view=kk, value=r[0], lo=r[1], hi=r[2], n=r[3]))
            L.append(f'| L{l} | ' + ' | '.join(cells) + ' |')
        L.append('')
    pd.DataFrame(out).to_csv(S / 'stage11_curves_by_recall.csv', index=False)


def probe(L, S, ds, folds=5, alphas=(0.1, 1.0, 10.0)):
    """Same predictions as stage11_analyze.probe_section (same folds, same alpha rule); only the summaries are split by recall level."""
    ROOT = R11; pv = np.load(sorted((ROOT / 'raw/probe_vocab').glob('shard_*.npz'))[0])
    W = pv['lm_head_rows'].astype(np.float32); nw = pv['norm_weight'].astype(np.float32); eps = float(pv['eps']); vid = {int(t): i for i, t in enumerate(pv['token_id'])}
    def loadc(c):
        zs = [np.load(f) for f in sorted((ROOT / 'raw/titlepos' / c).glob('shard_*.npz'))]
        return (np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]),
                pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zs]), zs[0]['probe_layers'])
    Xt, Ct, pid, gold, players = loadc('true'); Xf, _, pidf, _, _ = loadc('false_0')
    order = {p: i for i, p in enumerate(pidf)}; Xf = Xf[[order[p] for p in pid]]; Y = Ct[:, -1].astype(np.float32)
    g = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict()
    fold = np.random.default_rng(11).integers(0, folds, len(pid))
    def score(pred, idx):
        h = pred / np.sqrt((pred ** 2).mean(1, keepdims=True) + eps) * nw; lg = h @ W.T; o = np.full(len(idx), np.nan)
        for n, i in enumerate(idx):
            gi = [vid[x] for x in g.get(pid[i], []) if x in vid]
            if gi: o[n] = np.mean([-np.log10(1 + (lg[n] > lg[n, j]).sum()) for j in gi])
        return o
    meta = ds.drop_duplicates('paper_id').set_index('paper_id')[['group_tight', 'recall_level', 'citation_bin']]
    rows = []
    for li, l in enumerate(players):
        X = Xt[:, li].astype(np.float32); XF = Xf[:, li].astype(np.float32); mu, sd = X.mean(0), X.std(0) + 1e-6
        nt, nf = np.full(len(pid), np.nan), np.full(len(pid), np.nan); best = None
        for k in range(folds):
            tr, te = fold != k, np.where(fold == k)[0]
            A = (X[tr] - mu) / sd; ym = Y[tr].mean(0); G = A.T @ A; Bm = A.T @ (Y[tr] - ym)
            if best is None:
                errs = [((((X[te] - mu) / sd) @ np.linalg.solve(G + a_ * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm) + ym - Y[te]) ** 2).mean() for a_ in alphas]
                best = alphas[int(np.argmin(errs))]
            Wp = np.linalg.solve(G + best * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), Bm)
            nt[te] = score((X[te] - mu) / sd @ Wp + ym, te); nf[te] = score((XF[te] - mu) / sd @ Wp + ym, te)
        df = pd.DataFrame({'paper_id': pid, 'true': nt, 'false': nf}).set_index('paper_id').join(meta).reset_index()
        df['spec'] = df['true'] - df['false']; df = df[df.group_tight.isin(['target', 'control'])]
        df['bg'] = df.group_tight.map({'target': 'T', 'control': 'C'}) + df.recall_level.str[1]
        df['group'] = df.group_tight
        row = dict(layer=int(l), alpha=best)
        for k in ['T0', 'C0', 'T1', 'C1']:
            m = boot_mean(df[df.bg == k].spec); row |= {f'{k}': m[0], f'{k}_lo': m[1], f'{k}_hi': m[2], f'{k}_n': m[3]}
        for nm, sub in (('R0', df[df.recall_level == 'R0']), ('pooled', df)):
            e = a11.strat_diff(sub, 'spec'); row |= {f'tc_{nm}': e[0], f'tc_{nm}_lo': e[1], f'tc_{nm}_hi': e[2]}
        e = s10.stratified_diff(df[df.bg.isin(['T1', 'C0'])].assign(readout='probe', layer=l), 'bg', 'T1', 'C0', 'citation_bin', ['spec'], rng, min_n=10).iloc[0]
        row |= dict(tc_R1=e.spec_diff, tc_R1_lo=e.spec_lo, tc_R1_hi=e.spec_hi)
        e = s10.stratified_diff(df[df.bg.isin(['T1', 'T0'])].assign(readout='probe', layer=l), 'bg', 'T1', 'T0', 'citation_bin', ['spec'], rng, min_n=10).iloc[0]
        row |= dict(CA=e.spec_diff, CA_lo=e.spec_lo, CA_hi=e.spec_hi); rows.append(row); print('probe layer', l, flush=True)
    pr = pd.DataFrame(rows); pr.to_csv(S / 'E4b_probe_by_recall.csv', index=False)
    L += ['### E4b. Title-position probe (title-specific = probe(true) - probe(false_0)), by recall level', '',
          '| layer | target - control: R0 view (A - B) | R1 view (C - B) | pooled | C - A | A | B | C | D |', '|---|---|---|---|---|---|---|---|---|']
    for _, x in pr.iterrows():
        L.append(f'| L{int(x.layer)} | {fmt(x.tc_R0, x.tc_R0_lo, x.tc_R0_hi)} | {fmt(x.tc_R1, x.tc_R1_lo, x.tc_R1_hi)} | {fmt(x.tc_pooled, x.tc_pooled_lo, x.tc_pooled_hi)} | '
                 f'{fmt(x.CA, x.CA_lo, x.CA_hi)} | ' + ' | '.join(f'{x[k]:+.3f} (n={int(x[k + "_n"])})' for k in ['T0', 'C0', 'T1', 'C1']) + ' |')
    L.append('')


def main():
    S10 = R10 / 'summary_r0r1'; S11 = R11 / 'summary_r0r1'; S10.mkdir(exist_ok=True); S11.mkdir(exist_ok=True)
    L = ['# R0 / R1 stratified analysis (Stage 10 and Stage 11, existing outputs, CPU)', '']
    ds = stage10(L, S10); print('stage10 done', flush=True)
    stage11(L, S11, ds); print('stage11 done', flush=True)
    probe(L, S11, ds); print('probe done', flush=True)
    (R10 / 'reports/r0_r1_analysis.md').write_text('\n'.join(L) + '\n')                                      # partial report before the slow part
    per_author(L, S10, ds); print('per-author done', flush=True)
    (R10 / 'reports/r0_r1_analysis.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning); main()
