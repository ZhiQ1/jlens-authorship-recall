"""2026-11-25: main script v65 (HTML v71 / pptx v22v order) -> v66 (HTML v72 / pptx v22w order).
- 25 new pages for the story-figure slides (HTML v72 133-157 = pptx v22w S141-S165), inserted at the start of Part 7:
  A block (spoken, one EN line then one ZH line; step slides walk the lit stage and end on the bottom conclusion),
  B block (备查: slide text + the matching passage of the final experiment tree, 27_v67/experiment_tree.md, old page numbers removed);
- headings 'P{n} · HTML v72 p{n} · pptx S{k} (v22w)'; 'slide N' / '第 N 页' (v71 -> v72) and 'pptx S N' (v22v -> v22w)
  renumbered in the spoken A blocks only, OUTSIDE 【】; 【】 untouched and kept on their page; 备查 archives keep their own numbering.
usage: build_script_v66.py"""
import re, json
H = '/home/zhang.zhiqi2/jlens_work/'
SRC = H + 'script_stage1_13_v65.md'; OUT = H + 'script_stage1_13_v66.md'
RM = json.load(open(H + '27_v67/renumber_map_v72.json')); V = {int(a): b for a, b in RM['v71_to_v72'].items()}
PM = json.load(open(H + '27_v67/pptx_map_v22w_v72.json'))
PALL = {int(a): b for a, b in PM['v72_to_v22w_all'].items()}
V2W = {int(a): b for a, b in PM['v22v_to_v22w'].items()}
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
def v71(n): return V.get(n, n)
REF_EN = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
REF_ZH = re.compile(r'(第 ?)(\d{1,3})((?:[、，,–-] ?\d{1,3})*)( ?页)')
def renum(s):
    s = REF_EN.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(v71(int(x.group(0)))), m.group(2)), s)
    s = REF_ZH.sub(lambda m: m.group(1) + str(v71(int(m.group(2)))) + re.sub(r'\d+', lambda x: str(v71(int(x.group(0)))), m.group(3)) + m.group(4), s)
    s = re.sub(r'(\bpptx S)(\d{1,3})\b', lambda m: m.group(1) + str(V2W.get(int(m.group(2)), int(m.group(2)))), s)
    s = re.sub(r'(主 pptx 当前页码：S)(\d{1,3})', lambda m: m.group(1) + str(V2W.get(int(m.group(2)), int(m.group(2)))), s)
    return s
def renum_a(rest):
    i = rest.find('\n**备查')
    if i < 0: return outside(rest, renum)
    return outside(rest[:i], renum) + rest[i:]
pages = {}; extras = {}; last = None; nnotes_old = {}
for sg in segs:
    head, _, rest = sg.partition('\n')
    if head.startswith('# '): continue
    m = re.match(r'## P(\d+) · HTML v71 p\d+ · pptx S[\dS–-]+ \(v22v\) — (.*)$', head)
    if m:
        n = int(m.group(1)); p = V[n]; title = outside(m.group(2), renum)
        pages[p] = '## P%d · HTML v72 p%d · pptx %s (v22w) — %s\n' % (p, p, pp(p), title) + renum_a(rest)
        nnotes_old[p] = NOTE.findall(sg); last = p; continue
    m = re.match(r'## pptx S(\d+)（仅主 pptx，HTML deck 无对应页）— (.*)$', head)
    if m:
        k = V2W[int(m.group(1))]
        extras.setdefault(last, []).append('## pptx S%d（仅主 pptx，HTML deck 无对应页）— %s\n' % (k, m.group(2)) + renum_a(rest)); continue
    raise SystemExit('unexpected heading: ' + head)

# ---------------- final experiment tree passages (Chinese part) ----------------
tree = open(H + '27_v67/experiment_tree.md', encoding='utf-8').read()
zh = tree[:tree.index('\n## English version')]
def strip_pages(s):
    s = re.sub(r' · 第 [0-9、–,， ]+页(?:第 ?\d+ ?项)?', '', s)
    s = re.sub(r'（第 [0-9、–,， ]+页）', '', s)
    s = re.sub(r'第 [0-9、–,， ]+页', '（页码见 v72 目录）', s)
    return s.strip()
def block(start, stop_re=r'\n\*\*'):
    i = zh.index(start); j = re.search(stop_re, zh[i + len(start):]); j = i + len(start) + (j.start() if j else len(zh))
    return strip_pages(zh[i:j])
BAND = {b: block('**%s：' % b) for b in ['L0–L4', 'L4–L24', 'L24–L40', 'L40–L52', 'L48–L56', 'L56–L63']}
STEPMAP = {k: block('**第 %s 步' % c) for k, c in zip(range(1, 8), '①②③④⑤⑥⑦')}
GAPS = block('**两个已知缺口**', r'\n---')
WHOLE = strip_pages(zh[zh.index('### 总的拼图') + len('### 总的拼图'):zh.index('### 故事拼图')].strip().rstrip('-').strip())
SRCNOTE = '**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：'

NEWS = json.load(open(H + '32_v72/new_slides_v72.json'))
A = {}
A[133] = [
 ("This page opens the summary with the whole story on one map: the prompt tokens run across, the 64 layers run up.", "这一页用一张图打开总结：横着是提示词的每个 token，竖着是 64 层。"),
 ("Follow the blue pipes from the bottom: the input words set the states up to layer 4, the title is read from layer 24, and by layer 52 it has been delivered to the name positions.", "从下往上跟着蓝色管道走：到第 4 层为止，状态由输入的字决定；从第 24 层起读标题；到第 52 层，标题已经送到名字位置。"),
 ("Then the paper information waits at the names as something a probe can read but a lens cannot, and only at layers 57 to 61 do the late MLPs write the name.", "然后论文信息停在名字位置，probe 读得出、lens 读不出；直到第 57 到 61 层，后面的 MLP 才把名字写出来。"),
 ("The padlock marks where it gets stuck: at writing, hardest at the first token of the name.", "挂锁标出卡住的地方：在写出这一步，名字的第一个 token 最难。"),
 ("Read early, said late: the title is read and delivered by about layer 52, the name is written only at layers 57 to 61, and recall stalls there.", "读得早，说得晚：标题大约在第 52 层读完、送到；名字到第 57 到 61 层才写，回忆就卡在那里。"),
 ("Next, the same map six times, one stage lit at a time.", "接下来把同一张图看六遍，每次只点亮一段。")]
A[134] = [
 ("Step one lights only the bottom band, layers 0 to 4; everything else is faded.", "第一步只点亮最底下一段，第 0 到 4 层，其余都淡掉。"),
 ("Here the model has done almost no computing yet, so the state is set by the input words themselves.", "这里模型几乎还没做计算，所以状态由输入的字本身决定。"),
 ("The same title under two different questions already gives almost the same state at layer 4; even the bare word embedding, or a BERT model that knows no papers, finds the paper again every time.", "同一个标题放在两个不同问题下，第 4 层的状态已经几乎一样；就连不经过模型的词嵌入、或者完全不认识论文的 BERT，也每次都能把论文找回来。"),
 ("So at this level we cannot tell meaning from paper identity, and layer 4 becomes the literal baseline that every later test is measured above.", "所以在这一层分不开意思和论文身份，第 4 层就成了字面基线，后面每项检验都在它之上比较。"),
 ("The bar at the bottom says it: the input words decide almost everything.", "底下那条结论就是：输入的字决定了几乎一切。"),
 ("Next, layers 4 to 24.", "下一步：第 4 到 24 层。")]
A[135] = [
 ("Step two lights layers 4 to 24, the early read-in.", "第二步点亮第 4 到 24 层，也就是早期读入。"),
 ("At the colon, the state follows the question, not the paper: it moves about 4.7 times more when the question changes than when the paper changes.", "在冒号位置，状态跟着问题走，不跟着论文走：换问题时移动的距离大约是换论文时的 4.7 倍。"),
 ("At the title, the first title facts and the first author's token appear around layers 8 to 16, and a paraphrased title starts to be encoded beyond its wording from layer 8.", "在标题位置，最早的标题信息和第一作者的 token 大约在第 8 到 16 层出现；改写过的标题从第 8 层起开始在字面之上被编码。"),
 ("The one small reverse clue is a surname signal at layer 8: it survives a confirmatory test on about six thousand new papers, but it is small and about half of it is topic.", "唯一的反向线索是第 8 层的姓氏信号：它在大约六千篇新论文的确认检验里站住了，但很小，而且大约一半来自主题。"),
 ("Bottom line: early read-in, the first traces of the title and of the first author, a joint conclusion from several tests.", "底下的结论：早期读入，出现最早的标题痕迹和第一作者痕迹，这是几项检验合起来得出的。"),
 ("Next, layers 24 to 40.", "下一步：第 24 到 40 层。")]
A[136] = [
 ("Step three lights layers 24 to 40, the main title-reading phase.", "第三步点亮第 24 到 40 层，这是读标题的主要阶段。"),
 ("The put-back test shows the title being read here; the question is what is read.", "放回实验显示标题就在这里被读；问题是读走的是什么。"),
 ("A made-up title with the same meaning brings back about 75 percent of the true title's advantage.", "一个意思相同的编造标题，能找回真标题优势的大约 75%。"),
 ("The small extra of the real title sits on rare, specific words, is not larger for recognised papers, and is even smaller for highly cited ones.", "真标题多出的那一小块挂在稀有、具体的词上，在认得的论文上并不更大，引用多的论文反而更小。"),
 ("So the bar is red: what is read is meaning and specific words, not paper identity; this overturns the general form of hypothesis two.", "所以这条是红色的：读走的是意思和具体用词，不是论文身份；这推翻了 H2 的一般形式。"),
 ("Next, layers 40 to 52.", "下一步：第 40 到 52 层。")]
A[137] = [
 ("Step four lights layers 40 to 52, where the title reaches the name positions.", "第四步点亮第 40 到 52 层，标题在这里送到名字位置。"),
 ("Putting the true-title states back restores 0.82 of the advantage at layer 48 and almost all of it at 52; taking them away from 52 on costs almost nothing.", "把真标题的状态放回去，第 48 层恢复 0.82，第 52 层几乎全部恢复；从第 52 层起拿走，几乎没有损失。"),
 ("The two opposite tests agree, and the timing is the same for all five false titles.", "两个方向相反的检验结论一致，五个假标题下时间也一样。"),
 ("The names-from-title edge carries the delivery, but cutting any single layer loses at most 1.25 percent: several layers work in parallel.", "名字看标题这条边承担输送，但切掉任何一层最多只损失 1.25%：是多层并行。"),
 ("Bottom line: the information reaches the name positions over several layers in parallel, and the title is read by layer 52.", "底下的结论：信息经过多层并行送到名字位置，标题到第 52 层读完。"),
 ("Next, layers 48 to 56.", "下一步：第 48 到 56 层。")]
A[138] = [
 ("Step five lights layers 48 to 56: in what form is the information held at the names?", "第五步点亮第 48 到 56 层：信息在名字位置是以什么形式存着的？"),
 ("A lens fitted on author prompts reads nothing here, but a probe can; on the same scale, the probe reads 0.06 more at layer 48.", "用作者提示拟合的 lens 在这里读不出来，probe 却能读出；放在同一把尺子上，第 48 层 probe 多读出 0.06。"),
 ("The information is spread out: the author subspace carries only about 7 percent, and there is no single direction and no earlier shelf.", "信息是分散的：作者子空间只带过去约 7%，没有单一方向，也没有更早的架子。"),
 ("And the MLPs at layers 52 to 56 carry paper information, not ready-made name directions.", "第 52 到 56 层的 MLP 带的是论文信息，不是现成的名字方向。"),
 ("Bottom line, in dark blue because each part rests on one experiment: the probe reads it, the lens does not; what arrives is paper information, not ready-made names.", "底下的结论是深蓝色，因为每一部分各靠一个实验：probe 读得出，lens 读不出；送到的是论文信息，不是现成的名字。"),
 ("Next, the last layers.", "下一步：最后几层。")]
A[139] = [
 ("Step six lights the top, layers 56 to 63, where the name is written.", "第六步点亮最上面的第 56 到 63 层，名字在这里写出。"),
 ("Removing the MLPs at layers 57 to 61 costs more than removing attention at every layer, so the late MLPs write the name.", "在第 57 到 61 层，去掉 MLP 的代价每一层都比去掉注意力大，所以是后面的 MLP 写出名字。"),
 ("The gap between recognised and other papers grows here, to 0.21 at the output.", "认得和认不得的论文之间的差距在这里长大，到输出端是 0.21。"),
 ("Pushing the arrived signal harder barely helps, 2.5 to 2.8 percent, and the harm comes from direction, not amount; giving the first initial helps much more.", "把已到达的信号推得更强几乎没用，只从 2.5% 到 2.8%，而且伤害来自方向，不来自强度；给出名首字母则帮助大得多。"),
 ("Bottom line: the late MLPs write the name; the gap grows here, and it gets stuck at writing.", "底下的结论：后面的 MLP 写出名字；差距在这里长大，卡在写出这一步。"),
 ("Next, each stage in detail, experiment by experiment.", "接下来逐段展开，一个实验一个实验地看。")]
A[140] = [
 ("Now each stage in detail: the main line runs down the middle, what was rewritten or ruled out is on the left, exceptions and dependencies on the right.", "现在逐段展开：主线在中间往下走，左边是被改写或排除的，右边是例外和依赖。"),
 ("Stage one starts from two tests: a new question about the same paper, and the same title under another question; both look the same at layer 4.", "第一段从两个检验开始：同一篇论文换一个新问题，以及同一个标题放到另一个问题下；两者在第 4 层看起来都一样。"),
 ("So where does that ceiling come from? Three checks answer it: the last token is identical at layer 0, the word embedding alone already identifies the title at 0.998, and BERT, which knows no papers, retrieves it every time.", "那这个天花板是从哪来的？三项检查回答了：最后一个 token 在第 0 层完全相同，单靠词嵌入就能以 0.998 认出标题，不认识任何论文的 BERT 也每次都能找回。"),
 ("These are exploratory checks, but they point the same way: the ceiling comes from identical input words.", "这些是探索性的检查，但方向一致：天花板来自一模一样的输入字。"),
 ("Next, what that means for the rest of the story.", "下一页看这对后面的故事意味着什么。")]
A[141] = [
 ("Part two of stage one: the ceiling comes from identical input words, not from knowing the paper.", "第一段第二部分：天花板来自一模一样的输入字，不是因为认识这篇论文。"),
 ("On the left, the early reading that an unchanged state across questions supports paper identity is withdrawn by the ceiling audit.", "左边，早期的读法“换问题状态不变，所以支持论文身份”被天花板审计撤回。"),
 ("The stage conclusion: at layers 0 to 4 the input words set the states, and layer 4 is the literal baseline for every test that asks for something beyond the words.", "这一段的结论：第 0 到 4 层由输入的字决定状态，第 4 层是所有“超出字面”检验的字面基线。"),
 ("On the right, it hands on to layers 4 to 40, where paraphrase closeness is measured above its layer-4 level.", "右边，它交给第 4 到 40 层：改写标题的接近程度都是在第 4 层水平之上来衡量的。"),
 ("So: the input words decide almost everything here, and meaning cannot be separated from identity. Next, stage two.", "所以：这里输入的字决定了几乎一切，意思和身份分不开。下一页是第二段。")]
A[142] = [
 ("Stage two, layers 4 to 24, part one.", "第二段，第 4 到 24 层，第一部分。"),
 ("The colon first: a probe trained at the colon keeps only 0.24 to 0.41 under a new question, and 62 to 92 percent of the colon's attention goes to position 0, so the colon carries the question.", "先看冒号：在冒号位置训练的 probe，换一个问题只剩 0.24 到 0.41；冒号 62% 到 92% 的注意力落在第 0 个位置，所以冒号携带的是问题。"),
 ("Then the title: layer order puts title facts and the first author's token first, at layers 8 to 16; paper attributes become readable at the title from about layer 16, though they can be inferred from the title text.", "再看标题：层顺序显示，标题信息和第一作者的 token 最早出现，在第 8 到 16 层；论文属性大约从第 16 层起能在标题位置读出，不过这些属性能从标题文字推出来。"),
 ("And a paraphrased title stays closer to the original than its layer-4 level from layer 8 on.", "改写过的标题从第 8 层起，和原标题的接近程度超过了第 4 层的水平。"),
 ("Next, the one small reverse clue.", "下一页看那条唯一的反向小线索。")]
A[143] = [
 ("Part two of stage two: early read-in starts here.", "第二段第二部分：早期读入从这里开始。"),
 ("The surname test moves the layer-8 title state into a fixed question about the first author and decodes the surname; on 6,048 new papers it is +0.046 after removing topic-matched papers.", "姓氏检验把第 8 层的标题状态放进一个固定的“第一作者是谁”的问句，解码出姓；在 6,048 篇新论文上，扣掉同主题配对后是 +0.046。"),
 ("On the left, literal overlap is ruled out by the source check, and a topic-matched test that was too small is rescued by the confirmatory test.", "左边，来源检查排除了字面重叠；样本太小的主题配对检验由确认检验补上。"),
 ("On the right, whether this is identity cannot be decided: the text-only baseline fails its own positive control, and the signal is back near zero by layer 56.", "右边，这是否算身份还定不下来：纯文本基线没通过它自己的正对照，而且信号到第 56 层回到接近零。"),
 ("The title probe also separates recognised from other papers a little at layer 24.", "标题位置的 probe 在第 24 层也能稍微分开认得和认不得的论文。"),
 ("Stage conclusion: layers 4 to 24 are read-in only; meaning beyond the words starts at layer 8, with one small locked surname exception. Next, stage three.", "这一段的结论：第 4 到 24 层只是读入；超出字面的意思从第 8 层开始，有一个锁定的小姓氏例外。下一页是第三段。")]
A[144] = [
 ("Stage three, layers 24 to 40: what is read when the title is read?", "第三段，第 24 到 40 层：读标题的时候，读走的是什么？"),
 ("First, which title words carry the signal: swapping content words for random words wipes it out, while synonyms lose only a little, so it is carried by meaning.", "先看哪些标题词带着信号：把内容词换成随机词，信号就没了；换成同义词只掉一点，所以信号靠意思承载。"),
 ("A paraphrased title, the same meaning in other words, is encoded beyond the literal level, peaking at layer 36.", "改写过的标题，意思相同、用词不同，在字面水平之上被编码，在第 36 层达到峰值。"),
 ("Then the key test: a made-up title with the same meaning brings back 0.75 of the true title's advantage, and the real title adds a small extra, 0.11.", "然后是关键检验：一个意思相同的编造标题能找回真标题优势的 0.75，真标题再多出一小块，0.11。"),
 ("So the open question is: what is that small extra part? Next page.", "所以剩下的问题是：那一小块是什么？看下一页。")]
A[145] = [
 ("Part two of stage three: what is the small extra?", "第三段第二部分：那一小块是什么？"),
 ("Four locked tests together: it sits on rare words, not common ones; it is not larger for recognised papers and smaller for highly cited ones; a variance split finds identity adds about zero; and the paper-facts subspace carries no extra author information.", "四项锁定检验合起来看：它挂在稀有词上，不在常见词上；在认得的论文上不更大，引用多的反而更小；方差分解显示身份几乎不增加解释力；论文信息子空间也不带额外的作者信息。"),
 ("So the real title's small extra comes from specific words, not from recognising the paper.", "所以真标题多出的那一小块来自具体用词，不是来自认出这篇论文。"),
 ("On the left, the claim that the middle layers store which paper this is gets crossed out: it is not a general paper identity, with one small locked exception, the layer-8 surname signal.", "左边，“中间层存着这是哪篇论文”被划掉：不是一般意义上的论文身份，只有一个锁定的小例外，就是第 8 层的姓氏信号。"),
 ("Stage conclusion, in red: what is read in layers 24 to 40 is meaning and specific words, not paper identity; this overturns the general form of hypothesis two. Next, stage four.", "这一段的结论是红色的：第 24 到 40 层读走的是意思和具体用词，不是论文身份；这推翻了 H2 的一般形式。下一页是第四段。")]
A[146] = [
 ("Stage four, layers 40 to 52: when is the title read, and when has it arrived?", "第四段，第 40 到 52 层：标题什么时候读完，什么时候送到？"),
 ("Two opposite tests: putting the true-title states back restores 0.82 at layer 48 and 0.995 at 52; taking them away from layer 52 on loses at most 0.05.", "两个方向相反的检验：把真标题的状态放回去，第 48 层恢复 0.82，第 52 层恢复 0.995；从第 52 层起拿走，最多只损失 0.05。"),
 ("On the left, a lucky false title is ruled out: all five false titles give the same timing.", "左边排除了“碰巧某一个假标题”：五个假标题给出的时间都一样。"),
 ("Together: the title is read and has reached the positions after the title by layer 52, a cross-check from both directions.", "合起来：标题到第 52 层已经读完，并送到了标题之后的位置，这是两个方向的交叉验证。"),
 ("Next, where exactly it lands and by which route.", "下一页看它具体落在哪里、走哪条路。")]
A[147] = [
 ("Part two of stage four: where does it land, and by which route?", "第四段第二部分：落在哪里，走哪条路？"),
 ("Position by position, the information lands mainly on the names: names alone restore 0.18 at layer 40, 0.61 at 48 and 0.84 at 52.", "一个位置一个位置地看，信息主要落在名字上：只换名字位置，第 40 层恢复 0.18，第 48 层 0.61，第 52 层 0.84。"),
 ("Blocking attention edges in windows finds the names-from-title edge carrying the delivery at layers 44 to 55; but a single-layer sweep shows no bottleneck: any one layer costs at most 1.25 percent.", "按窗口切断注意力边，找到名字看标题这条边在第 44 到 55 层承担输送；但逐层扫描显示没有瓶颈：任何一层最多只损失 1.25%。"),
 ("On the left, the idea that recognised papers are read earlier is ruled out: recognition changes the size, not the timing; and one route through one layer is overturned.", "左边排除了“认得的论文读得更早”：认得改变的是大小，不是时间；“一条路、一层”的说法也被推翻。"),
 ("Stage conclusion: by layer 52 the title has reached the name positions, through several layers in parallel. Next, stage five.", "这一段的结论：到第 52 层，标题已经送到名字位置，经过多层并行。下一页是第五段。")]
A[148] = [
 ("Stage five, layers 48 to 56: in what form is it held at the names?", "第五段，第 48 到 56 层：在名字位置是以什么形式存着的？"),
 ("A lens fitted on author prompts cannot read it: target minus control is negative, minus 0.058 at layer 48.", "用作者提示拟合的 lens 读不出来：target 减 control 是负的，第 48 层是 −0.058。"),
 ("A probe at the name positions can: it separates recognised from other papers from layer 40.", "名字位置的 probe 能读出：从第 40 层起就能分开认得和认不得的论文。"),
 ("The rescue is the same-scale test: on exactly the same tokens and one rank scale, the probe reads 0.062 more than the lens at layer 48.", "救场的是同尺度检验：在完全相同的 token 和同一把排名尺子上，第 48 层 probe 比 lens 多读出 0.062。"),
 ("So author information is linearly readable at the names, but not in vocabulary directions. Next: is it in one place?", "所以作者信息在名字位置是线性可读的，但不在词表方向上。下一页问：它是不是集中在一处？")]
A[149] = [
 ("Part two of stage five: is it concentrated anywhere?", "第五段第二部分：它有没有集中在哪里？"),
 ("Swapping only the author subspace carries about 7 percent; a direction analysis finds no component above 7 percent; and the readout map finds no earlier shelf, only scattered traces.", "只替换作者子空间，只带过去约 7%；方向分析找不到超过 7% 的成分；读出地图也没有更早的架子，只有零星痕迹。"),
 ("Three tests, one answer: the information is spread out, with no clean subspace, no single direction and no earlier shelf.", "三项检验，一个答案：信息是分散的，没有干净的子空间，没有单一方向，也没有更早的架子。"),
 ("Next, what the MLPs at these layers carry.", "下一页看这几层的 MLP 带的是什么。")]
A[150] = [
 ("Part three of stage five: what do the MLPs at layers 52 to 56 carry?", "第五段第三部分：第 52 到 56 层的 MLP 带的是什么？"),
 ("Swapping in the true-title MLP output restores 0.16 to 0.28, but swapping only 512 author-name directions restores 0.02 to 0.04: paper information, not ready-made names.", "把真标题运行的 MLP 输出换进来，能恢复 0.16 到 0.28；只换 512 个作者名方向，只恢复 0.02 到 0.04：带的是论文信息，不是现成的名字。"),
 ("Injecting the author direction raises correct surnames from 2.5 to 9.7 percent, but another author's direction works too, so it is mainly a write channel.", "注入作者方向能把写对姓的比例从 2.5% 提高到 9.7%，但注入另一位作者的方向也一样有效，所以主要是一个写入通道。"),
 ("On the left, the format layer is rewritten: the locked rule gave layer 56, but cutting the sink distorts it, so the layer is not pinned down.", "左边，格式层被改写：锁定规则给出第 56 层，但切掉 sink 会扭曲结果，所以这一层定不下来。"),
 ("Stage conclusion: at the names the probe reads it and the lens does not; what arrives is paper information, spread out, not ready-made names. Next, stage six.", "这一段的结论：在名字位置，probe 读得出、lens 读不出；送到的是分散的论文信息，不是现成的名字。下一页是第六段。")]
A[151] = [
 ("Stage six, layers 56 to 63: who writes the name?", "第六段，第 56 到 63 层：谁写出名字？"),
 ("Mean ablation at layers 57 to 61: replacing a layer's MLP costs more than replacing its attention, by 0.040 on average, and each MLP removes 11 to 14 percent of the signal. This is settled.", "第 57 到 61 层的均值消融：替换一层的 MLP，代价比替换注意力平均多 0.040；每层 MLP 去掉 11% 到 14% 的信号。这是定论。"),
 ("The group comparison shows the gap building over the last dozen layers, to 0.21 at the output.", "分组比较显示差距在最后十几层积累，到输出端是 0.21。"),
 ("And in vocabulary terms, the true name reaches about rank 10 only at layer 62.", "用词表方向来看，真名字要到第 62 层才排进大约前 10 名。"),
 ("So the late MLPs, not attention, write the name. Next, which part of the name.", "所以是后面的 MLP、不是注意力写出名字。下一页看名字的哪一部分。")]
A[152] = [
 ("Part two of stage six: which tokens carry the signal?", "第六段第二部分：哪些 token 带着信号？"),
 ("The surname's first token carries +0.68 and the rest +0.58, but an initial only +0.13; knowing the given name helps with the surname.", "姓的第一个 token 是 +0.68，其余 +0.58，首字母只有 +0.13；知道名有助于写姓。"),
 ("Co-authors help too, but through the co-author network rather than this paper.", "合作者也有帮助，但来自合作者网络，不是这篇论文本身。"),
 ("Giving the first initial lifts recognised papers from 4.0 to 15.2 percent with at least one full author right.", "给出名首字母，认得的论文写对至少一位完整作者的比例从 4.0% 升到 15.2%。"),
 ("So the signal sits on surnames and full given names; the start of the name is hardest. Next, why it gets stuck.", "所以信号在姓和完整的名上；名字的开头最难。下一页看为什么会卡住。")]
A[153] = [
 ("Part three of stage six: why does it get stuck?", "第六段第三部分：为什么会卡住？"),
 ("Strengthening the arrived signal barely helps, 2.5 to 2.8 percent; direction-only pushes hurt in all nine cells, so the harm comes from direction, not amount.", "加强已到达的信号几乎没用，只从 2.5% 到 2.8%；只改方向的推法在九个格子里全都有害，所以伤害来自方向，不来自强度。"),
 ("About one paper in eight shows the name rising after layer 56 and then falling, slightly more often for recognised papers, just past the bound.", "大约八分之一的论文里，名字在第 56 层之后先升后降，认得的稍多一点，刚过界。"),
 ("On the left, the reversal curse is ruled out, and made-up names are not mixed-up neighbours: about half are not in the data at all.", "左边排除了反转诅咒；编造的名字也不是记混的近邻，大约一半根本不在数据里。"),
 ("Stage conclusion: the late MLPs write the name, and it gets stuck at writing, hardest at the start of the name. Next, how the pieces fit.", "这一段的结论：后面的 MLP 写出名字，卡在写出这一步，名字开头最难。下一页看这些部分怎么拼在一起。")]
A[154] = [
 ("This flowchart shows how each step of the story depends on the one before: thick arrows say what is handed down, and the experiments hang under each step.", "这张流程图显示故事的每一步怎样依赖上一步：粗箭头写着交下去的是什么，实验挂在每一步下面。"),
 ("Step one is the phenomenon, recognised but not said: the multiple-choice test defines the groups, and the gap appears only at the output, 0.21.", "第一步是现象：认得但说不出。选择题测试定义分组，差距只在输出端出现，0.21。"),
 ("On the left, the small-sample results were rescued by the full cohort and pre-registration, and statistical artefacts were ruled out.", "左边，小样本的结果由全队列和预注册补救，统计假象被排除。"),
 ("Step two is read early: put-back and take-away agree that the title is read by layer 52, and the colon follows the question.", "第二步是读得早：放回和拿走一致，标题到第 52 层读完，冒号跟着问题走。"),
 ("The dashed box on the right is a known gap: recognition is defined only in the multiple-choice prompt and never measured inside it. Next part.", "右边虚线框是一个已知缺口：“认得”只在选择题的 prompt 里定义，从没在它内部测过。看下一部分。")]
A[155] = [
 ("Part two: steps three and four.", "第二部分：第三步和第四步。"),
 ("Step three: what is delivered is meaning and specific words, not paper identity; the made-up title brings back about 75 percent.", "第三步：送去的是意思和具体用词，不是论文身份；编造标题能找回大约 75%。"),
 ("The gap left here is: if only meaning is delivered, where does the knowledge of who wrote this paper enter?", "这里留下的缺口是：如果送去的只是意思，“谁写的这篇论文”从哪里进来？"),
 ("Step four: where it goes and by which route; position patching, windowed edge blocking and the single-layer sweep together say names from title, several layers in parallel.", "第四步：送到哪里、走哪条路；逐位置替换、窗口式切断注意力边和单层扫描合起来说明：名字看标题，多层并行。"),
 ("On the left, one route through one layer is overturned. Next part.", "左边，“一条路、一层”被推翻。看下一部分。")]
A[156] = [
 ("Part three: steps five and six.", "第三部分：第五步和第六步。"),
 ("Step five: in what form it is held; the same-scale test shows the probe beats the lens, the information is spread out, and the MLPs at layers 52 to 56 carry paper information, not names.", "第五步：以什么形式存着；同尺度检验显示 probe 胜过 lens，信息是分散的，第 52 到 56 层的 MLP 带的是论文信息，不是名字。"),
 ("Made-up names are ruled out as mixed-up neighbours.", "编造的名字被排除是记混的近邻。"),
 ("Step six: who writes the name; the mean ablation shows the MLPs at layers 57 to 61 write it, with the signal on surnames and full given names.", "第六步：谁写出名字；均值消融显示第 57 到 61 层的 MLP 写出它，信号在姓和完整的名上。"),
 ("The dashed gap is still there: no direct test of where the knowledge of who wrote this paper enters. Next, the last part.", "虚线缺口还在：没有直接检验“谁写的这篇论文”从哪里进来。看最后一部分。")]
A[157] = [
 ("Part four: step seven, where it gets stuck.", "第四部分：第七步，卡在哪里。"),
 ("Giving the first initial helps, 4.0 to 15.2 percent; strengthening the signal does not, 2.5 to 2.8 percent; pushing hurts through direction; and late suppression affects about one paper in eight.", "给出名首字母有帮助，4.0% 到 15.2%；加强信号没有用，2.5% 到 2.8%；推法的伤害来自方向；后期压制影响大约八分之一的论文。"),
 ("On the left, the reversal curse is ruled out and the idea that the signal is too weak is overturned.", "左边，反转诅咒被排除，“信号太弱”被推翻。"),
 ("Joint conclusion: the bottleneck is the late writing step, not signal strength.", "合起来的结论：瓶颈在最后的写出这一步，不在信号强弱。"),
 ("Each step hands one question to the next, and two links are still broken: where the knowledge of who wrote this paper enters, and recognition measured inside the multiple-choice prompt.", "每一步把一个问题交给下一步；还有两处没接上：“谁写的这篇论文”从哪里进来，以及在选择题 prompt 内部测量“认得”。"),
 ("Next, what we learned, in words.", "接下来，用文字总结我们学到了什么。")]
assert sorted(A) == list(range(133, 158))
TAGZH = {'desc': 'descriptive', 'solid': 'fairly solid', 'lnot': 'not supported / locked', 'lsup': 'supported / locked', 'settled': 'settled', 'expl': 'exploratory'}
PARTS = {140: '实验（自上而下）：同一论文换新问题；同一标题换问题；天花板从哪来 → 三种问题的第 0 层、只用词嵌入（身份指数 0.998 [0.998, 0.999]）、不认识论文的 BERT（找回率 1.000）。',
         141: '实验：天花板来自一模一样的输入字 → 早期读法被天花板审计撤回 → 段结论：L0–L4 由输入的字决定状态，L4 是所有"超出字面"检验的字面基线 → 交给 L4–L40（改写标题以 G′ − G′(L4) 衡量）。',
         142: '实验：冒号 probe 换问题后 0.24–0.41；冒号注意力 62–92% 落在第 0 位置；层顺序（标题信息、第一作者 token 在 L8–L16 最早出现）；标题位置读论文属性（年份 R² 从 L16 的 0.38 上升，可由标题文字推出）；改写标题（从 L8 起高于 L4 水平）。',
         143: '实验：L8 姓氏确认检验（6,048 篇新论文，扣掉同主题配对 +0.046 [+0.035, +0.056]；超过文本基线和认得更大两项刚过线；约一半来自主题）；排除字面重叠（来源检查）；救场：主题配对检验样本太小，由确认检验补上；不能判定：文本基线未过正对照，L56 回到约 0；标题位置 probe L24 +0.052 [+0.018, +0.086]。',
         144: '实验：哪些标题词带信号（随机替换内容词 vs 同义词）；改写标题（L36 峰值 +0.159 [0.146, 0.171]）；编造标题检验（0.751 [0.723, 0.778]，真标题多出 +0.106）。',
         145: '实验：稀有词 vs 常见词（0.162 vs 0.027）；认得 / 引用数检查（不更大，引用多的更小）；方差分解（身份 ≈ 0，意思 0.17–0.27）；论文信息子空间替换（R_id 0.004）；被划掉："中间层存论文身份"；例外：L8 姓氏锁定小例外；排除：主题先验。',
         146: '实验：放回（L48 0.821、L52 0.995）与拿走（L52 起 ≤ 0.05）方向相反、结论一致；5 个假标题时间一致（排除碰巧某个假标题）。',
         147: '实验：逐位置替换（名字位置 0.176 → 0.605 → 0.835，L40/L48/L52）；窗口式切断注意力边（L48–51 窗口 +0.0112 [+0.0084, +0.0138]）；单层扫描（任何一层 ≤ 1.25%）；名字位置 probe L40 +0.031 [+0.019, +0.044]；排除："认得的论文读得更早"（R(L48) 0.90 → 0.81，只改变大小）；推翻："一条路、一层"；600 篇子样本，单层切断只是下界。',
         148: '实验：作者提示 lens（L48 −0.058 [−0.088, −0.028]）；名字位置 probe（+0.053 [+0.038, +0.067]）；同尺度检验（9,137 个名字 token，L40 +0.021、L48 +0.062 [+0.041, +0.081]）。',
         149: '实验：只替换作者子空间（约 7%）；差异方向分析（无主成分超过 7%）；读出地图（672 格中零星弱痕迹，无更早架子）。',
         150: '实验：L52–L56 MLP 携带的内容（恢复 0.158–0.275 vs 512 个名字方向 0.022–0.042）；注入作者方向（2.5% → 9.7%，主要是写入通道，认得特有部分 +0.025 到 +0.035）；改写：格式层（锁定规则给 L56，受切断 sink 影响，定不下来）。',
         151: '实验：L57–L61 均值消融（MLP − 注意力 +0.040 [+0.036, +0.045]，每层 MLP 去掉 11–14%）；分组比较（输出端 +0.207 [0.195, 0.220]）；名字到 L62 才排进约前 10 名。',
         152: '实验：第一个 token 还是其余部分（首字母写法第一个 token 约 0.1，后续约 0.45）；信号在哪些 token（姓首 token +0.68、其余 +0.58、首字母 +0.13）；知道名有助于写姓（+0.22 vs 约 0）；合作者（来自合作网络）；给出名首字母（4.0% → 15.2%）；真名 vs 编造名（AUROC 0.72–0.78，只比输出置信度 0.711 高 +0.050 到 +0.062）。',
         153: '实验：加强已到达的信号（2.5% → 2.8%）；为什么加强有害（只改方向 9/9 格有害）；后期压制（12.8% vs 9.1%，+0.037 [+0.002, +0.073]，刚过界）；排除：反转诅咒（−0.032 [−0.047, −0.016]）；排除：编造名是记混的近邻（约一半不在数据里）。'}
BANDOF = {}
for x in NEWS:
    m = re.match(r'(?:step\d_|stage_)(L\d+_L\d+)', x[1])
    if m: BANDOF[x[0]] = m.group(1).replace('_', '–')
FLOWSTEPS = {154: [1, 2], 155: [3, 4], 156: [5, 6], 157: [7]}
FIRSTPART = {}
for x in NEWS:
    if x[1].startswith('stage_') and x[1].endswith('_a.png'): FIRSTPART[BANDOF[x[0]]] = x[0]
for x in NEWS:
    pg, f, title, ask, so, tc, tt = x[:7]; sok = x[8] if len(x) > 8 else 'So (this slide)'
    k = PALL[pg][0]
    s = ['## P%d · HTML v72 p%d · pptx S%d (v22w) — %s\n' % (pg, pg, k, title), '**要说的话（一句英文一句中文）**']
    for en, zz in A[pg]: s += [en, zz]
    s += ['', '**备查（不念）· 本页幻灯片全文：** %s Now asking: %s [figure: %s] %s: %s %s' % (title, ask, f[:-4].replace('_', ' '), sok, so, tt),
          '', '**备查（不念）· 证据强度：** %s（页底标签“%s”）。%s' % (TAGZH[tc], tt,
              '图内自带三行灰字（公式、n、读法），在图片下方。' if not f.startswith('flow') else '流程图是示意图，没有画数值，所以没有公式 / n 行（prepublish 例外已登记）。'), '']
    if pg == 133: s += [SRCNOTE + '（总的拼图）', '', WHOLE, '']
    elif pg in FLOWSTEPS:
        s += [SRCNOTE + '（故事拼图）', '']
        for st in FLOWSTEPS[pg]: s += [STEPMAP[st], '']
        if pg == 157: s += [GAPS, '']
    elif f.startswith('step'): s += [SRCNOTE + '（完整故事，%s 段）' % BANDOF[pg], '', BAND[BANDOF[pg]], '']
    else:
        s += ['**备查（不念）· 本页内容：** ' + PARTS[pg], '']
        if FIRSTPART[BANDOF[pg]] == pg: s += [SRCNOTE + '（完整故事，%s 段；本段后续部分共用此段）' % BANDOF[pg], '', BAND[BANDOF[pg]], '']
        else: s += ['同段定稿树原文见 P%d 的备查。' % FIRSTPART[BANDOF[pg]], '']
    pages[pg] = '\n'.join(s) + '\n'
N = max(pages)
assert sorted(pages) == list(range(1, N + 1)), [p for p in range(1, N + 1) if p not in pages]
parts = []
for ln in open(H + '27_v67/toc_v72.md', encoding='utf-8'):
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
# 【】 verification: every old page keeps its notes, verbatim and in order
bad = []
for p, notes in nnotes_old.items():
    if NOTE.findall(pages[p]) != notes: bad.append(p)
print('pages', N, 'new', len(NEWS), 'notes old', sum(len(v) for v in nnotes_old.values()), 'notes new', len(NOTE.findall(txt)), 'pages with note mismatch', bad)
