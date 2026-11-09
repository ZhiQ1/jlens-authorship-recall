"""2-11b analysis (addendum 15, locked: config/prereg_addendum15.json, sha256 checked). CPU.
Reads b2_gennames_b/{names,raw,papers,h2}/shard_KKK.* (npz 'key' is a pickled object array: allow_pickle=True, own files).
Labels M / H enter the analysis; P (partial match) and U_* are excluded from M-vs-H and only counted.
Per layer (L16..L56) x position: (ii) name_mean = PRIMARY, (i) pred_first = SECONDARY, last = descriptive.
Probe: L2 logistic, C on fold 0, 5-fold out-of-fold on the archived author-team folds, training-fold standardisation
(v1 fit_oof), one pooled fit over target + control M/H names. Within-paper AUROC on TARGET papers with >= 1 M and >= 1 H
(pairs within paper, ties 0.5), 95% CI by author-team cluster bootstrap (2,000 draws, shared by all scores -> paired diffs).
Baselines (same fit): position (index, relative index) and string (length in characters, log(1 + cohort frequency of the full
name)); signal = CI(probe - position) > 0 AND CI(probe - string) > 0. Shuffled-label control (labels permuted within training
folds, rng 1212). Control papers: point estimates only. Minimum size: qualifying target papers < 100 or their M names < 200 ->
descriptive only. Descriptive split of H: in the cohort author pool (exact = primary definition, rule = secondary).
Usage: --root DIR [--out REPORT.md] [--nb 2000] [--layers 16,24,...]
"""
import argparse, hashlib, importlib.util, json, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
PLAN = R13 / 'config/prereg_addendum15.json'
_sp = importlib.util.spec_from_file_location('gnb_v3b', H / '13_stage13/stage13_b2_gennames_b_v3b.py'); V3B = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V3B)
B = V3B.V3.B; V1, V2 = B.V1, B.V2
LAYERS = [16, 24, 32, 40, 48, 52, 56]; POS = [('name_mean', 'primary (ii)'), ('pred_first', 'secondary (i)'), ('last', 'descriptive')]
N_SHARDS = 48


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def wauc(paper, y, s):
    st = V2.pair_stats(paper, y, s); n = sum(v[1] for v in st.values()); return (sum(v[0] for v in st.values()) / n) if n else np.nan


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--out'); ap.add_argument('--nb', type=int, default=2000)
    ap.add_argument('--layers'); ap.add_argument('--allow-partial', action='store_true'); a = ap.parse_args()
    sha = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    if sha != (PLAN.parent / 'prereg_addendum15.json.sha256').read_text().split()[0]: raise SystemExit('PLAN CHANGED (addendum 15)')
    root = Path(a.root); layers = [int(x) for x in a.layers.split(',')] if a.layers else LAYERS
    shards = [k for k in range(N_SHARDS) if (root / f'raw/shard_{k:03d}.npz').exists()]
    if len(shards) < N_SHARDS and not a.allow_partial: raise SystemExit(f'only {len(shards)}/{N_SHARDS} shards present')
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present')
    NA = pd.concat([pd.read_parquet(root / f'names/shard_{k:03d}.parquet') for k in shards], ignore_index=True)
    PA = pd.concat([pd.read_csv(root / f'papers/shard_{k:03d}.csv') for k in shards], ignore_index=True)
    h2 = []
    for k in shards:
        f = root / f'h2/shard_{k:03d}.csv'
        try: h2.append(pd.read_csv(f))
        except Exception: pass
    h2 = pd.concat(h2, ignore_index=True) if h2 else pd.DataFrame(columns=['final_argmax', 'next_tok'])
    zs = [np.load(root / f'raw/shard_{k:03d}.npz', allow_pickle=True) for k in shards]
    key = np.concatenate([z['key'].astype(str) for z in zs]); kidx = {k_: i for i, k_ in enumerate(key)}
    N = NA[NA.status.isin(['M', 'H'])].copy(); N['key'] = N.paper_id + '|' + N.item_index.astype(str)
    if not N.key.isin(kidx).all(): raise SystemExit(f'{(~N.key.isin(kidx)).sum()} M/H names without vectors')
    N = N.reset_index(drop=True); ix = np.array([kidx[k_] for k_ in N.key])
    N['item_rel'] = N.item_index / N.paper_id.map(NA.groupby('paper_id').item_index.max()).clip(lower=1)   # relative position in the generated list
    y = (N.status == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    tgt = (N.group_tight == 'target').to_numpy(); ctl = (N.group_tight == 'control').to_numpy()
    q = N[tgt].groupby('paper_id').status.agg(lambda s: (s == 'M').any() and (s == 'H').any()); qual = set(q[q].index)
    n_qual = len(qual); m_qual = int(((N.status == 'M') & N.paper_id.isin(qual)).sum()); descriptive_only = n_qual < 100 or m_qual < 200
    pin_ex = N.in_pool_exact.astype('boolean').fillna(False).to_numpy(bool); pin_ru = N.in_pool_rule.astype('boolean').fillna(False).to_numpy(bool)
    XP = N[['item_index', 'item_rel']].to_numpy(float); XS = np.stack([N.name_len_chars.to_numpy(float), np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1)
    pp_, _, _ = V1.fit_oof(XP, y, fold); ps_, _, _ = V1.fit_oof(XS, y, fold)
    rows = []
    for l in layers:
        for pos, role in POS:
            X = np.concatenate([z[f'{pos}@{l}'] for z in zs])[ix].astype(np.float32)
            pr, C, _ = V1.fit_oof(X, y, fold); psh, _, ysh = V1.fit_oof(X, y, fold, seed_shuffle=1212)
            st = [V2.pair_stats(paper[tgt], y[tgt], sc[tgt]) for sc in (pr, pp_, ps_)]
            common = set(st[0]) & set(st[1]) & set(st[2]); st = [{p: s[p] for p in common} for s in st]
            row = dict(layer=l, position=pos, role=role, C=C, n_M_target=int(y[tgt].sum()), n_H_target=int((1 - y[tgt]).sum()),
                       shuffled_within=wauc(paper[tgt], ysh[tgt], psh[tgt]),
                       control_within=wauc(paper[ctl], y[ctl], pr[ctl]),
                       M_vs_H_in_pool_exact=wauc(paper[tgt & ((y == 1) | pin_ex)], y[tgt & ((y == 1) | pin_ex)], pr[tgt & ((y == 1) | pin_ex)]),
                       M_vs_H_not_in_pool_exact=wauc(paper[tgt & ((y == 1) | ~pin_ex)], y[tgt & ((y == 1) | ~pin_ex)], pr[tgt & ((y == 1) | ~pin_ex)]),
                       M_vs_H_in_pool_rule=wauc(paper[tgt & ((y == 1) | pin_ru)], y[tgt & ((y == 1) | pin_ru)], pr[tgt & ((y == 1) | pin_ru)]),
                       M_vs_H_not_in_pool_rule=wauc(paper[tgt & ((y == 1) | ~pin_ru)], y[tgt & ((y == 1) | ~pin_ru)], pr[tgt & ((y == 1) | ~pin_ru)]))
            if common:
                est, bt, npap, npair = V2.within_auroc(st, PT, nb=a.nb); ci = lambda v: np.percentile(v, [2.5, 97.5])
                (lo, hi), (a1, b1), (a2, b2) = ci(bt[:, 0]), ci(bt[:, 0] - bt[:, 1]), ci(bt[:, 0] - bt[:, 2])
                (plo, phi), (slo, shi) = ci(bt[:, 1]), ci(bt[:, 2])
                row.update(auroc_within=est[0], lo=lo, hi=hi, position_baseline=est[1], pos_lo=plo, pos_hi=phi, string_baseline=est[2], str_lo=slo, str_hi=shi,
                           diff_pos=est[0] - est[1], diff_pos_lo=a1, diff_pos_hi=b1, diff_str=est[0] - est[2], diff_str_lo=a2, diff_str_hi=b2,
                           n_papers=npap, n_pairs=npair, signal=bool(a1 > 0 and a2 > 0 and not descriptive_only))
            else: row.update(auroc_within=np.nan, n_papers=0, n_pairs=0, signal=False)
            rows.append(row); log(f'L{l} {pos}: within {row["auroc_within"]:.3f}')
    T = pd.DataFrame(rows); (root / 'summary').mkdir(exist_ok=True); T.to_csv(root / 'summary/probe_within.csv', index=False)
    # ---- report
    vc = NA.groupby('group_tight').status.value_counts().unstack(fill_value=0)
    f3 = lambda e, lo, hi: '-' if pd.isna(e) else f'{e:.3f} [{lo:.3f}, {hi:.3f}]'
    fd = lambda e, lo, hi: '-' if pd.isna(e) else f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    h2a = float((h2.final_argmax == h2.next_tok).mean()) if len(h2) else float('nan')
    h1 = json.loads((root / 'summary/h1.json').read_text()) if (root / 'summary/h1.json').exists() else 'missing'
    h3 = json.loads((root / 'summary/h3.json').read_text()) if (root / 'summary/h3.json').exists() else {}
    L = ['# Addendum 15 item 2-11b: model-generated names (generated in this run), true (M) vs fabricated (H)', '',
         f'Plan `config/prereg_addendum15.json` (sha256 {sha[:16]}...). Scripts `13_stage13/stage13_b2_gennames_b_gpu.py` (+ `_gpu_multi.py`), '
         f'`stage13_b2_gennames_b_analyze.py`. Written {time.strftime("%Y-%m-%dT%H:%M:%S")}. Shards {len(shards)}/{N_SHARDS}.', '',
         '**Limitation (stated in advance):** chat-template context, not the raw prompt of the other experiments; labels from rule matching (matcher v3b, '
         'known limitations in the plan), not by hand.', '',
         '## Checks', '',
         f'- H2 self-consistency (residuals saved during generation; HARD >= 0.99): {h2a:.4f} over {len(h2)} positions',
         f'- H1 determinism (WARN only): {h1}', f'- H3 matcher reproduction: {h3.get("H3_counts_equal")}/{h3.get("papers")} ({h3.get("status")})', '',
         '## Labels (P and U excluded from M-vs-H)', '', '| group | ' + ' | '.join(vc.columns) + ' |', '|---|' + '---|' * len(vc.columns)]
    L += [f'| {g} | ' + ' | '.join(str(int(v)) for v in r) + ' |' for g, r in vc.iterrows()]
    L += ['', f'- papers generated: {len(PA)}; EOS share {PA.eos.mean():.3f}; mean generated tokens {PA.n_gen.mean():.1f}',
          f'- qualifying target papers (>= 1 M and >= 1 H): **{n_qual}**; M names in them: **{m_qual}** (thresholds 100 / 200: '
          f'{"NOT met -> descriptive only" if descriptive_only else "met"})',
          f'- H names in the cohort author pool: exact {int(pin_ex[y == 0].sum())} / rule {int(pin_ru[y == 0].sum())} of {int((y == 0).sum())}', '',
          '## Within-paper AUROC on target papers (team-cluster 95% CI, 2,000 draws); signal = CI(probe - position) > 0 and CI(probe - string) > 0', '']
    for pos, role in POS:
        L += [f'### {pos} - {role}', '', '| layer | probe | position baseline | string baseline | probe - position | probe - string | signal | papers / pairs | shuffled | control (descr.) |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for r in T[T.position == pos].itertuples():
            L.append(f'| L{r.layer} | {f3(r.auroc_within, getattr(r, "lo", np.nan), getattr(r, "hi", np.nan))} | {f3(getattr(r, "position_baseline", np.nan), getattr(r, "pos_lo", np.nan), getattr(r, "pos_hi", np.nan))} | '
                     f'{f3(getattr(r, "string_baseline", np.nan), getattr(r, "str_lo", np.nan), getattr(r, "str_hi", np.nan))} | {fd(getattr(r, "diff_pos", np.nan), getattr(r, "diff_pos_lo", np.nan), getattr(r, "diff_pos_hi", np.nan))} | '
                     f'{fd(getattr(r, "diff_str", np.nan), getattr(r, "diff_str_lo", np.nan), getattr(r, "diff_str_hi", np.nan))} | {"yes" if r.signal else "no"} | {int(r.n_papers)} / {int(r.n_pairs)} | {r.shuffled_within:.3f} | {r.control_within:.3f} |')
        L += ['']
    L += ['## Descriptive: M vs H split by author-pool membership (within-paper AUROC, target, point estimates)', '',
          '| layer | position | M vs H in pool (exact) | M vs H not in pool (exact) | in pool (rule) | not in pool (rule) |', '|---|---|---|---|---|---|']
    for r in T.itertuples():
        L.append(f'| L{r.layer} | {r.position} | {r.M_vs_H_in_pool_exact:.3f} | {r.M_vs_H_not_in_pool_exact:.3f} | {r.M_vs_H_in_pool_rule:.3f} | {r.M_vs_H_not_in_pool_rule:.3f} |')
    L += ['', 'Primary = name_mean (ii); secondary = pred_first (i); last = descriptive. Conclusions from (ii) only.', '', '## Conclusion', '',
          '<!--CONCLUSION: written by the main session after review-->', '']
    out = Path(a.out) if a.out else R13 / 'reports/b2_gennames_b_report.md'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text('\n'.join(L) + '\n'); log('wrote', out)


if __name__ == '__main__':
    main()
