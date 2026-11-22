"""New H2 wording v2 into the 8 local docs (2026-11-22). From backups .before_20261122_h2w: replace OLD_ZH/OLD_EN with NEW + caveat;
advisor table-cell variant too; ALT_ZH paragraph after the first H2 occurrence in report, handbook, advisor."""
import re, shutil, sys, os, importlib
sys.path.insert(0, os.path.dirname(__file__))
import h2w_texts_20261122 as T; importlib.reload(T)
REP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
ADV_OLD = '部分支持：存在真实论文成分，但大部分可由语义相似解释（补充 20，锁定）'
ADV_NEW = '部分支持：真标题比同义编造标题多出一部分（R̄_T +0.106），大部分由意思承担；多出部分主要在罕见、具体的词上（补充 24），认得出的论文上不更大（K4），引用多的论文上更小（K4c 反向）'
def edit(f, add_alt):
    p = REP + f; bk = p + '.before_20261122_h2w'
    if not os.path.exists(bk): shutil.copy2(p, bk)
    t = open(bk, encoding='utf-8').read(); nz, ne = t.count(T.OLD_ZH), t.count(T.OLD_EN)
    if add_alt:
        i = t.index(T.OLD_ZH); m = next(re.finditer(r'</(p|li)>', t[i:])); end = i + m.end(); tag = m.group(1)
        t = t[:end] + f'\n<{tag}>' + T.ALT_ZH + '<span class="src">（' + T.SRC + '）</span>' + f'</{tag}>' + t[end:]
    t = t.replace(T.OLD_ZH, T.NEW_ZH + T.CAV_ZH).replace(T.OLD_EN, T.NEW_EN + ' ' + T.CAV_EN)
    na = t.count(ADV_OLD); t = t.replace(ADV_OLD, ADV_NEW + T.CAV_ZH)
    open(p, 'w', encoding='utf-8').write(t); print('edited', f, 'zh', nz, 'en', ne, 'adv', na, 'alt', add_alt)
for f, a in [('stage1_11/stage1_11_report.html', True), ('methods/methods_handbook.html', True), ('advisor/index.html', True),
             ('process_report/index.html', False), ('talk_docs/experiment_walkthrough_methods_zh.html', False),
             ('talk_docs/experiment_walkthrough_zh.html', False), ('talk_docs/methods_handbook_guide_plain_zh.html', False),
             ('talk_docs/stage13_script_zh_en.html', False)]:
    edit(f, a)
