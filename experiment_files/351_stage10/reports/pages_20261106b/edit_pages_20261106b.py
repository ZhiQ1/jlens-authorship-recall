"""2026-11-06 b sync of the secondary pages (scope update from the user): a dated update box with the user-confirmed batch-1 wording
(PROGRESS 2026-11-06 ~13:30 a-e) + status of batches 2/3, and an inline flag after every statement that later work superseded.
Existing numbers are NOT changed (user rule); superseded statements are only flagged. Every conclusion in the box carries its source.
Pages (local source = live version, checked 2026-11-06 ~21:00 by diff of the saved live copies in this folder):
  advisor        351_stage10/reports/advisor/index.html                 -> https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs
  process report 351_stage10/reports/process_report/draft_zh.md (+ build_process_report.py -> index.html) -> https://claude.ai/artifact/TmqEtZg3gHTz7p7vCkaiB4
  scoring audit  audit_20261105/scoring_audit.html                       -> https://claude.ai/artifact/C6UVJDUtg4JJmkaKBrnwd7
  methods addendum (no local source; live copy saved by Artifact read)  pages_20261106b/methods_addendum/index.html -> https://claude.ai/artifact/VkyyqsvE43k2BkU6VSZ2kg
Backups *.before_20261106b.* are always the input. Usage: python edit_pages_20261106b.py [--pdf]"""
import re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; H = R / 'pages_20261106b'
R13 = '381_stage13/reports/'

def bk(p):
    b = p.with_name(p.stem + '.before_20261106b' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)

# (text, source) pairs; the text is the user-confirmed wording where one exists
ITEMS = [
 ('<b>X1–X4 改为全部作者（批次 1 第 1 项，已完成，硬检查 PASS）：</b>X1–X4 改为给全部作者打分（全部名字 token），并按作者排位分层。结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]）；X3 改写标题保留约 90% 的作者偏好，target 与 control 一样；X4 从 L8 起可解码出作者，各作者排位相同，认得出的论文在 L8–L40 更高；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释。X2 用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009），H3 仍证据不足。',
  R13 + 'b1_xall_report.md：X1 节（测试集，作者 − 年份，团队聚类 bootstrap 2,000 次）；X3 behaviour 表（测试集 552 篇，恢复比 0.897 [0.868, 0.926]）；X4 节（L8，全部作者 +0.048 [0.039, 0.058]；Recognition 表）；X2 verdict 表（L48 R_auth）；New S_auth 表（authall_r2 ≤ 0.009）；Hard check 表'),
 ('<b>E4b 减 5 个假标题（批次 1 第 4 项，已完成）：</b>E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题）：L40 姓首 token +0.076 [0.068, 0.083]，姓 − 首字母 +0.033 [0.023, 0.042]，原 E4b 第一个 token +0.066；置换对照首字母仍 +0.018，其余 ≈ 0；硬检查 E4b L40 +0.0609 PASS。按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正（L40 +0.030，L56 +0.058）；只用 false_0、样本较小时，L56 前不显著。',
  R13 + 'b1_e4b5_report.md：“Per-donor exclusion” 节（Vpd 表、target − control 表、置换对照、primary contrasts）；第 2 节硬检查；目标 + 对照，团队聚类 bootstrap 2,000 次'),
 ('<b>X7 五个假标题（批次 1 第 2 项，已完成）：</b>X7 补做了另外 4 个假标题，按 5 个平均判定，target、control 和全部论文都满足预注册判据（S(L52) 分别为 +0.022、+0.042、+0.028，均 ≤ 0.05）；原来对照组只用 false_0 时为 0.051，属于单个假标题的波动。',
  R13 + 'b1_x7f_report.md（target 593 / control 593 / 全部 1,186 篇，团队聚类 95% CI）'),
 ('<b>C-3b（补充 13，只作敏感性分析，含泄漏，不作结论）：</b>5 个假标题版本不剔除标题复用：硬检查 PASS；L40 姓的第一个 token +0.077 [0.071, 0.084]，首字母 +0.034 [0.029, 0.039]，姓 − 首字母 +0.043 [0.035, 0.051]（6,841 篇）；target − control 的区间几乎处处在 0 以上，与 C-3 一样。',
  R13 + 'c13_C3b.md（Primary contrasts at L40 表 V5x0_noexcl 列）'),
 ('<b>P1 / P2 用 5 个假标题（批次 1 第 3 项）：还在运行</b>，194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算；结果经用户确认后补入。', 'g391_b1p12f 作业链（14_groups/b1_p12f_gpu_v2.sbatch）'),
 ('<b>答辩后已完成、以前写“没做 / 暂停”的项目：</b>X2 只替换子空间（补充 6，2026-11-05）：按预注册判据 H2 不支持、H3 通过，但作者子空间几乎解码不出作者，H3 证据仍不足；全部名字 token 的标题位置 probe（补充 9）：L40 姓的第一个 token +0.071 [0.058, 0.085]；X5 跨问法检索曲线：没有一层高于 L4；M5 能用已有数据回答的部分；CPU 项 C-1 到 C-5（Stage 7.1 加标题对照、Stage 8 CPU 代理、不剔除标题复用的敏感性、M1 换 4 个假标题、Stage 10 附加分析补齐全部已存层）。',
  R13 + 'x2_report.md；e4b_alltok.md 第 5 节；x5_retrieval.md；m5_report.md；c13_C1.md–c13_C5.md'),
 ('<b>批次 2（补充 11、12）：</b>代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始（含 Stage 9 Fit B 与 holdout、F1 对半拆分、名字位置 probe 等）；与预注册的出入记在出入记录 D12-1 到 D12-3（2-1、2-2 较省但含原始提示逐位复现重拟合的硬检查；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述），2-7 的来源改用不含年份的 X4 提示。<b>批次 3（补充 14）：</b>3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写；3-4、3-5（Stage 8 按 W 的 GPU 重算）不做。',
  '381_stage13/config/prereg_addendum11.json、prereg_addendum12.json、prereg_addendum12_deviations.json、prereg_addendum14.json；' + R13 + 'b2_groupA_handoff.md'),
]
SRC = lambda t: f'<span style="color:#8a8f98;font-size:.8em">（{t}）</span>'
FLAG = lambda t: f'<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：{t}；见页首更新框〕</span>'
def box_html(title='2026-11-06 更新：答辩后的重做计划（批次 1 结果，用户已确认措辞）', cls=''):
    lis = ''.join(f'<li>{t}{SRC(s)}</li>' for t, s in ITEMS)
    return (f'<div {cls} style="border:1px solid #D6DEE1;border-left:4px solid #2E6B34;border-radius:4px;padding:12px 16px;margin:12px 0;background:rgba(46,107,52,.06)">'
            f'<p style="margin:0 0 6px"><b>{title}</b></p><p style="margin:0 0 6px;font-size:.92em">以下数字都来自看结果前写定规则的重做项目（补充 9–14），复现已发表数字是每一项的硬检查。本页其余内容保持原样，后来被更新的说法在原处加了橙色标注，原数字未改。</p>'
            f'<ul style="margin:0;padding-left:1.3em">{lis}</ul></div>')
def box_md():
    L = ['## 0. 2026-11-06 更新：答辩后的重做计划（批次 1 结果，用户已确认措辞）', '',
         '以下数字都来自看结果前写定规则的重做项目（补充 9–14），复现已发表数字是每一项的硬检查。本稿其余内容保持原样，后来被更新的说法在原处加了“〔2026-11-06 已更新…〕”标注，原数字未改。', '']
    for t, s in ITEMS:
        L.append('- ' + re.sub(r'</?b>', '**', t) + f'【{s}】')
    return '\n'.join(L) + '\n\n---\n\n'

# ---------------- advisor page
p = R / 'advisor/index.html'; s = bk(p)
s = rep(s, '</header>', '</header>\n<section>' + box_html() + '</section>')
F = [('（control 组 0.051，略高于 0.05 的预注册界线，到 L54–56 降为 0）', 'X7 按 5 个假标题平均，control +0.042，已满足判据'),
     ('但它只给名字第一个 token 打分，而这多半是首字母。</p>', '补充 9 给全部名字 token 打分，L40 姓的第一个 token +0.071；减 5 个假标题平均 +0.076'),
     ('只替换子空间的因果检验（X2）没有做</td>', 'X2 已于 2026-11-05 完成，H3 仍证据不足'),
     ('Fit B 停在 66/100，答辩前不补（lens 拟合稳定性只有一份证据）</td>', 'Fit B 与 holdout 列入批次 2，代码已就绪，自动开始'),
     ('M5 并入 X4；X2 暂停未做</td>', 'X2 已完成；M5 的 CPU 部分已完成；X1–X4 已改为全部作者重做'),
     ('<li>X5 预注册的“跨问法检索”曲线没有计算；X2（只替换子空间）没有做。</li>', 'X5 检索曲线与 X2 都已在答辩后完成'),
     ('<li>lens 的拟合稳定性只有 Stage 9 Fit A 一份证据；作者提示 lens 没做对半拟合。</li>', 'Fit B 与 F1 对半拆分都列入批次 2'),
     ('实验记录 v26：', '当前为第 29 版（本地已备，待发布）'), ('合并 PPT v16：', '当前为 v20（本地已备，待发布）')]
for a, t in F:
    if a.endswith('</td>') or a.endswith('</p>') or a.endswith('</li>'):
        cut = a.rfind('<'); s = rep(s, a, a[:cut] + FLAG(t) + a[cut:])
    else:
        s = rep(s, a, a + FLAG(t))
p.write_text(s, encoding='utf-8'); print('advisor ok')

# ---------------- process report (markdown source, then rebuild)
p = R / 'process_report/draft_zh.md'; s = bk(p)
s = rep(s, '---\n\n## 1. 数据与论证链', '---\n\n' + box_md() + '## 1. 数据与论证链')
FM = lambda t: f'〔2026-11-06 已更新：{t}；见第 0 节〕'
for a, t in [('用户 10-30 决定答辩前不补（V10，U33）。', 'Fit B 与 holdout 列入批次 2，代码已就绪，自动开始'),
             ('- 状态：M4 = Stage 12 F1/F2；M5 并入 X4/放弃；X2 用户暂停。', 'X2 已于 2026-11-05 完成；M5 的 CPU 部分已完成'),
             ('V50 F1 对半拟合；V51 X3 按 token 角色；V56 X5 top-1 检索。', 'X2、M5（CPU 部分）、X5 检索已完成；Fit B、F1 对半、X3 按角色列入批次 2'),
             ('F1 未做对半拟合；X2 未做。', 'X2 已完成；Fit B、F1 对半列入批次 2')]:
    s = rep(s, a, a + FM(t))
p.write_text(s, encoding='utf-8')
subprocess.run([sys.executable, str(R / 'process_report/build_process_report.py')], check=True)
assert '2026-11-06 更新' in (R / 'process_report/index.html').read_text(encoding='utf-8'); print('process report ok')

# ---------------- scoring audit
p = J / 'audit_20261105/scoring_audit.html'; s = bk(p)
AUD = ('<section class="sum">' + box_html('2026-11-06 更新：本审计指出的打分单位问题，答辩后已重做的部分') +
       '<p style="font-size:.9em">对照本审计：只打分第一作者的 X1–X4 已改为全部作者（上框第 1 条）；只减 false_0 的 X7、E4b 已改为 5 个假标题（第 2、3 条）；只打分第一个 token 的 E4b 已由补充 9 扩展到全部名字 token；Stage 5–7 加标题对照见 C-1；Stage 8 的 W 只做了 CPU 代理（C-2），GPU 重算不做。'
       + SRC('PROGRESS.md 2026-11-06 条；381_stage13/config/prereg_addendum10.json、prereg_addendum13.json') + '</p></section>\n')
s = rep(s, '<section class="sum"><h2>要点（主会话汇总）</h2>', AUD + '<section class="sum"><h2>要点（主会话汇总）</h2>')
p.write_text(s, encoding='utf-8'); print('audit ok')

# ---------------- methods addendum (working copy of the live page)
p = H / 'methods_addendum/index.html'; s = bk(p)
s = rep(s, '<nav><ol>', box_html(cls='class="box"') + '\n<nav><ol>')
for a, t in [('<b>L41–L47 和 L49 没有算</b>。', '批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码在写'),
             ('control 的 S(L52) = 0.051 超阈值 0.001，判定 DOES NOT HOLD（边界）；target 0.018、all 0.029 成立。', 'X7 按 5 个假标题平均，三组都成立（control +0.042）'),
             ('Fit B 停在 66/100（作业 11289356 时限到达，检查点可续跑）；9B、9C 没有代码', 'Fit B 续跑与 holdout 列入批次 2（补充 12 第 2-1 项），代码已就绪'),
             ('<li>4,314 个 token：队列内所有作者第 1 个 token ∪ 所有姓的第一个 token；gold 只用每位作者的第 1 个 token。</li>', '补充 9 扩展到全部名字 token，批次 1 第 4 项改为减 5 个假标题平均')]:
    if a.endswith('</li>'):
        s = rep(s, a, a[:-5] + FLAG(t) + '</li>')
    else:
        s = rep(s, a, a + FLAG(t))
p.write_text(s, encoding='utf-8'); print('methods addendum ok')

for f in [R / 'advisor/index.html', R / 'process_report/index.html', J / 'audit_20261105/scoring_audit.html', H / 'methods_addendum/index.html']:
    t = f.read_text(encoding='utf-8'); assert not re.search('minyan', t, re.I), f

if '--pdf' in sys.argv:
    from playwright.sync_api import sync_playwright
    out = R / 'downloads'
    jobs = [(R / 'advisor/index.html', 'jlens_progress_report_2026-11-06b_A4.pdf', 'advisor'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-06b_A4.pdf', 'process'),
            (J / 'audit_20261105/scoring_audit.html', 'scoring_audit_2026-11-06b_A4.pdf', 'audit'), (H / 'methods_addendum/index.html', 'methods_addendum_2026-11-06b_A4.pdf', 'addendum')]
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1000, 'height': 1400})
        for src, name, k in jobs:
            pg.goto(src.as_uri(), wait_until='networkidle', timeout=120000); pg.wait_for_timeout(800)
            el = pg.locator('div:has-text("2026-11-06 更新") >> nth=0') if k != 'process' else pg.locator('h2:has-text("2026-11-06 更新")').first
            pg.locator('text=2026-11-06 更新').first.scroll_into_view_if_needed()
            pg.screenshot(path=str(H / f'chk_{k}_box.png'))
            fl = pg.locator('text=/2026-11-06 已更新/').first
            if fl.count(): fl.scroll_into_view_if_needed(); pg.screenshot(path=str(H / f'chk_{k}_flag.png'))
            pg.emulate_media(media='print')
            pg.pdf(path=str(out / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name)
            pg.emulate_media(media='screen')
        br.close()
