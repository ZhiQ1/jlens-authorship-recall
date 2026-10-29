"""User request 2026-10-29 (item 4): text-only baseline for X4. How much of the patchscope first-author signal
(D = self - partner at the title, L8 +0.046) can the title WORDS explain?

Text model (no Qwen): k-nearest-neighbour over the titles of the whole cohort (9,108 papers), EXCLUDING every paper of
the same author team as A (team = stage13_cpu.group_folds), so the baseline can only use topic -> name associations,
never the author's other papers. Score of A's first-author surname given a title t:
    p(s | t) = (sum_{k in kNN(t)} sim_k [surname_k == s] + a * prior(s)) / (sum_k sim_k + a),  prior = cohort first-author surname freq
    D_text = log10 p(s_A | title_A) - log10 p(s_A | title_partner)        (same partner as X4)
Two representations: TF-IDF (word 1-2 grams) and bert-base-uncased (mean-pooled last layer). k = 50, a = 1.
Compared with Qwen's D at the title (L8 and L40): win rate (share self > partner), standardised effect mean/sd,
correlation of per-paper D_Qwen with D_text, mean D_Qwen where the text gives no advantage (D_text <= 0), and the
regression of D_Qwen on D_text (share of the mean explained = 1 - intercept / mean). Also target - control within bin.
Output: summary_x1x4/x4_textbase.csv, reports/x4_textbase.md"""
import importlib.util, re, unicodedata
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
OUT = ROOT / 'summary_x1x4'; K, ALPHA, NB = 50, 1.0, 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def surname(a):
    w = re.sub(r'[^a-z ]', ' ', unicodedata.normalize('NFKD', str(a)).encode('ascii', 'ignore').decode().lower()).split()
    return w[-1] if w else ''


def knn_scores(E, papers, team, rows, part_idx):
    """E: [n, d] unit-norm title embeddings; for each X4 row i: p(surname_A | title) for title = A and title = partner"""
    sur = papers.first_surname.to_numpy(); prior = pd.Series(sur).value_counts(normalize=True)
    out = np.zeros((len(rows), 2))
    for r, (ia, ip) in enumerate(zip(rows, part_idx)):
        s_a = sur[ia]; bad = team == team[ia]                      # never look at A's own team
        for c, it in enumerate((ia, ip)):
            sim = E @ E[it]; sim[bad] = -np.inf; sim[it] = -np.inf
            nn = np.argpartition(-sim, K)[:K]; w = np.clip(sim[nn], 0, None)
            p = (w[sur[nn] == s_a].sum() + ALPHA * prior.get(s_a, 1 / len(sur))) / (w.sum() + ALPHA)
            out[r, c] = np.log10(p)
    return out[:, 0] - out[:, 1]


def main():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').reset_index(drop=True)
    papers['first_surname'] = papers.authors.map(lambda a: surname(str(a).split('; ')[0]))
    _, team = c13.group_folds(papers.paper_id.to_numpy())
    pos = {p: i for i, p in enumerate(papers.paper_id)}
    zs = [np.load(f) for f in sorted((ROOT / 'raw/pscope').glob('shard_*.npz'))]
    ps = pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in ['paper_id', 'partner', 'author@self@title@8', 'author@partner@title@8', 'author@self@title@40', 'author@partner@title@40']})
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')[['paper_id', 'team', 'group']]
    ps = ps.merge(pairs, on='paper_id').merge(papers[['paper_id', 'citation_bin']], on='paper_id')
    ps['D8'] = ps['author@self@title@8'] - ps['author@partner@title@8']; ps['D40'] = ps['author@self@title@40'] - ps['author@partner@title@40']
    ia = ps.paper_id.map(pos).to_numpy(); ip = ps.partner.map(pos).to_numpy()
    from sklearn.feature_extraction.text import TfidfVectorizer
    T = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit_transform(papers.title.fillna('')).astype(np.float32)
    T = T.toarray(); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    ps['Dt_tfidf'] = knn_scores(T, papers, team, ia, ip); del T
    import torch, transformers
    tok = transformers.AutoTokenizer.from_pretrained('bert-base-uncased'); bert = transformers.AutoModel.from_pretrained('bert-base-uncased').eval(); E = []
    with torch.inference_mode():
        for i in range(0, len(papers), 64):
            e = tok(list(papers.title.fillna('').iloc[i:i + 64]), padding=True, truncation=True, max_length=64, return_tensors='pt')
            h = bert(**e).last_hidden_state; m = e.attention_mask[..., None].float(); E.append(((h * m).sum(1) / m.sum(1)).numpy())
    E = np.concatenate(E); E -= E.mean(0); E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
    ps['Dt_bert'] = knn_scores(E, papers, team, ia, ip)
    ps.to_csv(OUT / 'x4_textbase_perpaper.csv', index=False)
    codes, uniq = pd.factorize(ps.team); W = np.random.default_rng(41).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    def win(x): return np.mean(np.where(x > 0, 1, np.where(x < 0, 0, 0.5)))
    def ci_mean(x): b = (W @ x) / W.sum(1); return np.percentile(b, [2.5, 97.5])
    rows = []
    for col in ('D8', 'D40', 'Dt_tfidf', 'Dt_bert'):
        x = ps[col].to_numpy(); lo, hi = ci_mean(x)
        rows.append(dict(measure=col, mean=x.mean(), lo=lo, hi=hi, sd=x.std(), effect=x.mean() / x.std(), win_rate=win(x)))
    S = pd.DataFrame(rows)
    rel = []
    for q in ('D8', 'D40'):
        for t in ('Dt_tfidf', 'Dt_bert'):
            y, x = ps[q].to_numpy(), ps[t].to_numpy(); r = np.corrcoef(x, y)[0, 1]; b1, b0 = np.polyfit(x, y, 1)
            nohelp = y[x <= 0]
            rel.append(dict(qwen=q, text=t, corr=r, slope=b1, intercept=b0, share_explained=1 - b0 / y.mean(), n_text_no_help=len(nohelp),
                            qwen_mean_where_text_no_help=nohelp.mean(), qwen_mean_where_text_helps=y[x > 0].mean()))
    Rl = pd.DataFrame(rel)
    tc = []
    for col in ('D8', 'D40', 'Dt_tfidf', 'Dt_bert'):
        d = ps[['group', 'citation_bin']].assign(v=ps[col]).reset_index(drop=True); cells = []
        for _, g in d.groupby('citation_bin'):
            a, c = g.index[g.group == 'target'].to_numpy(), g.index[g.group == 'control'].to_numpy()
            if len(a) >= 10 and len(c) >= 10: cells.append((a, c))
        w = np.array([len(a) * len(c) / (len(a) + len(c)) for a, c in cells]); w /= w.sum(); x = d.v.to_numpy()
        est = sum(wi * (x[a].mean() - x[c].mean()) for wi, (a, c) in zip(w, cells)); bt = np.zeros(NB)
        for wi, (a, c) in zip(w, cells): bt += wi * ((W[:, a] @ x[a]) / W[:, a].sum(1) - (W[:, c] @ x[c]) / W[:, c].sum(1))
        tc.append(dict(measure=col, target_minus_control=est, lo=np.percentile(bt, 2.5), hi=np.percentile(bt, 97.5)))
    TC = pd.DataFrame(tc)
    pd.concat([S.assign(table='summary'), Rl.assign(table='relation'), TC.assign(table='target_minus_control')]).to_csv(OUT / 'x4_textbase.csv', index=False)
    f = lambda v: f'{v:+.3f}'
    L = ['# X4 text-only baseline (user request 2026-10-29, item 4)', '',
         f'{len(ps)} X4 papers. Text model: kNN (k={K}) over the 9,108 cohort titles, excluding A\'s own author team; score = log10 p(A\'s first-author surname | title); D_text = own title - partner title. Units differ from Qwen\'s D, so compare win rates, standardised effects and correlations.', '',
         '| measure | mean [team 95% CI] | sd | mean/sd | share self > partner |', '|---|---|---|---|---|']
    names = {'D8': 'Qwen patchscope, title, L8', 'D40': 'Qwen patchscope, title, L40', 'Dt_tfidf': 'text kNN, TF-IDF', 'Dt_bert': 'text kNN, BERT'}
    for r in S.itertuples(): L.append(f'| {names[r.measure]} | {f(r.mean)} [{f(r.lo)}, {f(r.hi)}] | {r.sd:.3f} | {r.effect:+.2f} | {r.win_rate:.3f} |')
    L += ['', '| Qwen | text | corr | share of Qwen mean explained by the text score (1 - intercept/mean) | Qwen mean where text gives no help (n) | Qwen mean where text helps |', '|---|---|---|---|---|---|']
    for r in Rl.itertuples(): L.append(f'| {names[r.qwen]} | {names[r.text]} | {r.corr:+.3f} | {r.share_explained:.2f} | {f(r.qwen_mean_where_text_no_help)} ({r.n_text_no_help}) | {f(r.qwen_mean_where_text_helps)} |')
    L += ['', '| measure | target - control within citation bin |', '|---|---|']
    for r in TC.itertuples(): L.append(f'| {names[r.measure]} | {f(r.target_minus_control)} [{f(r.lo)}, {f(r.hi)}] |')
    (ROOT / 'reports/x4_textbase.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nX4TEXT ANALYZED')


if __name__ == '__main__':
    main()
