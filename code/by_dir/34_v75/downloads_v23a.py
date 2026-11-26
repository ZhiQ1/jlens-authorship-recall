"""Downloads page 2026-11-25 (coordinator: '50.4% vs 50.5%' removed everywhere, user-approved): main pptx v23a (新; v22z off page for the
256 MiB cap, cluster copy kept), script v70 (v69 -> 上一版, v68 -> 更早一版), leader pptx v17o (新; v17m -> 上一版, v17l -> 更早一版),
leader script v17o (v17n -> 上一版, v17m -> 更早一版). Builds from dl_v22z/index.html (= live v128, published in this session)."""
import re, base64, os
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/'; OUTD = '/home/zhang.zhiqi2/jlens_work/34_v75/dl_v23a/'
h = open('/home/zhang.zhiqi2/jlens_work/34_v75/dl_v22z/index.html').read()
def row(name): return re.search(r'\n    <li><div class="name">' + re.escape(name) + r'</div>.*?</li>', h, re.S).group(0)
def b64parts(fn, maxn=14_000_000, minparts=2):
    b = base64.b64encode(open(D + fn, 'rb').read()).decode(); n = max(minparts, -(-len(b) // maxn)); step = -(-len(b) // n); out = []
    for i in range(n):
        nm = f'{fn}.b64.part{i+1}.txt' if n > 1 else f'{fn}.b64.txt'; open(OUTD + nm, 'w').write(b[i * step:(i + 1) * step]); out.append(nm)
    return out
parts = b64parts('jlens_1113_pre_v23a.pptx'); mb = os.path.getsize(D + 'jlens_1113_pre_v23a.pptx') / 1e6
r = row('jlens_1113_pre_v22z.pptx')
h = h.replace(r, ('\n    <li><div class="name">jlens_1113_pre_v23a.pptx</div><div class="meta"><b>新</b> · 主 PPT v23a（192 页，2026-11-25）：同 v22z，只改了 S132 和 S133：'
    '“不在数据里”一栏去掉和打乱基线的对比（柱子标签只留 50.4%，该柱的随机刻度去掉，Result ① 改为“about half (50.4%) are not in the data”）；理由同删便签：一个名字在不在作者库里与配哪篇论文无关，打乱前后必然相同（你批准的）。'
    'v22z 的改动（S131 名字前一位置拆开、S132 删便签和拼错的真名）都在。你的形状、中文框和 16 条小标注原样保留；发布前检查 C1–C4 和保留检查全部通过。为不超过本页 256 MiB 的上限，v22z 已从本页移下（集群上保留） · '
    f'<span class="size">{mb:.1f} MB</span></div><button type="button" id="bpre23a" data-f="jlens_1113_pre_v23a.pptx" data-b64="{"|".join(parts)}">保存</button><div class="status" id="spre23a" role="status"></div></li>'), 1)
r69, r68 = row('script_stage1_13_v69.md'), row('script_stage1_13_v68.md')
s70 = os.path.getsize(D + 'script_stage1_13_v70.md') / 1e6
h = h.replace(r69, ('\n    <li><div class="name">script_stage1_13_v70.md</div><div class="meta"><b>新</b> · Stage 1–13 逐页讲稿（184 页；HTML deck v76 / 主 PPT v23a，页码与 v75 / v22z 相同，各页标题仍写 v75 / v22z），Markdown 可编辑：'
    '同 v69，只改了第 125 页：口播里 “50.4% 对 50.5%” 改为“大约一半（50.4%）根本不在数据里”，备查注明同一对比已从各处去掉；你用【】写的批注 44 条全部原样保留在原来那张幻灯片的页里 · '
    f'<span class="size">{s70:.2f} MB</span></div><button type="button" id="bscr70" data-f="script_stage1_13_v70.md">保存</button><div class="status" id="sscr70" role="status"></div></li>')
    + r69.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(r68, r68.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
lp = b64parts('jlens_leader_v17o.pptx', minparts=1); lmb = os.path.getsize(D + 'jlens_leader_v17o.pptx') / 1e6
rm, rl = row('jlens_leader_v17m.pptx'), row('jlens_leader_v17l.pptx')
h = h.replace(rm, ('\n    <li><div class="name">jlens_leader_v17o.pptx</div><div class="meta"><b>新</b> · 领导版 v17o（68 页，2026-11-25）：同 v17n（按 HTML deck 的 Part 结构重排，检验表按统一矩阵重建并分到附录第 52–53 页），'
    '只改了第 66 页一句：“Made-up names: about half (50.4%) are not in the data”，去掉和打乱基线的对比（与 HTML deck 第 125 页一致）；结构、比喻、标题、版面不变；发布前检查 C1–C4 通过 · '
    f'<span class="size">{lmb:.1f} MB</span></div><button type="button" id="blead17o" data-f="jlens_leader_v17o.pptx" data-b64="{"|".join(lp)}">保存</button><div class="status" id="slead17o" role="status"></div></li>')
    + rm.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(rl, rl.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
sn, sm = row('script_leader_v17n.md'), row('script_leader_v17m.md')
sl = os.path.getsize(D + 'script_leader_v17o.md') / 1e6
h = h.replace(sn, ('\n    <li><div class="name">script_leader_v17o.md</div><div class="meta"><b>新</b> · Leader PPT v17o（68 页）逐页讲稿，Markdown 可编辑：同 v17n，只把三处“和打乱基线一样（50.4% vs 50.5%）”改为“大约一半（50.4%）不在数据里”，'
    f'并更新开头的当前版本行；你用【】写的批注原样保留 · <span class="size">{sl:.2f} MB</span></div><button type="button" id="bscrL17o" data-f="script_leader_v17o.md">保存</button><div class="status" id="sscrL17o" role="status"></div></li>')
    + sn.replace('<b>新</b>', '<b class="old">上一版</b>', 1), 1)
h = h.replace(sm, sm.replace('<b class="old">上一版</b>', '<b class="old">更早一版</b>', 1), 1)
a = 'Stage 1–13 v69〔2026-11-25，按 HTML v75 顺序〕）、主 PPT v22z（按 HTML v75）'; assert a in h
h = h.replace(a, 'Stage 1–13 v70〔2026-11-25，按 HTML v76 顺序〕）、主 PPT v23a（按 HTML v76）', 1)
a = '包括主 PPT v22y、v22x、'; assert a in h; h = h.replace(a, '包括主 PPT v22z、v22y、v22x、', 1)
open(OUTD + 'index.html', 'w').write(h)
print(parts, lp, 'v22z gone', 'pre_v22z.pptx</div>' not in h)
