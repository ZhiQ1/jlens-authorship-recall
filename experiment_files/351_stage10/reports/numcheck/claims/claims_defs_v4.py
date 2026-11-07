"""claims_defs v4 (2026-11-07 ~03:15): v3 (unchanged) +
(1) the H1 colon-ratio numbers written by sync_20261107/apply_20261107e.py (source 381_stage13/reports/x1_similarity.md, colon table, column
    'question share' = rel. distance question change / paper change, mean over 3 question pairs; = summary_m3/x1_similarity.csv);
(2) keys & shelves script 'L48 恢复 0.82' / 'recovers 0.82 at L48' = user decision D: taken out of E1-L48 and checked by its own claim with
    2 decimals (statement starts with '用户决定 D（源 0.825 两位小数为 0.82）', so the label is in the check output).
Run with:  CLAIMS_DEFS=claims_defs_v4 bash claims_run.sh"""
from claims_defs_v3 import *          # noqa: F401,F403
from claims_defs_v3 import C, add, csv, md
X1S = '381_stage13/reports/x1_similarity.md'
EARLY = ['L4', 'L8', 'L16', 'L24', 'L28', 'L32', 'L36', 'L40']; LATE = ['L56', 'L60', 'L62', 'L63']
SEL = lambda rows, agg=None: md(X1S, r'^## colon', col='question share', row={'layer': rows}, agg=agg)
COMP = '“:” 位置，同篇换问法 ÷ 换论文的相对距离（3 个问法对平均），9,108 篇；x1_similarity.md colon 表 question share 列'
add('H1-early-min', 'H1：“:” 位置 L4–L40 换问法 / 换论文距离比（最小）', SEL(EARLY, 'min'), COMP, '9,108 篇', 1, [r'L4–L40 为 #(?=–4\.9)'], sign=False)
add('H1-early-max', 'H1：同上（最大）', SEL(EARLY, 'max'), COMP, '9,108 篇', 1, [r'L4–L40 为 3\.0–#'], sign=False)
add('H1-early-min-int', 'H1：L4–L40 比值下限（整数写法 3）', SEL(EARLY, 'min'), COMP, '9,108 篇', 0,
    [r'(?<![\d.])#(?=–5 倍（L(?:4–L40|48))', r'(?<![\d.])#(?= 到 5 倍（L4–L40)'], sign=False)
add('H1-early-max-int', 'H1：L4–L40 比值上限（整数写法 5）', SEL(EARLY, 'max'), COMP, '9,108 篇', 0,
    [r'(?<![\d.])3–#(?= 倍（L(?:4–L40|48))', r'(?<![\d.])3 到 #(?= 倍（L4–L40)'], sign=False)
add('H1-L48', 'H1：L48 比值', SEL(['L48']), COMP, '9,108 篇', 1, [r'L48 (?:约|为) ?#(?= ?倍)', r'#(?=× at L48)'], sign=False)
add('H1-late-min', 'H1：L56–L63 比值（最小）', SEL(LATE, 'min'), COMP, '9,108 篇', 1, [r'L56–L63 (?:为 )?#(?=–1\.5)', r'#(?=–1\.5× at L56–L63)'], sign=False)
add('H1-late-max', 'H1：L56–L63 比值（最大）', SEL(LATE, 'max'), COMP, '9,108 篇', 1, [r'L56–L63 (?:为 )?1\.3–#', r'1\.3–#(?=× at L56–L63)'], sign=False)
# (2) user decision D
byid = {c['id']: c for c in C}
EX = r'L48 恢复 0\.82，L52 起约等于 1|recovers 0\.82 at L48 and about 1\.0'
byid['E1-L48']['excl'] = EX if not byid['E1-L48'].get('excl') else byid['E1-L48']['excl'] + '|' + EX
e = byid['E1-L48']
add('E1-L48-userD', '用户决定 D（源 0.825 两位小数为 0.82）：keys & shelves 讲稿 E1 替换 L48 恢复比例', e['sel'], e['comp'], e['n'], 2,
    [r'L48 恢复 #(?=，L52 起约等于 1)', r'recovers #(?= at L48 and about 1\.0)'], sign=False, note='用户决定 D（源 0.825 两位小数为 0.82）')
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
