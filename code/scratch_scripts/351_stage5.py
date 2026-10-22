#!/usr/bin/env python3
"""Stage 5 title-specific first-token controlled pilot; freeze/reuse cohort and controls.
Commands: prepare, run, analyze. Single standalone file. NO full-name teacher forcing.
"""
import os,sys,csv,json,hashlib,random,collections,math,time,statistics,argparse,platform
from pathlib import Path
SEED=35150
LAYERS=[16,24,32,40,48,56,62]
MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
PROMPT='Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'
ROOT=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_stage5')
DATA=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_all/351_four_groups.csv')
LENS=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
STAGE4=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_all/351_stage4_artifacts/raw/results.jsonl')

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def csvwrite(path,rows,cols):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
def csvread(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def author_list(r):return [n.strip() for n in r.get('authors','').split(';') if n.strip()]
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def file_sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def grp(r):return r.get('group_351') or r.get('group')
def stable_order(x,seed=SEED):return sorted(x,key=lambda r:hashlib.sha256((str(seed)+r['paper_id']).encode()).hexdigest())
def first_author(r):
    names=author_list(r)
    return names[0] if names else None

def prepare(a):
    root=Path(a.root);cohort=Path(a.data); data=csvread(cohort)
    by={r['paper_id']:r for r in data}
    if len(by)!=len(data):raise ValueError('Duplicate paper IDs')
    expected={'A':4110,'B':2186,'C':511,'D':34}
    counts=collections.Counter(grp(r) for r in data)
    if counts!=expected:raise ValueError(f'Frozen 351 groups changed: {counts}, expected {expected}')
    for r in data:
        if not first_author(r):raise ValueError('Missing author '+r['paper_id'])
    stage4=[]
    if Path(a.stage4).exists():
        with open(a.stage4,encoding='utf-8') as f:
            stage4=[json.loads(line) for line in f if line.strip()]
    ids=[]
    for p in stage4:
        if p['paper_id'] not in by:raise ValueError('Stage4 ID absent in cohort')
        if p['paper_id'] in ids:raise ValueError('Duplicate Stage4 ID')
        if p['group']!=grp(by[p['paper_id']]):raise ValueError('Stage4 group mismatch')
        ids.append(p['paper_id'])
    if len(ids)!=20 or collections.Counter(grp(by[i]) for i in ids)!= {'A':8,'B':8,'C':3,'D':1}:
        raise ValueError('Expected validated Stage4 20 IDs (A8 B8 C3 D1); do not silently resample. Path: '+str(a.stage4))
    quotas={'A':20,'B':20,'C':7,'D':3}
    selected=list(ids)
    # Select new A/B jointly to favor matched citation-bin+field, without relabeling or dropping Stage4 IDs.
    new={g:stable_order([r for r in data if grp(r)==g and r['paper_id'] not in ids]) for g in quotas}
    fresh=[]
    need={g:quotas[g]-collections.Counter(grp(by[i]) for i in ids)[g] for g in quotas}
    used=set(ids)
    def getnew(g,r):
        if need[g]<=0 or r['paper_id'] in used:return False
        selected.append(r['paper_id']);used.add(r['paper_id']);need[g]-=1;return True
    # Prioritize matching the immovable Stage 4 members, not only new-to-new pairs.
    for g,other in [('A','B'),('B','A')]:
        for pid in ids:
            if grp(by[pid])!=g or need[other]<=0:continue
            r=by[pid]
            options=[q for q in new[other] if q['paper_id'] not in used and (q['citation_bin'],q['field'])==(r['citation_bin'],r['field'])]
            options.sort(key=lambda q:(abs(int(q['year'])-int(r['year']))+2*abs(int(q['n_authors'])-int(r['n_authors'])),q['paper_id']))
            if options:getnew(other,options[0])
    # Fill new A/B in exact pairs where possible, then top off quotas.
    B_bucket=collections.defaultdict(list)
    for q in new['B']:B_bucket[(q['citation_bin'],q['field'])].append(q)
    for r in new['A']:
        if need['A']<=0 or need['B']<=0:break
        options=[q for q in B_bucket[(r['citation_bin'],r['field'])] if q['paper_id'] not in used]
        options.sort(key=lambda q:(abs(int(q['year'])-int(r['year']))+2*abs(int(q['n_authors'])-int(r['n_authors'])),q['paper_id']))
        if options:getnew('A',r);getnew('B',options[0])
    for g in quotas:
        for r in new[g]:
            if need[g]==0:break
            getnew(g,r)
        if need[g]:raise ValueError('Insufficient '+g)
    assert len(selected)==50
    out=[]
    for idx,pid in enumerate(selected):
        r=by[pid]
        out.append(dict(pilot_id='pilot50_v1',sampling_seed=SEED,sampling_rank=idx,paper_id=pid,group=grp(r),
            title=r['title'],year=r['year'],authors=r['authors'],first_author=first_author(r),
            field=r['field'],citation_bin=r['citation_bin'],n_authors=r['n_authors'],stage4_existing=(pid in ids)))
    # Crossed negative control: false author AND counterfactual title MUST
    # originate from the SAME matched source paper. Keep assignment immutable.
    control=[]
    bystratum=collections.defaultdict(list)
    for r in data:bystratum[(r['field'],r['citation_bin'])].append(r)
    for x in out:
        gold_names={n.casefold() for n in author_list(x)}
        candidates=[]
        for r in bystratum[(x['field'],x['citation_bin'])]:
            if r['paper_id']==x['paper_id'] or r['title']==x['title']:continue
            fname=first_author(r)
            if not fname or fname.casefold() in gold_names:continue
            if x['first_author'].casefold() in {n.casefold() for n in author_list(r)}:continue
            # Entire author teams should be disjoint to avoid mislabeled positives.
            if gold_names & {n.casefold() for n in author_list(r)}:continue
            if fname.split()[0].casefold()==x['first_author'].split()[0].casefold():continue
            candidates.append(r)
        candidates.sort(key=lambda r:(abs(int(r['year'])-int(x['year'])),
            abs(len(r['title'])-len(x['title'])),
            abs(len(first_author(r))-len(x['first_author'])),
            hashlib.sha256((str(SEED)+r['paper_id']).encode()).hexdigest()))
        if not candidates:raise ValueError('No crossed negative control for '+x['paper_id'])
        neg=candidates[0]
        control.append(dict(paper_id=x['paper_id'],group=x['group'],gold_author=x['first_author'],false_author=first_author(neg),
            false_source_paper_id=neg['paper_id'],true_title=x['title'],true_year=x['year'],
            shuffle_title=neg['title'],shuffle_year=x['year'],shuffle_title_source_paper_id=neg['paper_id'],
            matching_fields='field,citation_bin',control_seed=SEED,control_design='crossed_source_paper_v2'))
    # Maximum-cardinality bipartite matching within exact field/bin. Within that
    # maximum, minimize year/author-count distances; no replacement.
    try:import networkx as nx
    except ImportError as e:raise RuntimeError('prepare requires networkx (pip install networkx in CPU environment)') from e
    A=[x for x in out if x['group']=='A'];B=[x for x in out if x['group']=='B']
    G=nx.Graph()
    for x in A:G.add_node('A:'+x['paper_id'],bipartite=0)
    for y in B:G.add_node('B:'+y['paper_id'],bipartite=1)
    for x in A:
        for y in B:
            if (x['field'],x['citation_bin'])!=(y['field'],y['citation_bin']):continue
            cost=abs(int(x['year'])-int(y['year']))+2*abs(int(x['n_authors'])-int(y['n_authors']))
            G.add_edge('A:'+x['paper_id'],'B:'+y['paper_id'],weight=-cost)
    matching=nx.algorithms.matching.max_weight_matching(G,maxcardinality=True,weight='weight')
    matched=[]
    for a_node,b_node in matching:
        if a_node.startswith('B:'):a_node,b_node=b_node,a_node
        matched.append((a_node[2:],b_node[2:]))
    matched.sort()
    pairs=[]
    pilot_by={x['paper_id']:x for x in out}
    for aid,bid in matched:
        x=pilot_by[aid];y=pilot_by[bid]
        pairs.append(dict(pair_id=f'P{len(pairs)+1:03d}',A_id=aid,B_id=bid,field=x['field'],citation_bin=x['citation_bin'],year_gap=abs(int(x['year'])-int(y['year'])),author_count_gap=abs(int(x['n_authors'])-int(y['n_authors']))))
    manifest={'protocol':'stage5_crossed_title_author_v2','pilot_id':'pilot50_v1','seed':SEED,'layers':LAYERS,'group_counts_full':dict(counts),
      'group_counts_pilot':dict(collections.Counter(x['group'] for x in out)),'n_matched_pairs':len(pairs),
      'comparison':'A/B observational matched descriptive; C/D separately; no label changes',
      'endpoints':['first_token_gold_logit','first_token_false_logit','title_specific_margin (difference of margins)'],
      'controls':['true_title_gold','true_title_false','crossed_source_title_gold','crossed_source_title_false'],
      'limitations':['first-token may not discriminate names sharing first token','false author identity disjointness checked by name, not external authorship registry','unmatched A/B retained'],
      'parent_csv':str(cohort),'parent_csv_sha256':hashlib.sha256(cohort.read_bytes()).hexdigest(),
      'stage4_raw_sha256':hashlib.sha256(Path(a.stage4).read_bytes()).hexdigest(),
      'model':MODEL,'model_revision':REV,'lens':str(a.lens),'prompt':PROMPT,'token_protocol':'encode(prompt) + encode(ASCII_SPACE+author) first token', 'scoring_version':'crossed_source_same_candidate_logits_v2'}
    if (root/'cohort'/'pilot50_v1.json').exists() or (root/'raw'/'pilot50_results.jsonl').exists():
        raise ValueError('Existing frozen cohort or results. Do not overwrite; reuse existing manifest.')
    csvwrite(root/'cohort'/'pilot50_v1.csv',out,list(out[0]));csvwrite(root/'cohort'/'full_6841_manifest.csv', [dict(paper_id=r['paper_id'],group=grp(r),title=r['title'],year=r['year'],authors=r['authors'],field=r['field'],citation_bin=r['citation_bin'],n_authors=r['n_authors']) for r in data],['paper_id','group','title','year','authors','field','citation_bin','n_authors'])
    csvwrite(root/'controls'/'pilot50_controls.csv',control,list(control[0]));csvwrite(root/'matching'/'pilot50_ab_pairs.csv',pairs,['pair_id','A_id','B_id','field','citation_bin','year_gap','author_count_gap'])
    write_json(root/'config'/'protocol.json',manifest)
    # Commit manifest LAST, so a partial prepare cannot masquerade as frozen.
    write_json(root/'cohort'/'pilot50_v1.json',{'manifest':manifest,'paper_ids':selected,
        'cohort_sha256':sha(csvread(root/'cohort'/'pilot50_v1.csv')),
        'control_sha256':sha(csvread(root/'controls'/'pilot50_controls.csv')),
        'pairs_sha256':sha(csvread(root/'matching'/'pilot50_ab_pairs.csv')),
        'full_manifest_sha256':hashlib.sha256((root/'cohort'/'full_6841_manifest.csv').read_bytes()).hexdigest()})
    print('PREPARE SUCCESS',root,'cohort=',len(out),'Stage4 reused IDs=',len(ids),'exact A/B matched pairs=',len(pairs),'SHA',sha(out)[:16]);print('Groups:',collections.Counter(x['group'] for x in out));print('No GPU used')

def validate_plan(root):
    cohort=csvread(root/'cohort'/'pilot50_v1.csv');controls=csvread(root/'controls'/'pilot50_controls.csv')
    meta=json.loads((root/'cohort'/'pilot50_v1.json').read_text())
    if [r['paper_id'] for r in cohort]!=meta['paper_ids']:
        raise ValueError('Frozen cohort IDs or sampling order modified')
    if sha(cohort)!=meta['cohort_sha256']:raise ValueError('Frozen cohort content modified')
    if sha(controls)!=meta['control_sha256']:
        raise ValueError('Frozen controls modified')
    if sha(csvread(root/'matching'/'pilot50_ab_pairs.csv'))!=meta['pairs_sha256']:raise ValueError('Frozen match pairs modified')
    if hashlib.sha256((root/'cohort'/'full_6841_manifest.csv').read_bytes()).hexdigest()!=meta['full_manifest_sha256']:raise ValueError('Full cohort manifest modified')
    for c in controls:
        if c['false_source_paper_id']!=c['shuffle_title_source_paper_id']:raise ValueError('Crossed control source mismatch')
    if len(cohort)!=50 or len(controls)!=50:raise ValueError('Expected 50 frozen records')
    control_ids={x['paper_id'] for x in controls}
    if len(control_ids)!=50:raise ValueError('Duplicate paper ID in control mapping')
    ctrl={r['paper_id']:r for r in controls}
    if set(ctrl)!={r['paper_id'] for r in cohort}:raise ValueError('Control mapping incomplete')
    if collections.Counter(r['group'] for r in cohort)!={'A':20,'B':20,'C':7,'D':3}:raise ValueError('Group counts wrong')
    return cohort,ctrl,meta

def readout(lens,model,prompt,ids,torch):
    saved=model.encode
    base=saved(prompt,max_length=512)
    if base.ndim!=2 or base.shape[0]!=1:raise RuntimeError('model.encode unexpected output shape')
    if len(ids)>512:raise RuntimeError('Context too long')
    fixed=torch.tensor([ids],dtype=base.dtype,device=base.device)
    def fixed_enc(_,max_length=512):
        if len(ids)>max_length:raise RuntimeError('Context > lens max_length')
        return fixed
    try:
        model.encode=fixed_enc
        with torch.inference_mode():
            J,actual,i1=lens.apply(model,prompt,layers=LAYERS,positions=[-1],max_seq_len=512,use_jacobian=True)
            V,actual2,i2=lens.apply(model,prompt,layers=LAYERS,positions=[-1],max_seq_len=512,use_jacobian=False)
    finally:model.encode=saved
    if not torch.equal(i1.cpu(),fixed.cpu()) or not torch.equal(i2.cpu(),fixed.cpu()):raise RuntimeError('Wrong forced token IDs')
    if (actual-actual2).abs().max().item()>.1:raise RuntimeError('Final mismatch')
    return {**{f'jlens_L{l}':J[l][-1].cpu().float() for l in LAYERS},**{f'vanilla_L{l}':V[l][-1].cpu().float() for l in LAYERS},'final_L63':actual[-1].cpu().float()}

def run(a):
    root=Path(a.root);cohort,controls,meta=validate_plan(root)
    raw=root/'raw'/'pilot50_results.jsonl';raw.parent.mkdir(parents=True,exist_ok=True)
    protocol_hash=sha(meta['manifest'])
    lens_path=Path(a.lens)
    if not lens_path.exists():raise FileNotFoundError(f'Public lens missing: {lens_path}')
    lens_hash=file_sha256(lens_path)
    runtime_hash=sha({'protocol_hash':protocol_hash,'lens_sha256':lens_hash,'model_revision':REV,'layers':LAYERS})
    runtime_file=root/'config'/'runtime.json'
    if runtime_file.exists():
        previous=json.loads(runtime_file.read_text())
        if previous['runtime_hash']!=runtime_hash:raise RuntimeError('Model/lens/protocol changed; resume prohibited')
    else:write_json(runtime_file,{'runtime_hash':runtime_hash,'lens_sha256':lens_hash,'model_revision':REV,'layers':LAYERS})
    done={}

    if raw.exists():
        for line in raw.read_text().splitlines():
            if not line.strip():continue
            row=json.loads(line)
            if row['protocol_sha']!=protocol_hash or row.get('runtime_hash')!=runtime_hash:raise ValueError('Existing results use different protocol or lens')
            if row['paper_id'] in done:raise ValueError('Duplicate existing result')
            done[row['paper_id']]=row
    todo=[r for r in cohort if r['paper_id'] not in done]
    if a.max_papers is not None:todo=todo[:a.max_papers]
    print(f'STAGE 5: {len(done)}/50 already complete, {len(todo)} queued',flush=True)
    if not todo:return
    import torch,transformers,jlens
    from transformers import AutoTokenizer,AutoModelForCausalLM
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    device_map={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
    device_map.update({f'model.layers.{i}':(0 if i<a.gpu_layers else 'cpu') for i in range(64)})
    hf=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=device_map,low_cpu_mem_usage=True).eval()
    lens=jlens.JacobianLens.load(str(a.lens));model=jlens.from_hf(hf,tokenizer)
    job_start=time.monotonic();completed_times=[]
    for r in todo:
        if a.max_seconds is not None and (time.monotonic()-job_start)+max([a.paper_reserve_seconds]+completed_times)>a.max_seconds:
            print('TIME BUDGET: stopping safely after saved paper; resume in next allocation',flush=True);break
        t=time.monotonic();c=controls[r['paper_id']]
        gold=tokenizer.encode(' '+c['gold_author'],add_special_tokens=False);false=tokenizer.encode(' '+c['false_author'],add_special_tokens=False)
        if not gold or not false:raise ValueError('Empty candidate tokens')
        same=gold[0]==false[0]
        # This is a methodological diagnostic: zero difference when two identities share first token.
        results={}
        for typ,title in [('true',c['true_title']),('shuffle',c['shuffle_title'])]:
            prompt=PROMPT.format(title=title,year=c['true_year'])
            base_ids=model.encode(prompt,max_length=512).reshape(-1).tolist()
            if len(base_ids)>=512:raise RuntimeError('Prompt too long')
            scores=readout(lens,model,prompt,base_ids,torch)
            results[typ]={}
            for mode,vec in scores.items():
                gl=float(vec[gold[0]]);fl=float(vec[false[0]])
                gr=int((vec>vec[gold[0]]).sum())+1
                fr=int((vec>vec[false[0]]).sum())+1
                results[typ][mode]={'gold_logit':gl,'false_logit':fl,'margin':gl-fl,'gold_rr':1/gr,'false_rr':1/fr,'gold_rank':gr,'false_rank':fr}
        contrast={k:{'title_specific_advantage':results['true'][k]['margin']-results['shuffle'][k]['margin'],
            'true_margin':results['true'][k]['margin'],'shuffle_margin':results['shuffle'][k]['margin']} for k in results['true']}
        out={'paper_id':r['paper_id'],'group':r['group'],'pilot_id':'pilot50_v1','protocol_sha':protocol_hash,'runtime_hash':runtime_hash,
            'gold_author':c['gold_author'],'false_author':c['false_author'],'gold_first_token_id':gold[0],
            'false_first_token_id':false[0],'same_first_token':same,
            'true_title':c['true_title'],'shuffled_title':c['shuffle_title'],
            'crossed_control':True,'false_source_paper_id':c['false_source_paper_id'],'shuffle_title_source_paper_id':c['shuffle_title_source_paper_id'],
            'results':results,'contrast':contrast,'seconds':time.monotonic()-t,'gpu_peak_gib':torch.cuda.max_memory_allocated()/2**30}
        with raw.open('a',encoding='utf-8') as f:f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        done[r['paper_id']]=out;completed_times.append(out['seconds'])
        print(f'{len(done)}/50 {r["group"]} {r["paper_id"][:12]} title controls complete t={out["seconds"]:.1f}s same_first_token={same}',flush=True)
    print('Saved:',raw,flush=True)

def ci(v,seed=SEED):
    if len(v)<2:return (None,None)
    rng=random.Random(seed);s=sorted(statistics.mean(rng.choices(v,k=len(v))) for _ in range(2000))
    return s[49],s[1949]
def analyze(a):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(a.root);cohort,ctrl,meta=validate_plan(root)
    p=root/'raw'/'pilot50_results.jsonl'
    if not p.exists():raise ValueError('No raw results yet')
    rows=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    ids=set(r['paper_id'] for r in cohort);unique={}
    for r in rows:
        if r['paper_id'] not in ids or r['paper_id'] in unique:raise ValueError('Unknown/duplicate paper')
        unique[r['paper_id']]=r
    if any(r['protocol_sha']!=sha(meta['manifest']) for r in rows):raise ValueError('Protocol changed')
    d=root/'summary';f=root/'figures';rep=root/'reports';d.mkdir(exist_ok=True);f.mkdir(exist_ok=True);rep.mkdir(exist_ok=True)
    long=[];sample=[]
    for r in rows:
        for mode,x in r['contrast'].items():
            method,layer=mode.rsplit('_L',1)
            long.append({'paper_id':r['paper_id'],'group':r['group'],'mode':method,'layer':int(layer),
              'same_first_token':r['same_first_token'],'title_specific_advantage':x['title_specific_advantage'],
              'true_margin':x['true_margin'],'shuffle_margin':x['shuffle_margin'],'seconds':r['seconds']})
    cols=['paper_id','group','mode','layer','same_first_token','title_specific_advantage','true_margin','shuffle_margin','seconds']
    csvwrite(d/'paper_layer_contrasts.csv',long,cols)
    summaries=[]
    for g in ['ALL','A','B','C','D']:
        for mode in ['jlens','vanilla','final']:
            for l in (LAYERS if mode!='final' else [63]):
                x=[r['title_specific_advantage'] for r in long if r['mode']==mode and r['layer']==l and (g=='ALL' or r['group']==g) and not r['same_first_token']]
                lo,hi=ci(x,SEED+l+sum(map(ord,g+mode)))
                summaries.append({'group':g,'mode':mode,'layer':l,'n_discriminable':len(x),'mean':statistics.mean(x) if x else None,'median':statistics.median(x) if x else None,'ci95_low':lo,'ci95_high':hi})
    csvwrite(d/'layer_summary.csv',summaries,list(summaries[0]))
    pairs=csvread(root/'matching'/'pilot50_ab_pairs.csv');pair_rows=[]
    for pair in pairs:
        for m in ['jlens','vanilla']:
            for l in LAYERS:
                z={(r['paper_id'],r['mode'],r['layer']):r for r in long}
                aa=z.get((pair['A_id'],m,l));bb=z.get((pair['B_id'],m,l))
                if aa and bb and not aa['same_first_token'] and not bb['same_first_token']:
                    pair_rows.append({'pair_id':pair['pair_id'],'layer':l,'mode':m,'A_minus_B':aa['title_specific_advantage']-bb['title_specific_advantage']})
    csvwrite(d/'matched_pair_contrasts.csv',pair_rows,['pair_id','layer','mode','A_minus_B'])
    # One matched PAIR is one independent unit. Pilot estimates only.
    pair_by=collections.defaultdict(dict)
    for r in pair_rows:pair_by[(r['mode'],r['pair_id'])][r['layer']]=r['A_minus_B']
    paired_summary=[]
    for mode in ['jlens','vanilla']:
        for layer in LAYERS+['integrated']:
            values=[]
            for pair in pairs:
                row=pair_by.get((mode,pair['pair_id']),{})
                if len(row)!=len(LAYERS):continue  # all 7 predeclared layers required
                values.append(statistics.mean(list(row.values())) if layer=='integrated' else row[layer])
            low,high=ci(values,SEED+sum(map(ord,mode))+len(str(layer)))
            paired_summary.append({'mode':mode,'layer':layer,'n_pairs':len(values),
                'mean_A_minus_B':statistics.mean(values) if values else None,
                'median_A_minus_B':statistics.median(values) if values else None,
                'positive_fraction':sum(v>0 for v in values)/len(values) if values else None,
                'ci95_low':low,'ci95_high':high,'status':'EXPLORATORY; no multiplicity correction'})
    csvwrite(d/'matched_ab_summary.csv',paired_summary,list(paired_summary[0]))
    collision=[]
    for g in 'ABCD':
        sub=[r for r in rows if r['group']==g]
        collision.append({'group':g,'n_completed':len(sub),'n_collision':sum(r['same_first_token'] for r in sub),
            'rate':sum(r['same_first_token'] for r in sub)/len(sub) if sub else None})
    csvwrite(d/'first_token_collision_audit.csv',collision,list(collision[0]))

    for stem in ['title_specific_advantage','group_contrasts','control_comparison','sample_coverage']:
        fig,ax=plt.subplots(figsize=(8.5,4.7))
        if stem=='title_specific_advantage':
            for mode in ['jlens','vanilla']:
                z=[x for x in summaries if x['group']=='ALL' and x['mode']==mode];ax.plot([x['layer'] for x in z],[x['mean'] for x in z],marker='o',label=mode)
            ax.set(ylabel='True margin minus shuffled margin',xlabel='Source Layer',title='Title-specific advantage (discriminable only)');ax.legend()
        elif stem=='group_contrasts':
            for g in ['A','B','C','D']:
                z=[x for x in summaries if x['group']==g and x['mode']=='jlens'];ax.plot([x['layer'] for x in z],[x['mean'] for x in z],marker='o',label=g)
            ax.set(xlabel='Layer',ylabel='Mean title-specific advantage',title='A/B/C/D (exploratory only)');ax.legend()
        elif stem=='control_comparison':
            z=[x for x in long if x['mode']=='jlens' and x['layer']==48 and not x['same_first_token']]
            ax.scatter([x['shuffle_margin'] for x in z],[x['true_margin'] for x in z],alpha=.7)
            ax.set(xlabel='Shuffle-title margin',ylabel='True-title margin',title='L48 true vs shuffled controls')
        else:
            ct=collections.Counter(r['group'] for r in rows)
            ax.bar(list('ABCD'),[ct[g] for g in 'ABCD']);ax.set(xlabel='Group',ylabel='Completed papers',title='Stage 5 pilot coverage')
        ax.grid(alpha=.2);fig.tight_layout();fig.savefig(f/(stem+'.png'),dpi=170);fig.savefig(f/(stem+'.pdf'));plt.close(fig)
    same=sum(r['same_first_token'] for r in rows)
    report=['# Stage 5 · Pilot50 v1 Controlled Readout','',f'Status: {len(rows)}/50 completed; same-first-token (non-discriminable): {same}.',
     '', '## Research question','Does the title-specific gold-versus-false first-token readout differ across frozen A/B/C/D behavioral groups?',
     '', '## Protocol','Model Qwen3-32B BF16; Public Neuronpedia Jacobian Lens; L16/24/32/40/48/56/62; final L63 reference.',
     'Two model contexts per paper: true paper title and crossed-source matched paper title.',
     'Each context scores the first token of the frozen gold and false author from the SAME logits.',
     'Title-specific advantage = (gold−false under true title) − (gold−false under shuffled title).',
     'First-token ties excluded from author-discriminative analysis but always counted and retained.',
     '', '## Cohort and control quality',f'Original frozen group labels preserved. Completed groups: {dict(collections.Counter(r["group"] for r in rows))}.',
     f'Frozen exact citation-bin+field A/B pairs: {len(pairs)}; paired summaries in matched_ab_summary.csv.',
     'False author validated by name against provided paper author list; external author identity collision not independently checked.',
     'This is a RESOURCE-CONSTRAINED PILOT, not a confirmatory result. Stage4 first-token/teacher-forced results are separate.',
     '', '## Layer-level J-Lens results','|Layer|n discriminable|Mean title-specific advantage|95% bootstrap CI|','|---|---:|---:|---|']
    for x in summaries:
        if x['group']=='ALL' and x['mode']=='jlens':report.append(f'|L{x["layer"]}|{x["n_discriminable"]}|{x["mean"]}|[{x["ci95_low"]}, {x["ci95_high"]}]|')
    report+=['','## A/B matched-pair inference (exploratory)','All seven fixed layers included in predeclared integrated endpoint; bootstrap resamples matched pairs.','|Mode|Layer|n complete pairs|Mean A-B|95% CI|','|---|---|---:|---:|---|']
    for r in paired_summary:
        if r['mode']=='jlens':report.append(f'|{r["mode"]}|{r["layer"]}|{r["n_pairs"]}|{r["mean_A_minus_B"]}|[{r["ci95_low"]}, {r["ci95_high"]}]|')
    report+=['','## First-token collisions by original group','|Group|Completed|Collision|Rate|','|---|---:|---:|---:|']
    for r in collision:report.append(f'|{r["group"]}|{r["n_completed"]}|{r["n_collision"]}|{r["rate"]}|')
    report+=['','## Interpretation limits' ,'Differences are first-token candidate discrimination, NOT full-name factual recognition.',
      'Title shuffling may alter topic/length/other prompt characteristics even with field/bin matching.',
      'No causal knowledge conclusion. C/D have small sample sizes. Multiple testing not corrected.',
      'These are descriptive bootstrap intervals and must not be treated as confirmatory discovery.',
      '', '## Artifacts','Raw: raw/pilot50_results.jsonl; frozen samples: cohort/pilot50_v1.csv; controls: controls/pilot50_controls.csv.',
      'Summary: summary/paper_layer_contrasts.csv, layer_summary.csv, matched_pair_contrasts.csv, matched_ab_summary.csv, first_token_collision_audit.csv.',
      'Figures: figures/*.png and *.pdf, regenerate with analyze subcommand.',
      'Future full-cohort work MUST reuse the exact pilot50_v1 IDs and frozen control mappings, including non-discriminable cases.']
    (rep/'pilot50_experiment_report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    write_json(rep/'pilot50_audit_manifest.json',{'pilot_id':'pilot50_v1','n_completed':len(rows),'n_same_first_token':same,'protocol_sha':sha(meta['manifest']),'n_frozen_pairs':len(pairs),'n_pair_layer_rows':len(pair_rows),'status':'complete' if len(rows)==50 else 'partial'})
    print('ANALYSIS SAVED',root,'completed',len(rows),'same_first_token',same,'matched_pair_layer_rows',len(pair_rows))

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run','analyze']);p.add_argument('--root',default=str(ROOT()));p.add_argument('--data',default=str(DATA()));p.add_argument('--stage4',default=str(STAGE4()));p.add_argument('--lens',default=str(LENS()));p.add_argument('--gpu-layers',type=int,default=29);p.add_argument('--max-papers',type=int,default=None);p.add_argument('--max-seconds',type=int,default=4500);p.add_argument('--paper-reserve-seconds',type=int,default=450)
    a=p.parse_args()
    if a.command=='prepare':prepare(a)
    elif a.command=='run':run(a)
    else:analyze(a)
if __name__=='__main__':main()
