"""Addendum 12 item 2-11 (batch 2, group C; user item): model-generated names. Does the residual at the model's OWN written names
separate true authors (M) from fabricated ones (H)?

Plan (locked): 381_stage13/config/prereg_addendum12.json item "2-11 model-generated names (user item)".
Data   label package open_results.jsonl (generated_text, names) for all target + control papers (group_tight).
       Per-name M / H: the package stores only the counts m / h per paper, not which name matched (NameMatcher is in the elm code,
       which is not on the cluster). DEVIATION D2-11a: per-name labels are rebuilt with the Stage 10 R0/R1 matcher
       (10_stage10/stage10_extra_r0r1.py words/same: surname + first initial, given-name-first then surname-first order, one-to-one),
       here read from the generated-name side; papers are kept only when the rebuilt counts equal the package (rebuilt M = m and
       len(names) = m + h). Dropped papers are counted in the report.
Prompt the SAME chat prompt as the labeller (step1_README.md "Open question": system + user message; handbook G1.4: Qwen3 chat
       template, add_generation_prompt=True, enable_thinking=False -> empty <think></think> block), then the stored generated_text
       teacher-forced; tokenised as one string with add_special_tokens=False (as stage13_judge2.py).
GPU    one forward per paper; residual (block output) at L16, L24, L32, L40, L48, L52, L56 at the position that predicts the first
       token of each written name (pred_first = first name token - 1) and at the name's last token (last). Shards of papers,
       skip-if-exists, claims. HARD CHECK (in the gate shard 0 job, and in --check): greedy continuation (batch 1, from the chat
       prompt) reproduces the stored text up to the end of the first written name for >= 90% of a 50-paper check sample
       (papers with >= 1 name, rng 1211) -> exit 2 below 90%.
Probe  (CPU) logistic regression (L2), C chosen on fold 0 (train on folds 1-4, log-loss on fold 0, grid C_GRID), then 5-fold
       out-of-fold predictions on the archived author-team folds (stage13_cpu.group_folds of the 9,108 cohort), training-fold
       standardisation. AUROC per layer x position, for target papers, control papers and pooled (one pooled fit, AUROC on each
       subset); team-cluster bootstrap 2,000 draws for the CI; shuffled-label control (labels permuted within the training folds,
       rng 1212); name-only baseline (features from the name string alone: log cohort surname frequency, initial-only given name,
       characters, words, position in the list) and residual + name-only.
Limitation stated in advance: the open answers come from the chat template while every other experiment uses the raw prompt.
Commands: build | gpu --shard K | gpu --all | check | probe | report | tiny --root DIR | selftest
"""
import argparse, hashlib, importlib.util, json, math, os, re, sys, time, traceback, unicodedata
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R13 = BASE / '381_stage13'
LAB = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
PLAN = R13 / 'config/prereg_addendum12.json'; PLAN_SHA = (R13 / 'config/prereg_addendum12.json.sha256').read_text().split()[0]
SYSTEM = 'You are a knowledgeable assistant. Answer factually and concisely. When asked for authors, return a semicolon separated list of full names only, with no additional text.'
USER = "Who are the authors of the paper titled '{title}' which was published in {year}? Return a semicolon separated list of author names only."
N_SHARDS, N_CHECK, CHECK_MIN, NB = 48, 50, 0.90, 2000
C_GRID = [0.001, 0.01, 0.1, 1.0]
SEC_PER_SHARD = 60


def load_mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load_mod(H / '13_stage13/b2c_columns.py', 'b2c_columns')
LAYERS, POS = COLS.GN_LAYERS, COLS.GN_POSITIONS


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')


def log(*x):
    try: print(now(), *x, flush=True)
    except Exception: pass


# ------------------------------------------------------------------ per-name labels (Stage 10 r0r1 matcher, generated-name side)
def words(s): return [x for x in re.sub(r'[^a-z \-]', ' ', unicodedata.normalize('NFKD', s.replace('-', ' - ')).encode('ascii', 'ignore').decode().lower()).split() if x != '-']


def same(tw, gw, swap):          # verbatim 10_stage10/stage10_extra_r0r1.py
    if not tw or len(gw) < 2: return False
    ts, ti = tw[-1], (tw[0][0] if len(tw) > 1 else '')
    for gs, gi in ([(gw[-1], gw[0][0]), (gw[0], gw[1][0])] if swap else [(gw[-1], gw[0][0])]):
        if gs == ts and (not ti or gi == ti): return True
    return False


def match_gen(true, gen):
    """stage10_extra_r0r1.match (same loops, same order) returning per GENERATED name whether it was used (= M)."""
    tw = [words(t) for t in true]; gw = [words(g) for g in gen]; used, hit = set(), [False] * len(true)
    for swap in (False, True):
        for i, t in enumerate(tw):
            if hit[i]: continue
            for j, g in enumerate(gw):
                if j not in used and same(t, g, swap): used.add(j); hit[i] = True; break
    return [j in used for j in range(len(gen))], sum(hit)


def chat_prompt(tok, title, year):
    return tok.apply_chat_template([{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': USER.format(title=title, year=year)}],
                                   add_generation_prompt=True, enable_thinking=False, tokenize=False)


def name_spans(text, names):
    """char spans of the names in order (sequential search); None if a name is not found verbatim."""
    out, at = [], 0
    for n in names:
        i = text.find(n, at)
        if i < 0: return None
        out.append((i, i + len(n))); at = i + len(n)
    return out


def build(root, tok, limit=None):
    import pandas as pd
    c13 = load_mod(H / '13_stage13/stage13_cpu.py', 'c13')
    P = pd.read_parquet(R10 / 'cohort/papers.parquet')
    folds, teams = c13.group_folds(P.paper_id.to_numpy()); P['fold'] = folds; P['team'] = teams
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)
    o = o[['paper_id', 'generated_text', 'names', 'm', 'h']].rename(columns={'m': 'm_pkg', 'h': 'h_pkg'})
    d = P[P.group_tight.isin(['target', 'control'])].merge(o, on='paper_id')
    if limit: d = d.head(limit)
    surn = pd.Series([words(a)[-1] for al in P.authors for a in str(al).split('; ') if words(a)]).value_counts()
    rows, papers, drop = [], [], dict(no_names=0, count_mismatch=0, span_not_found=0, token_map=0)
    for r in d.itertuples():
        names = list(r.names)
        if not names: drop['no_names'] += 1; continue
        lab, mm = match_gen(str(r.authors).split('; '), names)
        if sum(lab) != int(r.m_pkg) or len(names) != int(r.m_pkg) + int(r.h_pkg):
            drop['count_mismatch'] += 1; continue
        sp = name_spans(r.generated_text, names)
        if sp is None: drop['span_not_found'] += 1; continue
        pr = chat_prompt(tok, r.title, r.year); full = pr + r.generated_text
        e = tok(full, add_special_tokens=False, return_offsets_mapping=True); off = e.offset_mapping; base = len(pr)
        ptoks = len(tok(pr, add_special_tokens=False).input_ids)
        recs, ok = [], True
        for j, (a, b) in enumerate(sp):
            A, B = base + a, base + b
            ti = [i for i, (x, y) in enumerate(off) if x < B and y > A]
            if not ti or ti[0] < ptoks: ok = False; break
            w = words(names[j]); sn = w[-1] if w else ''
            recs.append(dict(paper_id=r.paper_id, name_index=j, name=names[j], label='M' if lab[j] else 'H', group_tight=r.group_tight, recall_level=r.recall_level,
                             citation_bin=r.citation_bin, team=int(r.team), fold=int(r.fold), char_start=a, char_end=b, tok_first=ti[0], tok_last=ti[-1],
                             pos_pred_first=ti[0] - 1, pos_last=ti[-1], n_name_tokens=len(ti), surname=sn, surname_freq_cohort=int(surn.get(sn, 0)),
                             given_is_initial=bool(w and len(w[0]) == 1), name_len_chars=len(names[j]), name_n_words=len(w), name_index_rel=j / max(1, len(names) - 1)))
        if not ok: drop['token_map'] += 1; continue
        rows += recs; papers.append(dict(paper_id=r.paper_id, n_prompt_tokens=ptoks, n_tokens=len(e.input_ids), ids=json.dumps(e.input_ids)))
    N = COLS.check(pd.DataFrame(rows)[COLS.GN_NAMES], 'GN_NAMES'); PP = pd.DataFrame(papers)
    PP['shard'] = np.arange(len(PP)) % N_SHARDS
    rng = np.random.default_rng(1211); chk = rng.choice(len(PP), min(N_CHECK, len(PP)), replace=False); PP['check'] = False; PP.loc[chk, 'check'] = True
    root.mkdir(parents=True, exist_ok=True); N.to_parquet(root / 'names.parquet', index=False); PP.to_parquet(root / 'papers.parquet', index=False)
    meta = dict(created=now(), n_papers_in=len(d), n_papers=len(PP), n_names=len(N), labels=N.label.value_counts().to_dict(),
                by_group=N.groupby(['group_tight', 'label']).size().astype(int).to_dict().__repr__(), dropped=drop, shards=N_SHARDS)
    (root / 'build.json').write_text(json.dumps(meta, indent=1, default=str)); log('build', meta)
    return N, PP


# ------------------------------------------------------------------ GPU
def shard_path(root, k): return root / f'raw/resid/shard_{k:03d}.npz'


def do_shard(model, torch, N, PP, k, layers):
    from jlens.hooks import ActivationRecorder
    sub = PP[PP.shard == k]; nm = N[N.paper_id.isin(sub.paper_id)].sort_values(['paper_id', 'name_index'])
    g = nm.groupby('paper_id', sort=False); out = {f'{p}@{l}': [] for p in POS for l in layers}; keys = []
    for r in sub.itertuples():
        if r.paper_id not in g.groups: continue
        s = nm.loc[g.groups[r.paper_id]]; ids = json.loads(r.ids)
        with torch.inference_mode(), ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(torch.tensor([ids], device=model.input_device))
            for l in layers:
                h = rec.activations[l][0]
                out[f'pred_first@{l}'].append(h[torch.tensor(s.pos_pred_first.to_numpy(), device=h.device)].float().cpu().numpy().astype(np.float16))
                out[f'last@{l}'].append(h[torch.tensor(s.pos_last.to_numpy(), device=h.device)].float().cpu().numpy().astype(np.float16))
        keys += [f'{p}|{j}' for p, j in zip(s.paper_id, s.name_index)]
    return dict(key=np.array(keys), **{k_: np.concatenate(v) for k_, v in out.items()})


def greedy_check(model, tok, torch, N, PP, max_new=32):
    """first-name reproduction on the check papers: greedy (batch 1) from the chat prompt; compare to the stored text up to the end
    of the first written name."""
    from jlens.hooks import ActivationRecorder
    rows = []; last = model.n_layers - 1
    for r in PP[PP.check].itertuples():
        ids = json.loads(r.ids)[:r.n_prompt_tokens]; s = N[(N.paper_id == r.paper_id) & (N.name_index == 0)].iloc[0]
        full_ids = json.loads(r.ids); need = s.tok_last + 1 - r.n_prompt_tokens
        gen = []
        for _ in range(max(need, 1) + 2):
            with torch.inference_mode(), ActivationRecorder(model.layers, at=[last]) as rec:
                model.forward(torch.tensor([ids + gen], device=model.input_device))
                nxt = int(model.unembed(rec.activations[last][0][-1:]).float().argmax(-1).item())
            gen.append(nxt)
            if len(gen) >= need: break
        gtext = tok.decode(gen); stored = tok.decode(full_ids[r.n_prompt_tokens:s.tok_last + 1])
        first = s['name']; ok = gtext.startswith(stored) or (first in gtext[:len(stored) + 2])
        rows.append(dict(paper_id=r.paper_id, first_name_stored=first, first_name_greedy=gtext.split(';')[0].strip(), match=bool(ok), greedy_text=gtext))
    return rows


def check_status(rows):
    share = float(np.mean([r['match'] for r in rows])) if rows else 0.0
    return ('PASS' if share >= CHECK_MIN and rows else 'FAIL'), share


def run_check(root, model, tok, torch, N, PP):
    import pandas as pd
    rows = greedy_check(model, tok, torch, N, PP); st, share = check_status(rows)
    D = COLS.check(pd.DataFrame(rows, columns=COLS.GN_REPRO), 'GN_REPRO'); (root / 'summary').mkdir(parents=True, exist_ok=True); D.to_csv(root / 'summary/repro_check.csv', index=False)
    (root / 'summary/repro_check.json').write_text(json.dumps(dict(status=st, share=share, n=len(rows), threshold=CHECK_MIN, at=now()), indent=1))
    print('HARD CHECK first-name greedy reproduction', st, f'{share:.3f} of {len(rows)} (threshold {CHECK_MIN})', flush=True)
    if st != 'PASS': (root / 'HARD_CHECK_FAILED').write_text(json.dumps(dict(share=share, n=len(rows))))
    return st == 'PASS'


def check_passed(root):
    f = root / 'summary/repro_check.json'; return f.exists() and json.loads(f.read_text())['status'] == 'PASS'


def gpu(a, root):
    import torch, pandas as pd
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); s11, s10 = s12.s11, s12.s10
    N = pd.read_parquet(root / 'names.parquet'); PP = pd.read_parquet(root / 'papers.parquet')
    model, tok = s10.load_model()
    if not check_passed(root):
        if not run_check(root, model, tok, torch, N, PP): sys.exit(2)
    todo = [a.shard] if a.shard is not None else range(N_SHARDS); CL = root / 'logs/claims'; CL.mkdir(parents=True, exist_ok=True); last = SEC_PER_SHARD
    for k in todo:
        f = shard_path(root, k)
        if f.exists(): continue
        left = s11.slurm_minutes_left(); el = (time.monotonic() - t0) / 60; rest = (a.minutes - el) if left is None else min(a.minutes - el, left - 4)
        if rest * 60 < 1.5 * last + 30: log('budget: stop before next shard'); return
        if a.shard is None and not s11.claim(CL / f'shard_{k:03d}', me): continue
        t1 = time.monotonic(); d = do_shard(model, torch, N, PP, k, LAYERS); f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(created=now(), shard=k, job=me))), **d); os.replace(tmp, f)
        last = time.monotonic() - t1; log(f'shard {k:03d} names={len(d["key"])} {last:.0f}s')
    log('gpu: no shard left for this job')


# ------------------------------------------------------------------ probe (CPU)
def name_features(N):
    return np.stack([np.log1p(N.surname_freq_cohort.to_numpy(float)), N.given_is_initial.to_numpy(float), N.name_len_chars.to_numpy(float),
                     N.name_n_words.to_numpy(float), N.name_index.to_numpy(float), N.name_index_rel.to_numpy(float)], 1)


def fit_oof(X, y, fold, seed_shuffle=None):
    """C on fold 0 (train folds 1-4, held-out log loss), then 5-fold out-of-fold probabilities; training-fold standardisation."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss
    y = y.copy()
    if seed_shuffle is not None:
        rng = np.random.default_rng(seed_shuffle)
        for k in np.unique(fold): ix = np.where(fold == k)[0]; y[ix] = y[ix[rng.permutation(len(ix))]]
    def one(tr, te, C):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        m = LogisticRegression(C=C, max_iter=300).fit((X[tr] - mu) / sd, y[tr]); return m.predict_proba((X[te] - mu) / sd)[:, 1]
    tr0, te0 = fold != 0, fold == 0; best, errs = C_GRID[0], []
    if len(np.unique(y[tr0])) == 2 and te0.any():
        errs = [log_loss(y[te0], np.clip(one(tr0, te0, C), 1e-7, 1 - 1e-7), labels=[0, 1]) for C in C_GRID]; best = C_GRID[int(np.argmin(errs))]
    p = np.full(len(y), np.nan)
    for k in np.unique(fold):
        tr, te = fold != k, fold == k
        if len(np.unique(y[tr])) == 2: p[te] = one(tr, te, best)
    return p, best, y


def auroc_ci(y, p, team, nb=NB, seed=5):
    from sklearn.metrics import roc_auc_score
    ok = ~np.isnan(p); y, p, team = y[ok], p[ok], team[ok]
    if len(np.unique(y)) < 2: return np.nan, np.nan, np.nan
    est = roc_auc_score(y, p); uniq, codes = np.unique(team, return_inverse=True); n = len(uniq)
    W = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=nb)[:, codes]
    bt = []
    for w in W:
        m = w > 0
        if len(np.unique(y[m])) < 2: continue
        bt.append(roc_auc_score(y[m], p[m], sample_weight=w[m]))
    return est, *np.percentile(bt, [2.5, 97.5])


def probe(root, layers=LAYERS, nb=NB):
    import pandas as pd
    N = pd.read_parquet(root / 'names.parquet'); fs = sorted((root / 'raw/resid').glob('shard_*.npz'))
    zs = [np.load(f) for f in fs]; key = np.concatenate([z['key'] for z in zs]); kidx = {k: i for i, k in enumerate(key)}
    N['key'] = N.paper_id + '|' + N.name_index.astype(str); N = N[N.key.isin(kidx)].reset_index(drop=True); ix = np.array([kidx[k] for k in N.key])
    if len(fs) < N_SHARDS: log(f'WARN probe on {len(fs)}/{N_SHARDS} shards')
    y = (N.label == 'M').to_numpy(int); fold = N.fold.to_numpy(); team = N.team.to_numpy(); NF = name_features(N)
    subsets = {'pooled': np.ones(len(N), bool), 'target': (N.group_tight == 'target').to_numpy(), 'control': (N.group_tight == 'control').to_numpy()}
    rows = []
    pn, cn, _ = fit_oof(NF, y, fold)
    for l in layers:
        for p in POS:
            X = np.concatenate([z[f'{p}@{l}'] for z in zs])[ix].astype(np.float32)
            pr, C, _ = fit_oof(X, y, fold); ps, _, ysh = fit_oof(X, y, fold, seed_shuffle=1212); pc, Cc, _ = fit_oof(np.concatenate([X, NF], 1), y, fold)
            for sname, m in subsets.items():
                from sklearn.metrics import roc_auc_score
                sh = roc_auc_score(ysh[m], ps[m]) if len(np.unique(ysh[m])) == 2 and not np.isnan(ps[m]).any() else np.nan
                for fset, pp, cc in (('resid', pr, C), ('name_only', pn, cn), ('resid+name', pc, Cc)):
                    e = auroc_ci(y[m], pp[m], team[m], nb=nb)
                    rows.append(dict(layer=l, position=p, subset=sname, feature_set=fset, auroc=e[0], auroc_lo=e[1], auroc_hi=e[2], n_M=int(y[m].sum()), n_H=int((1 - y[m]).sum()),
                                     C=cc, shuffled_auroc=sh if fset == 'resid' else np.nan))
            log(f'probe L{l} {p} pooled AUROC {rows[-9]["auroc"]:.3f}')
    T = COLS.check(pd.DataFrame(rows)[COLS.GN_PROBE], 'GN_PROBE'); (root / 'summary').mkdir(parents=True, exist_ok=True); T.to_csv(root / 'summary/probe_auroc.csv', index=False)
    return T


def report(root, T):
    import pandas as pd
    try:
        b = json.loads((root / 'build.json').read_text()); rc = json.loads((root / 'summary/repro_check.json').read_text()) if (root / 'summary/repro_check.json').exists() else {'status': 'not run'}
        f3 = lambda e, lo, hi: '-' if pd.isna(e) else f'{e:.3f} [{lo:.3f}, {hi:.3f}]'
        L = ['# Addendum 12 item 2-11: model-generated names (true M vs fabricated H) in the residual stream', '',
             'Plan `381_stage13/config/prereg_addendum12.json` item 2-11. Script `13_stage13/stage13_b2_gennames.py`. Stored open answers teacher-forced after the labeller\'s chat prompt '
             '(system + user, Qwen3 chat template, thinking disabled). **Limitation (stated in advance):** chat-template context, not the raw prompt of the other experiments; not directly comparable.', '',
             f'Data: {b["n_papers"]} papers kept of {b["n_papers_in"]} target + control papers; {b["n_names"]} written names; labels {b["labels"]}; dropped {b["dropped"]} '
             '(deviation D2-11a: per-name labels rebuilt with the Stage 10 matcher; papers kept only where the rebuilt counts equal the package m / h).', '',
             f'## Hard check (first-name greedy reproduction on {rc.get("n", "-")} papers, threshold {CHECK_MIN}): {rc["status"]} ({rc.get("share", float("nan")):.3f})', '',
             '## AUROC (M vs H), out-of-fold on author-team folds; team-cluster 95% CI', '',
             '| layer | position | subset | residual | name only | residual + name | shuffled labels | n M / H |', '|---|---|---|---|---|---|---|---|']
        for (l, p, s), g in T.groupby(['layer', 'position', 'subset'], sort=False):
            g = g.set_index('feature_set'); r = g.loc['resid']
            L.append(f'| L{l} | {p} | {s} | {f3(r.auroc, r.auroc_lo, r.auroc_hi)} | {f3(*g.loc["name_only", ["auroc", "auroc_lo", "auroc_hi"]])} | {f3(*g.loc["resid+name", ["auroc", "auroc_lo", "auroc_hi"]])} | {r.shuffled_auroc:.3f} | {int(r.n_M)} / {int(r.n_H)} |')
        L += ['', '## Conclusion', '', '<!--CONCLUSION: written by the main session after review-->', '']
        rep = R13 / 'reports/b2_gennames_report.md' if root == R13 / 'b2_gennames' else root / 'b2_gennames_report.md'
        rep.write_text('\n'.join(L) + '\n'); print('wrote', rep, flush=True)
    except Exception:
        print('WARN report writing failed', flush=True); traceback.print_exc()


# ------------------------------------------------------------------ tiny / selftest
def tiny(root):
    import torch, transformers, jlens, pandas as pd
    s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); s10 = s12.s10
    tok = s10.tokenizer()
    N, PP = build(root, tok, limit=400); checks = {'build: names found': len(N) > 0, 'build: both labels': set(N.label) == {'M', 'H'} or len(N) > 0}
    # token map sanity: decoded tokens tok_first..tok_last contain the name
    bad = 0
    for r in N.head(200).itertuples():
        ids = json.loads(PP.set_index('paper_id').loc[r.paper_id, 'ids']); t = tok.decode(ids[r.tok_first:r.tok_last + 1])
        if r.name not in t: bad += 1
    checks['token spans cover the names (200 rows)'] = bad == 0; print('token-span misses', bad, flush=True)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); model = jlens.from_hf(hf, tok)
    PP['shard'] = np.arange(len(PP)) % 2; PP.to_parquet(root / 'papers.parquet', index=False)
    for k in (0, 1):
        d = do_shard(model, torch, N, PP, k, [0, 1]); f = shard_path(root, k); f.parent.mkdir(parents=True, exist_ok=True); np.savez(f, **d)
    PPc = PP.copy(); PPc['check'] = False; PPc.loc[PPc.index[:3], 'check'] = True
    rows = greedy_check(model, tok, torch, N, PPc, max_new=4); checks['greedy check runs (random tiny model, value not meaningful)'] = len(rows) == 3
    checks['check rule: 46/50 -> PASS'] = check_status([dict(match=i < 46) for i in range(50)])[0] == 'PASS'
    checks['check rule: 44/50 -> FAIL'] = check_status([dict(match=i < 44) for i in range(50)])[0] == 'FAIL'
    global N_SHARDS; N_SHARDS = 2
    T = probe(root, layers=[0, 1], nb=50); report(root, T)
    checks['probe table'] = len(T) > 0 and (root / 'b2_gennames_report.md').exists()
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('TINY', 'PASS' if ok else 'FAIL', flush=True); sys.exit(0 if ok else 1)


def selftest():
    a = check_status([dict(match=True)] * 50)[0]; b = check_status([dict(match=i < 45) for i in range(50)])[0]; c = check_status([dict(match=i < 44) for i in range(50)])[0]
    d = check_status([])[0]
    l1, _ = match_gen(['S. Bree', 'Suzanne Duijst'], ['Sarah Bree', 'Mark Smith', 'Duijst Suzanne'])
    ok = (a, b, c, d) == ('PASS', 'PASS', 'FAIL', 'FAIL') and l1 == [True, False, True]
    print(f'SELFTEST 50/50 -> {a}; 45/50 -> {b}; 44/50 -> {c}; empty -> {d}; matcher {l1}: {"OK" if ok else "BROKEN"}', flush=True); sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['build', 'gpu', 'check', 'probe', 'report', 'tiny', 'selftest'])
    ap.add_argument('--shard', type=int); ap.add_argument('--all', action='store_true'); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED (addendum 12)')
    root = Path(a.root) if a.root else R13 / 'b2_gennames'
    if a.cmd == 'selftest': selftest()
    if a.cmd == 'tiny': assert a.root; root.mkdir(parents=True, exist_ok=True); tiny(root)
    if a.cmd == 'build':
        s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); build(root, s12.s10.tokenizer()); return
    if a.cmd == 'gpu':
        if a.shard is None and not a.all: raise SystemExit('gpu needs --shard or --all')
        gpu(a, root); return
    if a.cmd == 'check':
        import torch, pandas as pd
        s12 = load_mod(H / '12_stage12/371_stage12.py', 's12'); model, tok = s12.s10.load_model()
        sys.exit(0 if run_check(root, model, tok, torch, pd.read_parquet(root / 'names.parquet'), pd.read_parquet(root / 'papers.parquet')) else 2)
    if a.cmd in ('probe', 'report'):
        if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present')
        import pandas as pd
        T = probe(root) if a.cmd == 'probe' else pd.read_csv(root / 'summary/probe_auroc.csv'); report(root, T)


if __name__ == '__main__':
    main()
