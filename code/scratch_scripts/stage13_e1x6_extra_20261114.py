"""E1 + X6 at the missing layers (2026-11-14; GPU driver, approved experiment "E1 + X6 at L41-47, 49, 51").

E1 = Stage 11 tail patching (361_stage11.do_patch): at layer l, the residual stream of ALL aligned post-title positions
(common token suffix of the true and the false prompt, never reaching into either title, plus the teacher-forced name
prefix) is copied from the true-title run into the false-title run; the true first author's name tokens are scored at the
output (rank). X6 = the same with false_1..false_4 (381_stage13.do_xf_patch). This driver calls the FROZEN code, imported by
path and not edited: 381_stage13.do_xf_patch (which itself calls 361_stage11.do_patch with the tail recomputed for the false
title by the Stage 11 freeze rule). The ONLY change is the module global 361_stage11.PATCH_LAYERS, set to LAYERS for the
call and restored afterwards (do_patch reads it at call time; the patched run is one batch of len(LAYERS) elements).

LAYERS (default, 15 = the batch size of the stored E1 / X6 runs, so the patched batch has the same shape and bf16 GEMM path):
  new      [41, 42, 43, 44, 45, 46, 47, 49, 51]
  overlap  [48, 52]            (hard check against the stored E1 / X6 rows)
  pad      [40, 50, 54, 56]    (also stored -> extra overlap checks; only there to keep the batch at 15)
  -> sorted: 40 41 42 43 44 45 46 47 48 49 50 51 52 54 56.  Override: env E1X6_LAYERS="41,42,...".
Sample: the Stage 11 sample (1,186 papers, 24 shards, 361_stage11/config/sample.parquet), false_0..false_4.
Optional (needs separate approval): SAMPLE=U0 = the 600-paper R0 x uncertain re-run list (391_groups/config/rerun_U0_600.parquet,
12 shards), false_0 only.
Output (row format as the stored files: row_id, rank_true, rank_false, rank_patch [rows, len(LAYERS)], layers, false_condition, meta):
  /scratch/zhang.zhiqi2/jlens/381_stage13/raw/e1x6_extra_20261114/false_k/shard_XXX.npz   (U0: .../U0/false_0/shard_XXX.npz)
Skip-if-exists, atomic save (tmp + os.replace). Per-unit check (WARN only, never stops): for every layer also in the stored
file of the same (title, shard) [E1: 361_stage11/raw/patch, X6: 381_stage13/raw/xf_patch/false_k, U0: 391_groups/raw/patch/U0],
row ids equal, exact-equality share of rank_true / rank_false / rank_patch, max |d log10 rank|, shard R(l) difference.
Commands:
  work [--titles false_0,false_1] [--shards 0-23] [--sample s11|U0] [--max-minutes 40]
  remaining [--sample s11|U0]
  tiny --root DIR      (CPU, random Qwen3-shaped model, 64 layers so that layer ids 40-56 exist, 4 real papers of shard 0)
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R13, R391 = J / '351_stage10', J / '361_stage11', J / '381_stage13', J / '391_groups'
OUT = Path(os.environ.get('E1X6_OUT', R13 / 'raw/e1x6_extra_20261114'))
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']
NEW_LAYERS = [41, 42, 43, 44, 45, 46, 47, 49, 51]; OVERLAP = [48, 52]; PAD = [40, 50, 54, 56]
LAYERS = [int(x) for x in os.environ['E1X6_LAYERS'].split(',')] if os.environ.get('E1X6_LAYERS') else sorted(NEW_LAYERS + OVERLAP + PAD)
SAMPLES = {'s11': (R11 / 'config/sample.parquet', 24, TITLES), 'U0': (R391 / 'config/rerun_U0_600.parquet', 12, ['false_0'])}
FROZEN = {'361_stage11.py': H / '11_stage11/361_stage11.py', '381_stage13.py': H / '13_stage13/381_stage13.py'}


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


_M = {}
def m13():
    if 'm13' not in _M:
        sp = importlib.util.spec_from_file_location('s13_e1x6', FROZEN['381_stage13.py']); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _M['m13'] = m
    return _M['m13']


def out_path(u, root=None):
    sample, title, shard = u; base = Path(root or OUT)
    return (base / title if sample == 's11' else base / sample / title) / f'shard_{shard:03d}.npz'


def stored_path(u):
    sample, title, shard = u
    if sample == 'U0': return R391 / 'raw/patch/U0' / f'shard_{shard:03d}.npz'
    return (R11 / 'raw/patch' if title == 'false_0' else R13 / 'raw/xf_patch' / title) / f'shard_{shard:03d}.npz'


def parse_shards(s, n):
    if not s or s == 'all': return list(range(n))
    out = []
    for part in s.split(','):
        if '-' in part: a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return out


def all_units(sample='s11', titles=None, shards=None):
    _, n, tt = SAMPLES[sample]
    titles = [t for t in (titles or tt) if t in tt]
    return [(sample, t, k) for t in titles for k in parse_shards(shards, n)]


# ------------------------------------------------------------------ compute
def compute(C, u, smp_override=None):
    """frozen 381_stage13.do_xf_patch with 361_stage11.PATCH_LAYERS = LAYERS (restored afterwards)."""
    import pandas as pd
    m = m13(); s11 = m.s11; sample, title, shard = u
    c = m.ctx11(C)                                                     # cached Stage 11 context around C.model
    base_smp = c.smp
    if smp_override is not None: c.smp = smp_override
    elif sample == 'U0': c.smp = pd.read_parquet(SAMPLES['U0'][0])
    old = s11.PATCH_LAYERS; s11.PATCH_LAYERS = list(LAYERS)
    try: d = m.do_xf_patch(C, title, shard)
    finally: s11.PATCH_LAYERS = old; c.smp = base_smp
    assert s11.PATCH_LAYERS == old and s11.FALSE_FOR_PATCH == 'false_0'
    return d


def unit_check(u, d, stored=None, tk=None):
    """WARN-only comparison of the overlap layers with the stored file of the same unit."""
    import pandas as pd
    f = Path(stored) if stored else stored_path(u)
    if not f.exists(): return dict(status='NO_STORED', file=str(f))
    z = np.load(f); ly_new = [int(x) for x in d['layers']]; ly_old = [int(x) for x in z['layers']]
    ov = [l for l in ly_new if l in ly_old]
    r = dict(file=str(f), overlap_layers=ov, rows_match=bool(len(d['row_id']) == len(z['row_id']) and (d['row_id'] == z['row_id']).all()))
    if not r['rows_match']: r['status'] = 'WARN'; return r
    r['eq_true'] = float((d['rank_true'] == z['rank_true']).mean()); r['eq_false'] = float((d['rank_false'] == z['rank_false']).mean())
    r['max_dnlr_true_false'] = float(max(np.abs(nlr(d['rank_true']) - nlr(z['rank_true'])).max(), np.abs(nlr(d['rank_false']) - nlr(z['rank_false'])).max()))
    if tk is None: tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    pid = tk.loc[d['row_id']].paper_id.to_numpy()
    def R(rt, rf, rp):
        df = pd.DataFrame({'p': pid, 'n': nlr(rp) - nlr(rf), 'd': nlr(rt) - nlr(rf)}).groupby('p').mean(); return float(df.n.mean() / df.d.mean())
    per = {}
    for l in ov:
        a, b = d['rank_patch'][:, ly_new.index(l)], z['rank_patch'][:, ly_old.index(l)]
        per[l] = dict(eq=float((a == b).mean()), max_dnlr=float(np.abs(nlr(a) - nlr(b)).max()),
                      dR=R(d['rank_true'], d['rank_false'], a) - R(z['rank_true'], z['rank_false'], b))
    r['per_layer'] = per
    ok = r['eq_true'] >= 0.99 and r['eq_false'] >= 0.99 and all(v['eq'] >= 0.99 and abs(v['dR']) <= 0.005 for v in per.values())
    r['status'] = 'OK' if ok else 'WARN'; return r


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **d); os.replace(tmp, f)


class Ctx:
    def __init__(self):
        import torch
        m = m13(); s10 = m.s10
        self.torch = torch; self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                        driver_sha256=sha(__file__), frozen_sha256={k: sha(v) for k, v in FROZEN.items()}, layers=LAYERS)


def work(a, C=None, root=None):
    import pandas as pd
    t0 = time.monotonic(); budget = a.max_minutes or 40
    left = m13().s11.slurm_minutes_left()
    if left is not None and left - 4 < budget: budget = left - 4
    us = all_units(a.sample, a.titles.split(',') if a.titles else None, a.shards)
    log('e1x6 work: units', len(us), 'layers', LAYERS, 'budget', f'{budget:.1f} min', 'out', root or OUT)
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id'); worst = 0; done = 0
    for u in us:
        f = out_path(u, root)
        if f.exists(): log('skip (exists)', u); continue
        if C is not None and done and (time.monotonic() - t0) / 60 + 1.3 * worst / 60 > budget: log('time budget reached before', u); break
        if C is None: C = Ctx()
        t1 = time.monotonic(); d = compute(C, u, getattr(a, 'smp_override', None))
        try: chk = unit_check(u, d, getattr(a, 'stored_override', {}).get(u) if hasattr(a, 'stored_override') else None, tk)
        except Exception as ex: chk = dict(status='WARN', note=f'check crashed: {ex!r}')
        save(f, d, dict(unit=list(u), created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=chk, **C.env))
        dt = time.monotonic() - t1; worst = max(worst, dt); done += 1
        log(f'e1x6 {u[0]} {u[1]} shard {u[2]:03d} rows={len(d["row_id"])} {dt:.0f}s total={(time.monotonic() - t0) / 60:.1f}min CHECK {chk.get("status")}',
            json.dumps({k: chk[k] for k in chk if k in ('eq_true', 'eq_false', 'per_layer', 'rows_match', 'note')}))
    miss = remaining(a, root)
    return miss


def remaining(a=None, root=None):
    sample = getattr(a, 'sample', 's11') or 's11'
    us = all_units(sample, a.titles.split(',') if a is not None and getattr(a, 'titles', None) else None, getattr(a, 'shards', None))
    miss = [u for u in us if not out_path(u, root).exists()]
    print(f'REMAINING {len(miss)} of {len(us)} ({sample})', flush=True); return miss


# ------------------------------------------------------------------ CPU tiny test
def tiny(a):
    import torch, transformers, jlens, pandas as pd
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True); m = m13(); s10, s11 = m.s10, m.s11
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok); C.env = {'tiny': True, 'layers': LAYERS}
    smp = pd.read_parquet(SAMPLES['s11'][0])
    pick = pd.concat([smp[(smp.shard == 0) & (smp.group == g)].head(2) for g in ('target', 'control')])
    raw = root / 'raw'; ok = {}
    # 1) "stored" analogue: the frozen code path with the ORIGINAL 15 layers on the same 4 papers (E1 via do_patch, X6 via do_xf_patch)
    c = m.ctx11(C); full = c.smp; c.smp = pick
    stored = {}
    for t in ['false_0', 'false_1']:
        d0 = s11.do_patch(c, 0) if t == 'false_0' else m.do_xf_patch(C, t, 0)
        p = root / 'stored' / t / 'shard_000.npz'; save(p, d0, {'tiny_stored': True}); stored[('s11', t, 0)] = p
    c.smp = full
    ok['frozen PATCH_LAYERS untouched'] = s11.PATCH_LAYERS == [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63]
    # 2) driver work() on false_0 + false_1, shard 0, 4 papers
    A = argparse.Namespace(sample='s11', titles='false_0,false_1', shards='0', max_minutes=30, smp_override=pick, stored_override=stored)
    work(A, C=C, root=raw)
    f0, f1 = out_path(('s11', 'false_0', 0), raw), out_path(('s11', 'false_1', 0), raw)
    ok['output files written'] = f0.exists() and f1.exists()
    z0, z1 = np.load(f0), np.load(f1); st0 = np.load(stored[('s11', 'false_0', 0)])
    ok['row format = stored (keys)'] = set(z0.files) == set(np.load(R13 / 'raw/xf_patch/false_1/shard_000.npz').files)
    ok['layer list honoured'] = [int(x) for x in z0['layers']] == LAYERS and z0['rank_patch'].shape[1] == len(LAYERS)
    ok['PATCH_LAYERS restored after work'] = s11.PATCH_LAYERS == [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63] and s11.FALSE_FOR_PATCH == 'false_0'
    ok['rows = stored rows'] = bool((z0['row_id'] == st0['row_id']).all())
    meta = json.loads(str(z0['meta'])); ok['unit check ran, overlap layers found'] = sorted(int(k) for k in meta['check'].get('per_layer', {})) == sorted(set(LAYERS) & set(s11.PATCH_LAYERS))
    ok['fp32 tiny: overlap ranks identical to frozen 15-layer run'] = meta['check'].get('status') == 'OK'
    ok['false_1 differs from false_0 (title changes the run)'] = not np.array_equal(z1['rank_false'], z0['rank_false'])
    # 3) skip-if-done
    mt = f0.stat().st_mtime; work(A, C=C, root=raw); ok['skip-if-done (mtime unchanged)'] = f0.stat().st_mtime == mt
    # 4) the U0 path (sample switch) on 2 papers
    u0 = pd.read_parquet(SAMPLES['U0'][0]); u0p = u0[u0.shard == 0].head(2)
    B_ = argparse.Namespace(sample='U0', titles='false_0', shards='0', max_minutes=30, smp_override=u0p, stored_override={})
    work(B_, C=C, root=raw); ok['U0 output written'] = out_path(('U0', 'false_0', 0), raw).exists()
    ok = {k: bool(v) for k, v in ok.items()}
    for k, v in ok.items(): print('E1X6 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    res = all(ok.values()); print('E1X6 TINY DRIVER', 'PASS' if res else 'FAIL', flush=True); return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny'])
    ap.add_argument('--titles'); ap.add_argument('--shards'); ap.add_argument('--sample', default='s11', choices=list(SAMPLES))
    ap.add_argument('--max-minutes', type=float, default=40); ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'remaining': remaining(a); return
    work(a)


if __name__ == '__main__':
    main()
