"""Downloads page (5Tdt1mQa8xnPiqQEKvjzta) 2026-11-23: main pptx v22s -> v22t (b64 parts), v22s kept as 上一版. Builds from the LIVE page file."""
import re, base64, os, sys
W = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/v22t_work/'
SRC = W + 'dl_live/index.html'; OUTD = W + 'dl_v22t/'; os.makedirs(OUTD, exist_ok=True)
NSL = int(sys.argv[1])
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/jlens_1113_pre_v22t.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 15_500_000))
step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22t.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
old = re.search(r'\n    <li><div class="name">jlens_1113_pre_v22s\.pptx</div>.*?</li>', h, re.S).group(0)
prev = old.replace('<b>新</b>', '<b class="old">上一版</b>', 1)
new = ('\n    <li><div class="name">jlens_1113_pre_v22t.pptx</div><div class="meta"><b>新</b> · 主 PPT v22t（' + str(NSL) + ' 页，2026-11-23）：按 HTML deck v68 的新顺序重排（Part 0–8：开场、方法、认得但说不出、3a 标题何时被读、3b H1、H2、路线与 H3、说得晚卡在写出、总结 S1–S10、检查与局限，然后术语表和备用页；每个 Part 的小样本页归在“Background: how we got here”下）；'
       'v22s 的每一页都保留（只移动不删除），只在主 PPT 里有的页和续页跟在对应页后面；v67–v68 新增的 42 页（每个 Part 的问题卡、判定卡、证据矩阵、新实验页、Part 分隔页和总结 S1–S10）按 HTML 原生重建，总结页的机制图用 HTML 截图；'
       '旧页按 v68 补上缺的 Now asking、So 行和证据标签（放在空白处，不盖住你的字）；我们自己文字里的页码改成 v22t 页码、内部代号改成白话名；你形状里的代号旁加“代号 → 白话名”小注（规则 13 扩展）；你的形状和中文框原样保留（里面的旧页码另列清单）；发布前检查 C1–C4 和保留检查全部通过 · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22t" data-f="jlens_1113_pre_v22t.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22t" role="status"></div></li>')
h = h.replace(old, new + prev)
h = h.replace('主 PPT v22s 和领导版 v17m（汇报冻结版）', '主 PPT v22t（按 HTML v68 新顺序）和领导版 v17m', 1)
open(OUTD + 'index.html', 'w').write(h)
print('ok parts', parts, [len(open(OUTD + p).read()) for p in parts], round(mb, 1))
