"""M3 reading under prereg addendum 2 (2026-10-31, user review of the methods handbook, item V28).

The automatic reading in stage13_m3_analyze.py judged H2 by the absolute level T >= 0.8. Addendum 2 says T is judged at
L16-L40 AND relative to T(L4), and the identity index counts only as I(l) - I(L4) > 0 (interval excludes 0): identical
title tokens across the three prompts already give T and I near 1 at L4. This script reads the saved summaries
(no recomputation), writes the addendum-2 reading, and marks the old reading in reports/m3_report.md as superseded
(backup reports/m3_report.before_verdict2_2026-10-31.md).

Per position and target, over L16-L40:
  above text level  : T - T(L4) interval > 0 at some layer   -> transfer beyond the L4 text level (would support H2)
  below text level  : T - T(L4) interval < 0 at every layer   -> not above L4; M3 does not support H2
  otherwise         : not distinguishable from L4
Identity index: I - I(L4) interval > 0 at some L16-L40 layer -> supports H2, else not."""
import shutil
from pathlib import Path
import pandas as pd

ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); S = ROOT / 'summary_m3'; REP = ROOT / 'reports/m3_report.md'
MARK = '## Reading under prereg addendum 2'


def main():
    A = pd.read_csv(S / 'm3_transfer.csv'); A = A[(A.train == 'avg') & A.layer.between(16, 40)]
    I = pd.read_csv(S / 'm3_identity.csv'); I = I[I.layer.between(16, 40)]
    L = [MARK + ' (2026-10-31; replaces the "Pre-registered reading" above, which used the absolute threshold T >= 0.8)', '',
         'Rule: T at L16-L40 judged relative to T(L4); identity index only as I(l) - I(L4) (intervals: team-cluster bootstrap).', '']
    rows = []
    for p in ('title_last', 'colon'):
        for t in ('year', 'log_citations', 'field'):
            s = A[(A.pos == p) & (A.target == t)].sort_values('layer')
            if s.empty: continue
            up = s[s.td_lo > 0].layer.tolist(); down = (s.td_hi < 0).all()
            v = (f'above the L4 text level at L{", L".join(map(str, up))}' if up else
                 'below the L4 text level at every layer (not above L4) -> M3 does not support H2' if down else
                 'not distinguishable from the L4 text level')
            if p == 'colon' and (s.hi < 0.5).all(): v += '; T < 0.5 throughout (task-specific, as before)'
            rng = f'{s.T_minus_L4.min():+.3f} to {s.T_minus_L4.max():+.3f}'
            L.append(f'- {p}, {t}: T - T(L4) at L16-L40 = {rng} -> {v}')
            rows.append(dict(pos=p, target=t, T_minus_L4_min=s.T_minus_L4.min(), T_minus_L4_max=s.T_minus_L4.max(), above_layers=' '.join(map(str, up)), all_below=down, verdict=v))
    for p in ('title_last', 'colon'):
        s = I[I.pos == p]
        up = s[s.d_lo > 0].layer.tolist()
        v = f'I - I(L4) > 0 at L{", L".join(map(str, up))} -> supports H2' if up else 'I - I(L4) < 0 or includes 0 at every layer -> does not support H2'
        L.append(f'- identity index, {p}: I - I(L4) at L16-L40 = {s.I_minus_L4.min():+.3f} to {s.I_minus_L4.max():+.3f} -> {v}')
        rows.append(dict(pos=p, target='identity_index', T_minus_L4_min=s.I_minus_L4.min(), T_minus_L4_max=s.I_minus_L4.max(), above_layers=' '.join(map(str, up)), all_below=(s.d_hi < 0).all(), verdict=v))
    L += ['', '**Summary:** at the title position the cross-prompt transfer and the identity index are high (T 0.92-0.99, I 0.96-0.98) but '
          'never above the L4 level, which identical title tokens already give; so M3 does not show a paper-identity state beyond '
          'the title text, and does not support H2. At the colon the state is task-specific (H1 reading unchanged). '
          'H2 rests on M2 and X1 (M2: Qwen above BERT counts only as a reference under addendum 2).', '']
    pd.DataFrame(rows).to_csv(S / 'm3_verdict_addendum2.csv', index=False)
    txt = REP.read_text()
    bak = REP.with_name('m3_report.before_verdict2_2026-10-31.md')
    if not bak.exists(): shutil.copy2(REP, bak)
    txt = txt.split(MARK)[0].rstrip() + '\n'
    txt = txt.replace('## Pre-registered reading (L16-L40)', '## Pre-registered reading (L16-L40) - SUPERSEDED 2026-10-31 (absolute threshold, not the addendum-2 rule; see below)')
    REP.write_text(txt + '\n' + '\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    main()
