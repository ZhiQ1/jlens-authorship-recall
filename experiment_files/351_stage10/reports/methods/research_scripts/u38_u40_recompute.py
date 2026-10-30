"""U38/U40 recompute (CPU, read-only). P1 recovery by token role, same estimator as stage12_analyze.py:46-58
(ratio of means over paper-averaged rows, recovery=(nlr_patch-nlr_none)/(nlr_true-nlr_none)); and P2 hook sanity."""
import numpy as np, pandas as pd, sys, glob
sys.path.insert(0,'/home/zhang.zhiqi2/jlens_work/12_stage12')
from pathlib import Path
R=Path('/scratch/zhang.zhiqi2/jlens/371_stage12')
def load(d):
    zs=[np.load(f,allow_pickle=True) for f in sorted(Path(d).glob('shard_*.npz'))]
    return {k:(np.concatenate([z[k] for z in zs]) if zs[0][k].ndim and k not in('layers','items','comps') else zs[0][k]) for k in zs[0].files if k!='meta'}
nlr=lambda r:-np.log10(np.asarray(r,float))
tok=pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/name_tokens.parquet',columns=['row_id','paper_id','role']).set_index('row_id')
d=load(R/'raw/patch_pos'); items=list(d['items']); layers=list(d['layers'])
pid=tok.loc[d['row_id']].paper_id.to_numpy(); role=tok.loc[d['row_id']].role.to_numpy()
nt=nlr(d['rank_true']); P=nlr(d['rank_patch']); none=P[:,:,items.index('none')]; valid=d['valid']
print('P1 rows',len(nt),'items',items,'layers',layers)
out=[]
for rl in ['ALL','initial_first','given_first','surname_first','surname_cont','given_cont','punct']:
    m=np.ones(len(nt),bool) if rl=='ALL' else role==rl
    for l in [48,52]:
        li=layers.index(l)
        for it in ['p1','names','all']:
            ii=items.index(it); ok=m&valid[:,ii]
            df=pd.DataFrame({'p':pid[ok],'num':(P[:,li,ii]-none[:,li])[ok],'den':(nt-none[:,li])[ok]}).groupby('p').mean()
            out.append(dict(role=rl,layer=l,item=it,n_rows=int(ok.sum()),n_papers=len(df),recovery=round(df.num.mean()/df.den.mean(),3),gap=round(df.den.mean(),3)))
o=pd.DataFrame(out); print(o.pivot_table(index=['role','item'],columns='layer',values='recovery').to_string())
print(o[o.item=='p1'][['role','layer','n_rows','gap']].to_string())
# U40: P2 hook sanity
c=load(R/'raw/patch_comp'); comps=list(c['comps']); Pc=c['rank_patch']; base=Pc[:,comps.index('none')]
print('P2 rows',len(base))
for ci,cn in enumerate(comps):
    if cn=='none':continue
    print(cn,'frac rows rank!=none %.3f'%(Pc[:,ci]!=base).mean(), 'mean dnlr %.4f'%(nlr(Pc[:,ci])-nlr(base)).mean())
s11=load('/scratch/zhang.zhiqi2/jlens/361_stage11/raw/patch')
mp=pd.Series(s11['rank_false'],index=s11['row_id']); mt=pd.Series(s11['rank_true'],index=s11['row_id'])
common=np.isin(c['row_id'],s11['row_id'])
print('P2 rows also in Stage11 E1:',common.sum(),'none==S11 rank_false:',(base[common]==mp.loc[c['row_id'][common]].to_numpy()).mean(),'rank_true==S11 rank_true:',(c['rank_true'][common]==mt.loc[c['row_id'][common]].to_numpy()).mean())
pp_none=load(R/'raw/patch_pos')
rf=mp.loc[c['row_id']].to_numpy()
dd=nlr(base)-nlr(rf); print('P2 none vs S11 rank_false: mean dnlr %.4f, median |dnlr| %.4f, p99 |dnlr| %.3f, rank ratio within 2x: %.3f'%(dd.mean(),np.median(abs(dd)),np.percentile(abs(dd),99),(abs(dd)<=np.log10(2)).mean()))
pn=d['rank_patch'][:,:,items.index('none')]; rf1=mp.loc[d['row_id']].to_numpy()
print('P1 none (L48 col) == S11 rank_false: %.3f; none identical across P1 layers: %.3f'%((pn[:,layers.index(48)]==rf1).mean(), (pn==pn[:,[0]]).all(1).mean()))
print('P1 none vs P2 none equal: %.3f'%(pn[:,0]==base).mean() if np.array_equal(d['row_id'],c['row_id']) else 'row order differs')
s11t=nlr(c['rank_true']); gap=(s11t-nlr(rf)).mean(); print('mean gap true-false (S11) %.3f'%gap)
