"""Item 2-1 decider + continuation watchdog (CPU, 2026-11-09), applies the USER'S RULE of 2026-11-09 without asking:

 1. Fit B prompt 66 re-run with the ORIGINAL code (stage9_b2_fitb_orig66.sbatch, job id given as argument): wait for it; sacct 0:9
    (node-epilog kill) -> resubmit, max 3; any other end without b2_fitb_orig66/orig66_result.json -> STOP (exit 3).
 2. x = max||J||/sqrt(d) from the original code (fp32, as jlens.fit logs it).
    A  |x - 4.378043| <= 0.0049 (new-code gate value): hardware/environment -> WARN. Write the locked deviation record
       381_stage13/config/prereg_addendum12_deviations_D12-4.json (+ .sha256, mode 444), set up the new root (stage9_b2_fitb_v3c.py setup)
       and run the continuation watchdog (chain stage9_b2_fitb_v3c_chain.sbatch; one GPU job at a time; 0:9 kills resubmitted, max 6).
    B  |x - 4.367| <= 0.004867 (original log value and threshold): the original code reproduces the log, the new gate code does not ->
       2-1 stays STOPPED per D12-1; outcome written to 381_stage13/reports/b2_fitb_D12-1_outcome.{json,md} for the limitations.
    neither -> STOP, outcome written, nothing else runs (rule does not cover it).
Log: 381_stage13/b2_fitb_orig66/decide.log (+ b2_fitb_d124/chain_v3c.log for the continuation).
"""
import hashlib, importlib.util, json, os, re, subprocess, sys, time
from datetime import datetime
from pathlib import Path

D = Path.home() / 'jlens_work/09_stage9'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
O66 = R13 / 'b2_fitb_orig66'; RES = O66 / 'orig66_result.json'; DLOG = O66 / 'decide.log'; DSTATE = O66 / 'decide_state.json'
ORIG_SB = D / 'stage9_b2_fitb_orig66.sbatch'
NEW, REF, THR_A, THR_REF = 4.378043340693925, 4.367, 0.0049, 0.004867
OLD = R13 / 'b2_fitb'; REC = R13 / 'config/prereg_addendum12_deviations_D12-4.json'
POLL = 120


def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


W = load('watch_v3b', D / 'stage9_b2_fitb_v3b_watch.py')       # helpers: sh, queued, ended, killed, submit
C = load('fitb_v3c', D / 'stage9_b2_fitb_v3c.py')


def note(*x):
    line = f'{datetime.now().isoformat(timespec="seconds")} decide {" ".join(str(v) for v in x)}'; print(line, flush=True)
    O66.mkdir(parents=True, exist_ok=True)
    with open(DLOG, 'a') as f: f.write(line + '\n')


def wait_rerun(first_job):
    st = json.loads(DSTATE.read_text()) if DSTATE.exists() else dict(jobs=[first_job] if first_job else [], kills=0)
    save = lambda: DSTATE.write_text(json.dumps(st, indent=1))
    O66.mkdir(parents=True, exist_ok=True); save()
    while not RES.exists():
        q = W.queued('b2c_orig66')
        if q is None or q: time.sleep(POLL); continue
        last = st['jobs'][-1] if st['jobs'] else None
        e = W.ended(last) if last else None
        if last and e is None: time.sleep(POLL); continue
        if RES.exists(): break
        if last and not W.killed(e): note(f'STOP: rerun job {last} ended {e} without a result'); return None
        if last:
            if st['kills'] >= 3: note('STOP: rerun killed 3 times (cap)'); return None
            st['kills'] += 1; note(f'rerun job {last} killed {e} (epilog); resubmit {st["kills"]}/3')
        j = W.submit(ORIG_SB)
        if j: st['jobs'].append(j); save(); note('rerun job submitted', j)
        time.sleep(POLL)
    return json.loads(RES.read_text())


def outcome(r, branch, text):
    o = dict(item='2-1', branch=branch, rerun=r, new_code_gate=dict(value=NEW, job='11753858', gate_json=str(OLD / 'summary/gate.json'),
             gate_json_sha256=C.sha(OLD / 'summary/gate.json')), reference_log=REF, threshold=THR_REF, text=text,
             at=datetime.now().isoformat(timespec='seconds'))
    (R13 / 'reports').mkdir(exist_ok=True)
    (R13 / 'reports/b2_fitb_D12-1_outcome.json').write_text(json.dumps(o, indent=1, default=str))
    (R13 / 'reports/b2_fitb_D12-1_outcome.md').write_text(f'# Item 2-1 D12-1 gate outcome ({branch})\n\n{text}\n')


def write_record(r, cont):
    x = r['max_norm_over_sqrt_d_fp32']
    rec = {
        'title': 'Addendum 12 deviation record D12-4 (item 2-1 Fit B gate tolerance): WARN and continue. Decided AFTER seeing the data.',
        'decision': 'WARN_continue',
        'applies_to': 'D12-1 part (b) of prereg_addendum12_deviations.json (that file and its sha256 are unchanged)',
        'approved_by_user': 'user decision relayed 2026-11-09 (rule: if the original code also gives ~4.378, record WARN and continue)',
        'decided_after_seeing_data': True,
        'gate_result': dict(job='11753858', check='gate_prompt66_max_norm_over_sqrt_d', value=NEW, reference_log=REF,
                            abs_diff=abs(NEW - REF), threshold=THR_REF, status='FAIL',
                            other_checks='max_d_mean 0.108080 vs 0.108 PASS; seq_len 128 == 128 PASS; part (a) Fit A k=3 bitwise PASS',
                            files={str(OLD / f): C.sha(OLD / f) for f in ('summary/gate.json', 'summary/gate_v2.json', 'HARD_CHECK_FAILED')}),
        'original_code_rerun': dict(job=r.get('job'), host=r.get('host'), gpu=r.get('gpu'), max_norm_over_sqrt_d_fp32=x,
                                    max_norm_over_sqrt_d_f64=r.get('max_norm_over_sqrt_d_f64'),
                                    max_d_mean_original_definition=r.get('max_d_mean_original_definition'),
                                    seq_len=r.get('seq_len'), n_valid=r.get('n_valid'), abs_diff_vs_new_code=abs(x - NEW),
                                    abs_diff_vs_log=abs(x - REF), result_file=str(RES), result_sha256=C.sha(RES)),
        'reason': ('The original frozen Fit B code, rerun now on A100-80GB with the unchanged environment, gives the same value as the new '
                   'gate code (within 0.0049), so the 0.011 difference from the 2026-10-21 log comes from hardware/environment, not from the '
                   'code path. The pre-registered threshold 0.5*0.001 + 1e-3*4.367 = 0.004867 is below the bf16 resolution at this magnitude '
                   '(bf16 spacing in [4, 8) is 2^-5 = 0.03125), which violates the CLAUDE.md tolerance rule (tolerances must allow several '
                   'bf16 units; misses are WARN, not stops). This handling was decided after seeing the data.'),
        'handling': ('Gate recorded as WARN (PASS-with-WARN). The D12-1 gate code and its checks are unchanged; the failed gate outputs stay in '
                     f'{OLD}. 2-1 continues with the unchanged v1/v2 code in the new root {C.ROOT2} (stage9_b2_fitb_v3c.py), whose gate files '
                     'state PASS with warn=D12-4 and point to the original FAIL files.'),
        'continuation': cont,
        'unchanged': 'all other pre-registered checks, prompts, layers, loaders, analysis of item 2-1',
        'written': datetime.now().isoformat(timespec='seconds'),
    }
    if REC.exists(): raise SystemExit(f'{REC} exists: not overwritten')
    REC.write_text(json.dumps(rec, indent=1, default=str)); os.chmod(REC, 0o444)
    h = C.sha(REC); s = REC.with_name(REC.name + '.sha256'); s.write_text(f'{h}  {REC.name}\n'); os.chmod(s, 0o444)
    note('record written + locked', REC, h); return h


def continuation():
    """continuation watchdog: chain phase only (gate already WARN-PASS via the verified record)."""
    W.CLOG = C.ROOT2 / 'chain_v3c.log'; W.STATE = C.ROOT2 / 'watch_v3c_state.json'
    st = json.loads(W.STATE.read_text()) if W.STATE.exists() else dict(chain_kills=0); save = lambda: W.STATE.write_text(json.dumps(st))
    W.note('start (v3c continuation)'); t0 = time.time()
    def last_job():
        best = None
        for l in (W.CLOG.read_text(errors='replace').splitlines() if W.CLOG.exists() else []):
            m = re.search(r'(?:next chain job|watch submitted chain job) (\d+)', l)
            if m: best = m.group(1)
        return best
    def env_of(job):
        lines = W.CLOG.read_text(errors='replace').splitlines()
        for l in reversed(lines):
            m = re.search(rf'job={job} round=\d+ HANDOFF round=(\d+) phase=(\S+) stall=(\d+)', l)
            if m: return 'handoff', m.groups()
        for l in reversed(lines):
            m = re.search(rf'job={job} round=(\d+) start .* phase_in=(\S+) stall=(\d+)', l)
            if m: return 'start', (m.group(1), '' if m.group(2) == 'none' else m.group(2), m.group(3))
        return None, None
    while time.time() - t0 < 46 * 3600:
        ok, why = C.verify()
        if not ok: W.note('STOP:', why); return 3
        rc, out, _ = W.sh([W.PY, str(D / 'stage9_b2_fitb_v3c.py'), 'status'], t=300)
        try: nx = json.loads(out.splitlines()[-1])
        except Exception: time.sleep(POLL); continue
        if nx['next'] == 'done': W.note('2-1 done (report written)'); return 0
        if nx['next'] == 'analyze' and 'analyze job:' in W.CLOG.read_text(): W.note('GPU work complete; analyze submitted by the chain'); return 0
        q = W.queued('b2c_fitb3cchain')
        if q is None or q: time.sleep(POLL); continue
        lj = last_job()
        if lj is None:
            j = W.submit(D / 'stage9_b2_fitb_v3c_chain.sbatch')
            if j: W.note(f'watch submitted chain job {j} (first)')
            time.sleep(POLL); continue
        e = W.ended(lj)
        if e is None: time.sleep(POLL); continue
        kind, env = env_of(lj)
        if W.killed(e):
            if st['chain_kills'] >= 6: W.note('STOP: chain killed 6 times (cap)'); return 4
            st['chain_kills'] += 1; save(); kind = 'kill'
        elif not (e[0] == 'COMPLETED' and kind == 'handoff'):
            W.note(f'STOP: chain job {lj} ended {e} with no successor (chain stop rule; see log)'); return 3
        if env is None: env = ('1', '', '0')
        j = W.submit(D / 'stage9_b2_fitb_v3c_chain.sbatch', f'ROUND={env[0]},PHASE={env[1]},STALL={env[2]}')
        if j: W.note(f'watch submitted chain job {j} round={env[0]} phase={env[1] or "none"} stall={env[2]} (after {lj}: {kind} {e})')
        time.sleep(POLL)
    W.note('STOP: watchdog time limit; resubmit stage9_b2_fitb_d124_decide.sbatch (state kept)'); return 5


def main():
    first = next((a for a in sys.argv[1:] if a.isdigit()), None)
    if REC.exists():
        ok, why = C.verify(); note('record exists:', why)
        return continuation() if ok else 3
    r = wait_rerun(first)
    if r is None: outcome(None, 'STOPPED', 'Original-code rerun of prompt 66 did not produce a result; 2-1 stays stopped.'); return 3
    x = r['max_norm_over_sqrt_d_fp32']
    note('RERUN', json.dumps({k: r.get(k) for k in ('max_norm_over_sqrt_d_fp32', 'max_norm_over_sqrt_d_f64', 'max_d_mean_original_definition', 'seq_len', 'n_valid', 'job', 'host')}))
    if abs(x - NEW) <= THR_A:
        note(f'BRANCH A: original code gives {x:.9f}, |diff vs new code| {abs(x - NEW):.2e} <= {THR_A} -> WARN, record, continue')
        cont = C.setup(); write_record(r, cont)
        ok, why = C.verify(); note('verify:', why)
        if not ok: return 3
        outcome(r, 'A_WARN_continue', f'Prompt 66 re-run with the original frozen Fit B code gives max||J||/sqrt(d) = {x:.6f} (new gate code {NEW:.6f}; '
                f'2026-10-21 log {REF}). The difference from the log is hardware/environment, below the bf16 resolution (0.031) at this '
                f'magnitude; the gate is recorded as WARN under D12-4 (decided after seeing the data) and 2-1 continues.')
        return continuation()
    if abs(x - REF) <= THR_REF:
        note(f'BRANCH B: original code gives {x:.9f} ~ log {REF}: 2-1 stays STOPPED per D12-1')
        outcome(r, 'B_stopped', f'Prompt 66 re-run with the original frozen Fit B code reproduces the 2026-10-21 log ({x:.6f} vs {REF}), '
                f'but the D12-1 gate code gives {NEW:.6f} (|diff| {abs(NEW - REF):.4f} > threshold {THR_REF}). Per D12-1 item 2-1 is stopped: '
                'Fit B stays at 66/100; no Fit A vs Fit B holdout comparison and no Fit B Stage 10 readout.')
        return 0
    note(f'STOP: original code gives {x:.9f}: neither ~{NEW:.6f} nor ~{REF} - rule does not cover it')
    outcome(r, 'neither_stopped', f'Original-code rerun gives {x:.6f}: neither the new gate value {NEW:.6f} nor the log {REF}; 2-1 stays stopped pending a decision.')
    return 3


if __name__ == '__main__':
    sys.exit(main())
