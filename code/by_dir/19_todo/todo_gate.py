#!/usr/bin/env python3
"""CPU gate for TODO items #9 (e1x6 U0), #3 (a27), #6 (a28), #11 (a29). Written rule:
- reads the FULL shard/unit list from each item's freeze (never a hard-coded range);
- if nothing is missing -> runs that item's analysis once and exits;
- else submits GPU jobs for the missing shards (only while the user has < 8 GPU jobs queued/running; at most 3 per round),
  then requeues itself (afterany on the jobs it submitted; or after 20 min if it could not submit) — at most MAX_ROUNDS rounds,
  then stops and prints STOP (mail via sbatch FAIL/END).
Usage: ITEM=a27 sbatch todo_gate.sbatch   (state in 391_groups/logs/todo_gate_<item>.round)
"""
import json, os, subprocess, sys
from pathlib import Path
import pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'; R13 = J / '381_stage13'
T = H / '19_todo'; MAX_ROUNDS = 40; PER_JOB = 3; ME = os.environ.get('SLURM_JOB_ID', 'local')
CAP_H = {'e1u0': 0.5, 'a27': 1.8, 'a28': 0.8, 'a29': 1.9}   # shares of the user's 5 GPU-h budget for #9/#3/#6/#11
LOAD_S = 240


def elapsed_s(jid):
    rc, out = sh(f'sacct -j {jid} -X -n -P --format=ElapsedRaw')
    try: return int(out.split()[0])
    except Exception: return None



def sh(cmd, env=None):
    e = dict(os.environ, **(env or {})); r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=e, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def gpu_jobs():
    for _ in range(3):
        rc, out = sh("squeue -u zhang.zhiqi2 -h -o '%P %j'")
        if rc == 0: return sum(1 for l in out.splitlines() if l.split()[0].startswith('gpu'))
    return 99


def missing(item):
    if item == 'e1u0':
        shards = sorted(int(x) for x in pd.read_parquet(G / 'config/rerun_U0_600.parquet').shard.unique())
        return [k for k in shards if not (R13 / f'raw/e1x6_extra_20261114/U0/false_0/shard_{k:03d}.npz').exists()]
    if item == 'a27':
        shards = sorted(int(x) for x in pd.read_parquet(G / 'raw/a21_freeze/freeze.parquet').shard.unique())
        return [k for k in shards if not (G / f'raw/a27/meta/shard_{k:03d}.json').exists()]
    if item == 'a28':
        shards = json.loads((G / 'raw/a28_freeze/freeze.json').read_text())['shards']
        return [k for k in shards if not (G / f'raw/a28/meta_{k:03d}.json').exists()]
    if item == 'a29':
        sys.argv = ['x']; import importlib.util
        sp = importlib.util.spec_from_file_location('a29w', T / 'a29_layerfill.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        mm, _ = m.g.s10.verify(m.g.K.R10); R = m.g.K.s10_roots('a29', False)
        return [k for k in range(mm['n_shards']) if any(not m.g.unit_path(R, c, k).exists() for c in m.g.K.CONDS)]
    raise SystemExit(f'unknown item {item}')


def submit(item, shards):
    s = ','.join(map(str, shards))
    if item == 'e1u0':
        return sh(f'sbatch --parsable --exclude=d1028 --export=ALL,SAMPLE=U0,TITLES=false_0,SHARDS={s} {H}/13_stage13/stage13_e1x6_extra_20261114_gpu.sbatch')
    if item == 'a29':
        return sh(f'sbatch --parsable --export=ALL,ALL=1 {T}/a29_gpu.sbatch')
    return sh(f'sbatch --parsable --export=ALL,SHARDS={s} {T}/{item}_gpu.sbatch')


def analyze(item):
    if item == 'e1u0':
        out = R13 / 'summary_e1x6_extra_U0_20261122'
        return sh(f'~/conda-envs/jlens/bin/python {H}/13_stage13/stage13_e1x6_extra_analyze_20261114.py --out {out}')
    if item == 'a27': return sh(f'~/conda-envs/jlens/bin/python {T}/a27_inject_followup.py analyze')
    if item == 'a28': return sh(f'~/conda-envs/jlens/bin/python {T}/a28_x4topic.py analyze')
    if item == 'a29': return sh(f'~/conda-envs/jlens/bin/python {T}/a29_layerfill.py analyze')


def main():
    item = os.environ['ITEM']; st = G / f'logs/todo_gate_{item}.round'
    rnd = int(st.read_text()) + 1 if st.exists() else 1; st.write_text(str(rnd))
    miss = missing(item); print(f'gate {item} round {rnd} job {ME}: missing {len(miss)} {miss}', flush=True)
    if not miss:
        rc, out = analyze(item); print(out[-4000:], flush=True); print('ANALYSIS', 'DONE' if rc == 0 else f'FAILED rc={rc}', flush=True); sys.exit(rc)
    if rnd == 1 and os.environ.get('TRIAL'):
        el = elapsed_s(os.environ['TRIAL']); n = len(miss) + 1
        if el is None: print('WARN: trial elapsed unknown; no cost check', flush=True)
        else:
            per = max(el - LOAD_S, 1) if item != 'a29' else max(el - LOAD_S, 1)
            est = (per * n + LOAD_S * (-(-n // PER_JOB))) / 3600
            print(f'cost check: trial {el}s -> projected {est:.2f} GPU-h for {n} shards (cap {CAP_H[item]} h)', flush=True)
            (G / f'logs/todo_gate_{item}.cost.json').write_text(json.dumps(dict(trial=os.environ['TRIAL'], trial_s=el, n_shards=n, projected_gpu_h=est, cap_h=CAP_H[item])))
            if est > CAP_H[item]: print('STOP: projected cost above cap; item stopped after the trial (report to user)', flush=True); sys.exit(0)
    if rnd > MAX_ROUNDS: print('STOP: still missing after', MAX_ROUNDS, 'rounds', flush=True); sys.exit(1)
    jobs = []
    groups = [miss[i:i + PER_JOB] for i in range(0, len(miss), PER_JOB)] if item != 'a29' else [miss] * 3   # a29 --all jobs share work via claims; up to 3 in parallel
    for gsh in groups[:3]:
        if gpu_jobs() >= 8: print('QOS: 8 GPU jobs queued, not submitting more this round', flush=True); break
        rc, out = submit(item, gsh)
        if rc != 0 or not out.strip().split()[-1].isdigit():
            print('sbatch failed (check squeue/sacct before resubmitting):', out, flush=True); break
        jobs.append(out.strip().split()[-1]); print('submitted', gsh, '->', jobs[-1], flush=True)
    dep = f'--dependency=afterany:{":".join(jobs)}' if jobs else '--begin=now+20minutes'
    rc, out = sh(f'sbatch --parsable {dep} --export=ALL,ITEM={item} {T}/todo_gate.sbatch')
    print('gate requeued' if rc == 0 else 'gate requeue FAILED', out, flush=True)


if __name__ == '__main__':
    main()
