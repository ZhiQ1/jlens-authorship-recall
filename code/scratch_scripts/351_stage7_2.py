#!/usr/bin/env python3
"""Stage 7.2 CPU-only, immutable Gold + 100 false authors candidate construction.
Never loads a language model, only the tokenizer. Outputs a frozen candidate set.
"""
import argparse,csv,hashlib,json,os,random,re,sys,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

LAYERS=[16,24,32,40,48,56,62]
GROUPS={'A':20,'B':20,'C':7,'D':3}

def norm(x):
    return ' '.join(unicodedata.normalize('NFKC',str(x)).casefold().split())
def sha(b):return hashlib.sha256(b).hexdigest()
def stable_int(*xs):return int(sha('|'.join(map(str,xs)).encode())[:16],16)
def readcsv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(p,rows,fields):
    with open(p,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
def load_tok(arg):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(arg,trust_remote_code=False)
def author_tokens(tok,name):
    out=tok.encode(' '+name,add_special_tokens=False)
    if not out:raise ValueError('No tokens for '+repr(name))
    return out

def main():
    ap=argparse.ArgumentParser(description='Freeze Stage 7.2 first-token 50 random + 50 matched false authors (CPU).')
    ap.add_argument('--stage5-root',default=None)
    ap.add_argument('--root',default=None)
    ap.add_argument('--tokenizer',default='Qwen/Qwen3-32B')
    ap.add_argument('--seed',type=int,default=35172)
    a=ap.parse_args()
    home=Path('/scratch')/os.environ.get('USER',os.environ.get('LOGNAME',''))/'jlens'
    s5=Path(a.stage5_root) if a.stage5_root else home/'351_stage5_crossed_v2'
    out=Path(a.root) if a.root else home/'351_stage7_2'
    cohort_path=s5/'cohort/pilot50_v1.csv';pool_path=s5/'cohort/full_6841_manifest.csv'
    cohort=readcsv(cohort_path);all_papers=readcsv(pool_path)
    if len(cohort)!=50 or Counter(p['group'] for p in cohort)!=Counter(GROUPS):raise RuntimeError('Frozen 50 A/B/C/D mismatch')
    if len({p['paper_id'] for p in cohort})!=50 or len(all_papers)!=6841:raise RuntimeError('Cohort or full pool counts changed')
    pilot_ids={p['paper_id'] for p in cohort}
    pilot_by_id={p['paper_id']:p for p in cohort}
    for p in cohort:
        if len([x for x in p['authors'].split(';') if x.strip()])!=int(p['n_authors']):raise RuntimeError('Authors count '+p['paper_id'])
    # Immutable existing outputs: never overwrite candidate assignment, even if seed changes.
    marker=out/'config/manifest.json'
    if marker.exists():
        manifest=json.loads(marker.read_text(encoding='utf-8'))
        if manifest['input_sha256']!={'pilot50':sha(cohort_path.read_bytes()),'full6841':sha(pool_path.read_bytes())}:
            raise RuntimeError('Existing frozen outputs were built using a different cohort/pool; do not overwrite.')
        if manifest['seed']!=a.seed or manifest['tokenizer']!=a.tokenizer:
            raise RuntimeError('Existing frozen outputs do not match seed/tokenizer; do not overwrite.')
        for rel,digest in manifest['output_sha256'].items():
            if not (out/rel).exists() or sha((out/rel).read_bytes())!=digest:raise RuntimeError('Frozen output missing or mutated: '+rel)
        print('ALREADY FROZEN; verified all SHA256 hashes:',out);return
    if out.exists() and any(out.rglob('*')):raise RuntimeError('Stage7.2 root is not empty and not frozen; choose a new --root')
    print('Loading tokenizer (CPU only):',a.tokenizer,flush=True)
    tok=load_tok(a.tokenizer)
    # Deterministic canonical author dictionary, indexed from frozen 6841 only.
    people={};paper_authors={};sources=defaultdict(list)
    for p in all_papers:
        author_set=set()
        for raw in p['authors'].split(';'):
            name=raw.strip();k=norm(name)
            if not k:continue
            author_set.add(k)
            if k not in people:people[k]=name
            sources[k].append((p['paper_id'],p['field'],int(p['year']) if p['year'] else -9999))
        paper_authors[p['paper_id']]=author_set
    for p in cohort:
        if p['paper_id'] not in paper_authors:raise RuntimeError('Pilot paper absent from 6841: '+p['paper_id'])
        if norm(p['first_author']) not in paper_authors[p['paper_id']]:raise RuntimeError('Gold first author not in source: '+p['paper_id'])
    print('Unique author names in source:',len(people),flush=True)
    token_cache={k:author_tokens(tok,v) for k,v in people.items()}
    candidate_rows=[];summary=[];tiers=Counter();collisions=Counter();random_collisions=Counter()
    for p in sorted(cohort,key=lambda v:int(v['sampling_rank'])):
        pid=p['paper_id'];gold=p['first_author'];gk=norm(gold);gt=token_cache[gk]
        forbidden=paper_authors[pid]
        candidates=[k for k in people if k not in forbidden]
        if len(candidates)<100:raise RuntimeError('Not enough negative author names')
        target_year=int(p['year']);field=p['field']
        # Source selection excludes target paper and avoids choosing pilot papers where feasible.
        def source_for(k):
            src=sorted(sources[k],key=lambda s:(s[1]!=field,abs(s[2]-target_year),s[0] in pilot_ids,s[0]))
            return src[0]
        # precompute best same-field year distance. If author appears in many papers,
        # matching may use a better source than the source used to report provenance.
        def samefieldyear(k):
            years=[abs(y-target_year) for _,f,y in sources[k] if f==field and y>-9999]
            return min(years) if years else None
        # Matched tiers are explicit and reportable. Name token count exact for tiers 0-3.
        def tier(k):
            ny=samefieldyear(k);exact=len(token_cache[k])==len(gt)
            if exact and ny is not None and ny<=2:return 0
            if exact and ny is not None and ny<=5:return 1
            if exact and ny is not None:return 2
            if exact:return 3
            if ny is not None and ny<=5:return 4
            if ny is not None:return 5
            return 6
        # Prefer exact field + token len + near year; do not artificially claim
        # that fallback tiers meet all matching criteria.
        eligible=sorted(candidates,key=lambda k:(tier(k),stable_int(a.seed,pid,'matched',k)))
        matched=eligible[:50];chosen=set(matched)
        # Random sampled uniformly over distinct authors without replacement.
        available=sorted(set(candidates)-chosen)
        rng=random.Random(stable_int(a.seed,pid,'random'))
        random_keys=rng.sample(available,50)
        cr=Counter();matched_tier=Counter();source_pilots=0
        def add(key,kind,index):
            nonlocal source_pilots
            name=people[key];t=token_cache[key];first=t[0];src=source_for(key)
            if src[0] in pilot_ids:source_pilots+=1
            same=(first==gt[0]);cr[kind]+=int(same)
            if kind=='matched':matched_tier[tier(key)]+=1;tiers[tier(key)]+=1
            candidate_rows.append({'paper_id':pid,'group':p['group'],'citation_bin':p['citation_bin'],
                'field':field,'year':p['year'],'pool':kind,'candidate_index':index,
                'candidate_name':name,'candidate_name_normalized':key,
                'first_token_id':first,'n_name_tokens':len(t),'all_token_ids':json.dumps(t),
                'gold_first_token_id':gt[0],'first_token_collision':int(same),
                'gold_n_name_tokens':len(gt),'name_token_count_gap':len(t)-len(gt),
                'match_tier':tier(key) if kind=='matched' else '',
                'nearest_same_field_year_gap':samefieldyear(key) if samefieldyear(key) is not None else '',
                'source_paper_id':src[0],'source_field':src[1],'source_year':src[2],
                'source_is_pilot':int(src[0] in pilot_ids),'source_paper_count':len({s[0] for s in sources[key]})})
        # Record gold separately, candidate_index 0.
        add(gk,'gold',0)
        for i,k in enumerate(matched,1):add(k,'matched',i)
        for i,k in enumerate(random_keys,1):add(k,'random',i)
        collisions[p['group']]+=cr['matched']+cr['random'];random_collisions[p['group']]+=cr['random']
        summary.append({'paper_id':pid,'group':p['group'],'citation_bin':p['citation_bin'],
            'field':field,'gold_author':gold,'gold_first_token_id':gt[0],
            'n_gold_tokens':len(gt),'n_matched':50,'n_random':50,
            'matched_first_token_collisions':cr['matched'],'random_first_token_collisions':cr['random'],
            'matched_tier_0':matched_tier[0],'matched_tier_1':matched_tier[1],
            'matched_tier_2':matched_tier[2],'matched_tier_3':matched_tier[3],
            'matched_tier_4':matched_tier[4],'matched_tier_5':matched_tier[5],
            'matched_tier_6':matched_tier[6],'source_pilot_count':source_pilots})
    # Important interpretation: a name-sharing first token is a TIE, not a loss.
    # Gold candidate's reference to itself is not part of 100 negatives.
    if len(candidate_rows)!=5050:raise RuntimeError('Expected 5050 candidate rows')
    for p in cohort:
        rr=[r for r in candidate_rows if r['paper_id']==p['paper_id']]
        if len(rr)!=101 or len({r['candidate_name_normalized'] for r in rr})!=101:raise RuntimeError('Bad uniqueness: '+p['paper_id'])
    for d in ['config','candidates','summary','reports']: (out/d).mkdir(parents=True,exist_ok=True)
    cfields=list(candidate_rows[0]);sfields=list(summary[0])
    writecsv(out/'candidates/pilot50_author_candidates.csv',candidate_rows,cfields)
    with (out/'candidates/pilot50_author_candidates.jsonl').open('w',encoding='utf-8') as f:
        for p in cohort:
            rr=[r for r in candidate_rows if r['paper_id']==p['paper_id']]
            f.write(json.dumps({'paper_id':p['paper_id'],'group':p['group'],'gold':rr[0],
                'matched':[x for x in rr if x['pool']=='matched'],
                'random':[x for x in rr if x['pool']=='random']},ensure_ascii=False)+'\n')
    writecsv(out/'summary/pilot50_candidate_quality.csv',summary,sfields)
    tot=Counter(r['pool'] for r in candidate_rows)
    quality={'status':'FROZEN','paper_count':50,'group_counts':dict(Counter(p['group'] for p in cohort)),
        'candidate_rows':len(candidate_rows),'pool_counts':dict(tot),'matching_tiers':dict(sorted(tiers.items())),
        'first_token_collision_count_by_group':dict(collisions),
        'collision_definition':'gold first token id == incorrect author first token id; count as tie (0.5), not forced replacement',
        'pool_sampling':'matched: lexicographic tier then seeded hash; random: seeded uniform sample without replacement after matched names are removed',
        'gold_definition':'First listed real author of each paper',
        'limitations':['String-normalized membership check; author entity aliases are not independently validated',
                       'Same first-token for different names is possible; first-token scores cannot distinguish such candidates',
                       'Matching uses tokenizer token count and field/year proxy, not global first-token base frequency',
                       'Gold Win Rate against 100 named candidates is not full-name identity classification',
                       'Pilot has exploratory sample size; no causal attribution']}
    dump(out/'summary/quality.json',quality)
    report=f'''# Stage 7.2 — Candidate Construction (CPU; no GPU)\n\n50 frozen papers, 20/20/7/3 A/B/C/D. Gold is first-listed author. Every paper has 50 unique matched and 50 unique random incorrect **real author names** drawn from frozen 6,841-paper source.\n\n## Matching tier interpretation\n\n- 0: same field, same Qwen name-token count, year difference <=2\n- 1: same field, same token count, year difference <=5\n- 2: same field, same token count, any year\n- 3: same token count, any field/year\n- 4: same field, any token count, year difference <=5\n- 5: same field, any token count/year\n- 6: remaining real authors\n\nTier counts across all 2,500 matched negatives: {dict(sorted(tiers.items()))}.\n\n## First-token collision\n\nBy group (matched + random): {dict(collisions)}. Retain ties; do not reselect candidates based on score. In Gold Win Rate, tied first tokens contribute 0.5, and the same-token collision is reported separately.\n\n## Boundaries\n\nThe same-field check is inferred from source papers, not author identity resolution. Checking author-name strings is not an external authorship registry. Candidate matching is based on field, year, Qwen token count, but cannot guarantee equal pretrained name priors. Stage 7.2 only freezes candidates; no J-Lens measurement has been run.\n'''
    (out/'reports/candidate_audit.md').write_text(report,encoding='utf-8')
    rels=['candidates/pilot50_author_candidates.csv','candidates/pilot50_author_candidates.jsonl','summary/pilot50_candidate_quality.csv','summary/quality.json','reports/candidate_audit.md']
    manifest={'protocol':'stage7_2_candidate_freeze_v1','seed':a.seed,'tokenizer':a.tokenizer,
        'input_sha256':{'pilot50':sha(cohort_path.read_bytes()),'full6841':sha(pool_path.read_bytes())},
        'output_sha256':{x:sha((out/x).read_bytes()) for x in rels},
        'scoring_plan':{'layers':LAYERS,'readouts':['jlens','vanilla','final_reference'],
                        'gold_win_rate':'mean over 100 false candidates: score_gold>score_false -> 1; equal -> 0.5; else -> 0',
                        'rank_not_identity':'first-token scores only'}}
    dump(marker,manifest)
    print('STAGE 7.2 FREEZE SUCCESS',out,'papers=50 candidate_rows=5050')
    print('Matched tiers:',dict(sorted(tiers.items())))
    print('Token collisions by group:',dict(collisions))
    print('Manifest SHA256:',sha(marker.read_bytes()))
    print('No GPU used; candidate scoring has NOT run.')
if __name__=='__main__':main()
