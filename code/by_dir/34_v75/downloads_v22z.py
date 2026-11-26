"""Downloads page 2026-11-25 (coordinator: slides 124/125 post-hoc caveats): main pptx v22z added (新), v22y taken off for the 256 MiB cap
(cluster copy kept); script v69 added (v68 -> 上一版, v67 -> 更早一版). Builds from the live page file (dl_v22y/index.html, version 1795604907-3270)."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/34_v75/dl_v22y/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/34_v75/dl_v22z/'
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/'
h = open(SRC).read()
pp = D + 'jlens_1113_pre_v22z.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 14_000_000)); step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22z.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
r22y = row('jlens_1113_pre_v22y.pptx')
new = ('\n    <li><div class="name">jlens_1113_pre_v22z.pptx</div><div class="meta"><b>新</b> · 主 PPT v22z（192 页，2026-11-25）：同 v22y，只改了两页。'
       'S131（自己写的名字：真 vs 编造）：右图加两条曲线——“名字前一位置”只看第 2 个及以后的名字（论文内 AUROC）和只看第 1 个名字（合并 AUROC，不可比），加事后发现、预注册未涵盖的说明（第 1 个名字前是换行、其后是“;”），'
       'Caveat 补上 probe 在 target + control 上合并拟合、只在 target 上评估，以及本实验 prompt 格式不同、数字不能横比；'
       'S132（编造的名字从哪来）：删掉底部 “50.4% vs 50.5%” 便签（你批准的；打乱前后必然相同，没有信息量），Caveat 补上“约 ≤ 0.6% 像是真作者名字拼错”。结论不变。'
       '你的形状、中文框和 16 条小标注原样保留；发布前检查 C1–C4 和保留检查全部通过。为不超过本页 256 MiB 的上限，v22y 已从本页移下（集群上保留） · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22z" data-f="jlens_1113_pre_v22z.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22z" role="status"></div></li>')
h = h.replace(r22y, new, 1)
r68, r67 = row('script_stage1_13_v68.md'), row('script_stage1_13_v67.md')
s69 = os.path.getsize(D + 'script_stage1_13_v69.md') / 1e6
new69 = ('\n    <li><div class="name">script_stage1_13_v69.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿（184 页；HTML deck v75 / 主 PPT v22z，各页标题写 v75 / v22z），Markdown 可编辑：'
         '同 v68，只改了第 124、125 页：各加一组口播（一句英文一句中文）和一个备查块（名字前一位置拆开、置信度放到同样的对上、置信度扣掉名字特征、拟合与评估方式、prompt 格式；拼错的真名、匹配规则和已知漏判）；'
         f'你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · <span class="size">{s69:.2f} MB</span></div><button type="button" id="bscr69" data-f="script_stage1_13_v69.md">保存</button><div class="status" id="sscr69" role="status"></div></li>')
assert '<b>新</b>' in r68 and '<b class="old">上一版</b>' in r67
h = h.replace(r68, new69 + r68.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r67, r67.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
a = 'Stage 1–13 v68〔2026-11-25，按 HTML v74 顺序〕）、主 PPT v22y（按 HTML v74）'; assert a in h
h = h.replace(a, 'Stage 1–13 v69〔2026-11-25，按 HTML v75 顺序〕）、主 PPT v22z（按 HTML v75）', 1)
a = '包括主 PPT v22x、v22w、v22v、'; assert a in h
h = h.replace(a, '包括主 PPT v22y、v22x、v22w、v22v、', 1)
open(OUTD + 'index.html', 'w').write(h)
print(parts, round(mb, 1), 'v22y gone', 'pre_v22y.pptx</div>' not in h)
