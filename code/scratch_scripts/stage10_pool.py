"""Stage 10 queue pool (CPU dispatcher, runs inside stage10_pool.sbatch).

Keeps as many A100-80GB jobs queued as the per-partition QOS allows (gpu: 8 submit, gpu-short: 8 submit, 2 h), each
job owning a disjoint chunk (track, condition, shards). Since 2026-10-25 the pool does all the work (no s10_w0/w1): main round first
(true first, so the main analysis can start early), then the extension (public+logit at L50-55,57-61). It also
submits the main analyses (MODE=main once 'true' is complete, MODE=title once all 7 conditions are).

Rules (written down so the pool never has to judge):
  - a pool job that ends FAILED/OUT_OF_MEMORY/NODE_FAIL, or any pool job stuck in DependencyNeverSatisfied -> stop
    dispatching, exit 1 (FAIL mail). Nothing is cancelled.
  - TIMEOUT / CANCELLED / budget stop: the chunk's unfinished shards simply go back to the pool; >= 4 TIMEOUTs -> stop.
  - one free submit slot is kept in each partition (self-resubmission of the main workers, the user's own jobs).
  - when all ext files exist and both main analysis jobs are COMPLETED, submit stage10_ext_analyze.sbatch once.
State: /scratch/$USER/jlens/351_stage10/logs/pool/state.json
"""
import importlib.util, json, os, re, statistics, subprocess, sys, time
from pathlib import Path

DIR = Path.home() / 'jlens_work/10_stage10'
spec = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s10)
ROOT = s10.ROOT; LOGS = ROOT / 'logs'; P = LOGS / 'pool'; P.mkdir(parents=True, exist_ok=True)
DRY = bool(os.environ.get('DRY'))  # DRY=1: one pass, print the sbatch commands, write nothing
STATE = P / ('state_dry.json' if DRY else 'state.json')
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
TRACKS = {'ext': ('jlens_public,logit', '50,51,52,53,54,55,57,58,59,60,61'),
          'main': ('jlens_public,jlens_self100,jlens_fitA,logit,final', '24,32,40,48,56,62')}
PARTS = {'gpu': dict(max_submit=8, keep_free=0, max_min=480), 'gpu-short': dict(max_submit=8, keep_free=0, max_min=120),
         'gpu-interactive': dict(max_submit=4, keep_free=0, max_min=120)}  # user: queue everything possible (2026-10-24/25)
MAIN_PARITY = os.environ.get('MAIN_PARITY', '11347585')  # job whose afterok releases main chunks (2026-10-25: the s10_decision gate)
LOAD_MIN = 12          # model load + setup, minutes (conservative)
GUESS_UNIT_S = 120     # seconds per (condition, shard) until measured
BAD = ('FAILED', 'OUT_OF_MEMORY', 'NODE_FAIL', 'BOOT_FAIL', 'DEADLINE')


def sh(cmd, tries=4):
    for i in range(tries):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        time.sleep(15 * (i + 1))
    raise RuntimeError(f'{cmd}: {r.stderr.strip()}')


def log(*x): print(time.strftime('%F %T'), *x, flush=True)


def missing_units(m, lenses, track):
    ro, ly = TRACKS[track]
    plan = s10.readout_plan(lenses, ro.split(','), s10.parse_layers(ly))
    return [(c, k) for c in CONDS for k in range(m['n_shards']) if any(not s10.out_file(ROOT, r, l, k, c).exists() for r, l in plan)]


def unit_seconds():
    """median seconds per (condition, shard) for each track, from pool job logs (run prints one line per shard)."""
    out = {}
    for track in TRACKS:
        xs = []
        for f in sorted(P.glob(f'job_s10p_{track}_*.log'))[-40:]:
            xs += [float(v) for v in re.findall(r'shard \d+ .*? (\d+)s total=', f.read_text(errors='ignore'))]
        out[track] = statistics.median(xs) if len(xs) >= 5 else GUESS_UNIT_S
    return out


def my_jobs():
    rows = sh(f'squeue -u {os.environ["USER"]} -h -o "%i|%j|%P|%T|%r|%k"').strip().splitlines()
    return [dict(zip(('id', 'name', 'part', 'state', 'reason', 'c1', 'c2', 'c3'), r.split('|'))) | {'comment': '|'.join(r.split('|')[5:8])} for r in rows if r]


def final_state(jid):
    out = sh(f'sacct -j {jid} -n -X -o State').split()
    return out[0] if out else 'UNKNOWN'


def dependency(parity_job):
    """afterok while the parity job is queued/running; none once it COMPLETED (slurm forgets old jobs); stop if it failed."""
    s = final_state(parity_job)
    if s == 'COMPLETED': return ''
    if s in ('PENDING', 'RUNNING', 'REQUEUED'): return f'--dependency=afterok:{parity_job} '
    log('STOP: parity job', parity_job, s); sys.exit(1)


def save(st):
    tmp = STATE.with_name(STATE.name + f'.tmp{os.getpid()}'); tmp.write_text(json.dumps(st, indent=1)); os.replace(tmp, STATE)


def take_lock():
    """one dispatcher only: logs/pool/dispatcher.lock holds the owner's job id ('handover' when it resubmitted itself)."""
    me = os.environ.get('SLURM_JOB_ID', 'local'); lk = P / 'dispatcher.lock'
    running = {j['id'] for j in my_jobs() if j['name'] == 's10_pool' and j['state'] == 'RUNNING'}
    owner = lk.read_text().strip() if lk.exists() else ''
    if owner and owner != me and owner in running: log('another dispatcher owns the pool:', owner, '- exiting'); sys.exit(0)
    lk.write_text(me); time.sleep(10)
    if lk.read_text().strip() != me: log('lost the lock race - exiting'); sys.exit(0)


def adopt(st, jobs):
    """pool jobs in the queue that the state does not know (sbatch said 'failed' but submitted): claim them via --comment."""
    for j in jobs:
        if j['name'].startswith('s10p_') and j['id'] not in st['claims'] and j.get('comment', '').count('|') == 2:
            track, cond, sh_ = j['comment'].split('|')
            st['claims'][j['id']] = dict(track=track, cond=cond, shards=[int(x) for x in sh_.split(':')], part=j['part'], minutes=None)
            log('adopted', j['id'], j['comment'][:40])


def main():
    try: st = json.loads(STATE.read_text())
    except (FileNotFoundError, ValueError): st = dict(claims={}, timeouts=0, ext_analyze=None)
    ext_parity = os.environ['EXT_PARITY']
    m, lenses = s10.verify(ROOT)
    if not DRY: (LOGS / '.pool_active').touch(); take_lock()
    while True:
        jobs = my_jobs(); live = {j['id']: j for j in jobs}
        adopt(st, jobs)
        stuck = [j for j in jobs if j['name'].startswith('s10p_') and 'DependencyNeverSatisfied' in j['reason']]
        if stuck: log('STOP: dependency never satisfied (parity FAIL?)', [j['id'] for j in stuck]); sys.exit(1)
        for jid in [j for j in st['claims'] if j not in live]:
            s = final_state(jid); c = st['claims'].pop(jid)
            log(f'job {jid} {c["track"]} {c["cond"]} {len(c["shards"])} shards ended {s}')
            # 2026-10-26: when one of our jobs ends on a node, our other jobs on that node get SIGKILLed (FAILED 0:9,
            # batch step CANCELLED; 3 jobs at 00:04:37 the second 11363853 finished). Steal mode loses only the shard
            # in flight, so count these instead of stopping; a real crash (non-zero exit, OOM, ...) still stops.
            if s.startswith('FAILED') and sh(f'sacct -j {jid} -n -X -o ExitCode').split()[:1] == ['0:9']:
                st['killed'] = st.get('killed', 0) + 1; log(f'killed by signal 9 (node co-location), count {st["killed"]}'); continue
            if s.startswith(BAD): save(st); log('STOP: pool job failed', jid, s); sys.exit(1)
            if s.startswith('TIMEOUT'): st['timeouts'] += 1
        if st['timeouts'] >= 4: save(st); log('STOP: 4 timeouts'); sys.exit(1)
        if st.get('killed', 0) >= 12: save(st); log('STOP: 12 signal-9 kills'); sys.exit(1)
        claimed = {(c['track'], c['cond'], k) for c in st['claims'].values() for k in c['shards']}
        miss = {t: [u for u in missing_units(m, lenses, t) if (t, *u) not in claimed] for t in TRACKS}
        n_ext_all = len(missing_units(m, lenses, 'ext'))
        secs = unit_seconds()
        paused = (P / 'PAUSED').exists()  # 2026-10-25: set by stage10_guard.py (GPU job ended within 2 min)
        if paused: log('PAUSED (logs/pool/PAUSED): submitting nothing')
        for part, cfg in ({} if paused else PARTS).items():
            free =cfg['max_submit'] - cfg['keep_free'] - sum(j['part'] == part for j in jobs)
            while free > 0:
                track = 'main' if miss['main'] else ('ext' if miss['ext'] else None)  # 2026-10-25: no w0/w1 any more, main first
                if track is None: break
                n_max = max(1, int((cfg['max_min'] - LOAD_MIN - 10) * 60 / (secs[track] * 1.3)))
                cond = miss[track][0][0]
                shards = [k for c, k in miss[track] if c == cond][:n_max]
                miss[track] = [u for u in miss[track] if not (u[0] == cond and u[1] in shards)]
                minutes = min(cfg['max_min'], max(60, int(LOAD_MIN + 10 + len(shards) * secs[track] * 1.3 / 60)))
                dep = dependency(ext_parity if track == 'ext' else MAIN_PARITY)
                ro, ly = TRACKS[track]
                name = f's10p_{track}_{cond}'
                cmd = (f'sbatch --parsable --partition={part} --time={minutes} --job-name={name} {dep}'
                       f'--output={P}/job_{name}_%j.log --comment=\'{track}|{cond}|{":".join(map(str, shards))}\' '
                       f'--export=ALL,CONDITION={cond},SHARDS={":".join(map(str, shards))},READOUTS={ro.replace(",", ":")},LAYERS={ly.replace(",", ":")},BUDGET={minutes - LOAD_MIN - 8} '
                       f'{DIR}/stage10_pool_job.sbatch')
                if DRY: print(cmd); jid = f'dry{len(st["claims"])}'
                else:
                  try: jid = sh(cmd, tries=1).strip().split(';')[0]
                  except RuntimeError as e: log('sbatch refused (may still have been submitted; adopted next pass if so):', e); break
                st['claims'][jid] = dict(track=track, cond=cond, shards=shards, part=part, minutes=minutes)
                jobs.append(dict(id=jid, name=name, part=part, state='PENDING', reason=''))
                log(f'submitted {jid} {part} {minutes}min {track} {cond} shards {shards[0]}..{shards[-1]} ({len(shards)})')
                free -= 1
        if DRY: log('dry run: secs', secs, 'missing', {t: len(v) for t, v in miss.items()}); return
        save(st)
        main_left = missing_units(m, lenses, 'main')
        for mode, cond_ok in (('main', not any(c == 'true' for c, _ in main_left)), ('title', not main_left)):
            lock = LOGS / f'.analyze_{mode}_submitted'
            if cond_ok and not DRY and not lock.exists():
                lock.mkdir(); jid = sh(f'sbatch --parsable --export=ALL,MODE={mode} --job-name=s10_analyze_{mode} {DIR}/stage10_analyze.sbatch').strip()
                log(f'submitted analyze {mode}', jid)
        if n_ext_all == 0 and not st['ext_analyze']:
            sm = [final_state(j) for j in sh('sacct -u $USER -n -X -S 2026-10-23 --name=s10_analyze_main,s10_analyze_title -o JobID').split()]
            if len(sm) >= 2 and all(s == 'COMPLETED' for s in sm[-2:]) and not (LOGS / '.analyze_ext_submitted').exists():
                (LOGS / '.analyze_ext_submitted').mkdir()
                st['ext_analyze'] = sh(f'sbatch --parsable {DIR}/stage10_ext_analyze.sbatch').strip(); log('submitted ext analyze', st['ext_analyze'])
                save(st)
        if st['ext_analyze'] and not st['claims'] and not miss['main'] and not any(j['name'].startswith('s10p_') for j in jobs):
            log('all done'); return
        time.sleep(300)


if __name__ == '__main__':
    main()
