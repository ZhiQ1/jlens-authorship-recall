"""Addendum 13 item C-5 (2026-11-06): Stage 10 extras (X1-X3, name-format split, conditional split) at every stored layer.

Plan (locked): 381_stage13/config/prereg_addendum13.json (sha256 be6d2c98...), item "C-5".
This is a parameterised copy of 10_stage10/stage10_extra.py (part x), stage10_extra_format.py and stage10_extra_cond_role.py
(part fmt); the frozen scripts are not edited. The computation is copied line for line; only PLAN, the RNG seeds and the output
directory are parameters, and raw ranks are read directly from the npz files of the PLAN readout-layers (same row_id / rank arrays
that s10.load_raw returns).
  --mode repro : the ORIGINAL PLAN and seeds -> summary_c13/c5/repro/  (HARD CHECK: equal to 351_stage10/summary_extra/*.csv)
  --mode ext   : every other stored readout-layer -> summary_c13/c5/ext/ (new seeds: original + 100)
       part x  : public and logit at L50-55, L57-61 (self100 / fitA have only the 6 main layers, already in the original PLAN)
       part fmt: X1_by_format and X1_cond_by_first_role at all stored readout-layers not in the original PLANs
                 (public / logit L24-L62, self100 / fitA L24-L62 6 layers, final 63)
Each mode writes the same CSV names as the originals. stage13_c13_c5_report.py merges repro + ext and checks.
Usage  stage13_c13_c5.py --part x|fmt --mode repro|ext [--tiny]   (tiny: first 8 shards' rows only; output in c5_tiny)
"""
import argparse, importlib.util, hashlib, json, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata

ap = argparse.ArgumentParser(); ap.add_argument('--part', required=True, choices=['x', 'fmt']); ap.add_argument('--mode', required=True, choices=['repro', 'ext'])
ap.add_argument('--tiny', action='store_true'); A = ap.parse_args()
BASE = Path('/scratch/zhang.zhiqi2/jlens'); R13 = BASE / '381_stage13'
PLANF = R13 / 'config/prereg_addendum13.json'
if hashlib.sha256(PLANF.read_bytes()).hexdigest() != 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e': raise SystemExit('PLAN CHANGED')
DIR = Path.home() / 'jlens_work/10_stage10'
spec_ = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(s10)
ROOT = s10.ROOT
OUT = R13 / ('summary_c13/c5_tiny' if A.tiny else 'summary_c13/c5') / A.mode; OUT.mkdir(parents=True, exist_ok=True)
SEED_ADD = 0 if A.mode == 'repro' else 100
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
EXT_L = [50, 51, 52, 53, 54, 55, 57, 58, 59, 60, 61]
ALL_STORED = [(r, l) for r in ['jlens_public', 'logit'] for l in [24, 32, 40, 48] + list(range(50, 63))] + \
             [(r, l) for r in ['jlens_self100', 'jlens_fitA'] for l in s10.DEFAULT_LAYERS] + [('final', 63)]


def log(*x): print(time.strftime('%T'), *x, flush=True)


toks_all = pd.read_parquet(ROOT / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'shard', 'token_index', 'word_index', 'role'])
assert (toks_all.row_id.to_numpy() == np.arange(len(toks_all))).all()
SHARDS = sorted(toks_all.shard.unique())[:8] if A.tiny else sorted(toks_all.shard.unique())


def raw_rank(cond, r, l, N):
    """[N] ranks by row_id for one (cond, readout, layer), straight from the npz files (as s10.load_raw / out_file)."""
    d = ROOT / 'raw' / ('' if cond == 'true' else f'cond_{cond}') / r / f'L{l}'; a = np.zeros(N, np.int64)
    for k in SHARDS:
        z = np.load(d / f'shard_{int(k):03d}.npz'); a[z['row_id']] = z['rank']
    return a


if A.tiny:   # keep rows and papers of the first shards only; row_ids stay global, so index into a compacted copy
    keep = toks_all.shard.isin(SHARDS).to_numpy(); RID = toks_all.row_id.to_numpy()[keep]
    toks_all = toks_all[keep].reset_index(drop=True)
    _rr = raw_rank
    raw_rank = lambda c, r, l, N: _rr(c, r, l, int(RID.max()) + 1)[RID]


# =============================================================================================== part x (stage10_extra.py)
def part_x():
    B = 2000; MIN_N = 30
    rng = np.random.default_rng(3512 + SEED_ADD)
    PLAN = [(r, l) for r in ['jlens_public', 'jlens_self100', 'jlens_fitA', 'logit'] for l in s10.DEFAULT_LAYERS] + [('final', 63)]
    if A.mode == 'ext': PLAN = [(r, l) for r in ['jlens_public', 'logit'] for l in EXT_L]
    papers = pd.read_parquet(ROOT / 'cohort/papers.parquet').drop(columns=['prompt_ids'])
    toks = toks_all
    if A.tiny: papers = papers[papers.paper_id.isin(set(toks.paper_id))].reset_index(drop=True)
    N = len(toks); pid = {p: i for i, p in enumerate(papers.paper_id)}; P = len(papers)
    tp = toks.paper_id.map(pid).to_numpy()
    ctx = toks.context_id.to_numpy()
    grp = papers.group_tight.to_numpy(); cbin = papers.citation_bin.astype(str).to_numpy()
    cites = np.log10(pd.to_numeric(papers.citations, errors='coerce').fillna(0).to_numpy() + 1)
    BINS = sorted(set(cbin), key=s10.bin_lo)
    R = {}
    for c in CONDS:
        a = np.zeros((len(PLAN), N), np.int32)
        for i, (r, l) in enumerate(PLAN): a[i] = raw_rank(c, r, l, N)
        if (a < 1).any(): raise RuntimeError(f'{c}: unfilled ranks')
        R[c] = a; log('loaded', c)
    NLR = {c: -np.log10(R[c].astype(np.float64)) for c in CONDS}

    def paper_mean(v, mask):
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
        sel = np.ones(P, bool) if sel is None else sel
        cells = []
        for b in BINS:
            A_ = v[sel & (cbin == b) & (grp == 'target')]; C = v[sel & (cbin == b) & (grp == 'control')]
            A_ = A_[~np.isnan(A_)]; C = C[~np.isnan(C)]
            if len(A_) >= MIN_N and len(C) >= MIN_N: cells.append((A_, C))
        if not cells: return (np.nan, np.nan, np.nan)
        w = np.array([len(A_) * len(C) / (len(A_) + len(C)) for A_, C in cells]); w /= w.sum()
        est = sum(wi * (A_.mean() - C.mean()) for wi, (A_, C) in zip(w, cells))
        bt = sum(wi * (A_[rng.integers(0, len(A_), (B, len(A_)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A_, C) in zip(w, cells))
        lo, hi = np.percentile(bt, [2.5, 97.5]); return (est, lo, hi)

    GROUPS = {'all': np.ones(P, bool), 'target': grp == 'target', 'control': grp == 'control'}
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

    cid, cinv = np.unique(ctx, return_inverse=True); NC = len(cid)
    cpaper = np.zeros(NC, int); cpaper[cinv] = tp
    counts = rng.multinomial(P, np.full(P, 1 / P), size=B).astype(np.float32)
    W = counts[:, cpaper]
    rows_cd = []
    for unit, fmask in (('token', first_tok), ('word', first_word)):
        has_later = np.bincount(cinv[~fmask], minlength=NC) > 0
        for i, (r, l) in enumerate(PLAN):
            rk = R['true'][i]
            f_top = np.ones(NC, bool)
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

    RO = ['jlens_public', 'jlens_self100', 'jlens_fitA', 'logit']
    idx = {pr: i for i, pr in enumerate(PLAN)}
    MET = {'level': lv, 'top10_share': lv10, 'spec': sp}
    rows_m, rows_p, rows_dd = [], [], []
    for l in (s10.DEFAULT_LAYERS if A.mode == 'repro' else EXT_L):
        ro = [r for r in RO if (r, l) in idx]
        for name, arr in MET.items():
            for r in ro:
                a = boot_mean(arr[idx[(r, l)]]); rows_m.append(dict(layer=l, metric=name, readout=r, mean=a[0], lo=a[1], hi=a[2], n=a[3]))
            for j, r1 in enumerate(ro):
                for r2 in ro[j + 1:]:
                    d = boot_mean(arr[idx[(r1, l)]] - arr[idx[(r2, l)]])
                    rows_p.append(dict(layer=l, metric=name, a=r1, b=r2, diff=d[0], lo=d[1], hi=d[2], n=d[3]))
        for r in [x for x in ro if x != 'logit']:
            d = strat_diff(sp[idx[(r, l)]] - sp[idx[('logit', l)]])
            rows_dd.append(dict(layer=l, lens=r, tc_spec_minus_logit=d[0], lo=d[1], hi=d[2]))
    pd.DataFrame(rows_m).to_csv(OUT / 'X3_means.csv', index=False); pd.DataFrame(rows_p).to_csv(OUT / 'X3_pairwise.csv', index=False)
    pd.DataFrame(rows_dd).to_csv(OUT / 'X3_tc_spec_vs_logit.csv', index=False)
    log('X DONE ->', OUT)


# =============================================================================================== part fmt (format + cond_role)
def part_fmt():
    # ---- stage10_extra_format.py
    B = 2000; MIN_N = 30; rng = np.random.default_rng(3514 + SEED_ADD)
    PLAN0 = [('jlens_public', 56), ('logit', 56), ('jlens_public', 62), ('logit', 62), ('final', 63)]
    PLAN = PLAN0 if A.mode == 'repro' else [x for x in ALL_STORED if x not in PLAN0]
    papers = pd.read_parquet(ROOT / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
    toks = toks_all
    if A.tiny: papers = papers[papers.paper_id.isin(set(toks.paper_id))].reset_index(drop=True)
    N = len(toks); P = len(papers); pid = {p: i for i, p in enumerate(papers.paper_id)}
    tp = toks.paper_id.map(pid).to_numpy(); grp = papers.group_tight.to_numpy(); cbin = papers.citation_bin.astype(str).to_numpy()
    BINS = sorted(set(cbin), key=s10.bin_lo)
    first = toks.token_index.to_numpy() == 0
    frole = toks[first].set_index('context_id').role; fmt = toks.context_id.map(frole).to_numpy()
    NLR = {}
    for c in CONDS:
        a = np.zeros((len(PLAN), N))
        for i, (r, l) in enumerate(PLAN): a[i] = -np.log10(raw_rank(c, r, l, N).astype(float))
        NLR[c] = a; log('loaded', c)

    def pmean(v, mask):
        cnt = np.bincount(tp[mask], minlength=P).astype(float)
        with np.errstate(invalid='ignore', divide='ignore'): return np.bincount(tp[mask], weights=v[mask], minlength=P) / cnt

    def boot(v):
        v = v[~np.isnan(v)]; mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
        return v.mean(), *np.percentile(mm, [2.5, 97.5]), len(v)

    def tc(v):
        cells = []
        for b in BINS:
            A_ = v[(cbin == b) & (grp == 'target')]; C = v[(cbin == b) & (grp == 'control')]; A_ = A_[~np.isnan(A_)]; C = C[~np.isnan(C)]
            if len(A_) >= MIN_N and len(C) >= MIN_N: cells.append((A_, C))
        if not cells: return np.nan, np.nan, np.nan
        w = np.array([len(A_) * len(C) / (len(A_) + len(C)) for A_, C in cells]); w /= w.sum()
        est = sum(wi * (A_.mean() - C.mean()) for wi, (A_, C) in zip(w, cells))
        bt = sum(wi * (A_[rng.integers(0, len(A_), (B, len(A_)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A_, C) in zip(w, cells))
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
    pd.DataFrame(rows).to_csv(OUT / 'X1_by_format.csv', index=False); log('format done')
    del NLR
    # ---- stage10_extra_cond_role.py (true title only)
    rng = np.random.default_rng(3513 + SEED_ADD)
    PLANC0 = [('final', 63), ('logit', 62), ('jlens_public', 62)]
    PLANC = PLANC0 if A.mode == 'repro' else [x for x in ALL_STORED if x not in PLANC0]
    papers = pd.read_parquet(ROOT / 'cohort/papers.parquet', columns=['paper_id', 'group_tight'])
    if A.tiny: papers = papers[papers.paper_id.isin(set(toks.paper_id))].reset_index(drop=True)
    pidx = {p: i for i, p in enumerate(papers.paper_id)}; P = len(papers)
    cid, cinv = np.unique(toks.context_id.to_numpy(), return_inverse=True); NC = len(cid)
    cpaper = np.zeros(NC, int); cpaper[cinv] = toks.paper_id.map(pidx).to_numpy()
    frole = np.empty(NC, object); f0 = toks.token_index.to_numpy() == 0; frole[cinv[f0]] = toks.role.to_numpy()[f0]
    fw = toks.word_index.to_numpy() == 0
    W = rng.multinomial(P, np.full(P, 1 / P), size=B).astype(np.float32)[:, cpaper]
    rows = []
    for r, l in PLANC:
        rk = raw_rank('true', r, l, len(toks))
        nlr = -np.log10(rk.astype(float))
        ftop = np.ones(NC, bool); np.logical_and.at(ftop, cinv[fw], rk[fw] <= 10)
        nl = np.bincount(cinv[~fw], minlength=NC); later = np.bincount(cinv[~fw], weights=nlr[~fw], minlength=NC) / np.maximum(nl, 1)
        for role in ['initial_first', 'given_first']:
            ok = (nl > 0) & (frole == role)
            yes, no = ok & ftop, ok & ~ftop
            my = (W[:, yes] * later[yes]).sum(1) / W[:, yes].sum(1); mn = (W[:, no] * later[no]).sum(1) / W[:, no].sum(1)
            rows.append(dict(readout=r, layer=l, first_role=role, n_contexts=int(ok.sum()), share_first_word_top10=ftop[ok].mean(),
                             later_if_top10=later[yes].mean(), later_if_not=later[no].mean(), diff=later[yes].mean() - later[no].mean(),
                             lo=np.percentile(my - mn, 2.5), hi=np.percentile(my - mn, 97.5), n_top10=int(yes.sum()), n_not=int(no.sum())))
    pd.DataFrame(rows).to_csv(OUT / 'X1_cond_by_first_role.csv', index=False); log('cond_role done ->', OUT)


part_x() if A.part == 'x' else part_fmt()
