"""Addendum 18b ("shelf map", LOCKED 2026-11-17, 381_stage13/config/prereg_addendum18b.md) - shared GPU/CPU helpers.

New file (2026-11-17). Frozen scripts are imported by path and never edited: 11_stage11/361_stage11.py (-> 351_stage10_fix1 ->
351_stage10.py). Every item driver (a18b_item{1..6}.py) uses:
  sample()        the 600-paper subsample of the Stage 11 sample (1,186 papers): 30 target + 30 control per citation bin
                  (10 bins; bin 513-1024 has 53 + 53 -> 30 + 30 drawn), numpy default_rng(SEED=1817) inside bin x group,
                  then shuffled with the same rng and cut into 24 shards of 25 papers (each shard mixes bins/groups).
                  The other 586 Stage 11 papers form the reference set (item 4 reference means only).
  Ctx / TinyCtx   model + tokenizer + cohort contexts + prompts of the 6 title conditions (true, false_0..4).
  layout()        per (paper, condition): prompt ids, title positions (Stage 11 rule), prompt tail after the title.
  work()          generic skip-if-exists unit loop with a time budget (min(max_minutes, Slurm time left - 4)), atomic saves,
                  a crash in compute stops the job (exit 1 = only code crashes stop the queue); checks are WARN only.
Outputs: /scratch/zhang.zhiqi2/jlens/381_stage13/raw/a18b_<item>/ and summary_a18b_<item>/.
"""
import hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens')
R10, R11, R12, R13, R391 = J / '351_stage10', J / '361_stage11', J / '371_stage12', J / '381_stage13', J / '391_groups'
CFG = R13 / 'a18b_config'
ADDENDUM = R13 / 'config/prereg_addendum18b.md'; ADDENDUM_SHA = '9104c351461c0fe91eb1f8a8cd0f29ae56b68985d064974b8156be7cb7cc52d3'
CONDS = ['true', 'false_0', 'false_1', 'false_2', 'false_3', 'false_4']; FALSES = CONDS[1:]
SEED = 1817; PER_CELL = 30; PAPERS_PER_SHARD = 25
FROZEN = {'361_stage11.py': H / '11_stage11/361_stage11.py', '351_stage10.py': H / '10_stage10/351_stage10.py'}
TINY = os.environ.get('A18B_TINY') == '1'


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


def load_mod(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


_M = {}
def s11():
    if 's11' not in _M: _M['s11'] = load_mod(FROZEN['361_stage11.py'], 's11_a18b')
    return _M['s11']


def check_addendum():
    h = sha(ADDENDUM)
    if h != ADDENDUM_SHA: raise SystemExit(f'ADDENDUM 18b CHANGED: {h}')
    return h


# ------------------------------------------------------------------ sample
def make_sample(write=True):
    import pandas as pd
    smp = pd.read_parquet(R11 / 'config/sample.parquet')
    rng = np.random.default_rng(SEED); pick = []
    for (b, g), x in smp.groupby(['citation_bin', 'group'], sort=True):
        x = x.sort_values('paper_id'); k = min(PER_CELL, len(x))
        pick.append(x.iloc[np.sort(rng.choice(len(x), k, replace=False))])
    s = pd.concat(pick).reset_index(drop=True)
    s = s.iloc[rng.permutation(len(s))].reset_index(drop=True)
    s['s11_shard'] = s['shard']; s['shard'] = np.arange(len(s)) // PAPERS_PER_SHARD
    ref = smp[~smp.paper_id.isin(s.paper_id)].sort_values('paper_id').reset_index(drop=True)
    ref['s11_shard'] = ref['shard']; ref['shard'] = np.arange(len(ref)) // PAPERS_PER_SHARD
    if write:
        CFG.mkdir(parents=True, exist_ok=True)
        f, fr = CFG / 'sample600.parquet', CFG / 'refset586.parquet'
        if f.exists():
            old = pd.read_parquet(f)
            if not (old.paper_id.tolist() == s.paper_id.tolist() and old.shard.tolist() == s.shard.tolist()): raise SystemExit('sample600 differs from the stored one')
        else:
            s.to_parquet(f, index=False); ref.to_parquet(fr, index=False)
        info = dict(seed=SEED, per_cell=PER_CELL, n=len(s), n_target=int((s.group == 'target').sum()), n_control=int((s.group == 'control').sum()),
                    n_shards=int(s.shard.max()) + 1, n_ref=len(ref), bins=s.groupby(['citation_bin', 'group']).size().unstack().to_dict(),
                    sha256_sample=sha(f), sha256_ref=sha(fr), stage11_sample_sha256=sha(R11 / 'config/sample.parquet'), addendum_sha256=check_addendum())
        (CFG / 'sample600.json').write_text(json.dumps(info, indent=1, default=str))
    return s, ref


def sample():
    import pandas as pd
    f = CFG / 'sample600.parquet'
    if not f.exists(): make_sample()
    return pd.read_parquet(f)


def refset():
    import pandas as pd
    if not (CFG / 'refset586.parquet').exists(): make_sample()
    return pd.read_parquet(CFG / 'refset586.parquet')


def parse_shards(s, n):
    if s is None or s in ('', 'all'): return list(range(n))
    out = []
    for part in str(s).split(','):
        if '-' in part: a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return [k for k in out if 0 <= k < n]


# ------------------------------------------------------------------ context
class Ctx:
    """real model on the GPU (Stage 10 fix-1 loader with weight prefetch)."""
    def __init__(self, tiny_model=None):
        import torch, pandas as pd
        m = s11(); s10 = m.s10; self.torch = torch; self.s10 = s10; self.s11 = m
        self.papers, toks = m.cohort(); self.ctx = m.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in CONDS}
        rt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
        self.role = dict(zip(rt.row_id, rt.role))
        self.sfirst = {(p, int(a)): int(t) for p, a, t in rt[rt.role == 'surname_first'][['paper_id', 'author_index', 'token_id']].itertuples(index=False)}
        if tiny_model is None:
            self.model, self.tok = s10.load_model(); self.tiny = False
        else:
            self.model, self.tok = tiny_model; self.tiny = True
        self.dtype = next(self.model.layers[0].parameters()).dtype
        self.env = dict(torch=torch.__version__, tiny=self.tiny,
                        gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [],
                        frozen_sha256={k: sha(v) for k, v in FROZEN.items()}, addendum18b_sha256=ADDENDUM_SHA)
        self._lay = {}

    def layout(self, pid, cond):
        """dict(ids, text, tpos, last_title, S) ; S = number of prompt tokens after the last title token (incl ':')."""
        k = (pid, cond)
        if k not in self._lay:
            text, ids = self.prompts[cond][pid]
            tpos = self.s11.title_positions(self.tok, text, ids)
            self._lay[k] = dict(ids=list(ids), text=text, tpos=tpos, last_title=tpos[-1], S=len(ids) - 1 - max(tpos))
        return self._lay[k]


def tiny_model():
    """random Qwen3-shaped model (64 layers so that every real layer id exists), fp32 on CPU, wrapped by jlens.from_hf."""
    import torch, transformers, jlens
    s10 = s11().s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer()
    return jlens.from_hf(hf, tok), tok


def make_ctx(tiny=False):
    return Ctx(tiny_model() if tiny else None)


# ------------------------------------------------------------------ forward helpers
def ranks(logits, gold, torch):
    """rank = 1 + number of logits strictly greater than the gold logit (Stage 10 score)."""
    gold = gold.to(logits.device); g = logits.gather(-1, gold[:, None]); return ((logits > g).sum(-1) + 1).int().cpu().numpy()


def final_logits(C, ids, positions, batch=1, hooks=(), mask_fn=None, record_layers=None):
    """forward of `batch` copies of ids with extra (module, hook) forward hooks; returns final logits [batch, n_pos, V]
    (Stage 11 run_final readout: block-63 output -> model.unembed), and optionally recorded block outputs."""
    torch = C.torch; model = C.model; hs = []
    x = torch.tensor([ids] * batch, device=model.input_device)
    try:
        for mod, fn in hooks: hs.append(mod.register_forward_hook(fn))
        if mask_fn is not None:
            for l in range(len(model.layers)):
                def pre(mod, args, kwargs, l=l):
                    mk = mask_fn(l)
                    if mk is not None: kwargs['attention_mask'] = mk.to(next(mod.parameters()).device)
                    return args, kwargs
                hs.append(model.layers[l].register_forward_pre_hook(pre, with_kwargs=True))
        from jlens.hooks import ActivationRecorder
        at = sorted(set([63] + list(record_layers or [])))
        with torch.inference_mode(), ActivationRecorder(model.layers, at=at) as rec:
            model.forward(x)
            h = rec.activations[63][:, positions]
            lg = torch.stack([model.unembed(h[i].float()).float() for i in range(batch)])
            acts = {l: rec.activations[l].detach().clone() for l in (record_layers or [])}
        return (lg, acts) if record_layers else lg
    finally:
        for hd in hs: hd.remove()


# ------------------------------------------------------------------ IO / loop
def save_npz(f, d, meta):
    f = Path(f); f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **d); os.replace(tmp, f)


def minutes_left():
    try: return s11().slurm_minutes_left()
    except Exception: return None


def work(units, out_path, compute, max_minutes=40, C=None, tiny=False, check=None, tag='a18b'):
    """units: list of hashable ids; out_path(u) -> Path; compute(C, u) -> (dict arrays, meta dict).
    Returns list of units still missing. A compute crash propagates (job exits non-zero)."""
    t0 = time.monotonic(); budget = max_minutes
    left = minutes_left()
    if left is not None and left - 4 < budget: budget = left - 4
    log(f'{tag} work: {len(units)} units, budget {budget:.1f} min')
    worst = 0.0; done = 0
    for u in units:
        f = out_path(u)
        if f.exists(): continue
        if done and (time.monotonic() - t0) / 60 + 1.3 * worst / 60 > budget: log('time budget reached before', u); break
        if C is None: C = make_ctx(tiny)
        t1 = time.monotonic(); d, meta = compute(C, u); dt = time.monotonic() - t1
        meta = dict(unit=list(u) if isinstance(u, tuple) else u, created=time.strftime('%Y-%m-%dT%H:%M:%S'), seconds=round(dt, 1), **C.env, **(meta or {}))
        save_npz(f, d, meta); worst = max(worst, dt); done += 1
        log(f'{tag} unit {u} {dt:.0f}s total={(time.monotonic() - t0) / 60:.1f}min', json.dumps(meta.get('check', {}), default=str)[:400])
    miss = [u for u in units if not out_path(u).exists()]
    print(f'REMAINING {len(miss)} of {len(units)}', flush=True)
    return miss, C


def write_daily(line):
    d = H / 'daily_log_cpu'; d.mkdir(exist_ok=True)
    with open(d / f'{time.strftime("%Y-%m-%d")}.txt', 'a') as f: f.write(line.rstrip() + '\n')


# ------------------------------------------------------------------ team bootstrap (2,000 draws, archived author teams)
class Boot:
    """team-cluster bootstrap on the archived author teams (stage13_cpu.group_folds), NB draws, one multinomial draw shared by
    every estimate of an analysis (paired contrasts). Within-bin target - control = Stage 10 definition (bins with >= min_n papers
    per group, weights n_t n_c / (n_t + n_c), fixed at the point counts)."""
    def __init__(self, nb=2000, seed=18):
        import pandas as pd
        c13 = load_mod(H / '13_stage13/stage13_cpu.py', 'c13_a18b')
        papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
        _, team = c13.group_folds(papers.paper_id.to_numpy())
        codes, uniq = pd.factorize(pd.Series(team)); self.team = pd.Series(codes, index=papers.paper_id.to_numpy())
        self.meta = papers.set_index('paper_id'); self.nb = nb
        self.cnt = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=nb).astype(np.float64)

    def W(self, pids): return self.cnt[:, self.team.loc[list(pids)].to_numpy()]

    def mean(self, pids, v):
        v = np.asarray(v, float); ok = np.isfinite(v); pids = np.asarray(pids)[ok]; v = v[ok]
        W = self.W(pids)
        with np.errstate(invalid='ignore', divide='ignore'): b = (W @ v) / W.sum(1)
        return float(v.mean()) if len(v) else np.nan, b

    def ratio(self, pids, num, den):
        num, den = np.asarray(num, float), np.asarray(den, float); ok = np.isfinite(num) & np.isfinite(den)
        pids = np.asarray(pids)[ok]; W = self.W(pids)
        with np.errstate(invalid='ignore', divide='ignore'): b = (W @ num[ok]) / (W @ den[ok])
        return float(num[ok].mean() / den[ok].mean()), b

    def tc(self, pids, v, min_n=30):
        """within-bin target - control of per-paper values v."""
        v = np.asarray(v, float); pids = np.asarray(pids); ok = np.isfinite(v); pids, v = pids[ok], v[ok]
        g = self.meta.group_tight.reindex(pids).to_numpy(); bins = self.meta.citation_bin.reindex(pids).to_numpy(); W = self.W(pids)
        est, boot, wsum = 0.0, np.zeros(self.nb), 0.0; nbins = 0
        for b in sorted(set(bins)):
            it = (bins == b) & (g == 'target'); ic = (bins == b) & (g == 'control')
            nt, nc = it.sum(), ic.sum()
            if nt < min_n or nc < min_n: continue
            w = nt * nc / (nt + nc); wsum += w; nbins += 1
            with np.errstate(invalid='ignore', divide='ignore'):
                est += w * (v[it].mean() - v[ic].mean())
                boot += w * ((W[:, it] @ v[it]) / W[:, it].sum(1) - (W[:, ic] @ v[ic]) / W[:, ic].sum(1))
        if wsum == 0: return np.nan, np.full(self.nb, np.nan), 0
        return est / wsum, boot / wsum, nbins

    @staticmethod
    def ci(b):
        b = np.asarray(b, float); b = b[np.isfinite(b)]
        return (np.nan, np.nan) if len(b) < 100 else tuple(np.percentile(b, [2.5, 97.5]))

    @staticmethod
    def p(b):
        b = np.asarray(b, float); b = b[np.isfinite(b)]
        if not len(b): return np.nan
        return max(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / len(b))


def fmt(e, b, d=3):
    lo, hi = Boot.ci(b); star = '*' if (np.isfinite(lo) and (lo > 0 or hi < 0)) else ''
    return f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]{star}'
