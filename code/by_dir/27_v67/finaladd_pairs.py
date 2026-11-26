ZH_START = """**出发点：先确认现象，再沿着层往上走**

- **早期小样本**：先导阶段只有 20–200 篇论文，结论靠少数几篇论文撑着，又取决于选哪一层，所以项目转到全队列并预注册 [小样本设计与教训 · 第 5、140、141 页 · descriptive]。
- **扣掉名字先验后的差距**：输出端的 +0.207 是扣掉"名字好不好猜"之后留下的、本论文特有的部分。三项检查支撑这一点：
  - 名字先验有多大：分数可以拆成名字先验、主题和本论文特有三部分，扣掉名字先验后，本论文特有的部分仍有 +0.21（姓的第一个 token +0.42）[名字先验占多少 · 第 68 页 · settled]；删去标题条件下的名字先验是 0.35 [名字合理性与纯名字先验检查 · 第 94 页第 2 项 · settled]。
  - 名字合理性和纯名字先验：纯名字先验的 target − control 只有 +0.047 [0.031, 0.062]，约为真标题下差距（+0.247）的 19% [名字合理性与纯名字先验检查 · 第 94 页第 2 项 · settled]。
  - 只用 R0 论文重算：A − B 是 +0.199，与合并后的 +0.207 形状一样 [只是部分写出的论文在起作用吗 · 第 26 页 · settled]。

"""
EN_START = """**Starting point: confirm the phenomenon, then climb the layers**

- *Early small samples.* The pilot stages had only 20–200 papers; their conclusions rested on a few papers and depended on which layer was chosen, so the project moved to the full cohort with pre-registration [small-sample design and lessons · slides 5, 140, 141 · descriptive].
- *The gap after removing the name prior.* The +0.207 at the output is the paper-specific part left after removing how guessable the names are. Three checks support this:
  - How large the name prior is: the score splits into name prior, topic and a paper-specific part; after removing the name prior the paper-specific part is still +0.21 (+0.42 on the surname's first token) [how much is just the name prior · slide 68 · settled]; the name prior from the delete-title condition is 0.35 [name plausibility and pure name-prior checks · slide 94 item 2 · settled].
  - Name plausibility and the pure name prior: the pure name prior's target − control is only +0.047 [0.031, 0.062], about 19% of the gap under the true title (+0.247) [name plausibility and pure name-prior checks · slide 94 item 2 · settled].
  - Recomputing on R0 papers only: A − B is +0.199, the same shape as the pooled +0.207 [is it only the partly written papers · slide 26 · settled].

"""
ZH_TOK = """- **名字里哪些 token 带信号**：姓的第一个 token +0.68、其余 +0.58，首字母只有 +0.13 [信号在哪些 token · 第 116 页 · full cohort]。前 10 名里有完整的名时，姓的信号是 +0.22；只有首字母时约为 0 [知道名有助于写姓 · 第 115 页 · full cohort]。标题位置的 probe 在 L40 按名字 token 分开读，姓的第一个 token 比首字母高 +0.028 [+0.011, +0.045] [每个名字 token 上的 probe · 第 98 页 · pre-registered]。
"""
EN_TOK = """*Which name tokens carry the signal.* The surname's first token gives +0.68 and the rest +0.58, the initial only +0.13 [which tokens carry the signal · slide 116 · full cohort]. With the full given name in the top 10 the surname signal is +0.22; with only the initial it is about 0 [knowing the given name helps the surname · slide 115 · full cohort]. Read token by token at L40, the title-position probe puts the surname's first token above the initial by +0.028 [+0.011, +0.045] [the probe on every name token · slide 98 · pre-registered].

"""
ZH_EXC = """  - 真名 vs 编造名：中间层区分真名和编造名的 AUROC 是 0.72–0.78，只比输出置信度（0.711）高 +0.050 到 +0.062，而且只在 L40–L52 出现；模型内部对真假只多知道一点 [真名 vs 编造名能否区分 · 第 119 页 · exploratory]。
"""
EN_EXC = """- Real vs made-up names: the middle layers tell real from made-up names at AUROC 0.72–0.78, only +0.050 to +0.062 above output confidence (0.711), and only at L40–L52; the model's internals know only a little more about real vs fake [can real and made-up names be told apart · slide 119 · exploratory].
"""
ZH = [
 ("**L0–L4：输入的字决定了几乎一切**", ZH_START+"**L0–L4：输入的字决定了几乎一切**"),
 ("- **加强没有用，伤害来自方向**：把已到达", ZH_TOK+"- **加强没有用，伤害来自方向**：把已到达"),
 ("约一半根本不在数据里 [编造名字从哪来 · 第 120 页 · exploratory]。\n", "约一半根本不在数据里 [编造名字从哪来 · 第 120 页 · exploratory]；\n"+ZH_EXC),
]
EN = [
 ("**L0–L4: the input words decide almost everything**", EN_START+"**L0–L4: the input words decide almost everything**"),
 ("*Strengthening does not help; the harm comes from direction.*", EN_TOK+"*Strengthening does not help; the harm comes from direction.*"),
 ("about half are not in the data at all [where fabricated names come from · slide 120 · exploratory].\n", "about half are not in the data at all [where fabricated names come from · slide 120 · exploratory].\n"+EN_EXC),
]
