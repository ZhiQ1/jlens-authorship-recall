"""Addendum 12 item 2-1 (batch 2, group C): Stage 9 Fit B resumed from its checkpoint (66/100) to 100/100 with the FROZEN Stage 9
code path, then the holdout comparison Fit A vs Fit B (planned 9B) and the Stage 10 title-specific signal with Fit B on the
Stage 11 sample (1,186 papers) at the fitA layers.

Plan (locked): 381_stage13/config/prereg_addendum12.json item "2-1 Stage 9 Fit B and holdout".
  HARD CHECK (plan): "the resumed run reproduces the stored checkpoint state (the 66 accumulated prompts give the same partial
  matrix, relative diff <= 1e-3)".

New file; the frozen Stage 9 scripts (/scratch/zhang.zhiqi2/jlens/{351_stage9.py, stage9_runner.py, stage9_fullfit.py}, byte-identical
to ~/jlens_work/09_stage9/) are NOT edited. The resume itself runs the frozen command unchanged:
    python /scratch/zhang.zhiqi2/jlens/stage9_fullfit.py run --half B --confirm-fit
under `timeout` (the frozen command runs until 100/100 or the job ends; jlens.fit writes the checkpoint atomically after every
prompt, so a stop between prompts loses at most the prompt in progress). Output stays where the frozen code writes it:
351_stage9/runner_runs/full_B_100_7layers/ (checkpoint.pt -> lens.pt + fit_status.json at 100/100).

Commands (root = 381_stage13/b2_fitb unless --root):
  backup       CPU. Copy the 66-prompt checkpoint to <root>/checkpoint_B066.pt (+ sha256, n_done) BEFORE any resume. Refuses if
               the run checkpoint is no longer at 66 and no backup exists.
  gate         GPU (Stage 9 loader). Early hard check: recompute the per-prompt Jacobian of prompt 66 (the last prompt in the
               checkpoint) with the frozen settings and compare (a) max_l ||J_l||/sqrt(d) and (b) the running-mean change
               max_l ||J_l - S65_l/65|| / (66 ||S65_l/65||) with S65 = S66 - J (S66 = backup) to the values the original run logged
               (351_stage9_full_B.log, 4 significant digits): |new - logged| <= half a unit of the last logged digit + 1e-3 |logged|.
               PASS required before the resume is submitted (exit 2 on FAIL).
  resume       GPU. Frozen command above under timeout (budget = Slurm time left - 3 min); then the frozen `check`. Exit 0 if the
               checkpoint is valid and did not go backwards.
  recompute66  GPU (Stage 9 loader). The literal plan check: fit prompts 1-66 of fit_B again with the frozen settings into
               <root>/recompute66/checkpoint.pt (resumable chunks inside the time budget).
  hardcheck66  CPU. recompute66 (66/66) vs backup: per layer rel. Frobenius of S/66 <= 1e-3 -> PASS; FAIL -> exit 2 and the
               file <root>/HARD_CHECK_FAILED (analysis refuses to run).
  holdout      GPU. 100 frozen holdout WikiText prompts (351_stage9/prompts/holdout.jsonl; disjoint from fit_A, fit_B and the Fit A
               repair prompt), max_seq_len 128, positions >= 16 (jlens valid_position_mask): for each fit layer and lens (fitA, fitB):
               KL(final || lens), top-1 agreement with the final output, top-10 overlap with final, and A vs B top-10 overlap /
               top-1 agreement.  -> <root>/holdout/holdout_stats.npz
  read:<c>:<k> GPU. Stage 10 readout (each author alone after "Authors:", name tokens, log10(1/rank)) with fitA and fitB in one
               forward, Stage 11 sample shard k, condition c in true, false_0..4, delete, layers 16-62 (fitA layers).
               -> <root>/raw/read/<c>/shard_kkk.npz
  gpu          --unit gate|holdout|read:<c>:<k>  or  --all (holdout + read units, claims, skip-if-exists, clean time budget).
  analyze      CPU. Lens matrices (cos, rel. Frobenius, (A-I) vs (B-I), each vs public), holdout table, Stage 10 signal per lens
               (title-specific = true - mean 5 false; total; topic; target / control; target - control within bin;
               fitB - fitA paired), parity of our fitA ranks vs the stored Stage 10 jlens_fitA ranks (WARN only).
               -> <root>/summary/*.csv, 381_stage13/reports/b2_fitb_report.md
  tiny         CPU whole-pipeline test with a tiny random Qwen3 config on real prompts / sample rows (synthetic lenses).
  selftest     hard-check comparators: identical -> PASS, perturbed -> FAIL.
"""
import argparse, hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R9 = BASE / '351_stage9'; R13 = BASE / '381_stage13'
RUN_B = R9 / 'runner_runs/full_B_100_7layers'; LOG_B = BASE / '351_stage9_full_B.log'; FULLFIT = BASE / 'stage9_fullfit.py'
FITA = R9 / 'runner_runs/full_A_repair_101_100valid/lens.pt'
LAYERS = [16, 24, 32, 40, 48, 56, 62]; TOL = 1e-3; N_CK = 66
PLAN = R13 / 'config/prereg_addendum12.json'; PLAN_SHA = (R13 / 'config/prereg_addendum12.json.sha256').read_text().split()[0]
FROZEN_SHA = {'351_stage9.py': None, 'stage9_runner.py': None, 'stage9_fullfit.py': None}   # filled from ~/jlens_work/09_stage9 copies
SEC_PER_PROMPT = 345     # Fit B log: 317-491 s per prompt (Stage 9 loader with 55 GiB GPU cap + CPU offload), median ~330
SEC_PER_READ = 45


def load_mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load_mod(H / '13_stage13/b2c_columns.py', 'b2c_columns')


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')


def log(*x):
    try: print(now(), *x, flush=True)
    except Exception: pass


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def check_frozen():
    """frozen Stage 9 scripts on /scratch must be byte-identical to the backup copies in ~/jlens_work/09_stage9."""
    for n in FROZEN_SHA:
        if sha(BASE / n) != sha(H / '09_stage9' / n): raise SystemExit(f'frozen Stage 9 script changed: {n}')
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED (addendum 12)')


def slurm_minutes_left():
    jid = os.environ.get('SLURM_JOB_ID')
    if not jid: return None
    try:
        s = subprocess.run(['squeue', '-h', '-j', jid, '-o', '%L'], capture_output=True, text=True, timeout=90).stdout.strip()
        d, _, hms = s.rpartition('-'); parts = [int(x) for x in hms.split(':')]
        while len(parts) < 3: parts.insert(0, 0)
        return int(d or 0) * 1440 + parts[0] * 60 + parts[1] + parts[2] / 60
    except Exception: return None


def minutes_left(t0, default):
    left = slurm_minutes_left(); el = (time.monotonic() - t0) / 60
    return (default - el) if left is None else min(default - el, left - 3)


def fit_b_prompts(n=100):
    rows = [json.loads(x) for x in (R9 / 'prompts/fit_B.jsonl').read_text().splitlines() if x.strip()][:n]
    assert all(hashlib.sha256(r['text'].encode()).hexdigest() == r['text_sha256'] for r in rows)
    cfg = json.loads((RUN_B / 'fitting_config.json').read_text())
    if [r['text_sha256'] for r in rows] != cfg['prompt_ids'][:n]: raise SystemExit('fit_B prompt ids differ from the frozen run config')
    return [r['text'] for r in rows]


def stage9_loader():
    """the model load of the frozen stage9_fullfit.execute (same arguments)."""
    import torch, transformers, jlens
    tok = transformers.AutoTokenizer.from_pretrained('Qwen/Qwen3-32B', revision='9216db5781bf21249d130ec9da846c4624c16137')
    hf = transformers.AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-32B', revision='9216db5781bf21249d130ec9da846c4624c16137',
                     torch_dtype=torch.bfloat16, device_map='auto', max_memory={0: '55GiB', 'cpu': '36GiB'}, low_cpu_mem_usage=True)
    return jlens.from_hf(hf, tok)


# ------------------------------------------------------------------ backup of the 66-prompt checkpoint
def backup(root):
    import torch
    root.mkdir(parents=True, exist_ok=True); dst = root / 'checkpoint_B066.pt'; meta = root / 'checkpoint_B066.json'
    if dst.exists() and meta.exists():
        m = json.loads(meta.read_text())
        if sha(dst) != m['sha256']: raise SystemExit('backup checkpoint sha256 changed')
        log('backup exists', m); return m
    st = torch.load(RUN_B / 'checkpoint.pt', map_location='cpu', weights_only=True)
    if (st['n_done'], st['next_idx']) != (N_CK, N_CK): raise SystemExit(f'run checkpoint is at {st["n_done"]}/{st["next_idx"]}, not 66: no backup possible')
    tmp = root / 'checkpoint_B066.pt.tmp'; shutil.copy2(RUN_B / 'checkpoint.pt', tmp); os.replace(tmp, dst)
    m = dict(sha256=sha(dst), source=str(RUN_B / 'checkpoint.pt'), source_sha256=sha(RUN_B / 'checkpoint.pt'), n_done=N_CK, copied=now())
    if m['sha256'] != m['source_sha256']: raise SystemExit('copy differs from source')
    meta.write_text(json.dumps(m, indent=1)); log('backup written', m); return m


def backup_ok(root):
    meta = root / 'checkpoint_B066.json'
    return meta.exists() and (root / 'checkpoint_B066.pt').exists() and sha(root / 'checkpoint_B066.pt') == json.loads(meta.read_text())['sha256']


# ------------------------------------------------------------------ gate: prompt 66 vs the logged statistics
RX = re.compile(r'prompt (\d+)/(\d+)\s+seq_len=(\d+) n_valid=(\d+)\s+\d+s\s+max\|\|J\|\|/sqrt\(d\)=([0-9.]+)\s+max_d_mean=([0-9.e+\-]+|nan)')


def logged_stats(path, k):
    """last logged (norm, d_mean, seq_len, n_valid) of prompt k (1-based) and their printed precisions."""
    hit = None
    for line in Path(path).read_text(errors='replace').splitlines():
        m = RX.search(line)
        if m and int(m.group(1)) == k: hit = m
    if hit is None: raise SystemExit(f'prompt {k} not in {path}')
    nv, dv = hit.group(5), hit.group(6)
    unit_n = 10 ** -len(nv.split('.')[1]) if '.' in nv else 1.0
    mant, _, ex = dv.partition('e'); unit_d = 10 ** (-len(mant.split('.')[1]) + int(ex or 0)) if dv != 'nan' else float('nan')
    return dict(norm=float(nv), norm_unit=unit_n, d_mean=float(dv), d_mean_unit=unit_d, seq_len=int(hit.group(3)), n_valid=int(hit.group(4)))


def gate_compare(J, S66, n_ck, ref, d_model):
    """J: per-prompt Jacobians {layer: T} of prompt n_ck; S66: summed checkpoint. Returns (status, rows)."""
    sq = math.sqrt(d_model)
    norm = max(J[l].double().norm().item() for l in J) / sq
    S65 = {l: S66[l].double() - J[l].double() for l in J}; n = n_ck - 1
    dm = max(((J[l].double() - S65[l] / n).norm() / ((n + 1) * (S65[l] / n).norm())).item() for l in J)
    rows = []
    for name, v, r, u in (('max_norm_over_sqrt_d', norm, ref['norm'], ref['norm_unit']), ('max_d_mean', dm, ref['d_mean'], ref['d_mean_unit'])):
        thr = 0.5 * u + TOL * abs(r); st = 'PASS' if abs(v - r) <= thr else 'FAIL'
        rows.append(dict(check=f'gate_prompt{n_ck}_{name}', layer=-1, value=v, reference=r, rel_diff=abs(v - r) / abs(r), threshold=thr, status=st))
    return ('PASS' if all(r['status'] == 'PASS' for r in rows) else 'FAIL'), rows


def gate(root, model=None, prompts=None, log_path=LOG_B, n_ck=N_CK, layers=LAYERS, target_layer=63):
    import torch, jlens, pandas as pd
    if not backup_ok(root): raise SystemExit('no verified backup of the 66-prompt checkpoint: run backup first')
    ref = logged_stats(log_path, n_ck); st = torch.load(root / 'checkpoint_B066.pt', map_location='cpu', weights_only=True)
    model = model or stage9_loader(); prompts = prompts or fit_b_prompts()
    t0 = time.monotonic()
    J, seq_len, n_valid = jlens.jacobian_for_prompt(model, prompts[n_ck - 1], layers, target_layer=target_layer, dim_batch=1, max_seq_len=128, skip_first=16)
    status, rows = gate_compare(J, st['jacobian_sum'], n_ck, ref, model.d_model)
    rows.append(dict(check=f'gate_prompt{n_ck}_seq_len', layer=-1, value=seq_len, reference=ref['seq_len'], rel_diff=0.0 if seq_len == ref['seq_len'] else 1.0, threshold=0, status='PASS' if seq_len == ref['seq_len'] and n_valid == ref['n_valid'] else 'FAIL'))
    if rows[-1]['status'] != 'PASS': status = 'FAIL'
    df = COLS.check(pd.DataFrame(rows, columns=COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); (root / 'summary').mkdir(parents=True, exist_ok=True)
    df.to_csv(root / 'summary/gate.csv', index=False)
    (root / 'summary/gate.json').write_text(json.dumps(dict(status=status, seconds=round(time.monotonic() - t0), rows=rows, at=now()), indent=1, default=float))
    log('GATE', status, rows)
    return status == 'PASS'


def gate_passed(root):
    f = root / 'summary/gate.json'; return f.exists() and json.loads(f.read_text())['status'] == 'PASS'


# ------------------------------------------------------------------ resume (frozen command)
def resume(root, budget_min):
    import torch
    if not backup_ok(root): raise SystemExit('no verified backup of the 66-prompt checkpoint: refuse to resume')
    if not gate_passed(root): raise SystemExit('gate not PASS: refuse to resume')
    if (RUN_B / 'fit_status.json').exists(): log('Fit B already complete (fit_status.json)'); return True
    before = torch.load(RUN_B / 'checkpoint.pt', map_location='cpu', weights_only=True)['next_idx']
    secs = int(budget_min * 60)
    if secs < SEC_PER_PROMPT + 300: log(f'not enough time ({budget_min:.1f} min) for load + 1 prompt'); return True
    cmd = ['timeout', '--signal=TERM', '--kill-after=60', str(secs), sys.executable, '-u', str(FULLFIT), 'run', '--half', 'B', '--confirm-fit']
    log('RUN (frozen):', ' '.join(cmd)); rc = subprocess.run(cmd, cwd=str(BASE)).returncode
    log('frozen run exit code', rc, '(124 = stopped by timeout at the time budget)')
    chk = subprocess.run([sys.executable, str(FULLFIT), 'check', '--half', 'B'], cwd=str(BASE), capture_output=True, text=True)
    print(chk.stdout, chk.stderr, flush=True)
    after = torch.load(RUN_B / 'checkpoint.pt', map_location='cpu', weights_only=True)['next_idx']
    rec = dict(job=os.environ.get('SLURM_JOB_ID'), before=before, after=after, rc=rc, check_rc=chk.returncode, at=now())
    try:
        with open(root / 'resume_log.jsonl', 'a') as f: f.write(json.dumps(rec) + '\n')
    except Exception as e: log('log warning', repr(e))
    for t in RUN_B.glob('checkpoint.pt.tmp.*'): log('WARN leftover temp checkpoint (job stopped during a save; not deleted):', t)
    if chk.returncode != 0 or after < before: log('RESUME CHECK FAILED', rec); return False
    if rc not in (0, 124, 137, 143): log('WARN frozen run ended with code', rc, '(checkpoint valid; continuing)')
    return True


# ------------------------------------------------------------------ recompute66 + hard check
def recompute66(root, model, budget_min, prompts=None, n_ck=N_CK, layers=LAYERS, target_layer=63, sec_per_prompt=SEC_PER_PROMPT):
    import jlens, torch
    d = root / 'recompute66'; d.mkdir(parents=True, exist_ok=True); cp = d / 'checkpoint.pt'
    done = torch.load(cp, map_location='cpu', weights_only=True)['next_idx'] if cp.exists() else 0
    if done >= n_ck: log('recompute66 complete'); return True
    n = int((budget_min * 60 - 60) // sec_per_prompt)
    if n < 1: log('recompute66: no time for one prompt'); return False
    target = min(n_ck, done + n); prompts = prompts or fit_b_prompts()
    log(f'recompute66: {done} -> {target} of {n_ck}')
    jlens.fit(model, prompts[:target], source_layers=layers, target_layer=target_layer, dim_batch=1, max_seq_len=128, skip_first=16,
              checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
    return target >= n_ck


def compare66(A, B, layers, n_ck, tol=TOL):
    """A = recomputed state, B = stored backup state (dicts with jacobian_sum, n_done, next_idx)."""
    rows = []; ok = (A['n_done'], A['next_idx'], B['n_done'], B['next_idx']) == (n_ck,) * 4
    rows.append(dict(check='counts', layer=-1, value=A['n_done'], reference=B['n_done'], rel_diff=0.0 if ok else 1.0, threshold=0, status='PASS' if ok else 'FAIL'))
    for l in layers:
        x, y = A['jacobian_sum'][l].double() / n_ck, B['jacobian_sum'][l].double() / n_ck
        r = float((x - y).norm() / y.norm()); st = 'PASS' if r <= tol else 'FAIL'; ok &= st == 'PASS'
        rows.append(dict(check='partial_matrix_relfro', layer=l, value=r, reference=0.0, rel_diff=r, threshold=tol, status=st))
    return ('PASS' if ok else 'FAIL'), rows


def hardcheck66(root, layers=LAYERS, n_ck=N_CK):
    import torch, pandas as pd
    A = torch.load(root / 'recompute66/checkpoint.pt', map_location='cpu', weights_only=True)
    B = torch.load(root / 'checkpoint_B066.pt', map_location='cpu', weights_only=True)
    st, rows = compare66(A, B, layers, n_ck)
    df = COLS.check(pd.DataFrame(rows, columns=COLS.FITB_HARDCHECK), 'FITB_HARDCHECK'); (root / 'summary').mkdir(parents=True, exist_ok=True)
    df.to_csv(root / 'summary/hardcheck66.csv', index=False)
    (root / 'summary/hardcheck66.json').write_text(json.dumps(dict(status=st, rows=rows, at=now()), indent=1, default=float))
    print('HARD CHECK (66-prompt partial matrix)', st, 'max rel', float(df[df.check == 'partial_matrix_relfro'].rel_diff.max()), flush=True)
    if st != 'PASS': (root / 'HARD_CHECK_FAILED').write_text(json.dumps(rows, default=float))
    return st == 'PASS'


# ------------------------------------------------------------------ holdout and Stage 10 read (Stage 10 loader)
def holdout_prompts(n=None):
    rows = [json.loads(x) for x in (R9 / 'prompts/holdout.jsonl').read_text().splitlines() if x.strip()]
    used = {json.loads(x)['text_sha256'] for f in ('fit_A.jsonl', 'fit_B.jsonl') for x in (R9 / 'prompts' / f).read_text().splitlines() if x.strip()}
    rep = json.loads((R9 / 'runner_runs/full_A_repair_101_100valid/repair_manifest.json').read_text())['replacement']['text_sha256']; used.add(rep)
    rows = [r for r in rows if r['text_sha256'] not in used]
    return [r['text'] for r in rows][:n]


def holdout(root, model, LS, prompts, layers=LAYERS):
    """per prompt sums over valid positions; LS = {'fitA': lens, 'fitB': lens} on the model devices."""
    import torch
    from jlens.hooks import ActivationRecorder
    from jlens.fitting import valid_position_mask
    out = {k: [] for k in ['n_pos'] + [f'{s}@{n}@{l}' for n in LS for l in layers for s in ('kl', 'top1f', 'top10f')] +
           [f'{s}@AB@{l}' for l in layers for s in ('top10AB', 'top1AB')]}
    last = model.n_layers - 1
    for t in prompts:
        ids = model.encode(t, max_length=128); m = valid_position_mask(ids.shape[1], skip_first=16)
        if int(m.sum()) == 0: continue
        with torch.inference_mode(), ActivationRecorder(model.layers, at=layers + [last]) as rec:
            model.forward(ids)
            pos = torch.nonzero(m.to(ids.device)).flatten() if torch.is_tensor(m) else torch.tensor(np.nonzero(np.asarray(m))[0], device=ids.device)
            fl = model.unembed(rec.activations[last][0][pos]).float(); lpf = torch.log_softmax(fl, -1); t1f = fl.argmax(-1); t10f = fl.topk(10, -1).indices
            out['n_pos'].append(len(pos)); tk = {}
            for n, L in LS.items():
                for l in layers:
                    lg = model.unembed(L.transport(rec.activations[l][0][pos].float(), l)).float().to(fl.device); lp = torch.log_softmax(lg, -1)
                    out[f'kl@{n}@{l}'].append(float((lpf.exp() * (lpf - lp)).sum(-1).sum()))
                    out[f'top1f@{n}@{l}'].append(float((lg.argmax(-1) == t1f).sum()))
                    t10 = lg.topk(10, -1).indices; tk[(n, l)] = t10
                    out[f'top10f@{n}@{l}'].append(float(sum(len(set(a.tolist()) & set(b.tolist())) for a, b in zip(t10, t10f)) / 10))
            for l in layers:
                a_, b_ = tk[('fitA', l)], tk[('fitB', l)]
                out[f'top10AB@AB@{l}'].append(float(sum(len(set(x.tolist()) & set(y.tolist())) for x, y in zip(a_, b_)) / 10))
                out[f'top1AB@AB@{l}'].append(float((a_[:, 0] == b_[:, 0]).sum()))
    f = root / 'holdout/holdout_stats.npz'; f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f'holdout_stats.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(created=now(), n_prompts=len(prompts)))), **{k: np.array(v) for k, v in out.items()}); os.replace(tmp, f)
    log('holdout written', f)


def read_path(root, c, k): return root / f'raw/read/{c}/shard_{k:03d}.npz'


def do_read(C, LS, cond, shard, layers):
    torch = C.torch; prompts = C.prompts[cond]; s11 = C.s11
    out = {f'{n}@{l}': [] for n in LS for l in layers}; rows = []
    from jlens.hooks import ActivationRecorder
    for r in C.smp[C.smp.shard == shard].itertuples():
        ptx, pids = prompts[r.paper_id]
        for ai, rids, name in C.ctx[r.paper_id]:
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]; g = torch.tensor(name, device=C.model.input_device)
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=layers) as rec:
                C.model.forward(torch.tensor([ids], device=C.model.input_device))
                for n, L in LS.items():
                    for l in layers:
                        lg = C.model.unembed(L.transport(rec.activations[l][0][pos].float(), l)).float(); out[f'{n}@{l}'].append(s11.ranks(lg, g, torch))
            rows += rids
    return dict(row_id=np.array(rows), **{k: np.concatenate(v) for k, v in out.items()})


def read_unit(C, LS, root, c, k, layers):
    f = read_path(root, c, k)
    if f.exists(): return 0.0
    t1 = time.monotonic(); d = do_read(C, LS, c, k, layers); f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(created=now(), cond=c, shard=k, **C.env))), **d); os.replace(tmp, f)
    dt = time.monotonic() - t1; log(f'read {c} shard {k:03d} rows={len(d["row_id"])} {dt:.0f}s'); return dt


def load_lens(path, model, s10):
    import jlens
    L = jlens.JacobianLens.load(str(path))
    for k in list(L.jacobians): L.jacobians[k] = L.jacobians[k].to(s10.layer_device(model, k))
    return L


class GCtx:
    def __init__(self):
        import torch, pandas as pd
        s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); self.s11, self.s10 = s12.s11, s12.s10
        self.torch = torch; self.papers, toks = self.s11.cohort(); self.ctx = self.s11.contexts_of(toks)
        self.prompts = {c: self.s10.condition_prompts(self.s11.R10, self.papers, c)[0] for c in self.s10.condition_names()}
        self.smp = pd.read_parquet(self.s11.ROOT / 'config/sample.parquet'); self.model, self.tok = self.s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], job=os.environ.get('SLURM_JOB_ID'))


def fitb_lens_path():
    return RUN_B / 'lens.pt' if (RUN_B / 'fit_status.json').exists() else None


def gpu(a, root):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    if a.unit == 'gate':
        ok = gate(root); sys.exit(0 if ok else 2)
    if a.unit == 'resume':
        sys.exit(0 if resume(root, minutes_left(t0, a.minutes)) else 2)
    if a.unit == 'recompute66':
        model = stage9_loader(); done = recompute66(root, model, minutes_left(t0, a.minutes))
        if done: sys.exit(0 if hardcheck66(root) else 2)
        return
    fb = fitb_lens_path()
    if fb is None: raise SystemExit('Fit B is not complete (no fit_status.json): holdout/read wait')
    C = GCtx(); LS = {'fitA': load_lens(FITA, C.model, C.s10), 'fitB': load_lens(fb, C.model, C.s10)}
    units = [a.unit] if a.unit else ['holdout'] + [f'read:{c}:{k}' for c in C.s10.condition_names() for k in range(24)]
    CL = root / 'logs/claims'; CL.mkdir(parents=True, exist_ok=True); last = SEC_PER_READ
    for u in units:
        if minutes_left(t0, a.minutes) * 60 < 1.5 * last + 30: log('budget: stop before next unit'); return
        if u == 'holdout':
            if (root / 'holdout/holdout_stats.npz').exists(): continue
            if not a.unit and not C.s11.claim(CL / 'holdout', me): continue
            t1 = time.monotonic(); holdout(root, C.model, LS, holdout_prompts()); last = max(last, time.monotonic() - t1); continue
        _, c, k = u.split(':'); k = int(k)
        if read_path(root, c, k).exists(): continue
        if not a.unit and not C.s11.claim(CL / f'read_{c}_{k:03d}', me): continue
        last = max(read_unit(C, LS, root, c, k, LAYERS), 1.0)
    log('gpu: no unit left for this job')


# ------------------------------------------------------------------ analysis (CPU)
def analyze(root, layers=LAYERS, conds=None, lens_paths=None, s10_layers=(24, 32, 40, 48, 56, 62)):
    import torch, pandas as pd, jlens
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: no analysis')
    s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); s11, s10 = s12.s11, s12.s10
    a12 = load_mod(H / '12_stage12/stage12_analyze.py', 's12a')
    W = []
    def warn(m):
        W.append(m)
        try: print('WARN', m, flush=True)
        except Exception: pass
    S = root / 'summary'; S.mkdir(parents=True, exist_ok=True)
    lp = lens_paths or dict(fitA=FITA, fitB=RUN_B / 'lens.pt', public=json.loads((s11.R10 / 'config/lenses.json').read_text())['public']['path'])
    LA, LB = jlens.JacobianLens.load(str(lp['fitA'])), jlens.JacobianLens.load(str(lp['fitB'])); LP = jlens.JacobianLens.load(str(lp['public'])) if lp.get('public') else None
    cos = lambda x, y: float((x.flatten().double() @ y.flatten().double()) / (x.flatten().double().norm() * y.flatten().double().norm()))
    eye = torch.eye(LA.jacobians[layers[0]].shape[0]); mr = []
    for l in layers:
        A, Bm = LA.jacobians[l].float(), LB.jacobians[l].float()
        r = dict(layer=l, cos_A_B=cos(A, Bm), relfro_A_B=float((A - Bm).double().norm() / A.double().norm()), cos_A_B_minus_I=cos(A - eye, Bm - eye),
                 normA=float(A.double().norm()), normB=float(Bm.double().norm()), cos_A_public=np.nan, cos_B_public=np.nan)
        if LP is not None and l in LP.jacobians: P = LP.jacobians[l].float(); r['cos_A_public'] = cos(A, P); r['cos_B_public'] = cos(Bm, P)
        mr.append(r)
    M = COLS.check(pd.DataFrame(mr)[COLS.FITB_MATRIX], 'FITB_MATRIX'); M.to_csv(S / 'fitb_matrix.csv', index=False)
    # holdout
    HO = pd.DataFrame(columns=COLS.FITB_HOLDOUT)
    hf = root / 'holdout/holdout_stats.npz'
    if hf.exists():
        z = np.load(hf); npos = z['n_pos'].sum(); hr = []
        for n in ('fitA', 'fitB'):
            for l in layers:
                hr.append(dict(layer=l, lens=n, n_positions=int(npos), kl_final_mean=float(z[f'kl@{n}@{l}'].sum() / npos),
                               kl_final_median=float(np.median(z[f'kl@{n}@{l}'] / z['n_pos'])), top1_final_agree=float(z[f'top1f@{n}@{l}'].sum() / npos),
                               top10_overlap_final=float(z[f'top10f@{n}@{l}'].sum() / npos), top10_overlap_A_B=float(z[f'top10AB@AB@{l}'].sum() / npos),
                               top1_A_B_agree=float(z[f'top1AB@AB@{l}'].sum() / npos)))
        HO = COLS.check(pd.DataFrame(hr)[COLS.FITB_HOLDOUT], 'FITB_HOLDOUT')
    else: warn('holdout stats missing')
    HO.to_csv(S / 'fitb_holdout.csv', index=False)
    # Stage 10 readout
    conds = conds or s10.condition_names()
    toks = pd.read_parquet(s11.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); nlr = lambda x: -np.log10(np.asarray(x, float))
    per, par = {}, []
    for c in conds:
        fs = sorted((root / f'raw/read/{c}').glob('shard_*.npz'))
        if not fs: warn(f'no read output for {c}'); continue
        zs = [np.load(f) for f in fs]; hz = {k: np.concatenate([z[k] for z in zs]) for k in zs[0].files if k != 'meta'}
        if c in ('true',) or c.startswith('false') or c == 'delete':          # parity of fitA vs stored Stage 10 ranks
            sub = 'jlens_fitA' if c == 'true' else f'cond_{c}/jlens_fitA'
            for l in s10_layers:
                try:
                    st = [np.load(f) for f in sorted((s11.R10 / f'raw/{sub}/L{l}').glob('shard_*.npz'))]
                    if not st: continue
                    sr = pd.Series(np.concatenate([x['rank'] for x in st]), index=np.concatenate([x['row_id'] for x in st]))
                    ours = pd.Series(hz[f'fitA@{l}'], index=hz['row_id']); j = sr.reindex(ours.index)
                    ok = j.notna(); x, y = ours[ok].to_numpy(float), j[ok].to_numpy(float)
                    eq = float((x == y).mean()) if ok.any() else float('nan'); md = float(np.abs(nlr(x) - nlr(y)).max()) if ok.any() else float('nan')
                    st_ = 'PASS' if eq >= 0.95 else 'WARN'
                    par.append(dict(cond=c, layer=l, n_rows=int(ok.sum()), share_rank_equal=eq, max_abs_log10rank_diff=md,
                                    mean_abs_log10rank_diff=float(np.abs(nlr(x) - nlr(y)).mean()) if ok.any() else float('nan'), threshold=0.95, status=st_))
                    if st_ != 'PASS' or ok.mean() < 1: warn(f'{c} L{l}: fitA ranks equal to stored Stage 10 for {eq:.3f} of {int(ok.sum())} rows (threshold 0.95; rows found {ok.mean():.3f})')
                except Exception as e: warn(f'parity {c} L{l} not run: {e!r}')
        df = pd.DataFrame({'row_id': hz['row_id'], **{k: nlr(v) for k, v in hz.items() if '@' in k}})
        per[c] = df.merge(toks, on='row_id').drop(columns='row_id').groupby('paper_id').mean()
    PA = COLS.check(pd.DataFrame(par, columns=COLS.FITB_PARITY), 'FITB_PARITY'); PA.to_csv(S / 'fitb_parity_fitA_vs_stage10.csv', index=False)
    rows = []
    falses = [c for c in per if c.startswith('false')]
    if 'true' in per and falses:
        common = per['true'].index
        for c in per: common = common.intersection(per[c].index)
        fm_ = sum(per[c].loc[common] for c in falses) / len(falses)
        meas = {'spec': per['true'].loc[common] - fm_}
        if 'delete' in per: meas |= {'total': per['true'].loc[common] - per['delete'].loc[common], 'topic': fm_ - per['delete'].loc[common]}
        for mname, mm in meas.items():
            spj = mm.join(smp.set_index('paper_id'))
            for l in layers:
                for n in ('fitA', 'fitB', 'B_minus_A'):
                    col = f'{n}@{l}'
                    if n == 'B_minus_A': spj[col] = spj[f'fitB@{l}'] - spj[f'fitA@{l}']
                    for g in ('target', 'control', 'all'):
                        v = spj[col] if g == 'all' else spj[spj.group == g][col]
                        e = a12.boot(v) if len(v.dropna()) else (np.nan,) * 3
                        t = a12.strat(spj, col) if g == 'all' else (np.nan,) * 3
                        rows.append(dict(lens=n if mname == 'spec' else f'{n}:{mname}', layer=l, group=g, spec=e[0], lo=e[1], hi=e[2], n_papers=int(v.notna().sum()), tc=t[0], tc_lo=t[1], tc_hi=t[2], tc_bins=np.nan))
    SG = COLS.check(pd.DataFrame(rows, columns=COLS.FITB_SIGNAL), 'FITB_SIGNAL'); SG.to_csv(S / 'fitb_stage10_signal.csv', index=False)
    # report
    try:
        f3 = lambda e, lo, hi: '-' if pd.isna(e) else f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')
        g66 = json.loads((S / 'hardcheck66.json').read_text()) if (S / 'hardcheck66.json').exists() else {'status': 'not run', 'rows': []}
        gg = json.loads((S / 'gate.json').read_text()) if (S / 'gate.json').exists() else {'status': 'not run', 'rows': []}
        L = ['# Addendum 12 item 2-1: Stage 9 Fit B (resumed to 100/100), Fit A vs Fit B, Stage 10 signal with Fit B', '',
             'Plan `381_stage13/config/prereg_addendum12.json` item 2-1. Script `09_stage9/stage9_b2_fitb.py`; the resume ran the frozen '
             '`stage9_fullfit.py run --half B --confirm-fit` unchanged (Stage 9 scripts byte-identical to `09_stage9/`).', '',
             f'Fit A: {LA.n_prompts} prompts (`full_A_repair_101_100valid`); Fit B: {LB.n_prompts} prompts (`full_B_100_7layers`).', '',
             f'## Hard checks', '', f'- Gate (prompt 66 recomputed vs the logged per-prompt statistics): **{gg["status"]}**']
        for r in gg['rows']: L.append(f'  - {r["check"]}: {r["value"]:.5g} vs logged {r["reference"]:.5g} (|diff| threshold {r["threshold"]:.2g}) {r["status"]}')
        L += [f'- Plan hard check (prompts 1-66 refitted vs the stored 66-prompt checkpoint, rel. Frobenius <= 1e-3): **{g66["status"]}**']
        for r in g66['rows']: L.append(f'  - {r["check"]} L{r["layer"]}: {r["value"]:.3g} {r["status"]}')
        L += ['', '## Checks (WARN = value and threshold; the run continued)', '', *(['- ' + w for w in W] or ['- No WARN.']), '',
              '## Fit A vs Fit B lens matrices', '', '| layer | cos A,B | rel. Frob. (A-B)/A | cos (A-I),(B-I) | ||A|| | ||B|| | cos A,public | cos B,public |', '|---|---|---|---|---|---|---|---|']
        for _, r in M.iterrows(): L.append(f'| L{int(r.layer)} | {r.cos_A_B:.4f} | {r.relfro_A_B:.4f} | {r.cos_A_B_minus_I:.4f} | {r.normA:.1f} | {r.normB:.1f} | {r.cos_A_public:.3f} | {r.cos_B_public:.3f} |')
        if len(HO):
            L += ['', f'## Holdout ({int(HO.n_positions.iloc[0])} positions of the frozen holdout WikiText prompts, positions >= 16)', '',
                  '| layer | KL(final, A) | KL(final, B) | top-1 = final A | top-1 = final B | top-10 overlap w/ final A | B | top-10 overlap A,B | top-1 A = B |', '|---|---|---|---|---|---|---|---|---|']
            for l in layers:
                a_, b_ = HO[(HO.layer == l) & (HO.lens == 'fitA')].iloc[0], HO[(HO.layer == l) & (HO.lens == 'fitB')].iloc[0]
                L.append(f'| L{l} | {a_.kl_final_mean:.3f} | {b_.kl_final_mean:.3f} | {a_.top1_final_agree:.3f} | {b_.top1_final_agree:.3f} | {a_.top10_overlap_final:.3f} | {b_.top10_overlap_final:.3f} | {a_.top10_overlap_A_B:.3f} | {a_.top1_A_B_agree:.3f} |')
        if len(SG):
            L += ['', '## Stage 10 title-specific signal on the Stage 11 sample (true - mean of 5 false titles, log10(1/rank), paper means)', '',
                  'Paper bootstrap (Stage 10 / F2 scheme, stage12_analyze.boot / strat); target - control within citation bin; * = CI excludes 0.', '',
                  '| layer | lens | target | control | all | target - control |', '|---|---|---|---|---|---|']
            for l in layers:
                for n in ('fitA', 'fitB', 'B_minus_A'):
                    s = SG[(SG.lens == n) & (SG.layer == l)].set_index('group')
                    if len(s): L.append(f'| L{l} | {n} | ' + ' | '.join(f3(s.loc[g, 'spec'], s.loc[g, 'lo'], s.loc[g, 'hi']) for g in ('target', 'control', 'all')) + f' | {f3(s.loc["all", "tc"], s.loc["all", "tc_lo"], s.loc["all", "tc_hi"])} |')
            call = lambda lo, hi: 'pos' if lo > 0 else ('neg' if hi < 0 else 'n.s.')
            ch = []
            for l in layers:
                for g in ('target', 'control', 'all'):
                    a_ = SG[(SG.lens == 'fitA') & (SG.layer == l) & (SG.group == g)]; b_ = SG[(SG.lens == 'fitB') & (SG.layer == l) & (SG.group == g)]
                    if len(a_) and len(b_) and call(a_.lo.iloc[0], a_.hi.iloc[0]) != call(b_.lo.iloc[0], b_.hi.iloc[0]): ch.append(f'L{l} {g}: fitA {call(a_.lo.iloc[0], a_.hi.iloc[0])} -> fitB {call(b_.lo.iloc[0], b_.hi.iloc[0])}')
                a_ = SG[(SG.lens == 'fitA') & (SG.layer == l) & (SG.group == 'all')]; b_ = SG[(SG.lens == 'fitB') & (SG.layer == l) & (SG.group == 'all')]
                if len(a_) and len(b_) and call(a_.tc_lo.iloc[0], a_.tc_hi.iloc[0]) != call(b_.tc_lo.iloc[0], b_.tc_hi.iloc[0]): ch.append(f'L{l} target-control: fitA {call(a_.tc_lo.iloc[0], a_.tc_hi.iloc[0])} -> fitB {call(b_.tc_lo.iloc[0], b_.tc_hi.iloc[0])}')
            L += ['', 'CI-call changes fitA -> fitB (title-specific): ' + ('; '.join(ch) if ch else 'none')]
        L += ['', '## Conclusion', '', '<!--CONCLUSION: written by the main session after review-->', '']
        rep = R13 / 'reports/b2_fitb_report.md' if root == R13 / 'b2_fitb' else root / 'reports/b2_fitb_report.md'
        rep.parent.mkdir(parents=True, exist_ok=True); rep.write_text('\n'.join(L) + '\n'); print('wrote', rep, flush=True)
    except Exception:
        print('WARN report writing failed', flush=True); traceback.print_exc()


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU)
def tiny(root):
    import logging, torch, transformers, jlens, pandas as pd
    s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); s11, s10 = s12.s11, s12.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok); s10.layer_device = lambda m, k: 'cpu'
    lay, tl, nck = [0, 1, 2], 3, 3; checks = {}
    prompts = fit_b_prompts()[:nck]
    # 1. "stored" tiny run: fit 3 prompts with a checkpoint and the jlens log -> fake RUN dir + log
    sroot = root / 'stored'; sroot.mkdir(parents=True, exist_ok=True); lf = root / 'stored_fit.log'
    hdl = logging.FileHandler(lf); hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')); lg = logging.getLogger('jlens'); lg.addHandler(hdl); lg.setLevel(logging.INFO)
    jlens.fit(model, prompts, source_layers=lay, target_layer=tl, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=str(sroot / 'checkpoint.pt'), checkpoint_every=1)
    lg.removeHandler(hdl); hdl.close()
    shutil.copy2(sroot / 'checkpoint.pt', root / 'checkpoint_B066.pt'); (root / 'checkpoint_B066.json').write_text(json.dumps(dict(sha256=sha(root / 'checkpoint_B066.pt'), n_done=nck)))
    checks['backup verified'] = backup_ok(root)
    # 2. gate on prompt nck vs the tiny log
    checks['gate identical -> PASS'] = gate(root, model=model, prompts=prompts, log_path=lf, n_ck=nck, layers=lay, target_layer=tl)
    txt = lf.read_text(); m = RX.search([x for x in txt.splitlines() if f'prompt {nck}/' in x][-1]); bad = txt.replace(f'max||J||/sqrt(d)={m.group(5)}', f'max||J||/sqrt(d)={float(m.group(5)) * 1.01:.3f}')
    (root / 'stored_fit_bad.log').write_text(bad)
    checks['gate perturbed log -> FAIL'] = not gate(root, model=model, prompts=prompts, log_path=root / 'stored_fit_bad.log', n_ck=nck, layers=lay, target_layer=tl)
    gate(root, model=model, prompts=prompts, log_path=lf, n_ck=nck, layers=lay, target_layer=tl)          # leave a PASS gate behind
    # 3. recompute (2 chunks: budget for 1 prompt, then the rest) + hard check; perturbed -> FAIL
    recompute66(root, model, budget_min=(60 + 30) / 60, prompts=prompts, n_ck=nck, layers=lay, target_layer=tl, sec_per_prompt=30)
    recompute66(root, model, budget_min=60, prompts=prompts, n_ck=nck, layers=lay, target_layer=tl, sec_per_prompt=30)
    checks['hard check 66 identical -> PASS'] = hardcheck66(root, layers=lay, n_ck=nck)
    A = torch.load(root / 'recompute66/checkpoint.pt', weights_only=True); B = torch.load(root / 'checkpoint_B066.pt', weights_only=True)
    Bp = dict(B); Bp['jacobian_sum'] = {l: v * 1.01 for l, v in B['jacobian_sum'].items()}
    checks['hard check 66 perturbed 1% -> FAIL'] = compare66(A, Bp, lay, nck)[0] == 'FAIL'
    # 4. frozen Stage 9 code path, read-only: `stage9_fullfit.py check --half B` on the real run (must report done=66)
    chk = subprocess.run([sys.executable, str(FULLFIT), 'check', '--half', 'B'], cwd=str(BASE), capture_output=True, text=True); print(chk.stdout[-600:], chk.stderr[-600:], flush=True)
    checks['frozen check runs and reports 66/100'] = chk.returncode == 0 and '"done": 66' in chk.stdout
    # 5. tiny lenses A / B, holdout and read on real rows, then analysis
    LA = jlens.fit(model, fit_b_prompts()[3:5], source_layers=lay, target_layer=tl, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None); LA.save(str(root / 'tinyA.pt'))
    LB = jlens.fit(model, fit_b_prompts()[5:7], source_layers=lay, target_layer=tl, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None); LB.save(str(root / 'tinyB.pt'))
    LS = {'fitA': LA, 'fitB': LB}
    holdout(root, model, LS, holdout_prompts(3), layers=lay)
    C = type('T', (), {})(); C.torch = torch; C.s11 = s11; C.model = model; C.env = {'tiny': True}
    papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks)
    cs = ['true', 'false_0', 'false_1', 'delete']; C.prompts = {c: s10.condition_prompts(s11.R10, papers, c)[0] for c in cs}
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); C.smp = smp[smp.shard == 0].head(4)
    for c in cs: read_unit(C, LS, root, c, 0, lay)
    analyze(root, layers=lay, conds=cs, lens_paths=dict(fitA=root / 'tinyA.pt', fitB=root / 'tinyB.pt', public=None), s10_layers=())
    checks['analysis outputs'] = all((root / f'summary/{f}').exists() for f in ('fitb_matrix.csv', 'fitb_holdout.csv', 'fitb_stage10_signal.csv')) and (root / 'reports/b2_fitb_report.md').exists()
    sg = pd.read_csv(root / 'summary/fitb_stage10_signal.csv'); checks['signal rows'] = len(sg) > 0 and sg.spec.notna().any()
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('TINY', 'PASS' if ok else 'FAIL', flush=True); sys.exit(0 if ok else 1)


def selftest():
    import torch
    g = torch.Generator().manual_seed(1); lay = [1, 2]
    S = {l: torch.randn(16, 16, generator=g) * 66 for l in lay}
    A = dict(jacobian_sum={l: v.clone() for l, v in S.items()}, n_done=66, next_idx=66); B = dict(jacobian_sum=S, n_done=66, next_idx=66)
    s1 = compare66(A, B, lay, 66)[0]; A2 = dict(A, jacobian_sum={l: v * 1.01 for l, v in S.items()}); s2 = compare66(A2, B, lay, 66)[0]
    A3 = dict(A, n_done=65); s3 = compare66(A3, B, lay, 66)[0]
    J = {l: torch.randn(16, 16, generator=g) for l in lay}; Ssum = {l: torch.randn(16, 16, generator=g) * 65 + J[l] for l in lay}
    sq = 4.0; norm = max(J[l].double().norm().item() for l in lay) / sq
    dm = max(((J[l].double() - (Ssum[l].double() - J[l].double()) / 65).norm() / (66 * ((Ssum[l].double() - J[l].double()) / 65).norm())).item() for l in lay)
    ref = dict(norm=round(norm, 3), norm_unit=1e-3, d_mean=float(f'{dm:.2e}'), d_mean_unit=10 ** (int(f'{dm:.2e}'.split('e')[1]) - 2))
    s4 = gate_compare(J, Ssum, 66, ref, 16)[0]; s5 = gate_compare(J, Ssum, 66, dict(ref, norm=ref['norm'] * 1.01), 16)[0]
    ok = (s1, s2, s3, s4, s5) == ('PASS', 'FAIL', 'FAIL', 'PASS', 'FAIL')
    print(f'SELFTEST 66-matrix identical -> {s1}; perturbed 1% -> {s2}; wrong count -> {s3}; gate identical (rounded log) -> {s4}; gate log +1% -> {s5}: {"OK" if ok else "BROKEN"}', flush=True)
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['backup', 'gpu', 'hardcheck66', 'analyze', 'tiny', 'selftest'])
    ap.add_argument('--unit'); ap.add_argument('--all', action='store_true'); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    check_frozen(); root = Path(a.root) if a.root else R13 / 'b2_fitb'; root.mkdir(parents=True, exist_ok=True)
    if a.cmd == 'selftest': selftest()
    if a.cmd == 'tiny': assert a.root, '--root required'; tiny(root)
    if a.cmd == 'backup': backup(root); return
    if a.cmd == 'hardcheck66': sys.exit(0 if hardcheck66(root) else 2)
    if a.cmd == 'analyze': analyze(root); return
    if a.cmd == 'gpu':
        if not (a.unit or a.all): raise SystemExit('gpu needs --unit or --all')
        gpu(a, root)


if __name__ == '__main__':
    main()
