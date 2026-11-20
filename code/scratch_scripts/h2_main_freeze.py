#!/usr/bin/env python3
"""Addendum 20 (LOCKED 2026-11-20) main experiment, step 1 (CPU): freeze the `fict` condition.

Reads (never writes): 391_groups/config/prereg_addendum20.md + addendum20_lock.json (sha256 checked),
h2_fictitious/v3/selected_v3b.csv (locked title set, sha256 from the lock json), Stage 11 config/sample.parquet,
Stage 10 cohort (papers, name tokens, condition prompts).

Writes OUT (default 391_groups/raw/a20_freeze/):
  fict_titles.parquet  one row per paper with a valid fictitious title (1,127): paper_id, group, citation_bin, shard
                       (Stage 11 shard id), gen_round, fict_title, year, prompt, prompt_ids (json), n_prompt_tokens,
                       title_pos (json, positions of the fict title tokens, Stage 11 title_positions rule),
                       tail_prompt (aligned tail fict vs false_0, Stage 11 freeze rule), title_pos_<cond> for
                       true and false_0..4 (title-likelihood readout), max_context.
  h2_main_freeze.json  sha256 of every input and output, counts, run-time exclusions (context > 512 etc.).
Prompt: Stage 10 PROMPT with the fict title and the TRUE paper's year (as the false titles).
"""
import argparse, hashlib, importlib.util, json, sys, time
from pathlib import Path

B = Path('/scratch/zhang.zhiqi2/jlens'); H = Path.home() / 'jlens_work'
CFG = B / '391_groups/config'
ADD = CFG / 'prereg_addendum20.md'; ADD_SHA = 'fee691de801c7c0eb6c6dad42ec7681d8297c2308c425cffdec1a9592274454a'
LOCK = CFG / 'addendum20_lock.json'
TITLES = B / '391_groups/h2_fictitious/v3/selected_v3b.csv'
S11 = B / '361_stage11/config/sample.parquet'
OUT = B / '391_groups/raw/a20v2_freeze'   # v2 2026-11-20: v1 (raw/a20_freeze) used the TRUE title column by mistake; INVALID


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 24), b''): h.update(c)
    return h.hexdigest()


def load_mod(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def check_lock():
    if sha(ADD) != ADD_SHA: raise SystemExit(f'ADDENDUM 20 CHANGED: {sha(ADD)}')
    lk = json.loads(LOCK.read_text())
    if lk['sha256'] != ADD_SHA: raise SystemExit('lock json does not match the addendum sha')
    if sha(TITLES) != lk['title_set_sha256']: raise SystemExit(f'LOCKED TITLE SET CHANGED: {sha(TITLES)}')
    return lk


def main():
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=str(OUT)); a = ap.parse_args()
    out = Path(a.out); lk = check_lock()
    s11 = load_mod(H / '11_stage11/361_stage11.py', 's11'); s10 = s11.s10; R10 = s11.R10
    s10.verify(R10); s10.verify_conditions(R10); s11.verify()
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); P = papers.set_index('paper_id')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'author_index', 'token_index', 'token_id'])
    longest = toks.groupby(['paper_id', 'author_index']).size().groupby(level=0).max()
    smp = pd.read_parquet(S11)
    sel = pd.read_csv(TITLES, dtype={'paper_id': str})
    if sel.paper_id.duplicated().any(): raise SystemExit('duplicate paper in title set')
    if not sel.paper_id.isin(smp.paper_id).all(): raise SystemExit('title-set paper outside the Stage 11 sample')
    tok = s10.tokenizer()
    conds = ['true'] + [f'false_{k}' for k in range(5)]
    pr = {c: s10.condition_prompts(R10, papers, c)[0] for c in conds}
    S = sel.set_index('paper_id'); rows, excl = [], []
    for r in smp.itertuples():
        if r.paper_id not in S.index:
            excl.append(dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, reason='no valid fictitious title (generation rule, v3/excluded.csv)')); continue
        s = S.loc[r.paper_id]; p = P.loc[r.paper_id]
        if str(s.year) != str(p.year): raise SystemExit(f'year mismatch {r.paper_id}: {s.year} vs {p.year}')
        if s.group != r.group: raise SystemExit(f'group mismatch {r.paper_id}')
        title = str(s.cand)                                  # fictitious title = column 'cand' ('title' = the true title)
        if str(s.title) != str(p.title): raise SystemExit(f'true title mismatch {r.paper_id}')
        if title.strip().lower() == str(p.title).strip().lower(): raise SystemExit(f'fict title equals the true title {r.paper_id}')
        prompt = s10.PROMPT.format(title=title, year=p.year); ids = tok(prompt).input_ids
        mc = len(ids) + int(longest.get(r.paper_id, 1)) - 1
        if mc > s10.MAX_CONTEXT:
            excl.append(dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, reason=f'context {mc} > {s10.MAX_CONTEXT}')); continue
        tp = s11.title_positions(tok, prompt, ids)
        f0x, f0 = pr['false_0'][r.paper_id]; tf = s11.title_positions(tok, f0x, f0)
        tail = min(s11.common_suffix(ids, f0), len(ids) - 1 - max(tp), len(f0) - 1 - max(tf))
        if tail < 3:
            excl.append(dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, reason=f'aligned tail {tail} < 3')); continue
        txt = tok.decode([ids[i] for i in tp])
        if title.strip()[:8] not in txt: raise SystemExit(f'title positions do not decode to the title: {r.paper_id} {txt!r}')
        row = dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, shard=int(r.shard), gen_round=int(s['round']),
                   fict_title=title, year=str(p.year), prompt=prompt, prompt_ids=json.dumps(ids), n_prompt_tokens=len(ids),
                   title_pos=json.dumps(tp), tail_prompt=int(tail), max_context=int(mc), n_title_tokens=len(tp))
        for c in conds:
            cx, cid = pr[c][r.paper_id]; row[f'title_pos_{c}'] = json.dumps(s11.title_positions(tok, cx, cid))
        rows.append(row)
    df = pd.DataFrame(rows); ex = pd.DataFrame(excl, columns=['paper_id', 'group', 'citation_bin', 'reason'])
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / 'fict_titles.parquet', index=False); ex.to_csv(out / 'exclusions.csv', index=False)
    rep = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), script=str(Path(__file__).resolve()), script_sha256=sha(__file__),
               addendum_sha256=ADD_SHA, lock=lk, inputs={str(p): sha(p) for p in (TITLES, S11, R10 / 'cohort/papers.parquet', R10 / 'cohort/name_tokens.parquet', R10 / 'cohort/conditions/prompts.parquet')},
               n_papers=len(df), n_target=int((df.group == 'target').sum()), n_control=int((df.group == 'control').sum()),
               n_excluded=len(ex), excluded_reasons=ex.reason.value_counts().to_dict(), max_context=int(df.max_context.max()),
               shards=sorted(df.shard.unique().tolist()), papers_per_shard=df.groupby('shard').size().to_dict(),
               outputs={f: sha(out / f) for f in ('fict_titles.parquet', 'exclusions.csv')})
    (out / 'h2_main_freeze.json').write_text(json.dumps(rep, indent=1, default=str))
    print(json.dumps({k: rep[k] for k in ('n_papers', 'n_target', 'n_control', 'n_excluded', 'excluded_reasons', 'max_context')}, indent=1))
    if len(df) != 1127 or rep['n_target'] != 566 or rep['n_control'] != 561: print('WARN: counts differ from the addendum (1,127 = 566 T + 561 C)')


if __name__ == '__main__':
    main()
