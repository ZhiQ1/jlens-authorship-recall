"""Stage 12 on V100 nodes (2026-10-28, user-approved): the A100-80GB nodes are full, so the forward-only prior units
(prior_mc, prior_pure) also run on 3 x V100-SXM2-32GB, with the model split across the GPUs (device_map='auto', same
bf16 weights, same prompts, same scoring code as 371_stage12.py). The author-lens fit and alens_read stay on A100.
Each output records the GPU names in its meta, so V100 and A100 shards can be told apart in the analysis.

  smoke : recompute prior_mc delete shard 0 (already done on A100) and compare; WARN only, never stops
  work  : the 371_stage12 work loop restricted to prior_mc / prior_pure; never claims the fit
"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np

DIR = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('s12', DIR / '371_stage12.py'); s12 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s12)
TYPES = ('prior_mc', 'prior_pure')
_units = s12.units
s12.units = lambda: [u for u in _units() if u[0] in TYPES]
_claim = s12.s11.claim
s12.s11.claim = lambda d, me: False if Path(d).name == 'alens_fit' else _claim(d, me)


def smoke():
    t0 = time.monotonic(); C = s12.s11.Ctx(); print('ctx', C.env, f'{time.monotonic() - t0:.0f}s', flush=True)
    for u in (('prior_mc', 'delete', 0), ('prior_pure', None, 0)):
        t1 = time.monotonic(); d = s12.compute(C, u); dt = time.monotonic() - t1
        ref = s12.out_path(u)
        rep = dict(unit=list(u), seconds=round(dt), rows=len(d['row_id']), gpu=C.env.get('gpu'))
        if ref.exists():
            z = np.load(ref)
            if u[0] == 'prior_mc':
                a, b = np.asarray(z['mean_nlr'], float), np.asarray(d['mean_nlr'], float)
                same = len(a) == len(b) and (z['paper_id'] == d['paper_id']).all()
                rep |= dict(rows_match=bool(same), max_abs_diff=float(np.abs(a - b).max()) if same else None, mean_abs_diff=float(np.abs(a - b).mean()) if same else None,
                            corr=float(np.corrcoef(a, b)[0, 1]) if same else None)
            rep['status'] = 'PASS' if rep.get('rows_match') and rep['max_abs_diff'] < 0.05 else 'WARN'
        else:
            vals = [np.asarray(v) for k, v in d.items() if '@' in k]
            rep |= dict(status='PASS' if vals and all(len(v) == len(d['row_id']) and (v >= 1).all() for v in vals) else 'WARN', note='no A100 reference; shape/rank sanity only')
        print('SMOKE', json.dumps(rep), flush=True)
        (s12.ROOT / 'logs').mkdir(exist_ok=True); open(s12.ROOT / 'logs/v100_smoke.jsonl', 'a').write(json.dumps(rep) + '\n')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'smoke': smoke()
    elif cmd == 'work':
        class A: max_minutes = float(sys.argv[2]) if len(sys.argv) > 2 else 110; fit = False
        s12.work(A())
