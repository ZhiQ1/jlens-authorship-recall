"""EXPLORATORY (post hoc, not pre-registered), 2026-11-21, user request: where does X4's L8 surname signal come from?
CPU only, existing caches only. No GPU job is run here.

X4 (381_stage13.py do_pscope): source = paper A's authors-prompt residual at the last title token, layer l, patched into
'Paper: X\n...' prompts; score = log10(1/rank) of A's answer tokens; D = mean over answer tokens, self source - partner
source. The partner (config/pairs.parquet) is already same field, same title token count, no shared surname.
Cached: raw/b2_pscope (title / colon / name sources; answers first author (per token role), year, field; layers
8..56; self and partner only). The score of A's answer from ANOTHER paper's state is not cached, so the Qwen D for a new
(topic-matched) partner needs new forwards (GPU; cost estimated in the report, not run).

Parts
 1  topic-matched partners: same field, nearest title under bert-base-uncased (mean-pooled) and all-mpnet-base-v2,
    excluding A's own author team and any shared surname. Qwen D for them is NOT computable from cache; reported instead:
    (i) how similar the cached partners already are, (ii) Qwen D vs partner similarity (terciles, slope, team CI) and the
    slope-extrapolated D at the topic-matched similarity (model-based proxy, labelled as such).
 2  text baseline, same design: supervised LR (as x4_textbase2) from title features to the first author's surname-first /
    given-first token and to the year; D_text = log10 p(answer | own title) - log10 p(answer | partner title) for the
    cached partner and both topic-matched partners; standardised Qwen - text difference with team CI.
 3  target - control within citation bin for every D (Stage 10 estimator, weights n_t n_c/(n_t+n_c)), team bootstrap.
 4  literal overlap flags (a) title contains an author surname, (b) title tokens contain the first author's surname-first
    token, (c) eponym rule; D recomputed without them.
 5  readout difficulty: no-patch and partner-source score distributions per answer, standardised D per layer, per year token.
Output: 381_stage13/summary_explore_x4_source_20261121/ (report.md + csv). TINY=1 -> small subset, out dir *_tiny.
"""
import importlib.util, json, os, re, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TINY = os.environ.get('TINY') == '1'
OUT = ROOT / ('summary_explore_x4_source_20261121' + ('_tiny' if TINY else '')); OUT.mkdir(parents=True, exist_ok=True)
NB = 200 if TINY else 2000; LAY = [8, 16, 24, 32, 40, 48, 56]; SEED = 1121
LABEL = 'exploratory (post hoc, not pre-registered)'


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# ------------------------------------------------------------------ Qwen D from cache
def qwen_D(pids):
    fs = sorted((ROOT / 'raw/b2_pscope').glob('shard_*.parquet'))
    d = pd.concat([pd.read_parquet(f, filters=[('src_kind', '=', 'title')]) for f in fs]); d = d[d.paper_id.isin(pids)]
    out, raw = {}, {}
    sets = {'author_all': (d.target == 'author'), 'author_surname_first': (d.target == 'author') & (d.ans_role == 'surname_first'),
            'author_given_first': (d.target == 'author') & (d.ans_role == 'given_first'), 'author_initial_first': (d.target == 'author') & (d.ans_role == 'initial_first'),
            'year_all': (d.target == 'year'), 'year_informative': (d.target == 'year') & d.ans_j.isin([3, 4]), 'field_all': (d.target == 'field')}
    for nm, m in sets.items():
        g = d[m].groupby(['paper_id', 'who', 'layer']).nlr.mean().unstack('who')
        D = (g['self'] - g['partner']).unstack('layer'); P = g['partner'].unstack('layer'); S = g['self'].unstack('layer')
        for l in LAY:
            out[f'{nm}@{l}'] = D[l]; raw[f'{nm}@partner@{l}'] = P[l]; raw[f'{nm}@self@{l}'] = S[l]
    yt = d[d.target == 'year'].groupby(['ans_j', 'who', 'layer']).nlr.mean().unstack('who'); yt['D'] = yt['self'] - yt['partner']
    nf = sorted((ROOT / 'raw/b2_pscope').glob('none_*.parquet')); n = pd.concat([pd.read_parquet(f) for f in nf]); n = n[n.paper_id.isin(pids)]
    return pd.DataFrame(out).reindex(pids), pd.DataFrame(raw).reindex(pids), yt.reset_index(), n


# ------------------------------------------------------------------ embeddings
def embeddings(papers):
    cache = OUT / 'emb.npz'
    if cache.exists():
        z = np.load(cache); return z['bert'], z['mpnet']
    import torch, transformers
    t = list(papers.title.fillna('')); bt = transformers.AutoTokenizer.from_pretrained('bert-base-uncased'); bm = transformers.AutoModel.from_pretrained('bert-base-uncased').eval(); E = []
    with torch.inference_mode():
        for i in range(0, len(t), 64):
            e = bt(t[i:i + 64], padding=True, truncation=True, max_length=64, return_tensors='pt'); h = bm(**e).last_hidden_state; m = e.attention_mask[..., None].float()
            E.append(((h * m).sum(1) / m.sum(1)).numpy())
    E = np.concatenate(E)
    from sentence_transformers import SentenceTransformer
    M = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cpu').encode(t, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    np.savez(cache, bert=E, mpnet=M); return E, M


def unit(X): X = X - X.mean(0); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)


def surnames(a): return {x.split()[-1].lower() for x in str(a).split('; ') if x.strip()}


def topic_partners(papers, team_all, U, ids):
    """for each A: same field, max cosine, not A's team, no shared surname"""
    pos = {p: i for i, p in enumerate(papers.paper_id)}; field = papers.field.to_numpy(); sur = [surnames(a) for a in papers.authors]
    res = {}
    for p in ids:
        i = pos[p]; cand = np.where((field == field[i]) & (team_all != team_all[i]))[0]
        s = U[cand] @ U[i]; order = np.argsort(-s)
        for j in order:
            c = cand[j]
            if not (sur[c] & sur[i]): res[p] = (papers.paper_id.iloc[c], float(s[j])); break
    return res


# ------------------------------------------------------------------ stats
class Boot:
    def __init__(s, teams):
        codes, uniq = pd.factorize(pd.Series(teams)); s.W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]

    def mean(s, x, mask=None):
        ok = np.isfinite(x) & (True if mask is None else mask); W = s.W[:, ok]; v = x[ok]; b = (W @ v) / W.sum(1)
        return v.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), int(ok.sum())

    def zstat(s, x, mask=None):
        """standardised mean (mean/sd) with its bootstrap"""
        ok = np.isfinite(x) & (True if mask is None else mask); W = s.W[:, ok]; v = x[ok]; n = W.sum(1)
        m = (W @ v) / n; sd = np.sqrt(np.maximum((W @ v ** 2) / n - m ** 2, 1e-12)); return v.mean() / v.std(), m / sd

    def tc(s, x, grp, cbin, mask=None):
        ok = np.isfinite(x) & (True if mask is None else mask); x, grp, cbin, W = x[ok], grp[ok], cbin[ok], s.W[:, ok]
        num = np.zeros(NB); den = np.zeros(NB); pnum = pden = 0.0
        for b in np.unique(cbin):
            it, ic = (cbin == b) & (grp == 'target'), (cbin == b) & (grp == 'control')
            if it.sum() < 3 or ic.sum() < 3: continue
            nt, nc = W[:, it].sum(1), W[:, ic].sum(1); mt = (W[:, it] @ x[it]) / np.maximum(nt, 1e-9); mc = (W[:, ic] @ x[ic]) / np.maximum(nc, 1e-9)
            w = nt * nc / np.maximum(nt + nc, 1e-9); num += w * (mt - mc); den += w
            w0 = it.sum() * ic.sum() / (it.sum() + ic.sum()); pnum += w0 * (x[it].mean() - x[ic].mean()); pden += w0
        if pden == 0: return np.nan, np.nan, np.nan, int(ok.sum())   # no citation bin with >= 3 target and >= 3 control papers
        b = num / np.maximum(den, 1e-9); return pnum / pden, np.percentile(b, 2.5), np.percentile(b, 97.5), int(ok.sum())


def fm(t): return f'{t[0]:+.4f} [{t[1]:+.4f}, {t[2]:+.4f}]'


# ------------------------------------------------------------------ text models
def text_models(papers, folds, feats, targets, pairs_by_kind, ia_pos):
    """LR from title features to an answer class; returns {(feat, target, kind): D_text per X4 paper} and positive control"""
    from sklearn.linear_model import LogisticRegression
    res, pc = {}, []
    for feat, X in feats.items():
        for tname, y_all, C in targets:
            lp_self = np.full(len(ia_pos), np.nan); lp_part = {k: np.full(len(ia_pos), np.nan) for k in pairs_by_kind}; llm, llp = [], []
            for k in range(5):
                tr, te = (folds != k) & (y_all >= 0), (folds == k) & (y_all >= 0)
                vc = pd.Series(y_all[tr]).value_counts(); kept = set(vc[vc >= 5].index); oov = vc[vc < 5]; poov = (oov / oov.sum()).to_dict() if len(oov) else {}
                ytr = np.where(np.isin(y_all[tr], list(kept)), y_all[tr], -1); prior = pd.Series(ytr).value_counts(normalize=True).to_dict()
                md = LogisticRegression(C=C, max_iter=400).fit(X[tr], ytr); col = {c: i for i, c in enumerate(md.classes_)}

                def lp(Xr, ys):
                    P = md.predict_proba(Xr); o = np.array([P[i, col[t]] if t in kept else P[i, col[-1]] * poov.get(t, 1e-4) for i, t in enumerate(ys)]); return np.log10(np.clip(o, 1e-12, None))
                if te.any():
                    llm.append(lp(X[te], y_all[te])); llp.append(np.log10(np.clip([prior.get(t, 0) if t in kept else prior.get(-1, 1e-9) * poov.get(t, 1e-4) for t in y_all[te]], 1e-12, None)))
                sel = (folds[ia_pos] == k) & (y_all[ia_pos] >= 0)
                if sel.any():
                    ya = y_all[ia_pos[sel]]; lp_self[sel] = lp(X[ia_pos[sel]], ya)
                    for kind, ip in pairs_by_kind.items():
                        s2 = sel & (ip >= 0)
                        if s2.any(): lp_part[kind][s2] = lp(X[ip[s2]], y_all[ia_pos[s2]])
            m, p = np.concatenate(llm), np.concatenate(llp); pc.append(dict(features=feat, target=tname, C=C, n=len(m), loglik_model=m.mean(), loglik_prior=p.mean(), gain=(m - p).mean()))
            for kind in pairs_by_kind: res[(feat, tname, kind)] = lp_self - lp_part[kind]
    return res, pd.DataFrame(pc)


# ------------------------------------------------------------------ literal flags
EPO_RE = [re.compile(r"\b[A-Z][a-z]+'s\b"), re.compile(r"\b[A-Z][a-z]{2,}[-–][A-Z][a-z]{2,}\b")]


def flags(papers, ids, tok, sf_tok):
    P = papers.set_index('paper_id'); allsur = set()
    for a in papers.authors: allsur |= {s for s in surnames(a) if len(s) >= 4 and s.isalpha()}
    lower_words = set()
    for t in papers.title.fillna(''): lower_words |= {w for w in re.findall(r"[A-Za-z]+", t) if w.islower()}
    rows = []
    for p in ids:
        t = str(P.loc[p].title); words = [w for w in re.findall(r"[A-Za-z]+", t)]; wl = {w.lower() for w in words}
        a = any(s in wl for s in surnames(P.loc[p].authors) if len(s) >= 3)
        ttok = set(tok.encode(t, add_special_tokens=False)) | set(tok.encode(' ' + t, add_special_tokens=False))
        st = sf_tok.get(p); sstr = tok.decode([int(st)]).strip().lower() if st is not None and st >= 0 else ''
        b = bool(st is not None and (int(st) in ttok or (len(sstr) >= 3 and sstr in {tok.decode([x]).strip().lower() for x in ttok})))
        cap = [w for w in words[1:] if w[0].isupper() and w[1:].islower() and len(w) >= 4]
        c = any(w.lower() in allsur and w.lower() not in lower_words for w in cap) or any(r.search(t) for r in EPO_RE)
        rows.append(dict(paper_id=p, a_surname_in_title=a, b_surname_token_in_title=b, c_eponym=c))
    return pd.DataFrame(rows).set_index('paper_id')


def main():
    t0 = time.time()
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').reset_index(drop=True)
    folds, team_all = c13.group_folds(papers.paper_id.to_numpy())
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet'); pairs = pairs.merge(papers[['paper_id', 'citation_bin']], on='paper_id')
    if TINY:
        pairs = pairs.sample(80, random_state=0)
        keep = set(pairs.paper_id) | set(pairs.partner) | set(papers.sample(1500, random_state=0).paper_id)
        sub = papers.paper_id.isin(keep).to_numpy(); papers = papers[sub].reset_index(drop=True); folds, team_all = folds[sub], team_all[sub]
    ids = pairs.paper_id.tolist(); pos = {p: i for i, p in enumerate(papers.paper_id)}
    log('papers', len(papers), 'x4', len(ids))
    D, RAW, YT, NONE = qwen_D(ids); log('qwen D loaded', D.shape)
    chk = dict(D_all_L8=float(D['author_all@8'].mean()), D_sf_L8=float(D['author_surname_first@8'].mean()), D_all_L40=float(D['author_all@40'].mean()),
               published=dict(D_all_L8=0.04843, D_sf_L8=0.06634, D_all_L40=0.06941))
    E, M = embeddings(papers); log('embeddings', E.shape, M.shape)
    Ub, Um = unit(E), M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    tp = {'bert': topic_partners(papers, team_all, Ub, ids), 'mpnet': topic_partners(papers, team_all, Um, ids)}
    ia = np.array([pos[p] for p in ids]); ipc = np.array([pos.get(q, -1) for q in pairs.partner])
    cos_cur = {'bert': np.array([Ub[i] @ Ub[j] if j >= 0 else np.nan for i, j in zip(ia, ipc)]), 'mpnet': np.array([Um[i] @ Um[j] if j >= 0 else np.nan for i, j in zip(ia, ipc)])}
    ipt = {k: np.array([pos[tp[k][p][0]] for p in ids]) for k in tp}; cos_top = {k: np.array([tp[k][p][1] for p in ids]) for k in tp}
    pd.DataFrame({'paper_id': ids, 'partner': pairs.partner.values, 'cos_bert_cur': cos_cur['bert'], 'cos_mpnet_cur': cos_cur['mpnet'],
                  'topic_bert': [tp['bert'][p][0] for p in ids], 'cos_bert_topic': cos_top['bert'], 'topic_mpnet': [tp['mpnet'][p][0] for p in ids], 'cos_mpnet_topic': cos_top['mpnet']}).to_csv(OUT / 'partners.csv', index=False)
    bs = Boot(pairs.team.to_numpy()); grp = pairs.group.to_numpy(); cbin = pairs.citation_bin.astype(str).to_numpy()
    L = [f'# X4 L8 surname signal: where does it come from? — {LABEL}', '',
         f'{len(ids)} X4 papers (Stage 11 sample with a cached partner); cohort {len(papers):,} titles for embeddings/text models; team bootstrap {NB} draws (seed {SEED}), teams = pairs.parquet. Qwen D = mean over answer tokens of log10(1/rank), self source − partner source, source = last title token (cached raw/b2_pscope). Reproduction of published D: all L8 {chk["D_all_L8"]:+.4f} (pub +0.0484), surname-first L8 {chk["D_sf_L8"]:+.4f} (pub +0.0663), all L40 {chk["D_all_L40"]:+.4f} (pub +0.0694).', '']

    # ---- 1. partners
    L += ['## 1. Topic-matched partners', '', 'Cached partner = same field, same title token count, no shared surname (random within those). Topic-matched = same field, highest title cosine, other author team, no shared surname.', '',
          '| embedding | cos(A, cached partner) mean [p10, p90] | cos(A, topic partner) mean [p10, p90] | share of cached partners at least as close as the median topic partner |', '|---|---|---|---|']
    for k in ('bert', 'mpnet'):
        c, t = cos_cur[k], cos_top[k]; L.append(f'| {k} | {np.nanmean(c):.3f} [{np.nanpercentile(c, 10):.3f}, {np.nanpercentile(c, 90):.3f}] | {t.mean():.3f} [{np.percentile(t, 10):.3f}, {np.percentile(t, 90):.3f}] | {np.nanmean(c >= np.median(t)):.3f} |')
    L += ['', '**Qwen D with the topic-matched partner is not computable from cache** (it needs A\'s answer scored from the topic partner\'s state). Cost of the direct run: per paper one authors-prompt forward of the partner (7 layers recorded) + 3 targets × 1 position × 7 patched layers (batched) — about 45 s per 50-paper shard on one A100-80GB (cached X4 runs: 63–85 s per shard for self + partner, two positions); 24 shards × 2 embeddings ≈ 0.6 GPU-h + model loading ≈ 1 GPU-h total. Not run.', '',
          '### Proxy: Qwen D against how similar the cached partner already is', '', 'Per-paper D regressed on cos(A, cached partner); slope with team CI; "D at topic similarity" = intercept + slope × mean topic-partner cosine (extrapolation beyond most of the observed range; a model-based proxy, not a measurement).', '',
          '| D | embedding | low tercile | mid | high tercile | slope per 0.1 cos [CI] | D at mean topic cos [CI] |', '|---|---|---|---|---|---|---|']
    prox = []
    for col in ('author_surname_first@8', 'author_all@8', 'author_surname_first@40', 'author_all@40', 'year_informative@40', 'year_all@40'):
        y = D[col].to_numpy()
        for k in ('bert', 'mpnet'):
            x = cos_cur[k]; ok = np.isfinite(x) & np.isfinite(y); q = np.nanpercentile(x[ok], [33.3, 66.7])
            ters = [y[ok & (x <= q[0])].mean(), y[ok & (x > q[0]) & (x <= q[1])].mean(), y[ok & (x > q[1])].mean()]
            W = bs.W[:, ok]; xx, yy = x[ok], y[ok]; n = W.sum(1); mx = (W @ xx) / n; my = (W @ yy) / n
            sl = ((W @ (xx * yy)) / n - mx * my) / np.maximum((W @ xx ** 2) / n - mx ** 2, 1e-12); it_ = my - sl * mx; pred = it_ + sl * cos_top[k].mean()
            b1, b0 = np.polyfit(xx, yy, 1); p0 = b0 + b1 * cos_top[k].mean()
            prox.append(dict(D=col, emb=k, ter_low=ters[0], ter_mid=ters[1], ter_high=ters[2], slope01=b1 * 0.1, slope_lo=np.percentile(sl, 2.5) * 0.1, slope_hi=np.percentile(sl, 97.5) * 0.1,
                             pred=p0, pred_lo=np.percentile(pred, 2.5), pred_hi=np.percentile(pred, 97.5), D_mean=yy.mean()))
            L.append(f'| {col} | {k} | {ters[0]:+.4f} | {ters[1]:+.4f} | {ters[2]:+.4f} | {b1 * 0.1:+.4f} [{np.percentile(sl, 2.5) * 0.1:+.4f}, {np.percentile(sl, 97.5) * 0.1:+.4f}] | {p0:+.4f} [{np.percentile(pred, 2.5):+.4f}, {np.percentile(pred, 97.5):+.4f}] |')
    pd.DataFrame(prox).to_csv(OUT / 'proxy_similarity.csv', index=False); log('part 1 done')

    # ---- 2. text baseline
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'role', 'token_id']); first = nt[nt.author_index == 0]
    tok_of = {r: first[first.role == r].drop_duplicates('paper_id').set_index('paper_id').token_id for r in ('given_first', 'surname_first')}
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    Tf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit_transform(papers.title.fillna('')); S = TruncatedSVD(min(300, Tf.shape[1] - 1), random_state=0).fit_transform(Tf)
    feats = {'bert': (E - E.mean(0)) / (E.std(0) + 1e-6), 'tfidf_svd': (S - S.mean(0)) / (S.std(0) + 1e-6)}
    yv = papers.year.fillna(-1).astype(int).to_numpy()
    targets = [('surname_first', papers.paper_id.map(tok_of['surname_first']).fillna(-2).astype(int).to_numpy(), 0.03),
               ('given_first', papers.paper_id.map(tok_of['given_first']).fillna(-2).astype(int).to_numpy(), 0.03), ('year', yv, 0.03)]
    kinds = {'cached': ipc, 'topic_bert': ipt['bert'], 'topic_mpnet': ipt['mpnet']}
    TX, PC = text_models(papers, folds, feats, targets, kinds, ia); PC.to_csv(OUT / 'text_posctrl.csv', index=False); log('text models done')
    L += ['', '## 2. Text-only baseline in the same design', '', 'Logistic regression from title features (bert-base-uncased mean-pooled; TF-IDF 1–2-gram SVD-300) to the first author\'s surname-first / given-first Qwen token and to the publication year (classes seen ≥ 5 times, rest OOV), 5 folds by author team, C = 0.03 (as x4_textbase2). D_text = log10 p(answer | own title) − log10 p(answer | partner title), units log10 p.', '',
          '### Positive control (held-out log-likelihood vs frequency prior)', '', '| features | target | n | model | prior | gain |', '|---|---|---|---|---|---|']
    for r in PC.itertuples(): L.append(f'| {r.features} | {r.target} | {r.n} | {r.loglik_model:.3f} | {r.loglik_prior:.3f} | {r.gain:+.3f} |')
    L += ['', '### D_text by partner type (mean [team CI]; mean/sd)', '', '| features | answer | cached partner | topic partner (bert) | topic partner (mpnet) |', '|---|---|---|---|---|']
    trows = []
    for feat in feats:
        for tname, _, _ in targets:
            cells = []
            for kind in kinds:
                x = TX[(feat, tname, kind)]; m = bs.mean(x); z = bs.zstat(x); cells.append(f'{fm(m)}; {z[0]:+.2f}')
                tcv = bs.tc(x, grp, cbin); trows.append(dict(source=f'text_{feat}', answer=tname, partner=kind, mean=m[0], lo=m[1], hi=m[2], n=m[3], z=z[0], tc=tcv[0], tc_lo=tcv[1], tc_hi=tcv[2]))
            L.append(f'| {feat} | {tname} | ' + ' | '.join(cells) + ' |')
    L += ['', '### Standardised comparison, cached partner (Qwen units log10(1/rank), text units log10 p, so compare mean/sd; difference with team CI)', '',
          '| Qwen D | text D | Qwen mean/sd | text mean/sd | Qwen − text [CI] |', '|---|---|---|---|---|']
    for qcol, tk in (('author_surname_first@8', ('bert', 'surname_first')), ('author_surname_first@40', ('bert', 'surname_first')), ('author_given_first@8', ('bert', 'given_first')),
                     ('year_informative@40', ('bert', 'year')), ('year_all@40', ('bert', 'year')), ('year_informative@8', ('bert', 'year'))):
        q = D[qcol].to_numpy(); t = TX[(tk[0], tk[1], 'cached')]; ok = np.isfinite(q) & np.isfinite(t)
        zq, bq = bs.zstat(q, ok); zt, bt_ = bs.zstat(t, ok); dd = bq - bt_
        L.append(f'| {qcol} | text {tk[0]} {tk[1]} | {zq:+.3f} | {zt:+.3f} | {zq - zt:+.3f} [{np.percentile(dd, 2.5):+.3f}, {np.percentile(dd, 97.5):+.3f}] |')
    log('part 2 done')

    # ---- 3. target - control
    L += ['', '## 3. Target − control within citation bins (team CI)', '', '| measure | L8 | L16 | L24 | L32 | L40 | L48 |', '|---|---|---|---|---|---|---|']
    qrows = []
    for nm in ('author_all', 'author_surname_first', 'author_given_first', 'author_initial_first', 'year_all', 'year_informative', 'field_all'):
        cells = []
        for l in LAY[:-1]:
            x = D[f'{nm}@{l}'].to_numpy(); m = bs.mean(x); tcv = bs.tc(x, grp, cbin); cells.append(fm(tcv))
            qrows.append(dict(source='qwen', answer=nm, layer=l, mean=m[0], lo=m[1], hi=m[2], n=m[3], tc=tcv[0], tc_lo=tcv[1], tc_hi=tcv[2]))
        L.append(f'| Qwen {nm} | ' + ' | '.join(cells) + ' |')
    L += ['', '| text D (layer-free) | cached partner | topic (bert) | topic (mpnet) |', '|---|---|---|---|']
    for feat in feats:
        for tname, _, _ in targets:
            r = [x for x in trows if x['source'] == f'text_{feat}' and x['answer'] == tname]
            L.append(f'| {feat} {tname} | ' + ' | '.join(f"{x['tc']:+.4f} [{x['tc_lo']:+.4f}, {x['tc_hi']:+.4f}]" for x in r) + ' |')
    pd.DataFrame(qrows + trows).to_csv(OUT / 'D_all.csv', index=False); log('part 3 done')

    # ---- 4. literal flags
    import transformers
    qtok = transformers.AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
    F = flags(papers, ids, qtok, tok_of['surname_first'].to_dict()).reindex(ids); F.to_csv(OUT / 'literal_flags.csv')
    fa, fb, fc = F.a_surname_in_title.to_numpy(), F.b_surname_token_in_title.to_numpy(), F.c_eponym.to_numpy()
    L += ['', '## 4. Literal overlap', '', 'Rules: (a) a word of the title equals an author surname (lower-case, ≥ 3 letters); (b) the first author\'s surname-first Qwen token id, or its stripped lower-case string (≥ 3 chars), occurs among the title\'s Qwen tokens (title tokenised with and without a leading space); (c) eponym: a capitalised non-initial title word of ≥ 4 letters that is a surname somewhere in the 9,108-paper cohort and never appears lower-case in any cohort title, or a possessive "Xxx\'s", or a capitalised hyphen pair "Xxx-Yyy".', '',
          f'Counts: (a) {int(fa.sum())}, (b) {int(fb.sum())}, (c) {int(fc.sum())}, any {int((fa | fb | fc).sum())} of {len(ids)}.', '',
          '| D | all papers | without (a) | without (a)+(b) | without (a)+(b)+(c) | T−C without (a)+(b)+(c) | D among flagged (any) |', '|---|---|---|---|---|---|---|']
    for col in ('author_surname_first@8', 'author_all@8', 'author_surname_first@40', 'author_all@40'):
        x = D[col].to_numpy(); cells = [fm(bs.mean(x)), fm(bs.mean(x, ~fa)), fm(bs.mean(x, ~(fa | fb))), fm(bs.mean(x, ~(fa | fb | fc))), fm(bs.tc(x, grp, cbin, ~(fa | fb | fc))), fm(bs.mean(x, fa | fb | fc))]
        L.append(f'| {col} | ' + ' | '.join(cells) + ' |')
    log('part 4 done')

    # ---- 5. readout difficulty
    L += ['', '## 5. Readout difficulty', '', 'No-patch score = the target prompt with the literal "X" (raw/b2_pscope none_*); partner score = A\'s answer read from another paper\'s state (a non-paper-specific source). Per-paper means of log10(1/rank) over answer tokens.', '',
          '| answer | no-patch mean (sd) | partner L8 mean (sd) | partner L40 mean (sd) | D/sd L8 | D/sd L40 | win L8 | win L40 |', '|---|---|---|---|---|---|---|---|']
    npm = NONE.groupby(['paper_id', 'target']).nlr.mean().unstack('target')
    for nm, tgt in (('author_all', 'author'), ('author_surname_first', None), ('year_all', 'year'), ('year_informative', None), ('field_all', 'field')):
        nps = f'{npm[tgt].mean():+.3f} ({npm[tgt].std():.3f})' if tgt else '-'
        p8, p40 = RAW[f'{nm}@partner@8'], RAW[f'{nm}@partner@40']; d8, d40 = D[f'{nm}@8'], D[f'{nm}@40']
        win = lambda d: np.nanmean(np.where(d > 0, 1, np.where(d < 0, 0, 0.5)))
        L.append(f'| {nm} | {nps} | {p8.mean():+.3f} ({p8.std():.3f}) | {p40.mean():+.3f} ({p40.std():.3f}) | {d8.mean() / d8.std():+.3f} | {d40.mean() / d40.std():+.3f} | {win(d8.to_numpy()):.3f} | {win(d40.to_numpy()):.3f} |')
    L += ['', 'Year answer tokens (position j in " YYYY"; partner-source mean log10(1/rank) and D, L8 / L40):', '', '| j | partner L8 | D L8 | partner L40 | D L40 |', '|---|---|---|---|---|']
    for j in sorted(YT.ans_j.unique()):
        a8 = YT[(YT.ans_j == j) & (YT.layer == 8)].iloc[0]; a40 = YT[(YT.ans_j == j) & (YT.layer == 40)].iloc[0]
        L.append(f'| {j} | {a8.partner:+.3f} | {a8.D:+.4f} | {a40.partner:+.3f} | {a40.D:+.4f} |')
    L += ['', 'Standardised D per layer (mean/sd) and earliest layer with a team CI above 0 (all papers):', '', '| answer | ' + ' | '.join(f'L{l}' for l in LAY) + ' | earliest |', '|---|' + '---|' * (len(LAY) + 1)]
    for nm in ('author_surname_first', 'author_all', 'year_informative', 'year_all', 'field_all'):
        zs, first_l = [], None
        for l in LAY:
            x = D[f'{nm}@{l}'].to_numpy(); m = bs.mean(x); zs.append(f'{np.nanmean(x) / np.nanstd(x):+.2f}')
            if first_l is None and m[1] > 0: first_l = l
        L.append(f'| {nm} | ' + ' | '.join(zs) + f' | {first_l} |')
    L += ['', f'Label: {LABEL}. Single model; partners are the cached X4 partners unless stated; text models are fit on the cohort excluding the held-out fold of A\'s team (the partner may be in training).']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n'); json.dump(chk, open(OUT / 'checks.json', 'w'), indent=1)
    print('\n'.join(L)); log('DONE', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
