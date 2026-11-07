#!/usr/bin/env python3
"""Stage 9 lens fitting reliability: immutable WikiText split -> guarded fit -> checkpoint audit.
This is NOT a claim that the two fits have been executed. Run preflight first on Explorer.
"""
import argparse, collections, hashlib, inspect, json, os, random, re, sys, time
from pathlib import Path

MODEL='Qwen/Qwen3-32B'
REVISION='9216db5781bf21249d130ec9da846c4624c16137'
LAYERS=[16,24,32,40,48,56,62]
SEED=3519001

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def jdump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')

def readjson(p):return json.loads(p.read_text(encoding='utf-8'))

def canonical(s):return ' '.join(s.split()).strip()

def sampled_corpus(args):
 if args.text_file:
  source=Path(args.text_file)
  if not source.is_file():raise FileNotFoundError(source)
  if source.resolve().is_relative_to(args.root.resolve()):raise ValueError('Source cannot be in output directory')
  # One paragraph per nonempty line; SHA of original file retained.
  lines=source.read_text(encoding='utf-8').splitlines()
  return lines,dict(kind='local_text',path=str(source.resolve()),sha256=sha(source))
 try:
  from datasets import load_dataset
 except ImportError as e:raise SystemExit('Install datasets in jlens env or pass --text-file with licensed WikiText lines') from e
 ds=load_dataset('Salesforce/wikitext','wikitext-103-raw-v1',split='train')
 return [x['text'] for x in ds],dict(kind='huggingface',dataset='Salesforce/wikitext',config='wikitext-103-raw-v1',split='train',revision=str(getattr(ds.info,'version','unknown')))

def prepare(a):
 root=a.root; mf=root/'config/manifest.json'
 if mf.exists():return audit(a)
 if root.exists() and any(root.iterdir()):raise RuntimeError('Nonempty unmanifested root; do not overwrite '+str(root))
 # Strip MediaWiki section markers, exclude tiny fragments; dedup exact text to prevent train/half overlap.
 lines,source=sampled_corpus(a)
 unique={}
 for line in lines:
  s=canonical(line)
  if len(s)<a.min_chars or len(s)>a.max_chars or re.match(r'^=+ .* =+$',s):continue
  h=hashlib.sha256(s.encode('utf-8')).hexdigest()
  unique.setdefault(h,s)
 needed=2*a.n_per_half+a.n_holdout
 if len(unique)<needed:raise RuntimeError(f'Not enough unique lines {len(unique)}; need {needed}. Nothing frozen.')
 rng=random.Random(SEED)
 keys=sorted(unique);rng.shuffle(keys)
 selected=keys[:needed]
 slices={'fit_A':selected[:a.n_per_half], 'fit_B':selected[a.n_per_half:2*a.n_per_half], 'holdout':selected[2*a.n_per_half:]}
 for k,ids in slices.items():
  path=root/'prompts'/f'{k}.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('w',encoding='utf-8') as f:
   for pid in ids:f.write(json.dumps({'text_sha256':pid,'text':unique[pid]},ensure_ascii=False)+'\n')
 plan={'version':'stage9_split_v1','seed':SEED,'source':source,'counts':{k:len(v) for k,v in slices.items()},'model':MODEL,'revision':REVISION,'layers':LAYERS,
       'prompt_length':'plain WikiText line, min/max characters; actual tokenizer lengths must be audited on Explorer',
       'split':'SHA256 dedup before split; nonoverlapping fit_A/fit_B/holdout; no scientific-paper outcomes used',
       'checkpoint_sizes':list(sorted(set([min(20,a.n_per_half),min(50,a.n_per_half),min(100,a.n_per_half),a.n_per_half]))),
       'interpretation':'fit_A vs fit_B measures sampling stability, NOT independence from public-lens training examples; checkpoint-size comparison is only comparable under matched fit settings',
       'status':'SPLITS_ONLY_NOT_FITTED'}
 jdump(root/'config/plan.json',plan)
 outputs={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
 jdump(mf,{'outputs':outputs,'plan_sha':sha(root/'config/plan.json'),'counts':plan['counts']})
 print('STAGE 9 SPLITS FROZEN',plan['counts'],'manifest_sha256',sha(mf),'NO FIT PERFORMED')
 return audit(a)

def audit(a):
 root=a.root;mf=root/'config/manifest.json'
 if not mf.is_file():raise FileNotFoundError('prepare first')
 manifest=readjson(mf)
 for name,digest in manifest['outputs'].items():
  p=root/name
  if not p.is_file() or sha(p)!=digest:raise RuntimeError('Frozen data changed: '+name)
 sets={}
 for name in ('fit_A','fit_B','holdout'):
  p=root/'prompts'/f'{name}.jsonl'
  arr=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
  ids=[x['text_sha256'] for x in arr]
  if len(ids)!=len(set(ids)):raise RuntimeError('Intra-split duplicate '+name)
  if any(hashlib.sha256(x['text'].encode()).hexdigest()!=x['text_sha256'] for x in arr):raise RuntimeError('Payload hash mismatch '+name)
  sets[name]=set(ids)
 for x,y in [('fit_A','fit_B'),('fit_A','holdout'),('fit_B','holdout')]:
  if sets[x]&sets[y]:raise RuntimeError(f'Split leakage: {x},{y}')
 print('STAGE 9 AUDIT PASS', {x:len(v) for x,v in sets.items()},'manifest_sha256',sha(mf))

def preflight(a):
 audit(a)
 try:
  import torch,transformers,jlens
 except ImportError as e:raise RuntimeError('Explorer environment missing dependency: '+str(e))
 print('Python',sys.version.split()[0], 'torch',torch.__version__,'transformers',transformers.__version__,'jlens',getattr(jlens,'__version__','unknown'))
 print('CUDA available',torch.cuda.is_available(),'devices',torch.cuda.device_count())
 if not hasattr(jlens,'fit') or not callable(jlens.fit):raise RuntimeError('Installed jlens has no jlens.fit')
 sig=inspect.signature(jlens.fit)
 print('jlens.fit signature',sig)
 params=sig.parameters
 for k in ('model','prompts'):
  if k not in params and not any(p.kind==inspect.Parameter.VAR_KEYWORD for p in params.values()):raise RuntimeError('Incompatible fit API; missing '+k)
 if 'checkpoint_path' not in params and not any(p.kind==inspect.Parameter.VAR_KEYWORD for p in params.values()):raise RuntimeError('Checkpoint API incompatible: inspect before running')
 lens_path=Path(a.public_lens)
 if not lens_path.is_file():raise FileNotFoundError('Public lens missing '+str(lens_path))
 print('PUBLIC LENS',lens_path,'bytes',lens_path.stat().st_size,'sha256',sha(lens_path))
 print('READY FOR SMALL FIT SMOKE, NOT YET VERIFIED FIT OR GPU MEMORY')

def validate_fit_args(a):
 if not a.source_layers or len(set(a.source_layers)) != len(a.source_layers) or any(l < 0 or l >= 63 for l in a.source_layers):
  raise ValueError('source layers must be unique integers 0..62; target is final L63')
 if a.dim_batch < 1 or a.max_seq_len <= a.skip_first or a.skip_first < 0:
  raise ValueError('invalid fitting dimension batch or token window')
 if a.n_fit < 1: raise ValueError('n-fit must be positive')

def verify_checkpoint(path, config):
 import torch
 state=torch.load(str(path),map_location='cpu',weights_only=True)
 required=('jacobian_sum','n_done','next_idx','source_layers','target_layer','skip_first')
 if any(k not in state for k in required):raise RuntimeError('Incomplete fitting checkpoint')
 if list(state['source_layers'])!=config['source_layers'] or state['target_layer']!=config['target_layer'] or state['skip_first']!=config['skip_first']:
  raise RuntimeError('Checkpoint hyperparameter mismatch')
 if state['next_idx'] > config['n_fit'] or state['n_done'] > state['next_idx'] or state['n_done'] < 1:
  raise RuntimeError('Checkpoint count invalid')
 if set(state['jacobian_sum']) != set(config['source_layers']):raise RuntimeError('Checkpoint layer keys mismatch')
 for layer,t in state['jacobian_sum'].items():
  if t.shape != (5120,5120) or not torch.isfinite(t).all():raise RuntimeError(f'Invalid matrix for layer {layer}')
 return state

def verify_saved_fit(out, config, write_marker=True):
 """Validate a saved lens against the float32 checkpoint mean, allowing lossy on-disk dtype."""
 import torch, jlens
 cfg=out/'fitting_config.json';ck=out/'checkpoint.pt'; lens_file=out/'lens.pt';marker=out/'fit_status.json'
 if not cfg.is_file() or not ck.is_file() or not lens_file.is_file():
  raise FileNotFoundError('Need fitting_config.json, checkpoint.pt and lens.pt for verification')
 if readjson(cfg)!=config:raise RuntimeError('Frozen fit configuration differs; refusing verification')
 state=verify_checkpoint(ck,config)
 n=config['n_fit']
 if state['next_idx']!=n or state['n_done']!=n:raise RuntimeError(f'Incomplete checkpoint: next={state["next_idx"]} done={state["n_done"]} expected={n}')
 lens=jlens.JacobianLens.load(str(lens_file))
 if set(lens.jacobians)!=set(config['source_layers']):raise RuntimeError('Reloaded layer set mismatch')
 checks={}
 for layer in config['source_layers']:
  ref=(state['jacobian_sum'][layer].float()/n).cpu()
  loaded=lens.jacobians[layer].detach().float().cpu()
  if ref.shape!=(5120,5120) or loaded.shape!=ref.shape:raise RuntimeError(f'Wrong matrix shape L{layer}')
  if not torch.isfinite(ref).all() or not torch.isfinite(loaded).all():raise RuntimeError(f'Nonfinite matrix L{layer}')
  error=(loaded-ref)
  norm=ref.norm().item()
  relative=error.norm().item()/max(norm,1e-12)
  max_error=error.abs().max().item()
  loaded_dtype=str(lens.jacobians[layer].dtype)
  # Most lens serialization paths use fp16/bf16; exact float32 equality is invalid across lossy storage.
  # Relative Frobenius error <=1% is a conservative fidelity gate, NOT proof of matching readout behavior.
  if relative>0.01:raise RuntimeError(f'Lens L{layer} failed numerical fidelity: relative_l2={relative:.6g}, dtype={loaded_dtype}')
  checks[str(layer)]={'serialized_dtype':loaded_dtype,'checkpoint_mean_dtype':str(ref.dtype),
      'relative_l2_error':relative,'max_abs_error':max_error,'reference_l2_norm':norm}
 if write_marker:
  jdump(marker,{'status':'FIT_SAVED_AND_RELOADED_NUMERICALLY_VERIFIED','fit_config_sha256':sha(cfg),'half':config['half'],
      'n_prompts':n,'lens_sha256':sha(lens_file),'checkpoint_sha256':sha(ck),
      'matrix_layers':config['source_layers'],'roundtrip_checks':checks})
 print('FIT VERIFIED',marker,'lens SHA',sha(lens_file),'roundtrip',checks,flush=True)
 return checks

def fit(a):
 validate_fit_args(a)
 preflight(a)
 if not a.confirm_fit:raise RuntimeError('Fit requires --confirm-fit')
 import torch,transformers,jlens
 rows=[json.loads(s) for s in (a.root/'prompts'/f'fit_{a.half}.jsonl').read_text().splitlines() if s]
 if a.n_fit>len(rows):raise RuntimeError('n-fit exceeds frozen half')
 n=a.n_fit;prompts=[r['text'] for r in rows[:n]]
 ids=[r['text_sha256'] for r in rows[:n]]
 config={'half':a.half,'n_fit':n,'prompt_ids':ids,'source_layers':a.source_layers,'target_layer':63,
         'dim_batch':a.dim_batch,'max_seq_len':a.max_seq_len,'skip_first':a.skip_first,
         'model':MODEL,'revision':REVISION,'split_manifest_sha256':sha(a.root/'config/manifest.json')}
 layer_label='-'.join(map(str,a.source_layers))
 out=a.root/'fits'/f'{a.half}_n{n:04d}_layers_{layer_label}'
 out.mkdir(parents=True,exist_ok=True)
 cfg_file=out/'fitting_config.json'; ck=out/'checkpoint.pt'; lens_file=out/'lens.pt';marker=out/'fit_status.json'
 if marker.exists():raise RuntimeError('Final fit already verified; refusing overwrite '+str(out))
 if lens_file.exists():
  print('EXISTING LENS FOUND: verifying previous fit without running GPU',flush=True)
  verify_saved_fit(out,config)
  return
 if cfg_file.exists():
  if readjson(cfg_file)!=config:raise RuntimeError('Existing fit configuration differs; checkpoint cannot be resumed safely')
  if not a.resume:raise RuntimeError('Fit state exists; pass --resume to continue')
  if not ck.exists():raise RuntimeError('Config exists without checkpoint; inspect incomplete run')
  state=verify_checkpoint(ck,config)
  print('CHECKPOINT RESUME VALIDATED next_idx=',state['next_idx'],'n_done=',state['n_done'])
 elif ck.exists():raise RuntimeError('Unbound checkpoint exists: refusing resume')
 else:jdump(cfg_file,config)
 print('FIT CONFIG',json.dumps({k:v for k,v in config.items() if k!='prompt_ids'}),flush=True)
 print('LOADING MODEL; fitting uses 1+ Jacobians per token and may OOM',flush=True)
 tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REVISION)
 model_hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,torch_dtype=torch.bfloat16,device_map='auto',low_cpu_mem_usage=True)
 model=jlens.from_hf(model_hf,tok)
 start=time.monotonic()
 fitted=jlens.fit(model,prompts=prompts,source_layers=a.source_layers,target_layer=63,
                  dim_batch=a.dim_batch,max_seq_len=a.max_seq_len,skip_first=a.skip_first,
                  checkpoint_path=str(ck),checkpoint_every=1,resume=a.resume)
 if getattr(fitted,'n_prompts',None)!=n:raise RuntimeError(f'Not all prompts fitted: n_prompts={getattr(fitted,"n_prompts",None)} expected={n}; do not mark success')
 state=verify_checkpoint(ck,config)
 if state['n_done']!=n or state['next_idx']!=n:raise RuntimeError(f'Checkpoint incomplete: next={state["next_idx"]} completed={state["n_done"]}, expected={n}')
 if set(fitted.jacobians)!=set(a.source_layers):raise RuntimeError('Fitted layer set mismatch')
 for layer,m in fitted.jacobians.items():
  if m.shape!=(5120,5120) or not torch.isfinite(m).all():raise RuntimeError(f'Bad fitted matrix L{layer}')
 fitted.save(str(lens_file))
 verify_saved_fit(out,config)

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('command',choices=['prepare','audit','preflight','fit'])
 ap.add_argument('--root',type=Path,default=Path('/scratch')/os.getenv('USER','')/'jlens/351_stage9')
 ap.add_argument('--text-file',help='Optional local WikiText source (one text passage per line). Otherwise use Salesforce/wikitext train.')
 ap.add_argument('--n-per-half',type=int,default=100)
 ap.add_argument('--n-holdout',type=int,default=100)
 ap.add_argument('--min-chars',type=int,default=100)
 ap.add_argument('--max-chars',type=int,default=1200)
 ap.add_argument('--public-lens',default=str(Path('/scratch')/os.getenv('USER','')/'jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'))
 ap.add_argument('--half',choices=['A','B'],default='A');ap.add_argument('--n-fit',type=int,default=2);ap.add_argument('--confirm-fit',action='store_true')
 ap.add_argument('--source-layers',type=int,nargs='+',default=LAYERS)
 ap.add_argument('--dim-batch',type=int,default=1);ap.add_argument('--max-seq-len',type=int,default=128)
 ap.add_argument('--skip-first',type=int,default=16);ap.add_argument('--resume',action='store_true')
 a=ap.parse_args()
 if a.n_per_half<2 or a.n_holdout<1 or a.min_chars<1 or a.max_chars<a.min_chars:ap.error('Invalid split parameters')
 if a.command=='prepare':prepare(a)
 elif a.command=='audit':audit(a)
 elif a.command=='preflight':preflight(a)
 else:fit(a)
if __name__=='__main__':main()
