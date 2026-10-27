"""Stage 11 queue keeper (CPU, 2026-10-27; user: "once a GPU job finishes, the next one must already be queued").

Every 10 min: while Stage 11 units remain, keep each A100 partition's submit slots full of 90-min s11w workers
(gpu 8, gpu-short 8, gpu-interactive 4 jobs per user, counting every job of ours in that partition). Submits nothing
while 351_stage10/logs/pool/PAUSED exists (smoke failure or fast-exit alarm) and stops when no unit is left. Never
cancels anything. Log: 361_stage11/logs/keeper_<job>.log
"""
import importlib.util, os, subprocess, sys, time
from pathlib import Path

D = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('s11', D / '361_stage11.py'); s11 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s11)
PARTS = {'gpu': 8, 'gpu-short': 8, 'gpu-interactive': 4}
MINUTES = 90
PAUSED = s11.R10 / 'logs/pool/PAUSED'


def sh(cmd):
    for i in range(4):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        time.sleep(15 * (i + 1))
    s11.log('command failed:', cmd, r.stderr.strip()); return None


def main():
    U = s11.units(); s11.log(f'keeper up: {len(U)} units, partitions {PARTS}, {MINUTES} min jobs')
    while True:
        left = [u for u in U if not s11.out_path(u).exists()]
        if not left: s11.log('all Stage 11 units exist - keeper done'); return
        if PAUSED.exists(): s11.log('PAUSED exists - submitting nothing'); time.sleep(600); continue
        q = sh(f'squeue -u {os.environ["USER"]} -h -o "%P"')
        if q is None: time.sleep(600); continue
        used = {p: 0 for p in PARTS}
        for p in q.split():
            if p in used: used[p] += 1
        for p, cap in PARTS.items():
            for _ in range(cap - used[p]):
                out = sh(f'sbatch --parsable --partition={p} --time={MINUTES} --export=ALL,BUDGET={MINUTES - 10} {D}/stage11_work.sbatch')
                s11.log(f'{len(left)} units left; {p} {used[p]}/{cap} -> submitted', (out or '?').strip())
                if out is None: break                                    # sbatch refused (may still have queued): recount next round
        time.sleep(600)


if __name__ == '__main__':
    main()
