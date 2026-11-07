"""2026-11-07 ~03:00 (user approved): final local edits.
1 H1 result cell of the hypothesis table (report + handbook copy if any + zh/en images via hyp_table_png_v29*.py) and every '3–5×' colon claim
  without a layer range -> qualified (L4–L40; 2.2× at L48, 1.3–1.5× at L56–L63); numbers recomputed from 381_stage13/summary_m3/x1_similarity.csv
  (question_share = rel. distance question change / paper change, mean over the 3 question pairs, pos = colon) = x1_similarity.md colon table.
2 'n = 2001' in the U0 summary-table row -> 'n = 2,001' (report #pd-groups; handbook #k-groups regenerated from the report).
Backups *.before_20261107c.* (report: .before_20261107e.html, because .before_20261107c.html is the input of apply_20261107c.py)."""
import re, shutil, json
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
d = pd.read_csv(J / '381_stage13/summary_m3/x1_similarity.csv'); c = d[d.pos == 'colon'].groupby('layer').question_share.mean()
lo, hi = c.loc[4:40].min(), c.loc[4:40].max(); l48 = c.loc[48]; late = c.loc[56:63]
assert round(lo, 1) == 3.0 and round(hi, 1) == 4.9 and round(l48, 1) == 2.2 and round(late.min(), 1) == 1.3 and round(late.max(), 1) == 1.5, (lo, hi, l48, late)
NUM = dict(lo=round(lo, 1), hi=round(hi, 1), l48=round(l48, 1), late_lo=round(late.min(), 1), late_hi=round(late.max(), 1))
json.dump(NUM, open(Path(__file__).parent / 'H1_numbers_20261107.json', 'w'))
REP = R / 'stage1_11/stage1_11_report.html'
T = {k: R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_methods_zh', 'experiment_walkthrough_zh', 'keys_and_shelves_script_zh_en', 'progress_report_for_advisor_zh', 'stage13_script_zh_en']}
FILES = [REP, *T.values()]
def bkp(p):
    tag = 'before_20261107e' if p == REP else 'before_20261107c'
    b = p.with_name(p.stem + '.' + tag + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b
S = {p: bkp(p).read_text(encoding='utf-8') for p in FILES}; LOG = []
def rep(p, a, b, n=1):
    k = S[p].count(a); assert k == n, (p.name, k, a[:60]); S[p] = S[p].replace(a, b); LOG.append((p.name, a, b))
QZ = f'（L4–L40；L48 约 {NUM["l48"]} 倍，L56–L63 为 {NUM["late_lo"]}–{NUM["late_hi"]} 倍）'
SRC = f'<span class="src">（Stage 13 X1 相似度检查，“:” 位置，同篇换问法与换论文的相对距离之比，9,108 篇、3 个问法对平均：L4–L40 为 {NUM["lo"]}–{NUM["hi"]}，L48 {NUM["l48"]}，L56–L63 {NUM["late_lo"]}–{NUM["late_hi"]}；381_stage13/reports/x1_similarity.md colon 表；summary_m3/x1_similarity.csv question_share）</span>'
SRCS = '<span class="src">（x1_similarity.md colon 表）</span>'
# 1a report hypothesis table H1 result cell
rep(REP, '<td>见上文 M3、X1 结果</td>', f'<td>在 “:” 和名字位置成立；在 L4–L40，“:” 位置换问法时的移动是换论文时的 3–5 倍（L48 为 {NUM["l48"]} 倍，L56–L63 为 {NUM["late_lo"]}–{NUM["late_hi"]} 倍）' + SRC + '</td>')
# 1b report: the existing qualified sentence gets the late-layer part (same meaning, now complete)
rep(REP, '换问法的移动距离在 L4–L40 是换论文的 3–5 倍（L48 约 2.2 倍）', f'换问法的移动距离在 L4–L40 是换论文的 3–5 倍（L48 约 {NUM["l48"]} 倍，L56–L63 为 {NUM["late_lo"]}–{NUM["late_hi"]} 倍）')
# 2 U0 n
rep(REP, 'n = 2001 (7298 authors)', 'n = 2,001 (7298 authors)')
# 3 talk docs: unqualified 3–5× claims
rep(T['experiment_walkthrough_methods_zh'], '“:” 位置 3–5 倍。', '“:” 位置 3–5 倍' + QZ + SRCS + '。')
rep(T['experiment_walkthrough_zh'], '冒号位置相反，换问法时变化是换论文的 3–5 倍。', '冒号位置相反，换问法时变化是换论文的 3–5 倍' + QZ + SRCS + '。')
rep(T['keys_and_shelves_script_zh_en'], '换问法时冒号位置的状态移动是换论文的 3 到 5 倍。', '换问法时冒号位置的状态移动是换论文的 3 到 5 倍' + QZ + SRCS + '。')
EN = f' (L4–L40; {NUM["l48"]}× at L48, {NUM["late_lo"]}–{NUM["late_hi"]}× at L56–L63)<span class="src">(x1_similarity.md, colon table)</span>'
rep(T['keys_and_shelves_script_zh_en'], "the colon's state moves three to five times more when the question changes than when the paper changes.", "the colon's state moves three to five times more when the question changes than when the paper changes" + EN + '.')
rep(T['progress_report_for_advisor_zh'], '换问法时冒号位置的变化是换论文的 3–5 倍', '换问法时冒号位置的变化是换论文的 3–5 倍' + QZ + SRCS)
rep(T['stage13_script_zh_en'], '换问法时它的变化是换论文的 3 到 5 倍，存的是任务。', '换问法时它的变化是换论文的 3 到 5 倍' + QZ + SRCS + '，存的是任务。')
rep(T['stage13_script_zh_en'], 'it moves three to five times more when the question changes than when the paper changes,', 'it moves three to five times more when the question changes than when the paper changes' + EN + ',')
for p, s in S.items():
    assert not re.search('minyan', s, re.I); p.write_text(s, encoding='utf-8')
json.dump(LOG, open(Path(__file__).parent / 'apply_log_20261107e.json', 'w'), ensure_ascii=False, indent=1)
print(NUM); [print(l[0], '|', l[1][:60]) for l in LOG]
