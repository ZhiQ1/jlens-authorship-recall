import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
toks = [('Who are the authors of the paper titled "', 'p'), ('Reduced', 't'), ('-order', 't'), ('…', 't'), ('delay', 't'), ('" (2014)?\\n', 'p'), ('Authors:', 'c'), (' S', 'n'), ('.', 'n'), (' Bree', 'n'), (',', 's'), (' S', 'm'), ('.', 'm'), (' Snoek', 'm')]
col = {'p': '#eef1f6', 't': '#fde3cf', 'c': '#d9e7f5', 'n': '#d8efdf', 's': '#f2f2f2', 'm': '#e6f4ea'}
fig, ax = plt.subplots(figsize=(13, 8.4)); ax.set_xlim(0, 13); ax.set_ylim(0, 8.4); ax.axis('off')
x = 0.2; pos = {}
for i, (tk, k) in enumerate(toks):
    w = max(0.42, 0.083 * len(tk) + 0.22)
    ax.add_patch(FancyBboxPatch((x, 7.0), w, 0.6, boxstyle='round,pad=0.02', fc=col[k], ec='#555', lw=0.8))
    ax.text(x + w / 2, 7.3, tk.replace('\\n', '↵'), ha='center', va='center', fontsize=9.5, family='monospace')
    pos[i] = (x, x + w); x += w + 0.06
ax.text(0.2, 7.9, 'Prompt + author name (teacher forcing). Orange = title tokens, blue = last prompt token ":", green = name tokens (2nd author only in the Stage 11 chain).', fontsize=10)
def bracket(i0, i1, y, label, c):
    a, b = pos[i0][0], pos[i1][1]
    ax.plot([a, a, b, b], [y + .14, y, y, y + .14], color=c, lw=2.2); ax.text(0.2, y - .3, label, fontsize=10.5, color=c, va='center')
rows = [
    (6, 7, 6.45, 'Stages 4, 5, 7.2, 7.3, 8: score the FIRST token of the first author at ":" (rank / win rate vs false names)', '#1f4e79'),
    (6, 9, 5.6, 'Stages 6, 7.1: every name token of every author (each author alone), J-Lens / Vanilla, L16-62', '#2e7d32'),
    (6, 9, 4.75, 'Stage 10: every name token, all 9,108 papers, 7 title conditions (true / 5 false / none), L24-62 + L50-61', '#2e7d32'),
    (10, 13, 3.9, 'Stage 11 E3: authors scored in a chain "A1, A2, ..." (co-author context)', '#6a1b9a'),
    (5, 9, 3.05, 'Stage 11 E1: patch the residual of these positions (true -> false title), one layer at a time', '#b23c17'),
    (4, 4, 2.2, 'Stage 11 E1t: patch only the last title token; E4: read lens / probe at the last title token', '#b23c17'),
    (1, 4, 1.35, 'Stage 11 E2 / E2n: block attention TO these title tokens from layer l on (from all later / from ":" + names)', '#b23c17'),
]
for r in rows: bracket(*r)
ax.text(0.2, 0.35, 'Title-specific signal (Stages 5, 7.3, 8, 10, 11) = score with the true title minus score with metadata-matched false titles, on the same name tokens.', fontsize=10, style='italic')
fig.tight_layout(); fig.savefig('measurement_positions.png', dpi=160); print('ok')
