"""Stage 11 pre-GPU check with the REAL Qwen3-32B weights and the real public lens, on CPU (2026-10-26).
Runs E1 patch, E2 knockout and E3 chain through the exact Stage 11 code for the sample paper with the fewest name tokens,
into a scratch root (never the real one), and checks: no exception; shapes; patch at L63 == true exactly; knockout
explicit-mask baseline == unmasked run on the same device; knockout from L0 lowers the score; chain first author ==
isolated context on the same device. Agreement with the Stage 10 (GPU) ranks is reported for information only:
CPU and GPU bf16 kernels round differently."""
import json, os, sys, time, importlib.util
from pathlib import Path
import numpy as np, torch, transformers

OUT = Path(sys.argv[1]); sys.argv = sys.argv[:1]
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D))
sp = importlib.util.spec_from_file_location('s11', D / '361_stage11.py'); s11 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s11)
REAL = s11.ROOT
OUT.mkdir(parents=True, exist_ok=True); (OUT / 'config').mkdir(exist_ok=True)
for f in ('sample.parquet', 'protocol.json'): (OUT / 'config' / f).write_bytes((REAL / 'config' / f).read_bytes())
s11.ROOT = OUT
torch.set_num_threads(int(os.environ.get('SLURM_CPUS_PER_TASK', '8')))
t0 = time.time()
import jlens
tok = s11.s10.tokenizer()
hf = transformers.AutoModelForCausalLM.from_pretrained(s11.s10.MODEL, revision=s11.s10.REV, dtype=torch.bfloat16, device_map='cpu', low_cpu_mem_usage=True).eval()
model = jlens.from_hf(hf, tok); print('model on cpu', round(time.time() - t0), 's, attn', hf.config._attn_implementation, flush=True)
s11.s10.load_model = lambda: (model, tok)
res = []
def check(n, ok, d=''): res.append(bool(ok)); print('PASS' if ok else 'FAIL', n, d, flush=True)
C = s11.Ctx(); print('ctx (real lens on cpu)', round(time.time() - t0), 's', flush=True)
ntok = {pid: sum(len(x[2]) for x in v) for pid, v in C.ctx.items()}
pid = min(C.smp.paper_id, key=lambda p: (ntok[p], len(C.P.loc[p].prompt_ids)))
C.smp = C.smp[C.smp.paper_id == pid].assign(shard=0); print('paper', pid, 'name tokens', ntok[pid], flush=True)
t1 = time.time(); p = s11.compute(C, ('patch', None, 0)); print('patch', round(time.time() - t1), 's', flush=True)
i63 = s11.PATCH_LAYERS.index(63); n = len(p['row_id'])
check('E1 shapes', p['rank_patch'].shape == (n, len(s11.PATCH_LAYERS)) and (p['rank_patch'] >= 1).all(), f'{n} rows')
check('E1 patch at L63 == true (exact)', (p['rank_patch'][:, i63] == p['rank_true']).all())
nl = lambda r: -np.log10(np.asarray(r, float))
print('   E1 log10(1/rank) true', nl(p['rank_true']).mean().round(3), 'false', nl(p['rank_false']).mean().round(3),
      'patched by layer', dict(zip(s11.PATCH_LAYERS, nl(p['rank_patch']).mean(0).round(3))), flush=True)
t1 = time.time(); k = s11.compute(C, ('knockout', None, 0)); print('knockout', round(time.time() - t1), 's', flush=True)
i64 = s11.KO_LAYERS.index(64)
check('E2 explicit-mask baseline == unmasked true (same device)', (k['rank_ko'][:, i64] == p['rank_true']).mean() >= .9, f"{(k['rank_ko'][:, i64] == p['rank_true']).mean():.2f}")
check('E2 knockout from L0 lowers the score', nl(k['rank_ko'][:, i64]).mean() > nl(k['rank_ko'][:, 0]).mean(),
      f"{nl(k['rank_ko'][:, i64]).mean():.3f} -> {nl(k['rank_ko'][:, 0]).mean():.3f}")
print('   E2 by start layer', dict(zip(s11.KO_LAYERS, nl(k['rank_ko']).mean(0).round(3))), flush=True)
sh = int(C.papers[C.papers.paper_id == pid].shard.iloc[0]); C.papers = C.papers[C.papers.paper_id == pid]
t1 = time.time(); ch = s11.compute(C, ('chain', 'true', sh)); print('chain', round(time.time() - t1), 's', flush=True)
check('E3 all readout columns', all(f'{r}@{l}' in ch for r, l in s11.CHAIN_PLAN), f'{len(ch["row_id"])} rows')
ai, rids, name = C.ctx[pid][0]; pr = C.prompts['true'][pid][1]
iso = s11.s10.fast_readout(model, C.L, pr + name[:-1], [len(pr) - 1 + j for j in range(len(name))], [('final', 63), ('jlens_public', 56)], torch)
first = np.isin(ch['row_id'], rids)
for key, rl in (('final@63', ('final', 63)), ('jlens_public@56', ('jlens_public', 56))):
    ri = s11.ranks(iso[rl], torch.tensor(name), torch)
    check(f'E3 first author in chain == isolated ({key}, same device)', (ri == ch[key][first]).mean() >= .9, f'{(ri == ch[key][first]).mean():.2f}')
z = np.load(s11.s10.out_file(s11.R10, 'final', 63, sh, 'true')); ref = dict(zip(z['row_id'], z['rank']))
print('   info: agreement with Stage 10 GPU ranks (final, true title):', f"{np.mean([ref[r] == x for r, x in zip(p['row_id'], p['rank_true'])]):.2f}",
      'mean |dlog10 rank|', f"{np.mean([abs(nl(ref[r]) - nl(x)) for r, x in zip(p['row_id'], p['rank_true'])]):.3f}", flush=True)
print(f'REALCHECK {"PASS" if all(res) else "FAIL"} {sum(res)}/{len(res)}  total {round(time.time() - t0)} s')
