"""Version-label check for title-position probe numbers (claims_defs_v8.VERSION_LABELS). Read-only; writes <out>/v8_version_labels.csv.
For each 3-decimal number within 160 chars after a version label (and before the next label), if the number equals (3-decimal rounding)
a value of some version in perdonor_by_run_layer.csv / c3b_role_layer.csv (spec / lo / hi / tc / tc_lo / tc_hi, layers L16-L60) but NOT
any value of the labelled version, the row is flagged 'label mismatch'; equal to the labelled version -> '一致'; equal to none -> 'n/a'.
Usage: CLAIMS_DEFS=claims_defs_v8 ~/conda-envs/jlens/bin/python claims_v8_post.py <out_dir>"""
import os, re, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import importlib
D = importlib.import_module(os.environ.get('CLAIMS_DEFS', 'claims_defs_v8'))
from claims_lib import JL
from claims_docs import units, locate

out = Path(sys.argv[1])
P = pd.concat([pd.read_csv(JL / '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv'), pd.read_csv(JL / '381_stage13/summary_c13/c3b/c3b_role_layer.csv')])
COLS = ['spec', 'lo', 'hi', 'tc', 'tc_lo', 'tc_hi']
VAL = {v: {round(x, 3) for c in COLS for x in g[c].dropna()} for v, g in P.groupby('version')}
LAB = re.compile('|'.join('(%s)' % rx for rx, _ in D.VERSION_LABELS))
NUMRX = re.compile(r'(?<![\d.])([+−\-]?\d\.\d{3})(?!\d)')
rows = []
for u in units():
    t = u[3]
    labs = list(LAB.finditer(t))
    for i, m in enumerate(labs):
        ver = D.VERSION_LABELS[next(k for k, g in enumerate(m.groups()) if g)][1]
        end = min(m.end() + 160, labs[i + 1].start() if i + 1 < len(labs) else len(t))
        for n in NUMRX.finditer(t, m.end(), end):
            if not re.search(r'L\d\d|token|首字母|姓|名|initial|surname|given', t[max(m.end(), n.start() - 40):n.start()]):
                continue
            x = round(float(n.group(1).replace('−', '-')), 3)
            others = [v for v, s in VAL.items() if v != ver and x in s]
            if x in VAL.get(ver, set()):
                st = '一致'
            elif others:
                st = 'label mismatch'
            else:
                st = 'n/a'
            rows.append(dict(doc=u[0], location=locate(u, n.start()), label=m.group(0), version=ver, number=n.group(1), status=st,
                             found_in_versions=' / '.join(others), context=t[max(0, m.start() - 30):n.end() + 30]))
R = pd.DataFrame(rows)
R.to_csv(out / 'v8_version_labels.csv', index=False, encoding='utf-8-sig')
print(R.status.value_counts().to_dict())
print(R[R.status == 'label mismatch'][['doc', 'location', 'label', 'number', 'found_in_versions', 'context']].to_string()[:6000])
