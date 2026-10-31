"""Report v22 (2026-10-31, user review of the handbook): M3 judged by the addendum-2 rule (does not support H2);
M3 / X1-similarity no longer used as support for paper identity; hypothesis table H2/H3 cells; X4 order sentence.
Every anchor must occur exactly once."""
import os, shutil
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p = 'stage1_11_report.html'
if not os.path.exists('stage1_11_report.v21.html'): shutil.copy2(p, 'stage1_11_report.v21.html')
s = open(p, encoding='utf-8').read()
R = [
('<th>T − T(L4)，L16–L40</th><th>预注册判定</th></tr>', '<th>T − T(L4)，L16–L40</th><th>判定（按补充 2）</th></tr>'),
('<td>年份 −0.03 到 −0.06，领域 −0.004 到 −0.007</td><td>T ≥ 0.8 → 判为“论文身份”（H2）；但没有超过 L4</td></tr>',
 '<td>年份 −0.03 到 −0.06，引用数 −0.02 到 −0.05（区间都不含 0）；领域 −0.004 到 −0.007</td><td>不高于 L4 文字水平（年份、引用数低于 L4，领域与 L4 分不开）→ <b>M3 不支持 H2</b></td></tr>'),
('T 在 L16–L40 一直 ≥ 0.92，按预注册阈值判为 H2，但它没有超过只有文字信息的 L4，反而略低。所以 M3 只能说明标题位置的表示不随问法改变，不能说明模型在标题处多出了文字以外的“论文身份”。',
 'T 在 L16–L40 一直 ≥ 0.92，但补充 2 规定只看它相对 L4 的变化：年份的 T − T(L4) 为 −0.03 到 −0.06，引用数为 −0.02 到 −0.05，区间都不含 0；领域为 −0.004 到 −0.007，与 L4 分不开。也就是说，中间层并不比只有文字信息的 L4 更跨问法一致，T 高是因为三种问法里标题文字完全相同。所以 <b>M3 不支持 H2</b>：它只说明标题位置的表示不随问法改变，不能说明模型在标题处多出了文字以外的“论文身份”。'
 '（2026-10-31 更正：此前的自动判定按 T ≥ 0.8 的绝对阈值写成“判为 H2”，不符合补充 2；已按补充 2 重写，见 <code>381_stage13/reports/m3_report.md</code> 末节，脚本 <code>13_stage13/stage13_m3_verdict2.py</code>。）'),
('所以准确的说法是：<b>问法让标题状态移动约 15–27%（以换论文为 1），但替换效果不变</b>。',
 '所以准确的说法是：<b>问法让标题状态移动约 15–27%（以换论文为 1），但替换效果不变</b>。这个相似度与 M3 一样受“三种问法标题文字相同”的影响，只说明问法对标题状态影响小，<b>不能单独作为“论文身份”的证据</b>。'),
('最先能读出的是第一作者，年份要到 L40 才能读出，而且很弱。',
 '最先能读出的是第一作者，年份要到 L40 才能读出，而且很弱。也就是说，最早可解码的顺序是第一作者（L8）早于年份（L40），<b>与 H2 预测的方向相反</b>。'),
('<td>不同问题下同一篇论文的表示在中间层相近，后期才按任务分开</td><td>见上文 M3、X1 结果</td></tr>',
 '<td>不同问题下同一篇论文的表示在中间层相近，后期才按任务分开<br><b>结果：</b>不高于 L4 文字水平，不支持</td>'
 '<td><b>M3 不支持（不高于 L4 文字水平）；H2 目前依据 M2 和 X1，其中 M2 的 Qwen 胜过 BERT 按补充 2 只作参考。</b>另外，X4 最早可解码的顺序是第一作者（L8）早于年份（L40），与 H2 预测的方向相反。</td></tr>'),
('<td><b>文本基线不弱于 Qwen，不能排除文字解释</b>（X4：名字首 token 上 BERT +0.088 ≥ Qwen L8 +0.018；L8 信号主要在姓上，见上文 X4）</td></tr>',
 '<td><b>文本基线不弱于 Qwen，不能排除文字解释，证据不足</b>（X4：名字首 token 上 BERT +0.088 ≥ Qwen L8 +0.018；L8 信号主要在姓上，见上文 X4）</td></tr>'),
('更新于 2026-10-30（第 21 版）', '更新于 2026-10-31（第 22 版）'),
]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:60]); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('applied', len(R))

# --- X1 relative to random C (V31), applied after the first block ---
s = open(p, encoding='utf-8').read()
a = '随机 C 的恢复率在 L4–L16 和 L48 的绝对值超过 0.1，按规则标为警告：这些层的恢复率要与 C 对照着读，结论不变。'
b = ('随机 C 的恢复率在 L4–L16 和 L48 的绝对值超过 0.1。2026-10-31 按 C 重算（每对论文先减去 C 的结果，R′ = R − R(C)；同一套团队 bootstrap，作业 11512702）：'
     '各问法的恢复率整体移动 −R(C)（测试集 L4–L32 上升约 0.07–0.15，L48 下降 0.12，L48 的 R′ 作者 0.30、年份 0.28、领域 0.29），'
     '但“作者 − 年份”“作者 − 领域”两个差值在减去同一个 C 后完全不变，所以按补充 2（区间在 [−0.1, 0.1] 内）L24–L48 的判定都不变。'
     'L48 有一点小而确实的任务依赖：作者 − 年份 +0.019 [+0.012, +0.026]、作者 − 领域 +0.008 [+0.001, +0.014]，区间不含 0；相对 C，年份问法保留作者问法效果的 94%，领域 97%。'
     '<span class="mono">381_stage13/reports/x1_vsC.md</span>')
assert s.count(a) == 1; s = s.replace(a, b); open(p, 'w', encoding='utf-8').write(s); print('X1 vs C applied')

# --- X6 / X7 by token role (V41, addendum 4), applied after the X1 block ---
s = open(p, encoding='utf-8').read()
a6 = '所有层的数字见 <code>summary_x6/x6_recovery.csv</code>。</p>\n</section>'
b6 = ('所有层的数字见 <code>summary_x6/x6_recovery.csv</code>。</p>\n'
      '<h4>按名字 token 角色拆开（补充 4 要求，2026-10-31，作业 11512706）</h4>\n'
      '<div class="tw"><table><thead><tr><th>角色（全部论文）</th><th>L48 的 R</th><th>L52</th><th>L48 角色 − 合计</th><th>预注册判定（target / control / 全部）</th></tr></thead><tbody>\n'
      '<tr><td>合计</td><td>0.821 [0.806, 0.835]</td><td>0.995</td><td>—</td><td>成立 / 成立 / 成立</td></tr>\n'
      '<tr><td>名字第一个 token（首字母或名）</td><td>0.791 [0.738, 0.849]</td><td>1.045</td><td>−0.030 [−0.077, +0.021]</td><td>成立 / 成立 / 成立</td></tr>\n'
      '<tr><td>姓的第一个 token</td><td>0.734 [0.711, 0.757]</td><td>0.971</td><td>−0.087 [−0.104, −0.070]</td><td><b>差一点不成立</b>（target L48 为 0.696，界线 0.70）/ 成立 / 成立</td></tr>\n'
      '<tr><td>姓的后续 token</td><td>0.893 [0.880, 0.906]</td><td>0.997</td><td>+0.072 [+0.057, +0.087]</td><td>成立 / 成立 / 成立</td></tr>\n'
      '</tbody></table></div>\n'
      '<p>标点的真假差距只有 0.006–0.018，低于 0.05，不报告比例。各角色在 5 个假标题之间 L48 的差都不超过 0.076。角色之间的差别只在 L48 恢复了多少：姓的第一个 token 和完整的名恢复得晚一些（完整的名 L48 只有 0.63，作为次要角色报告），姓的后续 token 早一些；“L48 约 80%”是这些角色的平均。到 L52 各角色都 ≥ 0.96，L56 都是 1.00。'
      '<span class="mono">381_stage13/reports/x6x7_roles.md</span></p>\n</section>')
a7 = '对 control，更准确的说法是“到 L54–56 才完全不需要”。</p>\n</section>'
b7 = ('对 control，更准确的说法是“到 L54–56 才完全不需要”。</p>\n'
      '<p><b>按名字 token 角色拆开</b>（2026-10-31，作业 11512706）：全部论文的 S(L52)，名字第一个 token 0.029 [−0.017, 0.075]，姓的第一个 token 0.032 [0.021, 0.043]，姓的后续 token 0.031 [0.022, 0.041]，与合计 0.029 都没有差别（差值区间都含 0）。'
      'target 和全部论文在三个角色上都成立；control 本来就差一点不成立（0.051），拆开后名字第一个 token 0.078、姓的后续 token 0.052 不成立，姓的第一个 token 0.049 刚好成立。所以 control 的“差一点”是合计层面的小效应，不是某一个角色造成的。'
      '<span class="mono">381_stage13/reports/x6x7_roles.md</span></p>\n</section>')
for a, b in ((a6, b6), (a7, b7)):
    assert s.count(a) == 1, a[:40]; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('X6/X7 roles applied')
# sed: 目前结果（2026-10-30）-> 2026-10-31 applied
