"""Exploratory, read-only (2026-11-14): share of R0-labelled papers for which our plain F0 prompt
writes >= 1 correct author, by group, with author-team cluster bootstrap 95% CI; and whether the
correct author written is the first author or a co-author. Uses whatever B parsed shards exist."""
import pandas as pd, numpy as np, glob, json, sys
G='/scratch/zhang.zhiqi2/jlens/391_groups/'
fs=sorted(glob.glob(G+'raw/a16_B/parsed/shard_*.parquet'))
d=pd.concat([pd.read_parquet(f) for f in fs]); d=d[d.cond=='F0'].copy()
s=pd.read_parquet(G+'config/prereg16_sample_B.parquet')[['paper_id','team']]
d=d.merge(s,on='paper_id',how='left')
d['any']=d.any_full|d.any_sur  # primary: any author full-name or surname match
d['first']=d.first_full|d.first_sur
d['co_only']=d['any']&~d['first']
d['c_any']=d.c_any_full|d.c_any_sur
rng=np.random.default_rng(13); out=[]
for g,x in list(d.groupby('grp'))+[('all',d)]:
    teams=x.team.unique(); byt={t:x[x.team==t] for t in teams}
    row=dict(group=g,n_papers=len(x),n_teams=len(teams))
    for c in ['any','first','co_only','c_any']:
        row[c]=x[c].mean()
        bs=[]
        for _ in range(2000):
            xx=pd.concat([byt[t] for t in rng.choice(teams,len(teams))]); bs.append(xx[c].mean())
        row[c+'_lo'],row[c+'_hi']=np.percentile(bs,[2.5,97.5])
    out.append(row)
r=pd.DataFrame(out); r.to_csv(G+'summary_r0_prompt_20261114/r0_prompt_by_group.csv',index=False)
json.dump(dict(shards=[f.split('/')[-1] for f in fs],note='F0 only; any=full or surname match of any true author; first=true first author matched anywhere; co_only=only co-authors; c_any=same metric against chance control paper'),open(G+'summary_r0_prompt_20261114/meta.json','w'),indent=1)
print(r.round(3).to_string())
