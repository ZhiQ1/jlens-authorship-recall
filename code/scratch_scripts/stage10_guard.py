"""Stage 10 guard (CPU, 2026-10-25; user: any GPU job that ends within 2 minutes -> alarm in PROGRESS.md + pause).

Every 60 s it reads sacct for this user's s10* jobs on the GPU partitions that started after the guard was first
launched. A job that started and ended within MIN_S seconds (any end state) is an alarm, unless its log says
'nothing left to claim' (the normal exit when all work is done). On an alarm:
  - write logs/pool/PAUSED (json: job, state, seconds, log tail) and put an ALARM entry at the top of PROGRESS.md
  - hold every pending s10p_* job (scontrol hold: reversible, keeps the job; nothing is cancelled), and keep holding new
    ones the dispatcher submits while PAUSED exists; the dispatcher itself submits nothing while PAUSED exists
  - mail the user (a tiny sbatch job named S10_ALARM_PAUSED with --mail-type=END)
Resume (after the cause is fixed): mv logs/pool/PAUSED logs/pool/PAUSED_resolved_<date>; scontrol release <held ids>.
"""
import json, os, subprocess, time
from pathlib import Path

ROOT = Path(f'/scratch/{os.environ["USER"]}/jlens/351_stage10'); P = ROOT / 'logs/pool'
PROGRESS = Path.home() / 'jlens_work/PROGRESS.md'
PREFIX = os.environ.get('GUARD_PREFIX', 's10')  # 2026-10-26: a second guard watches Stage 11 jobs (GUARD_PREFIX=s11)
PAUSED = P / 'PAUSED'; SEEN = P / ('guard_seen.json' if PREFIX == 's10' else f'guard_seen_{PREFIX}.json')
GPU_PARTS = ('gpu', 'gpu-short', 'gpu-interactive'); MIN_S = 120
SINCE = os.environ.get('GUARD_SINCE', '2026-10-25T22:00:00')


def sh(cmd):
    for i in range(4):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode == 0: return r.stdout
        time.sleep(15 * (i + 1))
    print('command failed:', cmd, r.stderr.strip(), flush=True); return ''


def log(*x): print(time.strftime('%F %T'), *x, flush=True)


def log_tail(jid, name):
    for f in [*P.glob(f'job_*_{jid}.log'), *(ROOT / 'logs').glob(f'*{jid}*.log')]:
        return f, f.read_text(errors='ignore')[-1500:]
    return None, ''


def alarm(rows):
    now = time.strftime('%F %T')
    tails = {r['id']: log_tail(r['id'], r['name']) for r in rows}
    if not PAUSED.exists():
        PAUSED.write_text(json.dumps(dict(created=now, jobs=rows, log=str(next(iter(tails.values()))[0])), indent=1))
    lines = [f'## {now} — ⚠️ ALARM: GPU job ended within {MIN_S} s; dispatch PAUSED (stage10_guard)', '']
    for r in rows:
        f, tail = tails[r['id']]
        last = [l for l in tail.splitlines() if l.strip()][-3:]
        lines += [f'- {r["id"]} {r["name"]} ({r["part"]}) {r["state"]} after {r["secs"]} s; log `{f}`'] + [f'  - `{l[:200]}`' for l in last]
    lines += ['- Pending s10p_* jobs are held (scontrol hold, nothing cancelled); the dispatcher submits nothing while `logs/pool/PAUSED` exists.',
              '- Resume after fixing: `mv logs/pool/PAUSED logs/pool/PAUSED_resolved_<date>`, then `scontrol release` the held jobs.', '']
    text = PROGRESS.read_text(); i = text.find('\n## ')
    PROGRESS.write_text(text[:i + 1] + '\n'.join(lines) + '\n' + text[i + 1:] if i >= 0 else text + '\n' + '\n'.join(lines))
    sh(f'sbatch --partition=short --account=cs7980.202710 --time=1 --mem=100M --job-name=S10_ALARM_PAUSED --mail-type=END '
       f'--mail-user=zhang.zhiqi2@northeastern.edu --output=/dev/null --wrap "echo {rows[0]["id"]} ended in {rows[0]["secs"]}s"')
    log('ALARM', rows)


def hold_pending():
    for row in sh(f'squeue -u {os.environ["USER"]} -h -t PENDING -o "%i|%j|%r"').splitlines():
        jid, name, reason = row.split('|', 2)
        if name.startswith(('s10p_', 's11w')) and 'Held' not in reason:
            sh(f'scontrol hold {jid}'); log('held', jid, name)


def main():
    seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
    log('guard up; jobs started since', SINCE, 'min seconds', MIN_S)
    while True:
        new = []
        for row in sh(f'sacct -u {os.environ["USER"]} -S {SINCE} -X -n -P -o JobID,JobName,Partition,State,ElapsedRaw,Start').splitlines():
            jid, name, part, state, secs, start = row.split('|')
            if jid in seen or not name.startswith(PREFIX) or part not in GPU_PARTS: continue
            if state.startswith(('PENDING', 'RUNNING', 'REQUEUED', 'SUSPENDED')) or start in ('Unknown', 'None', ''): continue
            seen.add(jid)
            if int(secs or 0) < MIN_S and 'nothing left to claim' not in log_tail(jid, name)[1]:
                new.append(dict(id=jid, name=name, part=part, state=state.split()[0], secs=int(secs or 0)))
        SEEN.write_text(json.dumps(sorted(seen)))
        if new: alarm(new)
        if PAUSED.exists(): hold_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
