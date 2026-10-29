import os
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
s=open('stage1_11_report.html').read()
sec='''<section id="m3x1x4-results"><h2><span class="st">Stage 13 · M3 X1 X4</span><span class="ln lB">B 读出工具</span><span class="ln lC">C 哪一层</span> 中间层的标题状态：是“这篇论文”，还是“这个问题”？</h2>
<p class="note">2026-10-29 完成。规则见 prereg.json 及补充 1、2：探针按作者团队分 5 折；X1、X4 在按团队划分的调参集上选层、在测试集上确认；区间均为按作者团队重抽的 bootstrap。报告：<code>381_stage13/reports/m3_report.md、x1_report.md、x4_report.md</code></p>
<h3>M3 同一篇论文换三种问法（问作者 / 问年份 / 问领域），探针能否通用（9,108 篇）</h3>
<p>迁移比 T = 在一种问法上训练、换另一种问法测试的成绩 ÷ 同一问法内训练和测试的成绩。补充 2 规定的主要指标是 L16–L40 的 T，并且要和 L4（只有文字信息的层）相比。</p>
<table><tr><th>位置</th><th>年份 T：L4</th><th>L16–L40</th><th>领域 T：L4</th><th>L16–L40</th><th>T − T(L4)，L16–L40</th><th>预注册判定</th></tr>
<tr><td>标题最后一个 token</td><td>0.98</td><td>0.92–0.95</td><td>1.00</td><td>0.99</td><td>年份 −0.03 到 −0.06，领域 −0.004 到 −0.007</td><td>T ≥ 0.8 → 判为“论文身份”（H2）；但没有超过 L4</td></tr>
<tr><td>最后的 “:”</td><td>&lt; 0</td><td>&lt; 0</td><td>0.29</td><td>0.26–0.36</td><td>—</td><td>T &lt; 0.5 → 判为“任务特定”（H1）</td></tr></table>
<p><b>怎么读</b>：三种问法只在标题前的 9 个 token 上不同，标题本身完全一样，所以标题位置的状态从 L4 起就主要由标题文字决定。T 在 L16–L40 一直 ≥ 0.92，按预注册阈值判为 H2，但它没有超过只有文字信息的 L4，反而略低。所以 M3 只能说明标题位置的表示不随问法改变，不能说明模型在标题处多出了文字以外的“论文身份”。到了 “:” 位置，状态已经按问题重新组织：用别的问法训练的探针预测年份和引用数，比直接猜平均值还差（R² 为负，表中写作 &lt; 0）。身份指数 I 在两个位置都低于 L4（标题位置 −0.003 到 −0.016，“:” 位置 −0.42 到 −0.61），同样不支持“高于文字水平”。完整数字见 <code>summary_m3/</code>。</p>
<h3>X1 把 A 从“别的问法”得到的标题状态替换进 B 的作者提示（测试集 582 篇）</h3>
<table><tr><th>层</th><th>R 作者问法</th><th>R 年份问法</th><th>R 领域问法</th><th>R 随机论文 C</th><th>判定（补充 2）</th></tr>
<tr><td>L4–L16</td><td>1.00</td><td>1.00</td><td>1.00</td><td>−0.15 到 −0.13</td><td>只作文字替换的对照，不下结论</td></tr>
<tr><td>L24</td><td>0.99</td><td>0.99</td><td>0.99</td><td>−0.10</td><td>与任务无关</td></tr>
<tr><td>L32</td><td>0.97</td><td>0.97</td><td>0.97</td><td>−0.07</td><td>与任务无关</td></tr>
<tr><td>L40</td><td>0.92</td><td>0.92</td><td>0.92</td><td>−0.01</td><td>与任务无关</td></tr>
<tr><td>L48</td><td>0.42</td><td>0.41</td><td>0.42</td><td>+0.12</td><td>与任务无关（作者 − 年份 = +0.019）</td></tr></table>
<p>L24–L48 各层，作者问法减年份问法、作者问法减领域问法都在 ±0.02 以内，区间在 [−0.1, 0.1] 之内；作者问法减随机 C 都 ≥ +0.30，所以判为“与任务无关”。随机 C 的恢复率在 L4–L16 和 L48 的绝对值超过 0.1，按规则标为警告：这些层的恢复率要与 C 对照着读，结论不变。和 M3 一样，这里替换的是同一段标题文字的状态，所以“与任务无关”的意思同样是“不随问法改变”。</p>
<h3>X4 把论文自己的标题状态放进“X 的发表年份 / 第一作者 / 领域是”这类提示</h3>
<table><tr><th>答案</th><th>标题位置：最早可读出层（调参集选、测试集确认）</th><th>测试集 D</th><th>“:” 位置</th></tr>
<tr><td>第一作者</td><td>L8（已确认）</td><td>+0.046 [0.035, 0.059]，L40 最高 +0.068</td><td>L48 起 +0.012</td></tr>
<tr><td>年份</td><td>L40（已确认）</td><td>+0.013 [0.008, 0.018]</td><td>读不出</td></tr>
<tr><td>领域</td><td>调参集上读不出（区间很宽）</td><td>—</td><td>读不出</td></tr></table>
<p>D = 用本论文的状态减去用配对论文的状态得到的答案得分（年份从不出现在提示里）。预注册的顺序（年份、领域不晚于作者）<b>不成立</b>：最先能读出的是第一作者，年份要到 L40 才能读出，而且很弱。在同一引用档内，认得出的论文（target）比 control 更容易读出作者：标题位置 L8–L40 高 +0.04 到 +0.06，区间都不含 0。年份没有这种差别。</p>
</section>

'''
assert s.count('<section id="p4-plan">')==1 and 'm3x1x4-results' not in s
s=s.replace('<section id="p4-plan">', sec+'<section id="p4-plan">').replace('<a href="#x7-results">X7 结果</a> · ','<a href="#x7-results">X7 结果</a> · <a href="#m3x1x4-results">M3、X1、X4 结果</a> · ')
open('stage1_11_report.html','w').write(s); print(s.count('m3x1x4-results'))
