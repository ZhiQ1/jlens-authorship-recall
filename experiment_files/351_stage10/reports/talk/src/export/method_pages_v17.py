"""2026-11-05 deck v17: 13 method pages ("methods in pictures"), each placed right before the results of its own experiment.
Shared by edit_deck_v17.py (HTML + slides.json + notes_zh.json) and patch_editable_v17.py (native-shape pptx).
INSERT maps a v16 slide number (1-based) -> method page keys inserted right before it."""
import sys
sys.path.insert(0, '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/method_figs')
import build_method_figs as B
from method_lib import walk, Text

INSERT = {5: ['legend', 'groups'],          # before Stage 1 "Cohort and behavioural labels" (first group-based results)
          14: ['replication'],              # before Stage 8D "On 200 new papers the title effect replicates"
          16: ['scoring', 'stats'],         # before the first Stage 10 results (title-specific signal by layer, target vs control)
          18: ['probe'],                    # before "Is the probe at the title token reading real paper knowledge" (E4b)
          20: ['compare'],                  # before "Is the target advantage just the R1 papers?" (group-based contrasts)
          27: ['readout'],                  # before "All readouts get better with depth" (layer-by-layer lens readouts)
          37: ['patch', 'knockout'],        # before Stage 11 interventions (patching + knockout curves)
          51: ['question', 'paraphrase', 'patchscope']}   # before the Stage 12-13 summary slides (M3/X1, X3, X4)

TAGS = {k: t for k, t, f in B.ORDER}
ITEMS = {k: items for k, t, items in B.slides()}


def new_order(n_old=54):
    """list of ('old', i) / ('new', key) in v17 order"""
    out = []
    for i in range(1, n_old + 1):
        out += [('new', k) for k in INSERT.get(i, [])]
        out.append(('old', i))
    return out


def slide_text(key):
    return ' '.join(t.s for t in walk(ITEMS[key]) if isinstance(t, Text))


NOTE_COMPARE_REAL = '组间比较是答辩后新增的分析，计划预先写定（补充 7、8）。P1 比较 A 和 B（都是 R0，只差识别），输出层标题特异信号 +0.200 [0.188, 0.213]；P2 比较 C 和 A，只看模型没写出的作者：合作者 +0.061 [0.034, 0.090]，第一作者 +0.031 [−0.006, 0.069]，不显著。剂量曲线：R0 论文按多选答对的顺序数 0 到 4，信号从 0.17 升到 0.46。所有对比都在引用档内加权，并按团队重抽样。'

NOTES = {
    'legend': '从这一页起，每个方法页都放在它所属实验的结果之前，背景是很浅的粉色网格。图例：提示词画成一排 token 方块，橙色是真标题、灰色是假标题、黄色是名字；层自下而上，L0 在底部、L63 在顶部；一个圆点代表某一层某个位置的隐藏状态。蓝色箭头表示把状态复制或注入到另一次运行，红色叉表示阻断注意力，放大镜表示读出名次，漏斗表示训练探针；带圈数字是步骤顺序。',
    'groups': '9,108 篇论文先按开放回答分成 R0（一个真作者都没写对）8,298 篇、R1 596 篇、R2（基本写出了作者）214 篇，再按四种选项顺序的多选识别分成 strong、uncertain、fail。R0 里 A = 4,110、U0 = 2,002、B = 2,186；R1 里 C = 511、51、D = 34；R2 为 204、9、1。target = A + C = 4,621，control = B + D = 2,220。Stage 10 和 M2、M3 用全部 9,108 篇，Stage 11–13 的干预和 X 系列用 593 + 593 = 1,186 篇（X 系列配对后 1,178 对），Stage 1–9 的 Pilot50 和 Stage 8 取自 A 和 B；示例论文 Coifman 等（2007）属于 C 格。',
    'scoring': '以 Coifman、Bonanno、Rafaeli（2007）为例：同一组名字 token 接在 7 个提示后面——真标题、5 个匹配的假标题和删去标题。每个名字 token 取它在全词表中的名次，例如第一作者 7 个 token 在真标题下是 83、2、25、1、61、1、1，再取 log10(1/名次) 并对 16 个 token 求平均：真标题 −0.7190，5 个假标题平均 −1.1126，删去标题 −0.8808。标题特异信号 spec = −0.7190 − (−1.1126) = +0.3935；total = 真 − 删 = +0.1618，topic = 假 − 删 = −0.2318。',
    'stats': '组间比较都在引用档内做：13 个引用档里只用 target 和 control 各至少 30 篇的档（主分析 10 档，0-2 到 513-1024），每档内算 target − control，再按 w_b ∝ n_t·n_c/(n_t+n_c) 加权合并。示例论文在 65-128 档，该档 target 441 篇、control 165 篇。Stage 13 起置信区间按作者团队重抽样：共享任一作者全名的论文并成一个团队，9,108 篇共 7,247 个团队，交叉验证时一个团队只进一个 fold。',
    'replication': 'Stage 8 是独立重复：分析计划在 10 月 18 日 14:29 冻结（analysis_plan.json），当天 21:14 的协议把 L56 定为主层，仍在打分之前。然后取 200 篇新论文（100 对 A/B），10 月 18 日 21:47 开始打分、10 月 20 日结束，再按计划检查。RQ1：L56 处真标题相对 20 个假标题的胜率高 +5.18 个百分点 [2.93, 7.48]；计划里冻结的主终点（7 层平均）是 +2.33 [1.50, 3.19]。',
    'probe': '探针直接从状态读属性：取标题最后一个 token（这里是 “loss”）的残差，例如 L40，用 5 折岭回归（按作者团队分折）预测第一作者的首个 token 或年份。标题特异分数 spec = 真标题的探针分 − 假标题的探针分，L40 为 +0.061 [0.047, 0.076]。年份的 R² 从 L16 的 0.38 升到 L52 的 0.56（M2）。',
    'compare': (NOTE_COMPARE_REAL if B.M.COMPARE_REAL_NUMBERS else '组间比较的方法：在 9 个格子里，P1 比较 A 和 B（都是 R0，只差识别），P2 比较 C 和 A，且只看模型没写出的作者，再按作者位置分为合作者和第一作者；另外看 R0 论文的信号随多选答对的顺序数（0 到 4）怎样变化，即剂量曲线。每个对比都在引用档内求差、按 w_b 加权合并，并按作者团队重抽样。这一页只示意方法，Δ₁、Δ₂ 和曲线都不是结果；这是答辩后新增的分析，计划预先写定（补充 7、8），结果先交给用户确认。'),
    'readout': '逐层读出：在名字位置取每一层的隐藏状态，用 logit lens 映射到全词表，看真名字 token 的名次，再算 nlr = log10(1/名次)。示例论文第一作者姓的首个 token “Co”：L24 名次 37,675，L56 120,750，L61 9,811，L62 120，输出层 61。第一作者 7 个 token 的平均 nlr 到 L58 都在 −4 左右，L62 升到 −1.11、输出层 −0.77；假标题 false_0 在输出层是 −1.19，真假之差只在最后几层出现。',
    'patch': '替换（patching）：同一组名字分别接在真标题和假标题后面跑两次；在第 l 层，把真标题运行中标题之后的 token（“(2007)?”、“Authors”、冒号）和名字位置的状态复制进假标题运行，再给名字打分。恢复比例 R(l) = (patched − false) ÷ (true − false)。1,186 篇、5 个假标题平均：L24 0.080、L40 0.302、L48 0.821、L52 0.995，即到 L52 标题信息已全部进入标题之后的位置。',
    'knockout': '阻断（knockout）：从第 l 层起，让标题之后的每个位置都不能注意标题 token，记下名字分数的损失 T；在假标题运行上做同样的阻断得到 F；S = T − F，用真 − 假差距的比例表示。X7（1,186 篇）：从 L0 阻断 S = 1.00，L24 0.87，L40 0.29，L48 0.14，L52 0.029（target 0.018，control 0.051），所以 L52 之后标题已基本不再被读取。',
    'question': '换问题：同一标题分别放进作者、年份、领域三个问题里（M3），比较标题最后位置的状态；它们不比 L4 时更接近，也就是没有超出标题文字本身的“论文身份”状态。X1 把本篇在任一问题下的标题状态复制进另一篇论文标题的作者提示，再给本篇第一作者打分：R(l) = (patched − other) ÷ (own − other)，L24 约 0.99，L40 约 0.92，L48 约 0.42，三种来源几乎一样（测试集 582 篇）。',
    'paraphrase': '改写标题（X3）：示例论文原标题 “Affect dynamics, bereavement and resilience to loss”，改写为 “Affect fluctuations, grief and adaptability in the face of loss”，词汇邻居 D 是另一篇论文 “Affect and Resistance to Temptation.”。比较标题最后位置状态的余弦：G′ = cos(原, 改写) − cos(原, D)，L8 为 +0.32，L36 峰值 +0.46。词重叠 jaccard2 的中位数是改写 0.61、D 0.15（本例 0.22 和 0.14）；第一作者分数改写 − D 为 +0.239。',
    'patchscope': 'Patchscope（X4）：取作者问题里标题最后一个 token 在第 l 层的状态，注入到 “Paper: X / The first author of the paper is” 里 X 的位置（同一层），看模型接下去说出的答案；另有年份和领域两个目标提示。D = 用本篇状态时的分数 − 用配对论文状态时的分数。第一作者从 L8 起可以解码（+0.046），年份从 L40 起（+0.013）。',
}
assert set(NOTES) == set(ITEMS), set(ITEMS) ^ set(NOTES)
