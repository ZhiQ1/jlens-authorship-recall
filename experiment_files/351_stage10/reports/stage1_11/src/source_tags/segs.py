"""Segment definitions for report v26 source tagging. seg(s, k) -> (start, end)."""
import re
ANCH = [
 ('S1a', None),
 ('S1b', '<h2><span class="st">Stage 7</span>'),
 ('S2',  '<h2>Stage 10–11：全量阶段</h2>'),
 ('S3',  '<h2><span class="num">§6</span>'),
 ('S4',  '<h3>6.11 Stage 11：干预'),
 ('S5',  '<h2>跨阶段：R0/R1 分层分析与两阶段对照</h2>'),
 ('S6',  '<h2><span class="st">Stage 13 · M3 X1 X4</span>'),
]
def bounds(s):
    pos = [0]
    for k, a in ANCH[1:]:
        assert s.count(a) == 1, (k, s.count(a)); pos.append(s.index(a))
    pos.append(len(s))
    return {k: (pos[i], pos[i+1]) for i, (k, _) in enumerate(ANCH)}
def strip_src(x):
    return re.sub(r'<span class="src">.*?</span>', '', x, flags=re.S)
