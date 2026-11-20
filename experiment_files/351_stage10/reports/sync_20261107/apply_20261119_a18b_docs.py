"""Write addendum 18b results into the HTML/MD documents by topic (2026-11-19). Backups <file>.before_20261119 (never overwritten).
Each edit: exact unique anchor (asserted), insert after/before or replace."""
import shutil, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from a18b_texts_20261119 import *

REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
done = []


def edit(path, ops):
    bk = path + '.before_20261119'
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    t = open(bk, encoding='utf-8').read()          # always rebuild from the backup (idempotent)
    for anchor, new, mode in ops:
        n = t.count(anchor)
        assert n == 1, (path, anchor[:60], n)
        if mode == 'after':
            t = t.replace(anchor, anchor + new)
        elif mode == 'before':
            t = t.replace(anchor, new + anchor)
        else:
            t = t.replace(anchor, new)
    open(path, 'w', encoding='utf-8').write(t)
    done.append(path)


P = lambda body, s: '\n<p>' + body + src(s) + '</p>'

# ------------------------------------------------------------------ combined report
ROUTE_BLOCK = ('\n<h4>这条路线的三段：注意力 L48 → MLP L52–56 → MLP L57–61（' + LOCK + ' 第 2、6、4 项）</h4>'
               + P(I2, S2) + P(I6, S6) + P(I4, S4) + '\n<p>' + ROUTE + '</p>')
edit(REP + 'stage1_11/stage1_11_report.html', [
    ('MLP 这一步究竟是在“查记忆”还是只在“变换格式”，这个实验分不开。</p>',
     'MLP 这一步究竟是在“查记忆”还是只在“变换格式”，这个实验分不开（补充 18b 第 6 项给出部分回答，见下）。</p>' + ROUTE_BLOCK, 'replace'),
    ('规则 381_stage13/config/prereg_addendum18.md 第 3 项）</span></p>', P(I3, S3), 'after'),
    ('起始层在主分析和敏感性分析之间不一致（L8 对 L24），不作为结论。</p>', P(I5, S5), 'after'),
    ('<p class="note">限定：M3 的身份指数从不高于 L4', P(I1, S1)[1:] + '\n', 'before'),
    ('标题信息在 L24–50 被读取，到 L57–61 才在名字位置被 lens 读出。', MAIN3 + src('（' + S4.strip('（）') + '；' + S6.strip('（）') + '）'), 'after'),
    ('<li><b>R0 标签与提示方式（2026-11-14', '<li>' + LIM + src(S1.split('；')[0] + '–6 项；keeper_state.json gpu_s；381_stage13/a18b_config/）') + '</li>', 'before'),
])

# ------------------------------------------------------------------ methods handbook
HB_I1 = ('\n<h3 id="s13-a18b-1">补充 18b 第 1 项　读出地图（位置组 × 层，同尺度）</h3>'
         '<h4>1 问题与作用</h4><p>X5 只汇总已有层。本项在同一组论文、同一尺度上，查名字位置之外的位置组是否更早带有论文特有的作者信息（“柜子先在该位置”）。</p>'
         '<h4>2 材料</h4><p>600 篇子样本（Stage 11 样本 1,186 篇中每个引用档 target / control 各 30 篇，seed 1817；24 个分片 × 25 篇）；真标题 + 5 个假标题。层：L8、16、24、32、36、L40–L52 每层、L56、L60（20 层）。位置组：标题全部 / 内容词 / 首 / 末 token、右引号（p9）、年份数字、“)?\\n”（p3）、“Authors”（p2）、“:”（p1）；名字位置（姓首 token、全部名字 token）。<span class="src">a18b_config/sample600.parquet · ~/jlens_work/13_stage13/a18b_item1.py 文件头</span></p>'
         '<h4>3 工具</h4><p>GPU：<code>a18b_item1.py work</code>（一次前向，直接在 GPU 上算受限名次，并存每组池化后的 fp16 残差）；CPU 分析 <code>a18b_item1.py analyze</code>（作业 11968239）。读出：logit lens 与 public J-lens，金标准只在 9,137 个名字 token id 中排名（bf16，名次 = 1 + 严格更大的个数，与 H3 同尺度相同）；名字 token ridge probe（E4b / 补充 11 A 做法，5 个存档团队折，训练折标准化，α ∈ {0.1, 1, 10}·tr(G)/d，经 final norm + 9,137 行 lm_head 解码；只用这 600 篇训练）；属性 probe（年份、log 引用数、领域）。</p>'
         '<h4>4 公式与判据</h4><p>每篇论文每条件平均 log10(1/名次)；spec = 真 − 5 个假标题平均；引用档内 target − control；团队整群 bootstrap 2,000 次。锁定规则：某位置组在 ≤ L48 的某层 target − control 区间 &gt; 0，而同层名字位置（姓首 token）区间含 0 → “柜子先在该位置”；否则“没有更早的位置”。主金标准为姓首 token（实现时、看 GPU 输出前定），名字第一个 token 并列。</p>'
         '<h4>5 结果</h4><p>' + I1 + src(S1) + '</p>'
         '<h4>6 局限</h4><p>未做多重比较校正（54 个组合 × 每个最多 14 个 ≤ L48 的层）；probe 只用 600 篇训练；单一模型；探索性解读。</p>')
HB_ROUTE = ('\n<h3 id="s12-a18b-route">路线三段的检验（补充 18b 第 2、6、4 项）</h3>'
            '<p><b>共同设定</b>：600 篇子样本（同第 1 项）；S = 真 − 5 个假标题平均（最终输出，论文平均 log10(1/名次)）；loss = S(none) − S(config)；恢复比例 = mean(替换 − none) / mean(真 − none)，五标题平均；团队整群 bootstrap 2,000 次，配对。代码 <code>~/jlens_work/13_stage13/a18b_item2.py</code>、<code>a18b_item4.py</code>、<code>a18b_item6.py</code>；队列由 <code>a18b_keeper.py</code> 按成本顺序排（第 4 → 1 → 6 → 5 → 2 → 3 项）。</p>'
            '<h4>第 2 项　分窗口注意力屏蔽</h4><p>做法：L40–L63 每 4 层一个窗口（6 个不重叠窗口），窗口内只断开一条边（所有头，注意力掩码设 bf16 最小值）：名字←标题、名字←尾部、尾部←标题、“:”←标题、名字←“:”；31 个配置（含 none）× 6 个标题条件。锁定规则：某边在窗口内的损失区间 &gt; 0 且大于同窗口其他边（实现为：点估计最大、区间 &gt; 0，且与每条其他边的配对差区间 &gt; 0）。敏感性：步长 2 的 11 个窗口（成本允许时加跑）。<b>实现问题</b>：<code>mask_fn_for</code> 中的 <code>win_of(l)</code> 只返回第一个包含第 l 层的窗口，对不重叠的主分析没有影响，但在步长 2 的重叠窗口中，除 L40–43 外每个窗口实际只屏蔽了后两层；第一次步长 2 运行因此作废，已用 <code>a18b_item2_fix.py</code>（逐配置显式传入窗口）修正重跑。</p><p>' + I2 + src(S2) + '</p>'
            '<h4>第 6 项　MLP 查记忆（L52–L56）</h4><p>做法：(a) 名字预测位置（“:” 和每个名字输入）上 L52–L56 MLP 神经元激活（down_proj 的输入，每层 25,600 个）在真 / 假标题下的差，同一篇论文两个假标题之间与不同论文之间的 top-50 重叠（Jaccard）；(b) 把真标题运行的 MLP 输出（整个对齐尾部，同 P2）换进 false_k 运行，只换作者名字子空间 U（9,137 个名字 token 的 lm_head 行 × final norm 权重、中心化后的前 512 个右奇异向量，占方差 0.339）里的部分、只换正交部分、随机 512 维子空间（seed 6）、整个输出：值 = out_F + P(out_T − out_F)；(c) 注意力输出同样做。没有锁定数值判据，全部描述性。</p><p>' + I6 + src(S6) + '</p>'
            '<h4>第 4 项　L57–L61 注意力 / MLP 均值消融</h4><p>做法：在尾部位置（p1–p9）和全部名字输入，把 L57–L61 中一层的注意力或 MLP 输出换成参考均值；参考均值来自 Stage 11 样本中不在子样本里的 586 篇、5 个假标题条件、同一位置，事先单独计算（单元 refmean）。10 个配置 + none × 6 个标题条件。锁定判据：MLP 消融损失 &gt; 注意力消融（配对区间不含 0）→ “后段由 MLP 写出”。</p><p>' + I4 + src(S4) + '</p>'
            '<p>' + ROUTE + '</p>')
HB_I3 = '\n<h4>8 逐格替换（补充 18b 第 3 项）</h4><p>做法：Stage 12 P1 的单位置替换（<code>s12.do_patch_pos</code>），6 个位置组（“:”、名字位置、年份十位 p5、右引号 p9、其余尾部、整个尾部）× 15 层（L40–L52 每层、L56、L60）= 90 格，true → false_k 5 个假标题；按已存 P1 的批量形状分块（48 / 36 / 7）。600 篇子样本；第 5(b) 部分已由补充 18 第 3 项完成，不重跑。硬检查：(a) 整个尾部 L48 / L52 与已存 P1 行逐行名次相同；(b) 已存 586 篇 + 新 600 篇合并复现 0.821 / 0.995，|差| ≤ 1e-6。代码 <code>a18b_item3.py</code>。</p><p>' + I3 + src(S3) + '</p>'
HB_I5 = '\n<h4>补充 18b 第 5 项：标题词的重要性（L8–L24 与最终输出）</h4><p>做法：真标题词分四类（内容词：&gt; 2 个字母、不在 sklearn 停用词表；罕见词：9,108 篇标题中文档频率 ≤ 5 的内容词；功能词：停用词；首末词），每类整体替换为 WordNet 3.0 同义词（功能词用固定近义表；没有同义词的词不变，覆盖率另报）或同 token 长度的随机词表 token（每篇每类固定种子），共 8 个变体；读出最终输出的名字 token 名次（loss = 真 − 变体）和标题最后一个 token 上的 E4b 式 probe（L8、12、16、20、24）。关键对比：同义词损失 − 随机损失。代码 <code>a18b_item5.py</code>（替换表 a18b_config/item5_variants_v3.parquet）。</p><p>' + I5 + src(S5) + '</p>'
HB_GPU = ('<tr><td>Stage 13 补充 18b 柜子地图（第 1–6 项 + 第 2 项步长 2，600 篇子样本）</td><td>1×A100-80GB（第 3 项部分分片在 H200）</td><td>13.2 h（第 1 项 0.82、第 2 项 1.56、第 2 项步长 2 修正重跑 2.0、第一次步长 2 运行 3.25（无效）、第 3 项 1.51、第 4 项 1.28、第 5 项 0.88、第 6 项 1.89；每项 ≤ 5 h）</td><td>分析 11968239、11970080、11970331、11971121、11988292、11989143、11990717；GPU 作业由 a18b_keeper 提交</td><td>11-17 → 11-19</td><td><span class="src">381_stage13/a18b_config/keeper_state.json（gpu_s）· PROGRESS.md 2026-11-17 / 18 / 19 条</span></td></tr>\n')
hb = REP + 'methods/methods_handbook.html'
t = open(hb + '.before_20261119' if os.path.exists(hb + '.before_20261119') else hb, encoding='utf-8').read()
i = t.find('<td>10:28（x4tok 检查失败后按规则停止）</td>'); j = t.find('</tr>', i) + len('</tr>')
gpu_anchor = t[t.rfind('<tr>', 0, i):j]
edit(hb, [
    ('<h3 id="s13-x6">', HB_I1 + '\n', 'before'),
    ('规则 381_stage13/config/prereg_addendum18.md 第 3 项）</span></p>', HB_I3, 'after'),
    ('<h2>N1 多选选项先验（prior_mc）', HB_ROUTE + '\n', 'before'),
    ('<h3 id="s13-x4">', HB_I5 + '\n', 'before'),
    (gpu_anchor, '\n' + HB_GPU, 'after'),
])

# ------------------------------------------------------------------ advisor page
A = lambda s: '<p>' + s + '</p>'
edit(REP + 'advisor/index.html', [
    ('MLP 在 L52–56 接手（<span class="num">0.18、0.22</span>）。</p></li>',
     'MLP 在 L52–56 接手（<span class="num">0.18、0.22</span>）。</p>\n      ' + A(ROUTEs + src(S2.split('；')[0] + '、第 4、6 项；381_stage13/summary_a18b_item{2,4,6}/）')) + '\n      ' + A(I3s + src(S3)) + '</li>', 'replace'),
    ('两者都报告，并记为与预注册的出入。</p></li>', '两者都报告，并记为与预注册的出入。</p>\n      ' + A(I5s + src(S5)) + '</li>', 'replace'),
    ('图中标签为英文（集群上没有中文字体）。</figcaption>\n  </figure>', '\n  ' + A(I1s + src(S1)), 'after'),
    ('只替换子空间的因果检验（X2）没有做', '只替换子空间的因果检验（X2）没有做；补充 18b 第 1 项读出地图没有清楚的更早“柜子”（探索性）；第 6 项 L52–56 MLP 的论文信息大部分不在作者名字方向上（描述性，与 H3 一致，不作检验）', 'replace'),
    ('X4 顺序与预测相反；', 'X4 顺序与预测相反；补充 18b 第 5 项（描述性）：内容词的意思比字面重要，与 X3 一致，仍分不开论文身份；', 'replace'),
    ('<li>只用了一个模型（Qwen3-32B，bf16）。</li>', '\n    <li>' + LIM + '</li>', 'after'),
])

# ------------------------------------------------------------------ process report (html + draft)
PR_ITEM = ('补充 18b 柜子地图（11-17 → 11-19，' + LOCK + '）：600 篇子样本；6 项 GPU 由 a18b_keeper.py 按成本顺序排队（第 4 → 1 → 6 → 5 → 2 → 3 项，第 2 项步长 2 敏感性在成本允许时加跑），' + GPU + '。过程问题：d1028 上作业结束 epilog 多次杀掉我们的作业（0:9，低内存，非 OOM；第 6 项被 keeper 停止后手工补交，第 3 项部分分片改到 H200）；第 2 项步长 2 的窗口分配错误事后发现（见 4.2）。结果：' + ROUTEs + I3s + I1s + I5s)
PR_42 = ('补充 18b 第 2 项步长 2 敏感性分析的窗口分配错误（11-19 写文档时发现）：重叠窗口下 <code>win_of(l)</code> 只把第 l 层分给第一个包含它的窗口，除 L40–43 外每个窗口实际只屏蔽后两层；主分析（不重叠窗口）不受影响。处理：不把步长 2 结果当作稳健性检验，结论暂时写作“锁定规则下成立，稳健性未确立”；<!--A18B2-STEP2-START-->修正窗口分配后已重跑（用户 2026-11-19 决定，约 2.0 GPU 小时）：锁定规则在 11 个重叠窗口中的 7 个满足（L42–L57，同一条边），对窗口位置稳健；第一次步长 2 运行作废。<!--A18B2-STEP2-END-->')
PR_5 = '路线后段（补充 18b）：L52–56 MLP 带论文信息但大部分不在作者名字方向上（描述性），L57–61 由 MLP 写出（锁定判据成立，+0.040 [0.036, 0.045]）。'
edit(REP + 'process_report/index.html', [
    ('见第 0 节〕<span class="src">S§0</span></li></ul>\n<h2 id="s4">', '见第 0 节〕<span class="src">S§0</span></li><li>' + PR_ITEM + src('381_stage13/summary_a18b_item{1..6}/、summary_a18b_item2_step2_fix/（第一次步长 2 运行 summary_a18b_item2_step2/ 作废）；keeper_state.json') + '</li></ul>\n<h2 id="s4">', 'replace'),
    ('注意力 L48、MLP L52–56。', PR_5, 'after'),
    ('</ol>\n<h2 id="s6">5.', '<li class="issue"><span class="date">11-19</span> <b>补充 18b 第 2 项步长 2 的窗口分配错误（已修正重跑）</b><br>' + PR_42 + src('~/jlens_work/13_stage13/a18b_item2.py mask_fn_for / win_of；381_stage13/summary_a18b_item2_step2/item2_report.md') + '</li></ol>\n<h2 id="s6">5.', 'replace'),
])
edit(REP + 'process_report/draft_zh.md', [
    ('见第 0 节〕【S§0】\n', '见第 0 节〕【S§0】\n- ' + PR_ITEM.replace('<code>', '`').replace('</code>', '`').replace('&gt;', '>') + '【381_stage13/summary_a18b_item{1..6}/、summary_a18b_item2_step2/；keeper_state.json】\n', 'replace'),
    ('注意力 L48、MLP L52–56。', PR_5, 'after'),
    ('｜措辞【P 2026-11-03】\n', '\n31. 11-19｜补充 18b 第 2 项步长 2 的窗口分配错误｜' + PR_42.replace('<code>', '`').replace('</code>', '`') + '【a18b_item2.py mask_fn_for / win_of】\n', 'after'),
])

# ------------------------------------------------------------------ walkthroughs
W = lambda h, s, sc: '\n<p><strong>' + h + '</strong>：' + s + src(sc) + '</p>'
wz = REP + 'talk_docs/experiment_walkthrough_zh.html'
edit(wz, [
    ('MLP 那一步是不是“查记忆”，这个实验分不出来。</p>', W('路线三段（补充 18b，锁定后补测）', I2s + I6s + I4s, S4), 'after'),
    ('阻断的结论也不是“搞乱模型”造成的。</p>', W('逐格替换（补充 18b 第 3 项）', I3s, S3), 'after'),
    ('一张图把“读得早，说得晚”的时间线完整串起来。</p>', W('读出地图（补充 18b 第 1 项）', I1s, S1), 'after'),
    ('预注册的结果和事后检验都如实报告。</p>', W('标题里哪些词重要（补充 18b 第 5 项）', I5s, S5), 'after'),
])
wm = REP + 'talk_docs/experiment_walkthrough_methods_zh.html'
edit(wm, [
    ('单层替换是下限；MLP 是否“查记忆”分不出。</p>', W('路线三段（补充 18b 第 2、6、4 项）', I2 + ' ' + I6 + ' ' + I4, S4), 'after'),
    ('<h3>实验 10：哪个位置（Stage 12 P1）</h3>', W('逐格替换（补充 18b 第 3 项）', I3, S3)[1:] + '\n', 'before'),
    ('<p><strong>说明什么</strong>：“读得早，说得晚”的完整时间线。</p>', W('读出地图（补充 18b 第 1 项）', I1, S1), 'after'),
    ('<h3>实验 19：Patchscope（X4）</h3>', W('标题里哪些词重要（补充 18b 第 5 项）', I5, S5)[1:] + '\n', 'before'),
])

# ------------------------------------------------------------------ Stage 13 script
ZH13 = ('后来补的“柜子地图”（补充 18b，2026-11-17 锁定，600 篇子样本）把这条路线的后半段补全了。L57 到 L61 这一段，是 MLP 在写，注意力几乎不参与：每一层把 MLP 换成平均值，损失都比换注意力大，平均多 +0.040 [0.036, 0.045]，这是锁定判据，成立，定为定论。往前一段，L52 到 L56 的 MLP 确实带着这篇论文的信息，但主要不在“作者名字”的方向上：对齐名字方向的那一小块只恢复 0.022–0.042，大部分在正交的部分。再往前，单独断开“名字←标题”这条注意力边，在 L44 到 L55 损失最大，按锁定规则成立，但最多只占信号的 3.4%，<!--A18B2-VERDICT-START-->换窗口位置也成立（修正后的步长 2 敏感性分析，11 个重叠窗口中 7 个，同一条边）<!--A18B2-VERDICT-END-->。到达名字位置的信息主要落在名字位置本身。读出地图在名字位置之外只看到零星的早期痕迹，没有清楚的更早“柜子”，这一项是探索性的。标题里，内容词换成随机词损失 +0.374，换成同义词只损失 +0.087，说明靠的主要是意思，和 X3 一致。')
edit(REP + 'talk_docs/stage13_script_zh_en.html', [
    ('<p>Putting it together:', '<p>' + ZH13 + src(S4.split('；')[0] + '–6 项；381_stage13/summary_a18b_item{1..6}/') + '</p>\n', 'before'),
    ('<p>Putting it together:', '<p>' + EN + src('381_stage13/summary_a18b_item{1..6}/, summary_a18b_item2_step2/') + '</p>\n', 'before'),
])
# fix order: zh then en, both before the English "Putting it together" -> move zh before zh paragraph instead
t = open(REP + 'talk_docs/stage13_script_zh_en.html', encoding='utf-8').read()
zp = '<p>' + ZH13 + src(S4.split('；')[0] + '–6 项；381_stage13/summary_a18b_item{1..6}/') + '</p>\n'
t = t.replace(zp, '', 1)
k = t.find('<p>连起来就是'); k2 = t.find('</p>', k) + 4
t = t[:k2] + '\n' + zp.rstrip('\n') + t[k2:]
open(REP + 'talk_docs/stage13_script_zh_en.html', 'w', encoding='utf-8').write(t)

# ------------------------------------------------------------------ plain guide
pg = REP + 'talk_docs/methods_handbook_guide_plain_zh.html'
edit(pg, [
    ('<li><strong>X6</strong>：E1 换成另外 4 个假标题重做。</li>',
     '\n<li><strong>补充 18b 第 3 项</strong>：逐格替换，一次只换一组位置、一层。' + I3s + '</li>\n<li><strong>补充 18b 第 6 项</strong>：只换 MLP 输出里和作者名字方向对齐的那一小块（512 维），和换剩下的部分比。' + I6s + '</li>', 'after'),
    ('<p><strong>版本</strong>：E2 挡全部；E2n 只挡 “:” 和名字位置；X7 在假标题那遍也做同样阻断，扣掉“被挡本身造成的破坏”。</p>',
     '\n<p><strong>补充 18b 第 2 项</strong>：只在一个 4 层窗口里断开一条边。' + I2s + '</p>\n<p><strong>补充 18b 第 4 项（均值消融）</strong>：不是挡注意力，而是把某层的注意力或 MLP 输出换成别的论文的平均值。' + I4s + '</p>', 'after'),
    ('<li><strong>Qwen 判断器</strong>：', '<li><strong>补充 18b 第 5 项</strong>：' + I5s + '</li>\n', 'before'),
    ('<tr>\n<td>X5 层序量化</td>', '<tr>\n<td>补充 18b 第 1 项读出地图</td>\n<td>完成，探索性：' + I1s + '</td>\n<td>“有零星的早期痕迹，但没有清楚的更早柜子；没做多重比较校正，不作结论”</td>\n</tr>\n<tr>\n<td>补充 18b 第 2 项步长 2 敏感性</td>\n<td>第一次运行重叠窗口的每一层只分给第一个窗口（除 L40–43 外实际只挡后两层），作废；修正后重跑：11 个窗口中 7 个满足（L42–L57，同一条边）</td>\n<td>“主分析按锁定规则成立，<!--A18B2-VERDICT-START-->对窗口位置稳健<!--A18B2-VERDICT-END-->，效应小（≤ S 的 3.5%）”</td>\n</tr>\n', 'before'),
])
print('\n'.join(done))
