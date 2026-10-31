"""Report v21 (2026-10-30 evening, user items 1 and 6): authors 1-20, E4b training-fold standardisation, M2 team-cluster
intervals, X4 token-role split + text baseline + approved wording, H3 result cell. Every anchor must occur exactly once."""
import os, shutil
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p = 'stage1_11_report.html'
if not os.path.exists('stage1_11_report.v20.html'): shutil.copy2(p, 'stage1_11_report.v20.html')
s = open(p, encoding='utf-8').read()
SRC = lambda x: f'<span class="mono">{x}</span>'
R = [
# authors 1-20
('去掉没有作者或作者 ≥ 20 位的记录',
 '去掉没有作者或作者超过 20 位的记录（保留 1–20 位；代码中 MAX_AUTHORS = 20，只去掉 &gt; 20 位；此前写成“≥ 20”有误，2026-10-30 据 Dreaming Up Authors 代码包核对）'),
('no records with zero or ≥ 20 authors',
 'no records with zero or more than 20 authors (1–20 kept; MAX_AUTHORS = 20 drops only &gt; 20; the earlier "≥ 20" was wrong, checked against the Dreaming Up Authors code package on 2026-10-30)'),
# E4b in 6.11
('L24 约 +0.05，L40 约 +0.07，L56 约 +0.08；目标组比对照组高 +0.04 到 +0.08（L24–L60，置信区间在 0 以上）。',
 'L24 约 +0.05，L40 约 +0.06，L56 约 +0.08（+0.050 / +0.061 / +0.075）；目标组比对照组高 +0.03 到 +0.08（L24–L60，置信区间在 0 以上，L44 下界 +0.000 在边界上）。'
 '这是 2026-10-30 改为<b>只在训练折内拟合标准化</b>后的数字：原来的标准化用了全部论文（含测试折，'
 + SRC('stage10_extra_r0r1.py:244') + '）；改后最大变化 0.0075，正则化强度不变，没有任何区间从“不含 0”变成“含 0”（'
 + SRC('381_stage13/reports/e4b_trainstd_compare.md') + '，作业 11500917）。'),
('about +0.05 at L24, +0.07 at L40 and +0.08 at L56, with target above control by +0.04 to +0.08 (CIs above zero).',
 'about +0.05 at L24, +0.06 at L40 and +0.08 at L56 (+0.050 / +0.061 / +0.075), with target above control by +0.03 to +0.08 (CIs above zero; the L44 lower bound is +0.000). These use standardisation fitted on the training folds only (2026-10-30); the original standardised over all papers including the test fold. Largest change 0.0075, no CI changes whether it contains 0.'),
# E4b review box
('与普通 probe 相当或略低，不再更强。原来那个“更强”来自泄漏：同一个借出标题同时在训练和测试里。§6.12 的这一句需要改写。</li>\n</ul></div>',
 '与普通 probe 相当或略低，不再更强。原来那个“更强”来自泄漏：同一个借出标题同时在训练和测试里。§6.12 的这一句需要改写。</li>\n'
 '<li><b>2026-10-30 更新：标准化只在训练折内拟合。</b>上面的数字用全部论文（含测试折）算均值和标准差。改为只用训练折后（作业 11500917），全部论文平均 L24 +0.050、L40 +0.061、L56 +0.075；目标组 − 对照组 L24–L60 为 +0.035 到 +0.078，L44 下界变为 +0.000（边界）。最大变化 0.0075，正则化强度不变，没有结论翻转。正文 §6.11 已改用新值。'
 + SRC('381_stage13/reports/e4b_trainstd_compare.md') + '</li>\n</ul></div>'),
# M2 team CI
('<li>“:” 位置的年份 R² 达 0.98，这是泄题，只作阳性对照。</li>',
 '<li>“:” 位置的年份 R² 达 0.98，这是泄题，只作阳性对照。</li>\n'
 '<li><b>按作者团队整群的区间（2026-10-30，作业 11503585）：</b>176 个点估计与原结果完全一致；区间平均宽 1.15 倍（真标题 1.02，false_0 1.32），没有任何一行从“不含 0 / 高于随机水平”变为相反。只用年份的基线也补了区间，例如“是否认得出”AUROC 0.555 [0.534, 0.573]。'
 + SRC('381_stage13/reports/m2_teamci.md') + '</li>'),
# X4 role split + wording
('年份没有这种差别。</p>\n</section>',
 '年份没有这种差别。</p>\n'
 '<h4>X4 第一作者 L8：按 token 角色拆开，并与纯文本基线比较（2026-10-30）</h4>\n'
 '<p>原结果只存了名字各 token 的平均分，所以按 token 重新打分（作业 11500437）。用原来的批大小重算，4,712 个值与原分数完全相同；换一种批大小，L8 平均 D 为 +0.0490 对 +0.0484，只差 0.0006，批大小不影响结论。'
 + SRC('381_stage13/summary_x1x4/x4_rolesplit.csv') + '</p>\n'
 '<div class="tw"><table><thead><tr><th>第一作者名字的 token</th><th>篇数</th><th>Qwen L8 的 D</th><th>Qwen L40 的 D</th><th>纯文本基线（BERT）</th></tr></thead><tbody>\n'
 '<tr><td>姓的第一个 token</td><td>1,178</td><td>+0.066 [0.045, 0.088]</td><td>+0.124 [0.099, 0.148]</td><td>阳性对照未通过，不可比</td></tr>\n'
 '<tr><td>名的第一个 token（完整的名）</td><td>357</td><td>+0.018 [−0.003, 0.041]</td><td>+0.058 [0.035, 0.083]</td><td>+0.088 [0.020, 0.156]</td></tr>\n'
 '<tr><td>首字母</td><td>880</td><td>+0.017 [0.006, 0.029]</td><td>+0.027 [0.016, 0.036]</td><td>—</td></tr>\n'
 '</tbody></table></div>\n'
 '<p><b>结论（2026-10-30，用户确认的措辞）：</b>在阳性对照通过的名字首 token 上（357 篇），纯文本基线（BERT）的自身优势（均值/标准差 0.13）不小于 Qwen 在同一 token 上的信号（L8 +0.018，0.09，区间含 0），两者逐篇几乎不相关（r = 0.07）。Qwen L8 的信号主要来自姓的首 token（+0.066 [0.045, 0.088]），而姓氏上文本基线的阳性对照没有通过，因此<b>不能排除</b> L8 的作者信号可以由标题文字解释。</p>\n'
 '</section>'),
# H3 table: add a result column
('<th>M3：换任务对照</th></tr></thead><tbody>', '<th>M3：换任务对照</th><th>目前结果（2026-10-30）</th></tr></thead><tbody>'),
('<td>同一标题在不同问题下，中间层表示早早分开</td></tr>', '<td>同一标题在不同问题下，中间层表示早早分开</td><td>见上文 M3、X1 结果</td></tr>'),
('<td>不同问题下同一篇论文的表示在中间层相近，后期才按任务分开</td></tr>', '<td>不同问题下同一篇论文的表示在中间层相近，后期才按任务分开</td><td>见上文 M3、X1 结果</td></tr>'),
('<td>按作者训练的 probe 能跨任务迁移；作者专用 lens（M4）在中间层读得出名字</td></tr>',
 '<td>按作者训练的 probe 能跨任务迁移；作者专用 lens（M4）在中间层读得出名字</td><td><b>文本基线不弱于 Qwen，不能排除文字解释</b>（X4：名字首 token 上 BERT +0.088 ≥ Qwen L8 +0.018；L8 信号主要在姓上，见上文 X4）</td></tr>'),
]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:60]); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('applied', len(R))

# X3 status (applied separately after the first run of this script)
s = open(p, encoding='utf-8').read()
a = '<td>生成已排队；正式运行等人工抽查（logs/para_ok）</td>'
b = ('<td>生成已完成（1,186 条）。2026-10-30 写定预注册补充 5（'
     '<span class="mono">381_stage13/config/prereg_addendum5.json</span>，sha256 181c72f7…b113ab）：主分析纳入通过自动检查且与原标题不完全相同的 1,115 条；'
     '敏感性分析再剔除 NLI 双向未通过和人工标为“改意思”的，剩 1,015 条；词重合度改用修正版 Jaccard（去停用词、任意长度、简单词形还原），近邻 D 按它重选；'
     'Qwen 判断器 v2 一致率 0.55 &lt; 0.80，不用。40 条人工标注中“改意思” 6 条，0.15 [0.07, 0.29]（Wilson 95%），“边界” 7 条，0.175 [0.09, 0.32]。'
     '正式运行先跑 1 个分片核对，再放行其余。</td>')
if s.count(a) == 1: s = s.replace(a, b); open(p, 'w', encoding='utf-8').write(s); print('X3 status applied')
else: print('X3 status anchor count', s.count(a))
sed -i 's/更新于 2026-10-28/更新于 2026-10-30（第 21 版）/' stage1_11_report.html  # applied 2026-10-30
