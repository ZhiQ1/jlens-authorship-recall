"""C24 / plan_batch_20261114b item 1a, option A (POST-HOC, exploratory; coordinator go 2026-11-14, within the ~0.5 A100-h approval).
New file; frozen code is only imported by path (stage13_b2_gennames_b_gpu.py -> v3b -> v3 (patched) -> rev2 pipeline).

GPU, shard 0 only (143 papers), one job:
  (1) REGENERATE with the frozen 2-11b generation call B.gen_one (greedy, 96 new tokens, batch 1, KV cache, output_hidden_states,
      output_logits; same chat prompt) and keep per generation step: logit of the generated token, top-5 logits + ids,
      logsumexp, full entropy (float32 on the raw step logits). Hidden states are NOT saved.
      Check (WARN only): regenerated token ids == stored papers/shard_000.csv gen_ids (share of papers; share of positions on the
      common prefix).
  (2) REPLAY (teacher-forced, use_cache=False, one forward per paper, exactly as stage13_b2_gennames_b_conf.py) of the STORED
      generated tokens; same per-position quantities. Old 0.99 replay gate = WARN only (never a stop).
  (3) item-1a rule: mismatch = replay argmax != generated token. For each mismatch: replay logit gap argmax - generated token
      (= log-prob gap), bf16 ulp at the magnitude of the larger logit (2^(floor(log2|x|) - 7)), share within 4 ulps; generation-time
      vs replay logit/log-prob of the generated token at every position. Per M/H name (names/shard_000.parquet): confidence =
      mean log-prob over all name tokens (primary), entropy at the pre-name position, min log-prob; |replay - generation|:
      median, max, share of names affected. Decision: >= 95% of mismatches within 4 ulps AND median |d mean log-prob| < 0.01 -> WARN,
      replay probabilities usable; else not.
Outputs: /scratch/zhang.zhiqi2/jlens/381_stage13/c24_regen_20261114/ (positions_000.parquet, names_000.parquet, regen_000.json,
         decision.json, report.md). Commands: gpu | tiny --out DIR | evaluate [--root DIR]
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); SRC = R13 / 'b2_gennames_b'; OUT = R13 / 'c24_regen_20261114'
_sp = importlib.util.spec_from_file_location('gnb_gpu', H / '13_stage13/stage13_b2_gennames_b_gpu.py'); G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
B = G.B; OLD_GATE = 0.99; K = 0


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def atomic(path, write):
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_name(path.stem + f'.tmp{os.getpid()}' + path.suffix); write(tmp); os.replace(tmp, path)


def stats_rows(lg, tgt, torch):
    """lg [n, V] raw logits (any dtype) for n positions, tgt [n] next tokens -> list of dicts (float32 math)."""
    x = lg.float(); lse = torch.logsumexp(x, -1); lp = x - lse[:, None]; ent = -(lp.exp() * lp).sum(-1)
    t5v, t5i = x.topk(5, -1); t = torch.tensor(tgt, device=x.device); lt = x.gather(1, t[:, None])[:, 0]
    a = [v.cpu().numpy() for v in (lt, lse, ent, t5v, t5i)]
    return [dict(logit_tok=float(a[0][i]), lse=float(a[1][i]), ent=float(a[2][i]), top5_logit=a[3][i].tolist(), top5_id=a[4][i].tolist()) for i in range(len(tgt))]


def run_shard(src, out, d, hf, tok, torch, max_new=None, names_override=None):
    import pandas as pd
    PP = pd.read_csv(src / f'papers/shard_{K:03d}.csv'); rows = []; preg = []; t0 = time.perf_counter(); tg = tr = 0.0
    for r in PP.itertuples():
        pr = B.V1.chat_prompt(tok, d.loc[r.paper_id, 'title'], d.loc[r.paper_id, 'year']); pids = tok(pr, add_special_tokens=False).input_ids; P = len(pids)
        stored = json.loads(r.gen_ids)
        t1 = time.perf_counter()
        g = B.gen_one(hf, tok, torch, pids, B.LAYERS, None, **({} if max_new is None else dict(max_new=max_new)))   # frozen generation call
        regen = g['gen']; tg += time.perf_counter() - t1
        cp = 0
        while cp < min(len(regen), len(stored)) and regen[cp] == stored[cp]: cp += 1
        # generation-time stats: step i logits predict regen[i]; valid for comparison with the stored sequence for i <= cp (same prefix)
        nv = min(len(g['logits']), len(stored), cp + 1)
        gl = torch.cat([g['logits'][i] for i in range(nv)], 0) if nv else None
        gs = stats_rows(gl, stored[:nv], torch) if nv else []
        gam = gl.argmax(-1).cpu().numpy().tolist() if nv else []
        del g, gl
        preg.append(dict(paper_id=r.paper_id, n_stored=len(stored), n_regen=len(regen), identical=regen == stored, common_prefix=cp, n_prompt_ok=P == int(r.n_prompt)))
        seq = pids + stored
        if len(stored) < 1: continue
        t1 = time.perf_counter()
        with torch.inference_mode():
            lg = hf(input_ids=torch.tensor([seq[:-1]], device=hf.device), use_cache=False).logits[0][P - 1:]
            rs = stats_rows(lg, stored, torch); ram = lg.argmax(-1).cpu().numpy().tolist()
        del lg; tr += time.perf_counter() - t1
        for i in range(len(stored)):
            row = dict(paper_id=r.paper_id, pos=P - 1 + i, step=i, tok=stored[i], rep_argmax=ram[i], **{'rep_' + k: v for k, v in rs[i].items()})
            if i < nv: row.update(gen_valid=True, gen_argmax=gam[i], **{'gen_' + k: v for k, v in gs[i].items()})
            else: row.update(gen_valid=False)
            rows.append(row)
    Pdf = pd.DataFrame(rows); R = pd.DataFrame(preg)
    meta = dict(papers=len(PP), regen_identical_papers=int(R.identical.sum()), regen_identical_share=float(R.identical.mean()),
                positions=len(Pdf), gen_valid_positions=int(Pdf.gen_valid.sum()), prompt_len_ok=bool(R.n_prompt_ok.all()),
                t_generate_s=tg, t_replay_s=tr, wall_s=time.perf_counter() - t0, job=os.environ.get('SLURM_JOB_ID'))
    meta['regen_check'] = 'OK' if meta['regen_identical_share'] == 1.0 else 'WARN'
    atomic(out / f'positions_{K:03d}.parquet', lambda p: Pdf.to_parquet(p, index=False)); atomic(out / f'regen_papers_{K:03d}.csv', lambda p: R.to_csv(p, index=False))
    atomic(out / f'regen_{K:03d}.json', lambda p: p.write_text(json.dumps(meta, indent=1)))
    log('regen+replay', meta); return meta


def ulp_bf16(x):
    x = np.maximum(np.abs(np.asarray(x, float)), 1e-30); return 2.0 ** (np.floor(np.log2(x)) - 7)


def evaluate(root, src=SRC, names=None):
    import pandas as pd
    Pdf = pd.read_parquet(root / f'positions_{K:03d}.parquet'); meta = json.loads((root / f'regen_{K:03d}.json').read_text())
    agree = float((Pdf.rep_argmax == Pdf.tok).mean()); n_mm = int((Pdf.rep_argmax != Pdf.tok).sum())
    rep_top1 = Pdf.rep_top5_logit.map(lambda v: v[0]).to_numpy(float)
    Pdf['rep_gap'] = rep_top1 - Pdf.rep_logit_tok.to_numpy(float)                       # >= 0; = log-prob gap (same lse)
    Pdf['ulp'] = ulp_bf16(np.maximum(np.abs(rep_top1), np.abs(Pdf.rep_logit_tok.to_numpy(float))))
    Pdf['gap_ulps'] = Pdf.rep_gap / Pdf.ulp
    Pdf['rep_lp'] = Pdf.rep_logit_tok - Pdf.rep_lse
    v = Pdf.gen_valid.to_numpy(bool)
    Pdf['gen_lp'] = np.where(v, Pdf.get('gen_logit_tok', np.nan) - Pdf.get('gen_lse', np.nan), np.nan)
    mm = Pdf[Pdf.rep_argmax != Pdf.tok].copy()
    # name-predicting positions: pre-name .. tok_last-1 of M/H names (as h2 rows)
    N = names if names is not None else pd.read_parquet(src / f'names/shard_{K:03d}.parquet')
    N = N[N.status.isin(['M', 'H'])].copy()
    key = set(); spans = []
    for x in N.itertuples():
        f, l = int(x.tok_first), int(x.tok_last); spans.append((x.paper_id, int(x.item_index), x.status, f, l))
        for p in range(f - 1, l): key.add((x.paper_id, p))
    Pdf['name_pred'] = [(a, b) in key for a, b in zip(Pdf.paper_id, Pdf.pos)]; mm['name_pred'] = [(a, b) in key for a, b in zip(mm.paper_id, mm.pos)]
    # gen-time argmax should equal the generated token (greedy) on valid positions
    cpm = dict(pd.read_csv(root / f'regen_papers_{K:03d}.csv')[['paper_id', 'common_prefix']].itertuples(index=False))
    vs = v & (Pdf.step.to_numpy() < Pdf.paper_id.map(cpm).to_numpy())          # strictly inside the identical prefix
    gen_self = float((Pdf.loc[vs, 'gen_argmax'] == Pdf.loc[vs, 'tok']).mean()) if vs.any() else None
    mmv = mm[mm.gen_valid]
    gen_gap = (mmv.gen_logit_tok - mmv.gen_top5_logit.map(lambda q: q[1] if len(q) > 1 else np.nan)) if len(mmv) else pd.Series(dtype=float)
    # per-name confidence
    idx = Pdf.set_index(['paper_id', 'pos'])
    nrows = []
    for pid, it, st, f, l in spans:
        ps = list(range(f - 1, l))
        try: s = idx.loc[[(pid, p) for p in ps]]
        except KeyError: continue
        if not s.gen_valid.all(): nrows.append(dict(paper_id=pid, item_index=it, status=st, gen_valid=False)); continue
        rec = dict(paper_id=pid, item_index=it, status=st, gen_valid=True, n_tok=len(ps), n_mismatch=int((s.rep_argmax != s.tok).sum()),
                   rep_lp_mean=float(s.rep_lp.mean()), gen_lp_mean=float(s.gen_lp.mean()), rep_lp_min=float(s.rep_lp.min()), gen_lp_min=float(s.gen_lp.min()),
                   rep_lp_first=float(s.rep_lp.iloc[0]), gen_lp_first=float(s.gen_lp.iloc[0]), rep_ent_pre=float(s.rep_ent.iloc[0]), gen_ent_pre=float(s.gen_ent.iloc[0]))
        nrows.append(rec)
    NM = pd.DataFrame(nrows); NV = NM[NM.gen_valid] if len(NM) else NM
    dl = {}
    for m in ('lp_mean', 'ent_pre', 'lp_min', 'lp_first'):
        if not len(NV): break
        a = (NV['rep_' + m] - NV['gen_' + m]).abs(); aff = NV.n_mismatch > 0
        dl[m] = dict(median=float(a.median()), max=float(a.max()), mean=float(a.mean()), share_gt_0p01=float((a > 0.01).mean()), share_gt_0=float((a > 0).mean()),
                     median_affected=float(a[aff].median()) if aff.any() else None, max_unaffected=float(a[~aff].max()) if (~aff).any() else None)
    # parity with the old replay (conf/shard_000.parquet) where available
    par_old = None
    fo = src / f'conf/shard_{K:03d}.parquet'
    if fo.exists() and len(NV):
        O = pd.read_parquet(fo).merge(NV, on=['paper_id', 'item_index'], suffixes=('_old', ''))
        if len(O): par_old = dict(n=len(O), max_abs_lp_mean=float((O.lp_mean - O.rep_lp_mean).abs().max()), max_abs_ent_pre=float((O.ent_pre - O.rep_ent_pre).abs().max()))
    within4 = float((mm.gap_ulps <= 4 + 1e-9).mean()) if len(mm) else 1.0
    allv = Pdf[v]
    res = dict(meta=meta, positions=len(Pdf), agreement=agree, old_gate_0p99=('OK' if agree >= OLD_GATE else 'WARN'), mismatches=n_mm,
               gen_argmax_eq_tok=gen_self, mismatch_gap_logit=dict(median=float(mm.rep_gap.median()) if len(mm) else None, max=float(mm.rep_gap.max()) if len(mm) else None,
                                                                  median_ulps=float(mm.gap_ulps.median()) if len(mm) else None, max_ulps=float(mm.gap_ulps.max()) if len(mm) else None,
                                                                  share_within_1ulp=float((mm.gap_ulps <= 1 + 1e-9).mean()) if len(mm) else None,
                                                                  share_within_2ulp=float((mm.gap_ulps <= 2 + 1e-9).mean()) if len(mm) else None,
                                                                  share_within_4ulp=within4, ulp_values=mm.ulp.value_counts().sort_index().to_dict() if len(mm) else {}),
               mismatch_gen_time_margin=dict(median=float(gen_gap.median()) if len(gen_gap) else None, max=float(gen_gap.max()) if len(gen_gap) else None, n=int(len(gen_gap))),
               gen_vs_rep_lp_all_positions=dict(median_abs=float((allv.rep_lp - allv.gen_lp).abs().median()) if len(allv) else None,
                                                p99_abs=float((allv.rep_lp - allv.gen_lp).abs().quantile(0.99)) if len(allv) else None,
                                                max_abs=float((allv.rep_lp - allv.gen_lp).abs().max()) if len(allv) else None,
                                                median_abs_logit=float((allv.rep_logit_tok - allv.gen_logit_tok).abs().median()) if len(allv) else None),
               concentration=dict(base_share_name_pred=float(Pdf.name_pred.mean()), mismatch_share_name_pred=float(mm.name_pred.mean()) if len(mm) else None,
                                  rate_name_pred=float((Pdf[Pdf.name_pred].rep_argmax != Pdf[Pdf.name_pred].tok).mean()) if Pdf.name_pred.any() else None,
                                  rate_other=float((Pdf[~Pdf.name_pred].rep_argmax != Pdf[~Pdf.name_pred].tok).mean()) if (~Pdf.name_pred).any() else None),
               names=dict(n=len(NM), n_gen_valid=int(len(NV)), share_affected=float((NV.n_mismatch > 0).mean()) if len(NV) else None, delta=dl),
               parity_old_replay=par_old)
    ok_ulps = within4 >= 0.95; ok_conf = bool(dl) and dl['lp_mean']['median'] < 0.01
    res['decision'] = dict(share_within_4ulp=within4, median_abs_d_lp_mean=dl.get('lp_mean', {}).get('median'),
                           rule='>=95% of mismatches within 4 bf16 ulps AND median |d name mean log-prob| < 0.01',
                           pass_ulps=ok_ulps, pass_conf=ok_conf,
                           verdict='WARN: replay probabilities usable' if (ok_ulps and ok_conf) else 'NOT MET: replay probabilities not shown equivalent')
    atomic(root / 'decision.json', lambda p: p.write_text(json.dumps(res, indent=1, default=float)))
    if len(NM): atomic(root / f'names_{K:03d}.parquet', lambda p: NM.to_parquet(p, index=False))
    atomic(root / 'mismatches.csv', lambda p: mm.drop(columns=[c for c in mm.columns if c.endswith('top5_id')]).to_csv(p, index=False))
    L = ['# C24 item 1a option A — shard 0 regeneration with saved logits + replay (POST-HOC, exploratory)', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `13_stage13/stage13_c24_regen_20261114.py`.', '', f'**Decision: {res["decision"]["verdict"]}**', '',
         '```', json.dumps(res, indent=1, default=float), '```', '']
    atomic(root / 'report.md', lambda p: p.write_text('\n'.join(L) + '\n')); log('decision', res['decision']); return res


def paper_table():
    _, d = B.load_papers(); return d.set_index('paper_id')


def gpu(a):
    import torch
    out = OUT; G.check_plan()
    if not (out / f'regen_{K:03d}.json').exists():
        d = paper_table(); s12 = B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t1 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model
        log(f'model load {time.perf_counter() - t1:.1f} s'); torch.cuda.reset_peak_memory_stats()
        run_shard(SRC, out, d, hf, tok, torch); log('peak GiB', torch.cuda.max_memory_allocated() / 2**30)
    else: log('regen output present: evaluate only')
    evaluate(out)


def tiny(a):
    """CPU, random 4-layer Qwen3-shaped model in bf16 (same config/seed as the runner tiny tests), 4 papers of real shard 0.
    (1) stored tokens are Qwen3-32B text -> regenerated tokens differ (regen check WARN, must not stop), only the common prefix is compared;
    (2) self-consistency: a copy of the shard whose stored gen_ids are the tiny model's own greedy output (max 24 tokens) and synthetic
        name spans -> regen identical share 1.0, mismatches evaluated, decision computed. Plus skip-if-done for gpu() style reuse."""
    import torch, transformers, pandas as pd
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); d = paper_table()
    s10 = B.load_mod(H / '12_stage12/371_stage12.py', 's12').s10; tok = s10.tokenizer()
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
    PP = pd.read_csv(SRC / 'papers/shard_000.csv'); N = pd.read_parquet(SRC / 'names/shard_000.parquet')
    keep = PP[PP.n_M + PP.n_H > 0].paper_id.head(4)
    s1 = out / 'real'; (s1 / 'papers').mkdir(parents=True, exist_ok=True); (s1 / 'names').mkdir(exist_ok=True)
    PP[PP.paper_id.isin(keep)].to_csv(s1 / 'papers/shard_000.csv', index=False); N[N.paper_id.isin(keep)].to_parquet(s1 / 'names/shard_000.parquet', index=False)
    m1 = run_shard(s1, s1 / 'o', d, hf, tok, torch, max_new=24); r1 = evaluate(s1 / 'o', src=s1)
    # (2) own-output copy
    s2 = out / 'own'; (s2 / 'papers').mkdir(parents=True, exist_ok=True); (s2 / 'names').mkdir(exist_ok=True)
    P2 = PP[PP.paper_id.isin(keep)].copy(); gens = []; nrows = []
    for r in P2.itertuples():
        pr = B.V1.chat_prompt(tok, d.loc[r.paper_id, 'title'], d.loc[r.paper_id, 'year']); pids = tok(pr, add_special_tokens=False).input_ids
        g = B.gen_one(hf, tok, torch, pids, B.LAYERS, None, max_new=24); gens.append(json.dumps(g['gen']))
        for j, f in enumerate(range(1, max(2, len(g['gen']) - 3), 5)):
            nrows.append(dict(paper_id=r.paper_id, item_index=j, status='M' if j % 2 else 'H', tok_first=float(len(pids) + f), tok_last=float(len(pids) + min(f + 2, len(g['gen']) - 1))))
    P2['gen_ids'] = gens; P2.to_csv(s2 / 'papers/shard_000.csv', index=False); pd.DataFrame(nrows).to_parquet(s2 / 'names/shard_000.parquet', index=False)
    m2 = run_shard(s2, s2 / 'o', d, hf, tok, torch, max_new=24); r2 = evaluate(s2 / 'o', src=s2)
    checks = {'real: regen mismatch -> WARN, no stop': m1['regen_check'] in ('OK', 'WARN'),
              'real: prompt lengths match stored n_prompt': m1['prompt_len_ok'],
              'real: gen-time argmax == generated token on valid positions': r1['gen_argmax_eq_tok'] in (None, 1.0),
              'own: regen identical share 1.0': m2['regen_identical_share'] == 1.0,
              'own: gen-time argmax == token (greedy)': r2['gen_argmax_eq_tok'] == 1.0,
              'own: names evaluated with deltas': r2['names']['n_gen_valid'] > 0 and 'lp_mean' in r2['names']['delta'],
              'own: decision computed': 'verdict' in r2['decision'],
              'old gate is WARN-only (field present, no exit)': r2['old_gate_0p99'] in ('OK', 'WARN')}
    for k_, v in checks.items(): print('C24 REGEN TINY CHECK', 'PASS' if v else 'FAIL', k_, flush=True)
    print('real', json.dumps(r1['decision'], default=float), '\nown', json.dumps({k: r2[k] for k in ('agreement', 'mismatches', 'mismatch_gap_logit', 'decision')}, default=float), flush=True)
    ok = all(checks.values()); print('C24 REGEN TINY', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['gpu', 'tiny', 'evaluate']); ap.add_argument('--out'); ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'evaluate': evaluate(Path(a.root) if a.root else OUT); return
    gpu(a)


if __name__ == '__main__':
    main()
