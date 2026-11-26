"""2026-11-25 coordinator: main script v68 -> v69 (= HTML v75 / pptx v22z). Headings relabelled; P124 and P125: one spoken EN/ZH pair
each + a 备查 block (post-hoc checks). 【】 notes untouched (count and text verified)."""
import re
W = '/home/zhang.zhiqi2/jlens_work/'
sc = open(W + 'script_stage1_13_v68.md').read()
notes0 = re.findall(r'【[^】]*】', sc)
assert sc.count('HTML v74 p') == 184 and sc.count('(v22y)') == 184
sc = sc.replace('HTML v74 p', 'HTML v75 p').replace('(v22y)', '(v22z)')


def page(sc, tag):
    i = sc.index(tag); j = sc.index('\n## ', i + 5); return i, j


# ---- P124
i, j = page(sc, '## P124 · HTML v75 p124')
pg = sc[i:j]
a = ("So it is mostly confidence, and we keep this as exploratory. Next, where the made-up names come from.\n"
     "所以大部分是置信度，我们把这一页保留为探索性。下一页看编造的名字从哪里来。")
assert pg.count(a) == 1
add = ("One check we added afterwards: the before-the-name curve mixed two kinds of tokens, a line break before the first name and a semicolon before the others; with later names only, it stays near chance until layer 52.\n"
       "我们事后补了一个检查：名字之前那条曲线混了两种 token，第一个名字前是换行，其他名字前是分号；只看后面的名字，到第 52 层之前都接近随机。\n"
       "On pairs of later names only, the small remainder beyond confidence is still there at layers 40 to 52.\n"
       "只看后面名字配成的对，超出置信度的那一小部分在第 40 到 52 层仍然在。\n")
pg = pg.replace(a, add + a)
bc124 = """
**备查（不念）· 2026-11-25 事后检查（未预注册，探索性）：**
- **(i) 前置 token 不一致：** pred_first = 名字第一个 token 的前一位置。第 1 个名字（6,746 个）落在 prompt 最后一个 token（`</think>` 后的 "\\n\\n"）；第 2 个及以后（24,815 个）落在 ";"（24,687），其余 ".;" 112、" ;" 15、");" 1。补充 15 只写了"第一个人名 token 的前一位置"，未涵盖这一点。
- **(i) 拆开（原 probe，论文内 AUROC）：** 含第 1 个名字的对（1,200 对）0.57–0.70；只有第 2 个及以后的对（2,188 对）L16 0.545 [0.502, 0.585]、L24 0.542、L32 0.556、L40 0.510 [0.467, 0.549]、L48 0.542 [0.496, 0.584]、L52 0.598 [0.551, 0.641]、L56 0.586 [0.540, 0.626]（只有 L52–L56 高于 0.5）。只用第 1 个名字另训 probe：每篇只有一个第 1 名，没有论文内对，只能报合并 AUROC 0.66–0.78（L48 0.784 [0.755, 0.815]），与论文内 AUROC 不可比。
- **置信度基线放到同样的对上：** 只有后面名字的对，输出置信度 0.681 [0.640, 0.718]（全部对 0.711，含第 1 名的对 0.767）；(ii) − 置信度：L40 +0.070 [+0.025, +0.121]、L48 +0.069 [+0.020, +0.123]、L52 +0.066 [+0.020, +0.115]，其余层 CI 含 0；只用后面名字另训 probe 与置信度，L48 +0.083 [+0.036, +0.135]。(ii) 本身在含第 1 名的对上也偏高（L48 0.841 vs 只有后面名字 0.750）。
- **置信度扣掉"名字好不好写"：** 三个生成时置信量对名字特征（长度、cohort 全名频率（不含本篇）、知名度 4 项）的留出 R² 0.02–0.06（加位置 0.04–0.09）；残差上的置信度 0.711 → 0.695 [0.661, 0.725]（加位置 0.700），差 +0.016 [+0.003, +0.029]；名字特征单独 0.560。probe 相对残差置信度：L40 +0.084、L48 +0.087 [+0.049, +0.128]、L52 +0.076。正文结论不变。
- **拟合与评估：** probe 在 target + control 的全部 M/H 名字上合并拟合（5 折，作者团队分折），只在 target 论文上评估（论文内 M–H 对）；预注册原文只写了评估部分，"合并拟合"只写在分析脚本说明里。
- **prompt 格式：** 本实验用聊天模板自由生成（system + user 问题，enable_thinking=False），和 deck 其他实验的 "Authors:" 续写格式不同，数字不能横比。
- 出处：381_stage13/b2_gennames_b/summary_predfirst_split_20261125/split_all.csv；381_stage13/summary_later_pairs_20261125/report.md；381_stage13/summary_conf_resid_20261125/report.md；脚本 13_stage13/stage13_b2_gennames_b_{predfirst_split,later_pairs,conf_resid}_20261125.py。
"""
k = pg.index('**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：**')
k2 = pg.index('\n', k) + 1
pg = pg[:k2] + bc124 + pg[k2:]
sc = sc[:i] + pg + sc[j:]

# ---- P125
i, j = page(sc, '## P125 · HTML v75 p125')
pg = sc[i:j]
a = ("So made-up names are not near-misses. Next, a summary of the token line.\n"
     "所以编造的名字不是“差一点就对”。下一页小结 token 这条线。")
assert pg.count(a) == 1
add = ("One more small check: fewer than one in a hundred of the names that are not in the data look like a misspelling of a true author.\n"
       "再补一个小检查：不在数据里的这些名字，像是真作者名字拼错的不到百分之一。\n")
pg = pg.replace(a, add + a)
bc125 = """
**备查（不念）· 2026-11-25 事后检查（未预注册，探索性）：**
- **删除的便签：** 原页底部便签 "50.4% not in the data, vs 50.5% for the shuffled baseline" 已删（用户批准）：一个名字在不在作者库里与配哪篇论文无关，打乱前后必然相同，没有信息量。图上柱子标签和 Result ① 暂保留。
- **拼错的真名（编辑距离）：** 20,286 个"不在数据里"的编造名，对 9,108 篇作者库求最近名字（姓 + 首字母须一致 / 全名 / 只看姓）。距离 ≤ 2 且最近的就是本篇真作者：全名 0.07%（15 个）、姓 + 首字母 0.13%（27 个）、只看姓 0.63%（128 个）；打乱论文标签 200 次（全局 / 同领域）分别 0.003% / 0.045% / 0.09%，p < 1/200。高于随机，但最多占"不在数据里"的 0.6%、全部编造名的约 0.3%；结论不变。约一半像真拼错（Johengen→Johengren、Wiig→Wiik、Kato→Katoh），其余是短姓巧合（Xu/Lu）。与本篇无关的最近距离（姓 + 首字母）1 步 41%、2 步 38%、≥3 步 21%，反映的是名字空间的密度。
- **匹配规则（Stage 10 匹配器，原样）：** 小写；NFKD 后丢弃非 ASCII（é→e、ü→u）；非字母→空格；连字符拆成词，姓 = 最后一个词；只比姓 + 名的第一个首字母（中间名不比）；名在前、姓在前两轮，一对一，按真作者顺序。
- **已知漏判：** Müller / Mueller（ue 不折叠）；Jr. / III 等后缀被当成姓；ı、ø、ß、ł 等无分解形式的字母被丢掉；复姓只写一段；前缀连写（Vanderberg）；昵称或首字母错（规则有意如此）。按 2-11b rev3 规则重查：0.4%（85 个）可匹配到作者库，其中 3 个是本篇真作者（Charles A. Janeway Jr.、L Joseph Melton III、C. Y. Yildirim / C. Yıldırım），影响可忽略。2-11b 预注册在同一批回答上：35,887 项中 8 项标签改变，1 项 H→M。
- 出处：391_groups/summary_fabricated_editdist_20261125/report.md；脚本 14_groups/fabricated_editdist_20261125.py。
"""
k = pg.rindex('**备查（不念）· 2026-11-23 公式行统一：**')
k2 = pg.index('\n', k) + 1
pg = pg[:k2] + bc125 + pg[k2:]
sc = sc[:i] + pg + sc[j:]

notes1 = re.findall(r'【[^】]*】', sc)
assert notes0 == notes1, 'user notes changed'
open(W + 'script_stage1_13_v69.md', 'w').write(sc)
print('ok', len(notes1), 'notes verbatim')
