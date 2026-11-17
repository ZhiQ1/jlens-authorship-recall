"""Addendum 18b item 6 - MLP memory lookup (GPU driver + CPU analysis). New file 2026-11-17.

Design (addendum 18b item 6 = addendum 17 item 6 / plan_batch_20261114b item 6; locked text has no numeric criterion, so every
result here is reported descriptively, "pre-registered design, no locked decision rule"):
 (a) L52-L56 MLP neuron activations (input of down_proj, 25,600 per layer) at the name-predicting positions (':' and every name
     input) for the true title and the 5 false titles: per paper mean over positions and author contexts. Paper-specific? Same
     neuron, team CIs: (i) shared part: mean over papers of d_p = act(true) - mean_k act(false_k), per neuron; (ii) specificity
     index SI = 1 - ||mean_p d_p||^2 / mean_p ||d_p||^2; (iii) top-50 neuron overlap of d_p^(k) = act(true) - act(false_k) between
     two false titles of the SAME paper vs between DIFFERENT papers (Jaccard; within - between > 0 -> paper-specific neurons).
 (b) Patch the true run's MLP output (whole aligned tail, as P2) into the false_k run at one layer l in L52..L56, only the part in
     the author-embedding subspace U (top-512 right singular vectors of the 9,137 name-token lm_head rows scaled by the final-norm
     weight, rows centred; summary_alltok/vocab_rows.npz), only the orthogonal part, a random 512-dim subspace (seed 6), and the
     full output. Value: out_F + P(out_T - out_F). 5 layers x 5 false titles x {aligned, orthogonal} = the 50 configs of the
     design, plus full / random as references.
 (c) The same for the attention output (full / aligned / orthogonal) -> division of labour.
 Readout (b, c): recovery = mean(patched - none) / mean(true - none) (P2 estimand; paper means of log10(1/rank), final output),
 five-title mean of the per-title ratios; team-bootstrap CIs (2,000 draws), paired.
Units ('main', k) -> raw/a18b_item6/main/shard_XXX.npz.  'prep' (CPU) writes a18b_config/item6_subspace.npz.
Commands: prep | work [--shards S] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

LAYERS = [52, 53, 54, 55, 56]; K_SUB = 512
KINDS = ['mlp_full', 'mlp_aligned', 'mlp_orth', 'mlp_rand', 'attn_full', 'attn_aligned', 'attn_orth']
CONFIGS = ['none'] + [f'{k}@{l}' for l in LAYERS for k in KINDS]
RAW = Path(os.environ.get('A18B_RAW6', A.R13 / 'raw/a18b_item6')); SUM = Path(os.environ.get('A18B_SUM6', A.R13 / 'summary_a18b_item6'))
SUBF = Path(os.environ.get('A18B_SUB6', A.CFG / 'item6_subspace.npz'))
_SMP = {}


def smp():
    if 'm' not in _SMP: _SMP['m'] = A.sample()
    return _SMP['m']


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None): return [('main', k) for k in A.parse_shards(shards, 24)]


def prep(a=None, rows=None, nw=None, k=K_SUB, out=None):
    out = Path(out or SUBF)
    if out.exists(): print('exists', out); return
    if rows is None:
        vr = np.load(A.R13 / 'summary_alltok/vocab_rows.npz'); rows = vr['lm_head_rows'].astype(np.float32); nw = vr['norm_weight'].astype(np.float32)
    M = rows * nw[None]; M = M - M.mean(0, keepdims=True)
    _, s, Vt = np.linalg.svd(M, full_matrices=False)
    U = Vt[:k].T.astype(np.float32); ev = float((s[:k] ** 2).sum() / (s ** 2).sum())
    R = np.linalg.qr(np.random.default_rng(6).standard_normal((M.shape[1], k)))[0].astype(np.float32)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, U=U, R=R, var_explained=np.array(ev), k=np.array(k), meta=np.array(json.dumps(dict(created=time.strftime('%F %T'),
             source='summary_alltok/vocab_rows.npz', rule='top-k right singular vectors of (lm_head rows * final-norm weight), rows centred; random = QR of N(0,1), seed 6'))))
    print('subspace', U.shape, 'variance explained by top', k, f'{ev:.3f}')


def tails_for(C, pid, cond):
    s11 = C.s11; Lt = C.layout(pid, 'true'); Lf = C.layout(pid, cond)
    return min(s11.common_suffix(Lt['ids'], Lf['ids']), len(Lt['ids']) - 1 - max(Lt['tpos']), len(Lf['ids']) - 1 - max(Lf['tpos']))


_SUB = {}
def subspaces(C):
    if 'U' not in _SUB:
        z = np.load(SUBF); dev = C.model.layers[LAYERS[0]].mlp.down_proj.weight.device
        _SUB['U'] = C.torch.tensor(z['U'], device=dev); _SUB['R'] = C.torch.tensor(z['R'], device=dev)
    return _SUB['U'], _SUB['R']


def compute(C, u):
    torch = C.torch; U, Rr = subspaces(C); sm = smp(); papers = sm[sm.shard == u[1]].paper_id.tolist()
    model = C.model; nI = model.layers[LAYERS[0]].mlp.down_proj.in_features
    ranks = {c: [] for c in A.FALSES}; rank_true = []; rows = []; acts_out = []
    for pid in papers:
        Lt = C.layout(pid, 'true'); acc = np.zeros((len(A.CONDS), len(LAYERS), nI)); cnt = np.zeros(len(A.CONDS))
        for ai, rids, name in C.ctx[pid]:
            rows += rids; gold = torch.tensor(name, device=model.input_device)
            T = Lt['ids'] + name[:-1]; posT = [len(Lt['ids']) - 1 + j for j in range(len(name))]
            rec, hs = {}, []
            for l in LAYERS:
                hs.append((model.layers[l].self_attn, lambda m_, i_, o, l=l: rec.__setitem__(('attn', l), o[0][0].detach().clone())))
                hs.append((model.layers[l].mlp, lambda m_, i_, o, l=l: rec.__setitem__(('mlp', l), o[0].detach().clone())))
            pre = []
            for l in LAYERS:
                pre.append(model.layers[l].mlp.down_proj.register_forward_pre_hook(lambda m_, i_, l=l: rec.__setitem__(('act', l), i_[0][0, posT].float().mean(0).cpu().numpy())))
            try: lt = A.final_logits(C, T, posT, hooks=hs)[0]
            finally:
                for h in pre: h.remove()
            rank_true.append(A.ranks(lt, gold, torch))
            acc[0] += np.stack([rec[('act', l)] for l in LAYERS]); cnt[0] += 1
            for ci, cond in enumerate(A.FALSES, start=1):
                Lf = C.layout(pid, cond); F = Lf['ids'] + name[:-1]; posF = [len(Lf['ids']) - 1 + j for j in range(len(name))]
                n = tails_for(C, pid, cond) + len(name) - 1
                hs2 = []; act0 = {}
                for l in LAYERS:
                    for comp in ('attn', 'mlp'):
                        val = rec[(comp, l)][-n:]
                        def hk(m_, i_, o, comp=comp, l=l, val=val):
                            t = o[0] if comp == 'attn' else o
                            for e, cfg in enumerate(CONFIGS):
                                if cfg == 'none': continue
                                kind, ll = cfg.split('@')
                                if int(ll) != l or not kind.startswith(comp): continue
                                cur = t[e, -n:]; dlt = (val.to(t.device) - cur).float()
                                sub = kind.split('_')[1]
                                if sub == 'full': new = val.to(t.device, t.dtype)
                                elif sub == 'aligned': new = (cur.float() + (dlt @ U) @ U.T).to(t.dtype)
                                elif sub == 'orth': new = (cur.float() + dlt - (dlt @ U) @ U.T).to(t.dtype)
                                else: new = (cur.float() + (dlt @ Rr) @ Rr.T).to(t.dtype)
                                t[e, -n:] = new
                            return o
                        hs2.append((model.layers[l].self_attn if comp == 'attn' else model.layers[l].mlp, hk))
                pre = [model.layers[l].mlp.down_proj.register_forward_pre_hook(lambda m_, i_, l=l: act0.__setitem__(l, i_[0][0, posF].float().mean(0).cpu().numpy())) for l in LAYERS]
                try: lp = A.final_logits(C, F, posF, batch=len(CONFIGS), hooks=hs2)
                finally:
                    for h in pre: h.remove()
                ranks[cond].append(np.stack([A.ranks(lp[i], gold, torch) for i in range(len(CONFIGS))], 1))
                acc[ci] += np.stack([act0[l] for l in LAYERS]); cnt[ci] += 1
        acts_out.append((acc / cnt[:, None, None]).astype(np.float16))
    d = dict(row_id=np.array(rows), configs=np.array(CONFIGS), layers=np.array(LAYERS), rank_true=np.concatenate(rank_true),
             papers=np.array(papers), acts=np.stack(acts_out), **{f'rank_{c}': np.concatenate(v) for c, v in ranks.items()})
    return d, dict(check=check(d))


def check(d):
    """WARN only: rank_true and the 'none' false_0 ranks vs the stored Stage 11 E1 rows; full-MLP patch at L52/L56 vs P2 is in analysis."""
    try:
        import a18b_item4 as I4
        dd = dict(row_id=d['row_id'], rank_true=d['rank_true'][:, None], rank_false_0=d['rank_false_0'][:, :1])
        return I4.check_vs_e1(dd)
    except Exception as ex: return dict(status='WARN', note=repr(ex))


def work(a, C=None):
    if not SUBF.exists(): prep()
    miss, C = A.work(all_units(a.shards), out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item6'); return miss


# ------------------------------------------------------------------ analysis
def analyze(a=None):
    import pandas as pd
    A.check_addendum(); B = A.Boot(); SUM.mkdir(parents=True, exist_ok=True)
    have = [out_path(u) for u in all_units() if out_path(u).exists()]; Z = [np.load(f) for f in have]
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    rid = np.concatenate([z['row_id'] for z in Z]); pid = tk.reindex(rid).to_numpy()
    nt = A.nlr(np.concatenate([z['rank_true'] for z in Z]))
    rows, boots = [], {}
    for cond in A.FALSES:
        R = A.nlr(np.concatenate([z[f'rank_{cond}'] for z in Z])); none = R[:, 0]
        for ci, cfg in enumerate(CONFIGS[1:], start=1):
            df = pd.DataFrame({'p': pid, 'n': R[:, ci] - none, 'd': nt - none}).groupby('p').mean()
            pids = df.index.to_numpy(); e, b = B.ratio(pids, df.n.to_numpy(), df.d.to_numpy())
            g = B.meta.group_tight.reindex(pids).to_numpy(); bt = B.ratio(pids[g == 'target'], df.n[g == 'target'], df.d[g == 'target'])
            bc = B.ratio(pids[g == 'control'], df.n[g == 'control'], df.d[g == 'control'])
            boots[(cfg, cond)] = (b, bt[1], bc[1]); rows.append(dict(config=cfg, title=cond, recovery=e, target=bt[0], control=bc[0], n_papers=len(pids)))
    D = pd.DataFrame(rows); M = []
    for cfg, x in D.groupby('config', sort=False):
        bb = [np.nanmean([boots[(cfg, c)][j] for c in A.FALSES], 0) for j in range(3)]
        kind, l = cfg.split('@')
        M.append(dict(config=cfg, kind=kind, layer=int(l), recovery=x.recovery.mean(), lo=B.ci(bb[0])[0], hi=B.ci(bb[0])[1], rmin=x.recovery.min(), rmax=x.recovery.max(),
                      target=x.target.mean(), t_lo=B.ci(bb[1])[0], t_hi=B.ci(bb[1])[1], control=x.control.mean(), c_lo=B.ci(bb[2])[0], c_hi=B.ci(bb[2])[1],
                      tc_diff=x.target.mean() - x.control.mean(), tc_lo=B.ci(bb[1] - bb[2])[0], tc_hi=B.ci(bb[1] - bb[2])[1], n_papers=int(x.n_papers.max())))
        boots[(cfg, 'mean5')] = bb[0]
    M = pd.DataFrame(M)
    comp = []
    for l in LAYERS:
        for a_, b_ in (('mlp_aligned', 'mlp_orth'), ('mlp_aligned', 'mlp_rand'), ('attn_aligned', 'attn_orth'), ('mlp_full', 'attn_full'), ('mlp_aligned', 'attn_aligned')):
            bb = boots[(f'{a_}@{l}', 'mean5')] - boots[(f'{b_}@{l}', 'mean5')]
            e = M.set_index('config').loc[f'{a_}@{l}', 'recovery'] - M.set_index('config').loc[f'{b_}@{l}', 'recovery']
            comp.append(dict(layer=l, contrast=f'{a_} − {b_}', diff=e, lo=B.ci(bb)[0], hi=B.ci(bb)[1], p=B.p(bb)))
    CP = pd.DataFrame(comp)
    # (a) neurons
    acts = np.concatenate([z['acts'] for z in Z]).astype(np.float32); pp = np.concatenate([z['papers'] for z in Z])     # [n, 6, 5, I]
    arows = []
    rng = np.random.default_rng(66)
    for li, l in enumerate(LAYERS):
        d5 = acts[:, 0, li][:, None] - acts[:, 1:, li]                         # [n, 5, I]
        d = d5.mean(1)                                                          # [n, I]
        W = B.W(pp); n = len(pp)
        mean_d = d.mean(0); energy = (d ** 2).sum(1)
        si = 1 - (mean_d ** 2).sum() / energy.mean()
        bmean = (W @ d) / W.sum(1)[:, None]; ben = (W @ energy) / W.sum(1); si_b = 1 - (bmean ** 2).sum(1) / ben
        lo, hi = np.percentile(bmean, [2.5, 97.5], axis=0); nsig = int(((lo > 0) | (hi < 0)).sum())
        # top-50 overlap within paper (false_k vs false_j) vs between papers (same k)
        top = np.argsort(-np.abs(d5), axis=2)[:, :, :50]
        def jac(a, b): return len(set(a) & set(b)) / len(set(a) | set(b))
        within = np.array([np.mean([jac(top[i, k], top[i, j]) for k in range(5) for j in range(k + 1, 5)]) for i in range(n)])
        perm = rng.permutation(n); perm = np.where(perm == np.arange(n), (perm + 1) % n, perm)
        between = np.array([np.mean([jac(top[i, k], top[perm[i], k]) for k in range(5)]) for i in range(n)])
        e_w, b_w = B.mean(pp, within - between); t_e, t_b, _ = B.tc(pp, np.sqrt(energy))
        arows.append(dict(layer=l, n_papers=n, n_neurons=d.shape[1], shared_neurons_ci_excl0=nsig, expected_by_chance=round(0.05 * d.shape[1]),
                          SI=float(si), SI_lo=float(np.nanpercentile(si_b, 2.5)), SI_hi=float(np.nanpercentile(si_b, 97.5)),
                          jaccard_within=float(within.mean()), jaccard_between=float(between.mean()), within_minus_between=e_w, wmb_lo=B.ci(b_w)[0], wmb_hi=B.ci(b_w)[1],
                          norm_d_tc=t_e, norm_d_tc_lo=B.ci(t_b)[0], norm_d_tc_hi=B.ci(t_b)[1]))
    AR = pd.DataFrame(arows)
    D.to_csv(SUM / 'item6_patch_per_title.csv', index=False); M.to_csv(SUM / 'item6_patch_mean5.csv', index=False); CP.to_csv(SUM / 'item6_contrasts.csv', index=False); AR.to_csv(SUM / 'item6_neurons.csv', index=False)
    sub = np.load(SUBF); checks = [json.loads(str(z['meta'])).get('check', {}) for z in Z]
    p2 = None
    try: p2 = pd.read_csv(A.R12 / 'summary/P2_patch_comp.csv'); p2 = p2[(p2.group == 'all') & (p2.layer.isin([52, 56]))]
    except Exception: pass
    f = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if (lo > 0 or hi < 0) else '')
    L = ['# Addendum 18b item 6 — MLP memory lookup (L52–L56)', '',
         f'**Pre-registered design (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…), no locked numeric decision rule → all results descriptive.** '
         f'600-paper subsample of the Stage 11 sample (seed {A.SEED}); {len(have)}/24 shards, {len(pp)} papers. Author-embedding subspace: top-{int(sub["k"])} right singular vectors of the '
         f'9,137 name-token lm_head rows × final-norm weight (centred), {float(sub["var_explained"]):.3f} of their variance; random control = 512-dim random subspace. '
         'Patching true → false_k on the whole aligned tail (P2 positions), value out_F + P(out_T − out_F); recovery = mean(patched − none)/mean(true − none), five-title mean; '
         'author-team cluster bootstrap 2,000 draws (paired). * = CI excludes 0.', '',
         '## (b)/(c) Recovery by layer and patched part (five-title mean)', '', '| config | recovery | min / max over titles | target | control | target − control |', '|---|---|---|---|---|---|']
    for r in M.itertuples():
        L.append(f'| {r.config} | {f(r.recovery, r.lo, r.hi)} | {r.rmin:+.3f} / {r.rmax:+.3f} | {f(r.target, r.t_lo, r.t_hi)} | {f(r.control, r.c_lo, r.c_hi)} | {f(r.tc_diff, r.tc_lo, r.tc_hi)} |')
    L += ['', '## Paired contrasts', '', '| layer | contrast | difference | p |', '|---|---|---|---|']
    for r in CP.itertuples(): L.append(f'| L{r.layer} | {r.contrast} | {f(r.diff, r.lo, r.hi)} | {r.p:.4f} |')
    if p2 is not None and len(p2): L += ['', 'Reference P2 (Stage 12, false_0, 1,186 papers, full component): ' + '; '.join(f'{r.comp}{r.layer} {r.recovery:+.3f}' for r in p2.itertuples())]
    L += ['', '## (a) MLP neurons: true − false activation differences (name-predicting positions)', '',
          '| layer | neurons with shared mean difference (CI excl. 0) / expected 5% | specificity index SI | top-50 Jaccard within paper | between papers | within − between | T − C of ‖d‖ |', '|---|---|---|---|---|---|---|']
    for r in AR.itertuples():
        L.append(f'| L{r.layer} | {r.shared_neurons_ci_excl0} / {r.expected_by_chance} | {r.SI:.3f} [{r.SI_lo:.3f}, {r.SI_hi:.3f}] | {r.jaccard_within:.3f} | {r.jaccard_between:.3f} | '
                 f'{f(r.within_minus_between, r.wmb_lo, r.wmb_hi)} | {f(r.norm_d_tc, r.norm_d_tc_lo, r.norm_d_tc_hi)} |')
    st = pd.Series([c.get('status') for c in checks]).value_counts().to_dict()
    L += ['', '## Checks (WARN only)', '', f'- unpatched true / false_0 ranks vs the stored Stage 11 E1 rows: {st}; min exact share true '
          f'{min([c.get("eq_true", 1) for c in checks]):.3f}, false_0 {min([c.get("eq_false0", 1) for c in checks]):.3f} (threshold 0.95).']
    (SUM / 'item6_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def tiny(a):
    global RAW, SUM, SUBF
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; SUBF = root / 'sub.npz'; ok = {}
    C = A.make_ctx(tiny=True); sm = A.sample(); _SMP['m'] = pd.concat([sm[sm.shard == k].head(2) for k in range(24)])
    W = C.model._lm_head.weight.detach().float().numpy(); vr = np.load(A.R13 / 'summary_alltok/vocab_rows.npz')
    prep(rows=W[vr['token_id']], nw=C.model._final_norm.weight.detach().float().numpy(), k=8, out=SUBF)
    ns = argparse.Namespace(shards='all', max_minutes=600); miss = work(ns, C=C); ok['all units written'] = not miss
    z = np.load(out_path(('main', 0)))
    ok['acts shape'] = z['acts'].shape[1:] == (6, len(LAYERS), C.model.layers[52].mlp.down_proj.in_features)
    R = z['rank_false_0']
    ok['full = aligned + orth composition differs from none'] = bool((R[:, 1:] != R[:, :1]).any())
    # orth + aligned with U spanning everything would equal full: check with a k = d subspace on one context (fp32)
    ok['none element = unpatched false run'] = True
    pid = _SMP['m'][_SMP['m'].shard == 0].paper_id.iloc[0]; ai, rids, name = C.ctx[pid][0]; Lf = C.layout(pid, 'false_0')
    lg = A.final_logits(C, Lf['ids'] + name[:-1], [len(Lf['ids']) - 1 + j for j in range(len(name))])[0]
    ok['none element = unpatched false run'] = bool((A.ranks(lg, C.torch.tensor(name), C.torch) == R[:len(name), 0]).all())
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item6_report.md').exists()
    except Exception: import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM6 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM6 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['prep', 'work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'prep': prep(a); return
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
