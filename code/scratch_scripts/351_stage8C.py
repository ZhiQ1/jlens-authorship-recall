
#!/usr/bin/env python3

"""Stage 8C: frozen 200-paper true/wrong title first-token GPU readout."""

import argparse,csv,hashlib,importlib.util,json,math,os,time,collections

from pathlib import Path



LAYERS=[16,24,32,40,48,56,62]

MODES={f'{kind}_L{l}' for kind in ('jlens','vanilla') for l in LAYERS}|{'final_L63'}

MODEL='Qwen/Qwen3-32B'

REV='9216db5781bf21249d130ec9da846c4624c16137'



def sha(p):

 h=hashlib.sha256()

 with open(p,'rb') as f:

  for x in iter(lambda:f.read(1<<20),b''):h.update(x)

 return h.hexdigest()



def jhash(v):

 return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()



def csvread(p):

 with p.open(encoding='utf-8-sig',newline='') as f:

  return list(csv.DictReader(f))



def jwrite(p,v):

 p.parent.mkdir(parents=True,exist_ok=True)

 p.write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n')



def check(a):

 root=a.root

 manifest=root/'config/manifest.json'

 bman=root/'config/stage8B_manifest.json'

 if not manifest.is_file() or not bman.is_file():

  raise RuntimeError('Stage 8A/8B freeze missing')

 bm=json.loads(bman.read_text())

 if sha(manifest)!=bm['stage8A_manifest_sha256']:

  raise RuntimeError('Stage8A manifest changed')

 for p,h in bm['files'].items():

  if sha(root/p)!=h:

   raise RuntimeError('Frozen 8B output modified: '+p)

 cps=csvread(root/'cohort/stage8_papers.csv')

 cand=csvread(root/'controls/stage8_author_candidates.csv')

 titles=csvread(root/'controls/stage8_shuffled_titles.csv')

 if len(cps)!=200 or len(cand)!=20200 or len(titles)!=4000:

  raise RuntimeError('Frozen row counts invalid')

 papers={r['paper_id']:r for r in cps}

 if len(papers)!=200 or collections.Counter(x['group'] for x in cps)!={'A':100,'B':100}:

  raise RuntimeError('Invalid frozen cohort')

 by=collections.defaultdict(list)

 for r in cand:by[r['paper_id']].append(r)

 ts=collections.defaultdict(list)

 for r in titles:ts[r['paper_id']].append(r)

 if set(papers)!=set(by) or set(papers)!=set(ts):

  raise RuntimeError('Paper coverage mismatch')

 contexts=[]

 ids_by={}

 for pid in sorted(papers):

  p=papers[pid]

  rows=by[pid]

  if collections.Counter(x['pool'] for x in rows)!={'gold':1,'matched':50,'random':50}:

   raise RuntimeError('Bad candidate counts '+pid)

  if len({int(r['candidate_index']) for r in rows})!=101:

   raise RuntimeError('Bad candidate indexes '+pid)

  ids_by[pid]=sorted({int(r['first_token_id']) for r in rows})

  if len(ts[pid])!=20 or len({int(x['shuffle_index']) for x in ts[pid]})!=20:

   raise RuntimeError('Bad null contexts '+pid)

  contexts.append(dict(paper_id=pid,shuffle_index=0,title=p['title'],year=p['year'],group=p['group'],source_paper_id=pid))

  for r in sorted(ts[pid],key=lambda r:int(r['shuffle_index'])):

   if r['year']!=p['year'] or r['group']!=p['group']:

    raise RuntimeError('Shuffle metadata mismatch')

   contexts.append(dict(paper_id=pid,shuffle_index=int(r['shuffle_index']),title=r['shuffled_title'],year=r['year'],group=p['group'],source_paper_id=r['source_paper_id']))

 if len(contexts)!=4200:

  raise RuntimeError('Not 4200 contexts')

 script=Path(a.stage5_script)

 if not script.is_file():

  raise FileNotFoundError('Stage5 readout source required: '+str(script))

 spec=importlib.util.spec_from_file_location('frozen_stage5_readout',str(script))

 mod=importlib.util.module_from_spec(spec)

 spec.loader.exec_module(mod)

 if list(mod.LAYERS)!=LAYERS or mod.REV!=REV or not callable(mod.readout):

  raise RuntimeError('Stage5 readout mismatch')

 if '{title}' not in mod.PROMPT or '{year}' not in mod.PROMPT:

  raise RuntimeError('Unexpected Stage5 prompt template')

 return root,bman,papers,by,contexts,ids_by,mod,script



def plan(a,items):

 root,bman,papers,by,contexts,ids_by,mod,script=items

 lens=Path(a.lens)

 if not lens.is_file():

  raise FileNotFoundError(lens)

 cfg={

  'stage8A_sha256':sha(root/'config/manifest.json'),

  'stage8B_sha256':sha(bman),

  'stage5_code_sha256':sha(script),

  'stage5_prompt':mod.PROMPT,

  'public_lens_sha256':sha(lens),

  'layers':LAYERS,

  'modes':sorted(MODES),

  'model':MODEL,

  'revision':REV,

  'gpu_layers':a.gpu_layers,

  'metric':'first_token_gold_author_weighted_win_ties_half_v1',

  'scorer':'stage8c_v1'

 }

 cfg['protocol_hash']=jhash({k:v for k,v in cfg.items() if k!='gpu_layers'})

 cfg['runtime_hash']=jhash(cfg)

 path=root/'config/stage8C_runtime.json'

 if path.exists() and json.loads(path.read_text())!=cfg:

  raise RuntimeError('Stage8C runtime changed; refusing mixed data')

 return cfg,path



def rawread(path,contexts,ids_by,cfg,prompt):

 valid={(x['paper_id'],x['shuffle_index']):x for x in contexts}

 done={}

 if not path.exists():

  return done

 with path.open(encoding='utf-8') as f:

  for line_no,line in enumerate(f,1):

   if not line.endswith('\n'):

    raise RuntimeError(f'Truncated raw line {line_no}; inspect before resume')

   r=json.loads(line)

   key=(r['paper_id'],int(r['shuffle_index']))

   if key not in valid or key in done:

    raise RuntimeError('Foreign/duplicate raw context '+str(key))

   x=valid[key]

   expected_prompt=prompt.format(title=x['title'],year=x['year'])

   if r['protocol_hash']!=cfg['protocol_hash'] or r['runtime_hash']!=cfg['runtime_hash']:

    raise RuntimeError('Raw protocol mismatch')

   if r['prompt_sha256']!=hashlib.sha256(expected_prompt.encode()).hexdigest():

    raise RuntimeError('Raw prompt mismatch '+str(key))

   if r['first_token_ids']!=ids_by[x['paper_id']] or set(r['score_by_mode'])!=MODES:

    raise RuntimeError('Raw scores missing modes/tokens')

   if any(len(z)!=len(r['first_token_ids']) or any(not math.isfinite(v) for v in z) for z in r['score_by_mode'].values()):

    raise RuntimeError('Invalid raw scores')

   done[key]=r

 return done



def audit(a):

 items=check(a)

 root,bman,papers,by,contexts,ids_by,mod,script=items

 cfg,path=plan(a,items)

 raw=root/'raw/stage8C_context_scores.jsonl'

 done=rawread(raw,contexts,ids_by,cfg,mod.PROMPT)

 print(f'STAGE8C AUDIT PASS frozen=4200 existing={len(done)} remaining={4200-len(done)} stage8B={sha(bman)} lens={cfg["public_lens_sha256"]}')

 return items,cfg,path,done



def run(a):

 items,cfg,runtime,done=audit(a)

 root,bman,papers,by,contexts,ids_by,mod,script=items

 raw=root/'raw/stage8C_context_scores.jsonl'

 todo=[x for x in contexts if (x['paper_id'],x['shuffle_index']) not in done]

 if a.max_contexts is not None:

  todo=todo[:a.max_contexts]

 print('Stage8C to score:',len(todo),'already:',len(done),flush=True)

 if not todo:

  return

 if not runtime.exists():

  jwrite(runtime,cfg)

 import torch,jlens

 from transformers import AutoTokenizer,AutoModelForCausalLM

 if not torch.cuda.is_available():

  raise RuntimeError('GPU required')

 tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)

 for pid,rs in by.items():

  for r in rs:

   tids=tok.encode(' '+r['candidate_name'],add_special_tokens=False)

   frozen=json.loads(r['all_token_ids'])

   if tids!=frozen or not tids or tids[0]!=int(r['first_token_id']):

    raise RuntimeError('Frozen candidate tokenizer mismatch '+pid)

 dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}

 dm.update({f'model.layers.{i}':(0 if i<a.gpu_layers else 'cpu') for i in range(64)})

 hf=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()

 lens=jlens.JacobianLens.load(str(a.lens))

 model=jlens.from_hf(hf,tok)

 begin=time.monotonic()

 recent=[]

 for x in todo:

  if time.monotonic()-begin+max([a.reserve_seconds]+recent)>a.max_seconds:

   print('SAFE TIME STOP; rerun identical command on new GPU allocation',flush=True)

   break

  t0=time.monotonic()

  pid=x['paper_id']

  ix=x['shuffle_index']

  prompt=mod.PROMPT.format(title=x['title'],year=x['year'])

  pids=model.encode(prompt,max_length=512).reshape(-1).tolist()

  if len(pids)>=512:

   raise RuntimeError('Prompt too long: '+pid)

  scores=mod.readout(lens,model,prompt,pids,torch)

  if set(scores)!=MODES:

   raise RuntimeError('Unexpected readout modes '+str(set(scores)))

  ids=ids_by[pid]

  values={k:[float(scores[k][v]) for v in ids] for k in sorted(MODES)}

  if any(not math.isfinite(v) for z in values.values() for v in z):

   raise RuntimeError('Nonfinite scoring')

  r={

   'paper_id':pid,

   'shuffle_index':ix,

   'group':x['group'],

   'source_paper_id':x['source_paper_id'],

   'protocol_hash':cfg['protocol_hash'],

   'runtime_hash':cfg['runtime_hash'],

   'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),

   'first_token_ids':ids,

   'score_by_mode':values,

   'seconds':round(time.monotonic()-t0,3)

  }

  raw.parent.mkdir(exist_ok=True,parents=True)

  with raw.open('a',encoding='utf-8') as f:

   f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')

   f.flush()

   os.fsync(f.fileno())

  done[(pid,ix)]=r

  recent.append(r['seconds'])

  recent=recent[-12:]

  print(f'{len(done)}/4200 {x["group"]} {pid[:10]} ctx={ix:02d} t={r["seconds"]:.1f}s',flush=True)

 print('Saved:',raw,flush=True)



def main():

 p=argparse.ArgumentParser()

 p.add_argument('cmd',choices=['audit','run'])

 base=Path('/scratch')/os.getenv('USER','')/'jlens'

 p.add_argument('--root',type=Path,default=base/'351_stage8')

 p.add_argument('--stage5-script',default=str(Path.home()/'351_stage5.py'))

 p.add_argument('--lens',default=str(base/'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'))

 p.add_argument('--gpu-layers',type=int,default=29)

 p.add_argument('--max-contexts',type=int)

 p.add_argument('--max-seconds',type=int,default=4500)

 p.add_argument('--reserve-seconds',type=int,default=450)

 a=p.parse_args()

 if not 1<=a.gpu_layers<=64 or a.max_seconds<=a.reserve_seconds or (a.max_contexts is not None and a.max_contexts<1):

  p.error('Invalid resource budget')

 {'audit':audit,'run':run}[a.cmd](a)



if __name__=='__main__':

 main()

