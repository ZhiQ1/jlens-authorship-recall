"""Report v28 (2026-11-05 evening, user decisions of ~17:20): group-comparison results (approved wording, finding 3 layer wording),
addendum-8 re-run results with numerator / denominator, P1/P2 placeholder (post_defence_v28.html); X2 results section (approved wording);
hypotheses table H2/H3 cells; overview box; X2 status in the Stage 13 plan table.
Input: v27 = backup stage1_11_report.before_20261105c.html (made from stage1_11_report.html on the first run). Usage: python edit_v28.py [out]"""
import os, sys, re, base64, csv, html, shutil
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11'; os.chdir(D)
SRC = 'stage1_11_report.html'; OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
BK = 'stage1_11_report.before_20261105c.html'
if not os.path.exists(BK): shutil.copy2(SRC, BK)
s = open(BK, encoding='utf-8').read(); assert '第 27 版' in s


def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:70]); s = s.replace(a, b)


rep('更新于 2026-11-05（第 27 版：Stage 1–13；答辩后新增见第五部分；正文数字后的灰色小字是出处）',
    '更新于 2026-11-05（第 28 版：Stage 1–13；答辩后新增见第五部分，含分组对比结果和 X2；正文数字后的灰色小字是出处）')

# ---- overview box
rep("① 分组对比（A/B/C/D 等，分析计划在看结果前写定，补充 7、8）：CPU 部分已算完，结果先交用户审阅；R2 和识别不确定组的干预重跑、E1 分子/分母分解还在进行，确认之前本报告不写结果数字。",
    '① 分组对比（分析计划在看结果前写定，补充 7、8）：在模型没写出的作者上，认得出的论文比认不出的高 +0.200 [0.188, 0.213]'
    '<span class="src">（分组对比 P1 A − B，R0，真标题 − 5 个假标题平均，最终输出 L63，A 3,417 / B 2,148 篇，引用档内差，团队聚类 95% CI；391_groups/primary.csv）</span>；'
    '多选题每多答对一种选项顺序，信号高 +0.059 [0.056, 0.063]<span class="src">（P3，R0 论文 8,288 篇，斜率，引用档固定效应；primary.csv）</span>；'
    '写对一部分作者对没写出的合作者只多 +0.061 [0.034, 0.090]<span class="src">（P2-other C − A，C 390 / A 2,826 篇；primary.csv）</span>。'
    '干预重跑显示 B 的恢复比例较高只是分母小（真假差距 B 0.214、A 0.407<span class="src">（E1 分母，B 586 / A 557 篇；391_groups/reports/e1_num_den.md）</span>），识别程度改变信号大小、不改变时间。')
rep('③ 进行中：X2（补充 6）、全部名字 token 的标题位置 probe（补充 9）、分组重跑（补充 8）。',
    '③ X2 子空间替换（补充 6）已完成：按预注册判据 H3 通过、H2 不支持，但作者子空间几乎解码不出作者，不能作为 H3 的有力证据（第四部分 X2）。进行中：全部名字 token 的标题位置 probe（补充 9）。')
rep('<a href="#pd-running">进行中（X2、全部 token 的 probe、分组重跑）</a>', '<a href="#pd-running">进行中（全部 token 的 probe）</a>')
rep('<a href="#pd-groups">分组对比（A/B/C/D 等）</a>', '<a href="#pd-groups">分组对比（A/B/C/D 等）与干预重跑</a>')
rep('<a href="#x5-results">X5 层序</a>', '<a href="#x2-results">X2 结果</a> · <a href="#x5-results">X5 层序</a>')

# ---- X2 section (before X5)
T = '<span class="src">（{}）</span>'
X2 = f'''<section id="x2-results"><h2><span class="st">Stage 13 · X2</span><span class="ln lC">C 哪一层</span> 只替换子空间：论文属性方向还是作者方向带着作者信息？</h2>
<p class="note">2026-11-05 完成，24 个 GPU 分片（作业 11637663、11654745、11655027），分析作业 11655257。规则：预注册补充 6（<span class="mono">381_stage13/config/prereg_addendum6.json</span>，sha256 5eea3c4a…）。配对与 X1 相同：标题等长的 1,178 对（调参集 596、测试集 582）{T.format('381_stage13/reports/x2_report.md 首段')}；区间为作者团队聚类 bootstrap 95% CI（2,000 次）。报告：<span class="mono">381_stage13/reports/x2_report.md</span>、<span class="mono">summary_x2/</span>。分数是教师强制下第一作者名字 token 的打分，不是生成。</p>
<p><b>做法。</b>在 L16、L24、L32、L40、L48 各层，用不属于任何配对团队的 5,041 篇训练论文{T.format('X2 子空间拟合，x2_report.md “Subspace fits” 表 n train 列')}拟合两个子空间：S_id 是年份、引用数、领域的 ridge 读出方向（9 维），S_auth 是预测第一作者首 token 反嵌入的方向（10 维）；另取 3 个随机 10 维子空间作对照（S_rand）。<b>搬运（carry）</b>：在 B 的作者提示里，只把标题位置状态在 S 上的分量换成 A 的，看 A 的第一作者分数恢复多少（R_S；完整替换 R_full 是上限，即 X1）。<b>移除（remove）</b>：把 A 自己提示里的 S 分量设为训练均值，看损失多少（L_S）。在调参集上选层，测试集上确认。</p>
<div class="tw"><table><thead><tr><th>子空间</th><th>调参集选的层</th><th>测试集 R_S</th><th>R_rand</th><th>R_full</th><th>R_S − R_rand [95% CI]</th><th>移除臂 L_S − L_rand [95% CI]</th></tr></thead><tbody>
<tr><td>S_id（论文属性，9 维）</td><td>L40</td><td>+0.005</td><td>+0.003</td><td>+0.920</td><td>+0.002 [−0.001, +0.005]</td><td>+0.001 [−0.003, +0.005]</td></tr>
<tr><td>S_auth（作者，10 维）</td><td>L48</td><td>+0.018</td><td>+0.003</td><td>+0.428</td><td>+0.015 [+0.010, +0.020]</td><td>+0.001 [−0.004, +0.006]</td></tr>
</tbody></table></div>
<p class="note">表 X2.1 来源：<span class="mono">381_stage13/reports/x2_report.md</span> “Verdict” 表（测试集 582 对）；逐层数字见 <span class="mono">summary_x2/x2_curves.csv</span>、<span class="mono">x2_diffs.csv</span>。</p>
<p><b>预注册判定。</b>H2（S_id 带得过去，且 R_id ≥ 0.5 × R_full）：L40 上 R_id 为 +0.005，而 0.5 × R_full 为 +0.460{T.format('X2 测试集 582 对，L40；x2_report.md Verdict 段')}，不支持。H3（S_auth 带得过去，且 R_auth − R_id &gt; 0）：L48 上 R_auth − R_id 为 +0.014 [+0.008, +0.020]{T.format('X2 测试集 582 对，L48，团队聚类 95% CI；x2_report.md Verdict 段')}，按规则通过。移除臂上两个子空间的损失都与随机子空间分不开{T.format('测试集 L_S − L_rand：S_id +0.001 [−0.003, +0.005]、S_auth +0.001 [−0.004, +0.006]；表 X2.1')}。</p>
<p><b>结论（用户 2026-11-05 确认的措辞）：</b>按预注册判据，H3 通过、H2 不支持。但作者子空间本身几乎解码不出作者（留出 R² ≤ 0.003{T.format('S_auth 作者映射在训练论文上 5 折团队留出 R²，L16–L48 为 0.0009–0.0033；x2_report.md “Subspace fits” 表；summary_x2/fit_sanity.csv')}，第一作者名字 token 猜中率 0.078–0.079{T.format('同表 “author top-1” 列，L16–L48 各层 0.078–0.079')}，低于常数基线 0.080{T.format('同表括号内 majority 基线')}），它搬动的量只有完整替换的约 4%{T.format('L48 测试集 R_auth 0.018 ÷ R_full 0.428 ≈ 0.042；表 X2.1')}，因此不能作为 H3 的有力证据。从标题传到作者名字的信息，几乎全部分散在这两个子空间之外。</p>
<p>补充：论文属性子空间本身读得出属性（留出年份 R² 0.36–0.52、引用数 R² 0.26–0.49、领域准确率 0.68–0.71{T.format('S_id 拟合，L16–L48，5 折团队留出；x2_report.md “Subspace fits” 表')}），但几乎搬不动作者信息：问题不在于方向没拟合好，而在于作者信息不在这些方向上。</p>
<p class="note">与预注册的出入：① X2 的 H3 判定按规则通过，但因子空间本身无解码能力而降级，与 X3 的处理方式相同。② S_id 只有 9 维而不是 10 维：同一个 ridge alpha 下 8 个领域方向之和恰为 0，年份 + 引用数 + 8 个领域只张成 9 维，去掉相关的一个方向；与 10 维随机子空间比较时，对 S_id 略偏保守。③ “调参集选层”取 R_S − R_rand 最大的层（沿用 X1 的选层规则）；“两者都不带”在调参集和测试集的搬运臂上检查。④ 移除臂的 S_full（标题位置全设为均值）只作参照，补充 6 只为搬运臂定义了 S_full。⑤ ridge 采用 Stage 13 probe 的约定（训练行上标准化、alpha × trace/d、带截距），读出向量映射回原始残差坐标后再正交化；alpha 按目标族（年份、引用数、领域、作者映射）用 5 个团队折的留出 MSE 选。⑥ 自检（只记 WARN）：S = 0 的恒等替换在 GPU 上不是逐位相同（最大差 0.103，bf16 批量舍入），3 个随机子空间之间只有搬运臂 L24 一处差 +0.003 [+0.001, +0.006]{T.format('x2_report.md “Checks” 与 “Deviations from addendum 6”')}。</p>
</section>
'''
rep('<section id="x5-results">', X2 + '<section id="x5-results">')

# ---- hypotheses table cells + overall paragraph
rep('另外，X4 最早可解码的顺序是第一作者（L8）早于年份（L40），与 H2 预测的方向相反。</td></tr>',
    '另外，X4 最早可解码的顺序是第一作者（L8）早于年份（L40），与 H2 预测的方向相反。<b>X2 不支持。</b></td></tr>')
rep('L8 信号主要在姓上，见上文 X4）</td></tr>', 'L8 信号主要在姓上，见上文 X4）；<b>X2 按规则通过但子空间无解码能力，证据仍不足</b></td></tr>')
rep('<th>目前结果（2026-11-01）</th>', '<th>目前结果（2026-11-05）</th>')
rep('M3 不支持，X3 不能区分语义与论文身份，X4 的顺序与 H2 预测相反。</p>',
    'M3 不支持，X3 不能区分语义与论文身份，X4 的顺序与 H2 预测相反，X2 不支持（2026-11-05）。H3：X2 按规则通过，但作者子空间几乎解码不出作者，证据仍不足。</p>')
# X2 row of the Stage 13 plan table: status cell
i = s.index('<tr><td>X2 只替换子空间（因果）</td>'); j = s.index('</tr>', i)
row = s[i:j]; k = row.rindex('<td>'); s = s[:i] + row[:k] + '<td>2026-11-05 完成（补充 6），见上文 <a href="#x2-results">X2</a></td>' + s[j:]

# ---- Part 5 replaced by the v28 fragment
G = '/scratch/zhang.zhiqi2/jlens/391_groups'
frag = open('src/post_defence_v28.html', encoding='utf-8').read()
for key, fn in [('{{FIG2}}', 'fig2_signal_vs_mc.png'), ('{{FIG3}}', 'fig3_primary_contrasts.png')]:
    frag = frag.replace(key, 'data:image/png;base64,' + base64.b64encode(open(f'{G}/figures/{fn}', 'rb').read()).decode())
rows = list(csv.reader(open(f'{G}/summary_table.csv', encoding='utf-8')))
HEAD_ZH = ['组', '输出层信号，未写出作者（L63）', '输出层信号，写出的作者（参照）', 'E1 替换恢复 L48（未写出）', 'E1 替换恢复 L52（未写出）',
           'E2 阻断损失 L52（未写出）', 'E4b probe 标题特异 L40（每篇，全部作者；只打分第一个名字 token）',
           'M2“认得出”AUROC（对 B，“:” L52，描述）', 'X3 行为恢复，测试集（第一作者未写出）']
t = ['<div class="tw"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in HEAD_ZH) + '</tr></thead><tbody>']
OVR = {'U0': {3: '+0.844 [+0.814, +0.877]; n = 599 (2096 authors)', 4: '+1.000 [+0.988, +1.012]; n = 599 (2096 authors)', 5: '+0.003 [-0.009, +0.014]; n = 599 (2096 authors)'},
       'R2s': {3: '+0.792; n = 28; 参照，不给区间', 4: '+1.027; n = 28; 参照，不给区间', 5: '-0.017; n = 28; 参照，不给区间'}}   # 391_groups/summary_rerun/rerun_group_values.csv (E1 L48/L52 recovery, E2 L52 loss, unwritten)
for r in rows[1:]:
    for ci, v in OVR.get(r[0], {}).items(): r[ci] = v
for r in rows[1:]: t.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in r) + '</tr>')
t.append('</tbody></table></div>')
frag = frag.replace('{{SUMMARY_TABLE}}', '<p class="note">表 P5.1 各组汇总</p>\n' + '\n'.join(t))
assert '{{' not in frag
i = s.index('<div class="partbar" id="p5">'); s = s[:i] + frag.strip() + '\n'
assert not re.search('minyan', s, re.I) and '出处文件未找到' not in s
open(OUT, 'w', encoding='utf-8').write(s); print('wrote', OUT, len(s))
