"""Texts for addendum 18b (shelf map) results, 2026-11-19. Every number checked against
381_stage13/summary_a18b_item{1..6}/ and summary_a18b_item2_step2/ (reports + csv)."""

SC = '600 篇子样本（Stage 11 样本中每个引用档 target / control 各 30 篇，seed 1817），团队整群 bootstrap 2,000 次'
LOCK = '补充 18b，2026-11-17 锁定（381_stage13/config/prereg_addendum18b.md，sha256 9104c351…）'
S1 = '（补充 18b 第 1 项；' + SC + '；381_stage13/summary_a18b_item1/item1_report.md、item1_criterion.csv、item1_map.csv；分析作业 11968239）'
S2 = '（补充 18b 第 2 项；' + SC + '；381_stage13/summary_a18b_item2/item2_report.md、item2_criterion.csv；步长 2（修正后）：summary_a18b_item2_step2_fix/item2_step2_fix_report.md、item2_criterion.csv（第一次运行 summary_a18b_item2_step2/ 有窗口分配错误，作废；修正代码 ~/jlens_work/13_stage13/a18b_item2_fix.py）；分析作业 11988292）'
S3 = '（补充 18b 第 3 项；' + SC + '；381_stage13/summary_a18b_item3/item3_report.md、item3_mean5.csv、item3_hardchecks.json；分析作业 11989143）'
S4 = '（补充 18b 第 4 项；' + SC + '；参考均值来自 Stage 11 样本中另外 586 篇；381_stage13/summary_a18b_item4/item4_report.md、item4_criterion.csv、item4_table.csv；分析作业 11970080）'
S5 = '（补充 18b 第 5 项；' + SC + '；381_stage13/summary_a18b_item5/item5_report.md、item5_table.csv；分析作业 11970331）'
S6 = '（补充 18b 第 6 项；' + SC + '；381_stage13/summary_a18b_item6/item6_report.md、item6_patch_mean5.csv、item6_contrasts.csv、item6_neurons.csv；分析作业 11971121）'


def src(s, html=True):
    return '<span class="src">' + s + '</span>' if html else '【' + s.strip('（）') + '】'


# ---------------------------------------------------------------- item 1 (layer map / readout)
I1 = ('<b>读出地图：名字位置之外有没有更早的“柜子”（' + LOCK + ' 第 1 项；探索性解读）：</b>在 9 个位置组（标题全部 / 内容词 / 首 / 末 token、右引号、年份数字、“)?\\n”、“Authors”、“:”）× 20 个层（L8、L16、L24、L32、L36、L40–L52 每层、L56、L60）上，用 logit lens、public J-lens（都只在同一套 9,137 个名字 token 内排名）和名字 token ridge probe（只用这 600 篇训练，比 9,108 篇的 probe 弱）读出作者，算 spec 的引用档内 target − control。锁定规则：某位置组在 ≤ L48 的某层 target − control 区间 &gt; 0，而同层名字位置（姓首 token）的区间含 0，记为“柜子先在该位置”。54 个“读出 × 金标准 × 位置组”组合中有 15 个在部分层满足（主金标准姓首 token 下 27 个中有 10 个），例如 logit lens 的年份位置 L40–L47、“:” L45–L48、“Authors” 只在 L36，public J-lens 的标题首 token 从 L8 起（L8、L24、L46–L48），probe 的年份位置从 L32 起；只有年份位置在三种读出下都满足（logit L40–L47、J-lens 只在 L42、probe L32–L47），其余位置在三种读出之间不一致。满足规则的格子效应都很小（target − control +0.008 到 +0.049），而且 54 个组合 × 每个最多 14 个 ≤ L48 的层都没有做多重比较校正。<b>读法：有零星的早期痕迹，但没有清楚的更早“柜子”（探索性）。</b>lens 名次与已存 H3 同尺度名次逐行一致的比例 0.971–0.996（阈值 0.95，通过）。')

# ---------------------------------------------------------------- item 2 (attention edges)
I2 = ('<b>哪条注意力边（第 2 项，分窗口屏蔽，锁定规则）：</b>在 6 个不重叠的 4 层窗口（L40–43 … L60–63）内各只断开一条边（所有头）：名字←标题、名字←尾部、尾部←标题、“:”←标题、名字←“:”。锁定规则（窗口内损失最大的边区间 &gt; 0，且与同窗口每条其他边的配对差区间 &gt; 0）在 L44–47、L48–51、L52–55 满足，三次都是名字←标题：S 损失 +0.0063 [0.0046, 0.0079]、+0.0112 [0.0084, 0.0138]、+0.0071 [0.0050, 0.0091]，最多是 S(none) = 0.328 的 3.4%；L40–43、L56–59、L60–63 不满足（L56 起各边损失约为 0，与 E2“从 L52 起阻断已没有影响”一致）。效应小：主分析中断开单条边最多去掉 3.4% 的信号，其余仍可走别的边。<!--A18B2-STEP2-START-->步长 2 的敏感性分析（11 个重叠窗口）：第一次运行有窗口分配错误（重叠窗口的每一层只分给第一个窗口，除 L40–43 外每个窗口实际只屏蔽后两层），已作废并修正重跑；修正后锁定规则在 11 个窗口中的 7 个满足（L42–45、L44–47、L46–49、L48–51、L50–53、L52–55、L54–57，覆盖 L42–L57，包括主分析的三个窗口），都是名字←标题，没有一个窗口由其他边胜出；L40–43、L56–59、L58–61、L60–63 不满足（损失约为 0）；最大损失 +0.0115 [0.0088, 0.0142]（L48–51，约为 S 的 3.5%）；修正后的掩码在主分析配置上与主分析名次完全一致。<!--A18B2-STEP2-END-->因此写作<b>“锁定规则下成立；<!--A18B2-VERDICT-START-->对窗口位置稳健（修正后的步长 2 敏感性分析：11 个重叠窗口中 7 个，L42–L57，同一条边）<!--A18B2-VERDICT-END-->；效应小（≤ S 的 3.5%）”</b>。未屏蔽基线（显式掩码）与已存 E1 行的名次一致性最低 0.632 / 0.513（阈值 0.95）记 WARN。')

# ---------------------------------------------------------------- item 6 (MLP L52-56)
I6 = ('<b>L52–56 的 MLP 做什么（第 6 项，描述性，无锁定数值判据）：</b>把真标题运行的 MLP 或注意力输出换进假标题运行（标题之后全部位置，5 个假标题平均）：整个 MLP 输出每层恢复 0.158–0.275（L52 +0.177 [0.168, 0.187]，L54 +0.275 [0.262, 0.289]），注意力 0.055–0.146，复现 Stage 12 P2 的分工。把 MLP 输出拆成与作者名字输出方向对齐的 512 维子空间（9,137 个名字 token 的 lm_head 行 × final norm 权重的前 512 个右奇异向量，占其方差 0.339）和它的正交补：对齐部分只恢复 0.022–0.042，只比随机 512 维子空间（0.014–0.023）略高；大部分在正交部分（0.132–0.229；每层“对齐 − 正交”−0.109 到 −0.187，区间都在 0 以下）。神经元层面，同一篇论文两个假标题之间 top-50 差异神经元的 Jaccard 0.267–0.297，不同论文之间 0.014–0.052（论文特有）。L52–L54 上 control 恢复得比 target 多（整个 MLP target − control −0.039 到 −0.059），L55–L56 没有差别。<b>读法：L52–56 的 MLP 带着这篇论文的信息，但不是以现成的作者名字方向写进去的（描述性）。</b>未替换的 false_0 名次与已存 E1 行的一致性最低 0.538（阈值 0.95）记 WARN。')

# ---------------------------------------------------------------- item 4 (L57-61)
I4 = ('<b>L57–L61 由谁写出（第 4 项，均值消融，锁定判据）：</b>在标题之后的尾部和全部名字输入位置，把 L57–L61 中一层的注意力或 MLP 输出换成参考均值（Stage 11 样本中另外 586 篇论文、5 个假标题下同一位置的均值，事先固定）。每一层 MLP 消融的损失都大于注意力消融：MLP − 注意力每层 +0.037 到 +0.046（区间都 &gt; 0），5 层平均 +0.040 [0.036, 0.045]；注意力消融损失 ≤ 0.0012，每层 MLP 消融去掉 S(none) = +0.328 的 11–14%；这个差在 target 上更大（target − control +0.025 [0.017, 0.034]）。<b>按锁定判据成立，定论（用户 2026-11-19 定）：“后段由 MLP 写出”。</b>未消融名次与已存 E1 行的一致性最低 0.627 / 0.527（阈值 0.95，bf16 批量形状差异）记 WARN。')

ROUTE = ('<b>合起来</b>：L48 的注意力把标题信息读入（P2；单独断开名字←标题这条边在 L44–55 损失最大，但最多只占信号的 3.4%）→ L52–56 的 MLP 加工（带论文信息，但大部分不在作者名字方向上）→ L57–61 的 MLP 写出（注意力几乎不起作用）。单部件替换 / 消融只给下限；单一模型、600 篇子样本。')

# ---------------------------------------------------------------- item 3 (arrival cells)
I3 = ('<b>逐格替换：到达的信息落在哪个位置（' + LOCK + ' 第 3 项；描述性，无锁定数值规则）：</b>把标题之后的尾部分成“:”、名字位置、年份数字 p5、右引号 p9、其余尾部，逐层（L40–L52 每层、L56、L60）只替换一组（true → false_k，5 个假标题平均）。名字位置带得最多：0.176（L40）→ 0.605（L48）→ 0.835（L52）→ 0.876（L56）；“:” 来得晚：L48 0.073 → L52 0.177；年份数字 p5 在 L41–L48 为 0.061–0.081（L46–47 最高 0.081），L56 降到约 0；右引号 p9 和其余尾部都 ≤ 0.026。整个尾部 0.292（L40）、0.804（L48）、0.988（L52）。整个尾部上 control 恢复得比 target 多（L40–L50 target − control −0.076 到 −0.093，L51 −0.058，L52 −0.024，L56 起约为 0）。<b>读法：到达的信息主要落在名字位置本身，“:” 在 L48 之后才分到一部分，年份位置只在 L41–L48 带一点。</b>硬检查两项都没有过、记 WARN：(a) 与已存 P1 行逐行名次相同的比例 0.72–0.81（要求 1；bf16 批量形状不同）；(b) 已存 586 篇 + 新 600 篇合并后的五标题平均 L48 0.821137，已发表 0.821056（差 8.1e-5，容差 1e-6），L52 差 −3.3e-5。')

# ---------------------------------------------------------------- item 5 (title words)
I5 = ('<b>标题里哪些词重要（' + LOCK + ' 第 5 项；描述性，无锁定数值判据）：</b>把标题词分成内容词 / 罕见词（标题语料文档频率 ≤ 5）/ 功能词 / 首末词，分别换成同义词（WordNet 3.0；功能词用固定近义表）或同长度的随机 token。最终输出上，内容词换成随机 token 损失 +0.374 [0.354, 0.394]，换成同义词只损失 +0.087 [0.072, 0.102]，差 −0.287 [−0.306, −0.269]；罕见词（同义 +0.023 / 随机 +0.151）、功能词（+0.008 / +0.044）、首末词（+0.018 / +0.067）的影响小得多。标题最后一个 token 上的 probe（L8–L24）方向相同但很小（内容词“同义 − 随机”：名字第一个 token −0.009 到 −0.018，姓首 token −0.021 到 −0.029）。<b>读法：模型主要靠标题内容词的意思，而不只是字面</b>，与 X3“表示了意思而不只是用词”一致，同样不能区分意思与论文身份。局限：WordNet 同义词很粗糙，不是严格的保义替换；4 篇论文的内容词没有可替换的同义词。true / false_0 名次与已存 E1 行完全一致（1.000）。')

LIM = ('<b>补充 18b（柜子地图）的范围。</b>六项都只在 600 篇子样本（Stage 11 样本中每档 target / control 各 30 篇，seed 1817）上、只用 Qwen3-32B；第 5 项的同义词来自 WordNet，很粗糙；第 2、4、6 项每次只断开 / 消融 / 替换一个部件，只给下限；第 1 项未做多重比较校正；第 3 项的两个硬检查和第 2、4、6 项的名次一致性检查没有达标（记 WARN，bf16 批量形状差异，照锁定规则继续算）；<!--A18B2-STEP2-START-->第 2 项步长 2 敏感性分析的第一次运行有窗口分配错误（重叠窗口的每一层只分给第一个窗口），已作废并修正重跑（修正后 11 个窗口中 7 个满足锁定规则）；<!--A18B2-STEP2-END-->第 3、5、6 项没有锁定的数值判据，只作描述。GPU 共 13.2 小时（含无效的第一次步长 2 运行）（第 1 项 0.82、第 2 项 1.56、第 2 项步长 2 修正重跑 2.0（第一次步长 2 运行 3.25，无效）、第 3 项 1.51、第 4 项 1.28、第 5 项 0.88、第 6 项 1.89；每项 ≤ 5 小时，符合锁定）。')

MAIN3 = ('补充 18b（600 篇子样本）补全了路线后段：L52–56 的 MLP 带论文信息，但大部分不在作者名字的输出方向上（描述性）；L57–61 由 MLP 写出（定论：锁定判据成立，MLP − 注意力 +0.040 [0.036, 0.045]）。')

# ---------------------------------------------------------------- short versions (talk docs, advisor, process report)
I1s = ('读出地图（补充 18b 第 1 项，600 篇子样本，探索性）：logit lens、public J-lens 和 probe 在 9 个位置组 × 20 个层上读作者；锁定规则（≤ L48 某位置组 target − control 区间 &gt; 0、同层名字位置区间含 0）在 54 个组合中的 15 个、部分层满足（如 logit 年份位置 L40–L47、J-lens 标题首 token L8、probe 年份位置从 L32），效应很小（+0.008 到 +0.049），未做多重比较校正。读法：有零星的早期痕迹，但没有清楚的更早“柜子”。')
I2s = ('第 2 项（分窗口屏蔽，锁定规则）：在 L44–47、L48–51、L52–55 规则满足，都是名字←标题这条边（+0.0063 [0.0046, 0.0079]、+0.0112 [0.0084, 0.0138]、+0.0071 [0.0050, 0.0091]），但主分析中最多只占信号的 3.4%；<!--A18B2-STEP2-START-->修正窗口分配后的步长 2 敏感性分析（第一次运行有窗口分配错误，已作废重跑）在 11 个重叠窗口中的 7 个（L42–L57）满足，同一条边。<!--A18B2-STEP2-END-->写作“锁定规则下成立，<!--A18B2-VERDICT-START-->对窗口位置稳健<!--A18B2-VERDICT-END-->，效应小（≤ S 的 3.5%）”。')
I6s = ('第 6 项（描述性）：L52–56 整个 MLP 输出每层恢复 0.158–0.275，注意力 0.055–0.146；与作者名字输出方向对齐的 512 维部分只恢复 0.022–0.042（随机 512 维 0.014–0.023），大部分在正交部分（0.132–0.229）：MLP 带论文信息，但不是现成的作者名字方向。')
I4s = ('第 4 项（均值消融，锁定判据成立，定论）：L57–L61 每层 MLP 消融的损失都大于注意力（每层 +0.037 到 +0.046，平均 MLP − 注意力 +0.040 [0.036, 0.045]；注意力消融损失 ≤ 0.0012，每层 MLP 去掉 S 的 11–14%）：后段由 MLP 写出。')
I3s = ('逐格替换（补充 18b 第 3 项，600 篇子样本，描述性）：名字位置带得最多（0.176（L40）→ 0.605（L48）→ 0.835（L52）→ 0.876（L56）），“:” 晚到（L48 0.073 → L52 0.177），年份数字在 L46–47 最高 0.081 后消失，右引号和其余尾部 ≤ 0.026；整个尾部 0.292（L40）、0.804（L48）、0.988（L52）。硬检查 (a)(b) 未过、记 WARN（逐行一致 0.72–0.81；合并均值差 8.1e-5）。')
I5s = ('标题词（补充 18b 第 5 项，600 篇子样本，描述性）：内容词换成随机 token 损失 +0.374 [0.354, 0.394]，换成同义词只损失 +0.087 [0.072, 0.102]（差 −0.287 [−0.306, −0.269]）；罕见词、功能词、首末词影响小得多。模型主要靠内容词的意思而不只是字面，与 X3 一致，仍分不开意思与论文身份；WordNet 同义词很粗糙。')

ROUTEs = ('路线三段（补充 18b，600 篇子样本）：' + I2s + I6s + I4s)
GPU = 'GPU 共 13.2 小时（含无效的第一次步长 2 运行）（第 1 项 0.82、第 2 项 1.56、第 2 项步长 2 修正重跑 2.0（第一次步长 2 运行 3.25，无效）、第 3 项 1.51、第 4 项 1.28、第 5 项 0.88、第 6 项 1.89；每项 ≤ 5 小时，符合锁定）'

# ---------------------------------------------------------------- English (Stage 13 script, README)
EN = ('Addendum 18b (shelf map; locked 2026-11-17, sha256 9104c351…; 600-paper subsample of the Stage 11 sample, 30 target + 30 control per citation bin, seed 1817; team-cluster bootstrap, 2,000 draws). '
      'Route: item 4 (L57–L61 mean ablation, locked criterion met; settled): the MLP loss exceeds the attention loss at every layer (+0.037 to +0.046 per layer; mean MLP − attention +0.040 [0.036, 0.045]; attention losses ≤ 0.0012; each MLP layer removes 11–14% of S) — the late layers are written by the MLPs. '
      'Item 6 (descriptive): the full MLP output at L52–L56 recovers 0.158–0.275 per layer, attention 0.055–0.146; the part aligned with the author-name output directions (512 dims) recovers only 0.022–0.042 (random 512 dims 0.014–0.023), most is orthogonal (0.132–0.229): the MLPs carry paper information, but not as ready-made author-name directions. '
      'Item 2 (windowed attention blocking): the locked rule is met in L44–47, L48–51 and L52–55, each time for the edge name ← title (+0.0063 [0.0046, 0.0079], +0.0112 [0.0084, 0.0138], +0.0071 [0.0050, 0.0091]; at most 3.4% of S); <!--A18B2-STEP2-START-->the first step-2 sensitivity run had a window-assignment bug and was rerun with the fix: the rule is met for the same edge in 7 of 11 overlapping windows (L42–L57; largest loss +0.0115 [0.0088, 0.0142], ≈ 3.5% of S)<!--A18B2-STEP2-END--> → met under the locked rule, <!--A18B2-VERDICT-START-->robust to window placement<!--A18B2-VERDICT-END-->, effects small (≤ 3.5% of S). '
      'Item 3 (per-cell patching, descriptive; hard checks a/b WARN): the name positions carry most of the arriving information (0.176 at L40 → 0.605 at L48 → 0.835 at L52 → 0.876 at L56), ":" arrives late (0.073 at L48 → 0.177 at L52), the year digit peaks at 0.081 (L46–47) and fades. '
      'Item 1 (readout map, exploratory): the locked rule is met in 15 of 54 readout × gold × position combinations at some layers, with small effects (+0.008 to +0.049) and no multiplicity correction → faint early traces, no clear earlier shelf. '
      'Item 5 (title words, descriptive): replacing content words with random tokens costs +0.374 [0.354, 0.394], with WordNet synonyms only +0.087 [0.072, 0.102] (difference −0.287 [−0.306, −0.269]) → meaning matters more than surface form (crude synonyms). '
      'GPU 13.2 h in total incl. the invalid first step-2 run (3.25 h) and its fixed rerun (2.0 h); each item ≤ 5 h, as locked.')
