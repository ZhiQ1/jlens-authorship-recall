"""Report v29, local revision b (2026-11-06 ~21:00, still unpublished v29): batch-1 results confirmed by the user written in.
- X1-X4 all authors = wording b (PROGRESS 2026-11-06 ~13:30 item b) -> #pd-b1-xall + box at the end of the M3/X1/X4 section, pointers in X3 / X2
- E4b minus 5 false titles = wording d + surname target - control = wording a -> #pd-b1-e4b5 + box in #alltok-results;
  wording a replaces "姓的第一个 token 在 L16-L52 约为 0" in #alltok-results
- C-3b (addendum 13, sensitivity only, includes leakage, not a conclusion) replaces "C-3b 在它之后"; C-3 box points to it
- P1/P2 five false titles (#pd-b1-p12f): still running, 116/194 units, no numbers
- batch 2 status (code + tiny tests + hard-check unit tests done; starts automatically after batch 1; D12-1..D12-3; 2-7 source), batch 3 (addendum 14)
X7 (wording c) and C-1..C-5 (wording e) were already written by edit_v29.py (checked by asserts below).
Input = backup stage1_11_report.before_20261106b.html (= v29 from edit_v29.py). Usage: python edit_v29b.py [out]"""
import os, sys, re, shutil
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11'; os.chdir(D)
SRC = 'stage1_11_report.html'; OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
BK = 'stage1_11_report.before_20261106b.html'
if not os.path.exists(BK): shutil.copy2(SRC, BK)
s = open(BK, encoding='utf-8').read(); assert '第 29 版' in s


def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:70]); s = s.replace(a, b)


T = lambda t: f'<span class="src">（{t}）</span>'
R13 = '381_stage13/reports/'
XA = R13 + 'b1_xall_report.md'; E5 = R13 + 'b1_e4b5_report.md'; C3B = R13 + 'c13_C3b.md'

# ---- already present (wording c, e): verify only
for must in ['X7 补做了另外 4 个假标题，按 5 个平均判定，target、control 和全部论文都满足预注册判据（S(L52) 分别为 +0.022',
             '属于单个假标题的波动', '加上标题对照（真标题 − Stage 10 的 5 个匹配假标题）后，A−B 的差别在模型输出和 L62 上成立，public J-lens 多层平均不显著',
             '这是 CPU 代理，不是原 Stage 8 的统计量', '包含标题复用造成的泄漏', '补充 13 C-4', '补充 13 C-5']:
    assert must in s, must

rep('更新于 2026-11-06（第 29 版：Stage 1–13；答辩后新增见第五部分；补充 9–13 的重做结果已写入各节；正文数字后的灰色小字是出处）',
    '更新于 2026-11-06（第 29 版：Stage 1–13；答辩后新增见第五部分；补充 9–13 的重做结果已写入各节，批次 1 只剩 P1 / P2 五个假标题在运行；正文数字后的灰色小字是出处）')

# ---- overview box
rep('批次 1 的其余项目还在运行（第五部分）。',
    'X1–X4 改为全部作者、E4b 减 5 个假标题平均也已完成，结论不变；P1 / P2 用 5 个假标题还在运行（第五部分）。')

# ---- wording b (X1-X4 all authors) with source tags
XALL = ('X1–X4 改为给全部作者打分（全部名字 token），并按作者排位分层。结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]'
        + T('补充 10 第 1 项，X1，测试集，全部作者分层，团队聚类 95% CI；' + XA + ' “X1” 节')
        + '）；X3 改写标题保留约 90% 的作者偏好' + T('X3 行为，主分析测试集 552 篇，恢复比 0.897 [0.868, 0.926]；同一报告 “X3 behaviour” 节')
        + '，target 与 control 一样' + T('同表 target − control −0.007 [−0.075, +0.059]')
        + '；X4 从 L8 起可解码出作者，各作者排位相同' + T('X4 作者答案，标题位置，L8 起，四个分层都在测试集确认（全部作者 +0.048 [0.039, 0.058]）；同一报告 “X4” 节')
        + '，认得出的论文在 L8–L40 更高' + T('同节 Recognition 表，引用档内 target − control，全部作者 L8 +0.031 到 L40 +0.052，团队 CI 不含 0')
        + '；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释。X2 用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%'
        + T('X2，测试集，L48，旧 / 新 S_auth 的 R_auth；完整替换 R_full 0.457；同一报告 “X2: verdict” 节')
        + '），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009' + T('新 S_auth 拟合，5,041 篇训练论文，L16–L48 authall_r2 0.004–0.009；同一报告 “New S_auth” 节')
        + '），H3 仍证据不足。')
XALL_CHK = T('硬检查 PASS：冻结的第一作者分数逐位复现，X1–X4 已发表的点估计差 ≤ 2e-15；' + XA + ' “Hard check” 节；1,178 对（X3 1,137 对）')

# ---- wording d + a (E4b minus five false titles, per-donor exclusion)
E4B5 = ('E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题'
        + T('补充 10 第 4 项，偏离 D1（381_stage13/config/prereg_addendum10_deviations.md）；' + E5 + ' “Per-donor exclusion” 节，姓的第一个 token，L40')
        + '）：L40 姓首 token +0.076 [0.068, 0.083]' + T('目标 + 对照 4,654 篇，团队聚类 95% CI；同节 “Vpd” 表')
        + '，姓 − 首字母 +0.033 [0.023, 0.042]' + T('同节 “Addendum-9 primary contrasts at L40 under Vpd”')
        + '，原 E4b 第一个 token +0.066' + T('同节 Vpd 表 e4b_parity 行，L40 [0.059, 0.073]')
        + '；置换对照首字母仍 +0.018，其余 ≈ 0' + T('金标准换成随机另一篇论文的作者，L40；首字母 [0.011, 0.025]，其余角色 CI 含 0；同节')
        + '；硬检查 E4b L40 +0.0609 PASS' + T('false_0 版本复现已发表的 +0.061 ± 0.005，1,395 篇；同一报告第 2 节') + '。')
WA = ('按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正（L40 +0.030'
      + T('引用档内 target − control，L40 [0.013, 0.048]，团队聚类 95% CI；' + E5 + ' “Per-donor exclusion” 节 target − control 表')
      + '，L56 +0.058' + T('同表，[0.039, 0.078]；L24 +0.019 [0.001, 0.038]，L16 CI 含 0')
      + '）；只用 false_0、样本较小时，L56 前不显著' + T('false_0 版本，1,395 篇，L16–L52 CI 含 0，L56 +0.058 [0.017, 0.098]；同一报告 V0 表') + '。')

# ---- C-3b
C3b = ('C-3b（补充 13，敏感性分析，<strong>包含标题复用造成的泄漏，不作结论</strong>，与 C-3 的处理相同）：把 5 个假标题平均的版本也不剔除标题复用重算，硬检查 PASS'
       + T('逐个假标题排除等三个已发表版本在此重算，189 行 × 14 列最大差 1.0e-16；' + C3B + ' “Hard check”')
       + '；L40 姓的第一个 token +0.077 [0.071, 0.084]，首字母 +0.034 [0.029, 0.039]，姓 − 首字母 +0.043 [0.035, 0.051]'
       + T('不剔除标题复用，目标 + 对照 6,841 篇（首字母 6,385 篇），团队聚类 95% CI；' + C3B + ' “Primary contrasts at L40” 表 V5x0_noexcl 列')
       + '；target − control 的区间几乎处处在 0 以上，与 C-3 一样' + T('同文件 target − control 表') + '。')

# ---- #alltok-results: wording a replaces the surname clause
rep('；姓的第一个 token 在 L16–L52 约为 0，L56–L60 才出现 +0.04 到 +0.06<span class="src">（同矩阵，姓的第一个 token：L16–L52 −0.002 到 +0.030（CI 含 0），L56 +0.058、L60 +0.043）</span>。</p>',
    '；' + WA + '（下表为只用 false_0 的版本。）</p>')
rep('目标 − 对照以逐个假标题排除的版本为准（补充 10 的偏离 D1，<span class="mono">381_stage13/config/prereg_addendum10_deviations.md</span>），该版本还在计算。</div>',
    '目标 − 对照以逐个假标题排除的版本为准（补充 10 的偏离 D1，<span class="mono">381_stage13/config/prereg_addendum10_deviations.md</span>），该版本已完成，见下框。</div>')
rep('<b>批次 1 第 4 项（E4b 和全部 token probe 减 5 个假标题平均、逐个假标题排除）还在运行，结果确认后补入此处。</b></p>\n</section>',
    '</p>\n<div class="bx ok"><b>2026-11-06 补做（批次 1 第 4 项：E4b 和全部 token probe 减 5 个假标题平均）</b>' + E4B5 + '<br>' + WA + '</div>\n'
    '<div class="bx"><b>敏感性分析（补充 13 C-3b）</b>' + C3b + '</div>\n</section>')

# ---- Part 4 X1/X4, X3, X2 sections
i = s.index('<section id="m3x1x4-results">'); j = s.index('</section>', i)
s = s[:j] + ('<div class="bx ok"><b>2026-11-06 补做（批次 1 第 1 项：X1–X4 改为全部作者）</b>' + XALL + XALL_CHK + '</div>\n') + s[j:]
PTR = '<p class="note"><b>2026-11-06：</b>全部作者版本（补充 10 第 1 项）见 <a href="#m3x1x4-results">M3 / X1 / X4 节</a> 末尾和第五部分 <a href="#pd-b1-xall">批次 1</a>：%s</p>\n'
i = s.index('<section id="x3-results">'); j = s.index('</section>', i)
s = s[:j] + PTR % 'X3 改写标题保留约 90% 的作者偏好，target 与 control 一样，结论不变。' + s[j:]
i = s.index('<section id="x2-results">'); j = s.index('</section>', i)
s = s[:j] + PTR % '用全部作者重新拟合作者子空间后搬动量从 0.016 升到 0.032（完整替换的约 7%），子空间仍几乎解码不出作者（留出 R² ≤ 0.009），H3 仍证据不足。' + s[j:]

# ---- Part 5 redo programme
rep('<li><b>已完成并写入：</b>X7 五个假标题（补充 10 第 2 项，见第四部分 X7）；',
    '<li><b>已完成并写入：</b>X7 五个假标题（补充 10 第 2 项，见第四部分 X7）；X1–X4 改为全部作者、E4b 减 5 个假标题平均（补充 10 第 1、4 项，见下）；C-3b（补充 13，只作敏感性分析）；')
rep('<li><b>批次 1 还在运行（结果经用户确认后补入，此处先留位置）：</b>', '<li><b>批次 1（补充 10）：</b>第 1、2、4 项已完成；第 3 项还在运行。')
rep('<li id="pd-b1-xall">X1–X4 改为全部作者（补充 10 第 1 项）：<i>结果待补</i>。</li>',
    '<li id="pd-b1-xall"><b>X1–X4 改为全部作者（补充 10 第 1 项，已完成）：</b>' + XALL + XALL_CHK + '</li>')
rep('<li id="pd-b1-p12f">P1 / P2 用 5 个假标题（补充 10 第 3 项）：<i>结果待补</i>。</li>',
    '<li id="pd-b1-p12f"><b>P1 / P2 用 5 个假标题（补充 10 第 3 项）：还在运行。</b>194 个计算单元已完成 116 个，其余 78 个分三条并行的作业链计算；结果经用户确认后补入。</li>')
rep('<li id="pd-b1-e4b5">E4b 与全部 token probe 减 5 个假标题平均，逐个假标题排除标题复用（补充 10 第 4 项及偏离 D1）：<i>结果待补</i>；C-3b 在它之后。</li>',
    '<li id="pd-b1-e4b5"><b>E4b 与全部 token probe 减 5 个假标题平均，逐个假标题排除标题复用（补充 10 第 4 项及偏离 D1，已完成）：</b>' + E4B5 + WA
    + '<br>' + C3b + '</li>')
B2 = ('<li><b>批次 2（补充 11、12）：代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始。</b>项目：')
rep('<li><b>批次 2（补充 11、12，排队中）：</b>', B2)
rep('M3 全部 token 分数、模型自生成名字的 probe。</li>',
    'M3 全部 token 分数、模型自生成名字的 probe。与预注册的出入写在补充 12 的出入记录 D12-1 到 D12-3'
    + T('381_stage13/config/prereg_addendum12_deviations.json，sha256 c4c79365…，用户 2026-11-06 决定，在任何批次 2 GPU 结果之前写定')
    + '：2-1（Fit B）和 2-2（F1 对半拆分）改用较省的硬检查，但都包含在原始提示上逐位复现的重拟合；2-11 用 Stage 10 的名字匹配重建标签，主分析为论文内 AUROC，加两个基线（名字在列表中的位置；名字长度与队列内出现频率），对照组只作描述。另外，2-7（名字位置的 patchscope）的来源改用不含年份的 X4 提示，以免年份泄漏'
    + T('381_stage13/reports/b2_groupA_handoff.md 出入记录') + '。</li>\n'
    '<li><b>批次 3（补充 14）：</b>3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写；3-4、3-5（Stage 8 按 W 的 GPU 重算及其依赖项）不做'
    + T('381_stage13/config/prereg_addendum14.json') + '。</li>')

# ---- Fit B statements
rep('（补充 12 第 2-1 项：Fit B 从 66/100 续跑并做 holdout 对比，批次 2，排队中）',
    '（补充 12 第 2-1 项：Fit B 从 66/100 续跑并做 holdout 对比，批次 2；代码与 tiny 测试已完成，批次 1 结束后自动开始）')
rep('已列入重做计划（补充 12 第 2-1 项，批次 2，规则已写定），尚未运行。</li>',
    '已列入重做计划（补充 12 第 2-1 项，批次 2，规则已写定；代码与 tiny 测试已完成，排队自动开始），尚未运行。</li>')

assert '结果待补' not in s and 'C-3b 在它之后' not in s and '还在计算' not in s
assert not re.search('minyan', s, re.I) and '出处文件未找到' not in s
open(OUT, 'w', encoding='utf-8').write(s); print('wrote', OUT, len(s))
