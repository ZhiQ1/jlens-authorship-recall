"""Addendum 21 (C37) into the 8 local docs, after the late-MLP (item 4 / route) paragraph. Backups .before_20261121_a21."""
import re, shutil, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from a21_texts_20261121 import *
REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
src = lambda s: '<span class="src">（' + s + '）</span>'
def hits(t):
    out = []
    for m in re.finditer(r'<(p|li)\b[^>]*>.*?</\1>', t, flags=re.S):
        b = t[m.start():m.end()]
        if 'L57' in b and 'MLP' in b and 'L61' in b: out.append((m.end(), m.group(1)))
    return out
def edit(f, plan):
    p = REP + f; bk = p + '.before_20261121_a21'
    if not os.path.exists(bk): shutil.copy2(p, bk)
    t = open(bk, encoding='utf-8').read(); H = hits(t)
    for idx, text in sorted(plan, key=lambda x: -H[x[0]][0]):
        end, tag = H[idx]; t = t[:end] + f'\n<{tag}>' + text + f'</{tag}>' + t[end:]
    open(p, 'w', encoding='utf-8').write(t); print('edited', f, len(H))
note = '<span class="src">' + NOTE + '</span>'
edit('stage1_11/stage1_11_report.html', [(0, A21 + src(SRC) + note)])
edit('methods/methods_handbook.html', [(1, A21 + src(SRC) + note)])
edit('talk_docs/experiment_walkthrough_methods_zh.html', [(0, A21 + src(SRC))])
edit('talk_docs/experiment_walkthrough_zh.html', [(0, A21s + src(SRC))])
edit('talk_docs/methods_handbook_guide_plain_zh.html', [(0, A21s + src(SRC))])
edit('advisor/index.html', [(0, A21s + src(SRC))])
edit('process_report/index.html', [(0, A21s + src(SRC) + note)])
edit('talk_docs/stage13_script_zh_en.html', [(0, A21s + src(SRC)), (1, A21_EN + '<span class="src">(' + SRC_EN + ')</span>')])
