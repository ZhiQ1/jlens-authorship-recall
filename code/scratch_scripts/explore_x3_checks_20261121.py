#!/usr/bin/env python3
"""Exploratory (post hoc, not pre-registered), user request 2026-11-21. X3 checks, CPU only, existing data + offline text models.
A. Per-layer paired comparison Qwen vs text-only models on the scale-free ratio r(l) = (G'(l) - G'(base)) / G'(base),
   G' = cos(orig, para) - cos(orig, lexical neighbour D); Qwen base L4 (title_last); text models: best layer fixed at the
   point estimate (as reports/x3_textbase_recovery.md). Paired difference r_Q(l) - r_text(best) on the same team draws
   (stage13_x3_analyze.team_w / SEED). Text share = r_text(best) / r_Q(best).
B. Behaviour-free familiarity proxy: citations (and year) within the X3 primary sample: halves at the median, tertiles;
   per group Qwen G'(l) - G'(L4) at L24-L48 and the behaviour recovery (para - D) / (true - D); high - low with team CI;
   plus target - control within citation bins (weights n_t n_c / (n_t + n_c)).
Reuses stage13_x3_textbase.py (encode_hf, cos_array) and stage13_x3_analyze.py (team_w, SEED, ci) read-only.
Output: 381_stage13/summary_explore_x3_checks_20261121/ (report.md + CSVs). Usage: [--limit N] [--out DIR]
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


TB = load(H / '13_stage13/stage13_x3_textbase.py', 'x3tb_ro'); X3 = TB.X3
VERS = ['paraphrase', 'partner', 'lexical_neighbour']
fm = lambda e, lo, hi, d=3: f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int); ap.add_argument('--out'); a = ap.parse_args()
    out = Path(a.out or ROOT / 'summary_explore_x3_checks_20261121'); out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / 'summary_x3/x3_pairs.csv')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): df[c] = df[c].astype(bool)
    P = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id')
    paras = {}
    for f in sorted((ROOT / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); paras |= dict(zip(z['paper_id'], z['paraphrase']))
    q = pd.read_csv(ROOT / 'summary_x3/x3_cos_per_paper.csv.gz')
    q = q[q.pos == 'title_last'].pivot_table(index='paper_id', columns=['version', 'layer'], values='cos_with_original')
    QL = sorted({l for _, l in q.columns})
    CQ = np.stack([q.loc[df.paper_id, [(v, l) for l in QL]].to_numpy() for v in VERS], 1).astype(np.float64)
    if a.limit: df = df.iloc[:a.limit].copy(); CQ = CQ[:a.limit]
    df['cit'] = P.loc[df.paper_id, 'citations'].to_numpy().astype(float); df['year'] = P.loc[df.paper_id, 'year'].to_numpy().astype(float)
    df['citation_bin'] = P.loc[df.paper_id, 'citation_bin'].to_numpy()
    # ---- text models (as stage13_x3_textbase.py)
    texts, tix = [], {}
    def add(t):
        t = str(t)
        if t not in tix: tix[t] = len(texts); texts.append(t)
        return tix[t]
    idx = np.array([[add(P.loc[r.paper_id].title), add(paras[r.paper_id]), add(P.loc[r.partner].title),
                     add(P.loc[r.lexical_neighbour_j2].title)] for r in df.itertuples()])
    REPS = {}
    for name, kind, poss in (('bert-base-uncased', 'bert', ['title_last', 'mean_title']), ('sentence-transformers/all-mpnet-base-v2', 'mpnet', ['mean', 'title_last'])):
        E = TB.encode_hf(name, texts, kind)
        for p in poss: REPS[name.split('/')[-1], p] = (list(range(13)), TB.cos_array(E[p], idx))
    print('encoded', len(texts), 'texts', flush=True)
    # ---- A. per-layer paired comparison
    rowsA = []
    subsets = [('primary', 'all', 'all'), ('primary', 'all', 'test'), ('primary', 'd_matched', 'all'), ('primary', 'd_matched', 'test')]
    for setn, sub, part in subsets:
        m = df.include_primary.to_numpy() & df.team.notna().to_numpy()
        if sub == 'd_matched': m &= df.d_matched.to_numpy()
        if part != 'all': m &= (df.split == part).to_numpy()
        s = df[m]
        if len(s) < 5: continue
        W = X3.team_w(s.team.to_numpy(), X3.SEED[part, sub])
        def gap_boot(C, layers):
            V = C[m][:, 0] - C[m][:, 2]; return V.mean(0), (W @ V) / W.sum(1, keepdims=True)
        gq, bq = gap_boot(CQ, QL); i4 = QL.index(4)
        rq = (gq - gq[i4]) / gq[i4]; brq = (bq - bq[:, [i4]]) / bq[:, [i4]]
        jq = int(np.argmax(rq[i4 + 1:])) + i4 + 1
        for (model, pos), (layers, C) in REPS.items():
            g, b = gap_boot(C, layers); i0 = 0
            if abs(g[i0]) < 1e-4: continue
            r = (g - g[i0]) / g[i0]; br = (b - b[:, [i0]]) / b[:, [i0]]
            j = int(np.argmax(r[1:])) + 1
            share = r[j] / rq[jq]; bshare = br[:, j] / brq[:, jq]
            for li, l in enumerate(QL):
                if l <= 4: continue
                d = brq[:, li] - br[:, j]; lo, hi = X3.ci(d)
                rowsA.append(dict(set=setn, subset=sub, split=part, n=len(s), text_model=model, text_pos=pos, text_best_layer=layers[j],
                                  r_text_best=r[j], qwen_layer=l, r_qwen=rq[li], r_qwen_lo=X3.ci(brq[:, li])[0], r_qwen_hi=X3.ci(brq[:, li])[1],
                                  diff=rq[li] - r[j], diff_lo=lo, diff_hi=hi, qwen_best_layer=QL[jq], r_qwen_best=rq[jq],
                                  text_share_of_qwen=share, share_lo=X3.ci(bshare)[0], share_hi=X3.ci(bshare)[1]))
    A = pd.DataFrame(rowsA); A.to_csv(out / 'A_qwen_vs_text_per_layer.csv', index=False)
    # ---- B. familiarity proxy regrouping (primary / all / all)
    m = df.include_primary.to_numpy() & df.team.notna().to_numpy(); s = df[m].reset_index(drop=True); Cs = CQ[m]
    V = Cs[:, 0] - Cs[:, 2]; i4 = QL.index(4); Lsel = [l for l in (24, 28, 32, 36, 40, 44, 48) if l in QL]
    O, Pp, F = s.score_original.to_numpy(), s.score_paraphrase.to_numpy(), s.score_lexical.to_numpy()
    W = X3.team_w(s.team.to_numpy(), 913)
    def stats(mask):
        w = W[:, mask]; ws = w.sum(1)
        out_ = {}
        for l in Lsel:
            x = V[mask, QL.index(l)] - V[mask, i4]; out_[f'gL{l}'] = (x.mean(), (w @ x) / ws)
        rec = (Pp[mask].mean() - F[mask].mean()) / (O[mask].mean() - F[mask].mean())
        brec = ((w @ Pp[mask]) - (w @ F[mask])) / ((w @ O[mask]) - (w @ F[mask]))
        out_['recovery'] = (rec, brec); return out_
    med = np.median(s.cit); ter = np.quantile(s.cit, [1 / 3, 2 / 3]); ymed = np.median(s.year)
    groupings = {'citations: low / high half (median %.0f)' % med: (s.cit <= med, s.cit > med),
                 'citations: bottom / top tertile (%.0f, %.0f)' % tuple(ter): (s.cit <= ter[0], s.cit > ter[1]),
                 'year: older / newer half (median %.0f)' % ymed: (s.year <= ymed, s.year > ymed),
                 'recognition: control / target (as published)': ((s.group == 'control').to_numpy(), (s.group == 'target').to_numpy())}
    rowsB = []
    for gname, (lo_m, hi_m) in groupings.items():
        lo_m, hi_m = np.asarray(lo_m), np.asarray(hi_m); a_, b_ = stats(lo_m), stats(hi_m)
        for k in a_:
            d = b_[k][1] - a_[k][1]; lo, hi = X3.ci(d)
            rowsB.append(dict(grouping=gname, measure=k, n_low=int(lo_m.sum()), n_high=int(hi_m.sum()), low=a_[k][0], low_lo=X3.ci(a_[k][1])[0], low_hi=X3.ci(a_[k][1])[1],
                              high=b_[k][0], high_lo=X3.ci(b_[k][1])[0], high_hi=X3.ci(b_[k][1])[1], high_minus_low=b_[k][0] - a_[k][0], d_lo=lo, d_hi=hi))
    # target - control within citation bins
    for k_l in Lsel + ['recovery']:
        num, bnum, wt = 0.0, 0.0, 0.0
        for cb, g in s.groupby('citation_bin'):
            it, ic = (g.group == 'target').to_numpy(), (g.group == 'control').to_numpy()
            if it.sum() < 5 or ic.sum() < 5: continue
            ix = g.index.to_numpy(); mt = np.zeros(len(s), bool); mc = mt.copy(); mt[ix[it]] = True; mc[ix[ic]] = True
            at, ac = stats(mt), stats(mc); key = 'recovery' if k_l == 'recovery' else f'gL{k_l}'
            wgt = it.sum() * ic.sum() / (it.sum() + ic.sum())
            num += wgt * (at[key][0] - ac[key][0]); bnum = bnum + wgt * (at[key][1] - ac[key][1]); wt += wgt
        if wt == 0:  # tiny subsets: no bin with >= 5 papers per group
            rowsB.append(dict(grouping='target - control within citation bins', measure='recovery' if k_l == 'recovery' else f'gL{k_l}',
                              high_minus_low=np.nan, d_lo=np.nan, d_hi=np.nan)); continue
        lo, hi = X3.ci(bnum / wt)
        rowsB.append(dict(grouping='target - control within citation bins', measure='recovery' if k_l == 'recovery' else f'gL{k_l}',
                          high_minus_low=num / wt, d_lo=lo, d_hi=hi))
    Bt = pd.DataFrame(rowsB); Bt.to_csv(out / 'B_familiarity_regroup.csv', index=False)
    # ---- report
    Lr = ['# X3 checks — exploratory (post hoc, not pre-registered), 2026-11-21', '',
          f'n (primary, all) = {len(s)}; teams from x3_pairs; 2,000 team draws (X3 seeds for A; seed 913 for B). Text models encoded offline: bert-base-uncased, all-mpnet-base-v2.', '',
          '## A. Qwen r(l) − text-model best ratio (paired)', '',
          '| subset | text model · pos (best layer) | r_text | text share of Qwen best (r_text / r_Qwen at L%s) | Qwen layers where r_Qwen(l) − r_text > 0 (CI) |' % '?', '|---|---|---|---|---|']
    for (st, sb, pt, tm, tp), g in A.groupby(['set', 'subset', 'split', 'text_model', 'text_pos'], sort=False):
        sig = [f'L{r.qwen_layer} {r.diff:+.2f} [{r.diff_lo:+.2f}, {r.diff_hi:+.2f}]' for r in g.itertuples() if r.diff_lo > 0]
        r0 = g.iloc[0]
        Lr.append(f'| {st}/{sb}/{pt} (n {r0.n}) | {tm} · {tp} (L{r0.text_best_layer}) | {r0.r_text_best:+.2f} | {fm(r0.text_share_of_qwen, r0.share_lo, r0.share_hi, 2)} (Qwen best L{r0.qwen_best_layer}, {r0.r_qwen_best:+.2f}) | {"; ".join(sig) or "none"} |')
    Lr += ['', '## B. Regrouping by behaviour-free proxies (primary / all)', '', '| grouping | measure | n low / high | low | high | high − low |', '|---|---|---|---|---|---|']
    for r in Bt.itertuples():
        if r.grouping.startswith('target - control'):
            Lr.append(f'| {r.grouping} | {r.measure} | | | | {fm(r.high_minus_low, r.d_lo, r.d_hi)} |')
        else:
            Lr.append(f'| {r.grouping} | {r.measure} | {r.n_low} / {r.n_high} | {fm(r.low, r.low_lo, r.low_hi)} | {fm(r.high, r.high_lo, r.high_hi)} | {fm(r.high_minus_low, r.d_lo, r.d_hi)} |')
    (out / 'report.md').write_text('\n'.join(Lr) + '\n'); print('\n'.join(Lr)); print('DONE', out)


if __name__ == '__main__':
    main()
