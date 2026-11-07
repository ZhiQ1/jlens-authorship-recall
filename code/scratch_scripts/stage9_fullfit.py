#!/usr/bin/env python3
"""Stage 9 full split-half fit scheduler. Does not edit stage9_runner.py / 351_stage9.py.

A bounded invocation fits an immutable *prefix* of the same 100-prompt sequence,
using jlens.fit's own resumable checkpoint. No final Lens is claimed until 100/100.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path('/scratch') / os.environ.get('USER', '') / 'jlens'
SRC = BASE / 'stage9_runner.py'
LAYERS = [16, 24, 32, 40, 48, 56, 62]
TOTAL = 100


def load_runner():
    import importlib.util
    if not SRC.is_file():
        raise FileNotFoundError(f'Missing verified runner: {SRC}')
    spec = importlib.util.spec_from_file_location('stage9_runner_existing', SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def args_for(m, half):
    from types import SimpleNamespace
    return SimpleNamespace(root=m.ROOT, half=half, total=TOTAL, layers=LAYERS[:], dim_batch=1,
                           run_id=f'full_{half}_100_7layers')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    with tmp.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def remaining_seconds(s):
    s = s.strip().splitlines()[0].strip() if s.strip() else ''
    if not s or s.upper() in ('N/A', 'UNLIMITED', 'NOT_SET', 'INVALID'):
        raise RuntimeError('No finite time limit from Slurm; use --budget-seconds')
    # Slurm %L format: [[days-]hours:]minutes:seconds or minutes
    days = 0
    if '-' in s:
        d, s = s.split('-', 1)
        days = int(d)
    parts = list(map(int, s.split(':')))
    if len(parts) == 3:
        hh, mm, ss = parts
    elif len(parts) == 2:
        hh, mm, ss = 0, *parts
    elif len(parts) == 1:
        hh, mm, ss = 0, parts[0], 0
    else:
        raise RuntimeError('Unrecognized Slurm time format')
    if any(x < 0 for x in [days, hh, mm, ss]) or not (0 <= ss < 60) or not (0 <= mm < 60):
        raise RuntimeError('Invalid Slurm duration')
    return ((days * 24 + hh) * 60 + mm) * 60 + ss


def slurm_budget():
    job = os.environ.get('SLURM_JOB_ID')
    if not job:
        raise RuntimeError('Not within a Slurm allocation; do not fit on login nodes')
    p = subprocess.run(['squeue', '-h', '-j', job, '-o', '%L'], check=True, text=True,
                       capture_output=True, timeout=15)
    if p.returncode != 0:
        raise RuntimeError('squeue returned failure')
    return remaining_seconds(p.stdout)


def configuration():
    # Critical: freeze BOTH library source and runner source to guard against silent edits mid-run.
    return dict(protocol='STAGE9_FULLFIT_PREFIX_V1', total=TOTAL, layers=LAYERS,
                dim_batch=1, target_layer=63, max_seq_len=128, skip_first=16,
                checkpoint_every=1, stage9_runner_sha256=sha(SRC),
                legacy_stage9_sha256=sha(BASE / '351_stage9.py'))


def status(m, a, cfg):
    out = m.target(a)
    if not (out / 'fitting_config.json').exists():
        if (out / 'checkpoint.pt').exists() or (out / 'lens.pt').exists() or (out / 'fit_status.json').exists():
            raise RuntimeError('Unbound artifacts in run directory')
        return out, 0, None
    if read_json(out / 'fitting_config.json') != cfg:
        raise RuntimeError('FROZEN CONFIG MISMATCH; abort, do not overwrite')
    ck = out / 'checkpoint.pt'
    if ck.exists():
        st = m.validate_existing(a, m.load_old(), out, cfg)
        done = st['next_idx']
        if done != st['n_done']:
            raise RuntimeError('Skipped prompt, cannot claim clean 100/100')
        return out, done, st
    if (out / 'lens.pt').exists() or (out / 'fit_status.json').exists():
        raise RuntimeError('Saved lens/marker without checkpoint')
    return out, 0, None


def get_environment(m, half):
    a = args_for(m, half)
    # Audit source files and verify payload hashes / distinct splits every invocation.
    cfg, prompts = m.frozen(m.load_old(), a)
    assert len(prompts) == TOTAL and len(cfg['prompt_ids']) == TOTAL
    return a, cfg, prompts


def pin_protocol(out, protocol, cfg):
    p = out / 'scheduler_protocol.json'
    frozen = dict(protocol=protocol, fit_config_sha256=hashlib.sha256(json.dumps(cfg, sort_keys=True, indent=2).encode()).hexdigest())
    # Use exact file hash, rather than re-rendered JSON, if available.
    if (out / 'fitting_config.json').exists():
        frozen['fit_config_sha256'] = sha(out / 'fitting_config.json')
    if p.exists():
        old = read_json(p)
        if old != frozen:
            raise RuntimeError('SCHEDULER SOURCE/PROTOCOL CHANGED; abort; review manually')
    else:
        atomic_json(p, frozen)


def plan_count(done, seconds, per_prompt, reserve, max_new):
    if seconds <= reserve:
        return 0
    return max(0, min(TOTAL - done, max_new, int((seconds - reserve) // per_prompt)))


def execute(ns):
    m = load_runner()
    a, cfg, prompts = get_environment(m, ns.half)
    out, done, ck_state = status(m, a, cfg)
    protocol = configuration()
    if out.exists() and (out / 'fitting_config.json').exists():
        if not (out / 'scheduler_protocol.json').is_file():
            raise RuntimeError('Existing run has no scheduler protocol; abort instead of adopting it')
        pin_protocol(out, protocol, cfg)
    if ns.command == 'check':
        print('FULLFIT CHECK', json.dumps(dict(half=ns.half, directory=str(out), done=done,
              remaining=TOTAL-done, complete_marker=(out/'fit_status.json').is_file(),
              config_sha256=(sha(out/'fitting_config.json') if (out/'fitting_config.json').exists() else None))), flush=True)
        if done == TOTAL:
            m.load_old().verify_saved_fit(out, cfg, write_marker=False)
        return
    if done == TOTAL:
        m.load_old().verify_saved_fit(out, cfg, write_marker=False)
        print('FULLFIT ALREADY COMPLETE', ns.half, '100/100; no GPU work', flush=True)
        return
    if ns.budget_seconds is not None:
        if not ns.allow_manual_budget:
            raise RuntimeError('--budget-seconds needs --allow-manual-budget (do not fake Slurm budget)')
        if not os.environ.get('SLURM_JOB_ID'):
            raise RuntimeError('GPU run requires Slurm allocation')
        seconds = min(ns.budget_seconds, slurm_budget())
    else:
        seconds = slurm_budget() if ns.command == 'run' else 7200
    n = TOTAL - done  # Run until all 100 prompts finish or Slurm terminates the job
    print('FULLFIT PLAN', json.dumps(dict(half=ns.half, done=done, remaining=TOTAL-done,
           budget_seconds=seconds, seconds_per_prompt=ns.seconds_per_prompt,
           reserve_seconds=ns.reserve_seconds, max_new=ns.max_new, this_job_new=n,
           target_prefix=done+n)), flush=True)
    if ns.command == 'plan': return
    if not ns.confirm_fit:
        raise RuntimeError('GPU execution needs --confirm-fit')
    if n == 0:
        print('NO SAFE WINDOW: no model load; obtain new allocation', flush=True)
        return
    out.mkdir(parents=True, exist_ok=True)
    cp = out / 'checkpoint.pt'
    cpath = out / 'fitting_config.json'
    if not cpath.exists():
        atomic_json(cpath, cfg)
    pin_protocol(out, protocol, cfg)
    # Never use 'check' to regenerate or alter a matrix checkpoint.
    print('FULLFIT EXECUTE',ns.half,'from',done,'to',done+n,'of',TOTAL,'checkpoint',cp,flush=True)
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s', force=True)
    import torch
    import transformers
    import jlens
    t0 = time.monotonic()
    tok = transformers.AutoTokenizer.from_pretrained(cfg['model'], revision=cfg['revision'])
    hf = transformers.AutoModelForCausalLM.from_pretrained(cfg['model'], revision=cfg['revision'],
                     torch_dtype=torch.bfloat16, device_map='auto', max_memory={0: '55GiB', 'cpu': '36GiB'}, low_cpu_mem_usage=True)
    model = jlens.from_hf(hf, tok)
    # Critical: immutable full config TOTAL=100, but jlens.fit only receives prefix[:target].
    # jlens.fit uses indexed prompt list, and resume skips indices < next_idx.
    lens = jlens.fit(model, prompts[:done+n], source_layers=LAYERS, target_layer=63,
                    dim_batch=1, max_seq_len=128, skip_first=16,
                    checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
    state = m.inspect_checkpoint(m.load_old(), cp, cfg)
    if state['next_idx'] != done+n or state['n_done'] != done+n or lens.n_prompts != done+n:
        raise RuntimeError(f'PARTIAL PROGRESS INVALID: next={state["next_idx"]}, done={state["n_done"]}, target={done+n}')
    if set(lens.jacobians) != set(LAYERS):
        raise RuntimeError('Lens layers incomplete')
    record = dict(half=ns.half, start=done, end=done+n, target=TOTAL,
                  checkpoint_sha256=sha(cp), elapsed_seconds=round(time.monotonic()-t0,3),
                  timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    atomic_json(out / f'progress_{done:03d}_{done+n:03d}.json',record)
    del model, hf, tok
    if done+n != TOTAL:
        print('FULLFIT PARTIAL SAVED', json.dumps(record,sort_keys=True),'RUN SAME COMMAND NEXT ALLOCATION',flush=True)
        return
    # Only the terminal 100/100 produces the final lens and success marker.
    if (out / 'lens.pt').exists() or (out / 'fit_status.json').exists():
        raise RuntimeError('Unexpected preexisting final artifacts')
    lens.save(str(out / 'lens.pt'))
    m.load_old().verify_saved_fit(out, cfg)
    print('FULLFIT COMPLETE VERIFIED', ns.half,'100/100',out,flush=True)


def main():
    p=argparse.ArgumentParser(description='Safe bounded Stage9 A/B 100-prompt, 7-layer fit')
    p.add_argument('command', choices=['plan','run','check'])
    p.add_argument('--half', choices=['A','B'], required=True)
    p.add_argument('--max-new', type=int, default=12)
    p.add_argument('--seconds-per-prompt', type=int, default=450)
    p.add_argument('--reserve-seconds', type=int, default=900)
    p.add_argument('--budget-seconds', type=int)
    p.add_argument('--allow-manual-budget', action='store_true')
    p.add_argument('--confirm-fit', action='store_true')
    ns=p.parse_args()
    if ns.max_new < 1 or ns.max_new > TOTAL or ns.seconds_per_prompt < 320 or ns.reserve_seconds < 600:
        p.error('Require 1<=max-new<=100, seconds-per-prompt>=320, reserve>=600')
    if ns.budget_seconds is not None and ns.budget_seconds <= 0: p.error('budget must be positive')
    execute(ns)

if __name__=='__main__':
    main()
