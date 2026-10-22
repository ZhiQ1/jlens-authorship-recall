#!/usr/bin/env python3
"""Stage 7.4 CPU-only, read-only cross-stage audit. --source points to unpacked experiment parent."""
import argparse, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

LAYERS=[16,24,32,40,48,56,62]
def ci(v,seed=741,n=20000):
    v=np.asarray(v,dtype=float);v=v[np.isfinite(v)]
    if not len(v):return (np.nan,np.nan)
    rng=np.random.default_rng(seed);means=np.empty(n)
    for k in range(n):means[k]=v[rng.integers(len(v),size=len(v))].mean()
    return tuple(np.quantile(means,[.025,.975]))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',default='/scratch/'+__import__('os').environ.get('USER','')+'/jlens');ap.add_argument('--out',default=None);a=ap.parse_args()
    src=Path(a.source);out=Path(a.out or (src/'351_stage7_4'));(out/'summary').mkdir(parents=True,exist_ok=True);(out/'figures').mkdir(exist_ok=True);(out/'reports').mkdir(exist_ok=True)
    def read(sub):
        p=src/sub
        if not p.is_file():raise FileNotFoundError(str(p))
        return pd.read_csv(p)
    s5=read('351_stage5_crossed_v2/summary/paper_layer_contrasts.csv')
    s6=read('351_stage6/summary/paper_integrated.csv')
    s72=read('351_stage7_2/summary/paper_layer_pool.csv')
    s73=read('351_stage7_3/summary/paper_null_distribution.csv')
    ctx=read('351_stage7_3/summary/shuffle_context_pool.csv')
    pairs=read('351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv')
    cohort=read('351_stage5_crossed_v2/cohort/pilot50_v1.csv')
    assert len(cohort)==50 and len(pairs)==20 and cohort.paper_id.nunique()==50
    assert len(ctx[ctx.pool=='combined'])==50*20*15 and (s73.n_null==20).all(), 'Missing shuffle contexts'
    # recompute title advantage independently from per-context null win
    raw=ctx.groupby(['paper_id','mode','pool'],as_index=False).agg(true_win=('true_win','first'),null_mean=('null_win','mean'),n_null=('null_win','size'))
    raw['adv_recalc']=raw.true_win-raw.null_mean
    chk=raw.merge(s73[['paper_id','mode','pool','title_advantage']],on=['paper_id','mode','pool'],validate='one_to_one')
    assert np.allclose(chk.adv_recalc,chk.title_advantage,atol=1e-9)
    assert len(s5[s5['mode']=='jlens'])==350
    # Stage 5/7.3 same-paper association by mode/layer, and only all-papers and L56
    joined=s5.rename(columns={'mode':'lens','title_specific_advantage':'stage5_margin'}).merge(
       s73[s73.pool=='combined'].assign(lens=lambda d:d['mode'].str.split('_L').str[0],layer=lambda d:d['mode'].str.split('_L').str[-1].astype(int))
       [['paper_id','lens','layer','title_advantage','null_mean','true_win','null_percentile_midrank','empirical_tail_fraction','advantage_no_source_false_overlap']],
       on=['paper_id','lens','layer'],validate='one_to_one')
    joined.to_csv(out/'summary'/'cross_stage_paper_layer.csv',index=False)
    consistency=[]
    for (lens,L),g in joined.groupby(['lens','layer']):
        x=g.stage5_margin.to_numpy();y=g.title_advantage.to_numpy()
        from scipy.stats import spearmanr,pearsonr
        consistency.append(dict(lens=lens,layer=L,n=len(g),pearson=float(pearsonr(x,y).statistic),spearman=float(spearmanr(x,y).statistic),same_sign_rate=float(np.mean(np.sign(x)==np.sign(y))),stage5_positive=int((x>0).sum()),stage73_positive=int((y>0).sum())))
    pd.DataFrame(consistency).sort_values(['lens','layer']).to_csv(out/'summary'/'cross_stage_correlations.csv',index=False)
    # paired jlens minus vanilla within same paper: primary paired unit paper
    lwide=s73[s73.pool=='combined'].copy();lwide['lens']=lwide['mode'].str.split('_L').str[0];lwide['layer']=lwide['mode'].str.split('_L').str[-1].astype(int)
    wide=lwide.pivot(index=['paper_id','group','citation_bin','layer'],columns='lens',values='title_advantage').reset_index()
    wide['jlens_minus_vanilla']=wide.jlens-wide.vanilla
    wide.to_csv(out/'summary'/'jlens_vs_vanilla_paper_layer.csv',index=False)
    comparisons=[]
    for L,g in list(wide.groupby('layer'))+ [('integrated',wide.groupby(['paper_id','group'],as_index=False).agg(jlens_minus_vanilla=('jlens_minus_vanilla','mean')))]:
        v=g.jlens_minus_vanilla.to_numpy();lo,hi=ci(v)
        comparisons.append(dict(layer=L,n_papers=len(v),mean=float(v.mean()),median=float(np.median(v)),positive=int((v>0).sum()),ci_low=lo,ci_high=hi,leave_one_out_min=float(min(np.delete(v,i).mean() for i in range(len(v)))),leave_one_out_max=float(max(np.delete(v,i).mean() for i in range(len(v))))))
    pd.DataFrame(comparisons).to_csv(out/'summary'/'jlens_increment_bootstrap.csv',index=False)
    # matched AB conditional: pair level directly, no repeated layer pseudoreplication
    diff=wide.pivot(index='paper_id',columns='layer',values='jlens_minus_vanilla');diff['integrated']=diff[LAYERS].mean(axis=1)
    p=pairs[['pair_id','A_id','B_id']].copy()
    for key in [*LAYERS,'integrated']:
        p[str(key)+'_AminusB_lens_increment']=p.A_id.map(diff[key])-p.B_id.map(diff[key])
    p.to_csv(out/'summary'/'matched_lens_increment_pairs.csv',index=False)
    vals=p['integrated_AminusB_lens_increment'].to_numpy();abci=ci(vals)
    # 50-papers high bins display clearly exploratory 129+
    floor=lwide[(lwide.lens=='jlens')&(lwide.layer==56)].merge(cohort[['paper_id','title']],on='paper_id',how='left')
    floor['range']=np.select([floor.citation_bin=='0-2',floor.citation_bin.isin(['129-256','129-256','129-256'])],['0-2','129+'],default='other')
    # do not infer '129+' from literal tokens; parse bin left bound
    floor['bin_lo']=floor.citation_bin.astype(str).str.split('-').str[0].str.replace(',','').astype(int)
    floor['range']=np.where(floor.bin_lo<=2,'0-2',np.where(floor.bin_lo>=129,'129+','3-128'))
    floor.to_csv(out/'summary'/'floor_L56_all_papers.csv',index=False)
    low=floor[floor.range=='0-2'].copy();assert len(low)==6
    low.to_csv(out/'summary'/'floor_L56_low_six.csv',index=False)
    highcmp=floor.groupby(['range','lens'],as_index=False).agg(n=('paper_id','size'),true_mean=('true_win','mean'),null_mean=('null_mean','mean'),adv_mean=('title_advantage','mean'),positive=('title_advantage',lambda s:int((s>0).sum())),pct90=('null_percentile_midrank',lambda s:int((s>=.9).sum())),tail05=('empirical_tail_fraction',lambda s:int((s<=.05).sum())))
    highcmp.to_csv(out/'summary'/'floor_L56_ranges.csv',index=False)
    # context overlap sensitivity
    t=ctx[ctx.pool=='combined'].copy()
    stability=t.groupby(['paper_id','mode'],as_index=False).agg(n=('null_win','size'),overall_null=('null_win','mean'),clean_n=('source_author_in_false_pool',lambda s:int((s==0).sum())))
    clean=t[t.source_author_in_false_pool==0].groupby(['paper_id','mode'],as_index=False).agg(clean_null=('null_win','mean'))
    stability=stability.merge(clean,on=['paper_id','mode']);stability['null_shift']=stability.clean_null-stability.overall_null
    stability.to_csv(out/'summary'/'overlap_sensitivity.csv',index=False)
    # figure
    cor=pd.DataFrame(consistency).query("lens == 'jlens'").sort_values('layer')
    fig,ax=plt.subplots(figsize=(8,4.5));ax.plot(cor.layer,cor.pearson,'o-',label='Pearson');ax.plot(cor.layer,cor.spearman,'s-',label='Spearman');ax.axhline(0,color='gray',lw=.8);ax.set(xlabel='Layer',ylabel='Within-paper correlation',title='Stage 5 margin vs Stage 7.3 title advantage');ax.legend();fig.tight_layout();fig.savefig(out/'figures'/'stage5_stage73_correlations.png',dpi=170);fig.savefig(out/'figures'/'stage5_stage73_correlations.pdf');plt.close(fig)
    ci_df=pd.DataFrame(comparisons);seven=ci_df[ci_df.layer.astype(str)!='integrated'];fig,ax=plt.subplots(figsize=(8,4.5));ax.errorbar(seven.layer.astype(int),seven['mean'],yerr=[seven['mean']-seven.ci_low,seven.ci_high-seven['mean']],fmt='o-',capsize=3);ax.axhline(0,color='gray',lw=.8);ax.set(xlabel='Layer',ylabel='J-Lens minus Vanilla title advantage',title='Within-paper lens increment (50 papers)');fig.tight_layout();fig.savefig(out/'figures'/'jlens_minus_vanilla.png',dpi=170);fig.savefig(out/'figures'/'jlens_minus_vanilla.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5));ax.scatter(floor[~(floor.range=='0-2')].null_mean,floor[~(floor.range=='0-2')].true_win,alpha=.6,label='Other bins');ax.scatter(low.null_mean,low.true_win,marker='D',s=60,label='Bin 0-2');ax.plot([0,1],[0,1],'--',color='gray');ax.set(xlabel='Shuffled-title Null mean',ylabel='True-title Gold win rate',title='L56 title-specific accessibility by paper');ax.legend();fig.tight_layout();fig.savefig(out/'figures'/'floor_L56_scatter.png',dpi=170);fig.savefig(out/'figures'/'floor_L56_scatter.pdf');plt.close(fig)
    overview={'n_papers':50,'n_pairs':20,'n_shuffle_contexts':1000,'matching_manifest':'f1712eabab1853fafaba08d774faf2eda7d341a908f2027104147e29ca8f0bcd','integrated_jlens_minus_vanilla':comparisons[-1],'matched_ab_difference_of_lens_increment':{'mean':float(vals.mean()),'ci_low':abci[0],'ci_high':abci[1]},'L56_jlens_stage5_stage73':next(z for z in consistency if z['lens']=='jlens' and z['layer']==56),'floor_low_six_L56':{'n':len(low),'mean_adv':float(low.title_advantage.mean()),'positive':int((low.title_advantage>0).sum()),'pct90':int((low.null_percentile_midrank>=.9).sum()),'tail05':int((low.empirical_tail_fraction<=.05).sum())}}
    (out/'summary'/'overview.json').write_text(json.dumps(overview,indent=2,ensure_ascii=False,default=lambda x: x.item() if hasattr(x,'item') else str(x)))
    report=f'''# Stage 7.4 — Cross-stage Measurement Validity Audit\n\nCPU-only, read-only exploration over frozen Pilot50. All bootstrap CIs are paper-level (or pair-level for matched AB), 20,000 draws, percentile 95%, unadjusted. No causal claims.\n\n## Main findings\n\nStage5 vs Stage7.3 L56 J-Lens same-paper Pearson r = {overview['L56_jlens_stage5_stage73']['pearson']:.4f}; Spearman rho = {overview['L56_jlens_stage5_stage73']['spearman']:.4f}. Both metrics use First-token but different contrasts, units and number of shuffled titles.\n\nIntegrated J-Lens minus Vanilla title advantage: {comparisons[-1]['mean']:+.5f}, 95% CI [{comparisons[-1]['ci_low']:+.5f}, {comparisons[-1]['ci_high']:+.5f}] over 50 papers. This is a **difference in title-specific advantage**, NOT J-Lens fidelity proof.\n\nMatched 20-pair A-B difference of lens increment: {vals.mean():+.5f}, 95% CI [{abci[0]:+.5f}, {abci[1]:+.5f}].\n\nBin 0-2 (6 papers) J-Lens L56 mean advantage {low.title_advantage.mean():+.5f}, {int((low.title_advantage>0).sum())}/6 positive, {int((low.null_percentile_midrank>=.9).sum())}/6 midrank percentile >=90%, {int((low.empirical_tail_fraction<=.05).sum())}/6 corrected empirical tail <=0.05. These six papers are NOT evidence of a population-wide floor.\n\n## Caveats\n\n* This cohort and L56 were inspected before Stage7.4. All conclusions exploratory; multiple comparisons and winner's curse apply.\n* Stage5 has one crossed shuffled source; Stage7.3 has 20 metadata-matched sources and a 100-author win-rate outcome. Correlation can be modest without either being invalid.\n* Matched shuffle titles are not exchangeable, so empirical tail fractions are reference fractions, not necessarily calibrated permutation p-values.\n* Frozen Stage7.2 first-token pools have repeated token IDs; Gold Win Rate measures candidate token discrimination, NOT full-name identification.\n* Source-author presence in false pool and lenient matched title tiers require sensitivity analysis.\n* Paper sharing/authors/contexts create possible dependence; conventional bootstrap may understate uncertainty.\n\nAll derived CSVs and figures are in summary/ and figures/. Stage 5-7.3 inputs were read, never overwritten.\n'''
    (out/'reports'/'audit_report.md').write_text(report)
    print('STAGE 7.4 COMPLETE',out,'stage5_l56_r',round(overview['L56_jlens_stage5_stage73']['pearson'],4),'lens_increment',round(comparisons[-1]['mean'],5),'ci',[round(comparisons[-1]['ci_low'],5),round(comparisons[-1]['ci_high'],5)],'floor_low',overview['floor_low_six_L56'])
if __name__=='__main__':main()
