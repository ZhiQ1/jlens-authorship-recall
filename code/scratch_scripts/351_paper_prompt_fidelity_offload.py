#!/usr/bin/env python3
"""Held-out paper-PROMPT J-Lens fidelity (no author labels, no hypothesis testing).
Qwen3-32B BF16 on A100-40GB with CPU-layer offload; compares predictions to final logits.
"""
import argparse, csv, hashlib, json, math, os, random, statistics, time
from collections import defaultdict
from pathlib import Path

MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
BINS=['0-2','3-4','5-8','9-16','17-32','33-64','65-128','129-256','257-512','513-1024','1025-2048','2049-4096','4097+']

def select(rows, seed):
    rng=random.Random(seed)
    buckets=defaultdict(list)
    for row in rows:
        if row.get('title','').strip() and row.get('year','').strip() and row.get('paper_id','').strip():
            buckets[row['citation_bin']].append(row)
    for v in buckets.values():rng.shuffle(v)
    selected=[]
    while any(buckets.values()):
        for b in BINS:
            if buckets[b]:selected.append(buckets[b].pop())
    return selected

def prompt_for(r):
    return f'Who are the authors of the paper titled "{r["title"]}" ({r["year"]})?\nAuthors:'

def metric(candidate, final):
    import torch
    a=candidate.float().reshape(-1).cpu(); b=final.float().reshape(-1).cpu()
    if a.shape!=b.shape or not bool(torch.isfinite(a).all()) or not bool(torch.isfinite(b).all()):
        raise ValueError('Nonfinite or mismatched logits')
    k=min(10,a.numel());ta=torch.topk(a,k).indices;tb=torch.topk(b,k).indices
    loga=torch.log_softmax(a,-1);logb=torch.log_softmax(b,-1)
    return {'top1_agree':int(ta[0]==tb[0]),'top10_overlap':len(set(ta.tolist())&set(tb.tolist()))/k,'kl_final_to_lens_nats':float(torch.sum(logb.exp()*(logb-loga)).item()),'final_top1_rank':int((a>a[tb[0]]).sum().item())+1, 'final_top1_reciprocal_rank':1.0/(int((a>a[tb[0]]).sum().item())+1)}

def report(rows,layers):
    print('===== PAPER PROMPT FIDELITY SUMMARY =====',len(rows),'papers',flush=True)
    for l in layers:
        for mode in ('jlens','vanilla'):
            x=[r['metrics'][str(l)][mode] for r in rows]
            if not x:continue
            avg=lambda k:statistics.mean(d[k] for d in x)
            print(f'L{l:02d} {mode:<7} Top1={avg("top1_agree"):.3f} Top10Overlap={avg("top10_overlap"):.3f} KL={avg("kl_final_to_lens_nats"):.3f} MRR_finalTop1={avg("final_top1_reciprocal_rank"):.4f} AvgRank={avg("final_top1_rank"):.1f}',flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    root=f'/scratch/{os.environ.get("USER","unknown")}/jlens'
    ap.add_argument('--data',default=f'{root}/351_all/351_four_groups.csv')
    ap.add_argument('--lens',default=f'{root}/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
    ap.add_argument('--output',default=f'{root}/351_all/351_paper_prompt_fidelity.jsonl')
    ap.add_argument('--n',type=int,default=4)
    ap.add_argument('--layers',default='16,24,32,40,48,56,62')
    ap.add_argument('--gpu-layers',type=int,default=29)
    ap.add_argument('--seed',type=int,default=74219)
    ap.add_argument('--max-seq-len',type=int,default=512)
    ap.add_argument('--plan-only',action='store_true')
    args=ap.parse_args()
    layers=[int(a) for a in args.layers.split(',')]
    if args.n<1 or not 1<=args.gpu_layers<=63 or not layers or len(layers)!=len(set(layers)) or not all(0<=x<=62 for x in layers):ap.error('invalid n, layers, or gpu-layers')
    with open(args.data,encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    selection=select(rows,args.seed)
    if len(selection)<args.n:ap.error('Not enough papers')
    plans=selection[:args.n]
    print('Prepared paper prompts:',len(plans),flush=True)
    for i,r in enumerate(plans):print(f'{i+1:>3} {r["paper_id"][:12]} bin={r["citation_bin"]} title={r["title"][:85]}',flush=True)
    if args.plan_only:return
    import torch,transformers,jlens
    if not torch.cuda.is_available():raise RuntimeError('CUDA GPU required')
    data_hash=hashlib.sha256(Path(args.data).read_bytes()).hexdigest()
    config={'protocol':'paper_prompt_fidelity_v1','model':MODEL,'revision':REV,'lens':str(Path(args.lens).resolve()),'data_sha':data_hash,'seed':args.seed,'layers':layers,'max_seq_len':args.max_seq_len,'prompt_template':'Who are the authors of the paper titled "{title}" ({year})?\\nAuthors:','metric':'KL(P_final || P_lens), top1/top10, final top1 rank'}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    done={}
    if out.exists():
        for line in out.read_text().splitlines():
            if not line.strip():continue
            r=json.loads(line)
            if r['config']!=config:raise RuntimeError('Output contains different configuration; use another --output file')
            if r['paper_id'] in done:raise RuntimeError('Duplicate saved paper ID')
            done[r['paper_id']]=r
    if all(r['paper_id'] in done for r in plans):
        report([done[r['paper_id']] for r in plans],layers);return
    print('Loading pretrained public J-Lens...',flush=True)
    lens=jlens.JacobianLens.load(args.lens)
    if lens.d_model!=5120 or not set(layers).issubset(set(lens.source_layers)):raise RuntimeError('Lens architecture mismatch')
    tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV)
    dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
    dm.update({f'model.layers.{i}':(0 if i<args.gpu_layers else 'cpu') for i in range(64)})
    print(f'Loading Qwen3-32B BF16: {args.gpu_layers} blocks GPU, {64-args.gpu_layers} CPU; final norm/head on GPU',flush=True)
    hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()
    model=jlens.from_hf(hf,tok)
    print('Model loaded. Performing paired final-logit checks...',flush=True)
    for i,r in enumerate(plans,1):
        pid=r['paper_id']
        if pid in done:print('SKIP',i,pid[:12],flush=True);continue
        prompt=prompt_for(r)
        t0=time.perf_counter();torch.cuda.reset_peak_memory_stats()
        with torch.inference_mode():
            j,final,ids=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=args.max_seq_len,use_jacobian=True)
            v,final2,ids2=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=args.max_seq_len,use_jacobian=False)
        if not torch.equal(ids.cpu(),ids2.cpu()):raise RuntimeError('Input mismatch between forward passes')
        diff=float((final.float()-final2.float()).abs().max().item())
        if not math.isfinite(diff) or diff>0.1:raise RuntimeError(f'Final logits changed between paired passes, maxdiff={diff}')
        metrics={str(l):{'jlens':metric(j[l][-1],final[-1]),'vanilla':metric(v[l][-1],final[-1])} for l in layers}
        rec={'paper_id':pid,'title':r['title'],'year':r['year'],'citation_bin':r['citation_bin'],'prompt':prompt,'tokens_in_prompt':int(ids.numel()),'metrics':metrics,'final_forward_max_delta':diff,'seconds':round(time.perf_counter()-t0,2),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,2),'config':config}
        with out.open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        print(f'{i}/{len(plans)} {pid[:12]} {rec["seconds"]:.1f}s {rec["peak_gpu_gib"]:.2f}GiB L32_KL_J={metrics.get("32",metrics[str(layers[0])])["jlens"]["kl_final_to_lens_nats"]:.3f}',flush=True)
        done[pid]=rec
        del j,v,final,final2,ids,ids2
    report([done[r['paper_id']] for r in plans],layers)
    print('Saved:',out,flush=True)
if __name__=='__main__':main()
