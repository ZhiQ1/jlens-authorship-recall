"""Write addendum 20 (H2 fictitious titles) into the HTML/MD documents by topic (2026-11-20). Backups <file>.before_20261120_a20
(never overwritten; each run rebuilds from the backup, so it is idempotent). Each edit: exact unique anchor (asserted)."""
import shutil, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from a20_texts_20261120 import *

REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
done = []
src = lambda s: '<span class="src">（' + s + '）</span>'


def edit(path, ops):
    bk = path + '.before_20261120_a20'
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    t = open(bk, encoding='utf-8').read()
    for anchor, new, mode in ops:
        n = t.count(anchor)
        assert n == 1, (path, anchor[:60], n)
        t = t.replace(anchor, anchor + new if mode == 'after' else new + anchor if mode == 'before' else new)
    open(path, 'w', encoding='utf-8').write(t)
    done.append(path)


# combined report
edit(REP + 'stage1_11/stage1_11_report.html', [
    ('<b>X2 不支持。</b></td></tr>', '<b>X2 不支持。</b><br><b>补充 20（虚构标题，锁定）：</b>φ_T = 0.751 [0.723, 0.778]，R̄_T = +0.106 [0.094, 0.118] → '
     + VERDICT + '。</td></tr>', 'replace'),
    ('H2 部分支持但未确立', STATUS, 'replace'),
    ('<p>三者不互斥。实验的目标是看每一层主要是哪一种', '<p>' + A20 + src(SRC) + '</p>\n', 'before'),
    ('<li><b>R0 标签与提示方式（2026-11-14', '<li>' + LIM + src('391_groups/summary_a20/a20_report.md 第 5、6 节；raw/a20_INVALID_README.txt') + '</li>\n', 'before'),
])

# methods handbook
hb = REP + 'methods/methods_handbook.html'
edit(hb, [
    ('<h3 id="s13-x4">', HB_SEC + '\n', 'before'),
    ('X2 不支持 H2（<a href="#s13-x2">s13-x2</a>）。', ' ' + A20s + '（<a href="#s13-a20">s13-a20</a>）', 'after'),
    ('H2 部分支持但未确立', STATUS, 'replace'),
    ('<tr><td>Stage 13 补充 18b 柜子地图', GPU_ROW, 'before'),
])

# advisor page
edit(REP + 'advisor/index.html', [
    ('<span class="pill part">部分支持，未确立</span></td><td>支持：',
     '<span class="pill part">部分支持：存在真实论文成分，但大部分可由语义相似解释（补充 20，锁定）</span></td><td>' + A20s + '其余依据——支持：', 'replace'),
    ('<li>设计新的实验区分“认出论文”和“懂得标题意思”，比如用模型不可能见过的虚构论文作对照。</li>',
     '<li>用模型不可能见过的虚构论文作对照，区分“认出论文”和“懂得标题意思”：已完成（补充 20，结果见上表 H2 行）。</li>', 'replace'),
    ('<li>只用了一个模型（Qwen3-32B，bf16）。</li>', '\n    <li>' + LIM + '</li>', 'after'),
])

# process report (html + draft)
PR_ITEM = ('补充 20 虚构标题（11-19 → 11-20，' + LOCK + '）：用户核对随机 20 个标题后锁定；先做 CPU 全流程小测、1 个分片 GPU 试跑和一致性检查，再跑全部分片（H200，有效运行 0.53 GPU 小时）。'
           '结果：' + A20s)
PR_42 = ('补充 20 第一次运行的冻结脚本取了标题表的真标题列（title）而不是虚构标题列（cand），虚构提示与真提示相同，分析得到 φ = 1.000、R = 0（11-20 当天发现）。'
         '处理：输出保留并标为无效（raw/a20_*、summary_a20_INVALID_v1_fict_eq_true/），冻结脚本改读 cand 并在虚构标题与真标题相同时停止，重跑；无效运行 0.55 GPU 小时，共 1.08。')
edit(REP + 'process_report/index.html', [
    ('</ul>\n<h2 id="s4">', '<li>' + PR_ITEM + src('391_groups/summary_a20/a20_report.md；raw/a20v2_*') + '</li>', 'before'),
    ('H2 部分支持但未确立；H3', STATUS + '；H3', 'replace'),
    ('</ol>\n<h2 id="s6">5.', '<li class="issue"><span class="date">11-20</span> <b>补充 20 第一次运行把真标题当作虚构标题（已修正重跑）</b><br>' + PR_42
     + src('~/jlens_work/15_h2fict/h2_main_freeze.py；raw/a20_INVALID_README.txt') + '</li>', 'before'),
])
edit(REP + 'process_report/draft_zh.md', [
    ('- 假设：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；', '- 假设：H1 在 ":" 和名字位置成立；' + STATUS + '；', 'replace'),
    ('【a18b_item2.py mask_fn_for / win_of】\n', '32. 11-20｜补充 20 第一次运行把真标题当作虚构标题｜' + PR_42 + '【h2_main_freeze.py；raw/a20_INVALID_README.txt】\n', 'after'),
])

# walkthroughs
W = lambda h, s, sc: '\n<p><strong>' + h + '</strong>：' + s + src(sc) + '</p>'
wz = REP + 'talk_docs/experiment_walkthrough_zh.html'
edit(wz, [
    ('H2 部分支持但未确立，', VERDICT + '（补充 20 虚构标题，锁定的确认性检验）；此前的依据是', 'replace'),
    ('或者用模型不可能见过的虚构论文做对照，来区分‘认出论文’和‘懂得意思’。', '（用虚构论文区分‘认出论文’和‘懂得意思’的对照已经做了，见补充 20）。', 'replace'),
])
t = open(wz, encoding='utf-8').read()
k = t.find('“三个假设的结论是：'); k = t.rfind('<p', 0, k); k2 = t.find('</p>', k) + 4
t = t[:k2] + W('虚构标题（补充 20）', A20s, SRC) + t[k2:]
open(wz, 'w', encoding='utf-8').write(t)

wm = REP + 'talk_docs/experiment_walkthrough_methods_zh.html'
edit(wm, [
    ('H2 部分支持但未确立：', VERDICT + '（补充 20 虚构标题，锁定的确认性检验）；此前：', 'replace'),
    ('用虚构论文作对照，区分“认出论文”和“懂得意思”。', '虚构论文对照已完成（补充 20）。', 'replace'),
])
t = open(wm, encoding='utf-8').read()
k = t.find(VERDICT + '（补充 20 虚构标题'); k = t.rfind('<p', 0, k); k2 = t.find('</p>', k) + 4
t = t[:k2] + W('虚构标题（补充 20）', A20, SRC) + t[k2:]
open(wm, 'w', encoding='utf-8').write(t)

# Stage 13 script (zh + en)
s13 = REP + 'talk_docs/stage13_script_zh_en.html'
edit(s13, [
    ('H2 部分支持但未确立：', VERDICT + '（补充 20 虚构标题，锁定的确认性检验：意思相近但不存在的标题恢复差距的 75%，只有真标题才给的部分 +0.106 [0.094, 0.118]）。此前的依据：', 'replace'),
    ('H2 is partly supported:', 'H2 is partly supported: a real-paper component exists, but meaning similarity explains most of the signal (addendum 20, fictitious titles, locked confirmatory test: a non-existent title close in meaning recovers 75% of the gap; what only the real title gives is +0.106 [0.094, 0.118]). Earlier evidence:', 'replace'),
])
t = open(s13, encoding='utf-8').read()
for key, para in [('H2 is partly supported: a real-paper', '<p>' + A20_EN + src(SRC_EN) + '</p>'),
                  (VERDICT + '（补充 20 虚构标题，锁定', '<p>' + A20s + src(SRC) + '</p>')]:
    k = t.find(key); k2 = t.find('</p>', k) + 4
    t = t[:k2] + '\n' + para + t[k2:]
open(s13, 'w', encoding='utf-8').write(t)

# plain guide
edit(REP + 'talk_docs/methods_handbook_guide_plain_zh.html', [
    ('<tr>\n<td>X3 判断器 v1、v2</td>', '<tr>\n<td>补充 20 虚构标题</td>\n<td>完成，锁定的确认性检验：' + A20s + '</td>\n<td>“' + VERDICT
     + '：意思相近的假想标题就能带回四分之三，真论文只多给一小块”</td>\n</tr>\n', 'before'),
])
print('\n'.join(done))
