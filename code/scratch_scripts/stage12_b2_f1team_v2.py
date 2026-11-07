"""Addendum 12 item 2-2, VERSION 2 (deviation record D12-2, config/prereg_addendum12_deviations.json, sha256 checked at start).

What is stored of the original F1 fit (checked 2026-11-06): 371_stage12/alens/checkpoint.pt = the fp32 running SUM after 40/40 prompts
(n_done = next_idx = 40, no skip) and lens.pt = fp16(sum / 40); progress.json. NOTHING per prompt is stored (no per-prompt
Jacobians, no intermediate checkpoint; the Stage 12 logs have no per-prompt jlens lines). So a bit-exact comparison on k >= 3
prompts is only possible against the 40-prompt sum. Closest bit-exact comparison, used here (no extra GPU cost):
  the two half-fits are run as ONE pass over the 40 frozen fit prompts IN THE ORIGINAL F1 ORDER, with the jlens.fit accumulation
  code (jlens.jacobian_for_prompt + the same fp32 `sum[l] += J[l]` starting from zeros, checkpoint after every prompt, atomic);
  each prompt's J is added to S_all and to S_A or S_B (its team half). Then
  (a) S_all (k = 40 original prompts) must be BITWISE identical (torch.equal) to the stored checkpoint sum, every layer, and
      fp16(S_all / 40) bitwise identical to the stored lens.pt;
  (b) (S_A + S_B) / 40 vs the stored lens, relative Frobenius <= 1e-3 (v1 rule);
  any miss = HARD FAIL (summary/B2_F1TEAM_HARD_CHECK_FAILED, exit 2; no read unit starts).
  Half lenses = S_A / n_A and S_B / n_B (the jlens.fit expression), saved with JacobianLens.save into alens_team_{A,B}/lens.pt,
  so the v1 read / analyze code is used unchanged. Cost: the same 40 prompts the two half fits need anyway (~3 A100-h), but
  sequential (one GPU job at a time).
Commands: fit (gpu, budgeted, resumable) | hardcheck | gpu --unit fit|read:<c>:<k> | gpu --all | analyze | tiny --root | selftest
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
if __name__ == '__main__' and sys.argv[1:2] == ['status']:          # fast path for b2_orch.py: file checks only, no torch
    _sp = importlib.util.spec_from_file_location('b2c_status', H / '13_stage13/b2c_status.py'); _st = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_st)
    _st.status_22(); sys.exit(0)
_sp = importlib.util.spec_from_file_location('f1team_v1', H / '12_stage12/stage12_b2_f1team.py'); V1 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V1)
s12, s11, s10, R12, R13, COLS = V1.s12, V1.s11, V1.s10, V1.R12, V1.R13, V1.COLS
DEV = R13 / 'config/prereg_addendum12_deviations.json'; DEV_SHA = 'c4c793653097d3b2a898892e4f28d5ea71fe8de71097c936f3345de027a52dba'
log = V1.safe_log


def check_dev():
    if hashlib.sha256(DEV.read_bytes()).hexdigest() != DEV_SHA: raise SystemExit('DEVIATION RECORD CHANGED (prereg_addendum12_deviations.json)')
    if (DEV.parent / 'prereg_addendum12_deviations.json.sha256').read_text().split()[0] != DEV_SHA: raise SystemExit('deviation .sha256 file differs')


def atomic_save(obj, path):
    import torch
    tmp = f'{path}.tmp.{os.getpid()}'; torch.save(obj, tmp); os.replace(tmp, path)


def joint_fit(model, root, budget_min, layers=None, n_total=None, sec_per_prompt=V1.SEC_PER_PROMPT, target_layer=None, max_new=None):
    """one pass over the fit prompts in original F1 order; returns True when complete."""
    import torch, jlens, pandas as pd
    layers = layers or s12.FIT_LAYERS; target_layer = target_layer if target_layer is not None else len(model.layers) - 1
    sp, _ = V1.make_split(root); fp = pd.read_parquet(R12 / 'config/fit_prompts.parquet').reset_index(drop=True)
    half = dict(zip(sp.fit_row, sp.half)); prompts = fp.text.tolist(); n_total = n_total or len(prompts)
    d = root / 'alens_team_joint'; d.mkdir(parents=True, exist_ok=True); cp = d / 'checkpoint.pt'
    if cp.exists(): st = torch.load(cp, map_location='cpu', weights_only=True)
    else:
        z = lambda: {l: torch.zeros(model.d_model, model.d_model, dtype=torch.float32) for l in layers}
        st = dict(S_all=z(), S_A=z(), S_B=z(), n_all=0, n_A=0, n_B=0, next_idx=0, skipped=[], layers=list(layers), target_layer=target_layer, order='fit_prompts.parquet row order')
    if st['layers'] != list(layers): raise SystemExit('checkpoint layers differ')
    t0 = time.monotonic(); new = 0
    while st['next_idx'] < n_total:
        if max_new is not None and new >= max_new: break
        new += 1
        if (budget_min * 60 - (time.monotonic() - t0)) < sec_per_prompt + 60: log('budget: stop before next prompt'); break
        i = st['next_idx']; t1 = time.monotonic()
        try:
            J, seq_len, n_valid = jlens.jacobian_for_prompt(model, prompts[i], layers, target_layer=target_layer, dim_batch=1, max_seq_len=128, skip_first=16)
        except ValueError as e:
            log('WARN skipping prompt', i, repr(e)); st['skipped'].append(i); st['next_idx'] = i + 1; atomic_save(st, cp); continue
        h = half[i]
        for l in layers:
            st['S_all'][l] += J[l]; st[f'S_{h}'][l] += J[l]
        st['n_all'] += 1; st[f'n_{h}'] += 1; st['next_idx'] = i + 1; atomic_save(st, cp)
        log(f'joint fit prompt {i + 1}/{n_total} half {h} seq_len={seq_len} n_valid={n_valid} {time.monotonic() - t1:.0f}s')
    (d / 'progress.json').write_text(json.dumps(dict(done=st['next_idx'], n_A=st['n_A'], n_B=st['n_B'], skipped=st['skipped'], updated=s11.now())))
    if st['next_idx'] >= n_total:
        for h in 'AB':
            out = root / f'alens_team_{h}'; out.mkdir(parents=True, exist_ok=True)
            if not (out / 'lens.pt').exists():
                L = jlens.JacobianLens(jacobians={l: st[f'S_{h}'][l] / st[f'n_{h}'] for l in layers}, n_prompts=st[f'n_{h}'], d_model=model.d_model)
                tmp = out / 'lens.tmp.pt'; L.save(str(tmp)); os.replace(tmp, out / 'lens.pt')
                (out / 'half.json').write_text(json.dumps(dict(half=h, seed=V1.SEED, n=st[f'n_{h}'], from_joint=str(cp)), indent=1))
        return True
    return False


def bit_compare(st, stored_sum, stored_lens, layers):
    import torch
    rows, ok = [], True
    for l in layers:
        a, b = st['S_all'][l], stored_sum['jacobian_sum'][l]
        eq = bool(a.shape == b.shape and torch.equal(a, b)); mx = float((a - b).abs().max()) if a.shape == b.shape else float('inf')
        eql = bool(torch.equal((a / st['n_all']).half().float(), stored_lens.jacobians[l].float()))
        r = dict(layer=l, relfro_combined_vs_stored=0.0 if eq else float((a - b).norm() / b.norm()), maxabs=mx, threshold=0.0, status='PASS' if eq and eql else 'FAIL')
        rows.append(r); ok &= r['status'] == 'PASS'
    cnt = (st['n_all'], st['next_idx']) == (stored_sum['n_done'], stored_sum['next_idx']) and not st['skipped']
    rows.append(dict(layer=-1, relfro_combined_vs_stored=float('nan'), maxabs=float(st['n_all']), threshold=float(stored_sum['n_done']), status='PASS' if cnt else 'FAIL'))
    return ('PASS' if ok and cnt else 'FAIL'), rows


def hardcheck(root, stored_ck=None, stored_lens=None, layers=None):
    import torch, jlens, pandas as pd
    layers = layers or s12.FIT_LAYERS
    st = torch.load(root / 'alens_team_joint/checkpoint.pt', map_location='cpu', weights_only=True)
    S = torch.load(stored_ck or (R12 / 'alens/checkpoint.pt'), map_location='cpu', weights_only=True)
    LF = jlens.JacobianLens.load(str(stored_lens or (R12 / 'alens/lens.pt')))
    sa, rows_a = bit_compare(st, S, LF, layers)
    sb, rows_b = V1.combined_vs_stored(dict(jacobian_sum=st['S_A'], n_done=st['n_A']), dict(jacobian_sum=st['S_B'], n_done=st['n_B']), LF.jacobians, layers)
    status = 'PASS' if sa == 'PASS' and sb == 'PASS' else 'FAIL'
    rows = [r | {'layer': 2000 + r['layer'] if r['layer'] >= 0 else -1} for r in rows_a] + rows_b
    df = COLS.check(pd.DataFrame(rows, columns=COLS.F1H_HARDCHECK), 'F1H_HARDCHECK'); (root / 'summary').mkdir(parents=True, exist_ok=True)
    df.to_csv(root / 'summary/b2_f1team_hardcheck.csv', index=False)
    (root / 'summary/b2_f1team_hardcheck.json').write_text(json.dumps(dict(status=status, rule='D12-2: (a) S_all over the 40 original prompts bitwise == stored F1 checkpoint sum and '
        'fp16(S_all/40) == stored lens (layer 2000+l); (b) (S_A+S_B)/40 vs stored lens rel. Frobenius <= 1e-3 (layer l)', a=sa, b=sb, rows=rows), indent=1, default=float))
    print('HARD CHECK D12-2', status, '(a)', sa, '(b)', sb, flush=True)
    if status != 'PASS': (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').write_text(json.dumps(dict(rows=rows), default=float)); return False
    return True


def gpu(a, root):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); CL = root / 'logs/claims_b2_f1team'; CL.mkdir(parents=True, exist_ok=True)
    if (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').exists(): raise SystemExit('hard check failed earlier: stop')
    C = None
    if not all((root / f'alens_team_{h}/lens.pt').exists() for h in 'AB'):
        if a.unit and a.unit != 'fit': raise SystemExit('fit not complete: only --unit fit can run')
        if not s11.claim(CL / 'joint_fit', me): log('joint fit held by another job: nothing to do (only ONE fit job at a time)'); return
        C = V1.GCtx(); done = joint_fit(C.model, root, V1.minutes_left(t0, a.minutes))
        if not done: return
    if not V1.hardcheck_passed(root):
        if not hardcheck(root): sys.exit(2)
    if a.unit == 'fit': return
    if C is None: C = V1.GCtx()
    LS = V1.lenses(C, root); rd = [a.unit] if a.unit else [f'read:{c}:{k}' for c in s12.TC for k in range(24)]; last = V1.SEC_PER_READ
    for u in rd:
        _, c, k = u.split(':'); k = int(k)
        if V1.read_path(root, c, k).exists(): continue
        if V1.minutes_left(t0, a.minutes) * 60 < 1.5 * last + 30: log('budget: stop before next read unit'); return
        if not a.unit and not s11.claim(CL / f'read_{c}_{k:03d}', me): continue
        last = max(V1.read_unit(C, LS, root, c, k, s12.FIT_LAYERS), 1.0)
    log('gpu: no unit left for this job')


def selftest():
    import torch, jlens
    g = torch.Generator().manual_seed(4); lay = [1, 2]
    Js = [{l: torch.randn(8, 8, generator=g) for l in lay} for _ in range(4)]
    S = {l: torch.zeros(8, 8) for l in lay}
    for J in Js:
        for l in lay: S[l] += J[l]
    st = dict(S_all={l: v.clone() for l, v in S.items()}, n_all=4, next_idx=4, skipped=[])
    L = jlens.JacobianLens(jacobians={l: (S[l] / 4).half().float() for l in lay}, n_prompts=4, d_model=8)
    s1 = bit_compare(st, dict(jacobian_sum=S, n_done=4, next_idx=4), L, lay)[0]
    S2 = {l: torch.zeros(8, 8) for l in lay}
    for J in [Js[1], Js[0], Js[2], Js[3]]:
        for l in lay: S2[l] += J[l]
    s2 = bit_compare(dict(st, S_all=S2), dict(jacobian_sum=S, n_done=4, next_idx=4), L, lay)[0]     # other summation order
    s3 = bit_compare(dict(st, skipped=[2]), dict(jacobian_sum=S, n_done=4, next_idx=4), L, lay)[0]
    ok = s1 == 'PASS' and s3 == 'FAIL' and (s2 == 'FAIL' or all(torch.equal(S[l], S2[l]) for l in lay))
    print(f'SELFTEST v2 bitwise same order -> {s1}; other order -> {s2} (FAIL unless fp32 sums happen to agree); skipped prompt -> {s3}: {"OK" if ok else "BROKEN"}', flush=True)
    return ok


def tiny(root):
    """CPU: tiny model; 'stored' = jlens.fit over the 40 F1 prompts in order (layers [0,1], max_seq_len 128) -> checkpoint + lens;
    joint_fit in 2 budgeted chunks must reproduce it bitwise and (S_A+S_B)/40 within 1e-3; perturbed stored sum -> FAIL; then read+analyze (v1)."""
    import torch, transformers, jlens, pandas as pd
    torch.use_deterministic_algorithms(True); torch.set_num_threads(1)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    lay = [0, 1]; fp = pd.read_parquet(R12 / 'config/fit_prompts.parquet'); sd = root / 'stored'; sd.mkdir(parents=True, exist_ok=True)
    ref = jlens.fit(model, fp.text.tolist(), source_layers=lay, target_layer=2, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=str(sd / 'checkpoint.pt'))
    ref.save(str(sd / 'lens.pt'))
    joint_fit(model, root, budget_min=600, layers=lay, sec_per_prompt=2, target_layer=2, max_new=15)    # partial chunk (15 prompts)
    p1 = torch.load(root / 'alens_team_joint/checkpoint.pt', weights_only=True)['next_idx']
    joint_fit(model, root, budget_min=600, layers=lay, sec_per_prompt=2, target_layer=2)
    checks = {f'chunked joint fit resumed ({p1} then 40)': 0 < p1 < 40}
    checks['hard check (a)+(b) -> PASS'] = hardcheck(root, sd / 'checkpoint.pt', sd / 'lens.pt', layers=lay)
    S = torch.load(sd / 'checkpoint.pt', weights_only=True); v = S['jacobian_sum'][0]; v[0, 0] = torch.nextafter(v[0, 0], torch.tensor(1e9)); torch.save(S, sd / 'checkpoint_bad.pt')
    checks['one-ulp perturbed stored sum -> FAIL'] = not hardcheck(root, sd / 'checkpoint_bad.pt', sd / 'lens.pt', layers=lay)
    (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').unlink(missing_ok=True); hardcheck(root, sd / 'checkpoint.pt', sd / 'lens.pt', layers=lay)
    C = type('T', (), {})(); C.torch = torch; C.tok = tok; C.model = model; C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks)
    C.prompts = {c: s10.condition_prompts(s11.R10, C.papers, c)[0] for c in ('true', 'false_0')}
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); C.smp = smp[smp.shard == 0].head(3); C.env = {'tiny': True}; s10.layer_device = lambda m, k: 'cpu'
    import shutil; shutil.copy2(sd / 'lens.pt', root / 'alens_full_tiny.pt')
    LS = {'teamA': V1.load_lens(C, root / 'alens_team_A/lens.pt'), 'teamB': V1.load_lens(C, root / 'alens_team_B/lens.pt'), 'full': V1.load_lens(C, root / 'alens_full_tiny.pt')}
    for c in ('true', 'false_0'): V1.read_unit(C, LS, root, c, 0, lay)
    V1.analyze(root, layers=lay); checks['analysis report'] = (root / 'reports/b2_f1team_report.md').exists()
    checks['selftest'] = selftest()
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('TINY v2', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['hardcheck', 'gpu', 'analyze', 'tiny', 'selftest', 'status'])
    ap.add_argument('--unit'); ap.add_argument('--all', action='store_true'); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    V1.check_plan(); check_dev(); root = Path(a.root) if a.root else R12
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'tiny': assert a.root; root.mkdir(parents=True, exist_ok=True); sys.exit(0 if tiny(root) else 1)
    if a.cmd == 'hardcheck': sys.exit(0 if hardcheck(root) else 2)
    if a.cmd == 'analyze':
        if not V1.hardcheck_passed(root): raise SystemExit('hard check not PASS')
        V1.analyze(root, conds_needed=s12.TC); return
    if not (a.unit or a.all): raise SystemExit('gpu needs --unit or --all')
    gpu(a, root)


if __name__ == '__main__':
    main()
