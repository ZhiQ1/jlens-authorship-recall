"""Batch 2, addendum 12 items 2-7 (patchscope with the source at ':' and at every name-predicting position) and 2-9 (x4tok:
first author decoded per token role at all X4 layers and at the ':' source). GPU, one unit = one Stage 11 sample shard (24).

Plan (locked): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum12.json (sha256 checked below), items 2-7 and 2-9.
Everything is the published X4 (381_stage13.do_pscope, imported by path, not edited) except the SOURCE position:
  target prompts  s13.PS_TARGETS ('Paper: X\\nThe paper was published in the year' / '...first author of the paper is' /
                  '...Research field:'), answers s13.ps_answers (year, first author's Stage 10 name tokens, field)
  patch           block-output replacement at the X placeholder, the 7 PS_LAYERS (8..56) patched in ONE forward of batch 7
                  (batch element i = layer PS_LAYERS[i]), exactly as do_pscope (the x4tok audit showed the batch matters)
  sources         the X4 authors prompt (s13 TASKS['authors'], no year anywhere) of paper A ('self') or partner B ('partner'):
     title  last title token                                  (published X4; hard-check source)
     colon  ':' = the position predicting every author's first name token   (published X4 'colon'; 2-7 / 2-9 ':' source)
     name   for every author a of paper A and j >= 1: the position predicting name token j of author a (addendum-11 position
            set), i.e. the authors prompt + A's author a tokens [0..j-1] teacher-forced. For the partner source the SAME
            author tokens of A are appended to B's title, so self - partner differs only in the title (the name tokens seen by
            the source, which include the gold first author's tokens when a = 0, cancel in D).
  scores          every answer token: log10(1/rank) at the model output (full vocabulary), as x4tok (per token) -> the
                  published per-paper score is the mean over tokens (do_pscope / score_tf).
Output per shard: raw/b2_pscope/shard_XXX.parquet (token rows, stage13_b2A_cols.PS_TOKEN_COLS) and none_XXX.parquet (unpatched).
Per-shard check (summary_b2_ps/checks/shard_XXX.json, WARN only here; the hard checks are in stage13_b2_ps_analyze.py):
  title / colon per-paper means vs the published raw/pscope shard; author title per-token vs followup/x4tok2 (b7) at L8 / L40.
Usage:  stage13_b2_ps_gpu.py --shards 0 [--max-minutes 40]   (single-shard gate)
        stage13_b2_ps_gpu.py --all [--max-minutes 40]         (claim mode, skip-if-exists)
        stage13_b2_ps_gpu.py --tiny                            (CPU, 2-layer random Qwen3 with the real tokenizer, 3 papers;
                                                               compares title / colon with the frozen do_pscope and x4tok code)
"""
import importlib.util, json, os, sys, time, traceback, subprocess, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT0 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); R10 = Path('/scratch/zhang.zhiqi2/jlens/351_stage10')
PLAN = ROOT0 / 'config/prereg_addendum12.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
T0 = time.monotonic()
def log(*x):
    try: print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
    except Exception: pass
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols')
x2 = load(H / '13_stage13/stage13_x2.py', 'x2'); s13 = x2.s13; s10, s11 = s13.s10, s13.s11
R = {}


def set_root(tiny, tag=''):
    r = ROOT0 / 'b2_ps_tiny' if tiny else ROOT0
    R.update(root=r, raw=r / (f'raw/b2_pscope_{tag}' if tiny else 'raw/b2_pscope'), chk=r / 'summary_b2_ps/checks', claims=r / 'logs/claims_b2_ps', logs=r / 'logs')


_ROLES = {}
def first_author_roles(pid, n):
    if 'r' not in _ROLES:
        nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index', 'role'])
        _ROLES['r'] = nt[nt.author_index == 0].sort_values('token_index').groupby('paper_id').role.apply(list).to_dict()
        _ROLES['all'] = nt.sort_values('token_index').groupby(['paper_id', 'author_index']).role.apply(list).to_dict()
    rl = _ROLES['r'].get(pid, []); return rl if len(rl) == n else ['?'] * n


def targets(C):
    tgt = {}
    for k, t in s13.PS_TARGETS.items():
        e = C.tok(t, return_offsets_mapping=True); ids = list(e.input_ids); x = t.index('X')
        tgt[k] = (ids, [i for i, (a, b) in enumerate(e.offset_mapping) if a <= x < b][0])
    return tgt


def tok_scores(C, ids, xi, ans, state, PL):
    """per-token log10(1/rank) of ans after ids with state[l] injected at xi, all PL layers in one forward of batch len(PL)
    (= x4tok / do_pscope score_tf, per token). state=None -> unpatched (batch 1)."""
    torch = C.torch
    full = list(ids) + list(ans[:-1]); pos = [len(ids) - 1 + j for j in range(len(ans))]
    patch = None if state is None else {l: [(i, ('at', xi), state[l])] for i, l in enumerate(PL)}
    lg = s13.run_final(C, full, pos, patch=patch, batch=1 if state is None else len(PL)); g = torch.tensor(ans, device=lg.device)
    out = []
    for b in range(lg.shape[0]):
        rk = (lg[b] > lg[b].gather(1, g[:, None])).sum(1) + 1; out.append((-torch.log10(rk.double())).cpu().numpy())
    return out


def do_shard(C, shard):
    smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); PL = list(s13.PS_LAYERS); tgt = targets(C)
    rows, none = [], []
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        A = r.paper_id; q = pairs.loc[A].partner; ans = s13.ps_answers(C, A, P)
        arole = {'author': first_author_roles(A, len(ans['author'])), 'year': ['na'] * len(ans['year']), 'field': ['na'] * len(ans['field'])}
        for k, (ids, xi) in tgt.items():
            v = tok_scores(C, ids, xi, ans[k], None, PL)[0]
            none += [(A, k, j, arole[k][j], float(x)) for j, x in enumerate(v)]
        authors = C.ctx[A]
        for who, src in (('self', A), ('partner', q)):
            title = P.loc[src].title
            ids0, it, ic = s13.build(C.tok, title, 'authors', []); acts = C.record(ids0, PL)        # = do_pscope source run
            sources = [('title', -1, -1, 'na', {l: acts[l][it] for l in PL}), ('colon', -1, 0, 'na', {l: acts[l][ic] for l in PL})]
            for ai, _, name in authors:
                if len(name) < 2: continue
                full, it2, ic2 = s13.build(C.tok, title, 'authors', name[:-1])
                if ic2 != ic: raise RuntimeError(f'colon index differs with answer appended: {A} {who}')
                actn = C.record(full, PL); rl = _ROLES['all'].get((A, ai), ['?'] * len(name))
                for j in range(1, len(name)):
                    sources.append(('name', ai, j, rl[j] if len(rl) == len(name) else '?', {l: actn[l][ic + j] for l in PL}))
            for kind, ai, j, role, st in sources:
                for k, (ids, xi) in tgt.items():
                    V = tok_scores(C, ids, xi, ans[k], st, PL)
                    for b, l in enumerate(PL):
                        for aj, x in enumerate(V[b]): rows.append((A, q, kind, ai, j, role, who, k, l, aj, arole[k][aj], float(x)))
    T = pd.DataFrame(rows, columns=K.PS_TOKEN_COLS); N = pd.DataFrame(none, columns=K.PS_NONE_COLS)
    for c in ('src_author', 'src_j', 'layer', 'ans_j'): T[c] = T[c].astype(np.int16)
    T['nlr'] = T.nlr.astype(np.float64)
    return T, N


def shard_check(T, N, shard, tiny):
    """WARN-only reproduction numbers for the log (hard checks: stage13_b2_ps_analyze.py)."""
    out = dict(shard=shard, n_papers=int(T.paper_id.nunique()), n_rows=int(len(T)), tiny=tiny)
    if tiny: return out
    try:
        z = np.load(ROOT0 / f'raw/pscope/shard_{shard:03d}.npz'); ref = pd.DataFrame({k: z[k] for k in z.files if k != 'meta'}).set_index('paper_id')
        m = T[T.src_kind.isin(['title', 'colon'])].groupby(['paper_id', 'target', 'who', 'src_kind', 'layer']).nlr.mean()
        d = np.array([m[i] - ref.loc[i[0], f'{i[1]}@{i[2]}@{i[3]}@{i[4]}'] for i in m.index])
        out |= dict(pscope_cells=int(len(d)), pscope_max_abs=float(np.abs(d).max()), pscope_exact_share=float((np.abs(d) < 1e-12).mean()))
        nm = N.groupby(['paper_id', 'target']).nlr.mean(); dn = np.array([nm[i] - ref.loc[i[0], f'{i[1]}@none'] for i in nm.index])
        out['none_max_abs'] = float(np.abs(dn).max())
        for l in K.PS_LAYERS:
            Dn = (m.xs(('author', 'self', 'title', l), level=[1, 2, 3, 4]) - m.xs(('author', 'partner', 'title', l), level=[1, 2, 3, 4])).mean()
            Do = (ref[f'author@self@title@{l}'] - ref[f'author@partner@title@{l}']).loc[m.index.get_level_values(0).unique()].mean()
            out[f'D_author_title_L{l}_new'] = float(Dn); out[f'D_author_title_L{l}_pub'] = float(Do)
        x4 = pd.read_csv(ROOT0 / f'followup/x4tok2/shard_{shard:03d}.csv'); x4 = x4[x4.batch == 'b7'].set_index(['paper_id', 'source', 'layer', 'token_j']).nlr
        t = T[(T.src_kind == 'title') & (T.target == 'author') & T.layer.isin(K.X4TOK_HARD_LAYERS)].set_index(['paper_id', 'who', 'layer', 'ans_j']).nlr
        t.index = t.index.set_names(['paper_id', 'source', 'layer', 'token_j']); j = x4.to_frame('o').join(t.rename('n'), how='left')
        out |= dict(x4tok_rows=int(len(j)), x4tok_missing=int(j.n.isna().sum()), x4tok_max_abs=float((j.n - j.o).abs().max()), x4tok_exact_share=float(((j.n - j.o).abs() < 1e-12).mean()))
        out['status'] = 'OK' if out['pscope_max_abs'] <= 1e-9 and out['x4tok_max_abs'] <= 1e-9 and out['x4tok_missing'] == 0 else 'WARN'
    except Exception as e:
        out['status'] = f'WARN (check failed: {e!r})'
    return out


def claim(k, me):
    R['claims'].mkdir(parents=True, exist_ok=True); d = R['claims'] / f'ps_{k:03d}'
    try: d.mkdir(); (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")}\n'); return True
    except FileExistsError:
        try: o = (d / 'owner').read_text().split()[0]
        except Exception: o = ''
        if o and o.isdigit():
            try: st = subprocess.run(['squeue', '-h', '-j', o, '-o', '%T'], capture_output=True, text=True, timeout=60).stdout.strip()
            except Exception: st = 'UNKNOWN'
            if st == '':
                (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")} (reclaimed from {o})\n'); return True
        return False


def out_path(k): return R['raw'] / f'shard_{k:03d}.parquet'


def run(shards, tiny=False, max_minutes=None, C=None):
    me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); budget = max_minutes
    left = s11.slurm_minutes_left()
    if left is not None and (budget is None or left - 6 < budget): budget = left - 6
    todo = [k for k in shards if not out_path(k).exists()]
    log(f'b2_ps job {me}: {len(todo)} of {len(shards)} shards to do, budget {budget} min', 'TINY' if tiny else '')
    if not todo: return C
    if C is None: C = x2.tiny_ctx() if tiny else s13.Ctx()
    env = dict(getattr(C, 'env', {}), b2_script_sha256=s10.sha_file(__file__), plan_sha256=PLAN_SHA, job=me, ps_layers=list(s13.PS_LAYERS))
    for d in ('raw', 'chk', 'logs'): R[d].mkdir(parents=True, exist_ok=True)
    last = 0.0
    for k in todo:
        if out_path(k).exists(): continue
        est = 1.5 * max(last, 30 if tiny else 480) / 60
        if budget is not None and (time.monotonic() - T0) / 60 + est > budget: log('time budget reached; stop before shard', k); break
        if not tiny and not claim(k, me): log('claimed by another job, skip', k); continue
        t1 = time.monotonic()
        try:
            T, N = do_shard(C, k)
            f = out_path(k); fn = R['raw'] / f'none_{k:03d}.parquet'
            for df, ff in ((N, fn), (T, f)):                                      # main file last = completion marker
                tmp = ff.with_name(ff.stem + f'.tmp{os.getpid()}.parquet'); df.to_parquet(tmp, index=False); os.replace(tmp, ff)
            (R['raw'] / f'meta_{k:03d}.json').write_text(json.dumps(dict(env, unit=k, created=time.strftime('%Y-%m-%dT%H:%M:%S'))))
        except Exception as e:
            try: (R['logs'] / f'b2_ps_error_{k:03d}_{me}.txt').write_text(traceback.format_exc())
            except Exception: pass
            log('UNIT ERROR (logged, continue):', k, repr(e)); continue
        last = time.monotonic() - t1
        try:
            ck = shard_check(T, N, k, tiny); (R['chk'] / f'shard_{k:03d}.json').write_text(json.dumps(ck, indent=1))
            log(f'b2_ps shard {k:03d} papers={ck["n_papers"]} rows={ck["n_rows"]} {last:.0f}s total={(time.monotonic() - T0) / 60:.1f}min check={ck.get("status")}',
                'pscope_max_abs=%s x4tok_max_abs=%s D_author_title_L8 new/pub=%s/%s' % (ck.get('pscope_max_abs'), ck.get('x4tok_max_abs'), ck.get('D_author_title_L8_new'), ck.get('D_author_title_L8_pub')))
        except Exception as e: log('WARN: shard check / log failed', repr(e))
    return C


def tiny():
    """whole pipeline on the 2-layer random model (fp32), 3 papers of the first sample shard: compute -> save -> reload ->
    compare title / colon with the frozen do_pscope and x4tok code on the same model (must be equal), then the analysis runs
    on these files (stage13_b2_ps_analyze.py --tiny)."""
    tag = os.environ.get('B2_TAG', f'local{os.getpid()}'); set_root(True, tag)
    smp, pairs = s13.sample(); sh = int(smp.shard.iloc[0])
    _, toks = s11.cohort(); nctx = toks.groupby('paper_id').author_index.nunique()
    s = smp[(smp.shard == sh) & smp.paper_id.isin(pairs.index)].copy(); s['na'] = s.paper_id.map(nctx)
    sp = pairs.loc[s.paper_id].split.to_numpy()
    pick = pd.concat([s[(sp == 'tune') & (s.na >= 3)].head(1), s[(sp == 'test') & (s.na >= 2)].head(1), s[s.na == 1].head(1)])
    s13._CACHE['smp'] = pick.drop(columns='na'); s13.PS_LAYERS = [0, 1]; s13.XP_LAYERS = [0, 1]; s13.LAYERS = [0, 1]
    log('tiny papers', pick[['paper_id', 'na']].values.tolist(), 'raw', R['raw'])
    C = run([sh], tiny=True) or x2.tiny_ctx()
    ok = []
    def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)
    T = pd.read_parquet(out_path(sh)); N = pd.read_parquet(R['raw'] / f'none_{sh:03d}.parquet')
    check('columns = stage13_b2A_cols.PS_TOKEN_COLS', list(T.columns) == K.PS_TOKEN_COLS and list(N.columns) == K.PS_NONE_COLS)
    ref = s13.do_pscope(C, sh); rf = pd.DataFrame({k: v for k, v in ref.items()}).set_index('paper_id')
    ref_root = R['root'] / f'ref_{tag}'; (ref_root / 'raw/pscope').mkdir(parents=True, exist_ok=True)       # reference for the tiny analysis
    np.savez(ref_root / f'raw/pscope/shard_{sh:03d}.npz', meta=np.array('{}'), **ref)
    m = T[T.src_kind.isin(['title', 'colon'])].groupby(['paper_id', 'target', 'who', 'src_kind', 'layer']).nlr.mean()
    d = np.array([m[i] - rf.loc[i[0], f'{i[1]}@{i[2]}@{i[3]}@{i[4]}'] for i in m.index])
    check('title / colon per-paper means == frozen do_pscope', len(d) == len(rf) * 3 * 2 * 2 * 2 and np.abs(d).max() <= 1e-12, f'{len(d)} cells, max |diff| {np.abs(d).max():.2e}')
    nm = N.groupby(['paper_id', 'target']).nlr.mean(); dn = np.array([nm[i] - rf.loc[i[0], f'{i[1]}@none'] for i in nm.index])
    check('none == frozen do_pscope @none', np.abs(dn).max() <= 1e-12, f'max |diff| {np.abs(dn).max():.2e}')
    fu = load(H / '13_stage13/stage13_gpu_followup.py', 'followup'); fu.X4L = [0, 1]; fu.s13 = s13
    x4d = fu._x4tok(C, sh, 'b7', [0, 1]); x4d.to_csv(ref_root / 'x4tok_b7.csv', index=False); x4 = x4d.set_index(['paper_id', 'source', 'layer', 'token_j']).nlr
    t = T[(T.src_kind == 'title') & (T.target == 'author')].set_index(['paper_id', 'who', 'layer', 'ans_j']).nlr
    t.index = t.index.set_names(x4.index.names); j = x4.to_frame('o').join(t.rename('n'))
    check('author title per-token == frozen x4tok (b7)', j.n.notna().all() and (j.n - j.o).abs().max() <= 1e-12, f'{len(j)} rows, max |diff| {(j.n - j.o).abs().max():.2e}')
    nm_ = T[T.src_kind == 'name']
    exp = sum(sum(len(nm) - 1 for _, _, nm in C.ctx[p] if len(nm) >= 2) for p in pick.paper_id)
    got = nm_.groupby(['paper_id', 'src_author', 'src_j']).ngroups
    check('one name source per (author, j >= 1) of each paper', got == exp, f'{got} vs {exp}')
    check('name sources: both who, 3 targets, all layers', nm_.groupby(['paper_id', 'src_author', 'src_j']).apply(lambda g: g.who.nunique() == 2 and g.target.nunique() == 3 and g.layer.nunique() == 2).all())
    check('name sources differ from colon (non-trivial)', (nm_.groupby(['paper_id', 'who', 'target', 'layer', 'ans_j']).nlr.std().fillna(0) > 0).any())
    check('roles attached for name sources', (nm_.src_role != '?').mean() > 0.9, f'{(nm_.src_role != "?").mean():.3f}')
    print(f'TINY PS GPU-CODE {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)} (raw {R["raw"]})', flush=True)
    (R['root'] / 'summary_b2_ps').mkdir(parents=True, exist_ok=True); (R['root'] / 'summary_b2_ps/tiny_raw_dir.txt').write_text(str(R['raw']))
    sys.exit(0 if all(ok) else 1)


def main():
    a = sys.argv[1:]
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    mm = float(a[a.index('--max-minutes') + 1]) if '--max-minutes' in a else None
    if '--tiny' in a: tiny(); return
    set_root(False)
    if (R['root'] / 'summary_b2_ps/HARD_CHECK_FAILED').exists(): log('HARD_CHECK_FAILED present -> stop'); sys.exit(3)
    smp, _ = s13.sample()
    if '--all' in a: run(sorted(int(x) for x in smp.shard.unique()), max_minutes=mm); return
    if '--shards' in a:
        ks = []
        for x in a[a.index('--shards') + 1:]:
            if x.startswith('--'): break
            ks.append(int(x))
        run(ks, max_minutes=mm); return
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
