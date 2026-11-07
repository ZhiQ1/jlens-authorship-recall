"""Addendum 10 (batch 1) item 2: X7 knockout on the false run with all five false titles.

Plan: /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum10.json (sha256 8243a4ed...), item "2 X7 five false
titles". The frozen 13_stage13/381_stage13.py is loaded by path and NOT edited; its unit function do_ko_false (the Stage 11
knockout on the false-title run) is called unchanged with cond = false_1..false_4 (it already takes the condition).

GPU units (raw/b1_x7f/<cond>/shard_XXX.npz, skip if exists, atomic save):
  false_0_check shard 0  = false_0 re-run through this driver; compared with the stored raw/ko_false/false_0/shard_000.npz
  false_k shard 0..23    k = 1..4
Analysis (CPU), the published stage13_x7_analyze.py estimand per title k (X6 convention: each title uses its own
denominator mean(true - false_k); false_0 = Stage 11 raw/patch, false_k = X6 raw/xf_patch/false_k):
  T_k(l) = mean(kT64 - kT_l) / den_k     (Stage 11 knockout, true run)
  F_k(l) = mean(kF64_k - kF_k,l) / den_k (knockout on the false_k run)
  S_k = T_k - F_k; five-title mean = plain average of the five per-title values (bootstrap: average of the per-title draws,
  one shared team draw -> paired). Decision (addendum 3 thresholds) on the MEAN: S(L52) <= 0.05 and S(L0) >= 0.5.
  Sensitivity: the same with the false_0 denominator for every title.
Hard check (addendum 10): (a) the false_0 re-run reproduces the stored shard (F loss per layer |diff| <= 0.005);
(b) the false_0 arm of this analysis reproduces summary_x7/x7_knockout.csv (T, F, S and CIs, |diff| <= 0.005), incl.
control S(L52) = 0.051.
Commands: hardcheck_cpu | tiny --root DIR | work [--check] [--units SPEC] [--max-minutes M] | check | remaining | analyze
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; RAW = ROOT / 'raw/b1_x7f'; SUM = ROOT / 'summary_b1_x7f'; REP = ROOT / 'reports/b1_x7f_report.md'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; NB = 2000; TOL = 0.005
PLAN = ROOT / 'config/prereg_addendum10.json'; PLAN_SHA = '8243a4edebcc4da00933c7647eb4e322b0e8831dbac632622e52a8316f9e7e05'
FROZEN = H / '13_stage13/381_stage13.py'


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


_S13 = {}
def s13():
    if 'm' not in _S13: _S13['m'] = load(FROZEN, 's13')
    return _S13['m']


# ------------------------------------------------------------------ GPU
def all_units():
    return [('false_0_check', 0)] + [(t, k) for t in TITLES[1:] for k in range(24)]


def out_path(u, raw=None): return (raw or RAW) / u[0] / f'shard_{u[1]:03d}.npz'


def compute(C, u):
    cond = 'false_0' if u[0] == 'false_0_check' else u[0]
    return s13().do_ko_false(C, cond, u[1])


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def parse_units(spec):
    if not spec or spec == 'all': return all_units()
    us = []
    for part in spec.split(','):
        t, ks = part.split(':'); us += [(t, k) for k in (range(24) if ks == 'all' else [int(x) for x in ks.split('+')])]
    return us


def shard_loss(rank_ko, layers, rows, pz):
    """paper-level loss fraction per layer on one shard: mean_p(k64 - k_l) / mean_p(true - false_0)."""
    import pandas as pd
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    pid = tk.loc[rows].paper_id.to_numpy(); L = list(layers)
    den = pd.DataFrame({'p': tk.loc[pz['row_id']].paper_id.to_numpy(), 'g': nlr(pz['rank_true']) - nlr(pz['rank_false'])}).groupby('p').g.mean().mean()
    df = pd.DataFrame({'p': pid, **{f'k{l}': nlr(rank_ko[:, i]) for i, l in enumerate(L)}}).groupby('p').mean()
    return {int(l): float((df.k64 - df[f'k{l}']).mean() / den) for l in L if l != 64}


def check(a=None, raw=None, stored=None):
    """hard check (a): false_0 re-run vs stored ko_false/false_0 shard 0."""
    raw = raw or RAW; stored = stored or ROOT / 'raw/ko_false/false_0'
    f = out_path(('false_0_check', 0), raw)
    if not f.exists(): log('check: no re-run yet'); return None
    d = np.load(f); z = np.load(stored / 'shard_000.npz'); pz = np.load(R11 / 'raw/patch/shard_000.npz')
    rep = dict(rows_match=len(d['row_id']) == len(z['row_id']) and bool((d['row_id'] == z['row_id']).all()))
    if rep['rows_match']:
        rep['rank_equal'] = float((d['rank_ko'] == z['rank_ko']).mean())
        rep['max_abs_dnlr'] = float(np.abs(nlr(d['rank_ko']) - nlr(z['rank_ko'])).max())
        ln, lo = shard_loss(d['rank_ko'], d['layers'], d['row_id'], pz), shard_loss(z['rank_ko'], z['layers'], z['row_id'], pz)
        rep['F_new'], rep['F_stored'] = ln, lo; rep['F_max_abs_diff'] = max(abs(ln[l] - lo[l]) for l in ln)
    rep['tolerance'] = TOL
    rep['status'] = 'PASS' if rep['rows_match'] and rep['F_max_abs_diff'] <= TOL else 'FAIL'
    p = (raw.parent.parent / 'summary_b1_x7f' if raw == RAW else raw) / 'hardcheck_a_rerun.json'; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rep, indent=1)); log('HARDCHECK A', rep['status'], json.dumps({k: v for k, v in rep.items() if k not in ('F_new', 'F_stored')}))
    return rep


def work(a):
    t0 = time.monotonic(); budget = a.max_minutes or 40; S11 = s13().s11
    left = S11.slurm_minutes_left()
    if left is not None and left - 5 < budget: budget = left - 5
    us = parse_units(a.units)
    if a.check and ('false_0_check', 0) not in us: us = [('false_0_check', 0)] + us
    C = None; last = 0.0; sh = sha(PLAN)
    if sh != PLAN_SHA: log('WARN plan sha differs', sh)
    log('units', len(us), 'budget', budget)
    for u in us:
        f = out_path(u)
        if f.exists(): continue
        if C is not None and (time.monotonic() - t0) / 60 + 1.5 * last / 60 > budget: log('time budget reached before', u); break
        if C is None: C = s13().Ctx(); C.env |= dict(driver_sha256=sha(__file__), frozen_sha256=sha(FROZEN))
        t1 = time.monotonic(); d = compute(C, u)
        save(f, d, dict(unit=list(u), created=time.strftime('%Y-%m-%dT%H:%M:%S'), **C.env)); last = time.monotonic() - t1
        log(f'x7f {u[0]} shard {u[1]:03d} rows={len(d["row_id"])} {last:.0f}s total={(time.monotonic() - t0) / 60:.1f}min')
        if u[0] == 'false_0_check':
            try: check()
            except Exception as ex: log('check crashed (non-fatal):', repr(ex))
    remaining(a)


def remaining(a=None):
    miss = [u for u in all_units() if not out_path(u).exists()]
    print(f'REMAINING {len(miss)} of {len(all_units())}', miss[:6], flush=True); return miss


# ------------------------------------------------------------------ analysis
def load_dir(d, keys):
    fs = sorted(Path(d).glob('shard_*.npz')); zs = [np.load(f) for f in fs]
    if not zs: return None, None, 0
    return {k: np.concatenate([z[k] for z in zs]) for k in keys}, [int(x) for x in zs[0]['layers']], len(fs)


def sources(test_root=None):
    if test_root:
        r = Path(test_root)
        return dict(patch=r / 'R11/raw/patch', knockout=r / 'R11/raw/knockout', e2=None,
                    xf={t: r / 'xf_patch' / t for t in TITLES[1:]}, kf={'false_0': r / 'ko_false/false_0'} | {t: r / 'b1_x7f' / t for t in TITLES[1:]},
                    sample=None, out=r / 'summary_b1_x7f', rep=r / 'b1_x7f_report.md', published=None)
    return dict(patch=R11 / 'raw/patch', knockout=R11 / 'raw/knockout', e2=R11 / 'summary/E2_knockout.csv',
                xf={t: ROOT / 'raw/xf_patch' / t for t in TITLES[1:]}, kf={'false_0': ROOT / 'raw/ko_false/false_0'} | {t: RAW / t for t in TITLES[1:]},
                sample=R11 / 'config/sample.parquet', out=SUM, rep=REP, published=ROOT / 'summary_x7/x7_knockout.csv')


def analyze(a=None, test_root=None, titles=None, write=True):
    import pandas as pd
    src = sources(test_root); titles = titles or TITLES; out = src['out']; out.mkdir(parents=True, exist_ok=True)
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    grp = pd.read_parquet(src['sample'] or R11 / 'config/sample.parquet')[['paper_id', 'group']].set_index('paper_id').group
    warn = []; info = {}
    d0, _, n0 = load_dir(src['patch'], ['row_id', 'rank_true', 'rank_false'])
    kT, kl, nT = load_dir(src['knockout'], ['row_id', 'rank_ko'])
    base = pd.DataFrame({'row_id': d0['row_id'], 'true': nlr(d0['rank_true'])})
    t = pd.DataFrame({'row_id': kT['row_id'], **{f'T{l}': nlr(kT['rank_ko'][:, i]) for i, l in enumerate(kl)}})
    m = base.merge(t, on='row_id'); info['shards'] = {'patch': n0, 'knockout': nT}
    for ti in titles:
        if ti == 'false_0': fr = pd.DataFrame({'row_id': d0['row_id'], 'false_0': nlr(d0['rank_false']), 'rf_false_0': d0['rank_false']})
        else:
            dx, _, nx = load_dir(src['xf'][ti], ['row_id', 'rank_true', 'rank_false']); info['shards'][f'xf_{ti}'] = nx
            fr = pd.DataFrame({'row_id': dx['row_id'], ti: nlr(dx['rank_false']), 'rf_' + ti: dx['rank_false'], 'true_' + ti: nlr(dx['rank_true'])})
        kF, klF, nF = load_dir(src['kf'][ti], ['row_id', 'rank_ko']); info['shards'][f'ko_{ti}'] = nF
        if kF is None: raise SystemExit(f'no knockout data for {ti}')
        if klF != kl: warn.append(f'{ti}: knockout layers differ')
        f = pd.DataFrame({'row_id': kF['row_id'], 'kF64_' + ti: kF['rank_ko'][:, -1], **{f'F{l}_{ti}': nlr(kF['rank_ko'][:, i]) for i, l in enumerate(klF)}})
        n_before = len(m); m = m.merge(fr, on='row_id').merge(f, on='row_id')
        if len(m) != n_before: warn.append(f'{ti}: rows {n_before} -> {len(m)} after merge')
        eq = float((m['kF64_' + ti] == m['rf_' + ti]).mean()); info[f'kF64_equals_false_run_{ti}'] = eq
        if eq < 1: warn.append(f'{ti}: nothing-blocked element equals the plain false run on {eq:.4f} of rows (batching; also in the published run)')
        if 'true_' + ti in m:
            dt = float(np.abs(m['true_' + ti] - m['true']).max()); info[f'true_run_max_diff_{ti}'] = dt
            if dt > 0: warn.append(f'{ti}: X6 true run differs from Stage 11 by up to {dt:.3g} (log10 rank)')
    m['paper_id'] = toks.loc[m.row_id].paper_id.to_numpy()
    keep = ['true'] + [f'T{l}' for l in kl] + titles + [f'F{l}_{ti}' for ti in titles for l in kl]
    pp = m[['paper_id'] + keep].groupby('paper_id').mean()
    allp = list(pp.index); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in allp]))
    W = pd.DataFrame(np.random.default_rng(17).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes].T, index=allp)
    e11 = pd.read_csv(src['e2']) if src['e2'] else None
    rows = []; groups = ('target', 'control', 'all')
    for g in groups:
        s = pp if g == 'all' else pp[grp.reindex(pp.index).to_numpy() == g]
        if not len(s): continue
        w = W.loc[s.index].to_numpy()
        dens = {ti: (s['true'] - s[ti]).to_numpy() for ti in titles}
        for l in kl:
            if l == 64: continue
            nt = (s['T64'] - s[f'T{l}']).to_numpy(); bts = {}
            for ti in titles:
                den = dens[ti]; dw = den @ w; nf = (s[f'F64_{ti}'] - s[f'F{l}_{ti}']).to_numpy()
                bt, bf = (nt @ w) / dw, (nf @ w) / dw; bts[ti] = (bt, bf)
                r = dict(group=g, start_layer=l, title=ti, n_papers=len(s), den=den.mean(), T=nt.mean() / den.mean(), F=nf.mean() / den.mean())
                r['S'] = r['T'] - r['F']
                for k, b in (('T', bt), ('F', bf), ('S', bt - bf)): r[k + '_lo'], r[k + '_hi'] = np.percentile(b, [2.5, 97.5])
                # sensitivity: false_0 denominator for every title
                d0_ = dens[titles[0]]; r['S_den0'] = (nt.mean() - nf.mean()) / d0_.mean()
                rows.append(r)
            if len(titles) > 1:
                pr = [x for x in rows if x['group'] == g and x['start_layer'] == l and x['title'] in titles]
                r = dict(group=g, start_layer=l, title='mean5', n_papers=len(s), den=np.mean([x['den'] for x in pr]),
                         T=np.mean([x['T'] for x in pr]), F=np.mean([x['F'] for x in pr]), S=np.mean([x['S'] for x in pr]), S_den0=np.mean([x['S_den0'] for x in pr]))
                mb = {k: np.mean([bts[ti][0] if k == 'T' else (bts[ti][1] if k == 'F' else bts[ti][0] - bts[ti][1]) for ti in titles], 0) for k in ('T', 'F', 'S')}
                for k, b in mb.items(): r[k + '_lo'], r[k + '_hi'] = np.percentile(b, [2.5, 97.5])
                Sv = [x['S'] for x in pr]; r['S_min'], r['S_max'], r['S_sd'] = min(Sv), max(Sv), float(np.std(Sv, ddof=1))
                rows.append(r)
    D = pd.DataFrame(rows)
    if e11 is not None:
        x = D[D.title == titles[0]].merge(e11.rename(columns={'loss_fraction': 'T_stage11'})[['group', 'start_layer', 'T_stage11']], on=['group', 'start_layer'], how='left')
        dT = float(np.nanmax(np.abs(x['T'] - x['T_stage11']))); info['T_vs_stage11_E2_maxdiff_false0'] = dT
        if not dT < 1e-6: warn.append(f'false_0 T differs from Stage 11 E2 by up to {dT:.2e}')
    # hard check (b): false_0 arm vs the published table
    hc = None
    if src['published'] is not None and titles[0] == 'false_0':
        P = pd.read_csv(src['published']); x = D[D.title == 'false_0'].merge(P, on=['group', 'start_layer'], suffixes=('', '_pub'))
        cols = ['T', 'F', 'S', 'T_lo', 'T_hi', 'F_lo', 'F_hi', 'S_lo', 'S_hi']
        md = float(max(np.abs(x[c] - x[c + '_pub']).max() for c in cols))
        c52 = x[(x.group == 'control') & (x.start_layer == 52)].iloc[0]
        hc = dict(cells=len(x), expected_cells=len(P), max_abs_diff=md, tolerance=TOL, control_S_L52_new=float(c52.S), control_S_L52_published=float(c52.S_pub),
                  status='PASS' if (md <= TOL and len(x) == len(P)) else 'FAIL')
        json.dump(hc, open(out / 'hardcheck_b_published.json', 'w'), indent=1); log('HARDCHECK B', json.dumps(hc))
    if not write: return D, hc, warn
    D.to_csv(out / 'x7f_knockout.csv', index=False)
    # verdicts
    ver = {}
    for ti in titles + (['mean5'] if len(titles) > 1 else []):
        for g in groups:
            x = D[(D.group == g) & (D.title == ti)].set_index('start_layer')
            if not len(x): continue
            ver.setdefault(ti, {})[g] = dict(S_L52=float(x.loc[52, 'S']), S_L52_lo=float(x.loc[52, 'S_lo']), S_L52_hi=float(x.loc[52, 'S_hi']), S_L0=float(x.loc[0, 'S']),
                                             holds=bool(x.loc[52, 'S'] <= 0.05 and x.loc[0, 'S'] >= 0.5), S_L52_den0=float(x.loc[52, 'S_den0']))
    json.dump(dict(verdict=ver, warn=warn, info=info, hardcheck_b=hc, plan_sha256=sha(PLAN) if PLAN.exists() else None), open(out / 'x7f_verdict.json', 'w'), indent=1, default=float)
    fm = lambda r, k: f'{r[k]:+.3f} [{r[k + "_lo"]:+.3f}, {r[k + "_hi"]:+.3f}]'
    L = ['# Stage 13 X7 with five false titles (addendum 10, item 2)', '',
         'Plan: config/prereg_addendum10.json item 2 (thresholds of addendum 3 applied to the mean of the five false titles; per-title values beside it; '
         'the published false_0-only verdict is the reference). Same estimand as reports/x7_report.md, per title k with its own denominator mean(true - false_k) '
         '(as X6); mean5 = plain average of the five per-title values; 95% team-cluster bootstrap (2,000 draws, one draw shared by all titles -> paired).', '',
         f'Data: Stage 11 patch {info["shards"]["patch"]} / knockout {info["shards"]["knockout"]} shards; ' + ', '.join(f'{k} {v}' for k, v in info['shards'].items() if k not in ('patch', 'knockout')) + f'; {len(pp)} papers.', '']
    if hc: L += [f'Hard check (b): the false_0 arm reproduces summary_x7/x7_knockout.csv: max |diff| {hc["max_abs_diff"]:.1e} over {hc["cells"]} cells (T, F, S + CIs); control S(L52) {hc["control_S_L52_new"]:.3f} vs published {hc["control_S_L52_published"]:.3f} -> **{hc["status"]}**.']
    ha = ROOT / 'summary_b1_x7f/hardcheck_a_rerun.json'
    if not test_root and ha.exists():
        h = json.loads(ha.read_text()); L += [f'Hard check (a): false_0 shard 0 re-run through the new driver vs stored ko_false shard: rank equality {h.get("rank_equal", float("nan")):.4f}, F loss max |diff| {h.get("F_max_abs_diff", float("nan")):.1e} -> **{h["status"]}**.']
    L += ['']
    if warn: L += ['**WARN** (non-fatal): ' + '; '.join(warn), '']
    L += ['## Pre-registered check on the five-title mean (primary)', '', 'Claim holds if S(L52) <= 0.05 and S(L0) >= 0.5.', '',
          '| group | S(L52) mean5 [CI] | S(L0) mean5 | per-title S(L52) (false_0..4) | verdict mean5 | false_0 verdict (published reference) | S(L52) mean5, false_0 denominator |', '|---|---|---|---|---|---|---|']
    for g in groups:
        if 'mean5' not in ver or g not in ver['mean5']: continue
        v = ver['mean5'][g]; v0 = ver['false_0'][g]
        L.append(f'| {g} | {v["S_L52"]:+.3f} [{v["S_L52_lo"]:+.3f}, {v["S_L52_hi"]:+.3f}] | {v["S_L0"]:+.3f} | ' + ', '.join(f'{ver[ti][g]["S_L52"]:+.3f}' for ti in titles) +
                 f' | **{"HOLDS" if v["holds"] else "DOES NOT HOLD"}** | {"HOLDS" if v0["holds"] else "DOES NOT HOLD"} (S(L52) {v0["S_L52"]:+.3f}) | {v["S_L52_den0"]:+.3f} |')
    L += ['', 'Per-title verdicts: ' + '; '.join(f'{ti}: ' + ', '.join(f'{g} {"holds" if ver[ti][g]["holds"] else "fails"}' for g in groups if g in ver[ti]) for ti in titles), '']
    for g in groups:
        if not len(D[D.group == g]): continue
        L += [f'## {g}: five-title mean', '', '| block from | T (true run) | F (false runs) | S = T - F | S per title min..max (SD) |', '|---|---|---|---|---|']
        for r in D[(D.group == g) & (D.title == 'mean5')].to_dict('records'):
            L.append(f'| L{r["start_layer"]} | {fm(r, "T")} | {fm(r, "F")} | {fm(r, "S")} | {r["S_min"]:+.3f}..{r["S_max"]:+.3f} ({r["S_sd"]:.3f}) |')
        L += ['', f'### {g}: S per title', '', '| block from | ' + ' | '.join(titles) + ' |', '|---|' + '---|' * len(titles)]
        for l in [x for x in kl if x != 64]:
            L.append(f'| L{l} | ' + ' | '.join(fm(D[(D.group == g) & (D.title == ti) & (D.start_layer == l)].iloc[0], 'S') for ti in titles) + ' |')
        L += ['', 'denominator mean(true - false_k): ' + ', '.join(f'{ti} {D[(D.group == g) & (D.title == ti)].den.iloc[0]:.3f}' for ti in titles), '']
    src['rep'].parent.mkdir(parents=True, exist_ok=True); src['rep'].write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('X7F ANALYZED')
    return D, hc, warn


def hardcheck_cpu(a=None):
    """hard check (b) only: the false_0 arm of the new analysis vs the published table (needs no GPU data)."""
    D, hc, warn = analyze(titles=['false_0'], write=False)
    print('HARDCHECK B', hc['status'], json.dumps(hc)); return hc['status'] == 'PASS'


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU)
def tiny(a):
    """64 tiny layers (every frozen layer list / readout L63 used unchanged), real tokenizer, 3 papers of one Stage 11
    shard: Stage 11 E1 (false_0) + knockout, X6 xf_patch false_1..4, X7 ko_false false_0 + this driver's false_1..4 and the
    false_0 re-run -> check -> analysis on the tiny root -> skip-if-exists."""
    import torch, transformers, jlens, pandas as pd
    global RAW
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True); m = s13(); s11 = m.s11; s10 = m.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok); C.env = {'tiny': True}
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks)
    c11 = m.ctx11(C); sh = int(c11.smp.shard.iloc[0]); c11.smp = c11.smp[c11.smp.shard == sh].head(3).copy()
    full_smp = c11.smp
    save(root / f'R11/raw/patch/shard_{sh:03d}.npz', s11.do_patch(c11, sh), {}); save(root / f'R11/raw/knockout/shard_{sh:03d}.npz', s11.do_knockout(c11, sh), {})
    for ti in TITLES[1:]: c11.smp = full_smp; save(root / f'xf_patch/{ti}/shard_{sh:03d}.npz', m.do_xf_patch(c11, ti, sh), {})
    c11.smp = full_smp; save(root / f'ko_false/false_0/shard_{sh:03d}.npz', m.do_ko_false(C, 'false_0', sh), {})
    RAW = root / 'b1_x7f'
    for u in [('false_0_check', sh)] + [(ti, sh) for ti in TITLES[1:]]:
        c11.smp = full_smp; save(out_path(u), compute(C, u), {'tiny': True})
    ok = {}
    a0, b0 = np.load(out_path(('false_0_check', sh))), np.load(root / f'ko_false/false_0/shard_{sh:03d}.npz')
    ok['false_0 re-run == stored (same code, CPU)'] = bool(np.array_equal(a0['rank_ko'], b0['rank_ko']))
    z1 = np.load(out_path(('false_1', sh))); ok['false_1 differs from false_0'] = not np.array_equal(z1['rank_ko'], b0['rank_ko'])
    ok['layers'] = list(z1['layers']) == list(s11.KO_LAYERS) and str(z1['false_condition']) == 'false_1'
    D, hc, warn = analyze(test_root=root)
    ok['analysis rows'] = set(D.title) == set(TITLES + ['mean5'])
    x = D[(D.group == 'all') & (D.start_layer == 52)].set_index('title')
    ok['mean5 S = average of titles'] = abs(x.loc['mean5', 'S'] - x.loc[TITLES, 'S'].mean()) < 1e-12
    # skip-if-exists through the work loop (must not recompute; would need the GPU context)
    before = out_path(('false_1', sh)).stat().st_mtime
    work_skip = [u for u in [('false_1', sh)] if not out_path(u).exists()]; ok['skip-if-exists'] = (work_skip == []) and out_path(('false_1', sh)).stat().st_mtime == before
    ok = {k: bool(v) for k, v in ok.items()}; print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['hardcheck_cpu', 'tiny', 'work', 'check', 'remaining', 'analyze'])
    ap.add_argument('--units'); ap.add_argument('--max-minutes', type=float); ap.add_argument('--root'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'hardcheck_cpu': sys.exit(0 if hardcheck_cpu(a) else 1)
    r = {'work': work, 'check': check, 'remaining': remaining, 'analyze': analyze}[a.cmd](a)
    if a.cmd == 'check' and (r is None or r['status'] != 'PASS'): sys.exit(1)


if __name__ == '__main__':
    main()
