#!/usr/bin/env python3
"""Stage 7.2 frozen candidate first-token GPU scorer & CPU analytics.
Run: python 351_stage7_2_score.py audit | run | analyze
Requires 351_stage5.py in same directory for the validated readout implementation.
Never changes candidate manifest/candidates or earlier stages.
"""
import argparse,csv,hashlib,importlib.util,json,math,os,statistics,sys,time
from pathlib import Path
from collections import Counter,defaultdict
LAYERS=[16,24,32,40,48,56,62]
PROMPT='Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'
REV='9216db5781bf21249d130ec9da846c4624c16137'
MODEL='Qwen/Qwen3-32B'

def jhash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def fhash(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def readcsv(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(p,rs):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rs:return
 keys=list(rs[0]);
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rs)
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');tmp.replace(p)
def inputs(a):
 root=Path(a.root);s5=Path(a.stage5_root);manifest_path=root/'config/manifest.json';manifest=json.loads(manifest_path.read_text())
 if manifest['protocol']!='stage7_2_candidate_freeze_v1' or manifest['scoring_plan']['layers']!=LAYERS:raise RuntimeError('Unrecognized frozen candidate protocol')
 for rel,digest in manifest['output_sha256'].items():
  p=root/rel
  if not p.is_file() or fhash(p)!=digest:raise RuntimeError('Frozen input modified: '+rel)
 for k,p in [('pilot50',s5/'cohort/pilot50_v1.csv'),('full6841',s5/'cohort/full_6841_manifest.csv')]:
  if fhash(p)!=manifest['input_sha256'][k]:raise RuntimeError('Frozen Stage5 inputs differ: '+k)
 cohort=readcsv(s5/'cohort/pilot50_v1.csv');by={r['paper_id']:r for r in cohort}
 if len(by)!=50 or Counter(r['group'] for r in cohort)!=Counter({'A':20,'B':20,'C':7,'D':3}):raise RuntimeError('Pilot cohort changed')
 candidate={}
 with (root/'candidates/pilot50_author_candidates.jsonl').open(encoding='utf-8') as f:
  for line in f:
   if not line.strip():continue
   x=json.loads(line);pid=x['paper_id']
   if pid in candidate or pid not in by:raise RuntimeError('Candidate duplicate/foreign ID')
   if x['group']!=by[pid]['group'] or len(x['matched'])!=50 or len(x['random'])!=50:raise RuntimeError('Candidate group/count mismatch')
   for pool in ('matched','random'):
    if [int(r['candidate_index']) for r in x[pool]]!=list(range(1,51)):raise RuntimeError('Candidate order mismatch: '+pid)
    for r in x[pool]:
     if r['pool']!=pool or r['paper_id']!=pid:raise RuntimeError('Candidate metadata mismatch')
   if x['gold']['pool']!='gold' or x['gold']['paper_id']!=pid:raise RuntimeError('Gold mismatch')
   candidate[pid]=x
 if len(candidate)!=50:raise RuntimeError('Expected 50 candidate JSON records')
 return root,s5,cohort,candidate,manifest

def audit(a):
 root,s5,cohort,cs,m=inputs(a)
 print('CANDIDATE HASH/COHORT VERIFIED',len(cohort),'papers',sum(len(x['matched'])+len(x['random'])+1 for x in cs.values()),'candidate records')
 print('Manifest SHA256',fhash(root/'config/manifest.json'));print('No GPU required')

def load_raw(p,cs,ph,rh=None):
 d={}
 if not p.exists():return d
 with p.open(encoding='utf-8') as f:
  for i,line in enumerate(f,1):
   if not line.strip():continue
   try:x=json.loads(line)
   except Exception as e:raise RuntimeError(f'Invalid/incomplete JSONL line {i}; inspect before resume') from e
   if x.get('protocol_hash')!=ph or (rh is not None and x.get('runtime_hash')!=rh):raise RuntimeError('Raw hash differs from frozen protocol/runtime')
   if x['paper_id'] not in cs or x['paper_id'] in d:raise RuntimeError('Unknown/duplicate raw paper')
   d[x['paper_id']]=x
 return d

def read_stage5(a):
 p=Path(a.stage5_script)
 if not p.is_file():raise FileNotFoundError('Validated Stage5 scorer required: '+str(p))
 spec=importlib.util.spec_from_file_location('stage5_fixed_reader',str(p));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 if m.LAYERS!=LAYERS or m.PROMPT!=PROMPT or m.REV!=REV:raise RuntimeError('Stage5 lens readout protocol differs')
 return m

def run(a):
 root,s5,cohort,cs,manifest=inputs(a);stage5=read_stage5(a)
 raw=root/'raw/pilot50_firsttoken_scores.jsonl';raw.parent.mkdir(parents=True,exist_ok=True)
 lens_path=Path(a.lens)
 if not lens_path.is_file():raise FileNotFoundError('Lens absent: '+str(lens_path))
 protocol={'candidate_manifest_sha256':fhash(root/'config/manifest.json'),'candidate_jsonl_sha256':manifest['output_sha256']['candidates/pilot50_author_candidates.jsonl'],'stage5_cohort_sha256':manifest['input_sha256']['pilot50'],'layers':LAYERS,'prompt':PROMPT,'model':MODEL,'revision':REV,'metric':'first_token_author_weighted_ties_half_v1','scorer':'stage7_2_v1'}
 ph=jhash(protocol);rh=jhash({'protocol_hash':ph,'lens_sha256':fhash(lens_path),'stage5_readout_sha256':fhash(Path(a.stage5_script)),'revision':REV,'gpu_layers':a.gpu_layers})
 rp=root/'config/gpu_scoring_runtime.json'
 if rp.exists():
  r=json.loads(rp.read_text());
  if r['runtime_hash']!=rh:raise RuntimeError('Existing scorer model/script/lens differs; do not mix results')
 done=load_raw(raw,cs,ph,rh)
 if not rp.exists():dump(rp,{'protocol':protocol,'protocol_hash':ph,'runtime_hash':rh,'lens_sha256':fhash(lens_path),'readout_sha256':fhash(Path(a.stage5_script)),'gpu_layers':a.gpu_layers})
 todo=[r for r in cohort if r['paper_id'] not in done]
 if a.max_papers is not None:todo=todo[:a.max_papers]
 print(f'STAGE 7.2: {len(done)}/50 completed; {len(todo)} queued',flush=True)
 if not todo:return
 import torch,jlens
 from transformers import AutoTokenizer,AutoModelForCausalLM
 tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
 device_map={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
 device_map.update({f'model.layers.{i}':(0 if i<a.gpu_layers else 'cpu') for i in range(64)})
 hf=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=device_map,low_cpu_mem_usage=True).eval()
 lens=jlens.JacobianLens.load(str(lens_path));model=jlens.from_hf(hf,tok)
 tstart=time.monotonic();dur=[]
 for r in todo:
  if time.monotonic()-tstart+max([a.paper_reserve_seconds]+dur)>a.max_seconds:
   print('SAFE TIME STOP; rerun same command in another allocation',flush=True);break
  start=time.monotonic();pid=r['paper_id'];c=cs[pid]
  allc=[c['gold']]+c['matched']+c['random']
  # Check the frozen tokenizer semantics on every candidate, never retokenize to redefine candidate IDs.
  for cand in allc:
   ids=tok.encode(' '+cand['candidate_name'],add_special_tokens=False)
   if not ids or ids[0]!=int(cand['first_token_id']) or len(ids)!=int(cand['n_name_tokens']):raise RuntimeError('Tokenizer changed for '+pid+' '+cand['candidate_name'])
  prompt=PROMPT.format(title=r['title'],year=r['year']);pids=model.encode(prompt,max_length=512).reshape(-1).tolist()
  if len(pids)>=512:raise RuntimeError('Prompt too long: '+pid)
  scores=stage5.readout(lens,model,prompt,pids,torch)
  # Store one score per UNIQUE token per mode, not 101 repeated vectors.
  ids=sorted({int(z['first_token_id']) for z in allc})
  values={mode:[float(vec[z]) for z in ids] for mode,vec in scores.items()}
  if any(not math.isfinite(v) for vs in values.values() for v in vs):raise RuntimeError('Nonfinite logits')
  if set(scores)!={*(f'jlens_L{l}' for l in LAYERS),*(f'vanilla_L{l}' for l in LAYERS),'final_L63'}:raise RuntimeError('Missing readout modes')
  row={'paper_id':pid,'group':r['group'],'protocol_hash':ph,'runtime_hash':rh,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'first_token_ids':ids,'score_by_mode':values,'seconds':round(time.monotonic()-start,3),'gpu_peak_gib':round(torch.cuda.max_memory_allocated()/2**30,3)}
  with raw.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
  done[pid]=row;dur.append(row['seconds']);print(f'{len(done)}/50 {r["group"]} {pid[:12]} modes={len(values)} unique_tokens={len(ids)} t={row["seconds"]:.1f}s',flush=True)
 print('Saved:',raw,flush=True)

def win(score, gold, negatives):
 return sum(1. if gold>score[x] else (0.5 if gold==score[x] else 0.) for x in negatives)/len(negatives)
def ci(v,seed=351720,B=10000):
 import numpy as np
 if not v:return (float('nan'),float('nan'))
 rg=np.random.default_rng(seed);x=np.array(v,float);z=np.mean(x[rg.integers(0,len(x),(B,len(x)))],axis=1)
 return tuple(float(t) for t in np.quantile(z,[0.025,0.975]))
def analyze(a):
 root,s5,cohort,cs,manifest=inputs(a);rp=root/'config/gpu_scoring_runtime.json'
 if not rp.exists():raise RuntimeError('No GPU run found')
 runtime=json.loads(rp.read_text());raw=load_raw(root/'raw/pilot50_firsttoken_scores.jsonl',cs,runtime['protocol_hash'],runtime['runtime_hash'])
 print('Analyzing',len(raw),'of 50; incomplete output is descriptive only',flush=True)
 if not raw:raise RuntimeError('No raw papers')
 measures=[];rank=[]
 for p in cohort:
  pid=p['paper_id'];r=raw.get(pid)
  if r is None:continue
  c=cs[pid];order=r['first_token_ids']
  for mode,values in r['score_by_mode'].items():
   if len(order)!=len(values):raise RuntimeError('Score vector length mismatch')
   lookup=dict(zip(order,values));gold=int(c['gold']['first_token_id']);gs=lookup[gold]
   for pool in ['random','matched','combined']:
    neg=c['random'] if pool=='random' else c['matched'] if pool=='matched' else c['matched']+c['random']
    tids=[int(x['first_token_id']) for x in neg];uniq=sorted(set(tids));non=[x for x in tids if x!=gold]
    ties=sum(x==gold for x in tids)
    for ix,x in enumerate(neg):
     if pool=='combined':continue
     tid=int(x['first_token_id']);sc=lookup[tid]
     rank.append({'paper_id':pid,'group':p['group'],'citation_bin':p['citation_bin'],'mode':mode,'pool':pool,'candidate_index':int(x['candidate_index']),'first_token_id':tid,'collision':int(tid==gold),'gold_score':gs,'false_score':sc,'gold_minus_false':gs-sc,'win':1 if gs>sc else 0.5 if gs==sc else 0})
    measures.append({'paper_id':pid,'group':p['group'],'field':p['field'],'citation_bin':p['citation_bin'],'mode':mode,'layer':int(mode.split('_L')[-1]),'pool':pool,'gold_win_rate':win(lookup,gs,tids),'unique_token_win_rate':win(lookup,gs,uniq),'non_collision_win_rate':win(lookup,gs,non) if non else float('nan'),'gold_first_token_id':gold,'gold_score':gs,'n_candidates':len(tids),'n_unique_tokens':len(uniq),'n_gold_collisions':ties,'collision_rate':ties/len(tids)})
 pairs=readcsv(s5/'matching/pilot50_ab_pairs.csv')
 keys={(r['paper_id'],r['mode'],r['pool']):r for r in measures}
 prs=[];summary=[]
 for mode in [*(f'{mt}_L{l}' for mt in ('jlens','vanilla') for l in LAYERS),'final_L63']:
  for pool in ('random','matched','combined'):
   subset=[]
   for pr in pairs:
    left=keys.get((pr['A_id'],mode,pool));right=keys.get((pr['B_id'],mode,pool))
    if left is None or right is None:continue
    d=left['gold_win_rate']-right['gold_win_rate'];subset.append(d)
    prs.append({'pair_id':pr['pair_id'],'A_id':pr['A_id'],'B_id':pr['B_id'],'mode':mode,'layer':int(mode.split('_L')[-1]),'pool':pool,'A_win_rate':left['gold_win_rate'],'B_win_rate':right['gold_win_rate'],'difference':d})
   if subset:
    lo,hi=ci(subset,seed=351720+len(subset)+len(mode)+len(pool))
    summary.append({'mode':mode,'pool':pool,'n_pairs':len(subset),'A_minus_B':statistics.mean(subset),'ci_lower':lo,'ci_upper':hi,'positive_pairs':sum(x>0 for x in subset),'median_difference':statistics.median(subset)})
 binrows=[]
 for (b,g,m,pool),rs in __import__('itertools').groupby(sorted(measures,key=lambda z:(z['citation_bin'],z['group'],z['mode'],z['pool'])),key=lambda z:(z['citation_bin'],z['group'],z['mode'],z['pool'])):
  grp=list(rs);binrows.append({'citation_bin':b,'group':g,'mode':m,'pool':pool,'n_papers':len(grp),'mean_gold_win_rate':statistics.mean(x['gold_win_rate'] for x in grp),'mean_tie_rate':statistics.mean(x['collision_rate'] for x in grp)})
 out=root/'summary';writecsv(out/'paper_layer_pool.csv',measures);writecsv(out/'candidate_pairwise_scores.csv',rank);writecsv(out/'matched_pair_layer.csv',prs);writecsv(out/'matched_ab_bootstrap.csv',summary);writecsv(out/'citation_bin_layer.csv',binrows)
 dump(out/'analysis_overview.json',{'n_papers':len(raw),'matched_complete_pairs':len({x['pair_id'] for x in prs}),'candidate_manifest_sha256':runtime['protocol']['candidate_manifest_sha256'],'protocol_hash':runtime['protocol_hash'],'readout_description':'first-token only; author-weighted gold win with tie=0.5; unique-token and non-collision sensitivity; no title shuffle in Stage7.2','citation_bin_0_2': [r for r in binrows if r['citation_bin'] in ['0-2','0–2','0–2 citations']]})
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 figdir=root/'figures';figdir.mkdir(exist_ok=True)
 for mode in ('jlens','vanilla'):
  fig,ax=plt.subplots(figsize=(9,5))
  for pool in ('random','matched','combined'):
   for g,sty in [('A','-'),('B','--')]:
    y=[statistics.mean(x['gold_win_rate'] for x in measures if x['mode']==f'{mode}_L{l}' and x['pool']==pool and x['group']==g) if any(x['mode']==f'{mode}_L{l}' and x['pool']==pool and x['group']==g for x in measures) else float('nan') for l in LAYERS]
    ax.plot(LAYERS,y,sty,marker='o',label=f'{g} {pool}')
  ax.set(xlabel='Layer',ylabel='Gold first-token win rate',title=f'Stage 7.2 {mode} / 50-paper pilot');ax.set_ylim(0,1);ax.legend(ncol=3,fontsize=8);fig.tight_layout()
  for ext in ('png','pdf'):fig.savefig(figdir/f'{mode}_ab_win_trajectory.{ext}',dpi=180)
  plt.close(fig)
 lines=['# Stage 7.2 — Frozen Gold vs 100 False Authors','',f'Completed papers: {len(raw)}/50; complete A/B pairs: {len({x["pair_id"] for x in prs})}/20.','', 'Measures are **first-token**, NOT complete author identity. Collision is a tie (0.5), not a correct classification.','', '## Matched A/B per-layer mean difference (exploratory)', '', '| Readout | Pool | Layer | n pairs | A−B | Bootstrap 95% CI |','|---|---|---:|---:|---:|---|']
 for r in summary:
  lines.append(f'| {r["mode"].split("_L")[0]} | {r["pool"]} | {r["mode"].split("_L")[-1]} | {r["n_pairs"]} | {r["A_minus_B"]:+.4f} | [{r["ci_lower"]:+.4f}, {r["ci_upper"]:+.4f}] |')
 lines+=['','## Interpretation limits','','Random/Matched false candidates are historical dataset authors, not verified exhaustive nonauthors outside the sampled paper list.','The frozen Matched pool uses tiered matching with different constraints by paper. Readout scores share token priors and candidate duplication.','This experiment does **not** run shuffled title controls or full-name conditional validation.','The pilot and per-layer comparisons are exploratory; confidence intervals are unadjusted for multiple comparisons.','']
 (root/'reports').mkdir(exist_ok=True);(root/'reports/stage7_2_gpu_report.md').write_text('\n'.join(lines),encoding='utf-8')
 print(f'ANALYSIS SAVED papers={len(raw)}/50 complete_pairs={len({x["pair_id"] for x in prs})}/20 output={root}',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('cmd',choices=['audit','run','analyze']);p.add_argument('--root',default=None);p.add_argument('--stage5-root',default=None);p.add_argument('--stage5-script',default=str(Path(__file__).with_name('351_stage5.py')));p.add_argument('--lens',default=None);p.add_argument('--gpu-layers',type=int,default=29);p.add_argument('--max-papers',type=int,default=None);p.add_argument('--max-seconds',type=int,default=4500);p.add_argument('--paper-reserve-seconds',type=int,default=450)
 a=p.parse_args();base=Path('/scratch')/os.environ.get('USER','unknown')/'jlens';a.root=a.root or str(base/'351_stage7_2');a.stage5_root=a.stage5_root or str(base/'351_stage5_crossed_v2');a.lens=a.lens or str(base/'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
 {'audit':audit,'run':run,'analyze':analyze}[a.cmd](a)
if __name__=='__main__':main()
