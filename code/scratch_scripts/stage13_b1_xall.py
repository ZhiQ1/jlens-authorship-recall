"""Stage 13 batch 1 item 1 (config/prereg_addendum10.json): X1, X2, X3 (behaviour), X4 scored for ALL authors.

The frozen code (381_stage13.py do_xpatch / do_pscope / do_para_run, stage13_x2.py do_x2) scores only the first author
(C.ctx[paper][0]). Here the same pair loop, the same prompts, layers, readouts (L63 teacher-forced mean log10(1/rank),
s13.score_tf), partner B, random C, lexical neighbour D, patch lists and batch sizes are used, and the scoring is repeated
for EVERY author context of paper A (C.ctx[paper], all name tokens). The first author's calls are identical to the
frozen ones, so its rows must reproduce the published raw data (hard check, addendum 10).
Components (one output file per component and shard; one row per (pair, author)):
  xpatch : X1 clean / corrupt / authors|year|field|random_c @ XP_LAYERS (batch 7), as s13.do_xpatch.
  x2     : X2 carry / remove for VARIANTS (batch 35, unchanged) + the new S_auth_all (summary_b1_xall, one extra
           forward of batch 5 per arm: carry_authall@l, remove_authall@l); cap_* per pair. As stage13_x2.do_x2.
  pscope : X4 author target only ('The first author of the paper is'; the year / field targets do not depend on the
           author and are not re-run): author@none, author@{self,partner}@{title,colon}@l (batch 7), as s13.do_pscope.
  para   : X3 behaviour scores (original / paraphrase / partner / lexical neighbour D titles), as s13.do_para_run
           (no residuals: the X3 representation analysis scores no author).
Usage: python stage13_b1_xall.py --tiny                        (CPU, 2-layer random Qwen3; compares author 0 with the
                                                                 frozen functions run on the same tiny model)
       python stage13_b1_xall.py --shards 0 [1 ...] [--comps xpatch x2 pscope para] [--max-minutes M]
       python stage13_b1_xall.py --all [--max-minutes M]
Outputs: raw/b1_xall/{comp}/shard_XXX.npz; skip-if-exists per (comp, shard); claims logs/claims_b1_xall/."""
import importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT0 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
COMPS = ['xpatch', 'x2', 'pscope', 'para']


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


x2 = load(H / '13_stage13/stage13_x2.py', 'x2'); s13 = x2.s13; s10, s11 = s13.s10, s13.s11
R = dict(root=ROOT0)


def set_root(tiny):
    r = ROOT0 / 'b1_xall_tiny' if tiny else ROOT0
    R.update(root=r, raw=r / 'raw/b1_xall', sub_new=r / 'summary_b1_xall', sub_old=(ROOT0 / 'x2_tiny/summary_x2') if tiny else (ROOT0 / 'summary_x2'),
             claims=r / 'logs/claims_b1_xall', logs=r / 'logs')


def authors_of(C, pid):
    cx = C.ctx[pid]; n = len(cx)
    return [(ai, name, n) for ai, _, name in cx]


def to_cols(rows):
    return {k: np.array([x[k] for x in rows]) for k in rows[0]} if rows else dict(paper_id=np.array([]))


# ------------------------------------------------------------------ X1
def do_xpatch(C, shard):
    smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); rows = []; XL = s13.XP_LAYERS
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; A, Bt = P.loc[r.paper_id].title, P.loc[q].title
        spanA, fullA = s13.title_span(C.tok, A); spanB, fullB = s13.title_span(C.tok, Bt)
        if spanA != spanB: continue
        c = pairs.loc[r.paper_id].random_c; spanC, fullC = s13.title_span(C.tok, P.loc[c].title)
        if spanC != spanB: continue
        rec = {}
        actsC = C.record(fullC[:len(fullC)], XL); rec['random_c'] = {l: actsC[l][spanC[0]:spanC[-1] + 1] for l in XL}
        for task in s13.TASK_NAMES:
            ids, _, _ = s13.build(C.tok, A, task, []); acts = C.record(ids, XL)
            rec[task] = {l: acts[l][spanA[0]:spanA[-1] + 1] for l in XL}
        patches = {}
        for task in s13.TASK_NAMES + ['random_c']:
            patch = {}
            for i, l in enumerate(XL):
                patch.setdefault(l, []).extend([(i, ('at', p), rec[task][l][j]) for j, p in enumerate(spanA)])
            patches[task] = patch
        for ai, name, n in authors_of(C, r.paper_id):
            clean = s13.score_tf(C, fullA, name)[0]; corrupt = s13.score_tf(C, fullB, name)[0]
            row = dict(paper_id=r.paper_id, author_index=ai, n_authors=n, n_name_tokens=len(name), partner=q, random_c=c,
                       split=pairs.loc[r.paper_id].split, clean=clean, corrupt=corrupt)
            for task in s13.TASK_NAMES + ['random_c']:
                v = s13.score_tf(C, fullB, name, patch=patches[task], batch=len(XL))
                for i, l in enumerate(XL): row[f'{task}@{l}'] = v[i]
            rows.append(row)
    return to_cols(rows)


# ------------------------------------------------------------------ X2
_SUB = {}


def subspaces(C, layers):
    if 'SUB' not in _SUB:
        SUB, MU = x2.load_subspaces(C, R['sub_old'], layers); NEW = {}
        for l in layers:
            q = np.load(R['sub_new'] / f'subspaces_authall_L{l}.npz')['S_auth_all'].astype(np.float32)
            assert q.shape[1] == 10 and np.allclose(q.T @ q, np.eye(10), atol=1e-4), (l, q.shape)
            NEW[l] = C.torch.tensor(q)
        sha = {f'old_L{l}': s10.sha_file(R['sub_old'] / f'subspaces_L{l}.npz') for l in layers} | \
              {f'new_L{l}': s10.sha_file(R['sub_new'] / f'subspaces_authall_L{l}.npz') for l in layers}
        _SUB.update(SUB=SUB, MU=MU, NEW=NEW, sha=sha)
    return _SUB['SUB'], _SUB['MU'], _SUB['NEW']


def do_x2(C, shard, layers):
    SUB, MU, NEW = subspaces(C, layers)
    smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); rows = []; V = x2.VARIANTS
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; A, Bt = P.loc[r.paper_id].title, P.loc[q].title
        spanA, fullA = s13.title_span(C.tok, A); spanB, fullB = s13.title_span(C.tok, Bt)
        if spanA != spanB: continue
        aA = C.record(fullA, layers); aB = C.record(fullB, layers)
        base = dict(paper_id=r.paper_id, partner=q, split=pairs.loc[r.paper_id].split, n_title_tokens=len(spanA))
        pc, pr, pcn, prn = {}, {}, {}, {}
        for li, l in enumerate(layers):                                   # exactly as stage13_x2.do_x2
            hA = aA[l][spanA[0]:spanA[-1] + 1]; hB = aB[l][spanB[0]:spanB[-1] + 1]; dt = hA.dtype; dev = hA.device
            dAB = (hA.float() - hB.float()); dAm = hA.float() - MU[l].to(dev)[None]; e2 = float((dAB ** 2).sum())
            for vi, v in enumerate(V):
                Q = SUB[l][v]; i = vi * len(layers) + li
                if v == 'full':
                    newB, newA = hA, MU[l].to(dev)[None].expand_as(hA).to(dt); base[f'cap_{v}@{l}'] = 1.0
                else:
                    Q = Q.to(dev); pAB = x2.proj(dAB, Q)
                    newB = (hB.float() + pAB).to(dt); newA = (hA.float() - x2.proj(dAm, Q)).to(dt)
                    base[f'cap_{v}@{l}'] = float((pAB ** 2).sum()) / max(e2, 1e-30)
                pc.setdefault(l, []).extend([(i, ('at', p), newB[j]) for j, p in enumerate(spanA)])
                pr.setdefault(l, []).extend([(i, ('at', p), newA[j]) for j, p in enumerate(spanA)])
            Qn = NEW[l].to(dev); pABn = x2.proj(dAB, Qn)                        # new S_auth (all authors' tokens)
            newBn = (hB.float() + pABn).to(dt); newAn = (hA.float() - x2.proj(dAm, Qn)).to(dt)
            base[f'cap_authall@{l}'] = float((pABn ** 2).sum()) / max(e2, 1e-30)
            pcn.setdefault(l, []).extend([(li, ('at', p), newBn[j]) for j, p in enumerate(spanA)])
            prn.setdefault(l, []).extend([(li, ('at', p), newAn[j]) for j, p in enumerate(spanA)])
        nb = len(V) * len(layers)
        for ai, name, n in authors_of(C, r.paper_id):
            clean = s13.score_tf(C, fullA, name)[0]; corrupt = s13.score_tf(C, fullB, name)[0]
            row = dict(base, author_index=ai, n_authors=n, n_name_tokens=len(name), clean=clean, corrupt=corrupt)
            vc = s13.score_tf(C, fullB, name, patch=pc, batch=nb); vr = s13.score_tf(C, fullA, name, patch=pr, batch=nb)
            for vi, v in enumerate(V):
                for li, l in enumerate(layers):
                    row[f'carry_{v}@{l}'] = vc[vi * len(layers) + li]; row[f'remove_{v}@{l}'] = vr[vi * len(layers) + li]
            vcn = s13.score_tf(C, fullB, name, patch=pcn, batch=len(layers)); vrn = s13.score_tf(C, fullA, name, patch=prn, batch=len(layers))
            for li, l in enumerate(layers): row[f'carry_authall@{l}'] = vcn[li]; row[f'remove_authall@{l}'] = vrn[li]
            rows.append(row)
    return to_cols(rows)


# ------------------------------------------------------------------ X4 (author target)
def do_pscope(C, shard):
    smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); rows = []; PL = s13.PS_LAYERS
    t = s13.PS_TARGETS['author']; e = C.tok(t, return_offsets_mapping=True); tids = list(e.input_ids); x = t.index('X')
    xi = [i for i, (a, b) in enumerate(e.offset_mapping) if a <= x < b][0]
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; src = {}
        for who, pid in (('self', r.paper_id), ('partner', q)):
            ids, it, ic = s13.build(C.tok, P.loc[pid].title, 'authors', []); acts = C.record(ids, PL)
            src[who] = {('title', l): acts[l][it] for l in PL} | {('colon', l): acts[l][ic] for l in PL}
        for ai, name, n in authors_of(C, r.paper_id):
            row = dict(paper_id=r.paper_id, author_index=ai, n_authors=n, n_name_tokens=len(name), partner=q)
            row['author@none'] = s13.score_tf(C, tids, name)[0]
            for who in ('self', 'partner'):
                for pos in ('title', 'colon'):
                    patch = {l: [(i, ('at', xi), src[who][(pos, l)])] for i, l in enumerate(PL)}
                    v = s13.score_tf(C, tids, name, patch=patch, batch=len(PL))
                    for i, l in enumerate(PL): row[f'author@{who}@{pos}@{l}'] = v[i]
            rows.append(row)
    return to_cols(rows)


# ------------------------------------------------------------------ X3 behaviour
def do_para(C, shard):
    smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); rows = []
    para = {}; J2 = {}
    j = pd.read_csv(ROOT0 / 'config/x3_lexical_neighbour_j2.csv')
    J2 = {p: (q, v) for p, q, v in zip(j.paper_id, j.lexical_neighbour_j2, j.lexical_jaccard2)}
    for f in sorted((ROOT0 / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); para |= {p: (t, ok, jj) for p, t, ok, jj in zip(z['paper_id'], z['paraphrase'], z['auto_ok'], z['word_jaccard'])}
    for r in smp[smp.shard == shard].itertuples():
        if r.paper_id not in pairs.index or r.paper_id not in para or not para[r.paper_id][1] or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner
        if r.paper_id in J2: dpid, djac = J2[r.paper_id]
        else: dpid, djac = s13.lexical_neighbour(C.papers, r.paper_id, para[r.paper_id][2])
        idsv = [s13.build(C.tok, title, 'authors', [])[0] for title in (P.loc[r.paper_id].title, para[r.paper_id][0], P.loc[q].title, P.loc[dpid].title)]
        for ai, name, n in authors_of(C, r.paper_id):
            sc = [s13.score_tf(C, ids, name)[0] for ids in idsv]
            rows.append(dict(paper_id=r.paper_id, author_index=ai, n_authors=n, n_name_tokens=len(name), partner=q, score_original=sc[0],
                             score_paraphrase=sc[1], score_partner=sc[2], score_lexical=sc[3], word_jaccard=para[r.paper_id][2],
                             lexical_neighbour=dpid, lexical_jaccard=djac))
    return to_cols(rows)


def compute(C, comp, shard, tiny):
    if comp == 'x2': return do_x2(C, shard, [0, 1] if tiny else x2.LAYERS)
    return dict(xpatch=do_xpatch, pscope=do_pscope, para=do_para)[comp](C, shard)


def out_path(comp, k): return R['raw'] / comp / f'shard_{k:03d}.npz'


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def claim(comp, k, me):
    R['claims'].mkdir(parents=True, exist_ok=True); d = R['claims'] / f'{comp}_{k:03d}'
    try: d.mkdir(); (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")}\n'); return True
    except FileExistsError:
        o = (d / 'owner').read_text().split()[0] if (d / 'owner').exists() else ''
        if o and o.isdigit():                                                  # reclaim if the owner job is gone
            import subprocess
            try: st = subprocess.run(['squeue', '-h', '-j', o, '-o', '%T'], capture_output=True, text=True, timeout=60).stdout.strip()
            except Exception: st = 'UNKNOWN'
            if st == '':
                (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")} (reclaimed from {o})\n'); return True
        return False


def run(shards, comps, tiny=False, max_minutes=None):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); budget = max_minutes
    left = s11.slurm_minutes_left()
    if left is not None and (budget is None or left - 6 < budget): budget = left - 6
    todo = [(c, k) for k in shards for c in comps if not out_path(c, k).exists()]
    log(f'b1_xall: job {me}, {len(todo)} of {len(shards) * len(comps)} units to do, budget {budget} min')
    if not todo: return None
    C = x2.tiny_ctx() if tiny else s13.Ctx()
    env = dict(getattr(C, 'env', {}), b1_script_sha256=s10.sha_file(__file__), job=me, xp_layers=s13.XP_LAYERS, ps_layers=s13.PS_LAYERS)
    last = {}
    for comp, k in todo:
        f = out_path(comp, k)
        if f.exists(): continue
        est = 1.5 * max(last.get(comp, 0), 60 if tiny else 300) / 60
        if budget is not None and (time.monotonic() - t0) / 60 + est > budget: log('time budget reached; stop before', comp, k); break
        if not tiny and not claim(comp, k, me): log('claimed by another job, skip', comp, k); continue
        t1 = time.monotonic()
        try:
            d = compute(C, comp, k, tiny)
            meta = dict(env, unit=[comp, k], created=time.strftime('%Y-%m-%dT%H:%M:%S'))
            if comp == 'x2': meta['subspace_sha256'] = _SUB['sha']
            save(f, d, meta)
        except Exception as e:                                                  # non-fatal: log and go on
            R['logs'].mkdir(parents=True, exist_ok=True)
            (R['logs'] / f'b1_xall_error_{comp}_{k:03d}_{me}.txt').write_text(traceback.format_exc()); log('UNIT ERROR (logged, continue):', comp, k, repr(e)); continue
        last[comp] = time.monotonic() - t1
        log(f'b1_xall {comp} shard {k:03d} rows={len(d["paper_id"])} pairs={len(set(d["paper_id"].tolist()))} {last[comp]:.0f}s total={(time.monotonic() - t0) / 60:.1f}min')
    return C


def tiny():
    """whole pipeline on the tiny model; author-0 rows must equal the frozen functions' output exactly (CPU fp32)."""
    set_root(True); tag = os.environ.get('B1_TAG', f'local{os.getpid()}')
    R['raw'] = R['root'] / f'raw/b1_xall_{tag}'          # fresh per tiny job (no stale units)
    smp, pairs = s13.sample(); sh = int(smp.shard.iloc[0])
    _, toks = s11.cohort(); nctx = toks.groupby('paper_id').author_index.nunique()
    s = smp[(smp.shard == sh) & smp.paper_id.isin(pairs.index)].copy(); s['na'] = s.paper_id.map(nctx)
    sp = pairs.loc[s.paper_id].split.to_numpy()
    pick = pd.concat([s[(sp == 'tune') & (s.na >= 3)].head(2), s[(sp == 'tune') & (s.na == 1)].head(1), s[(sp == 'test') & (s.na >= 3)].head(2), s[(sp == 'test') & (s.na == 2)].head(1)])
    s13._CACHE['smp'] = pick.drop(columns='na'); s13.XP_LAYERS = [0, 1]; s13.PS_LAYERS = [0, 1]; s13.LAYERS = [0, 1]
    log('tiny papers', pick[['paper_id', 'na']].values.tolist())
    C = run([sh], COMPS, tiny=True) or x2.tiny_ctx()
    ok = []
    def check(n, c, det=''): ok.append(bool(c)); print('PASS' if c else 'FAIL', n, det, flush=True)
    new = {c: pd.DataFrame({k: v for k, v in np.load(out_path(c, sh)).items() if k != 'meta'}) for c in COMPS}
    for c in COMPS:
        exp = int(pick[pick.paper_id.isin(set(new[c].paper_id))].na.sum())
        check(f'{c}: one row per author context', len(new[c]) == exp and (len(new[c]) == int(pick.na.sum()) or c == 'para'), f'{len(new[c])} rows vs {exp} contexts of {new[c].paper_id.nunique()} pairs (picked {int(pick.na.sum())})')
    # reference = the frozen first-author functions on the same tiny model
    ref = {'xpatch': s13.do_xpatch(C, sh), 'pscope': s13.do_pscope(C, sh), 'para': s13.do_para_run(C, sh)}
    SUB, MU = x2.load_subspaces(C, R['sub_old'], [0, 1]); ref['x2'] = x2.do_x2(C, sh, [0, 1], SUB, MU)
    refdir = R['root'] / f'raw/ref_first_{tag}'
    for c in COMPS:
        d = {k: v for k, v in ref[c].items() if not (c == 'para' and k == 'resid')}
        save(refdir / c / f'shard_{sh:03d}.npz', d, dict(tiny=True))
        rf = pd.DataFrame({k: v for k, v in d.items() if np.ndim(v) == 1 and len(v) == len(d['paper_id'])})
        nf = new[c][new[c].author_index == 0].set_index('paper_id').loc[rf.paper_id]
        cols = [k for k in rf.columns if k in nf.columns and k not in ('paper_id', 'partner', 'random_c', 'split', 'lexical_neighbour') and rf[k].dtype.kind == 'f']
        dmax = max(float(np.abs(nf[k].to_numpy(float) - rf[k].to_numpy(float)).max()) for k in cols)
        check(f'{c}: author-0 rows == frozen function ({len(cols)} columns, {len(rf)} pairs)', dmax == 0.0, f'max |diff| {dmax:.3g}')
    x = new['xpatch']
    check('xpatch: authors differ in score (non-trivial per-author scoring)', x.groupby('paper_id').clean.nunique().max() > 1)
    check('x2: new S_auth columns present', all(f'carry_authall@{l}' in new['x2'] and f'remove_authall@{l}' in new['x2'] for l in (0, 1)))
    check('x2: new S_auth differs from old', float(np.abs(new['x2']['carry_authall@0'] - new['x2']['carry_auth@0']).max()) > 0)   # layer 1 = last layer: title patches cannot reach the readout
    check('n_authors consistent', all((new[c].groupby('paper_id').author_index.count() == new[c].groupby('paper_id').n_authors.first()).all() for c in COMPS))
    print(f'TINY GPU-CODE {"PASS" if all(ok) else "FAIL"}: {sum(ok)}/{len(ok)}'); sys.exit(0 if all(ok) else 1)


def main():
    a = sys.argv[1:]
    mm = float(a[a.index('--max-minutes') + 1]) if '--max-minutes' in a else None
    comps = COMPS
    if '--comps' in a:
        comps = []
        for x in a[a.index('--comps') + 1:]:
            if x.startswith('--'): break
            comps.append(x)
    if '--tiny' in a: tiny(); return
    set_root(False)
    if '--all' in a:
        smp, _ = s13.sample(); run(sorted(int(x) for x in smp.shard.unique()), comps, max_minutes=mm); return
    if '--shards' in a:
        ks = []
        for x in a[a.index('--shards') + 1:]:
            if x.startswith('--'): break
            ks.append(int(x))
        run(ks, comps, max_minutes=mm); return
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
