"""Stage 12 P2 hook check (U40; user decision 2026-10-30: "同意补 P2 的显式检查（L63 替换后应完全恢复），只跑 1 个分片").

Imports 371_stage12.py (and through it 361_stage11.py) by path, read-only; the frozen scripts are not changed.
Reruns P2 (patch_comp) on ONE shard of the Stage 11 sample with explicit controls. All component hooks use the SAME hook
body as 371_stage12.do_patch_comp (forward hook on decoder_layer.self_attn -> o[0][e, -tail:] = true value, or on
decoder_layer.mlp -> o[e, -tail:] = true value), plus an invocation counter. Residual (block-output) patches use the
Stage 11 path s11.run_final(patch=...). Batch elements of the false_0 run (all share one forward, as in P2):

  none          unpatched false_0 run (= P2 'none')
  full_true     POSITIVE CONTROL. attention AND MLP outputs of EVERY layer 0..63 replaced by the true run's on the whole
                aligned tail. The tail tokens are identical in both prompts, so the residual entering layer 0 at the tail
                is identical; by induction every block output at the tail, and so the final hidden state at the scored
                positions, equals the true run's bit for bit (each residual add sees identical operands). Expected:
                logits == true-run logits exactly; recovery = 1 exactly ("完全恢复").
  r62c63_true   POSITIVE CONTROL at L63 itself: residual output of block 62 on the tail replaced (Stage 11 path) + attention
                and MLP of layer 63 replaced (P2 hook path). Final residual = h62_true + attn63_true + mlp63_true = true:
                same exact expectation. This is the precise form of "L63 替换后应完全恢复": replacing ONLY the L63
                components cannot recover exactly, because the residual arriving from L62 still carries the false title.
  full_false    NEGATIVE CONTROL. Same hooks at every layer, but filled with the false_0 run's own components (recorded
                in a separate batch-1 false run). Expected: equals the batch-1 false run exactly, and the false baseline
                ('none', batched) up to batch-size bf16 noise; recovery 0.
  r62_true      residual of block 62 only (shows how much the L63 components still matter)
  attn63_true, mlp63_true, c63_true (attn63 + mlp63)   L63 components only (informational; not expected to be 1)
  attn56_true, mlp56_true   reproduce the stored P2 columns (parity with raw/patch_comp/shard_000.npz; WARN only)

Score as in P2 / Stage 11 E1: nlr = log10(1/rank) of the gold name token at the model output; recovery =
mean(patched - none) / mean(true - none) (pooled tokens, and paper means as in stage12_analyze). Also: gold-token
log-prob recovery, max |logit_patched - logit_true| over the whole vocabulary at the scored positions, max |final residual
- true| at the tail, hook call counts (each registered hook must fire exactly once per forward).
Tolerance (user rule): a few bf16 ulps - at |logit| 32-64 one ulp is 0.25, so max |dlogit| <= 1.0 (4 ulps) and
|recovery - 1| <= 0.01. Misses are WARN (value + threshold recorded); only a crash stops.

Usage: python stage12_p2_hookcheck.py --tiny   (CPU, random Qwen3 with 64 tiny layers (d=64; s11.run_final reads block 63), real tokenizer, 3 papers: whole pipeline)
       python stage12_p2_hookcheck.py --real   (GPU, Qwen3-32B bf16, Stage 11 sample shard SHARD=0)
"""
import importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
MODE = next((m for m in ('--tiny', '--real') if m in sys.argv), None)
if MODE is None: sys.exit(__doc__)
SHARD = int(os.environ.get('SHARD', '0'))
ROOT12 = Path('/scratch/zhang.zhiqi2/jlens/371_stage12')
OUT = ROOT12 / 'hookcheck_2026-10-30' / ('tiny' if MODE == '--tiny' else '')
TOL_LOGIT, TOL_REC, TOL_NEG = 1.0, 0.01, 0.01


def log(*x):
    try: print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
    except Exception: pass


_sp = importlib.util.spec_from_file_location('s12', H / '12_stage12/371_stage12.py'); s12 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s12)
s11, s10 = s12.s11, s12.s10


def make_ctx():
    if MODE == '--real': return s11.Ctx()
    import torch, transformers, jlens, pandas as pd
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]   # 64 tiny layers: s11.run_final reads block 63
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); tok = s10.tokenizer()

    class Tiny:
        def __init__(self):
            self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
            smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); self.smp = smp[smp.shard == SHARD].head(3)
            self.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(s10.ROOT, self.papers, s11.FALSE_FOR_PATCH)[0]}
            self.model = jlens.from_hf(hf, tok); self.tok = tok; self.env = dict(script_sha256='tiny', gpu=[])
    return Tiny()


def p2_hook(e, val, kind, cnt, key):
    """identical body to the hook in 371_stage12.do_patch_comp, plus a call counter."""
    def hook(m_, i_, o, e=e, val=val, kind=kind):
        cnt[key] = cnt.get(key, 0) + 1
        t = o[0] if kind == 'attn' else o
        t[e, -val.shape[0]:] = val.to(t.device, t.dtype); return o
    return hook


def run_check(C):
    torch = C.torch; model = C.model; NL = len(model.layers); LAST = NL - 1; PREV = LAST - 1
    REP = 56 if NL > 56 else 0
    elems = ['none', 'full_true', 'r62c63_true', 'full_false', 'r62_true', 'attn63_true', 'mlp63_true', 'c63_true', 'attn56_true', 'mlp56_true']
    B = len(elems); ei = {n: i for i, n in enumerate(elems)}
    # (element -> list of (kind, layer, source)); layer names use the real model's numbers, mapped onto LAST/PREV/REP
    comp_plan = {'full_true': [(k, l, 'T') for l in range(NL) for k in ('attn', 'mlp')],
                 'full_false': [(k, l, 'F') for l in range(NL) for k in ('attn', 'mlp')],
                 'r62c63_true': [('attn', LAST, 'T'), ('mlp', LAST, 'T')], 'attn63_true': [('attn', LAST, 'T')], 'mlp63_true': [('mlp', LAST, 'T')],
                 'c63_true': [('attn', LAST, 'T'), ('mlp', LAST, 'T')], 'attn56_true': [('attn', REP, 'T')], 'mlp56_true': [('mlp', REP, 'T')]}
    resid_plan = ['r62c63_true', 'r62_true']
    out = {k: [] for k in ('row_id', 'paper_id', 'nlr_true', 'nlr_false1', 'nlr', 'lp_true', 'lp_false1', 'lp', 'dlogit_true', 'dlogit_false1',
                           'rank_true', 'rank_patch')}
    ctxrows = []
    t0 = time.monotonic()
    for r in C.smp[C.smp.shard == SHARD].itertuples():
        pt, pfi, S = s12.tail_layout(C, r)
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; tail = S + len(name) - 1
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=model.input_device)
            assert T[-tail:] == F[-tail:], 'aligned tail differs'
            # ---- batch-1 runs of T and F: record every layer's attention / MLP output and block 62 / 63 outputs on the tail
            runs = {}
            for tag, ids, pos in (('T', T, posT), ('F', F, posF)):
                rec, hs = {}, []
                try:
                    for l in range(NL):
                        hs.append(model.layers[l].self_attn.register_forward_hook(lambda m_, i_, o, l=l: rec.__setitem__(('attn', l), o[0][0, -tail:].detach().clone())))
                        hs.append(model.layers[l].mlp.register_forward_hook(lambda m_, i_, o, l=l: rec.__setitem__(('mlp', l), o[0, -tail:].detach().clone())))
                    for l in (PREV, LAST):
                        hs.append(model.layers[l].register_forward_hook(lambda m_, i_, o, l=l: rec.__setitem__(('res', l), (o if torch.is_tensor(o) else o[0])[0, -tail:].detach().clone())))
                    lg = s11.run_final(C, ids, pos)[0]
                finally:
                    for h in hs: h.remove()
                runs[tag] = (rec, lg)
            recT, lt = runs['T']; recF, lf = runs['F']
            # ---- the patched false_0 batch
            cnt, hs, fin = {}, [], {}
            expected = {}
            try:
                for en, plan in comp_plan.items():
                    e = ei[en]
                    for kind, l, src in plan:
                        val = (recT if src == 'T' else recF)[(kind, l)]
                        mod = model.layers[l].self_attn if kind == 'attn' else model.layers[l].mlp
                        key = f'{en}|{kind}{l}'; expected[key] = 1
                        hs.append(mod.register_forward_hook(p2_hook(e, val, kind, cnt, key)))
                hs.append(model.layers[LAST].register_forward_hook(lambda m_, i_, o: fin.__setitem__('h', (o if torch.is_tensor(o) else o[0])[:, -tail:].detach().clone())))
                patch = {PREV: [(ei[en], tail, recT[('res', PREV)]) for en in resid_plan]}
                lp = s11.run_final(C, F, posF, patch=patch, batch=B)
            finally:
                for h in hs: h.remove()
            hf = fin['h'].float(); hT = recT[('res', LAST)].float(); hF = recF[('res', LAST)].float()
            calls = [cnt.get(k, 0) for k in expected]
            ctxrows.append(dict(paper_id=r.paper_id, author_index=ai, tail=tail, n_tokens=len(name),
                                hooks_registered=len(expected), hook_calls_min=min(calls), hook_calls_max=max(calls), hook_calls_total=sum(calls),
                                **{f'dres_{en}_vs_true': float((hf[ei[en]] - hT).abs().max()) for en in ('full_true', 'r62c63_true', 'r62_true', 'c63_true', 'none')},
                                **{f'dres_{en}_vs_false1': float((hf[ei[en]] - hF).abs().max()) for en in ('full_false', 'none')}))
            # ---- scores
            def sc(lg_):
                rk, _, lpg, _ = s10.score(lg_.float(), gold, torch); return rk, lpg
            rkT, lpT = sc(lt); rkF, lpF = sc(lf)
            rks, lps = zip(*[sc(lp[i]) for i in range(B)])
            nl = lambda x: -np.log10(np.asarray(x, float))
            out['row_id'] += rids; out['paper_id'] += [r.paper_id] * len(rids)
            out['rank_true'].append(rkT); out['rank_patch'].append(np.stack(rks, 1))
            out['nlr_true'].append(nl(rkT)); out['nlr_false1'].append(nl(rkF)); out['nlr'].append(nl(np.stack(rks, 1)))
            out['lp_true'].append(lpT); out['lp_false1'].append(lpF); out['lp'].append(np.stack(lps, 1))
            out['dlogit_true'].append(np.stack([(lp[i].float() - lt.float()).abs().amax(-1).cpu().numpy() for i in range(B)], 1))
            out['dlogit_false1'].append(np.stack([(lp[i].float() - lf.float()).abs().amax(-1).cpu().numpy() for i in range(B)], 1))
        log(f'paper {r.paper_id} done, {len(out["row_id"])} rows, {time.monotonic() - t0:.0f}s')
    d = {k: (np.array(v) if k in ('row_id', 'paper_id') else np.concatenate(v)) for k, v in out.items()}
    d['elems'] = np.array(elems); d['n_layers'] = np.array(NL)
    return d, ctxrows


def summarize(d, ctx, ref_file):
    import pandas as pd
    elems = list(d['elems']); none = elems.index('none'); res = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), mode=MODE, shard=SHARD,
                                                                       n_rows=int(len(d['row_id'])), n_contexts=len(ctx), n_papers=int(len(set(d['paper_id']))))
    rows = []
    for i, en in enumerate(elems):
        r = dict(elem=en)
        for sc in ('nlr', 'lp'):
            P, Tt, N = d[sc][:, i], d[f'{sc}_true'], d[sc][:, none]
            r[f'rec_{sc}_pooled'] = float((P - N).mean() / (Tt - N).mean())
            g = pd.DataFrame(dict(p=d['paper_id'], num=P - N, den=Tt - N)).groupby('p').mean()
            r[f'rec_{sc}_papermean'] = float(g.num.mean() / g.den.mean())
            r[f'max_abs_{sc}_vs_true'] = float(np.abs(P - Tt).max())
            r[f'max_abs_{sc}_vs_false1'] = float(np.abs(P - d[f'{sc}_false1']).max())
        r['rank_eq_true'] = float((d['rank_patch'][:, i] == d['rank_true']).mean())
        r['max_abs_logit_vs_true'] = float(d['dlogit_true'][:, i].max()); r['max_abs_logit_vs_false1'] = float(d['dlogit_false1'][:, i].max())
        rows.append(r)
    T = pd.DataFrame(rows).set_index('elem'); res['table'] = T.reset_index().to_dict('records')
    C = pd.DataFrame(ctx)
    res['hooks'] = dict(registered_per_forward=int(C.hooks_registered.iloc[0]), calls_min=int(C.hook_calls_min.min()), calls_max=int(C.hook_calls_max.max()),
                        total_calls=int(C.hook_calls_total.sum()), expected_total=int(C.hooks_registered.sum()))
    res['final_residual'] = {c: float(C[c].max()) for c in C.columns if c.startswith('dres_')}
    res['denominator'] = dict(mean_nlr_true_minus_none=float((d['nlr_true'] - d['nlr'][:, none]).mean()),
                              mean_lp_true_minus_none=float((d['lp_true'] - d['lp'][:, none]).mean()))
    chk = {}
    def add(name, val, ok, thr): chk[name] = dict(value=val, threshold=thr, status='PASS' if ok else 'WARN')
    for en in ('full_true', 'r62c63_true'):
        add(f'{en}: recovery nlr (pooled)', T.loc[en, 'rec_nlr_pooled'], abs(T.loc[en, 'rec_nlr_pooled'] - 1) <= TOL_REC, f'|x-1|<={TOL_REC}')
        add(f'{en}: recovery gold log-prob (pooled)', T.loc[en, 'rec_lp_pooled'], abs(T.loc[en, 'rec_lp_pooled'] - 1) <= TOL_REC, f'|x-1|<={TOL_REC}')
        add(f'{en}: max |nlr - true|', T.loc[en, 'max_abs_nlr_vs_true'], T.loc[en, 'max_abs_nlr_vs_true'] <= 0.05, '<=0.05')
        add(f'{en}: max |logit - true| (whole vocab)', T.loc[en, 'max_abs_logit_vs_true'], T.loc[en, 'max_abs_logit_vs_true'] <= TOL_LOGIT, f'<={TOL_LOGIT} (4 bf16 ulps at |logit| 32-64)')
        add(f'{en}: max |final residual - true| (tail)', res['final_residual'][f'dres_{en}_vs_true'], res['final_residual'][f'dres_{en}_vs_true'] == 0, '==0 (bitwise)')
    add('full_false: recovery nlr vs none (pooled)', T.loc['full_false', 'rec_nlr_pooled'], abs(T.loc['full_false', 'rec_nlr_pooled']) <= TOL_NEG, f'|x|<={TOL_NEG}')
    add('full_false: max |logit - false batch-1 run|', T.loc['full_false', 'max_abs_logit_vs_false1'], T.loc['full_false', 'max_abs_logit_vs_false1'] <= TOL_LOGIT, f'<={TOL_LOGIT}')
    add('full_false: max |final residual - false batch-1| (tail)', res['final_residual']['dres_full_false_vs_false1'], res['final_residual']['dres_full_false_vs_false1'] == 0, '==0 (bitwise)')
    add('none (batched) vs false batch-1: max |logit|', T.loc['none', 'max_abs_logit_vs_false1'], T.loc['none', 'max_abs_logit_vs_false1'] <= TOL_LOGIT, f'<={TOL_LOGIT} (batch-size noise)')
    h = res['hooks']; add('every hook fired exactly once per forward', [h['calls_min'], h['calls_max']], h['calls_min'] == 1 and h['calls_max'] == 1, 'min=max=1')
    add('c63_true (L63 components only) differs from true (sanity: not exact)', T.loc['c63_true', 'max_abs_logit_vs_true'], T.loc['c63_true', 'max_abs_logit_vs_true'] > 0, '>0')
    # parity with the stored P2 shard (WARN only; batch size 23 there, 10 here)
    if ref_file is not None and ref_file.exists():
        z = np.load(ref_file, allow_pickle=True); zc = list(z['comps']); m = dict(zip(z['row_id'], range(len(z['row_id']))))
        idx = np.array([m.get(x, -1) for x in d['row_id']]); ok = idx >= 0
        par = dict(rows_matched=int(ok.sum()), rows=int(len(idx)))
        par['rank_true_equal'] = float((z['rank_true'][idx[ok]] == d['rank_true'][ok]).mean())
        for mine, theirs in (('none', 'none'), ('attn56_true', 'attn56'), ('mlp56_true', 'mlp56')):
            a = z['rank_patch'][idx[ok], zc.index(theirs)]; b = d['rank_patch'][ok, elems.index(mine)]
            par[f'{theirs}_rank_equal'] = float((a == b).mean()); par[f'{theirs}_mean_abs_dnlr'] = float(np.abs(np.log10(a.astype(float)) - np.log10(b.astype(float))).mean())
        res['p2_parity'] = par
        add('parity with stored P2 shard (rank_true equal fraction)', par['rank_true_equal'], par['rank_true_equal'] >= 0.9, '>=0.9')
        for c in ('none', 'attn56', 'mlp56'):
            add(f'parity with stored P2: {c} mean |dnlr|', par[f'{c}_mean_abs_dnlr'], par[f'{c}_mean_abs_dnlr'] <= 0.05, '<=0.05 (bf16 batch noise)')
    res['checks'] = chk
    res['status'] = 'PASS' if all(v['status'] == 'PASS' for v in chk.values()) else 'WARN'
    return res, T


def report(res, T, path):
    f = lambda x: f'{x:.4g}' if isinstance(x, float) else str(x)
    L = [f'# Stage 12 P2 hook check (U40) - {res["mode"]} - shard {res["shard"]}', '',
         f'Created {res["created"]}. Script `12_stage12/stage12_p2_hookcheck.py` (imports 371_stage12.py unchanged). '
         f'{res["n_papers"]} papers, {res["n_contexts"]} author contexts, {res["n_rows"]} name tokens. **Status: {res["status"]}** (WARN = a threshold missed; recorded, nothing stopped).', '',
         '## Design', '',
         'All component patches use the P2 hook body (forward hook on `self_attn` / `mlp`, writes the true run\'s output on the aligned tail of one batch element).',
         '- `full_true`: attention + MLP outputs of every layer 0-63 replaced by the true run\'s on the tail. The tail tokens are identical, so the final hidden state at the scored positions must equal the true run\'s bit for bit; recovery must be 1 ("完全恢复").',
         '- `r62c63_true`: block-62 residual output on the tail (Stage 11 residual patch) + attention and MLP of layer 63 (P2 hooks). Final residual = h62 + attn63 + mlp63 of the true run: same exact expectation. Replacing only the L63 components (`c63_true`) cannot be exact, because the residual from L62 still carries the false title.',
         '- `full_false` (negative control): every layer\'s components replaced by the false run\'s own (from a batch-1 false run): must equal that run exactly and the false baseline up to batch noise; recovery 0.',
         '- `attn56_true`, `mlp56_true`, `none`: reproduce the stored P2 columns of this shard.',
         '- recovery = mean(patched - none) / mean(true - none); nlr = log10(1/rank) of the gold token at the model output; lp = gold-token log-prob.', '',
         f'Denominator (mean true - none): nlr {res["denominator"]["mean_nlr_true_minus_none"]:.4f}, log-prob {res["denominator"]["mean_lp_true_minus_none"]:.4f}.', '',
         '## Per element', '', '| element | recovery nlr (pooled / paper means) | recovery log-prob | max abs nlr - true | max abs logit - true | max abs logit - false batch-1 | rank = true |', '|---|---|---|---|---|---|---|']
    for en, r in T.iterrows():
        L.append(f'| {en} | {r.rec_nlr_pooled:.4f} / {r.rec_nlr_papermean:.4f} | {r.rec_lp_pooled:.4f} | {r.max_abs_nlr_vs_true:.4g} | {r.max_abs_logit_vs_true:.4g} | {r.max_abs_logit_vs_false1:.4g} | {r.rank_eq_true:.3f} |')
    L += ['', '## Checks', '', '| check | value | threshold | status |', '|---|---|---|---|']
    for k, v in res['checks'].items(): L.append(f'| {k} | {f(v["value"])} | {v["threshold"]} | {v["status"]} |')
    L += ['', f'Hooks: {res["hooks"]}', '', f'Final residual max abs diff on the tail: {json.dumps(res["final_residual"])}']
    if 'p2_parity' in res: L += ['', f'Parity with stored `raw/patch_comp/shard_{res["shard"]:03d}.npz`: {json.dumps(res["p2_parity"])}']
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text('\n'.join(L) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / f'shard_{SHARD:03d}.npz'
    C = make_ctx()
    log('ctx ready', MODE, 'layers', len(C.model.layers), 'papers in shard', int((C.smp.shard == SHARD).sum()))
    d, ctx = run_check(C)
    meta = dict(mode=MODE, shard=SHARD, created=time.strftime('%Y-%m-%dT%H:%M:%S'), env=C.env, job=os.environ.get('SLURM_JOB_ID'),
                hookcheck_sha256=s11.sha_file(__file__), s12_sha256=s11.sha_file(H / '12_stage12/371_stage12.py'))
    tmp = raw.with_name(raw.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **d); os.replace(tmp, raw)
    import pandas as pd; pd.DataFrame(ctx).to_csv(OUT / f'contexts_{SHARD:03d}.csv', index=False)
    # reload from disk, then summarise (tests the write -> reload -> summary path)
    z = np.load(raw, allow_pickle=True); d2 = {k: z[k] for k in z.files if k != 'meta'}
    assert all(np.array_equal(d[k], d2[k]) for k in d), 'reload mismatch'
    ref = ROOT12 / f'raw/patch_comp/shard_{SHARD:03d}.npz'
    res, T = summarize(d2, pd.read_csv(OUT / f'contexts_{SHARD:03d}.csv').to_dict('records'), ref if MODE == '--real' else None)
    res['meta'] = meta
    (OUT / 'summary.json').write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
    rp = ROOT12 / 'reports/p2_hookcheck.md' if MODE == '--real' else OUT / 'p2_hookcheck_tiny.md'
    report(res, T, rp)
    log('STATUS', res['status']); print(open(rp).read(), flush=True)


if __name__ == '__main__':
    main()
