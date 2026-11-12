"""Item 2-2 (F1 split-half, D12-2) resume chain, 2026-11-10. Runs as ONE CPU job on `short` (stage12_b2_f1team_v2_chain.sbatch).

Why: b2_orch.py stopped 2-2 at 2026-11-10 11:47 ("step fit submitted 12 times without progress"). Evidence: all 12 fit jobs
ended COMPLETED (one TIMEOUT), none 0:9; each started through backfill with --time-min=20, so its limit was 20 min, the python
budget min(42, left-4) allowed only 2 prompts (~290 s each) after the model load, and the joint fit advanced 2 prompts per job
(13 -> 25 of 40). STEP_CAP (12) counts submissions, not progress. Not a hard-check failure; frozen code unchanged.

What it does (one GPU job at a time except 'rest', which may run 2 read workers: their units are claimed by s11.claim):
  loop every POLL s: `stage12_b2_f1team_v2.py status` -> next step
    fit / read_gate  -> sbatch stage12_b2_f1team_v2_gpu.sbatch (UNIT=fit | UNIT=read:true:0), full 45 min, NO --time-min,
                        -p gpu,gpu-short, --exclude from killguard (DEFER -> wait)
    rest             -> same with ALL=1, up to 2 workers
    analyze          -> sbatch stage12_b2_f1team_v2_analyze.sbatch once, then wait for 'done'
    done -> exit 0 ; failed / HARD_CHECK_FAILED marker -> exit 3 (hard check: stop, report)
  job endings: signal 9 (epilog kill) -> resubmit, kills counted per unit (step@progress), > 3 -> stop + review_queue line;
  plain CANCELLED at a controller reset -> resubmit, not counted; COMPLETED/TIMEOUT without progress twice in a row on the
  same step -> stop (exit 4); exit 2 (hard check) -> stop (exit 3); any other failure -> stop (exit 5).
  After an sbatch error: squeue check before trying again next poll. State: 371_stage12/summary/chain22/state.json; log chain.log.
"""
import json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

H = Path.home() / 'jlens_work'; D = H / '12_stage12'; R12 = Path('/scratch/zhang.zhiqi2/jlens/371_stage12')
sys.path.insert(0, str(H)); import killguard as kg   # noqa: E402
PY = str(Path.home() / 'conda-envs/jlens/bin/python')
ST = R12 / 'summary/chain22'; STATE = ST / 'state.json'; CLOG = ST / 'chain.log'
GPU_SB = D / 'stage12_b2_f1team_v2_gpu.sbatch'; AN_SB = D / 'stage12_b2_f1team_v2_analyze.sbatch'
NAME, AN_NAME = 'b2c_f1team2', 'b2c_f1t2_an'
STEPS = {'fit': 'UNIT=fit', 'read_gate': 'UNIT=read:true:0', 'rest': 'ALL=1'}
PAR = {'fit': 1, 'read_gate': 1, 'rest': 2}
POLL = int(__import__('os').environ.get('CHAIN_POLL', 300)); MAX_H = 46.5; STALL_CAP = 2
DRY = '--dry' in sys.argv


def note(*x):
    line = f'{datetime.now().isoformat(timespec="seconds")} chain22 {" ".join(str(v) for v in x)}'
    print(line, flush=True)
    ST.mkdir(parents=True, exist_ok=True)
    with open(CLOG, 'a') as f: f.write(line + '\n')


def sh(cmd, t=300):
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=t); return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e: return -1, '', repr(e)


def status():
    rc, out, _ = sh([PY, str(D / 'stage12_b2_f1team_v2.py'), 'status'])
    try: return json.loads(out.splitlines()[-1])
    except Exception: return None


def queued(name):
    rc, out, _ = sh(['squeue', '-h', '-u', 'zhang.zhiqi2', '-n', name, '-o', '%i'], 90)
    return None if rc != 0 else [x for x in out.split() if x]


def submit(env, gpu=True, unit=''):
    ex = []
    if gpu:
        ex, mode, why = kg.gpu_exclude(NAME, 45)
        if mode == 'defer': note('killguard DEFER:', why); return None
    cmd = ['sbatch', '--parsable'] + (['-p', 'gpu,gpu-short'] + ex if gpu else []) + ([f'--export=ALL,{env}'] if env else []) + [str(GPU_SB if gpu else AN_SB)]
    if DRY: note('DRY', ' '.join(cmd)); return 'DRY'
    rc, out, err = sh(cmd, 120)
    if rc == 0 and out.split(';')[0].isdigit():
        j = out.split(';')[0]; kg.record(j, NAME if gpu else AN_NAME, unit, 45, 'chain22', '', ','.join(ex)); note('submitted', j, ' '.join(cmd[2:])); return j
    note('sbatch error (squeue checked before any retry next poll):', (err or out)[:200]); return None


def main():
    st = json.loads(STATE.read_text()) if STATE.exists() else dict(jobs=[], stall={}, an_job=None)
    save = lambda: (None if DRY else kg.atomic_write_json(STATE, st))
    note('start', json.dumps({k: v for k, v in st.items() if k != 'jobs'}), 'open jobs', [j['id'] for j in st['jobs']])
    t0 = time.time()
    while time.time() - t0 < MAX_H * 3600:
        o = status()
        if o is None: time.sleep(POLL); continue
        nxt, prog = o.get('next'), str(o.get('progress'))
        if (R12 / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').exists() or nxt == 'failed':
            note('STOP: hard check failed / status failed:', o.get('reason')); return 3
        if nxt == 'done': note('2-2 done:', prog); return 0
        # ---- endings of our jobs
        for j in list(st['jobs']):
            s, ec, end = kg.job_info(j['id'])
            if s is None or s.split()[0] in ('PENDING', 'RUNNING', 'REQUEUED', 'CONFIGURING', 'COMPLETING', 'SUSPENDED'): continue
            st['jobs'].remove(j); save()
            if kg.is_reset_cancel(s, end): note(f'job {j["id"]} ({j["step"]}) CANCELLED by the controller reset: resubmit, not counted'); continue
            if kg.is_kill(s, ec):
                n = kg.kill_note('chain22', f'{j["step"]}@{j["prog"]}', j['id']); note(f'job {j["id"]} ({j["step"]} @ {j["prog"]}) killed by signal 9 ({s} {ec}), kill {n}')
                if kg.over_cap(n): kg.review_line('chain22', f'2-2:{j["step"]}@{j["prog"]}', f'jobs {j["id"]}'); note('STOP: kill cap'); return 4
                continue
            rc = ec.split(':')[0]
            if s.startswith('COMPLETED') or s.startswith('TIMEOUT'):
                key = j['step']
                if prog == j['prog'] and nxt == j['step']: st['stall'][key] = st['stall'].get(key, 0) + 1
                else: st['stall'][key] = 0
                note(f'job {j["id"]} ({j["step"]}) ended {s}; progress {j["prog"]} -> {prog}; stall {st["stall"][key]}'); save()
                if st['stall'][key] >= STALL_CAP and j['step'] != 'rest':
                    note(f'STOP: {STALL_CAP} {j["step"]} jobs in a row without progress'); return 4
                continue
            if rc == '2': note(f'STOP: job {j["id"]} exit 2 (hard check) {s}'); return 3
            note(f'STOP: job {j["id"]} ({j["step"]}) ended {s} {ec} (crash, not an epilog kill)'); return 5
        if st.get('an_job'):
            s, ec, end = kg.job_info(st['an_job'])
            if s and s.split()[0] not in ('PENDING', 'RUNNING', 'REQUEUED', 'CONFIGURING', 'COMPLETING'):
                if kg.is_reset_cancel(s, end) or kg.is_kill(s, ec): note(f'analysis {st["an_job"]} ended {s} {ec}: resubmit'); st['an_job'] = None; save()
                elif nxt != 'done': note(f'STOP: analysis {st["an_job"]} ended {s} {ec} but status is {nxt}'); return 5
        # ---- submit
        if nxt == 'analyze':
            if st.get('an_job') is None and not (queued(AN_NAME) or []):
                j = submit('', gpu=False, unit='analyze')
                if j: st['an_job'] = j; save()
        elif nxt in STEPS:
            q = queued(NAME)
            if q is None: time.sleep(POLL); continue
            for _ in range(max(0, PAR[nxt] - len(q))):
                j = submit(STEPS[nxt], unit=f'{nxt}@{prog}')
                if not j: break
                st['jobs'].append(dict(id=j, step=nxt, prog=prog)); save()
        elif nxt != 'wait_tests':
            note(f'STOP: next step {nxt!r} not handled'); return 5
        if DRY: return 0
        time.sleep(POLL)
    note('time limit reached: resubmit stage12_b2_f1team_v2_chain.sbatch to continue (state kept)'); return 6


if __name__ == '__main__':
    sys.exit(main())
