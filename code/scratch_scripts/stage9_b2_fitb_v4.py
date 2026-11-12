"""Item 2-1, gate v4 + continuation (deviation record D12-5, 2026-11-12). New file; v1/v2/v3 and the frozen Stage 9 scripts unchanged.

D12-5: the D12-1 part (b) gate (stage9_b2_fitb.py gate_compare, line 162) computed max||J||/sqrt(d) in float64
(J.double().norm()), but the reference it is compared with is the value the original fit LOGGED, which jlens.fit computes in
float32 (jlens/fitting.py:352, per_prompt_J[l].norm().item()). On the same J the two differ by 0.0112 (original-code rerun 11760695:
fp32 4.366808, f64 4.378043; log 4.367). v4 computes both part-(b) quantities the way jlens.fit computes the logged ones (fp32,
fitting.py:352-358; S65 = S66 - J in fp32). Everything else is the v1/v2/v3 code: part (a) Fit A k=3 bitwise (v3: reuse of the
provenance-checked states in 381_stage13/b2_fitb/fitA_k3, else model load + recompute), the frozen fullfit loader for prompt 66
(stage9_b2_fitb.py stage9_loader), jlens.jacobian_for_prompt with the frozen arguments, the same checks (norm, d_mean, seq_len+n_valid)
and the same thresholds (0.5 * printed unit + 1e-3 * |reference|). The f64 values are kept in the json as information.
The failed v2/v3 gate outputs stay untouched in 381_stage13/b2_fitb/. The continuation uses the NEW root 381_stage13/b2_fitb_d125/
(verified copy of the 66-prompt backup); all later work there is the unchanged v2/v1 code with --root: Fit B prompts 67-100 through the
frozen command (stage9_fullfit.py run --half B, stage9_b2_fitb.py:202), then holdout + 168 read units + analysis.
Commands: setup | gate | verify | status | gpu <v2 gpu args> | analyze
"""
import hashlib, importlib.util, json, math, os, shutil, stat, sys, time
from datetime import datetime
from pathlib import Path

H = Path.home() / 'jlens_work'; D = H / '09_stage9'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
OLD = R13 / 'b2_fitb'; ROOT4 = R13 / 'b2_fitb_d125'
REC = R13 / 'config/prereg_addendum12_deviations_D12-5.json'; REC_SHA = R13 / 'config/prereg_addendum12_deviations_D12-5.json.sha256'


def load(name, p):
    sp = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
    return h.hexdigest()


def record_ok():
    if not REC.exists(): return False, 'no D12-5 record'
    if stat.S_IMODE(os.stat(REC).st_mode) & 0o222: return False, 'D12-5 record not locked'
    if sha(REC) != REC_SHA.read_text().split()[0]: return False, 'D12-5 record sha256 differs from .sha256'
    if json.loads(REC.read_text()).get('decision') != 'fix_gate_precision_fp32': return False, 'D12-5 decision field'
    return True, 'D12-5 record verified'


def setup():
    ROOT4.mkdir(parents=True, exist_ok=True); m = json.loads((OLD / 'checkpoint_B066.json').read_text())
    for f in ('checkpoint_B066.pt', 'checkpoint_B066.json'):
        if not (ROOT4 / f).exists(): shutil.copy2(OLD / f, ROOT4 / f)
    if sha(ROOT4 / 'checkpoint_B066.pt') != m['sha256']: raise SystemExit('backup copy sha256 differs')
    return dict(root=str(ROOT4), backup_sha256=m['sha256'])


def compare_fp32(J, S66, n_ck, ref, d_model, V1):
    """part (b) as jlens.fit computes the logged values (fitting.py:352-358), fp32 throughout; thresholds as v1 gate_compare."""
    sq = math.sqrt(d_model); n = n_ck - 1
    S65 = {l: S66[l] - J[l] for l in J}                                       # fp32 (both stored fp32)
    norm = max(J[l].norm().item() for l in J) / sq
    dm = max(((J[l] - S65[l] / n).norm() / ((n + 1) * (S65[l] / n).norm())).item() for l in J)
    info = dict(norm_f64=max(J[l].double().norm().item() for l in J) / sq,
                d_mean_f64=max(((J[l].double() - (S66[l].double() - J[l].double()) / n).norm() / ((n + 1) * ((S66[l].double() - J[l].double()) / n).norm())).item() for l in J))
    rows = []
    for name, v, r, u in (('max_norm_over_sqrt_d', norm, ref['norm'], ref['norm_unit']), ('max_d_mean', dm, ref['d_mean'], ref['d_mean_unit'])):
        thr = 0.5 * u + V1.TOL * abs(r); st = 'PASS' if abs(v - r) <= thr else 'FAIL'
        rows.append(dict(check=f'gate_prompt{n_ck}_{name}', layer=-1, value=v, reference=r, rel_diff=abs(v - r) / abs(r), threshold=thr, status=st))
    return ('PASS' if all(x['status'] == 'PASS' for x in rows) else 'FAIL'), rows, info


def gate_b(V1, model=None, J_given=None):
    import torch, jlens, pandas as pd
    ref = V1.logged_stats(V1.LOG_B, V1.N_CK); st = torch.load(ROOT4 / 'checkpoint_B066.pt', map_location='cpu', weights_only=True)
    t0 = time.monotonic()
    if J_given is None:
        model = model or V1.stage9_loader(); prompts = V1.fit_b_prompts()
        J, seq_len, n_valid = jlens.jacobian_for_prompt(model, prompts[V1.N_CK - 1], V1.LAYERS, target_layer=63, dim_batch=1, max_seq_len=128, skip_first=16)
    else: J, seq_len, n_valid = J_given
    status, rows, info = compare_fp32(J, st['jacobian_sum'], V1.N_CK, ref, model.d_model if model is not None else J[V1.LAYERS[0]].shape[0], V1)
    rows.append(dict(check=f'gate_prompt{V1.N_CK}_seq_len', layer=-1, value=seq_len, reference=ref['seq_len'], rel_diff=0.0 if seq_len == ref['seq_len'] else 1.0, threshold=0,
                     status='PASS' if seq_len == ref['seq_len'] and n_valid == ref['n_valid'] else 'FAIL'))
    if rows[-1]['status'] != 'PASS': status = 'FAIL'
    df = V1.COLS.check(pd.DataFrame(rows, columns=V1.COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); (ROOT4 / 'summary').mkdir(parents=True, exist_ok=True)
    df.to_csv(ROOT4 / 'summary/gate.csv', index=False)
    torch.save({l: J[l] for l in J}, ROOT4 / 'J_prompt66_gate_v4.pt')
    (ROOT4 / 'summary/gate.json').write_text(json.dumps(dict(status=status, precision='fp32 (as jlens.fit logs, D12-5)', info_f64=info, seconds=round(time.monotonic() - t0),
                                                            rows=rows, at=V1.now()), indent=1, default=float))
    V1.log('GATE v4 (fp32)', status, rows, info); return status == 'PASS', rows, info


def gate():
    ok, why = record_ok()
    if not ok: raise SystemExit(f'gate v4 refused: {why}')
    import torch, pandas as pd, gc
    V3 = load('fitb_v3', D / 'stage9_b2_fitb_v3.py'); V2, V1 = V3.V2, V3.V1
    V1.check_frozen(); V2.check_dev(); setup()
    if (ROOT4 / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present in the v4 root: stop')
    t0 = time.monotonic(); pok, pwhy = V3.provenance_ok(OLD)
    if pok:
        V1.log('BRANCH reuse (part (a) from', OLD / 'fitA_k3', '):', pwhy); sa, rows = V2.gate_a(OLD, model=V3._NoModel())
    else:
        V1.log('BRANCH reload:', pwhy); model, hf = V2.runner_loader(); sa, rows = V3.gate_a_fresh(ROOT4 / 'fitA_k3_v4', model); del model, hf
    gc.collect(); torch.cuda.empty_cache(); V1.log(f'D12-1 (a) Fit A k={V2.K} bitwise:', sa)
    okb, rb, info = gate_b(V1); rows += rb
    st = 'PASS' if sa == 'PASS' and okb else 'FAIL'
    df = V1.COLS.check(pd.DataFrame(rows, columns=V1.COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); df.to_csv(ROOT4 / 'summary/gate_v2.csv', index=False)
    (ROOT4 / 'summary/gate_v2.json').write_text(json.dumps(dict(status=st, rule='D12-1 with D12-5: (a) Fit A prompts 1-3 bitwise == stored prefix states; (b) Fit B prompt 66 vs log, fp32 as logged',
                                                               runner='stage9_b2_fitb_v4.py', record=str(REC), record_sha256=sha(REC), info_f64=info,
                                                               seconds=round(time.monotonic() - t0), rows=rows, at=V1.now()), indent=1, default=float))
    print('HARD CHECK D12-1/D12-5 (gate v4)', st, flush=True)
    if st != 'PASS': (ROOT4 / 'HARD_CHECK_FAILED').write_text(json.dumps(rows, default=float))
    return st == 'PASS'


def verify():
    ok, why = record_ok()
    if not ok: return False, why
    try: g = json.loads((ROOT4 / 'summary/gate_v2.json').read_text())
    except Exception: return False, 'no v4 gate result'
    if g.get('status') != 'PASS' or g.get('runner') != 'stage9_b2_fitb_v4.py': return False, f'v4 gate status {g.get("status")}'
    if (ROOT4 / 'HARD_CHECK_FAILED').exists(): return False, 'HARD_CHECK_FAILED in the v4 root'
    return True, 'D12-5 record + v4 gate PASS verified'


def status():
    st = load('b2c_status', H / '13_stage13/b2c_status.py')
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): st.status_21(root=ROOT4)
    d = json.loads(buf.getvalue().strip().splitlines()[-1])
    if d.get('next') == 'analyze' and (ROOT4 / 'reports/b2_fitb_report.md').exists(): d.update(next='done', reason='report written (v4 root)')
    ok, why = verify()
    if not ok and d.get('next') not in ('gate_v2',): d.update(next='failed', reason=why)
    print(json.dumps(d), flush=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'setup': print(json.dumps(setup())); return 0
    if cmd == 'gate': return 0 if gate() else 2
    if cmd == 'verify': ok, why = verify(); print('VERIFY', ok, why); return 0 if ok else 3
    if cmd == 'status': status(); return 0
    if cmd in ('gpu', 'analyze'):
        ok, why = verify()
        if not ok: raise SystemExit(f'v4 continuation refused: {why}')
        V2 = load('fitb_v2', D / 'stage9_b2_fitb_v2.py'); sys.argv = ['stage9_b2_fitb_v2.py'] + sys.argv[1:] + ['--root', str(ROOT4)]; V2.main(); return 0
    raise SystemExit('usage: stage9_b2_fitb_v4.py setup|gate|verify|status|gpu ...|analyze')


if __name__ == '__main__':
    sys.exit(main())
