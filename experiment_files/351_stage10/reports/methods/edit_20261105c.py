"""Handbook update 2026-11-05 evening (user decisions ~17:20): part K rebuilt from report v28 Part 5 (group results, re-runs);
X2 section (s13-x2) with results; H2/H3 summary; prereg-deviation row and V57 for X2; M1/M2 bootstrap count fixed (200, not 1,000).
Backups *.before_20261105c.* (edits always start from them). Then run build_methods.py."""
import re, shutil, base64, csv, html
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods'); P = D / 'parts'
def bk(p):
    b = p.with_name(p.stem + '.before_20261105c' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
S = lambda t: f'<span class="src">{t}</span>'

# --- B: bootstrap count for stage13_cpu.py (M1/M2); prereg-deviation row for X2
s = bk(P / 'B_global2.html')
s = rep(s, '<tr><td>13_stage13/stage13_cpu.py（M1/M2）</td><td>论文</td><td><b>1,000</b></td>',
        '<tr><td>13_stage13/stage13_cpu.py（M1/M2）</td><td>论文</td><td><b>200</b>（M2 探针区间；boot() 第 176–180 行，按论文有放回重抽 200 次；第 26 行的 B = 1000 已定义但未使用；M1 不做重抽）'
        + S('~/jlens_work/13_stage13/stage13_cpu.py:26（rng = default_rng(3813); B = 1000，全文未再引用 B）、:176–180（def boot … for _ in range(200)）') + '</td>')
i = s.index('<tr><td>X2</td><td>X2 运行前另写补充</td>'); j = s.index('</tr>', i) + 5
s = s[:i] + ('<tr><td>X2</td><td>补充 6（2026-11-05 写定，sha256 5eea3c4a…）：S_id / S_auth / 3 个随机 10 维子空间；搬运臂在调参集选层、测试集确认；H2：S_id 带得过去且 R_id ≥ 0.5 × R_full；H3：S_auth 带得过去且 R_auth − R_id &gt; 0</td>'
             '<td>按规则实现（2026-11-05，24 个分片，分析作业 11655257）：H3 按规则通过、H2 不支持；S_id 只有 9 维（8 个领域方向之和为 0）；调参集选层取 R_S − R_rand 最大的层；移除臂的 S_full 只作参照；因作者子空间本身几乎解码不出作者（留出 R² ≤ 0.003，猜中率 0.078–0.079 &lt; 常数基线 0.080），H3 降级为“证据仍不足”，与 X3 的处理方式相同</td>'
             '<td><span class="st st-done">已完成</span> <span class="st st-review">偏离</span></td><td>' + S('381_stage13/reports/x2_report.md “Verdict”“Subspace fits”“Deviations from addendum 6” · 附录 V57') + '</td></tr>') + s[j:]
(P / 'B_global2.html').write_text(s, encoding='utf-8')

# --- F: X2 section with results; H2/H3 summary
s = bk(P / 'F_stage13.html')
i = s.index('<h3 id="s13-x2">'); j = s.index('<!-- ====================================================== X3')
X2 = ('<h3 id="s13-x2">X2　只替换子空间（因果）</h3>\n'
  '<div class="fix"><b>2026-11-05 完成。</b>按预注册判据，H3 通过、H2 不支持。但作者子空间本身几乎解码不出作者（留出 R² ≤ 0.003，第一作者名字 token 猜中率 0.078–0.079，低于常数基线 0.080），它搬动的量只有完整替换的约 4%，因此不能作为 H3 的有力证据。从标题传到作者名字的信息，几乎全部分散在这两个子空间之外。'
  + S('381_stage13/reports/x2_report.md “Verdict”“Subspace fits” · summary_x2/x2_verdict.csv、fit_sanity.csv') + '</div>\n'
  '<h4>1 问题与作用</h4><p>从标题带到作者名字的信息，是在“论文属性”的低维方向里（H2），还是在“作者”的低维方向里（H3），还是都不是？做法是只替换或抹掉这些方向，看第一作者的分数是否跟着走。' + S('381_stage13/config/prereg_addendum6.json “question”') + '</p>\n'
  '<p>注意：Stage 10 也有一个叫“X2”的分析（引用数分箱，<code>stage10_extra.py</code>），与此无关。</p>\n'
  '<h4>2 材料</h4><p>配对与 X1 相同：标题等长的 1,178 对（调参集 596、测试集 582，按作者团队划分）。子空间在不属于任何配对团队的 5,041 篇训练论文上拟合（M3 残差缓存，作者问法不含年份，标题最后一个 token）。'
  + S('x2_report.md 首段与 “Subspace fits” 表 · config/pairs.parquet · summary_m3/resid_cache.f16') + '</p>\n'
  '<h4>3 工具</h4><p><code>~/jlens_work/13_stage13/stage13_x2.py</code>（拟合 + GPU 替换），<code>stage13_x2_analyze.py</code>（汇总）；GPU 作业 11637663（分片 0）、11654745（分片 1–13，被系统 kill 后续跑）、11655027（分片 14–23），分析作业 11655257。'
  + S('PROGRESS.md 2026-11-05 X2 条目') + '</p>\n'
  '<h4>4 步骤</h4><ol><li>每层（L16、L24、L32、L40、L48）用 ridge 拟合 S_id：年份、log 引用数、8 个领域的读出方向，QR 正交化（9 维）；S_auth：预测第一作者首 token 反嵌入的 10 个方向；S_rand：3 个随机 10 维子空间（种子 61–63）。</li>'
  '<li>搬运臂：在 B 的作者提示里，把每个标题位置的状态改为 h_B + P_S(h_A − h_B)，给 A 的第一作者打分。</li>'
  '<li>移除臂：在 A 自己的提示里，把状态改为 h_A − P_S(h_A − μ)（μ = 训练均值）。</li>'
  '<li>调参集上选 R_S − R_rand 最大的层，测试集上确认；区间为作者团队聚类 bootstrap（2,000 次）。</li></ol>\n'
  '<h4>5 公式</h4><p>R_S = mean(patched − corrupt) / mean(clean − corrupt)；L_S = mean(clean − removed) / mean(clean − corrupt)；分数 = 第一作者名字 token 的 log10(1/名次) 平均（教师强制）。' + S('x2_report.md 首段') + '</p>\n'
  '<h4>6 对照</h4><p>S_rand（3 个随机 10 维子空间的平均）；S_full（完整替换，= X1）作上限；S = 0（恒等替换）作自检。</p>\n'
  '<h4>7 结果</h4><table class="t"><tr><th>子空间</th><th>调参集选的层</th><th>测试集 R_S</th><th>R_rand</th><th>R_full</th><th>R_S − R_rand [95% CI]</th><th>移除臂 L_S − L_rand [95% CI]</th></tr>'
  '<tr><td>S_id（9 维）</td><td>L40</td><td>+0.005</td><td>+0.003</td><td>+0.920</td><td>+0.002 [−0.001, +0.005]</td><td>+0.001 [−0.003, +0.005]</td></tr>'
  '<tr><td>S_auth（10 维）</td><td>L48</td><td>+0.018</td><td>+0.003</td><td>+0.428</td><td>+0.015 [+0.010, +0.020]</td><td>+0.001 [−0.004, +0.006]</td></tr></table>'
  '<p>H2：R_id +0.005 &lt; 0.5 × R_full +0.460（L40）→ 不支持。H3：R_auth − R_id +0.014 [+0.008, +0.020]（L48）→ 按规则通过。S_auth 的作者映射留出 R² 0.0009–0.0033，猜中率 0.078–0.079（L16–L48 各层；常数基线 0.080）；S_id 的年份 R² 0.36–0.52、引用数 R² 0.26–0.49、领域准确率 0.68–0.71。R_auth / R_full = 0.018 / 0.428 ≈ 4%。'
  + S('x2_report.md “Verdict”与 “Subspace fits” 表；测试集 582 对') + '</p>\n'
  '<h4>8 局限与质疑</h4><ul><li>H3 按规则通过，但作者子空间本身几乎没有解码能力，搬动量只有完整替换的约 4%，降级为“证据仍不足”（与 X3 的处理方式相同；附录 V57）。</li>'
  '<li>S_id 只有 9 维（同一 alpha 下 8 个领域方向之和为 0），与 10 维随机子空间比较对 S_id 略偏保守。</li>'
  '<li>“调参集选层”取 R_S − R_rand 最大的层（沿用 X1 规则）；移除臂的 S_full 只作参照（补充 6 只为搬运臂定义 S_full）。</li>'
  '<li>自检 WARN：S = 0 在 GPU 上不逐位相同（最大差 0.103，bf16 批量舍入）；3 个随机子空间之间只有搬运臂 L24 一处差 +0.003 [+0.001, +0.006]。</li></ul>'
  + S('x2_report.md “Checks”“Deviations from addendum 6”') + '\n'
  '<h4>9 状态</h4><p><span class="st st-done">已完成</span>（2026-11-05） <span class="st st-review">偏离</span>（H3 降级；见附录 V57）</p>\n\n')
s = s[:i] + X2 + s[j:]
s = rep(s, '<li><b>H3</b>：X4 文本基线不弱于 Qwen，不能排除文字解释，证据不足；X2 暂停，H3 没有因果检验（<a href="#s13-x2">s13-x2</a>）。</li>',
        '<li><b>H3</b>：X4 文本基线不弱于 Qwen，不能排除文字解释，证据不足；X2 按规则通过但子空间无解码能力，证据仍不足（<a href="#s13-x2">s13-x2</a>）。</li>')
s = rep(s, '与 H2 预测的方向相反（<a href="#s13-x4">s13-x4</a>）。', '与 H2 预测的方向相反（<a href="#s13-x4">s13-x4</a>）。X2 不支持 H2（<a href="#s13-x2">s13-x2</a>）。')
(P / 'F_stage13.html').write_text(s, encoding='utf-8')

# --- G: deviation list V57
s = bk(P / 'G_appendix.html')
i = s.index('<tr><td>V56</td>'); j = s.index('</tr>', i) + 5
s = s[:j] + ('\n<tr><td>V57</td><td>X2 的 H3 判定（补充 6）</td><td><span class="st st-done">已完成（2026-11-05）</span> <span class="st st-review">偏离</span></td>'
             '<td>X2 的 H3 判定按规则通过，但因子空间本身无解码能力而降级，与 X3 的处理方式相同。另：S_id 只有 9 维；调参集选层取 R_S − R_rand 最大的层；移除臂 S_full 只作参照。'
             + S('381_stage13/reports/x2_report.md “Verdict”“Subspace fits”“Deviations from addendum 6”') + '</td><td><a href="#s13-x2">s13-x2</a>、<a href="#h-prereg-dev">h-prereg-dev</a></td></tr>') + s[j:]
(P / 'G_appendix.html').write_text(s, encoding='utf-8')

# --- K: post-defence part, from the report fragment
fr = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/src/post_defence_v28.html').read_text(encoding='utf-8')
fr = re.sub(r'<div class="partbar".*?</div>\s*<div class="p19"><main>', '', fr, flags=re.S)
fr = fr.replace('</main></div>', '')
fr = fr.replace('<section id="pd-groups"><h2>', '<h3 id="k-groups">').replace('<section id="pd-cpu"><h2>', '<h3 id="k-cpu">').replace('<section id="pd-running"><h2>', '<h3 id="k-running">')
fr = re.sub(r'</h2>', '</h3>', fr); fr = fr.replace('</section>', '')
fr = re.sub(r'<h3>', '<h4>', fr); fr = re.sub(r'<h3>(.*?)</h3>', r'<h4>\1</h4>', fr)
# h3 without id were turned into h4 above; close tags of those: fix pairing
fr = re.sub(r'<h4>(.*?)</h3>', r'<h4>\1</h4>', fr, flags=re.S)
fr = fr.replace('<span class="ln lA">A 这篇论文？</span>', '').replace('<span class="ln lC">C 哪一层</span>', '')
fr = re.sub(r'<span class="st">([^<]*)</span>', r'<span class="st st-done">\1</span>', fr)
fr = fr.replace('<span class="st st-done">进行中</span>', '<span class="st st-plan">进行中</span>')
fr = fr.replace('<div class="bx">', '<div class="fix">').replace('<table>', '<table class="t">')
fr = fr.replace('见第四部分的说明', '见本手册 M5 节')
fr = fr.replace('#x2-results', '#s13-x2').replace('第四部分 <a href="#s13-x2">X2</a>', '<a href="#s13-x2">六 · X2</a>')
assert 'p19' not in fr
G = '/scratch/zhang.zhiqi2/jlens/391_groups'
for key, fn in [('{{FIG2}}', 'fig2_signal_vs_mc.png'), ('{{FIG3}}', 'fig3_primary_contrasts.png')]:
    fr = fr.replace(key, 'data:image/png;base64,' + base64.b64encode(open(f'{G}/figures/{fn}', 'rb').read()).decode())
rows = list(csv.reader(open(f'{G}/summary_table.csv', encoding='utf-8')))
H = ['组', '输出层信号，未写出作者（L63）', '输出层信号，写出的作者（参照）', 'E1 恢复 L48（未写出）', 'E1 恢复 L52（未写出）', 'E2 阻断损失 L52（未写出）',
     'E4b probe 标题特异 L40（只打分第一个名字 token）', 'M2“认得出”AUROC（对 B，“:” L52，描述）', 'X3 行为恢复，测试集（第一作者未写出）']
OVR = {'U0': {3: '+0.844 [+0.814, +0.877]; n = 599 (2096 authors)', 4: '+1.000 [+0.988, +1.012]; n = 599 (2096 authors)', 5: '+0.003 [-0.009, +0.014]; n = 599 (2096 authors)'},
       'R2s': {3: '+0.792; n = 28; 参照，不给区间', 4: '+1.027; n = 28; 参照，不给区间', 5: '-0.017; n = 28; 参照，不给区间'}}
for r in rows[1:]:
    for ci, v in OVR.get(r[0], {}).items(): r[ci] = v
t = '<div class="tw"><table class="t"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in H) + '</tr></thead><tbody>' + ''.join(
    '<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
fr = fr.replace('{{SUMMARY_TABLE}}', '<p class="note">表 P5.1 各组汇总</p>' + t)
assert '{{' not in fr
K = ('<section id="k-post"><h2>十一 答辩后新增（2026-11-05）</h2>\n'
     '<p class="lead">答辩材料 2026-11-02/03 定稿之后的工作。分组对比的分析计划在看结果前写定（补充 7、8）；其余 CPU 补充分析是事后分析，只作描述；进行中的实验只写状态。'
     '与《Stage 1–13 实验报告》第 28 版第五部分内容相同（图号、表号沿用报告）。</p>\n' + fr + '\n</section>')
K_old = bk(P / 'K_post_defence.html')
(P / 'K_post_defence.html').write_text(K, encoding='utf-8')

# --- builder header date
s = bk(D / 'build_methods.py')
s = rep(s, '2026-11-05 补充（第十一部分：答辩后新增；E4b 只打分第一个名字 token 的说明）', '2026-11-05 补充（第十一部分：答辩后新增，含分组对比结果；X2 结果；E4b 只打分第一个名字 token 的说明）')
(D / 'build_methods.py').write_text(s, encoding='utf-8')
print('ok')
