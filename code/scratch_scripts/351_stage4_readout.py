#!/usr/bin/env python3
"""Stage 4: exploratory multi-author gold readout benchmark, NOT the 6841-paper analysis.
Qwen3-32B BF16 + public Neuronpedia J-Lens + Vanilla + final logits;
explicit token-ID teacher forcing; durable per-paper JSONL and resumability.
"""
import argparse,csv,hashlib,json,math,os,random,statistics,time,collections,sys
from collections import defaultdict
from pathlib import Path
MODEL='Qwen/Qwen3-32B'
REV='9216db5781bf21249d130ec9da846c4624c16137'
BINS=['0-2','3-4','5-8','9-16','17-32','33-64','65-128','129-256','257-512','513-1024','1025-2048','2049-4096','4097+']
PROMPT='Who are the authors of the paper titled "{title}" ({year})?\nAuthors:'

def select(rows,seed,quotas):
    """Deterministic per-group stratified draws; ordering is a prefix across --n."""
    pools=defaultdict(lambda: defaultdict(list))
    for r in rows:
        if (r.get('group_351') in quotas and r.get('paper_id') and
            r.get('title','').strip() and r.get('year','').strip() and r.get('authors','').strip()):
            pools[r['group_351']][r['citation_bin']].append(r)
    per_group={}
    for group,limit in quotas.items():
        group_rows=[]
        for bin_ in BINS:
            arr=pools[group][bin_]
            random.Random(f'{seed}:{group}:{bin_}').shuffle(arr)
        while len(group_rows)<limit:
            found=False
            for bin_ in BINS:
                if pools[group][bin_] and len(group_rows)<limit:
                    group_rows.append(pools[group][bin_].pop())
                    found=True
            if not found:raise RuntimeError(f'Insufficient {group} papers')
        per_group[group]=group_rows
    # Stable prefix: --n 4 is literally the first four of --n 20.
    out=[]
    while any(per_group.values()):
        for group in ('A','B','C','D'):
            if per_group.get(group):out.append(per_group[group].pop(0))
    return out

def unique_names(r):
    out=[];seen=set()
    for a in r['authors'].split(';'):
        a=' '.join(a.strip().split())
        if a and a.casefold() not in seen:seen.add(a.casefold());out.append(a)
    return out

def token_plan(tok,base_prompt,name,max_name_tokens):
    """Explicit token-ID continuation. Do not re-tokenize prompt+name.

    The prompt is tokenized once; a name is independently tokenized with one
    leading ASCII space, then appended as a token sequence. This defines a
    forced-token protocol, NOT the tokenizer's natural joint encoding.
    """
    if not name.strip():return None,'empty_name'
    rest=tok.encode(' '+name,add_special_tokens=False)
    if not rest:return None,'empty_name_tokens'
    if len(rest)>max_name_tokens:return None,'too_many_name_tokens'
    return {'token_ids':[int(x) for x in rest],
            'contexts':[(tuple(int(x) for x in rest[:j]),int(target)) for j,target in enumerate(rest)]},None


def apply_on_ids(lens,model,prompt,ids,layers,max_seq_len,torch):
    """Run the unmodified public lens on a precisely specified token sequence.

    jlens.apply internally calls model.encode(prompt). Override that *one call*
    to supply prevalidated IDs, restoring the method even on failure. Both
    Jacobian and vanilla readouts therefore see the same token-ID context.
    """
    if len(ids)>max_seq_len:raise ValueError('Token-ID context exceeds max_seq_len')
    original=model.encode
    reference=original(prompt,max_length=max_seq_len)
    if reference.ndim!=2 or reference.shape[0]!=1:
        raise RuntimeError(f'Unexpected jlens encode shape: {tuple(reference.shape)}')
    fixed=torch.tensor([ids],dtype=reference.dtype,device=reference.device)
    def fixed_encode(_ignored,max_length=512):
        if len(ids)>max_length:raise ValueError('Forced context exceeds lens max_length')
        return fixed
    try:
        model.encode=fixed_encode
        with torch.inference_mode():
            j,final,jids=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=max_seq_len,use_jacobian=True)
            v,final2,vids=lens.apply(model,prompt,layers=layers,positions=[-1],max_seq_len=max_seq_len,use_jacobian=False)
    finally:
        model.encode=original
    if not torch.equal(jids.cpu(),fixed.cpu()) or not torch.equal(vids.cpu(),fixed.cpu()):
        raise RuntimeError('Jacobian/vanilla did not use requested token IDs')
    if float((final-final2).abs().max())>0.1:
        raise RuntimeError('Nonmatching paired final logits')
    return j,final,v

def measure(vec,token_id):
    import torch
    a=vec.float().reshape(-1).cpu();t=int(token_id)
    if not bool(torch.isfinite(a).all()):raise ValueError('Nonfinite logits')
    z=a[t]
    return {'token_id':t,'rank':int((a>z).sum().item())+1,'logprob':float(torch.log_softmax(a,-1)[t].item())}

def summarize(path,layers,selection):
    byid={r['paper_id']:r for r in (json.loads(s) for s in path.read_text().splitlines() if s.strip())}
    rows=[byid[x['paper_id']] for x in selection if x['paper_id'] in byid]
    counts=collections.Counter(r['group'] for r in rows)
    scored=sum(len(r['authors_scored']) for r in rows)
    skipped=sum(len(r['authors_skipped']) for r in rows)
    print('===== STAGE 4 BENCHMARK =====',len(rows),'papers',dict(counts),'authors_scored',scored,'authors_skipped',skipped,flush=True)
    if not rows:return
    print('Mean seconds per paper',round(statistics.mean(r['seconds'] for r in rows),2),'Max',max(r['seconds'] for r in rows),flush=True)
    print('Papers with NO scored authors:',sum(not r['authors_scored'] for r in rows),flush=True)
    print('Skip reasons:',dict(collections.Counter(z['reason'] for r in rows for z in r['authors_skipped'])),flush=True)
    print('PRIMARY: first-listed gold author at Authors: position; all-author probes only exploratory (order confound).')
    for l in layers:
        for mode in ('jlens','vanilla'):
            k=f'{mode}_L{l}'
            per_paper=[];first_listed=[]
            for r in rows:
                aa=r['authors_scored']
                if aa:
                    per_paper.append((statistics.mean(a['measurements'][k]['first_rr'] for a in aa), statistics.mean(a['measurements'][k]['conditional_token_mrr'] for a in aa)))
                    lead=next((a for a in aa if a['name']==r['first_listed_gold_author']),None)
                    if lead:first_listed.append(lead['measurements'][k]['first_rr'])
            if per_paper:
                print(f'L{l:02d} {mode:<7} PRIMARY_first_listed_RR={statistics.mean(first_listed) if first_listed else float("nan"):.6f} N_lead={len(first_listed)} exploratory_all_author_first_RR={statistics.mean(x for x,y in per_paper):.6f} conditional_token_MRR={statistics.mean(y for x,y in per_paper):.6f} N_papers={len(per_paper)}',flush=True)
    final=[statistics.mean(a['measurements']['final']['conditional_token_mrr'] for a in r['authors_scored']) for r in rows if r['authors_scored']]
    if final:print('Final paper_mean_conditional_token_MRR',statistics.mean(final),flush=True)

def generate_artifacts(raw_file, selection, layers, report_dir, config, args):
    """Offline deterministic results compiler. Run anytime with --report-only."""
    import datetime
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    report_dir=Path(report_dir)
    dirs={k:report_dir/k for k in ('raw','summary','figures','reports','config')}
    for d in dirs.values():d.mkdir(parents=True,exist_ok=True)
    source=[]
    if raw_file.exists():
        with raw_file.open(encoding='utf-8') as f:
            for lineno,line in enumerate(f,1):
                if not line.strip():continue
                try:rec=json.loads(line)
                except json.JSONDecodeError:
                    raise RuntimeError(f'Invalid JSONL at line {lineno}; check interrupted write')
                if rec.get('config')!=config:raise RuntimeError(f'Config mismatch in raw line {lineno}')
                source.append(rec)
    ids={p['paper_id'] for p in selection}
    recs={}
    for rec in source:
        pid=rec['paper_id']
        if pid in recs:raise RuntimeError(f'Duplicate paper ID in raw: {pid}')
        if pid in ids:recs[pid]=rec
    rows=[recs[p['paper_id']] for p in selection if p['paper_id'] in recs]
    # Snapshot in artifact tree. Preserve original append-only file separately.
    raw_snapshot=dirs['raw']/'results.jsonl'
    atomic_text(raw_snapshot,''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    run_config={**config,'requested_n':len(selection),'completed_n':len(rows),
                'lens_sha256':sha256_or_none(Path(args.lens)),
                'source_csv':str(Path(args.data).resolve()),
                'raw_source':str(raw_file.resolve()),
                'report_created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'report_generator':'351_stage4_readout.py'}
    atomic_text(dirs['config']/'run_config.json',json.dumps(run_config,indent=2,ensure_ascii=False))
    # Long format -- complete traceability for paper, author, token, layer, lens.
    token_cols=['paper_id','group','field','citation_bin','year','author_index','author_name','is_first_listed','mode','layer','token_index','token_id','rank','reciprocal_rank','logprob']
    token_rows=[];paper_rows=[];skip_rows=[]
    paper_scores=collections.defaultdict(list)
    for r in rows:
        for bad in r.get('authors_skipped',[]):
            skip_rows.append({'paper_id':r['paper_id'],'group':r['group'],'author_name':bad['name'],'reason':bad['reason']})
        for ai,a in enumerate(r.get('authors_scored',[])):
            is_lead=a['name']==r['first_listed_gold_author']
            for key,score in a['measurements'].items():
                if key=='final':mode='final';layer=63
                else:mode,layerstr=key.split('_L');layer=int(layerstr)
                for ti,t in enumerate(score['tokens']):
                    token_rows.append({'paper_id':r['paper_id'],'group':r['group'],'field':r['field'],
                      'citation_bin':r['citation_bin'],'year':r['year'],'author_index':ai,
                      'author_name':a['name'],'is_first_listed':int(is_lead),
                      'mode':mode,'layer':layer,'token_index':ti,
                      'token_id':t['token_id'],'rank':t['rank'],
                      'reciprocal_rank':1/t['rank'],'logprob':t['logprob']})
                paper_scores[(r['paper_id'],mode,layer)].append((is_lead,score))
    for r in rows:
        for mode,layer in [('final',63)]+[(m,l) for l in layers for m in ('jlens','vanilla')]:
            val=paper_scores.get((r['paper_id'],mode,layer),[])
            first=next((x['first_rr'] for lead,x in val if lead),None)
            paper_rows.append({'paper_id':r['paper_id'],'group':r['group'],'citation_bin':r['citation_bin'],
                'field':r['field'],'year':r['year'],'mode':mode,'layer':layer,
                'first_listed_first_rr':first,
                'all_author_first_rr':statistics.mean(x['first_rr'] for _,x in val) if val else None,
                'conditional_token_mrr':statistics.mean(x['conditional_token_mrr'] for _,x in val) if val else None,
                'conditional_mean_logprob':statistics.mean(x['conditional_mean_logprob'] for _,x in val) if val else None,
                'n_authors_scored':len(val),'n_authors_raw':r['n_authors_raw'],
                'seconds':r['seconds'],'peak_gpu_gib':r['peak_gpu_gib']})
    write_csv(dirs['raw']/'token_scores.csv',token_rows,token_cols)
    write_csv(dirs['raw']/'skipped_authors.csv',skip_rows,['paper_id','group','author_name','reason'])
    paper_cols=['paper_id','group','citation_bin','field','year','mode','layer','first_listed_first_rr',
                'all_author_first_rr','conditional_token_mrr','conditional_mean_logprob','n_authors_scored','n_authors_raw','seconds','peak_gpu_gib']
    write_csv(dirs['summary']/'paper_metrics.csv',paper_rows,paper_cols)
    # Each row is one PAPER; inference never treats tokens/authors as independent papers.
    group_metrics=[]
    metrics=('first_listed_first_rr','all_author_first_rr','conditional_token_mrr','conditional_mean_logprob')
    for group in ('ALL','A','B','C','D'):
        for mode,layer in [('final',63)]+[(m,l) for l in layers for m in ('jlens','vanilla')]:
            subset=[x for x in paper_rows if x['mode']==mode and x['layer']==layer and (group=='ALL' or x['group']==group)]
            for metric in metrics:
                values=[float(x[metric]) for x in subset if x[metric] is not None]
                lo,hi=bootstrap_ci(values,seed=3514+layer+sum(map(ord,group+mode+metric)))
                group_metrics.append({'group':group,'mode':mode,'layer':layer,'metric':metric,
                  'n_papers':len(values),'mean':statistics.mean(values) if values else None,
                  'ci95_low':lo,'ci95_high':hi,'ci_method':'percentile paper bootstrap (2000 replicates)' if len(values)>=2 else 'unavailable: n<2'})
    gcols=['group','mode','layer','metric','n_papers','mean','ci95_low','ci95_high','ci_method']
    write_csv(dirs['summary']/'layer_metrics.csv',group_metrics,gcols)
    # Only A vs B is the target contrast; small pilot must not be interpreted as evidence.
    contrasts=[]
    for mode in ('jlens','vanilla'):
        for layer in layers:
            for metric in ('first_listed_first_rr','conditional_token_mrr'):
                av=[float(x[metric]) for x in paper_rows if x['group']=='A' and x['mode']==mode and x['layer']==layer and x[metric] is not None]
                bv=[float(x[metric]) for x in paper_rows if x['group']=='B' and x['mode']==mode and x['layer']==layer and x[metric] is not None]
                low,high=bootstrap_difference_ci(av,bv,seed=3514+layer+len(metric))
                contrasts.append({'mode':mode,'layer':layer,'metric':metric,'group_a_n':len(av),'group_b_n':len(bv),
                  'a_minus_b':statistics.mean(av)-statistics.mean(bv) if av and bv else None,
                  'ci95_low':low,'ci95_high':high,'inference':'exploratory only; unmatched pilot'})
    write_csv(dirs['summary']/'a_vs_b_exploratory.csv',contrasts,['mode','layer','metric','group_a_n','group_b_n','a_minus_b','ci95_low','ci95_high','inference'])
    counts=collections.Counter(r['group'] for r in rows)
    reasons=collections.Counter(s['reason'] for s in skip_rows)
    summary={'status':'complete' if len(rows)==len(selection) else 'partial',
        'requested_papers':len(selection),'completed_papers':len(rows),'groups':dict(counts),
        'authors_scored':sum(len(r.get('authors_scored',[])) for r in rows),
        'authors_skipped':len(skip_rows),'skip_reasons':dict(reasons),
        'papers_with_no_scored_authors':sum(not r.get('authors_scored',[]) for r in rows),
        'mean_seconds_per_paper':statistics.mean(r['seconds'] for r in rows) if rows else None,
        'max_gpu_gib':max((r['peak_gpu_gib'] for r in rows),default=None),
        'metrics_file':'summary/layer_metrics.csv','contrasts_file':'summary/a_vs_b_exploratory.csv',
        'control_analysis':'NOT RUN: no matched-false or title-shuffle controls in Stage 4',
        'precision_note':'The public lens was fit on a separately sourced model whose exact revision is not recorded in lens provenance.'}
    atomic_text(dirs['summary']/'summary.json',json.dumps(summary,ensure_ascii=False,indent=2))
    # Figures; show only real computed results. Never generate placeholder control charts.
    all_metrics={(x['mode'],x['layer'],x['metric']):x for x in group_metrics if x['group']=='ALL'}
    for metric,title,stem in [('first_listed_first_rr','First-listed author / Unconditional first-token RR','first_listed_first_rr'),
                              ('conditional_token_mrr','All gold authors / Conditional token MRR (teacher-forced)','conditional_token_mrr')]:
        fig,ax=plt.subplots(figsize=(8.6,4.8))
        for mode,label in [('jlens','Public J-Lens'),('vanilla','Vanilla Lens')]:
            xx=[];yy=[];low=[];high=[]
            for layer in layers:
                record=all_metrics.get((mode,layer,metric))
                if record and record['mean'] is not None:
                    xx.append(layer);yy.append(record['mean']);low.append(record['ci95_low']);high.append(record['ci95_high'])
            if xx:
                ax.plot(xx,yy,marker='o',label=label)
                if all(v is not None for v in low+high):ax.fill_between(xx,low,high,alpha=0.13)
        ref=all_metrics.get(('final',63,metric))
        if ref and ref['mean'] is not None:ax.axhline(ref['mean'],linestyle='--',label='Actual final model')
        ax.set(xlabel='Source layer',ylabel='Paper-level mean reciprocal rank',title=title)
        ax.set_xticks(layers);ax.set_ylim(bottom=0);ax.legend(fontsize=9);ax.grid(alpha=.2)
        fig.tight_layout();save_fig(fig,dirs['figures'],stem);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,4.8))
    for group in ('A','B','C','D'):
        xx=[];yy=[]
        for layer in layers:
            record=next((x for x in group_metrics if x['group']==group and x['mode']=='jlens' and x['layer']==layer and x['metric']=='first_listed_first_rr'),None)
            if record and record['mean'] is not None:xx.append(layer);yy.append(record['mean'])
        if xx:ax.plot(xx,yy,marker='o',label=f'{group} (n={counts[group]} papers)')
    ax.set(xlabel='Source layer',ylabel='First-listed first-token RR',title='A/B/C/D: descriptive pilot only (unmatched)')
    ax.set_xticks(layers);ax.set_ylim(bottom=0);ax.legend(fontsize=9);ax.grid(alpha=.2)
    fig.tight_layout();save_fig(fig,dirs['figures'],'abcd_descriptive');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,4.2))
    labels=['A','B','C','D'];bars=[counts[k] for k in labels]
    ax.bar(labels,bars);ax.set(xlabel='Behavioral group',ylabel='Completed papers',title='Stage 4 sample coverage')
    for i,v in enumerate(bars):ax.text(i,v+0.05,str(v),ha='center')
    fig.tight_layout();save_fig(fig,dirs['figures'],'sample_coverage');plt.close(fig)
    lines=[
      '# Stage 4 — Gold-author readout benchmark',
      '', f'**Status:** {summary["status"].upper()} · {len(rows)}/{len(selection)} planned papers completed.',
      '', '## Research question',
      'Can the pretrained public Jacobian Lens produce reproducible layer-wise candidate-token readouts on scientific-paper author prompts, before the formal A/B/C/D study?',
      '', '## Methods',
      f'- Model: `{MODEL}` · pinned revision `{REV}` · BF16.',
      f'- Lens: `{args.lens}`; lens SHA-256 in `config/run_config.json`.',
      f'- Prompt: `{PROMPT}` with title/year substitution.',
      f'- Layers: {layers}; device map uses {args.gpu_layers} blocks on GPU and remaining blocks on CPU.',
      '- Primary measure: first-listed author first-token RR at `Authors:` with no author prefix.',
      '- Exploratory measure: all listed authors at the *same* list-start position (author-order confound).',
      '- Auxiliary measure: teacher-forced mean per-token reciprocal rank of the complete name (not unprompted full-name recall).',
      '- Aggregation: each paper has equal weight; author and token rows are not independent samples.',
      '- Percentile bootstrap intervals resample papers within groups; suppressed for n < 2.',
      '', '## Dataset and completion',
      f'- Group counts: {dict(counts)}.',
      f'- Authors scored: {summary["authors_scored"]}; skipped: {len(skip_rows)}; skip reasons: {dict(reasons)}.',
      f'- Papers with no scored authors: {summary["papers_with_no_scored_authors"]}.',
      f'- Mean observed wall time: {summary["mean_seconds_per_paper"]} seconds per paper.',
      '', '## Actual measured results',
      '| Layer | J-Lens primary RR | Vanilla primary RR | J-Lens conditional MRR | Vanilla conditional MRR |',
      '|---|---:|---:|---:|---:|',
    ]
    for layer in layers:
        def fmt(m,metric):
            x=all_metrics.get((m,layer,metric),{}).get('mean')
            return f'{x:.6f}' if x is not None else 'N/A'
        lines.append(f'| {layer} | {fmt("jlens","first_listed_first_rr")} | {fmt("vanilla","first_listed_first_rr")} | {fmt("jlens","conditional_token_mrr")} | {fmt("vanilla","conditional_token_mrr")} |')
    lines += ['','## Interpretation and limitations',
      '- This is an exploratory pipeline benchmark, not a statistical test of the research hypothesis.',
      '- Even a high gold-author RR cannot alone establish factual storage or causal knowledge accessibility.',
      '- The probe position favors the first-listed author; all-author first-token probes are exploratory.',
      '- Teacher forcing reveals candidate-name prefixes and must not be interpreted as free recall.',
      '- The public average Jacobian is an approximation; generic/paper-prompt fidelity varies by layer and metric.',
      '- A/B/C/D are unbalanced in small pilot samples; reported plots are descriptive, not confirmatory.',
      '- Source CSV and lens version are recorded; exact pretrained fit model revision cannot be confirmed from lens provenance.',
      '- Matched-false and title-shuffled controls have **NOT** been executed in this Stage 4 run; no control results/figures are claimed.',
      '- Findings for omitted authors could be biased by strict tokenizer checks; see skipped_authors.csv.',
      '', '## Conclusion',
      f'- Observed {len(rows)} completed papers with {summary["authors_scored"]} scored authors. This establishes pipeline output coverage only.',
      '- Do not claim an A-vs-B difference, tool reliability across all 63 layers, or validated author knowledge without additional controls and larger matched analysis.',
      '', '## Reproducibility and figures',
      '- `raw/results.jsonl`: raw per-paper checkpoint snapshot.',
      '- `raw/token_scores.csv`: paper–author–token–layer scores.',
      '- `raw/skipped_authors.csv`: omissions and reasons.',
      '- `summary/paper_metrics.csv`: paper-level aggregates.',
      '- `summary/layer_metrics.csv`: layer/group estimates with paper-bootstrap CI where estimable.',
      '- `summary/a_vs_b_exploratory.csv`: descriptive A–B differences, not a formal test.',
      '- `summary/summary.json`: completion and validation metadata.',
      '- `config/run_config.json`: run settings and hashes.',
      '- `figures/first_listed_first_rr.png` / `.pdf`: primary rank readout.',
      '- `figures/conditional_token_mrr.png` / `.pdf`: conditional full-name diagnostic.',
      '- `figures/abcd_descriptive.png` / `.pdf`: behavioral group description.',
      '- `figures/sample_coverage.png` / `.pdf`: completed sample counts.',
      '', '**No matched-false/title-shuffle control figure is generated because this run contains no control measurements.**',
    ]
    atomic_text(dirs['reports']/'experiment_report.md','\n'.join(lines)+'\n')
    print('ARTIFACTS:',report_dir,'status=',summary['status'],'papers=',len(rows),'tokens=',len(token_rows),flush=True)


def atomic_text(path,contents):
    path=Path(path);tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(contents,encoding='utf-8');os.replace(tmp,path)


def sha256_or_none(path):
    if not path.exists():return None
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def write_csv(path,rows,cols):
    import io
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
    atomic_text(path,buf.getvalue())


def bootstrap_ci(values,seed):
    if len(values)<2:return None,None
    import numpy as np
    rng=np.random.default_rng(seed);v=np.asarray(values,dtype=float)
    sims=v[rng.integers(0,len(v),size=(2000,len(v)))].mean(axis=1)
    return float(np.quantile(sims,.025)),float(np.quantile(sims,.975))


def bootstrap_difference_ci(a,b,seed):
    if len(a)<2 or len(b)<2:return None,None
    import numpy as np
    rng=np.random.default_rng(seed);a=np.asarray(a);b=np.asarray(b)
    sim=a[rng.integers(0,len(a),size=(2000,len(a)))].mean(axis=1)-b[rng.integers(0,len(b),size=(2000,len(b)))].mean(axis=1)
    return float(np.quantile(sim,.025)),float(np.quantile(sim,.975))


def save_fig(fig,directory,stem):
    for ext in ('png','pdf'):
        dest=Path(directory)/(stem+'.'+ext)
        fig.savefig(dest,dpi=180,bbox_inches='tight')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    root=f'/scratch/{os.environ.get("USER","unknown")}/jlens'
    p.add_argument('--data',default=f'{root}/351_all/351_four_groups.csv')
    p.add_argument('--lens',default=f'{root}/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt')
    p.add_argument('--output',default=f'{root}/351_all/351_stage4_readout.jsonl')
    p.add_argument('--n',type=int,default=4)
    p.add_argument('--seed',type=int,default=3514)
    p.add_argument('--layers',default='16,24,32,40,48,56,62')
    p.add_argument('--gpu-layers',type=int,default=29)
    p.add_argument('--max-name-tokens',type=int,default=16)
    p.add_argument('--max-seq-len',type=int,default=512)
    p.add_argument('--plan-only',action='store_true')
    p.add_argument('--report-only',action='store_true',help='Regenerate summaries, figures and report from saved JSONL; no GPU needed')
    p.add_argument('--report-dir',default=None,help='Artifact directory (default sibling 351_stage4_artifacts)')
    p.add_argument('--tokenizer-check',action='store_true',help='CPU-only check of author tokenizer alignment before GPU allocation')
    args=p.parse_args()
    if args.n<1 or args.n>50:p.error('Benchmark --n must be 1..50')
    layers=[int(x) for x in args.layers.split(',')]
    if not layers or len(set(layers))!=len(layers) or not all(0<=x<=62 for x in layers):p.error('distinct layers must be 0..62')
    if not 1<=args.gpu_layers<=63:p.error('gpu-layers must be 1..63')
    quotas={'A':8,'B':8,'C':3,'D':1} if args.n<=20 else {'A':20,'B':20,'C':7,'D':3}
    with open(args.data,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    selection=select(rows,args.seed,quotas)[:args.n]
    print('STAGE4 plan:',len(selection),'papers; sampled group counts:',dict(collections.Counter(r['group_351'] for r in selection)),flush=True)
    for r in selection:print(r['group_351'],r['paper_id'][:12],r['citation_bin'],'authors=',len(unique_names(r)),r['title'][:70],flush=True)
    if args.plan_only:return
    if args.tokenizer_check:
        import transformers
        tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV)
        reasons=collections.Counter();total=0;valid=0
        for r in selection:
            prompt=PROMPT.format(title=r['title'],year=r['year'])
            for author in unique_names(r):
                total+=1
                plan,reason=token_plan(tok,prompt,author,args.max_name_tokens)
                if plan is not None:valid+=1
                else:reasons[reason]+=1
        print('TOKENIZER CHECK (forced token-ID continuation):',valid,'/',total,'valid; skipped by reason:',dict(reasons),flush=True)
        if valid==0:raise RuntimeError('Zero tokenizable names; inspect input names and tokenizer')
        return
    import torch,transformers,jlens
    if not torch.cuda.is_available():raise RuntimeError('CUDA allocation required')
    config={'protocol':'stage4_multi_gold_first_and_teacher_forcing_v4_forced_token_ids','model':MODEL,'revision':REV,'data_sha':hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),'lens':str(Path(args.lens).resolve()),'seed':args.seed,'layers':layers,'max_name_tokens':args.max_name_tokens,'max_seq_len':args.max_seq_len,'tokenization':'encode(prompt) + encode(ASCII_SPACE + name); forced suffix IDs; no joint retokenization','prompt_template':PROMPT,'name_prefix':'ASCII space','sampling':'fixed seeded 20-paper plan 8A8B3C1D, prefix --n <=20; 50-plan for >20','scores':'primary first-listed author first token RR at beginning-of-list; exploratory all-authors paper weighted; teacher forced token MRR separate'}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    completed={}
    if out.exists():
        for s in out.read_text().splitlines():
            if not s.strip():continue
            r=json.loads(s)
            if r['config']!=config:raise RuntimeError('Resume configuration mismatch. Change --output.')
            if r['paper_id'] in completed:raise RuntimeError('Duplicate paper')
            completed[r['paper_id']]=r
    report_dir=Path(args.report_dir) if args.report_dir else out.parent/'351_stage4_artifacts'
    if args.report_only:
        generate_artifacts(out,selection,layers,report_dir,config,args);return
    if all(r['paper_id'] in completed for r in selection):
        summarize(out,layers,selection);generate_artifacts(out,selection,layers,report_dir,config,args);return
    print('Loading public lens...',flush=True)
    lens=jlens.JacobianLens.load(args.lens)
    if lens.d_model!=5120 or not set(layers).issubset(set(lens.source_layers)):raise RuntimeError('Invalid lens dimensions')
    tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=REV)
    dm={'model.embed_tokens':0,'model.norm':0,'model.rotary_emb':0,'lm_head':0}
    dm.update({f'model.layers.{i}':(0 if i<args.gpu_layers else 'cpu') for i in range(64)})
    print('Loading BF16 32B with',args.gpu_layers,'blocks GPU and',64-args.gpu_layers,'CPU',flush=True)
    hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.bfloat16,device_map=dm,low_cpu_mem_usage=True).eval()
    model=jlens.from_hf(hf,tok)
    for idx,r in enumerate(selection,1):
        pid=r['paper_id']
        if pid in completed:print('SKIP',idx,pid[:12],flush=True);continue
        t0=time.perf_counter();torch.cuda.reset_peak_memory_stats()
        prompt=PROMPT.format(title=r['title'],year=r['year'])
        authors_scored=[];authors_skipped=[];cache={}
        # Freeze the entire prompt as token IDs; do not retokenize at the boundary.
        prompt_ids=model.encode(prompt,max_length=args.max_seq_len).reshape(-1).tolist()
        if len(prompt_ids)>=args.max_seq_len:
            raise ValueError(f'Base prompt exceeds max_seq_len, paper={pid}')
        for author in unique_names(r):
            plan,reason=token_plan(tok,prompt,author,args.max_name_tokens)
            if plan is None:
                authors_skipped.append({'name':author,'reason':reason});continue
            bymode=defaultdict(list)
            for name_prefix,target in plan['contexts']:
                prefix_ids=prompt_ids+list(name_prefix)
                if len(prefix_ids)>args.max_seq_len:
                    raise ValueError(f'Context exceeds max_seq_len, paper={pid}, author={author}')
                key=tuple(name_prefix)
                if key not in cache:
                    j,final,v=apply_on_ids(lens,model,prompt,prefix_ids,layers,args.max_seq_len,torch)
                    cache[key]={'final':final[-1].cpu(),**{f'jlens_L{l}':j[l][-1].cpu() for l in layers},**{f'vanilla_L{l}':v[l][-1].cpu() for l in layers}}
                for mode,vec in cache[key].items():bymode[mode].append(measure(vec,target))
            scores={}
            for mode,items in bymode.items():
                scores[mode]={'tokens':items,'first_rank':items[0]['rank'],'first_rr':1/items[0]['rank'],'conditional_token_mrr':statistics.mean(1/z['rank'] for z in items),'conditional_mean_logprob':statistics.mean(z['logprob'] for z in items),'conditional_sum_logprob':sum(z['logprob'] for z in items),'n_tokens':len(items)}
            authors_scored.append({'name':author,'token_ids':plan['token_ids'],'name_tokenization':'independent_leading_space','measurements':scores})
        rec={'paper_id':pid,'group':r['group_351'],'citation_bin':r['citation_bin'],'field':r['field'],'year':r['year'],'title':r['title'],'prompt':prompt,'prompt_token_ids':prompt_ids,'n_authors_raw':len(unique_names(r)),'first_listed_gold_author':unique_names(r)[0],'authors_scored':authors_scored,'authors_skipped':authors_skipped,'seconds':round(time.perf_counter()-t0,2),'peak_gpu_gib':round(torch.cuda.max_memory_allocated()/1024**3,2),'config':config}
        with out.open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        completed[pid]=rec
        print(f'{idx}/{len(selection)} {r["group_351"]} {pid[:10]} authors={len(authors_scored)}/{len(unique_names(r))} t={rec["seconds"]}s gpu={rec["peak_gpu_gib"]}GiB',flush=True)
        cache.clear()
        if idx % 4 == 0:
            generate_artifacts(out,selection,layers,report_dir,config,args)
    summarize(out,layers,selection)
    generate_artifacts(out,selection,layers,report_dir,config,args)
    print('Saved:',out,flush=True)
if __name__=='__main__':main()
