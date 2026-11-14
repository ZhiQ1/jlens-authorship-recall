"""C24 option B analysis (CPU; POST-HOC, exploratory). New file; nothing existing is edited.
Inputs: generation-time confidence from option B (c24_optB_20261114/shard_KKK/names_KKK.parquet, K=1..47) and option A
(c24_regen_20261114/names_000.parquet, shard 0, same code). Same data/fit/bootstrap as stage13_c24_conf_20261114.py part 1b
(within-paper AUROC over M-H pairs on target papers, fit_oof, team bootstrap 2,000 draws seed 12, all scores on one draw set).
Reports:
 (1) regeneration token identity vs the stored 2-11b tokens (papers; positions on the common prefix);
 (2) |replay - generation| of name mean log-prob: median, share > 0.01 (all shards);
 (3) confidence baselines (generation-time): raw lp_mean, raw lp_first, raw -entropy (no fitting) and conf3 = fit_oof of the three;
 (4) probe - comb_new (parity with the published +0.146 at L48) and probe - comb_conf (comb_new features + conf3 features),
     probe - conf3; layers where any confidence baseline is above the probe are listed separately.
Restricted to M/H names whose generation-time confidence is valid (regenerated prefix identical through the name); count reported.
Usage: analyze [--allow-missing]  (default requires all 48 shards)"""
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('c24c', H / '13_stage13/stage13_c24_conf_20261114.py'); CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
RB, AN, V1, V2, B, ROOT = CC.RB, CC.AN, CC.V1, CC.V2, CC.B, CC.ROOT
R13 = CC.R13; OA = R13 / 'c24_regen_20261114'; OB = R13 / 'c24_optB_20261114'; OUT = R13 / 'summary_c24_optB_20261114'
PUB_PMC48 = 0.146


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
ci = CC.ci; fmt = CC.fmt


def shard_dir(k): return OA if k == 0 else OB / f'shard_{k:03d}'


def load_conf(allow_missing):
    import pandas as pd
    ks = list(range(AN.N_SHARDS)); have = [k for k in ks if (shard_dir(k) / f'names_{k:03d}.parquet').exists()]
    miss = sorted(set(ks) - set(have))
    if miss and not allow_missing: raise SystemExit(f'missing shards {miss}')
    NM = pd.concat([pd.read_parquet(shard_dir(k) / f'names_{k:03d}.parquet') for k in have], ignore_index=True)
    RG = pd.concat([pd.read_csv(shard_dir(k) / f'regen_papers_{k:03d}.csv') for k in have], ignore_index=True)
    PO = pd.concat([pd.read_parquet(shard_dir(k) / f'positions_{k:03d}.parquet', columns=['paper_id', 'step', 'gen_valid', 'rep_argmax', 'tok']) for k in have], ignore_index=True)
    cp = dict(zip(RG.paper_id, RG.common_prefix)); ns = dict(zip(RG.paper_id, RG.n_stored))
    v = NM[NM.gen_valid.astype(bool)].copy(); a = (v.rep_lp_mean - v.gen_lp_mean).abs()
    regen = dict(shards=len(have), missing=miss, papers=len(RG), papers_identical=int(RG.identical.sum()), share_papers_identical=float(RG.identical.mean()),
                 positions_stored=int(RG.n_stored.sum()), positions_common_prefix=int(np.minimum(RG.common_prefix, RG.n_stored).sum()),
                 share_positions_common_prefix=float(np.minimum(RG.common_prefix, RG.n_stored).sum() / RG.n_stored.sum()),
                 replay_argmax_agreement=float((PO.rep_argmax == PO.tok).mean()),
                 names_MH=int(len(NM)), names_gen_valid=int(len(v)),
                 d_lp_mean_median=float(a.median()), d_lp_mean_mean=float(a.mean()), d_lp_mean_max=float(a.max()), d_lp_mean_share_gt_0p01=float((a > 0.01).mean()),
                 rule_1a_median_lt_0p01=bool(a.median() < 0.01))
    log('regen', json.dumps(regen, default=float)); return v, regen


def analyze(v):
    import pandas as pd
    shards = list(range(AN.N_SHARDS))
    NA = pd.concat([pd.read_parquet(ROOT / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    zs = [np.load(ROOT / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    v = v.copy(); v['key'] = v.paper_id + '|' + v.item_index.astype(str); cm = v.set_index('key')
    n_all = len(N); N = N[N.key.isin(cm.index)].reset_index(drop=True)
    ix = np.array([kidx[k_] for k_ in N.key])
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy()
    RB.V3.patch(); P, _ = B.load_papers(); pool = B.Pool(P)
    exc = np.array([len(pool.full.get(' '.join(B.words(nm)), set()) - {pid}) for nm, pid in zip(N.name, N.paper_id)], float)
    XP = N[['item_index', 'item_rel']].to_numpy(float); L = N.name_len_chars.to_numpy(float)
    XS_new = np.stack([L, np.log1p(exc)], 1); XF = RB.fame_features(N, P)
    lpm = N.key.map(cm.gen_lp_mean).to_numpy(float); lpf = N.key.map(cm.gen_lp_first).to_numpy(float); ent = N.key.map(cm.gen_ent_pre).to_numpy(float)
    XC = np.stack([lpm, lpf, -ent], 1)
    base = {}
    for nm_, X_ in [('comb_new', np.concatenate([XP, XS_new, XF], 1)), ('conf3', XC), ('comb_conf', np.concatenate([XP, XS_new, XF, XC], 1))]:
        base[nm_], Cb, _ = V1.fit_oof(X_, y, fold); log('baseline', nm_, 'C', Cb)
    raw = dict(conf_lp_mean=lpm, conf_lp_first=lpf, conf_neg_entropy=-ent)
    names = ['probe', 'comb_new', 'conf3', 'comb_conf'] + list(raw)
    rows = []
    for l in AN.LAYERS:
        X = np.concatenate([z[f'name_mean@{l}'] for z in zs])[ix].astype(np.float32)
        pr, C, _ = V1.fit_oof(X, y, fold)
        scs = [pr, base['comb_new'], base['conf3'], base['comb_conf']] + [raw[k] for k in raw]
        st = [V2.pair_stats(paper[tgt], y[tgt], sc[tgt]) for sc in scs]
        common = set.intersection(*[set(s) for s in st]); st = [{p_: s[p_] for p_ in common} for s in st]
        est, bt, npap, npair = V2.within_auroc(st, PT)
        r = dict(layer=l, C=C, n_papers=npap, n_pairs=npair)
        for j, nm_ in enumerate(names): r[nm_] = est[j]; r[nm_ + '_lo'], r[nm_ + '_hi'] = ci(bt[:, j])
        jj = {nm_: j for j, nm_ in enumerate(names)}
        for b_ in names[1:]:
            d = bt[:, 0] - bt[:, jj[b_]]; lab = 'probe_minus_' + b_; r[lab] = est[0] - est[jj[b_]]; r[lab + '_lo'], r[lab + '_hi'] = ci(d); r[lab + '_p_le0'] = float((d <= 0).mean())
        d = bt[:, jj['comb_conf']] - bt[:, jj['comb_new']]; r['comb_conf_minus_comb_new'] = est[jj['comb_conf']] - est[jj['comb_new']]; r['ccn_lo'], r['ccn_hi'] = ci(d)
        rows.append(r); log(f'L{l}', {k: round(x, 4) if isinstance(x, float) else x for k, x in r.items()})
    return pd.DataFrame(rows), dict(names_MH_all=n_all, names_used=len(N), target_names_used=int(tgt.sum()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['analyze']); ap.add_argument('--allow-missing', action='store_true'); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    v, regen = load_conf(a.allow_missing); T, cnt = analyze(v)
    T.to_csv(OUT / 'c24_optB_table.csv', index=False); (OUT / 'c24_optB_regen.json').write_text(json.dumps(dict(regen=regen, counts=cnt), indent=1, default=float))
    conf_cols = ['conf3', 'conf_lp_mean', 'conf_lp_first', 'conf_neg_entropy']
    above = [dict(layer=int(r.layer), baseline=c, value=float(getattr(r, c)), probe=float(r.probe)) for r in T.itertuples() for c in conf_cols if getattr(r, c) > r.probe]
    t48 = T.set_index('layer').loc[48]
    Ls = ['# C24 option B — generation-time confidence baseline (POST-HOC, exploratory)', '',
          f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_c24_optB_analyze_20261114.py` (CPU).' + (' **PARTIAL: missing shards %s**' % regen['missing'] if regen['missing'] else ''), '',
          '## (1) regeneration identity and (2) replay vs generation', '', '```', json.dumps(dict(regen=regen, counts=cnt), indent=1, default=float), '```', '',
          f'Parity: probe − comb_new at L48 {fmt(t48.probe_minus_comb_new, t48.probe_minus_comb_new_lo, t48.probe_minus_comb_new_hi, "+")} (published +0.146 on all M/H names; here restricted to names with valid generation-time confidence).', '',
          '## (3) confidence baselines and (4) probe increments (target papers, within-paper AUROC, team bootstrap 2,000)', '',
          '| layer | probe | conf3 (fitted) | lp_mean raw | lp_first raw | −entropy raw | comb_new | comb_conf | probe − comb_new | probe − comb_conf | probe − conf3 | papers / pairs |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in T.itertuples():
        Ls.append(f'| L{r.layer} | {fmt(r.probe, r.probe_lo, r.probe_hi)} | {fmt(r.conf3, r.conf3_lo, r.conf3_hi)} | {fmt(r.conf_lp_mean, r.conf_lp_mean_lo, r.conf_lp_mean_hi)} | '
                  f'{fmt(r.conf_lp_first, r.conf_lp_first_lo, r.conf_lp_first_hi)} | {fmt(r.conf_neg_entropy, r.conf_neg_entropy_lo, r.conf_neg_entropy_hi)} | {fmt(r.comb_new, r.comb_new_lo, r.comb_new_hi)} | '
                  f'{fmt(r.comb_conf, r.comb_conf_lo, r.comb_conf_hi)} | {fmt(r.probe_minus_comb_new, r.probe_minus_comb_new_lo, r.probe_minus_comb_new_hi, "+")} | '
                  f'{fmt(r.probe_minus_comb_conf, r.probe_minus_comb_conf_lo, r.probe_minus_comb_conf_hi, "+")} | {fmt(r.probe_minus_conf3, r.probe_minus_conf3_lo, r.probe_minus_conf3_hi, "+")} | {r.n_papers} / {r.n_pairs} |')
    Ls += ['', '## Layers where a confidence baseline is above the probe', '', json.dumps(above, indent=1) if above else 'none', '']
    (OUT / 'report.md').write_text('\n'.join(Ls) + '\n'); log('wrote', OUT / 'report.md')


if __name__ == '__main__':
    main()
