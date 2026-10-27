"""Stage 12 queue keeper (CPU): while Stage 12 units remain, keep the A100 submit slots filled with 90-min s12w workers,
spread over gpu / gpu-short / gpu-interactive, and keep one FIT=1 worker queued until the author lens is complete.
Submits nothing while 351_stage10/logs/pool/PAUSED exists. Never cancels anything."""
import importlib.util, os, subprocess, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('s12', D / '371_stage12.py'); s12 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s12)
PARTS = {'gpu': 8, 'gpu-short': 8, 'gpu-interactive': 4}; MIN = 90
PAUSED = s12.R10 / 'logs/pool/PAUSED'


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    s12.log('stage12 keeper up')
    while True:
        left = [u for u in s12.all_units() if not s12.out_path(u).exists()]
        if not left and s12.fit_done(): s12.log('all Stage 12 units exist - keeper done'); return
        if PAUSED.exists(): s12.log('PAUSED - submitting nothing'); time.sleep(600); continue
        q = sh(f'squeue -u {os.environ["USER"]} -h -o "%P|%j"')
        if q is None: time.sleep(600); continue
        rows = [l.split('|') for l in q.split()]; used = {p: sum(r[0] == p for r in rows) for p in PARTS}
        fit_queued = sum(r[1] == 's12fit' for r in rows)
        for p in sorted(PARTS, key=lambda p: used[p] - PARTS[p]):           # emptiest partition first
            for _ in range(PARTS[p] - used[p]):
                fit = not s12.fit_done() and fit_queued == 0
                name = 's12fit' if fit else 's12w'
                out = sh(f'sbatch --parsable --partition={p} --time={MIN} --job-name={name} --export=ALL,BUDGET={MIN - 10},FIT={int(fit)} {D}/stage12_work.sbatch')
                s12.log(f'{len(left)} units left, fit {s12.fit_progress()}/{s12.FIT_N}; {p} -> {name}', (out or 'refused').strip())
                if out is None: break
                fit_queued += fit
        time.sleep(600)


if __name__ == '__main__':
    main()
