"""Stage 10 extra analyses (CPU, 2026-10-26; user request, no new GPU runs). Reads the frozen main-round raw files of all 7
conditions (readouts final/logit/jlens_public/jlens_self100/jlens_fitA at L24,32,40,48,56,62 + final L63) and writes
summary_extra/*.csv. Same conventions as 351_stage10.py analyze/analyze-title: per-token nlr = log10(1/rank), paper-level
means, spec = true - mean(false_0..4) per paper, target - control pooled within citation bin (bins with >= 30 papers in
both groups, weights n_t*n_c/(n_t+n_c)), 95% bootstrap CIs over papers (B = 2000; clustered by paper for context-level).

  X1  token position: first token of the author string vs later tokens; first word vs later words
      X1_levels      true-title level and spec by group (all / target / control)
      X1_tc          target - control within bin, for true level and spec, per position
      X1_cond        later tokens (words) when the first token (word) is / is not in the top 10, true title
  X2  citation: per citation bin x group (target / control / all), true level and spec; Spearman vs log10(citations+1)
  X3  lenses: per layer, paired differences between readouts (level, top-10 share, spec), all papers;
      target - control spec of (lens - logit) within bin
"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata

DIR = Path(__file__).parent
spec_ = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(s10)
ROOT = s10.ROOT; OUT = ROOT / 'summary_extra'; OUT.mkdir(exist_ok=True)
B = 2000; MIN_N = 30
rng = np.random.default_rng(3512)
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
PLAN = [(r, l) for r in ['jlens_public', 'jlens_self100', 'jlens_fitA', 'logit'] for l in s10.DEFAULT_LAYERS] + [('final', 63)]


def log(*x): print(time.strftime('%T'), *x, flush=True)


# ------------------------------------------------------------------ load
m, lenses = s10.verify(ROOT)
papers = pd.read_parquet(ROOT / 'cohort/papers.parquet').drop(columns=['prompt_ids'])
toks = pd.read_parquet(ROOT / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'word_index', 'role'])
assert (toks.row_id.to_numpy() == np.arange(len(toks))).all()
N = len(toks); pid = {p: i for i, p in enumerate(papers.paper_id)}; P = len(papers)
tp = toks.paper_id.map(pid).to_numpy()                       # paper index per token
ctx = toks.context_id.to_numpy()
grp = papers.group_tight.to_numpy(); cbin = papers.citation_bin.astype(str).to_numpy()
cites = np.log10(pd.to_numeric(papers.citations, errors='coerce').fillna(0).to_numpy() + 1)
BINS = sorted(set(cbin), key=s10.bin_lo)

R = {}  # R[cond] = int32 [len(PLAN), N] ranks
for c in CONDS:
    raw = s10.load_raw(ROOT, m, lenses, require_complete=True, cond=c)
    a = np.zeros((len(PLAN), N), np.int32)
    for i, (r, l) in enumerate(PLAN):
        sub = raw[(raw.readout == r) & (raw.layer == l)]
        if len(sub) != N: raise RuntimeError(f'{c} {r} L{l}: {len(sub)} rows, expected {N}')
        a[i, sub.row_id.to_numpy()] = sub['rank'].to_numpy()
    if (a < 1).any(): raise RuntimeError(f'{c}: unfilled ranks')
    R[c] = a; del raw; log('loaded', c)
NLR = {c: -np.log10(R[c].astype(np.float64)) for c in CONDS}


def paper_mean(v, mask):
    """[pairs, N] token values -> [pairs, P] paper means over tokens in mask (NaN where a paper has none)."""
    cnt = np.bincount(tp[mask], minlength=P).astype(float)
    out = np.stack([np.bincount(tp[mask], weights=row[mask], minlength=P) for row in v])
    with np.errstate(invalid='ignore', divide='ignore'): return out / cnt


def level_and_spec(mask, metric=lambda c: NLR[c]):
    lv = {c: paper_mean(metric(c), mask) for c in CONDS}
    sp = lv['true'] - np.mean([lv[f'false_{k}'] for k in range(5)], 0)
    return lv['true'], sp


def boot_mean(v):
    v = v[~np.isnan(v)]
    if len(v) < 2: return (np.nan, np.nan, np.nan, len(v))
    mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    lo, hi = np.percentile(mm, [2.5, 97.5]); return (v.mean(), lo, hi, len(v))


def strat_diff(v, sel=None):
    """target - control pooled within citation bin; v = [P] paper values."""
    sel = np.ones(P, bool) if sel is None else sel
    cells = []
    for b in BINS:
        A = v[sel & (cbin == b) & (grp == 'target')]; C = v[sel & (cbin == b) & (grp == 'control')]
        A = A[~np.isnan(A)]; C = C[~np.isnan(C)]
        if len(A) >= MIN_N and len(C) >= MIN_N: cells.append((A, C))
    if not cells: return (np.nan, np.nan, np.nan)
    w = np.array([len(A) * len(C) / (len(A) + len(C)) for A, C in cells]); w /= w.sum()
    est = sum(wi * (A.mean() - C.mean()) for wi, (A, C) in zip(w, cells))
    bt = sum(wi * (A[rng.integers(0, len(A), (B, len(A)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A, C) in zip(w, cells))
    lo, hi = np.percentile(bt, [2.5, 97.5]); return (est, lo, hi)


GROUPS = {'all': np.ones(P, bool), 'target': grp == 'target', 'control': grp == 'control'}

# ------------------------------------------------------------------ X1 token / word position
first_tok = toks.token_index.to_numpy() == 0
first_word = toks.word_index.to_numpy() == 0
POS = {'first_token': first_tok, 'later_tokens': ~first_tok, 'first_word': first_word, 'later_words': ~first_word}
rows_lv, rows_tc = [], []
for pos, mask in POS.items():
    lv, sp = level_and_spec(mask)
    for i, (r, l) in enumerate(PLAN):
        for g, gm in GROUPS.items():
            a = boot_mean(lv[i][gm]); b = boot_mean(sp[i][gm])
            rows_lv.append(dict(position=pos, readout=r, layer=l, group=g, n_papers=a[3], level=a[0], level_lo=a[1], level_hi=a[2], spec=b[0], spec_lo=b[1], spec_hi=b[2]))
        a = strat_diff(lv[i]); b = strat_diff(sp[i])
        rows_tc.append(dict(position=pos, readout=r, layer=l, level_tc=a[0], level_tc_lo=a[1], level_tc_hi=a[2], spec_tc=b[0], spec_tc_lo=b[1], spec_tc_hi=b[2]))
    log('X1 levels', pos)
pd.DataFrame(rows_lv).to_csv(OUT / 'X1_levels.csv', index=False); pd.DataFrame(rows_tc).to_csv(OUT / 'X1_tc.csv', index=False)

# conditional: later tokens (words) given the first token (word) is in the top 10, true title, clustered bootstrap by paper
cid, cinv = np.unique(ctx, return_inverse=True); NC = len(cid)
cpaper = np.zeros(NC, int); cpaper[cinv] = tp
counts = rng.multinomial(P, np.full(P, 1 / P), size=B).astype(np.float32)   # [B, P] paper resample weights
W = counts[:, cpaper]                                                        # [B, NC] context weights
rows_cd = []
for unit, fmask in (('token', first_tok), ('word', first_word)):
    has_later = np.bincount(cinv[~fmask], minlength=NC) > 0
    for i, (r, l) in enumerate(PLAN):
        rk = R['true'][i]
        f_top = np.ones(NC, bool)                        # every token of the first unit in the top 10
        np.logical_and.at(f_top, cinv[fmask], rk[fmask] <= 10)
        later = np.bincount(cinv[~fmask], weights=NLR['true'][i][~fmask], minlength=NC) / np.maximum(np.bincount(cinv[~fmask], minlength=NC), 1)
        later10 = np.bincount(cinv[~fmask], weights=(rk[~fmask] <= 10).astype(float), minlength=NC) / np.maximum(np.bincount(cinv[~fmask], minlength=NC), 1)
        for g, gm in GROUPS.items():
            ok = has_later & gm[cpaper]
            row = dict(unit=unit, readout=r, layer=l, group=g, n_contexts=int(ok.sum()), share_first_top10=f_top[ok].mean())
            for name, val in (('later_level', later), ('later_top10', later10)):
                yes, no = ok & f_top, ok & ~f_top
                if yes.sum() < 30 or no.sum() < 30: continue
                my = (W[:, yes] * val[yes]).sum(1) / W[:, yes].sum(1); mn = (W[:, no] * val[no]).sum(1) / W[:, no].sum(1)
                row |= {f'{name}_if_top10': val[yes].mean(), f'{name}_if_not': val[no].mean(), f'{name}_diff': val[yes].mean() - val[no].mean(),
                        f'{name}_diff_lo': np.percentile(my - mn, 2.5), f'{name}_diff_hi': np.percentile(my - mn, 97.5), 'n_top10': int(yes.sum()), 'n_not': int(no.sum())}
            rows_cd.append(row)
    log('X1 cond', unit)
pd.DataFrame(rows_cd).to_csv(OUT / 'X1_cond.csv', index=False)

# ------------------------------------------------------------------ X2 citation bins
allm = np.ones(N, bool)
lv, sp = level_and_spec(allm)
top10 = {c: (R[c] <= 10).astype(np.float64) for c in CONDS}
lv10, sp10 = level_and_spec(allm, metric=lambda c: top10[c])
rows_b, rows_s = [], []
for i, (r, l) in enumerate(PLAN):
    for g, gm in GROUPS.items():
        for b in BINS:
            sel = gm & (cbin == b)
            a = boot_mean(lv[i][sel]); s = boot_mean(sp[i][sel])
            rows_b.append(dict(readout=r, layer=l, group=g, citation_bin=b, n_papers=a[3], level=a[0], level_lo=a[1], level_hi=a[2], spec=s[0], spec_lo=s[1], spec_hi=s[2]))
        for name, v in (('level', lv[i]), ('spec', sp[i])):
            ok = gm & ~np.isnan(v); x, y = cites[ok], v[ok]
            rho = np.corrcoef(rankdata(x), rankdata(y))[0, 1]
            bs = []
            for _ in range(1000):
                ix = rng.integers(0, len(x), len(x)); bs.append(np.corrcoef(rankdata(x[ix]), rankdata(y[ix]))[0, 1])
            rows_s.append(dict(readout=r, layer=l, group=g, metric=name, n=int(ok.sum()), spearman_rho=rho, rho_lo=np.percentile(bs, 2.5), rho_hi=np.percentile(bs, 97.5)))
    log('X2', r, l)
pd.DataFrame(rows_b).to_csv(OUT / 'X2_by_bin.csv', index=False); pd.DataFrame(rows_s).to_csv(OUT / 'X2_spearman.csv', index=False)

# ------------------------------------------------------------------ X3 lens comparison
RO = ['jlens_public', 'jlens_self100', 'jlens_fitA', 'logit']
idx = {pr: i for i, pr in enumerate(PLAN)}
MET = {'level': lv, 'top10_share': lv10, 'spec': sp}
rows_m, rows_p, rows_dd = [], [], []
for l in s10.DEFAULT_LAYERS:
    for name, arr in MET.items():
        for r in RO:
            a = boot_mean(arr[idx[(r, l)]]); rows_m.append(dict(layer=l, metric=name, readout=r, mean=a[0], lo=a[1], hi=a[2], n=a[3]))
        for j, r1 in enumerate(RO):
            for r2 in RO[j + 1:]:
                d = boot_mean(arr[idx[(r1, l)]] - arr[idx[(r2, l)]])
                rows_p.append(dict(layer=l, metric=name, a=r1, b=r2, diff=d[0], lo=d[1], hi=d[2], n=d[3]))
    for r in RO[:3]:
        d = strat_diff(sp[idx[(r, l)]] - sp[idx[('logit', l)]])
        rows_dd.append(dict(layer=l, lens=r, tc_spec_minus_logit=d[0], lo=d[1], hi=d[2]))
pd.DataFrame(rows_m).to_csv(OUT / 'X3_means.csv', index=False); pd.DataFrame(rows_p).to_csv(OUT / 'X3_pairwise.csv', index=False)
pd.DataFrame(rows_dd).to_csv(OUT / 'X3_tc_spec_vs_logit.csv', index=False)
log('EXTRA DONE ->', OUT)
