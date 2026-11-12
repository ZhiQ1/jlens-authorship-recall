"""Item 2-1 v4 watchdog (CPU on short, 2026-11-12; D12-5). One GPU job at a time, 45 min, no --time-min, killguard --exclude.
 gate phase : b2_fitb_d125/summary/gate_v2.json missing -> submit stage9_b2_fitb_v4_gate.sbatch; sacct 0:9 (epilog kill) -> resubmit,
              max 3 kills; gate FAIL or any other end without a result -> STOP (2-1 stays stopped).
 chain phase: gate PASS (stage9_b2_fitb_v4.py verify) -> stage9_b2_fitb_v4_chain.sbatch (Fit B 67-100 frozen command, then holdout +
              168 read units, then analysis). Chain job killed with 0:9 -> resubmit with its ROUND/PHASE/STALL (max 3 kills); HANDOFF
              (GPU submit cap) -> submit the announced round; any other end without successor -> STOP (chain stop rule).
Log: b2_fitb_d125/chain_v4.log. State: b2_fitb_d125/watch_v4_state.json.
"""
import importlib.util, json, re, sys, time
from pathlib import Path

D = Path.home() / 'jlens_work/09_stage9'


def load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


W = load('watch_v3b', D / 'stage9_b2_fitb_v3b_watch.py')     # sh, queued, ended, killed, submit (killguard), kg
V4 = load('fitb_v4', D / 'stage9_b2_fitb_v4.py')
ROOT = V4.ROOT4; W.CLOG = ROOT / 'chain_v4.log'; STATE = ROOT / 'watch_v4_state.json'
GATE_SB, CHAIN_SB, CAP, POLL = D / 'stage9_b2_fitb_v4_gate.sbatch', D / 'stage9_b2_fitb_v4_chain.sbatch', 3, 120


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    st = json.loads(STATE.read_text()) if STATE.exists() else dict(gate_jobs=[], gate_kills=0, chain_kills=0)
    save = lambda: STATE.write_text(json.dumps(st, indent=1))
    W.note('start (v4); state', st); save(); t0 = time.time()
    while time.time() - t0 < 46 * 3600:
        try:
            for m in W.kg.refresh_pending(): W.note('killguard refresh:', m)
        except Exception as e: W.note('killguard refresh warning', repr(e))
        ok, why = V4.record_ok()
        if not ok: W.note('STOP:', why); return 3
        gp = ROOT / 'summary/gate_v2.json'
        if not gp.exists():                                                         # ---- gate phase
            q = W.queued('b2c_fitb4gate')
            if q is None or q: time.sleep(POLL); continue
            last = st['gate_jobs'][-1] if st['gate_jobs'] else None
            e = W.ended(last) if last else None
            if last and e is None: time.sleep(POLL); continue
            if gp.exists(): continue
            if last and not W.killed(e): W.note(f'STOP: gate v4 job {last} ended {e} without a result'); return 3
            if last:
                if st['gate_kills'] >= CAP: W.note(f'STOP: gate v4 killed {CAP} times'); return 4
                st['gate_kills'] += 1; W.note(f'gate v4 job {last} killed {e}; resubmit {st["gate_kills"]}/{CAP}')
            j = W.submit(GATE_SB, name='b2c_fitb4gate', unit='2-1:gate_v4')
            if j: st['gate_jobs'].append(j); save(); W.note('gate v4 job submitted', j)
            time.sleep(POLL); continue
        g = json.loads(gp.read_text()).get('status')
        if g != 'PASS': W.note('STOP: gate v4 status', g, '- 2-1 stays stopped'); return 3
        rc, out, _ = W.sh([W.PY, str(D / 'stage9_b2_fitb_v4.py'), 'status'], t=300)  # ---- chain phase
        try: nx = json.loads(out.splitlines()[-1])
        except Exception: time.sleep(POLL); continue
        if nx['next'] == 'done': W.note('2-1 done (report written)'); return 0
        if nx['next'] == 'failed': W.note('STOP: status failed:', nx.get('reason')); return 3
        if nx['next'] == 'analyze' and 'analyze job:' in W.CLOG.read_text(): W.note('GPU work complete; analyze submitted by the chain'); return 0
        q = W.queued('b2c_fitb4chain')
        if q is None or q: time.sleep(POLL); continue
        lines = W.CLOG.read_text(errors='replace').splitlines()
        lj = None
        for l in lines:
            m = re.search(r'(?:next chain job|watch submitted chain job) (\d+)', l)
            if m: lj = m.group(1)
        if lj is None:
            j = W.submit(CHAIN_SB, name='b2c_fitb4chain', unit='2-1:v4chain:first')
            if j: W.note(f'watch submitted chain job {j} (first)')
            time.sleep(POLL); continue
        e = W.ended(lj)
        if e is None: time.sleep(POLL); continue
        env, kind = None, None
        for l in reversed(lines):
            m = re.search(rf'job={lj} round=\d+ HANDOFF round=(\d+) phase=(\S+) stall=(\d+)', l)
            if m: env, kind = m.groups(), 'handoff'; break
        if env is None:
            for l in reversed(lines):
                m = re.search(rf'job={lj} round=(\d+) start .* phase_in=(\S+) stall=(\d+)', l)
                if m: env = (m.group(1), '' if m.group(2) == 'none' else m.group(2), m.group(3)); break
        if W.killed(e):
            if st['chain_kills'] >= CAP: W.note(f'STOP: chain killed {CAP} times'); return 4
            st['chain_kills'] += 1; save(); kind = 'kill'
        elif kind != 'handoff' or e[0] != 'COMPLETED':
            W.note(f'STOP: chain job {lj} ended {e} with no successor (chain stop rule; see log)'); return 3
        env = env or ('1', '', '0')
        j = W.submit(CHAIN_SB, f'ROUND={env[0]},PHASE={env[1]},STALL={env[2]}', name='b2c_fitb4chain', unit=f'2-1:v4chain:{env[1]}:round{env[0]}')
        if j: W.note(f'watch submitted chain job {j} round={env[0]} phase={env[1] or "none"} stall={env[2]} (after {lj}: {kind} {e})')
        time.sleep(POLL)
    W.note('STOP: watchdog time limit; resubmit stage9_b2_fitb_v4_watch.sbatch (state kept)'); return 5


if __name__ == '__main__':
    sys.exit(main())
