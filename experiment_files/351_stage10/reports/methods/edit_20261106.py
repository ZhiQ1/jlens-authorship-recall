"""Handbook update 2026-11-06 (redo programme, addenda 9-13; same approved wording as report v29): part K rebuilt from report v29 Part 5;
new F section s13-alltok (addendum 9 + C-3 sensitivity); X7 five false titles; M1 C-4; M5 status (done on CPU); E4b caveat boxes -> pointer;
C part: Stage 7.1 C-1, Stage 8 C-2, Stage 9 Fit B status; D part: C-5 note; G: M5 rows, V58-V60; B: prereg-dev rows; header date.
Backups *.before_20261106.* (edits always start from them). Then run build_methods.py."""
import re, shutil
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods'); P = D / 'parts'
def bk(p):
    b = p.with_name(p.stem + '.before_20261106' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
def after_h3(s, hid, block):
    m = re.search(r'<h3 id="%s"[^>]*>.*?</h3>' % re.escape(hid), s, re.S); assert m, hid
    return s[:m.end()] + '\n' + block + s[m.end():]
S = lambda t: f'<span class="src">{t}</span>'
R13 = '381_stage13/reports/'

POINTER = ('<div class="fix"><b>E4b 只给每位作者名字的第一个 token 打分</b>（多数是首字母）。覆盖全部名字 token、按首字母 / 名 / 姓分开的版本（补充 9，2026-11-05 完成）见 '
           '<a href="#s13-alltok">六 · 补充 9</a>：L40 姓的第一个 token +0.071 [0.058, 0.085]，首字母 +0.044 [0.030, 0.057]，名的第一个 token +0.124。'
           + S(R13 + 'e4b_alltok.md 第 5 节与 Summary matrix；目标 + 对照，剔除标题复用，团队聚类 95% CI') + '</div>')

# --- D: E4b caveat boxes -> pointer; C-5 note
s = bk(P / 'D_stage10_11.html')
s, n = re.subn(r'<div class="fix"><b>注意（2026-11-05 补）：E4b 只给每位作者名字的第一个 token 打分</b>.*?</div>', POINTER, s, flags=re.S); assert n == 2, n
s = after_h3(s, 's1011-s10-format', '<div class="fix"><b>2026-11-06 补（补充 13 C-5，事后）：</b>本节和 10-7a、10-7b 的附加分析已补到全部已存的层（public / logit lens L50–L55、L57–L61），原有层逐位复现，结论不变；public J-lens 下后续 token 的目标 − 对照在 L48–L54 为负（−0.020 到 −0.050），从 L56 起转正（L56 +0.026，L62 +0.282）；logit lens 从 L50 起为正。'
                + S(R13 + 'c13_C5.md “X1 token position” 表；381_stage13/summary_c13/c5/all_layers/') + '</div>')
(P / 'D_stage10_11.html').write_text(s, encoding='utf-8')

# --- C: Stage 7.1 (C-1), Stage 8 (C-2), Stage 9 Fit B
s = bk(P / 'C_stage1_9.html')
s = after_h3(s, 's19-s71', '<div class="fix"><b>2026-11-06 补（补充 13 C-1，事后）：</b>加上标题对照（真标题 − Stage 10 的 5 个匹配假标题）后，A−B 的差别在模型输出和 L62 上成立，public J-lens 多层平均不显著：名字其余 token 上输出 +0.244 [0.087, 0.398]、logit L62 +0.278 [0.088, 0.483]、public J-lens L62 +0.317 [0.145, 0.506]，public J-lens 6 层平均 +0.077 [−0.021, +0.180]。原结论（无标题对照的 JMRR）“A−B 的差别在名字其余 token 上”由此改写。'
                + S(R13 + 'c13_C1.md Pilot50 表 aa_cont 行（20 对，配对 bootstrap 95% CI）') + '</div>')
s = after_h3(s, 's19-s8d', '<div class="fix"><b>2026-11-06 补：CPU 代理（补充 13 C-2，事后）。</b>用 Stage 10 的原始分数在 200 篇论文上重算冻结的多层终点：全部作者、全部 token 的版本中 RQ1 和 RQ2 都成立（public J-lens 6 层平均 RQ1 +0.130 [0.109, 0.153]，RQ2 +0.054 [0.008, 0.102]）；只看 L56 时 RQ2 +0.064 [−0.032, +0.163]，不显著。'
                '这是 CPU 代理：public J-lens 的名次指标、Stage 10 的 5 个假标题，不是 W 统计量；按原 W 的 GPU 重算没有做（用户 2026-11-06 决定）。'
                + S(R13 + 'c13_C2.md aa_all 行') + '</div>')
s = after_h3(s, 's19-s9-fitB', '<div class="fix"><b>2026-11-06 状态：</b>Fit B 从 66/100 续跑并做 holdout 对比已列入重做计划（补充 12 第 2-1 项，批次 2，规则已写定），尚未运行。'
                + S('381_stage13/config/prereg_addendum12.json “2-1 Stage 9 Fit B and holdout”') + '</div>')
(P / 'C_stage1_9.html').write_text(s, encoding='utf-8')

# --- F: X7 five titles, M1 C-4, M5 status, new all-token section, U47 row
s = bk(P / 'F_stage13.html')
s = after_h3(s, 's13-x7', '<div class="fix"><b>2026-11-06 补做（补充 10 第 2 项）：</b>X7 补做了另外 4 个假标题，按 5 个平均判定，target、control 和全部论文都满足预注册判据（S(L52) 分别为 +0.022、+0.042、+0.028，均 ≤ 0.05）；原来对照组只用 false_0 时为 0.051，属于单个假标题的波动。'
                + S(R13 + 'b1_x7f_report.md（target 593 / control 593 / 全部 1,186 篇，团队聚类 95% CI；false_0 臂逐位复现 summary_x7/x7_knockout.csv）') + '</div>')
s = after_h3(s, 's13-m1', '<div class="fix"><b>2026-11-06 补（补充 13 C-4）：</b>换成另外 4 个假标题，各读出、各层排第一的词改变的比例与 false_0 平均只差 +0.26 个百分点（范围 −0.08 到 +0.64），结论不变。'
                + S(R13 + 'c13_C4.md（149,999 个名字 token，47 个读出 × 层；false_0 列逐位复现 M1_title_sensitivity.csv）') + '</div>')
s = rep(s, '<h3 id="s13-m5">M5　逐位置 probe / patchscope / 名字位置上的真假判别（提议）</h3>', '<h3 id="s13-m5">M5　逐位置 probe / patchscope / 名字位置上的真假判别</h3>')
s = rep(s, 's13-m5 | U47 与 X4 同一问题则并入 X4，否则放弃', 's13-m5 | U47 与 X4 同一问题则并入 X4，否则放弃 → 2026-11-05：能用已有数据回答的部分已在 CPU 上做完（十一 · CPU 补充）；名字位置的 patchscope 列入补充 12 第 2-7 项')
AT = ('<h3 id="s13-alltok">补充 9　全部名字 token 的标题位置 probe（按首字母 / 名 / 姓）</h3>\n'
      '<div class="fix"><b>2026-11-05 完成。</b>补充 9（答辩后新增，分析计划在看结果前写定）：把标题位置 probe 扩展到每位作者的全部名字 token，并按角色分开。在 L40，姓的第一个 token 的标题特异信号为 +0.071 [0.058, 0.085]，高于首字母的 +0.044 [0.030, 0.057]，差为 +0.028 [0.011, 0.045]，两项预注册判据都通过。名的第一个 token 最强（L40 +0.124，L56 +0.163）。原 E4b 只给每位作者的第一个 token 打分，而这个 token 多半是首字母，所以它低估了标题位置携带的名字信息。两种置换对照在姓、名的其余 token 上约为 0；在首字母上约为 +0.02，说明首字母的信号约一半不针对具体论文。'
      + S(R13 + 'e4b_alltok.md 第 3、5、7 节；summary_alltok/') + '</div>\n'
      '<h4>1 问题与作用</h4><p>E4b 只打分每位作者的第一个名字 token（多半是首字母）。补充 9 问：标题位置携带的名字信息是否主要在姓上？预注册的主要比较：L40 姓的第一个 token 的标题特异信号 &gt; 0，以及姓 − 首字母。' + S('381_stage13/config/prereg_addendum9.json（sha256 a9896357…）') + '</p>\n'
      '<h4>2 材料</h4><p>全部 9,108 篇论文的 GPU 数据步骤（72 个分片，149,999 个名字 token 行）：记录模型在 L63、在预测每个名字 token 的位置上的状态；输入用 Stage 11 titlepos 的标题最后一个 token 残差（真标题与 false_0 运行）。' + S(R13 + 'e4b_alltok.md 第 1 节') + '</p>\n'
      '<h4>3 工具</h4><p><code>~/jlens_work/13_stage13/stage13_alltok_probe.py</code>、<code>stage13_alltok_controls.py</code>；作业 11655112、11655130、11655136（GPU）、11655139（probe）、11655152（报告）、11657421（置换对照）。</p>\n'
      '<h4>4 步骤</h4><ol><li>每个角色（首字母、名的第一个 / 其余 token、姓的第一个 / 其余 token），目标 = 该论文该角色各位置 L63 状态的平均。</li><li>ridge，按存档的作者团队分折，只在训练折上标准化，alpha 在第 0 折上选，剔除标题复用的论文。</li><li>预测的状态经 final norm 与反嵌入，在 9,137 个名字 token 的词表里给每个金标准 token 求名次，取 log10(1/名次) 平均。</li><li>标题特异信号 = probe(真标题) − probe(false_0)；目标 − 对照在引用档内比较。</li></ol>\n'
      '<h4>5 公式</h4><p>spec_r(p) = mean_{t ∈ role r} log10(1/rank_t | ŷ(h_true)) − mean_{t} log10(1/rank_t | ŷ(h_false_0))。</p>\n'
      '<h4>6 对照</h4><p>两种置换对照：金标准换成随机另一篇 / 同领域另一篇论文的作者（rng 3712）。</p>\n'
      '<h4>7 结果</h4><p>见上框。目标 − 对照：认得出的论文在标题位置携带更多名字信息，这一差别主要来自首字母和名（L24–L32 起为正，+0.02 到 +0.09）；姓的第一个 token 在 L16–L52 约为 0，L56–L60 才出现 +0.04 到 +0.06。'
      + S(R13 + 'e4b_alltok.md 第 3 节 “Target - control” 矩阵') + '</p>\n'
      '<p><b>敏感性分析（补充 13 C-3）：</b>不剔除标题复用的版本<b>包含标题复用造成的泄漏</b>，只作敏感性分析：全部论文的信号不变（L40 姓的第一个 token +0.077 [0.070, 0.085]，6,841 篇）；其中“姓的第一个 token 目标 − 对照在 L16–L52 显著”不是结论，目标 − 对照以逐个假标题排除的版本为准（补充 10 偏离 D1，计算中）。'
      + S(R13 + 'c13_C3.md · 381_stage13/config/prereg_addendum10_deviations.md') + '</p>\n'
      '<h4>8 局限与质疑</h4><ul><li>置换对照的真金标准列与 probe 逐篇值有一处 0.036 的 WARN：浮点求和顺序使个别 token 名次差 1；两次拟合在全部 63 个格子选到的正则强度相同，报告精度下的数字不受影响。' + S(R13 + 'alltok_deviations.md') + '</li><li>减 5 个假标题平均的版本（补充 10 第 4 项）还在运行。</li></ul>\n'
      '<h4>9 状态</h4><p><span class="st st-done">已完成</span>（2026-11-05）；5 个假标题版本 <span class="st st-plan">进行中</span></p>\n\n')
s = rep(s, '<!-- ====================================================== X3', AT + '<!-- ====================================================== X3')
s = rep(s, '<p><span class="st st-plan">计划未做</span>（与 X4 重合则并入 X4，否则放弃）。无预注册条款。</p>',
        '<p><span class="st st-done">CPU 部分已完成（2026-11-05，事后）</span>：名字位置上的真假判别与标题位置 probe 区分真假运行，见十一 · CPU 补充；名字位置的 probe / patchscope 列入补充 11 A 与补充 12 第 2-7 项（批次 2）。原 2026-10-30 决定：与 X4 重合则并入 X4，否则放弃。</p>')
(P / 'F_stage13.html').write_text(s, encoding='utf-8')

# --- G: M5 rows, V58-V60
s = bk(P / 'G_appendix.html')
s = rep(s, '<tr><td>M5</td><td>提议中的逐位置 probe / patchscope / 名字位置真假判别，无代码、未执行。</td>',
        '<tr><td>M5</td><td>能用已有数据回答的部分 2026-11-05 已在 CPU 上做完（名字位置上的真假判别、标题位置 probe 区分真假运行，见十一 · CPU 补充）；名字位置的 probe / patchscope 列入重做计划（补充 11 A、补充 12 第 2-7 项）。</td>')
s = rep(s, '<tr><td>V29</td><td>M5（逐位置 probe / patchscope / 名字位置真假判别）</td><td><span class="st st-plan">计划未做</span></td>',
        '<tr><td>V29</td><td>M5（逐位置 probe / patchscope / 名字位置真假判别）</td><td><span class="st st-done">CPU 部分已完成（2026-11-05）</span>；GPU 部分列入补充 11、12</td>')
i = s.index('<tr><td>V57</td>'); j = s.index('</tr>', i) + 5
s = s[:j] + ('\n<tr><td>V58</td><td>E4b / 全部 token probe 减 5 个假标题：标题复用改为逐个假标题排除（补充 10 偏离 D1）</td><td><span class="st st-review">偏离</span> 进行中</td><td>按 5 个假标题一起排除时 target + control 剩 0 篇，结果出来前改为逐个假标题排除并锁定。'
             + S('381_stage13/config/prereg_addendum10_deviations.md（sha256 d59da0f0…）') + '</td><td><a href="#s13-alltok">s13-alltok</a></td></tr>'
             '\n<tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）</td><td><span class="st st-plan">不做</span></td><td>用户 2026-11-06 决定不做；只报 CPU 代理（public J-lens 名次指标，不是 W）。'
             + S(R13 + 'c13_C2.md “Decision for batch 3 item 3-4”') + '</td><td><a href="#s19-s8d">s19-s8d</a></td></tr>'
             '\n<tr><td>V60</td><td>补充 9 置换对照与 probe 逐篇值的 0.036 WARN</td><td><span class="st st-done">已查明</span></td><td>浮点求和顺序导致个别 token 名次差 1，正则强度相同，报告数字不受影响。'
             + S(R13 + 'alltok_deviations.md') + '</td><td><a href="#s13-alltok">s13-alltok</a></td></tr>') + s[j:]
s = rep(s, '（用户决定）：X2 暂停 <span class="src">PROGRESS.md 2026-10-30 14:00 条</span>', '（用户决定）：X2 暂停 <span class="src">PROGRESS.md 2026-10-30 14:00 条</span>；2026-11-05 按补充 6 恢复并完成（见 <a href="#s13-x2">s13-x2</a>）')
s = rep(s, '<tr><td>V32</td><td>X2（只替换子空间）</td><td><span class="st st-plan">计划未做</span>（暂停）</td><td>prereg 要求运行前另写补充，未写；无代码；<b>用户 2026-10-30 决定暂停</b>。</td>',
        '<tr><td>V32</td><td>X2（只替换子空间）</td><td><span class="st st-done">已完成（2026-11-05）</span></td><td>2026-10-30 暂停；2026-11-05 写定补充 6 后运行完成（H3 按规则通过但降级，见 V57）。</td>')
(P / 'G_appendix.html').write_text(s, encoding='utf-8')

# --- B: prereg-deviation rows (addendum 9, X7 five titles)
s = bk(P / 'B_global2.html')
i = s.index('<tr><td>X2</td><td>补充 6（2026-11-05 写定'); j = s.index('</tr>', i) + 5
s = s[:j] + ('\n<tr><td>补充 9（全部 token probe）</td><td>L40 姓的第一个 token &gt; 0，且姓 − 首字母</td><td>按规则实现；两项都通过；0.036 WARN 为浮点</td><td><span class="st st-done">已完成</span></td><td>' + S(R13 + 'e4b_alltok.md · alltok_deviations.md') + '</td></tr>'
             '\n<tr><td>X7（5 个假标题，补充 10 第 2 项）</td><td>补充 3 的阈值用于 5 个假标题平均</td><td>按规则实现；false_0 臂逐位复现已发表结果；三组都成立</td><td><span class="st st-done">已完成</span></td><td>' + S(R13 + 'b1_x7f_report.md') + '</td></tr>') + s[j:]
(P / 'B_global2.html').write_text(s, encoding='utf-8')

# --- K: from report v29 Part 5 (figures already embedded, summary table already filled)
rep_html = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html').read_text(encoding='utf-8')
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
K_old = bk(P / 'K_post_defence.html')
K = ('<section id="k-post"><h2>十一 答辩后新增（2026-11-05 / 06）</h2>\n'
     '<p class="lead">答辩材料 2026-11-02/03 定稿之后的工作。分组对比是答辩后新增的分析，分析计划在看结果前写定（补充 7、8）；其余 CPU 补充分析是事后分析；重做计划（补充 10–13）的规则都在看结果前写定。'
     '与《Stage 1–13 实验报告》第 29 版第五部分内容相同（图号、表号沿用报告）。</p>\n' + fr.strip() + '\n</section>')
assert 'p19' not in re.sub(r'data:[^"]*', '', K)
(P / 'K_post_defence.html').write_text(K, encoding='utf-8')

# --- builder header and part title
s = bk(D / 'build_methods.py')
s = rep(s, '2026-11-05 补充（第十一部分：答辩后新增，含分组对比结果；X2 结果；E4b 只打分第一个名字 token 的说明）',
        '2026-11-06 补充（第十一部分：答辩后新增与重做计划；X2、补充 9 全部名字 token 的 probe、X7 五个假标题、补充 13 CPU 项）')
s = rep(s, "('K_post_defence.html', '十一 答辩后新增（2026-11-05）')", "('K_post_defence.html', '十一 答辩后新增（2026-11-05 / 06）')")
(D / 'build_methods.py').write_text(s, encoding='utf-8')
print('ok')
