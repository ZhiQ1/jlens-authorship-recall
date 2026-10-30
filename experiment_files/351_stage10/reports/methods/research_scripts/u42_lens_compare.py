"""U42: F1 author-prompt lens vs public / Fit A / self100 at shared layers (CPU, mmap, one layer at a time).
rel = ||A-B||_F/||B||_F ; cos = <A,B>_F/(||A|| ||B||) ; idd = ||J-I||_F/||I||_F (own definition)."""
import torch
P={'alens':'/scratch/zhang.zhiqi2/jlens/371_stage12/alens/lens.pt',
   'public':'/scratch/zhang.zhiqi2/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt',
   'fitA':'/scratch/zhang.zhiqi2/jlens/351_stage9/runner_runs/full_A_repair_101_100valid/lens.pt',
   'self100':'/scratch/zhang.zhiqi2/jlens/qwen32b_jlens_prelim_100.pt'}
L={k:torch.load(v,map_location='cpu',mmap=True,weights_only=False) for k,v in P.items()}
def J(k,l):
    j=L[k]['J']; return (j[l] if isinstance(j,dict) else j[L[k]['source_layers'].index(l)]).float()
I=None
for l in [24,32,40,48,56,62,44,52]:
    a=J('alens',l); I=torch.eye(a.shape[0]); row=[f'L{l}', 'idd(alens)=%.3f'%((a-I).norm()/I.norm())]
    for k in ['public','fitA','self100']:
        try:
            b=J(k,l)
            row.append('%s: rel=%.3f cos=%.3f idd=%.3f'%(k,(a-b).norm()/b.norm(),(a*b).sum()/(a.norm()*b.norm()),(b-I).norm()/I.norm()))
            if k=='public':
                for k2 in ['fitA','self100']:
                    try: c=J(k2,l); row.append('[%s vs public rel=%.3f cos=%.3f]'%(k2,(c-b).norm()/b.norm(),(c*b).sum()/(c.norm()*b.norm())))
                    except Exception: pass
        except Exception as e: row.append(f'{k}: n/a')
    print(' | '.join(row),flush=True)
