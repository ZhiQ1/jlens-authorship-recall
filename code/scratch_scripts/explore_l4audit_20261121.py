"""Exploratory (post hoc) audit of the L4 'text level' baseline of M3 / X5, CPU only, existing cache + offline models.
User request 2026-11-21 (coordinator relay). Results to the user only (no docs/decks/git).

1. Qwen L0 (token embedding of the last title token, computed from the embedding matrix without a forward pass):
   M3 transfer T (year, log citations, field), identity index I, X5 top-1 retrieval, with the published M3 / X5 code
   (stage13_m3_analyze.probes/scores/identity, stage13_v56_retrieval.retrieve), same folds, same team weights.
2. External text baselines with the same protocol, on the same three task prompts:
   bert-base-uncased: hidden state of the last title token in the full prompt, layers 0..12;
   all-mpnet-base-v2: (a) last title token, last layer; (b) mean-pooled sentence embedding of the full prompt.
   (all-mpnet was trained on S2ORC/SPECTER pairs, so it may know papers: sensitivity only.)
3. Stored Qwen values at L4 / L8 / L16 / L24 / L40 are read from summary_m3/m3_transfer.csv, m3_identity.csv and
   summary_x5/x5_retrieval.csv (not recomputed).
Output: 381_stage13/summary_explore_l4audit_20261121/ (report.md, l4audit.csv). --test: 600 papers, output *_test.
"""
import importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
TEST = '--test' in sys.argv
OUT = ROOT / ('summary_explore_l4audit_20261121' + ('_test' if TEST else '')); OUT.mkdir(parents=True, exist_ok=True)
HF = Path(os.environ.get('HF_HOME', '/scratch/zhang.zhiqi2/hf'))


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)


def load(path, name):
    argv = sys.argv; sys.argv = [argv[0]]            # the imported scripts read --test from argv at import
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    sys.argv = argv; return m


m3 = load(H / '13_stage13/stage13_m3_analyze.py', 'm3a'); x5 = load(H / '13_stage13/stage13_v56_retrieval.py', 'x5r')
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); s13 = load(H / '13_stage13/381_stage13.py', 's13cfg')
TASKS = s13.TASKS; TN = list(TASKS)


def snapshot(repo):
    d = HF / 'hub' / ('models--' + repo.replace('/', '--')) / 'snapshots'; return sorted(d.iterdir())[-1]


def title_span(prompt, title):
    a = prompt.index('titled "') + len('titled "'); return a, a + len(title)


def main():
    pids_all = np.load(ROOT / 'summary_m3/resid_cache_pids.npy')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id').loc[pids_all]
    idx = np.arange(len(pids_all))
    if TEST: idx = np.sort(np.random.default_rng(0).choice(len(pids_all), 600, replace=False))
    pids = pids_all[idx]; P = papers.loc[pids]; n = len(pids)
    folds, team = c13.group_folds(pids)
    fields = sorted(P.field.unique()); F = (P.field.to_numpy()[:, None] == np.array(fields)[None]).astype(float)
    Y = np.column_stack([P.year.to_numpy(float), np.log10(1 + P.citations.to_numpy(float)), F])
    codes, uniq = pd.factorize(pd.Series(team))
    W = np.random.default_rng(31).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=m3.NB).astype(float)[:, codes]
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet'); ix = {p: i for i, p in enumerate(pids)}
    q = pairs[(pairs.split == 'test') & pairs.paper_id.isin(ix)]; test_i = np.array([ix[p] for p in q.paper_id]); test_team = q.team.to_numpy()
    Wt_test = x5.weights(test_team, 561); Wt_all = x5.weights(team, 561)
    prompts = [[TASKS[t][0].format(t=ti) for t in TN] for ti in P.title]
    titles = list(P.title)
    log('papers', n, 'test set', len(test_i))

    reps = {}
    # ---- Qwen L0: embedding rows of the last title token (exactly as build() picks it)
    from transformers import AutoTokenizer
    qdir = snapshot('Qwen/Qwen3-32B'); qtok = AutoTokenizer.from_pretrained(qdir)
    tid = np.zeros((n, 3), dtype=np.int64)
    for i in range(n):
        for k, pr in enumerate(prompts[i]):
            e = qtok(pr, return_offsets_mapping=True); a, b = title_span(pr, titles[i])
            tp = [j for j, (x, y) in enumerate(e.offset_mapping) if x < b and y > a]; tid[i, k] = e.input_ids[tp[-1]]
    same_tok = float((tid[:, 0] == tid[:, 1]).mean()); same_tok2 = float((tid[:, 0] == tid[:, 2]).mean())
    log('last-title-token id equal across tasks: authors=year', same_tok, 'authors=field', same_tok2)
    from safetensors import safe_open
    wmap = json.load(open(qdir / 'model.safetensors.index.json'))['weight_map']; key = 'model.embed_tokens.weight'
    import torch
    with safe_open(str(qdir / wmap[key]), framework='pt') as f:
        E = f.get_tensor(key)
    uniq_ids = np.unique(tid); rows = E[torch.tensor(uniq_ids)].float().numpy(); del E
    pos_of = {t: j for j, t in enumerate(uniq_ids)}
    reps['qwen_L0'] = np.stack([rows[[pos_of[t] for t in tid[:, k]]] for k in range(3)], 1).astype(np.float32)
    # ties: at L0 every paper whose last title token id is shared by other papers has identical gallery vectors
    vc = pd.Series(tid[:, 0]).value_counts(); share = pd.Series(tid[:, 0]).map(vc)
    tv = pd.Series(tid[test_i, 0]).value_counts(); share_t = pd.Series(tid[test_i, 0]).map(tv)
    meta = dict(qwen_L0_same_token_authors_year=same_tok, qwen_L0_same_token_authors_field=same_tok2,
                qwen_L0_unique_last_token_share_all=float((share == 1).mean()), qwen_L0_expected_top1_random_ties_all=float((1 / share).mean()),
                qwen_L0_unique_last_token_share_test=float((share_t == 1).mean()), qwen_L0_expected_top1_random_ties_test=float((1 / share_t).mean()))
    log(meta)

    # ---- text baselines
    from transformers import AutoModel
    torch.set_num_threads(int(os.environ.get('SLURM_CPUS_PER_TASK', 8)))
    for repo, tag, layers_keep in (('bert-base-uncased', 'bert', list(range(13))), ('sentence-transformers/all-mpnet-base-v2', 'mpnet', [12])):
        d = snapshot(repo); tk = AutoTokenizer.from_pretrained(d); md = AutoModel.from_pretrained(d).eval()
        last = {l: np.zeros((n, 3, md.config.hidden_size), np.float32) for l in layers_keep}
        pooled = np.zeros((n, 3, md.config.hidden_size), np.float32)
        flat = [(i, k) for i in range(n) for k in range(3)]; bs = 64; t0 = time.time()
        for s in range(0, len(flat), bs):
            ch = flat[s:s + bs]; txt = [prompts[i][k] for i, k in ch]
            enc = tk(txt, return_offsets_mapping=True, padding=True, truncation=True, max_length=128, return_tensors='pt')
            off = enc.pop('offset_mapping').numpy()
            with torch.no_grad(): out = md(**enc, output_hidden_states=True)
            hs = out.hidden_states; m = enc['attention_mask'].unsqueeze(-1).float()
            pm = ((hs[-1] * m).sum(1) / m.sum(1)).numpy()
            for r, (i, k) in enumerate(ch):
                a, b = title_span(txt[r], titles[i])
                tp = [j for j, (x, y) in enumerate(off[r]) if y > x and x < b and y > a]
                for l in layers_keep: last[l][i, k] = hs[l][r, tp[-1]].numpy()
                pooled[i, k] = pm[r]
        log(tag, 'encoded', f'{time.time() - t0:.0f}s')
        for l in layers_keep: reps[f'{tag}_last_L{l}'] = last[l]
        if tag == 'mpnet': reps['mpnet_prompt_meanpool'] = pooled

    rows = []
    for name, Xs in reps.items():
        t0 = time.time(); d_i = m3.identity(Xs); bI = (W @ d_i) / W.sum(1)
        Pr, _ = m3.probes(Xs, Y, folds); Tv = {}
        for tname, cols, kind in (('year', [0], 'r2'), ('log_citations', [1], 'r2'), ('field', list(range(2, Y.shape[1])), 'acc')):
            y = Y[:, cols] if kind == 'acc' else Y[:, cols[0]]
            g = lambda a, b_: Pr[a, b_][:, cols] if kind == 'acc' else Pr[a, b_][:, cols[0]]
            within = {b_: m3.scores(y, g(b_, b_), W, kind) for b_ in range(3)}
            re, rb = [], []
            for a in range(3):
                for b_ in range(3):
                    if a == b_: continue
                    cr = m3.scores(y, g(a, b_), W, kind); re.append(cr[0] / within[b_][0]); rb.append(cr[1] / within[b_][1])
            tb = np.mean(rb, 0); Tv[tname] = (float(np.mean(re)), *m3.ci(tb), float(np.mean([w[0] for w in within.values()])))
        hit_t, _ = x5.retrieve(Xs[test_i]); bt = (Wt_test @ hit_t) / Wt_test.sum(1)
        hit_a, _ = x5.retrieve(Xs); ba = (Wt_all @ hit_a) / Wt_all.sum(1)
        row = dict(rep=name, I=d_i.mean(), I_lo=m3.ci(bI)[0], I_hi=m3.ci(bI)[1],
                   ret_test=hit_t.mean(), ret_test_lo=x5.ci(bt)[0], ret_test_hi=x5.ci(bt)[1],
                   ret_all=hit_a.mean(), ret_all_lo=x5.ci(ba)[0], ret_all_hi=x5.ci(ba)[1])
        for t, v in Tv.items(): row.update({f'T_{t}': v[0], f'T_{t}_lo': v[1], f'T_{t}_hi': v[2], f'within_{t}': v[3]})
        rows.append(row); log(name, f"T year {row['T_year']:.3f} field {row['T_field']:.3f} ret_test {row['ret_test']:.3f} ({time.time() - t0:.0f}s)")
    D = pd.DataFrame(rows); D.to_csv(OUT / 'l4audit.csv', index=False); json.dump(meta, open(OUT / 'meta.json', 'w'), indent=1)
    log('DONE', OUT)


if __name__ == '__main__':
    main()
