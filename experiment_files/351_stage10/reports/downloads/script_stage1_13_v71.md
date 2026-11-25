# Qwen3-32B 把论文作者放在哪里？—— Stage 1–13 逐页讲稿（按 HTML deck 新顺序）

每页两块：**要说的话**（念出来，一句英文一句中文，约 1 分钟）和 **备查（不念）**（完整数字、CI、n、公式、证据强度、出处、内部编号；上一版讲稿的全文和当时各检验的判定原样保留在这里）。用户本人的方括号笔记逐字保留在原来那张幻灯片的页里。版本与维护说明见修改日志。

比喻全程只用一套：索书号（这是哪一篇论文）vs 书脊上的主题（标题的意思）；编造标题 = 一张写着同样主题、但不属于这本书的卡片。

## 总览：一个问题，四条论证线（上一版讲稿开头的总览，备查，不念）


**问题：** Qwen3-32B 把一篇论文的作者放在网络的什么地方？它能不能把作者说出来？特别是那些"认得出作者名单、却写不出作者"的论文，作者信息是在中间层就形成了，还是只在最后才出现？

**两个阶段：**
- Stages 1–9（深色页）：小样本（20 → 50 → 200 篇），先找信号、再想办法推翻它。
- Stages 10–13（浅色页）：全队列（9,108 篇、149,999 个名字 token），先定位、再做干预。

**四条论证线（每条都在缩小可能的解释范围）：**
- **A · 是不是关于"这篇"论文？** 信号是论文特异的，还是只是名字好猜？（Stage 5、7.2、7.3、8 → Stage 10–11 的 title-specific 信号、名字先验、probe；补充 19 曝光门槛）
- **B · 读出工具能看到什么？** logit lens、J-Lens、probe 各自能看到什么？（Stage 3、7.4、8、9 → lens 对比、线性 probe）
- **C · 哪一层？** 信息什么时候出现、什么时候被使用？（Stage 4、7.2、7.3、8 的 L56 → 细层、patching、knockout）
- **D · 哪个 token？** 名字或提示里哪一部分在承载信息？（Stage 6、7.1 → 名字格式、标题后 token、合作者链；补充 16 答案格式）
- Stage 12–13 补上路线（attention → MLP）、标题用词、意思相同的虚构标题（补充登记 20）、模型自己编出来的名字。

**结论状态标签说明：**
- **定论**：全队列、主分析、并被多处结果反复印证（通常是第 64 页"小样本 vs 全队列"表里标 confirmed / consistent / resolved 的条目）。
- **初步（较稳但有前提）**：方向稳定，但有明确的前提或局限（单个假标题、只打第一个 token、事后检查等）。
- **探索性**：小样本、反复查看后选层、未做多重比较校正，或明确未预注册。
- **描述性**：只报告数值，没有锁定判据。
- 预注册（或锁定判据）的结果写"预注册判据成立 / 不成立"；判据在看过数据后才锁定的，单独注明。

---


# Part 0 · Opening (1–4)

## P1 · HTML v75 p1 · pptx S1 (v22z) — Stages 1–13: where Qwen3-32B holds a paper’s authors

**要说的话（一句英文一句中文）**
This talk asks one question: where does Qwen3-32B keep the authors of a paper, and why does it so often fail to say them?
这次报告只问一个问题：Qwen3-32B 把一篇论文的作者放在哪里，为什么它常常说不出来？
We worked in two phases. First, small samples of 20 to 200 papers, where the job was to find a signal and then try hard to break it.
我们分两个阶段做。第一阶段是 20 到 200 篇的小样本，任务是先找到信号，再想办法推翻它。
Then the full cohort: 9,108 papers and about 150 thousand name tokens, where the job was to locate the signal and then intervene on it.
第二阶段是全队列：9,108 篇论文、大约 15 万个名字 token，任务是先定位，再动手干预。
The first thing to settle is whether we can measure this per paper at all, and trust the numbers.
第一件要定下来的事，是能不能逐篇测出来，而且数字可信。
So let me first show the one question and the lines of argument we used.
所以先看这个问题，以及我们用的几条论证线。

**备查（不念）· 上一版讲稿本页全文（原第 P1 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 封面，交代全片的两段结构。左边是 Stages 1–9：小样本（20 → 50 → 200 篇，对应 Stage 4、Pilot50、Stage 8），任务是"找到信号，再设法推翻它"。右边是 Stages 10–13：全队列 9,108 篇论文、149,999 个名字 token，任务是"先定位，再干预"。

**过渡：** 先用一页说清楚整个报告围绕的一个问题和四条论证线。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(Stage 10 cohort: papers.parquet, name_tokens.parquet)

## P2 · HTML v75 p2 · pptx S2 (v22z) — One question, four lines of argument

**要说的话（一句英文一句中文）**
Here is the plan of the whole talk on one page.
这一页是整个报告的路线图。
Each line asks a narrower question: is the signal about this paper, which readout can see it, at which layer it appears, and which token carries it.
每一条线问一个更窄的问题：信号是不是关于这篇论文，哪种读出工具看得到，在哪一层出现，由哪个 token 承载。
Dark pages are the small samples, light pages the full cohort; a purple tag marks a comparison between the two.
深色页是小样本，浅色页是全队列；紫色标签表示两个阶段的对比。
The short answers are on the right: yes, it is about this paper, but mostly through the meaning of the title; a probe reads it earlier than the lens.
右边是简短答案：是的，信号是关于这篇论文的，但主要通过标题的意思；probe 比 lens 更早读出来。
The next page puts these answers together as one picture.
下一页把这些答案拼成一张图。

**备查（不念）· 上一版讲稿本页全文（原第 P2 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 提出核心问题："Qwen3-32B 把论文作者放在哪里？它能不能说出来？"然后列出四条线：A（是不是这篇论文）、B（读出工具）、C（哪一层）、D（哪个 token），每条线标出小样本阶段（1–9）和全队列阶段（10–11）分别对应的 Stage。颜色约定：深色页 = Stages 1–9，浅色页 = Stages 10–11，紫色标签 = 两阶段对比。各条线里还穿插了 A 的曝光门槛、D 的答案格式和合作者链，以及 12–13 的路线、标题用词、编造的名字。

**过渡：** 先看两个阶段的设计到底有哪些不同，以及为什么要改。

## P3 · HTML v75 p3 · pptx S3 (v22z) — Keys and shelves

**要说的话（一句英文一句中文）**
This page asks what the four lines add up to.
这一页问：四条线加起来说明了什么？
Think of a library. The question is whether the book is on the shelf at all, or whether it is there but cannot be fetched.
把模型想成一座图书馆。问题是：这本书到底在不在书架上，还是在，但取不出来。
First, the book is on the shelf: the true title beats the false titles, and a probe at the title already carries paper-specific author information.
第一，书在书架上：真标题胜过假标题，标题位置的 probe 已经带着这篇论文特有的作者信息。
Second, the title is carried into the name positions mainly between layers 40 and 50, and after layer 52 blocking it costs almost nothing.
第二，标题主要在第 40 到 50 层被送进名字位置，过了第 52 层再阻断几乎没有代价。
Third and fourth, the information sits at the names in a form the vocabulary readout cannot see, and the late layers write it out.
第三、第四，信息停在名字位置，但形式是词表读不出来的，最后由后面的层写出来。
So the problem is not that the book is missing; it is getting it off the shelf and saying it. Next, how to read the rest of the deck.
所以问题不是书不在，而是把它取下来、说出来。下一页说明后面的幻灯片怎么看。

**备查（不念）· 上一版讲稿本页全文（原第 P62 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 比喻：书在不在书架上？还是钥匙取不出来？四步：
1. **书在书架上吗？在。** 真标题胜过假标题（L62 约 0.44，§6.9）；标题 token 上的 probe 从 L8 起就能读出论文特异的作者信息（可能来自标题文本本身；和识别相关的上升从 L24 开始）。（A、B 线 · Stage 5、7.3、8D、10、11）
2. **钥匙 = 标题，主要在 L40–L50 进入名字位置。** L45 时完成一半；最大一步是 L47→L48，+0.26 [0.253, 0.272]。整个提示：L48 为 0.82，L52 起约 1.0；只 patch 名字位置 0.613 → 0.841（false_0 0.61 → 0.85）；':' ≤ 0.181（0.17）（E1，P1 五个标题均值；1,186 篇）；L52 之后 knockout 几乎没有代价。（C 线 · Stage 11、12 P1）
3. **书在但卡住了？** 没有可读的标签（lens），但"条码扫描器"（probe）能读到微弱信号（H3：同一尺度上得到支持）。lens：target − control 在 L24–L40 约 0，L48 略负（−0.04 到 −0.05），只在 L57–61 增长（输出 +0.21，§6.4）。在同样 9,137 个名字 token 上，probe − J-lens 的 target − control：L40 +0.021 [0.008, 0.034]，L48 +0.062 [0.041, 0.081]（补充 17 第 2 项；只看姓氏第一个 token）。（A、C 线 · Stage 7.2、10）
4. **哪个书架？两个都用，有先后。** attention 在 L48 把标题带进来（0.237；false_0 0.231；大小和 L47→L48 那一步吻合，这只是吻合，不是检验）；MLP 在 L52–56 接手（0.181、0.226；false_0 0.178、0.224）（P2 五个标题均值）。单层 patching 只给出下界；MLP 这一步是否是记忆查找，目前还分不开。（Stage 12 P2）

**注意：** 读出没找到 ≠ 不存在。Stage 13：':' 和名字位置承载任务信息；标题位置承载论文属性和超出字面的含义，但还没有证明那就是论文身份。补充 18b 延伸了第 ④ 步：L52–L56 的 MLP 携带论文信息而不是名字方向（描述性 → 第 76 页）；L57–L61 由 MLP 写入（定论（锁定判据成立） → 第 77 页）；第 ③ 步里名字之前的早期痕迹仍然很弱（探索性 → 第 72 页）。

**结论状态：** 综合页，各步状态如上：①② 为定论 / 初步；③ H3 在同一尺度上为预注册判据成立（补充 17）；④ 为初步（单层 patching 是下界）。

**过渡：** 回头看小样本阶段教会了我们要警惕哪些陷阱。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$ · $R(l)=\mathrm{mean}(\mathrm{patched}-\mathrm{false})/\mathrm{mean}(\mathrm{true}-\mathrm{false})$；② n = 9,108 papers (lens) · 1,186 papers (patching)；③ spec > 0: the true title ranks the author higher than false titles / R ≈ 1: fully restored; R ≈ 0: nothing restored；原 “How computed” 段：How computed: spec = true − mean(false_0..4); recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p]; T − C pooled within bin · 9,108 papers (lens) / 1,186 papers (E1, P1, P2; P1/P2 averaged over 5 false titles) · source: X3_means.csv, E1_recovery.csv, p12f_mean5.csv；方法细节移到备用页 B16 (slide 111)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(§6.9)
- 出处（原在幻灯片上）：(§6.4)
- 出处（原在幻灯片上）：(P2 5-title mean, p12f_mean5.csv)

**备查（不念）：**
- 原写 “(E1, P1 5-title mean; …)”、“Stage 11, 12 P1”、“Stage 12 P2”、“(addendum 17 item 2; …)”、“Add. 18b:”：E1 = 放回检验，P1 = 单位置 patching，P2 = 注意力 / MLP patching，addendum 17 item 2 = 锁定的名字位置 probe 检验，18b = 后续检验（600 篇）

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** T − C 在同引用档内合并。

## P4 · HTML v75 p4 · pptx S4 (v22z) — How to read this deck

**要说的话（一句英文一句中文）**
Before the results, this page explains how to read every page that follows.
进入结果之前，这一页先说明后面每一页怎么看。
Each result carries a coloured tag. Settled means shown with interventions or the full cohort. Locked means the rule was written down before the run, and the result either passed or failed it.
每个结果都带一个彩色标签。settled 表示有干预实验或全队列支持；locked 表示判定规则在运行前就写好了，结果要么通过、要么没通过。
Descriptive means measured but not decided by a test; exploratory means a clue only, and we never build a conclusion on it.
descriptive 表示只是测量、没有检验来判定；exploratory 只是线索，我们从不用它下结论。
Under every chart there are three grey lines: the formula of the plotted number, the sample size, and one sentence on how to read it.
每张图下面有三行灰字：画出来的数是怎么算的、样本量多少、一句话说明怎么读。
From Part 3 on, each part follows one pattern: a question card, the experiments, a verdict card, and the evidence matrix.
从第 3 部分开始，每部分都是同一个结构：问题卡、实验、判定卡、证据矩阵。
With that, let's look at how the study was set up.
有了这些，我们先看研究是怎么搭起来的。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

How to read How to read this deck Now asking: what do the coloured tags, the grey lines and the cards mean? Evidence tags: every result carries one settled shown with interventions or the full cohort; not in doubt locked · supported a rule fixed before the run, and the result passed it locked · not supported a rule fixed before the run, and the result failed it descriptive measured, but no test decides it exploratory a clue only: looked at after the fact fairly solid several checks agree, no locked test Caveat: exploratory results are never used for a conclusion ; they are marked “clue”. Three grey lines under every chart: 1 the formula of the plotted number (LaTeX) 2 the sample size n (LaTeX) 3 one reading, e.g. “R ≈ 1: fully restored” Parts 3–6 follow one pattern: question card → experiments → verdict card → evidence matrix Names: plain test names on the slides; codes and file names are in the Glossary, slide 148, and in the script. Method figures: how to read them, slide 12. So (section): the setup is fixed; next, the first finding: the model picks the true author list in multiple choice for papers whose authors it cannot write (Part 2). descriptive

# Part 1 · Setup and methods (5–24)

## P5 · HTML v75 p5 · pptx S5 (v22z) — Pilot design

**要说的话（一句英文一句中文）**
This page asks why the design changed between the two phases.
这一页问：为什么两个阶段的设计不一样？
The pilot looked mostly at the first token of the first author, against one or a hundred false names, and picked layer 56 after looking several times.
小样本阶段主要只看第一作者的第一个 token，跟 1 个或 100 个假名字比，第 56 层是反复看过之后才选的。
The full cohort scores every author and every token against the whole vocabulary, uses five matched false titles, and reports every layer.
全队列阶段给每个作者、每个 token 在整个词表里打分，用 5 个匹配的假标题，并报告所有层。
A quick check that the two phases compare like with like: with only papers where no author was written, the gap at the output is 0.199, against 0.207 for the full groups.
核对两阶段比较的是同一类东西：只用一个作者都没写出的论文，输出层差距是 0.199，全组是 0.207。
So the move to the full cohort fixed the weak points of the pilot. Next, the two ways of grouping the same papers.
所以改用全队列，补上了小样本的弱点。下一页看同一批论文的两种分组方式。

**备查（不念）· 上一版讲稿本页全文（原第 P3 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 小样本阶段（Pilot50 / Stage 8，50 和 200 篇）主要只看第一作者的第一个 token，打分方式是金标作者对 1 个或 100 个假名字的 logit margin / 胜率；A/B 两组都是 R0，成对匹配；错误标题是 1 个交叉标题或 20 个打乱标题；L56 是反复查看之后才选出来的。全队列阶段（Stages 10–11）用全部 9,108 篇、每个作者、每个 token，按整个词表排名打分（log10(1/rank)）；target = A + C，control = B + D（R0 + R1），在引用档内比较；用 5 个匹配的假标题加"无标题"；报告所有层并补了细层；分析前先做 parity 和 Stage 6 交叉核对。

**关键数字和 CI：**
- 只用 R0（A vs B，和 pilot 一样）时，输出层差距 +0.199，target vs control 为 +0.207（Stage 10，最终层 L63，R0 3,423 vs 2,151；§6.13），各层形状一样。
- n = 50 / 200 篇（Pilot50 / Stage 8）· 9,108 篇（全队列）。

**结论状态：** 方法页（设计说明）。

**过渡：** 两个阶段的分组口径不同，下一页把同一批论文的两种分组放在一张表里对照。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{score}=\log_{10}(1/\mathrm{rank})$ · $\mathrm{target}=A+C,\ \mathrm{control}=B+D$；② n = 50 / 200 papers (pilot / Stage 8) · 9,108 papers (full cohort)；③ score = 0: true name ranked first；原公式框：score = log 10 (1/rank), target = A + C, control = B + D n = 50 / 200 papers (Pilot50 / Stage 8) · 9,108 papers (full cohort)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(pilot50_v1.csv, stage8_papers.csv)
- 出处（原在幻灯片上）：(papers.parquet)
- 出处（原在幻灯片上）：(Stage 10, final L63, R0 3,423 vs 2,151; §6.13)

## P6 · HTML v75 p6 · pptx S6 (v22z) — Same papers, two ways of grouping

**要说的话（一句英文一句中文）**
This page asks: are the small-sample groups and the full-cohort groups the same kind of papers?
这一页问：小样本阶段的分组和全队列的分组，是不是同一类论文？
We cross two behaviours: open recall, whether the model writes any true author, and multiple choice, whether it picks the true author list.
我们把两种行为交叉：开放回忆，即模型有没有写出真作者；多选题，即它能不能选中真作者名单。
The pilot compared A with B: both write no true author, and they differ only in recognising the list. That is purely “knows but cannot say”.
小样本比较 A 和 B：两组都写不出真作者，只在认不认得名单上不同，这就是纯粹的“知道但说不出”。
The full cohort compares target, A plus C, with control, B plus D; the extra 511 partial-recall papers sit almost all on the target side.
全队列比较 target（A 加 C）和 control（B 加 D）；多出来的 511 篇部分回忆的论文几乎都在 target 一边。
So the two phases compare the same kind of papers. Next, where these labels come from.
所以两个阶段比较的是同类论文。下一页看这些标签是怎么来的。

**备查（不念）· 上一版讲稿本页全文（原第 P4 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 用 6,841 篇冻结队列的计数，把"开放回忆"（R0 = 一个真作者都没写出；R1 = 写出部分作者，HR2 > 0.5）和"多选识别"（认得出 = target；认不出 = control）交叉成四格。Stages 1–9 比较 A vs B（都是 R0，对比纯粹是"知道但说不出"）；Stages 10–11 比较 (A + C) vs (B + D)，多出来的 511 篇部分回忆论文几乎都在 target 一侧。

**关键数字和 CI：**
- A = 4,110，B = 2,186，C = 511，D = 34；target = A + C = 4,621，control = B + D = 2,220（Stage 1，351_audit.json）。
- 核对：只用 R0（A vs B）输出层差距 +0.199，target vs control +0.207（Stage 10，最终层 L63，引用档内；§6.13），各层形状一样。
- n = 6,841 篇（冻结队列：4,621 target + 2,220 control）。

**结论状态：** 描述性（计数）；口径核对结论：两阶段比较的是同类对象。

**过渡：** 接下来几页是方法图的图例和样本结构，之后进入各 Stage。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{target}=A+C,\ \ \mathrm{control}=B+D$；② n = 6,841 papers (frozen cohort: 4,621 target + 2,220 control)；③ T − C > 0: recognised papers carry more author signal than unrecognised ones；原公式框：target = A + C, control = B + D n = 6,841 papers (frozen cohort: 4,621 target + 2,220 control)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(Stage 1, 351_audit.json group_counts)
- 出处（原在幻灯片上）：(351_audit.json)
- 出处（原在幻灯片上）：(Stage 10, final L63, within-bin; §6.13)

## P7 · HTML v75 p7 · pptx S7 (v22z) — Cohort and behavioural labels

**要说的话（一句英文一句中文）**
This page asks where the behavioural labels come from.
这一页问：这些行为标签是怎么来的？
From a label package of 9,108 papers we froze an analysis cohort of 6,841.
我们从 9,108 篇的标签包里冻结出 6,841 篇的分析队列。
Recognised means the true list is picked in all four option orders, with the true option averaging at least one half.
“认得”的意思是：四种选项顺序下都选中真名单，而且真选项的平均概率至少一半。
One caveat to keep in mind: even for papers with almost no citations, a quarter pass the strict test, so passing does not prove the model has stored the paper.
有一点要记住：即使几乎没被引用的论文，也有四分之一能通过严格测试，所以通过并不能证明模型记住了这篇论文。
So the labels are useful but noisy. Next, the one fixed model, prompt and score used everywhere.
所以标签有用，但有噪声。下一页是贯穿全程的固定模型、提示词和打分方式。

**备查（不念）· 上一版讲稿本页全文（原第 P7 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 从 10 月 15 日的标签包（9,108 篇）得到冻结的 6,841 篇分析队列。识别"通过" = 4 种选项顺序全对且真选项平均概率 ≥ 0.5；"不通过" = 0–1/4。Pilot50 用种子 35150，保留 Stage 4 的 20 篇再加 30 篇新论文；20 个 A/B 对按领域和引用档精确匹配，再按 |Δyear| + 2·|Δauthors| 配对。选 A vs B 的理由：两组都写不出任何正确作者，只在"认不认得真名单"上不同，正好隔离出"知道但说不出"。

**关键数字和 CI：**
- 全量：A 4,110、B 2,186、C 511、D 34；Pilot50：A 20、B 20、C 7、D 3。
- 注意：0–2 引用档的严格通过率是 25.5%（796 篇；label_README.md 第 8 行），高于计划的 ≤10% 下限，所以"通过"不能证明模型存了这条知识。
- n = 9,108 篇（标签）· 6,841（队列）· 50（Pilot50）。

**结论状态：** 描述性（数据与标签说明）；带标签噪声的局限。

**过渡：** 有了分组之后，下一页固定模型、提示词和打分方式，之后所有结果都在这套设定下测量。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{pass}:\ 4/4\ \mathrm{orders\ right}\ \wedge\ \overline{p}(\mathrm{true})\geq 0.5$；② n = 9,108 papers (labels) · 6,841 (cohort) · 50 (pilot)；③ pass = recognised: picks the true author list in every order；原公式框：pass: 4/4 orders right ∧ mean p(true) ≥ 0.5 n = 9,108 papers (labels) · 6,841 (cohort) · 50 (Pilot50)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(351_audit.json total, four_group_total)
- 出处（原在幻灯片上）：(351_audit.json)
- 出处（原在幻灯片上）：(pilot50_v1.csv)
- 出处（原在幻灯片上）：(796 papers; label_README.md l.8)

## P8 · HTML v75 p8 · pptx S8 (v22z) — One fixed model, prompt and score

**要说的话（一句英文一句中文）**
This page fixes the settings that every later number uses.
这一页定下后面所有数字共用的设定。
One model, Qwen3-32B in bf16, one prompt: “Who are the authors of the paper titled ... ? Authors:”, followed by an author name.
一个模型：Qwen3-32B，bf16；一个提示词：“Who are the authors of the paper titled …? Authors:”，后面接作者名。
We read the hidden states at several layers with a lens, that is, a tool that reads a hidden state as words, and with the real output.
我们在几层上用 lens 读隐藏状态——lens 就是把隐藏状态读成词的工具——同时也看真实输出。
The score is the rank of the true name token among all tokens.
分数是真名字 token 在所有 token 里的排名。
So everything later is measured under these same settings. Next, how the groups and comparisons are built.
所以后面的一切都在同一套设定下测量。下一页看分组和对比是怎么搭的。

**备查（不念）· 上一版讲稿本页全文（原第 P8 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型 Qwen/Qwen3-32B，BF16，revision 9216db57，64 个 block，d = 5,120。读出层 L16、24、32、40、48、56、62 → 目标 L63；读出方式为 public J-Lens、Vanilla（logit lens）和真实最终 logits。位置是最后一个输入位置，上下文上限 512；名字编码为 encode(prompt) + encode(" " + author)。29 个 block 在 GPU，35 个 offload 到 CPU。提示词："Who are the authors of the paper titled "{title}" ({year})? Authors:"。

**关键数字和 CI：**
- 排名 r = 1 + 严格更大 logit 的 token 数；JMRR = 各作者、各 token 的 1/r 均值；Integrated = 7 个源层的平均（不含 L63）。
- 保护措施：检查强制 token ID；J-Lens 和 Vanilla 最终 logit 差 > 0.1 就拒绝这次运行。
- n：每个样本都用这套设定，从 20 篇（Stage 4）到 9,108 篇（Stage 10）。

**结论状态：** 方法页（固定设定）。

**过渡：** 再看 Stage 10 里分组和对比具体怎么构造。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $r=1+\#\{\mathrm{tokens\ with\ a\ larger\ logit}\}$ · $\mathrm{nlr}=\log_{10}(1/r)$；② n = 20 papers (Stage 4) → 9,108 papers (Stage 10), same settings；③ nlr = 0: true name ranked first; −2: ranked 100th；原公式框：r = 1 + #{tokens with a larger logit}, nlr = log 10 (1/r) n = settings for every sample: 20 papers (Stage 4) → 9,108 papers (Stage 10)。

## P9 · HTML v75 p9 · pptx S9 (v22z) — How groups and contrasts are built

**要说的话（一句英文一句中文）**
This page asks how the groups and the comparisons are built.
这一页问：分组和对比是怎么搭起来的？
Four building blocks: the open answer gives the recall level; multiple choice gives recognised or not; five matched false titles per paper; and we only compare within a citation bin.
四个模块：开放回答给出回忆等级；多选题给出认得或认不得；每篇论文配 5 个匹配的假标题；而且只在同一个引用档内比较。
On the chart, HR2 at most one half means at most half of the author slots are written wrongly, which we call recalled.
图上 HR2 不超过一半，表示最多一半的作者位置写错，我们把这叫做“回忆出来了”。
The false titles are matched on field, year, team size and citations, and share no surname with the real paper.
假标题在领域、年份、团队规模和引用数上都匹配，而且和真论文没有共同的姓氏。
So every comparison is recognised against not recognised, against five false titles, inside one citation bin. Next, how we read the model.
所以每个比较都是认得对认不得、对照 5 个假标题、在同一个引用档内。下一页看怎么读模型。

**备查（不念）· 上一版讲稿本页全文（原第 P9 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 四个模块。① 开放回答 → R0/R1/R2：贪心解码、chat template，模糊名字匹配得到 M、H、U，HR2 = (H+U)/(M+H+U)；R2：HR2 ≤ 0.5，R0：M = 0，R1：M > 0；固定规则，没有人工或模型评判。② 多选 → target / control：真名单加 3 个其他论文的真实团队（同领域、团队规模、引用档、年份相近），4 种顺序，从下一个 token 读 p(字母)；target：4/4 且平均 p(true) ≥ 0.5；control：≤ 1/4。③ 每篇 5 个假标题：同领域、保留原年份，按 |dyear|/5 + |dauthors| + |dtitle tokens| + 1.5 |dcitation bin| 最小代价匹配，不共享姓氏，Jaccard ≤ 0.6。④ 统计：target vs control 只在引用档内比较，用每组 ≥ 30 篇的 10 个档，权重 n_t n_c / (n_t + n_c)，对论文做 2,000 次 bootstrap 求 95% CI，敏感性分析去掉 0–4 档。标签来自组长在同一个 Qwen3-32B 上跑的流程，原样使用。

**关键数字和 CI：**
- 79% 是严格档（35,898 / 45,540 对；conditions_manifest.json）。
- n = 9,108 篇 · 45,540 个假标题对（35,898 个严格档）。

**结论状态：** 方法页。

**过渡：** 分组定了，下一页讲怎么从模型里读出作者信号。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $w_b=n_{t,b}\,n_{c,b}/(n_{t,b}+n_{c,b})$ · $\mathrm{HR2}=(H+U)/(M+H+U)$；② n = 9,108 papers · 45,540 false-title pairs (35,898 strict)；③ HR2 ≤ 0.5: at most half of the author slots are written wrongly (= R2, recalled)；原公式框：w b = n t,b n c,b / (n t,b + n c,b ), HR2 = (H+U)/(M+H+U)；原公式框：n = 9,108 papers · 45,540 false-title pairs (35,898 strict)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, 35,898 of 45,540 pairs, conditions_manifest.json)” → “(Stage 10, 35,898 of 45,540 pairs)”；“(Stage 10, §6.2)” → “(Stage 10)”

## P10 · HTML v75 p10 · pptx S10 (v22z) — How we read the model

**要说的话（一句英文一句中文）**
This page asks how we read the author signal out of the model.
这一页问：怎么从模型里读出作者信号？
We take the prompt, read the hidden state at the name, and turn it into a rank for the true name token.
我们拿提示词，读名字位置的隐藏状态，再把它变成真名字 token 的排名。
On the chart, spec above zero means the true title ranks the author higher than the false titles do.
图上 spec 大于 0，表示真标题让作者排得比假标题更靠前。
Because the name and its tokens are identical across the seven title conditions, whatever difference is left belongs to knowing this paper.
因为七种标题条件下名字和 token 完全一样，剩下的差别就只能归于“知道这篇论文”。
So true minus false is our per-paper signal. Next, whether we can trust the code and the scores.
所以“真减假”就是我们逐篇的信号。下一页看代码和分数能不能信。

**备查（不念）· 上一版讲稿本页全文（原第 P10 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 提示词后接一个作者名（例如 "S. Bree"），取第 24、32、40、48、56、62 层的隐藏状态，用 logit lens、3 个 Jacobian lens 和真实输出（L63）读出。分数 = 正确的下一个名字 token 的排名，取 log10(1/rank)：0 = 第 1 名，−1 = 第 10 名。共 7 种标题条件：真标题、5 个匹配假标题、无标题。核心量 title-specific 信号 = 真标题 − 5 个假标题的均值；名字相同、token 相同，剩下的就是"知道这篇论文"。三种 lens 都不改模型权重，只是把各层到 L63 的 Jacobian 在提示词上取平均：public = 557 个 WikiText-103 提示（Neuronpedia）；self100 = 100 个冻结的 WikiText-103 提示；fitA = 另外 100 个 WikiText-103 提示（Stage 9，跳过一个、替换后共 100 个有效）。

**关键数字和 CI：**
- title-specific = nlr_true − mean5 nlr_false。
- n = 9,108 篇 · lens 分别在 557 / 100 / 100 个 WikiText-103 提示上拟合。

**结论状态：** 方法页。

**过渡：** 在看结果之前，先确认这些数字本身可信。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 9,108 papers · lenses fitted on 557 / 100 / 100 WikiText-103 prompts；③ spec > 0: the true title ranks the author higher than false titles；原公式框：title-specific = nlr true − mean 5 nlr false n = 9,108 papers · lenses fitted on 557 / 100 / 100 WikiText-103 prompts。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(n_prompts: 351_stage10/config/lenses.json; Stage 9 final_status.json)” → “(prompt counts: Stage 10 lens settings; Stage 9 final check)”

## P11 · HTML v75 p11 · pptx S11 (v22z) — Can we trust the numbers?

**要说的话（一句英文一句中文）**
This page asks whether we can trust the code and the scores.
这一页问：代码和分数可信吗？
Three checks: the fast code and the slow code give the same logits; the scores match an earlier stage token by token; and punctuation, which should carry nothing, carries nothing.
三项检查：快代码和慢代码给出相同的 logits；分数和早先阶段逐 token 对得上；标点本来不该带信号，结果确实没有。
On the chart, a gap near zero means the two codes agree; the largest gap was 0.37 of a logit, which is bf16 rounding, and the ranks were identical.
图上差距接近 0 表示两套代码一致；最大差距 0.37 logit，是 bf16 舍入，排名完全相同。
One caveat: we raised the tolerance from 0.25 to 0.5 after seeing these rounding gaps, and we keep that as a limitation.
有一点要说明：我们是在看到这些舍入差距之后，把容差从 0.25 放宽到 0.5 的，这一点作为局限保留。
So the measurement holds up. Next, how to read the method figures.
所以测量是靠得住的。下一页说明方法图怎么看。

**备查（不念）· 上一版讲稿本页全文（原第 P11 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 三项检查。① fast = slow：一次前向（fast）和每个前缀单独跑一次（slow）对比。② 和 Stage 6 对照：972 个 token 的 token id 和 log-prob 是否一致。③ 阴性对照：标点 token 理应没有 title-specific 信号。

**关键数字和 CI：**
- fast vs slow：最大差距 0.37 logit（bf16 舍入），排名 1–41 完全相同（Stage 10，12 个上下文，parity.json）。
- 与 Stage 6 比：972 个 token 的 token id 相同，log-prob 差距中位数约 1e-5（crosscheck_stage6.csv）。
- 阴性对照：标点 token 在每一层的 title-specific 信号都约为 0（最大 0.014，9,108 篇，§6.5）。
- 注意：看到这些 bf16 差距之后，parity 容差从 0.25 放宽到 0.5（parity.json tolerance_amendment）。
- n = 12 个上下文（parity）· 972 个 token（Stage 6 交叉核对）· 9,108 篇（阴性对照）。

**结论状态：** 描述性（质量检查通过）；容差是看过数据后改的，作为局限保留。

**过渡：** 进入 A 线：信号到底是不是关于"这篇"论文。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\Delta_{\max}=\max\,|z_{\mathrm{fast}}-z_{\mathrm{slow}}|$；② n = 12 contexts (parity) · 972 tokens (Stage 6 cross-check) · 9,108 papers (negative control)；③ Δmax ≈ 0: fast and slow code give the same logits；原公式框：Δ max = max |z fast − z slow | n = 12 contexts (parity) · 972 tokens (Stage 6 cross-check) · 9,108 papers (negative control)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, 12 contexts, parity.json)” → “(Stage 10, 12 contexts, fast-vs-slow check)”；“(Stage 10, crosscheck_stage6.csv)” → “(Stage 10, cross-check with Stage 6)”；“(Stage 10, max 0.014, 9,108 papers, §6.5)” → “(Stage 10, max 0.014, 9,108 papers)”；“(parity.json tolerance_amendment)” → “(recorded tolerance change)”

## P12 · HTML v75 p12 · pptx S12 (v22z) — Reading the method figures

**要说的话（一句英文一句中文）**
This page is the legend for every method figure.
这一页是所有方法图的图例。
Orange tokens are the true title, grey a false title, yellow the name being scored.
橙色 token 是真标题，灰色是假标题，黄色是正在打分的名字。
A blue arrow means we copy or inject a state; a red cross means we block it.
蓝色箭头表示复制或注入状态；红叉表示阻断。
Layers run upward from 0 to 63, positions run across.
层从 0 到 63 往上走，位置横着排。
Next, the groups and samples each analysis uses.
下一页看每项分析用的分组和样本。

**备查（不念）· 上一版讲稿本页全文（原第 P5 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 方法图的统一图例：带圆圈的数字表示步骤顺序；提示词 token 用颜色区分真标题、名字、假标题；纵轴是层（L0 到 L63），横轴是位置，每个点是一个隐藏状态；还有"从真运行复制状态到假运行"（patching）、"阻断"、"注入 X"、"读出排名"（如 1. Coifman、2. Smith、3. Zhang）以及 probe（如读年份）的符号。

**过渡：** 先用这套图例画出分组和样本是怎么来的。

## P13 · HTML v75 p13 · pptx S13 (v22z) — Groups and samples

**要说的话（一句英文一句中文）**
This page asks which papers each analysis uses.
这一页问：每项分析用的是哪些论文？
All papers go through open recall and multiple choice and land in a three by three table.
全部论文都经过开放回忆和多选题，落到一张三乘三的表里。
The full-cohort analyses use all of them; the intervention experiments use 593 target and 593 control papers.
全队列分析用全部论文；干预实验用 593 篇 target 和 593 篇 control。
On the chart, target minus control above zero means recognised papers carry more author signal than unrecognised ones.
图上 target 减 control 大于 0，表示认得的论文比认不得的论文带更多作者信号。
The uncertain group, about two thousand papers, is in neither group. Next, how one paper is scored.
不确定的那一组大约两千篇，两边都不放。下一页看一篇论文是怎么打分的。

**备查（不念）· 上一版讲稿本页全文（原第 P6 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 以单元格 C 为例，五步：全部论文 → 开放回忆（R0/R1/R2）→ 多选识别（strong / uncertain / fail）→ 九宫格 → 各分析用的样本。Stage 10、M2、M3 用全部论文；Stages 11–13 和 X 系列用 593 target + 593 control；1,178 个匹配对；Stages 1–9 用 Pilot50 和 Stage 8 的 A、B。

**关键数字和 CI：**
- 9,108 篇；R0：A 4,110（strong）、U0 2,002（uncertain）、B 2,186（fail）；R1：C 511 · 51 · D 34；R2：204 · 9 · 1。
- target = A + C = 4,621；control = B + D = 2,220。
- 干预样本 593 + 593；1,178 个匹配对。

**结论状态：** 方法页（样本说明）。

**过渡：** 下面从 Stage 1 开始，先看这些行为标签和冻结队列是怎么来的。

**图旁 n（灰色行）：** n = 9,108 papers (A 4,110 · U0 2,002 · B 2,186 · C 511 · D 34 …) · Stages 11–13: 593 + 593 · X3: 1,178 pairs

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{target}=A+C,\ \ \mathrm{control}=B+D$；② n = 9,108 papers (A 4,110 · U0 2,002 · B 2,186 · C 511 · D 34) · 593 + 593 · 1,178 pairs；③ T − C > 0: recognised papers carry more author signal than unrecognised ones；原 “How computed” 段：How computed: target = A + C, control = B + D · 9,108 papers; 593 + 593; 1,178 pairs；原公式框：n = 9,108 papers (A 4,110 · U0 2,002 · B 2,186 · C 511 · D 34 …) · Stages 11–13: 593 + 593 · X3: 1,178 pairs；原出处行：Counts: cohort/papers.parquet · Stage 11 sample · X3 pair table；方法细节移到备用页 B13 (slide 108)。

## P14 · HTML v75 p14 · pptx S14 (v22z) — Scoring: rank → log → spec

**要说的话（一句英文一句中文）**
This page walks through the score for one real paper.
这一页用一篇真实论文走一遍打分。
We run seven prompts: the true title, five false titles, and no title, and read the rank of each author name token.
我们跑七个提示：真标题、5 个假标题、没有标题，读出每个作者名字 token 的排名。
The rank is turned into log ten of one over the rank, so zero means ranked first and minus two means ranked one hundredth.
排名换成 log10(1/名次)，所以 0 表示排第一，−2 表示排第一百。
On the chart, spec above zero means the true title lifts the true author above the false titles; for this paper it is about plus 0.39.
图上 spec 大于 0 表示真标题把真作者抬到假标题之上；这篇论文大约是 +0.39。
So one number per paper. Next, the statistical rules we compare with.
所以每篇论文一个数。下一页看比较时用的统计规则。

**备查（不念）· 上一版讲稿本页全文（原第 P22 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 例子：Coifman, Bonanno, Rafaeli (2007)，输出层。四步：7 种提示（真标题、5 个假标题、删除标题）→ 每个名字 token 的排名 → mean log10(1/rank) → 对比。

**关键数字和 CI：**
- 作者 1（16 个 token 平均）：true −0.7190；false_0 −1.0234；false_1 −1.1540；false_2 −1.2625；false_3 −1.1334；false_4 −0.9895；delete −0.8808；假标题均值 −1.1126。
- spec = −0.7190 − (−1.1126) = +0.3935。
- total = true − delete = +0.1618；topic = 假标题均值 − delete = −0.2318。
- 来源：shard_011.npz 第 25025–40 行；paper_title_contrasts.parquet（final，L63）。

**结论状态：** 方法页（示例计算）。

**过渡：** 有了每篇论文的 spec，下一页讲怎样在组间比较、怎样算 CI。

**图旁 n（灰色行）：** n = 1 example paper (Coifman, Bonanno, Rafaeli 2007), author 1 · the method is applied to all 9,108 papers

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{nlr}=\log_{10}(1/\mathrm{rank})$ · $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 1 example paper, author 1 (method used on all 9,108 papers)；③ nlr = 0: true name ranked first; −2: ranked 100th / spec > 0: the true title ranks the author higher than false titles；原 “How computed” 段：How computed: nlr = log10(1/rank) = −log10(rank); spec = true − mean(false_0..4) · one example paper, L63, 16 tokens · source: paper_title_contrasts.parquet；原公式框：n = 1 example paper (Coifman, Bonanno, Rafaeli 2007), author 1 · the method is applied to all 9,108 papers；原出处行：Ranks: shard_011.npz rows 25025–40 (author 1 shown) · nlr, spec, total, topic: paper_title_contrasts.parquet (final, L63)；方法细节移到备用页 B13 (slide 108)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 示例论文用的是 L63、16 个 token。

## P15 · HTML v75 p15 · pptx S15 (v22z) — Statistical conventions

**要说的话（一句英文一句中文）**
This page asks how we compare groups fairly.
这一页问：怎么公平地比较两组？
We compare target with control only inside a citation bin, then take a weighted average across bins.
我们只在同一个引用档里比较 target 和 control，再跨档加权平均。
Papers that share an author are not independent, so we resample whole author teams, 7,247 of them, 2,000 times.
共享作者的论文不是独立的，所以我们按整个作者团队重抽样，共 7,247 个团队，抽 2,000 次。
On the chart, target minus control above zero means recognised papers' authors read better than control.
图上 target 减 control 大于 0，表示认得的论文的作者读得比对照组好。
So the intervals are honest about shared authors. Next, the probe.
所以置信区间考虑了作者共享。下一页看 probe。

**备查（不念）· 上一版讲稿本页全文（原第 P23 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 五步：引用档 → 档内 target − control → 加权平均 → 作者团队 → 按团队重抽样。13 个引用档（0-2 到 4097+），每组 < 30 篇的档丢掉；Δ = Σ w_b · (mean_t − mean_c)，w_b ∝ n_t·n_c / (n_t + n_c)；共享作者名字的论文算同一个团队，一个团队只进一个折；2,000 次抽样。

**关键数字和 CI：**
- 9,108 篇里有 7,247 个团队（cluster_ci.md）；最终使用 10 个档。
- CI 口径：Stage 10–12 已发布的表用论文级 bootstrap（在档 × 组内重抽论文）；Stage 13 起以团队整群 bootstrap 为主，团队层面的结论相同。
- n = 9,108 篇 · 7,247 个作者团队 · 2,000 次抽样。

**结论状态：** 方法页。

**过渡：** 方法讲完，进入全队列结果：知道"这篇论文"的信号在哪一层出现？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $T-C=\Sigma_b w_b\,(\overline{\mathrm{spec}}_{T,b}-\overline{\mathrm{spec}}_{C,b})$ · $w_b\propto\frac{n_t\,n_c}{n_t+n_c}$；② n = 9,108 papers · 7,247 author teams · 10 bins · 2,000 draws；③ T − C > 0: recognised papers’ authors read better than control；原 “How computed” 段：How computed: T − C = Σ_b w_b (mean_t,b − mean_c,b), w_b ∝ n_t n_c / (n_t + n_c) · 10 bins, 7,247 teams；原公式框：n = 9,108 papers · 7,247 author teams · 2,000 draws；原出处行：7,247 teams among 9,108 papers: cluster_ci.md；方法细节移到备用页 B13 (slide 108)。

## P16 · HTML v75 p16 · pptx S16 (v22z) — Statistical conventions (continued)

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

## P17 · HTML v75 p17 · pptx S17–S18 (v22z) — Probe

**要说的话（一句英文一句中文）**
This page asks what a probe is and what it reads.
这一页问：probe 是什么，读的是什么？
A probe is a small trained readout: we take the state at the last title token and train a ridge regression to point at the true names, with author teams kept apart between training and testing.
probe 是训练出来的小读出器：取最后一个标题 token 的状态，训练一个岭回归去指向真名字，训练和测试时作者团队分开。
On the chart, spec above zero means the probe reads this paper's authors from the title.
图上 spec 大于 0，表示 probe 能从标题读出这篇论文的作者。
For the surname's first token at layer 40 it is about plus 0.07, and the same state also carries the year.
姓氏第一个 token 在第 40 层大约是 +0.07，同一个状态里也带着年份。
So the probe is a second, more flexible way of reading the model. Next, how we compare the behaviour groups.
所以 probe 是第二种、更灵活的读法。下一页看怎么比较行为分组。

**备查（不念）· 上一版讲稿本页全文（原第 P26 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 例子 Coifman, Bonanno, Rafaeli (2007)，取最后一个标题 token（"loss"）处的状态。四步：取该状态 → 用岭回归 probe，按作者团队分折 → 读所有作者 → 也读年份。probe 分数 = 真名字 token 的 log10(1/rank)（所有作者，按角色）；spec = probe(真标题) − probe(假标题)。

**关键数字和 CI：**
- 姓氏第一个 token，L40：+0.071（补充 9，所有作者、所有 token，V0，1,395 篇；旧版只打第一个 token：+0.061；e4b_alltok.md）。
- 年份 R²：L16 → L52 为 0.38 → 0.56。
- 主数字口径：所有作者、所有名字 token、按角色（补充 9）；旧版第一个 token（E4b）+0.061 是预注册 V0，只用 false_0，1,395 篇。

**结论状态：** 方法页。

**过渡：** 下一页检验 probe 读到的是不是"这篇论文"特有的信息。

**图旁 n（灰色行）：** n = 9,108 papers (probe fit, 5 author-team folds) · 1,395 reuse-free papers (V0 main number)

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{probe}(\mathrm{true\ title})-\mathrm{probe}(\mathrm{false\ title})$；② n = 9,108 papers (probe fit, 5 team folds) · 1,395 reuse-free papers (main number)；③ spec > 0: the probe reads this paper’s authors from the title；原公式框：n = 9,108 papers (probe fit, 5 author-team folds) · 1,395 reuse-free papers (V0 main number)；原出处行：+0.071: addendum 9, all authors, all tokens, surname first token, V0, 1,395 papers (old first-token: +0.061); e4b_alltok.md。

## pptx S28（仅主 pptx，HTML deck 无对应页）— Probe: how the training samples are built

**要说的话（一句英文一句中文）**
This page shows how the probe's training samples are built.
这一页说明 probe 的训练样本是怎么取的。
Each paper is one sample: the state at the last title token goes in, and the model's own state where it predicts the author comes out; author teams are kept apart between training and testing.
每篇论文是一个样本：输入是最后一个标题 token 处的状态，目标是模型自己预测作者那个位置的状态；训练和测试时作者团队分开。
We then score the true authors under the true title and under a false title, and the difference is the probe's paper-specific signal.
然后在真标题和假标题下分别给真作者打分，两者之差就是 probe 读出的论文特有信号。

**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**
（主 pptx 当前页码：S17；HTML deck 无对应页。）

【讲稿】这一页讲 probe 的训练样本是怎么取的。一篇论文就是一个样本：提示里放真标题，取标题最后一个 token 在第 l 层的残差，5,120 维，这是输入 X；目标 Y 是同一次运行里模型自己在“预测作者名字”的位置上的 L63 状态（E4b 用冒号位置，补充 9 用某一类名字 token 的平均）。按作者团队分 5 折，共享作者名的论文放在同一折；标准化只用训练折，α 在第 0 折上选。对留出折的每篇论文，用同一个 W 分别喂真标题和匹配的假标题 false_0 的残差，预测出的状态过 final norm 和 9,137 个名字 token 的 lm_head 行，算每个真作者 token 的名次，取 log10(1/rank)，两者相减就是 spec。对照：同一个 probe，但把要打分的作者换成随机另一篇或同领域另一篇论文的作者。名字位置 probe（补充 11）做法相同，只是 X 换成预测名字那个位置的残差。
【怎么算】W = (AᵀA + α·tr(G)/d·I)⁻¹Aᵀ(Y − ȳ)；spec = nlr(X_true) − nlr(X_false_0)
【出处】stage11_analyze.py:150–202；stage13_alltok_probe.py；e4b_alltok.md
【从页面移出】Methods handbook: Stage 11 E4b (folds, standardisation, α) and addendum 9; 381_stage13/reports/e4b_alltok.md (header: probe definition)
【页面精简后移入备注】页面上“Stage 11 E4b”改称 title probe（标题探针），“addendum 9 / addendum 11”字样移入备注：补充 9 给全部名字 token 打分；E4b 旧版的 Y 取冒号“:”位置的 L63 状态，补充 9 取某一角色名字 token 的平均；名字位置探针为补充 11（原写 slide 82）。原“How computed”行：W = (AᵀA + α·tr(G)/d·I)⁻¹ Aᵀ(Y_tr − ȳ)，A = 训练折标准化后的 X，d = 5,120；ŷ → RMSNorm → 9,137 个名字 id 的 logits；nlr = log10(1/rank)，rank = 1 + #(logit > gold logit)；spec = nlr(true) − nlr(false_0)；出处 stage11_analyze.py:150–202 probe_section()、13_stage13/stage13_alltok_probe.py。
【2026-11-18 整合（v20）】【公式与样本量】方法图第 1 步已有 ridge 公式；加 n：拟合 9,108 篇，每个角色打分 1,395–1,706 篇。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(pre-registered V0: false_0 only, 1,395 papers; e4b_alltok.md)

**备查（不念）· 2026-11-23 v60 移出幻灯片的标签和出处（幻灯片上改用通俗名称）：**
- 警示行原写 “(addendum 9; … old first-token version (E4b) +0.061)”：addendum 9 = 按角色全 token 打分的补充登记；E4b = 旧版只打第一个名字 token 的探针

## P18 · HTML v75 p18 · pptx S19 (v22z) — Group comparisons

**要说的话（一句英文一句中文）**
This page asks whether recognised papers read their authors better than unrecognised ones.
这一页问：认得的论文，作者是不是读得比认不得的好？
We compare cells of the table: A against B, C against A, and a dose curve by how many option orders the model got right.
我们比较表里的格：A 对 B、C 对 A，以及按多选答对几个顺序画的剂量曲线。
On the chart, a contrast above zero means the first cell reads its authors better.
图上对比大于 0，表示第一个格的作者读得更好。
A minus B is plus 0.20, a pre-registered result, and the signal rises steadily from 0 to 4 orders right.
A 减 B 是 +0.20，是预注册的结果；信号随答对的顺序数从 0 到 4 稳定上升。
So recognition goes with a stronger hidden signal. Next, how we read the name's rank layer by layer.
所以认得和更强的内部信号是一起的。下一页看怎么逐层读名字排名。

**备查（不念）· 上一版讲稿本页全文（原第 P30 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 以单元格 C 为例。四步：九宫格 → P1：A − B → P2：C − A → 剂量：多选顺序答对的个数。指标是未写出作者在输出层的 title-specific 信号，团队 bootstrap。contrast = Σ w_b (mean_格1 − mean_格2)。

**关键数字和 CI：**
- P1 A − B：+0.200 [0.188, 0.213]（3,417 / 2,148 篇）。
- P2 C − A：合作者 +0.061；第一作者 +0.031（不显著）。
- 剂量：R0 按答对个数，0.17 → 0.46（primary.csv，stage10_curves.csv）。

**结论状态：** 方法页（结果详见第 97 页）。

**过渡：** target 一侧混进了 R1 论文，结果会不会只是 R1 论文造成的？下一页检验。

**图旁 n（灰色行）：** n = P1: A 3,417 + B 2,148 papers · P2: C − A (co-authors, first author) · dose: R0 papers by orders right

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{contrast}=\Sigma_b w_b\,(\overline{\mathrm{spec}}_{\mathrm{cell1},b}-\overline{\mathrm{spec}}_{\mathrm{cell2},b})$；② n = 3,417 A + 2,148 B papers (P1) · C − A (P2) · R0 papers by orders right (dose)；③ contrast > 0: the first cell reads its authors better；原公式框：n = P1: A 3,417 + B 2,148 papers · P2: C − A (co-authors, first author) · dose: R0 papers by orders right；原出处行：P1 +0.200 [0.188, 0.213]: A − B, 3,417 / 2,148 papers; P2 co-authors +0.061, first author +0.031: C − A; dose 0.17 → 0.46: R0 by orders right; primary.csv, stage10_curves.csv。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 图内公式框里的判据 / 说明（移出幻灯片）：title-specific signal, unwritten authors, output layer; team bootstrap

**备查（不念）：**
- 原写 “P1: A − B”、“P2: C − A”、行标 “P1”“P2”、n 行 “(P1)”“(P2)”：P1 = 预注册假设 1（识别，A − B），P2 = 假设 2（部分回忆，C − A）；现用 ②③ 和 “recognition / partial recall”

## P19 · HTML v75 p19 · pptx S20 (v22z) — Layer-by-layer readout

**要说的话（一句英文一句中文）**
This page asks how we read the name's rank at each layer.
这一页问：怎么在每一层读名字的排名？
We project the state at the name position onto the vocabulary with a lens and see where the true token lands.
我们用 lens 把名字位置的状态投到词表上，看真 token 排在哪里。
On the chart, zero means the true name is ranked first and minus two means ranked one hundredth.
图上 0 表示真名字排第一，−2 表示排第一百。
In this example the token “Co” is ranked about 120 thousandth at layer 56 and about 61st at the output.
在这个例子里，“Co” 这个 token 在第 56 层大约排第 12 万名，到输出层大约排第 61 名。
So true and false titles stay close until the last layers. Next, the put-back test.
所以真假标题一直很接近，直到最后几层。下一页看放回实验。

**备查（不念）· 上一版讲稿本页全文（原第 P38 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 例子 Coifman, Bonanno, Rafaeli (2007)，logit lens。五步：提示 → 名字位置的状态 → lens 投到词表 → 真 token 的排名 → 取平均。以作者 1 的第 5 个 token "Co" 为例。

**关键数字和 CI：**
- "Co" 的排名：L24 37,675；L40 3,979；L48 44,676；L56 120,750；L60 23,169；L61 9,811；L62 120；输出 61。
- nlr = log10(1/rank)，rank = 1 + 得分高于真 token 的 token 数；图中对比 7 个 token 的平均 nlr，true vs false_0。
- 来源：raw/logit/L*/shard_011.npz 第 25029 行。

**结论状态：** 方法页（示例）。

**过渡：** 把这个计算推广到全部 9,108 篇，看名字从哪一层开始变得可读。

**图旁 n（灰色行）：** n = 1 example paper (author 1, token “Co”), true title vs false_0

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{nlr}=\log_{10}(1/\mathrm{rank})$ · $\mathrm{rank}=1+\#(\mathrm{logit}>\mathrm{gold\ logit})$；② n = 1 example paper (author 1, token “Co”), true title vs false_0；③ nlr = 0: true name ranked first; −2: ranked 100th；原 “How computed” 段：How computed: nlr = log10(1/rank) = −log10(rank); rank = 1 + #(logit > gold logit) · one example paper, “Co”, logit lens · source: raw/logit/L*/shard_011.npz row 25029；原公式框：n = 1 example paper (author 1, token “Co”), true title vs false_0；原出处行：Ranks of “Co” (author 1, token 5), true title: shard_011.npz row 25029; out = L63；方法细节移到备用页 B14 (slide 109)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 示例用的是 logit lens。

## P20 · HTML v75 p20 · pptx S21 (v22z) — Replacement (patching)

**要说的话（一句英文一句中文）**
This page explains the put-back test.
这一页讲放回实验。
We run the true title and a false title side by side, then copy the states after the title from the true run into the false run at one layer.
我们把真标题和假标题并排跑，然后在某一层，把真运行里标题之后的状态复制到假运行里。
On the chart, R equal to 1 means the copied states bring back the whole true-title advantage; zero means nothing comes back.
图上 R 等于 1 表示复制过去的状态找回了全部真标题优势；0 表示什么都没找回。
Averaged over five false titles, R is about 0.8 at layer 48 and essentially 1 at layer 52.
在 5 个假标题上平均，R 在第 48 层约 0.8，到第 52 层基本是 1。
So by layer 52 the copied states carry everything. Next, the opposite test: taking the title away.
所以到第 52 层，复制的状态已经带着全部信息。下一页是反过来的实验：把标题拿走。

**备查（不念）· 上一版讲稿本页全文（原第 P48 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 例子 Coifman, Bonanno, Rafaeli (2007)，真标题运行和假标题运行（"The conjunction fallacy and the many meanings of and"）并排。五步：真标题 → 假标题 → 在第 l 层复制状态 → 给名字打分 → 恢复比例 R(l) = (patched − false) ÷ (true − false)。

**关键数字和 CI：**
- R(l)（5 个假标题均值，1,186 篇）：L24 0.080，L40 0.302，L48 0.821，L52 0.995（团队整群；x6_recovery.csv）。

**结论状态：** 方法页（数字和第 79 页一致）。

**过渡：** 反方向的干预是阻断注意力。

**图旁 n（灰色行）：** n = 1,186 papers (593 target + 593 control), mean of 5 false titles

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** How computed: R(l) = (patched − false) / (true − false), mean of 5 false titles, 1,186 papers, team cluster · 381_stage13/summary_x6/x6_recovery.csv。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{patched}-\mathrm{false}}{\mathrm{true}-\mathrm{false}}$；② n = 1,186 papers, mean of 5 false titles；③ R ≈ 1: fully restored；原 “How computed” 段：How computed: R(l) = (patched − false) / (true − false), mean of 5 false titles, 1,186 papers, team cluster；原公式框：[formula] · [formula]；原公式框：[formula] R ≈ 1: fully restored；方法细节移到备用页 B15 (slide 110)。

## P21 · HTML v75 p21 · pptx S22 (v22z) — Knockout (block attention)

**要说的话（一句英文一句中文）**
This page explains the take-away test.
这一页讲拿走实验。
From a given layer on, we block the later tokens from looking at the title, in the true run and in a false run, and take the difference.
从某一层开始，阻断后面的 token 看标题，真标题运行和假标题运行都做，再取差值。
On the chart, S near zero means nothing is lost, so the title is no longer needed after that layer.
图上 S 接近 0 表示没有损失，也就是说过了这一层就不再需要标题。
The loss falls from the whole advantage when blocking from the start, to about 0.03 when blocking from layer 52.
从一开始就阻断时损失是全部优势，从第 52 层开始阻断时只剩约 0.03。
So reading the title is done by layer 52. Next, the change-the-question test.
所以标题到第 52 层已经读完。下一页看换问题检验。

**备查（不念）· 上一版讲稿本页全文（原第 P49 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 四步：从第 l 层起阻断尾部 token 对标题的注意力 → 真标题下的损失 T → 假标题下的损失 F → S = T − F（论文特异的损失）。

**关键数字和 CI：**
- S 随起始阻断层下降：L0 1.00，L24 0.87，L32 0.56，L40 0.29，L48 0.14，L52 0.03（以 (真 − 假) 的份额表示，1,186 篇）。
- L52：target 0.018，control 0.051。
- 来源：Stage 13 X7，1,186 篇（593 target + 593 control）；x7_report.md。

**结论状态：** 方法页（判定见第 79 页）。

**过渡：** 把两种干预放在一起，看标题在哪几层被读取。

**图旁 n（灰色行）：** n = 1,186 papers (593 target + 593 control)

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** S(l): Stage 13 X7, 1,186 papers (593 target + 593 control); x7_report.md。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $S(l)=T(l)-F(l)$；② n = 1,186 papers (593 + 593)；③ S ≈ 0: nothing lost — reading done；原公式框：[formula] · [formula] S ≈ 0: nothing lost — reading done。

## P22 · HTML v75 p22 · pptx S23 (v22z) — Changing the question

**要说的话（一句英文一句中文）**
This page asks: if the middle layers do not hold the name, what do they hold?
这一页问：如果中间层存的不是名字，那存的是什么？
This is the change-the-question test. We take the title states made under one question, authors, year or field, and copy them into the authors prompt of another paper.
这是换问题检验。我们把在某个问题下（作者、年份或领域）得到的标题状态，复制到另一篇论文的作者提示里。
On the chart, R near 1 means the other question's state works as well as the paper's own.
图上 R 接近 1，表示另一个问题下的状态和本来的状态一样好用。
Copied at layer 24 it is almost 1 for all three questions; at layer 48 only about 0.45, so by then the state is tied to its own question.
在第 24 层复制，三种问题都接近 1；到第 48 层只有约 0.45，说明那时状态已经和自己的问题绑在一起。
So the title state is first general, then question-specific. Next, a reworded title.
所以标题状态先是通用的，后来才和问题绑定。下一页看改写的标题。

**备查（不念）· 上一版讲稿本页全文（原第 P65 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 例子 Coifman, Bonanno, Rafaeli (2007)。四步：同一个标题配三种问题（Authors: / Year: / Field:）→ M3：比较不同问题下标题处的状态（结论：不比 L4 更接近）→ X1：把某一问题下的标题状态复制进另一篇论文（"Scholars and foreign policy…"）的作者提示 → 给所有作者打分。R(l) = (patched − other) ÷ (own − other)，在第 l 层复制标题状态，582 篇测试论文。

**关键数字和 CI：**
- 来自 authors / year / field 三种问题的 R：L24 0.996 / 0.990 / 0.992；L40 0.933 / 0.928 / 0.929；L48 0.455 / 0.431 / 0.444。
- 来源：Stage 13 X1，所有作者（batch 1 第 1 项），测试集 582 篇；旧版第一作者为 0.99 / 0.92 / 0.42。

**结论状态：** 方法页（结果见第 81 页）。

**过渡：** 第二种方法：换一种说法写同一个标题。

**图旁 n（灰色行）：** n = 582 test papers (team folds)

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{patched}-\mathrm{other}}{\mathrm{own}-\mathrm{other}}$；② n = 582 test papers (team folds)；③ R ≈ 1: the other question’s state works as well；原公式框：n = 582 test papers (team folds)；原出处行：R: Stage 13 X1, all authors (batch 1 item 1), test 582 papers; b1_xall_report.md (old first-author: 0.99 / 0.92 / 0.42)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："compare states" ← "M3: compare states"; "copy into other title" ← "X1: copy into other title"

## P23 · HTML v75 p23 · pptx S24 (v22z) — Paraphrased title

**要说的话（一句英文一句中文）**
This page asks whether a reworded title of the same paper looks closer than a different paper with similar words.
这一页问：同一篇论文换个说法的标题，是不是比用词相近的另一篇论文看起来更近？
We compare three titles: the original, a paraphrase, and a neighbour that shares words but is another paper.
我们比较三个标题：原标题、改写的标题，以及用词相近但属于另一篇论文的邻居。
On the chart, G prime above zero means the reworded same paper is closer than the similar other paper.
图上 G′ 大于 0，表示改写的同一篇论文比用词相近的另一篇更近。
It is about plus 0.3 already at layer 8 and peaks near plus 0.46 at layer 36.
它在第 8 层就有大约 +0.3，在第 36 层达到峰值，约 +0.46。
So meaning counts more than shared words. Next, patchscope.
所以意思比共同的用词更重要。下一页看 patchscope。

**备查（不念）· 上一版讲稿本页全文（原第 P66 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 比较"同一篇论文换一种说法"和"另一篇论文、用词相近"。四步：三个标题（原标题；改写 "Affect fluctuations, grief and adaptability in the face of loss"；用词相近的邻居 D "Affect and Resistance to Temptation."）→ 取最后一个标题 token 的状态 → 比较距离 → 词重叠。G′ = cos(orig, para) − cos(orig, D)。

**关键数字和 CI：**
- 词重叠：改写 0.22，D 0.14（这一篇）；中位数 0.61 vs 0.15（主集，1,110 篇）。
- G′：L8 +0.32，L36 达到峰值 +0.46（测试集）。
- 所有作者得分，改写 − D：+0.229。

**结论状态：** 方法页（结果见第 82 页）。

**过渡：** 第三种方法：Patchscope，让模型自己把标题状态"说出来"。

**图旁 n（灰色行）：** n = 1,110 papers (primary set; 552 test papers)

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $G'=\cos(\mathrm{orig},\mathrm{para})-\cos(\mathrm{orig},D)$；② n = 1,110 papers (552 test papers)；③ G′ > 0: reworded same paper is closer than a similar other paper；原公式框：n = 1,110 papers (primary set; 552 test papers)；原出处行：Word overlap 0.22 / 0.14: x3_lexical_neighbour_j2.csv (this paper) · medians: x3_report.md (primary set, 1,110)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Paraphrased title" ← "Paraphrased title (X3)"

## P24 · HTML v75 p24 · pptx S25 (v22z) — Patchscope

**要说的话（一句英文一句中文）**
This page asks whether the title state can name anything about its own paper when another prompt reads it out.
这一页问：用另一个提示去读标题状态时，它能不能说出关于自己论文的东西？
This is patchscope: we take the state at the last title token and insert it into the prompt “Paper: X. The first author of the paper is”.
这就是 patchscope：取最后一个标题 token 的状态，把它插进提示 “Paper: X. The first author of the paper is”。
On the chart, D above zero means the paper's own state scores its true answer higher than a partner paper's state does.
图上 D 大于 0，表示用本论文自己的状态，真答案的分数比用配对论文的状态更高。
For the first author it is about plus 0.046 from layer 8, and for the year a smaller plus 0.013 from layer 40.
第一作者从第 8 层起大约是 +0.046，年份从第 40 层起是较小的 +0.013。
These are small differences, and later we test whether they go beyond topic. That closes the methods; next, the gap between recognising and saying.
这些差别都很小，后面我们会检验它们是否超出主题。方法部分到此结束；下一部分讲“认得”和“说出”之间的差距。

**备查（不念）· 上一版讲稿本页全文（原第 P67 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 四步：取最后一个标题 token 的状态 → 在第 l 层注入到另一个提示 "Paper: X. The first author of the paper is" 的 X 位置 → 让模型回答 → 比较用本论文状态和用配对论文状态的结果。D = score(own state) − score(partner state)，score = 真答案 token 的 log10(1/rank)；也问年份、领域。

**关键数字和 CI：**
- 第一作者从 L8 起：+0.046 [0.035, 0.059]；年份从 L40 起：+0.013 [0.008, 0.018]（Stage 13 X4，提示按设计问第一作者，测试集，团队 CI；x4_report.md）。

**结论状态：** 方法页（结果见第 82 页）。

**过渡：** 下一页把 Stage 12–13 对三个假设的结论汇总成一张表。

**图旁 n（灰色行）：** n = 582 test papers (596 tune), team CI

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $D=\mathrm{score}(\mathrm{own\ state})-\mathrm{score}(\mathrm{partner\ state})$；② n = 582 test papers (596 tune)；③ D > 0: this state carries this paper’s answer；原公式框：n = 582 test papers (596 tune), team CI；原出处行：D: Stage 13 X4 (prompt asks for the first author by design), test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; x4_report.md。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Patchscope" ← "Patchscope (X4)"

# Part 2 · Recognised but not said (25–35)

## P25 · HTML v75 p25 · pptx S26 (v22z) — Writing an author needs about 276× the exposure that recognising does

**要说的话（一句英文一句中文）**
This page asks how much more exposure writing an author needs than recognising one.
这一页问：写出一个作者，比认出一个作者需要多多少曝光？
We use citations as a stand-in for exposure, and fit, for every paper, how the chance of recognising and the chance of writing rise with citations.
我们用引用数代替曝光量，拟合认出的概率和写出的概率怎样随引用数上升。
On the chart, each curve crosses one half at its threshold; recognition crosses at about 40 citations, writing only at about 11 thousand.
图上每条曲线过一半的地方就是它的门槛；认出大约在 40 次引用，写出要到大约 1.1 万次。
That ratio, rho, is about 276. The rule was locked after we had seen the estimates, so we only claim that writing needs more exposure than recognising.
这个比值 ρ 大约是 276。规则是看过估计值之后才锁定的，所以我们只主张“写出比认出需要更多曝光”。
So recognising and saying are two very different levels of knowing. Next, whether the paper signal grows with citations.
所以认出和说出是两种差得很远的“知道”。下一页看论文信号是不是随引用数增长。

**备查（不念）· 上一版讲稿本页全文（原第 P29 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 19（规则在看过数据后锁定），9,108 篇，7,247 个团队，2,000 次团队抽样。对"认出"（多选团队结果为 strong）和"写出"（至少写出 1 个真作者，R1 或 R2）分别在 log10(1 + 引用) 加年份上做 logistic 拟合，c50 = p = 0.5 时的引用数；ρ = c50(写出) / c50(认出)。右图：档内 T − C（spec，L63）对 log 引用做 WLS（10 个档）。

**关键数字和 CI：**
- 认出 c50 = 40 [36, 44]；写出 c50 = 11,038 [8,172, 15,607]；ρ = 276 [203, 390]。
- 档内 T − C 的 WLS 斜率：每 10 倍引用 +0.030 [+0.014, +0.044]。
- 局限：只有一个模型；引用只是曝光的代理；写出 c50 接近引用范围的顶端（只有 16 篇高于 11,038）；低档有约 25% 的猜测下限；去掉"uncertain"时 ρ = 1,184 [851, 1,712]。
- n = 9,108 篇（左）；右图 7,995 篇（所用 10 个档）。

**结论状态：** 锁定判据成立（ρ 的整个 CI > 1），但判据是在看过数据后才锁定的，因此按初步（较稳但有前提）处理，不当作预注册定论。

**过渡：** 下面换一种组织方式，用九宫格里的单元格两两对比。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\rho=c_{50}^{\mathrm{written}}\,/\,c_{50}^{\mathrm{recognised}}$ · $c_{50}:\ p(\mathrm{citations})=0.5$；② n = 9,108 papers · 7,247 teams · 7,995 papers in the 10 bins used；③ ρ > 1: writing needs more exposure than recognising；原 “How computed” 段：How computed: recognised = multiple-choice team result “strong”; written = ≥ 1 true author (R1 or R2); logistic fit on log10(1 + citations) + year; c50 = citations at p = 0.5; WLS of within-bin T − C on log citations (10 bins). 9,108 papers, 7,247 teams, team bootstrap ×2,000.；原出处行：391_groups/summary_exposure_prereg19/ (thresholds_ratio.csv, trend_by_bin.csv) · summary_exposure_20261114/exposure_by_bin.csv；方法细节移到备用页 B14 (slide 109)。

**备查（不念）：**
- 标签与副标题原写 “Line A · addendum 19”、“Addendum 19 (rule locked after the data were seen)”：addendum 19 = 曝光门槛检验的补充登记（看过数据后锁定）

## P26 · HTML v75 p26 · pptx S27 (v22z) — More citations, more paper knowledge

**要说的话（一句英文一句中文）**
This page asks whether the paper signal grows with citations.
这一页问：论文信号会不会随引用数增长？
We plot the signal at the output layer for each citation bin, separately for recognised and unrecognised papers.
我们按引用档画出输出层的信号，认得和认不得的论文分开画。
On the chart, spec above zero means the true title beats the five false titles; for recognised papers it rises from about 0.35 in the lowest bin to about 0.64 in the highest.
图上 spec 大于 0 表示真标题胜过 5 个假标题；认得的论文从最低档的约 0.35 升到最高档的约 0.64。
And recognised papers stay above unrecognised ones in every bin.
而且每一个档里，认得的都高于认不得的。
So more exposure means a stronger paper-specific signal. Next, whether the recognition effect comes only from papers with partial recall.
所以曝光越多，论文特有的信号越强。下一页看认得的效应是不是只来自部分回忆的论文。

**备查（不念）· 上一版讲稿本页全文（原第 P28 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型输出层，按引用档画读出水平和 title-specific 信号，分 target / control；少于 10 篇的档不画。

**关键数字和 CI：**
- target：+0.35 → +0.64（Stage 10，final，200 / 84 篇，§6.8）。
- title-specific 的 Spearman：全部 0.45 · target 0.33 · control 0.19（Stage 10 X2，9,108 篇，§6.8）。
- 每个档里都是 target > control。
- n = 9,108 篇（少于 10 篇的档不画）。

**结论状态：** 定论（第 64 页"引用：单调，ρ = 0.451，resolved"）。

**过渡：** 引用数是曝光的代理变量。下一页用补充 19 正式比较：认出论文和写出作者分别需要多少曝光。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$$\ \mathrm{per\ citation\ bin}$；② n = 9,108 papers (bins with < 10 papers omitted)；③ spec > 0: the true title beats false_0…false_4; it rises with citations；原公式框：spec = nlr true − mean 5 nlr false , per citation bin n = 9,108 papers (bins with。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, final, 200 / 84 papers, §6.8)” → “(Stage 10, final, 200 / 84 papers)”；“(Stage 10 X2, 9,108 papers, §6.8)” → “(Stage 10 citation correlation, 9,108 papers)”

## P27 · HTML v75 p27 · pptx S28 (v22z) — Is it just the R1 papers? No.

**要说的话（一句英文一句中文）**
This page asks: is the recognition effect only the partially recalled papers?
这一页问：认得的效应是不是只来自部分回忆的论文？
We split the comparison: only papers with no author written, and papers with some authors written.
我们把比较拆开：只看一个作者都没写出的论文，以及写出部分作者的论文。
On the chart, target minus control above zero means recognised papers' authors read better; with no author written it is 0.199, almost the same as 0.207 for everyone.
图上 target 减 control 大于 0 表示认得的论文作者读得更好；只看一个都没写出的论文是 0.199，和全部论文的 0.207 几乎一样。
Partially recalled papers are stronger, about 0.37, but they also show up only late.
部分回忆的论文更强，大约 0.37，但同样很晚才出现。
So it is not just those papers. Next, authors it wrote versus authors it missed.
所以不只是这些论文的效应。下一页比较写出的作者和漏掉的作者。

**备查（不念）· 上一版讲稿本页全文（原第 P31 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 左图：档内 title-specific 的 target − control，分 R0 视角（A − B）、R1 视角（C − B）和合并（logit lens，菱形 = 输出）。右图：Stage 11 patching 恢复的差距比例，分 A（R0，n=557）、C（R1，n=36）、B（R0，n=588）。

**关键数字和 CI：**
- 只看 R0（A − B）：输出 +0.199 vs +0.207，形状相同（Stage 10，A 3,423 / B 2,151，§6.13）。
- R1（C − B）：+0.37，同样出现得晚（C 391 / B 885）。
- target 内部 C − A：+0.11，从 L56 开始（C 485 / A 3,204）。
- patching：R1 稍晚，到 L52 完成（Stage 11 E1，36 篇 R1 target）。
- n = A 3,423 / B 2,151（R0）· C 391 vs B 885（R1）· patching 551 + 36 + 588 篇。

**结论状态：** 定论（第 64 页"同组比较：comparable, unchanged"）；R1 的 patching 只有 36 篇，属描述性。

**过渡：** 在 R1 论文内部还可以做一个更干净的配对：同一篇论文里，写出来的作者 vs 漏掉的作者。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $T-C=\Sigma_b w_b\,(\overline{\mathrm{spec}}_{T,b}-\overline{\mathrm{spec}}_{C,b})$ · $R(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false})}{\mathrm{mean}(\mathrm{true}-\mathrm{false})}$；② n = A 3,423 / B 2,151 (R0) · C 391 vs B 885 (R1) · patching 551 + 36 + 588 papers；③ T − C > 0: recognised papers’ authors read better than control / R ≈ 1: fully restored; R ≈ 0: nothing restored；原公式框：T − C = Σ b w b (spec T,b − spec C,b ); R(l) = mean(patched − false) / mean(true − false) n = A 3,423 / B 2,151 (R0) · C 391 vs B 885 (R1) · patching 551 + 36 + 588 papers。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, A 3,423 / B 2,151, §6.13)” → “(Stage 10, A 3,423 / B 2,151)”；“(Stage 11 E1, 36 R1 targets)” → “(Stage 11 put-back test, 36 R1 targets)”

## P28 · HTML v75 p28 · pptx S29 (v22z) — Authors it wrote vs authors it missed

**要说的话（一句英文一句中文）**
This page asks: within the same paper, are the authors it wrote read better than the ones it missed?
这一页问：在同一篇论文里，写出来的作者是不是比漏掉的作者读得更好？
We pair authors inside each of 495 partially recalled papers and follow the difference across layers.
我们在 495 篇部分回忆的论文里，逐篇把作者配对，逐层看差值。
On the chart, delta above zero means the written authors read better; at the output it is about 0.20, while the no-title prior alone gives about 0.10.
图上 Δ 大于 0 表示写出的作者读得更好；输出层大约是 0.20，而不给标题的先验只有大约 0.10。
It is about zero up to layer 52 and grows only from layer 54.
到第 52 层为止它都约等于 0，从第 54 层才开始增长。
So the difference appears only at the very end. Next, the three pre-registered group comparisons.
所以这个差别只在最后才出现。下一页看三个预注册的分组比较。

**备查（不念）· 上一版讲稿本页全文（原第 P32 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 495 篇 R1 论文，在每篇论文内部配对：title-specific(写出的作者) − title-specific(漏掉的作者)，逐层看 logit lens、public lens 和输出，另画"无标题"条件作为先验参照。

**关键数字和 CI：**
- 写出 − 漏掉，输出层：+0.20（Stage 10，final L63，495 篇）。
- 到 L52 约为 0，从 L54 开始增长。
- 无标题（先验）：+0.10。
- 去掉第一作者后结果相同。
- n = 495 篇 R1 论文（论文内配对）。

**结论状态：** 初步（较稳但有前提：只有 R1 论文；有一半来自名字先验）。

**过渡：** 汇总 A 线：小样本看到了什么，规模化之后看到了什么。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\Delta=\mathrm{spec}(\mathrm{written})-\mathrm{spec}(\mathrm{missed}),\ \mathrm{same\ paper}$；② n = 495 R1 papers (paired within paper)；③ Δ > 0: authors it wrote are read better than ones it missed；原公式框：written − missed = spec(written author) − spec(missed author), same paper n = 495 R1 papers (paired within paper)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, r0_r1_analysis.md §4)” → “(Stage 10, R0/R1 analysis)”

## P29 · HTML v75 p29 · pptx S30 (v22z) — Group comparisons: three findings

**要说的话（一句英文一句中文）**
This page asks whether recognising a paper changes how strong the signal is, or when it arrives.
这一页问：认得一篇论文，改变的是信号的强弱，还是到达的时间？
The plan was fixed before the results: only authors that were not written, the output layer, within citation bins, with a correction for four tests.
计划是在看结果之前定好的：只看没写出的作者、输出层、引用档内，并对四个检验做多重比较校正。
On the chart, a contrast above zero means the first group reads its authors better. Recognised beats unrecognised by 0.20, and the signal rises by about 0.06 for every option order answered correctly.
图上对比大于 0 表示第一组的作者读得更好。认得比认不得高 0.20，而多选每多答对一个顺序，信号大约上升 0.06。
Partial recall adds only about a third of the recognition effect, and only at the output.
部分回忆带来的提升只有认得效应的大约三分之一，而且只在输出层。
So recognition changes the size of the signal. Next, whether it also changes the timing.
所以认得改变的是信号大小。下一页看它是不是也改变时间。

**备查（不念）· 上一版讲稿本页全文（原第 P97 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 计划在看到结果之前固定（补充 7、8）：只看未写出的作者，输出层（L63）title-specific 信号，引用档内比较，团队 bootstrap 95% CI，对 4 个检验做 Holm 校正。P1：R0 内 A − B；P3：每多答对一种多选顺序的增量；P2：C − A（合作者和第一作者分开）。

**关键数字和 CI：**
- ① 识别：R0 内 A − B +0.200 [0.188, 0.213]（3,417 / 2,148 篇，Holm p ≤ 0.002）；加入混杂变量 +0.173 [0.161, 0.186]（论文级，5,565）；作者级加位置 +0.151 [0.139, 0.163]（19,893 位作者）。
- ② 分级：每多答对一种顺序 +0.059 [0.056, 0.063]（P3，8,288 篇 R0，档固定效应；Holm p ≤ 0.002）（加混杂 +0.046 [0.042, 0.049]，作者级）；全错约 0.17，全对约 0.46（R0，927 / 4,105 篇）。
- ③ 部分回忆帮助不大（约为识别效应的 ⅓），且只在输出层：C − A 合作者 +0.061 [0.034, 0.090]（P2-other，390 / 2,826 篇，Holm p ≤ 0.002）；第一作者 +0.031 [−0.006, 0.069]，不显著（P2-first，292 / 3,199）；logit lens 在 L48–L62 约 0，public J-lens 在 L48–L59 为 −0.07 到 −0.11。早先约 +0.11 的结果用了所有作者（循环）。
- 仅供参考：R2 已写出作者 +0.844（200 篇）；只有 28 篇 R2 论文有未写出的作者。
- n = 3,417 / 2,148（P1）· 8,288（P3）· 390 / 2,826（P2-other）· 292 / 3,199（P2-first）· 200（R2）。

**结论状态：** 预注册判据：P1 成立，P3 成立，P2-other 成立；P2-first 不成立。

**过渡：** 再看 Stage 11 E1 的恢复比例按组拆开后，分子和分母各是什么情况。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{contrast}=\Sigma_b w_b\,(\overline{\mathrm{spec}}_{A,b}-\overline{\mathrm{spec}}_{B,b})$；② n = 3,417 / 2,148 (P1) · 8,288 (P3) · 390 / 2,826 · 292 / 3,199 (P2) · 200 (R2)；③ contrast > 0: the first group reads its authors better；原公式框：contrast = Σ b w b (spec A,b − spec B,b ), Holm over 4 n = 3,417 / 2,148 (P1) · 8,288 (P3) · 390 / 2,826 (P2-other) · 292 / 3,199 (P2-first) · 200 (R2)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(P1 A − B, 3,417 / 2,148 papers, Holm p ≤ 0.002; primary.csv)
- 出处（原在幻灯片上）：(R0, 927 / 4,105 papers; stage10_curves.csv)
- 出处（原在幻灯片上）：(P2-other, 390 / 2,826 papers, Holm p ≤ 0.002)
- 出处（原在幻灯片上）：(P2-first, 292 / 3,199)
- 出处（原在幻灯片上）：(stage10_contrasts.csv, unwritten_other)
- 出处（原在幻灯片上）：(r0_r1_analysis.md §2)
- 出处（原在幻灯片上）：(200 papers; summary_table.md)

**备查（不念）：**
- 副标题原写 “(addenda 7, 8)”（组比较的两份补充登记）；图与 n 行原写 P1 / P2 / P3（预注册假设编号：P1 识别 A − B，P2 部分回忆 C − A，P3 每多答对一个顺序）；“(P3, 8,288 R0 papers …)”

## P30 · HTML v75 p30 · pptx S31 (v22z) — Recognition changes the size; timing nearly the same

**要说的话（一句英文一句中文）**
This page asks whether recognition changes the timing as well as the size.
这一页问：认得除了改变大小，是不是也改变时间？
We plot the output signal against how many option orders were answered correctly, and against the probability of the true option.
我们把输出层信号对多选答对的顺序数、以及对真选项的概率画出来。
On the chart, spec above zero means the true title ranks the author higher; for papers with no author written it climbs from about 0.17 to about 0.46.
图上 spec 大于 0 表示真标题让作者排得更前；一个都没写出的论文，从约 0.17 升到约 0.46。
But the put-back share at layer 48 barely moves, from about 0.90 to 0.81, so the arrival time is nearly the same.
但第 48 层的放回比例几乎不动，从约 0.90 到 0.81，所以到达时间差不多。
So recognition makes the signal bigger, not earlier. Next, the recovery by group, split into numerator and denominator.
所以认得让信号更大，而不是更早。下一页按组看恢复比例，把分子和分母拆开。

**备查（不念）· 上一版讲稿本页全文（原第 P100 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 未写出作者的输出层（L63）信号，取普通均值，团队 bootstrap 95% CI；n < 30 的点仅作描述。左图：按多选答对顺序数（0–4）；右图：按真选项平均概率分档。蓝色 R0，绿色 R1（391_groups/figures/fig2）。

**关键数字和 CI：**
- R0：0 对约 0.17（n=927）→ 4 对约 0.46（n=4,105）（图中读数，与第 97 页一致）。
- 重跑：答对 0–4 时，分母从 0.185 升到 0.407，而 E1 R(L48) 略降，0.90 → 0.81（R0 论文 A + U0 + B，0 / 4 时为 241 / 557 篇；rerun_report.md "Continuous recognition"）。
- n = R0 927–4,105 / R1 15–462 篇。

**结论状态：** 描述性。

**过渡：** Stage 12 的 P1 / P2 按组拆开，也有同样的小分母效应。

**图旁公式（灰色行）：** y = mean over unwritten authors of spec,  spec = nlr(true) − mean₅ nlr(false),  L63 · n = R0 927–4,105 · R1 15–462 papers per level

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $y=\mathrm{mean}_{\mathrm{unwritten}}\,\mathrm{spec}$ · $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = R0 927–4,105 · R1 15–462 papers per level；③ spec > 0: the true title ranks the author higher than false titles；原 “How computed” 段：How computed: plain means of the spec of unwritten authors (L63, true − mean of 5 false titles) by recognition level · R0 927–4,105 / R1 15–462 papers · team cluster · source: stage10_curves.csv, rerun_report.md；原公式框：y = mean over unwritten authors of spec, spec = nlr(true) − mean₅ nlr(false), L63 n = R0 927–4,105 · R1 15–462 papers per level；方法细节移到备用页 B21 (slide 116)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(R0 papers A + U0 + B, 241 / 557 papers at 0 / 4; rerun_report.md “Continuous recognition”)

**备查（不念）：**
- 图注原写 “(391_groups/figures/fig2)”（图文件路径）；正文 “E1 R(L48)” = Stage 11 放回实验的恢复比例

## P31 · HTML v75 p31 · pptx S32 (v22z) — Recovery by group: numerator and denominator

**要说的话（一句英文一句中文）**
This page asks why recovery ratios differ between groups.
这一页问：不同组的恢复比例为什么不一样？
We list, for each group, the denominator, which is true minus false, the amount restored at layer 48, and the ratio at layers 48 and 52.
我们按组列出分母（真减假）、第 48 层恢复的量，以及第 48、52 层的比例。
On the chart, a ratio of 1 means fully restored. At layer 52 every group is close to 1; at layer 48 the unrecognised group even looks higher, about 0.87 against 0.81.
图上比例为 1 表示完全恢复。第 52 层每组都接近 1；第 48 层认不得的组看起来反而更高，约 0.87 对 0.81。
That is because its denominator is about half as large; in absolute terms it restores less.
这是因为它的分母只有大约一半；按绝对量算，它恢复得更少。
So a ratio can mislead when the denominators differ. Next, whether highly cited papers arrive at a different time.
所以分母不同时，比例会误导。下一页看引用多的论文到达时间是不是不同。

**备查（不念）· 上一版讲稿本页全文（原第 P98 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 8：E1 恢复 R = mean(patched − false) ÷ mean(true − false)，只看未写出作者，团队整群 95% CI，按组列出分母（真 − 假）、L48 分子、R(L48)、R(L52)。

**关键数字和 CI：**
- A（R0 × 认得出，557 篇）：分母 +0.407 [0.386, 0.430]；分子 +0.330；R(L48) +0.811 [0.790, 0.832]；R(L52) +0.988 [0.980, 0.996]。
- B（R0 × 认不出，586）：+0.214 [0.196, 0.234]；+0.186；+0.869 [0.835, 0.906]；+1.016 [1.002, 1.031]。
- U0（R0 × 不确定，599）：+0.293 [0.271, 0.316]；+0.248；+0.844 [0.814, 0.877]；+1.000 [0.988, 1.012]。
- C（R1 × 认得出，补充 11 B，462）：+0.559 [0.529, 0.590]；+0.408；+0.731 [0.705, 0.757]；+0.985 [0.977, 0.994]。
- R2 已写出作者（参照，200）：+0.845 [0.798, 0.897]；+0.566；+0.670 [0.630, 0.707]；+0.948 [0.927, 0.965]。
- B 比率更高是分母小造成的：分子 B − A 在 L24 / L40 / L48 / L52 分别为 −0.010、−0.040、−0.144、−0.184，CI 全在 0 以下——任何一层上 B 携带的绝对论文特异信号都不多于 A。
- C 补到 462 篇：引用档内（462 篇中 258 篇，6 个档）和 A 一样在 L52 达到 R 约 1，差距更大（C − A +0.075 [+0.024, +0.130]）；D 33 篇 / R2 未写出 28 篇 → 描述性。
- n = A 557 · B 586 · U0 599 · C 462 · R2 200 篇。

**结论状态：** 初步（较稳但有前提：比率受分母影响）；分子 B − A 的 CI 全在 0 以下；U0、R2、D 为描述性。

**过渡：** 把识别程度做成连续变量，看信号大小和时间如何变化。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false})}{\mathrm{mean}(\mathrm{true}-\mathrm{false})}$；② n = A 557 · B 586 · U0 599 · C 462 · R2 200 papers；③ R ≈ 1: fully restored; R ≈ 0: nothing restored；原公式框：R = mean(patched − false) / mean(true − false) n = A 557 · B 586 · U0 599 · C 462 · R2 200 papers。

## pptx S64（仅主 pptx，HTML deck 无对应页）— Re-runs by group: curves, numerator, denominator

**要说的话（一句英文一句中文）**
This page shows the re-runs by group: the recovery curves, and the numerator and denominator separately.
这一页按组展示重跑结果：恢复曲线，以及分开看的分子和分母。
All groups rise in the same layers; the unrecognised group's ratio looks higher only because its denominator is about half as large.
各组都在同样的层上升；认不得的组比例看起来更高，只是因为它的分母只有大约一半。
So the groups differ in size, not in timing.
所以各组的差别在大小，不在时间。

**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**
（主 pptx 当前页码：S47；HTML deck 无对应页。）

【讲稿】这一页把补充 8 的重跑结果画出来。a：各组的恢复比例 R(l) 曲线，A、B、U0、C 走势相同，都在 L44–52 急升；R2 只有 28 篇，只作参照。b：把分子和分母分开看。B 的分母比 A 小一半左右，分子在每一层也比 A 小，所以 B 的比例高只是分母小造成的。c：按选择题答对次数 0–4 分档（R0 论文；0–1 档全是 B，2–3 档是 U0，4 档是 A）。分母从 0.185 升到 0.407，R(L48) 从 0.904 降到 0.811，斜率每答对一次 −0.019 [−0.032, −0.007]，区间不含 0。这个趋势检验是事后的，补充 7、8 没有为 E1 预设；而且答对次数和组完全嵌套，所以这是组间比较，不是剂量反应。
【怎么算】R = mean(替换 − 假) ÷ mean(真 − 假)；斜率 = 五个档的 R_k 对 k 的加权最小二乘斜率（权重 n_k），在 2,000 次作者团队 bootstrap 中逐次重算。
【出处】391_groups/summary_rerun_plot_20261112/（作业 11845547）
【从页面移出】How computed: R(l) = mean_p(patched@l − false) / mean_p(true − false), unwritten authors, final output; numerator and denominator shown separately · trend: slope of the five per-k ratios R_k on k, weighted by n_k, recomputed in each of 2,000 author-team bootstrap draws (seed 391) · A 557, B 586, U0 599, C 462, R2 28 papers · no trend test was pre-specified for E1 (addenda 7, 8)
【页面精简后移入备注】补充 8 的重跑（E1 标题替换，真 → false_0）；趋势检验是事后、描述性的，补充 7、8 没有为 E1 预设趋势检验；答对次数与组嵌套（0–1 = B，2–3 = U0，4 = A）。
【2026-11-15 更新】上文“都在 L44–52 急升”按补充 18 第 3 项补层结果，应读为：恢复比例主要在 L40–L50 上升（L45 过半；最大的一步在 L47→L48，+0.26 [0.253, 0.272]）。这一页的组别曲线只有已存层，补层只做了全部论文的 5 个假标题平均。
【公式与样本量（v18）】R(l) 与分子 mean(替换 − 假)、分母 mean(真 − 假)；A 557、B 586、U0 599、C 462 篇（页面副标题），R2 28 篇仅参考。
【2026-11-19 整合（v21）】新增小框（来自原第 99 页，已删除）：C 组补全：C 462 篇；同一引用档内 462 篇中的 258 篇与 A 比较，R 到 L52 约为 1。〔b2_cd_report.md〕

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(e1_e2_num_den_B_minus_A.csv)
- 出处（原在幻灯片上）：(rerun_report.md Counts; b2_cd_report.md)

**备查（不念）· 2026-11-23 v60 移出幻灯片的标签和出处（幻灯片上改用通俗名称）：**
- 标签/副标题/表头原写 “Stage 11 E1”、“Addendum 8 · E1 recovery R”、“E1 numerator / R(L48) / R(L52)”、“C R1 × recognised (addendum 11 B)”：E1 = Stage 11 放回（尾部 patching）实验；addendum 8 = 组比较补充登记；addendum 11 B = C/D 组后来补齐

## P32 · HTML v75 p32 · pptx S33 (v22z) — More-cited papers: the title arrives a little later

**要说的话（一句英文一句中文）**
This page asks, as an exploratory check, whether more-cited papers get their title information at a different time.
这一页做一个探索性检查：引用多的论文，标题信息到达的时间是不是不一样？
We split the intervention sample at the median of 31 citations and repeat the put-back test in each half.
我们按引用数中位数 31 把干预样本分成两半，在每一半里重做放回实验。
On the chart, the share recovered at layer 48 is about 0.87 in the low half and about 0.79 in the high half.
图上第 48 层恢复的比例，低引用的一半约 0.87，高引用的一半约 0.79。
By layer 52 both are close to 1, and the gap between recognised and unrecognised does not change with citations.
到第 52 层两半都接近 1，而认得与认不得之间的差距不随引用数变化。
So more-cited papers arrive a little later; this is a clue, not a tested result. Next, the same small-denominator effect in the patched parts.
所以引用多的论文到得稍晚一点；这只是线索，不是检验过的结论。下一页看各个被替换部分里同样的“分母小”效应。

**备查（不念）· 上一版讲稿本页全文（原第 P99 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 探索性（事后，未预注册）：把 Stage 11 的 1,186 篇按引用数中位数（31，并列归低半）分成两半（低半 297 target + 297 control，高半 296 + 296），在每一半里重算 E1 的标题替换恢复比例 R(l) = mean(patched − false) / mean(true − false)（5 个假标题平均），并比较 lens 的 target − control（分箱内，标题特异信号）。作者团队整群 bootstrap 2,000 次，所有比较用同一组抽样；全样本 L48 0.821 / L52 0.995 与已发表值完全一致。来源：381_stage13/summary_explore_citesplit_20261120/（report.md、recovery_by_half.csv、lens_tc_by_half.csv、info.json）。

**关键数字和 CI：**
- R(L48)：低半 0.865 [0.843, 0.886]，高半 0.789 [0.770, 0.808]，高 − 低 −0.076 [−0.104, −0.046]（target −0.079，control −0.073）。
- R(L52)：1.006 对 0.988，高 − 低 −0.018 [−0.029, −0.007]。
- target − control 的 R 在两半之间没有差别（L48 −0.006 [−0.072, +0.065]）。
- logit lens 的 target − control 在 L40–L56 两半之间没有差别（全部含 0）。
- J-lens：引用多的一半自身的 target − control 在 L48–L55 低于 0，但两半之差只在 L53–L55 排除 0（L53 −0.073 [−0.138, −0.010]，L54 −0.076 [−0.141, −0.012]，L55 −0.073 [−0.145, −0.006]），L48–L52 和 L56 含 0；全队列补充（中位数 66）两半之差在 L40–L56 每一层都低于 0（L48 −0.065 [−0.093, −0.038]）。
- n = 1,186 篇（低半 297 + 297，高半 296 + 296）· 全队列补充 6,841 篇。

**结论状态：** 探索性（事后，未预注册）：引用多的论文，标题之后的信息到达稍晚（L48 恢复比例更低，两组都是）；"认得出 vs 认不出"的时间差不随引用数变化；J-lens 中间层的负值在引用多的论文上更强，和"词表拥挤"的解释一致。

**过渡：** 回到识别程度：认得多少会改变大小，但时间几乎不变。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false})}{\mathrm{mean}(\mathrm{true}-\mathrm{false})}$；② n = 1,186 papers (low / high citation halves)；③ R ≈ 1: fully restored; R ≈ 0: nothing restored；原 “How computed” 段：How computed: halves by the median citation count of the 1,186 Stage 11 papers (31; low = 0–31, high = 32–1,010); R(l) as in E1 (mean over 5 false titles, paper means of log10(1/rank)); lens target − control within citation bins; team-cluster bootstrap, 2,000 draws (one draw set); published R(L48) 0.821 / R(L52) 0.995 reproduced exactly · 381_stage13/summary_explore_citesplit_20261120/ (recovery_by_half.csv, lens_tc_by_half.csv)；原出处行：381_stage13/summary_explore_citesplit_20261120/report.md · info.json；方法细节移到备用页 B20 (slide 115)。

**备查（不念）：**
- 副标题与图注原写 “E1 tail patching”、“R(l) as published for E1”：E1 = Stage 11 放回实验

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 高引用那一半的最大引用数是 1,010。

## P33 · HTML v75 p33 · pptx S34 (v22z) — Patched parts: the same small-denominator effect

**要说的话（一句英文一句中文）**
This page asks whether the same denominator effect shows up when we patch only parts of the model.
这一页问：只替换模型的一部分时，是不是也出现同样的分母效应？
We split the single-position and attention-versus-MLP patching by group.
我们把单位置替换和注意力、MLP 的替换按组拆开。
On the chart, the restored amount itself is always smaller for the unrecognised group, about half to two thirds, while the ratio can look larger.
图上认不得的组恢复的量本身总是更小，大约是认得组的一半到三分之二，而比例看起来可能更大。
It is the same pattern as on the previous page: the smaller denominator inflates the ratio.
和上一页一样：分母小把比例撑大了。
So we read the numerators, not just the ratios. Next, the one answer format that helps.
所以我们看分子，不只看比例。下一页看唯一有帮助的答案格式。

**备查（不念）· 上一版讲稿本页全文（原第 P101 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** Stage 12 单位置（P1）和 attention / MLP（P2）按组拆开，只看未写出作者，配对团队 bootstrap 95% CI；比较分子 B − A、比率 B − A 和分子 B/A。

**关键数字和 CI：**
- P1 所有名字位置 L48：分子 B − A −0.105 [−0.123, −0.087]；比率 B − A +0.052 [+0.011, +0.098]；B/A 0.57。
- P1 所有名字位置 L56：−0.183 [−0.209, −0.157]；−0.050 [−0.087, −0.012]；0.50。
- P2 attention L48：−0.029 [−0.038, −0.021]；+0.057 [+0.030, +0.086]；0.66。
- P2 MLP L56：−0.041 [−0.053, −0.029]；+0.008 [−0.030, +0.044]；0.54。
- P1 只有 ':' L48：−0.000 [−0.007, +0.005]；+0.050 [+0.026, +0.071]；0.99。
- P1 只有 ':' L52：−0.013 [−0.024, −0.002]；+0.073 [+0.038, +0.106]；0.79。
- 在 ':' 处，L44–L48 的分子相近（5 个假标题时 B/A 0.72–0.87；false_0 时 0.78–0.99），B 的比率更高只是因为它的分母约为 A 的一半（分母 B − A −0.192，B/A 0.53）。
- n = A 557 / B 586 篇（未写出作者）· 每个假标题 694–711 篇。

**结论状态：** 描述性（分母效应的说明）。

**过渡：** 下一页是几项不需要新 GPU 的检查。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{ratio}\ B-A=R_B-R_A$ · $\mathrm{numerator}=\mathrm{mean}(\mathrm{patched}-\mathrm{false})$；② n = A 557 / B 586 papers · 694–711 per false title；③ ratio B − A > 0: group B recovers a larger share (driven here by B’s smaller denominator)；原公式框：ratio B − A = R B − R A ; numerator = mean(patched − false) n = A 557 / B 586 papers (unwritten authors) · 694–711 papers per false title。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(A 557 / B 586 papers; denominator B − A −0.192, B/A 0.53; p1_p2_num_den_B_minus_A.csv; e1_num_den.md P1/P2)

**备查（不念）：**
- 标签/标题/副标题/表与图原写 “P1 / P2”（Stage 12 单位置 patching = P1，注意力 / MLP 分量 = P2）

**备查（不念）：**
- 标题原写 “P1 / P2: the same small-denominator effect”（P1 = Stage 12 单位置 patching，P2 = 注意力 / MLP patching）；HTML 目录菜单同步改为幻灯片标题 “Patched parts: …”

## P34 · HTML v75 p34 · pptx S35 (v22z) — Giving the first initial unlocks the name

**要说的话（一句英文一句中文）**
This page asks whether giving the model part of the answer lets it write the authors.
这一页问：给模型一部分答案，它能不能写出作者？
In a pre-registered test we tried four answer formats on 600 recognised and 600 unrecognised papers, and compared each with the plain prompt.
在一个预注册检验里，我们对 600 篇认得和 600 篇认不得的论文试了四种答案格式，每种都和普通提示比。
On the chart, a bar above chance means the model writes true authors more often than an author of an unrelated paper would be written by luck.
图上柱子高于机会水平，表示模型写出真作者的频率高于随便写到一篇无关论文作者的概率。
Only one format helps: giving the first author's initial raises the above-chance rate for recognised papers from about 0.02 to about 0.13; the other three formats do not help.
只有一种格式有帮助：给出第一作者的首字母后，认得的论文高于机会水平的比率从约 0.02 升到约 0.13；另外三种格式没用。
So a tiny cue at the start of the name helps; the trouble is in starting the name. Next, the whole gap in one picture.
所以名字开头一个小提示就有用；困难在于名字怎么起头。下一页把整个差距放在一张图上。

**备查（不念）· 上一版讲稿本页全文（原第 P59 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 16（预注册，对 5 个检验做 Holm 校正），贪心生成，600 篇 A + 600 篇 B（另有 300 篇 C，仅描述）。比较不同答案格式 F1–F4 相对基线 F0 的变化。指标 corr = 写出真作者的比率 − 机会比率（同领域固定对照论文作者的比率）；Δ_g = 格式 − F0；DiD = Δ_A − Δ_B；团队整群 95% CI，2,000 次。

**关键数字和 CI：**
- F1 "姓, 名"（任一作者全名）：A 0.037 → 0.070，B 0.003 → 0.015；DiD +0.022，Holm CI [−0.012, +0.055]，p 0.3280。
- F2 只写姓（任一作者姓）：A 0.058 → 0.105，B 0.028 → 0.043；DiD +0.032，Holm CI [−0.012, +0.076]，p 0.2370。
- F3 第一作者姓：A 0.023 → 0.010，B 0.008 → 0.002；DiD −0.007，Holm CI [−0.024, +0.011]，p 0.4430。
- F4 给出名首字母（第一作者姓）：A 0.023 → 0.127，B 0.008 → 0.027；DiD +0.085，Holm CI [+0.047, +0.124]，p 0.0025；F4 单独 Δ_A +0.103。
- n = 每种格式 600 A + 600 B 篇（F0 和 F1–F4 是同一批论文）。

**结论状态：** 预注册判据成立，但只通过 F4（给出真第一作者的首字母）；F1–F3 不成立。局限：标签来自另一次生成运行；shard 0 之后改过停止规则（偏离 D16-4，已记录）；只有贪心解码；C（300 篇）仅描述。

**过渡：** 再看名字链：给出一个真合作者，会不会帮模型写出更多作者？

**探索性补充（幻灯片底部橙色一行，主 pptx S73 同）：** A 组写对至少一位完整作者：F0 4.0% [2.5, 5.6] → F4 15.2% [12.5, 18.0]；仍有 85% 一个都写不出，首字母只修好约 12% 的失败（(15.2 − 4.0) / 96.0）；B 组 0.5% → 3.2%。格式是一个瓶颈，但不是主要的。来源 391_groups/summary_a16_20261115/b_rates.csv。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{corr}=\mathrm{rate}(\mathrm{true\ author})-\mathrm{rate}(\mathrm{chance\ author})$ · $\mathrm{DiD}=\Delta_A-\Delta_B,\ \ \Delta=\mathrm{format}-F0$；② n = 600 A + 600 B papers per format；③ corr > 0: writes true authors above chance / DiD > 0: the format helps recognised papers more；原 “How computed” 段：How computed: corr = rate(true author written) − rate(chance author of a fixed same-field control paper); Δ = format − F0 within a group; DiD = Δ_A − Δ_B. 600 + 600 papers, team bootstrap ×2,000, Holm over 5 tests.；原出处行：391_groups/summary_a16_20261115/ (b_rates.csv, holm.csv) · config/prereg_addendum16.md；方法细节移到备用页 B15 (slide 110)。

**备查（不念）：**
- 标签、副标题、aria 原写 “addendum 16”（Line D · addendum 16；Addendum 16 (pre-registered, Holm over 5 tests)）；警示行原写 “(deviation D16-4, recorded)”：D16-4 = 补充 16 的第 4 条偏离记录（shard 0 之后改了停止规则）

## P35 · HTML v75 p35 · pptx S36 (v22z) — The gap in one picture

**要说的话（一句英文一句中文）**
This page puts the gap between recognising and writing on one citation axis.
这一页把认出和写出的差距放在同一条引用数轴上。
Recognising starts at about 40 citations; writing starts at about 11 thousand.
认出大约从 40 次引用开始；写出要到大约 1.1 万次。
On the chart, rho above 1 means writing needs more exposure than recognising; here it is about 276.
图上 ρ 大于 1 表示写出比认出需要更多曝光；这里大约是 276。
Only rho above 1 is confirmed, because the exact ratio was locked after we had seen the estimates.
只确认 ρ 大于 1，因为确切的比值是看过估计之后才锁定的。
So “recognised but not said” is a large exposure gap. Next, Part 3: what the model reads early, the question and the title.
所以“认得但说不出”是一个很大的曝光差距。接下来是第 3 部分：模型早期读到什么——问题和标题。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Recognised but not said The gap in one picture: writing needs about 276× the exposure of recognising Now asking: on one citation axis, where does recognising start, and where does writing start? · ρ > 1: writing needs more exposure than recognising Result: 1 recognising starts at about 40 citations; 2 writing at about 11,038 . Result: 3 the gap is ρ = 276 [203, 390]. Caveat: the exact ratio was locked after seeing the estimates; only ρ > 1 is confirmed . Source: same fit as slide 24. So (section): recognised but not said is a large exposure gap; next we ask what the model reads early — the question and the title (Part 3). locked · ρ > 1

数字出处：same fit as slide 24 (exposure test)

# Part 3 · Read early: the question and the title (H1) (36–57)

## P36 · HTML v75 p36 · pptx S37 (v22z) — Stage 12–13: what the middle layers hold

**要说的话（一句英文一句中文）**
Before the next parts, this page lays out the three hypotheses we test.
进入后面几部分之前，这一页先列出我们要检验的三个假设。
H1: the middle layers mainly hold the task, “output an author list”. H2: they hold which paper this is. H3: the author information is already there, just not in directions the vocabulary can read.
H1：中间层主要存的是任务，“输出一个作者名单”。H2：存的是这是哪一篇论文。H3：作者信息已经在那里，只是不在词表能读的方向上。
For each hypothesis, the table writes down what three checks should show if it holds: the top word of the lens, a probe for paper attributes, and the change-the-question test.
表里为每个假设写下：如果它成立，三项检查应该看到什么——lens 读出的首位词、读论文属性的 probe、换问题检验。
The last column gives the current result; the details come in the parts that follow.
最后一列是目前的结果；细节在后面几部分展开。
Next, the same table continued for H3.
下一页是这张表关于 H3 的续表。

**备查（不念）· 上一版讲稿本页全文（原第 P68 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**【2026-11-22 v55 · H2 新措辞（用户确定，状态仍为 partly supported）】** 讲这句（英文原句，屏幕上同样写法）：“H2 partly supported: a real-title extra over a same-meaning fabricated title exists (R̄_T +0.106), mostly carried by meaning (75%). The extra sits mainly on the title's rare and specific words (names, acronyms, technical terms): replacing only those words loses R̄ = 0.162, vs 0.027 for common words (addendum 24). It is not larger for recognised papers (K4 not supported) and is smaller for more-cited papers (K4c reversed). Whether the extra reflects specific wording or a penalty on fabricated titles remains open.” 紧接着说明补充 24 的两点：（补充 24 的两点说明：两种替换的词数不同，罕见词平均换 3.4 个、常见词 2.1 个；常见词是按词频匹配替换，不是同义词，意思也会改变。） 中文意思：H2 部分支持：真标题比意思相同的编造标题多出一部分（R̄_T +0.106），大部分由意思承担（75%）。多出的部分主要落在标题里罕见、具体的词上（人名、缩写、专门术语）：只替换这些词损失 R̄ = 0.162，只替换常见词损失 0.027（补充 24）。它在认得出的论文上并不更大（K4 不支持），在引用多的论文上反而更小（K4c 反向）。这多出的部分反映的是具体措辞，还是模型对编造标题的惩罚，仍未确定。

**关键数字和 CI：**
- M2：论文事实（年份、引用、领域）在标题处很早就可读。
- H2：部分支持——存在真实论文成分，但大部分信号可由语义相似解释（补充登记 20，锁定：虚构标题恢复 φ = 0.751，真标题多出 +0.106，第 85 页）；M3 不支持（不超过 L4 文本水平）；X2 单独看：H2 不成立；作者子空间几乎解码不出作者（R² ≤ 0.009）。
- H3：同一尺度上得到支持（补充 17 第 2 项，锁定的确认性检验）：在同样 9,137 个名字 token 上，probe − J-lens 的 target − control：L40 +0.021 [0.008, 0.034]，L48 +0.062 [0.041, 0.081]（只靠补充 11 时，由于尺度不同，只能给"部分支持"）。
- H1：只在 ":" 和名字位置成立（表内：L4–L40 换问题时 ":" 移动 3–5 倍）。
- 最新结果框：H2 标题含义比用词更重要（第 5 项，描述性 → 第 84 页）；意思相同的虚构标题恢复 0.75，真标题多出 +0.11（补充登记 20，锁定 → 第 85 页）；H3 早期痕迹微弱（第 1 项，探索性 → 第 72 页），L52–L56 MLP 内容大部分在作者名字方向之外（第 6 项，描述性 → 第 76 页）；路线：名字位置从 L48 起承载标题，':' 晚到（第 3 项，描述性 → 第 74 页）；名字 ← 标题是 L44–L55 中最大的单条注意力边，但代价 ≤ S 的 3.5%（第 2 项，判据成立、稳健 → 第 75 页）；L57–L61 由 MLP 写入（第 4 项，定论（锁定判据成立） → 第 77 页）。
- n：补充 18b 为 600 篇；H3 同尺度检验 4,654 篇（姓首 token，同一套 9,137 个名字 token，团队整群）；H2 补充 20 为 566 篇 target（最终层）。左侧“How computed”小字同步改为 φ_T、R̄_T 和 probe − J-lens 的算法，来源 a20_report.md、h3_samescale_paired.csv、x1_similarity.md。

**结论状态：** H3：预注册判据成立（补充 17 锁定检验，同一尺度上得到支持）；H2：部分支持，大部分由语义解释（补充登记 20 锁定判据；M3、X2 的预注册判据不支持）；H1：初步。

**过渡：** 下一页把各类信息"最早出现在哪一层"排成一条时间线。

**备查（不念）：**
- 页码指向原写 “→ slide 81”（带 ⚠ 待核页码标记）→ 改指新备用页 B22（slide 118）

**2026-11-23 锁定姓氏检验后的口播补充：**

The overall verdict for H2 has changed with one locked test.  
H2 的总判定因为一个锁定检验改了。

Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal).  
作为一般的“论文身份”表示不成立，只有一个锁定的例外：L8 的标题状态带有一个很小的、本论文特有的姓氏信号——去掉主题后仍在（T1，稳健），超过一个偏弱的纯文本基线（T2，勉强；这个基线没通过它自己的正对照），而且认得的论文更大（T3，勉强）。

About half of that surname signal comes from the topic: 0.44 of it survives topic matching, so it is a small effect, not strong evidence.  
这个姓氏信号大约一半来自主题：配对主题后还剩 0.44，所以是个小效应，不是强证据。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

## P37 · HTML v75 p37 · pptx S38 (v22z) — Stage 12–13: what the middle layers hold (2 of 2)

**要说的话（一句英文一句中文）**
This page continues the hypothesis table with H3 and the latest results.
这一页接着上表，讲 H3 和最新结果。
H3 predicts that a probe sees author information that the lens cannot.
H3 预测：probe 能看到 lens 看不到的作者信息。
On the same name tokens, the probe separates recognised from unrecognised papers better than the lens, which is the locked same-scale test.
在同样的名字 token 上，probe 区分认得和认不得论文的能力强于 lens，这是锁定的同尺度检验。
The other rows will be filled as the parts go on.
其他行会随着后面各部分逐步填上。
Next, the predictions and results side by side.
下一页把预测和结果并排放。

**备查（不念）· 上一版讲稿本页全文（原第 P69 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This page continues the hypothesis table with the third hypothesis, H3.  
这一页接着上一页的假设表，讲第三个假设 H3。

H3 says the author information is already in the middle layers, just not in vocabulary directions.  
H3 说：作者信息已经在中间层里，只是不在词表方向上。

The prediction: a probe can read the authors’ first token, while the lens cannot.  
预测是：probe 能读出作者的第一个 token，而 lens 读不出。

Result: supported on the same scale — probe minus lens is +0.021 at L40 and +0.062 at L48.  
结果：在同一尺度上得到支持——probe 减 lens 在 L40 是 +0.021，在 L48 是 +0.062。

The box on the right lists the latest results for H2, H3 and the route, each with its status tag.  
右边的框列出 H2、H3 和路线的最新结果，每条都带状态标签。

The three grey lines under the table give the formulas, the sample size and how to read each number.  
表下面三行灰字给出公式、样本量和每个量的读法。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** (566 target papers, final layer); H3: probe − J-lens, target − control within bin, same 9,137 name tokens (4,654 papers, team cluster); H1 question share · source: a20_report.md, h3_samescale_paired.csv, x1_similarity.md。

**备查（不念）· 2026-11-23 公式行统一：** 原 “How computed” 段：How computed: H2: φ T = made-up-title share of the true − false gap, R̄ T = mean(S true − S made-up ) (566 target papers, final layer); H3: probe − J-lens, target − control within bin, same 9,137 name tokens (4,654 papers, team cluster); H1 question share；方法细节移到备用页 B16 (slide 111)。

**2026-11-23 锁定姓氏检验后的口播补充：**

In the latest results, the surname signal at L8 survives topic matching, plus 0.046; the other two parts are marginal.  
最新结果里，L8 的姓氏信号去掉主题后还在，+0.046；另外两部分是勉强通过。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** H2 的 φ 和 R̄ 在最后一层计算。

## P38 · HTML v75 p38 · pptx S39–S40 (v22z) — Prediction vs result, per hypothesis

**要说的话（一句英文一句中文）**
This page shows, for each hypothesis, the predictions on the left and what we found on the right.
这一页把每个假设的预测放在左边，实际发现放在右边。
Results that support a hypothesis and results that weaken it are shown separately, so nothing is averaged away.
支持假设的结果和削弱假设的结果分开列出，不互相抵消。
For example, H1 predicted that the lens would mostly read “author” words; it reads punctuation and common name starts instead, unrelated to the title.
例如 H1 预测 lens 主要读出“作者”一类的词；实际读出的是标点和常见的名字开头，和标题无关。
We now test the hypotheses one by one, starting with H1 and the timing of the title.
接下来逐个检验，先从 H1 和标题的时间开始。

**备查（不念）· 上一版讲稿本页全文（原第 P70 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This page is an emphasis view of the hypothesis table.  
这一页是假设表的重点版。

For each hypothesis, the three predictions are on the left and what we found is on the right.  
每个假设，左边是三条预测，右边是实际结果。

H1, task and format: supported at the colon and the name positions; the colon moves 4.7 times more for a new question than for a new paper.  
H1（任务/格式）：在冒号和名字位置成立；换问题时冒号的移动是换论文时的 4.7 倍。

H2, paper identity: a same-meaning made-up title recovers 75%, and the real title adds R-bar +0.106.  
H2（论文身份）：意思相同的编造标题恢复 75%，真标题多出 R̄ +0.106。

But the extra sits on rare words and is not larger for recognised papers, so H2 is only partly supported.  
但多出的部分落在罕见词上，在认得出的论文上也不更大，所以 H2 只是部分支持。

H3, hidden authors: supported on the same scale by the name-position probe.  
H3（隐藏的作者）：名字位置的 probe 在同一尺度上支持。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** add. 22 K4/K4c。

**2026-11-23 锁定姓氏检验后的口播补充：**

The evidence matrix gets one new column, the locked surname test: it supports H2 only in a small way.  
证据矩阵加了一列“锁定姓氏检验”：它只在很小的程度上支持 H2。

Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal).  
作为一般的“论文身份”表示不成立，只有一个锁定的例外：L8 的标题状态带有一个很小的、本论文特有的姓氏信号——去掉主题后仍在（T1，稳健），超过一个偏弱的纯文本基线（T2，勉强；这个基线没通过它自己的正对照），而且认得的论文更大（T3，勉强）。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

## pptx S89（仅主 pptx，HTML deck 无对应页）— Update 2026-11-17/18

**要说的话（一句英文一句中文）**
This is your own summary table, with a small update box beside it.
这是你自己做的汇总表，旁边加了一个小的更新框。
The update gives the current H2 wording: not a general paper identity, with one small locked exception, the surname signal from layer 8.
更新框给出现在 H2 的说法：不是一般意义上的论文身份，有一个小的锁定例外，就是从第 8 层起的姓氏信号。
The table itself is unchanged.
表格本身没有改动。

**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**
（主 pptx 当前页码：S39；HTML deck 无对应页。）

**【2026-11-22 v55 · H2 新措辞（用户确定，状态仍为 partly supported）】** 讲这句（英文原句，屏幕上同样写法）：“H2 partly supported: a real-title extra over a same-meaning fabricated title exists (R̄_T +0.106), mostly carried by meaning (75%). The extra sits mainly on the title's rare and specific words (names, acronyms, technical terms): replacing only those words loses R̄ = 0.162, vs 0.027 for common words (addendum 24). It is not larger for recognised papers (K4 not supported) and is smaller for more-cited papers (K4c reversed). Whether the extra reflects specific wording or a penalty on fabricated titles remains open.” 紧接着说明补充 24 的两点：（补充 24 的两点说明：两种替换的词数不同，罕见词平均换 3.4 个、常见词 2.1 个；常见词是按词频匹配替换，不是同义词，意思也会改变。） 中文意思：H2 部分支持：真标题比意思相同的编造标题多出一部分（R̄_T +0.106），大部分由意思承担（75%）。多出的部分主要落在标题里罕见、具体的词上（人名、缩写、专门术语）：只替换这些词损失 R̄ = 0.162，只替换常见词损失 0.027（补充 24）。它在认得出的论文上并不更大（K4 不支持），在引用多的论文上反而更小（K4c 反向）。这多出的部分反映的是具体措辞，还是模型对编造标题的惩罚，仍未确定。

【2026-11-18 整合（v20）】这一页是用户自己的表格图片，没有改动；在右侧空白处加了"Update 2026-11-17/18"小框：H2（论文身份）← 第 5 项，标题的意思比字面重要（描述性），仍不能和论文身份分开；H3（隐藏作者）← 第 1 项早期痕迹（探索性、未校正），第 6 项 L52–56 MLP 内容大部分不在作者名字输出方向上（描述性），与"信息在、但不在词表方向上"一致；路径 ← 第 4 项（确认）。
【2026-11-19 整合（v22）】右侧 Update 小框（我们加的框，用户的表格未动）："Route" 一条补上第 3 项（名字位置从 L48 起承担，":" 较晚，描述性，第 82 页）和第 2 项（名字 ← 标题 是 L44–L55 最大的单条注意力边，但只占 S 的 ≤ 3.4%；锁定规则满足，稳健性尚未确立，第 83 页）；页码顺延（85、80、81）。框加高。
【2026-11-19 整合（v22c）】Route 一条中第 2 项改为：锁定规则满足，对窗口位置稳健（修复后的步长 2 检查 11 个重叠窗口中 7 个满足，同一条边）；效果 ≤ S 的 3.5%。
【2026-11-20 整合（v22e）】右侧 Update 小框（我们加的框）H2 一条："still not separable from paper identity" 改为补充登记 20 的锁定结果：意思相同的虚构标题恢复 0.75，真标题多出 +0.11 → 部分支持，大部分可由语义解释（第 90–91 页）。框加高。
【2026-11-21 晚（v22j），用户授权修改】左边原来的表格图片（report v30 版）换成同位置同大小的可编辑表格，内容与 HTML 第 68 页一致：H1 在 ":" 和名字位置成立（较稳；“:” 换问法比换论文多动 4.7×/3.0×/2.2×）；H2 部分支持、语义解释大部分（确认：φ = 0.75 [0.723, 0.778]，R̄ = +0.106 [0.094, 0.118]，补充 20）；H3 同尺度下支持（补充 17：probe − lens L40 +0.021 [0.008, 0.034]，L48 +0.062 [0.041, 0.081]）。颜色：支持蓝、部分黄、削弱红（H2 × M3 格）。S81 表格 H3 格加“(add. 17)”。

## P39 · HTML v75 p39 · pptx S41 (v22z) — Question card · H1: is the answer format fixed in the middle layers?

**要说的话（一句英文一句中文）**
This question card opens Part 3: what would we see if the middle layers mainly encoded the task, “output an author list”?
这张问题卡开启第 3 部分：如果中间层主要编码的是任务“输出作者名单”，我们会看到什么？
If H1 holds, the state at the colon should move more when the question changes than when the paper changes, and the format should be locked in at some middle layer.
如果 H1 成立，冒号位置的状态在换问题时应该比换论文时变化更大，而且格式应该在某个中间层定下来。
If H1 fails, the colon moves as much for a new paper as for a new question, and the answer type can still be changed late.
如果 H1 不成立，换论文和换问题时冒号的变化一样大，答案类型到很晚还能被改变。
This part asks two questions: first, when is the title read; second, when is the answer format fixed.
这一部分问两个问题：第一，标题什么时候被读；第二，答案格式什么时候定下来。
We start with the title.
先从标题开始。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Question card · H1: is the answer format set in the middle layers? Part 3 · Read early: the question and the title (H1) Question card · Part 3: title (3a) and format (H1, 3b) Now asking: what would we see if the middle layers mainly encode the task ("output an author list")? If H1 holds, we expect 1 the ":" state moves more when the question changes than when the paper changes 2 a knockout of the question words before a middle layer changes the answer type, after it does not 3 swapping the ":" state between questions switches the answer type from that middle layer on If H1 fails, we expect 1 the ":" state moves as much for a new paper as for a new question 2 the answer type can still be changed late (after L48) 3 no layer where the format is locked in Two questions: 3a when is the title read? → slides 40–47 · 3b H1: when is the answer format fixed? → slides 49–54 Tests in this part: 1 distance ratio at ":" → slide 51 · 2 format-locking knockout (pre-registered) + supplementary attention-sink checks → slide 52 · 3 ":" swap at L56 → slide 52 Earlier pages: same title, different question → slide 49 · layer order → slide 50 · ratio curves in full → slide 150 Caveat: only the authors question gives a usable format measure; year/field answers are too often wrong at baseline question card · H1 hypothesis So (this slide): three predictions, three tests; the verdict card at the end of this part scores each one.

数字出处：27_v67/fragments/part34_numbers.md

## P40 · HTML v75 p40 · pptx S42 (v22z) — Part 3a · When is the title read?

**要说的话（一句英文一句中文）**
Part 3a asks: at which layers is the title read, and from when is it no longer needed?
第 3a 部分问：标题在哪几层被读，从什么时候起就不再需要？
First we read with lenses, then we intervene with the put-back and take-away tests.
先用 lens 读，再用放回和拿走两种实验去干预。
If the title is read early, putting it back should restore most of the advantage before the late layers, and taking it away late should cost nothing.
如果标题读得早，放回实验在后期层之前就应该恢复大部分优势，晚些拿走也不会有损失。
Let's see the timing pages.
来看时间这几页。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Part 3a Part 3a · When is the title read? Now asking: at which layers is the title read, and from when is it no longer needed? Question: when does the paper information arrive at the positions after the title? What we did: read with lenses (slides 41, 42), then intervene: put back and take away (slides 43–46) If read early, we expect: put back restores most of the true-title advantage before the late layers; taking the title away late costs nothing What follows: the timing pages, slides 40–47; then 3b asks about the question format (slide 48) So (section): first the title: when is it read and delivered? settled

## P41 · HTML v75 p41 · pptx S43 (v22z) — When does it appear, and when is it used?

**要说的话（一句英文一句中文）**
This page asks when the paper information arrives, and when it is used.
这一页问：论文信息什么时候到，什么时候被用？
The small samples kept pointing at layer 56 as the peak.
小样本一再把第 56 层指为峰值。
The full cohort gives a sharper answer: the names become readable only late, in layers 57 to 61, but the title is read much earlier, between layers 24 and 50.
全队列给出更清楚的答案：名字到很后面的第 57 到 61 层才读得出来，但标题早得多，在第 24 到 50 层就读了。
The route tests add that the late rise is written by the MLPs.
路线检验还补充了一点：后期的上升是 MLP 写出来的。
So readable late, read early. Next, when the recognised group pulls ahead.
所以读出得晚，读取得早。下一页看认得的组什么时候领先。

**备查（不念）· 上一版讲稿本页全文（原第 P44 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 小样本问的是：哪一层是峰值（L56 一再突出）？全队列的回答是：在后层（L57–61）才可读，但从标题读取信息发生在更早的 L24–50。另附补充 18b：L57–L61 的上升是谁写的？是 MLP（第 4 项，定论（锁定判据成立））→ 第 77 页；L52–L56 的 MLP 携带论文信息，而不是名字方向（第 6 项，描述性）→ 第 76 页；哪些位置、哪条注意力边在承载（第 3、2 项；描述性 / 判据成立，对窗口位置稳健）→ 第 74–75 页。Stage 4 和 7.2 的小样本结果放在 A 线（第 13、15 页），小结页（第 51 页）引用它们；Stage 11 的设计见第 47 页及其后的方法图。

**过渡：** 先看全队列里 target 从哪一层开始领先。

## P42 · HTML v75 p42 · pptx S44 (v22z) — Target pulls ahead only in the last layers

**要说的话（一句英文一句中文）**
This page asks when the recognised group pulls ahead of the unrecognised one.
这一页问：认得的组什么时候领先认不得的组？
We compare them inside citation bins, layer by layer, with the lenses and with the real output.
我们在引用档内逐层比较两组，用 lens 也用真实输出。
On the chart, target minus control above zero means target authors read better, and near zero means no head start.
图上 target 减 control 大于 0 表示认得组的作者读得更好，接近 0 表示没有领先。
In the middle layers there is no head start; at the last layer and the output the gap is about 0.21 to 0.23.
中间层没有领先；到最后一层和输出层，差距大约是 0.21 到 0.23。
So the lead appears only at the end. Next, how fast it builds up.
所以领先只在最后出现。下一页看它积累得多快。

**备查（不念）· 上一版讲稿本页全文（原第 P45 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 档内 target − control，带 95% CI。左图：真标题条件的原始读出；右图：title-specific（真 − 5 个假标题均值）。比较 public、logit lens 和模型输出；名字位置，3,734 + 2,182 篇，论文 bootstrap。

**关键数字和 CI：**
- 中间层：没有领先。
- L62 / 输出：+0.21 到 +0.23（Stage 10，L62 + final L63，3,734 + 2,182 篇，§6.4），几乎全是 title-specific。
- 只看 R0（没有写出作者）：输出 +0.199 vs +0.207（Stage 10，3,423 + 2,151 篇 R0，§6.13）。
- n = 3,734 + 2,182 篇。

**结论状态：** 定论。

**过渡：** 把 L40–L62 的每一层都补上，看它具体是怎样积累起来的。

**图旁公式（灰色行）：** y = T − C within citation bins of spec,  spec = nlr(true) − mean₅ nlr(false),  nlr = log₁₀(1/rank) · n = 3,734 target + 2,182 control papers, name positions

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, name positions · paper bootstrap · source: B_spec_target_vs_control_within_bin.csv。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $y=T-C\ \mathrm{within\ citation\ bins\ of\ spec}$ · $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$ · $\mathrm{nlr}=\log_{10}(1/\mathrm{rank})$；② n = 3,734 target + 2,182 control papers；③ T − C > 0: target authors read better than control / T − C ≈ 0: no head start；原 “How computed” 段：How computed: within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, name positions · paper bootstrap；原公式框：[formula] · [formula] · [formula] · [formula] T − C > 0: target authors read better than control T − C ≈ 0: no head start；方法细节移到备用页 B14 (slide 109)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 读的是名字位置。

## P43 · HTML v75 p43 · pptx S45 (v22z) — It builds up over the last dozen layers

**要说的话（一句英文一句中文）**
This page asks how fast the gap builds up.
这一页问：差距积累得有多快？
We fill in every layer from 40 to 62 and read the gap with the logit lens.
我们把第 40 到 62 层每一层都补上，用 logit lens 读差距。
On the chart, target minus control above zero means target authors read better; it is about 0.007 at layer 50 and about 0.23 at layer 62.
图上 target 减 control 大于 0 表示认得组作者读得更好；第 50 层约 0.007，第 62 层约 0.23。
The steepest rise is in layers 57 to 61.
上升最陡的是第 57 到 61 层。
So the readable gap is built in the last dozen layers. Next, we stop only reading and start intervening.
所以读得出的差距是在最后十几层积累起来的。下一页我们不只读，开始动手干预。

**备查（不念）· 上一版讲稿本页全文（原第 P46 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 细层 L40–L62（L41–L47、L49 由第 3-1 项补上，结论不变），title-specific 信号，95% CI。左图：logit lens 分 target / control；右图：target − control（logit lens 和 public）。

**关键数字和 CI：**
- logit lens target − control：L50 +0.007；L62 +0.23（Stage 10 logit lens，3,734 + 2,182 篇，§6.10）。
- 上升最陡的是 L57–L61。
- n = 3,734 + 2,182 篇。

**结论状态：** 定论。

**过渡：** 读出只能告诉我们哪里"可读"，要知道哪里在"用"，得做干预。下一页是 Stage 11 的设计。

**图旁公式（灰色行）：** y = T − C within citation bins of spec,  spec = nlr(true) − mean₅ nlr(false),  nlr = log₁₀(1/rank) · n = 3,734 target + 2,182 control papers, L40–L62

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, L40–L62 (L41–L47, L49 filled by item 3-1, conclusion unchanged) · paper bootstrap · source: B_spec_target_vs_control_within_bin.csv。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $y=T-C\ \mathrm{within\ citation\ bins\ of\ spec}$ · $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 3,734 target + 2,182 control papers, L40–L62；③ T − C > 0: target authors read better than control；原 “How computed” 段：How computed: within-bin target − control of spec = true − mean(false_0..4) · 3,734 + 2,182 papers, L40–L62 (L41–L47, L49 filled by a later run, conclusion unchanged) · paper bootstrap；原公式框：[formula] · [formula] · [formula] T − C > 0: target authors read better than control；方法细节移到备用页 B14 (slide 109)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** L41–L47、L49 由后续运行补齐，结论不变。

## P44 · HTML v75 p44 · pptx S46 (v22z) — Stage 11: intervene, do not just read

**要说的话（一句英文一句中文）**
This page asks: if we intervene instead of only reading, when is the title read?
这一页问：如果不只是读，而是干预，标题是什么时候被读的？
We use about 600 recognised and 600 unrecognised papers, and two interventions: put the true-title states back into a false-title run, or block the later tokens from the title.
我们用大约 600 篇认得和 600 篇认不得的论文，做两种干预：把真标题的状态放回假标题运行，或者阻断后面的 token 看标题。
On the chart, a share near 1 means the intervened run scores like the true-title run: fully restored for put-back, nothing lost for take-away.
图上比例接近 1 表示干预后的运行和真标题运行一样：放回时是完全恢复，拿走时是没有损失。
These tests time the reading itself, not just when it becomes readable.
这些实验测的是读取本身的时间，而不只是什么时候读得出来。
Next, the result.
下一页看结果。

**备查（不念）· 上一版讲稿本页全文（原第 P47 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 593 + 593 篇（每个引用档取 min(60, n_t, n_c)，种子 11）。四种方法：patch（在某一层把真标题的隐藏状态复制进假标题运行，用 false_0）；knock out（从第 l 层到最后一层阻断对标题 token 的注意力，所有 head）；probe（从最后一个标题 token 到输出状态的线性映射）；chain（"Authors: A1, A2, ..." 代替每个作者单独出现）。probe 和 chain 用全部 9,108 篇。分数是模型输出层上正确名字 token 的排名。

**关键数字和 CI：**
- share = (干预后 − 假) / (真 − 假)。
- n = 593 + 593 篇（patch、knockout）· 9,108（probe、chain）。

**结论状态：** 方法页。

**过渡：** 先用方法图把 patching 和 knockout 讲清楚。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{share}=\frac{\mathrm{intervened}-\mathrm{false}}{\mathrm{true}-\mathrm{false}}$；② n = 593 + 593 (patch, knockout) · 9,108 (probe, chain)；③ share ≈ 1: the intervened run scores like the true-title run (put back: restored; take away: nothing lost)；原公式框：[formula] · [formula]；原公式框：share ≈ 1: fully brought back。

## P45 · HTML v75 p45 · pptx S47–S48 (v22z) — The title is read in L24–L50, early

**要说的话（一句英文一句中文）**
This page asks when the title is actually read.
这一页问：标题到底是什么时候被读的？
We put back the states after the title at one layer, or block the title from one layer on.
我们在某一层把标题之后的状态放回，或者从某一层起阻断标题。
On the chart, R near 1 means fully restored, and a loss near zero means nothing lost, so the reading is done.
图上 R 接近 1 表示完全恢复，损失接近 0 表示没有损失，也就是读取已经完成。
The title is read between layers 24 and 50; from layer 52 on it is no longer needed, and recognised and unrecognised papers follow the same timing.
标题在第 24 到 50 层被读；从第 52 层起就不再需要，认得和认不得的论文时间进程相同。
So the title is read early. Next, whether this holds for every false title.
所以标题读得早。下一页看这一点是不是对每个假标题都成立。

**备查（不念）· 上一版讲稿本页全文（原第 P50 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型输出层，看真−假差距被恢复或损失的比例（CI 约 ±0.02；Stage 11 E1/E2，593 + 593 篇，§6.11）。左图：在第 l 层把标题之后的 token 从真标题 patch 到假标题（target、control，另画"只 patch 最后一个标题 token"）；右图：从第 l 层起阻断对标题的注意力（全部后续 token、":" + 名字）。用 false_0，论文 bootstrap。

**关键数字和 CI：**
- L52 起：标题不再被需要。
- 信息在 L44–52 进入名字位置，部分经由标题后紧邻的 token。
- target 和 control 的时间进程相同。
- n = 593 + 593 篇。

**结论状态：** 定论（第 79 页用 5 个假标题复现了 X6/X7 的时间进程；X7 的预注册判定见第 79 页）。

**过渡：** 汇总 C 线。

**图旁公式（灰色行）：** R(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p];   loss(l) = mean_p[K̄_p(64) − K̄_p(l)] / mean_p[T̄_p − F̄_p] · n = 1,186 papers (593 + 593), false_0

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p]; loss(l) = mean_p[K̄_p(64) − K̄_p(l)] / mean_p[T̄_p − F̄_p] · 593 + 593 papers, false_0 · paper bootstrap · source: E1_recovery.csv, E2_knockout.csv。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{mean}_p[\bar P_p(l)-\bar F_p]}{\mathrm{mean}_p[\bar T_p-\bar F_p]}$ · $\mathrm{loss}(l)=\frac{\mathrm{mean}_p[\bar K_p(64)-\bar K_p(l)]}{\mathrm{mean}_p[\bar T_p-\bar F_p]}$；② n = 1,186 papers (593 + 593), false_0；③ R ≈ 1: fully restored / loss ≈ 0: nothing lost — reading done；原 “How computed” 段：How computed: recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p]; loss(l) = mean_p[K̄_p(64) − K̄_p(l)] / mean_p[T̄_p − F̄_p] · 593 + 593 papers, false_0 · paper bootstrap；原公式框：[formula] · [formula] · [formula] R ≈ 1: fully restored · loss ≈ 0: nothing lost — reading done；方法细节移到备用页 B15 (slide 110)。

## P46 · HTML v75 p46 · pptx S49–S50 (v22z) — The Stage 11 timing holds for all 5 false titles

**你在讲稿 doc 里写的批注（从 doc 原样搬来，原在上一版本页的标题下面）：**

【】

**要说的话（一句英文一句中文）**
This page asks whether the timing depends on which false title we use.
这一页问：时间进程会不会取决于用哪个假标题？
We repeat the put-back test with each of the five false titles, and the take-away test with a matching knockout on the false-title run subtracted.
我们用 5 个假标题分别重做放回实验；拿走实验则减去在假标题运行上做同样阻断的结果。
On the chart, R near 1 means fully restored; averaged over five false titles it is about 0.82 at layer 48 and essentially 1 at layer 52, and the five curves almost overlap.
图上 R 接近 1 表示完全恢复；5 个假标题平均，第 48 层约 0.82，第 52 层基本是 1，5 条曲线几乎重合。
The take-away loss from layer 52 is below the pre-set line of 0.05 for all groups.
从第 52 层起拿走标题的损失，各组都低于事先定的 0.05 判定线。
So the timing holds for all five false titles. Next, how the two timing tests work.
所以时间进程对 5 个假标题都成立。下一页说明这两种时间实验是怎么做的。

**备查（不念）· 上一版讲稿本页全文（原第 P79 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** X6：分别用 5 个假标题做替换（patching）；X7：knockout 减去在假标题运行上做同样 knockout 的结果（S = T − F）。1,186 篇，团队整群 95% CI。决策线 S = 0.05。

**关键数字和 CI：**
- X6 R(l)（5 个均值）：L24 0.080 [0.075, 0.086]；L40 0.302 [0.290, 0.315]；L48 0.821 [0.806, 0.835]；L52 0.995 [0.990, 1.001]；之后约 1.0；5 个假标题各自的曲线几乎重合。
- X7 S(L52)（5 个均值）：target +0.022 [+0.015, +0.029] ≤ 0.05；control +0.042 [+0.028, +0.055] ≤ 0.05；全部 +0.028 [+0.022, +0.035] ≤ 0.05。
- 按名字 token 角色：L48 时姓氏第一个 token 0.734，姓氏后续 0.893；L52 所有角色 ≥ 0.96。
- 预注册判定（只用 false_0）：target S(L52) 0.018 成立，control 0.051 以微小差距没过 0.05；用 5 个均值时所有组都通过。
- n = 1,186 篇（593 target + 593 control）。

**结论状态：** 预注册判据：target 成立，control 不成立（0.051 vs 0.05，差一点）；按补充 10 的 5 个假标题均值，所有组成立。时间进程本身为定论。

**过渡：** 下面三页是 Stage 13 的 X 系列：同一个标题换成不同问题会怎样？

**图旁公式（灰色行）：** R(l) = mean(patched − false) / mean(true − false), mean of 5;   S(l) = T(l) − F(l) · n = 1,186 papers (593 + 593)

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** By name-token role: X6 roles, all papers; x6x7_roles.md；Pre-registered verdict (false_0 only): X7 x7_report.md；addendum 10 item 2, b1_x7f_report.md；381_stage13/summary_x6/x6_recovery.csv · summary_b1_x7f/x7f_knockout.csv · x6_report.md, x7_report.md。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false})}{\mathrm{mean}(\mathrm{true}-\mathrm{false})}$ · $S(l)=T(l)-F(l)$；② n = 1,186 papers (593 + 593), R: mean of 5 false titles；③ R ≈ 1: fully restored / S ≈ 0: nothing lost — reading done；原 “How computed” 段：How computed: put back R(l) = mean(patched − false) / mean(true − false) per false title, averaged over 5; take away S(l) = T(l) − F(l), the knockout loss minus the same knockout on the false-title run. 1,186 papers, team-cluster 95% CI.；原公式框：[formula] · [formula] R: mean of 5 false titles [formula] R ≈ 1: fully restored S ≈ 0: nothing lost — reading done；方法细节移到备用页 B18 (slide 113)。

## P47 · HTML v75 p47 · pptx S51 (v22z) — Backup B12 · Timing tests: criteria and per-title numbers

**要说的话（一句英文一句中文）**
This backup page gives the timing test criteria and the numbers for each false title, shown only if asked.
这张备用页给出时间实验的判定标准和每个假标题的数字，只有被问到时才展示。

**备查（不念）· 上一版讲稿本页全文（原第 P108 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This backup page holds the criteria and the per-title numbers behind slide 79.  
这张备用页放第 79 页背后的判据和每个假标题的数字。

The pre-registered knockout rule: S at L52 at most 0.05, and S at L0 at least 0.5.  
预注册的阻断判据：S(L52) ≤ 0.05，且 S(L0) ≥ 0.5。

With false_0 only, control misses by 0.001; with the mean of five false titles all groups pass, but the control interval crosses 0.05.  
只用 false_0 时 control 差 0.001 没过；用 5 个假标题的平均，各组都过，但 control 的区间跨过 0.05。

Put back R is 0.81 to 0.83 at L48 and 0.99 to 1.00 at L52 for every false title.  
每个假标题的放回 R 在 L48 是 0.81–0.83，在 L52 是 0.99–1.00。

The arrival rule gives half-way at L45 and full arrival at L50.  
到达判据给出：L45 到一半，L50 全部到达。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $S(L52)=T(L52)-F(L52)$ · $R(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false})}{\mathrm{mean}(\mathrm{true}-\mathrm{false})}$；② n = 1,186 papers (593 + 593), team-cluster 95% CI；③ S ≈ 0: nothing lost — reading done (decision line 0.05) / R ≈ 1: fully restored；原公式框：[formula] · [formula] team-cluster 95% CI, 2,000 draws [formula] S ≈ 0: nothing lost — reading done (decision line 0.05) R ≈ 1: fully restored。

**备查（不念）：** knockout 判据 = 补充登记 3（锁定）；5 个假标题平均 = 补充 10；到达判据 = 补充 18 第 3 项（锁定）。

## P48 · HTML v75 p48 · pptx S52 (v22z) — How the two timing tests work

**要说的话（一句英文一句中文）**
This page explains how the put-back and take-away tests time the reading.
这一页说明放回和拿走两种实验怎么测出读取的时间。
Put-back copies all fifteen positions after the title from the true run into the false run at one layer; take-away blocks those positions from reading the title from one layer to the end.
放回是在某一层把标题之后全部 15 个位置从真运行复制到假运行；拿走是从某一层到最后，阻断这些位置去读标题。
On the chart, R near 1 means fully restored, and S near zero means nothing lost.
图上 R 接近 1 表示完全恢复，S 接近 0 表示没有损失。
By the locked rule, half the advantage has arrived by layer 45 and all of it by layer 50; the name is written later, at layers 57 to 61.
按锁定规则，第 45 层到达一半，第 50 层全部到达；名字要到更后面的第 57 到 61 层才写出。
So the title is read by layer 52. Next, a summary of what we saw.
所以标题到第 52 层已经读完。下一页小结我们看到了什么。

**备查（不念）· 上一版讲稿本页全文（原第 P80 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This page shows how the two timing tests work, on one real paper.  
这一页用一篇真实论文说明两个时间检验怎么做。

Put back: we copy the states of all 15 positions after the title from the true-title run into the false-title run, one layer at a time.  
放回：把真标题运行里标题之后全部 15 个位置的状态，逐层复制到假标题运行里。

The last name token is only scored, never copied; the model still has to predict it.  
最后一个名字 token 只用来打分，从不复制；模型仍然要自己预测它。

The restored share, R of l, is how much of the true-title advantage comes back.  
恢复比例 R(l) 就是真标题优势回来了多少。

Take away: from layer l up, we block attention from every position after the title to every title token.  
拿走：从第 l 层往上，阻断标题之后每个位置对每个标题 token 的注意力。

The loss, S of l, is the drop with the true title minus the same block on the false-title run.  
损失 S(l) 是真标题下的下降，减去在假标题运行上做同样阻断的下降。

Both tests use five matched false titles and compare target with control papers.  
两个检验都用 5 个匹配的假标题，并比较 target 和 control 论文。

The five false titles are named false_0 to false_4, the same names as on the previous page and in backup B12.  
五个假标题记作 false_0 到 false_4，和上一页、备用页 B12 的叫法一致。

So, for this section: the title is read by L52 — by the locked rule half-way at L45 and fully arrived at L50 — and the name is written later, at L57 to L61; the route is on slides 73 to 77.  
本节结论：标题在 L52 前读完——按锁定规则 L45 过半、L50 完全到达——名字在之后的 L57–L61 才写出；路线见第 73–77 页。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** Copied / blocked positions follow the Stage 11 code (361_stage11.py do_patch, do_knockout): the aligned post-title tail shared by the true and false prompts (closing quote, year, “Authors:”) plus every name-input position；the last name token is only scored, never fed in. 1,186 papers (593 target + 593 control) · x6_report.md, x7_report.md, b1_x7f_report.md · tokens: Qwen3-32B tokenizer, name_tokens.parquet。

**备查（不念）：**

## P49 · HTML v75 p49 · pptx S53 (v22z) — What we saw: “When does it appear and when is it used?”

**要说的话（一句英文一句中文）**
This page sums up the timing story.
这一页小结时间这条线。
The small samples saw a peak at layer 56, and one paper drove most of it.
小样本看到第 56 层的峰值，其中大部分来自一篇论文。
The full cohort showed that layer 56 is where the rise starts, and the steepest rise is in layers 57 to 61.
全队列显示第 56 层只是上升的起点，最陡的上升在第 57 到 61 层。
The interventions filled in what reading could not see: copying the states recovers about 80 to 87% at layer 48 and almost all from layer 52, and blocking the title from layer 52 costs nothing.
干预补上了读出看不到的部分：复制状态在第 48 层恢复大约 80% 到 87%，从第 52 层起几乎全部恢复；从第 52 层起阻断标题没有代价。
So read early, said late. Next, Part 3b: when is the answer format fixed?
所以是读得早、说得晚。接下来是第 3b 部分：答案格式什么时候定下来？

**备查（不念）· 上一版讲稿本页全文（原第 P51 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 小样本：Stage 4 的 L56 峰值由一篇论文驱动（71%）；7.2 的 A−B 胜率在 L40–L56 为正；7.3 和 8 看到 L56 的标题优势，L56 被定为主层。全队列：L56 是起点，最陡的上升在 L57–L61；patching：复制尾部状态在 L48 恢复 80–87%，从 L52 起恢复 99.6%（Stage 11 E1，593 + 593；x6_report.md）；knockout：从 L52 起阻断标题没有代价；L57–L61 由 MLP 写入：MLP − attention 损失 +0.040 [0.036, 0.045]（第 4 项，定论（锁定判据成立））→ 第 77 页；L52–L56 的 MLP 携带论文信息，几乎不沿作者名字方向（第 6 项，描述性）→ 第 76 页；名字位置从 L48 起承载标题（L52 时 0.84；第 3 项，描述性），单条注意力边的代价 ≤ S 的 3.5%（第 2 项，锁定判据在 L44–L55 成立，对窗口位置稳健）→ 第 74–75 页。

**关键数字：** 见上；n = 20–200（Stages 1–9）· 9,108（10）· 1,186（11）· 600（补充 18b）。

**结论状态：** C 线时间进程为定论；MLP 写入为定论（锁定判据成立）；L52–L56 MLP 内容为描述性；名字位置承载（第 3 项）为描述性；单条注意力边（第 2 项）为预注册判据成立、对窗口位置稳健（效应小）。一句话："读得早，说得晚"。L56 确实是一个地标，但不是峰值；干预补上了读出看不到的部分：标题在 L24–50 被消化，答案要到十几层之后才在名字处变得可读。

**过渡：** 进入 D 线：哪个 token 在承载信息。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** ​(audit_report.md)；​(Stage 11 E1, 593 + 593; x6_report.md)。

## P50 · HTML v75 p50 · pptx S54 (v22z) — Part 3b · H1: when is the answer format fixed?

**要说的话（一句英文一句中文）**
Part 3b asks the H1 question: does the question settle the answer format in the middle layers?
第 3b 部分问 H1 的问题：问题是不是在中间层就把答案格式定下来了？
We compare the same title under different questions, look at the layer order, measure how far the colon moves, and knock out or swap the colon state.
我们比较同一个标题在不同问题下的情况，看各类信息出现的层序，测冒号位置移动多远，再阻断或替换冒号位置的状态。
If H1 holds, the format is fixed at a middle layer and cannot be changed after it.
如果 H1 成立，格式会在某个中间层定下来，之后就改不了。
One caveat up front: only the authors question gives a usable format measure.
先说明一点：只有问作者的问题能给出可用的格式测量。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Part 3b Part 3b · H1: when is the answer format fixed? Now asking: does the question settle the answer format in the middle layers? Question: H1 says the middle layers mainly encode the task (“output an author list”) What we did: compare the same title under different questions (slide 49), the layer order (slide 50), the “:” distance ratio (slide 51), knockout and swap at “:” (slide 52) If H1 holds, we expect: the format is fixed at a middle layer and cannot be changed after it Caveat: only the authors question gives a usable format measure So (section): then the question format; the verdict card (slide 53) scores H1. locked · H1 revised

## P51 · HTML v75 p51 · pptx S55 (v22z) — Same title, different question

**你在讲稿 doc 里写的批注（从 doc 原样搬来，原在上一版本页的标题下面）：**

【

**M3**

M3 要回答的不是"两个 state 整体像不像"，而是"**某一种信息在两种问题下是不是用同样的方式存的**"。probe 正好能测这一点：在一种问题下学会的"读法"，换到另一种问题下还能不能用。

**T** = 换了问题后的准确率 ÷ 不换问题的准确率。T = 1 表示换问题完全不影响；T 越小，影响越大。

T = acc(train q₁ → test q₂) / acc(train q₂ → test q₂), mean of 6 ordered question pairs

**p****robe 在这里具体测什么**

**举个例子**（q₁ = 问作者，q₂ = 问年份）

- 用"问年份"的 state 训练，在"问年份"的 state 上测：准确率 80%（分母）
- 用"问作者"的 state 训练，在"问年份"的 state 上测：准确率 79%（分子）
- T = 79 / 80 ≈ 0.99
  - **还读得准**：领域信息在两种问题下用同样的方式存储，与问题无关；——证实**H2（存的是"这是哪篇论文"）**
  - **读不准**：信息的存储方式跟着问题变了，即使信息本身可能还在。——**H1（存的是"要完成什么任务"）——冒号**

结果是：标题位置 T 高（≈0.99）——标题位置的 state 主要由标题自己的词决定，模型读标题时，几乎不会因为问题不同而改变对标题的表示。冒号位置 T 低（0.24–0.41）。——冒号位置按问题组织。

**但在标题位置，probe 也绕不开天花板**

三个 prompt 里标题的字一样，state 几乎相同，所以无论用 cosine 还是 probe，结果都是"几乎不变"，而且在 L4 就是这样。所以在标题位置，probe 并没有比 cosine 多告诉我们什么。

probe 真正有信息量的是**冒号位置**：cosine 只能告诉你冒号变了多少，probe 能告诉你"冒号里的领域信息换问题后就读不出来了"，也就是信息的组织方式随问题改变了。

cosine 和 probe 都碰到天花板。两种方法测的都是"换问题前后的 state 有多像"，而三个 prompt 的标题一字不差，state 本来就几乎一样。cosine 看的是整个向量；probe 看的是和领域有关的那部分。不管用什么方法去比，结果都是"几乎一样"，而且从 L4 开始就是这样。

**cosine **不在 M3 或 X1 的方法本身里，而是这一页后来加上的**天花板检查**（探索性，2026-11-21 补做，出处 x1\_similarity.md / summary\_explore\_l4audit\_20261121）。在 P78 上出现在两个地方：

1. **左下折线图的黄色带**：标注写着 "ceiling: identical title text, cos(same paper, 2 questions) 0.998 at L4"；
2. **底部灰字那一行**："Ceiling: same paper, two questions — title-state cosine 0.9976 at L4, 0.9832 at L24 (two papers 0.45)"。

**它算的是什么：**取标题最后一个 token 的 state，比较两种情况下的 cosine 相似度

| 比较 | L4 | L24 |
| --- | --- | --- |
| 同一篇论文，两个不同问题 | 0.9976 | 0.9832 |
| 两篇不同论文，同一个问题 | 约 0.45 | — |

意思是：换问题，标题 state 几乎不变（接近 1）；换论文，state 差别很大（0.45）。

**M3 的结果**

| 位置 | T | 意思 |
| --- | --- | --- |
| 标题 | L4 就是 0.998，L40 是 0.992 | 换问题几乎不影响，而且从一开始就这样 |
| 冒号 | 0.24–0.41 | 换问题影响很大：冒号按问题组织 |

"年份 T − T(L4) 是 −0.060 到 −0.031" 的意思是：在中间层，年份 probe 的 T 反而比 L4 **略低**。中间层没有比字面更好。

X1

把论文 A 在"问年份"prompt 里的标题 state，替换进论文 B 的"问作者"prompt，看作者输出能恢复多少：

R = (patched − false) / (true − false)

可以理解为：替换之后，"答对作者"的差距被补回了百分之几。

| 层 | R |
| --- | --- |
| L24 | 0.996 |
| L40 | 0.933 |
| L48 | 0.455 |

关键在于：**无论 state 来自哪个问题，R 几乎一样**（authors 和 year 的差在 ±0.02 以内）。也就是说，标题 state 不太受问题影响，替换效果与任务无关。

L48 掉到 0.455，与前面 Stage 11 一致：到 L48 以后，信息已经从标题流到后面的名字位置了，只换标题就不够了。

】

**要说的话（一句英文一句中文）**
This page asks: does the question change what the model stores at the title?
这一页问：问题会不会改变模型在标题处存的东西？
We train a probe under one question and test it under another; and we swap title states between questions.
我们在一个问题下训练 probe，到另一个问题下测试；还把不同问题下的标题状态互换。
On the chart, a transfer near 1 means the probe works just as well under the other question; at the title it is about 0.99, but already 0.998 at layer 4, so it never rises above what the words alone give.
图上迁移值接近 1 表示 probe 在另一个问题下一样好用；标题处约 0.99，但第 4 层已经是 0.998，所以从来没超过单靠文字就能达到的水平。
At the colon, by contrast, the transfer is only 0.24 to 0.41: the colon is organised by the question.
相反，在冒号处迁移只有 0.24 到 0.41：冒号是按问题组织的。
So the title state looks the same under every question, and the colon carries the question. Next, the layer order.
所以标题状态在各个问题下都一样，问题由冒号承载。下一页看层序。

**备查（不念）· 上一版讲稿本页全文（原第 P81 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**本页在问（标题下一行小字）：** “Now asking: is it the title’s meaning, or the identity of this paper?” —— 靠的是标题的意思，还是这篇论文本身？

**先讲怎么做（指着两张方法图）：**
- M3（左上）：三个问题（authors / year / field）都是问题在前（9 个 token）、标题在后，标题文字完全相同；在最后一个标题 token（蓝点）或冒号（灰点）取状态，用一个问题训练 probe、在另外两个问题上测试。
- X1（右上）：把 A 论文在某个问题下、第 l 层的标题状态复制进另一篇论文的作者提示，再给 A 的作者打分。

**再讲结果（指着两张结果图）：**
- M3（左下折线）：在标题处，field probe 的迁移比 T 在 L40 是 0.992，但 L4 已经是 0.998，从未超过 L4（虚线）；年份 T − T(L4) 在 L16–L40 为 −0.060 到 −0.031。冒号处 T 只有 0.24–0.41（按问题组织，H1）。黄色带 = 天花板：同一篇两个问题的标题状态余弦 L4 0.998。
- X1（右下柱图）：R 在 L24 / L40 / L48 为 0.996 / 0.933 / 0.455（状态来自 authors 问题），0.990 / 0.928 / 0.431（year），field 几乎一样；L4 R 1.004；authors − year 在 L48 +0.024 [0.019, 0.030]（全部作者测试集值；旧版 +0.019 是第一作者的值）。
- 天花板一行（灰字）：同一篇两个问题余弦 L4 0.9976、L24 0.9832（两篇不同论文 0.45）；X5 跨问题检索 L4–L44 都是 1.000（L48 0.984）。
- 公式（灰字）：T = acc(q₁ 训练 → q₂ 测试) / acc(q₂ 训练 → q₂ 测试)，6 个有序问题对的平均；R(l) = mean(patched − other) / mean(own − other)。n = 9,108 篇（M3）· 582 测试篇（X1）。

**So 行（探索性天花板检查）：** 在标题位置这些检验受天花板限制：同样的标题文字在 L4 就给出同样的状态（纯文本 BERT 也一样），所以 M3 和 X1 分不开“意思”和“论文身份”；X1 的“与任务无关”就是由此而来，不是关于身份的发现。

**结论状态：** M3：H2 的预注册判据不成立（不超过 L4 文本水平，L4 基准在补充 2 中数据前预注册）；X1：描述性；天花板为探索性检查（summary_explore_l4audit_20261121）。

**过渡：** 再看 Patchscope 和改写标题。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** ​(M3: summary_m3/m3_transfer.csv, 9,108 papers, 5 team folds, team CI · X1: summary_b1_xall/x1__all.csv, test 582 papers, team CI · x1_similarity.md, x5_retrieval.md)。

## P52 · HTML v75 p52 · pptx S56 (v22z) — Layer order

**要说的话（一句英文一句中文）**
This page asks in which order the different kinds of information appear across layers.
这一页问：不同种类的信息按什么顺序在各层出现？
We use existing results only, and each source keeps its own rule for “first appears”.
我们只用已有结果，每个来源沿用它自己“首次出现”的判据。
Title facts and the first-author token appear by layers 8 to 16; the paper signal reaches the positions after the title by layers 48 to 52; the names become readable by lens only in layers 53 to 62.
标题事实和第一作者 token 在第 8 到 16 层出现；论文信号在第 48 到 52 层到达标题之后的位置；名字要到第 53 到 62 层才能被 lens 读出。
These sources use different rules, so this is a description, not a test.
这些来源的判据不同，所以这是描述，不是检验。
So read early, carried, said late. Next, how far the colon moves for a new question.
所以是读得早、传过去、说得晚。下一页看换问题时冒号移动多远。

**备查（不念）· 上一版讲稿本页全文（原第 P71 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 只用已有结果，每个来源沿用各自的判据，标出每类信息最早出现的测量层（≤Lx = 来源自己的判据首次通过的最早测量层）。分为标题位置读出、改写/论文身份、作者读出、因果 patching、knockout 几类。

**关键数字和 CI：**
- ≤L8–L16：标题事实和第一作者 token。
- L48–L52：论文信号到达标题之后的尾部（patching R 在 L48 ≥ 0.5，L52 ≥ 0.95；从 L52 起 knockout 没有代价）。
- L53–L62：lens 可以读出名字。
- 细化：名字之前的位置 × 层（第 1 项，探索性 → 第 72 页）；位置组 × 层（第 3 项，描述性 → 第 74 页）；按窗口的注意力边（第 2 项 → 第 75 页）；L57–L61 由 MLP 写入（第 4 项，定论（锁定判据成立） → 第 77 页）。
- n = 9,108（Stage 10，X5）· 1,186（patching、knockout）· 552–582 测试（Stage 13）。

**结论状态：** 描述性（汇总已有结果，各自的判据不同）。一句话："读得早，传过去，说得晚"。

**过渡：** 名字出现之前，作者信息有没有在某个提示位置提前出现？补充 18b 第 1 项画了一张读出图。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\leq L_x=\mathrm{earliest\ layer\ where\ the\ rule\ passes}$；② n = 9,108 (Stage 10) · 1,186 (patching, knockout) · 552–582 test papers (Stage 13)；③ smaller L: the information is there earlier；原公式框：≤L x = earliest measured layer at which the source’s own rule passes n = 9,108 (Stage 10, X5) · 1,186 (patching, knockout) · 552–582 test (Stage 13)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Layer order", tag "Stage 13 · layer order" ← X5; item 1/3/2/4 → readout map / per-position patching / single-edge blocking / late-layer ablation; chart-image labels masked: X4 patchscope → patchscope, X3 paraphrase → paraphrase, E4b probe → title-position probe, X6 tail patching → put back (tail patching), X7 knockout → take away, "Stage 13 X5:" → "Stage 13:"

**备查（不念）：**
- 图重新绘制（同一脚本、同一数据）：标题 “Stage 13 X5:” → “Stage 13:”；M2 probe → attribute probe；X4 patchscope → patchscope；X3 paraphrase identity → paraphrase identity；M3 identity index → identity index；E4b probe → title-position probe；Stage 12 F2 author-prompt lens → Stage 12 author-prompt lens；X6 tail patching → put back (tail patching)；X7 knockout → take away；图例 “X7: last layer” → “take away: last layer”；灰带 “H2-predicted” → “predicted (pre-registered)”；原来盖在旧图上的 11 个白底改字补丁随之去掉；alt 文字去掉 X5

## P53 · HTML v75 p53 · pptx S57 (v22z) — At “:”, a new question moves the state more than a new paper

**要说的话（一句英文一句中文）**
This page asks whether the colon state is organised by the question, H1's first prediction.
这一页问：冒号位置的状态是不是按问题组织的，这是 H1 的第一个预测。
For 9,108 papers we measure how far the colon state moves when the question changes, compared with when the paper changes.
在 9,108 篇论文上，我们测冒号状态在换问题时移动多远，和换论文时比。
On the chart, a ratio above 1 means the question matters more than the paper; it is 4.7 at layer 4, 3.0 at layer 40 and 2.2 at layer 48.
图上比值大于 1 表示问题比论文更重要；第 4 层是 4.7，第 40 层 3.0，第 48 层 2.2。
From layer 52 the paper's own change grows, so the ratio falls; and a distance only says the state differs, not what it encodes.
从第 52 层起换论文带来的变化本身变大，所以比值下降；而且距离只说明状态不同，不说明它编码了什么。
So the first prediction holds up to layer 48. Next, when the format is fixed.
所以第一个预测到第 48 层为止成立。下一页看格式什么时候定下来。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

At ":", a new question moves the state more than a new paper — until L48 Part 3 · Read early: the question and the title (H1) At ":", a new question moves the state more than a new paper — until L48 Now asking: is the ":" state organised by the question (H1, prediction 1)? Method: state at ":" (where the answer starts) for 9,108 papers under three questions; distances relative to the state's length Result: 1 at L4 a new question moves ":" 4.7× as far as a new paper (0.443 vs 0.094); 2 3.0× at L40, 3 2.2× at L48 Control: the denominator (new paper, same question) is the yardstick: ratio = 1 means the question matters no more than the paper Caveat: 4 from L52 the denominator grows (0.733 at L56), so the ratio falls to 1.3× although the numerator stays high (0.867) ; a distance says the state differs, not what it encodes Fits H1?: prediction 1 holds : ":" is organised by the question through L48 descriptive ratio > 1: a new question moves the ":" state more than a new paper So (this slide): the ":" state tracks the question 2–5× more than the paper up to L48 (descriptive); whether the format is fixed there is the next test.

数字出处：27_v67/fragments/part34_numbers.md

## P54 · HTML v75 p54 · pptx S58 (v22z) — Backup B22 · At “:”, a new question moves the state more than a new paper (for slide 53)

**要说的话（一句英文一句中文）**
This backup page gives the colon distance ratio layer by layer, shown only if asked.
这张备用页逐层给出冒号位置的距离比值，只有被问到时才展示。
It is the data behind the colon-ratio page in Part 3: 4.7 times at layer 4, 2.2 times at layer 48.
这是第 3 部分冒号比值那一页背后的数据：第 4 层 4.7 倍，第 48 层 2.2 倍。

**备查（不念）· 上一版讲稿本页全文（原第 P118 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This backup page shows the numbers behind the H1 line on slide 68.
这张备用页是第 68 页 H1 那一行背后的数字。

We take the hidden state at the colon after “Authors” and measure how far it moves, relative to its own length.
我们取 “Authors” 后面冒号处的隐藏状态，量它移动了多远（相对于它自身的长度）。

The orange curve is the numerator: the same paper under a different question.
橙色曲线是分子：同一篇论文，换一个问题。

The blue curve is the denominator: a different paper under the same question.
蓝色曲线是分母：同一个问题，换一篇论文。

At L4 the question change moves the state 4.7 times as far as the paper change, 0.443 against 0.094.
在 L4，换问题的移动是换论文的 4.7 倍，0.443 对 0.094。

The ratio is still 3.0 at L40 and 2.2 at L48: the state at the colon is organised by the question.
到 L40 比值还是 3.0，L48 是 2.2：冒号处的状态是按问题组织的。

From L52 the denominator grows, so the ratio falls to 1.3 to 1.5 at L56 to L63, although the numerator stays near 0.85 to 0.90.
从 L52 起分母变大，所以 L56 到 L63 比值降到 1.3 到 1.5，而分子一直在 0.85 到 0.90 左右。

**备查（不念）：** 数字来自 381_stage13/summary_m3/x1_similarity.csv（pos = colon，三对问题 authors–year、authors–field、year–field 取平均；脚本 13_stage13/stage13_x1_similarity.py；报告 381_stage13/reports/x1_similarity.md）。d = ‖a − b‖ / ‖a‖；分子 = reldist_same_paper，分母 = reldist_diff_paper（随机配对的另一篇论文），比值 = question_share = 每对问题的 mean(d_q) / mean(d_p) 再对三对取平均（因此 L4 比值 4.737 与 0.443 / 0.094 = 4.71 略有差别）。9,108 篇，15 层。第 68 页的页码指向原写 “→ slide 81”，2026-11-23 用户决定改指这一页。

## P55 · HTML v75 p55 · pptx S59 (v22z) — When is the answer format fixed? The format layer is not pinned down

**要说的话（一句英文一句中文）**
This page asks from which layer the author-list format is locked in, H1's second and third predictions.
这一页问：作者名单这种格式从哪一层起被锁定，这是 H1 的第二、第三个预测。
We knock out what the colon can read, from one layer to the end, and count how often the first answer token is still a name.
我们从某一层到最后，阻断冒号能读到的内容，统计第一个答案 token 仍然是名字的比例。
On the chart, a share near 1 means the answer stays a name. The locked rule gives layer 56, but the curve is not monotonic: it is 1 at layer 16 and falls to about 0.13 at layer 40.
图上比例接近 1 表示答案仍然是名字。锁定规则给出第 56 层，但曲线不单调：第 16 层是 1，到第 40 层掉到约 0.13。
A supplementary check, exploratory, found why: the dip appears only when we also cut the attention sink, the first position that absorbs much of the attention; keeping it, the names answer type holds from layer 4.
补充检查（探索性）找到了原因：只有连 attention sink——吸走大量注意力的第一个位置——一起切掉时才出现下凹；保留它，作者名这种答案类型从第 4 层起就保持住。
Swapping the colon state at layer 56 does lower the author signal, but the layer where the format is fixed is not pinned down. Next, the verdict card.
在第 56 层替换冒号状态确实会降低作者信号，但格式在哪一层定下来，定不下来。下一页是判定卡。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

When is the answer format fixed? The layer is not pinned down Part 3 · Read early: the question and the title (H1) When is the answer format fixed? The layer is not pinned down Now asking: from which layer is the "author list" format locked in (H1, predictions 2 and 3)? Method: knock out what ":" may read, from layer l to the end; K = share of papers whose first answer token stays a name (582 papers) Result (locked): 1 the pre-registered rule gives L56 (0.96) locked rule — but the curve is not monotonic: K is 1.00 at L16 and falls to 0.13 at L40 Supplement: 2 the dip appears only when position 0 is cut ; keeping it (gentle, sink only) keeps the names answer type from L4 exploratory Patching: swap the ":" state: the year prompt switches to names from L48 (1.00), field from L40 → L40–L56 Gate (locked): swapping ":" at L56 lowers the author signal: year −0.031 [−0.038, −0.024], field −0.032 [−0.040, −0.024] locked · supported Caveat: names are the default answer type, so "kept" is partly a default; year/field answers are right too rarely at baseline (0.80 / 0.05 < 0.90) to test K ≈ 1: the answer type survives the knockout So (this slide): the locked rule gives L56, but its main test is distorted by cutting the attention sink; with the sink kept the names format holds from L4 — the format layer is not pinned down ; the ":" state does gate the author signal at L56.

数字出处：27_v67/fragments/part34_numbers.md

## P56 · HTML v75 p56 · pptx S60 (v22z) — Verdict card · H1

**要说的话（一句英文一句中文）**
This verdict card closes H1: the question is read, but the format layer stays open.
这张判定卡给 H1 收尾：问题被读到了，但格式在哪层定下来仍然没有答案。
First prediction: the colon moves more for a new question than for a new paper; that holds up to layer 48, a descriptive result.
第一个预测：换问题时冒号移动比换论文时大；到第 48 层为止成立，这是描述性结果。
Second prediction: a knockout before a middle layer changes the answer type; not shown, because the locked test is distorted by cutting the sink.
第二个预测：在某个中间层之前阻断会改变答案类型；没有得到证明，因为锁定检验受到切掉 sink 的干扰。
Third: after swapping the colon, the field prompt switches to names from layer 40 and the year prompt from layer 48; and the colon state gates the author signal at layer 56.
第三：替换冒号后，问领域的提示从第 40 层起、问年份的从第 48 层起改答人名；而且冒号状态在第 56 层控制作者信号。
So H1 is revised: the format layer is not pinned down. Next, the evidence matrix after Part 3.
所以 H1 要修正：格式在哪层定下来，定不下来。下一页是第 3 部分之后的证据矩阵。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Verdict card · H1: the question is read, the format layer stays open Part 3 · Read early: the question and the title (H1) Verdict card · H1: the question is read, the format layer stays open Now asking: what did the H1 tests show, and how strong is each result? Prediction Result Strength Slides ① ":" moves more for a new question than for a new paper holds to L48 (4.7× → 2.2×) descriptive 51 ② knockout before a middle layer changes the answer type not shown : locked rule L56, but the test is distorted by cutting the sink; with the sink kept the type holds from L4 locked rule supplement: exploratory 52 ③ ":" swap switches the answer type from a middle layer switches from L40–L48; the ":" state gates the author signal at L56 locked · supported 52 — question-only tests separate meaning from identity no : the title state is the same under every question (ceiling) exploratory 49, 77 Verdict · H1 Revised. The ":" position tracks the question, but the layer where the answer format is fixed is not pinned down . The locked rule gives L56; its main test is non-monotonic and likely distorted by cutting attention sinks; the patching test points to L40–L56. The format gates the author signal at L56. Open: year / field: a measure the model gets right at baseline "names" is the default answer type — a default, not proof of a set format So (section): H1 is revised — the question is read at ":", but no middle layer is shown to fix the format. Next (Part 4): if the middle layers do not hold the format, do they hold which paper this is?

数字出处：27_v67/fragments/part34_numbers.md

## P57 · HTML v75 p57 · pptx S61 (v22z) — Evidence matrix after Part 3

**要说的话（一句英文一句中文）**
This matrix shows where each hypothesis stands after Part 3.
这张矩阵显示第 3 部分之后每个假设的位置。
The H1 row is now filled: the colon tracks the question, and the format test is distorted by the attention sink, so H1 is revised.
H1 这一行已经填上：冒号跟着问题走，格式检验受 attention sink 干扰，所以 H1 要修正。
The other rows are still open and will be filled in the next parts.
其他几行还空着，后面几部分会逐一填上。
Next, Part 4: what is read from the title, its meaning or the identity of the paper?
接下来是第 4 部分：从标题读到的是意思，还是论文的身份？

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Evidence matrix after Part 3 Now asking: with Part 3 done, where does each hypothesis stand? H1 · does the middle know "what is asked"? (✓) “:” new question vs paper 4.7× (L4) → 2.2× (L48) descriptive s. 51 (✓) probe after the question change T 0.24–0.41 descriptive s. 49 ~ top lens word format words; title-dependent 28–64% descriptive s. 37 ~ format locking (+ checks) L56 = sink artefact; names default locked + exploratory s. 52 (✓) swap “:” at L56 author signal −0.03 locked s. 52 Verdict: downgraded: “:” follows the question; the format layer is not pinned down → s. 53 H3 · author info in the middle, not in vocabulary directions? tested in Part 5 H2 · does the middle know "which paper"? tested in Part 4 Writing step (the bottleneck) tested in Part 6 ✓ supports (✓) partly ✗ weakens ~ cannot separate strength: settled locked pre-registered descriptive exploratory s. = slide So (section): H1 row filled: the question is read at “:”, the format layer is not pinned down. Next: H2 — is what the model reads from the title this paper , or its meaning?

数字出处：27_v67/fragments/part34_numbers.md

# Part 4 · What is read: meaning, not identity (H2) (58–87)

## P58 · HTML v75 p58 · pptx S62 (v22z) — Question card · H2: does the title state hold this paper’s identity?

**要说的话（一句英文一句中文）**
This question card opens Part 4: does the model hold which paper this is, or what the title means?
这张问题卡开启第 4 部分：模型存的是“这是哪一篇论文”，还是“标题是什么意思”？
Think of a library. The first is the call number, which points to one book only; the second is the topic written on the spine, which many books share.
把它想成图书馆。前一种是索书号，只指向一本书；后一种是书脊上写的主题，很多本书都一样。
By the title state we mean the model's internal state at the title, the numbers it holds there.
我们说的标题状态，就是模型读到标题时内部的状态，也就是它在那里存着的那串数字。
If it is the call number, a card with the same topic written on it, but not belonging to this book, should get us almost nowhere, and whatever the real title adds should grow with recognition and citations.
如果是索书号，一张写着同样主题、但不属于这本书的卡片应该几乎没用，而真标题多出来的部分应该随“认得”和引用数变大。
If it is the topic, that card should get most of the way, and what is left should sit on a few specific words.
如果是主题，那张卡片应该能走到大半，剩下的部分会落在几个具体的词上。
First a short look back at the small samples, then the decisive tests.
先简单回顾小样本阶段，再看决定性的检验。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Question card · H2: does the model hold which paper this is? Part 4 · What is read: meaning, not identity (H2) Question card · H2: does the model hold which paper this is? Now asking: what would we see if the middle layers encode paper identity rather than meaning? If H2 holds, we expect 1 a made-up title with the same meaning recovers little of the true-title advantage 2 the real-title extra is larger for recognised and for more-cited papers 3 paper identity explains the title state beyond its text 4 a paper-specific answer can be decoded beyond the topic If H2 fails, we expect 1 the made-up title recovers most of the advantage (meaning carries it) 2 the extra does not depend on recognition or citations 3 text features (meaning, words) explain the state; identity adds ≈ 0 4 what remains sits on specific words, not on the paper Tests in this part: why question-only tests cannot decide → slide 77 · made-up title → slides 73, 74 · rare vs common words → slide 80 · recognition and citations → slide 78 · variance split → slide 79 · surname signal beyond topic → slide 81 Earlier pages: small-sample title effect → slides 57–66 · patchscope and paraphrases → slides 70, 71 Caveat: identity and meaning travel together in a real title; only inputs that differ (made-up titles, word swaps) can pull them apart question card · H2 hypothesis So (this slide): four predictions; the verdict card scores each, with one locked exception.

数字出处：27_v67/fragments/part34_numbers.md

## P59 · HTML v75 p59 · pptx S63 (v22z) — Background: how we got here (small samples) · Part 4

**要说的话（一句英文一句中文）**
This divider marks a background block: what the earlier, smaller samples suggested before the decisive tests.
这张分隔页标出一个背景块：在决定性检验之前，早期的小样本提示了什么。
They suggested that the true title helps the true author in late layers, but whether recognised papers gain more stayed uncertain.
它们提示真标题在后期层帮助真作者，但认得的论文是不是收益更大，一直不确定。
These are small samples, where single papers or pairs can drive a result, so in the talk this block can be skipped.
这些都是小样本，一两篇论文或一两对就能左右结果，所以汇报时这一块可以跳过。
If we skip it, we go straight to why question-only tests cannot decide H2.
如果跳过，就直接讲为什么只换问题的检验判定不了 H2。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Part 4 · background Background: how we got here (small samples) Now asking: what did the earlier, smaller samples suggest before the decisive tests? In this block: slides 57–69 57 Is it about this paper? 58 First readout: is any author signal there? 59 Crossed title–author control 60 Gold vs 100 real false authors 61 Shuffled titles: the true title helps 62 Does the title effect survive the obvious objections? 63 Independent replication (Stage 8) 64 On 200 new papers the title effect replicates 65 But the A−B gap rests on a few pairs 66 Stage 8 re-scored on CPU: three premises 67 Knowing the paper shows up only at the end 68 How much is just the name prior? 69 The probe signal is paper-specific What they suggested: the true title helps the true author in late layers; whether recognised papers gain more stayed uncertain Caveat: small samples; single papers or pairs can drive a result Decisive tests: start at slide 70 So (section): these pages set up the question; the decisive tests of this part start at slide 70. descriptive

## P60 · HTML v75 p60 · pptx S64 (v22z) — Is it about this paper?

**要说的话（一句英文一句中文）**
This page opens the background question: is the author signal about this paper, or just about easy names?
这一页提出背景问题：作者信号是关于这篇论文的，还是只是名字好猜？
The small samples asked whether the true title beats a crossed or shuffled title, and whether recognised papers gain more.
小样本问的是：真标题能不能胜过交叉的或打乱的标题，认得的论文是不是收益更大。
The full cohort answered with a paper-specific signal for every token, with recognised papers ahead only in the late layers, and with the name prior split out.
全队列给出的回答是：每个 token 都有论文特有的信号，认得的论文只在后期层领先，名字先验被单独拆了出来。
The next pages walk through the small-sample steps in order.
接下来几页按顺序走一遍小样本的各步。

**备查（不念）· 上一版讲稿本页全文（原第 P12 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** A 线的问题。小样本阶段问的是：真标题能不能赢过交叉标题或打乱标题？A 组的提升是否大于 B 组？全队列给出的回答是：每个 token 上都有 title-specific 信号；target 只在后层胜过 control；名字先验被单独拆出来；probe 做了对照。另附补充 19 的确认结果（锁定发生在看过数据之后）：写出作者所需的曝光远多于认出论文（第 29 页）。小样本部分按 Stage 4 → 5 → 7.2 → 7.3 的顺序展开（第 13–16 页），每一步的结论引出下一步。

**过渡：** 第一步：到底有没有作者信号？

**备查（不念）：**
- 原写 “+ addendum 19”（曝光门槛检验，补充登记 19，事后锁定）

## P61 · HTML v75 p61 · pptx S65 (v22z) — First readout: is any author signal there?

**要说的话（一句英文一句中文）**
This page asks the very first question: is there any author signal inside the model at all?
这一页问最初的问题：模型里面到底有没有作者信号？
On 20 papers and 93 authors we read the rank of the true name across layers.
在 20 篇论文、93 位作者上，我们逐层读真名字的排名。
On the chart, a higher reciprocal rank means the true name sits nearer the top; at layer 56 the mean looked like a peak, but the median was tiny.
图上倒数排名越高，表示真名字越靠前；第 56 层的均值看起来像个峰，但中位数很小。
One paper alone made up 71% of that mean; without it the value dropped to about a third.
单单一篇论文就占了这个均值的 71%；去掉它，数值降到大约三分之一。
So a layer peak can be one easy paper, and every later stage adds controls. Next, the first control.
所以一个层峰值可能只是一篇容易的论文造成的，之后每个阶段都加了对照。下一页是第一个对照。

**备查（不念）· 上一版讲稿本页全文（原第 P13 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 20 篇论文、93 位作者（A8 / B8 / C3 / D1），每篇约 91 秒、约 29.5 GiB GPU。画出第一作者第一个 token 的 RR（左）和条件全名 JMRR（右）随层的变化。

**关键数字和 CI：**
- 流程跑通；中间层 J-Lens 高于 Vanilla。
- L56 第一作者 RR 均值 0.0070，中位数只有 0.0009（20 篇；audit_report.md 表 1）。
- 一篇论文贡献了 L56 均值的 71%：去掉它，0.0070 → 0.0021。
- n = 20 篇，93 位作者。

**结论状态：** 探索性。层峰值可能只是某一篇容易的论文造成的，所以之后每个 Stage 都加了对照。

**过渡：** 有信号了，但它来自标题，还是只因为这个名字本身好猜？下一页用交叉对照来检验。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{RR}=\mathrm{mean}_{\mathrm{papers}}\,1/\mathrm{rank}$；② n = 20 papers, 93 authors (first-listed author, first token)；③ RR = 1: always ranked first; 0.1 ≈ rank 10；原公式框：RR = mean over papers of 1/rank (first-listed author, first token) n = 20 papers, 93 authors。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(20 papers; audit_report.md table 1)

**备查（不念）：**
- 出处：351_stage4_readout.log（副标题）；“(same file)”

## P62 · HTML v75 p62 · pptx S66 (v22z) — Crossed title–author control

**要说的话（一句英文一句中文）**
This page asks: is the true name high because of the title, or just because the name is easy?
这一页问：真名字排得高，是因为标题，还是只是因为名字好猜？
We cross titles and authors: the margin of the true author over another author, under the true title minus under the other paper's title. Any fixed preference for a name cancels out.
我们把标题和作者交叉：真作者相对另一位作者的优势，在真标题下减去在另一篇论文标题下。对某个名字的固定偏好就抵消掉了。
On the chart, T above zero means the title moves the answer towards the true author; over 50 papers it is clearly positive at layers 56 and 62.
图上 T 大于 0 表示标题把答案推向真作者；在 50 篇论文上，第 56 和 62 层明显为正。
Whether recognised papers gain more than unrecognised ones stayed unclear: the interval easily included zero.
认得的论文是不是比认不得的收益更大，仍然不清楚：区间轻松包含 0。
So the title changes which name wins in late layers. Next, a hundred real false authors instead of one.
所以标题会改变后期层里哪个名字胜出。下一页用 100 个真实的假作者，而不是一个。

**备查（不念）· 上一版讲稿本页全文（原第 P14 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 论文 P（作者 G）和来源论文 Q（作者 F，同领域、同引用档）。M = logit(G) − logit(F)，T = M(P 的标题) − M(Q 的标题)。这样对 G 的固定偏好会被抵消掉，T 只反映标题带来的变化。左图 50 篇全部论文，右图 20 个 A/B 对。

**关键数字和 CI：**
- 全部 50 篇：L56 +1.17 [0.53, 1.84]，L62 +1.08 [0.36, 1.82]（Stage 5，J-Lens，layer_summary.csv）。
- 匹配 A−B，7 层 integrated：+0.08 [−0.43, +0.65]（20 对，matched_ab_summary.csv）。
- n = 50 篇 · 20 个匹配 A/B 对。

**结论状态：** 探索性。后层里标题确实会改变哪个名字胜出；A 的提升是否大于 B：未成立。

**过渡：** 只拿一个对手名字太弱，下一页把对手扩大到 100 个真实的假作者。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $T=M(P_{\mathrm{title}})-M(Q_{\mathrm{title}}),\ \ M=\mathrm{logit}(G)-\mathrm{logit}(F)$；② n = 50 papers · 20 matched A/B pairs；③ T > 0: the paper’s own title lifts its true author；原公式框：T = M(P title) − M(Q title), M = logit(G) − logit(F) n = 50 papers · 20 matched A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(Stage 5, J-Lens, 50 papers, layer_summary.csv)
- 出处（原在幻灯片上）：(20 pairs, matched_ab_summary.csv)

## P63 · HTML v75 p63 · pptx S67 (v22z) — Gold vs 100 real false authors

**要说的话（一句英文一句中文）**
This page asks whether the true author beats many real alternative names, not just one.
这一页问：真作者能不能胜过很多真实的候选名字，而不只是一个？
For each paper we score the true name against 50 matched and 50 random real names.
每篇论文我们把真名字和 50 个匹配的、50 个随机的真实名字比。
On the chart, the win rate is how often the true name scores above a false one; recognised papers lead by about 0.15 to 0.19 in the middle layers.
图上胜率是真名字得分高于假名字的比例；认得的论文在中间层领先大约 0.15 到 0.19。
But these names might win under any title, and many share the same first token, so this is still a clue.
但这些名字可能在任何标题下都会赢，而且很多名字第一个 token 相同，所以这还只是线索。
Next, we keep the names and change only the title.
下一页我们保持名字不变，只换标题。

**备查（不念）· 上一版讲稿本页全文（原第 P15 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 每篇论文 50 个匹配名字（同领域、同 token 数、同年份）加 50 个随机名字，共 75,000 个打分对。指标是金标胜率 P(logit gold > logit false)，比较匹配的 A − B。

**关键数字和 CI：**
- J-Lens A−B：L40 +0.15、L48 +0.19、L56 +0.19（CI 都在 0 以上）；L62 +0.04（跨过 0）（20 对，matched_ab_bootstrap.csv）。
- 7 层 integrated：+0.105 [−0.012, +0.229]（20 对；10-30 重算）。
- 5,000 个假名字中有 156 个和金标的第一个 token 相同（平局）（quality.json）。
- 100 个名字只有约 46 个不同的第一个 token（50 篇的平均）。
- n = 50 篇 · 每篇 100 个假名字（75,000 对）· 20 个 A/B 对。

**结论状态：** 探索性。中间层里，A 组金标胜过真实名字的程度大于 B 组；但这些名字也可能在任何标题下都赢。

**过渡：** 7.3 用打乱标题来检验这一点。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{win}=P(\mathrm{logit}_{\mathrm{gold}}>\mathrm{logit}_{\mathrm{false}})$ · $A-B\ \mathrm{(matched\ pairs)}$；② n = 50 papers · 100 false names each (75,000 pairs) · 20 A/B pairs；③ win = 0.5: chance / A − B > 0: recognised papers win more often；原公式框：win = P(logit gold > logit false); matched A − B n = 50 papers · 100 false names each (75,000 pairs) · 20 A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(candidate_pairwise_scores.csv)
- 出处（原在幻灯片上）：(20 pairs, matched_ab_bootstrap.csv)
- 出处（原在幻灯片上）：(quality.json)

**备查（不念）：**
- 出处：“(mean of 50 papers; candidates csv)” 中的 “candidates csv”
- “recomputed 10-30”（7 层积分 CI 于 10-30 重算）

## P64 · HTML v75 p64 · pptx S68 (v22z) — Shuffled titles: the true title helps

**要说的话（一句英文一句中文）**
This page asks: if only the title changes, does the true title help?
这一页问：如果只换标题，真标题有没有帮助？
Same hundred candidate names, and for each paper twenty wrong titles matched on its metadata.
候选名字还是那 100 个，每篇论文配 20 个元数据匹配的错误标题。
On the chart, the advantage is the win rate under the true title minus under the wrong titles; at layer 56 it is about 9 percentage points, and 35 of 50 papers are positive.
图上优势是真标题下的胜率减去错误标题下的胜率；第 56 层大约 9 个百分点，50 篇里有 35 篇为正。
But again, recognised papers did not gain more than unrecognised ones.
但同样，认得的论文并没有比认不得的收益更大。
So the title helps, but the group difference is not shown. Next, the obvious objections.
所以标题有帮助，但组间差异没有显示出来。下一页看几个显而易见的质疑。

**备查（不念）· 上一版讲稿本页全文（原第 P16 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 候选名字还是那 100 个，每篇配 20 个元数据匹配的错误标题，共 1,000 个上下文，只有标题在变。指标 adv = 真标题下的胜率 − 20 个错误标题下胜率的均值。

**关键数字和 CI：**
- 合并 L56：0.616 vs 0.523 → +9.3 pp [4.8, 14.0]，50 篇中 35 篇为正（J-Lens L56；paper_null_distribution.csv；CI 于 10-30 重算）。
- 留一法：+8.6 到 +10.0 pp（stage7_l56_loo.csv）。
- Vanilla L56 +10.6 pp；最终输出 +7.2 pp。
- 匹配 A−B integrated：+0.018 [−0.021, +0.063]（20 对）。
- n = 50 篇 · 1,000 个上下文（每篇 20 个错误标题）· 20 个 A/B 对。

**结论状态：** 探索性。要分开两个问题："标题有没有帮助？"有；"对 A 的帮助是否大于 B？"没有显示出来。

**过渡：** 下一页看这个标题效应能不能经得起几种明显的质疑。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{adv}=\mathrm{win}(\mathrm{true\ title})-\mathrm{mean}_{20}\,\mathrm{win}(\mathrm{wrong\ title})$；② n = 50 papers · 1,000 contexts · 20 A/B pairs；③ adv > 0: the true title helps；原公式框：adv = win(true title) − mean 20 win(wrong title) n = 50 papers · 1,000 contexts (20 wrong titles each) · 20 A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(J-Lens L56, 50 papers; paper_null_distribution.csv; CI recomputed 10-30)
- 出处（原在幻灯片上）：(stage7_l56_loo.csv)
- 出处（原在幻灯片上）：(paper_null_distribution.csv)
- 出处（原在幻灯片上）：(20 pairs, integrated_ab_bootstrap.csv)

## P65 · HTML v75 p65 · pptx S69 (v22z) — Does the title effect survive the obvious objections?

**要说的话（一句英文一句中文）**
This page asks whether the title effect survives the obvious objections.
这一页问：标题效应经不经得起几个显而易见的质疑？
We exclude wrong titles whose authors are in the false-name pool, try different weightings, and look at the least-cited papers.
我们排除了作者在假名字池里的错误标题，试了不同的加权，又单独看引用最少的论文。
On the chart, each version stays positive, around 0.03.
图上每个版本都保持为正，大约 0.03。
But the recognised-minus-unrecognised gap flips sign between layers: positive at 56, negative at 32, so reporting only the positive layer would mislead.
但认得减认不得的差距在不同层会变号：第 56 层为正，第 32 层为负，所以只报告为正的那一层会误导。
So the title effect holds; the group gap does not. Next, an independent replication with the rules fixed first.
所以标题效应站得住，组间差距站不住。下一页是一次先定规则的独立复现。

**备查（不念）· 上一版讲稿本页全文（原第 P17 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 三项稳健性检查和一个分层检查：① 错误标题的来源论文作者恰好在假名字池里；② 换不同的候选加权；③ 低引用论文单独看；④ 逐层看校正标题后的 A−B 胜率。

**关键数字和 CI：**
- 来源作者重叠：1,000 个错误标题中 199 个来自这种论文；排除后 +0.026 → +0.028。
- 候选加权（作者、unique token、非碰撞权重）：合并 +0.026 到 +0.032；6 个 A−B 的 CI 都包含 0。
- 低引用（0–2 引用，n = 6）：L56 +0.22，6 篇中 5 篇为正，但没有一篇超出自己 20 个标题的尾部（≤ 0.05）。
- 层间异质性：L56 +0.11，但 L32 −0.03（CI 在 0 以下）（20 对）。只报告为正的层会误导。
- n = 50 篇 · 1,000 个错误标题 · 6 篇低引用论文 · 20 个 A/B 对。

**结论状态：** 探索性。标题效应经得起这几种质疑；A−B 依旧不稳定，而且随层变化。

**过渡：** 小样本结果需要独立复现，下一页是先锁定计划、再看数据的 Stage 8。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{adv}=\mathrm{win}(\mathrm{true\ title})-\mathrm{mean}_{20}\,\mathrm{win}(\mathrm{wrong\ title})$；② n = 50 papers · 1,000 wrong titles · 6 low-citation papers · 20 A/B pairs；③ adv > 0: the true title helps；原公式框：adv = win(true title) − mean 20 win(wrong title) n = 50 papers · 1,000 wrong titles · 6 low-citation papers · 20 A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(quality.json; paper_null_distribution.csv)
- 出处（原在幻灯片上）：(stage7_weighting_title_advantage.csv)
- 出处（原在幻灯片上）：(floor_L56_low_six.csv)
- 出处（原在幻灯片上）：(20 pairs, matched_ab_bootstrap.csv)

## P66 · HTML v75 p66 · pptx S70 (v22z) — Independent replication (Stage 8)

**要说的话（一句英文一句中文）**
This page asks how the replication was set up.
这一页问：复现实验是怎么设计的？
We locked the plan first, then scored 200 new papers, with the first author against a hundred false names.
我们先锁定计划，再给 200 篇新论文打分，第一作者对 100 个假名字。
On the chart, a title test above zero means the true title helps.
图上标题检验大于 0 表示真标题有帮助。
One caveat that matters later: layer 56 was made the primary endpoint during the run, and it is unclear who decided that and why.
有一点后面会用到：第 56 层是在运行过程中才被定为主终点的，由谁、为什么决定并不清楚。
Next, the result.
下一页看结果。

**备查（不念）· 上一版讲稿本页全文（原第 P18 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 先锁计划，再看数据。六步：锁定计划（10-18 14:29；L56 在 21:14 被定为主终点）→ 200 篇新论文 → 打分（10-18 21:47 → 10-20）→ 对照计划检查 → L56 → 7 层。100 个 A/B 对。RQ1 = 真标题胜率 − 20 个假标题胜率均值；第一作者对 100 个假名字，J-Lens，按论文 bootstrap。

**关键数字和 CI：**
- L56：+5.18 pp [2.93, 7.48]（Stage 8D RQ1，J-Lens L56，200 篇，primary_questions.csv）。
- 7 层：+2.33 pp [1.50, 3.19]（J-Lens 7 层，200 篇，s8_endpoints.csv）。

**结论状态：** 方法页（预注册复现）。

**过渡：** 下一页逐项看 Stage 8D 的结果。

**图旁 n（灰色行）：** n = 200 new papers (100 A/B pairs), Stage 8D

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{RQ1}=\mathrm{win}(\mathrm{true\ title})-\mathrm{win}(\mathrm{wrong\ title})$；② n = 200 new papers (100 A/B pairs)；③ RQ1 > 0: the true title helps；原公式框：n = 200 new papers (100 A/B pairs), Stage 8D；原出处行：+5.18 pp: Stage 8D RQ1, J-Lens L56, 200 papers, primary_questions.csv · +2.33 pp: J-Lens 7-layer, 200 papers, s8_endpoints.csv。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 图内公式框里的判据 / 说明（移出幻灯片）：first author vs 100 false names · J-Lens · paper bootstrap

## P67 · HTML v75 p67 · pptx S71 (v22z) — On 200 new papers the title effect replicates

**要说的话（一句英文一句中文）**
This page asks whether the title effect replicates on 200 new papers.
这一页问：标题效应在 200 篇新论文上能不能复现？
We estimated the pre-registered questions: the title effect, the recognised-minus-unrecognised gap, and low versus high citations.
我们估计了预注册的几个问题：标题效应、认得减认不得的差距、低引用对高引用。
On the chart, a bar above zero means an advantage; the title effect is about 5 percentage points, and its interval stays above zero.
图上柱子大于 0 表示有优势；标题效应大约 5 个百分点，区间都在 0 以上。
The group gap is also positive on the frozen endpoint; low versus high citations is not.
按冻结的主终点，组间差距也为正；低引用对高引用不成立。
So the title effect is confirmed on new papers for the first time. Next, what the group gap rests on.
所以标题效应第一次在新论文上得到确认。下一页看组间差距靠什么撑着。

**备查（不念）· 上一版讲稿本页全文（原第 P19 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 按 PROTOCOL.md 在 200 篇新论文上估计 RQ1（标题效应）、RQ2（A−B，100 对）、RQ3（低引用 − 高引用，25 + 25 对），以及 J-Lens − Vanilla。

**关键数字和 CI：**
- RQ1 标题，L56：+5.18 pp [+2.93, +7.48]（200 篇）。
- RQ2 A−B，L56：+4.98 pp [+0.32, +9.91]（100 对）。
- RQ2 A−B，7 层（冻结的主终点）：+2.41 pp [+0.91, +4.00]（100 对；s8_endpoints.csv）。
- RQ3 低−高：+2.45 pp [−3.69, +8.60]（25 + 25 对）。
- J-Lens − Vanilla：−1.38 pp [−3.48, +0.68]。
- 引用分段：低 +6.8 [2.5, 11.6]，中 +4.8，高 +4.4 [−1.1, 10.0]（50/100/50 篇）。
- n = 200 篇 · 100 个 A/B 对（RQ2）· 25 + 25 对（RQ3）。

**结论状态：** 预注册判据：RQ1 成立（第一次独立确认：在新论文上，正确标题帮助金标作者）；RQ2 7 层主终点 CI 在 0 以上（成立）；RQ3 不成立（CI 跨 0）；J-Lens 相对 Vanilla 没有增益。总体按报告记为初步（较稳但有前提）：前提是 W 只打第一个 token、偏离 D13-1、U28（见第 21 页）。

**过渡：** 但 A−B 这个正值是怎么来的？下一页看它是否只靠少数几对撑着。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{RQ1}=\mathrm{win}(\mathrm{true\ title})-\mathrm{win}(\mathrm{wrong\ title}),\ L56$；② n = 200 papers · 100 A/B pairs (RQ2) · 25 + 25 pairs (RQ3)；③ RQ1 > 0: the true title helps；原公式框：RQ1 = win(true title) − win(wrong title), L56 n = 200 papers · 100 A/B pairs (RQ2) · 25 + 25 pairs (RQ3)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(primary_questions.csv)
- 出处（原在幻灯片上）：(Stage 8D, J-Lens L56; primary_questions.csv)
- 出处（原在幻灯片上）：(100 pairs; s8_endpoints.csv)
- 出处（原在幻灯片上）：(jlens_minus_vanilla.csv)
- 出处（原在幻灯片上）：(50/100/50 papers; layer_and_band_summary.csv)

**备查（不念）：**
- 图注原写 “(PROTOCOL.md)” → 改为 “(pre-registered)”

## P68 · HTML v75 p68 · pptx S72 (v22z) — But the A−B gap rests on a few pairs

**要说的话（一句英文一句中文）**
This page asks what the recognised-minus-unrecognised gap rests on.
这一页问：认得减认不得的差距是靠什么撑着的？
We drop the pairs that contribute the most, one after another, and watch the mean.
我们把贡献最大的配对一个一个去掉，看均值怎么变。
On the chart, the remaining gap falls fast: removing the top five pairs leaves about 2 points, removing the top ten leaves about zero.
图上剩下的差距掉得很快：去掉前 5 对只剩约 2 个点，去掉前 10 对就约为 0。
A Stage 8 follow-up audit, not pre-registered, re-checked the weighting and recomputed the numbers from the raw logits, with the same estimates.
Stage 8 的一次补充审计（未预注册）重新核对了加权方式，并从原始 logits 重新计算，估计值不变。
So the gap is real in the mean but carried by a few pairs, which is why we moved to the full cohort. Next, Stage 8 re-scored the full-cohort way.
所以这个差距在均值上存在，但只靠少数几对撑着，这就是我们改用全队列的原因。下一页按全队列的方式重新给 Stage 8 打分。

**备查（不念）· 上一版讲稿本页全文（原第 P20 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 依次去掉贡献最大的正向对，看剩下的 A−B 均值。另附 8E 外部审计（未预注册）：unique-token 加权、错误标题长度差，以及在原脚本缺失的情况下从原始 logits 重算。

**关键数字和 CI：**
- 100 对：55 正、45 负；中位数 +4.4 pp（J-Lens L56）。
- 单独一对（S8P094）约 +84 pp。
- 去掉前 5 对 → +1.9 pp；去掉前 10 对 → −0.4 pp。
- 8E：unique-token 加权 RQ1 +4.6、RQ2 +5.4 pp；错误标题长度差每个 token +0.12 pp（200 篇，只是相关）。
- 原脚本缺失；10 月 30 日从原始 logits 重算，估计值相同（不在预注册范围内）。
- n = 100 个 A/B 对（200 篇）。

**结论状态：** 初步（较稳但有前提）：A−B 为正，但靠尾部少数对撑着；8E 部分为探索性（未预注册）。小样本可以给出一个正的 A−B 均值，而它其实只由少数几篇论文撑着，这是 Stage 10 改用全队列的主要原因。

**过渡：** 能不能用 Stage 10 的打分在 CPU 上重看 Stage 8？下一页。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $(A-B)_{-k}=\mathrm{mean\ of\ the\ remaining\ pair\ differences}$；② n = 100 A/B pairs (200 papers)；③ falls to ≈ 0: the gap rests on a few pairs；原公式框：A − B after removing the top k = mean of the remaining pair differences n = 100 A/B pairs (200 papers)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(J-Lens L56; matched_pair_differences.csv)
- 出处（原在幻灯片上）：(s8_8E_weighting_by_paper.csv)
- 出处（原在幻灯片上）：(200 papers; s8_unsourced_intervals.csv)
- 出处（原在幻灯片上）：(351_stage8/recompute_2026-10-30/)

**备查（不念）：**
- 出处：“(recomputed from same file)”

**备查（不念）：**
- 原写 “One pair (S8P094)”：S8P094 = 该 Stage 8 论文的内部编号

## P69 · HTML v75 p69 · pptx S73 (v22z) — Stage 8 re-scored on CPU: three premises

**要说的话（一句英文一句中文）**
This page asks what the Stage 8 papers look like when scored the full-cohort way.
这一页问：用全队列的方式重新打分，Stage 8 的论文看起来怎么样？
We re-scored them on CPU with five false titles and every author.
我们在 CPU 上用 5 个假标题、全部作者重新打分。
On the chart, a point above zero means an advantage; over six layers both the title effect and the group gap are positive.
图上点在 0 以上表示有优势；6 层平均下，标题效应和组间差距都为正。
At layer 56 alone the group gap includes zero, which by the pre-registered rule asked for a re-run that was not done; that is recorded as a deviation.
单看第 56 层，组间差距的区间包含 0，按预注册规则应当重跑，但没有重跑，这一点记录为偏离。
So the replication holds with three stated premises. Next, the full cohort's own answer: at which layers the paper signal shows.
所以复现在三个明确前提下成立。下一页看全队列自己的回答：论文信号在哪几层出现。

**备查（不念）· 上一版讲稿本页全文（原第 P21 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**先讲怎么做（指着左边的方法图）：** 同样的 200 篇 Stage 8 论文、100 个 A/B 对；用 Stage 10 的打分：真标题 vs 5 个假标题，每个作者、每个名字 token，public J-lens 名次指标（不是 Stage 8 的 W 统计量）。RQ1 = 真 − 假（全部论文），RQ2 = A − B（配对）。比较四个终点：6 层均值（不含 L16）、单看 L56、锁定 7 层终点的两种近似（L16 记 0 / L16 = L24）。

**再讲结果（指着右边的森林图：灰 = RQ1，蓝 = RQ2，横线 = 95% 团队 CI）：**
- 6 层均值：RQ1 +0.130 [0.108, 0.153]，RQ2 +0.054 [0.008, 0.102] → 都为正。
- 单看 L56：RQ2 +0.064 [-0.032, 0.163]，CI 包含 0 → 触发补充 13 规则，要求重跑 W；没有重跑 = 偏离 D13-1。
- 7 层终点两种近似：RQ2 +0.046 [0.007, 0.088] / +0.049 [0.005, 0.094]，方向相同。
- 三个前提（左下）：W 只打第一作者的第一个 token（64.5% 是首字母）；D13-1；U28（L56 在 21:14 被定为主终点，由谁、为什么决定不明）。

**So 行：** 用 5 个假标题和所有作者打分，Stage 8 的方向成立（6 层和 7 层终点 RQ1、RQ2 都为正），但单看 L56 不成立，所以 Stage 8 的结果依赖三个前提。

**结论状态：** 较稳但有前提（CPU 代理，不是锁定终点）；记录偏离 D13-1。

**过渡：** 后面的结果都用全词表名次打分，先用一个例子把 rank → log → spec 走一遍。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 200 papers · 100 A/B pairs；③ RQ1 > 0: true title helps / RQ2 > 0: A beats B；原公式框：n = 200 papers · 100 A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(addendum 13 C-2: 381_stage13/c13_C2_followup/c2_followup_proxy.csv (version aa_all: all authors, all name tokens), team CI)

**备查（不念）：**
- (addendum 13 C-2: 381_stage13/c13_C2_followup/c2_followup_proxy.csv (version aa_all: all authors, all name tokens), team CI)
- 原写 “D13-1”（偏离记录）、“U28”（未解决问题编号）、“addendum-13 rule”（补充登记 13 的判据）

## P70 · HTML v75 p70 · pptx S74 (v22z) — Knowing the paper shows up only at the end

**要说的话（一句英文一句中文）**
This page asks at which layers the paper-specific signal shows in the full cohort.
这一页问：在全队列里，论文特有的信号在哪几层出现？
We score all 9,108 papers and follow the signal across layers for recognised and unrecognised papers.
我们给全部 9,108 篇论文打分，逐层看认得和认不得两组的信号。
On the chart, spec above zero means the true title ranks the author higher than false titles; from layer 24 to 48 both groups are about zero.
图上 spec 大于 0 表示真标题让作者排得比假标题更前；第 24 到 48 层两组都约为 0。
It rises from layer 56, and at layer 62 recognised papers reach about 0.56 against about 0.24.
从第 56 层开始上升，到第 62 层认得的论文约 0.56，认不得的约 0.24。
So the paper signal shows only at the end. Next, how much of the score is just an easy name.
所以论文信号只在最后才出现。下一页看分数里有多少只是名字好猜。

**备查（不念）· 上一版讲稿本页全文（原第 P24 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 全部 9,108 篇打分，按 target（4,621）和 control（2,220）画 title-specific 信号随层的变化：线是 public Jacobian lens，菱形是模型输出。

**关键数字和 CI：**
- L24–L48：两组都约为 0（所有读出方式最大 0.04，§6.3）。
- 从 L56 开始上升。
- L62：target +0.56 vs control +0.24（public lens L62，4,621 + 2,220 篇，§6.3 图）。
- n = 4,621 target + 2,220 control 篇（Stage 10；全部 9,108 篇都打了分）。

**结论状态：** 定论（第 64 页表中"认得出 > 认不出：confirmed，只在后层"）。

**过渡：** 输出层的差距里有多少只是"名字本身像不像作者"的先验？下一页拆开看。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 4,621 target + 2,220 control papers (all 9,108 scored)；③ spec > 0: the true title ranks the author higher than false titles；原公式框：title-specific = nlr true − mean 5 nlr false n = 4,621 target + 2,220 control papers (Stage 10; all 9,108 scored)。

## P71 · HTML v75 p71 · pptx S75 (v22z) — How much is just the name prior?

**要说的话（一句英文一句中文）**
This page asks how much of the score is just an easy name.
这一页问：分数里有多少只是名字好猜？
We split the score into three parts: no title, which is the name prior; any title from the field; and the true title over false titles.
我们把分数拆成三部分：没有标题，也就是名字先验；同领域的任意标题；以及真标题相对假标题。
On the chart, the last part above zero is the paper-specific signal; after removing the prior it is about 0.21 for all tokens and about 0.42 for the surname's first token.
图上最后一部分大于 0 就是论文特有的信号；去掉先验后，全部 token 约 0.21，姓氏第一个 token 约 0.42。
For the surname's first token the prior is about zero, so the signal there is almost all about this paper.
姓氏第一个 token 上先验约为 0，所以那里的信号几乎全是关于这篇论文的。
So part of the score is name prior, but a clear paper-specific part remains. Next, whether the probe signal is paper-specific too.
所以分数里有一部分是名字先验，但清楚地留下了论文特有的部分。下一页看 probe 信号是不是也论文特有。

**备查（不念）· 上一版讲稿本页全文（原第 P25 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型输出层，比较无标题（名字先验）、假标题、真标题三种条件，全部 9,108 篇。分解方式：prior = m_delete；topic = m_false均值 − m_delete；spec = m_true − m_false均值；每一项都在引用档内算 T − C（4,621 / 2,220 篇，L63，论文 bootstrap）。按 token 角色（全部 token、姓氏第一个 token、姓氏其余部分、名的第一个 token、首字母）分开。

**关键数字和 CI：**
- 无标题时：排名约 12（Stage 12 A，9,108 篇，§6.12）。
- target − control：先验 +0.09，论文特异 +0.21（Stage 12 A，4,621 + 2,220，档内，§6.12）。
- 姓氏第一个 token：先验约 0，论文特异 +0.42。
- 先验与识别的相关 rho 0.09（Stage 12 B，8,894 篇 R0/R1）。

**结论状态：** 初步（较稳但有前提：删除标题不等于纯名字先验；第 73 页的 N2 纯先验估计约占差距的 19%）。

**过渡：** 读出 lens 在中间层看不到这种差别，换一个工具：在标题位置训练 probe。下一页是 probe 的方法图。

**图旁公式（灰色行）：** prior = nlr(delete),  topic = mean₅ nlr(false) − nlr(delete),  spec = nlr(true) − mean₅ nlr(false);  each T − C within citation bins · n = 9,108 papers (4,621 target + 2,220 control), L63

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{prior}=\mathrm{nlr}(\mathrm{delete})$ · $\mathrm{topic}=\mathrm{mean}_5\,\mathrm{nlr}(\mathrm{false})-\mathrm{nlr}(\mathrm{delete})$ · $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 9,108 papers (4,621 target + 2,220 control), L63；③ prior > 0: the name is easy to guess without a title / topic > 0: any title of the field helps / spec > 0: the true title ranks the author higher than false titles；原 “How computed” 段：How computed: prior = m_delete; topic = m_falsē − m_delete; spec = m_true − m_falsē; each as within-bin T − C · 9,108 papers; 4,621 / 2,220 papers, L63 · paper bootstrap · source: A_prior_decomposition.csv；原公式框：prior = nlr(delete), topic = mean₅ nlr(false) − nlr(delete), spec = nlr(true) − mean₅ nlr(false); each T − C within citation bins n = 9,108 papers (4,621 target + 2,220 control), L63；方法细节移到备用页 B13 (slide 108)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 三项（先验、主题、本论文特有）都按同引用档内的 T − C 计算。

## P72 · HTML v75 p72 · pptx S76 (v22z) — The probe signal is paper-specific

**要说的话（一句英文一句中文）**
This page asks whether the probe signal at the title is specific to this paper.
这一页问：标题处的 probe 信号是不是这篇论文特有的？
We train the probe at the last title token, then replace the true authors with another paper's authors or with authors from the same field.
我们在最后一个标题 token 处训练 probe，再把真作者换成另一篇论文的作者，或者同领域论文的作者。
On the chart, above zero means the probe signal is specific to this paper; it rises from about 0.05 at layer 24 to about 0.08 at layer 56, while both controls are about zero.
图上大于 0 表示 probe 信号是这篇论文特有的；它从第 24 层的约 0.05 升到第 56 层的约 0.08，两个对照都约为 0。
So the probe reads something about this paper from layer 24, which the lens cannot read.
所以 probe 从第 24 层起就能读出关于这篇论文的东西，而 lens 读不出来。
That closes the background block. Next, the tests that read the title position.
背景块到此结束。下一页看读标题位置的几项检验。

**备查（不念）· 上一版讲稿本页全文（原第 P27 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 在最后一个标题 token 处做 5 折岭回归 probe；复核时按作者团队分折，并去掉标题复用。对照组：金标换成另一篇论文的作者、换成同领域论文的作者，以及在假标题上训练的 probe。比较 L24、L40、L56。

**关键数字和 CI：**
- 另一篇论文的作者：约 0；同领域论文：约 0（Stage 12 X1 + Stage 13 复核，§6.12）。
- 所以读到的是"这篇论文"的信息，从 L24 就已存在；lens 读不出来。
- n = 1,863 篇（X1 对照流程，已去掉标题复用：896 target + 499 control + 433 excluded + 35 guard；probe 和两个金标对照柱都是这 1,863 篇的平均，L24/40/56 = 0.0505 / 0.0661 / 0.0801）；“trained on false titles”柱 n = 1,568 篇（复用规则更严）。

**过渡：** 信号是论文特异的；那它和论文的知名度有什么关系？下一页按引用数看。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{probe\ signal}=\mathrm{probe}(\mathrm{true\ title})-\mathrm{probe}(\mathrm{false}_0)$；② n = 1,863 papers (title reuse removed) · 1,568 (trained on false titles, stricter rule)；③ > 0: the probe signal is specific to this paper；原公式框：probe signal = probe(true title) − probe(false_0) n = 1,863 papers (X1-control pipeline, title reuse removed); “trained on false titles” bars: n = 1,568 (stricter reuse rule)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 12 X1 + Stage 13 re-check, §6.12)” → “(Stage 12 probe controls + Stage 13 re-check)”；“(addendum 9, done): surname first token L40 +0.071 [0.058, 0.085] (1,395 papers; e4b_alltok.md).” → “(every-name-token check, done): surname first token L40 +0.071 [0.058, 0.085] (1,395 papers).”

## P73 · HTML v75 p73 · pptx S77 (v22z) — Patchscope and paraphrases

**你在讲稿 doc 里写的批注（从 doc 原样搬来，原在上一版本页的标题下面）：**

【X4 Patchscope：从标题状态里"读出"作者

**怎么做**

1. 正常跑这篇论文的 prompt："Who … titled *Affect dynamics, bereavement and resilience to loss*?"，取**标题最后一个 token** 在第 l 层的 state；
2. 另写一个空白的解码 prompt："Paper: **X** · The first author of the paper is"；
3. 把第 1 步的 state 塞到 **X** 的位置；
4. 看模型接下来说出真实第一作者（Coifman）的可能性有多大。

**对照**：同样的操作，但塞进去的是\*\*另一篇论文（partner）\*\*的标题 state。

**D = 用自己 state 的分数 − 用 partner state 的分数**。分数是 log10(1/真答案的排名)。D > 0 说明这个 state 里有关于这篇论文作者的信息。

| 读什么 | 最早出现 | D | 怎么理解 |
| --- | --- | --- | --- |
| 第一作者 | **L8** | +0.046 | 真作者排名好了约 11% |
| 所有作者 | **L8** | +0.048 | 约 12% |
| 年份 | L40 | +0.013 | 约 3% |
| 领域 | 从未通过 | — | 图上灰色虚线区间很宽 |

X4 "没通过 tune → test 规则"是什么意思：论文分成两半。先在 tune 那一半里找"从哪一层开始有信号"，再到 test 那一半里确认。领域在 tune 里找到的层，到 test 上都没确认成功，所以算"读不出"。在 tune 那一半里，领域在某些层看起来有信号；但拿到 test 那一半去验证，没有一层成立。所以 tune 上的信号很可能是随机波动，结论是"读不出"。

没通过的只是 X4 里"读领域"这一项，第一作者、全部作者、年份都通过了。

"领域没通过"本身也是一个结果，意思是：**用 patchscope 这种方法，从标题 state 里读不出领域。**

但它不能说明"标题 state 里没有领域信息"，因为可能是读法的问题：领域的说法五花八门（"psychology"、"clinical psychology"、"social science"…），要求模型接着 "The field of the paper is" 准确说出某个标签词，本身就很难。M2 用 probe 读领域是能读出来的。

为什么作者先出现值得注意：如果标题位置存的是"这是哪篇论文"，按理说年份、领域这类属性应该比作者名更早、更容易读出。实际上作者在 L8 就有，年份要到 L40，领域一直没有，顺序是反的。

作者是一串名字 token，年份是数字，领域是一个标签词。"谁先出现"比的可能只是"哪个更容易用这种方法读出"，而不是模型内部真正的顺序。所以它只能算一个提示，不能单独作为证据。

另外，P80 的新检查显示 L8 的姓氏信号**超出**了纯文本模型，而且在认得的论文上更强，所以"只是字面联想"也不能完全解释它。这正是目前最值得追的线索。

**2026-11-23 口播补充：**

We then ran a locked follow-up of the surname signal on 6,048 new papers.\
之后我们在 6,048 篇新论文上做了姓氏信号的锁定后续检验。

Beyond a topic-matched paper the signal is plus 0.046; beating a weak text-only model and the recognised-versus-unrecognised gap are both only marginal.\
比主题配对论文多 +0.046；超过偏弱的纯文本模型、以及认得 vs 认不得的差别，都只是勉强通过。

### X3 改写：意思相同的标题会不会被当成同一篇

**怎么做**

每篇论文准备三个标题：

- **原标题**：Affect dynamics, bereavement and resilience to loss
- **改写**（同一篇，换说法）：Affect fluctuations, grief and adaptability in the face of loss
- **D**（用词相近的另一篇真实论文）：Affect and Resistance to Temptation

取最后一个标题 token 的 state，计算：

**G = cos(原, 改写) − cos(原, D)**

G > 0 表示模型觉得"换了说法的同一篇"比"用词相近的另一篇"更接近原标题，也就是它看的是**意思**，不是字面。

图上画的是 **G − G(L4)**：减掉 L4 的值，只看中间层比字面多出来的部分。

**结果**

- **G − G(L4) 从 L8 开始上升，L36 达到峰值 +0.159**：中间层确实比字面更看重意思。
- **行为保留 0.897**：用改写标题提问时，模型偏向真作者的程度保留了约 90%。用原标题时算 100%，换个说法问，它基本仍知道是哪篇。
- **target − control = −0.007**：认得和认不得的论文结果一样。

】

**要说的话（一句英文一句中文）**
This page asks what two tests at the title position show: patchscope and paraphrases.
这一页问：标题位置的两项检验——patchscope 和改写标题——显示了什么？
Patchscope reads the title state out through another prompt; the paraphrase test compares a reworded title of the same paper with a similar other paper.
patchscope 用另一个提示去读标题状态；改写检验把同一篇论文换个说法的标题和用词相近的另一篇论文比较。
On the chart, D above zero means the paper's own state scores its answer higher; the first author is readable from layer 8, about plus 0.046, while the year only from layer 40.
图上 D 大于 0 表示用论文自己的状态时答案分数更高；第一作者从第 8 层起可读，约 +0.046，年份要到第 40 层。
The paraphrase gap rises from layer 8 and peaks near layer 36.
改写标题的差距从第 8 层开始上升，在第 36 层左右达到峰值。
But both could still come from the title's words alone. Next, what these tests can and cannot separate.
但这两项仍然可能只来自标题的文字本身。下一页看这些检验能分开什么、分不开什么。

**备查（不念）· 上一版讲稿本页全文（原第 P82 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**先讲怎么做（指着两张方法图）：**
- X4 Patchscope（左上）：取这篇论文自己提示里最后一个标题 token 的状态（第 l 层），注入一个解码提示（“Paper: X · The first author of the paper is”）的 X 位置，给真答案打分；D = 用自己状态的分数 − 用另一篇（partner）状态的分数。答案有第一作者、所有作者、年份、领域。
- X3 改写（右上）：同一个提示里分别放原标题、意思相同的改写、和一篇用词相近的别的论文，比较最后一个标题 token 的状态余弦；G = cos(原, 改写) − cos(原, 用词相近的论文)。

**再讲结果（指着两张折线图）：**
- X4（左下）：第一作者从 L8 起可读，L8 +0.046 [0.035, 0.059]；所有作者 L8 +0.048 [0.039, 0.058]；年份要到 L40，+0.013 [0.008, 0.018]；领域在任何一层都没通过 tune → test 规则（灰色虚线区间很宽）。
- X3（右下）：G 相对 L4 从 L8 起升高，峰值 L36 +0.159 [0.146, 0.171]；行为上保留 0.897 [0.868, 0.926] 的作者偏好；target − control -0.007 [-0.075, 0.059]。
- 探索性检查（指向第 83 页）：X4 的 L8 姓氏信号不是字面重叠，但年份不超过纯文本模型；X3 的大部分差距纯文本 embedding 模型也有。
- 公式（灰字）：D(l) = mean[log10(1/rank | 自己状态) − log10(1/rank | partner 状态)]；G′(l) − G′(L4)。n = 582 测试篇（X4）· 552 测试篇（X3）。

**So 行：** 第一作者在 L8 就能从标题状态读出，改写标题比用词相近的论文更接近原标题；但这两者都和纯文本模型能看到的差不多，所以都分不开论文身份和意思。

**结论状态：** 较稳 · 描述性；X4 单独不能排除标题文字的解释（C21 未定）。

**过渡：** 先看探索性的总检查页（第 83 页）。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $D=\mathrm{score}(\mathrm{own})-\mathrm{score}(\mathrm{partner})$ · $G'=\cos(\mathrm{orig},\mathrm{para})-\cos(\mathrm{orig},D)$；② n = 582 · 552 test papers；③ D > 0: this state carries this paper’s answer / G′ > 0: reworded same paper is closer；原公式框：n = 582 test papers (X4) · 552 test papers (X3)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）：X4 → patchscope, X3 → paraphrase test; removed source: (X4: summary_x1x4/x4_decodability.csv, summary_b1_xall/x4_D__all.csv, x4_earliest.csv · X3: summary_x3/x3_gap.csv, summary_b1_xall/x3_recovery__all.csv)

**2026-11-23 锁定姓氏检验后的口播补充：**

We then ran a locked follow-up of the surname signal on 6,048 new papers.  
之后我们在 6,048 篇新论文上做了姓氏信号的锁定后续检验。

Beyond a topic-matched paper the signal is plus 0.046; beyond a weak text-only model and the recognised-versus-unrecognised gap are both marginal.  
比主题配对论文多 +0.046；超过偏弱的纯文本模型、以及认得 vs 认不得的差别，都只是勉强通过。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

## P74 · HTML v75 p74 · pptx S78 (v22z) — What the title-position tests can and cannot separate

**要说的话（一句英文一句中文）**
This page asks, as an exploratory check, what the title-position tests can and cannot separate.
这一页做一个探索性检查：标题位置的这些检验能分开什么、分不开什么？
We compared each test with a text-only model, which sees only the title text, and removed papers with literal overlap such as a surname in the title.
我们把每项检验和纯文本模型比——它只看得到标题文字——并去掉了有字面重叠的论文，比如标题里带姓氏的。
Most tests hit a ceiling or match the text-only model: they cannot tell meaning from paper identity.
大多数检验要么碰到天花板，要么和纯文本模型差不多：它们分不开意思和论文身份。
The one thing that went beyond text was the surname signal for recognised papers, and that is what the later locked test checks.
唯一超出文本的是认得的论文上的姓氏信号，后面的锁定检验正是检验这一点。
So to separate meaning from identity, the input itself must change. Next, which title words carry the signal.
所以要把意思和身份分开，必须改变输入本身。下一页看哪些标题词在承载信号。

**备查（不念）· 上一版讲稿本页全文（原第 P83 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这一页讲什么：** 先讲怎么做，再讲结果。四项检查都只用现有数据（事后、未预注册，页面上有“Exploratory”标签）。

**实验设计和关键数字：**
- ① 天花板（左上图）：同一篇论文三种问法时标题状态几乎相同（L4 余弦 0.998）；Qwen L4 的 T 0.98–1.00、跨问题检索 1.000；纯文本 BERT 从第 1 层起检索就是 1.000（图里灰线）。L4 基准对 M3 在补充 2 里事先登记（在任何 M3 数据之前），X5 是事后类推。公式：retrieval = 跨问题 top-1 找回同一篇论文的比例；n = 9,108 篇（测试 582 篇）。
- ② X4（右上）：排除 104 篇字面重叠（标题含姓氏 token 或以人名命名的方法词）后 D +0.064（全部 +0.066）→ 字面重叠贡献约 0；姓 L8 Qwen − BERT +0.104 [0.029, 0.180]；target − control +0.083 [0.042, 0.125]；年份 L40 Qwen − BERT −0.005 [−0.082, +0.072] → 年份不超过纯文本模型；主题先验没有直接测（代理斜率 +0.009 [−0.002, +0.020]）。公式 D = decode(own) − decode(partner)；n = 1,178 篇，效应 = 均值/标准差，团队 CI。
- ③ X3（右下）：all-mpnet（平均池化）达到 Qwen 的 60% [54, 67]，Qwen 只在 L32–L40 显著更高；匹配 D 的 66 篇里是 92% [50, 147]，没有一层显著（all-mpnet 用学术论文对训练过，可能本身带身份）；target 与 control 相同（G′ 差 0.000 [−0.017, 0.018]；保留率 0.898 对 0.898）；按引用数高低分半有差（L24–L48 +0.015 到 +0.033）→ 曝光有影响，选择题标签没有。公式 G′ = (para − D)/(orig − D)；n = 1,110 篇。
- ④ 意思双胞胎（左下图）：两篇意思几乎相同、作者不同的真实论文；106 对候选，严格阈值只有 7 对；标题状态相似度从 L4 到 L63 是平的（双胞胎 0.34–0.39，改写 0.71–0.81，D 0.12–0.16）→ 没有一层显出身份，可行性弱。公式 cos(h_A − μ, h_B − μ)；n = 106 对。

**结论状态：** 全部探索性。底部一句：标题位置的检验要么受天花板限制（M3、检索、X1），要么和纯文本模型差不多（X3、X4 年份）；超出纯文本的只有认得出的论文上 X4 的姓氏信号。要把意思和身份分开，需要输入本身不同（补充 20 的虚构标题）。

**过渡：** 那标题里哪些词在承载论文信号？补充 18b 第 5 项逐类替换。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）：X4/X3/X1/X5 → patchscope / paraphrase test / question swap / layer order; "(add. 2)" dropped; "(addendum 20:" → "(made-up-title test:"; removed source: 381_stage13/summary_explore_{l4audit,x4_source,x3_checks,twins}_20261121/

**2026-11-23 锁定姓氏检验后的口播补充：**

So what goes beyond text is a small surname signal for this paper; about half of the raw signal is topic.  
所以超出文本的是一个很小的、本论文的姓氏信号；原始信号里大约一半是主题。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

## P75 · HTML v75 p75 · pptx S79 (v22z) — Content words carry the signal by meaning: synonyms keep most of it

**要说的话（一句英文一句中文）**
This page asks which words of the title carry the signal, and whether by meaning or by spelling.
这一页问：标题里哪些词在承载信号，是靠意思还是靠字面？
We replace one class of words in the title, either with synonyms or with random tokens, and measure how much paper signal is lost.
我们把标题里的一类词换成同义词或随机 token，测论文信号损失多少。
On the chart, a longer bar means more signal lost; replacing content words with random tokens wipes out the whole signal, about 0.37, while synonyms lose only about 0.09.
图上柱子越长表示损失越多；把内容词换成随机 token 会抹掉整个信号，约 0.37，换成同义词只损失约 0.09。
Random swaps change more tokens than synonyms do, so part of the gap may come from that.
随机替换改动的 token 比同义词多，所以差距有一部分可能来自这一点。
So the meaning matters more than the exact words. Next, a made-up title with the same meaning.
所以重要的是意思，而不是确切的字面。下一页看意思相同的编造标题。

**备查（不念）· 上一版讲稿本页全文（原第 P84 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 18b 第 5 项（设计于 2026-11-17 锁定，没有数值判据 → 描述性）：把标题中的一类词（内容词、罕见词、功能词、首/尾 token）换成 WordNet 同义词或随机 token，看最终输出的论文信号损失。loss = S(true) − S(variant)；Δ = loss(syn) − loss(rand)，Δ < 0 表示同义词保留得更多。词类和表格都在看到任何 GPU 输出之前固定；600 篇（没有可替换词的论文不计），团队 bootstrap。

**关键数字和 CI：**
- 全部信号：S(true) = 0.328。
- 内容词：同义词 0.087，随机 0.374 [0.354, 0.394]（整个信号）；Δ −0.287 [−0.306, −0.269]（n 596）。
- 罕见词：0.023 vs 0.151；Δ −0.140 [−0.159, −0.120]（n 397）。
- 功能词：0.008 vs 0.044；Δ −0.036 [−0.046, −0.027]（n 580）。
- 首/尾 token：0.018 vs 0.067；Δ −0.046 [−0.058, −0.035]（n 544）。
- 标题位置 probe（L8–L24，姓氏金标）：内容词 Δ −0.021 到 −0.029，CI 全部 < 0，方向相同但效应小。
- 局限：WordNet 同义词很粗糙；随机替换改动的 token 更多（12.8 vs 5.6），所以 Δ 有一部分可能来自改动量；有同义词可换的论文更少（罕见词 397 篇）；没有锁定判据。
- n = 有至少 1 个该类词被改动的论文（600 篇中）。

**结论状态：** 描述性。随机替换内容词会抹掉整个信号，同义词只损失一小部分：重要的是含义，而不是字面。

**过渡：** 那么，换成一个意思相同、但根本不存在的虚构标题，能拿到多少？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{loss}=S(\mathrm{true})-S(\mathrm{variant})$ · $\Delta=\mathrm{loss}(\mathrm{synonym})-\mathrm{loss}(\mathrm{random})$；② n = 600 papers (papers without a replaceable word left out)；③ loss > 0: changing these words hurts / Δ < 0: synonyms keep most of it (meaning)；原 “How computed” 段：How computed: loss = S(true) − S(variant); Δ = loss(synonym) − loss(random), paired on the same draws; word classes and tables fixed before any GPU output. 600 papers (papers without a replaceable word left out), team bootstrap.；原出处行：381_stage13/summary_a18b_item5/ (item5_table.csv) · a18b_config/item5_variants_v3.parquet · config/prereg_addendum18b.md；方法细节移到备用页 B18 (slide 113)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Title-word test (design pre-registered …)" ← "Addendum 18b item 5 (design locked 2026-11-17 …)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 同义词和随机替换在同一批抽样上配对；词类和词表在任何 GPU 输出之前就定好了。

## P76 · HTML v75 p76 · pptx S80 (v22z) — A same-meaning made-up title gets about 75% of the way

**要说的话（一句英文一句中文）**
This page asks the sharpest version: does a card with the same topic, but not belonging to this book, work?
这一页问最尖锐的问法：一张写着同样主题、但不属于这本书的卡片，管不管用？
For each paper we wrote a made-up title with the same meaning that belongs to no real paper, and scored it with the true and the false titles, under a rule locked before the run.
我们给每篇论文写了一个意思相同、但不属于任何真实论文的编造标题，和真标题、假标题一起打分，判定规则在运行前锁定。
On the chart, 1 means the made-up title brings back everything the real title gives; we see about 0.75.
图上 1 表示编造标题能找回真标题的全部优势，我们看到的是约 0.75。
The real title adds a little on top, about 0.11.
真标题在上面再多给一点，大约 0.11。
So it mostly reads the topic on the spine, not the call number. This page ran only the made-up-title test; the following pages show where the small extra appears and on which papers it is larger.
所以它读的主要是书脊上的主题，不是索书号。这一页只做了编造标题这一项检验；接下来几页看这一小块多出来的部分在哪里出现、在哪些论文上更大。

**备查（不念）· 上一版讲稿本页全文（原第 P85 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**【2026-11-22 v55】** 锁定判定行不变（部分支持，意思解释大部分）；判定行下方加了一句 “Later: not larger for recognised papers (add. 22); see slide 87.” —— 后续锁定检验：认得出的论文上多出的部分不更大（补充 22 K4 不支持），完整措辞见第 87 页。

**实验设计：** 补充登记 20（2026-11-20 11:14 锁定，sha256 fee691de…，锁定的确认性检验）：给每篇论文写一个意思相同、但 Crossref 查不到的虚构标题，和真标题、5 个假标题一起打分（最终输出 L63，全部作者、全部名字 token 的 log10(1/名次)，论文内平均）。真 − 假的差距 G = S_true − F̄ 拆成两部分：A = S_fict − F̄（虚构标题能恢复的部分，即"意思"），R = S_true − S_fict（只有真标题才给的部分）；φ = ΣA / ΣG。锁定规则：R̄_T 的 95% CI 全在 0 以上才读 φ̂_T；φ̂ < 0.3 强支持，0.3–0.5 部分支持（权重有限），≥ 0.5 部分支持（大部分由语义解释）；R̄ 含 0 不支持；R̄ < 0 被反向结果否定；φ 的 CI 跨 0.3 或 0.5 算边界。1,127 篇（566 target + 561 control；59 篇按生成规则事先排除），作者团队整群 bootstrap 2,000 次。S_true、S_false 用已存的 Stage 10，S_fict 来自本次运行。

**关键数字和 CI：**
- target：φ_T = 0.751 [0.723, 0.778]；R̄_T = +0.106 [+0.094, +0.118]；Ḡ_T 0.425；Ā_T 0.319。
- control：φ_C = 0.770 [0.727, 0.814]；R̄_C = +0.050 [+0.039, +0.061]。
- 分箱内 target − control：R +0.056 [+0.039, +0.072]（H2 预测的方向）；φ −0.022 [−0.081, +0.033]。
- 敏感性 a–f（只用 false_0；去掉 Crossref 相似 ≥ 0.4；真标题 ≥ 6 词；只看第一作者 / 姓首 token；只用 R0；标题 log-prob 三等分）：φ_T 0.708–0.778，R̄_T 都 > 0，结论不变。
- 局限：单一模型；虚构标题在模型下的概率比真标题高（title log-prob 真 − 虚构 target −0.124，control −0.251）；φ 随意思接近程度上升，真标题多出的部分可能部分来自虚构标题没抓住的意思；parity WARN（名次完全相同的比例 0.55–0.66 < 0.75，平均 |Δlog10 名次| ≤ 0.014），按规则保留数字。
- n = 1,127 篇（566 target，561 control）· 团队整群 bootstrap 2,000 次。

**结论状态：** 锁定的确认性检验：R̄_T 的 CI > 0 且 φ̂_T ≥ 0.5 → H2 部分支持——存在真实论文成分，但大部分信号可由语义相似解释。不在边界上。

**过渡：** 只有真标题才给的那一小块，是在哪些层加进来的？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\varphi=\sum A\,/\sum G$ · $G=S_{\mathrm{true}}-\bar F,\ A=S_{\mathrm{made\ up}}-\bar F,\ R=S_{\mathrm{true}}-S_{\mathrm{made\ up}}$；② n = 1,127 papers (566 target, 561 control)；③ φ ≈ 1: meaning alone is enough / R > 0: the real title adds something；原 “How computed” 段：How computed: per paper, S = mean over name tokens of log10(1/rank) at the final output (all authors, all tokens); S_true, S_fict, F̄ = mean of the 5 false titles; G = S_true − F̄, A = S_fict − F̄, R = S_true − S_fict; φ = ΣA / ΣG over the group (ratio of sums); verdict by the point estimate φ̂_T, read only when the 95% CI of R̄_T lies entirely above 0 (φ̂ < 0.3 strongly supported; 0.3–0.5 partly, limited weight; ≥ 0.5 partly, meaning explains most; R̄ CI ∋ 0 not supported; R̄ CI < 0 refuted); borderline if the φ CI crosses 0.3 or 0.5 · S_true, S_false from the stored Stage 10 run, S_fict from this run · 391_groups/summary_a20/primary_secondary_sensitivity.csv；原灰色 n 行（已并入 LaTeX n 行）：n = 1,127 papers (566 target, 561 control; 59 excluded by the generation rule) · team-cluster bootstrap, 2,000 draws；原出处行：391_groups/summary_a20/a20_report.md · primary_secondary_sensitivity.csv · a20_results.json (tc_R, tc_phi) · config/prereg_addendum20.md (sha256 fee691de…)；方法细节移到备用页 B18 (slide 113)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Made-up-title test (locked before the run)" ← "Addendum 20 (locked before the run)"; "(add. 22)" → "(rewrite test, pre-registered)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 计入全部作者、全部 token；φ 是按组求和后再相除（比值的和，不是和的比值的平均）。 其余判定：R̄ 的 CI 含 0 = 不支持，< 0 = 推翻；φ 的 CI 跨过 0.3 或 0.5 = 边界。 S_true、S_false 来自已存的 Stage 10 运行，S_fict 来自本次运行。

## P77 · HTML v75 p77 · pptx S81 (v22z) — How the 75% is computed

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
So "about 75%" is a locked reading of this one test; the next pages ask what the remaining small part is.
所以"约 75%"是这一项检验的锁定读法；接下来几页问剩下的那一小块是什么。

**备查（不念）：** 每篇论文的得分 S = 名字各 token 的 log10(1/排名) 取平均（最后一层，所有作者、所有 token）；F̄ = 5 个假标题（false_0…false_4）的平均；G = S_true − F̄，A = S_fict − F̄，R = S_true − S_fict；φ = ΣA / ΣG（组内求和之比）。认得的论文（566 篇）：G 0.425，A 0.319，φ̂ = 0.751 [0.723, 0.778]，R̄ +0.106 [+0.094, +0.118]；对照组 561 篇。判定分档（运行前锁定）：φ̂ < 0.3 强支持（论文身份），0.3–0.5 部分支持、权重有限，≥ 0.5 部分支持、以意思解释为主；R̄ 的 CI 含 0 = 不支持，< 0 = 推翻；φ 的 CI 跨过 0.3 或 0.5 = 边界。S_true 和假标题得分取自已存的全队列运行，S_fict 取自本次运行。这是这一项检验的锁定读法；H2 的总判定见判定卡。证据强度：locked。

## P78 · HTML v75 p78 · pptx S82 (v22z) — Where the real-title extra appears

**要说的话（一句英文一句中文）**
This page asks at which layers the real title's small extra appears.
这一页问：真标题多出来的那一小块在哪几层出现？
We follow, layer by layer, the real title minus the made-up title, and we repeat the put-back test with the made-up title as the source.
我们逐层看真标题减编造标题，并用编造标题作来源重做放回实验。
On the chart, a value above zero means the real title gives more; it is about zero up to layer 48 and clearly positive from layer 56.
图上大于 0 表示真标题给得更多；到第 48 层为止约为 0，从第 56 层起明显为正。
Putting back the made-up title's states restores only about three quarters, while the real title restores everything.
放回编造标题的状态只能恢复大约四分之三，而真标题能恢复全部。
So the extra is added late, at the name positions. Next, whether it is already there at the title.
所以多出的部分是在后面、在名字位置加进来的。下一页看它在标题位置是不是已经有了。

**备查（不念）· 上一版讲稿本页全文（原第 P87 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**【2026-11-22 v55 · H2 新措辞（用户确定，状态仍为 partly supported）】** 讲这句（英文原句，屏幕上同样写法）：“H2 partly supported: a real-title extra over a same-meaning fabricated title exists (R̄_T +0.106), mostly carried by meaning (75%). The extra sits mainly on the title's rare and specific words (names, acronyms, technical terms): replacing only those words loses R̄ = 0.162, vs 0.027 for common words (addendum 24). It is not larger for recognised papers (K4 not supported) and is smaller for more-cited papers (K4c reversed). Whether the extra reflects specific wording or a penalty on fabricated titles remains open.” 紧接着说明补充 24 的两点：（补充 24 的两点说明：两种替换的词数不同，罕见词平均换 3.4 个、常见词 2.1 个；常见词是按词频匹配替换，不是同义词，意思也会改变。） 中文意思：H2 部分支持：真标题比意思相同的编造标题多出一部分（R̄_T +0.106），大部分由意思承担（75%）。多出的部分主要落在标题里罕见、具体的词上（人名、缩写、专门术语）：只替换这些词损失 R̄ = 0.162，只替换常见词损失 0.027（补充 24）。它在认得出的论文上并不更大（K4 不支持），在引用多的论文上反而更小（K4c 反向）。这多出的部分反映的是具体措辞，还是模型对编造标题的惩罚，仍未确定。

**实验设计：** 补充登记 20 的次要比较（描述性）：同样 1,127 篇。左图：逐层看 R̄ = S_true − S_fict（名字位置，logit lens 和公开 J-lens，L24–L62，再加最终输出 L63）。右图：Stage 11 E1 式替换——把 false_0 运行中标题之后的那段状态在第 l 层换成供体运行的状态，rec(l) = mean(patched − false_0) / mean(true − false_0)；供体是真标题（已存的 Stage 11 E1）或虚构标题（本次运行）。

**关键数字和 CI：**
- R̄ 在 L48 以前约为 0（J-lens 在 L32、L48 对 target 略低于 0），从 L56 起才明显 > 0：J-lens L62 +0.115，最终输出 +0.106。
- E1 替换：真标题供体 L52 起恢复全部（1.00）；虚构标题供体从 L52 起停在约 0.745；差 +0.255 [+0.227, +0.284]（L54）。L63 自检一致（0.7453 = 0.7453）。
- 标题位置 probe：真 − 虚构只有 +0.02 到 +0.04（target），真 − 假标题 +0.06 到 +0.10。
- 语义剂量：按虚构与真标题的余弦三等分，φ 为 0.722 / 0.740 / 0.794；第 3 − 第 1 组 +0.072 [+0.002, +0.140]，方向符合"标题文字相似"的解释。
- n = 1,127 篇（566 target，561 control）。

**结论状态：** 描述性（次要比较，无单独判据）：只有真标题才给的部分是在后面、名字位置上（L52 以后）加进来的；虚构标题替换只能恢复约四分之三。

**过渡：** 回到子空间：如果只交换标题状态里的某个子空间，能把论文信息搬过去吗？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\bar R=\mathrm{mean}(S_{\mathrm{true}}-S_{\mathrm{made\ up}})$ · $\mathrm{rec}(l)=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{false}_0)}{\mathrm{mean}(\mathrm{true}-\mathrm{false}_0)}$；② n = 1,127 papers (566 target, 561 control)；③ R̄ > 0: only the real title gives it / rec ≈ 1: the donor restores all of it；原 “How computed” 段：How computed: R̄ = mean over papers of S_true − S_fict at each readout (logit lens, public J-lens) and layer, name positions, within each group; rec(l): the post-title tail of the false_0 run is replaced at layer l by the donor run’s states, rec = mean(patched − false_0) / mean(true − false_0) (denominator and true-donor curve from the stored Stage 11 E1 run; L63 identity checked: 0.7453 = 0.7453) · team-cluster bootstrap, 2,000 draws · 391_groups/summary_a20/S3_layer_profile.csv, S4_E1_fict_donor.csv, S5_E4b_probe.csv, a20_results.json (dose_trend)；原灰色 n 行（已并入 LaTeX n 行）：n = 1,127 papers (566 target, 561 control; 59 excluded by the generation rule) · team-cluster bootstrap, 2,000 draws；原出处行：391_groups/summary_a20/a20_report.md (§2 S3, S4, S5, S7) · config/prereg_addendum20.md；方法细节移到备用页 B19 (slide 114)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Made-up-title test, secondary comparisons" ← "Addendum 20, secondary comparisons"; "(E1 design)" → "(put-back design)"; "stored Stage 11 E1" → "stored Stage 11 put-back run"; "addendum-24 caveats" → "rare-word caveats"; "(add. 22)" → "(rewrite test, pre-registered)"
- 图内公式框里的判据 / 说明（移出幻灯片）：donor = true title (stored Stage 11 put-back run) or the made-up title (this run)

**2026-11-23 锁定姓氏检验后的口播补充：**

This page is the made-up-title test alone; with the locked surname test, H2 overall is: not a general paper identity, with one small exception.  
这一页只是虚构标题检验本身；加上锁定姓氏检验后，H2 总判定是：不是一般的论文身份，只有一个小例外。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 分母和真标题供体曲线取自已存的 Stage 11 放回运行；L63 一致性检查 0.7453 = 0.7453。 剂量趋势检验在原始报告里另有内部名称（不上幻灯片）。

## P79 · HTML v75 p79 · pptx S83 (v22z) — Not at the title: the real-title extra and the exposure gap both form later

**要说的话（一句英文一句中文）**
This page asks, as an exploratory check, whether the real title's extra is already there at the title position.
这一页做一个探索性检查：真标题多出的部分，在标题位置是不是已经存在？
We read the title position with a probe under the real title, the made-up title and a false title.
我们用 probe 分别读真标题、编造标题和假标题下的标题位置。
On the chart, true minus made-up above zero means the real title carries more; at layer 40 it is only about 0.016, about a fifth of the gap between true and false titles.
图上真减编造大于 0 表示真标题带的更多；第 40 层只有约 0.016，大约是真标题和假标题差距的五分之一。
It grows only from about layer 48, and more-cited papers are not stronger here.
它大约从第 48 层才开始增长，引用多的论文在这里也并不更强。
So the extra and the exposure gap both form later, nearer the saying step. Next, a summary of the background line.
所以多出的部分和曝光差距都是后来才形成的，更靠近“说出”那一步。下一页小结这条背景线。

**备查（不念）· 上一版讲稿本页全文（原第 P86 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计（探索性，事后分析，未预注册）：** 左图：补充 20 的 1,127 篇（566 target + 561 control），用标题位置的 probe（第一作者名的第一个 token；按已发表设置在 9,108 篇真标题运行上重新拟合，作者团队分折）分别读真标题、虚构标题和 false_0 的标题状态，Δ = probe(真) − probe(虚构)，逐层。右图：已存的逐篇 probe 输出，按各自集合的引用数中位数分成两半（标题 probe V0 1,395 篇中位数 55，Vpd 4,654 篇中位数 66；名字位置 probe 4,654 篇），比较引用数中位数分半后的 target − control（引用档内）。团队整群 bootstrap 2,000 次。

**关键数字和 CI：**
- 标题位置 L40：target 真 − 虚构 +0.016 [−0.001, +0.033]，control +0.009 [−0.008, +0.025]，target − control +0.008 [−0.016, +0.031]；同一位置真 − 假标题 +0.078 [0.058, 0.097]，所以真标题多出的部分在标题位置约只有五分之一。
- 往后长大：target 真 − 虚构 L52 +0.039 [0.022, 0.057]，L56 +0.041 [0.024, 0.058]；target − control 只有 L32 排除 0（+0.026 [0.003, 0.050]）。
- 高 − 低引用半，target − control：标题 probe V0 +0.003 [−0.076, +0.083]；Vpd −0.019 [−0.059, +0.021]；名字位置 L40 +0.002 [−0.025, +0.027]，L48 +0.001 [−0.031, +0.030]——区间都含 0。高引用的对照组很少（119 / 331 篇），区间宽。

**图旁公式（灰色行）：** 左 Δ = probe(true) − probe(made-up title)；右 y = (T̄ − C̄)_high − (T̄ − C̄)_low，T − C 在引用档内算，probe spec = probe(true) − probe(false)。n = 左 1,127 篇（566 + 561），右 1,395 / 4,654 篇。

**结论状态：** 探索性（事后，未预注册）。读法：真标题多出的部分在标题位置很小、从 L48 起才形成；引用多的论文在标题和名字位置的 probe 上并不更强——曝光断层更像在“说出”那一步。来源 391_groups/summary_a20/S5_E4b_probe.csv；381_stage13/summary_explore_citesplit_probes_20261121/report.md。

**过渡：** 那真标题多出的部分从哪一层出现？看下一页。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{extra}=\mathrm{probe}(\mathrm{true})-\mathrm{probe}(\mathrm{made\ up})$ · $y=(\bar T-\bar C)_{\mathrm{high}}-(\bar T-\bar C)_{\mathrm{low}}$；② n = 1,127 papers (566 target + 561 control) · right: 1,395 / 4,654 papers；③ extra > 0: the real title adds at this layer / y > 0: more-cited papers are stronger；原 “How computed” 段：How computed: left = addendum 20 papers, title-position probe refitted on the 9,108 true runs (team folds), applied to the true, made-up and false_0 title states; right = stored per-paper probe outputs (title probe V0 reuse-free set and per-donor set; name-position probe of the locked H3 test), split by citations; team-cluster bootstrap, 2,000 draws · 391_groups/summary_a20/S5_E4b_probe.csv · 381_stage13/summary_explore_citesplit_probes_20261121/；原灰色 n 行（已并入 LaTeX n 行）：n = 1,127 papers left (566 target + 561 control) · right: 1,395 / 4,654 papers (split at medians 55 / 66)；原出处行：391_groups/summary_a20/S5_E4b_probe.csv · 381_stage13/summary_explore_citesplit_probes_20261121/report.md；方法细节移到备用页 B19 (slide 114)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："(made-up-title set)" ← "(addendum 20 set)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 左图：预注册检验论文；标题位置 probe 在 9,108 次真标题运行上按团队分折重拟合，再用到真标题、编造标题和 false_0 的状态上。

## P80 · HTML v75 p80 · pptx S84 (v22z) — What we saw: “Is it about this paper?”

**要说的话（一句英文一句中文）**
This page sums up what the small samples and the full cohort showed about “is it about this paper?”.
这一页小结关于“是不是这篇论文”，小样本和全队列各自看到了什么。
The small samples showed that the true title helps, about 9 points in the pilot and about 5 on 200 new papers, while the group gap was uncertain.
小样本显示真标题有帮助：先导阶段约 9 个点，200 篇新论文上约 5 个点；而组间差距不确定。
The full cohort showed a clear paper signal in every group, recognised papers ahead only at the output, and a signal that grows steadily with citations.
全队列显示每一组都有清楚的论文信号，认得的论文只在输出层领先，信号随引用数稳定增长。
The pilot could not see that the recognised lead sits only in the last layers, so its averages diluted it.
小样本看不出认得的领先只集中在最后几层，所以它的平均把这个效应稀释了。
Next, back to the decisive tests: why question-only tests cannot see identity.
接下来回到决定性检验：为什么只换问题的检验看不到身份。

**备查（不念）· 上一版讲稿本页全文（原第 P33 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 左右对照。小样本：真标题有用（pilot L56 +9.3 pp，7.3，50 篇；200 篇新论文 +5.2 pp，8D RQ1）；A−B 在 pilot 里不确定，200 篇上 +5.0 pp，但去掉 10 对后消失（8D RQ2，100 对）；低 − 高引用：没有结论。全队列：title-specific 信号在每组都清楚，L62 约 0.44（§6.9）；target − control 在 L24–L40 约 0，L48 略负（−0.04 到 −0.05）（§6.4），输出层 +0.21 [0.20, 0.22]（L63，§6.4）；名字先验（删除标题条件）只占差距的约 0.35，在姓氏上约 0（§6.12）；信号随引用稳定上升（ρ = 0.451，§6.8）；与 pilot 同组（只看 R0，A − B）：+0.20 [0.19, 0.21]（§6.13），同样晚出现；R1 论文（C）知道得更多（比 A 高 +0.11，§6.13），但出现时间差不多一样晚。

**关键数字（全队列补充）：**
- 曝光差距（补充 19，锁定在看数据之后）：认出约 40 次引用，写出约 11,000 次，ρ = 276 [203, 390] → 第 29 页。
- 合作者链（补充 16）：效应真实存在（+0.167），但这是合作者网络的关联，不是对这篇论文的记忆 → 第 59–60 页。
- n = 50 / 200 篇、100 对（Stages 1–9）· 9,108（Stages 10–11，补充 19）· 1,428（补充 16 D）。

**结论状态：** A 线总体：标题效应和后层的 target 优势为定论；曝光门槛为初步（锁定在看数据之后）；合作者链为预注册判据成立但不是论文特异。一句话：从"标题有用"推进到"是这篇论文、出现得晚、随知名度分级"。pilot 没能看出 target 优势只集中在最后几层，所以 7 层平均和 L56 终点都把它稀释了；全队列只保留 A/B（R0）时结果不变，说明结论不是 R1 论文带出来的。

**过渡：** 进入 B 线：不同读出工具各自能看到什么。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $T-C=\Sigma_b w_b\,(\overline{\mathrm{spec}}_{T,b}-\overline{\mathrm{spec}}_{C,b})$；② n = 50 / 200 papers, 100 pairs (Stages 1–9) · 9,108 (Stages 10–11) · 1,428 (name-chain test)；③ T − C > 0: recognised papers’ authors read better than control；原公式框：T − C = Σ b w b (spec T,b − spec C,b ) n = 50 / 200 papers, 100 pairs (Stages 1–9) · 9,108 (Stages 10–11, add. 19) · 1,428 (add. 16 D)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(L62, §6.9)
- 出处（原在幻灯片上）：(§6.4)
- 出处（原在幻灯片上）：(L63, §6.4)
- 出处（原在幻灯片上）：(§6.12)
- 出处（原在幻灯片上）：(§6.8)
- 出处（原在幻灯片上）：(R0, §6.13)
- 出处（原在幻灯片上）：(§6.13)

**备查（不念）：**
- 方框原写 “(add. 19; …)”、“Co-author chain (add. 16)”：add. 19 = 曝光门槛补充登记，add. 16 = 生成测试补充登记（名字链）

## P81 · HTML v75 p81 · pptx S85 (v22z) — Why the change-the-question test cannot see identity: a ceiling

**要说的话（一句英文一句中文）**
This page asks whether a test that changes only the question can tell paper identity from meaning.
这一页问：只换问题的检验，能不能把论文身份和意思分开？
We keep the title and change the question, then compare the title state across questions.
我们保持标题不变、只换问题，再比较各问题下的标题状态。
On the chart, a value near 1 means the same paper is found again; a text-only model already reaches it at its first layers, and Qwen at layer 4, where the two states have a cosine of 0.9976.
图上接近 1 表示又找回了同一篇论文；纯文本模型在最初几层就达到了，Qwen 在第 4 层，两个状态的余弦是 0.9976。
The same words give the same state under every question, so these tests sit at the ceiling.
同样的文字在每个问题下给出同样的状态，所以这些检验都在天花板上。
So they cannot decide H2; the next tests change the words instead. Next, whether the extra grows with recognition.
所以它们判定不了 H2，下面的检验改为改变文字本身。下一页看多出的部分会不会随“认得”变大。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Why tests that change only the question cannot decide H2: the ceiling Part 4 · What is read: meaning, not identity (H2) Why tests that change only the question cannot decide H2: the ceiling Now asking: can a question-only test (same title, different question) tell paper identity from meaning? Method: change only the question, keep the title: compare the title state across questions (retrieval, cosine, probe transfer, question swap) Result: 1 a text-only model already finds the same paper at its first layers; 2 Qwen does so from L4 (1.000) — cosine of the two states 0.9976 at L4 Control: a text-only model (BERT) sees only the title text, so whatever it reaches is reachable from the words alone So what: these tests are at the ceiling : the same words give the same state under every question, so they cannot tell meaning from paper identity exploratory Caveat: retrieval on the 582 test papers; Qwen's ceiling is from earlier slides, BERT's from this check Next: make the inputs differ: same meaning with new words → slide 73 retrieval ≈ 1: the title finds its own paper — no room left above So (this slide): question-only tests hit the ceiling at L4 — identical words, identical state; separating meaning from identity needs different inputs.

数字出处：27_v67/fragments/part34_numbers.md

## P82 · HTML v75 p82 · pptx S86 (v22z) — Recognised vs not, and by citations: the real-title extra does not grow

**要说的话（一句英文一句中文）**
This page asks: if the extra were the call number, would it grow with recognition and with citations?
这一页问：如果多出的部分是索书号，它会不会随“认得”和引用数变大？
We score the same papers with the real title and with the same-topic card, and take the difference, under rules locked before the run.
我们用真标题和同主题的卡片给同一批论文打分，取差值，规则在运行前锁定。
On the chart, a value above zero means the extra is larger in the first group; for recognised against unrecognised the interval includes zero at every pre-registered layer.
图上大于 0 表示第一组多出的部分更大；认得对认不得，在每个预注册的层上区间都包含 0。
For more against less cited papers it is even reversed: the extra is smaller for the more-cited ones.
引用多对引用少，结果甚至相反：引用多的论文多出的部分反而更小。
So the extra does not behave like the call number. Next, what explains the title state.
所以多出的部分不像索书号那样变化。下一页看标题状态由什么解释。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

The real-title extra is not larger for recognised papers — and smaller for more-cited ones Part 4 · What is read: meaning, not identity (H2) The real-title extra is not larger for recognised papers — and smaller for more-cited ones Now asking: if the extra were paper identity, would it grow with recognition and with citations (H2, prediction 2)? Method: the same papers scored with the real title and with a same-meaning made-up title; the extra = what only the real title gives Result 1 (locked): 1 the extra is not larger for recognised papers (Holm CI includes 0 at every pre-registered layer) locked · not supported Result 2 (locked): 2 it is smaller for more-cited papers (Holm CI < 0 from L24) locked · reversed Control: recognised vs not compared within citation bins; more vs less cited compared within field Caveat: without the Holm correction the recognised − not difference is just above 0 at L24 (+0.018 [+0.001, +0.034]) So what: two identity predictions fail : what the real title adds does not track how strongly the paper is recognised Δ > 0: the real-title extra is larger for recognised (or more-cited) papers So (this slide): recognition: not supported; citations: reversed (both locked) — the extra is not a recognition-related signal.

数字出处：27_v67/fragments/part34_numbers.md

## P83 · HTML v75 p83 · pptx S87 (v22z) — Variance split: identity adds ≈ 0 beyond text features

**要说的话（一句英文一句中文）**
This page asks whether paper identity explains the title state beyond its text.
这一页问：在文字之外，论文身份能不能解释标题状态？
We predict the title-position state of 9,108 papers from four groups of features, and ask what each group adds on its own.
我们用四组特征去预测 9,108 篇论文的标题位置状态，看每组单独能多解释多少。
On the chart, a bar is the share of variance a group adds; meaning adds about 0.17 to 0.27, identity adds about zero.
图上柱子是每组特征多解释的方差比例；意思多解释约 0.17 到 0.27，身份约为 0。
Identity is positive only at one layer and with one text model, so it counts as borderline at most.
身份只在一层、只用一个文本模型时为正，所以最多算边界。
So meaning explains the state; identity adds almost nothing. Next, which words carry what the made-up title misses.
所以解释标题状态的是意思，身份几乎没有贡献。下一页看编造标题漏掉的部分由哪些词承载。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

What explains the title state? Meaning does; paper identity adds ≈ 0 Part 4 · What is read: meaning, not identity (H2) What explains the title state? Meaning does; paper identity adds ≈ 0 Now asking: does paper identity explain the title-position state beyond its text (H2, prediction 3)? Method: predict the title-position state of 9,108 papers from four feature groups; ask what each group adds on its own Result 1 (locked): 1 meaning adds 0.17–0.27 of the variance beyond the other three groups locked · supported Result 2 (locked): 2 identity adds ≈ 0 (−0.0097 to +0.0019); positive only at L48 and only with one text model borderline Recognition: identity adds a little more for recognised papers (target − control +0.0011 to +0.0045) locked · supported (tiny) Control: two text models (BERT primary, MPNet reported); author features residualised on text so overlap is not double-counted So what: the state is explained by meaning; identity adds ≈ 0 unique R² > 0: that feature group explains part of the state the others do not So (this slide): meaning adds 0.17–0.27 of the variance on its own; identity ≈ 0 (borderline at L48) — prediction 3 fails.

数字出处：27_v67/fragments/part34_numbers.md

## P84 · HTML v75 p84 · pptx S88 (v22z) — Rare words carry the real-title extra

**要说的话（一句英文一句中文）**
This page asks which words of the real title carry what the same-topic card misses.
这一页问：真标题里哪些词承载了同主题卡片漏掉的那部分？
We swap either rare, specific words or common words in the true title, under a locked rule.
按锁定的规则，我们把真标题里的罕见具体词或者常见词换掉。
On the chart, a longer bar means more of the signal lost; swapping rare words costs about 0.16, swapping common words only about 0.03.
图上柱子越长表示信号损失越多；换罕见词损失约 0.16，换常见词只损失约 0.03。
Two caveats: the rare-word swap changes more words on average, and the common words were matched on frequency, not synonyms; with equal counts the gap remains.
两点局限：换罕见词平均改动的词更多；常见词是按词频匹配的，不是同义词。词数相等时差距仍然存在。
So the extra sits mainly on rare, specific words. Next, the one place where something paper-specific does show up.
所以多出的部分主要在罕见、具体的词上。下一页看唯一确实出现了论文特有信息的地方。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Rare, specific words carry the real-title extra; common words barely do Part 4 · What is read: meaning, not identity (H2) Rare, specific words carry the real-title extra; common words barely do Now asking: which words of the real title carry what a same-meaning made-up title misses? Method: two word swaps on the true title of each paper; same prompt, same scoring at the final layer Result (locked): 1 rare-word swap costs 0.162 , common-word swap 0.027 : D = +0.134 [+0.115, +0.154] locked · supported Control: the common-word swap replaces the same number of words; the made-up title (same meaning, all words new) is shown for scale Caveat: (a) replaces more tokens on average (3.4 vs 2.1 words); common words are frequency-matched, not synonyms ; with equal counts the gap remains (+0.066 [0.049, 0.082], exploratory) So what: the real-title extra sits mainly on rare, specific words — consistent with meaning + specific words, not identity R̄ > 0: swapping those words loses part of the true-title advantage So (this slide): swapping rare words costs about 6× more than swapping common ones (locked) — the extra is in specific words.

数字出处：27_v67/fragments/part34_numbers.md

## P85 · HTML v75 p85 · pptx S89 (v22z) — The one locked exception: a small surname signal at L8

**要说的话（一句英文一句中文）**
This page asks whether any paper-specific signal in the title state survives matching on topic.
这一页问：标题状态里有没有论文特有的信号，在配对主题之后仍然存在？
We decode the first author from the title state at layer 8 and subtract what a paper on the same topic gives, on 6,048 new papers, with the rules locked before the run.
我们从第 8 层的标题状态解码第一作者，再减去同主题论文的状态给出的结果，在 6,048 篇新论文上做，规则在运行前锁定。
On the chart, a value above zero means the state carries information about this paper's first author beyond its topic; at layer 8 it is about 0.046, a robust result.
图上大于 0 表示这个状态在主题之外带着这篇论文第一作者的信息；第 8 层约 0.046，结果稳健。
Two further checks only just pass: beyond a text-only model, whose own positive control failed, and larger for recognised papers.
另外两项检验只是刚过线：超过纯文本模型——而这个模型自己的正对照没通过——以及认得的论文更大。
The locked test is at layer 8; later layers are larger, peaking at layer 40, but that part is descriptive only. And about half of the raw signal comes from the topic.
锁定检验只在第 8 层；后面几层更大，在第 40 层最高，但那只是描述性的。而且原始信号大约一半来自主题。
So there is one small locked exception, not strong evidence. Next, the verdict card.
所以有一个小的锁定例外，不是强证据。下一页是判定卡。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

The one locked exception: a small paper-specific surname signal from L8, beyond topic Part 4 · What is read: meaning, not identity (H2) The one locked exception: a small paper-specific surname signal from L8, beyond topic Now asking: is there any paper-specific signal in the title state that survives topic matching (H2, prediction 4)? Method: decode the first author from the title state at L8 (patchscope); subtract what a topic-matched paper's state gives; 6,048 new papers, rules locked before the run Result: 1 T1 beyond topic: +0.046 [+0.035, +0.056] locked · supported ; T2 beyond a text-only model and T3 larger for recognised papers marginal (Holm lower bounds +0.002, +0.003) Layers: the locked test is at L8; at later layers the topic-matched signal is larger (peak L40, +0.093), descriptive only, and falls back to ≈ 0 by L56 Control: topic-matched and random same-field partners; a BERT text baseline on the same pairs; embeddings-only (L0) source ≈ 0 Caveat: about half of the raw surname signal is topic (0.44 [0.36, 0.52] survives topic matching); the text baseline failed its own positive control; small effect, not strong evidence So what: one small locked exception to "not identity": the L8 title state carries a little paper-specific surname information D_topic > 0: the state carries information about this paper's first author beyond its topic So (this slide): T1 robust, T2 and T3 marginal, about half of the raw signal is topic — a small locked exception, not a paper-identity representation.

数字出处：27_v67/fragments/part34_numbers.md

## P86 · HTML v75 p86 · pptx S90 (v22z) — Verdict card · H2

**要说的话（一句英文一句中文）**
Let's close Part 4 by answering the question we opened it with.
用开头那个问题来结束第 4 部分。
The model mostly takes the topic on the spine, not the call number.
模型主要拿走的是书脊上的主题，不是索书号。
The same-topic card gets about three quarters of the way, and the real title's small extra sits on rare words and does not grow with recognition.
同主题的卡片能走到大约四分之三，真标题多出的一小块落在罕见词上，而且不随“认得”变大。
There is one exception that held up under a locked test on six thousand new papers: from layer 8, the title state carries a small surname signal for this particular paper, beyond its topic.
有一个例外，在六千多篇新论文上的锁定检验里站住了：从第 8 层起，标题状态里有一个属于这篇论文的小姓氏信号，超出了主题。
But keep it in proportion: about half of that signal is still topic, and two of the three checks only just pass.
但要看清比例：这个信号大约一半仍然来自主题，三项检验里有两项只是刚过线。
So the verdict is: meaning, not a general paper identity, with one small locked exception. Next, the evidence matrix.
所以结论是：是意思，不是一般意义上的论文身份，有一个小的锁定例外。下一页是证据矩阵。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Verdict card · H2: meaning and specific words, one small exception Part 4 · What is read: meaning, not identity (H2) Verdict card · H2: meaning and specific words, one small exception Now asking: what did the H2 tests show, and how strong is each result? Prediction Result Strength Slides ① made-up title recovers little fails : it recovers 75% (φ = 0.751) locked · supported 73, 74 ② extra larger for recognised / more-cited fails : not larger; smaller for more-cited locked · not supported locked · reversed 78 ③ identity explains the state beyond text fails : ≈ 0 (meaning does) locked borderline 79 ④ paper-specific answer beyond topic small exception : surname signal from L8 (T1 robust; T2, T3 marginal); locked at L8, larger at later layers (peak L40, descriptive) locked · supported marginal 81 — what remains sits on specific words holds : rare 0.162 vs common 0.027 locked · supported 80 Verdict · H2 Not supported as a general paper-identity representation, with one locked exception: the title state at L8 carries a small paper-specific surname signal that survives topic matching (T1, robust), exceeds a weak text-only baseline (T2, marginal; the baseline failed its positive control) and is larger for recognised papers (T3, marginal). Otherwise the real-title advantage is carried mainly by meaning and specific words. Open: a text-only baseline that passes its positive control (would make T2 decisive) about half of the surname signal is topic meaning twins (real papers, same meaning): too few pairs so far So (section): H2 is not supported as paper identity (one small locked exception). Next (Part 5): the meaning reaches the name positions — how does it get there, and in what form is the author held?

数字出处：27_v67/fragments/part34_numbers.md

## P87 · HTML v75 p87 · pptx S91 (v22z) — Evidence matrix after Part 4

**要说的话（一句英文一句中文）**
This matrix shows where each hypothesis stands after Part 4.
这张矩阵显示第 4 部分之后每个假设的位置。
The H2 row is now filled: title words matter by meaning, the same-topic card gets about 75%, and there is a small surname signal from layer 8.
H2 这一行已经填上：标题词靠意思起作用，同主题卡片能走到约 75%，还有一个从第 8 层起的小姓氏信号。
So H2 reads: not a general paper identity, with one small locked exception.
所以 H2 是：不是一般意义上的论文身份，有一个小的锁定例外。
Next, Part 5: where the information goes, and in what form it is held.
接下来是第 5 部分：信息送到哪里，以什么形式存着。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Evidence matrix after Part 4 Now asking: with Part 4 done, where does each hypothesis stand? H1 · does the middle know "what is asked"? (✓) “:” new question vs paper 4.7× (L4) → 2.2× (L48) descriptive s. 51 (✓) probe after the question change T 0.24–0.41 descriptive s. 49 ~ top lens word format words; title-dependent 28–64% descriptive s. 37 ~ format locking (+ checks) L56 = sink artefact; names default locked + exploratory s. 52 (✓) swap “:” at L56 author signal −0.03 locked s. 52 Verdict: downgraded: “:” follows the question; the format layer is not pinned down → s. 53 H3 · author info in the middle, not in vocabulary directions? tested in Part 5 H2 · does the middle know "which paper"? ~ paper facts at the title readable, inferable from text descriptive s. 16 ~ same title, other question · copy ceiling: L4 cosine 0.998 exploratory s. 77 ~ paraphrased title text-only model reaches 60% pre-registered s. 71 ✗ made-up title meaning 75%; real title +0.106 locked s. 73 ✗ rare vs common words 0.162 vs 0.027 locked s. 80 ✗ recognised / citation check not larger; smaller if cited more locked s. 78 ✗ variance split identity ≈ 0 locked s. 79 ✗ "paper facts" subspace swap R_id 0.004 pre-registered s. 101 (✓) L8 surname test T1 +0.046; T2/T3 marginal; ½ topic locked s. 81 Verdict: not a general paper identity, with one small locked exception → s. 82 Writing step (the bottleneck) tested in Part 6 ✓ supports (✓) partly ✗ weakens ~ cannot separate strength: settled locked pre-registered descriptive exploratory s. = slide So (section): H1 and H2 rows filled: question read, format layer open; meaning and specific words, not identity (one small locked exception). Next: the route and H3.

数字出处：27_v67/fragments/part34_numbers.md

# Part 5 · Where it goes and how it is held (route + H3) (88–113)

## P88 · HTML v75 p88 · pptx S92 (v22z) — Question card: route and H3

**要说的话（一句英文一句中文）**
This question card opens Part 5: after the title is read, how does its information reach the name positions, and in what form is it held there?
这张问题卡开启第 5 部分：标题读完之后，它的信息怎么到达名字位置，在那里以什么形式存着？
The hypothesis is that the information travels from the title to the names over attention, and is held there in a form the lens, the tool that reads a hidden state as words, cannot see.
假设是：信息经由注意力从标题走到名字，存在那里的形式是 lens——把隐藏状态读成词的工具——看不到的。
If it holds, a probe on the name tokens should beat the lens on the same scale, cutting the route should remove signal, and handing the late layers the probe's author direction should make them write this author.
如果成立，名字 token 上的 probe 应该在同一尺度上胜过 lens，切断路线应该减少信号，把 probe 的作者方向交给后面的层应该能让它们写出这个作者。
If it fails, probe and lens see the same, no route matters, and the direction does nothing or writes any author it points to.
如果不成立，probe 和 lens 看到的一样，哪条路线都不重要，那个方向要么没用，要么指向谁就写谁。
First a short background block on the readouts, then the decisive tests.
先简单看读出工具的背景块，再看决定性检验。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Question card: route and H3 Now asking: after the title is read, how does its information reach the author name positions, and in what form is it held there? Hypothesis (H3 + route) The paper’s information travels from the title to the name positions over attention, and the author information is held there in a form the vocabulary readouts (lenses) cannot see . If it holds, we expect ① a probe on the name tokens beats the lens on the same scale ; ② cutting the title → name route removes signal; ③ handing the late layers the probe’s author direction makes them write this author. If it fails, we expect ① probe ≈ lens on the same tokens; ② no edge or layer matters; ③ the direction does nothing, or writes any author it points to. Tests in this part Route: where the paper information travels (slide 94) → which positions carry it (slide 95) → which attention edge, 4-layer windows (slide 96) → MLP lookup at L52–L56 (slide 97) → single layers (slide 104). Readouts: lenses over layers (slides 86–93) → probe on every name token (slide 98) → probe vs lens on the same scale (slide 99) → directions of the difference (slide 100) → swapping a small subspace (slide 101) → readout map (slide 102). Use: injecting the author direction vs more title signal (slide 105) → why pushing hurts (slide 106). → So (section): Part 4 showed the title is read for its meaning and specific words; this part follows that information to the name positions and asks how it is held.

数字出处：27_v67/fragments/part56_numbers.md

## P89 · HTML v75 p89 · pptx S93 (v22z) — Background: how we got here (small samples) · Part 5

**要说的话（一句英文一句中文）**
This divider marks the background block for Part 5: what the earlier samples suggested about the readouts.
这张分隔页标出第 5 部分的背景块：早期样本对读出工具有什么提示。
They suggested that lenses read names only late and add little, while a probe at the title reads a little paper-specific signal early.
它们提示：lens 只在后期才读出名字，而且增益很小；标题处的 probe 早期就能读出一点论文特有的信号。
These pages can be skipped in the talk; the decisive tests start with the route.
汇报时这几页可以跳过；决定性检验从路线开始。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Part 5 · background Background: how we got here (small samples) Now asking: what did the earlier, smaller samples suggest before the decisive tests? In this block: slides 86–93 86 What can each readout see? 87 Two lenses: Public-557 vs Self-100 88 Cross-stage audit: does J-Lens add value? 89 Stage 9: is the lens stable across fitting data? 90 Names become readable late 91 Which lens reads best? 92 Do lenses reveal hidden paper knowledge? 93 Read early: a probe finds it at the title What they suggested: lenses read names only late and add little; a probe at the title reads a little paper-specific signal early Caveat: small samples; single papers or pairs can drive a result Decisive tests: start at slide 94 So (section): these pages set up the question; the decisive tests of this part start at slide 94. descriptive

## P90 · HTML v75 p90 · pptx S94 (v22z) — What can each readout see?

**要说的话（一句英文一句中文）**
This page opens the readout question: which readout can see the author signal, and how early?
这一页提出读出的问题：哪种读出工具能看到作者信号，能多早看到？
The small samples asked whether the Jacobian lens beats the plain logit lens, and whether a fitted lens is stable.
小样本问的是：Jacobian lens 是否胜过普通的 logit lens，拟合出来的 lens 是否稳定。
The full cohort answered: lenses read the shape of names earlier, but not which paper it is; a probe at the title reads paper-specific information.
全队列的回答是：lens 能更早读出名字的形状，但读不出是哪篇论文；标题处的 probe 能读出论文特有的信息。
The next pages show the steps.
接下来几页展开这些步骤。

**备查（不念）· 上一版讲稿本页全文（原第 P34 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** B 线的问题。小样本问的是：J-Lens 比 Vanilla 好吗？拟合出来的 lens 稳定吗？全队列的回答是：lens 能更早读出名字的形状，但读不出论文身份；在标题 token 上训练的 probe 能读出论文特异的信息。另附补充 18b 第 1 项（探索性）：名字出现之前，按提示位置 × 层画出的读出图 → 第 72 页。

**过渡：** 先看 Stage 3 的两种 lens。

**备查（不念）：**
- 方框原写 “+ addendum 18b item 1”：读出地图 = 补充登记 18b 第 1 项（探索性）

## P91 · HTML v75 p91 · pptx S95 (v22z) — Two lenses: Public-557 vs Self-100

**要说的话（一句英文一句中文）**
This page asks whether a middle layer can approximate the model's final next-token distribution, and whether that helps with authors.
这一页问：中间层能不能近似模型最后的下一个 token 分布，这对作者有没有帮助？
We compared two fitted lenses and the plain logit lens on 20 general and 20 paper prompts.
我们在 20 个通用提示和 20 个论文提示上，比较两种拟合的 lens 和普通 logit lens。
On the chart, a lower KL means the readout is closer to the final distribution; the self-fitted lens is closer on most layers.
图上 KL 越低表示读出越接近最后的分布；自己拟合的 lens 在大多数层上更接近。
But closer distributions did not mean better author ranks: on the author pilot both lenses won 14 of 20 at layer 48.
但分布更接近并不等于作者排得更好：在作者小样本上，两种 lens 在第 48 层都是 20 篇中赢 14 篇。
So fidelity is not the task. Next, whether the Jacobian lens adds any title-specific value.
所以保真度不等于任务本身。下一页看 Jacobian lens 有没有带来额外的标题特有价值。

**备查（不念）· 上一版讲稿本页全文（原第 P35 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 问题：中间层能不能近似出最终的下一个 token 分布？用 20 个通用提示和 20 个论文提示，计算 KL(final ‖ readout)（越低越好），比较 Public-557 和 Self-100 两种 lens 以及 Vanilla，再在作者 pilot 上比较全名胜出次数。

**关键数字和 CI：**
- 两个 checkpoint 数值都有效（63/63 和 6/6 为有限值）。
- Self-100 在 6/6 个通用层和 5/6 个论文层上 KL 更低（论文 L32：11.1 → 7.2）。
- 但在论文 L62，Self-100 的 KL 好于 Vanilla（0.58 vs 0.81），Top-10 重合却更差（0.36 vs 0.72）。
- 作者 pilot：L48 两种 lens 都是 14/20 全名胜出（20 篇）。
- n = 20 个通用 + 20 个论文提示 · 作者 pilot 20 篇。

**结论状态：** 探索性。教训：分布匹配得更好，不等于作者排得更好，保真度不能代替任务本身。

**过渡：** 那么 J-Lens 在标题效应上到底有没有增益？下一页做跨 Stage 审计。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{KL}(\mathrm{final}\,\|\,\mathrm{readout})\ \mathrm{per\ layer}$；② n = 20 generic + 20 paper prompts · author pilot 20 papers；③ KL lower: the lens reads closer to the final output；原公式框：KL(final ‖ readout) per layer n = 20 generic + 20 paper prompts · author pilot 20 papers。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(matrices.csv; frobenius_norms.csv)
- 出处（原在幻灯片上）：(20 + 20 prompts; metrics.csv)
- 出处（原在幻灯片上）：(metrics.csv)
- 出处（原在幻灯片上）：(20 papers, layer_summary.csv)

## P92 · HTML v75 p92 · pptx S96 (v22z) — Cross-stage audit: does J-Lens add value?

**要说的话（一句英文一句中文）**
This page asks whether the Jacobian lens adds any title-specific value over the plain logit lens.
这一页问：Jacobian lens 相对普通 logit lens，有没有带来额外的标题特有价值？
We joined the earlier stages and bootstrapped the difference 20 thousand times.
我们把前几个阶段的结果合起来，对差值做了 2 万次 bootstrap。
On the chart, a value above zero means the Jacobian lens adds title advantage; it is about plus 0.002, with an interval around zero, and only 24 of 50 papers positive.
图上大于 0 表示 Jacobian lens 带来更多标题优势；结果约 +0.002，区间在 0 附近，50 篇里只有 24 篇为正。
Dropping a single paper can flip its sign.
去掉一篇论文就可能让符号翻转。
So in the pilot the Jacobian lens added nothing. Next, whether the lens is stable across fitting data.
所以在小样本里 Jacobian lens 没有带来增益。下一页看 lens 在不同拟合数据上是否稳定。

**备查（不念）· 上一版讲稿本页全文（原第 P36 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 只读地合并 Stage 5–7.3 的结果，做 20,000 次 bootstrap；比较 J-Lens 减 Vanilla 的标题优势，并给出留一法范围。

**关键数字和 CI：**
- Stage 5 vs 7.3（L56）：r = 0.45，ρ = 0.47；符号一致 32/50（50 篇）。
- J-Lens − Vanilla：+0.002 [−0.008, +0.012]；中位数 −0.002；24/50 为正。
- 这个增量的 A−B：−0.014 [−0.033, +0.004]（20 对）。
- n = 50 篇 · 20 个 A/B 对 · 20,000 次 bootstrap。

**结论状态：** 探索性（幻灯片原话：到此为止都是探索性，因为 L56 被反复查看过）。去掉一篇论文就可能翻转 J-Lens 增量的符号；pilot 中 J-Lens 没有带来额外的 title-specific 价值。

**过渡：** 另一个问题是 lens 本身稳不稳定：换一批拟合数据会不会变？这是 Stage 9 要回答的。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\Delta=\mathrm{adv}(\mathrm{J\text{-}Lens})-\mathrm{adv}(\mathrm{Vanilla})$；② n = 50 papers · 20 A/B pairs · 20,000 draws；③ Δ > 0: J-Lens adds over the plain lens；原公式框：Δ = adv(J-Lens) − adv(Vanilla) n = 50 papers · 20 A/B pairs · 20,000 bootstrap draws。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(50 papers, cross_stage_correlations.csv)
- 出处（原在幻灯片上）：(jlens_increment_bootstrap.csv)

## P93 · HTML v75 p93 · pptx S97 (v22z) — Stage 9: is the lens stable across fitting data?

**要说的话（一句英文一句中文）**
This page asks whether the fitted lens is stable when fitted on different data.
这一页问：用不同的数据拟合，lens 稳不稳定？
The plan was two disjoint sets of a hundred prompts each, plus a separate holdout.
计划是用两组互不重叠、各 100 个的提示，再加一组独立的留出数据。
Each prompt takes about five minutes of Jacobian computation, so only the first fit was completed; the second fit and the holdout were not run.
每个提示要大约 5 分钟的 Jacobian 计算，所以只完成了第一组拟合，第二组和留出数据都没有跑。
So the lens's stability is still untested, and the full cohort used that first fit as one of its lenses.
所以 lens 的稳定性仍未检验，全队列把那第一组拟合当作其中一种 lens 来用。
Next, when names become readable with a lens.
下一页看名字什么时候能被 lens 读出。

**备查（不念）· 上一版讲稿本页全文（原第 P37 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 新的 FullFit 协议，和历史上的 50+50 split-half 不同：用两组互不重叠的 100 个提示（WikiText-103 train，100–1,200 字符，按 hash 去重，种子 3519001），在独立的 100 个 WikiText 上做 holdout，7 层（增加了 L16）。

**关键数字和 CI：**
- 每个提示约 324 秒 Jacobian 时间、约 62 GiB CPU 内存；每个提示单独存 checkpoint。
- 存档进度：写作时 Fit A 4/100，Fit B 0/100（351_stage9 checkpoints）。
- 只有 Fit A 完成，Stage 10 把它当作 "fitA" 使用；Fit B 和 holdout 没有跑。
- n = 计划 100 + 100 个 WikiText 提示（完成 Fit A 4、Fit B 0）。

**结论状态：** 描述性（未完成）：没有 Fit B 和 holdout，拟合稳定性尚未检验。

**过渡：** 进入全队列的逐层读出，先用方法图走一遍。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $J_l=\mathbb{E}_x[\partial h_{63}/\partial h_l]$；② n = 100 + 100 WikiText prompts planned (Fit A 4, Fit B 0 done)；③ J(fit A) ≈ J(fit B): the lens is stable across fitting data (Fit B not run yet)；原公式框：J l = E x [∂h 63 / ∂h l ] n = 100 + 100 WikiText prompts planned (Fit A 4, Fit B 0 done)。

**备查（不念）：**
- 出处原写 “(351_stage9 checkpoints)”（图注）与 “(full_A.log; benchmark log)”（正文）

## P94 · HTML v75 p94 · pptx S98 (v22z) — Names become readable late

**要说的话（一句英文一句中文）**
This page asks when names become readable with a lens.
这一页问：名字什么时候能被 lens 读出来？
On all 9,108 papers with the true title, we read the true name token with each lens at each layer.
在全部 9,108 篇真标题论文上，我们用每种 lens 逐层读真名字 token。
On the chart, zero means the true name is ranked first and minus two means one hundredth; the logit lens is near rank ten thousand until layer 48.
图上 0 表示真名字排第一，−2 表示排第一百；logit lens 到第 48 层为止都在一万名左右。
The Jacobian lenses read more from layer 40, and every readout jumps at layer 62, to about rank ten.
Jacobian lens 从第 40 层起读得多一些，所有读出方式都在第 62 层跳升，到第十名左右。
So names are readable only late. Next, which lens reads best, and where.
所以名字要到很后面才读得出来。下一页看哪种 lens 读得最好、在哪里最好。

**备查（不念）· 上一版讲稿本页全文（原第 P39 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 全部 9,108 篇，真标题，比较 fitA、public、self100 三种 Jacobian lens 和 logit lens 读出的真名字 token 的 log10(1/rank) 随层的变化。

**关键数字和 CI：**
- logit lens：L48 之前几乎读不出（约排名 10,000+）。
- Jacobian lens：从 L40 起读出更多。
- 所有读出方式都在 L62 跳升（排名约 10；Stage 10，logit L62 −0.93，§6.1）。
- n = 9,108 篇（真标题）。

**结论状态：** 定论（描述性的逐层曲线，全队列）。

**过渡：** 哪种 lens 读得最好？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{nlr}=\log_{10}(1/\mathrm{rank})$；② n = 9,108 papers (true title)；③ nlr = 0: true name ranked first; −2: ranked 100th；原公式框：nlr = log 10 (1/rank of the true name token) n = 9,108 papers (true title)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10 cohort, §6.1)” → “(Stage 10 cohort)”；“(Stage 10, logit L62 -0.93, §6.1)” → “(Stage 10, logit L62 -0.93)”

## P95 · HTML v75 p95 · pptx S99 (v22z) — Which lens reads best?

**要说的话（一句英文一句中文）**
This page asks which lens reads names best, and at which layers.
这一页问：哪种 lens 读名字最好，在哪几层？
We compare four readouts on all papers, with the rank and with the share of papers where the true name reaches the top ten.
我们在全部论文上比较四种读出方式，看排名，也看真名字进入前十的论文比例。
On the chart, a top-ten share of 0.5 means the true name is in the top ten for half of the papers; at layer 48 the Jacobian lenses reach 15 to 18%, the logit lens only 1%.
图上前十比例 0.5 表示一半的论文里真名字在前十；第 48 层 Jacobian lens 达到 15% 到 18%，logit lens 只有 1%。
At layer 62 the plain logit lens is best, at 59%.
到第 62 层，普通 logit lens 最好，是 59%。
So Jacobian lenses help in the middle layers, but only with the shape of names. Next, whether lenses reveal hidden paper knowledge.
所以 Jacobian lens 在中间层有帮助，但只是帮助读出名字的形状。下一页看 lens 能不能揭示隐藏的论文知识。

**备查（不念）· 上一版讲稿本页全文（原第 P40 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 全部论文、真标题，两个指标：读出水平（log10(1/rank)）和金标 token 进入 top-10 的比例，比较四种读出方式。

**关键数字和 CI：**
- 中间层：fitA 最好；L48 时 Jacobian lens 的 top-10 比例为 15–18%，logit lens 为 1%（Stage 10 X3，9,108 篇，§6.9）。
- L62：logit lens 最好（59%）。
- n = 9,108 篇（真标题）。

**结论状态：** 定论（描述性）。

**过渡：** Jacobian lens 在中间层能读出更多，但读出来的东西是论文知识吗？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{nlr}=\log_{10}(1/\mathrm{rank})$ · $\mathrm{top\text{-}10\ share}=P(\mathrm{rank}\leq 10)$；② n = 9,108 papers (true title)；③ nlr = 0: true name ranked first; −2: ranked 100th / top-10 share = 0.5: the true name is in the top 10 for half of the papers；原公式框：nlr = log 10 (1/rank); top-10 share = P(rank ≤ 10) n = 9,108 papers (true title)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10 X3, 9,108 papers, §6.9)” → “(Stage 10 lens comparison, 9,108 papers)”

## P96 · HTML v75 p96 · pptx S100 (v22z) — Do lenses reveal hidden paper knowledge?

**要说的话（一句英文一句中文）**
This page asks whether the lenses reveal hidden knowledge about the paper.
这一页问：lens 能不能揭示出关于论文的隐藏知识？
We take what a lens reads beyond the logit lens, for the paper-specific signal, and compare recognised with unrecognised papers.
我们取 lens 比 logit lens 多读出的论文特有信号，再比较认得和认不得的论文。
On the chart, extra above zero means the lens reads more than the logit lens; it is only about 0.01 to 0.03 in the middle layers, against about 0.44 at layer 62.
图上 extra 大于 0 表示 lens 读得比 logit lens 多；中间层只有约 0.01 到 0.03，而第 62 层约是 0.44。
And it is not larger for recognised papers.
而且对认得的论文并不更大。
So lenses add no hidden paper knowledge. Next, where a probe finds it.
所以 lens 没有带来隐藏的论文知识。下一页看 probe 在哪里找到它。

**备查（不念）· 上一版讲稿本页全文（原第 P41 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 配对差：extra = spec_lens − spec_logit lens，即 lens 比 logit lens 多读出的 title-specific 信号；左图看全部论文的 extra，右图看这个 extra 的 target − control。

**关键数字和 CI：**
- 额外信号：+0.01 到 +0.03（Stage 10 X3，L24–L48，9,108 篇，§6.9），而 L62 约 0.44。
- 对 target 并不更大（L48–56 甚至为负）。
- n = 9,108 篇（4,621 target + 2,220 control）。

**结论状态：** 定论（第 64 页"J-Lens over Vanilla：更多名字形状，没有论文身份，consistent"）。

**过渡：** lens 读不到，那训练出来的 probe 能不能在更早的位置读到？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{extra}=\mathrm{spec}_{\mathrm{lens}}-\mathrm{spec}_{\mathrm{logit\ lens}}$ · $T-C\ \mathrm{of\ the\ extra}$；② n = 9,108 papers (4,621 target + 2,220 control)；③ extra > 0: the lens reads more than the logit lens；原公式框：extra = spec lens − spec logit lens ; T − C of the extra n = 9,108 papers (4,621 target + 2,220 control)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10 X3, L24-L48, 9,108 papers, §6.9)” → “(Stage 10 lens comparison, L24-L48, 9,108 papers)”

## P97 · HTML v75 p97 · pptx S101 (v22z) — Read early: a probe finds it at the title

**要说的话（一句英文一句中文）**
This page asks where a probe finds the paper-specific signal.
这一页问：probe 在哪里找到论文特有的信号？
We compare the lenses and a trained probe at the last title token.
我们在最后一个标题 token 处比较 lens 和训练出来的 probe。
On the chart, target minus control above zero means recognised papers' authors read better; the lenses give about 0.01 to 0.03, the probe about 0.05 rising to 0.08.
图上 target 减 control 大于 0 表示认得的论文作者读得更好；lens 约 0.01 到 0.03，probe 约 0.05，升到 0.08。
So a probe finds a little at the title early, while lenses see it only late.
所以 probe 在标题处早早找到一点信号，而 lens 要到很后面才看到。
That closes the background. Next, the decisive tests, starting with where the paper information travels.
背景块到此结束。下面是决定性检验，先看论文信息走向哪里。

**备查（不念）· 上一版讲稿本页全文（原第 P42 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 在最后一个标题 token 处看 title-specific 信号。左图：logit lens 和 public J-lens 分 target/control（9,108 篇）；右图：线性 probe（复核版：团队分折、去掉标题复用；target n=896、control n=499）。

**关键数字和 CI：**
- lens：约 0.01–0.03（Stage 11 E4，4,621 + 2,220，§6.11）。
- probe：0.05 → 0.08（Stage 13 E4b，只打第一个名字 token）。
- target 高于 control +0.03–0.08（E4b，896 vs 499，档内）。
- n = 9,108 篇（lens）· 1,395 篇（probe：896 target + 499 control）；图中 probe 篇数也已改为 1,395，与 n 行一致（已按作图来源核对：右图只画 target、control 两条曲线，图例 n=896、n=499；0.05 → 0.08 是这 1,395 篇的平均 0.0508 → 0.0755）。第 27 页写 1,863 篇不矛盾：那是 X1 对照流程里去掉标题复用后的全部论文（含 433 excluded、35 guard），平均 0.0505 → 0.0801。

**结论状态：** 初步（较稳但有前提：只打第一个 token、只减 false_0）。一句话：读得早（标题处，从 L24 起），说得晚（名字处，L57–61）。

**过渡：** 汇总 B 线。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{nlr}_{\mathrm{false}_0}$ · $T-C\ \mathrm{within\ bin}$；② n = 9,108 papers (lenses) · 1,395 papers (probe: 896 target + 499 control)；③ T − C > 0: recognised papers’ authors read better than control；原公式框：spec = nlr true − nlr false_0 ; T − C within bin n = 9,108 papers (lenses) · 1,395 papers (probe: 896 target + 499 control)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 11 E4; Stage 13 E4b)” → “(Stage 11 title-position probe; Stage 13 re-check)”；“(Stage 11 E4, 4,621 + 2,220, §6.11)” → “(Stage 11, 4,621 + 2,220)”；“(Stage 13 E4b, 1,863 papers, first name token only)” → “(Stage 13 re-checked probe, 1,395 papers, first name token only)”；“(E4b, 896 vs 499, within bin)” → “(re-checked probe, 896 vs 499, within bin)”；“(addendum 9, done): surname first token L40 +0.071 [0.058, 0.085] (1,395 papers; e4b_alltok.md).” → “(every-name-token check, done): surname first token L40 +0.071 [0.058, 0.085] (1,395 papers).”；“title reuse removed: 1,863 papers (896 target, 499 control)” → “title reuse removed: 1,395 papers (896 target, 499 control)”
- 图片重新生成：子标题与便签里的 1,863 已改成 1,395（896 + 499，2026-11-19 已定的更正），原来盖在图上的两个 “1,395” 补丁随之去掉

## P98 · HTML v75 p98 · pptx S102–S103 (v22z) — Stage 12: where the paper information travels

**要说的话（一句英文一句中文）**
This page asks where the paper information travels after the title, and which part of the model writes the name.
这一页问：论文信息在标题之后走向哪里，模型的哪一部分写出名字？
We copy groups of positions, or single components of one layer, from the true-title run into the false-title run, averaged over five false titles.
我们把一组位置，或者某一层的单个组件，从真标题运行复制到假标题运行，在 5 个假标题上平均。
On the chart, recovery near 1 means the copied part carries all of the true-title advantage; all positions after the title give about 0.82 at layer 48 and almost 1 at layer 52, the names alone about 0.84, and the colon at most 0.18.
图上恢复接近 1 表示复制的部分带着全部真标题优势；标题之后的全部位置在第 48 层约 0.82、第 52 层接近 1，只有名字位置约 0.84，冒号最多 0.18。
For single components, attention peaks at layer 48 and the MLP rises later.
按单个组件看，注意力在第 48 层达到峰值，MLP 在更后面上升。
So the information goes mainly to the name positions. Next, which position group carries it, layer by layer.
所以信息主要送到名字位置。下一页逐层看是哪一组位置在承载。

**备查（不念）· 上一版讲稿本页全文（原第 P73 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** P1 / P2 用 5 个假标题（补充 10 第 3 项），看在输出层恢复了真−假差距的多少，1,186 篇，团队整群 95% CI。P1：在第 l 层 patch 一组位置（标题后所有位置 / 只有名字位置 / 只有 ':'）；P2：只 patch 某一层的某一个组件（attention 或 MLP）。recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄]，取 5 个假标题均值（细虚线 = false_0）。另附 N1、N2、F2 三项。

**关键数字和 CI：**
- P1 标题后所有位置：L40 0.302 [0.290, 0.314]；L48 0.821 [0.807, 0.835]；L52 0.995 [0.990, 1.001]。
- P1 只有名字位置：L48 0.613 [0.599, 0.630]；L52 0.841 [0.827, 0.856]；L56 0.877 [0.864, 0.891]。
- P1 只有 ':'：L52 0.181 [0.168, 0.193]（最高）。
- P2 attention：L48 0.237 [0.229, 0.246]（false_0 0.231）；MLP：L52 0.181 [0.174, 0.188]（0.178），L56 0.226 [0.217, 0.236]（0.224）。
- N1 名字合理性：没有标题时，真名单在 0.255 的论文里看起来"最像真的"（机会 0.25）；有真标题时 0.625 [0.615, 0.635]（8,894 篇 R0/R1）。
- N2 纯名字先验：target − control +0.047 [0.031, 0.062]，有真标题时为 +0.247 → 约占差距的 19%（§6.12 的删除标题先验为 0.35）。
- F2 用作者提示拟合的 lens：target − control 在 L24–L56 ≤ 0，只在 L62 达到 +0.238。
- n = 1,186 篇（P1/P2）。

页尾引向更细的两页：逐层看是哪组位置（第 74 页）、哪条注意力边（第 75 页）在承载。

**结论状态：** 初步（较稳但有前提：规则事先固定，5 个假标题与 false_0 一致；单层 patching 只给出下界）；N1/N2/F2 为描述性。

**过渡：** 先细到位置：一次只换一组位置，看标题到底装在哪组位置上（补充 18b 第 3 项）。

**图旁公式（灰色行）：** recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄],  mean of 5 false titles · n = 1,186 papers (593 + 593)

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{recovery}(l)=\frac{\mathrm{mean}_p[\bar P(l)-\bar F]}{\mathrm{mean}_p[\bar T-\bar F]}$；② n = 1,186 papers (593 + 593), mean of 5 false titles；③ recovery ≈ 1: the copied positions carry all of it；原 “How computed” 段：How computed: recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄]; P1 = a set of positions, P2 = one component in one layer; mean of 5 false titles (thin dashed = false_0). 1,186 papers, team-cluster 95% CI.；原公式框：recovery(l) = mean_p[P̄(l) − F̄] / mean_p[T̄ − F̄], mean of 5 false titles n = 1,186 papers (593 + 593)；原出处行：N1 name plausibility: Stage 12 N1, 8,894 R0/R1 papers, paper bootstrap; N1_prior_mc.csv · N2 pure name prior: Stage 12 N2, final L63, 4,621 + 2,220, within bin, paper bootstrap; stage12_report.md · F2 lens fitted on author prompts: Stage 12 F2, name positions, Stage 11 sample, true − 5 false; F2_author_lens.csv；原出处行：391_groups/summary_b1_p12f/p12f_mean5.csv · b1_p12f_report.md · Stage 12 N1 / N2 / F2 reports；方法细节移到备用页 B16 (slide 111)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："(pre-registered extension)" ← "(addendum 10, item 3)"

**备查（不念）：**
- 原写 “P1 / P2”、“P1 · … / P2 · …”、“Result (P1) / (P2)”：P1 = 位置 patching，P2 = 分量（注意力 / MLP）patching

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 细虚线 = false_0。

## P99 · HTML v75 p99 · pptx S104 (v22z) — By L52 the name positions carry most of the title’s signal

**要说的话（一句英文一句中文）**
This page asks which positions carry the title's signal, layer by layer.
这一页问：逐层看，是哪些位置在承载标题的信号？
We copy one group of positions at a time from the true-title run into the false-title run.
我们每次只把一组位置从真标题运行复制到假标题运行。
On the chart, recovery near 1 means that group carries all of it; the name positions go from about 0.31 at layer 47 to about 0.6 at layer 48 and about 0.84 at layer 52.
图上恢复接近 1 表示这一组带着全部信号；名字位置从第 47 层的约 0.31，到第 48 层的约 0.6，再到第 52 层的约 0.84。
The colon joins late and carries much less, and the other positions carry almost nothing.
冒号加入得晚，带的也少得多，其他位置几乎什么都不带。
So the title enters the name positions mainly in one step, from layer 47 to 48. Next, which attention edge carries it.
所以标题主要是在第 47 到 48 层这一步进入名字位置的。下一页看是哪条注意力边在承载。

**备查（不念）· 上一版讲稿本页全文（原第 P74 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 18b 第 3 项（设计于 2026-11-17 锁定，没有判定规则 → 描述性）：每次只把一组位置（名字位置、整个尾部、':'、年份十位数字、标题后引号、其余尾部）在某一层的状态从真标题复制到假标题运行（true → false），看输出恢复了多少；5 个假标题；6 组 × 15 层；600 篇（300 target + 300 control；引号组 363 篇），配对团队 bootstrap 2,000 次。R(g, l) = mean_p[nlr_patch(g, l) − nlr_false] / mean_p[nlr_true − nlr_false]（Stage 12 P1 的估计量，先取论文均值），再取 5 个假标题比值的均值。

**关键数字和 CI：**
- 名字位置承载大部分：L40 0.176 [0.165, 0.187] → L47 0.314 [0.297, 0.333] → L48 0.605 [0.584, 0.627] → L52 0.835 [0.816, 0.854]；L56 0.876 [0.855, 0.894]。
- ':' 晚加入：L48 0.073 [0.066, 0.082] → L52 0.177 [0.161, 0.194]；L56 0.131。
- 年份十位数字：L46–L47 最高 0.081 [0.073, 0.090]，到 L56 约 0（−0.001）。
- 引号和其余尾部 ≤ 0.026。
- 整个尾部：L48 0.804 [0.784, 0.825]，L52 0.988 [0.980, 0.996]（已存曲线 0.821 / 0.995 保留）。
- target − control：整个尾部在 L40–L50 为 −0.076 到 −0.093（L52 −0.024）；名字位置只从 L56 起 > 0（+0.051）。
- 局限：没有判定规则；硬检查 WARN、按规则继续：与已存行的逐行名次一致率 0.72–0.81（要求 1.0，bf16 batch 形状）；1,186 篇均值 0.821137 vs 0.821056（容差 1e-6）。
- n = 600 篇（300 target + 300 control）· 引号 363 篇。

**结论状态：** 描述性（没有锁定判据）。标题主要在 L47 → L48 这一步进入名字位置，':' 晚到。

**过渡：** 名字位置在 L48 拿到标题；那是哪一条注意力边把它带过来的？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R_g(l)=\frac{\mathrm{mean}_p[\mathrm{nlr}(\mathrm{patched})-\mathrm{nlr}(\mathrm{false})]}{\mathrm{mean}_p[\mathrm{nlr}(\mathrm{true})-\mathrm{nlr}(\mathrm{false})]}$；② n = 600 papers (300 target + 300 control)；③ R ≈ 1: this position group carries all of it；原 “How computed” 段：How computed: R = mean_p[nlr(patched) − nlr(false)] / mean_p[nlr(true) − nlr(false)] for one position group g copied true → false at layer l (Stage 12 P1 estimand, paper means first), mean of the 5 false titles’ ratios; 6 groups × 15 layers. 600 papers, paired team bootstrap ×2,000.；原出处行：381_stage13/summary_a18b_item3/ (item3_mean5.csv, item3_hardchecks.json) · config/prereg_addendum18b.md；方法细节移到备用页 B17 (slide 112)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Per-position patching (design pre-registered …)" ← "Addendum 18b item 3 (design locked 2026-11-17 …)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 估计量：先按论文取平均，再取 5 个假标题比值的平均；6 组位置 × 15 层。

## P100 · HTML v75 p100 · pptx S105 (v22z) — Name ← title carries the arrival in L44–L55; each cut costs ≤ 3.5%

**要说的话（一句英文一句中文）**
This page asks which attention edge carries the title into the names.
这一页问：是哪条注意力边把标题带进名字？
We cut one edge, for all heads, inside a four-layer window, and see how much paper signal is lost, under a rule locked before the run.
我们在一个 4 层窗口内切断一条边（所有注意力头），看论文信号损失多少，规则在运行前锁定。
On the chart, a loss above zero means that edge in that window carries part of the signal; the name-from-title edge wins in the windows from layer 44 to 55.
图上损失大于 0 表示这条边在这个窗口里承载了一部分信号；名字看标题这条边在第 44 到 55 层的几个窗口里胜出。
But each cut costs at most about 3.5% of the signal, so no single edge is a bottleneck.
但每次切断最多只损失约 3.5% 的信号，所以没有哪一条边是瓶颈。
So the main route is name from title, and it is not the only one. Next, what the MLPs carry just before the name is written.
所以主要路线是名字看标题，但不是唯一的一条。下一页看名字写出之前，MLP 带的是什么。

**备查（不念）· 上一版讲稿本页全文（原第 P75 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 18b 第 2 项（2026-11-17 锁定）：在一个 4 层窗口内只切断一条注意力边（所有头），5 条边（名字 ← 标题、名字 ← 尾部、尾部 ← 标题、':' ← 标题、名字 ← ':'）× 6 个不重叠窗口（L40–43 … L60–63）。loss(e, w) = S(none) − S(边 e 在窗口 w 被切断)，S = mean_p nlr(true) − 5 个假标题均值（最终输出）。锁定规则：最大损失那条边 CI > 0，且与同窗口每条其他边的配对差 CI > 0。600 篇（300 target + 300 control），配对团队 bootstrap 2,000 次。稳健性：修正后的步长 2 检查，11 个重叠窗口。

**关键数字和 CI：**
- S(none) = 0.328。
- 锁定规则在 L44–47、L48–51、L52–55 成立，每次都是名字 ← 标题：+0.0063 [+0.0046, +0.0079]、+0.0112 [+0.0084, +0.0138]、+0.0071 [+0.0050, +0.0091]。
- 不成立：L40–43（名字 ← 标题 +0.0019 [+0.0007, +0.0031]，名字 ← 尾部同为 +0.0019）、L56–59、L60–63（损失约 0）。
- 稳健（修正后的步长 2）：11 个重叠窗口中 7 个（L42–L57）名字 ← 标题满足规则，包括上面 3 个；没有别的边胜出；最大损失 +0.0115 [+0.0088, +0.0142]（L48–51）= S(none) 的 3.5%。
- 局限：效应小（每条边、每个窗口 ≤ 3.5% 的 S）；第一次步长 2 运行无效、已被取代；未屏蔽名次与已存行一致率 0.63 / 0.51（WARN，bf16），按规则继续。
- n = 600 篇（300 target + 300 control）。

**结论状态：** 预注册判据成立（3 个窗口），对窗口位置稳健（效应小）。

**过渡：** 标题经名字 ← 标题这条边进入名字位置之后，L52–L56 的 MLP 这一步是不是"记忆查找"？补充 18b 第 6 项检验它写入的是不是作者名字方向。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{loss}=S(\mathrm{none})-S(\mathrm{blocked})$；② n = 600 papers (300 target + 300 control)；③ loss > 0: this edge carries the title；原 “How computed” 段：How computed: loss = S(none) − S(config), S = paper-mean nlr(true title) − mean of 5 false titles at the output; one edge (all heads) masked inside one 4-layer window; rule: the top edge’s CI > 0 and its paired difference to every other edge CI > 0. 600 papers, paired team bootstrap ×2,000.；原出处行：381_stage13/summary_a18b_item2/, summary_a18b_item2_step2_fix/ (item2_table.csv, item2_criterion.csv) · config/prereg_addendum18b.md；方法细节移到备用页 B17 (slide 112)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Single-edge blocking (pre-registered, locked)" ← "Addendum 18b item 2 (locked 2026-11-17)"
- 图内公式框里的判据 / 说明（移出幻灯片）：S = mean_p nlr(true) − mean of 5 false titles; rule: top edge CI &gt; 0 and paired CI &gt; 0 vs every other edge

## P101 · HTML v75 p101 · pptx S106 (v22z) — In L52–L56 the MLPs carry the paper, not yet the author’s name

**要说的话（一句英文一句中文）**
This page asks what the MLPs in layers 52 to 56 carry: the paper, or the author's name already?
这一页问：第 52 到 56 层的 MLP 带的是什么，是论文，还是已经是作者名字？
We replace the MLP output with the true-title version, either fully or only inside an author-aligned subspace, its complement, or a random subspace.
我们把 MLP 的输出换成真标题下的版本，要么整体换，要么只换作者对齐的子空间、它的补空间，或者一个随机子空间。
On the chart, recovery near 1 means that part carries all of it; the full MLP gives up to about 0.28, the author-aligned part only about 0.02 to 0.04.
图上恢复接近 1 表示这部分带着全部信号；整个 MLP 最高约 0.28，作者对齐的部分只有约 0.02 到 0.04。
So the MLPs here carry paper information, not a ready-made name direction; this is descriptive.
所以这里的 MLP 带的是论文信息，不是现成的名字方向；这是描述性结果。
Next, the probe on every name token.
下一页看每个名字 token 上的 probe。

**备查（不念）· 上一版讲稿本页全文（原第 P76 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** （接第 73–75 页：标题在 L48 已到名字位置。）补充 18b 第 6 项（设计于 2026-11-17 锁定，没有数值判据 → 描述性）：在整个对齐尾部把真标题 → 假标题的组件输出替换为 out_F + P(out_T − out_F)，P 分别取完整、作者对齐的 512 维子空间、正交补、随机 512 维；5 个假标题；600 篇（300 target + 300 control）；配对团队 bootstrap。R = mean_p[nlr_patched − nlr_false] / mean_p[nlr_true − nlr_false]。

**关键数字和 CI：**
- MLP 完整：L52 0.177 [0.168, 0.187] … L54 0.275 [0.262, 0.289]（峰值）… L56 0.223 [0.209, 0.237]；范围 0.158–0.275。
- MLP 正交补：L54 0.229 [0.217, 0.242]。
- attention 完整：0.055–0.146（L56 0.055 [0.049, 0.061]）。
- MLP 作者对齐方向：0.022–0.042；随机 512 维：0.014–0.023。
- 对齐 − 随机（配对）：+0.009 到 +0.019，CI 全部 > 0。
- MLP 完整的 target − control：L52 −0.056 [−0.079, −0.037]；L53 −0.039 [−0.060, −0.019]；L54 −0.059 [−0.093, −0.029]；L55 −0.006 [−0.038, +0.023]；L56 +0.011 [−0.023, +0.043]。
- 神经元：变化最大的前 50 个神经元，同一论文内的重合 0.27–0.30，不同论文之间 0.01–0.05（Jaccard）。
- 局限：control 论文在 L52–L54 恢复得稍多；作者子空间占名字行方差的 0.339；自检 WARN，排名一致率 0.538（bf16 batch 形状），按规则继续。
- n = 600 篇。

**结论状态：** 描述性（没有锁定判据）。MLP 携带的是论文信息，而不是现成的名字方向。

**过渡：** 那最后 L57–L61 的陡升是谁写的？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R=\frac{\mathrm{mean}_p[\mathrm{nlr}(\mathrm{patched})-\mathrm{nlr}(\mathrm{false})]}{\mathrm{mean}_p[\mathrm{nlr}(\mathrm{true})-\mathrm{nlr}(\mathrm{false})]}$；② n = 600 papers (300 target + 300 control)；③ R ≈ 1: this component carries all of it；原 “How computed” 段：How computed: R = mean_p[nlr(patched) − nlr(false)] / mean_p[nlr(true) − nlr(false)], 5 false titles; the layer-l MLP or attention output over the aligned tail is set to out_F + P(out_T − out_F). 600 papers, paired team bootstrap.；原出处行：381_stage13/summary_a18b_item6/ (item6_patch_mean5.csv, item6_contrasts.csv) · config/prereg_addendum18b.md；方法细节移到备用页 B17 (slide 112)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："MLP-content test (design pre-registered …)" ← "Addendum 18b item 6 (design locked 2026-11-17 …)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 替换作用在对齐后的标题之后各位置。

## P102 · HTML v75 p102 · pptx S107–S108 (v22z) — The probe on every name token

**要说的话（一句英文一句中文）**
This page asks how the probe does on every kind of name token.
这一页问：probe 在各种名字 token 上表现如何？
We probe the given name, the surname's first token and the initial separately, with permuted controls.
我们分别对名、姓的第一个 token、首字母做 probe，并配上打乱的对照。
On the chart, spec above zero means the true title ranks the author higher; the surname's first token reaches about 0.07, above the initial at about 0.04.
图上 spec 大于 0 表示真标题让作者排得更前；姓的第一个 token 约 0.07，高于首字母的约 0.04。
The permuted control is about zero for surnames and given names, but about 0.02 for initials, so half of the initial's signal is not paper-specific.
打乱的对照在姓和名上约为 0，在首字母上约 0.02，所以首字母的信号有一半不是论文特有的。
So the probe reads real paper-specific author information. Next, probe against lens on the same scale.
所以 probe 读到的是真正论文特有的作者信息。下一页在同一尺度上比较 probe 和 lens。

**备查（不念）· 上一版讲稿本页全文（原第 P89 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**关键数字和 CI：**
- 名的第一个 token：probe +0.124 [+0.108, +0.142]；随机论文 +0.007；同领域 +0.009（n 1,706）。
- 姓氏第一个 token：+0.071 [+0.058, +0.085]；对照 +0.003 / +0.004（n 1,395）。
- 首字母：+0.044 [+0.030, +0.057]；对照 +0.018 [+0.005, +0.031] / +0.020 [+0.008, +0.033]（n 1,590）。
- 姓氏第一个 token 高于首字母：差 +0.028 [+0.011, +0.045]。
- T − C 名：V0 +0.049 [+0.005, +0.095]；Vpd +0.048 [+0.021, +0.076]；V5x0 +0.047 [+0.012, +0.081]。
- T − C 姓氏：V0 +0.012 [−0.026, +0.048]；Vpd +0.030 [+0.013, +0.048]；V5x0 +0.024 [−0.006, +0.052]。
- T − C 首字母：V0 +0.031 [−0.001, +0.062]；Vpd +0.014 [−0.002, +0.030]；V5x0 +0.021 [−0.002, +0.043]。
- n = V0 1,395–1,706 篇，Vpd 3,046–4,812 篇。

**过渡：** 把 probe 移到"预测名字的那个位置"，并和 lens 在同一尺度上比较，这就是 H3 的检验。

**图旁公式（灰色行）：** spec = nlr(true) − nlr(false₀) per name token, ranked by role;  T − C within citation bins · n = V0 1,395–1,706 · Vpd 3,046–4,812 papers (L40)

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{nlr}_{\mathrm{false}_0}\ \mathrm{per\ name\ token}$ · $T-C\ \mathrm{within\ bin}$；② n = 1,395–1,706 (reuse-free) · 3,046–4,812 papers (per donor), L40；③ spec > 0: the true title ranks the author higher than false titles；原 “How computed” 段：How computed: spec = score(true title) − score(false_0) per name token, ranked by role → nlr; T − C pooled within citation bin. L40; V0 1,395–1,706 and Vpd 3,046–4,812 papers; team-cluster 95% CI.；原公式框：spec = nlr(true) − nlr(false₀) per name token, ranked by role; T − C within citation bins n = V0 1,395–1,706 · Vpd 3,046–4,812 papers (L40)；原出处行：381_stage13/summary_alltok/alltok_controls.csv · summary_e4b5/perdonor_by_run_layer.csv · e4b_alltok.md；方法细节移到备用页 B19 (slide 114)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Stage 13 · every name token" ← "Stage 13 · addendum 9"; "E4b" → "the title-position probe"

## P103 · HTML v75 p103 · pptx S109 (v22z) — Name-position probe: H3 supported on the same scale

**要说的话（一句英文一句中文）**
This page asks whether the author information at the names is held in a form the lens cannot read, H3.
这一页问：名字位置的作者信息，是不是以 lens 读不出的形式存着，这就是 H3。
We compare a probe and the lens on exactly the same 9,137 name tokens, on the same scale, with a rule locked before the run.
我们在完全相同的 9,137 个名字 token 上、用同一尺度比较 probe 和 lens，规则在运行前锁定。
On the chart, a probe above the lens means the probe separates recognised from unrecognised papers better; the difference is about 0.02 at layer 40 and about 0.06 at layer 48.
图上 probe 高于 lens 表示 probe 区分认得和认不得论文的能力更强；差值在第 40 层约 0.02，第 48 层约 0.06。
This passed the locked test, so H3 is supported on the same scale.
这一点通过了锁定检验，所以 H3 在同一尺度上得到支持。
So the information is there, but not in vocabulary directions. Next, which directions it moves.
所以信息在那里，只是不在词表方向上。下一页看它沿哪些方向变化。

**备查（不念）· 上一版讲稿本页全文（原第 P90 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**关键数字和 CI：**
- probe（9,137 个名字）：L32 +0.062；L40 +0.069 [+0.064, +0.074]；L48 +0.103 [+0.097, +0.110]；L52 +0.133；L56 +0.233。
- public J-lens（全词表）：L40 +0.048；L48 +0.030；L56 +0.270。logit lens：L40 +0.010；L48 +0.010；L56 +0.283。（排名尺度不同：9,137 个名字 vs 全词表，只比较符号和 CI，不比较大小。）
- probe target − control：L32 +0.030 [+0.018, +0.042]；L40 +0.031 [+0.019, +0.044]；L48 +0.053 [+0.038, +0.067]；L52 +0.073 [+0.057, +0.089]；L56 +0.127 [+0.107, +0.145]。
- 首字母（L40）：置换对照行 +0.020 [+0.015, +0.026]，约为信号 +0.045 [+0.039, +0.051] 的一半 → 这部分信号约一半不是论文特异的。
- n = 4,654 篇。

**结论状态：** 预注册判据成立：补充 11 判据通过（姓氏第一个 token，L40/L48）；之后发现 lens 的区间也不含 0，而尺度不同、无法比较大小，于是暂定为"部分支持"；补充 17 的锁定同尺度检验之后：同一尺度上得到支持。

**过渡：** 前面都是 teacher forcing。如果让模型自己写作者名单，probe 能不能区分真名字和编造的名字？

**图旁 n（灰色行）：** n = 4,654 papers (3,130 target + 1,524 control), surname first token

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{probe}(\mathrm{true})-\mathrm{probe}(\mathrm{false})$ · $T-C\ \mathrm{within\ bin}$；② n = 4,654 papers (3,130 target + 1,524 control)；③ T − C > 0 at the name position: author information is there；原 “How computed” 段：How computed: name-position probe = ridge from the layer-l residual at the name-predicting position to the model’s own L63 state, ranked among 9,137 name tokens; spec = probe(true) − probe(false); within-bin T − C. 4,654 papers, team CI.；原公式框：n = 4,654 papers (3,130 target + 1,524 control), surname first token；原出处行：381_stage13/summary_b2_np/ (np_lens_compare_v2.csv, np_role_layer_v2.csv) · reports/b2_np_report_v2.md；方法细节移到备用页 B19 (slide 114)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Name-position probe (pre-registered) · per-donor version Vpd" ← "Addendum 11 A · per-donor version Vpd (D11-1)"; addendum-11 / addendum-17 → "pre-registered criterion" / "locked same-scale test"
- 图内公式框里的判据 / 说明（移出幻灯片）：false = mean of the usable false titles (Vpd)

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** probe 是用 ridge 回归把第 l 层的残差流映射到模型自己最后一层（L63）的状态，再在 9,137 个名字 token 里排名，这样才能和 lens 放在同一尺度上比较。

## P104 · HTML v75 p104 · pptx S110 (v22z) — Recognition moves many quiet directions, not the author or attribute axes

**要说的话（一句英文一句中文）**
This page asks, as an exploratory check, along which directions recognised and unrecognised papers differ at the names.
这一页做一个探索性检查：在名字位置，认得和认不得的论文沿哪些方向不同？
We look at the per-paper differences between true and false titles, and compare their average with the probe's author directions and with attribute directions.
我们看每篇论文真标题和假标题之间的差，再把平均差和 probe 的作者方向、以及属性方向相比。
On the chart, the differences spread over many directions, but by layer 48 their average lines up, half of it on the first component.
图上这些差分散在很多方向上，但到第 48 层平均差聚拢了，有一半落在第一个主成分上。
It points only weakly along the author or attribute axes: together they cover about 6 to 7% of it.
它和作者轴、属性轴的方向只有很弱的重合：加起来只占约 6% 到 7%。
So recognition moves many quiet directions, not the obvious axes. Next, swapping only a small subspace.
所以认得改变的是很多“安静”的方向，而不是明显的那几根轴。下一页看只替换一个小子空间。

**备查（不念）· 上一版讲稿本页全文（原第 P91 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计（探索性，事后分析）：** 已存的名字位置状态（姓的第一个 token，用锁定 H3 检验的可用假标题规则），每篇 d = h(真标题) − 可用假标题 h 的平均，3,130 target + 1,524 control 篇，L40 和 L48。左：对 target 行减去 control 平均后做 PCA。右：平均差 Δ = target 平均 d − control 平均 d 与各方向的余弦——作者 probe 方向（已发表的名字位置 ridge 映射，重新拟合）和属性方向（年份、引用数、领域；在名字位置重新拟合的 ridge，已发表的属性 probe 读的是标题位置）。

**关键数字：**
- 逐篇差散在很多方向上：50% / 80% 方差需要 L40 31 / 234 个主成分，L48 25 / 151 个；单个主成分不超过 7%。
- 平均差 Δ 到 L48 聚拢：在第一主成分上 0.7%（L40）→ 50.0%（L48），前 10 个主成分里 59.9% → 80.8%。
- 和作者 probe 方向的余弦约 0.12–0.15（L48 真作者读出方向 −0.133；随机方向 ±0.014），年份 ≈ 0.01，引用数 0.06，领域 ≤ 0.08；17 个方向合起来只占 Δ 的 7.1%（L40）/ 6.1%（L48）。作者 probe 读出方向在前 10 个主成分里只有 2.4% / 1.4%（低方差方向）。

**图旁公式（灰色行）：** 左 y = λ_k / Σ_j λ_j（target 行 d − mean_C d 的特征值占比）；右 x = cos(Δ, v) = Δ·v / (‖Δ‖‖v‖)，v 为单位化的 probe 方向；Δ = d̄_T − d̄_C，d = h_true − h̄_false。n = 4,654 篇（3,130 + 1,524），姓的第一个 token。

**结论状态：** 探索性（事后）。读法：认得出和认不出的差别分布在很多“安静”的方向上，到 L48 才聚拢，不是沿作者或论文属性的轴。来源 381_stage13/summary_explore_pca_np_20261120/report.md；summary_explore_dir_overlap_20261121/report.md。

**过渡：** 再看模型自己写出的名字。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{share}_k=\frac{(\Delta\cdot u_k)^2}{\|\Delta\|^2},\ \ \Delta=\bar x_T-\bar x_C$；② n = 4,654 papers (3,130 target + 1,524 control), L40, L48；③ share high on few PCs: the difference has one direction；原 “How computed” 段：How computed: stored name-position states (surname first token, usable false titles as in the locked H3 test); PCA of the target rows minus the control mean; attribute directions = ridge refits of year, log citations and field on the true name-position states (the published attribute probes read the title position); author directions = the published name-position probe map, refitted · 381_stage13/summary_explore_pca_np_20261120/ · summary_explore_dir_overlap_20261121/；原灰色 n 行（已并入 LaTeX n 行）：n = 4,654 papers (3,130 target + 1,524 control) · surname first token · L40, L48；原出处行：381_stage13/summary_explore_pca_np_20261120/report.md · summary_explore_dir_overlap_20261121/report.md；方法细节移到备用页 B20 (slide 115)。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 用已存的名字位置状态（姓的第一个 token；可用的假标题与锁定的 H3 检验相同）。 属性方向 = 在真标题名字位置状态上重拟合年份、log 引用数、领域的岭回归；作者方向 = 已发表的名字位置 probe 映射，重拟合。

## P105 · HTML v75 p105 · pptx S111–S112 (v22z) — Swap only a subspace

**要说的话（一句英文一句中文）**
This page asks whether author information sits in a small subspace that we can swap on its own.
这一页问：作者信息是不是在一个小子空间里，可以单独替换？
We fit two small subspaces, one for paper identity and one for authors, and swap only that part of the state.
我们拟合两个小子空间，一个对应论文身份、一个对应作者，只替换状态里的这一部分。
On the chart, the moved share is how much of the effect the swap carries; the identity subspace moves about 0.004 against 0.93 for the full state, the author subspace about 0.03 against 0.46.
图上搬动比例是替换带过去的效应多少；身份子空间搬动约 0.004，而整个状态是 0.93；作者子空间约 0.03，而整个状态是 0.46。
By the locked rule H3 passes, but a subspace that hardly decodes authors is not strong evidence for it.
按锁定规则 H3 通过，但一个几乎解码不出作者的子空间，不能算 H3 的强证据。
So the information is spread out, not in one small subspace. Next, whether there is an earlier place where it is stored.
所以信息是分散的，不在一个小子空间里。下一页看有没有更早的存放位置。

**备查（不念）· 上一版讲稿本页全文（原第 P88 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**先讲怎么做（指着左边的方法图）：** 把 A 论文标题状态拆出一个小子空间分量：S_id（9 维，论文属性）或 S_auth（10 维，作者）；只把这个分量换进 B 论文的作者提示（第 l 层），给 A 的作者打分；对照是同样大小的随机子空间，以及全部维度的完整替换。子空间在 5,041 篇训练论文上拟合；S_auth 几乎解码不出作者（留出 R² ≤ 0.009）。

**再讲结果（指着右边的柱图：灰 = S_id，蓝 = S_auth，浅灰 = 随机；橙字 = 完整替换）：**
- S_id 在 L40 搬动 0.004（完整替换 0.932）；S_auth 在 L48 搬动 0.032（完整 0.457）。
- 预注册判定：H2 不成立；H3 通过（S_auth − S_id +0.030 [0.023, 0.036]）。
- 数字按全部作者、新版子空间（summary_b1_xall/x2_curves_new__all.csv）重新核对；旧页写的 S_auth +0.018、完整 0.428、R² ≤ 0.003 是第一作者旧版的数。
- 公式（灰字）：moved share = mean(patched − corrupt) / mean(clean − corrupt)；n = 582 测试对 · 子空间在 5,041 篇上拟合。

**So 行：** 按锁定规则 H3 通过，但一个解码不出作者的子空间只搬动完整替换的约 7% —— 从标题搬到名字的信息几乎都在这两个子空间之外。

**结论状态：** 预注册判据：H2 不成立；H3 通过，但不是 H3 的强证据。

**过渡：** 回到 probe：把所有作者、所有名字 token 都打分，按角色看。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{moved}=\frac{\mathrm{mean}(\mathrm{patched}-\mathrm{corrupt})}{\mathrm{mean}(\mathrm{clean}-\mathrm{corrupt})}$；② n = 582 test pairs · subspaces fitted on 5,041 papers；③ moved ≈ 0: the subspace alone carries little；原公式框：n = 582 test pairs · subspaces fitted on 5,041 papers。

## pptx S110（仅主 pptx，HTML deck 无对应页）— Subspace swap: does a small part of the state carry it?

**要说的话（一句英文一句中文）**
This page asks whether a small part of the state carries the paper or the authors.
这一页问：状态里的一小部分，是不是就承载了论文或作者？
Swapping only a small subspace moves very little compared with swapping the whole state; for the author subspace about 0.03 against about 0.46.
只替换一个小子空间，和替换整个状态相比搬动得很少；作者子空间约 0.03，整个状态约 0.46。
So the information is spread out, not held in one small subspace.
所以信息是分散的，不在一个小子空间里。

**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**
（主 pptx 当前页码：S108；HTML deck 无对应页。）

**【2026-11-22 v55】** 中文批注框 #4840 的 H3 判定句已按用户授权改为全部作者值：R_auth − R_id +0.030 [0.023, 0.036]（原第一作者值 +0.014 [0.008, 0.020]）。

**【v54，2026-11-22，用户授权修改：本页数字已改为全部作者版，按这一段讲】**
**先讲怎么做：** 把 A 论文标题状态在一个 9 维或 10 维子空间上的分量换进 B 论文的作者提示，读 B 的最终输出对 A 全部作者（全部名字 token）的分数；582 个测试对，子空间在另外 5,041 篇论文上拟合（5 折作者团队）。
**再讲结果（指着下方横条）：**
- S_id（论文属性，9 维）在 L40 搬动 +0.004 [0.001, 0.007]，和随机 10 维子空间 +0.002 [−0.001, 0.004] 差不多；完整替换 +0.932 [0.914, 0.950]。〔b1_xall_report.md，stratum all；summary_b1_xall/x2_curves_new__all.csv〕
- S_auth（按全部作者重拟合，10 维）在 L48 搬动 +0.032 [0.026, 0.039]，随机 +0.001 [−0.002, 0.003]，完整替换 +0.457 [0.430, 0.485]，约 7%；R_auth − R_id +0.030 [0.023, 0.036]。〔同上〕
- 但 S_auth 本身几乎解码不出作者：留出 R² 0.004–0.009（第一作者旧版 ≤ 0.0033、命中率 0.078–0.079 < 常数猜测 0.080）。〔fit_authall_sanity.csv；summary_x2/fit_sanity.csv〕
- 公式（灰字）：moved share = mean(patched − corrupt) / mean(clean − corrupt)；n = 582 测试对。
**So：** 只换 S_id 等于没搬 → 论文身份假设不支持；S_auth 搬得比随机多，但子空间无效 → 不算隐藏作者假设的证据。
**注意：** 页面外的中文批注框 #4840、#4847、#4848 已按用户授权（2026-11-22，主 pptx v22n–v22p）改为全部作者数字（0.932、0.457、0.032、0.004、约 7%、“A 的作者的分数”）；#4840 的 H3 判定句也已改为全部作者值 +0.030 [0.023, 0.036]（v22q）。

**（以下为 v53 及以前的讲稿，数字是第一作者旧版，仅存档）**

第 73 / 85 页 · v18 新增页（原生形状，2026-11-05） · 【新写讲稿】
〔…〕内为数字出处。

X2 只替换子空间（预注册补充 6，2026-11-05 完成）。在 B 的作者提示里只把标题位置状态在某个子空间上的分量换成 A 的：论文属性子空间 S_id（年份、引用数、领域，9 维）在 L40 只搬动 +0.005〔Stage 13 X2，测试集 582 对，R_S（均值比）；随机子空间 +0.003，完整替换 +0.920；381_stage13/reports/x2_report.md Verdict 表〕，作者子空间 S_auth 在 L48 搬动 +0.018〔同上，L48；随机 +0.003，完整替换 +0.428〕。按预注册判据，H3 通过、H2 不支持〔H2：R_id 0.005 < 0.5 × R_full 0.460；H3：R_auth − R_id +0.014 [+0.008, +0.020]，团队聚类 95% CI；同上〕。但作者子空间本身几乎解码不出作者（留出 R² ≤ 0.003〔S_auth 作者映射，5,041 篇训练论文，5 折团队留出 R² 0.0009–0.0033；x2_report.md Subspace fits 表〕，第一作者名字 token 猜中率 0.078–0.079〔同表 author top-1，L16–L48 各层〕，低于常数基线 0.080〔同表 majority〕），它搬动的量只有完整替换的约 4%〔0.018 ÷ 0.428〕，因此不能作为 H3 的有力证据。从标题传到作者名字的信息，几乎全部分散在这两个子空间之外。与预注册的出入：X2 的 H3 判定按规则通过，但因子空间本身无解码能力而降级，与 X3 的处理方式相同；S_id 只有 9 维。 2026-11-06（批次 1 第 1 项）：用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009），单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持）〔381_stage13/reports/b1_xall_report.md “X2: verdict” 与 “New S_auth” 节〕。
【页面精简后移入备注】子空间怎么来：每层用 ridge 拟合读出方向。S_id：年份、log 引用数、8 个领域，QR 正交化；8 个领域方向和为 0，所以是 9 维（计划 10 维，记录为偏离）。S_auth：从残差到第一作者名首 token 的 W_U 行的 ridge 映射，取残差一侧前 10 个奇异方向（占奇异值平方 0.50–0.56）。5,041 篇训练论文（9,108 篇减去含配对论文的作者团队），5 折作者团队交叉验证，全部是留出集分数，没有 CI。领域 8 类大致均衡：最多的数学占 0.137，均匀 0.125。全作者重拟合 R² 最大 0.0092（L48）。搬动结果（测试集 582 对，团队 95% CI）：S_id L40 +0.005 [+0.001, +0.009]，随机 +0.003 [+0.001, +0.006]，完整替换 +0.920 [+0.895, +0.945]；S_auth L48 +0.018 [+0.012, +0.024]，随机 +0.003，完整 +0.428 [+0.394, +0.462]，约为完整替换的 4%。移除臂：把任一子空间设为均值，损失不超过随机子空间（+0.001）。预注册判定：H2 不支持（R_id 0.005 < 0.5 × R_full 0.460）；H3 按规则通过（R_auth − R_id +0.014 [+0.008, +0.020]），但 S_auth 读不出作者，所以不算 H3 的证据。怎么算：R_S = mean(替换 − 被替换方) ÷ mean(干净 − 被替换方)，B 的提示里每个标题位置用 h_B + P_S(h_A − h_B)。
【训练论文筛选链（2026-11-13 核对）】① 9,108 篇全部队列（存档作者团队编号，共享任一作者全名 = 同一团队）→ ② 配对涉及的论文：1,178 篇 A + 1,100 篇 B（配对伙伴）+ 1,109 篇 C（随机论文）的并集 = 2,966 篇，分属 2,611 个团队 → ③ 排除这 2,611 个团队的全部论文 4,067 篇（= 2,966 篇配对论文 + 1,101 篇与配对论文共享作者全名、但不在配对里的论文）→ ④ 剩 5,041 篇训练论文，再按存档团队折做 5 折交叉验证。出处：~/jlens_work/13_stage13/stage13_x2_fit.py 第 5–7、85–89 行；381_stage13/logs/x2fit_11637589.log 第 1 行。替换实验另用 1,178 对（调参 596 / 测试 582，按作者团队分），与训练论文不重叠。随机对照 = 3 个随机 10 维子空间（种子 61–63）。
【公式与样本量（v18）】R_S = 只把 A 的子空间分量换进 B 后移动的 A − B 差距比例；测试集 582 对（页面方法说明）。
【2026-11-19 整合（v21）】新增小框（来自原第 99 页，已删除）：用全部作者重新拟合作者子空间后，搬动量 0.032（完整替换 0.457，约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.0092），单看这一项，对"隐藏作者"没有支持。〔b1_xall_report.md〕

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）：X2 → subspace swap; removed source: (X2: summary_b1_xall/x2_curves_new__all.csv, x2_verdict_new__all.csv, fit_authall_sanity.csv)

## P106 · HTML v75 p106 · pptx S113 (v22z) — No clear earlier shelf: only small, scattered early traces

**要说的话（一句英文一句中文）**
This page asks, as an exploratory map, whether there is an earlier place in the prompt where the paper signal is already stored.
这一页用一张探索性的图问：提示词里有没有更早的位置已经存着论文信号？
We read every prompt position at every layer with three readouts and compare recognised with unrecognised papers.
我们用三种读出方式逐层读每一个提示位置，比较认得和认不得的论文。
On the chart, a coloured cell above zero means recognised papers read better there; a few cells pass the rule, with small values from about 0.008 to 0.05.
图上着色格大于 0 表示认得的论文在那里读得更好；有几个格子满足规则，数值很小，大约 0.008 到 0.05。
But we tested 672 cells without correction, and about 17 would pass by chance, so these are only traces.
但我们检验了 672 个格子且没有做校正，碰运气大约也会有 17 个通过，所以这些只是痕迹。
So there is no clear earlier store, only small scattered traces. Next, a summary of the readouts.
所以没有清楚的更早存放位置，只有零散的小痕迹。下一页小结读出工具这条线。

**备查（不念）· 上一版讲稿本页全文（原第 P72 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 补充 18b 第 1 项（2026-11-17 锁定）：3 种读出（logit lens、public J-lens、名字 token probe）× 9 个提示位置（标题全部 / 内容词 / 第一个 / 最后一个、标题后引号、年份数字、")?\n"、"Authors"、":"，另以名字位置作参照）× 20 层；金标 = 姓氏第一个 token；指标是 spec 的档内 target − control。锁定规则：某个位置在 L ≤ 48 的某层 CI > 0，同时名字位置在该层的 CI 包含 0。600 篇（300 target + 300 control；Stage 11 子样本，种子 1817），团队 bootstrap 2,000 次。

**关键数字和 CI：**
- 锁定规则在部分格子中满足：logit lens 年份从 L40 起、":" L45、"Authors" L36；J-lens 第一个标题 token L8；probe 标题 L32（title_all L32、title_content L40、year L32）。
- 首 token 金标：logit 年份 L24、close L16、冒号 L44；J-lens close L40；probe title_first L40。
- 名字位置（参照）首次 CI > 0：logit L52，J-lens L56，probe L48。
- 48 个位置 × 金标 × 读出组合中有 15 个满足规则（'quote' 无法估计），共 59 个格子；这些格子的 T − C 为 +0.008 到 +0.049。
- 局限：共检验 672 个格子，60 个 CI > 0，按机会约应有 17 个，没有校正，所以只能当作位置线索；规则比较的是两个 CI，不是配对检验；probe 是在 600 篇上训练的。

**结论状态：** 探索性（锁定规则在部分格子中满足，但效应小，未校正）。

**过渡：** 再看论文信息在 Stage 12 的 patching 里具体经过哪些位置、哪些组件。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $T-C\ \mathrm{of\ spec\ per\ position\ and\ layer}$；② n = 600 papers (300 target + 300 control)；③ T − C > 0 before the name: an earlier shelf；原 “How computed” 段：How computed: within-bin target − control of spec at 9 prompt positions × 20 layers; locked rule: a position has CI > 0 at some L ≤ 48 while the name position’s CI at that layer includes 0. 600 papers, team bootstrap ×2,000.；原出处行：381_stage13/summary_a18b_item1/ (item1_map.csv, item1_criterion.csv) · config/prereg_addendum18b.md；方法细节移到备用页 B16 (slide 111)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Readout map (pre-registered, locked)" ← "Addendum 18b item 1 (locked 2026-11-17)"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 共测 20 层（L8–L60），锁定规则只在 L8–L48 这 14 层上检验；9 个提示位置 × 14 层 × 3 种读法 × 2 种名字 token = 756 格，其中引号位置无法估计，可估计 672 格。 锁定规则全文：某位置在 L ≤ 48 的某层 T − C 的 CI > 0，而名字位置同层 CI 含 0。

## P107 · HTML v75 p107 · pptx S114 (v22z) — The locked rule of the readout map

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

## P108 · HTML v75 p108 · pptx S115 (v22z) — What we saw: “What can each readout see?”

**要说的话（一句英文一句中文）**
This page sums up what each readout can see.
这一页小结每种读出工具能看到什么。
In the small samples, a better-fitted lens did not rank authors better, and the Jacobian lens added about nothing.
小样本里，拟合得更好的 lens 并没有把作者排得更好，Jacobian lens 几乎没有增益。
In the full cohort, lenses read the shape of names in the middle layers but add no paper knowledge, while a trained probe at the title decodes it.
全队列里，lens 在中间层能读出名字的形状，但不带来论文知识；训练出来的 probe 在标题处能解码出来。
So the information is there, but not in a form the lens can read; the bottleneck is the readout tool, not missing information.
所以信息在那里，只是不在 lens 能读的形式里；瓶颈在读出工具，而不是信息不存在。
Next, back to the route: is any single layer a bottleneck?
接下来回到路线：有没有哪一层是瓶颈？

**备查（不念）· 上一版讲稿本页全文（原第 P43 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 小样本：Self-100 对最终分布拟合得更好，作者排名没有更好；J-Lens − Vanilla 约 0（7.4：+0.002；Stage 8：−1.4 pp；50 / 200 篇）；Stage 9 只拟合了 Fit A，稳定性没有检验。全队列：Jacobian lens 在 L48 的 top-10 比例 15–18%，logit lens 为 1%（9,108 篇；X3_means.csv）；额外 title-specific 信号只有 +0.01–0.03（L24–L48），而且不偏向 target；L62 上普通 logit lens 最好；标题 token 处的线性 probe：+0.05 → +0.08（复核；E4b 只打第一个名字 token），是论文特异的；读出图（补充 18b 第 1 项，探索性）：年份 / ':' / 第一个标题 token 处有微弱的早期痕迹，+0.008 到 +0.049，未校正 → 第 72 页。

**关键数字：** 见上；n = 50 / 200 篇（Stages 1–9）· 9,108（10–11）· 1,395（probe）· 600（补充 18b）。

**结论状态：** B 线：lens 结论为定论；probe 为初步；早期痕迹为探索性。一句话：信息在那里，但不是 lens 能读的形式。两个阶段一致：没有哪种 lens 能在中间层揭示出隐藏的论文知识；规模化补上了正面证据，训练出来的 probe 能在标题处解码，所以瓶颈在读出工具，而不是信息不存在。

**过渡：** 进入 C 线：信息在哪一层出现、在哪一层被使用。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\Delta=\mathrm{spec}_{\mathrm{lens}}-\mathrm{spec}_{\mathrm{logit\ lens}}$；② n = 50 / 200 papers (Stages 1–9) · 9,108 (10–11) · 1,395 (probe) · 600 (route tests)；③ Δ > 0: the lens reads more than the logit lens；原公式框：Δ = spec lens − spec logit lens n = 50 / 200 papers (Stages 1–9) · 9,108 (10–11) · 1,395 (probe) · 600 (add. 18b)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(50 / 200 papers)
- 出处（原在幻灯片上）：(9,108 papers; X3_means.csv)
- 出处（原在幻灯片上）：(L24–L48; X3_means.csv)
- 出处（原在幻灯片上）：(E4b, scores only the first name token; e4b_trainstd_compare.md)

**备查（不念）：**
- 列表原写 “Readout map (add. 18b item 1, exploratory)”：读出地图 = 补充登记 18b 第 1 项

## P109 · HTML v75 p109 · pptx S116 (v22z) — Single-layer route: no single layer is a bottleneck

**要说的话（一句英文一句中文）**
This page asks which single layers each attention edge needs, or whether the route is spread over many layers.
这一页问：每条注意力边需要哪几个单独的层，还是路线分散在很多层上？
We cut one edge at one layer, between layers 40 and 56, on the same papers and five false titles, with a rule locked before the run.
我们在第 40 到 56 层之间，每次在一层切断一条边，用同样的论文和 5 个假标题，规则在运行前锁定。
On the chart, a loss above zero means that edge at that layer carries part of the signal; name from title carries some at layers 44, 48, 52 and 54.
图上损失大于 0 表示这条边在这一层承载了一部分信号；名字看标题在第 44、48、52、54 层各承载一点。
But each single cut removes at most 1.25% of the signal.
但每次单独切断最多只去掉 1.25% 的信号。
So the route is parallel: no single layer is a bottleneck. Next, what happens if we push information into the late layers.
所以路线是并行的：没有哪一层是瓶颈。下一页看把信息推进后面的层会怎样。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Single-layer route: no single layer is a bottleneck Now asking: which single layers does each attention edge need, or is the route spread over many layers? locked · supported single-layer route located · evidence type: intervention ▲ (edge knockout) · loss > 0: that edge at that layer carries part of the paper signal Method: one attention edge (all heads) cut at one layer, L40–L56; same papers and five false titles as the window test (slide 96). 1 Result: name ← title carries information at L44, L48, L52, L54 ; at L48 and L52 it beats every other edge. – also small: “:” ← title at L50 and name ← “:” at L44; – 6 of 45 cells pass Holm; none reversed. 2 Size: each single cut removes at most 1.25% of S(none) = 0.328. Control: S already subtracts the five false titles, so names that are easy to guess do not count. Caveat: a single-layer cut is a lower bound: the other layers can carry the same information ; 600-paper sub-sample. Compare: the 4-layer windows (slide 96) cost up to 3.5% — the information is spread over neighbouring layers. So (this slide): the title reaches the names through many layers in parallel; name ← title at L48 and L52 is the strongest single step, but no single layer is a bottleneck locked · supported

数字出处：27_v67/fragments/part56_numbers.md

## P110 · HTML v75 p110 · pptx S117 (v22z) — Injection: author direction vs own title signal

**要说的话（一句英文一句中文）**
This page asks: if we push the information that has already arrived, or the author direction the probe reads, does the model write the author?
这一页问：如果把已经到达的信息，或者 probe 读到的作者方向再推一把，模型会写出作者吗？
We add each direction to the state at the names, at several layers and strengths, under rules locked before the run.
我们在名字位置的状态上，按不同层、不同强度加上这些方向，规则在运行前锁定。
On the chart, the share is how often the model writes the right surname. Pushing the paper's own title signal moves it from 2.5% to only 2.8%, no real gain.
图上比例是模型写对姓氏的频率。推论文自己的标题信号，只从 2.5% 升到 2.8%，没有实际增益。
Pushing the probe's author direction raises it to 9.7%, but another author's direction writes that other author too, so it acts mainly as a write channel; only a small part is specific to recognised papers.
推 probe 的作者方向能升到 9.7%，但换成别的作者的方向，也会写出那个作者，所以它主要是一个写入通道；只有很小一部分是认得的论文特有的。
So more of what arrived does not help, and the author direction writes rather than unlocks. Next, why pushing can hurt.
所以已经到达的信息再多也没用，作者方向是在写入，而不是解锁。下一页看为什么推一把反而会有害。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Injection: author direction vs own title signal Now asking: if we push the information that has already arrived, or the author direction the probe reads, does the model write the author? ① locked · not supported ② locked · supported direction usable + exploratory mostly a write channel · evidence type: intervention ▲ (injection) · G ≈ 0: pushing the title signal adds nothing · S > 0: this author’s direction writes this paper’s author more 1 Result: own title signal: 2.5% → 2.8% (L52 β2), no gain at any layer or β; see slide 123. Why: the damage is direction-driven , and near the writer the paper’s own push hurts more than another paper’s (P −0.050 at L56 β4; slide 106). So: more of what already arrived does not help . 2 Result: author direction: 2.5% → 9.7% (L52 β2) vs 2.0% for another author’s direction. Control: another author’s direction also writes that author (+0.042 vs +0.072) → mainly a write channel; – recognised-specific extra only +0.025 [+0.004, +0.048] (L52 β1), +0.035 [+0.011, +0.058] (L48 β2) — small. So (this slide): the late layers can write a name when handed the answer’s direction, but not when handed more of the arrived title signal; the direction works mainly as a write channel, with a small recognised-specific part locked exploratory

数字出处：27_v67/fragments/part56_numbers.md

## P111 · HTML v75 p111 · pptx S118 (v22z) — Why pushing hurts: direction, not length

**要说的话（一句英文一句中文）**
This page asks why pushing more title signal did not help, and at high strength even hurt: is it the length of the push, its direction, or this paper's own signal?
这一页问：为什么推更多标题信号没用，强度大时甚至有害——是推的长度、方向，还是这篇论文自己的信号？
Under a locked rule, we pushed with the same length in a new direction, with the same direction at a new length, and with another paper's signal.
按锁定的规则，我们分别用相同长度的新方向、相同方向的新长度，以及另一篇论文的信号去推。
On the chart, O below zero means a push in a new direction lowers the true name; direction-only pushes hurt in all nine cells, length-only pushes only at the highest strength near the writer.
图上 O 小于 0 表示换一个方向推会降低真名字；只改方向的推法在全部 9 个格子里都有害，只改长度的推法只在最高强度、靠近写出层时有害。
Right before the writing layers, the paper's own signal even hurts more than another paper's.
就在写出层之前，论文自己的信号甚至比别的论文的信号伤害更大。
So the damage is about direction, not length. Next, the verdict card for Part 5.
所以损害来自方向，不是长度。下一页是第 5 部分的判定卡。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Why pushing hurts: direction, not length Now asking: more title signal did not help and at β4 even hurt (slide 105); is the damage the extra length of the push, its direction, or this paper’s own signal? locked · supported damage is direction-driven; own hurts more than another near the writer · evidence type: intervention ▲ (injection) · · · O < 0: a push in a new direction (same length) lowers the true name 1 Result: direction-only pushes hurt in all 9 cells (from −0.015 at L48 β1 to the large drops shown at L56–L57); length-only pushes hurt only at β4 near the writer (2 of 9 cells, e.g. −0.043). 2 Result: right before the writer the paper’s own signal hurts more than another paper’s (P −0.020 at L56 β2, larger at β4) — the reverse of “own helps”. Caveat: teacher-forced scores only; injection at the after-title positions only; one decomposition (length vs direction) . So (this slide): the late writer is sensitive to the direction of its input, not just to how much signal arrives: extra paper signal near L56–L57 disrupts rather than helps locked · supported

数字出处：27_v67/fragments/part56_numbers.md

## P112 · HTML v75 p112 · pptx S119 (v22z) — Verdict card: route and H3

**要说的话（一句英文一句中文）**
This verdict card closes Part 5: what do the route and readout tests say together?
这张判定卡给第 5 部分收尾：路线和读出检验合起来说明什么？
H3 is supported on the same scale: at the name positions a probe separates recognised from unrecognised papers better than the lens.
H3 在同一尺度上得到支持：在名字位置，probe 区分认得和认不得论文的能力强于 lens。
The title reaches the names over parallel routes; name from title is strongest at layers 48 and 52, but no single cut matters much.
标题经由多条并行路线到达名字；名字看标题这条在第 48 和 52 层最强，但切断任何一处影响都不大。
The author direction is usable, but mainly as a write channel, and pushing more title signal hurts through its direction.
作者方向是可用的，但主要是写入通道；推更多标题信号会因为方向而造成损害。
Open questions remain: which subspace holds the authors, and whether the readout difference is causal. Next, the evidence matrix.
还有未解决的问题：作者到底存在哪个子空间里，读出上的差别是不是因果性的。下一页是证据矩阵。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Verdict card: route and H3 Now asking: what do the route and readout tests together say about H3? Conclusion H3 supported on the same scale : at the name positions a probe separates target from control more than the lens (L40 +0.021 , L48 +0.062 ; slide 99). The title reaches the names over parallel routes ; name ← title is strongest at L48 and L52 (slides 96, 104). Evidence strength locked · supported same-scale probe vs lens; route rule met in the windows and at single layers. locked · supported the author direction is usable; exploratory it works mainly as a write channel (slide 105). locked · supported pushing more title signal hurts through direction (slide 106). descriptive the name positions carry most of the restored signal by L52 (slide 95). Open questions which subspace holds the authors (a small subspace swap moves little, slide 101); is the direction an unlock or just a write channel; a linear causal test at L48–L56 is not yet run. → So (this slide): the information is there at the name positions in a probe-readable form; whether the late layers can use it is the question of Part 6 locked

数字出处：27_v67/fragments/part56_numbers.md

## P113 · HTML v75 p113 · pptx S120 (v22z) — Evidence matrix after Part 5

**要说的话（一句英文一句中文）**
This matrix shows where each hypothesis stands after Part 5.
这张矩阵显示第 5 部分之后每个假设的位置。
The H3 row and the route row are now filled: the probe beats the lens on the same scale, the names carry most of the signal by layer 52, and the route is parallel.
H3 和路线这两行已经填上：probe 在同一尺度上胜过 lens，名字位置到第 52 层承载了大部分信号，路线是并行的。
Only the writing step is left.
只剩写出这一步。
Next, Part 6: said late, and stuck at writing.
接下来是第 6 部分：说得晚，卡在写出这一步。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Evidence matrix after Part 5 Now asking: with Part 5 done, where does each hypothesis stand? H1 · does the middle know "what is asked"? (✓) “:” new question vs paper 4.7× (L4) → 2.2× (L48) descriptive s. 51 (✓) probe after the question change T 0.24–0.41 descriptive s. 49 ~ top lens word format words; title-dependent 28–64% descriptive s. 37 ~ format locking (+ checks) L56 = sink artefact; names default locked + exploratory s. 52 (✓) swap “:” at L56 author signal −0.03 locked s. 52 Verdict: downgraded: “:” follows the question; the format layer is not pinned down → s. 53 H3 · author info in the middle, not in vocabulary directions? ✗ author-prompt lens, mid layers −0.058 at L48 pre-registered s. 94 (✓) probe at the title +0.052 at L24 descriptive s. 93 ✓ same-scale probe vs lens L40 +0.021, L48 +0.062 locked s. 99 ~ "author" subspace swap passes, moves only ≈ 7% pre-registered s. 101 ~ direction of the difference spread; not on author axes exploratory s. 100 (✓) inject the author direction 2.5% → 9.7%; mainly write channel locked s. 105 Verdict: supported; small effect; correlational evidence → s. 107 H2 · does the middle know "which paper"? ~ paper facts at the title readable, inferable from text descriptive s. 16 ~ same title, other question · copy ceiling: L4 cosine 0.998 exploratory s. 77 ~ paraphrased title text-only model reaches 60% pre-registered s. 71 ✗ made-up title meaning 75%; real title +0.106 locked s. 73 ✗ rare vs common words 0.162 vs 0.027 locked s. 80 ✗ recognised / citation check not larger; smaller if cited more locked s. 78 ✗ variance split identity ≈ 0 locked s. 79 ✗ "paper facts" subspace swap R_id 0.004 pre-registered s. 101 (✓) L8 surname test T1 +0.046; T2/T3 marginal; ½ topic locked s. 81 Verdict: not a general paper identity, with one small locked exception → s. 82 Writing step (the bottleneck) tested in Part 6 ✓ supports (✓) partly ✗ weakens ~ cannot separate strength: settled locked pre-registered descriptive exploratory s. = slide So (section): the information reaches the names over parallel routes and is held there in a probe-readable form; next, Part 6 asks why it is still not written out.

数字出处：27_v67/fragments/part56_numbers.md

# Part 6 · Said late, stuck at writing (114–132)

## P114 · HTML v75 p114 · pptx S121 (v22z) — Question card: the writing step

**要说的话（一句英文一句中文）**
This question card opens Part 6: the information is at the name positions by about layer 50, so why does the model still not write the author?
这张问题卡开启第 6 部分：信息大约在第 50 层就到了名字位置，为什么模型还是写不出作者？
The hypothesis is that recall fails at the late writing step, the MLPs of layers 57 to 61 and the first name token, not because too little information arrives.
假设是：回忆失败在最后的写出这一步——第 57 到 61 层的 MLP 和名字的第一个 token——而不是因为到达的信息太少。
If it holds, removing the late MLPs should remove the signal, a stronger arrived signal should not help, some names should rise and then fall late, and the first token should be the hardest.
如果成立，去掉后面的 MLP 应该会去掉信号，更强的到达信号不会有帮助，有些名字会在后期先升后降，第一个 token 最难。
And if the problem were storage direction, writing the title from the authors would be much easier.
如果问题出在存储方向上，那从作者写出标题应该容易得多。
First a background block on which token carries it, then the decisive tests.
先看“哪个 token 承载信号”的背景块，再看决定性检验。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Question card: the writing step Now asking: the information is at the name positions by about L50; why does the model still not write the author? Hypothesis (writing step) Recall fails at the late writing step (the L57–L61 MLPs and the first name token), not because too little information arrives. If it holds, we expect ① removing the late MLPs removes the signal; ② a stronger arrived signal does not help; ③ some papers’ names rise and then fall late; ④ the first token is the hardest; a hint of it helps; ⑤ writing the title from the authors is no easier. If it fails, we expect ① attention, not MLPs, writes; ② more input → more names; ③ no late fall; ④ all name tokens equally hard; ⑤ authors → title much easier (a reversal curse). Tests in this part Who writes: mean ablation at L57–L61 (slide 122) → late suppression in a subgroup (slide 124). Does more input help: strengthening the arrived information (slide 123) → why pushing hurts (slide 106). Is it the direction of storage: authors → title vs title → authors (slide 125). Which part of the name: first token vs the rest (slides 111–117) → co-author chain (slide 118) → names it writes itself, true vs made up (slides 119, 120). So (section): Part 5 showed the information arrives and is held at the name positions; this part asks what goes wrong when it has to be written out.

数字出处：27_v67/fragments/part56_numbers.md

## P115 · HTML v75 p115 · pptx S122 (v22z) — Background: how we got here (small samples) · Part 6

**要说的话（一句英文一句中文）**
This divider marks the background block for Part 6: what the earlier samples suggested about which token carries the signal.
这张分隔页标出第 6 部分的背景块：早期样本对“哪个 token 承载信号”有什么提示。
They suggested that the recognition gap sits on the rest of the name, which turned out to be a name-format effect.
它们提示认得的差距落在名字的后半部分，后来发现这是名字格式造成的。
These pages can be skipped in the talk; the decisive tests start with who writes the name.
汇报时这几页可以跳过；决定性检验从“谁写出名字”开始。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Part 6 · background Background: how we got here (small samples) Now asking: what did the earlier, smaller samples suggest before the decisive tests? In this block: slides 111–121 111 Which token carries it? 112 From first token to the full name 113 The A−B gap sits on the rest of the name 114 First token or the rest of the name? 115 Knowing the given name helps with the surname 116 Where the signal sits, and a dose-response 117 Co-authors help, and partly replace the title 118 A true co-author helps — through the co-author network, not this paper 119 Names the model writes itself: true vs fabricated 120 Made-up names are not confused neighbours: half are not in the data 121 What we saw: “Which token carries it?” What they suggested: the recognition gap sits on the rest of the name; full given names and surnames carry the signal, initials little Caveat: small samples; single papers or pairs can drive a result Decisive tests: start at slide 122 So (section): these pages set up the question; the decisive tests of this part start at slide 122. descriptive

## P116 · HTML v75 p116 · pptx S123 (v22z) — Which token carries it?

**要说的话（一句英文一句中文）**
This page opens the question: which part of the name, and which cue in the prompt, carries the signal?
这一页提出问题：名字的哪一部分、提示里的哪一个线索在承载信号？
The small samples asked whether it sits on the first token or the rest of the name.
小样本问的是：信号在第一个 token 上，还是在名字的其余部分？
The full cohort answered: it depends on the name format, the information enters the name positions mainly at layers 40 to 50, and co-authors can partly replace the title.
全队列的回答是：取决于名字格式；信息主要在第 40 到 50 层进入名字位置；合作者能部分替代标题。
The next pages show the steps.
接下来几页展开这些步骤。

**备查（不念）· 上一版讲稿本页全文（原第 P52 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 小样本问的是：信息在第一个 token 上，还是在名字的其余部分？全队列的回答是：取决于名字格式；信息主要在 L40–L50 进入名字位置，部分经由标题之后的 token；合作者能部分替代标题。另附补充 16：答案格式（只有 F4，即给出第一作者的名首字母，有帮助）得到支持；合作者链是网络关联，不是对这篇论文的记忆 → 第 59–60 页。

**过渡：** 从 Stage 6 的全名打分开始。

**备查（不念）：**
- 底部条原写 “+ addendum 16:”：addendum 16 = 生成测试补充登记（答案格式 B + 名字链 D）

## P117 · HTML v75 p117 · pptx S124 (v22z) — From first token to the full name

**要说的话（一句英文一句中文）**
This page asks whether the model scores the full author names better for recognised papers.
这一页问：对认得的论文，模型给完整作者名的分数是不是更高？
On 50 papers we scored every listed author with teacher forcing, which means we feed the correct earlier tokens and score the next one.
在 50 篇论文上，我们用 teacher forcing 给每位作者打分，也就是把前面正确的 token 喂进去，再给下一个打分。
On the chart, a higher mean reciprocal rank means the name tokens sit nearer the top; recognised papers are ahead, about plus 0.10 at layer 62.
图上倒数排名均值越高，表示名字 token 越靠前；认得的论文领先，第 62 层大约 +0.10。
But every token after the first already gets the correct prefix, which makes it much easier.
但第一个之后的每个 token 都已经拿到了正确的前缀，这让它容易得多。
So the next step splits the first token from the rest.
所以下一步把第一个 token 和其余部分分开。

**备查（不念）· 上一版讲稿本页全文（原第 P53 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 50 篇论文、227 位作者、972 个名字 token；用 teacher forcing 给每位列出的作者打分；按组比较条件全作者 JMRR。

**关键数字和 CI：**
- Integrated JMRR：A（20）0.085 [0.075, 0.096]；B（20）0.068 [0.057, 0.080]；C（7）0.106；D（3）0.050。
- L62 A−B +0.097 [0.028, 0.163]；Vanilla 也是 +0.091（20 对）。
- n = 50 篇 · 227 位作者 · 972 个名字 token · 20 个 A/B 对。

**结论状态：** 探索性。结果为正，但第一个 token 之后的每个 token 都已经给了正确前缀。下一步：把第一个 token 和其余部分分开（7.1）。

**过渡：** 7.1 把第一个 token 和后续 token 拆开。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{JMRR}=\mathrm{mean}_a\,\mathrm{mean}_t\,1/r$；② n = 50 papers · 227 authors · 972 name tokens · 20 A/B pairs；③ JMRR = 1: every name token ranked first (teacher forcing)；原公式框：JMRR = mean a mean t 1/r (teacher forcing) n = 50 papers · 227 authors · 972 name tokens · 20 A/B pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(token_layer_scores.csv)
- 出处（原在幻灯片上）：(integrated_group.csv)
- 出处（原在幻灯片上）：(20 pairs, matched_ab_bootstrap.csv)

## P118 · HTML v75 p118 · pptx S125 (v22z) — The A−B gap sits on the rest of the name

**要说的话（一句英文一句中文）**
This page asks whether the recognition gap sits on the first token or on the rest of the name.
这一页问：认得的差距是在第一个 token 上，还是在名字的其余部分？
We re-analysed the same data, splitting by token position.
我们按 token 位置拆开，重新分析同一批数据。
On the chart, a value above zero means recognised papers score higher; on the first token it is about zero, on the later tokens about plus 0.02.
图上大于 0 表示认得的论文分数更高；第一个 token 上约为 0，后面的 token 上约 +0.02。
Completing a name is easier than starting it, so a gap on later tokens does not show the model can recall the name on its own.
补全一个名字比起头容易，所以后面 token 上的差距不能说明模型能自己回忆出名字。
The open question was whether this is about initials versus surnames. Next, the full cohort's answer.
遗留的问题是：这是不是首字母和姓氏的区别？下一页看全队列的回答。

**备查（不念）· 上一版讲稿本页全文（原第 P54 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 只用 CPU 重新分析 Stage 6；10,000 次配对 bootstrap；按 token 位置比较 integrated A−B JMRR。

**关键数字和 CI：**
- 第一个 token：+0.001 [−0.011, +0.015]；后续 token：+0.021 [+0.002, +0.039]；全部 token：+0.017 [+0.003, +0.030]（20 对，7 层）。
- L62：第一个 token +0.014（12/20 对）vs 后续 +0.121（15/20）。
- 加上标题对比（补充 13 C-1）：输出层成立（+0.244），L62 也成立（logit +0.278，public J-lens +0.317）；public J-lens 6 层均值不显著（+0.077 [−0.021, +0.180]）（20 对，名字其余部分；c13_C1.md）。
- n = 20 个 A/B 对（40 篇）· 10,000 次配对 bootstrap。

**结论状态：** 探索性。补全名字比起头容易，后续 token 上的差距不能说明模型能独立回忆出名字。遗留问题：这是不是首字母 vs 姓氏的问题？

**过渡：** 全队列可以直接按名字格式拆开回答这个问题。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $A-B=\mathrm{JMRR}_A-\mathrm{JMRR}_B\ \mathrm{by\ token\ position}$；② n = 20 A/B pairs (40 papers) · 10,000 draws；③ A − B > 0: recognised papers read better at that token；原公式框：A − B = JMRR A − JMRR B by token position n = 20 A/B pairs (40 papers) · 10,000 pair-bootstrap draws。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(20 pairs; layer_and_integrated_effects.csv)
- 出处（原在幻灯片上）：(layer_position_effects.csv)
- 出处（原在幻灯片上）：(20 pairs, rest of the name; c13_C1.md)

**备查（不念）：**
- 绿字原写 “With a title contrast (addendum 13 C-1)”：addendum 13 C-1 = 补充登记 13 的 CPU 复核项 C-1（加标题对比）

## P119 · HTML v75 p119 · pptx S126 (v22z) — First token or the rest of the name?

**要说的话（一句英文一句中文）**
This page asks, in the full cohort, which part of the name carries the signal.
这一页问：在全队列里，名字的哪一部分承载信号？
We split names by format: those that start with an initial, like “S. Bree”, and those that start with a full given name, like “Yan Zhao”.
我们按格式把名字分开：以首字母开头的，比如 “S. Bree”；以完整的名开头的，比如 “Yan Zhao”。
On the chart, spec above zero means the true title ranks the author higher; for initials the first token gives about 0.1 and the later tokens about 0.45.
图上 spec 大于 0 表示真标题让作者排得更前；首字母开头的名字，第一个 token 约 0.1，后面的 token 约 0.45。
For full given names, the first and later tokens are about equal, around 0.36 and 0.40.
完整的名开头时，第一个 token 和后面的差不多，大约 0.36 和 0.40。
So the small-sample puzzle is a format effect: for “S. Bree”, the surname is itself a later token. Next, whether knowing the given name helps with the surname.
所以小样本的谜题是格式效应：对 “S. Bree” 这种名字，姓本身就是后面的 token。下一页看知道了名能不能帮助猜姓。

**备查（不念）· 上一版讲稿本页全文（原第 P55 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型输出层，按名字格式分两类："以首字母开头"（如 "S. Bree"）和"以完整的名开头"（如 "Yan Zhao"）；分别看第一个 token 和后续 token 的 title-specific 信号及 target − control。

**关键数字和 CI：**
- 首字母携带的信息很少，信号在姓氏上。
- 完整的名携带的信息和姓氏差不多。
- （柱状图数值见幻灯片，文字框没有给出具体数字。）
- n = 9,108 篇（T − C：4,621 + 2,220）。

**结论状态：** 定论（第 64 页"第一个 vs 其余：由首字母 vs 完整的名解释，explained"）。

**过渡：** 完整的名不仅自身携带信息，还能帮助预测后面的姓氏。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$$\ \mathrm{by\ name\ format}$；② n = 9,108 papers (T − C: 4,621 + 2,220)；③ spec > 0: the true title ranks the author higher than false titles；原公式框：spec = nlr true − mean 5 nlr false , by name format n = 9,108 papers (T − C: 4,621 + 2,220)。

## P120 · HTML v75 p120 · pptx S127 (v22z) — Knowing the given name helps with the surname

**要说的话（一句英文一句中文）**
This page asks whether knowing the given name helps with the surname.
这一页问：知道了名，对猜姓有没有帮助？
We split authors by whether the given name reaches the top ten, and compare how well the surname is read.
我们按名有没有进入前十把作者分开，比较姓读得好不好。
On the chart, delta above zero means knowing the given name helps with the surname; a full given name in the top ten adds about 0.22 at the output.
图上 Δ 大于 0 表示知道名有助于猜姓；完整的名进入前十时，输出层大约多 0.22。
An initial in the top ten does not help at all.
首字母进入前十则完全没有帮助。
So a full given name narrows down the surname; this is a correlation. Next, where the signal sits, and a dose-response.
所以完整的名能缩小姓的范围；这是相关关系。下一页看信号落在哪里，以及剂量反应。

**备查（不念）· 上一版讲稿本页全文（原第 P56 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 真标题条件下，按"第一个词（名）是否进入 top 10"把作者分开，比较后续词（姓）的 nlr：Δ = nlr(后续词 | 第一个词在 top 10) − nlr(… 不在 top 10)；分首字母和完整的名，看模型输出、logit L62、public L62。

**关键数字和 CI：**
- 完整的名进入 top 10 时：姓 +0.22（输出层；Stage 10，8,876 位作者，§6.7）；+0.32（logit L62）。
- 首字母进入 top 10：没有帮助。
- n = 8,876 位作者（Stage 10）。

**结论状态：** 初步（较稳但有前提：条件分析，属相关关系）。

**过渡：** 下一页把信号按 token 角色拆开，并看它和识别程度之间的剂量关系。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\Delta=\mathrm{nlr}(\mathrm{later}\mid\mathrm{first\ in\ top\,10})-\mathrm{nlr}(\mathrm{later}\mid\mathrm{not})$；② n = 8,876 authors (Stage 10)；③ Δ > 0: knowing the given name helps with the surname；原公式框：Δ = nlr(later words | first word in top 10) − nlr(… not in top 10) n = 8,876 authors (Stage 10)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(X3_means.csv)；(X2_spearman.csv)
- 出处（原在幻灯片上）：(X4: summary_x1x4/x4_decodability.csv (first author, year, field), summary_b1_xall/x4_D__all.csv (all authors), x4_earliest.csv, test split, team CI · X3: summary_x3/x3_gap.csv, summary_b1_xall/x3_recovery__all.csv, test split, team CI)
- 出处（原在幻灯片上）：381_stage13/summary_explore_{l4audit,x4_source,x3_checks,twins}_20261121/
- 出处（原在幻灯片上）：(X2: summary_b1_xall/x2_curves_new__all.csv, x2_verdict_new__all.csv, fit_authall_sanity.csv; all authors, test split, team CI)

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, 8,876 authors, §6.7)” → “(Stage 10, 8,876 authors)”

## P121 · HTML v75 p121 · pptx S128 (v22z) — Where the signal sits, and a dose-response

**要说的话（一句英文一句中文）**
This page asks which tokens carry the signal, and whether it grows with recognition.
这一页问：哪些 token 承载信号，它会不会随认得的程度增长？
We split the paper-specific signal by token role, and group papers by how many option orders they answered correctly.
我们按 token 角色拆开论文特有信号，再按多选答对的顺序数给论文分组。
On the chart, spec above zero means the true title ranks the author higher; the surname's first token is highest at about 0.68, the initial only about 0.13, and punctuation zero.
图上 spec 大于 0 表示真标题让作者排得更前；姓的第一个 token 最高，约 0.68，首字母只有约 0.13，标点为 0。
And the more option orders answered correctly, the stronger the signal, with a rank correlation of about 0.27.
答对的顺序越多信号越强，秩相关约 0.27。
So surname tokens carry it, and better-recognised papers read better. Next, whether co-authors help.
所以承载信号的是姓的 token，认得越好的论文读得越好。下一页看合作者有没有帮助。

**备查（不念）· 上一版讲稿本页全文（原第 P57 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 模型输出层。左图：按 token 角色的 title-specific 信号（9,108 篇）；右图：R0/R1 论文在引用档内中心化后的输出，按多选顺序答对的个数（0–4）分组（8,894 篇）。

**关键数字和 CI：**
- 姓氏第一个 token +0.68；姓氏其余 +0.58；名的第一个 token +0.36；首字母 +0.13；标点（对照）+0.00。
- 剂量反应：Spearman rho = 0.27，p < 0.001（Stage 10，8,894 篇，§6.6）。
- n = 9,108 篇（左）· 8,894 篇 R0/R1（右）。

**结论状态：** 初步（较稳但有前提）。（这一页本身没有状态标签；分组剂量的预注册检验见第 97 页 P3。）

**过渡：** 名字之间也会相互提示：前面的合作者能帮到后面的作者吗？

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec\ by\ token\ role}$ · $\rho=\mathrm{Spearman}(\mathrm{spec},\ \mathrm{orders\ right})$；② n = 9,108 papers (left) · 8,894 R0/R1 papers (right)；③ spec > 0: the true title ranks the author higher than false titles / ρ > 0: better-recognised papers read better (dose-response)；原公式框：spec by token role; ρ = Spearman(spec, orders right) n = 9,108 papers (left) · 8,894 R0/R1 papers (right)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 10, 8,894 papers, §6.6)” → “(Stage 10, 8,894 papers)”

## P122 · HTML v75 p122 · pptx S129 (v22z) — Co-authors help, and partly replace the title

**要说的话（一句英文一句中文）**
This page asks whether earlier co-authors help with later ones.
这一页问：前面的合作者对后面的作者有没有帮助？
We compare an author scored after the earlier co-authors with the same author scored alone.
我们把排在前面合作者之后打分的作者，和单独打分的同一位作者比较。
On the chart, chain above zero means the next author reads better given the co-authors; for later authors it is about 0.17 to 0.23.
图上 chain 大于 0 表示给了合作者之后，下一位作者读得更好；后面的作者大约是 0.17 到 0.23。
The title-specific part shrinks once co-authors are given, but recognised papers stay ahead.
给了合作者之后，标题特有的部分变小，但认得的论文仍然领先。
So co-authors help and partly replace the title. Next, whether that help is about this paper.
所以合作者有帮助，并且部分替代了标题。下一页看这种帮助是不是关于这篇论文的。

**备查（不念）· 上一版讲稿本页全文（原第 P58 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** Stage 11 E3，模型输出层，全部 9,108 篇，95% CI。比较 chain（"Authors: A1, A2, ..." 中排在后面的作者）和作者单独出现的分数：chain = spec(合作者之后) − spec(单独)，按作者位置（第 1、2、3、4+）分开。

**关键数字和 CI：**
- 后面的作者：+0.17 到 +0.23（Stage 11 E3，4,621 篇 target，§6.11）。
- title-specific 部分缩小。
- target 仍然高于 control。
- n = 9,108 篇（4,621 target、2,220 control）。

**结论状态：** 初步（较稳但有前提：teacher forcing；补充 16 D 进一步检验是否论文特异，见第 60 页）。

**过渡：** 补充 16 做了两个预注册检验：答案格式（B）和名字链（D）。先看答案格式。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{chain}=\mathrm{spec}(\mathrm{after\ co\text{-}authors})-\mathrm{spec}(\mathrm{author\ alone})$；② n = 9,108 papers (4,621 target, 2,220 control)；③ chain > 0: given co-authors, the next author reads better；原公式框：chain = spec(after co-authors) − spec(author alone) n = 9,108 papers (4,621 target, 2,220 control)。

**备查（不念）：**
- 图片重新生成（同一画图脚本、同一图表、同一样式），灰色出处标签改成白话名：“(Stage 11 E3, §6.11)” → “(Stage 11 co-author test)”；“(Stage 11 E3, 4,621 target, §6.11)” → “(Stage 11 co-author test, 4,621 target)”

## P123 · HTML v75 p123 · pptx S130 (v22z) — A true co-author helps — through the co-author network, not this paper

**要说的话（一句英文一句中文）**
This page asks whether a true co-author helps because of this paper, or because of the co-author network.
这一页问：真合作者的帮助是因为这篇论文，还是因为合作者网络？
In a pre-registered test, we gave the true first author or another paper's first author as a prefix, and let the model continue.
在一个预注册检验里，我们把真第一作者或者另一篇论文的第一作者作为开头，让模型往下写。
On the chart, a taller blue bar means the true first author leads to more true co-authors; for recognised papers 11.8% against 1.5%.
图上蓝色柱子更高，表示给真第一作者能带出更多真合作者；认得的论文是 11.8% 对 1.5%。
But the title-specific part is about zero, the effect is even larger without a title, and recognised and unrecognised papers are about equal.
但标题特有的部分约为 0，没有标题时效应反而更大，认得和认不得的论文差不多。
So the effect is real, but it is the co-author network, not memory of this paper. Next, names the model writes itself.
所以效应是真的，但它来自合作者网络，不是对这篇论文的记忆。下一页看模型自己写出的名字。

**备查（不念）· 上一版讲稿本页全文（原第 P60 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**关键数字和 CI：**
- 生成：A 真前缀 11.8% vs 其他前缀 1.5%；B 2.5% vs 0.3%；C（228）48.7% vs 12.7%。
- Teacher forcing G(1)：A 真标题 +0.167 [+0.147, +0.185]（Holm p 0.0025）；A title-specific +0.012 [−0.001, +0.025]；A 删除标题 +0.223 [+0.201, +0.247]；A − B 真标题 −0.019 [−0.045, +0.007]；B 真标题 +0.186 [+0.168, +0.204]；C 真标题 +0.124 [+0.090, +0.156]。
- n = 600 A / 600 B / 227–228 C 篇。

**结论状态：** 预注册判据成立（效应存在），但不是论文特异的：title-specific 约 0，没有标题时反而更大，A ≈ B，说明这是合作者网络的关联。局限：teacher forcing 分数反映偏好而非生成；只有贪心解码；标签来自另一次运行；C 功效低，仅描述。

**过渡：** 汇总 D 线。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{generation}=\mathrm{share\ writing}\geq 1\ \mathrm{more\ true\ author}$ · $G(1)=S(\mathrm{true\ co\text{-}author})-S(\mathrm{other\ paper\'s\ author})$；② n = 600 A / 600 B / 227–228 C papers；③ G > 0: a true co-author makes the next true author likelier / title-specific ≈ 0: not about this paper；原 “How computed” 段：How computed: generation = share of papers writing ≥ 1 more true author (full name) after a one-author prefix; teacher forcing G(1) = S(true co-author given) − S(other paper’s author given), later authors scored; title-specific = true − mean of 5 false titles.；原出处行：391_groups/summary_a16_20261115/ (d_gen.csv, d_contrasts.csv, holm.csv) · config/prereg_addendum16.md；方法细节移到备用页 B15 (slide 110)。

**备查（不念）：**
- 标签、副标题、aria 原写 “addendum 16”（Line D · addendum 16；Addendum 16 (pre-registered)）：addendum 16 = 生成测试补充登记（名字链 D）

## P124 · HTML v75 p124 · pptx S131 (v22z) — Names the model writes itself: true vs fabricated

**要说的话（一句英文一句中文）**
This page asks whether the middle layers can tell the true names the model writes from the names it makes up.
这一页问：中间层能不能分辨模型写出的真名字和它编造的名字？
We let the model write author lists, label each name as true or made up, and train a probe on the saved states.
我们让模型自己写作者名单，把每个名字标为真或编造，再在保存的状态上训练 probe。
On the chart, an AUROC above 0.5 means true names score above made-up ones; the middle layers reach about 0.72 to 0.78.
图上 AUROC 大于 0.5 表示真名字得分高于编造的名字；中间层达到约 0.72 到 0.78。
But the model's own output confidence already gives about 0.71, and what is left, about 0.05, appears only at layers 40 to 52.
但模型自己的输出置信度就已经给出约 0.71，剩下的约 0.05 只在第 40 到 52 层出现。
One check we added afterwards: the before-the-name curve mixed two kinds of tokens, a line break before the first name and a semicolon before the others; with later names only, it stays near chance until layer 52.
我们事后补了一个检查：名字之前那条曲线混了两种 token，第一个名字前是换行，其他名字前是分号；只看后面的名字，到第 52 层之前都接近随机。
On pairs of later names only, the small remainder beyond confidence is still there at layers 40 to 52.
只看后面名字配成的对，超出置信度的那一小部分在第 40 到 52 层仍然在。
So it is mostly confidence, and we keep this as exploratory. Next, where the made-up names come from.
所以大部分是置信度，我们把这一页保留为探索性。下一页看编造的名字从哪里来。

**备查（不念）· 上一版讲稿本页全文（原第 P92 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** C24 · 补充 15 第 2-11b 项：模型自己生成作者名单（chat template），生成时保存残差；按规则把每个写出的名字标为真（M）或编造（H）；计算论文内 AUROC（所有真 vs 编造名字对，probe(M) > probe(H) 记 1，平局记 0.5）。518 篇 target 论文，671 个真名字，3,388 对，L16–L56，团队整群 95% CI。和若干基线比较：位置、名字/字符串特征、知名度、组合、输出置信度、打乱标签。

**关键数字和 CI：**
- probe（ii，名字 token）：L16 0.723 [0.696, 0.751]；L40 0.780 [0.750, 0.808]；L48 0.782 [0.754, 0.812]；L56 0.736 [0.706, 0.765]。
- probe（i，名字之前的位置，次要）：0.541–0.633（如 L24 0.552，L48 0.589）。
- 基线：位置 0.632 [0.599, 0.666]；名字/字符串特征（2026-11-14 修正）0.530；知名度（非预注册）0.548；组合（非预注册，修正）0.636；输出置信度（非预注册，生成时）0.711 [0.678, 0.740]；打乱标签约 0.5。
- 超出置信度的余量（+0.050 到 +0.062）只出现在 L40–L52。
- n = 518 篇 target 论文，3,388 对。

**结论状态：** 预注册判据成立（补充 15 判据在全部 7 层通过，L48 0.782）；但非预注册的置信度检查显示大部分可由输出置信度解释，因此整体标为探索性（未定）。局限：实时生成；按规则匹配标签；置信度检查和与 H3 的联系都不是预注册的。

**过渡：** 那些编造出来的名字是从哪里来的？是不是把"邻居"搞混了？

**图旁公式（灰色行）：** AUROC = mean over (true M, fabricated H) pairs of 1[probe(M) > probe(H)]  (ties 0.5) · n = 518 target papers, 3,388 pairs

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{AUROC}=\mathrm{mean}_{(M,H)}\,\mathbf{1}[\mathrm{probe}(M)>\mathrm{probe}(H)]$；② n = 518 target papers, 3,388 pairs；③ AUROC > 0.5: true names score above made-up ones；原 “How computed” 段：How computed: within-paper AUROC over all true (M) vs fabricated (H) name pairs: 1 if probe(M) > probe(H), 0.5 for ties. 518 target papers, 3,388 pairs, L16–L56, team-cluster 95% CI.；原公式框：AUROC = mean over (true M, fabricated H) pairs of 1[probe(M) > probe(H)] (ties 0.5) n = 518 target papers, 3,388 pairs；原出处行：381_stage13/b2_gennames_b/summary/ (probe_within.csv, robust_posthoc.csv) · summary_c24_optB_20261114/report.md；方法细节移到备用页 B20 (slide 115)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Self-generated-name check" ← "C24 · addendum 15, item 2-11b"; tag ← "C24 (2-11b)"; "addendum-15 criterion" → "pre-registered criterion"

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 平局记 0.5；层范围 L16–L56。

**备查（不念）· 2026-11-25 事后检查（未预注册，探索性）：**
- **(i) 前置 token 不一致：** pred_first = 名字第一个 token 的前一位置。第 1 个名字（6,746 个）落在 prompt 最后一个 token（`</think>` 后的 "\n\n"）；第 2 个及以后（24,815 个）落在 ";"（24,687），其余 ".;" 112、" ;" 15、");" 1。补充 15 只写了"第一个人名 token 的前一位置"，未涵盖这一点。
- **(i) 拆开（原 probe，论文内 AUROC）：** 含第 1 个名字的对（1,200 对）0.57–0.70；只有第 2 个及以后的对（2,188 对）L16 0.545 [0.502, 0.585]、L24 0.542、L32 0.556、L40 0.510 [0.467, 0.549]、L48 0.542 [0.496, 0.584]、L52 0.598 [0.551, 0.641]、L56 0.586 [0.540, 0.626]（只有 L52–L56 高于 0.5）。只用第 1 个名字另训 probe：每篇只有一个第 1 名，没有论文内对，只能报合并 AUROC 0.66–0.78（L48 0.784 [0.755, 0.815]），与论文内 AUROC 不可比。
- **置信度基线放到同样的对上：** 只有后面名字的对，输出置信度 0.681 [0.640, 0.718]（全部对 0.711，含第 1 名的对 0.767）；(ii) − 置信度：L40 +0.070 [+0.025, +0.121]、L48 +0.069 [+0.020, +0.123]、L52 +0.066 [+0.020, +0.115]，其余层 CI 含 0；只用后面名字另训 probe 与置信度，L48 +0.083 [+0.036, +0.135]。(ii) 本身在含第 1 名的对上也偏高（L48 0.841 vs 只有后面名字 0.750）。
- **置信度扣掉"名字好不好写"：** 三个生成时置信量对名字特征（长度、cohort 全名频率（不含本篇）、知名度 4 项）的留出 R² 0.02–0.06（加位置 0.04–0.09）；残差上的置信度 0.711 → 0.695 [0.661, 0.725]（加位置 0.700），差 +0.016 [+0.003, +0.029]；名字特征单独 0.560。probe 相对残差置信度：L40 +0.084、L48 +0.087 [+0.049, +0.128]、L52 +0.076。正文结论不变。
- **拟合与评估：** probe 在 target + control 的全部 M/H 名字上合并拟合（5 折，作者团队分折），只在 target 论文上评估（论文内 M–H 对）；预注册原文只写了评估部分，"合并拟合"只写在分析脚本说明里。
- **prompt 格式：** 本实验用聊天模板自由生成（system + user 问题，enable_thinking=False），和 deck 其他实验的 "Authors:" 续写格式不同，数字不能横比。
- 出处：381_stage13/b2_gennames_b/summary_predfirst_split_20261125/split_all.csv；381_stage13/summary_later_pairs_20261125/report.md；381_stage13/summary_conf_resid_20261125/report.md；脚本 13_stage13/stage13_b2_gennames_b_{predfirst_split,later_pairs,conf_resid}_20261125.py。

## P125 · HTML v75 p125 · pptx S132–S133 (v22z) — Made-up names are not confused neighbours: half are not in the data

**要说的话（一句英文一句中文）**
This page asks, as an exploratory check, whether made-up names are confused neighbours, such as co-authors or authors from the same field.
这一页做一个探索性检查：编造的名字是不是混淆了的“邻居”，比如合作者或同领域作者？
We classified about 40 thousand made-up names: co-author of a true author, same-field author, another author in the cohort, or not in the data at all.
我们把大约 4 万个编造的名字分类：真作者的合作者、同领域作者、队列中的其他作者，或者根本不在数据里。
On the chart, each bar is compared with chance from shuffled names; about half, 50.4%, are not in the data at all, in none of the cohort's author lists.
图上每根柱子都和打乱名字得到的机会水平比；大约一半，50.4%，根本不在数据里，不在队列任何一篇论文的作者名单上。
Co-authors make up only 4%, against 1.3% by chance.
合作者只占 4%，机会水平是 1.3%。
One more small check: fewer than one in a hundred of the names that are not in the data look like a misspelling of a true author.
再补一个小检查：不在数据里的这些名字，像是真作者名字拼错的不到百分之一。
So made-up names are not near-misses. Next, a summary of the token line.
所以编造的名字不是“差一点就对”。下一页小结 token 这条线。

**备查（不念）· 上一版讲稿本页全文（原第 P93 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** 探索性（未预注册）：用标签包里的开放回忆答案（贪心），共 40,219 个编造名字，分布在 8,872 篇论文中。每个名字按先匹配先归类：真作者的合作者 → 同领域作者 → 队列中其他作者 → 不在数据中；机会水平 = 在领域内打乱名字（20 次）。团队 bootstrap。

**关键数字和 CI：**
- 合作者 4.0% [3.0, 5.2]（机会 1.3%）；同领域作者 20.2% [19.4, 21.0]（机会 22.6%）；队列其他作者 25.4% [24.8, 26.0]（机会 25.7%）；不在数据中 50.4% [49.0, 51.7]（机会 50.5%）。
- target − control：合作者（姓 + 首字母）−0.027 [−0.039, −0.015]；合作者（全名）+0.000 [−0.000, +0.000]；合作者（罕见姓）+0.000 [−0.001, +0.001]；不在数据中（姓 + 首字母）+0.063 [+0.043, +0.082]。
- 局限：只用原标签包的开放回答（贪心）；"不在数据中"指不在 9,108 篇队列的作者名单里。
- n = 8,872 篇，40,219 个可归类名字（target 4,578 / control 2,187 篇）。

**结论状态：** 探索性（未预注册）：邻居混淆假说不成立（不支持）。大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）；合作者只占 4.0%（随机 1.3%）；用全名匹配时 T − C 约 0。

**过渡：** 汇总 Stage 10–13 学到的东西。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{share}_c=\#\{\mathrm{made\text{-}up\ names\ in\ class}\ c\}/\#\{\mathrm{made\text{-}up\ names}\}$；② n = 8,872 papers, 40,219 names；③ share ≈ chance: made-up names are not near misses；原 “How computed” 段：How computed: each fabricated name is classed (first match): co-author of a true author → same-field author → other cohort author → not in the data; chance = names shuffled within field (20×). 8,872 papers, 40,219 names, team bootstrap.；原出处行：391_groups/summary_fabricated_20261114/ (report.md, class_shares_by_group.csv) · 14_groups/fabricated_names_20261114.py；方法细节移到备用页 B20 (slide 115)。

**备查（不念）· 2026-11-25 事后检查（未预注册，探索性）：**
- **删除的便签：** 原页底部便签 "50.4% not in the data, vs 50.5% for the shuffled baseline" 已删（用户批准）：一个名字在不在作者库里与配哪篇论文无关，打乱前后必然相同，没有信息量。同一对比也已从柱子标签、Result ①、主 PPT S133 和 leader 第 66 页的文字里去掉（用户批准）；各柱上的随机刻度保留，它是整张图的读数基准（合作者 4.0 vs 1.3、同领域 20.2 vs 22.6、其他作者 25.4 vs 25.7 都要靠它判断高低）；本页“上一版讲稿全文”里的旧说法作为历史记录保留。
- **拼错的真名（编辑距离）：** 20,286 个"不在数据里"的编造名，对 9,108 篇作者库求最近名字（姓 + 首字母须一致 / 全名 / 只看姓）。距离 ≤ 2 且最近的就是本篇真作者：全名 0.07%（15 个）、姓 + 首字母 0.13%（27 个）、只看姓 0.63%（128 个）；打乱论文标签 200 次（全局 / 同领域）分别 0.003% / 0.045% / 0.09%，p < 1/200。高于随机，但最多占"不在数据里"的 0.6%、全部编造名的约 0.3%；结论不变。约一半像真拼错（Johengen→Johengren、Wiig→Wiik、Kato→Katoh），其余是短姓巧合（Xu/Lu）。与本篇无关的最近距离（姓 + 首字母）1 步 41%、2 步 38%、≥3 步 21%，反映的是名字空间的密度。
- **匹配规则（Stage 10 匹配器，原样）：** 小写；NFKD 后丢弃非 ASCII（é→e、ü→u）；非字母→空格；连字符拆成词，姓 = 最后一个词；只比姓 + 名的第一个首字母（中间名不比）；名在前、姓在前两轮，一对一，按真作者顺序。
- **已知漏判：** Müller / Mueller（ue 不折叠）；Jr. / III 等后缀被当成姓；ı、ø、ß、ł 等无分解形式的字母被丢掉；复姓只写一段；前缀连写（Vanderberg）；昵称或首字母错（规则有意如此）。按 2-11b rev3 规则重查：0.4%（85 个）可匹配到作者库，其中 3 个是本篇真作者（Charles A. Janeway Jr.、L Joseph Melton III、C. Y. Yildirim / C. Yıldırım），影响可忽略。2-11b 预注册在同一批回答上：35,887 项中 8 项标签改变，1 项 H→M。
- 出处：391_groups/summary_fabricated_editdist_20261125/report.md；脚本 14_groups/fabricated_editdist_20261125.py。

## pptx S117（仅主 pptx，HTML deck 无对应页）— Exploratory: recognised but cannot say

**要说的话（一句英文一句中文）**
This page collects four exploratory looks at recognised but unsaid papers.
这一页汇集了关于“认得但说不出”的四个探索性观察。
The first name token often loses to another initial or a common given name; writing needs far more citations than recognising; and about half of the made-up names are not in the data.
名字的第一个 token 常常输给另一个首字母或常见的名；写出需要的引用远多于认出；编造的名字大约一半根本不在数据里。
All four are descriptive clues, later followed up by locked tests.
这四项都是描述性线索，后来都用锁定检验做了跟进。

**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**
（主 pptx 当前页码：S128；HTML deck 无对应页。）

【探索性】四项都只用已有数据，事后、描述性。① 第一个决策：真第一作者首 token 排前 5 的比例 A 0.298 [0.283, 0.312]、B 0.249；首字母开头 0.361、名开头 0.099；只有 6.5% 的 A 组论文是真标题下进前 5、换任何假标题都掉出前 5；赢家：另一个首字母 53.6%、常见的名 19.3%、真合作者 16.5%。② 曝光量：认得出约 40 次引用 [36, 44] 达到 50%；写得出 64 次引用以内 < 0.05，最高档 0.574；内部 target − control 在最低档已有 +0.189 [0.153, 0.227]，10 档合并 +0.207 [0.196, 0.220]。③ 编造名：合作者 4.0%（同领域打乱基线 1.3%），但 95% 是常见姓；罕见名字版 0.1%，与随机一致；约一半在数据集中不存在。④ A 组内：R(L48) 斜率 +0.031 [−0.312, +0.413]、R(L52) +0.004 [−0.133, +0.149]，分母 +0.690 [+0.391, +0.992]。
【2026-11-15 更新】确认性检验（补充 16）已全部完成，角标为“D supported · B supported (F4)”。D（名字链条，补充 16，锁定确认性检验，最终结果）：支持。给出一位真实合作者的名字，会提高其余真作者的分数（G_A(1) +0.167 [0.147, 0.185]，Holm 校正后 p = 0.0025）；这个效应大部分不针对标题（真标题 − 假标题 +0.012 [−0.001, +0.025]），认得出和认不出的论文相近（A − B −0.019 [−0.045, +0.007]）。A 组中，至少再写对一位作者的论文比例从 1.5%（给出对照第一作者）升到 11.8%（给出真第一作者）。C 组统计功效低。〔391_groups/summary_a16_20261115_tinytest/report.md、d_contrasts.csv、d_levels.csv、d_gen.csv；D 全部分片 1,428 篇〕B（输出格式，补充 16，锁定确认性检验，最终结果）：只在 F4 上得到支持：提示里给出第一作者名的首字母时，认得出的论文写对第一作者姓的比例更高（比 B 组多 +0.085 [0.047, 0.124]，Holm 校正后 p = 0.0025）；列表或只写姓的格式没有显著帮助。前提：首字母是在提示里给出的，所以这是第一步之后的帮助，不是模型自己找到的。次要结果：F4 的 Δ_A +0.103 [0.078, 0.129]；F2（只写姓）DiD +0.032（Holm 校正区间 −0.012, 0.076），F1（姓在前的列表）+0.022（−0.012, 0.055），F3（只写第一作者的姓）−0.007；没有一种格式提高编造率（F1 空答较多）。〔391_groups/summary_a16_20261115/report.md、holm.csv、b_main.csv、b_rates.csv、b_fab.csv；B 全部 30 个分片 1,500 篇；+0.085 与 F1–F3 的区间为 Holm 校正区间，Δ_A 为普通 95% 区间〕
【公式与样本量（v18）】面板 3：share = 某来源的编造名数 ÷ 全部编造名；40,219 个编造名、8,872 篇（391_groups/summary_fabricated_20261114/report.md，同 leader deck）。其他面板未加。
【2026-11-18 更新（v19）】F（面板 2，曝光门槛）已由补充 19 确认（2026-11-17 锁定，已看过数据后的锁定 = post hoc lock）：认得出 c50 = 40 [36, 44] 次引用，写得出 c50 = 11,038 [8,172, 15,607]，ρ = 276 [203, 390]，区间 > 1 → 确认；引用档内 T − C 随曝光增加，斜率 +0.030 [+0.014, +0.044] / 10 倍引用。前提：写得出的门槛接近引用范围上端（9,108 篇中 16 篇超过 11,038）。详见第 97 页；状态角标改为 "Exploratory · F confirmed (add. 19) · D, B (F4) supported"，面板 2 旁加了小注。D 的解读（措辞更正，结论不变）：效应存在（G_A(1) +0.167 [0.147, 0.185]），但与标题无关（真 − 假标题 +0.012 [−0.001, 0.025]，删掉标题 +0.223 [0.201, 0.247]），A − B 无差别（−0.019 [−0.045, 0.007]；B 组 +0.186 [0.168, 0.204]，C 组 +0.124 [0.090, 0.156]，227 篇）→ 是合作者网络的关联，不是对这篇论文的记忆。C（面板 3）方法与敏感性见第 98 页：不支持。〔391_groups/summary_exposure_prereg19/report.md；summary_a16_20261115/d_contrasts.csv；summary_fabricated_20261114/report.md〕
【2026-11-18 整合（v20）】本页仍在附录（探索性汇总）。页码改为 96；面板 2 旁的小注改为指向第 30 页（补充 19 已移入 Line A）；面板 3 的方法见第 93 页。
【2026-11-19 整合（v21）】本页从附录移到第 94 页（紧跟"编造的名字"一页，面板 3 用的是同一批数据）；角标从"Appendix · exploratory"改为"Lines A–D · exploratory"，"探索性、事后、描述"的说明留在页面上；底部加了一行导引。内容和数字没有改动。
【2026-11-19 整合（v22）】页码引用顺延：第 82 页起新增两页（补充 18b 第 3、2 项），原第 82 页起各页 +2。
【2026-11-20 整合（v22e）】页码引用顺延：第 90 页起新增两页（补充登记 20，虚构标题），原第 90 页起各页 +2。

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 同领域内打乱名字 20 次作为机会基线。

## P126 · HTML v75 p126 · pptx S134 (v22z) — What we saw: “Which token carries it?”

**要说的话（一句英文一句中文）**
This page sums up which token carries the signal.
这一页小结哪个 token 承载信号。
The small samples saw the recognition gap on the later tokens, not the first.
小样本看到认得的差距在后面的 token 上，不在第一个。
The full cohort explained why: 73% of names start with an initial, which carries little, so the surname is a later token; full given names carry as much as surnames.
全队列解释了原因：73% 的名字以首字母开头，而首字母带的信息很少，所以姓本身是后面的 token；完整的名带的信息和姓一样多。
Co-authors help, but through the network, and only the first-initial hint helps writing.
合作者有帮助，但那是网络关联；而能帮助写出的只有首字母提示。
That closes the background. Next, the decisive tests: who writes the name.
背景块到此结束。下面是决定性检验：谁写出名字。

**备查（不念）· 上一版讲稿本页全文（原第 P61 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 小样本：A−B 在后续 token 上（+0.021），不在第一个 token 上（+0.001）（7.1，20 对）；遗留问题：这是 teacher forcing、首字母还是姓氏造成的？全队列：73% 的名字以首字母开头（24,739 / 33,780；§6.7），而首字母携带的信息很少；完整的名和姓氏携带的信息一样多，还能帮助预测姓（+0.22）（final L63；§6.7）；信息从标题流向名字位置（主要在 L40–L50），部分经由标题后的 token；前面的合作者让后面的更容易，标题的作用随之变小；答案格式（补充 16）：给出名首字母（F4）对认得出的论文帮助更大，A − B +0.085 [0.047, 0.124]（只通过 F4）；合作者链（补充 16）：+0.167，不是 title-specific，A ≈ B → 网络关联 → 第 59–60 页。

**关键数字：** Stage 12 P1（已完成）做了单位置 patching：名字位置承载信号（L52 +0.85），单独的冒号很少（+0.17）（P1，1,186 篇；P1_patch_pos.csv）。n = 20 对（1–9）· 9,108（10–11）· 1,186（P1）· 1,200 / 1,428（补充 16 B / D）。

**结论状态：** 名字格式解释为定论；补充 16 为预注册判据成立（B 只通过 F4；D 效应存在但非论文特异）。一句话：7.1 的谜题可以用名字格式解释。pilot 的"后续 token"结果主要是格式效应：对 "S. Bree" 这种名字，姓本身就是后续 token。

**过渡：** 用一个比喻把四条线串起来：钥匙和书架。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$；② n = 20 pairs (1–9) · 9,108 (10–11) · 1,186 (patching) · 1,200 / 1,428 (format / chain tests)；③ spec > 0: the true title ranks the author higher than false titles；原公式框：spec = nlr true − mean 5 nlr false n = 20 pairs (1–9) · 9,108 (10–11) · 1,186 (P1) · 1,200 / 1,428 (add. 16 B / D)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(24,739 / 33,780; §6.7)
- 出处（原在幻灯片上）：(final L63; §6.7)
- 出处（原在幻灯片上）：(P1, 1,186 papers; P1_patch_pos.csv)

**备查（不念）：**
- 原写 “Answer format (add. 16)”、“Co-author chain (add. 16)”、“Stage 12 P1 (done)”：add. 16 = 生成测试补充登记；P1 = Stage 12 单位置 patching

## P127 · HTML v75 p127 · pptx S135 (v22z) — The MLPs, not attention, write the author signal in L57–L61

**要说的话（一句英文一句中文）**
This page asks who writes the author signal in layers 57 to 61: attention or the MLPs?
这一页问：第 57 到 61 层的作者信号是谁写出来的，注意力还是 MLP？
We replace one component of one layer with its average from other papers, called mean ablation, and see how much of the paper signal is lost, under a rule locked before the run.
我们把某一层的一个组件换成它在其他论文上的平均值，这叫均值消融，再看论文信号损失多少，规则在运行前锁定。
By the paper signal we mean the extra score the true title gives the true authors, compared with a false title.
我们说的论文信号，就是真标题相对假标题，给真作者多出来的那部分分数。
On the chart, a loss above zero means that component writes part of the signal; each MLP layer from 57 to 61 removes about 11 to 14% of it, while attention removes about nothing.
图上损失大于 0 表示这个组件写出了一部分信号；第 57 到 61 层的每一层 MLP 都去掉约 11% 到 14%，注意力几乎为 0。
The difference, MLP minus attention, is about 0.04 at every one of the five layers.
MLP 减注意力的差值，在这五层每一层都约是 0.04。
So the late MLPs write the name; this is settled. Next, whether a stronger arrived signal would help.
所以是后面的 MLP 写出名字，这是定论。下一页看更强的到达信号有没有帮助。

**备查（不念）· 上一版讲稿本页全文（原第 P77 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** （接第 51、76 页：最陡的上升在 L57–L61。）补充 18b 第 4 项（2026-11-17 锁定）：每次只对一层的一个组件（attention 或 MLP）做均值消融，作用于提示尾部和所有名字输入，参照均值取自 586 篇其他论文；600 篇。loss(c, l) = S(none) − S(c 在 l 层被消融)，S = nlr(true) − mean_k nlr(false_k)（最终输出）；判据：配对 CI 下 loss(MLP) − loss(attn) > 0。

**关键数字和 CI：**
- S(none) = 0.328 [0.308, 0.348]。
- MLP 损失：L57 +0.040、L58 +0.037、L59 +0.039、L60 +0.045、L61 +0.041（各占 S 的 11–14%）；attention 约 0（≤ 0.0012）。
- MLP − attn：L57 +0.039 [+0.032, +0.046]；L58 +0.037 [+0.031, +0.044]；L59 +0.039 [+0.031, +0.046]；L60 +0.046 [+0.038, +0.053]；L61 +0.041 [+0.033, +0.048]；平均 +0.040 [+0.036, +0.045]。
- 这个差值的 target − control：+0.025 [+0.017, +0.034]。
- 参照 P2（patching，≤ L56）：MLP L52 0.181，L56 0.226。
- 局限：均值消融，每次只动一层一个组件（不含联合效应）；target 论文损失更多；自检 WARN，排名一致率 0.627 / 0.527（bf16），按规则继续。
- n = 600 篇（300 target + 300 control）。

**结论状态：** 定论（锁定判据成立，5/5 层满足）。

**过渡：** 名字是后段的 MLP 写出来的。那说不出，是不是因为到达的信号太弱？下一页直接把它放大试试。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{loss}=S(\mathrm{none})-S(\mathrm{ablated})$；② n = 600 papers (300 target + 300 control)；③ loss > 0: removing this part hurts the signal；原 “How computed” 段：How computed: loss = S(none) − S(ablated); one layer’s attention or MLP output at the tail and name inputs replaced by a fixed reference mean (586 other papers); criterion: paired CI of loss(MLP) − loss(attention) > 0. 600 papers.；原出处行：381_stage13/summary_a18b_item4/ (item4_table.csv, item4_criterion.csv) · config/prereg_addendum18b.md；方法细节移到备用页 B17 (slide 112)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："Late-layer ablation (pre-registered, locked)" ← "Addendum 18b item 4 (locked 2026-11-17)"
- 图内公式框里的判据 / 说明（移出幻灯片）：S = nlr(true) − mean_k nlr(false_k), final output;  criterion: loss(MLP) − loss(attn) &gt; 0

**备查（不念）：**
- 原写 “reference P2 (patching, ≤ L56)”：P2 = Stage 12 注意力 / MLP patching

**备查（不念）· 原备用页 B13–B21 迁入（2026-11-24）：** 参照均值取自另外 586 篇论文。

## P128 · HTML v75 p128 · pptx S136 (v22z) — Strengthening the arrived information does not make the model write the author

**要说的话（一句英文一句中文）**
This page asks: is the arrived information simply too weak?
这一页问：是不是到达的信息太弱了？
Under a rule locked before the run, we add more of the paper's own title signal to the state, at layers 48 or 52, with three strengths, on 1,200 papers.
按运行前锁定的规则，我们在第 48 或 52 层，用三种强度把论文自己的标题信号再加进状态里，共 1,200 篇论文。
On the chart, G near zero means the injection does not help; across the six settings the gain is between about minus 1 and plus 0.5 points, and none passes.
图上 G 接近 0 表示注入没有帮助；六种设置下，增益在约负 1 到正 0.5 个百分点之间，没有一个通过。
Pushing harder even hurts: at the highest strength the true name falls.
推得更用力反而有害：最高强度下真名字的分数下降。
So strengthening the arrived information does not make the model write the author. Next, whether some names rise and are then pushed down.
所以加强已到达的信息，并不能让模型写出作者。下一页看有没有名字先上升、再被压下去。

**备查（不念）· 上一版讲稿本页全文（原第 P78 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**实验设计：** （接第 77 页：L57–L61 由 MLP 把名字写出来。这里问：是不是到达的信号太弱？）补充登记 21（2026-11-21 13:18 锁定，sha256 bdbf80bd…，锁定前没有任何真模型运行）。1,200 篇：A 600（认得出 · R0）、B 600（认不出 · R0），补充 16 B 样本。真标题提示里，在提示尾部 L48 或 L52 的块输出加 β·Δ，Δ = 这篇论文真标题状态 − 5 个假标题状态均值（模型自己算出的标题特异分量，不是把答案塞进去），β = 1、2、4。对照（同范数）：另一篇论文（同领域、同引用档）的 Δ、随机方向；只含意思的 Δ_fict 只在补充 20 重叠的 94 篇 A 上（次要）。主指标：A 组开放生成写对 ≥ 1 位作者全名的比例；G = rate(own) − rate(none)，S = rate(own) − rate(other)；团队整群 bootstrap 2,000 次，Holm 校正 6 格。
先讲怎么做（指着左图的横轴：两层 × 三种放大倍数，每组三根柱子：自己的 Δ、另一篇论文的 Δ、随机方向），再讲结果。

**关键数字和 CI：**
- 不注入时 A 组 3.8%；自己的 Δ 最好一格 4.3%（L52 β1），L52 β4 反而 2.8%；另一篇论文的 Δ（L52 β4）1.7%。
- G = 自己 − 不注入：6 格 −0.010 到 +0.005，Holm 区间都含 0。
- S = 自己 − 另一篇：−0.002 到 +0.020，最大 L52 β2 +0.020 [0.003, 0.037]（未校正），Holm p 0.15。
- 右图（teacher-forcing，最终输出）：自己 − 不注入 L48 β4 −0.054 [−0.061, −0.047]，L52 β4 −0.102 [−0.113, −0.092]；放大另一篇论文的 Δ 也一样往下走（自己 − 另一篇 L52 β4 +0.012 [−0.002, +0.026]）：一般性损伤，不是论文特异的帮助；B 组相同。
- 检查：β = 0 时与不注入逐 token 相同；范数匹配误差 ≤ 5e-7；与 Stage 10 名次逐行一致比例 0.69 < 0.75（WARN，平均 |Δlog10 名次| 0.009），按规则继续。第一次 gate 只覆盖 30 个分片中的 24 个（953 篇，结论相同），补齐后以 1,200 篇为准。
- 【公式】G = rate(own) − rate(none)，S = rate(own) − rate(other)；Δ = mean log10(1/rank_true)_inj − mean log10(1/rank_true)_none。
- n = 1,200 篇（600 A、600 B）。

**结论状态：** 确认（补充 21，锁定的确认性检验）：不支持——说不出不只是信号太弱；加强已经到达的信息不能让模型写出作者，瓶颈在后段把信息转成名字这一步（C37；与 C29、C30 一致）。

**过渡：** 回到 Stage 11 的时间进程：原来只用了 false_0，换成 5 个假标题还成立吗？

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** 391_groups/summary_a21/ (rates.csv, primary.csv, tf.csv) · prereg_addendum21.md sha256 bdbf80bd…。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $G=\mathrm{rate}(\mathrm{own})-\mathrm{rate}(\mathrm{no\ injection})$ · $S=\mathrm{rate}(\mathrm{own})-\mathrm{rate}(\mathrm{another\ paper})$；② n = 1,200 papers (600 A, 600 B)；③ G ≈ 0: injection does not help / S > 0: the gain is this paper’s own signal；原公式框：[formula] · [formula] [formula]；原公式框：[formula] [formula]；原公式框：G ≈ 0: injection does not help；原公式框：Δ。

## P129 · HTML v75 p129 · pptx S137 (v22z) — Late suppression in a subgroup

**要说的话（一句英文一句中文）**
This page asks whether the average hides papers whose true name rises after layer 56 and is then pushed down.
这一页问：平均值是不是掩盖了一些论文——真名字在第 56 层之后先上升，然后又被压下去？
We follow each paper's true name with the logit lens, and see which layer parts push it up or down at the output.
我们用 logit lens 跟踪每篇论文的真名字，看哪些层的哪些部分在输出端把它往上推或往下压。
On the chart, a share above zero means some papers rise and then fall; that happens in 12.8% of recognised papers against 9.1% of unrecognised ones.
图上比例大于 0 表示有些论文先升后降；认得的论文里有 12.8%，认不得的有 9.1%。
The difference passed the locked rule, but its lower bound is just above zero.
这个差值通过了锁定规则，但下界只是刚刚高于 0。
So there is a late-suppression subgroup, a little more often in recognised papers. Next, whether the problem is the direction in which the pair was learned.
所以存在一个后期压制的子组，在认得的论文里略多一些。下一页看问题是不是出在学习这对关系的方向上。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Late suppression in a subgroup Now asking: the average true-name rank keeps rising to the output; does it hide papers whose name rises after L56 and is then pushed down? locked · supported late-suppression subgroup, more often in recognised papers (just above the bound) · evidence type: readout ◉ (logit lens + direct logit attribution) DLA > 0: this layer part pushes the true name up at the output · share > 0: some papers’ true name rises after L56, then falls by the output 1 Result: rise-then-fall in 12.8% of target vs 9.1% of control papers; T − C +0.037 [+0.002, +0.073] → subgroup more frequent when the paper is recognised. 2 Control: over all name tokens the share is about the same in both groups (T − C −0.010 [−0.021, +0.001]); the T − C lower bound is just above 0 . So (this slide): the name is written by the late MLPs (slide 122), and in about 1 in 8 recognised papers it rises after L56 and is then pushed back down — one concrete way “recognised but not said” fails at the writing step locked

数字出处：27_v67/fragments/part56_numbers.md

## P130 · HTML v75 p130 · pptx S138 (v22z) — Direction asymmetry: not a reversal curse

**要说的话（一句英文一句中文）**
This page asks whether “recognised but not said” is a reversal curse: the pair learned only as authors to title, so recalling authors from the title runs the wrong way.
这一页问：“认得但说不出”是不是反转诅咒——这对关系只按“作者到标题”的方向学过，所以从标题回忆作者是在逆着走。
Under a locked rule, we scored both directions on the same papers: the title after the authors, and the authors after the title.
按锁定规则，我们在同一批论文上给两个方向打分：作者之后接标题，以及标题之后接作者。
On the chart, F above zero means the true authors make the true title more likely; for recognised papers it is far higher, about plus 0.44, so the association is present.
图上 F 大于 0 表示真作者让真标题更可能出现；认得的论文高得多，约 +0.44，所以这种关联是存在的。
But generating the title from the authors is slightly harder than recalling the authors from the title, by about 3 points; the locked reading is “reversed”.
但从作者生成标题，反而比从标题回忆作者稍难，大约差 3 个百分点；锁定判定是“反向”。
So the reversal curse does not explain it. Next, the verdict card for Part 6.
所以反转诅咒解释不了这个现象。下一页是第 6 部分的判定卡。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Direction asymmetry: not a reversal curse Now asking: is “recognised but not said” a reversal curse: the pair learned only in the direction authors → title, so recall from the title runs the wrong way? locked · not supported reading “Reversed”: authors → title is slightly harder · evidence type: behaviour (generation) + teacher-forced likelihood · F_id > 0: the true authors make this title more likely than another field’s authors do R2 > 0: authors → title is easier (what a reversal curse predicts) 1 Result: given the true authors, the true title is far more likely for recognised papers (A − B +0.443 [+0.373, +0.517]) — the association is present (forward likelihood). 2 Result: but generating the title from the authors is slightly harder than recalling the authors from the title (R2 −0.032 [−0.047, −0.016]): locked reading “Reversed”. Caveat: greedy decoding; one citation format; both success rates are low ; secondary: forward likelihood also predicts recognition beyond citations (+0.110 [+0.034, +0.187]). So (this slide): the reversal-curse explanation is not supported: the authors–title association exists, but writing either side out is hard, which points back to the writing step locked

数字出处：27_v67/fragments/part56_numbers.md

## P131 · HTML v75 p131 · pptx S139 (v22z) — Verdict card: the writing step

**要说的话（一句英文一句中文）**
This verdict card closes Part 6: why is a recognised author not written?
这张判定卡给第 6 部分收尾：为什么认得的作者写不出来？
The bottleneck is the late writing step: the MLPs of layers 57 to 61 write the name, and that is settled.
瓶颈在最后的写出这一步：第 57 到 61 层的 MLP 写出名字，这是定论。
More of the arrived signal does not help, and near the writer it disrupts rather than helps.
更多的到达信号没有帮助，靠近写出层时反而起干扰作用。
Storage direction is not the cause, a small subgroup is pushed down late, and only a hint of the first initial helps.
存储方向不是原因；有一个小子组在后期被压下去；只有首字母提示能帮上忙。
Next, the evidence matrix after Part 6.
下一页是第 6 部分之后的证据矩阵。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Verdict card: the writing step Now asking: what do the writing-step tests together say about why a recognised author is not written? Conclusion The bottleneck is the late writing step : the L57–L61 MLPs write the name (MLP − attention +0.040 [+0.036, +0.045], slide 122); more of the arrived signal does not help (slide 123) and near the writer disrupts rather than helps (slide 106); storage direction is not the cause: writing the title from the authors is slightly harder (slide 125). Evidence strength settled late MLPs write (locked criterion met at all 5 layers). locked · not supported strengthening the arrived information; reversal curse (reading “Reversed”). locked · supported direction-driven damage; late suppression in a subgroup (slide 124); first-initial hint 4.0% → 15.2% in recognised papers (slide 33). Open questions which heads or neurons push the name down in the subgroup; a first-token causal test; a second model. → So (this slide): read early, said late: the information reaches the names, and recall fails at the late writing step settled locked

数字出处：27_v67/fragments/part56_numbers.md

## P132 · HTML v75 p132 · pptx S140 (v22z) — Evidence matrix after Part 6

**要说的话（一句英文一句中文）**
This matrix shows every hypothesis after Part 6.
这张矩阵显示第 6 部分之后的全部假设。
The writing-step row is now filled: the late MLPs write, pushing does not help, and the reversal curse is ruled out.
写出这一行已经填上：后面的 MLP 负责写出，推一把没用，反转诅咒被排除。
All rows are now in: H1 revised, H2 meaning with one small exception, H3 supported, a parallel route, and a late writing bottleneck.
现在所有行都填好了：H1 修正，H2 是意思加一个小例外，H3 得到支持，路线是并行的，瓶颈在后期写出。
Next, Part 7: the summary.
接下来是第 7 部分：总结。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Evidence matrix after Part 6 Now asking: with Part 6 done, where does each hypothesis stand? H1 · does the middle know "what is asked"? (✓) “:” new question vs paper 4.7× (L4) → 2.2× (L48) descriptive s. 51 (✓) probe after the question change T 0.24–0.41 descriptive s. 49 ~ top lens word format words; title-dependent 28–64% descriptive s. 37 ~ format locking (+ checks) L56 = sink artefact; names default locked + exploratory s. 52 (✓) swap “:” at L56 author signal −0.03 locked s. 52 Verdict: downgraded: “:” follows the question; the format layer is not pinned down → s. 53 H3 · author info in the middle, not in vocabulary directions? ✗ author-prompt lens, mid layers −0.058 at L48 pre-registered s. 94 (✓) probe at the title +0.052 at L24 descriptive s. 93 ✓ same-scale probe vs lens L40 +0.021, L48 +0.062 locked s. 99 ~ "author" subspace swap passes, moves only ≈ 7% pre-registered s. 101 ~ direction of the difference spread; not on author axes exploratory s. 100 (✓) inject the author direction 2.5% → 9.7%; mainly write channel locked s. 105 Verdict: supported; small effect; correlational evidence → s. 107 H2 · does the middle know "which paper"? ~ paper facts at the title readable, inferable from text descriptive s. 16 ~ same title, other question · copy ceiling: L4 cosine 0.998 exploratory s. 77 ~ paraphrased title text-only model reaches 60% pre-registered s. 71 ✗ made-up title meaning 75%; real title +0.106 locked s. 73 ✗ rare vs common words 0.162 vs 0.027 locked s. 80 ✗ recognised / citation check not larger; smaller if cited more locked s. 78 ✗ variance split identity ≈ 0 locked s. 79 ✗ "paper facts" subspace swap R_id 0.004 pre-registered s. 101 (✓) L8 surname test T1 +0.046; T2/T3 marginal; ½ topic locked s. 81 Verdict: not a general paper identity, with one small locked exception → s. 82 Writing step (the bottleneck) ✓ L57–L61 MLPs write MLP − attention +0.040 settled s. 122 ✗ strengthen the arrived signal unchanged ("too weak" refuted) locked s. 123 ✓ give the first initial 4.0% → 15.2% locked s. 33 (✓) late suppression about 1 in 8 papers locked (just past bound) s. 124 ✗ reversal curse (direction) −0.032 (refuted) locked s. 125 Verdict: the bottleneck is the late writing step, not signal strength → s. 126 ✓ supports (✓) partly ✗ weakens ~ cannot separate strength: settled locked pre-registered descriptive exploratory s. = slide So (section): read early, said late — the summary (Part 7) walks through the whole route on one map.

数字出处：27_v67/fragments/part56_numbers.md

# Part 7 · Summary (133–173)

## P133 · HTML v75 p133 · pptx S141 (v22z) — The whole story on one map (all six stages lit)

**要说的话（一句英文一句中文）**
This page opens the summary with the whole story on one map: the prompt tokens run across, the 64 layers run up.
这一页用一张图打开总结：横着是提示词的每个 token，竖着是 64 层。
Follow the blue pipes from the bottom: the input words set the states up to layer 4, the title is read from layer 24, and by layer 52 it has been delivered to the name positions.
从下往上跟着蓝色管道走：到第 4 层为止，状态由输入的字决定；从第 24 层起读标题；到第 52 层，标题已经送到名字位置。
Then the paper information waits at the names as something a probe can read but a lens cannot, and only at layers 57 to 61 do the late MLPs write the name.
然后论文信息停在名字位置，probe 读得出、lens 读不出；直到第 57 到 61 层，后面的 MLP 才把名字写出来。
The padlock marks where it gets stuck: at writing, hardest at the first token of the name.
挂锁标出卡住的地方：在写出这一步，名字的第一个 token 最难。
Read early, said late: the title is read and delivered by about layer 52, the name is written only at layers 57 to 61, and recall stalls there.
读得早，说得晚：标题大约在第 52 层读完、送到；名字到第 57 到 61 层才写，回忆就卡在那里。
Next, one page on the phenomenon itself, then the same map six times, one stage lit at a time.
接下来先用一页看现象本身，再把同一张图看六遍，每次只点亮一段。

**备查（不念）· 本页幻灯片全文：** The whole story on one map (all six stages lit) Now asking: putting every result together, where does recall of a paper’s authors break? [figure: step0 all] So (section): read early, said late: the title is read and delivered by about L52; the name is written only at L57–L61, and recall stalls there. summary of the six stages; details on the stage slides

**备查（不念）· 证据强度：** descriptive（页底标签“summary of the six stages; details on the stage slides”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（总的拼图）

- **推进故事的**：
  - 认得但说不出是一个很大的曝光差距（现象）；
  - 标题在 L52 前沿多层并行送到名字位置（路线）；
  - 送去的是意思和具体用词（H2 第二批）；
  - 作者信息在中间层能被 probe 线性读出、lens 读不出；效应小，属于相关性证据，不能说明模型存着自己的知识却没用上（H3）；
  - 名字由后期 MLP 写出，卡在写出这一步，名字开头最难（写出阶段）。
- **推翻的（原来的说法站不住）**：中间层存答案格式（H1 原形式）；"格式在 L56 才固定（锁定）"，现改为"锁定规则给 L56，但受切断 sink 影响，固定层定不下来"（H1 第二批）；中间层存一般意义上的论文身份（H2 原形式）；信号太弱。
- **排除的替代解释**：
  - 字面重叠（姓氏不是直接出现在标题里）；
  - 主题先验（姓氏信号里约一半是主题，扣掉后仍剩一小块）；
  - 反转诅咒；
  - 认得的论文读得更早（只是大小不同）；
  - 编造名是记混的近邻；
  - 统计方法造成的假象。
- **保留为小例外的**：L8 起的姓氏信号（T1 稳健，T2、T3 刚过线）。
- **还不确定的**：
  - 格式在哪层固定，年份 / 领域无法解读；
  - 姓氏例外的文本基线偏弱；
  - H3 只有相关性证据：L48 上 lens 的 target − control 为负、probe 为正，方向相反，没有解释；
  - 后期压制刚过界；
  - lens 拟合稳定性没检验过；
  - 只在一个模型上做过。

**一句话**：读得早，说得晚。瓶颈在最后的写出这一步，不在读取。

## P134 · HTML v75 p134 · pptx S142 (v22z) — Before the map: recognised but not said — a large exposure gap, not just guessable names

**要说的话（一句英文一句中文）**
Before the map, one page on the phenomenon itself: the model recognises papers whose authors it cannot name.
在看地图之前，先用一页讲现象本身：模型认得出这篇论文，却说不出它的作者。
On the left, the share of papers recognised and the share written both rise with citations; recognising reaches one half at about 40 citations, writing at least one true author needs about 11,000.
左边，认得的比例和写出的比例都随引用数上升；认得在大约 40 次引用时达到一半，写出至少一位真作者要大约 11,000 次。
That is about 276 times more exposure, but the rule was locked after seeing the estimates, so only 'more than one' is confirmed.
差不多要多 276 倍的曝光，但这条规则是看了估计值之后才锁定的，所以只确认了“大于 1”。
On the right: is this just guessable names? Without the title, the name prior is only about 19 percent of the recognised-minus-other gap; the rest is specific to the paper.
右边：这会不会只是容易猜的名字？去掉标题后，名字先验只占“认得减认不得”那个差距的约 19%，其余是这篇论文特有的。
And papers where the model wrote no true author at all give the same picture, 0.20 against 0.21 for all papers.
只看模型一个真作者都没写出的论文，结果也一样，0.20 对比全部论文的 0.21。
So recognised but not said is real: a large exposure gap, not explained by guessable names. Next, the six stages one at a time.
所以认得但说不出是真的：是一个很大的曝光差距，不能用容易猜的名字解释。接下来一次看一段，共六段。

**备查（不念）· 本页幻灯片全文：** Before the map: recognised but not said — a large exposure gap, not just guessable names Now asking: how large is the gap between recognising and writing, and is it more than guessable names? [figure: step0b phenomenon] So (this slide): recognising needs about 40 citations, writing about 11,000 (ρ ≈ 276; only ρ > 1 is confirmed); guessable names are only about 19% of the gap, and papers with no author written give the same picture. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法）。

**备查（不念）· 图中数字：** 左：c50 40 [36, 44] vs 11,038 [8,172, 15,607] 次引用；ρ = c50(write) / c50(recognise) = 276 [203, 390]；约 25% 猜测底；n = 9,108 篇；规则在看到估计值后锁定 → 只确认 ρ > 1。右：name prior +0.047 [0.031, 0.062] vs true title +0.247（约 19%）；R0 +0.199 vs 全部 +0.207；对照：去掉标题时真作者列表看起来最真的比例 0.26，机会水平 0.25。
**备查（不念）· 出处：** 第 7、24、26、41、68 页（选择题测试、曝光阈值、R0 重算、分组比较、名字先验）；27_v67/experiment_contribution.md S1。

## P135 · HTML v75 p135 · pptx S143 (v22z) — Step ① of 6 · L0–L4: the input words decide almost everything

**要说的话（一句英文一句中文）**
Step one lights only the bottom band, layers 0 to 4; everything else is faded.
第一步只点亮最底下一段，第 0 到 4 层，其余都淡掉。
Here the model has done almost no computing yet, so the state is set by the input words themselves.
这里模型几乎还没做计算，所以状态由输入的字本身决定。
The same title under two different questions already gives almost the same state at layer 4; even the bare word embedding, or a BERT model that knows no papers, finds the paper again every time.
同一个标题放在两个不同问题下，第 4 层的状态已经几乎一样；就连不经过模型的词嵌入、或者完全不认识论文的 BERT，也每次都能把论文找回来。
So at this level we cannot tell meaning from paper identity, and layer 4 becomes the literal baseline that every later test is measured above.
所以在这一层分不开意思和论文身份，第 4 层就成了字面基线，后面每项检验都在它之上比较。
The bar at the bottom says it: the input words decide almost everything.
底下那条结论就是：输入的字决定了几乎一切。
Next, layers 4 to 24.
下一步：第 4 到 24 层。

**备查（不念）· 本页幻灯片全文：** Step ① of 6 · L0–L4: the input words decide almost everything Now asking: what happens in L0–L4, position by position? [figure: step1 L0 L4] So (this slide): L0–L4: the input words decide almost everything. cannot separate meaning from identity here

**备查（不念）· 证据强度：** descriptive（页底标签“cannot separate meaning from identity here”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L0–L4 段）

**L0–L4：输入的字决定了几乎一切**

在最底层，模型还没做多少计算，状态主要由输入的字本身决定。
- **问题词和冒号**：三种问题（问作者、问年份、问领域）的提示里，最后一个 token 在第 0 层完全相同，这个位置在三种问题下没有差别 [L4 基准审计 · 仅在探索性结果文件中 · exploratory]。但冒号位置从一开始就跟着问题变：在 L4，换一个问题时冒号状态移动 0.443，换一篇论文只移动 0.094，是 4.7 倍；这个大比值主要来自问题的字面不同 [冒号：换问题 vs 换论文 · descriptive]。
- **标题 token**：同一个标题在不同问题下，L4 的状态余弦已经是 0.9976（两篇不同论文是 0.45），跨问题找回同一篇论文的成功率在 L4–L44 都是 1.000 [天花板审计 · exploratory]。只取最后一个标题 token 的词嵌入、不经过模型，身份指数 I 就有 0.998 [0.998, 0.999]；不认识任何论文的 BERT 从第 1 层起找回率也是 1.000 [L4 基准审计 · 仅在探索性结果文件中 · exploratory]。
- **为什么 L4 是字面基准**：一模一样的字给出一模一样的状态，天花板来自输入的字，与模型是否认识论文无关。所以后面所有"中间层是否超出字面"的比较，都拿 L4 作基线，比如改写标题的差距用 G′ − G′(L4) 来算 [改写标题 · pre-registered + exploratory]。
- **被推翻的**：早期把"换问题后标题状态不变"读成支持论文身份；天花板审计（救场）把它改为"分不开意思和身份"[天花板审计 · exploratory]。
- **不确定**：这一段本身没有缺口，但它限制了所有只换问题的检验：这些检验从 L4 起就到顶。

## P136 · HTML v75 p136 · pptx S144 (v22z) — Step ② of 6 · L4–L24: early read-in; the first traces of the title and of the first author

**要说的话（一句英文一句中文）**
Step two lights layers 4 to 24, the early read-in.
第二步点亮第 4 到 24 层，也就是早期读入。
At the colon, the state follows the question, not the paper: it moves about 4.7 times more when the question changes than when the paper changes.
在冒号位置，状态跟着问题走，不跟着论文走：换问题时移动的距离大约是换论文时的 4.7 倍。
At the title, the first title facts and the first author's token appear around layers 8 to 16, and a paraphrased title starts to be encoded beyond its wording from layer 8.
在标题位置，最早的标题信息和第一作者的 token 大约在第 8 到 16 层出现；改写过的标题从第 8 层起开始在字面之上被编码。
The one small reverse clue is a surname signal at layer 8: it survives a confirmatory test on about six thousand new papers, but it is small and about half of it is topic.
唯一的反向线索是第 8 层的姓氏信号：它在大约六千篇新论文的确认检验里站住了，但很小，而且大约一半来自主题。
Bottom line: early read-in, the first traces of the title and of the first author, a joint conclusion from several tests.
底下的结论：早期读入，出现最早的标题痕迹和第一作者痕迹，这是几项检验合起来得出的。
Next, layers 24 to 40.
下一步：第 24 到 40 层。

**备查（不念）· 本页幻灯片全文：** Step ② of 6 · L4–L24: early read-in; the first traces of the title and of the first author Now asking: what happens in L4–L24, position by position? [figure: step2 L4 L24] So (this slide): L4–L24: early read-in; the first traces of the title and of the first author. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L4–L24 段）

**L4–L24：早期读入，最早的标题信息和第一作者痕迹**

- **问题词和冒号**：冒号继续按问题组织。在冒号位置训练的领域 probe，换一种问题后只剩 0.24–0.41（L4–L52）[换问题后 probe 还能否用 · descriptive]。补充实验发现，冒号 62–92% 的注意力落在第 0 个位置；只要保留这个位置，从 L4 起人名答案类型就保持住 [格式锁定补充实验 · exploratory]。
- **标题 token**：标题信息和第一作者 token 最早在 L8–L16 出现 [层顺序 · descriptive]。在标题位置用 probe 读年份，R² 从 L16 的 0.38 开始上升，但这些属性能从标题文字推出来 [标题位置读论文属性 · descriptive]。改写标题后，状态与原标题的差距从 L8 起高于 L4 的水平，说明中间层开始在字面之上编码意思 [改写标题 · pre-registered + exploratory]。
- **唯一的反向线索**：把 L8 的标题状态搬进固定提问句"Paper: X / The first author of the paper is"，能解码出第一作者的姓。在 6,048 篇新论文上，扣掉同主题配对论文后仍有 +0.046 [+0.035, +0.056]；超过纯文本基线和认得的更大两项都刚过线；原始信号约一半来自主题 [L8 姓氏确认检验 · locked]。这是排除（来源检查砍掉字面重叠、主题配对砍掉主题先验）加救场（确认检验补上样本太小的主题配对）共同得出的锁定小例外。
- **标题位置的 probe**：在 L24，标题位置的 probe 已经能稍微分开认得和认不得（+0.052 [+0.018, +0.086]）[标题位置的 probe · descriptive]。
- **不确定**：姓氏例外的文本基线没通过它自己的正对照，偏弱；锁定检验只在 L8。

## P137 · HTML v75 p137 · pptx S145 (v22z) — Step ③ of 6 · L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity

**要说的话（一句英文一句中文）**
Step three lights layers 24 to 40, the main title-reading phase.
第三步点亮第 24 到 40 层，这是读标题的主要阶段。
The put-back test shows the title being read here; the question is what is read.
放回实验显示标题就在这里被读；问题是读走的是什么。
A made-up title with the same meaning brings back about 75 percent of the true title's advantage.
一个意思相同的编造标题，能找回真标题优势的大约 75%。
The small extra of the real title sits on rare, specific words, is not larger for recognised papers, and is even smaller for highly cited ones.
真标题多出的那一小块挂在稀有、具体的词上，在认得的论文上并不更大，引用多的论文反而更小。
So the bar is red: what is read is meaning and specific words, not paper identity; this overturns the general form of hypothesis two.
所以这条是红色的：读走的是意思和具体用词，不是论文身份；这推翻了 H2 的一般形式。
Next, layers 40 to 52.
下一步：第 40 到 52 层。

**备查（不念）· 本页幻灯片全文：** Step ③ of 6 · L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity Now asking: what happens in L24–L40, position by position? [figure: step3 L24 L40] So (this slide): L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity. overturns the general form of H2

**备查（不念）· 证据强度：** not supported / locked（页底标签“overturns the general form of H2”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L24–L40 段）

**L24–L40：读标题的主要阶段；读到的是意思和具体用词，不是论文身份**

- **标题 token**：放回实验显示，标题在 L24–L52 被读 [放回 / 拿走实验 · settled]。改写标题后状态与原标题的差距在 L36 达到峰值 +0.159 [0.146, 0.171]，中间层在字面之上编码了意思 [改写标题 · pre-registered + exploratory]。
- **意思 vs 身份**：这一段是 H2 一般形式被推翻的地方，靠合力：
  - 意思相同的编造标题能补回真标题优势的 0.751 [0.723, 0.778] [编造标题检验 · locked]；
  - 真标题多出的那一小块挂在稀有、具体的词上（只换稀有词掉 0.162，只换常见词掉 0.027）[稀有词 vs 常见词 · locked]；
  - 那一小块在认得的论文上没有更大，在引用多的论文上从 L24 起反而更小 [认得 / 引用数检查 · locked]；
  - 在字词和意思之外，身份对标题位置状态几乎没有解释力（≈ 0），意思单独多解释 0.17–0.27 [方差分解 · locked]。
- **标题位置上的真标题多出部分**：在 L40 只有 +0.016 [−0.001, +0.033]，在标题位置还不明显 [标题位置的真标题多出部分 · exploratory]。
- **冒号**：冒号仍按问题组织（L40 比值 3.0 倍）[冒号：换问题 vs 换论文 · descriptive]。格式锁定检验的曲线在这一段掉到 0.13（L40），后来查明是切掉 sink 造成的 [格式锁定检验 + 补充实验 · locked + exploratory]。
- **被推翻的**：H2 的一般形式"部分支持：存在真实论文成分"，现在是"不是一般意义上的论文身份，有一个锁定的小例外"。
- **不确定**：真标题多出的那一小块，是具体用词的作用，还是编造标题本身更"顺"带来的扣分，还没分开 [编造标题检验 · locked]。

## P138 · HTML v75 p138 · pptx S146 (v22z) — Step ④ of 6 · L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52

**要说的话（一句英文一句中文）**
Step four lights layers 40 to 52, where the title reaches the name positions.
第四步点亮第 40 到 52 层，标题在这里送到名字位置。
Putting the true-title states back restores 0.82 of the advantage at layer 48 and almost all of it at 52; taking them away from 52 on costs almost nothing.
把真标题的状态放回去，第 48 层恢复 0.82，第 52 层几乎全部恢复；从第 52 层起拿走，几乎没有损失。
The two opposite tests agree, and the timing is the same for all five false titles.
两个方向相反的检验结论一致，五个假标题下时间也一样。
The names-from-title edge carries the delivery, but cutting any single layer loses at most 1.25 percent: several layers work in parallel.
名字看标题这条边承担输送，但切掉任何一层最多只损失 1.25%：是多层并行。
Bottom line: the information reaches the name positions over several layers in parallel, and the title is read by layer 52.
底下的结论：信息经过多层并行送到名字位置，标题到第 52 层读完。
Next, layers 48 to 56.
下一步：第 48 到 56 层。

**备查（不念）· 本页幻灯片全文：** Step ④ of 6 · L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52 Now asking: what happens in L40–L52, position by position? [figure: step4 L40 L52] So (this slide): L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L40–L52 段）

**L40–L52：信息送到名字位置，多层并行；标题到 L52 读完**

- **标题之后的位置**：放回实验在 L45 恢复一半、L48 恢复 0.821、L52 恢复 0.995；从 L52 起拿走只损失 ≤ 0.05。放回和拿走方向相反、结论一致，是交叉验证；5 个假标题下结果一样，排除了某个假标题碰巧 [放回 / 拿走实验 · settled]。
- **名字 token**：只复制名字位置，能恢复 0.176（L40）→ 0.605（L48）→ 0.835（L52）；冒号来得晚，只有 0.073 → 0.177 [逐位置替换 · descriptive]。
- **路线**：在 L44–L55，名字 ← 标题这条注意力边承担输送（L48–51 窗口损失 +0.0112 [+0.0084, +0.0138]）[窗口式切断注意力边 · locked]。逐层切断时，名字 ← 标题在 L44、L48、L52、L54 都有作用，但切掉任何一层最多只损失 1.25% [单层扫描 · locked]。两项合力说明是多层并行，推翻了"单一路径、单一层"。
- **认得的作用**：认得改变的是信号大小，不改变到达时间（放回 R(L48) 只从 0.90 降到 0.81）[认得改变大小，时间几乎不变 · settled]。组间恢复率的差别是小分母效应 [按组恢复：分子与分母 · pre-registered]。这一项是排除。
- **名字位置的 probe**：在 L40，名字位置的 probe 已能分开认得和认不得（+0.031 [+0.019, +0.044]）[名字位置的 probe · pre-registered]。
- **不确定**：单层切断只是下界，其他层可能补上同样的信息；600 篇子样本。

## P139 · HTML v75 p139 · pptx S147 (v22z) — Step ⑤ of 6 · L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names

**要说的话（一句英文一句中文）**
Step five lights layers 48 to 56: in what form is the information held at the names?
第五步点亮第 48 到 56 层：信息在名字位置是以什么形式存着的？
A lens fitted on author prompts reads nothing here, but a probe can; on the same scale, the probe reads 0.06 more at layer 48.
用作者提示拟合的 lens 在这里读不出来，probe 却能读出；放在同一把尺子上，第 48 层 probe 多读出 0.06。
The information is spread out: the author subspace carries only about 7 percent, and there is no single direction and no earlier shelf.
信息是分散的：作者子空间只带过去约 7%，没有单一方向，也没有更早的架子。
And the MLPs at layers 52 to 56 carry paper information, not ready-made name directions.
第 52 到 56 层的 MLP 带的是论文信息，不是现成的名字方向。
Bottom line, in dark blue because each part rests on one experiment: the probe reads it, the lens does not; what arrives is paper information, not ready-made names.
底下的结论是深蓝色，因为每一部分各靠一个实验：probe 读得出，lens 读不出；送到的是论文信息，不是现成的名字。
Next, the last layers.
下一步：最后几层。

**备查（不念）· 本页幻灯片全文：** Step ⑤ of 6 · L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names Now asking: what happens in L48–L56, position by position? [figure: step5 L48 L56] So (this slide): L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names. one experiment each: same-scale test, MLP swap

**备查（不念）· 证据强度：** supported / locked（页底标签“one experiment each: same-scale test, MLP swap”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L48–L56 段）

**L48–L56：probe 读得出、lens 读不出；送到的是论文信息，不是现成的名字**

- **名字 token**：在 L48，同尺度下 probe 比 lens 多读出 +0.062 [+0.041, +0.081]；这是救场，补的是 probe 和 lens 尺度不同、没法比大小的问题 [同尺度检验 · locked]。同一位置，用作者提示拟合的 lens 读出的 target − control 是负的（−0.058 [−0.088, −0.028]），而 probe 是正的（+0.053 [+0.038, +0.067]）[作者提示 lens · pre-registered；名字位置的 probe · pre-registered]。
- **信息是分散的（合力）**：作者子空间只带过去约 7% [只替换"作者"子空间 · pre-registered]；认得 vs 认不得的差异没有任何主成分超过 7% [差异方向分析 · exploratory]；名字之前的位置没有更早的"架子"，672 个格子里只有零散的弱痕迹 [读出地图 · exploratory]。
- **注入**：在 L48–L52 加入 probe 的作者方向，写对姓的比例从 2.5% 升到 9.7%；但加入另一位作者的方向也会写出那位作者，主要是写入通道；认得的论文特有的部分只有 +0.025 到 +0.035 [注入作者方向 · locked]。
- **L52–L56 的 MLP**：把真标题运行的 MLP 输出换进来，能恢复 0.158–0.275；只换 512 个作者名方向，只恢复 0.022–0.042。带的是论文信息，不是现成的名字方向 [L52–L56 MLP 携带的内容 · descriptive]。
- **冒号和格式**：在 L56 把冒号状态换成问年份或问领域时的状态，作者信号下降约 0.03 [L56 替换冒号状态 · locked]。patching 指向 L40–L56，锁定规则给出 L56，但被切掉 sink 干扰 [格式锁定检验 + 补充实验 + patching · locked + exploratory]。
- **真标题多出的部分**：从 L56 起才明显大于 0 [真标题多出的部分在哪层出现 · descriptive]。姓氏信号在这一段回落，到 L56 约为 0 [L8 姓氏确认检验 · descriptive]。
- **被推翻的**：
  - "格式在 L56 才固定（锁定）"，现在是"锁定规则给 L56，但受切断 sink 影响，固定层定不下来"；
  - H3 的说法从"作者信息已经在中间层"降级为"线性可读：probe 能读出、lens 读不出；效应小，属于相关性证据；注入主要是写入通道，不能说明模型存着自己的知识却没用上"。
- **不确定**：L48 上 lens 为负、probe 为正，方向相反，没有解释；格式到底在哪一层固定定不下来，年份 / 领域无法测。

## P140 · HTML v75 p140 · pptx S148 (v22z) — Step ⑥ of 6 · L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing

**要说的话（一句英文一句中文）**
Step six lights the top, layers 56 to 63, where the name is written.
第六步点亮最上面的第 56 到 63 层，名字在这里写出。
Removing the MLPs at layers 57 to 61 costs more than removing attention at every layer, so the late MLPs write the name.
在第 57 到 61 层，去掉 MLP 的代价每一层都比去掉注意力大，所以是后面的 MLP 写出名字。
The gap between recognised and other papers grows here, to 0.21 at the output.
认得和认不得的论文之间的差距在这里长大，到输出端是 0.21。
Pushing the arrived signal harder barely helps, 2.5 to 2.8 percent, and the harm comes from direction, not amount; giving the first initial helps much more.
把已到达的信号推得更强几乎没用，只从 2.5% 到 2.8%，而且伤害来自方向，不来自强度；给出名首字母则帮助大得多。
Bottom line: the late MLPs write the name; the gap grows here, and it gets stuck at writing.
底下的结论：后面的 MLP 写出名字；差距在这里长大，卡在写出这一步。
Next, each stage in detail, experiment by experiment.
接下来逐段展开，一个实验一个实验地看。

**备查（不念）· 本页幻灯片全文：** Step ⑥ of 6 · L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing Now asking: what happens in L56–L63, position by position? [figure: step6 L56 L63] So (this slide): L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L56–L63 段）

**L56–L63：后期 MLP 写出名字；差距在这里长大，卡在写出这一步**

- **名字 token**：L57–L61 由 MLP 写出，不是注意力：MLP − 注意力平均 +0.040 [+0.036, +0.045]，每层 MLP 去掉信号的 11–14% [L57–L61 均值消融 · settled]。认得 vs 认不得的差距在最后十几层积累，L57–L61 上升最快，输出端是 +0.207 [0.195, 0.220] [分组比较 · settled]。用词表方向去读，名字到 L62 才排进约前 10 名 [名字到后期才读得出 · settled]。
- **先升后降**：约八分之一的论文里，真名字在 L56 之后先升后降，认得的 12.8%、认不得的 9.1%，差 +0.037 [+0.002, +0.073]，刚过界 [后期压制 · locked]。
- **名字开头最难**：首字母写法第一个 token 带的信号很少（约 0.1，后续约 0.45）[第一个 token 还是其余部分 · descriptive]。给出第一作者名首字母后，认得的论文写对至少一位完整作者的比例从 4.0% 升到 15.2% [给出名首字母 · locked]。
- **名字里哪些 token 带信号**：姓的第一个 token +0.68、其余 +0.58，首字母只有 +0.13 [信号在哪些 token · full cohort]。前 10 名里有完整的名时，姓的信号是 +0.22；只有首字母时约为 0 [知道名有助于写姓 · full cohort]。标题位置的 probe 在 L40 按名字 token 分开读，姓的第一个 token 比首字母高 +0.028 [+0.011, +0.045] [每个名字 token 上的 probe · pre-registered]。
- **加强没有用，伤害来自方向**：把已到达的论文信号放大，写对率只从 2.5% 到 2.8% [加强已到达的信号 · locked]。只改方向的推法 9 个格子全部有害，只加长度的只在靠近写出层、强度最大时有害 [为什么加强反而有害 · locked]。两项合力推翻"信号太弱"。
- **排除**：
  - 反转诅咒：从作者生成标题反而比从标题写作者略难，−0.032 [−0.047, −0.016] [方向不对称 · locked]；
  - 记混名字：编造名不是记错的近邻，约一半根本不在数据里 [编造名字从哪来 · exploratory]；
  - 真名 vs 编造名：中间层区分真名和编造名的 AUROC 是 0.72–0.78，只比输出置信度（0.711）高 +0.050 到 +0.062，而且只在 L40–L52 出现；模型内部对真假只多知道一点 [真名 vs 编造名能否区分 · exploratory]。
- **被推翻的**："信号太弱"；"只按作者 → 标题一个方向存储"。
- **缺口**：后期 MLP 里是否装着这篇论文的作者知识，没有实验直接测过（见下文缺口 ①）。

## P141 · HTML v75 p141 · pptx S149 (v22z) — Stage ① · L0–L4 in detail: the input words decide almost everything (part 1 of 2)

**要说的话（一句英文一句中文）**
Now each stage in detail: the main line runs down the middle, what was rewritten or ruled out is on the left, exceptions and dependencies on the right.
现在逐段展开：主线在中间往下走，左边是被改写或排除的，右边是例外和依赖。
Stage one starts from two tests: a new question about the same paper, and the same title under another question; both look the same at layer 4.
第一段从两个检验开始：同一篇论文换一个新问题，以及同一个标题放到另一个问题下；两者在第 4 层看起来都一样。
So where does that ceiling come from? Three checks answer it: the last token is identical at layer 0, the word embedding alone already identifies the title at 0.998, and BERT, which knows no papers, retrieves it every time.
那这个天花板是从哪来的？三项检查回答了：最后一个 token 在第 0 层完全相同，单靠词嵌入就能以 0.998 认出标题，不认识任何论文的 BERT 也每次都能找回。
These are exploratory checks, but they point the same way: the ceiling comes from identical input words.
这些是探索性的检查，但方向一致：天花板来自一模一样的输入字。
Next, what that means for the rest of the story.
下一页看这对后面的故事意味着什么。

**备查（不念）· 本页幻灯片全文：** Stage ① · L0–L4 in detail: the input words decide almost everything (part 1 of 2) Now asking: how was the L0–L4 conclusion reached, experiment by experiment? [figure: stage L0 L4 16x9 a] So (this slide): L0–L4: the input words decide almost everything. cannot separate meaning from identity here

**备查（不念）· 证据强度：** descriptive（页底标签“cannot separate meaning from identity here”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验（自上而下）：同一论文换新问题；同一标题换问题；天花板从哪来 → 三种问题的第 0 层、只用词嵌入（身份指数 0.998 [0.998, 0.999]）、不认识论文的 BERT（找回率 1.000）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L0–L4 段；本段后续部分共用此段）

**L0–L4：输入的字决定了几乎一切**

在最底层，模型还没做多少计算，状态主要由输入的字本身决定。
- **问题词和冒号**：三种问题（问作者、问年份、问领域）的提示里，最后一个 token 在第 0 层完全相同，这个位置在三种问题下没有差别 [L4 基准审计 · 仅在探索性结果文件中 · exploratory]。但冒号位置从一开始就跟着问题变：在 L4，换一个问题时冒号状态移动 0.443，换一篇论文只移动 0.094，是 4.7 倍；这个大比值主要来自问题的字面不同 [冒号：换问题 vs 换论文 · descriptive]。
- **标题 token**：同一个标题在不同问题下，L4 的状态余弦已经是 0.9976（两篇不同论文是 0.45），跨问题找回同一篇论文的成功率在 L4–L44 都是 1.000 [天花板审计 · exploratory]。只取最后一个标题 token 的词嵌入、不经过模型，身份指数 I 就有 0.998 [0.998, 0.999]；不认识任何论文的 BERT 从第 1 层起找回率也是 1.000 [L4 基准审计 · 仅在探索性结果文件中 · exploratory]。
- **为什么 L4 是字面基准**：一模一样的字给出一模一样的状态，天花板来自输入的字，与模型是否认识论文无关。所以后面所有"中间层是否超出字面"的比较，都拿 L4 作基线，比如改写标题的差距用 G′ − G′(L4) 来算 [改写标题 · pre-registered + exploratory]。
- **被推翻的**：早期把"换问题后标题状态不变"读成支持论文身份；天花板审计（救场）把它改为"分不开意思和身份"[天花板审计 · exploratory]。
- **不确定**：这一段本身没有缺口，但它限制了所有只换问题的检验：这些检验从 L4 起就到顶。

## P142 · HTML v75 p142 · pptx S150 (v22z) — Stage ① · L0–L4 in detail: the input words decide almost everything (part 2 of 2)

**要说的话（一句英文一句中文）**
Part two of stage one: the ceiling comes from identical input words, not from knowing the paper.
第一段第二部分：天花板来自一模一样的输入字，不是因为认识这篇论文。
On the left, the early reading that an unchanged state across questions supports paper identity is withdrawn by the ceiling audit.
左边，早期的读法“换问题状态不变，所以支持论文身份”被天花板审计撤回。
The stage conclusion: at layers 0 to 4 the input words set the states, and layer 4 is the literal baseline for every test that asks for something beyond the words.
这一段的结论：第 0 到 4 层由输入的字决定状态，第 4 层是所有“超出字面”检验的字面基线。
On the right, it hands on to layers 4 to 40, where paraphrase closeness is measured above its layer-4 level.
右边，它交给第 4 到 40 层：改写标题的接近程度都是在第 4 层水平之上来衡量的。
So: the input words decide almost everything here, and meaning cannot be separated from identity. Next, stage two.
所以：这里输入的字决定了几乎一切，意思和身份分不开。下一页是第二段。

**备查（不念）· 本页幻灯片全文：** Stage ① · L0–L4 in detail: the input words decide almost everything (part 2 of 2) Now asking: how was the L0–L4 conclusion reached, experiment by experiment? [figure: stage L0 L4 16x9 b] So (this slide): L0–L4: the input words decide almost everything. cannot separate meaning from identity here

**备查（不念）· 证据强度：** descriptive（页底标签“cannot separate meaning from identity here”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：天花板来自一模一样的输入字 → 早期读法被天花板审计撤回 → 段结论：L0–L4 由输入的字决定状态，L4 是所有"超出字面"检验的字面基线 → 交给 L4–L40（改写标题以 G′ − G′(L4) 衡量）。

同段定稿树原文见 P140 的备查。

## P143 · HTML v75 p143 · pptx S151 (v22z) — Stage ② · L4–L24 in detail: early read-in; first traces of the title and of the first author (part 1 of 2)

**要说的话（一句英文一句中文）**
Stage two, layers 4 to 24, part one.
第二段，第 4 到 24 层，第一部分。
The colon first: a probe trained at the colon keeps only 0.24 to 0.41 under a new question, and 62 to 92 percent of the colon's attention goes to position 0, so the colon carries the question.
先看冒号：在冒号位置训练的 probe，换一个问题只剩 0.24 到 0.41；冒号 62% 到 92% 的注意力落在第 0 个位置，所以冒号携带的是问题。
Then the title: layer order puts title facts and the first author's token first, at layers 8 to 16; paper attributes become readable at the title from about layer 16, though they can be inferred from the title text.
再看标题：层顺序显示，标题信息和第一作者的 token 最早出现，在第 8 到 16 层；论文属性大约从第 16 层起能在标题位置读出，不过这些属性能从标题文字推出来。
And a paraphrased title stays closer to the original than its layer-4 level from layer 8 on.
改写过的标题从第 8 层起，和原标题的接近程度超过了第 4 层的水平。
On the right, a new box: the top lens word cannot decide; at layers 24 to 48 it is mostly punctuation or format, but it changes with the title for 28 to 64 percent of name tokens.
右边新加了一个框：最上面的 lens 词定不下来；在第 24 到 48 层它大多是标点或格式词，但在 28% 到 64% 的名字 token 上会随标题变化。
Next, the one small reverse clue.
下一页看那条唯一的反向小线索。

**备查（不念）· 本页幻灯片全文：** Stage ② · L4–L24 in detail: early read-in; first traces of the title and of the first author (part 1 of 2) Now asking: how was the L4–L24 conclusion reached, experiment by experiment? [figure: stage L4 L24 16x9 a] So (this slide): L4–L24: early read-in; the first traces of the title and of the first author. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：冒号 probe 换问题后 0.24–0.41；冒号注意力 62–92% 落在第 0 位置；层顺序（标题信息、第一作者 token 在 L8–L16 最早出现）；标题位置读论文属性（年份 R² 从 L16 的 0.38 上升，可由标题文字推出）；改写标题（从 L8 起高于 L4 水平）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L4–L24 段；本段后续部分共用此段）

**L4–L24：早期读入，最早的标题信息和第一作者痕迹**

- **问题词和冒号**：冒号继续按问题组织。在冒号位置训练的领域 probe，换一种问题后只剩 0.24–0.41（L4–L52）[换问题后 probe 还能否用 · descriptive]。补充实验发现，冒号 62–92% 的注意力落在第 0 个位置；只要保留这个位置，从 L4 起人名答案类型就保持住 [格式锁定补充实验 · exploratory]。
- **标题 token**：标题信息和第一作者 token 最早在 L8–L16 出现 [层顺序 · descriptive]。在标题位置用 probe 读年份，R² 从 L16 的 0.38 开始上升，但这些属性能从标题文字推出来 [标题位置读论文属性 · descriptive]。改写标题后，状态与原标题的差距从 L8 起高于 L4 的水平，说明中间层开始在字面之上编码意思 [改写标题 · pre-registered + exploratory]。
- **唯一的反向线索**：把 L8 的标题状态搬进固定提问句"Paper: X / The first author of the paper is"，能解码出第一作者的姓。在 6,048 篇新论文上，扣掉同主题配对论文后仍有 +0.046 [+0.035, +0.056]；超过纯文本基线和认得的更大两项都刚过线；原始信号约一半来自主题 [L8 姓氏确认检验 · locked]。这是排除（来源检查砍掉字面重叠、主题配对砍掉主题先验）加救场（确认检验补上样本太小的主题配对）共同得出的锁定小例外。
- **标题位置的 probe**：在 L24，标题位置的 probe 已经能稍微分开认得和认不得（+0.052 [+0.018, +0.086]）[标题位置的 probe · descriptive]。
- **不确定**：姓氏例外的文本基线没通过它自己的正对照，偏弱；锁定检验只在 L8。

**备查（不念）· 图中新增的元素：** 图右栏新增“Top lens word: cannot decide”框（L24–L48 最上面的 lens 词多为标点 / 格式，但 28–64% 的名字 token 上随标题变化）。

## P144 · HTML v75 p144 · pptx S152 (v22z) — Stage ② · L4–L24 in detail: early read-in; first traces of the title and of the first author (part 2 of 2)

**要说的话（一句英文一句中文）**
Part two of stage two: early read-in starts here.
第二段第二部分：早期读入从这里开始。
The surname test moves the layer-8 title state into a fixed question about the first author and decodes the surname; on 6,048 new papers it is +0.046 after removing topic-matched papers.
姓氏检验把第 8 层的标题状态放进一个固定的“第一作者是谁”的问句，解码出姓；在 6,048 篇新论文上，扣掉同主题配对后是 +0.046。
On the left, literal overlap is ruled out by the source check, and a topic-matched test that was too small is rescued by the confirmatory test.
左边，来源检查排除了字面重叠；样本太小的主题配对检验由确认检验补上。
On the right, whether this is identity cannot be decided: the text-only baseline fails its own positive control, and the signal is back near zero by layer 56.
右边，这是否算身份还定不下来：纯文本基线没通过它自己的正对照，而且信号到第 56 层回到接近零。
The title probe also separates recognised from other papers a little at layer 24.
标题位置的 probe 在第 24 层也能稍微分开认得和认不得的论文。
Stage conclusion: layers 4 to 24 are read-in only; meaning beyond the words starts at layer 8, with one small locked surname exception. Next, stage three.
这一段的结论：第 4 到 24 层只是读入；超出字面的意思从第 8 层开始，有一个锁定的小姓氏例外。下一页是第三段。

**备查（不念）· 本页幻灯片全文：** Stage ② · L4–L24 in detail: early read-in; first traces of the title and of the first author (part 2 of 2) Now asking: how was the L4–L24 conclusion reached, experiment by experiment? [figure: stage L4 L24 16x9 b] So (this slide): L4–L24: early read-in; the first traces of the title and of the first author. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：L8 姓氏确认检验（6,048 篇新论文，扣掉同主题配对 +0.046 [+0.035, +0.056]；超过文本基线和认得更大两项刚过线；约一半来自主题）；排除字面重叠（来源检查）；救场：主题配对检验样本太小，由确认检验补上；不能判定：文本基线未过正对照，L56 回到约 0；标题位置 probe L24 +0.052 [+0.018, +0.086]。

同段定稿树原文见 P142 的备查。

## P145 · HTML v75 p145 · pptx S153 (v22z) — Stage ③ · L24–L40 in detail: what is read is meaning and specific words, not paper identity (part 1 of 2)

**要说的话（一句英文一句中文）**
Stage three, layers 24 to 40: what is read when the title is read?
第三段，第 24 到 40 层：读标题的时候，读走的是什么？
First, which title words carry the signal: swapping content words for random words wipes it out, while synonyms lose only a little, so it is carried by meaning.
先看哪些标题词带着信号：把内容词换成随机词，信号就没了；换成同义词只掉一点，所以信号靠意思承载。
A paraphrased title, the same meaning in other words, is encoded beyond the literal level, peaking at layer 36.
改写过的标题，意思相同、用词不同，在字面水平之上被编码，在第 36 层达到峰值。
Then the key test: a made-up title with the same meaning brings back 0.75 of the true title's advantage, and the real title adds a small extra, 0.11.
然后是关键检验：一个意思相同的编造标题能找回真标题优势的 0.75，真标题再多出一小块，0.11。
On the right, a caveat: made-up titles are a little more likely to the model, log-prob 0.12 higher, so part of the extra may be closeness that the made-up title missed.
右边有一条注意：编造的标题对模型来说可能性稍高，对数概率高 0.12；所以那一小块里可能有一部分是编造标题没贴近的意思。
So the open question is: what is that small extra part? Next page.
所以剩下的问题是：那一小块是什么？看下一页。

**备查（不念）· 本页幻灯片全文：** Stage ③ · L24–L40 in detail: what is read is meaning and specific words, not paper identity (part 1 of 2) Now asking: how was the L24–L40 conclusion reached, experiment by experiment? [figure: stage L24 L40 16x9 a] So (this slide): L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity. overturns the general form of H2

**备查（不念）· 证据强度：** not supported / locked（页底标签“overturns the general form of H2”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：哪些标题词带信号（随机替换内容词 vs 同义词）；改写标题（L36 峰值 +0.159 [0.146, 0.171]）；编造标题检验（0.751 [0.723, 0.778]，真标题多出 +0.106）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L24–L40 段；本段后续部分共用此段）

**L24–L40：读标题的主要阶段；读到的是意思和具体用词，不是论文身份**

- **标题 token**：放回实验显示，标题在 L24–L52 被读 [放回 / 拿走实验 · settled]。改写标题后状态与原标题的差距在 L36 达到峰值 +0.159 [0.146, 0.171]，中间层在字面之上编码了意思 [改写标题 · pre-registered + exploratory]。
- **意思 vs 身份**：这一段是 H2 一般形式被推翻的地方，靠合力：
  - 意思相同的编造标题能补回真标题优势的 0.751 [0.723, 0.778] [编造标题检验 · locked]；
  - 真标题多出的那一小块挂在稀有、具体的词上（只换稀有词掉 0.162，只换常见词掉 0.027）[稀有词 vs 常见词 · locked]；
  - 那一小块在认得的论文上没有更大，在引用多的论文上从 L24 起反而更小 [认得 / 引用数检查 · locked]；
  - 在字词和意思之外，身份对标题位置状态几乎没有解释力（≈ 0），意思单独多解释 0.17–0.27 [方差分解 · locked]。
- **标题位置上的真标题多出部分**：在 L40 只有 +0.016 [−0.001, +0.033]，在标题位置还不明显 [标题位置的真标题多出部分 · exploratory]。
- **冒号**：冒号仍按问题组织（L40 比值 3.0 倍）[冒号：换问题 vs 换论文 · descriptive]。格式锁定检验的曲线在这一段掉到 0.13（L40），后来查明是切掉 sink 造成的 [格式锁定检验 + 补充实验 · locked + exploratory]。
- **被推翻的**：H2 的一般形式"部分支持：存在真实论文成分"，现在是"不是一般意义上的论文身份，有一个锁定的小例外"。
- **不确定**：真标题多出的那一小块，是具体用词的作用，还是编造标题本身更"顺"带来的扣分，还没分开 [编造标题检验 · locked]。

**备查（不念）· 图中新增的元素：** 图右栏新增“Caveat: made-up title”框（编造标题的 log-prob 高 +0.12；意思越近找回越多 → 多出的部分可能有一部分是编造标题没贴近的意思）。

## P146 · HTML v75 p146 · pptx S154 (v22z) — Stage ③ · L24–L40 in detail: what is read is meaning and specific words, not paper identity (part 2 of 2)

**要说的话（一句英文一句中文）**
Part two of stage three: what is the small extra?
第三段第二部分：那一小块是什么？
Four locked tests together: it sits on rare words, not common ones; it is not larger for recognised papers and smaller for highly cited ones; a variance split finds identity adds about zero; and the paper-facts subspace carries no extra author information.
四项锁定检验合起来看：它挂在稀有词上，不在常见词上；在认得的论文上不更大，引用多的反而更小；方差分解显示身份几乎不增加解释力；论文信息子空间也不带额外的作者信息。
So the real title's small extra comes from specific words, not from recognising the paper.
所以真标题多出的那一小块来自具体用词，不是来自认出这篇论文。
On the left, the claim that the middle layers store which paper this is gets crossed out: it is not a general paper identity, with one small locked exception, the layer-8 surname signal.
左边，“中间层存着这是哪篇论文”被划掉：不是一般意义上的论文身份，只有一个锁定的小例外，就是第 8 层的姓氏信号。
On the right, a caveat on rare versus common words: the two swaps replace unequal numbers of words, 3.4 versus 2.1, and the common words are frequency-matched, not synonyms; with equal counts the gap remains, about 0.07, an exploratory check.
右边有一条关于稀有词和常见词的注意：两种替换换掉的词数不同，3.4 对 2.1，常见词是按词频配的，不是同义词；词数相同时差距仍在，约 0.07，这是探索性检查。
Stage conclusion, in red: what is read in layers 24 to 40 is meaning and specific words, not paper identity; this overturns the general form of hypothesis two. Next, stage four.
这一段的结论是红色的：第 24 到 40 层读走的是意思和具体用词，不是论文身份；这推翻了 H2 的一般形式。下一页是第四段。

**备查（不念）· 本页幻灯片全文：** Stage ③ · L24–L40 in detail: what is read is meaning and specific words, not paper identity (part 2 of 2) Now asking: how was the L24–L40 conclusion reached, experiment by experiment? [figure: stage L24 L40 16x9 b] So (this slide): L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity. overturns the general form of H2

**备查（不念）· 证据强度：** not supported / locked（页底标签“overturns the general form of H2”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：稀有词 vs 常见词（0.162 vs 0.027）；认得 / 引用数检查（不更大，引用多的更小）；方差分解（身份 ≈ 0，意思 0.17–0.27）；论文信息子空间替换（R_id 0.004）；被划掉："中间层存论文身份"；例外：L8 姓氏锁定小例外；排除：主题先验。

同段定稿树原文见 P144 的备查。

**备查（不念）· 图中新增的元素：** 图右栏新增“Caveat: rare vs common words”框（替换词数 3.4 vs 2.1；常见词按词频配对、不是同义词；词数相同时差距仍在 +0.07，exploratory）。

## P147 · HTML v75 p147 · pptx S155 (v22z) — Stage ④ · L40–L52 in detail: the title reaches the names over several layers in parallel; read by L52 (part 1 of 2)

**要说的话（一句英文一句中文）**
Stage four, layers 40 to 52: when is the title read, and when has it arrived?
第四段，第 40 到 52 层：标题什么时候读完，什么时候送到？
Two opposite tests: putting the true-title states back restores 0.82 at layer 48 and 0.995 at 52; taking them away from layer 52 on loses at most 0.05.
两个方向相反的检验：把真标题的状态放回去，第 48 层恢复 0.82，第 52 层恢复 0.995；从第 52 层起拿走，最多只损失 0.05。
On the left, a lucky false title is ruled out: all five false titles give the same timing.
左边排除了“碰巧某一个假标题”：五个假标题给出的时间都一样。
Together: the title is read and has reached the positions after the title by layer 52, a cross-check from both directions.
合起来：标题到第 52 层已经读完，并送到了标题之后的位置，这是两个方向的交叉验证。
Next, where exactly it lands and by which route.
下一页看它具体落在哪里、走哪条路。

**备查（不念）· 本页幻灯片全文：** Stage ④ · L40–L52 in detail: the title reaches the names over several layers in parallel; read by L52 (part 1 of 2) Now asking: how was the L40–L52 conclusion reached, experiment by experiment? [figure: stage L40 L52 16x9 a] So (this slide): L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：放回（L48 0.821、L52 0.995）与拿走（L52 起 ≤ 0.05）方向相反、结论一致；5 个假标题时间一致（排除碰巧某个假标题）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L40–L52 段；本段后续部分共用此段）

**L40–L52：信息送到名字位置，多层并行；标题到 L52 读完**

- **标题之后的位置**：放回实验在 L45 恢复一半、L48 恢复 0.821、L52 恢复 0.995；从 L52 起拿走只损失 ≤ 0.05。放回和拿走方向相反、结论一致，是交叉验证；5 个假标题下结果一样，排除了某个假标题碰巧 [放回 / 拿走实验 · settled]。
- **名字 token**：只复制名字位置，能恢复 0.176（L40）→ 0.605（L48）→ 0.835（L52）；冒号来得晚，只有 0.073 → 0.177 [逐位置替换 · descriptive]。
- **路线**：在 L44–L55，名字 ← 标题这条注意力边承担输送（L48–51 窗口损失 +0.0112 [+0.0084, +0.0138]）[窗口式切断注意力边 · locked]。逐层切断时，名字 ← 标题在 L44、L48、L52、L54 都有作用，但切掉任何一层最多只损失 1.25% [单层扫描 · locked]。两项合力说明是多层并行，推翻了"单一路径、单一层"。
- **认得的作用**：认得改变的是信号大小，不改变到达时间（放回 R(L48) 只从 0.90 降到 0.81）[认得改变大小，时间几乎不变 · settled]。组间恢复率的差别是小分母效应 [按组恢复：分子与分母 · pre-registered]。这一项是排除。
- **名字位置的 probe**：在 L40，名字位置的 probe 已能分开认得和认不得（+0.031 [+0.019, +0.044]）[名字位置的 probe · pre-registered]。
- **不确定**：单层切断只是下界，其他层可能补上同样的信息；600 篇子样本。

## P148 · HTML v75 p148 · pptx S156 (v22z) — Stage ④ · L40–L52 in detail: the title reaches the names over several layers in parallel; read by L52 (part 2 of 2)

**要说的话（一句英文一句中文）**
Part two of stage four: where does it land, and by which route?
第四段第二部分：落在哪里，走哪条路？
Position by position, the information lands mainly on the names: names alone restore 0.18 at layer 40, 0.61 at 48 and 0.84 at 52.
一个位置一个位置地看，信息主要落在名字上：只换名字位置，第 40 层恢复 0.18，第 48 层 0.61，第 52 层 0.84。
Blocking attention edges in windows finds the names-from-title edge carrying the delivery at layers 44 to 55; but a single-layer sweep shows no bottleneck: any one layer costs at most 1.25 percent.
按窗口切断注意力边，找到名字看标题这条边在第 44 到 55 层承担输送；但逐层扫描显示没有瓶颈：任何一层最多只损失 1.25%。
On the left, the idea that recognised papers are read earlier is ruled out: recognition changes the size, not the timing; and one route through one layer is overturned.
左边排除了“认得的论文读得更早”：认得改变的是大小，不是时间；“一条路、一层”的说法也被推翻。
Stage conclusion: by layer 52 the title has reached the name positions, through several layers in parallel. Next, stage five.
这一段的结论：到第 52 层，标题已经送到名字位置，经过多层并行。下一页是第五段。

**备查（不念）· 本页幻灯片全文：** Stage ④ · L40–L52 in detail: the title reaches the names over several layers in parallel; read by L52 (part 2 of 2) Now asking: how was the L40–L52 conclusion reached, experiment by experiment? [figure: stage L40 L52 16x9 b] So (this slide): L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：逐位置替换（名字位置 0.176 → 0.605 → 0.835，L40/L48/L52）；窗口式切断注意力边（L48–51 窗口 +0.0112 [+0.0084, +0.0138]）；单层扫描（任何一层 ≤ 1.25%）；名字位置 probe L40 +0.031 [+0.019, +0.044]；排除："认得的论文读得更早"（R(L48) 0.90 → 0.81，只改变大小）；推翻："一条路、一层"；600 篇子样本，单层切断只是下界。

同段定稿树原文见 P146 的备查。

## P149 · HTML v75 p149 · pptx S157 (v22z) — Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 1 of 3)

**要说的话（一句英文一句中文）**
Stage five, layers 48 to 56: in what form is it held at the names?
第五段，第 48 到 56 层：在名字位置是以什么形式存着的？
A lens fitted on author prompts cannot read it: target minus control is negative, minus 0.058 at layer 48.
用作者提示拟合的 lens 读不出来：target 减 control 是负的，第 48 层是 −0.058。
A probe at the name positions can: it separates recognised from other papers from layer 40.
名字位置的 probe 能读出：从第 40 层起就能分开认得和认不得的论文。
The rescue is the same-scale test: on exactly the same tokens and one rank scale, the probe reads 0.062 more than the lens at layer 48.
救场的是同尺度检验：在完全相同的 token 和同一把排名尺子上，第 48 层 probe 比 lens 多读出 0.062。
So author information is linearly readable at the names, but not in vocabulary directions. Next: is it in one place?
所以作者信息在名字位置是线性可读的，但不在词表方向上。下一页问：它是不是集中在一处？

**备查（不念）· 本页幻灯片全文：** Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 1 of 3) Now asking: how was the L48–L56 conclusion reached, experiment by experiment? [figure: stage L48 L56 16x9 a] So (this slide): L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names. one experiment each: same-scale test, MLP swap

**备查（不念）· 证据强度：** supported / locked（页底标签“one experiment each: same-scale test, MLP swap”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：作者提示 lens（L48 −0.058 [−0.088, −0.028]）；名字位置 probe（+0.053 [+0.038, +0.067]）；同尺度检验（9,137 个名字 token，L40 +0.021、L48 +0.062 [+0.041, +0.081]）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L48–L56 段；本段后续部分共用此段）

**L48–L56：probe 读得出、lens 读不出；送到的是论文信息，不是现成的名字**

- **名字 token**：在 L48，同尺度下 probe 比 lens 多读出 +0.062 [+0.041, +0.081]；这是救场，补的是 probe 和 lens 尺度不同、没法比大小的问题 [同尺度检验 · locked]。同一位置，用作者提示拟合的 lens 读出的 target − control 是负的（−0.058 [−0.088, −0.028]），而 probe 是正的（+0.053 [+0.038, +0.067]）[作者提示 lens · pre-registered；名字位置的 probe · pre-registered]。
- **信息是分散的（合力）**：作者子空间只带过去约 7% [只替换"作者"子空间 · pre-registered]；认得 vs 认不得的差异没有任何主成分超过 7% [差异方向分析 · exploratory]；名字之前的位置没有更早的"架子"，672 个格子里只有零散的弱痕迹 [读出地图 · exploratory]。
- **注入**：在 L48–L52 加入 probe 的作者方向，写对姓的比例从 2.5% 升到 9.7%；但加入另一位作者的方向也会写出那位作者，主要是写入通道；认得的论文特有的部分只有 +0.025 到 +0.035 [注入作者方向 · locked]。
- **L52–L56 的 MLP**：把真标题运行的 MLP 输出换进来，能恢复 0.158–0.275；只换 512 个作者名方向，只恢复 0.022–0.042。带的是论文信息，不是现成的名字方向 [L52–L56 MLP 携带的内容 · descriptive]。
- **冒号和格式**：在 L56 把冒号状态换成问年份或问领域时的状态，作者信号下降约 0.03 [L56 替换冒号状态 · locked]。patching 指向 L40–L56，锁定规则给出 L56，但被切掉 sink 干扰 [格式锁定检验 + 补充实验 + patching · locked + exploratory]。
- **真标题多出的部分**：从 L56 起才明显大于 0 [真标题多出的部分在哪层出现 · descriptive]。姓氏信号在这一段回落，到 L56 约为 0 [L8 姓氏确认检验 · descriptive]。
- **被推翻的**：
  - "格式在 L56 才固定（锁定）"，现在是"锁定规则给 L56，但受切断 sink 影响，固定层定不下来"；
  - H3 的说法从"作者信息已经在中间层"降级为"线性可读：probe 能读出、lens 读不出；效应小，属于相关性证据；注入主要是写入通道，不能说明模型存着自己的知识却没用上"。
- **不确定**：L48 上 lens 为负、probe 为正，方向相反，没有解释；格式到底在哪一层固定定不下来，年份 / 领域无法测。

## P150 · HTML v75 p150 · pptx S158 (v22z) — Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 2 of 3)

**要说的话（一句英文一句中文）**
Part two of stage five: is it concentrated anywhere?
第五段第二部分：它有没有集中在哪里？
Swapping only the author subspace carries about 7 percent; a direction analysis finds no component above 7 percent; and the readout map finds no earlier shelf, only scattered traces.
只替换作者子空间，只带过去约 7%；方向分析找不到超过 7% 的成分；读出地图也没有更早的架子，只有零星痕迹。
Three tests, one answer: the information is spread out, with no clean subspace, no single direction and no earlier shelf.
三项检验，一个答案：信息是分散的，没有干净的子空间，没有单一方向，也没有更早的架子。
Next, what the MLPs at these layers carry.
下一页看这几层的 MLP 带的是什么。

**备查（不念）· 本页幻灯片全文：** Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 2 of 3) Now asking: how was the L48–L56 conclusion reached, experiment by experiment? [figure: stage L48 L56 16x9 b] So (this slide): L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names. one experiment each: same-scale test, MLP swap

**备查（不念）· 证据强度：** supported / locked（页底标签“one experiment each: same-scale test, MLP swap”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：只替换作者子空间（约 7%）；差异方向分析（无主成分超过 7%）；读出地图（672 格中零星弱痕迹，无更早架子）。

同段定稿树原文见 P148 的备查。

## P151 · HTML v75 p151 · pptx S159 (v22z) — Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 3 of 3)

**要说的话（一句英文一句中文）**
Part three of stage five: what do the MLPs at layers 52 to 56 carry?
第五段第三部分：第 52 到 56 层的 MLP 带的是什么？
Swapping in the true-title MLP output restores 0.16 to 0.28, but swapping only 512 author-name directions restores 0.02 to 0.04: paper information, not ready-made names.
把真标题运行的 MLP 输出换进来，能恢复 0.16 到 0.28；只换 512 个作者名方向，只恢复 0.02 到 0.04：带的是论文信息，不是现成的名字。
Injecting the author direction raises correct surnames from 2.5 to 9.7 percent, but another author's direction works too, so it is mainly a write channel.
注入作者方向能把写对姓的比例从 2.5% 提高到 9.7%，但注入另一位作者的方向也一样有效，所以主要是一个写入通道。
On the left, the format layer is rewritten: the locked rule gave layer 56, but cutting the sink distorts it, so the layer is not pinned down.
左边，格式层被改写：锁定规则给出第 56 层，但切掉 sink 会扭曲结果，所以这一层定不下来。
Stage conclusion: at the names the probe reads it and the lens does not; what arrives is paper information, spread out, not ready-made names. Next, stage six.
这一段的结论：在名字位置，probe 读得出、lens 读不出；送到的是分散的论文信息，不是现成的名字。下一页是第六段。

**备查（不念）· 本页幻灯片全文：** Stage ⑤ · L48–L56 in detail: the probe reads it, the lens does not; paper information, not ready-made names (part 3 of 3) Now asking: how was the L48–L56 conclusion reached, experiment by experiment? [figure: stage L48 L56 16x9 c] So (this slide): L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names. one experiment each: same-scale test, MLP swap

**备查（不念）· 证据强度：** supported / locked（页底标签“one experiment each: same-scale test, MLP swap”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：L52–L56 MLP 携带的内容（恢复 0.158–0.275 vs 512 个名字方向 0.022–0.042）；注入作者方向（2.5% → 9.7%，主要是写入通道，认得特有部分 +0.025 到 +0.035）；改写：格式层（锁定规则给 L56，受切断 sink 影响，定不下来）。

同段定稿树原文见 P148 的备查。

## P152 · HTML v75 p152 · pptx S160 (v22z) — Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 1 of 3)

**要说的话（一句英文一句中文）**
Stage six, layers 56 to 63: who writes the name?
第六段，第 56 到 63 层：谁写出名字？
Mean ablation at layers 57 to 61: replacing a layer's MLP costs more than replacing its attention, by 0.040 on average, and each MLP removes 11 to 14 percent of the signal. This is settled.
第 57 到 61 层的均值消融：替换一层的 MLP，代价比替换注意力平均多 0.040；每层 MLP 去掉 11% 到 14% 的信号。这是定论。
The group comparison shows the gap building over the last dozen layers, to 0.21 at the output.
分组比较显示差距在最后十几层积累，到输出端是 0.21。
And in vocabulary terms, the true name reaches about rank 10 only at layer 62.
用词表方向来看，真名字要到第 62 层才排进大约前 10 名。
So the late MLPs, not attention, write the name. Next, which part of the name.
所以是后面的 MLP、不是注意力写出名字。下一页看名字的哪一部分。

**备查（不念）· 本页幻灯片全文：** Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 1 of 3) Now asking: how was the L56–L63 conclusion reached, experiment by experiment? [figure: stage L56 L63 16x9 a] So (this slide): L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：L57–L61 均值消融（MLP − 注意力 +0.040 [+0.036, +0.045]，每层 MLP 去掉 11–14%）；分组比较（输出端 +0.207 [0.195, 0.220]）；名字到 L62 才排进约前 10 名。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（完整故事，L56–L63 段；本段后续部分共用此段）

**L56–L63：后期 MLP 写出名字；差距在这里长大，卡在写出这一步**

- **名字 token**：L57–L61 由 MLP 写出，不是注意力：MLP − 注意力平均 +0.040 [+0.036, +0.045]，每层 MLP 去掉信号的 11–14% [L57–L61 均值消融 · settled]。认得 vs 认不得的差距在最后十几层积累，L57–L61 上升最快，输出端是 +0.207 [0.195, 0.220] [分组比较 · settled]。用词表方向去读，名字到 L62 才排进约前 10 名 [名字到后期才读得出 · settled]。
- **先升后降**：约八分之一的论文里，真名字在 L56 之后先升后降，认得的 12.8%、认不得的 9.1%，差 +0.037 [+0.002, +0.073]，刚过界 [后期压制 · locked]。
- **名字开头最难**：首字母写法第一个 token 带的信号很少（约 0.1，后续约 0.45）[第一个 token 还是其余部分 · descriptive]。给出第一作者名首字母后，认得的论文写对至少一位完整作者的比例从 4.0% 升到 15.2% [给出名首字母 · locked]。
- **名字里哪些 token 带信号**：姓的第一个 token +0.68、其余 +0.58，首字母只有 +0.13 [信号在哪些 token · full cohort]。前 10 名里有完整的名时，姓的信号是 +0.22；只有首字母时约为 0 [知道名有助于写姓 · full cohort]。标题位置的 probe 在 L40 按名字 token 分开读，姓的第一个 token 比首字母高 +0.028 [+0.011, +0.045] [每个名字 token 上的 probe · pre-registered]。
- **加强没有用，伤害来自方向**：把已到达的论文信号放大，写对率只从 2.5% 到 2.8% [加强已到达的信号 · locked]。只改方向的推法 9 个格子全部有害，只加长度的只在靠近写出层、强度最大时有害 [为什么加强反而有害 · locked]。两项合力推翻"信号太弱"。
- **排除**：
  - 反转诅咒：从作者生成标题反而比从标题写作者略难，−0.032 [−0.047, −0.016] [方向不对称 · locked]；
  - 记混名字：编造名不是记错的近邻，约一半根本不在数据里 [编造名字从哪来 · exploratory]；
  - 真名 vs 编造名：中间层区分真名和编造名的 AUROC 是 0.72–0.78，只比输出置信度（0.711）高 +0.050 到 +0.062，而且只在 L40–L52 出现；模型内部对真假只多知道一点 [真名 vs 编造名能否区分 · exploratory]。
- **被推翻的**："信号太弱"；"只按作者 → 标题一个方向存储"。
- **缺口**：后期 MLP 里是否装着这篇论文的作者知识，没有实验直接测过（见下文缺口 ①）。

## P153 · HTML v75 p153 · pptx S161 (v22z) — Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 2 of 3)

**要说的话（一句英文一句中文）**
Part two of stage six: which tokens carry the signal?
第六段第二部分：哪些 token 带着信号？
The surname's first token carries +0.68 and the rest +0.58, but an initial only +0.13; knowing the given name helps with the surname.
姓的第一个 token 是 +0.68，其余 +0.58，首字母只有 +0.13；知道名有助于写姓。
Co-authors help too, but through the co-author network rather than this paper.
合作者也有帮助，但来自合作者网络，不是这篇论文本身。
Giving the first initial lifts recognised papers from 4.0 to 15.2 percent with at least one full author right.
给出名首字母，认得的论文写对至少一位完整作者的比例从 4.0% 升到 15.2%。
So the signal sits on surnames and full given names; the start of the name is hardest. Next, why it gets stuck.
所以信号在姓和完整的名上；名字的开头最难。下一页看为什么会卡住。

**备查（不念）· 本页幻灯片全文：** Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 2 of 3) Now asking: how was the L56–L63 conclusion reached, experiment by experiment? [figure: stage L56 L63 16x9 b] So (this slide): L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：第一个 token 还是其余部分（首字母写法第一个 token 约 0.1，后续约 0.45）；信号在哪些 token（姓首 token +0.68、其余 +0.58、首字母 +0.13）；知道名有助于写姓（+0.22 vs 约 0）；合作者（来自合作网络）；给出名首字母（4.0% → 15.2%）；真名 vs 编造名（AUROC 0.72–0.78，只比输出置信度 0.711 高 +0.050 到 +0.062）。

同段定稿树原文见 P151 的备查。

## P154 · HTML v75 p154 · pptx S162 (v22z) — Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 3 of 3)

**要说的话（一句英文一句中文）**
Part three of stage six: why does it get stuck?
第六段第三部分：为什么会卡住？
Strengthening the arrived signal barely helps, 2.5 to 2.8 percent; direction-only pushes hurt in all nine cells, so the harm comes from direction, not amount.
加强已到达的信号几乎没用，只从 2.5% 到 2.8%；只改方向的推法在九个格子里全都有害，所以伤害来自方向，不来自强度。
About one paper in eight shows the name rising after layer 56 and then falling, slightly more often for recognised papers, just past the bound.
大约八分之一的论文里，名字在第 56 层之后先升后降，认得的稍多一点，刚过界。
On the left, the reversal curse is ruled out, and made-up names are not mixed-up neighbours: about half are not in the data at all.
左边排除了反转诅咒；编造的名字也不是记混的近邻，大约一半根本不在数据里。
Stage conclusion: the late MLPs write the name, and it gets stuck at writing, hardest at the start of the name. Next, how the pieces fit.
这一段的结论：后面的 MLP 写出名字，卡在写出这一步，名字开头最难。下一页看这些部分怎么拼在一起。

**备查（不念）· 本页幻灯片全文：** Stage ⑥ · L56–L63 in detail: the late MLPs write the name; it gets stuck at writing (part 3 of 3) Now asking: how was the L56–L63 conclusion reached, experiment by experiment? [figure: stage L56 L63 16x9 c] So (this slide): L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing. joint

**备查（不念）· 证据强度：** fairly solid（页底标签“joint”）。图内自带三行灰字（公式、n、读法），在图片下方。

**备查（不念）· 本页内容：** 实验：加强已到达的信号（2.5% → 2.8%）；为什么加强有害（只改方向 9/9 格有害）；后期压制（12.8% vs 9.1%，+0.037 [+0.002, +0.073]，刚过界）；排除：反转诅咒（−0.032 [−0.047, −0.016]）；排除：编造名是记混的近邻（约一半不在数据里）。

同段定稿树原文见 P151 的备查。

## P155 · HTML v75 p155 · pptx S163 (v22z) — How the pieces fit: the story map, step by step (part 1 of 4)

**要说的话（一句英文一句中文）**
This flowchart shows how each step of the story depends on the one before: thick arrows say what is handed down, and the experiments hang under each step.
这张流程图显示故事的每一步怎样依赖上一步：粗箭头写着交下去的是什么，实验挂在每一步下面。
Step one is the phenomenon, recognised but not said: the multiple-choice test defines the groups, and the gap appears only at the output, 0.21.
第一步是现象：认得但说不出。选择题测试定义分组，差距只在输出端出现，0.21。
On the left, the small-sample results were rescued by the full cohort and pre-registration, and statistical artefacts were ruled out.
左边，小样本的结果由全队列和预注册补救，统计假象被排除。
Step two is read early: put-back and take-away agree that the title is read by layer 52, and the colon follows the question.
第二步是读得早：放回和拿走一致，标题到第 52 层读完，冒号跟着问题走。
The step-one experiments now carry their numbers: the name prior is about 19 percent of the gap, the R0-only recount gives 0.20 with the same shape, and recognising needs about 40 citations against about 11,000 for writing.
第一步下面的实验现在标了数字：名字先验约占差距的 19%，只用 R0 重算得到 0.20、形状相同，认得大约需要 40 次引用，写出则要大约 11,000 次。
The dashed box on the right is a known gap: recognition is defined only in the multiple-choice prompt and never measured inside it. Next part.
右边虚线框是一个已知缺口：“认得”只在选择题的 prompt 里定义，从没在它内部测过。看下一部分。

**备查（不念）· 本页幻灯片全文：** How the pieces fit: the story map, step by step (part 1 of 4) Now asking: how does each step of the story depend on the one before, and which experiments carry it? [figure: flow 16x9 a] So (this slide): each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt. summary; two known gaps

**备查（不念）· 证据强度：** descriptive（页底标签“summary; two known gaps”）。流程图是示意图，没有画数值，所以没有公式 / n 行（prepublish 例外已登记）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（故事拼图）

**第 ① 步　现象：认得但说不出**
- 上游依赖：无，这是起点。
- 合力：
  - 选择题识别测试（树 1 ①）定义谁算"认得"、谁算"说不出"：A 组 4,110 篇。没有它就没有分组。
  - 名字先验和名字合理性检查（树 1 ③④）说明认得的差距不是名字好猜。没有它，差距可能只是常见名字。
  - 分组比较（树 1 ⑤⑥⑦）把差距定位在最后几层，输出端 +0.207。没有它不知道差距在哪层出现。
  - 只用 R0 重算（树 1 ⑧）说明不是部分写出的论文在撑。
  - 曝光门槛（树 1 ⑩⑪）把"说不出"量化成曝光差距，ρ 点估计 276。没有它只知道有差距、不知道差多少。
- 救场：小样本阶段（树 3 第 0 批）的认得 − 认不得差距靠少数几对撑着，促成全队列和预注册，现象才在全队列上重新确立。
- 排除：认得的论文读得更早（树 7 第三批：认得只改变大小，不改变时间）；统计方法造成的假象（树 7 第二批）。
- 例外和保留：低引用档里"认得"的比例偏高（25.5%），"认得"不等于一定存着这篇论文；ρ 的规则在看过数据后锁定，只确认 ρ > 1。
- 下游留给谁：差距只在最后几层出现，那么模型是什么时候读标题的？交给第 ② 步。另有一个**已知缺口 ②**："认得"只在选择题的 prompt 上定义，从未在该 prompt 的内部测量过。

**第 ② 步　读得早：标题和问题在什么时候被读**
- 上游依赖：第 ① 步的分组（target / control）和打分方式（真 − 5 个假标题）。
- 交叉验证：放回（给回去能恢复，L48 0.821、L52 0.995）和拿走（L52 起切断损失 ≤ 0.05）方向相反，都指向"L52 前读完"（树 4 ①）。只有其中一个方向，就不能排除方法本身的偏差。
- 排除：5 个假标题下时间一致（树 4 ②），排除"只是某一个假标题碰巧"。
- 合力（问题这一侧）：冒号换问题 vs 换论文的距离比（树 2 ①）和 probe 迁移（树 2 ②）说明冒号跟着问题走。
- 救场：格式锁定检验读出 L56，补充实验发现那是切掉 sink 的假象，patching 从反方向交叉检验（树 2 第二批）。没有补充实验，就会误以为格式到 L56 才定下来。
- 例外和保留：格式到底在哪一层固定，定不下来；年份 / 领域无法测。
- 下游留给谁：标题被读了，读走的是什么？交给第 ③ 步。

**备查（不念）· 图中新增的元素：** 图中第 ① 步的实验条加了数字（name prior ~19% of the gap；R0-only recount +0.20, same shape；exposure: recognise ~40 vs write ~11,000 citations, ρ ~276）；左栏小样本救场框写明 pilot 50 → 200 papers，true title +9 / +5 pp。

## P156 · HTML v75 p156 · pptx S164 (v22z) — How the pieces fit: the story map, step by step (part 2 of 4)

**要说的话（一句英文一句中文）**
Part two: steps three and four.
第二部分：第三步和第四步。
Step three: what is delivered is meaning and specific words, not paper identity; the made-up title brings back about 75 percent.
第三步：送去的是意思和具体用词，不是论文身份；编造标题能找回大约 75%。
The gap left here is: if only meaning is delivered, where does the knowledge of who wrote this paper enter?
这里留下的缺口是：如果送去的只是意思，“谁写的这篇论文”从哪里进来？
Step four: where it goes and by which route; position patching, windowed edge blocking and the single-layer sweep together say names from title, several layers in parallel.
第四步：送到哪里、走哪条路；逐位置替换、窗口式切断注意力边和单层扫描合起来说明：名字看标题，多层并行。
On the left, one route through one layer is overturned. Next part.
左边，“一条路、一层”被推翻。看下一部分。

**备查（不念）· 本页幻灯片全文：** How the pieces fit: the story map, step by step (part 2 of 4) Now asking: how does each step of the story depend on the one before, and which experiments carry it? [figure: flow 16x9 b] So (this slide): each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt. summary; two known gaps

**备查（不念）· 证据强度：** descriptive（页底标签“summary; two known gaps”）。流程图是示意图，没有画数值，所以没有公式 / n 行（prepublish 例外已登记）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（故事拼图）

**第 ③ 步　送去的是意思和具体用词，不是论文身份**
- 上游依赖（跨树依赖）：路线树"标题在 L52 前送到名字位置"（第 ② 步）。没有它，"送去的是什么"无从谈起。
- 前导："哪些标题词带着信号"（树 3 ⑤）提出问题：换成同义词大部分信号还在。由编造标题检验回答。
- 合力（缺一不可）：
  - 编造标题检验（树 3 ⑥）：大部分靠意思（0.751），还剩一小块（+0.106）。没有它不知道有这一小块。
  - 多出部分在哪层出现（树 3 ⑦⑧）：这一小块很晚才出现，在标题位置还不明显。
  - 稀有词 vs 常见词（树 3 ⑨a）：这一小块挂在稀有、具体的词上。
  - 认得 / 引用数检查（树 3 ⑨b）：它和"认识这篇论文"无关，引用多的反而更小。没有它，不能排除"只有认得的论文才有"。
  - 方差分解（树 3 ⑨c）：统计上看不到身份的位置。
  - 属性子空间替换（树 3 ④）：那块子空间里几乎没有作者信息。
- 救场：天花板审计（树 3 第一批）撤回了早期"换问题检验支持身份"的读法。
- 排除：字面重叠（来源检查）、主题先验（主题配对与确认检验）。
- 例外和保留：L8 起的姓氏信号是锁定的小例外（T1 稳健，T2、T3 刚过线，约一半来自主题）。
- 下游留给谁：如果送去的只是意思，"谁写的这篇论文"从哪一步进来？→ **已知缺口 ①**，见第 ⑥ 步。

**第 ④ 步　送到哪里、怎么走**
- 上游依赖：第 ② 步"L52 前读完"。
- 合力：
  - 位置与组件 patching、逐位置替换（树 4 ⑨⑩）：信号主要落在名字位置；没有哪一个部件单独带着全部信号。
  - 窗口式切断注意力边（树 4 ⑪）：找到名字 ← 标题这条边，在 L44–L55 承担输送。
  - 单层扫描（树 4 ⑬）：切掉任何一层最多损失 1.25%，是多层并行。没有它，会误以为是单层单路径。
  - 层顺序（树 4 ⑭）：给出先读标题、再送达、最后说出的先后。
- 推翻："单一路径、单一层"的说法。
- 下游留给谁：送到名字位置时是什么形式？交给第 ⑤ 步。

## P157 · HTML v75 p157 · pptx S165 (v22z) — How the pieces fit: the story map, step by step (part 3 of 4)

**要说的话（一句英文一句中文）**
Part three: steps five and six.
第三部分：第五步和第六步。
Step five: in what form it is held; the same-scale test shows the probe beats the lens, the information is spread out, and the MLPs at layers 52 to 56 carry paper information, not names.
第五步：以什么形式存着；同尺度检验显示 probe 胜过 lens，信息是分散的，第 52 到 56 层的 MLP 带的是论文信息，不是名字。
Made-up names are ruled out as mixed-up neighbours.
编造的名字被排除是记混的近邻。
Step six: who writes the name; the mean ablation shows the MLPs at layers 57 to 61 write it, with the signal on surnames and full given names.
第六步：谁写出名字；均值消融显示第 57 到 61 层的 MLP 写出它，信号在姓和完整的名上。
The dashed gap is still there: no direct test of where the knowledge of who wrote this paper enters. Next, the last part.
虚线缺口还在：没有直接检验“谁写的这篇论文”从哪里进来。看最后一部分。

**备查（不念）· 本页幻灯片全文：** How the pieces fit: the story map, step by step (part 3 of 4) Now asking: how does each step of the story depend on the one before, and which experiments carry it? [figure: flow 16x9 c] So (this slide): each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt. summary; two known gaps

**备查（不念）· 证据强度：** descriptive（页底标签“summary; two known gaps”）。流程图是示意图，没有画数值，所以没有公式 / n 行（prepublish 例外已登记）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（故事拼图）

**第 ⑤ 步　以什么形式存着**
- 上游依赖：第 ④ 步"送到名字位置"。
- 前导：早期 lens 比较没有定论、probe 能读出一点（树 5 第 0 批），提出 H3。
- 合力：作者提示 lens 读不出（树 5 ①），probe 在标题和名字位置读得出（树 5 ②③④）。
- 救场：同尺度检验（树 5）把 probe 和 lens 放在同一把尺子上比，L48 probe 比 lens 高 +0.062。没有它只能比方向、不能比大小。
- 合力（信息分散）：作者子空间只带过去约 7%（树 5 ⑤），差异分散在很多方向上（树 5 ⑥），没有更早的集中存放处（树 5 ⑦）。
- L52–L56 MLP 携带的内容（树 4 ⑫）：带的是论文信息，不是现成的名字方向。
- 例外和保留：注入作者方向（树 5 ⑧）主要是写入通道，不能说明模型存着自己的知识却没用上；L48 上 lens 为负、probe 为正，方向相反，没有解释。
- 下游留给谁：线性可读的信息怎样变成名字？交给第 ⑥ 步。

**第 ⑥ 步　谁写出名字**
- 上游依赖（跨树依赖）：第 ④ 步"送到名字位置"、第 ⑤ 步"不是现成的名字"。
- 证据：L57–L61 均值消融（树 6 ⑨）：MLP − 注意力平均 +0.040，名字由后期 MLP 写出。
- 合力（名字的哪一部分）：首 token 和其余部分（树 6 ①）、名有助于写姓（树 6 ②）、信号在哪些 token（树 6 ③）、合作者（树 6 ④）。信号主要在姓和完整的名上，首字母很弱。
- 排除：编造名不是记混的近邻（树 6 ⑦⑧）。
- 下游留给谁：**已知缺口 ①**：送去的是意思，"谁写的这篇论文"这一知识从哪一步进来，目前没有实验直接回答。L52–L56 MLP patching和 L57–L61 均值消融只是间接证据。

## P158 · HTML v75 p158 · pptx S166 (v22z) — How the pieces fit: the story map, step by step (part 4 of 4)

**要说的话（一句英文一句中文）**
Part four: step seven, where it gets stuck.
第四部分：第七步，卡在哪里。
Giving the first initial helps, 4.0 to 15.2 percent; strengthening the signal does not, 2.5 to 2.8 percent; pushing hurts through direction; and late suppression affects about one paper in eight.
给出名首字母有帮助，4.0% 到 15.2%；加强信号没有用，2.5% 到 2.8%；推法的伤害来自方向；后期压制影响大约八分之一的论文。
On the left, the reversal curse is ruled out and the idea that the signal is too weak is overturned.
左边，反转诅咒被排除，“信号太弱”被推翻。
Joint conclusion: the bottleneck is the late writing step, not signal strength.
合起来的结论：瓶颈在最后的写出这一步，不在信号强弱。
Gap one: where the knowledge of who wrote this paper enters — do the late MLPs hold this paper’s author knowledge? That is not tested yet.
缺口一：“谁写的这篇论文”从哪里进来——后面的 MLP 里有没有这篇论文的作者知识？这一点还没有检验。
A new box at the bottom covers robustness across all steps: four pre-registered replication batches changed no conclusion, and neither did the name prior by layer.
底部新加了一个框，讲所有步骤的稳健性：四批预注册的复现没有改变任何结论，逐层的名字先验也没有。
Next, which experiments build each sentence of the story.
接下来看故事的每一句由哪些实验搭起来。

**备查（不念）· 本页幻灯片全文：** How the pieces fit: the story map, step by step (part 4 of 4) Now asking: how does each step of the story depend on the one before, and which experiments carry it? [figure: flow 16x9 d] So (this slide): Gap ①: where “who wrote this paper” enters — do the late MLPs hold this paper’s author knowledge? Not tested yet. summary; two known gaps

**备查（不念）· 证据强度：** descriptive（页底标签“summary; two known gaps”）。流程图是示意图，没有画数值，所以没有公式 / n 行（prepublish 例外已登记）。

**备查（不念）· 定稿树原文**（出处 27_v67/experiment_tree.md；树里的页码是旧编号，已删去，对应页见本讲稿各页标题）：（故事拼图）

**第 ⑦ 步　卡在哪一步**
- 上游依赖（跨树依赖）：第 ⑥ 步"L57–L61 由 MLP 写出"、路线树"L52 前送到"。
- 合力：
  - 给出名首字母（树 6 ⑤）：补上名字开头有帮助（认得的论文 4.0% → 15.2%）。
  - 名字链（树 6 ⑥）：合作者的帮助来自合作网络，不是论文特有的。
  - 加强已到达的信号（树 6 ⑩）：写对率 2.5% → 2.8%，推翻"信号太弱"。
  - 为什么加强有害（树 6 ⑪）：伤害来自方向，不来自信号量。
  - 后期压制（树 6 ⑫）：约八分之一的论文名字先升后降，认得的略多（刚过界）。
- 排除：反转诅咒（树 6 ⑬：从作者生成标题反而略难）。
- 结论：瓶颈在最后的写出这一步，不在信号强弱，也不是存储方向的问题。
- 下游留给谁：后期 MLP 里是否装着这篇论文的作者知识？→ **已知缺口 ①**，目前没有实验。

**两个已知缺口**
1. 如果送去的只是意思，"谁写的这篇论文"从哪一步进来？目前没有实验直接回答。L52–L56 MLP patching和 L57–L61 均值消融只是间接证据。
2. "认得"只在选择题的 prompt 上定义，从未在该 prompt 的内部测量过；所有内部测量都是在开放提问的 prompt 上做的。

**备查（不念）· 图中新增的元素：** 图底新增“Robustness across all steps”框（四批预注册复现：false titles、all-token probes、position and component patching、completed groups，结论都没变；name prior by layer 不改结论；paper vs team 区间宽度比 ~1，"excludes 0" 在 1,155 行里变了 2 行）。

## P159 · HTML v75 p159 · pptx S167 (v22z) — From experiments to the story (1 of 2): which experiments build sentences 1–4

**要说的话（一句英文一句中文）**
This page and the next turn the hundred experiments back into the story: each band is one sentence on the right, built by the experiments on the left; thick lines are the main line.
这一页和下一页把一百个实验变回故事：每一条带子是右边的一句话，由左边的实验搭起来；粗线是主线。
Sentence one, recognised but not said, needs four main-line experiments together: the multiple-choice test defines who is recognised, the name-prior check shows it is not just guessable names, the group comparison shows recognised papers pull ahead only at the end, and the exposure threshold gives the 276-fold gap.
第一句“认得但说不出”要四个主线实验合起来：选择题测试定义谁算认得，名字先验检查说明不只是容易猜的名字，分组比较显示认得的论文只在最后才拉开，曝光阈值给出 276 倍的差距。
Sentence two, that at layers 0 to 4 the words decide everything, rests on one audit, the ceiling audit; it overturned the early claim of paper identity, so this sentence is grey: it cannot be decided.
第二句“第 0 到 4 层由字决定一切”只靠一项审计，也就是天花板审计；它推翻了早期“支持论文身份”的说法，所以这一句是灰色：定不下来。
Sentence three, early read-in with the colon following the question, comes from the colon test, new question versus new paper, plus the layer-8 surname test, the one small locked exception.
第三句“早期读入、冒号跟着问题走”来自冒号检验，换问题对比换论文，再加上第 8 层的姓氏检验，也就是那个锁定的小例外。
Sentence four, meaning and specific words but not paper identity, needs five together: swapping the paper-facts subspace, the made-up title, rare versus common words, the recognition and citation check, and the variance split.
第四句“读走的是意思和具体用词，不是论文身份”要五个合起来：替换论文信息子空间、编造标题、稀有词对常见词、认得和引用数检查、方差分解。
The thin cards underneath are supporting tests; the dashed ones ruled out an alternative. Next, sentences five to seven.
下面的细线小卡片是辅助检验，虚线的那些排除了另一种解释。接下来是第五到第七句。

**备查（不念）· 本页幻灯片全文：** From experiments to the story (1 of 2): which experiments build sentences 1–4 Now asking: which experiments carry each sentence of the story, and how do they combine? [figure: exp2story a] So (this slide): S1 rests on four main-line experiments together, S2 on one audit (it cannot decide), S3 on two, S4 on five together. summary; 24 of 100 experiments are main line

**备查（不念）· 证据强度：** descriptive（页底标签“summary; 24 of 100 experiments are main line”）。这是故事图示意图，没有画数值，所以没有公式 / n 行。

**备查（不念）· 主线实验（★，出处 27_v67/experiment_contribution.md）：**
- Multiple-choice recognition test（S1，✓）：defines "recognised" and the groups (A 4,110)
- How much is just the name prior?（S1，✓）：paper-specific part remains after the name prior
- Recognised papers pull ahead only late（S1，✓）：gap +0.207 at the output, ≈ 0 in the middle
- Exposure threshold 276×（S1，✓）：writing needs far more exposure (ρ > 1)
- ":" new question vs new paper（S3，✓）：":" moves 4.7× more for a new question
- Ceiling audit（S2，✗）：withdrew "change-the-question supports identity"
- Swap only the paper-facts subspace（S4，✓）：that subspace holds no author info (0.004)
- Made-up title test（S4，✓）：meaning brings back ~75%; small extra remains
- Rare vs common words（S4，✓）：extra sits on rare words (0.162 vs 0.027)
- Recognised / citation check（S4，✓）：extra not tied to recognition; reversed for citations
- Variance split（S4，✓）：identity adds ≈ 0 beyond text
- L8 surname confirmatory test（S3，✓）：small locked exception beyond topic (T1 +0.046)

## P160 · HTML v75 p160 · pptx S168 (v22z) — From experiments to the story (2 of 2): which experiments build sentences 5–7

**要说的话（一句英文一句中文）**
Sentence five, delivered to the names over many layers in parallel and read by layer 52, rests on a cross-check: put-back and take-away agree on layer 52, position by position it lands on the names, the windowed edge test finds the names-from-title edge, and the single-layer sweep finds no single bottleneck.
第五句“经过多层并行送到名字、第 52 层读完”靠的是交叉验证：放回和拿走在第 52 层一致，逐位置看它落在名字上，窗口式切边找到名字看标题这条边，单层扫描找不到单一瓶颈。
Sentence six, held at the names but not as words, combines one overturned claim, the format-locking test, with three positives: the MLPs at layers 52 to 56 carry paper information, the author-prompt lens reads nothing, and the same-scale probe reads more.
第六句“存在名字位置、但不是以词的形式”把一个被推翻的说法，也就是格式锁定检验，和三个正面结果合在一起：第 52 到 56 层的 MLP 带论文信息，作者提示 lens 读不出，同尺度的 probe 读得更多。
Sentence seven, the late MLPs write the name and it gets stuck at writing, combines first token versus the rest, giving the first initial and the mean ablation at layers 57 to 61, with one overturned claim: strengthening the arrived signal does not help.
第七句“后面的 MLP 写出名字，卡在写出这一步”把第一个 token 对其余部分、给出名首字母、第 57 到 61 层均值消融合起来，再加一个被推翻的说法：加强已到达的信号没有用。
Under sentence seven, gap one is still open: at which step does the knowledge of who wrote this paper enter? We only have indirect evidence.
第七句下面，缺口一还开着：“谁写的这篇论文”在哪一步进来？我们只有间接证据。
The grey box on the right counts the 24 experiments that added little: early small samples, method checks and infeasible designs. Next, all hundred at a glance.
右边灰色的框数的是贡献很小的 24 个实验：早期小样本、方法检查和做不成的设计。接下来一眼看完全部一百个。

**备查（不念）· 本页幻灯片全文：** From experiments to the story (2 of 2): which experiments build sentences 5–7 Now asking: which experiments carry the last three sentences, and what is still missing? [figure: exp2story b] So (this slide): S5 rests on a cross-check (put back and take away agree); S6 and S7 each combine positive results with an overturned claim; gap ① is still open. summary; one known gap

**备查（不念）· 证据强度：** descriptive（页底标签“summary; one known gap”）。这是故事图示意图，没有画数值，所以没有公式 / n 行。

**备查（不念）· 主线实验（★，出处 27_v67/experiment_contribution.md）：**
- Format locking + supplement + patching + L56 swap（S6，✗）：overturned "format fixed at L56"; layer not pinned down
- Put-back / take-away tests（S5，✓）：opposite directions agree: read by L52
- Position by position（S5，✓）：lands mainly on the names (0.835 at L52)
- Windowed attention-edge blocking（S5，✓）：name ← title edge carries delivery L44–L55
- What the L52–L56 MLPs carry（S6，✓）：paper information, not ready-made names
- Single-layer sweep（S5，✓）：no single-layer bottleneck (≤ 1.25% each); overturned "one route"
- Lens fitted on author prompts（S6，✓）：lens cannot read it (≤ 0 at L24–L56)
- Name-position probe + same-scale test（S6，✓）：probe beats lens on one scale (+0.062 L48)
- First token or the rest（S7，✓）：the start of the name is hardest
- Giving the first initial（S7，✓）：supplying the first piece helps (4.0% → 15.2%)
- Mean ablation L57–L61（S7，✓）：the late MLPs write the name (+0.040)
- Strengthening the arrived signal（S7，✗）：overturned "the signal is too weak"
缺口 ①：“谁写的这篇论文”在哪一步进来，只有间接证据。

## P161 · HTML v75 p161 · pptx S169 (v22z) — What each experiment contributed: all 100 at a glance

**要说的话（一句英文一句中文）**
This page shows all hundred experiments at once, one column per tree, each cell marked with what it contributed.
这一页一次展示全部一百个实验，每棵树一列，每个格子标出它贡献了什么。
Forty-eight advanced the story, five overturned an earlier claim, twelve ruled out an alternative, eleven could not decide, and twenty-four added little.
48 个推进了故事，5 个推翻了早先的说法，12 个排除了另一种解释，11 个定不下来，24 个贡献很小。
The bold-bordered cells are the 24 main-line experiments, the ones on the previous two pages.
粗边框的格子是 24 个主线实验，就是前两页上的那些。
The overturned ones matter too: the ceiling audit, the format-locking test and the strengthening test each removed a wrong sentence from the story.
被推翻的那些也重要：天花板审计、格式锁定检验和加强信号检验，各自从故事里拿掉了一句错话。
So the story rests on 24 main-line experiments; the rest support it, rule things out, or mark what is still open. Next, what we learned, in words.
所以故事靠 24 个主线实验；其余的在支持它、排除别的解释，或者标出还没解决的地方。接下来用文字总结我们学到了什么。

**备查（不念）· 本页幻灯片全文：** What each experiment contributed: all 100 at a glance Now asking: how many experiments advanced the story, overturned a claim, ruled out an alternative, could not decide, or added little? [figure: contrib overview] So (this slide): 48 advanced the story, 5 overturned an earlier claim, 12 ruled out an alternative, 11 could not decide, 24 added little; 24 are main line. summary of the experiment tree

**备查（不念）· 证据强度：** descriptive（页底标签“summary of the experiment tree”）。这是故事图示意图，没有画数值，所以没有公式 / n 行。

**备查（不念）· 计数（出处 27_v67/experiment_contribution.md）：** ✓ 48 · ✗ 5 · ⊘ 12 · ~ 11 · ○ 24；★ 主线 24（共 100）。各树：Overview 3、Phenomenon 12、H1 5、H2 26、Route 10、H3 14、Writing 15、Audits 15。

## P162 · HTML v75 p162 · pptx S170 (v22z) — What we learned: read early, spoken late

**要说的话（一句英文一句中文）**
This page brings the main findings together: read early, said late.
这一页把主要发现放在一起：读得早，说得晚。
Read early: the title is read between layers 24 and 50 and gathered at the name positions by layer 52, after which it is no longer needed.
读得早：标题在第 24 到 50 层被读，到第 52 层汇集到名字位置，之后就不再需要。
Said late: at the name positions, paper-specific author knowledge becomes readable by lens only from about layer 50, fastest over layers 57 to 61.
说得晚：在名字位置，论文特有的作者知识要从大约第 50 层起才能被 lens 读出，在第 57 到 61 层增长最快。
And it is real knowledge: the name prior is only part of the gap, and the rest is about this paper and grows with citations.
而且这是真正的知识：名字先验只占差距的一部分，其余是关于这篇论文的，并随引用数增长。
Next, who writes it and what it needs.
下一页看谁写出它、它需要什么。

**备查（不念）· 上一版讲稿本页全文（原第 P94 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 六条结论：
- **读得早：** 因果上，标题在 L24–L50 被读取，到 L52 汇集到名字位置，之后就不再需要。标题 token 处的 probe 从 L24 起能读出一点（已复核）。
- **说得晚：** 在名字位置，论文特异的作者知识只有从约 L50 起才能被 lens 读出，L57–L61 增长最快。
- **lens 没有提前：** 在名字处用 lens 读，中间层 target 并不领先 control；+0.21 的差距出现在最后（Stage 10，final L63，§6.4）（标题处的 probe：target − control +0.03–0.08，已复核；Stage 13 E4b，只看第一个名字 token）。
- **是真知识：** 名字先验总体约占差距的 1/3，但在姓氏上约 0（Stage 12 A，0.087 / 0.247，§6.12）；其余是论文特异的，并随引用增长。
- **lens 之间一致：** Jacobian lens 在中间层读出更多，但没有 target 特异的内容。
- **名字格式：** 首字母携带的信息很少；完整的名和姓氏携带的信息一样多，并能帮助预测姓氏。

**关键数字：** 见上；n = 9,108（读出）· 1,186（干预）· 1,395（probe）。

**结论状态：** 汇总页：前两条和"lens 没有提前"、"lens 之间一致"、"名字格式"为定论；probe 部分为初步；"是真知识"为初步（名字先验的估计依赖删除标题条件）。

**过渡：** 接着讲是谁写下了答案、需要什么条件，以及每条的状态。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(Stage 10, final L63, §6.4)
- 出处（原在幻灯片上）：(Stage 12 A, 0.087 / 0.247, §6.12)

## P163 · HTML v75 p163 · pptx S171 (v22z) — What we learned, continued: who writes it, what it needs

**要说的话（一句英文一句中文）**
This page continues: who writes the name, and what it needs, each with its evidence strength.
这一页接着讲：谁写出名字，它需要什么，每一条都标了证据强度。
The late MLPs write it, which is settled; the title enters the name positions mainly in one step at layer 48; and the name-from-title edge is the largest, though each cut costs little.
后面的 MLP 写出它，这是定论；标题主要在第 48 层那一步进入名字位置；名字看标题这条边最大，但切断任何一处代价都不大。
Writing needs about 276 times the exposure of recognising, and a first-initial hint helps.
写出需要的曝光大约是认出的 276 倍，首字母提示有帮助。
The co-author chain is real but comes from the network, and the made-up names are not near-misses.
合作者链是真的，但来自合作者网络；编造的名字也不是“差一点就对”。
Next, the whole answer on one map.
下一页把整个答案放在一张图上。

**备查（不念）· 上一版讲稿本页全文（原第 P95 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 七条，每条带状态：
- **后层由 MLP 写入：** L57–L61 每一层消融 MLP 的代价都大于消融 attention，+0.040 [0.036, 0.045]，定论（锁定判据成立）→ 第 77 页。L52–L56 的 MLP 携带论文信息，大部分在作者名字方向之外，描述性 → 第 76 页。
- **由名字位置承载（新）：** 标题主要在 L47 → L48 这一步进入名字位置（恢复 0.31 → 0.61；L52 时 0.84）；':' 晚到，描述性（硬检查 WARN）→ 第 74 页。在一个 4 层窗口里切断一条注意力边，代价 ≤ S 的 3.5%；名字 ← 标题是 L44–L55 中最大的一条，判据成立，对窗口位置稳健（修正后的步长 2 检查：11 个重叠窗口中 7 个，L42–L57，同一条边）→ 第 75 页。
- **曝光差距：** 认出论文约需 40 次引用，写出作者约需 11,000 次，ρ = 276 [203, 390]，确认（锁定在看过数据之后；回忆门槛接近引用范围顶端）→ 第 29 页。
- **含义而非字面：** 随机替换内容词会抹掉标题信号（损失 0.374，S = 0.328）；WordNet 同义词只损失 0.087，描述性（同义词很粗糙）→ 第 84 页。
- **早期痕迹：** 名字之前，年份 / ':' / 第一个标题 token 带有微弱的作者痕迹，+0.008 到 +0.049；59 个格子满足锁定规则，672 个检验格子中 60 个 CI > 0，没有多重比较校正，探索性 → 第 72 页。
- **格式与链：** 给出名首字母（F4）对认得出的论文帮助更大，A − B +0.085 [0.047, 0.124]，支持（只有 F4）。真合作者有帮助（+0.167 [0.147, 0.185]），但不是 title-specific（+0.012 [−0.001, 0.025]），是合作者网络关联 → 第 59–60 页。
- **编造的名字：** 大约一半不在数据里，和打乱基线一样（50.4% vs 50.5%）；合作者只占 4.0%（随机 1.3%）：是看起来合理的名字，而不是混淆的邻居，探索性（不支持）→ 第 93 页。probe 只在 L40–L52 胜过输出置信度（C24），探索性（未定）→ 第 92 页。
- 右图"穿过各层的路线"：≤ L16 标题事实在标题处可读（M2）→ L24–L50 标题被读取（L48 patching R ≥ 0.5）→ L48 attention 把标题带进来（P2 0.237）→ L52–L56 MLP 携带论文信息（R 0.158–0.275；名字方向 0.022–0.042）→ L57–L61 MLP 写入（MLP − attention 损失 +0.040）→ L63 说出作者。

**关键数字：** n = 600 篇（补充 18b）· 9,108（补充 19）· 1,200 / 1,428（补充 16 B / D）· 8,872 篇中 40,219 个名字（C）· 518（C24）。

**结论状态：** 各条状态见上（MLP 写入：定论（锁定判据成立）；名字位置承载：描述性；单条注意力边：预注册判据成立、对窗口位置稳健（效应小）；曝光差距：锁定在看数据之后，按初步处理；标题用词：描述性；早期痕迹：探索性；格式：预注册判据成立（仅 F4）；名字链：预注册判据成立但非论文特异；编造名字：探索性）。

**过渡：** 下一页列出已经做了什么，以及剩下的局限。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{loss}(c)=S(\mathrm{none})-S(c)$ · $\rho=c_{50}^{\mathrm{recall}}/c_{50}^{\mathrm{recog}}$；② n = 600 papers (route tests) · 9,108 · 1,200 / 1,428 (format / chain) · 40,219 names · 518 papers；③ loss > 0: that part carries the signal / ρ > 1: writing needs more exposure；原公式框：loss(c) = S(none) − S(c), ρ = c 50 recall / c 50 recog n = 600 papers (add. 18b) · 9,108 (add. 19) · 1,200 / 1,428 (add. 16 B / D) · 40,219 names in 8,872 papers (C) · 518 (C24)。

**备查（不念）：**
- 原写 “(C24)”、路线图 “(P2 0.237)”、“(M2)”、n 行 “(add. 18b)”：C24 = 自写名字 probe 检验（补充 15 第 2-11b 项），P2 = 注意力 / MLP patching，M2 = 标题处属性 probe，18b = 后续检验（600 篇）

## P164 · HTML v75 p164 · pptx S172 (v22z) — Summary S1: the answer on one map

**要说的话（一句英文一句中文）**
This page puts the whole answer on one map: the prompt tokens across, the 64 layers up.
这一页把整个答案放在一张图上：横着是提示词的每个 token，竖着是 64 层。
Read early, said late: the bottleneck is the late writing step, not reading.
读得早，说得晚：瓶颈在最后的写出这一步，不在读。
The title is read and delivered to the name positions by about layer 52, but the name is written only at layers 57 to 61, and that is where recall stalls.
标题大约在第 52 层读完并送到名字位置，但名字要到第 57 到 61 层才写出来，回忆就卡在那里。
The next five pages walk along this map, one step at a time.
接下来五页沿着这张图一步一步走。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S1 ← slide 129: who writes it, what it needs. Here: the whole answer on one map → step by step, slides 131–135 Read early, said late: the bottleneck is the late writing step, not reading. Now asking: putting every result together, where does recall of a paper’s authors break? So (section): the title is read and delivered by about L52; the name is written only at L57–L61, and recall stalls there.

数字出处：27_v67/fragments/part7_numbers.md

## P165 · HTML v75 p165 · pptx S173 (v22z) — Summary S2: step 1, the question

**要说的话（一句英文一句中文）**
Step one: when does the model settle that it must answer with names?
第一步：模型什么时候确定要用名字来回答？
The question is read at the colon: at layer 4 a new question moves the colon state 4.7 times as far as a new paper, and still 2.2 times at layer 48.
问题在冒号处被读到：第 4 层换问题时冒号状态的移动是换论文时的 4.7 倍，到第 48 层仍有 2.2 倍。
Swapping the colon state at layer 56 lowers the author signal, which we measured.
在第 56 层替换冒号状态会降低作者信号，这是测出来的。
But the locked format test also cut the attention sink, so the layer where the format is fixed is not pinned down.
但锁定的格式检验同时切掉了 attention sink，所以格式在哪一层定下来，定不下来。
Next, steps two and three: the title.
下一页是第二、三步：标题。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S2 ← slide 130: the map. Here: step ① → step ②③, slide 132 ① The question is read at “:”, but the layer that fixes the format is not pinned down Now asking: when does the model settle that it must answer with names? Evidence (▲ intervention · ◉ readout) ◉ descriptive At L4 a new question moves the “:” state 4.7× as far as a new paper; still 2.2× at L48. → slide 150 ▲ locked rule downgraded Knocking the question out at “:”: the locked rule gave L56, but that test also cuts the attention sink. With the sink kept, the names format holds from early layers (clue) . → slide 52 ▲ locked · supported Swapping the “:” state at L56 lowers the author signal (measured); the layer where the format is fixed is not pinned down. → slide 52 Strength: locked rule downgraded for the layer; descriptive for the question signal at “:”. Type: ▲ intervention (knockout, swap) + ◉ readout (state distance). Rules out: Nothing yet: the earlier claim “format fixed in the middle layers” no longer holds. Caveat: names are also the default answer; year / field questions are not interpretable with the current measure. So (this slide): the question is read at “:”, but at which layer the format is fixed stays open.

数字出处：27_v67/fragments/part7_numbers.md

## P166 · HTML v75 p166 · pptx S174 (v22z) — Summary S3: steps 2 and 3, the title

**要说的话（一句英文一句中文）**
Steps two and three: when is the title read, and what about it is used?
第二、三步：标题什么时候被读，用到的是它的哪一部分？
Putting the true-title states back restores about 82% of the advantage at layer 48 and nearly all at layer 52, and taking the title away from layer 52 costs almost nothing.
把真标题的状态放回去，第 48 层恢复约 82% 的优势，第 52 层几乎全部恢复；从第 52 层起拿走标题几乎没有代价。
What is read is mostly the topic on the spine: a card with the same topic gets about 75% of the way, and synonyms keep most of the signal.
读到的主要是书脊上的主题：同主题的卡片能走到约 75%，同义词保留了大部分信号。
With one small locked exception: from layer 8 the title state carries a little of this paper's surname beyond its topic, locked at layer 8, larger at later layers but descriptive only.
外加一个小的锁定例外：从第 8 层起，标题状态在主题之外带着一点这篇论文的姓氏信号；锁定检验在第 8 层，后面几层更大，但只是描述性的。
Next, step four: delivery to the names.
下一页是第四步：送到名字位置。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S3 ← slide 131: step ①. Here: steps ②③ → step ④, slide 133 ②③ The title is read by L52 — for its meaning and specific words Now asking: when is the title read, and what about it is used? Evidence (▲ intervention · ◉ readout) ▲ settled Put back: about 82% of the true-title advantage restored at L48, ≈ 100% at L52 (five false titles); taking the title away from L52 on costs ≤ 0.05. → slides 45, 46 ▲ locked · supported A same-meaning made-up title gets about 75% of the way (φ = 0.751); the real title adds +0.106 . → slide 73 ▲ descriptive Synonyms keep most of the signal (loss 0.087 vs 0.374 for random words); rare words carry more than common ones. → slides 72, 80 ◉ locked One small exception: a surname signal beyond topic from L8, +0.046 [0.035, 0.056] in the locked test at L8; larger at later layers (peak L40, descriptive); beyond a weak text baseline and larger for recognised papers only marginal ; about half of it is topic. → slides 70, 81 Strength: settled timing; locked · supported meaning; the surname exception is small, two of its three tests marginal . Type: ▲ intervention (put back, take away, made-up titles, word swaps) + ◉ readout (surname decoding). Rules out: Paper identity as a general representation: the real-title extra is not larger for recognised papers and is smaller for more-cited ones → slides 78, 79 . Caveat: the text baseline for the surname test failed its positive control; rare-word swaps replaced more words than common-word swaps. So (this slide): the title is read early for what it means and its specific words, not as a “which paper” label (one small exception).

数字出处：27_v67/fragments/part7_numbers.md

## P167 · HTML v75 p167 · pptx S175 (v22z) — Summary S4: step 4, delivery

**要说的话（一句英文一句中文）**
Step four: how does the title's information get to where the name is written?
第四步：标题的信息怎么到达写名字的地方？
Copying one position group at a time, the name positions carry most of it, about 0.84 at layer 52, and the colon joins late.
每次复制一组位置，名字位置承载了大部分，第 52 层约 0.84，冒号加入得晚。
Blocking one attention edge, name from title is the largest, but each cut costs at most a few percent.
阻断单条注意力边，名字看标题这条最大，但每次切断最多只损失几个百分点。
So the information arrives over parallel routes, with no single bottleneck.
所以信息是通过多条并行路线到达的，没有单一瓶颈。
Next, step five: how it is held at the names.
下一页是第五步：它在名字位置以什么形式存着。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S4 ← slide 132: steps ②③. Here: step ④ → step ⑤, slide 134 ④ The title’s information reaches the name positions by L52, along parallel routes Now asking: how does the title’s information get to where the name is written? Evidence (▲ intervention · ◉ readout) ▲ descriptive Copying one position group at a time: the name positions carry most of it, 0.835 at L52; “:” joins late. → slide 95 ▲ fairly solid Blocking one attention edge in a 4-layer window: name ← title is the largest edge in L44–L55, but each cut costs ≤ 3.5% of S. → slide 96 ▲ locked Blocking one edge at one layer: several small edges carry it, no single route. → slide 104 Strength: fairly solid for the edge; locked for “no single route”. Type: ▲ intervention only (patching, attention blocking). Rules out: One dominant attention edge carrying the paper to the name. Caveat: every single cut is small, so most of the route is still unexplained. So (this slide): the title’s information arrives at the name positions by about L52, through many small routes.

数字出处：27_v67/fragments/part7_numbers.md

## P168 · HTML v75 p168 · pptx S176 (v22z) — Summary S5: step 5, held at the names

**要说的话（一句英文一句中文）**
Step five: once the information has arrived, can the model already see the author?
第五步：信息到达之后，模型是不是已经“看得见”作者？
On the same 9,137 name tokens, a probe separates recognised from unrecognised papers better than the lens, which is a locked result.
在同样的 9,137 个名字 token 上，probe 区分认得和认不得论文的能力强于 lens，这是锁定的结果。
The lenses see the difference only in the last layers.
lens 只在最后几层才看得到差别。
Injecting the probe's author direction makes the model write that author, but mainly as a write channel.
注入 probe 的作者方向能让模型写出那个作者，但主要是一个写入通道。
So the author information is there, but not in vocabulary directions. Next, steps six and seven: writing.
所以作者信息在那里，只是不在词表方向上。下一页是第六、七步：写出。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S5 ← slide 133: step ④. Here: step ⑤ → steps ⑥⑦, slide 135 ⑤ At the name positions the author information is there, but not in vocabulary directions Now asking: once the information has arrived, can the model already “see” the author? Evidence (▲ intervention · ◉ readout) ◉ locked · supported Same-scale test on the same 9,137 name tokens: probe − lens +0.021 [0.008, 0.034] at L40, +0.062 [0.041, 0.081] at L48. → slide 99 ◉ descriptive Lenses see target ≠ control only in the last layers. → slide 41 ▲ locked Injecting the probe’s author direction makes the model write that author, but mainly as a write channel; only a small part is specific to recognised papers. → slide 105 ◉ exploratory Recognition moves many quiet directions, not one author axis (clue) . → slide 100 Strength: locked · supported for “there but not in vocabulary directions”; injection locked . Type: mostly ◉ readout (probe vs lens) + ▲ injection. Rules out: “No author information before the output”: a probe finds it from the middle layers. Caveat: a probe readout is correlational; injection mostly writes rather than unlocks. So (this slide): the author information is present at the names, in directions the output does not read directly.

数字出处：27_v67/fragments/part7_numbers.md

## P169 · HTML v75 p169 · pptx S177 (v22z) — Summary S6: steps 6 and 7, writing

**要说的话（一句英文一句中文）**
Steps six and seven: who writes the name, and where do recognised-but-unsaid papers fail?
第六、七步：谁写出名字，认得却说不出的论文在哪里失败？
The MLPs of layers 57 to 61 write the name; ablating them costs about 0.04 per layer, while attention costs about nothing.
第 57 到 61 层的 MLP 写出名字；消融它们每层损失约 0.04，注意力几乎没有损失。
Strengthening the arrived information does not help, and pushing harder hurts through its direction.
加强已到达的信息没有帮助，推得更用力反而会因为方向而造成损害。
A first-initial hint helps recognised papers more, and the surname's first token is the hardest.
首字母提示对认得的论文帮助更大，姓的第一个 token 最难。
So recall stalls at the writing step. Next, the evidence ledger.
所以回忆卡在写出这一步。下一页是证据账本。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S6 ← slide 134: step ⑤. Here: steps ⑥⑦ → the evidence ledger, slide 136 ⑥⑦ The L57–L61 MLPs write the name — and recall stalls at that step Now asking: who writes the name, and where do recognised-but-unsaid papers fail? Evidence (▲ intervention · ◉ readout) ▲ settled Mean ablation: MLP − attention +0.040 [0.036, 0.045] at L57–L61; attention ≈ 0. → slide 122 ▲ locked · not supported Strengthening the arrived information does not help; pushing harder hurts, and the damage is direction-driven. → slides 123, 106 ▲ locked · supported Giving the first initial helps recognised papers more, +0.085 [0.047, 0.124]. → slide 33 ◉ descriptive The surname’s first token is the hardest (≈ 0.1 vs ≈ 0.45 for later tokens). → slide 114 ◉ exploratory In a minority of papers the true name rises after L56 and then falls (clue) . → slide 124 Strength: settled who writes; locked · not supported “a stronger signal fixes it”; locked · supported first-initial help. Type: ▲ intervention (ablation, injection, a given initial) + ◉ readout (token ranks). Rules out: “The arrived signal is just too weak”. Caveat: late suppression is only a clue; which heads or neurons push the name down is untested. So (this slide): the bottleneck is the late writing step, starting with the first name token.

数字出处：27_v67/fragments/part7_numbers.md

## P170 · HTML v75 p170 · pptx S178 (v22z) — Summary S7: evidence ledger

**要说的话（一句英文一句中文）**
This page puts every claim on one sheet: the claim, its test, how strong it is, what it rules out, and what doubt remains.
这一页把每条结论放在一张表上：结论、对应的检验、证据强度、排除了什么、还有什么疑点。
The settled parts are the timing of the title and the late MLP writing.
定论部分是标题读取的时间和后期 MLP 的写出。
The locked parts are the same-scale probe result, the made-up-title test and the small surname exception, which is locked at layer 8 with two marginal checks.
锁定的部分是同尺度 probe 结果、编造标题检验，以及那个小的姓氏例外——它在第 8 层锁定，另两项检验刚过线。
The format layer and the exposure ratio carry stated doubts.
格式层和曝光比值都标明了疑点。
Next, what the tests rule out.
下一页看这些检验排除了什么。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S7 ← slide 135: steps ⑥⑦. Here: every claim on one sheet → what was ruled out, slide 137 Evidence ledger: each claim, its test, and how strong it is Now asking: which parts of the answer rest on what, and how firmly? Claim Evidence Strength Rules out Open doubt Slides Recognised but not said exposure needed to write ≈ ρ = 276× that to recognise locked (lock after data) “the model never saw the paper” lock made after the data 24 ① Question read; format layer open “:” tracks the question; format knockout locked rule downgraded “format fixed in the middle layers” sink cut; year / field 150, 52 ② Title read by L52 put back · take away, five false titles settled “the title is read late” “fully read” is a description 45, 46 ③ Meaning + specific words made-up title 75% · synonyms · rare words locked · supported paper identity as a general code one small surname exception from L8 (locked at L8; 2 of 3 marginal) 73, 72, 80, 81 ④ Parallel routes to the names position patching · edge blocking fairly solid one dominant edge each cut small 95, 96, 104 ⑤ Held, not in vocabulary directions probe vs lens, same scale · injection locked · supported “no author info before the output” correlational; mostly a write channel 99, 105 ⑥ MLPs write at L57–L61 mean ablation, MLP vs attention settled attention writes the name which MLP units write it is untested 122 ⑦ Stalls at writing strengthening fails · first initial helps locked “the signal is too weak” late suppression only a clue 123, 33, 125, 124 Method: conclusions use only settled and locked results; descriptive and exploratory rows are clues. Colour: row colour = strength of the claim. So (this slide): ② and ⑥ rest on settled interventions, ③, ⑤ and ⑦ on locked tests; ① and the surname exception are the soft spots.

数字出处：27_v67/fragments/part7_numbers.md

## P171 · HTML v75 p171 · pptx S179 (v22z) — Summary S8: ruled out

**要说的话（一句英文一句中文）**
This page lists four tempting explanations that the tests reject.
这一页列出四种看似合理、但被检验否定的解释。
Paper identity as a general representation: the same-topic card gets 75% of the way, and the extra does not grow with recognition; the one small surname exception remains.
论文身份作为一般表示：同主题卡片能走到 75%，多出的部分不随“认得”变大；只剩那个小的姓氏例外。
Strengthening the arrived signal: adding more does not help, and harder pushes hurt.
加强已到达的信号：加得再多也没用，推得更用力反而有害。
The reversal curse: generating the title from the authors is slightly harder, not easier; the locked reading is “reversed”.
反转诅咒：从作者生成标题反而稍难，而不是更容易；锁定判定是“反向”。
And literal word overlap: removing papers with overlap changes nothing. Next, how this fits earlier work.
还有字面重叠：去掉有重叠的论文，结果不变。下一页看这些结果和已有工作怎么对上。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S8 ← slide 136: the ledger. Here: what the tests reject → comparison with earlier work, slide 138 Ruled out: four explanations the tests reject Now asking: which tempting explanations do the results exclude? Explanation Paper identity as a general representation ↓ Test A same-meaning made-up title gets 75% of the way; the real-title extra is not larger for recognised papers and is smaller for more-cited ones. ↓ Verdict locked · not supported ✕ ruled out one small locked exception: the surname signal from L8 (two of three tests marginal, about half topic) → slides 73, 78, 79, 81 Explanation Strengthening the arrived signal ↓ Test Adding more of the arrived information does not make the model write the author; pushing harder hurts. ↓ Verdict locked · not supported ✕ ruled out → slide 123 Explanation The reversal curse, in free generation ↓ Test Given the true authors, the true title is far more likely for recognised papers; but generating the title from the authors is slightly harder than recalling the authors from the title. ↓ Verdict locked: reversed ✕ ruled out → slide 125 Explanation Literal word overlap ↓ Test Synonyms keep most of the title signal; the surname test excluded titles containing the surname and still passed. ↓ Verdict descriptive ✕ ruled out synonym test descriptive; the exclusion is part of the locked surname test → slides 72, 81 Method: each card = one explanation → the test that could have supported it → the verdict. Caveat: “ruled out” means not supported by a locked test, not proven impossible. So (this slide): the failure is not a missing “which paper” code, a weak signal, a reversal effect, or word copying.

数字出处：27_v67/fragments/part7_numbers.md

## P172 · HTML v75 p172 · pptx S180 (v22z) — Summary S9: earlier work

**要说的话（一句英文一句中文）**
This page asks what we add to what was known.
这一页问：我们在已知的基础上补充了什么？
Geva and colleagues showed that attribute extraction runs in three steps, ending with attention moving the attribute to the last position; our results are consistent with that.
Geva 等人证明了属性提取分三步，最后由注意力把属性搬到最后一个位置；我们的结果和这一点一致。
We add a separate late writing stage in the MLPs of layers 57 to 61, a parallel route rather than one edge, and the place where recall fails.
我们补充的是：第 57 到 61 层 MLP 里一个独立的后期写出阶段，并行的路线而不是单一一条边，以及回忆失败的位置。
Gekhman and colleagues showed that models hold more than they say; we show where that knowledge arrives, how it is carried, and where saying it breaks.
Gekhman 等人证明了模型知道的比说出来的多；我们说明了这些知识在哪里到达、怎么被搬运、在哪里说不出来。
Next, the open questions.
下一页是未解决的问题。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S9 ← slide 137: ruled out. Here: how this fits earlier work → open questions, slide 139 Where this fits: Geva et al.’s extraction steps, plus a late writing stage Now asking: what do we add to what was known? Geva et al. (EMNLP 2023) Gekhman et al., “Inside-Out” (COLM 2025) This work Main claim Attribute extraction runs in three steps: subject enrichment → relation propagation → attention extraction at the last position. Models hold hidden knowledge: they know more than they say. Consistent with the three steps; adds a separate late writing stage (L57–L61 MLPs) and localises where recall fails. Route Attention moves the attribute from the subject to the last position. — A parallel route: several small edges, no single dominant one. Where it fails Not the focus. Shows that hidden knowledge exists. Shows where it arrives, which route carries it, what writes it and where it fails. Evidence Interventions on factual recall. Internal scores compared with generated answers. Causal tests plus readouts, pre-registered decision rules. So (this slide): we confirm the known extraction steps and add where they end: a late writing stage that recognised-but-unsaid papers fail.

数字出处：27_v67/fragments/part7_numbers.md

## P173 · HTML v75 p173 · pptx S181 (v22z) — Summary S10: open questions

**要说的话（一句英文一句中文）**
This page asks what would make the answer strong enough to publish.
这一页问：要让这个答案强到可以发表，还需要什么？
First, replicate the core results on a second model; that is the biggest reviewer risk.
第一，在第二个模型上复现核心结果；这是审稿人最大的质疑点。
Second, freeze papers we have never used, lock the rules, and re-run the main results once as one confirmatory table.
第二，冻结从未用过的论文，锁定规则，把主要结果重跑一次，做成一张确认性的表。
Third, a causal test of the writing step; then a better measure for the year and field format question, and a check of the multiple-choice distractors.
第三，对写出这一步做因果检验；然后为年份、领域的格式问题找一个更好的测量，并检查多选题的干扰项。
That closes the summary. Next, the checks and limits.
总结部分到此结束。下一部分是检查和局限。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Summary · S10 ← slide 138: earlier work. Here: what is still open → checks and limits, slide 140 Open questions and next steps Now asking: what would make the answer strong enough to publish? 1. Second model must do Next: Replicate the arrival curve, the probe–lens gap, late-MLP writing and the made-up-title test on another model. Why: biggest reviewer risk 2. Held-out locked replication must do Next: Freeze unused papers, lock the rules, re-run the main results once as one confirmatory table. Why: answers “too many tests” 3. Causal test of the writing step must do Next: Give the first name token and let the model continue; a linear subspace test at L48–L56; look at the late-suppression heads. Why: step ⑦ is still partly a clue 4. H1 follow-up open Next: A year / field measure with enough baseline accuracy, and the gentle knockout as the locked test. Why: step ① not pinned down 5. Multiple-choice distractor check open Next: Topic-matched distractors may relabel some recognised papers. Why: group labels Status: must do = needed before submission; open = closes a known soft spot. So (section): one model and many tests are the main risks: a second model and one locked held-out replication come first.

数字出处：27_v67/fragments/part7_numbers.md

# Part 8 · Checks and limits (174–181)

## P174 · HTML v75 p174 · pptx S182 (v22z) — What the small samples taught us to watch for

**要说的话（一句英文一句中文）**
This page lists the traps the small samples taught us to watch for.
这一页列出小样本教会我们要提防的陷阱。
A single paper can carry a layer peak; a contrast can rest on a few pairs; a layer chosen after many looks is a forking path; and candidate names can share first tokens.
一篇论文就能撑起一个层峰值；一个对比可能只靠少数几对；看了很多次才选定的层是分叉路径；候选名字可能共享第一个 token。
Labels are noisy, the first author does not stand for the team, and a better-fitting lens does not mean better author ranks.
标签有噪声，第一作者代表不了整个团队，拟合得更好的 lens 也不等于作者排得更好。
The full-cohort design answers each of these, but not one: the groups still come from the same model's own labels.
全队列的设计逐条回应了这些问题，但有一条解决不了：分组仍然来自同一个模型自己的标签。
Next, small against large in one table.
下一页用一张表对照小样本和全队列。

**备查（不念）· 上一版讲稿本页全文（原第 P63 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 列出八种陷阱：单篇杠杆（一篇论文占 Stage 4 L56 均值的 71%，20 篇）；尾部驱动（Stage 8 A−B 去掉 100 对中的 10 对后消失）；分叉路径（L56 被反复查看，然后被定为主层）；候选伪影（100 个假名字只有约 46 个不同的第一个 token；3% 和金标平局，156/5,000）；标签噪声（0–2 引用档严格"通过"率 25.5%）；覆盖不全（用第一作者代表整个团队）；指标选择（KL 保真度和作者排名不一致）；协议漂移（计划在 10-18 14:29 锁定，7 层积分为主终点；21:14 的 PROTOCOL 改成 L56，两者都在 8C 打分之前；由谁、为什么改仍未知，U28）。

**关键数字和 CI：**
- 单篇杠杆：全部 20 篇 0.0070，去掉一篇 0.0021，share = 71%（audit_report.md）。
- 尾部驱动（Stage 8D，A − B，L56）：全部 +5.0 pp → 去掉前 5 对 +1.9 pp → 去掉前 10 对 −0.4 pp（100 对，200 篇）。
- n = 20 篇（Stage 4）· 100 对（8D）· 5,000 个假名字（7.2）· 796 篇（0–2 档）。

**结论状态：** 描述性（方法学教训）。Stage 10 在设计上逐条回应了这些问题：全队列、每个作者和 token、报告所有层、全词表排名、档内比较、冻结输入加 parity 检查。它解决不了的是：分组仍然来自同一个模型的同一次标注运行。

**过渡：** 把小样本和全队列的结论放进一张表。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{share}=x_{(1)}/\sum_i x_i$；② n = 20 papers · 100 pairs · 5,000 false names · 796 papers (0–2 bin)；③ share near 1: one item carries the effect；原公式框：share = x (1) / Σ i x i n = 20 papers (Stage 4) · 100 pairs (8D) · 5,000 false names (7.2) · 796 papers (0–2 bin)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(8D, matched_pair_differences.csv)
- 出处（原在幻灯片上）：(7.2 quality.json: 156/5,000)
- 出处（原在幻灯片上）：(label_README.md)

**备查（不念）：**
- 原写 “who and why open (U28)”、n 行 “(audit_report.md)”：U28 = 未解决问题清单第 28 条；audit_report.md = Stage 4 审计报告

## P175 · HTML v75 p175 · pptx S183 (v22z) — Small vs large, in one table

**要说的话（一句英文一句中文）**
This page compares the small-sample findings with the full cohort, item by item.
这一页逐项对照小样本的发现和全队列的结果。
The true title helps: confirmed. Recognised beats unrecognised: confirmed, but only in the late layers.
真标题有帮助：确认。认得胜过认不得：确认，但只在后期层。
The key layer, 56, was refined: the rise starts there, the steepest part is 57 to 61, and the title is read much earlier.
关键层第 56 层被细化了：上升从那里开始，最陡的是第 57 到 61 层，而标题早得多就读了。
The Jacobian lens reads more name shape but no paper identity, and the first-token puzzle is explained by name format.
Jacobian lens 读出更多名字形状，但读不出论文身份；第一个 token 的谜题由名字格式解释。
Next, the remaining checks.
下一页看剩下的检查。

**备查（不念）· 上一版讲稿本页全文（原第 P64 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 逐项对照并给出判定：
- 真标题有用：pilot +9.3 pp、新 200 篇 +5.2 pp → L62 title-specific 约 0.44 → **confirmed**。
- 认得出 > 认不出：不确定、靠尾部 → 输出 +0.21，L24–L40 约 0，L48 略负（−0.04 到 −0.05）→ **confirmed，只在后层**。
- 同组比较（A vs B，只看 R0）：输出 +0.20（§6.13），形状相同；R1 只增加强度，不改变时间 → **comparable, unchanged**。
- 关键层：L56 → 从 L56 开始，L57–61 上升，L24–50 被读取 → **refined**。
- J-Lens 相对 Vanilla：没有增量 → 更多名字形状，没有论文身份 → **consistent**。
- 第一个 vs 其余：差距在后续 token → 由首字母 vs 完整的名解释 → **explained**。
- 引用：低−高没有结论 → 单调，ρ = 0.451（X2_spearman.csv）→ **resolved**。
- lens 稳定性：split-half 只有一次切分，Stage 9 只有 Fit A → 在不同文本上拟合的三种 Jacobian lens 结果一致；拟合稳定性只靠 Stage 9 Fit A → **只有一项证据，Fit B 未完成**。
- 下方条形图：每项分析的论文数（对数轴），Stage 4 · 20、Pilot50 · 50、Stage 8 · 200、补充 18b · 600、Stage 11–12 · 1,186、Stage 10 · 9,108。

**结论状态：** 汇总表（前七项为定论级判定；lens 稳定性证据不足）。

**过渡：** 进入 Stage 12–13：既然中间层在名字处读不出作者，那中间层里到底存着什么？先用三张方法图说明。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $\mathrm{spec}=\mathrm{nlr}_{\mathrm{true}}-\mathrm{mean}_5\,\mathrm{nlr}_{\mathrm{false}}$ · $T-C\ \mathrm{within\ bin}$；② n = 20–200 papers (Stages 1–9) · 9,108 (Stages 10–11)；③ T − C > 0: recognised papers’ authors read better than control；原公式框：spec = nlr true − mean 5 nlr false ; T − C within bin n = 20–200 papers (Stages 1–9) · 9,108 (Stages 10–11)。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 幻灯片上改用通俗名称（原内部标签 / 文件名移到这里）："route tests · 600" ← "add. 18b · 600"; removed sources: (X3_means.csv), (X2_spearman.csv)
- 出处（原在幻灯片上）：(§6.4)
- 出处（原在幻灯片上）：(§6.13)

## P176 · HTML v75 p176 · pptx S184 (v22z) — Retrieval, behaviour and interval checks

**要说的话（一句英文一句中文）**
This page asks what could still be wrong.
这一页问：还有什么地方可能出错？
The retrieval check is at the ceiling: the title state finds the same paper at layer 4, as a text-only model does from its first layer, because the title text is identical.
检索检查在天花板上：标题状态在第 4 层就能找回同一篇论文，纯文本模型从第一层起也能，因为标题文字完全相同。
The other checks use existing data and are descriptive, and paper-level and team-level intervals agree.
其他检查用的是已有数据，属于描述性；论文级和团队级的置信区间是一致的。
So nothing here changes a conclusion. Next, the pre-registered replication batches.
所以这里没有改变任何结论。下一页看几批预注册的复现。

**备查（不念）· 上一版讲稿本页全文（原第 P102 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**本页在问（标题下一行小字）：** “Now asking: what could still be wrong?” —— 还有什么可能出错？

**先讲怎么做（指着左边的方法图）：** X5：在问题 1 下取一篇论文最后一个标题 token 的状态，在问题 2 下所有 9,108 篇论文的状态里找最近的一个，看是不是同一篇；逐层算 top-1 命中率（也在冒号位置算）。

**再讲结果（指着左下折线）：** 标题 token：L4 1.000，L44 0.9999，L48 0.984，输出 0.734；从未超过 L4 —— 这是天花板，因为标题文字相同（纯文本 BERT 从第 1 层起也是 1.000）。冒号（灰虚线）从 L8 后下降。
- 右栏其他检查（已有数据，描述性）：M3 行为分数（年份 T − C +0.007 [0.003, 0.012]；所有作者 +0.234 [0.215, 0.252]）；N2 按层（输出 +0.047，logit L62 +0.039，J-lens L48 −0.133）；论文级 vs 团队级区间（宽度比 0.97–1.00，1,155 行中 2 行改变）；M5（输出 0.919；logit L24 0.516 → L62 0.899；标题 / 冒号 probe AUROC 0.50–0.52）。
- 公式（灰字）：retrieval(l) = P(问题 2 下最近的状态是同一篇)，9,108 篇；n = 9,108 篇（X5、M3）· 4,621 / 2,220（M3 T − C）· 1,155 区间行。

**So 行：** 跨问题检索从 L4 起就到了天花板，所以不能说明身份；行为、先验和区间检查都不改变任何结论。

**结论状态：** 描述性；X5 预注册，判据不成立（从未超过 L4）。

**过渡：** 下一页汇总按事先固定规则做的复现及其状态。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** ​(X5: summary_x5/x5_retrieval.csv, team CI · other checks: m3 behaviour (2-10), N2, interval comparison, summary_m5 (as on the previous version of this page))。

## P177 · HTML v75 p177 · pptx S185 (v22z) — Replications with rules fixed first (four pre-registered batches)

**要说的话（一句英文一句中文）**
This page lists the replications run with the rules fixed before the results.
这一页列出几批在结果出来之前就定好规则的复现。
For every item, reproducing the published numbers was a hard check.
每一项都把能否重现已发布的数字作为硬性检查。
Four batches were run; the conclusions did not change, and the deviations are recorded.
一共跑了四批；结论没有改变，偏离都做了记录。
Next, the limits.
下一页是局限。

**备查（不念）· 上一版讲稿本页全文（原第 P103 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 所有规则都在结果出来之前固定；能否重现已发布的数字是每一项的硬性检查；状态截至 2026-11-08。
- 先完成：5 个假标题的 X7；全 token probe（补充 9）；CPU 项 C-1 到 C-5；C-3b（不排除的敏感性分析，含泄漏，不作结论）。
- Batch 1（补充 10），已完成：所有作者的 X1–X4 → 结论不变（X1 与任务无关，L48 有小的 author − year +0.024；X3 保留约 90%；X4 从 L8 起；X2 搬动 0.032，子空间 R² ≤ 0.009，X2 单独看 H3 证据不足）；E4b 按 donor 排除（4,654 篇，每篇约 1.5 个假标题）：姓氏 L40 +0.076 [0.068, 0.083]，姓氏 − 首字母 +0.033；5 个假标题的 P1 / P2（以五标题均值为主，false_0 并列）：每个 mean5 − false_0 的 CI 都包含 0 → 结论不变；冒号分子 B/A 0.72–0.87；p9：每个假标题 694–711 篇，集合不同，不加权。
- Batch 2（补充 11、12）：进行中；C / D 补齐完成（C 462 篇；档内 462 篇中 258 篇 vs A：L52 时 R 约 1）；2-11 因硬性检查停止 → 2-11b（补充 15）已完成：预注册判定在全部 7 层通过（C24；置信度检查非预注册：大部分可由输出置信度解释，现为未定，探索性）；2-2、2-3、2-4、2-5（名字位置 probe：H3 部分支持；2026-11-14 补充 17 第 2 项之后在同一尺度上得到支持）、2-8、2-10 完成；Patchscope（2-7、2-9）完成（仅描述）；2-1：偏离 D12-5（门控参照用错了精度，f64 vs fp32 日志；不是放宽判据）；门控改为 fp32 vs fp32 后恢复，gate v4 已排队；偏离已记录（D12-1 到 D12-3；2-7 来源 = 不含年份的 X4 提示）。
- Batch 3（补充 14）：3-1 Stage 10 L41–L47、L49 完成；3-2 L0–L23 于 2026-11-13 完成，通过硬性检查；3-3 Stage 7.1B 快速路径停止（偏离 D14-1；与旧的逐前缀结果是否等价未确认）；3-4 / 3-5（Stage 8 GPU W）未运行。
- 未做：Stage 8 用 GPU 重跑原始 W（用户 2026-11-06 决定；改用 CPU 代理 C-2）。

**结论状态：** 状态页（绿色 = 完成、结论不变；蓝色 = 完成但记录了偏离；橙色 = 部分停止 / 未运行）。

**过渡：** 最后一页：哪些局限是重跑也去不掉的。

**备查（不念）· 2026-11-23 公式行统一：** 图下固定三行灰字（不念）：① $R(l)=\mathrm{mean}(\mathrm{patched}-\mathrm{false})/\mathrm{mean}(\mathrm{true}-\mathrm{false})$；② n = 4,654 (probe) · 694–711 per false title · 462 (C) · 582 test pairs；③ R ≈ 1: fully restored; R ≈ 0: nothing restored；原公式框：R(l) = mean(patched − false) / mean(true − false)；原公式框：n = 4,654 (E4b) · 694–711 / false title (P1/P2) · 462 (C) · 582 test pairs。

**备查（不念）· 2026-11-23 移出幻灯片的标签和出处：**
- 出处（原在幻灯片上）：(b1_xall_report.md)
- 出处（原在幻灯片上）：(b1_e4b5_report.md)
- 出处（原在幻灯片上）：(b1_p12f_report.md)
- 出处（原在幻灯片上）：(prereg_addendum12_deviations.json)
- 出处（原在幻灯片上）：(prereg_addendum14.json)
- 出处（原在幻灯片上）：(c13_C2.md)

**备查（不念）：**
- 标题原写 “(addenda 10–14)”；正文与流程框原写内部编号：addendum 9 = 按角色全 token 打分；batch 1 = 补充 10，batch 2 = 补充 11、12，batch 3 = 补充 14，2-11b = 补充 15；X7 = 五个假标题复跑；C-1 … C-5 = CPU 复核项，C-3b = 不排除敏感性分析，C-2 = Stage 8 CPU 代理；X1 复制进另一标题、X2 子空间交换、X3 改写、X4 早期第一作者 probe（不含年份提示）；E4b = 旧版第一个 token probe（按 donor 排除）；P1 / P2 = 位置 / 分量 patching；2-11 = 自写名字 probe 检验（C24，slide 92）；2-2 … 2-5 = probe 项（含名字位置 probe），2-8、2-10 = 其余两项，2-7、2-9 = Patchscope；2-1 = 门控项（偏离 D12-5），D12-1 … D12-3 = 其余偏离；3-1 = Stage 10 L41–L47、L49，3-2 = L0–L23，3-3 = Stage 7.1B 快速路径（偏离 D14-1），3-4 / 3-5 = Stage 8 GPU W；addendum 17 item 2 = 锁定的名字位置检验；“p9:” = batch 1 中该项的内部编号

**备查（不念）：**
- 标题原写 “(addenda 10–14)”；HTML 目录菜单同步改为幻灯片标题 “(four pre-registered batches)”

## P178 · HTML v75 p178 · pptx S186 (v22z) — Limits

**要说的话（一句英文一句中文）**
This page lists what was done and the limits that remain.
这一页列出已经做了什么，以及仍然存在的局限。
There is one model; teacher forcing measures preference, not generation; and the labelling code is not available to re-check.
只有一个模型；teacher forcing 测的是偏好而不是生成；标注代码拿不到，无法复核。
Several recent results carry their own stated limits, such as rules locked after the data, or no correction for many cells.
最近的几项结果各自带有明确的局限，比如规则是在看过数据后锁定的，或者很多格子没有做多重比较校正。
Next, the limits that new runs cannot remove.
下一页是新的运行也去不掉的局限。

**备查（不念）· 上一版讲稿本页全文（原第 P96 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**【2026-11-22 v55 · H2 新措辞（用户确定，状态仍为 partly supported）】** 讲这句（英文原句，屏幕上同样写法）：“H2 partly supported: a real-title extra over a same-meaning fabricated title exists (R̄_T +0.106), mostly carried by meaning (75%). The extra sits mainly on the title's rare and specific words (names, acronyms, technical terms): replacing only those words loses R̄ = 0.162, vs 0.027 for common words (addendum 24). It is not larger for recognised papers (K4 not supported) and is smaller for more-cited papers (K4c reversed). Whether the extra reflects specific wording or a penalty on fabricated titles remains open.” 紧接着说明补充 24 的两点：（补充 24 的两点说明：两种替换的词数不同，罕见词平均换 3.4 个、常见词 2.1 个；常见词是按词频匹配替换，不是同义词，意思也会改变。） 中文意思：H2 部分支持：真标题比意思相同的编造标题多出一部分（R̄_T +0.106），大部分由意思承担（75%）。多出的部分主要落在标题里罕见、具体的词上（人名、缩写、专门术语）：只替换这些词损失 R̄ = 0.162，只替换常见词损失 0.027（补充 24）。它在认得出的论文上并不更大（K4 不支持），在引用多的论文上反而更小（K4c 反向）。这多出的部分反映的是具体措辞，还是模型对编造标题的惩罚，仍未确定。

**这页做什么：** 已完成：Stage 12 单位置 patching（P1）、attention vs MLP（P2，hook 检查通过）、名字先验（N1、N2）、作者提示 lens（F1、F2：中间层仍然读不出）；Stage 13 中 probe 在标题处 ≤L16 就能读出年份、引用、领域（M2），身份不超过 L4 文本水平（M3），替换与任务无关（X1），改写在 L28–L40 体现出超出字面的含义、但不能与论文身份分开（X3），第一作者在 L8 可解码、可能由文本解释（X4），5 个假标题确认 Stage 11 的时间进程（X6、X7）。局限：只有一个模型（Qwen3-32B）；teacher forcing 测的是偏好而不是生成；标签来自组长的包，标注代码（elm）拿不到；H2（论文身份）部分支持，大部分信号可由语义相似解释（补充登记 20），真标题多出 +0.11；H3（隐藏的作者知识）起初判为证据不足，补充 17 锁定检验后在同一尺度上得到支持（第 68 页）。

**关键数字：**
- 最新结果的局限：补充 19 的规则在看过数据后锁定；回忆 c50 接近引用范围顶端（9,108 篇中 16 篇高于 11,038）。第 1 项：检验 672 个格子，没有多重比较校正。第 5 项：WordNet 同义词粗糙。第 4 / 6 项：每次只动一层一个组件，600 篇子样本，parity WARN（bf16 batch 形状）。补充 16：teacher forcing 偏好，只有贪心解码。C：未预注册。第 2、3 项：600 篇子样本，硬检查 WARN；第 3 项没有判定规则；第 2 项对窗口位置稳健（修正后的步长 2 检查：11 个重叠窗口中 7 个，L42–L57，同一条边）；效应小（≤ S 的 3.5%）。
- 各分析的论文数（对数轴）：标签包 9,108；冻结队列 6,841；probe（Vpd）4,654；Stage 11–12 干预 1,186；补充 18b 600；Stage 8 200；Pilot50 50；Stage 4 20。

**结论状态：** 局限页。

**过渡：** 附录部分：先把组间比较的三个预注册结果单独展开。

**备查（不念）：**
- 原写测试编号：P1 单位置 patching、P2 注意力 vs MLP、N1 / N2 名字先验（合理性 / 纯先验）、F1 / F2 作者提示 lens、M2 属性 probe、M3 换问题对照、X1 复制进另一标题、X3 改写、X4 早期第一作者 probe、X6 / X7 五个假标题复跑；“(add. 22)” = 补充 22（意义 vs 识别）；“addendum-17 locked test” = 锁定的名字位置 probe 检验；方框 “addendum 19” = 曝光门槛，“Item 1 / 5 / 4 / 6 / 2 / 3” = 补充 18b 各项（1 早期痕迹图、5 同义词、4 / 6 消融与 MLP、2 注意力边切断、3 名字到达），“Addendum 16” = 格式与名字链测试；柱图 “add. 18b items” = 后续检验

**2026-11-23 锁定姓氏检验后的口播补充：**

In the limits, H2 now reads: not a general paper identity, with one small locked exception at L8, about half of it topic.  
局限里 H2 现在写成：不是一般的论文身份，只有 L8 一个小的锁定例外，其中约一半是主题。

**备查（不念）· 2026-11-23 锁定姓氏检验（addendum 33，sha 7a28ae2d…，6,048 篇新论文：target 4,577 / control 1,471）：** T1 D_topic(姓首 token, L8) +0.0457 [0.035, 0.056]（Holm 下界 +0.033）；T2 标准化 Qwen − BERT +0.045 [0.008, 0.082]（Holm 下界 +0.002；BERT 基线留出拟合比频率先验差 0.24 log10，正对照未过 = WARN）；T3 target − control（引用档内）+0.025 [0.003, 0.047]（Holm 下界 +0.003）。ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]：约一半信号来自主题；只用 L0 词嵌入 ≈ 0。来源 391_groups/summary_a33/report.md。幻灯片上写白话名“locked surname test”，不写 addendum 编号。不写成“强证据”。

## P179 · HTML v75 p179 · pptx S187 (v22z) — Limits that cannot be redone

**要说的话（一句英文一句中文）**
This page lists the design and data limits that new runs cannot remove.
这一页列出新的运行也去不掉的设计和数据局限。
The groups come from Qwen3-32B's own labels, so the results hold for this model only.
分组来自 Qwen3-32B 自己的标签，所以结果只对这个模型成立。
Every score is the rank the model gives the correct name once it is in the prompt, a preference rather than generation.
每个分数都是正确名字已经在提示里时模型给它的排名，是偏好而不是生成。
And the most-cited bin has no unrecognised papers, so it cannot enter the within-bin comparison.
引用最高的那一档没有认不得的论文，所以它进不了档内比较。
Next, the continued list.
下一页是续表。

**备查（不念）· 上一版讲稿本页全文（原第 P104 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**这页做什么：** 设计和数据层面的局限，新的运行无法消除：
- **一个模型：** 分组（认不认得、写没写出作者）来自 Qwen3-32B 自己的标签，换一个模型就需要重新打标签。
- **Teacher forcing：** 每个分数都是正确名字已经在提示里时模型给它的排名——是偏好，不是生成（C24 用的是模型自己生成的文本，不是 teacher forcing）。
- **标签流程：** 标签包作者的 elm 代码和 run.json 不在集群上，所以生成长度、thinking 模式和多选设置都无法复核。
- **高引用档：** 4097+ 档没有 B / D 论文（84 篇 target，0 篇 control），档内比较用不上它。
- **层与样本：** Stage 10 在 L24–L40 每 8 层采样一次（没有 L25–L31、L33–L39，也不打算补；L41–L47、L49 由 3-1 补上；E1/X6 的 L41–L47、L49、L51 由补充 18 补上）；干预只用了 9,108 篇中的 1,186 篇；分母效应（C 0.559 vs A 0.407）。
- **容差与单一标题：** parity 容差从 0.25 放宽到 0.5，是看过数据后做的改动（主轮 25 对中有 10 对超过 0.25，最大 0.367；大小与 bf16 舍入相符，最多约 0.46）；M5 part B 和 E4b 的 X1 对照流程只用 false_0，没有补跑计划。
- **层间空隙、停止的项目：** X4 的年份起点在 L33–L40 之间某处；Jacobian 和 logit 的跳升在 L32 与 L40 之间；X4 第一作者的峰值可能在 L33–L47；2-11 已停止（名的复现率 0.880 < 0.90）。

**关键数字和 CI：**
- 分母效应（E1 真 − 假差距，未写出作者，false_0）：A 0.407 [0.386, 0.430]（n 557）；B 0.214 [0.196, 0.234]（n 586）；C 0.559 [0.529, 0.590]（n 462）；D 0.197 [0.122, 0.277]（n 33，仅描述）。

**结论状态：** 局限页。

**结束语：** 总结一句：作者信息在标题处很早就被读取，在 L40–L52 传到名字位置，最后由 L57–L61 的 MLP 写成可读的名字；中间层 lens 看不到，但 probe 能在同一尺度上读到微弱信号（H3）。所有这些都只基于一个模型、teacher forcing 下的偏好，以及同一个模型给出的标签。

**图旁 n（灰色行）：** n = A 557 · B 586 · C 462 · D 33 papers (D descriptive)

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** the label package author’s elm code and run.json are not on the cluster, so generation length, thinking mode and the multiple-choice setup；(84 target, 0 control; m3_scores.md §2)。

## P180 · HTML v75 p180 · pptx S188 (v22z) — Limits that cannot be redone (continued)

**要说的话（一句英文一句中文）**
This page continues the list of limits.
这一页继续列局限。
Some layers were sampled only every eighth layer, and are being filled by a pre-registered layer sweep, with results pending.
有些层只是每 8 层采样一次，正在用一个预注册的逐层扫描补上，结果待定。
The interventions use about 1,200 of the 9,108 papers, and denominators differ between groups.
干预实验用了 9,108 篇中的约 1,200 篇，各组的分母也不同。
Next, the denominator effect in one chart.
下一页用一张图说明分母效应。

**备查（不念）· 上一版讲稿本页全文（原第 P105 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This page continues the limits with three more cards.  
这一页接着讲另外三张局限卡片。

Layers and samples: Stage 10 samples L24 to L40 only every eighth layer, and interventions use 1,186 of the 9,108 papers.  
层与样本：Stage 10 在 L24–L40 只每 8 层采样一次，干预只用了 9,108 篇中的 1,186 篇。

So “about zero before L50” rests on sampled layers.  
所以“L50 之前约为 0”依赖于采样到的层。

Tolerance: the parity tolerance was loosened from 0.25 to 0.5 after seeing the data; the gap matches bf16 rounding.  
容差：parity 容差在看过数据后从 0.25 放宽到 0.5；差距与 bf16 舍入相符。

Layer gap and a stopped item: the decode-from-title onset and the self-generated-name check stay uncertain.  
层间空隙和停止的项目：从标题解码的起点层和模型自生成名字的检查仍不确定。

The table on the right says what each limit does to the conclusions: none reverses one.  
右边的表说明每条局限对结论的影响：没有一条推翻结论。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** Stage 10 samples L24–L40 every 8th layer (no L25–L31, L33–L39; no plan to fill; L41–L47, L49 filled by 3-1; E1/X6 L41–L47, L49, L51 filled by addendum 18)。

**备查（不念）：**
- 原写 “no plan to fill” → “being filled by a pre-registered layer sweep; results pending”（用户 2026-11-23）

## P181 · HTML v75 p181 · pptx S189 (v22z) — Limits (2): the denominator effect, in one chart

**要说的话（一句英文一句中文）**
This page shows the denominator effect in one chart.
这一页用一张图说明分母效应。
The gap between true and false titles, which is the denominator of the restored share, differs a lot by group: from about 0.20 to about 0.56.
真假标题之间的差距——也就是恢复比例的分母——在各组之间差别很大：从约 0.20 到约 0.56。
So a group with a small denominator can look as if it restores more, when it actually restores less.
所以分母小的组看起来恢复得更多，实际恢复的量反而更少。
Ratios across groups need the denominators shown next to them. Next, the glossary.
跨组比较比例时，必须把分母一起列出来。下一页是术语表。

**备查（不念）· 上一版讲稿本页全文（原第 P106 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

The true minus false gap, which is the denominator of the restored share, differs a lot by group.  
真减假的差距，也就是恢复比例的分母，在各组之间差别很大。

A is 0.407, B 0.214, C 0.559 and D 0.197.  
A 是 0.407，B 0.214，C 0.559，D 0.197。

So B’s restored share looks higher only because its denominator is small.  
所以 B 的恢复比例看起来更高，只是因为它的分母小。

Ratios across groups need their denominators shown next to them.  
跨组比较比例时，要把分母一起给出。

**备查（不念）· 移出幻灯片的出处（2026-11-22）：** 95% CI · source: 391_groups/b2_cd/summary/cd_group_values.csv (b2_cd_report.md)。

**备查（不念）· 2026-11-23 公式行统一：** 原 “How computed” 段：How computed: denominator = mean_p[T̄_p − F̄_p] (the denominator of recovery(l) = mean_p[P̄_p(l) − F̄_p] / mean_p[T̄_p − F̄_p], false_0) · unwritten authors, Stage 11 sample + a later completion of groups C and D (C 462; D 33 papers descriptive only) · team-cluster 95% CI ·；方法细节移到备用页 B21 (slide 116)。

# Glossary and backups (182–184)

## P182 · HTML v75 p182 · pptx S190 (v22z) — Glossary · plain names ↔ internal codes, reading keys

**要说的话（一句英文一句中文）**
This is the glossary, a reference page we show only if asked.
这是术语表，只有被问到时才展示。
It maps the plain test names on the slides to the internal codes in the reports, and gives the reading of each plotted quantity.
它把幻灯片上的白话测试名对应到报告里的内部代号，并给出每个画出来的量怎么读。

**备查（不念）· 上一版讲稿本页全文（原第 P107 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**

**讲稿（一句英文一句中文）：**

This glossary maps the plain test names on the slides to the internal codes used in the reports and scripts.
这一页把幻灯片上的白话检验名称对应到报告和脚本里的内部编号。

For example, the put-back test is Stage 11 E1 and Stage 13 X6; the take-away test is E2 and X7.
例如，放回检验就是 Stage 11 的 E1 和 Stage 13 的 X6；拿走检验是 E2 和 X7。

The exposure test is addendum 19, and the made-up-title test is addendum 20.
曝光检验是补充登记 19，虚构标题检验是补充登记 20。

The lower half lists how to read each plotted quantity, with the same grey formula and reading line as under the charts.
下半部分列出每个画出来的量怎么读，公式和那一句读法与图下的灰色三行完全一样。

It is not presented; it is there for questions.
这一页不讲，答问时用。

**备查（不念）：** 名称对照来自各轮移出幻灯片的标签清单：hc_pass_20261123/moves_list.md、rollout3_20261123/labels_moved_b7b8.md、rollout4 moved_formula_lines.json + moves_extra.json、rollout5 moved_b1b2.json、rollout6 moved_b3b4.json、rollout7 moved_b6b9.json、rollout8 moved_r8.json。读法一栏逐字照抄图下的灰色读法行；公式取自 hc_pass_20261123/specs.py（ρ 用第 29 页的写法）。新增一行：“:” 位置的换问题 / 换论文比值（备用页 B22）。

## P183 · HTML v75 p183 · pptx S191 (v22z) — Glossary (continued)

**要说的话（一句英文一句中文）**
This continues the glossary with codes from the older reports, also shown only if asked.
这是术语表的续页，列出早期报告里的代号，同样只有被问到时才展示。
For example, the change-the-question test, and the Stage 8 follow-up audit, which was not pre-registered.
比如换问题检验，以及 Stage 8 的补充审计（未预注册）。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Glossary Glossary (continued): codes in the older reports code in the older reports and scripts → plain name on the slides Line A → “Is it about this paper?” (pages of the small-sample line) Line B → “What can each readout see?” Line C → “When does it appear and when is it used?” Line D → “Which token carries it?” RQ1 → title test (true title vs wrong titles) RQ2 → A−B test (recognised vs not, paired) RQ3 → low−high test (citation bands) Stage 8D → Stage 8 replication (200 new papers) Stage 8E → Stage 8 follow-up audit (not pre-registered; unique-token weights, wrong-title length, raw-logit recompute) JMRR → mean reciprocal rank of the name tokens (teacher-forced) M1 → top lens word (top word of the lens in middle layers) M2 → attribute probe (probe reads non-name attributes) M3 → change-the-question test (same title under another question) M4 → author-specific lens (lens fitted on author prompts)

## P184 · HTML v75 p184 · pptx S192 (v22z) — Backup B23 · Earlier evidence-matrix layouts (superseded)

**要说的话（一句英文一句中文）**
This backup page keeps the earlier evidence-matrix layouts for reference, shown only if asked.
这张备用页保留早先几版证据矩阵的版式，只作参考，只有被问到时才展示。
Every matrix in the deck is now drawn from one canonical matrix.
现在 deck 里的每一张矩阵都从同一张标准矩阵生成。

**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**

Backup B23 B23 · Earlier evidence-matrix layouts (superseded) Kept unchanged for reference; every matrix in the deck is now drawn from one canonical matrix (slides 37, 54, 83, 108, 127). Slide 37 · earlier evidence matrix (sample mapping, superseded by the canonical matrix) Evidence matrix — colour = what each result does to the hypothesis (sample mapping, to confirm) result per test → (predictions: boxes above) lens word (measured) probes question swap same-scale test made-up title rewrite test: recognition / citations rare-word test subspace swap / decode test surname test (locked) H1 partly weakens supports – – – – – – H2 partly supports weakens – supports weakens weakens neutral supports (small; T2/T3 marginal) H3 – supports – supports – – – neutral – Slide 127 · earlier evidence-matrix layout (columns by method; superseded by the canonical matrix) Hypothesis Prediction Readout (lens / probe) Replace / knock out Inject / push Rewritten titles · behaviour Result (verdict) H1 · question format the middle layers fix the answer format the “:” state tracks the question (slides 49, 150) format test distorted by cutting the attention sink (slide 52) — — revised: the format layer is not pinned down H2 · paper identity the title state codes which paper it is small surname signal from L8 beyond topic (slide 81) title tokens matter by meaning (slide 72) — same-meaning made-up title gets ≈ 75% (slide 73) not a general paper identity; one small locked exception H3 · held, not in vocabulary a probe sees author information the lens cannot probe beats lens on the same scale (slide 99) names carry most of the restored signal by L52 (slide 95) author direction writes names, mostly any author (slide 105) — supported on the same scale Route one dominant edge carries the title — name ← title strongest at L48/L52; no single-layer bottleneck (slides 96, 104) — — parallel routes Writing step recall fails at the late writing step late rise-then-fall in a subgroup (slide 124) L57–L61 MLPs write (slide 122) more arrived signal does not help (slide 123); direction hurts (slide 106) — the bottleneck Storage direction (reversal curse) authors → title is easier than title → authors given the authors, the title is far more likely for recognised papers (slide 125) — — authors → title slightly harder than title → authors (slide 125) not supported (reading “Reversed”) settled locked · supported locked · not supported descriptive exploratory later part highlighted row = updated by this part

