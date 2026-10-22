#!/usr/bin/env python3
"""Neuronpedia Qwen3-32B J-Lens TASK VALIDATION, not formal 3.5.1 inference.
40 sampled papers, one gold + one field/bin-matched false author per paper.
First-token & conditional full-name, J-Lens/Vanilla/Final, resumable JSONL.
"""
import argparse, csv, hashlib, json, math, os, random, statistics, time
from collections import defaultdict
from pathlib import Path

MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
DEFAULT_LAYERS='16,24,32,40,48,56,62'

def names(r): return [x.strip() for x in r['authors'].split(';') if x.strip()]
def valid_name(a): return len(a.split())>=2 and len(a)>=8 and not any(x.isdigit() for x in a) and '.' not in a

def make_prompt(r): return f'Who are the authors of the paper titled "{r["title"]}" ({r["year"]})?\nAuthors:'

def token_plan(tok,prompt,name,max_name_tokens):
    # Essential invariant: the exact prefix token IDs remain unchanged when author is appended.
    base=tok.encode(prompt,add_special_tokens=False)
    full=tok.encode(prompt+' '+name,add_special_tokens=False)
    if len(full)<=len(base) or full[:len(base)]!=base: return None
    rest=full[len(base):]
    if len(rest)>max_name_tokens: return None
    # Decode/reencode exact input prefixes to avoid tokenization boundary shifts.
    contexts=[]
    for j,target in enumerate(rest):
        prefix_ids=full[:len(base)+j]
        text=tok.decode(prefix_ids,skip_special_tokens=False,clean_up_tokenization_spaces=False)
        actual=tok.encode(text,add_special_tokens=False)
        if actual!=prefix_ids: return None
        contexts.append((text,int(target)))
    return {'ids':rest,'contexts':contexts}

def score(v,target):
    import torch
    x=v.float().flatten().cpu()
    if not torch.isfinite(x).all().item():raise ValueError('Nonfinite logits')
    z=x[target]; return {'rank':int(torch.sum(x>z).item())+1,'logprob':float(torch.log_softmax(x,dim=-1)[target].item())}

def all_scores(logits,tokens):
    items=[score(vec,t) for vec,t in zip(logits,tokens)]
    return {'tokens':items,'first_rank':items[0]['rank'],'first_logprob':items[0]['logprob'], 'mean_reciprocal_rank':statistics.mean(1/x['rank'] for x in items),'mean_logprob':statistics.mean(x['logprob'] for x in items),'sum_logprob':sum(x['logprob'] for x in items),'num_tokens':len(items)}

def select_papers(rows,seed):
    # Deterministic diverse selection: cycle citation bins, no group-based balancing.
    bins=defaultdict(list)
    for r in rows:
        if any(valid_name(n) for n in names(r)):bins[r['citation_bin']].append(r)
    rng=random.Random(seed)
    order=['0-2','3-4','5-8','9-16','17-32','33-64','65-128','129-256','257-512','513-1024','1025-2048','2049-4096','4097+']
    for b in order:rng.shuffle(bins[b])
    selected=[]
    while any(bins.values()):
        for b in order:
            if bins[b]:selected.append(bins[b].pop())
    return selected

def choose_pair(row,rows,tok,max_tokens):
    prompt=make_prompt(row)
    golds=[]
    for name in names(row):
        if valid_name(name):
            p=token_plan(tok,prompt,name,max_tokens)
            if p:golds.append((name,p))
    if not golds:return None
    gold_name,gold_plan=golds[0]
    gold_norm={x.casefold() for x in names(row)}
    candidates=[]
    pool=[r for r in rows if r['paper_id']!=row['paper_id'] and r['field']==row['field'] and r['citation_bin']==row['citation_bin']]
    pool.sort(key=lambda r:abs(int(r['year'])-int(row['year'])) if str(r['year']).isdigit() and str(row['year']).isdigit() else 9999)
    for other in pool[:60]:
        try:dist=abs(int(other['year'])-int(row['year']))
        except Exception:dist=9999
        for fake_name in names(other):
            if not valid_name(fake_name) or fake_name.casefold() in gold_norm:continue
            fp=token_plan(tok,prompt,fake_name,max_tokens)
            if not fp or fp['ids'][0]==gold_plan['ids'][0]:continue
            candidates.append(((abs(len(fp['ids'])-len(gold_plan['ids'])),dist,fake_name.casefold(),other['paper_id']),fake_name,fp,other['paper_id']))
    if not candidates:return None
    candidates.sort(key=lambda x:x[0]);_,fake_name,fp,source=candidates[0]
    return {'paper':row,'prompt':prompt,'gold_name':gold_name,'gold':gold_plan,'false_name':fake_name,'false':fp,'false_source':source}

def summary(path,layers):
    records=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    print('===== TASK VALIDATION SUMMARY =====',len(records),'papers',flush=True)
    for l in layers:
        for mode in ('jlens','vanilla','final'):
            ds=[]; first=[]; full=[]
            key=f'{mode}_L{l}' if mode!='final' else 'final'
            for r in records:
                d=r['measurements'][key];ds.append(d['gold']['mean_logprob']-d['false']['mean_logprob']);first.append(int(d['gold']['first_logprob']>d['false']['first_logprob']));full.append(int(ds[-1]>0))
            print(f'L{l} {mode:<7} first_win={statistics.mean(first):.3f} full_win={statistics.mean(full):.3f} mean_full_logprob_delta={statistics.mean(ds):.3f}',flush=True)
        # final is repeated per layer only for legible side-by-side comparisons

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    root=f'/scratch/{os.environ.get("USER","unknown")}/jlens'
    ap.add_argument('--data',default=f'{root}/351_all/351_four_groups.csv')
    ap.add_argument('--lens',default=f'{root}/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
    ap.add_argument('--output',default=f'{root}/351_all/351_public_task_validation.jsonl')
    ap.add_argument('--n',type=int,default=4)
    ap.add_argument('--layers',default=DEFAULT_LAYERS)
    ap.add_argument('--max-name-tokens',type=int,default=8)
    ap.add_argument('--seed',type=int,default=351)
    ap.add_argument('--plan-only',action='store_true')
    ap.add_argument('--cpu-offload',action='store_true',help='Keep BF16 and place some transformer layers on CPU RAM')
    ap.add_argument('--gpu-memory',default='33GiB',help='HF device_map GPU memory limit')
    ap.add_argument('--gpu-layers',type=int,default=29,help='GPU-resident transformer blocks; keep final norm and lm_head on GPU')
    ap.add_argument('--cpu-memory',default='45GiB',help='HF device_map CPU memory limit')
    args=ap.parse_args()
    if args.n<1:ap.error('--n must be >=1')
    layers=[int(s) for s in args.layers.split(',')]
    if len(set(layers))!=len(layers) or not layers or not all(0<=x<=62 for x in layers):ap.error('layers must be distinct 0..62')
    import transformers
    tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV,local_files_only=False)
    with open(args.data,encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    sequence=select_papers(rows,args.seed)
    # Planning can be costly because of author matching; only plan first n eligible.
    plans=[]
    for row in sequence:
        pair=choose_pair(row,rows,tok,args.max_name_tokens)
        if pair:plans.append(pair)
        if len(plans)>=args.n:break
    if len(plans)<args.n:raise RuntimeError(f'Could prepare only {len(plans)} / {args.n} pairs')
    data_sha=hashlib.sha256(Path(args.data).read_bytes()).hexdigest()
    config={'protocol':'author_prefix_teacher_forcing_v1','model':MODEL,'revision':REV,'lens':str(Path(args.lens).resolve()),'data_sha':data_sha,'layers':layers,'seed':args.seed,'max_name_tokens':args.max_name_tokens,'scoring':'mean token logprob; strict prefix token id match; one author pair per paper'}
    print('Prepared',len(plans),'papers; names lengths:',[(len(x['gold']['ids']),len(x['false']['ids'])) for x in plans],flush=True)
    if args.plan_only:
        for p in plans:print(p['paper']['paper_id'],p['paper']['citation_bin'],p['gold_name'],'VS',p['false_name'])
        return
    import torch,jlens
    if not torch.cuda.is_available():raise RuntimeError('CUDA GPU allocation required')
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    done=set()
    if out.exists():
        for line in out.read_text().splitlines():
            if not line.strip():continue
            r=json.loads(line)
            if r['config']!=config:raise RuntimeError('Existing output config differs. Use a new --output.')
            if r['paper_id'] in done:raise RuntimeError('Duplicate saved paper')
            done.add(r['paper_id'])
    if all(p['paper']['paper_id'] in done for p in plans):summary(out,layers);return
    print('Loading public lens...',flush=True)
    lens=jlens.JacobianLens.load(args.lens)
    if lens.d_model!=5120 or not set(layers).issubset(set(lens.source_layers)):raise RuntimeError('Lens dimensions/layers mismatch')
    print('Loading Qwen3-32B...',flush=True)
    if args.cpu_offload:
        # Crucial: jlens.hf.unembed calls final norm and lm_head OUTSIDE the
        # full model forward. With auto placement they end up as meta tensors
        # (Accelerate hooks cannot retrieve the weights for this direct call).
        # Pin BOTH to GPU and explicitly offload only transformer blocks.
        if not (1 <= args.gpu_layers <= 63):
            raise ValueError('--gpu-layers must be between 1 and 63')
        dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
        dm.update({f'model.layers.{i}':(0 if i<args.gpu_layers else 'cpu') for i in range(64)})
        print('BF16 explicit CPU offload; GPU blocks',args.gpu_layers,'CPU blocks',64-args.gpu_layers,flush=True)
        load_args={'device_map':dm,'low_cpu_mem_usage':True}
    else:
        load_args={'device_map':'cuda','low_cpu_mem_usage':True}
    hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,**load_args).eval()
    if args.cpu_offload:
        print('Device map:',getattr(hf,'hf_device_map',None),flush=True)
    model=jlens.from_hf(hf,tok)
    for idx,p in enumerate(plans,1):
        row=p['paper']
        if row['paper_id'] in done:
            print('SKIP already completed',row['paper_id'],flush=True);continue
        t0=time.perf_counter();torch.cuda.reset_peak_memory_stats()
        # Cache shared prefix evaluations, apply twice because vanilla comparison is needed.
        measurements={'gold':{},'false':{}};cache={}
        for label in ('gold','false'):
            plan=p[label]
            for j,(prompt,target) in enumerate(plan['contexts']):
                if prompt not in cache:
                    jlogs,actual,ids=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=512,use_jacobian=True)
                    vlogs,actual2,ids2=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=512,use_jacobian=False)
                    if not torch.equal(ids.cpu(),ids2.cpu()) or (actual-actual2).abs().max().item()>0.1:raise RuntimeError('Paired output mismatch')
                    cache[prompt]=({'final':actual[0]}|{f'jlens_L{x}':jlogs[x][0] for x in layers}|{f'vanilla_L{x}':vlogs[x][0] for x in layers})
                for mode,vec in cache[prompt].items():measurements[label].setdefault(mode,[]).append(score(vec,target))
        processed={}
        for mode in measurements['gold']:
            processed[mode]={}
            for label in ('gold','false'):
                items=measurements[label][mode]
                processed[mode][label]={'tokens':items,'num_tokens':len(items),'first_rank':items[0]['rank'],'first_logprob':items[0]['logprob'],'mean_reciprocal_rank':statistics.mean(1/x['rank'] for x in items),'mean_logprob':statistics.mean(x['logprob'] for x in items),'sum_logprob':sum(x['logprob'] for x in items)}
            processed[mode]['gold_minus_false_mean_logprob']=processed[mode]['gold']['mean_logprob']-processed[mode]['false']['mean_logprob']
        result={'paper_id':row['paper_id'],'group_label_for_reference_only':row.get('group_351'),'citation_bin':row['citation_bin'],'title':row['title'],'gold_author':p['gold_name'],'false_author':p['false_name'],'false_source_paper_id':p['false_source'],'gold_token_ids':p['gold']['ids'],'false_token_ids':p['false']['ids'],'measurements':processed,'seconds':round(time.perf_counter()-t0,3),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,3),'config':config}
        with out.open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        print(f'{idx}/{len(plans)} {row["paper_id"][:9]} {result["seconds"]:.1f}s peak={result["peak_gpu_gib"]:.2f}GiB L32full_delta={processed.get("jlens_L32",processed[f"jlens_L{layers[0]}"])["gold_minus_false_mean_logprob"]:.3f}',flush=True)
        cache.clear()
    summary(out,layers)
    print('Saved:',out,flush=True)

if __name__=='__main__':main()
