"""Downloads page (5Tdt1mQa8xnPiqQEKvjzta) 2026-11-25: main pptx v22w added (新), v22v -> 上一版, v22u taken off the page; to stay under the
256 MiB cap the oldest pptx on the page, Stage1-13_deck_v21_editable.pptx (2026-11-08), is also taken off (cluster copies kept in reports/downloads/);
script v66 added (v65 -> 上一版, v64 -> 更早一版). Builds from the live page file (= 28_v22t/dl_v22v/index.html, version 1795583144-7e24)."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/28_v22t/dl_v22v/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/32_v72/dl_v22w/'
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/jlens_1113_pre_v22w.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 14_000_000)); step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22w.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
r22u, r22v, r21 = row('jlens_1113_pre_v22u.pptx'), row('jlens_1113_pre_v22v.pptx'), row('Stage1-13_deck_v21_editable.pptx')
h = h.replace(r22u, '', 1).replace(r21, '', 1)
new = ('\n    <li><div class="name">jlens_1113_pre_v22w.pptx</div><div class="meta"><b>新</b> · 主 PPT v22w（188 页，2026-11-25）：按 HTML deck v72 的顺序：'
       '第 7 部分（总结）开头新增 25 页故事图（S141–S165：全图一页、六段各点亮一页、六段逐段展开 13 页、故事拼图流程图 4 页），每页有标题、Now asking、整页图和 So 行加证据标签；'
       '原总结页起顺延 25 页，什么都没替换；8 页上的小字框放大到不小于 14 px 等效字号（S3、S9、S21、S56、S69、S101、S113、S178）；'
       '我们自己文字里的页码全部改成 v22w 页码；你的形状、中文框和 16 条小标注原样保留；发布前检查 C1–C4 和保留检查全部通过 · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22w" data-f="jlens_1113_pre_v22w.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22w" role="status"></div></li>')
h = h.replace(r22v, new + r22v.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
r65, r64 = row('script_stage1_13_v65.md'), row('script_stage1_13_v64.md')
s66 = os.path.getsize('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/script_stage1_13_v66.md') / 1e6
new66 = ('\n    <li><div class="name">script_stage1_13_v66.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿，按 HTML deck v72 的顺序（180 页；主 PPT v22w 页码），Markdown 可编辑：'
         '第 7 部分开头新增 25 页故事图的讲稿（第 133–157 页：一句英文一句中文的“要说的话”，点亮的那一段逐个讲、最后说底部结论；备查里是本页全文和定稿树的对应原文）；'
         '原第 133 页起顺延 25 页，标题写 HTML v72 页码和主 PPT v22w 页码；'
         f'你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · <span class="size">{s66:.2f} MB</span></div><button type="button" id="bscr66" data-f="script_stage1_13_v66.md">保存</button><div class="status" id="sscr66" role="status"></div></li>')
h = h.replace(r65, new66 + r65.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r64, r64.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
a = 'Stage 1–13 v65〔2026-11-25，按 HTML v71 顺序〕）、主 PPT v22v（按 HTML v71）'; assert a in h
h = h.replace(a, 'Stage 1–13 v66〔2026-11-25，按 HTML v72 顺序〕）、主 PPT v22w（按 HTML v72）', 1)
a = '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22t、v22s、'; assert a in h
h = h.replace(a, '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22u、v22t、v22s、PPT v21 可编辑版 pptx、', 1)
open(OUTD + 'index.html', 'w').write(h)
print('parts', parts, round(mb, 1), 'v22u gone', 'pre_v22u.pptx</div>' not in h, 'v21pptx gone', 'v21_editable.pptx</div>' not in h, 'v66', 'script_stage1_13_v66.md</div>' in h)
