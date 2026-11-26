"""leader script v17l -> v17m (2026-11-23 freeze). Keeps every 【】 note verbatim and in place; version/maintenance lines move
to the changelog; headings get 'leader p · main pptx S'; changed pages get an EN/ZH spoken block + 备查."""
import re, json, sys
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/tools')
from pptx import Presentation
SRC = '/home/zhang.zhiqi2/jlens_work/script_leader_v17l.md'
DST = '/home/zhang.zhiqi2/jlens_work/script_leader_v17m.md'
MOVED = '/home/zhang.zhiqi2/jlens_work/27_leader17m/moved_to_changelog.md'
V22S = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/jlens_1113_pre_v22s.pptx'
t = open(SRC, encoding='utf-8').read()
moved = []

# ---- main pptx v22s page lookup by heading text (largest font), robust to renumbering
prs = Presentation(V22S)
def head(sl):
    best, tt = 0, ''
    for sh in sl.shapes:
        if not sh.has_text_frame or not sh.text_frame.text.strip(): continue
        sz = max([r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size] or [0])
        if sz > best: best, tt = sz, sh.text_frame.text.strip()
    return tt
HEADS = [head(s) for s in prs.slides]
def S(key):
    hits = [i + 1 for i, h in enumerate(HEADS) if key.lower() in h.lower()]
    return 'S%d' % hits[0] if hits else None
MAP = {1: 'One question, four lines of argument', 2: '276×', 3: 'Keys and shelves', 4: 'How we read the model', 5: 'Group comparisons: three findings',
       6: 'Content words carry the signal', 7: 'same-meaning made-up title gets about 75%', 8: 'The title is read in L24-L50',
       9: 'Names become readable late', 10: 'where the paper information travels', 11: 'The MLPs, not attention, write',
       12: 'What we learned: read early', 13: 'what the middle layers hold', 14: 'Prediction vs result', 15: 'Hidden author: supported on the same scale',
       16: 'first initial unlocks the name', 17: 'Strengthening the arrived information', 18: 'Names the model writes itself',
       19: 'What we learned: read early', 20: 'What we learned, continued', 22: '276×', 23: 'Group comparisons: three findings',
       24: 'Content words carry the signal', 25: 'same-meaning made-up title gets about 75%', 26: 'Not at the title',
       27: 'The title is read in L24-L50', 28: 'By L52 the name positions', 29: 'More-cited papers: the title arrives', 30: 'Names become readable late',
       31: 'where the paper information travels', 32: 'Name ← title carries the arrival', 33: 'In L52–L56 the MLPs carry',
       34: 'Layer order', 35: 'No clear earlier shelf', 36: 'Prediction vs result', 37: 'Which lens reads best', 38: 'what the middle layers hold',
       39: 'Same title, different question', 40: 'Same title, different question', 41: 'Same title, different question',
       42: 'Patchscope and paraphrases', 43: 'Patchscope and paraphrases', 44: 'subspace', 45: 'Hidden author: supported on the same scale',
       46: 'The title probe on every name token', 47: 'The title probe on every name token', 48: 'Recognition moves many quiet directions',
       49: 'First token or the rest of the name', 50: 'Strengthening the arrived information', 51: 'Made-up names are not confused neighbours',
       52: 'Patchscope and paraphrases'}
pm = {}
def newhead(m):
    n = int(m.group(1)); rest = m.group(2)
    s = S(MAP[n]) if n in MAP else None
    pm[n] = s
    return '## P%d · leader p%d · main pptx %s — %s' % (n, n, s if s else '—', rest)
t = re.sub(r'(?m)^## P(\d+) — (.*)$', newhead, t)

# ---- header version block -> changelog
hv = re.search(r'(?m)^版本：.*$', t).group(0)
moved.append(('header', hv)); t = t.replace(hv, '版本信息和修改历史见修改日志（~/jlens_work/changelog_2026-11-23.md 及更早的 changelog）。当前：jlens_leader_v17m.pptx，53 页。')
hs = re.search(r'(?m)^结构说明：.*$', t).group(0)
moved.append(('header', hs)); t = t.replace(hs, '结构说明：正文是 P1–P20，P21 是附录分隔页，附录是 P22–P53；每页标题写 leader 页码和主 PPT（v22s）对应页码，没有一一对应的写 “—”。')

# ---- version/maintenance lines inside pages (not inside 【】)
def strip_tag(line):
    new = re.sub(r'（v1\d[a-z]?）', '', line); new = re.sub(r'（v17i：[^）]*）', '', new)
    return new
out = []
for ln in t.split('\n'):
    if '【' in ln: out.append(ln); continue
    if re.match(r'^- v17j（用户 2026-11-21 确认）', ln):
        moved.append(('P14', ln)); continue
    nl = strip_tag(ln)
    if nl != ln: moved.append(('tag', ln))
    out.append(nl)
t = '\n'.join(out)
t = t.replace('（v17h）每个 ✓', '每个 ✓')

# ---- content sync (EN line then ZH line; 备查 not read aloud)
H2V = ('Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small '
       'paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; '
       'the baseline failed its positive control) and is larger for recognised papers (T3, marginal).')
def add_after_heading(n, block):
    global t
    m = re.search(r'(?m)^## P%d · .*$' % n, t)
    t = t[:m.end()] + '\n\n' + block + t[m.end():]
SAY = '**2026-11-23 更新 · 要说的话（一句英文一句中文）**\n'
add_after_heading(7, SAY +
 'One small exception survived a locked test: at layer 8 the title state carries a little of this paper\'s surname, beyond its topic.\n'
 '有一个小例外通过了锁定检验：第 8 层的标题状态里带着一点这篇论文的姓氏信号，超出了主题能解释的部分。\n'
 'So the answer is still "mostly meaning", with one small locked exception; the details are on page 52.\n'
 '所以答案仍然是“主要是意思”，外加一个小的锁定例外；细节在第 52 页。\n\n'
 '**备查（不念）：** H2 总判定（逐字）：' + H2V + ' 约一半来自主题（配对主题后保留 0.44 [0.36, 0.52]）。来源：391_groups/summary_a33/（补充 33，锁定 sha256 7a28ae2d…）。')
add_after_heading(14, SAY +
 'H2 now reads: not a general paper identity, with one small locked exception, a surname signal at layer 8.\n'
 'H2 现在的结论：不是一般意义上的“论文身份”，有一个小的锁定例外——第 8 层的姓氏信号。\n'
 'H1 still holds at the colon and the name slots, but which layer fixes the answer format is not pinned down.\n'
 'H1 在冒号和名字位置仍然成立，但哪一层把答案格式定下来，目前定不下来。\n\n'
 '**备查（不念）：** 天平上的代号改成了白话短词：swap = 换问题（X1），match = 跨问题找同一篇（X5），decode = 从标题解码（X4），part = 只换一小部分（X2），reword = 改写标题（X3），probe = 标题位置的检测器（E4b），ruler = 同一把尺子检验（补充 17），made-up = 虚构标题（补充 20）。H1 降级：锁定规则给出 L56，但主检验不单调、很可能被切断 attention sink 扭曲；patching 检验指向 L40–L56；补充检查（探索性）显示下凹只在切掉 sink 时出现（391_groups/summary_a23_supp/）。')
add_after_heading(19, SAY +
 'Read early, said late: the bottleneck is the late writing step, not reading.\n'
 '读得早，说得晚：瓶颈在后面写的那一步，不在读。\n'
 'On the form card, H2 now says: not a general paper identity, with one small surname exception at layer 8.\n'
 '在“什么形式”这张卡上，H2 现在写的是：不是一般意义上的论文身份，有一个第 8 层姓氏信号的小例外。\n\n'
 '**备查（不念）：** 一句话答案按用户 2026-11-23 定稿，不加“作者信息已经在那里，只是没用上”之类的说法；机制图在第 53 页。')
add_after_heading(36, '**备查（不念）：** 2026-11-23：代号列改为白话短词（question swap = X1、part swap = X2、reworded = X3、title decode = X4、match paper = X5、title probe = E4b、same scale = 补充 17、made-up title = 补充 20；表头 code → tag）。“Together” 行改为：H1 成立于冒号和名字位置（哪一层定格式定不下来）；H2 不是一般意义上的论文身份，有一个小的锁定例外（第 8 层姓氏信号，判定原文见第 52 页）；H3 同尺度下支持。旧的 “Together” 行原文：H2 → partly supported (C35): a real-title extra exists (R̄_T +0.11), mostly meaning (φ_T 0.75); it sits on rare words (add. 24 …), is not larger for recognised papers and smaller for more-cited ones (add. 22); wording vs made-up-title penalty open (p. 25)。')
add_after_heading(40, '**备查（不念）：** 2026-11-23 加一句：哪一层把格式定下来，目前定不下来（第 53 页）。')
add_after_heading(43, '**备查（不念）：** 2026-11-23 加一句：在 6,048 篇新论文上的锁定后续检验——一个小的姓氏信号在配对主题后仍然存在（第 52 页）。原来“削弱 H2”的判定针对“年份比作者晚出现”的顺序，仍然保留。')
t = t.replace('## P21 · leader p21', '## P21 · leader p21', 1)
add_after_heading(21, '**备查（不念）：** 2026-11-23 新增一行：52–53 → 正文 14、19（唯一的锁定例外；机制图）。页面上的内部标签（18b 第 N 项、add. N、addendum N）改成了白话名。')
t = t.rstrip('\n') + '\n\n' + (
 '## P52 · leader p52 · main pptx %s — Appendix · the one locked exception（唯一的锁定例外：第 8 层的姓氏信号）\n\n' % (S('Patchscope and paraphrases') or '—') +
 '**要说的话（一句英文一句中文）**\n'
 'We planted the layer-8 title state into a neutral prompt and asked for the first author, from three sources.\n'
 '我们把第 8 层的标题状态放进一个中性提示词，问第一作者，状态来自三个地方。\n'
 'The sources are this paper\'s own title, the same-field paper with the closest title, and a random same-field paper.\n'
 '三个来源是：这篇论文自己的标题、同领域里标题最接近的一篇、随机一篇同领域论文。\n'
 'P near one half means about half of the surname signal is this paper\'s own, and half comes from its topic.\n'
 'P 接近一半，意思是姓氏信号里大约一半是这篇论文自己的，另一半来自主题。\n'
 'Beyond the topic it holds firmly; beyond a text-only model and for recognised papers it only just passes.\n'
 '超出主题这一点很稳；超出纯文本模型、以及认得出的论文更强这两点，都只是刚过线。\n'
 'So it is a small locked exception, not strong evidence for a paper identity.\n'
 '所以这是一个小的锁定例外，不是“论文身份”的强证据。\n\n'
 '**备查（不念）：** 判定（逐字）：' + H2V + ' T1 超出主题 +0.0457 [0.0353, 0.0559]，Holm 下界 +0.033；T2 Qwen − BERT（标准化）+0.045 [0.008, 0.082]，Holm 下界 +0.002；T3 target − control（按引用分档）+0.0246 [0.003, 0.047]。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]；L0 来源 ≈ 0。BERT 文本基线正对照 gain −0.24 log10（WARN，基线弱）。n = 6,048 篇（target 4,577、control 1,471），补充登记 33 锁定于 2026-11-23 08:52（sha256 7a28ae2d…），在任何模型运行之前；作者团队整群 bootstrap 2,000 次；来源 391_groups/summary_a33/。\n\n'
 '## P53 · leader p53 · main pptx — — Appendix · mechanism map（机制图）\n\n'
 '**要说的话（一句英文一句中文）**\n'
 'This map puts the whole story on one picture: the prompt tokens across, the 64 layers up.\n'
 '这张图把整个故事放在一张图上：横着是提示词的每个 token，竖着是 64 层。\n'
 'The title is read from layer 24 and is done by layer 52; it reaches the name positions in layers 40 to 50.\n'
 '标题从第 24 层开始读，到第 52 层读完；在第 40 到 50 层到达名字的位置。\n'
 'The name is written only by the late MLPs in layers 57 to 61, and that writing step is where it fails.\n'
 '名字要到第 57 到 61 层才由后面的 MLP 写出来，卡住的就是这一步。\n'
 'Read early, said late: the bottleneck is the late writing step, not reading.\n'
 '读得早，说得晚：瓶颈在后面写的那一步，不在读。\n\n'
 '**备查（不念）：** 步骤①（哪一层定答案格式）已降级为“定不下来”；步骤③有一个小的锁定例外（第 52 页）。图 ~/jlens_work/25_restructure/mechanism_map.png（make_map.py）。\n')
open(DST, 'w', encoding='utf-8').write(t)
with open(MOVED, 'w', encoding='utf-8') as f:
    for where, ln in moved: f.write('- [%s] %s\n' % (where, ln))
print('pages mapped:', {k: v for k, v in pm.items()}, '\nmoved lines:', len(moved))
