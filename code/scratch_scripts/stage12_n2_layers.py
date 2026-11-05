"""V21 (handbook G4), POST-HOC: Stage 12 N2 (pure name prior) per readout and layer.
371_stage12/raw/prior_pure saved ranks for final@63 and logit / jlens_public at L48, L56, L62 (PURE_PLAN in 371_stage12.py),
but 12_stage12/stage12_analyze.py analysed final@63 only. This script repeats the N2 estimands unchanged
(stage12_analyze.py lines 107-127) for every saved readout x layer, pairing each with the Stage 10 true / delete runs
at the SAME readout and layer (351_stage10/raw[/cond_delete]/<readout>/L<layer>/shard_*.npz, same row ids):
  per group (all / target / control, cohort group_tight): mean pure, delete, true (tokens averaged within paper first),
  year_prompt = delete - pure; target - control within citation bin (bins with >= 30 papers per group) for pure,
  delete, true. Intervals: paper bootstrap (as Stage 12, 2,000 draws) AND team-cluster bootstrap (addendum 2; teams =
  stage13_cpu.group_folds), both 95%. Group means also get both intervals.
Self-check (WARN only): final@63 point estimates reproduce 371_stage12/summary/N2_prior_pure.csv.
Not pre-registered in Stage 12 for these layers: post-hoc.
Outputs (new): 371_stage12/summary/N2_prior_pure_layers.csv, 371_stage12/reports/n2_layers.md"""
import importlib.util, json, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '371_stage12'; NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def nlr(r): return -np.log10(np.asarray(r, float))
def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'
def safe(p):
    p = Path(p)
    return p if not p.exists() else p.with_name(f'{p.stem}.{time.strftime("%Y%m%d_%H%M%S")}{p.suffix}')


def cw(cl, seed):
    codes, uniq = pd.factorize(pd.Series(cl))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def mean_ci(x, Ws):
    return [ci((W @ x) / W.sum(1)) for W in Ws]


def strat(x, grp, cbin, Ws, min_n=30):
    cells = []
    for b in pd.unique(cbin):
        ia = np.where((cbin == b) & (grp == 'target'))[0]; ib = np.where((cbin == b) & (grp == 'control'))[0]
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum()
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); out = []
    for W in Ws:
        bt = np.zeros(NB)
        for wi, (a, b) in zip(w, cells): bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
        out.append(ci(bt))
    return est, out, len(cells)


def main():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    zs = [np.load(f, allow_pickle=True) for f in sorted((ROOT / 'raw/prior_pure').glob('shard_*.npz'))]
    keys = [k for k in zs[0].files if '@' in k]; rid = np.concatenate([z['row_id'] for z in zs])
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
    _, team = c13.group_folds(papers.paper_id.to_numpy()); papers['team'] = team
    rows, warn = [], []
    for k in keys:
        ro, l = k.split('@'); l = int(l)
        df = pd.DataFrame({'row_id': rid, 'pure': nlr(np.concatenate([z[k] for z in zs]))})
        for c in ('true', 'delete'):
            d = R10 / 'raw' if c == 'true' else R10 / 'raw' / f'cond_{c}'
            fs = sorted((d / ro / f'L{l:02d}').glob('shard_*.npz'))
            if len(fs) != 72: warn.append(f'{ro} L{l} {c}: {len(fs)} shards (expected 72)')
            q = [np.load(f) for f in fs]; ref = pd.Series(nlr(np.concatenate([x['rank'] for x in q])), index=np.concatenate([x['row_id'] for x in q]))
            miss = ~df.row_id.isin(ref.index)
            if miss.any(): warn.append(f'{ro} L{l} {c}: {int(miss.sum())} rows missing')
            df[c] = ref.reindex(df.row_id).to_numpy()
        df['paper_id'] = toks.loc[df.row_id].paper_id.to_numpy()
        pp = df.groupby('paper_id')[['pure', 'delete', 'true']].mean().join(papers.set_index('paper_id')).reset_index()
        for g in ('all', 'target', 'control'):
            s = pp if g == 'all' else pp[pp.group_tight == g]; Ws = [cw(s.team, 1201), cw(s.paper_id, 1202)]
            for est in ('pure', 'delete', 'true', 'year_prompt', 'title_gain'):
                x = (s.delete - s.pure) if est == 'year_prompt' else ((s.true - s.delete) if est == 'title_gain' else s[est])
                x = x.to_numpy(float); (lt, ht), (lp, hp) = mean_ci(x, Ws)
                rows.append(dict(readout=ro, layer=l, group=g, estimand=est, n=len(s), est=x.mean(), lo_team=lt, hi_team=ht, lo_paper=lp, hi_paper=hp))
        Ws = [cw(pp.team, 1203), cw(pp.paper_id, 1204)]
        for est in ('pure', 'delete', 'true', 'year_prompt', 'title_gain'):
            x = (pp.delete - pp.pure) if est == 'year_prompt' else ((pp.true - pp.delete) if est == 'title_gain' else pp[est])
            e, ((lt, ht), (lp, hp)), nb = strat(x.to_numpy(float), pp.group_tight.to_numpy(), pp.citation_bin.to_numpy(), Ws)
            rows.append(dict(readout=ro, layer=l, group='target-control (within bin)', estimand=est, n=nb, est=e, lo_team=lt, hi_team=ht, lo_paper=lp, hi_paper=hp))
        print(time.strftime('%H:%M:%S'), k, 'done', flush=True)
    D = pd.DataFrame(rows)
    try:
        o = pd.read_csv(ROOT / 'summary/N2_prior_pure.csv'); f = D[(D.readout == 'final') & (D.layer == 63)]
        for g in ('all', 'target', 'control'):
            for est in ('pure', 'delete', 'true', 'year_prompt'):
                a = f[(f.group == g) & (f.estimand == est)].est.iloc[0]; b = o[o.group == g][est].iloc[0]
                if abs(a - b) > 1e-9: warn.append(f'final@63 {g} {est}: {a:.6f} vs Stage 12 {b:.6f}')
        for est in ('pure', 'delete', 'true'):
            a = f[(f.group.str.startswith('target-control')) & (f.estimand == est)].est.iloc[0]; b = o[o.group == f'tc_{est}'][est].iloc[0]
            if abs(a - b) > 1e-9: warn.append(f'final@63 tc {est}: {a:.6f} vs Stage 12 {b:.6f}')
    except Exception as ex: warn.append(f'parity check failed: {ex!r}')
    p_csv = safe(ROOT / 'summary/N2_prior_pure_layers.csv'); D.to_csv(p_csv, index=False)
    order = [('final', 63)] + [(r, l) for r in ('logit', 'jlens_public') for l in (48, 56, 62)]
    L = ['# Stage 12 N2 by readout and layer (V21, POST-HOC)', '',
         f'Script `~/jlens_work/13_stage13/stage12_n2_layers.py`, run {time.strftime("%Y-%m-%d %H:%M")}. CPU only, saved ranks (371_stage12/raw/prior_pure, 72 shards; Stage 10 true / delete raw at the same readout and layer). **Post-hoc: Stage 12 analysed only final@63.**',
         'Pure prompt: ' + json.dumps('The following is the name of a researcher.\nName:') + ' (no paper). Score = log10(1/rank) of the gold name tokens, averaged within paper. year_prompt = no-title prompt (with year) - pure; title_gain = true - no title.',
         'Groups: cohort group_tight (target 4,621, control 2,220). Target - control within citation bin, bins with >= 30 papers per group (Stage 10/12 rule). 95% intervals: team-cluster (addendum 2, primary) and paper bootstrap (as Stage 12), 2,000 draws each.',
         f'CSV: `{p_csv}`.', '']
    if warn: L += ['**WARN**: ' + '; '.join(warn), '']
    else: L += ['Self-check: final@63 reproduces summary/N2_prior_pure.csv exactly.', '']
    g = lambda ro, l, grp, est: D[(D.readout == ro) & (D.layer == l) & (D.group == grp) & (D.estimand == est)].iloc[0]
    L += ['## Group means (team CI)', '', '| readout | layer | group | pure prior | no title (year) | true title | no title - pure | true - no title |', '|---|---|---|---|---|---|---|---|']
    for ro, l in order:
        for grp in ('all', 'target', 'control'):
            L.append(f'| {ro} | L{l} | {grp} | ' + ' | '.join(fm(g(ro, l, grp, e).est, g(ro, l, grp, e).lo_team, g(ro, l, grp, e).hi_team) for e in ('pure', 'delete', 'true', 'year_prompt', 'title_gain')) + ' |')
    L += ['', '## Target - control within citation bin', '', '| readout | layer | estimand | estimate | team CI | paper CI | bins |', '|---|---|---|---|---|---|---|']
    for ro, l in order:
        for e in ('pure', 'delete', 'true', 'title_gain'):
            r = g(ro, l, 'target-control (within bin)', e)
            L.append(f'| {ro} | L{l} | {e} | {r.est:+.4f} | [{r.lo_team:+.4f}, {r.hi_team:+.4f}] | [{r.lo_paper:+.4f}, {r.hi_paper:+.4f}] | {r.n} |')
    L += ['', '## Reading (post-hoc)', '',
          '- Stage 12 N2 (final@63): target papers\' authors are slightly more expected even with no paper at all (pure prior target - control), which is the name-prior part of the target - control output difference. The table above shows how much of that prior, of the no-title (year) level and of the true-title level is already readable by the logit / public J-lens at L48, L56 and L62.',
          '- Compare the pure-prior target - control with the true-title target - control at the same layer: the share of the true-title difference that a paper-free prior already gives is the prior-only part at that layer.',
          '- The logit lens at L48 is near the floor for every prompt (about -4.5); the public J-lens at L48 / L56 is not at the floor, but there the true title scores BELOW the no-title prompt (true - no title < 0, more so for target papers), so at those layers its target - control values are negative and do not show the output-level pattern; only L62 (both lenses) reproduces the output pattern (pure prior +0.03-0.04, true title +0.22-0.25).',
          '- The pure prompt differs from the paper prompts in everything before the name, so "pure" vs "no title" compares two prompts, not a single intervention.']
    p_md = safe(ROOT / 'reports/n2_layers.md'); p_md.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nN2 LAYERS DONE', p_md)


if __name__ == '__main__':
    main()
