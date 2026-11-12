"""2-11b per-shard consistency check, run BEFORE the (unchanged) analysis stage13_b2_gennames_b_analyze.py.
Per shard k the four files raw/shard_k.npz, names/, papers/, h2/ must come from ONE run:
  shards written by the hash runner (npz has 'run_id'): run_id identical in npz, names, papers and h2; per paper gen_sha in papers
    == sha256(gen_ids) recomputed, names gen_sha == papers gen_sha, npz gen_sha (per M/H key) == that paper's gen_sha;
  legacy shards (no run id; 0, 1, 7-12, 37 and any written by stage13_b2_gennames_b_gpu.py): content check only - npz keys ==
    M/H rows of names in order, names papers within papers csv, npz meta paper count == papers csv rows, h2 papers within names'
    M/H papers; and the shard's 'shard KKK {' completion line must appear in exactly one GPU job log (one writer).
Any mismatch -> exit 1 with the shard and paper ids; result in summary/verify.json. Usage: --root DIR [--logs DIR] [--allow-partial]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path
import numpy as np


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--logs', default='/scratch/zhang.zhiqi2/jlens/381_stage13/logs')
    ap.add_argument('--allow-partial', action='store_true'); a = ap.parse_args(); root = Path(a.root)
    shards = [k for k in range(48) if (root / f'raw/shard_{k:03d}.npz').exists()]
    logs = sorted(Path(a.logs).glob('b2_gennames_b_gpu_[0-9]*.log')) + sorted(Path(a.logs).glob('b2_gennames_b_grp_*.log'))
    logtxt = {p.name: p.read_text(errors='ignore') for p in logs}
    res, bad = {}, []
    for k in shards:
        f = dict(npz=root / f'raw/shard_{k:03d}.npz', names=root / f'names/shard_{k:03d}.parquet', papers=root / f'papers/shard_{k:03d}.csv', h2=root / f'h2/shard_{k:03d}.csv')
        miss = [n for n, p in f.items() if not p.exists()]
        if miss: bad.append(f'shard {k}: missing {miss}'); res[k] = 'MISSING'; continue
        z = np.load(f['npz'], allow_pickle=True); keys = z['key'].astype(str); meta = json.loads(str(z['meta']))
        N = pd.read_parquet(f['names']); PP = pd.read_csv(f['papers'])
        try: H2 = pd.read_csv(f['h2'])
        except Exception: H2 = pd.DataFrame(columns=['paper_id'])
        K = N[N.status.isin(['M', 'H'])]; kn = list(K.paper_id + '|' + K.item_index.astype(str)); errs = []
        if list(keys) != kn: errs.append(f'npz keys != names M/H rows ({len(keys)} vs {len(kn)}); papers ' + str(sorted({x.split("|")[0] for x in set(keys) ^ set(kn)})[:20]))
        if not set(N.paper_id) <= set(PP.paper_id): errs.append(f'names papers not in papers csv: {sorted(set(N.paper_id) - set(PP.paper_id))[:20]}')
        if meta.get('papers') != len(PP): errs.append(f'npz meta papers {meta.get("papers")} != papers csv rows {len(PP)}')
        if len(H2) and not set(H2.paper_id) <= set(K.paper_id): errs.append(f'h2 papers without M/H names: {sorted(set(H2.paper_id) - set(K.paper_id))[:20]}')
        if 'run_id' in z.files:
            rid = str(z['run_id']); kind = 'hash'
            for nm, df in (('names', N), ('papers', PP), ('h2', H2)):
                if len(df) and ('run_id' not in df.columns or set(df.run_id.astype(str)) != {rid}):
                    errs.append(f'{nm} run_id {sorted(set(df.run_id.astype(str)))[:3] if "run_id" in df.columns else "absent"} != npz {rid}')
            ps = dict(zip(PP.paper_id, PP.gen_sha))
            re_ = [p for p, g, s in zip(PP.paper_id, PP.gen_ids, PP.gen_sha) if hashlib.sha256(str(g).encode()).hexdigest() != s]
            if re_: errs.append(f'papers gen_sha != sha256(gen_ids): {re_[:20]}')
            nb = sorted({p for p, s in zip(N.paper_id, N.gen_sha) if ps.get(p) != s})
            if nb: errs.append(f'names gen_sha != papers gen_sha: {nb[:20]}')
            zb = sorted({kk.split('|')[0] for kk, s in zip(keys, z['gen_sha'].astype(str)) if ps.get(kk.split('|')[0]) != s})
            if zb: errs.append(f'npz gen_sha != papers gen_sha: {zb[:20]}')
        else:
            kind = 'legacy (no run id; content check + single writer)'
            writers = [n for n, t in logtxt.items() if re.search(rf'shard {k:03d} \{{', t)]
            if len(writers) != 1: errs.append(f'completion line found in {len(writers)} job logs: {writers}')
        res[k] = dict(kind=kind, job=meta.get('job'), ok=not errs, errors=errs)
        bad += [f'shard {k}: {e}' for e in errs]
    out = dict(shards=len(shards), ok=not bad and (len(shards) == 48 or a.allow_partial), problems=bad, per_shard=res)
    (root / 'summary').mkdir(exist_ok=True); (root / 'summary/verify.json').write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(dict(shards=len(shards), ok=out['ok'], problems=bad, kinds={k: (v['kind'] if isinstance(v, dict) else v) for k, v in res.items()}), indent=1, default=str), flush=True)
    if len(shards) < 48 and not a.allow_partial: print(f'only {len(shards)}/48 shards', flush=True); sys.exit(1)
    sys.exit(0 if not bad else 1)


if __name__ == '__main__':
    main()
