#!/usr/bin/env python3
"""Audit saved Stage 4 results, without loading model/GPU. Does not overwrite input."""
import argparse,csv,json,math,random,statistics,collections,datetime,hashlib
from pathlib import Path

def read(path):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def num(s):
    try:
        x=float(s);return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None
def savecsv(p,rows,cols):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def ci(v,w=None,seed=3514):
    if len(v)<2 or w is not None and len(w)<2:return None,None
    rng=random.Random(seed);z=[]
    for _ in range(3000):
        a=statistics.mean(rng.choices(v,k=len(v)))
        z.append(a if w is None else a-statistics.mean(rng.choices(w,k=len(w))))
    z.sort();return z[74],z[2924]
def f(x):return 'N/A' if x is None else f'{x:.6g}'
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',default=None);p.add_argument('--cohort',default=None)
    a=p.parse_args()
    import os
    root=Path(a.root or f'/scratch/{os.environ["USER"]}/jlens/351_all/351_stage4_artifacts')
    source=root/'summary/paper_metrics.csv';raw=root/'raw/results.jsonl'
    if not source.exists() or not raw.exists():raise SystemExit('Missing saved input CSV/JSONL; no results will be invented')
    rs=read(source);papers=[json.loads(s) for s in raw.read_text(encoding='utf-8').splitlines() if s.strip()]
    ids=[x['paper_id'] for x in papers]
    if len(ids)!=len(set(ids)):raise SystemExit('Duplicate paper IDs')
    expected=len(ids)*15
    if len(rs)!=expected:raise SystemExit(f'Expected {expected} paper mode/layer rows, observed {len(rs)}')
    keys=[(r['paper_id'],r['mode'],r['layer']) for r in rs]
    if len(keys)!=len(set(keys)):raise SystemExit('Duplicated paper/mode/layer')
    if set(r['paper_id'] for r in rs)!=set(ids):raise SystemExit('IDs inconsistent between raw and summary')
    groups=collections.Counter(x['group'] for x in papers)
    out=root/'audit';fig=out/'figures';fig.mkdir(parents=True,exist_ok=True)
    metrics=['first_listed_first_rr','conditional_token_mrr','all_author_first_rr']
    layers=[16,24,32,40,48,56,62]
    dist=[];contrast=[];ranks=[];paired=[]
    for r in rs:
        x=num(r['first_listed_first_rr'])
        if x is not None:
            if not 0<x<=1:raise SystemExit('RR outside (0,1]')
            ranks.append(dict(paper_id=r['paper_id'],group=r['group'],mode=r['mode'],layer=r['layer'],rr=x,implied_rank=round(1/x)))
    for metric in metrics:
        for mode in ['jlens','vanilla']:
            for layer in layers:
                sub=[r for r in rs if r['mode']==mode and int(r['layer'])==layer]
                for group in ['ALL','A','B','C','D']:
                    vals=[num(r[metric]) for r in sub if group=='ALL' or r['group']==group]
                    vals=[v for v in vals if v is not None]
                    lo,hi=ci(vals,seed=3514+layer+sum(map(ord,metric+mode+group)))
                    dist.append(dict(metric=metric,mode=mode,layer=layer,group=group,n=len(vals),mean=statistics.mean(vals) if vals else None,median=statistics.median(vals) if vals else None,max_share=max(vals)/sum(vals) if vals and sum(vals)>0 else None,without_max_mean=statistics.mean(sorted(vals)[:-1]) if len(vals)>1 else None,ci95_low=lo,ci95_high=hi))
                A=[num(r[metric]) for r in sub if r['group']=='A'];B=[num(r[metric]) for r in sub if r['group']=='B']
                A=[x for x in A if x is not None];B=[x for x in B if x is not None]
                lo,hi=ci(A,B,seed=3514+layer+sum(map(ord,metric+mode)))
                contrast.append(dict(metric=metric,mode=mode,layer=layer,n_A=len(A),n_B=len(B),mean_A=statistics.mean(A) if A else None,mean_B=statistics.mean(B) if B else None,A_minus_B=statistics.mean(A)-statistics.mean(B) if A and B else None,ci95_low=lo,ci95_high=hi,matching='UNMATCHED exploratory'))
    lookup={(r['paper_id'],r['mode'],int(r['layer'])):r for r in rs}
    for p0 in papers:
        for layer in layers:
            j=lookup[(p0['paper_id'],'jlens',layer)];v=lookup[(p0['paper_id'],'vanilla',layer)]
            d=dict(paper_id=p0['paper_id'],group=p0['group'],layer=layer)
            for metric in metrics:
                x=num(j[metric]);y=num(v[metric]);d[metric+'_jlens_minus_vanilla']=x-y if x is not None and y is not None else None
            paired.append(d)
    savecsv(out/'paper_first_token_ranks.csv',ranks,['paper_id','group','mode','layer','rr','implied_rank'])
    savecsv(out/'distribution_and_ci.csv',dist,list(dist[0]))
    savecsv(out/'ab_unmatched_bootstrap.csv',contrast,list(contrast[0]))
    savecsv(out/'paired_jlens_vanilla.csv',paired,list(paired[0]))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    def chart(name,plot):
        fi,ax=plt.subplots(figsize=(9,5));plot(ax);fi.tight_layout()
        fi.savefig(fig/(name+'.png'),dpi=180);fi.savefig(fig/(name+'.pdf'));plt.close(fi)
    def rankplot(ax):
        for mode in ['jlens','vanilla']:
            xx=[int(r['layer'])+(-1 if mode=='jlens' else 1) for r in ranks if r['mode']==mode and int(r['layer'])!=63]
            yy=[r['implied_rank'] for r in ranks if r['mode']==mode and int(r['layer'])!=63]
            ax.scatter(xx,yy,label=mode,alpha=.5,s=18)
        ax.set_yscale('log');ax.set(xlabel='Source layer',ylabel='Individual first-author token rank (log)',title='Stage 4: 20-paper rank distribution');ax.legend()
    chart('paper_rank_distribution',rankplot)
    def curves(ax,metric,groups0,mode0):
        for group in groups0:
            v=[r for r in dist if r['metric']==metric and r['group']==group and r['mode']==mode0]
            ax.plot([r['layer'] for r in v],[r['mean'] for r in v],marker='o',label=group)
        ax.set(xlabel='Layer',ylabel=metric,title=f'{mode0}: {metric} (descriptive)');ax.legend();ax.grid(alpha=.2)
    chart('ab_first_token_unmatched',lambda ax:curves(ax,'first_listed_first_rr',['A','B'],'jlens'))
    def traj(ax):
        for mode in ['jlens','vanilla']:
            for metric,style in [('first_listed_first_rr','-'),('conditional_token_mrr','--')]:
                v=[r for r in dist if r['metric']==metric and r['group']=='ALL' and r['mode']==mode]
                ax.plot([r['layer'] for r in v],[r['mean'] for r in v],marker='o',linestyle=style,label=f'{mode} {metric}')
        ax.legend(fontsize=7);ax.grid(alpha=.2);ax.set(xlabel='Layer',ylabel='Paper-mean RR/MRR',title='Unconditional vs teacher-forced trajectories')
    chart('first_vs_teacher_forced',traj)
    def influence(ax):
        for mode in ['jlens','vanilla']:
            v=[r for r in dist if r['metric']=='first_listed_first_rr' and r['group']=='ALL' and r['mode']==mode]
            ax.plot([r['layer'] for r in v],[r['max_share'] for r in v],marker='o',label=mode)
        ax.set(xlabel='Layer',ylabel='Largest paper share of sum',ylim=(0,1.05),title='Outlier influence on mean');ax.legend();ax.grid(alpha=.2)
    chart('outlier_contribution',influence)
    protocol={
       'status':'PROPOSED; controls and matching NOT YET RUN',
       'primary':'first-listed gold author first-token RR, Authors: position, per layer',
       'primary_weighting':'one paper one weight, A/B matched pair-bootstrap after pairing',
       'auxiliary':['paper-mean all gold-author first-token RR; list-start order confound', 'teacher-forced full-name token MRR; not free recall','within-paper J-Lens minus Vanilla'],
       'layers':layers,'prompt_and_token_ids':'reuse exact Stage4 frozen run_config and forced token IDs',
       'matching':'one-to-one A/B; citation_bin and field exact where possible, then year and n_authors near; record balance; no silent fallback',
       'control_plan':['matched-false author with similar name-token length','shuffled title-year while preserving gold author','unrelated-title/name-prior baseline','Vanilla Lens (existing)','final model (existing)'],
       'control_status':'matched-false, shuffled-title, name-prior NOT RUN',
       'inference':'matched pair bootstrap; prespecify layer or adjust multiple comparisons',
       'scope':'Stage4 n=20 exploration, no confirmatory claims'}
    (out/'stage5_protocol_candidate.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    feasibility='Not checked (provide --cohort file to inspect candidate strata)'
    if a.cohort:
        cohort=read(a.cohort);counts=collections.Counter((r.get('group_351') or r.get('group'),r.get('citation_bin'),r.get('field')) for r in cohort)
        n=sum(min(k,counts.get(('B',b,c),0)) for (g,b,c),k in counts.items() if g=='A')
        feasibility=f'Max theoretical A/B same citation_bin+field candidates before additional restrictions: {n}. Not an executed matching.'
    groupstr=', '.join(f'{k}={groups[k]}' for k in ('A','B','C','D'))
    report=['# Stage 4 Result Audit','',f'Input: {source}',f'Papers: {len(papers)} ({groupstr}); paper/mode/layer rows: {len(rs)}; raw author skips: {sum(len(p.get("authors_skipped",[])) for p in papers)}.',
      '', '## First-listed first-token rank & outlier check',
      '|Layer|Mean J-Lens|Median|Largest-paper share|Leave-top-one-out mean|','|---|---:|---:|---:|---:|']
    for r in (r for r in dist if r['metric']=='first_listed_first_rr' and r['mode']=='jlens' and r['group']=='ALL'):
        report.append(f'|L{r["layer"]}|{f(r["mean"])}|{f(r["median"])}|{f(r["max_share"])}|{f(r["without_max_mean"])}|')
    report+=['','The largest-paper share diagnoses dominance by an extreme rank. No data were dropped.',
      '', '## A/B descriptive comparison (NOT MATCHED)',
      '|Layer|A mean|B mean|A-B|95% paper-bootstrap CI|','|---|---:|---:|---:|---:|']
    for r in (r for r in contrast if r['metric']=='first_listed_first_rr' and r['mode']=='jlens'):
        report.append(f'|L{r["layer"]}|{f(r["mean_A"])}|{f(r["mean_B"])}|{f(r["A_minus_B"])}|[{f(r["ci95_low"])}, {f(r["ci95_high"])}]|')
    report+=['','These CIs resample A and B papers independently; they are NOT matched-pair or causal estimates.',
      '', '## First-token versus full-name teacher forcing',
      'See `figures/first_vs_teacher_forced.png`; the second endpoint conditions on preceding gold-name tokens and does not measure unassisted recall.',
      '', '## Artifacts and integrity',f'Original JSONL and {len(rs)} paper-level rows checked; audit figures are regenerated from saved records without GPU.',
      'Saved additional numerical CSV tables, plots in PNG+PDF, and a protocol candidate JSON.',
      '', '## Stage 5 protocol (CANDIDATE, not scientifically validated)',
      'Primary: first-listed author first-token reciprocal rank, paper-level equal weight.',
      'Auxiliary: all-author first-token RR and teacher-forced full-name MRR, explicitly separate.',
      'Required: exact citation-bin + field matched A/B where feasible; nearest year and author count; no silent relaxation.',
      f'Matching feasibility: {feasibility}',
      'Negative controls: matched false authors, title shuffle, and unrelated-title name-prior. These have **NOT RUN**.',
      'A future matched-pair bootstrap and multiplicity policy are required before inferential conclusions.',
      '', '## Conclusion',
      'Stage4 demonstrated end-to-end execution and saved outputs. It cannot by itself establish internal gold-author knowledge or an A>B accessibility difference.',
      'Plots are descriptions of the existing 20-paper pilot, not independent validation of J-Lens fidelity.']
    (out/'audit_report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    (out/'audit_manifest.json').write_text(json.dumps({'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'papers':len(papers),'rows':len(rs),'csv_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    print('AUDIT SUCCESS',out,'papers=',len(papers),'groups=',groupstr,'figures=4 x PNG/PDF')
if __name__=='__main__':main()
