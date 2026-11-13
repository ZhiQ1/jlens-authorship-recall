"""Team-cluster CIs for the Stage 10-12 CIs that enter core conclusions C01-C24 (2026-11-12, CPU, read-only on frozen outputs).

For each quantity:
  1. REPRODUCE the published paper-level bootstrap CI by re-running the frozen estimator functions with their original RNG seed
     and call order (outputs redirected to a scratch dir; frozen scripts are only imported, never edited):
       Stage 10 6.4  : 351_stage10.title analysis sequence, rng 3511 (A_group_layer -> negative_control_by_role -> B_spec)
       Stage 10 R0   : stage10_extra_r0.py, rng 3512, first stratified_diff call
       Stage 10 R1   : stage10_extra_r0r1.py, rng 3513: stage10() -> probe() -> per_author loop on stored R1_author_scores.parquet
       Stage 11 E1/E2: stage11_analyze.py, rng 3611: patch_section(E1) -> patch_section(E1t) -> ko_section(E2)
       Stage 12 F2   : stage12_analyze.main, rng 3713, on a scratch ROOT whose raw/ and config/ are symlinks to the real ones
     Check: reproduced lo/hi equal the published file to 3-decimal rounding (also reports max |diff|). FAIL -> no team CI reported
     for that quantity (marked STOP).
  2. TEAM-CLUSTER bootstrap: archived Stage 13 team ids (stage13_c13_s10lib.team_ids = stage13_cpu.group_folds, archived folds),
     2,000 multinomial team draws, seed 1414, one draw per paper population (Stage 10 target+control 6,841 papers = the same draw
     as b3 3-1; Stage 11 sample 1,186; Stage 12 F2 sample minus 3 excluded; R1 495 papers). Same point estimate, same strata /
     within-bin weights (bins with >= 30 per group), same ratio-of-means for E1/E2.
Outputs: 381_stage13/summary_teamci_s10_12/{teamci_s10_12.csv, replay_check.csv}; scratch replay files under .../replay/.
"""
import importlib.util, json, os, sys, time, warnings
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R12 = J / '351_stage10', J / '361_stage11', J / '371_stage12'
OUT = J / '381_stage13/summary_teamci_s10_12'; RP = OUT / 'replay'
NB, SEED = 2000, 1414
warnings.simplefilter('ignore', RuntimeWarning)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def log(*x): print(time.strftime('%T'), *x, flush=True)


CK = load(H / '13_stage13/stage13_b3_checks.py', 'b3_checks')
LIB = load(H / '13_stage13/stage13_c13_s10lib.py', 'c13_s10lib')
TEAM = LIB.team_ids()


def W_for(pids):
    return CK.team_weights(CK.factor_teams(list(pids), TEAM), NB, SEED).astype(np.float64)


def ratio_team(num, den, W):
    num, den = np.asarray(num, float), np.asarray(den, float)
    return float(num.mean() / den.mean()), *np.percentile((W @ num) / (W @ den), [2.5, 97.5])


ROWS, CHK = [], []


def add(cid, stage, qty, src, est, plo, phi, rlo, rhi, tlo, thi, n, note=''):
    ok = (round(plo, 3) == round(rlo, 3)) and (round(phi, 3) == round(rhi, 3))
    CHK.append(dict(conclusion=cid, quantity=qty, published_lo=plo, published_hi=phi, replay_lo=rlo, replay_hi=rhi,
                    max_abs_diff=max(abs(plo - rlo), abs(phi - rhi)), match_3dp=ok))
    ROWS.append(dict(conclusion=cid, stage=stage, quantity=qty, source=src, n=n, estimate=est, paper_lo=plo, paper_hi=phi,
                     replay_match=ok, team_lo=tlo if ok else np.nan, team_hi=thi if ok else np.nan,
                     width_ratio=(thi - tlo) / (phi - plo) if ok else np.nan, status='OK' if ok else 'STOP (paper CI not reproduced)', note=note))
    log('ADD', cid, qty, f'{est:+.4f} paper [{plo:+.4f},{phi:+.4f}] replay [{rlo:+.4f},{rhi:+.4f}] team [{tlo:+.4f},{thi:+.4f}]', 'MATCH' if ok else 'NO MATCH')


def stage10():
    s10 = load(H / '10_stage10/351_stage10.py', 's10')
    ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet')
    pub = pd.read_csv(R10 / 'summary_title/B_spec_target_vs_control_within_bin.csv')
    # ---- replay rng 3511 sequence
    rng = np.random.default_rng(3511)
    main = ['spec_mean_nlr', 'spec_author_mean_nlr', 'spec_mean_nlr_surname_first', 'total_mean_nlr', 'topic_mean_nlr', 'spec_strict_mean_nlr', 'tail_fraction']
    s10.group_means(ds, ['group_tight'], main, rng, sums=[]); log('replay A_group_layer')
    d2 = ds.copy(); d2['all'] = 'all'
    roles = [f'spec_{x}' for x in s10.TITLE_BASE if x.startswith('mean_nlr_')]
    s10.group_means(d2, ['all'], roles, rng, sums=[]); log('replay negative_control_by_role'); del d2
    rep = s10.stratified_diff(ds, 'group_tight', 'target', 'control', 'citation_bin', main[:3] + ['spec_strict_mean_nlr'], rng)
    rep.to_csv(RP / 's10_B_spec_replay.csv', index=False)
    m = rep.merge(pub, on=['readout', 'layer'], suffixes=('_r', '_p'))
    allmax = float(np.max(np.abs(m[['spec_mean_nlr_lo_r', 'spec_mean_nlr_hi_r']].to_numpy() - m[['spec_mean_nlr_lo_p', 'spec_mean_nlr_hi_p']].to_numpy())))
    log('Stage 10 B_spec replay: rows', len(m), 'max |diff| lo/hi over all rows', allmax)
    # ---- R0 replay (rng 3512, first call)
    rng0 = np.random.default_rng(3512)
    mets0 = ['spec_mean_nlr', 'spec_author_mean_nlr', 'spec_mean_nlr_surname_first', 'total_mean_nlr', 'topic_mean_nlr']
    rep0 = s10.stratified_diff(ds[ds.recall_level == 'R0'], 'group_tight', 'target', 'control', 'citation_bin', mets0, rng0)
    pub0 = pd.read_csv(R10 / 'summary_r0/B_spec_target_vs_control_within_bin_R0.csv')
    # ---- team draws: target + control papers (same population and seed as b3 3-1)
    P = ds[ds.group_tight.isin(['target', 'control'])].drop_duplicates('paper_id').sort_values('paper_id')[['paper_id', 'group_tight', 'citation_bin', 'recall_level']].reset_index(drop=True)
    W = W_for(P.paper_id); grp = P.group_tight.to_numpy(); cb = P.citation_bin.astype(str).to_numpy(); r0 = P.recall_level.to_numpy() == 'R0'
    def x_of(r, l):
        return ds[(ds.readout == r) & (ds.layer == l)].set_index('paper_id').spec_mean_nlr.reindex(P.paper_id).to_numpy(float)
    items = [('C01', 'final', 63, 'output (final L63)'), ('C01', 'logit', 24, 'logit L24'), ('C01', 'logit', 32, 'logit L32'),
             ('C01', 'logit', 50, 'logit L50'), ('C01', 'logit', 56, 'logit L56'), ('C01', 'logit', 62, 'logit L62'),
             ('C01', 'jlens_public', 48, 'public J-lens L48'), ('C01', 'jlens_public', 57, 'public J-lens L57')]
    src = 'R10/summary_title/B_spec_target_vs_control_within_bin.csv'
    for cid, r, l, nm in items:
        p = pub[(pub.readout == r) & (pub.layer == l)].iloc[0]; q = rep[(rep.readout == r) & (rep.layer == l)].iloc[0]
        e = CK.strat_cluster_w(x_of(r, l), grp, cb, W)
        assert abs(e[0] - p.spec_mean_nlr_diff) < 1e-9, (r, l, e[0], p.spec_mean_nlr_diff)
        add(cid, 'Stage 10', f'title-specific target - control within bin, {nm}', src, e[0], p.spec_mean_nlr_lo, p.spec_mean_nlr_hi,
            q.spec_mean_nlr_lo, q.spec_mean_nlr_hi, e[1], e[2], f'{e[4]} / {e[5]} ({e[3]} bins)')
    p = pub0[(pub0.readout == 'final') & (pub0.layer == 63)].iloc[0]; q = rep0[(rep0.readout == 'final') & (rep0.layer == 63)].iloc[0]
    x = x_of('final', 63); x[~r0] = np.nan
    e = CK.strat_cluster_w(x, grp, cb, W); assert abs(e[0] - p.spec_mean_nlr_diff) < 1e-9
    add('C01', 'Stage 10', 'R0 papers only, title-specific target - control within bin, output', 'R10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv (r0_sensitivity.md l.16)',
        e[0], p.spec_mean_nlr_lo, p.spec_mean_nlr_hi, q.spec_mean_nlr_lo, q.spec_mean_nlr_hi, e[1], e[2], f'{e[4]} / {e[5]} ({e[3]} bins)')
    return allmax


def stage10_r1():
    """C17. rng 3513 is consumed by stage10() and probe() before the per-author loop; replay those (outputs to scratch)."""
    x = load(H / '10_stage10/stage10_extra_r0r1.py', 'r0r1')
    S = RP / 'r0r1'; S.mkdir(parents=True, exist_ok=True); L = []
    ds = x.stage10(L, S); log('r0r1 stage10 replayed')
    x.probe(L, S, ds); log('r0r1 probe replayed')
    A = pd.read_parquet(R10 / 'summary_r0r1/R1_author_scores.parquet')
    pub = pd.read_csv(R10 / 'summary_r0r1/R1_author_written_minus_missed.csv')
    res = None
    for (r, l), s in A.groupby(['readout', 'layer']):
        for excl in (False, True):
            t = s[s.author_index > 0] if excl else s
            g = t.groupby(['paper_id', 'hit'])[['spec', 'true', 'delete']].mean().unstack('hit').dropna()
            if g.empty: continue
            for mt in ['spec', 'true', 'delete']:
                dv = (g[(mt, True)] - g[(mt, False)]).to_numpy(); e = x.boot_mean(dv)
                if r == 'final' and l == 63 and not excl and mt == 'spec': res = (e, g.index.to_numpy(), dv)
    (e, pids, dv) = res
    p = pub[(pub.readout == 'final') & (pub.layer == 63) & (~pub.excl_first_author)].iloc[0]
    assert abs(e[0] - p.spec_diff) < 1e-12
    W = W_for(pids); t = CK.mean_cluster_w(dv, W)
    add('C17', 'Stage 10', 'R1 papers: written - missed author, title-specific, output (paired within paper)', 'R10/summary_r0r1/R1_author_written_minus_missed.csv row 2',
        t[0], p.spec_lo, p.spec_hi, e[1], e[2], t[1], t[2], f'{len(dv)} papers')


def stage11():
    a11 = load(H / '11_stage11/stage11_analyze.py', 'a11_replay')                     # fresh module -> rng 3611
    S = RP / 's11'; S.mkdir(parents=True, exist_ok=True)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    d, layers = a11.load_unit_dir(R11 / 'raw/patch'); a11.patch_section('E1', '', d, layers, toks, smp, S)
    dt, lt = a11.load_unit_dir(R11 / 'raw/patch_title'); a11.patch_section('E1t', '', dt, lt, toks, smp, S); del dt
    k, kl = a11.load_unit_dir(R11 / 'raw/knockout'); a11.ko_section('E2', '', k, kl, d, toks, smp, S)
    log('Stage 11 replayed')
    rE1, pE1 = pd.read_csv(S / 'E1_recovery.csv'), pd.read_csv(R11 / 'summary/E1_recovery.csv')
    rE2, pE2 = pd.read_csv(S / 'E2_knockout.csv'), pd.read_csv(R11 / 'summary/E2_knockout.csv')
    # team: paper means exactly as patch_section / ko_section
    t = toks.set_index('row_id').loc[d['row_id']].reset_index()
    df = pd.DataFrame({'paper_id': t.paper_id, 'true': a11.nlr(d['rank_true']), 'false': a11.nlr(d['rank_false'])})
    for i, l in enumerate(layers): df[f'p{l}'] = a11.nlr(d['rank_patch'][:, i])
    pp = df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    W = W_for(pp.paper_id); den = (pp['true'] - pp['false']).to_numpy()
    for l in (48, 52):
        e = ratio_team((pp[f'p{l}'] - pp['false']).to_numpy(), den, W)
        p = pE1[(pE1.group == 'all') & (pE1.layer == l)].iloc[0]; q = rE1[(rE1.group == 'all') & (rE1.layer == l)].iloc[0]
        assert abs(e[0] - p.recovery) < 1e-12
        add('C02', 'Stage 11', f'E1 recovery (false_0, all papers), L{l}', 'R11/summary/E1_recovery.csv', e[0], p.rec_lo, p.rec_hi, q.rec_lo, q.rec_hi, e[1], e[2], f'{len(pp)} papers')
    tk = toks.set_index('row_id').loc[k['row_id']].reset_index()
    kd = pd.DataFrame({'row_id': k['row_id'], 'paper_id': tk.paper_id})
    for i, l in enumerate(kl): kd[f'k{l}'] = a11.nlr(k['rank_ko'][:, i])
    kd = kd.merge(pd.DataFrame({'row_id': d['row_id'], 'true': a11.nlr(d['rank_true']), 'false': a11.nlr(d['rank_false'])}), on='row_id')
    kp = kd.drop(columns='row_id').groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    W2 = W_for(kp.paper_id); den2 = (kp['true'] - kp['false']).to_numpy()
    for l in (0, 52):
        e = ratio_team((kp['k64'] - kp[f'k{l}']).to_numpy(), den2, W2)
        p = pE2[(pE2.group == 'all') & (pE2.start_layer == l)].iloc[0]; q = rE2[(rE2.group == 'all') & (rE2.start_layer == l)].iloc[0]
        assert abs(e[0] - p.loss_fraction) < 1e-12
        add('C03', 'Stage 11', f'E2 knockout loss (all papers), from L{l}', 'R11/summary/E2_knockout.csv', e[0], p.lo, p.hi, q.lo, q.hi, e[1], e[2], f'{len(kp)} papers')


def stage12():
    s11 = load(H / '11_stage11/361_stage11.py', 's11'); s10 = s11.s10
    a12 = load(H / '12_stage12/stage12_analyze.py', 'a12_replay')                       # fresh module -> rng 3713
    root = RP / 's12root'; root.mkdir(parents=True, exist_ok=True)
    for n in ('raw', 'config'):
        if not (root / n).exists(): os.symlink(R12 / n, root / n)
    a12.main(root, R10, s10, s11); log('Stage 12 replayed')
    rep, pub = pd.read_csv(root / 'summary/F2_author_lens.csv'), pd.read_csv(R12 / 'summary/F2_author_lens.csv')
    q = rep[(rep.layer == 62) & (rep.position == 'name')].iloc[0]; p = pub[(pub.layer == 62) & (pub.position == 'name')].iloc[0]
    # team: rebuild sp as in main()
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    per = {}
    for c in [c for c in s10.condition_names() if c != 'delete' and (R12 / 'raw/alens_read' / c).exists()]:
        z = a12.load_dir(R12 / 'raw/alens_read' / c); df = pd.DataFrame({'row_id': z['row_id'], **{k: a12.nlr(z[k]) for k in z if k.startswith('alens@')}}).merge(toks, on='row_id')
        per[c] = df.drop(columns='row_id').groupby('paper_id').mean()
    common = per['true'].index
    for c in per: common = common.intersection(per[c].index)
    drop = set(json.loads((R12 / 'config/alens_eval_exclude.json').read_text())['paper_ids']); common = common[~common.isin(drop)]
    spec = per['true'].loc[common] - sum(per[c].loc[common] for c in per if c != 'true') / (len(per) - 1)
    sp = spec.join(smp.set_index('paper_id')).reset_index()
    col = [c for c in spec.columns if c.split('@')[1] == '62' and c.split('@')[2] == 'name'][0]
    W = W_for(sp.paper_id)
    e = CK.strat_cluster_w(sp[col].to_numpy(float), sp.group.to_numpy(), sp.citation_bin.astype(str).to_numpy(), W)
    assert abs(e[0] - p.tc) < 1e-12, (e[0], p.tc)
    add('C16', 'Stage 12', 'F2 author-prompt lens, name position, target - control within bin, L62', 'R12/summary/F2_author_lens.csv (x5_layer_order.csv row 17)',
        e[0], p.tc_lo, p.tc_hi, q.tc_lo, q.tc_hi, e[1], e[2], f'{e[4]} / {e[5]} ({e[3]} bins)')


def main():
    OUT.mkdir(parents=True, exist_ok=True); RP.mkdir(parents=True, exist_ok=True)
    parts = sys.argv[1:] or ['s10', 's11', 's12', 'r1']
    info = {}
    for nm, f in (('s10', stage10), ('s11', stage11), ('s12', stage12), ('r1', stage10_r1)):
        if nm not in parts: continue
        try: info[nm] = f()
        except Exception as ex:
            import traceback; traceback.print_exc(); log('PART FAILED', nm, ex); info[nm] = f'FAILED: {ex}'
        pd.DataFrame(ROWS).to_csv(OUT / f'teamci_s10_12_{"_".join(parts)}.csv', index=False)
        pd.DataFrame(CHK).to_csv(OUT / f'replay_check_{"_".join(parts)}.csv', index=False)
    (OUT / f'info_{"_".join(parts)}.json').write_text(json.dumps(info, default=str, indent=1))
    log('DONE', info)


if __name__ == '__main__':
    main()
