"""2026-11-07 ~22:00: user changed the D13-1 wording (for_user_2026-11-07.md section a, lines 9–12). Rebuild the D13-1 box in the report
(#p1-s8, written by apply_20261107g.py) without "因此，不一致只出现在后改的 L56 上；在原定的主终点上，代理结果不要求重算。", and align the
handbook V59 / deviation-list rows. Numbers re-read from c2_followup_proxy.csv (aa_all). Note: the 7-layer (L16 = L24) RQ2 lower bound is
+0.0055 in the CSV -> written +0.005 (the for_user file says +0.006). Backups: *.before_20261107i.*"""
import re, shutil
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
REP = R / 'stage1_11/stage1_11_report.html'; G = R / 'methods/parts/G_appendix.html'; B = R / 'methods/parts/B_global2.html'
def load(p):
    b = p.with_name(p.stem + '.before_20261107i' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
px = pd.read_csv(J / '381_stage13/c13_C2_followup/c2_followup_proxy.csv'); px = px[px.version == 'aa_all'].set_index('endpoint')
f3 = lambda v: f'{v:+.3f}'.replace('-', '−'); ci = lambda a, b: f'[{f3(a)}, {f3(b)}]'
r2 = lambda e: f'{f3(px.loc[e, "rq2"])} {ci(px.loc[e, "rq2_lo"], px.loc[e, "rq2_hi"])}'
r1 = lambda e: f'{f3(px.loc[e, "rq1"])} {ci(px.loc[e, "rq1_team_lo"], px.loc[e, "rq1_team_hi"])}'
SZ = lambda t: f'<span class="src">（{t}）</span>'
SRC13 = '381_stage13/reports/c13_C2.md；381_stage13/c13_C2_followup/c2_followup_proxy.csv（aa_all 行；RQ1 团队 bootstrap 2,000 次，RQ2 配对 bootstrap 10,000 次，200 篇 / 100 对，种子同 C-2）'
BOX = ('<div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>'
       f'按补充 13 C-2 的判定规则（prereg_addendum13.json 第 18 行），全部作者 CPU 代理（public J-lens 名次、Stage 10 的 5 个假标题——每篇都是整 5 个，351_stage10.py 第 302、863 行；不是原 W）只在 L56 的 RQ2 上与已发表结论不一致：{r2("L56")}，区间含 0'
       + SZ(SRC13 + '，endpoint=L56') + '。因此触发按原 W 在 GPU 上重算；用户 2026-11-06 决定不做，列为偏离。'
       '报告 v29 和 PPT v20 都以锁定计划的 7 层积分为冻结主终点（本节“Stage 8 结论”；PPT 第 17 页“7-layer (frozen primary)”）；L56 在锁定计划里是探索性次终点，10-18 21:14 的 PROTOCOL.md 把它改为主终点，改动者和依据仍未查清（U28）。'
       f'在 10-18 14:29 锁定计划的 7 层积分终点上（Stage 10 没有 L16，按 L16 = 0 或 L16 = L24 近似），代理 RQ2 为 {r2("int7_L16zero")} 或 {r2("int7_L16eqL24")}，RQ1 为 {r1("int7_L16zero")} 或 {r1("int7_L16eqL24")}，都与已发表结论同向、区间不含 0'
       + SZ('同上，endpoint=int7_L16zero / int7_L16eqL24') + f'。6 层 int6 的 RQ2 为 {r2("int6")}'
       + SZ('同上，endpoint=int6；int6 = public J-lens 在 L24、L32、L40、L48、L56、L62 的等权平均，少了 L16，与锁定的 7 层积分不是同一终点（13_stage13/stage13_c13_s10lib.py 第 17、70 行；351_stage8/config/analysis_plan.json 第 14、27、29 行）')
       + '。补充 13 的规则是 RQ1 或 RQ2 任一结论改变即触发；本次触发只来自 L56。7 层积分的代理结果是近似值（Stage 10 没有 L16 的读出）。Stage 8 RQ2 在 L56 的结论没有用原统计量复核。'
       '已发表的原 W（按原种子复现）：7 层积分 RQ1 +2.326 [+1.496, +3.192] pp、RQ2 +2.409 [+0.909, +4.003] pp；L56 RQ1 +5.178 [+2.926, +7.476] pp、RQ2 +4.981 [+0.322, +9.915] pp'
       + SZ('351_stage8/recompute_2026-10-30/s8_endpoints.csv 第 2–7 行') + '</div>\n')
s = load(REP)
s, c = re.subn(r'<div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>.*?</div>\n', lambda m: BOX, s, flags=re.S); assert c == 1
assert '代理结果不要求重算' not in s
a = '列为偏离 D13-1：CPU 代理只在后改的 L56 上 RQ2 区间含 0，在原定的 7 层积分终点上同向且区间不含 0，'
assert s.count(a) == 1
s = s.replace(a, '列为偏离 D13-1：规则是 RQ1 或 RQ2 任一改变即触发，本次只来自 L56（PROTOCOL.md 后改的终点，U28）的 RQ2；在锁定计划的 7 层积分终点上（近似，Stage 10 没有 L16）同向且区间不含 0，')
REP.write_text(s, encoding='utf-8')
g = load(G)
a = '。L56 是 21:14 PROTOCOL.md 改定的终点（U28）；Stage 8 RQ2 在 L56 的结论没有用原统计量复核。'
assert g.count(a) == 1
g = g.replace(a, '。规则是 RQ1 或 RQ2 任一改变即触发，本次只来自 L56；L56 在锁定计划里是探索性次终点，21:14 由 PROTOCOL.md 改为主终点（U28）；7 层积分的代理是近似值（Stage 10 没有 L16）；代理用 Stage 10 的 5 个假标题，每篇整 5 个（351_stage10.py 第 302、863 行）。Stage 8 RQ2 在 L56 的结论没有用原统计量复核。')
G.write_text(g, encoding='utf-8')
b = load(B)
a = '用户决定不做；锁定的 7 层积分终点上同向、区间不含 0</td>'
assert b.count(a) == 1
b = b.replace(a, '用户决定不做；规则是 RQ1 或 RQ2 任一改变即触发，本次只来自 L56（PROTOCOL.md 后改的终点，U28）；锁定的 7 层积分终点上（近似，Stage 10 没有 L16）同向、区间不含 0</td>')
B.write_text(b, encoding='utf-8'); print('ok', r2('int7_L16eqL24'))
