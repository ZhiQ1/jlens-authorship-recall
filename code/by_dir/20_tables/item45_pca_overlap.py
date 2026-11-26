#!/usr/bin/env python3
"""Exploratory (post hoc, not pre-registered), 2026-11-22. CPU only, stored states.
Item 4 (L48): meaning of the leading PCs of the name-position title-specific vectors d_i (surname first token, Vpd usable
  false titles; raw/b2_npprobe; same d_i as explore_pca_np_20261120.py). PCA = centered PCA of pooled paper-mean d
  (target + control) so that target share is a feature. For PCs 1-30: top-20 and bottom-20 papers by score; features of each
  20-set: papers sharing an author team with another paper in the set, papers sharing the first author (full-name string),
  modal field share, mean year, mean log10(1+citations), target share, mean title word count, modal share of the first
  author's surname-first token. Enrichment vs 2,000 random 20-sets from the same papers (one-sided upper for count/mode
  features, two-sided for means); Holm over 30 PCs x 2 ends x 8 features.
Item 5 (L40, L48): H2 x H3 direction overlap.
  ID_title = mean over addendum-20 target papers of (h_true - h_fict) at the LAST TITLE TOKEN (a20v2_titlepos resid_title_*;
  name-position fict states are not stored), also control and target - control.
  author_gold_name / author_svd_name = H3 name-position probe read-out directions (as explore_dir_overlap_20261121.py).
  author_gold_title = title-position author probe (E4b-style ridge: Stage 11 true title residual -> stored L63 colon residual,
  read through lm_head rows x final-norm weight of the gold first tokens), mean over target papers.
  Delta_name = name-position target - control mean shift of d_i.
  Cosines with random baseline 1/sqrt(5120); team-bootstrap CIs (1,000 draws, seed 22) for cosines of the mean vectors
  (ID_title, Delta_name) with fixed probe directions; shares in the top-10 / top-50 PCs of the item-4 pooled PCA (name
  position; for title-position vectors this is a cross-position comparison in the same residual basis).
Usage: item45_pca_overlap.py [--tiny]
"""
import argparse, importlib.util, json, time
from pathlib import Path
import numpy as np, pandas as pd
H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
G391 = B / '391_groups'; RAW = R13 / 'raw/b2_npprobe'; KS = [0, 1, 2, 3, 4]; T0 = time.monotonic(); NPERM = 2000; NB = 1000
OUTB = G391 / 'summary_tables_20261122'
def log(*a): print(f'[{time.monotonic() - T0:7.0f}s]', *a, flush=True)
def unit(v): return v / np.linalg.norm(v)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (m - r) * p[i])); adj[i] = run
    return adj

def md(df, floatfmt='.4f'):
    cols=list(df.columns); f=lambda v: (format(v, floatfmt) if isinstance(v, float) else str(v))
    return '\n'.join(['| '+' | '.join(map(str,cols))+' |','|'+'---|'*len(cols)]+['| '+' | '.join(f(v) for v in r)+' |' for r in df.itertuples(index=False)])

def main(a):
    sfx = '_tiny' if a.tiny else ''
    O4 = OUTB / f'item4{sfx}'; O5 = OUTB / f'item5{sfx}'; O4.mkdir(parents=True, exist_ok=True); O5.mkdir(parents=True, exist_ok=True)
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'role', 'token_id', 'author_index']).set_index('row_id')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citations', 'year', 'field', 'title', 'authors']).set_index('paper_id')
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); _, team = c13.group_folds(papers.index.to_numpy()); TEAM = pd.Series(team, index=papers.index)
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); nw = vr['norm_weight'].astype(np.float32); vpos = pd.Series(np.arange(len(vr['token_id'])), index=vr['token_id'])
    sur_ids = np.array(sorted(tok[tok.role == 'surname_first'].token_id.unique())); sur_ids = sur_ids[vpos.reindex(sur_ids).notna().to_numpy()]
    U = vr['lm_head_rows'][vpos.reindex(sur_ids).astype(int).to_numpy()].astype(np.float32); col = pd.Series(np.arange(len(sur_ids)), index=sur_ids)
    shards = sorted((RAW / 'true').glob('shard_*.npz'))[: (3 if a.tiny else None)]
    # paper metadata for item 4
    fa_tok = tok[(tok.role == 'surname_first') & (tok.author_index == 0)].groupby('paper_id').token_id.first()
    def first_author(s):
        s = str(s); 
        for sep in [';', ',', ' and ']:
            if sep in s: return s.split(sep)[0].strip().lower()
        return s.strip().lower()
    meta = pd.DataFrame(dict(team=TEAM, field=papers.field, year=pd.to_numeric(papers.year, errors='coerce'), lc=np.log10(1 + pd.to_numeric(papers.citations, errors='coerce')),
                             target=(papers.group_tight == 'target').astype(float), tlen=papers.title.astype(str).str.split().str.len(), fa=papers.authors.map(first_author), fatok=fa_tok.reindex(papers.index)))
    # title-position E4b-style author probe (Stage 11 true titlepos, all stored papers)
    tz = [np.load(f) for f in sorted((R11 / 'raw/titlepos/true').glob('shard_*.npz'))[: (3 if a.tiny else None)]]
    pl11 = list(tz[0]['probe_layers']); res = dict(label='exploratory (post hoc, not pre-registered)', item5={})
    a20 = [np.load(f) for f in sorted((G391 / 'raw/a20v2_titlepos').glob('shard_*.npz'))]
    pl20 = list(a20[0]['probe_layers']); F20 = pd.read_parquet(G391 / 'raw/a20v2_freeze/fict_titles.parquet').set_index('paper_id')
    rows5 = []
    for l in ([48] if a.tiny else [40, 48]):
        pp = pd.read_parquet(R13 / f'summary_b2_np/probe_v2/perpaper_surname_first_L{l}.parquet', columns=['paper_id'] + [f'dropped_{k}' for k in KS]).set_index('paper_id')
        Xs, Ds, PID, GT, Ys = [], [], [], [], []
        for f in shards:
            zt = np.load(f); rid = zt['row_id']; sel = tok.role.reindex(rid).to_numpy() == 'surname_first'; r = rid[sel]
            ht = zt[f'resid_L{l}'][sel].astype(np.float32); pid = tok.paper_id.reindex(r).to_numpy()
            dm = np.stack([~pp[f'dropped_{k}'].reindex(pid).fillna(True).to_numpy().astype(bool) for k in KS], 1); fs = np.zeros_like(ht)
            for k in KS:
                zf = np.load(RAW / f'false_{k}' / f.name); fs += zf[f'resid_L{l}'][sel].astype(np.float32) * dm[:, k:k + 1]
            with np.errstate(invalid='ignore', divide='ignore'): Ds.append(ht - fs / dm.sum(1, keepdims=True))
            Xs.append(ht); PID.append(pid); GT.append(tok.token_id.reindex(r).to_numpy())
            zy = np.load(R13 / 'raw/allTok_L63' / f.name); yp = pd.Series(np.arange(len(zy['row_id'])), index=zy['row_id']).reindex(r).to_numpy().astype(int)
            Ys.append(zy['resid'][yp].astype(np.float32))
        X = np.concatenate(Xs); D = np.concatenate(Ds); PID = np.concatenate(PID); GT = np.concatenate(GT); Y = np.concatenate(Ys); del Xs, Ds, Ys
        mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; Gm = A.T @ A
        Wm = np.linalg.solve(Gm + np.trace(Gm) / Gm.shape[0] * np.eye(Gm.shape[0], dtype=np.float32), A.T @ (Y - Y.mean(0))); del A, Gm, Y
        Q = ((Wm / sd[:, None]) * nw[None, :]) @ U.T; del Wm
        gi = col.reindex(GT).to_numpy(); okg = np.isfinite(gi)
        qrow = np.full((len(X), X.shape[1]), np.nan, np.float32); qrow[okg] = Q[:, gi[okg].astype(int)].T
        Us, _, _ = np.linalg.svd(Q, full_matrices=False); asvd = Us[:, :5].T; del Q, X
        dfD = pd.DataFrame(D); dfD['p'] = PID; okd = np.isfinite(D).all(1); Dp = dfD[okd].groupby('p').mean(); del dfD, D
        dfq = pd.DataFrame(qrow); dfq['p'] = PID; qp = dfq[okg].groupby('p').mean(); del dfq, qrow
        g = papers.group_tight.reindex(Dp.index).to_numpy(); isT = g == 'target'; isC = g == 'control'
        Dpn = Dp.to_numpy(); Delta = Dpn[isT].mean(0) - Dpn[isC].mean(0)
        Pc = Dpn[isT | isC] - Dpn[isT | isC].mean(0); pids_pool = Dp.index[isT | isC]
        _, sv, Vt = np.linalg.svd(Pc, full_matrices=False); evs = sv ** 2 / (sv ** 2).sum()
        log(f'L{l}: papers T {isT.sum()} C {isC.sum()}')
        # ---------------- item 4 (L48 only)
        if l == 48:
            S = Pc @ Vt[:30].T; M = meta.reindex(pids_pool); rng = np.random.default_rng(22); n = len(M)
            def feats(idx):
                m = M.iloc[idx]
                return dict(team_shared=int(m.team.duplicated(keep=False).sum()), firstauthor_shared=int(m.fa.duplicated(keep=False).sum()),
                            field_mode=float(m.field.value_counts().iloc[0] / len(m)) if m.field.notna().any() else np.nan, year=float(m.year.mean()), logcit=float(m.lc.mean()),
                            target_share=float(m.target.mean()), title_len=float(m.tlen.mean()), surtok_mode=float(m.fatok.value_counts().iloc[0] / len(m)) if m.fatok.notna().any() else np.nan)
            null = pd.DataFrame([feats(rng.choice(n, 20, replace=False)) for _ in range(NPERM)])
            upper = {'team_shared', 'firstauthor_shared', 'field_mode', 'surtok_mode'}
            rows4 = []
            for k in range(30):
                for end, idx in (('top', np.argsort(-S[:, k])[:20]), ('bottom', np.argsort(S[:, k])[:20])):
                    fv = feats(idx); m = M.iloc[idx]
                    for fn, v in fv.items():
                        nv = null[fn].dropna().to_numpy()
                        p = float(((nv >= v).sum() + 1) / (len(nv) + 1)) if fn in upper else float(min(1, 2 * min(((nv >= v).sum() + 1) / (len(nv) + 1), ((nv <= v).sum() + 1) / (len(nv) + 1))))
                        rows4.append(dict(pc=k + 1, var_share=float(evs[k]), end=end, feature=fn, value=v, null_mean=float(nv.mean()), p=p,
                                          modal_field=str(m.field.value_counts().index[0]) if fn == 'field_mode' and m.field.notna().any() else '',
                                          examples=' || '.join(papers.title.reindex(m.index[:3]).astype(str).str[:70]) if fn == 'team_shared' else ''))
            R4 = pd.DataFrame(rows4); R4['p_holm'] = holm(R4.p.to_numpy()); R4.to_csv(O4 / 'pc_enrichment.csv', index=False)
            sig = R4[R4.p_holm < 0.05]
            ex = R4[(R4.feature == 'team_shared')][['pc', 'end', 'examples']]
            L4 = ['# Item 4 — meaning of the leading name-position PCs at L48 (exploratory, post hoc)', '', __doc__.split('Item 5')[0], '',
                  f'Pooled papers {n} (target {int(isT.sum())}, control {int(isC.sum())}); PC1–30 variance shares: ' + ', '.join(f'{x:.3f}' for x in evs[:30]), '',
                  f'## Holm-significant features (p_holm < 0.05): {len(sig)} of {len(R4)} tests', md(sig.drop(columns=['examples']), '.3f'), '',
                  '## Example titles (first 3 of each 20-set)', md(ex)]
            (O4 / 'report.md').write_text('\n'.join(L4) + '\n'); log('item4 done', len(sig), 'significant')
        # ---------------- item 5
        li = pl20.index(l); ids, dT = [], []
        for z in a20:
            dT.append(z['resid_title_true'][:, li].astype(np.float32) - z['resid_title_fict'][:, li].astype(np.float32)); ids += list(z['paper_id'])
        dT = np.concatenate(dT); grp20 = F20.group.reindex(ids).to_numpy(); t20 = grp20 == 'target'; c20 = grp20 == 'control'
        ID_T = dT[t20].mean(0); ID_C = dT[c20].mean(0); ID_TC = ID_T - ID_C
        # title-position author probe (E4b-style) at the same layer
        lt = pl11.index(l); Xt = np.concatenate([z['resid_title'][:, lt].astype(np.float32) for z in tz]); Yt = np.concatenate([z['resid_colon'][:, -1].astype(np.float32) for z in tz])
        rp = np.concatenate([z['resid_paper_id'] for z in tz]).astype(str)
        gold = pd.concat([pd.DataFrame({'paper_id': z['paper_id'].astype(str), 'kind': z['kind'], 'gold': z['gold']}) for z in tz])
        gold = gold[gold.kind.astype(str).str.contains('first', case=False)] if gold.kind.astype(str).str.contains('first', case=False).any() else gold
        gids = np.array(sorted(gold.gold.unique())); gids = gids[vpos.reindex(gids).notna().to_numpy()]
        Ug = vr['lm_head_rows'][vpos.reindex(gids).astype(int).to_numpy()].astype(np.float32); gcol = pd.Series(np.arange(len(gids)), index=gids)
        mu, sdt = Xt.mean(0), Xt.std(0) + 1e-6; A = (Xt - mu) / sdt; Gm = A.T @ A
        Wt = np.linalg.solve(Gm + np.trace(Gm) / Gm.shape[0] * np.eye(Gm.shape[0], dtype=np.float32), A.T @ (Yt - Yt.mean(0))); del A, Gm, Xt, Yt
        Qt = ((Wt / sdt[:, None]) * nw[None, :]) @ Ug.T; del Wt
        g1 = gold.groupby('paper_id').gold.first(); g1 = g1[g1.index.isin(papers.index[papers.group_tight == 'target'])]
        gi1 = gcol.reindex(g1.to_numpy()).dropna().astype(int).to_numpy(); author_gold_title = unit(Qt[:, gi1].mean(1)); Ust, _, _ = np.linalg.svd(Qt, full_matrices=False); del Qt
        gq = papers.group_tight.reindex(qp.index).to_numpy(); author_gold_name = unit(qp[gq == 'target'].to_numpy().mean(0))
        dirs = {'author_gold_name (H3 probe, name pos)': author_gold_name, 'author_gold_title (E4b-style, title pos)': author_gold_title, 'Delta_name (T−C shift, name pos)': unit(Delta)}
        for i in range(3): dirs[f'author_svd_name {i + 1}'] = asvd[i]
        for i in range(3): dirs[f'author_svd_title {i + 1}'] = Ust[:, i]
        vecs = {'ID_title target (true − fict)': ID_T, 'ID_title control': ID_C, 'ID_title T−C': ID_TC}
        # team bootstrap for ID vectors (a20 papers)
        teams20 = pd.factorize(TEAM.reindex(ids))[0]; nte = teams20.max() + 1; rng = np.random.default_rng(22); bootW = rng.multinomial(nte, np.full(nte, 1 / nte), size=NB).astype(np.float32)[:, teams20]
        for vn, v in vecs.items():
            for dn, d in dirs.items():
                c = float(unit(v) @ d)
                if vn.startswith('ID_title target'): sel_ = t20
                elif vn.startswith('ID_title control'): sel_ = c20
                else: sel_ = None
                bs = []
                for b in range(NB):
                    w = bootW[b]
                    if sel_ is None: vb = (w[t20] @ dT[t20]) / w[t20].sum() - (w[c20] @ dT[c20]) / w[c20].sum()
                    else: vb = (w[sel_] @ dT[sel_]) / w[sel_].sum()
                    bs.append(float(unit(vb) @ d))
                rows5.append(dict(layer=l, vector=vn, direction=dn, cos=c, lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                                  share_top10PC_name=float(((Vt[:10] @ unit(v)) ** 2).sum()), share_top50PC_name=float(((Vt[:50] @ unit(v)) ** 2).sum())))
        for dn, d in dirs.items():
            rows5.append(dict(layer=l, vector='(direction itself)', direction=dn, cos=np.nan, lo=np.nan, hi=np.nan,
                              share_top10PC_name=float(((Vt[:10] @ d) ** 2).sum()), share_top50PC_name=float(((Vt[:50] @ d) ** 2).sum())))
        res['item5'][l] = dict(n_a20_target=int(t20.sum()), n_a20_control=int(c20.sum()), n_name_T=int(isT.sum()), n_name_C=int(isC.sum()),
                               norm_ID_T=float(np.linalg.norm(ID_T)), norm_ID_TC=float(np.linalg.norm(ID_TC)), random_sd=float(1 / np.sqrt(5120)))
        log(f'item5 L{l} done')
    R5 = pd.DataFrame(rows5); R5.to_csv(O5 / 'h2_h3_overlap.csv', index=False); json.dump(res, open(O5 / 'h2_h3_overlap.json', 'w'), indent=1)
    L5 = ['# Item 5 — H2 × H3 direction overlap (exploratory, post hoc)', '', 'Item 5' + __doc__.split('Item 5')[1].split('Usage')[0], '', json.dumps(res['item5'], indent=1), '',
          md(R5, '.3f'), '', f'Random direction: ±{1 / np.sqrt(5120):.3f} (1 sd); random share in top 10 / 50 PCs: {10 / 5120:.4f} / {50 / 5120:.4f}.']
    (O5 / 'report.md').write_text('\n'.join(L5) + '\n'); log('DONE')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); main(ap.parse_args())
