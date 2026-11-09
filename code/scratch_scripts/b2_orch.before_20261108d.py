#!/usr/bin/env python
"""Batch-2 orchestrator (2026-11-06). Runs as a short CPU Slurm job every ~15 min (b2_orch.sbatch resubmits itself),
so no Claude helper has to wait. One poll = one pass over the items below; all decisions come from files and sacct.

Rules (HANDOFF long-term rules + addenda 10-12):
- Nothing starts before batch 1 is finished (391_groups/reports/b1_p12f_report.md exists).
- Per item: gate (1 real shard, hard check) -> only if the gate job COMPLETED (exit 0) and its check file says PASS
  -> the rest. A gate that FAILED (exit 3 = hard check, or a crash) stops that item only (state 'stopped'); the gate
  job itself mails on FAIL. Other items continue.
- GPU jobs: at most MAX_GPU_QUEUED of the user's GPU jobs in the queue (QOS limit 8). Every GPU job here is submitted
  with -p gpu,gpu-short,gpu-interactive --time-min=20 (backfill); the scripts cap their budget at the real time left.
- Items whose rest phase self-chains (cd, b2B) are re-kicked if their chain broke (no job queued, not finished), <= 6 times.
- STOP file (orch_b2/STOP) ends the orchestrator. State: orch_b2/state.json; log: orch_b2/orch.log.
Usage: b2_orch.py poll [--dry]
"""
import json, os, subprocess, sys, time
from pathlib import Path

J = Path('/scratch/zhang.zhiqi2/jlens'); R13 = J / '381_stage13'; G = J / '391_groups'
W13 = Path.home() / 'jlens_work/13_stage13'; W14 = Path.home() / 'jlens_work/14_groups'
OD = R13 / 'orch_b2'; STATE = OD / 'state.json'; LOG = OD / 'orch.log'
GPU_OPTS = ['-p', 'gpu,gpu-short,gpu-interactive', '--time-min=00:20:00']
MAX_GPU_QUEUED = 8
DRY = '--dry' in sys.argv


def log(*a):
    s = time.strftime('%F %T ') + ' '.join(str(x) for x in a)
    print(s, flush=True)
    try:
        with open(LOG, 'a') as f: f.write(s + '\n')
    except Exception as ex: print('WARN log write failed', ex)


def sh(cmd, cwd=None):
    for i in range(3):
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if p.returncode == 0: return p.stdout.strip()
        time.sleep(10)
    raise RuntimeError(f'{cmd}: {p.stderr.strip()}')


def sbatch(args, cwd, gpu=False):
    cmd = ['sbatch', '--parsable'] + (GPU_OPTS if gpu else []) + args
    if DRY: log('DRY', cwd, ' '.join(cmd)); return 'DRY'
    try: out = sh(cmd, cwd=cwd)
    except RuntimeError as ex:
        log('sbatch error (checking squeue before any retry next poll):', ex); return None
    jid = out.split(';')[0]; log('submitted', jid, ' '.join(args)); return jid


def job_state(jid):
    if not jid or jid == 'DRY': return 'DRY' if jid == 'DRY' else None
    try: out = sh(['sacct', '-j', str(jid), '-X', '-n', '-P', '-o', 'State,ExitCode'])
    except RuntimeError: return None
    if not out: return 'PENDING'
    st = out.splitlines()[0].split('|')[0].split()[0]
    return st


def queued(names):
    out = sh(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%j|%P'])
    rows = [l.split('|') for l in out.splitlines() if l]
    gpu = sum(1 for j, p in rows if p.startswith('gpu'))
    return {n: sum(1 for j, p in rows if j == n) for n in names}, gpu


def jread(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None


def n_files(d, pat): return len(list(Path(d).glob(pat)))


# ---------------------------------------------------------------- items
ITEMS = {
    'cd': dict(cwd=W14, name='b2cd_gpu', gate=['--export=ALL,MODE=gate', 'b2_cd_gpu.sbatch'],
               gate_ok=lambda: (jread(G / 'b2_cd/summary/hardcheck_rerun.json') or {}).get('status') == 'PASS',
               rest=['--export=ALL,MODE=all,AUTO=1', 'b2_cd_gpu.sbatch'], selfchain=True,
               done=lambda: (G / 'reports/b2_cd_report.md').exists() or (G / 'b2_cd/reports/b2_cd_report.md').exists()),
    'b2B': dict(cwd=W13, name='b2B_gpu', gate=['--export=ALL,MODE=gate', 'stage13_b2B_gpu.sbatch'],
                gate_ok=lambda: (jread(R13 / 'summary_b2B/gate.json') or {}).get('status') in ('PASS', 'WARN'),
                rest=['--export=ALL,MODE=all,AUTO=1', 'stage13_b2B_gpu.sbatch'], selfchain=True,
                done=lambda: all((R13 / f'reports/b2_{k}.md').exists() for k in ('e1noise', 'e1t5', 'x3role', 'm3tok'))),
    'ps': dict(cwd=W13, name='b2ps_gpu', gate=['--export=ALL,SHARDS=0', 'stage13_b2_ps_gpu.sbatch'],
               partial=['--export=ALL,ARGS=--partial', 'stage13_b2_ps_analyze.sbatch'],
               gate_ok=lambda: (jread(R13 / 'summary_b2_ps/hardcheck_partial.json') or {}).get('status') == 'PASS',
               rest=['--export=ALL,SHARDS=--all', 'stage13_b2_ps_gpu.sbatch'], parallel=2,
               complete=lambda: n_files(R13 / 'raw/b2_pscope', 'shard_*.parquet') >= 24,
               final=[['stage13_b2_ps_analyze.sbatch']],
               done=lambda: (R13 / 'summary_b2_ps/hardcheck.json').exists()),
    'np': dict(cwd=W13, name='b2np_gpu', gate=['--export=ALL,SHARDS=0', 'stage13_b2_np_gpu.sbatch'],
               gate_ok=lambda: not (R13 / 'summary_b2_np/HARD_CHECK1_FAILED').exists() and n_files(R13 / 'raw/b2_npprobe', '*/shard_000.npz') >= 6,
               rest=['--export=ALL,SHARDS=--all', 'stage13_b2_np_gpu.sbatch'], parallel=3,
               complete=lambda: n_files(R13 / 'raw/b2_npprobe', '*/shard_*.npz') >= 432,
               final=[['stage13_b2_np_probe_v2.sbatch'], ['stage13_b2_np_report_v2.sbatch']],   # D11-1 v2 (2026-11-08): probe_v2 stores per-title controls; report_v2 Vpd primary
               done=lambda: (R13 / 'reports/b2_np_report_v2.md').exists()),
}
# group C items (2-1, 2-2, 2-11): status-driven (b2_orch_items_c.json; each script's `status` names the next step).
ITEMS_C = json.loads((W13 / 'b2_orch_items_c.json').read_text())
ITEMS_C.pop('_doc', None)
STEP_CAP = dict(gate=2, gate_v2=2, read_gate=2, fit=12, resume=12, rest=12, holdout_and_rest=12, probe=2, analyze=2)


def poll_c(st, gpu):
    for k, it in ITEMS_C.items():
        s = st.setdefault('C' + k, dict(phase='run', subs={}))
        if s['phase'] in ('done', 'stopped'): continue
        try:
            o = json.loads(sh(it['status_cmd'], cwd=it['cwd']).splitlines()[-1])
        except Exception as ex:
            log(k, 'WARN status failed (retry next poll):', repr(ex)); continue
        nxt = o.get('next'); s['last'] = o
        if nxt == 'done': s['phase'] = 'done'; log(k, 'DONE', o.get('progress')); continue
        if nxt == 'failed': s['phase'] = 'stopped'; log(k, 'FAILED - item STOPPED:', o.get('reason')); continue
        if nxt == 'wait_tests' or nxt not in it['steps']: continue
        step = it['steps'][nxt]
        nq = sum(queued(it['job_names'])[0].values())
        if nq >= step['max_parallel']: continue
        if step['gpu'] and gpu >= MAX_GPU_QUEUED: continue
        n = s['subs'].get(nxt, 0)
        if n >= STEP_CAP.get(nxt, 4):
            s['phase'] = 'stopped'; log(k, f'step {nxt} submitted {n} times without progress - item STOPPED'); continue
        for _ in range(step['max_parallel'] - nq):
            if step['gpu'] and gpu >= MAX_GPU_QUEUED: break
            if sbatch(step['sbatch_args'], it['cwd'], gpu=step['gpu']):
                s['subs'][nxt] = s['subs'].get(nxt, 0) + 1
                if step['gpu']: gpu += 1
    return gpu


def poll():
    OD.mkdir(parents=True, exist_ok=True)
    if (OD / 'STOP').exists(): log('STOP file present - orchestrator ends'); return False
    st = jread(STATE) or {}
    if not Path(os.environ.get('ORCH_B1_REPORT', G / 'reports/b1_p12f_report.md')).exists():
        log('batch 1 not finished (no b1_p12f_report.md) - waiting'); return True
    names = [v['name'] for v in ITEMS.values()]
    q, gpu = queued(names)
    for k, it in ITEMS.items():
        s = st.setdefault(k, dict(phase='gate', kicks=0))
        if s['phase'] in ('done', 'stopped'): continue
        if it['done']():
            s['phase'] = 'done'; log(k, 'DONE'); continue
        if s['phase'] == 'gate':
            if gpu >= MAX_GPU_QUEUED: continue
            j = sbatch(it['gate'], it['cwd'], gpu=True)
            if j: s.update(phase='gate_wait', gate_job=j); gpu += 1
        elif s['phase'] == 'gate_wait':
            js = job_state(s['gate_job'])
            if js in ('PENDING', 'RUNNING', 'REQUEUED', 'CONFIGURING', 'COMPLETING', None): continue
            if js != 'COMPLETED' and js != 'DRY':
                s['phase'] = 'stopped'; log(k, f'GATE job {s["gate_job"]} ended {js} - item STOPPED (hard check failed or crash)'); continue
            if 'partial' in it:
                j = sbatch(it['partial'], it['cwd'])
                if j: s.update(phase='partial_wait', partial_job=j)
                continue
            s['phase'] = 'gate_check'
        if s['phase'] == 'partial_wait':
            js = job_state(s['partial_job'])
            if js in ('PENDING', 'RUNNING', 'REQUEUED', 'CONFIGURING', 'COMPLETING', None): continue
            if js != 'COMPLETED' and js != 'DRY':
                s['phase'] = 'stopped'; log(k, f'partial check job {s["partial_job"]} ended {js} - item STOPPED'); continue
            s['phase'] = 'gate_check'
        if s['phase'] == 'gate_check':
            if not (it['gate_ok']() or DRY):
                s['phase'] = 'stopped'; log(k, 'gate check file not PASS - item STOPPED'); continue
            log(k, 'GATE PASS'); s['phase'] = 'rest'
        if s['phase'] == 'rest':
            if it.get('selfchain'):
                if s.get('rest_job') is None:
                    if gpu < MAX_GPU_QUEUED:
                        j = sbatch(it['rest'], it['cwd'], gpu=True)
                        if j: s['rest_job'] = j; gpu += 1
                elif q.get(it['name'], 0) == 0 and job_state(s['rest_job']) not in ('PENDING', 'RUNNING', None):
                    # chain ended without the final report: re-kick (chain scripts skip finished units)
                    if s['kicks'] < 6 and gpu < MAX_GPU_QUEUED:
                        j = sbatch(it['rest'], it['cwd'], gpu=True)
                        if j: s['rest_job'] = j; s['kicks'] += 1; gpu += 1; log(k, 'chain re-kicked', s['kicks'])
                    elif s['kicks'] >= 6: s['phase'] = 'stopped'; log(k, 'chain broke 6 times - STOPPED')
            else:
                if it['complete']():
                    s['phase'] = 'final'
                else:
                    want = it['parallel'] - q.get(it['name'], 0)
                    for _ in range(max(0, want)):
                        if gpu >= MAX_GPU_QUEUED: break
                        if sbatch(it['rest'], it['cwd'], gpu=True): gpu += 1
        if s['phase'] == 'final' and (OD / f'HOLD_{k}_final').exists():
            log(k, f'final step held by orch_b2/HOLD_{k}_final (user/main session); not submitting'); continue
        if s['phase'] == 'final':
            prev = None
            for f in it['final']:
                j = sbatch(([f'--dependency=afterok:{prev}'] if prev and prev != 'DRY' else []) + f, it['cwd'])
                prev = j
            s['phase'] = 'final_wait'; log(k, 'final analysis submitted')
        if s['phase'] == 'final_wait' and it['done']():
            s['phase'] = 'done'; log(k, 'DONE')
    gpu = poll_c(st, gpu)
    if not DRY: STATE.write_text(json.dumps(st, indent=1))
    log('state', json.dumps({k: v['phase'] for k, v in st.items()}), 'gpu_queued', gpu)
    if all(v['phase'] in ('done', 'stopped', 'final_wait') for v in st.values()) and len(st) == len(ITEMS) + len(ITEMS_C) and \
            all(v['phase'] in ('done', 'stopped') for v in st.values()):
        log('all batch-2 items done or stopped - orchestrator ends (batch 3 to be started by the main session / its own orchestrator)')
        return False
    return True


if __name__ == '__main__':
    try: again = poll()
    except Exception as ex:
        log('WARN poll crashed (non-fatal, retry next poll):', repr(ex)); again = True
    print('AGAIN' if again else 'END')
