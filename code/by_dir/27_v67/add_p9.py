import re,sys,html,json
sys.path.insert(0,'/home/zhang.zhiqi2/jlens_work/27_v67')
from coverage_lines_v66 import C66
D='/home/zhang.zhiqi2/jlens_work/27_v67/deck_v67.html'; t=open(D).read()
ms=list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>',t,flags=re.S))
s=C66[9]  # v66 p9 = v67 p9 ("How groups and contrasts are built")
assert 'How groups' in open('/home/zhang.zhiqi2/jlens_work/27_v67/toc_v67.md').read()
add=(f'<div class="soln covso" style="left:70px;top:6px;width:1000px;font-size:12.5px;box-sizing:border-box;z-index:7"><b>So (this slide):</b> {html.escape(s["so"])} <span class="tg {s["tag"][0]}">{html.escape(s["tag"][1])}</span></div>')
m=ms[8]; x=m.group(0); assert 'covso' not in x; x=x[:-10]+add+'</section>'; t=t[:m.start()]+x+t[m.end():]; open(D,'w').write(t)
b=json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/coverage_boxes.json')); b['9'].append(['so',{'x':70,'y':6,'w':1000,'h':28,'fs':12.5}]); json.dump(b,open('/home/zhang.zhiqi2/jlens_work/27_v67/coverage_boxes.json','w'),indent=0)
print('p9 so added')
