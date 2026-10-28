"""Stage 13 M2c (CPU): a text model that has not memorised these papers, probed the same way.
bert-base-uncased (pre-trained on Wikipedia + BookCorpus, before 2019; scientific paper titles are rare there), every
layer, mean-pooled over the title tokens; the same 9,108 papers, the same 5 folds by paper, the same ridge as M2.
If BERT reaches the R^2 / AUROC of Qwen's last-title-token residual, year and citations come from the style of the
title, not from knowing the paper. Targets: year, log citations, log citations with the year removed, recognised
(target vs control, AUROC within citation bin). Title text only (no year, no authors) - as at Qwen's last title token.
"""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd, torch, transformers

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'; ROOT = BASE / '381_stage13'
sp = importlib.util.spec_from_file_location('m', Path.home() / 'jlens_work/13_stage13/stage13_cpu.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
pid = np.concatenate([np.load(f)['resid_paper_id'] for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))])   # same order as M2
P = papers.loc[pid]; folds = np.random.default_rng(13).integers(0, 5, len(pid)) if m.SPLIT == 'paper' else m.group_folds(pid)[0]
tok = transformers.AutoTokenizer.from_pretrained('bert-base-uncased'); bert = transformers.AutoModel.from_pretrained('bert-base-uncased', output_hidden_states=True).eval()
H = []
with torch.inference_mode():
    for i in range(0, len(P), 64):
        e = tok(list(P.title.astype(str).iloc[i:i + 64]), padding=True, truncation=True, max_length=96, return_tensors='pt')
        hs = bert(**e).hidden_states; msk = e.attention_mask[..., None].float()
        H.append(torch.stack([(h * msk).sum(1) / msk.sum(1) for h in hs], 1).numpy().astype(np.float32))
H = np.concatenate(H); print('BERT features', H.shape, flush=True)
year = pd.to_numeric(P.year, errors='coerce').to_numpy(float); cit = np.log10(pd.to_numeric(P.citations, errors='coerce').fillna(0).to_numpy(float) + 1)
Yd = np.eye(40)[np.clip(((np.nan_to_num(year, nan=2000) - 1820) // 5).astype(int), 0, 39)]
cit_res = cit - m.ridge_cv(Yd, cit[:, None], np.random.default_rng(13).integers(0, 5, len(cit)))[0][:, 0]
grp = P.group_tight.to_numpy(); keep = np.isin(grp, ['target', 'control']); rec = (grp == 'target').astype(float); bins = P.citation_bin.to_numpy()
ok = ~np.isnan(year); rows = []
for l in range(H.shape[1]):
    X = H[:, l]
    for name, kind, Y, sel, ex in (('year', 'r2', year, ok, None), ('log citations', 'r2', cit, slice(None), None),
                                   ('log citations | year removed', 'r2', cit_res, slice(None), None), ('recognised (target vs control)', 'auc_bin', rec, keep, bins)):
        p, a = m.ridge_cv(X[sel], Y[sel][:, None], folds[sel])
        rows.append(dict(model='bert-base-uncased', layer=l, target=name, value=m.metric(kind, Y[sel], p[:, 0], None if ex is None else ex[sel]), alpha=a))
    print('layer', l, ' '.join(f"{r['target'][:8]}={r['value']:.3f}" for r in rows[-4:]), flush=True)
d = pd.DataFrame(rows); d.to_csv(m.S / 'M2c_bert_baseline.csv', index=False); print(d.round(3).to_string(index=False))
