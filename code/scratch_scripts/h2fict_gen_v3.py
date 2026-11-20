#!/usr/bin/env python3
"""H2 fictitious control titles, generator v3 (user decision 2026-11-19). Copy of v2 with: (a) prompt says the title
must not be shorter than the original (at least N words, N..N+3); (b) papers = the Stage 11 subset (1,186) by default,
or --sample s60 for the 60-paper quality sample; (c) time guard: no new batch after --max-min minutes (default 36),
so a job stays under 45 min; the driver resubmits until every paper of the round is done (skip-if-done).

(v2 docstring follows)
H2 fictitious control titles, generator v2 (user-approved fixes 2026-11-18; exploratory quality sample).

Changes vs v1 (h2fict_gen.py, kept): one call per paper returns a numbered list of 8 candidates with different
openings; terminology must exist by {year}; the true title's first word and sentence pattern are forbidden;
duplicates removed. Regeneration rounds (--round 1, 2) only for papers that have no passing candidate after the
previous round's check (OUT/round{r-1}_status.csv, written by h2fict_check_v2.py); the prompt then lists the
rejected titles. If no paper needs regeneration the job exits before loading the model.

Usage: python h2fict_gen_v2.py --round R [--out OUT] [--bs 30]
Output: OUT/candidates_r{R}.jsonl  {paper_id, round, raw, cands}
"""
import argparse, json, os, re, time
from pathlib import Path

ROOT = Path('/scratch/zhang.zhiqi2/jlens')
V1 = ROOT / '391_groups/h2_fictitious'
MODEL = 'Qwen/Qwen3-32B'
SEED = 20261119
S11 = ROOT / '361_stage11/config/sample.parquet'
PAPERS = ROOT / '351_stage10/cohort/papers.parquet'
SAMPLE = os.environ.get('H2F_SAMPLE', 's11')
N_CAND = 8
GEN = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, max_new_tokens=700)
ARTICLES = {'a', 'an', 'the'}

SYSTEM = ('You are an experienced researcher who writes realistic academic paper titles. '
          'You never copy existing titles.')
USER = '''Here is the title of a real {field} paper published in {year}:

"{title}"

Write {n} titles of DIFFERENT, fictitious papers that could plausibly have appeared in the same subfield around {year}. Requirements for every title:
- Same field and closely related topic, so a reader would place it in the same research area as the original.
- A different specific contribution: change the main object, method, system, population, or result. Do not just swap synonyms or substitute one noun into the original sentence.
- Do not start with the word "{first}", and do not reuse the original's sentence pattern (its sequence of phrases and connecting words).
- Do not reuse the distinctive phrases of the original title.
- Use only terminology, methods, instruments and concepts that already existed by {year}.
- It must not be the title of any real, existing paper you know of.
- Match the style of the original. Length: the new title must NOT be shorter than the original; use at least {nwords} words (between {nwords} and {nmax} words).
The {n} titles must all differ from each other and must each begin with a different first word.
{extra}Output only a numbered list (1. ... {n}. ...), one title per line, without quotes or explanations.'''
EXTRA = ('These earlier attempts were rejected (too close to an existing paper or to the original, or off-topic); '
         'do not repeat them or anything similar:\n{rej}\n')


def first_word(title):
    ws = re.findall(r"[A-Za-z0-9][\w'\-]*", title)
    for w in ws:
        if w.lower() not in ARTICLES: return w
    return ws[0] if ws else ''


def build_prompt(tok, row, rejected=()):
    extra = EXTRA.format(rej='\n'.join(f'- {t}' for t in list(rejected)[:12])) if rejected else ''
    u = USER.format(field=row.field, year=row.year, title=row.title, n=N_CAND, first=first_word(row.title),
                    nwords=len(row.title.split()), nmax=len(row.title.split()) + 3, extra=extra)
    msgs = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': u}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)


def parse(txt):
    out, seen = [], set()
    for line in txt.split('\n'):
        m = re.match(r'^\s*\d{1,2}\s*[.)]\s*(.+)$', line)
        if not m: continue
        t = re.sub(r'^(title\s*:\s*)', '', m.group(1).strip(), flags=re.I).strip().strip('"“”\'* ').strip()
        key = re.sub(r'[^a-z0-9]', '', t.lower())
        if len(key) >= 5 and key not in seen: seen.add(key); out.append(t)
    return out


def load_sample():
    import pandas as pd
    if SAMPLE == 's60': return pd.read_parquet(V1 / 'sample_papers.parquet')
    p = pd.read_parquet(PAPERS, columns=['paper_id', 'title', 'year', 'field', 'citations', 'citation_bin', 'group_tight', 'n_authors'])
    s = pd.read_parquet(S11, columns=['paper_id', 'group', 'citation_bin']).rename(columns={'citation_bin': 's11_bin'})
    d = s.merge(p, on='paper_id', how='left'); assert d.title.notna().all() and len(d) == 1186
    return d


def todo_papers(out, rnd):
    import pandas as pd
    r = load_sample()
    rej = {}
    if rnd > 0:
        st = pd.read_csv(out / f'round{rnd - 1}_status.csv')
        need = set(st.loc[st.n_ok == 0, 'paper_id'])
        r = r[r.paper_id.isin(need)]
        cc = pd.read_csv(out / f'checked_r{rnd - 1}.csv')
        for p, g in cc[cc.paper_id.isin(need)].groupby('paper_id'): rej[p] = g.cand.tolist()
        for q in range(rnd - 1):   # also earlier rounds
            f = out / f'checked_r{q}.csv'
            if f.exists():
                c0 = pd.read_csv(f)
                for p, g in c0[c0.paper_id.isin(need)].groupby('paper_id'): rej[p] = g.cand.tolist() + rej.get(p, [])
    return r, rej


def gen(out, rnd, bs, max_min=36.0):
    T_START = time.time()
    r, rej = todo_papers(out, rnd)
    fo_path = out / f'candidates_r{rnd}.jsonl'
    done = {json.loads(l)['paper_id'] for l in fo_path.open()} if fo_path.exists() else set()
    todo = [x for x in r.itertuples() if x.paper_id not in done]
    print(f'round {rnd}: {len(r)} papers need generation, {len(todo)} to do', flush=True)
    if not todo:
        fo_path.touch(); return
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.manual_seed(SEED + rnd)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = 'left'
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map='cuda:0').eval()
    t_load = time.time() - t0; print(f'load {t_load:.1f}s', flush=True)
    timings = []
    with fo_path.open('a') as fo:
        for i in range(0, len(todo), bs):
            if (time.time() - T_START) / 60 > max_min:
                print(f'time guard: stopping after {i} papers; resubmit to continue', flush=True); break
            chunk = todo[i:i + bs]
            enc = tok([build_prompt(tok, x, rej.get(x.paper_id, ())) for x in chunk], return_tensors='pt', padding=True).to('cuda:0')
            torch.cuda.synchronize(); t1 = time.time()
            with torch.no_grad():
                o = model.generate(**enc, pad_token_id=tok.pad_token_id, **GEN)
            torch.cuda.synchronize(); dt = time.time() - t1
            txt = tok.batch_decode(o[:, enc.input_ids.shape[1]:], skip_special_tokens=True)
            n_new = int((o[:, enc.input_ids.shape[1]:] != tok.pad_token_id).sum())
            timings.append(dict(batch=i // bs, n_papers=len(chunk), sec=dt, new_tokens=n_new))
            ncs = []
            for x, t in zip(chunk, txt):
                c = parse(t); ncs.append(len(c))
                fo.write(json.dumps(dict(paper_id=x.paper_id, round=rnd, raw=t, cands=c)) + '\n')
            fo.flush()
            few = sum(n < 6 for n in ncs)   # non-fatal self-check
            print(f'batch {i // bs}: {len(chunk)} papers {dt:.1f}s ({dt / len(chunk):.2f}s/paper) new_tokens={n_new} '
                  f'cands/paper min {min(ncs)} mean {sum(ncs) / len(ncs):.1f} {"WARN <6 cands: " + str(few) if few else "selfcheck ok"}', flush=True)
            if i == 0: print('  example:\n' + txt[0], flush=True)
    json.dump(dict(round=rnd, load_sec=t_load, batches=timings, bs=bs, n_cand=N_CAND, gen=GEN, gpu=torch.cuda.get_device_name(0),
                   max_mem_gb=torch.cuda.max_memory_allocated() / 1e9),
              (out / f'timing_r{rnd}_{os.environ.get("SLURM_JOB_ID", "local")}.json').open('w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', type=int, required=True)
    ap.add_argument('--out', default=str(V1 / 'v3'))
    ap.add_argument('--max-min', type=float, default=36.0)
    ap.add_argument('--bs', type=int, default=30)
    ap.add_argument('--show-prompt', action='store_true')
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.show_prompt:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(MODEL); r, rej = todo_papers(out, a.round)
        x = next(r.itertuples()); s = build_prompt(tok, x, rej.get(x.paper_id, ['Example rejected title']))
        print(s); print('n_tokens', len(tok(s).input_ids)); print('first word:', first_word(x.title))
        print(parse('1. Alpha beta gamma\n2) "Delta epsilon"\n3. alpha beta gamma\nnoise\n4. Title: Zeta eta'))
    else: gen(out, a.round, a.bs, a.max_min)
