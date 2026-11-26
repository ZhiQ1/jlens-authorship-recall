"""2026-11-25 coordinator: slide 158 (HTML v73) So line = known gap ①, same as the image. HTML v73 -> v74, script v67 -> v68 (wording only)."""
import re
W='/home/zhang.zhiqi2/jlens_work/'
OLD_SO='each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt.'
NEW_SO='Gap ①: where “who wrote this paper” enters — do the late MLPs hold this paper’s author knowledge? Not tested yet.'
t=open(W+'33_v73/deck_v73.html').read()
S=list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>',t,re.S))
m=S[157]; s=m.group(0); assert 'story_flow_16x9_d' in s and s.count(OLD_SO)==1
t=t[:m.start()]+s.replace(OLD_SO,NEW_SO)+t[m.end():]
open(W+'33_v73/deck_v74.html','w').write(t)
sc=open(W+'script_stage1_13_v67.md').read()
i=sc.index('## P158 · HTML v73'); j=sc.index('\n## ',i+5); pg=sc[i:j]
a_en='Each step hands one question to the next, and two links are still broken: where the knowledge of who wrote this paper enters, and recognition measured inside the multiple-choice prompt.'
a_zh='每一步把一个问题交给下一步；还有两处没接上：“谁写的这篇论文”从哪里进来，以及在选择题 prompt 内部测量“认得”。'
n_en='Gap one: where the knowledge of who wrote this paper enters — do the late MLPs hold this paper’s author knowledge? That is not tested yet.'
n_zh='缺口一：“谁写的这篇论文”从哪里进来——后面的 MLP 里有没有这篇论文的作者知识？这一点还没有检验。'
assert pg.count(a_en+'\n'+a_zh)==1 and pg.count(OLD_SO)==1
pg2=pg.replace(a_en+'\n'+a_zh,n_en+'\n'+n_zh).replace(OLD_SO,NEW_SO)
open(W+'script_stage1_13_v68.md','w').write(sc[:i]+pg2+sc[j:])
print('ok')
