"""Addendum 12 item 2-1, VERSION 2 (deviation record D12-1, config/prereg_addendum12_deviations.json, sha256 checked at start).

D12-1 replaces the planned 66-prompt refit by a cheaper hard check that MUST include a bit-exact refit of original prompts:
  (a) k = 3 original Fit A prompts re-run through the same accumulation code (jlens.fit, checkpoint per prompt) with the loader of
      the stored runs (351_stage9.py / stage9_runner.py: from_pretrained(bf16, device_map='auto', low_cpu_mem_usage=True)), layers
      48 and 56, and compared BITWISE (torch.equal) with every stored Fit A partial state of those prompts:
        after prompt 1: fits/A_n0001_layers_56 (L56) and runner_runs/benchmark_A1_7layers (L48, L56)
        after prompt 2: fits/A_n0002_layers_48-56 (L48, L56)
        after prompt 3: runner_runs/fresh_A3 and runner_runs/resume_A3 (L48, L56)
      (stored per-prompt quantities: Fit A has these prefix checkpoints only; the 100-prompt run keeps the final sum, not per prompt.
      Already on disk: A_n0001 L56 == benchmark_A1 L56 bitwise, and resume_A3 == fresh_A3 bitwise, so the stored states are
      reproducible across runs.)
  (b) prompt 66 of Fit B recomputed (v1 `gate`: frozen fullfit loader) vs the original log (rounded values, v1 rule).
  Any non-identical / out-of-rule result = HARD FAIL: summary/gate_v2.json status FAIL, exit 2; the resume (v1 `resume`) refuses
  to start unless gate_v2 is PASS. The v1 recompute66 / hardcheck66 path is NOT used (v2 analysis passes SKIP of hardcheck66).
Commands: gpu --unit gate_v2 | gpu --unit resume | gpu --unit holdout | gpu --unit read:<c>:<k> | gpu --all | analyze | selftest | tiny --root
Everything except gate_v2 / the resume guard is v1 (stage9_b2_fitb.py, imported by path, unchanged).
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path

H = Path.home() / 'jlens_work'
if __name__ == '__main__' and sys.argv[1:2] == ['status']:          # fast path for b2_orch.py: file checks only, no torch
    _sp = importlib.util.spec_from_file_location('b2c_status', H / '13_stage13/b2c_status.py'); _st = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_st)
    _st.status_21(); sys.exit(0)
_sp = importlib.util.spec_from_file_location('fitb_v1', H / '09_stage9/stage9_b2_fitb.py'); V1 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V1)
R9, R13 = V1.R9, V1.R13
DEV = R13 / 'config/prereg_addendum12_deviations.json'; DEV_SHA = 'c4c793653097d3b2a898892e4f28d5ea71fe8de71097c936f3345de027a52dba'
K, KL = 3, [48, 56]
STORED = [(1, R9 / 'fits/A_n0001_layers_56', [56]), (1, R9 / 'runner_runs/benchmark_A1_7layers', [48, 56]),
          (2, R9 / 'fits/A_n0002_layers_48-56', [48, 56]), (3, R9 / 'runner_runs/fresh_A3', [48, 56]), (3, R9 / 'runner_runs/resume_A3', [48, 56])]
log = V1.log


def check_dev():
    if hashlib.sha256(DEV.read_bytes()).hexdigest() != DEV_SHA: raise SystemExit('DEVIATION RECORD CHANGED (prereg_addendum12_deviations.json)')
    if (DEV.parent / 'prereg_addendum12_deviations.json.sha256').read_text().split()[0] != DEV_SHA: raise SystemExit('deviation .sha256 file differs')


def fita_prompts(k):
    rows = [json.loads(x) for x in (R9 / 'prompts/fit_A.jsonl').read_text().splitlines() if x.strip()][:k]
    for n, d, _ in STORED:
        ids = json.loads((d / 'fitting_config.json').read_text())['prompt_ids']
        if ids != [r['text_sha256'] for r in rows][:len(ids)]: raise SystemExit(f'{d}: stored prompt ids differ from fit_A.jsonl')
    return [r['text'] for r in rows]


def runner_loader():
    """the loader of 351_stage9.py fit / stage9_runner.py run (stored Fit A prefix states)."""
    import torch, transformers, jlens
    tok = transformers.AutoTokenizer.from_pretrained('Qwen/Qwen3-32B', revision='9216db5781bf21249d130ec9da846c4624c16137')
    hf = transformers.AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-32B', revision='9216db5781bf21249d130ec9da846c4624c16137',
                                                           torch_dtype=torch.bfloat16, device_map='auto', low_cpu_mem_usage=True)
    return jlens.from_hf(hf, tok), hf


def bitwise_compare(states, stored):
    """states: {n: state dict after n prompts}; stored: [(n, dir, layers, stored state)] -> (status, rows). Missing = FAIL."""
    import torch
    rows, ok = [], True
    for n, d, lays, st in stored:
        s = states.get(n)
        for l in lays:
            if s is None or l not in s['jacobian_sum']: eq, mx = False, float('inf')
            else:
                a, b = s['jacobian_sum'][l], st['jacobian_sum'][l]
                eq = bool(a.shape == b.shape and torch.equal(a, b)); mx = float((a - b).abs().max()) if a.shape == b.shape else float('inf')
            cnt = s is not None and (s['n_done'], s['next_idx']) == (st['n_done'], st['next_idx']) == (n, n)
            st_ = 'PASS' if eq and cnt else 'FAIL'; ok &= st_ == 'PASS'
            rows.append(dict(check=f'fitA_prefix{n}_bitwise:{Path(d).name}', layer=l, value=mx, reference=0.0, rel_diff=0.0 if eq else 1.0, threshold=0.0, status=st_))
    return ('PASS' if ok else 'FAIL'), rows


def gate_a(root, model=None, prompts=None, stored=None, layers=KL, target_layer=63):
    import torch
    stored = stored if stored is not None else [(n, d, l, torch.load(d / 'checkpoint.pt', map_location='cpu', weights_only=True)) for n, d, l in STORED]
    prompts = prompts or fita_prompts(K); model = model or runner_loader()[0]
    d = root / 'fitA_k3'; d.mkdir(parents=True, exist_ok=True); cp = d / 'checkpoint.pt'; states = {}
    import jlens
    for n in range(1, max(x[0] for x in stored) + 1):
        f = d / f'state_{n}.pt'
        if not f.exists():
            jlens.fit(model, prompts[:n], source_layers=layers, target_layer=target_layer, dim_batch=1, max_seq_len=128, skip_first=16,
                      checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
            torch.save(torch.load(cp, map_location='cpu', weights_only=True), f)
        states[n] = torch.load(f, map_location='cpu', weights_only=True)
    return bitwise_compare(states, stored)


def gate_v2(root):
    import torch, pandas as pd, gc
    if not V1.backup_ok(root): raise SystemExit('no verified backup of the 66-prompt checkpoint: run backup first')
    t0 = time.monotonic(); model, hf = runner_loader(); sa, rows = gate_a(root, model=model); del model, hf; gc.collect(); torch.cuda.empty_cache()
    log('D12-1 (a) Fit A k=3 bitwise:', sa)
    okb = V1.gate(root)                                     # (b) prompt 66 vs log, frozen fullfit loader (writes summary/gate.json)
    rows += json.loads((root / 'summary/gate.json').read_text())['rows']
    st = 'PASS' if sa == 'PASS' and okb else 'FAIL'
    df = V1.COLS.check(pd.DataFrame(rows, columns=V1.COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); df.to_csv(root / 'summary/gate_v2.csv', index=False)
    (root / 'summary/gate_v2.json').write_text(json.dumps(dict(status=st, rule='D12-1: (a) Fit A prompts 1-3 bitwise == stored prefix states; (b) Fit B prompt 66 vs log',
                                                               seconds=round(time.monotonic() - t0), rows=rows, at=V1.now()), indent=1, default=float))
    print('HARD CHECK D12-1', st, flush=True)
    if st != 'PASS': (root / 'HARD_CHECK_FAILED').write_text(json.dumps(rows, default=float))
    return st == 'PASS'


def gate_v2_passed(root):
    f = root / 'summary/gate_v2.json'; return f.exists() and json.loads(f.read_text())['status'] == 'PASS'


def selftest():
    import torch
    g = torch.Generator().manual_seed(3); S = {l: torch.randn(8, 8, generator=g) for l in KL}
    mk = lambda n, J: dict(jacobian_sum=J, n_done=n, next_idx=n)
    stored = [(1, 'x', KL, mk(1, S)), (3, 'y', KL, mk(3, S))]
    s1 = bitwise_compare({1: mk(1, {l: v.clone() for l, v in S.items()}), 3: mk(3, {l: v.clone() for l, v in S.items()})}, stored)[0]
    bump = {l: v.clone() for l, v in S.items()}; bump[56][0, 0] = torch.nextafter(bump[56][0, 0], torch.tensor(1e9))
    s2 = bitwise_compare({1: mk(1, S), 3: mk(3, bump)}, stored)[0]
    s3 = bitwise_compare({1: mk(1, S)}, stored)[0]
    s4 = bitwise_compare({1: mk(1, S), 3: mk(2, S)}, stored)[0]
    ok = (s1, s2, s3, s4) == ('PASS', 'FAIL', 'FAIL', 'FAIL')
    print(f'SELFTEST v2 bitwise identical -> {s1}; one ulp -> {s2}; missing state -> {s3}; wrong count -> {s4}: {"OK" if ok else "BROKEN"}', flush=True)
    return ok


def tiny(root):
    """CPU: tiny model; 'stored' prefix states written by jlens.fit in one run, gate_a re-fits them in another call -> PASS;
    one-ulp perturbation -> FAIL. Then the v1 tiny (whole pipeline) in a sub-root."""
    import torch, transformers, jlens
    torch.use_deterministic_algorithms(True); torch.set_num_threads(1)
    s12 = V1.load_mod(H / '12_stage12/371_stage12.py', 's12'); s10 = s12.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); model = jlens.from_hf(hf, s10.tokenizer())
    prompts = fita_prompts(K); lay = [1, 2]; stored = []
    sd = root / 'stored'; sd.mkdir(parents=True, exist_ok=True)
    for n in (1, 2, 3):
        jlens.fit(model, prompts[:n], source_layers=lay, target_layer=3, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=str(sd / f'ck{n}.pt'))
        stored.append((n, sd / f'ck{n}', lay, torch.load(sd / f'ck{n}.pt', weights_only=True)))
    st, rows = gate_a(root, model=model, prompts=prompts, stored=stored, layers=lay, target_layer=3)
    n3, d3, l3, s3 = stored[-1]; pj = {k: v.clone() for k, v in s3['jacobian_sum'].items()}; v = pj[lay[0]]; v[0, 0] = torch.nextafter(v[0, 0], torch.tensor(1e9))
    bad = stored[:-1] + [(n3, d3, l3, dict(s3, jacobian_sum=pj))]
    st_bad = bitwise_compare({n: torch.load(root / f'fitA_k3/state_{n}.pt', weights_only=True) for n in (1, 2, 3)}, bad)[0]
    print('TINY CHECK', 'PASS' if st == 'PASS' else 'FAIL', 'gate_a chunked refit == stored prefix states bitwise', rows[:2], flush=True)
    print('TINY CHECK', 'PASS' if st_bad == 'FAIL' else 'FAIL', 'one-ulp perturbed stored state -> FAIL', flush=True)
    ok = st == 'PASS' and st_bad == 'FAIL' and selftest()
    print('TINY v2', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['gpu', 'analyze', 'selftest', 'tiny', 'status'])
    ap.add_argument('--unit'); ap.add_argument('--all', action='store_true'); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    V1.check_frozen(); check_dev(); root = Path(a.root) if a.root else R13 / 'b2_fitb'; root.mkdir(parents=True, exist_ok=True)
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'tiny': assert a.root; sys.exit(0 if tiny(root) else 1)
    if a.cmd == 'analyze':
        if not gate_v2_passed(root): raise SystemExit('gate_v2 not PASS: no analysis')
        V1.analyze(root); return
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    if a.unit == 'gate_v2': sys.exit(0 if gate_v2(root) else 2)
    if a.unit in ('gate', 'recompute66'): raise SystemExit(f'unit {a.unit} is replaced by gate_v2 under D12-1')
    if a.unit == 'resume':
        if not gate_v2_passed(root): raise SystemExit('gate_v2 not PASS: refuse to resume')
        t0 = time.monotonic(); sys.exit(0 if V1.resume(root, V1.minutes_left(t0, a.minutes)) else 2)
    V1.gpu(a, root)


if __name__ == '__main__':
    main()
