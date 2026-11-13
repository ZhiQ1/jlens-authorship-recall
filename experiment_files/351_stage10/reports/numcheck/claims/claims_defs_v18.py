"""claims_defs v18 (2026-11-12 priority deck build): v17 + P1/P2 five-title-mean numbers (slides 59/67, notes 59/67) checked against
391_groups/summary_b1_p12f/p12f_mean5.csv (column ratio, who=all_authors, group=all); the old false_0 claims (E1-L48, P1-names, A5-P1-names48,
A5-P1-colon2, A5-P2-mlp52-2) no longer catch windows that carry the five-title-mean value (EXCL18).
Run with:  CLAIMS_DEFS=claims_defs_v18 bash claims_run.sh"""
from claims_defs_v17 import *          # noqa: F401,F403
from claims_defs_v17 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A18-' + cid; MANUAL[-1] = c['id']


PF = '391_groups/summary_b1_p12f/p12f_mean5.csv'
W = dict(who='all_authors', group='all')
COMP = 'P1/P2 五个假标题平均恢复 R，全部作者，团队聚类 95% CI；p12f_mean5.csv 列 ratio；'
for cid, ex, item, L, pats in [
    ('p1-all48', 'P1', 'all', 48, [r'整段标题之后 L48 #', r'L48 #(?= \[0\.807, 0\.835)']),
    ('p1-names48', 'P1', 'names', 48, [r'名字位置从 #(?= 升到)', r'name positions alone #(?= →)', r'L48 #(?= \[0\.599)']),
    ('p1-names52', 'P1', 'names', 52, [r'升到 #(?=（5 个假标题平均)', r'(?<=→ )#(?= \(false_0 0\.61)', r'只换名字位置 L52 #(?=（false_0 版)', r'L52 #(?= \[0\.827)']),
    ('p1-colon52', 'P1', 'p1', 52, [r'只换“:”最多 #', r'‘:’ ≤ #', r'L52 #(?= \[0\.168)']),
    ('p2-attn48', 'P2', 'attn', 48, [r'读进来（#', r'L48 注意力 #(?=（0\.231）)', r'at L48 \(#(?=; false_0)', r'L48 #(?= \[0\.229)']),
    ('p2-mlp52', 'P2', 'mlp', 52, [r'MLP 接手（#', r'MLP #(?=、0\.226)', r'L52–56 \(#', r'L52 #(?= \[0\.174)']),
    ('p2-mlp56', 'P2', 'mlp', 56, [r'MLP 接手（0\.181、#', r'MLP 0\.181、#', r'\(0\.181, #', r'L56 #(?= \[0\.217)'])]:
    A(cid, 'P1/P2 五个假标题平均：%s %s L%d' % (ex, item, L), csv(PF, 'ratio', experiment=ex, item=item, layer=L, **W), COMP, '1,186 篇', 3, pats, sign=False)
EX = r'0\.821|0\.613|0\.841|0\.181|0\.237|0\.226'
for c in C:
    if c['id'] in ('E1-L48', 'P1-names', 'A5-P1-names48', 'A5-P1-colon2', 'A5-P2-mlp52-2'):
        c['excl'] = EX if not c.get('excl') else c['excl'] + '|' + EX
