"""Texts for addendum 20 (H2 fictitious titles) doc sync, 2026-11-20. Numbers from 391_groups/summary_a20/a20_report.md,
primary_secondary_sensitivity.csv, S3_layer_profile.csv, S4_E1_fict_donor.csv, S6_M2_attributes.csv (checked by hand 2026-11-20)."""

LOCK = '补充 20，2026-11-20 锁定（391_groups/config/prereg_addendum20.md，sha256 fee691de…）'
SRC = '391_groups/summary_a20/a20_report.md、primary_secondary_sensitivity.csv；1,127 篇（566 target、561 control），团队整群 bootstrap 2,000 次，seed 20261120'
SRC_EN = '391_groups/summary_a20/a20_report.md, primary_secondary_sensitivity.csv; 1,127 papers (566 target, 561 control), team-cluster bootstrap, 2,000 draws'

VERDICT = 'H2 部分支持——存在真实论文成分，但大部分信号可由语义相似解释'
VERDICT_EN = 'H2 partly supported — a real-paper component exists, but meaning similarity explains most of the signal'
STATUS = VERDICT + '（补充 20，锁定的确认性检验）'

# long version (report, handbook result paragraph, methods walkthrough)
A20 = ('<b>虚构标题检验（' + LOCK + '；锁定的确认性检验）：</b>为 Stage 11 样本中的 1,127 篇论文（566 篇 target、561 篇 control；59 篇按生成规则事先排除）'
       '各写一个意思相近、但并不存在的虚构标题（由 Qwen3-32B 生成，过滤：与队列标题和 Crossref 检索结果都不重合，与真标题的 mpnet 余弦中位数 0.65，'
       '假标题 0.09，X3 同义改写 0.97），放进同一提示、同一年份打分。G = 真 − 5 个假标题平均，A = 虚构 − 5 个假标题平均，R = 真 − 虚构；'
       'φ = ΣA / ΣG 是虚构标题恢复的“标题特有差距”的比例。target 组最终输出（L63）：<b>φ_T = 0.751 [0.723, 0.778]</b>，'
       '<b>R̄_T = +0.106 [0.094, 0.118]</b>（Ḡ_T 0.425，Ā_T 0.319）。按锁定规则（R̄_T 区间全部大于 0、φ̂_T ≥ 0.5）判为：<b>' + VERDICT + '</b>'
       '（φ_T 区间不跨 0.3 或 0.5，不是临界）。次要（描述性）：control φ_C 0.770 [0.727, 0.814]、R̄_C +0.050 [0.039, 0.061]；'
       '同一引用档内 R_T − R_C +0.056 [0.039, 0.072]，是 H2 预测的方向；φ_T − φ_C −0.022 [−0.081, 0.033]。R̄ 只在 L56 之后明显大于 0'
       '（J-lens L62 +0.115 [0.101, 0.131]）；以虚构标题为供体的尾部替换（E1 做法）从 L52 起恢复约 0.745，真标题为 1.00（L54 差 +0.255 [0.227, 0.284]）；'
       '标题位置 probe 的真 − 虚构 +0.02 到 +0.04，真 − 假标题 +0.06 到 +0.10（target）；标题位置读年份、引用数的 R² 换成虚构标题后明显下降'
       '（L48 引用数 0.36 → 0.10，全部 1,127 篇），领域准确率不变；语义越接近 φ 越高（按余弦三分位 0.72 / 0.74 / 0.79，第 3 − 第 1 分位 +0.072 [0.002, 0.140]）。'
       '敏感性 a–f（只用 false_0、去掉 Crossref 重合 ≥ 0.4 的标题、真标题 ≥ 6 词、只看第一作者或姓首 token、只看 R0、按标题似然分层）中 φ_T 在 0.708–0.778，'
       'R̄_T 都大于 0，判定不变。虚构标题在模型下比真标题更“典型”（标题 token 平均 log 概率 真 − 虚构 target −0.12、control −0.25）。')

# short version (advisor, walkthrough, plain guide, Stage 13 script)
A20s = ('补充 20（虚构标题，锁定的确认性检验，2026-11-20）：给每篇论文写一个意思相近但不存在的标题，它能恢复“真 − 假标题差距”的 75%'
        '（φ_T = 0.751 [0.723, 0.778]）；只有真标题才给的部分 R̄_T = +0.106 [0.094, 0.118]，区间在 0 以上。按锁定规则：' + VERDICT +
        '（target 566 篇，最终输出 L63；control φ 0.770、R̄ +0.050）。')

A20_EN = ('Addendum 20 (fictitious titles, locked confirmatory test, 2026-11-20): each paper got a fictitious title close in meaning to the real one '
          'that does not exist. It recovers 0.751 [0.723, 0.778] of the true − false-title gap; what only the real title gives is '
          'R̄ = +0.106 [0.094, 0.118] (target, final L63, 566 papers; control 0.770 and +0.050). By the locked rule: ' + VERDICT_EN + '.')

LIM = ('<b>补充 20 的一致性检查与第一次运行：</b>H200 重算与已存 A100 Stage 10 值的名次完全相同比例 0.55–0.66（阈值 0.75），'
       '平均 |Δlog10 名次| ≤ 0.014，记 WARN，数字保留；S_真 和 S_假 用已存 A100 值、S_虚构 用 H200 本次运行。第一次运行的冻结脚本把真标题当作虚构标题'
       '（φ = 1、R = 0），已作废并修正重跑（GPU 共 1.08 小时，其中无效运行 0.55）。标题位置 probe 和 M2 读出原未存权重，按已发表设置重拟合。')

GPU_ROW = ('<tr><td>补充 20 虚构标题（H2；1,127 篇）</td><td>1×H200</td><td>1.08 h（有效运行 0.53；第一次运行 0.55，冻结脚本把真标题当作虚构标题，无效）</td>'
           '<td>12015462、12015463（有效）；12014065、12014453、12014454（无效）</td><td>11-20</td>'
           '<td><span class="src">391_groups/summary_a20/a20_report.md 第 6 节 · raw/a20_INVALID_README.txt</span></td></tr>\n')

HB_SEC = ('\n<h3 id="s13-a20">补充 20　虚构标题：H2 论文身份还是标题语义</h3>'
          '<h4>1 问题与作用</h4><p>H2 说标题位置的状态表示“是哪一篇论文”。假标题是另一篇真实论文的标题，意思离得很远（余弦中位数约 0.1），所以“真 − 假标题”的差距既可能来自论文身份，'
          '也可能来自标题意思接近该领域常见作者。意思相近、但不存在的标题只带领域、不带身份，可以把两者分开：若是语义，它应恢复大部分差距；若是身份，它应恢复很少。</p>'
          '<h4>2 材料</h4><p>Stage 11 样本（593 + 593 篇，10 个引用档）中有合格虚构标题的 1,127 篇（566 target、561 control；59 篇按生成规则排除，真标题较短，中位 5 词对 12 词）。'
          '虚构标题由 Qwen3-32B 生成（关闭思考，T 0.7，每篇 8 个候选，最多 2 轮重生成），过滤：与 9,108 篇队列标题不重合；Crossref 前 3 个结果 jaccard2 &lt; 0.5；与真标题 jaccard2 &lt; 0.3；'
          '长度相近；mpnet 余弦在 [0.30, min(0.85, 同义改写余弦 − 0.1))；双向蕴含排除；首词不同；取通过的候选中余弦最高的。锁定前随机 20 个由用户核对，100 个人工核对中 #41、#80 已替换。'
          '<span class="src">391_groups/h2_fictitious/v3/selected_v3b.csv（sha256 7b8dd31d…）· raw/a20v2_freeze/</span></p>'
          '<h4>3 工具</h4><p>GPU：<code>~/jlens_work/15_h2fict/h2_main_gpu.py</code>（只读导入 Stage 10 / 11 冻结脚本；每个 Stage 11 分片：打分、标题位置残差和 7 个提示的标题 log 概率、尾部替换，分片 0 加一致性检查）；'
          'CPU 分析 <code>h2_main_analyze.py</code>（groups_core.Engine）。提示与 Stage 10 相同（真论文的年份），teacher forcing。</p>'
          '<h4>4 公式与判据</h4><p>每篇论文 S_c = 最终输出 L63 所有作者所有名字 token 的平均 log10(1/名次)；F̄ = 5 个假标题平均；G = S_真 − F̄，A = S_虚构 − F̄，R = S_真 − S_虚构。'
          '主量（target）：φ_T = ΣA / ΣG，R̄_T = mean R；团队整群 bootstrap 2,000 次（seed 20261120），比值在每次抽样中重算。锁定规则（用户 2026-11-19 定的四种读法加反向一行）：'
          'R̄_T 区间全部大于 0 时按 φ̂_T 读——&lt; 0.3 强支持，0.3–0.5 部分支持（权重有限），≥ 0.5 部分支持（语义解释大部分）；R̄_T 区间含 0 不支持；全部小于 0 被反向结果否定；'
          'φ_T 区间跨 0.3 或 0.5 时标“临界”。0.5 和 0.3 的依据：X3 同义改写（余弦约 0.95–0.97）恢复约 0.92，纯语义解释按余弦 0.65 预测 φ ≈ 0.6。</p>'
          '<h4>5 结果</h4><p>' + A20 + '<span class="src">' + SRC + '</span></p>'
          '<h4>6 局限</h4><p>' + LIM + '单一模型；虚构标题由同一模型生成，可能更“典型”（敏感性 f 按标题似然分层后判定不变）；0.5 和 0.3 的界限是在知道 X3 结果后定的。</p>')
