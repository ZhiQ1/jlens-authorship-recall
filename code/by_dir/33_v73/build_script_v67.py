"""2026-11-25: main script v66 (HTML v72 / pptx v22w) -> v67 (HTML v73 / pptx v22x).
- 4 new pages (HTML v73 134, 159, 160, 161 = pptx v22x S142, S167, S168, S169): A block (EN line then ZH line; exp2story pages walk
  sentence by sentence through the main-line experiments that build it) + B block (备查: slide text, evidence, numbers in the figure,
  main-line list from 27_v67/experiment_contribution.md);
- updated figures (v73 143, 145, 146, 155, 158): one spoken EN/ZH pair added for the new element + a 备查 line; transitions on
  v73 133 and 158 point to the new next page;
- headings 'P{n} · HTML v73 p{n} · pptx S{k} (v22x)'; 'slide N' / '第 N 页' (v72 -> v73) and 'pptx S N' (v22w -> v22x) renumbered in
  spoken A blocks only, outside 【】; 【】 untouched and on their page.
usage: build_script_v67.py"""
import re, json
H = '/home/zhang.zhiqi2/jlens_work/'
SRC = H + 'script_stage1_13_v66.md'; OUT = H + 'script_stage1_13_v67.md'
RM = json.load(open(H + '27_v67/renumber_map_v73.json')); V = {int(a): b for a, b in RM['v72_to_v73'].items()}
PM = json.load(open(H + '27_v67/pptx_map_v22x_v73.json'))
PALL = {int(a): b for a, b in PM['v73_to_v22x_all'].items()}
W2X = {int(a): b for a, b in PM['v22w_to_v22x'].items()}
def pp(p):
    a = PALL[p]; return 'S%d' % a[0] if len(a) == 1 else 'S%d–S%d' % (a[0], a[-1])
t = open(SRC, encoding='utf-8').read()
first_part = t.index('\n# Part 0')
pre, body = t[:first_part + 1], t[first_part + 1:]
segs = [s for s in re.split(r'(?m)^(?=#{1,2} )', body) if s.strip()]
NOTE = re.compile(r'【.*?】', re.S)
def outside(text, fn):
    out, last = [], 0
    for m in NOTE.finditer(text):
        out.append(fn(text[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(fn(text[last:])); return ''.join(out)
def v(n): return V.get(n, n)
REF_EN = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
REF_ZH = re.compile(r'(第 ?)(\d{1,3})((?:[、，,–-] ?\d{1,3})*)( ?页)')
def renum(s):
    s = REF_EN.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(v(int(x.group(0)))), m.group(2)), s)
    s = REF_ZH.sub(lambda m: m.group(1) + str(v(int(m.group(2)))) + re.sub(r'\d+', lambda x: str(v(int(x.group(0)))), m.group(3)) + m.group(4), s)
    s = re.sub(r'(\bpptx S)(\d{1,3})\b', lambda m: m.group(1) + str(W2X.get(int(m.group(2)), int(m.group(2)))), s)
    s = re.sub(r'(主 pptx 当前页码：S)(\d{1,3})', lambda m: m.group(1) + str(W2X.get(int(m.group(2)), int(m.group(2)))), s)
    return s
def renum_a(rest):
    i = rest.find('\n**备查')
    if i < 0: return outside(rest, renum)
    return outside(rest[:i], renum) + rest[i:]
pages = {}; extras = {}; last = None; nnotes_old = {}
for sg in segs:
    head, _, rest = sg.partition('\n')
    if head.startswith('# '): continue
    m = re.match(r'## P(\d+) · HTML v72 p\d+ · pptx S[\dS–-]+ \(v22w\) — (.*)$', head)
    if m:
        n = int(m.group(1)); p = V[n]; title = outside(m.group(2), renum)
        pages[p] = '## P%d · HTML v73 p%d · pptx %s (v22x) — %s\n' % (p, p, pp(p), title) + renum_a(rest)
        nnotes_old[p] = NOTE.findall(sg); last = p; continue
    m = re.match(r'## pptx S(\d+)（仅主 pptx，HTML deck 无对应页）— (.*)$', head)
    if m:
        k = W2X[int(m.group(1))]
        extras.setdefault(last, []).append('## pptx S%d（仅主 pptx，HTML deck 无对应页）— %s\n' % (k, m.group(2)) + renum_a(rest)); continue
    raise SystemExit('unexpected heading: ' + head)
# ---------------- transitions to the new next pages
def swap(p, old_en, old_zh, en, zh):
    assert pages[p].count(old_en + '\n' + old_zh) == 1, p
    pages[p] = pages[p].replace(old_en + '\n' + old_zh, en + '\n' + zh, 1)
swap(133, 'Next, the same map six times, one stage lit at a time.', '接下来把同一张图看六遍，每次只点亮一段。',
     'Next, one page on the phenomenon itself, then the same map six times, one stage lit at a time.', '接下来先用一页看现象本身，再把同一张图看六遍，每次只点亮一段。')
swap(158, 'Next, what we learned, in words.', '接下来，用文字总结我们学到了什么。',
     'Next, which experiments build each sentence of the story.', '接下来看故事的每一句由哪些实验搭起来。')
# ---------------- updated figures: one spoken pair (before the closing pair) + a 备查 line
UPD = {
 143: ("On the right, a new box: the top lens word cannot decide; at layers 24 to 48 it is mostly punctuation or format, but it changes with the title for 28 to 64 percent of name tokens.",
       "右边新加了一个框：最上面的 lens 词定不下来；在第 24 到 48 层它大多是标点或格式词，但在 28% 到 64% 的名字 token 上会随标题变化。",
       '图右栏新增“Top lens word: cannot decide”框（L24–L48 最上面的 lens 词多为标点 / 格式，但 28–64% 的名字 token 上随标题变化）。'),
 145: ("On the right, a caveat: made-up titles are a little more likely to the model, log-prob 0.12 higher, so part of the extra may be closeness that the made-up title missed.",
       "右边有一条注意：编造的标题对模型来说可能性稍高，对数概率高 0.12；所以那一小块里可能有一部分是编造标题没贴近的意思。",
       '图右栏新增“Caveat: made-up title”框（编造标题的 log-prob 高 +0.12；意思越近找回越多 → 多出的部分可能有一部分是编造标题没贴近的意思）。'),
 146: ("On the right, a caveat on rare versus common words: the two swaps replace unequal numbers of words, 3.4 versus 2.1, and the common words are frequency-matched, not synonyms; with equal counts the gap remains, about 0.07, an exploratory check.",
       "右边有一条关于稀有词和常见词的注意：两种替换换掉的词数不同，3.4 对 2.1，常见词是按词频配的，不是同义词；词数相同时差距仍在，约 0.07，这是探索性检查。",
       '图右栏新增“Caveat: rare vs common words”框（替换词数 3.4 vs 2.1；常见词按词频配对、不是同义词；词数相同时差距仍在 +0.07，exploratory）。'),
 155: ("The step-one experiments now carry their numbers: the name prior is about 19 percent of the gap, the R0-only recount gives 0.20 with the same shape, and recognising needs about 40 citations against about 11,000 for writing.",
       "第一步下面的实验现在标了数字：名字先验约占差距的 19%，只用 R0 重算得到 0.20、形状相同，认得大约需要 40 次引用，写出则要大约 11,000 次。",
       '图中第 ① 步的实验条加了数字（name prior ~19% of the gap；R0-only recount +0.20, same shape；exposure: recognise ~40 vs write ~11,000 citations, ρ ~276）；左栏小样本救场框写明 pilot 50 → 200 papers，true title +9 / +5 pp。'),
 158: ("A new box at the bottom covers robustness across all steps: four pre-registered replication batches changed no conclusion, and neither did the name prior by layer.",
       "底部新加了一个框，讲所有步骤的稳健性：四批预注册的复现没有改变任何结论，逐层的名字先验也没有。",
       '图底新增“Robustness across all steps”框（四批预注册复现：false titles、all-token probes、position and component patching、completed groups，结论都没变；name prior by layer 不改结论；paper vs team 区间宽度比 ~1，"excludes 0" 在 1,155 行里变了 2 行）。'),
}
for p, (en, zh, bz) in UPD.items():
    s = pages[p]; i = s.index('\n\n**备查'); a, b = s[:i], s[i:]
    assert not NOTE.search(a), p
    L = a.split('\n'); L[-2:-2] = [en, zh]
    b = b.rstrip('\n') + '\n\n**备查（不念）· 图中新增的元素：** ' + bz + '\n'
    pages[p] = '\n'.join(L) + b
# ---------------- new pages
NEWS = json.load(open(W_ := H + '33_v73/new_slides_v73.json'))
A = {}
A[134] = [
 ("Before the map, one page on the phenomenon itself: the model recognises papers whose authors it cannot name.", "在看地图之前，先用一页讲现象本身：模型认得出这篇论文，却说不出它的作者。"),
 ("On the left, the share of papers recognised and the share written both rise with citations; recognising reaches one half at about 40 citations, writing at least one true author needs about 11,000.", "左边，认得的比例和写出的比例都随引用数上升；认得在大约 40 次引用时达到一半，写出至少一位真作者要大约 11,000 次。"),
 ("That is about 276 times more exposure, but the rule was locked after seeing the estimates, so only 'more than one' is confirmed.", "差不多要多 276 倍的曝光，但这条规则是看了估计值之后才锁定的，所以只确认了“大于 1”。"),
 ("On the right: is this just guessable names? Without the title, the name prior is only about 19 percent of the recognised-minus-other gap; the rest is specific to the paper.", "右边：这会不会只是容易猜的名字？去掉标题后，名字先验只占“认得减认不得”那个差距的约 19%，其余是这篇论文特有的。"),
 ("And papers where the model wrote no true author at all give the same picture, 0.20 against 0.21 for all papers.", "只看模型一个真作者都没写出的论文，结果也一样，0.20 对比全部论文的 0.21。"),
 ("So recognised but not said is real: a large exposure gap, not explained by guessable names. Next, the six stages one at a time.", "所以认得但说不出是真的：是一个很大的曝光差距，不能用容易猜的名字解释。接下来一次看一段，共六段。")]
A[159] = [
 ("This page and the next turn the hundred experiments back into the story: each band is one sentence on the right, built by the experiments on the left; thick lines are the main line.", "这一页和下一页把一百个实验变回故事：每一条带子是右边的一句话，由左边的实验搭起来；粗线是主线。"),
 ("Sentence one, recognised but not said, needs four main-line experiments together: the multiple-choice test defines who is recognised, the name-prior check shows it is not just guessable names, the group comparison shows recognised papers pull ahead only at the end, and the exposure threshold gives the 276-fold gap.", "第一句“认得但说不出”要四个主线实验合起来：选择题测试定义谁算认得，名字先验检查说明不只是容易猜的名字，分组比较显示认得的论文只在最后才拉开，曝光阈值给出 276 倍的差距。"),
 ("Sentence two, that at layers 0 to 4 the words decide everything, rests on one audit, the ceiling audit; it overturned the early claim of paper identity, so this sentence is grey: it cannot be decided.", "第二句“第 0 到 4 层由字决定一切”只靠一项审计，也就是天花板审计；它推翻了早期“支持论文身份”的说法，所以这一句是灰色：定不下来。"),
 ("Sentence three, early read-in with the colon following the question, comes from the colon test, new question versus new paper, plus the layer-8 surname test, the one small locked exception.", "第三句“早期读入、冒号跟着问题走”来自冒号检验，换问题对比换论文，再加上第 8 层的姓氏检验，也就是那个锁定的小例外。"),
 ("Sentence four, meaning and specific words but not paper identity, needs five together: swapping the paper-facts subspace, the made-up title, rare versus common words, the recognition and citation check, and the variance split.", "第四句“读走的是意思和具体用词，不是论文身份”要五个合起来：替换论文信息子空间、编造标题、稀有词对常见词、认得和引用数检查、方差分解。"),
 ("The thin cards underneath are supporting tests; the dashed ones ruled out an alternative. Next, sentences five to seven.", "下面的细线小卡片是辅助检验，虚线的那些排除了另一种解释。接下来是第五到第七句。")]
A[160] = [
 ("Sentence five, delivered to the names over many layers in parallel and read by layer 52, rests on a cross-check: put-back and take-away agree on layer 52, position by position it lands on the names, the windowed edge test finds the names-from-title edge, and the single-layer sweep finds no single bottleneck.", "第五句“经过多层并行送到名字、第 52 层读完”靠的是交叉验证：放回和拿走在第 52 层一致，逐位置看它落在名字上，窗口式切边找到名字看标题这条边，单层扫描找不到单一瓶颈。"),
 ("Sentence six, held at the names but not as words, combines one overturned claim, the format-locking test, with three positives: the MLPs at layers 52 to 56 carry paper information, the author-prompt lens reads nothing, and the same-scale probe reads more.", "第六句“存在名字位置、但不是以词的形式”把一个被推翻的说法，也就是格式锁定检验，和三个正面结果合在一起：第 52 到 56 层的 MLP 带论文信息，作者提示 lens 读不出，同尺度的 probe 读得更多。"),
 ("Sentence seven, the late MLPs write the name and it gets stuck at writing, combines first token versus the rest, giving the first initial and the mean ablation at layers 57 to 61, with one overturned claim: strengthening the arrived signal does not help.", "第七句“后面的 MLP 写出名字，卡在写出这一步”把第一个 token 对其余部分、给出名首字母、第 57 到 61 层均值消融合起来，再加一个被推翻的说法：加强已到达的信号没有用。"),
 ("Under sentence seven, gap one is still open: at which step does the knowledge of who wrote this paper enter? We only have indirect evidence.", "第七句下面，缺口一还开着：“谁写的这篇论文”在哪一步进来？我们只有间接证据。"),
 ("The grey box on the right counts the 24 experiments that added little: early small samples, method checks and infeasible designs. Next, all hundred at a glance.", "右边灰色的框数的是贡献很小的 24 个实验：早期小样本、方法检查和做不成的设计。接下来一眼看完全部一百个。")]
A[161] = [
 ("This page shows all hundred experiments at once, one column per tree, each cell marked with what it contributed.", "这一页一次展示全部一百个实验，每棵树一列，每个格子标出它贡献了什么。"),
 ("Forty-eight advanced the story, five overturned an earlier claim, twelve ruled out an alternative, eleven could not decide, and twenty-four added little.", "48 个推进了故事，5 个推翻了早先的说法，12 个排除了另一种解释，11 个定不下来，24 个贡献很小。"),
 ("The bold-bordered cells are the 24 main-line experiments, the ones on the previous two pages.", "粗边框的格子是 24 个主线实验，就是前两页上的那些。"),
 ("The overturned ones matter too: the ceiling audit, the format-locking test and the strengthening test each removed a wrong sentence from the story.", "被推翻的那些也重要：天花板审计、格式锁定检验和加强信号检验，各自从故事里拿掉了一句错话。"),
 ("So the story rests on 24 main-line experiments; the rest support it, rule things out, or mark what is still open. Next, what we learned, in words.", "所以故事靠 24 个主线实验；其余的在支持它、排除别的解释，或者标出还没解决的地方。接下来用文字总结我们学到了什么。")]
CON = open(H + '27_v67/experiment_contribution.md', encoding='utf-8').read()
def mainline(ss):
    rows = []
    for ln in CON.splitlines():
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) >= 7 and c[4] == '★' and c[5] in ss: rows.append('%s（%s，%s）：%s' % (c[0], c[5], c[3], c[6]))
    return rows
B = {
 134: ['**备查（不念）· 图中数字：** 左：c50 40 [36, 44] vs 11,038 [8,172, 15,607] 次引用；ρ = c50(write) / c50(recognise) = 276 [203, 390]；约 25% 猜测底；n = 9,108 篇；规则在看到估计值后锁定 → 只确认 ρ > 1。'
       '右：name prior +0.047 [0.031, 0.062] vs true title +0.247（约 19%）；R0 +0.199 vs 全部 +0.207；对照：去掉标题时真作者列表看起来最真的比例 0.26，机会水平 0.25。',
       '**备查（不念）· 出处：** 第 7、24、26、41、68 页（选择题测试、曝光阈值、R0 重算、分组比较、名字先验）；27_v67/experiment_contribution.md S1。'],
 159: ['**备查（不念）· 主线实验（★，出处 27_v67/experiment_contribution.md）：**'] + ['- ' + r for r in mainline({'S1', 'S2', 'S3', 'S4'})],
 160: ['**备查（不念）· 主线实验（★，出处 27_v67/experiment_contribution.md）：**'] + ['- ' + r for r in mainline({'S5', 'S6', 'S7'})] +
      ['缺口 ①：“谁写的这篇论文”在哪一步进来，只有间接证据。'],
 161: ['**备查（不念）· 计数（出处 27_v67/experiment_contribution.md）：** ✓ 48 · ✗ 5 · ⊘ 12 · ~ 11 · ○ 24；★ 主线 24（共 100）。各树：Overview 3、Phenomenon 12、H1 5、H2 26、Route 10、H3 14、Writing 15、Audits 15。'],
}
TAGZH = {'desc': 'descriptive', 'solid': 'fairly solid', 'lnot': 'not supported / locked', 'lsup': 'supported / locked', 'settled': 'settled', 'expl': 'exploratory'}
for x in NEWS:
    pg, f, title, ask, so, tc, tt = x[:7]; sok = x[8] if len(x) > 8 else 'So (this slide)'
    s = ['## P%d · HTML v73 p%d · pptx %s (v22x) — %s\n' % (pg, pg, pp(pg), title), '**要说的话（一句英文一句中文）**']
    for en, zz in A[pg]: s += [en, zz]
    s += ['', '**备查（不念）· 本页幻灯片全文：** %s Now asking: %s [figure: %s] %s: %s %s' % (title, ask, f[:-4].replace('_', ' '), sok, so, tt),
          '', '**备查（不念）· 证据强度：** %s（页底标签“%s”）。%s' % (TAGZH[tc], tt,
              '图内自带三行灰字（公式、n、读法）。' if pg == 134 else '这是故事图示意图，没有画数值，所以没有公式 / n 行。'), '']
    for ln in B[pg]: s.append(ln)
    s.append('')
    pages[pg] = '\n'.join(s) + '\n'
N = max(pages)
assert sorted(pages) == list(range(1, N + 1)), [p for p in range(1, N + 1) if p not in pages]
parts = []
for ln in open(H + '27_v67/toc_v73.md', encoding='utf-8'):
    m = re.match(r'## (Part .*?|Glossary.*?) \((\d+)–(\d+)\)\s*$', ln.strip())
    if m: parts.append((int(m.group(2)), '# %s (%s–%s)\n\n' % (m.group(1), m.group(2), m.group(3))))
phead = dict(parts)
out = [pre]
for p in range(1, N + 1):
    if p in phead: out.append(phead[p])
    out.append(pages[p].rstrip('\n') + '\n\n')
    for e in extras.get(p, []): out.append(e.rstrip('\n') + '\n\n')
txt = ''.join(out)
open(OUT, 'w', encoding='utf-8').write(txt)
bad = [p for p, notes in nnotes_old.items() if NOTE.findall(pages[p]) != notes]
print('pages', N, 'parts', len(parts), 'notes old', sum(len(v) for v in nnotes_old.values()), 'notes new', len(NOTE.findall(txt)), 'mismatch', bad,
      'mainline rows', len(B[159]) - 1, len(B[160]) - 2)
