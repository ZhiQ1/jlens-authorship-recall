#!/usr/bin/env python3
"""Stage 8D: frozen independent validation; CPU-only analysis."""
import argparse,collections,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np

LAYERS=[16,24,32,40,48,56,62]
MODES=[f'{kind}_L{l}' for kind in ('jlens','vanilla') for l in LAYERS]+['final_L63']
SEED=3518401
NBOOT=10000

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def readcsv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))

def writecsv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:raise ValueError('Refusing to write empty CSV '+str(p))
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]))
  w.writeheader()
  w.writerows(rows)

def writejson(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n')

def bootstrap(v,seed):
 a=np.asarray(v,dtype=float)
 if not len(a) or not np.isfinite(a).all():
  raise ValueError('Invalid bootstrap values')
 rng=np.random.default_rng(seed)
 samples=np.empty(NBOOT)
 for i in range(0,NBOOT,500):
  n=min(500,NBOOT-i)
  samples[i:i+n]=a[rng.integers(0,len(a),(n,len(a)))].mean(axis=1)
 return dict(n=len(a),mean=float(a.mean()),
             median=float(np.median(a)),
             ci_low=float(np.quantile(samples,.025)),
             ci_high=float(np.quantile(samples,.975)),
             positive=int((a>0).sum()),
             negative=int((a<0).sum()),
             zero=int((a==0).sum()))

def win(score,gold,neg):
 g=score[gold]
 return sum(1.0 if g>score[x] else
            0.5 if g==score[x] else 0.0 for x in neg)/len(neg)

def validate(root):
 cfg=root/'config'
 m8a=cfg/'manifest.json'
 m8b=cfg/'stage8B_manifest.json'
 runtime=cfg/'stage8C_runtime.json'
 for p in (m8a,m8b,runtime):
  if not p.is_file():raise FileNotFoundError(p)

 bm=json.loads(m8b.read_text())
 if bm['stage8A_manifest_sha256']!=sha(m8a):
  raise RuntimeError('Stage8A checksum mismatch')
 for name,digest in bm['files'].items():
  if sha(root/name)!=digest:
   raise RuntimeError('Stage8B frozen file changed: '+name)

 rc=json.loads(runtime.read_text())
 if rc['stage8A_sha256']!=sha(m8a) or rc['stage8B_sha256']!=sha(m8b):
  raise RuntimeError('Stage8C input checksums mismatch')
 if rc['public_lens_sha256']!='0af5ccf2e1c251bedc202607a7ca214f3b9f60980bab73d67a3d0b887db213d8':
  raise RuntimeError('Unexpected public lens')
 if rc['layers']!=LAYERS or set(rc['modes'])!=set(MODES):
  raise RuntimeError('Unexpected layers or modes')

 papers=readcsv(root/'cohort/stage8_papers.csv')
 pairs=readcsv(root/'matching/stage8_ab_pairs.csv')
 cand=readcsv(root/'controls/stage8_author_candidates.csv')
 shuffles=readcsv(root/'controls/stage8_shuffled_titles.csv')

 bypaper={x['paper_id']:x for x in papers}
 if len(papers)!=200 or len(bypaper)!=200:
  raise RuntimeError('Bad paper count')
 if collections.Counter(x['group'] for x in papers)!={'A':100,'B':100}:
  raise RuntimeError('Bad A/B count')
 if collections.Counter(x['citation_band'] for x in papers)!={'low':50,'mid':100,'high':50}:
  raise RuntimeError('Bad citation-band counts')
 if len(pairs)!=100 or len({x['pair_id'] for x in pairs})!=100:
  raise RuntimeError('Bad matched pairs')

 pairids=set()
 for x in pairs:
  A,B=x['A_id'],x['B_id']
  if A not in bypaper or B not in bypaper:
   raise RuntimeError('Pair references unknown paper')
  if bypaper[A]['group']!='A' or bypaper[B]['group']!='B':
   raise RuntimeError('Pair group mismatch')
  if bypaper[A]['citation_band']!=x['citation_band'] or bypaper[B]['citation_band']!=x['citation_band']:
   raise RuntimeError('Pair citation band mismatch')
  if bypaper[A]['citation_bin']!=bypaper[B]['citation_bin'] or bypaper[A]['field']!=bypaper[B]['field']:
   raise RuntimeError('Pair exact matching broken')
  pairids.update((A,B))
 if pairids!=set(bypaper):
  raise RuntimeError('Pairs do not cover each paper exactly once')

 ca=collections.defaultdict(list)
 for x in cand:ca[x['paper_id']].append(x)
 if len(cand)!=20200 or set(ca)!=set(bypaper):
  raise RuntimeError('Candidate coverage invalid')

 falseids={}
 goldids={}
 for pid,rs in ca.items():
  c=collections.Counter(x['pool'] for x in rs)
  if c!={'gold':1,'matched':50,'random':50}:
   raise RuntimeError('Candidate pool invalid '+pid)
  if len({int(x['candidate_index']) for x in rs})!=101:
   raise RuntimeError('Candidate indexing invalid '+pid)
  goldids[pid]=int(next(x['first_token_id'] for x in rs if x['pool']=='gold'))
  falseids[pid]={
   pool:[int(x['first_token_id']) for x in rs if x['pool']==pool]
   for pool in ('matched','random')
  }

 titles={}
 if len(shuffles)!=4000:raise RuntimeError('Bad title count')
 for x in shuffles:
  key=(x['paper_id'],int(x['shuffle_index']))
  if key in titles:raise RuntimeError('Duplicate title control '+str(key))
  titles[key]=x
 for pid in bypaper:
  if {i for p,i in titles if p==pid}!=set(range(1,21)):
   raise RuntimeError('Title controls incomplete '+pid)

 rawpath=root/'raw/stage8C_context_scores.jsonl'
 raw={}
 with rawpath.open(encoding='utf-8') as f:
  for line_no,line in enumerate(f,1):
   if not line.endswith('\n'):
    raise RuntimeError('Truncated raw line '+str(line_no))
   x=json.loads(line)
   pid=x['paper_id'];ix=int(x['shuffle_index'])
   key=(pid,ix)
   if pid not in bypaper or ix not in range(21) or key in raw:
    raise RuntimeError('Foreign or duplicate context '+str(key))
   if x['group']!=bypaper[pid]['group']:
    raise RuntimeError('Context group mismatch '+str(key))
   if ix==0:
    if x['source_paper_id']!=pid:
     raise RuntimeError('True-title source mismatch '+pid)
   elif x['source_paper_id']!=titles[key]['source_paper_id']:
    raise RuntimeError('Wrong-title source mismatch '+str(key))
   if x['protocol_hash']!=rc['protocol_hash'] or x['runtime_hash']!=rc['runtime_hash']:
    raise RuntimeError('Context protocol mismatch '+str(key))
   expected=sorted(set([goldids[pid]]+falseids[pid]['matched']+falseids[pid]['random']))
   ids=x['first_token_ids']
   if ids!=expected or set(x['score_by_mode'])!=set(MODES):
    raise RuntimeError('Candidate IDs or modes mismatch '+str(key))
   scores={}
   for mode,v in x['score_by_mode'].items():
    if len(v)!=len(ids) or not all(math.isfinite(float(z)) for z in v):
     raise RuntimeError('Invalid scores '+str(key))
    scores[mode]=dict(zip(ids,map(float,v)))
   x['_scores']=scores
   raw[key]=x
 if len(raw)!=4200 or set(raw)!={(p,i) for p in bypaper for i in range(21)}:
  raise RuntimeError(f'Raw incomplete {len(raw)}/4200')

 return bypaper,pairs,ca,titles,raw,falseids,goldids,rc

def analyze(root):
 papers,pairs,ca,titles,raw,falseids,goldids,rc=validate(root)
 print('STAGE8D INTEGRITY PASS: 200 papers, 100 pairs, 4200 contexts, 15 modes',flush=True)

 summarydir=root/'stage8D/summary'
 figdir=root/'stage8D/figures'
 reportdir=root/'stage8D/reports'
 figdir.mkdir(parents=True,exist_ok=True)

 contextrows=[]
 paperrows=[]
 lookup={}
 for pid,p in sorted(papers.items()):
  neg= falseids[pid]['matched']+falseids[pid]['random']
  g=goldids[pid]
  for mode in MODES:
   true=win(raw[(pid,0)]['_scores'][mode],g,neg)
   noncoll=[x for x in neg if x!=g]
   if not noncoll:
    raise RuntimeError('All candidates collide with gold '+pid)
   true_non=win(raw[(pid,0)]['_scores'][mode],g,noncoll)
   null=[]
   for ix in range(1,21):
    t=titles[(pid,ix)]
    n=win(raw[(pid,ix)]['_scores'][mode],g,neg)
    nc=win(raw[(pid,ix)]['_scores'][mode],g,noncoll)
    contextrows.append(dict(
     paper_id=pid,group=p['group'],citation_band=p['citation_band'],
     citation_bin=p['citation_bin'],mode=mode,
     shuffle_index=ix,source_paper_id=t['source_paper_id'],
     title_token_gap=int(t['title_token_gap']),
     source_author_in_false_pool=int(t['source_author_in_false_pool']),
     true_win=true,null_win=n,advantage=true-n,
     true_noncollision=true_non,null_noncollision=nc))
    null.append((n,nc,t))
   mean_null=float(np.mean([x[0] for x in null]))
   nonadv=true_non-float(np.mean([x[1] for x in null]))
   no_overlap=[x[0] for x in null if int(x[2]['source_author_in_false_pool'])==0]
   short_title=[x[0] for x in null if int(x[2]['title_token_gap'])<=10]
   r=dict(
    paper_id=pid,group=p['group'],citation_band=p['citation_band'],
    citation_bin=p['citation_bin'],field=p['field'],mode=mode,
    true_win=true,null_mean=mean_null,title_advantage=true-mean_null,
    noncollision_advantage=nonadv,
    n_first_token_collisions=len(neg)-len(noncoll),
    n_no_source_overlap=len(no_overlap),
    advantage_no_source_overlap=(true-float(np.mean(no_overlap))) if no_overlap else float('nan'),
    n_short_title=len(short_title),
    advantage_short_title=(true-float(np.mean(short_title))) if short_title else float('nan'),
    null_percentile_midrank=(sum(x[0]<true for x in null)+.5*sum(x[0]==true for x in null))/20,
    descriptive_tail=(1+sum(x[0]>=true for x in null))/21)
   paperrows.append(r)
   lookup[(pid,mode)]=r

 writecsv(summarydir/'context_level_scores.csv',contextrows)
 writecsv(summarydir/'paper_layer_advantage.csv',paperrows)

 pairrows=[]
 for x in pairs:
  for mode in MODES:
   av=lookup[(x['A_id'],mode)]['title_advantage']
   bv=lookup[(x['B_id'],mode)]['title_advantage']
   pairrows.append(dict(
    pair_id=x['pair_id'],citation_band=x['citation_band'],mode=mode,
    A_id=x['A_id'],B_id=x['B_id'],
    A_advantage=av,B_advantage=bv,A_minus_B=av-bv))
 writecsv(summarydir/'matched_pair_differences.csv',pairrows)

 primary=[]
 l56=[r for r in paperrows if r['mode']=='jlens_L56']
 r1=bootstrap([x['title_advantage'] for x in l56],SEED+1)
 primary.append(dict(question='RQ1_L56_replication',mode='jlens_L56',contrast='True_minus_20_wrong_titles',**r1))

 ab=[x for x in pairrows if x['mode']=='jlens_L56']
 r2=bootstrap([x['A_minus_B'] for x in ab],SEED+2)
 primary.append(dict(question='RQ2_matched_A_minus_B',mode='jlens_L56',contrast='matched_A_minus_B',**r2))

 low=[x for x in ab if x['citation_band']=='low']
 high=[x for x in ab if x['citation_band']=='high']
 if len(low)!=25 or len(high)!=25:
  raise RuntimeError('Low/high pair count mismatch')
 # Group-balanced Low-minus-High: averaging both A and B, cluster on matched pairs.
 def pairavg(x):return (x['A_advantage']+x['B_advantage'])/2
 lv=np.asarray([pairavg(x) for x in low])
 hv=np.asarray([pairavg(x) for x in high])
 rng=np.random.default_rng(SEED+3)
 boot=np.empty(NBOOT)
 for i in range(0,NBOOT,500):
  n=min(500,NBOOT-i)
  boot[i:i+n]=lv[rng.integers(0,25,(n,25))].mean(axis=1)-hv[rng.integers(0,25,(n,25))].mean(axis=1)
 r3=dict(n=50,mean=float(lv.mean()-hv.mean()),
         median=float(np.median(lv)-np.median(hv)),
         ci_low=float(np.quantile(boot,.025)),
         ci_high=float(np.quantile(boot,.975)),
         positive=int((lv>0).sum()),negative=int((lv<0).sum()),
         zero=int((lv==0).sum()))
 primary.append(dict(question='RQ3_low_minus_high',mode='jlens_L56',contrast='pair_balanced_low_minus_high',**r3))
 writecsv(summarydir/'primary_questions.csv',primary)

 secondary=[]
 for mode in MODES:
  rr=[r for r in paperrows if r['mode']==mode]
  z=bootstrap([r['title_advantage'] for r in rr],SEED+11+MODES.index(mode))
  secondary.append(dict(scope='all_papers',mode=mode,band='all',**z))
  for band in ('low','mid','high'):
   z=bootstrap([r['title_advantage'] for r in rr if r['citation_band']==band],SEED+100+MODES.index(mode)*3+('low','mid','high').index(band))
   secondary.append(dict(scope='citation_band',mode=mode,band=band,**z))
 writecsv(summarydir/'layer_and_band_summary.csv',secondary)

 # J-Lens minus Vanilla title-specific increment, paired within each paper.
 diffs=[
  lookup[(pid,'jlens_L56')]['title_advantage']-
  lookup[(pid,'vanilla_L56')]['title_advantage']
  for pid in sorted(papers)
 ]
 inc=bootstrap(diffs,SEED+4)
 writecsv(summarydir/'jlens_minus_vanilla.csv',[
  dict(mode='L56_JLens_minus_Vanilla',**inc)
 ])

 sensitivity=[]
 for metric in ('title_advantage','noncollision_advantage',
                'advantage_no_source_overlap','advantage_short_title'):
  vals=[float(r[metric]) for r in l56 if math.isfinite(float(r[metric]))]
  if vals:
   sensitivity.append(dict(metric=metric,**bootstrap(vals,SEED+500+len(sensitivity))))
 writecsv(summarydir/'sensitivity.csv',sensitivity)

 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for kind in ('jlens','vanilla'):
  fig,ax=plt.subplots(figsize=(8,5))
  for group in ('A','B'):
   y=[np.mean([r['title_advantage'] for r in paperrows if r['mode']==f'{kind}_L{layer}' and r['group']==group]) for layer in LAYERS]
   ax.plot(LAYERS,y,marker='o',label=group)
  ax.axhline(0,color='gray',linewidth=.8)
  ax.set(title=f'Stage 8 independent validation — {kind}',
         xlabel='Layer',ylabel='True title − matched wrong-title mean win')
  ax.legend()
  fig.tight_layout()
  for ext in ('png','pdf'):
   fig.savefig(figdir/f'{kind}_seven_layers.{ext}',dpi=180)
  plt.close(fig)

 fig,ax=plt.subplots(figsize=(7,5))
 for band in ('low','mid','high'):
  vals=[r['title_advantage'] for r in l56 if r['citation_band']==band]
  ax.boxplot(vals,positions=[('low','mid','high').index(band)+1],widths=.5)
 ax.axhline(0,color='gray',linewidth=.8)
 ax.set(xticks=[1,2,3],xticklabels=['Low','Middle','High'],
        ylabel='L56 title-specific advantage',
        title='Stage 8 — J-Lens L56 by citation band')
 fig.tight_layout()
 for ext in ('png','pdf'):
  fig.savefig(figdir/f'jlens_L56_citation_bands.{ext}',dpi=180)
 plt.close(fig)

 lines=['# Stage 8 — Independent Validation Results','',
        '## Integrity',
        '200 unique papers, 100 matched A/B pairs, 4,200 unique scored contexts and 15 score modes verified.',
        '',
        '## Predeclared primary analyses',
        '',
        '| Question | Estimate | 95% bootstrap CI | N |',
        '|---|---:|---|---:|']
 for r in primary:
  lines.append(f"| {r['question']} | {r['mean']:+.6f} | [{r['ci_low']:+.6f}, {r['ci_high']:+.6f}] | {r['n']} |")
 lines+=['','## J-Lens vs Vanilla (L56)','',
         f"Mean increment: {inc['mean']:+.6f}, 95% CI [{inc['ci_low']:+.6f}, {inc['ci_high']:+.6f}].",
         '','## Interpretation boundaries','',
         '- First-token candidate discrimination is not full author identity recovery.',
         '- Wrong-title controls are metadata-selected, not exchangeable permutations; empirical tails are descriptive, not calibrated p-values.',
         '- A/B matching is observational; differences are not causal effects of recognition.',
         '- Multiple layers and sensitivity measures are descriptive; L56 is the predeclared main layer.',
         '- Zero-crossing confidence intervals do not prove equivalence or absence of an effect.',
         '- J-Lens superiority must be tested against Vanilla, not assumed.',
         '- The sampled low-citation distribution cannot alone establish a universal accessibility floor.',
         '']
 reportdir.mkdir(parents=True,exist_ok=True)
 (reportdir/'stage8_results.md').write_text('\n'.join(lines),encoding='utf-8')

 output_files=sorted(
  [p for p in (root/'stage8D').rglob('*') if p.is_file() and p.name!='output_manifest.json']
 )
 writejson(root/'stage8D/output_manifest.json',{
  'stage8C_raw_sha256':sha(root/'raw/stage8C_context_scores.jsonl'),
  'stage8A_manifest_sha256':sha(root/'config/manifest.json'),
  'stage8B_manifest_sha256':sha(root/'config/stage8B_manifest.json'),
  'runtime_sha256':sha(root/'config/stage8C_runtime.json'),
  'bootstrap_seed':SEED,
  'bootstrap_replicates':NBOOT,
  'files':{str(p.relative_to(root)):sha(p) for p in output_files}
 })
 print('\nPRIMARY RESULTS')
 for r in primary:
  print(r['question'],f"mean={r['mean']:+.6f}",
        f"95%CI=[{r['ci_low']:+.6f},{r['ci_high']:+.6f}]")
 print('J-LENS MINUS VANILLA',f"{inc['mean']:+.6f}",
       f"[{inc['ci_low']:+.6f},{inc['ci_high']:+.6f}]")
 print('STAGE 8D ANALYSIS SAVED:',root/'stage8D',flush=True)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('command',choices=['audit','analyze'])
 ap.add_argument('--root',type=Path,
  default=Path('/scratch')/os.getenv('USER','')/'jlens/351_stage8')
 a=ap.parse_args()
 if a.command=='audit':
  validate(a.root)
  print('STAGE8D INTEGRITY PASS: 200 papers / 100 pairs / 4200 contexts / 15 modes')
 else:
  analyze(a.root)

if __name__=='__main__':
 main()
