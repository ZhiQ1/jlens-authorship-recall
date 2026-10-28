"""Side-by-side: per-paper folds (summary_cpu/) vs author-team group folds (summary_cpu_group/) for M2, M2b, M2c.
Writes 381_stage13/reports/split_compare.md (E4b and its controls are in reports/e4b_split_compare.md)."""
from pathlib import Path
import pandas as pd
R = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); L = ['# Probe results: split by paper vs split by author team', '']
def side(fname, keys, val='value'):
    a, b = R / 'summary_cpu' / fname, R / 'summary_cpu_group' / fname
    if not (a.exists() and b.exists()): return [f'({fname}: not available yet)', '']
    d = pd.read_csv(a).merge(pd.read_csv(b), on=keys, suffixes=('_paper', '_group'))
    d['change'] = d[f'{val}_group'] - d[f'{val}_paper']
    return [d[keys + [f'{val}_paper', f'{val}_group', 'change']].round(3).to_string(index=False), '']
m2k = ['condition', 'position', 'layer', 'target']
L += ['## M2 (residual probes; false_0 per-paper numbers are invalid: donor titles crossed folds)', ''] + side('M2_probes.csv', m2k)
L += ['## M2b (title words vs residual probe; r2)', ''] + side('M2b_words_vs_probe.csv', ['model', 'layer', 'target'], 'r2')
L += ['## M2c (BERT baseline)', ''] + side('M2c_bert_baseline.csv', ['model', 'layer', 'target'])
(R / 'reports/split_compare.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
