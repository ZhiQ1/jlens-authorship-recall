#!/usr/bin/env python3
"""Stage 7.3A: CPU-only immutable 20-title-per-paper matched title shuffle freeze.
No J-Lens scores are used to select titles. Does not touch prior stage outputs.
"""
import argparse,csv,hashlib,json,os,random,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

K=20
GROUPS={'A':20,'B':20,'C':7,'D':3}

def normal(s):return ' '.join(unicodedata.normalize('NFKC',str(s)).casefold().split())
def names(s):return set(normal(x) for x in str(s).split(';') if x.strip())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def readcsv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(path,rows,fields):
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,data):p.write_text(json.dumps(data,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def seed_for(*x):return int(hashlib.sha256('|'.join(map(str,x)).encode()).hexdigest()[:16],16)
def metadata(p,tok):
    title=p['title'];ids=tok.encode(title,add_special_tokens=False)
    return {'id':p['paper_id'],'title':title,'title_norm':normal(title),'year':int(p['year']),
            'field':p['field'],'bin':p['citation_bin'],'authors':names(p['authors']), 'title_tokens':len(ids)}
def tier(p,q):
    field=p['field']==q['field'];bn=p['bin']==q['bin'];yd=abs(p['year']-q['year']);ld=abs(p['title_tokens']-q['title_tokens'])
    # Strict to broad; preserves diagnostics for every relaxed property.
    if field and bn and yd<=2 and ld<=5:return 0
    if field and bn and yd<=5 and ld<=10:return 1
    if field and yd<=5 and ld<=10:return 2
    if field and yd<=10 and ld<=20:return 3
    if field:return 4
    if bn and yd<=5:return 5
    return 6

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('command',nargs='?',choices=['freeze','audit'],default='freeze')
    ap.add_argument('--stage5-root');ap.add_argument('--stage72-root');ap.add_argument('--root')
    ap.add_argument('--seed',type=int,default=35173);ap.add_argument('--k',type=int,default=K)
    args=ap.parse_args()
    if args.k!=20:raise ValueError('Protocol fixed to 20 title shuffles per paper')
    base=Path('/scratch')/os.environ.get('USER','')/'jlens'
    s5=Path(args.stage5_root or base/'351_stage5_crossed_v2')
    s72=Path(args.stage72_root or base/'351_stage7_2')
    out=Path(args.root or base/'351_stage7_3')
    pilotfile=s5/'cohort/pilot50_v1.csv';poolfile=s5/'cohort/full_6841_manifest.csv'
    candidatefile=s72/'candidates/pilot50_author_candidates.csv';candmanifest=s72/'config/manifest.json'
    inputs={'pilot50':pilotfile,'full6841':poolfile,'frozen_candidates':candidatefile,'candidate_manifest':candmanifest}
    for key,p in inputs.items():
        if not p.is_file():raise FileNotFoundError(f'Missing {key}: {p}')
    prev=json.loads(candmanifest.read_text())
    if sha(candidatefile)!=prev['output_sha256']['candidates/pilot50_author_candidates.csv']:
        raise ValueError('Stage7.2 Candidate CSV hash mismatch')
    for key,v in [('pilot50','pilot50'),('full6841','full6841')]:
        if sha(inputs[key])!=prev['input_sha256'][v]:raise ValueError('Stage5 input hash mismatch vs frozen candidate manifest: '+key)
    frozen_path=out/'config/manifest.json'
    if frozen_path.exists():
        manifest=json.loads(frozen_path.read_text())
        for key,p in inputs.items():
            if sha(p)!=manifest['input_sha256'][key]:raise ValueError('Input changed: '+key)
        for rel,h in manifest['output_sha256'].items():
            if sha(out/rel)!=h:raise ValueError('Frozen output changed: '+rel)
        if manifest['seed']!=args.seed or manifest['k']!=args.k:raise ValueError('Freeze parameters differ')
        rows=readcsv(out/'titles/pilot50_shuffled_titles.csv')
        print('ALREADY FROZEN; verified all SHA256 hashes; papers=50 shuffles=',len(rows),'manifest=',sha(frozen_path))
        return
    if args.command=='audit':raise FileNotFoundError('No frozen Stage7.3 manifest; run freeze first')
    if out.exists() and any(out.iterdir()):raise FileExistsError('Output path is nonempty without manifest; refuse overwrite: '+str(out))
    pilot=readcsv(pilotfile);pool=readcsv(poolfile);candidates=readcsv(candidatefile)
    if len(pilot)!=50 or Counter(r['group'] for r in pilot)!=GROUPS:raise ValueError('Frozen pilot50 invalid')
    if len(candidates)!=5050:raise ValueError('Stage7.2 candidate count invalid')
    gold_by_paper=defaultdict(set);false_by_paper=defaultdict(set)
    for c in candidates:
        (gold_by_paper if c['pool']=='gold' else false_by_paper)[c['paper_id']].add(normal(c['candidate_name']))
    print('Loading Qwen tokenizer on CPU for title length matching...',flush=True)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained('Qwen/Qwen3-32B',trust_remote_code=False)
    allpapers=[metadata(x,tok) for x in pool];byid={q['id']:q for q in allpapers}
    chosen=[];summaries=[];bad=[]
    for raw in pilot:
        p=metadata(raw,tok);pname=p['authors'];gold=gold_by_paper[p['id']]
        if p['id'] not in byid or gold!=set([normal(raw['first_author'])]):raise ValueError('Pilot/gold mismatch '+p['id'])
        available=[q for q in allpapers if q['id']!=p['id'] and q['title_norm']!=p['title_norm'] and q['authors'].isdisjoint(pname)]
        # Unique source TITLE globally within each target (not necessarily across targets).
        bytitle={}
        for q in available:
            k=q['title_norm']; z=(tier(p,q),abs(p['year']-q['year']),abs(p['title_tokens']-q['title_tokens']),seed_for(args.seed,p['id'],q['id']))
            if k not in bytitle or z<bytitle[k][0]:bytitle[k]=(z,q)
        ordered=sorted(bytitle.values(),key=lambda a:a[0]);selected=ordered[:args.k]
        if len(selected)!=args.k:bad.append((p['id'],len(selected)));continue
        for ix,(ordering,q) in enumerate(selected,1):
            t=ordering[0]
            chosen.append({'paper_id':p['id'],'group':raw['group'],'citation_bin':p['bin'],'field':p['field'],
                'year':p['year'],'true_title':p['title'],'true_title_tokens':p['title_tokens'],
                'shuffle_index':ix,'shuffled_title':q['title'],'source_paper_id':q['id'],
                'source_field':q['field'],'source_citation_bin':q['bin'],'source_year':q['year'],
                'shuffled_title_tokens':q['title_tokens'],'match_tier':t,'year_gap':abs(p['year']-q['year']),
                'title_token_gap':abs(p['title_tokens']-q['title_tokens']),
                'source_author_in_false_pool':int(bool(q['authors']&false_by_paper[p['id']])),
                'source_author_overlap_gold_paper':0,
                'shuffle_prompt_year':p['year']})
        summaries.append({'paper_id':p['id'],'group':raw['group'],'citation_bin':p['bin'],
            'n_shuffles':len(selected),'tier0':sum(z['match_tier']==0 for z in chosen[-20:]),
            'max_tier':max(z['match_tier'] for z in chosen[-20:]),
            'mean_year_gap':round(sum(z['year_gap'] for z in chosen[-20:])/20,3),
            'mean_title_token_gap':round(sum(z['title_token_gap'] for z in chosen[-20:])/20,3),
            'source_author_in_false_pool':sum(z['source_author_in_false_pool'] for z in chosen[-20:])})
    if bad:raise ValueError('Insufficient valid source titles: '+repr(bad))
    if len(chosen)!=1000:raise ValueError('Wrong title count')
    (out/'titles').mkdir(parents=True);(out/'config').mkdir();(out/'summary').mkdir();(out/'reports').mkdir()
    mainfile=out/'titles/pilot50_shuffled_titles.csv';quality=out/'summary/title_matching_quality.csv'
    writecsv(mainfile,chosen,list(chosen[0]));writecsv(quality,summaries,list(summaries[0]))
    counts=Counter(r['match_tier'] for r in chosen)
    summary={'papers':50,'shuffles_per_paper':20,'total_shuffles':len(chosen),'tier_counts':dict(sorted(counts.items())),
        'same_field_fraction':sum(r['field']==r['source_field'] for r in chosen)/len(chosen),
        'same_bin_fraction':sum(r['citation_bin']==r['source_citation_bin'] for r in chosen)/len(chosen),
        'source_author_in_false_pool':sum(r['source_author_in_false_pool'] for r in chosen),
        'mean_year_gap':sum(r['year_gap'] for r in chosen)/len(chosen),
        'mean_title_token_gap':sum(r['title_token_gap'] for r in chosen)/len(chosen),
        'notes':['All 20 shuffles are selected by metadata only; scored outputs were not read',
         'Same original target year retained in all shuffled prompts; source title year may differ',
         'Author overlap is checked against target paper authors by normalized name strings, not external registry',
         'Matched title source may have a real author included in frozen false candidates; flagged, not hidden',
         'Repeated source title use across distinct target papers is allowed; dependent null contexts require care']}
    summaryfile=out/'summary/quality.json';dump(summaryfile,summary)
    report=out/'reports/freeze_audit.md'
    report.write_text('# Stage 7.3A frozen title controls\n\n'+f'50 targets × 20 shuffles = {len(chosen)} title contexts.\n\n'+f'Tier counts: {dict(sorted(counts.items()))}\n\n'+f'Cross-pool source-author overlaps: {summary["source_author_in_false_pool"]}.\n\n'+'\n'.join('- '+x for x in summary['notes'])+'\n',encoding='utf-8')
    outputs={str(p.relative_to(out)):sha(p) for p in [mainfile,quality,summaryfile,report]}
    manifest={'protocol':'stage7_3a_title_freeze_v1','k':args.k,'seed':args.seed,'tokenizer':'Qwen/Qwen3-32B',
        'input_sha256':{k:sha(p) for k,p in inputs.items()},'output_sha256':outputs,
        'fixed_candidate_manifest_sha256':sha(candmanifest),
        'scoring_rule':'Original target year, identical prompt/candidates/readouts; only title text replaced',
        'selection':'Sort by match tier, year gap, title token gap, stable seeded hash. No score-based selection.'}
    dump(frozen_path,manifest)
    print('STAGE 7.3A FREEZE SUCCESS',out,'papers=50 shuffles=1000')
    print('Matched tiers:',dict(sorted(counts.items())),'source_author_in_false_pool:',summary['source_author_in_false_pool'])
    print('same_field_fraction=',round(summary['same_field_fraction'],4),'same_bin_fraction=',round(summary['same_bin_fraction'],4))
    print('Manifest SHA256:',sha(frozen_path));print('No GPU used. Stage7.3B scoring NOT run.')
if __name__=='__main__':main()
