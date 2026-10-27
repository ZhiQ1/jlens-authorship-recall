"""Stage 10 — follow-up to stage10_extra.py X1 (2026-10-26): first token vs later tokens split by name format, i.e. the role of the
author string's first token (initial_first = starts with an initial, given_first = starts with a full given name).
Title-specific signal (true - mean false_0..4) per paper over the tokens of that format/position, all papers, and
target - control within citation bin; 95% bootstrap CIs (B = 2000). Writes summary_extra/X1_by_format.csv."""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd
DIR = Path(__file__).parent
sp = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s10)
ROOT = s10.ROOT; B = 2000; MIN_N = 30; rng = np.random.default_rng(3514)
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
PLAN = [('jlens_public', 56), ('logit', 56), ('jlens_public', 62), ('logit', 62), ('final', 63)]
m, lenses = s10.verify(ROOT)
papers = pd.read_parquet(ROOT / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
toks = pd.read_parquet(ROOT / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'role'])
N = len(toks); P = len(papers); pid = {p: i for i, p in enumerate(papers.paper_id)}
tp = toks.paper_id.map(pid).to_numpy(); grp = papers.group_tight.to_numpy(); cbin = papers.citation_bin.astype(str).to_numpy()
BINS = sorted(set(cbin), key=s10.bin_lo)
first = toks.token_index.to_numpy() == 0
frole = toks[first].set_index('context_id').role; fmt = toks.context_id.map(frole).to_numpy()   # format of each token's author
NLR = {}
for c in CONDS:
    raw = s10.load_raw(ROOT, m, lenses, require_complete=True, cond=c)
    a = np.zeros((len(PLAN), N))
    for i, (r, l) in enumerate(PLAN):
        s = raw[(raw.readout == r) & (raw.layer == l)]; assert len(s) == N
        a[i, s.row_id.to_numpy()] = -np.log10(s['rank'].to_numpy().astype(float))
    NLR[c] = a; del raw; print('loaded', c, flush=True)


def pmean(v, mask):
    cnt = np.bincount(tp[mask], minlength=P).astype(float)
    with np.errstate(invalid='ignore', divide='ignore'): return np.bincount(tp[mask], weights=v[mask], minlength=P) / cnt


def boot(v):
    v = v[~np.isnan(v)]; mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    return v.mean(), *np.percentile(mm, [2.5, 97.5]), len(v)


def tc(v):
    cells = []
    for b in BINS:
        A = v[(cbin == b) & (grp == 'target')]; C = v[(cbin == b) & (grp == 'control')]; A = A[~np.isnan(A)]; C = C[~np.isnan(C)]
        if len(A) >= MIN_N and len(C) >= MIN_N: cells.append((A, C))
    w = np.array([len(A) * len(C) / (len(A) + len(C)) for A, C in cells]); w /= w.sum()
    est = sum(wi * (A.mean() - C.mean()) for wi, (A, C) in zip(w, cells))
    bt = sum(wi * (A[rng.integers(0, len(A), (B, len(A)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A, C) in zip(w, cells))
    return est, *np.percentile(bt, [2.5, 97.5])


rows = []
for f in ['initial_first', 'given_first']:
    for pos, pm in (('first_token', first), ('later_tokens', ~first)):
        mask = (fmt == f) & pm
        for i, (r, l) in enumerate(PLAN):
            per = {c: pmean(NLR[c][i], mask) for c in CONDS}
            spec = per['true'] - np.mean([per[f'false_{k}'] for k in range(5)], 0)
            lv = boot(per['true']); s = boot(spec); t = tc(spec)
            rows.append(dict(format=f, position=pos, readout=r, layer=l, n_tokens=int(mask.sum()), n_papers=s[3], level=lv[0], level_lo=lv[1], level_hi=lv[2],
                             spec=s[0], spec_lo=s[1], spec_hi=s[2], spec_tc=t[0], spec_tc_lo=t[1], spec_tc_hi=t[2]))
# where the surname-first token sits: share that is the author's first token, per format
sf = toks.role.to_numpy() == 'surname_first'
for f in ['initial_first', 'given_first', 'surname_first']:
    mk = (fmt == f) & sf; print('surname_first tokens in format', f, int(mk.sum()), 'share at token_index 0:', round(float((mk & first).sum() / max(mk.sum(), 1)), 3))
print('authors per format', pd.Series(fmt[first]).value_counts().to_dict())
out = pd.DataFrame(rows); out.to_csv(ROOT / 'summary_extra/X1_by_format.csv', index=False); print(out.round(3).to_string())
