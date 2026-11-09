"""2-11b shard 0 CPU addendum (runs after the shard-0 GPU job, afterany). Writes <root>/shard0_cost_extra.md and appends a link line
to <root>/shard0_cost.md (creates a stub if the GPU job died before writing it). Never submits anything.
 a. self-consistency method used by the runner + H2 agreement (from h2/shard_000.csv)
 b. label counts M / H / P / U_* ; target papers with >= 1 M and >= 1 H; projection to all 48 shards vs addendum-15 minimum size
    (qualifying target papers >= 100, M names in them >= 200)
 c. read-back of the saved npz: 5 papers, shapes / counts vs names table, positions x layers
Usage: --root DIR [--shard 0]
"""
import argparse, json, time
from pathlib import Path
import numpy as np

POS = ['name_mean', 'pred_first', 'last']; LAYERS = [16, 24, 32, 40, 48, 52, 56]
N_TARGET_ALL, N_ALL = 4621, 6841          # target / target+control papers of the cohort (group_tight)


def wilson(x, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = x / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n); return c - h, c + h


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--shard', type=int, default=0); ap.add_argument('--layers'); a = ap.parse_args()
    root = Path(a.root); k = a.shard; layers = [int(x) for x in a.layers.split(',')] if a.layers else LAYERS
    f = dict(npz=root / f'raw/shard_{k:03d}.npz', names=root / f'names/shard_{k:03d}.parquet', papers=root / f'papers/shard_{k:03d}.csv', h2=root / f'h2/shard_{k:03d}.csv')
    L = [f'# 2-11b shard {k} - CPU addendum (a-c)', '', f'Written {time.strftime("%Y-%m-%dT%H:%M:%S")} from {root}. Files present: ' +
         ', '.join(f'{n}={"yes" if p.exists() else "NO"}' for n, p in f.items()), '']
    # ---- a
    L += ['## a. Self-consistency method and agreement', '',
          '- Method: **residuals saved during generation** (HF generate with output_hidden_states=True and output_logits=True; no second '
          'forward pass). Check H2: at every analysed position (pred_first and every name token of M/H names) the logits recomputed from the '
          'stored final-layer state (lm_head, [1,1,d] as in the decode step) must have argmax == the generated next token; < 0.99 = HARD stop.']
    if f['h2'].exists() and f['h2'].stat().st_size > 1:
        try: h = pd.read_csv(f['h2'])
        except Exception: h = pd.DataFrame()
        if len(h):
            a1 = (h.final_argmax == h.next_tok).mean(); a2 = (h.step_logit_argmax == h.next_tok).mean(); a3 = (h.final_argmax == h.step_logit_argmax).mean()
            L += [f'- H2 agreement (recomputed from stored final state == generated token): **{a1:.4f}** over {len(h)} positions in {h.paper_id.nunique()} papers '
                  f'({"PASS" if a1 >= 0.99 else "FAIL"}, threshold 0.99)',
                  f'- for reference: step logits argmax == generated token {a2:.4f}; recomputed == step logits {a3:.4f}']
        else: L += ['- H2: no analysed positions in this shard (WARN)']
    elif f['h2'].exists(): L += ['- H2: h2 file empty: no analysed positions in this shard (WARN)']
    else: L += ['- H2: h2 file missing (GPU job did not finish the shard)']
    if (root / 'HARD_CHECK_FAILED').exists(): L += [f'- HARD_CHECK_FAILED present: {(root / "HARD_CHECK_FAILED").read_text()[:300]}']
    L += ['']
    # ---- b
    L += ['## b. Labels in this shard and projection to all 48 shards', '']
    N = pd.read_parquet(f['names']) if f['names'].exists() else None
    if N is not None and len(N):
        vc = N.status.value_counts().to_dict(); u = {s: c for s, c in vc.items() if s.startswith('U')}
        L += [f'- names: M {vc.get("M", 0)}, H {vc.get("H", 0)}, P {vc.get("P", 0)}, duplicate (U_dup) {vc.get("U_dup", 0)}; other U {dict((s, c) for s, c in u.items() if s != "U_dup")}',
              f'- by group: {N.groupby("group_tight").status.value_counts().unstack(fill_value=0).to_dict("index")}']
        PP = pd.read_csv(f['papers']) if f['papers'].exists() else None
        n_t = int((PP.group_tight == 'target').sum()) if PP is not None else int(N[N.group_tight == 'target'].paper_id.nunique())
        T = N[N.group_tight == 'target']; g = T.groupby('paper_id').status.agg(lambda s: (s == 'M').any() and (s == 'H').any())
        qual = g[g].index; x = len(qual); m_q = int(((T.status == 'M') & T.paper_id.isin(qual)).sum()); m_all = int((T.status == 'M').sum())
        lo, hi = wilson(x, n_t); proj = x / max(1, n_t) * N_TARGET_ALL
        # M names in qualifying papers: ratio estimator with a paper bootstrap inside the shard
        per = T.groupby('paper_id').apply(lambda s: int((s.status == 'M').sum()) if (s.status == 'M').any() and (s.status == 'H').any() else 0)
        per = per.reindex(PP[PP.group_tight == 'target'].paper_id, fill_value=0).to_numpy() if PP is not None else per.to_numpy()
        bt = np.random.default_rng(48).choice(per, (2000, len(per))).mean(1) * N_TARGET_ALL if len(per) else np.array([np.nan])
        pm = per.mean() * N_TARGET_ALL if len(per) else np.nan
        L += [f'- target papers in shard: {n_t}; with >= 1 M and >= 1 H: **{x}**; M names in those papers: **{m_q}** (all target M: {m_all})',
              f'- projection method: shard k holds papers with cohort index % 48 == k, a systematic 1/48 sample, so counts scale by '
              f'(all target papers {N_TARGET_ALL}) / (target papers in shard {n_t}); 95% interval for papers = Wilson interval of the shard share x 4,621; '
              f'for M names = paper bootstrap (2,000) of the per-paper count x 4,621. Assumes the labels of other shards behave like this one (same generation settings).',
              f'- projected qualifying target papers: **{proj:.0f}** [{lo * N_TARGET_ALL:.0f}, {hi * N_TARGET_ALL:.0f}] vs threshold 100 -> '
              f'{"reached" if lo * N_TARGET_ALL >= 100 else ("likely" if proj >= 100 else "NOT reached")}',
              f'- projected M names in qualifying target papers: **{pm:.0f}** [{np.nanpercentile(bt, 2.5):.0f}, {np.nanpercentile(bt, 97.5):.0f}] vs threshold 200 -> '
              f'{"reached" if np.nanpercentile(bt, 2.5) >= 200 else ("likely" if pm >= 200 else "NOT reached")}', '']
    else:
        L += ['- names file missing or empty: no label counts', '']
    # ---- c
    L += ['## c. Read-back of the saved name vectors', '']
    if f['npz'].exists() and N is not None:
        z = np.load(f['npz'], allow_pickle=True)          # runner stores 'key' as an object array (pickled); own file, safe to unpickle
        kraw = z['key']; keys = kraw.astype(str)
        if kraw.dtype == object: L.append('- note: npz "key" is stored as an object (pickled) array: readable only with allow_pickle=True; the probe step must load it that way (or a later runner stores str keys)')
        need = [f'{p}@{l}' for p in POS for l in layers]; miss = [n for n in need if n not in z.files]
        K = N[N.status.isin(['M', 'H'])]; kn = (K.paper_id + '|' + K.item_index.astype(str)).to_numpy()
        bad = []
        if miss: bad.append(f'missing arrays {miss}')
        shapes = {n: z[n].shape for n in need if n in z.files}
        if any(s[0] != len(keys) for s in shapes.values()): bad.append(f'row counts differ from keys ({len(keys)}): {shapes}')
        if len(set(s[1:] for s in shapes.values())) > 1: bad.append(f'vector widths differ: {set(s[1:] for s in shapes.values())}')
        if list(keys) != list(kn): bad.append(f'npz keys != M/H rows of the names table in order ({len(keys)} vs {len(kn)})')
        papers = list(dict.fromkeys(k_.split('|')[0] for k_ in keys)); smp = [papers[i] for i in np.random.default_rng(5).choice(len(papers), min(5, len(papers)), replace=False)] if papers else []
        L += [f'- arrays: {len(shapes)}/{len(need)} (3 positions x {len(layers)} layers); rows per array {len(keys)} (= M + H names {len(kn)}); vector width {next(iter(shapes.values()))[1:] if shapes else "-"}; dtype {z[need[0]].dtype if shapes else "-"}',
              '', '| paper | M+H names (table) | npz rows | arrays with that many rows | NaN/inf | max abs |', '|---|---|---|---|---|---|']
        for p in smp:
            ix = np.where(np.char.startswith(keys, p + '|'))[0]; nt = int((K.paper_id == p).sum())
            ok_arr = sum(z[n][ix].shape[0] == nt for n in shapes); fin = all(np.isfinite(z[n][ix].astype(np.float32)).all() for n in shapes)
            mx = max(float(np.abs(z[n][ix].astype(np.float32)).max()) for n in shapes) if len(ix) else float('nan')
            if len(ix) != nt or ok_arr != len(shapes) or not fin: bad.append(f'paper {p}: table {nt}, npz {len(ix)}, arrays ok {ok_arr}, finite {fin}')
            L.append(f'| {p[:12]} | {nt} | {len(ix)} | {ok_arr}/{len(shapes)} | {"none" if fin else "PRESENT"} | {mx:.2f} |')
        L += ['', f'- result: **{"no mismatch" if not bad else "MISMATCH"}**'] + [f'  - {b}' for b in bad]
        if not smp: L += ['- (no M/H names in this shard: only the empty-array layout was checked)']
    else: L += ['- npz or names file missing: read-back not possible']
    out = root / 'shard0_cost_extra.md'; out.write_text('\n'.join(L) + '\n')
    cm = root / 'shard0_cost.md'
    if not cm.exists(): cm.write_text(f'# 2-11b shard 0 cost report\n\nGPU job did not write this report (see the job log).\n')
    if 'shard0_cost_extra.md' not in cm.read_text():
        with open(cm, 'a') as fh: fh.write(f'\n## Addendum (CPU, {time.strftime("%Y-%m-%dT%H:%M:%S")})\n\nSections a-c (self-consistency method, label counts + projection, vector read-back): see [shard0_cost_extra.md](shard0_cost_extra.md).\n')
    print('\n'.join(L), flush=True)


if __name__ == '__main__':
    main()
