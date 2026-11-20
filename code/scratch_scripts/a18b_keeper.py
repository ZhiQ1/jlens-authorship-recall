#!/usr/bin/env python
"""Addendum 18b queue keeper (2026-11-17). Runs as a CPU job on 'short' (a18b_keeper.sbatch), polls every 5 min, standard
library only (+ numpy for reading unit metadata). Applies the written workflow rule of addendum 18b lock amendment 3:

  order      items 4 -> 1 -> 6 -> 5 -> 2 -> 3 (then '2s' = item 2 step-2 sensitivity, only if item 2's measured GPU time x 11/6 <= 5 h)
  per item   needs tiny PASS (a18b_config/tiny_pass_item<k> or the PASS line in its tiny log) -> 1-shard job (shard 0) ->
             projection = 24 x t(shard 0) [+ item-4 reference means] + 4 min load per job; if > 5 GPU-h the shard set is cut to
             n = floor((5 h - fixed) / t) shards (never below 12 shards = 300 papers; if even 12 do not fit: item STOPPED, review)
             and the change is logged in PROGRESS.md -> worker jobs (a18b_gpu.sbatch, SHARDS = chunks sized to ~34 min of work)
             -> when every unit of the item's shard set exists: CPU analysis job (a18b_cpu.sbatch CMD=analyze) -> daily-log line.
  GPU cap    at most 4 of the user's GPU jobs pending+running at any time (all job names; the user's own jobs count too).
  failures   worker exit 0:9 (epilog SIGKILL) -> units go back to the pool (cap 3 kills per item); any other non-zero exit = code
             crash -> that item is STOPPED (other items continue), line in review_queue.md. Checks inside jobs are WARN only.
  sbatch     errors: check squeue by comment tag before retrying; killguard exclude/record on every GPU submission.
State: a18b_config/keeper_state.json (atomic). Log: logs/a18b/keeper.log. Commands: run | once | status
"""
import json, os, subprocess, sys, time
from pathlib import Path

H = Path.home() / 'jlens_work'; D = H / '13_stage13'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
CFG = R13 / 'a18b_config'; LOGD = R13 / 'logs/a18b'; STATE = CFG / 'keeper_state.json'
PY = str(Path.home() / 'conda-envs/jlens/bin/python'); KG = str(H / 'killguard.py')
ORDER = ['4', '1', '6', '5', '2', '3', '2s']; CAP_H = 5.0; MIN_SHARDS = 12; NSH = 24; LOAD_MIN = 4.0; GPU_CAP = 4; CHUNK_MIN = 34.0
ME = 'zhang.zhiqi2'


def now(): return time.strftime('%Y-%m-%d %H:%M:%S')
def log(*a):
    s = now() + ' ' + ' '.join(str(x) for x in a); print(s, flush=True)
    with open(LOGD / 'keeper.log', 'a') as f: f.write(s + '\n')


def sh(cmd, tries=3, timeout=90):
    out = ''
    for i in range(tries):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0: return r.stdout
            out = r.stdout + r.stderr
        except Exception as e: out = repr(e)
        time.sleep(10)
    raise RuntimeError(f'{cmd[0]} failed: {out[:300]}')


def progress(msg):
    try: subprocess.run([PY, str(D / 'a18b_progress.py'), msg], timeout=60)
    except Exception as e: log('progress write failed', e)


def daily(msg):
    try:
        (H / 'daily_log_cpu').mkdir(exist_ok=True)
        with open(H / 'daily_log_cpu' / f'{time.strftime("%Y-%m-%d")}.txt', 'a') as f: f.write(msg.rstrip() + '\n')
    except Exception as e: log('daily log failed', e)


def review(msg):
    try:
        with open(H / 'review_queue.md', 'a') as f: f.write(f'- {now()} [a18b keeper] {msg}\n')
    except Exception: pass


def load_state():
    if STATE.exists(): return json.loads(STATE.read_text())
    return dict(items={k: dict(phase='wait_tiny', jobs={}, nshards=NSH, kills=0, gpu_s=0.0, analysis=None) for k in ORDER}, created=now())


def save_state(S):
    tmp = STATE.with_suffix('.tmp'); tmp.write_text(json.dumps(S, indent=1)); os.replace(tmp, STATE)


def raw(item): return R13 / ('raw/a18b_item2_step2' if item == '2s' else f'raw/a18b_item{item}')
def unit_file(item, k): return raw(item) / 'main' / f'shard_{k:03d}.npz'
def script_item(item): return '2' if item == '2s' else item


def unit_seconds(f):
    try:
        import numpy as np
        return float(json.loads(str(np.load(f)['meta'])).get('seconds', 0))
    except Exception: return None


def tiny_ok(item):
    it = script_item(item)
    if (CFG / f'tiny_pass_item{it}').exists(): return True
    for f in LOGD.glob(f'cpu_a18b_t{it}_*.log'):
        try:
            if f'A18B ITEM{it} TINY PASS' in f.read_text(errors='ignore'): return True
        except Exception: pass
    return False


def my_gpu_jobs():
    """all of the user's GPU jobs (pending + running): {jobid: (name, state, comment)}"""
    out = sh(['squeue', '-u', ME, '-h', '-o', '%i|%j|%T|%b|%k|%P'])
    J = {}
    for line in out.strip().splitlines():
        p = line.split('|')
        if len(p) < 6: continue
        if 'gpu' in p[3] or p[5].startswith('gpu'): J[p[0]] = (p[1], p[2], p[4])
    return J


def sacct_state(jid):
    try:
        out = sh(['sacct', '-n', '-X', '-j', str(jid), '-o', 'State,ExitCode,ElapsedRaw', '-P'])
        line = out.strip().splitlines()[0]; st, ec, el = line.split('|'); return st.split()[0], ec, int(el or 0)
    except Exception: return None, None, 0


def submit_gpu(item, shards, S):
    tag = f'a18b_{item}_{shards}'; name = f'a18b_i{item}'
    ex = ''
    try:
        ex = sh([PY, KG, 'exclude', '--name', name, '--minutes', '45']).strip().splitlines()[-1]
    except Exception as e: log('killguard exclude failed', e)
    if ex == 'DEFER': log('killguard DEFER for', tag); return None
    env = f'ALL,ITEM={script_item(item)},SHARDS={shards}' + (',A18B_WIN2=step2' if item == '2s' else '')
    cmd = ['sbatch', '--parsable'] + ([ex] if ex.startswith('--exclude') else []) + ['-J', name, f'--comment={tag}', f'--export={env}', str(D / 'a18b_gpu.sbatch')]
    for i in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and r.stdout.strip():
                jid = r.stdout.strip().split(';')[0]; break
            log('sbatch error', r.stderr.strip()[:200])
        except Exception as e: log('sbatch exception', e)
        time.sleep(30)
        q = sh(['squeue', '-u', ME, '-h', '-o', '%i|%k'])
        hit = [l.split('|')[0] for l in q.splitlines() if l.endswith('|' + tag)]
        if hit: jid = hit[0]; break
    else:
        return None
    try: sh([PY, KG, 'record', '--jid', jid, '--name', name, '--minutes', '45', '--orch', 'a18b'])
    except Exception: pass
    S['items'][item]['jobs'][jid] = dict(shards=shards, submitted=now())
    log('submitted', item, shards, jid); return jid


def parse(shards):
    out = []
    for p in str(shards).split(','):
        if '-' in p: a, b = p.split('-'); out += list(range(int(a), int(b) + 1))
        elif p != '': out.append(int(p))
    return out


def step(S):
    J = my_gpu_jobs(); n_gpu = len(J)
    for item in ORDER:
        st = S['items'][item]
        if st['phase'] in ('done', 'stopped', 'skipped'): continue
        # job bookkeeping
        inflight = set()
        for jid, info in list(st['jobs'].items()):
            if jid in J: inflight |= set(parse(info['shards'])); continue
            if info.get('final'): continue
            state, ec, el = sacct_state(jid)
            if state is None or state in ('PENDING', 'RUNNING', 'REQUEUED'): inflight |= set(parse(info['shards'])); continue
            info['final'] = state; info['exit'] = ec; info['elapsed_s'] = el; st['gpu_s'] += el
            log('job end', item, jid, state, ec, el)
            if state != 'COMPLETED':
                if ec and ec.endswith(':9') or state in ('CANCELLED', 'NODE_FAIL', 'PREEMPTED', 'TIMEOUT'):
                    st['kills'] += 1; log('kill/timeout -> units back to the pool', item, jid, st['kills'])
                    if st['kills'] > 3: st['phase'] = 'stopped'; review(f'item {item}: more than 3 killed/timeout jobs, stopped'); progress(f'keeper: item {item} STOPPED after >3 kills/timeouts')
                else:
                    st['phase'] = 'stopped'; review(f'item {item}: worker {jid} {state} {ec} (code crash?) - item stopped, other items continue; see logs/a18b/gpu_a18b_i{item}_{jid}.log')
                    progress(f'keeper: item {item} STOPPED, worker {jid} {state} exit {ec} (crash); review_queue.md')
        if st['phase'] == 'stopped': continue
        if st['phase'] == 'wait_tiny' and st['jobs']: st['phase'] = 'measure'
        if st['phase'] == 'wait_tiny':
            if item == '2s':
                s2 = S['items']['2']
                if s2['phase'] != 'done': continue
                proj = s2['gpu_s'] / 3600 * 11 / 6
                if proj > CAP_H: st['phase'] = 'skipped'; progress(f'keeper: item 2 step-2 sensitivity NOT run (projected {proj:.2f} GPU-h > 5)'); continue
                st['phase'] = 'measure'; progress(f'keeper: item 2 step-2 sensitivity starts (projected {proj:.2f} GPU-h)')
            elif tiny_ok(item):
                prev = ORDER[:ORDER.index(item)]
                if any(S['items'][k]['phase'] in ('wait_tiny', 'measure') for k in prev if k != '2s'): continue   # strict queue order
                st['phase'] = 'measure'; log('tiny ok', item)
            else: continue
        if st['phase'] == 'measure':
            f0 = unit_file(item, 0)
            if f0.exists():
                t = unit_seconds(f0) or 600.0; fixed = 0.0
                if item == '4': fixed = sum(unit_seconds(raw('4') / 'refmean' / f'shard_{k:03d}.npz') or 0 for k in range(NSH))
                njobs = max(1, round(NSH * t / 60 / CHUNK_MIN))
                proj = (NSH * t + fixed) / 3600 + njobs * LOAD_MIN / 60
                n = NSH
                if proj > CAP_H:
                    n = int((CAP_H - fixed / 3600 - njobs * LOAD_MIN / 60) * 3600 // t)
                    if n < MIN_SHARDS:
                        st['phase'] = 'stopped'; review(f'item {item}: projected {proj:.2f} GPU-h, even 300 papers exceed 5 h -> ask the user'); progress(f'keeper: item {item} STOPPED, projected {proj:.2f} GPU-h even at 300 papers'); continue
                    progress(f'keeper: item {item} 1-shard t={t:.0f}s projects {proj:.2f} GPU-h > 5 -> subsample cut to {n} shards = {25 * n} papers (shards 0..{n - 1})')
                proj_n = (n * t + fixed) / 3600 + max(1, round(n * t / 60 / CHUNK_MIN)) * LOAD_MIN / 60
                st['nshards'] = n; st['t_shard'] = t; st['projected_h_24'] = proj; st['projected_h'] = proj_n; st['phase'] = 'run'
                progress(f'keeper: item {item} 1-shard measured {t:.0f} s/shard (25 papers); projected {proj_n:.2f} GPU-h for {n} shards ({25 * n} papers)')
            elif 0 not in inflight and n_gpu < GPU_CAP:          # (fix 15:55: also after a killed measurement job)
                if submit_gpu(item, '0', S): n_gpu += 1
                continue
            else: continue
        if st['phase'] == 'run':
            todo = [k for k in range(st['nshards']) if not unit_file(item, k).exists()]
            free = [k for k in todo if k not in inflight]
            per = max(1, int(CHUNK_MIN * 60 // max(st.get('t_shard', 600), 1)))
            while free and n_gpu < GPU_CAP:
                ch = free[:per]; free = free[per:]
                if submit_gpu(item, ','.join(map(str, ch)), S): n_gpu += 1
                else: break
            if not todo and not inflight:
                st['phase'] = 'analysis'
                jid = sh(['sbatch', '--parsable', '-J', f'a18b_an{item}', f'--export=ALL,ITEM={script_item(item)},CMD=analyze' + (',A18B_WIN2=step2' if item == '2s' else ''),
                          str(D / 'a18b_cpu.sbatch')]).strip().split(';')[0]
                st['analysis'] = jid; progress(f'keeper: item {item} all {st["nshards"]} shards done; measured GPU time {st["gpu_s"] / 3600:.2f} h (sum of worker elapsed); analysis job {jid}')
        if st['phase'] == 'analysis':
            state, ec, el = sacct_state(st['analysis'])
            if state == 'COMPLETED':
                st['phase'] = 'done'; summ = R13 / (f'summary_a18b_item2_step2' if item == '2s' else f'summary_a18b_item{item}')
                daily(f'addendum 18b item {item} analysis — {summ} ({25 * st["nshards"]} papers, {st["nshards"]} shards, {st["gpu_s"] / 3600:.2f} GPU-h)')
                progress(f'keeper: item {item} analysis {st["analysis"]} done -> {summ}')
            elif state and state not in ('PENDING', 'RUNNING'):
                st['phase'] = 'stopped'; review(f'item {item}: analysis job {st["analysis"]} {state} {ec}'); progress(f'keeper: item {item} analysis {st["analysis"]} {state} {ec} (review)')
    return all(S['items'][k]['phase'] in ('done', 'stopped', 'skipped') for k in ORDER)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'once'
    S = load_state()
    if cmd == 'status': print(json.dumps(S, indent=1)); return
    if cmd == 'adopt':                                     # adopt an already submitted job: adopt ITEM JOBID SHARDS
        it, jid, shards = sys.argv[2:5]; S['items'][it]['jobs'][jid] = dict(shards=shards, submitted='adopted ' + now()); save_state(S); print('adopted'); return
    t_end = time.time() + float(os.environ.get('KEEPER_HOURS', '46')) * 3600
    while True:
        try: fin = step(S)
        except Exception as e:
            import traceback; log('STEP ERROR (keeper continues)', repr(e), traceback.format_exc()[-800:]); fin = False
        save_state(S)
        if fin or cmd == 'once': log('keeper', 'finished' if fin else 'one step'); break
        if time.time() > t_end:
            log('keeper time up: resubmitting itself')
            sh(['sbatch', '--parsable', str(D / 'a18b_keeper.sbatch')]); break
        time.sleep(300)


if __name__ == '__main__':
    main()
