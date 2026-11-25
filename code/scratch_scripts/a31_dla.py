#!/usr/bin/env python3
"""Addendum 31 (direct logit attribution + per-paper late trajectories). Locked prereg: 391_groups/config/prereg_addendum31.md.

Sample: the Stage 11 sample (361_stage11/config/sample.parquet, 1,186 papers, 593 target / 593 control, 24 shards).
work (GPU): per paper, the TRUE Stage 10 prompt + each author's name (teacher forcing), batch = the paper's authors (right-padded).
  At every name-token position p (predicting name token j) record
    - the final output rank and logit of the true token t, and the top competitor c* (argmax of the final logits over tokens != t);
    - for l = 40..63: logit-lens rank of t (model's final RMSNorm + lm_head applied to the block-l output);
    - for every layer l = 0..63 the direct contributions of attention output a_l and MLP output m_l to the final logit of t and to
      the margin logit(t) - logit(c*):  DLA_c = r * <c, g * (W_U[t] (- W_U[c*]))>, r = rsqrt(mean(h63^2) + eps) of the final
      residual h63 (exact linearisation of the final RMSNorm for fixed r); embedding contribution likewise (exactness check).
  Stored layers 40..63 (+ sums over 0..39) -> raw/a31/{tok,lay}/shard_KKK.parquet, meta/shard_KKK.json.
analyze: rise-then-fall (RTF) per paper on the first author's surname-first token (primary) and on all name tokens (secondary),
  shares target / control and T - C within citation bins, team bootstrap 2,000 (seed 31); components of the fall; C29 consistency.
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'; R11 = BASE / '361_stage11'
PREREG = G / 'config/prereg_addendum31.md'
OUT = Path(os.environ.get('A31_OUT', G / 'raw/a31')); SUMM = Path(os.environ.get('A31_SUM', G / 'summary_a31'))
LAYS = list(range(40, 64)); SEED = 31; NB = 2000; THR = 0.301


def _load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


a16 = _load(H / '14_groups/prereg16_a16.py', 'a16_frozen_for_a31'); s10 = a16.s10; R10 = a16.R10
s11 = _load(H / '11_stage11/361_stage11.py', 's11_frozen_for_a31')


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def lock_check():
    lk = json.load(open(G / 'config/addendum31_lock.json')); h = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    if h != lk['sha256']: raise SystemExit(f'addendum 31 changed after lock: {h}')
    return h


def sample():
    import pandas as pd
    return pd.read_parquet(R11 / 'config/sample.parquet')


class Ctx:
    def __init__(self, tiny=False):
        import torch
        self.torch = torch; self.S = sample()
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
        self.pr = s10.condition_prompts(R10, self.papers, 'true')[0]
        self.hf, self.model, self.tok = a16.load_model(tiny=tiny); self.dev = next(self.hf.parameters()).device
        self.blocks = self.hf.model.layers; self.norm = self.hf.model.norm; self.WU = self.hf.lm_head.weight
        self.g = self.norm.weight.float(); self.eps = float(getattr(self.norm, 'variance_epsilon', 1e-6))


def do_paper(C, pid):
    torch = C.torch; ids = C.pr[pid][1]; T = len(ids); items = C.ctx[pid]
    seqs = [ids + name[:-1] for _, _, name in items]; Lmax = max(len(s) for s in seqs); B = len(seqs); pad = C.tok.pad_token_id
    x = torch.full((B, Lmax), pad, dtype=torch.long); m = torch.zeros((B, Lmax), dtype=torch.long)
    for i, s in enumerate(seqs): x[i, :len(s)] = torch.tensor(s); m[i, :len(s)] = 1
    pos = [[T - 1 + j for j in range(len(name))] for _, _, name in items]
    rec = {}; hs = []
    def grab(key):
        def f(mod, inp, out):
            h = out if torch.is_tensor(out) else out[0]; rec[key] = h.detach(); return out
        return f
    hs.append(C.hf.model.embed_tokens.register_forward_hook(grab(('emb',))))
    for l in range(64):
        hs.append(C.blocks[l].self_attn.register_forward_hook(grab(('attn', l))))
        hs.append(C.blocks[l].mlp.register_forward_hook(grab(('mlp', l))))
        if l in LAYS: hs.append(C.blocks[l].register_forward_hook(grab(('res', l))))
    try:
        with torch.inference_mode(): logits = C.hf(input_ids=x.to(C.dev), attention_mask=m.to(C.dev)).logits
    finally:
        for h in hs: h.remove()
    trow, lrow = [], []
    with torch.inference_mode():
        for i, (ai, rids, name) in enumerate(items):
            p = torch.tensor(pos[i], device=logits.device); t = torch.tensor(name, device=logits.device)
            lg = logits[i, p].float(); tl = lg.gather(1, t[:, None])[:, 0]
            rank = (lg > tl[:, None]).sum(1) + 1
            lg2 = lg.clone(); lg2.scatter_(1, t[:, None], float('-inf')); comp = lg2.argmax(1)
            h63 = rec[('res', 63)][i, p].float(); r = torch.rsqrt(h63.pow(2).mean(-1) + C.eps)
            ut = C.WU[t].float() * C.g; uc = C.WU[comp].float() * C.g; um = ut - uc
            def dla(v): return (r * (v.float() * ut).sum(-1)), (r * (v.float() * um).sum(-1))
            e_l, e_m = dla(rec[('emb',)][i, p]); tot_l = e_l.clone(); tot_m = e_m.clone(); lo_l = torch.zeros_like(e_l); lo_m = torch.zeros_like(e_m)
            per = {}
            for l in range(64):
                al, am = dla(rec[('attn', l)][i, p]); ml, mm = dla(rec[('mlp', l)][i, p])
                tot_l += al + ml; tot_m += am + mm
                if l < 40: lo_l += al + ml; lo_m += am + mm
                else: per[l] = (al, am, ml, mm)
            for l in LAYS:
                hl = rec[('res', l)][i, p]
                ll = (C.norm(hl) @ C.WU.T).float() if l < 63 else lg
                tll = ll.gather(1, t[:, None])[:, 0]; rk = (ll > tll[:, None]).sum(1) + 1
                al, am, ml, mm = per[l]
                for j in range(len(name)):
                    lrow.append(dict(paper_id=pid, author_index=ai, token_index=j, row_id=int(rids[j]), layer=l, lens_rank=int(rk[j]),
                                     dla_attn_logit=float(al[j]), dla_mlp_logit=float(ml[j]), dla_attn_margin=float(am[j]), dla_mlp_margin=float(mm[j])))
            for j in range(len(name)):
                trow.append(dict(paper_id=pid, author_index=ai, token_index=j, row_id=int(rids[j]), token_id=int(name[j]), final_rank=int(rank[j]),
                                 final_logit=float(tl[j]), competitor=int(comp[j]), final_margin=float(tl[j] - lg[j, comp[j]]),
                                 dla_sum_logit=float(tot_l[j]), dla_sum_margin=float(tot_m[j]), dla_below40_logit=float(lo_l[j]), dla_below40_margin=float(lo_m[j])))
    return trow, lrow


def out_path(kind, k, ext='parquet'): return OUT / kind / f'shard_{k:03d}.{ext}'


def do_shard(C, k):
    import pandas as pd
    if out_path('meta', k, 'json').exists(): log(f'shard {k} skip (exists)'); return False
    pids = C.S[C.S.shard == k].paper_id.tolist(); t0 = time.time(); T_, L_ = [], []
    for pid in pids:
        a, b = do_paper(C, pid); T_ += a; L_ += b
    tdf, ldf = pd.DataFrame(T_), pd.DataFrame(L_)
    for kind, df in (('tok', tdf), ('lay', ldf)):
        out_path(kind, k).parent.mkdir(parents=True, exist_ok=True); df.to_parquet(out_path(kind, k), index=False)
    rel = (tdf.dla_sum_logit - tdf.final_logit).abs() / tdf.final_logit.abs().clip(lower=1.0)
    chk = dict(papers=len(pids), tokens=len(tdf), exact_rel_err_median=float(rel.median()), exact_share_rel_le_0p02=float((rel <= 0.02).mean()))
    try:
        z = [np.load(f) for f in sorted((R10 / 'raw/final/L63').glob('shard_*.npz'))]
        ref = pd.Series(np.concatenate([zz['rank'] for zz in z]), index=np.concatenate([zz['row_id'] for zz in z]))
        rr = ref.reindex(tdf.row_id).to_numpy(float); okm = ~np.isnan(rr)
        chk['final_rank_vs_stage10_equal_share'] = float((tdf.final_rank.to_numpy()[okm] == rr[okm]).mean())
        chk['final_rank_vs_stage10_mean_abs_dlog10'] = float(np.abs(np.log10(tdf.final_rank.to_numpy()[okm]) - np.log10(rr[okm])).mean())
    except Exception as e: chk['stage10_error'] = repr(e)
    chk['status'] = 'PASS' if chk['exact_share_rel_le_0p02'] >= 0.99 and chk.get('final_rank_vs_stage10_equal_share', 0) >= 0.75 else 'WARN'
    meta = dict(shard=k, seconds=time.time() - t0, checks=chk, host=os.uname().nodename, job=os.environ.get('SLURM_JOB_ID'),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out_path('meta', k, 'json').parent.mkdir(parents=True, exist_ok=True); json.dump(meta, open(out_path('meta', k, 'json'), 'w'), indent=1)
    log(f'shard {k} done papers={len(pids)} {time.time() - t0:.0f}s', json.dumps(chk)); return True


def parse_shards(s):
    out = []
    for p in str(s).split(','):
        if '-' in p: a_, b_ = p.split('-'); out += list(range(int(a_), int(b_) + 1))
        elif p: out.append(int(p))
    return out


def work(a, C=None):
    if C is None: lock_check(); C = Ctx()
    t_start = time.time(); per = []
    for k in parse_shards(a.shards):
        if k not in set(C.S.shard): continue
        if a.max_minutes and per and (time.time() - t_start + 1.3 * max(per)) / 60 > a.max_minutes: log('budget stop before shard', k); break
        t0 = time.time()
        if do_shard(C, k): per.append(time.time() - t0)


def missing(): return [k for k in sorted(sample().shard.unique()) if not out_path('meta', k, 'json').exists()]


# ------------------------------------------------------------------ analysis
def team_W(teams):
    import pandas as pd
    codes, uniq = pd.factorize(pd.Series(teams))
    cnt = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)
    return cnt[:, codes]


def ci(b):
    b = b[np.isfinite(b)]
    return (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))) if len(b) else (float('nan'), float('nan'))


def wmean(W, idx, v):
    Wi = W[:, idx]; return (Wi @ v) / Wi.sum(1)


def within(df, col, W):
    num, den, bn, bd = 0.0, 0.0, np.zeros(W.shape[0]), 0.0
    for _, g in df.groupby('citation_bin'):
        it = (g.group == 'target').to_numpy(); ic = (g.group == 'control').to_numpy()
        if it.sum() == 0 or ic.sum() == 0: continue
        w = it.sum() * ic.sum() / (it.sum() + ic.sum()); v = g[col].to_numpy(float); idx = g.index.to_numpy()
        num += w * (v[it].mean() - v[ic].mean()); den += w; bn += w * (wmean(W, idx[it], v[it]) - wmean(W, idx[ic], v[ic])); bd += w
    if den == 0: return float('nan'), np.full(W.shape[0], np.nan)
    return num / den, bn / bd


def rtf_table(lay, tok_sel):
    """per token: y_l = log10(1/rank) at 56..62 (lens) and 63 (final); RTF flag; peak layer."""
    import pandas as pd
    L = lay.merge(tok_sel[['row_id']], on='row_id')
    Y = L.pivot_table(index='row_id', columns='layer', values='lens_rank'); Y = -np.log10(Y)
    mid = Y[list(range(57, 63))]; mx = mid.max(1); pk = mid.idxmax(1)
    rtf = ((mx - Y[56]) >= THR) & ((mx - Y[63]) >= THR)
    return pd.DataFrame({'rtf': rtf.astype(float), 'peak': pk, 'y56': Y[56], 'ymax': mx, 'y63': Y[63]})


def analyze(a=None):
    import pandas as pd
    h = lock_check(); c13 = _load(H / '13_stage13/stage13_cpu.py', 'c13_for_a31')
    S = sample(); papers, _ = s11.cohort(); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    tok = pd.concat([pd.read_parquet(f) for f in sorted((OUT / 'tok').glob('shard_*.parquet'))])
    lay = pd.concat([pd.read_parquet(f) for f in sorted((OUT / 'lay').glob('shard_*.parquet'))])
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'role', 'author_index'])
    tok = tok.merge(nt[['row_id', 'role']], on='row_id', how='left')
    prim = tok[(tok.author_index == 0) & (tok.role == 'surname_first')]
    res = {}; out_rows = []
    for name, sel in (('primary: first author surname-first token', prim), ('secondary: all name tokens', tok)):
        R = rtf_table(lay, sel).join(sel.set_index('row_id')[['paper_id']])
        Pp = R.groupby('paper_id').rtf.mean().rename('rtf').reset_index().merge(S[['paper_id', 'group', 'citation_bin']], on='paper_id')
        Pp['team'] = Pp.paper_id.map(TEAM); W = team_W(Pp.team.to_numpy())
        it = (Pp.group == 'target').to_numpy(); v = Pp.rtf.to_numpy(float)
        sT, sC = v[it].mean(), v[~it].mean(); bT, bC = wmean(W, np.where(it)[0], v[it]), wmean(W, np.where(~it)[0], v[~it])
        d, bd = within(Pp.reset_index(drop=True), 'rtf', W)
        row = dict(token_set=name, n_papers=len(Pp), share_target=sT, t_lo=ci(bT)[0], t_hi=ci(bT)[1], share_control=sC, c_lo=ci(bC)[0], c_hi=ci(bC)[1],
                   tc_within_bin=d, tc_lo=ci(bd)[0], tc_hi=ci(bd)[1])
        if row['tc_hi'] < 0: v_ = 'Reversed (control has more rise-then-fall)'
        elif sT >= 0.10 and row['t_lo'] > 0.05 and row['tc_lo'] > 0: v_ = 'Late-suppression subgroup specific to recognised papers'
        elif row['t_lo'] > 0.05: v_ = 'Late-suppression subgroup present, not specific to recognised papers'
        else: v_ = 'Small / absent (target share CI lower bound <= 0.05)'
        row['reading'] = v_; out_rows.append(row); res[name] = row
        if name.startswith('primary'): Rprim = R
    T1 = pd.DataFrame(out_rows); SUMM.mkdir(parents=True, exist_ok=True); T1.to_csv(SUMM / 'a31_rtf.csv', index=False)
    # components of the fall (primary RTF tokens): sum over layers > peak .. 63 of DLA margin, attention vs MLP
    L = lay.merge(prim[['row_id']], on='row_id').merge(Rprim[['peak', 'rtf']].reset_index(), on='row_id')
    L['after'] = L.layer > L.peak
    F = L[(L.rtf == 1) & L.after].groupby('row_id')[['dla_attn_margin', 'dla_mlp_margin']].sum()
    comp = dict(n_rtf_tokens=int(len(F)), attn_after_peak_mean=float(F.dla_attn_margin.mean()) if len(F) else None,
                mlp_after_peak_mean=float(F.dla_mlp_margin.mean()) if len(F) else None)
    # per-layer DLA means by group (all primary tokens), and C29 consistency (sum 57..61 MLP - attention, logit version)
    Lg = lay.merge(prim[['row_id']], on='row_id').merge(S[['paper_id', 'group']], on='paper_id')
    per = Lg.groupby(['group', 'layer'])[['dla_attn_logit', 'dla_mlp_logit', 'dla_attn_margin', 'dla_mlp_margin']].mean()
    per.to_csv(SUMM / 'a31_dla_by_layer.csv')
    c29 = Lg[Lg.layer.between(57, 61)].groupby('paper_id').apply(lambda g: (g.dla_mlp_logit - g.dla_attn_logit).sum()).rename('d').reset_index()
    c29['team'] = c29.paper_id.map(TEAM); W = team_W(c29.team.to_numpy()); bd = (W @ c29.d.to_numpy()) / W.sum(1)
    comp['C29_sum57_61_mlp_minus_attn_logit'] = float(c29.d.mean()); comp['C29_ci'] = ci(bd)
    chk = [json.load(open(f))['checks'] for f in sorted((OUT / 'meta').glob('shard_*.json'))]
    res.update(dict(components=comp, addendum_sha256=h, missing_shards=missing(), checks_status=pd.Series([c['status'] for c in chk]).value_counts().to_dict(),
                    min_exact_share=min(c['exact_share_rel_le_0p02'] for c in chk), min_stage10_equal=min(c.get('final_rank_vs_stage10_equal_share', np.nan) for c in chk)))
    json.dump(res, open(SUMM / 'a31_results.json', 'w'), indent=1, default=float)
    md = ['# Addendum 31 (LOCKED) — direct logit attribution and late trajectories', '', f'prereg sha256 {h}; missing shards {res["missing_shards"]}', '',
          T1.to_string(index=False), '', '## Components', '', json.dumps(comp, indent=1, default=float), '', '## Per-layer DLA (group means)', '', per.to_string()]
    (SUMM / 'a31_report.md').write_text('\n'.join(md) + '\n'); log('A31 ANALYSIS', json.dumps({k: res[k]['reading'] for k in res if isinstance(res[k], dict) and 'reading' in res[k]}))
    return res


def tiny(a):
    import pandas as pd
    global OUT, SUMM
    root = Path(a.root); OUT = root / 'raw'; SUMM = root / 'summary'
    C = Ctx(tiny=True)
    keep = C.S[C.S.group == 'target'].head(1).paper_id.tolist() + C.S[C.S.group == 'control'].head(1).paper_id.tolist()
    C.S = C.S[C.S.paper_id.isin(keep)].copy(); C.S['shard'] = [0, 1]
    work(argparse.Namespace(shards='0-1', max_minutes=None), C); work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    tok = pd.concat([pd.read_parquet(out_path('tok', k)) for k in (0, 1)]); lay = pd.concat([pd.read_parquet(out_path('lay', k)) for k in (0, 1)])
    m = [json.load(open(out_path('meta', k, 'json'))) for k in (0, 1)]
    ok = {'tok rows > 0': len(tok) > 0, 'lay rows = tok x 24': len(lay) == 24 * len(tok),
          'exact decomposition (rel err <= 2% for >= 95% tokens, tiny fp32/bf16)': all(x['checks']['exact_share_rel_le_0p02'] >= 0.95 for x in m),
          'L63 lens rank == final rank': bool((lay[lay.layer == 63].set_index('row_id').lens_rank == tok.set_index('row_id').final_rank).all())}
    print('TINY CHECKS', json.dumps(ok), json.dumps([x['checks'] for x in m]), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'tiny', 'remaining', 'analyze']); ap.add_argument('--shards', default='0')
    ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'remaining': mm = missing(); print(len(mm), 'missing', mm); return
    {'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
