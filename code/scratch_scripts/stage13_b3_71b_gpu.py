"""Batch 3 item 3-3 (addendum 14): Stage 7.1B terminal readout completed on the Stage 10 fast path, GPU.

7.1B (07_1_stage7_1/351_stage7_1B_terminal.py, frozen, not edited) froze 15,519 contexts = Pilot50 paper x title condition
(true = shuffle 0, 20 wrong titles = shuffle 1..20) x gold name prefix; each context scores the next gold name token of every
author sharing that prefix, at final L63 and public J-lens / logit (7.1B 'jlens' / 'vanilla') at L16-L62 (7 layers). The old
path ran one per-prefix lens.apply forward per context (layers 29-63 on CPU); only the first 1,166 contexts (7 papers) were run.
Fast path here: for every paper x condition x author ONE forward over encode(prompt) + name[:-1] (frozen 351_stage10.fast_readout,
model from 351_stage10_fix1.load_model, public lens from the Stage 10 registry, sha 0af5ccf2 = the 7.1B lens), every name token j
read at the position before it = the 7.1B context (prompt, prefix name[:j]). Scores as 351_stage10.score (rank = 1 + number of
strictly greater logits; log_softmax). Unit = paper: raw/b3_71b/paper_<paper_id>.npz (keys stage13_b3_cols.RAW_71B).
For papers with old 7.1B results the old rank / logprob are stored beside the new ones, with the bf16 distance to the old rank.
Commands
  run [--gate | --all] [--max-minutes M] [--tiny [--tiny-papers N]]
        --gate: the 7 papers holding the 1,166 old contexts, then gate-check (exit 3 on FAIL unless HC33_POLICY=warn)
        --all : every remaining paper (refuses unless gate.json is PASS, or HC33_POLICY=warn and gate.json exists)
  gate-check   CPU: hard check (rank match >= 99% over all scores of the 1,166 old contexts) -> summary_b3_71b/gate.json
  remaining | chain --sbatch F | tiny-ref (CPU: old per-prefix helper.readout on the tiny model for the tiny reference)
"""
import argparse, importlib.util, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b3_cols.py', 'b3_cols'); CK = load(H / '13_stage13/stage13_b3_checks.py', 'b3_checks')
G = load(H / '13_stage13/stage13_b3_s10_gpu.py', 'b3_s10_gpu'); s10 = G.s10; fix1 = G.fix1
T71 = load(H / '07_1_stage7_1/351_stage7_1B_terminal.py', 's71b')
ME = G.ME; log = G.log; wjson = G.wjson
POLICY = os.environ.get('HC33_POLICY', 'plan')        # 'plan' (default, the frozen rule: FAIL stops) | 'warn' (only if the user approves)
PLAN71 = [(K.R71_S10NAME[m], l) for m, l in K.R71_READOUTS]


def roots(tiny):
    R = K.r71_roots(tiny); R['ref'] = (R['raw'].parent.parent / 'ref71b_raw') if tiny else K.R71B / 'raw'; return R


def frozen_71b():
    ns = argparse.Namespace(root=K.R71B)
    plan, tasks, manifest = T71.verify(ns)                                    # 7.1B frozen files + sources + task hashes
    authors = T71.read(K.R71B / 'authors.json')
    if len(tasks) != K.N_TASKS_71B: raise RuntimeError('7.1B task count differs')
    return plan, tasks, authors


def done_tasks(R, tasks):
    have = {f.stem for f in R['ref'].glob('*.json')} if R['ref'].exists() else set()
    return [t for t in tasks if t['task_id'] in have]


def gate_papers(R, tasks, tiny):
    d = done_tasks(R, tasks)
    ps = []
    for t in d:
        if t['paper_id'] not in ps: ps.append(t['paper_id'])
    return ps


def paper_order(tasks):
    ps = []
    for t in tasks:
        if t['paper_id'] not in ps: ps.append(t['paper_id'])
    return ps


def unit_path(R, pid): return R['raw'] / f'paper_{pid}.npz'


def ref_map(R, tasks_p):
    """old 7.1B scores of one paper: (shuffle, ai, j, mode, layer) -> (rank, logprob)."""
    out = {}
    for t in tasks_p:
        f = R['ref'] / f"{t['task_id']}.json"
        if not f.exists(): continue
        r = json.loads(f.read_text())
        for q in r['rows']: out[(t['shuffle_index'], q['author_index'], q['token_index'], q['mode'], int(q['layer']))] = (q['rank'], q['logprob'])
    return out


def compute_paper(model, L, pid, tasks_p, authors_p, ref, torch):
    conds = sorted({(t['shuffle_index'], t['prompt']) for t in tasks_p})
    if [c[0] for c in conds] != list(range(K.K_WRONG + 1)): raise RuntimeError(f'{pid}: conditions differ')
    rows = []; res_all = []
    for k, prompt in conds:
        base = model.encode(prompt, max_length=512).reshape(-1).tolist()
        for au in authors_p:
            name = au['token_ids']; ids = base + name[:-1]
            if len(base) >= 512 or len(ids) > 512: raise RuntimeError('context reaches the truncation limit')
            pos = [len(base) - 1 + j for j in range(len(name))]
            res = s10.fast_readout(model, L, ids, pos, PLAN71, torch)
            gold = torch.tensor(name, device=model.input_device)
            sc = []
            for pi, rl in enumerate(PLAN71):
                lg = res[rl]; rk, ti, lp, t1 = s10.score(lg, gold, torch)
                gl = lg.gather(1, gold.to(lg.device)[:, None])[:, 0].float().cpu().numpy()
                m7, l7 = K.R71_READOUTS[pi]
                rr = np.array([ref.get((k, au['author_index'], j, m7, l7), (0, np.nan))[0] for j in range(len(name))])
                rl_lp = np.array([ref.get((k, au['author_index'], j, m7, l7), (0, np.nan))[1] for j in range(len(name))], float)
                ul = np.full(len(name), np.nan)
                has = rr > 0
                if has.any():
                    ul[has] = 0.0; mis = np.nonzero(has & (rk != rr))[0]
                    if len(mis):
                        mt = torch.tensor(mis, device=lg.device)
                        ul[mis] = CK.ulps_to_rank_torch(lg[mt], gold.to(lg.device)[mt], torch.tensor(rr[mis]), torch)
                sc.append((rk, lp, ti, t1, gl, rr, rl_lp, ul))
            res_all.append(sc)
            for j, tid in enumerate(name): rows.append((k, au['author_index'], j, tid))
    n = len(rows); P = len(PLAN71)
    out = {x: np.zeros((P, n), dt) for x, dt in (('rank', np.int32), ('logprob', np.float32), ('ties', np.int32), ('top1', np.int32), ('logit_gold', np.float32),
                                                ('ref_rank', np.int32), ('ref_logprob', np.float32), ('ulps', np.float32))}
    c0 = 0
    for sc in res_all:
        m_ = len(sc[0][0])
        for pi in range(P):
            for x, v in zip(['rank', 'logprob', 'ties', 'top1', 'logit_gold', 'ref_rank', 'ref_logprob', 'ulps'], sc[pi]): out[x][pi, c0:c0 + m_] = v
        c0 += m_
    a = np.array(rows)
    out.update(shuffle_index=a[:, 0].astype(np.int16), author_index=a[:, 1].astype(np.int16), token_index=a[:, 2].astype(np.int16), token_id=a[:, 3].astype(np.int64))
    if (out['rank'] < 1).any(): raise RuntimeError(f'unfilled ranks {pid}')
    # coverage: every 7.1B target of this paper is a row here
    have = set(zip(a[:, 0], a[:, 1], a[:, 2], a[:, 3]))
    for t in tasks_p:
        for q in t['targets']:
            if (t['shuffle_index'], q['author_index'], q['token_index'], q['token_id']) not in have: raise RuntimeError(f'7.1B target not covered {t["task_id"]}')
    return out


def tiny_lenses():
    return json.loads((G.TINY_S10 / 'config/lenses.json').read_text())


def run(a):
    import torch
    K.check_plan(); R = roots(a.tiny); plan, tasks, authors = frozen_71b()
    if R['fail'].exists() and POLICY == 'plan': log('REFUSE: HARD_CHECK_FAILED marker exists', R['fail']); sys.exit(3)
    gp = gate_papers(R, tasks, a.tiny); allp = paper_order(tasks)
    if not a.tiny and (len(gp) != 7 or len(done_tasks(R, tasks)) != K.N_DONE_71B): raise RuntimeError(f'old 7.1B coverage differs: {len(gp)} papers')
    if a.all:
        if not a.tiny:
            g = json.loads(R['gate'].read_text()) if R['gate'].exists() else None
            if g is None or not (g['status'] == 'PASS' or (POLICY == 'warn' and g['status'] in ('PASS', 'WARN', 'FAIL'))):
                log('REFUSE --all: gate.json missing or not PASS (HC33_POLICY=%s)' % POLICY); sys.exit(3)
        want = [p for p in allp if p not in gp]
        if a.tiny: want = want[:a.tiny_papers]
    else:
        want = gp if not a.tiny else gp[:1]
    todo = [p for p in want if not unit_path(R, p).exists()]
    log(f'b3_71b job {ME}: {len(todo)} of {len(want)} papers to do ({"all" if a.all else "gate"}); budget {a.max_minutes} min', 'TINY' if a.tiny else '')
    t_start = time.monotonic()
    if todo:
        if a.tiny: lenses = tiny_lenses(); model, tok = G.tiny_model()
        else:
            _, lenses = s10.verify(K.R10); model, tok = fix1.load_model()
        if lenses['public']['sha256'] != (lenses['public']['sha256'] if a.tiny else T71.LENS_SHA): raise RuntimeError('public lens sha differs from 7.1B lens')
        for au in authors:
            if tok.encode(' ' + au['author'], add_special_tokens=False) != au['token_ids']: raise RuntimeError('author tokenization changed')
        L = s10.open_lenses(lenses, [p for p in PLAN71 if p[0] != 'final'], model)
        env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
                   s10_script_sha256=s10.sha_file(s10.__file__), s71b_script_sha256=s10.sha_file(T71.__file__), wrapper_sha256=s10.sha_file(__file__),
                   plan_sha256=K.PLAN_SHA, lens_sha256=lenses['public']['sha256'], job=ME, tiny=a.tiny, readouts=[f'{m}@L{l}' for m, l in K.R71_READOUTS])
        log('model + lens ready', f'{(time.monotonic() - t_start) / 60:.1f} min'); last = 0.0
        for pid in todo:
            if a.max_minutes and (time.monotonic() - t_start) / 60 + 1.5 * max(last, 30) / 60 > a.max_minutes: log('time budget reached'); break
            if unit_path(R, pid).exists(): continue
            if not G.claim(R, 'paper', int(allp.index(pid))): log('claimed by another job, skip', pid); continue
            t0 = time.monotonic(); tp = [t for t in tasks if t['paper_id'] == pid]
            d = compute_paper(model, L, pid, tp, [x for x in authors if x['paper_id'] == pid], ref_map(R, tp), torch)
            meta = dict(env, paper_id=pid, group=tp[0]['group'], n_rows=int(d['rank'].shape[1]), created=s10.now(), seconds=time.monotonic() - t0)
            f = unit_path(R, pid); f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
            np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f); last = time.monotonic() - t0
            try:
                h = d['ref_rank'] > 0
                log(f'paper {pid[:10]} rows={d["rank"].shape[1]} {last:.0f}s' + (f' old-match {(d["rank"][h] == d["ref_rank"][h]).mean():.4f} n={int(h.sum())}' if h.any() else ''))
            except Exception as e: log('WARNING log line failed', e)
    if not a.all:
        res = gate_check(a.tiny)
        if res['status'] == 'FAIL' and POLICY == 'plan': log('GATE HARD CHECK FAILED -> exit 3'); sys.exit(3)


def check_table(R, tasks, papers):
    """all old 7.1B scores of the given papers vs the new rows."""
    rows = []
    for pid in papers:
        z = np.load(unit_path(R, pid)); h = z['ref_rank'] > 0
        for pi, (m7, l7) in enumerate(K.R71_READOUTS):
            hh = h[pi]
            rows.append(pd.DataFrame(dict(paper_id=pid, shuffle_index=z['shuffle_index'][hh], author_index=z['author_index'][hh], token_index=z['token_index'][hh],
                                          token_id=z['token_id'][hh], mode=m7, layer=l7, rank_old=z['ref_rank'][pi][hh], rank_new=z['rank'][pi][hh],
                                          logprob_old=z['ref_logprob'][pi][hh], logprob_new=z['logprob'][pi][hh], ulps=z['ulps'][pi][hh])))
    return pd.concat(rows, ignore_index=True)


def summarise(D, scope):
    out = []
    for (m7, l7), g in [(('ALL', -1), D)] + list(D.groupby(['mode', 'layer'])):
        ex = g.rank_old == g.rank_new; w = (~ex) & (g.ulps <= K.ULPS_MAX)
        out.append(dict(scope=scope, mode=m7, layer=l7, n_scores=len(g), n_exact=int(ex.sum()), share_exact=float(ex.mean()), n_within_4_bf16=int(w.sum()),
                        share_exact_or_within=float((ex | w).mean()), max_ulps=float(g.ulps[~ex].max()) if (~ex).any() else 0.0,
                        max_abs_dlogprob=float((g.logprob_new - g.logprob_old).abs().max()),
                        max_abs_dlog10rank=float((np.log10(g.rank_new) - np.log10(g.rank_old)).abs().max())))
    return pd.DataFrame(out)[K.R71_HC_SUMMARY]


def gate_check(tiny):
    R = roots(tiny); plan, tasks, authors = frozen_71b()
    gp = gate_papers(R, tasks, tiny); have = [p for p in gp if unit_path(R, p).exists()]
    D = check_table(R, tasks, have)
    nd = len(done_tasks(R, tasks)); exp = sum(len(t['targets']) for t in done_tasks(R, tasks) if t['paper_id'] in have) * len(K.R71_READOUTS)
    S = summarise(D, 'old 7.1B contexts'); K.write_csv(S, R['summ'] / 'hardcheck_rank_match.csv', K.R71_HC_SUMMARY)
    try: D.to_parquet(R['summ'] / 'hardcheck_rows.parquet', index=False)
    except Exception as e: log('WARNING could not write rows parquet', e)
    pooled = S.iloc[0]
    complete = len(have) == len(gp) and len(D) == exp
    st = 'PASS' if complete and pooled.share_exact >= K.R71B_RANK_MIN else 'FAIL'
    checks = [dict(item='3-3', check='rank_match_old_7_1B', scope=f'{nd} old contexts, {len(D)} scores', value=float(pooled.share_exact), threshold=K.R71B_RANK_MIN,
                   status=st, kind='HARD', note=f'complete={complete} ({len(D)}/{exp} scores)'),
              dict(item='3-3', check='rank_match_or_within_4_bf16', scope='same', value=float(pooled.share_exact_or_within), threshold=K.R71B_RANK_MIN,
                   status='PASS' if pooled.share_exact_or_within >= K.R71B_RANK_MIN else 'WARN', kind='INFO (not in the plan; the 3-1 tolerance rule applied to 3-3)',
                   note=f'max ulps {pooled.max_ulps:.2f}')]
    status = st if POLICY == 'plan' else ('PASS' if st == 'PASS' else 'WARN')
    res = dict(item='3-3', status=status, plan_status=st, policy=POLICY, tiny=tiny, created=s10.now(), papers=have, checks=checks,
               per_readout=S.to_dict('records'))
    wjson(R['gate'], res)
    if st == 'FAIL' and POLICY == 'plan': R['fail'].parent.mkdir(parents=True, exist_ok=True); R['fail'].write_text(time.ctime() + '\n')
    try:
        for c in checks: log('GATE', c['status'], c['check'], f"value={c['value']:.6g} thr={c['threshold']}", c['note'])
        log('GATE STATUS', status, '(plan status', st + ', policy', POLICY + ')')
    except Exception as e: log('WARNING', e)
    return res


def remaining(a, quiet=False):
    R = roots(a.tiny); _, tasks, _ = frozen_71b(); n = sum(not unit_path(R, p).exists() for p in paper_order(tasks))
    if not quiet: print(n)
    return n


def chain(a):
    R = roots(a.tiny); R['chain'].mkdir(parents=True, exist_ok=True); n = remaining(a, quiet=True)
    rnd = int(os.environ.get('ROUND', '1')); mx = int(os.environ.get('MAX_ROUNDS', '4'))
    def submit(marker, cmd):
        if a.dry: log('dry run: would create marker', marker, 'and run', ' '.join(cmd)); return
        try: fd = os.open(R['chain'] / marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, f'{ME}\n'.encode()); os.close(fd)
        except FileExistsError: log('chain marker exists:', marker); return
        log('SUBMIT', ' '.join(cmd))
        if a.dry: log('dry run: not submitted'); return
        for i in range(3):
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=120); log('sbatch:', p.stdout.strip(), p.stderr.strip())
                if p.returncode == 0: return
            except Exception as e: log('sbatch error', e)
            q = subprocess.run(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%j'], capture_output=True, text=True).stdout
            log('after sbatch error, squeue job names:', ' '.join(sorted(set(q.split())))); time.sleep(30)
    if n > 0:
        if rnd >= mx: log(f'{n} papers remain, MAX_ROUNDS={mx} reached: stop'); return
        submit(f'round_{rnd + 1}', ['sbatch', f'--export=ALL,MODE=all,AUTO=1,ROUND={rnd + 1},MAX_ROUNDS={mx},HC33_POLICY={POLICY}', a.sbatch])
    else: submit('analyze', ['sbatch', f'--export=ALL,HC33_POLICY={POLICY}', a.analyze_sbatch])


def tiny_ref(a):
    """tiny reference = the OLD 7.1B per-prefix path (frozen helper.readout from ~/351_stage5.py, sha-checked) on the tiny model,
    for the contexts of the first paper; written in the 7.1B raw JSON row format into the tiny ref dir."""
    import torch
    R = roots(True); plan, tasks, authors = frozen_71b(); R['ref'].mkdir(parents=True, exist_ok=True)
    helper_path = Path.home() / '351_stage5.py'
    if s10.sha_file(helper_path) != T71.HELPER_SHA: raise RuntimeError('Stage 5 helper sha differs')
    helper = load(helper_path, 'frozen_stage5')
    import jlens
    model, tok = G.tiny_model(); lens = jlens.JacobianLens.load(tiny_lenses()['public']['path'])
    pid = paper_order(tasks)[0]; tp = [t for t in tasks if t['paper_id'] == pid][:a.tiny_contexts]
    for t in tp:
        base = model.encode(t['prompt'], max_length=512).reshape(-1).tolist(); ids = base + t['prefix_ids']
        vec = helper.readout(lens, model, t['prompt'], ids, torch)
        rows = []
        for name, v in vec.items():
            lp = torch.log_softmax(v.float(), dim=-1); mode, layer = name.rsplit('_L', 1)
            for q in t['targets']:
                rk = 1 + int((v > v[q['token_id']]).sum().item())
                rows.append(dict(**q, mode=mode, layer=int(layer), rank=rk, rr=1 / rk, logprob=float(lp[q['token_id']].item())))
        T71.save(R['ref'] / f"{t['task_id']}.json", dict(task_id=t['task_id'], rows=rows, tiny=True))
    log('tiny 7.1B reference (old per-prefix path):', len(tp), 'contexts of', pid, '->', R['ref'])


def main():
    K.check_plan()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=['run', 'gate-check', 'remaining', 'chain', 'tiny-ref'])
    ap.add_argument('--gate', action='store_true'); ap.add_argument('--all', action='store_true'); ap.add_argument('--max-minutes', type=float, default=None)
    ap.add_argument('--tiny', action='store_true'); ap.add_argument('--tiny-papers', type=int, default=2); ap.add_argument('--tiny-contexts', type=int, default=40)
    ap.add_argument('--sbatch', default=str(H / '13_stage13/stage13_b3_71b_gpu.sbatch'))
    ap.add_argument('--analyze-sbatch', default=str(H / '13_stage13/stage13_b3_71b_analyze.sbatch')); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    if a.command == 'tiny-ref': return tiny_ref(a)
    if a.command == 'gate-check': r = gate_check(a.tiny); sys.exit(3 if r['status'] == 'FAIL' else 0)
    {'run': run, 'remaining': remaining, 'chain': chain}[a.command](a)


if __name__ == '__main__':
    main()
