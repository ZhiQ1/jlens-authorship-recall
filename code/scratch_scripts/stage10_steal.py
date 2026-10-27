"""Work stealing for Stage 10 pool jobs (2026-10-25; user: one full main round is needed within 12 h).

The queued s10p_* jobs each carry a fixed chunk (track, condition, shards) in their environment, and the jobs that reach
the head of the A100 queues first were ext chunks. With logs/pool/steal_mode present, 351_stage10_fix1.py hands `run` to
this module instead: the job loads the model once, then keeps taking the next unfinished unit in global priority order
(main round: true, false_0..false_4, delete; then ext), whatever its own chunk says.
  - claim: mkdir logs/pool/claims/<track>_<cond>_<shard>/ (atomic) holding the owner job id; a claim whose owner is no
    longer RUNNING is taken over (rename first, so only one job wins).
  - each unit goes through the frozen s10.run (parity gate, readout code, output files unchanged); the model and the
    lenses are loaded once and reused.
  - budget: stop before a unit that would not finish within --max-minutes (same 1.5x rule as s10.run).
"""
import argparse, os, subprocess, time
from pathlib import Path

CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4', 'delete']
TRACKS = [('main', 'jlens_public,jlens_self100,jlens_fitA,logit,final', '24,32,40,48,56,62'),
          ('ext', 'jlens_public,logit', '50,51,52,53,54,55,57,58,59,60,61')]


def running_jobs():
    try: r = subprocess.run(['squeue', '-u', os.environ['USER'], '-h', '-t', 'RUNNING', '-o', '%i'], capture_output=True, text=True, timeout=90)
    except Exception: return None
    return set(r.stdout.split()) if r.returncode == 0 else None


def claim(d, me):
    try: d.mkdir(parents=True); (d / 'owner').write_text(me); return True
    except FileExistsError: pass
    try: owner = (d / 'owner').read_text().strip()
    except FileNotFoundError: return False  # another job is creating it right now
    if owner == me: return True
    run = running_jobs()
    if run is None or owner in run: return False
    moved = d.with_name(f'{d.name}.stale_{owner}_{me}')
    try: os.rename(d, moved)
    except OSError: return False
    if (moved / 'owner').read_text().strip() != owner:  # another job took it over first and re-claimed it: put it back
        os.rename(moved, d); return False
    print(f'took over stale claim {d.name} from {owner}', flush=True)
    return claim(d, me)


def main(s10, argv):
    p = argparse.ArgumentParser(); p.add_argument('command'); p.add_argument('--max-minutes', type=float, default=None)
    a, _ = p.parse_known_args(argv)
    budget, me, root = a.max_minutes, os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'), s10.ROOT
    C = root / 'logs/pool/claims'; C.mkdir(parents=True, exist_ok=True)
    m, lenses = s10.verify(root)
    model_cache, lens_cache = {}, {}
    load_model, open_lenses = s10.load_model, s10.open_lenses

    def cached_model():
        if 'm' not in model_cache: model_cache['m'] = load_model()
        return model_cache['m']

    def cached_lenses(lenses_, plan, model):
        key = tuple(plan)
        if key not in lens_cache:
            lens_cache.clear()
            import torch; torch.cuda.empty_cache()
            lens_cache[key] = open_lenses(lenses_, plan, model)
        return lens_cache[key]

    s10.load_model, s10.open_lenses = cached_model, cached_lenses
    print(f'{s10.now()} steal mode: job {me} ignores its own chunk; budget {budget} min', flush=True)
    t_start, last = time.monotonic(), 0.0
    while True:
        unit = None
        for track, ro, ly in TRACKS:
            plan = s10.readout_plan(lenses, ro.split(','), s10.parse_layers(ly))
            for cond in CONDS:
                for k in range(m['n_shards']):
                    if all(s10.out_file(root, r, l, k, cond).exists() for r, l in plan): continue
                    if claim(C / f'{track}_{cond}_{k:03d}', me): unit = (track, ro, ly, cond, k); break
                if unit: break
            if unit: break
        if unit is None:
            print(f'{s10.now()} steal: nothing left to claim', flush=True)
            s11dir = Path.home() / 'jlens_work/11_stage11'; flag = Path('/scratch') / os.environ['USER'] / 'jlens/361_stage11/logs/accept_stage10_jobs'
            if flag.exists():                 # 2026-10-26: queued Stage 10 jobs that find no work run Stage 11 units instead
                import importlib.util, sys
                sys.path.insert(0, str(s11dir))
                sp = importlib.util.spec_from_file_location('s11', s11dir / '361_stage11.py'); s11 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s11)
                s11.work(argparse.Namespace(max_minutes=budget), budget=budget, t_start=t_start)
            return
        track, ro, ly, cond, k = unit
        if budget and model_cache and (time.monotonic() - t_start) / 60 + 1.5 * last / 60 > budget:
            os.rename(C / f'{track}_{cond}_{k:03d}', C / f'{track}_{cond}_{k:03d}.released_{me}')
            print('time budget reached; released', track, cond, k, flush=True); return
        t0 = time.monotonic()
        print(f'{s10.now()} steal: {track} {cond} shard {k}', flush=True)
        s10.run(argparse.Namespace(root=str(root), readouts=ro, layers=ly, shards=str(k), condition=cond,
                                   max_minutes=None, skip_parity_gate=False))
        last = time.monotonic() - t0 if model_cache.get('timed') else 0.0
        model_cache['timed'] = True  # the first unit includes the model load, so it does not count for the budget rule
