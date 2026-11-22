# New H2 wording v2 (user change 2026-11-22, after addendum 22 Part A and addendum 24 results). Status stays 'partly supported'.
OLD_ZH = 'H2 部分支持——存在真实论文成分，但大部分信号可由语义相似解释'
OLD_EN = 'H2 partly supported — a real-paper component exists, but meaning similarity explains most of the signal'
NEW_EN = ('H2 partly supported: a real-title extra over a same-meaning fabricated title exists (R̄_T +0.106), mostly carried by meaning (75%). '
          "The extra sits mainly on the title's rare and specific words (names, acronyms, technical terms): replacing only those words loses R̄ = 0.162, "
          'vs 0.027 for common words (addendum 24). It is not larger for recognised papers (K4 not supported) and is smaller for more-cited papers (K4c reversed). '
          'Whether the extra reflects specific wording or a penalty on fabricated titles remains open.')
NEW_ZH = ('H2 部分支持：真标题比意思相同的编造标题多出一部分（R̄_T +0.106），大部分由意思承担（75%）。'
          '多出的部分主要落在标题里罕见、具体的词上（人名、缩写、专门术语）：只替换这些词损失 R̄ = 0.162，只替换常见词损失 0.027（补充 24）。'
          '它在认得出的论文上并不更大（K4 不支持），在引用多的论文上反而更小（K4c 反向）。'
          '这多出的部分反映的是具体措辞，还是模型对编造标题的惩罚，仍未确定。')
CAV_ZH = ('（补充 24 的两点说明：两种替换的词数不同，罕见词平均换 3.4 个、常见词 2.1 个；常见词是按词频匹配替换，不是同义词，意思也会改变。）')
CAV_EN = ('(Addendum 24 caveats: the replacement counts differ — rare words 3.4 vs common words 2.1 on average — and common words were replaced by frequency-matched words, not synonyms, so their meaning changes.)')
SRC = ('补充 20（φ_T 0.751 [0.723, 0.778]，R̄_T +0.106 [0.094, 0.118]，566 篇 target）；补充 24（2026-11-22 锁定，sha256 270f2157…；target 418 篇：R̄_a 0.162 [0.142, 0.183]，R̄_b 0.027 [0.019, 0.036]，差 +0.134 [0.115, 0.154]；control 差 +0.057 [0.042, 0.072]；391_groups/summary_a24/a24_results.csv）；'
       '补充 22 Part A（2026-11-21 锁定，sha256 d648ef11…；1,083 篇；K4 L24 +0.018 [0.001, 0.034] 仅未校正，Holm p 0.195；K4c L24 −0.027 [Holm −0.049, −0.009] … L48 −0.115 [Holm −0.166, −0.072]；391_groups/summary_a22_partA/contrasts.csv）')
ALT_ZH = ('<b>H2 结论的范围（2026-11-22，补充 22 Part A 与补充 24 之后）：</b>英文原句：“' + NEW_EN + '” ' + CAV_EN + ' '
          '补充 20 显示的是“真标题 vs 编造标题”的差异；之后两项锁定检验缩小了它的含义：'
          '①<b>补充 22 Part A（不变性阶梯）</b>：K1（同义改写 − 打乱词序）支持，中间层编码了意思（L48 +0.082 [Holm 0.064, 0.101]）；K3（同义改写 − 高词汇重叠的另一篇）支持（L48 +0.458）；'
          'K4（[真 − 编造]，target − control，同引用档内）不支持（只有 L24 未校正 +0.018 [0.001, 0.034]，Holm p 0.195）；K4c（同领域内引用数高 − 低）反向：L24 −0.027 到 L48 −0.115，Holm 区间都小于 0——引用多的论文多出的部分反而更小。'
          '②<b>补充 24（只换真标题里的罕见词 vs 只换常见词）</b>：target 只换罕见词损失 R̄ 0.162 [0.142, 0.183]，只换常见词 0.027 [0.019, 0.036]，差 +0.134 [0.115, 0.154]；control 差 +0.057。' + CAV_ZH +
          '另外：身份方向与作者 probe 方向几乎正交（|cos| ≤ 0.06，探索性）；补充 22 Part B 标题位置身份独有解释量全体约为 0（D2 边界）、target 略大（D3）。'
          '<b>读法：</b>多出的部分不是“认得出才有”的论文身份，而主要来自标题里的具体词；它是具体措辞的作用，还是模型对编造标题（缺少这些具体词）的惩罚，仍未确定。')
