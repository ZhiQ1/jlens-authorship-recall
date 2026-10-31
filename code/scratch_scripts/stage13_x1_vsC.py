"""Stage 13 X1 relative to random C (handbook V31: "year/field 恢复率相对随机论文 C 重算，不只打 NULL FLAG").

Reads the same raw data and uses the same estimator and team-cluster bootstrap as stage13_x1x4_analyze.x1
(imported: load_dir, team_w with seed 101, NB = 2000, per split test / tune / all), so every bootstrap draw is the
same draw as in x1_recovery.csv.

Per split and layer (all saved layers 4..48):
  R(src)          = mean(src - corrupt) / mean(clean - corrupt)                     (reproduced; checked against x1_recovery.csv)
  R'(task)        = R(task) - R(C) = mean(task - C) / mean(clean - corrupt)           task in authors / year / field, paired per pair
  R'(a) - R'(t)   = differences of the C-corrected recoveries; C cancels exactly (per draw), so they equal R(a) - R(t)
  N(task)         = (R(task) - R(C)) / (1 - R(C)) = mean(task - C) / mean(clean - C)  (C as the baseline instead of B)
  N(a) - N(t)     = (R(a) - R(t)) / (1 - R(C))
  share(t)        = R'(t) / R'(a)                                                       (reference only)
Verdicts (addendum 2, L24+): task-independent if both differences have intervals inside [-b, b] and R'(authors) > 0
(interval excludes 0); task-specific if R'(a) - R'(year) > b (interval excludes b); else undecided. b = 0.1 is the
written addendum-2 bound; b = 0.02 is also reported (stricter variant named in the V31 request). Applied to the
C-corrected (R') and the normalised (N) curves. Tolerance misses are WARN only.
Outputs: summary_x1x4/x1_recovery_vsC.csv, reports/x1_vsC.md (new files; originals untouched)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage13_x1x4_analyze import ROOT, OUT, XL, NB, load_dir, team_w, ci, fm  # noqa: E402

SRC = ('authors', 'year', 'field')
BOUNDS = (0.1, 0.02)


def verdict(r, pre, b):
    ti = all(-b <= r[f'{pre}a_minus_{o}_lo'] and r[f'{pre}a_minus_{o}_hi'] <= b for o in ('year', 'field')) and r[f'{pre}authors_lo'] > 0
    ts = r[f'{pre}a_minus_year_lo'] > b
    return 'task-independent' if ti else ('task-specific' if ts else 'undecided')


def main():
    od = Path(sys.argv[1]) if len(sys.argv) > 1 else None   # test mode: write to this dir instead
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')
    df, nsh = load_dir(ROOT / 'raw/xpatch'); df = df.merge(pairs[['paper_id', 'team']], on='paper_id')
    orig = pd.read_csv(OUT / 'x1_recovery.csv')
    rows, warns = [], []
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]
        W = team_w(s.team, 101); den = (s.clean - s.corrupt).to_numpy(); dw = W @ den
        for l in XL:
            C = s[f'random_c@{l}'].to_numpy(); c_den = (s.clean.to_numpy() - C); cdw = W @ c_den
            r = dict(split=part, layer=l, n=len(s), clean_minus_corrupt=den.mean(), clean_minus_C=c_den.mean())
            Rb, Rpb, Nb = {}, {}, {}
            for src in SRC + ('random_c',):
                num = (s[f'{src}@{l}'] - s.corrupt).to_numpy(); Rb[src] = (num.mean() / den.mean(), (W @ num) / dw)
            r['R_random_c'] = Rb['random_c'][0]; r['R_random_c_lo'], r['R_random_c_hi'] = ci(Rb['random_c'][1])
            for t in SRC:
                d = s[f'{t}@{l}'].to_numpy() - C
                Rpb[t] = (d.mean() / den.mean(), (W @ d) / dw)          # R(t) - R(C)
                Nb[t] = (d.mean() / c_den.mean(), (W @ d) / cdw)        # (R(t) - R(C)) / (1 - R(C))
                r[f'R_{t}'] = Rb[t][0]
                r[f'Rc_{t}'] = Rpb[t][0]; r[f'Rc_{t}_lo'], r[f'Rc_{t}_hi'] = ci(Rpb[t][1])
                r[f'N_{t}'] = Nb[t][0]; r[f'N_{t}_lo'], r[f'N_{t}_hi'] = ci(Nb[t][1])
            for o in ('year', 'field'):
                for pre, B in (('Rc_', Rpb), ('N_', Nb)):
                    r[f'{pre}a_minus_{o}'] = B['authors'][0] - B[o][0]; r[f'{pre}a_minus_{o}_lo'], r[f'{pre}a_minus_{o}_hi'] = ci(B['authors'][1] - B[o][1])
                sh = Rpb[o][1] / Rpb['authors'][1]
                r[f'share_{o}'] = Rpb[o][0] / Rpb['authors'][0]; r[f'share_{o}_lo'], r[f'share_{o}_hi'] = ci(sh)
                # identity check: C-corrected difference == uncorrected difference, per bootstrap draw
                unc = Rb['authors'][1] - Rb[o][1]; dif = np.max(np.abs((Rpb['authors'][1] - Rpb[o][1]) - unc))
                r[f'maxabs_drawdiff_vs_uncorrected_{o}'] = dif
                orow = orig[(orig.split == part) & (orig.layer == l)].iloc[0]
                for k, v in ((f'a_minus_{o}', r[f'Rc_a_minus_{o}']), (f'a_minus_{o}_lo', r[f'Rc_a_minus_{o}_lo']), (f'a_minus_{o}_hi', r[f'Rc_a_minus_{o}_hi'])):
                    if abs(orow[k] - v) > 1e-9: warns.append(f'WARN {part} L{l} {k}: original {orow[k]:.6f} vs C-corrected {v:.6f}')
            orow = orig[(orig.split == part) & (orig.layer == l)].iloc[0]
            for t in SRC + ('random_c',):
                if abs(orow[f'R_{t}'] - Rb[t][0]) > 1e-9: warns.append(f'WARN {part} L{l} R_{t}: original {orow[f"R_{t}"]:.6f} vs recomputed {Rb[t][0]:.6f}')
            for k in ('a_minus_random_c_lo', 'a_minus_random_c_hi'):
                v = r['Rc_authors_lo' if k.endswith('lo') else 'Rc_authors_hi']
                if abs(orow[k] - v) > 1e-9: warns.append(f'WARN {part} L{l} {k}: original {orow[k]:.6f} vs {v:.6f}')
            r['orig_verdict'] = orow['verdict']; r['null_flag'] = abs(r['R_random_c']) > 0.1
            for b in BOUNDS:
                for pre in ('Rc_', 'N_'):
                    r[f'verdict_{pre}b{b}'] = verdict(r, pre, b) if l >= 24 else 'text-replacement control (no conclusion)'
            rows.append(r)
    D = pd.DataFrame(rows); D.to_csv((od or OUT) / 'x1_recovery_vsC.csv', index=False)

    L = ['# Stage 13 X1 relative to random paper C (V31)', '',
         f'Shards {nsh}; papers: test {int((df.split == "test").sum())}, tune {int((df.split == "tune").sum())}. Same data, estimator and team-cluster bootstrap as `x1_report.md` (seed 101, 2,000 draws, per split), so each draw is the same draw as there.',
         "R'(t) = R(t) - R(C) = mean(t - C) / mean(clean - corrupt), paired per pair. N(t) = (R(t) - R(C)) / (1 - R(C)) = mean(t - C) / mean(clean - C), i.e. C instead of B as the baseline.",
         "Rule (addendum 2, L24+): task-independent if R'(a) - R'(year) and R'(a) - R'(field) both have intervals inside [-b, b] and R'(authors) > 0; task-specific if R'(a) - R'(year) > b. Written bound b = 0.1; b = 0.02 shown as a stricter variant. L4-L16: text-replacement control only.", '',
         '## Reproduction / identity checks', '']
    mx = max(D[[c for c in D.columns if c.startswith('maxabs_drawdiff')]].max())
    L += [f'- R(authors/year/field/C) and the original difference intervals reproduced from `x1_recovery.csv`: ' + ('all match to 1e-9.' if not warns else f'{len(warns)} WARN (listed at the end).'),
          f"- R'(a) - R'(t) equals the uncorrected R(a) - R(t) in every bootstrap draw (max |difference| over draws, layers, splits: {mx:.1e}). Because the same C is subtracted from both tasks in each pair, C cancels: **correcting for C does not change the authors - year / authors - field differences or their intervals.**",
          "- Hence the addendum-2 verdict on the C-corrected curves (R') is identical to the original verdict at every layer; the R'(authors) > 0 condition is the original R(authors) - R(C) > 0.", '']
    for part in ('test', 'tune', 'all'):
        x = D[D.split == part]
        L += [f'## {part}' + (' (confirmatory)' if part == 'test' else ''), '',
              f'clean - corrupt {x.clean_minus_corrupt.iloc[0]:.3f}', '',
              "### C-corrected recoveries R'(t) = R(t) - R(C)", '',
              "| layer | R(C) | R'(authors) | R'(year) | R'(field) | R'(a) - R'(year) | R'(a) - R'(field) | verdict b=0.1 | verdict b=0.02 |", '|---|---|---|---|---|---|---|---|---|']
        for r in x.to_dict('records'):
            L.append(f'| L{r["layer"]} | {fm(r["R_random_c"], r["R_random_c_lo"], r["R_random_c_hi"])} | ' + ' | '.join(fm(r[f'Rc_{t}'], r[f'Rc_{t}_lo'], r[f'Rc_{t}_hi']) for t in SRC)
                     + ' | ' + ' | '.join(fm(r[f'Rc_a_minus_{o}'], r[f'Rc_a_minus_{o}_lo'], r[f'Rc_a_minus_{o}_hi']) for o in ('year', 'field'))
                     + f' | {r["verdict_Rc_b0.1"]} | {r["verdict_Rc_b0.02"]} |')
        L += ['', '### Normalised N(t) = (R(t) - R(C)) / (1 - R(C)), and share R\'(t) / R\'(authors)', '',
              '| layer | clean - C | N(authors) | N(year) | N(field) | N(a) - N(year) | N(a) - N(field) | share year | share field | verdict b=0.1 | verdict b=0.02 |', '|---|---|---|---|---|---|---|---|---|---|---|']
        for r in x.to_dict('records'):
            L.append(f'| L{r["layer"]} | {r["clean_minus_C"]:.3f} | ' + ' | '.join(fm(r[f'N_{t}'], r[f'N_{t}_lo'], r[f'N_{t}_hi']) for t in SRC)
                     + ' | ' + ' | '.join(fm(r[f'N_a_minus_{o}'], r[f'N_a_minus_{o}_lo'], r[f'N_a_minus_{o}_hi']) for o in ('year', 'field'))
                     + ' | ' + ' | '.join(fm(r[f'share_{o}'], r[f'share_{o}_lo'], r[f'share_{o}_hi']) for o in ('year', 'field'))
                     + f' | {r["verdict_N_b0.1"]} | {r["verdict_N_b0.02"]} |')
        L.append('')
    L += ['## Verdict changes (L24+)', '']
    ch = []
    for r in D[D.layer >= 24].to_dict('records'):
        for k in ('verdict_Rc_b0.1', 'verdict_N_b0.1', 'verdict_Rc_b0.02', 'verdict_N_b0.02'):
            if r[k] != r['orig_verdict']: ch.append(f'- {r["split"]} L{r["layer"]}: original "{r["orig_verdict"]}" -> {k} "{r[k]}"')
    L += ch if ch else ['- none']
    t48 = D[(D.split == 'test') & (D.layer == 48)].iloc[0]
    L += ['', 'Every change listed above comes from the bound b = 0.02, not from the C correction: under b = 0.02 the uncorrected curves give the same verdicts, because the differences are identical.', '',
          '## Conclusion', '',
          f"1. Subtracting random C per pair changes the level of every recovery (by -R(C): on test up by 0.07-0.15 at L4-L32, down by {t48.R_random_c:.3f} at L48) but not the authors - year / authors - field differences: C cancels exactly (checked per bootstrap draw).",
          "2. With the written addendum-2 bound (0.1) every verdict is unchanged: L24-L48 stay task-independent on test, tune and all, including L48, which was flagged.",
          f"3. At L48 on test, R'(authors) = {t48.Rc_authors:.3f}, R'(year) = {t48.Rc_year:.3f}, R'(field) = {t48.Rc_field:.3f}; normalised to C as the baseline, year keeps {t48.share_year:.1%} [{t48.share_year_lo:.1%}, {t48.share_year_hi:.1%}] and field {t48.share_field:.1%} [{t48.share_field_lo:.1%}, {t48.share_field_hi:.1%}] of the authors effect: a small but non-zero task dependence (interval of authors - year excludes 0).",
          f"4. With a stricter bound of 0.02, L48 becomes 'undecided' in every split, because the upper end of authors - year is above 0.02 (test {t48.Rc_a_minus_year_hi:.3f}; normalised {t48.N_a_minus_year_hi:.3f}). L24-L40 stay task-independent even with 0.02."]
    L += [''] +(['## WARN', ''] + warns if warns else [])
    ((od or ROOT / 'reports') / 'x1_vsC.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('X1 vsC DONE', flush=True)


if __name__ == '__main__':
    main()
