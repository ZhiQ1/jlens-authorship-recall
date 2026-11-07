#!/usr/bin/env python3
"""Stage9 A repair: preserve frozen A + original checkpoint; append ONE vetted WikiText replacement.

No checkpoint cursor rewriting. Exactly one skipped prompt is expected. The final state
must be next_idx=101, n_done=100. B, original A, and holdout are never modified.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, sys, time, datetime
from pathlib import Path
BASE=Path('/scratch')/os.environ['USER']/'jlens'
ROOT=BASE/'351_stage9'
OLD=ROOT/'runner_runs'/'full_A_100_7layers'
NEW=ROOT/'runner_runs'/'full_A_repair_101_100valid'
LAYERS=[16,24,32,40,48,56,62]
SRC=BASE/'stage9_fullfit.py'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def hash_text(s):return hashlib.sha256(s.encode()).hexdigest()
def canon(s):return ' '.join(s.split()).strip()
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def jread(p):return json.loads(p.read_text())
def atomic(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+f'.tmp.{os.getpid()}'); tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n');os.replace(tmp,p)
def checkpoint(path):
 import torch
 s=torch.load(path,map_location='cpu',weights_only=True)
 if list(s['source_layers'])!=LAYERS or s['target_layer']!=63 or s['skip_first']!=16:raise RuntimeError('checkpoint fitting layers/target/skip_first mismatch')
 if set(s['jacobian_sum'])!=set(LAYERS):raise RuntimeError('matrix keys mismatch')
 if not 0<=s['n_done']<=s['next_idx']<=101:raise RuntimeError('invalid checkpoint counts')
 return s

def split_data():
 m=load_module(BASE/'stage9_runner.py','existing_stage9_runner')
 args=m.__dict__.get('args_for')
 from types import SimpleNamespace
 a=SimpleNamespace(root=m.ROOT,half='A',total=100,layers=LAYERS,dim_batch=1,run_id='full_A_100_7layers')
 cfg,prompts=m.frozen(m.load_old(),a)
 if len(prompts)!=100:return (_ for _ in ()).throw(RuntimeError('frozen A is not 100 items'))
 return cfg,prompts

def investigate():
 import transformers
 old_cfg,orig=split_data()
 if not (OLD/'checkpoint.pt').is_file() or not (OLD/'fitting_config.json').is_file():raise RuntimeError('original A checkpoint/config missing')
 if jread(OLD/'fitting_config.json')!=old_cfg:raise RuntimeError('original frozen config differs')
 s=checkpoint(OLD/'checkpoint.pt')
 n=int(s['next_idx']);k=int(s['n_done']);print('ORIGINAL A progress',dict(next_idx=n,n_done=k,skipped=n-k),flush=True)
 if n-k!=1:raise RuntimeError('Expected EXACTLY 1 skip so far; do NOT repair until reconciled')
 tok=transformers.AutoTokenizer.from_pretrained(old_cfg['model'],revision=old_cfg['revision'])
 bad=[]
 for i,t in enumerate(orig[:n]):
  ids=tok.encode(t,add_special_tokens=False,truncation=True,max_length=128)
  if len(ids)<=17:bad.append((i,len(ids),old_cfg['prompt_ids'][i]))
 print('Tokenizer short prefixes (diagnostic only):',bad,flush=True)
 return old_cfg,orig,s,bad

def pick_replacement(cfg,tok):
 from datasets import load_dataset
 ds=load_dataset('Salesforce/wikitext','wikitext-103-raw-v1',split='train')
 protected=set()
 for split in ('fit_A','fit_B','holdout'):
  for line in (ROOT/'prompts'/f'{split}.jsonl').read_text().splitlines():protected.add(json.loads(line)['text_sha256'])
 for row_num,r in enumerate(ds):
  t=canon(r['text']); h=hash_text(t)
  if h in protected or not (100<=len(t)<=1200) or re.match(r'^=+ .* =+$',t):continue
  ids=tok.encode(t,add_special_tokens=False,truncation=True,max_length=128)
  if len(ids)==128:return dict(text=t,text_sha256=h,row_index=row_num,token_count=128,source='Salesforce/wikitext/wikitext-103-raw-v1 train')
 raise RuntimeError('No 128-token replacement found')

def prepare():
 import transformers
 cfg,orig,s,bad=investigate()
 if NEW.exists():
  if not (NEW/'repair_manifest.json').is_file():raise RuntimeError('repair directory exists without manifest')
  print('REPAIR ALREADY PREPARED; audit instead. Refusing overwrite');return
 # n_done can be less than next_idx, but cannot change index or matrix sum
 tok=transformers.AutoTokenizer.from_pretrained(cfg['model'],revision=cfg['revision'])
 replacement=pick_replacement(cfg,tok)
 NEW.mkdir(parents=True,exist_ok=False)
 cp=NEW/'checkpoint.pt'
 shutil.copy2(OLD/'checkpoint.pt',cp)
 manifest=dict(protocol='A_APPEND_ONE_V1',original_checkpoint_sha256=sha(OLD/'checkpoint.pt'),seed_checkpoint_sha256=sha(cp),original_config_sha256=sha(OLD/'fitting_config.json'),
    original_prompt_ids=cfg['prompt_ids'],replacement=replacement,model=cfg['model'],revision=cfg['revision'],source_layers=LAYERS,
    target_layer=63,dim_batch=1,max_seq_len=128,skip_first=16,split_manifest_sha256=cfg['split_manifest_sha256'],
    original_next_idx=int(s['next_idx']),original_n_done=int(s['n_done']),original_skipped=1,
    runner_sha256=sha(BASE/'stage9_runner.py'),original_fullfit_sha256=sha(SRC),stage9_sha256=sha(BASE/'351_stage9.py'))
 atomic(NEW/'repair_manifest.json',manifest)
 print('REPAIR PREPARED:',NEW,'original',int(s['n_done']),'/',int(s['next_idx']),'replacement_row',replacement['row_index'],'new_total_indices=101,valid_goal=100',flush=True)

def audit():
 import torch
 cfg,orig=split_data();p=NEW/'repair_manifest.json'
 if not p.is_file():raise RuntimeError('Run prepare first')
 mf=jread(p); repl=mf['replacement']; ids=cfg['prompt_ids']
 if mf['original_prompt_ids']!=ids or mf['original_config_sha256']!=sha(OLD/'fitting_config.json'):raise RuntimeError('source original config/prefix changed')
 if repl['text_sha256']!=hash_text(repl['text']) or repl['token_count']!=128:raise RuntimeError('replacement hash invalid')
 other=set()
 for half in ('fit_A','fit_B','holdout'):
  for line in (ROOT/'prompts'/f'{half}.jsonl').read_text().splitlines():other.add(json.loads(line)['text_sha256'])
 if repl['text_sha256'] in other:raise RuntimeError('replacement overlaps frozen data')
 for f,key in ((BASE/'stage9_runner.py','runner_sha256'),(SRC,'original_fullfit_sha256'),(BASE/'351_stage9.py','stage9_sha256')):
  if sha(f)!=mf[key]:raise RuntimeError('SOURCE CHANGED '+str(f))
 s=checkpoint(NEW/'checkpoint.pt')
 if not (int(s['next_idx'])<=101 and int(s['n_done'])<=100 and int(s['next_idx'])-int(s['n_done'])==1):raise RuntimeError('A repair has unexpected skip count')
 if s['next_idx']==mf['original_next_idx'] and s['n_done']==mf['original_n_done'] and sha(NEW/'checkpoint.pt')!=mf['seed_checkpoint_sha256']:raise RuntimeError('seed checkpoint changed before progress')
 print('REPAIR AUDIT PASS next_idx',s['next_idx'],'n_done',s['n_done'],'target next_idx=101,n_done=100',flush=True)
 return mf,cfg,orig,s

def finish_if_ready(s, mf):
 import torch,jlens
 if int(s['next_idx'])!=101 or int(s['n_done'])!=100:return False
 lens_file=NEW/'lens.pt'
 if not lens_file.is_file():
  jac={layer:s['jacobian_sum'][layer].float()/100 for layer in LAYERS}
  jlens.JacobianLens(jacobians=jac,n_prompts=100,d_model=5120).save(str(lens_file))
 loaded=jlens.JacobianLens.load(str(lens_file))
 errs={}
 for layer in LAYERS:
  ref=s['jacobian_sum'][layer].float()/100; got=loaded.jacobians[layer].float().cpu()
  if ref.shape!=(5120,5120) or got.shape!=ref.shape or not bool(torch.isfinite(got).all()):raise RuntimeError(f'L{layer} bad shape/finite')
  err=(got-ref).norm().item()/max(ref.norm().item(),1e-12)
  if err>0.01:raise RuntimeError(f'L{layer} relative diff {err}>1%')
  errs[str(layer)]=err
 atomic(NEW/'final_status.json',dict(status='VERIFIED_100_VALID_OF_101_CANDIDATES',next_idx=101,n_done=100,skipped=1,lens_sha256=sha(lens_file),checkpoint_sha256=sha(NEW/'checkpoint.pt'),errors=errs,repair_manifest_sha256=sha(NEW/'repair_manifest.json')))
 print('REPAIRED A COMPLETE 100 VALID, 101 INDICES, lens SHA',sha(lens_file),flush=True)
 return True

def run(a):
 import torch,transformers,jlens,logging
 mf,cfg,orig,s=audit()
 n=int(s['next_idx']);done=int(s['n_done'])
 if n==101:
  finish_if_ready(s,mf);return
 if 'SLURM_JOB_ID' not in os.environ:raise RuntimeError('GPU execution requires Slurm job')
 if not a.confirm_fit:raise RuntimeError('Requires --confirm-fit')
 # Limit to a small prefix each call; relies on Slurm allocation remaining time.
 fullfit=load_module(SRC,'source_fullfit')
 remaining=fullfit.slurm_budget()
 nnew=min(a.max_new,max(0,(remaining-a.reserve_seconds)//a.seconds_per_prompt),101-n)
 if nnew<1:print('NO SAFE WINDOW; remaining seconds',remaining);return
 prompts=orig+[mf['replacement']['text']]
 target=n+nnew
 print('RESUME REPAIR from_index',n,'valid_count',done,'to_index',target,'target=101/100; Slurm remaining',remaining,flush=True)
 logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s: %(message)s',force=True)
 tok=transformers.AutoTokenizer.from_pretrained(cfg['model'],revision=cfg['revision'])
 hf=transformers.AutoModelForCausalLM.from_pretrained(cfg['model'],revision=cfg['revision'],torch_dtype=torch.bfloat16,device_map='auto',low_cpu_mem_usage=True)
 model=jlens.from_hf(hf,tok)
 fitted=jlens.fit(model,prompts[:target],source_layers=LAYERS,target_layer=63,dim_batch=1,max_seq_len=128,skip_first=16,checkpoint_path=str(NEW/'checkpoint.pt'),checkpoint_every=1,resume=True)
 del model,hf
 mf,cfg,orig,s=audit()
 if s['next_idx']!=target or s['n_done']!=target-1 or fitted.n_prompts!=target-1:raise RuntimeError('Unexpected additional skips or progress mismatch')
 if target==101:finish_if_ready(s,mf)
 else:print('REPAIR PARTIAL',s['n_done'],'valid /',s['next_idx'],'positions. Use SAME run command next allocation',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['inspect','prepare','check','run']);p.add_argument('--confirm-fit',action='store_true');p.add_argument('--max-new',type=int,default=12);p.add_argument('--seconds-per-prompt',type=int,default=450);p.add_argument('--reserve-seconds',type=int,default=900);a=p.parse_args()
 if a.command=='inspect':investigate()
 elif a.command=='prepare':prepare()
 elif a.command=='check':audit()
 else:run(a)
if __name__=='__main__':main()
