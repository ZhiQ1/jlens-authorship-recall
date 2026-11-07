import os, sys, json, time, hashlib, shutil, argparse
from pathlib import Path

BASE = Path('/scratch') / os.environ['USER'] / 'jlens'
sys.path.insert(0, str(BASE))
import stage9_fullfit as f

SKIP_INDEX = 66
TOTAL = 100
LAYERS = [16, 24, 32, 40, 48, 56, 62]

def prepare():
    m = f.load_runner()
    a, cfg, prompts = f.get_environment(m, 'A')
    out = m.target(a)
    cp = out / 'checkpoint.pt'

    if not cp.exists():
        raise RuntimeError('Original Fit A checkpoint missing')
    if f.read_json(out / 'fitting_config.json') != cfg:
        raise RuntimeError('Frozen configuration mismatch')
    if not (out / 'scheduler_protocol.json').is_file():
        raise RuntimeError('Original scheduler protocol missing')
    f.pin_protocol(out, f.configuration(), cfg)

    import torch
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(
        cfg['model'], revision=cfg['revision']
    )
    lengths = [
        min(len(tok.encode(t)), 128)
        for t in prompts
    ]
    skipped = [i for i, n in enumerate(lengths) if n <= 17]

    if skipped != [SKIP_INDEX] or lengths[SKIP_INDEX] != 14:
        raise RuntimeError(
            f'Unexpected short prompts: {skipped}, '
            f'index66 length={lengths[SKIP_INDEX]}'
        )

    state = m.load_old().verify_checkpoint(cp, cfg)
    next_idx = int(state['next_idx'])
    n_done = int(state['n_done'])
    expected = next_idx - int(SKIP_INDEX < next_idx)

    if not 0 <= next_idx <= TOTAL or n_done != expected:
        raise RuntimeError(
            f'Checkpoint count mismatch: next={next_idx}, '
            f'n_done={n_done}, expected={expected}'
        )

    print('SKIP-AWARE AUDIT PASS', json.dumps({
        'next_idx': next_idx,
        'n_done': n_done,
        'skipped_index': SKIP_INDEX,
        'skipped_token_length': 14,
        'remaining': TOTAL-next_idx,
        'checkpoint_sha256': f.sha(cp)
    }), flush=True)

    del state
    return m, cfg, prompts, out, cp, next_idx

def verify_final(m, cfg, out, cp):
    import torch
    import jlens

    st = m.load_old().verify_checkpoint(cp, cfg)

    if st['next_idx'] != 100 or st['n_done'] != 99:
        raise RuntimeError('Final checkpoint must be 100 attempted / 99 valid')

    lens_path = out / 'lens.pt'
    if not lens_path.exists():
        raise RuntimeError('Final lens file missing')

    lens = jlens.JacobianLens.load(str(lens_path))
    if lens.n_prompts != 99:
        raise RuntimeError('Saved lens effective prompt count is not 99')
    if set(lens.jacobians) != set(LAYERS):
        raise RuntimeError('Saved lens layers mismatch')

    checks = {}
    for layer in LAYERS:
        ref = st['jacobian_sum'][layer].float() / 99
        actual = lens.jacobians[layer].detach().float().cpu()
        if ref.shape != (5120, 5120) or actual.shape != ref.shape:
            raise RuntimeError(f'Layer {layer}: matrix shape mismatch')
        if not torch.isfinite(ref).all() or not torch.isfinite(actual).all():
            raise RuntimeError(f'Layer {layer}: nonfinite matrix')
        relative_error = (actual-ref).norm().item() / max(ref.norm().item(), 1e-12)
        if relative_error > 0.01:
            raise RuntimeError(f'L{layer}: relative error {relative_error}')
        checks[str(layer)] = relative_error
        del ref, actual

    marker = {
        'status': 'FIT_SAVED_AND_RELOADED_NUMERICALLY_VERIFIED_SKIP_AWARE',
        'half': 'A',
        'attempted_prompts': 100,
        'valid_prompts': 99,
        'skipped_indices_zero_based': [66],
        'skipped_reason': 'tokenized length 14 <= 17',
        'source_layers': LAYERS,
        'checkpoint_sha256': f.sha(cp),
        'lens_sha256': f.sha(lens_path),
        'fit_config_sha256': f.sha(out / 'fitting_config.json'),
        'relative_l2_errors': checks
    }
    f.atomic_json(out / 'fit_status_skipaware.json', marker)
    print('FIT A VERIFIED: attempted=100 valid=99 skipped=[66]', flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['check', 'run'])
    p.add_argument('--confirm-fit', action='store_true')
    args = p.parse_args()

    m, cfg, prompts, out, cp, done = prepare()

    if args.command == 'check':
        return
    if not args.confirm_fit:
        raise RuntimeError('GPU run requires --confirm-fit')
    if not os.environ.get('SLURM_JOB_ID'):
        raise RuntimeError('Run only inside the allocated GPU Slurm job')

    if done == 100:
        verify_final(m, cfg, out, cp)
        return

    original = cp.with_name('checkpoint.before_skipaware.pt')
    if not original.exists():
        shutil.copy2(cp, original)
    print('ORIGINAL CHECKPOINT BACKUP:', original, flush=True)

    if (out / 'lens.pt').exists() or (out / 'fit_status.json').exists():
        raise RuntimeError('Unexpected existing final artifacts')

    import torch
    import transformers
    import jlens
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        force=True
    )

    print('RESUMING FIT A:', done, '-> 100, valid target=99', flush=True)
    tok = transformers.AutoTokenizer.from_pretrained(
        cfg['model'], revision=cfg['revision']
    )
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        cfg['model'],
        revision=cfg['revision'],
        torch_dtype=torch.bfloat16,
        device_map='auto',
        max_memory={0: '55GiB', 'cpu': '36GiB'},
        low_cpu_mem_usage=True
    )
    model = jlens.from_hf(hf, tok)

    lens = jlens.fit(
        model, prompts,
        source_layers=LAYERS,
        target_layer=63,
        dim_batch=1,
        max_seq_len=128,
        skip_first=16,
        checkpoint_path=str(cp),
        checkpoint_every=1,
        resume=True
    )

    if lens.n_prompts != 99:
        raise RuntimeError(f'Expected 99 valid prompts, got {lens.n_prompts}')

    st = m.load_old().verify_checkpoint(cp, cfg)
    if st['next_idx'] != 100 or st['n_done'] != 99:
        raise RuntimeError('Final checkpoint counters invalid')
    del st, model, hf, tok
    lens.save(str(out / 'lens.pt'))
    del lens

    verify_final(m, cfg, out, cp)

if __name__ == '__main__':
    main()
