"""Report v26 (2026-11-03): overall hypothesis wording unified with the deck and handbook: H2 部分支持但未确立，H3 证据不足."""
import os
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p = 'stage1_11_report.html'; s = open(p, encoding='utf-8').read()
R = [('上文 X4）</td></tr>\n</tbody></table></div>\n<p>三者不互斥。',
      '上文 X4）</td></tr>\n</tbody></table></div>\n<p><b>总体判断（2026-11-03）：H2 部分支持但未确立，H3 证据不足。</b>H2 的支持来自 M2（标题位置读得出论文属性）和 X1（替换效果与问法无关）；M3 不支持，X3 不能区分语义与论文身份，X4 的顺序与 H2 预测相反。</p>\n<p>三者不互斥。'),
     ('更新于 2026-11-02（第 25 版，答辩定稿）', '更新于 2026-11-03（第 26 版，答辩定稿）')]
for a, b in R:
    n = s.count(a); assert n == 1, (n, a[:50]); s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('applied', len(R))
