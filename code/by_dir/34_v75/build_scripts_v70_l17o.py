"""2026-11-25 coordinator: main script v69 -> v70 (P125 spoken pair + 备查 note: the 50.4% vs 50.5% comparison removed everywhere, user-approved);
leader script v17n -> v17o (same change, 3 places + current-version line). Headings unchanged (page numbers identical). 【】 verified."""
import re
W = '/home/zhang.zhiqi2/jlens_work/'
def notes(s): return re.findall(r'【[^】]*】', s)
sc = open(W + 'script_stage1_13_v69.md').read(); n0 = notes(sc)
rep = [("On the chart, each bar is compared with chance from shuffled names; about half are not in the data, exactly as by chance, 50.4% against 50.5%.",
        "On the chart, each bar is compared with chance from shuffled names; about half, 50.4%, are not in the data at all, in none of the cohort's author lists."),
       ("图上每根柱子都和打乱名字得到的机会水平比；大约一半不在数据里，和机会水平一模一样，50.4% 对 50.5%。",
        "图上每根柱子都和打乱名字得到的机会水平比；大约一半，50.4%，根本不在数据里，不在队列任何一篇论文的作者名单上。"),
       ("没有信息量。图上柱子标签和 Result ① 暂保留。",
        "没有信息量。同一对比也已从柱子标签、该柱的随机标记、Result ①、主 PPT S133 和 leader 第 66 页去掉（用户批准）；本页“上一版讲稿全文”里的旧说法作为历史记录保留。")]
for a, b in rep:
    assert sc.count(a) == 1, a[:40]; sc = sc.replace(a, b)
assert notes(sc) == n0; open(W + 'script_stage1_13_v70.md', 'w').write(sc)
ld = open(W + 'script_leader_v17n.md').read(); m0 = notes(ld)
assert ld.count('和打乱基线一样（50.4% vs 50.5%）') == 3
ld = ld.replace('大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）', '大约一半（50.4%）不在数据里')
assert '50.5' not in ld
a = '当前：jlens_leader_v17n.pptx，68 页（2026-11-24）。'; assert ld.count(a) == 1
ld = ld.replace(a, '当前：jlens_leader_v17o.pptx，68 页（2026-11-25；v17o = v17n 第 66 页去掉 “50.4% vs 50.5%” 对比，其余不变）。')
assert notes(ld) == m0; open(W + 'script_leader_v17o.md', 'w').write(ld)
print('ok', len(n0), len(m0))
