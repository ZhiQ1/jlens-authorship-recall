"""Stage 10 entry point with fix 1 (2026-10-24). Same CLI as 351_stage10.py, which stays frozen and unedited.

Fix 1: with transformers 5.x, a model that fits on a single GPU is not dispatched, so `hf.hf_device_map` does not
exist and load_model() crashed (parity job 11334054). The patched load_model reads the placement from the parameters
and buffers instead; everything else (same max_memory, never CPU offload, same jlens.from_hf) is unchanged.
Outputs still record the frozen script's sha256 (the module's __file__ is 351_stage10.py).
"""
import importlib.util, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('s10', Path(__file__).with_name('351_stage10.py'))
s10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s10)


def prefetch_weights():
    """2026-10-25: from_pretrained read the weights from /scratch at ~35 MB/s (mmap, small random reads; 25-30 min per
    job). A plain sequential read runs at ~600 MB/s, so read every shard once first; the load then hits the page cache.
    Only speed changes: the same files are loaded the same way. Any error just skips the prefetch."""
    import glob, os, time
    from concurrent.futures import ThreadPoolExecutor
    try:
        snap = sorted(glob.glob(os.path.join(os.environ.get('HF_HOME', ''), 'hub/models--Qwen--Qwen3-32B/snapshots/*/')))
        files = sorted(glob.glob(os.path.join(snap[-1], '*.safetensors'))) if snap else []
        def read(f):
            with open(f, 'rb') as h:
                while h.read(64 << 20): pass
        t = time.monotonic()
        with ThreadPoolExecutor(4) as ex: list(ex.map(read, files))
        print(f'prefetched {len(files)} weight files in {time.monotonic() - t:.0f}s', flush=True)
    except Exception as e: print('prefetch skipped:', e, flush=True)


def load_model():
    import torch, transformers, jlens
    n = torch.cuda.device_count()
    if n == 0: raise RuntimeError('no GPU visible')
    prefetch_weights()
    tok = s10.tokenizer()
    gib = [torch.cuda.get_device_properties(i).total_memory / 2**30 for i in range(n)]
    max_memory = {i: f'{int(g - (6 if i in (0, n - 1) else 3))}GiB' for i, g in enumerate(gib)}
    max_memory['cpu'] = '0GiB'
    hf = transformers.AutoModelForCausalLM.from_pretrained(s10.MODEL, revision=s10.REV, dtype=torch.bfloat16, device_map='auto',
                                                           max_memory=max_memory, low_cpu_mem_usage=True).eval()
    dm = getattr(hf, 'hf_device_map', None)
    placement = sorted({str(v) for v in dm.values()}) if dm else sorted({str(t.device) for t in [*hf.parameters(), *hf.buffers()]})
    if any(p.startswith(('cpu', 'disk', 'meta')) for p in placement): raise RuntimeError(f'model offloaded to CPU/disk: {placement}')
    print('model placement', placement, 'gpus', [torch.cuda.get_device_name(i) for i in range(n)], '(fix1)', flush=True)
    return jlens.from_hf(hf, tok), tok


s10.load_model = load_model
if __name__ == '__main__':
    import os
    if sys.argv[1:2] == ['run'] and os.environ.get('SLURM_JOB_NAME', '').startswith('s10p_') and (s10.ROOT / 'logs/pool/steal_mode').exists():
        sys.path.insert(0, str(Path(__file__).parent)); import stage10_steal  # 2026-10-25: work stealing, see stage10_steal.py
        stage10_steal.main(s10, sys.argv[1:])
    else:
        s10.main()
