#!/usr/bin/env python3
"""Stage 7.3B/C: immutable shuffled-title score + empirical-null analysis.
Commands: audit, run, analyze. Never writes Stage5/7.2 or Stage7.3A frozen files.
Requires 351_stage5.py in same directory (identical readout implementation).
"""
import argparse,csv,hashlib,importlib.util,json,math,os,statistics,time
from pathlib import Path
from collections import Counter,defaultdict
LAYERS=[16,24,32,40,48,56,62]
MODES=[*(f'jlens_L{i}' for i in LAYERS),*(f'vanilla_L{i}' for i in LAYERS),'final_L63']
PROMPT='Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'
MODEL='Qwen/Qwen3-32B';REV='9216db5781bf21249d130ec9da846c4624c16137'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def csvread(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(p,rows):
 if not rows:return
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def putjson(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n');q.replace(p)
def load(a):
 root=Path(a.root);s72=Path(a.stage72_root);s5=Path(a.stage5_root)
 mfile=root/'config/manifest.json';m=json.loads(mfile.read_text())
 if m['protocol']!='stage7_3a_title_freeze_v1' or m['k']!=20:raise ValueError('Wrong frozen titles protocol')
 for rel,h in m['output_sha256'].items():
  if sha(root/rel)!=h:raise ValueError('Frozen title file modified: '+rel)
 expected={'pilot50':s5/'cohort/pilot50_v1.csv','full6841':s5/'cohort/full_6841_manifest.csv','frozen_candidates':s72/'candidates/pilot50_author_candidates.csv','candidate_manifest':s72/'config/manifest.json'}
 for k,p in expected.items():
  if sha(p)!=m['input_sha256'][k]:raise ValueError('Title freeze input changed: '+k)
 cs=json.loads((s72/'config/manifest.json').read_text())
 for rel,h in cs['output_sha256'].items():
  if sha(s72/rel)!=h:raise ValueError('Candidate freeze file changed: '+rel)
 rt=json.loads((s72/'config/gpu_scoring_runtime.json').read_text());truefile=s72/'raw/pilot50_firsttoken_scores.jsonl'
 paper=csvread(expected['pilot50']);pby={r['paper_id']:r for r in paper}
 shuffles=csvread(root/'titles/pilot50_shuffled_titles.csv')
 if len(paper)!=50 or len(pby)!=50 or Counter(r['group'] for r in paper)!=Counter(A=20,B=20,C=7,D=3):raise ValueError('Pilot50 corrupted')
 if len(shuffles)!=1000:raise ValueError('Expected exactly 1,000 frozen shuffles')
 seen=set();grouped=defaultdict(list)
 for x in shuffles:
  pid=x['paper_id'];i=int(x['shuffle_index']);k=(pid,i)
  if pid not in pby or k in seen or i<1 or i>20 or x['group']!=pby[pid]['group'] or str(x['year'])!=str(pby[pid]['year']):raise ValueError('Bad shuffle entry: '+str(k))
  if x['true_title']!=pby[pid]['title'] or not x['shuffled_title'] or x['shuffled_title']==x['true_title']:raise ValueError('Bad title: '+str(k))
  seen.add(k);grouped[pid].append(x)
 if any(len(grouped[p])!=20 for p in pby):raise ValueError('Missing per-paper shuffled titles')
 candidate={}
 with (s72/'candidates/pilot50_author_candidates.jsonl').open(encoding='utf-8') as f:
  for line in f:
   if line.strip():
    c=json.loads(line);candidate[c['paper_id']]=c
 if set(candidate)!=set(pby):raise ValueError('Frozen candidates/papers mismatch')
 true={}
 with truefile.open(encoding='utf-8') as f:
  for line in f:
   if line.strip():
    t=json.loads(line);pid=t['paper_id']
    if pid in true or pid not in pby or t['protocol_hash']!=rt['protocol_hash'] or t['runtime_hash']!=rt['runtime_hash']:raise ValueError('True raw score invalid')
    if set(t['score_by_mode'])!=set(MODES):raise ValueError('True scores missing modes')
    true[pid]=t
 if len(true)!=50:raise ValueError('Stage7.2 true-title score is not 50/50')
 return root,s72,s5,m,mfile,rt,truefile,paper,shuffles,candidate,true

def runtime_config(a,info):
 root,s72,s5,m,mfile,rt,truefile,*_=info
 if sha(Path(a.stage5_script))!=rt['readout_sha256']:raise ValueError('Stage5 readout script changed versus Stage7.2')
 if sha(Path(a.lens))!=rt['lens_sha256']:raise ValueError('J-Lens weights changed versus Stage7.2')
 if a.gpu_layers!=rt['gpu_layers']:raise ValueError('GPU layer placement must match Stage7.2')
 protocol={'stage73_manifest_sha256':sha(mfile),'stage72_candidate_manifest_sha256':sha(s72/'config/manifest.json'),'stage72_runtime_hash':rt['runtime_hash'],'stage72_true_raw_sha256':sha(truefile),'prompt':PROMPT,'model':MODEL,'revision':REV,'modes':MODES,'k':20,'comparison':'same candidate first-token logits, same target year; title only differs','scorer':'stage7_3b_v1'}
 ph=digest(protocol);rh=digest({'protocol_hash':ph,'lens_sha256':rt['lens_sha256'],'readout_sha256':rt['readout_sha256'],'gpu_layers':a.gpu_layers})
 return {'protocol':protocol,'protocol_hash':ph,'runtime_hash':rh,'lens_sha256':rt['lens_sha256'],'readout_sha256':rt['readout_sha256'],'gpu_layers':a.gpu_layers}

def raw_read(p,ph,rh):
 done={}
 if p.exists():
  for ln,line in enumerate(p.open(encoding='utf-8'),1):
   if not line.strip():continue
   try:x=json.loads(line)
   except Exception as e:raise RuntimeError(f'Broken JSONL at line {ln}; repair before resuming') from e
   key=(x['paper_id'],int(x['shuffle_index']))
   if key in done or x['protocol_hash']!=ph or x['runtime_hash']!=rh:raise RuntimeError('Duplicate key or mismatched hashes at line '+str(ln))
   done[key]=x
 return done

def audit(a):
 info=load(a);*_,paper,shuffles,cs,true=info
 print('STAGE 7.3A + STAGE 7.2 VERIFIED',len(paper),'papers',len(shuffles),'shuffles',len(cs),'candidate sets',len(true),'true-title score records')
 print('Title manifest:',sha(info[4]));print('GPU not used')

def run(a):
 info=load(a);root,s72,s5,m,mfile,rt,truefile,papers,shuffles,candidates,trues=info
 readout_file=Path(a.stage5_script)
 spec=importlib.util.spec_from_file_location('frozen_s5_readout',str(readout_file));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if mod.LAYERS!=LAYERS or mod.PROMPT!=PROMPT or mod.REV!=REV:raise ValueError('Stage5 readout implementation incompatible')
 cfg=runtime_config(a,info);runtime=root/'config/stage73b_runtime.json';raw=root/'raw/shuffled_firsttoken_scores.jsonl'
 if runtime.exists():
  old=json.loads(runtime.read_text())
  if old['runtime_hash']!=cfg['runtime_hash']:raise ValueError('Runtime changed; refuse to mix raw scores')
 done=raw_read(raw,cfg['protocol_hash'],cfg['runtime_hash'])
 valid={(x['paper_id'],int(x['shuffle_index'])):x for x in shuffles}
 if not set(done).issubset(valid):raise ValueError('Raw contains nonfrozen title IDs')
 for key,x in done.items():
  r=valid[key]
  prompt=PROMPT.format(title=r['shuffled_title'],year=r['year'])
  if x['prompt_sha256']!=hashlib.sha256(prompt.encode()).hexdigest():raise ValueError('Raw prompt does not match frozen title '+str(key))
  ids=x['first_token_ids'];expected=sorted({int(c['first_token_id']) for pool in ['gold','matched','random'] for c in ([candidates[key[0]][pool]] if pool=='gold' else candidates[key[0]][pool])})
  if ids!=expected or set(x['score_by_mode'])!=set(MODES) or any(len(v)!=len(ids) for v in x['score_by_mode'].values()):raise ValueError('Raw candidate/mode mismatch: '+str(key))
 if not runtime.exists():putjson(runtime,cfg)
 todo=[x for x in shuffles if (x['paper_id'],int(x['shuffle_index'])) not in done]
 if a.max_papers is not None:
  ids=[]
  for x in todo:
   if x['paper_id'] not in ids:ids.append(x['paper_id'])
  todo=[x for x in todo if x['paper_id'] in set(ids[:a.max_papers])]
 if a.shuffles_per_paper is not None:todo=[x for x in todo if int(x['shuffle_index'])<=a.shuffles_per_paper]
 if a.max_contexts is not None:todo=todo[:a.max_contexts]
 print(f'STAGE 7.3B: {len(done)}/1000 complete; {len(todo)} queued',flush=True)
 if not todo:return
 import torch,jlens
 from transformers import AutoTokenizer,AutoModelForCausalLM
 tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
 device_map={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
 device_map.update({f'model.layers.{i}':(0 if i<a.gpu_layers else 'cpu') for i in range(64)})
 hf=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=device_map,low_cpu_mem_usage=True).eval()
 lens=jlens.JacobianLens.load(str(a.lens));model=jlens.from_hf(hf,tok)
 elapsed_start=time.monotonic();times=[]
 for r in todo:
  if time.monotonic()-elapsed_start+max([a.paper_reserve_seconds]+times)>a.max_seconds:
   print('SAFE TIME STOP: Resume same command in another allocation.',flush=True);break
  start=time.monotonic();pid=r['paper_id'];ix=int(r['shuffle_index']);c=candidates[pid]
  allc=[c['gold']]+c['matched']+c['random']
  for cand in allc:
   z=tok.encode(' '+cand['candidate_name'],add_special_tokens=False)
   if not z or z[0]!=int(cand['first_token_id']) or len(z)!=int(cand['n_name_tokens']):raise ValueError('Tokenizer mismatch '+pid)
  prompt=PROMPT.format(title=r['shuffled_title'],year=r['year']);pids=model.encode(prompt,max_length=512).reshape(-1).tolist()
  if len(pids)>=512:raise ValueError('Prompt exceeds 512 tokens '+pid)
  scores=mod.readout(lens,model,prompt,pids,torch)
  if set(scores)!=set(MODES):raise ValueError('Unexpected readout modes '+str(set(scores)))
  ids=sorted({int(z['first_token_id']) for z in allc});values={k:[float(v[t]) for t in ids] for k,v in scores.items()}
  if any(not math.isfinite(x) for vs in values.values() for x in vs):raise ValueError('Nonfinite logit '+pid)
  record={'paper_id':pid,'shuffle_index':ix,'group':r['group'],'source_paper_id':r['source_paper_id'],'protocol_hash':cfg['protocol_hash'],'runtime_hash':cfg['runtime_hash'],'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'first_token_ids':ids,'score_by_mode':values,'seconds':round(time.monotonic()-start,3)}
  raw.parent.mkdir(parents=True,exist_ok=True)
  with raw.open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
  done[(pid,ix)]=record;times.append(record['seconds'])
  print(f'{len(done)}/1000 {r["group"]} {pid[:12]} shuffle={ix:02d} tier={r["match_tier"]} modes=15 t={record["seconds"]:.1f}s',flush=True)
 print('Saved:',raw,flush=True)

def win(vals,gold,neg):
 g=vals[gold]
 return sum(1 if g>vals[n] else (0.5 if g==vals[n] else 0) for n in neg)/len(neg)
def boot(xs,seed=35173,B=10000):
 import numpy as np
 v=np.array(xs,float);rng=np.random.default_rng(seed);res=v[rng.integers(0,len(v),(B,len(v)))].mean(axis=1)
 return tuple(np.quantile(res,[.025,.975]).tolist())
def analyze(a):
 info=load(a);root,s72,s5,m,mfile,rt,truefile,paper,shuffles,cands,true=info
 runtime=root/'config/stage73b_runtime.json'
 if not runtime.exists():raise FileNotFoundError('No Shuffle GPU run')
 cfg=json.loads(runtime.read_text());done=raw_read(root/'raw/shuffled_firsttoken_scores.jsonl',cfg['protocol_hash'],cfg['runtime_hash'])
 frozen={(r['paper_id'],int(r['shuffle_index'])):r for r in shuffles}
 if not set(done).issubset(frozen):raise ValueError('Unknown shuffle context')
 grouped=defaultdict(list);out=[]
 for (pid,i),r in sorted(done.items()):
  source=frozen[(pid,i)];c=cands[pid];gold=int(c['gold']['first_token_id']);ids=r['first_token_ids'];values=r['score_by_mode']
  exp=sorted({int(z['first_token_id']) for z in [c['gold']]+c['random']+c['matched']})
  if ids!=exp or set(values)!=set(MODES) or any(len(v)!=len(ids) for v in values.values()):raise ValueError('Corrupt context '+str((pid,i)))
  if r['prompt_sha256']!=hashlib.sha256(PROMPT.format(title=source['shuffled_title'],year=source['year']).encode()).hexdigest():raise ValueError('Prompt hash differs')
  for mode,vs in values.items():
   lookup=dict(zip(ids,vs));t=true[pid];tl=dict(zip(t['first_token_ids'],t['score_by_mode'][mode]))
   for pool in ['random','matched','combined']:
    neg=c['random'] if pool=='random' else c['matched'] if pool=='matched' else c['random']+c['matched'];nt=[int(z['first_token_id']) for z in neg]
    if any(z not in tl for z in [gold]+nt):raise ValueError('True score missing token')
    wn=win(lookup,gold,nt);wt=win(tl,gold,nt)
    excl=[z for z in nt if z!=gold];uniq=sorted(set(nt))
    out.append({'paper_id':pid,'group':source['group'],'citation_bin':source['citation_bin'],'mode':mode,'pool':pool,'shuffle_index':i,'match_tier':int(source['match_tier']),'source_author_in_false_pool':int(source['source_author_in_false_pool']),'true_win':wt,'null_win':wn,'advantage':wt-wn,'null_unique':win(lookup,gold,uniq),'null_noncollision':win(lookup,gold,excl) if excl else float('nan')})
    grouped[(pid,mode,pool)].append(out[-1])
 summary=[]
 for (pid,mode,pool),rs in grouped.items():
  wt=rs[0]['true_win'];nulls=[z['null_win'] for z in rs];k=len(nulls);sortedr=sorted(nulls)
  nonoverlap=[z['null_win'] for z in rs if not z['source_author_in_false_pool']]
  summary.append({'paper_id':pid,'group':rs[0]['group'],'citation_bin':rs[0]['citation_bin'],'mode':mode,'pool':pool,'n_null':k,'true_win':wt,'null_mean':statistics.mean(nulls),'null_median':statistics.median(nulls),'null_p95':float(__import__('numpy').quantile(nulls,.95)),'title_advantage':wt-statistics.mean(nulls),'null_percentile_midrank':(sum(x<wt for x in nulls)+.5*sum(x==wt for x in nulls))/k,'empirical_tail_fraction':(1+sum(x>=wt for x in nulls))/(k+1),'n_no_source_false_overlap':len(nonoverlap),'advantage_no_source_false_overlap':wt-statistics.mean(nonoverlap) if nonoverlap else float('nan')})
 writecsv(root/'summary/shuffle_context_pool.csv',out);writecsv(root/'summary/paper_null_distribution.csv',summary)
 by={(r['paper_id'],r['mode'],r['pool']):r for r in summary}
 pairs=csvread(s5/'matching/pilot50_ab_pairs.csv');pr=[];effects=[]
 for pair in pairs:
  for mode in MODES:
   for pool in ['random','matched','combined']:
    A=by.get((pair['A_id'],mode,pool));B=by.get((pair['B_id'],mode,pool))
    if A and B:
     pr.append({'pair_id':pair['pair_id'],'mode':mode,'pool':pool,'A_id':pair['A_id'],'B_id':pair['B_id'],'difference':A['title_advantage']-B['title_advantage']})
 for mode in MODES:
  for pool in ['random','matched','combined']:
   diffs=[r['difference'] for r in pr if r['mode']==mode and r['pool']==pool]
   if diffs:
    lo,hi=boot(diffs)
    effects.append({'mode':mode,'pool':pool,'n_pairs':len(diffs),'mean_A_minus_B':statistics.mean(diffs),'ci_lower':lo,'ci_upper':hi,'positive_pairs':sum(x>0 for x in diffs),'median_difference':statistics.median(diffs)})
 writecsv(root/'summary/matched_pair_differences.csv',pr);writecsv(root/'summary/matched_ab_bootstrap.csv',effects)
 integration=[]
 for pid in {r['paper_id'] for r in summary}:
  for lens in ['jlens','vanilla']:
   for pool in ['random','matched','combined']:
    z=[by[(pid,f'{lens}_L{l}',pool)] for l in LAYERS if (pid,f'{lens}_L{l}',pool) in by]
    if len(z)==7:integration.append({'paper_id':pid,'group':z[0]['group'],'citation_bin':z[0]['citation_bin'],'lens':lens,'pool':pool,'integrated_advantage':statistics.mean(t['title_advantage'] for t in z)})
 writecsv(root/'summary/paper_integrated.csv',integration)
 integby={(r['paper_id'],r['lens'],r['pool']):r for r in integration};integ_pairs=[];integ_effect=[]
 for pair in pairs:
  for lens in ['jlens','vanilla']:
   for pool in ['random','matched','combined']:
    A=integby.get((pair['A_id'],lens,pool));B=integby.get((pair['B_id'],lens,pool))
    if A and B:integ_pairs.append({'pair_id':pair['pair_id'],'lens':lens,'pool':pool,'A_minus_B':A['integrated_advantage']-B['integrated_advantage']})
 for lens in ['jlens','vanilla']:
  for pool in ['random','matched','combined']:
   diffs=[x['A_minus_B'] for x in integ_pairs if x['lens']==lens and x['pool']==pool]
   if diffs:
    lo,hi=boot(diffs);integ_effect.append({'lens':lens,'pool':pool,'n_pairs':len(diffs),'mean_A_minus_B':statistics.mean(diffs),'ci_lower':lo,'ci_upper':hi,'positive_pairs':sum(x>0 for x in diffs)})
 writecsv(root/'summary/integrated_pair_differences.csv',integ_pairs);writecsv(root/'summary/integrated_ab_bootstrap.csv',integ_effect)
 if len(done)==1000:
  assert len(summary)==50*15*3 and len(integration)==50*2*3 and len(integ_pairs)==20*2*3
  assert all(r['n_null']==20 for r in summary)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 figdir=root/'figures';figdir.mkdir(exist_ok=True)
 for lens in ['jlens','vanilla']:
  fig,ax=plt.subplots(figsize=(9,5))
  for group,sty in [('A','-o'),('B','--s')]:
   y=[statistics.mean(x['title_advantage'] for x in summary if x['group']==group and x['mode']==f'{lens}_L{l}' and x['pool']=='combined') if any(x['group']==group and x['mode']==f'{lens}_L{l}' and x['pool']=='combined' for x in summary) else float('nan') for l in LAYERS]
   ax.plot(LAYERS,y,sty,label=group)
  ax.axhline(0,color='grey',linewidth=.8);ax.set(xlabel='Layer',ylabel='True − mean shuffled gold win rate',title=f'Stage 7.3 {lens} title-specific advantage');ax.legend();fig.tight_layout()
  for ext in ['png','pdf']:fig.savefig(figdir/f'{lens}_title_advantage.{ext}',dpi=175)
  plt.close(fig)
 low=[x for x in summary if x['citation_bin'] in ('0–2','0-2','0–2 citations') and x['mode']=='jlens_L56' and x['pool']=='combined']
 overview={'scored_contexts':len(done),'expected_contexts':1000,'complete_papers':sum(all((p['paper_id'],i) in done for i in range(1,21)) for p in paper),'matched_complete_pairs':len({x['pair_id'] for x in integ_pairs}),'n_low_bin_0_2_at_L56':len(low),'stage73_manifest_sha256':sha(mfile),'stage72_true_raw_sha256':sha(truefile),'readout':'First token only; title-conditioned candidate discrimination; empirical null is matched wrong titles, not a claim about total model ignorance','null_sampling':'20 metadata-selected titles, not exchangeable random permutations; tail fractions are descriptive','status':'COMPLETE' if len(done)==1000 else 'PARTIAL, exploratory only'}
 putjson(root/'summary/analysis_overview.json',overview)
 report=['# Stage 7.3B/C empirical shuffled-title null','',f'Contexts: {len(done)}/1000; full papers {overview["complete_papers"]}/50; full A/B pairs {overview["matched_complete_pairs"]}/20.','', 'This is **first-token** candidate discrimination, not full-author knowledge. Null contexts use the target paper year and original false-author pools.', '', '## Seven-layer matched A−B title advantage (exploratory)','', '| Lens | Pool | A−B | 95% pair-bootstrap CI | n pairs |','|---|---|---:|---|---:|']
 for x in integ_effect:report.append(f'| {x["lens"]} | {x["pool"]} | {x["mean_A_minus_B"]:+.5f} | [{x["ci_lower"]:+.5f},{x["ci_upper"]:+.5f}] | {x["n_pairs"]} |')
 report+=['','## Scientific limitations','','- 20 metadata-optimized shuffled titles per paper are not exchangeable under a formal randomization test. Empirical tail fractions are **descriptive**, not calibrated p-values.','- 19.9% of frozen sources overlap at least one false-author candidate (as earlier audit); use per-paper no-source-overlap sensitivity.','- Multiple layers and pools have been examined; individual CIs are exploratory and unadjusted.','- Citation Bin 0–2 has only six pilot papers and cannot establish a population-wide accessibility floor.','- Do not report a complete or confirmatory result until all 1,000 contexts score successfully.','']
 (root/'reports').mkdir(exist_ok=True);(root/'reports/stage7_3_null_report.md').write_text('\n'.join(report),encoding='utf-8')
 print(f'ANALYSIS SAVED contexts={len(done)}/1000 full_papers={overview["complete_papers"]}/50 matched_pairs={overview["matched_complete_pairs"]}/20 status={overview["status"]}',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('cmd',choices=['audit','run','analyze']);p.add_argument('--root');p.add_argument('--stage72-root');p.add_argument('--stage5-root');p.add_argument('--stage5-script',default=str(Path(__file__).with_name('351_stage5.py')));p.add_argument('--lens');p.add_argument('--gpu-layers',type=int,default=29);p.add_argument('--max-papers',type=int);p.add_argument('--shuffles-per-paper',type=int);p.add_argument('--max-contexts',type=int);p.add_argument('--max-seconds',type=int,default=4500);p.add_argument('--paper-reserve-seconds',type=int,default=450)
 a=p.parse_args();base=Path('/scratch')/os.environ.get('USER','unknown')/'jlens';a.root=a.root or str(base/'351_stage7_3');a.stage72_root=a.stage72_root or str(base/'351_stage7_2');a.stage5_root=a.stage5_root or str(base/'351_stage5_crossed_v2');a.lens=a.lens or str(base/'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
 {'audit':audit,'run':run,'analyze':analyze}[a.cmd](a)
if __name__=='__main__':main()
