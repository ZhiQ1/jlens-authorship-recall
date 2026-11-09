"""Addendum 12 item 2-1, gate runner v3 (D12-1 unchanged). NOT SUBMITTED; proposal written 2026-11-09 after gate_v2 jobs
11725846 (SIGKILL at 11 min of a 20-min backfill limit) and 11728013 (TIMEOUT at 20 min: 14.5-min first load on a crowded d1028).

Only change vs stage9_b2_fitb_v2.py `gpu --unit gate_v2`: the runner-loader model for part (a) is loaded ONLY if one of the
per-prompt Fit A states fitA_k3/state_{1,2,3}.pt is missing (v2 loaded it unconditionally, then gate_a skipped all prompts because
the states from 11725846 exist). Rule, prompts, layers, loaders, comparison (torch.equal), part (b) (V1.gate, frozen fullfit loader
with 55 GiB GPU cap + CPU offload, prompt 66 vs log) and outputs (summary/gate_v2.json/.csv, HARD_CHECK_FAILED) are the v2 code,
called by import. The bitwise comparison is still recomputed from the state files every run.
Code-version guard (2026-11-09, user request): the stored states are reused ONLY if fitA_k3/provenance.json exists and every
recorded sha256 (v1/v2 runner, the 3 frozen Stage 9 scripts, every jlens/*.py, the 3 state files) and library version equals the
current one; otherwise the runner model is loaded and part (a) is recomputed into a fresh directory fitA_k3_v3/ (states not reused).
provenance.json was written by `provenance` (CPU) on 2026-11-09 for the states of job 11725846 (2026-11-08 04:51-04:57): v1/v2 sha256
equal their blobs in git commit b8e9eb1 (2026-11-07 02:52, before that job); frozen scripts equal the git copies; jlens files and the
env have mtimes before the job (recorded). The branch taken is logged ("BRANCH reuse" / "BRANCH reload: <reason>").
Usage: python stage9_b2_fitb_v3.py gate | provenance   (gate via stage9_b2_fitb_v3_gate.sbatch, full 45 min, no --time-min)
"""
import gc, hashlib, importlib.util, json, os, sys, time
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('fitb_v2', H / '09_stage9/stage9_b2_fitb_v2.py'); V2 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V2)
V1, log = V2.V1, V2.log


JL = Path.home() / 'projects/jacobian-lens/jlens'
PROV_JOB = '11725846'


def _sha(p): 
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()


def code_record(root):
    import torch, transformers, accelerate
    files = {str(H / '09_stage9' / n): None for n in ('stage9_b2_fitb.py', 'stage9_b2_fitb_v2.py', '351_stage9.py', 'stage9_runner.py', 'stage9_fullfit.py')}
    files.update({str(p): None for p in sorted(JL.rglob('*.py'))})
    files.update({str(root / 'fitA_k3' / f'state_{n}.pt'): None for n in range(1, max(x[0] for x in V2.STORED) + 1)})
    rec = {f: (_sha(f) if os.path.exists(f) else 'MISSING') for f in files}
    return dict(files=rec, versions=dict(torch=torch.__version__, transformers=transformers.__version__, accelerate=accelerate.__version__))


def write_provenance(root):
    """CPU, once: record the code of the existing states (job 11725846). Refuses if any file is newer than those states."""
    d = root / 'fitA_k3'; out = d / 'provenance.json'
    if out.exists(): raise SystemExit(f'{out} exists: not overwritten')
    rec = code_record(root); t_states = min(os.path.getmtime(d / f'state_{n}.pt') for n in (1, 2, 3))
    newer = [f for f in rec['files'] if '/fitA_k3/' not in f and os.path.getmtime(f) >= t_states - 300]
    if newer: raise SystemExit(f'code newer than the states, provenance not provable: {newer}')
    rec.update(job=PROV_JOB, written=V1.now(), method='reconstructed after the job: current sha256 + mtimes before the job start '
               '(2026-11-08T04:50:40); v1/v2 sha256 == git blobs of commit b8e9eb1 (2026-11-07 02:52 EST); frozen Stage 9 scripts == git copies',
               mtimes={f: time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.path.getmtime(f))) for f in rec['files']})
    out.write_text(json.dumps(rec, indent=1)); log('provenance written', out); return rec


def provenance_ok(root):
    f = root / 'fitA_k3' / 'provenance.json'
    if not f.exists(): return False, 'no fitA_k3/provenance.json'
    p = json.loads(f.read_text()); c = code_record(root)
    if p['versions'] != c['versions']: return False, f'library versions differ {p["versions"]} vs {c["versions"]}'
    diff = [k for k in set(p['files']) | set(c['files']) if p['files'].get(k) != c['files'].get(k) or c['files'].get(k) == 'MISSING']
    return (not diff), ('code/state sha256 equal to provenance of job ' + p['job']) if not diff else f'differs: {diff}'


class _NoModel:
    """truthy placeholder: gate_a only touches the model inside jlens.fit for a missing state file."""
    def __getattr__(self, k): raise RuntimeError('runner model needed but not loaded (state file missing?)')


def gate_a_fresh(d, model):
    """v2 gate_a logic with its output dir moved to d (gate_a writes root/'fitA_k3'): run it on a shim root."""
    d.mkdir(parents=True, exist_ok=True); shim = d / '_root'; shim.mkdir(exist_ok=True)
    link = shim / 'fitA_k3'
    if not link.exists(): link.symlink_to(d)
    return V2.gate_a(shim, model=model)


def gate_v3(root):
    import torch, pandas as pd
    if not V1.backup_ok(root): raise SystemExit('no verified backup of the 66-prompt checkpoint: run backup first')
    t0 = time.monotonic(); ok, why = provenance_ok(root)
    if ok:
        log('BRANCH reuse (runner model not loaded):', why); sa, rows = V2.gate_a(root, model=_NoModel())
    else:
        log('BRANCH reload:', why, '-> part (a) recomputed into', root / 'fitA_k3_v3')
        model, hf = V2.runner_loader(); sa, rows = gate_a_fresh(root / 'fitA_k3_v3', model); del model, hf
    gc.collect(); torch.cuda.empty_cache()
    log(f'D12-1 (a) Fit A k={V2.K} bitwise:', sa, f'cuda allocated after free {torch.cuda.memory_allocated() / 2**30:.2f} GiB', f'{time.monotonic() - t0:.0f}s')
    okb = V1.gate(root)                                     # (b) unchanged: prompt 66 vs log, frozen fullfit loader
    rows += json.loads((root / 'summary/gate.json').read_text())['rows']
    st = 'PASS' if sa == 'PASS' and okb else 'FAIL'
    df = V1.COLS.check(pd.DataFrame(rows, columns=V1.COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); df.to_csv(root / 'summary/gate_v2.csv', index=False)
    (root / 'summary/gate_v2.json').write_text(json.dumps(dict(status=st, rule='D12-1: (a) Fit A prompts 1-3 bitwise == stored prefix states; (b) Fit B prompt 66 vs log',
                                                               runner='stage9_b2_fitb_v3.py (lazy part-(a) model load)', seconds=round(time.monotonic() - t0),
                                                               rows=rows, at=V1.now()), indent=1, default=float))
    print('HARD CHECK D12-1', st, flush=True)
    if st != 'PASS': (root / 'HARD_CHECK_FAILED').write_text(json.dumps(rows, default=float))
    return st == 'PASS'


if __name__ == '__main__':
    if sys.argv[1:] not in (['gate'], ['provenance'], ['check']): raise SystemExit('usage: stage9_b2_fitb_v3.py gate|provenance|check')
    V1.check_frozen(); V2.check_dev(); root = V1.R13 / 'b2_fitb'
    if sys.argv[1] == 'provenance': write_provenance(root); sys.exit(0)
    if sys.argv[1] == 'check': print('BRANCH would be', *provenance_ok(root)); sys.exit(0)
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    sys.exit(0 if gate_v3(root) else 2)
