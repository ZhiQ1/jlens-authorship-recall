"""Stage 11 E1 same-batch no-replacement baseline (handbook V47 / U37; user-approved 2026-11-05).

E1 (361_stage11.do_patch) compares the patched false runs - ONE batch of len(PATCH_LAYERS)=15 elements - with a
batch-1 false run. Batched bf16 GEMMs round differently from batch 1, so part of 'patched - false' is rounding noise.
As in X4 (pscope '@none') and Stage 12 P1/P2 ('none'), this re-runs E1 on a sample of shards with ONE extra element in
the same batch that gets NO replacement (element 15 of a batch of 16): its score is the same-batch false baseline.
Everything else is the Stage 11 code itself (record / run_final / ranks, the same tails and prompts).
Stored per name token: row_id, rank_true, rank_false (batch 1), rank_patch [15 layers], rank_none (same batch, unpatched).
Checks (WARN only): true / false / patched ranks vs stored raw/patch (share equal; patched ranks can differ because the
batch is 16 instead of 15); L63 element == true.
Commands: run [--shards 0,4,...] (GPU) | tiny --root DIR (CPU, tiny model) | analyze [--raw DIR]
Output: 361_stage11/raw/e1_noise/shard_kkk.npz, reports/e1_batch_noise.md, summary/e1_batch_noise.csv"""
import argparse, importlib.util, inspect, json, os, sys, textwrap, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('s11', H / '11_stage11/361_stage11.py'); s11 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s11)
s10 = s11.s10; R11 = Path('/scratch/zhang.zhiqi2/jlens/361_stage11')
SHARDS = [0, 4, 8, 12, 16, 20]
NB = 2000


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def do_patch_none(C, shard):
    """361_stage11.do_patch with one unpatched element appended to the patched batch."""
    torch = C.torch; rows, out_t, out_f, out_p, out_n = [], [], [], [], []
    PL = s11.PATCH_LAYERS; pf = C.prompts[s11.FALSE_FOR_PATCH]
    for r in C.smp[C.smp.shard == shard].itertuples():
        pt = json.loads(C.P.loc[r.paper_id].prompt_ids); pfi = pf[r.paper_id][1]
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; tail = r.tail_prompt + len(name) - 1
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = s11.record(C, T, PL)
            lt = s11.run_final(C, T, posT)[0]; lf = s11.run_final(C, F, posF)[0]
            patch = {}
            for i, l in enumerate(PL): patch.setdefault(l, []).append((i, tail, acts[l][-tail:]))
            lp = s11.run_final(C, F, posF, patch=patch, batch=len(PL) + 1)          # element len(PL): no replacement
            rows += rids; out_t.append(s11.ranks(lt, gold, torch)); out_f.append(s11.ranks(lf, gold, torch))
            out_p.append(np.stack([s11.ranks(lp[i], gold, torch) for i in range(len(PL))], 1)); out_n.append(s11.ranks(lp[len(PL)], gold, torch))
    return dict(row_id=np.array(rows), rank_true=np.concatenate(out_t), rank_false=np.concatenate(out_f),
                rank_patch=np.concatenate(out_p), rank_none=np.concatenate(out_n), layers=np.array(PL))


def check(d, k, ref_dir):
    f = ref_dir / f'shard_{k:03d}.npz'
    if not f.exists(): return dict(shard=k, status='WARN', note='no stored E1 shard')
    z = np.load(f); same = len(z['row_id']) == len(d['row_id']) and bool((z['row_id'] == d['row_id']).all())
    rep = dict(shard=k, rows=len(d['row_id']), rows_match=same)
    if same:
        nl = lambda x: -np.log10(np.asarray(x, float))
        for c in ('rank_true', 'rank_false', 'rank_patch'):
            rep[c + '_equal'] = float((z[c] == d[c]).mean()); rep[c + '_mean_abs_dnlr'] = float(np.abs(nl(z[c]) - nl(d[c])).mean())
        i63 = list(d['layers']).index(63) if 63 in list(d['layers']) else None
        if i63 is not None: rep['L63_equals_true'] = float((d['rank_patch'][:, i63] == d['rank_true']).mean())
        rep['none_equals_false_b1'] = float((d['rank_none'] == d['rank_false']).mean())
        rep['none_mean_abs_dnlr_vs_false_b1'] = float(np.abs(nl(d['rank_none']) - nl(d['rank_false'])).mean())
    rep['status'] = 'PASS' if same and rep.get('rank_true_equal', 0) >= 0.95 and rep.get('rank_false_equal', 0) >= 0.95 else 'WARN'
    return rep


def run(C, shards, root):
    for k in shards:
        f = root / f'raw/e1_noise/shard_{k:03d}.npz'
        if f.exists(): log('skip (exists)', f); continue
        t0 = time.monotonic(); d = do_patch_none(C, k)
        try: rep = check(d, k, R11 / 'raw/patch')
        except Exception as e: rep = dict(shard=k, status='WARN', note=repr(e))
        f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
        np.savez(tmp, meta=np.array(json.dumps(dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=rep, script_sha256=s10.sha_file(__file__), **getattr(C, 'env', {})))), **d)
        os.replace(tmp, f)
        try:
            (root / 'logs').mkdir(parents=True, exist_ok=True)
            with open(root / 'logs/e1_noise_check.jsonl', 'a') as fh: fh.write(json.dumps(rep) + '\n')
            log(f'e1_noise shard {k:03d} rows={len(d["row_id"])} {time.monotonic() - t0:.0f}s check', json.dumps(rep))
        except Exception as e: print('log warning', repr(e), flush=True)


class GCtx:
    """model + data only (no lenses: E1 needs none)."""
    def __init__(self):
        import torch, pandas as pd
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(s11.R10, self.papers, s11.FALSE_FOR_PATCH)[0]}
        self.smp = pd.read_parquet(R11 / 'config/sample.parquet'); self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])


def tiny(root):
    import torch, transformers, jlens, pandas as pd
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    src = textwrap.dedent(inspect.getsource(s11.run_final)).replace('at=[63]', 'at=[len(model.layers) - 1]').replace('activations[63]', 'activations[len(model.layers) - 1]')
    ns = dict(vars(s11)); exec(src, ns); s11.run_final = ns['run_final']; s11.PATCH_LAYERS = [0, 1]
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(s11.R10, C.papers, s11.FALSE_FOR_PATCH)[0]}
    smp = pd.read_parquet(R11 / 'config/sample.parquet'); C.smp = pd.concat([smp[smp.shard == k].head(2) for k in (0, 4)]); C.env = {'tiny': True}
    run(C, [0, 4], root)
    z = np.load(root / 'raw/e1_noise/shard_000.npz')
    # tiny fp32 on CPU: last layer (1) patch must equal true, the unpatched element must equal the batch-1 false run
    ok = (z['rank_patch'][:, -1] == z['rank_true']).all() and (z['rank_none'] == z['rank_false']).all() and z['rank_patch'].shape[1] == 2
    print('TINY', 'PASS' if ok else 'FAIL', {k: z[k].shape for k in z.files}); sys.exit(0 if ok else 1)


def analyze(raw, out_csv, rep_md):
    import pandas as pd
    zs = [np.load(f) for f in sorted(Path(raw).glob('shard_*.npz'))]; layers = [int(x) for x in zs[0]['layers']]
    d = {k: np.concatenate([z[k] for z in zs]) for k in ('row_id', 'rank_true', 'rank_false', 'rank_patch', 'rank_none')}
    checks = [json.loads(str(z['meta']))['check'] for z in zs]
    nl = lambda x: -np.log10(np.asarray(x, float))
    toks = pd.read_parquet(s11.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group']]
    df = pd.DataFrame({'paper_id': toks.loc[d['row_id']].paper_id.to_numpy(), 'true': nl(d['rank_true']), 'f1': nl(d['rank_false']), 'fn': nl(d['rank_none'])})
    for i, l in enumerate(layers): df[f'p{l}'] = nl(d['rank_patch'][:, i])
    # stored E1 (batch of 15) on the same rows, for the published recovery
    old = {}
    for z in zs:
        k = json.loads(str(z['meta']))['check']['shard']; o = np.load(R11 / f'raw/patch/shard_{k:03d}.npz')
        if len(o['row_id']) == len(z['row_id']) and (o['row_id'] == z['row_id']).all():
            for i, l in enumerate(layers): old.setdefault(l, []).append(nl(o['rank_patch'][:, i]))
    for l in old: df[f'o{l}'] = np.concatenate(old[l]) if len(np.concatenate(old[l])) == len(df) else np.nan
    pp = df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    rng = np.random.default_rng(47); rows = []
    tok_noise = dict(tokens=len(df), papers=len(pp), none_eq_f1=float((d['rank_none'] == d['rank_false']).mean()),
                     tok_mean_abs=float(np.abs(df.fn - df.f1).mean()), tok_mean=float((df.fn - df.f1).mean()), tok_max_abs=float(np.abs(df.fn - df.f1).max()),
                     paper_mean_abs=float(np.abs(pp.fn - pp.f1).mean()), paper_max_abs=float(np.abs(pp.fn - pp.f1).max()))
    for g in ('all', 'target', 'control'):
        s = pp if g == 'all' else pp[pp.group == g]; n = len(s); ix = rng.integers(0, n, (NB, n))
        T, F1, FN = (s[c].to_numpy() for c in ('true', 'f1', 'fn'))
        nb = (FN - F1); r = dict(group=g, layer=-1, n=n, none_minus_false_b1=nb.mean(), lo=np.percentile(nb[ix].mean(1), 2.5), hi=np.percentile(nb[ix].mean(1), 97.5),
                                 true_minus_false=(T - F1).mean(), noise_share_of_gap=nb.mean() / (T - F1).mean()); rows.append(r)
        for l in layers:
            P = s[f'p{l}'].to_numpy(); r1 = (P - F1).mean() / (T - F1).mean(); rn = (P - FN).mean() / (T - FN).mean()
            b1 = (P - F1)[ix].mean(1) / (T - F1)[ix].mean(1); bn = (P - FN)[ix].mean(1) / (T - FN)[ix].mean(1)
            ro = ((s[f'o{l}'] - s.f1).mean() / (T - F1).mean()) if f'o{l}' in s else np.nan
            rows.append(dict(group=g, layer=l, n=n, rec_false_b1=r1, rec_false_b1_lo=np.percentile(b1, 2.5), rec_false_b1_hi=np.percentile(b1, 97.5),
                             rec_same_batch=rn, rec_same_batch_lo=np.percentile(bn, 2.5), rec_same_batch_hi=np.percentile(bn, 97.5),
                             diff=rn - r1, diff_lo=np.percentile(bn - b1, 2.5), diff_hi=np.percentile(bn - b1, 97.5), rec_stored_E1_b15=ro))
    R = pd.DataFrame(rows); Path(out_csv).parent.mkdir(parents=True, exist_ok=True); R.to_csv(out_csv, index=False)
    fm = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    L = ['# Stage 11 E1: same-batch no-replacement baseline (bf16 batch-rounding noise)', '',
         'Handbook V47 / U37 (user 2026-10-30: write "about 0.01, far below the main effect", re-measure the X4 way when a GPU is free; approved 2026-11-05). '
         'Script `11_stage11/stage11_e1_batchnoise.py` (imports `361_stage11.py` by path; E1 code unchanged except one extra batch element without replacement, so the batch is 16 instead of 15). '
         f'Sample: Stage 11 shards {sorted({c["shard"] for c in checks})} ({tok_noise["papers"]} papers, {tok_noise["tokens"]} name tokens). '
         'Not pre-registered (quality check; the recovery definition is Stage 11 E1 unchanged). Paper bootstrap 2,000 draws (seed 47), as stage11_analyze.', '',
         '## Checks (WARN only)', '']
    for c in checks: L.append('- ' + json.dumps(c))
    L += ['', '## Noise of the false baseline', '',
          f'- Same-batch unpatched element vs batch-1 false run: identical rank for {tok_noise["none_eq_f1"]:.1%} of tokens; per token mean |d log10 rank| {tok_noise["tok_mean_abs"]:.4f} (signed {tok_noise["tok_mean"]:+.4f}, max {tok_noise["tok_max_abs"]:.3f}); per paper mean |d| {tok_noise["paper_mean_abs"]:.4f} (max {tok_noise["paper_max_abs"]:.3f}).', '',
          '| group | n papers | same-batch none - batch-1 false [CI] | true - false | share of the true - false gap |', '|---|---|---|---|---|']
    for r in R[R.layer == -1].itertuples(): L.append(f'| {r.group} | {r.n} | {fm(r.none_minus_false_b1, r.lo, r.hi)} | {r.true_minus_false:+.3f} | {r.noise_share_of_gap:+.3f} |')
    L += ['', '## E1 recovery with either baseline', '', 'recovery(l) = mean(patched - false) / mean(true - false), paper means. "batch-1" = as published; "same batch" = unpatched element of the same batch as false. Stored = the published E1 shards (batch 15) on the same rows with the batch-1 false.', '',
          '| layer | group | recovery, batch-1 false [CI] | recovery, same-batch false [CI] | same-batch - batch-1 [CI] | stored E1 (b15) |', '|---|---|---|---|---|---|']
    for l in layers:
        for r in R[(R.layer == l)].itertuples():
            L.append(f'| L{l} | {r.group} | {fm(r.rec_false_b1, r.rec_false_b1_lo, r.rec_false_b1_hi)} | {fm(r.rec_same_batch, r.rec_same_batch_lo, r.rec_same_batch_hi)} | {fm(r.diff, r.diff_lo, r.diff_hi)} | {r.rec_stored_E1_b15:+.3f} |')
    a = R[(R.layer >= 0) & (R.group == 'all')]
    L += ['', '## Summary', '', f'- Largest |same-batch - batch-1| recovery difference over layers (all papers): {a["diff"].abs().max():.4f} (at L{int(a.loc[a["diff"].abs().idxmax(), "layer"])}); median {a["diff"].abs().median():.4f}.', '',
          '<!--CONCLUSION-->', '']
    Path(rep_md).parent.mkdir(parents=True, exist_ok=True); Path(rep_md).write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['run', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--root'); ap.add_argument('--raw')
    a = ap.parse_args(); root = Path(a.root) if a.root else R11
    if a.cmd == 'tiny': assert a.root; tiny(root)
    elif a.cmd == 'run': run(GCtx(), [int(x) for x in a.shards.split(',')] if a.shards else SHARDS, root)
    else:
        raw = Path(a.raw) if a.raw else root / 'raw/e1_noise'
        analyze(raw, root / 'summary/e1_batch_noise.csv', root / 'reports/e1_batch_noise.md')


if __name__ == '__main__':
    main()
