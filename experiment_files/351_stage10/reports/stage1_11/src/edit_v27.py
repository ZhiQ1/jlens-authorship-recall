"""Report v27 (2026-11-05): Stage 1–13; grey source tag after every number (tags_v27/S*.json, one file per segment of v26);
first-token caveat wherever the E4b title-position probe is reported; new Part 5 "答辩后新增（2026-11-05）"
(post_defence_v27.html: group comparisons = plan and status only (user 2026-11-05: no results until re-runs are approved), CPU leftovers, in-progress items).
Usage: python edit_v27.py [out.html]   (input = stage1_11_report.html as v26; backup stage1_11_report.before_20261105b.html)
"""
import os, sys, json, re, base64, shutil, html
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11'
os.chdir(D)
SRC = 'stage1_11_report.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
BK = 'stage1_11_report.before_20261105b.html'
if not os.path.exists(BK):
    shutil.copy2(SRC, BK)
s = open(BK, encoding='utf-8').read()          # always start from v26
assert '第 26 版' in s

# ---------- 1. source tags per segment (positions computed on v26) ----------
ANCH = [('S1a', None), ('S1b', '<h2><span class="st">Stage 7</span>'), ('S2', '<h2>Stage 10–11：全量阶段</h2>'),
        ('S3', '<h2><span class="num">§6</span>'), ('S4', '<h3>6.11 Stage 11：干预'),
        ('S5', '<h2>跨阶段：R0/R1 分层分析与两阶段对照</h2>'), ('S6', '<h2><span class="st">Stage 13 · M3 X1 X4</span>')]
pos = [0] + [s.index(a) for _, a in ANCH[1:]] + [len(s)]
parts, ntag, nfix = [], 0, 0
for i, (k, _) in enumerate(ANCH):
    seg = s[pos[i]:pos[i + 1]]
    fn = f'src/tags_v27/{k}.json'
    if os.path.exists(fn):
        L = json.load(open(fn, encoding='utf-8'))
        hits = []
        for e in L:
            c = seg.count(e['old']); assert c == 1, (k, c, e['old'][:80])
            hits.append((seg.index(e['old']), e))
        hits.sort(key=lambda x: x[0])
        for (a, e), (b, _) in zip(hits, hits[1:]):
            assert b >= a + len(e['old']), (k, 'overlap', e['old'][:60])
        out, last = [], 0
        for a, e in hits:
            out.append(seg[last:a]); out.append(e['new']); last = a + len(e['old'])
            ntag += e['new'].count('class="src"'); nfix += bool(e.get('fix'))
        out.append(seg[last:]); seg = ''.join(out)
    else:
        print('WARN no tag file for', k)
    parts.append(seg)
s = ''.join(parts)
print('tags inserted', ntag, 'number fixes', nfix)


def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:70]); s = s.replace(a, b)


# ---------- 2. CSS ----------
CSS = ('.src{color:#878e99;font-size:.74em;font-weight:400;font-style:normal;letter-spacing:0;line-height:1.35;'
       'font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif}\n'
       '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .src{color:#8d96a4}}\n'
       ':root[data-theme="dark"] .src{color:#8d96a4}\n'
       '.cav{border-left:4px solid #B54708;background:rgba(181,71,8,.07);padding:8px 12px;border-radius:6px;font-size:.92em;margin:8px 0;line-height:1.6}\n'
       '.cav .en{display:block;font-family:"Source Serif 4",Georgia,serif;color:inherit;opacity:.85;margin-top:4px;border:0;padding:0}\n'
       'td .src,th .src{display:block}\n')
rep('</style>', CSS + '</style>', n=s.count('</style>'))  # first style block only is enough, but all are harmless

# ---------- 3. Stage 1–13 naming, version, TOC ----------
rep('<title>Stage 1–11 实验报告</title>', '<title>Stage 1–13 实验报告</title>')
rep('<h1>Stage 1–11 实验报告<small>', '<h1>Stage 1–13 实验报告<small>')
rep('更新于 2026-11-03（第 26 版，答辩定稿）',
    '更新于 2026-11-05（第 27 版：Stage 1–13；答辩后新增见第五部分；正文数字后的灰色小字是出处）')
rep('并加入跨阶段的 R0/R1 分层分析。之后的新实验都只更新本报告和 Stage 1–11 合并 PPT。',
    '并加入跨阶段的 R0/R1 分层分析、Stage 12–13 的正式结果（第四部分）和答辩后新增的分析（第五部分）。之后的新实验都只更新本报告和 Stage 1–13 合并 PPT。'
    '正文中每个数字后的灰色小字注明它来自哪个实验、什么条件、哪种读出和层、哪组样本和多少篇、什么统计量，以及对应的图表或结果文件。')
rep('<a href="#p4-plan">Stage 13 计划</a></span>\n</nav>',
    '<a href="#p4-plan">Stage 13 计划</a></span>\n'
    '<a href="#p5">第五部分 · 答辩后新增（2026-11-05）</a>\n'
    '<span class="sub"><a href="#pd-groups">分组对比（A/B/C/D 等）</a> · <a href="#pd-cpu">CPU 补充（X5 检索、M3 分数、N2 按层、区间对照、M5）</a> · '
    '<a href="#pd-running">进行中（X2、全部 token 的 probe、分组重跑）</a></span>\n</nav>')
rep('<div class="ov" id="ov"><h2>总览：一个问题，四条论证线</h2>',
    '<div class="ov" id="ov"><h2>总览：一个问题，四条论证线</h2>\n'
    '<div class="bx"><b>答辩后新增（2026-11-05），见第五部分。</b>'
    '① 分组对比（A/B/C/D 等，分析计划在看结果前写定，补充 7、8）：CPU 部分已算完，结果先交用户审阅；R2 和识别不确定组的干预重跑、E1 分子/分母分解还在进行，确认之前本报告不写结果数字。'
    '② CPU 补充（事后分析）：X5 跨任务检索没有一层高于 L4 文字水平；M3 分数、N2 按层、论文与团队区间对照、M5。'
    '③ 进行中：X2（补充 6）、全部名字 token 的标题位置 probe（补充 9）、分组重跑（补充 8）。'
    '<br><b>注意：</b>本报告里的标题位置 probe（E4b）只给每位作者名字的<b>第一个 token</b> 打分（多数是首字母）；全部 token、按角色分开的版本（补充 9）还在进行。</div>')

# ---------- 4. first-token caveat at every place the E4b probe is reported ----------
CAV_ZH = ('<b>注意：这里的标题位置 probe（E4b）只给每位作者名字的第一个 token 打分</b>，而 73% 的名字以首字母开头'
          '<span class="src">（Stage 11 E4b 打分规则，gold = 每位作者的第 1 个名字 token；stage11_analyze.py:163–171；方法手册 E4b 节）</span>，'
          '所以多数时候测的是首字母，不是整个名字。给全部名字 token 打分、按首字母 / 名 / 姓分开的版本按补充 9 进行中（GPU 数据步骤排在分组重跑和 X2 之后），尚无结果。')
CAV_EN = ('Note: this title-position probe (E4b) scores only the first token of each author name (73% of names start with an initial, '
          'so mostly an initial), not the whole name. The all-token version split by role (initial / given name / surname) is in progress '
          'under addendum 9; no result yet.')
CAV_BI = f'<div class="cav">{CAV_ZH}<span class="en">{CAV_EN}</span></div>'
CAV_ZH_ONLY = f'<div class="cav">{CAV_ZH}</div>'


def after_pair(phrase, block=CAV_BI):
    """insert block after the <div class="pair"> (zh p + en p) that contains phrase"""
    global s
    assert s.count(phrase) == 1, (s.count(phrase), phrase)
    i = s.index(phrase); e1 = s.index('</p>', i); e2 = s.index('</p>', e1 + 4); e3 = s.index('</div>', e2) + 6
    assert '<p class="en">' in s[e1:e2] and s[e2 + 4:e3 - 6].strip() == '', s[e1:e3][:200]
    s = s[:e3] + '\n  ' + block + s[e3:]


def after_tag(phrase, close, block):
    global s
    assert s.count(phrase) == 1, (s.count(phrase), phrase)
    i = s.index(phrase); e = s.index(close, i) + len(close)
    s = s[:e] + block + s[e:]


after_pair('才变成 lens 能读出的形式。标题最后一个 token 上，线性 probe')       # §1 summary
after_pair('换成线性 probe（5 折 ridge 回归')                               # §6.11
after_pair('标题位置 probe 的对照检验。</b>§6.11 中线性 probe')                  # §6.12
after_tag('但在标题最后一个 token 上，线性 probe 从 L24 起', '</div></div>', CAV_BI)   # §7 finding
after_tag('标题位置的线性 probe：R0 口径的目标−对照', '</p>', CAV_ZH_ONLY)          # Part 3 R0/R1
after_tag('作者首 token（E4b probe，标题位置）', '</table>', CAV_ZH_ONLY)            # X5 layer-order table
after_tag('换成在标题最后一个 token 上训练的线性 probe', '</p>', CAV_ZH_ONLY)        # Stage 13 plan, H2 text
rep('E4b 复核结果（作业 11443587，13:00）</b>', 'E4b 复核结果（作业 11443587，13:00）</b>' + CAV_ZH_ONLY)

rep('预注册写的“跨任务检索 top-1”曲线没有计算（与预注册的出入）。',
    '预注册写的“跨任务检索 top-1”曲线答辩时没有计算（与预注册的出入）；2026-11-05 已补算，没有一层高于 L4 文字水平，见<a href="#pd-cpu">第五部分</a>。')
# ---------- 4b. wording decisions of the user (2026-11-05 afternoon) ----------
DUA = 'Dreaming Up Authors 代码包 ~/archives/dreaming-up-authors-code-v0.zip'
L48TAG = ('<span class="src">（Stage 10，真标题 − 5 个假标题平均，引用档内目标−对照，三种 Jacobian lens L48 为 −0.037 到 −0.054，区间不含 0；'
          'L24–L40 约为 0；351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv）</span>')
W = [
 # 1. L48 recovery 0.825 -> 82%
 ('L48 已恢复 83%', 'L48 已恢复 82%', 2), ('recovers 83% at L48', 'recovers 82% at L48', 1), ('L48 恢复 83%', 'L48 恢复 82%', 2),
 # 2. one source for the R0-only intervals (r0_sensitivity.md)
 ('0.187, 0.212', '0.188, 0.212', None), ('0.086, 0.133', '0.086, 0.135', None),
 # 3. 2.4x
 ('真标题让平均名次再好约 2.4 倍', '真标题让平均名次比假标题好约 2.4 倍（比不给标题好约 1.9 倍）', 1),
 ('The true title improves the average rank by about 2.4×', 'The true title improves the average rank by about 2.4× over a false title (about 1.9× over no title)', 1),
 # 4. section 7 finding 3
 ('相对对照组的优势只出现在最后两层', '相对对照组的优势在 J-lens 下只在最后两层明显；logit lens 在 L56 已有 +0.065，上升最快在 L57–61', 1),
 ('their advantage over control appears only in the last two layers', 'their advantage over control is clear only in the last two layers with the J-lenses; the logit lens already shows +0.065 at L56, and the steepest rise is over L57–61', 1),
 # 5. team folds
 ('随机分折时，约 80% 的测试论文会被去掉', '按团队分折时，约 80% 的测试论文会被去掉', 1),
 # 6. middle layers (target - control)
 ('全量在引用档内比较：中间层约为 0，输出处 +0.21', '全量在引用档内比较：L24–L40 约为 0；L48 略为负（−0.04 到 −0.05，区间不含 0）' + L48TAG + '；输出处 +0.21', 1),
 ('<td>输出 +0.21，中间层约 0</td>', '<td>输出 +0.21；L24–L40 约为 0，L48 略为负（−0.04 到 −0.05，区间不含 0）</td>', 1),
 ('<td>输出 +0.21 [0.20, 0.22]，中间层约 0</td>', '<td>输出 +0.21 [0.20, 0.22]；L24–L40 约为 0，L48 略为负（−0.04 到 −0.05，区间不含 0）</td>', 1),
 # 7. field coverage: real source in the DUA package; the unsourced 100,000 sample is removed
 ('8 个领域是在初始集合中随机抽 100,000 篇、按出现频率选出的，合计约占整理后数据的 76.95%<span class="src">（Dreaming Up Authors 原研究的数据说明（用户提供的 Dataset Provenance 文稿）；代码包与项目结果目录中出处文件未找到）</span>',
  '8 个领域按 Semantic Scholar 的主领域（fieldsOfStudy 第一项）计，合计 1,478,297 篇，约占过滤后 1,921,209 篇的 76.95%<span class="src">（' + DUA + ' src/dua/sampling/stratified.py:39–44 primary_field；src/dua/data/distributions.py:93–96）</span>', 1),
 ('The 8 fields were chosen by their frequency in a random sample of 100,000 papers from the initial collection; together they cover about 76.95% of the curated data<span class="src">(data description of the original Dreaming Up Authors study (user-provided Dataset Provenance text); source file not found in the code package or project results)</span>',
  'Counted by the Semantic Scholar primary field (first fieldsOfStudy entry), the 8 fields hold 1,478,297 of the 1,921,209 filtered papers, about 76.95%<span class="src">(Dreaming Up Authors code package ~/archives/dreaming-up-authors-code-v0.zip, src/dua/sampling/stratified.py:39–44 primary_field; src/dua/data/distributions.py:93–96)</span>', 1),
 ('；报告原出处文件未找到）', '）', 1),
 ('合并口径 +0.207 [0.195, 0.220]；论文 bootstrap 95% CI；351_stage10/reports/r0_r1_analysis.md §1）</span>，各层形状相同', '合并口径 +0.207 [0.195, 0.220]；论文 bootstrap 95% CI；351_stage10/reports/r0_sensitivity.md）</span>，各层形状相同', 1),
 # 8. remaining small items of the source-tag issue lists
 ('351_prepare_all.py 保留 group_tight = target/control 且 HR2 &gt; 0.5 的论文', '351_prepare_all.py 保留 group_tight = target/control 的论文，HR2 &gt; 0.5 只作自检断言', 1),
 ('（0-2 档目标组占 25%，4097+ 档占 99%', '（0-2 档认出（4/4）的论文占 25%，4097+ 档占 99%', 1),
 ('(target share 25% in bin 0-2, 99% in 4097+', '(share recognised 4/4: 25% in bin 0-2, 99% in 4097+', 1),
 ('主轮实际约 7 GPU 小时', '主轮实际约 6.4 GPU 小时', 1), ('about 7 GPU-hours', 'about 6.4 GPU-hours', 1),
 ('均值的置信区间宽度均小于 ±0.01', '均值的置信区间半宽最大约 ±0.011', 1), ('CIs of the means are narrower than ±0.01', 'CI half-widths of the means are at most about ±0.011', 1),
 ('<strong class="k">+0.247</strong> [0.230, 0.265]', '<strong class="k">+0.247</strong> [0.230, 0.266]', 2),
 ('/scratch/zhang.zhiqi2/jlens/351_stage10/summary_title/C_graded_mc_team_a.csv</span></div>',
  '/scratch/zhang.zhiqi2/jlens/351_stage10/summary_title/C_graded_mc_team_a.csv</span> · <span class="mono">/scratch/zhang.zhiqi2/jlens/351_stage10/summary/C_graded_mc_team_a.csv（正文数字，metric=mean_nlr）</span></div>', 1),
 ('正则化强度不变，没有任何区间从“不含 0”变成“含 0”', '正则化强度不变，确认版配置中没有任何区间从“不含 0”变成“含 0”', 1),
 ('no CI changes whether it contains 0.', 'in the confirmatory configuration no CI changes whether it contains 0.', 1),
 ('恢复比例只有约 0.12（L8–L40）', '恢复比例只有约 0.12–0.15（L8–L40）', 1), ('recovers about 0.12 (L8–L40)', 'recovers about 0.12–0.15 (L8–L40)', 1),
 ('到 L52 两者都恢复 0.97 以上', '到 L52 两者都恢复约 0.97 及以上', 1),
 ('三组全部满足，各假标题之间的差都不超过 0.02', '三组全部满足，每个假标题与 false_0 的差都不超过 0.02', 1),
 ('（标题位置 −0.003 到 −0.016，', '（标题位置 −0.003 到 −0.017，', 1),
 ('换问法的移动距离是换论文的 3–5 倍', '换问法的移动距离在 L4–L40 是换论文的 3–5 倍（L48 约 2.2 倍）', 1),
 ('同领域里与原标题词重合超过 0.3 的论文只占 2.4%', '为每个标题选出的同领域近邻 D 中，与原标题词重合超过 0.3 的只占 2.4%', 1),
 ('Fit A 4/100，Fit B 0/100，holdout 未评估', 'Fit A 4/100，Fit B 0/100（档案记录时；之后 Fit B 检查点停在 66/100），holdout 未评估', 1),
]
for a_, b_, n_ in W:
    c_ = s.count(a_)
    assert (c_ >= 1) if n_ is None else (c_ == n_), (c_, a_[:60])
    s = s.replace(a_, b_)
# tags of the R0-only intervals now cite r0_sensitivity.md
s = re.sub(r'(<span class="src">[^<]*?(?:0\.188, 0\.212|0\.086, 0\.135)[^<]*?)351_stage10/reports/r0_r1_analysis\.md §[12]', r'\g<1>351_stage10/reports/r0_sensitivity.md', s)
assert '出处文件未找到' not in s and 'source file not found' not in s
assert '0.187, 0.212' not in s and '0.086, 0.133' not in s

# ---------- 5. Part 5: post-defence ----------
G = '/scratch/zhang.zhiqi2/jlens/391_groups'
frag = open('src/post_defence_v27.html', encoding='utf-8').read()
for key, fn in [('{{FIG2}}', 'fig2_signal_vs_mc.png'), ('{{FIG3}}', 'fig3_primary_contrasts.png')]:
    frag = frag.replace(key, 'data:image/png;base64,' + base64.b64encode(open(f'{G}/figures/{fn}', 'rb').read()).decode())
import csv
rows = list(csv.reader(open(f'{G}/summary_table.csv', encoding='utf-8')))
HEAD_ZH = ['组', '输出层信号，未写出作者（L63）', '输出层信号，写出的作者（参照）', 'E1 替换恢复 L48（未写出）', 'E1 替换恢复 L52（未写出）',
           'E2 阻断损失 L52（未写出）', 'E4b probe 标题特异 L40（每篇，全部作者；只打分第一个名字 token）',
           'M2“认得出”AUROC（对 B，“:” L52，描述）', 'X3 行为恢复，测试集（第一作者未写出）']
t = ['<div class="tw"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in HEAD_ZH) + '</tr></thead><tbody>']
for r in rows[1:]:
    t.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in r) + '</tr>')
t.append('</tbody></table></div>')
frag = frag.replace('{{SUMMARY_TABLE}}', '<p class="note">表 P5.1 各组汇总</p>\n' + '\n'.join(t))
assert '{{' not in frag
assert s.rstrip().endswith('</main></div>'), s[-80:]
s = s.rstrip() + '\n' + frag + '\n'

assert not re.search('minyan', s, re.I)
open(OUT, 'w', encoding='utf-8').write(s)
print('wrote', OUT, len(s))
