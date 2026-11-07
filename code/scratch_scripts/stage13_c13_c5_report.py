"""Addendum 13 item C-5 report: hard check (repro == published summary_extra) and merged all-layer tables.

HARD CHECK (plan): the original PLAN re-run (summary_c13/c5/repro) equals 351_stage10/summary_extra/*.csv for the 6 main layers
(every non-numeric cell identical, every numeric cell |diff| <= 1e-9 incl. bootstrap CIs, same RNG stream).
Merged tables (repro rows = published + ext rows) -> summary_c13/c5/all_layers/*.csv; report reports/c13_C5.md.
Usage  stage13_c13_c5_report.py [--tiny]
"""
import argparse, json, hashlib, sys
from pathlib import Path
import numpy as np, pandas as pd

ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
B = Path('/scratch/zhang.zhiqi2/jlens'); R13 = B / '381_stage13'; PUB = B / '351_stage10/summary_extra'
if hashlib.sha256((R13 / 'config/prereg_addendum13.json').read_bytes()).hexdigest() != 'be6d2c98a75bc63d22b070b8f00604c5a6e1e5f06da488754f3bd1a26404ec1e': raise SystemExit('PLAN CHANGED')
C5 = R13 / ('summary_c13/c5_tiny' if a.tiny else 'summary_c13/c5'); ALL = C5 / 'all_layers'; ALL.mkdir(parents=True, exist_ok=True)
REP = C5 / 'c13_C5.md' if a.tiny else R13 / 'reports/c13_C5.md'
FILES = ['X1_levels', 'X1_tc', 'X1_cond', 'X2_by_bin', 'X2_spearman', 'X3_means', 'X3_pairwise', 'X3_tc_spec_vs_logit', 'X1_by_format', 'X1_cond_by_first_role']

hc = {}
for f in FILES:
    p, q = pd.read_csv(PUB / f'{f}.csv'), pd.read_csv(C5 / 'repro' / f'{f}.csv')
    r = dict(shape_pub=list(p.shape), shape_new=list(q.shape))
    if p.shape != q.shape or list(p.columns) != list(q.columns): r |= dict(ok=False, why='shape/columns'); hc[f] = r; continue
    num = [c for c in p.columns if pd.api.types.is_numeric_dtype(p[c])]; oth = [c for c in p.columns if c not in num]
    same_oth = bool((p[oth].astype(str).values == q[oth].astype(str).values).all()) if oth else True
    dif = (p[num] - q[num]).abs(); nan_same = bool((p[num].isna().values == q[num].isna().values).all())
    mx = float(np.nanmax(dif.values)) if dif.size else 0.0
    r |= dict(ok=same_oth and nan_same and mx <= 1e-9, max_abs_diff=mx, labels_identical=same_oth, nan_pattern_identical=nan_same); hc[f] = r
status = 'PASS' if all(v['ok'] for v in hc.values()) else 'FAIL'
if a.tiny: status = f'TINY ({status} vs published; a shard subset is not expected to equal the full cohort)'
(C5 / 'c5_hardcheck.json').write_text(json.dumps(dict(status=status, files=hc), indent=1)); print('HARD CHECK', status)
if status == 'FAIL':
    REP.write_text(f'# C-5: HARD CHECK FAILED (item stopped)\n\n```\n{json.dumps(hc, indent=1)}\n```\n'); sys.exit(2)

# merged tables
M = {}
for f in FILES:
    p = pd.read_csv(C5 / 'repro' / f'{f}.csv').assign(source='published (main layers)'); e = pd.read_csv(C5 / 'ext' / f'{f}.csv').assign(source='C-5 new layer')
    m = pd.concat([p, e], ignore_index=True)
    m = m.sort_values([c for c in ('position', 'format', 'unit', 'metric', 'first_role', 'readout', 'lens', 'a', 'layer', 'group', 'citation_bin') if c in m.columns], kind='stable')
    m.to_csv(ALL / f'{f}.csv', index=False); M[f] = m

f3 = lambda v, lo, hi: f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
mark = lambda s: '' if s.startswith('published') else ' (new)'
ex = lambda lo, hi: '*' if (lo > 0 or hi < 0) else ''
L = ['# C-5 (addendum 13): Stage 10 extras at every stored layer', '',
     ('**TINY TEST (8 shards)**\n' if a.tiny else '') +
     'Plan `381_stage13/config/prereg_addendum13.json` (sha256 be6d2c98...). Copies of stage10_extra.py / _format.py / _cond_role.py with PLAN extended '
     '(13_stage13/stage13_c13_c5.py); main-layer rows re-run with the original seeds, new layers with seeds + 100. spec = true - mean of 5 false titles, '
     'log10(1/rank); bootstrap over papers as in the originals (B = 2,000). Teacher-forced preference, not generation. * = CI excludes 0.', '',
     f'## Hard check: {status}', '', '| file | rows (published / re-run) | max abs diff | labels identical | ok |', '|---|---|---|---|---|']
for f, v in hc.items():
    L.append(f'| {f} | {v["shape_pub"][0]} / {v["shape_new"][0]} | {v.get("max_abs_diff", float("nan")):.1e} | {v.get("labels_identical", "-")} | {v["ok"]} |')
L += ['', 'New readout-layers: X1 / X2 / X3 public and logit at L50-55, L57-61 (self100 / fitA have only the 6 main layers, already done); '
      'X1_by_format and X1_cond_by_first_role every stored readout-layer (public / logit 17 layers, self100 / fitA 6, final).', '']

# X1: spec all papers, first vs later tokens; target - control of spec
x1 = M['X1_levels']; x1 = x1[x1.group == 'all']; tc = M['X1_tc']
for ro in ['jlens_public', 'logit']:
    L += [f'### X1 token position, {ro}: title-specific signal (all papers) and target - control within bin', '',
          '| layer | first token spec | later tokens spec | first token T-C | later tokens T-C |', '|---|---|---|---|---|']
    for l in sorted(x1[x1.readout == ro].layer.unique()):
        g = x1[(x1.readout == ro) & (x1.layer == l)].set_index('position'); t = tc[(tc.readout == ro) & (tc.layer == l)].set_index('position')
        L.append(f'| L{l}{mark(g.source.iloc[0])} | ' + ' | '.join(f'{f3(g.loc[p, "spec"], g.loc[p, "spec_lo"], g.loc[p, "spec_hi"])}{ex(g.loc[p, "spec_lo"], g.loc[p, "spec_hi"])}' for p in ('first_token', 'later_tokens')) +
                 ' | ' + ' | '.join(f'{f3(t.loc[p, "spec_tc"], t.loc[p, "spec_tc_lo"], t.loc[p, "spec_tc_hi"])}{ex(t.loc[p, "spec_tc_lo"], t.loc[p, "spec_tc_hi"])}' for p in ('first_token', 'later_tokens')) + ' |')
    L.append('')
# X1_cond: later tokens given first token in top 10 (token unit, all)
xc = M['X1_cond']; xc = xc[(xc.unit == 'token') & (xc.group == 'all')]
L += ['### X1 conditional (token unit, all papers, true title): later-token level if the first token is in the top 10 minus if not', '', '| readout | ' + ' | '.join(['layer: diff [CI]']) + ' |', '|---|---|']
for ro in ['jlens_public', 'logit']:
    s = xc[xc.readout == ro]
    L.append(f'| {ro} | ' + '; '.join(f'L{int(x.layer)} {x.later_level_diff:+.3f}{ex(x.later_level_diff_lo, x.later_level_diff_hi)}' for _, x in s.iterrows() if not pd.isna(x.get('later_level_diff', np.nan))) + ' |')
L.append('')
# X2 spearman spec, all
x2 = M['X2_spearman']; x2 = x2[(x2.group == 'all') & (x2.metric == 'spec')]
L += ['### X2 Spearman (spec vs log10 citations, all papers)', '', '| readout | layers |', '|---|---|']
for ro in ['jlens_public', 'logit']:
    s = x2[x2.readout == ro]; L.append(f'| {ro} | ' + '; '.join(f'L{int(x.layer)} {x.spearman_rho:+.3f}{ex(x.rho_lo, x.rho_hi)}' for _, x in s.iterrows()) + ' |')
L.append('')
# X3 public - logit (spec), and T-C of (public - logit)
x3 = M['X3_pairwise']; x3 = x3[(x3.a == 'jlens_public') & (x3.b == 'logit') & (x3.metric == 'spec')]; xd = M['X3_tc_spec_vs_logit']; xd = xd[xd.lens == 'jlens_public']
L += ['### X3 public J-lens minus logit lens, title-specific signal', '', '| layer | public - logit (all papers) | target - control of (public - logit) |', '|---|---|---|']
for l in sorted(x3.layer.unique()):
    x = x3[x3.layer == l].iloc[0]; d = xd[xd.layer == l]
    L.append(f'| L{l}{mark(x.source)} | {f3(x["diff"], x.lo, x.hi)}{ex(x.lo, x.hi)} | ' + (f'{f3(d.iloc[0].tc_spec_minus_logit, d.iloc[0].lo, d.iloc[0].hi)}{ex(d.iloc[0].lo, d.iloc[0].hi)}' if len(d) else '-') + ' |')
L.append('')
# X1_by_format: spec (all papers) per format x position, public / logit
xf = M['X1_by_format']
for ro in ['jlens_public', 'logit', 'jlens_self100', 'jlens_fitA']:
    s = xf[xf.readout == ro]
    if not len(s): continue
    L += [f'### Name-format split, {ro}: title-specific signal (all papers) / target - control', '',
          '| layer | initial-first: first token | initial-first: later | given-first: first token | given-first: later |', '|---|---|---|---|---|']
    for l in sorted(s.layer.unique()):
        g = s[s.layer == l].set_index(['format', 'position'])
        L.append(f'| L{l}{mark(g.source.iloc[0])} | ' + ' | '.join(f'{g.loc[(fm, p), "spec"]:+.3f}{ex(g.loc[(fm, p), "spec_lo"], g.loc[(fm, p), "spec_hi"])} / {g.loc[(fm, p), "spec_tc"]:+.3f}{ex(g.loc[(fm, p), "spec_tc_lo"], g.loc[(fm, p), "spec_tc_hi"])}'
                                                                  for fm in ('initial_first', 'given_first') for p in ('first_token', 'later_tokens')) + ' |')
    L.append('')
f = M['X1_by_format']; f = f[f.readout == 'final']
if len(f):
    L.append('final 63: ' + '; '.join(f'{x.format}/{x.position} {x.spec:+.3f} / T-C {x.spec_tc:+.3f}' for _, x in f.iterrows())); L.append('')
# X1_cond_by_first_role
cr = M['X1_cond_by_first_role']
L += ['### Conditional split by first role (true title): later words if the first word is in the top 10 minus if not', '', '| readout | initial_first | given_first |', '|---|---|---|']
for ro in ['jlens_public', 'logit', 'jlens_self100', 'jlens_fitA', 'final']:
    s = cr[cr.readout == ro]
    if not len(s): continue
    L.append(f'| {ro} | ' + ' | '.join('; '.join(f'L{int(x.layer)} {x["diff"]:+.3f}{ex(x.lo, x.hi)}' for _, x in s[s.first_role == role].iterrows()) for role in ('initial_first', 'given_first')) + ' |')
L += ['', 'Full tables: `381_stage13/summary_c13/c5/all_layers/*.csv` (column `source` marks published vs new rows).']
REP.write_text('\n'.join(L) + '\n'); print('wrote', REP)
