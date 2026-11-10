"""Item 2-1, user decision 2026-11-09: re-run ONLY Fit B prompt 66 with the ORIGINAL Fit B code path, to full precision.

Original path (frozen /scratch/zhang.zhiqi2/jlens/stage9_fullfit.py `run --half B`, used for prompts 1-66):
  m = load_runner(); a, cfg, prompts = get_environment(m, 'B')   (frozen audit of runner/split/prompt hashes)
  from_pretrained(bf16, device_map='auto', max_memory={0: '55GiB', 'cpu': '36GiB'}, low_cpu_mem_usage=True); jlens.from_hf
  jlens.fit(model, prompts[:66], source_layers=LAYERS, target_layer=63, dim_batch=1, max_seq_len=128, skip_first=16,
            checkpoint_path=<cp>, checkpoint_every=1, resume=True)
Here the frozen module is imported by path and its helpers are called unchanged; the loader line and the jlens.fit call are the same
arguments. The checkpoint is a NEW file in a NEW directory: the backup state (checkpoint_B066.pt, read only) with n_done = next_idx = 65,
so jlens.fit resumes at index 65 and computes exactly prompt 66 (its logged max_d_mean then uses S66/65 as the running mean, so it is
not the original quantity; the original-definition d_mean is computed below with S65 = S66 - J). jacobian_for_prompt is wrapped by an
observer that only keeps a reference to the returned J (no change to the computation) so the norm can be reported to full precision,
computed exactly as jlens.fit does (fp32 .norm().item() / sqrt(d)) and in float64.
Outputs: /scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb_orig66/ (never the run directory, never checkpoint_B066.*).
"""
import hashlib, importlib.util, json, math, os, sys, time
from datetime import datetime
from pathlib import Path

BASE = Path('/scratch/zhang.zhiqi2/jlens'); FULLFIT = BASE / 'stage9_fullfit.py'
BK = BASE / '381_stage13/b2_fitb/checkpoint_B066.pt'; BKJ = BASE / '381_stage13/b2_fitb/checkpoint_B066.json'
OUT = BASE / '381_stage13/b2_fitb_orig66'; N_CK = 66
REF = dict(norm=4.367, d_mean=0.108, seq_len=128, n_valid=111)          # original log line of prompt 66
NEWCODE = 4.378043340693925                                             # gate (stage9_b2_fitb_v2/v3) value, job 11753858


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()


def log(*x): print(datetime.now().isoformat(timespec='seconds'), *x, flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True); res = OUT / 'orig66_result.json'
    if res.exists(): log('result exists, nothing to do:', res); return 0
    if sha(BK) != json.loads(BKJ.read_text())['sha256']: raise SystemExit('backup checkpoint sha256 changed')
    sp = importlib.util.spec_from_file_location('stage9_fullfit_frozen', FULLFIT); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
    m = F.load_runner(); a, cfg, prompts = F.get_environment(m, 'B')
    run_cfg = json.loads((BASE / '351_stage9/runner_runs/full_B_100_7layers/fitting_config.json').read_text())
    if run_cfg != cfg: raise SystemExit('frozen config differs from the run directory config')
    import torch, transformers, jlens, jlens.fitting as JF, logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s', force=True)
    st = torch.load(BK, map_location='cpu', weights_only=True)
    if (st['n_done'], st['next_idx']) != (N_CK, N_CK): raise SystemExit('backup is not at 66/66')
    S66 = {l: st['jacobian_sum'][l].clone() for l in F.LAYERS}
    cp = OUT / 'checkpoint_resume65.pt'
    if cp.exists(): log('re-creating own temp checkpoint from the backup (earlier attempt was interrupted):', cp)
    torch.save(dict(st, n_done=N_CK - 1, next_idx=N_CK - 1), cp)
    seen = {}
    _orig = JF.jacobian_for_prompt
    def observer(*args, **kw):
        r = _orig(*args, **kw); seen['J'], seen['seq_len'], seen['n_valid'] = r; return r
    JF.jacobian_for_prompt = observer
    t0 = time.monotonic()
    tok = transformers.AutoTokenizer.from_pretrained(cfg['model'], revision=cfg['revision'])
    hf = transformers.AutoModelForCausalLM.from_pretrained(cfg['model'], revision=cfg['revision'],
                     torch_dtype=torch.bfloat16, device_map='auto', max_memory={0: '55GiB', 'cpu': '36GiB'}, low_cpu_mem_usage=True)
    model = jlens.from_hf(hf, tok); t_load = time.monotonic() - t0
    dm = getattr(hf, 'hf_device_map', {}); n_cpu = sum(1 for v in dm.values() if str(v) == 'cpu')
    log('loaded in', round(t_load), 's; device map entries', len(dm), 'on cpu', n_cpu)
    jlens.fit(model, prompts[:N_CK], source_layers=F.LAYERS, target_layer=63, dim_batch=1, max_seq_len=128, skip_first=16,
              checkpoint_path=str(cp), checkpoint_every=1, resume=True)
    J = seen['J']; d = model.d_model; sq = math.sqrt(d)
    norm_fp32 = max(J[l].norm().item() for l in F.LAYERS) / sq                     # exactly jlens.fit's prompt_norm
    norm_f64 = max(J[l].double().norm().item() for l in F.LAYERS) / sq
    per_layer = {l: J[l].double().norm().item() / sq for l in F.LAYERS}
    n = N_CK - 1; S65 = {l: S66[l].double() - J[l].double() for l in F.LAYERS}
    dmean = max(((J[l].double() - S65[l] / n).norm() / ((n + 1) * (S65[l] / n).norm())).item() for l in F.LAYERS)
    torch.save({l: J[l] for l in F.LAYERS}, OUT / 'J_prompt66_orig_code.pt')
    r = dict(job=os.environ.get('SLURM_JOB_ID'), host=os.uname().nodename, gpu=(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'), torch=torch.__version__,
             transformers=transformers.__version__, cuda=torch.version.cuda, load_seconds=round(t_load), device_map_cpu_entries=n_cpu,
             device_map=dm, seq_len=seen['seq_len'], n_valid=seen['n_valid'],
             max_norm_over_sqrt_d_fp32=norm_fp32, max_norm_over_sqrt_d_f64=norm_f64, per_layer_norm_over_sqrt_d=per_layer,
             max_d_mean_original_definition=dmean, reference_log=REF, new_code_gate_value=NEWCODE,
             abs_diff_vs_new_code=abs(norm_fp32 - NEWCODE), abs_diff_vs_log=abs(norm_fp32 - REF['norm']),
             frozen_sha256={p.name: sha(p) for p in (FULLFIT, BASE / 'stage9_runner.py', BASE / '351_stage9.py')},
             backup_sha256=sha(BK), seconds=round(time.monotonic() - t0), at=datetime.now().isoformat(timespec='seconds'))
    res.write_text(json.dumps(r, indent=1, default=str)); log('RESULT', json.dumps({k: r[k] for k in ('max_norm_over_sqrt_d_fp32', 'max_norm_over_sqrt_d_f64', 'max_d_mean_original_definition', 'seq_len', 'n_valid', 'abs_diff_vs_new_code', 'abs_diff_vs_log')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
