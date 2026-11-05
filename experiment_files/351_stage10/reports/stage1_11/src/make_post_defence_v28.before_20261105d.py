"""post_defence_v28.html = post_defence_v27.with_group_results.html + finding-3 layer wording (user 2026-11-05 17:20)
+ addendum-8 re-run results + P1/P2 placeholder + updated in-progress list."""
from pathlib import Path
D = Path(__file__).parent
s = (D / 'post_defence_v27.with_group_results.html').read_text(encoding='utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
# finding 3: layer-specific wording (values: 391_groups/stage10_contrasts.csv, unwritten_other, P2 C - A by layer)
i = s.index('这一差别从 L48 到 L62 都约为 0'); j = s.index('只在最终输出出现。', i) + len('只在最终输出出现。')
s = s[:i] + ('logit lens 下 L48–L62 约为 0<span class="src">（P2-other C − A 按层，logit lens L48–L62，未写出的合作者：−0.019 到 +0.035，团队聚类 95% CI 都含 0；'
             '391_groups/stage10_contrasts.csv “unwritten_other, P2 C - A (by layer)”）</span>；公开 J-lens 下 L48–L59 为 −0.07 到 −0.11'
             '<span class="src">（同一比较，public J-lens：L48 −0.084、L53 −0.073、L57 −0.107、L59 −0.077，团队聚类 95% CI 都在 0 以下；L60 −0.038（CI 含 0）、L62 +0.038；同一文件）</span>。') + s[j:]
s = s.replace('<h3>三个主要发现（用户 2026-11-05 确认的措辞）</h3>', '<h3>三个主要发现（用户 2026-11-05 确认的措辞；发现 3 的分层表述按用户 2026-11-05 17:20 的修改）</h3>')
# summary table note: U0 / R2s intervention cells come from the re-runs below
rep('n &lt; 30 篇的格只作描述。</p>', 'n &lt; 30 篇的格只作描述。U0 和 R2s 的 E1 / E2 格在汇总表生成时还没有数据（“not available”），重跑结果见下一节。</p>')
# re-run block replaces the "still running" box
i = s.index('<div class="bx"><b>还在进行（补充 8'); j = s.index('</div>', i) + 6
RR = '''<h3>补充 8 的干预重跑：分子、分母与识别程度</h3>
<p class="note">R2 × strong 204 篇（E1、E2、P1、P2）与 R0 × uncertain 600 篇（E1、E2）已在 GPU 上跑完，与 Stage 11 原样本（A、B、C、D）一起只按模型没写出的作者汇总。E1 恢复比例 R = mean(替换 − 假标题) ÷ mean(真标题 − 假标题)：分子是替换后恢复的绝对量，分母是这组论文真假标题的差距。区间为作者团队聚类 bootstrap 95% CI。出处：<span class="mono">391_groups/reports/rerun_report.md</span>、<span class="mono">e1_num_den.md</span>、<span class="mono">summary_rerun/*.csv</span>。</p>
<ul>
<li><b>B 的恢复比例更高，是分母小造成的。</b>分母（真标题 − 假标题）：A 0.407、B 0.214、U0 0.293、C 0.464<span class="src">（补充 8 / Stage 11，E1，未写出作者，最终输出，mean(真 − false_0)；A 557、B 586、U0 599、C 32 篇；391_groups/reports/e1_num_den.md E1 表 denominator 列）</span>。分子 B − A 在 L24、L40、L48、L52 分别为 −0.010、−0.040、−0.144、−0.184，区间都在 0 以下<span class="src">（E1 分子 B − A，配对团队 bootstrap 95% CI：L24 [−0.015, −0.004]、L40 [−0.052, −0.028]、L48 [−0.169, −0.119]、L52 [−0.213, −0.154]；391_groups/summary_rerun/e1_e2_num_den_B_minus_A.csv）</span>。B 的比值较高（L48 B 0.869、A 0.811<span class="src">（E1 R(L48)，A 557 / B 586 篇；e1_num_den.md）</span>），只是因为分母约为 A 的一半（B/A 0.53<span class="src">（同上文件 “B/A denominator”）</span>）。在任何一层，B 携带的论文特有绝对信号都不比 A 多。E2 阻断的分子同样是 B 小于 A（L24–L48 为 A 的 0.49–0.59 倍<span class="src">（E2 分子 B/A；e1_e2_num_den_B_minus_A.csv）</span>）。</li>
<li><b>识别程度改变信号的大小，不改变时间。</b>R0 论文按多选题答对的选项顺序数从 0 到 4，分母从 0.185 升到 0.407<span class="src">（R0 论文 A + U0 + B，E1 真 − false_0，未写出作者；0 种对 241 篇、4 种对 557 篇；391_groups/reports/rerun_report.md “Continuous recognition within R0” 表）</span>，而 E1 R(L48) 基本持平，从 0.90 到 0.81<span class="src">（同表 L48 列：0.904 [0.848, 0.965] → 0.811 [0.790, 0.832]）</span>。</li>
<li><b>识别不确定的 R0 论文（U0）时间点与 A、B 相同（描述）。</b>U0 的 R(L48) 0.844、R(L52) 1.000<span class="src">（E1，U0 599 篇，团队 CI [0.814, 0.877] / [0.988, 1.012]；rerun_report.md E1 表）</span>；A 为 0.811 / 0.988，B 为 0.869 / 1.016<span class="src">（同表）</span>。</li>
<li><b>R2 只作上限参照。</b>R2 写出的作者真假差距 0.845<span class="src">（R2 × strong 写出的作者，200 篇，E1 分母 [0.798, 0.897]；e1_num_den.md）</span>。C 只有 32 篇、D 5 篇、R2 中有未写出作者的论文 28 篇<span class="src">（rerun_report.md Counts 表，papers_unwritten 列）</span>，都只作描述，不下结论。</li>
</ul>
<div class="tw"><table><thead><tr><th>组（未写出作者）</th><th>篇数</th><th>分母：真 − 假标题</th><th>E1 分子 L48</th><th>E1 R(L48)</th><th>E1 分子 L52</th><th>E1 R(L52)</th></tr></thead><tbody>
<tr><td>A（R0 × 认得出）</td><td>557</td><td>+0.407 [0.386, 0.430]</td><td>+0.330</td><td>+0.811 [0.790, 0.832]</td><td>+0.402</td><td>+0.988 [0.980, 0.996]</td></tr>
<tr><td>B（R0 × 认不出）</td><td>586</td><td>+0.214 [0.196, 0.234]</td><td>+0.186</td><td>+0.869 [0.835, 0.906]</td><td>+0.218</td><td>+1.016 [1.002, 1.031]</td></tr>
<tr><td>U0（R0 × 不确定）</td><td>599</td><td>+0.293 [0.271, 0.316]</td><td>+0.248</td><td>+0.844 [0.814, 0.877]</td><td>+0.293</td><td>+1.000 [0.988, 1.012]</td></tr>
<tr><td>C（R1 × 认得出，描述）</td><td>32</td><td>+0.464 [0.388, 0.538]</td><td>+0.335</td><td>+0.721 [0.650, 0.806]</td><td>+0.462</td><td>+0.996 [0.968, 1.026]</td></tr>
<tr><td>R2 写出的作者（参照）</td><td>200</td><td>+0.845 [0.798, 0.897]</td><td>+0.566</td><td>+0.670 [0.630, 0.707]</td><td>+0.801</td><td>+0.948 [0.927, 0.965]</td></tr>
</tbody></table></div>
<p class="note">表 P5.2 来源：<span class="mono">391_groups/reports/e1_num_den.md</span>（E1 表，<span class="mono">summary_rerun/e1_e2_num_den.csv</span>）；D（5 篇）和 R2 中未写出的作者（28 篇）见原表，只作描述。</p>
<h3 id="pd-p1p2-numden">P1 / P2 按组的分子与分母（计算中）</h3>
<p class="note">P1（只替换单个位置）和 P2（注意力 / MLP）按组的分子 / 分母拆分正在计算，结果出来后补入本节。</p>
'''
s = s[:i] + RR + s[j:]
# in-progress list
i = s.index('<li><b>X2 子空间替换（补充 6'); j = s.index('</li>', i) + 5
s = s[:i] + '<li><b>X2 子空间替换（补充 6）：</b>已完成，结果见第四部分 <a href="#x2-results">X2</a>。</li>' + s[j:]
rep('<li><b>分组干预重跑（补充 8）：</b>见上文“还在进行”。</li>', '<li><b>分组干预重跑（补充 8）：</b>E1 / E2 已完成（见上文）；P1 / P2 按组的分子 / 分母拆分正在计算。</li>')
rep('需要一步 GPU 数据（约 1 个 A100 小时），排在分组重跑和 X2 之后。尚无结果。', '需要一步 GPU 数据（约 1 个 A100 小时）。尚无结果。')
assert 'minyan' not in s.lower()
(D / 'post_defence_v28.html').write_text(s, encoding='utf-8'); print('ok', len(s))
