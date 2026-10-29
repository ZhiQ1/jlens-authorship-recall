"""Stage 13 X1 (cross-task title patching) and X4 (patchscope decodability) analysis (CPU).
Rules: config/prereg.json (X1, X4), addendum 1 (team tune/test split), addendum 2 (X1 replaced rule; team-cluster
intervals). Intervals: 95% bootstrap over author teams (pairs.parquet `team`), 2,000 draws.

X1  R(src,l) = mean(src@l - corrupt) / mean(clean - corrupt), src in authors / year / field (A's own states from a prompt
    asking for that task) and random_c (C's states). Full curves R(authors) - R(year), R(authors) - R(field),
    R(authors) - R(random_c) at every layer, on test (confirmatory), tune and all. Layers <= L16 are a text-replacement
    control only. Per layer >= 24 on test: 'task-independent' if both differences lie inside [-0.1, 0.1] and
    R(authors) - R(random_c) > 0; 'task-specific' if R(authors) - R(year) > 0.1 (interval excludes 0.1); else 'undecided'.
    Null check: any |R(random_c,l)| > 0.1 is flagged.
X4  D(answer,pos,l) = mean(self) - mean(partner) of the answer score (patchscope: the source state at the X placeholder).
    Earliest layer with D's interval above 0, found on tune, confirmed on test (D at that layer on test, interval > 0).
    Order: earliest(year), earliest(field) <= earliest(author). Recognition: target - control of the per-paper
    self - partner within citation bin (Stage 10 estimator), team bootstrap.
Outputs: summary_x1x4/*.csv, reports/x1_report.md, reports/x4_report.md"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; ROOT = B / '381_stage13'
OUT = ROOT / 'summary_x1x4'; NB = 2000
XL = [4, 8, 16, 24, 32, 40, 48]; PL = [8, 16, 24, 32, 40, 48, 56]


def load_dir(d):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
    keys = [k for k in zs[0].files if k != 'meta']
    return pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in keys}), len(zs)


def team_w(teams, seed):
    codes, uniq = pd.factorize(pd.Series(teams))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]   # [NB, n]


def ci(b): return np.percentile(b, [2.5, 97.5])
def fm(e, lo, hi): return f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def x1(pairs, L):
    df, n = load_dir(ROOT / 'raw/xpatch'); df = df.merge(pairs[['paper_id', 'team']], on='paper_id')
    rows = []
    for part in ('test', 'tune', 'all'):
        s = df if part == 'all' else df[df.split == part]; W = team_w(s.team, 101); den = (s.clean - s.corrupt).to_numpy(); dw = W @ den
        R = {}
        for src in ('authors', 'year', 'field', 'random_c'):
            for l in XL:
                num = (s[f'{src}@{l}'] - s.corrupt).to_numpy(); R[src, l] = (num.mean() / den.mean(), (W @ num) / dw)
        for l in XL:
            r = dict(split=part, layer=l, n=len(s), clean_minus_corrupt=den.mean())
            for src in ('authors', 'year', 'field', 'random_c'):
                r[f'R_{src}'] = R[src, l][0]; r[f'R_{src}_lo'], r[f'R_{src}_hi'] = ci(R[src, l][1])
            for o in ('year', 'field', 'random_c'):
                b = R['authors', l][1] - R[o, l][1]; r[f'a_minus_{o}'] = R['authors', l][0] - R[o, l][0]; r[f'a_minus_{o}_lo'], r[f'a_minus_{o}_hi'] = ci(b)
            if l >= 24:
                ti = all(-0.1 <= r[f'a_minus_{o}_lo'] and r[f'a_minus_{o}_hi'] <= 0.1 for o in ('year', 'field')) and r['a_minus_random_c_lo'] > 0
                ts = r['a_minus_year_lo'] > 0.1
                r['verdict'] = 'task-independent' if ti else ('task-specific' if ts else 'undecided')
            else:
                r['verdict'] = 'text-replacement control (no conclusion)'
            r['null_flag'] = abs(r['R_random_c']) > 0.1
            rows.append(r)
    D = pd.DataFrame(rows); D.to_csv(OUT / 'x1_recovery.csv', index=False)
    L += ['# Stage 13 X1: patch A\'s title states from a prompt asking a different question', '',
          f'Shards {n}; papers: test {int((df.split == "test").sum())}, tune {int((df.split == "tune").sum())}. R = mean(patched - corrupt) / mean(clean - corrupt) of A\'s first-author score. 95% team-cluster bootstrap.',
          'Rule (addendum 2): full curves; L4-L16 are a text-replacement control only; at L24+ (test): task-independent if R(authors) - R(year) and R(authors) - R(field) both lie inside [-0.1, 0.1] and R(authors) - R(random_c) > 0; task-specific if R(authors) - R(year) > 0.1.', '']
    for part in ('test', 'tune', 'all'):
        x = D[D.split == part]
        L += [f'## {part}' + (' (confirmatory)' if part == 'test' else ''), '', f'clean - corrupt: {x.clean_minus_corrupt.iloc[0]:.3f}', '',
              '| layer | R authors | R year | R field | R random C | authors - year | authors - field | authors - random C | verdict |', '|---|---|---|---|---|---|---|---|---|']
        for r in x.to_dict('records'):
            L.append(f'| L{r["layer"]} | ' + ' | '.join(fm(r[f'R_{s}'], r[f'R_{s}_lo'], r[f'R_{s}_hi']) for s in ('authors', 'year', 'field', 'random_c'))
                     + ' | ' + ' | '.join(fm(r[f'a_minus_{o}'], r[f'a_minus_{o}_lo'], r[f'a_minus_{o}_hi']) for o in ('year', 'field', 'random_c')) + f' | {r["verdict"]}{" · NULL FLAG" if r["null_flag"] else ""} |')
        L.append('')
    flags = D[D.null_flag]
    L += ['Null check: ' + ('none of the random-C recoveries exceeds 0.1.' if flags.empty else 'FLAG: |R(random_c)| > 0.1 at ' + ', '.join(f'{r.split} L{r.layer} ({r.R_random_c:+.3f})' for r in flags.itertuples()) + '; recoveries above are to be read relative to it.'), '']
    return D


def strat_diff_team(df, col, teams, seed, min_n=10):
    df = df.reset_index(drop=True); cells = []
    for _, ss in df.groupby('citation_bin'):
        ia, ib = ss.index[ss.group == 'target'].to_numpy(), ss.index[ss.group == 'control'].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan, 0
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum(); x = df[col].to_numpy(float); W = team_w(teams, seed)
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (a, b) in zip(w, cells):
        bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
    return est, *ci(bt), len(cells)


def x4(pairs, cbin, L):
    df, n = load_dir(ROOT / 'raw/pscope'); df = df.merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id').merge(cbin, on='paper_id', how='left')
    rows = []
    for part in ('tune', 'test', 'all'):
        s = df if part == 'all' else df[df.split == part]; W = team_w(s.team, 202)
        for a in ('year', 'author', 'field'):
            for pos in ('title', 'colon'):
                for l in PL:
                    v = (s[f'{a}@self@{pos}@{l}'] - s[f'{a}@partner@{pos}@{l}']).to_numpy(); b = (W @ v) / W.sum(1)
                    rows.append(dict(split=part, answer=a, pos=pos, layer=l, n=len(s), D=v.mean(), lo=ci(b)[0], hi=ci(b)[1],
                                     self=s[f'{a}@self@{pos}@{l}'].mean(), partner=s[f'{a}@partner@{pos}@{l}'].mean(), none=s[f'{a}@none'].mean()))
    D = pd.DataFrame(rows); D.to_csv(OUT / 'x4_decodability.csv', index=False)
    early = []
    for a in ('year', 'author', 'field'):
        for pos in ('title', 'colon'):
            t = D[(D.split == 'tune') & (D.answer == a) & (D.pos == pos) & (D.lo > 0)]
            l0 = int(t.layer.min()) if len(t) else None
            te = D[(D.split == 'test') & (D.answer == a) & (D.pos == pos) & (D.layer == l0)] if l0 else None
            conf = bool(l0 and te.lo.iloc[0] > 0)
            early.append(dict(answer=a, pos=pos, earliest_tune=l0, confirmed_on_test=conf, D_test=float(te.D.iloc[0]) if l0 else np.nan,
                              lo_test=float(te.lo.iloc[0]) if l0 else np.nan, hi_test=float(te.hi.iloc[0]) if l0 else np.nan))
    E = pd.DataFrame(early); E.to_csv(OUT / 'x4_earliest.csv', index=False)
    rec = []
    for a in ('year', 'author'):
        for pos in ('title', 'colon'):
            for l in PL:
                s = df.assign(v=df[f'{a}@self@{pos}@{l}'] - df[f'{a}@partner@{pos}@{l}'])
                e, lo, hi, nc = strat_diff_team(s[['v', 'group', 'citation_bin']], 'v', s.team.to_numpy(), 303 + l)
                rec.append(dict(answer=a, pos=pos, layer=l, target_minus_control=e, lo=lo, hi=hi, n_bins=nc))
    Rc = pd.DataFrame(rec); Rc.to_csv(OUT / 'x4_recognition.csv', index=False)
    L += ['# Stage 13 X4: decode year / first author / field from the paper\'s own state (patchscope)', '',
          f'Shards {n}; papers: tune {int((df.split == "tune").sum())}, test {int((df.split == "test").sum())}. D = mean score(self source) - mean score(partner source) (log10(1/rank) of the answer); the year never appears in the source prompt. 95% team-cluster bootstrap.', '',
          '## Earliest layer with D > 0 (chosen on tune, confirmed on test)', '', '| answer | position | earliest (tune) | D on test at that layer | confirmed |', '|---|---|---|---|---|']
    for r in E.to_dict('records'):
        has = pd.notna(r['earliest_tune'])
        L.append(f'| {r["answer"]} | {r["pos"]} | ' + (f'L{int(r["earliest_tune"])} | {fm(r["D_test"], r["lo_test"], r["hi_test"])} | {"yes" if r["confirmed_on_test"] else "no"}' if has else 'none on tune | - | -') + ' |')
    L.append('')
    for pos in ('title', 'colon'):
        g = E[E.pos == pos].set_index('answer').earliest_tune
        ok = all(g[x] is not None and not pd.isna(g[x]) for x in ('year', 'field', 'author'))
        L.append(f'- Order at {pos}: ' + (f'year L{int(g["year"])}, field L{int(g["field"])}, author L{int(g["author"])} -> H2 order (year and field no later than author) ' + ('**HOLDS**' if ok and g['year'] <= g['author'] and g['field'] <= g['author'] else '**DOES NOT HOLD**') if ok else 'not all three decodable on tune -> order undetermined'))
    L += ['', '## D at every layer (test, confirmatory)', '']
    for pos in ('title', 'colon'):
        L += [f'### {pos}', '', '| layer | year | first author | field |', '|---|---|---|---|']
        for l in PL:
            f = lambda a: D[(D.split == 'test') & (D.answer == a) & (D.pos == pos) & (D.layer == l)].iloc[0]
            L.append(f'| L{l} | ' + ' | '.join(fm(f(a).D, f(a).lo, f(a).hi) for a in ('year', 'author', 'field')) + ' |')
        L.append('')
    L += ['## Recognition: target - control of (self - partner) within citation bin (all papers)', '', '| layer | year, title | year, colon | author, title | author, colon |', '|---|---|---|---|---|']
    for l in PL:
        f = lambda a, p: Rc[(Rc.answer == a) & (Rc.pos == p) & (Rc.layer == l)].iloc[0]
        L.append(f'| L{l} | ' + ' | '.join(fm(f(a, p).target_minus_control, f(a, p).lo, f(a, p).hi) for a in ('year', 'author') for p in ('title', 'colon')) + ' |')
    L.append('')
    return D


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    cb = [c for c in ('citation_bin', 'cit_bin') if c in papers.columns]
    cbin = papers[['paper_id', cb[0]]].rename(columns={cb[0]: 'citation_bin'}) if cb else pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'citation_bin']]
    for name, fn, args in (('x1', x1, (pairs,)), ('x4', x4, (pairs, cbin))):
        L = []
        try:
            fn(*args, L); (ROOT / f'reports/{name}_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print(f'{name.upper()} ANALYZED', flush=True)
        except Exception:
            import traceback; traceback.print_exc(); print(f'{name.upper()} FAILED', flush=True)


if __name__ == '__main__':
    main()
