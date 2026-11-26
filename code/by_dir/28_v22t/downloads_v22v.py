"""Downloads page (5Tdt1mQa8xnPiqQEKvjzta) 2026-11-25: main pptx v22v added (new), v22u -> 上一版, v22t removed from the page to stay under the 256 MiB cap
(cluster copy kept: /scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/jlens_1113_pre_v22t.pptx and reports/downloads/); script v65 added (v64 -> 上一版,
v63 -> 更早一版); leader script v17n replaced (heading page numbers only, HTML v71 / main pptx v22v). Builds from the LIVE page file."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/28_v22t/dl_live_w/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/28_v22t/dl_v22v/'; os.makedirs(OUTD, exist_ok=True)
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/jlens_1113_pre_v22v.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 15_500_000))
step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22v.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
r22t, r22u = row('jlens_1113_pre_v22t.pptx'), row('jlens_1113_pre_v22u.pptx')
h = h.replace(r22t, '', 1)
new = ('\n    <li><div class="name">jlens_1113_pre_v22v.pptx</div><div class="meta"><b>新</b> · 主 PPT v22v（163 页，2026-11-25）：按 HTML deck v71 的顺序：'
       '新增三页（S16 统计约定续页、S81 “How the 75% is computed”、S114 读出地图的锁定规则），备用页 B12 移到 S51、B22 移到 S58（紧跟各自的正文页），'
       '删除九张 “How computed” 备用页（B13–B21，用户 2026-11-24 批准；内容已移到 S16 和讲稿备查），B23 保留；我们自己文字里的页码全部改成 v22v 页码；'
       '你的形状和中文框原样保留；发布前检查 C1–C4 和保留检查全部通过 · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22v" data-f="jlens_1113_pre_v22v.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22v" role="status"></div></li>')
h = h.replace(r22u, new + r22u.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
# scripts
r64, r63 = row('script_stage1_13_v64.md'), row('script_stage1_13_v63.md')
s65 = os.path.getsize('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/script_stage1_13_v65.md') / 1e6
new65 = ('\n    <li><div class="name">script_stage1_13_v65.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿，按 HTML deck v71 的顺序（155 页；主 PPT v22v 页码），Markdown 可编辑：'
         '每页标题写 HTML v71 页码和主 PPT v22v 页码；新增三页的讲稿（统计约定续页、“How the 75% is computed”、读出地图的锁定规则：一句英文一句中文的“要说的话”加备查）；'
         '删除九张 “How computed” 备用页的讲稿页（原内容已移到统计约定续页和各页备查）；原备用页上正文没有的条目已写进对应页的备查；'
         f'你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · <span class="size">{s65:.2f} MB</span></div><button type="button" id="bscr65" data-f="script_stage1_13_v65.md">保存</button><div class="status" id="sscr65" role="status"></div></li>')
h = h.replace(r64, new65 + r64.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r63, r63.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
rL = row('script_leader_v17n.md')
rL2 = rL.replace('每页标题写领导版页码、HTML v68 页码和主 PPT v22t 页码', '每页标题写领导版页码、HTML v71 页码和主 PPT v22v 页码（2026-11-25 只更新了标题里的页码）', 1)
assert rL2 != rL; h = h.replace(rL, rL2, 1)
h = h.replace('Stage 1–13 v64〔2026-11-24，按 HTML v70 新顺序〕）、主 PPT v22u（按 HTML v70）', 'Stage 1–13 v65〔2026-11-25，按 HTML v71 顺序〕）、主 PPT v22v（按 HTML v71）', 1)
h = h.replace('（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22s、', '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22t、v22s、', 1)
open(OUTD + 'index.html', 'w').write(h)
print('ok parts', parts, round(mb, 1), 'v22t gone:', 'pre_v22t.pptx</div>' not in h, 'v65 row:', 'script_stage1_13_v65.md</div>' in h, 'lead:', 'v22v（按 HTML v71）' in h)
