"""Addendum 18b item 4 - L57-L61 attention / MLP mean ablation (GPU driver + analysis). New file 2026-11-17.

Design (addendum 18b item 4, locked): at the name positions and the tail, the attention output or the MLP output of ONE layer
l in L57..L61 is replaced by a reference mean. Reference means: the 586 Stage 11 papers NOT in the 600-paper subsample
(independent half), 5 false-title conditions, same position, fixed before the main run (unit 'refmean'). Position roles:
prompt-tail offset p1..p9 from the end of the prompt (p1 = ':', p9 = closing quote when it is its own token) and 'name' (all
name input tokens after ':', pooled). Prompt-tail roles are counted once per (paper, condition) (first author context), name
inputs over every author context. 10 configs (5 layers x {attn, mlp}) + 'none', for the 6 title conditions (true, false_0..4).
Readout: final-output rank of every gold name token (teacher forcing, Stage 10 contexts); S = true - mean_k false_k (paper
means of log10(1/rank)); loss = S(none) - S(config). P2 (patching up to L56) is the reference (cited, not rerun).
Units: ('refmean', k) k = 0..23 over the reference set -> raw/a18b_item4/refmean/shard_XXX.npz (sums, counts)
       ('main', k)    k = 0..23 over the 600 subsample -> raw/a18b_item4/main/shard_XXX.npz
Check (WARN only): 'none' ranks under true / false_0 vs the stored Stage 11 E1 rank_true / rank_false of the same rows.
Commands: work [--shards S] [--max-minutes M] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

LAYERS = [57, 58, 59, 60, 61]; COMPS = ['attn', 'mlp']; ROLES = [f'p{k}' for k in range(1, 10)] + ['name']
CONFIGS = ['none'] + [f'{c}{l}' for l in LAYERS for c in COMPS]
RAW = Path(os.environ.get('A18B_RAW4', A.R13 / 'raw/a18b_item4')); SUM = Path(os.environ.get('A18B_SUM4', A.R13 / 'summary_a18b_item4'))
_SMP = {}


def smp(kind):
    if kind not in _SMP: _SMP[kind] = A.refset() if kind == 'refmean' else A.sample()
    return _SMP[kind]


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None):
    return [('refmean', k) for k in range(24)] + [('main', k) for k in A.parse_shards(shards, 24)]     # refmean always complete first


def roles_of(L, n_name_inputs):
    """positions and role index of the tail of one context: prompt tail after the title + name inputs."""
    ids = L['ids']; pos, rix = [], []
    for i in range(max(L['tpos']) + 1, len(ids)):
        r = f'p{len(ids) - i}'
        if r in ROLES: pos.append(i); rix.append(ROLES.index(r))
    for j in range(n_name_inputs): pos.append(len(ids) + j); rix.append(ROLES.index('name'))
    return pos, rix


def mod_of(C, comp, l): return C.model.layers[l].self_attn if comp == 'attn' else C.model.layers[l].mlp


def do_refmean(C, shard):
    torch = C.torch; d = C.model.layers[0].mlp.down_proj.out_features
    S = np.zeros((2, len(LAYERS), len(ROLES), d)); N = np.zeros((2, len(LAYERS), len(ROLES)))
    sm = smp('refmean'); papers = sm[sm.shard == shard].paper_id.tolist()
    for pid in papers:
        for cond in A.FALSES:
            L = C.layout(pid, cond)
            for ci_, (ai, rids, name) in enumerate(C.ctx[pid]):
                T = L['ids'] + name[:-1]; pos, rix = roles_of(L, len(name) - 1)
                rec, hs = {}, []
                for c in COMPS:
                    for l in LAYERS:
                        def hk(m_, i_, o, c=c, l=l):
                            t = o[0] if c == 'attn' else o; rec[(c, l)] = t[0, pos].float().cpu().numpy()
                        hs.append((mod_of(C, c, l), hk))
                A.final_logits(C, T, [len(T) - 1], hooks=hs)
                keep = [i for i, r in enumerate(rix) if ci_ == 0 or ROLES[r] == 'name']
                for a, c in enumerate(COMPS):
                    for b, l in enumerate(LAYERS):
                        v = rec[(c, l)]
                        for i in keep: S[a, b, rix[i]] += v[i]; N[a, b, rix[i]] += 1
    return dict(sums=S, counts=N, papers=np.array(papers), layers=np.array(LAYERS), roles=np.array(ROLES), comps=np.array(COMPS)), {}


_MEAN = {}
def ref_means(C):
    if 'm' not in _MEAN:
        fs = [out_path(('refmean', k)) for k in range(24)]
        miss = [str(f) for f in fs if not f.exists()]
        if miss: raise RuntimeError(f'reference means incomplete: {len(miss)} refmean shards missing')
        S = sum(np.load(f)['sums'] for f in fs); N = sum(np.load(f)['counts'] for f in fs)
        M = S / np.maximum(N, 1)[..., None]
        _MEAN['m'] = {(c, l): C.torch.tensor(M[a, b], dtype=C.dtype, device=A.s11().s10.layer_device(C.model, l))
                      for a, c in enumerate(COMPS) for b, l in enumerate(LAYERS)}
        _MEAN['n'] = N
    return _MEAN['m']


def do_main(C, shard):
    torch = C.torch; M = ref_means(C); sm = smp('main')
    out = {c: [] for c in A.CONDS}; rows = []
    for pid in sm[sm.shard == shard].paper_id:
        for ai, rids, name in C.ctx[pid]:
            rows += rids; gold = torch.tensor(name, device=C.model.input_device)
            for cond in A.CONDS:
                L = C.layout(pid, cond); T = L['ids'] + name[:-1]; pos, rix = roles_of(L, len(name) - 1)
                outpos = [len(L['ids']) - 1 + j for j in range(len(name))]
                hs = []
                for e, cfg in enumerate(CONFIGS):
                    if cfg == 'none': continue
                    c = cfg.rstrip('0123456789'); l = int(cfg[len(c):])
                    def hk(m_, i_, o, e=e, c=c, l=l):
                        t = o[0] if c == 'attn' else o; t[e, pos] = M[(c, l)][rix].to(t.device, t.dtype); return o
                    hs.append((mod_of(C, c, l), hk))
                lg = A.final_logits(C, T, outpos, batch=len(CONFIGS), hooks=hs)
                out[cond].append(np.stack([A.ranks(lg[i], gold, torch) for i in range(len(CONFIGS))], 1))
    d = dict(row_id=np.array(rows), configs=np.array(CONFIGS), **{f'rank_{c}': np.concatenate(v) for c, v in out.items()})
    return d, dict(check=check_vs_e1(d))


def check_vs_e1(d, stored_dir=None):
    """WARN-only: 'none' ranks vs the stored Stage 11 E1 rank_true (true) / rank_false (false_0) of the same rows."""
    try:
        import pandas as pd
        rid = d['row_id']; base = Path(stored_dir or (A.R11 / 'raw/patch')); rt, rf = {}, {}
        tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
        s11s = pd.read_parquet(A.R11 / 'config/sample.parquet').set_index('paper_id').shard
        for k in sorted(set(s11s.reindex(tk.reindex(rid)).dropna().astype(int))):
            f = base / f'shard_{k:03d}.npz'
            if not f.exists(): continue
            z = np.load(f); rt.update(zip(z['row_id'].tolist(), z['rank_true'].tolist())); rf.update(zip(z['row_id'].tolist(), z['rank_false'].tolist()))
        m = np.array([r in rt for r in rid])
        if not m.any(): return dict(status='NO_STORED')
        a_t = d['rank_true'][m, 0]; a_f = d['rank_false_0'][m, 0]; b_t = np.array([rt[r] for r in rid[m]]); b_f = np.array([rf[r] for r in rid[m]])
        eq_t, eq_f = float((a_t == b_t).mean()), float((a_f == b_f).mean())
        mx = float(max(np.abs(A.nlr(a_t) - A.nlr(b_t)).max(), np.abs(A.nlr(a_f) - A.nlr(b_f)).max()))
        return dict(status='OK' if min(eq_t, eq_f) >= 0.95 else 'WARN', rows=int(m.sum()), eq_true=eq_t, eq_false0=eq_f, max_dnlr=mx, threshold_eq=0.95)
    except Exception as ex:
        return dict(status='WARN', note=f'check crashed: {ex!r}')


def compute(C, u):
    return do_refmean(C, u[1]) if u[0] == 'refmean' else do_main(C, u[1])


def work(a, C=None):
    us = all_units(a.shards)
    # main units need every refmean shard: refmean first, then main
    miss, C = A.work(us, out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item4')
    return miss


# ------------------------------------------------------------------ analysis
def analyze(a=None):
    import pandas as pd
    B = A.Boot(); A.check_addendum(); SUM.mkdir(parents=True, exist_ok=True)
    fs = [out_path(('main', k)) for k in range(24)]; have = [f for f in fs if f.exists()]
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    Z = [np.load(f) for f in have]; rid = np.concatenate([z['row_id'] for z in Z]); pid = tk.reindex(rid).to_numpy()
    R = {c: A.nlr(np.concatenate([z[f'rank_{c}'] for z in Z])) for c in A.CONDS}          # rows x configs
    PM = {c: pd.DataFrame(R[c], columns=CONFIGS).groupby(pid).mean() for c in A.CONDS}       # paper means
    pids = PM['true'].index.to_numpy(); grp = B.meta.group_tight.reindex(pids).to_numpy()
    F = sum(PM[c] for c in A.FALSES) / 5; S = PM['true'] - F                                   # paper x config
    checks = [json.loads(str(z['meta'])).get('check', {}) for z in Z]
    rows, boots = [], {}
    def add(name, v, extra=None):
        e, b = B.mean(pids, v); et, bt = B.mean(pids[grp == 'target'], v[grp == 'target']); ec, bc = B.mean(pids[grp == 'control'], v[grp == 'control'])
        t, tb, nb = B.tc(pids, v); boots[name] = (b, tb)
        r = dict(quantity=name, all=e, all_lo=B.ci(b)[0], all_hi=B.ci(b)[1], target=et, target_lo=B.ci(bt)[0], target_hi=B.ci(bt)[1],
                 control=ec, control_lo=B.ci(bc)[0], control_hi=B.ci(bc)[1], tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1], tc_bins=nb, n_papers=len(pids))
        if extra: r.update(extra)
        rows.append(r); return b, tb
    add('S_none', S['none'].to_numpy())
    for cfg in CONFIGS[1:]:
        loss = (S['none'] - S[cfg]).to_numpy()
        per = [((PM['true']['none'] - PM[f]['none']) - (PM['true'][cfg] - PM[f][cfg])).mean() for f in A.FALSES]
        add(f'loss_{cfg}', loss, dict(loss_min_over_false=float(min(per)), loss_max_over_false=float(max(per)),
                                      share_of_S=float(loss.mean() / S['none'].mean())))
        add(f'loss_true_only_{cfg}', (PM['true']['none'] - PM['true'][cfg]).to_numpy())
    # criterion: MLP loss - attention loss (paired, same draws), per layer and mean over the 5 layers
    crit = []
    for l in LAYERS + ['mean']:
        if l == 'mean':
            v = np.mean([(S[f'attn{x}'] - S[f'mlp{x}']).to_numpy() for x in LAYERS], 0)
        else:
            v = (S[f'attn{l}'] - S[f'mlp{l}']).to_numpy()                                       # = loss_mlp - loss_attn
        e, b = B.mean(pids, v); t, tb, _ = B.tc(pids, v); lo, hi = B.ci(b)
        verdict = 'MLP > attention (CI > 0): "后段由 MLP 写出"' if lo > 0 else ('attention > MLP (CI < 0)' if hi < 0 else 'no difference (CI includes 0)')
        crit.append(dict(layer=l, mlp_minus_attn_loss=e, lo=lo, hi=hi, p=B.p(b), tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1], verdict=verdict))
    T = pd.DataFrame(rows); CR = pd.DataFrame(crit)
    T.to_csv(SUM / 'item4_table.csv', index=False); CR.to_csv(SUM / 'item4_criterion.csv', index=False)
    p2 = None
    try:
        p2 = pd.read_csv(A.R12 / 'summary/P2_patch_comp.csv'); p2 = p2[(p2.group == 'all') & (p2.layer.isin([48, 52, 56]))]
    except Exception: pass
    nm = _MEAN.get('n')
    st = pd.Series([c.get('status') for c in checks]).value_counts().to_dict()
    eqs = [(c.get('eq_true'), c.get('eq_false0')) for c in checks if 'eq_true' in c]
    L = ['# Addendum 18b item 4 — L57–L61 attention / MLP mean ablation', '',
         f'**Pre-registered (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…); criterion fixed by the lock ("判据草案" as written).** '
         f'Sample: 600-paper subsample of the Stage 11 sample (300 target + 300 control, 30 + 30 per citation bin, seed {A.SEED}); '
         f'{len(have)}/24 shards, {len(pids)} papers, {len(rid)} name-token rows. Reference means from the other 586 Stage 11 papers (5 false titles). '
         'Ablation positions: prompt tail after the title (roles p1..p9) and all name inputs; one layer and one component per config. '
         'S = true − mean of 5 false titles (paper mean of log10(1/rank), final output); loss = S(none) − S(config). '
         'Intervals: author-team cluster bootstrap, 2,000 draws (one draw shared by all rows → paired); T − C within citation bin (Stage 10 definition). * = CI excludes 0.', '',
         '## Criterion (MLP loss − attention loss, paired)', '', '| layer | MLP − attn loss | p | T − C of the difference | verdict |', '|---|---|---|---|---|']
    for r in CR.itertuples():
        L.append(f'| {r.layer} | {r.mlp_minus_attn_loss:+.4f} [{r.lo:+.4f}, {r.hi:+.4f}] | {r.p:.4f} | {r.tc:+.4f} [{r.tc_lo:+.4f}, {r.tc_hi:+.4f}] | {r.verdict} |')
    L += ['', '## Loss per config (spec units, log10(1/rank))', '', '| quantity | all | target | control | T − C (within bin) | min / max over false titles | share of S(none) |', '|---|---|---|---|---|---|---|']
    for r in T.itertuples():
        mm = f'{r.loss_min_over_false:+.4f} / {r.loss_max_over_false:+.4f}' if 'loss_min_over_false' in T and np.isfinite(getattr(r, 'loss_min_over_false', np.nan)) else ''
        sh = f'{r.share_of_S:.3f}' if 'share_of_S' in T and np.isfinite(getattr(r, 'share_of_S', np.nan)) else ''
        L.append(f'| {r.quantity} | {r.all:+.4f} [{r.all_lo:+.4f}, {r.all_hi:+.4f}] | {r.target:+.4f} [{r.target_lo:+.4f}, {r.target_hi:+.4f}] | '
                 f'{r.control:+.4f} [{r.control_lo:+.4f}, {r.control_hi:+.4f}] | {r.tc:+.4f} [{r.tc_lo:+.4f}, {r.tc_hi:+.4f}] | {mm} | {sh} |')
    if p2 is not None and len(p2):
        L += ['', 'Reference P2 (Stage 12, component patching true → false_0 on the whole aligned tail, recovery share, all 1,186 papers): ' +
              '; '.join(f'{r.comp}{r.layer} {r.recovery:+.3f}' for r in p2.itertuples())]
    L += ['', '## Checks (WARN only, never stop)', '', f'- per-shard check status: {st}; exact-match share of the unablated ranks vs the stored Stage 11 E1 rows '
          f'(true / false_0): min {min([x[0] for x in eqs] + [1]):.3f} / {min([x[1] for x in eqs] + [1]):.3f} (threshold 0.95; bf16 batch-shape differences allowed).']
    (SUM / 'item4_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
    return T, CR


# ------------------------------------------------------------------ tiny full-pipeline test (CPU, random model)
def tiny(a):
    global RAW, SUM
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; ok = {}
    C = A.make_ctx(tiny=True)
    sm, rf = A.sample(), A.refset()
    _SMP['main'] = pd.concat([sm[sm.shard == k].head(2) for k in range(24)])
    _SMP['refmean'] = pd.concat([rf[rf.shard == k].head(1) for k in range(24)])
    ns = argparse.Namespace(shards='all', max_minutes=600)
    miss = work(ns, C=C)
    ok['all units written'] = not miss
    z = np.load(out_path(('main', 0)))
    ok['shape rows x configs'] = z['rank_true'].shape[1] == len(CONFIGS)
    # none element equals a plain run (fp32 tiny)
    pid = _SMP['main'][_SMP['main'].shard == 0].paper_id.iloc[0]; ai, rids, name = C.ctx[pid][0]; Lt = C.layout(pid, 'true')
    lg = A.final_logits(C, Lt['ids'] + name[:-1], [len(Lt['ids']) - 1 + j for j in range(len(name))])[0]
    r0 = A.ranks(lg, C.torch.tensor(name), C.torch)
    ok['none element = plain unhooked run'] = bool((z['rank_true'][:len(name), 0] == r0).all())
    ok['ablation changes ranks'] = bool((z['rank_true'][:, 1:] != z['rank_true'][:, :1]).any())
    ok['refmean counts > 0 for p1 and name'] = bool((_MEAN['n'][:, :, ROLES.index('p1')] > 0).all() and (_MEAN['n'][:, :, ROLES.index('name')] > 0).all())
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item4_report.md').exists()
    except Exception as ex: print('ANALYZE FAIL', repr(ex)); import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM4 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM4 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
