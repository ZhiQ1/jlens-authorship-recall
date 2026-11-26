#!/usr/bin/env python3
"""Leader script v17m -> v17n (user 2026-11-23): new page order = leader deck v17n (Part structure).
Every page: A block (spoken, one EN line then one ZH line) + B block (备查, not read). Old page text is kept verbatim inside
the B block (including every 【…】 note, in place on its page). Headings: leader page + HTML v67 page; main pptx v22t page is
filled later from 27_v67/pptx_map_v22t.json (heading says 'main pptx — (v22t pending)' until then).
"""
import re, json
SRC = '/home/zhang.zhiqi2/jlens_work/script_leader_v17m.md'
OUT = '/home/zhang.zhiqi2/jlens_work/script_leader_v17n.md'
LOG = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/leader1/v17n/build_leader17n_log.json'))
NEWPOS = {(int(k) if k.isdigit() else k): v for k, v in LOG['newpos'].items()}
ORDER = LOG['order']
LMAP = json.load(open('/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/180809d4-e5ec-4f13-97be-7ef90a42d8be/scratchpad/leader_map.json'))
H67 = {int(k): v[2] for k, v in LMAP.items()}
H67.update({52: 78, 53: 125})
H67_NEW = {'Q2': 24, 'V2': 34, 'Q1': 38, 'Q3a': 'NEW39', 'Q3b': 'NEW48', 'V1': 51, 'QH2': 53, 'VH2': 79, 'Q3': 81, 'V3': 103, 'QW': 105, 'VW': 121, 'LED': 131, 'SET': 134}
_M68 = {int(k): v for k, v in json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/v67_to_v68.json')).items()}
H67 = {k: (_M68.get(v) if v else None) for k, v in H67.items()}
H67_NEW = {k: (int(v[3:]) if isinstance(v, str) else _M68[v]) for k, v in H67_NEW.items()}
PMAP = None
try:
    PMAP = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t.json'))
except Exception:
    pass

t = open(SRC, encoding='utf-8').read()
parts = re.split(r'(?m)^(## .*)$', t)
head = parts[0]
pages = {}
overview = None
for j in range(1, len(parts) - 1, 2):
    h, b = parts[j], parts[j + 1]
    m = re.match(r'## P(\d+) · leader p\d+ · main pptx [^—]*— (.*)$', h)
    if m:
        ttl = re.sub(r'^—\s*', '', m.group(2).strip())
        ttl = {52: 'Part 4 · the one locked exception（唯一的锁定例外：从第 8 层起的姓氏信号）',
               53: 'Part 7 · the answer on one map（机制图）'}.get(int(m.group(1)), ttl)
        pages[int(m.group(1))] = (ttl, b.strip('\n'))
    elif h.startswith('## 论证链概览'): overview = b.strip('\n')
assert len(pages) == 53, len(pages)

P = lambda k: NEWPOS[k]

# ---------------------------------------------------------------- A blocks (EN line, ZH line)
A = {
 1: [('People ask an AI who wrote a paper, and it confidently names authors who do not exist.', '大家问 AI 某篇论文是谁写的，它会很自信地报出根本不存在的作者。'),
     ('Two pictures: it does not know, or it knows but cannot say.', '两种可能：它不知道，或者它知道但说不出来。'),
     ('For papers it recognises, the answer is the second picture.', '对它认得出的论文，答案是第二种。')],
 3: [('Think of the model as a library with 64 floors; the title is the key, the authors are the book.', '把模型想成一座 64 层的图书馆：标题是钥匙，作者是那本书。'),
     ('A trolley carries things up, a desk works on them, and the top floors say the next word.', '推车把东西往上送，书桌加工，最上面几层把下一个词说出来。')],
 4: [('We look inside three ways: read the label, scan the barcode, or swap and lock.', '我们用三种办法往里看：读标签、扫条形码、换货或锁门。'),
     ('The label reader (lens) sees only words; the scanner (probe) can see what is not yet a word.', '读标签（lens）只看得到已经是词的东西；扫描器（probe）能看到还不是词的东西。')],
 2: [('Shown four author lists, it picks the right one; asked to write the authors, it writes none.', '给它四份作者名单，它能挑对；让它自己写，一个真作者也写不出。'),
     ('Recognising needs about 40 citations, writing about 11,000: about 276 times more.', '认出来大约要 40 次引用，写出来要大约 11,000 次，差了大约 276 倍。'),
     ('So knowing and saying are two different things.', '所以知道和说得出是两回事。')],
 13: [('Before a name comes out, what form is the book in? Three pictures.', '名字说出来之前，书是什么形式？有三种图景。'),
      ('H1: the middle layers hold the task; H2: they hold which paper; H3: the authors are there, but not yet as words.', 'H1：中间层装的是任务；H2：装的是哪篇论文；H3：作者信息在，但还不是词。'),
      ('The three can all be partly true; the next pages test each one.', '三者可以同时部分成立；后面几页逐个检验。')],
 14: [('Here every test is put on a balance, for or against each picture.', '这里把每个检验放到天平上，看它支持还是反对每种图景。'),
      ('The task at the colon holds; meaning, not paper identity, with one small exception; hidden authors hold on the same scale.', '冒号处的任务成立；是意思不是论文身份，有一个小例外；藏着的作者在同一把尺子上成立。'),
      ('Part 3 starts with the first picture: the task.', '第 3 部分先看第一种图景：任务。')],
 8: [('If the title were read only at the top, swapping it in at layer 50 would bring little back.', '如果标题要到最上面才被读，在第 50 层换货应该找不回多少。'),
     ('In fact the trolley is half full at layer 45, 93% at layer 50 and almost full at layer 52.', '实际上推车在第 45 层装了一半，第 50 层 93%，第 52 层几乎全满。'),
     ('The title is read on the way up, early.', '标题在往上走的路上就读完了，读得早。')],
 5: [('If the model did not know the paper, the real title would pull no harder than a look-alike.', '如果模型不知道这篇论文，真标题的拉力不会比长得像的假标题大。'),
     ('In fact only the real key opens the book: knowing the paper adds +0.42, an easy-to-guess name only +0.02.', '实际上只有真钥匙打得开：知道这篇论文贡献 +0.42，好猜的名字只贡献 +0.02。')],
 6: [('Swap meaningful words for synonyms and the key still turns; swap them for random words and it does not.', '把有意义的词换成近义词，钥匙还能转；换成随机词就转不动。'),
     ('So the key is the title’s meaning, not its exact spelling; this page is descriptive.', '所以钥匙是标题的意思，不是写法；这一页是描述性的。')],
 7: [('A forged key: a made-up title with the same meaning, for a paper that does not exist.', '一把仿造的钥匙：意思相同、但论文并不存在的编造标题。'),
     ('It opens three quarters; the real title adds only a little more, mostly on rare words.', '它能打开四分之三；真标题只多给一点，主要落在罕见词上。'),
     ('That extra is not larger for recognised papers, so it is mostly meaning.', '多出来的部分在认得出的论文上并不更大，所以主要是意思。')],
 52: [('The one locked exception: a small surname signal at the title state from layer 8, beyond its topic.', '唯一的锁定例外：从第 8 层起，标题状态里有一个小的、超出主题的姓氏信号。'),
      ('The locked test is at layer 8; later layers show more, peaking at layer 40, but that part is descriptive.', '锁定检验只在第 8 层；后面的层更大，第 40 层最高，但那部分只是描述性的。'),
      ('Beyond a text-only model and for recognised papers it only just passes, and about half of it is topic.', '超出纯文本模型、认得出的论文更强，这两点都只是刚过线，而且大约一半来自主题。'),
      ('So it is a small locked exception, not strong evidence for a paper identity.', '所以它是一个小的锁定例外，不是论文身份的强证据。')],
 10: [('If one part did all the work, swapping just that part would bring almost everything back.', '如果只有一个部件在干活，单换它就应该找回几乎全部。'),
      ('Instead it is a relay: attention fetches the title around layer 48, the desk works on it, and it lands on the name slots.', '实际上是一场接力：注意力在第 48 层附近把标题取过来，书桌加工，最后落在名字格。'),
      ('Closing any one corridor costs only a few percent: no single route.', '关掉任何一条走廊只损失几个百分点：没有唯一的路线。')],
 15: [('If there were no author information before it becomes a word, the scanner and the label reader would tie.', '如果变成词之前根本没有作者信息，扫描器和读标签应该打平。'),
      ('On the same ruler, the scanner sees a little more in the middle layers, by a rule locked in advance.', '在同一把尺子上，扫描器在中间层多看到一点，判据是事先锁定的。'),
      ('So the authors are there, but not yet as words; the effect is small.', '所以作者信息在，但还不是词；效应小。')],
 9: [('If fetching meant saying, the cover would be readable as soon as the book arrives.', '如果拿到就等于说得出，书一送到，封面上的字就该读得出来。'),
     ('The book is half there by layer 45, but the label reader reaches half only at layer 58.', '书在第 45 层就到了一半，可读标签要到第 58 层才读到一半。'),
     ('In between, the book has arrived but is still wrapped.', '中间这一段，书已经到了，但还包着包装纸。')],
 11: [('In layers 52 to 56 the desk carries the paper, but not as ready-made name cards.', '第 52 到 56 层，书桌带着这篇论文，但不是一摞现成的名片。'),
      ('In layers 57 to 61, removing the desk costs about 12% per layer; removing attention costs almost nothing.', '第 57 到 61 层，每层拿掉书桌，信号少大约 12%；拿掉注意力几乎没影响。'),
      ('So the desk writes the name.', '所以名字是书桌写出来的。')],
 16: [('Names come out piece by piece, and the first piece, the initial, gets the weakest push from the real title.', '名字是一段一段写的，最先的首字母恰恰得到真标题最弱的推力。'),
      ('Give the first initial in the prompt and recognised papers write the surname far more often.', '在提示里先给出首字母，认得出的论文写出姓的次数就多得多。')],
 17: [('Is the push simply too weak? We amplified the signal that had already arrived, by 1, 2 and 4 times.', '是不是推力不够？我们把已经到达的信号放大 1、2、4 倍。'),
      ('No setting helped, and the harder we pushed, the worse the true name ranked.', '没有一种推法有帮助，推得越用力，真名字的名次反而越差。')],
 18: [('Exploratory: its own hesitation while writing a name already tells real names from made-up ones.', '探索性：它写名字时的犹豫程度，就能分出真名和编造的名字。'),
      ('Middle-layer states add a little; made-up names are not confused neighbours.', '中间层的状态再多一点；编造的名字不是把邻近的人搞混了。')],
 12: [('Put the whole journey on one ruler: read early on the left, said late on the right.', '把整趟旅程放在一把尺子上：左边读得早，右边说得晚。'),
      ('The title is read by layers 50 to 52; the name is written only at 57 to 61.', '标题在第 50 到 52 层读完；名字要到第 57 到 61 层才写出来。')],
 53: [('This map puts the whole story in one picture: the prompt tokens across, the 64 layers up.', '这张图把整个故事放在一张图上：横着是提示词的每个 token，竖着是 64 层。'),
      ('The title is read from layer 24 and done by 52; it reaches the name slots in layers 40 to 50.', '标题从第 24 层开始读，到第 52 层读完；在第 40 到 50 层到达名字格。'),
      ('Which layer fixes the format is not pinned down; what is read is meaning, with one small surname exception from layer 8.', '哪一层定答案格式，目前定不下来；读到的是意思，有一个从第 8 层起的小姓氏例外。'),
      ('Read early, said late: the bottleneck is the late writing step, not reading.', '读得早，说得晚：瓶颈在后面写的那一步，不在读。')],
 19: [('Four questions, four short answers.', '四个问题，四个简短回答。'),
      ('The book is on the shelf; it is fetched by layer 50; it is not yet a word; and the first key is the weakest.', '书在架上；第 50 层就取到了；还不是词；最先那把钥匙最弱。')],
 20: [('What it means: “it doesn’t know” is often the wrong diagnosis.', '这意味着什么：“它不知道”常常是错误的诊断。'),
      ('The bottleneck is late, at writing; one model and one task are the main limits.', '瓶颈在后面写的那一步；一个模型、一种任务是主要局限。')],
 21: [('From here on is the appendix, in the order of the argument.', '从这里开始是附录，按论证的顺序排。')],
}
APPX_A = {
 22: ('Back-up for the puzzle: the line-up result and the two exposure thresholds.', '谜题的备份：选择题结果和两个曝光门槛。'),
 23: ('Back-up for “the book is on the shelf”: the split into knowing the paper and easy names.', '“书在架上”的备份：拆成“知道这篇论文”和“好猜的名字”。'),
 24: ('Back-up for the key: synonyms versus random words, by word class.', '钥匙的备份：近义词和随机词，按词类分开。'),
 25: ('Back-up for the forged key: how much a same-meaning made-up title recovers.', '仿造钥匙的备份：意思相同的编造标题能找回多少。'),
 26: ('Exploratory: at the title position the real-title extra is barely there; it forms later.', '探索性：在标题位置，真标题多出来的部分几乎还没有，后面才长出来。'),
 27: ('Back-up for “fetched early”: the full put-back curve by layer.', '“取得早”的备份：逐层的换货恢复曲线。'),
 28: ('Which shelf of the trolley carries the book: mainly the name slots.', '推车上哪一格装着书：主要是名字格。'),
 29: ('Exploratory: for more-cited papers the book is fetched a little later.', '探索性：引用多的论文，书取得稍晚一点。'),
 30: ('Back-up for “said late”: names become readable as words only in the last layers.', '“说得晚”的备份：名字要到最后几层才读得出是词。'),
 31: ('Back-up for the route: which part picks up the title and where it lands.', '路线的备份：哪个部件取标题，最后落在哪里。'),
 32: ('The corridors: closing one attention edge costs at most a few percent.', '走廊：关掉一条注意力边，最多损失几个百分点。'),
 33: ('The desk, floor by floor: what it passes on, and who writes.', '书桌逐层：它传下去什么，谁来写。'),
 34: ('Every measurement on one ruler.', '所有测量放在一把尺子上。'),
 35: ('Shelf map: where else the book shows up before layer 48.', '书架格子图：第 48 层以前书还出现在哪里。'),
 36: ('How the tests fit together: each speaks to one side.', '各个检验怎么拼在一起：每个只回答一边。'),
 37: ('Test: word-readers see punctuation in the middle; names only near the top.', '检验：读词工具在中间层看到的是标点，名字要到顶部才出现。'),
 38: ('Test: at the title a trained detector can read the paper’s year, citations and field.', '检验：在标题处，训练过的检测器能读出论文的年份、引用数和领域。'),
 39: ('Test: three questions, same title — no more alike than the words alone.', '检验：同一个标题换三个问题——并不比文字本身更相似。'),
 40: ('Test: at the colon the state is already organised by the question.', '检验：在冒号处，状态已经按问题组织好了。'),
 41: ('Test: a title state from a different question brings the authors back just as well.', '检验：用换了问题的标题状态替换，找回作者的效果一样好。'),
 42: ('Test: a reworded title stays close, but a meaning-only text model does that too.', '检验：改写后的标题仍然很接近，但只看意思的文本模型也能做到。'),
 43: ('Test: from the title state the first author is decoded at layer 8, the year only at 40.', '检验：从标题状态里，第一作者在第 8 层就解得出，年份要到第 40 层。'),
 44: ('Test: swapping only the “paper facts” directions moves almost nothing.', '检验：只换“论文属性”那几个方向，几乎什么也没动。'),
 45: ('Same-ruler check for H3: the detector sees more of the true surname than the word-reader.', 'H3 的同尺度检验：检测器比读词工具看到更多真姓氏。'),
 46: ('Layer by layer: the probe sees more than the word-readers until layer 56.', '逐层看：到第 56 层以前，探针都比读词工具看到更多。'),
 47: ('By name part: every part carries some paper-specific signal.', '按名字部分：每一部分都带一点论文特有的信号。'),
 48: ('Exploratory: recognised papers differ along many quiet directions, not the author axes.', '探索性：认得出的论文的差别落在很多安静的方向上，不在作者轴上。'),
 49: ('Why it can’t say it: the first step is the weak key, across all name parts.', '为什么说不出：第一步是那把弱钥匙，所有名字部分都是这样。'),
 50: ('Pushing harder: no gain in any of the 6 settings.', '用力推：6 种推法都没有收益。'),
 51: ('Back-up for Finding 5: hesitation tells real from made-up; middle layers add a little.', '发现 5 的备份：犹豫程度能分真假；中间层再多一点。'),
}
for k, v in APPX_A.items(): A[k] = [v]

# ---------------------------------------------------------------- new pages: title, A, B
NEW = {
 'Q2': ('Part 2 · question card（问题卡：认得出但说不出）',
        [('Part 2 asks one thing: does it not know the authors, or know them but cannot say them?', '第 2 部分只问一件事：它是不知道作者，还是知道但说不出？'),
         ('If it knows, it still picks the true list in a line-up for papers it cannot write.', '如果它知道，那些写不出的论文，它仍然能在一排名单里挑出真作者。'),
         ('If it does not know, those papers are not picked out either.', '如果它不知道，这些论文它也挑不出来。')],
        '对应 HTML v67 第 24、34 页；正文第 %d 页（谜题）、附录第 %d 页（曝光门槛）。本页不出现新数字。' % (P(2), P(22))),
 'V2': ('Part 2 · verdict card（判定卡：认得出但说不出）',
        [('Verdict: recognised but not said.', '结论：认得出，但说不出。'),
         ('For 4,110 of 6,296 papers with no author written, it still picks the true list.', '6,296 篇一个作者都写不出的论文里，有 4,110 篇仍能挑出真名单。'),
         ('Writing needs about 276 times the citations that recognising needs; only “more than one” is confirmed.', '写出来需要的引用数大约是认出来的 276 倍；锁定后只确认“大于 1 倍”。'),
         ('Next: what does the model read first — the question and the title?', '下一步：模型最先读的是什么——问题和标题。')],
        '4,110 / 6,296 篇（A 组 / R0 全部）；ρ = 276 [203, 390]，看过点估计后锁定，只确认 ρ > 1（补充登记 19）。证据强度：measured / locked · supported。未解决：按主题匹配的选择题干扰项可能会让一部分 target 论文改标。'),
 'Q1': ('Part 3 · question card（问题卡：H1 任务）',
        [('Part 3 asks: is the task, “write an author list”, what the middle layers mainly hold?', '第 3 部分问：中间层主要装的是不是任务——“写一个作者名单”？'),
         ('If yes, the colon state follows the question, and some middle layer fixes the answer format.', '如果是，冒号处的状态会跟着问题变，某个中间层会把答案格式定下来。'),
         ('If not, the colon follows the paper, and nothing fixes the format before the end.', '如果不是，冒号处跟着论文变，到最后都没有哪一层定下格式。')],
        '对应 HTML v67 第 38 页（问题卡）；检验：冒号与换问题（附录第 %d–%d 页），标题读得早（正文第 %d 页）。本页不出现新数字。' % (P(40), P(41), P(8))),
 'Q3a': ('Part 3a · question card（问题卡：标题什么时候被读）', [], '对应 HTML v68 第 39 页（3a 问题卡）；检验：换货与阻断（正文第 %d 页、附录第 %d 页）。本页不出现新数字。' % (P(8), P(27))),
 'Q3b': ('Part 3b · question card（问题卡：H1 格式什么时候定下来）', [], '对应 HTML v68 第 48 页（3b 问题卡）；检验：冒号与换问题（附录第 %d–%d 页）。本页不出现新数字。' % (P(40), P(41))),
 'V1': ('Part 3 · verdict card（判定卡：H1）',
        [('Verdict: the question is read at the colon, but the layer that fixes the format is not pinned down.', '结论：问题在冒号处被读到，但哪一层把格式定下来，目前定不下来。'),
         ('A new question moves the colon state far more than a new paper; the title is read by layers 50 to 52.', '换一个问题，冒号处的状态比换一篇论文动得多得多；标题在第 50 到 52 层读完。'),
         ('The locked format rule gave layer 56, but its test cuts the attention sink; with the sink kept, names hold from early on.', '锁定的格式规则给出第 56 层，可那个检验切断了 attention sink；保留 sink 时，名字从很早就保持住了。'),
         ('Swapping the colon state at layer 56 does lower the author signal; that part is measured.', '在第 56 层换掉冒号处的状态，确实会降低作者信号，这一点是测到的。'),
         ('Next: what exactly is read from the title?', '下一步：从标题里读到的到底是什么。')],
        '冒号：换问题比换论文多移动 2.2–4.7 倍（描述性）；标题到达：R 一半在 L45，L50–L52 完全到达（已定论）；格式锁定：锁定规则给出 L56，但主检验不单调、受切断 attention sink 影响（补充登记 23；补充实验为探索性：sink = position 0，保留 sink 时 names 类型从 L4 起保持，名字是默认答案类型）；L56 换“:”状态 Δspec −0.031 [−0.038, −0.024]（补充登记 26）。对应 HTML v67 第 49–51 页。未解决：年份/领域需要基线准确率足够的测量。'),
 'QH2': ('Part 4 · question card（问题卡：H2 论文身份）',
         [('Part 4 asks: does the title state hold which paper this is, or what the title means?', '第 4 部分问：标题状态里装的是“这是哪篇论文”，还是“标题是什么意思”？'),
          ('If it is the paper, a same-meaning made-up title should not open the book.', '如果是论文身份，意思相同的编造标题应该打不开这本书。'),
          ('If it is meaning, the forged key opens most of it, and the extra sits on specific words.', '如果是意思，仿造钥匙能打开大半，多出来的部分落在具体用词上。')],
         '对应 HTML v67 第 53 页（问题卡）；检验：钥匙（正文第 %d–%d 页）、仿造钥匙（第 %d 页）、唯一的锁定例外（第 %d 页）。本页不出现新数字。' % (P(5), P(6), P(7), P(52))),
 'VH2': ('Part 4 · verdict card（判定卡：H2）',
         [('Verdict: meaning, not paper identity, with one small locked exception.', '结论：是意思，不是论文身份，有一个小的锁定例外。'),
          ('A same-meaning made-up title opens three quarters; the real title adds a little, mostly on rare words.', '意思相同的编造标题能打开四分之三；真标题多给一点，主要落在罕见词上。'),
          ('The exception is a small surname signal from layer 8, beyond topic; the locked test is at layer 8, later layers are descriptive.', '例外是一个从第 8 层起、超出主题的小姓氏信号；锁定检验在第 8 层，后面的层只是描述性的。'),
          ('Two of its three tests only just pass, and about half of it is topic: a small effect, not strong evidence.', '三项检验里有两项刚过线，大约一半来自主题：是小效应，不是强证据。'),
          ('Next: where does the meaning go, and in what form is it held?', '下一步：意思送到哪里，以什么形式存着。')],
         'H2 判定（逐字）：Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal). φ 0.751 [0.723, 0.778]、R̄ +0.106 [0.094, 0.118]（补充登记 20）；罕见词 0.162 vs 常见词 0.027（补充登记 24，词数 3.4 vs 2.1、常见词按词频匹配不是同义词）；K4 不支持、K4c 反向（补充登记 22）；补充登记 33：T1 +0.046 [0.035, 0.056]，T2 +0.045 [0.008, 0.082]（Holm 下界 +0.002，BERT 正对照失败），T3 +0.025 [0.003, 0.047]；配对主题后按层 D：L8 +0.046（锁定），L16 0.056、L24 0.066、L32 0.076、L40 0.093（最高）、L48 0.027、L56 ≈ 0（描述性）；0.44 [0.36, 0.52] 在配对主题后保留；L0 ≈ 0。对应 HTML v67 第 78–80 页。'),
 'Q3': ('Part 5 · question card（问题卡：路线 + H3）',
        [('Part 5 asks how the title reaches the name, and whether the author is held there in a readable form.', '第 5 部分问：标题怎么送到名字那里，作者信息在那里是不是以输出读得出的形式存着。'),
         ('If the authors are there but not yet words, the scanner beats the label reader on the same ruler.', '如果作者信息在、但还不是词，在同一把尺子上扫描器会胜过读标签。'),
         ('If not, the two see the same, or one corridor carries everything.', '如果不是，两者看到的一样，或者只有一条走廊包办。')],
        '对应 HTML v67 第 81 页（问题卡）；检验：路线（正文第 %d 页；走廊：附录第 %d 页）、同一把尺子（第 %d 页）。本页不出现新数字。' % (P(10), P(32), P(15))),
 'V3': ('Part 5 · verdict card（判定卡：路线 + H3）',
        [('Verdict: a relay with many corridors carries the book to the name slots; the authors are there, but not yet as words.', '结论：多条走廊的接力把书送到名字格；作者信息在那里，但还不是词。'),
         ('By layer 52 the name slots carry the title’s signal; no single corridor or layer is a bottleneck.', '到第 52 层，名字格已经带着标题的信号；没有哪一条走廊或哪一层是瓶颈。'),
         ('On the same ruler the scanner sees more than the label reader, at layers 40 and 48.', '在同一把尺子上，扫描器在第 40、48 层比读标签看到更多。'),
         ('Pushing the scanner’s author direction mainly works as a write channel: another author’s direction writes that author too.', '沿扫描器的作者方向推，主要是写入通道：换成别的作者的方向，也会写出那个作者。'),
         ('Next: the book is there by layer 52, so why doesn’t the name come out?', '下一步：书在第 52 层就到了，为什么名字说不出来？')],
        '到达 R(L52) 0.995（已定论）；单层扫描：name ← title 在 L44/L48/L52/L54 有信息，每次切断 ≤ 1.25% 的 S（补充登记 32）；probe − lens 同尺度 L40 +0.021 [0.008, 0.034]、L48 +0.062 [0.041, 0.081]（补充登记 17）；注入：写对姓氏 2.5% → 9.7%，主要是写入通道，target 特有部分 +0.02–0.035（补充登记 25）。对应 HTML v67 第 100–104 页。未解决：书桌从名字格读了什么，需要因果检验。'),
 'QW': ('Part 6 · question card（问题卡：写名字这一步）',
        [('Part 6 asks: is the failure in reading the paper, or in writing the name?', '第 6 部分问：失败是在读论文，还是在写名字？'),
         ('If it is writing, the late desk writes the name, pushing harder does not help, and the first piece is hardest.', '如果是卡在写，后面的书桌写名字，用力推没用，最先那一块最难。'),
         ('If not, a stronger signal brings the name out, or going from authors to title is easier.', '如果不是，加强信号就能把名字推出来，或者从作者到标题更容易。')],
        '对应 HTML v67 第 105 页（问题卡）；检验：说得晚（正文第 %d 页）、书桌（第 %d 页）、最弱的第一把钥匙（第 %d 页）、用力推（第 %d 页）。本页不出现新数字。' % (P(9), P(11), P(16), P(17))),
 'VW': ('Part 6 · verdict card（判定卡：写名字这一步）',
        [('Verdict: stuck at writing — the late desk writes the name, and the first piece is the hardest.', '结论：卡在写这一步——后面的书桌写名字，最先那一块最难。'),
         ('In layers 57 to 61 the MLPs, not attention, write the name.', '第 57 到 61 层，是 MLP 而不是注意力在写名字。'),
         ('Pushing harder gives no gain; giving the first initial raises correct writing from 4.0% to 15.2%.', '用力推没有收益；给出首字母，写对的比例从 4.0% 升到 15.2%。'),
         ('Going from authors to title is slightly harder, not easier, so this is not a reversal curse.', '从作者到标题反而稍难，不是更容易，所以这不是反转诅咒。'),
         ('Next: put it all together — read early, said late.', '下一步：把它们放在一起——读得早，说得晚。')],
        'L57–L61 MLP − attention +0.040 [0.036, 0.045]（已定论）；用力推 6 种设置均无收益，损害取决于方向（补充登记 21、27）；首字母 4.0% → 15.2%（补充登记 16 B，F4）；方向不对称（补充登记 30）：R1 +0.443 [0.373, 0.517]，R2 −0.032 [−0.047, −0.016]，锁定判定“反向”（生成标题稍难），反转诅咒解释不成立；后期压制约 1/8 论文先升后降（12.8% vs 9.1%，T−C +0.037 [0.002, 0.073]，补充登记 31）。对应 HTML v67 第 106–122 页。'),
 'LED': ('Part 7 · evidence ledger（证据账本）',
         [('Here is the evidence behind each of the seven steps, in one table.', '这里把七步背后的证据放在一张表里。'),
          ('The early steps are settled; meaning not identity and the hidden authors are locked; the format layer is downgraded.', '前面几步已经定论；意思不是身份、作者藏着这两步是锁定的；格式层那一步降级了。'),
          ('Ruled out: a general paper identity, a stronger signal fixing recall, a reversal curse, and literal word overlap.', '排除了：一般意义上的论文身份、加强信号就能回忆、反转诅咒，以及字面重叠。')],
         '本页不出现新数字；每一行的数字都在所列页码上。对应 HTML v67 第 131 页（证据账本）、第 132 页（排除了什么）。'),
 'SET': ('Part 7 · settled vs pending（已定 vs 待定）',
         [('On the left, what is settled or locked; on the right, what is still open.', '左边是已定或锁定的，右边是还没定的。'),
          ('Open: the format layer, a stronger baseline for the surname exception, a second model, a held-out replication, a causal test of writing.', '还没定的：格式层、姓氏例外需要更强的基线、第二个模型、留出样本复现、写名字的因果检验。'),
          ('In one sentence: read early, said late — the bottleneck is the late writing step, not reading.', '一句话：读得早，说得晚——瓶颈在后面写的那一步，不在读。')],
         '本页不出现新数字。对应 HTML v67 第 134 页（未解决的问题和下一步）。'),
}

# ---- user-approved style (2026-11-23): replace all A blocks from leader_A17n.py (one metaphor, reading line first)
import importlib.util, sys as _sys
_spec = importlib.util.spec_from_file_location('leader_A17n', '/home/zhang.zhiqi2/jlens_work/27_v67/leader_A17n.py')
_LA = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_LA)
A = _LA.A
for _k, (_ttl, _al) in _LA.NEW.items():
    NEW[_k] = (_ttl, _al, NEW[_k][2])
assert set(A) >= set(range(1, 54)) - set(), sorted(set(range(1, 54)) - set(A))


VERDICT_LABEL = {7: '**当时那项检验（编造标题检验）的锁定判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 @@VHTWO@@ 页）',
                 14: '**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 @@VHTWO@@ 页）',
                 19: '**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 @@VHTWO@@ 页）',
                 36: '**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 @@VHTWO@@ 页）'}


def strip_update_block(body):
    """remove the leftover '2026-11-23 更新 · 要说的话' blocks (their content now lives in the main A block)"""
    out_, skip = [], False
    for ln in body.split('\n'):
        if ln.startswith('**2026-11-23 更新 · 要说的话'): skip = True; continue
        if skip:
            if ln.strip() == '' or ln.startswith('**'):
                if ln.startswith('**'): skip = False; out_.append(ln)
                continue
            if '【' in ln: out_.append(ln)
            continue
        out_.append(ln)
    return '\n'.join(out_)


def strip_old_A(body):
    """drop the old spoken pairs (keep every 【】 line and everything from the next ** header on)"""
    if '**要说的话' not in body: return body
    out_, skip = [], False
    for ln in body.split('\n'):
        if ln.startswith('**要说的话'): skip = True; continue
        if skip and ln.startswith('**'): skip = False
        if skip and '【' not in ln: continue
        out_.append(ln)
    return '\n'.join(out_)


PART_OF = {}
cur = None
PARTNAME = {1: 'Part 0 · Opening', 'Q2': 'Part 2 · Recognised but not said', 13: 'Part 3 · Read early (H1)', 'Q3a': 'Part 3a · When is the title read?', 'Q3b': 'Part 3b · H1: when is the answer format fixed?', 'QH2': 'Part 4 · Meaning, not identity (H2)',
            'Q3': 'Part 5 · Route + H3', 'QW': 'Part 6 · Said late, stuck at writing', 12: 'Part 7 · Summary', 21: 'Appendix'}


_PM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json'))['v68_to_v22t_first']


def pptx_str(k):
    h = H67.get(k) if isinstance(k, int) else H67_NEW.get(k)
    if h and str(h) in _PM: return 'main pptx S%s (v22t)' % _PM[str(h)]
    return 'main pptx —'



out = [head.strip('\n').replace('当前：jlens_leader_v17m.pptx，53 页。', '当前：jlens_leader_v17n.pptx，67 页。')
       .replace('结构说明：正文是 P1–P20，P21 是附录分隔页，附录是 P22–P53；每页标题写 leader 页码和主 PPT（v22s）对应页码，没有一一对应的写 “—”。',
                '结构说明（v17n）：正文 P1–P36 按 HTML v68 的 Part 排列——Part 0 开场；Part 2–6 每部分以问题卡开头、关键页居中、判定卡和过渡结尾，Part 3 分 3a（标题什么时候被读）和 3b（H1：格式什么时候定下来）；Part 7 总结（机制图、证据账本、已定 vs 待定，再接原总结页）。P37 是附录分隔页，附录 P38–P67。每页标题写 leader 页码、HTML v68/v69 页码（两版页码相同）和主 PPT v22t 页码。每页分 A（要说的话，一句英文一句中文）和 B（备查，不念）。'), '']
out.append('## 论证链概览\n')
out.append('This deck walks the argument in parts: the puzzle, then what is read early, what is read, where it goes, and where it gets stuck.\n'
           '这份 deck 按部分讲论证：先是谜题，然后是读得早的是什么、读到的是什么、送到哪里、卡在哪里。\n\n'
           '**备查（不念）：** 上一版的概览原文：' + overview.replace('\n', ' ') + '\n')
for k in ORDER:
    n = P(k)
    if k in PARTNAME: out.append('# %s\n' % PARTNAME[k])
    if isinstance(k, int):
        title, body = pages[k]
        h67 = H67.get(k)
        hstr = ('HTML v68 p%d' % h67) if h67 else 'HTML —'
        out.append('## P%d · leader p%d · %s · %s — %s\n' % (n, n, hstr, pptx_str(k), title))
        body = strip_update_block(strip_old_A(body))
        if k in VERDICT_LABEL: body = VERDICT_LABEL[k] + '\n\n' + body
        al = A[k]
        out.append('**要说的话（一句英文一句中文）**')
        for en, zh in al: out.append(en); out.append(zh)
        out.append('')
        out.append('**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。\n')
        out.append(body + '\n')
    else:
        title, al, b = NEW[k]
        out.append('## P%d · leader p%d · HTML v68 p%d · %s — %s\n' % (n, n, H67_NEW[k], pptx_str(k), title))
        out.append('**要说的话（一句英文一句中文）**')
        for en, zh in al: out.append(en); out.append(zh)
        out.append('')
        out.append('**备查（不念）：** ' + b + '\n')
txt = '\n'.join(out)
def _m68(s_):
    out_ = []
    for part in re.split(r'([、–])', s_):
        out_.append(str(_M68.get(int(part), int(part))) if part.isdigit() else part)
    return ''.join(out_)
txt = re.sub(r'HTML v67 第 ([\d、–]+) 页', lambda m: 'HTML v67 第 ' + _m68(m.group(1)) + ' 页', txt)
txt = re.sub(r'(?<=\*\*备查（不念）：\*\* )(.*)', lambda m: m.group(1).replace('HTML v67 第', 'HTML deck 第').replace('HTML v68 第', 'HTML deck 第'), txt)


# page references inside kept old text: P-numbers and 'p. N' / '第 N 页' refer to v17m numbering -> v17n
def fmt(a, b=None):
    if b is None: return str(P(a))
    seq = [P(x) for x in range(a, b + 1)]
    if seq == list(range(seq[0], seq[0] + len(seq))): return '%d–%d' % (seq[0], seq[-1])
    return ', '.join(map(str, seq))


def remap_body(s):
    lines = s.split('\n')
    res = []
    for ln in lines:
        if ln.startswith('## P') or ln.startswith('# ') or '【' in ln:
            res.append(ln); continue
        if '以下是上一版的本页原文' in ln or ln.startswith('**备查（不念）：** 上一版的概览原文') or ln.startswith('**备查（不念）：** 对应') or '本页不出现新数字' in ln:
            pass
        ln = re.sub(r'(?<![\w.])(pp?\.\s*)(\d+)(?:–(\d+))?', lambda m: m.group(1) + (fmt(int(m.group(2)), int(m.group(3)) if m.group(3) else None) if 1 <= int(m.group(2)) <= 53 else m.group(0)[len(m.group(1)):]), ln) if '上一版的本页原文' not in ln else ln
        ln = re.sub(r'第 (\d+)(?:–(\d+))? 页', lambda m: '第 ' + (fmt(int(m.group(1)), int(m.group(2)) if m.group(2) else None) if 1 <= int(m.group(1)) <= 53 else m.group(1)) + ' 页', ln)
        ln = re.sub(r'(?<![\w])P(\d+)(?:–P?(\d+))?(?![\d])', lambda m: 'P' + (fmt(int(m.group(1)), int(m.group(2)) if m.group(2) else None) if 1 <= int(m.group(1)) <= 53 else m.group(1)), ln)
        res.append(ln)
    return '\n'.join(res)


# remap only inside the kept v17m text (B blocks of old pages); new-page text already uses v17n numbers
blocks = re.split(r'(?m)^(## P\d+ · .*)$', txt)
for i in range(1, len(blocks) - 1, 2):
    m = re.search(r'以下是上一版的本页原文（页码已改为新编号）。\n', blocks[i + 1]) or re.search(r'@@REMAP@@\n', blocks[i + 1])
    if m:
        pre, post = blocks[i + 1][:m.end()], blocks[i + 1][m.end():]
        blocks[i + 1] = pre + remap_body(post)
txt = ''.join(blocks).replace('@@REMAP@@\n', '').replace('@@VHTWO@@', str(P('VH2')))
# ---- one metaphor (user 2026-11-23): no key / forged key / open-the-book wording outside 【】 notes
KEYMAP = [('一把意思相同的仿造钥匙能打开四分之三', '一张写着同样主题、但不属于这本书的卡片（编造标题）能走到四分之三'),
          ('最先要转的那把钥匙恰恰最磨损', '最先要写的那一块恰恰最弱'), ('如果只是缺知识，备用钥匙不会有用', '如果只是缺知识，额外的提示不会有用'),
          ('另一把备用钥匙是', '另一种提示是'), ('首字母这把弱钥匙', '首字母这一块'), ('最先要转的首字母那把钥匙最弱', '最先要写的首字母那一块最弱'),
          ('最弱的第一把钥匙', '最弱的第一块（首字母）'), ('第一把钥匙最弱', '第一块（首字母）最弱'),
          ('一把仿造的钥匙', '一张同主题的卡片'), ('仿造钥匙应该和真钥匙一样把锁全打开', '同主题的卡片应该和真标题一样走到底'),
          ('真钥匙打开', '真标题给出'), ('仿造的钥匙', '同主题的卡片'), ('仿造钥匙', '同主题的卡片'), ('真钥匙', '真标题'),
          ('钥匙上哪几个齿最要紧', '标题里哪些词最要紧'), ('钥匙打开了书', '找到了书'), ('有意义的词是钥匙', '有意义的词起作用'),
          ('钥匙还大致能转', '还大致能找到'), ('完全转不动', '完全找不到'), ('钥匙是有意义的词', '起作用的是有意义的词'),
          ('钥匙靠的是', '起作用的是'), ('既然钥匙是"意思"', '既然起作用的是"意思"'), ('如果钥匙靠的是', '如果起作用的是'),
          ('下面一把钥匙，橙色齿', '下面一张标题卡片，橙色部分'), ('标题是钥匙', '标题像书脊上的主题'), ('论文标题是"钥匙"', '论文标题像书脊上写的"主题"'),
          ('含钥匙 18b-5、同主题的卡片 补充 20', '含按词类 18b-5、同主题的卡片 补充 20'), ('检验：钥匙（', '检验：按词替换（'),
          ('真标题能打开这本书', '真标题能找到这本书'), ('打开 3/4', '走到 3/4'), ('能打开多少', '能走到多少'), ('一样打不开', '一样找不到'), ('同主题的卡片打开 +0.32', '同主题的卡片给出 +0.32'), ('打开 +', '给出 +'), ('那一把意思相同的同主题的卡片', '那一张写着同样主题的卡片'), ('一把意思相同的同主题的卡片', '一张写着同样主题的卡片'), ('钥匙', '标题')]
lines_ = txt.split('\n')
for i_, ln in enumerate(lines_):
    if '【' in ln: continue
    for a_, b_ in KEYMAP:
        ln = ln.replace(a_, b_)
    if ln.startswith('## P'):
        ln = (ln.replace('Finding 1 （', 'Finding 1（').replace('Finding 1b · the key（发现 1b：标题）', 'Finding 1b · meaning, not spelling（发现 1b：意思，不是写法）')
                .replace('Finding 1c · the forged key（发现 1c：同主题的卡片）', 'Finding 1c · the same-topic card（发现 1c：同主题的卡片）')
                .replace('Appendix · the key (18b item 5)（标题：按词类）', 'Appendix · by word class（按词类替换）')
                .replace('Appendix · the forged key (add. 20)（同主题的卡片：细节）', 'Appendix · the made-up title, details（同主题的卡片：细节）'))
    lines_[i_] = ln
txt = '\n'.join(lines_)
# ---- 【】 audit (2026-11-23): notes confirmed as OUR maintenance notes move to the changelog verbatim
OURS = ('【v17i】', '【2026-11-22 v17l · H2 新措辞（状态仍为 partly supported）】', '【2026-11-22 v17l】')
moved_notes, keep, cur_ = [], [], None
for ln in txt.split('\n'):
    mm = re.match(r'## (P\d+) ', ln)
    if mm: cur_ = mm.group(1)
    if any(ln.lstrip('*').startswith(o) for o in OURS):
        moved_notes.append((cur_, ln)); continue
    keep.append(ln)
txt = re.sub(r'\n{3,}', '\n\n', '\n'.join(keep))
json.dump(moved_notes, open('/home/zhang.zhiqi2/jlens_work/27_v67/leader_notes_moved.json', 'w'), ensure_ascii=False, indent=0)
open(OUT, 'w', encoding='utf-8').write(txt)
print('wrote', OUT, len(txt.splitlines()), 'lines')
