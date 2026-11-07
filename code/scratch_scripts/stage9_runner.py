"""Stage9 immutable fitting runner. Keep 351_stage9.py unchanged."""
import argparse, hashlib, importlib.util, json, os, shutil, sys, time
from pathlib import Path

BASE = Path('/scratch') / os.environ.get('USER', '') / 'jlens'
ROOT = BASE / '351_stage9'
OLD = BASE / '351_stage9.py'


def load_old():
    spec = importlib.util.spec_from_file_location('stage9_legacy', OLD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    with open(tmp, 'x') as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(p): return json.loads(p.read_text())


def frozen(m, a):
    m.audit(a)
    rows = [json.loads(x) for x in (ROOT / 'prompts' / ('fit_' + a.half + '.jsonl')).read_text().splitlines() if x.strip()]
    assert 1 <= a.total <= len(rows)
    ids = [r['text_sha256'] for r in rows[:a.total]]
    assert all(hashlib.sha256(r['text'].encode()).hexdigest() == r['text_sha256'] for r in rows[:a.total])
    cfg = dict(half=a.half, n_fit=a.total, prompt_ids=ids, source_layers=a.layers,
               target_layer=63, dim_batch=a.dim_batch, max_seq_len=128, skip_first=16,
               model=m.MODEL, revision=m.REVISION,
               split_manifest_sha256=digest(ROOT / 'config' / 'manifest.json'))
    return cfg, [r['text'] for r in rows[:a.total]]


def target(a):
    if not a.run_id.isascii() or not a.run_id or not all(c.isalnum() or c in '-_' for c in a.run_id):
        raise ValueError('run-id must contain only letters, digits, - or _')
    return ROOT / 'runner_runs' / a.run_id


def inspect_checkpoint(m, path, cfg):
    st = m.verify_checkpoint(path, cfg)
    if not (0 <= st['next_idx'] <= cfg['n_fit'] and st['n_done'] == st['next_idx']):
        raise RuntimeError('Incomplete/skipped prompts: require n_done == next_idx')
    return st


def seed(a, m, cfg):
    if a.total != 3 or a.half != 'A' or a.layers != [48, 56]:
        raise RuntimeError('Seed protocol only supports A, total=3, layers 48 56')
    source = ROOT / 'fits' / 'A_n0002_layers_48-56'
    oldcfg = read_json(source / 'fitting_config.json')
    marker = read_json(source / 'fit_status.json')
    if marker.get('checkpoint_sha256') != digest(source / 'checkpoint.pt') or marker.get('fit_config_sha256') != digest(source / 'fitting_config.json'):
        raise RuntimeError('Source verified hashes changed')
    for key in cfg:
        if key not in ('n_fit', 'prompt_ids') and cfg[key] != oldcfg.get(key):
            raise RuntimeError('Seed configuration mismatch: ' + key)
    if oldcfg['n_fit'] != 2 or cfg['prompt_ids'][:2] != oldcfg['prompt_ids']:
        raise RuntimeError('Prompt prefix mismatch')
    st = inspect_checkpoint(m, source / 'checkpoint.pt', oldcfg)
    if (st['n_done'], st['next_idx']) != (2, 2): raise RuntimeError('Source not 2/2')
    out = target(a)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / 'fitting_config.json', cfg)
    shutil.copy2(source / 'checkpoint.pt', out / 'checkpoint.pt')
    write_json(out / 'seed_provenance.json', dict(seed_checkpoint_sha256=digest(out / 'checkpoint.pt'),
                prefix_prompt_ids=cfg['prompt_ids'][:2], config_sha256=digest(out / 'fitting_config.json')))
    print('SEED READY:', out, 'next_idx=2', flush=True)


def validate_existing(a, m, out, cfg):
    if read_json(out / 'fitting_config.json') != cfg: raise RuntimeError('Run configuration changed')
    st = inspect_checkpoint(m, out / 'checkpoint.pt', cfg)
    if (out / 'seed_provenance.json').exists():
        proof = read_json(out / 'seed_provenance.json')
        if proof['config_sha256'] != digest(out / 'fitting_config.json') or proof['prefix_prompt_ids'] != cfg['prompt_ids'][:2]:
            raise RuntimeError('Seed provenance mismatch')
        if st['next_idx'] == 2 and proof['seed_checkpoint_sha256'] != digest(out / 'checkpoint.pt'):
            raise RuntimeError('Seed checkpoint modified before continuation')
        if st['next_idx'] < 2: raise RuntimeError('Seed checkpoint rewound')
    return st


def run(a, m, cfg, prompts):
    out = target(a)
    out.mkdir(parents=True, exist_ok=True)
    checkpoint = out / 'checkpoint.pt'
    status = out / 'fit_status.json'
    if status.exists():
        m.verify_saved_fit(out, cfg, write_marker=False)
        x = read_json(status)
        if x['checkpoint_sha256'] != digest(checkpoint): raise RuntimeError('Completed checkpoint modified')
        print('ALREADY VERIFIED; no GPU work', out)
        return
    if (out / 'lens.pt').exists():
        m.verify_saved_fit(out, cfg)
        return
    if (out / 'fitting_config.json').exists():
        if checkpoint.exists():
            st = validate_existing(a, m, out, cfg)
            print('RESUME next_idx=', st['next_idx'], 'n_done=', st['n_done'], flush=True)
        elif read_json(out / 'fitting_config.json') != cfg:
            raise RuntimeError('Configuration changed before first checkpoint')
        else:
            print('NO CHECKPOINT YET; starting frozen run from zero', flush=True)
    elif checkpoint.exists():
        raise RuntimeError('Unbound checkpoint')
    else:
        write_json(out / 'fitting_config.json', cfg)
        print('NEW RUN, target=', cfg['n_fit'], flush=True)
    if not a.confirm_fit: raise RuntimeError('GPU computation requires --confirm-fit')
    import torch, transformers, jlens
    tokenizer = transformers.AutoTokenizer.from_pretrained(m.MODEL, revision=m.REVISION)
    model_hf = transformers.AutoModelForCausalLM.from_pretrained(m.MODEL, revision=m.REVISION,
                       torch_dtype=torch.bfloat16, device_map='auto', low_cpu_mem_usage=True)
    model = jlens.from_hf(model_hf, tokenizer)
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
    lens = jlens.fit(model, prompts, source_layers=a.layers, target_layer=63,
                    dim_batch=a.dim_batch, max_seq_len=128, skip_first=16,
                    checkpoint_path=str(checkpoint), checkpoint_every=1,
                    resume=checkpoint.exists())
    state = inspect_checkpoint(m, checkpoint, cfg)
    if (state['n_done'], state['next_idx']) != (a.total, a.total) or lens.n_prompts != a.total:
        raise RuntimeError('Fit did not complete all prompts')
    if set(lens.jacobians) != set(a.layers): raise RuntimeError('Lens layer mismatch')
    lens.save(str(out / 'lens.pt'))
    m.verify_saved_fit(out, cfg)
    print('RUN COMPLETE', out, flush=True)


def compare(a, m, cfg):
    import torch
    r = ROOT / 'runner_runs' / 'resume_A3'
    u = ROOT / 'runner_runs' / 'fresh_A3'
    for out in (r, u):
        if not (out / 'fit_status.json').is_file(): raise RuntimeError('Missing completed fit '+str(out))
        validate_existing(a, m, out, cfg)
        m.verify_saved_fit(out, cfg, write_marker=False)
        status = read_json(out / 'fit_status.json')
        if status['checkpoint_sha256'] != digest(out / 'checkpoint.pt'): raise RuntimeError('Checkpoint hash changed')
        if status['fit_config_sha256'] != digest(out / 'fitting_config.json'): raise RuntimeError('Fit configuration hash changed')
    if not (r / 'seed_provenance.json').exists(): raise RuntimeError('Resume provenance missing')
    x = inspect_checkpoint(m, r / 'checkpoint.pt', cfg)
    y = inspect_checkpoint(m, u / 'checkpoint.pt', cfg)
    if (x['next_idx'], y['next_idx']) != (3, 3): raise RuntimeError('Expected both 3/3')
    result = {}
    for l in a.layers:
        xr = x['jacobian_sum'][l].float() / 3
        yr = y['jacobian_sum'][l].float() / 3
        e = (xr - yr).norm().item() / max(yr.norm().item(), 1e-12)
        if not (e <= a.tolerance): raise RuntimeError(f'Layer {l} relative L2={e} > {a.tolerance}')
        result[str(l)] = e
    print('RESUME COMPARE PASS', result, flush=True)
    write_json(ROOT / 'reports' / 'stage9_resume_comparison.json', dict(status='PASS', layers=result, tolerance=a.tolerance))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['seed','run','compare','check'])
    p.add_argument('--run-id',default='resume_A3')
    p.add_argument('--half',choices=['A','B'],default='A')
    p.add_argument('--total',type=int,default=3)
    p.add_argument('--layers',type=int,nargs='+',default=[48,56])
    p.add_argument('--dim-batch',type=int,default=1)
    p.add_argument('--confirm-fit',action='store_true')
    p.add_argument('--tolerance',type=float,default=1e-3)
    a=p.parse_args()
    a.root=ROOT
    if len(a.layers)!=len(set(a.layers)) or any(l<0 or l>=63 for l in a.layers): raise ValueError('Invalid layers')
    m=load_old()
    cfg,prompts=frozen(m,a)
    if a.command=='seed': seed(a,m,cfg)
    elif a.command=='run': run(a,m,cfg,prompts)
    elif a.command=='compare': compare(a,m,cfg)
    elif a.command=='check':
        out=target(a)
        st=validate_existing(a,m,out,cfg)
        print('CHECKPOINT OK',out,'n_done',st['n_done'],'next_idx',st['next_idx'])

if __name__=='__main__': main()
