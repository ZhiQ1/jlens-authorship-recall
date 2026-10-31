"""Stage 13 X3 analysis (CPU): does the model keep the paper's identity when the title is paraphrased?
Rules (authoritative): config/prereg.json (X3), addendum 1 (team tune/test split, pairs.parquet `split`), addendum 2
(team-cluster intervals primary; X3 word-overlap control), addendum 4 (X3 primary G' with the lexical neighbour D; partner
rule secondary; token roles; wording), addendum 5 (inclusion sets, jaccard2, matched-D subset, both sets, robustness).

Data: raw/para_run/shard_*.npz (whatever exists; the number is printed, WARN if < 24). resid [n, 4 versions (original,
paraphrase, partner, lexical_neighbour), 15 layers, 2 positions (title_last, colon), 5120] float16; cosine in float32.

PRIMARY (addendum 4)   G'(l,pos) = mean over papers [cos(orig, para) - cos(orig, D)].
   Paper identity from layer l: G'(l) > 0 AND G'(l) - G'(L4) > 0, both 95% team-cluster intervals excluding 0.
   The first such layer (> L4) is found on tune; it is confirmed if both conditions hold on test at that same layer.
SECONDARY (prereg.json) G(l,pos) = mean [cos(orig, para) - cos(orig, partner B)], same rule.
BEHAVIOUR first-author score (teacher-forced mean log10(1/rank) of the first author's name tokens):
   paraphrase - lexical neighbour > 0 (primary, addendum 4); paraphrase - partner (prereg.json, secondary); also
   original - paraphrase (reference). Judged on test (confirmatory); tune and all shown.
WORD-OVERLAP CONTROL (addendum 2) per pair: dcos = cos(o,para) - cos(o,X), djac = jaccard2(o,para) - jaccard2(o,X),
   drare = rare-share(o,para) - rare-share(o,X) (share of the original's rare words, document frequency < 10 among the
   cohort titles, that X contains). OLS dcos ~ 1 + djac + drare; the intercept is the version effect at equal overlap.
   Team-cluster bootstrap by weighted least squares with the same team draws.
SETS (addendum 5): primary include_primary (1,115), sensitivity include_sensitive (1,015), table
   config/x3_lexical_neighbour_j2.csv; subsets all / d_matched (D's jaccard2 >= paraphrase's) / d_unmatched.
TOKEN ROLES (addendum 4): not applicable - para_run stores only the per-name mean score and title_last/colon states.
Intervals: 95% bootstrap over author teams (pairs.parquet `team`), 2,000 draws; paper bootstrap also given for G'.

Usage: python stage13_x3_analyze.py [--out DIR] [--shards N]
   default outputs summary_x3/x3_*.csv and reports/x3_report.md; with --out everything (incl. report) goes to DIR.
   --shards N: use only the first N shard files (tiny test)."""
import argparse, hashlib, importlib.util, json, re
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; ROOT = B / '381_stage13'
NB = 2000; N_SHARDS = 24; VERS = ['original', 'paraphrase', 'partner', 'lexical_neighbour']; POS = ['title_last', 'colon']
TABLE = ROOT / 'config/x3_lexical_neighbour_j2.csv'; TABLE_SHA = 'a1c91c8763ef148f64021ca3f0d31203eed1ce294db9bbcf7df099f51a02ff69'
SETS = {'primary': 'include_primary', 'sensitivity': 'include_sensitive'}
SUBSETS = ['all', 'd_matched', 'd_unmatched']; SPLITS = ['tune', 'test', 'all']
CMP = {'lex': ('lexical neighbour D', "G'"), 'partner': ('partner B', 'G')}
SEED = {('tune', 'all'): 311, ('test', 'all'): 312, ('all', 'all'): 313, ('tune', 'd_matched'): 321, ('test', 'd_matched'): 322,
        ('all', 'd_matched'): 323, ('tune', 'd_unmatched'): 331, ('test', 'd_unmatched'): 332, ('all', 'd_unmatched'): 333}
WARN = []


def warn(m): WARN.append(m); print('WARN', m, flush=True)
def ci(b): return np.nanpercentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.4f} [{lo:+.4f}, {hi:+.4f}]'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def team_w(teams, seed):
    codes, uniq = pd.factorize(pd.Series(teams))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]   # [NB, n]


def paper_w(n, seed):
    return np.random.default_rng(seed + 1000).multinomial(n, np.full(n, 1 / n), size=NB).astype(float)


def read_shards(nmax):
    fs = sorted((ROOT / 'raw/para_run').glob('shard_*.npz'))
    if nmax: fs = fs[:nmax]
    print(f'para_run shards found: {len(fs)} of {N_SHARDS}: ' + ', '.join(f.stem for f in fs), flush=True)
    if len(fs) < N_SHARDS: warn(f'only {len(fs)} of {N_SHARDS} para_run shards present (results are partial)')
    meta, cos, layers = [], [], None
    for f in fs:
        z = np.load(f); n = len(z['paper_id'])
        if n == 0: print(f'{f.stem}: 0 rows'); continue
        ly = [int(x) for x in z['layers']]; vs = [str(x) for x in z['versions']]
        if layers is None: layers = ly
        elif ly != layers: warn(f'{f.stem}: layers {ly} differ from {layers}')
        if vs != VERS: warn(f'{f.stem}: versions {vs} != {VERS}')
        R = z['resid']
        if R.shape[1:] != (4, len(ly), 2, R.shape[-1]): warn(f'{f.stem}: resid shape {R.shape} unexpected')
        R = R.astype(np.float32); Rn = R / np.linalg.norm(R, axis=-1, keepdims=True)
        c = np.einsum('nlpd,nvlpd->nvlp', Rn[:, 0], Rn)                      # [n, 4 (orig vs each version), L, pos]
        if not np.isfinite(c).all(): warn(f'{f.stem}: non-finite cosines ({(~np.isfinite(c)).sum()})')
        dev = np.abs(c[:, 0] - 1).max()
        print(f'{f.stem}: n={n} resid {R.shape} {z["resid"].dtype}; |cos(orig,orig)-1| max {dev:.2e}', flush=True)
        if dev > 1e-3: warn(f'{f.stem}: cos(original, original) deviates from 1 by {dev:.2e}')
        cos.append(c)
        meta.append(pd.DataFrame({k: z[k] for k in ('paper_id', 'partner', 'score_original', 'score_paraphrase', 'score_partner',
                                                     'score_lexical', 'word_jaccard', 'lexical_neighbour', 'lexical_jaccard')}).assign(shard=f.stem))
        del R, Rn
    if not cos: raise SystemExit('no para_run rows')
    return pd.concat(meta, ignore_index=True), np.concatenate(cos), layers, len(fs)


def overlap_cols(df, papers):
    """jaccard2 (addendum 5) and rare-word share (addendum 2) of (original, paraphrase), (original, D), (original, partner)."""
    pn = load(H / '13_stage13/stage13_para_nli.py', 'pnli')
    W = {q: pn.words2(t) for q, t in zip(papers.paper_id, papers.title)}
    dfreq = {}
    for s in W.values():
        for w in s: dfreq[w] = dfreq.get(w, 0) + 1
    rare = lambda s: {w for w in s if dfreq.get(w, 0) < 10}
    paras = {}
    for f in sorted((ROOT / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); paras |= dict(zip(z['paper_id'], z['paraphrase']))
    out = {}
    for x in ('para', 'lex', 'partner'): out[f'jac_{x}'] = []; out[f'rare_{x}'] = []
    out['n_rare_orig'] = []
    for r in df.itertuples():
        a = W[r.paper_id]; ra = rare(a); out['n_rare_orig'].append(len(ra))
        for x, s in (('para', pn.words2(paras[r.paper_id])), ('lex', W[r.lexical_neighbour]), ('partner', W[r.partner])):
            out[f'jac_{x}'].append(pn.jac(a, s)); out[f'rare_{x}'].append(len(ra & s) / len(ra) if ra else 0.0)
    return df.assign(**out)


def g_rows(s, C, layers, W, Wp, part, sub, setn):
    """per comparison, layer, position: mean gap, team CI, paper CI, gap - gap(L4) with team CI."""
    rows = []; i4 = layers.index(4) if 4 in layers else None
    for key in CMP:
        vi = 3 if key == 'lex' else 2
        V = C[:, 1] - C[:, vi]                                                   # [n, L, pos]
        for p, pos in enumerate(POS):
            Bt = np.einsum('bn,nl->bl', W, V[:, :, p]) / W.sum(1, keepdims=True); Bp = np.einsum('bn,nl->bl', Wp, V[:, :, p]) / Wp.sum(1, keepdims=True)
            for li, l in enumerate(layers):
                r = dict(set=setn, subset=sub, split=part, comparison=key, pos=pos, layer=l, n=len(s), n_teams=s.team.nunique(),
                         cos_orig_para=C[:, 1, li, p].mean(), cos_orig_other=C[:, vi, li, p].mean(), gap=V[:, li, p].mean())
                r['lo'], r['hi'] = ci(Bt[:, li]); r['lo_paper'], r['hi_paper'] = ci(Bp[:, li])
                if i4 is not None:
                    r['gap_minus_L4'] = V[:, li, p].mean() - V[:, i4, p].mean(); r['dL4_lo'], r['dL4_hi'] = ci(Bt[:, li] - Bt[:, i4])
                rows.append(r)
    return rows


def ols_rows(s, C, layers, W, part, sub, setn):
    """addendum 2 control: dcos ~ 1 + djac + drare (team-weighted bootstrap); intercept = version effect at equal overlap."""
    rows = []
    for key in CMP:
        vi = 3 if key == 'lex' else 2
        X = np.column_stack([np.ones(len(s)), (s.jac_para - s[f'jac_{key}']).to_numpy(), (s.rare_para - s[f'rare_{key}']).to_numpy()])
        if len(s) < 5 or np.linalg.matrix_rank(X) < 3:
            X = X[:, :2]                                                         # e.g. no rare words at all: drop that covariate
        for p, pos in enumerate(POS):
            Y = (C[:, 1, :, p] - C[:, vi, :, p])                                 # [n, L]
            beta = np.linalg.lstsq(X, Y, rcond=None)[0]                          # [k, L]
            XtWX = np.einsum('bn,nk,nj->bkj', W, X, X); XtWY = np.einsum('bn,nk,nl->bkl', W, X, Y)
            bb = np.full((NB, X.shape[1], len(layers)), np.nan); ok = np.linalg.cond(XtWX) < 1e12
            bb[ok] = np.linalg.solve(XtWX[ok], XtWY[ok])
            for li, l in enumerate(layers):
                r = dict(set=setn, subset=sub, split=part, comparison=key, pos=pos, layer=l, n=len(s), k=X.shape[1],
                         mean_djac=X[:, 1].mean(), version_effect=beta[0, li], slope_djac=beta[1, li])
                r['lo'], r['hi'] = ci(bb[:, 0, li]); r['slope_djac_lo'], r['slope_djac_hi'] = ci(bb[:, 1, li])
                if X.shape[1] == 3: r['slope_drare'] = beta[2, li]
                rows.append(r)
    return rows


def beh_rows(s, W, part, sub, setn):
    rows = []
    for name, a, b in (('para_minus_lex', 'score_paraphrase', 'score_lexical'), ('para_minus_partner', 'score_paraphrase', 'score_partner'),
                       ('orig_minus_para', 'score_original', 'score_paraphrase'), ('orig_minus_partner', 'score_original', 'score_partner'),
                       ('orig_minus_lex', 'score_original', 'score_lexical')):
        v = (s[a] - s[b]).to_numpy(); bt = (W @ v) / W.sum(1)
        rows.append(dict(set=setn, subset=sub, split=part, contrast=name, n=len(s), mean=v.mean(), lo=ci(bt)[0], hi=ci(bt)[1],
                         share_positive=(v > 0).mean(), score_a=s[a].mean(), score_b=s[b].mean()))
    return rows


def identity(G, setn, sub, key, pos, layers):
    g = G[(G.set == setn) & (G.subset == sub) & (G.comparison == key) & (G.pos == pos)]
    ok = lambda r: bool(r.lo > 0 and r.dL4_lo > 0)
    t = g[(g.split == 'tune') & (g.layer > 4)].sort_values('layer')
    l0 = next((int(r.layer) for r in t.itertuples() if ok(r)), None)
    if l0 is None: return dict(layer_tune=None, confirmed=False, test=None)
    te = g[(g.split == 'test') & (g.layer == l0)].iloc[0]
    return dict(layer_tune=l0, confirmed=ok(te), test=te)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--shards', type=int); a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / 'summary_x3'; rep = (out / 'x3_report.md') if a.out else ROOT / 'reports/x3_report.md'
    out.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    if sha != TABLE_SHA: warn(f'inclusion table sha256 {sha} != addendum 5 value {TABLE_SHA}')
    tab = pd.read_csv(TABLE); pairs = pd.read_parquet(ROOT / 'config/pairs.parquet'); papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    df, C, layers, nsh = read_shards(a.shards)
    print(f'rows {len(df)}; cos array {C.shape}; layers {layers}', flush=True)
    # ---- joins (WARN, never stop)
    miss_t = ~df.paper_id.isin(tab.paper_id); miss_p = ~df.paper_id.isin(pairs.paper_id)
    if miss_t.any(): warn(f'{miss_t.sum()} para_run paper_id(s) missing from the inclusion table: {df.paper_id[miss_t].tolist()[:10]}')
    if miss_p.any(): warn(f'{miss_p.sum()} para_run paper_id(s) missing from pairs.parquet: {df.paper_id[miss_p].tolist()[:10]}')
    if df.paper_id.duplicated().any(): warn(f'{df.paper_id.duplicated().sum()} duplicated paper_id rows in para_run')
    df = df.merge(tab[['paper_id', 'lexical_neighbour_j2', 'lexical_jaccard2', 'para_jaccard2', 'd_matched', 'include_primary', 'include_sensitive']],
                  on='paper_id', how='left').merge(pairs[['paper_id', 'partner', 'team', 'split', 'group', 'field']].rename(columns={'partner': 'partner_pairs'}),
                                                   on='paper_id', how='left')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): df[c] = df[c].fillna(False).astype(bool)
    nd = (df.lexical_neighbour != df.lexical_neighbour_j2).sum(); npn = (df.partner != df.partner_pairs).sum()
    if nd: warn(f'{nd} rows: stored lexical_neighbour != table lexical_neighbour_j2')
    if npn: warn(f'{npn} rows: stored partner != pairs.parquet partner')
    dj = np.nanmax(np.abs(df.lexical_jaccard - df.lexical_jaccard2)) if len(df) else 0
    if dj > 1e-9: warn(f'stored lexical_jaccard differs from table lexical_jaccard2 (max {dj:.3g})')
    df = overlap_cols(df, papers)
    dj2 = np.abs(df.jac_para - df.para_jaccard2).max()
    if dj2 > 1e-9: warn(f'recomputed jaccard2(original, paraphrase) differs from table para_jaccard2 (max {dj2:.3g})')
    # expected counts given the shards present (table rows that are in pairs; para_run also needs the paper's author context)
    exp = tab[tab.paper_id.isin(pairs.paper_id)]
    joins = dict(shards=nsh, rows=len(df), missing_in_table=int(miss_t.sum()), missing_in_pairs=int(miss_p.sum()),
                 primary=int(df.include_primary.sum()), sensitive=int(df.include_sensitive.sum()),
                 primary_d_matched=int((df.include_primary & df.d_matched).sum()), sensitive_d_matched=int((df.include_sensitive & df.d_matched).sum()),
                 rows_not_primary=int((~df.include_primary).sum()), table_primary_in_pairs=int(exp.include_primary.sum()),
                 table_sensitive_in_pairs=int(exp.include_sensitive.sum()), d_mismatch=int(nd), partner_mismatch=int(npn))
    if nsh == N_SHARDS and joins['primary'] != 1115: warn(f'all shards present but primary n = {joins["primary"]} (addendum 5: 1,115; table rows in pairs: {joins["table_primary_in_pairs"]})')
    if nsh == N_SHARDS and joins['sensitive'] != 1015: warn(f'all shards present but sensitivity n = {joins["sensitive"]} (addendum 5: 1,015)')
    print('joins', json.dumps(joins), flush=True)
    df.drop(columns=[]).to_csv(out / 'x3_pairs.csv', index=False)
    # per-paper cosines (long) for later checks
    li = pd.MultiIndex.from_product([range(len(df)), ['paraphrase', 'partner', 'lexical_neighbour'], layers, POS], names=['row', 'version', 'layer', 'pos'])
    pd.DataFrame({'cos_with_original': C[:, 1:].reshape(-1)}, index=li).reset_index().assign(paper_id=lambda x: df.paper_id.to_numpy()[x.row]).drop(columns='row') \
        .to_csv(out / 'x3_cos_per_paper.csv.gz', index=False)
    # ---- analyses
    G, O, Bh = [], [], []
    for setn, col in SETS.items():
        for sub in SUBSETS:
            m0 = df[col].to_numpy() & (df.team.notna().to_numpy())
            if sub == 'd_matched': m0 &= df.d_matched.to_numpy()
            if sub == 'd_unmatched': m0 &= ~df.d_matched.to_numpy()
            for part in SPLITS:
                m = m0 if part == 'all' else m0 & (df.split == part).to_numpy()
                s = df[m]; Cs = C[m]
                if len(s) < 2: print(f'skip {setn}/{sub}/{part}: n={len(s)}'); continue
                W = team_w(s.team.to_numpy(), SEED[part, sub]); Wp = paper_w(len(s), SEED[part, sub])
                G += g_rows(s, Cs, layers, W, Wp, part, sub, setn); Bh += beh_rows(s, W, part, sub, setn)
                O += ols_rows(s, Cs, layers, W, part, sub, setn)
    G, O, Bh = pd.DataFrame(G), pd.DataFrame(O), pd.DataFrame(Bh)
    G.to_csv(out / 'x3_gap.csv', index=False); O.to_csv(out / 'x3_overlap_control.csv', index=False); Bh.to_csv(out / 'x3_behaviour.csv', index=False)
    # ---- verdicts
    V = []
    for setn in SETS:
        for sub in SUBSETS:
            for key in CMP:
                for pos in POS:
                    if G.empty or not ((G.set == setn) & (G.subset == sub) & (G.comparison == key) & (G.pos == pos) & (G.split == 'tune')).any():
                        V.append(dict(set=setn, subset=sub, comparison=key, pos=pos, layer_tune=None, confirmed=None, note='no data')); continue
                    r = identity(G, setn, sub, key, pos, layers); t = r['test']
                    oc = O[(O.set == setn) & (O.subset == sub) & (O.comparison == key) & (O.pos == pos) & (O.split == 'test') & (O.layer == r['layer_tune'])] if r['layer_tune'] else None
                    V.append(dict(set=setn, subset=sub, comparison=key, pos=pos, layer_tune=r['layer_tune'], confirmed=r['confirmed'],
                                  gap_test=None if t is None else t.gap, lo_test=None if t is None else t.lo, hi_test=None if t is None else t.hi,
                                  dL4_test=None if t is None else t.gap_minus_L4, dL4_lo_test=None if t is None else t.dL4_lo, dL4_hi_test=None if t is None else t.dL4_hi,
                                  overlap_ctrl_test=None if oc is None or oc.empty else oc.version_effect.iloc[0],
                                  overlap_ctrl_lo=None if oc is None or oc.empty else oc.lo.iloc[0], overlap_ctrl_hi=None if oc is None or oc.empty else oc.hi.iloc[0]))
    V = pd.DataFrame(V); V.to_csv(out / 'x3_identity_verdict.csv', index=False)
    # ---- report
    L = ['# Stage 13 X3: paper identity under paraphrase', '',
         'Rules: config/prereg.json (X3), addenda 1, 2, 4, 5. Results are the model\'s internal representation similarity and its internal preference for the correct first-author tokens under teacher forcing (scored continuations), not the process by which it generates authors (addendum 4, wording).', '',
         f'Shards: {nsh} of {N_SHARDS}. Rows {len(df)}; primary set n = {joins["primary"]} (addendum 5 full: 1,115), sensitivity n = {joins["sensitive"]} (full: 1,015); matched-D: primary {joins["primary_d_matched"]}, sensitivity {joins["sensitive_d_matched"]}. Layers {layers}; positions {POS}.',
         'Intervals: 95% team-cluster bootstrap (pairs.parquet `team`, 2,000 draws; primary per addendum 2); paper bootstrap also in x3_gap.csv. Inclusion table sha256 ' + ('OK' if sha == TABLE_SHA else 'MISMATCH') + '.', '']
    if nsh < N_SHARDS: L += [f'**PARTIAL DATA ({nsh}/{N_SHARDS} shards): numbers below are a pipeline check, not results.**', '']
    if WARN: L += ['**WARN**:', ''] + [f'- {w}' for w in WARN] + ['']
    fv = lambda r: 'none on tune' if r.layer_tune is None or pd.isna(r.layer_tune) else f'L{int(r.layer_tune)} on tune; test: gap {fm(r.gap_test, r.lo_test, r.hi_test)}, minus L4 {fm(r.dL4_test, r.dL4_lo_test, r.dL4_hi_test)} -> ' + ('**confirmed**' if r.confirmed else '**not confirmed**')
    L += ['## Verdict (automatic)', '']
    beh = lambda setn, sub, c, part='test': Bh[(Bh.set == setn) & (Bh.subset == sub) & (Bh.contrast == c) & (Bh.split == part)]
    summ = {}
    for setn in SETS:
        L += [f'### {setn} set', '']
        for sub in ('all', 'd_matched'):
            lab = 'all included pairs' if sub == 'all' else 'matched-D subset (D\'s jaccard2 >= paraphrase\'s)'
            for key in ('lex', 'partner'):
                tag = 'PRIMARY G\' (vs lexical neighbour D)' if key == 'lex' else 'secondary G (vs partner B, prereg.json)'
                for pos in POS:
                    r = V[(V.set == setn) & (V.subset == sub) & (V.comparison == key) & (V.pos == pos)].iloc[0]
                    if r.get('note') == 'no data': L.append(f'- {lab}, {tag}, {pos}: no data'); continue
                    oc = '' if r.layer_tune is None or pd.isna(r.layer_tune) or pd.isna(r.overlap_ctrl_test) else f'; word-overlap-controlled version effect on test {fm(r.overlap_ctrl_test, r.overlap_ctrl_lo, r.overlap_ctrl_hi)}'
                    L.append(f'- {lab}, {tag}, {pos}: identity from {fv(r)}{oc}')
                    summ[setn, sub, key, pos] = (None if r.layer_tune is None or pd.isna(r.layer_tune) else int(r.layer_tune), bool(r.confirmed))
            for c, tag in (('para_minus_lex', 'PRIMARY behaviour: paraphrase - lexical neighbour'), ('para_minus_partner', 'secondary behaviour: paraphrase - partner')):
                b = beh(setn, sub, c)
                if b.empty: L.append(f'- {lab}, {tag}: no test data'); continue
                b = b.iloc[0]; res = 'POSITIVE (> 0)' if b.lo > 0 else ('NEGATIVE (< 0)' if b.hi < 0 else 'interval includes 0')
                ba = beh(setn, sub, c, 'all'); extra = '' if ba.empty else f' (all: {fm(ba.iloc[0]["mean"], ba.iloc[0].lo, ba.iloc[0].hi)})'
                L.append(f'- {lab}, {tag}, test n={b.n}: {fm(b["mean"], b.lo, b.hi)} -> **{res}**{extra}')
                summ[setn, sub, c] = res
            L.append('')
    diff = [k for k in summ if k[0] == 'primary' and ('sensitivity',) + k[1:] in summ and summ[k] != summ[('sensitivity',) + k[1:]]]
    L += ['### Robustness (addendum 5: a conclusion that changes between sets is "not robust")', '']
    if not diff: L.append('- All verdicts above (identity layer and confirmation per comparison/position, behaviour sign) are the same in the primary and sensitivity sets: **robust**.')
    for k in diff:
        a, b = summ[k], summ[('sensitivity',) + k[1:]]
        kind = ('identity layer differs (both ' + ('confirmed' if a[1] else 'not confirmed') + ')') if isinstance(a, tuple) and a[1] == b[1] and a[0] is not None and b[0] is not None else 'conclusion differs'
        L.append(f'- {"/".join(map(str, k[1:]))}: primary {a} vs sensitivity {b} ({kind}) -> **not robust**')
    L += ['', 'Conclusions follow the primary set (addendum 5). Token roles: not applicable (para_run stores only the per-name mean score). Pairs without a matched D (d_unmatched) are reported separately in the CSVs and the tables below (addendum 4, "also").', '']
    # tables
    for setn in SETS:
        for sub in SUBSETS:
            for key in CMP:
                g = G[(G.set == setn) & (G.subset == sub) & (G.comparison == key)]
                if g.empty: continue
                L += [f'## {setn} / {sub}: {CMP[key][1]} = cos(orig, para) - cos(orig, {CMP[key][0]})', '']
                for pos in POS:
                    L += [f'### {pos}', '', '| layer | tune | tune - L4 | test | test - L4 | test, overlap-controlled | all |', '|---|---|---|---|---|---|---|']
                    for l in layers:
                        f = lambda part: g[(g.split == part) & (g.pos == pos) & (g.layer == l)]
                        o = O[(O.set == setn) & (O.subset == sub) & (O.comparison == key) & (O.pos == pos) & (O.split == 'test') & (O.layer == l)]
                        cell = lambda x: '-' if x.empty else fm(x.iloc[0].gap, x.iloc[0].lo, x.iloc[0].hi)
                        cd = lambda x: '-' if x.empty else fm(x.iloc[0].gap_minus_L4, x.iloc[0].dL4_lo, x.iloc[0].dL4_hi)
                        L.append(f'| L{l} | {cell(f("tune"))} | {cd(f("tune"))} | {cell(f("test"))} | {cd(f("test"))} | ' + ('-' if o.empty else fm(o.iloc[0].version_effect, o.iloc[0].lo, o.iloc[0].hi)) + f' | {cell(f("all"))} |')
                    L.append('')
    L += ['## Behaviour (first-author teacher-forced score, mean log10(1/rank))', '', '| set | subset | split | n | para - D | para - partner | orig - para | orig - partner | orig - D |', '|---|---|---|---|---|---|---|---|---|']
    for (setn, sub, part), b in Bh.groupby(['set', 'subset', 'split'], sort=False):
        b = b.set_index('contrast')
        L.append(f'| {setn} | {sub} | {part} | {b.n.iloc[0]} | ' + ' | '.join(fm(b.loc[c, "mean"], b.loc[c, "lo"], b.loc[c, "hi"]) for c in ('para_minus_lex', 'para_minus_partner', 'orig_minus_para', 'orig_minus_partner', 'orig_minus_lex')) + ' |')
    L += ['', '## Word overlap (jaccard2, addendum 5; rare = document frequency < 10 among cohort titles)', '', '| set | n | jac(o, para) | jac(o, D) | jac(o, partner) | rare share para | rare share D | rare share partner | D matched |', '|---|---|---|---|---|---|---|---|---|']
    for setn, col in SETS.items():
        s = df[df[col]]
        if len(s): L.append(f'| {setn} | {len(s)} | {s.jac_para.median():.3f} | {s.jac_lex.median():.3f} | {s.jac_partner.median():.3f} | {s.rare_para.mean():.3f} | {s.rare_lex.mean():.3f} | {s.rare_partner.mean():.3f} | {s.d_matched.mean():.3f} |')
    L += ['', '(jaccard: medians; rare share: means.) Overlap control: OLS dcos ~ 1 + djac + drare per layer/position, intercept = version effect at equal word overlap (addendum 2); full results incl. slopes in x3_overlap_control.csv.', '']
    rep.write_text('\n'.join(L) + '\n'); print('\n'.join(L))
    json.dump(dict(joins=joins, warn=WARN, robust=not diff, not_robust=[list(map(str, k)) for k in diff]), open(out / 'x3_meta.json', 'w'), indent=1)
    print('X3 ANALYZED', flush=True)


if __name__ == '__main__':
    main()
