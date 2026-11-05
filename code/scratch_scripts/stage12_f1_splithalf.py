"""Stage 12 F1 author-prompt lens split-half (handbook V50 / U42; user-approved 2026-11-05). Not pre-registered: post-hoc
quality check of the F1 lens (no prereg file covers it; the comparison metrics below were fixed before any half was fitted).

Halves: the 40 frozen F1 fit prompts (371_stage12/config/fit_prompts.parquet, already in random draw order, seed 12) ->
A = rows 0-19, B = rows 20-39. Each half is fitted with exactly the Stage 12 F1 procedure (371_stage12.fit_step:
jlens.fit(source_layers=FIT_LAYERS, target_layer=63, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_every=1)),
resumable, into 371_stage12/alens_half_{A,B}/.
Readout (F2 style, 371_stage12.do_alens_read with each half lens): Stage 11 sample, 6 title conditions, name positions
and the last title token, FIT_LAYERS -> raw/alens_half_read/<cond>/shard_k.npz (keys halfA@l@pos, halfB@l@pos).
Comparison (analyze, CPU): per layer cos(vec J_A, vec J_B), A/B vs the full F1 lens and the WikiText lenses; linearity
check (20 J_A + 20 J_B)/40 == full F1 (WARN only, GPU fp32 accumulation order); F2 estimand (true - mean of 5 false,
paper means, target / control / within-bin target - control) per lens and its A-B agreement (correlation of per-paper
values, per-token Spearman, share of identical ranks), on the same papers as F2 (alens_eval_exclude applied).
Commands: fit --half A|B | read | tiny --root DIR | analyze"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('s12', H / '12_stage12/371_stage12.py'); s12 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s12)
s11, s10 = s12.s11, s12.s10
R12 = Path('/scratch/zhang.zhiqi2/jlens/371_stage12')
HALVES = {'A': slice(0, 20), 'B': slice(20, 40)}
log = s11.log


def half_prompts(h):
    import pandas as pd
    fp = pd.read_parquet(R12 / 'config/fit_prompts.parquet'); return fp.text.tolist()[HALVES[h]], fp.iloc[HALVES[h]]


def fit_half(C, h, root, budget_min, layers=None, n_total=None):
    import jlens
    prompts, fp = half_prompts(h); n_total = n_total or len(prompts); prompts = prompts[:n_total]; layers = layers or s12.FIT_LAYERS
    d = root / f'alens_half_{h}'; d.mkdir(parents=True, exist_ok=True); cp = d / 'checkpoint.pt'
    if (d / 'lens.pt').exists(): log(f'half {h}: lens exists'); return
    (d / 'halves.json').write_text(json.dumps(dict(half=h, rows=[HALVES[h].start, HALVES[h].stop], paper_ids=fp.paper_id.tolist(),
                                                   groups=fp.group_tight.value_counts().to_dict()), indent=1))
    prog = json.loads((d / 'progress.json').read_text())['done'] if (d / 'progress.json').exists() else 0
    n = max(1, int((budget_min - 4) / 5)); target = min(n_total, prog + n)
    log(f'F1 half {h}: {prog} -> {target} of {n_total} (budget {budget_min:.0f} min)'); t0 = time.monotonic()
    lens = jlens.fit(C.model, prompts[:target], source_layers=layers, target_layer=len(C.model.layers) - 1, dim_batch=1, max_seq_len=128, skip_first=16,
                     checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
    (d / 'progress.json').write_text(json.dumps(dict(done=lens.n_prompts, updated=s11.now(), seconds=round(time.monotonic() - t0),
                                                     per_prompt=round((time.monotonic() - t0) / max(1, lens.n_prompts - prog)))))
    if lens.n_prompts >= n_total:
        tmp = d / 'lens.tmp.pt'; lens.save(str(tmp)); os.replace(tmp, d / 'lens.pt'); log(f'half {h} lens COMPLETE ({lens.n_prompts} prompts)')


def load_half(C, h, root):
    import jlens
    L = jlens.JacobianLens.load(str(root / f'alens_half_{h}/lens.pt'))
    for k in list(L.jacobians): L.jacobians[k] = L.jacobians[k].to(s10.layer_device(C.model, k))
    return L


def do_read(C, LS, cond, shard, layers):
    """371_stage12.do_alens_read with several lenses in one forward."""
    torch = C.torch; prompts = C.prompts[cond]
    out = {f'{n}@{l}@{p}': [] for n in LS for l in layers for p in ('name', 'title')}; rows = []
    from jlens.hooks import ActivationRecorder
    for r in C.smp[C.smp.shard == shard].itertuples():
        ptx, pids = prompts[r.paper_id]; it = s11.title_positions(C.tok, ptx, pids)[-1]
        for ai, rids, name in C.ctx[r.paper_id]:
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]; g = torch.tensor(name, device=C.model.input_device)
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=layers) as rec:
                C.model.forward(torch.tensor([ids], device=C.model.input_device))
                for n, L in LS.items():
                    for l in layers:
                        h = rec.activations[l][0]
                        lg = C.model.unembed(L.transport(h[pos].float(), l)).float(); out[f'{n}@{l}@name'].append(s11.ranks(lg, g, torch))
                        lt = C.model.unembed(L.transport(h[it:it + 1].float(), l)).float().expand(len(name), -1); out[f'{n}@{l}@title'].append(s11.ranks(lt, g, torch))
            rows += rids
    return dict(row_id=np.array(rows), **{k: np.concatenate(v) for k, v in out.items()})


def read(C, root, budget_min, layers=None, shards=None, conds=None):
    layers = layers or s12.FIT_LAYERS; LS = {'halfA': load_half(C, 'A', root), 'halfB': load_half(C, 'B', root)}
    t0 = time.monotonic(); last = 30
    for c in conds or s12.TC:
        for k in shards if shards is not None else range(24):
            f = root / f'raw/alens_half_read/{c}/shard_{k:03d}.npz'
            if f.exists(): continue
            if (time.monotonic() - t0 + 1.5 * last) / 60 > budget_min: log('budget reached'); return
            t1 = time.monotonic(); d = do_read(C, LS, c, k, layers); f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(created=s11.now(), **getattr(C, 'env', {})))), **d); os.replace(tmp, f)
            last = time.monotonic() - t1
            try: log(f'alens_half_read {c} shard {k:03d} rows={len(d["row_id"])} {last:.0f}s')
            except Exception as e: print('log warning', repr(e), flush=True)
    log('read: all units done')


class GCtx:
    def __init__(self):
        import torch, pandas as pd
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(s11.R10, self.papers, c)[0] for c in s12.TC}
        self.smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])


def budget(default):
    left = s11.slurm_minutes_left(); return default if left is None else min(default, left - 6)


def tiny(root):
    import torch, transformers, jlens, pandas as pd
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 3; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:3]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {c: s10.condition_prompts(s11.R10, C.papers, c)[0] for c in ('true', 'false_0')}
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); C.smp = smp[smp.shard.isin([0])].head(2); C.env = {'tiny': True}
    s10.layer_device = lambda model, k: 'cpu'
    for h in 'AB':
        fit_half(C, h, root, budget_min=9, layers=[0, 1], n_total=2)     # 1 prompt in the first call (budget) ...
        fit_half(C, h, root, budget_min=60, layers=[0, 1], n_total=2)    # ... resumed to 2
    read(C, root, 60, layers=[0, 1], shards=[0], conds=['true', 'false_0'])
    z = np.load(root / 'raw/alens_half_read/true/shard_000.npz')
    A = jlens.JacobianLens.load(str(root / 'alens_half_A/lens.pt')); B = jlens.JacobianLens.load(str(root / 'alens_half_B/lens.pt'))
    ok = A.n_prompts == 2 and B.n_prompts == 2 and 'halfB@1@title' in z.files and len(z['row_id']) > 0 and not torch.equal(A.jacobians[0], B.jacobians[0])
    # resume check: the 1 + 1 resumed fit equals a fresh 2-prompt fit of the same half (CPU fp32)
    ref = jlens.fit(C.model, half_prompts('A')[0][:2], source_layers=[0, 1], target_layer=2, dim_batch=1, max_seq_len=128, skip_first=16, checkpoint_path=None)
    dres = max(float((ref.jacobians[l] - A.jacobians[l]).abs().max()) for l in (0, 1)); ok &= dres < 1e-4
    print('TINY', 'PASS' if ok else 'FAIL', 'resume max|d|', dres, {k: z[k].shape for k in list(z.files)[:4]}); sys.exit(0 if ok else 1)


# ------------------------------------------------------------------ analysis (CPU)
def analyze(root):
    import torch, pandas as pd, jlens
    sp = importlib.util.spec_from_file_location('s12a', H / '12_stage12/stage12_analyze.py'); a12 = importlib.util.module_from_spec(sp); sp.loader.exec_module(a12)
    W = []
    def warn(m): W.append(m); print('WARN', m, flush=True)
    LA = jlens.JacobianLens.load(str(root / 'alens_half_A/lens.pt')); LB = jlens.JacobianLens.load(str(root / 'alens_half_B/lens.pt'))
    LF = jlens.JacobianLens.load(str(R12 / 'alens/lens.pt'))
    reg = json.loads((s11.R10 / 'config/lenses.json').read_text())
    other = {k: jlens.JacobianLens.load(v['path']) for k, v in reg.items() if k in ('public', 'fitA')}
    cos = lambda x, y: float((x.flatten().double() @ y.flatten().double()) / (x.flatten().double().norm() * y.flatten().double().norm()))
    rel = lambda x, y: float((x - y).double().norm() / y.double().norm())
    eye = torch.eye(LA.jacobians[s12.FIT_LAYERS[0]].shape[0])
    rows = []
    for l in s12.FIT_LAYERS:
        A, B, F = LA.jacobians[l].float(), LB.jacobians[l].float(), LF.jacobians[l].float(); mix = (A * LA.n_prompts + B * LB.n_prompts) / (LA.n_prompts + LB.n_prompts)
        r = dict(layer=l, cos_A_B=cos(A, B), cos_A_full=cos(A, F), cos_B_full=cos(B, F), relfro_A_B=rel(A, B), relfro_mix_full=rel(mix, F),
                 maxabs_mix_full=float((mix - F).abs().max()), cos_A_B_minus_I=cos(A - eye, B - eye))
        for k, Lo in other.items():
            if l in Lo.jacobians:
                O = Lo.jacobians[l].float(); r[f'cos_full_{k}'] = cos(F, O); r[f'cos_A_{k}'] = cos(A, O); r[f'cos_B_{k}'] = cos(B, O)
        rows.append(r)
        if r['relfro_mix_full'] > 1e-3: warn(f'L{l}: (20 J_A + 20 J_B)/40 vs full F1 relative Frobenius {r["relfro_mix_full"]:.2e} (> 1e-3)')
    M = pd.DataFrame(rows); S = R12 / 'summary'; S.mkdir(exist_ok=True); M.to_csv(S / 'f1_splithalf_matrix.csv', index=False)
    # readouts
    toks = pd.read_parquet(s11.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet')
    nlr = lambda x: -np.log10(np.asarray(x, float))
    per, tokd, conds = {}, {}, [c for c in s12.TC if (root / f'raw/alens_half_read/{c}').exists()]
    for c in conds:
        zs = [np.load(f) for f in sorted((root / f'raw/alens_half_read/{c}').glob('shard_*.npz'))]
        hz = {k: np.concatenate([z[k] for z in zs]) for k in zs[0].files if k != 'meta'}
        fz = [np.load(R12 / f'raw/alens_read/{c}/' + f.name) for f in sorted((root / f'raw/alens_half_read/{c}').glob('shard_*.npz'))]
        fz = {k: np.concatenate([z[k] for z in fz]) for k in fz[0].files if k != 'meta'}
        if not np.array_equal(fz['row_id'], hz['row_id']): warn(f'{c}: row ids differ from stored F2')
        df = pd.DataFrame({'row_id': hz['row_id'], **{k: nlr(v) for k, v in hz.items() if '@' in k}, **{'full@' + k.split('@', 1)[1]: nlr(v) for k, v in fz.items() if k.startswith('alens@')}})
        tokd[c] = df; per[c] = df.merge(toks, on='row_id').drop(columns='row_id').groupby('paper_id').mean()
    common = per['true'].index
    for c in per: common = common.intersection(per[c].index)
    ex = R12 / 'config/alens_eval_exclude.json'
    if ex.exists(): drop = set(json.loads(ex.read_text())['paper_ids']); common = common[~common.isin(drop)]
    spec = per['true'].loc[common] - sum(per[c].loc[common] for c in per if c != 'true') / (len(per) - 1)
    spj = spec.join(smp.set_index('paper_id'))
    rows = []
    for l in s12.FIT_LAYERS:
        for pos in ('name', 'title'):
            r = dict(layer=l, position=pos, n_papers=len(spj))
            for n in ('halfA', 'halfB', 'full'):
                col = f'{n}@{l}@{pos}'
                for g in ('target', 'control'):
                    m = a12.boot(spj[spj.group == g][col]); r |= {f'{n}_{g}': m[0], f'{n}_{g}_lo': m[1], f'{n}_{g}_hi': m[2]}
                e = a12.strat(spj, col); r |= {f'{n}_tc': e[0], f'{n}_tc_lo': e[1], f'{n}_tc_hi': e[2]}
                r[f'{n}_true_mean'] = per['true'].loc[common][col].mean()
            r['corr_spec_A_B'] = float(np.corrcoef(spj[f'halfA@{l}@{pos}'], spj[f'halfB@{l}@{pos}'])[0, 1])
            r['corr_true_A_B'] = float(np.corrcoef(per['true'].loc[common][f'halfA@{l}@{pos}'], per['true'].loc[common][f'halfB@{l}@{pos}'])[0, 1])
            t = tokd['true']; xa, xb = t[f'halfA@{l}@{pos}'], t[f'halfB@{l}@{pos}']
            r['tok_spearman_A_B'] = float(xa.rank().corr(xb.rank())); r['tok_equal_rank_A_B'] = float((xa == xb).mean())
            r['tok_spearman_A_full'] = float(xa.rank().corr(t[f'full@{l}@{pos}'].rank()))
            r['tc_sign_agree'] = bool(np.sign(r['halfA_tc']) == np.sign(r['halfB_tc']))
            r['tc_ci_excl0_agree'] = bool((r['halfA_tc_lo'] > 0 or r['halfA_tc_hi'] < 0) == (r['halfB_tc_lo'] > 0 or r['halfB_tc_hi'] < 0))
            rows.append(r)
    F = pd.DataFrame(rows); F.to_csv(S / 'f1_splithalf_readout.csv', index=False)
    fm = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
    pa = json.loads((root / 'alens_half_A/halves.json').read_text()); pb = json.loads((root / 'alens_half_B/halves.json').read_text())
    L = ['# Stage 12 F1: author-prompt lens split-half (V50)', '',
         'Handbook V50 / U42 (F1 lens vs WikiText lens cosine 0.27-0.70 at L24-L48: prompt distribution or 40-prompt noise?). User-approved 2026-11-05. '
         '**Post-hoc** (no pre-registration covers F1 split-half). Script `12_stage12/stage12_f1_splithalf.py` (imports `371_stage12.py` by path; fit = the Stage 12 F1 procedure).', '',
         f'Halves of the 40 frozen fit prompts (draw order, seed 12): A = rows 0-19 (groups {pa["groups"]}), B = rows 20-39 (groups {pb["groups"]}). '
         f'Fitted prompts: A {LA.n_prompts}, B {LB.n_prompts}, full F1 {LF.n_prompts}. Readout: Stage 11 sample, conditions {conds}, {len(common)} papers (F2 exclusions applied).', '',
         '## Checks', '', *(['- WARN: ' + w for w in W] or ['- No WARN.']),
         f'- Linearity: (20 J_A + 20 J_B)/40 vs full F1, max relative Frobenius over layers {M.relfro_mix_full.max():.2e}, max |entry diff| {M.maxabs_mix_full.max():.2e}.', '',
         '## Matrix agreement per layer (cosine of the flattened 5120 x 5120 matrices)', '',
         '| layer | A vs B | A vs full | B vs full | (A-I) vs (B-I) | rel. Frobenius A-B | full vs WikiText public | A vs public | B vs public | full vs Stage 9 fitA | A vs fitA | B vs fitA |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    g = lambda r, k: '-' if k not in r or pd.isna(r[k]) else f'{r[k]:.3f}'
    for _, r in M.iterrows():
        L.append(f'| L{int(r.layer)} | {r.cos_A_B:.3f} | {r.cos_A_full:.3f} | {r.cos_B_full:.3f} | {r.cos_A_B_minus_I:.3f} | {r.relfro_A_B:.3f} | ' + ' | '.join(g(r, k) for k in ('cos_full_public', 'cos_A_public', 'cos_B_public', 'cos_full_fitA', 'cos_A_fitA', 'cos_B_fitA')) + ' |')
    L += ['', '## F2 readout with each lens', '', 'Title-specific signal = true - mean(5 false), mean log10(1/rank) per paper; target / control paper bootstrap, target - control within citation bin (stage12_analyze.boot / strat).', '',
          '| pos | layer | A target | B target | full target | A control | B control | full control | A t-c | B t-c | full t-c | corr A,B (per-paper signal) | corr A,B (per-paper true score) | token Spearman A,B (true) | same rank A,B |', '|' + '---|' * 15]
    for _, r in F.sort_values(['position', 'layer']).iterrows():
        L.append(f'| {r.position} | L{int(r.layer)} | ' + ' | '.join(fm(r[f'{n}_{g_}'], r[f'{n}_{g_}_lo'], r[f'{n}_{g_}_hi']) for g_ in ('target', 'control', 'tc') for n in ('halfA', 'halfB', 'full'))
                 + f' | {r.corr_spec_A_B:.3f} | {r.corr_true_A_B:.3f} | {r.tok_spearman_A_B:.3f} | {r.tok_equal_rank_A_B:.3f} |')
    L += ['', f'Target - control sign agreement A vs B: {int(F.tc_sign_agree.sum())}/{len(F)} rows; same "CI excludes 0" call: {int(F.tc_ci_excl0_agree.sum())}/{len(F)}.', '', '## Conclusion', '', '<!--CONCLUSION-->', '']
    (R12 / 'reports/f1_splithalf.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fit', 'read', 'tiny', 'analyze']); ap.add_argument('--half', choices=['A', 'B'])
    ap.add_argument('--root'); ap.add_argument('--minutes', type=float, default=110); a = ap.parse_args()
    root = Path(a.root) if a.root else R12
    if a.cmd == 'tiny': assert a.root; tiny(root); return
    if a.cmd == 'analyze': analyze(root); return
    C = GCtx()
    if a.cmd == 'fit':
        halves = [a.half] if a.half else ['A', 'B']
        for h in halves:
            if not (root / f'alens_half_{h}/lens.pt').exists(): fit_half(C, h, root, budget(a.minutes)); break
    else: read(C, root, budget(a.minutes))


if __name__ == '__main__':
    main()
