"""Whole-pipeline test for 381_stage13.py (rule 1, 2026-10-28): for every unit type, run the real work() loop
(claim -> compute -> save -> log line) on a 2-layer random Qwen3 with the real tokenizer and real data, in a temp ROOT,
then load every saved shard back and check its columns. Tests what dry() does not: work(), save(), the log line, np.load.
Usage: python stage13_pipeline_test.py   (CPU, ~10 min)"""
import importlib.util, inspect, sys, tempfile, textwrap
from pathlib import Path
import numpy as np

spec = importlib.util.spec_from_file_location('s13', Path(__file__).with_name('381_stage13.py')); s13 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s13)
s10, s11 = s13.s10, s13.s11
import torch, transformers, jlens

cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); tok = s10.tokenizer()
papers_all, toks_all = s11.cohort(); ctx_all = s11.contexts_of(toks_all)


class Tiny(s13.Ctx):
    def __init__(self):
        self.torch = torch; self.papers = papers_all; self.ctx = ctx_all
        self.model = jlens.from_hf(hf, tok); self.tok = tok; self.env = dict(torch=torch.__version__, gpu=[], script_sha256='pipeline-test')


s13.Ctx = Tiny
s13.XP_LAYERS, s13.PS_LAYERS, s13.LAYERS = [0, 1], [0, 1], [0, 1]
src = textwrap.dedent(inspect.getsource(s11.run_final)).replace('at=[63]', 'at=[len(model.layers) - 1]').replace('activations[63]', 'activations[len(model.layers) - 1]')
ns = dict(vars(s11)); exec(src, ns); s11.run_final = ns['run_final']; s11.PATCH_LAYERS = [0, 1]; s11.KO_LAYERS = [0, 1, 2]

real_root = s13.ROOT; tmp = Path(tempfile.mkdtemp(prefix='s13pipe_')); s13.ROOT = tmp
(tmp / 'config').mkdir(parents=True); (tmp / 'logs').mkdir()
(tmp / 'config/pairs.parquet').symlink_to(real_root / 'config/pairs.parquet')
for f in (real_root / 'config').glob('prereg*'): (tmp / 'config' / f.name).symlink_to(f)

# keep the shards small: the sampled papers of one shard, 2-3 rows each
smp, pairs = s13.sample(); sh = int(smp.shard.iloc[0]); s13._CACHE['smp'] = smp[smp.shard == sh].head(3)
c11 = s13.ctx11(Tiny()); sh11 = int(c11.smp.shard.iloc[0]); c11.smp = c11.smp[c11.smp.shard == sh11].head(2)
task_sh = int(papers_all.shard.iloc[0])
s13.do_task.__defaults__ = ([0, 1],)        # the default layer list is bound at definition time

plan = [('xf_patch', 'false_0', sh11), ('xf_patch', 'false_2', sh11), ('ko_false', 'false_0', sh11), ('task', None, task_sh),
        ('xpatch', None, sh), ('pscope', None, sh), ('para_gen', None, sh), ('para_run', None, sh)]
ok = []
def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)

for u in plan:
    if u[0] == 'para_run':                       # para_run reads para_gen's output and needs at least one accepted paraphrase
        g = dict(np.load(s13.out_path(('para_gen', None, sh)), allow_pickle=True)); g['auto_ok'][:] = True; g.pop('meta')
        np.savez(s13.out_path(('para_gen', None, sh)), meta=np.array('{}'), **g); (tmp / 'logs/para_ok').touch()
    s13.units = (lambda uu: lambda *a, **k: [uu])(u)
    class A: max_minutes = 60; ctx = None
    try:
        s13.work(A()); crashed = None
    except Exception as e:
        crashed = repr(e)
    check(f'{u} work() returned without exception', crashed is None, crashed or '')
    check(f'{u} no broken_*.json', not list((tmp / 'logs').glob('broken_*.json')), str([p.name for p in (tmp / 'logs').glob('broken_*.json')]))
    f = s13.out_path(u); check(f'{u} shard saved', f.exists(), str(f))
    if f.exists():
        try:
            d = np.load(f, allow_pickle=False); keys = d.files; n = {k: d[k].shape for k in keys if k != 'meta'}
            check(f'{u} loads without pickle', True, f'{len(keys)} arrays')
        except Exception as e:
            check(f'{u} loads without pickle', False, repr(e)); d = np.load(f, allow_pickle=True); keys = d.files; n = {}
        idc = [k for k in ('paper_id', 'row_id') if k in keys]
        check(f'{u} has an id column (paper_id or row_id)', bool(idc), str(keys[:8]))
        if idc:
            m = len(d[idc[0]]); other = {k: s for k, s in n.items() if s and s[0] != m}
            check(f'{u} {m} rows', m > 0, f'arrays not of length {m} (expected: layer lists, scalars): {other}')
print(f'PIPELINE {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}  (temp root {tmp})'); sys.exit(0 if all(ok) else 1)
