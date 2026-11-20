"""2026-11-19 c: drop inline process labels in talk docs, advisor page, process report (facts and status words kept);
move the English 18b paragraph of the Stage 13 script after 'Putting it together'. Run last (after ..._b_md.py)."""
import re
REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
FILES = ['advisor/index.html', 'process_report/index.html', 'process_report/draft_zh.md', 'talk_docs/experiment_walkthrough_zh.html',
         'talk_docs/experiment_walkthrough_methods_zh.html', 'talk_docs/stage13_script_zh_en.html', 'talk_docs/methods_handbook_guide_plain_zh.html']
SUB = [('（答辩后新增，分析计划在看结果前写定）', '（分析计划在看结果前写定）'),
       ('(post-defence, plan fixed before the results)', '(plan fixed before the results)'),
       ('答辩后的结果见下方更新框', '2026-11-05 以后的结果见下方更新框'),
       ('更新：答辩后的重做计划（批次 1 全部结果', '更新：补充 10–13 的结果（批次 1 全部结果'),
       ('答辩后已完成、以前写“没做 / 暂停”的项目：', '2026-11-05 以后完成、以前写“没做 / 暂停”的项目：'),
       ('X5 检索曲线与 X2 都已在答辩后完成', 'X5 检索曲线与 X2 都已于 2026-11-05 完成'),
       ('重做计划的新结果用绿色框标出', '补充 10 以后的新结果用绿色框标出'),
       ('（由答辩后的分组对比补上）', '（由分组对比（补充 7、8）补上）'),
       ('“列入重做计划，尚未运行”', '“列入补充 12 第 2-1 项，尚未运行”'),
       ('“CPU 部分已完成，GPU 部分在重做计划里”', '“CPU 部分已完成，GPU 部分列入补充 11、12”'),
       ('已列入重做计划（', '已列入（'), ('列入重做计划（', '列入（')]
for f in FILES:
    p = REP + f; t = open(p, encoding='utf-8').read()
    for a, b in SUB:
        t = t.replace(a, b)
    if f.endswith('stage13_script_zh_en.html'):
        i = t.index('<p>Addendum 18b (shelf map'); j = t.index('</p>', i) + 4
        para = t[i:j]; t = t[:i] + t[j:].lstrip('\n')
        k = t.index('<p>Putting it together:'); k2 = t.index('</p>', k) + 4
        t = t[:k2] + '\n' + para + t[k2:]
    open(p, 'w', encoding='utf-8').write(t)
    left = [re.sub(r'\s+', ' ', t[max(0, m.start() - 40):m.start() + 40]) for m in re.finditer(r'答辩后新增|重做计划|答辩后补算|CPU 补充|[Pp]ost-defen[cs]e|[Rr]edo programme|答辩后', t)]
    print(f, 'left:', left)
