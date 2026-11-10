"""Item 2-1 watchdog (CPU, 2026-11-09). Runs on `short` (not on the GPU nodes) via stage9_b2_fitb_v3b_watch.sbatch.

Why: /etc/slurm/epilog.d/00-slurm.epilog.clean.sh runs `pkill -KILL -U <uid>` on a node when the ending job's squeue finds no other job
of the user there (a failed/slow squeue gives an empty list). Every signal-9 death of our d-node jobs since 2026-11-01 (12/12, incl. gate
jobs 11725846 and 11746631) ended within 10 s of another of our jobs ending normally on the same node. Such a kill shows in sacct as
State FAILED (or CANCELLED) with ExitCode 0:9; it is not a code crash and loses at most the unit in progress (all units checkpoint / skip-if-exists).

What it does (one GPU job at a time, all GPU jobs 45 min, no --time-min):
  phase gate : gate_v2.json PASS -> chain; FAIL -> stop. No json: if no gate job queued, submit stage9_b2_fitb_v3b_gate.sbatch when the
               previous gate (if any) died with 0:9 (max KILL_CAP resubmits); a gate ending any other way without json -> stop.
  phase chain: status `next` analyze/done -> end. If a chain or starter job is queued/running -> wait. If the last chain job died with 0:9 ->
               resubmit stage9_b2_fitb_v3_chain.sbatch with its ROUND/PHASE/STALL (max KILL_CAP); if it ended otherwise and no successor
               exists -> stop (the chain's own STOP rules: crash, 12 rounds, no progress).
After every sbatch error: re-check squeue before trying again (next poll). Every action is logged to b2_fitb/chain_v3.log.
"""
import json, re, subprocess, sys, time
from datetime import datetime
from pathlib import Path

D = Path.home() / 'jlens_work/09_stage9'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb'); CLOG = ROOT / 'chain_v3.log'
PY = str(Path.home() / 'conda-envs/jlens/bin/python'); GATE_SB = D / 'stage9_b2_fitb_v3b_gate.sbatch'; CHAIN_SB = D / 'stage9_b2_fitb_v3_chain.sbatch'
KILL_CAP, POLL, MAX_H = 6, 120, 47
STATE = ROOT / 'watch_v3b_state.json'


def note(*x):
    line = f'{datetime.now().isoformat(timespec="seconds")} watch {" ".join(str(v) for v in x)}'
    print(line, flush=True)
    with open(CLOG, 'a') as f: f.write(line + '\n')


def sh(cmd, t=90):
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=t); return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e: return -1, '', repr(e)


def queued(name):
    rc, out, _ = sh(['squeue', '-h', '-u', 'zhang.zhiqi2', '-n', name, '-o', '%i'])
    return None if rc != 0 else [x for x in out.split() if x]


def ended(jid):
    """(state, exitcode) from sacct, or None while unknown/running."""
    rc, out, _ = sh(['sacct', '-n', '-X', '-P', '-j', str(jid), '-o', 'State,ExitCode'])
    if rc != 0 or not out: return None
    s, e = out.splitlines()[0].split('|'); s = s.split()[0]
    return None if s in ('PENDING', 'RUNNING', 'REQUEUED', 'SUSPENDED', 'CONFIGURING', 'COMPLETING') else (s, e)


def killed(st): return st is not None and st[1] == '0:9' and st[0] in ('FAILED', 'CANCELLED')


def submit(sb, env=''):
    cmd = ['sbatch', '--parsable'] + ([f'--export=ALL,{env}'] if env else []) + [str(sb)]
    rc, out, err = sh(cmd)
    if rc == 0 and out.split(';')[0].isdigit(): return out.split(';')[0]
    note('sbatch error (squeue checked before any retry next poll):', ' '.join(cmd), (err or out)[:160]); return None


def gate_status():
    try: return json.loads((ROOT / 'summary/gate_v2.json').read_text())['status']
    except Exception: return None


def item_next():
    rc, out, _ = sh([PY, str(D / 'stage9_b2_fitb_v2.py'), 'status'], t=300)
    try: return json.loads(out.splitlines()[-1])
    except Exception: return None


def last_chain_job():
    """latest chain job id and its ROUND/PHASE/STALL as announced in chain_v3.log."""
    best = None; lines = CLOG.read_text(errors='replace').splitlines() if CLOG.exists() else []
    first = next((i for i, l in enumerate(lines) if ' watch start;' in l), 0)   # chain jobs announced before the watchdog (11749795) are ignored
    for l in lines[first:]:
        m = re.search(r'(?:first|next) chain job (\d+)(?: \(round (\d+), phase (\S+)\))?', l)
        if m: best = dict(job=m.group(1), round=m.group(2), phase=m.group(3))
        m = re.search(r'watch resubmitted chain job (\d+) round=(\S+) phase=(\S+) stall=(\S+)', l)
        if m: best = dict(job=m.group(1), round=m.group(2), phase=m.group(3), stall=m.group(4))
    return best


def chain_env_of(job):
    """ROUND/PHASE/STALL the job was started with (its own 'start' line)."""
    for l in reversed(CLOG.read_text(errors='replace').splitlines()):
        m = re.search(rf'job={job} round=(\d+) start .* phase_in=(\S+) stall=(\d+)', l)
        if m: return m.group(1), ('' if m.group(2) == 'none' else m.group(2)), m.group(3)
    return None


def main():
    st = json.loads(STATE.read_text()) if STATE.exists() else dict(gate_jobs=[], gate_kills=0, chain_kills=0)
    save = lambda: STATE.write_text(json.dumps(st, indent=1))
    prev_gates = [x for x in sys.argv[1:] if x.isdigit()]
    for g in prev_gates:
        if g not in st['gate_jobs']: st['gate_jobs'].append(g)
    note('start; known gate jobs', st['gate_jobs'], 'kills so far gate/chain', st['gate_kills'], st['chain_kills']); save()
    t0 = time.time()
    while time.time() - t0 < MAX_H * 3600:
        g = gate_status()
        if g == 'FAIL' or (ROOT / 'HARD_CHECK_FAILED').exists(): note('STOP: D12-1 gate FAIL / HARD_CHECK_FAILED - nothing else runs'); return 3
        if g is None:                                                   # ---------------- gate phase
            q = queued('b2c_fitb3bgate')
            if q is None: time.sleep(POLL); continue                    # squeue hiccup
            if q: time.sleep(POLL); continue
            last = st['gate_jobs'][-1] if st['gate_jobs'] else None
            e = ended(last) if last else ('NONE', '')
            if last and e is None: time.sleep(POLL); continue
            if last and not killed(e) and e[0] != 'NONE':
                if e[0] == 'COMPLETED': time.sleep(POLL); g2 = gate_status()
                else: g2 = None
                if g2 is None: note(f'STOP: gate job {last} ended {e} without gate_v2.json (not an epilog kill)'); return 3
                continue
            if last and killed(e):
                if st['gate_kills'] >= KILL_CAP: note(f'STOP: gate killed {st["gate_kills"]} times (cap {KILL_CAP})'); return 4
                st['gate_kills'] += 1; note(f'gate job {last} killed by signal 9 ({e}); resubmit {st["gate_kills"]}/{KILL_CAP}')
            j = submit(GATE_SB)
            if j: st['gate_jobs'].append(j); note('gate job submitted', j); save()
            time.sleep(POLL); continue
        # ---------------------------------------------------------------- chain phase (gate PASS)
        nx = item_next()
        if nx is None: time.sleep(POLL); continue
        if nx.get('next') == 'done': note('2-1 done (report written)'); return 0
        qc, qs = queued('b2c_fitb3chain'), queued('b2c_fitb3start')
        if qc is None or qs is None: time.sleep(POLL); continue
        if qc or qs: time.sleep(POLL); continue
        if nx.get('next') == 'analyze' and 'analyze job:' in (CLOG.read_text() if CLOG.exists() else ''):
            note('GPU work complete; analyze job submitted by the chain - watchdog ends'); return 0
        lc = last_chain_job()
        if lc is None:                                                  # no chain job yet: start it
            j = submit(CHAIN_SB)
            if j: note(f'watch resubmitted chain job {j} round=1 phase=none stall=0 (first chain job)')
            time.sleep(POLL); continue
        e = ended(lc['job'])
        if e is None: time.sleep(POLL); continue
        if killed(e):
            if st['chain_kills'] >= KILL_CAP: note(f'STOP: chain killed {st["chain_kills"]} times (cap {KILL_CAP})'); return 4
            env = chain_env_of(lc['job']) or (lc.get('round') or '1', lc.get('phase') or '', lc.get('stall') or '0')
            st['chain_kills'] += 1; save()
            j = submit(CHAIN_SB, f'ROUND={env[0]},PHASE={env[1]},STALL={env[2]}')
            if j: note(f'watch resubmitted chain job {j} round={env[0]} phase={env[1] or "none"} stall={env[2]} (previous {lc["job"]} killed {e}, kill {st["chain_kills"]}/{KILL_CAP})')
            time.sleep(POLL); continue
        note(f'STOP: last chain job {lc["job"]} ended {e} with no successor queued (chain stop rule; see log above)'); return 3
    note('STOP: watchdog time limit reached; resubmit stage9_b2_fitb_v3b_watch.sbatch to continue (state kept)'); return 5


if __name__ == '__main__':
    sys.exit(main())
