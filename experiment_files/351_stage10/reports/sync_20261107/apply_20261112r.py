"""Round r (PRIORITY build for the talk, 2026-11-12 evening; user/coordinator: only the priority slides change).
Base = v21 deck / notes / slides.json as they were before round r (backups *.before_20261112r, written here once).
Priority slides (old numbers): 59, 6, 20, 23, 21, 35, 44, 45, 46, 49, 67, 68, 72, 65, 78, 82 + two NEW slides after 72
(name-position probe; C24). New numbering: new slides 73, 74; old 73..82 -> 75..84.
- 67, 68, 72: replaced by chart slides (r_frag/, apply_20261112r_charts.py); new np / c24 slides from the same script.
- 65: header date patch (r_frag/slide65.html from apply_20261112r_frag_b.py).
- 21: CI method statement + "团队级补算进行中"; 59: P1/P2 five-title mean as main, false_0 in parentheses;
  82: chart (E1 denominators) + "C24 使用模型自生成文本，非 teacher forcing".
- every priority slide: one-line 怎么算; its note = ~1-minute Chinese talk script + full five-line 怎么算.
Manifest: sync_20261108c_manifest.md "round r (deck charts, priority build)"."""
import json, re, shutil, sys, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import apply_20261112r_lib as L
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'merged_deck/stage1_11_deck.html'
N = R / 'talk/src/export/notes_zh.json'; S = R / 'talk/src/export/slides.json'; FR = Path(__file__).parent / 'r_frag'
SUF = '.before_20261112r'
for p in (D, N, S):
    b = p.with_name(p.name + SUF)
    if not b.exists(): shutil.copy2(p, b)
h = (D.with_name(D.name + SUF)).read_text(encoding='utf-8')
notes = json.loads(N.with_name(N.name + SUF).read_text(encoding='utf-8')); slides = json.loads(S.with_name(S.name + SUF).read_text(encoding='utf-8'))
H = json.load(open(FR / 'charts_how.json', encoding='utf-8'))
man = []

# ---- split sections
st = [m.start() for m in re.finditer(r'<section[^>]*class="[^"]*slide', h)]
end = h.index('</div>\n<nav')
head, secs, tail = h[:st[0]], [h[a:b] for a, b in zip(st, st[1:] + [end])], h[end:]
assert len(secs) == 82, len(secs)
def sec(n): return secs[n - 1]
def put(n, s, what):
    secs[n - 1] = s; man.append((f'deck slide {n}', what))
def sub1(n, a, b, what):
    s = sec(n); assert s.count(a) == 1, (n, a[:50], s.count(a)); put(n, s.replace(a, b), what)

HOWR = lambda left, top, width, txt: f'<div class="howr" style="left:{left}px;top:{top}px;width:{width}px"><b>怎么算：</b>{L.esc(txt)}</div>'
def svg_one(n, x, y, maxw, txt):
    t, _ = L.para(x, y, '怎么算：' + txt, 10.5, maxw, '#4B5363', lh=13.2)
    s = sec(n); i = s.rindex('</svg>'); put(n, s[:i] + f'<g data-name="how computed (one line)">{t}</g>' + s[i:], 'one-line 怎么算 (SVG text)')

# ---- five-line blocks for the non-chart priority slides (same quantity -> same wording, lib F / CI)
F, C = L.F, L.CI
FIVE = {
 59: L.how(f"{F['spec']}；{F['rec']}；{F['tc']}", 'Stage 10 全部 9,108 篇（lens，名字位置，L62 四种读出 0.436–0.463）；Stage 11/12 样本 1,186 篇（E1、P1、P2，标题之后的位置）；补充 9 标题位置 probe 1,395–1,706 篇',
           '5 个假标题（Stage 10；P1 / P2 五标题平均，括号内为只用 false_0）；E1 与标题位置 probe 只减 false_0；control 组（同一引用档）', 'Stage 10–12 表：' + C['paper'] + '；P1 / P2 五标题平均与补充 9：' + C['team'],
           '351_stage10/summary_extra/X3_means.csv；361_stage11/summary/E1_recovery.csv；391_groups/summary_b1_p12f/p12f_mean5.csv；summary_title/B_spec_target_vs_control_within_bin.csv；381_stage13/reports/e4b_alltok.md'),
 6: L.how('计数：recall_level × 多选结果（A = R0 × strong，B = R0 × fail，C = R1 × strong，D = R1 × fail）；target = A + C，control = B + D', 'Stage 10 队列 9,108 篇；Stage 11–13 干预样本 593 + 593 篇（每个引用档取 min(60, n_t, n_c)，seed 11）；X1 / X3 配对 1,178 对',
          'control = 写不全、也认不出名单的论文（B + D），只在同一引用档内比较', '无区间（计数）', '351_stage10/cohort/papers.parquet；361_stage11 样本表；381_stage13 X1 / X3 配对表'),
 20: L.how(f"{F['nlr']}；{F['rank']}；{F['spec']}", '1 篇示例论文（Coifman, Bonanno, Rafaeli 2007），最终输出 L63，16 个名字 token 的平均（图中只画作者 1）', '5 个假标题 false_0..4；删标题（total = true − delete，topic = mean false − delete）', C['none'],
           '351_stage10/raw/[cond_*/]final/L63/shard_011.npz 第 25025–40 行；351_stage10/summary_title/paper_title_contrasts.parquet（final, L63）'),
 21: L.how(F['tc'], '引用档 0-2 … 513-1024 共 10 档（两组都 ≥ 30 篇的档才用）；9,108 篇论文共 7,247 个作者团队（共享作者全名 = 同一团队）', 'control 组，只在同一引用档内比较',
           'Stage 10–12 已发表的表：' + C['paper'] + '；Stage 13 起（补充 2）以' + C['team'] + '为主；Stage 10–12 的团队级补算进行中', '351_stage10.py:670–691 stratified_diff()；381_stage13/reports/cluster_ci.md'),
 23: L.how(f"{F['prior']}；四项各自做档内 target − control", '全部 9,108 篇（不给标题时平均约第 12 名 = 10^1.089）；target 4,621 / control 2,220 篇，最终输出 L63，全部名字 token 与姓的第一个 token；rho：R0 / R1 8,894 篇', '删标题（先验）、5 个假标题（主题、论文特有）', C['paper'],
           '371_stage12/summary_cpu/A_prior_decomposition.csv；371_stage12/summary_cpu/B_prior_vs_recognition.csv'),
 35: L.how(f"{F['nlr']}；{F['rank']}", '1 篇示例论文，作者 1 的第 5 个 token “Co”；logit lens，L24–L62 与最终输出 L63；右图为 7 个 token 的平均 nlr', 'false_0', C['none'],
           '351_stage10/raw/logit/L{24…62}/shard_011.npz 第 25029 行；raw/final/L63'),
 44: L.how(f"{F['spec']}；{F['tc']}", 'target 3,734 + control 2,182 篇（10 个引用档），名字位置全部 token，L24–L62 与最终输出；只用 R0：A 3,423 / B 2,151 篇', '5 个假标题；control 组（同档）', C['paper'],
           '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv；351_stage10/reports/r0_sensitivity.md'),
 45: L.how(f"{F['spec']}；{F['tc']}", 'target 3,734 + control 2,182 篇，名字位置全部 token，L40–L62（3-1 之后补了 L41–L47、L49：logit 在 L41–L49 都在 ±0.005 以内，public 在 L41–L55 为负）', '5 个假标题；control 组（同档）', C['paper'],
           '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv 第 12、20 行'),
 46: L.how(F['x6'], 'Stage 11 样本 1,186 篇，标题之后全部位置，全部作者全部名字 token，最终输出；L24、L40、L48、L52', '5 个假标题各替换一次，再平均', C['team'], '381_stage13/summary_x6/x6_recovery.csv'),
 49: L.how(f"{F['rec']}；{F['loss']}", 'Stage 11 样本 target 593 / control 593 篇，标题之后全部位置（E1t：只换标题最后一个 token），最终输出', 'false_0', C['paper'],
           '361_stage11/summary/E1_recovery.csv；E1t_recovery.csv；E2_knockout.csv'),
 65: L.how('H1：question share = mean(同篇换问法相对距离) / mean(换论文相对距离)（方法手册原文）；H3：' + L.NOTE['np'], 'H1：M3 缓存 9,108 篇，“:” 位置；H3：名字位置 probe 逐个排除版 Vpd 4,654 篇，姓首 token；X2：测试集 582 对', '换论文（H1）；lens 与置换对照（H3）', C['team'],
           '381_stage13/reports/x1_similarity.md；381_stage13/reports/b2_np_report_v2.md；381_stage13/reports/b1_xall_report.md'),
 78: L.how('未写出作者的 spec（Stage 10 最终输出 L63，真标题 − 5 个假标题平均，对名字 token 平均），按多选答对次数 / 真选项概率分组取普通均值；E1 分母 = mean_p[ T̄_p − F̄_p ]', 'R0 每组 927–4,105 篇，R1 每组 15–462 篇（n < 30 只作描述）；重跑：答对 0 次 241 篇、4 次 557 篇', '5 个假标题（信号）；false_0（E1 分母）', C['team'],
           '391_groups/stage10_curves.csv；391_groups/reports/rerun_report.md “Continuous recognition”'),
}
for k in ('67', '68', '72', 'np', 'c24', '82'): FIVE[int(k) if k.isdigit() else k] = [tuple(x) for x in H['five'][k]]
ONE = {59: 'spec = true − mean(false_0..4)；recovery(l) = mean_p[ P̄_p(l) − F̄_p ] / mean_p[ T̄_p − F̄_p ]；T − C 档内合并 · 9,108 篇（lens）/ 1,186 篇（E1、P1、P2，P1/P2 为 5 个假标题平均）· 出处：X3_means.csv、E1_recovery.csv、p12f_mean5.csv',
       6: 'target = A + C，control = B + D（recall_level × 多选结果计数）· 9,108 篇；593 + 593；1,178 对 · 出处：cohort/papers.parquet',
       20: 'nlr = log10(1/rank) = −log10(rank)；spec = true − mean(false_0..4) · 1 篇示例，L63，16 个 token · 出处：paper_title_contrasts.parquet',
       21: F['tc'] + ' · 10 个引用档，7,247 个团队 · 出处：stratified_diff()、cluster_ci.md',
       23: 'prior = m_delete；topic = m_falsē − m_delete；spec = m_true − m_falsē；各项做档内 T − C · 9,108 篇；4,621 / 2,220 篇，L63 · 论文 bootstrap · 出处：A_prior_decomposition.csv',
       35: 'nlr = log10(1/rank) = −log10(rank)；rank = 1 + #(logit > gold logit) · 1 篇示例，“Co”，logit lens · 出处：raw/logit/L*/shard_011.npz 第 25029 行',
       44: 'spec = true − mean(false_0..4) 的档内 target − control · 3,734 + 2,182 篇，名字位置 · 论文 bootstrap · 出处：B_spec_target_vs_control_within_bin.csv',
       45: 'spec = true − mean(false_0..4) 的档内 target − control · 3,734 + 2,182 篇，L40–L62（L41–L47、L49 由 3-1 补，结论不变）· 论文 bootstrap · 出处：B_spec_target_vs_control_within_bin.csv',
       46: 'R(l) = mean_papers(nlr_patched@l − nlr_false) / mean_papers(nlr_true − nlr_false)，5 个假标题平均 · 1,186 篇 · 团队整群 · 出处：x6_recovery.csv',
       49: 'recovery(l) = mean_p[ P̄_p(l) − F̄_p ] / mean_p[ T̄_p − F̄_p ]；loss(l) = mean_p[ K̄_p(64) − K̄_p(l) ] / mean_p[ T̄_p − F̄_p ] · 593 + 593 篇，false_0 · 论文 bootstrap · 出处：E1_recovery.csv、E2_knockout.csv',
       65: 'H3 名字位置 probe spec = probe(true) − probe(false)（Vpd 4,654 篇，团队整群）；H1 question share · 出处：b2_np_report_v2.md、x1_similarity.md',
       78: '未写出作者的 spec（L63，真 − 5 个假标题平均）按识别程度分组的普通均值 · R0 927–4,105 / R1 15–462 篇 · 团队整群 · 出处：stage10_curves.csv、rerun_report.md'}
for k in ('67', '68', '72', 'np', 'c24', '82'): ONE[int(k) if k.isdigit() else k] = H['one'][k]

# ---- talk scripts (about one minute each)
SCRIPT = {
 59: '这一页用“书架和钥匙”总结前面四条线。第一，书在架上吗？在：真标题比假标题强，L62 约 0.44；标题位置的 probe 从 L24 起就能读出这篇论文的作者信息。第二，钥匙就是标题：整段替换在 L48 恢复 0.82、L52 起约 1.0；只换名字位置从 0.613 升到 0.841（5 个假标题平均；只用 false_0 时 0.61 → 0.85），只换“:”最多 0.181（false_0 版 0.17）；L52 之后再阻断标题几乎没有损失。第三，书在架上但拿不出来？不支持：中间层 target − control 约为 0，只在 L57–61 上升，到输出 +0.21。第四，哪层架子？两步：L48 注意力把标题读进来（0.237，false_0 版 0.231），L52–56 由 MLP 接手（0.181、0.226）。最后提醒：读不出来不等于没有。',
 6: '这一页说明分组和样本。9,108 篇论文先按开放回忆分成 R0、R1、R2，再按多选题能否认出真名单分成 strong、uncertain、fail，得到 A 4,110、U0 2,002、B 2,186、C 511、D 34 等格。target = A + C = 4,621 篇，control = B + D = 2,220 篇。Stage 10、M2、M3 用全部论文；Stage 11 到 13 的干预实验用每个引用档等量抽样的 593 + 593 篇；X1、X3 用 1,178 对配对论文。后面所有 target − control 都只在同一引用档内比较，因为两组的引用数分布差别很大。',
 20: '这一页是打分方法。以 Coifman 2007 为例：在 7 个提示下——真标题、5 个假标题、删掉标题——读最终输出，对每个名字 token 求它的名次 rank，再取 log10(1/rank)，第 1 名是 0，第 10 名是 −1。对 16 个名字 token 取平均：真标题 −0.7190，5 个假标题平均 −1.1126。标题特异信号 spec 就是两者之差，+0.3935。另外 total = 真 − 删标题 = +0.1618，topic = 假 − 删标题 = −0.2318。用名次的对数，是为了能反映从第 50,000 名到第 500 名这样的倍数变化。',
 21: '统计约定。target 和 control 的引用数分布差别很大，所以只在同一个引用档内比较：两组都至少 30 篇的档才用，一共 10 档，各档的差按 n_t·n_c/(n_t+n_c) 加权平均。区间分两种：Stage 10 到 12 已发表的表是论文级 bootstrap，在“档 × 组”内重抽论文 2,000 次；从 Stage 13 起以作者团队整群 bootstrap 为主——共享作者全名的论文算同一个团队，9,108 篇共 7,247 个团队，按团队重抽 2,000 次。Stage 10 到 12 的团队级补算正在进行。',
 23: '名字先验有多大？不给标题时，真作者的名字平均约排第 12 名。把输出分解成先验（删标题）、主题（假标题 − 删标题）和论文特有（真 − 假）三部分，再看 target − control：先验部分只有 +0.087，论文特有部分 +0.207；在姓的第一个 token 上，先验约为 0（+0.022），论文特有 +0.423。先验与识别程度的相关只有 0.085。所以 target 的优势主要来自这篇论文本身，而不是 target 的名字更常见。',
 35: '逐层读出。以 Coifman 2007 第一位作者名字里的“Co”为例：在名字位置取每一层的残差，用 logit lens 投到词表，看真 token 排第几：L24 第 37,675 名，L40 第 3,979，L48 第 44,676，L56 第 120,750，L60 第 23,169，L61 第 9,811，L62 第 120，最终输出第 61。转成 nlr = log10(1/rank) 后，右图是 7 个 token 的平均：中间层很低，最后几层才跳上来；真标题和 false_0 的差也只在最后出现。',
 44: 'target 什么时候领先？在名字位置用 lens 逐层读，左图是真标题条件，右图是标题特异信号，都是同一引用档内的 target − control。中间层没有领先：logit lens 接近 0，public J-lens 在 L48 前后甚至略为负。只有到 L62 和最终输出才拉开，+0.21 到 +0.23，而且几乎全部是标题特异的。只用 R0 论文（模型没写出作者的）时，输出 +0.199，与合并口径的 +0.207 一样。',
 45: '把最后十几层放大看。logit lens 的 target − control 在 L50 只有 +0.007，到 L62 是 +0.23，上升最快在 L57 到 L61；public J-lens 在 L48 到 L54 为负。图上没有 L41–L47 和 L49，这些层后来由 3-1 补上：logit 在 L41–L49 都在 ±0.005 以内，public 在 L41–L55 为负，结论不变。',
 46: '替换实验。在第 l 层，把真标题运行里标题之后各位置的状态复制到假标题运行里，再看最终输出时真作者名字的分数恢复了多少：R = (替换后 − 假) ÷ (真 − 假)。5 个假标题各做一次再平均：L24 0.080，L40 0.302，L48 0.821，L52 0.995。也就是说，到 L52，标题的信息已经全部搬到标题之后的位置上了。',
 49: '因果上标题什么时候被读入？E1 替换：L24 恢复 0.07–0.09，L40 0.27–0.34，L48 0.80–0.87，L52 1.00（target 和 control 各 593 篇，false_0）。E1t 只替换标题最后一个 token，只有 0.12–0.15，说明信息不在单个 token 上。E2 阻断：从 L0 起挡住标题损失 0.83，从 L52 起约为 0。所以标题在 L24 到 L50 被读入，L52 之后就不再需要了。',
 65: '这张表把三个假设和三种读法对齐。H1 任务 / 格式：在“:”和名字位置成立，换问法时状态的移动是换论文的 3–5 倍（L48 2.2 倍）。H2 论文身份：部分支持但未确立——M3 不支持，X3 有超出用词的语义但与论文身份分不开，X2 不支持。H3 隐藏的作者知识：2026-11-09 起改为部分支持——名字位置 probe 按补充 11 判据，姓首 token L40 +0.069、L48 +0.103，target − control L40 +0.031；但 lens 的区间也不含 0，而且尺度不同，所以只能说部分支持。',
 78: '识别程度改变信号的大小，不改变时间。按多选题答对次数（0 到 4）分组，未写出作者在输出层的标题特异信号从 0.17 升到 0.46（R0），R1 到 0.55；右图按真选项概率分箱，趋势一样。重跑的 E1 显示：从答对 0 次到 4 次，分母从 0.185 升到 0.407，但 L48 的恢复比例基本不变（0.90 → 0.81）。认得越清楚，信号越大，但标题被读入的层是一样的。',
 67: 'Stage 12：论文信息走到哪里。左图 P1 一次替换一组位置，主线是 5 个假标题平均，细虚线是只用 false_0：整段标题之后 L48 0.821、L52 0.995；只换名字位置 L52 0.841（false_0 版 0.847）；只换“:”最多 0.181（0.172）。右图 P2 只换一层的一个组件：L48 注意力 0.237（0.231），L52–L56 MLP 0.181、0.226（0.178、0.224）——先是注意力把标题读进来，再由 MLP 处理。下面三条：N1 不给标题时真名单“最像真的”比例 0.255，与随机 0.25 一样；N2 纯名字先验约占差距的 19%；F2 用作者提示拟合的 lens 在中间层仍读不出论文特有的信息。',
 68: 'X6 把 Stage 11 的替换换成 5 个假标题各做一遍：平均恢复 L48 0.821 [0.806, 0.835]、L52 0.995，每个假标题与 false_0 相差不超过 0.02，所以“L48 约 80%、L52 起全部”不是 false_0 特有的。右图 X7：阻断减去同样阻断在假标题运行上的损失，S = T − F；从 L0 起约 1.0，到 L52 只剩 +0.028（全部论文），target +0.022、control +0.042，都低于预注册判据 0.05（红虚线）。原来只用 false_0 时 control 0.051 差一点不过，是单个假标题的波动。',
 72: '补充 9 把标题位置的 probe 扩展到全部作者的全部名字 token，并按角色分开。左图 L40：名的第一个 token +0.124，姓的第一个 token +0.071，首字母 +0.044；姓比首字母高 +0.028，两项预注册判据都通过。灰色和土黄色是置换对照（gold 换成别的论文的作者）：在姓和名上约为 0，在首字母上约 +0.02，说明首字母的信号约一半不针对具体论文。右图是 target − control 的三个版本：预注册版里名为正、姓不显著（+0.012）；事后逐个排除版里姓为正（+0.030）；浅色的 5 个假标题平均版含泄漏，只作敏感性。结论：名的信号稳定，姓的证据弱。',
 'np': '这一页是新的名字位置 probe，直接检验 H3。在预测名字 token 的位置取第 l 层残差，用 ridge 拟合到模型自己在 L63 的状态，再在 9,137 个名字 token 里求真作者的名次；spec = 真标题 − 假标题。姓的第一个 token：probe L40 +0.069、L48 +0.103；右图 target − control L40 +0.031、L48 +0.053，区间都在 0 以上。按补充 11 预注册判据通过（姓首 token L40/L48）；事后检验：lens 区间同样不含 0（logit L40 +0.010，J-lens +0.048），尺度不同无法比较大小，因此降为部分支持。另外，首字母的对照行 +0.020 约为信号 +0.045 的一半。',
 'c24': '这一页是 C24：让模型自己写作者名单，生成时保存残差，把每个写出的名字标为真作者或编造，再在每篇论文内算 AUROC。名字写出之后，名字 token 上的 probe 在 L16 到 L56 七层都同时高于排位基线（0.632）和名字特征基线（0.549），例如 L48 0.782 [0.754, 0.812]；加上名气、三者合并基线（0.679）后仍更高；打乱标签约 0.5。写名字之前的位置读不出，不高于排位基线。这是初步结果：输出置信度基线还在跑；而且是在 chat 模板下现场生成，标签来自规则匹配，和 H3 的关系没有预注册。',
 82: '最后是不能重做的局限。只有一个模型，分组也来自它自己的标签；teacher forcing 测的是偏好不是生成——例外是 C24，它用的是模型自生成的文本，不是 teacher forcing；标签代码拿不到；4097 以上的引用档没有 B、D 论文；层不完整，干预只用了 1,186 篇；parity 容差事后从 0.25 放宽到 0.5；2-11 首名复现率 0.880 低于 0.90 而停止。下面的图是各组 E1 的分母（真 − 假差距）：C 0.559、A 0.407，B 只有约一半，所以比较恢复比例时要先看分母。',
}

# ---- build sections
import importlib
fr = lambda name: (FR / f'{name}.html').read_text(encoding='utf-8')
put(67, fr('slide67'), 'chart slide: P1 / P2 by layer, five-title mean + CI, false_0 thin (p12f_mean5.csv)')
put(68, fr('slide68'), 'chart slide: X6 five false titles + mean; X7 S(l) target/control/all with S = 0.05 line')
put(72, fr('slide72'), 'chart slide: L40 bars by role + permutation controls; T − C forest V0 / Vpd / V5x0 (leaky light)')
s65 = fr('slide65'); assert 'report v41, 2026-11-12' in s65; put(65, s65, 'header date → report v41, 2026-11-12 (patch over image + figcaption)')
# 59: P1/P2 numbers
sub1(59, 'name positions alone 0.61 → 0.85; ‘:’ alone ≤ 0.17<span class="src">​(E1, P1; 1,186 papers)</span>',
     'name positions alone 0.613 → 0.841 (false_0 0.61 → 0.85); ‘:’ ≤ 0.181 (0.17)<span class="src">​(E1, P1 5-title mean; 1,186 papers)</span>', 'P1 five-title mean main, false_0 in parentheses')
sub1(59, 'Attention brings the title in at L48 (0.23); MLP takes over at L52–56 (0.18, 0.22)<span class="src">​(P2, 1,186 papers)</span>',
     'Attention brings the title in at L48 (0.237; false_0 0.231); MLP takes over at L52–56 (0.181, 0.226; false_0 0.178, 0.224)<span class="src">​(P2 5-title mean, p12f_mean5.csv)</span>', 'P2 five-title mean main, false_0 in parentheses')
s = sec(59).replace('<div style="display:flex;gap:12px;margin-bottom:16px">', '<div style="display:flex;gap:12px;margin-bottom:9px">'); i = s.rindex('<span class="pg">'); put(59, s[:i] + HOWR(70, 640, 520, ONE[59]) + s[i:], 'one-line 怎么算')
# 21: CI statement
t1, _ = L.para(860, 600, 'CIs: Stage 10–12 published tables = paper-level bootstrap (papers resampled within bin × group); from Stage 13 on the team-cluster bootstrap (resample author teams) is the main method · 团队级补算进行中', 15, 380, L.INK, font=L.HAND, lh=18)
s = sec(21); i = s.rindex('</svg>'); put(21, s[:i] + f'<g data-name="CI method">{t1}</g>' + s[i:], 'CI method statement (paper-level Stage 10–12, team-cluster from Stage 13) + 团队级补算进行中')
svg_one(21, 70, 682, 690, ONE[21])
svg_one(6, 70, 652, 480, ONE[6]); svg_one(20, 880, 585, 350, ONE[20]); svg_one(35, 412, 244, 400, ONE[35]); svg_one(46, 70, 693, 950, ONE[46])
for n in (23, 44, 45, 49):
    s = sec(n); i = s.rindex('</section>'); put(n, s[:i] + HOWR(70, 664, 1140, ONE[n]) + s[i:], 'one-line 怎么算 (overlay below the image content)')
s = sec(65); i = s.rindex('<span class="pg">') if '<span class="pg">' in s else s.rindex('</section>'); put(65, s[:i] + HOWR(70, 201, 1140, ONE[65]) + s[i:], 'one-line 怎么算')
s = sec(78); i = s.rindex('<span class="pg">'); put(78, s[:i] + HOWR(70, 655, 1140, ONE[78]) + s[i:], 'one-line 怎么算')
# 82
sub1(82, '— a preference, not generation</li>', '— a preference, not generation (C24 使用模型自生成文本，非 teacher forcing)</li>', 'teacher-forcing limit: C24 exception')
svg82 = (FR / 'slide82_chart.svg').read_text(encoding='utf-8'); svg82s = svg82.replace('width="1140" height="190"', 'width="912" height="152"')
s = sec(82); i = s.rindex('<span class="pg">'); put(82, s[:i] + f'<div style="position:absolute;left:130px;top:560px;width:912px">{svg82s}</div>' + s[i:], 'chart: E1 denominators by group (cd_group_values.csv) + one-line 怎么算')
# insert new slides after 72
secs[72:72] = [fr('slide_np'), fr('slide_c24')]; man.append(('deck slides 73, 74 (new)', 'name-position probe (addendum 11 A, H3 partly supported); C24 2-11b (初步：输出置信度基线进行中)'))
assert len(secs) == 84
# head: CSS + Noto Sans SC subset (CJK chars only, so existing .src Latin rendering is unchanged)
body = ''.join(secs)
chars = ''.join(sorted(set(re.findall(r'[⺀-鿿　-〿＀-￯]', body))))
link = f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&text={urllib.parse.quote(chars)}&display=swap">'
css = '<style>.howr{position:absolute;font-family:"Noto Sans SC","PingFang SC","Droid Sans Fallback",system-ui,sans-serif;font-size:10.5px;line-height:1.3;color:#4B5363;z-index:2}.howr b{color:#B0566F}</style>'
head2 = head.replace('</head>', link + css + '</head>', 1)
D.write_text(head2 + body + tail, encoding='utf-8')

# ---- notes: renumber (insert 73, 74) and set priority notes
def note_text(k):
    return '【讲稿】' + SCRIPT[k] + ' ' + L.howtext(FIVE[k])
old = {int(k): v for k, v in notes.items()}
new = {}
for i in range(1, 85):
    if i <= 72: new[i] = dict(old[i])
    elif i == 73: new[i] = {'new': True, 'text': note_text('np')}
    elif i == 74: new[i] = {'new': True, 'text': note_text('c24')}
    else: new[i] = dict(old[i - 2])
for k in (59, 6, 20, 23, 21, 35, 44, 45, 46, 49, 67, 68, 72, 65, 78):
    kn = k + 2 if k > 72 else k
    new[kn]['text'] = note_text(k); new[kn]['new'] = True; man.append((f'notes_zh.json #{kn}' + (f' (old {k})' if kn != k else ''), '1-minute talk script + five-line 怎么算 (old note kept in notes_zh.json.before_20261112r)'))
new[84]['text'] = note_text(82); new[84]['new'] = True; man.append(('notes_zh.json #84 (old 82)', '1-minute talk script + five-line 怎么算'))
man.append(('notes_zh.json #73, #74 (new)', 'talk script + five-line 怎么算'))
N.write_text(json.dumps({str(k): v for k, v in new.items()}, ensure_ascii=False, indent=1), encoding='utf-8')
# slides.json
sl = [dict(x) for x in slides]
ins = [{'kind': 'html', 'text': 'Name-position probe: H3 partly supported (addendum 11 A)', 'figs': [], 'added': '2026-11-12', 'new18': 'np'},
       {'kind': 'html', 'text': 'Names the model writes itself: true vs fabricated (C24, 2-11b; 初步：输出置信度基线进行中)', 'figs': [], 'added': '2026-11-12', 'new18': 'c24'}]
sl[72:72] = ins
for i, x in enumerate(sl, 1): x['i'] = i
for k in (67, 68, 72): sl[k - 1]['updated'] = '2026-11-12r'
S.write_text(json.dumps(sl, ensure_ascii=False, indent=1), encoding='utf-8')
json.dump({'one': {str(k): v for k, v in ONE.items()}, 'five': {str(k): v for k, v in FIVE.items()}}, open(FR / 'how_all.json', 'w'), ensure_ascii=False, indent=1)
# manifest
MF = R / 'sync_20261108c_manifest.md'; mt = MF.read_text(encoding='utf-8'); k = mt.find('\n## round r (deck charts, priority build')
if k >= 0: MF.write_text(mt[:k], encoding='utf-8')  # re-run: replace own section
with open(MF, 'a', encoding='utf-8') as fh:
    fh.write('\n## round r (deck charts, priority build for the talk)\n\nScript `sync_20261107/apply_20261112r.py` (+ `apply_20261112r_lib.py`, `apply_20261112r_charts.py`, `apply_20261112r_frag_b.py` for slide 65); backups `*.before_20261112r`. Priority slides only (coordinator 2026-11-12 19:05); slide numbers before insertion except where marked. Non-priority redraws (25, 28, 36, 39, 73, 74, 17, 34, 66), report 729/730, handbook definitions and the image-number CSV postponed (nothing written to those files).\n\n| # | file | change |\n|---|---|---|\n')
    for j, (a, b) in enumerate(man, 1): fh.write(f'| r{j} | {a} | {b} |\n')
print('deck slides', len(secs), '; manifest rows', len(man), '; cjk chars', len(chars))
