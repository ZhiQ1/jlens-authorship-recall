"""Stage 13 (CPU, existing outputs): what do the middle layers hold, if the lenses cannot read the name there?
(2026-10-28, user request: "not decodable by a lens" is not "absent".)

M1  What the lenses DO predict at the name positions. Stage 10 stored, for every name token, readout and layer, the top-1
    token. Classify it: the correct token; a name-like token (a token that starts some author name in the cohort);
    punctuation / list format; task words ("author", "paper", "et", "al", ...); a word copied from the prompt's title; other.
    Also: how often the top-1 changes when the true title is replaced by a false title (title-sensitivity of the readout
    even when it is wrong).
M2  Linear probes on the stored residuals (Stage 11 titlepos: last title token, layers 16-60; ':' position, layers 16-63;
    all 9,108 papers; true title and false_0 title). Targets that are NOT the author name:
      field (8 classes, accuracy); year (R^2; at the title token the year has not been read yet, so year must come from
      knowing the paper); log citations (R^2, "fame"); recognised = target vs control (AUROC within citation bin);
      first-author first token (E4b-style, at ':' as well as at the title token, for comparison).
    False_0 runs: the same probes with the donor paper's labels (the title in the prompt) vs the target paper's labels.
    5-fold CV by paper, ridge with alpha picked on fold 0; label-shuffle control for every target.
Outputs: /scratch/$USER/jlens/381_stage13/summary_cpu/*.csv, reports/stage13_cpu_report.md
"""
import importlib.util, json, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'; ROOT = BASE / '381_stage13'
H = Path.home() / 'jlens_work'; S = ROOT / 'summary_cpu'; S.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(3813); B = 1000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


TASK = {'author', 'authors', 'paper', 'papers', 'title', 'titled', 'et', 'al', 'by', 'published', 'journal', 'university', 'study',
        'and', 'the', 'of', 'in', 'who', 'are', 'is', 'was', 'were', 'written', 'name', 'names', 'unknown', 'none', 'n', 'a', 'an'}


def m1(s10):
    import transformers
    tok = transformers.AutoTokenizer.from_pretrained(s10.MODEL, revision=s10.REV)
    m, lenses = s10.verify(R10)
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id', 'role'])
    name_start = set(nt[nt.token_index == 0].token_id.unique())
    pr = pd.read_parquet(R10 / 'cohort/conditions/prompts.parquet', columns=['paper_id', 'condition', 'prompt_ids'])
    title_ids = {}
    for r in pr.itertuples(index=False):
        title_ids[(r.paper_id, r.condition)] = set(json.loads(r.prompt_ids)[8:-8])           # rough title span: drop the fixed template tokens
    vocab = {}
    def cls(t):
        if t not in vocab:
            s = tok.decode([int(t)]).strip().lower()
            vocab[t] = 'punct/format' if (not s or re.fullmatch(r'[\W_]+', s)) else ('task word' if s in TASK else None)
        return vocab[t]
    rows, tops = [], {}
    for cond in ('true', 'false_0', 'delete'):
        raw = s10.load_raw(R10, m, lenses, require_complete=True, cond=cond)
        d = raw.merge(nt, on='row_id'); del raw
        tops[cond] = d.set_index(['row_id', 'readout', 'layer']).top1
        tids = [title_ids.get((p, cond), set()) for p in d.paper_id]
        c = np.where(d['rank'].to_numpy() == 1, 'correct', None).astype(object)
        fixed = np.array([cls(t) for t in d.top1.to_numpy()], dtype=object)
        intitle = np.array([t in s for t, s in zip(d.top1.to_numpy(), tids)])
        isname = d.top1.isin(name_start).to_numpy()
        lab = np.where(c != None, c, np.where(isname, 'name-like', np.where(fixed != None, fixed, np.where(intitle, 'title word', 'other'))))
        d['cls'] = lab; d['first'] = d.token_index == 0
        for first in (True, False):
            sub = d[d['first']] if first else d
            t = sub.groupby(['readout', 'layer']).cls.value_counts(normalize=True).rename('share').reset_index()
            t['condition'] = cond; t['tokens'] = 'first token of each name' if first else 'all name tokens'; rows.append(t)
        log('M1', cond, len(d)); del d
    M1 = pd.concat(rows); M1.to_csv(S / 'M1_top1_classes.csv', index=False)
    a, b = tops['true'], tops['false_0']; j = a.to_frame('t').join(b.rename('f'), how='inner')
    ch = (j.t != j.f).groupby(level=['readout', 'layer']).mean().rename('share_top1_changes_true_vs_false').reset_index()
    ch.to_csv(S / 'M1_title_sensitivity.csv', index=False)
    return M1, ch


def ridge_cv(X, Y, folds, alphas=(0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)):
    """standardise on train folds; ridge (alpha scaled by trace/d) picked on fold 0; returns held-out predictions."""
    P = np.zeros_like(Y, dtype=float); best = None
    for k in np.unique(folds):
        tr, te = folds != k, folds == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; A = (X[tr] - mu) / sd; ym = Y[tr].mean(0)
        G = A.T @ A; Bm = A.T @ (Y[tr] - ym); I = np.eye(G.shape[0]); sc = np.trace(G) / G.shape[0]
        Xt = (X[te] - mu) / sd
        if best is None:
            errs = [(((Xt @ np.linalg.solve(G + a * sc * I, Bm) + ym) - Y[te]) ** 2).mean() for a in alphas]; best = alphas[int(np.argmin(errs))]
        P[te] = Xt @ np.linalg.solve(G + best * sc * I, Bm) + ym
    return P, best


def auroc(y, s):
    o = np.argsort(s); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def metric(kind, y, p, extra=None):
    if kind == 'acc': return float((p.argmax(1) == y.argmax(1)).mean())
    if kind == 'r2': return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    if kind == 'auc_bin':                                     # AUROC within citation bin, pooled by bin size
        bins = extra; out, w = [], []
        for b in np.unique(bins):
            i = bins == b
            if 10 <= y[i].sum() <= i.sum() - 10: out.append(auroc(y[i], p[i])); w.append(i.sum())
        return float(np.average(out, weights=w))


def boot(kind, y, p, extra=None):
    n = len(y); v = []
    for _ in range(200):
        i = rng.integers(0, n, n); v.append(metric(kind, y[i], p[i], None if extra is None else extra[i]))
    return np.percentile(v, [2.5, 97.5])


def m2(s10):
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    P = papers.set_index('paper_id')
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); donor = ft[ft.k == 0].set_index('paper_id').donor_paper_id
    def loadc(c):
        zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))]
        return np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]), zs[0]['probe_layers']
    fields = sorted(papers.field.unique()); rows = []
    for cond in ('true', 'false_0'):
        Xt, Xc, pid, pl = loadc(cond); log('M2 loaded', cond, Xt.shape, Xc.shape)
        lab_ids = pid if cond == 'true' else np.array([donor[p] for p in pid])          # the paper whose title is in the prompt
        L = P.loc[lab_ids]; T = P.loc[pid]
        y_field = np.eye(len(fields))[[fields.index(f) for f in L.field]]
        y_year = pd.to_numeric(L.year, errors='coerce').to_numpy(float)[:, None]
        y_cit = np.log10(pd.to_numeric(L.citations, errors='coerce').fillna(0).to_numpy(float) + 1)[:, None]
        grp = T.group_tight.to_numpy(); keep_r = np.isin(grp, ['target', 'control'])
        y_rec = (grp == 'target').astype(float)[:, None]; bins = T.citation_bin.to_numpy()
        folds = np.random.default_rng(13).integers(0, 5, len(pid))
        targets = [('field', 'acc', y_field, None, slice(None)), ('year', 'r2', y_year, None, ~np.isnan(y_year[:, 0])),
                   ('log citations', 'r2', y_cit, None, slice(None))]
        if cond == 'true': targets.append(('recognised (target vs control)', 'auc_bin', y_rec, bins, keep_r))
        for pos, X, layers in (('title', Xt, list(pl)), ('colon', Xc, list(pl) + [63])):
            for li, l in enumerate(layers):
                Xl = X[:, li].astype(np.float32)
                for name, kind, Y, extra, sel in targets:
                    Ys, Xs = Y[sel], Xl[sel]; ex = None if extra is None else extra[sel]; fs = folds[sel]
                    p, a = ridge_cv(Xs, Ys, fs)
                    yv = Ys if kind == 'acc' else Ys[:, 0]; pv = p if kind == 'acc' else p[:, 0]
                    v = metric(kind, yv, pv, ex); lo, hi = boot(kind, yv, pv, ex)
                    sh = np.random.default_rng(li).permutation(len(Ys)); ps, _ = ridge_cv(Xs, Ys[sh], fs)
                    vs = metric(kind, yv[sh], ps if kind == 'acc' else ps[:, 0], ex)
                    rows.append(dict(condition=cond, position=pos, layer=int(l), target=name, metric=kind, value=v, lo=lo, hi=hi, shuffled=vs, alpha=a, n=len(Ys)))
                log('M2', cond, pos, l, ' '.join(f"{r['target'][:6]}={r['value']:.3f}" for r in rows[-len(targets):]))
                pd.DataFrame(rows).to_csv(S / 'M2_probes.csv', index=False)
    return pd.DataFrame(rows)


def report(M1, ch, M2):
    L = ['# Stage 13 CPU: what the middle layers hold (existing outputs)', '']
    L += ['## M1. Top-1 token of the readout at the first token of each name (true title)', '']
    t = M1[(M1.condition == 'true') & (M1.tokens == 'first token of each name')].pivot_table(index=['readout', 'layer'], columns='cls', values='share').fillna(0)
    L += [t.round(3).to_string(), '']
    L += ['## M1b. Share of name tokens whose top-1 changes when the true title is replaced by false_0', '', ch.pivot(index='layer', columns='readout', values='share_top1_changes_true_vs_false').round(3).to_string(), '']
    L += ['## M2. Linear probes (5-fold CV by paper; 95% bootstrap CI; shuffled-label control)', '']
    for (cond, pos), g in M2.groupby(['condition', 'position']):
        L += [f'### {cond} title run, {pos} position', '', '| target | ' + ' | '.join(f'L{l}' for l in sorted(g.layer.unique())) + ' |', '|---' * (g.layer.nunique() + 1) + '|']
        for tname, h in g.groupby('target', sort=False):
            h = h.set_index('layer'); L.append(f'| {tname} ({h.metric.iloc[0]}) | ' + ' | '.join(f'{h.loc[l, "value"]:.3f} (sh {h.loc[l, "shuffled"]:.2f})' for l in sorted(g.layer.unique())) + ' |')
        L.append('')
    (ROOT / 'reports/stage13_cpu_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    s10 = load(H / '10_stage10/351_stage10.py', 's10')
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    M2 = m2(s10) if which in ('all', 'm2') else pd.read_csv(S / 'M2_probes.csv')
    M1, ch = m1(s10) if which in ('all', 'm1') else (pd.read_csv(S / 'M1_top1_classes.csv'), pd.read_csv(S / 'M1_title_sensitivity.csv'))
    report(M1, ch, M2)
