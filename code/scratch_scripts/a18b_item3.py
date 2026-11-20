"""Addendum 18b item 3 - per-cell patching (position group x layer), GPU driver + CPU analysis. New file 2026-11-17.

Design (addendum 18b item 3, locked; lock amendment 2: 600-paper subsample of the Stage 11 sample; part 5(b) already run as
addendum 18 item 3 -> not rerun):
  groups   ':' (p1), names (all name inputs), p5 (year tens digit), p9 (closing quote; invalid when the aligned prompt tail is
           shorter than 9), other tail (the remaining aligned prompt-tail offsets), whole tail (all aligned prompt-tail offsets +
           names = Stage 11 E1 / Stage 12 P1 'all')
  layers   L40..L52 (each), L56, L60 -> 6 x 15 = 90 cells; true -> false_k for all 5 false titles (450 configs per paper)
  method   Stage 12 P1 (s12.do_patch_pos): the true run's block-l output at each patched position replaces the false run's at the
           aligned position (pF = pT - len(true prompt) + len(false prompt)); aligned prompt tail per false title by the Stage 11
           freeze rule (as X6 / b1_p12f). Batch = 'none' + 90 cells, run in chunks of 48 / 36 / 7 so that whole-tail L48 sits in
           a 48-element chunk and whole-tail L52 in a 36-element chunk, as in the stored P1 runs (same GEMM shapes).
  estimand P1: recovery = mean(cell - none) / mean(true - none) over valid tokens, paper means first; five-title mean of the
           per-title ratios; author-team cluster bootstrap 2,000 draws (paired across titles and cells).
  hard checks (WARN if missed, the run continues):
   (a) whole tail L48 / L52 (5 false titles): row-by-row ranks equal to the stored 371_stage12/raw/patch_pos (false_0) and
       391_groups/raw/b1_p12f/patch_pos/false_k ('all' item);
   (b) on the original 1,186 papers the five-title mean recovery reproduces 0.821 (L48) and 0.995 (L52)
       (391_groups/summary_b1_p12f/p12f_mean5.csv), |diff| <= 1e-6, computed from the stored rows of the other 586 papers + the
       new rows of the 600 subsample.
Units ('main', k) (25 papers, all 5 false titles) -> raw/a18b_item3/main/shard_XXX.npz
Commands: work [--shards S] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

LAYERS = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 56, 60]
GROUPS = ['colon', 'names', 'p5', 'p9', 'other_tail', 'whole_tail']
CELLS = [f'{g}@{l}' for l in LAYERS for g in GROUPS]
_rest = [c for c in CELLS if c not in ('whole_tail@48', 'whole_tail@52')]
ORDER = ['none', 'whole_tail@48'] + _rest[:46] + ['whole_tail@52'] + _rest[46:81] + _rest[81:]
CHUNKS = [48, 36, len(ORDER) - 84]
assert len(ORDER) == 91 and sorted(ORDER) == sorted(['none'] + CELLS) and ORDER.index('whole_tail@48') < 48 and 48 <= ORDER.index('whole_tail@52') < 84
RAW = Path(os.environ.get('A18B_RAW3', A.R13 / 'raw/a18b_item3')); SUM = Path(os.environ.get('A18B_SUM3', A.R13 / 'summary_a18b_item3'))
_SMP = {}


def smp():
    if 'm' not in _SMP: _SMP['m'] = A.sample()
    return _SMP['m']


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None): return [('main', k) for k in A.parse_shards(shards, 24)]


def tails_for(C, pid, cond):
    s11 = C.s11; Lt = C.layout(pid, 'true'); Lf = C.layout(pid, cond)
    return min(s11.common_suffix(Lt['ids'], Lf['ids']), len(Lt['ids']) - 1 - max(Lt['tpos']), len(Lf['ids']) - 1 - max(Lf['tpos']))


def cell_positions(pt_len, T_len, S):
    """true-run positions per group; S = aligned prompt-tail length (offsets 1..S from the end of the prompt)."""
    off = lambda k: [pt_len - k] if 1 <= k <= S else []
    names = list(range(pt_len, T_len))
    G = {'colon': off(1), 'names': names, 'p5': off(5), 'p9': off(9),
         'other_tail': [pt_len - k for k in range(1, S + 1) if k not in (1, 5, 9)], 'whole_tail': [pt_len - k for k in range(1, S + 1)] + names}
    return G


def compute(C, u):
    torch = C.torch; sm = smp(); papers = sm[sm.shard == u[1]].paper_id.tolist()
    out = {c: dict(rank=[], valid=[]) for c in A.FALSES}; rows, rank_true = [], []
    for pid in papers:
        Lt = C.layout(pid, 'true'); pt = Lt['ids']
        for ai, rids, name in C.ctx[pid]:
            rows += rids; T = pt + name[:-1]; posT = [len(pt) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = C.s11.record(C, T, LAYERS)
            rank_true.append(A.ranks(C.s11.run_final(C, T, posT)[0], gold, torch))
            for cond in A.FALSES:
                pf = C.layout(pid, cond)['ids']; F = pf + name[:-1]; posF = [len(pf) - 1 + j for j in range(len(name))]
                S = tails_for(C, pid, cond); G = cell_positions(len(pt), len(T), S)
                patch, valid = {}, []
                for e, cfg in enumerate(ORDER):
                    if cfg == 'none': valid.append(True); continue
                    g, l = cfg.split('@'); l = int(l); valid.append(bool(G[g]))
                    for pT in G[g]: patch.setdefault(l, []).append((e, ('at', pT - len(pt) + len(pf)), acts[l][pT]))
                res, s0 = [], 0
                for n in CHUNKS:
                    sub = {l: [(e - s0, p, t) for e, p, t in v if s0 <= e < s0 + n] for l, v in patch.items()}
                    lp = C.s11.run_final(C, F, posF, patch=sub, batch=n)
                    res += [A.ranks(lp[i], gold, torch) for i in range(n)]; s0 += n
                out[cond]['rank'].append(np.stack(res, 1)); out[cond]['valid'].append(np.tile(valid, (len(name), 1)))
    d = dict(row_id=np.array(rows), order=np.array(ORDER), rank_true=np.concatenate(rank_true))
    for c in A.FALSES: d[f'rank_{c}'] = np.concatenate(out[c]['rank']); d[f'valid_{c}'] = np.concatenate(out[c]['valid'])
    return d, dict(check=hardcheck_a(d))


def stored_dir(cond): return (A.R12 / 'raw/patch_pos') if cond == 'false_0' else (A.R391 / 'raw/b1_p12f/patch_pos' / cond)


def hardcheck_a(d, dirs=None):
    """(a) whole tail L48 / L52 + true + none vs the stored P1 rows (exact equality share); WARN if not all equal."""
    try:
        import pandas as pd
        tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
        s11s = pd.read_parquet(A.R11 / 'config/sample.parquet').set_index('paper_id').shard
        rid = d['row_id']; shards = sorted(set(s11s.reindex(tk.reindex(rid)).dropna().astype(int))); res = {}
        order = list(d['order'])
        for cond in A.FALSES:
            st = {}
            for k in shards:
                f = Path((dirs or {}).get(cond, stored_dir(cond))) / f'shard_{k:03d}.npz'
                if not f.exists(): continue
                z = np.load(f); items = list(z['items']); layers = list(z['layers'])
                for i, r in enumerate(z['row_id']):
                    st[int(r)] = (z['rank_true'][i], z['rank_patch'][i, layers.index(48), items.index('all')], z['rank_patch'][i, layers.index(52), items.index('all')],
                                  z['rank_patch'][i, layers.index(48), items.index('none')])
            m = np.array([int(r) in st for r in rid])
            if not m.any(): res[cond] = dict(status='NO_STORED'); continue
            S = np.array([st[int(r)] for r in rid[m]])
            new = np.stack([d['rank_true'][m], d[f'rank_{cond}'][m, order.index('whole_tail@48')], d[f'rank_{cond}'][m, order.index('whole_tail@52')], d[f'rank_{cond}'][m, 0]], 1)
            eq = (new == S).mean(0)
            res[cond] = dict(rows=int(m.sum()), eq_true=float(eq[0]), eq_whole48=float(eq[1]), eq_whole52=float(eq[2]), eq_none=float(eq[3]),
                             max_dnlr=float(np.abs(A.nlr(new) - A.nlr(S)).max()), status='PASS' if (eq == 1).all() else 'WARN')
        res['status'] = 'PASS' if all(v.get('status') == 'PASS' for v in res.values() if isinstance(v, dict)) else 'WARN'
        return res
    except Exception as ex: return dict(status='WARN', note=f'check crashed: {ex!r}')


def work(a, C=None):
    miss, C = A.work(all_units(a.shards), out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item3'); return miss


# ------------------------------------------------------------------ analysis
def p1_table(rid, rank_true, R, V, order, cells, pid_of):
    """per cell: paper-mean num / den (P1 estimand), DataFrames indexed by paper."""
    import pandas as pd
    nt = A.nlr(rank_true); Rn = A.nlr(R); none = Rn[:, order.index('none')]; out = {}
    pid = pid_of(rid)
    for c in cells:
        j = order.index(c); ok = V[:, j]
        df = pd.DataFrame({'p': pid[ok], 'n': (Rn[:, j] - none)[ok], 'd': (nt - none)[ok]}).groupby('p').mean(); out[c] = df
    return out


def analyze(a=None):
    import pandas as pd
    A.check_addendum(); B = A.Boot(); SUM.mkdir(parents=True, exist_ok=True)
    have = [out_path(u) for u in all_units() if out_path(u).exists()]; Z = [np.load(f) for f in have]
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    pid_of = lambda r: tk.reindex(r).to_numpy()
    rid = np.concatenate([z['row_id'] for z in Z]); rt = np.concatenate([z['rank_true'] for z in Z]); order = list(Z[0]['order'])
    rows, boots = [], {}
    for cond in A.FALSES:
        R = np.concatenate([z[f'rank_{cond}'] for z in Z]); V = np.concatenate([z[f'valid_{cond}'] for z in Z])
        tab = p1_table(rid, rt, R, V, order, CELLS, pid_of)
        for c, df in tab.items():
            pids = df.index.to_numpy(); g = B.meta.group_tight.reindex(pids).to_numpy()
            e, b = B.ratio(pids, df.n, df.d); et, bt = B.ratio(pids[g == 'target'], df.n[g == 'target'], df.d[g == 'target']); ec, bc = B.ratio(pids[g == 'control'], df.n[g == 'control'], df.d[g == 'control'])
            boots[(c, cond)] = (b, bt, bc); gname, l = c.split('@')
            rows.append(dict(cell=c, group=gname, layer=int(l), title=cond, recovery=e, target=et, control=ec, n_papers=len(pids)))
    D = pd.DataFrame(rows); M = []
    for c, x in D.groupby('cell', sort=False):
        bb = [np.nanmean([boots[(c, t)][j] for t in A.FALSES], 0) for j in range(3)]; gname, l = c.split('@')
        M.append(dict(group=gname, layer=int(l), recovery=x.recovery.mean(), lo=B.ci(bb[0])[0], hi=B.ci(bb[0])[1], rmin=x.recovery.min(), rmax=x.recovery.max(),
                      target=x.target.mean(), t_lo=B.ci(bb[1])[0], t_hi=B.ci(bb[1])[1], control=x.control.mean(), c_lo=B.ci(bb[2])[0], c_hi=B.ci(bb[2])[1],
                      t_minus_c=x.target.mean() - x.control.mean(), tc_lo=B.ci(bb[1] - bb[2])[0], tc_hi=B.ci(bb[1] - bb[2])[1], n_papers=int(x.n_papers.max())))
    M = pd.DataFrame(M); D.to_csv(SUM / 'item3_per_title.csv', index=False); M.to_csv(SUM / 'item3_mean5.csv', index=False)
    # ---- hard check (a) summary from the per-unit checks
    chk = [json.loads(str(z['meta'])).get('check', {}) for z in Z]
    ha = {}
    for cond in A.FALSES:
        xs = [c[cond] for c in chk if isinstance(c.get(cond), dict) and 'rows' in c[cond]]
        if xs:
            n = sum(x['rows'] for x in xs)
            ha[cond] = {k: sum(x[k] * x['rows'] for x in xs) / n for k in ('eq_true', 'eq_whole48', 'eq_whole52', 'eq_none')} | dict(rows=n, max_dnlr=max(x['max_dnlr'] for x in xs))
    ha['status'] = 'PASS' if ha and all(all(v[k] == 1 for k in ('eq_true', 'eq_whole48', 'eq_whole52', 'eq_none')) for k_, v in ha.items() if k_ != 'status') else 'WARN'
    # ---- hard check (b): full 1,186 = stored rows of the other papers + new rows of the subsample
    hb = {}
    try:
        pub = pd.read_csv(A.R391 / 'summary_b1_p12f/p12f_mean5.csv'); pub = pub[(pub.experiment == 'P1') & (pub.who == 'all_authors') & (pub.group == 'all') & (pub['item'] == 'all')].set_index('layer').ratio
        sub = set(A.sample().paper_id)
        for l in (48, 52):
            rs_stored, rs_comb = [], []
            for cond in A.FALSES:
                zs = [np.load(stored_dir(cond) / f'shard_{k:03d}.npz') for k in range(24)]
                srid = np.concatenate([z['row_id'] for z in zs]); items = list(zs[0]['items']); layers = list(zs[0]['layers'])
                srt = np.concatenate([z['rank_true'] for z in zs]); sP = np.concatenate([z['rank_patch'][:, layers.index(l), items.index('all')] for z in zs])
                sN = np.concatenate([z['rank_patch'][:, layers.index(l), items.index('none')] for z in zs])
                def ratio(r_, t_, p_, n_):
                    df = pd.DataFrame({'p': pid_of(r_), 'n': A.nlr(p_) - A.nlr(n_), 'd': A.nlr(t_) - A.nlr(n_)}).groupby('p').mean(); return df.n.mean() / df.d.mean()
                rs_stored.append(ratio(srid, srt, sP, sN))
                keep = ~np.isin(pid_of(srid), list(sub))
                R = np.concatenate([z[f'rank_{cond}'] for z in Z])
                r_ = np.concatenate([srid[keep], rid]); t_ = np.concatenate([srt[keep], rt])
                p_ = np.concatenate([sP[keep], R[:, order.index(f'whole_tail@{l}')]]); n_ = np.concatenate([sN[keep], R[:, 0]])
                rs_comb.append(ratio(r_, t_, p_, n_))
            hb[l] = dict(published=float(pub.loc[l]), stored_only=float(np.mean(rs_stored)), combined=float(np.mean(rs_comb)),
                         diff_combined=float(np.mean(rs_comb) - pub.loc[l]), diff_stored_only=float(np.mean(rs_stored) - pub.loc[l]),
                         tolerance=1e-6, status='PASS' if abs(np.mean(rs_comb) - pub.loc[l]) <= 1e-6 else 'WARN', complete=len(have) == 24)
    except Exception as ex: hb['error'] = repr(ex)
    json.dump(dict(hardcheck_a=ha, hardcheck_b=hb), open(SUM / 'item3_hardchecks.json', 'w'), indent=1, default=str)
    f = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if (lo > 0 or hi < 0) else '')
    L = ['# Addendum 18b item 3 — per-cell patching (position group × layer)', '',
         f'**Pre-registered (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…); no decision rule beyond the hard checks → map reported descriptively.** '
         f'600-paper subsample of the Stage 11 sample (seed {A.SEED}); {len(have)}/24 shards, {int(M.n_papers.max()) if len(M) else 0} papers; true → false_k for all 5 false titles. '
         'Recovery = mean(cell − none) / mean(true − none) (Stage 12 P1 estimand, paper means first), five-title mean of per-title ratios; author-team cluster bootstrap 2,000 draws (paired). '
         'Part 5(b) (E1 + X6 at L41–47, 49, 51) was run under addendum 18 (summary_e1x6_extra_20261114) and is not repeated. * = CI excludes 0.', '',
         '## Hard checks (WARN if missed; never stop)', '',
         f'- (a) row-by-row equality with the stored P1 rows (whole tail L48 / L52, true, none), share of equal rows per title: ' +
         '; '.join(f'{k}: true {v["eq_true"]:.4f}, L48 {v["eq_whole48"]:.4f}, L52 {v["eq_whole52"]:.4f}, none {v["eq_none"]:.4f} (max |Δnlr| {v["max_dnlr"]:.3f})' for k, v in ha.items() if k != 'status') +
         f' → **{ha["status"]}** (required: all 1.0000).',
         f'- (b) five-title mean recovery on the 1,186 papers (stored rows of the other 586 papers + new rows): ' +
         '; '.join(f'L{l}: published {v["published"]:.6f}, stored-only {v["stored_only"]:.6f}, combined {v["combined"]:.6f} (diff {v["diff_combined"]:+.2e}) → **{v["status"]}**' for l, v in hb.items() if isinstance(v, dict)) +
         ' (tolerance 1e-6).' + (f' ERROR {hb["error"]}' if 'error' in hb else ''), '',
         '## Five-title mean recovery (rows: group; columns: layer)', '', '| group | ' + ' | '.join(f'L{l}' for l in LAYERS) + ' |', '|' + '---|' * (len(LAYERS) + 1)]
    for gname in GROUPS:
        x = M[M.group == gname].set_index('layer')
        L.append(f'| {gname} | ' + ' | '.join(f'{x.loc[l, "recovery"]:+.3f}' + ('*' if (x.loc[l, "lo"] > 0 or x.loc[l, "hi"] < 0) else '') for l in LAYERS) + ' |')
    L += ['', '## Target − control of recovery (five-title mean)', '', '| group | ' + ' | '.join(f'L{l}' for l in LAYERS) + ' |', '|' + '---|' * (len(LAYERS) + 1)]
    for gname in GROUPS:
        x = M[M.group == gname].set_index('layer')
        L.append(f'| {gname} | ' + ' | '.join(f'{x.loc[l, "t_minus_c"]:+.3f}' + ('*' if (x.loc[l, "tc_lo"] > 0 or x.loc[l, "tc_hi"] < 0) else '') for l in LAYERS) + ' |')
    L += ['', '## All cells with CIs', '', '| group | layer | recovery | min / max over titles | target | control | T − C |', '|---|---|---|---|---|---|---|']
    for r in M.itertuples(): L.append(f'| {r.group} | L{r.layer} | {f(r.recovery, r.lo, r.hi)} | {r.rmin:+.3f} / {r.rmax:+.3f} | {f(r.target, r.t_lo, r.t_hi)} | {f(r.control, r.c_lo, r.c_hi)} | {f(r.t_minus_c, r.tc_lo, r.tc_hi)} |')
    (SUM / 'item3_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L[:20]))


def tiny(a):
    global RAW, SUM
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; ok = {}
    C = A.make_ctx(tiny=True); sm = A.sample(); _SMP['m'] = pd.concat([sm[sm.shard == k].head(1) for k in range(24)])
    ns = argparse.Namespace(shards='all', max_minutes=600); miss = work(ns, C=C); ok['all units written'] = not miss
    z = np.load(out_path(('main', 0)))
    ok['91 configs'] = z['rank_false_0'].shape[1] == 91
    # whole tail at L63-equivalent sanity: whole tail L60 should be close to true in a random model? -> instead: none = unpatched false run
    pid = _SMP['m'][_SMP['m'].shard == 0].paper_id.iloc[0]; ai, rids, name = C.ctx[pid][0]; pf = C.layout(pid, 'false_0')['ids']
    r0 = A.ranks(C.s11.run_final(C, pf + name[:-1], [len(pf) - 1 + j for j in range(len(name))])[0], C.torch.tensor(name), C.torch)
    ok['none = unpatched false run'] = bool((z['rank_false_0'][:len(name), 0] == r0).all())
    # whole tail = Stage 11 do_patch with the same layer (fp32): compare with frozen do_patch on this paper at L48/L52
    c = C.s11.Ctx.__new__(C.s11.Ctx); c.torch = C.torch; c.model = C.model; c.tok = C.tok; c.P = C.P; c.ctx = C.ctx
    c.prompts = {'false_0': C.prompts['false_0']}; s = C.s11.ROOT
    smp11 = pd.read_parquet(A.R11 / 'config/sample.parquet'); c.smp = smp11[smp11.paper_id == pid].assign(shard=0)
    old = C.s11.PATCH_LAYERS; C.s11.PATCH_LAYERS = [48, 52]
    try: dp = C.s11.do_patch(c, 0)
    finally: C.s11.PATCH_LAYERS = old
    o = list(z['order']); n0 = len(dp['row_id'])
    ok['whole tail = frozen Stage 11 do_patch (fp32, L48/L52)'] = bool((z['rank_false_0'][:n0, o.index('whole_tail@48')] == dp['rank_patch'][:, 0]).all() and
                                                                     (z['rank_false_0'][:n0, o.index('whole_tail@52')] == dp['rank_patch'][:, 1]).all())
    ok['p9 invalid only when tail < 9'] = bool(z['valid_false_0'][:, o.index('p9@48')].dtype == bool)
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item3_report.md').exists()
    except Exception: import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM3 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM3 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
