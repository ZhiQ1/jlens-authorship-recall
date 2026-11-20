"""2026-11-19 b (user decisions): (1) fabricated-names wording; (3) dissolve process chapters in report and handbook by topic.
Runs on the current files (after apply_20261119_a18b_docs.py / _md.py); backups *.before_20261119b were taken before this round."""
import re, os

REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'


def R(t, a, b, n=1):
    assert t.count(a) == n, (a[:70], t.count(a))
    return t.replace(a, b)


def cut_section(t, sid):
    i = t.index('<section id="%s">' % sid); j = t.index('</section>', i) + len('</section>')
    return t[:i] + t[j:], t[i:j]


def sec_end(t, sid):
    i = t.index('<section id="%s">' % sid); return t.index('</section>', i)


def insert_at(t, pos, s):
    return t[:pos] + s + t[pos:]


def cut_li(t, lid):
    i = t.index('<li id="%s">' % lid); d = 0
    for m in re.finditer(r'<li[ >]|</li>', t[i:]):
        d += 1 if m.group(0) != '</li>' else -1
        if d == 0:
            j = i + m.end(); return t[:i] + t[j:], t[i:j]
    raise ValueError(lid)


def split_h(block, tag):
    """split block at <tag ...> boundaries -> (head, [pieces])"""
    idx = [m.start() for m in re.finditer('<%s[ >]' % tag, block)]
    return block[:idx[0]], [block[a:b] for a, b in zip(idx, idx[1:] + [len(block)])]


# ================================================================== (1) fabricated names wording
ZH = '编造的名字约一半不在数据中，与打乱基线相同（50.4% vs 50.5%）；是合作者的只有 4.0%（随机 1.3%）'
EN = 'about half are not in the data, the same as the shuffled baseline (50.4% vs 50.5%); co-authors are only 4.0% (chance 1.3%)'

f = REP + 'stage1_11/stage1_11_report.html'; t = open(f, encoding='utf-8').read()
t = R(t, '编造的名字大多来自数据中不存在的人（50.4% [49.0, 51.7] 不在数据中）；合作者比例 4.0% 虽高于同领域打乱基线 1.3%，但改用全名键或罕见名键后',
      ZH + '，而且改用全名键或罕见名键后')

# ================================================================== (3) report: dissolve part 5
t, groups = cut_section(t, 'pd-groups'); t, say = cut_section(t, 'pd-sayable')
t, a16d = cut_section(t, 'pd-a16d'); t, a16b = cut_section(t, 'pd-a16b')
t, clean = cut_section(t, 'pd-cleandonor'); t, h3s = cut_section(t, 'pd-h3samescale')
t, cpu = cut_section(t, 'pd-cpu'); t, run = cut_section(t, 'pd-running')
# pd-cpu: head (h2 + note) + 5 h3 pieces
head, pcs = split_h(cpu[:-len('</section>')], 'h3')
note = re.search(r'<p class="note">.*?</p>', head, re.S).group(0)
note = note.replace('<p class="note">', '<p class="note">（CPU，已有数据）', 1)
ids = ['pd-cpu', 'pd-cpu-u46', 'pd-cpu-v21', 'pd-cpu-v42', 'pd-cpu-v29']
pcs = [p.replace('<h3>', '<h3 id="%s">' % k, 1) for p, k in zip(pcs, ids)]
v56, u46, v21, v42, v29 = pcs
v56 = v56.replace('</h3>', '</h3>\n' + note, 1)
for p in (u46, v21, v42, v29):
    pass
# pd-running: pull the three result items out to their topic sections
run, xall = cut_li(run, 'pd-b1-xall'); run, p12f = cut_li(run, 'pd-b1-p12f'); run, e4b5 = cut_li(run, 'pd-b1-e4b5')
run = R(run, '<b>批次 1（补充 10）：</b>第 1–4 项都已完成。\n<ul></ul>',
        '<b>批次 1（补充 10）：</b>第 1–4 项都已完成（第 1 项见 <a href="#pd-b1-xall">M3 / X1 / X4 节</a>，第 3 项见 <a href="#pd-b1-p12f">Stage 12 节</a>，第 4 项见 <a href="#pd-b1-e4b5">补充 9 节</a>）。') \
    if '<b>批次 1（补充 10）：</b>第 1–4 项都已完成。\n<ul></ul>' in run else R(run, '<b>批次 1（补充 10）：</b>第 1–4 项都已完成。',
        '<b>批次 1（补充 10）：</b>第 1–4 项都已完成（第 1 项见 <a href="#pd-b1-xall">M3 / X1 / X4 节</a>，第 3 项见 <a href="#pd-b1-p12f">Stage 12 节</a>，第 4 项见 <a href="#pd-b1-e4b5">补充 9 节</a>）。')
run = re.sub(r'<h2><span class="st">重做计划</span> 补充 10–13：完成的、正在运行的和不做的（2026-11-06）</h2>',
             '<h2><span class="st">预注册</span> 补充 10–14 各项的状态：完成、停止、不做与偏离（规则 2026-11-05 / 06 起写定）</h2>', run)
assert '预注册</span> 补充 10–14 各项的状态' in run
run = R(run, '重做计划的规则都在看结果之前写定并锁定', '补充 10–14 的规则都在看结果之前写定并锁定')
W = lambda li: '\n<ul class="moved">' + li + '</ul>\n'
# placements (insert in an order that does not invalidate later lookups: compute positions fresh each time)
t = insert_at(t, sec_end(t, 's12-results'), v21 + W(p12f))
t = insert_at(t, sec_end(t, 'm3x1x4-results'), u46 + W(xall))
t = insert_at(t, sec_end(t, 'alltok-results'), W(e4b5))
i = sec_end(t, 'alltok-results') + len('</section>'); t = insert_at(t, i, '\n' + clean + '\n' + h3s)
t = insert_at(t, sec_end(t, 'x5-results'), v56)
t = insert_at(t, sec_end(t, 'p2-5'), v42)
t = insert_at(t, sec_end(t, 'p4-plan'), v29)
i = sec_end(t, 'p4-plan') + len('</section>'); t = insert_at(t, i, '\n' + run)
i = t.index('<section id="p3-bridge">'); t = insert_at(t, i, groups + '\n' + say + '\n' + a16d + '\n' + a16b + '\n')
# part bars
t = re.sub(r'<div class="partbar" id="p5"><span class="tagp">第五部分</span><h2>答辩后新增（2026-11-05）</h2><p>.*?</p></div>',
           '<div class="partbar" id="p5"><span class="tagp">第五部分</span><h2>全报告的局限</h2><p>不能补做的局限；各项结果自己的前提和局限写在各节。</p></div>', t, count=1, flags=re.S)
assert '<h2>全报告的局限</h2>' in t
t = R(t, '<h2>跨阶段：R0/R1 分层分析与两阶段对照</h2><p>Stage 1–9 只比 A vs B（都是 R0），Stage 10–11 比 target vs control（R0 + R1 合并）。这一部分把两者放到同一口径下。</p>',
      '<h2>跨阶段：R0/R1 分层、分组对比与“认得出却说不出”</h2><p>Stage 1–9 只比 A vs B（都是 R0），Stage 10–11 比 target vs control（R0 + R1 合并）。这一部分把两者放到同一口径下，并收录 A/B/C/D 分组对比（补充 7、8，计划在看结果前写定）、瓶颈分析（探索性 / 补充 19 事后锁定）和输出格式 / 名字链条（补充 16，锁定）。</p>')
# table of contents
t = R(t, '<a href="#p3">第三部分 · 跨阶段：R0/R1 分层分析与两阶段对照</a>',
      '<a href="#p3">第三部分 · 跨阶段：R0/R1 分层、分组对比与“认得出却说不出”</a>\n<span class="sub"><a href="#p3-r0r1">R0/R1 分层</a> · <a href="#pd-groups">A/B/C/D 分组对比与干预重跑</a> · <a href="#pd-sayable">认得出却说不出（瓶颈）</a> · <a href="#pd-a16d">D 名字链条</a> · <a href="#pd-a16b">B 输出格式</a> · <a href="#p3-bridge">两阶段对照</a></span>')
t = R(t, '<a href="#alltok-results">全部名字 token 的 probe（补充 9）</a> · <a href="#x5-results">X5 层序</a> · <a href="#p4-plan">Stage 13 计划</a></span>',
      '<a href="#alltok-results">全部名字 token 的 probe（补充 9）</a> · <a href="#pd-cleandonor">干净供体</a> · <a href="#pd-h3samescale">H3 同尺度</a> · <a href="#x5-results">X5 层序</a> · <a href="#p4-plan">Stage 13 计划</a> · <a href="#pd-running">补充 10–14 状态</a></span>')
t = re.sub(r'<a href="#p5">第五部分 · 答辩后新增（2026-11-05）</a>\s*<span class="sub">.*?</span>',
           '<a href="#p5">第五部分 · 全报告的局限</a>\n<span class="sub"><a href="#pd-limits">不能补做的局限</a></span>', t, count=1, flags=re.S)
assert '第五部分 · 全报告的局限' in t
# cross references
t = R(t, '答辩后新增见第五部分', '分组对比与瓶颈分析见第三部分，补充 9–18b 写入第四部分各节')
t = R(t, '和答辩后新增的分析（第五部分）', '、分组对比与瓶颈分析（第三部分）')
t = R(t, '<b>答辩后新增（2026-11-05），见第五部分。</b>', '<b>分组对比、CPU 补算与补充 6–15（分组对比见第三部分，其余在第四部分各节）：</b>')
t = R(t, '④ 重做计划（补充 10–13，2026-11-05/06 写定）：', '④ 补充 10–13（2026-11-05/06 写定）：')
t = R(t, '与 H3 的关系未预注册，只作讨论（第五部分）。', '与 H3 的关系未预注册，只作讨论（第四部分 <a href="#pd-running">补充 10–14 状态</a>）。')
t = R(t, '（见第五部分“P1 / P2 用 5 个假标题”）', '（见 Stage 12 节 <a href="#pd-b1-p12f">P1 / P2 用 5 个假标题</a>）')
t = R(t, '末尾和第五部分 <a href="#pd-b1-xall">批次 1</a>', '末尾 <a href="#pd-b1-xall">全部作者版本</a>', n=2)
t = R(t, '见<a href="#pd-cpu">第五部分</a>', '见本节下文 <a href="#pd-cpu">X5 预注册的跨任务检索曲线（V56）</a>')
left = [m.start() for m in re.finditer('第五部分|答辩后新增|重做计划', t)]
open(f, 'w', encoding='utf-8').write(t)
print('report leftovers', [re.sub(r'\s+', ' ', t[max(0, k - 60):k + 40]) for k in left])

# ================================================================== (3) handbook: dissolve "十一"
f = REP + 'methods/methods_handbook.html'; t = open(f, encoding='utf-8').read()


def h3_block(t, hid):
    i = t.index('<h3 id="%s">' % hid)
    nxt = [x for x in (t.find('<h3', i + 4), t.find('<h2', i + 4), t.find('</section>', i + 4)) if x > 0]
    return i, min(nxt)


def cut_h3(t, hid):
    i, j = h3_block(t, hid); return t[:i] + t[j:], t[i:j]


t, kg = cut_h3(t, 'k-groups'); t, kp = cut_h3(t, 'k-p1p2-numden'); t, ks = cut_h3(t, 'k-sayable')
t, kc = cut_h3(t, 'k-cleandonor'); t, kcpu = cut_h3(t, 'k-cpu'); t, kr = cut_h3(t, 'k-running'); t, kl = cut_h3(t, 'k-limits')
head, hp = split_h(kcpu, 'h4')
hnote = re.search(r'<p class="note">.*?</p>|<p>.*?</p>', head, re.S)
hnote = hnote.group(0) if hnote else ''
hids = ['k-cpu', 'k-cpu-u46', 'k-cpu-v21', 'k-cpu-v42', 'k-cpu-v29']
hp = [p.replace('<h4>', '<h4 id="%s">' % k, 1) for p, k in zip(hp, hids)]
hp[0] = hp[0].replace('</h4>', '</h4>\n' + hnote.replace('<p', '<p data-k="cpu-note"', 1), 1)
kr = re.sub(r'<h3 id="k-running">.*?</h3>', '<h3 id="k-running"><span class="st">预注册</span> 补充 10–14 各项的状态：完成、停止、不做与偏离（规则 2026-11-05 / 06 起写定）</h3>', kr, count=1, flags=re.S)
kr = kr.replace('重做计划的规则', '补充 10–14 的规则')
kg = kg.replace('</h3>', '</h3>\n<p class="note">图号、表号沿用《Stage 1–13 实验报告》。分组对比的分析计划在看结果前写定（补充 7、8）。</p>', 1)
# the remaining (now empty) k-post section becomes the limitations section
kpost_i = t.index('<section id="k-post">'); kpost_j = t.index('</section>', kpost_i)
oldpost = t[kpost_i:kpost_j]
kl_body = re.sub(r'<h3 id="k-limits">.*?</h3>', '', kl, count=1, flags=re.S)
t = t[:kpost_i] + '<section id="k-post"><h2 id="k-limits">局限：不能补做的局限</h2>\n' + kl_body + t[kpost_j:]


def after_h3(t, hid):
    return h3_block(t, hid)[1]


def end_of_h2_section(t, heading_text):
    i = t.index(heading_text); return t.index('</section>', i)


t = insert_at(t, after_h3(t, 's13-x5'), hp[0])
t = insert_at(t, after_h3(t, 's13-m3'), hp[1])
t = insert_at(t, after_h3(t, 's13-m5'), hp[4])
t = insert_at(t, end_of_h2_section(t, '<h2>N2 纯名字先验（prior_pure）'), hp[2])
t = insert_at(t, end_of_h2_section(t, '>B3. 统计：引用档、分层权重、bootstrap、作者团队、多重比较</h2>'), hp[3])
t = insert_at(t, after_h3(t, 'h-prereg-dev'), kr)
t = insert_at(t, after_h3(t, 's13-alltok'), kc)
t = insert_at(t, after_h3(t, 's1011-s10-r0r1'), kg + kp + ks)
# toc / lead / cross references
t = re.sub(r'<li>十一 答辩后新增（2026-11-05 / 06 / 08）<div class="sub"><a href="#k-post">十一 答辩后新增（2026-11-05 / 06 / 08）</a></div></li>',
           '<li>局限<div class="sub"><a href="#k-limits">不能补做的局限</a></div></li>', t, count=1)
assert '<a href="#k-limits">不能补做的局限</a>' in t
lead_old = re.search(r'（第十一部分：答辩后新增与重做计划；', t)
t = t.replace('（第十一部分：答辩后新增与重做计划；', '（分组对比、补充 10–19 的方法写入各节：分组对比在 Stage 10 R0/R1 之后，补充 10–14 状态在 B5，CPU 补算在各实验节；', 1)
t = t.replace('<a href="#k-cpu">十一 · CPU 补充</a>', '<a href="#k-cpu">X5 节“X5 预注册的跨任务检索曲线（V56）”及各实验节的 CPU 补算</a>')
t = t.replace('见十一 · CPU 补充', '见 M5 节“M5 能用已有数据回答的部分（V29）”')
t = t.replace('见第十一部分 k-b1-p12f', '见 B5“补充 10–14 各项的状态”k-b1-p12f')
open(f, 'w', encoding='utf-8').write(t)
left = [m.start() for m in re.finditer('十一|答辩后新增|重做计划', t)]
print('handbook leftovers', [re.sub(r'\s+', ' ', t[max(0, k - 60):k + 40]) for k in left][:20])

# inline leftovers of the process labels (report + handbook)
for f in (REP + 'stage1_11/stage1_11_report.html', REP + 'methods/methods_handbook.html'):
    t = open(f, encoding='utf-8').read()
    for a, b in [('<a href="#pd-h3samescale">见答辩后新增部分</a>', '<a href="#pd-h3samescale">见第四部分 H3 同尺度节</a>'),
                 ('已列入重做计划（', '已列入（'), ('列入重做计划（', '列入（'), ('答辩后新增的分析，分析计划在看结果前写定', '分析计划在看结果前写定'),
                 ('（答辩后新增，分析计划在看结果前写定）', '（分析计划在看结果前写定）')]:
        t = t.replace(a, b)
    open(f, 'w', encoding='utf-8').write(t)
    print(f.split('/')[-1], 'left:', [re.sub(r'\s+', ' ', t[max(0, m.start() - 40):m.start() + 30]) for m in re.finditer('答辩后新增|重做计划|十一 ·|第十一部分', t)])
