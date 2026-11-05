"""Addendum 9 (2026-11-05): lm_head rows for ALL name token ids + final-norm weight, read on CPU from the safetensors shard.

Same format and conversion as Stage 11 do_probe_vocab (bf16 weight -> float32 -> fp16 rows; norm weight float32; eps from config).
Check: the rows of the 4,314 Stage 11 probe_vocab ids and the norm weight must equal raw/probe_vocab/shard_000.npz exactly (WARN only).
Output: 381_stage13/summary_alltok/vocab_rows.npz (skip if exists)
"""
import glob, json, hashlib, os
from pathlib import Path
import numpy as np, pandas as pd

B = Path('/scratch/zhang.zhiqi2/jlens'); OUT = B / '381_stage13/summary_alltok'; OUT.mkdir(parents=True, exist_ok=True)
f_out = OUT / 'vocab_rows.npz'
if f_out.exists(): print('exists', f_out); raise SystemExit(0)
import torch
from safetensors import safe_open
snap = sorted(glob.glob(os.path.join(os.environ['HF_HOME'], 'hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137/')))[0]
wm = json.load(open(snap + 'model.safetensors.index.json'))['weight_map']; cfg = json.load(open(snap + 'config.json'))
ids = np.array(sorted(pd.read_parquet(B / '351_stage10/cohort/name_tokens.parquet', columns=['token_id']).token_id.unique()), np.int64)
with safe_open(snap + wm['lm_head.weight'], framework='pt') as f:
    W = f.get_tensor('lm_head.weight')
    print('lm_head', W.shape, W.dtype)
    rows = W[torch.from_numpy(ids)].float().numpy().astype(np.float16); del W
with safe_open(snap + wm['model.norm.weight'], framework='pt') as f:
    nw = f.get_tensor('model.norm.weight').float().numpy()
eps = float(cfg['rms_norm_eps'])
pv = np.load(B / '361_stage11/raw/probe_vocab/shard_000.npz'); pos = {int(t): i for i, t in enumerate(ids)}
sel = np.array([pos[int(t)] for t in pv['token_id']])
chk = dict(n_ids=int(len(ids)), n_probe_vocab=int(len(pv['token_id'])), probe_vocab_subset=bool(all(int(t) in pos for t in pv['token_id'])),
           rows_equal_probe_vocab=bool(np.array_equal(rows[sel], pv['lm_head_rows'])), max_abs_row_diff=float(np.abs(rows[sel].astype(np.float32) - pv['lm_head_rows'].astype(np.float32)).max()),
           norm_equal=bool(np.array_equal(nw, pv['norm_weight'])), eps=eps, eps_probe_vocab=float(pv['eps']))
chk['status'] = 'OK' if chk['rows_equal_probe_vocab'] and chk['norm_equal'] and chk['eps'] == chk['eps_probe_vocab'] else 'WARN'
meta = dict(source=snap, lm_head_file=wm['lm_head.weight'], conversion='bf16 -> float32 -> fp16 (as Stage 11 do_probe_vocab)', checks=chk)
np.savez(f_out, token_id=ids, lm_head_rows=rows, norm_weight=nw, eps=np.array(eps), meta=np.array(json.dumps(meta)))
(OUT / 'vocab_rows_check.json').write_text(json.dumps(chk, indent=1)); print(json.dumps(chk, indent=1))
