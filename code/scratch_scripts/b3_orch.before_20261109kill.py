#!/usr/bin/env python
"""Batch-3 orchestrator (2026-11-08). Runs as a short CPU Slurm job every ~15 min (b3_orch.sbatch resubmits itself),
like b2_orch.py. One poll = one pass; all decisions come from files and sacct.

Rules (addendum 14 + HANDOFF long-term rules):
- Nothing starts before batch 2 is finished: every item in orch_b2/state.json is 'done' or 'stopped' (afterany between
  batches). Env ORCH_B2_STATE overrides the path (dry-run simulation).
- Items in order: 3-1, then 3-2 (3-2 starts once 3-1 is done OR stopped). 3-3 is STOPPED (user decision (a)): not here.
- Per item (afterok within the item):
    gate   = stage13_b3_s10_gpu.sbatch MODE=gate (shard 0, 7 conditions, hard check; exit 3 = FAIL), full 45 min, no
             --time-min (a cut gate would look like a FAIL). Exit 3 -> item STOPPED. Other failure (crash/timeout/node)
             -> one retry, then STOPPED. After COMPLETED, summary_b3_s10_<item>/gate.json must say PASS.
    rest   = b3_orch_gpu.sbatch workers (MODE=all, budget capped at the real time left), -p gpu,gpu-short (not gpu-interactive: submit cap 4)
             --time-min=20; up to PARALLEL at once (1 when <= 40 units remain), capped submissions per item.
             3 worker crashes in a row without new units -> STOPPED. HARD_CHECK_FAILED marker -> STOPPED.
    final  = stage13_b3_s10_analyze.sbatch (CPU; NEXT_GATE not used, the orchestrator starts 3-2 itself).
             Held while orch_b3/HOLD_<item>_final exists. Exit 0 -> done; exit 3 (marker) -> STOPPED;
             exit 2 (units missing) -> back to rest; other -> one retry, then STOPPED.
- GPU queue: all of the user's GPU jobs (any partition starting with 'gpu') count; at most MAX_GPU_QUEUED (QOS 8).
- Every item that becomes done/stopped appends one line to review_queue_events.log (env ORCH_EVENTS_LOG overrides).
- STOP file (orch_b3/STOP) ends the orchestrator. State: orch_b3/state.json; log: orch_b3/orch.log (env ORCH_B3_DIR
  overrides the directory, for the dry-run simulation).
Usage: b3_orch.py poll [--dry]      (--dry: print sbatch commands, submit nothing; ORCH_DRY_ADVANCE=1 also treats
                                     every 'complete'/'report' check as true so the whole path is printed)
"""
import json, os, subprocess, sys, time
from pathlib import Path

J = Path('/scratch/zhang.zhiqi2/jlens'); R13 = J / '381_stage13'
W13 = Path.home() / 'jlens_work/13_stage13'
OD = Path(os.environ.get('ORCH_B3_DIR', R13 / 'orch_b3')); STATE = OD / 'state.json'; LOG = OD / 'orch.log'
B2_STATE = Path(os.environ.get('ORCH_B2_STATE', R13 / 'orch_b2/state.json'))
B2_KEYS = ['cd', 'b2B', 'ps', 'np', 'C2-1', 'C2-2', 'C2-11']          # items of b2_orch.py (ITEMS + 'C' + ITEMS_C)
EVENTS = Path(os.environ.get('ORCH_EVENTS_LOG', J / 'review_queue_events.log'))
GPU_OPTS = ['-p', 'gpu,gpu-short']        # not gpu-interactive: submit cap 4 (QOSMaxSubmit), as b2_orch.py
TIME_MIN = ['--time-min=00:20:00']
MAX_GPU_QUEUED = 8
PARALLEL = 3
N_UNITS = 504                                                            # 7 conditions x 72 Stage 10 shards
DRY = '--dry' in sys.argv
ADV = DRY and os.environ.get('ORCH_DRY_ADVANCE') == '1'
WAITING = ('PENDING', 'RUNNING', 'REQUEUED', 'CONFIGURING', 'COMPLETING', 'SUSPENDED', 'RESIZING', None)


def log(*a):
    s = time.strftime('%F %T ') + ' '.join(str(x) for x in a)
    print(s, flush=True)
    try:
        with open(LOG, 'a') as f: f.write(s + '\n')
    except Exception as ex: print('WARN log write failed', ex)


def event(item, state, report, note=''):
    line = '\t'.join([time.strftime('%F %T'), 'b3', item, state, str(report), note])
    log('EVENT', line)
    try:
        with open(EVENTS, 'a') as f: f.write(line + '\n')
    except Exception as ex: log('WARN events log write failed', ex)


def sh(cmd, cwd=None):
    for i in range(3):
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if p.returncode == 0: return p.stdout.strip()
        time.sleep(10)
    raise RuntimeError(f'{cmd}: {p.stderr.strip()}')


def sbatch(args, gpu=False, time_min=False):
    cmd = ['sbatch', '--parsable'] + (GPU_OPTS if gpu else []) + (TIME_MIN if time_min else []) + args
    if DRY: log('DRY', W13, ' '.join(cmd)); return 'DRY'
    try: out = sh(cmd, cwd=W13)
    except RuntimeError as ex:
        log('sbatch error (checking squeue before any retry next poll):', ex)
        try: log('squeue:', sh(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%i %j %T']).replace('\n', '; '))
        except Exception: pass
        return None
    jid = out.split(';')[0]; log('submitted', jid, ' '.join(args)); return jid


def job_state(jid):
    """(state, exit code) from sacct; ('COMPLETED', 0) for DRY."""
    if jid == 'DRY': return 'COMPLETED', 0
    if not jid: return None, None
    try: out = sh(['sacct', '-j', str(jid), '-X', '-n', '-P', '-o', 'State,ExitCode'])
    except RuntimeError: return None, None
    if not out: return 'PENDING', None
    st, ec = out.splitlines()[0].split('|')[:2]
    try: rc = int(ec.split(':')[0])
    except Exception: rc = None
    return st.split()[0], rc


def queued():
    out = sh(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%j|%P'])
    rows = [l.split('|') for l in out.splitlines() if l]
    return {j: sum(1 for jj, _ in rows if jj == j) for j, _ in rows}, sum(1 for _, p in rows if p.startswith('gpu'))


def jread(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None


# ---------------------------------------------------------------- items (paths as stage13_b3_cols.s10_roots)
def roots(item):
    t = item.replace('-', '_')
    return dict(raw=R13 / f'raw/b3_s10_{t}', gate=R13 / f'summary_b3_s10_{t}/gate.json',
                fail=R13 / f'summary_b3_s10_{t}/HARD_CHECK_FAILED', report=R13 / f'reports/b3_{t}_report.md')


def n_units(item):
    return sum(1 for f in roots(item)['raw'].glob('*/shard_*.npz') if '.tmp' not in f.name)


ITEMS = {
    '3-1': dict(name='b3_31_gpu', an='b3_31_an', max_workers=40),     # ~9-18 worker jobs needed
    '3-2': dict(name='b3_32_gpu', an='b3_32_an', max_workers=60),     # ~13-26 worker jobs needed
}
ORDER = ['3-1', '3-2']


def b2_finished():
    st = jread(B2_STATE)
    if not st: return False, 'no orch_b2 state'
    miss = [k for k in B2_KEYS if k not in st]
    open_ = {k: v.get('phase') for k, v in st.items() if v.get('phase') not in ('done', 'stopped')}
    if miss or open_: return False, f'missing {miss} open {open_}'
    return True, ''


def stop(k, s, why):
    s['phase'] = 'stopped'; s['why'] = why; log(k, 'STOPPED:', why)
    event(k, 'stopped', roots(k)['report'] if roots(k)['report'].exists() else '-', why)


def poll_item(k, s, q, gpu):
    it, R = ITEMS[k], roots(k)
    if s['phase'] == 'gate':
        if (jread(R['gate']) or {}).get('status') == 'PASS':
            log(k, 'gate.json already PASS - skipping gate job'); s['phase'] = 'rest'
        elif gpu < MAX_GPU_QUEUED:
            j = sbatch(['-J', it['name'], f'--export=ALL,ITEM={k},MODE=gate', 'stage13_b3_s10_gpu.sbatch'], gpu=True)
            if j: s.update(phase='gate_wait', gate_job=j); s['gate_tries'] = s.get('gate_tries', 0) + 1; gpu += 1
            return gpu
        else: return gpu
    if s['phase'] == 'gate_wait':
        js, rc = job_state(s['gate_job'])
        if js in WAITING: return gpu
        if js != 'COMPLETED':
            if rc == 3 or R['fail'].exists(): stop(k, s, f'GATE job {s["gate_job"]} {js} exit {rc}: hard check FAILED'); return gpu
            if s.get('gate_tries', 1) < 2:
                log(k, f'gate job {s["gate_job"]} ended {js} exit {rc} (not exit 3) - one retry'); s['phase'] = 'gate'; return gpu
            stop(k, s, f'GATE job {s["gate_job"]} ended {js} exit {rc} twice'); return gpu
        if not ((jread(R['gate']) or {}).get('status') == 'PASS' or DRY):
            stop(k, s, f'gate job COMPLETED but {R["gate"]} not PASS'); return gpu
        log(k, 'GATE PASS'); s['phase'] = 'rest'
    if s['phase'] == 'rest':
        if R['fail'].exists(): stop(k, s, 'HARD_CHECK_FAILED marker present'); return gpu
        n = n_units(k)
        # crash bookkeeping: finished worker jobs that were not COMPLETED/TIMEOUT, with no new units since
        for j in list(s.get('workers', [])):
            js, rc = job_state(j)
            if js in WAITING: continue
            s['workers'].remove(j)
            if js in ('COMPLETED', 'TIMEOUT') or n > s.get('units_seen', 0): s['crashes'] = 0
            else: s['crashes'] = s.get('crashes', 0) + 1; log(k, f'worker {j} ended {js} exit {rc} (crash {s["crashes"]})')
            if rc == 3: stop(k, s, f'worker {j} exit 3 (refused / hard check marker)'); return gpu
        s['units_seen'] = max(n, s.get('units_seen', 0))
        if s.get('crashes', 0) >= 3: stop(k, s, '3 worker crashes in a row without new units'); return gpu
        if n >= N_UNITS or ADV:
            log(k, f'all {N_UNITS} units present'); s['phase'] = 'final'
        else:
            left = N_UNITS - n; want = (PARALLEL if left > 40 else 1) - q.get(it['name'], 0)
            for _ in range(max(0, want)):
                if gpu >= MAX_GPU_QUEUED: break
                if s.get('n_workers', 0) >= it['max_workers']:
                    stop(k, s, f'{it["max_workers"]} worker jobs submitted, {left} units still missing'); return gpu
                j = sbatch(['-J', it['name'], f'--export=ALL,ITEM={k}', 'b3_orch_gpu.sbatch'], gpu=True, time_min=True)
                if not j: break
                s.setdefault('workers', []).append(j); s['n_workers'] = s.get('n_workers', 0) + 1; gpu += 1
            if s.get('n_workers'): log(k, f'rest: {n}/{N_UNITS} units, workers submitted so far {s["n_workers"]}')
            return gpu
    if s['phase'] == 'final':
        if q.get(it['name'], 0) and not DRY: log(k, 'workers still queued/running - analysis waits'); return gpu
        if (OD / f'HOLD_{k}_final').exists():
            log(k, f'final step held by {OD}/HOLD_{k}_final (user/main session); not submitting'); return gpu
        j = sbatch(['-J', it['an'], f'--export=ALL,ITEM={k}', 'stage13_b3_s10_analyze.sbatch'])
        if j: s.update(phase='final_wait', an_job=j); s['an_tries'] = s.get('an_tries', 0) + 1; log(k, 'final analysis submitted')
        return gpu
    if s['phase'] == 'final_wait':
        js, rc = job_state(s['an_job'])
        if js in WAITING: return gpu
        if js == 'COMPLETED' and (R['report'].exists() or ADV) and not R['fail'].exists():
            s['phase'] = 'done'; log(k, 'DONE'); event(k, 'done', R['report'], 'analysis exit 0 (full hard check PASS)')
        elif rc == 3 or R['fail'].exists():
            stop(k, s, f'analysis {s["an_job"]} exit {rc}: full hard check FAILED (report with FAIL banner)')
        elif rc == 2 and s.get('an_tries', 1) < 3:
            log(k, 'analysis exit 2 (units missing) - back to rest'); s['phase'] = 'rest'
        elif s.get('an_tries', 1) < 2:
            log(k, f'analysis {s["an_job"]} ended {js} exit {rc} - one retry'); s['phase'] = 'final'
        else:
            stop(k, s, f'analysis {s["an_job"]} ended {js} exit {rc} (retries used)')
    return gpu


def poll():
    OD.mkdir(parents=True, exist_ok=True)
    if (OD / 'STOP').exists(): log('STOP file present - orchestrator ends'); return False
    ok, why = b2_finished()
    if not ok: log('batch 2 not finished -', why, '- waiting'); return True
    st = jread(STATE) or {}
    q, gpu = queued()
    for k in ORDER:
        s = st.setdefault(k, dict(phase='gate'))
        if s['phase'] in ('done', 'stopped'): continue
        prev = ORDER[:ORDER.index(k)]
        if any(st.get(p, {}).get('phase') not in ('done', 'stopped') for p in prev): break   # 3-2 after 3-1
        try: gpu = poll_item(k, s, q, gpu)
        except Exception as ex: log(k, 'WARN item poll crashed (non-fatal, retry next poll):', repr(ex))
        if s['phase'] not in ('done', 'stopped'): break
    if not DRY or 'ORCH_B3_DIR' in os.environ: STATE.write_text(json.dumps(st, indent=1))
    log('state', json.dumps({k: v['phase'] for k, v in st.items()}), 'gpu_queued', gpu)
    if all(st.get(k, {}).get('phase') in ('done', 'stopped') for k in ORDER):
        log('all batch-3 items (3-1, 3-2) done or stopped - orchestrator ends')
        return False
    return True


if __name__ == '__main__':
    try: again = poll()
    except Exception as ex:
        log('WARN poll crashed (non-fatal, retry next poll):', repr(ex)); again = True
    print('AGAIN' if again else 'END')
