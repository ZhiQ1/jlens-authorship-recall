# Leader deck 讲稿：AI 为什么编作者名——"读得早，说得晚"

版本信息和修改历史见修改日志（~/jlens_work/changelog_2026-11-23.md 及更早的 changelog）。当前：jlens_leader_v17n.pptx，68 页（2026-11-24）。

结构说明（v17n）：正文 P1–P36 按 HTML v68 的 Part 排列——Part 0 开场；Part 2–6 每部分以问题卡开头、关键页居中、判定卡和过渡结尾，Part 3 分 3a（标题什么时候被读）和 3b（H1：格式什么时候定下来）；Part 7 总结（机制图、证据账本、已定 vs 待定，再接原总结页）。P37 是附录分隔页，附录 P38–P68（检验表占 P52–P53）。每页标题写 leader 页码、HTML v68/v69 页码（两版页码相同）和主 PPT v22t 页码。每页分 A（要说的话，一句英文一句中文）和 B（备查，不念）。

## 论证链概览

This deck walks the argument in parts: the puzzle, then what is read early, what is read, where it goes, and where it gets stuck.
这份 deck 按部分讲论证：先是谜题，然后是读得早的是什么、读到的是什么、送到哪里、卡在哪里。

**备查（不念）：** 上一版的概览原文：AI 会编造作者名，这有两种解释：它不知道（书从来没上过架），或者它知道但说不出（书在架上，送不到嘴边）。我们把 Qwen3-32B（64 层）比作一座 64 层的图书馆，标题像书脊上的主题，作者是书，用 9,108 篇论文一步步检验。第一步，"认得出"和"写得出"需要的曝光量差约 276 倍（确认性），说明知道和说得出是两回事（P2）。第二步，对认得出的论文，真标题能在模型内部打开这篇论文的书，起作用的是标题的意思（P5–P6）；一张写着同样主题、但不属于这本书的卡片（编造标题）能走到四分之三，真实论文只多给一小块（锁定的确认性检验，P7）。第三步，书在第 40–50 层就被推车送到名字格（P8，推车上装书的主要是名字格），路上是一场接力、没有哪条走廊包办（P10），但要到第 57–61 层才由书桌（MLP）写成词（P9–P11，已定论），整趟路程放在一把尺子上就是"读得早，说得晚"（P12）。第四步，名字说出来之前是什么形式：三个假设里，H1 在冒号和名字位置成立，H2 部分支持（大部分是意思，真实论文多出一点），H3（作者信息在，但还不是词）在同一把尺子上得到支持（P13–P15）。第五步，说不出的直接原因是最先要写的首字母最弱（P16）；模型自己还带着一个弱的"这是编的"信号（探索性，P18）。最后是总结和意义（P19–P20）。  ---

# Part 0 · Opening

## P1 · leader p1 · HTML v71 p2 · main pptx S2 (v22v) — The question（问题）

**要说的话（一句英文一句中文）**
Ask an AI who wrote a paper, and it will often name authors with great confidence — and they are made up.
问 AI 一篇论文是谁写的，它常常很自信地报出作者——而这些名字是编的。
There are two ways to read that. Either it never knew the authors, or it knows them but cannot get them out.
这有两种理解：要么它从来不知道作者，要么它知道，只是说不出来。
These two pictures predict different things inside the model, so we can tell them apart.
这两种图景对模型内部的预测不一样，所以我们分得开。
We tested them on 9,108 papers with one model, Qwen3-32B.
我们用一个模型 Qwen3-32B，在 9,108 篇论文上做了检验。
The short answer, for papers the model recognises, is the second picture: it knows but cannot say.
先说结论：对模型认得出的论文，是第二种——知道，但说不出。
First, a picture that helps us talk about what happens inside.
先给一个图景，方便我们讲模型内部发生了什么。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
大家可能都遇到过：问 AI 某篇论文是谁写的，它会很自信地报出几个名字，一查全是编的。有两种可能：一种是它根本不知道，书从来没上过架；另一种是它知道，书就在架上，只是送不到嘴边。这两种图景的预测不同：如果不知道，真标题在模型里面什么也不会改变；如果知道但说不出，里面会对真标题有反应，只是名字在出口处丢了。先给结论：对认得出的论文，是第二种。

**核心数字/数据点**
- 一个模型：Qwen3-32B，64 层
- 9,108 篇论文，33,811 个作者位置
- 结论预告：对认得出的论文，是图景 2（"知道但说不出"）
- 对话框里的标题和名字是中性占位，不是真实记录

**过渡语**
那凭什么说它"知道"？先看一个外面就能看到的现象。

## P2 · leader p2 · HTML v71 p3 · main pptx S3 (v22v) — The library（图书馆）

**要说的话（一句英文一句中文）**
Think of the model as a library with 64 floors, one floor per layer.
把模型想成一座 64 层的图书馆，一层对应模型的一层。
The authors of a paper are a book somewhere in it, and the title is how we ask for that book.
一篇论文的作者是馆里的一本书，标题是我们借这本书时报的信息。
A trolley carries things up through the middle floors, a desk near the top works on them, and the top floors say the next word.
推车在中间几层把东西往上送，靠近顶层的书桌加工，最上面几层把下一个词说出来。
Keep in mind that floors are steps of computation, not storage rooms.
要记住：一层是一步计算，不是一个储物间。
Next: how we look inside this library.
下一页：我们怎么往这座图书馆里看。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
我们把模型想成一座 64 层的图书馆。论文标题像书脊上写的"主题"，这篇论文的作者是一本"书"；从下往上分几段：早段、中段，运输段像一辆小推车把信息送到要写答案的位置，加工段像一张书桌处理送来的东西，最上面的"说出"段把它念出来，变成下一个词。要提醒的是：层是计算的步骤，不是储物格，每一层能做什么取决于它在多高的位置。

**核心数字/数据点**
- 64 层（L0–L63）分段：早段 L0–24，中段 L24–40，运输 L40–50，最后装载 L50–52，加工 L52–56，说出 L57–63
- 运输、加工、说出三段的描述来自本项目的发现；早段和中段是对 Transformer 一般作用的通俗说法
- 本页没有实验数字

**过渡语**
有了这座图书馆，我们怎么看里面发生了什么？用三种工具。

## P3 · leader p3 · HTML v71 p10 · main pptx S10 (v22v) — How we look inside（怎么往里看）

**要说的话（一句英文一句中文）**
We look inside in three ways.
我们用三种方式往里看。
Reading the label: a lens asks, at each floor, which word the state looks most like; it only sees what is already a word.
读标签：lens 在每一层问，这个状态最像哪个词；它只看得到已经变成词的东西。
Scanning the barcode: a probe is trained to spot a particular author even before the name is printed as a word.
扫条形码：probe 是训练出来专门认某个作者的，名字还没变成词时也能认出来。
Swapping or locking: we move states between runs, or block a route, and see what changes.
换货或锁门：在两次运行之间搬状态，或者堵住一条路，看什么会变。
The first two read; the third intervenes, and that is what lets us talk about causes.
前两种是读，第三种是干预，有了干预才能谈因果。
With these tools, Part 2 starts from something we can see from the outside.
有了这些工具，第 2 部分从一个外面就看得到的现象开始。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
三种工具。读标签（lens）：在每一层问"这个状态现在最像哪个词"，只能看到已经贴上词标签的书。扫条形码（probe）：用很多论文训练一个检测器专门认某个作者，书上还没印出字也能认出来。换货或锁门（替换 / 阻断）：把真标题那次运行里推车上的货换进假标题的运行，或者从第 L 层起锁门不让答案那边再看标题，由此知道书必须在什么时候搬走。

**核心数字/数据点**
- 读标签 = word-reader（"lens"）；扫条形码 = trained detector（"probe"）；换货 / 锁门 = replacement / blocking
- 后面的关键对比：读标签的看不到、扫条形码的看得到，说明信息在，只是还不是词的形式（第 22 页）
- 本页没有实验数字

**过渡语**
先用这些工具回答第一个问题：书到底在不在架上？

# Part 2 · Recognised but not said

## P4 · leader p4 · HTML v71 p25 · main pptx S26 (v22v) — Part 2 · question card（问题卡：认得出但说不出）

**要说的话（一句英文一句中文）**
Part 2 asks one thing: does the model not know the authors, or know them but cannot say them?
第 2 部分只问一件事：模型是不知道作者，还是知道但说不出？
If it knows, then for papers it cannot write, it should still pick the true author list out of a line-up.
如果它知道，那些它写不出作者的论文，它仍然应该能从一排名单里挑出真作者。
And picking should need far less exposure than writing.
而且挑出来需要的曝光应该远少于写出来。
If it does not know, those papers are not picked out either, and both need about the same exposure.
如果它不知道，这些论文它也挑不出来，两者需要的曝光也差不多。
The next page checks exactly this.
下一页就检验这个。

**备查（不念）：** 对应 HTML deck 第 24、34 页；正文第 5 页（谜题）、附录第 38 页（曝光门槛）。本页不出现新数字。

## P5 · leader p5 · HTML v71 p25 · main pptx S26 (v22v) — The puzzle（谜题）

**要说的话（一句英文一句中文）**
This page asks whether recognising the authors and writing them are the same ability.
这一页问：认得出作者和写得出作者，是不是同一种能力。
We showed the model four author lists and asked it to pick; separately, we asked it to write the authors itself.
我们给模型四份作者名单让它挑，另外再让它自己写作者。
Then we asked how many citations a paper needs before each of these works half the time.
然后看一篇论文要被引用多少次，这两件事才各有一半时候能做到。
On the chart, each curve is the share of papers where it works; the point where a curve crosses one half is the threshold.
图上每条曲线是能做到的论文比例；曲线过一半的那个点就是门槛。
Recognising crosses at about 40 citations, writing at about 11,000 — roughly 276 times more.
认出来的门槛约 40 次引用，写出来约 11,000 次——大约 276 倍。
So knowing and saying really are two different things, and the rest of the talk asks where the gap sits.
所以知道和说得出确实是两回事，后面整场都在问这个差距在哪里。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
同一篇论文，给它四个作者名单让它选，它能选对；让它自己写，一个真作者都写不出来，就像在列队里认得出那张脸，却叫不出名字。如果"认得出"和"写得出"是同一种能力，两者需要的曝光量应该差不多。实际上，论文被引用约 40 次模型就认得出，要约 11,000 次才写得出，差了约 276 倍。

**核心数字/数据点**
- 认得出的门槛：约 40 次引用；写得出的门槛：约 11,000 次引用（n = 9,108 篇）
- 比值 ≈ 276×，95% CI 203–390，**已确认**（补充 19；数据先看过、规则事后锁定）
- 结论：知道 ≠ 说得出 **[已确认]**
- 后面比较的两组：A 组 4,110 篇（认得出、写不出），B 组 2,186 篇（都不行）
- 细节在附录 p. 38

- 画面与来源：右边两条 logistic S 形曲线（横轴对数引用数），绿 = 认得出、红 = 写得出，点 = 13 个引用档的实际比例，两线之间橙色带 = "认得出但说不出"；50% 门槛 40 [36, 44] 与 11,038 [8,172, 15,607]，ρ = 276 [203, 390]（锁定在看过数据之后）；只有 16 / 9,108 篇在 11,038 次以上。来源：391_groups/summary_exposure_prereg19/thresholds_ratio.csv（c50、slope_log10cit，平均年份）、391_groups/summary_exposure_20261114/exposure_by_bin.csv（点）、351_stage10/cohort/papers.parquet（16 篇）。

**过渡语**
既然知道和说得出是两回事，就得打开模型往里看。先介绍我们用的比喻。

## P6 · leader p6 · HTML v71 p35 · main pptx S36 (v22v) — Part 2 · verdict card（判定卡：认得出但说不出）

**要说的话（一句英文一句中文）**
So, the answer to Part 2: recognised, but not said.
所以第 2 部分的答案是：认得出，但说不出。
Of 6,296 papers where it writes no author at all, it still picks the true list for 4,110.
在 6,296 篇它一个作者都写不出的论文里，有 4,110 篇它仍能挑出真名单。
Writing needs about 276 times the citations that recognising needs; the locked part is simply that it needs more.
写出来需要的引用大约是认出来的 276 倍；锁定确认的只是“需要更多”这一点。
One thing is still open: line-up distractors matched by topic might relabel some papers.
还有一点没定：按主题匹配的选择题干扰项，可能会让一部分论文改标。
So the book is in the library. Next: what does the model read first — the question and the title.
所以书在馆里。下一步：模型最先读的是什么——问题和标题。

**备查（不念）：** 4,110 / 6,296 篇（A 组 / R0 全部）；ρ = 276 [203, 390]，看过点估计后锁定，只确认 ρ > 1（补充登记 19）。证据强度：measured / locked · supported。未解决：按主题匹配的选择题干扰项可能会让一部分 target 论文改标。

# Part 3 · Read early (H1)

## P7 · leader p7 · HTML v71 p36 · main pptx S37 (v22v) — Three hypotheses（三个假设）

**要说的话（一句英文一句中文）**
Before a name comes out, what form is the information in? We had three pictures.
名字说出来之前，信息是什么形式？我们有三种图景。
H1, the task: the middle layers mainly hold “write an author list”.
H1，任务：中间层主要装的是“要写一个作者名单”。
H2, which paper: they hold the call number of this paper.
H2，哪一篇：中间层装的是这篇论文的索书号。
H3, hidden authors: the authors are already there, but not yet as words.
H3，藏着的作者：作者信息已经在了，只是还不是词。
They are not exclusive; the next page weighs the evidence for each.
三者不互斥；下一页把每一种的证据放到天平上。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
名字说出来之前，书以什么形式存在？三种图景。H1"任务"：馆员只知道接下来要给一份名单，中间层主要存的是任务。H2"哪一篇"：馆员知道要的是哪本书，中间层主要存的是论文身份。H3"藏着的作者"：书已经在手上，只是封面上的字还没印出来，作者信息在，但不在词的方向上。三者不互斥。

**核心数字/数据点**
- H1 预测：换问题时状态会变
- H2 预测：年份、领域、引用早早可读；同一篇论文在不同问题下看起来相似
- H3 预测：扫条形码能读到作者，读标签读不到
- 每个检验问的是：某一层、某个位置主要体现哪一种图景
- 本页没有实验数字

**过渡语**
把每个检验放到天平上，看三个假设各站在哪里。

## P8 · leader p8 · HTML v71 p38 · main pptx S39–S40 (v22v) — Where they stand（证据天平：综合）

**要说的话（一句英文一句中文）**
Here every test sits on a balance for each picture: for, against, or can’t tell.
这里每个检验都放在天平上：支持、反对，或者分不清。
H1 holds at the colon and the name slots, but which layer fixes the format is not pinned down.
H1 在冒号和名字位置成立，但哪一层把格式定下来，目前定不下来。
H2 comes out as the topic on the spine rather than the call number, with one small locked exception.
H2 的结果是书脊上的主题，而不是索书号，有一个小的锁定例外。
H3 is supported on the same scale, but the effect is small.
H3 在同一把尺子上成立，但效应小。
Part 3 now takes the first picture, the task, on its own.
第 3 部分单独看第一种图景：任务。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 19 页）

**备查（不念）：** 天平上的代号改成了白话短词：swap = 换问题（X1），match = 跨问题找同一篇（X5），decode = 从标题解码（X4），part = 只换一小部分（X2），reword = 改写标题（X3），probe = 标题位置的检测器（E4b），ruler = 同一把尺子检验（补充 17），made-up = 虚构标题（补充 20）。H1 降级：锁定规则给出 L56，但主检验不单调、很可能被切断 attention sink 扭曲；patching 检验指向 L40–L56；补充检查（探索性）显示下凹只在切掉 sink 时出现（391_groups/summary_a23_supp/）。

**这页在讲什么**
每个小方块是一个检验，放在"支持"或"反对"一边，分不清的放在下面；横梁的倾斜表示结论，不是数方块。H1：冒号处换问题比换论文让状态移动得多得多，在冒号和名字位置成立。H2：标题处读得出论文属性；补充登记 20 用意思相同的虚构标题把"意思"和"这篇论文"分开了：意思给四分之三，真实论文多出一小块，所以是部分支持、大部分由意思解释。H3：在同一把尺子上得到支持，但效应小。旁边虚线框是两项不上天平的描述性结果。

**核心数字/数据点**
- H1：支持 ":"，分不清 M1 → 在冒号和名字位置成立
- H2：支持 M2、X1，部分支持 add.20（新加的虚线筹码）；反对 M3、X5、X4、X2；分不清 X3 → 部分支持：大部分由意思解释（意思相同的虚构标题走到 3/4，真标题多出 +0.11，补充登记 20，锁定）
- H3：支持 add.17、E4b；反对 M4；分不清 X4、X2 → 同尺度下支持（效应小，只看姓的第一个片段）
- 不上天平 **[描述性，18b]**：书桌的内容大部分不在名字词方向上，符合 H3 的图景（p. 26）；第 48 层以前的早期痕迹很弱（p. 31）
- 矩阵在附录 pp. 52–53，每个检验在 pp. 54–61
- 画面与来源：筹码颜色 = 这个检验所属结论有多稳（conclusions_v30_draft.md 第五节表第 2 列），位置 = 判定（支持 / 反对 / 分不清），虚线边 = 部分支持。绿：add.20（C35 确认）、M3 和 X5（C06 定论）、add.17（C22，补充 17 锁定检验）。橙：":"（C23）、M2（C13）、X1（C12）、X3（C14）、H2 一侧的 X4（C15）、E4b（C09–C11）、M4（C16）都是没有锁定检验的较稳；H3 一侧的 X4（C21 未定）；两处 X2（C22 下的降级子项，事后改判据）；M1 在结论表里没有单独条目，只作描述。所以 H1 唯一的“支持”筹码 ":" 也是橙色。图例：settled · confirmed · locked / no lock yet · open · exploratory / partly。

**过渡语**
H3 最关键的那条证据，下一页细看。

## P9 · leader p9 · HTML v71 p39 · main pptx S41 (v22v) — Part 3 · question card（问题卡：H1 任务）

**要说的话（一句英文一句中文）**
Part 3 asks whether the task — “write an author list” — is what the middle layers mainly hold.
第 3 部分问：中间层主要装的是不是任务——“写一个作者名单”。
The colon state is the model’s internal state at the colon, just before the answer starts.
冒号状态就是模型读到答案前那个冒号时内部的状态。
If the task is what is held, that state should follow the question, not the paper, and some middle layer should fix the answer format.
如果装的是任务，这个状态应该跟着问题变、不跟着论文变，而且某个中间层会把答案格式定下来。
If not, it follows the paper, and nothing fixes the format before the very end.
如果不是，它跟着论文变，直到最后都没有哪一层定下格式。
We test this with question swaps at the colon, and by asking when the title is read.
我们用在冒号处换问题，以及看标题什么时候被读，来检验。

**备查（不念）：** 对应 HTML deck 第 38 页（问题卡）；检验：冒号与换问题（附录第 57–58 页），标题读得早（正文第 11 页）。本页不出现新数字。

# Part 3a · When is the title read?

## P10 · leader p10 · HTML v71 p40 · main pptx S42 (v22v) — Part 3a · question card（问题卡：标题什么时候被读）

**要说的话（一句英文一句中文）**
Part 3a asks a timing question: is the title read on the way up, or only at the top?
第 3a 部分问一个时间问题：标题是在往上走的路上被读，还是到顶才读？
If it is read early, swapping in the real-title states at a middle floor should bring back most of its advantage.
如果读得早，在中间某一层把真标题那次的状态换进来，应该能找回大部分优势。
And blocking the title late should cost almost nothing, because it has already been read.
而且很晚才挡住标题，应该几乎没有损失，因为它已经读完了。
If it is read only at the top, nothing comes back until the last floors.
如果到顶才读，直到最后几层什么也找不回来。
The next page runs both tests.
下一页同时做这两个检验。

**备查（不念）：** 对应 HTML deck 第 39 页（3a 问题卡）；检验：换货与阻断（正文第 11 页、附录第 43 页）。本页不出现新数字。

## P11 · leader p11 · HTML v71 p45 · main pptx S47–S48 (v22v) — Finding 2（发现 2：书拿得早）

**要说的话（一句英文一句中文）**
This page asks when the title is read: early on the way up, or only at the top?
这一页问：标题什么时候被读——往上走的路上，还是到顶才读？
We ran the model with a wrong title, then at one floor swapped in the states from the real-title run, after the title.
我们先用错误的标题跑，在某一层把标题之后的状态换成真标题那次的。
On the chart, 1 means the swap brings back all of the real title’s advantage, 0 means nothing comes back.
图上 1 表示这次替换找回了真标题的全部优势，0 表示什么也没找回。
It is about half by layer 45, 93% by layer 50 and almost all by layer 52.
第 45 层找回一半，第 50 层 93%，第 52 层几乎全部。
And the name slots carry most of it: 0.84 at layer 52, against 0.18 for the colon.
而且主要装在名字格：第 52 层 0.84，冒号格只有 0.18。
So the title is read early; Part 3’s verdict comes next.
所以标题读得早；接下来是第 3 部分的结论。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果标题要到最上面才被读，那么在第 50 层"换货"应该找不回多少。我们先用假标题跑，在某一层把标题之后各位置的状态换成真标题那次的，看能找回多少，就是看推车上装了多少书。第 45 层装了一半，第 50 层 93%，第 52 层几乎全满。再看推车上哪一层架子装着这本书：每次只换一组位置，第 52 层时名字格找回 0.84，冒号格只有 0.18，年份格 0.03；名字格从第 40 层的 0.18 涨到第 52 层的 0.84。所以标题在往上走的路上就被读完了，书主要装在名字格里（描述性）。

**核心数字/数据点**
- 推车上的书（换货找回比例）：第 45 层一半，第 50 层 93%，第 52 层 99.5%，第 63 层全满（n = 1,186 篇）
- 哪一层架子装着书（18b 第 3 项，第 52 层，五个假标题平均 R）：名字格 0.84，冒号格 0.18，年份格 0.03；名字格 0.18 → 0.84（第 40 → 52 层）**[描述性]**（600 篇）
- 从第 52 层起锁住标题只损失约 3%：已移出本页，在第 31 页里程碑 3 和附录 p. 43
- 结论：标题在往上的路上就被读了，64 层里第 50 层就取到，装在名字格里 **[描述性]**
- 右下虚线小标签 **[探索性]**：引用多的论文到得稍晚一点——按引用中位数（31）分半，L48 找回比例高半 0.789、低半 0.865（差 −0.076 [−0.104, −0.046]），target、control 都一样；L52 两半都接近满
- 细节：附录 p. 43（替换和阻断曲线）· p. 44（哪一层架子，18b 第 3 项）· p. 45（按引用数分半）

**过渡语**
书拿得这么早，那是不是马上就能说出来？

# Part 3b · H1: when is the answer format fixed?

## P12 · leader p12 · HTML v71 p50 · main pptx S54 (v22v) — Part 3b · question card（问题卡：H1 格式什么时候定下来）

**要说的话（一句英文一句中文）**
Part 3b turns to H1: when is the answer format, “write an author list”, fixed?
第 3b 部分回到 H1：答案格式——“写一个作者名单”——是什么时候定下来的？
If a middle floor fixes it, the colon state should follow the question, and blocking the question before that floor should change the answer type.
如果是中间某一层定下来，冒号处的状态应该跟着问题变；在那一层之前挡住问题，会改变答案的类型。
If not, the colon follows the paper, or no single floor can be pinned down.
如果不是，冒号处跟着论文变，或者找不到一个确定的层。
The verdict card that follows gives the answer, and it is a cautious one.
后面的判定卡给出答案，而且是一个谨慎的答案。

**备查（不念）：** 对应 HTML deck 第 48 页（3b 问题卡）；检验：冒号与换问题（附录第 57–58 页）。本页不出现新数字。

## P13 · leader p13 · HTML v71 p56 · main pptx S60 (v22v) — Part 3 · verdict card（判定卡：H1）

**要说的话（一句英文一句中文）**
So, Part 3: the question is read at the colon, but the layer that fixes the format is not pinned down.
所以第 3 部分：问题在冒号处被读到，但哪一层把格式定下来，目前定不下来。
A new question moves the colon state far more than a new paper, and the title is read by layers 50 to 52.
换一个问题，冒号处的状态比换一篇论文动得多得多；标题在第 50 到 52 层读完。
The locked format rule pointed to layer 56, but that test also cuts the attention sink; with the sink kept, names hold from early on, partly because names are the default answer.
锁定的格式规则指向第 56 层，可那个检验同时切断了 attention sink；保留 sink 时，名字从很早就保持住，部分原因是名字本来就是默认答案。
What we did measure is that swapping the colon state at layer 56 lowers the author signal.
确实测到的是：在第 56 层换掉冒号处的状态，会降低作者信号。
Still open: a year and field measure good enough to test the format layer.
还没解决的：需要一个足够好的年份和领域测量，才能检验格式层。
So the question and the title are read early. Next: what exactly is read from the title.
所以问题和标题都读得早。下一步：从标题里读到的到底是什么。

**备查（不念）：** 冒号：换问题比换论文多移动 2.2–4.7 倍（描述性）；标题到达：R 一半在 L45，L50–L52 完全到达（已定论）；格式锁定：锁定规则给出 L56，但主检验不单调、受切断 attention sink 影响（补充登记 23；补充实验为探索性：sink = position 0，保留 sink 时 names 类型从 L4 起保持，名字是默认答案类型）；L56 换“:”状态 Δspec −0.031 [−0.038, −0.024]（补充登记 26）。对应 HTML deck 第 51–53 页。未解决：年份/领域需要基线准确率足够的测量。

# Part 4 · Meaning, not identity (H2)

## P14 · leader p14 · HTML v71 p58 · main pptx S62 (v22v) — Part 4 · question card（问题卡：H2 论文身份）

**要说的话（一句英文一句中文）**
So far we know the title is read early. Now the question is: what does the model actually take from it?
到这里我们知道标题读得早。现在的问题是：模型到底从标题里拿走了什么？
By the title state we mean the model’s internal state at the title.
我们说的标题状态，就是模型读到标题时内部的状态。
There are two very different answers. One is “which paper this is”, like a library call number.
有两种很不一样的答案。一种是“这是哪一篇论文”，像图书馆的索书号。
The other is “what the title means”, more like the topic written on the spine.
另一种是“这个标题是什么意思”，更像书脊上写的主题。
If it is the call number, a card with the same topic written on it, but not belonging to this book, should get us nowhere.
如果是索书号，一张写着同样主题、但不属于这本书的卡片，应该什么也找不到。
And whatever the real title adds should be bigger for papers the model recognises, and for papers that are cited a lot.
而且真标题多出来的那部分，在模型认得出的论文、被引用很多的论文上应该更大。
If it is the topic, that card should get most of the way, and the extra should sit on a few specific words.
如果是主题，那张卡片应该能走到大半，多出来的那点会落在几个具体的词上。
The next pages run exactly these tests, ending with one small exception we found and locked.
接下来几页就做这几个检验，最后是我们发现并锁定的一个小例外。

**备查（不念）：** 对应 HTML deck 第 55 页（问题卡）；检验：按词替换（正文第 15–16 页）、同主题的卡片（第 17 页）、唯一的锁定例外（第 18 页）。本页不出现新数字。

## P15 · leader p15 · HTML v71 p29 · main pptx S30 (v22v) — Finding 1（发现 1：书在架上）

**要说的话（一句英文一句中文）**
This page asks whether the model knows this particular paper at all.
这一页问：模型到底知不知道这一篇论文。
We compared the real title with look-alike titles from the same field and year.
我们拿真标题和同领域、同年份、长得像的标题比较。
On the chart, a value above 0 means the real title pushes the true author up more than a look-alike does.
图上大于 0 表示真标题比长得像的标题更能把真作者往前推。
Knowing the paper adds +0.42; a name that is simply easy to guess adds only +0.02.
知道这篇论文贡献 +0.42；只是好猜的名字只贡献 +0.02。
So the real title finds the right book and a wrong title does not; the next pages ask what in the title does it.
所以真标题能找到那本书，错误的标题找不到；后面几页问标题里起作用的是什么。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果模型不知道这篇论文，真标题和同领域、同年份的"长得像"的假标题拉力应该一样，架上没有哪本书会被单独点亮。实际上，真标题能找到这本书：模型内部会把真作者的姓往前排。这不是因为名字好猜：拆开看，好猜的名字只贡献 +0.02，"知道这篇论文"贡献 +0.42；而且论文被引用得越多，书在架上越清楚。

**核心数字/数据点**
- 指向真作者姓的拉力：知道这篇论文 +0.42，好猜的名字 +0.02（n = 4,621 + 2,220 篇）
- 随曝光增强：每 10 倍引用 +0.030 **[已确认]**（补充 19 第二项，n = 9,108 篇）
- 结论：对认得出的论文，排除"不知道"，书在架上
- 细节（约 1.6 倍、不给标题 = 随机水平）在附录 p. 39，曝光趋势在 p. 38

**过渡语**
书在架上，那标题里哪些词最要紧？

## P16 · leader p16 · HTML v71 p75 · main pptx S79 (v22v) — Finding 1b · meaning, not spelling（发现 1b：意思，不是写法）

**要说的话（一句英文一句中文）**
This page asks whether the model needs the title spelled exactly, or only its meaning.
这一页问：模型需要一字不差的标题，还是只需要它的意思。
We replaced meaningful words with synonyms, or with random words.
我们把有意义的词换成近义词，或者换成随机词。
On the chart, a bigger drop means that change hurt more.
图上下降越多，说明这种改动伤害越大。
Synonyms cost little; random words cost a lot; small words like “of” hardly matter.
换近义词损失很小；换随机词损失很大；of 这类小词几乎没影响。
So it reads the topic on the spine, not the exact spelling — a descriptive result, with rough synonyms.
所以它读的是书脊上的主题，不是写法——这是描述性结果，近义词比较粗。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果起作用的是一字不差的拼写，把标题里有意义的词换成近义词，应该和换成随机词一样找不到。实际上换成近义词还大致能找到，换成随机词就完全找不到；of、for 这类虚词影响很小。所以模型靠的是标题的意思，不是写法。这是描述性结果，近义词是自动找的，比较粗。

**核心数字/数据点**
- 真标题 +0.33；实义词换近义词 +0.24；实义词换随机词 −0.05
- n = 600 篇（其中 596 篇有近义词版本）
- 结论：起作用的是有意义的词 **[描述性；近义词测试较粗]**，虚词影响小
- 细节（词类、罕见词）在附录 p. 40

**过渡语**
既然起作用的是"意思"，那一张写着同样主题的卡片能走到多少？

## P17 · leader p17 · HTML v71 p76 · main pptx S80 (v22v) — Finding 1c · the same-topic card（发现 1c：同主题的卡片）

**要说的话（一句英文一句中文）**
This page asks the sharpest version: does a card with the same topic, but no real book behind it, work?
这一页问最尖锐的问法：一张写着同样主题、但背后没有真书的卡片，管不管用？
For each paper we wrote a made-up title that means the same thing but belongs to no real paper.
我们给每篇论文写了一个意思相同、但不属于任何真实论文的编造标题。
On the chart, 1 means the made-up title brings back everything the real title gives; we see about 0.75.
图上 1 表示编造标题能找回真标题的全部优势，我们看到的是约 0.75。
The real title adds a little on top, mostly from rare, specific words.
真标题在上面再多给一点，主要来自罕见、具体的词。
And that extra is not larger for papers it recognises — if anything, smaller for much-cited ones.
而且多出来的部分在认得出的论文上并不更大，在被引用很多的论文上反而更小。
So it mostly reads the topic on the spine, not the call number.
所以它读的主要是书脊上的主题，不是索书号。
One small exception survived a locked test: from layer 8, the title state carries a little of this paper's surname, beyond its topic.
有一个小例外通过了锁定检验：从第 8 层起，标题状态里带着一点这篇论文的姓氏信号，超出了主题能解释的部分。
So the answer is still “mostly meaning”, with one small locked exception; the details are on the next page.
所以答案仍然是“主要是意思”，外加一个小的锁定例外；细节在下一页。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**当时那项检验（编造标题检验）的锁定判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 19 页）

**备查（不念）：** H2 总判定（逐字）：Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal). 约一半来自主题（配对主题后保留 0.44 [0.36, 0.52]）。来源：391_groups/summary_a33/（补充 33，锁定 sha256 7a28ae2d…）。

**这页在讲什么**
上一页说起作用的是标题的意思。那模型认的是"这篇真实的论文"，还是只是"这个意思"？我们给每篇论文写了一个意思相同、但根本不存在的虚构标题——一张同主题的卡片。左边是"如果只有意思起作用"：同主题的卡片应该和真标题一样走到底（示意）。右边是实际：真标题给出 +0.42，同主题的卡片给出 +0.32，也就是四分之三；只有真标题才有的那一块是 +0.11。所以大部分是意思，但真实的论文确实多给了一小块，而且是在第 52 层以后才写进去的。这是事先锁定判据的确认性检验。

**核心数字/数据点**
- 真标题 +0.42（Ḡ 0.425）；意思相同的虚构标题 +0.32（Ā 0.319）；φ = 0.751 [0.723, 0.778]，即四分之三
- 只有真标题才给的部分 R̄ = +0.106 [0.094, 0.118]
- 锁定规则：R̄ 的 CI 全在 0 以上才读 φ；φ ≥ 0.5 → "部分支持：存在真实论文成分，但大部分信号可由语义相似解释" **[锁定的确认性检验，不在边界上]**
- 对照组 φ 0.770、R̄ +0.050；六项敏感性分析 φ 0.708–0.778，结论不变
- n = 566 篇 target（加对照共 1,127 篇）
- 细节（对照组、敏感性、层）在附录 p. 41

- 画面与来源：右边一根堆叠条——真 − 假差距 Ḡ_T 0.425 中橙色 75%（意思，φ_T 0.751 [0.723, 0.778]）+ 绿色 25%（只有真标题，R̄_T +0.106 [0.094, 0.118]）；下面一张标题卡片，橙色部分 = 任何意思相同的标题都有，最后一颗绿色齿 = 只有真实论文才切出。来源：391_groups/summary_a20/primary_secondary_sensitivity.csv（n = 566 target）。

**过渡语**
找到了书，那书是什么时候被取走的？

## P18 · leader p18 · HTML v71 p85 · main pptx S89 (v22v) — Part 4 · the one locked exception（唯一的锁定例外：从第 8 层起的姓氏信号）

**要说的话（一句英文一句中文）**
This page asks whether anything paper-specific survives once the topic is taken away.
这一页问：把主题拿掉之后，还剩不剩这篇论文特有的东西。
The title state is the model’s internal state at the title; we placed it into a neutral prompt and asked for the first author.
标题状态就是模型读到标题时内部的状态；我们把它放进一个中性的提示里，问第一作者。
We did that with this paper’s own state, with the state of the same-field paper whose title is closest, and with a random same-field paper.
分别用这篇论文自己的状态、同领域标题最接近的那篇的状态、随机一篇同领域论文的状态。
On the chart, above 0 means its own state beats its topic twin’s; at layer 8 it does, by a small amount.
图上大于 0 表示自己的状态胜过主题孪生的状态；在第 8 层确实如此，只多一点。
The locked test is at layer 8; later layers look larger, peaking at layer 40, but that part is descriptive.
锁定检验在第 8 层；后面的层看起来更大，第 40 层最高，但那部分只是描述性的。
About half of the raw signal is topic, and two of the three checks only just pass — a small exception, not strong evidence.
原始信号大约一半是主题，三项检验里有两项刚过线——是一个小例外，不是强证据。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**备查（不念）：** 判定（逐字）：Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal). T1 超出主题 +0.0457 [0.0353, 0.0559]，Holm 下界 +0.033；T2 Qwen − BERT（标准化）+0.045 [0.008, 0.082]，Holm 下界 +0.002；T3 target − control（按引用分档）+0.0246 [0.003, 0.047]。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]；L0 来源 ≈ 0。BERT 文本基线正对照 gain −0.24 log10（WARN，基线弱）。n = 6,048 篇（target 4,577、control 1,471），补充登记 33 锁定于 2026-11-23 08:52（sha256 7a28ae2d…），在任何模型运行之前；作者团队整群 bootstrap 2,000 次；来源 391_groups/summary_a33/。

## P19 · leader p19 · HTML v71 p86 · main pptx S90 (v22v) — Part 4 · verdict card（判定卡：H2）

**要说的话（一句英文一句中文）**
Let’s close Part 4 by answering the question we opened it with.
用开头那个问题来结束第 4 部分。
The model mostly takes the topic on the spine, not the call number.
模型主要拿走的是书脊上的主题，不是索书号。
The same-topic card gets about three quarters of the way, and the real title’s small extra sits on rare words and does not grow with recognition.
同主题的卡片能走到大约四分之三，真标题多出的一小块落在罕见词上，而且不随“认得出”变大。
There is one exception that held up under a locked test on six thousand new papers.
有一个例外，在六千多篇新论文上的锁定检验里站住了。
From layer 8, the title state carries a small surname signal for this particular paper, beyond its topic; the locked test is at layer 8, later layers are descriptive.
从第 8 层起，标题状态里有一个属于这篇论文的小姓氏信号，超出了主题；锁定检验在第 8 层，后面的层只是描述性的。
But keep it in proportion: about half of that signal is still topic, and two of the three checks only just pass.
但要看清比例：这个信号大约一半仍然来自主题，三项检验里有两项只是刚过线。
So the fair verdict is: meaning, not paper identity, with one small locked exception — not strong evidence.
所以公平的结论是：是意思，不是论文身份，有一个小的锁定例外——不是强证据。
Now that we know what arrives, the next part asks where it goes and in what form it is held.
知道了送来的是什么，下一部分就问：它送到哪里，以什么形式存着。

**备查（不念）：** H2 判定（逐字）：Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal). φ 0.751 [0.723, 0.778]、R̄ +0.106 [0.094, 0.118]（补充登记 20）；罕见词 0.162 vs 常见词 0.027（补充登记 24，词数 3.4 vs 2.1、常见词按词频匹配不是同义词）；K4 不支持、K4c 反向（补充登记 22）；补充登记 33：T1 +0.046 [0.035, 0.056]，T2 +0.045 [0.008, 0.082]（Holm 下界 +0.002，BERT 正对照失败），T3 +0.025 [0.003, 0.047]；配对主题后按层 D：L8 +0.046（锁定），L16 0.056、L24 0.066、L32 0.076、L40 0.093（最高）、L48 0.027、L56 ≈ 0（描述性）；0.44 [0.36, 0.52] 在配对主题后保留；L0 ≈ 0。对应 HTML deck 第 81–83 页。

# Part 5 · Route + H3

## P20 · leader p20 · HTML v71 p88 · main pptx S92 (v22v) — Part 5 · question card（问题卡：路线 + H3）

**要说的话（一句英文一句中文）**
Part 5 asks two things: how the title’s information reaches the name, and in what form it is held there.
第 5 部分问两件事：标题的信息怎么到达名字那里，以及在那里以什么形式存着。
If the authors are there but not yet words, the barcode scanner should see more than the label reader on the same ruler.
如果作者信息在、但还不是词，在同一把尺子上扫描器应该比读标签看到更多。
And pushing in the scanner’s direction should make the model write that author.
而且沿扫描器的方向推，应该能让模型写出那个作者。
If not, the two see the same, or one single corridor carries everything.
如果不是，两者看到的一样，或者只有一条走廊包办一切。
The next two pages test the route and the scanner.
接下来两页检验路线和扫描器。

**备查（不念）：** 对应 HTML deck 第 84 页（问题卡）；检验：路线（正文第 21 页；走廊：附录第 48 页）、同一把尺子（第 22 页）。本页不出现新数字。

## P21 · leader p21 · HTML v71 p98 · main pptx S102–S103 (v22v) — Finding 4（发现 4：路线）

**要说的话（一句英文一句中文）**
This page asks how the title’s information gets to the place where the name is written.
这一页问：标题的信息怎么送到写名字的地方。
If one part did all the work, swapping just that part would bring almost everything back.
如果只有一个部件在干活，单换它就应该找回几乎全部。
Instead it is a relay: attention fetches the title around layer 48, the desk works on it in layers 52 to 56, and it lands on the name slots.
实际上是一场接力：注意力在第 48 层附近把标题取过来，书桌在第 52 到 56 层加工，最后落在名字格。
On the corridor chart, the bar is the share of the signal lost when one corridor is closed; the biggest is about 3.4%.
走廊图上，柱子是关掉一条走廊时损失的信号比例；最大的约 3.4%。
So there is no single route; many corridors share the load.
所以没有唯一的路线，很多条走廊分担。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果只有一个部件在干活，单换它就应该找回接近全部，关掉它唯一的走廊就几乎全丢。实际上是一场接力：一个"回头看"的店员（attention）在第 48 层回到门口把标题信息取过来，书桌（MLP）在第 52 到 56 层继续加工，东西最后落在要写名字的格子里。单换任何一个部件都只能找回一部分。再关走廊：在 4 层的窗口里只切断"名字 ← 标题"这一条注意力边，它是损失最大的那条，但最多也只丢 3.4% 的信号；锁定判据成立，而且换 11 种窗口切法有 7 种同样成立（第 42–57 层），对窗口位置稳健，效应小。

**核心数字/数据点**
- 店员（attention，L48）：24%
- 书桌（MLP，L52 / 56）：18–23%
- 名字格（L48 → L52）：61% → 84%
- n = 1,186 篇；单一部件的替换是下界（加起来不必等于 100%）
- 关掉"名字 ← 标题"走廊 4 层（第 44–55 层内的窗口）：最多损失 3.4% 的信号（18b 第 2 项，n = 600 篇）**[锁定判据成立 · 稳健]**
- 稳健：11 个错开窗口中 7 个成立（第 42–57 层）
- 结论：没有哪一个部件或哪一条走廊包办，是一条以名字格为终点的接力
- 细节：附录 p. 47（路线）· p. 48（走廊，18b 第 2 项）· p. 49（书桌）

- 画面与来源：一条从左到右的流程图：标题 → 注意力 L48（单独替换找回 +0.237，391_groups/summary_b1_p12f/p12f_mean5.csv，P5，1,186 篇）→ 名字格（只复制名字位置 L48 0.605 → L52 0.835，381_stage13/summary_a18b_item3/item3_mean5.csv，600 篇）→ MLP L52–56（+0.181 / +0.226，P5）→ MLP L57–61（每拿掉一层损失 11–14%，summary_a18b_item4/item4_table.csv，锁定判据成立）→ 输出（整段尾部 L52 复制 0.988，600 篇；E1 0.995，1,186 篇）；下方：单条走廊最多 3.5%（summary_a18b_item2_step2_fix/item2_table.csv）。各数字来自不同实验、不同样本，不能相加。

**过渡语**
书桌在这条路上做了什么、交出去的是什么？往书桌里面看。

## P22 · leader p22 · HTML v71 p103 · main pptx S109 (v22v) — H3 · key evidence（H3 的关键证据）

**要说的话（一句英文一句中文）**
This page asks whether author information is there before it becomes a word — the H3 picture.
这一页问：作者信息在变成词之前是不是已经在了——也就是 H3。
We put the barcode scanner and the label reader on the same ruler, on the same name tokens, with a rule locked in advance.
我们把扫描器和读标签放在同一把尺子上，用同样的名字 token，判据事先锁定。
On the chart, above 0 means the scanner sees more of the true author than the label reader.
图上大于 0 表示扫描器比读标签看到更多真作者。
In the middle layers it does, a little, until the label reader catches up at layer 56.
在中间层确实多一点，到第 56 层读标签才追上来。
So the authors are there, but not yet as words; the effect is small.
所以作者信息在，只是还不是词；效应小。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果说出词之前根本没有作者信息，那么在同一把尺子上，扫条形码和读标签应该打平。实际上，在名字位置的中间层，读标签读不到，扫描器能扫到一点点：比读标签多看到一些，规则是事先锁定的，到第 56 层读标签才追上来。所以 H3 同尺度下成立，但效应小；这和书桌那一页是同一种形式：信息在，但还不在词的方向上。

**核心数字/数据点**
- 扫描器 − 读标签（同一把尺子）：第 48 层 +0.062，第 40 层 +0.021；第 56 层打平
- n = 4,654 篇
- 结论：H3 同尺度下支持，效应小 **[锁定]**，与书桌（p. 26）形式相同
- 细节（同尺度检验、逐层、按名字部分）在附录 pp. 62–64

**过渡语**
信息在里面，那为什么最后还是说不出来？

## P23 · leader p23 · HTML v71 p112 · main pptx S119 (v22v) — Part 5 · verdict card（判定卡：路线 + H3）

**要说的话（一句英文一句中文）**
So, Part 5: a relay with many corridors brings the information to the name slots, and the authors are held there, but not yet as words.
所以第 5 部分：一场多条走廊的接力把信息送到名字格，作者信息在那里存着，但还不是词。
By layer 52 the name slots carry the title’s signal, and no single corridor or layer is a bottleneck.
到第 52 层名字格已经带着标题的信号，没有哪一条走廊或哪一层是瓶颈。
On the same ruler the scanner sees more than the label reader at layers 40 and 48.
在同一把尺子上，扫描器在第 40 和 48 层比读标签看到更多。
Pushing the scanner’s author direction does make it write surnames more often, but mainly as a write channel: another author’s direction writes that author too.
沿扫描器的作者方向推，确实会更常写出姓，但主要是写入通道：换成别的作者的方向，也会写出那个作者。
Still open: what the late desk actually reads from those slots, tested causally.
还没解决：后面的书桌到底从这些格子里读了什么，需要因果检验。
So the information is there by layer 52. Next: why doesn’t the name come out?
所以信息在第 52 层就到了。下一步：为什么名字说不出来？

**备查（不念）：** 到达 R(L52) 0.995（已定论）；单层扫描：name ← title 在 L44/L48/L52/L54 有信息，每次切断 ≤ 1.25% 的 S（补充登记 32）；probe − lens 同尺度 L40 +0.021 [0.008, 0.034]、L48 +0.062 [0.041, 0.081]（补充登记 17）；注入：写对姓氏 2.5% → 9.7%，主要是写入通道，target 特有部分 +0.02–0.035（补充登记 25）。对应 HTML deck 第 104–108 页。未解决：书桌从名字格读了什么，需要因果检验。

# Part 6 · Said late, stuck at writing

## P24 · leader p24 · HTML v71 p114 · main pptx S121 (v22v) — Part 6 · question card（问题卡：写名字这一步）

**要说的话（一句英文一句中文）**
Part 6 asks where the failure is: in reading the paper, or in writing the name?
第 6 部分问：失败在哪里——是读论文，还是写名字？
If it is writing, the late desk writes the name, a stronger arrived signal does not help, and the first piece of the name is the hardest.
如果是卡在写，后面的书桌写名字，加强已经到达的信号没用，名字最先那一块最难。
If not, pushing the signal harder should bring the name out, or going from authors to title should be easier — a reversal curse.
如果不是，把信号推得更用力就该能把名字推出来，或者从作者到标题会更容易——也就是反转诅咒。
The next pages test each of these.
接下来几页逐个检验。

**备查（不念）：** 对应 HTML deck 第 109 页（问题卡）；检验：说得晚（正文第 25 页）、书桌（第 26 页）、最弱的第一块（首字母）（第 27 页）、用力推（第 28 页）。本页不出现新数字。

## P25 · leader p25 · HTML v71 p94 · main pptx S98 (v22v) — Finding 3（发现 3：说得晚）

**要说的话（一句英文一句中文）**
This page asks: once the book arrives, can the model already say the name?
这一页问：书送到之后，模型是不是马上就说得出名字？
We put two curves side by side: how much has arrived, and how much the label reader — that is, the lens — can read as a word.
我们把两条曲线放在一起：送到了多少，以及读标签的工具，也就是 lens，能读出成词的有多少。
On the chart, each curve goes from 0 to 1; where it crosses one half is the floor where that step is half done.
图上每条曲线从 0 到 1；过一半的那一层，就是这一步完成一半的地方。
Arrival is half done by layer 45; readable as a word only by layer 58.
送到在第 45 层完成一半；能读成词要到第 58 层。
In between, the book is there but still wrapped — read early, said late.
中间这一段，书已经到了，但还包着——读得早，说得晚。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果拿到就等于说得出，书在第 50 层送到时，封面上的字也应该能读出来。实际上，"书到了没有"在第 45 层就到一半，而读标签的工具在名字位置要到第 58 层才读到一半。中间这一段就是"已经拿到、还说不出来"的空档：书已经送到，但还包着包装纸。

**核心数字/数据点**
- 到达一半：L45；可读成词一半：L58
- n：到达 1,186 篇，可读 6,841 篇
- 两条线量纲不同，只比较"什么时候起来"
- 结论：图书馆从第 50 层起就有这本书，但大约第 57 层以前说不出来
- 细节（两条逐层曲线）在附录 p. 46

- 画面与来源：书架纵剖面（L24–L63）：左侧蓝条 = 推车上装书比例 R(l)（L45 0.529，L50 0.929，L52 0.995；381_stage13/summary_e1x6_extra_20261114/e1x6_recovery.csv，1,186 篇），右侧橙条 = logit lens 名字位置 T − C ÷ L62 的 0.229（351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv，6,841 篇）；"Name!" 气泡在 L57，因为 J-lens T − C 从 L57 起 > 0（+0.029 [0.009, 0.048]）；L50–57 的浅橙带 = 书到了但还包着。

**过渡语**
从取到书到说出来，中间是谁在搬、谁在干活？

## P26 · leader p26 · HTML v71 p127 · main pptx S135 (v22v) — Finding 4b · the desk（发现 4b：书桌）

**要说的话（一句英文一句中文）**
This page asks who writes the name at the top.
这一页问：最上面是谁在写名字。
In layers 52 to 56 we swapped the desk’s output, either all of it or only its name-word part.
在第 52 到 56 层，我们换掉书桌的输出，要么全换，要么只换跟名字词有关的那一部分。
The name-word part brings back only a little more than a random part of the same size.
只换名字词那一部分，比同样大小的随机部分只多找回一点点。
In layers 57 to 61 we removed the desk or the attention, one layer at a time.
在第 57 到 61 层，我们一层一层拿掉书桌或者注意力。
On the right chart, the bar is the share of the signal lost; the desk costs about 12% per layer, attention almost nothing.
右边的图上，柱子是损失的信号比例；拿掉书桌每层约 12%，拿掉注意力几乎没有。
So the desk writes the name, but not from ready-made name cards.
所以名字是书桌写的，但不是照着现成的名片写的。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
左边是第 52 到 56 层：把整张书桌的输出换进假标题运行能找回一部分；如果书桌里放的是一摞现成的名片，只换"名字词方向"那一部分应该差不多一样多，可实际上只比同样大小的随机部分多一点点，大部分在其余方向里。右边是第 57 到 61 层，也就是名字真正被念出来的那几层：每层拿掉书桌，信号少约 12%；拿掉店员几乎没影响。所以名字是书桌写出来的，但不是照着现成的名片写的。

**核心数字/数据点**
- 第 52–56 层（找回比例）：整张书桌 0.16–0.28；名片部分 0.02–0.04；同维随机部分 0.01–0.02（n = 600 篇）**[描述性]**
- 第 57–61 层（拿掉后每层损失的信号）：书桌约 12%（每层 11–14%），店员 ≈ 0（n = 600 篇）**[已定论（锁定判据成立）]**
- 结论：书桌写出名字 **[已定论（锁定判据成立）]**，用的内容不在名字词方向上 **[描述性]**
- 细节（逐层、attention、目标 vs 对照）在附录 p. 49

**过渡语**
把到现在为止的发现放到同一把尺子上看。

## P27 · leader p27 · HTML v71 p34 · main pptx S35 (v22v) — Why it can't say it（为什么说不出）

**要说的话（一句英文一句中文）**
This page asks why the name does not come out, even though it has arrived.
这一页问：名字明明到了，为什么还是说不出来。
A name is written piece by piece, and the model usually starts with the initial.
名字是一块一块写的，模型通常先写首字母。
On the chart, each bar is how much the real title pushes that piece of the name; the initial gets the smallest push.
图上每根柱子是真标题对名字这一块的推力；首字母得到的推力最小。
When we give the first initial in the prompt, recognised papers write the surname more often.
在提示里先给出首字母，认得出的论文写出姓的次数就更多。
So the first step of writing is the weak point; the next page asks whether pushing harder helps.
所以写的第一步是薄弱点；下一页问用力推能不能解决。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
名字是一段一段写出来的，模型通常先写首字母。可是真标题对首字母的推力最小，对名和姓大得多：最先要写的那一块恰恰最弱。如果只是缺知识，额外的提示不会有用；实际上，在提示里先给出第一作者首字母，认得出的论文就更能写出姓。另一种提示是给一个真合作者，其他作者的排名也会上升，但这是合作者网络的联想，不是这篇论文特有的记忆。

**核心数字/数据点**
- 真标题对名字各部分的推力（按写出顺序）：首字母 +0.12，名 +0.35，姓 +0.72（n = 每部分 3,163–6,841 篇）
- 给首字母：认得出比认不出多写出姓 +0.085 **[锁定 · B]**（600 + 600 篇）
- 给一个真合作者：其他作者 +0.17，但不是论文特有的，是网络联想（D，600 篇，A 组）
- 结论：首字母这一块是真正的瓶颈；合作者路线是网络联想
- 细节（全部五个名字部分、格式）在附录 p. 66

**过渡语**
既然说不出时它会编，那模型自己分得清真名和编的名字吗？

## P28 · leader p28 · HTML v71 p128 · main pptx S136 (v22v) — Why it can't say it (2) · pushing harder（为什么说不出（二）：用力推也推不出来）

**要说的话（一句英文一句中文）**
This page asks: is the push simply too weak?
这一页问：是不是推力不够？
At layer 48 or 52 we amplified the paper’s own signal that had already arrived, by 1, 2 and 4 times.
在第 48 或 52 层，我们把这篇论文自己已经到达的信号放大 1、2、4 倍。
On the chart, a bar to the right of the line would mean more correct authors than with no push.
图上柱子越过竖线向右，就表示比不推时写对更多作者。
None of the six settings clearly beats the line, and the harder we push, the worse the true name ranks.
6 种推法没有一种明显越过竖线，推得越用力，真名字的名次反而越差。
So it is not a matter of strength; Part 6’s verdict sums this up.
所以问题不在力度；第 6 部分的结论会总结这一点。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
上一页说第一块（首字母）最弱。那是不是推力不够？补充登记 21 直接检验：在第 48 或 52 层，把这篇论文自己已经到达的标题信号放大 1、2、4 倍（不是把答案塞进去），看认得出的论文会不会因此写出作者。左边是“如果只是推力不够”：推得越用力，写出来的越多（示意）。右边是实际：没有一格明显变好，推得越用力，真名字的名次反而越差。

**核心数字/数据点**
- 认得出的论文写对至少一位作者：不推 3.8%；自己的信号最好一档 4.3%；L52 放大 4 倍 2.8%；放大另一篇论文同样强度的信号 1.7%（n = 1,200 篇，600 认得出 + 600 认不出）
- 自己 − 不推：6 格都在 −0.010 到 +0.005，Holm 区间都含 0；自己 − 另一篇最大 +0.020 [0.003, 0.037]，Holm p 0.15 **[锁定 · 补充 21：不支持]**
- 推得越用力，真名字名次越差：L52 ×4 −0.102 [−0.113, −0.092]，推另一篇论文也一样（一般性损伤）
- 公式：G = rate(own) − rate(none)，S = rate(own) − rate(other)
- 结论：卡住的不是信号强弱，而是最后几层把信息变成名字这一步
- 细节（6 种推法、名次随推力变化）在附录 p. 67

**过渡语**
既然说不出时它会编，那模型自己分得清真名和编的名字吗？

## P29 · leader p29 · HTML v71 p124 · main pptx S131 (v22v) — Finding 5 · exploratory（发现 5：探索性）

**要说的话（一句英文一句中文）**
This page is exploratory: does the model carry its own sign that a name is made up?
这一页是探索性的：模型自己有没有“这个名字是编的”的信号？
We looked at how hesitant it is while writing a name, and at what a probe reads in the middle layers.
我们看它写名字时有多犹豫，再看 probe 在中间层读到什么。
On the chart, 0.5 would be a coin flip between real and made-up names; above that means it can tell them apart.
图上 0.5 等于抛硬币分真假；高于 0.5 表示分得开。
Hesitation alone already beats a coin flip, and the middle layers add a little.
光看犹豫程度就比抛硬币好，中间层再多一点。
About half the made-up names are not in the data at all, so they are not confused neighbours.
编造的名字大约一半根本不在数据里，所以不是把邻近的人搞混了。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
如果模型自己没有任何信号，分辨真名和编造名就是抛硬币。实际上，光看它写名字时的犹豫程度，就能分得比抛硬币好；用扫描器读中间层还能再多一点，而且只在第 40 到 52 层多出来。另外，编造出来的名字大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）；合作者只占 4.0%（随机 1.3%），"把邻近的人搞混"这个想法不成立。这一页全部是探索性的。

**核心数字/数据点**
- 分辨真名与编造名：抛硬币 0.50；只看置信度 0.71；中间层扫描器 0.78
- 扫描器只在第 40–52 层领先
- n = 518 篇，3,388 对
- 编造名：大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）；合作者只占 4.0%（随机 1.3%）（n = 40,219 个名字，8,872 篇）→ 想法 C 不支持 **[探索性]**
- 结论：模型带着一个弱的、自己的"这是编的"信号 **[探索性]**
- 细节在附录 pp. 66–68

**过渡语**
把四个问题的答案收在一起。

## P30 · leader p30 · HTML v71 p131 · main pptx S139 (v22v) — Part 6 · verdict card（判定卡：写名字这一步）

**要说的话（一句英文一句中文）**
So, Part 6: it gets stuck at writing — the late desk writes the name, and the first piece is the hardest.
所以第 6 部分：卡在写这一步——后面的书桌写名字，最先那一块最难。
In layers 57 to 61 the desk, not attention, writes the name.
第 57 到 61 层，是书桌而不是注意力在写名字。
Pushing harder gives no gain in any setting, while giving the first initial raises correct writing from 4.0% to 15.2%.
用力推在任何设置下都没有收益；给出首字母，写对的比例从 4.0% 升到 15.2%。
Going from authors to title turns out slightly harder, not easier, so this is not a reversal curse.
从作者到标题反而稍难，不是更容易，所以这不是反转诅咒。
Still open: a causal test of the writing step itself.
还没解决：对写名字这一步本身做因果检验。
Now let’s put the whole story together.
现在把整个故事放在一起。

**备查（不念）：** L57–L61 MLP − attention +0.040 [0.036, 0.045]（已定论）；用力推 6 种设置均无收益，损害取决于方向（补充登记 21、27）；首字母 4.0% → 15.2%（补充登记 16 B，F4）；方向不对称（补充登记 30）：R1 +0.443 [0.373, 0.517]，R2 −0.032 [−0.047, −0.016]，锁定判定“反向”（生成标题稍难），反转诅咒解释不成立；后期压制约 1/8 论文先升后降（12.8% vs 9.1%，T−C +0.037 [0.002, 0.073]，补充登记 31）。对应 HTML deck 第 122–127 页。

# Part 7 · Summary

## P31 · leader p31 · HTML v71 p133 · main pptx S141 (v22v) — One ruler（一把尺子：综合）

**要说的话（一句英文一句中文）**
Part 7 starts by putting the whole journey on one ruler.
第 7 部分先把整趟旅程放在一把尺子上。
On the left, read early: title facts by layer 16, the paper arrives half by layer 45 and fully by 50.
左边是读得早：标题的事实在第 16 层前就有，论文第 45 层送到一半，第 50 层送完。
On the right, said late: the name is written only in layers 57 to 61.
右边是说得晚：名字要到第 57 到 61 层才写出来。
Before layer 48 there are only faint, scattered traces — no clear earlier shelf.
第 48 层以前只有微弱、零散的痕迹，没有清楚的更早书架。
Next, the same story as one map.
下一页，把同一个故事画成一张图。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
把整趟旅程放在同一把尺子上：左半段"读得早"，标题的事实在第 16 层以前就能在标题处读出来，论文信息在第 45 层送到一半、第 50 层送完，从第 52 层起锁住标题几乎没有代价；右半段"说得晚"，名字要到第 57–61 层才由书桌写成词。我们还查了书会不会更早出现在名字格以外的地方：第 48 层以前只有微弱、零散的痕迹，没有一个清楚的"更早的书架"；推车上装书的主要是名字格，年份格最多 0.08，而且只是短暂出现。

**核心数字/数据点**
- ① 第 16 层以前：标题的事实在标题处可读
- ② 一半 L45、全部 L50：论文信息到达名字格
- ③ 从 L52 起：锁住标题几乎不损失
- ④ L57–61：书桌把名字写成词
- 第 48 层以前其他位置只有微弱零散痕迹（18b 第 1 项；按讲稿：54 个组合里 15 个过线，效应小，未做多重比较校正）
- 推车上主要是名字格在装，年份格 ≤ 0.08 且短暂（18b 第 3 项，L46–47 最高，L56 ≈ 0）
- n = 每行 518–9,108 篇；每个里程碑只比"何时"，不比大小
- 结论：论文在第 50 层前已读完，名字到 57–61 层才说出来
- 完整图在附录 p. 50，18b 第 1 项格子图在 p. 51

**过渡语**
知道了书在哪、什么时候到，下一个问题是：说出来之前，书是什么形式？

## P32 · leader p32 · HTML v71 p135 · main pptx S143 (v22v) — Part 7 · the answer on one map（机制图）

**要说的话（一句英文一句中文）**
This map puts the whole story in one picture: the prompt tokens across, the 64 layers up.
这张图把整个故事放在一张图上：横着是提示词的每个 token，竖着是 64 层。
The question is read at the colon, but which layer fixes the format is not pinned down.
问题在冒号处被读到，但哪一层把格式定下来，目前定不下来。
The title is read from layer 24 and done by 52; what it gives is the topic on the spine, with one small surname exception from layer 8.
标题从第 24 层开始读，到第 52 层读完；它给的是书脊上的主题，有一个从第 8 层起的小姓氏例外。
It reaches the name slots in layers 40 to 50, through many corridors, and is held there, not yet as words.
它在第 40 到 50 层通过很多条走廊到达名字格，在那里存着，但还不是词。
The late desk writes the name in layers 57 to 61, and that writing step is where it fails.
后面的书桌在第 57 到 61 层写名字，卡住的就是这一步。
Read early, said late: the bottleneck is the late writing step, not reading.
读得早，说得晚：瓶颈在后面写的那一步，不在读。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**备查（不念）：** 步骤①（哪一层定答案格式）已降级为“定不下来”；步骤③有一个小的锁定例外（第 18 页）。图 ~/jlens_work/25_restructure/mechanism_map.png（make_map.py）。

## P33 · leader p33 · HTML v71 p141 · main pptx S149 (v22v) — Part 7 · evidence ledger（证据账本）

**要说的话（一句英文一句中文）**
Here is the evidence behind each of the seven steps on the map, in one table.
这里把机制图上七步背后的证据放在一张表里。
Reading the title early and the late desk writing the name are settled.
标题读得早、后面的书桌写名字，这两步已经定论。
The topic rather than the call number, the hidden authors, and the failed push are locked tests.
是主题不是索书号、作者藏着、用力推无效，这几步是锁定检验。
The route is fairly solid, and the format layer is downgraded to not pinned down.
路线比较可靠，格式层降级为定不下来。
Ruled out: paper identity as a general representation, a stronger signal fixing recall, a reversal curse, and literal word overlap.
排除了：一般意义上的论文身份、加强信号就能回忆、反转诅咒，以及字面重叠。

**备查（不念）：** 本页不出现新数字；每一行的数字都在所列页码上。对应 HTML deck 第 136 页（证据账本）、第 132 页（排除了什么）。

## P34 · leader p34 · HTML v71 p144 · main pptx S152 (v22v) — Part 7 · settled vs pending（已定 vs 待定）

**要说的话（一句英文一句中文）**
On the left is what is settled or locked; on the right, what is still open.
左边是已定或锁定的，右边是还没定的。
Settled: knowing is not saying, the title is read early, it reads the topic not the call number, the authors sit at the name slots, and the late desk writes.
已定的：知道不等于说得出，标题读得早，读的是主题不是索书号，作者信息在名字格，后面的书桌负责写。
Open: which layer fixes the format, a stronger text baseline for the surname exception, a second model, a held-out replication, and a causal test of writing.
还没定的：哪一层定格式、姓氏例外需要更强的文本基线、第二个模型、留出样本复现，以及写名字的因果检验。
In one sentence: read early, said late — the bottleneck is the late writing step, not reading.
一句话：读得早，说得晚——瓶颈在后面写的那一步，不在读。

**备查（不念）：** 本页不出现新数字。对应 HTML deck 第 139 页（未解决的问题和下一步）。

## P35 · leader p35 · HTML v71 p133 · main pptx S141 (v22v) — Summary（总结）

**要说的话（一句英文一句中文）**
Four questions, four short answers.
四个问题，四个简短回答。
Is the book in the library? Yes, for recognised papers, and writing it needs far more exposure than recognising it.
书在不在馆里？在，对认得出的论文是这样；写出来需要的曝光远多于认出来。
Which floor? Fetched by layer 50, written as a word only at 57 to 61.
在哪一层？第 50 层就取到了，要到第 57 到 61 层才写成词。
What form? Not yet a word; the topic on the spine rather than a call number, with one small exception.
什么形式？还不是词；是书脊上的主题，不是索书号，有一个小例外。
Why can’t it say it? The first piece, the initial, is the weakest, and giving it helps.
为什么说不出？最先那一块——首字母——最弱，给出它就有帮助。
In one sentence: read early, said late — the bottleneck is the late writing step, not reading.
一句话：读得早，说得晚——瓶颈在后面写的那一步，不在读。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 19 页）

**备查（不念）：** 一句话答案按用户 2026-11-23 定稿，不加“作者信息已经在那里，只是没用上”之类的说法；机制图在第 32 页。

**这页在讲什么**
一句话：读得早，说得晚。四个问题各有答案，每条后面标了状态：书在架上吗？在，对认得出的论文，而且写得出需要多得多的曝光。在哪一层？第 40–50 层取到、装在名字格里，第 57–61 层才由书桌写成词。什么形式？还不是词。为什么说不出？最先要写的首字母最弱。

**核心数字/数据点**
- 书在架上吗：对认得出的论文，是；拉力随引用增强 **[已确认]**；写得出需要约 276 倍于认得出的引用 **[已确认]**；有意义的词起作用 **[描述性]**
- 哪一层：第 40–50 层取到（第 45 层一半），装在名字格里 **[描述性]**；第 57–61 层由书桌而不是店员写成词 **[已定论（锁定判据成立）]**
- 18b 第 2 项（单条走廊效应小、对窗口位置稳健）不改任何一张卡，只在第 21 页和附录 p. 48
- 什么形式：还不是词；H1 在冒号和名字位置成立；H2 部分支持（虚构标题拿到四分之三，真实论文多出一点）**[锁定]**；H3 同尺度下支持 **[锁定]**；书桌的内容大部分不在名字词方向上 **[描述性]**
- 为什么说不出：首字母最弱，给出首字母对认得出的论文有帮助 **[锁定]**；合作者提示靠网络联想，不是论文记忆；模型自带的"编造"信号 **[探索性]**
- n：9,108（门槛、趋势）· 4,621 + 2,220（书在架上）· 1,186（取到）· 6,841（说出）· 4,654（H3）· 600 + 600（B）· 600（D；18b）篇

**过渡语**
最后说说这对理解和改进模型意味着什么。

## P36 · leader p36 · HTML v71 p134 · main pptx S142 (v22v) — What it means（意义）

**要说的话（一句英文一句中文）**
What does this mean?
这意味着什么？
“It doesn’t know” is often the wrong diagnosis: for recognised papers the book is in the library.
“它不知道”常常是错误的诊断：对认得出的论文，书就在馆里。
The bottleneck is late, at writing, and the first piece is the weak point.
瓶颈在后面写的那一步，最先那一块是薄弱点。
The limits: one model and one task; the checker on the right is an idea, not a result.
局限：一个模型、一种任务；右边的检查器只是一个想法，不是结果。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**这页在讲什么**
模型可能带着一个自己的"这是编的"信号，但它没有用。第一，"它不知道"常常是错误的诊断：对认得出的论文，书在架上，只是写出来需要多得多的曝光。第二，瓶颈在后面：书桌到第 57–61 层才写出名字，最先要写的首字母那一块最弱，给它就有帮助。第三，局限：一个模型、一种任务；右边的检查器只是一种可能，没有做出来，不是结果。

**核心数字/数据点**
- 将来的检查器示意（未搭建，示意图）：置信度 0.71，中间层 0.78（518 篇，3,388 对，**探索性**）
- 约 276 倍的引用差（9,108 篇）
- 局限：一个模型（Qwen3-32B），一种任务（作者名）

**过渡语**
（正文到此结束。）后面是附录，按正文论证的顺序排，提问时可以直接翻到对应页。

---

# Appendix

## P37 · leader p37 · HTML — · main pptx — — Appendix（附录分隔页）

**要说的话（一句英文一句中文）**
From here on is the appendix, grouped by the step of the argument each page supports.
从这里开始是附录，按每页支撑的论证步骤分组。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**备查（不念）：** 2026-11-23 新增一行：52–53 → 正文 14、19（唯一的锁定例外；机制图）。页面上的内部标签（18b 第 N 项、add. N、addendum N）改成了白话名。
附录索引：按正文步骤分组，每组标出对应的正文页（21 → 正文 2；22–24 → 5–7（含按词类 18b-5、同主题的卡片 补充 20）；25–28 → 8–9（含哪一层架子 18b-3、按引用数分半 探索性）；29–31 → 10–11（路线、走廊 18b-2、书桌 18b-6/4）；32–33 → 12；34–42 → 14；43–45 → 15；46 → 16；47 → 17）。

## P38 · leader p38 · HTML v71 p25 · main pptx S26 (v22v) — Appendix · The puzzle（谜题）

**要说的话（一句英文一句中文）**
Back-up for the puzzle: on the chart, each curve is the share of papers where recognising or writing works; recognising crosses one half at about 40 citations, writing at about 11,000.
谜题的备份：图上每条曲线是能认出或能写出的论文比例；认出在约 40 次引用过一半，写出在约 11,000 次。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P5：选名单能选对、自己写写不出的示意；A 组 4,110 篇 / B 组 2,186 篇；认得不是开关（每多答对一种顺序约 +0.06，0/4 时 0.17 → 4/4 时 0.46，n = 8,288）；门槛约 40 [36, 44] vs 约 11,000 [8,172, 15,607] 次引用（n = 9,108）。

## P39 · leader p39 · HTML v71 p29 · main pptx S30 (v22v) — Appendix · Finding 1（发现 1 细节）

**要说的话（一句英文一句中文）**
Back-up for the right book: above 0 means the real title pushes the true author up; knowing the paper gives +0.42, easy names only +0.02.
“找对那本书”的备份：大于 0 表示真标题把真作者往前推；知道这篇论文给 +0.42，好猜的名字只给 +0.02。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P15：真作者确实在里面；+0.42（知道这篇论文）vs +0.02（好猜的名字）；认得出的论文真作者排名约高 1.6 倍；不给标题时 0.255 vs 随机 0.25；引用最少档 +0.35 → 最多档 +0.64（n = 3,734 + 2,182）。

## P40 · leader p40 · HTML v71 p75 · main pptx S79 (v22v) — Appendix · by word class（按词类替换）

**要说的话（一句英文一句中文）**
By word class: a bigger loss means that change hurt more; synonyms cost far less than random words, especially for content words.
按词类：损失越大表示伤害越大；近义词比随机词损失小得多，实义词尤其明显。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P16：换近义词 vs 换随机词按词类的损失（实义词 +0.087 / +0.374，虚词 +0.008 / +0.044，罕见词 +0.023 / +0.151）；近义词 − 随机 −0.287 [−0.306, −0.269]；描述性，WordNet 近义词粗糙且改动 token 数不同（5.6 vs 12.8）。

## P41 · leader p41 · HTML v71 p76 · main pptx S80 (v22v) — Appendix · the made-up title, details（同主题的卡片：细节）

**要说的话（一句英文一句中文）**
Back-up for the made-up title: on the chart, 1 means it brings back everything the real title gives; we see about 0.75, and the real title adds +0.11.
编造标题的备份：图上 1 表示能找回真标题的全部优势；我们看到约 0.75，真标题再多 +0.11。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P17：真 − 假标题差距 G 拆成 A（意思相同的虚构标题能恢复）+ R（只有真标题才给）；target A 0.319、R +0.106、φ 0.751 [0.723, 0.778]，control A 0.167、R +0.050、φ 0.770 [0.727, 0.814]；分箱内 target − control R +0.056 [0.039, 0.072]；六项敏感性 φ 0.708–0.778；R̄ 只在第 56 层以后 > 0（J-lens L62 +0.115），虚构标题替换从 L52 起停在 0.75；锁定的确认性检验，不在边界上；局限：单一模型、虚构标题在模型下概率更高、φ 随意思接近程度上升（0.72 → 0.79）、parity WARN；n = 1,127 篇。

## P42 · leader p42 · HTML v71 p79 · main pptx S83 (v22v) — Appendix · at the title (exploratory)（标题位置：真标题那颗齿几乎还没有）

**要说的话（一句英文一句中文）**
Exploratory: at the title position itself, above 0 means the real title beats the made-up one; it is barely above 0 there and grows only from about layer 48.
探索性：在标题位置，大于 0 表示真标题胜过编造标题；那里几乎只略高于 0，大约从第 48 层才长起来。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P17（探索性，事后，未预注册）：标题位置 probe 读真标题与意思相同的虚构标题，第 40 层 target 只差 +0.016 [−0.001, +0.033]，control +0.009，target − control +0.008 [−0.016, +0.031]；同位置真 − 假标题 +0.078，所以真标题多出的齿在标题位置约只有五分之一，到第 52 / 56 层才长到 +0.039 / +0.041。按引用数中位数分半：标题 probe 高 − 低 +0.003 [−0.076, +0.083]，名字位置 probe 第 40 层 +0.002、第 48 层 +0.001，都含 0——这指向曝光断层在“说出”那一步（探索性）。图旁公式：Δ = probe(true) − probe(made-up title)；n = 1,127 篇（566 + 561），分半用 1,395 / 4,654 篇。来源 391_groups/summary_a20/S5_E4b_probe.csv；381_stage13/summary_explore_citesplit_probes_20261121/report.md。

## P43 · leader p43 · HTML v71 p45 · main pptx S47–S48 (v22v) — Appendix · Finding 2（发现 2 细节）

**要说的话（一句英文一句中文）**
Back-up for “read early”: 1 means the swap brings back everything; half by layer 45, 93% by 50, 99.5% by 52.
“读得早”的备份：1 表示替换找回全部；第 45 层一半，第 50 层 93%，第 52 层 99.5%。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P11：提示中各位置示意 + 替换曲线（一半 L45，L48 82%，L50 93%，L52 99.5%，最大一步 L47→48 +0.26）和阻断曲线（从 L52 起只损失 3%），n = 1,186。

## P44 · leader p44 · HTML v71 p99 · main pptx S104 (v22v) — Appendix · which shelf (18b item 3)（哪一层架子）

**要说的话（一句英文一句中文）**
Which slot of the trolley carries the book: 1 means that slot alone brings back everything; the name slots reach 0.84 by layer 52, the colon only 0.18.
推车上哪一格装着书：1 表示只换这一格就找回全部；名字格到第 52 层是 0.84，冒号格只有 0.18。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P11：每次只把一组位置在某一层从真标题换成假标题，看效应回来多少；名字格 0.18 → 0.61 → 0.84（L40 / 48 / 52），冒号格晚起 0.07（L48）→ 0.18（L52），年份数字早而短（最高 0.08，L46–47，L56 ≈ 0），引号和其余尾部 ≤ 0.03，整个尾部 0.29 / 0.80 / 0.99 = p. 43 的已存曲线；对照论文找回多于目标论文；两项硬检查未达标记 WARN（逐行名次一致 0.72–0.81；五题均值 0.8211 vs 0.8211，差 8e-5）；描述性，n = 600 篇（引号格 363）× 5 个假标题。

## P45 · leader p45 · HTML v71 p32 · main pptx S33 (v22v) — Appendix · by citations (exploratory)（按引用数分半：细节）

**要说的话（一句英文一句中文）**
Exploratory, by citations: on the chart, a lower curve means the book arrives later; the more-cited half is a little later at layer 48.
探索性，按引用数：图上曲线越低表示书到得越晚；引用多的一半在第 48 层稍晚一点。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P11：按引用数中位数（31）把 1,186 篇分半，推车装书比例 R：第 48 层低半 0.865、高半 0.789（差 −0.076 [−0.104, −0.046]，target −0.079、control −0.073），第 52 层 1.006 对 0.988；target − control 的时间差不随引用数变化（−0.006 [−0.072, +0.065]）；logit lens 两半没有差别；J-lens：引用多的一半自身的 target − control 在 L48–L55 低于 0，但两半之差只在 L53–L55 排除 0（L53 −0.073 [−0.138, −0.010]，L54 −0.076 [−0.141, −0.012]，L55 −0.073 [−0.145, −0.006]），L48–L52 和 L56 含 0；全队列补充（中位数 66）两半之差在 L40–L56 每一层都低于 0（L48 −0.065 [−0.093, −0.038]）；事后分析、未预注册、单一模型；n = 1,186 篇；来源 381_stage13/summary_explore_citesplit_20261120/。

## P46 · leader p46 · HTML v71 p94 · main pptx S98 (v22v) — Appendix · Finding 3（发现 3 细节）

**要说的话（一句英文一句中文）**
Back-up for “said late”: both curves run from 0 to 1; arrival is at 93% by layer 50, while reading it as a word reaches half only at layer 58.
“说得晚”的备份：两条曲线都从 0 到 1；第 50 层已送到 93%，能读成词要到第 58 层才一半。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P25：逐层的"已到达"（蓝）与"可读成词"（橙）两条曲线，L50 已到达 93%，可读到 L58 才一半、L62 最高；n = 1,186 / 6,841。

## P47 · leader p47 · HTML v71 p98 · main pptx S102–S103 (v22v) — Appendix · Finding 4（路线细节）

**要说的话（一句英文一句中文）**
The route in detail: each bar is how much one swapped part brings back; no single part brings back everything.
路线细节：每根柱子是单换一个部件能找回多少；没有哪个部件能找回全部。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P21：路线示意，attention L48 单换 24%，MLP L52 / 56 单换 18% / 23%，名字格 61% → 84%（L48 → L52），n = 1,186。

## P48 · leader p48 · HTML v71 p100 · main pptx S105 (v22v) — Appendix · the corridors (18b item 2)（走廊）

**要说的话（一句英文一句中文）**
The corridors: each bar is the share of the signal lost when one attention edge is closed for four layers; the biggest, name from title, is about 3.4%.
走廊：每根柱子是在 4 层里关掉一条注意力边时损失的信号比例；最大的“名字 ← 标题”约 3.4%。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P21：在一个 4 层窗口里只切断一条注意力边（所有头），信号 S 损失的比例；锁定判据在 6 个窗口中 3 个成立（L44–47 +1.9%、L48–51 +3.4%、L52–55 +2.2%），每次都是"名字 ← 标题"，L56 起损失 ≈ 0；一条走廊最多只运 3.4%；稳健：11 个错开窗口中 7 个成立（起始层 42–54，覆盖第 42–57 层），包括主跑的三个，没有别的边赢，最大损失 3.5%（L48–51）；n = 600 篇。

## P49 · leader p49 · HTML v71 p101 · main pptx S106 (v22v) — Appendix · the desk (18b items 6, 4)（书桌逐层）

**要说的话（一句英文一句中文）**
The desk floor by floor: in layers 57 to 61, removing the desk loses about 11 to 14% per layer, removing attention almost nothing.
书桌逐层：第 57 到 61 层，拿掉书桌每层损失约 11% 到 14%，拿掉注意力几乎没有。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P26：第 6 项逐层找回比例表（MLP 全部、名字部分、随机、其余、attention，L52–56，描述性）；第 4 项 L57–61 逐层损失表（MLP 每层 11.4%–13.7%，attention ≈ 0，MLP − attn 均值 +0.040 [0.036, 0.045]，锁定判据成立，已定论 settled），n = 600。

## P50 · leader p50 · HTML v71 p52 · main pptx S56 (v22v) — Appendix · map（层图）

**要说的话（一句英文一句中文）**
Every measurement on one ruler: each row marks where that step happens, from title facts by layer 16 to the name at 57 to 61.
所有测量放在一把尺子上：每一行标出这一步发生在哪里，从第 16 层前的标题事实到第 57 到 61 层的名字。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P31：所有按层测量放在同一把尺子上的完整层图（标题事实 ≤ L16，一半 L45 / 全部 L50 到达，L52 起阻断几乎无代价，名字 L57–61 上升最快），n = 每行 518–9,108。

## P51 · leader p51 · HTML v71 p106 · main pptx S113 (v22v) — Appendix · shelf map (18b item 1)（书架格子图）

**要说的话（一句英文一句中文）**
Shelf map: each cell shows the first layer where a locked rule passes; only scattered small cells pass, so there is no clear earlier shelf.
书架格子图：每格写第一个满足锁定规则的层；只有零散的小格子过线，所以没有清楚的更早书架。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P31：3 种读法 × 2 种名字部分 × 9 个位置的格子，每格写第一个满足锁定规则的层；54 个组合里 15 个过线，效应 +0.008 到 +0.049，未做多重比较校正 → 没有清楚的"更早书架"，n = 600。

## P52 · leader p52 · HTML v71 p38 · main pptx S39–S40 (v22v) — Appendix · How the pieces fit（检验矩阵，第 1 页：H1 + H2）

**要说的话（一句英文一句中文）**
How the tests fit together: each row is one test, each column one picture; a tick supports it, a cross weakens it.
各个检验怎么拼在一起：每一行是一个检验，每一列是一种图景；打勾是支持，打叉是削弱。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**当时的 H2 判定：部分支持**（以下是当时的讲法；现在的 H2 总判定见第 19 页）

**备查（不念）：** 2026-11-24 结果更新（单一来源 27_v67/canonical_matrix.md）：表格按假设分组重排为 28 行（H1 5、H2 12、H3 5、写出步骤 5 + 1 行组标题）；按用户 2026-11-24 批准分成两页：本页 H1 + H2 共 17 行，下一页（第 53 页）H3 + 写出步骤 11 行，两页都保留总结行；新加：格式锁定检验 H1 ~（L56 是切掉注意力汇点的假象）、L56 换 ":" 状态 H1 (✓) −0.03、换问法后 probe 仍可读 H1 (✓) T 0.24–0.41、罕见 vs 常见词 H2 ✗ 0.162 vs 0.027、认得 / 引用多 H2 ✗、方差分解 H2 ✗ identity ≈ 0、L8 姓氏锁定检验 H2 (✓) +0.046、差值方向分析 H3 ~ ≤ 7%、注入作者方向 H3 (✓) 2.5% → 9.7%；写出步骤：L57–L61 MLP 写名 ✓ +0.040、加强已到达信号 ✗、给首字母 ✓ 4.0% → 15.2%、晚期压制 (✓) 约 1/8、方向不对称 ✗ −0.032。改格：":" 槽 ✓ 3.0× L40 → (✓) 4.7× → 2.2×；顶词 ~ 加 28–64%；标题处论文属性 ✓ R² 0.38 → ~；同标题 3 问法、换问法、跨问法找同一论文 → ~（天花板 cos 0.998）；改写标题 ~ 0.897 → ~ 文本模型 60%；编造标题 (✓) → ✗ φ 0.75；只换论文事实子空间 R_id 0.005 → 0.004（全部作者重拟合）。“Together” 行改为与三张判定卡一致：H1 降级（冒号处读问题，定格式的层定不下来）；H2 意义而非论文身份，一个小的锁定例外（L8 姓氏信号，判定见第 19 页）；H3 同尺度支持，效应小、相关性证据；瓶颈在写出步骤。下面 2026-11-23 的记录保留作历史。
**备查（不念）：** 2026-11-23：代号列改为白话短词（question swap = X1、part swap = X2、reworded = X3、title decode = X4、match paper = X5、title probe = E4b、same scale = 补充 17、made-up title = 补充 20；表头 code → tag）。“Together” 行改为：H1 成立于冒号和名字位置（哪一层定格式定不下来）；H2 不是一般意义上的论文身份，有一个小的锁定例外（第 8 层姓氏信号，判定原文见第 18 页）；H3 同尺度下支持。旧的 “Together” 行原文：H2 → partly supported (C35): a real-title extra exists (R̄_T +0.11), mostly meaning (φ_T 0.75); it sits on rare words (add. 24 …), is not larger for recognised papers and smaller for more-cited ones (add. 22); wording vs made-up-title penalty open (p. 41)。
支撑正文 P8：每个检验（M1–M4、X1–X5、E4b、add. 17、add. 20）对 H1 / H2 / H3 的判定矩阵（支持 / 部分支持 / 削弱 / 分不清）；新加的 add. 20 一行（意思相同的虚构标题）：H2 部分支持（锁定：R̄_T > 0 且 φ_T ≥ 0.5；φ_T 0.75，R̄_T +0.11）。每个 ✓ / ✗ / (✓) / ~ 旁加一个小灰字 = 这一格最重要的一个数，出处：M4 × H3 ✗ −0.058 L48（C16，作者提示 lens 名字位置 target − control，b2_f1team_report.md）；M2 × H2 ✓ R² 0.38（C13，标题位置 probe 读年份 L16 R² 0.383 [0.362, 0.403]，M2_teamci.csv）；M3 × H2 ✗ −0.03…−0.06（C06，年份迁移 T − T(L4)，L16–L40，m3_report.md）；":"（M3, X1）× H1 ✓ 3.0× L40（C23，":" 处换问法 / 换论文的移动比，L4 4.7、L40 3.0、L48 2.2，x1_similarity.md）；X1 × H2 ✓ R 0.93 L40（替换恢复 0.933，全部作者，测试 582 对，x1_report.md）；X3 × H2 ~ 0.897（C14，改写标题行为恢复比 [0.868, 0.926]，b1_xall_report.md）；X4 × H2 ✗ L8 < L40（C15，第一作者 L8 +0.046 早于年份 L40 +0.013，x4_report.md）；X4 × H3 ~ +0.018 L8（C15 / C21，Qwen 名首 token L8 +0.018，BERT 文本基线 +0.088 不更弱）；X2 × H2 ✗ R_id 0.005（x2_report.md：S_id 在 L40 只搬 0.005，随机 0.003，完整替换 0.920）；X2 × H3 ~ +0.032（C22 下 X2 子项，全部作者重拟合 R_auth +0.032 [0.026, 0.039]，约完整替换的 7%，b1_xall_report.md）；E4b × H3 (✓) +0.052 L24（C09，标题位置 probe target − control [0.017, 0.089]，b1_e4b5_report.md）；add. 17 × H3 ✓ +0.062 L48（C22，probe − J-lens target − control [0.041, 0.081]，h3_samescale_paired.csv）；add. 20 × H2 (✓) φ 0.75（C35，φ_T 0.751 [0.723, 0.778]，a20_report.md）。没有加数字的两格：M1 × H1 ~（读标签顶词只是定性描述）；X5 × H2 ✗（跨问法检索没有一层高于 L4，没有单一代表数）。总结行改为 H2 → partly supported (C35)，H3 → supported on the same scale (add. 17)。

## P53 · leader p53 · HTML v71 p38 · main pptx S39–S40 (v22v) — Appendix · How the pieces fit（检验矩阵，第 2 页：H3 + 写出步骤）

**要说的话（一句英文一句中文）**
The second half of the table: the hidden-author tests and the writing step.
表的后半部分：隐藏作者的检验，以及写出名字这一步。
The author information is there on the same ruler, but small; and the name gets stuck at the writing step.
作者信息在同一把尺子上看得到，但很小；名字卡在写出这一步。

**备查（不念）：** 本页是检验表的第 2 页（用户 2026-11-24 批准分页；单一来源 27_v67/canonical_matrix.md）。H3：作者提示 lens ✗ −0.058 L48；标题位置 probe (✓) +0.052 L24；同尺度 ✓ L40 +0.021、L48 +0.062；差值方向分析 ~（没有主成分超过 7%，作者方向上 6–7%）；注入作者方向 (✓) 2.5% → 9.7%（主要是写入通道）。写出步骤：L57–L61 MLP − attention ✓ +0.040；加强已到达信号 ✗（写出率不变）；给首字母 ✓ 4.0% → 15.2%；晚期压制 (✓) 约 1/8（12.8% vs 9.1%）；方向不对称 ✗ R2 −0.032 [−0.047, −0.016]。总结行与第 52 页相同。

## P54 · leader p54 · HTML v71 p95 · main pptx S99 (v22v) — Appendix · Test: word-readers (M1, M4)

**要说的话（一句英文一句中文）**
Word-readers: the share of times the true name is the top word stays near zero in the middle and appears only near the top.
读词工具：真名字是顶词的比例在中间层接近 0，到顶部才出现。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：读标签工具在中间层看到的是标点，名字到顶层才出现（正确名字是顶词的比例 L52 0.1%、L62 2%；作者提示 lens 只在 L62 有 +0.238 的论文特有差距）。

## P55 · leader p55 · HTML v71 p36 · main pptx S37 (v22v) — Appendix · Test: paper facts (M2)

**要说的话（一句英文一句中文）**
Paper facts at the title: higher means a trained detector reads the year better; it is already readable by layer 16.
标题处的论文属性：越高表示训练的检测器越能读出年份；第 16 层就读得出了。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：在标题处训练的检测器能读出年份、引用、领域（年份 R² 从 L16 0.38 升到 L52 0.56，BERT 0.24），支持 H2。

## P56 · leader p56 · HTML v71 p51 · main pptx S55 (v22v) — Appendix · Test: three questions (M3)

**要说的话（一句英文一句中文）**
Three questions, one title: higher means the states are more alike; they are alike, but no more than the words alone already make them.
同一标题三种问法：越高表示状态越相似；确实相似，但不超过文字本身就能做到的程度。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：同一标题三种问法下状态相似（迁移 ≥ 0.92），但不超过只看文字的 L4 水平，不支持 H2。

## P57 · leader p57 · HTML v71 p51 · main pptx S55 (v22v) — Appendix · Test: the ":" slot (M3, X1)

**要说的话（一句英文一句中文）**
The colon slot: above 1 means a new question moves the state more than a new paper; it does, three to five times more.
冒号格：大于 1 表示换问题比换论文更能移动状态；确实如此，多 3 到 5 倍。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**备查（不念）：** 2026-11-23 加一句：哪一层把格式定下来，目前定不下来（第 32 页）。
支撑正文 P8：冒号处换问题让状态移动是换论文的 3–5 倍（L4–L40），支持 H1（冒号和名字位置）。

## P58 · leader p58 · HTML v71 p51 · main pptx S55 (v22v) — Appendix · Test: question swap (X1)

**要说的话（一句英文一句中文）**
Question swap: near 0 means a title state from a different question works just as well; the difference stays within about 0.02.
换问题替换：接近 0 表示用别的问题下的标题状态效果一样；差别在约 0.02 以内。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：换入不同问题下的标题状态，作者找回效果差不多（L24–L48 差别 ≤ 0.02，全部作者只在 L48 有 +0.024），支持 H2。

## P59 · leader p59 · HTML v71 p73 · main pptx S77 (v22v) — Appendix · Test: reworded title (X3)

**要说的话（一句英文一句中文）**
Reworded title: higher means the reworded title stays closer to the original; it does, but a text model that only sees meaning does that too.
改写标题：越高表示改写后的标题更接近原题；确实如此，但只看意思的文本模型也能做到。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：改写标题在中间层更接近原题（L36 +0.16），保留约 90% 的作者偏好，但这里分不清"意思"和"哪一篇"；后来补充登记 20 用虚构标题分开了：意思给四分之三，真实论文多出 +0.11（p. 41）。

## P60 · leader p60 · HTML v71 p73 · main pptx S77 (v22v) — Appendix · Test: decode from the title (X4)

**要说的话（一句英文一句中文）**
Decode from the title state: the earliest layer where each answer can be decoded; the first author comes out at layer 8, the year only at 40.
从标题状态解码：每种答案最早能解出来的层；第一作者在第 8 层，年份要到第 40 层。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

**备查（不念）：** 2026-11-23 加一句：在 6,048 篇新论文上的锁定后续检验——一个小的姓氏信号在配对主题后仍然存在（第 18 页）。原来“削弱 H2”的判定针对“年份比作者晚出现”的顺序，仍然保留。
支撑正文 P8：从标题状态解码，第一作者在 L8 就出来、年份要到 L40，顺序与 H2 预测相反，削弱 H2；单看不足以支持 H3。

## P61 · leader p61 · HTML v71 p105 · main pptx S111–S112 (v22v) — Appendix · Test: swap a small part (X2)

**要说的话（一句英文一句中文）**
Swap a small part: 1 would mean that part carries everything; the paper-facts directions move almost nothing.
只换一小部分：1 表示这部分就带着全部；论文属性那几个方向几乎什么也没搬动。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P8：只换"论文属性"方向几乎搬不动（0.005，随机 0.003，整体 0.920）；作者方向 0.032（约占整体 7%），H2 不支持，H3 过了书面规则但太弱不计。

## P62 · leader p62 · HTML v71 p103 · main pptx S109 (v22v) — Appendix · Test: same-ruler check (H3)

**要说的话（一句英文一句中文）**
Same-ruler check: above 0 means the scanner sees more than the label reader; +0.021 at layer 40 and +0.062 at layer 48.
同尺度检验：大于 0 表示扫描器比读标签看到更多；第 40 层 +0.021，第 48 层 +0.062。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P22：同尺度锁定检验原页，检测器比读标签多 +0.021（L40）和 +0.062（L48），区间都 > 0（4,654 篇，补充 17 第 2 项）。

## P63 · leader p63 · HTML v71 p102 · main pptx S107–S108 (v22v) — Appendix · Layer by layer (H3)

**要说的话（一句英文一句中文）**
Layer by layer: above 0 means the scanner sees more; it stays above 0 in the middle layers and the gap closes at layer 56.
逐层看：大于 0 表示扫描器看到更多；中间层都在 0 以上，到第 56 层差距消失。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P22：逐层的 probe − J-lens（L32 +0.025，L40 +0.021，L48 +0.062，L52 +0.053，L56 +0.008 不显著）及 probe − logit lens 对比。

## P64 · leader p64 · HTML v71 p102 · main pptx S107–S108 (v22v) — Appendix · By name part (H3)

**要说的话（一句英文一句中文）**
By name part: higher means more paper-specific signal in that piece; every piece has some, the first pieces of given name and surname most.
按名字部分：越高表示这一块带的论文特有信号越多；每一块都有，名和姓的第一块最多。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P22：按名字部分的 probe 信号（L40：名首 0.140，姓首 0.069，名后续 0.056，首字母 0.045，姓后续 0.037），每部分都带一些论文特有信号。

## P65 · leader p65 · HTML v71 p104 · main pptx S110 (v22v) — Appendix · directions (exploratory)（方向：认得出的差别落在很多安静的方向上）

**要说的话（一句英文一句中文）**
Exploratory: the bar is the share of the recognised-minus-not difference on each direction; it spreads over many quiet directions, not the author axes.
探索性：柱子是“认得出 − 认不出”的差别落在每个方向上的比例；它分散在很多安静的方向上，不在作者轴上。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P22（探索性，事后）：名字位置每篇“真标题 − 假标题”的状态差散在很多方向上：50% / 80% 方差第 40 层要 31 / 234 个方向，第 48 层 25 / 151 个；认得出 − 认不出的平均差在第一个方向上的比例从第 40 层的 1% 升到第 48 层的 50%（前 10 个方向 60% → 81%）。它和作者 probe 方向的余弦约 0.12–0.15（随机 ±0.014），年份约 0.01、引用数 0.06、领域 ≤ 0.08，17 个方向合计只占 7.1% / 6.1%。图旁公式：Δ = d̄_T − d̄_C，d = h_true − h̄_false；y = λ_k / Σ_j λ_j；n = 4,654 篇（3,130 + 1,524），姓的第一个 token。来源 381_stage13/summary_explore_pca_np_20261120/report.md；summary_explore_dir_overlap_20261121/report.md。

## P66 · leader p66 · HTML v71 p119 · main pptx S126 (v22v) — Appendix · Why it can't say it（说不出：全部名字部分）

**要说的话（一句英文一句中文）**
Why it can’t say it, all name parts: the initial gets the smallest push; giving it raises correct writing in recognised papers from 4.0% to 15.2%.
说不出，全部名字部分：首字母得到的推力最小；给出它后，认得出的论文写对的比例从 4.0% 升到 15.2%。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P27（也支撑 P29）：真标题对五个名字部分的推力，首字母最小却通常最先写；B（给首字母 +0.085，列表 / 只写姓格式不显著）、D（其他作者 +0.17，网络联想）；编造名：大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）；合作者只占 4.0%（随机 1.3%），探索性（n = 40,219 个名字，8,872 篇）。
底部新增一行探索性补充：A 组写对至少一位完整作者 F0 4.0% [2.5, 5.6] → F4 15.2% [12.5, 18.0]，仍有 85% 一个都写不出，首字母只修好约 12% 的失败；B 组 0.5% → 3.2%（391_groups/summary_a16_20261115/b_rates.csv）。

## P67 · leader p67 · HTML v71 p128 · main pptx S136 (v22v) — Appendix · pushing harder (add. 21)（用力推：6 种推法的细节）

**要说的话（一句英文一句中文）**
Pushing harder in detail: the vertical line is no push at 3.8%; none of the six settings clearly beats it.
用力推的细节：竖线是不推时的 3.8%；6 种推法没有一种明显超过它。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P28：6 种推法（L48 / L52 × 放大 1、2、4 倍）下认得出的论文写对作者的比例，橙色 = 放大自己的信号，灰色 = 放大另一篇论文同样强度的信号，竖线 = 不推时 3.8%；没有一种明显超过竖线。锁定规则：自己必须同时胜过不推和另一篇论文（Holm 校正 6 格）；结果自己 − 不推 −0.010 到 +0.005，Holm 区间都含 0；自己 − 另一篇最大 +0.020 [0.003, 0.037]，Holm p 0.15 → 不支持。真名字名次 L52 ×4 −0.102 [−0.113, −0.092]，与推另一篇论文相近。局限：单一模型；两层、三种强度；只推提示尾部；贪心解码；与 Stage 10 名次一致比例 0.69 < 0.75（WARN，保留）。公式 h′ = h + β·Δ，Δ = h_true − 5 个假标题均值；n = 1,200 篇（391_groups/summary_a21/）。

## P68 · leader p68 · HTML v71 p125 · main pptx S132–S133 (v22v) — Appendix · Finding 5 · exploratory（发现 5 细节）

**要说的话（一句英文一句中文）**
Back-up for the made-up-name signal: above 0.5 means it can tell real from made-up; hesitation gives 0.71, the middle layers 0.78.
编造名字信号的备份：高于 0.5 表示分得开真假；犹豫程度给 0.71，中间层给 0.78。

**备查（不念）：** 以下是上一版的本页原文（页码已改为新编号）。

支撑正文 P29：置信度 0.71 vs 中间层 0.78，probe 只在 L40–52 领先（L40 +0.059，L48 +0.062，L52 +0.050）；已写出的作者在内部排名高于未写出的（+0.20，约从 L54 起出现）。
