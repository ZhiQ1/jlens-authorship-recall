"""Stage 13 X3 text-model baseline (user request 2026-10-31, task 1). CPU.

Question: does a plain text model show the same "middle-layer advantage over its own text baseline" that Qwen3-32B shows
for G'(l) = cos(orig, para) - cos(orig, D) (Qwen: G'(L4) ~ +0.30, G' - G'(L4) peaks +0.16 at L36, +0.06..+0.16 at L28-L40)?

Texts (identical to X3): original title, Qwen paraphrase (raw/para_gen), lexical neighbour D (x3_pairs.csv lexical_neighbour_j2
= config/x3_lexical_neighbour_j2.csv), partner B (reference). Each text is encoded ALONE (no prompt).
Models / representations:
  bert-base-uncased  hidden layers 0..12 (0 = embedding layer = text baseline, analogous to Qwen L4; also relative to L1)
                     positions: title_last (last wordpiece of the title, i.e. the token before [SEP]), mean_title (mean over the
                     title wordpieces, specials excluded), cls ([CLS]).
  all-mpnet-base-v2  hidden layers 0..12, positions: mean (attention-mask mean over all tokens incl. <s> </s>, exactly the
                     model's own Pooling module), title_last (token before </s>), cls (<s>); plus layer 'final' = the
                     SentenceTransformer sentence embedding (mean pooling + Normalize; cosine equals layer-12 mean - checked).
  Qwen3-32B          for comparison, per-paper cosines from summary_x3/x3_cos_per_paper.csv.gz (base L4), point values
                     checked against summary_x3/x3_gap.csv.
Intervals: team-cluster bootstrap with the SAME draws as stage13_x3_analyze.py (team_w, SEED[(split, subset)], 2,000 draws),
so model-vs-Qwen differences are paired.
Scale-free comparison: ratio = max_l (G'(l) - G'(base)) / G'(base), l > base; base = text baseline (BERT/mpnet L0, Qwen L4)
and, as a second reading, the next layer (L1 / Qwen L8); NaN when G'(base) ~ 0 ([CLS] at L0 is the same vector for every text) (argmax on the point estimate; CI at that fixed
layer, and CI of the re-maximised ratio); also ratio_qwen - ratio_model with paired CIs.

Usage: python stage13_x3_textbase.py [--limit N] [--out DIR]   (--limit: first N papers, tiny test)
Outputs: summary_x3/x3_textbase_gap.csv, x3_textbase_ratio.csv, x3_textbase_meta.json"""
import argparse, importlib.util, json, os
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
SETS = {'primary': 'include_primary', 'sensitivity': 'include_sensitive'}
SUBSETS = ['all', 'd_matched', 'd_unmatched']; SPLITS = ['tune', 'test', 'all']
VERS = ['paraphrase', 'partner', 'lexical_neighbour']          # compared with the original
WARN = []


def warn(m): WARN.append(m); print('WARN', m, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


X3 = load(H / '13_stage13/stage13_x3_analyze.py', 'x3a')     # team_w, SEED, NB, ci (not edited)


def encode_hf(name, texts, kind, bs=64):
    """returns {pos: [n_texts, 13, d] unit-norm float32}"""
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
    tok = AutoTokenizer.from_pretrained(name); mod = AutoModel.from_pretrained(name).eval()
    poss = ['title_last', 'mean_title', 'cls'] if kind == 'bert' else ['mean', 'title_last', 'cls']
    out = {p: [] for p in poss}; ntr = 0
    for i in range(0, len(texts), bs):
        e = tok(texts[i:i + bs], padding=True, truncation=True, max_length=384 if kind == 'mpnet' else 512, return_tensors='pt',
                return_special_tokens_mask=True)
        sm = e.pop('special_tokens_mask')
        ntr += int((e.attention_mask.sum(1) >= (384 if kind == 'mpnet' else 512)).sum())
        with torch.no_grad(): hs = torch.stack(mod(**e, output_hidden_states=True).hidden_states, 1).float()   # [b, 13, T, d]
        am = e.attention_mask.float(); tm = am * (1 - sm.float())              # title tokens = non-special, non-pad
        last = (tm * torch.arange(tm.shape[1])).argmax(1)                       # index of the last title token
        bi = torch.arange(hs.shape[0])
        rep = {'title_last': hs[bi, :, last], 'cls': hs[:, :, 0]}
        if kind == 'bert': rep['mean_title'] = (hs * tm[:, None, :, None]).sum(2) / tm.sum(1)[:, None, None]
        else: rep['mean'] = (hs * am[:, None, :, None]).sum(2) / am.sum(1)[:, None, None]
        for p in poss: out[p].append(torch.nn.functional.normalize(rep[p], dim=-1).numpy())
        if i == 0:
            j = 0; ids = e.input_ids[j][e.attention_mask[j].bool()]
            print(name, 'example tokens', tok.convert_ids_to_tokens(ids.tolist()), '| last title token', tok.convert_ids_to_tokens([int(e.input_ids[j, last[j]])]), flush=True)
    if ntr: warn(f'{name}: {ntr} texts hit max_length (truncated)')
    return {p: np.concatenate(v) for p, v in out.items()}


def encode_st(name, texts):
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(name, device='cpu')
    E = m.encode(texts, batch_size=64, convert_to_numpy=True, normalize_embeddings=False, show_progress_bar=False)
    return (E / np.linalg.norm(E, axis=1, keepdims=True)).astype(np.float32)


def cos_array(E, idx):
    """E [n_texts, L, d] unit-norm; idx [n_papers, 4] (orig, para, partner, D) -> [n, 3, L]"""
    o = E[idx[:, 0]]
    return np.stack([np.einsum('nld,nld->nl', o, E[idx[:, k]]) for k in (1, 2, 3)], 1)


def gap_rows(model, pos, layers, C, s, W, setn, sub, part, base, base2):
    rows = []; ib = layers.index(base); ib2 = layers.index(base2) if base2 in layers else None
    for key, vi in (('lex', 2), ('partner', 1)):
        V = C[:, 0] - C[:, vi]                                                  # [n, L]
        Bt = (W @ V) / W.sum(1, keepdims=True)
        for li, l in enumerate(layers):
            r = dict(model=model, pos=pos, set=setn, subset=sub, split=part, comparison=key, layer=l, base_layer=base, n=len(s),
                     n_teams=s.team.nunique(), cos_orig_para=C[:, 0, li].mean(), cos_orig_other=C[:, vi, li].mean(), gap=V[:, li].mean())
            r['lo'], r['hi'] = X3.ci(Bt[:, li])
            r['gap_minus_base'] = V[:, li].mean() - V[:, ib].mean(); r['dbase_lo'], r['dbase_hi'] = X3.ci(Bt[:, li] - Bt[:, ib])
            if ib2 is not None:
                r['gap_minus_base2'] = V[:, li].mean() - V[:, ib2].mean(); r['dbase2_lo'], r['dbase2_hi'] = X3.ci(Bt[:, li] - Bt[:, ib2])
            rows.append(r)
    return rows


def ratio_stats(C, W, layers, base):
    """G' (lex). returns point ratio, argmax layer, boot ratio at fixed layer, boot re-maximised ratio"""
    V = C[:, 0] - C[:, 2]; g = V.mean(0); Bt = (W @ V) / W.sum(1, keepdims=True)
    ib = layers.index(base); later = [i for i, l in enumerate(layers) if l > base]
    d = g[later] - g[ib]; j = later[int(np.argmax(d))]
    if abs(g[ib]) < 1e-4:                                                       # e.g. [CLS] at the embedding layer: identical for all texts
        nan = np.full(len(Bt), np.nan)
        return dict(base_layer=base, gap_base=g[ib], best_layer=layers[j], gap_best=g[j], max_gap_minus_base=g[j] - g[ib], ratio=np.nan), nan, nan
    with np.errstate(divide='ignore', invalid='ignore'):
        bfix = (Bt[:, j] - Bt[:, ib]) / Bt[:, ib]; bmax = (Bt[:, later] - Bt[:, [ib]]).max(1) / Bt[:, ib]
    return dict(base_layer=base, gap_base=g[ib], best_layer=layers[j], gap_best=g[j], max_gap_minus_base=g[j] - g[ib],
                ratio=(g[j] - g[ib]) / g[ib]), bfix, bmax


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int); ap.add_argument('--out'); a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / 'summary_x3'; out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / 'summary_x3/x3_pairs.csv')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): df[c] = df[c].astype(bool)
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
    paras = {}
    for f in sorted((ROOT / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); paras |= dict(zip(z['paper_id'], z['paraphrase']))
    nd = (df.lexical_neighbour != df.lexical_neighbour_j2).sum()
    if nd: warn(f'{nd} rows: stored lexical_neighbour != lexical_neighbour_j2 (using lexical_neighbour_j2)')
    # Qwen per-paper cosines, aligned to df order (before --limit so the row order is the analysis order)
    q = pd.read_csv(ROOT / 'summary_x3/x3_cos_per_paper.csv.gz')
    q = q[q.pos == 'title_last'].pivot_table(index='paper_id', columns=['version', 'layer'], values='cos_with_original')
    qlayers = sorted({l for _, l in q.columns})
    if q.index.duplicated().any() or df.paper_id.duplicated().any(): warn('duplicated paper ids in Qwen cos table / x3_pairs')
    CQ = np.stack([q.loc[df.paper_id, [(v, l) for l in qlayers]].to_numpy() for v in VERS], 1).astype(np.float64)   # [n, 3, 15]
    if a.limit: df = df.iloc[:a.limit].copy(); CQ = CQ[:a.limit]
    texts, tix = [], {}
    def add(t):
        t = str(t)
        if t not in tix: tix[t] = len(texts); texts.append(t)
        return tix[t]
    idx = np.array([[add(papers.loc[r.paper_id].title), add(paras[r.paper_id]), add(papers.loc[r.partner].title),
                     add(papers.loc[r.lexical_neighbour_j2].title)] for r in df.itertuples()])
    print(f'papers {len(df)}; unique texts {len(texts)}', flush=True)
    # ---- encode
    REPS = {}   # (model, pos) -> (layers, C [n, 3, L])
    Eb = encode_hf('bert-base-uncased', texts, 'bert')
    for p, E in Eb.items(): REPS['bert-base-uncased', p] = (list(range(13)), cos_array(E, idx))
    Em = encode_hf('sentence-transformers/all-mpnet-base-v2', texts, 'mpnet')
    for p, E in Em.items(): REPS['all-mpnet-base-v2', p] = (list(range(13)), cos_array(E, idx))
    Es = encode_st('sentence-transformers/all-mpnet-base-v2', texts)
    chk = np.abs((Es * Em['mean'][:, 12]).sum(1) - 1).max()
    print(f'mpnet: sentence embedding vs layer-12 mean pooling, max |cos - 1| = {chk:.2e}', flush=True)
    if chk > 1e-3: warn(f'mpnet sentence embedding differs from layer-12 mean pooling (max |cos-1| {chk:.2e})')
    Cm = REPS['all-mpnet-base-v2', 'mean'][1]
    REPS['all-mpnet-base-v2', 'mean'] = (list(range(13)) + [13], np.concatenate([Cm, cos_array(Es[:, None], idx)], 2))   # layer 13 = 'final'
    REPS['Qwen3-32B', 'title_last'] = (qlayers, CQ)
    BASE = {'bert-base-uncased': (0, 1), 'all-mpnet-base-v2': (0, 1), 'Qwen3-32B': (4, 8)}
    # ---- analyses
    G, R = [], []
    for setn, col in SETS.items():
        for sub in SUBSETS:
            m0 = df[col].to_numpy() & df.team.notna().to_numpy()
            if sub == 'd_matched': m0 &= df.d_matched.to_numpy()
            if sub == 'd_unmatched': m0 &= ~df.d_matched.to_numpy()
            for part in SPLITS:
                m = m0 if part == 'all' else m0 & (df.split == part).to_numpy()
                s = df[m]
                if len(s) < 2: print(f'skip {setn}/{sub}/{part}: n={len(s)}'); continue
                W = X3.team_w(s.team.to_numpy(), X3.SEED[part, sub])
                bq = {}; rr = []
                for (model, pos), (layers, C) in REPS.items():
                    b1, b2 = BASE[model]
                    G += gap_rows(model, pos, layers, C[m], s, W, setn, sub, part, b1, b2)
                    for kind, b in (('text_baseline', b1), ('next_layer', b2)):
                        pt, bfix, bmax = ratio_stats(C[m], W, layers, b)
                        r = dict(model=model, pos=pos, set=setn, subset=sub, split=part, n=len(s), base_kind=kind, **pt)
                        r['ratio_lo'], r['ratio_hi'] = X3.ci(bfix); r['ratio_remax_lo'], r['ratio_remax_hi'] = X3.ci(bmax)
                        if model == 'Qwen3-32B': bq[kind] = (bfix, pt['ratio'])
                        rr.append((r, bfix))
                for r, bfix in rr:
                    q0 = bq[r['base_kind']]
                    r['qwen_minus_model'] = q0[1] - r['ratio']; r['qmm_lo'], r['qmm_hi'] = X3.ci(q0[0] - bfix); R.append(r)
    G, R = pd.DataFrame(G), pd.DataFrame(R)
    # parity with x3_gap.csv (Qwen, title_last, lex)
    if not a.limit:
        x = pd.read_csv(ROOT / 'summary_x3/x3_gap.csv'); x = x[(x.pos == 'title_last') & (x.comparison.isin(['lex', 'partner']))]
        g = G[G.model == 'Qwen3-32B'].merge(x, on=['set', 'subset', 'split', 'comparison', 'layer'], suffixes=('', '_x3'))
        dev = max(np.abs(g.gap - g.gap_x3).max(), np.abs(g.lo - g.lo_x3).max(), np.abs(g.gap_minus_base - g.gap_minus_L4).max())
        print(f'Qwen parity with x3_gap.csv: {len(g)} rows, max |diff| {dev:.2e}', flush=True)
        if dev > 1e-3: warn(f'Qwen recomputation differs from x3_gap.csv (max {dev:.2e}); x3_gap.csv point values are authoritative')
    G.to_csv(out / 'x3_textbase_gap.csv', index=False); R.to_csv(out / 'x3_textbase_ratio.csv', index=False)
    json.dump(dict(n_papers=len(df), n_texts=len(texts), mpnet_final_check=float(chk), warn=WARN, limit=a.limit), open(out / 'x3_textbase_meta.json', 'w'), indent=1)
    t = R[(R.set == 'primary') & (R.subset == 'all') & (R.split == 'test')]
    print(t[['model', 'pos', 'base_kind', 'gap_base', 'best_layer', 'max_gap_minus_base', 'ratio', 'ratio_lo', 'ratio_hi']].to_string(), flush=True)
    print('X3 TEXTBASE DONE', flush=True)


if __name__ == '__main__':
    main()
