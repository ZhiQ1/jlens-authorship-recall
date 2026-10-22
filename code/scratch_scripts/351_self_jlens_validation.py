#!/usr/bin/env python3
"""Matched validation of locally fitted 100-prompt J-Lens against public Neuronpedia lens.
Modes: numerical, generic, paper, report, all. Held-out prompt sets and metrics are IDENTICAL
 to 351_public_lens_fidelity.py and 351_paper_prompt_fidelity_offload.py. No fitting here.
Split-half requires TWO independently fitted 50-prompt lenses; NOT asserted here.
"""
import argparse,csv,hashlib,importlib.util,json,math,os,random,statistics,time
from collections import defaultdict
from pathlib import Path
MODEL='Qwen/Qwen3-32B'; REV='9216db5781bf21249d130ec9da846c4624c16137'
LAYERS=[24,32,40,48,56,62]
BINS=['0-2','3-4','5-8','9-16','17-32','33-64','65-128','129-256','257-512','513-1024','1025-2048','2049-4096','4097+']
PROMPTS=[
'Explain why a bicycle remains easier to balance while moving than while standing still.\nAnswer:',
'A library is organizing returned books by subject and author. Describe a sensible procedure.\nAnswer:',
'In a distributed computing system, a request may wait for one slow server. Explain the resulting latency problem.\nAnswer:',
'A farmer observes that tomatoes grow poorly when the soil stays waterlogged. Give a biological explanation.\nAnswer:',
'Describe the role of a checksum when transferring a file between two computers.\nAnswer:',
'Why does a metal spoon feel colder than a wooden spoon at the same room temperature?\nAnswer:',
'A train arrives every fifteen minutes. Explain how a traveler could estimate the expected waiting time.\nAnswer:',
'Summarize how sediment accumulates at the bottom of a river delta.\nAnswer:',
'Explain the distinction between a database transaction and a database query.\nAnswer:',
'In an orchestra, why must musicians coordinate rhythm even when playing different notes?\nAnswer:',
'Describe a method for testing whether a new algorithm is faster on large datasets.\nAnswer:',
'How do ocean currents influence coastal temperatures?\nAnswer:',
'Explain what happens to network throughput when packet loss becomes frequent.\nAnswer:',
'Describe the basic purpose of error-correcting codes in digital communication.\nAnswer:',
'Why might a desert become cold shortly after sunset despite being very hot during the day?\nAnswer:',
'A city adds dedicated bus lanes. Explain one possible effect on traffic patterns.\nAnswer:',
'Compare the roles of producers and consumers in an ecosystem.\nAnswer:',
'How does a compiler differ from an interpreter when processing source code?\nAnswer:',
'Explain why repeated measurements are useful in a scientific experiment.\nAnswer:',
'Describe how a telescope collects light from distant astronomical objects.\nAnswer:',
]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def paper_select(rows,seed=74219):
 rng=random.Random(seed);buckets=defaultdict(list)
 for row in rows:
  if row.get('title','').strip() and row.get('year','').strip() and row.get('paper_id','').strip():buckets[row['citation_bin']].append(row)
 for v in buckets.values():rng.shuffle(v)
 selected=[]
 while any(buckets.values()):
  for b in BINS:
   if buckets[b]:selected.append(buckets[b].pop())
 return selected
def plan_paper(data,n):
 with open(data,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 selected=paper_select(rows)[:n]
 return [{'id':r['paper_id'],'prompt':f'Who are the authors of the paper titled "{r["title"]}" ({r["year"]})?\nAuthors:','title':r['title'],'year':r['year'],'citation_bin':r['citation_bin']} for r in selected]
def plans(data,n,which):
 return [{'id':str(i),'prompt':p} for i,p in enumerate(PROMPTS[:n])] if which=='generic' else plan_paper(data,n)
def metric(a,b):
 import torch
 a=a.float().flatten().cpu();b=b.float().flatten().cpu()
 if a.shape!=b.shape or not bool(torch.isfinite(a).all()) or not bool(torch.isfinite(b).all()):raise ValueError('Invalid logits')
 k=min(10,a.numel()); ta=torch.topk(a,k).indices;tb=torch.topk(b,k).indices
 loga=torch.log_softmax(a,-1);logb=torch.log_softmax(b,-1)
 rank=int((a>a[tb[0]]).sum().item())+1
 return {'top1_agree':int(ta[0]==tb[0]),'top10_overlap':len(set(ta.tolist())&set(tb.tolist()))/k,'kl_final_to_lens_nats':float((logb.exp()*(logb-loga)).sum().item()),'final_top1_rank':rank,'final_top1_reciprocal_rank':1/rank}
def load_existing(file,which):
 d={}
 if not Path(file).exists():return d
 for line in Path(file).read_text().splitlines():
  if not line.strip():continue
  r=json.loads(line); k=str(r['prompt_index']) if which=='generic' else r['paper_id'];d[k]=r
 return d
def numerical(args):
 import torch,jlens
 lens=jlens.JacobianLens.load(args.lens)
 if lens.d_model!=5120 or sorted(lens.source_layers)!=LAYERS:raise RuntimeError(f'Source layers mismatch: {lens.source_layers}')
 results=[]
 for l in LAYERS:
  j=lens.jacobians[l].float().cpu()
  rec={'layer':l,'shape':list(j.shape),'dtype':str(j.dtype),'finite':bool(torch.isfinite(j).all()),'min':float(j.min()),'max':float(j.max()),'mean':float(j.mean()),'std':float(j.std()),'fro_norm':float(torch.linalg.vector_norm(j)),'max_abs':float(j.abs().max())}
  results.append(rec)
 if not all(r['finite'] and r['shape']==[5120,5120] for r in results):raise RuntimeError('Numerical check failed')
 p=args.out/'numerical';p.mkdir(parents=True,exist_ok=True)
 (p/'matrices.json').write_text(json.dumps({'lens_sha256':sha(args.lens),'n_fit_prompts':lens.n_prompts,'source_layers':list(lens.source_layers),'results':results},indent=2))
 with (p/'matrices.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
 print('NUMERICAL PASSED',len(results),'matrices; fitted prompts=',lens.n_prompts)
def validate(args,which):
 import torch,transformers,jlens
 requested=plans(args.data,args.n,which);output=args.out/'raw'/f'{which}.jsonl';output.parent.mkdir(parents=True,exist_ok=True)
 config={'protocol':'self100_matched_v1','mode':which,'model':MODEL,'revision':REV,'lens_sha256':sha(args.lens),'layers':LAYERS,'data_sha':sha(args.data) if which=='paper' else None,'seed':74219 if which=='paper' else None,'max_seq_len':128 if which=='generic' else 512,'prompt_source':'EXACT previous 20 generic authored prompts' if which=='generic' else 'EXACT previous paper selection seed 74219'}
 done={}
 if output.exists():
  for line in output.read_text().splitlines():
   if not line.strip():continue
   r=json.loads(line)
   if r['config']!=config:raise RuntimeError('Incompatible previous run; use fresh --out')
   if r['id'] in done:raise RuntimeError('Duplicate saved ID')
   done[r['id']]=r
 print(which,'planned',len(requested),'complete',len(done),flush=True)
 for i,p in enumerate(requested):print(i+1,p['id'][:12],p['prompt'][:90].replace('\n',' | '),flush=True)
 if all(p['id'] in done for p in requested):return
 if not torch.cuda.is_available():raise RuntimeError('CUDA required')
 lens=jlens.JacobianLens.load(args.lens)
 if lens.d_model!=5120 or sorted(lens.source_layers)!=LAYERS:raise RuntimeError('Lens is not the 6-layer fitted checkpoint')
 tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV)
 dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
 dm.update({f'model.layers.{i}':(0 if i<args.gpu_layers else 'cpu') for i in range(64)})
 hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()
 model=jlens.from_hf(hf,tok)
 for i,p in enumerate(requested,1):
  if p['id'] in done:print('SKIP',p['id'][:12]);continue
  t0=time.perf_counter();torch.cuda.reset_peak_memory_stats()
  with torch.inference_mode():
   j,final,ids=lens.apply(model,p['prompt'],layers=LAYERS,positions=[-1],max_seq_len=config['max_seq_len'],use_jacobian=True)
   v,final2,ids2=lens.apply(model,p['prompt'],layers=LAYERS,positions=[-1],max_seq_len=config['max_seq_len'],use_jacobian=False)
  if not torch.equal(ids.cpu(),ids2.cpu()):raise RuntimeError('Paired input token IDs mismatch')
  if int(ids.numel()) >= config['max_seq_len']:raise RuntimeError('Prompt may have been truncated: do not silently compare')
  diff=float((final.float()-final2.float()).abs().max().item())
  if not math.isfinite(diff) or diff>0.1:raise RuntimeError(f'Paired final logits differ {diff}')
  ms={str(l):{'jlens':metric(j[l][-1],final[-1]),'vanilla':metric(v[l][-1],final[-1])} for l in LAYERS}
  record={'id':p['id'],'prompt':p['prompt'],'paper_metadata':{k:v for k,v in p.items() if k not in ('id','prompt')},'token_count':int(ids.numel()),'metrics':ms,'final_forward_max_delta':diff,'seconds':round(time.perf_counter()-t0,2),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,2),'config':config}
  with output.open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
  done[p['id']]=record
  print(f'{i}/{len(requested)} {p["id"][:12]} t={record["seconds"]:.1f}s peak={record["peak_gpu_gib"]:.2f}GiB L32KL={ms["32"]["jlens"]["kl_final_to_lens_nats"]:.3f}',flush=True)
 print('Saved',output)
def plot_and_report(args):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 summary=args.out/'summary';fig=args.out/'figures';report=args.out/'reports'
 for p in (summary,fig,report):p.mkdir(parents=True,exist_ok=True)
 old_files={'generic':args.public_generic,'paper':args.public_paper}
 report_lines=['# Qwen3-32B — Self-fitted J-Lens (100 prompts) vs Neuronpedia','',f'- Model: {MODEL}, pinned revision `{REV}`','- Source layers: 24, 32, 40, 48, 56, 62; target layer: 63.','- Self lens fitted on 100 generic WikiText prompts. Comparison uses only common 6 source layers.','- Only matched evaluation items, prompts, model and metric definitions are compared.','- Split-half stability: **NOT RUN**; requires independent 50+50 fits.','- Gold-vs-False Author Pilot: **NOT PART OF THIS SCRIPT** (requires matched task scorer; do not mislabel Fidelity).','']
 aggregate=[]; paired=[]
 for which in ('generic','paper'):
  path=args.out/'raw'/f'{which}.jsonl'
  if not path.exists():report_lines.append(f'## {which}: NOT RUN');continue
  rows=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
  if not rows:continue
  old=load_existing(old_files[which],which)
  report_lines.extend([f'## {which.title()} Fidelity',f'- Self evaluated items: {len(rows)}; public records available: {len(old)}',''])
  for l in LAYERS:
   for mode in ('jlens','vanilla'):
    for metric_name in ('kl_final_to_lens_nats','top1_agree','top10_overlap','final_top1_rank','final_top1_reciprocal_rank'):
     scores=[r['metrics'][str(l)][mode][metric_name] for r in rows]
     aggregate.append({'task':which,'lens':'self100' if mode=='jlens' else 'vanilla','layer':l,'metric':metric_name,'mean':statistics.mean(scores),'n':len(scores)})
   pairs=[]
   for r in rows:
    if r['id'] not in old:continue
    pub=old[r['id']]
    if pub['prompt']!=r['prompt']:raise RuntimeError(f'Mismatched prompts: {which} {r["id"]}')
    if pub.get('model_revision',pub.get('config',{}).get('revision'))!=REV:raise RuntimeError('Model revision mismatch public/self')
    if [int(x) for x in pub.get('layers', pub.get('config',{}).get('layers',[]))] and not set(LAYERS).issubset(set(pub.get('layers',pub.get('config',{}).get('layers',[])))):raise RuntimeError('Public data missing one of the six matched layers')
    if which=='generic' and pub.get('prompt_index')!=int(r['id']):raise RuntimeError('Public generic index mismatch')
    if which=='paper' and pub.get('paper_id')!=r['id']:raise RuntimeError('Public paper id mismatch')
    if which=='paper' and pub.get('config',{}).get('seed')!=74219:raise RuntimeError('Public paper sample seed mismatch')
    if which=='paper' and pub.get('config',{}).get('data_sha')!=sha(args.data):raise RuntimeError('Public paper data checksum mismatch')
    for met in ('kl_final_to_lens_nats','top1_agree','top10_overlap','final_top1_rank','final_top1_reciprocal_rank'):
     own=r['metrics'][str(l)]['jlens'][met];out=(1.0/pub['metrics'][str(l)]['jlens']['final_top1_rank'] if met=='final_top1_reciprocal_rank' and met not in pub['metrics'][str(l)]['jlens'] else pub['metrics'][str(l)]['jlens'][met])
     paired.append({'task':which,'item_id':r['id'],'layer':l,'metric':met,'self100':own,'neuronpedia':out,'difference_self_minus_public':own-out})
    for met in ('kl_final_to_lens_nats','top1_agree','top10_overlap','final_top1_rank'):
     a=r['metrics'][str(l)]['vanilla'][met];b=pub['metrics'][str(l)]['vanilla'][met]
     if abs(a-b)> (0.2 if met=='kl_final_to_lens_nats' else (2 if met=='final_top1_rank' else 0.01)):
      raise RuntimeError(f'Vanilla control mismatch at {which} {r["id"]} L{l} {met}: {a} vs {b}; check same model/prompt and device numeric behavior')
    pairs.append(r['id'])
   if not pairs:report_lines.append(f'- L{l}: No exact prompt matches with public result.');continue
  nmatched=len(set(x['item_id'] for x in paired if x['task']==which))
  report_lines.append(f'- Exact matched public comparison items: {nmatched} (out of {len(rows)})')
  if nmatched != len(rows):report_lines.append('- **WARNING:** unmatched examples excluded from paired comparisons; not a complete matched evaluation.')
  report_lines.append('')
 with (summary/'metrics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['task','lens','layer','metric','mean','n']);w.writeheader();w.writerows(aggregate)
 with (summary/'paired_self_vs_public.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['task','item_id','layer','metric','self100','neuronpedia','difference_self_minus_public']);w.writeheader();w.writerows(paired)
 rng=random.Random(3512026)
 ci=[]
 for task in ('generic','paper'):
  for l in LAYERS:
   for met in ('kl_final_to_lens_nats','top10_overlap','final_top1_reciprocal_rank'):
    vals=[x['difference_self_minus_public'] for x in paired if x['task']==task and x['layer']==l and x['metric']==met]
    if not vals:continue
    boots=sorted(statistics.mean(rng.choices(vals,k=len(vals))) for _ in range(2000))
    ci.append({'task':task,'layer':l,'metric':met,'n_matched':len(vals),'mean_delta_self_minus_public':statistics.mean(vals),'ci95_low':boots[49],'ci95_high':boots[1949]})
 with (summary/'paired_bootstrap_ci.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['task','layer','metric','n_matched','mean_delta_self_minus_public','ci95_low','ci95_high']);w.writeheader();w.writerows(ci)
 for task in ('generic','paper'):
  for met,title in [('kl_final_to_lens_nats','KL(Final || Lens) — lower is better'),('final_top1_reciprocal_rank','RR of final top-1 — higher is better'),('top10_overlap','Top-10 overlap — higher is better')]:
   fig1,ax=plt.subplots(figsize=(8,4.6));had=False
   for mode,color in [('self100','#155c9c'),('neuronpedia','#c35a49'),('vanilla','#777777')]:
    if mode=='neuronpedia':
     points=[(l,statistics.mean(x['neuronpedia'] for x in paired if x['task']==task and x['layer']==l and x['metric']==met)) for l in LAYERS if any(x['task']==task and x['layer']==l and x['metric']==met for x in paired)]
    elif mode=='self100':
     points=[(x['layer'],x['mean']) for x in aggregate if x['task']==task and x['lens']=='self100' and x['metric']==met]
    else:
     points=[(x['layer'],x['mean']) for x in aggregate if x['task']==task and x['lens']=='vanilla' and x['metric']==met]
    if points:
     ax.plot([p[0] for p in points],[p[1] for p in points],marker='o',color=color,label=mode);had=True
   if had:
    ax.set_title(f'{task.title()} — {title}');ax.set_xlabel('Source layer');ax.set_ylabel(met);ax.grid(alpha=.22);ax.legend();fig1.tight_layout()
    for ext in ('png','pdf'):fig1.savefig(fig/f'{task}_{met}.{ext}',dpi=180)
   plt.close(fig1)

 # Fourth (task pilot) matching, only if the SAME 20 paper IDs and candidate names were scored with both lenses.
 public_author=Path(args.public_author);self_author=Path(args.self_author)
 if public_author.exists() and self_author.exists():
  pubrows={r['paper_id']:r for r in (json.loads(z) for z in public_author.read_text().splitlines() if z.strip())}
  selfrows={r['paper_id']:r for r in (json.loads(z) for z in self_author.read_text().splitlines() if z.strip())}
  pa=[]
  for pid,r in selfrows.items():
   if pid not in pubrows:continue
   u=pubrows[pid]
   for field in ('gold_author','false_author','false_source_paper_id','gold_token_ids','false_token_ids'):
    if r[field]!=u[field]:raise RuntimeError(f'Author control mismatch {pid} {field}')
   for l in LAYERS:
    for mode in ('jlens','vanilla'):
     key=f'{mode}_L{l}'
     for field in ('first_logprob','mean_logprob'):
      for who in ('gold','false'):
       aa=r['measurements'][key][who][field];bb=u['measurements'][key][who][field]
       pa.append({'paper_id':pid,'layer':l,'mode':mode,'which':who,'metric':field,'self100':aa,'neuronpedia':bb,'delta_self_minus_public':aa-bb})
  if pa:
   with (summary/'author_pilot_paired.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(pa[0]));w.writeheader();w.writerows(pa)
   report_lines.append(f'## Gold-vs-False task pilot: paired {len(set(x["paper_id"] for x in pa))} papers; score comparison exported to `summary/author_pilot_paired.csv`. Not an independent fidelity validation.')
  else:report_lines.append('## Gold-vs-False task pilot: No overlapping completed papers; NOT RUN as comparison.')
 else:
  report_lines.append('## Gold-vs-False task pilot: NOT RUN for both lenses yet. Use `351_validate_public_lens_offload_fixed.py` with the same seed, names, prompts and six shared layers for the self-fit lens.')

 report_lines.extend(['## Interpretation boundaries','- Numerical finite matrices do not prove readout fidelity.','- Compare only six shared layers and exact same examples. Generic and Paper are separately evaluated.','- MRR and KL may disagree; neither certifies hidden factual knowledge.','- 20 prompts per task yield exploratory rather than conclusive uncertainty estimates.','- A gold-vs-false author pilot is not an independent fidelity standard.','- Published Neuronpedia fitting dataset overlaps WikiText provenance; exact fit/eval overlap is unverified, so do not claim universally held-out evaluation.','', '## Outputs','- `numerical/matrices.csv`, `numerical/matrices.json`','- `raw/generic.jsonl`, `raw/paper.jsonl`','- `summary/metrics.csv`, `summary/paired_self_vs_public.csv`, `summary/paired_bootstrap_ci.csv`','- `figures/*.png`, `figures/*.pdf`',''])
 (report/'comparison_report.md').write_text('\n'.join(report_lines),encoding='utf-8')
 print('REPORT',report/'comparison_report.md','matched comparisons',len(paired))
def main():
 root=f'/scratch/{os.environ.get("USER","unknown")}/jlens'
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--mode',choices=['numerical','generic','paper','report','all'],default='numerical')
 ap.add_argument('--lens',default=f'{root}/qwen32b_jlens_prelim_100.pt')
 ap.add_argument('--data',default=f'{root}/351_all/351_four_groups.csv')
 ap.add_argument('--public-generic',default=f'{root}/351_all/351_public_fidelity.jsonl')
 ap.add_argument('--public-paper',default=f'{root}/351_all/351_paper_prompt_fidelity.jsonl')
 ap.add_argument('--self-author',default=f'{root}/351_self100_author_pilot.jsonl')
 ap.add_argument('--public-author',default=f'{root}/351_all/351_offload_fixed_validation.jsonl')
 ap.add_argument('--out',type=Path,default=Path(f'{root}/351_self100_validation'))
 ap.add_argument('--n',type=int,default=20)
 ap.add_argument('--gpu-layers',type=int,default=29)
 ap.add_argument('--plan-only',action='store_true')
 a=ap.parse_args()
 if not 1<=a.n<=20:ap.error('--n must be between 1 and 20 for matched validation')
 a.out.mkdir(parents=True,exist_ok=True)
 if a.plan_only:
  for m in (['generic','paper'] if a.mode=='all' else [a.mode]):
   if m in ('generic','paper'):
    for p in plans(a.data,a.n,m):print(m,p['id'],p['prompt'][:90].replace('\n',' | '))
  return
 if a.mode in ('numerical','all'):numerical(a)
 if a.mode in ('generic','all'):validate(a,'generic')
 if a.mode in ('paper','all'):validate(a,'paper')
 if a.mode in ('report','all'):plot_and_report(a)
if __name__=='__main__':main()
