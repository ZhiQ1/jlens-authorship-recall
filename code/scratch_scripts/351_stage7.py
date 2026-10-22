#!/usr/bin/env python3
"""Stage 7.1 CPU audit: decompose Stage 6 full-name conditional JMRR.
Does not run a model or modify Stage 6/5 frozen files.
"""
import argparse,csv,hashlib,json,math,random,statistics
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
LAYERS=[16,24,32,40,48,56,62]
MODES=['jlens','vanilla','final']
SEED=35171

def readcsv(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def writecsv(p,rows,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not fields: fields=list(rows[0]) if rows else []
 with open(p,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,o):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def ci(vals,seed,n):
 if not vals:return [None,None]
 arr=np.asarray(vals,dtype=float)
 rng=np.random.default_rng(seed)
 # resample independent matched pairs, not tokens/authors
 means=np.empty(n)
 for k in range(0,n,500):
  c=min(500,n-k)
  means[k:k+c]=arr[rng.integers(0,len(arr),size=(c,len(arr)))].mean(axis=1)
 return [float(x) for x in np.quantile(means,[0.025,0.975])]
def f(v):return float(v) if v is not None else None

def audit(args):
 root=Path(args.stage6_root).expanduser(); s5=Path(args.stage5_root).expanduser(); out=Path(args.output).expanduser()
 raw=root/'raw/pilot50_full_author.jsonl'; pairpath=s5/'matching/pilot50_ab_pairs.csv'
 if not raw.exists():raise SystemExit(f'Missing Stage6 raw: {raw}')
 if not pairpath.exists():raise SystemExit(f'Missing Stage5 pairs: {pairpath}')
 if (out.resolve()==root.resolve() or out.resolve()==s5.resolve()):raise SystemExit('Output must be separate from frozen stage5/6 roots')
 papers={}; nrows=0; failures=[]
 with open(raw,encoding='utf-8') as h:
  for lineno,line in enumerate(h,1):
   if not line.strip():continue
   d=json.loads(line);pid=d['paper_id']
   if pid in papers:failures.append(f'duplicate paper_id {pid}')
   papers[pid]=d;nrows+=len(d['rows'])
 if len(papers)!=50:failures.append(f'expected 50 papers, got {len(papers)}')
 if Counter(p['group'] for p in papers.values())!=Counter({'A':20,'B':20,'C':7,'D':3}):failures.append('unexpected group distribution')
 pairs=readcsv(pairpath)
 if len(pairs)!=20:failures.append(f'expected 20 pairs, got {len(pairs)}')
 for p in pairs:
  if p['A_id'] not in papers or p['B_id'] not in papers:failures.append('missing matched paper')
  elif papers[p['A_id']]['group']!='A' or papers[p['B_id']]['group']!='B':failures.append('bad pair labels')
  if p['A_id']==p['B_id']:failures.append('self pair')
 if failures:raise SystemExit('INPUT AUDIT FAILED: '+'; '.join(failures))
 out.mkdir(parents=True,exist_ok=True)
 # Equal weighting; within each author, first token and continuation tokens independently.
 paper_rows=[];author_rows=[];seen_count=Counter();len_stats=Counter()
 for pid,d in papers.items():
  by_author=defaultdict(list)
  for x in d['rows']:
   m=x['mode'];ly=int(x['layer']); idx=int(x['token_index']);rank=int(x['rank']);rr=float(x['rr'])
   if not math.isclose(rr,1.0/rank,abs_tol=1e-10,rel_tol=1e-9):failures.append(f'RR mismatch {pid} {m} {ly}')
   if (m=='final' and ly!=63) or (m!='final' and ly not in LAYERS):failures.append(f'unexpected layer {pid} {m} {ly}')
   by_author[(int(x['author_index']),x['author'],m,ly)].append((idx,rank,rr))
  group=d['group']; ainds={k[0] for k in by_author}
  if len(ainds)!=d['n_authors']:failures.append(f'author count mismatch {pid}')
  for (ai,name,m,ly),tokens in by_author.items():
   tokens.sort(key=lambda z:z[0]);ix=[z[0] for z in tokens]
   if ix!=list(range(len(ix))):failures.append(f'incomplete token indices: {pid} {ai} {m} L{ly}')
   seen_count[(pid,ai,m,ly)]+=1
   first=[tokens[0][2]];cont=[t[2] for t in tokens[1:]];allrr=[t[2] for t in tokens]
   author_rows.append(dict(paper_id=pid,group=group,author_index=ai,author=name,mode=m,layer=ly,n_tokens=len(tokens),first_rr=float(np.mean(first)),continuation_rr=float(np.mean(cont)) if cont else None,all_rr=float(np.mean(allrr)),first_log10rank=float(np.log10(tokens[0][1])),continuation_log10rank=float(np.mean([math.log10(t[1]) for t in tokens[1:]])) if cont else None,all_log10rank=float(np.mean([math.log10(t[1]) for t in tokens]))))
  for m in MODES:
   for ly in ([63] if m=='final' else LAYERS):
    ars=[a for a in author_rows if a['paper_id']==pid and a['mode']==m and a['layer']==ly]
    if len(ars)!=d['n_authors']:failures.append(f'missing author record {pid} {m} L{ly}')
    # continuation available only for multi-token authors. Do not artificially zero-fill one-token authors.
    cont=[a for a in ars if a['continuation_rr'] is not None]
    len_stats[(group,m,ly,'all')]+=len(ars)
    len_stats[(group,m,ly,'continuation')]+=len(cont)
    paper_rows.append(dict(paper_id=pid,group=group,source=d.get('source'),mode=m,layer=ly,n_authors=len(ars),n_continuation_authors=len(cont),n_first_tokens=len(ars),n_continuation_tokens=sum(a['n_tokens']-1 for a in ars),first_jmrr=float(np.mean([a['first_rr'] for a in ars])),continuation_jmrr=float(np.mean([a['continuation_rr'] for a in cont])) if cont else None,all_jmrr=float(np.mean([a['all_rr'] for a in ars])),first_log10rank=float(np.mean([a['first_log10rank'] for a in ars])),continuation_log10rank=float(np.mean([a['continuation_log10rank'] for a in cont])) if cont else None,all_log10rank=float(np.mean([a['all_log10rank'] for a in ars]))))
 if failures:raise SystemExit('RAW QUALITY AUDIT FAILED: '+'; '.join(failures[:12]))
 # Check original all-JMRR against Stage6 saved summaries.
 old=root/'summary/paper_layer_trajectories.csv';comparison=None
 if old.exists():
  oldrows=readcsv(old);print('Previous Stage6 summary columns:',list(oldrows[0]))
  # Find expected columns defensively rather than silently bypass mismatch.
  keys=list(oldrows[0]); keycol=next((k for k in ['jmrr','paper_jmrr','mean_rr'] if k in keys),None)
  if keycol:
   oldmap={(r['paper_id'],r['mode'],int(r['layer'])):float(r[keycol]) for r in oldrows}
   differences=[abs(r['all_jmrr']-oldmap[(r['paper_id'],r['mode'],r['layer'])]) for r in paper_rows if (r['paper_id'],r['mode'],r['layer']) in oldmap]
   if len(differences)!=len(paper_rows):raise SystemExit(f'Historical comparison only {len(differences)}/{len(paper_rows)} records')
   comparison={'rows_checked':len(differences),'max_abs_difference':max(differences)}
   if comparison['max_abs_difference']>1e-8:raise SystemExit(f'Stage6 recompute mismatch: {comparison}')
 writecsv(out/'raw/author_token_position_scores.csv',author_rows)
 writecsv(out/'summary/paper_layer_decomposition.csv',paper_rows)
 lookup={(r['paper_id'],r['mode'],r['layer']):r for r in paper_rows}
 diffs=[]
 for pair in pairs:
  for m in MODES:
   for ly in ([63] if m=='final' else LAYERS):
    A=lookup[(pair['A_id'],m,ly)];B=lookup[(pair['B_id'],m,ly)]
    for metric in ['first_jmrr','continuation_jmrr','all_jmrr','first_log10rank','continuation_log10rank','all_log10rank']:
     av=A[metric];bv=B[metric]
     diffs.append(dict(pair_id=pair['pair_id'],A_id=pair['A_id'],B_id=pair['B_id'],mode=m,layer=ly,metric=metric,A=av,B=bv,difference=av-bv if av is not None and bv is not None else None,A_n_continuation_authors=A['n_continuation_authors'],B_n_continuation_authors=B['n_continuation_authors']))
 writecsv(out/'summary/matched_pair_position_differences.csv',diffs)
 effects=[]
 for m in MODES:
  for ly in ([63] if m=='final' else LAYERS):
   for metric in ['first_jmrr','continuation_jmrr','all_jmrr','first_log10rank','continuation_log10rank','all_log10rank']:
    v=[d['difference'] for d in diffs if d['mode']==m and d['layer']==ly and d['metric']==metric and d['difference'] is not None]
    effects.append(dict(mode=m,layer=ly,metric=metric,n_pairs=len(v),A_minus_B_mean=float(np.mean(v)) if v else None,median_difference=float(np.median(v)) if v else None,n_positive=sum(x>0 for x in v),bootstrap_ci_low=ci(v,SEED+ly+len(metric),args.bootstrap)[0] if v else None,bootstrap_ci_high=ci(v,SEED+ly+len(metric),args.bootstrap)[1] if v else None))
 writecsv(out/'summary/layer_position_effects.csv',effects)
 # integrated by paper (7-layer equal weights) and then pair (same paper pairs)
 integ=[]
 for pair in pairs:
  for m in ['jlens','vanilla']:
   for metric in ['first_jmrr','continuation_jmrr','all_jmrr']:
    a=[lookup[(pair['A_id'],m,l)][metric] for l in LAYERS];b=[lookup[(pair['B_id'],m,l)][metric] for l in LAYERS]
    av=float(np.mean(a)) if all(x is not None for x in a) else None
    bv=float(np.mean(b)) if all(x is not None for x in b) else None
    integ.append(dict(pair_id=pair['pair_id'],mode=m,metric=metric,A=av,B=bv,difference=av-bv if av is not None and bv is not None else None))
 writecsv(out/'summary/matched_integrated_position_differences.csv',integ)
 for m in ['jlens','vanilla']:
  for metric in ['first_jmrr','continuation_jmrr','all_jmrr']:
   v=[x['difference'] for x in integ if x['mode']==m and x['metric']==metric and x['difference'] is not None]
   lo,hi=ci(v,SEED+len(metric)+len(m),args.bootstrap)
   effects.append(dict(mode=m,layer='integrated_7',metric=metric,n_pairs=len(v),A_minus_B_mean=float(np.mean(v)) if v else None,median_difference=float(np.median(v)) if v else None,n_positive=sum(x>0 for x in v),bootstrap_ci_low=lo,bootstrap_ci_high=hi))
 writecsv(out/'summary/layer_and_integrated_effects.csv',effects)
 # source subgroup diagnostics (reuse/new): avoid using this as causal or group-adjusted evidence
 source_rows=[]
 for m in ['jlens','vanilla']:
  for metric in ['first_jmrr','continuation_jmrr','all_jmrr']:
   for grp in ['A','B','C','D']:
    for source in ['stage4_verified_reuse','stage6_gpu']:
     vals=[r[metric] for r in paper_rows if r['mode']==m and r['group']==grp and r['source']==source and r['layer']==62 and r[metric] is not None]
     source_rows.append(dict(group=grp,source=source,mode=m,layer=62,metric=metric,n_papers=len(vals),mean=float(np.mean(vals)) if vals else None))
 writecsv(out/'summary/reuse_vs_new_diagnostic.csv',source_rows)
 (out/'figures').mkdir(parents=True,exist_ok=True)
 for mode in ['jlens','vanilla']:
  fig,ax=plt.subplots(figsize=(9,5))
  for metric,label in [('first_jmrr','First token'),('continuation_jmrr','Continuation tokens'),('all_jmrr','All tokens')]:
   row=[x for x in effects if x['mode']==mode and x['metric']==metric and isinstance(x['layer'],int) and x['layer'] in LAYERS]
   row.sort(key=lambda z:z['layer']);x=[q['layer'] for q in row]
   y=[q['A_minus_B_mean'] for q in row];ax.plot(x,y,marker='o',label=label)
   ax.fill_between(x,[q['bootstrap_ci_low'] for q in row],[q['bootstrap_ci_high'] for q in row],alpha=.12)
  ax.axhline(0,linestyle='--',linewidth=.8);ax.set_xticks(LAYERS);ax.set_xlabel('Source Layer');ax.set_ylabel('Matched A − B mean JMRR');ax.set_title(f'Stage 7.1 | {mode} · First vs Continuation');ax.legend();fig.tight_layout()
  for ext in ['png','pdf']:fig.savefig(out/f'figures/{mode}_first_vs_continuation.{ext}',dpi=180)
  plt.close(fig)
 # conclusion report factual; no automatic significance claims
 lines=['# Stage 7.1 — Token-position Decomposition (CPU Only)','',f'- Stage6 raw: `{raw}` (SHA256 `{sha(raw)}`)',f'- Matching: `{pairpath}` (SHA256 `{sha(pairpath)}`)',f'- Papers: {len(papers)}, raw scored rows: {nrows}, matched pairs: {len(pairs)}',f'- Equal-weight Token→Author→Paper; 7-layer integrated; {args.bootstrap} pair-bootstrap replicates (seed {SEED}).',f'- Historical Stage6 JMRR reconciliation: `{comparison}`.','','## Main matched effects','', '| Readout | Position | n paired | Integrated A−B | 95% bootstrap CI | Positive pairs |','|---|---|---:|---:|---|---:|']
 for x in effects:
  if x['layer']=='integrated_7':
   lines.append(f"| {x['mode']} | {x['metric']} | {x['n_pairs']} | {x['A_minus_B_mean']:.6f} | [{x['bootstrap_ci_low']:.6f}, {x['bootstrap_ci_high']:.6f}] | {x['n_positive']} |")
 lines+=['','## L62 effects','', '| Readout | Position | n paired | A−B | 95% bootstrap CI | Positive pairs |','|---|---|---:|---:|---|---:|']
 for x in effects:
  if x['layer']==62 and x['metric'] in ('first_jmrr','continuation_jmrr','all_jmrr'):
   lines.append(f"| {x['mode']} | {x['metric']} | {x['n_pairs']} | {x['A_minus_B_mean']:.6f} | [{x['bootstrap_ci_low']:.6f}, {x['bootstrap_ci_high']:.6f}] | {x['n_positive']} |")
 lines+=['','## Interpretation boundaries','', '- First-token score is measured without any revealed tokens of the *current* author, but for later listed authors the surrounding prompt may still contain earlier author names if that is how Stage4/6 constructed it; inspect the frozen prompt protocol before making a truly unconditioned claim.','- Continuation scores condition on a revealed correct-name prefix. They do not establish free recall of the full author identity.','- A/B comparisons are observational; split and integrated layer results are exploratory.','- Multi-token and one-token authors differ: continuation JMRR excludes authors with no continuation; each paper records the eligible count.','- A large JMRR at L62 and positive A−B, if found, does not by itself prove factual title–author association. Stage 7.2 matched false-author and title-shuffle controls are needed.','- Bootstrap CIs are paper-pair resampling. Pair dependence through shared authors/candidate sources has not been corrected.','', '## Files','', '- `summary/layer_and_integrated_effects.csv`: full effects and bootstrap CIs','- `summary/matched_pair_position_differences.csv`: per-pair per-layer differences','- `summary/paper_layer_decomposition.csv`: per-paper all/first/continuation metrics','- `raw/author_token_position_scores.csv`: per-author metrics','- `figures/`: PNG/PDF trajectory figures','']
 (out/'reports').mkdir(parents=True,exist_ok=True)
 (out/'reports/experiment_report.md').write_text('\n'.join(lines),encoding='utf-8')
 dump(out/'config/audit_manifest.json',dict(stage='stage7.1',raw_stage6=str(raw),raw_sha256=sha(raw),pairs=str(pairpath),pairs_sha256=sha(pairpath),layers=LAYERS,groups={'A':20,'B':20,'C':7,'D':3},seed=SEED,bootstrap=args.bootstrap,stage6_reconciliation=comparison,notes='CPU retrospective decomposition; no model invoked'))
 print('STAGE 7.1 COMPLETE papers=',len(papers),'raw_rows=',nrows,'pairs=',len(pairs),'output=',out)
 print('\n'.join(lines[lines.index('## Main matched effects')+2:lines.index('## L62 effects')-1]))
 print('\n'.join(lines[lines.index('## L62 effects')+2:lines.index('## Interpretation boundaries')-1]))

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--stage6-root',default=None)
 ap.add_argument('--stage5-root',default=None)
 ap.add_argument('--output',default=None)
 ap.add_argument('--bootstrap',type=int,default=10000)
 a=ap.parse_args()
 base=Path('/scratch')/Path.home().name/'jlens'
 a.stage6_root=a.stage6_root or str(base/'351_stage6')
 a.stage5_root=a.stage5_root or str(base/'351_stage5_crossed_v2')
 a.output=a.output or str(base/'351_stage7_1')
 audit(a)
if __name__=='__main__':main()
