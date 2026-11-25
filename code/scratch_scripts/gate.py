#!/usr/bin/env python3
"""CPU gate for addenda 30-32 (written rule, 2026-11-22). Each run:
  for each item: trial = shard 0. If the trial is not done and not queued -> submit it (if a GPU QOS slot is free).
  When the trial is done -> projected GPU-h = (trial seconds / trial papers) x all papers / 3600 x 1.15 (load overhead) ;
  if projected > the item cap -> item STOPPED (reported). Else submit missing shards (3 per job) while the user has < 8 GPU jobs.
  When every shard of the item's freeze/sample has its done marker -> run the item's analysis once.
  Requeue itself (--begin now+15 min) until all items are analysed or stopped; at most 80 rounds; never scancel.
State: 391_groups/logs/a3x/gate_state.json.
"""
import json, os, subprocess, sys, time
from pathlib import Path

W = Path.home() / 'jlens_work/24_gpubatch'; G = Path('/scratch/zhang.zhiqi2/jlens/391_groups'); ST = G / 'logs/a3x/gate_state.json'
PY = '/home/zhang.zhiqi2/conda-envs/jlens/bin/python'
ITEMS = {'a30': dict(script='a30_h5.py', meta=G / 'raw/a30/meta', cap=1.2, per_job=6),
         'a31': dict(script='a31_dla.py', meta=G / 'raw/a31/meta', cap=0.6, per_job=3),
         'a32': dict(script='a32_sweep.py', meta=G / 'raw/a32/main', cap=3.2, per_job=3)}
# 2026-11-22 late: a32 cap 2.0 -> 3.2 GPU-h (coordinator: the 3-h batch cap was ours; total stays within the user's <= 5 GPU-h standing rule)
# 2026-11-22 20:xx: a30 cap 1.0 -> 1.2 with 6 shards per job (model load ~240 s per job dominated the 3-shard projection); total budget 3 GPU-h kept
MAX_ROUNDS = 80


def run(cmd):
    for _ in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if r.returncode == 0: return r.stdout
        except subprocess.TimeoutExpired: pass
        time.sleep(5)
    return None


def queued_ids():
    out = run(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%i|%P']) or ''
    rows = [l.split('|') for l in out.strip().splitlines() if l.strip()]
    return {r[0] for r in rows}, sum(1 for r in rows if r[1].startswith('gpu'))


def shards_all(item):
    import pandas as pd
    if item == 'a30': return sorted(pd.read_parquet(G / 'raw/a30_freeze/freeze.parquet').shard.unique().tolist())
    if item == 'a31': return sorted(pd.read_parquet('/scratch/zhang.zhiqi2/jlens/361_stage11/config/sample.parquet').shard.unique().tolist())
    return list(range(24))


def done(item, k):
    m = ITEMS[item]['meta']
    return (m / f'shard_{k:03d}.json').exists() if item != 'a32' else (m / f'shard_{k:03d}.npz').exists()


def trial_seconds(item):
    if item == 'a32':
        z = __import__('numpy').load(G / 'raw/a32/main/shard_000.npz'); mt = json.loads(str(z['meta'])); return float(mt.get('seconds', mt.get('elapsed', 0)) or 0), None
    mt = json.load(open(ITEMS[item]['meta'] / 'shard_000.json')); return float(mt['seconds']), mt


def submit(item, shards):
    env = dict(os.environ, SCRIPT=ITEMS[item]['script'], SHARDS=','.join(map(str, shards)))
    out = subprocess.run(['sbatch', '--parsable', '--export=ALL', '-J', f'{item}_gpu', str(W / 'gpu.sbatch')], capture_output=True, text=True, env=env)
    if out.returncode != 0: print('SBATCH FAILED', item, shards, out.stderr.strip(), flush=True); return None
    return out.stdout.strip().split(';')[0]


def main():
    S = json.load(open(ST)) if ST.exists() else {'round': 0, 'items': {k: {'jobs': {}, 'state': 'trial'} for k in ITEMS}}
    S['round'] += 1; print(time.strftime('%Y-%m-%dT%H:%M:%S'), 'gate round', S['round'], flush=True)
    q, ngpu = queued_ids()
    for item, it in S['items'].items():
        if it['state'] in ('analysed', 'stopped'): continue
        allk = shards_all(item); miss = [k for k in allk if not done(item, k)]
        inflight = {k for jid, ks in it['jobs'].items() if jid in q for k in ks}
        if not done(item, 0):
            if 0 not in inflight and ngpu < 8:
                j = submit(item, [0]);
                if j: it['jobs'][j] = [0]; ngpu += 1; print(item, 'trial submitted', j, flush=True)
            continue
        if 'projected_gpu_h' not in it:
            sec, _ = trial_seconds(item); per_shard = sec; n = len(allk)
            kj = ITEMS[item]['per_job']; it['projected_gpu_h'] = round((per_shard * n + -(-n // kj) * 240) / 3600, 3); it['trial_seconds'] = sec
            print(item, 'trial seconds', sec, 'projected GPU-h', it['projected_gpu_h'], 'cap', ITEMS[item]['cap'], flush=True)
            if it['projected_gpu_h'] > ITEMS[item]['cap']: it['state'] = 'stopped'; print(item, 'STOPPED: projection above cap', flush=True); continue
        if miss:
            todo = [k for k in miss if k not in inflight]
            kj = ITEMS[item]['per_job']
            for i in range(0, len(todo), kj):
                if ngpu >= 8: break
                ks = todo[i:i + kj]; j = submit(item, ks)
                if j: it['jobs'][j] = ks; ngpu += 1; print(item, 'submitted', ks, '->', j, flush=True)
            continue
        r = subprocess.run([PY, ITEMS[item]['script'], 'analyze'], cwd=W, capture_output=True, text=True,
                           env=dict(os.environ, HF_HOME='/scratch/zhang.zhiqi2/hf', HF_HUB_OFFLINE='1'))
        print(item, 'ANALYZE rc', r.returncode, r.stdout[-3000:], r.stderr[-3000:], flush=True)
        it['state'] = 'analysed' if r.returncode == 0 else 'analyze_failed'
    json.dump(S, open(ST, 'w'), indent=1)
    pending = [k for k, it in S['items'].items() if it['state'] not in ('analysed', 'stopped', 'analyze_failed')]
    if pending and S['round'] < MAX_ROUNDS:
        out = subprocess.run(['sbatch', '--parsable', '--begin=now+15minutes', str(W / 'gate.sbatch')], capture_output=True, text=True)
        print('gate requeued', out.stdout.strip(), out.stderr.strip(), flush=True)
    else:
        print('gate done', {k: v['state'] for k, v in S['items'].items()}, flush=True)


if __name__ == '__main__':
    main()
