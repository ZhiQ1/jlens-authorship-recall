#!/usr/bin/env python3
"""Stage 8D supplement (CPU only): the endpoints named in the FROZEN Stage 8A analysis plan
(config/analysis_plan.json) that 351_stage8D.py did not compute.

Frozen primary endpoint (analysis_plan.json): paper-level mean over the 7 fixed layers of the
true-title minus mean-20-wrong-title Gold Win Rate, J-Lens readout; primary group test = matched
A-B on that integrated value (pair bootstrap). L56 is listed there as a secondary,
pilot-selected endpoint. 351_stage8D.py reports L56 as primary; this script adds the integrated
values so both are visible. It reads only saved 8D summaries, never raw scores or the GPU, and
writes to a NEW directory (stage8D_supplement/); frozen 8D outputs are not modified.
"""
import argparse,csv,hashlib,json,os
from pathlib import Path
import numpy as np

LAYERS=[16,24,32,40,48,56,62]
SEED=3518501
NBOOT=10000

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def readcsv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def bootstrap(v,seed):
    a=np.asarray(v,dtype=float)
    if not len(a) or not np.isfinite(a).all():raise ValueError('invalid values')
    rng=np.random.default_rng(seed)
    s=np.empty(NBOOT)
    for i in range(0,NBOOT,500):
        n=min(500,NBOOT-i)
        s[i:i+n]=a[rng.integers(0,len(a),(n,len(a)))].mean(axis=1)
    return dict(n=len(a),mean=float(a.mean()),median=float(np.median(a)),
                ci_low=float(np.quantile(s,.025)),ci_high=float(np.quantile(s,.975)),
                positive=int((a>0).sum()),negative=int((a<0).sum()),zero=int((a==0).sum()))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path('/scratch')/os.getenv('USER','unknown')/'jlens/351_stage8')
    a=ap.parse_args();root=a.root
    pla=root/'stage8D/summary/paper_layer_advantage.csv'
    prs=root/'matching/stage8_ab_pairs.csv'
    adv={}
    for r in readcsv(pla):adv[(r['paper_id'],r['mode'])]=float(r['title_advantage'])
    pairs=readcsv(prs)
    papers=sorted({p for p,_ in adv})
    if len(papers)!=200 or len(pairs)!=100:raise RuntimeError('unexpected cohort size')
    def integ(pid,kind):return float(np.mean([adv[(pid,f'{kind}_L{l}')] for l in LAYERS]))
    rows=[]
    for kind in ('jlens','vanilla'):
        rows.append(dict(endpoint=f'{kind}_integrated7_RQ1_paper_mean',**bootstrap([integ(p,kind) for p in papers],SEED+(0 if kind=='jlens' else 10))))
        rows.append(dict(endpoint=f'{kind}_integrated7_matched_A_minus_B',**bootstrap([integ(x['A_id'],kind)-integ(x['B_id'],kind) for x in pairs],SEED+(1 if kind=='jlens' else 11))))
    rows.append(dict(endpoint='jlens_minus_vanilla_integrated7_paper',**bootstrap([integ(p,'jlens')-integ(p,'vanilla') for p in papers],SEED+2)))
    for i,l in enumerate(LAYERS):  # descriptive per-layer A-B, J-Lens, unadjusted
        rows.append(dict(endpoint=f'jlens_L{l}_matched_A_minus_B_descriptive',**bootstrap([adv[(x['A_id'],f'jlens_L{l}')]-adv[(x['B_id'],f'jlens_L{l}')] for x in pairs],SEED+100+i)))
    out=root/'stage8D_supplement';out.mkdir(parents=True,exist_ok=True)
    with open(out/'frozen_plan_endpoints.csv','w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'supplement_manifest.json').write_text(json.dumps({'seed':SEED,'nboot':NBOOT,'inputs':{'paper_layer_advantage.csv':sha(pla),'stage8_ab_pairs.csv':sha(prs)},'note':'CPU-only; unadjusted CIs; per-layer rows are descriptive and not Holm-adjusted'},indent=2,sort_keys=True)+'\n',encoding='utf-8')
    for r in rows:print(f"{r['endpoint']:55s} mean={r['mean']:+.6f} CI=[{r['ci_low']:+.6f},{r['ci_high']:+.6f}] pos={r['positive']}/{r['n']}")
if __name__=='__main__':main()
