"""Stage 13 X3 behaviour by name-token role (handbook V51; prereg addendum 4 "token_roles", addendum 5). CPU.

Input: raw/para_tok (stage13_x3_tok_gpu.py: per-token ranks of the first author's name tokens for the 4 title versions,
same rows / prompt / scoring as para_run), summary_x3/x3_pairs.csv (inclusion sets, team, split, group, d_matched),
Stage 10 cohort/name_tokens.parquet (role per row_id).
Estimands per role (tokens of that role averaged within paper first; papers without such tokens drop out):
  behaviour (addendum 4): mean(paraphrase - D)            ("D" = lexical neighbour, score_lexical)
  recovery (stage13_x3_recovery.py, post-hoc there):     (mean P - mean D) / (mean O - mean D); also with partner B.
Gap rule (addendum 4): the recovery is not reported where mean(O - D) < 0.05 for that role (behaviour still shown).
Intervals: 95% team-cluster bootstrap, 2,000 draws, the SAME draws as stage13_x3_recovery.py (stage13_x3_analyze.team_w,
SEED[(split, subset)] over the whole set, then restricted to the papers with the role), so role 'ALL' reproduces
x3_recovery.csv (checked, WARN only). Roles: name_first = initial_first + given_first (first token, predicted at ':'),
surname_first, surname_cont (pre-registered); also initial_first, given_first, given_cont, punct, particle_first.
Usage: stage13_x3_roles.py [--raw DIR --out DIR]   Outputs: summary_x3/x3_roles.csv, reports/x3_roles.md"""
import argparse, importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT = B / '381_stage13'; GAP = 0.05
ROLES = {'ALL': None, 'name_first': ['initial_first', 'given_first'], 'surname_first': ['surname_first'], 'surname_cont': ['surname_cont'],
         'initial_first': ['initial_first'], 'given_first': ['given_first'], 'given_cont': ['given_cont'], 'punct': ['punct'], 'particle_first': ['particle_first']}
PRIMARY = ['name_first', 'surname_first', 'surname_cont']
VERS = {'O': 'rank_original', 'P': 'rank_paraphrase', 'B': 'rank_partner', 'D': 'rank_lexical'}
SETS = {'primary': 'include_primary', 'sensitivity': 'include_sensitive'}
WARN = []


def warn(m): WARN.append(m); print('WARN', m, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
X3 = load(H / '13_stage13/stage13_x3_analyze.py', 'x3a')
def fm(e, lo, hi, d=3): return '-' if pd.isna(e) else f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'


def per_paper(raw):
    fs = sorted(Path(raw).glob('shard_*.npz')); zs = [np.load(f) for f in fs]
    t = pd.DataFrame({k: np.concatenate([z[k] for z in zs]) for k in ['row_id', 'paper_id', 'token_index'] + list(VERS.values())})
    roles = pd.read_parquet(B / '351_stage10/cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'role']).set_index('row_id')
    r = roles.loc[t.row_id.to_numpy()]
    if not (r.paper_id.to_numpy() == t.paper_id.to_numpy()).all() or (r.author_index != r.author_index.min()).any(): warn('row_id -> paper / first author mismatch')
    t['role'] = r.role.to_numpy()
    for k, c in VERS.items(): t[k] = -np.log10(t[c].astype(float))
    out = {}
    for role, rl in ROLES.items():
        s = t if rl is None else t[t.role.isin(rl)]
        out[role] = s.groupby('paper_id')[list(VERS)].mean()
    return out, t, len(fs)


def analyse(pp, df):
    rows = []
    for setn, col in SETS.items():
        for sub in ('all', 'd_matched'):
            m0 = df[col].to_numpy() & df.team.notna().to_numpy()
            if sub == 'd_matched': m0 &= df.d_matched.to_numpy()
            for part in ('tune', 'test', 'all'):
                s = df[m0 if part == 'all' else m0 & (df.split == part).to_numpy()]
                if len(s) < 2: continue
                Wfull = X3.team_w(s.team.to_numpy(), X3.SEED[part, sub])          # the same draws as x3_recovery
                boots = {}
                for role in ROLES:
                    q = pp[role]; have = s.paper_id.isin(q.index).to_numpy()
                    for grp in ('all', 'target', 'control'):
                        g = have & (np.ones(len(s), bool) if grp == 'all' else (s.group == grp).to_numpy())
                        if g.sum() < 2: continue
                        v = q.loc[s.paper_id[g]]; W = Wfull[:, g]; sw = W.sum(1)
                        O, P, Bp, D = (v[k].to_numpy() for k in 'OPBD')
                        with np.errstate(divide='ignore', invalid='ignore'):
                            mo, mp, mb, md = ((W @ x) / sw for x in (O, P, Bp, D))
                        gap = O.mean() - D.mean(); gapB = O.mean() - Bp.mean()
                        r = dict(set=setn, subset=sub, split=part, role=role, group=grp, n=int(g.sum()), n_teams=s.team[g].nunique(),
                                 O=O.mean(), P=P.mean(), B=Bp.mean(), D=D.mean(), P_minus_D=P.mean() - D.mean(), O_minus_D=gap, O_minus_B=gapB,
                                 recovery_D=(P.mean() - D.mean()) / gap if gap >= GAP else np.nan,
                                 recovery_B=(P.mean() - Bp.mean()) / gapB if gapB >= GAP else np.nan, gap_rule_D=bool(gap >= GAP), gap_rule_B=bool(gapB >= GAP))
                        r['PmD_lo'], r['PmD_hi'] = X3.ci(mp - md); r['OmD_lo'], r['OmD_hi'] = X3.ci(mo - md)
                        with np.errstate(divide='ignore', invalid='ignore'):
                            bD = (mp - md) / (mo - md); bB = (mp - mb) / (mo - mb)
                        r['recD_lo'], r['recD_hi'] = X3.ci(bD) if gap >= GAP else (np.nan, np.nan)
                        r['recB_lo'], r['recB_hi'] = X3.ci(bB) if gapB >= GAP else (np.nan, np.nan)
                        r['boot_den_le0_D'] = float((mo - md <= 0).mean())
                        boots[role, grp] = (mp - md, bD); rows.append(r)
                    if (role, 'target') in boots and (role, 'control') in boots:
                        a, b = boots[role, 'target'], boots[role, 'control']
                        t = [x for x in rows if x['set'] == setn and x['subset'] == sub and x['split'] == part and x['role'] == role]
                        tt = {x['group']: x for x in t}
                        rows.append(dict(set=setn, subset=sub, split=part, role=role, group='target_minus_control', n=len(s),
                                         P_minus_D=tt['target']['P_minus_D'] - tt['control']['P_minus_D'], PmD_lo=X3.ci(a[0] - b[0])[0], PmD_hi=X3.ci(a[0] - b[0])[1],
                                         recovery_D=tt['target']['recovery_D'] - tt['control']['recovery_D'],
                                         recD_lo=X3.ci(a[1] - b[1])[0] if tt['target']['gap_rule_D'] and tt['control']['gap_rule_D'] else np.nan,
                                         recD_hi=X3.ci(a[1] - b[1])[1] if tt['target']['gap_rule_D'] and tt['control']['gap_rule_D'] else np.nan))
                for role in ROLES:                                     # paired role - ALL difference of the behaviour
                    if role != 'ALL' and (role, 'all') in boots and ('ALL', 'all') in boots:
                        r0 = [x for x in rows if x['set'] == setn and x['subset'] == sub and x['split'] == part and x['group'] == 'all']
                        rr = {x['role']: x for x in r0}
                        d = boots[role, 'all'][0] - boots['ALL', 'all'][0]
                        rows.append(dict(set=setn, subset=sub, split=part, role=role, group='role_minus_ALL', n=rr[role]['n'],
                                         P_minus_D=rr[role]['P_minus_D'] - rr['ALL']['P_minus_D'], PmD_lo=X3.ci(d)[0], PmD_hi=X3.ci(d)[1]))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--raw'); ap.add_argument('--out'); a = ap.parse_args()
    raw = Path(a.raw) if a.raw else ROOT / 'raw/para_tok'; out = Path(a.out) if a.out else ROOT / 'summary_x3'
    rep = (out / 'x3_roles.md') if a.out else ROOT / 'reports/x3_roles.md'; out.mkdir(parents=True, exist_ok=True)
    pp, t, nsh = per_paper(raw)
    df = pd.read_csv(ROOT / 'summary_x3/x3_pairs.csv')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): df[c] = df[c].astype(bool)
    # check 1: per-token means reproduce the stored para_run scores (bf16, batch 1 both times)
    al = pp['ALL'].reindex(df.paper_id); have = al.O.notna().to_numpy()
    dd = {k: np.abs(al[k].to_numpy()[have] - df[c].to_numpy()[have]) for k, c in (('O', 'score_original'), ('P', 'score_paraphrase'), ('B', 'score_partner'), ('D', 'score_lexical'))}
    chk = {k: dict(max=float(v.max()), mean=float(v.mean()), share_exact=float((v < 1e-9).mean()), share_le_0_01=float((v <= 0.01).mean())) for k, v in dd.items()}
    if any(c['max'] > 0.05 for c in chk.values()): warn(f'per-token means vs para_run scores: max |d| > 0.05 ({json.dumps({k: round(c["max"], 4) for k, c in chk.items()})})')
    if have.sum() < len(df): warn(f'{len(df) - have.sum()} x3_pairs papers have no para_tok rows ({nsh} shards read)')
    df = df[have].reset_index(drop=True)
    R = analyse(pp, df); R.to_csv(out / 'x3_roles.csv', index=False)
    # check 2: role ALL reproduces x3_recovery.csv (D, ratio of means and its CI)
    old = ROOT / 'summary_x3/x3_recovery.csv'
    if old.exists():
        o = pd.read_csv(old); o = o[(o.false == 'lexical_neighbour_D') & o.group.isin(['all', 'target', 'control'])]
        m = R[R.role == 'ALL'].merge(o, on=['set', 'subset', 'split', 'group'], suffixes=('', '_old'))
        dr = (m.recovery_D - m.ratio).abs().max(); dl = (m.recD_lo - m.lo).abs().max()
        chk['ALL_vs_x3_recovery'] = dict(n=len(m), max_ratio=float(dr), max_lo=float(dl))
        if not (dr < 0.01): warn(f'role ALL vs x3_recovery.csv: max |ratio diff| {dr:.4f}, |lo diff| {dl:.4f} (per-token rerun noise)')
    n_role = t.groupby('role').size().to_dict()
    L = ['# Stage 13 X3 by name-token role (V51)', '',
         'Handbook V51 (previously "not possible: para_run stored only per-name means"). User-approved re-run 2026-11-05. '
         'GPU: `13_stage13/stage13_x3_tok_gpu.py` (same rows, prompt `Who are the authors of the paper titled "{t}"?\\nAuthors:` and batch-1 teacher-forced scoring as para_run; per-token ranks with Stage 10 row_id; no residuals). '
         'Analysis: `13_stage13/stage13_x3_roles.py`. Pre-registered: addendum 4 token roles (name_first, surname_first, surname_cont; gap rule 0.05), behaviour = paraphrase - D (addendum 4). '
         'The recovery ratio (P - D)/(O - D) follows the post-hoc `stage13_x3_recovery.py` (V54) and is post-hoc here too. Intervals: 95% team-cluster bootstrap, 2,000 draws, the same draws as x3_recovery.', '',
         f'Tokens: {len(t)} first-author name tokens of {t.paper_id.nunique()} papers ({nsh} shards); by role ' + ', '.join(f'{k} {v}' for k, v in sorted(n_role.items())) + '.', '',
         '## Checks', '',
         '- Per-token mean vs stored para_run score, |difference| per version: ' + '; '.join(f'{k}: max {c["max"]:.4f}, mean {c["mean"]:.5f}, exact {c["share_exact"]:.3f}, <= 0.01 {c["share_le_0_01"]:.3f}' for k, c in chk.items() if k in 'OPBD') + '.',
         ('- Role ALL vs x3_recovery.csv (D): ' + f'{chk["ALL_vs_x3_recovery"]["n"]} rows, max |ratio diff| {chk["ALL_vs_x3_recovery"]["max_ratio"]:.4f}, max |CI low diff| {chk["ALL_vs_x3_recovery"]["max_lo"]:.4f}.') if 'ALL_vs_x3_recovery' in chk else '- x3_recovery.csv not found.',
         *(['- WARN: ' + w for w in WARN] or ['- No WARN.']), '']
    def tab(setn, sub, part):
        s = R[(R.set == setn) & (R.subset == sub) & (R.split == part)]
        o = [f'### {setn} / {sub} / {part}', '', '| role | group | n | O | P | D | O - D | P - D [CI] | recovery (P-D)/(O-D) [CI] | recovery vs B [CI] |', '|---|---|---|---|---|---|---|---|---|---|']
        for role in ROLES:
            for r in s[s.role == role].itertuples():
                if r.group in ('all', 'target', 'control'):
                    rec = fm(r.recovery_D, r.recD_lo, r.recD_hi) if r.gap_rule_D else f'not reported (O - D {r.O_minus_D:+.3f} < {GAP})'
                    recb = fm(r.recovery_B, r.recB_lo, r.recB_hi) if r.gap_rule_B else 'not reported (gap)'
                    o.append(f'| {role} | {r.group} | {r.n} | {r.O:+.3f} | {r.P:+.3f} | {r.D:+.3f} | {r.O_minus_D:+.3f} | {fm(r.P_minus_D, r.PmD_lo, r.PmD_hi)} | {rec} | {recb} |')
                elif r.group == 'target_minus_control':
                    o.append(f'| {role} | target - control | | | | | | {fm(r.P_minus_D, r.PmD_lo, r.PmD_hi)} | {fm(r.recovery_D, r.recD_lo, r.recD_hi)} | |')
                else:
                    o.append(f'| {role} | role - ALL (paired) | {r.n} | | | | | {fm(r.P_minus_D, r.PmD_lo, r.PmD_hi)} | | |')
        return o + ['']
    L += ['## Results', '', 'O = original title, P = paraphrase, D = lexical neighbour (addendum 5 jaccard2), B = partner. Scores: mean log10(1/rank) of the role\'s tokens (within paper), then mean over papers.', '']
    for k in (('primary', 'all', 'test'), ('primary', 'all', 'all'), ('sensitivity', 'all', 'test'), ('primary', 'd_matched', 'test'), ('primary', 'd_matched', 'all')):
        L += tab(*k)
    L += ['(Tune rows and all columns in `summary_x3/x3_roles.csv`.)', '', '## Conclusion', '', '<!--CONCLUSION-->', '']
    rep.write_text('\n'.join(L) + '\n'); (out / 'x3_roles_checks.json').write_text(json.dumps(dict(checks=chk, warn=WARN), indent=1))
    print('\n'.join(L[:20]))


if __name__ == '__main__':
    main()
