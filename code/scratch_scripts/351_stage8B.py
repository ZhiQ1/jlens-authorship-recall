
#!/usr/bin/env python3

"""Stage 8B CPU-only: freeze independent-validation wrong-author and wrong-title controls.

Never reads Stage 8 readout scores. Does not touch Stage 8A manifest.

"""

import argparse,csv,hashlib,json,random,re,collections,os,sys

from pathlib import Path



SEED=3518201

CHEAD='paper_id group citation_bin field year pool candidate_index candidate_name candidate_name_normalized first_token_id n_name_tokens all_token_ids gold_first_token_id first_token_collision gold_n_name_tokens name_token_count_gap match_tier nearest_same_field_year_gap source_paper_id source_field source_year source_is_pilot source_paper_count'.split()

THEAD='paper_id group citation_bin field year true_title true_title_tokens shuffle_index shuffled_title source_paper_id source_field source_citation_bin source_year shuffled_title_tokens match_tier year_gap title_token_gap source_author_in_false_pool source_author_overlap_gold_paper shuffle_prompt_year'.split()



def digest(p):

 h=hashlib.sha256()

 with open(p,'rb') as f:

  for b in iter(lambda:f.read(1<<20),b''):h.update(b)

 return h.hexdigest()



def jsonwrite(p,obj):

 p.parent.mkdir(parents=True,exist_ok=True)

 p.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n')



def readcsv(p):

 with p.open(encoding='utf-8-sig',newline='') as f:

  return list(csv.DictReader(f))



def writecsv(p,rows,header):

 p.parent.mkdir(parents=True,exist_ok=True)

 with p.open('w',encoding='utf-8',newline='') as f:

  w=csv.DictWriter(f,fieldnames=header,extrasaction='ignore')

  w.writeheader()

  w.writerows(rows)



def norm(x):

 return ' '.join(x.casefold().strip().split())



def authors(x):

 return [s.strip() for s in re.split(r'\s*;\s*',x or '') if s.strip()]



def rank(*s):

 return int(hashlib.sha256(('|'.join(map(str,s))).encode()).hexdigest()[:16],16)



def get_paths(a):

 root=a.root

 cohort=root/'cohort/stage8_papers.csv'

 full=a.full

 if not cohort.is_file():

  raise RuntimeError(f'Missing Stage 8A cohort: {cohort}')

 if not full.is_file():

  raise RuntimeError(f'Missing Stage 5 full manifest: {full}; pass --full')

 return cohort,full



def controls(a):

 root=a.root

 manifest=root/'config/manifest.json'

 if not manifest.is_file():

  raise RuntimeError('Stage 8A manifest missing')

 cfile,fullfile=get_paths(a)

 rows=readcsv(cfile)

 full=readcsv(fullfile)



 if len(rows)!=200 or collections.Counter(r['group'] for r in rows)!={'A':100,'B':100}:

  raise RuntimeError('Stage 8 cohort must be 100 A +100 B')



 ids=[r['paper_id'] for r in rows]

 if len(set(ids))!=200:

  raise RuntimeError('Stage 8 paper ids not unique')



 fmap={r['paper_id']:r for r in full}

 if len(fmap)!=len(full):

  raise RuntimeError('Duplicate full manifest paper ids')



 for r in rows:

  src=fmap.get(r['paper_id'])

  if not src:

   raise RuntimeError('Cohort missing from full manifest '+r['paper_id'])

  for key in ('title','field','citation_bin','group','year'):

   if str(r.get(key,''))!=str(src.get(key,'')):

    raise RuntimeError(f'Cohort-full mismatch {key} {r["paper_id"]}')



 from transformers import AutoTokenizer

 tok=AutoTokenizer.from_pretrained(a.tokenizer,revision=a.revision)



 def tokens(name):

  return tok.encode(' '+name,add_special_tokens=False)



 members=collections.defaultdict(list)

 names={}

 source_count=collections.Counter()



 for r in full:

  for name in authors(r['authors']):

   key=norm(name)

   if not key:

    continue

   names.setdefault(key,name)

   members[key].append(r)

   source_count[key]+=1



 if len(names)<200:

  raise RuntimeError('Author pool implausibly small')



 allnames=sorted(names)

 global_meta={k:tokens(names[k]) for k in allnames}

 title_tok={

  r['paper_id']:len(tok.encode(r['title'],add_special_tokens=False))

  for r in full

 }

 name_fields={k:{r['field'] for r in members[k]} for k in allnames}

 allnames=[k for k in allnames if global_meta[k]]



 outauthors=[]

 outtitles=[]

 quality=[]



 for target in sorted(rows,key=lambda r:r['paper_id']):

  pid=target['paper_id']

  g=target['group']

  field=target['field']

  bin_=target['citation_bin']

  year=int(target['year'])



  real=authors(target['authors'])

  real_norm={norm(n) for n in real}

  if not real:

   raise RuntimeError('Missing gold authors '+pid)



  gold=real[0]

  goldtok=tokens(gold)

  if not goldtok:

   raise RuntimeError('Empty gold tokens '+pid)



  allowed=[k for k in allnames if k not in real_norm]

  if len(allowed)<100:

   raise RuntimeError('Not enough false authors')



  def source_for(k):

   records=[x for x in members[k] if x['paper_id']!=pid]

   if not records:

    raise RuntimeError('No external source for '+k)

   return min(

    records,

    key=lambda x:(

     0 if x['field']==field else 1,

     abs(int(x['year'])-year),

     rank(pid,k,x['paper_id'])

    )

   )



  def pretier(k):

   samefield=field in name_fields[k]

   sametok=len(global_meta[k])==len(goldtok)

   if samefield and sametok:

    return 0

   if samefield:

    return 1

   if sametok:

    return 2

   return 3



  preordered=sorted(

   allowed,

   key=lambda k:(pretier(k),rank(SEED,pid,'matched',k))

  )

  shortlisted=preordered[:min(600,len(preordered))]

  metas={}



  for k in shortlisted:

   t=global_meta[k]

   s=source_for(k)

   metas[k]=(

    pretier(k),

    abs(int(s['year'])-year),

    abs(len(t)-len(goldtok)),

    s

   )



  matched=sorted(

   shortlisted,

   key=lambda k:(metas[k][:3],rank(SEED,pid,'matched',k))

  )[:50]



  remaining=[k for k in allowed if k not in set(matched)]

  random_keys=sorted(

   remaining,

   key=lambda k:rank(SEED,pid,'random',k)

  )[:50]



  for k in random_keys:

   s=source_for(k)

   t=global_meta[k]

   metas[k]=(

    pretier(k),

    abs(int(s['year'])-year),

    abs(len(t)-len(goldtok)),

    s

   )



  if len(random_keys)!=50:

   raise RuntimeError('Too few random author controls')



  false_set=set(matched+random_keys)



  for pool,index,keys in [

   ('gold',0,[norm(gold)]),

   ('matched',1,matched),

   ('random',51,random_keys)

  ]:

   for i,k in enumerate(keys):

    s=target if pool=='gold' else metas[k][3]

    t=goldtok if pool=='gold' else global_meta[k]

    tier='' if pool=='gold' else metas[k][0]



    outauthors.append(dict(

     paper_id=pid,

     group=g,

     citation_bin=bin_,

     field=field,

     year=year,

     pool=pool,

     candidate_index=index+i,

     candidate_name=gold if pool=='gold' else names[k],

     candidate_name_normalized=k,

     first_token_id=t[0],

     n_name_tokens=len(t),

     all_token_ids=json.dumps(t),

     gold_first_token_id=goldtok[0],

     first_token_collision=int(t[0]==goldtok[0]),

     gold_n_name_tokens=len(goldtok),

     name_token_count_gap=abs(len(t)-len(goldtok)),

     match_tier=tier,

     nearest_same_field_year_gap=(

      0 if pool=='gold' else abs(int(s['year'])-year)

     ),

     source_paper_id=s['paper_id'],

     source_field=s['field'],

     source_year=s['year'],

     source_is_pilot='',

     source_paper_count=source_count[k]

    ))



  true_title_tokens=len(

   tok.encode(target['title'],add_special_tokens=False)

  )



  title_options=[]

  for s in full:

   if s['paper_id']==pid or norm(s['title'])==norm(target['title']):

    continue



   source_auth={norm(x) for x in authors(s['authors'])}

   if source_auth & real_norm:

    continue



   st=title_tok[s['paper_id']]



   if s['field']==field and s['citation_bin']==bin_:

    tier=0

   elif s['field']==field:

    tier=1

   else:

    tier=2



   title_options.append((

    tier,

    abs(int(s['year'])-year),

    abs(st-true_title_tokens),

    rank(SEED,pid,'title',s['paper_id']),

    s,st,source_auth

   ))



  title_options.sort(key=lambda x:x[:4])

  if len(title_options)<20:

   raise RuntimeError('Too few wrong titles '+pid)



  for i,(tier,yg,tg,_,s,st,sa) in enumerate(

   title_options[:20],start=1

  ):

   outtitles.append(dict(

    paper_id=pid,

    group=g,

    citation_bin=bin_,

    field=field,

    year=year,

    true_title=target['title'],

    true_title_tokens=true_title_tokens,

    shuffle_index=i,

    shuffled_title=s['title'],

    source_paper_id=s['paper_id'],

    source_field=s['field'],

    source_citation_bin=s['citation_bin'],

    source_year=s['year'],

    shuffled_title_tokens=st,

    match_tier=tier,

    year_gap=yg,

    title_token_gap=tg,

    source_author_in_false_pool=int(bool(sa&false_set)),

    source_author_overlap_gold_paper=0,

    shuffle_prompt_year=year

   ))



  quality.append(dict(

   paper_id=pid,

   group=g,

   year=year,

   citation_bin=bin_,

   matched_tier0=sum(metas[k][0]==0 for k in matched),

   candidate_first_token_collisions=sum(

    global_meta[k][0]==goldtok[0] for k in matched+random_keys

   ),

   title_tier0=sum(x[0]==0 for x in title_options[:20]),

   title_same_field=sum(

    x[4]['field']==field for x in title_options[:20]

   )

  ))



 cpath=root/'controls/stage8_author_candidates.csv'

 tpath=root/'controls/stage8_shuffled_titles.csv'

 qpath=root/'controls/stage8_control_quality.csv'

 mpath=root/'config/stage8B_manifest.json'



 if any(p.exists() for p in (cpath,tpath,qpath,mpath)):

  raise RuntimeError(

   'Stage 8B frozen output already exists; use audit, no overwrite'

  )



 writecsv(cpath,outauthors,CHEAD)

 writecsv(tpath,outtitles,THEAD)

 writecsv(qpath,quality,list(quality[0]))



 m={

  'version':'stage8B_v1',

  'seed':SEED,

  'stage8A_manifest_sha256':digest(manifest),

  'full_manifest_sha256':digest(fullfile),

  'tokenizer':a.tokenizer,

  'revision':a.revision,

  'n_papers':200,

  'n_authors':len(outauthors),

  'n_titles':len(outtitles),

  'files':{

   str(p.relative_to(root)):digest(p)

   for p in (cpath,tpath,qpath)

  },

  'protocol':(

   '50 matched +50 random false authors; '

   '20 closest field/bin/year/title-length wrong titles; '

   'no true coauthors; no lens outcomes'

  ),

  'analysis_status':'CONTROLS_ONLY_NOT_GPU_SCORED'

 }



 jsonwrite(mpath,m)

 print(

  'STAGE 8B FREEZE',

  len(outauthors),'candidate records',

  len(outtitles),'wrong-title records',

  'SHA',digest(mpath)

 )

 audit(a)



def audit(a):

 root=a.root

 mfile=root/'config/stage8B_manifest.json'

 if not mfile.is_file():

  raise RuntimeError('Stage 8B not frozen yet')



 m=json.loads(mfile.read_text())



 if digest(root/'config/manifest.json')!=m['stage8A_manifest_sha256']:

  raise RuntimeError('Stage 8A manifest changed')



 for file,h in m['files'].items():

  if digest(root/file)!=h:

   raise RuntimeError('Stage 8B file changed: '+file)



 c=readcsv(root/'controls/stage8_author_candidates.csv')

 t=readcsv(root/'controls/stage8_shuffled_titles.csv')



 if len(c)!=20200 or len(t)!=4000:

  raise RuntimeError(

   'Expected 20200 candidates (200 gold + 20000 false) '

   'and 4000 shuffled titles'

  )



 cc=collections.defaultdict(list)

 tt=collections.defaultdict(list)



 for r in c:

  cc[r['paper_id']].append(r)

 for r in t:

  tt[r['paper_id']].append(r)



 if set(cc)!=set(tt) or len(cc)!=200:

  raise RuntimeError('Paper coverage mismatch')



 for pid,rr in cc.items():

  if collections.Counter(r['pool'] for r in rr)!={

   'gold':1,'matched':50,'random':50

  }:

   raise RuntimeError('Candidate pool bad: '+pid)



  if len({r['candidate_name_normalized'] for r in rr})!=101:

   raise RuntimeError('Duplicate candidate author: '+pid)



  if sorted(int(r['candidate_index']) for r in rr)!=list(range(101)):

   raise RuntimeError('Candidate index mismatch: '+pid)



  if any(

   r['source_paper_id']==pid

   for r in rr if r['pool']!='gold'

  ):

   raise RuntimeError('Own-paper false author: '+pid)



  titles=tt[pid]

  if len(titles)!=20 or {

   int(r['shuffle_index']) for r in titles

  }!=set(range(1,21)):

   raise RuntimeError('Title index mismatch: '+pid)



  if len({r['source_paper_id'] for r in titles})!=20:

   raise RuntimeError('Duplicate title sources: '+pid)



  if any(

   r['source_paper_id']==pid or

   r['source_author_overlap_gold_paper']!='0'

   for r in titles

  ):

   raise RuntimeError('Invalid title source: '+pid)



 print(

  'STAGE 8B VERIFIED 200 papers / '

  '20,200 candidate records / 4,000 title controls; '

  'manifest_sha256',digest(mfile)

 )



def main():

 p=argparse.ArgumentParser()

 p.add_argument('command',choices=['freeze','audit'])



 p.add_argument(

  '--root',

  type=Path,

  default=Path('/scratch')/os.environ.get('USER','')/'jlens/351_stage8'

 )

 p.add_argument(

  '--full',

  type=Path,

  default=Path('/scratch')/os.environ.get('USER','')/

          'jlens/351_stage5_crossed_v2/cohort/full_6841_manifest.csv'

 )

 p.add_argument('--tokenizer',default='Qwen/Qwen3-32B')

 p.add_argument(

  '--revision',

  default='9216db5781bf21249d130ec9da846c4624c16137'

 )



 a=p.parse_args()

 if a.command=='freeze':

  controls(a)

 else:

  audit(a)



if __name__=='__main__':

 main()

