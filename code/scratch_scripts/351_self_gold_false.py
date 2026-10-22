#!/usr/bin/env python3
"""Exact-paired Self-100 vs Neuronpedia authorship pilot.
Source of truth: existing public 20-paper results, including selected false authors.
No random re-selection, no changes to tokenization protocol. Saves full archive.
"""
import argparse,csv,hashlib,json,os,statistics,time,math,random
from pathlib import Path
from collections import defaultdict

MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
LAYERS=[24,32,40,48,56,62]

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def token_plan(tok,prompt,name,max_len):
 # EXACT original pilot protocol. Do not replace with stage4 forced-token protocol.
 base=tok.encode(prompt,add_special_tokens=False)
 full=tok.encode(prompt+' '+name,add_special_tokens=False)
 if len(full)<=len(base) or full[:len(base)]!=base:return None
 rest=full[len(base):]
 if len(rest)>max_len:return None
 contexts=[]
 for j,target in enumerate(rest):
  prefix=full[:len(base)+j]
  text=tok.decode(prefix,skip_special_tokens=False,clean_up_tokenization_spaces=False)
  if tok.encode(text,add_special_tokens=False)!=prefix:return None
  contexts.append((text,int(target)))
 return {'ids':rest,'contexts':contexts}

def measure(vec,tid):
 import torch
 x=vec.float().reshape(-1).cpu();z=x[int(tid)]
 if not torch.isfinite(x).all().item():raise ValueError('Nonfinite logits')
 return {'rank':int((x>z).sum().item())+1,'logprob':float(torch.log_softmax(x,-1)[int(tid)].item())}

def summarize_tokens(items):
 return {'tokens':items,'num_tokens':len(items),'first_rank':items[0]['rank'],'first_logprob':items[0]['logprob'],'mean_reciprocal_rank':statistics.mean(1/x['rank'] for x in items),'mean_logprob':statistics.mean(x['logprob'] for x in items),'sum_logprob':sum(x['logprob'] for x in items)}

def get_metric(record,layer,mode):
 return record['measurements'][f'{mode}_L{layer}']

def bootstrap(ds,seed=7351,n=5000):
 rng=random.Random(seed);means=[];n0=len(ds)
 for _ in range(n):means.append(sum(ds[rng.randrange(n0)] for __ in range(n0))/n0)
 means.sort();return means[int(.025*n)],means[min(n-1,int(.975*n))]

def archive(public_rows,self_rows,layers,dest,public_path,self_path):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 folders={x:dest/x for x in ('raw','summary','figures','reports','config')}
 for p in folders.values():p.mkdir(parents=True,exist_ok=True)
 byid={r['paper_id']:r for r in self_rows}
 pairs=[(r,byid[r['paper_id']]) for r in public_rows if r['paper_id'] in byid]
 raw_csv=[];pair_metrics=[];summary=[]
 for public,selfr in pairs:
  for l in layers:
   for lens_name,rec,key in [('self100',selfr,f'jlens_L{l}'),('neuronpedia',public,f'jlens_L{l}'),('vanilla',public,f'vanilla_L{l}'),('final',public,'final')]:
    m=rec['measurements'][key];g=m['gold'];f=m['false'];d=g['mean_logprob']-f['mean_logprob']
    pair_metrics.append({'paper_id':public['paper_id'],'layer':l,'lens':lens_name,'first_win':int(g['first_logprob']>f['first_logprob']),'full_win':int(d>0),'gold_minus_false_full_logprob':d,'gold_first_rank':g['first_rank'],'false_first_rank':f['first_rank'],'gold_first_rr':1/g['first_rank'],'false_first_rr':1/f['first_rank'],'gold_n_tokens':g['num_tokens'],'false_n_tokens':f['num_tokens']})
    for label in ('gold','false'):
     for pos,token in enumerate(m[label]['tokens']):
      raw_csv.append({'paper_id':public['paper_id'],'lens':lens_name,'layer':l,'author_type':label,'token_position':pos,'token_id':(rec['gold_token_ids'] if label=='gold' else rec['false_token_ids'])[pos],'rank':token['rank'],'logprob':token['logprob']})
 for l in layers:
  for name in ('self100','neuronpedia','vanilla','final'):
   sub=[r for r in pair_metrics if r['layer']==l and r['lens']==name]
   if not sub:continue
   summary.append({'layer':l,'lens':name,'n_pairs':len(sub),'first_win_rate':statistics.mean(r['first_win'] for r in sub),'full_win_rate':statistics.mean(r['full_win'] for r in sub),'mean_full_delta':statistics.mean(r['gold_minus_false_full_logprob'] for r in sub)})
 ci=[]
 for l in layers:
  x={r['paper_id']:r for r in pair_metrics if r['layer']==l and r['lens']=='self100'}
  y={r['paper_id']:r for r in pair_metrics if r['layer']==l and r['lens']=='neuronpedia'}
  common=sorted(set(x)&set(y))
  if not common:continue
  for name in ('first_win','full_win','gold_minus_false_full_logprob'):
   vals=[x[p][name]-y[p][name] for p in common]
   low,high=bootstrap(vals,seed=351+l)
   ci.append({'layer':l,'metric':name,'n_pairs':len(vals),'mean_self_minus_public':statistics.mean(vals),'ci95_low':low,'ci95_high':high})
 def writecsv(path,data):
  if not data:return
  with path.open('w',encoding='utf-8',newline='') as f:
   w=csv.DictWriter(f,data[0].keys());w.writeheader();w.writerows(data)
 writecsv(folders['raw']/'token_scores.csv',raw_csv)
 writecsv(folders['summary']/'per_paper_pair.csv',pair_metrics)
 writecsv(folders['summary']/'layer_summary.csv',summary)
 writecsv(folders['summary']/'paired_bootstrap_ci.csv',ci)
 (folders['summary']/'summary.json').write_text(json.dumps({'n_pairs':len(pairs),'layers':layers,'summary':summary,'paired_ci':ci},indent=2),encoding='utf-8')
 (folders['raw']/'self_results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for _,r in pairs),encoding='utf-8')
 (folders['config']/'comparison_config.json').write_text(json.dumps({'public_file':str(public_path),'public_sha256':digest(public_path),'self_file':str(self_path),'self_sha256':digest(self_path),'n_pairs':len(pairs),'layers':layers,'protocol':'reuse_original_public_pair_and_strict_tokenization_v1','fit100_model_revision':REV},indent=2),encoding='utf-8')
 for metric,ylabel,fname in [('full_win_rate','Gold > false fraction','full_name_win_rate'),('first_win_rate','Gold > false fraction','first_token_win_rate'),('mean_full_delta','Mean gold-minus-false log P','full_name_logprob_delta')]:
  fig,ax=plt.subplots(figsize=(7.2,4.2))
  for name in ('self100','neuronpedia','vanilla','final'):
   s=[r for r in summary if r['lens']==name]
   if name=='final':continue  # horizontal constant omitted from main plotted layer curves
   ax.plot([r['layer'] for r in s],[r[metric] for r in s],marker='o',label=name)
  fin=next((r for r in summary if r['lens']=='final'),None)
  if fin:ax.axhline(fin[metric],linestyle='--',alpha=.5,label='Final model')
  ax.set_xlabel('Source layer');ax.set_ylabel(ylabel);ax.set_xticks(layers);ax.legend(fontsize=9)
  ax.set_title('Exact matched 20-paper Gold vs False pilot')
  fig.tight_layout()
  for ext in ('.png','.pdf'):fig.savefig(folders['figures']/(fname+ext),dpi=180)
  plt.close(fig)
 report=['# Self-100 vs Neuronpedia — matched author pilot','',f'- Matched papers completed: {len(pairs)}/{len(public_rows)}','- **Same gold/false authors, same paper prompts, tokenizer protocol and model revision as original Neuronpedia pilot.**','- This is a task-specific discrimination pilot, not a standalone causal proof of factual knowledge.','- Primary metric: paired author full-name mean conditional log-probability difference (gold minus false).','- Tokens after first are teacher-forced. Name-frequency and first-listed position confounds remain.','', '## Layer-wise results','', '| Layer | Self full win | Public full win | Vanilla full win | Self ΔlogP | Public ΔlogP |','|---|---:|---:|---:|---:|---:|']
 for l in layers:
  m={r['lens']:r for r in summary if r['layer']==l}
  if all(k in m for k in ('self100','neuronpedia','vanilla')):report.append(f"| L{l} | {m['self100']['full_win_rate']:.3f} | {m['neuronpedia']['full_win_rate']:.3f} | {m['vanilla']['full_win_rate']:.3f} | {m['self100']['mean_full_delta']:+.3f} | {m['neuronpedia']['mean_full_delta']:+.3f} |")
 report += ['', '## Interpretation', '- A higher gold-win rate on this small, selected set is suggestive but not a fidelity certificate.','- Bootstrap intervals pair the **same papers**; compare their deltas with uncertainty.','- The Public lens original task pilot must NOT be confused with the 20-paper Paper-Prompt Fidelity test.','- This archive does not perform title shuffle or independent split-half stability.','- Outputs: raw JSONL/CSV, per-paper metrics, layer summary, paired bootstrap CI, PNG/PDF plots.']
 (folders['reports']/'comparison_report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
 print('ARCHIVE',dest,'paired',len(pairs),'of',len(public_rows),flush=True)
 for r in summary:
  if r['lens'] in ('self100','neuronpedia'):
   print(f"L{r['layer']} {r['lens']:<11} n={r['n_pairs']} first_win={r['first_win_rate']:.3f} full_win={r['full_win_rate']:.3f} full_delta={r['mean_full_delta']:+.3f}",flush=True)

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 root=Path('/scratch')/os.environ.get('USER','unknown')/'jlens'
 ap.add_argument('--public-results',default=str(root/'351_all/351_offload_fixed_validation.jsonl'))
 ap.add_argument('--lens',default=str(root/'qwen32b_jlens_prelim_100.pt'))
 ap.add_argument('--output',default=str(root/'351_self100_gold_false/self_results.jsonl'))
 ap.add_argument('--archive-dir',default=str(root/'351_self100_gold_false/archive'))
 ap.add_argument('--n',type=int,default=4)
 ap.add_argument('--gpu-layers',type=int,default=29)
 ap.add_argument('--max-name-tokens',type=int,default=8)
 ap.add_argument('--plan-only',action='store_true')
 ap.add_argument('--report-only',action='store_true')
 args=ap.parse_args()
 public_path=Path(args.public_results);out=Path(args.output);archive_dir=Path(args.archive_dir)
 if not public_path.exists():raise FileNotFoundError(f'Public reference JSONL missing: {public_path}')
 public=[json.loads(s) for s in public_path.read_text().splitlines() if s.strip()]
 if len(public)!=20:raise RuntimeError(f'Expected exactly 20 public records, got {len(public)}. Verify path and original run.')
 if len({r['paper_id'] for r in public})!=20:raise RuntimeError('Duplicate public paper_ids')
 if not 1<=args.n<=20:ap.error('n must be 1..20')
 layers=LAYERS
 for r in public:
  if r['config'].get('model')!=MODEL or r['config'].get('revision')!=REV:raise RuntimeError('Public model mismatch')
  if not set(layers).issubset(set(r['config']['layers'])):raise RuntimeError('Public missing required layer')
  if not all(k in r for k in ('gold_author','false_author','gold_token_ids','false_token_ids')):raise RuntimeError('Public record missing paired names/tokens')
 print('Reference public data:',len(public),'papers; target',args.n,'exact pairs',flush=True)
 if not args.report_only:
  import transformers
  tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV)
  plans=[]
  for r in public[:args.n]:
   prompt=f'Who are the authors of the paper titled "{r["title"]}" ({r["config"].get("year", "")})?\nAuthors:'
   # Recover exact prompt year from source CSV, rather than assuming it is in public record.
   plans.append({'ref':r})
  # Public source records may not retain year; CSV is required for exact prompt reconstruction.
  data=Path(root/'351_all/351_four_groups.csv')
  with data.open(encoding='utf-8-sig',newline='') as f:byid={r['paper_id']:r for r in csv.DictReader(f)}
  plans=[]
  for r in public[:args.n]:
   if r['paper_id'] not in byid:raise RuntimeError('Paper not in source data: '+r['paper_id'])
   row=byid[r['paper_id']]
   prompt=f'Who are the authors of the paper titled "{row["title"]}" ({row["year"]})?\nAuthors:'
   g=token_plan(tok,prompt,r['gold_author'],args.max_name_tokens)
   f=token_plan(tok,prompt,r['false_author'],args.max_name_tokens)
   if not g or not f:raise RuntimeError('Tokenizer mismatch for old paired author: '+r['paper_id'])
   if g['ids']!=r['gold_token_ids'] or f['ids']!=r['false_token_ids']:raise RuntimeError('Original token IDs changed; refusing unpaired evaluation: '+r['paper_id'])
   plans.append({'ref':r,'prompt':prompt,'gold':g,'false':f})
  print('Exact pair/token match PASS:',len(plans),'/',len(plans),flush=True)
  if args.plan_only:
   for p in plans:print(p['ref']['paper_id'][:12],p['ref']['gold_author'],'vs',p['ref']['false_author'],len(p['gold']['ids']),len(p['false']['ids']))
   return
  import torch,jlens
  if not torch.cuda.is_available():raise RuntimeError('Requires GPU; use --plan-only on CPU')
  out.parent.mkdir(parents=True,exist_ok=True)
  done={}
  if out.exists():
   for s in out.read_text().splitlines():
    if not s.strip():continue
    r=json.loads(s)
    if r['paper_id'] in done:raise RuntimeError('Duplicate output paper ID')
    if r['protocol']!='paired_self100_original_public_v1' or r['layers']!=layers or r['public_sha256']!=digest(public_path):raise RuntimeError('Resume config mismatch')
    done[r['paper_id']]=r
  if not all(p['ref']['paper_id'] in done for p in plans):
   print('Loading self-100 lens and BF16 Qwen3-32B',flush=True)
   lens=jlens.JacobianLens.load(args.lens)
   if not set(layers).issubset(set(lens.source_layers)) or lens.d_model!=5120:raise RuntimeError('Wrong self lens')
   dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
   dm.update({f'model.layers.{i}':(0 if i<args.gpu_layers else 'cpu') for i in range(64)})
   hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()
   model=jlens.from_hf(hf,tok)
   for idx,p in enumerate(plans,1):
    r=p['ref'];pid=r['paper_id']
    if pid in done:print('SKIP',idx,pid[:12],flush=True);continue
    t0=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    cache={}; processed={}
    for label in ('gold','false'):
     for context,target in p[label]['contexts']:
      if context not in cache:
       with torch.inference_mode():
        logits,fin,ids=lens.apply(model,context,layers=layers,positions=[-1],max_seq_len=512,use_jacobian=True)
       cache[context]={f'jlens_L{l}':logits[l][0].cpu() for l in layers}
      for mode,vec in cache[context].items():processed.setdefault(mode,{}).setdefault(label,[]).append(measure(vec,target))
    measurements={}
    for mode,labels in processed.items():
     measurements[mode]={lab:summarize_tokens(labels[lab]) for lab in ('gold','false')}
     measurements[mode]['gold_minus_false_mean_logprob']=measurements[mode]['gold']['mean_logprob']-measurements[mode]['false']['mean_logprob']
    record={'paper_id':pid,'title':r['title'],'gold_author':r['gold_author'],'false_author':r['false_author'],'gold_token_ids':p['gold']['ids'],'false_token_ids':p['false']['ids'],'measurements':measurements,'seconds':round(time.perf_counter()-t0,2),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,2),'protocol':'paired_self100_original_public_v1','public_sha256':digest(public_path),'layers':layers,'self_lens':str(Path(args.lens).resolve()),'revision':REV}
    with out.open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    done[pid]=record
    print(f'{idx}/{args.n} {pid[:12]} {record["seconds"]}s peak={record["peak_gpu_gib"]}GiB L32_delta={measurements["jlens_L32"]["gold_minus_false_mean_logprob"]:+.3f}',flush=True)
 public_sel=public[:args.n];byid={r['paper_id']:r for r in (json.loads(s) for s in out.read_text().splitlines() if s.strip())}
 archive(public_sel,[byid[r['paper_id']] for r in public_sel if r['paper_id'] in byid],layers,archive_dir,public_path,out)
 if args.report_only and len(byid)<args.n:print('Partial report:',len(byid),'of',args.n,flush=True)

if __name__=='__main__':main()
