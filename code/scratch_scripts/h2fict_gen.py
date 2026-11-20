#!/usr/bin/env python3
"""H2 fictitious control titles: generator (exploratory quality sample; NOT a preregistered run).

For each sampled paper, Qwen3-32B (chat template, thinking off) writes K candidate titles for a
non-existent paper in the same field / close topic, with a different specific contribution.
Candidates are filtered later by h2fict_check.py (CPU).

Usage:
  python h2fict_gen.py --mode sample --out OUT          # writes OUT/sample_papers.parquet (CPU)
  python h2fict_gen.py --mode prompts --out OUT          # prints 2 rendered prompts (CPU, tokenizer only)
  python h2fict_gen.py --mode gen --out OUT [--limit N]  # GPU generation -> OUT/candidates.jsonl
"""
import argparse, json, os, time, re
from pathlib import Path

ROOT = Path('/scratch/zhang.zhiqi2/jlens')
PAPERS = ROOT / '351_stage10/cohort/papers.parquet'
S11 = ROOT / '361_stage11/config/sample.parquet'
MODEL = 'Qwen/Qwen3-32B'
SEED = 20261117
K = 4                      # candidates per paper
GEN = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, max_new_tokens=96)

SYSTEM = ('You are an experienced researcher who writes realistic academic paper titles. '
          'You never copy existing titles.')
USER = '''Here is the title of a real {field} paper published in {year}:

"{title}"

Write the title of a DIFFERENT, fictitious paper that could plausibly appear in the same subfield around the same time. Requirements:
- Same field and closely related topic, so a reader would place both papers in the same research area.
- A different specific contribution: change the main object, method, system, population, or result (not just synonyms or reordered words). Do not reuse the distinctive phrases of the original title.
- It must not be the title of any real, existing paper you know of.
- Match the style and length of the original: about {nwords} words, same kind of punctuation (colon, subtitle, abbreviations) if the original uses them.
Output only the new title on one line, without quotes or any explanation.'''


def sample(out):
    import pandas as pd, numpy as np
    p = pd.read_parquet(PAPERS, columns=['paper_id', 'title', 'year', 'field', 'citations', 'citation_bin', 'group_tight', 'n_authors'])
    s = pd.read_parquet(S11, columns=['paper_id', 'group', 'citation_bin']).rename(columns={'citation_bin': 's11_bin'})
    d = s.merge(p, on='paper_id', how='left'); assert d.title.notna().all()
    rng = np.random.default_rng(SEED)
    parts = []
    for (b, g), x in d.groupby(['s11_bin', 'group'], sort=True):   # 10 bins x 2 groups x 3 = 60
        parts.append(x.iloc[rng.choice(len(x), size=min(3, len(x)), replace=False)])
    r = pd.concat(parts).reset_index(drop=True)
    out.mkdir(parents=True, exist_ok=True); r.to_parquet(out / 'sample_papers.parquet', index=False)
    print(r.groupby(['s11_bin', 'group']).size().unstack(), len(r))
    print(r.field.value_counts().to_string())


def build_prompt(tok, row):
    nwords = len(row.title.split())
    msgs = [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': USER.format(field=row.field, year=row.year, title=row.title, nwords=nwords)}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)


def clean(t):
    t = t.strip().split('\n')[0].strip()
    t = re.sub(r'^(new\s+)?title\s*:\s*', '', t, flags=re.I).strip()
    return t.strip('"“”\'* ').strip()


def gen(out, limit, bs):
    import torch, pandas as pd
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.manual_seed(SEED)
    r = pd.read_parquet(out / 'sample_papers.parquet')
    if limit: r = r.head(limit)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = 'left'
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map='cuda:0').eval()
    t_load = time.time() - t0; print(f'load {t_load:.1f}s', flush=True)
    fo = (out / 'candidates.jsonl').open('a'); done = set()
    if (out / 'candidates.jsonl').exists():
        done = {json.loads(l)['paper_id'] for l in (out / 'candidates.jsonl').open()}
    todo = [x for x in r.itertuples() if x.paper_id not in done]
    timings = []
    for i in range(0, len(todo), bs):
        chunk = todo[i:i + bs]
        enc = tok([build_prompt(tok, x) for x in chunk], return_tensors='pt', padding=True).to('cuda:0')
        torch.cuda.synchronize(); t1 = time.time()
        with torch.no_grad():
            o = model.generate(**enc, num_return_sequences=K, pad_token_id=tok.pad_token_id, **GEN)
        torch.cuda.synchronize(); dt = time.time() - t1
        txt = tok.batch_decode(o[:, enc.input_ids.shape[1]:], skip_special_tokens=True)
        n_new = int((o[:, enc.input_ids.shape[1]:] != tok.pad_token_id).sum())
        timings.append(dict(batch=i // bs, n_papers=len(chunk), sec=dt, new_tokens=n_new))
        for j, x in enumerate(chunk):
            raw = txt[j * K:(j + 1) * K]
            fo.write(json.dumps(dict(paper_id=x.paper_id, raw=raw, cands=[clean(c) for c in raw])) + '\n')
        fo.flush()
        # in-job self-check (non-fatal): WARN on empty / think-tag outputs
        bad = sum(1 for c in txt if not clean(c) or '<think>' in c)
        print(f'batch {i // bs}: {len(chunk)} papers {dt:.1f}s ({dt / len(chunk):.2f}s/paper), new_tokens={n_new}, '
              f'{"WARN empty/think=" + str(bad) if bad else "selfcheck ok"}', flush=True)
        if i == 0:
            for c in txt[:K]: print('  example:', repr(c), flush=True)
    json.dump(dict(load_sec=t_load, batches=timings, bs=bs, K=K, gen=GEN, gpu=torch.cuda.get_device_name(0),
                   max_mem_gb=torch.cuda.max_memory_allocated() / 1e9), (out / f'timing_{os.environ.get("SLURM_JOB_ID", "local")}.json').open('w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', required=True, choices=['sample', 'prompts', 'gen'])
    ap.add_argument('--out', default=str(ROOT / '391_groups/h2_fictitious'))
    ap.add_argument('--limit', type=int, default=0); ap.add_argument('--bs', type=int, default=20)
    a = ap.parse_args(); out = Path(a.out)
    if a.mode == 'sample': sample(out)
    elif a.mode == 'prompts':
        import pandas as pd
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(MODEL); r = pd.read_parquet(out / 'sample_papers.parquet')
        for x in list(r.itertuples())[:2]:
            s = build_prompt(tok, x); print(s); print('n_tokens', len(tok(s).input_ids)); assert '<think>\n\n</think>' in s
    else: gen(out, a.limit, a.bs)
