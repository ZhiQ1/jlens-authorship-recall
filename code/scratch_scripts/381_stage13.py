"""Stage 13 GPU (2026-10-28, user request): is the middle-layer content "this paper" or "this task"?

M3 task contrast. The same title under three questions, none of which contains the year:
  authors: Who are the authors of the paper titled "{title}"?\nAuthors:
  year   : In which year was the paper titled "{title}" published?\nYear:
  field  : Which research field does the paper titled "{title}" belong to?\nField:
For all 9,108 papers, one forward per prompt (prompt + teacher-forced answer, so the answer tokens are also scored at the
model output); store the residual at the last title token and at the final ':' for LAYERS (fp16), plus
  year task   : log10(1/rank) of every digit of the true year at the output (does the model know the year?)
  authors task: log10(1/rank) of the first author's first token at the output.
Analysis (stage13_analyze.py, CPU): same-paper vs different-paper similarity across tasks by layer, cross-task probe
transfer (field, year, citations, author first token), and task decodability. If the early representation is shared
across tasks and splits late, the middle layers encode "this paper"; if it splits early, they encode the task.

Units = 72 Stage 10 shards (128 papers each). Claims, budget and crash policy as in Stage 11/12 (a crash disables
the unit type and the job continues). X1/X3/X4 (added 2026-10-28, user-approved), on the Stage 11 sample (1,186 papers, 24 shards):
  X1 xpatch : cross-task patching (+ random control: the authors-run state of an unrelated paper C of the same title
              length; tune/test split by paper - layers chosen on tune, reported on test). Corrupted run = authors prompt with partner B's title (same field, same title token
              count, no shared surname). At layer l, replace the residuals of ALL title positions with paper A's residuals
              from (a) the authors prompt, (b) the year prompt, (c) the field prompt. Score A's first author.
              Same recovery in (a) and (b)/(c) = the title-span state is task-independent paper identity at layer l.
  X3 para   : para_gen = Qwen3-32B rewrites each title (raw-text greedy, no chat template); automatic checks (no year, no
              author surname, word overlap, length); para_run opens only after logs/para_ok exists (manual review).
              para_run: authors prompt with original / paraphrase / partner title; residuals + first-author score.
  X4 pscope : patchscope. Source = A's authors-prompt residual (no year anywhere) at the last title token or ':' at
              layer l; injected at the same layer into the placeholder of 'Paper: X\n...' target prompts that ask for
              the year, the first author, the field. Control source = partner B. Score the true answer tokens.
Runs as a hand-over from the Stage 12 work loop when Stage 12 has nothing left,
or in its own job. Any GPU with enough memory for the model works (forward only); outputs record the GPU names.
  python 381_stage13.py dry        # CPU, tiny random Qwen3 with the real tokenizer: positions, shapes, scoring
  python 381_stage13.py work [--max-minutes 80]
  python 381_stage13.py remaining
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

DIR = Path(__file__).resolve().parent
S11 = Path.home() / 'jlens_work/11_stage11'
_sp = importlib.util.spec_from_file_location('s11', S11 / '361_stage11.py'); s11 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s11)
s10 = s11.s10; R10 = s11.R10
ROOT = Path('/scratch') / os.environ.get('USER', '') / 'jlens/381_stage13'
LAYERS = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]
# 2026-10-28 provenance audit: no template contains the year, and all three have the same 9 tokens before the title, so
# the title occupies the same absolute positions in every task (needed for cross-task patching, X1).
TASKS = {'authors': ('Who are the authors of the paper titled "{t}"?\nAuthors:', 'authors'),
         'year': ('In what year was the research paper titled "{t}" published?\nYear:', 'year'),
         'field': ('In what research field is the paper titled "{t}"?\nField:', 'field')}
PREFIX_TOKENS = 9
TASK_NAMES = list(TASKS)


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')
def log(*x): print(now(), *x, flush=True)


def units(n_shards=72, n11=24):
    broken = {f.stem[len('broken_'):] for f in (ROOT / 'logs').glob('broken_*.json')}
    U = [('task', None, k) for k in range(n_shards)]
    if (ROOT / 'config/pairs.parquet').exists():
        U += [('xpatch', None, k) for k in range(n11)] + [('pscope', None, k) for k in range(n11)] + [('para_gen', None, k) for k in range(n11)]
        if (ROOT / 'logs/para_ok').exists(): U += [('para_run', None, k) for k in range(n11)]
    return [u for u in U if u[0] not in broken]


def out_path(u, root=None): return (root or ROOT) / 'raw' / u[0] / f'shard_{u[2]:03d}.npz'


def remaining(a=None):
    left = [u for u in units() if not out_path(u).exists()]
    print(f'{len(left)} of {len(units())} Stage 13 units missing'); return left


def build(tok, title, task, answer_ids):
    """prompt ids (+ teacher-forced answer); index of the last title token and of the final ':'."""
    tpl = TASKS[task][0]; prompt = tpl.format(t=title)
    e = tok(prompt, return_offsets_mapping=True); ids = list(e.input_ids)
    a = prompt.index('titled "') + len('titled "'); b = a + len(title)
    tpos = [i for i, (x, y) in enumerate(e.offset_mapping) if x < b and y > a]
    if not tpos: raise ValueError('no title tokens')
    colon = len(ids) - 1
    if tok.decode(ids[colon:]).strip() != ':': raise ValueError(f'prompt does not end with ":" ({tok.decode(ids[-2:])!r})')
    full = ids + list(answer_ids)
    return full, tpos[-1], colon


def do_task(C, shard, layers=LAYERS):
    torch = C.torch; tok = C.tok
    P = C.papers[C.papers.shard == shard]
    res, pids, yr_nlr, au_nlr = [], [], [], []
    for r in P.itertuples():
        year_ids = tok.encode(' ' + str(int(r.year)), add_special_tokens=False)
        first = C.ctx.get(r.paper_id, [])
        au_ids = [first[0][2][0]] if first else []
        per_task = []
        for task in TASK_NAMES:
            ans = year_ids if task == 'year' else (au_ids if task == 'authors' else [])
            full, it, ic = build(tok, r.title, task, ans)
            ids = full[:len(full) - 1] if ans else full          # the last answer token is only a target
            acts = C.record(ids, layers)
            per_task.append(np.stack([np.stack([acts[l][it].float().cpu().numpy(), acts[l][ic].float().cpu().numpy()]) for l in layers]))
            if ans:
                h = acts[layers[-1]][ic:ic + len(ans)].float()
                lg = C.unembed(h).float(); g = torch.tensor(ans, device=lg.device)
                rk = (lg > lg.gather(1, g[:, None])).sum(1) + 1
                v = (-torch.log10(rk.double())).cpu().numpy()
                (yr_nlr if task == 'year' else au_nlr).append(float(v.mean()))
        if not au_ids: au_nlr.append(np.nan)
        res.append(np.stack(per_task).astype(np.float16)); pids.append(r.paper_id)       # [task, layer, pos(title, colon), d]
    return dict(paper_id=np.array(pids), resid=np.stack(res), year_nlr=np.array(yr_nlr), author_first_nlr=np.array(au_nlr),
                layers=np.array(layers), tasks=np.array(TASK_NAMES), positions=np.array(['title_last', 'colon']))


# ------------------------------------------------------------------ X1 / X3 / X4 (2026-10-28)
XP_LAYERS = [4, 8, 16, 24, 32, 40, 48]
PS_LAYERS = [8, 16, 24, 32, 40, 48, 56]
PS_TARGETS = {'year': 'Paper: X\nThe paper was published in the year', 'author': 'Paper: X\nThe first author of the paper is',
              'field': 'Paper: X\nResearch field:'}
PARA_PROMPT = ('Rewrite the title of a research paper using different words while keeping exactly the same meaning. '
               'Do not add any information.\nOriginal title: {t}\nRewritten title:')
_CACHE = {}


def sample():
    import pandas as pd
    if 'smp' not in _CACHE:
        _CACHE['smp'] = pd.read_parquet(s11.ROOT / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin', 'shard']]
        _CACHE['pairs'] = pd.read_parquet(ROOT / 'config/pairs.parquet').set_index('paper_id')
    return _CACHE['smp'], _CACHE['pairs']


def title_span(tok, title):
    full, it, ic = build(tok, title, 'authors', [])
    return list(range(PREFIX_TOKENS, it + 1)), full


def freeze(a=None):
    """partner B for every Stage 11 sample paper: same field, same number of title tokens, no shared surname, not itself;
    deterministic (seed 1313). Also checks the provenance conditions of the templates."""
    import pandas as pd
    tok = s10.tokenizer(); papers, toks = s11.cohort(); ctx = s11.contexts_of(toks)
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet')
    for t, (tpl, _) in TASKS.items():
        pre = tpl.split('{t}')[0]; n = len(tok(pre).input_ids)
        assert n == PREFIX_TOKENS, (t, n)
    P = papers.set_index('paper_id'); L = {pid: len(title_span(tok, P.loc[pid].title)[0]) for pid in papers.paper_id}
    sur = {pid: {a.split()[-1].lower() for a in str(P.loc[pid].authors).split('; ') if a.strip()} for pid in papers.paper_id}
    rng = np.random.default_rng(1313); rows = []
    for pid in smp.paper_id:
        f = P.loc[pid].field
        cand = [q for q in papers[papers.field == f].paper_id if q != pid and L[q] == L[pid] and not (sur[q] & sur[pid]) and q in ctx]
        if not cand: continue
        q = cand[rng.integers(len(cand))]
        # random control C (Hana's lesson): another paper, any field, same title length, no surname shared with A or B
        cc = [x for x in papers.paper_id if x not in (pid, q) and L[x] == L[pid] and not (sur[x] & (sur[pid] | sur[q])) and x in ctx]
        c = cc[rng.integers(len(cc))]
        rows.append(dict(paper_id=pid, partner=q, random_c=c, n_title_tokens=L[pid], field=f))
    d = pd.DataFrame(rows)
    # tune / test split (by paper, stratified by group): layers and positions are chosen on tune, reported on test
    d = d.merge(smp[['paper_id', 'group']], on='paper_id')
    # 2026-10-28 review: split by author TEAM (papers sharing any full author name are one group, conservative), so no
    # team is on both sides; whole groups are assigned, alternating within target / control, seed 1314.
    sys.path.insert(0, str(DIR)); import stage13_cpu as c13
    _, team = c13.group_folds(d.paper_id.to_numpy(), k=2, seed=1314)
    d['team'] = team; d['split'] = ''
    for g, sub in d.groupby('group'):
        teams = list(dict.fromkeys(sub.team)); np.random.default_rng(1314).shuffle(teams); n_t = 0
        for t in teams:
            i = d.index[(d.team == t) & (d.group == g) & (d.split == '')]
            if not len(i): continue
            lab = 'tune' if n_t < len(sub) / 2 else 'test'; d.loc[d.team == t, 'split'] = d.loc[d.team == t, 'split'].where(d.loc[d.team == t, 'split'] != '', lab); n_t += len(i); (ROOT / 'config').mkdir(parents=True, exist_ok=True); d.to_parquet(ROOT / 'config/pairs.parquet', index=False)
    print(f'pairs: {len(d)} of {len(smp)} sample papers have a same-field, same-length partner without shared surnames')


def run_final(C, ids, positions, patch=None, batch=1):
    """as Stage 11 run_final (block-output replacement at ('at', position) per batch element), for any model depth."""
    torch = C.torch; model = C.model; handles = []; last = len(model.layers) - 1
    x = torch.tensor([ids] * batch, device=model.input_device)
    try:
        for l, items in (patch or {}).items():
            def hook(mod, inp, out, items=items):
                h = out if torch.is_tensor(out) else out[0]
                for e, n, t in items: h[e, n[1]] = t.to(h.device, h.dtype)
                return out
            handles.append(model.layers[l].register_forward_hook(hook))
        from jlens.hooks import ActivationRecorder
        with torch.inference_mode(), ActivationRecorder(model.layers, at=[last]) as rec:
            model.forward(x); h = rec.activations[last][:, positions]
            return torch.stack([model.unembed(h[i].float()).float() for i in range(batch)])
    finally:
        for hd in handles: hd.remove()


def score_tf(C, ids_prompt, answer, patch=None, batch=1):
    """teacher-forced mean log10(1/rank) of the answer tokens after ids_prompt (per batch element)."""
    torch = C.torch; ids = list(ids_prompt) + list(answer[:-1]); pos = [len(ids_prompt) - 1 + j for j in range(len(answer))]
    lg = run_final(C, ids, pos, patch=patch, batch=batch); g = torch.tensor(answer, device=lg.device)
    out = []
    for b in range(batch):
        rk = (lg[b] > lg[b].gather(1, g[:, None])).sum(1) + 1; out.append(float((-torch.log10(rk.double())).mean()))
    return np.array(out)


def do_xpatch(C, shard):
    smp, pairs = sample(); P = C.papers.set_index('paper_id'); rows = []
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; A, Bt = P.loc[r.paper_id].title, P.loc[q].title
        name = C.ctx[r.paper_id][0][2]
        spanA, fullA = title_span(C.tok, A); spanB, fullB = title_span(C.tok, Bt)
        if spanA != spanB: continue                                            # equal length by construction
        clean = score_tf(C, fullA, name)[0]; corrupt = score_tf(C, fullB, name)[0]
        c = pairs.loc[r.paper_id].random_c; spanC, fullC = title_span(C.tok, P.loc[c].title)
        if spanC != spanB: continue
        rec = {}
        actsC = C.record(fullC[:len(fullC)], XP_LAYERS); rec['random_c'] = {l: actsC[l][spanC[0]:spanC[-1] + 1] for l in XP_LAYERS}
        for task in TASK_NAMES:
            ids, _, _ = build(C.tok, A, task, []); acts = C.record(ids, XP_LAYERS)
            rec[task] = {l: acts[l][spanA[0]:spanA[-1] + 1] for l in XP_LAYERS}
        row = dict(paper_id=r.paper_id, partner=q, random_c=c, split=pairs.loc[r.paper_id].split, clean=clean, corrupt=corrupt)
        for task in TASK_NAMES + ['random_c']:
            patch = {}
            for i, l in enumerate(XP_LAYERS):
                patch.setdefault(l, []).extend([(i, ('at', p), rec[task][l][j]) for j, p in enumerate(spanA)])
            v = score_tf(C, fullB, name, patch=patch, batch=len(XP_LAYERS))
            for i, l in enumerate(XP_LAYERS): row[f'{task}@{l}'] = v[i]
        rows.append(row)
    return {k: np.array([x[k] for x in rows]) for k in rows[0]} if rows else dict(paper_id=np.array([]))


def ps_answers(C, r, P):
    yr = C.tok.encode(' ' + str(int(P.loc[r].year)), add_special_tokens=False)
    au = C.ctx[r][0][2]; fl = C.tok.encode(' ' + str(P.loc[r].field), add_special_tokens=False)
    return dict(year=yr, author=au, field=fl)


def do_pscope(C, shard):
    smp, pairs = sample(); P = C.papers.set_index('paper_id'); rows = []
    tgt = {}
    for k, t in PS_TARGETS.items():
        e = C.tok(t, return_offsets_mapping=True); ids = list(e.input_ids); x = t.index('X')
        tgt[k] = (ids, [i for i, (a, b) in enumerate(e.offset_mapping) if a <= x < b][0])
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; ans = ps_answers(C, r.paper_id, P)
        src = {}
        for who, pid in (('self', r.paper_id), ('partner', q)):
            ids, it, ic = build(C.tok, P.loc[pid].title, 'authors', []); acts = C.record(ids, PS_LAYERS)
            src[who] = {('title', l): acts[l][it] for l in PS_LAYERS} | {('colon', l): acts[l][ic] for l in PS_LAYERS}
        row = dict(paper_id=r.paper_id, partner=q)
        for k, (ids, xi) in tgt.items():
            row[f'{k}@none'] = score_tf(C, ids, ans[k])[0]
            for who in ('self', 'partner'):
                for pos in ('title', 'colon'):
                    patch = {l: [(i, ('at', xi), src[who][(pos, l)])] for i, l in enumerate(PS_LAYERS)}
                    v = score_tf(C, ids, ans[k], patch=patch, batch=len(PS_LAYERS))
                    for i, l in enumerate(PS_LAYERS): row[f'{k}@{who}@{pos}@{l}'] = v[i]
        rows.append(row)
    return {k: np.array([x[k] for x in rows]) for k in rows[0]} if rows else dict(paper_id=np.array([]))


def para_checks(title, para, year, authors):
    w = lambda s: {x for x in ''.join(c.lower() if c.isalnum() else ' ' for c in s).split() if len(x) > 3}
    a, b = w(title), w(para); jac = len(a & b) / max(1, len(a | b))
    sur = {x.split()[-1].lower() for x in str(authors).split('; ') if x.strip()}
    ok = bool(para.strip()) and str(int(year)) not in para and not any(s and s in para.lower() for s in sur) and 0.5 <= len(para) / max(1, len(title)) <= 2.0
    return ok, jac


def do_para_gen(C, shard):
    torch = C.torch; smp, _ = sample(); P = C.papers.set_index('paper_id'); hf = C.model._hf_model; out = []
    for r in smp[smp.shard == shard].itertuples():
        t = P.loc[r.paper_id].title; ids = C.tok(PARA_PROMPT.format(t=t), return_tensors='pt').input_ids.to(C.model.input_device)
        with torch.inference_mode():
            g = hf.generate(ids, max_new_tokens=60, do_sample=False, pad_token_id=C.tok.eos_token_id)
        txt = C.tok.decode(g[0, ids.shape[1]:], skip_special_tokens=True).split('\n')[0].strip().strip('"')
        ok, jac = para_checks(t, txt, P.loc[r.paper_id].year, P.loc[r.paper_id].authors)
        out.append((r.paper_id, t, txt, ok, jac))
    return dict(paper_id=np.array([x[0] for x in out]), title=np.array([x[1] for x in out]), paraphrase=np.array([x[2] for x in out]),
                auto_ok=np.array([x[3] for x in out]), word_jaccard=np.array([x[4] for x in out]))


def do_para_run(C, shard):
    smp, pairs = sample(); P = C.papers.set_index('paper_id'); rows, res = [], []
    para = {}
    for f in sorted((ROOT / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); para |= {p: (t, ok, j) for p, t, ok, j in zip(z['paper_id'], z['paraphrase'], z['auto_ok'], z['word_jaccard'])}
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in para or not para[r.paper_id][1] or r.paper_id not in C.ctx: continue
        name = C.ctx[r.paper_id][0][2]; q = pairs.loc[r.paper_id].partner
        per, sc = [], []
        for title in (P.loc[r.paper_id].title, para[r.paper_id][0], P.loc[q].title):
            ids, it, ic = build(C.tok, title, 'authors', []); acts = C.record(ids, LAYERS)
            per.append(np.stack([np.stack([acts[l][it].float().cpu().numpy(), acts[l][ic].float().cpu().numpy()]) for l in LAYERS]))
            sc.append(score_tf(C, ids, name)[0])
        rows.append((r.paper_id, q, *sc, para[r.paper_id][2])); res.append(np.stack(per).astype(np.float16))
    return dict(paper_id=np.array([x[0] for x in rows]), partner=np.array([x[1] for x in rows]), score_original=np.array([x[2] for x in rows]),
                score_paraphrase=np.array([x[3] for x in rows]), score_partner=np.array([x[4] for x in rows]), word_jaccard=np.array([x[5] for x in rows]),
                resid=np.stack(res) if res else np.zeros((0,)), layers=np.array(LAYERS), versions=np.array(['original', 'paraphrase', 'partner']))


def compute(C, u):
    return {'task': lambda: do_task(C, u[2]), 'xpatch': lambda: do_xpatch(C, u[2]), 'pscope': lambda: do_pscope(C, u[2]),
            'para_gen': lambda: do_para_gen(C, u[2]), 'para_run': lambda: do_para_run(C, u[2])}[u[0]]()


class Ctx:
    def __init__(self):
        import torch, pandas as pd
        self.torch = torch
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
        self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], script_sha256=s10.sha_file(__file__))

    def record(self, ids, layers): return s11.record(self, ids, layers)
    def unembed(self, h): return self.model.unembed(h)


def save(u, d, env):
    f = out_path(u); f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(unit=list(u), created=now(), **env))), **d); os.replace(tmp, f)


def work(a):
    budget = a.max_minutes; t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    left = s11.slurm_minutes_left()
    if left is not None and left - 8 < budget: budget = left - 8
    CL = ROOT / 'logs/claims'; CL.mkdir(parents=True, exist_ok=True); C = getattr(a, 'ctx', None); last = 0.0
    log(f'stage13 work: job {me}, budget {budget:.0f} min')
    while True:
        u = None
        for v in units():
            if out_path(v).exists(): continue
            if s11.claim(CL / f'{v[0]}_{v[2]}', me): u = v; break
        if u is None: log('stage13: nothing left to claim'); return
        if (time.monotonic() - t0) / 60 + 1.5 * max(last, 60) / 60 > budget:
            d = CL / f'{u[0]}_{u[2]}'; os.rename(d, d.with_name(d.name + f'.released_{me}')); log('time budget reached; released', u); return
        if C is None: C = Ctx()
        t1 = time.monotonic()
        try: d = compute(C, u)
        except Exception as e:
            import traceback; s11.dump(ROOT / f'logs/broken_{u[0]}.json', dict(unit=list(u), error=repr(e), job=me, at=now(), tb=traceback.format_exc()))
            dd = CL / f'{u[0]}_{u[2]}'; os.rename(dd, dd.with_name(dd.name + f'.crashed_{me}')); log('UNIT CRASH (type disabled, job continues):', u, repr(e)); return
        save(u, d, C.env); last = time.monotonic() - t1
        log(f'stage13 {u[0]} shard {u[2]:03d} papers={len(d["paper_id"])} {last:.0f}s total={(time.monotonic() - t0) / 60:.1f}min')


def dry(a):
    """CPU: a 2-layer random Qwen3 with the real tokenizer and the jlens wrapper; 6 papers of shard 0."""
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer()
    class D(Ctx):
        def __init__(self):
            self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
            self.papers = self.papers[self.papers.shard == 0].head(6); self.model = jlens.from_hf(hf, tok); self.tok = tok; self.env = {}
    C = D(); ok = []
    def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)
    for r in C.papers.itertuples():
        for task in TASK_NAMES:
            full, it, ic = build(tok, r.title, task, [])
            check(f'{task} title token inside title', tok.decode([full[it]]).strip() in r.title or r.title.strip().endswith(tok.decode([full[it]]).strip()), repr(tok.decode([full[it]])))
            check(f'{task} ends with ":"', tok.decode([full[ic]]).strip() == ':')
            check(f'{task} no year in prompt', str(int(r.year)) not in tok.decode(full))
        break
    d = do_task(C, 0, layers=[0, 1])
    n = len(C.papers)
    check('resid shape', d['resid'].shape == (n, 3, 2, 2, 64), str(d['resid'].shape))
    check('year scores finite', len(d['year_nlr']) == n and np.isfinite(d['year_nlr']).all())
    check('author scores', len(d['author_first_nlr']) == n)
    check('resid differs across tasks at colon', float(np.abs(d['resid'][:, 0, -1, 1] - d['resid'][:, 1, -1, 1]).max()) > 0)
    # the recorded residual at the colon must not depend on the appended answer tokens (causality)
    full, it, ic = build(tok, C.papers.iloc[0].title, 'year', tok.encode(' 1999', add_special_tokens=False))
    a1 = C.record(full[:ic + 1], [1])[1][ic]; a2 = C.record(full[:-1], [1])[1][ic]
    check('colon residual unaffected by the answer tokens', float((a1 - a2).abs().max()) < 1e-4)
    # X1 / X3 / X4 on the tiny model (needs config/pairs.parquet from `freeze`)
    global XP_LAYERS, PS_LAYERS, LAYERS
    XP_LAYERS, PS_LAYERS, LAYERS = [0, 1], [0, 1], [0, 1]
    smp, pairs = sample(); sh = int(smp.shard.iloc[0]); C.papers = s11.cohort()[0]
    _CACHE['smp'] = smp[smp.shard == sh].head(3)
    x = do_xpatch(C, sh); check('xpatch rows', len(x['paper_id']) >= 1, f"{len(x['paper_id'])} rows")
    r0 = _CACHE['smp'].iloc[0]; P = C.papers.set_index('paper_id'); q = pairs.loc[r0.paper_id].partner; name = C.ctx[r0.paper_id][0][2]
    spanB, fullB = title_span(C.tok, P.loc[q].title); actsB = C.record(fullB, [0, 1])
    ident = score_tf(C, fullB, name, patch={l: [(i, ('at', p_), actsB[l][p_]) for p_ in spanB] for i, l in enumerate([0, 1])}, batch=2)
    check('xpatch identity patch (B with its own states) == corrupt', np.allclose(ident, x['corrupt'][0], atol=1e-5), f'{ident} vs {x["corrupt"][0]}')
    full_patch = score_tf(C, fullB, name, patch={1: [(0, ('at', p_), C.record(title_span(C.tok, P.loc[r0.paper_id].title)[1] + list(name[:-1]), [1])[1][p_]) for p_ in range(len(fullB) + len(name) - 1)]})
    check('patching every position at the last layer with the clean run == clean', np.allclose(full_patch, x['clean'][0], atol=1e-5), f'{full_patch} vs {x["clean"][0]}')
    check('xpatch all task columns + random control', all(f'{t}@{l}' in x for t in TASK_NAMES + ['random_c'] for l in XP_LAYERS))
    check('pairs have random C and a tune/test split', {'random_c', 'split'} <= set(pairs.columns) and set(pairs.split) == {'tune', 'test'})
    ps = do_pscope(C, sh); check('pscope rows', len(ps['paper_id']) >= 1 and 'year@self@colon@1' in ps)
    check('pscope patched differs from none', any(abs(ps['author@self@title@0'][i] - ps['author@none'][i]) > 0 for i in range(len(ps['paper_id']))))
    for k, t in PS_TARGETS.items():
        e = C.tok(t, return_offsets_mapping=True); xi = [i for i, (a_, b_) in enumerate(e.offset_mapping) if a_ <= t.index('X') < b_]
        check(f'pscope placeholder found in {k} prompt', len(xi) == 1 and C.tok.decode([e.input_ids[xi[0]]]).strip() == 'X')
    import tempfile; global ROOT
    old_root = ROOT; ROOT = Path(tempfile.mkdtemp())
    g = do_para_gen(C, sh); check('para_gen rows', len(g['paper_id']) == len(_CACHE['smp']))
    check('para checks reject year / surname', not para_checks('A study of x', 'A 1999 study', 1999, 'J. Smith')[0] and not para_checks('A study of x', 'Smith study', 2000, 'J. Smith')[0] and para_checks('A study of mice', 'Research on mice', 2000, 'J. Smith')[0])
    (ROOT / 'raw/para_gen').mkdir(parents=True); g['auto_ok'][:] = True; np.savez(ROOT / f'raw/para_gen/shard_{sh:03d}.npz', **g)
    pr = do_para_run(C, sh); check('para_run rows', len(pr['paper_id']) >= 1 and pr['resid'].shape[1:3] == (3, 2), str(pr['resid'].shape))
    ROOT = old_root
    print(f'DRY {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['dry', 'freeze', 'work', 'remaining']); p.add_argument('--max-minutes', type=float, default=80)
    a = p.parse_args(); {'dry': dry, 'freeze': freeze, 'work': work, 'remaining': remaining}[a.command](a)


if __name__ == '__main__':
    main()
