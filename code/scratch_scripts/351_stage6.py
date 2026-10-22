#!/usr/bin/env python3
"""Stage 6: Full-author conditional JMRR, paper/layer/bin trajectories, reproducible artifacts.

Uses frozen Stage5 pilot50_v1, optionally reuses Stage4 per-author readouts only after
strict consistency checks. Stage4 and Stage6 source protocols are not silently mixed.
Single file; CPU prepare/analyze, GPU run. No claim of unassisted full-name recall.
"""
import argparse,collections,csv,hashlib,importlib.util,json,math,os,statistics,time
from pathlib import Path

LAYERS=[16,24,32,40,48,56,62]
GROUPS=('A','B','C','D')
PROMPT='Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'
MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
ROOT=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_stage6')
STAGE5=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_stage5_crossed_v2')
STAGE4=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/351_all/351_stage4_artifacts/raw/results.jsonl')
LENS=lambda:Path(f'/scratch/{os.environ.get("USER","unknown")}/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')


def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');os.replace(tmp,p)

def writecsv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    with tmp.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    os.replace(tmp,p)

def readcsv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def load_jsonl(p):
    if not p.exists():return []
    with p.open(encoding='utf-8') as f:return [json.loads(x) for x in f if x.strip()]

def names(r):return [x.strip() for x in r['authors'].split(';') if x.strip()]

def bootstrap(values,seed=3516,B=2000):
    if len(values)<2:return (None,None)
    import numpy as np
    v=np.asarray(values,dtype=float);rng=np.random.default_rng(seed)
    sim=v[rng.integers(0,len(v),size=(B,len(v)))].mean(axis=1)
    return tuple(map(float,np.quantile(sim,[.025,.975])))

def inputs(a):
    s=Path(a.stage5);cohort=readcsv(s/'cohort/pilot50_v1.csv')
    if len(cohort)!=50 or len({r['paper_id'] for r in cohort})!=50:raise RuntimeError('Frozen pilot50 invalid')
    if collections.Counter(r['group'] for r in cohort)!={'A':20,'B':20,'C':7,'D':3}:raise RuntimeError('Original group counts changed')
    if sum(str(r['stage4_existing']).lower()=='true' for r in cohort)!=20:raise RuntimeError('Stage4 reuse cohort not 20')
    for r in cohort:
        if not names(r):raise RuntimeError('No authors: '+r['paper_id'])
    return s,cohort

def existing(path,cohort,protocol):
    valid_ids={r['paper_id'] for r in cohort};done={}
    for r in load_jsonl(path):
        if r['paper_id'] not in valid_ids:raise RuntimeError('Unknown paper in existing results')
        if r['protocol']!=protocol:raise RuntimeError('Stage6 scoring protocol mismatch in existing data')
        if r['paper_id'] in done:raise RuntimeError('Duplicate Stage6 paper: '+r['paper_id'])
        done[r['paper_id']]=r
    return done

def stage4_reuse(source,cohort,model_tokenizer=None):
    """Do not reinterpret old scores without verifying stage4 schema and prompt.
    For reuse, require complete author names, exact prompt, layers and all token ranks.
    """
    sr={r['paper_id']:r for r in load_jsonl(Path(source))}
    reused={};reasons={}
    for p in cohort:
        pid=p['paper_id']
        if str(p['stage4_existing']).lower()!='true':continue
        r=sr.get(pid)
        if not r:reasons[pid]='stage4_missing';continue
        expected_prompt=PROMPT.format(title=p['title'],year=p['year'])
        if r.get('prompt')!=expected_prompt:reasons[pid]='prompt_not_identical';continue
        if r.get('group')!=p['group']:reasons[pid]='group_mismatch';continue
        candidates=r.get('authors_scored',[])
        expected=names(p)
        # Include all authors, preserve author order and no silent skipping.
        if len(candidates)!=len(expected) or [x.get('name') for x in candidates]!=expected:
            reasons[pid]='author_order_or_count_mismatch';continue
        rr=[];failed=None
        for au in candidates:
            scores=au.get('measurements',{})
            needed=['final']+[f'{mode}_L{l}' for l in LAYERS for mode in ('jlens','vanilla')]
            if any(k not in scores for k in needed):failed='missing_measurement';break
            tokids=au.get('token_ids')
            if not tokids:failed='missing_token_ids';break
            if model_tokenizer and tokids!=model_tokenizer.encode(' '+au['name'],add_special_tokens=False):failed='author_tokenization_disagrees';break
            for mode,layer,key in [('final',63,'final')]+[(m,l,f'{m}_L{l}') for l in LAYERS for m in ('jlens','vanilla')]:
                ts=scores[key].get('tokens',[])
                if len(ts)!=len(tokids):failed='token_count_mismatch';break
                for j,t in enumerate(ts):
                    if int(t.get('token_id',-1))!=int(tokids[j]) or int(t.get('rank',0))<1:
                        failed='token_id_or_rank_mismatch';break
                    rr.append(dict(author=au['name'],author_index=expected.index(au['name']),token_index=j,
                        token_id=int(tokids[j]),mode=mode,layer=layer,rank=int(t['rank']),
                        logprob=float(t['logprob']),rr=1/int(t['rank'])))
                if failed:break
            if failed:break
        if failed:reasons[pid]=failed;continue
        reused[pid]={'paper_id':pid,'group':p['group'],'protocol':'stage6_v1_conditional_full_author_same_stage4',
           'source':'stage4_verified_reuse','rows':rr,'n_authors':len(expected),'seconds':0.0,
           'prompt':expected_prompt}
    return reused,reasons

def make_protocol(s,cohort,a):
    obj=dict(version='stage6_v1_conditional_full_author_same_stage4',layers=LAYERS,
        model=MODEL,revision=REV,prompt=PROMPT,tokenization='encode(prompt) + encode(ASCII_SPACE + full_author); forced token ID prefixes',
        ranking='1+number_of_vocab_logits_strictly_greater_than_gold_logit',
        author_mean='arithmetic mean reciprocal rank of each author token',
        paper_layer='arithmetic mean over all authors; all gold authors',
        paper_integrated='arithmetic mean across exactly 7 selected layers',
        log10rank='mean_author(mean_token(log10(rank)))',
        scoring='conditional teacher forcing; not free recall',stage5_cohort_sha256=sha_file(s/'cohort/pilot50_v1.csv'),
        stage5_manifest_sha256=sha_file(s/'config/protocol.json'),
        sample='pilot50_v1; A20/B20/C7/D3; fixed stage5 cohort')
    return obj

def run(a):
    s,cohort=inputs(a);root=Path(a.root);root.mkdir(parents=True,exist_ok=True)
    protocol=make_protocol(s,cohort,a);pf=root/'config/protocol.json'
    if pf.exists() and json.loads(pf.read_text())!=protocol:raise RuntimeError('Protocol/cohort changed: refusing overwrite')
    if not pf.exists():dump(pf,protocol)
    data=root/'raw/pilot50_full_author.jsonl';done=existing(data,cohort,protocol['version'])
    runtime=root/'config/runtime.json'
    runtime_info={'model':MODEL,'revision':REV,'layers':LAYERS,'lens_sha256':sha_file(a.lens) if Path(a.lens).exists() else None,'scoring_protocol':protocol['version']}
    if runtime.exists() and json.loads(runtime.read_text())!=runtime_info:raise RuntimeError('Runtime/Lens mismatch; cannot resume')
    if not runtime.exists():dump(runtime,runtime_info)
    print('Stage6: saved',len(done),'of',len(cohort),'papers',flush=True)
    if a.reuse_stage4 and not a.no_reuse_stage4:
        reused,reasons=stage4_reuse(a.stage4,cohort)
        # Deliberately do not trust schema migration if any old paper incompatible.
        if reasons:
            print('Stage4 reusable:',len(reused),'out of 20; rejected:',reasons,flush=True)
            if a.strict_reuse:raise RuntimeError('Stage4 reuse not fully compatible; rerun originals or inspect reasons')
        for p in cohort:
            row=reused.get(p['paper_id'])
            if row and row['paper_id'] not in done:
                with data.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
                done[row['paper_id']]=row
        print('After verified reuse:',len(done),'of 50',flush=True)
    todo=[x for x in cohort if x['paper_id'] not in done]
    if a.max_papers is not None:todo=todo[:a.max_papers]
    print('GPU papers queued:',len(todo),flush=True)
    if not todo:return
    import torch,transformers,jlens
    from transformers import AutoTokenizer,AutoModelForCausalLM
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
    dm.update({f'model.layers.{i}':(0 if i<a.gpu_layers else 'cpu') for i in range(64)})
    hf=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()
    lens=jlens.JacobianLens.load(str(a.lens));model=jlens.from_hf(hf,tokenizer)
    # Same token-ID readout implementation as the successful Stage5, loaded from local script.
    helper=Path(a.stage5_script)
    spec=importlib.util.spec_from_file_location('s5_readout',helper);s5=importlib.util.module_from_spec(spec);spec.loader.exec_module(s5)
    if s5.LAYERS!=LAYERS or s5.PROMPT!=PROMPT:raise RuntimeError('Stage5 readout layers/prompt differ')
    if not callable(s5.readout):raise RuntimeError('Missing stage5 readout')
    started=time.monotonic();history=[]
    for p in todo:
        if a.max_seconds and time.monotonic()-started+max([a.paper_reserve_seconds]+history)>a.max_seconds:
            print('Safe time-budget stop, all previous papers saved',flush=True);break
        t0=time.monotonic();prompt=PROMPT.format(title=p['title'],year=p['year'])
        base_ids=model.encode(prompt,max_length=512).reshape(-1).tolist()
        if len(base_ids)>=512:raise RuntimeError('Prompt too long')
        cache={};rawrows=[];authors=names(p)
        for ai,author in enumerate(authors):
            target_ids=tokenizer.encode(' '+author,add_special_tokens=False)
            if not target_ids or len(target_ids)>a.max_name_tokens:raise RuntimeError(f'Invalid author tokens paper={p["paper_id"]} author={author}')
            for j,target in enumerate(target_ids):
                ids=base_ids+target_ids[:j]
                if len(ids)>512:raise RuntimeError('Input context too long')
                key=tuple(target_ids[:j])
                if key not in cache:cache[key]=s5.readout(lens,model,prompt,ids,torch)
                for m,vec in cache[key].items():
                    if m=='final_L63':mode,layer='final',63
                    else:mode,l=m.split('_L');layer=int(l)
                    rank=int((vec>vec[target]).sum().item())+1
                    logp=float(torch.log_softmax(vec,dim=-1)[target].item())
                    rawrows.append(dict(author=author,author_index=ai,token_index=j,token_id=int(target),mode=mode,
                        layer=layer,rank=rank,rr=1/rank,logprob=logp))
        rec={'paper_id':p['paper_id'],'group':p['group'],'protocol':protocol['version'],'source':'stage6_gpu',
             'prompt':prompt,'n_authors':len(authors),'rows':rawrows,'seconds':time.monotonic()-t0}
        with data.open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        done[p['paper_id']]=rec;history.append(rec['seconds'])
        print(f'{len(done)}/50 {p["group"]} {p["paper_id"][:12]} authors={len(authors)} tokens={len(rawrows)} seconds={rec["seconds"]:.1f}',flush=True)
    print('Saved',data,flush=True)

def analyze(a):
    import numpy as np,matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    s,cohort=inputs(a);root=Path(a.root);protocol=make_protocol(s,cohort,a)
    if not (root/'config/protocol.json').exists() or json.loads((root/'config/protocol.json').read_text())!=protocol:
        raise RuntimeError('Protocol missing/differs')
    done=existing(root/'raw/pilot50_full_author.jsonl',cohort,protocol['version'])
    if not done:raise RuntimeError('No Stage6 raw data')
    byid={r['paper_id']:r for r in cohort};token_rows=[];author_values=collections.defaultdict(list)
    for pid,r in done.items():
        expected=names(byid[pid])
        seen=collections.defaultdict(list)
        for v in r['rows']:
            k=(v['mode'],int(v['layer']),int(v['author_index']))
            if int(v['rank'])<1:raise RuntimeError('Invalid rank')
            if not math.isfinite(float(v['logprob'])):raise RuntimeError('Nonfinite logprob')
            seen[k].append(v)
            token_rows.append({'paper_id':pid,'group':byid[pid]['group'],**v})
        for mode,layer in [('final',63)]+[(m,l) for l in LAYERS for m in ('jlens','vanilla')]:
            for ai,an in enumerate(expected):
                vs=seen[(mode,layer,ai)]
                if not vs or len({int(x['token_index']) for x in vs})!=len(vs) or vs[0]['author']!=an:
                    raise RuntimeError(f'Incomplete author measurements {pid} {mode} {layer} {an}')
                author_values[(pid,mode,layer)].append(dict(mrr=statistics.mean(float(x['rr']) for x in vs),
                    log10rank=statistics.mean(math.log10(int(x['rank'])) for x in vs),name=an,n_tokens=len(vs)))
    paperrows=[]
    for pid in [r['paper_id'] for r in cohort if r['paper_id'] in done]:
        c=byid[pid]
        for mode,layer in [('final',63)]+[(m,l) for l in LAYERS for m in ('jlens','vanilla')]:
            av=author_values[(pid,mode,layer)]
            paperrows.append(dict(paper_id=pid,group=c['group'],citation_bin=c['citation_bin'],field=c['field'],year=c['year'],
                stage4_existing=c['stage4_existing'],mode=mode,layer=layer,n_authors=len(av),
                jmrr=statistics.mean(x['mrr'] for x in av),log10rank=statistics.mean(x['log10rank'] for x in av)))
    papercols=['paper_id','group','citation_bin','field','year','stage4_existing','mode','layer','n_authors','jmrr','log10rank']
    writecsv(root/'summary/paper_layer_trajectories.csv',paperrows,papercols)
    # Full token file is reproducible, and text CSV is intentionally complete.
    writecsv(root/'raw/token_layer_scores.csv',token_rows,['paper_id','group','author','author_index','token_index','token_id','mode','layer','rank','rr','logprob'])
    ip=[];idx=collections.defaultdict(list)
    for r in paperrows:
        if r['layer']!=63:idx[(r['paper_id'],r['mode'])].append(r)
    for (pid,mode),rs in idx.items():
        if len(rs)!=7:raise RuntimeError('Expected exactly 7 layers')
        ip.append(dict(paper_id=pid,group=byid[pid]['group'],citation_bin=byid[pid]['citation_bin'],mode=mode,
            paper_jmrr=statistics.mean(r['jmrr'] for r in rs),paper_log10rank=statistics.mean(r['log10rank'] for r in rs)))
    writecsv(root/'summary/paper_integrated.csv',ip,['paper_id','group','citation_bin','mode','paper_jmrr','paper_log10rank'])
    groups=[];bins=sorted(set(c['citation_bin'] for c in cohort),key=lambda z:int(z.split('-')[0].replace('+','')))
    for bin_name in ['ALL']+bins:
        for group in GROUPS:
            for mode in ('jlens','vanilla'):
                for l in LAYERS:
                    v=[r['jmrr'] for r in paperrows if r['mode']==mode and r['layer']==l and r['group']==group and (bin_name=='ALL' or r['citation_bin']==bin_name)]
                    lo,hi=bootstrap(v,seed=35160+l+len(group)+len(bin_name)+len(mode))
                    groups.append(dict(citation_bin=bin_name,group=group,mode=mode,layer=l,n_papers=len(v),mean_jmrr=statistics.mean(v) if v else None,
                        median_jmrr=statistics.median(v) if v else None,ci95_low=lo,ci95_high=hi))
    gcols=['citation_bin','group','mode','layer','n_papers','mean_jmrr','median_jmrr','ci95_low','ci95_high']
    writecsv(root/'summary/group_bin_layer.csv',groups,gcols)
    contrasts=[]
    for bin_name in ['ALL']+bins:
        for mode in ('jlens','vanilla'):
            for layer in LAYERS:
                va=[r['jmrr'] for r in paperrows if r['mode']==mode and r['layer']==layer and r['group']=='A' and (bin_name=='ALL' or r['citation_bin']==bin_name)]
                vb=[r['jmrr'] for r in paperrows if r['mode']==mode and r['layer']==layer and r['group']=='B' and (bin_name=='ALL' or r['citation_bin']==bin_name)]
                lo,hi=(None,None)
                if len(va)>=2 and len(vb)>=2:
                    rng=np.random.default_rng(351600+layer+len(bin_name)+len(mode))
                    a0=np.asarray(va);b0=np.asarray(vb)
                    dif=a0[rng.integers(0,len(va),size=(2000,len(va)))].mean(1)-b0[rng.integers(0,len(vb),size=(2000,len(vb)))].mean(1)
                    lo,hi=map(float,np.quantile(dif,[.025,.975]))
                contrasts.append(dict(citation_bin=bin_name,mode=mode,layer=layer,n_A=len(va),n_B=len(vb),
                    A_minus_B=statistics.mean(va)-statistics.mean(vb) if va and vb else None,ci95_low=lo,ci95_high=hi,
                    inference='UNMATCHED observational, exploratory'))
    writecsv(root/'summary/a_minus_b_bin_layer.csv',contrasts,['citation_bin','mode','layer','n_A','n_B','A_minus_B','ci95_low','ci95_high','inference'])
    integrated=[]
    for mode in ('jlens','vanilla'):
        for group in GROUPS:
            vals=[r['paper_jmrr'] for r in ip if r['group']==group and r['mode']==mode]
            lo,hi=bootstrap(vals,35161+len(group)+len(mode))
            integrated.append(dict(group=group,mode=mode,n_papers=len(vals),mean_paper_jmrr=statistics.mean(vals) if vals else None,ci95_low=lo,ci95_high=hi))
    writecsv(root/'summary/integrated_group.csv',integrated,['group','mode','n_papers','mean_paper_jmrr','ci95_low','ci95_high'])
    # Keep Stage5 crossed first-token scores analytically separate; paper-ID join is traceability only.
    stage5raw={r['paper_id']:r for r in load_jsonl(s/'raw/pilot50_results.jsonl')}
    joint=[]
    for r in ip:
        sr=stage5raw.get(r['paper_id']);key=f"{r['mode']}_L56"
        value=sr.get('contrast',{}).get(key,{}).get('title_specific_advantage') if sr else None
        joint.append(dict(**r,stage5_first_token_title_specific_L56=value))
    writecsv(root/'summary/stage5_stage6_paper_join.csv',joint,['paper_id','group','citation_bin','mode','paper_jmrr','paper_log10rank','stage5_first_token_title_specific_L56'])
    # Pair-level bootstrap (only complete matched pairs), never pool paper-bootstrap as matched inference.
    pairs=readcsv(s/'matching/pilot50_ab_pairs.csv');pairrows=[]
    for pair in pairs:
        a_id=next((pair[x] for x in ['A_id','a_paper_id','A_paper_id','paper_a','a_id'] if x in pair),None)
        b_id=next((pair[x] for x in ['B_id','b_paper_id','B_paper_id','paper_b','b_id'] if x in pair),None)
        if not a_id or not b_id:raise RuntimeError('Unknown Stage5 pair column names: '+str(list(pair)))
        for mode in ('jlens','vanilla'):
            for layer in LAYERS:
                aa=next((r['jmrr'] for r in paperrows if r['paper_id']==a_id and r['mode']==mode and r['layer']==layer),None)
                bb=next((r['jmrr'] for r in paperrows if r['paper_id']==b_id and r['mode']==mode and r['layer']==layer),None)
                if aa is not None and bb is not None:pairrows.append(dict(a_paper_id=a_id,b_paper_id=b_id,mode=mode,layer=layer,A_minus_B=aa-bb))
    writecsv(root/'summary/matched_pair_layer.csv',pairrows,['a_paper_id','b_paper_id','mode','layer','A_minus_B'])
    ps=[]
    for mode in ('jlens','vanilla'):
        for layer in LAYERS:
            v=[r['A_minus_B'] for r in pairrows if r['mode']==mode and r['layer']==layer]
            lo,hi=bootstrap(v,35162+layer+len(mode))
            ps.append(dict(mode=mode,layer=layer,n_pairs=len(v),mean_A_minus_B=statistics.mean(v) if v else None,
                ci95_low=lo,ci95_high=hi,matched=True))
    writecsv(root/'summary/matched_ab_bootstrap.csv',ps,['mode','layer','n_pairs','mean_A_minus_B','ci95_low','ci95_high','matched'])
    figs=root/'figures';figs.mkdir(parents=True,exist_ok=True)
    def save(fig,name):
        fig.tight_layout()
        for x in ['png','pdf']:fig.savefig(figs/f'{name}.{x}',dpi=180,bbox_inches='tight')
        plt.close(fig)
    for mode in ('jlens','vanilla'):
        fig,ax=plt.subplots(figsize=(9,5))
        for g in GROUPS:
            ys=[next(z['mean_jmrr'] for z in groups if z['citation_bin']=='ALL' and z['group']==g and z['mode']==mode and z['layer']==l) for l in LAYERS]
            ax.plot(LAYERS,[np.nan if x is None else x for x in ys],marker='o',label=f'{g} (n={sum(c["group"]==g for c in cohort if c["paper_id"] in done)})')
        ax.set(title=f'Stage6 {mode} · conditional full-author JMRR',xlabel='Source layer',ylabel='Paper mean JMRR',xticks=LAYERS);ax.legend();ax.grid(alpha=.2)
        save(fig,f'{mode}_abcd_jmrr')
        fig,ax=plt.subplots(figsize=(9,5))
        for g in GROUPS:
            ys=[statistics.mean([r['log10rank'] for r in paperrows if r['mode']==mode and r['layer']==l and r['group']==g]) if any(r['mode']==mode and r['layer']==l and r['group']==g for r in paperrows) else np.nan for l in LAYERS]
            ax.plot(LAYERS,ys,marker='o',label=g)
        ax.set(title=f'Stage6 {mode} · mean log10 token rank',xlabel='Source layer',ylabel='mean(log10 rank)',xticks=LAYERS);ax.legend();ax.grid(alpha=.2)
        save(fig,f'{mode}_log10_rank')
    fig,ax=plt.subplots(figsize=(9,5))
    for mode in ('jlens','vanilla'):
        rr=[next(z for z in ps if z['mode']==mode and z['layer']==l) for l in LAYERS]
        ax.plot(LAYERS,[r['mean_A_minus_B'] if r['mean_A_minus_B'] is not None else np.nan for r in rr],marker='o',label=mode)
    ax.axhline(0,color='gray',linestyle='--');ax.set(title='Matched A−B Conditional JMRR (exploratory)',xlabel='Source layer',ylabel='Mean matched pair difference',xticks=LAYERS);ax.legend();ax.grid(alpha=.2);save(fig,'matched_ab_difference')
    # Citation-bin charts (only non-empty observed bins; no fabricated estimates)
    fig,ax=plt.subplots(figsize=(10,5))
    for b in bins:
        vals=[next(z['A_minus_B'] for z in contrasts if z['mode']=='jlens' and z['citation_bin']==b and z['layer']==l) for l in LAYERS]
        if all(x is None for x in vals):continue
        ax.plot(LAYERS,[np.nan if x is None else x for x in vals],marker='.',label=b)
    ax.axhline(0,color='gray',linestyle='--');ax.set(title='Citation-bin A−B (UNMATCHED, descriptive)',xlabel='Source layer',ylabel='A−B JMRR',xticks=LAYERS);ax.legend(fontsize=7,ncol=2);ax.grid(alpha=.2);save(fig,'citation_bin_a_minus_b')
    summary={'completed':len(done),'planned':50,'groups':dict(collections.Counter(byid[k]['group'] for k in done)),
        'reused_stage4':sum(v.get('source')=='stage4_verified_reuse' for v in done.values()),'measured_gpu':sum(v.get('source')=='stage6_gpu' for v in done.values()),
        'matching_total_pairs':len(pairs),'matched_pairs_observed':len({(r['a_paper_id'],r['b_paper_id']) for r in pairrows}),
        'protocol':'stage6_v1_conditional_full_author_same_stage4','notes':'Stage6 is conditional teacher forcing, not free recall; Stage5 measures separate first-token crossed control.'}
    dump(root/'summary/summary.json',summary)
    lines=['# Stage 6 · Full-author Conditional JMRR Pilot','',f"**Completion:** {len(done)}/50; groups: {summary['groups']}; Stage4 verified reused: {summary['reused_stage4']}; new GPU measured: {summary['measured_gpu']}.",
       '', '## Research question','How do per-paper full-author conditional JMRR trajectories vary by fixed A/B/C/D labels and citation bins?',
       '', '## Frozen protocol','- Original group labels preserved (A410? see frozen cohort; no relabeling).',
       f'- Seven source layers: {LAYERS}; final model output excluded from integrated score.',
       '- Each author: mean reciprocal rank over all forced gold-name tokens; each paper: mean over authors; integrated: mean across 7 layers.',
       '- Log10 rank is averaged at the token level before author- and paper-level averaging.',
       '- Teacher forcing supplies each true author prefix; this does not measure unaided retrieval.',
       '- Stage5 title/author controls are a separate measurement, and were not implicitly applied to these full-name scores.',
       '', '## Actual group estimates', '| Group | Lens | Papers | Mean integrated JMRR | 95% paper-bootstrap CI |','|---|---|---:|---:|---|']
    for x in integrated:
        fmt=lambda a: 'NA' if a is None else f'{a:.6f}'
        lines.append(f"| {x['group']} | {x['mode']} | {x['n_papers']} | {fmt(x['mean_paper_jmrr'])} | [{fmt(x['ci95_low'])}, {fmt(x['ci95_high'])}] |")
    lines += ['','## Matching','',f"{summary['matched_pairs_observed']} complete A/B pairs of {summary['matching_total_pairs']} planned pairs. Pair-bootstrap summaries are in `summary/matched_ab_bootstrap.csv`.",
       'The 50-paper pilot is exploratory; no causal inference, no A>B claim from an uncorrected Layer result.',
       '', '## Known limitations','- Matched bin/year/field observational comparison still has unobserved confounders.',
       '- Small within-bin sample sizes give imprecise estimates; empty group/bin combinations are reported as NA.',
       '- Whole-name rank is conditional on name prefixes; any stronger claim requires negative controls.',
       '- Stage4 reuse depends on exact prompt and token/rank parity; records failing checks are recomputed.',
       '- All 100-incorrect-author and empirical-null controls belong to planned Stage7 (NOT RUN).',
       '', '## Files','- `raw/pilot50_full_author.jsonl` — incremental per-paper results',
       '- `raw/token_layer_scores.csv` — complete paper×author×token×layer scores',
       '- `summary/paper_layer_trajectories.csv` — equal-author paper JMRR and log10 Rank',
       '- `summary/paper_integrated.csv` — seven-layer paper score',
       '- `summary/stage5_stage6_paper_join.csv` — aligned but distinct conditional and title-control measures',
       '- `summary/group_bin_layer.csv` — A/B/C/D and citation-bin bootstrap summaries',
       '- `summary/a_minus_b_bin_layer.csv` — unmatched differences',
       '- `summary/matched_pair_layer.csv` and `matched_ab_bootstrap.csv` — matched comparisons',
       '- `figures/*.png`, `figures/*.pdf` — observed trajectories; no invented control charts','']
    # Correct no-typo cohort provenance as a literal frozen promise
    lines=[z.replace('A410? see frozen cohort; no relabeling','A=4110, B=2186, C=511, D=34 in source full cohort; no relabeling') for z in lines]
    (root/'reports').mkdir(parents=True,exist_ok=True)
    (root/'reports/experiment_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('ANALYSIS SAVED',root,'papers=',len(done),'matched_pairs=',summary['matched_pairs_observed'],flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='cmd',required=True)
    for command in ('run','analyze','audit-reuse'):
        p=sub.add_parser(command)
        p.add_argument('--root',default=str(ROOT()));p.add_argument('--stage5',default=str(STAGE5()));p.add_argument('--stage4',default=str(STAGE4()))
        p.add_argument('--lens',default=str(LENS()));p.add_argument('--stage5-script',default=str(Path.home()/'351_stage5.py'))
        p.add_argument('--gpu-layers',type=int,default=29);p.add_argument('--max-papers',type=int);p.add_argument('--max-seconds',type=int,default=4500)
        p.add_argument('--paper-reserve-seconds',type=int,default=500);p.add_argument('--max-name-tokens',type=int,default=32)
        p.add_argument('--no-reuse-stage4',action='store_true');p.add_argument('--strict-reuse',action='store_true')
        p.set_defaults(reuse_stage4=True)
    a=parser.parse_args()
    if a.cmd=='audit-reuse':
        _,cohort=inputs(a);r,reasons=stage4_reuse(a.stage4,cohort)
        print('Reusable Stage4:',len(r),'of 20');print('Rejected:',json.dumps(reasons,indent=2))
    elif a.cmd=='run':run(a)
    elif a.cmd=='analyze':analyze(a)
if __name__=='__main__':main()
