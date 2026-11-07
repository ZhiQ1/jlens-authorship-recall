"""Report v29 (2026-11-06, redo programme, addenda 9-13; user-approved wording): X7 with five false titles; Stage 8 CPU proxy (C-2);
Stage 7.1 claim with a title contrast (C-1); M1 with five false titles (C-4); Stage 10 extras at every stored layer (C-5);
all-token title-position probe (addendum 9) + no-exclusion sensitivity (C-3); caveat boxes -> pointer; limitations that cannot be redone;
Part 5: redo programme status with placeholders for batch-1 items still running. Stale statements fixed.
Input = backup stage1_11_report.before_20261106.html (= v28). Usage: python edit_v29.py [out]"""
import os, sys, re, shutil
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11'; os.chdir(D)
SRC = 'stage1_11_report.html'; OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
BK = 'stage1_11_report.before_20261106.html'
if not os.path.exists(BK): shutil.copy2(SRC, BK)
s = open(BK, encoding='utf-8').read(); assert '第 28 版' in s


def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:70]); s = s.replace(a, b)


def ins_before(anchor, block):
    rep(anchor, block + anchor)


T = lambda t: f'<span class="src">（{t}）</span>'
E = lambda t: f'<span class="src">({t})</span>'
R13 = '381_stage13/reports/'

rep('更新于 2026-11-05（第 28 版：Stage 1–13；答辩后新增见第五部分，含分组对比结果和 X2；正文数字后的灰色小字是出处）',
    '更新于 2026-11-06（第 29 版：Stage 1–13；答辩后新增见第五部分；补充 9–13 的重做结果已写入各节；正文数字后的灰色小字是出处）')

# ---------- overview box + TOC
rep('进行中：全部名字 token 的标题位置 probe（补充 9）。',
    '全部名字 token 的标题位置 probe（补充 9）已完成：L40 姓的第一个 token +0.071 [0.058, 0.085]'
    + T('补充 9，标题最后一个 token，probe 打分姓的第一个 token，真标题 − false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；' + R13 + 'e4b_alltok.md 第 5 节')
    + '，高于首字母 +0.044 [0.030, 0.057]' + T('同上，首字母，1,590 篇') + '（第四部分）。'
    '④ 重做计划（补充 10–13，2026-11-05/06 写定）：X7 补做另外 4 个假标题后三组都满足判据；Stage 8 的 CPU 代理、Stage 7.1 加标题对照等写在各节；批次 1 的其余项目还在运行（第五部分）。')
rep('<br><b>注意：</b>本报告里的标题位置 probe（E4b）只给每位作者名字的<b>第一个 token</b> 打分（多数是首字母）；全部 token、按角色分开的版本（补充 9）还在进行。',
    '<br><b>注意：</b>原 E4b 只给每位作者名字的<b>第一个 token</b> 打分（多数是首字母）；全部名字 token、按角色分开的版本见第四部分 <a href="#alltok-results">补充 9</a>。')
rep('<a href="#pd-running">进行中（全部 token 的 probe）</a>', '<a href="#pd-running">重做计划与批次 1</a> · <a href="#pd-limits">不能补做的局限</a>')
rep('<a href="#x2-results">X2 结果</a>', '<a href="#x2-results">X2 结果</a> · <a href="#alltok-results">全部名字 token 的 probe（补充 9）</a>')

# ---------- caveat boxes -> pointer to the all-token section
PZ = ('<b>原 E4b 只给每位作者名字的第一个 token 打分</b>（多数是首字母）。覆盖全部名字 token、按首字母 / 名 / 姓分开的版本（补充 9，已完成）见第四部分 '
      '<a href="#alltok-results">全部名字 token 的标题位置 probe</a>：L40 姓的第一个 token +0.071 [0.058, 0.085]'
      + T('补充 9，目标 + 对照 1,395 篇，团队聚类 95% CI；' + R13 + 'e4b_alltok.md') + '，名的第一个 token +0.124'
      + T('同上，L40，1,706 篇') + '。')
PE = ('<span class="en">E4b scores only the first name token (mostly an initial). The all-token, by-role version (addendum 9, done) is in Part 4: '
      'surname first token at L40 +0.071 [0.058, 0.085]' + E('addendum 9, 1,395 target + control papers, team CI; e4b_alltok.md') + '.</span>')
n_cav = 0
def cav_sub(m):
    global n_cav; n_cav += 1
    return '<div class="cav">' + PZ + (PE if '<span class="en">' in m.group(0) else '') + '</div>'
s = re.sub(r'<div class="cav"><b>注意：这里的标题位置 probe（E4b）只给每位作者名字的第一个 token 打分</b>.*?</div>', cav_sub, s, flags=re.S)
assert n_cav == 8, n_cav

# ---------- C-1: Stage 7.1 claim with a title contrast
C1 = ('<b>2026-11-06 补（补充 13 C-1，事后）：</b>加上标题对照（真标题 − Stage 10 的 5 个匹配假标题）后，A−B 的差别在模型输出和 L62 上成立，public J-lens 多层平均不显著：'
      '名字其余 token 上，输出 +0.244 [0.087, 0.398]、logit lens L62 +0.278 [0.088, 0.483]、public J-lens L62 +0.317 [0.145, 0.506]，public J-lens 6 层平均 +0.077 [−0.021, +0.180]'
      + T('补充 13 C-1，Pilot50 20 对 A−B，Stage 10 原始分数，名字其余 token，配对 bootstrap 95% CI；' + R13 + 'c13_C1.md Pilot50 表 aa_cont 行') + '；全部 token 的 public J-lens 6 层平均 +0.065 [−0.026, +0.155]'
      + T('同表 aa_all 行') + '。')
rep('<div class="bx ok"><b>结论</b>A−B 差异主要在给出正确前缀之后的后续 token 上；第一个 token 不确定。这不能证明无提示的作者回忆。当时未能解释为什么后续 token 才有差异。</div>',
    '<div class="bx ok"><b>结论</b>原分析（无标题对照的 JMRR）：A−B 差异主要在给出正确前缀之后的后续 token 上；第一个 token 不确定。这不能证明无提示的作者回忆。当时未能解释为什么后续 token 才有差异。<br>' + C1 + '</div>')
rep('<td>A−B 差异在后续 token 上</td>', '<td>A−B 差异：加上标题对照后，在模型输出和 L62 上成立，public J-lens 多层平均不显著（补充 13 C-1）</td>')

# ---------- C-2: Stage 8 CPU proxy
C2 = ('<div class="bx"><b>2026-11-06 补：Stage 8 的 CPU 代理（补充 13 C-2，事后）</b>用 Stage 10 已有的原始分数，在 Stage 8 的 200 篇论文上重算冻结的多层终点：'
      '全部作者、全部名字 token 的版本中 RQ1 和 RQ2 都成立——public J-lens 6 层平均 RQ1 +0.130 [0.109, 0.153]'
      + T('补充 13 C-2，200 篇，标题特异信号（真标题 − Stage 10 的 5 个假标题），团队聚类 95% CI；' + R13 + 'c13_C2.md aa_all int6 行')
      + '，RQ2 +0.054 [0.008, 0.102]' + T('同上，100 对 A−B，配对 bootstrap 95% CI') + '；只看 L56 时 RQ2 +0.064 [−0.032, +0.163]，不显著'
      + T('同上，L56 行') + '。<strong>这是 CPU 代理，不是原 Stage 8 的统计量：</strong>它用 public J-lens 的名次指标和 Stage 10 的 5 个假标题，不是 Stage 8 的 W（真标题对 20 个错误标题的胜率）；'
      'GPU 上按原 W 重算没有做（用户 2026-11-06 决定）。</div>\n')
i = s.index('<section id="p1-s8">'); j = s.index('</section>', i)
s = s[:j] + C2 + s[j:]

# ---------- X7 five false titles (addendum 10 item 2)
X7 = ('<div class="bx ok"><b>2026-11-06 补做（补充 10 第 2 项）</b>X7 补做了另外 4 个假标题，按 5 个平均判定，target、control 和全部论文都满足预注册判据（S(L52) 分别为 +0.022'
      + T('X7 五个假标题平均，target 593 篇，S(L52) [0.015, 0.029]，团队聚类 95% CI；' + R13 + 'b1_x7f_report.md') + '、+0.042'
      + T('control 593 篇，[0.028, 0.055]') + '、+0.028' + T('全部 1,186 篇，[0.022, 0.035]') + '，均 ≤ 0.05）；原来对照组只用 false_0 时为 0.051'
      + T('summary_x7/x7_knockout.csv，补做时逐位复现') + '，属于单个假标题的波动。'
      + T('control 逐个假标题 S(L52)：0.051 / 0.035 / 0.048 / 0.033 / 0.041；同一报告') + '</div>\n')
i = s.index('<section id="x7-results">'); j = s.index('</section>', i)
s = s[:j] + X7 + s[j:]
rep('control 本来就差一点不成立（0.051）', 'control 只用 false_0 时差一点不成立（0.051；按 5 个假标题平均已成立，见下框）')

# ---------- C-4: M1 with five false titles
i = s.index('<li><b>真假标题对比：</b>'); j = s.index('</li>', i) + 5
s = s[:j] + ('<li><b>2026-11-06 补（补充 13 C-4）：</b>换成另外 4 个假标题，各读出、各层变化的比例与 false_0 平均只差 +0.26 个百分点（范围 −0.08 到 +0.64）'
    + T('补充 13 C-4，全部 149,999 个名字 token，47 个读出 × 层；' + R13 + 'c13_C4.md') + '，结论不变。</li>') + s[j:]

# ---------- C-5: Stage 10 extras at all stored layers (before 6.11)
C5 = ('  <div class="pair">\n    <p class="zh"><b>2026-11-06 补（补充 13 C-5，事后）：</b>§6.7–§6.9 的附加分析补到全部已存的层（public J-lens 与 logit lens 的 L50–L55、L57–L61），原有层逐位复现，结论不变'
      + T('补充 13 C-5，Stage 10 全部 9,108 篇；' + R13 + 'c13_C5.md；381_stage13/summary_c13/c5/all_layers/') + '。一处需要注意：public J-lens 下，后续 token 的目标 − 对照在 L48–L54 为负（−0.020 到 −0.050）'
      + T('Stage 10 后续 token 标题特异信号，引用档内目标 − 对照，论文 bootstrap 95% CI 都在 0 以下；c13_C5.md “X1 token position, jlens_public” 表') + '，从 L56 起转正（L56 +0.026，L62 +0.282）'
      + T('同表') + '；logit lens 从 L50 起为正' + T('同文件 logit 表，L50 +0.007 [0.000, 0.013]') + '。</p>\n'
      '    <p class="en"><b>Added 2026-11-06 (addendum 13 C-5, post hoc):</b> the extra analyses of §6.7–§6.9 were run at every stored layer (public J-lens and logit lens L50–L55, L57–L61); the original layers reproduce exactly and the conclusions are unchanged'
      + E('addendum 13 C-5; c13_C5.md') + '. Note: with the public J-lens, later-token target − control is negative at L48–L54 (−0.020 to −0.050) and positive from L56 (L56 +0.026, L62 +0.282)'
      + E('c13_C5.md, X1 token position, jlens_public') + '; the logit lens is positive from L50' + E('same file, logit') + '.</p>\n  </div>\n')
ins_before('<h3>6.11 Stage 11：干预', C5)

# ---------- all-token probe section (addendum 9), before X5
AT = f'''<section id="alltok-results"><h2><span class="st">Stage 13 · 补充 9</span><span class="ln lB">B 读出工具</span><span class="ln lD">D 名字</span> 全部名字 token 的标题位置 probe（按首字母 / 名 / 姓分开）</h2>
<p class="note">2026-11-05 完成（GPU 数据步骤 72 个分片，作业 11655112、11655130、11655136；probe 11655139；报告 11655152）。规则：预注册补充 9（<span class="mono">381_stage13/config/prereg_addendum9.json</span>，sha256 a9896357…）。报告：<span class="mono">{R13}e4b_alltok.md</span>、<span class="mono">381_stage13/summary_alltok/</span>。教师强制打分，不是生成。</p>
<p><b>probe 的定义。</b>输入是第 l 层标题最后一个 token 的残差（真标题运行与 false_0 运行）；目标是模型自己在 L63、在预测该角色名字 token 的那些位置上的状态，按论文平均；用 ridge 回归，按作者团队分折（存档的团队折），只在训练折上标准化，正则强度在第 0 折上选，剔除标题复用的论文；预测的状态经 final norm 和反嵌入，在 9,137 个名字 token 组成的词表里给该角色的每个金标准 token 求名次{T('e4b_alltok.md 首段；9,137 个名字 token id，其中 4,314 个与 Stage 11 probe 词表逐位相同')}。标题特异信号 = probe(真标题) − probe(false_0)。</p>
<p><b>结果（用户确认的措辞）：</b>补充 9（答辩后新增，分析计划在看结果前写定）：把标题位置 probe 扩展到每位作者的全部名字 token，并按角色分开。在 L40，姓的第一个 token 的标题特异信号为 +0.071 [0.058, 0.085]{T('补充 9，L40，姓的第一个 token，目标 + 对照 1,395 篇，团队聚类 95% CI；e4b_alltok.md 第 5 节')}，高于首字母的 +0.044 [0.030, 0.057]{T('同上，首字母，1,590 篇')}，差为 +0.028 [0.011, 0.045]{T('同上，两项全论文均值之差，共同团队抽样；论文内配对版 +0.032 [0.015, 0.050]，1,296 篇')}，两项预注册判据都通过。名的第一个 token 最强（L40 +0.124{T('同上，名的第一个 token，1,706 篇，[0.108, 0.142]')}，L56 +0.163{T('同上，L56，[0.145, 0.181]')}）。原 E4b 只给每位作者的第一个 token 打分，而这个 token 多半是首字母，所以它低估了标题位置携带的名字信息。两种置换对照在姓、名的其余 token 上约为 0；在首字母上约为 +0.02{T('置换对照（金标准换成随机另一篇 / 同领域另一篇论文的作者）：首字母随机论文 L40–L60 +0.017 到 +0.023、同领域 L32–L44 与 L56 +0.013 到 +0.020，团队 CI 不含 0；e4b_alltok.md 第 7 节；summary_alltok/alltok_controls.csv')}，说明首字母的信号约一半不针对具体论文。</p>
<p><b>目标 − 对照（用户确认的措辞）：</b>认得出的论文在标题位置携带更多名字信息，这一差别主要来自首字母和名（L24–L32 起为正，+0.02 到 +0.09{T('引用档内目标 − 对照，首字母 L24 +0.033、名的第一个 token L24 +0.051、L56 +0.086，团队 CI 不含 0；e4b_alltok.md 第 3 节 “Target - control” 矩阵')}）；姓的第一个 token 在 L16–L52 约为 0，L56–L60 才出现 +0.04 到 +0.06{T('同矩阵，姓的第一个 token：L16–L52 −0.002 到 +0.030（CI 含 0），L56 +0.058、L60 +0.043')}。</p>
<div class="tw"><table><thead><tr><th>角色</th><th>篇数</th><th>L40 标题特异 [95% CI]</th><th>L56 标题特异</th><th>L40 目标 − 对照</th><th>L56 目标 − 对照</th></tr></thead><tbody>
<tr><td>首字母</td><td>1,590</td><td>+0.044 [0.030, 0.057]</td><td>+0.054</td><td>+0.031</td><td>+0.058</td></tr>
<tr><td>名的第一个 token</td><td>1,706</td><td>+0.124 [0.108, 0.142]</td><td>+0.163</td><td>+0.049</td><td>+0.086</td></tr>
<tr><td>名的其余 token</td><td>1,409</td><td>+0.045 [0.035, 0.056]</td><td>+0.050</td><td>+0.036</td><td>+0.040</td></tr>
<tr><td>姓的第一个 token</td><td>1,395</td><td>+0.071 [0.058, 0.085]</td><td>+0.098</td><td>+0.012</td><td>+0.058</td></tr>
<tr><td>姓的其余 token</td><td>1,754</td><td>+0.030</td><td>+0.040</td><td>+0.025</td><td>+0.035</td></tr>
<tr><td>每位作者的第一个 token（= E4b）</td><td>1,395</td><td>+0.061</td><td>+0.076</td><td>+0.063</td><td>+0.075</td></tr>
</tbody></table></div>
<p class="note">表 AT.1 来源：<span class="mono">{R13}e4b_alltok.md</span> 第 3 节 “Summary matrix” 与 “Target - control” 矩阵；<span class="mono">summary_alltok/alltok_role_layer.csv</span>（目标 + 对照，剔除标题复用，团队聚类 95% CI；目标 − 对照为引用档内比较）。</p>
<div class="bx"><b>敏感性分析（补充 13 C-3）：不剔除标题复用</b>这一版<strong>包含标题复用造成的泄漏</strong>，只作敏感性分析。全部论文的信号不变（例如 L40 姓的第一个 token +0.077 [0.070, 0.085]，6,841 篇{T('补充 13 C-3，同一 probe 预测，不剔除标题复用，目标 + 对照 6,841 篇，团队聚类 95% CI；' + R13 + 'c13_C3.md')}；首字母 +0.032{T('同上，6,385 篇')}）。在这一版里“姓的第一个 token 目标 − 对照在 L16–L52 显著”<strong>不是结论</strong>：目标 − 对照以逐个假标题排除的版本为准（补充 10 的偏离 D1，<span class="mono">381_stage13/config/prereg_addendum10_deviations.md</span>），该版本还在计算。</div>
<p class="note">与预注册的出入与检查：置换对照的真金标准列与 probe 本身的逐篇值有一处 0.036 的 WARN，查明是浮点求和顺序导致个别 token 名次差 1，两次拟合在全部 63 个格子选到的正则强度相同，报告精度下的数字不受影响{T(R13 + 'alltok_deviations.md')}。E4b 一致性检查（第一个 token、Stage 11 的 4,314 词表）复现已发表的 L24 +0.050、L40 +0.061{T('e4b_alltok.md 第 2 节')}。<b>批次 1 第 4 项（E4b 和全部 token probe 减 5 个假标题平均、逐个假标题排除）还在运行，结果确认后补入此处。</b></p>
</section>
'''
ins_before('<section id="x5-results">', AT)

# ---------- limitations that cannot be redone (§8 + Part 5)
LZ = ('只有一个模型（Qwen3-32B）：分组标签来自同一模型的标注，换模型需要重新标注；教师强制：所有分数都是把正确名字放进去后模型给它的名次，不是生成；'
      '标注流程：标注包作者的 elm 代码和 run.json 不在集群上，开放回答的生成参数和多选提示设置无法复核；高引用档缺对照：4097+ 档没有 B / D 论文，引用档内比较用不到这些论文。')
rep('  </ul>\n</section>\n\n<footer>',
    '    <li><b>不能补做的局限（2026-11-06 写定）。</b>' + LZ + '<span class="en">Limits that cannot be redone: one model (labels come from this model); teacher forcing, not generation; the label pipeline (elm code and run.json) is not available; the highest citation bin (4097+) has no B / D papers, so within-bin comparisons cannot use it.</span></li>\n  </ul>\n</section>\n\n<footer>')

# ---------- stale statements
rep('Stage 9 最终只完成了 Fit A（Stage 10 使用的 fitA 即此）；Fit B 和 holdout 稳定性比较没有做，lens 的拟合稳定性尚未检验。',
    'Stage 9 最终只完成了 Fit A（Stage 10 使用的 fitA 即此）；Fit B 和 holdout 稳定性比较当时没有做，lens 的拟合稳定性尚未检验。2026-11-05 已列入重做计划（补充 12 第 2-1 项：Fit B 从 66/100 续跑并做 holdout 对比，批次 2，排队中）。')
rep('<li>Stage 9：Fit B 未拟合，holdout 稳定性比较未做；如需检验 lens 稳定性，需补做，且打分位置、token 范围、bootstrap 方案和接受标准应在评估前冻结。</li>',
    '<li>Stage 9：Fit B 未拟合，holdout 稳定性比较未做；已列入重做计划（补充 12 第 2-1 项，批次 2，规则已写定），尚未运行。</li>')

# ---------- Part 5: in-progress section -> redo programme + limitations
i = s.index('<section id="pd-running">'); j = s.index('</section>', i) + len('</section>')
RUN = f'''<section id="pd-running"><h2><span class="st">重做计划</span> 补充 10–13：完成的、正在运行的和不做的（2026-11-06）</h2>
<p class="note">重做计划的规则都在看结果之前写定并锁定：<span class="mono">381_stage13/config/prereg_addendum10.json</span>（批次 1）、<span class="mono">prereg_addendum11.json</span>、<span class="mono">prereg_addendum12.json</span>（批次 2）、<span class="mono">prereg_addendum13.json</span>（CPU 项）。复现已发表的数字是每一项的硬检查。完整清单见计划文档。</p>
<ul>
<li><b>已完成并写入：</b>X7 五个假标题（补充 10 第 2 项，见第四部分 X7）；全部名字 token 的标题位置 probe（补充 9，见第四部分）；CPU 项 C-1（Stage 7.1 加标题对照）、C-2（Stage 8 CPU 代理）、C-3（不剔除标题复用的敏感性）、C-4（M1 换 4 个假标题）、C-5（Stage 10 附加分析补齐全部已存层），硬检查都通过{T(R13 + 'c13_C1.md–c13_C5.md')}。</li>
<li><b>批次 1 还在运行（结果经用户确认后补入，此处先留位置）：</b>
<ul><li id="pd-b1-xall">X1–X4 改为全部作者（补充 10 第 1 项）：<i>结果待补</i>。</li>
<li id="pd-b1-p12f">P1 / P2 用 5 个假标题（补充 10 第 3 项）：<i>结果待补</i>。</li>
<li id="pd-b1-e4b5">E4b 与全部 token probe 减 5 个假标题平均，逐个假标题排除标题复用（补充 10 第 4 项及偏离 D1）：<i>结果待补</i>；C-3b 在它之后。</li></ul></li>
<li><b>批次 2（补充 11、12，排队中）：</b>名字位置 probe（直接检验 H3）、C / D 组补全 E1 / E2、Stage 9 Fit B 与 holdout、F1 作者 lens 对半拆分、X3 按 token 角色、E1 批量舍入噪声、名字位置的 patchscope（M5 的 GPU 部分）、E1t 用 5 个假标题、X4 角色拆分补齐其余层、M3 全部 token 分数、模型自生成名字的 probe。</li>
<li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做；CPU 代理见 Stage 8 节）。</li>
</ul>
</section>

<section id="pd-limits"><h2><span class="st">局限</span> 不能补做的局限</h2>
<ul>
<li><b>只有一个模型。</b>分组标签（认得出 / 认不出、写对几位作者）来自 Qwen3-32B 自己的标注；换一个模型需要重新标注，而标注流程不在集群上。</li>
<li><b>教师强制。</b>所有分数都是把正确名字放进去后模型给它的名次，测的是偏好，不是生成。</li>
<li><b>标注流程。</b>标注包作者的 elm 代码和 run.json 不在集群上：开放回答的生成长度、thinking 模式和多选题设置无法复核（方法手册附录 G3 的 U01、U03）。</li>
<li><b>高引用档缺对照。</b>4097+ 档没有 B / D 论文{T('Stage 10 队列 4097+ 档：目标 84 篇、对照 0 篇；381_stage13/reports/m3_scores.md 第 2 节')}，引用档内比较用不到这一档的论文。</li>
</ul>
</section>'''
s = s[:i] + RUN + s[j:]

assert not re.search('minyan', s, re.I) and '出处文件未找到' not in s
assert '尚无结果' not in s, [m.start() for m in re.finditer('尚无结果', s)]
open(OUT, 'w', encoding='utf-8').write(s); print('wrote', OUT, len(s), 'cav', n_cav)
