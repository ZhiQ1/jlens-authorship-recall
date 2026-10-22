#!/usr/bin/env python3
"""Stage 8 independent-target validation cohort + analysis-plan freeze (CPU only).
No scoring, no pilot-dependent outcomes used in sampling. Immutable manifests.
"""
import argparse,csv,hashlib,json,os,random,collections,datetime,math,unicodedata
from pathlib import Path

SEED=3518001
QUOTA={'low':25,'mid':50,'high':25}
LAYERS=[16,24,32,40,48,56,62]
PILOT_SHA_LABEL='pilot50_v1'

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for buf in iter(lambda:f.read(1024*1024),b''):h.update(buf)
 return h.hexdigest()
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with open(p,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())
def author_set(r):return {norm(z) for z in r['authors'].split(';') if z.strip()}
def citation_group(x):
 if x=='0-2':return 'low'
 n=int(x.split('-')[0].rstrip('+'))
 return 'high' if n>=129 else 'mid'
def rank_seed(*items):return int(hashlib.sha256('|'.join(map(str,items)).encode()).hexdigest()[:16],16)
def pair_cost(a,b):
 return (abs(int(a['year'])-int(b['year']))*10+abs(int(a['n_authors'])-int(b['n_authors']))*3,
         rank_seed(SEED,a['paper_id'],b['paper_id']))
def make_pairs(records,pilotids):
 bycell=collections.defaultdict(lambda:{'A':[],'B':[]})
 for r in records:
  if r['paper_id'] in pilotids or r['group'] not in ('A','B'):continue
  bycell[(r['field'],r['citation_bin'])][r['group']].append(r)
 # deterministic nearest-neighbor *without replacement*, field+bin exact, no common author.
 choices=[];rejections=collections.Counter()
 for (field,bin_),gr in sorted(bycell.items()):
  aa=sorted(gr['A'],key=lambda r:(int(r['year']),rank_seed(SEED,r['paper_id'])))
  bb=sorted(gr['B'],key=lambda r:(int(r['year']),rank_seed(SEED,r['paper_id'])))
  # Process underrepresented side first. Greedy matching is not maximum cardinality.
  left,right=(aa,bb) if len(aa)<=len(bb) else (bb,aa)
  remaining={r['paper_id']:r for r in right}
  for row in left:
   possible=[x for x in remaining.values() if author_set(x).isdisjoint(author_set(row))]
   if not possible:
    rejections['no_disjoint_candidate']+=1;continue
   chosen=min(possible,key=lambda x:pair_cost(row,x))
   del remaining[chosen['paper_id']]
   a,b=(row,chosen) if row['group']=='A' else (chosen,row)
   choices.append((citation_group(bin_),field,bin_,a,b))
 # Quotas applied *after* possible pairs have been generated, without inspecting model outputs.
 selected=[];available=collections.Counter(x[0] for x in choices)
 for category in ('low','mid','high'):
  items=[x for x in choices if x[0]==category]
  items.sort(key=lambda x:(pair_cost(x[3],x[4])[0],rank_seed(SEED,'select',x[3]['paper_id'],x[4]['paper_id'])))
  selected.extend(items[:QUOTA[category]])
 selected.sort(key=lambda x:('low','mid','high').index(x[0])*100000+rank_seed(SEED,x[3]['paper_id'],x[4]['paper_id'])%100000)
 rows=[];members=[]
 for i,(cat,field,bin_,a,b) in enumerate(selected,1):
  pid=f'S8P{i:03d}'
  rows.append(dict(pair_id=pid,citation_band=cat,field=field,citation_bin=bin_,A_id=a['paper_id'],B_id=b['paper_id'],year_gap=abs(int(a['year'])-int(b['year'])),author_count_gap=abs(int(a['n_authors'])-int(b['n_authors']))))
  for p in (a,b):members.append(dict(validation_id='stage8_v1',pair_id=pid,citation_band=cat,**p))
 return rows,members,available,rejections

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('command',choices=['freeze','audit','budget'])
 ap.add_argument('--stage5-root',default=None)
 ap.add_argument('--root',default=None)
 args=ap.parse_args()
 base=Path('/scratch')/os.getenv('USER','')/'jlens'
 s5=Path(args.stage5_root or base/'351_stage5_crossed_v2')
 root=Path(args.root or base/'351_stage8')
 input_files={'full_manifest':s5/'cohort/full_6841_manifest.csv','pilot50':s5/'cohort/pilot50_v1.csv'}
 for name,p in input_files.items():
  if not p.is_file():raise FileNotFoundError(f'{name}: {p}')
 manifest=root/'config/manifest.json'
 if manifest.exists():
  m=json.loads(manifest.read_text())
  for k,p in input_files.items():
   if digest(p)!=m['inputs'][k]:raise ValueError('INPUT HASH MISMATCH '+k)
  for rel,h in m['outputs'].items():
   if digest(root/rel)!=h:raise ValueError('FROZEN OUTPUT CHANGED '+rel)
  if m['seed']!=SEED or m['quotas']!=QUOTA:raise ValueError('Protocol changed')
  print('STAGE 8 VERIFIED',root,'pairs=',m['n_pairs'],'papers=',m['n_papers'],'manifest_sha256=',digest(manifest))
  return
 if args.command!='freeze':raise FileNotFoundError('Run freeze first')
 if root.exists() and any(root.iterdir()):raise FileExistsError('Nonempty non-frozen directory '+str(root))
 full=read(input_files['full_manifest']);pilot=read(input_files['pilot50'])
 if len(full)!=6841 or len(pilot)!=50:raise ValueError('Cohort size differs from frozen Stage 5')
 if collections.Counter(x['group'] for x in pilot)!= {'A':20,'B':20,'C':7,'D':3}:raise ValueError('Pilot group mismatch')
 pilotids={x['paper_id'] for x in pilot}
 pairs,papers,available,rejected=make_pairs(full,pilotids)
 if len({x['paper_id'] for x in papers})!=len(papers):raise AssertionError('Paper duplicated')
 if any(x['paper_id'] in pilotids for x in papers):raise AssertionError('Pilot overlap')
 if any(x['group'] not in ('A','B') for x in papers):raise AssertionError('Non A/B in confirmatory primary set')
 if not pairs:raise ValueError('No matched pairs')
 for sub in ('cohort','matching','config','reports','summary'): (root/sub).mkdir(parents=True,exist_ok=True)
 write(root/'matching/stage8_ab_pairs.csv',pairs,list(pairs[0]))
 write(root/'cohort/stage8_papers.csv',papers,list(papers[0]))
 balance={'requested_quotas':QUOTA,'available_greedy':dict(available),'actual':dict(collections.Counter(p['citation_band'] for p in pairs)),'rejections':dict(rejected), 'year_gap_mean':sum(int(p['year_gap']) for p in pairs)/len(pairs),'authors_gap_mean':sum(int(p['author_count_gap']) for p in pairs)/len(pairs),'excludes_pilot_target_ids':50}
 dump(root/'summary/matching_audit.json',balance)
 protocol={'status':'FROZEN_BEFORE_STAGE8_SCORING','protocol_version':'stage8_v1','seed':SEED,
 'pilot_exclusion':'all 50 Stage5 Pilot target paper IDs; possible shared original author-source universe remains a limitation',
 'sampling':'greedy nearest-year/author-count within exact field+citation_bin, disjoint listed author names; deterministic; without replacement; not globally optimal',
 'quota_pairs':QUOTA,'groups':{'A':'recognition-pass, free-recall R0','B':'recognition-fail, free-recall R0'},
 'layers':LAYERS,'final_reference_layer':63,'gold_candidate':'first listed ground-truth author',
 'main_readout':'J-Lens; Vanilla and Final as fixed comparators',
 'primary_endpoint':'paper-level mean over 7 layers of [true-title author-weighted first-token Gold Win Rate minus mean of 20 frozen shuffled-title win rates], 100 pre-frozen false authors (50 random,50 matched); ties=0.5',
 'primary_group_test':'within exact field+citation_bin matched A/B pairs; pair-bootstrap two-sided 95% CI on integrated A-B; paper pair is resampling unit',
 'primary_global_title_test':'paper-level integrated true-minus-shuffle J-Lens advantage; bootstrap papers, treating related-paper dependence as a limitation',
 'secondary_l56':'L56 advantage; exploratory pilot-selected layer, must be clearly labeled prior-discovery validation',
 'floor_primary':'low citation 0-2: paper-specific integrated true-minus-shuffle effect plus empirical tail fractions; compare to high 129+ among matched A/B pairs, control for group',
 'null_empirical_tail':'(1 + number of shuffled-context win rates >= true-context win rate)/(K+1), K=20; this is reference-tail fraction, not calibrated randomization p-value',
 'comparison':'J-Lens minus Vanilla within paper and context using identical candidate set',
 'sensitivity':['source-author false-pool overlap excluded','unique-first-token','noncollision','shuffle matching tiers','low-high by group','leave-one-pair-out'],
 'candidate_rule':'must be newly frozen solely from source metadata and tokenizer, with no Stage8 readout scores; false authors exclude all actual authors of target paper',
 'shuffle_rule':'20 title sources per target same field priority exact citation bin, year and token-length matching; exclude actual shared author; year held at target year',
 'data_leakage':'stage8 target papers excluded from prior pilot; source author/title pool overlaps must be logged; J-Lens and prompt design fixed before outcomes',
 'decision_boundary':'association not causal, first token not full-name identity, citation bin not direct training frequency; no selection by outcomes',
 'multiplicity':'primary 7-layer integrated one comparison; seven layer-specific comparisons exploratory and Holm-adjusted',
 'group_C_D':'retained in 6841 source table; not injected into matched A/B confirmatory test; optional independently labelled descriptive cohort in later version'}
 dump(root/'config/analysis_plan.json',protocol)
 (root/'reports/freeze_report.md').write_text('# Stage 8 freeze report\n\n'+f"Pairs: {len(pairs)}; Papers: {len(papers)}. Pilot overlap: 0.\n\n"+json.dumps(balance,indent=2)+'\n\nSampling and endpoints frozen *before new target-model scoring*. Do not infer confirmatory validity if any of these targets were used to tune the lens, prompt, or source exposure.\n',encoding='utf-8')
 outputs={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
 dump(manifest,{'version':'stage8_v1','seed':SEED,'quotas':QUOTA,'inputs':{k:digest(v) for k,v in input_files.items()},'outputs':outputs,'n_pairs':len(pairs),'n_papers':len(papers)})
 print('STAGE8 FREEZE SUCCESS',root,'pairs=',len(pairs),'papers=',len(papers),'bands=',balance['actual'],'available=',dict(available),'manifest_sha256=',digest(manifest))
 print('CPU only. Stage8 candidate selection and title freeze NOT RUN; Stage8 GPU scoring NOT RUN.')
if __name__=='__main__':main()
