#!/usr/bin/env python3
"""Independent 50/50 fit of the SAME original 100-prompt Qwen3-32B J-Lens protocol.

Usage:
  python 351_self_jlens_split_half.py --mode inspect
  python -u 351_self_jlens_split_half.py --mode fit --half A
  python -u 351_self_jlens_split_half.py --mode fit --half B
  python 351_self_jlens_split_half.py --mode analyze

A uses corpus indices 0,2,...,98; B uses 1,3,...,99. Explicitly distinct
fitting checkpoints. No claim of independent evaluation from this script:
for held-out output-fidelity comparison reuse separate 20 generic + 20 paper
prompts from 351_self_jlens_validation.py after adding lens-path support.
"""
import argparse, csv, hashlib, json, os, time
from pathlib import Path
ROOT=Path(f'/scratch/{os.environ.get("USER", "zhang.zhiqi2")}/jlens')
CORPUS=ROOT/'fitting_corpus/wikitext103_qwen32b_1000.jsonl'
MANIFEST=ROOT/'fitting_corpus/manifest.json'
OUT=ROOT/'351_self100_split_half'
MODEL='Qwen/Qwen3-32B'
LAYERS=[24,32,40,48,56,62]

def filehash(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def load_inputs():
    meta=json.loads(MANIFEST.read_text())
    assert filehash(CORPUS)==meta['corpus_sha256'],'Corpus checksum mismatch'
    rows=[json.loads(x) for x in CORPUS.read_text(encoding='utf-8').splitlines() if x.strip()]
    assert len(rows)==1000 and [r['index'] for r in rows]==list(range(1000))
    return rows,meta

def config(half,meta):
    indices=list(range(0 if half=='A' else 1,100,2))
    return {'protocol':'351_self100_split_half_v1','half':half,'model':MODEL,
            'model_revision':meta['model_revision'],'corpus_sha256':meta['corpus_sha256'],
            'indices':indices,'source_layers':LAYERS,'target_layer':63,
            'dim_batch':8,'max_seq_len':128,'skip_first':16,
            'dtype':'bfloat16','device_map':'cuda','n_prompts':50}

def paths(half):
    base=OUT/'fits'
    return base/f'lens_{half}.pt',base/f'checkpoint_{half}.pt',base/f'config_{half}.json'

def fit_half(half,rows,meta):
    import torch,transformers,jlens
    if not torch.cuda.is_available():raise RuntimeError('CUDA required for Jacobian fitting')
    free,total=torch.cuda.mem_get_info()
    print(f'CUDA GPU={torch.cuda.get_device_name(0)} total={total/1024**3:.2f} GiB free={free/1024**3:.2f} GiB',flush=True)
    if total < 70*1024**3:
        raise RuntimeError('Original fitting uses BF16 full-GPU Qwen3-32B: 80GB-class GPU required. Do not launch on A100 40GB or silently switch to 4-bit/offload for backward.')
    p,ckpt,conf=paths(half);p.parent.mkdir(parents=True,exist_ok=True)
    c=config(half,meta)
    if conf.exists():
        if json.loads(conf.read_text())!=c:raise RuntimeError('Split checkpoint config mismatch; no overwrite')
    elif ckpt.exists():raise RuntimeError('Checkpoint exists without config manifest')
    else:conf.write_text(json.dumps(c,indent=2)+'\n')
    if p.exists():
        obj=jlens.JacobianLens.load(str(p))
        if obj.n_prompts==50:
            print(f'Already finished lens {half}: {p}; no refit',flush=True);return
        raise RuntimeError('Existing lens has unexpected n_prompts')
    prompts=[rows[i]['text'] for i in c['indices']]
    print(f'Starting split {half}, indices {c["indices"]}, checkpoint={ckpt}',flush=True)
    hf=transformers.AutoModelForCausalLM.from_pretrained(MODEL,revision=c['model_revision'],dtype=torch.bfloat16,device_map='cuda',low_cpu_mem_usage=True).eval()
    tok=transformers.AutoTokenizer.from_pretrained(MODEL,revision=c['model_revision'])
    model=jlens.from_hf(hf,tok)
    t=time.time()
    obj=jlens.fit(model,prompts=prompts,source_layers=LAYERS,target_layer=63,dim_batch=8,
                  max_seq_len=128,skip_first=16,checkpoint_path=str(ckpt),checkpoint_every=1,resume=True)
    if obj.n_prompts!=50:raise RuntimeError(f'Expected 50 valid fitting prompts, got {obj.n_prompts}. Check checkpoint.')
    obj.save(str(p))
    (OUT/'fits'/f'complete_{half}.json').write_text(json.dumps({'config':c,'n_prompts':obj.n_prompts,'lens':str(p),'checkpoint':str(ckpt),'elapsed_seconds':round(time.time()-t,2)},indent=2)+'\n')
    print(f'FIT COMPLETE {half}: prompts={obj.n_prompts} saved={p}',flush=True)

def analyze():
    import numpy as np, torch, jlens
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    a,b=[paths(h)[0] for h in 'AB']
    for p in (a,b):
        if not p.exists():raise RuntimeError(f'Missing finished fitted lens {p}; run both halves first')
    A=jlens.JacobianLens.load(str(a)); B=jlens.JacobianLens.load(str(b))
    if A.n_prompts!=50 or B.n_prompts!=50:raise RuntimeError('Not both valid 50 prompt lenses')
    summary=[]
    for l in LAYERS:
        x=A.jacobians[l].detach().float().cpu().numpy().astype(np.float64,copy=False)
        y=B.jacobians[l].detach().float().cpu().numpy().astype(np.float64,copy=False)
        if x.shape!=(5120,5120) or y.shape!=(5120,5120):raise RuntimeError(f'Invalid shape layer {l}')
        finite=bool(np.isfinite(x).all() and np.isfinite(y).all())
        if not finite:raise RuntimeError(f'Nonfinite matrix layer {l}')
        nx=float(np.linalg.norm(x));ny=float(np.linalg.norm(y))
        cosine=float(np.sum(x*y)/(nx*ny)) if nx*ny else float('nan')
        relative=float(np.linalg.norm(x-y)/(0.5*(nx+ny))) if nx+ny else float('nan')
        summary.append({'layer':l,'frob_A':nx,'frob_B':ny,'cosine':cosine,'relative_frobenius_difference':relative,
                        'entry_std_A':float(x.std()),'entry_std_B':float(y.std()),'nonfinite_count':0})
        print(f'L{l}: cosine={cosine:.6f} relFro={relative:.6f} frob_A={nx:.2f} frob_B={ny:.2f}',flush=True)
    (OUT/'summary').mkdir(parents=True,exist_ok=True)
    (OUT/'figures').mkdir(parents=True,exist_ok=True)
    (OUT/'reports').mkdir(parents=True,exist_ok=True)
    dest=OUT/'summary'/'matrix_stability.csv'
    with dest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    (OUT/'summary'/'matrix_stability.json').write_text(json.dumps({'n_prompts_each':50,'source_layers':LAYERS,'matrix_metrics':summary,'interpretation':'Matrix-only stability; does not establish held-out output/rank stability'},indent=2)+'\n')
    for field,ylabel,name in [('cosine','Matrix cosine similarity','matrix_cosine'),('relative_frobenius_difference','Relative Frobenius difference','matrix_relative_difference')]:
        fig,ax=plt.subplots(figsize=(7.5,4.5));ax.plot(LAYERS,[r[field] for r in summary],marker='o');ax.set(xlabel='Source layer',ylabel=ylabel,title='Self-100 independent 50/50 fits');ax.grid(alpha=.25)
        fig.tight_layout()
        for ext in ('png','pdf'):fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=180)
        plt.close(fig)
    md=['# Self-fitted Qwen3-32B J-Lens: Split-half Matrix Stability','',
        '## Experimental design',
        'Original WikiText fitting corpus verified against manifest SHA-256. Split A uses even indices 0..98, Split B uses odd indices 1..99. Each half was independently fit with exactly the original 100-prompt script settings (BF16 Qwen3-32B, source layers 24/32/40/48/56/62, target L63, dim_batch=8, max_seq_len=128, skip_first=16).',
        '', '## Matrix numerical checks and stability','',
        '| Layer | Cosine(A,B) | Relative Frobenius Difference | Norm A | Norm B |','|---|---:|---:|---:|---:|']
    for r in summary:md.append(f'| {r["layer"]} | {r["cosine"]:.6f} | {r["relative_frobenius_difference"]:.6f} | {r["frob_A"]:.2f} | {r["frob_B"]:.2f} |')
    md+=['','## Conclusions and limitations',
         'This is a MATRIX-LEVEL split-half check, not yet a complete readout-stability validation. Neither high cosine nor low norm difference proves the two lenses agree on vocabulary ranks, KL, or gold author readouts. Those require the same held-out 20 generic and 20 paper prompts, and the same output-scoring code.',
         'Do not use the fitting prompts for held-out assessment. The selection rule is interleaved, not random; it is predeclared for reproducibility.',
         '', '## Artifacts', '`fits/lens_A.pt`, `fits/lens_B.pt`, `summary/matrix_stability.csv`, `figures/matrix_cosine.{png,pdf}`, `figures/matrix_relative_difference.{png,pdf}`.']
    (OUT/'reports'/'split_half_report.md').write_text('\n'.join(md)+'\n')
    print('ARTIFACTS',OUT,flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['inspect','fit','analyze'],required=True);p.add_argument('--half',choices=['A','B'])
    args=p.parse_args()
    if args.mode=='analyze':return analyze()
    rows,meta=load_inputs()
    if args.mode=='inspect':
        for h in 'AB':
            c=config(h,meta);lens,ckpt,cf=paths(h)
            print(h,'indices=',c['indices'],'lens_exists=',lens.exists(),'checkpoint_exists=',ckpt.exists())
        print('Fitting corpus verified; halves disjoint and jointly cover original first 100 prompts')
        return
    if not args.half:p.error('--mode fit requires --half A or B')
    fit_half(args.half,rows,meta)
if __name__=='__main__':main()
