"""Stage 13 X2 analysis (CPU): subspace patching. Rules: config/prereg_addendum6.json (frozen 2026-11-05).

carry : R_S(l) = mean(carry_S@l - corrupt) / mean(clean - corrupt)   (ratio of means, as X1)
remove: L_S(l) = mean(clean - remove_S@l) / mean(clean - corrupt)
S in id (H2), auth (H3), rand (average of the 3 random subspaces, per bootstrap draw), full (X1 replacement), zero.
Intervals: 95% team-cluster bootstrap (pairs.parquet team), 2,000 draws (seed 101, as X1).
Decision (carry arm): the layer for S_id and for S_auth is the one with the largest R_S - R_rand on TUNE; on TEST at that
layer: 'S carries' if the interval of R_S - R_rand > 0; H2 support = S_id carries and R_id >= 0.5 x R_full; H3 support =
S_auth carries and the interval of R_auth - R_id > 0; 'neither' if no layer (tune or test) has an R_id - R_rand or
R_auth - R_rand interval above 0. Remove arm: same intervals, converging evidence only.
Checks (WARN only): S_full vs X1 authors@l (|delta R| <= 0.05), S = 0 identity patch (carry_zero == corrupt,
remove_zero == clean), the 3 random subspaces agree (pairwise difference intervals include 0).
Usage: python stage13_x2_analyze.py [--tiny]
Outputs: summary_x2/x2_curves.csv, x2_diffs.csv, x2_verdict.csv, x2_checks.csv, x2_capture.csv; reports/x2_report.md"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

TINY = '--tiny' in sys.argv
B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT0 = B / '381_stage13'; ROOT = ROOT0 / 'x2_tiny' if TINY else ROOT0
SUB = ROOT / 'summary_x2'; RAW = ROOT / 'raw/x2'; X1RAW = ROOT / 'raw/xpatch'; REP = ROOT / 'reports'
NB = 2000; LAYERS = [0, 1] if TINY else [16, 24, 32, 40, 48]; RS = ['rand61', 'rand62', 'rand63']
SNAMES = ['id', 'auth', 'rand', 'full', 'zero']


def load_dir(d):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
    keys = [k for k in zs[0].files if k != 'meta']
    return pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in keys}), len(zs)


def team_w(teams, seed):
    codes, uniq = pd.factorize(pd.Series(teams))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def ratios(s):
    """{(arm, S, l): (estimate, draws)} for one split"""
    W = team_w(s.team, 101); den = (s.clean - s.corrupt).to_numpy(); dw = W @ den; out = {}
    for arm in ('carry', 'remove'):
        for l in LAYERS:
            for v in ['id', 'auth', 'full', 'zero'] + RS:
                x = s[f'{arm}_{v}@{l}'].to_numpy()
                num = x - s.corrupt.to_numpy() if arm == 'carry' else s.clean.to_numpy() - x
                out[arm, v, l] = (num.mean() / den.mean(), (W @ num) / dw)
            out[arm, 'rand', l] = (np.mean([out[arm, r, l][0] for r in RS]), np.mean([out[arm, r, l][1] for r in RS], 0))
    return out, den.mean()


def main():
    REP.mkdir(parents=True, exist_ok=True)
    pairs = pd.read_parquet(ROOT0 / 'config/pairs.parquet')
    df, nsh = load_dir(RAW); df = df.merge(pairs[['paper_id', 'team']], on='paper_id')
    fit = pd.read_csv(SUB / 'fit_sanity.csv')
    curves, diffs, Rall = [], [], {}
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]
        R, dm = ratios(s); Rall[part] = R
        for (arm, v, l), (e, b) in R.items():
            lo, hi = ci(b); curves.append(dict(split=part, arm=arm, S=v, layer=l, n=len(s), clean_minus_corrupt=dm, value=e, lo=lo, hi=hi))
        for arm in ('carry', 'remove'):
            for l in LAYERS:
                g = lambda v: R[arm, v, l]
                for nm, (e, b) in {'id - rand': (g('id')[0] - g('rand')[0], g('id')[1] - g('rand')[1]),
                                   'auth - rand': (g('auth')[0] - g('rand')[0], g('auth')[1] - g('rand')[1]),
                                   'full - rand': (g('full')[0] - g('rand')[0], g('full')[1] - g('rand')[1]),
                                   'auth - id': (g('auth')[0] - g('id')[0], g('auth')[1] - g('id')[1]),
                                   'id - 0.5 full': (g('id')[0] - 0.5 * g('full')[0], g('id')[1] - 0.5 * g('full')[1]),
                                   'rand61 - rand62': (g('rand61')[0] - g('rand62')[0], g('rand61')[1] - g('rand62')[1]),
                                   'rand61 - rand63': (g('rand61')[0] - g('rand63')[0], g('rand61')[1] - g('rand63')[1]),
                                   'rand62 - rand63': (g('rand62')[0] - g('rand63')[0], g('rand62')[1] - g('rand63')[1])}.items():
                    lo, hi = ci(b); diffs.append(dict(split=part, arm=arm, layer=l, contrast=nm, value=e, lo=lo, hi=hi))
    Cv = pd.DataFrame(curves); D = pd.DataFrame(diffs)
    Cv.to_csv(SUB / 'x2_curves.csv', index=False); D.to_csv(SUB / 'x2_diffs.csv', index=False)
    dd = lambda part, arm, l, c: D[(D.split == part) & (D.arm == arm) & (D.layer == l) & (D.contrast == c)].iloc[0]
    cv = lambda part, arm, l, v: Cv[(Cv.split == part) & (Cv.arm == arm) & (Cv.layer == l) & (Cv.S == v)].iloc[0]

    # ---------------------------------------------------------------- verdict (carry arm decides; remove = converging)
    sel = {S: max(LAYERS, key=lambda l: dd('tune', 'carry', l, f'{S} - rand').value) for S in ('id', 'auth')}
    V = {}
    for S in ('id', 'auth'):
        l = sel[S]; x = dd('test', 'carry', l, f'{S} - rand'); xr = dd('test', 'remove', l, f'{S} - rand')
        V[S] = dict(layer=l, tune_diff=dd('tune', 'carry', l, f'{S} - rand').value, test_diff=x.value, test_lo=x.lo, test_hi=x.hi, carries=bool(x.lo > 0),
                    R_S=cv('test', 'carry', l, S).value, R_rand=cv('test', 'carry', l, 'rand').value, R_full=cv('test', 'carry', l, 'full').value,
                    remove_diff=xr.value, remove_lo=xr.lo, remove_hi=xr.hi, L_S=cv('test', 'remove', l, S).value, L_rand=cv('test', 'remove', l, 'rand').value)
    h2 = V['id']['carries'] and V['id']['R_S'] >= 0.5 * V['id']['R_full']
    ai = dd('test', 'carry', sel['auth'], 'auth - id'); air = dd('test', 'remove', sel['auth'], 'auth - id')
    h3 = V['auth']['carries'] and ai.lo > 0
    anywhere = D[(D.arm == 'carry') & D.split.isin(['tune', 'test']) & D.contrast.isin(['id - rand', 'auth - rand']) & (D.lo > 0)]
    neither = anywhere.empty
    if h2 and h3: verdict = 'H2 and H3 both supported'
    elif h2: verdict = 'H2 supported (S_id carries the paper information, >= half of the full replacement)'
    elif h3: verdict = 'H3 supported (S_auth carries more than S_id)'
    elif neither: verdict = 'neither: S_id and S_auth never exceed S_rand (the carried information is not in these 10-dim subspaces)'
    else:
        parts = []
        for S in ('id', 'auth'):
            if V[S]['carries']: parts.append(f'S_{S} carries at L{V[S]["layer"]} but ' + ('R_id < 0.5 x R_full' if S == 'id' else 'R_auth - R_id interval includes 0'))
        ex = sorted({f'{r.split} L{r.layer} {r.contrast}' for r in anywhere.itertuples()})
        verdict = 'no pre-registered support for H2 or H3' + ('; ' + '; '.join(parts) if parts else '') + f'; intervals above 0 only at: {", ".join(ex)}'
    vrow = dict(verdict=verdict, H2=h2, H3=h3, neither=neither, layer_id=sel['id'], layer_auth=sel['auth'],
                **{f'id_{k}': v for k, v in V['id'].items()}, **{f'auth_{k}': v for k, v in V['auth'].items()},
                auth_minus_id=ai.value, auth_minus_id_lo=ai.lo, auth_minus_id_hi=ai.hi,
                remove_auth_minus_id=air.value, remove_auth_minus_id_lo=air.lo, remove_auth_minus_id_hi=air.hi)
    pd.DataFrame([vrow]).to_csv(SUB / 'x2_verdict.csv', index=False)

    # ---------------------------------------------------------------- checks (WARN only)
    chk = []
    if X1RAW.exists() and any(X1RAW.glob('shard_*.npz')):
        x1, _ = load_dir(X1RAW); m = df.merge(x1, on='paper_id', suffixes=('', '_x1'))
        for l in LAYERS:
            if f'authors@{l}' not in m: continue
            r2 = (m[f'carry_full@{l}'] - m.corrupt).mean() / (m.clean - m.corrupt).mean()
            r1 = (m[f'authors@{l}'] - m.corrupt_x1).mean() / (m.clean_x1 - m.corrupt_x1).mean()
            pp = (m[f'carry_full@{l}'] - m[f'authors@{l}']).abs()
            chk.append(dict(check=f'S_full vs X1 authors@L{l}', value=r2 - r1, threshold=0.05, ok=abs(r2 - r1) <= 0.05,
                            detail=f'R_full {r2:.4f} vs X1 R_authors {r1:.4f} on {len(m)} common pairs; per pair |score diff| max {pp.max():.4f}, exact share {(pp < 1e-12).mean():.3f}; clean |diff| max {(m.clean - m.clean_x1).abs().max():.4f}, corrupt |diff| max {(m.corrupt - m.corrupt_x1).abs().max():.4f}'))
    else:
        chk.append(dict(check='S_full vs X1', value=np.nan, threshold=0.05, ok=False, detail=f'no X1 data at {X1RAW}'))
    for arm, ref in (('carry', 'corrupt'), ('remove', 'clean')):
        dv = np.concatenate([(df[f'{arm}_zero@{l}'] - df[ref]).abs().to_numpy() for l in LAYERS])
        rz = [cv('all', arm, l, 'zero').value for l in LAYERS]
        chk.append(dict(check=f'identity patch S=0 ({arm} == {ref})', value=float(dv.max()), threshold=0.0, ok=bool(dv.max() == 0),
                        detail=f'max |diff| {dv.max():.4f}, mean {dv.mean():.5f}, exact share {(dv == 0).mean():.3f}; ratio with S=0 per layer ' + ', '.join(f'{x:+.4f}' for x in rz)))
    rr = D[D.contrast.str.startswith('rand6') & (D.split == 'all')]; bad = rr[(rr.lo > 0) | (rr.hi < 0)]
    chk.append(dict(check='3 random subspaces agree (all pairs, both arms, all layers)', value=float(rr.value.abs().max()), threshold=np.nan, ok=bad.empty,
                    detail='all pairwise difference intervals include 0' if bad.empty else 'interval excludes 0 at: ' + ', '.join(f'{r.arm} L{r.layer} {r.contrast} {fm(r.value, r.lo, r.hi)}' for r in bad.itertuples())))
    K = pd.DataFrame(chk); K.to_csv(SUB / 'x2_checks.csv', index=False)

    capc = [c for c in df.columns if c.startswith('cap_')]
    cap = pd.DataFrame([dict(S=c.split('@')[0][4:], layer=int(c.split('@')[1]), mean_share=df[c].mean(), median_share=df[c].median()) for c in capc])
    cap.to_csv(SUB / 'x2_capture.csv', index=False)

    # ---------------------------------------------------------------- report
    nt, nu = int((df.split == 'test').sum()), int((df.split == 'tune').sum())
    L = ['# Stage 13 X2: subspace patching (addendum 6)' + ('  **TINY TEST (random 2-layer model)**' if TINY else ''), '',
         f'Shards {nsh}; pairs: test {nt}, tune {nu} (equal title token length, as X1). Score = A\'s first-author teacher-forced score (mean log10(1/rank) of the name tokens); '
         'this is the model\'s internal preference for the correct first-author tokens under teacher forcing, not generation (addendum 4).',
         'carry: R_S = mean(patched - corrupt) / mean(clean - corrupt), B\'s prompt with h_B + P_S(h_A - h_B) at every title position. '
         'remove: L_S = mean(clean - removed) / mean(clean - corrupt), A\'s prompt with h_A - P_S(h_A - mu). 95% team-cluster bootstrap (2,000 draws). '
         'S_rand = average of 3 random 10-dim subspaces (seeds 61-63). S_full = identity map (carry = X1 full replacement; remove = mu at every title position).', '',
         '## Verdict (carry arm, layer chosen on tune, confirmed on test)', '',
         '| subspace | layer (tune) | tune R_S - R_rand | test R_S - R_rand | test R_S | test R_rand | test R_full | carries? | remove arm test L_S - L_rand |', '|---|---|---|---|---|---|---|---|---|']
    for S in ('id', 'auth'):
        v = V[S]
        L.append(f'| S_{S} | L{v["layer"]} | {v["tune_diff"]:+.3f} | {fm(v["test_diff"], v["test_lo"], v["test_hi"])} | {v["R_S"]:+.3f} | {v["R_rand"]:+.3f} | {v["R_full"]:+.3f} | {"yes" if v["carries"] else "no"} | {fm(v["remove_diff"], v["remove_lo"], v["remove_hi"])} |')
    L += ['', f'- H2 (S_id carries AND R_id >= 0.5 x R_full at L{sel["id"]}): **{"supported" if h2 else "not supported"}** (R_id {V["id"]["R_S"]:+.3f} vs 0.5 x R_full {0.5 * V["id"]["R_full"]:+.3f}).',
          f'- H3 (S_auth carries AND R_auth - R_id > 0 at L{sel["auth"]}): **{"supported" if h3 else "not supported"}** (R_auth - R_id on test {fm(ai.value, ai.lo, ai.hi)}; remove arm {fm(air.value, air.lo, air.hi)}).',
          f'- Neither (no tune/test layer with R_id - R_rand or R_auth - R_rand above 0): **{"yes" if neither else "no"}**.', '', f'**Verdict: {verdict}**', '']
    for arm, lab in (('carry', 'carry arm: R_S (share of the clean - corrupt gap moved into B by patching A\'s S-component)'),
                     ('remove', 'remove arm: L_S (share of the clean - corrupt gap lost when A\'s S-component is set to the training mean)')):
        L += [f'## {lab}', '']
        for part in ('test', 'tune', 'all'):
            L += [f'### {part}' + (' (confirmatory)' if part == 'test' else '') + f' - clean - corrupt {Cv[Cv.split == part].clean_minus_corrupt.iloc[0]:.3f}, n {int(Cv[Cv.split == part].n.iloc[0])}', '',
                  '| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |', '|---|---|---|---|---|---|---|---|---|---|']
            for l in LAYERS:
                L.append(f'| L{l} | ' + ' | '.join(fm(cv(part, arm, l, S).value, cv(part, arm, l, S).lo, cv(part, arm, l, S).hi) for S in SNAMES) + ' | '
                         + ' | '.join(fm(dd(part, arm, l, c).value, dd(part, arm, l, c).lo, dd(part, arm, l, c).hi) for c in ('id - rand', 'auth - rand', 'auth - id', 'id - 0.5 full')) + ' |')
            L.append('')
        L += [f'Single random subspaces ({arm}, all pairs): ' + '; '.join(f'L{l} ' + ', '.join(f'{r} {cv("all", arm, l, r).value:+.3f}' for r in RS) for l in LAYERS), '']
    L += ['## Share of ||h_A - h_B||^2 at the title positions inside each subspace (mean over pairs)', '', '| layer | ' + ' | '.join(['id', 'auth', 'rand61', 'rand62', 'rand63']) + ' |', '|---|---|---|---|---|---|']
    for l in LAYERS:
        L.append(f'| L{l} | ' + ' | '.join(f'{cap[(cap.S == s) & (cap.layer == l)].mean_share.iloc[0]:.4f}' for s in ['id', 'auth', 'rand61', 'rand62', 'rand63']) + ' |')
    L += ['', '## Subspace fits (training papers outside all pair teams; held-out 5-fold team CV)', '',
          '| layer | n train | rank S_id | alpha year / logcit / field / auth | year R² | log cit R² | field acc | author-map R² | author top-1 (majority) | max cos(S_id, S_auth) |', '|---|---|---|---|---|---|---|---|---|---|']
    for r in fit.itertuples():
        L.append(f'| L{r.layer} | {r.n_train} | {r.rank_id} | {r.alpha_year:g} / {r.alpha_logcit:g} / {r.alpha_field:g} / {r.alpha_auth:g} | {r.year_r2:.3f} | {r.logcit_r2:.3f} | {r.field_acc:.3f} | {r.auth_r2:.4f} | {r.auth_top1:.3f} ({r.auth_top1_majority:.3f}) | {r.id_auth_cos_max:.3f} |')
    L += ['', '## Checks (WARN only)', '']
    for r in K.itertuples(): L.append(f'- {"OK" if r.ok else "WARN"} {r.check}: {r.detail}')
    L += ['', '## Deviations from addendum 6', '',
          '- S_id has 9 dimensions, not 10: with one shared ridge alpha the 8 one-vs-rest field weight vectors sum to exactly 0 (centred one-hot rows sum to 0), so year + log citations + 8 field vectors span 9 dimensions; the dependent QR direction is dropped. S_auth, S_rand stay 10-dim (the comparison with S_rand is therefore slightly conservative for S_id).',
          '- Ridge convention of the Stage 13 probes (features standardised on the training rows, alpha x trace/d, intercept); the fitted readout vectors are mapped back to raw residual coordinates (w / sd) before orthonormalisation. Alpha per target family (year, log citations, field, author map) by pooled held-out normalised MSE over the 5 team folds.',
          '- Training teams = the archived 9,108-paper team ids (summary_cpu_teamci/folds_own9108_k5s13.npz); CV folds = the archived team folds restricted to the training papers.',
          '- "Layer selected on tune" = the layer with the largest R_S - R_rand on tune (as the X1 layer choice of prereg.json). "Neither ... anywhere" is checked on tune and test, carry arm.',
          '- S_full in the remove arm (every title position set to mu) is reported as a reference; addendum 6 only defines S_full for carry.', '']
    rz = V['id']; ra = V['auth']; fr = cv('test', 'carry', sel['id'], 'full').value
    L += ['## Plain summary', '',
          f'1. Replacing B\'s whole title states with A\'s (S_full) moves {fr:.2f} of the clean - corrupt gap at L{sel["id"]} on test; this is the X1 ceiling.',
          f'2. Moving only A\'s 10-dim paper-attribute component (S_id: year, citations, field) moves {rz["R_S"]:+.2f} of the gap at L{rz["layer"]} vs {rz["R_rand"]:+.2f} for random 10-dim subspaces (difference {fm(rz["test_diff"], rz["test_lo"], rz["test_hi"])}).',
          f'3. Moving A\'s 10-dim author component (S_auth: the directions that predict the first-author token\'s unembedding) moves {ra["R_S"]:+.2f} at L{ra["layer"]} vs {ra["R_rand"]:+.2f} random (difference {fm(ra["test_diff"], ra["test_lo"], ra["test_hi"])}).',
          f'4. Removing the components from A\'s own prompt (remove arm) costs S_id {rz["L_S"]:+.2f} and S_auth {ra["L_S"]:+.2f} of the gap at those layers (random {rz["L_rand"]:+.2f} / {ra["L_rand"]:+.2f}).',
          f'5. Pre-registered verdict: {verdict}.', '']
    (REP / 'x2_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('X2 ANALYZED')


if __name__ == '__main__':
    main()
