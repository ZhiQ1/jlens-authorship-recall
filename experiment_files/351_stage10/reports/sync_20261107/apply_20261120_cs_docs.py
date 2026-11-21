"""Exploratory citation median split into docs next to the arrival (C02/C04) text, 2026-11-20. Backups .before_20261120_cs."""
import shutil, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from cs_texts_20261120 import *
REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
src = lambda s: '<span class="src">（' + s + '）</span>'
A_P = '规则 381_stage13/config/prereg_addendum18.md 第 3 项）</span></p>'
A_LI = 'prereg_addendum18.md 第 3 项）</span></li>'

def edit(path, ops):
    bk = path + '.before_20261120_cs'
    if not os.path.exists(bk): shutil.copy2(path, bk)
    t = open(bk, encoding='utf-8').read()
    for anchor, new, mode in ops:
        assert t.count(anchor) == 1, (path, anchor[:50], t.count(anchor))
        t = t.replace(anchor, anchor + new if mode == 'after' else new + anchor if mode == 'before' else new)
    open(path, 'w', encoding='utf-8').write(t); print('edited', path)

P = '\n<p>' + CS + src(SRC) + '</p>'
for f in ['stage1_11/stage1_11_report.html', 'methods/methods_handbook.html', 'talk_docs/experiment_walkthrough_methods_zh.html']:
    edit(REP + f, [(A_P, P, 'after')])
for f in ['talk_docs/experiment_walkthrough_zh.html', 'talk_docs/methods_handbook_guide_plain_zh.html']:
    edit(REP + f, [(A_P, '\n<p>' + CSs + src(SRC) + '</p>', 'after')])
for f in ['advisor/index.html', 'process_report/index.html']:
    edit(REP + f, [(A_LI, A_LI[:-5] + '<br>' + CSs + src(SRC) + '</li>', 'replace')])
s13 = REP + 'talk_docs/stage13_script_zh_en.html'
edit(s13, [(A_P, '\n<p>' + CSs + src(SRC) + '</p>', 'after')])
t = open(s13, encoding='utf-8').read()
k = t.find('arrival range therefore reads'); k2 = t.find('</p>', k) + 4
t = t[:k2] + '\n<p>' + CS_EN + '<span class="src">(' + SRC_EN + ')</span></p>' + t[k2:]
open(s13, 'w', encoding='utf-8').write(t)
