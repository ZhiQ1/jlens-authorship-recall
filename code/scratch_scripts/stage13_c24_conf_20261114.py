"""C24 / 2-11b follow-up (plan_batch_20261114b item 1; POST-HOC, exploratory). CPU only. New file; nothing existing is edited.
1a (read-only): what the shard-0 confidence replay (job 11836635) stored, and the CPU-only checks that remain possible:
    - mismatch concentration on name-predicting positions (h2 rows: pre-name + name tokens of M/H names) vs base share;
    - first-name-token mismatches (tf_argmax_first_eq == False): upper bound on the logit gap argmax - generated token
      from the replay log p(generated) alone: gap = lp(argmax) - lp(gen) <= log(1 - p_gen) - log p_gen.
1b: name-feature baseline with cohort full-name frequency EXCLUDING the current paper (same rule as fame: discard pid);
    old vs new name-feature and combined (position + name + fame) baselines; probe - combined, L16-L56, same fit_oof,
    within-paper AUROC over M-H pairs (target papers), team bootstrap 2,000 draws seed 12, all scores on one draw set.
1c (descriptive, shard 0 only): replay confidence scores (lp_mean, lp_first, -ent_pre) vs probe on shard-0 target papers.
Outputs: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_c24_conf_20261114/
"""
import importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); ROOT = R13 / 'b2_gennames_b'
OUT = R13 / 'summary_c24_conf_20261114'
_sp = importlib.util.spec_from_file_location('gnb_rob', H / '13_stage13/stage13_b2_gennames_b_robust.py'); RB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RB)
AN, V1, V2, B = RB.AN, RB.V1, RB.V2, RB.B
PUB = dict(probe48=0.7824675324675324, probe48_lo=0.7539618541778288, probe48_hi=0.8116577549036231, combined=0.6785714285714286)


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def ci(v): return tuple(np.percentile(v, [2.5, 97.5]))


def part1a():
    import pandas as pd
    rep = json.loads((ROOT / 'conf/replay_000.json').read_text())
    C = pd.read_parquet(ROOT / 'conf/shard_000.parquet'); H2 = pd.read_csv(ROOT / 'h2/shard_000.csv'); PP = pd.read_csv(ROOT / 'papers/shard_000.csv')
    npz = np.load(ROOT / 'raw/shard_000.npz', allow_pickle=True)
    stored = dict(conf_parquet_columns=list(C.columns), conf_rows=len(C), h2_columns=list(H2.columns), npz_keys_sample=sorted(npz.keys())[:4] + ['...'],
                  npz_layers='residuals L16-L56 only (name_mean / pred_first / last), no final layer, no logits')
    mm_all = rep['positions'] - rep['agree']; mm_h2 = rep['h2_positions'] - rep['h2_agree']
    gen_eq_final = float((H2.next_tok == H2.final_argmax).mean())
    PP['P'] = PP.n_prompt; pm = dict(zip(PP.paper_id, PP.P)); ng = dict(zip(PP.paper_id, PP.n_gen))
    in_range = bool(((H2.pos >= H2.paper_id.map(pm) - 1) & (H2.pos <= H2.paper_id.map(pm) + H2.paper_id.map(ng) - 2)).all())
    dup = int(H2.duplicated(['paper_id', 'pos']).sum())
    base = rep['h2_positions'] / rep['positions']; share = mm_h2 / mm_all
    other_pos = rep['positions'] - rep['h2_positions']; mm_other = mm_all - mm_h2
    first = C[~C.tf_argmax_first_eq].copy(); p = np.exp(first.lp_first.to_numpy())
    first['gap_upper'] = np.log1p(-np.minimum(p, 1 - 1e-12)) - first.lp_first.to_numpy()
    r = dict(replay=rep, stored=stored, generation_time_logits_stored=False, h2_next_tok_eq_stored_final_argmax=gen_eq_final, h2_positions_in_replay_range=in_range, h2_duplicate_rows=dup,
             mismatches_all=mm_all, mismatches_on_name_predicting_positions=mm_h2, mismatches_other=mm_other,
             base_share_name_predicting=base, mismatch_share_name_predicting=share, enrichment=share / base,
             mismatch_rate_name_predicting=mm_h2 / rep['h2_positions'], mismatch_rate_other=mm_other / max(1, other_pos),
             names=len(C), names_first_token_mismatch=len(first), first_mismatch_lp_gen=first.lp_first.describe().to_dict(),
             first_mismatch_gap_upper=dict(median=float(first.gap_upper.median()), max=float(first.gap_upper.max()),
                                           share_le_0p5=float((first.gap_upper <= 0.5).mean()), share_le_1p0=float((first.gap_upper <= 1.0).mean()),
                                           share_le_2p0=float((first.gap_upper <= 2.0).mean())),
             names_affected_lower=len(first) / len(C), names_affected_upper=min(len(C), len(first) + (mm_h2 - len(first))) / len(C))
    first[['paper_id', 'item_index', 'status', 'lp_first', 'ent_pre', 'lp_mean', 'n_tok', 'gap_upper']].to_csv(OUT / 'c24_1a_first_token_mismatches.csv', index=False)
    log('1a', json.dumps({k: v for k, v in r.items() if k not in ('stored',)}, default=float)); return r, C


def part1b(C0):
    import pandas as pd
    shards = list(range(AN.N_SHARDS))
    NA = pd.concat([pd.read_parquet(ROOT / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    zs = [np.load(ROOT / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    N = N.reset_index(drop=True); ix = np.array([kidx[k_] for k_ in N.key])
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy()
    RB.V3.patch(); P, _ = B.load_papers(); pool = B.Pool(P)   # generation run used V3.patch() (words3)
    inc = np.array([len(pool.full.get(' '.join(B.words(nm)), set())) for nm in N.name], float)
    exc = np.array([len(pool.full.get(' '.join(B.words(nm)), set()) - {pid}) for nm, pid in zip(N.name, N.paper_id)], float)
    par_freq = float(np.mean(inc == N.fullname_freq_cohort.to_numpy(float)))
    freq_desc = dict(parity_incl_vs_stored=par_freq, M_old_ge1=float((inc[y == 1] >= 1).mean()), H_old_ge1=float((inc[y == 0] >= 1).mean()),
                     M_new_ge1=float((exc[y == 1] >= 1).mean()), H_new_ge1=float((exc[y == 0] >= 1).mean()),
                     names_changed=float(np.mean(inc != exc)), M_changed=float(np.mean((inc != exc)[y == 1])), H_changed=float(np.mean((inc != exc)[y == 0])))
    log('freq', freq_desc)
    XP = N[['item_index', 'item_rel']].to_numpy(float); L = N.name_len_chars.to_numpy(float)
    XS_old = np.stack([L, np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1); XS_new = np.stack([L, np.log1p(exc)], 1)
    XF = RB.fame_features(N, P)
    base = {}
    for nm_, X_ in [('position', XP), ('name_old', XS_old), ('name_new', XS_new), ('fame', XF),
                    ('comb_old', np.concatenate([XP, XS_old, XF], 1)), ('comb_new', np.concatenate([XP, XS_new, XF], 1))]:
        base[nm_], Cb, _ = V1.fit_oof(X_, y, fold); log('baseline', nm_, 'C', Cb)
    # shard-0 confidence (1c descriptive)
    C0 = C0.copy(); C0['key'] = C0.paper_id + '|' + C0.item_index.astype(str); cm = C0.set_index('key')
    s0 = N.key.isin(cm.index).to_numpy()
    conf = {c: N.key.map(cm[c]).to_numpy(float) for c in ('lp_mean', 'lp_first', 'ent_pre')}
    rows, rows1c = [], []; bnames = list(base)
    for l in AN.LAYERS:
        X = np.concatenate([z[f'name_mean@{l}'] for z in zs])[ix].astype(np.float32)
        pr, C, _ = V1.fit_oof(X, y, fold)
        scs = [pr] + [base[b] for b in bnames]
        st = [V2.pair_stats(paper[tgt], y[tgt], sc[tgt]) for sc in scs]
        common = set.intersection(*[set(s) for s in st]); st = [{p_: s[p_] for p_ in common} for s in st]
        est, bt, npap, npair = V2.within_auroc(st, PT)
        r = dict(layer=l, C=C, n_papers=npap, n_pairs=npair)
        for j, nm_ in enumerate(['probe'] + bnames):
            r[nm_] = est[j]; r[nm_ + '_lo'], r[nm_ + '_hi'] = ci(bt[:, j])
        jj = {nm_: j for j, nm_ in enumerate(['probe'] + bnames)}
        for a_, b_, lab in [('probe', 'comb_old', 'probe_minus_comb_old'), ('probe', 'comb_new', 'probe_minus_comb_new'), ('comb_old', 'comb_new', 'comb_old_minus_new'),
                            ('name_old', 'name_new', 'name_old_minus_new'), ('probe', 'name_new', 'probe_minus_name_new')]:
            d = bt[:, jj[a_]] - bt[:, jj[b_]]; r[lab] = est[jj[a_]] - est[jj[b_]]; r[lab + '_lo'], r[lab + '_hi'] = ci(d); r[lab + '_p_le0'] = float((d <= 0).mean())
        rows.append(r); log(f'L{l}', {k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})
        # 1c descriptive: shard-0 target names with replay confidence, probe vs raw confidence scores (no fitting; higher = more confident)
        m = s0 & tgt
        sc1 = [pr[m], conf['lp_mean'][m], conf['lp_first'][m], -conf['ent_pre'][m], base['comb_new'][m]]
        st1 = [V2.pair_stats(paper[m], y[m], s) for s in sc1]; com1 = set.intersection(*[set(s) for s in st1])
        if com1:
            st1 = [{p_: s[p_] for p_ in com1} for s in st1]; e1, b1, np1, nq1 = V2.within_auroc(st1, PT)
            r1 = dict(layer=l, n_papers=np1, n_pairs=nq1, n_M=int(y[m & np.isin(paper, list(com1))].sum()))
            for j, nm_ in enumerate(['probe', 'conf_lp_mean', 'conf_lp_first', 'conf_neg_entropy', 'comb_new']):
                r1[nm_] = e1[j]; r1[nm_ + '_lo'], r1[nm_ + '_hi'] = ci(b1[:, j])
            d = b1[:, 0] - b1[:, 1]; r1['probe_minus_conf_lp_mean'] = e1[0] - e1[1]; r1['pmc_lo'], r1['pmc_hi'] = ci(d)
            rows1c.append(r1)
    return pd.DataFrame(rows), pd.DataFrame(rows1c), freq_desc


def fmt(e, lo, hi, s=''): return f'{e:{s}.3f} [{lo:{s}.3f}, {hi:{s}.3f}]'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    r1a, C0 = part1a(); (OUT / 'c24_1a.json').write_text(json.dumps(r1a, indent=1, default=float))
    T, T1c, fd = part1b(C0)
    T.to_csv(OUT / 'c24_1b_baselines.csv', index=False); T1c.to_csv(OUT / 'c24_1c_shard0_descriptive.csv', index=False)
    (OUT / 'c24_1b_freq.json').write_text(json.dumps(fd, indent=1))
    t48 = T.set_index('layer').loc[48]
    par = dict(probe48=float(t48.probe), probe48_ci=[float(t48.probe_lo), float(t48.probe_hi)], comb_old=float(t48.comb_old),
               d_probe=abs(t48.probe - PUB['probe48']), d_lo=abs(t48.probe_lo - PUB['probe48_lo']), d_hi=abs(t48.probe_hi - PUB['probe48_hi']), d_comb=abs(t48.comb_old - PUB['combined']))
    par['status'] = 'OK' if max(par['d_probe'], par['d_lo'], par['d_hi'], par['d_comb']) < 0.002 else 'WARN'
    (OUT / 'c24_parity.json').write_text(json.dumps(par, indent=1, default=float)); log('parity', par)
    Ls = ['# C24 / 2-11b follow-up (plan_batch_20261114b item 1) — POST-HOC, exploratory', '',
          f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_c24_conf_20261114.py` (CPU).', '',
          '## Parity', '', f'probe L48 {fmt(t48.probe, t48.probe_lo, t48.probe_hi)} (published 0.782 [0.754, 0.812]); old combined {t48.comb_old:.3f} (published 0.679): {par["status"]}', '',
          '## 1a (shard 0, replay job 11836635)', '', '```', json.dumps({k: v for k, v in r1a.items()}, indent=1, default=float), '```', '',
          '## 1b name-feature frequency excluding the current paper', '', '```', json.dumps(fd, indent=1), '```', '',
          '| layer | probe | name old | name new | combined old | combined new | probe - comb old | probe - comb new | comb old - new | papers / pairs |', '|---|---|---|---|---|---|---|---|---|---|']
    for r in T.itertuples():
        Ls.append(f'| L{r.layer} | {fmt(r.probe, r.probe_lo, r.probe_hi)} | {fmt(r.name_old, r.name_old_lo, r.name_old_hi)} | {fmt(r.name_new, r.name_new_lo, r.name_new_hi)} | '
                  f'{fmt(r.comb_old, r.comb_old_lo, r.comb_old_hi)} | {fmt(r.comb_new, r.comb_new_lo, r.comb_new_hi)} | {fmt(r.probe_minus_comb_old, r.probe_minus_comb_old_lo, r.probe_minus_comb_old_hi, "+")} | '
                  f'{fmt(r.probe_minus_comb_new, r.probe_minus_comb_new_lo, r.probe_minus_comb_new_hi, "+")} | {fmt(r.comb_old_minus_new, r.comb_old_minus_new_lo, r.comb_old_minus_new_hi, "+")} | {r.n_papers} / {r.n_pairs} |')
    t0 = T.iloc[0]
    Ls += ['', f'Position only: {fmt(t0.position, t0.position_lo, t0.position_hi)}; fame only: {fmt(t0.fame, t0.fame_lo, t0.fame_hi)} (layer-independent).', '',
           '## 1c (descriptive only: shard 0, replay confidence, raw scores, no fitting)', '', "```\n" + T1c.round(3).to_string(index=False) + "\n```" if len(T1c) else '(no qualifying papers)', '']
    (OUT / 'report.md').write_text('\n'.join(Ls) + '\n'); log('wrote', OUT / 'report.md')


if __name__ == '__main__':
    main()
