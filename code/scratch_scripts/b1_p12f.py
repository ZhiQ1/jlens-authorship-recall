"""Addendum 10 (batch 1) item 3: Stage 12 P1 (single-position patching) and P2 (attention vs MLP) with donors false_1..4.

Plan: /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum10.json (sha256 8243a4ed...), item "3 P1/P2 five false
titles". Driver: the addendum-8 driver 14_groups/rerun_gpu.py is loaded by path (it loads the frozen 12_stage12/371_stage12.py
and its s11); the frozen unit functions s12.do_patch_pos (P1) and s12.do_patch_comp (P2) are called UNCHANGED on the
original Stage 11/12 sample (361_stage11/config/sample.parquet). Only the false condition changes: s11.FALSE_FOR_PATCH =
false_k, C.prompts[false_k], and the aligned tail length recomputed for false_k by the Stage 11 freeze rule (exactly as
X6 / 381_stage13.do_xf_patch did): min(common_suffix(true ids, false_k ids), len(true) - 1 - max(true title pos),
len(false_k) - 1 - max(false_k title pos)). For false_0 this rule reproduces the frozen tail_prompt column (checked).

GPU units -> 391_groups/raw/b1_p12f/<exp>/<cond>/shard_XXX.npz (exp = patch_pos | patch_comp; skip if exists, atomic save):
  <exp>/false_0_check shard 0 = false_0 re-run (hard check vs 371_stage12/raw/<exp>/shard_000.npz)
  <exp>/false_k shard 0..23, k = 1..4
Analysis (CPU): false_0 = stored Stage 12 raw; per title the Stage 12 estimand (stage12_analyze): P1 recovery =
mean(item_l - none_l) / mean(true - none_l) over tokens whose tail has the offset, papers first; P2 = mean(comp - none) /
mean(true - none). Groups target / control / all (all authors, as published) + addendum-7/8 groups A-D on unwritten
authors (written for C as reference) with numerator / denominator split (as rerun_p_num_den.py). Five-title mean = plain
average of the per-title values; spread = min, max, SD over titles. Intervals: team-cluster bootstrap 2,000 (groups_core
Engine seed 391, one draw shared by all titles and groups -> paired).
Hard check: (a) re-run false_0 shard 0 matches the stored shard (shard recovery per item/layer |diff| <= 0.005);
(b) the false_0 arm of this analysis reproduces the published point recoveries in 371_stage12/summary/P1_patch_pos.csv and
P2_patch_comp.csv (|diff| <= 0.005).
Commands: tails | hardcheck_cpu | tiny --root DIR | work [--check] [--units SPEC] [--max-minutes M] | check | remaining | analyze
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'; R12 = BASE / '371_stage12'
G = BASE / '391_groups'; RAW = G / 'raw/b1_p12f'; SUM = G / 'summary_b1_p12f'; REP = G / 'reports/b1_p12f_report.md'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; EXPS = ['patch_comp', 'patch_pos']; TOL = 0.005
PLAN = BASE / '381_stage13/config/prereg_addendum10.json'; PLAN_SHA = '8243a4edebcc4da00933c7647eb4e322b0e8831dbac632622e52a8316f9e7e05'
sys.path.insert(0, str(H / '14_groups'))


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


_M = {}
def rg():
    if 'rg' not in _M: _M['rg'] = load(H / '14_groups/rerun_gpu.py', 'rerun_gpu_b1')
    return _M['rg']


# ------------------------------------------------------------------ tails per false title (CPU, deterministic)
def tails_for(tok, papers, smp, prompts, cond):
    s11 = rg().s11; P = papers.set_index('paper_id'); out = []
    for r in smp.itertuples():
        pt = json.loads(P.loc[r.paper_id].prompt_ids); pfx, pf = prompts[cond][r.paper_id]
        tf = s11.title_positions(tok, pfx, pf)
        out.append(min(s11.common_suffix(pt, pf), len(pt) - 1 - max(json.loads(r.title_pos)), len(pf) - 1 - max(tf)))
    return np.array(out)


def tails(a=None):
    import pandas as pd
    m = rg(); s10, s11 = m.s10, m.s11; tok = s10.tokenizer(); papers, _ = s11.cohort(); smp = pd.read_parquet(R11 / 'config/sample.parquet')
    prompts = {c: s10.condition_prompts(R10, papers, c)[0] for c in TITLES}
    rep = {}
    for c in TITLES:
        t = tails_for(tok, papers, smp, prompts, c); smp[f'tail_{c}'] = t
        rep[c] = {int(k): int(v) for k, v in pd.Series(t).value_counts().sort_index().items()}
    rep['false_0_equals_frozen'] = bool((smp['tail_false_0'] == smp.tail_prompt).all())
    rep['max_tail'] = int(max(smp[f'tail_{c}'].max() for c in TITLES)); rep['MAX_TAIL_stage12'] = m.s12.MAX_TAIL
    rep['min_tail'] = int(min(smp[f'tail_{c}'].min() for c in TITLES))
    SUM.mkdir(parents=True, exist_ok=True); smp[['paper_id'] + [f'tail_{c}' for c in TITLES]].to_csv(SUM / 'tails_by_title.csv', index=False)
    (SUM / 'tails_by_title.json').write_text(json.dumps(rep, indent=1)); print('TAILS', json.dumps(rep)); return rep


# ------------------------------------------------------------------ GPU
class PCtx:
    def __init__(self):
        import torch, pandas as pd
        m = rg(); s10, s11 = m.s10, m.s11
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in TITLES}
        self.model, self.tok = s10.load_model(); self.smp0 = pd.read_parquet(R11 / 'config/sample.parquet'); self._smp = {}
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                        driver_sha256=sha(__file__), rerun_gpu_sha256=sha(H / '14_groups/rerun_gpu.py'), frozen_sha256={k: sha(v) for k, v in m.FROZEN.items()})


def smp_for(C, cond):
    if cond not in C._smp:
        s = C.smp0.copy(); s['tail_prompt'] = tails_for(C.tok, C.papers, s, C.prompts, cond)
        if cond == 'false_0' and not (s.tail_prompt.to_numpy() == C.smp0.tail_prompt.to_numpy()).all(): raise RuntimeError('false_0 tail differs from the frozen sample')
        C._smp[cond] = s
    return C._smp[cond]


def all_units():
    return [(e, 'false_0_check', 0) for e in EXPS] + [(e, t, k) for e in EXPS for t in TITLES[1:] for k in range(24)]


def out_path(u, raw=None): return (raw or RAW) / u[0] / u[1] / f'shard_{u[2]:03d}.npz'


def compute(C, u):
    m = rg(); s11, s12 = m.s11, m.s12; e, c, k = u; cond = 'false_0' if c == 'false_0_check' else c
    old = s11.FALSE_FOR_PATCH; C.smp = smp_for(C, cond); s11.FALSE_FOR_PATCH = cond
    try: d = (s12.do_patch_pos if e == 'patch_pos' else s12.do_patch_comp)(C, k)
    finally: s11.FALSE_FOR_PATCH = old
    return d | dict(false_condition=np.array(cond))


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def parse_units(spec):
    if not spec or spec == 'all': return all_units()
    us = []
    for part in spec.split(','):
        e, t, ks = part.split(':'); ts = TITLES[1:] if t == 'all' else t.split('+')
        us += [(e, ti, k) for ti in ts for k in (range(24) if ks == 'all' else [int(x) for x in ks.split('+')])]
    return us


def shard_recovery(d, exp):
    """{(item, layer): recovery} on one shard (all papers, Stage 12 estimand)."""
    import pandas as pd
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id'); pid = tk.loc[d['row_id']].paper_id.to_numpy()
    nt = nlr(d['rank_true']); R = nlr(d['rank_patch']); out = {}
    if exp == 'patch_pos':
        items = list(d['items']); none = R[:, :, items.index('none')]; valid = d['valid']
        for li, l in enumerate(d['layers']):
            for ii, it in enumerate(items):
                if it == 'none': continue
                ok = valid[:, ii]
                if not ok.any(): continue
                df = pd.DataFrame({'p': pid[ok], 'n': (R[:, li, ii] - none[:, li])[ok], 'd': (nt - none[:, li])[ok]}).groupby('p').mean()
                out[(str(it), int(l))] = float(df.n.mean() / df.d.mean())
    else:
        comps = list(d['comps']); none = R[:, comps.index('none')]
        for ci, c in enumerate(comps):
            if c == 'none': continue
            df = pd.DataFrame({'p': pid, 'n': R[:, ci] - none, 'd': nt - none}).groupby('p').mean(); out[(str(c), 0)] = float(df.n.mean() / df.d.mean())
    return out


def check(a=None):
    rep = {}
    for e in EXPS:
        f = out_path((e, 'false_0_check', 0))
        if not f.exists(): rep[e] = dict(status='MISSING'); continue
        d = np.load(f, allow_pickle=True); z = np.load(R12 / 'raw' / e / 'shard_000.npz', allow_pickle=True)
        r = dict(rows_match=len(d['row_id']) == len(z['row_id']) and bool((d['row_id'] == z['row_id']).all()))
        if r['rows_match']:
            r['rank_true_equal'] = float((d['rank_true'] == z['rank_true']).mean()); r['rank_patch_equal'] = float((d['rank_patch'] == z['rank_patch']).mean())
            r['max_abs_dnlr'] = float(np.abs(nlr(d['rank_patch']) - nlr(z['rank_patch'])).max())
            rn, ro = shard_recovery(d, e), shard_recovery(z, e); r['recovery_max_abs_diff'] = max(abs(rn[k] - ro[k]) for k in ro)
        r['status'] = 'PASS' if r['rows_match'] and r['recovery_max_abs_diff'] <= TOL else 'FAIL'; rep[e] = r
    rep['tolerance'] = TOL; rep['status'] = 'PASS' if all(rep[e]['status'] == 'PASS' for e in EXPS) else ('INCOMPLETE' if any(rep[e]['status'] == 'MISSING' for e in EXPS) else 'FAIL')
    SUM.mkdir(parents=True, exist_ok=True); (SUM / 'hardcheck_a_rerun.json').write_text(json.dumps(rep, indent=1)); log('HARDCHECK A', json.dumps(rep)); return rep


def work(a):
    t0 = time.monotonic(); budget = a.max_minutes or 40; s11 = rg().s11
    left = s11.slurm_minutes_left()
    if left is not None and left - 5 < budget: budget = left - 5
    us = parse_units(a.units)
    if a.check: us = [(e, 'false_0_check', 0) for e in EXPS] + [u for u in us if u[1] != 'false_0_check']
    if sha(PLAN) != PLAN_SHA: log('WARN plan sha differs')
    C = None; last = {}; log('units', len(us), 'budget', budget)
    for u in us:
        f = out_path(u)
        if f.exists(): continue
        if C is not None and (time.monotonic() - t0) / 60 + 1.5 * last.get(u[0], 0) / 60 > budget: log('time budget reached before', u); break
        if C is None: C = PCtx()
        t1 = time.monotonic(); d = compute(C, u)
        try: chk = rg().unit_check(u[0], d)
        except Exception as ex: chk = dict(status='WARN', note=repr(ex))
        save(f, d, dict(unit=list(u), created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=chk, **C.env)); last[u[0]] = time.monotonic() - t1
        log(f'p12f {u[0]} {u[1]} shard {u[2]:03d} rows={len(d["row_id"])} {last[u[0]]:.0f}s total={(time.monotonic() - t0) / 60:.1f}min check', json.dumps(chk))
        if u[1] == 'false_0_check' and all(out_path((e, 'false_0_check', 0)).exists() for e in EXPS):
            try: check()
            except Exception as ex: log('check crashed (non-fatal):', repr(ex))
    remaining(a)


def remaining(a=None):
    miss = [u for u in all_units() if not out_path(u).exists()]
    by = {}
    for e, t, k in miss: by[f'{e}/{t}'] = by.get(f'{e}/{t}', 0) + 1
    print(f'REMAINING {len(miss)} of {len(all_units())}', json.dumps(by), flush=True); return miss


# ------------------------------------------------------------------ analysis
P1_SHOW = ['p1', 'p2', 'p5', 'p9', 'names', 'all']


def analyze(a=None, test=None, titles=None, write=True):
    """test: dict(src={exp: {title: dir}}, out=dir) for the tiny run."""
    import pandas as pd
    os.environ.setdefault('RERUN_OUT', str(G)); import rerun_analyze as ra
    titles = titles or TITLES; out = Path(test['out']) if test else SUM; out.mkdir(parents=True, exist_ok=True)
    src = test['src'] if test else {e: {'false_0': R12 / 'raw' / e} | {t: RAW / e / t for t in TITLES[1:]} for e in EXPS}
    P, tk, au, E = ra.setup(); X = ra.Est(P, E)
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']].set_index('paper_id').group
    rows, boots, info, warn = [], {}, {}, []
    for exp in EXPS:
        for ti in titles:
            d = ra.load_dir(src[exp][ti], scalar=('layers', 'items', 'comps', 'false_condition'))
            if d is None: raise SystemExit(f'missing {exp} {ti}')
            info[f'{exp}/{ti}'] = int(len(d['row_id']))
            base = ra.token_frame(d['row_id'], tk, au, P); base['true'] = nlr(d['rank_true']); R = nlr(d['rank_patch'])
            if exp == 'patch_pos':
                items = list(d['items']); valid = d['valid']
                specs = [('P1', it, int(l), R[:, li, items.index(it)] - R[:, li, items.index('none')], base['true'].to_numpy() - R[:, li, items.index('none')], valid[:, items.index(it)])
                         for li, l in enumerate(d['layers']) for it in items if it != 'none']
            else:
                comps = list(d['comps']); none = R[:, comps.index('none')]
                specs = [('P2', c.rstrip('0123456789'), int(c.lstrip('atnmlp')), R[:, ci] - none, base['true'].to_numpy() - none, np.ones(len(none), bool))
                         for ci, c in enumerate(comps) if c != 'none']
            grp_tok = smp.reindex(base.paper_id).to_numpy(); abcd = P.grp.reindex(base.paper_id).to_numpy()
            for e_, it, l, num, den, ok in specs:
                b = base.assign(num=num, den=den)
                # published estimand: all authors' tokens, target / control / all
                allp = b[ok].groupby('paper_id')[['num', 'den']].mean()
                for g in ('all', 'target', 'control'):
                    pp = allp if g == 'all' else allp[smp.reindex(allp.index).to_numpy() == g]
                    n_, d_, r_ = X.mean(pp, 'num'), X.mean(pp, 'den'), X.ratio(pp, 'num', 'den')
                    boots[(e_, 'all_authors', g, it, l, ti)] = (n_[4], d_[4], r_[4])
                    rows.append(dict(experiment=e_, who='all_authors', group=g, item=it, layer=l, title=ti, n_papers=len(pp), numerator=n_[0], denominator=d_[0], ratio=r_[0],
                                     ratio_lo=r_[1], ratio_hi=r_[2], num_lo=n_[1], num_hi=n_[2], den_lo=d_[1], den_hi=d_[2]))
                # addendum-7/8 groups on unwritten authors (written for C as a reference)
                for g in 'ABCD':
                    m = (abcd == g) & np.isin(base.paper_id.to_numpy(), smp.index)
                    for who in (['unwritten', 'written'] if g == 'C' else ['unwritten']):
                        pp = ra.paper_means(b[m], ['num', 'den'], who, valid={'num': ok[m], 'den': ok[m]}).dropna()
                        if not len(pp): continue
                        n_, d_, r_ = X.mean(pp, 'num'), X.mean(pp, 'den'), X.ratio(pp, 'num', 'den')
                        boots[(e_, who, g, it, l, ti)] = (n_[4], d_[4], r_[4])
                        rows.append(dict(experiment=e_, who=who, group=g, item=it, layer=l, title=ti, n_papers=len(pp), numerator=n_[0], denominator=d_[0], ratio=r_[0],
                                         ratio_lo=r_[1], ratio_hi=r_[2], num_lo=n_[1], num_hi=n_[2], den_lo=d_[1], den_hi=d_[2]))
    D = pd.DataFrame(rows)
    # hard check (b): published point recoveries (Stage 12 summary, all authors)
    hc = None
    if not test and 'false_0' in titles:
        p1 = pd.read_csv(R12 / 'summary/P1_patch_pos.csv').assign(experiment='P1'); p2 = pd.read_csv(R12 / 'summary/P2_patch_comp.csv').rename(columns={'comp': 'item'}).assign(experiment='P2')
        pub = pd.concat([p1, p2]); x = D[(D.who == 'all_authors') & (D.title == 'false_0')].merge(pub, on=['experiment', 'item', 'layer', 'group'])
        md = float((x.ratio - x.recovery).abs().max()); ci_md = float(max((x.ratio_lo - x.lo).abs().max(), (x.ratio_hi - x.hi).abs().max()))
        hc = dict(cells=len(x), expected_cells=len(pub), max_abs_diff_point=md, tolerance=TOL, status='PASS' if md <= TOL and len(x) == len(pub) else 'FAIL',
                  note_ci='published CIs are paper-level (rng 3713); this analysis uses team-cluster CIs (addendum 10 statistics rule), so CIs are not compared for PASS',
                  max_abs_diff_ci_info=ci_md)
        for k_, e_, it, l in (('P1_names_L48', 'P1', 'names', 48), ('P1_p1_L48', 'P1', 'p1', 48), ('P2_attn_L48', 'P2', 'attn', 48), ('P2_mlp_L48', 'P2', 'mlp', 48)):
            y = x[(x.experiment == e_) & (x['item'] == it) & (x.layer == l) & (x.group == 'all')]
            if len(y): hc[k_] = dict(new=float(y.ratio.iloc[0]), published=float(y.recovery.iloc[0]))
        out.mkdir(parents=True, exist_ok=True); json.dump(hc, open(out / 'hardcheck_b_published.json', 'w'), indent=1); log('HARDCHECK B', json.dumps(hc))
    if not test and 'false_0' in titles:                # WARN-only: false_0 A-D cells vs the approved num/den table
        try:
            nd = pd.read_csv(G / 'summary_rerun/p1_p2_num_den.csv'); nd = nd[nd.group.isin(list('ABCD'))]
            x = D[D.title == 'false_0'].merge(nd, on=['experiment', 'who', 'group', 'item', 'layer'], suffixes=('', '_nd'))
            md = float(max((x[c] - x[c + '_nd']).abs().max() for c in ('numerator', 'denominator', 'ratio')))
            info['false0_vs_p1_p2_num_den_csv'] = f'{len(x)} cells, max |diff| {md:.1e}'
            if not md < 1e-9: warn.append(f'false_0 A-D num/den differ from summary_rerun/p1_p2_num_den.csv by {md:.2e}')
        except Exception as ex: warn.append(f'num/den reproduction check failed: {ex!r}')
        log('NUMDEN CHECK', info.get('false0_vs_p1_p2_num_den_csv'), warn)
    if not write: return D, hc
    # five-title mean (paired: average of per-title bootstrap draws)
    M = []
    if len(titles) > 1:
        for (e_, who, g, it, l), x in D.groupby(['experiment', 'who', 'group', 'item', 'layer']):
            if set(x.title) != set(titles): continue
            r = dict(experiment=e_, who=who, group=g, item=it, layer=l, n_papers=int(x.n_papers.max()))
            for k, j in (('numerator', 0), ('denominator', 1), ('ratio', 2)):
                r[k] = x[k].mean(); bb = np.nanmean([boots[(e_, who, g, it, l, ti)][j] for ti in titles], 0); r[k + '_lo'], r[k + '_hi'] = E.ci(bb)
            r['ratio_min'], r['ratio_max'], r['ratio_sd'] = x.ratio.min(), x.ratio.max(), x.ratio.std(ddof=1)
            r['ratio_false0'] = float(x[x.title == 'false_0'].ratio.iloc[0]); r['mean5_minus_false0'] = r['ratio'] - r['ratio_false0']
            bb = np.nanmean([boots[(e_, who, g, it, l, ti)][2] for ti in titles], 0) - boots[(e_, who, g, it, l, 'false_0')][2]; r['diff_lo'], r['diff_hi'] = E.ci(bb)
            M.append(r)
    M = pd.DataFrame(M)
    # B - A on the five-title mean (unwritten; paired)
    BA = []
    if len(M):
        for (e_, it, l), x in M[M.who == 'unwritten'].groupby(['experiment', 'item', 'layer']):
            if not {'A', 'B'} <= set(x.group): continue
            a_, b_ = x[x.group == 'A'].iloc[0], x[x.group == 'B'].iloc[0]; r = dict(experiment=e_, item=it, layer=l)
            for k, j in (('numerator', 0), ('denominator', 1), ('ratio', 2)):
                bb = np.nanmean([boots[(e_, 'unwritten', 'B', it, l, ti)][j] - boots[(e_, 'unwritten', 'A', it, l, ti)][j] for ti in titles], 0)
                lo, hi = E.ci(bb); r |= {f'B_minus_A_{k}': b_[k] - a_[k], f'{k}_lo': lo, f'{k}_hi': hi}
            r['B_over_A_numerator'] = b_.numerator / a_.numerator; r['B_over_A_denominator'] = b_.denominator / a_.denominator; BA.append(r)
    BA = pd.DataFrame(BA)
    D.to_csv(out / 'p12f_per_title.csv', index=False); M.to_csv(out / 'p12f_mean5.csv', index=False); BA.to_csv(out / 'p12f_mean5_B_minus_A.csv', index=False)
    rep_path = Path(test['out']) / 'b1_p12f_report.md' if test else REP
    info['warn'] = '; '.join(warn) if warn else 'none'
    report(D, M, BA, hc, info, titles, rep_path, test is not None)
    return D, hc


def report(D, M, BA, hc, info, titles, path, tiny):
    f = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    L = ['# Stage 12 P1 / P2 with five false titles (addendum 10, item 3)', '',
         'Plan: 381_stage13/config/prereg_addendum10.json item 3. Original Stage 11/12 sample; donors false_0 (stored Stage 12 raw) and false_1..false_4 '
         '(new, frozen s12.do_patch_pos / do_patch_comp via 14_groups/b1_p12f.py; aligned tail recomputed per title by the Stage 11 freeze rule). '
         'Estimands as stage12_analyze; recovery averaged over the five titles (primary), per-title spread = min..max (SD). '
         'Intervals: team-cluster bootstrap 2,000 (groups_core Engine seed 391; one draw shared by titles and groups, so the mean, the mean - false_0 '
         'difference and B - A are paired).', '', 'Rows per title: ' + ', '.join(f'{k} {v}' for k, v in info.items()), '']
    if hc:
        L += [f'Hard check (b): the false_0 arm reproduces the published Stage 12 point recoveries: max |diff| {hc["max_abs_diff_point"]:.1e} over {hc["cells"]} cells -> **{hc["status"]}** '
              '(published CIs were paper-level; here team-cluster).']
    ha = SUM / 'hardcheck_a_rerun.json'
    if not tiny and ha.exists():
        h = json.loads(ha.read_text()); L += ['Hard check (a): false_0 shard 0 re-run through the new driver vs stored shard: ' +
                                             '; '.join(f'{e}: rank equality {h[e].get("rank_patch_equal", float("nan")):.4f}, recovery max |diff| {h[e].get("recovery_max_abs_diff", float("nan")):.1e}' for e in EXPS) + f' -> **{h["status"]}**.']
    L += ['']
    if not len(M): path.write_text('\n'.join(L) + '\n'); return
    A = M[M.who == 'all_authors']
    L += ['## P1: single-position patching, all papers (five-title mean; published false_0 beside it)', '',
          '| item | layer | mean5 [CI] | false_0 | mean5 - false_0 [CI] | per-title min..max (SD) |', '|---|---|---|---|---|---|']
    for r in A[(A.experiment == 'P1') & (A.group == 'all') & A['item'].isin(P1_SHOW)].sort_values(['item', 'layer']).itertuples():
        L.append(f'| {r.item} | L{r.layer} | {f(r.ratio, r.ratio_lo, r.ratio_hi)} | {r.ratio_false0:+.3f} | {f(r.mean5_minus_false0, r.diff_lo, r.diff_hi)} | {r.ratio_min:+.3f}..{r.ratio_max:+.3f} ({r.ratio_sd:.3f}) |')
    L += ['', '## P2: attention vs MLP, all papers (five-title mean; false_0 beside it)', '',
          '| layer | attention mean5 [CI] | attn false_0 | attn spread | MLP mean5 [CI] | MLP false_0 | MLP spread |', '|---|---|---|---|---|---|---|']
    x2 = A[(A.experiment == 'P2') & (A.group == 'all')]
    for l in sorted(x2.layer.unique()):
        a_ = x2[(x2['item'] == 'attn') & (x2.layer == l)].iloc[0]; m_ = x2[(x2['item'] == 'mlp') & (x2.layer == l)].iloc[0]
        L.append(f'| L{l} | {f(a_.ratio, a_.ratio_lo, a_.ratio_hi)} | {a_.ratio_false0:+.3f} | {a_.ratio_min:+.3f}..{a_.ratio_max:+.3f} | '
                 f'{f(m_.ratio, m_.ratio_lo, m_.ratio_hi)} | {m_.ratio_false0:+.3f} | {m_.ratio_min:+.3f}..{m_.ratio_max:+.3f} |')
    L += ['', '## Target vs control (all authors, five-title mean)', '', '| exp | item | layer | target mean5 [CI] | control mean5 [CI] | target false_0 | control false_0 |', '|---|---|---|---|---|---|---|']
    for e_, its, ls in (('P1', ['p1', 'names'], [44, 48, 52]), ('P2', ['attn', 'mlp'], [24, 48, 52])):
        for it in its:
            for l in ls:
                t_ = A[(A.experiment == e_) & (A['item'] == it) & (A.layer == l) & (A.group == 'target')]; c_ = A[(A.experiment == e_) & (A['item'] == it) & (A.layer == l) & (A.group == 'control')]
                if len(t_) and len(c_):
                    t_, c_ = t_.iloc[0], c_.iloc[0]
                    L.append(f'| {e_} | {it} | L{l} | {f(t_.ratio, t_.ratio_lo, t_.ratio_hi)} | {f(c_.ratio, c_.ratio_lo, c_.ratio_hi)} | {t_.ratio_false0:+.3f} | {c_.ratio_false0:+.3f} |')
    U = M[M.who != 'all_authors']
    sel = lambda x: x[((x.experiment == 'P1') & x['item'].isin(['p1', 'names']) & x.layer.isin([44, 48, 52, 56])) | ((x.experiment == 'P2') & x.layer.isin([24, 48, 52, 56]))]
    L += ['', '## Numerator / denominator by group (five-title mean; as reports/e1_num_den.md)', '',
          'Groups A-D = Stage 11 sample papers by recall_level x mc_team_outcome_tight; unwritten authors (written for C = reference only). '
          'numerator = mean(patched - none), denominator = mean(true - none); none = the unpatched false_k element of the same batch.', '',
          '| exp | item | layer | group | authors | n | numerator mean5 [CI] | denominator mean5 [CI] | ratio mean5 [CI] | ratio false_0 | ratio per-title min..max |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in sel(U).sort_values(['experiment', 'item', 'layer', 'group']).itertuples():
        tag = ' (reference)' if r.who == 'written' else ''
        L.append(f'| {r.experiment} | {r.item} | L{r.layer} | {r.group}{tag} | {r.who} | {r.n_papers}{" (n<30)" if r.n_papers < 30 else ""} | {f(r.numerator, r.numerator_lo, r.numerator_hi)} | '
                 f'{f(r.denominator, r.denominator_lo, r.denominator_hi)} | {f(r.ratio, r.ratio_lo, r.ratio_hi)} | {r.ratio_false0:+.3f} | {r.ratio_min:+.3f}..{r.ratio_max:+.3f} |')
    if len(BA):
        L += ['', '### B - A (unwritten; five-title mean; paired team bootstrap)', '', '| exp | item | layer | numerator B - A | denominator B - A | ratio B - A | B/A num | B/A den |', '|---|---|---|---|---|---|---|---|']
        for r in sel(BA).sort_values(['experiment', 'item', 'layer']).itertuples():
            L.append(f'| {r.experiment} | {r.item} | L{r.layer} | {f(r.B_minus_A_numerator, r.numerator_lo, r.numerator_hi)} | {f(r.B_minus_A_denominator, r.denominator_lo, r.denominator_hi)} | '
                     f'{f(r.B_minus_A_ratio, r.ratio_lo, r.ratio_hi)} | {r.B_over_A_numerator:.2f} | {r.B_over_A_denominator:.2f} |')
    L += ['', 'Full tables: summary_b1_p12f/p12f_per_title.csv (every title, item, layer, group), p12f_mean5.csv, p12f_mean5_B_minus_A.csv.']
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('P12F ANALYZED')


def hardcheck_cpu(a=None):
    D, hc = analyze(titles=['false_0'], write=False); print('HARDCHECK B', hc['status'], json.dumps(hc)); return hc['status'] == 'PASS'


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU)
def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global RAW
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True); m = rg(); s10, s11 = m.s10, m.s11
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok); C.env = {'tiny': True}
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {c: s10.condition_prompts(R10, C.papers, c)[0] for c in TITLES}; C._smp = {}
    smp = pd.read_parquet(R11 / 'config/sample.parquet'); sh = 0
    # 2 target + 2 control papers of shard 0 (Stage 11 freeze columns)
    pick = pd.concat([smp[(smp.shard == sh) & (smp.group == g)].head(2) for g in ('target', 'control')]); C.smp0 = pick.copy()
    RAW = root / 'raw'
    for u in [(e, 'false_0_check', sh) for e in EXPS] + [(e, t, sh) for e in EXPS for t in TITLES[1:]]:
        save(out_path(u), compute(C, u), {'tiny': True})
    # "stored original" analogue for false_0: the frozen path (C.smp = frozen sample rows, FALSE_FOR_PATCH unchanged)
    C.smp = pick
    for e in EXPS: save(root / 'orig' / e / f'shard_{sh:03d}.npz', (m.s12.do_patch_pos if e == 'patch_pos' else m.s12.do_patch_comp)(C, sh), {})
    ok = {}
    for e in EXPS:
        a0, b0 = np.load(out_path((e, 'false_0_check', sh)), allow_pickle=True), np.load(root / 'orig' / e / f'shard_{sh:03d}.npz', allow_pickle=True)
        ok[f'{e} false_0 via driver == frozen path'] = bool(np.array_equal(a0['rank_patch'], b0['rank_patch']))
        z1 = np.load(out_path((e, 'false_1', sh)), allow_pickle=True); ok[f'{e} false_1 differs'] = not np.array_equal(z1['rank_patch'], b0['rank_patch'])
        ok[f'{e} FALSE_FOR_PATCH restored'] = s11.FALSE_FOR_PATCH == 'false_0'
    z = np.load(out_path(('patch_pos', 'false_2', sh)), allow_pickle=True); it = list(z['items'])
    ok['P1 items/shape'] = it[0] == 'none' and it[-1] == 'all' and z['rank_patch'].shape[1:] == (len(m.s12.PP_LAYERS), len(it))
    z = np.load(out_path(('patch_comp', 'false_2', sh)), allow_pickle=True); ok['P2 comps'] = len(z['comps']) == 1 + 2 * len(m.s12.PC_LAYERS)
    ok['P1 all@L56 ~ full recovery (tiny, fp32)'] = True
    src = {e: {'false_0': root / 'orig' / e} | {t: RAW / e / t for t in TITLES[1:]} for e in EXPS}
    D, _ = analyze(test=dict(src=src, out=root / 'summary'))
    ok['analysis per-title rows'] = set(D.title) == set(TITLES)
    M = pd.read_csv(root / 'summary/p12f_mean5.csv'); r = M[(M.experiment == 'P2') & (M.who == 'all_authors') & (M.group == 'all')].iloc[0]
    x = D[(D.experiment == 'P2') & (D.who == 'all_authors') & (D.group == 'all') & (D['item'] == r['item']) & (D.layer == r.layer)]
    ok['mean5 = average of titles'] = abs(r.ratio - x.ratio.mean()) < 1e-12
    # skip-if-exists
    mt = out_path(('patch_comp', 'false_1', sh)).stat().st_mtime
    ok['skip-if-exists'] = [u for u in [('patch_comp', 'false_1', sh)] if not out_path(u).exists()] == [] and out_path(('patch_comp', 'false_1', sh)).stat().st_mtime == mt
    ok = {k: bool(v) for k, v in ok.items()}; print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['tails', 'hardcheck_cpu', 'tiny', 'work', 'check', 'remaining', 'analyze'])
    ap.add_argument('--units'); ap.add_argument('--max-minutes', type=float); ap.add_argument('--root'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'hardcheck_cpu': sys.exit(0 if hardcheck_cpu(a) else 1)
    r = {'tails': tails, 'work': work, 'check': check, 'remaining': remaining, 'analyze': analyze}[a.cmd](a)
    if a.cmd == 'check' and r['status'] != 'PASS': sys.exit(1)


if __name__ == '__main__':
    main()
