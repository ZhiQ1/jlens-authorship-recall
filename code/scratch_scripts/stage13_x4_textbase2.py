"""X4 stronger text-only baseline (user request 2026-10-29: the kNN baseline failed its positive control).
Supervised: from the title text alone, predict the first author's Qwen name tokens that X4 scores (role given_first =
first token of the given name / initial, role surname_first = first token of the surname). Multinomial logistic
regression on (a) bert-base-uncased mean-pooled title embeddings, (b) TF-IDF 1-2 grams reduced to 300 dims (SVD).
Classes = token ids seen >= 5 times as that role among first authors; rarer tokens share one OOV class whose mass is
split by the training frequency. 5 folds by author team (stage13_cpu.group_folds); C picked on fold 0 by log-loss.
Positive control: held-out log10-likelihood of the true token must beat the frequency prior (the model has learned a
topic -> name association). X4 comparison: D_text = mean over the two roles of log10 p(tok | own title) -
log10 p(tok | partner title), the model being the fold in which A is held out (the partner may be in its training set;
that can only push D_text up). Output: summary_x1x4/x4_textbase2.csv, reports/x4_textbase2.md"""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
OUT = ROOT / 'summary_x1x4'; NB = 2000; MINC = 5; CS = (0.03, 0.3, 3.0)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def logp_matrix(model, X, classes_kept, y_tok, prior_oov):
    """log10 p(true token) for each row of X under model; OOV tokens get p(OOV) * their share of OOV training mass"""
    P = model.predict_proba(X); col = {c: i for i, c in enumerate(model.classes_)}
    out = np.empty(len(X))
    for i, t in enumerate(y_tok):
        if t in classes_kept: out[i] = P[i, col[t]]
        else: out[i] = P[i, col[-1]] * prior_oov.get(t, min(prior_oov.values()) if prior_oov else 1e-4)
    return np.log10(np.clip(out, 1e-12, None))


def main():
    from sklearn.linear_model import LogisticRegression
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').reset_index(drop=True); pos = {p: i for i, p in enumerate(papers.paper_id)}
    folds, team = c13.group_folds(papers.paper_id.to_numpy())
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'role', 'token_id'])
    first = nt[nt.author_index == 0]
    tok = {r: first[first.role == r].drop_duplicates('paper_id').set_index('paper_id').token_id for r in ('given_first', 'surname_first')}
    import torch, transformers
    bt = transformers.AutoTokenizer.from_pretrained('bert-base-uncased'); bm = transformers.AutoModel.from_pretrained('bert-base-uncased').eval(); E = []
    with torch.inference_mode():
        for i in range(0, len(papers), 64):
            e = bt(list(papers.title.fillna('').iloc[i:i + 64]), padding=True, truncation=True, max_length=64, return_tensors='pt')
            h = bm(**e).last_hidden_state; m = e.attention_mask[..., None].float(); E.append(((h * m).sum(1) / m.sum(1)).numpy())
    E = np.concatenate(E); E = (E - E.mean(0)) / (E.std(0) + 1e-6)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    T = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit_transform(papers.title.fillna(''))
    S = TruncatedSVD(300, random_state=0).fit_transform(T); S = (S - S.mean(0)) / (S.std(0) + 1e-6)
    zs = [np.load(f) for f in sorted((ROOT / 'raw/pscope').glob('shard_*.npz'))]
    ps = pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in ['paper_id', 'partner', 'author@self@title@8', 'author@partner@title@8', 'author@self@title@40', 'author@partner@title@40']})
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')[['paper_id', 'team', 'group']]
    ps = ps.merge(pairs, on='paper_id').merge(papers[['paper_id', 'citation_bin']], on='paper_id')
    ps['D8'] = ps['author@self@title@8'] - ps['author@partner@title@8']; ps['D40'] = ps['author@self@title@40'] - ps['author@partner@title@40']
    ia = ps.paper_id.map(pos).to_numpy(); ip = ps.partner.map(pos).to_numpy()
    rows_pc = []
    for feat, X in (('bert', E), ('tfidf_svd', S)):
        dsum = np.zeros(len(ps))
        for role in ('given_first', 'surname_first'):
            y_all = papers.paper_id.map(tok[role]).fillna(-2).astype(int).to_numpy()
            ll_model, ll_prior = np.full(len(papers), np.nan), np.full(len(papers), np.nan)
            lp_self, lp_part = np.full(len(ps), np.nan), np.full(len(ps), np.nan); bestC = None
            for k in range(5):
                tr, te = (folds != k) & (y_all >= 0), (folds == k) & (y_all >= 0)
                vc = pd.Series(y_all[tr]).value_counts(); kept = set(vc[vc >= MINC].index)
                oov = vc[vc < MINC]; prior_oov = (oov / oov.sum()).to_dict() if len(oov) else {}
                ytr = np.where(np.isin(y_all[tr], list(kept)), y_all[tr], -1)
                prior = (pd.Series(ytr).value_counts(normalize=True)).to_dict()
                if bestC is None:
                    sc = []
                    for C in CS:
                        md = LogisticRegression(C=C, max_iter=300).fit(X[tr], ytr)
                        sc.append(logp_matrix(md, X[te], kept, y_all[te], prior_oov).mean())
                    bestC = CS[int(np.argmax(sc))]
                md = LogisticRegression(C=bestC, max_iter=500).fit(X[tr], ytr)
                ll_model[te] = logp_matrix(md, X[te], kept, y_all[te], prior_oov)
                ll_prior[te] = [np.log10(max(prior.get(t, 0) if t in kept else prior.get(-1, 1e-9) * prior_oov.get(t, 1e-4), 1e-12)) for t in y_all[te]]
                sel = folds[ia] == k
                if sel.any():
                    ya = y_all[ia[sel]]
                    lp_self[sel] = logp_matrix(md, X[ia[sel]], kept, ya, prior_oov); lp_part[sel] = logp_matrix(md, X[ip[sel]], kept, ya, prior_oov)
            ok = ~np.isnan(ll_model)
            rows_pc.append(dict(features=feat, role=role, C=bestC, n=int(ok.sum()), loglik_model=np.nanmean(ll_model), loglik_prior=np.nanmean(ll_prior),
                                gain=np.nanmean(ll_model - ll_prior), win_vs_prior=float(np.nanmean((ll_model > ll_prior)[ok]))))
            ps[f'lp_{feat}_{role}'] = lp_self - lp_part; dsum += lp_self - lp_part
        ps[f'Dt2_{feat}'] = dsum / 2
    PC = pd.DataFrame(rows_pc); ps.to_csv(OUT / 'x4_textbase2_perpaper.csv', index=False)
    codes, uniq = pd.factorize(ps.team); W = np.random.default_rng(43).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    def ci(x): b = (W @ x) / W.sum(1); return np.percentile(b, [2.5, 97.5])
    def win(x): return np.mean(np.where(x > 0, 1, np.where(x < 0, 0, 0.5)))
    # positive control interval: gain over prior on the X4 papers' own held-out rows is not needed; cohort-level gain with team bootstrap
    L = ['# X4 stronger text-only baseline (supervised; user request 2026-10-29)', '',
         'Logistic regression from the title text to the first author\'s Qwen name tokens (first given-name token, first surname token), 5 folds by author team.', '',
         '## Positive control: does the text model beat the frequency prior on held-out papers?', '',
         '| features | role | C | papers | mean log10 p, model | mean log10 p, prior | gain | share of papers where model > prior |', '|---|---|---|---|---|---|---|---|']
    for r in PC.itertuples(): L.append(f'| {r.features} | {r.role} | {r.C} | {r.n} | {r.loglik_model:.3f} | {r.loglik_prior:.3f} | {r.gain:+.3f} | {r.win_vs_prior:.3f} |')
    L += ['', '## X4 papers: own title vs partner title (D, log10 p units for the text model)', '', '| measure | mean [team 95% CI] | mean/sd | share self > partner | corr with Qwen D(L8) | Qwen D(L8) where text gives no help |', '|---|---|---|---|---|---|']
    for col, nm in (('D8', 'Qwen patchscope L8'), ('D40', 'Qwen patchscope L40'), ('Dt2_bert', 'text LR, BERT'), ('Dt2_tfidf_svd', 'text LR, TF-IDF+SVD')):
        x = ps[col].to_numpy(); lo, hi = ci(x)
        extra = '' if col.startswith('D4') or col == 'D8' else f'{np.corrcoef(x, ps.D8)[0, 1]:+.3f} | {ps.D8[x <= 0].mean():+.3f} (n={int((x <= 0).sum())})'
        L.append(f'| {nm} | {x.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] | {x.mean() / x.std():+.2f} | {win(x):.3f} | ' + (extra if extra else '- | -') + ' |')
    for col in ('Dt2_bert', 'Dt2_tfidf_svd'):
        x = ps[col].to_numpy(); y = ps.D8.to_numpy(); b1, b0 = np.polyfit(x, y, 1)
        L.append(f'\nRegression of Qwen D(L8) on {col}: slope {b1:+.3f}, intercept {b0:+.3f} -> share of the Qwen mean explained by the text score {1 - b0 / y.mean():.2f}')
    (ROOT / 'reports/x4_textbase2.md').write_text('\n'.join(L) + '\n'); PC.to_csv(OUT / 'x4_textbase2_posctrl.csv', index=False)
    print('\n'.join(L)); print('\nX4TEXT2 ANALYZED')


if __name__ == '__main__':
    main()
