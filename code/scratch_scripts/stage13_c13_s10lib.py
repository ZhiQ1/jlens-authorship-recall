"""Addendum 13 (2026-11-06): shared helpers for C-1 and C-2 (Stage 10 title-specific rank signal for archived paper lists).

Stage 10 raw (351_stage10/raw/[cond_false_k/]<readout>/L<l>/shard_*.npz) stores the gold-token rank of every author x name token
for true and false_0..4 titles. Per token: nlr = log10(1/rank). Per paper and token subset: true = mean nlr over the subset tokens
(token-weighted, the Stage 10 paper value), false = mean over k of the same mean under false_k, spec = true - false.
Subsets: aa_all (all authors, all name tokens = Stage 10 mean_nlr), aa_first (token 0 of every author, Stage 7.1 'first'),
aa_cont (tokens >= 1, Stage 7.1 'continuation'), fa_first (first author, token 0 = the Stage 5-8 unit), fa_all (first author, all tokens).
Readouts: jlens_public and logit at L24, 32, 40, 48, 56, 62 (the Stage 4-8 layers stored in Stage 10; L16 not stored) and final L63;
'int6' = mean of the 6 lens layers (the 7-layer-equivalent without L16).
Read-only; nothing here writes outside the caller's output directory.
"""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'
LAYERS = [24, 32, 40, 48, 56, 62]
READOUTS = [('jlens_public', l) for l in LAYERS] + [('logit', l) for l in LAYERS] + [('final', 63)]
CONDS = ['true'] + [f'false_{k}' for k in range(5)]
SUBSETS = ['aa_all', 'aa_first', 'aa_cont', 'fa_first', 'fa_all']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def raw_dir(cond, readout, layer):
    return R10 / 'raw' / ('' if cond == 'true' else f'cond_{cond}') / readout / f'L{layer}'


def tokens_for(pids):
    t = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'author_index', 'token_index', 'token_id', 'role'])
    return t[t.paper_id.isin(set(pids))].reset_index(drop=True)


def load_ranks(tok, readouts=READOUTS, conds=CONDS):
    """returns dict (cond, readout, layer) -> rank array aligned with tok rows; raises if any row is missing."""
    shards = sorted(tok.shard.unique()); out = {}
    for cond in conds:
        for ro, l in readouts:
            d = raw_dir(cond, ro, l); rid, rk = [], []
            for s in shards:
                z = np.load(d / f'shard_{int(s):03d}.npz'); rid.append(z['row_id']); rk.append(z['rank'])
            ser = pd.Series(np.concatenate(rk), index=np.concatenate(rid))
            v = ser.reindex(tok.row_id.to_numpy())
            if v.isna().any(): raise RuntimeError(f'missing rows {cond} {ro} L{l}: {int(v.isna().sum())}')
            out[(cond, ro, l)] = v.to_numpy(np.int64)
    return out


def subset_mask(tok, s):
    ai, ti = tok.author_index.to_numpy(), tok.token_index.to_numpy()
    return {'aa_all': np.ones(len(tok), bool), 'aa_first': ti == 0, 'aa_cont': ti > 0, 'fa_first': (ai == 0) & (ti == 0), 'fa_all': ai == 0}[s]


def paper_table(tok, ranks, readouts=READOUTS):
    """long table: paper_id, subset, readout, layer ('int6' for the lens mean), true, false, spec, n_tok"""
    rows = []
    for s in SUBSETS:
        m = subset_mask(tok, s); t = tok[m]
        for ro, l in readouts:
            nl = {c: -np.log10(ranks[(c, ro, l)][m].astype(float)) for c in CONDS}
            df = pd.DataFrame({'paper_id': t.paper_id.to_numpy(), 'true': nl['true'], **{c: nl[c] for c in CONDS[1:]}})
            g = df.groupby('paper_id', sort=True).mean()
            fal = g[CONDS[1:]].mean(1)
            rows.append(pd.DataFrame({'paper_id': g.index, 'subset': s, 'readout': ro, 'layer': str(l), 'true': g['true'].to_numpy(),
                                      'false': fal.to_numpy(), 'spec': (g['true'] - fal).to_numpy(), 'n_tok': df.groupby('paper_id', sort=True).size().to_numpy()}))
    T = pd.concat(rows, ignore_index=True)
    lens = T[T.readout != 'final']
    I = lens.groupby(['paper_id', 'subset', 'readout'], as_index=False)[['true', 'false', 'spec', 'n_tok']].mean(); I['layer'] = 'int6'
    I['n_tok'] = I.n_tok.round().astype(int)
    return pd.concat([T, I[T.columns]], ignore_index=True)


# ---------------- estimators
def team_ids():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id'])
    _, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); return dict(zip(papers.paper_id, TEAMS))


def mean_cluster(pids, x, TEAM, seed=2, NB=2000):
    """as stage13_alltok_report.mean_cluster: team-cluster bootstrap of a mean (archived team ids)."""
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]
    if len(x) == 0: return np.nan, np.nan, np.nan, 0
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    W = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float64)[:, codes]
    return x.mean(), *np.percentile((W @ x) / np.maximum(W.sum(1), 1e-9), [2.5, 97.5]), len(x)


def boot8d(v, seed, NBOOT=10000):
    """verbatim logic of 08_stage8/351_stage8D.py bootstrap(): iid resampling of the values (pairs or papers), percentile CI."""
    a = np.asarray(v, dtype=float)
    if not len(a) or not np.isfinite(a).all(): raise ValueError('Invalid bootstrap values')
    rng = np.random.default_rng(seed); samples = np.empty(NBOOT)
    for i in range(0, NBOOT, 500):
        n = min(500, NBOOT - i); samples[i:i + n] = a[rng.integers(0, len(a), (n, len(a)))].mean(axis=1)
    return float(a.mean()), float(np.quantile(samples, .025)), float(np.quantile(samples, .975)), len(a)


def identity_check(tok, ranks, pids, gold_first=None, gold_all=None):
    """HARD check (plan): first author's first-token true-title score at final, via this join, equals the Stage 10 stored value
    for the same rows read through an independent path (contexts.parquet -> context_id -> name_tokens -> raw final/L63).
    Plus (also hard): the all-token paper value equals Stage 10 summary_title/paper_title_contrasts (true_mean_nlr, spec_mean_nlr)
    at final 63 and jlens_public 56. WARN only: Stage 10 author-0 token ids vs archived gold first-token id / all token ids."""
    res = {}
    m = subset_mask(tok, 'fa_first'); a = pd.Series(-np.log10(ranks[('true', 'final', 63)][m].astype(float)), index=tok.paper_id[m].to_numpy())
    ctx = pd.read_parquet(R10 / 'cohort/contexts.parquet', columns=['context_id', 'paper_id', 'author_index', 'shard'])
    ctx = ctx[ctx.paper_id.isin(set(pids)) & (ctx.author_index == 0)]
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'token_index', 'token_id'])
    r0 = nt[nt.context_id.isin(set(ctx.context_id)) & (nt.token_index == 0)].merge(ctx, on='context_id')
    vals = {}
    for s, g in r0.groupby('shard'):
        z = np.load(raw_dir('true', 'final', 63) / f'shard_{int(s):03d}.npz'); pos = {int(r): i for i, r in enumerate(z['row_id'])}
        for _, x in g.iterrows(): vals[x.paper_id] = -np.log10(float(z['rank'][pos[int(x.row_id)]]))
    b = pd.Series(vals).reindex(a.index)
    res['fa_first_final_true'] = dict(n_papers=int(len(a)), n_expected=len(set(pids)), n_missing=int(b.isna().sum()),
                                      max_abs_diff=float((a - b).abs().max()), equal=bool(len(a) == len(set(pids)) and (a - b).abs().max() == 0))
    pt = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'true_mean_nlr', 'spec_mean_nlr'])
    pt = pt[pt.paper_id.isin(set(pids))]
    P = paper_table(tok, ranks, readouts=[('final', 63), ('jlens_public', 56)])
    for ro, l in (('final', 63), ('jlens_public', 56)):
        x = P[(P.subset == 'aa_all') & (P.readout == ro) & (P.layer == str(l))].set_index('paper_id')
        y = pt[(pt.readout == ro) & (pt.layer == l)].set_index('paper_id').reindex(x.index)
        res[f'aa_all_{ro}_{l}'] = dict(n=int(len(x)), max_abs_diff_true=float((x['true'] - y.true_mean_nlr).abs().max()),
                                       max_abs_diff_spec=float((x.spec - y.spec_mean_nlr).abs().max()))
    hard = res['fa_first_final_true']['equal'] and all(res[k]['max_abs_diff_true'] <= 1e-9 and res[k]['max_abs_diff_spec'] <= 1e-9
                                                        for k in res if k.startswith('aa_all'))
    if gold_first is not None:
        s10 = r0.set_index('paper_id').token_id
        g = pd.Series(gold_first); s10 = s10.reindex(g.index)
        res['warn_gold_first_token_match'] = dict(n=int(len(g)), match=int((s10 == g).sum()), mismatch_papers=[p for p in g.index if s10.get(p) != g[p]][:20])
    if gold_all is not None:
        fa = tok[tok.author_index == 0].sort_values(['paper_id', 'token_index']).groupby('paper_id').token_id.apply(list)
        mm = [p for p, ids in gold_all.items() if fa.get(p) != ids]
        res['warn_gold_all_tokens_match'] = dict(n=len(gold_all), match=len(gold_all) - len(mm), mismatch_papers=mm[:20])
    res['status'] = 'PASS' if hard else 'FAIL'
    return res
