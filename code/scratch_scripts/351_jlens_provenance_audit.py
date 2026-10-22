#!/usr/bin/env python3
"""Read-only, CPU-only J-Lens fitting/evaluation leakage & protocol audit.
Two checkpoint files are inspected only for metadata; existing fitting and result artifacts are never changed.
"""
import argparse, csv, hashlib, json, os, re, sys, unicodedata
from pathlib import Path
from collections import Counter

ROOT=Path('/scratch')/os.getenv('USER','unknown')/'jlens'
LAYERS=[24,32,40,48,56,62]
REV='9216db5781bf21249d130ec9da846c4624c16137'

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def norm(t):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',t).casefold()).strip()
def words(t):return re.findall(r"[\w']+",norm(t))
def grams(t,n=8):
 w=words(t)
 return {' '.join(w[i:i+n]) for i in range(max(0,len(w)-n+1))}

def load_jsonl(path):
 if not path.exists():return []
 with open(path,encoding='utf-8-sig') as f:return [json.loads(s) for s in f if s.strip()]

def inspection_checkpoint(path,name):
 info={'checkpoint':name,'path':str(path),'exists':path.exists()}
 if not path.exists():return info
 info.update({'bytes':path.stat().st_size,'sha256':digest(path)})
 try:
  import torch
  d=torch.load(str(path),map_location='cpu',weights_only=True,mmap=True)
  if not isinstance(d,dict):return info|{'error':'not a dict'}
  info['keys']=list(map(str,d.keys()))
  if 'jacobian_sum' in d:
   info['schema']='running_jacobian_sum_checkpoint'
   info['n_prompts']=int(d.get('n_done',-1));info['source_layers']=sorted(map(int,d['jacobian_sum'].keys()))
   info['normalization']='raw sum: mean requires jacobian_sum/n_done'
  elif 'J' in d or 'jacobians' in d:
   info['schema']='finished_lens'
   j=d.get('J',d.get('jacobians',{}));info['source_layers']=sorted(map(int,j.keys()))
   info['n_prompts']=int(d.get('n_prompts',-1))
   info['normalization']='already averaged lens weights (verify upstream saver)'
  else:info['schema']='unknown';info['normalization']='unverified'
  if 'provenance' in d:
   prov=d['provenance'];info['provenance']=prov if isinstance(prov,(str,dict,list,float,int,bool,type(None))) else str(type(prov))
  del d
 except Exception as exc: info['error']=f'{type(exc).__name__}: {exc}'
 return info

def read_config(path):
 if not path.exists():return {'path':str(path),'exists':False}
 txt=path.read_text(encoding='utf8');d={'path':str(path),'exists':True,'sha256':digest(path)}
 try:
  import yaml
  d['parsed']=yaml.safe_load(txt)
 except Exception as exc:d['warning']=f'YAML parse missing: {exc}';d['text_excerpt']=txt[:3500]
 return d

def overlap_rows(fit,ev,split):
 ftext=[norm(x['text']) for x in fit if isinstance(x.get('text'),str)]
 whole={s for s in ftext if s}
 token_index={}
 for i,txt in enumerate(ftext):
  for gram in grams(txt,8): token_index.setdefault(gram,set()).add(i)
 out=[]
 for item in ev:
  txt=norm(item.get('prompt',''))
  if not txt:continue
  matches=[]
  for s in set([txt]):
   matches=[i for i,v in enumerate(ftext) if s and len(s)>=30 and (s in v or v in s and len(v)>=30)]
  hits=Counter()
  for g in grams(txt,8):
   for i in token_index.get(g,[]):hits[i]+=1
  top=hits.most_common(1)
  out.append({'eval_type':split,'item_id':str(item.get('id','')),'eval_prompt_sha256':hashlib.sha256(txt.encode()).hexdigest(),
   'exact_normalized_match':txt in whole,'contains_long_substring':bool(matches),
   'n_shared_8grams_max':top[0][1] if top else 0,
   'best_fitting_index':top[0][0] if top else None,
   'lexical_overlap_flag':bool(matches) or bool(top),
   'note':'8-word overlap is a manual-review flag, not proof of leakage; titles in templated paper prompts can cause spurious matches'})
 return out

def write_csv(path,rows,keys):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:r.get(k) for k in keys} for r in rows])

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--root',type=Path,default=ROOT)
 ap.add_argument('--public-lens',type=Path)
 ap.add_argument('--public-config',type=Path)
 ap.add_argument('--self-lens',type=Path)
 ap.add_argument('--out',type=Path)
 ap.add_argument('--no-weight-read',action='store_true',help='Skip CPU mmap reads of large torch lens files')
 a=ap.parse_args()
 root=a.root; public=a.public_lens or root/'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'
 config=a.public_config or public.parent/'config.yaml';selflens=a.self_lens or root/'qwen32b_jlens_prelim_100.pt'
 out=a.out or root/'351_provenance_audit';(out/'summary').mkdir(parents=True,exist_ok=True);(out/'raw').mkdir(exist_ok=True);(out/'reports').mkdir(exist_ok=True);(out/'figures').mkdir(exist_ok=True)
 ownconf=read_config(root/'qwen32b_jlens_prelim_100_config.json');pubconf=read_config(config)
 # JSON config is not YAML on all environments - use standard json for the local config
 if (root/'qwen32b_jlens_prelim_100_config.json').exists():ownconf['parsed']=json.loads((root/'qwen32b_jlens_prelim_100_config.json').read_text())
 ck={}
 for label,path in [('self100',selflens),('neuronpedia',public)]:
  ck[label]=inspection_checkpoint(path,label) if not a.no_weight_read else {'checkpoint':label,'path':str(path),'exists':path.exists(),'not_read':'--no-weight-read'}
 corpus=root/'fitting_corpus/wikitext103_qwen32b_1000.jsonl';manifest=root/'fitting_corpus/manifest.json'
 rows=load_jsonl(corpus);man=json.loads(manifest.read_text()) if manifest.exists() else {}
 self_meta={'fitting_corpus':str(corpus),'exists':corpus.exists(),'n_corpus_rows':len(rows),'n_selected':min(100,len(rows)),'corpus_sha256':digest(corpus) if corpus.exists() else None,'manifest_matches_corpus':bool(corpus.exists() and man.get('corpus_sha256')==digest(corpus))}
 evalsets={}
 for typ,path in [('generic',root/'351_self100_validation/raw/generic.jsonl'),('paper',root/'351_self100_validation/raw/paper.jsonl')]:
  evalsets[typ]={'path':str(path),'rows':load_jsonl(path)}
  if not evalsets[typ]['rows']:
   pubpath=root/('351_all/351_public_fidelity.jsonl' if typ=='generic' else '351_all/351_paper_prompt_fidelity.jsonl')
   evalsets[typ]={'path':str(pubpath),'rows':load_jsonl(pubpath)}
 all_overlap=[]
 for typ,data in evalsets.items():
  ev=[]
  for j,r in enumerate(data['rows']):
   p=r.get('prompt');ev.append({'id':r.get('id',r.get('paper_id',r.get('prompt_index',j))),'prompt':p})
  all_overlap+=overlap_rows(rows[:100],ev,typ)
 keys=['eval_type','item_id','eval_prompt_sha256','exact_normalized_match','contains_long_substring','n_shared_8grams_max','best_fitting_index','lexical_overlap_flag','note']
 write_csv(out/'raw/self_fitting_vs_evaluation_overlap.csv',all_overlap,keys)
 own=ownconf.get('parsed',{}) or {};pub=pubconf.get('parsed',{}) or {}
 pd=pub.get('dataset',{}) if isinstance(pub,dict) else {}; fit=pub.get('fit',{}) if isinstance(pub,dict) else {}
 report=[
 '# Audit 3 & 4 — Data leakage and fitting protocol', '',
 '## Artifact authenticity / actual fitting count',
 f'- Self file SHA256: `{ck["self100"].get("sha256","not available")}`; schema `{ck["self100"].get("schema","unknown")}`; recorded n={ck["self100"].get("n_prompts","unknown")}.',
 f'- Public file SHA256: `{ck["neuronpedia"].get("sha256","not available")}`; schema `{ck["neuronpedia"].get("schema","unknown")}`; recorded n={ck["neuronpedia"].get("n_prompts","unknown")}.',
 '- CAUTION: historical Neuronpedia Qwen3-32B checkpoint (80 prompts) was replaced by a finalized 557-prompt artifact in 2026. Do not infer the actual local file version from its filename.',
 '- The public fit version is confirmed only if local checkpoint schema/n_prompts and SHA256 are recorded. The comparison must be tied to this exact SHA256 used in prior tests.',
 '', '## Audit 3 — Fitting / evaluation leakage',
 f'- Self fit corpus: `{corpus}`; SHA256 `{self_meta["corpus_sha256"]}`; manifest integrity: `{self_meta["manifest_matches_corpus"]}`.',
 '- Self fit selection is exactly indices 0–99 from the saved 1,000-row JSONL; there is no randomized selection in the 100-prompt fitting script.',
 f'- Available evaluation records: generic {len(evalsets["generic"]["rows"])}, paper {len(evalsets["paper"]["rows"])}.',
 f'- Self-fit vs evaluation: {sum(bool(x["exact_normalized_match"]) for x in all_overlap)} exact prompt matches, {sum(bool(x["lexical_overlap_flag"]) for x in all_overlap)} lexical review flags among {len(all_overlap)} evaluation examples.',
 '- Exact normalized-match test and 8-word lexical overlap only measure text reuse of the available fitted prompt strings. They do NOT establish distribution independence or absence of latent / source-document overlap.',
 '- Public Neuronpedia: no 557 individual fitting prompt strings supplied by public checkpoint or config; per-prompt exact overlap **UNDETERMINED** until its original fitting text/indices are obtained.',
 '- Training split shared provenance (WikiText-103) can create distribution overlap even with zero exact evaluation-prompt matches. Self fit uses WikiText and paper-title prompts represent different tasks; this is not necessarily direct leakage.',
 '', '## Audit 4 — Protocol comparability',
 '- See `summary/protocol_comparison.csv` for evidence-status rows; public config is read if present (otherwise marked unknown).',
 '- `dim_batch` is a backward-pass vectorization/memory control, not a weighting hyperparameter in the released estimator; a different value is not by itself proof of a different mathematical estimator. Numerical equivalence still depends on implementation and floating-point behavior.',
 '- A public `prompts_fitted` count from config cannot override local checkpoint metadata; verify artifact version and any refit provenance.',
 '- The released `jlens.fitting.fit` accumulates a per-prompt Jacobian sum and divides by number of valid prompts. Reproducing the public wrapper may require checking its own implementation and library revision.',
 '- Model revision in the self100 script was pinned via the fitting-corpus manifest; if the public fitting model revision is absent, model-name equality is insufficient to claim identical weights.',
 '', '## Interpretation / restrictions',
 '- Both audits are provenance checks, not GPU performance experiments. No original outputs or weights are overwritten.',
 '- Do not infer that the 100-prompt fit outperforms a 557-prompt fit *because of* fitting size. Other protocol differences and fit-version effects remain confounded.',
 '- Public 557-prompt training-text exact membership remains unavailable locally; record as unverifiable unless original prompt list is obtained.',
 ]
 selfparams={'model':'Qwen/Qwen3-32B','model_revision':own.get('model_revision',REV),'fitting_prompt_count':ck['self100'].get('n_prompts',100),'source_layers':own.get('source_layers',LAYERS),'target_layer':own.get('target_layer',63),'skip_first':own.get('skip_first',16),'dim_batch':own.get('dim_batch',8),'max_seq_len':own.get('max_seq_len',128),'dataset':'WikiText-103 corpus JSONL (manifest-pinned)','dataset_split':'inspect manifest.json','prompt_selection':'first 100 of stored 1000','jacobian_average':'unweighted mean over successfully fitted prompts','early_stopping':'none (fixed 100)'}
 publicparams={'model':pub.get('hf_model_name','unknown'),'model_revision':pub.get('model_revision',pub.get('revision','unknown')),'fitting_prompt_count':ck['neuronpedia'].get('n_prompts',pub.get('results',{}).get('prompts_fitted','unknown')),'source_layers':ck['neuronpedia'].get('source_layers','unknown'),'target_layer':fit.get('target_layer',pub.get('target_layer','unknown')),'skip_first':fit.get('skip_first',pub.get('skip_first','unknown')),'dim_batch':fit.get('dim_batch',pub.get('dim_batch','unknown')),'max_seq_len':fit.get('max_seq_len',pub.get('max_seq_len','unknown')),'dataset':pd,'dataset_split':pd.get('split','unknown'),'prompt_selection':'public fitting prompts not supplied','jacobian_average':'verify public source / wrapper','early_stopping':fit.get('stop_at_delta',pub.get('stop_at_delta','unknown'))}
 comp=[]
 for key in selfparams:
  a0,b0=selfparams[key],publicparams.get(key,'unknown')
  known=b0 not in (None,'unknown','')
  comp.append({'parameter':key,'self100':json.dumps(a0,ensure_ascii=False),'neuronpedia':json.dumps(b0,ensure_ascii=False),'status':('SAME' if a0==b0 else 'DIFFERENT') if known else 'UNKNOWN_PUBLIC','note':('verified from local artifacts or configuration; inspect source revision for exact implementation' if known else 'not verifiable from available provenance')})
 write_csv(out/'summary/protocol_comparison.csv',comp,['parameter','self100','neuronpedia','status','note'])
 summary={'self_meta':self_meta,'checkpoint':ck,'public_config':pubconf,'self_config':ownconf,'eval_file_paths':{k:v['path'] for k,v in evalsets.items()},'eval_counts':{k:len(v['rows']) for k,v in evalsets.items()},'overlap_counts':{'evaluations_checked':len(all_overlap),'exact':sum(bool(x['exact_normalized_match']) for x in all_overlap),'lexical_flags':sum(bool(x['lexical_overlap_flag']) for x in all_overlap)},'protocol':comp,'limitations':['Neuronpedia fitting texts unavailable for exact matching','Config may not match checkpoint revision; compare actual hashes']}
 (out/'summary/audit_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,default=str))
 (out/'reports/audit_report.md').write_text('\n'.join(report)+'\n',encoding='utf8')
 try:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  counts=Counter(x['status'] for x in comp)
  fig,ax=plt.subplots(figsize=(7,3.8)); categories=['SAME','DIFFERENT','UNKNOWN_PUBLIC'];ax.bar(categories,[counts[x] for x in categories]);ax.set_ylabel('Number of protocol fields');ax.set_title('Protocol audit: agreement vs unresolved');fig.tight_layout()
  fig.savefig(out/'figures/protocol_status.png',dpi=180);fig.savefig(out/'figures/protocol_status.pdf');plt.close(fig)
  fig,ax=plt.subplots(figsize=(7,3.8));ts=['generic','paper'];vv=[sum(x['lexical_overlap_flag'] for x in all_overlap if x['eval_type']==t) for t in ts];ax.bar(ts,vv);ax.set_ylabel('Number of lexical 8-gram overlap flags');ax.set_title('Self-100 fit vs available evaluation prompts');fig.tight_layout()
  fig.savefig(out/'figures/lexical_overlap_flags.png',dpi=180);fig.savefig(out/'figures/lexical_overlap_flags.pdf');plt.close(fig)
 except Exception as exc:print('PLOT_SKIPPED',exc,flush=True)
 print('AUDIT COMPLETE:',out,flush=True)
 print('SELF',ck['self100'].get('schema'),ck['self100'].get('n_prompts'),'PUBLIC',ck['neuronpedia'].get('schema'),ck['neuronpedia'].get('n_prompts'),flush=True)
 print('OVERLAP',summary['overlap_counts'],'EVAL COUNTS',summary['eval_counts'],flush=True)
 print('READ',out/'reports/audit_report.md',flush=True)

if __name__=='__main__':main()
