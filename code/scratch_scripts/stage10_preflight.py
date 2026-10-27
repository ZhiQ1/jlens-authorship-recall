"""Stage 10 preflight (CPU, 2026-10-25): run every check a pool job does before it needs the GPU, so a job that gets a
card is not stopped at a gate. Prints one PASS/FAIL line per check; exit 1 if any check fails.

  A. the real job command (351_stage10_fix1.py run, steal mode, pool-job env) end to end: it must reach load_model and
     stop only at 'no GPU visible'
  B. s10.run for all 14 (track, condition) pairs: parity gate, condition prompts, todo list; must reach load_model
  C. what s10.run checks after the load: prompt encoding == frozen ids (every paper, every condition, same tokenizer),
     lens sha256 + layers present, model weights present, output dirs writable
"""
import argparse, importlib.util, json, os, subprocess, sys
from pathlib import Path

DIR = Path(__file__).parent
spec = importlib.util.spec_from_file_location('s10', DIR / '351_stage10.py'); s10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s10)
sys.path.insert(0, str(DIR)); import stage10_steal as st
ROOT = s10.ROOT; results = []


def check(name, ok, detail=''):
    results.append(ok); print(f'{"PASS" if ok else "FAIL"}  {name}  {detail}', flush=True)


class ReachedGPU(Exception): pass


def part_a():
    env = dict(os.environ, SLURM_JOB_NAME='s10p_preflight', SLURM_JOB_ID='preflight', CUDA_VISIBLE_DEVICES='',
               HF_HOME=f'/scratch/{os.environ["USER"]}/hf', HF_HUB_OFFLINE='1', PYTHONDONTWRITEBYTECODE='1')
    cmd = [sys.executable, '-u', str(DIR / '351_stage10_fix1.py'), 'run', '--condition', 'true', '--shards', '0',
           '--readouts', 'jlens_public,logit', '--layers', '50', '--max-minutes', '90']
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1800)
    out = r.stdout + r.stderr
    claims = sorted((ROOT / 'logs/pool/claims').glob('*'))
    for d in claims:  # give back the claim this check took (owner 'preflight'); kept as a renamed dir, nothing deleted
        if d.is_dir() and (d / 'owner').exists() and (d / 'owner').read_text().strip() == 'preflight':
            os.rename(d, d.with_name(d.name + '.preflight_released'))
    ok = 'steal mode' in out and 'steal: main' in out and 'no GPU visible' in out and 'run parity first' not in out and 'no parity PASS' not in out
    last = [l for l in out.splitlines() if l.strip()][-1:]
    check('A real job command reaches the GPU load', ok, f'steal={"steal mode" in out} last="{last[0][:120] if last else ""}"')
    if not ok: print(out[-3000:])


def part_b(m, lenses):
    def stop(*a, **k): raise ReachedGPU
    s10.load_model = stop
    for track, ro, ly in st.TRACKS:
        for cond in st.CONDS:
            a = argparse.Namespace(root=str(ROOT), readouts=ro, layers=ly, shards=None, condition=cond, max_minutes=None, skip_parity_gate=False)
            try: s10.run(a); check(f'B gate {track} {cond}', False, 'returned without work (all done?)')
            except ReachedGPU: check(f'B gate {track} {cond}', True, 'parity gate + prompts + todo OK, reached load_model')
            except Exception as e: check(f'B gate {track} {cond}', False, repr(e)[:200])


def part_c(m, lenses):
    import pandas as pd
    tok = s10.tokenizer()
    papers = pd.read_parquet(ROOT / 'cohort/papers.parquet')
    for cond in st.CONDS:
        prompts, _ = s10.condition_prompts(ROOT, papers, cond)
        bad = [pid for pid, (p, ids) in prompts.items() if tok(p, truncation=True, max_length=s10.MAX_CONTEXT).input_ids != ids]
        check(f'C prompt encoding {cond}', not bad, f'{len(prompts)} papers, {len(bad)} differ {bad[:3]}')
    import jlens
    for name, e in lenses.items():
        sha_ok = s10.sha_file(e['path']) == e['sha256']
        lens = jlens.JacobianLens.load(e['path'])
        need = {l for _, ro, ly in st.TRACKS for l in s10.parse_layers(ly) if f'jlens_{name}' in ro.split(',')}
        miss = sorted(need - set(lens.jacobians))
        check(f'C lens {name}', sha_ok and not miss, f'sha={sha_ok} missing layers={miss}')
        del lens
    snap = Path(os.environ.get('HF_HOME', f'/scratch/{os.environ["USER"]}/hf')) / f'hub/models--Qwen--Qwen3-32B/snapshots/{s10.REV}'
    idx = json.loads((snap / 'model.safetensors.index.json').read_text())
    files = sorted(set(idx['weight_map'].values())); missing = [f for f in files if not (snap / f).exists()]
    check('C model weights present', not missing, f'{len(files)} files, missing {missing}')
    import transformers; transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV); check('C model config loads offline', True)
    for track, ro, ly in st.TRACKS:
        for cond in st.CONDS:
            d = s10.raw_dir(ROOT, cond); d.mkdir(parents=True, exist_ok=True)
            t = d / f'.preflight_write_test_{os.getpid()}'; t.write_text('x'); t.rename(d / '.preflight_write_ok')
    check('C output dirs writable', True)


if __name__ == '__main__':
    m, lenses = s10.verify(ROOT)
    pj = s10.load(ROOT / 'reports/parity.json')
    check('parity.json status', pj['status'] == 'PASS', f"{pj['status']}, {len(pj['passed_pairs'])} pairs")
    check('steal_mode flag', (ROOT / 'logs/pool/steal_mode').exists())
    part_b(m, lenses)
    part_c(m, lenses)
    part_a()
    print(f'PREFLIGHT {"PASS" if all(results) else "FAIL"}: {sum(results)}/{len(results)} checks passed', flush=True)
    sys.exit(0 if all(results) else 1)
