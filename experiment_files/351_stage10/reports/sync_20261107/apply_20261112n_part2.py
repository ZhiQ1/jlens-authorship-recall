"""Round n, part 2: slide 24 (deck HTML) — the overlay warning line still described E4b as the main version, and the long footnote overlapped the page number.
Same backups as round n (*.before_20261112n). pptx counterpart already done by pptx_text_fix_20261112n.py (warning line); footnote shortened there too via _part2 rule below."""
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'merged_deck/stage1_11_deck.html'; s = D.read_text(encoding='utf-8'); rows = []
for a, b in [('⚠ E4b scores only the first name token (mostly an initial) · all tokens by role: see the addendum-9 slide (surname first token L40 +0.071',
              '⚠ Main number = all authors, all name tokens by role (addendum 9; surname first token L40 +0.071; old first-token version (E4b) +0.061'),
             ('+0.071: addendum 9, all authors, all name tokens by role (surname first token), pre-registered V0, 1,395 papers, team folds, title reuse dropped (old first-token version: +0.061); e4b_alltok.md',
              '+0.071: addendum 9, all authors, all tokens, surname first token, V0, 1,395 papers (old first-token: +0.061); e4b_alltok.md')]:
    assert s.count(a) == 1, a[:50]; s = s.replace(a, b); rows.append((a, b))
D.write_text(s, encoding='utf-8')
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(f'| n2-{i} | merged_deck/stage1_11_deck.html (slide 24) | {a[:120]}… | {b} | 1 |' for i, (a, b) in enumerate(rows, 1)) + '\n')
print('ok')
