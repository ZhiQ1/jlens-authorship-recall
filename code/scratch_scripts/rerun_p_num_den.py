"""User addition (2026-11-05): Stage 12 P1 / P2 split into numerator and denominator by group, as e1_num_den.

P1 (patch_pos): numerator = mean(item@l - none@l), denominator = mean(true - none@l), over the tokens whose tail has the
offset (valid), paper means over the author set; ratio = recovery (stage12_analyze). P2 (patch_comp): numerator =
mean(comp - none), denominator = mean(true - none). 'none' = the unpatched false_0 element of the same batch (the Stage 12
baseline). Groups A/B/C/D: original Stage 12 raw (Stage 11 sample); R2: addendum-8 re-run (reference only; U0 has no
P1/P2). Unwritten authors; written authors for C and R2 as a reference. Team-cluster bootstrap 2,000 (rerun_analyze Est,
seed 391 shared draw). B - A paired for numerator, denominator and ratio.
Outputs: summary_rerun/p1_p2_num_den.csv, p1_p2_num_den_B_minus_A.csv; new section appended to reports/e1_num_den.md.
"""
import numpy as np, pandas as pd
import rerun_analyze as ra

P1_ITEMS = ['p1', 'p5', 'p9', 'names', 'all']
MARK = '<!--P1P2-->'


def main():
    P, tk, au, E = ra.setup(); X = ra.Est(P, E)
    smp11 = pd.read_parquet(ra.R11 / 'config/sample.parquet'); r2 = pd.read_parquet(ra.CFG / 'rerun_R2.parquet')
    gof = {g: set(smp11.paper_id[P.grp.reindex(smp11.paper_id).to_numpy() == g]) for g in 'ABCD'}; gof['R2'] = set(r2.paper_id)
    rows, bt = [], {}
    for exp, key in (('P1', 'patch_pos'), ('P2', 'patch_comp')):
        for s in ('orig', 'R2'):
            d = ra.load_dir(ra.R12 / 'raw' / key if s == 'orig' else ra.OUT / 'raw' / key / 'R2')
            if d is None: print('WARN missing', exp, s); continue
            base = ra.token_frame(d['row_id'], tk, au, P); base['true'] = ra.nlr(d['rank_true']); R = ra.nlr(d['rank_patch'])
            if exp == 'P1':
                items = list(d['items']); layers = [int(l) for l in d['layers']]
                valid = d['valid'] if 'valid' in d else np.ones((R.shape[0], R.shape[2]), bool)
                specs = [(it, l, R[:, li, items.index(it)] - R[:, li, items.index('none')], base['true'].to_numpy() - R[:, li, items.index('none')], valid[:, items.index(it)])
                         for li, l in enumerate(layers) for it in P1_ITEMS if it in items]
            else:
                comps = list(d['comps']); none = R[:, comps.index('none')]
                specs = [(c.rstrip('0123456789'), int(c.lstrip('atnmlp')), R[:, ci] - none, base['true'].to_numpy() - none, np.ones(len(none), bool))
                         for ci, c in enumerate(comps) if c != 'none']
            for g in (['A', 'B', 'C', 'D'] if s == 'orig' else ['R2']):
                m = base.paper_id.isin(gof[g]).to_numpy()
                for who in (['unwritten', 'written'] if g in ('C', 'R2') else ['unwritten']):
                    for it, l, num, den, ok in specs:
                        b = base[m].assign(num=num[m], den=den[m])
                        pp = ra.paper_means(b, ['num', 'den'], who, valid={'num': ok[m], 'den': ok[m]}).dropna()
                        if not len(pp): continue
                        n_ = X.mean(pp, 'num'); d_ = X.mean(pp, 'den'); r_ = X.ratio(pp, 'num', 'den')
                        bt[(exp, who, g, it, l)] = (n_[4], d_[4], r_[4])
                        rows.append(dict(experiment=exp, who=who, group=g, item=it, layer=l, n_papers=len(pp),
                                         numerator=n_[0], num_lo=n_[1], num_hi=n_[2], denominator=d_[0], den_lo=d_[1], den_hi=d_[2],
                                         ratio=r_[0], ratio_lo=r_[1], ratio_hi=r_[2], descriptive_only=len(pp) < 30))
    D = pd.DataFrame(rows); D.to_csv(ra.S / 'p1_p2_num_den.csv', index=False)
    crow = []
    for (exp, who, g, it, l), (bn, bd, br) in bt.items():
        if g != 'B' or who != 'unwritten' or (exp, who, 'A', it, l) not in bt: continue
        an, ad, ar = bt[(exp, who, 'A', it, l)]
        a = D[(D.experiment == exp) & (D.who == who) & (D.group == 'A') & (D['item'] == it) & (D.layer == l)].iloc[0]
        b = D[(D.experiment == exp) & (D.who == who) & (D.group == 'B') & (D['item'] == it) & (D.layer == l)].iloc[0]
        r = dict(experiment=exp, item=it, layer=l)
        for k, x, y in (('numerator', bn, an), ('denominator', bd, ad), ('ratio', br, ar)):
            lo, hi = E.ci(x - y); r |= {f'B_minus_A_{k}': b[k] - a[k], f'{k}_lo': lo, f'{k}_hi': hi}
        r['B_over_A_numerator'] = b.numerator / a.numerator; r['B_over_A_denominator'] = b.denominator / a.denominator
        crow.append(r)
    BA = pd.DataFrame(crow); BA.to_csv(ra.S / 'p1_p2_num_den_B_minus_A.csv', index=False)
    f = ra.fmt
    L = [MARK, '## P1 / P2: numerator, denominator and ratio by group (Stage 12 originals for A-D; R2 re-run, reference only)', '',
         'P1: numerator = mean(item_l - none_l), denominator = mean(true - none_l) over tokens whose tail has the offset; P2: numerator = mean(comp - none), '
         'denominator = mean(true - none); none = unpatched false_0 element of the same batch (Stage 12 baseline). Unwritten authors; written for C/R2 '
         'as reference. U0 has no P1/P2 run. Team-cluster CIs (2,000, seed 391). R2: upper reference only, no conclusion; ceiling +0.844.', '']
    sel = lambda x: x[((x.experiment == 'P1') & x['item'].isin(['p1', 'names']) & x.layer.isin([44, 48, 52, 56])) |
                      ((x.experiment == 'P2') & x.layer.isin([24, 48, 52, 56]))]
    L += ['| exp | item | layer | group | authors | n | numerator [CI] | denominator [CI] | ratio [CI] |', '|---|---|---|---|---|---|---|---|---|']
    for r in sel(D).sort_values(['experiment', 'item', 'layer']).itertuples():
        tag = ' (reference)' if r.group == 'R2' or r.who == 'written' else ''
        L.append(f'| {r.experiment} | {r.item} | L{r.layer} | {r.group}{tag} | {r.who} | {r.n_papers}{" (n<30)" if r.descriptive_only else ""} | '
                 f'{f(r.numerator, r.num_lo, r.num_hi)} | {f(r.denominator, r.den_lo, r.den_hi)} | {f(r.ratio, r.ratio_lo, r.ratio_hi)} |')
    L += ['', '### B - A (unwritten; paired team bootstrap)', '', '| exp | item | layer | numerator B - A | denominator B - A | ratio B - A | B/A num | B/A den |', '|---|---|---|---|---|---|---|---|']
    for r in sel(BA).sort_values(['experiment', 'item', 'layer']).itertuples():
        L.append(f'| {r.experiment} | {r.item} | L{r.layer} | {f(r.B_minus_A_numerator, r.numerator_lo, r.numerator_hi)} | {f(r.B_minus_A_denominator, r.denominator_lo, r.denominator_hi)} | '
                 f'{f(r.B_minus_A_ratio, r.ratio_lo, r.ratio_hi)} | {r.B_over_A_numerator:.2f} | {r.B_over_A_denominator:.2f} |')
    L += ['', '<!--P1P2NOTE-->', '']
    md = ra.REP / 'e1_num_den.md'; old = md.read_text() if md.exists() else ''
    if MARK in old: old = old[:old.index(MARK)]
    md.write_text(old.rstrip('\n') + '\n\n' + '\n'.join(L) + '\n'); print('wrote', md, len(D), 'rows')
    # WARN-only check: ratios reproduce rerun_group_values.csv (same estimand)
    gv = ra.S / 'rerun_group_values.csv'
    if gv.exists():
        G = pd.read_csv(gv); m = D.merge(G, on=['experiment', 'who', 'group', 'item', 'layer'], suffixes=('', '_g'))
        dif = (m.ratio - m.estimate).abs().max() if len(m) else np.nan
        print(('CHECK PASS' if dif < 1e-9 else 'CHECK WARN'), 'max |ratio - rerun_group_values| =', dif, 'over', len(m), 'cells')


if __name__ == '__main__':
    main()
