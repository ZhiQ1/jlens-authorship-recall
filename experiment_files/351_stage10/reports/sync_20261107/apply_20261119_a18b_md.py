"""Addendum 18b into conclusions_v30 (+ repo copy), STATUS §3/§6, repo README (2026-11-19). Rebuilds from .before_20261119 backups."""
import shutil, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from a18b_texts_20261119 import *

def load(path):
    bk = path + '.before_20261119'
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    return open(bk, encoding='utf-8').read()

def put(t, anchor, new, mode='after'):
    assert t.count(anchor) == 1, (anchor[:60], t.count(anchor))
    return t.replace(anchor, anchor + new if mode == 'after' else (new + anchor if mode == 'before' else new))

def md(s):
    return s.replace('<b>', '**').replace('</b>', '**').replace('&gt;', '>').replace('<code>', '`').replace('</code>', '`')

PRE = '600 篇子样本（Stage 11 样本中每档 target / control 各 30 篇，seed 1817）；单一模型'
C29 = f'''
### C29 〔定论（补充 18b 第 4 项，锁定判据成立；用户 2026-11-19 由较稳升级）〕L57–L61 的作者信号由 MLP 写出，注意力几乎不起作用（均值消融）

- **结论**：在标题之后的尾部和全部名字输入位置，把 L57–L61 中一层的 MLP 输出换成参考均值，损失都大于同层注意力消融：MLP − 注意力每层 +0.037 到 +0.046（区间都 > 0），5 层平均 +0.040 [0.036, 0.045]；按锁定判据判为"后段由 MLP 写出"。
- **数字**：S(none) = +0.328 [0.308, 0.348]；注意力消融损失 ≤ 0.0012；每层 MLP 消融去掉 S(none) 的 11–14%；差的 target − control +0.025 [0.017, 0.034]。
- **出处**：`R13/summary_a18b_item4/item4_report.md`（Criterion 表、Loss per config 表）、`item4_criterion.csv`、`item4_table.csv`；分析作业 11970080；规则 `R13/config/prereg_addendum18b.md` 第 4 项（sha256 9104c351…，2026-11-17 锁定）。
- **相对 v29**：新增。补全 C04 路线的后段（C04 只到 L56）。2026-11-19 用户定为定论（原写较稳）。
- 〔前提：{PRE}；每次只消融一层一个部件（下限）；均值消融可能偏离分布；未消融名次与已存 E1 行的一致性 0.627 / 0.527 < 0.95（WARN，bf16 批量形状差异，照规则继续）〕
'''
C30_34 = f'''
### C30 〔未定（描述性，无锁定数值判据；补充 18b 第 6 项）〕L52–L56 的 MLP 带着这篇论文的信息，但大部分不在作者名字的输出方向上

- **结论**：{md(I6)}
- **出处**：`R13/summary_a18b_item6/item6_report.md`、`item6_patch_mean5.csv`、`item6_contrasts.csv`、`item6_neurons.csv`；分析作业 11971121；子空间 `R13/a18b_config/item6_subspace.npz`。
- **相对 v29**：新增。部分回答 C04 留下的"MLP 是查记忆还是变换格式"。
- 〔前提：{PRE}；描述性；512 维子空间是作者名字输出方向的一种取法；单层替换为下限〕

### C31 〔较稳（补充 18b 第 2 项，锁定规则成立且对窗口位置稳健；2026-11-19 由未定升级）〕L44–L55 的信息走"名字←标题"这条注意力边；对窗口位置稳健；效应小（≤ S 的 3.5%）

- **结论**：{md(I2)}
- **出处**：`R13/summary_a18b_item2/item2_report.md`（Rule per window 表）、`item2_criterion.csv`、`item2_table.csv`；步长 2：`R13/summary_a18b_item2_step2/`；窗口分配 `~/jlens_work/13_stage13/a18b_item2.py` `mask_fn_for` / `win_of`；分析作业 11988292、11990717。
- **相对 v29**：新增。2026-11-19 修正后的步长 2 敏感性分析显示对窗口位置稳健，由未定升级为较稳（出处 `R13/summary_a18b_item2_step2_fix/item2_step2_fix_report.md`、`item2_criterion.csv`；第一次步长 2 运行 `summary_a18b_item2_step2/` 作废）。
- 〔前提：{PRE}；单条边断开为下限；<!--A18B2-STEP2-START-->修正窗口分配后的步长 2 敏感性分析（第一次运行有窗口分配错误，已作废重跑）在 11 个重叠窗口中的 7 个（L42–L57）满足，同一条边。<!--A18B2-STEP2-END-->；名次一致性 WARN〕

### C32 〔未定（探索性；补充 18b 第 1 项）〕读出地图：名字位置之外有零星的早期痕迹，但没有清楚的更早"柜子"

- **结论**：{md(I1)}
- **出处**：`R13/summary_a18b_item1/item1_report.md`（Main comparison 表）、`item1_criterion.csv`、`item1_map.csv`；分析作业 11968239。
- **相对 v29**：新增。
- 〔前提：{PRE}；未做多重比较校正；probe 只用 600 篇训练；探索性解读〕

### C33 〔未定（描述性；补充 18b 第 3 项）〕到达的信息主要落在名字位置本身；":" 在 L48 之后才分到一部分；年份数字只短暂带一点

- **结论**：{md(I3)}
- **出处**：`R13/summary_a18b_item3/item3_report.md`、`item3_mean5.csv`、`item3_hardchecks.json`；分析作业 11989143。
- **相对 v29**：新增。细化 C02 / C04 的到达位置。
- 〔前提：{PRE}；描述性；硬检查 (a)(b) 未过（WARN）〕

### C34 〔未定（描述性；补充 18b 第 5 项）〕标题内容词的意思比字面重要

- **结论**：{md(I5)}
- **出处**：`R13/summary_a18b_item5/item5_report.md`（Final output 表、Title-position probe 表）、`item5_table.csv`；分析作业 11970331。
- **相对 v29**：新增。与 C14 一致。
- 〔前提：{PRE}；WordNet 同义词粗糙；描述性〕
'''
ROWS = '''| C29 | 定论（补充 18b 第 4 项，锁定判据成立；用户 2026-11-19 升级） | 路线 | 支持（后段由 MLP 写出） | L57–L61 每层 MLP 消融损失 > 注意力（+0.037 到 +0.046；平均 +0.040 [0.036, 0.045]）；注意力消融 ≤ 0.0012 |
| C30 | 未定（描述性，补充 18b 第 6 项） | H3 | 一致（描述性，不作检验） | L52–56 MLP 带论文信息，但对齐作者名字方向的部分只恢复 0.022–0.042（正交部分 0.132–0.229） |
| C31 | 较稳（补充 18b 第 2 项；2026-11-19 由未定升级） | 路线 | 锁定规则下成立，<!--A18B2-VERDICT-START-->对窗口位置稳健<!--A18B2-VERDICT-END-->，效应小 | L44–47、L48–51、L52–55 名字←标题损失最大（主分析最多 3.4% 的信号）；修正后的步长 2：11 个重叠窗口中 7 个（L42–L57）同一条边，最大 +0.0115 [0.0088, 0.0142] |
| C32 | 未定（探索性，补充 18b 第 1 项） | H3 | 不增加支持 | 54 个组合中 15 个在部分层满足规则，效应 +0.008 到 +0.049，未做多重比较校正：没有清楚的更早柜子 |
| C33 | 未定（描述性，补充 18b 第 3 项） | — | 时间框架 | 到达的信息主要落在名字位置（L52 0.835）；":" 晚到；年份数字短暂 |
| C34 | 未定（描述性，补充 18b 第 5 项） | H2 | 不能区分（与 C14 一致） | 内容词随机替换损失 +0.374 vs 同义词 +0.087；意思比字面重要，分不开论文身份 |
'''
CHG = '''20. **C29–C34 补充 18b 柜子地图（2026-11-19，600 篇子样本）**：C29（第 4 项，锁定判据成立）L57–L61 由 MLP 写出，**新增（定论；用户 2026-11-19 由较稳升级）**；C30（第 6 项，描述性）L52–56 MLP 带论文信息但不在作者名字方向；C31（第 2 项）锁定规则下名字←标题，对窗口位置稳健（修正后的步长 2：11 个窗口中 7 个；第一次步长 2 运行有窗口分配错误，已作废重跑），效应小，**新增（较稳；2026-11-19 由未定升级）**；C32（第 1 项，探索性）没有清楚的更早柜子；C33（第 3 项，描述性）到达信息落在名字位置；C34（第 5 项，描述性）内容词意思比字面重要。**新增**；同时更新"进行中"中补充 18b 一条和第五节对照表。
'''
cf = os.path.expanduser('~/jlens_work/conclusions_v30_draft.md')
t = load(cf)
t = put(t, '\n## 二、较稳', C29 + '\n', 'before')
t = put(t, '\n### 进行中（只写状态，不写结果）', C30_34, 'before')
old = [l for l in t.split('\n') if l.startswith('- **补充 18b**（柜子地图')][0]
t = put(t, old, '- **补充 18b**（柜子地图）：2026-11-17 锁定（`R13/config/prereg_addendum18b.md`，sha256 9104c351…），六项已完成（600 篇子样本，' + GPU + '），见 C29–C34；第 3 项 5(b) 已在补充 18 第 3 项完成，未重跑。', 'replace')
t = put(t, '当前总体判断（2026-11-09、2026-11-14 更新 H3）：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 同尺度下支持（补充 17 第 2 项，锁定确认性检验）。',
        '路线（2026-11-19，补充 18b）：注意力 L48 读入 → MLP L52–56 加工（论文信息大部分不在作者名字方向上，描述性）→ MLP L57–61 写出（锁定判据成立）；名字←标题这条边在锁定规则下成立、对窗口位置稳健，但效应小（≤ S 的 3.5%）。H 的总体判断不变。', 'after')
last_row = [l for l in t.split('\n') if l.startswith('| C22 | 较稳（用户 2026-11-14 升级')][0]
t = put(t, last_row, '\n' + ROWS.rstrip('\n'), 'after')
t = put(t, '19. **C25 D 名字链条（2026-11-17）**', '', 'after')
i = t.find('19. **C25 D 名字链条（2026-11-17）**'); j = t.find('\n', i)
t = t[:j + 1] + CHG + t[j + 1:]
open(cf, 'w', encoding='utf-8').write(t)
rc = '/scratch/zhang.zhiqi2/jlens-authorship-recall_update/docs/conclusions_v30.md'
load(rc); open(rc, 'w', encoding='utf-8').write(t)

# ------------------------------------------------------------------ STATUS
sf = '/scratch/zhang.zhiqi2/jlens/STATUS.md'
t = load(sf)
old = [l for l in t.split('\n') if l.startswith('- Addendum 18b (shelf map')][0]
S3new = ('- Addendum 18b (shelf map) LOCKED 2026-11-17 (381_stage13/config/prereg_addendum18b.md, sha256 9104c351…) — ALL SIX ITEMS DONE 2026-11-19 (600-paper subsample of the Stage 11 sample, 30 T + 30 C per bin, seed 1817; conclusions C29–C34). ' + EN.split('). ', 1)[1]
         + ' GPU-h per item (keeper_state.json gpu_s): 1 0.82, 2 1.56, 2-step2 3.25 (invalid, window-assignment bug), 2-step2-fix 2.0, 3 1.51, 4 1.28, 5 0.88, 6 1.89 = 13.2 GPU-h (9.9 without the invalid first step-2 run). WARN checks: item 3 hard checks (a) 0.72–0.81 row equality, (b) diff 8.1e-5 > 1e-6; items 2/4/6 rank parity vs stored E1 rows (min 0.513–0.632); item 1 parity OK (0.971–0.996), item 5 OK. Reports 381_stage13/summary_a18b_item{1..6}/, summary_a18b_item2_step2_fix/ (the first step-2 run summary_a18b_item2_step2/ is invalid).')
t = put(t, old, S3new, 'replace')
S6new = ('00000000000000. **2026-11-19 — addendum 18b (shelf map) complete, written into the documents locally (not published, no git):** report, handbook, advisor, process report (+ draft), walkthroughs, Stage 13 script, plain guide, conclusions (new C29–C34 + hypothesis rows; repo copy), README; claims_defs_v26. Item 4 locked criterion met (late layers written by MLPs, C29; settled per user 2026-11-19); item 2 met under the locked rule (C31; after the fixed step-2 rerun the same evening: robust to window placement, C31 → 较稳); item 1 exploratory, no clear earlier shelf (C32); items 3, 5, 6 descriptive (C33, C34, C30). DONE 2026-11-19 evening: item-2 step-2 rerun with fixed window assignment (381_stage13/summary_a18b_item2_step2_fix/item2_step2_fix_report.md; ≈ 2.0 GPU-h): rule met for name ← title in 7 of 11 overlapping windows (L42–L57), robust to window placement → C31 upgraded 未定 → 较稳. Bug of the first run: (a18b_item2.py win_of returns the first window containing a layer, so overlapping windows other than L40–43 blocked only their last two layers) . Results brief 351_stage10/reports/results_brief_20261118.md says "rule met in NO window" for step 2, but the report shows L42–45 and L52–55 (by label); brief also says T−C −0.076 to −0.093 "up to L51" (L51 is −0.058) and attention losses "≤ 0.001" (max 0.0012) — docs use the report values.\n\n')
t = put(t, '0000000000000. **2026-11-17 d', S6new, 'before')
open(sf, 'w', encoding='utf-8').write(t)

# ------------------------------------------------------------------ README
rf = '/scratch/zhang.zhiqi2/jlens-authorship-recall_update/README.md'
t = load(rf)
old = [l for l in t.split('\n') if l.startswith('| Addendum 18b |')][0]
t = put(t, old, '| Addendum 18b | shelf map (remaining items of the addendum-18 draft) | item 4 criterion met, settled (late layers written by MLPs); item 2 met under the locked rule, <!--A18B2-VERDICT-START-->robust to window placement<!--A18B2-VERDICT-END-->, small effects (≤ 3.5% of S); item 1 exploratory (no clear earlier shelf); items 3, 5, 6 descriptive | done 2026-11-19 (600-paper subsample, 13.2 GPU-h incl. the invalid first step-2 run) | 381_stage13/summary_a18b_item{1..6}/ |', 'replace')
t = put(t, '**Latest (2026-11-17).**', '**Latest (2026-11-19).** ' + EN + ' <sub>(381_stage13/summary_a18b_item{1..6}/, summary_a18b_item2_step2/; conclusions C29–C34)</sub>\n\n', 'before')
st12 = '### Stage 12 · Single positions, attention vs MLP, name priors, author-prompt lens'
i = t.find(st12); j = t.find('\n### ', i + 5)
t = t[:j] + '\n- Route, tested further by addendum 18b (600 papers): attention reads the title in at L48; the L52–L56 MLPs carry paper information mostly outside the author-name output directions (item 6, descriptive); the L57–L61 MLPs write the names (item 4, locked criterion met, settled: MLP − attention +0.040 [0.036, 0.045]); cutting the edge name ← title alone costs at most 3.4% of the signal in the main run, robust to window placement (item 2; fixed step-2 sensitivity). See Latest (2026-11-19).\n' + t[j:]
open(rf, 'w', encoding='utf-8').write(t)
print('ok')
