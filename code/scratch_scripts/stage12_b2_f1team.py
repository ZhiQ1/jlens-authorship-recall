"""Addendum 12 item 2-2 (batch 2, group C): Stage 12 F1 author-prompt lens SPLIT-HALF BY AUTHOR TEAM, then F2 with each half.

Plan (locked): 381_stage13/config/prereg_addendum12.json (sha256 in PLAN_SHA below), item "2-2 F1 author-lens split-half":
  refit the Stage 12 F1 author lens separately on two halves of its 40 fit papers (20 + 20, split by author team, seed 1206),
  then repeat F2 with each half-lens. Report cosine and top-10 agreement between the half-lenses and with the full F1 lens per
  layer; F2 title-specific signal with each half-lens; whether the F2 null result holds with both.
  HARD CHECK: refitting on all 40 papers with the new wrapper reproduces the stored F1 lens (relative Frobenius diff <= 1e-3).

Implementation (new file; 371_stage12.py / stage12_f1_splithalf.py are imported by path and not edited):
  split    team ids = stage13_cpu.group_folds team ids of the 9,108-paper cohort (archived folds). Unique teams of the 40 fit
           papers are permuted with np.random.default_rng(1206); teams are taken in that order into half A until A holds 20
           papers (a team that would overshoot 20 is skipped to B), the rest is B. Within a half, prompts keep the frozen fit
           order (fit_prompts.parquet row order, the order of the stored F1 fit). -> 371_stage12/config/b2_f1team_split.parquet
  fit      exactly the Stage 12 F1 call (jlens.fit(source_layers=FIT_LAYERS, target_layer=63, dim_batch=1, max_seq_len=128,
           skip_first=16, checkpoint_every=1, resume)), model loaded as Stage 12 (s10.load_model), into 371_stage12/alens_team_{A,B}/.
  hardcheck (deviation D2-2a, written down): the "refit on all 40 with the new wrapper" is evaluated as the fit of all 40 prompts
           by this wrapper accumulated in two parts: J_all = (S_A + S_B) / (n_A + n_B) from the two half checkpoints (jlens.fit
           accumulates a plain running SUM of per-prompt Jacobians, so this is the 40-prompt fit up to fp32 summation order) vs
           the stored 371_stage12/alens/lens.pt, per layer relative Frobenius <= 1e-3. A literal third fit of all 40 prompts
           (`fit --half ALL`, ~3 GPU-h) is implemented and is compared the same way if it exists (alens_team_ALL/lens.pt).
           FAIL -> HARD_CHECK_FAILED file, exit 2, no read unit starts.
  read     F2 readout (371_stage12.do_alens_read logic) with three lenses in one forward: teamA, teamB and the stored full F1
           lens (full = parity vs the stored F2 ranks, WARN only); Stage 11 sample, the 6 F2 title conditions, name positions and the
           last title token, FIT_LAYERS -> raw/alens_team_read/<cond>/shard_k.npz (ranks; for 'true' also top-10 token ids).
  analyze  per layer: cos(vec J_A, vec J_B), A/B vs full, (A-I) vs (B-I), rel. Frobenius; top-10 agreement = mean overlap |top10_x
           & top10_y| / 10 of the readouts at the name (and title) positions of the true-title runs; F2 estimand per lens (true minus
           mean of 5 false, paper means, target / control paper bootstrap and target - control within bin, stage12_analyze.boot/
           strat, F2 exclusions alens_eval_exclude.json), sign / CI agreement of A and B.
Commands: split | fit --half A|B|ALL | hardcheck | read [--cond C --shard K] | gpu --unit fit:A|fit:B|read:<cond>:<k> | gpu --all
          | analyze | tiny --root DIR | selftest
GPU jobs: `gpu --unit ...` = one unit (gate); `gpu --all` = claim units (fit halves first, read units after a PASS hard check),
          skip finished outputs, stop cleanly when the next unit would not fit the Slurm time left.
"""
import argparse, hashlib, importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('s12', H / '12_stage12/371_stage12.py'); s12 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s12)
s11, s10 = s12.s11, s12.s10
_sp = importlib.util.spec_from_file_location('b2c_columns', H / '13_stage13/b2c_columns.py'); COLS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(COLS)
R12 = Path('/scratch/zhang.zhiqi2/jlens/371_stage12'); R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
PLAN = R13 / 'config/prereg_addendum12.json'
PLAN_SHA = (R13 / 'config/prereg_addendum12.json.sha256').read_text().split()[0]
SEED, HALF_N, TOL = 1206, 20, 1e-3
SEC_PER_PROMPT = 300          # stored F1: 269 s / prompt (8 layers, A100-80GB); budget uses 300 s
SEC_PER_READ = 60             # one read unit (cond x shard, 3 lenses); stored F2 single lens ~15 s
log = s11.log


def safe_log(*x):
    try: log(*x)
    except Exception as e: print('log warning', repr(e), flush=True)


def check_plan():
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED (addendum 12 sha256 mismatch)')


# ------------------------------------------------------------------ split
def make_split(root):
    import pandas as pd
    f = root / 'config/b2_f1team_split.parquet'
    fp = pd.read_parquet(R12 / 'config/fit_prompts.parquet').reset_index(drop=True)
    c13 = load_mod(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(s11.R10 / 'cohort/papers.parquet', columns=['paper_id'])
    _, teams = c13.group_folds(papers.paper_id.to_numpy()); T = dict(zip(papers.paper_id, teams))
    fp['team'] = [int(T[p]) for p in fp.paper_id]; fp['fit_row'] = np.arange(len(fp))
    uniq = np.array(sorted(fp.team.unique())); order = np.random.default_rng(SEED).permutation(len(uniq))
    size = fp.team.value_counts().to_dict(); A, nA = set(), 0
    for t in uniq[order]:
        if nA + size[t] <= HALF_N: A.add(t); nA += size[t]
        if nA == HALF_N: break
    fp['half'] = np.where(fp.team.isin(A), 'A', 'B')
    out = COLS.check(fp[['paper_id', 'team', 'half', 'fit_row', 'group_tight']].copy(), 'F1H_SPLIT')
    nA, nB = int((out.half == 'A').sum()), int((out.half == 'B').sum())
    if nA != HALF_N or nB != len(fp) - HALF_N: safe_log(f'WARN split sizes A={nA} B={nB} (wanted 20 + 20; team sizes {sorted(size.values())})')
    if f.exists():
        old = pd.read_parquet(f)
        if not old.equals(out): raise SystemExit(f'existing split {f} differs from the recomputed split: stop')
    else:
        f.parent.mkdir(parents=True, exist_ok=True); out.to_parquet(f, index=False)
    return out, fp


def half_prompts(root, h):
    import pandas as pd
    sp = pd.read_parquet(root / 'config/b2_f1team_split.parquet') if (root / 'config/b2_f1team_split.parquet').exists() else make_split(root)[0]
    fp = pd.read_parquet(R12 / 'config/fit_prompts.parquet').reset_index(drop=True)
    rows = sp.fit_row.to_numpy() if h == 'ALL' else sp[sp.half == h].sort_values('fit_row').fit_row.to_numpy()
    return fp.text.iloc[rows].tolist(), fp.iloc[rows]


def load_mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# ------------------------------------------------------------------ fit
def fit_half(C, h, root, budget_min, layers=None, n_total=None, sec_per_prompt=SEC_PER_PROMPT):
    import jlens
    prompts, fp = half_prompts(root, h); n_total = n_total or len(prompts); prompts = prompts[:n_total]; layers = layers or s12.FIT_LAYERS
    d = root / f'alens_team_{h}'; d.mkdir(parents=True, exist_ok=True); cp = d / 'checkpoint.pt'
    if (d / 'lens.pt').exists(): safe_log(f'team half {h}: lens exists'); return True
    (d / 'half.json').write_text(json.dumps(dict(half=h, seed=SEED, fit_rows=fp.index.tolist(), paper_ids=fp.paper_id.tolist(),
                                                 groups=fp.group_tight.value_counts().to_dict()), indent=1))
    prog = json.loads((d / 'progress.json').read_text())['done'] if (d / 'progress.json').exists() else 0
    n = int((budget_min * 60 - 120) // sec_per_prompt)
    if n < 1: safe_log(f'half {h}: no time for one prompt ({budget_min:.1f} min left)'); return False
    target = min(n_total, prog + n)
    safe_log(f'F1 team half {h}: {prog} -> {target} of {n_total} (budget {budget_min:.0f} min)'); t0 = time.monotonic()
    lens = jlens.fit(C.model, prompts[:target], source_layers=layers, target_layer=len(C.model.layers) - 1, dim_batch=1, max_seq_len=128, skip_first=16,
                     checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
    (d / 'progress.json').write_text(json.dumps(dict(done=lens.n_prompts, updated=s11.now(), seconds=round(time.monotonic() - t0),
                                                     per_prompt=round((time.monotonic() - t0) / max(1, lens.n_prompts - prog)))))
    if lens.n_prompts >= n_total:
        tmp = d / 'lens.tmp.pt'; lens.save(str(tmp)); os.replace(tmp, d / 'lens.pt'); safe_log(f'team half {h} lens COMPLETE ({lens.n_prompts} prompts)')
        return True
    return False


# ------------------------------------------------------------------ hard check
def combined_vs_stored(ckA, ckB, stored, layers, tol=TOL):
    """ckA/ckB: dicts with jacobian_sum {layer: T}, n_done; stored: {layer: T} (the stored lens means). Returns (status, rows)."""
    rows, ok = [], True
    n = ckA['n_done'] + ckB['n_done']
    for l in layers:
        J = (ckA['jacobian_sum'][l].double() + ckB['jacobian_sum'][l].double()) / n; S = stored[l].double()
        rel = float((J - S).norm() / S.norm()); mx = float((J - S).abs().max())
        st = 'PASS' if rel <= tol else 'FAIL'; ok &= st == 'PASS'
        rows.append(dict(layer=l, relfro_combined_vs_stored=rel, maxabs=mx, threshold=tol, status=st))
    if n != 40 and len(layers) == len(s12.FIT_LAYERS): ok = False; rows.append(dict(layer=-1, relfro_combined_vs_stored=float('nan'), maxabs=float(n), threshold=40, status='FAIL'))
    return ('PASS' if ok else 'FAIL'), rows


def hardcheck(root, stored_path=None, layers=None, n_expected=40):
    import torch, pandas as pd, jlens
    layers = layers or s12.FIT_LAYERS
    ck = {h: torch.load(root / f'alens_team_{h}/checkpoint.pt', map_location='cpu', weights_only=True) for h in 'AB'}
    for h in 'AB':
        if ck[h]['n_done'] != ck[h]['next_idx']: safe_log(f'WARN half {h}: n_done {ck[h]["n_done"]} != next_idx {ck[h]["next_idx"]} (a prompt was skipped)')
    S = jlens.JacobianLens.load(str(stored_path or (R12 / 'alens/lens.pt')))
    st, rows = combined_vs_stored(ck['A'], ck['B'], S.jacobians, layers)
    if ck['A']['n_done'] + ck['B']['n_done'] != n_expected: st = 'FAIL'
    lit = root / 'alens_team_ALL/lens.pt'
    if lit.exists():                                          # literal 40-prompt refit, if it was run
        L = jlens.JacobianLens.load(str(lit))
        for l in layers:
            rel = float((L.jacobians[l].double() - S.jacobians[l].double()).norm() / S.jacobians[l].double().norm())
            r = dict(layer=l, relfro_combined_vs_stored=rel, maxabs=float((L.jacobians[l] - S.jacobians[l]).abs().max()), threshold=TOL, status='PASS' if rel <= TOL else 'FAIL')
            rows.append(r | {'layer': 1000 + l}); st = st if r['status'] == 'PASS' else 'FAIL'
    df = COLS.check(pd.DataFrame(rows, columns=COLS.F1H_HARDCHECK), 'F1H_HARDCHECK')
    (root / 'summary').mkdir(parents=True, exist_ok=True); df.to_csv(root / 'summary/b2_f1team_hardcheck.csv', index=False)
    (root / 'summary/b2_f1team_hardcheck.json').write_text(json.dumps(dict(status=st, rule='(S_A+S_B)/40 vs stored F1 lens, rel. Frobenius <= 1e-3 per layer'
                                                                       ' (layer 1000+l = literal ALL refit, if present)', rows=rows), indent=1, default=float))
    print('HARD CHECK', st, 'max rel', float(df.relfro_combined_vs_stored.max()), flush=True)
    if st != 'PASS':
        (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').write_text(json.dumps(dict(rows=rows), default=float)); return False
    return True


def hardcheck_passed(root):
    f = root / 'summary/b2_f1team_hardcheck.json'
    return f.exists() and json.loads(f.read_text())['status'] == 'PASS' and not (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').exists()


# ------------------------------------------------------------------ read
def load_lens(C, path):
    import jlens
    L = jlens.JacobianLens.load(str(path))
    for k in list(L.jacobians): L.jacobians[k] = L.jacobians[k].to(s10.layer_device(C.model, k))
    return L


def do_read(C, LS, cond, shard, layers, top10):
    """371_stage12.do_alens_read with several lenses in one forward; top-10 ids (for agreement) when top10=True."""
    torch = C.torch; prompts = C.prompts[cond]
    keys = [f'{n}@{l}@{p}' for n in LS for l in layers for p in ('name', 'title')]
    out = {k: [] for k in keys}; tops = {k: [] for k in keys} if top10 else {}; rows = []
    from jlens.hooks import ActivationRecorder
    for r in C.smp[C.smp.shard == shard].itertuples():
        ptx, pids = prompts[r.paper_id]; it = s11.title_positions(C.tok, ptx, pids)[-1]
        for ai, rids, name in C.ctx[r.paper_id]:
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]; g = torch.tensor(name, device=C.model.input_device)
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=layers) as rec:
                C.model.forward(torch.tensor([ids], device=C.model.input_device))
                for n, L in LS.items():
                    for l in layers:
                        h = rec.activations[l][0]
                        lg = C.model.unembed(L.transport(h[pos].float(), l)).float(); out[f'{n}@{l}@name'].append(s11.ranks(lg, g, torch))
                        lt = C.model.unembed(L.transport(h[it:it + 1].float(), l)).float().expand(len(name), -1); out[f'{n}@{l}@title'].append(s11.ranks(lt, g, torch))
                        if top10:
                            tops[f'{n}@{l}@name'].append(lg.topk(10, dim=-1).indices.int().cpu().numpy())
                            tops[f'{n}@{l}@title'].append(lt.topk(10, dim=-1).indices.int().cpu().numpy())
            rows += rids
    d = dict(row_id=np.array(rows), **{k: np.concatenate(v) for k, v in out.items()})
    if top10: d |= {'top10|' + k: np.concatenate(v) for k, v in tops.items()}
    return d


def read_path(root, cond, shard): return root / f'raw/alens_team_read/{cond}/shard_{shard:03d}.npz'


def read_unit(C, LS, root, cond, shard, layers):
    f = read_path(root, cond, shard)
    if f.exists(): return 0.0
    t1 = time.monotonic(); d = do_read(C, LS, cond, shard, layers, top10=(cond == 'true')); f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(created=s11.now(), cond=cond, shard=shard, **getattr(C, 'env', {})))), **d); os.replace(tmp, f)
    dt = time.monotonic() - t1; safe_log(f'alens_team_read {cond} shard {shard:03d} rows={len(d["row_id"])} {dt:.0f}s'); return dt


def lenses(C, root):
    return {'teamA': load_lens(C, root / 'alens_team_A/lens.pt'), 'teamB': load_lens(C, root / 'alens_team_B/lens.pt'), 'full': load_lens(C, R12 / 'alens/lens.pt')}


# ------------------------------------------------------------------ GPU job driver
class GCtx:
    def __init__(self):
        import torch, pandas as pd
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(s11.R10, self.papers, c)[0] for c in s12.TC}
        self.smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], job=os.environ.get('SLURM_JOB_ID'))


def minutes_left(t0, default):
    left = s11.slurm_minutes_left(); el = (time.monotonic() - t0) / 60
    return (default - el) if left is None else min(default - el, left - 4)


def gpu(a, root):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); CL = root / 'logs/claims_b2_f1team'; CL.mkdir(parents=True, exist_ok=True)
    if (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').exists(): raise SystemExit('hard check failed earlier: stop')
    make_split(root); C = None
    units = [a.unit] if a.unit else None
    def ctx():
        nonlocal C
        if C is None: C = GCtx()
        return C
    # fit units
    fit_units = [u for u in (units or ['fit:A', 'fit:B']) if u.startswith('fit:')]
    for u in fit_units:
        h = u.split(':')[1]
        if (root / f'alens_team_{h}/lens.pt').exists(): continue
        if not units and not s11.claim(CL / f'fit_{h}', me): continue
        while not (root / f'alens_team_{h}/lens.pt').exists():
            ctx(); b = minutes_left(t0, a.minutes)             # model loaded first, then the budget is measured
            if b * 60 < SEC_PER_PROMPT + 120: safe_log('budget: stop before next prompt'); return
            done = fit_half(C, h, root, b)
            if units: break                          # gate: one fit chunk only
            if not done and minutes_left(t0, a.minutes) * 60 < SEC_PER_PROMPT + 120: return
    # hard check once both halves exist
    if all((root / f'alens_team_{h}/lens.pt').exists() for h in 'AB') and not hardcheck_passed(root):
        if not hardcheck(root): sys.exit(2)
    rd = [u for u in (units or []) if u.startswith('read:')]
    if units and not rd: return
    if not hardcheck_passed(root): safe_log('read units wait for the PASS hard check (both halves fitted)'); return
    LS = lenses(ctx(), root); todo = [(c, k) for c in s12.TC for k in range(24)] if not rd else [(u.split(':')[1], int(u.split(':')[2])) for u in rd]
    last = SEC_PER_READ
    for c, k in todo:
        if read_path(root, c, k).exists(): continue
        if minutes_left(t0, a.minutes) * 60 < 1.5 * last + 30: safe_log('budget: stop before next read unit'); return
        if not units and not s11.claim(CL / f'read_{c}_{k:03d}', me): continue
        last = max(read_unit(C, LS, root, c, k, s12.FIT_LAYERS), 1.0)
    safe_log('gpu: no unit left for this job')


# ------------------------------------------------------------------ analysis (CPU)
def topk_overlap(a, b): return float(np.mean([len(set(x) & set(y)) / 10 for x, y in zip(a, b)])) if len(a) else float('nan')


def analyze(root, conds_needed=None, layers=None):
    import torch, pandas as pd, jlens
    a12 = load_mod(H / '12_stage12/stage12_analyze.py', 's12a')
    W = []
    def warn(m):
        W.append(m)
        try: print('WARN', m, flush=True)
        except Exception: pass
    layers = layers or s12.FIT_LAYERS
    LA = jlens.JacobianLens.load(str(root / 'alens_team_A/lens.pt')); LB = jlens.JacobianLens.load(str(root / 'alens_team_B/lens.pt'))
    LF = jlens.JacobianLens.load(str(root / 'alens_full_tiny.pt' if (root / 'alens_full_tiny.pt').exists() else R12 / 'alens/lens.pt'))
    cos = lambda x, y: float((x.flatten().double() @ y.flatten().double()) / (x.flatten().double().norm() * y.flatten().double().norm()))
    rel = lambda x, y: float((x - y).double().norm() / y.double().norm())
    eye = torch.eye(LA.jacobians[layers[0]].shape[0])
    conds = [c for c in s12.TC if (root / f'raw/alens_team_read/{c}').exists()]
    zt = [np.load(f) for f in sorted((root / 'raw/alens_team_read/true').glob('shard_*.npz'))]
    top = {k: np.concatenate([z[k] for z in zt]) for k in zt[0].files if k.startswith('top10|')} if zt else {}
    mrows = []
    for l in layers:
        A, Bm, F = LA.jacobians[l].float(), LB.jacobians[l].float(), LF.jacobians[l].float()
        r = dict(layer=l, cos_A_B=cos(A, Bm), cos_A_full=cos(A, F), cos_B_full=cos(Bm, F), cos_A_B_minus_I=cos(A - eye, Bm - eye), relfro_A_B=rel(A, Bm))
        g = lambda x, y: topk_overlap(top[f'top10|{x}@{l}@name'], top[f'top10|{y}@{l}@name']) if top else float('nan')
        r |= dict(top10_A_B=g('teamA', 'teamB'), top10_A_full=g('teamA', 'full'), top10_B_full=g('teamB', 'full'))
        mrows.append(r)
    M = COLS.check(pd.DataFrame(mrows)[COLS.F1H_MATRIX], 'F1H_MATRIX'); S = root / 'summary'; S.mkdir(exist_ok=True); M.to_csv(S / 'b2_f1team_matrix.csv', index=False)
    toks = pd.read_parquet(s11.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet')
    nlr = lambda x: -np.log10(np.asarray(x, float))
    per = {}; par = []
    for c in conds:
        zs = [np.load(f) for f in sorted((root / f'raw/alens_team_read/{c}').glob('shard_*.npz'))]
        hz = {k: np.concatenate([z[k] for z in zs]) for k in zs[0].files if k != 'meta' and not k.startswith('top10|')}
        # parity: our 'full' ranks vs the stored F2 ranks (same lens, same code path), WARN only
        try:
            fz = [np.load(R12 / f'raw/alens_read/{c}' / f.name) for f in sorted((root / f'raw/alens_team_read/{c}').glob('shard_*.npz')) if (R12 / f'raw/alens_read/{c}' / f.name).exists()]
            if fz:
                fz = {k: np.concatenate([z[k] for z in fz]) for k in fz[0].files if k != 'meta'}
                if np.array_equal(fz['row_id'], hz['row_id']):
                    for l in layers:
                        for p in ('name', 'title'):
                            x, y = hz[f'full@{l}@{p}'], fz[f'alens@{l}@{p}']; eq = float((x == y).mean()); md = float(np.abs(nlr(x) - nlr(y)).max())
                            par.append(dict(cond=c, layer=l, position=p, share_equal=eq, max_abs_log10rank=md))
                            if eq < 0.95: warn(f'{c} L{l} {p}: full-lens ranks equal to stored F2 for {eq:.3f} of rows (threshold 0.95), max |dlog10 rank| {md:.2f}')
                else: warn(f'{c}: row ids differ from stored F2 (parity skipped)')
        except Exception as e: warn(f'parity vs stored F2 not run for {c}: {e!r}')
        df = pd.DataFrame({'row_id': hz['row_id'], **{k: nlr(v) for k, v in hz.items() if '@' in k}})
        per[c] = df.merge(toks, on='row_id').drop(columns='row_id').groupby('paper_id').mean()
    if par: pd.DataFrame(par).to_csv(S / 'b2_f1team_parity_vs_F2.csv', index=False)
    if 'true' not in per or len(per) < 2: warn('readout incomplete: F2 part skipped'); F = pd.DataFrame(columns=COLS.F1H_READOUT)
    else:
        if conds_needed and set(conds) != set(conds_needed): warn(f'conditions present {conds} != expected {conds_needed}')
        common = per['true'].index
        for c in per: common = common.intersection(per[c].index)
        ex = R12 / 'config/alens_eval_exclude.json'
        if ex.exists(): drop = set(json.loads(ex.read_text())['paper_ids']); common = common[~common.isin(drop)]
        spec = per['true'].loc[common] - sum(per[c].loc[common] for c in per if c != 'true') / (len(per) - 1)
        spj = spec.join(smp.set_index('paper_id'))
        rows = []
        for l in layers:
            for pos in ('name', 'title'):
                for n in ('teamA', 'teamB', 'full'):
                    col = f'{n}@{l}@{pos}'; r = dict(position=pos, layer=l, lens=n, n_papers=len(spj))
                    for g in ('target', 'control'):
                        v = spj[spj.group == g][col]
                        m = a12.boot(v) if len(v.dropna()) else (np.nan,) * 3
                        r |= {g: m[0], f'{g}_lo': m[1], f'{g}_hi': m[2]}
                    e = a12.strat(spj, col); r |= {'tc': e[0], 'tc_lo': e[1], 'tc_hi': e[2]}
                    rows.append(r)
        F = COLS.check(pd.DataFrame(rows)[COLS.F1H_READOUT], 'F1H_READOUT')
    F.to_csv(S / 'b2_f1team_readout.csv', index=False)
    # report
    try:
        sp = pd.read_parquet(root / 'config/b2_f1team_split.parquet'); hc = json.loads((root / 'summary/b2_f1team_hardcheck.json').read_text()) if (root / 'summary/b2_f1team_hardcheck.json').exists() else {'status': 'not run'}
        fm = lambda e, lo, hi: '-' if pd.isna(e) else f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if lo > 0 or hi < 0 else '')
        L = ['# Addendum 12 item 2-2: Stage 12 F1 author-lens split-half by author team', '',
             'Plan `381_stage13/config/prereg_addendum12.json` item 2-2. Script `12_stage12/stage12_b2_f1team.py` (imports `371_stage12.py` by path; fit = the Stage 12 F1 call). '
             f'Halves: 40 frozen fit prompts split by author team (archived team ids), seed {SEED}: A {int((sp.half == "A").sum())} papers ({sp[sp.half == "A"].group_tight.value_counts().to_dict()}), '
             f'B {int((sp.half == "B").sum())} ({sp[sp.half == "B"].group_tight.value_counts().to_dict()}); teams {sp.team.nunique()}. Fitted prompts A {LA.n_prompts}, B {LB.n_prompts}, full F1 {LF.n_prompts}.', '',
             f'## Hard check: {hc["status"]}', '', '(S_A + S_B) / 40 from the two half checkpoints vs the stored F1 lens, relative Frobenius per layer (threshold 1e-3; deviation D2-2a: '
             'the 40-prompt refit is accumulated in two parts by the same wrapper; a literal third fit is optional).', '']
        for r in hc.get('rows', []): L.append(f'- L{r["layer"]}: rel {r["relfro_combined_vs_stored"]:.2e}, max |diff| {r["maxabs"]:.2e} -> {r["status"]}')
        L += ['', '## Checks (WARN = value and threshold; the run continued)', '', *(['- ' + w for w in W] or ['- No WARN.']), '',
              '## Matrix and readout agreement per layer', '', 'cos = cosine of the flattened 5120 x 5120 matrices; top-10 = mean overlap of the top-10 tokens read at the name positions of the true-title runs.', '',
              '| layer | cos A,B | cos A,full | cos B,full | cos (A-I),(B-I) | rel. Frob. A-B | top-10 A,B | top-10 A,full | top-10 B,full |', '|---|---|---|---|---|---|---|---|---|']
        for _, r in M.iterrows():
            L.append(f'| L{int(r.layer)} | {r.cos_A_B:.3f} | {r.cos_A_full:.3f} | {r.cos_B_full:.3f} | {r.cos_A_B_minus_I:.3f} | {r.relfro_A_B:.3f} | {r.top10_A_B:.3f} | {r.top10_A_full:.3f} | {r.top10_B_full:.3f} |')
        L += ['', '## F2 with each lens: title-specific signal (true - mean of 5 false titles), paper means', '',
              'target / control: paper bootstrap; t-c: target - control within citation bin (stage12_analyze.boot / strat, as published F2). * = CI excludes 0.', '',
              '| pos | layer | lens | target | control | target - control |', '|---|---|---|---|---|---|']
        for _, r in F.sort_values(['position', 'layer']).iterrows():
            L.append(f'| {r.position} | L{int(r.layer)} | {r.lens} | {fm(r.target, r.target_lo, r.target_hi)} | {fm(r.control, r.control_lo, r.control_hi)} | {fm(r.tc, r.tc_lo, r.tc_hi)} |')
        if len(F):
            g = F.pivot_table(index=['position', 'layer'], columns='lens', values=['tc', 'tc_lo', 'tc_hi'])
            call = lambda lo, hi: 'pos' if lo > 0 else ('neg' if hi < 0 else 'n.s.')
            agree = [(i, call(g.loc[i, ('tc_lo', 'teamA')], g.loc[i, ('tc_hi', 'teamA')]), call(g.loc[i, ('tc_lo', 'teamB')], g.loc[i, ('tc_hi', 'teamB')]),
                      call(g.loc[i, ('tc_lo', 'full')], g.loc[i, ('tc_hi', 'full')])) for i in g.index]
            L += ['', 'Target - control CI call per position x layer (A / B / full): ' + '; '.join(f'{p} L{l}: {a_}/{b_}/{f_}' for (p, l), a_, b_, f_ in agree), '',
                  f'Same call in A and B: {sum(a_ == b_ for _, a_, b_, _ in agree)}/{len(agree)}; middle layers (L24-L56) where both halves are n.s. or negative at the name position: '
                  f'{sum(1 for (p, l), a_, b_, _ in agree if p == "name" and l <= 56 and a_ != "pos" and b_ != "pos")}/{sum(1 for (p, l), *_ in agree if p == "name" and l <= 56)}.']
        L += ['', '## Conclusion', '', '<!--CONCLUSION: written by the main session after review-->', '']
        (root / 'reports').mkdir(parents=True, exist_ok=True)
        rep = (R13 / 'reports/b2_f1team_report.md') if root == R12 else (root / 'reports/b2_f1team_report.md')
        rep.write_text('\n'.join(L) + '\n'); print('wrote', rep, flush=True)
    except Exception:
        print('WARN report writing failed', flush=True); traceback.print_exc()


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU, tiny random model, real data rows)
def tiny(root):
    import torch, transformers, jlens, pandas as pd
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {c: s10.condition_prompts(s11.R10, C.papers, c)[0] for c in ('true', 'false_0')}
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); C.smp = smp[smp.shard.isin([0])].head(3); C.env = {'tiny': True}
    s10.layer_device = lambda model, k: 'cpu'
    lay = [0, 1]; checks = {}
    sp, _ = make_split(root); checks['split 20+20 by team'] = int((sp.half == 'A').sum()) == 20 and not set(sp[sp.half == 'A'].team) & set(sp[sp.half == 'B'].team)
    for h in 'AB':
        fit_half(C, h, root, budget_min=2 + 1.2 * 1 * 30 / 60, layers=lay, n_total=2, sec_per_prompt=30)   # 1 prompt (budget) ...
        fit_half(C, h, root, budget_min=60, layers=lay, n_total=2, sec_per_prompt=30)                      # ... resumed to 2
    LA = jlens.JacobianLens.load(str(root / 'alens_team_A/lens.pt')); LB = jlens.JacobianLens.load(str(root / 'alens_team_B/lens.pt'))
    checks['halves fitted 2+2'] = LA.n_prompts == 2 and LB.n_prompts == 2
    ref = jlens.fit(C.model, half_prompts(root, 'A')[0][:2], source_layers=lay, target_layer=2, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None)
    ref2 = jlens.fit(C.model, half_prompts(root, 'A')[0][:2], source_layers=lay, target_layer=2, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None)
    rr = max(float((ref.jacobians[l] - LA.jacobians[l]).norm() / ref.jacobians[l].norm()) for l in lay)
    rr0 = max(float((ref.jacobians[l] - ref2.jacobians[l]).norm() / ref.jacobians[l].norm()) for l in lay)
    print(f'resume vs fresh: rel. Frobenius {rr:.2e}; fresh vs fresh (CPU fp32 noise floor) {rr0:.2e}', flush=True)
    checks['resume == fresh fit (rel. Frobenius <= 1e-3, the hard-check rule)'] = rr <= 1e-3
    # "stored full lens" for the tiny = a fresh fit on the 4 prompts in fit order -> hard check must PASS; a perturbed copy must FAIL
    p4 = half_prompts(root, 'A')[0][:2] + half_prompts(root, 'B')[0][:2]
    full = jlens.fit(C.model, p4, source_layers=lay, target_layer=2, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None)
    full.save(str(root / 'alens_full_tiny.pt'))
    checks['hard check identical -> PASS'] = hardcheck(root, stored_path=root / 'alens_full_tiny.pt', layers=lay, n_expected=4)
    bad = jlens.JacobianLens(jacobians={l: full.jacobians[l] * 1.01 for l in lay}, n_prompts=4, d_model=full.d_model); bad.save(str(root / 'alens_full_tiny_bad.pt'))
    hc_bad = hardcheck(root, stored_path=root / 'alens_full_tiny_bad.pt', layers=lay, n_expected=4)
    checks['hard check perturbed 1% -> FAIL'] = not hc_bad
    (root / 'summary/B2_F1TEAM_HARD_CHECK_FAILED').unlink(missing_ok=True); hardcheck(root, stored_path=root / 'alens_full_tiny.pt', layers=lay, n_expected=4)
    LS = {'teamA': load_lens(C, root / 'alens_team_A/lens.pt'), 'teamB': load_lens(C, root / 'alens_team_B/lens.pt'), 'full': load_lens(C, root / 'alens_full_tiny.pt')}
    for c in ('true', 'false_0'): read_unit(C, LS, root, c, 0, lay)
    z = np.load(read_path(root, 'true', 0)); checks['read keys + top10'] = 'teamB@1@title' in z.files and 'top10|full@1@name' in z.files and len(z['row_id']) > 0
    analyze(root, layers=lay)
    checks['analysis files'] = all((root / f'summary/{f}').exists() for f in ('b2_f1team_matrix.csv', 'b2_f1team_readout.csv')) and (root / 'reports/b2_f1team_report.md').exists()
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('TINY', 'PASS' if ok else 'FAIL', flush=True); sys.exit(0 if ok else 1)


def selftest():
    """hard-check comparator: identical -> PASS, 1e-2 relative perturbation -> FAIL (synthetic matrices, no data)."""
    import torch
    g = torch.Generator().manual_seed(0); lay = [1, 2]
    SA = {l: torch.randn(8, 8, generator=g) for l in lay}; SB = {l: torch.randn(8, 8, generator=g) for l in lay}
    stored = {l: (SA[l] + SB[l]) / 40 for l in lay}
    s1, _ = combined_vs_stored(dict(jacobian_sum=SA, n_done=20), dict(jacobian_sum=SB, n_done=20), stored, lay)
    s2, _ = combined_vs_stored(dict(jacobian_sum=SA, n_done=20), dict(jacobian_sum=SB, n_done=20), {l: stored[l] * 1.01 for l in lay}, lay)
    s3, _ = combined_vs_stored(dict(jacobian_sum=SA, n_done=20), dict(jacobian_sum=SB, n_done=20), {l: stored[l] * (1 + 5e-4) for l in lay}, lay)
    ok = (s1, s2, s3) == ('PASS', 'FAIL', 'PASS')
    print(f'SELFTEST identical -> {s1}; perturbed 1e-2 -> {s2}; perturbed 5e-4 (inside 1e-3) -> {s3}: {"OK" if ok else "BROKEN"}', flush=True); sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['split', 'fit', 'hardcheck', 'read', 'gpu', 'analyze', 'tiny', 'selftest'])
    ap.add_argument('--half', choices=['A', 'B', 'ALL']); ap.add_argument('--unit'); ap.add_argument('--all', action='store_true')
    ap.add_argument('--cond'); ap.add_argument('--shard', type=int); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    check_plan(); root = Path(a.root) if a.root else R12
    if a.cmd == 'selftest': selftest()
    if a.cmd == 'tiny': assert a.root, '--root required'; root.mkdir(parents=True, exist_ok=True); tiny(root); return
    if a.cmd == 'split': sp, _ = make_split(root); print(sp.to_string()); return
    if a.cmd == 'hardcheck': sys.exit(0 if hardcheck(root) else 2)
    if a.cmd == 'analyze': analyze(root, conds_needed=s12.TC); return
    if a.cmd == 'gpu':
        if not (a.unit or a.all): raise SystemExit('gpu needs --unit or --all')
        gpu(a, root); return
    t0 = time.monotonic(); C = GCtx()
    if a.cmd == 'fit': make_split(root); fit_half(C, a.half, root, minutes_left(t0, a.minutes)); return
    if a.cmd == 'read':
        if not hardcheck_passed(root): raise SystemExit('hard check not passed')
        read_unit(C, lenses(C, root), root, a.cond, a.shard, s12.FIT_LAYERS)


if __name__ == '__main__':
    main()
