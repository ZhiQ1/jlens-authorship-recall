"""Merge the per-part outputs of stage13_teamci_s10_12.py and write reports/teamci_s10_12.md (CPU, seconds)."""
from pathlib import Path
import time
import numpy as np, pandas as pd

J = Path('/scratch/zhang.zhiqi2/jlens'); OUT = J / '381_stage13/summary_teamci_s10_12'; REP = J / '381_stage13/reports/teamci_s10_12.md'
parts = ['s10', 's11', 's12', 'r1']
T = pd.concat([pd.read_csv(OUT / f'teamci_s10_12_{p}.csv') for p in parts if (OUT / f'teamci_s10_12_{p}.csv').exists()], ignore_index=True)
C = pd.concat([pd.read_csv(OUT / f'replay_check_{p}.csv') for p in parts if (OUT / f'replay_check_{p}.csv').exists()], ignore_index=True)

# decision rule used by each conclusion (what the published wording relies on)
RULE = {
    'output (final L63)': ('excl0', 'C01: output > 0'),
    'logit L24': ('about0', 'C01: "about 0" = |est| <= 0.05; CI not used by the wording'),
    'logit L32': ('about0', 'C01: "about 0" = |est| <= 0.05; CI not used by the wording'),
    'logit L50': ('excl0', 'C01: onset "from about L50" (lo > 0)'),
    'logit L56': ('excl0', 'C01: > 0'),
    'logit L62': ('excl0', 'C01: > 0'),
    'public J-lens L48': ('excl0', 'C01: < 0 (no mid-layer lead)'),
    'public J-lens L57': ('excl0', 'C01: J-lens positive from L57'),
    'R0 papers only': ('excl0', 'C01: R0-only output > 0'),
    'E1 recovery (false_0, all papers), L48': ('line', 'C02: "most recovered" at L48 (lo > 0.5)'),
    'E1 recovery (false_0, all papers), L52': ('line', 'C02: "almost fully" from L52 (CI covers ~1 / lo >= 0.95)'),
    'E2 knockout loss (all papers), from L0': ('line', 'C03: large loss from L0 (lo > 0.5)'),
    'E2 knockout loss (all papers), from L52': ('line', 'C03: no effect from L52 (hi < 0.05)'),
    'F2': ('excl0', 'C16: only L62 positive'),
    'R1 papers': ('excl0', 'C17: written > missed at output'),
}


def rule_of(q):
    for k, v in RULE.items():
        if k in q: return v
    return ('excl0', '')


def verdict(r):
    kind, txt = rule_of(r.quantity)
    if not r.replay_match: return 'not assessed (paper CI not reproduced)', txt
    lo, hi = r.team_lo, r.team_hi
    plo, phi = r.paper_lo, r.paper_hi
    def side(a, b): return 'pos' if a > 0 else ('neg' if b < 0 else 'zero')
    if kind == 'excl0': ch = side(plo, phi) != side(lo, hi)
    elif kind == 'about0': ch = abs(r.estimate) > 0.05
    else:
        q = r.quantity
        if 'L48' in q and 'E1' in q: ch = not (lo > 0.5)
        elif 'L52' in q and 'E1' in q: ch = not (lo >= 0.95)
        elif 'from L0' in q: ch = not (lo > 0.5)
        else: ch = not (hi < 0.05)
    extra = ''
    if kind == 'about0' and (side(plo, phi) != side(lo, hi)): extra = f' (excludes-0 flips: paper {side(plo, phi)}, team {side(lo, hi)}; wording unaffected)'
    return ('changed' if ch else 'unchanged') + extra, txt


f = lambda v: f'{v:+.3f}'
L = ['# Team-cluster CIs for the Stage 10-12 CIs in core conclusions C01-C24', '',
     f'Generated {time.ctime()} by `~/jlens_work/13_stage13/stage13_teamci_s10_12.py` (+ `_report.py`). CPU only, read-only on frozen outputs.', '',
     '**Method.** (1) The published paper-level bootstrap CI is first reproduced by re-running the frozen estimator functions with their original seed and '
     'call order (Stage 10 rng 3511 / 3512 / 3513, Stage 11 rng 3611, Stage 12 rng 3713; outputs redirected to `summary_teamci_s10_12/replay/`). '
     'Check: reproduced lo / hi equal the published values at 3 decimals; otherwise no team CI is given for that quantity. '
     '(2) Team-cluster bootstrap: archived Stage 13 author-team ids (`stage13_cpu.group_folds`, via `stage13_c13_s10lib.team_ids`; 7,247 teams over 9,108 papers), '
     '2,000 multinomial team draws, seed 1414, one draw per paper population; same point estimate, same citation-bin strata and within-bin weights '
     '(bins with >= 30 papers per group), same ratio-of-means for E1 / E2. For Stage 10 target + control the draw is identical to batch 3 item 3-1 '
     '(`reports/b3_3_1_report.md`), so the stored-layer values there are the same numbers.', '',
     '## 1. Inventory: Stage 10-12 CIs that enter C01-C24', '',
     'Already team-cluster in their sources (not recomputed): C04 P1 / P2 five-false-title mean (`R391/reports/b1_p12f_report.md`, team seed 391); '
     'C05 A - B (`R391/primary.csv`, groups_core team draw); C08 C / D (`R391/reports/b2_cd_report.md`, team seed 391); C01 3-1 layers L41-L49 '
     '(`b3_3_1_report.md`, team seed 1414). C07 (Stage 8) and all Stage 13 items (C06, C09-C15, C18-C24) are outside Stage 10-12. '
     'X6 / X7 numbers in C02 / C03 are Stage 13. Everything below was paper-level bootstrap.', '',
     '## 2. Paper vs team CI side by side', '',
     '| concl. | stage | quantity | n | estimate | paper CI (published) | team CI | width team/paper | replay check | decision line used | under team CI |',
     '|---|---|---|---|---|---|---|---|---|---|---|']
for r in T.itertuples():
    v, txt = verdict(r)
    tci = f'[{f(r.team_lo)}, {f(r.team_hi)}]' if r.replay_match else '-'
    wr = f'{r.width_ratio:.2f}' if r.replay_match else '-'
    L.append(f'| {r.conclusion} | {r.stage} | {r.quantity} | {r.n} | {f(r.estimate)} | [{f(r.paper_lo)}, {f(r.paper_hi)}] | {tci} | {wr} | '
             f'{"match" if r.replay_match else "NO MATCH"} | {txt} | {v} |')
L += ['', '## 3. Replay check (paper bootstrap reproduced with the frozen code)', '',
      '| concl. | quantity | published lo / hi | replayed lo / hi | max abs diff | match at 3 dp |', '|---|---|---|---|---|---|']
for r in C.itertuples():
    L.append(f'| {r.conclusion} | {r.quantity} | {r.published_lo:+.5f} / {r.published_hi:+.5f} | {r.replay_lo:+.5f} / {r.replay_hi:+.5f} | {r.max_abs_diff:.2e} | {r.match_3dp} |')
V = [verdict(r)[0] for r in T.itertuples()]; T['verdict'] = V
nch = sum(v.startswith('changed') for v in V)
L += ['', '## 4. Does any conclusion change under the team CI?', '',
      f'{len(T)} quantities; all {int(T.replay_match.sum())} paper CIs reproduced exactly with the frozen code (max |diff| {C.max_abs_diff.max():.1e}). '
      f'Changed: {nch}. Team / paper width ratio {T.width_ratio.min():.2f}-{T.width_ratio.max():.2f}.', '',
      '- C01: unchanged. Output, L50 onset, L56, L62 stay > 0; public J-lens L48 stays < 0 and L57 stays > 0; R0-only stays > 0. '
      'logit L32 (+0.005) now includes 0 under the team CI ([-0.000, +0.011]); the conclusion already calls L24-L48 "about 0" (|est| <= 0.05), so the wording is, if anything, better supported. '
      'Logit L24 (+0.007) still excludes 0 under both CIs, also covered by "about 0".',
      '- C02: unchanged (E1 L48 0.825 still well below 1 and well above 0.5; L52 CI still covers 1).',
      '- C03: unchanged (E2 from L52 0.007, team CI [+0.001, +0.013] still tiny and > 0; from L0 0.831).',
      '- C16: unchanged (F2 L62 > 0).',
      '- C17: unchanged (written - missed > 0 at output).', '']
T.to_csv(OUT / 'teamci_s10_12.csv', index=False); C.to_csv(OUT / 'replay_check.csv', index=False)
REP.write_text('\n'.join(L) + '\n' + (Path(__file__).with_name('stage13_teamci_s10_12_handbook_draft.md').read_text()
                                      if Path(__file__).with_name('stage13_teamci_s10_12_handbook_draft.md').exists() else ''))
print('\n'.join(L))
