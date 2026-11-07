"""Handbook update 2026-11-06 b (same user-confirmed batch-1 wording as report v29 revision b, stage1_11/src/edit_v29b.py):
F: s13-alltok (surname target - control = wording a; five-false-title result = wording d; C-3b; limits/status), X1-X4 all-author box (wording b)
   after the s13-x1 heading + pointers in s13-x2 / s13-x3 / s13-x4; G: V58 done, new V61 (C-3b) and V62 (addendum 12 deviation record D12-1..3);
C: Stage 9 Fit B status (batch 2 code ready, auto start); K: rebuilt from the report v29b Part 5 (same conversion as edit_20261106.py);
B: rows for X1-X4 all authors and E4b five false titles; header date. Backups *.before_20261106b.* (edits always start from them).
Then: build_methods.py, export_pdf_20261106b.py."""
import re, shutil
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods'); P = D / 'parts'
def bk(p):
    b = p.with_name(p.stem + '.before_20261106b' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
def after_h3(s, hid, block):
    m = re.search(r'<h3 id="%s"[^>]*>.*?</h3>' % re.escape(hid), s, re.S); assert m, hid
    return s[:m.end()] + '\n' + block + s[m.end():]
S = lambda t: f'<span class="src">{t}</span>'
R13 = '381_stage13/reports/'; XA = R13 + 'b1_xall_report.md'; E5 = R13 + 'b1_e4b5_report.md'; C3B = R13 + 'c13_C3b.md'

XALL = ('X1–X4 改为给全部作者打分（全部名字 token），并按作者排位分层。结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]'
        + S(XA + ' “X1” 节：测试集，全部作者分层，作者 − 年份，团队聚类 bootstrap 2,000 次 95% CI') + '）；X3 改写标题保留约 90% 的作者偏好'
        + S(XA + ' “X3 behaviour” 表：主分析测试集 552 篇，恢复比 (改写 − D)/(原标题 − D) = 0.897 [0.868, 0.926]') + '，target 与 control 一样'
        + S('同表 target − control −0.007 [−0.075, +0.059]') + '；X4 从 L8 起可解码出作者，各作者排位相同'
        + S(XA + ' “X4” 节：D = self − partner，tune 上选最早层、test 上确认；全部作者 L8 +0.048 [0.039, 0.058]，first / others / last 都是 L8') + '，认得出的论文在 L8–L40 更高'
        + S('同节 Recognition 表：引用档内 target − control，全部作者 L8 +0.031 [0.017, 0.045] 到 L40 +0.052 [0.038, 0.067]')
        + '；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释。X2 用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%'
        + S(XA + ' “X2: verdict” 表：测试集，L48，R_auth 旧 / 新 S_auth；R_full 0.457') + '），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009'
        + S(XA + ' “New S_auth” 表：5,041 篇训练论文，L16–L48 authall_r2 0.004–0.009') + '），H3 仍证据不足。'
        + S('硬检查 PASS：冻结的第一作者分数逐位复现（35,340 / 84,816 / 34,162 / 4,548 格，差 0），X1–X4 已发表点估计最大差 1.2e-15；' + XA + ' “Hard check”'))
E4B5 = ('E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题）：L40 姓首 token +0.076 [0.068, 0.083]，姓 − 首字母 +0.033 [0.023, 0.042]，原 E4b 第一个 token +0.066；置换对照首字母仍 +0.018，其余 ≈ 0；硬检查 E4b L40 +0.0609 PASS。'
        + S(E5 + ' “Per-donor exclusion” 节（Vpd = 真标题 − 供体不在训练折的假标题的平均，至少 1 个可用；目标 + 对照；团队聚类 bootstrap 2,000 次 95% CI）：kept 表、Vpd 表 surname_first / e4b_parity 行 L40、“primary contrasts under Vpd”、置换对照 any 行；第 2 节硬检查（V0 e4b_parity L40 +0.0609，1,395 篇，容差 ±0.005）'))
WA = ('按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正（L40 +0.030，L56 +0.058）；只用 false_0、样本较小时，L56 前不显著。'
      + S(E5 + ' “Per-donor exclusion” 节 target − control 表 surname_first 行（引用档内，团队聚类 95% CI）：L24 +0.019 [0.001, 0.038]，L40 +0.030 [0.013, 0.048]，L56 +0.058 [0.039, 0.078]；V0 表（1,395 篇）L16–L52 CI 含 0，L56 +0.058 [0.017, 0.098]'))
C3b = ('C-3b（补充 13，不剔除标题复用，<b>含泄漏，只作敏感性分析，不作结论</b>，与 C-3 相同）：硬检查 PASS；L40 姓的第一个 token +0.077 [0.071, 0.084]，首字母 +0.034 [0.029, 0.039]，姓 − 首字母 +0.043 [0.035, 0.051]（6,841 篇）；target − control 的区间几乎处处在 0 以上，与 C-3 一样。'
       + S(C3B + '：“Hard check”（三个已发表版本重算，189 行 × 14 列最大差 1.0e-16）；“Primary contrasts at L40” 表 V5x0_noexcl 列；团队聚类 bootstrap 2,000 次'))

# --- F
s = bk(P / 'F_stage13.html')
s = rep(s, '；姓的第一个 token 在 L16–L52 约为 0，L56–L60 才出现 +0.04 到 +0.06。', '；' + WA)
s = rep(s, '目标 − 对照以逐个假标题排除的版本为准（补充 10 偏离 D1，计算中）。', '目标 − 对照以逐个假标题排除的版本为准（补充 10 偏离 D1，已完成，见下）。')
s = rep(s, '<li>减 5 个假标题平均的版本（补充 10 第 4 项）还在运行。</li>', '<li>5 个假标题版本按 5 个一起排除时剩 0 篇，所以改为逐个假标题排除（偏离 D1，结果出来前写定），每篇平均只用 1.5 个假标题。</li>')
s = rep(s, '<h4>8 局限与质疑</h4><ul><li>置换对照的真金标准列',
        '<p><b>2026-11-06 补做（补充 10 第 4 项）：</b>' + E4B5 + '</p>\n<p>' + C3b + '</p>\n<h4>8 局限与质疑</h4><ul><li>置换对照的真金标准列')
s = rep(s, '（2026-11-05）；5 个假标题版本 <span class="st st-plan">进行中</span></p>', '（2026-11-05）；5 个假标题版本 <span class="st st-done">已完成</span>（2026-11-06）；C-3b <span class="st st-done">已完成（只作敏感性分析）</span></p>')
s = after_h3(s, 's13-x1', '<div class="fix" id="s13-xall"><b>2026-11-06 补做（补充 10 第 1 项：X1–X4 改为全部作者）：</b>' + XALL + '</div>')
for hid in ('s13-x2', 's13-x3', 's13-x4'):
    s = after_h3(s, hid, '<div class="fix"><b>2026-11-06：</b>全部作者版本（补充 10 第 1 项）见 <a href="#s13-xall">X1 节开头</a>，结论不变。</div>')
(P / 'F_stage13.html').write_text(s, encoding='utf-8')

# --- G
s = bk(P / 'G_appendix.html')
s = rep(s, '（补充 10 偏离 D1）</td><td><span class="st st-review">偏离</span> 进行中</td>', '（补充 10 偏离 D1）</td><td><span class="st st-review">偏离</span> 已完成（2026-11-06）</td>')
i = s.index('<tr><td>V60</td>'); j = s.index('</tr>', i) + 5
s = s[:j] + ('\n<tr><td>V61</td><td>C-3b：5 个假标题版本不剔除标题复用（补充 13）</td><td><span class="st st-done">已完成</span></td><td>含泄漏，只作敏感性分析，不作结论；硬检查 PASS。'
             + S(C3B) + '</td><td><a href="#s13-alltok">s13-alltok</a></td></tr>'
             '\n<tr><td>V62</td><td>补充 12 出入记录 D12-1..D12-3（2-1、2-2 较省的硬检查，含原始提示逐位复现重拟合；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述）；2-7 来源改用不含年份的 X4 提示</td><td><span class="st st-review">偏离</span> 已写定，未运行</td><td>用户 2026-11-06 决定，在任何批次 2 GPU 结果之前写定。'
             + S('381_stage13/config/prereg_addendum12_deviations.json（sha256 c4c79365…）；381_stage13/reports/b2_groupA_handoff.md') + '</td><td><a href="#k-running">k-running</a></td></tr>') + s[j:]
(P / 'G_appendix.html').write_text(s, encoding='utf-8')

# --- C
s = bk(P / 'C_stage1_9.html')
s = rep(s, '批次 2，规则已写定），尚未运行。', '批次 2，规则已写定；代码、tiny 测试和硬检查单元测试已完成，批次 1 结束后由编排作业自动开始），尚未运行。')
(P / 'C_stage1_9.html').write_text(s, encoding='utf-8')

# --- B
s = bk(P / 'B_global2.html')
a = '<tr><td>X7（5 个假标题，补充 10 第 2 项）</td>'; i = s.index(a); j = s.index('</tr>', i) + 5
s = s[:j] + ('\n<tr><td>X1–X4 全部作者（补充 10 第 1 项）</td><td>复现已发表的第一作者数字（硬检查）</td><td>按规则实现；逐位复现；结论不变</td><td><span class="st st-done">已完成</span></td><td>' + S(XA) + '</td></tr>'
             '\n<tr><td>E4b 减 5 个假标题（补充 10 第 4 项）</td><td>按 5 个一起排除标题复用</td><td>剩 0 篇 → 逐个假标题排除（偏离 D1，结果前写定）；硬检查 PASS</td><td><span class="st st-done">已完成</span></td><td>' + S(E5 + ' · 381_stage13/config/prereg_addendum10_deviations.md') + '</td></tr>') + s[j:]
(P / 'B_global2.html').write_text(s, encoding='utf-8')

# --- K from the report (same conversion as edit_20261106.py)
rep_html = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html').read_text(encoding='utf-8')
assert 'id="pd-b1-xall"><b>X1–X4' in rep_html, 'run stage1_11/src/edit_v29b.py first'
fr = rep_html[rep_html.index('<div class="partbar" id="p5">'):]
fr = re.sub(r'<div class="partbar".*?</div>\s*<div class="p19"><main>', '', fr, count=1, flags=re.S)
fr = fr.replace('</main></div>', '')
for sid, kid in [('pd-groups', 'k-groups'), ('pd-cpu', 'k-cpu'), ('pd-running', 'k-running'), ('pd-limits', 'k-limits')]:
    fr = fr.replace(f'<section id="{sid}"><h2>', f'<h3 id="{kid}">')
fr = re.sub(r'</h2>', '</h3>', fr); fr = fr.replace('</section>', '')
fr = re.sub(r'<h3>(.*?)</h3>', r'<h4>\1</h4>', fr, flags=re.S)
fr = fr.replace('<span class="ln lA">A 这篇论文？</span>', '').replace('<span class="ln lC">C 哪一层</span>', '')
fr = re.sub(r'<span class="st">([^<]*)</span>', r'<span class="st st-done">\1</span>', fr)
fr = fr.replace('<div class="bx">', '<div class="fix">').replace('<table>', '<table class="t">')
fr = fr.replace('#x2-results', '#s13-x2').replace('#alltok-results', '#s13-alltok').replace('见第四部分的说明', '见本手册 M5 节')
fr = fr.replace('id="pd-b1-', 'id="k-b1-').replace('id="pd-p1p2-numden"', 'id="k-p1p2-numden"')
bk(P / 'K_post_defence.html')
K = ('<section id="k-post"><h2>十一 答辩后新增（2026-11-05 / 06）</h2>\n'
     '<p class="lead">答辩材料 2026-11-02/03 定稿之后的工作。分组对比是答辩后新增的分析，分析计划在看结果前写定（补充 7、8）；其余 CPU 补充分析是事后分析；重做计划（补充 10–14）的规则都在看结果前写定。'
     '与《Stage 1–13 实验报告》第 29 版第五部分内容相同（图号、表号沿用报告）。</p>\n' + fr.strip() + '\n</section>')
assert 'p19' not in re.sub(r'data:[^"]*', '', K)
(P / 'K_post_defence.html').write_text(K, encoding='utf-8')

# --- builder header
s = bk(D / 'build_methods.py')
s = rep(s, '2026-11-06 补充（第十一部分：答辩后新增与重做计划；X2、补充 9 全部名字 token 的 probe、X7 五个假标题、补充 13 CPU 项）',
        '2026-11-06 补充（第十一部分：答辩后新增与重做计划；X2、补充 9 全部名字 token 的 probe、X7 五个假标题、补充 13 CPU 项；晚间 b 版：批次 1 的 X1–X4 全部作者、E4b 减 5 个假标题、C-3b）')
(D / 'build_methods.py').write_text(s, encoding='utf-8')
for f in P.glob('*.html'):
    if 'before_' not in f.name: assert not re.search('minyan', f.read_text(encoding='utf-8'), re.I), f
print('ok')
