#!/usr/bin/env python3
"""Addendum 23 (LOCKED 2026-11-22, 391_groups/config/prereg_addendum23.md): H1 format-locking layer at the ':' position.

freeze  (CPU) sample = 582 X1/M3 test papers (381_stage13/config/pairs.parquet split=test), shards of 50; format-class
        vocabularies (name / year / field, disjoint) -> raw/a23_freeze/{freeze.parquet, vocab.json, freeze.json}
tiny    (CPU) whole work pipeline on a random 2-layer Qwen3 (real tokenizer) for 3 papers + checks + skip-if-done
work    (GPU) per shard: base outputs (3 questions), colon patching (6 ordered pairs x layers), knockouts (primary isolated
        colon, secondary question positions) -> raw/a23/shard_KKK.npz (+ .json marker written last)
analyze (CPU) S(l), dF(l), K(l), K2(l) with team bootstrap (2,000, seed 23), decision table -> summary_a23/
Frozen Stage 10/11/13 scripts are imported by path and never edited.
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'
ADD = G / 'config/prereg_addendum23.md'; ADD_SHA = '34f7ea1e48d28cdf85853c5c1d61cfe4a8b234b578836df6f8f723eb31704b96'
FREEZE = Path(os.environ.get('A23_FREEZE', G / 'raw/a23_freeze')); OUT = Path(os.environ.get('A23_OUT', G / 'raw/a23'))
SUMMARY = Path(os.environ.get('A23_SUMMARY', G / 'summary_a23'))
LAYERS = [4, 8, 16, 24, 32, 40, 48, 56]; KO_NONE = 64; SHARD = 50; NB = 2000; SEED = 23
TASKS = {'authors': 'Who are the authors of the paper titled "{t}"?\nAuthors:',
         'year': 'In what year was the research paper titled "{t}" published?\nYear:',
         'field': 'In what research field is the paper titled "{t}"?\nField:'}
TN = list(TASKS); CLASS_OF = {'authors': 0, 'year': 1, 'field': 2}; CLASSES = ['name', 'year', 'field']
PAIRS = [(q, d) for q in TN for d in TN if q != d]


def _load(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sys.modules[n] = m; sp.loader.exec_module(m); return m


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def check_lock():
    h = hashlib.sha256(ADD.read_bytes()).hexdigest()
    if h != ADD_SHA: raise SystemExit(f'addendum 23 changed: {h}')


def s11(): return _load(H / '11_stage11/361_stage11.py', 's11_frozen_a23')


def build(tok, title, task):
    """prompt ids, title token positions, colon index (as 381_stage13.build, without answer)."""
    prompt = TASKS[task].format(t=title); e = tok(prompt, return_offsets_mapping=True); ids = list(e.input_ids)
    a = prompt.index('titled "') + len('titled "'); b = a + len(title)
    tpos = [i for i, (x, y) in enumerate(e.offset_mapping) if x < b and y > a]
    colon = len(ids) - 1
    if not tpos or tok.decode(ids[colon:]).strip() != ':': raise ValueError('prompt layout')
    return ids, tpos, colon


# ------------------------------------------------------------------ freeze (CPU)
def freeze(a):
    import pandas as pd
    check_lock()
    if (FREEZE / 'freeze.json').exists() and not a.force: raise SystemExit(f'{FREEZE} exists')
    S = s11(); s10 = S.s10; tok = s10.tokenizer(); papers, toks = S.cohort(); ctx = S.contexts_of(toks)
    pr = pd.read_parquet(J / '381_stage13/config/pairs.parquet')
    smp = pr[pr.split == 'test'][['paper_id', 'group', 'team']].merge(papers[['paper_id', 'title', 'field', 'citation_bin']], on='paper_id')
    smp = smp.sort_values('paper_id').reset_index(drop=True); smp['shard'] = np.arange(len(smp)) // SHARD
    for r in smp.itertuples():
        for t in TN: build(tok, r.title, t)
    name = {v[2][0] for vs in ctx.values() for v in vs}
    year = {220} | {tok.convert_tokens_to_ids(str(d)) for d in range(10)}
    field = set()
    for f in papers.field.unique():
        for w in {f, f.capitalize(), f.title()}:
            for s in (w, ' ' + w): field.add(tok.encode(s, add_special_tokens=False)[0])
    # D23-1 (recorded 2026-11-22 before any real-model data): prereg section 3 lists the bare space token 220 explicitly as a
    # year token; it also starts 2 of 33,811 cohort name contexts (a Chinese name, a digit), so the generic overlap rule
    # would delete it from the year class. The explicit listing takes precedence: 220 stays in year, is dropped from name.
    name.discard(220)
    over = (name & year) | (name & field) | (year & field)
    voc = {'name': sorted(name - over), 'year': sorted(year - over), 'field': sorted(field - over)}
    assert not (set(voc['name']) & set(voc['year']) or set(voc['name']) & set(voc['field']) or set(voc['year']) & set(voc['field']))
    FREEZE.mkdir(parents=True, exist_ok=True); smp.to_parquet(FREEZE / 'freeze.parquet', index=False)
    json.dump(voc, open(FREEZE / 'vocab.json', 'w'))
    info = dict(n=len(smp), by_group=smp.group.value_counts().to_dict(), shards=sorted(smp.shard.unique().tolist()),
                vocab_sizes={k: len(v) for k, v in voc.items()}, removed_overlap=len(over), addendum_sha256=ADD_SHA,
                field_tokens=[tok.decode([i]) for i in voc['field']], year_tokens=[tok.decode([i]) for i in voc['year']])
    json.dump(info, open(FREEZE / 'freeze.json', 'w'), indent=1); log('FREEZE', json.dumps(info)[:600])


# ------------------------------------------------------------------ GPU work
class Ctx:
    def __init__(self, model=None, tok=None):
        import torch; self.torch = torch
        S = s11(); self.s10 = S.s10
        if model is None: model, tok = S.s10.load_model()
        self.model, self.tok = model, tok
        self.D = __import__('pandas').read_parquet(FREEZE / 'freeze.parquet'); voc = json.load(open(FREEZE / 'vocab.json'))
        dev = model.input_device; self.cls = [torch.tensor(voc[c], device=dev) for c in CLASSES]
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
                        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), addendum_sha256=ADD_SHA)

    def n_layers(self): return len(self.model.layers)

    def forward(self, ids, batch, patch=None, mask_fn=None, record=None):
        """batch copies of ids; patch {layer: [(element, pos, tensor[d])]}; mask_fn(layer)->[B,1,T,T] additive or None;
        record: list of layers -> returns (logits_last [B,V], {l: resid_last [d]} from element 0)."""
        torch = self.torch; model = self.model; hs = []; last = len(model.layers) - 1; rec_l = sorted(set((record or []) + [last]))
        x = torch.tensor([ids] * batch, device=model.input_device)
        try:
            for l, items in (patch or {}).items():
                def hook(mod, inp, out, items=items):
                    h = out if torch.is_tensor(out) else out[0]
                    for e, p, t in items: h[e, p] = t.to(h.device, h.dtype)
                    return out
                hs.append(model.layers[l].register_forward_hook(hook))
            if mask_fn is not None:
                for l in range(len(model.layers)):
                    def pre(mod, args, kwargs, l=l):
                        mk = mask_fn(l)
                        if mk is not None: kwargs['attention_mask'] = mk.to(next(mod.parameters()).device)
                        return args, kwargs
                    hs.append(model.layers[l].register_forward_pre_hook(pre, with_kwargs=True))
            from jlens.hooks import ActivationRecorder
            with torch.inference_mode(), ActivationRecorder(model.layers, at=rec_l) as rec:
                model.forward(x)
                lg = model.unembed(rec.activations[last][:, -1].float()).float()
                return lg, {l: rec.activations[l][0, -1].detach().clone() for l in (record or [])}
        finally:
            for h in hs: h.remove()

    def masses(self, lg):
        p = self.torch.softmax(lg.double(), -1)
        return self.torch.stack([p[:, c].sum(-1) for c in self.cls], -1).cpu().numpy()    # [B, 3]

    def ko_mask(self, T, colon, keep, ko_layers, dtype):
        """additive mask per batch element i: from layer >= ko_layers[i] the colon query attends only to positions in keep."""
        torch = self.torch; B = len(ko_layers); causal = torch.ones(T, T, dtype=torch.bool).tril()
        row = torch.zeros(T, dtype=torch.bool); row[list(keep)] = True; neg = torch.finfo(dtype).min; cache = {}
        def fn(layer):
            key = tuple(layer >= k for k in ko_layers)
            if key not in cache:
                allow = causal[None].repeat(B, 1, 1)
                for i, on in enumerate(key):
                    if on: allow[i, colon] &= row
                mk = torch.zeros(B, 1, T, T, dtype=dtype); mk.masked_fill_(~allow[:, None], neg); cache[key] = mk
            return cache[key]
        return fn


def do_shard(C, k, layers):
    torch = C.torch; rows = C.D[C.D.shard == k]; dtype = next(C.model.layers[0].parameters()).dtype
    KO = layers + [KO_NONE]; out = dict(paper_id=[], base=[], patch=[], ko1=[], ko2=[], selfpatch_maxdiff=[], ko_none_vs_nomask=[])
    for r in rows.itertuples():
        P = {t: build(C.tok, r.title, t) for t in TN}; base, res, lgb = {}, {}, {}
        for t in TN:
            lg, rr = C.forward(P[t][0], 1, record=layers); base[t] = C.masses(lg)[0]; res[t] = rr; lgb[t] = lg[0]
        pm = np.zeros((len(PAIRS), len(layers), 3))
        for j, (q, d) in enumerate(PAIRS):
            ids, _, colon = P[q]
            patch = {l: [(i, colon, res[d][l])] for i, l in enumerate(layers)}
            pm[j] = C.masses(C.forward(ids, len(layers), patch=patch)[0])
        # self-patch check (recipient with its own colon state at the first layer)
        ids, _, colon = P['authors']; lg_s, _ = C.forward(ids, 1, patch={layers[0]: [(0, colon, res['authors'][layers[0]])]})
        k1 = np.zeros((3, len(KO), 3)); k2 = np.zeros((3, len(KO), 3)); kchk = []
        for qi, q in enumerate(TN):
            ids, tpos, colon = P[q]; T = len(ids)
            k1[qi] = C.masses(C.forward(ids, len(KO), mask_fn=C.ko_mask(T, colon, [colon], KO, dtype))[0])
            keep2 = sorted(set(tpos) | {colon})
            lk2, _ = C.forward(ids, len(KO), mask_fn=C.ko_mask(T, colon, keep2, KO, dtype)); k2[qi] = C.masses(lk2)
            kchk.append(int(np.argmax(k1[qi, -1]) == np.argmax(base[q])))
        out['paper_id'].append(r.paper_id); out['base'].append(np.stack([base[t] for t in TN])); out['patch'].append(pm)
        out['ko1'].append(k1); out['ko2'].append(k2); out['selfpatch_maxdiff'].append(float((lg_s[0] - lgb['authors']).abs().max()))
        out['ko_none_vs_nomask'].append(float(np.mean(kchk)))
    return {kk: np.array(v) for kk, v in out.items()} | dict(layers=np.array(layers), ko_layers=np.array(KO), tasks=np.array(TN), pairs=np.array([f'{q}>{d}' for q, d in PAIRS]), classes=np.array(CLASSES))


def work(a):
    check_lock(); OUT.mkdir(parents=True, exist_ok=True); t0 = time.time(); C = None
    for k in [int(x) for x in a.shards.split(',')]:
        f = OUT / f'shard_{k:03d}.npz'
        if (OUT / f'shard_{k:03d}.json').exists(): log(f'shard {k} skip (exists)'); continue
        if (time.time() - t0) / 60 > a.max_minutes: log('time budget reached before shard', k); break
        if C is None: C = Ctx(); log('model loaded', C.env['gpu'], f'{(time.time() - t0) / 60:.1f} min')
        t1 = time.time(); d = do_shard(C, k, LAYERS)
        tmp = OUT / f'shard_{k:03d}.tmp{os.getpid()}.npz'; np.savez(tmp, **d); os.replace(tmp, f)
        meta = dict(shard=k, papers=len(d['paper_id']), seconds=time.time() - t1, env=C.env,
                    selfpatch_maxdiff=float(d['selfpatch_maxdiff'].max()), ko_none_vs_nomask_share=float(d['ko_none_vs_nomask'].mean()),
                    base_acc={t: float(np.mean(np.argmax(d['base'][:, i], -1) == CLASS_OF[t])) for i, t in enumerate(TN)})
        meta['status'] = 'OK' if meta['selfpatch_maxdiff'] <= 0.5 and meta['ko_none_vs_nomask_share'] >= 0.99 else 'WARN'
        json.dump(meta, open(OUT / f'shard_{k:03d}.json', 'w'), indent=1); log(f'shard {k} done', json.dumps(meta)[:500])


# ------------------------------------------------------------------ tiny (CPU)
def tiny(a):
    import torch, transformers, jlens, tempfile
    global OUT, LAYERS
    S = s11(); s10 = S.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = Ctx(model, tok); C.D = C.D[C.D.shard == 0].head(3).copy(); OUT = Path(tempfile.mkdtemp()); LAYERS = [0, 1]
    ok = []
    def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)
    d = do_shard(C, 0, LAYERS)
    check('rows', len(d['paper_id']) == 3); check('patch shape', d['patch'].shape == (3, 6, 2, 3), str(d['patch'].shape))
    check('ko shapes', d['ko1'].shape == (3, 3, 3, 3) and d['ko2'].shape == (3, 3, 3, 3), str(d['ko1'].shape))
    check('masses in [0,1]', bool((d['base'] >= 0).all() and (d['base'].sum(-1) <= 1 + 1e-6).all()))
    check('self-patch == base', float(d['selfpatch_maxdiff'].max()) < 1e-4, str(d['selfpatch_maxdiff'].max()))
    check('explicit mask (nothing blocked) == no mask', float(d['ko_none_vs_nomask'].mean()) == 1.0)
    check('patch changes output', float(np.abs(d['patch'][:, :, 0] - d['base'][:, [0, 0, 1, 1, 2, 2]]).max()) > 0)
    check('knockout changes output', float(np.abs(d['ko1'][:, :, 0] - d['ko1'][:, :, -1]).max()) > 0)
    # last-layer patch of the colon state with the donor's state must reproduce the donor output exactly
    r = C.D.iloc[0]; Pq = build(tok, r.title, 'authors'); Pd = build(tok, r.title, 'year'); last = C.n_layers() - 1
    lgd, rd = C.forward(Pd[0], 1, record=[last]); lgp, _ = C.forward(Pq[0], 1, patch={last: [(0, Pq[2], rd[last])]})
    check('last-layer colon patch == donor output', float((lgp - lgd).abs().max()) < 1e-4)
    # skip-if-done through work()
    a2 = argparse.Namespace(shards='0', max_minutes=10); C.D.to_parquet(OUT / 'd.parquet')
    global Ctx_cached
    np.savez(OUT / 'shard_000.npz', **d); json.dump({}, open(OUT / 'shard_000.json', 'w'))
    import io, contextlib; buf = io.StringIO()
    with contextlib.redirect_stdout(buf): work(a2)
    check('skip-if-done', 'skip (exists)' in buf.getvalue())
    vo = json.load(open(FREEZE / 'vocab.json')); check('vocab disjoint and non-empty', all(len(v) > 0 for v in vo.values()))
    print(f'TINY {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)


# ------------------------------------------------------------------ analysis (CPU)
def analyze(a):
    import pandas as pd
    check_lock(); fr = json.load(open(FREEZE / 'freeze.json'))
    miss = [k for k in fr['shards'] if not (OUT / f'shard_{k:03d}.json').exists()]
    if miss and not a.allow_missing: raise SystemExit(f'missing shards {miss}')
    ds = [np.load(OUT / f'shard_{k:03d}.npz') for k in fr['shards'] if (OUT / f'shard_{k:03d}.npz').exists()]
    pid = np.concatenate([d['paper_id'] for d in ds]); base = np.concatenate([d['base'] for d in ds])
    pm = np.concatenate([d['patch'] for d in ds]); k1 = np.concatenate([d['ko1'] for d in ds]); k2 = np.concatenate([d['ko2'] for d in ds])
    layers = list(ds[0]['layers']); KO = list(ds[0]['ko_layers'])
    D = pd.read_parquet(FREEZE / 'freeze.parquet').set_index('paper_id').loc[pid]
    codes, uniq = pd.factorize(D.team.to_numpy())
    W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    def mci(x, sel=None):
        x = x.astype(float) if sel is None else np.where(sel, x, np.nan).astype(float)
        ok = np.isfinite(x); w = W[:, ok]; v = x[ok]; b = (w @ v) / w.sum(1)
        return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    tgt = (D.group == 'target').to_numpy()
    rows = []; acc = {}
    for i, t in enumerate(TN):
        c = np.argmax(base[:, i], -1) == CLASS_OF[t]; acc[t] = mci(c)
        rows.append(dict(kind='baseline_accuracy', task=t, layer='', est=acc[t][0], lo=acc[t][1], hi=acc[t][2]))
    lnF = lambda m, q, d: np.log(m[..., CLASS_OF[q]] + 1e-300) - np.log(m[..., CLASS_OF[d]] + 1e-300)
    for j, (q, d) in enumerate(PAIRS):
        qi = TN.index(q)
        for li, l in enumerate(layers):
            sw = np.argmax(pm[:, j, li], -1) == CLASS_OF[d]; e = mci(sw)
            dF = lnF(pm[:, j, li], q, d) - lnF(base[:, qi], q, d); f = mci(dF)
            et = mci(sw, tgt); ec = mci(sw, ~tgt)
            rows.append(dict(kind='S_switch', task=f'{q}>{d}', layer=l, est=e[0], lo=e[1], hi=e[2], dF=f[0], dF_lo=f[1], dF_hi=f[2], target=et[0], control=ec[0]))
    verdict = {}
    for qi, q in enumerate(TN):
        Ks = []
        for li, l in enumerate(KO):
            keep = np.argmax(k1[:, qi, li], -1) == CLASS_OF[q]; e = mci(keep); Ks.append(e)
            keep2 = np.argmax(k2[:, qi, li], -1) == CLASS_OF[q]; e2 = mci(keep2)
            et = mci(keep, tgt); ec = mci(keep, ~tgt)
            rows.append(dict(kind='K_isolated', task=q, layer=l, est=e[0], lo=e[1], hi=e[2], K2=e2[0], K2_lo=e2[1], K2_hi=e2[2], target=et[0], control=ec[0]))
        okl = [Ks[i][0] >= 0.95 and Ks[i][1] >= 0.90 for i in range(len(layers))]
        X = next((layers[i] for i in range(len(layers)) if all(okl[i:])), None)
        if acc[q][0] < 0.90 or Ks[-1][0] < 0.95: v = 'odd / not interpretable'
        elif X is None: v = 'never fully fixed at the colon'
        elif X <= 16: v = 'format fixed early'
        elif X <= 40: v = 'fixed in the middle'
        else: v = 'fixed only late'
        verdict[q] = dict(locked_layer=X, reading=v, baseline_acc=acc[q][0], K_none=Ks[-1][0])
    S = {}
    for j, (q, d) in enumerate(PAIRS):
        s = [r_['est'] for r_ in rows if r_['kind'] == 'S_switch' and r_['task'] == f'{q}>{d}']
        S[f'{q}>{d}'] = next((layers[i] for i in range(len(layers)) if all(x >= 0.95 for x in s[i:])), None)
    SUMMARY.mkdir(parents=True, exist_ok=True); T = pd.DataFrame(rows); T.to_csv(SUMMARY / 'a23_table.csv', index=False)
    res = dict(n=len(pid), by_group=D.group.value_counts().to_dict(), verdict=verdict, S_from_layer=S, addendum_sha256=ADD_SHA, missing=miss)
    json.dump(res, open(SUMMARY / 'a23_results.json', 'w'), indent=1, default=str)
    rep = ['# Addendum 23 — H1 format-locking layer at ":" (LOCKED 2026-11-22)', '', f'{len(pid)} papers ({res["by_group"]}); team bootstrap {NB} draws, seed {SEED}.', '',
           '## Verdict per task (primary knockout, isolated colon)', '', pd.DataFrame(verdict).T.to_markdown(), '',
           '## Patching: first layer from which S(l) >= 0.95 at every later layer', '', json.dumps(S), '',
           '## Full table', '', T.to_markdown(index=False, floatfmt='.3f')]
    (SUMMARY / 'report.md').write_text('\n'.join(rep) + '\n'); print(json.dumps(res, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['freeze', 'tiny', 'work', 'analyze'])
    ap.add_argument('--force', action='store_true'); ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=38)
    ap.add_argument('--allow-missing', action='store_true'); a = ap.parse_args()
    {'freeze': freeze, 'tiny': tiny, 'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
