"""Report v23 (2026-11-01, user approved the X3 wording and the H2 cell): new X3 section (G', text baselines, behaviour
recovery, target/control split, D overlap), H2 result cell, X3 status cell, TOC link. Anchors must occur exactly once."""
import os, shutil
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p = 'stage1_11_report.html'
if not os.path.exists('stage1_11_report.v22.html'): shutil.copy2(p, 'stage1_11_report.v22.html')
s = open(p, encoding='utf-8').read()
M = lambda x: f'<span class="mono">{x}</span>'
X3 = ('<section id="x3-results"><h2><span class="st">Stage 13 · X3</span><span class="ln lC">C 哪一层</span> 换一种说法的标题：模型表示的是意思、用词，还是这篇论文？</h2>\n'
 '<p class="note">2026-10-31 完成。规则：prereg.json（X3）及补充 1、2、4、5。para_run 24 个分片（作业 11513313 分片 0、11385978 其余 23 个），分析作业 11521572，文本基线作业 11522507。主分析 1,110 篇（补充 5 的 1,115 篇中有 5 篇不在 pairs 表里），敏感性分析 1,012 篇。区间均为按作者团队重抽的 bootstrap。'
 + M('381_stage13/reports/x3_report.md') + '、' + M('x3_textbase_recovery.md') + '、' + M('x3_groupsplit.md') + '</p>\n'
 '<p>做法：用 Qwen3-32B 把标题改写成意思相同、用词不同的版本，比较原标题、改写、同领域里用词最接近的另一篇论文（近邻 D）在“作者是谁”提示中的表示和作者打分。主指标 G′ = cos(原, 改写) − cos(原, D)，只看它超出 L4 文字水平的部分 G′ − G′(L4)。</p>\n'
 '<div class="tw"><table><thead><tr><th>标题最后一个 token，测试集</th><th>L4 的 G′</th><th>G′ − G′(L4)，L28–L40</th><th>最高</th><th>L48</th><th>L60–L62</th></tr></thead><tbody>\n'
 '<tr><td>主分析（552 篇）</td><td>+0.30</td><td>+0.06 到 +0.16</td><td>L36 +0.159 [0.146, 0.171]</td><td>+0.013（区间含 0）</td><td>&lt; 0</td></tr>\n'
 '<tr><td>敏感性分析（506 篇）</td><td>+0.31</td><td>相近</td><td>L36 约 +0.16</td><td>—</td><td>&lt; 0</td></tr>\n'
 '<tr><td>有匹配近邻的子集（37 篇）</td><td>+0.12</td><td>—</td><td>+0.036（按规则的起始层）</td><td>—</td><td>—</td></tr>\n'
 '</tbody></table></div>\n'
 '<p>L4 上 G′ 已有 +0.30，这来自用词：改写与原标题的词重合度（修正版 Jaccard）中位数 0.611，近邻 D 只有 0.154。所以近邻 D 在 94% 的论文上找不到“用词不少于改写”的候选：同领域里与原标题词重合超过 0.3 的论文只占 2.4%，而改写有 88% 超过 0.3；只有 66 篇改写本身用词变化很大（中位数 0.143），才有匹配的 D。按规则取“调参集上第一个显著的层”得到 L8（+0.012），敏感性分析是 L24，起始层不稳，不作为结论。</p>\n'
 '<p><b>按 target / control 拆开</b>（主分析，测试集）：L28–L40 两组几乎相同（L36：target +0.158，control +0.160，差 −0.002 [−0.027, +0.025]），L24–L48 各层两组之差的区间都含 0。认不认得这篇论文，对这个中间层优势没有影响。</p>\n'
 '<p><b>文本模型基线</b>（同样的 G′，减去各模型自己的文字基线层）：BERT 每一层都低于它的第 0 层（−0.06 到 −0.21），没有中间层优势；句子向量模型 all-mpnet 只在最后一层超出（+0.142 [0.129, 0.156]）。最大优势 ÷ 文字基线的 G′：Qwen 0.52 [0.46, 0.59]，mpnet 0.30，BERT 为负；但在用词匹配的 66 篇子集上，mpnet（1.40）与 Qwen（1.90）之差的区间含 0。mpnet 的训练语料可能见过这些标题，但没有作者信息。</p>\n'
 '<p><b>行为</b>（教师强制打分，第一作者）：改写 − D 为 +0.239 [0.212, 0.266]。换算成恢复比例（改写 − 假）÷（真 − 假），“真”为原标题、“假”为近邻 D（Stage 10 的 false_0 提示带年份，与 X3 的提示模板不同，所以不用）：全部 0.90 [0.87, 0.94]，target 0.90 [0.85, 0.94]，control 0.91 [0.84, 0.98]，两组之差 −0.01 [−0.09, +0.07]；有匹配近邻的子集 0.73 [0.57, 0.89]。</p>\n'
 '<p><b>结论（2026-11-01 用户确认的措辞）：</b>改写标题在 Qwen 中间层（L28–L40，最高 L36 +0.16）比用词相近的近邻 D 更接近原标题，超出 L4 文字水平；行为上改写保留了原标题对 D 约 90% 的第一作者偏好（教师强制打分）。但这不足以说明“论文身份”：只懂语义、不认识作者的句子向量模型（all-mpnet）在用词匹配的子集上也有相当的优势；行为恢复和中间层优势在 target 与 control 之间都没有差别，与“认出论文”无关。所以 X3 只说明 Qwen 中间层表示了标题的意思而不只是用词，<b>不能区分“论文身份”与“语义”</b>。起始层在主分析和敏感性分析之间不一致（L8 对 L24），不作为结论。</p>\n'
 '<p class="note">与预注册的出入：补充 5 要求“按 token 角色”报告，但 para_run 只存了每个名字的平均分，无法按角色拆分。“:” 位置上各版本的余弦在 L4–L8 都接近 1，差距只有约 0.002，不作解读。</p>\n'
 '</section>\n\n')
R = [
('<a href="#m3x1x4-results">M3、X1、X4 结果</a> · ', '<a href="#m3x1x4-results">M3、X1、X4 结果</a> · <a href="#x3-results">X3 结果</a> · '),
('因此<b>不能排除</b> L8 的作者信号可以由标题文字解释。</p>\n</section>\n\n',
 '因此<b>不能排除</b> L8 的作者信号可以由标题文字解释。</p>\n</section>\n\n' + X3),
('M3 不支持（不高于 L4 文字水平）；H2 目前依据 M2 和 X1，其中 M2 的 Qwen 胜过 BERT 按补充 2 只作参考。</b>',
 'M3 不支持；X3 显示中间层超出用词的语义表示，但不能与论文身份区分；H2 目前依据 M2 和 X1，其中 M2 的 Qwen 胜过 BERT 按补充 2 只作参考。</b>'),
('<td>生成已完成（1,186 条）。', '<td><b>已完成（2026-10-31），结果见上文 X3。</b>生成已完成（1,186 条）。'),
('<th>目前结果（2026-10-31）</th>', '<th>目前结果（2026-11-01）</th>'),
('更新于 2026-10-31（第 22 版）', '更新于 2026-11-01（第 23 版）'),
]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:60]); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('applied', len(R))
