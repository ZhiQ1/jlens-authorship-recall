"""Downloads page (5Tdt1mQa8xnPiqQEKvjzta) 2026-11-25 v73 round: main pptx v22x added (新); to stay under the 256 MiB version cap the two
oldest pptx on the page are taken off: v22v and v22w (cluster copies kept in reports/downloads/); script v67 added (v66 -> 上一版,
v65 -> 更早一版). Builds from the live page file (= 32_v72/dl_v22w/index.html, version 1795603080-e21b, sha 787dd4a3…)."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/32_v72/dl_v22w/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/33_v73/dl_v22x/'
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/jlens_1113_pre_v22x.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 14_000_000)); step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22x.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
r22v, r22w = row('jlens_1113_pre_v22v.pptx'), row('jlens_1113_pre_v22w.pptx')
new = ('\n    <li><div class="name">jlens_1113_pre_v22x.pptx</div><div class="meta"><b>新</b> · 主 PPT v22x（192 页，2026-11-25）：按 HTML deck v73 的顺序：故事图一节增加 4 页（S142 现象：认得但说不出、曝光差距和名字先验；S167–S168 每句故事由哪些实验搭起来；S169 全部 100 个实验的贡献总览），每页有标题、Now asking、整页图和 So 行加证据标签；'
       '5 页故事图换成更新的图（S151、S153、S154、S163、S166：新增注意框、数字和稳健性框）；故事图一节现为 S141–S169，原总结页起顺延 4 页，什么都没删；'
       '我们自己文字里的页码全部改成 v22x 页码；你的形状、中文框和 16 条小标注原样保留；发布前检查 C1–C4 和保留检查全部通过。为不超过本页 256 MiB 的上限，v22w 和 v22v 已从本页移下（集群上保留） · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22x" data-f="jlens_1113_pre_v22x.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22x" role="status"></div></li>')
h = h.replace(r22w, new, 1).replace(r22v, '', 1)
r66, r65, r64 = row('script_stage1_13_v66.md'), row('script_stage1_13_v65.md'), row('script_stage1_13_v64.md')
s67 = os.path.getsize('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/script_stage1_13_v67.md') / 1e6
new67 = ('\n    <li><div class="name">script_stage1_13_v67.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿，按 HTML deck v73 的顺序（184 页；主 PPT v22x 页码），Markdown 可编辑：'
         '新增 4 页讲稿（第 134 页现象；第 159–160 页按故事句子逐句讲由哪些主线实验搭起来；第 161 页全部 100 个实验总览：一句英文一句中文的“要说的话”加备查）；'
         '5 页换了新图的讲稿各加一句口播（一句英文一句中文）和一行备查，说明图上新增的元素；第 133、158 页的过渡句改为指向新的下一页；原第 134 页起按新顺序编号，标题写 HTML v73 页码和主 PPT v22x 页码；'
         f'你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · <span class="size">{s67:.2f} MB</span></div><button type="button" id="bscr67" data-f="script_stage1_13_v67.md">保存</button><div class="status" id="sscr67" role="status"></div></li>')
h = h.replace(r66, new67 + r66.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r65, r65.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
a = 'Stage 1–13 v66〔2026-11-25，按 HTML v72 顺序〕）、主 PPT v22w（按 HTML v72）'; assert a in h
h = h.replace(a, 'Stage 1–13 v67〔2026-11-25，按 HTML v73 顺序〕）、主 PPT v22x（按 HTML v73）', 1)
a = '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22u、'; assert a in h
h = h.replace(a, '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22w、v22v、v22u、', 1)
open(OUTD + 'index.html', 'w').write(h)
print('parts', parts, round(mb, 1), 'v22v gone', 'pre_v22v.pptx</div>' not in h, 'v22w gone', 'pre_v22w.pptx</div>' not in h, 'v67', 'script_stage1_13_v67.md</div>' in h)
