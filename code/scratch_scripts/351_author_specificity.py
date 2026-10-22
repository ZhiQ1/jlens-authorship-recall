#!/usr/bin/env python3
"""3.5.1 exploratory task-specific readout: gold vs field/bin-matched false FIRST token.
Unsteered; first-token only, NOT full-name teacher forcing or full-cohort inference.
One fixed Open Recall prompt per paper, same logits for gold/false comparisons.
"""
import argparse
import hashlib
import json
import math
import os
import random
import time
from collections import defaultdict
from pathlib import Path

MODEL = 'Qwen/Qwen3-32B'
REVISION = '9216db5781bf21249d130ec9da846c4624c16137'
DEFAULT_LAYERS = '16,24,32,40,48,56,62'

def authors(row):
    return [s.strip() for s in row['authors'].split(';') if s.strip()]

def good_name(s):
    return len(s.split()) >= 2 and len(s) >= 8 and not any(ch.isdigit() for ch in s) and '.' not in s

def prompt_for(r):
    return f'Who are the authors of the paper titled "{r["title"]}" ({r["year"]})?\nAuthors:'

def first_token(tok, prompt, name, prefix_ids):
    ids = tok.encode(prompt + ' ' + name, add_special_tokens=False)
    if ids[:len(prefix_ids)] != prefix_ids or len(ids) <= len(prefix_ids):
        return None
    return int(ids[len(prefix_ids)])

def select_papers(rows, n_each, seed):
    rng = random.Random(seed)
    groups = defaultdict(list)
    for row in rows:
        if row.get('group_351') in 'ABCD' and row.get('group_351') and any(good_name(a) for a in authors(row)):
            groups[row['group_351']].append(row)
    selected = []
    for group in 'ABCD':
        options = sorted(groups[group], key=lambda x:x['paper_id'])
        if len(options) < n_each:
            raise RuntimeError(f'Only {len(options)} eligible papers in group {group}; requested {n_each}')
        selected.extend(rng.sample(options, n_each))
    return selected

def pick_false(row, gold_name, rows, tok, prompt, prefix_ids):
    gold_norm = {x.casefold() for x in authors(row)}
    gold_id = first_token(tok, prompt, gold_name, prefix_ids)
    if gold_id is None:
        return None
    gold_n_tokens = len(tok.encode(' ' + gold_name, add_special_tokens=False))
    candidates = []
    for other in rows:
        if other['paper_id'] == row['paper_id'] or other.get('field') != row.get('field') or other.get('citation_bin') != row.get('citation_bin'):
            continue
        try:
            year_dist = abs(int(other['year']) - int(row['year']))
        except (ValueError, TypeError):
            year_dist = 9999
        for name in authors(other):
            if not good_name(name) or name.casefold() in gold_norm:
                continue
            fake_id = first_token(tok, prompt, name, prefix_ids)
            if fake_id is None or fake_id == gold_id:
                continue
            n_tokens = len(tok.encode(' ' + name, add_special_tokens=False))
            key = (abs(n_tokens - gold_n_tokens), year_dist, name.casefold(), other['paper_id'])
            candidates.append((key, name, fake_id, other['paper_id']))
    if not candidates:
        return None
    candidates.sort(key=lambda x:x[0])
    _, name, token_id, source = candidates[0]
    return {'name':name,'token_id':token_id,'source_paper_id':source, 'year_distance': abs(int(next(x for x in rows if x['paper_id']==source)['year'])-int(row['year']))}

def score(vec, token_id):
    import torch
    v=vec.float().flatten().cpu()
    if not bool(torch.isfinite(v).all()):
        raise ValueError('Nonfinite output logits')
    value=v[token_id]
    return {'rank':int((v>value).sum().item())+1,'logit':float(value.item()),'logprob':float(torch.log_softmax(v,dim=-1)[token_id].item())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',default=f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_all/351_four_groups.jsonl')
    ap.add_argument('--lens',default=f'/scratch/{os.environ.get("USER","unknown")}/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
    ap.add_argument('--output',default=f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_all/351_author_specificity.jsonl')
    ap.add_argument('--layers',default=DEFAULT_LAYERS)
    ap.add_argument('--n-each',type=int,default=1,help='1 => four papers, A/B/C/D')
    ap.add_argument('--seed',type=int,default=351)
    ap.add_argument('--plan-only',action='store_true',help='CPU-only paper selection, no model/lens')
    args=ap.parse_args()
    layers=[int(x) for x in args.layers.split(',')]
    if not layers or len(set(layers))!=len(layers) or not set(layers).issubset(set(range(63))):
        ap.error('Layers must be distinct integers in 0..62')
    if args.n_each<1:
        ap.error('--n-each must be >=1')
    data_path=Path(args.data)
    rows=[json.loads(x) for x in data_path.read_text(encoding='utf-8').splitlines() if x.strip()]
    assert len({r['paper_id'] for r in rows})==len(rows)
    selected=select_papers(rows,args.n_each,args.seed)
    config={'data_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),'model':MODEL,'revision':REVISION,'lens_path':str(Path(args.lens).resolve()),'layers':layers,'seed':args.seed,'n_each':args.n_each,'protocol':'first author token (space-prefixed), same prompt for gold vs false, no gold-name prefix; one matched false candidate per paper'}
    if args.plan_only:
        for row in selected:
            print(row['group_351'],row['paper_id'],row['citation_bin'],row['field'],next(a for a in authors(row) if good_name(a)))
        print('Plan only; no GPU used')
        return
    import torch
    import transformers
    import jlens
    if not torch.cuda.is_available():
        raise RuntimeError('A100/H200 CUDA allocation required')
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    done={}
    if out.exists():
        for line in out.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            item=json.loads(line)
            if item.get('config')!=config:
                raise RuntimeError('Existing output configuration differs; use another --output')
            if item['paper_id'] in done:
                raise RuntimeError('Duplicate existing paper_id')
            done[item['paper_id']]=item
    print('Selected:',len(selected),'Previously completed:',len(done),flush=True)
    print('Loading tokenizer...',flush=True)
    tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REVISION)
    planned=[]
    for row in selected:
        if row['paper_id'] in done:continue
        prompt=prompt_for(row)
        prefix_ids=tok.encode(prompt,add_special_tokens=False)
        golds=[(a,first_token(tok,prompt,a,prefix_ids)) for a in authors(row) if good_name(a)]
        golds=[(a,tid) for a,tid in golds if tid is not None]
        if not golds:
            print('SKIP boundary gold:',row['paper_id'],flush=True);continue
        gold_name,gold_id=golds[0]
        # Strict same field/citation-bin; closest first-token length and year.
        false=pick_false(row,gold_name,rows,tok,prompt,prefix_ids)
        if false is None:
            print('SKIP no suitable false:',row['paper_id'],flush=True);continue
        planned.append((row,prompt,gold_name,gold_id,false))
    print('Eligible to measure:',len(planned),'groups:',[r['group_351'] for r,*_ in planned],flush=True)
    if not planned:
        return
    print('Loading public lens and Qwen3-32B...',flush=True)
    lens=jlens.JacobianLens.load(args.lens)
    assert lens.d_model==5120 and set(layers)<=set(lens.source_layers)
    hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,dtype=torch.bfloat16,device_map='cuda',low_cpu_mem_usage=True).eval()
    model=jlens.from_hf(hf,tok)
    for i,(row,prompt,gold_name,gold_id,false) in enumerate(planned,1):
        torch.cuda.reset_peak_memory_stats()
        t0=time.perf_counter()
        jlog,final,ids=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=512,use_jacobian=True)
        vlog,final2,ids2=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=512,use_jacobian=False)
        if not torch.equal(ids.cpu(),ids2.cpu()):raise RuntimeError('Paired passes token IDs differ')
        if (final.float()-final2.float()).abs().max().item()>0.1:raise RuntimeError('Paired final logits differ unexpectedly')
        result={}
        for tag,values in [('final',final[0])]+[(f'jlens_L{l}',jlog[l][0]) for l in layers]+[(f'vanilla_L{l}',vlog[l][0]) for l in layers]:
            gs=score(values,gold_id)
            fs=score(values,false['token_id'])
            result[tag]={'gold':gs,'false':fs,'gold_minus_false_logprob':gs['logprob']-fs['logprob'],'gold_rank_better':gs['rank']<fs['rank']}
        item={'paper_id':row['paper_id'],'group_351':row['group_351'],'citation_bin':row['citation_bin'],'field':row['field'],'year':row['year'],'title':row['title'],'prompt':prompt,'gold_author':gold_name,'gold_first_token_id':gold_id,'gold_first_token_text':tok.decode([gold_id]),'false_author':false,'false_first_token_text':tok.decode([false['token_id']]),'seconds':round(time.perf_counter()-t0,3),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,3),'measurements':result,'config':config}
        with out.open('a',encoding='utf-8') as f:
            f.write(json.dumps(item,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        print(f'{i}/{len(planned)} Group {row["group_351"]}, paper {row["paper_id"][:8]}, {item["seconds"]:.2f}s, peak {item["peak_gpu_gib"]:.2f}GiB, L32 J gold rank={result.get("jlens_L32",result[f"jlens_L{layers[0]}"])["gold"]["rank"]}, false rank={result.get("jlens_L32",result[f"jlens_L{layers[0]}"])["false"]["rank"]}',flush=True)
        del jlog,vlog,final,final2
    print('SAVED',out,flush=True)
    print('Diagnostic only: one selected gold name and one matched false per paper; not full-name recall or group inference.',flush=True)

if __name__=='__main__':main()
