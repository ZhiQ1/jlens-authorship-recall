"""Batch 2 group B analysis (CPU): addendum 12 items 2-4, 2-8, 2-3, 2-10. New file; frozen analyses loaded by path.

Plan: /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum12.json (sha256 checked; mismatch = WARN in the report).
Inputs: 381_stage13/raw/b2_{e1noise,e1t5,x3tok,m3tok} (stage13_b2B_gpu.py) + stored originals. Columns: b2_groupB_cols.py.

e1noise (2-4, no hard check in the plan; the original-batch arm must reproduce the stored E1 shard = HARD, as in the gate):
  per name token |delta log10(1/rank)| between batch sizes for true, false_0 (batch 1 vs one 15-copy batch) and patched
  L40 / L48 / L52 (alone at batch 1 vs inside the original 15-element batch): share equal, mean, median, p90, p99, max;
  paper-level E1 recovery per shard x group (target / control / all) x layer: original (patched b15, true / false b1),
  all batch 1, all batch 15; per-paper numerator (patched) differences; per-paper recovery differences on papers with
  |true - false| >= 0.1. -> summary_b2B/e1noise_token.csv, e1noise_recovery.csv, reports/b2_e1noise.md
e1t5 (2-8): E1t recovery per donor false_k (k = 0..4; false_0 = stored raw/patch_title) with the stage11_analyze estimand
  (false baseline = the unpatched L63 element of the same batch); groups target / control / all; five-title mean = plain
  average of the per-title recoveries; intervals: paper bootstrap 2,000 (the original E1t scheme; one index draw per group
  shared by all titles -> paired, rng 3611) and team-cluster 2,000 (groups_core.Engine seed 391) beside it.
  HARD CHECK: the false_0 arm reproduces the published summary/E1t_recovery.csv point recoveries (|diff| <= 0.005, all
  group x layer cells); in addition the frozen stage11_analyze.patch_section is re-run (E1 then E1t, fresh rng) and must
  give the published CSV including CIs (|diff| <= 1e-9; reported, part of the hard check).
  -> summary_b2B/e1t5_per_title.csv, e1t5_mean5.csv, e1t5_tc.csv, hardcheck_e1t5.json, reports/b2_e1t5.md
x3role (2-3): per role (ALL, initial, given_first, given_cont, surname_first, surname_cont) the role's tokens are averaged
  within (pair, author), the author rows are pooled by stratum exactly as stage13_b1_xall_analyze.strata (first / all = mean
  over the paper's authors / others), and the frozen X3 statistics are applied unchanged (stage13_x3_recovery.recovery,
  stage13_x3_analyze.beh_rows, their seeds and team draws). Pairs without a token of the role drop out. Recovery cells with
  O - D < 0.05 are flagged 'gap rule' (addendum 4) in the report.
  HARD CHECK: stratum first, role ALL reproduces the published summary_x3/x3_behaviour.csv (mean) and x3_recovery.csv
  (ratio), |diff| <= 0.005 on every cell compared (as batch 1). WARN: all-author per-author means vs b1_xall para scores.
  -> summary_b2B/x3role_behaviour.csv, x3role_recovery.csv, hardcheck_x3.json, reports/b2_x3role.md
m3tok (2-10): per paper (all authors' name tokens, M3 authors prompt, model output): m3_alltok (token mean over all
  authors; primary, the Stage 10 averaging), m3_authormean, m3_first_alltok, m3_firsttok_allauthors, role means and
  m3_first_first (first scored author's first token inside its name forward; WARN-only comparison) and m3_first_exact (prompt-only do_task path). Summaries as
  stage13_m3_scores (by group; target - control within citation bin: cohort bins >= 30, Stage 11 sample / tune / test
  bins >= 10; team CI seed 461, paper CI seed 462).
  HARD CHECK: m3_first_exact (exact prompt-only do_task path, added by main-session decision) reproduces the published m3_scores_summary.csv author_first_nlr rows (by-group means and the
  four target - control estimates), |diff| <= 0.005. Per-paper agreement is reported (WARN if mean |diff| > 0.005).
  -> summary_b2B/m3tok_perpaper.csv, m3tok_summary.csv, hardcheck_m3.json, reports/b2_m3tok.md
Commands: e1noise | e1t5 | x3role | m3tok | hardcheck_e1t5 (CPU now: stored data only) | unittest | tiny --root DIR
Exit code 3 when a HARD CHECK fails.
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
R13 = BASE / '381_stage13'; PLAN = R13 / 'config/prereg_addendum12.json'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; TOL = 0.005; NB = 2000
P_ = dict(raw=R13 / 'raw', out=R13 / 'summary_b2B', rep=R13 / 'reports')


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))
def fm(e, lo, hi, d=3): return '-' if pd.isna(e) else (f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]' if np.isfinite(lo) else f'{e:+.{d}f}')
def pci(b): b = np.asarray(b, float); b = b[np.isfinite(b)]; return tuple(np.percentile(b, [2.5, 97.5])) if len(b) else (np.nan, np.nan)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load(H / '13_stage13/b2_groupB_cols.py', 'b2cols')


def plan_ok():
    try: return sha(PLAN) == Path(str(PLAN) + '.sha256').read_text().split()[0]
    except Exception: return False


def load_dir(d, scalar=('layers', 'layers_b15', 'layers_b1', 'false_condition')):
    fs = sorted(Path(d).glob('shard_*.npz'))
    if not fs: return None, []
    zs = [np.load(f, allow_pickle=False) for f in fs]
    return {k: (zs[0][k] if k in scalar else np.concatenate([z[k] for z in zs])) for k in zs[0].files if k != 'meta'}, [f.stem for f in fs]


def tokens():
    return pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'role']).set_index('row_id')


def write_hc(name, rep):
    P_['out'].mkdir(parents=True, exist_ok=True); (P_['out'] / name).write_text(json.dumps(rep, indent=1, default=str))
    try: log('HARDCHECK', name, rep.get('status'), json.dumps({k: v for k, v in rep.items() if not isinstance(v, (list, dict))}, default=str))
    except Exception as ex: print('WARN log failed', repr(ex), flush=True)


def hdr(title, script_cmd):
    return [f'# {title}', '', f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_b2B_analyze.py {script_cmd}`. Plan: '
            f'`381_stage13/config/prereg_addendum12.json` (sha256 {"OK" if plan_ok() else "MISMATCH - WARN"}). Raw: `{P_["raw"]}`.', '']


# ================================================================== 2-4 e1noise
def e1noise(a=None):
    smp = pd.read_parquet(R11 / 'config/sample.parquet').set_index('paper_id').group
    fs = sorted((P_['raw'] / 'b2_e1noise').glob('shard_*.npz'))
    if not fs: raise SystemExit('no e1noise data')
    tok_rows, rec_rows, hc = [], [], dict(item='2-4', tolerance=TOL, shards={})
    gc = load(H / '13_stage13/stage13_b2B_gpu.py', 'b2Bgpu_an') if a is None or not getattr(a, 'nogpu_import', False) else None
    for f in fs:
        k = int(f.stem.split('_')[1]); d = dict(np.load(f)); L15 = list(d['layers_b15']); L1 = [int(x) for x in d['layers_b1']]
        stored = P_.get('stored_patch', R11 / 'raw/patch') / f'shard_{k:03d}.npz'
        if stored.exists():
            r = gc.cmp_e1(d, dict(np.load(stored)), 'e1noise'); hc['shards'][k] = r
        else: hc['shards'][k] = dict(status='MISSING')
        arms = [('true', d['rank_true_b1'], d['rank_true_b15']), ('false_0', d['rank_false_b1'], d['rank_false_b15'])]
        arms += [(f'patch_L{l}', d['rank_patch_b1'][:, j], d['rank_patch_b15'][:, L15.index(l)]) for j, l in enumerate(L1)]
        for arm, x1, x15 in arms:
            ad = np.abs(nlr(x1) - nlr(x15))
            tok_rows.append(dict(shard=k, arm=arm, n_tokens=len(ad), share_equal=float((x1 == x15).mean()), mean_abs_dnlr=ad.mean(), median_abs_dnlr=np.median(ad),
                                 p90_abs_dnlr=np.percentile(ad, 90), p99_abs_dnlr=np.percentile(ad, 99), max_abs_dnlr=ad.max()))
        df = pd.DataFrame({'p': d['paper_id'], 't1': nlr(d['rank_true_b1']), 'f1': nlr(d['rank_false_b1']), 't15': nlr(d['rank_true_b15']), 'f15': nlr(d['rank_false_b15'])})
        for j, l in enumerate(L1): df[f'p1_{l}'] = nlr(d['rank_patch_b1'][:, j]); df[f'p15_{l}'] = nlr(d['rank_patch_b15'][:, L15.index(l)])
        pp = df.groupby('p').mean(); pp['grp'] = smp.reindex(pp.index).to_numpy()
        for g in ('all', 'target', 'control'):
            s = pp if g == 'all' else pp[pp.grp == g]
            if not len(s): continue
            for l in L1:
                gap1 = s.t1 - s.f1; gap15 = s.t15 - s.f15
                r15 = (s[f'p15_{l}'] - s.f1).mean() / gap1.mean(); r1 = (s[f'p1_{l}'] - s.f1).mean() / gap1.mean(); r15a = (s[f'p15_{l}'] - s.f15).mean() / gap15.mean()
                nd = np.abs(s[f'p15_{l}'] - s[f'p1_{l}']); big = gap1.abs() >= 0.1
                prd = np.abs(((s[f'p15_{l}'] - s.f1) - (s[f'p1_{l}'] - s.f1))[big] / gap1[big])
                rec_rows.append(dict(shard=k, group=g, layer=l, n_papers=len(s), recovery_b15=r15, recovery_b1=r1, recovery_b15_all=r15a, diff_b15_minus_b1=r15 - r1,
                                     diff_b15all_minus_b1=r15a - r1, paper_num_mean_abs_diff=nd.mean(), paper_num_p90_abs_diff=np.percentile(nd, 90), paper_num_max_abs_diff=nd.max(),
                                     paper_rec_median_abs_diff=np.median(prd) if len(prd) else np.nan, paper_rec_p90_abs_diff=np.percentile(prd, 90) if len(prd) else np.nan,
                                     n_papers_gap_ge_0_1=int(big.sum())))
        hc['shards'][k]['b15_copies_identical_true'] = float(d['b15_elements_identical_true'].mean()); hc['shards'][k]['b15_copies_identical_false'] = float(d['b15_elements_identical_false'].mean())
    T = pd.DataFrame(tok_rows); Rr = pd.DataFrame(rec_rows)
    COLS.write_csv(T, COLS.NOISE_TOKEN, P_['out'] / 'e1noise_token.csv'); COLS.write_csv(Rr, COLS.NOISE_RECOVERY, P_['out'] / 'e1noise_recovery.csv')
    st = [v['status'] for v in hc['shards'].values()]; hc['status'] = 'FAIL' if 'FAIL' in st else ('INCOMPLETE' if 'MISSING' in st or len(st) < 2 else 'PASS')
    write_hc('hardcheck_e1noise.json', hc)
    L = hdr('Addendum 12 item 2-4: E1 batch rounding noise', 'e1noise')
    L += ['Two original Stage 11 shards (rule: lowest-index shard with the highest target share, and with the highest control share): ' + ', '.join(f'shard {k}' for k in sorted(hc['shards'])) + '. '
          'Original arms = 361_stage11.do_patch unchanged (true / false_0 batch 1, patched at 15 layers in one batch of 15). New: patched at L40 / L48 / L52 alone (batch 1); '
          'true and false_0 as 15 identical copies in one batch (element 0). The original unpatched runs were batch 1, so for them "original batch size" = batch 1 and the 15-copy batch is the comparison (stated deviation).', '',
          'Hard check (original arms == stored raw/patch shard; rows identical, recovery per layer |diff| <= 0.005): ' +
          '; '.join(f'shard {k}: {v.get("status")} (rank equality {v.get("rank_equal_share", float("nan")):.4f}, max |diff| {v.get("recovery_max_abs_diff", float("nan")):.1e}; '
                    f'15 copies identical: true {v.get("b15_copies_identical_true", float("nan")):.3f}, false {v.get("b15_copies_identical_false", float("nan")):.3f})' for k, v in hc['shards'].items()) + f' -> **{hc["status"]}**.', '',
          '## Per name token: |delta log10(1/rank)|, batch 1 vs 15-element batch', '', '| shard | arm | tokens | share equal | mean | median | p90 | p99 | max |', '|---|---|---|---|---|---|---|---|---|']
    for r in T.itertuples(): L.append(f'| {r.shard} | {r.arm} | {r.n_tokens} | {r.share_equal:.3f} | {r.mean_abs_dnlr:.4f} | {r.median_abs_dnlr:.4f} | {r.p90_abs_dnlr:.4f} | {r.p99_abs_dnlr:.4f} | {r.max_abs_dnlr:.4f} |')
    L += ['', '## Paper-level E1 recovery by batch size', '', 'b15 = original (patched in the 15-batch, true / false batch 1); b1 = all batch 1; b15 all = patched, true and false all in 15-batches. '
          'Per-paper: |patched b15 - patched b1| (paper means of log10(1/rank)); per-paper recovery |diff| on papers with |true - false| >= 0.1.', '',
          '| shard | group | layer | papers | R b15 (orig) | R b1 | R b15 all | b15 - b1 | b15all - b1 | paper num mean / p90 / max abs diff | paper R median / p90 abs diff (n) |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in Rr.itertuples():
        L.append(f'| {r.shard} | {r.group} | L{r.layer} | {r.n_papers} | {r.recovery_b15:+.4f} | {r.recovery_b1:+.4f} | {r.recovery_b15_all:+.4f} | {r.diff_b15_minus_b1:+.4f} | {r.diff_b15all_minus_b1:+.4f} | '
                 f'{r.paper_num_mean_abs_diff:.4f} / {r.paper_num_p90_abs_diff:.4f} / {r.paper_num_max_abs_diff:.4f} | {r.paper_rec_median_abs_diff:.4f} / {r.paper_rec_p90_abs_diff:.4f} ({r.n_papers_gap_ge_0_1}) |')
    L += ['', 'Noise floor (for tolerances): the largest |b15 - b1| group-level recovery difference above, and the token p99 above.', '']
    (P_['rep']).mkdir(parents=True, exist_ok=True); (P_['rep'] / 'b2_e1noise.md').write_text('\n'.join(L) + '\n'); log('wrote', P_['rep'] / 'b2_e1noise.md')
    return hc['status'] != 'FAIL'


# ================================================================== 2-8 e1t5
def e1t_frame(d, tk):
    t = tk.loc[d['row_id']]
    df = pd.DataFrame({'paper_id': t.paper_id.to_numpy(), 'true': nlr(d['rank_true']), 'false_b1': nlr(d['rank_false'])})
    for i, l in enumerate(d['layers']): df[f'p{int(l)}'] = nlr(d['rank_patch'][:, i])
    df['false'] = df['p63']                    # stage11_analyze E1t: the batch's unpatched L63 element is the baseline
    return df.groupby('paper_id').mean(), [int(l) for l in d['layers']]


def e1t_published_check(d0, tk, smp, out_dir=None):
    """(a) own estimator on the false_0 arm vs published E1t_recovery.csv points; (b) frozen patch_section rerun == published CSV."""
    pub = pd.read_csv(R11 / 'summary/E1t_recovery.csv'); pp, layers = e1t_frame(d0, tk); pp = pp.join(smp)
    rows = []
    for g in ('target', 'control', 'all'):
        s = pp if g == 'all' else pp[pp.group == g]; den = (s['true'] - s['false']).mean()
        for l in layers: rows.append(dict(group=g, layer=l, rec=(s[f'p{l}'] - s['false']).mean() / den))
    m = pd.DataFrame(rows).merge(pub, on=['group', 'layer']); md = float((m.rec - m.recovery).abs().max())
    rep = dict(item='2-8', cells=len(m), expected_cells=len(pub), point_max_abs_diff=md, tolerance=TOL)
    try:
        import tempfile
        sa = load(H / '11_stage11/stage11_analyze.py', 'stage11_analyze_b2B')     # fresh module -> fresh rng(3611)
        toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
        smp_df = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR', '/tmp')) as td:
            dd, ll = sa.load_unit_dir(R11 / 'raw/patch'); sa.patch_section('E1', '', dd, ll, toks, smp_df, Path(td))
            dt = {k: v for k, v in d0.items() if k not in ('layers', 'false_condition')}
            sa.patch_section('E1t', '', dt, d0['layers'], toks, smp_df, Path(td))
            new = pd.read_csv(Path(td) / 'E1t_recovery.csv'); full = float((new.select_dtypes('number') - pub.select_dtypes('number')).abs().max().max())
        rep['frozen_patch_section_rerun_max_abs_diff_incl_CI'] = full; rep['frozen_rerun_threshold'] = 1e-9
    except Exception as ex:
        rep['frozen_patch_section_rerun_error'] = repr(ex); full = np.inf
    rep['status'] = 'PASS' if md <= TOL and len(m) == len(pub) and full <= 1e-9 else 'FAIL'
    return rep


def hardcheck_e1t5(a=None):
    tk = tokens(); smp = pd.read_parquet(R11 / 'config/sample.parquet').set_index('paper_id')[['group']]
    d0, _ = load_dir(R11 / 'raw/patch_title'); rep = e1t_published_check(d0, tk, smp); write_hc('hardcheck_e1t5.json', rep)
    print('HARDCHECK e1t5', rep['status'], json.dumps(rep)); return rep['status'] == 'PASS'


def e1t5(a=None, src=None):
    gcm = load(H / '14_groups/groups_core.py', 'gc_b2B'); tk = tokens()
    smp = pd.read_parquet(R11 / 'config/sample.parquet').set_index('paper_id')[['group']]
    src = src or {'false_0': R11 / 'raw/patch_title'} | {t: P_['raw'] / 'b2_e1t5' / t for t in TITLES[1:]}
    data = {}
    for t in TITLES:
        d, sh = load_dir(src[t])
        if d is None or len(sh) < (24 if src.get('_n') is None else src['_n']): raise SystemExit(f'e1t5: {t} incomplete ({len(sh)} shards)')
        data[t] = d
    hc = e1t_published_check(data['false_0'], tk, smp) if '_n' not in src else dict(status='SKIPPED (tiny)')
    write_hc('hardcheck_e1t5.json', hc)
    frames = {}
    for t in TITLES:
        pp, layers = e1t_frame(data[t], tk); frames[t] = pp.join(smp)
    common = sorted(set.intersection(*[set(f.index) for f in frames.values()]))
    E = gcm.Engine(pd.DataFrame(index=pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id']).paper_id))
    rows, boots = [], {}
    gidx = {}
    for g in ('target', 'control', 'all'):
        ids = [p for p in common if g == 'all' or frames['false_0'].loc[p, 'group'] == g]
        if len(ids) < 2: log(f'e1t5: group {g} has {len(ids)} papers - skipped'); continue
        gidx[g] = (ids, np.random.default_rng(3611).integers(0, len(ids), (NB, len(ids))), E.W(np.array(ids)))
    for t in TITLES:
        f = frames[t]
        for g, (ids, ix, W) in gidx.items():
            s = f.loc[ids]; den = (s['true'] - s['false']).to_numpy()
            for l in layers:
                num = (s[f'p{l}'] - s['false']).to_numpy(); rec = num.mean() / den.mean()
                bp = num[ix].mean(1) / den[ix].mean(1)
                with np.errstate(invalid='ignore', divide='ignore'): bt = (W @ num) / (W @ den)
                boots[(t, g, l)] = (bp, bt)
                lo, hi = pci(bp); lt, ht = E.ci(bt)
                rows.append(dict(title=t, group=g, layer=l, n_papers=len(ids), recovery=rec, rec_lo=lo, rec_hi=hi, rec_lo_team=lt, rec_hi_team=ht, gain=num.mean(), true_minus_false=den.mean()))
    D = pd.DataFrame(rows); M, TC = [], []
    for (g, l), x in D.groupby(['group', 'layer']):
        x = x.set_index('title'); bp = np.mean([boots[(t, g, l)][0] for t in TITLES], 0); bt = np.nanmean([boots[(t, g, l)][1] for t in TITLES], 0)
        dp = bp - boots[('false_0', g, l)][0]
        r = dict(group=g, layer=l, n_papers=int(x.n_papers.iloc[0]), recovery_mean5=x.recovery.mean(), recovery_false0=x.recovery['false_0'],
                 rec_min=x.recovery.min(), rec_max=x.recovery.max(), rec_sd=x.recovery.std(ddof=1))
        r['lo'], r['hi'] = pci(bp); r['lo_team'], r['hi_team'] = E.ci(bt); r['mean5_minus_false0'] = r['recovery_mean5'] - r['recovery_false0']; r['diff_lo'], r['diff_hi'] = pci(dp)
        M.append(r)
    for l in (layers if {'target', 'control'} <= set(gidx) else []):
        bp = np.mean([boots[(t, 'target', l)][0] - boots[(t, 'control', l)][0] for t in TITLES], 0)
        bt = np.nanmean([boots[(t, 'target', l)][1] - boots[(t, 'control', l)][1] for t in TITLES], 0)
        rt = D[(D.group == 'target') & (D.layer == l)].set_index('title').recovery; rc = D[(D.group == 'control') & (D.layer == l)].set_index('title').recovery
        r = dict(layer=l, tc_mean5=(rt - rc).mean(), tc_false0=rt['false_0'] - rc['false_0']); r['lo'], r['hi'] = pci(bp); r['lo_team'], r['hi_team'] = E.ci(bt); TC.append(r)
    M = pd.DataFrame(M); TC = pd.DataFrame(TC, columns=COLS.E1T_TC)
    COLS.write_csv(D, COLS.E1T_PER_TITLE, P_['out'] / 'e1t5_per_title.csv'); COLS.write_csv(M, COLS.E1T_MEAN5, P_['out'] / 'e1t5_mean5.csv'); COLS.write_csv(TC, COLS.E1T_TC, P_['out'] / 'e1t5_tc.csv')
    L = hdr('Addendum 12 item 2-8: E1t with five false titles', 'e1t5')
    L += ['E1t = patch only the last title token (true -> false_k), one layer at a time (frozen 361_stage11.do_patch_title; donor false_k with its own title position). '
          'Recovery = mean(patched - false) / mean(true - false), false = the unpatched L63 element of the same batch (stage11_analyze rule); paper means, all authors. '
          'false_0 = stored Stage 11 run; false_1..4 = new. Five-title mean = plain average of the per-title recoveries. '
          'Intervals: paper bootstrap 2,000 (original E1t scheme; shared index draw per group -> paired over titles) and team-cluster 2,000 (groups_core seed 391).', '',
          f'Papers in all five titles: {len(common)}.', '']
    if 'point_max_abs_diff' in hc:
        L += [f'HARD CHECK (false_0 arm vs published summary/E1t_recovery.csv): point max |diff| {hc["point_max_abs_diff"]:.1e} over {hc["cells"]} cells (threshold {TOL}); '
              f'frozen patch_section re-run incl. CIs max |diff| {hc.get("frozen_patch_section_rerun_max_abs_diff_incl_CI", float("nan")):.1e} (threshold 1e-9) -> **{hc["status"]}**.', '']
    for g in ('all', 'target', 'control'):
        L += [f'## {g}', '', '| layer | mean5 [paper CI] | team CI | false_0 | mean5 - false_0 [CI] | per-title min..max (SD) |', '|---|---|---|---|---|---|']
        for r in M[M.group == g].sort_values('layer').itertuples():
            L.append(f'| L{r.layer} | {fm(r.recovery_mean5, r.lo, r.hi)} | [{r.lo_team:+.3f}, {r.hi_team:+.3f}] | {r.recovery_false0:+.3f} | {fm(r.mean5_minus_false0, r.diff_lo, r.diff_hi)} | {r.rec_min:+.3f}..{r.rec_max:+.3f} ({r.rec_sd:.3f}) |')
        L.append('')
    L += ['## target - control (recovery)', '', '| layer | mean5 [paper CI] | team CI | false_0 |', '|---|---|---|---|']
    for r in TC.itertuples(): L.append(f'| L{r.layer} | {fm(r.tc_mean5, r.lo, r.hi)} | [{r.lo_team:+.3f}, {r.hi_team:+.3f}] | {r.tc_false0:+.3f} |')
    L += ['', 'Full tables: summary_b2B/e1t5_per_title.csv, e1t5_mean5.csv, e1t5_tc.csv.', '']
    (P_['rep'] / 'b2_e1t5.md').write_text('\n'.join(L) + '\n'); log('wrote', P_['rep'] / 'b2_e1t5.md')
    return hc['status'] != 'FAIL'


# ================================================================== 2-3 x3role
def x3_token_frame(d, tk):
    t = tk.loc[d['row_id']]; warn = []
    if not ((t.paper_id.to_numpy() == d['paper_id']).all() and (t.author_index.to_numpy() == d['author_index']).all()): warn.append('row_id -> paper / author mismatch')
    df = pd.DataFrame({'paper_id': d['paper_id'], 'author_index': d['author_index'], 'n_authors': d['n_authors'], 'partner': d['partner'],
                       'lexical_neighbour': d['lexical_neighbour'], 'role': t.role.to_numpy()})
    for v in COLS.X3_VERS: df[f'score_{v}'] = nlr(d[f'rank_{v}']) if f'rank_{v}' in d else d[f'nlr_{v}']
    return df, warn


def x3_compute(tokdf):
    b1a = load(H / '13_stage13/stage13_b1_xall_analyze.py', 'b1xa_b2B')
    sc = [f'score_{v}' for v in COLS.X3_VERS]; outR, outB = [], []
    for role, rl in COLS.ROLES.items():
        s = tokdf if rl is None else tokdf[tokdf.role.isin(rl)]
        ctx = s.groupby(['paper_id', 'author_index'], sort=False).agg({**{c: 'mean' for c in sc}, 'n_authors': 'first', 'partner': 'first', 'lexical_neighbour': 'first'}).reset_index()
        if ctx.empty: continue
        st = b1a.strata(ctx)
        for stratum in COLS.STRATA:
            fr = st[stratum].dropna(subset=sc)
            if len(fr) < 4: continue
            Rr, Bh = b1a.x3_stats(fr)
            outR.append(Rr.assign(stratum=stratum, role=role)); outB.append(Bh.assign(stratum=stratum, role=role))
    R = pd.concat(outR, ignore_index=True); B = pd.concat(outB, ignore_index=True)
    R = R[COLS.X3_KEYS + [c for c in R.columns if c not in COLS.X3_KEYS]]; B = B[COLS.X3_KEYS + [c for c in B.columns if c not in COLS.X3_KEYS]]
    return R, B


def x3_hardcheck(R, B, pub_dir=None):
    pub_dir = Path(pub_dir or R13 / 'summary_x3'); rep = dict(item='2-3', tolerance=TOL)
    pr = pd.read_csv(pub_dir / 'x3_recovery.csv'); pb = pd.read_csv(pub_dir / 'x3_behaviour.csv')
    r = R[(R.stratum == 'first') & (R.role == 'ALL')].merge(pr, on=['set', 'subset', 'split', 'false', 'group'], suffixes=('', '_pub'))
    b = B[(B.stratum == 'first') & (B.role == 'ALL')].merge(pb, on=['set', 'subset', 'split', 'contrast'], suffixes=('', '_pub'))
    rep['recovery_cells'] = len(r); rep['recovery_expected'] = len(pr); rep['behaviour_cells'] = len(b); rep['behaviour_expected'] = len(pb)
    rep['recovery_max_abs_diff'] = float((r.ratio - r.ratio_pub).abs().max()) if len(r) else np.inf
    rep['behaviour_max_abs_diff'] = float((b['mean'] - b['mean_pub']).abs().max()) if len(b) else np.inf
    rep['status'] = 'PASS' if (rep['recovery_max_abs_diff'] <= TOL and rep['behaviour_max_abs_diff'] <= TOL and len(r) == len(pr) and len(b) == len(pb)) else 'FAIL'
    return rep


def x3role(a=None, tokdf=None, tag=''):
    tk = tokens(); warn = []
    if tokdf is None:
        d, sh = load_dir(P_['raw'] / 'b2_x3tok', scalar=())
        if d is None: raise SystemExit('no x3tok data')
        if len(sh) < 24: warn.append(f'only {len(sh)} of 24 shards')
        tokdf, w = x3_token_frame(d, tk); warn += w
        # WARN check: per-author all-token means == batch-1 all-author para scores
        try:
            ref, _ = load_dir(R13 / 'raw/b1_xall/para', scalar=())
            ref = pd.DataFrame({k: ref[k] for k in ('paper_id', 'author_index', 'score_original', 'score_paraphrase', 'score_partner', 'score_lexical')})
            mine = tokdf.groupby(['paper_id', 'author_index'])[[f'score_{v}' for v in COLS.X3_VERS]].mean().reset_index()
            m = mine.merge(ref, on=['paper_id', 'author_index'], suffixes=('', '_ref'))
            dd = np.abs(np.r_[[m[f'score_{v}'] - m[f'score_{v}_ref'] for v in COLS.X3_VERS]])
            warn_chk = f'{len(m)} author rows vs raw/b1_xall/para: mean |d| {dd.mean():.2e}, max |d| {dd.max():.2e}, exact {(dd < 1e-12).mean():.3f}'
            if dd.max() > 0.05: warn.append('per-author means differ from b1_xall para: ' + warn_chk + ' (threshold 0.05)')
        except Exception as ex: warn_chk = f'failed: {ex!r}'
    else: warn_chk = 'synthetic input (unit test)'
    R, B = x3_compute(tokdf)
    hc = x3_hardcheck(R, B); hc['author_mean_check'] = warn_chk
    write_hc(f'hardcheck_x3{tag}.json', hc)
    R.to_csv(P_['out'] / f'x3role_recovery{tag}.csv', index=False); B.to_csv(P_['out'] / f'x3role_behaviour{tag}.csv', index=False)
    if tag: return hc['status'] == 'PASS'
    L = hdr('Addendum 12 item 2-3: X3 behaviour by token role and for all authors', 'x3role')
    L += ['Per-token batch-1 scores of every author (original / paraphrase / partner B / lexical neighbour D title; batch-1 all-author rows of raw/b1_xall/para). '
          'Role tokens averaged within (pair, author); strata as stage13_b1_xall_analyze (first author; all = mean over the paper\'s authors; others = authors >= 2); '
          'frozen X3 statistics (stage13_x3_recovery.recovery, stage13_x3_analyze.beh_rows; same seeds / team draws). Pairs without a token of the role drop out.', '',
          f'HARD CHECK (first author, role ALL vs published x3_behaviour.csv / x3_recovery.csv; threshold {TOL}): behaviour max |diff| {hc["behaviour_max_abs_diff"]:.1e} ({hc["behaviour_cells"]}/{hc["behaviour_expected"]} cells), '
          f'recovery max |diff| {hc["recovery_max_abs_diff"]:.1e} ({hc["recovery_cells"]}/{hc["recovery_expected"]} cells) -> **{hc["status"]}**.', f'Per-author check (WARN only): {warn_chk}.', '']
    for part in ('test', 'all'):
        L += [f'## Primary set, subset all, split {part}: recovery (P - D)/(O - D) vs D and behaviour P - D', '',
              '| stratum | role | group | n | O - D | recovery [CI] | P - D [CI] |', '|---|---|---|---|---|---|---|']
        for stratum in COLS.STRATA:
            for role in COLS.ROLES:
                for g in ('all', 'target', 'control', 'target_minus_control'):
                    x = R[(R.stratum == stratum) & (R.role == role) & (R.set == 'primary') & (R.subset == 'all') & (R.split == part) & (R['false'] == 'lexical_neighbour_D') & (R.group == g)]
                    if not len(x): continue
                    x = x.iloc[0]; gap = x.get('den', np.nan)
                    rec = fm(x.ratio, x.lo, x.hi) + (' (gap rule: O - D < 0.05)' if g != 'target_minus_control' and np.isfinite(gap) and gap < 0.05 else '')
                    pd_ = ''
                    if g != 'target_minus_control': pd_ = fm(x.num, x.num_lo, x.num_hi)
                    L.append(f'| {stratum} | {role} | {g} | {int(x.n)} | {"" if not np.isfinite(gap) else f"{gap:+.3f}"} | {rec} | {pd_} |')
        L.append('')
    L += ['Full tables (all sets / subsets / splits / contrasts): summary_b2B/x3role_recovery.csv, x3role_behaviour.csv.', '', '## WARN', ''] + ([f'- {w}' for w in warn] or ['- none']) + ['']
    (P_['rep'] / 'b2_x3role.md').write_text('\n'.join(L) + '\n'); log('wrote', P_['rep'] / 'b2_x3role.md')
    return hc['status'] != 'FAIL'


# ================================================================== 2-10 m3tok
def m3_perpaper(tokdf):
    """tokdf: paper_id, author_index, token_index, role, nlr."""
    g = tokdf.groupby('paper_id')
    first_ai = g.author_index.transform('min'); isf = tokdf.author_index == first_ai
    out = pd.DataFrame({'m3_alltok': g.nlr.mean(), 'n_tokens': g.size(), 'n_authors': g.author_index.nunique()})
    out['m3_authormean'] = tokdf.groupby(['paper_id', 'author_index']).nlr.mean().groupby(level=0).mean()
    out['m3_first_alltok'] = tokdf[isf].groupby('paper_id').nlr.mean()
    out['m3_first_first'] = tokdf[isf & (tokdf.token_index == 0)].groupby('paper_id').nlr.mean()
    out['m3_firsttok_allauthors'] = tokdf[tokdf.token_index == 0].groupby('paper_id').nlr.mean()
    for role, rl in COLS.ROLES.items():
        if rl is None: continue
        out[f'm3_role_{role}'] = tokdf[tokdf.role.isin(rl)].groupby('paper_id').nlr.mean()
    return out


def m3_summary(d):
    m3s = load(H / '13_stage13/stage13_m3_scores.py', 'm3s_b2B'); S = []
    for sc in COLS.M3_SCORES:
        for gname, x in [('all', d)] + list(d.groupby('group')):
            v = x[sc].dropna(); S.append(dict(table='by_group', score=sc, group=gname, n=len(v), mean=v.mean(), share_rank1=(v == 0).mean()))
    subsets = [('all cohort target/control', d)]
    sub11 = d[d.stage11_group.notna()].assign(group=lambda x: x.stage11_group); subsets.append(('Stage 11 sample (1,186)', sub11))
    for sp in ('tune', 'test'): subsets.append((f'pairs.parquet {sp}', sub11[sub11.split == sp]))
    for name, x in subsets:
        x = x.reset_index(drop=True)
        for sc in COLS.M3_SCORES:
            mn = 30 if name.startswith('all cohort') else 10
            e, (ct, cp), nb = m3s.strat(x[sc].to_numpy(float), x.group.to_numpy(), x.citation_bin.to_numpy(), [m3s.cw(x.team.to_numpy(), 461), m3s.cw(x.paper_id.to_numpy(), 462)], min_n=mn)
            S.append(dict(table='target_minus_control', score=sc, group=name, n=len(x), mean=e, lo_team=ct[0], hi_team=ct[1], lo_paper=cp[0], hi_paper=cp[1], n_bins=nb))
    return pd.DataFrame(S)


def m3_hardcheck(S, pub=None):
    pub = pd.read_csv(pub or R13 / 'summary_m3/m3_scores_summary.csv'); pub = pub[(pub.score == 'author_first_nlr') & pub.table.isin(['by_group', 'target_minus_control'])]
    new = S[S.score == 'm3_first_exact'].assign(score='author_first_nlr')
    m = new.merge(pub, on=['table', 'score', 'group'], suffixes=('', '_pub'))
    md = float((m['mean'] - m['mean_pub']).abs().max()) if len(m) else np.inf
    return dict(item='2-10', cells=len(m), expected_cells=len(pub), max_abs_diff=md, tolerance=TOL, status='PASS' if md <= TOL and len(m) == len(pub) else 'FAIL',
                cells_detail=m[['table', 'group', 'mean', 'mean_pub']].to_dict('records'))


def m3_meta(pp):
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13_b2B')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); _, team = c13.group_folds(papers.paper_id.to_numpy()); papers['team'] = team
    d = papers.assign(group=papers.group_tight)[['paper_id', 'group', 'citation_bin', 'team']].merge(pp, left_on='paper_id', right_index=True, how='left')
    s11 = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].rename(columns={'group': 'stage11_group'}); d = d.merge(s11, on='paper_id', how='left')
    pairs = pd.read_parquet(R13 / 'config/pairs.parquet')[['paper_id', 'split']]; d = d.merge(pairs, on='paper_id', how='left')
    pubpp = pd.read_csv(R13 / 'summary_m3/m3_scores_perpaper.csv')[['paper_id', 'author_first_nlr']].rename(columns={'author_first_nlr': 'author_first_nlr_published'})
    return d.merge(pubpp, on='paper_id', how='left')


def m3tok(a=None, pp=None, tag=''):
    warn = []
    if pp is None:
        tk = tokens(); dd, sh = load_dir(P_['raw'] / 'b2_m3tok', scalar=())
        if dd is None: raise SystemExit('no m3tok data')
        if len(sh) < 72: warn.append(f'only {len(sh)} of 72 shards')
        t = tk.loc[dd['row_id']]
        if not ((t.paper_id.to_numpy() == dd['paper_id']).all() and (t.token_index.to_numpy() == dd['token_index']).all()): warn.append('row_id -> paper / token mismatch')
        tokdf = pd.DataFrame({'paper_id': dd['paper_id'], 'author_index': dd['author_index'], 'token_index': dd['token_index'], 'role': t.role.to_numpy(), 'nlr': nlr(dd['rank'])})
        pp = m3_perpaper(tokdf)
        ex = pd.Series(nlr(dd['exact_first_rank']), index=dd['exact_paper_id']); pp['m3_first_exact'] = ex.reindex(pp.index)
    d = m3_meta(pp)
    def agree(col):
        x = d.dropna(subset=[col, 'author_first_nlr_published']); ad = np.abs(x[col] - x.author_first_nlr_published)
        return dict(n=len(x), mean_abs=float(ad.mean()) if len(x) else None, max_abs=float(ad.max()) if len(x) else None, share_exact=float((ad < 1e-12).mean()) if len(x) else None)
    perpaper = agree('m3_first_exact'); inseq = agree('m3_first_first')
    if len(d.dropna(subset=['m3_first_exact'])) and perpaper['mean_abs'] > TOL: warn.append(f'per-paper exact first token vs published author_first_nlr: mean |d| {perpaper["mean_abs"]:.4f} > {TOL} (WARN; the hard check is on the summary numbers)')
    if inseq['n'] and inseq['mean_abs'] > TOL: warn.append(f'in-sequence first token vs published: mean |d| {inseq["mean_abs"]:.4f}, threshold {TOL} (WARN only)')
    S = m3_summary(d); hc = m3_hardcheck(S); hc['per_paper_exact'] = perpaper
    Si = S[S.score == 'm3_first_first'].assign(score='m3_first_exact'); hw = m3_hardcheck(pd.concat([S[S.score != 'm3_first_exact'], Si]))
    hc['in_sequence_warn'] = dict(value=hw['max_abs_diff'], threshold=TOL, status='OK' if hw['status'] == 'PASS' else 'WARN', per_paper=inseq)
    write_hc(f'hardcheck_m3{tag}.json', hc)
    COLS.write_csv(d, COLS.M3_PERPAPER, P_['out'] / f'm3tok_perpaper{tag}.csv'); COLS.write_csv(S.reindex(columns=COLS.M3_SUMMARY), COLS.M3_SUMMARY, P_['out'] / f'm3tok_summary{tag}.csv')
    if tag: return hc['status'] == 'PASS'
    L = hdr('Addendum 12 item 2-10: M3 task runs scored on all name tokens of all authors', 'm3tok')
    L += ['M3 authors prompt `Who are the authors of the paper titled "{t}"?\\nAuthors:` (no year), every author context of every cohort paper, teacher-forced, '
          'log10(1/rank) of every name token at the model output (batch 1, as score_tf). Paper scores: m3_alltok = mean over all name tokens of all authors (primary; '
          'Stage 10 averaging); m3_authormean = mean over authors of their token means; m3_first_alltok = first author all tokens; m3_firsttok_allauthors = first token of every author; '
          'm3_first_first = first author first token inside its name forward; m3_first_exact = the same token by the exact published prompt-only forward (hard check); m3_role_* = tokens of one role.', '',
          f'In-sequence first token (m3_first_first) vs the same published cells, WARN only: max |diff| {hc["in_sequence_warn"]["value"]:.1e} (threshold {TOL}) -> {hc["in_sequence_warn"]["status"]}; per paper {hc["in_sequence_warn"]["per_paper"]}.',
          f'HARD CHECK (m3_first_exact = exact published prompt-only path, reproduces the published m3_scores_summary.csv author_first_nlr cells; threshold {TOL}): max |diff| {hc["max_abs_diff"]:.1e} over {hc["cells"]}/{hc["expected_cells"]} cells -> **{hc["status"]}**.',
          f'Per paper, exact arm (WARN only): {perpaper}.', '', '## Means by cohort group', '', '| score | ' + ' | '.join(['all', 'target', 'control', 'guard', 'excluded']) + ' |', '|---|' + '---|' * 5]
    for sc in COLS.M3_SCORES:
        y = S[(S.table == 'by_group') & (S.score == sc)].set_index('group')
        L.append(f'| {sc} | ' + ' | '.join((f'{y.loc[g, "mean"]:+.4f} (n {int(y.loc[g, "n"])})' if g in y.index else '-') for g in ['all', 'target', 'control', 'guard', 'excluded']) + ' |')
    L += ['', '## Target - control within citation bin (team CI primary; paper CI beside it)', '', '| score | papers | estimate | team CI | paper CI | bins |', '|---|---|---|---|---|---|']
    for r in S[S.table == 'target_minus_control'].itertuples():
        L.append(f'| {r.score} | {r.group} | {r.mean:+.4f} | [{r.lo_team:+.4f}, {r.hi_team:+.4f}] | [{r.lo_paper:+.4f}, {r.hi_paper:+.4f}] | {int(r.n_bins)} |')
    L += ['', 'Full tables: summary_b2B/m3tok_perpaper.csv, m3tok_summary.csv.', '', '## WARN', ''] + ([f'- {w}' for w in warn] or ['- none']) + ['']
    (P_['rep'] / 'b2_m3tok.md').write_text('\n'.join(L) + '\n'); log('wrote', P_['rep'] / 'b2_m3tok.md')
    return hc['status'] != 'FAIL'


# ================================================================== unit tests of the hard checks (CPU, stored data)
def unittest(a=None):
    """identical -> PASS, perturbed -> FAIL for every hard check (no GPU data needed)."""
    P_['out'] = R13 / 'summary_b2B/unittest'; P_['out'].mkdir(parents=True, exist_ok=True); res = {}
    tk = tokens(); smp = pd.read_parquet(R11 / 'config/sample.parquet').set_index('paper_id')[['group']]
    # 2-8: stored false_0 E1t vs published (identical), and with L48 ranks perturbed
    d0, _ = load_dir(R11 / 'raw/patch_title'); res['2-8 identical -> PASS'] = e1t_published_check(d0, tk, smp)['status'] == 'PASS'
    dp = dict(d0); rp = dp['rank_patch'].copy(); i = list(dp['layers']).index(48); rp[:, i] = rp[:, i] * 3 + 1; dp['rank_patch'] = rp
    res['2-8 perturbed -> FAIL'] = e1t_published_check(dp, tk, smp)['status'] == 'FAIL'
    # 2-3: synthetic one-'token'-per-author frame carrying the stored batch-1 per-author scores (first author = published)
    ref, _ = load_dir(R13 / 'raw/b1_xall/para', scalar=())
    syn = pd.DataFrame({'paper_id': ref['paper_id'], 'author_index': ref['author_index'], 'n_authors': ref['n_authors'], 'partner': ref['partner'],
                        'lexical_neighbour': ref['lexical_neighbour'], 'role': 'surname_first'})
    for v in COLS.X3_VERS: syn[f'score_{v}'] = ref[f'score_{v}']
    res['2-3 identical -> PASS'] = x3role(tokdf=syn, tag='_unittest_identical')
    syn2 = syn.copy(); syn2['score_paraphrase'] = syn2['score_paraphrase'] + 0.02
    res['2-3 perturbed (+0.02 paraphrase) -> FAIL'] = not x3role(tokdf=syn2, tag='_unittest_perturbed')
    # 2-10: per-paper frame whose m3_first_first = published author_first_nlr
    pub = pd.read_csv(R13 / 'summary_m3/m3_scores_perpaper.csv').set_index('paper_id')
    pp = pd.DataFrame(index=pub.index); pp['m3_first_exact'] = pub.author_first_nlr
    for c in COLS.M3_SCORES:
        if c not in pp: pp[c] = pub.author_first_nlr
    pp['n_tokens'] = 1; pp['n_authors'] = 1
    res['2-10 identical -> PASS'] = m3tok(pp=pp, tag='_unittest_identical')
    pp2 = pp.copy(); pp2['m3_first_exact'] = pp2['m3_first_exact'] + 0.01
    res['2-10 perturbed (+0.01) -> FAIL'] = not m3tok(pp=pp2, tag='_unittest_perturbed')
    # 2-4: original-arm comparison (stored raw/patch shard 0 dressed as an e1noise unit) identical / perturbed
    gcm = load(H / '13_stage13/stage13_b2B_gpu.py', 'b2Bgpu_ut'); z = dict(np.load(R11 / 'raw/patch/shard_000.npz'))
    fake = dict(row_id=z['row_id'], rank_true_b1=z['rank_true'], rank_false_b1=z['rank_false'], rank_patch_b15=z['rank_patch'], layers_b15=z['layers'])
    res['2-4 identical -> PASS'] = gcm.cmp_e1(fake, z, 'e1noise')['status'] == 'PASS'
    fake2 = dict(fake); fake2['rank_patch_b15'] = z['rank_patch'] * 2 + 1
    res['2-4 perturbed -> FAIL'] = gcm.cmp_e1(fake2, z, 'e1noise')['status'] == 'FAIL'
    res = {k: bool(v) for k, v in res.items()}; print('UNITTEST', json.dumps(res), flush=True)
    (P_['out'] / 'unittest_result.json').write_text(json.dumps(res, indent=1)); return all(res.values())


# ================================================================== tiny (analysis part on tiny GPU outputs)
def tiny(a):
    """runs every analysis on the tiny-model outputs of stage13_b2B_gpu.py tiny (code path only; hard checks are
    expected to FAIL on random-model numbers and are therefore not asserted here - see unittest)."""
    root = Path(a.root); P_.update(raw=root / 'raw', out=root / 'summary_b2B', rep=root / 'reports', stored_patch=root / 'stored/patch'); P_['out'].mkdir(parents=True, exist_ok=True)
    ok = {}
    try: ok['e1noise runs (hard check PASS on tiny stored analogue)'] = bool(e1noise())
    except SystemExit as ex: ok['e1noise runs'] = False; print('e1noise', ex)
    src = {'false_0': root / 'stored/patch_title'} | {t: root / 'raw/b2_e1t5' / t for t in TITLES[1:]}
    # tiny: only shard 0 present for false_1..4 and shards 0/6 stored for false_0 -> restrict false_0 to shard 0
    (root / 'stored/patch_title_s0').mkdir(parents=True, exist_ok=True)
    import shutil; shutil.copy(root / 'stored/patch_title/shard_000.npz', root / 'stored/patch_title_s0/shard_000.npz'); src['false_0'] = root / 'stored/patch_title_s0'; src['_n'] = 1
    try: e1t5(src=src); ok['e1t5 runs'] = (P_['out'] / 'e1t5_mean5.csv').exists()
    except Exception as ex: ok['e1t5 runs'] = False; print('e1t5 crashed', repr(ex))
    M = pd.read_csv(P_['out'] / 'e1t5_mean5.csv'); D = pd.read_csv(P_['out'] / 'e1t5_per_title.csv')
    x = D[(D.group == 'all') & (D.layer == 48)]; ok['e1t5 mean5 = average of titles'] = abs(M[(M.group == 'all') & (M.layer == 48)].recovery_mean5.iloc[0] - x.recovery.mean()) < 1e-12
    ok['e1t5 L63 recovery == 0 (baseline = L63 element)'] = bool(np.allclose(D[D.layer == 63].recovery, 0))
    ok['e1t5 csv columns from the column module'] = list(M.columns) == COLS.E1T_MEAN5
    # x3 / m3 tiny: the frames are built from the tiny raw files (code path); the statistics need >= 4 pairs -> run the
    # frame builders and per-paper aggregation only, plus the full statistics on the synthetic real-data frames (unittest)
    tk = tokens(); d, _ = load_dir(root / 'raw/b2_x3tok', scalar=()); tf, w = x3_token_frame(d, tk); ok['x3 token frame roles + no mismatch'] = tf.role.notna().all() and not w
    dm, _ = load_dir(root / 'raw/b2_m3tok', scalar=()); t = tk.loc[dm['row_id']]
    tokdf = pd.DataFrame({'paper_id': dm['paper_id'], 'author_index': dm['author_index'], 'token_index': dm['token_index'], 'role': t.role.to_numpy(), 'nlr': nlr(dm['rank'])})
    pp = m3_perpaper(tokdf); pp['m3_first_exact'] = pd.Series(nlr(dm['exact_first_rank']), index=dm['exact_paper_id']).reindex(pp.index)
    ok['m3 exact column filled'] = pp.m3_first_exact.notna().all(); ok['m3 per-paper scores'] = len(pp) == len(set(dm['paper_id'])) and pp.m3_first_first.notna().all()
    ok['m3 alltok = token mean'] = abs(pp.m3_alltok.iloc[0] - tokdf[tokdf.paper_id == pp.index[0]].nlr.mean()) < 1e-12
    ok = {k: bool(v) for k, v in ok.items()}; print('TINY ANALYSIS CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['e1noise', 'e1t5', 'x3role', 'm3tok', 'hardcheck_e1t5', 'unittest', 'tiny']); ap.add_argument('--root')
    a = ap.parse_args(); P_['out'].mkdir(parents=True, exist_ok=True); P_['rep'].mkdir(parents=True, exist_ok=True)
    if not plan_ok(): log('WARN addendum 12 sha256 differs from its .sha256 file')
    ok = {'e1noise': e1noise, 'e1t5': e1t5, 'x3role': x3role, 'm3tok': m3tok, 'hardcheck_e1t5': hardcheck_e1t5, 'unittest': unittest, 'tiny': tiny}[a.cmd](a)
    sys.exit(0 if ok else (1 if a.cmd in ('unittest', 'tiny') else 3))


if __name__ == '__main__':
    main()
