"""Addendum 18b item 1 - readout map (position group x layer), GPU driver + CPU analysis. New file 2026-11-17.

Design (addendum 18b item 1, locked; 600-paper subsample per lock amendment 2):
  position groups  title tokens (all / content words / first / last), closing quote ('"', p9 when it is its own token), year
                   digits (the 4 digit tokens), ')?\\n' (p3), 'Authors' (p2), ':' (p1), name positions (surname first token
                   rows = Stage 10 role surname_first, and all name tokens after ':' = token_index >= 1).
  layers           L8, 16, 24, 32, 36, 40..52 (each), 56, 60 (20 layers).
  readouts         logit lens and public J-lens (Stage 10 lens file), gold ranked ONLY among the 9,137 name token ids (as the H3
                   same-scale job; bf16 final norm + bf16 lm_head rows, bf16 logits, rank = 1 + #strictly greater), and probes
                   on the same scale (CPU analysis): name-token ridge probe (addendum 11 A / E4b recipe: ridge from the layer-l
                   residual to the TRUE-title L63 residual - at ':' for prompt positions (E4b), at the same position for the
                   surname-first name position (addendum 11 A); fitted on true-title rows, 5 archived author-team folds,
                   standardisation on the training folds, alpha in (0.1, 1, 10) x trace(G)/d on fold-0 held-out MSE; decoded
                   through the final norm + the 9,137 lm_head rows), attribute probes (year, log citations, field).
  gold             prompt positions: every author's first name token ('first') and surname first token ('surname'), as Stage
                   11 E4; name positions: the next (teacher-forced) name token.
  statistic        per paper mean log10(1/rank) per condition; spec = true - mean of 5 false titles; within-bin target - control
                   of spec; author-team cluster bootstrap 2,000 draws.
  main comparison  per position group and readout: earliest layer with T - C CI > 0. Rule (locked): a group with T - C CI > 0 at
                   some layer <= 48 while the name position (surname first) at that same layer has a CI including 0 ->
                   "shelf first at that position"; otherwise "no earlier position". Primary gold kind for prompt positions =
                   surname first token (same token as the name-position row); 'first' reported beside it.
GPU unit ('main', k), k = 0..23 (25 papers each) -> raw/a18b_item1/main/shard_XXX.npz: lens nlr tables + fp16 residuals (pooled per
prompt group; surname-first positions) + true-title L63 targets for the probe.
Commands: work [--shards S] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, re, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

LAYERS = [8, 16, 24, 32, 36, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 56, 60]
GROUPS = ['title_all', 'title_content', 'title_first', 'title_last', 'quote', 'year', 'close', 'authors', 'colon']
LENSES = ['logit', 'jlens_public']; KINDS = ['first', 'surname']
RAW = Path(os.environ.get('A18B_RAW1', A.R13 / 'raw/a18b_item1')); SUM = Path(os.environ.get('A18B_SUM1', A.R13 / 'summary_a18b_item1'))
_SMP = {}


def smp():
    if 'm' not in _SMP: _SMP['m'] = A.sample()
    return _SMP['m']


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None): return [('main', k) for k in A.parse_shards(shards, 24)]


_SW = None
def stopwords():
    global _SW
    if _SW is None:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        _SW = set(ENGLISH_STOP_WORDS)
    return _SW


def group_positions(C, L):
    """{group: [positions]} for one prompt."""
    ids, text, tpos = L['ids'], L['text'], L['tpos']
    e = C.tok(text, return_offsets_mapping=True); offs = e.offset_mapping
    a = text.index('titled "') + len('titled "'); b = text.rindex('" (')
    title = text[a:b]; content = []
    for p in tpos:
        x, y = max(offs[p][0], a), min(offs[p][1], b)
        # the word(s) this token overlaps
        ws = [m for m in re.finditer(r"[A-Za-z][A-Za-z'-]*|\d+", title) if m.start() + a < y and m.end() + a > x]
        if any(len(m.group()) > 2 and m.group().lower() not in stopwords() and not m.group().isdigit() for m in ws): content.append(p)
    G = {'title_all': list(tpos), 'title_content': content, 'title_first': [tpos[0]], 'title_last': [tpos[-1]]}
    tail = list(range(max(tpos) + 1, len(ids)))
    toks = C.tok.convert_ids_to_tokens([ids[i] for i in tail])
    off = {len(ids) - i: (i, t) for i, t in zip(tail, toks)}
    G['colon'] = [len(ids) - 1]; G['authors'] = [off[2][0]] if 2 in off else []; G['close'] = [off[3][0]] if 3 in off else []
    G['year'] = [i for k, (i, t) in off.items() if 4 <= k <= 7 and t.strip('Ġ').isdigit()]
    G['quote'] = [i for k, (i, t) in off.items() if k >= 8 and t == '"']
    return G


class Lens:
    def __init__(self, C):
        torch = C.torch; self.torch = torch
        vr = np.load(A.R13 / 'summary_alltok/vocab_rows.npz'); self.vid = vr['token_id'].astype(np.int64)
        self.col = {int(t): i for i, t in enumerate(self.vid)}
        W = C.model._lm_head.weight
        self.W = W[torch.tensor(self.vid, device=W.device)].clone()                       # bf16 rows (fp32 for tiny)
        if C.tiny:
            g = torch.Generator().manual_seed(1); d = C.model.d_model
            self.J = {l: (torch.eye(d) + 0.1 * torch.randn(d, d, generator=g)) for l in LAYERS}
        else:
            s10 = A.s11().s10; m, lenses = s10.verify(A.R10)
            Lp = s10.open_lenses(lenses, [('jlens_public', l) for l in LAYERS], C.model)['public']
            self.J = {l: Lp.jacobians[l].to(torch.float32) for l in LAYERS}
        self.norm = C.model._final_norm; self.dtype = C.dtype

    def logits(self, h, lens, l):
        """h [n, d] -> restricted logits [n, 9137] (Stage 10 decoder: transport in float, bf16 norm + bf16 rows)."""
        torch = self.torch; h = h.float()
        if lens == 'jlens_public': h = h @ self.J[l].to(h.device).T
        y = self.norm(h.to(self.dtype).to(self.W.device))
        return (y @ self.W.T).float()

    def nlr(self, lg, gold_cols):
        g = lg.gather(1, gold_cols[:, None]); return -np.log10(((lg > g).sum(1) + 1).cpu().numpy().astype(float))


_LENS = {}
def compute(C, u):
    torch = C.torch
    if 'L' not in _LENS: _LENS['L'] = Lens(C)
    LZ = _LENS['L']; sm = smp(); papers = sm[sm.shard == u[1]].paper_id.tolist()
    rec_layers = LAYERS + [63]; nL = len(LAYERS)
    P = dict(pid=[], cond=[], ai=[], kind=[], gold=[], nlr=[])                   # prompt rows
    N = dict(row_id=[], cond=[], role=[], tix=[], nlr=[])                        # name rows
    RP = dict(pid=[], cond=[], res=[], npos=[])                                   # pooled prompt residuals
    RS = dict(pid=[], ai=[], cond=[], gold=[], res=[])                            # surname-first residuals
    Y = dict(colon_pid=[], colon=[], sf_pid=[], sf_ai=[], sf=[])
    tix_of = {}
    for pid in papers:
        ctxs = C.ctx[pid]
        golds = []
        for ai, rids, name in ctxs:
            golds.append((ai, 'first', name[0]))
            if (pid, ai) in C.sfirst: golds.append((ai, 'surname', C.sfirst[(pid, ai)]))
        gcols = torch.tensor([LZ.col[g[2]] for g in golds], device=LZ.W.device)
        for cond in A.CONDS:
            L = C.layout(pid, cond); G = group_positions(C, L)
            for ci_, (ai, rids, name) in enumerate(ctxs):
                T = L['ids'] + name[:-1]
                _, acts = A.final_logits(C, T, [len(T) - 1], record_layers=rec_layers)
                H = {l: acts[l][0] for l in rec_layers}
                if ci_ == 0:                                                     # prompt positions: once per (paper, cond)
                    allpos = sorted({p for g in GROUPS for p in G[g]}); idx = {p: i for i, p in enumerate(allpos)}
                    tab = np.full((len(golds), len(GROUPS), nL, len(LENSES)), np.nan, np.float32)
                    pooled = np.zeros((len(GROUPS), nL, H[8].shape[-1]), np.float16); npos = np.array([len(G[g]) for g in GROUPS])
                    for li, l in enumerate(LAYERS):
                        hp = H[l][allpos]
                        for gi, g in enumerate(GROUPS):
                            if G[g]: pooled[gi, li] = hp[[idx[p] for p in G[g]]].float().mean(0).cpu().numpy().astype(np.float16)
                        for ki, lens in enumerate(LENSES):
                            lg = LZ.logits(hp, lens, l)                          # [n_pos, 9137]
                            # nlr of every gold at every position
                            gl = lg[:, gcols]                                    # [n_pos, n_gold]
                            rk = (lg[:, :, None] > gl[:, None, :]).sum(1) + 1       # [n_pos, n_gold]
                            nl = -torch.log10(rk.float()).cpu().numpy()
                            for gi, g in enumerate(GROUPS):
                                if G[g]: tab[:, gi, li, ki] = nl[[idx[p] for p in G[g]]].mean(0)
                    for j, (ai_, kd, gt) in enumerate(golds):
                        P['pid'].append(pid); P['cond'].append(cond); P['ai'].append(ai_); P['kind'].append(kd); P['gold'].append(gt)
                    P['nlr'].append(tab); RP['pid'].append(pid); RP['cond'].append(cond); RP['res'].append(pooled); RP['npos'].append(npos)
                    if cond == 'true':
                        Y['colon_pid'].append(pid); Y['colon'].append(H[63][len(L['ids']) - 1].float().cpu().numpy().astype(np.float16))
                # name positions: rows predicting name[j] sit at len(ids) - 1 + j
                pos = [len(L['ids']) - 1 + j for j in range(len(name))]
                gc = torch.tensor([LZ.col[t] for t in name], device=LZ.W.device)
                tab = np.zeros((len(name), nL, len(LENSES)), np.float32)
                for li, l in enumerate(LAYERS):
                    for ki, lens in enumerate(LENSES): tab[:, li, ki] = LZ.nlr(LZ.logits(H[l][pos], lens, l), gc)
                N['row_id'] += rids; N['cond'] += [cond] * len(rids); N['role'] += [C.role[r] for r in rids]; N['tix'] += list(range(len(rids))); N['nlr'].append(tab)
                sfj = [j for j, r in enumerate(rids) if C.role[r] == 'surname_first']
                if sfj:
                    j = sfj[0]; RS['pid'].append(pid); RS['ai'].append(ai); RS['cond'].append(cond); RS['gold'].append(name[j])
                    RS['res'].append(np.stack([H[l][pos[j]].float().cpu().numpy() for l in LAYERS]).astype(np.float16))
                    if cond == 'true': Y['sf_pid'].append(pid); Y['sf_ai'].append(ai); Y['sf'].append(H[63][pos[j]].float().cpu().numpy().astype(np.float16))
    d = dict(layers=np.array(LAYERS), groups=np.array(GROUPS), lenses=np.array(LENSES),
             p_pid=np.array(P['pid']), p_cond=np.array(P['cond']), p_ai=np.array(P['ai']), p_kind=np.array(P['kind']), p_gold=np.array(P['gold']),
             p_nlr=np.concatenate(P['nlr']),
             n_row_id=np.array(N['row_id']), n_cond=np.array(N['cond']), n_role=np.array(N['role']), n_tix=np.array(N['tix']), n_nlr=np.concatenate(N['nlr']),
             rp_pid=np.array(RP['pid']), rp_cond=np.array(RP['cond']), rp_res=np.stack(RP['res']), rp_npos=np.stack(RP['npos']),
             rs_pid=np.array(RS['pid']), rs_ai=np.array(RS['ai']), rs_cond=np.array(RS['cond']), rs_gold=np.array(RS['gold']), rs_res=np.stack(RS['res']),
             y_colon_pid=np.array(Y['colon_pid']), y_colon=np.stack(Y['colon']), y_sf_pid=np.array(Y['sf_pid']), y_sf_ai=np.array(Y['sf_ai']), y_sf=np.stack(Y['sf']))
    chk = dict(n_papers=len(papers), empty_groups={g: int((d['rp_npos'][:, gi] == 0).sum()) for gi, g in enumerate(GROUPS)})
    return d, dict(check=chk)


def work(a, C=None):
    miss, C = A.work(all_units(a.shards), out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item1'); return miss


# ------------------------------------------------------------------ analysis (CPU)
def ridge_predict(Xtr_all, Ytr_all, folds_tr, evals, alphas=(0.1, 1.0, 10.0)):
    """Xtr_all [n, d] true-title rows with fold ids folds_tr; evals: list of (X [m, d], fold ids [m]); returns alpha, fold-0 mse,
    list of held-out predictions (each eval row predicted by the model trained without its fold)."""
    X = Xtr_all.astype(np.float64); Yt = Ytr_all.astype(np.float64); d = X.shape[1]; fl = np.unique(folds_tr)
    def fit(tr):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; Z = (X[tr] - mu) / sd; ym = Yt[tr].mean(0); Km = Z @ Z.T
        return mu, sd, Z, ym, Km, np.trace(Km) / d
    tr = folds_tr != fl[0]; te = ~tr; mu, sd, Z, ym, Km, tg = fit(tr); best, ba = None, None
    for a_ in alphas:
        Wd = np.linalg.solve(Km + a_ * tg * np.eye(len(Km)), Yt[tr] - ym)
        pr = ((X[te] - mu) / sd) @ Z.T @ Wd + ym; mse = float(((pr - Yt[te]) ** 2).mean())
        if best is None or mse < best: best, ba = mse, a_
    outs = [np.full((len(x), Yt.shape[1]), np.nan) for x, _ in evals]
    for f in fl:
        tr = folds_tr != f; mu, sd, Z, ym, Km, tg = fit(tr)
        Wd = np.linalg.solve(Km + ba * tg * np.eye(len(Km)), Yt[tr] - ym); B_ = Z.T @ Wd                   # [d, out]
        for o, (x, fe) in zip(outs, evals):
            m = fe == f
            if m.any(): o[m] = ((x[m].astype(np.float64) - mu) / sd) @ B_ + ym
    return ba, best, outs


def decode_nlr(pred, gold, Wr, nw, eps):
    """fp32 decoder of the probe (addendum 11): RMSNorm with the final-norm weight, restricted lm_head rows; rank among 9,137."""
    x = pred / np.sqrt((pred ** 2).mean(1, keepdims=True) + eps) * nw
    lg = x @ Wr.T; g = lg[np.arange(len(gold)), gold]
    return -np.log10((lg > g[:, None]).sum(1) + 1.0)


DECODER = {}
def decoder():
    """probe decoder: 9,137 name-token lm_head rows (fp16 -> fp32), final-norm weight, eps (tiny test: overridden by the tiny model)."""
    if 'd' not in DECODER:
        vr = np.load(A.R13 / 'summary_alltok/vocab_rows.npz')
        DECODER['d'] = (vr['lm_head_rows'].astype(np.float32), vr['norm_weight'].astype(np.float32), float(vr['eps']), {int(t): i for i, t in enumerate(vr['token_id'])})
    return DECODER['d']


def set_tiny_decoder(C):
    vr = np.load(A.R13 / 'summary_alltok/vocab_rows.npz'); ids = vr['token_id']
    W = C.model._lm_head.weight.detach().float().numpy()[ids]; nw = C.model._final_norm.weight.detach().float().numpy()
    DECODER['d'] = (W, nw, 1e-6, {int(t): i for i, t in enumerate(ids)})


def analyze(a=None):
    import pandas as pd
    A.check_addendum(); B = A.Boot(); SUM.mkdir(parents=True, exist_ok=True)
    fs = [out_path(u) for u in all_units()]; have = [f for f in fs if f.exists()]
    Z = [dict(np.load(f)) for f in have]
    cat = lambda k: np.concatenate([z[k] for z in Z])
    rows = []
    def cell(position, kind, readout, layer, pm, extra=None):
        """pm: DataFrame paper x cond of mean nlr."""
        pm = pm.dropna(); pids = pm.index.to_numpy(); spec = (pm['true'] - pm[A.FALSES].mean(1)).to_numpy()
        e, b = B.mean(pids, spec); t, tb, nb = B.tc(pids, spec); tt, ttb, _ = B.tc(pids, pm['true'].to_numpy())
        r = dict(position=position, kind=kind, readout=readout, layer=int(layer), n_papers=len(pids), true_mean=float(pm['true'].mean()),
                 spec=e, spec_lo=B.ci(b)[0], spec_hi=B.ci(b)[1], tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1], tc_bins=nb,
                 tc_true=tt, tc_true_lo=B.ci(ttb)[0], tc_true_hi=B.ci(ttb)[1])
        if extra: r.update(extra)
        rows.append(r)
    # ---- lens, prompt groups
    pp = pd.DataFrame(dict(pid=cat('p_pid'), cond=cat('p_cond'), kind=cat('p_kind'))); PN = cat('p_nlr')
    for kd in KINDS:
        m = (pp.kind == kd).to_numpy()
        for gi, g in enumerate(GROUPS):
            for li, l in enumerate(LAYERS):
                for ki, lens in enumerate(LENSES):
                    v = pd.Series(PN[m, gi, li, ki]); pm = v.groupby([pp.pid[m].to_numpy(), pp.cond[m].to_numpy()]).mean().unstack()
                    cell(g, kd, lens, l, pm[A.CONDS])
    # ---- lens, name positions
    nn = pd.DataFrame(dict(row=cat('n_row_id'), cond=cat('n_cond'), role=cat('n_role'), tix=cat('n_tix'))); NN = cat('n_nlr')
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'token_index']).set_index('row_id')
    nn['pid'] = tk.paper_id.reindex(nn.row).to_numpy(); nn['tix0'] = tk.token_index.reindex(nn.row).to_numpy()
    for nm, m in (('name_surname_first', (nn.role == 'surname_first').to_numpy()), ('name_all', (nn.tix0 >= 1).to_numpy())):
        for li, l in enumerate(LAYERS):
            for ki, lens in enumerate(LENSES):
                v = pd.Series(NN[m, li, ki]); pm = v.groupby([nn.pid[m].to_numpy(), nn.cond[m].to_numpy()]).mean().unstack()
                cell(nm, 'next_token', lens, l, pm[A.CONDS])
    # ---- parity with the H3 same-scale ranks (surname first, L32/40/48/52/56, WARN only)
    par = {}
    try:
        SS = A.R13 / 'summary_h3_samescale_20261114/ranks'
        for cond in ('true', 'false_0'):
            h3 = pd.read_parquet(SS / f'{cond}.parquet').set_index('row_id')
            m = ((nn.role == 'surname_first') & (nn.cond == cond)).to_numpy(); rid = nn.row[m].to_numpy()
            for li, l in enumerate(LAYERS):
                for ki, lens in enumerate(LENSES):
                    col = f'rr_{lens}_b16_L{l}'
                    if col not in h3.columns: continue
                    ref = -np.log10(h3[col].reindex(rid).to_numpy(float)); new = NN[m, li, ki]; ok = np.isfinite(ref)
                    par[f'{cond}_{lens}_L{l}'] = dict(rows=int(ok.sum()), exact_share=float((np.abs(new[ok] - ref[ok]) < 1e-9).mean()),
                                                     max_abs_dnlr=float(np.abs(new[ok] - ref[ok]).max()))
    except Exception as ex: par['error'] = repr(ex)
    # ---- probes (CPU): name-token ridge probe on the same 9,137 scale
    Wr, nw, eps, col = decoder()
    c13 = A.load_mod(A.H / '13_stage13/stage13_cpu.py', 'c13_i1'); allp = B.meta.index.to_numpy(); fo, _ = c13.group_folds(allp); FOLD = pd.Series(np.asarray(fo), index=allp)
    rp_pid, rp_cond, RPres = cat('rp_pid'), cat('rp_cond'), cat('rp_res'); rp_n = cat('rp_npos')
    ycp = cat('y_colon_pid'); YC = cat('y_colon').astype(np.float32); ycol = dict(zip(ycp, range(len(ycp))))
    golds_by_paper = {}
    for p_, kd, gt in zip(cat('p_pid')[cat('p_cond') == 'true'], cat('p_kind')[cat('p_cond') == 'true'], cat('p_gold')[cat('p_cond') == 'true']):
        golds_by_paper.setdefault((p_, kd), []).append(col[int(gt)])
    probe_info = {}
    for gi, g in enumerate(GROUPS):
        for li, l in enumerate(LAYERS):
            have_g = rp_n[:, gi] > 0
            tr = have_g & (rp_cond == 'true'); trp = rp_pid[tr]
            Xtr = RPres[tr, gi, li].astype(np.float32); Ytr = YC[[ycol[p] for p in trp]]
            evals = [(RPres[have_g & (rp_cond == c), gi, li].astype(np.float32), FOLD.reindex(rp_pid[have_g & (rp_cond == c)]).to_numpy()) for c in A.CONDS]
            alpha, mse, preds = ridge_predict(Xtr, Ytr, FOLD.reindex(trp).to_numpy(), evals)
            probe_info[f'{g}_L{l}'] = dict(alpha=alpha, fold0_mse=mse, n_train=int(tr.sum()))
            for kd in KINDS:
                pm = {}
                for c, pr in zip(A.CONDS, preds):
                    pc = rp_pid[have_g & (rp_cond == c)]; vals = []
                    for p_, y_ in zip(pc, pr):
                        gl = golds_by_paper.get((p_, kd), [])
                        vals.append(decode_nlr(np.repeat(y_[None], len(gl), 0), np.array(gl), Wr, nw, eps).mean() if gl else np.nan)
                    pm[c] = pd.Series(vals, index=pc)
                cell(g, kd, 'probe', l, pd.DataFrame(pm)[A.CONDS])
    # surname-first name position probe (target = true L63 at the same position)
    rs_pid, rs_ai, rs_cond, rs_gold, RS = cat('rs_pid'), cat('rs_ai'), cat('rs_cond'), cat('rs_gold'), cat('rs_res')
    ysk = list(zip(cat('y_sf_pid'), cat('y_sf_ai'))); YS = cat('y_sf').astype(np.float32); ysi = {k: i for i, k in enumerate(ysk)}
    for li, l in enumerate(LAYERS):
        tr = rs_cond == 'true'; keys = list(zip(rs_pid[tr], rs_ai[tr]))
        evals = [(RS[rs_cond == c, li].astype(np.float32), FOLD.reindex(rs_pid[rs_cond == c]).to_numpy()) for c in A.CONDS]
        alpha, mse, preds = ridge_predict(RS[tr, li].astype(np.float32), YS[[ysi[k] for k in keys]], FOLD.reindex(rs_pid[tr]).to_numpy(), evals)
        probe_info[f'name_sf_L{l}'] = dict(alpha=alpha, fold0_mse=mse, n_train=int(tr.sum()))
        pm = {}
        for c, pr in zip(A.CONDS, preds):
            m = rs_cond == c; gl = np.array([col[int(x)] for x in rs_gold[m]])
            pm[c] = pd.Series(decode_nlr(pr, gl, Wr, nw, eps)).groupby(rs_pid[m]).mean()
        cell('name_surname_first', 'next_token', 'probe', l, pd.DataFrame(pm)[A.CONDS])
    # ---- attribute probes (year, log citations, field) on the pooled prompt-group residuals: held-out score per paper
    Pm = pd.read_parquet(A.R10 / 'cohort/papers.parquet', columns=['paper_id', 'year', 'citations', 'field']).set_index('paper_id')
    attr_rows = []
    for gi, g in enumerate(GROUPS):
        for li, l in enumerate(LAYERS):
            have_g = rp_n[:, gi] > 0; tr = have_g & (rp_cond == 'true'); trp = rp_pid[tr]
            fields = sorted(Pm.field.dropna().unique()); yy = {
                'year': Pm.year.reindex(trp).astype(float).to_numpy()[:, None],
                'log_citations': np.log10(1 + Pm.citations.reindex(trp).astype(float).to_numpy())[:, None],
                'field': (Pm.field.reindex(trp).to_numpy()[:, None] == np.array(fields)[None]).astype(float)}
            evals = [(RPres[have_g & (rp_cond == c), gi, li].astype(np.float32), FOLD.reindex(rp_pid[have_g & (rp_cond == c)]).to_numpy()) for c in A.CONDS]
            for att, Yv in yy.items():
                _, _, preds = ridge_predict(RPres[tr, gi, li].astype(np.float32), Yv, FOLD.reindex(trp).to_numpy(), evals)
                pm = {}
                for c, pr in zip(A.CONDS, preds):
                    pc = rp_pid[have_g & (rp_cond == c)]
                    if att == 'field': s = (np.array(fields)[pr.argmax(1)] == Pm.field.reindex(pc).to_numpy()).astype(float)   # accuracy
                    elif att == 'year': s = -np.abs(pr[:, 0] - Pm.year.reindex(pc).astype(float).to_numpy())                    # -|error| years
                    else: s = -np.abs(pr[:, 0] - np.log10(1 + Pm.citations.reindex(pc).astype(float).to_numpy()))
                    pm[c] = pd.Series(s, index=pc)
                pm = pd.DataFrame(pm)[A.CONDS].dropna(); pids = pm.index.to_numpy(); spec = (pm['true'] - pm[A.FALSES].mean(1)).to_numpy()
                e, b = B.mean(pids, spec); t, tb, _ = B.tc(pids, spec)
                attr_rows.append(dict(position=g, layer=l, attribute=att, score_true=float(pm['true'].mean()), score_false=float(pm[A.FALSES].mean(1).mean()),
                                      spec=e, spec_lo=B.ci(b)[0], spec_hi=B.ci(b)[1], tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1]))
    T = pd.DataFrame(rows); T.to_csv(SUM / 'item1_map.csv', index=False); AT = pd.DataFrame(attr_rows); AT.to_csv(SUM / 'item1_attribute_probes.csv', index=False)
    # ---- main comparison (locked rule), per readout; primary kind = surname for prompt groups
    crit = []
    for ro in ('logit', 'jlens_public', 'probe'):
        nmc = T[(T.position == 'name_surname_first') & (T.readout == ro)].set_index('layer')
        for kd in KINDS:
            for g in GROUPS:
                x = T[(T.position == g) & (T.kind == kd) & (T.readout == ro)].sort_values('layer')
                pos_layers = x[x.tc_lo > 0].layer.tolist(); earliest = pos_layers[0] if pos_layers else None
                hits = [l for l in pos_layers if l <= 48 and l in nmc.index and nmc.loc[l, 'tc_lo'] <= 0 <= nmc.loc[l, 'tc_hi']]
                crit.append(dict(readout=ro, kind=kd, primary=kd == 'surname', position=g, earliest_tc_ci_gt0=earliest, layers_meeting_rule=';'.join(map(str, hits)),
                                 verdict=f'shelf first at {g} (L{hits[0]})' if hits else 'no earlier position'))
        x = nmc.sort_index(); pl = x[x.tc_lo > 0].index.tolist()
        crit.append(dict(readout=ro, kind='next_token', primary=True, position='name_surname_first', earliest_tc_ci_gt0=pl[0] if pl else None, layers_meeting_rule='', verdict='(reference)'))
    CR = pd.DataFrame(crit); CR.to_csv(SUM / 'item1_criterion.csv', index=False)
    json.dump(dict(parity_h3=par, probe=probe_info), open(SUM / 'item1_checks.json', 'w'), indent=1, default=str)
    report(T, AT, CR, par, probe_info, len(have), len(set(cat('p_pid'))))
    return T


def report(T, AT, CR, par, probe_info, nshards, npapers):
    f3 = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if (lo > 0 or hi < 0) else '')
    L = ['# Addendum 18b item 1 — readout map (position group × layer)', '',
         f'**Pre-registered (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…); the main-comparison rule is fixed by the lock.** '
         f'600-paper subsample of the Stage 11 sample (seed {A.SEED}); {nshards}/24 shards, {npapers} papers. Readouts: logit lens and public J-lens '
         '(gold ranked only among the 9,137 name token ids, Stage 10 bf16 decoder) and the name-token ridge probe on the same scale (fp32 decoder; '
         'trained on 600 papers here, so weaker than the 9,108-paper probes of addendum 11). spec = true − mean of 5 false titles; T − C = within-citation-bin '
         'target − control of spec; author-team cluster bootstrap 2,000 draws. * = CI excludes 0. Primary gold for prompt positions = surname first token '
         '(chosen at implementation, before any GPU output; "first" token reported beside it).', '',
         '## Main comparison (locked rule: group with T − C CI > 0 at some layer ≤ L48 while the surname-first name position at that layer has CI ∋ 0)', '',
         '| readout | gold kind | position group | earliest layer T − C CI > 0 | layers meeting the rule | verdict |', '|---|---|---|---|---|---|']
    for r in CR.itertuples():
        el = '' if r.earliest_tc_ci_gt0 is None or (isinstance(r.earliest_tc_ci_gt0, float) and np.isnan(r.earliest_tc_ci_gt0)) else f'L{int(r.earliest_tc_ci_gt0)}'
        L.append(f'| {r.readout} | {r.kind}{" (primary)" if r.primary and r.kind == "surname" else ""} | {r.position} | {el} | {r.layers_meeting_rule} | {r.verdict} |')
    for ro in ('logit', 'jlens_public', 'probe'):
        L += ['', f'## {ro}: T − C of spec (rows: position group / gold kind; columns: layer)', '']
        sub = T[T.readout == ro]; hdr = '| position | kind | ' + ' | '.join(f'L{l}' for l in LAYERS) + ' |'
        L += [hdr, '|' + '---|' * (len(LAYERS) + 2)]
        for (p, k), x in sub.groupby(['position', 'kind'], sort=False):
            x = x.set_index('layer')
            L.append(f'| {p} | {k} | ' + ' | '.join((f'{x.loc[l, "tc"]:+.3f}' + ('*' if (x.loc[l, "tc_lo"] > 0 or x.loc[l, "tc_hi"] < 0) else '')) if l in x.index else '' for l in LAYERS) + ' |')
        L += ['', f'{ro}: spec (title-specific signal, target + control papers)', '', hdr, '|' + '---|' * (len(LAYERS) + 2)]
        for (p, k), x in sub.groupby(['position', 'kind'], sort=False):
            x = x.set_index('layer')
            L.append(f'| {p} | {k} | ' + ' | '.join((f'{x.loc[l, "spec"]:+.3f}' + ('*' if (x.loc[l, "spec_lo"] > 0 or x.loc[l, "spec_hi"] < 0) else '')) if l in x.index else '' for l in LAYERS) + ' |')
    L += ['', '## Attribute probes (held-out; spec = true − mean false of the per-paper score; year/citations: −|error|, field: accuracy)', '',
          '| position | attribute | ' + ' | '.join(f'L{l}' for l in LAYERS) + ' |', '|' + '---|' * (len(LAYERS) + 2)]
    for (p, at), x in AT.groupby(['position', 'attribute'], sort=False):
        x = x.set_index('layer')
        L.append(f'| {p} | {at} | ' + ' | '.join((f'{x.loc[l, "spec"]:+.3f}' + ('*' if (x.loc[l, "spec_lo"] > 0 or x.loc[l, "spec_hi"] < 0) else '')) for l in LAYERS) + ' |')
    ex = [v['exact_share'] for k, v in par.items() if isinstance(v, dict) and 'exact_share' in v]
    L += ['', '## Checks (WARN only)', '',
          f'- lens parity vs the stored H3 same-scale ranks (surname first, true / false_0, overlapping layers): exact-nlr share min {min(ex) if ex else float("nan"):.3f}, '
          f'max {max(ex) if ex else float("nan"):.3f} over {len(ex)} cells (threshold 0.95; batch / kernel differences give ±1 bf16 unit ties). '
          + ('WARN' if ex and min(ex) < 0.95 else 'OK'),
          f'- probe alphas chosen: ' + ', '.join(f'{k}:{v["alpha"]}' for k, v in list(probe_info.items())[:6]) + ' … (all in item1_checks.json)', '',
          'Full table: item1_map.csv (all cells, spec / T − C / true-only T − C with CIs); item1_criterion.csv; item1_attribute_probes.csv.']
    (SUM / 'item1_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L[:60]))


# ------------------------------------------------------------------ tiny
def tiny(a):
    global RAW, SUM
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; ok = {}
    C = A.make_ctx(tiny=True); sm = A.sample(); set_tiny_decoder(C)
    _SMP['m'] = pd.concat([sm[sm.shard == k].head(3) for k in range(24)])
    ns = argparse.Namespace(shards='all', max_minutes=600)
    miss = work(ns, C=C); ok['all units written'] = not miss
    z = np.load(out_path(('main', 0)))
    ok['prompt table shape'] = z['p_nlr'].shape[1:] == (len(GROUPS), len(LAYERS), len(LENSES))
    ok['colon / authors / close present in every prompt'] = bool((z['rp_npos'][:, [GROUPS.index(g) for g in ('colon', 'authors', 'close')]] == 1).all())
    ok['year has 4 digits mostly'] = bool((z['rp_npos'][:, GROUPS.index('year')] == 4).mean() > 0.9)
    # restricted nlr <= 0 and finite
    ok['nlr finite (present groups)'] = bool(np.isfinite(z['n_nlr']).all() and (z['n_nlr'] <= 0).all())
    # consistency: the colon row of kind 'first' at logit = the name-position row for token_index 0 (same position, same gold)
    try:
        pp = pd.DataFrame(dict(pid=z['p_pid'], cond=z['p_cond'], ai=z['p_ai'], kind=z['p_kind'])); m = ((pp.kind == 'first') & (pp.cond == 'true')).to_numpy()
        first_rows = z['n_tix'] == 0; nm = z['n_nlr'][first_rows & (z['n_cond'] == 'true'), :, 0]
        pc = z['p_nlr'][m, GROUPS.index('colon'), :, 0]
        ok['colon/first = name row 0 (two code paths)'] = bool(np.allclose(np.sort(pc.ravel()), np.sort(nm.ravel()), atol=1e-6))
    except Exception as ex: print('consistency check error', ex); ok['colon/first = name row 0 (two code paths)'] = False
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item1_report.md').exists()
    except Exception as ex: import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM1 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM1 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
