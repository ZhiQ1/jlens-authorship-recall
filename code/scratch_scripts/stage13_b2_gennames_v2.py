"""Addendum 12 item 2-11, VERSION 2 (deviation record D12-3, config/prereg_addendum12_deviations.json, sha256 checked at start).
Imports version 1 (stage13_b2_gennames.py) by path for the prompt, token positions, GPU residual extraction, greedy hard check and
the probe fitting (fit_oof); changes only what D12-3 fixes:
 (a) HARD CHECK of the rebuilt labels: per paper, rebuilt M, H and U (U = true authors not matched = n_true - rebuilt M, the package
     definition: u = n_authors - m holds for 9,108/9,108 papers) must equal the package m, h, u; papers that differ are EXCLUDED
     and counted (summary/label_counts.csv, build.json). The job stops only if the comparison code itself fails.
 (b) PRIMARY = TARGET papers with >= 1 M and >= 1 H name: within-paper AUROC = sum over papers of concordant (M, H) pairs (ties 0.5)
     / number of pairs (AUROC stratified by paper); 95% CI by author-team cluster bootstrap (2,000 multinomial team draws, archived
     group_folds team ids; one draw shared by all scores, so differences are paired). Pooled all-names AUROC = reference only.
 (c) Baselines (out-of-fold logistic, same folds and C rule as the probe): position = (index in the generated list, relative
     index); string = (name length in characters, log(1 + frequency of the full name among all cohort author names)).
     signal = team-bootstrap CI of (probe - position) > 0 AND of (probe - string) > 0.
 (d) CONTROL papers: descriptive only (point estimate, no CI, no signal call).
 Unchanged (addendum 12): positions, layers, logistic probe, folds, shuffled-label control, greedy first-name hard check (>= 90%
 of 50 papers), chat-template limitation.
Root: 381_stage13/b2_gennames_v2/ (separate from the v1 build). Commands: build | gpu --shard K | gpu --all | probe | tiny --root | selftest
"""
import argparse, hashlib, importlib.util, json, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
if __name__ == '__main__' and sys.argv[1:2] == ['status']:          # fast path for b2_orch.py: file checks only, no torch
    _sp = importlib.util.spec_from_file_location('b2c_status', H / '13_stage13/b2c_status.py'); _st = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_st)
    _st.status_211(); sys.exit(0)
_sp = importlib.util.spec_from_file_location('gn_v1', H / '13_stage13/stage13_b2_gennames.py'); V1 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V1)
R10, R13, LAB, COLS = V1.R10, V1.R13, V1.LAB, V1.COLS
DEV = R13 / 'config/prereg_addendum12_deviations.json'; DEV_SHA = 'c4c793653097d3b2a898892e4f28d5ea71fe8de71097c936f3345de027a52dba'
ROOT = R13 / 'b2_gennames_v2'; NB = 2000; log = V1.log


def check_dev():
    if hashlib.sha256(DEV.read_bytes()).hexdigest() != DEV_SHA: raise SystemExit('DEVIATION RECORD CHANGED (prereg_addendum12_deviations.json)')
    if (DEV.parent / 'prereg_addendum12_deviations.json.sha256').read_text().split()[0] != DEV_SHA: raise SystemExit('deviation .sha256 file differs')


def full_key(a):
    return ' '.join(V1.words(a))


def build(root, tok, limit=None):
    import pandas as pd
    c13 = V1.load_mod(H / '13_stage13/stage13_cpu.py', 'c13')
    P = pd.read_parquet(R10 / 'cohort/papers.parquet'); folds, teams = c13.group_folds(P.paper_id.to_numpy()); P['fold'] = folds; P['team'] = teams
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'generated_text', 'names', 'm', 'h', 'u']].rename(columns={'m': 'm_pkg', 'h': 'h_pkg', 'u': 'u_pkg'})
    d = P[P.group_tight.isin(['target', 'control'])].merge(o, on='paper_id')
    if limit: d = d.head(limit)
    allauth = [a for al in P.authors for a in str(al).split('; ')]
    surn = pd.Series([V1.words(a)[-1] for a in allauth if V1.words(a)]).value_counts(); fulln = pd.Series([full_key(a) for a in allauth if V1.words(a)]).value_counts()
    rows, papers, counts = [], [], []; drop = dict(count_mismatch=0, no_names=0, span_not_found=0, token_map=0)
    for r in d.itertuples():
        names = list(r.names); true = str(r.authors).split('; ')
        lab, nhit = V1.match_gen(true, names)
        mr = int(sum(lab)); hr = len(names) - mr; ur = len(true) - nhit
        ok = (mr, hr, ur) == (int(r.m_pkg), int(r.h_pkg), int(r.u_pkg)) and mr == nhit
        counts.append(dict(paper_id=r.paper_id, group_tight=r.group_tight, m_pkg=int(r.m_pkg), h_pkg=int(r.h_pkg), u_pkg=int(r.u_pkg), m_rebuilt=mr, h_rebuilt=hr, u_rebuilt=ur, match=bool(ok)))
        if not ok: drop['count_mismatch'] += 1; continue
        if not names: drop['no_names'] += 1; continue
        sp = V1.name_spans(r.generated_text, names)
        if sp is None: drop['span_not_found'] += 1; continue
        pr = V1.chat_prompt(tok, r.title, r.year); e = tok(pr + r.generated_text, add_special_tokens=False, return_offsets_mapping=True); off = e.offset_mapping; base = len(pr)
        ptoks = len(tok(pr, add_special_tokens=False).input_ids); recs, good = [], True
        for j, (a, b) in enumerate(sp):
            A, B = base + a, base + b; ti = [i for i, (x, y) in enumerate(off) if x < B and y > A]
            if not ti or ti[0] < ptoks: good = False; break
            w = V1.words(names[j]); sn = w[-1] if w else ''
            recs.append(dict(paper_id=r.paper_id, name_index=j, name=names[j], label='M' if lab[j] else 'H', group_tight=r.group_tight, recall_level=r.recall_level,
                             citation_bin=r.citation_bin, team=int(r.team), fold=int(r.fold), char_start=a, char_end=b, tok_first=ti[0], tok_last=ti[-1],
                             pos_pred_first=ti[0] - 1, pos_last=ti[-1], n_name_tokens=len(ti), surname=sn, surname_freq_cohort=int(surn.get(sn, 0)),
                             given_is_initial=bool(w and len(w[0]) == 1), name_len_chars=len(names[j]), name_n_words=len(w), name_index_rel=j / max(1, len(names) - 1),
                             fullname_freq_cohort=int(fulln.get(full_key(names[j]), 0))))
        if not good: drop['token_map'] += 1; continue
        rows += recs; papers.append(dict(paper_id=r.paper_id, n_prompt_tokens=ptoks, n_tokens=len(e.input_ids), ids=json.dumps(e.input_ids)))
    N = COLS.check(pd.DataFrame(rows)[COLS.GN2_NAMES], 'GN2_NAMES'); PP = pd.DataFrame(papers); PP['shard'] = np.arange(len(PP)) % V1.N_SHARDS
    rng = np.random.default_rng(1211); chk = rng.choice(len(PP), min(V1.N_CHECK, len(PP)), replace=False); PP['check'] = False; PP.loc[chk, 'check'] = True
    CT = COLS.check(pd.DataFrame(counts)[COLS.GN2_COUNTS], 'GN2_COUNTS')
    root.mkdir(parents=True, exist_ok=True); (root / 'summary').mkdir(exist_ok=True)
    N.to_parquet(root / 'names.parquet', index=False); PP.to_parquet(root / 'papers.parquet', index=False); CT.to_csv(root / 'summary/label_counts.csv', index=False)
    pm = N.groupby('paper_id').label.agg(lambda x: (x == 'M').any() and (x == 'H').any())
    prim = N[N.paper_id.isin(pm[pm].index)]
    meta = dict(created=V1.now(), deviation='D12-3', n_papers_in=len(d), n_papers=len(PP), n_names=len(N), labels=N.label.value_counts().to_dict(),
                count_check=dict(compared=len(CT), equal=int(CT.match.sum()), excluded=int((~CT.match).sum()),
                                 excluded_by_group=CT[~CT.match].group_tight.value_counts().to_dict()),
                dropped=drop, primary_papers=dict(target=int(prim[prim.group_tight == 'target'].paper_id.nunique()), control=int(prim[prim.group_tight == 'control'].paper_id.nunique())),
                primary_names=prim.groupby(['group_tight', 'label']).size().astype(int).to_dict().__repr__(), shards=V1.N_SHARDS)
    (root / 'build.json').write_text(json.dumps(meta, indent=1, default=str)); log('build v2', meta)
    return N, PP


# ------------------------------------------------------------------ within-paper AUROC with team-cluster bootstrap
def pair_stats(paper, y, s):
    """per paper: concordant (ties 0.5) and number of (M, H) pairs."""
    import pandas as pd
    df = pd.DataFrame(dict(p=paper, y=y, s=s)); out = {}
    for p, g in df.groupby('p', sort=False):
        a, b = g.s[g.y == 1].to_numpy(), g.s[g.y == 0].to_numpy()
        if len(a) and len(b): out[p] = ((a[:, None] > b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum(), len(a) * len(b))
    return out


def within_auroc(stats_list, paper_team, nb=NB, seed=12):
    """stats_list: list of {paper: (conc, pairs)} on the SAME paper set; returns point estimates and bootstrap draws [nb, k]."""
    ps = sorted(stats_list[0]); teams = np.array([paper_team[p] for p in ps]); uniq, codes = np.unique(teams, return_inverse=True)
    C = np.array([[st[p][0] for p in ps] for st in stats_list], float); Np = np.array([[st[p][1] for p in ps] for st in stats_list], float)
    est = C.sum(1) / Np.sum(1)
    W = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=nb)[:, codes].astype(float)
    bt = (W @ C.T) / np.maximum(W @ Np.T, 1e-12)
    return est, bt, len(ps), int(Np[0].sum())


def probe(root, layers=None, nb=NB):
    import pandas as pd
    from sklearn.metrics import roc_auc_score
    layers = layers or V1.LAYERS
    N = pd.read_parquet(root / 'names.parquet'); fs = sorted((root / 'raw/resid').glob('shard_*.npz'))
    zs = [np.load(f) for f in fs]; key = np.concatenate([z['key'] for z in zs]); kidx = {k: i for i, k in enumerate(key)}
    N['key'] = N.paper_id + '|' + N.name_index.astype(str); N = N[N.key.isin(kidx)].reset_index(drop=True); ix = np.array([kidx[k] for k in N.key])
    y = (N.label == 'M').to_numpy(int); fold = N.fold.to_numpy(); paper = N.paper_id.to_numpy(); PT = dict(zip(N.paper_id, N.team))
    XP = N[['name_index', 'name_index_rel']].to_numpy(float); XS = np.stack([N.name_len_chars.to_numpy(float), np.log1p(N.fullname_freq_cohort.to_numpy(float))], 1)
    pp_, _, _ = V1.fit_oof(XP, y, fold); ps_, _, _ = V1.fit_oof(XS, y, fold)
    subs = {'target': (N.group_tight == 'target').to_numpy(), 'control': (N.group_tight == 'control').to_numpy(), 'all': np.ones(len(N), bool)}
    rows = []
    for l in layers:
        for pos in V1.POS:
            X = np.concatenate([z[f'{pos}@{l}'] for z in zs])[ix].astype(np.float32)
            pr, C, _ = V1.fit_oof(X, y, fold); psh, _, ysh = V1.fit_oof(X, y, fold, seed_shuffle=1212)
            for sname, m in subs.items():
                st = [pair_stats(paper[m], y[m], sc[m]) for sc in (pr, pp_, ps_)]
                common = set(st[0]) & set(st[1]) & set(st[2]); st = [{p: s[p] for p in common} for s in st]
                ssh = pair_stats(paper[m], ysh[m], psh[m])
                shv = sum(v[0] for v in ssh.values()) / max(1, sum(v[1] for v in ssh.values())) if ssh else np.nan
                ref = roc_auc_score(y[m], pr[m]) if len(np.unique(y[m])) == 2 and not np.isnan(pr[m]).any() else np.nan
                if not common:
                    rows.append(dict(layer=l, position=pos, subset=sname, score='probe', auroc_within=np.nan, lo=np.nan, hi=np.nan, n_papers=0, n_pairs=0,
                                     n_M=int(y[m].sum()), n_H=int((1 - y[m]).sum()), diff_vs_position=np.nan, diff_pos_lo=np.nan, diff_pos_hi=np.nan,
                                     diff_vs_string=np.nan, diff_str_lo=np.nan, diff_str_hi=np.nan, signal=False, auroc_pooled_ref=ref, shuffled_within=shv)); continue
                est, bt, npap, npair = within_auroc(st, PT, nb=nb)
                ci = lambda v: np.percentile(v, [2.5, 97.5])
                d1, d2 = bt[:, 0] - bt[:, 1], bt[:, 0] - bt[:, 2]; (a1, b1), (a2, b2) = ci(d1), ci(d2); lo, hi = ci(bt[:, 0])
                desc = sname == 'control'
                for k_, nm in enumerate(('probe', 'position', 'string')):
                    lo_k, hi_k = ci(bt[:, k_])
                    rows.append(dict(layer=l, position=pos, subset=sname, score=nm, auroc_within=est[k_], lo=np.nan if desc else lo_k, hi=np.nan if desc else hi_k,
                                     n_papers=npap, n_pairs=npair, n_M=int(y[m].sum()), n_H=int((1 - y[m]).sum()),
                                     diff_vs_position=est[0] - est[1] if k_ == 0 else np.nan, diff_pos_lo=np.nan if desc or k_ else a1, diff_pos_hi=np.nan if desc or k_ else b1,
                                     diff_vs_string=est[0] - est[2] if k_ == 0 else np.nan, diff_str_lo=np.nan if desc or k_ else a2, diff_str_hi=np.nan if desc or k_ else b2,
                                     signal=bool(k_ == 0 and not desc and a1 > 0 and a2 > 0), auroc_pooled_ref=ref if k_ == 0 else np.nan, shuffled_within=shv if k_ == 0 else np.nan))
            log(f'probe v2 L{l} {pos} done')
    T = COLS.check(pd.DataFrame(rows)[COLS.GN2_PROBE], 'GN2_PROBE'); (root / 'summary').mkdir(exist_ok=True); T.to_csv(root / 'summary/probe_within.csv', index=False)
    report(root, T); return T


def report(root, T):
    import pandas as pd
    try:
        b = json.loads((root / 'build.json').read_text()); rc = json.loads((root / 'summary/repro_check.json').read_text()) if (root / 'summary/repro_check.json').exists() else {'status': 'not run'}
        f3 = lambda e, lo, hi: '-' if pd.isna(e) else (f'{e:.3f}' if pd.isna(lo) else f'{e:.3f} [{lo:.3f}, {hi:.3f}]')
        fd = lambda e, lo, hi: '-' if pd.isna(e) else (f'{e:+.3f}' if pd.isna(lo) else f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]')
        L = ['# Addendum 12 item 2-11 (v2, deviation D12-3): model-generated names, true (M) vs fabricated (H)', '',
             'Plan `prereg_addendum12.json` item 2-11 + `prereg_addendum12_deviations.json` D12-3. Script `13_stage13/stage13_b2_gennames_v2.py`. '
             '**Limitation:** chat-template context (labeller prompt), not the raw prompt of the other experiments.', '',
             f'## Label hard check (D12-3 a): rebuilt per-paper M / H / U == package m / h / u', '',
             f'- {b["count_check"]["compared"]} papers compared; equal {b["count_check"]["equal"]}; **excluded {b["count_check"]["excluded"]}** {b["count_check"]["excluded_by_group"]}.',
             f'- Other drops: {b["dropped"]}. Kept {b["n_papers"]} papers, {b["n_names"]} names {b["labels"]}.',
             f'- Primary papers (>= 1 M and >= 1 H): target {b["primary_papers"]["target"]}, control {b["primary_papers"]["control"]} (descriptive).', '',
             f'## Greedy first-name reproduction (hard check, >= 90% of 50): {rc["status"]} ({rc.get("share", float("nan")):.3f})', '',
             '## Within-paper AUROC (pairs within paper), team-cluster 95% CI (2,000 draws); signal = CI(probe - position) > 0 and CI(probe - string) > 0', '',
             '| layer | position | subset | probe | position baseline | string baseline | probe - position | probe - string | signal | papers / pairs | pooled AUROC (ref.) | shuffled |',
             '|---|---|---|---|---|---|---|---|---|---|---|---|']
        for (l, p, s), g in T.groupby(['layer', 'position', 'subset'], sort=False):
            g = g.set_index('score')
            if 'probe' not in g.index: continue
            r = g.loc['probe']; gp = lambda k: f3(g.loc[k, 'auroc_within'], g.loc[k, 'lo'], g.loc[k, 'hi']) if k in g.index else '-'
            L.append(f'| L{l} | {p} | {s}{" (descriptive)" if s == "control" else ""} | {gp("probe")} | {gp("position")} | {gp("string")} | '
                     f'{fd(r.diff_vs_position, r.diff_pos_lo, r.diff_pos_hi)} | {fd(r.diff_vs_string, r.diff_str_lo, r.diff_str_hi)} | {"yes" if r.signal else "no"} | '
                     f'{int(r.n_papers)} / {int(r.n_pairs)} | {r.auroc_pooled_ref:.3f} | {r.shuffled_within:.3f} |')
        L += ['', 'Primary = target rows. "all" (target + control) is a secondary view; control rows are descriptive (no CI).', '', '## Conclusion', '', '<!--CONCLUSION: written by the main session after review-->', '']
        rep = R13 / 'reports/b2_gennames_report.md' if root == ROOT else root / 'b2_gennames_report.md'; rep.write_text('\n'.join(L) + '\n'); print('wrote', rep, flush=True)
    except Exception:
        print('WARN report writing failed', flush=True); traceback.print_exc()


def selftest():
    # within-paper AUROC: perfect, reversed, ties; bootstrap shape; count rule
    paper = np.array(['a', 'a', 'a', 'b', 'b']); y = np.array([1, 0, 0, 1, 0]); team = {'a': 1, 'b': 2}
    s_good = np.array([.9, .1, .2, .8, .3]); s_bad = -s_good; s_tie = np.ones(5)
    est, bt, npap, npair = within_auroc([pair_stats(paper, y, s) for s in (s_good, s_bad, s_tie)], team, nb=50)
    ok1 = np.allclose(est, [1.0, 0.0, 0.5]) and bt.shape == (50, 3) and (npap, npair) == (2, 3)
    l1, nh = V1.match_gen(['S. Bree', 'Suzanne Duijst', 'J. Vliet'], ['Sarah Bree', 'Mark Smith', 'Duijst Suzanne'])
    ok2 = (sum(l1), 3 - sum(l1), 3 - nh) == (2, 1, 1)
    print(f'SELFTEST v2 within-AUROC {est} pairs {npair}: {"OK" if ok1 else "BROKEN"}; M/H/U rebuild (2,1,1): {"OK" if ok2 else "BROKEN"}', flush=True)
    return ok1 and ok2


def tiny(root):
    import torch, transformers, jlens, pandas as pd
    s12 = V1.load_mod(H / '12_stage12/371_stage12.py', 's12'); s10 = s12.s10; tok = s10.tokenizer()
    N, PP = build(root, tok, limit=600); b = json.loads((root / 'build.json').read_text())
    checks = {'build + count check ran': b['count_check']['compared'] > 0, 'some primary target papers': b['primary_papers']['target'] > 0}
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); model = jlens.from_hf(hf, tok)
    PP['shard'] = np.arange(len(PP)) % 2; PP.to_parquet(root / 'papers.parquet', index=False)
    for k in (0, 1):
        d = V1.do_shard(model, torch, N, PP, k, [0, 1]); f = V1.shard_path(root, k); f.parent.mkdir(parents=True, exist_ok=True); np.savez(f, **d)
    V1.N_SHARDS = 2; T = probe(root, layers=[0, 1], nb=50)
    checks['probe table + report'] = len(T) > 0 and (root / 'b2_gennames_report.md').exists()
    checks['selftest'] = selftest()
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('TINY v2', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['build', 'gpu', 'probe', 'tiny', 'selftest', 'status'])
    ap.add_argument('--shard', type=int); ap.add_argument('--all', action='store_true'); ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=42); a = ap.parse_args()
    if hashlib.sha256(V1.PLAN.read_bytes()).hexdigest() != V1.PLAN_SHA: raise SystemExit('PLAN CHANGED (addendum 12)')
    check_dev(); root = Path(a.root) if a.root else ROOT
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'tiny': assert a.root; root.mkdir(parents=True, exist_ok=True); sys.exit(0 if tiny(root) else 1)
    if a.cmd == 'build':
        s12 = V1.load_mod(H / '12_stage12/371_stage12.py', 's12'); build(root, s12.s10.tokenizer()); return
    if a.cmd == 'gpu':
        if a.shard is None and not a.all: raise SystemExit('gpu needs --shard or --all')
        V1.gpu(a, root); return
    if a.cmd == 'probe':
        if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present')
        probe(root)


if __name__ == '__main__':
    main()
