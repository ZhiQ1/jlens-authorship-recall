"""Report v25 (2026-11-02, final for the defence): X5 layer-order section with figure; X5 status; TOC; date."""
import base64, os, shutil
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p = 'stage1_11_report.html'
if not os.path.exists('stage1_11_report.v24.html'): shutil.copy2(p, 'stage1_11_report.v24.html')
s = open(p, encoding='utf-8').read()
M = lambda x: f'<span class="mono">{x}</span>'
img = base64.b64encode(open('/scratch/zhang.zhiqi2/jlens/381_stage13/reports/x5_layer_order.png', 'rb').read()).decode()
X5 = ('<section id="x5-results"><h2><span class="st">Stage 13 · X5</span><span class="ln lC">C 哪一层</span> 层序：各类信息最早在哪一层出现</h2>\n'
 '<p class="note">2026-11-02 完成，只用已有结果、CPU。每个来源沿用它自己的判定规则（多数为“团队区间不含 0 的第一层”）；各来源测量的层不同，“≤Lx”表示第一个测到的层就已经有了。'
 + M('381_stage13/reports/x5_report.md') + '、' + M('summary_x5/x5_layer_order.csv') + '，脚本 ' + M('13_stage13/stage13_x5_layer_order.py') + '</p>\n'
 f'<figure><img alt="X5 层序图：各类信息最早出现的层" src="data:image/png;base64,{img}" style="width:100%;height:auto"><figcaption>图 X5　圆点 = 按来源规则最早出现的层（X7 为“仍需要标题”的最后一层）；菱形 = 更严的阈值或敏感性分析；色条 = 规则成立的层；灰点 = 实际测量的层；灰带 = 预注册里 H2 预测的“lens 读出名字”的 L57–61。</figcaption></figure>\n'
 '<div class="tw"><table><thead><tr><th>信息</th><th>最早出现（来源规则）</th><th>更严的阈值</th></tr></thead><tbody>\n'
 '<tr><td>标题位置的年份 / 引用数 / 领域（M2 probe）</td><td>≤ L16（年份 R² 0.383 [0.362, 0.403]）</td><td>引用数比 BERT 高 0.10 以上从 L24（只作参考）</td></tr>\n'
 '<tr><td>作者首 token（E4b probe，标题位置）</td><td>≤ L16（+0.041 [0.028, 0.054]）</td><td>target − control 从 L24（+0.052 [0.017, 0.089]）</td></tr>\n'
 '<tr><td>第一作者（X4 patchscope，标题位置）</td><td>≤ L8（+0.046 [0.035, 0.059]）</td><td>可能来自标题文字（见 X4）</td></tr>\n'
 '<tr><td>年份（X4 patchscope）</td><td>L40（+0.013 [0.008, 0.018]）</td><td>领域：没有一层可读出</td></tr>\n'
 '<tr><td>改写的意思超出用词（X3）</td><td>≤ L8（起始层不稳健，敏感性 L24）</td><td>主要在 L28–L40</td></tr>\n'
 '<tr><td>论文身份（M3 身份指数）</td><td>没有：从不高于 L4</td><td>—</td></tr>\n'
 '<tr><td>替换恢复（X6，标题之后的 token）</td><td>≤ L24</td><td>R ≥ 0.5 在 L48（0.821），R ≥ 0.95 在 L52（0.995）</td></tr>\n'
 '<tr><td>阻断损失（X7，还需要标题的最后一层）</td><td>L54（target L52，control L54）</td><td>S ≤ 0.05 从 L52</td></tr>\n'
 '<tr><td>名字位置的 lens 读出（Stage 10，target − control）</td><td>logit lens ≤ L24 但极小（+0.007）；J-lens L57</td><td>≥ 0.05：logit lens L56，J-lens L58</td></tr>\n'
 '<tr><td>作者提示 lens（Stage 12 F2，名字位置）</td><td>L62</td><td>—</td></tr>\n'
 '</tbody></table></div>\n'
 '<p><b>层序</b>：标题位置的论文属性和作者首 token 在第一个测到的层（≤ L8–L16）就能读出；论文信息在 L48–L52 汇集到标题之后的 token（替换在 L48 恢复一半、L52 恢复 95% 以上，从 L52 起阻断对标题的注意力已几乎没有损失）；名字位置用 lens 读出作者要到 L53–L62。这与“读得早，说得晚”一致。</p>\n'
 '<p class="note">限定：M3 的身份指数从不高于 L4，所以没有“论文身份”出现的层；预注册写的“跨任务检索 top-1”曲线没有计算（与预注册的出入）。X3 不能区分语义与论文身份，起始层不稳健；X4 L8 的作者信号可能来自标题文字；Stage 10 lens 在严格规则下 L24 起的信号极小，0.05 是 Stage 10 的“约为 0”惯例，不是预注册阈值；E4b 为论文 bootstrap、F2 为 Stage 12 的 bootstrap，其余为团队整群区间。</p>\n'
 '</section>\n\n')
R = [
('<a href="#x3-results">X3 结果</a> · ', '<a href="#x3-results">X3 结果</a> · <a href="#x5-results">X5 层序</a> · '),
('“:” 位置上各版本的余弦在 L4–L8 都接近 1，差距只有约 0.002，不作解读。</p>\n</section>\n\n', '“:” 位置上各版本的余弦在 L4–L8 都接近 1，差距只有约 0.002，不作解读。</p>\n</section>\n\n' + X5),
('<td>M3 + X4 + 已有数据；CPU</td><td>等 M3、X4</td></tr>', '<td>M3 + X4 + 已有数据；CPU</td><td><b>已完成（2026-11-02），见上文 X5</b>；跨任务检索 top-1 曲线未计算</td></tr>'),
('更新于 2026-11-02（第 24 版）', '更新于 2026-11-02（第 25 版，答辩定稿）'),
]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:60]); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('applied', len(R))
