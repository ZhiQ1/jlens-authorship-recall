# A blocks for the five pptx-only slides (keyed by their old heading's pptx number)
A = {
'S27': [
("This page shows how the probe's training samples are built.",
 "这一页说明 probe 的训练样本是怎么取的。"),
("Each paper is one sample: the state at the last title token goes in, and the model's own state where it predicts the author comes out; author teams are kept apart between training and testing.",
 "每篇论文是一个样本：输入是最后一个标题 token 处的状态，目标是模型自己预测作者那个位置的状态；训练和测试时作者团队分开。"),
("We then score the true authors under the true title and under a false title, and the difference is the probe's paper-specific signal.",
 "然后在真标题和假标题下分别给真作者打分，两者之差就是 probe 读出的论文特有信号。")],
'S85': [
("This is your own summary table, with a small update box beside it.",
 "这是你自己做的汇总表，旁边加了一个小的更新框。"),
("The update gives the current H2 wording: not a general paper identity, with one small locked exception, the surname signal from layer 8.",
 "更新框给出现在 H2 的说法：不是一般意义上的论文身份，有一个小的锁定例外，就是从第 8 层起的姓氏信号。"),
("The table itself is unchanged.",
 "表格本身没有改动。")],
'S106': [
("This page asks whether a small part of the state carries the paper or the authors.",
 "这一页问：状态里的一小部分，是不是就承载了论文或作者？"),
("Swapping only a small subspace moves very little compared with swapping the whole state; for the author subspace about 0.03 against about 0.46.",
 "只替换一个小子空间，和替换整个状态相比搬动得很少；作者子空间约 0.03，整个状态约 0.46。"),
("So the information is spread out, not held in one small subspace.",
 "所以信息是分散的，不在一个小子空间里。")],
'S112': [
("This page collects four exploratory looks at recognised but unsaid papers.",
 "这一页汇集了关于“认得但说不出”的四个探索性观察。"),
("The first name token often loses to another initial or a common given name; writing needs far more citations than recognising; and about half of the made-up names are not in the data.",
 "名字的第一个 token 常常输给另一个首字母或常见的名；写出需要的引用远多于认出；编造的名字大约一半根本不在数据里。"),
("All four are descriptive clues, later followed up by locked tests.",
 "这四项都是描述性线索，后来都用锁定检验做了跟进。")],
'S61': [
("This page shows the re-runs by group: the recovery curves, and the numerator and denominator separately.",
 "这一页按组展示重跑结果：恢复曲线，以及分开看的分子和分母。"),
("All groups rise in the same layers; the unrecognised group's ratio looks higher only because its denominator is about half as large.",
 "各组都在同样的层上升；认不得的组比例看起来更高，只是因为它的分母只有大约一半。"),
("So the groups differ in size, not in timing.",
 "所以各组的差别在大小，不在时间。")],
}
