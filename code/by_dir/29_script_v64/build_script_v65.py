"""2026-11-24: main script v65 = working copy script_stage1_13_v65.md (v70 order, 备查 items moved from the deleted
How-computed backups already added) -> HTML v71 order, headings 'P{n} · HTML v71 p{n} · pptx S{k} (v22v)'.
- drops the nine How-computed backup pages (v70 152-160; pointer-only pages, no 【】; their content now on slide 16 / in 备查)
- adds pages for the 3 new v71 slides (16, 77, 107) with A (spoken EN/ZH) + B (备查)
- renumbers 'slide N' / '第 N 页' (v70 -> v71) and 'pptx S N' (v22u -> v22v) OUTSIDE 【】; 【】 untouched and kept on their page
usage: build_script_v65.py"""
import re, json
H = '/home/zhang.zhiqi2/jlens_work/'
SRC = H + 'script_stage1_13_v65.md'; OUT = H + 'script_stage1_13_v65.md'
RM = json.load(open(H + '27_v67/renumber_map_v71.json')); V = {int(a): b for a, b in RM['v70_to_v71'].items()}; DEL = set(RM['deleted_v70'])
PM = json.load(open(H + '27_v67/pptx_map_v22v_v71.json'))
P71 = {int(a): b for a, b in PM['v71_to_v22v_first'].items()}; P71ALL = {int(a): b for a, b in PM['v71_to_v22v_all'].items()}
def pp(p):
    a = P71ALL.get(p, [P71[p]]); return 'S%d' % a[0] if len(a) == 1 else 'S%d–S%d' % (a[0], a[-1])
U2V = {int(a): b for a, b in PM['v22u_to_v22v'].items()}
t = open(SRC, encoding='utf-8').read()
open(H + 'script_stage1_13_v65.before_v71.md', 'w', encoding='utf-8').write(t)
first_part = t.index('\n# Part 0')
pre, body = t[:first_part + 1], t[first_part + 1:]
segs = re.split(r'(?m)^(?=#{1,2} )', body)
segs = [s for s in segs if s.strip()]
NOTE = re.compile(r'【.*?】', re.S)
def outside(text, fn):
    out, last = [], 0
    for m in NOTE.finditer(text):
        out.append(fn(text[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(fn(text[last:])); return ''.join(out)
def v70(n): return V.get(n, n) if n not in DEL else 16
REF_EN = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
REF_ZH = re.compile(r'(第 ?)(\d{1,3})((?:[、，,–-] ?\d{1,3})*)( ?页)')
REF_S = re.compile(r'(\bpptx S|主 pptx 当前页码：S|\bS)(\d{1,3})(?=\D)')
def renum_a(rest):
    # only the spoken A block is renumbered; the 备查 blocks hold archived text from earlier versions with their own numbering
    i = rest.find('\n**备查')
    if i < 0: return outside(rest, renum)
    return outside(rest[:i], renum) + rest[i:]
def renum(s):
    s = REF_EN.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(v70(int(x.group(0)))), m.group(2)), s)
    s = REF_ZH.sub(lambda m: m.group(1) + str(v70(int(m.group(2)))) + re.sub(r'\d+', lambda x: str(v70(int(x.group(0)))), m.group(3)) + m.group(4), s)
    s = re.sub(r'(\bpptx S)(\d{1,3})\b', lambda m: m.group(1) + str(U2V.get(int(m.group(2)), int(m.group(2)))), s)
    s = re.sub(r'(主 pptx 当前页码：S)(\d{1,3})', lambda m: m.group(1) + str(U2V.get(int(m.group(2)), int(m.group(2)))), s)
    return s
pages = {}; extras = {}; dropped = []; last = None; order_keys = []
for sg in segs:
    head, _, rest = sg.partition('\n')
    if head.startswith('# '): continue                    # Part headers rebuilt below
    m = re.match(r'## P(\d+) · HTML v70 p\d+ · pptx S[\dS–-]+ \(v22u\) — (.*)$', head)
    if m:
        n = int(m.group(1))
        if n in DEL:
            assert '【' not in sg, n; dropped.append(n); last = None; continue
        p = V[n]; title = outside(m.group(2), renum)
        pages[p] = '## P%d · HTML v71 p%d · pptx %s (v22v) — %s\n' % (p, p, pp(p), title) + renum_a(rest)
        last = p; continue
    m = re.match(r'## pptx S(\d+)（仅主 pptx，HTML deck 无对应页）— (.*)$', head)
    if m:
        k = U2V[int(m.group(1))]
        extras.setdefault(last, []).append('## pptx S%d（仅主 pptx，HTML deck 无对应页）— %s\n' % (k, m.group(2)) + renum_a(rest)); continue
    raise SystemExit('unexpected heading: ' + head)
NEW = {}
NEW[16] = """## P16 · HTML v71 p16 · pptx S%d (v22v) — Statistical conventions (continued)

**要说的话（一句英文一句中文）**
This page answers one question: which kind of interval sits behind each number in the deck?
这一页只回答一个问题：deck 里每个数字背后的置信区间是哪一种？
Unless a slide says otherwise, we resample whole author teams, two thousand times, so papers written by the same people are not counted as independent.
除非页面另有说明，我们都是按整个作者团队重抽样两千次，这样同一批作者写的论文不会被当成相互独立。
Where two conditions are compared on the same papers, the draws are paired.
在同一批论文上比较两种条件时，抽样是配对的。
A few slides resample single papers instead, and the format test corrects over its five answer formats.
少数几页改为按单篇论文重抽样，答案格式检验则对五种格式做了多重比较校正。
So from here on, when you see an interval, it is a team-level interval unless the slide says otherwise. Next, the probe.
所以后面看到的区间，除非页面另说，都是按团队算的。下一页讲 probe。

**备查（不念）：** 团队聚类 bootstrap ×2,000：第 20、25、32、34、37、46、75、78、79、98、99、100、102、103、106、124、125、152 页（第 99、100 页为配对抽样；第 32 页两个引用半区共用一组抽样）。论文层面 bootstrap：第 42、43、45、71 页。Holm 校正：第 34 页对 5 项答案格式检验。本页取代原九张"How computed"备用页（B13–B21）上的逐页统计说明（2026-11-24 用户批准删除那九页）。证据强度：descriptive。
""" % P71[16]
NEW[77] = """## P77 · HTML v71 p77 · pptx S%d (v22v) — How the 75%% is computed

**要说的话（一句英文一句中文）**
This page asks: how exactly do we get "about three quarters" from the scores on the previous page?
这一页问：上一页的"大约四分之三"到底是怎么从分数里算出来的？
We score each paper three ways: with the true title, with the same-topic card, and with five wrong titles, which we average.
我们给每篇论文打三种分：用真标题、用那张同主题的卡片、再用五个错误标题取平均。
Put the three scores on one line: the gap from the wrong titles to the true title is the whole advantage, and the gap from the wrong titles to the card is what the card brings back.
把三个分数放在一条线上：从错误标题到真标题的距离是全部优势，从错误标题到卡片的距离是卡片找回的部分。
On the chart, the share is that second gap divided by the first; 1 would mean meaning alone brings back everything, and we see about 0.75.
图上的比例就是后一段除以前一段；等于 1 表示单靠意思就能找回全部，我们看到的是约 0.75。
The rule was fixed before the run: the share is read only when the real title's small extra is clearly above zero, and 0.75 falls in the top band, "meaning explains most".
规则在运行前就定好了：只有当真标题多出的那一小块明显大于零时才读这个比例，而 0.75 落在最高一档，"大部分由意思解释"。
So "about 75%%" is a locked reading of this one test; the next pages ask what the remaining small part is.
所以"约 75%%"是这一项检验的锁定读法；接下来几页问剩下的那一小块是什么。

**备查（不念）：** 每篇论文的得分 S = 名字各 token 的 log10(1/排名) 取平均（最后一层，所有作者、所有 token）；F̄ = 5 个假标题（false_0…false_4）的平均；G = S_true − F̄，A = S_fict − F̄，R = S_true − S_fict；φ = ΣA / ΣG（组内求和之比）。认得的论文（566 篇）：G 0.425，A 0.319，φ̂ = 0.751 [0.723, 0.778]，R̄ +0.106 [+0.094, +0.118]；对照组 561 篇。判定分档（运行前锁定）：φ̂ < 0.3 强支持（论文身份），0.3–0.5 部分支持、权重有限，≥ 0.5 部分支持、以意思解释为主；R̄ 的 CI 含 0 = 不支持，< 0 = 推翻；φ 的 CI 跨过 0.3 或 0.5 = 边界。S_true 和假标题得分取自已存的全队列运行，S_fict 取自本次运行。这是这一项检验的锁定读法；H2 的总判定见判定卡。证据强度：locked。
""" % P71[77]
NEW[107] = """## P107 · HTML v71 p107 · pptx S%d (v22v) — The locked rule of the readout map

**要说的话（一句英文一句中文）**
This page asks: what exactly does the readout map's rule require before a position counts as an "earlier shelf"?
这一页问：读出地图上的规则，到底要满足什么，一个位置才算"更早的架子"？
Picture a grid: the prompt positions across, the layers up to 48, and three ways of reading.
想象一张网格：横着是提示词的各个位置，竖着是到第 48 层为止的各层，再乘上三种读法。
A cell counts only if two things hold at the same layer: that position already shows the author signal, while the name position does not yet.
一个格子要同时满足两个条件才算：这个位置已经出现作者信号，而同一层的名字位置还没有。
A few cells pass, but the effects are tiny, and about as many would pass by chance.
有少数格子满足，但效应都很小，靠偶然也会有差不多这么多。
So there is no clear earlier shelf, only faint, scattered traces before layer 48. Next, the summary of what each readout can see.
所以没有清楚的更早架子，第 48 层之前只有零星的微弱痕迹。下一页是各种读法能看到什么的小结。

**备查（不念）：** 分档内 target − control 的 spec；规则：某位置在某层 L ≤ 48 的 CI 大于 0，同时名字位置在该层的 CI 包含 0（两个 CI 的比较，不是配对检验）。可估计的格子 672 个（9 个提示位置 × 到 L48 为止的 14 层 × 3 种读法 × 2 个名字 token；引号位置不可估计），其中 60 个 CI > 0，偶然预期约 17 个，未做多重比较校正。满足规则的格子：logit lens 年份从 L40 起、":" 在 L45、"Authors" 在 L36；J-lens 标题第一个 token 在 L8；probe 标题在 L32；效应 +0.008 到 +0.049。600 篇（300 target + 300 control），团队 bootstrap ×2,000；probe 在 600 篇上训练。数据文件见第 106 页备查。证据强度：exploratory。
""" % P71[107]
pages.update(NEW)
N71 = max(pages)
assert sorted(pages) == list(range(1, N71 + 1)), [p for p in range(1, N71 + 1) if p not in pages]
# Part headers from toc_v71
parts = []
for ln in open(H + '27_v67/toc_v71.md', encoding='utf-8'):
    m = re.match(r'## (Part .*?|Glossary.*?) \((\d+)–(\d+)\)\s*$', ln.strip())
    if m: parts.append((int(m.group(2)), '# %s (%s–%s)\n\n' % (m.group(1), m.group(2), m.group(3))))
phead = dict(parts)
out = [pre]
for p in range(1, N71 + 1):
    if p in phead: out.append(phead[p])
    out.append(pages[p].rstrip('\n') + '\n\n')
    for e in extras.get(p, []): out.append(e.rstrip('\n') + '\n\n')
txt = ''.join(out)
txt = re.sub(r'HTML v70', 'HTML v71', txt, count=0) if False else txt
open(OUT, 'w', encoding='utf-8').write(txt)
print('pages', N71, 'dropped', dropped, 'pptx-only', sum(len(v) for v in extras.values()), 'part headers', len(phead))
