"""Downloads page (5Tdt1mQa8xnPiqQEKvjzta) 2026-11-24: main pptx v22u added (new), v22t -> 上一版, v22s removed from the page (cluster copy kept; user approved 2026-11-24). Builds from the LIVE page file."""
import re, base64, os
SRC = '/home/zhang.zhiqi2/jlens_work/28_v22t/dl_live_v/index.html'; OUTD = '/home/zhang.zhiqi2/jlens_work/28_v22t/dl_v22u/'; os.makedirs(OUTD, exist_ok=True)
h = open(SRC).read()
pp = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/jlens_1113_pre_v22u.pptx'
b = base64.b64encode(open(pp, 'rb').read()).decode(); n = max(2, -(-len(b) // 15_500_000))
step = -(-len(b) // n); parts = []
for i in range(n):
    fn = f'jlens_1113_pre_v22u.pptx.b64.part{i+1}.txt'; open(OUTD + fn, 'w').write(b[i * step:(i + 1) * step]); parts.append(fn)
mb = os.path.getsize(pp) / 1e6
v22s = re.search(r'\n    <li><div class="name">jlens_1113_pre_v22s\.pptx</div>.*?</li>', h, re.S).group(0)
v22t = re.search(r'\n    <li><div class="name">jlens_1113_pre_v22t\.pptx</div>.*?</li>', h, re.S).group(0)
h = h.replace(v22s, '', 1)
prev = v22t.replace('<b>新</b>', '<b class="old">上一版</b>', 1)
new = ('\n    <li><div class="name">jlens_1113_pre_v22u.pptx</div><div class="meta"><b>新</b> · 主 PPT v22u（169 页，2026-11-24）：页序同 v22t（HTML v68/v70 顺序），同步 HTML v69–v70 的修改：'
       '假设表两页和四个 Part 的证据矩阵按统一的假设 × 检验矩阵重做（S58 用户批准：旧版留底在 B23，形状数减少是版式变化，不是删内容），假设表第 2 页改为指引“Full evidence matrix → slide 135”，'
       '页码引用修正（S57、S86、S144）、S24 过强动词改为 “carries information about”，新增备用页 B23（S169，被取代的旧版矩阵）；你的形状和中文框原样保留；发布前检查 C1–C4 和保留检查全部通过 · '
       f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre22u" data-f="jlens_1113_pre_v22u.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre22u" role="status"></div></li>')
h = h.replace(v22t, new + prev, 1)
h = h.replace('主 PPT v22t（按 HTML v68 新顺序）', '主 PPT v22u（按 HTML v70）', 1)
h = h.replace('（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括 ', '（/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/，包括主 PPT v22s、', 1)
open(OUTD + 'index.html', 'w').write(h)
print('ok parts', parts, [len(open(OUTD + p).read()) for p in parts], round(mb, 1), 'v22s gone:', 'pre_v22s.pptx</div>' not in h)
