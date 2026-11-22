"""Exploratory feasibility (post hoc), addendum 22 additions, CPU only. User request 2026-11-21 via coordinator.
Meaning twins: real cohort papers whose titles mean nearly the same, with no shared author and different author teams.
Selection (reproducible, threshold-free): pairs that are MUTUAL nearest neighbours by title embedding in BOTH
bert-base-uncased (mean-pooled last layer) and all-mpnet-base-v2 (sentence-transformers mean pooling, normalised), after
excluding every pair sharing any author full name (normalised) or the same author team (stage13_cpu.group_folds team).
Counts at cosine thresholds are also reported. Part (a): per-layer Qwen last-title-token similarity (authors prompt, M3 task
cache; centred cosine with the layer mean over all 9,108 papers) for twins vs X3 paraphrase (para_run) vs X3 lexical
neighbour D vs random pairs; team bootstrap over the anchor paper's team (2,000 draws).
Output: 381_stage13/summary_explore_twins_20261121/ (pairs.csv, sample20.csv, layer_similarity.csv, counts.json).
"""
import importlib.util, json, os, re, sys, time, glob
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT = B / '381_stage13'
OUT = ROOT / 'summary_explore_twins_20261121'; OUT.mkdir(parents=True, exist_ok=True)
HF = Path(os.environ.get('HF_HOME', '/scratch/zhang.zhiqi2/hf')); TEST = '--test' in sys.argv


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    argv = sys.argv; sys.argv = [argv[0]]
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); sys.argv = argv; return m


def snap(repo): return sorted((HF / 'hub' / ('models--' + repo.replace('/', '--')) / 'snapshots').iterdir())[-1]


def embed(repo, texts, norm):
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.set_num_threads(int(os.environ.get('SLURM_CPUS_PER_TASK', 8)))
    d = snap(repo); tk = AutoTokenizer.from_pretrained(d); md = AutoModel.from_pretrained(d).eval(); out = []
    for s in range(0, len(texts), 128):
        enc = tk(texts[s:s + 128], padding=True, truncation=True, max_length=64, return_tensors='pt')
        with torch.no_grad(): h = md(**enc).last_hidden_state
        m = enc['attention_mask'].unsqueeze(-1).float(); out.append(((h * m).sum(1) / m.sum(1)).numpy())
    E = np.concatenate(out).astype(np.float32)
    return E / np.linalg.norm(E, axis=1, keepdims=True) if norm else E


def norm_name(a): return re.sub(r'[^a-z ]', '', a.lower()).strip()


def main():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    pids = np.load(ROOT / 'summary_m3/resid_cache_pids.npy'); N = len(pids)
    P = pd.read_parquet(B / '351_stage10/cohort/papers.parquet').set_index('paper_id').loc[pids]
    n = 800 if TEST else N
    titles = list(P.title[:n]); _, team = c13.group_folds(pids); team = team[:n]
    auth = [set(norm_name(a) for a in s.split(';') if a.strip()) for s in P.authors[:n]]
    grp = P.group_tight.to_numpy()[:n]
    cos = {}
    for repo, tag in (('bert-base-uncased', 'bert'), ('sentence-transformers/all-mpnet-base-v2', 'mpnet')):
        E = embed(repo, titles, True); C = E @ E.T; np.fill_diagonal(C, -9); cos[tag] = C; log(tag, 'embedded')
    # exclusion mask: shared author or same team
    name_to = {}
    for i, s in enumerate(auth):
        for a in s: name_to.setdefault(a, []).append(i)
    bad = np.zeros((n, n), bool)
    for idx in name_to.values():
        if len(idx) > 1: ii = np.array(idx); bad[np.ix_(ii, ii)] = True
    tm = pd.Series(team);
    for idx in tm.groupby(tm).indices.values():
        if len(idx) > 1: bad[np.ix_(idx, idx)] = True
    for t in cos: cos[t][bad] = -9
    nn = {t: cos[t].argmax(1) for t in cos}
    mutual = [(i, int(nn['bert'][i])) for i in range(n) if i < nn['bert'][i] and nn['bert'][nn['bert'][i]] == i
              and nn['mpnet'][i] == nn['bert'][i] and nn['mpnet'][nn['mpnet'][i]] == i]
    rows = []
    for i, j in mutual:
        g = sorted([grp[i], grp[j]])
        rows.append(dict(a=pids[i], b=pids[j], title_a=titles[i], title_b=titles[j], cos_bert=float(cos['bert'][i, j]), cos_mpnet=float(cos['mpnet'][i, j]),
                         group_a=grp[i], group_b=grp[j], composition='both target' if g == ['target', 'target'] else 'both control' if g == ['control', 'control']
                         else 'mixed T/C' if g == ['control', 'target'] else 'other (excluded/guard)', cites_a=P.citations.iloc[i], cites_b=P.citations.iloc[j]))
    D = pd.DataFrame(rows).sort_values('cos_mpnet', ascending=False); D.to_csv(OUT / 'pairs.csv', index=False)
    counts = dict(n_papers=n, mutual_nn_both_models=len(D), composition=D.composition.value_counts().to_dict())
    for tb, tm_ in ((0.90, 0.80), (0.93, 0.85), (0.95, 0.90)):
        s = D[(D.cos_bert >= tb) & (D.cos_mpnet >= tm_)]
        counts[f'bert>={tb}&mpnet>={tm_}'] = dict(n=len(s), composition=s.composition.value_counts().to_dict())
    counts['all_pairs_quantiles'] = {t: {q: float(np.quantile(cos[t][np.triu_indices(n, 1)][::max(1, n // 50)], q)) for q in (0.5, 0.99, 0.9999)} for t in cos}
    log(counts)
    sel = D[(D.cos_bert >= 0.93) & (D.cos_mpnet >= 0.85)]
    smp = sel.sample(min(20, len(sel)), random_state=2211); smp.to_csv(OUT / 'sample20.csv', index=False)
    json.dump(counts, open(OUT / 'counts.json', 'w'), indent=1, default=str)
    if TEST: log('TEST done'); return
    # ---- part (a): Qwen title-state similarity per layer (authors prompt, last title token)
    X = np.memmap(ROOT / 'summary_m3/resid_cache.f16', np.float16, 'r', shape=(N, 3, 15, 2, 5120)); layers = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]
    ix = {p: i for i, p in enumerate(pids)}
    fs = sorted(glob.glob(str(ROOT / 'raw/para_run/shard_*.npz'))); PR = [np.load(f) for f in fs]
    para_ids = np.concatenate([z['paper_id'] for z in PR]); Dn = np.concatenate([z['lexical_neighbour'] for z in PR])
    Rp = np.concatenate([z['resid'][:, :, :, 0, :] for z in PR]).astype(np.float32)   # [n, version, layer, d] title_last
    rng = np.random.default_rng(22); rand_a = rng.choice(N, 3000, replace=False); rand_b = rng.permutation(rand_a)
    tw = np.array([[ix[a], ix[b]] for a, b in zip(sel.a, sel.b)]) if len(sel) else np.zeros((0, 2), int)
    twall = np.array([[ix[a], ix[b]] for a, b in zip(D.a, D.b)])
    pd_i = np.array([ix[p] for p in para_ids]); dn_i = np.array([ix[d] for d in Dn])
    codes = pd.Series(team).factorize()[0]; nt = codes.max() + 1
    Wdraw = np.random.default_rng(22).multinomial(nt, np.full(nt, 1 / nt), size=2000).astype(np.float32)
    out = []
    for li, l in enumerate(layers):
        S = np.asarray(X[:, 0, li, 0, :], dtype=np.float32); mu = S.mean(0); U = S - mu; U /= np.linalg.norm(U, axis=1, keepdims=True)
        def pc(a, b, Ua=None, Ub=None):
            ua = U[a] if Ua is None else Ua; ub = U[b] if Ub is None else Ub; return (ua * ub).sum(1)
        Vp = Rp[:, :, li, :] - mu; Vp /= np.linalg.norm(Vp, axis=2, keepdims=True)
        chk = float(np.abs(Rp[:, 0, li, :] - S[pd_i]).max())
        sets = {'twins (selected)': (pc(tw[:, 0], tw[:, 1]) if len(tw) else np.array([]), codes[tw[:, 0]] if len(tw) else np.array([], int)),
                'twins (all mutual NN)': (pc(twall[:, 0], twall[:, 1]), codes[twall[:, 0]]),
                'same paper paraphrase (X3)': ((Vp[:, 0] * Vp[:, 1]).sum(1), codes[pd_i]),
                'lexical neighbour D (X3)': (pc(pd_i, dn_i), codes[pd_i]),
                'random pairs': (pc(rand_a, rand_b), codes[rand_a])}
        for k, (v, cl) in sets.items():
            if len(v) == 0: continue
            W = Wdraw[:, cl]; b = (W @ v) / W.sum(1)
            out.append(dict(layer=l, set=k, n=len(v), mean_cos=float(v.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), para_run_vs_cache_maxabs=chk))
        log('layer', l, 'done')
    pd.DataFrame(out).to_csv(OUT / 'layer_similarity.csv', index=False); log('DONE', OUT)


if __name__ == '__main__':
    main()
