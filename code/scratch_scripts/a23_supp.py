#!/usr/bin/env python3
"""Exploratory supplement to addendum 23 (user approval 2026-11-22). NOT part of the locked test; the locked result
(391_groups/summary_a23/) stays as it is. Reuses the a23 freeze (582 test papers, 12 shards), prompts and class vocabularies
by importing a23_h1lock.py read-only.

stage 1 (all shards):
  (a) gentle knockout: from layer l the ":" query may attend to title tokens + sink positions + itself (question-word positions
      blocked); K_gentle(l) = share keeping the recipient's own format class (first-token class masses, as a23).
  (b) sink-only control: from layer l the ":" query may attend only to the sink positions + itself.
  (c) content-token baseline: greedy continuation (no KV cache, up to GEN_MAX tokens), first non-whitespace token -> class
      (year: digits; field: field vocabulary or a field label prefix; name: name vocabulary); per task.
  (d) shard 0 only: attention diagnostic — mean (over heads) attention of the ":" query to each key position, per layer, for the
      first DIAG papers under the authors prompt (eager attention), to confirm the sink set before the remaining shards.
stage 2 (only for year/field if the content baseline accuracy >= 0.90): gentle knockout + colon patching with the content
  measure.
Outputs: raw/a23_supp/shard_KKK.npz + .json ; summary_a23_supp/.
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
spec = importlib.util.spec_from_file_location('a23', H / '18_h1lock/a23_h1lock.py'); A = importlib.util.module_from_spec(spec)
sys.argv_backup = sys.argv; spec.loader.exec_module(A)
G = A.G; FREEZE = A.FREEZE
OUT = Path(os.environ.get('A23S_OUT', G / 'raw/a23_supp')); SUMMARY = Path(os.environ.get('A23S_SUMMARY', G / 'summary_a23_supp'))
LAYERS = A.LAYERS; KO = LAYERS + [A.KO_NONE]; TN = A.TN; CLASSES = A.CLASSES; CLASS_OF = A.CLASS_OF; PAIRS = A.PAIRS
SINK = [int(x) for x in os.environ.get('A23S_SINK', '0').split(',')]     # fixed after the shard-0 diagnostic
GEN_MAX = 4; DIAG = 5


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


class S(A.Ctx):
    def __init__(self, model=None, tok=None):
        super().__init__(model, tok)
        voc = json.load(open(FREEZE / 'vocab.json')); self.vset = {c: set(voc[c]) for c in CLASSES}
        fr = json.load(open(FREEZE / 'freeze.json')); self.field_words = [w.strip().lower() for w in fr.get('field_tokens', [])]
        import pandas as pd
        self.labels = sorted({str(f).lower() for f in pd.read_parquet(A.J / '351_stage10/cohort/papers.parquet', columns=['field']).field.unique()})

    def content_class(self, tid):
        s = self.tok.decode([tid]); st = s.strip()
        if st and st[0].isdigit(): return 1
        if tid in self.vset['field'] or any(lab.startswith(st.lower()) and len(st) >= 3 for lab in self.labels): return 2
        if tid in self.vset['name']: return 0
        return -1                                      # other

    def gen_first_content(self, ids, batch, patch=None, mask_builder=None):
        """greedy continuation without cache for `batch` copies (each copy its own intervention); returns first content token
        id per copy (-1 if none within GEN_MAX)."""
        torch = self.torch; cur = [list(ids) for _ in range(batch)]; first = [-1] * batch; T0 = len(ids)
        for step in range(GEN_MAX):
            T = T0 + step; mfn = mask_builder(T) if mask_builder else None
            # all copies share length T (greedy appends one token each step)
            lg = self._fwd_rows(cur, patch, mfn)
            nxt = lg.argmax(-1).tolist()
            for i, t in enumerate(nxt):
                if first[i] == -1 and self.tok.decode([t]).strip() != '': first[i] = t
                cur[i].append(t)
            if all(f != -1 for f in first): break
        return first

    def _fwd_rows(self, rows, patch, mfn):
        torch = self.torch; model = self.model; hs = []; last = len(model.layers) - 1
        x = torch.tensor(rows, device=model.input_device)
        try:
            for l, items in (patch or {}).items():
                def hook(mod, inp, out, items=items):
                    h = out if torch.is_tensor(out) else out[0]
                    for e, p, t in items: h[e, p] = t.to(h.device, h.dtype)
                    return out
                hs.append(model.layers[l].register_forward_hook(hook))
            if mfn is not None:
                for l in range(len(model.layers)):
                    def pre(mod, args, kwargs, l=l):
                        mk = mfn(l)
                        if mk is not None: kwargs['attention_mask'] = mk.to(next(mod.parameters()).device)
                        return args, kwargs
                    hs.append(model.layers[l].register_forward_pre_hook(pre, with_kwargs=True))
            from jlens.hooks import ActivationRecorder
            with torch.inference_mode(), ActivationRecorder(model.layers, at=[last]) as rec:
                model.forward(x)
                return model.unembed(rec.activations[last][:, -1].float()).float()
        finally:
            for h in hs: h.remove()

    def attn_diag(self, ids, colon):
        """mean-over-heads attention of the colon query to every key, per layer (eager attention)."""
        torch = self.torch; hf = self.model._hf_model; old = hf.config._attn_implementation
        try:
            try: hf.set_attn_implementation('eager')
            except Exception: hf.config._attn_implementation = 'eager'
            with torch.inference_mode():
                o = hf(input_ids=torch.tensor([ids], device=self.model.input_device), output_attentions=True)
            return np.stack([a[0, :, colon, :].float().mean(0).cpu().numpy() for a in o.attentions])   # [L, T]
        finally:
            try: hf.set_attn_implementation(old)
            except Exception: hf.config._attn_implementation = old


def do_shard(C, k, stage, tasks2):
    rows = C.D[C.D.shard == k]; dtype = next(C.model.layers[0].parameters()).dtype
    out = dict(paper_id=[], kg=[], ks=[], cbase=[], diag=[])
    if stage == 2: out.update(kg_c=[], pm_c=[])
    for n, r in enumerate(rows.itertuples()):
        P = {t: A.build(C.tok, r.title, t) for t in TN}
        kg = np.zeros((3, len(KO), 3)); ks = np.zeros((3, len(KO), 3)); cb = np.zeros(3, int)
        for qi, q in enumerate(TN):
            ids, tpos, colon = P[q]; T = len(ids); sink = [s for s in SINK if s < colon]
            keep_g = sorted(set(tpos) | set(sink) | {colon}); keep_s = sorted(set(sink) | {colon})
            kg[qi] = C.masses(C.forward(ids, len(KO), mask_fn=C.ko_mask(T, colon, keep_g, KO, dtype))[0])
            ks[qi] = C.masses(C.forward(ids, len(KO), mask_fn=C.ko_mask(T, colon, keep_s, KO, dtype))[0])
            cb[qi] = C.content_class(C.gen_first_content(ids, 1)[0])
        out['paper_id'].append(r.paper_id); out['kg'].append(kg); out['ks'].append(ks); out['cbase'].append(cb)
        if k == 0 and n < DIAG:
            ids, _, colon = P['authors']
            try:
                ad = C.attn_diag(ids, colon)[:, :40]; pad = np.full((ad.shape[0], 40), np.nan); pad[:, :ad.shape[1]] = ad
                out['diag'].append(pad)
            except Exception as e: log('WARN attn diag failed', repr(e)); out['diag'].append(np.full((len(C.model.layers), 40), np.nan))
        if stage == 2:
            kgc = np.full((3, len(KO)), -9, int); pmc = np.full((len(PAIRS), len(LAYERS)), -9, int)
            res = {}
            for t in TN: res[t] = C.forward(P[t][0], 1, record=LAYERS)[1]
            for qi, q in enumerate(TN):
                if q not in tasks2: continue
                ids, tpos, colon = P[q]; sink = [s for s in SINK if s < colon]; keep_g = sorted(set(tpos) | set(sink) | {colon})
                mb = lambda T, ids=ids, colon=colon, keep_g=keep_g: C.ko_mask(T, colon, keep_g, KO, dtype)
                kgc[qi] = [C.content_class(t) for t in C.gen_first_content(ids, len(KO), mask_builder=mb)]
            for j, (q, d) in enumerate(PAIRS):
                if q not in tasks2 and d not in tasks2: continue
                ids, _, colon = P[q]; patch = {l: [(i, colon, res[d][l])] for i, l in enumerate(LAYERS)}
                pmc[j] = [C.content_class(t) for t in C.gen_first_content(ids, len(LAYERS), patch=patch)]
            out['kg_c'].append(kgc); out['pm_c'].append(pmc)
    d = {kk: np.array(v) for kk, v in out.items() if len(v)}
    return d | dict(ko_layers=np.array(KO), layers=np.array(LAYERS), tasks=np.array(TN), sink=np.array(SINK), pairs=np.array([f'{q}>{d_}' for q, d_ in PAIRS]))


def work(a):
    A.check_lock(); od = OUT / f'stage{a.stage}'; od.mkdir(parents=True, exist_ok=True); t0 = time.time(); C = None
    tasks2 = [t for t in a.tasks2.split(',') if t]
    for k in [int(x) for x in a.shards.split(',')]:
        if (od / f'shard_{k:03d}.json').exists(): log(f'shard {k} skip (exists)'); continue
        if (time.time() - t0) / 60 > a.max_minutes: log('time budget reached before shard', k); break
        if C is None: C = S(); log('model loaded', C.env['gpu'], f'{(time.time() - t0) / 60:.1f} min')
        t1 = time.time(); d = do_shard(C, k, a.stage, tasks2)
        tmp = od / f'shard_{k:03d}.tmp{os.getpid()}.npz'; np.savez(tmp, **d); os.replace(tmp, od / f'shard_{k:03d}.npz')
        meta = dict(shard=k, stage=a.stage, papers=len(d['paper_id']), seconds=time.time() - t1, sink=SINK, env=C.env,
                    content_base_acc={t: float(np.mean(d['cbase'][:, i] == CLASS_OF[t])) for i, t in enumerate(TN)},
                    K_gentle_none_eq_own=float(np.mean([np.argmax(d['kg'][p, i, -1]) == CLASS_OF[t] for p in range(len(d['paper_id'])) for i, t in enumerate(TN)])))
        if 'diag' in d:
            dg = np.nanmean(d['diag'], 0)                      # [L, 40]
            meta['diag_mean_attn_pos0_by_layer'] = [float(x) for x in dg[:, 0]]
            meta['diag_top_positions_L24_L40'] = {int(l): np.argsort(-dg[l])[:4].tolist() for l in (8, 24, 32, 40, 48) if l < dg.shape[0]}
        json.dump(meta, open(od / f'shard_{k:03d}.json', 'w'), indent=1); log(f'shard {k} done', json.dumps(meta)[:900])


def tiny(a):
    import torch, transformers, jlens, tempfile
    global OUT
    S11 = A.s11(); s10 = S11.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    global LAYERS, KO
    LAYERS = [0, 1]; KO = LAYERS + [A.KO_NONE]; A.LAYERS = LAYERS
    C = S(model, tok); C.D = C.D[C.D.shard == 0].head(2).copy(); OUT = Path(tempfile.mkdtemp())
    ok = []
    def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)
    d1 = do_shard(C, 0, 1, []); check('stage1 shapes', d1['kg'].shape == (2, 3, 3, 3) and d1['ks'].shape == (2, 3, 3, 3), str(d1['kg'].shape))
    check('cbase classes', set(np.unique(d1['cbase']).tolist()) <= {-1, 0, 1, 2})
    check('diag present', 'diag' in d1 and d1['diag'].shape[0] == 2, str(d1.get('diag', np.zeros(0)).shape))
    check('nothing blocked == base first-token class',
          all(np.argmax(d1['kg'][p, i, -1]) == np.argmax(C.masses(C.forward(A.build(tok, C.D.iloc[p].title, t)[0], 1)[0])[0]) for p in range(2) for i, t in enumerate(TN)))
    d2 = do_shard(C, 0, 2, ['year', 'field']); check('stage2 shapes', d2['kg_c'].shape == (2, 3, 3) and d2['pm_c'].shape == (2, 6, 2), str(d2['kg_c'].shape))
    check('stage2 authors-only rows skipped', bool((d2['kg_c'][:, 0] == -9).all()))
    print(f'TINY {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)


def analyze(a):
    import pandas as pd
    fr = json.load(open(FREEZE / 'freeze.json')); od1 = OUT / 'stage1'
    miss = [k for k in fr['shards'] if not (od1 / f'shard_{k:03d}.json').exists()]
    if miss and not a.allow_missing: raise SystemExit(f'missing stage1 shards {miss}')
    ds = [np.load(od1 / f'shard_{k:03d}.npz') for k in fr['shards'] if (od1 / f'shard_{k:03d}.npz').exists()]
    pid = np.concatenate([d['paper_id'] for d in ds]); kg = np.concatenate([d['kg'] for d in ds]); ks = np.concatenate([d['ks'] for d in ds])
    cb = np.concatenate([d['cbase'] for d in ds])
    D = pd.read_parquet(FREEZE / 'freeze.parquet').set_index('paper_id').loc[pid]
    codes, uniq = pd.factorize(D.team.to_numpy())
    W = np.random.default_rng(A.SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=A.NB).astype(float)[:, codes]
    def mci(x, sel=None):
        x = x.astype(float) if sel is None else np.where(sel, x, np.nan).astype(float)
        ok = np.isfinite(x); w = W[:, ok]; v = x[ok]; b = (w @ v) / w.sum(1)
        return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    tgt = (D.group == 'target').to_numpy(); rows = []
    for i, t in enumerate(TN):
        e = mci(cb[:, i] == CLASS_OF[t]); rows.append(dict(kind='content_baseline_acc', task=t, layer='', est=e[0], lo=e[1], hi=e[2]))
        for li, l in enumerate(KO):
            for nm, arr in (('K_gentle', kg), ('K_sink_only', ks)):
                keep = np.argmax(arr[:, i, li], -1) == CLASS_OF[t]; e = mci(keep); et = mci(keep, tgt); ec = mci(keep, ~tgt)
                rows.append(dict(kind=nm, task=t, layer=l, est=e[0], lo=e[1], hi=e[2], target=et[0], target_lo=et[1], target_hi=et[2],
                                 control=ec[0], control_lo=ec[1], control_hi=ec[2]))
    od2 = OUT / 'stage2'
    if od2.exists() and any(od2.glob('shard_*.npz')):
        d2 = [np.load(f) for f in sorted(od2.glob('shard_*.npz'))]; p2 = np.concatenate([d['paper_id'] for d in d2])
        kgc = np.concatenate([d['kg_c'] for d in d2]); pmc = np.concatenate([d['pm_c'] for d in d2])
        idx = pd.Index(pid).get_indexer(p2); Wsave = W
        for i, t in enumerate(TN):
            if (kgc[:, i] == -9).all(): continue
            for li, l in enumerate(KO):
                keep = kgc[:, i, li] == CLASS_OF[t]; v = keep.astype(float); w = Wsave[:, idx]; b = (w @ v) / w.sum(1)
                rows.append(dict(kind='K_gentle_content', task=t, layer=l, est=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5))))
        for j, (q, d_) in enumerate(PAIRS):
            if (pmc[:, j] == -9).all(): continue
            for li, l in enumerate(LAYERS):
                sw = pmc[:, j, li] == CLASS_OF[d_]; v = sw.astype(float); w = Wsave[:, idx]; b = (w @ v) / w.sum(1)
                rows.append(dict(kind='S_switch_content', task=f'{q}>{d_}', layer=l, est=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5))))
    SUMMARY.mkdir(parents=True, exist_ok=True); T = pd.DataFrame(rows); T.to_csv(SUMMARY / 'a23_supp_table.csv', index=False)
    meta = [json.load(open(od1 / f'shard_{k:03d}.json')) for k in fr['shards'] if (od1 / f'shard_{k:03d}.json').exists()]
    res = dict(label='exploratory supplement to addendum 23 (post hoc; locked result unchanged)', n=len(pid), by_group=D.group.value_counts().to_dict(),
               sink=SINK, diag=meta[0].get('diag_mean_attn_pos0_by_layer'), diag_top=meta[0].get('diag_top_positions_L24_L40'), missing=miss)
    json.dump(res, open(SUMMARY / 'a23_supp_results.json', 'w'), indent=1, default=str)
    (SUMMARY / 'report.md').write_text('# Exploratory supplement to addendum 23\n\n' + json.dumps(res, default=str) + '\n\n' + T.to_string(index=False, float_format=lambda v: f'{v:.3f}') + '\n')
    print(T.to_string())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['tiny', 'work', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--stage', type=int, default=1); ap.add_argument('--tasks2', default='')
    ap.add_argument('--max-minutes', type=float, default=36); ap.add_argument('--allow-missing', action='store_true'); a = ap.parse_args()
    {'tiny': tiny, 'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
