"""Batch 3 (addendum 14): unit tests of every hard check (identical -> PASS, perturbed -> FAIL) on REAL stored data, plus the
CPU prediction of the 3-3 hard check, CPU only.

  real   : U1 bf16-distance function (numpy vs torch, known cases); U2 rank_match rule; U3 3-1/3-2 paper-level L48 check: stored
           Stage 10 ranks through the b3 functions reproduce the published per-paper spec and the published group / within-bin
           values (identical -> PASS), shifted ranks -> FAIL; U4 the 3-1 rank check through rank_rows on stored ranks (PASS / FAIL);
           U5 3-3 check on the stored 7.1B rows (identical -> PASS, perturbed -> FAIL); U6 onset rule;
           P1 PREDICTION for 3-3: Stage 10 fast-path ranks (true title, GPU, stored) vs the old 7.1B shuffle-0 rows (same contexts).
  pert   : copy the tiny 3-1 gate units into b3_tiny_pert/, perturb 2% of the L24 ranks, run gate-check -> must exit 3.
Output: summary_b3_unittest/unittest.json (+ p1_prediction_3_3.csv). Exit 1 if any unit test fails.
"""
import argparse, importlib.util, json, math, os, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b3_cols.py', 'b3_cols'); CK = load(H / '13_stage13/stage13_b3_checks.py', 'b3_checks')
G = load(H / '13_stage13/stage13_b3_s10_gpu.py', 'b3_s10_gpu'); s10 = G.s10
OUT = K.R13 / 'summary_b3_unittest'; RES = []


def T(name, cond, detail=''):
    RES.append(dict(test=name, ok=bool(cond), detail=str(detail))); print(('OK  ' if cond else 'FAIL'), name, detail, flush=True)


def u1():
    import torch
    rng = np.random.default_rng(0)
    for trial in range(30):
        row = (rng.normal(0, 8, 1000)).astype(np.float32); row = torch.tensor(row).bfloat16().float().numpy()   # bf16-representable
        gold = int(rng.integers(0, 1000)); r_now = 1 + int((row > row[gold]).sum())
        tgt = max(1, r_now + int(rng.integers(-3, 4)))
        a = CK.ulps_to_rank_np(row, gold, tgt); b = CK.ulps_to_rank_torch(torch.tensor(row)[None], torch.tensor([gold]), torch.tensor([tgt]), torch)[0]
        if not (a == b or abs(a - b) < 1e-9): T('U1 numpy == torch', False, (a, b)); return
        if tgt == r_now and a != 0: T('U1 same rank -> 0', False, a); return
        # moving the gold logit by the returned distance (+ tiny eps in the right direction) reaches the target rank
        if math.isfinite(a) and a > 0:
            u = float(CK.bf16_ulp(row[gold])); up = tgt < r_now
            g2 = float(row[gold]) + (a * u if up else -(a - 1) * u - 1e-6 * u)          # float64 (a float32 sum would round the eps away)
            r2 = 1 + int((np.delete(row, gold).astype(np.float64) > g2).sum())
            if r2 != tgt: T('U1 distance reaches the target rank', False, (tgt, r_now, r2, a)); return
    T('U1 numpy == torch, 0 for same rank, distance reaches the target rank (30 random cases)', True)
    T('U1 bf16 unit at 40 is 0.25', float(CK.bf16_ulp(40.0)) == 0.25, CK.bf16_ulp(40.0))
    row = np.array([10.0, 10.0, 9.0, 8.0]); T('U1 tie -> rank 2 unreachable = inf', CK.ulps_to_rank_np(row, 3, 2) == math.inf, CK.ulps_to_rank_np(row, 3, 2))


def u2():
    r = np.arange(1, 1001); T('U2 identical -> PASS', CK.rank_match(r, r, np.zeros(1000))['status'] == 'PASS')
    n = r.copy(); n[:20] += 1; ul = np.zeros(1000); ul[:20] = 1.0
    T('U2 2% mismatches -> FAIL (exact < 99%)', CK.rank_match(n, r, ul)['status'] == 'FAIL')
    n = r.copy(); n[:5] += 1; ul = np.zeros(1000); ul[:5] = 2.0
    T('U2 0.5% mismatches within 4 units -> PASS', CK.rank_match(n, r, ul)['status'] == 'PASS')
    ul[0] = 4.5; T('U2 one mismatch at 4.5 units -> FAIL', CK.rank_match(n, r, ul)['status'] == 'FAIL')
    ul[0] = np.nan; T('U2 NaN distance -> FAIL', CK.rank_match(n, r, ul)['status'] == 'FAIL')


def stored_tc():
    papers = pd.read_parquet(K.R10 / 'cohort/papers.parquet', columns=['paper_id', 'shard', 'group_tight', 'citation_bin'])
    P_ = papers[papers.group_tight.isin(K.GROUPS)].sort_values('paper_id').reset_index(drop=True)
    toks = pd.read_parquet(K.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'token_index'])
    Tt = toks[toks.paper_id.isin(set(P_.paper_id))].sort_values('row_id').reset_index(drop=True)
    return P_, Tt


def stored_rank(Tt, cond, r, l):
    arr = np.zeros(len(Tt), np.int64)
    for k, g in Tt.groupby('shard'):
        z = np.load(s10.out_file(K.R10, r, l, int(k), cond)); arr[g.index.to_numpy()] = pd.Series(z['rank'], index=z['row_id']).reindex(g.row_id).to_numpy()
    return arr


def u3():
    P_, Tt = stored_tc(); pidx = {p: i for i, p in enumerate(P_.paper_id)}; codes = Tt.paper_id.map(pidx).to_numpy(); NP = len(P_)
    grp = P_.group_tight.to_numpy(); cbin = P_.citation_bin.astype(str).to_numpy()
    pg = pd.read_csv(K.R10 / 'summary_title/A_group_layer.csv'); pb = pd.read_csv(K.R10 / 'summary_title/B_spec_target_vs_control_within_bin.csv')
    pt = pd.read_parquet(K.R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr'])
    T('U3 6,841 target+control papers', NP == K.N_PAPERS_TC, NP)
    for r in K.READOUTS:
        R_ = {c: stored_rank(Tt, c, r, 48) for c in ['true'] + K.FALSE}
        def spec(Rd): return CK.spec_total_topic({c: CK.paper_means(codes, NP, CK.nlr(Rd[c])) for c in Rd})['spec']
        sp = spec(R_)
        ref = pt[(pt.readout == r) & (pt.layer == 48)].set_index('paper_id').spec_mean_nlr.reindex(P_.paper_id).to_numpy()
        T(f'U3 {r} L48 per-paper spec == published paper_title_contrasts', np.nanmax(np.abs(sp - ref)) < 1e-9, f'max {np.nanmax(np.abs(sp - ref)):.2e}')
        chk = []
        for g in K.GROUPS:
            pub = float(pg[(pg.group_tight == g) & (pg.readout == r) & (pg.layer == 48)].spec_mean_nlr_mean.iloc[0])
            chk.append(CK.scalar_check(g, float(np.nanmean(sp[grp == g])), pub, K.PAPER_SPEC_TOL))
        tc = CK.within_bin_point(sp, grp, cbin)[0]; pub = float(pb[(pb.readout == r) & (pb.layer == 48)].spec_mean_nlr_diff.iloc[0])
        chk.append(CK.scalar_check('tc', tc, pub, K.PAPER_SPEC_TOL))
        T(f'U3 {r} L48 identical -> PASS (group means, within-bin)', all(c['status'] == 'PASS' for c in chk), [f"{c['check']} {c['value']:.1e}" for c in chk])
        T(f'U3 {r} L48 within-bin point == published to 1e-12', abs(tc - pub) < 1e-12, f'{tc - pub:.2e}')
        # perturbation: target papers' true-title ranks x 1.03 (log10 shift ~ -0.013) -> target mean and tc move > 0.005
        Rp = dict(R_); tmask = grp[codes] == 'target'; x = R_['true'].copy(); x[tmask] = np.maximum(1, np.round(x[tmask] * 1.03 + 1)); Rp['true'] = x
        spp = spec(Rp)
        chk2 = [CK.scalar_check('target', float(np.nanmean(spp[grp == 'target'])), float(pg[(pg.group_tight == 'target') & (pg.readout == r) & (pg.layer == 48)].spec_mean_nlr_mean.iloc[0]), K.PAPER_SPEC_TOL),
                CK.scalar_check('tc', CK.within_bin_point(spp, grp, cbin)[0], pub, K.PAPER_SPEC_TOL)]
        T(f'U3 {r} L48 perturbed -> FAIL', all(c['status'] == 'FAIL' for c in chk2), [f"{c['check']} {c['value']:.4f}" for c in chk2])


def u4():
    P_, Tt = stored_tc(); sh = [0, 1]; U = {}
    for c in K.CONDS:
        for k in sh:
            sel = Tt[Tt.shard == k]; n = len(sel); pairs = K.item_pairs('3-1')
            rk = np.zeros((len(pairs), n), np.int32); ref = np.zeros((2 * 2, n), np.int32)
            for j, (r, l) in enumerate(K.check_pairs()):
                z = np.load(s10.out_file(K.R10, r, l, k, c)); v = pd.Series(z['rank'], index=z['row_id']).reindex(sel.row_id).to_numpy()
                ref[j] = v; rk[pairs.index((r, l))] = v
            U[(c, k)] = dict(row_id=sel.row_id.to_numpy(), rank=rk, chk_ref_rank=ref, chk_ulps=np.zeros_like(ref, np.float32), chk_dlogprob=np.zeros_like(ref, np.float32),
                             meta=dict(pairs=[K.pair_name(*p) for p in pairs]))
    rows, pooled = G.rank_rows('3-1', U, 'unittest'); T('U4 rank_rows identical stored ranks -> PASS', pooled['status'] == 'PASS', f"{pooled['n_tokens']} tokens")
    rng = np.random.default_rng(1)
    for u in U.values():
        j = K.item_pairs('3-1').index(('logit', 24)); n = u['rank'].shape[1]; ix = rng.choice(n, max(1, int(0.03 * n)), replace=False)
        u['rank'][j, ix] += 7
        u['chk_ulps'][K.check_pairs().index(('logit', 24)), ix] = 9.0
    rows, pooled = G.rank_rows('3-1', U, 'unittest'); T('U4 rank_rows with 3% of logit L24 perturbed (9 units) -> FAIL', pooled['status'] == 'FAIL',
                                                        f"share {pooled['share_exact']:.4f}, within {pooled['n_mismatch_le_ulps']}/{pooled['n_mismatch']}")


def old71():
    T71 = load(H / '07_1_stage7_1/351_stage7_1B_terminal.py', 's71b'); tasks = T71.read(K.R71B / 'tasks.json')
    rows = []
    for t in tasks:
        f = K.R71B / 'raw' / f"{t['task_id']}.json"
        if not f.exists(): continue
        for q in json.loads(f.read_text())['rows']:
            rows.append(dict(task_id=t['task_id'], paper_id=t['paper_id'], shuffle_index=t['shuffle_index'], author_index=q['author_index'], token_index=q['token_index'],
                             token_id=q['token_id'], mode=q['mode'], layer=int(q['layer']), rank=q['rank'], logprob=q['logprob']))
    return pd.DataFrame(rows), T71


def u5_p1():
    GP = load(H / '13_stage13/stage13_b3_71b_gpu.py', 'b3_71b_gpu')
    D0, T71 = old71(); T('U5 old 7.1B: 1,166 contexts', D0.task_id.nunique() == K.N_DONE_71B, D0.task_id.nunique())
    D = D0.rename(columns={'rank': 'rank_old', 'logprob': 'logprob_old'}).assign(rank_new=D0['rank'], logprob_new=D0['logprob'], ulps=0.0)
    S = GP.summarise(D, 'unittest'); T('U5 identical -> PASS (share 1)', S.iloc[0].share_exact == 1.0 and S.iloc[0].share_exact >= K.R71B_RANK_MIN, S.iloc[0].share_exact)
    rng = np.random.default_rng(2); ix = rng.choice(len(D), int(0.02 * len(D)), replace=False); D2 = D.copy(); D2.loc[ix, 'rank_new'] += 1
    S2 = GP.summarise(D2, 'unittest'); T('U5 2% perturbed -> FAIL (< 0.99)', S2.iloc[0].share_exact < K.R71B_RANK_MIN, S2.iloc[0].share_exact)
    # P1 prediction: Stage 10 stored fast path (true title) vs the old shuffle-0 rows, same (paper, author name, token)
    au = pd.DataFrame(T71.read(K.R71B / 'authors.json'))
    o = D0[D0.shuffle_index == 0].merge(au[['paper_id', 'author_index', 'author']], on=['paper_id', 'author_index'])
    ctx = pd.read_parquet(K.R10 / 'cohort/contexts.parquet', columns=['context_id', 'paper_id', 'author', 'shard'])
    nt = pd.read_parquet(K.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'token_index', 'token_id'])
    j = o.merge(ctx, on=['paper_id', 'author']).merge(nt, on=['context_id', 'token_index'], suffixes=('', '_s10'))
    j = j[j.token_id == j.token_id_s10].drop_duplicates(['paper_id', 'author_index', 'token_index', 'mode', 'layer'])
    out = []
    for (m7, l7), g in j.groupby(['mode', 'layer']):
        r = K.R71_S10NAME[m7]
        if r != 'final' and l7 not in s10.DEFAULT_LAYERS: continue
        new = np.zeros(len(g), np.int64)
        for k, gg in g.groupby('shard'):
            z = np.load(s10.out_file(K.R10, r, int(l7), int(k), 'true')); new[np.searchsorted(g.index.to_numpy(), gg.index.to_numpy())] = pd.Series(z['rank'], index=z['row_id']).reindex(gg.row_id).to_numpy()
        out.append(dict(mode=m7, layer=l7, n=len(g), share_exact=float((new == g['rank'].to_numpy()).mean()),
                        median_abs_dlog10rank=float(np.median(np.abs(np.log10(new) - np.log10(g['rank'].to_numpy())))),
                        ranks_le_41_exact=float((new == g['rank'].to_numpy())[g['rank'].to_numpy() <= 41].mean()) if (g['rank'] <= 41).any() else np.nan))
    P = pd.DataFrame(out); tot = (P.share_exact * P.n).sum() / P.n.sum()
    OUT.mkdir(parents=True, exist_ok=True); P.to_csv(OUT / 'p1_prediction_3_3.csv', index=False)
    print(P.to_string(index=False), flush=True)
    RES.append(dict(test='P1 PREDICTION 3-3 (not a test): Stage 10 fast path vs old 7.1B shuffle-0 rows, pooled rank-exact share', ok=True,
                    detail=f'{tot:.4f} over {int(P.n.sum())} scores (L16 not stored in Stage 10); plan threshold 0.99'))
    print('P1 pooled share', tot, flush=True)


def u6():
    o = CK.onset([24, 32, 40], [-0.1, 0.01, 0.02], [0.1, 0.05, 0.06]); T('U6 onset first lo>0', o == (32, '+', 32, 32), o)
    o = CK.onset([24, 32, 40], [-0.1, -0.05, 0.02], [-0.01, 0.05, 0.06]); T('U6 onset negative first', o == (24, '-', 40, 40), o)


def pert():
    """perturbed copy of the tiny 3-1 gate units -> gate-check must exit 3."""
    src = K.s10_roots('3-1', True); os.environ['B3_TINY_SUFFIX'] = '_pert'; dst = K.s10_roots('3-1', True)
    if dst['raw'].exists(): print('pert root exists, reusing', dst['raw'])
    for c in K.CONDS:
        f = G.unit_path(src, c, 0); g = G.unit_path(dst, c, 0); g.parent.mkdir(parents=True, exist_ok=True)
        z = dict(np.load(f)); m = json.loads(str(z['meta']))
        if c == 'true':
            j = m['pairs'].index('logit@L24'); n = z['rank'].shape[1]; ix = np.random.default_rng(3).choice(n, max(1, int(0.02 * n)), replace=False)
            z['rank'][j, ix] += 5; z['chk_ulps'][m['check_pairs'].index('logit@L24'), ix] = 6.0
        np.savez(g, **z)
    env = dict(os.environ, B3_TINY_SUFFIX='_pert')
    p = subprocess.run([sys.executable, str(H / '13_stage13/stage13_b3_s10_gpu.py'), 'gate-check', '--item', '3-1', '--shards', '0', '--tiny'], env=env, capture_output=True, text=True)
    print(p.stdout[-1500:], p.stderr[-1500:])
    T('PERT tiny 3-1 gate-check on perturbed units exits 3', p.returncode == 3, p.returncode)
    p = subprocess.run([sys.executable, str(H / '13_stage13/stage13_b3_s10_gpu.py'), 'gate-check', '--item', '3-1', '--shards', '0', '--tiny'], capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if k != 'B3_TINY_SUFFIX'})
    T('PERT tiny 3-1 gate-check on the unperturbed units exits 0', p.returncode == 0, p.returncode)


def main():
    K.check_plan(); ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['real', 'pert']); a = ap.parse_args()
    fns = [u1, u2, u3, u4, u5_p1, u6] if a.mode == 'real' else [pert]
    for f in fns:
        try: f()
        except Exception as e:
            import traceback; traceback.print_exc(); T(f'{f.__name__} crashed', False, repr(e))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'unittest_{a.mode}.json').write_text(json.dumps(dict(created=time.ctime(), job=os.environ.get('SLURM_JOB_ID'), results=RES), indent=1))
    bad = [r for r in RES if not r['ok']]; print(f'UNITTEST {a.mode}: {len(RES) - len(bad)}/{len(RES)} OK', flush=True)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
