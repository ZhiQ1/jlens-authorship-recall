"""Stage 12 GPU-unit analysis: P1 single-position patching, P2 attention vs MLP, N1 MC-option priors, N2 pure prior,
F2 author-prompt lens readout. Writes summary/*.csv and reports/stage12_report.md under the Stage 12 root."""
import json
from pathlib import Path
import numpy as np, pandas as pd

B = 2000; rng = np.random.default_rng(3713)
def nlr(r): return -np.log10(np.asarray(r, float))
def fmt(v, lo, hi): return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def boot_ratio(num, den):
    num, den = np.asarray(num, float), np.asarray(den, float); ix = rng.integers(0, len(num), (B, len(num)))
    r = num[ix].mean(1) / den[ix].mean(1); return num.mean() / den.mean(), *np.percentile(r, [2.5, 97.5])


def boot(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]; mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1); return v.mean(), *np.percentile(mm, [2.5, 97.5])


def strat(df, col, g='group'):
    cells = []
    for b, x in df.groupby('citation_bin'):
        A = x[x[g] == 'target'][col].dropna().to_numpy(); C = x[x[g] == 'control'][col].dropna().to_numpy()
        if len(A) >= 30 and len(C) >= 30: cells.append((A, C))
    if not cells: return (np.nan,) * 3
    w = np.array([len(A) * len(C) / (len(A) + len(C)) for A, C in cells]); w /= w.sum()
    est = sum(wi * (A.mean() - C.mean()) for wi, (A, C) in zip(w, cells))
    bt = sum(wi * (A[rng.integers(0, len(A), (B, len(A)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A, C) in zip(w, cells))
    return est, *np.percentile(bt, [2.5, 97.5])


def load_dir(d):
    zs = [np.load(f, allow_pickle=True) for f in sorted(Path(d).glob('shard_*.npz'))]
    keep = [k for k in zs[0].files if k not in ('meta',)]
    return {k: (np.concatenate([z[k] for z in zs]) if zs[0][k].ndim and k not in ('layers', 'items', 'comps') else zs[0][k]) for k in keep}


def main(ROOT, R10, s10, s11):
    S = ROOT / 'summary'; S.mkdir(exist_ok=True); (ROOT / 'reports').mkdir(exist_ok=True)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'mc_team_a', 'recall_level'])
    L = ['# Stage 12 - single positions, attention vs MLP, name priors, author-prompt lens', '']
    # ---------- P1
    d = load_dir(ROOT / 'raw/patch_pos'); items = list(d['items']); layers = list(d['layers'])
    pid = toks.set_index('row_id').loc[d['row_id']].paper_id.to_numpy(); nt = nlr(d['rank_true']); P = nlr(d['rank_patch'])   # [n, L, I]
    none = P[:, :, items.index('none')]
    rows = []
    for li, l in enumerate(layers):
        for ii, it in enumerate(items):
            if it == 'none': continue
            df = pd.DataFrame({'paper_id': pid, 'num': P[:, li, ii] - none[:, li], 'den': nt - none[:, li]}).groupby('paper_id').mean().join(smp.set_index('paper_id'))
            for g in ['all', 'target', 'control']:
                s = df if g == 'all' else df[df.group == g]; r = boot_ratio(s.num, s.den)
                rows.append(dict(layer=l, item=it, group=g, recovery=r[0], lo=r[1], hi=r[2]))
    P1 = pd.DataFrame(rows); P1.to_csv(S / 'P1_patch_pos.csv', index=False)
    tt = pd.Series(d['tail_tokens']).value_counts().head(3)
    L += ['## P1. Which post-title token carries the paper? (patch one position, true -> false_0; all papers)', '',
          'Items: p1 = ":" (last prompt token), p2 = "Authors", p3 = ")?\\n", ... counting back from the end of the prompt; names = all name positions; all = everything (Stage 11 E1).',
          f'Most common prompt tails: {"; ".join(tt.index[:2])}', '', '| item | ' + ' | '.join(f'L{l}' for l in layers) + ' |', '|---|' + '---|' * len(layers)]
    for it in items:
        if it == 'none': continue
        L.append(f'| {it} | ' + ' | '.join(fmt(*P1[(P1.item == it) & (P1.layer == l) & (P1.group == "all")][['recovery', 'lo', 'hi']].iloc[0]) for l in layers) + ' |')
    # ---------- P2
    d = load_dir(ROOT / 'raw/patch_comp'); comps = list(d['comps']); pid = toks.set_index('row_id').loc[d['row_id']].paper_id.to_numpy()
    nt = nlr(d['rank_true']); Pc = nlr(d['rank_patch']); none = Pc[:, comps.index('none')]
    rows = []
    for ci, c in enumerate(comps):
        if c == 'none': continue
        df = pd.DataFrame({'paper_id': pid, 'num': Pc[:, ci] - none, 'den': nt - none}).groupby('paper_id').mean().join(smp.set_index('paper_id'))
        for g in ['all', 'target', 'control']:
            s = df if g == 'all' else df[df.group == g]; r = boot_ratio(s.num, s.den)
            rows.append(dict(comp=c.rstrip('0123456789'), layer=int(c.lstrip('atnmlp')), group=g, recovery=r[0], lo=r[1], hi=r[2]))
    P2 = pd.DataFrame(rows); P2.to_csv(S / 'P2_patch_comp.csv', index=False)
    L += ['', '## P2. Attention vs MLP: patch one component output of one layer on the whole post-title tail (all papers)', '',
          '| layer | attention | MLP |', '|---|---|---|']
    for l in sorted(P2.layer.unique()):
        a = P2[(P2.comp == 'attn') & (P2.layer == l) & (P2.group == 'all')].iloc[0]; m = P2[(P2.comp == 'mlp') & (P2.layer == l) & (P2.group == 'all')].iloc[0]
        L.append(f'| L{l} | {fmt(a.recovery, a.lo, a.hi)} | {fmt(m.recovery, m.lo, m.hi)} |')
    # ---------- N1
    mc = {c: pd.DataFrame({k: v for k, v in load_dir(ROOT / 'raw/prior_mc' / c).items() if k in ('paper_id', 'option', 'mean_nlr', 'first_token_nlr')}) for c in ('delete', 'true')}
    rows = []
    for c, x in mc.items():
        w = x.pivot_table(index='paper_id', columns='option', values='mean_nlr')
        w = w.dropna(); best = (w[0] >= w[[1, 2, 3]].max(1)).astype(float); margin = w[0] - w[[1, 2, 3]].mean(1)
        z = pd.DataFrame({'best': best, 'margin': margin}).join(papers.set_index('paper_id'))
        z = z[z.recall_level.isin(['R0', 'R1'])]
        for g in ['all', 'target', 'control']:
            s = z if g == 'all' else z[z.group_tight == g]; m = boot(s.margin); b = boot(s.best)
            rows.append(dict(prompt=c, group=g, n=len(s), margin=m[0], margin_lo=m[1], margin_hi=m[2], true_list_most_plausible=b[0], best_lo=b[1], best_hi=b[2]))
        e = strat(z.rename(columns={'group_tight': 'group'}), 'margin'); rows.append(dict(prompt=c, group='target-control', margin=e[0], margin_lo=e[1], margin_hi=e[2]))
        z['a'] = pd.to_numeric(z.mc_team_a, errors='coerce'); z['margin_c'] = z.margin - z.groupby('citation_bin').margin.transform('mean')
        from scipy.stats import spearmanr
        rows.append(dict(prompt=c, group='spearman_with_mc_right', margin=spearmanr(z.a, z.margin_c, nan_policy='omit').statistic))
    N1 = pd.DataFrame(rows); N1.to_csv(S / 'N1_prior_mc.csv', index=False)
    L += ['', '## N1. Is the TRUE author list simply the most plausible-sounding of the 4 multiple-choice options? (R0/R1 papers)', '',
          'margin = mean log10(1/rank) of the true list - mean of the 3 distractor lists; "most plausible" = share of papers where the true list scores highest.', '',
          '| prompt | group | margin | true list most plausible | ', '|---|---|---|---|']
    for _, r in N1.iterrows():
        if r.group in ('all', 'target', 'control'): L.append(f'| {r.prompt} | {r.group} | {fmt(r.margin, r.margin_lo, r.margin_hi)} | {r.true_list_most_plausible:.3f} [{r.best_lo:.3f}, {r.best_hi:.3f}] |')
        elif r.group == 'target-control': L.append(f'| {r.prompt} | target - control (within bin) | {fmt(r.margin, r.margin_lo, r.margin_hi)} | |')
        else: L.append(f'| {r.prompt} | Spearman(margin, orders right), within bin | {r.margin:+.3f} | |')
    L.append('\nChance level for "most plausible" is 0.25.')
    # ---------- N2
    z = load_dir(ROOT / 'raw/prior_pure'); rid = z['row_id']
    pure = pd.DataFrame({'row_id': rid, 'pure': nlr(z['final@63'])}).merge(toks, on='row_id')
    ref = {}
    for c in ('true', 'delete'):
        zs = [np.load(s10.out_file(R10, 'final', 63, k, c)) for k in range(72)]
        ref[c] = pd.Series(nlr(np.concatenate([q['rank'] for q in zs])), index=np.concatenate([q['row_id'] for q in zs]))
    pure['delete'] = ref['delete'].loc[pure.row_id].to_numpy(); pure['true'] = ref['true'].loc[pure.row_id].to_numpy()
    pp = pure.groupby('paper_id')[['pure', 'delete', 'true']].mean().join(papers.set_index('paper_id'))
    rows = []
    for g in ['all', 'target', 'control']:
        s = pp if g == 'all' else pp[pp.group_tight == g]
        rows.append(dict(group=g, n=len(s), pure=s.pure.mean(), delete=s.delete.mean(), true=s.true.mean(), year_prompt=(s.delete - s.pure).mean()))
    for k in ['pure', 'delete', 'true']:
        e = strat(pp.reset_index().rename(columns={'group_tight': 'group'}), k); rows.append(dict(group=f'tc_{k}', **{k: e[0]}, lo=e[1], hi=e[2]))
    N2 = pd.DataFrame(rows); N2.to_csv(S / 'N2_prior_pure.csv', index=False)
    L += ['', '## N2. Pure name prior (no paper at all) vs no title vs true title (model output, log10(1/rank))', '',
          'Pure prompt: ' + json.dumps('The following is the name of a researcher.' + chr(10) + 'Name:'), '', '| group | pure prior | no title | true title |', '|---|---|---|---|']
    for _, r in N2[N2.group.isin(['all', 'target', 'control'])].iterrows(): L.append(f'| {r.group} | {r.pure:+.3f} | {r.delete:+.3f} | {r.true:+.3f} |')
    for k in ['pure', 'delete', 'true']:
        r = N2[N2.group == f'tc_{k}'].iloc[0]; L.append(f'\ntarget - control within bin, {k}: {fmt(r[k], r.lo, r.hi)}')
    # ---------- F2
    if (ROOT / 'raw/alens_read/true').exists():
        per = {}
        for c in [c for c in s10.condition_names() if c != 'delete' and (ROOT / 'raw/alens_read' / c).exists()]:
            z = load_dir(ROOT / 'raw/alens_read' / c); df = pd.DataFrame({'row_id': z['row_id'], **{k: nlr(z[k]) for k in z if k.startswith('alens@')}}).merge(toks, on='row_id')
            per[c] = df.drop(columns='row_id').groupby('paper_id').mean()
        common = per['true'].index
        for c in per: common = common.intersection(per[c].index)
        spec = per['true'].loc[common] - sum(per[c].loc[common] for c in per if c != 'true') / (len(per) - 1)
        sp = spec.join(smp.set_index('paper_id'))
        rows = []
        for col in [c for c in spec.columns]:
            _, l, pos = col.split('@')
            row = dict(layer=int(l), position=pos)
            for g in ['target', 'control']:
                m = boot(sp[sp.group == g][col]); row |= {f'spec_{g}': m[0], f'{g}_lo': m[1], f'{g}_hi': m[2]}
            e = strat(sp, col); row |= dict(tc=e[0], tc_lo=e[1], tc_hi=e[2]); rows.append(row)
        F2 = pd.DataFrame(rows); F2.to_csv(S / 'F2_author_lens.csv', index=False)
        L += ['', '## F2. A lens fitted on author prompts: title-specific signal (sample, true vs 5 false titles)', '',
              '| position | layer | target | control | target - control |', '|---|---|---|---|---|']
        for _, r in F2.sort_values(['position', 'layer']).iterrows():
            L.append(f'| {r.position} | L{r.layer} | {fmt(r.spec_target, r.target_lo, r.target_hi)} | {fmt(r.spec_control, r.control_lo, r.control_hi)} | {fmt(r.tc, r.tc_lo, r.tc_hi)} |')
    (ROOT / 'reports/stage12_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('STAGE12 ANALYZED')
