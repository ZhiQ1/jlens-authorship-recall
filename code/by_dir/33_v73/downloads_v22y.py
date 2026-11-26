"""Downloads page 2026-11-25 (coordinator: slide 158 gap ① wording): main pptx v22y added (新), v22x taken off for the 256 MiB cap
(cluster copy kept); script v68 added (v67 -> 上一版, v66 -> 更早一版). Builds from the live page file (dl_v22x/index.html, version 1795604527-9e12)."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/33_v73/dl_v22x/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/33_v73/dl_v22y/'
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/jlens_1113_pre_v22y.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 14_000_000)); step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22y.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
r22x = row('jlens_1113_pre_v22x.pptx')
new = ('\n    <li><div class="name">jlens_1113_pre_v22y.pptx</div><div class="meta"><b>新</b> · 主 PPT v22y（192 页，2026-11-25）：同 v22x，只改了 S166（故事拼图第 4 部分）的 So 行，和图上的已知缺口 ① 说法一致：'
       '“Gap ①: where ‘who wrote this paper’ enters — do the late MLPs hold this paper’s author knowledge? Not tested yet.”（措辞更正，结论不变）；v22x 的内容：故事图一节 S141–S169（新增 S142、S167–S169，5 页换新图）；'
       '你的形状、中文框和 16 条小标注原样保留；发布前检查 C1–C4 和保留检查全部通过。为不超过本页 256 MiB 的上限，v22x 已从本页移下（集群上保留） · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22y" data-f="jlens_1113_pre_v22y.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22y" role="status"></div></li>')
h = h.replace(r22x, new, 1)
r67, r66 = row('script_stage1_13_v67.md'), row('script_stage1_13_v66.md')
s68 = os.path.getsize('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/script_stage1_13_v68.md') / 1e6
new68 = ('\n    <li><div class="name">script_stage1_13_v68.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿（184 页；HTML deck v74 / 主 PPT v22y，页码与 v73 / v22x 相同，各页标题仍写 v73 / v22x），Markdown 可编辑：'
         '同 v67，只改了第 158 页：口播一句英文一句中文和备查里的本页全文改成和图一致的缺口 ① 说法（后面的 MLP 里有没有这篇论文的作者知识？还没有检验）；'
         f'你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · <span class="size">{s68:.2f} MB</span></div><button type="button" id="bscr68" data-f="script_stage1_13_v68.md">保存</button><div class="status" id="sscr68" role="status"></div></li>')
h = h.replace(r67, new68 + r67.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r66, r66.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
a = 'Stage 1–13 v67〔2026-11-25，按 HTML v73 顺序〕）、主 PPT v22x（按 HTML v73）'; assert a in h
h = h.replace(a, 'Stage 1–13 v68〔2026-11-25，按 HTML v74 顺序〕）、主 PPT v22y（按 HTML v74）', 1)
a = '包括主 PPT v22w、v22v、'; assert a in h
h = h.replace(a, '包括主 PPT v22x、v22w、v22v、', 1)
open(OUTD + 'index.html', 'w').write(h)
print(parts, round(mb, 1), 'v22x gone', 'pre_v22x.pptx</div>' not in h)
