"""Addendum 7 (group comparisons), step 1: per-author 'written' flags + per-paper Stage 10 signals split by written/unwritten authors.

Plan (frozen, read-only): /scratch/zhang.zhiqi2/jlens/391_groups/config/prereg_addendum7_groups.json (sha256 621525e4...).
CPU only, existing Stage 10 raw outputs only.

Written flag = Stage 10 R0/R1 reconstruction (10_stage10/stage10_extra_r0r1.py: match(), surname + first initial, either order,
one-to-one), imported unchanged. Papers whose rebuilt count != label m are flagged (consistent = False) and dropped downstream.

Per paper x who (unwritten / written / all) x role (all + token roles) x readout x layer:
    true, false (mean of the 5 matched false titles), delete, spec = true - false; tokens pooled (mean over name tokens),
    log10(1/rank) = -log10(rank), exactly as Stage 10 paper_scores/analyze_title (mean_nlr).
Outputs: OUT/data/author_flags.parquet, OUT/data/paper_signal.parquet (refuses to overwrite).
"""
import importlib.util, os, sys, json, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'
LAB = BASE / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
OUT = Path(os.environ.get('GROUPS_OUT', BASE / '391_groups'))
PLAN = BASE / '391_groups/config/prereg_addendum7_groups.json'; PLAN_SHA = '621525e4360f09bda8d7290b204ddc3e6bbed5c0ab3ddf6aedc8db50dd2da7de'
ROLES = ['surname_first', 'surname_cont', 'initial_first', 'given_first', 'given_cont', 'punct']


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def check_plan():
    h = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    if h != PLAN_SHA: raise SystemExit(f'PLAN CHANGED {h}')
    return h


def author_flags(r01):
    o = pd.read_json(LAB / 'open_results.jsonl', lines=True)[['paper_id', 'names']]
    p = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'authors', 'm', 'recall_level']).merge(o, on='paper_id', how='left')
    assert p.names.notna().all(), 'paper without open answer'
    p['m'] = p.m.astype(int); p['hits'] = [r01.match(a.split('; '), n) for a, n in zip(p.authors, p.names)]; p['mm'] = p.hits.map(sum)
    au = p[['paper_id', 'hits', 'm', 'mm']].explode('hits').rename(columns={'hits': 'written'})
    au['author_index'] = au.groupby('paper_id').cumcount(); au['written'] = au.written.astype(bool)
    au['consistent'] = au.m == au.mm
    ctx = pd.read_parquet(R10 / 'cohort/contexts.parquet', columns=['paper_id', 'author_index', 'author'])
    au = au.merge(ctx, on=['paper_id', 'author_index'], how='left'); au['scored'] = au.author.notna()
    # sanity: scored author string equals the list entry
    lst = p.set_index('paper_id').authors.str.split('; ')
    chk = au[au.scored]; bad = sum(lst[q][i] != a for q, i, a in zip(chk.paper_id, chk.author_index, chk.author))
    print(f'author string mismatches between contexts and papers.authors: {bad}', flush=True)
    return au.drop(columns=['author'])


def main():
    check_plan()
    (OUT / 'data').mkdir(parents=True, exist_ok=True)
    fa, fs = OUT / 'data/author_flags.parquet', OUT / 'data/paper_signal.parquet'
    for f in (fa, fs, OUT / 'data/author_signal.parquet'):
        if f.exists(): raise SystemExit(f'{f} exists; refusing to overwrite')
    r01 = load(H / '10_stage10/stage10_extra_r0r1.py', 'r01'); s10 = r01.s10
    au = author_flags(r01); au.to_parquet(fa, index=False); print('wrote', fa, len(au), flush=True)
    pp = au.drop_duplicates('paper_id')
    print('papers consistent:', pp.consistent.sum(), 'of', len(pp), flush=True)

    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'role'])
    toks = toks.merge(au[['paper_id', 'author_index', 'written']], on=['paper_id', 'author_index'], how='left')
    assert toks.written.notna().all()
    toks = toks.sort_values('row_id').reset_index(drop=True); rid = toks.row_id.to_numpy()
    sub = os.environ.get('GROUPS_TINY') == '1'
    root = R10; m, lenses = s10.verify(root); cm = s10.verify_conditions(root)
    conds = cm['conditions']; K = cm['K']; assert conds[0] == 'true' and len(conds) == K + 2
    mats, rls = {}, None
    for cond in conds:
        raw = s10.load_raw(root, m, lenses, require_complete=True, cond=cond)
        if sub: raw = raw[raw.readout.isin(['final', 'logit']) & raw.layer.isin([62, 63])]     # tiny test: two readout-layers only
        raw['nlr'] = -np.log10(raw['rank'].astype(np.float64))
        w = raw.pivot_table(index='row_id', columns=['readout', 'layer'], values='nlr', aggfunc='first')
        del raw
        if rls is None: rls = list(w.columns)
        w = w.reindex(index=rid, columns=pd.MultiIndex.from_tuples(rls))
        mats[cond] = w.to_numpy(np.float64); print(cond, mats[cond].shape, 'nan share', np.isnan(mats[cond]).mean().round(5), flush=True)
    T = mats['true']; D = mats['delete']; F = np.mean([mats[f'false_{k}'] for k in range(K)], axis=0)
    del mats
    rows = []
    keys = pd.DataFrame({'paper_id': toks.paper_id, 'written': toks.written, 'role': toks.role})
    first = (toks.author_index == 0).to_numpy(); un = ~keys.written.to_numpy()
    who_sets = {'unwritten': un, 'written': ~un, 'all': np.ones(len(keys), bool),
                'unwritten_first': un & first, 'unwritten_other': un & ~first, 'written_first': ~un & first, 'written_other': ~un & ~first}  # addendum 8
    # addendum 8: per-author table (role all): paper x author_index x readout x layer
    akey = toks.paper_id.astype(str) + '|' + toks.author_index.astype(str)
    codes, uniq = pd.factorize(akey); n = np.bincount(codes); arows = {}
    for name, X in (('true', T), ('false', F), ('delete', D)):
        s_ = np.zeros((len(uniq), X.shape[1])); c_ = np.zeros_like(s_); ok = ~np.isnan(X)
        np.add.at(s_, codes, np.where(ok, X, 0)); np.add.at(c_, codes, ok)
        with np.errstate(invalid='ignore', divide='ignore'): arows[name] = s_ / c_
    pa = pd.Series(uniq).str.split('|', expand=True)
    fa_ = OUT / 'data/author_signal.parquet'
    A = pd.concat([pd.DataFrame({'paper_id': pa[0], 'author_index': pa[1].astype(int), 'readout': r, 'layer': int(l), 'n_tok': n,
                                 'true': arows['true'][:, j], 'false': arows['false'][:, j], 'delete': arows['delete'][:, j]}) for j, (r, l) in enumerate(rls)], ignore_index=True)
    A['spec'] = A['true'] - A['false']
    A = A.merge(au[['paper_id', 'author_index', 'written']], on=['paper_id', 'author_index'], how='left')
    for c in ['true', 'false', 'delete', 'spec']: A[c] = A[c].astype(np.float32)
    A.to_parquet(fa_, index=False); print('wrote', fa_, A.shape, flush=True); del A, arows
    for who, wm in who_sets.items():
        for role in ['all'] + ROLES:
            sel = wm & ((keys.role == role).to_numpy() if role != 'all' else True)
            if not sel.any(): continue
            pid = keys.paper_id.to_numpy()[sel]
            codes, uniq = pd.factorize(pid)
            n = np.bincount(codes)
            for name, X in (('true', T), ('false', F), ('delete', D)):
                Xs = X[sel]; ok = ~np.isnan(Xs)
                s = np.zeros((len(uniq), Xs.shape[1])); c = np.zeros_like(s)
                np.add.at(s, codes, np.where(ok, Xs, 0)); np.add.at(c, codes, ok)
                with np.errstate(invalid='ignore', divide='ignore'):
                    mean = s / c
                for j, (r, l) in enumerate(rls):
                    if name == 'true':
                        rows.append(pd.DataFrame({'paper_id': uniq, 'who': who, 'role': role, 'readout': r, 'layer': int(l), 'n_tok': n, 'true': mean[:, j]}))
                    else:
                        rows[-len(rls) + j][name] = mean[:, j]
            print(who, role, len(uniq), flush=True)
    out = pd.concat(rows, ignore_index=True); out['spec'] = out['true'] - out['false']
    for c in ['true', 'false', 'delete', 'spec']: out[c] = out[c].astype(np.float32)
    out.to_parquet(fs, index=False); print('wrote', fs, out.shape, flush=True)


if __name__ == '__main__':
    main()
