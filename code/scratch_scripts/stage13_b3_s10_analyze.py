"""Batch 3 items 3-1 / 3-2 (addendum 14): full hard check + report, CPU.

1. HARD CHECK on all 504 units (7 conditions x 72 shards, target + control rows):
   a. L24 and L48 (logit, jlens_public) per-token ranks vs stored Stage 10: exact on >= 99% of tokens (pooled), every other
      token within 4 bf16 units (bf16 distance of the gold logit to the stored rank, computed in the GPU job);
   b. paper-level title-specific signal at L48 (spec_mean_nlr, token mean, true - mean false_0..4) vs published Stage 10:
      target mean, control mean (summary_title/A_group_layer.csv) and target - control within bin
      (B_spec_target_vs_control_within_bin.csv), both readouts, |diff| <= 0.005.  Per-paper agreement = WARN only.
   Exit 3 (and summary_b3_s10_<item>/HARD_CHECK_FAILED) on FAIL; the report is still written, with a FAIL banner.
2. REPORT (plan): title-specific signal and target - control within citation bin at every layer of the grid (new layers from
   this item and earlier b3 items if complete + stored Stage 10 layers L24, 32, 40, 48, 50-62; final L63 as reference), by token
   position (all / first = token_index 0 / later) and role; team-cluster bootstrap CIs (archived team ids, 2,000 draws, one draw
   set shared by every cell); onset layer = first grid layer whose team CI excludes 0 (also first with lo > 0, and sustained).
Usage: stage13_b3_s10_analyze.py --item 3-1|3-2 [--tiny]
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b3_cols.py', 'b3_cols'); CK = load(H / '13_stage13/stage13_b3_checks.py', 'b3_checks')
G = load(H / '13_stage13/stage13_b3_s10_gpu.py', 'b3_s10_gpu'); s10 = G.s10
NB = 2000; SEED = 1414


def log(*x):
    try: print(time.strftime('%T'), *x, flush=True)
    except Exception: pass


def main():
    K.check_plan()
    ap = argparse.ArgumentParser(); ap.add_argument('--item', choices=['3-1', '3-2'], required=True); ap.add_argument('--tiny', action='store_true')
    a = ap.parse_args()
    R = K.s10_roots(a.item, a.tiny); root = G.s10root(a.tiny); m, _ = s10.verify(root)
    shards = [0] if a.tiny else list(range(m['n_shards']))
    min_n = 3 if a.tiny else s10.MIN_STRATUM
    papers = pd.read_parquet(root / 'cohort/papers.parquet', columns=['paper_id', 'shard', 'group_tight', 'citation_bin'])
    P_ = papers[papers.group_tight.isin(K.GROUPS) & papers.shard.isin(shards)].sort_values('paper_id').reset_index(drop=True)
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'token_index', 'role'])
    T = toks[toks.paper_id.isin(set(P_.paper_id))].sort_values('row_id').reset_index(drop=True)
    pidx = {p: i for i, p in enumerate(P_.paper_id)}; codes = T.paper_id.map(pidx).to_numpy(); NP = len(P_)
    grp = P_.group_tight.to_numpy(); cbin = P_.citation_bin.astype(str).to_numpy()
    log(f'{a.item}: {NP} papers, {len(T)} tokens, shards {len(shards)}')

    # ------------------------------------------------ load new units
    units = [(c, k) for c in K.CONDS for k in shards]
    miss = [u for u in units if not G.unit_path(R, *u).exists()]
    if miss: log(f'INCOMPLETE: {len(miss)} units missing, e.g. {miss[:5]}'); sys.exit(2)
    U = G.load_units(R, units)
    rowpos = pd.Series(np.arange(len(T)), index=T.row_id.to_numpy())
    NEW = {}                                                                     # (cond, readout, layer) -> ranks aligned to T
    pairs = U[units[0]]['meta']['pairs']
    for c in K.CONDS:
        for pn in pairs:
            arr = np.zeros(len(T), np.int64)
            for k in shards:
                u = U[(c, k)]; arr[rowpos[u['row_id']].to_numpy()] = u['rank'][u['meta']['pairs'].index(pn)]
            if (arr < 1).any(): raise RuntimeError(f'unfilled {c} {pn}')
            NEW[(c, pn)] = arr

    # ------------------------------------------------ 1a rank check
    rows, pooled = G.rank_rows(a.item, U, 'all units')
    K.write_csv(rows, R['summ'] / 'rank_match.csv', K.RANK_MATCH)
    HC = [dict(item=a.item, check='rank_exact_L24_L48', scope='all units pooled', value=pooled['share_exact'], threshold=K.RANK_EXACT_MIN,
               status='PASS' if pooled['share_exact'] >= K.RANK_EXACT_MIN else 'FAIL', kind='HARD', note=f"{pooled['n_exact']}/{pooled['n_tokens']} exact"),
          dict(item=a.item, check='mismatch_within_4_bf16', scope='all units pooled', value=pooled['max_ulps'], threshold=K.ULPS_MAX,
               status='PASS' if pooled['n_mismatch_le_ulps'] == pooled['n_mismatch'] else 'FAIL', kind='HARD',
               note=f"{pooled['n_mismatch_le_ulps']}/{pooled['n_mismatch']} mismatches within {K.ULPS_MAX} units")]
    for x in rows[rows.cond == 'ALL'].itertuples():
        HC.append(dict(item=a.item, check=f'rank_exact_{x.readout}_L{x.layer}', scope='per pair (WARN)', value=x.share_exact, threshold=K.RANK_EXACT_MIN,
                       status='PASS' if x.share_exact >= K.RANK_EXACT_MIN and x.n_mismatch_le_ulps == x.n_mismatch else 'WARN', kind='WARN', note=f'max ulps {x.max_ulps:.2f}'))

    # ------------------------------------------------ level per paper for any (cond -> ranks) set
    def levels(getr, mask=None):
        return {c: CK.paper_means(codes, NP, CK.nlr(getr(c)), mask) for c in K.CONDS}

    # ------------------------------------------------ 1b paper-level L48
    pub_g = None if a.tiny else pd.read_csv(K.R10 / 'summary_title/A_group_layer.csv')
    pub_b = None if a.tiny else pd.read_csv(K.R10 / 'summary_title/B_spec_target_vs_control_within_bin.csv')
    pt = None if a.tiny else pd.read_parquet(K.R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr'])
    for r in K.READOUTS:
        sp = CK.spec_total_topic(levels(lambda c: NEW[(c, K.pair_name(r, 48))]))['spec']
        if a.tiny:
            ref = G.paper_spec_ref_tiny(T, P_.paper_id.to_numpy(), r, 48, shards)
            refs = {g: float(np.nanmean(ref[grp == g])) for g in K.GROUPS}; ref_tc = CK.within_bin_point(ref, grp, cbin, min_n=min_n)[0]
        else:
            ref = pt[(pt.readout == r) & (pt.layer == 48)].set_index('paper_id').spec_mean_nlr.reindex(P_.paper_id).to_numpy()
            refs = {g: float(pub_g[(pub_g.group_tight == g) & (pub_g.readout == r) & (pub_g.layer == 48)].spec_mean_nlr_mean.iloc[0]) for g in K.GROUPS}
            ref_tc = float(pub_b[(pub_b.readout == r) & (pub_b.layer == 48)].spec_mean_nlr_diff.iloc[0])
        for g in K.GROUPS: HC.append(dict(item=a.item, **CK.scalar_check(f'paper_spec_L48_{r}_{g}_mean', float(np.nanmean(sp[grp == g])), refs[g], K.PAPER_SPEC_TOL, 'HARD', 'all papers')))
        HC.append(dict(item=a.item, **CK.scalar_check(f'paper_spec_L48_{r}_tc_within_bin', CK.within_bin_point(sp, grp, cbin, min_n=min_n)[0], ref_tc, K.PAPER_SPEC_TOL, 'HARD', 'all papers')))
        d = np.abs(sp - ref); sh = float(np.mean(d <= K.PAPER_SPEC_TOL))
        HC.append(dict(item=a.item, check=f'paper_spec_L48_{r}_share_within', scope='per paper', value=sh, threshold=K.PAPER_SHARE_WARN,
                       status='PASS' if sh >= K.PAPER_SHARE_WARN else 'WARN', kind='WARN', note=f'max per-paper |diff| {np.nanmax(d):.5f}'))
    hc = pd.DataFrame(HC)[K.HARDCHECK]; K.write_csv(hc, R['summ'] / 'hardcheck.csv', K.HARDCHECK)
    hard_fail = bool((hc.status == 'FAIL').any())
    try:
        for x in hc.itertuples(): log('CHECK', x.status, x.check, f'value={x.value:.6g} thr={x.threshold}', x.note)
    except Exception as e: log('WARNING', e)
    if hard_fail: R['fail'].parent.mkdir(parents=True, exist_ok=True); R['fail'].write_text(time.ctime() + '\n')

    # ------------------------------------------------ 2 report: layer grid
    new_layers = {it: K.ITEM_LAYERS[it] for it in ['3-1', '3-2']}
    SRC = {}                                                                     # (readout, layer) -> (source, getter)
    for r in K.READOUTS:
        for l in K.STORED_LAYERS:
            if not a.tiny or l in K.CHECK_LAYERS: SRC[(r, l)] = 'stage10'
        for it, ls in new_layers.items():
            Ri = K.s10_roots(it, a.tiny)
            done = it == a.item or all(G.unit_path(Ri, c, k).exists() for c in K.CONDS for k in shards)
            if done:
                for l in ls: SRC[(r, l)] = f'b3_{it}'
    if not a.tiny: SRC[('final', 63)] = 'stage10'
    other = {}
    def getter(c, r, l):
        src = SRC[(r, l)]
        if src == f'b3_{a.item}': return NEW[(c, K.pair_name(r, l))]
        if src == 'stage10':
            key = ('s10', c, r, l)
            if key not in other:
                arr = np.zeros(len(T), np.int64)
                for k in shards:
                    z = np.load(s10.out_file(root, r, l, k, c)); s = pd.Series(z['rank'], index=z['row_id'])
                    sel = T.shard.to_numpy() == k; arr[sel] = s.reindex(T.row_id[sel]).to_numpy()
                other[key] = arr
            return other[key]
        it = src[3:]; key = (it, c, r, l)
        if key not in other:
            Ri = K.s10_roots(it, a.tiny); arr = np.zeros(len(T), np.int64)
            for k in shards:
                z = np.load(G.unit_path(Ri, c, k)); mm = json.loads(str(z['meta']))
                arr[rowpos[z['row_id']].to_numpy()] = z['rank'][mm['pairs'].index(K.pair_name(r, l))]
            other[key] = arr
        return other[key]

    teams = None
    if a.tiny: TEAM = {p: i for i, p in enumerate(P_.paper_id)}               # tiny: paper = team (team file not needed)
    else:
        lib = load(H / '13_stage13/stage13_c13_s10lib.py', 'c13_s10lib'); TEAM = lib.team_ids()
    W = CK.team_weights(CK.factor_teams(P_.paper_id.to_numpy(), TEAM), NB, SEED)
    ti = T.token_index.to_numpy(); role = T.role.to_numpy()
    SUBS = [('all', 'all', None), ('first', 'all', ti == 0), ('later', 'all', ti > 0)] + [('all', ro, role == ro) for ro in K.ROLES[1:]]
    GM = {'target': grp == 'target', 'control': grp == 'control', 'target+control': np.ones(NP, bool)}
    GW = {g: W[:, gm] for g, gm in GM.items()}
    sig, tcr = [], []
    for (r, l), src in sorted(SRC.items(), key=lambda x: (x[0][0], x[0][1])):
        for pos, ro, mask in SUBS:
            lv = {c: CK.paper_means(codes, NP, CK.nlr(getter(c, r, l)), mask) for c in K.CONDS}
            st = CK.spec_total_topic(lv)
            for g, gm in GM.items():
                s_ = CK.mean_cluster_w(st['spec'][gm], GW[g])
                sig.append(dict(readout=r, layer=l, source=src, position=pos, role=ro, group=g, n_papers=s_[3], spec=s_[0], spec_lo=s_[1], spec_hi=s_[2],
                                true=float(np.nanmean(st['true'][gm])), total=float(np.nanmean(st['total'][gm])), topic=float(np.nanmean(st['topic'][gm]))))
            e = CK.strat_cluster_w(st['spec'], grp, cbin, W, min_n=min_n); e2 = CK.strat_cluster_w(st['true'], grp, cbin, W, min_n=min_n)
            tcr.append(dict(readout=r, layer=l, source=src, position=pos, role=ro, n_bins=e[3], n_target=e[4], n_control=e[5], tc_spec=e[0], tc_lo=e[1], tc_hi=e[2],
                            tc_true=e2[0], tc_true_lo=e2[1], tc_true_hi=e2[2]))
        log('layer done', r, l, src)
    SIG = pd.DataFrame(sig)[K.LAYER_SIGNAL]; TC = pd.DataFrame(tcr)[K.LAYER_TC]
    K.write_csv(SIG, R['summ'] / 'layer_signal.csv', K.LAYER_SIGNAL); K.write_csv(TC, R['summ'] / 'layer_tc.csv', K.LAYER_TC)

    on = []
    for r in K.READOUTS:
        for pos, ro, _ in SUBS:
            s = SIG[(SIG.readout == r) & (SIG.position == pos) & (SIG.role == ro)]
            for g in GM:
                x = s[s.group == g].sort_values('layer'); o = CK.onset(x.layer.tolist(), x.spec_lo, x.spec_hi)
                on.append(dict(readout=r, quantity='title_specific', position=pos, role=ro, group=g, layer_grid=' '.join(map(str, x.layer)),
                               onset_excl0=o[0], onset_sign=o[1], onset_pos=o[2], onset_pos_sustained=o[3]))
            x = TC[(TC.readout == r) & (TC.position == pos) & (TC.role == ro)].sort_values('layer'); o = CK.onset(x.layer.tolist(), x.tc_lo, x.tc_hi)
            on.append(dict(readout=r, quantity='target_minus_control_within_bin', position=pos, role=ro, group='target-control', layer_grid=' '.join(map(str, x.layer)),
                           onset_excl0=o[0], onset_sign=o[1], onset_pos=o[2], onset_pos_sustained=o[3]))
    ON = pd.DataFrame(on)[K.ONSET]; K.write_csv(ON, R['summ'] / 'onset.csv', K.ONSET)
    write_report(a, R, hc, rows, SIG, TC, ON, SRC, hard_fail, NP, len(T))
    if hard_fail: log('HARD CHECK FAILED -> exit 3'); sys.exit(3)
    log('DONE', R['report'])


def write_report(a, R, hc, rows, SIG, TC, ON, SRC, hard_fail, NP, NT):
    try:
        f3 = lambda v, lo, hi: '' if pd.isna(v) else f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
        grid = sorted({l for (r, l) in SRC if r != 'final'})
        new = sorted({l for (r, l), s in SRC.items() if s.startswith('b3_')})
        L = [f'# Batch 3 item {a.item}: Stage 10 readouts at new layers (addendum 14)' + (' — TINY TEST' if a.tiny else ''), '',
             f'Generated {time.ctime()}. Plan `prereg_addendum14.json` (sha256 {K.PLAN_SHA[:12]}…). {NP} papers (target + control), {NT} name tokens, '
             'conditions true, false_0..4, delete; readouts logit and public J-lens (Neuronpedia 557); Stage 10 fast path.', '']
        L += ['**HARD CHECK FAILED — numbers below are not to be used until the cause is found.**' if hard_fail else '**Hard check: PASS.**', '',
              '## 1. Hard check', '', '| check | scope | value | threshold | status | note |', '|---|---|---|---|---|---|']
        L += [f'| {x.check} | {x.scope} | {x.value:.6g} | {x.threshold} | {x.status} | {x.note} |' for x in hc.itertuples()]
        L += ['', 'Per pair and condition: `rank_match.csv`.', '',
              f'## 2. Layer grid', '', f'Layers with data: {", ".join(f"L{l}" for l in grid)} (+ final L63). New in batch 3: {", ".join(f"L{l}" for l in new)}. '
              'Not computed anywhere: ' + ', '.join(f'L{l}' for l in range(0, 63) if l not in grid) + '. Onset = first layer of this grid whose 95% team-cluster CI excludes 0.', '']
        for r in K.READOUTS:
            L += [f'## 3. {r}: title-specific signal (all tokens) and target − control within citation bin', '',
                  '| layer | source | target | control | target+control | target − control (within bin) |', '|---|---|---|---|---|---|']
            s = SIG[(SIG.readout == r) & (SIG.position == 'all') & (SIG.role == 'all')]; t = TC[(TC.readout == r) & (TC.position == 'all') & (TC.role == 'all')]
            for l in sorted(s.layer.unique()):
                c = {g: s[(s.layer == l) & (s.group == g)].iloc[0] for g in ['target', 'control', 'target+control']}; d = t[t.layer == l].iloc[0]
                L.append(f"| L{l} | {c['target'].source} | {f3(c['target'].spec, c['target'].spec_lo, c['target'].spec_hi)} | {f3(c['control'].spec, c['control'].spec_lo, c['control'].spec_hi)} | "
                         f"{f3(c['target+control'].spec, c['target+control'].spec_lo, c['target+control'].spec_hi)} | {f3(d.tc_spec, d.tc_lo, d.tc_hi)} |")
            fs = SIG[(SIG.readout == 'final') & (SIG.position == 'all') & (SIG.role == 'all')]; ft = TC[(TC.readout == 'final') & (TC.position == 'all') & (TC.role == 'all')]
            if len(fs) and len(ft):
                c = {g: fs[fs.group == g].iloc[0] for g in ['target', 'control', 'target+control']}; d = ft.iloc[0]
                L.append(f"| final L63 | stage10 | {f3(c['target'].spec, c['target'].spec_lo, c['target'].spec_hi)} | {f3(c['control'].spec, c['control'].spec_lo, c['control'].spec_hi)} | "
                         f"{f3(c['target+control'].spec, c['target+control'].spec_lo, c['target+control'].spec_hi)} | {f3(d.tc_spec, d.tc_lo, d.tc_hi)} |")
            L.append('')
        L += ['## 4. Onset layers (first grid layer whose team CI excludes 0; sign; first with lo > 0; sustained lo > 0 to L62)', '',
              '| readout | quantity | position | role | group | onset (excl. 0) | sign | first lo>0 | sustained |', '|---|---|---|---|---|---|---|---|---|']
        for x in ON[ON.role.isin(['all', 'surname_first', 'initial_first', 'given_first'])].itertuples():
            L.append(f'| {x.readout} | {x.quantity} | {x.position} | {x.role} | {x.group} | {x.onset_excl0} | {x.onset_sign} | {x.onset_pos} | {x.onset_pos_sustained} |')
        L += ['', '## 5. By position (first token / later tokens), target − control within bin', '', '| readout | layer | first | later |', '|---|---|---|---|']
        for r in K.READOUTS:
            t = TC[TC.readout == r]
            for l in sorted(t.layer.unique()):
                p1 = t[(t.layer == l) & (t.position == 'first') & (t.role == 'all')].iloc[0]; p2 = t[(t.layer == l) & (t.position == 'later') & (t.role == 'all')].iloc[0]
                L.append(f'| {r} | L{l} | {f3(p1.tc_spec, p1.tc_lo, p1.tc_hi)} | {f3(p2.tc_spec, p2.tc_lo, p2.tc_hi)} |')
        L += ['', 'Roles (initial_first, given_first, given_cont, surname_first, surname_cont, particle_first, punct): `layer_signal.csv` / `layer_tc.csv` '
              '(punct is the negative control).', '', '## 6. Notes', '',
              '- Title-specific signal = per paper, token mean of log10(1/rank) under the true title minus the mean over the 5 matched false titles; '
              'target − control within citation bins with >= 30 papers in both groups, weights n_t n_c/(n_t+n_c) (Stage 10 definition).',
              '- CIs: team-cluster bootstrap (archived team ids, 2,000 draws, seed 1414, one draw set shared by every layer and cell). '
              'Stage 10 published CIs were paper bootstraps, so stored-layer CIs here differ from the published ones; point estimates are the same.',
              '- L24 and L48 rows use the stored Stage 10 ranks (the recomputed ranks are used only for the hard check).',
              '- Outputs: `' + str(R['summ']) + '/` (hardcheck.csv, rank_match.csv, layer_signal.csv, layer_tc.csv, onset.csv).']
        R['report'].parent.mkdir(parents=True, exist_ok=True); R['report'].write_text('\n'.join(L) + '\n'); log('report', R['report'])
    except Exception as e:
        log('WARNING report writing failed (results CSVs are saved):', repr(e))


if __name__ == '__main__':
    main()
