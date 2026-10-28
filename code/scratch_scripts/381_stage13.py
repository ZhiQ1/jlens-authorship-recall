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
the unit type and the job continues). Runs as a hand-over from the Stage 12 work loop when Stage 12 has nothing left,
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
TASKS = {'authors': ('Who are the authors of the paper titled "{t}"?\nAuthors:', 'authors'),
         'year': ('In which year was the paper titled "{t}" published?\nYear:', 'year'),
         'field': ('Which research field does the paper titled "{t}" belong to?\nField:', 'field')}
TASK_NAMES = list(TASKS)


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')
def log(*x): print(now(), *x, flush=True)


def units(n_shards=72):
    broken = {f.stem[len('broken_'):] for f in (ROOT / 'logs').glob('broken_*.json')}
    return [] if 'task' in broken else [('task', None, k) for k in range(n_shards)]


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
        try: d = do_task(C, u[2])
        except Exception as e:
            import traceback; s11.dump(ROOT / f'logs/broken_{u[0]}.json', dict(unit=list(u), error=repr(e), job=me, at=now(), tb=traceback.format_exc()))
            dd = CL / f'{u[0]}_{u[2]}'; os.rename(dd, dd.with_name(dd.name + f'.crashed_{me}')); log('UNIT CRASH (type disabled, job continues):', u, repr(e)); return
        save(u, d, C.env); last = time.monotonic() - t1
        log(f'stage13 task shard {u[2]:03d} papers={len(d["paper_id"])} {last:.0f}s total={(time.monotonic() - t0) / 60:.1f}min '
            f'year_nlr={np.nanmean(d["year_nlr"]):.2f} author_first_nlr={np.nanmean(d["author_first_nlr"]):.2f}')


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
    print(f'DRY {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['dry', 'work', 'remaining']); p.add_argument('--max-minutes', type=float, default=80)
    a = p.parse_args(); {'dry': dry, 'work': work, 'remaining': remaining}[a.command](a)


if __name__ == '__main__':
    main()
