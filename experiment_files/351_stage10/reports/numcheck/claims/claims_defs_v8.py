"""claims_defs v8 (2026-11-08): v7 (unchanged file) + wording B version 3 (for_user_2026-11-07.md section f; round e,
sync_20261108a_manifest.md). Every number of the three-version sentence is a claim on
381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv (run x layer x version -> tc / tc_lo / tc_hi, n at L40).
Patterns are built per version segment (① / ② / ③, zh and en) and per role; the earlier numbers of the same role are matched by a
generic number pattern, never by a typed value. Version-label consistency of other title-position numbers is checked by
claims_v8_post.py (VERSION_LABELS below). New ids start with 'A8-'.
Run with:  CLAIMS_DEFS=claims_defs_v8 bash claims_run.sh ; then claims_v5_post.py, claims_v7_post.py, claims_v8_post.py <out>"""
from claims_defs_v7 import *          # noqa: F401,F403
from claims_defs_v7 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A8-' + cid; MANUAL[-1] = c['id']


PDL = '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv'
NUM = r'[+−\-]?\d\.\d+'
CIR = r'\[%s, %s\]' % (NUM, NUM)
VDESC = {'V0': '预注册版：真标题 − false_0，false_0 剔除规则', 'Vpd': '逐个假标题排除（偏离 D1），每篇平均约 1.5 个可用假标题',
         'V5x0': '5 个假标题平均，只按 false_0 剔除（含泄漏，仅敏感性参考）'}
COMP = '引用档内 target − control；团队整群 bootstrap 2,000 次 95% CI；perdonor_by_run_layer.csv 列 tc / tc_lo / tc_hi'
RUNS = {'given_first': '名的第一个 token', 'surname_first': '姓的第一个 token', 'initial': '首字母'}

# segments: (version, zh start regex, zh end char, zh role labels, en start, en end char, en role labels, layers per role)
SEG = [('V0', r'① 预注册版', '②', {'given_first': '：名的第一个 token', 'surname_first': '；姓', 'initial': '；首字母'},
        r'① pre-registered', '②', {'given_first': ': given-name first token', 'surname_first': '; surname', 'initial': '; initial'},
        {'given_first': [24, 40, 48], 'surname_first': [24, 40, 48], 'initial': [24, 40, 48]}),
       ('Vpd', r'② 逐个排除版', '③', {'given_first': '：名', 'surname_first': '；姓', 'initial': '；首字母'},
        r'② per-donor exclusion', '③', {'given_first': ': given name', 'surname_first': '; surname', 'initial': '; initial'},
        {'given_first': [24, 40, 48], 'surname_first': [24, 40, 48], 'initial': [24, 40, 48]}),
       ('V5x0', r'③ "5 个假标题平均"版', '结', {'given_first': '：名', 'surname_first': '；姓', 'initial': '；首字母'},
        r'③ "mean of 5 false titles"', 'C', {'given_first': ': given name', 'surname_first': '; surname', 'initial': '; initial'},
        {'given_first': [40], 'surname_first': [40, 48], 'initial': [40]})]


def chain(start, end, role, layers, L, sep):
    pre = ''.join('L%d %s %s%s' % (l, NUM, CIR, sep) for l in layers[:layers.index(L)])
    return start + r'[^' + end + r']*?' + re.escape(role) + ' ' + pre + 'L%d ' % L


import re
for v, zs, ze, zr, es, ee, er, LAY in SEG:
    for run, layers in LAY.items():
        for L in layers:
            z = chain(zs, ze, zr[run], layers, L, '、'); e = chain(es, ee, er[run], layers, L, ', ')
            W = dict(run=run, layer=L, version=v)
            stmt = '措辞 B v3 %s：%s L%d target − control' % (v, RUNS[run], L)
            A('B3-%s-%s-L%d' % (v, run, L), stmt, csv(PDL, 'tc', **W), VDESC[v] + '；' + COMP, '见 n', 3, [z + '#', e + '#'])
            A('B3-%s-%s-L%d-lo' % (v, run, L), stmt + '（下限）', csv(PDL, 'tc_lo', **W), VDESC[v] + '；' + COMP, '见 n', 3,
              [z + NUM + r' \[#', e + NUM + r' \[#'])
            A('B3-%s-%s-L%d-hi' % (v, run, L), stmt + '（上限）', csv(PDL, 'tc_hi', **W), VDESC[v] + '；' + COMP, '见 n', 3,
              [z + NUM + r' \[' + NUM + r', #\]', e + NUM + r' \[' + NUM + r', #\]'])
    # paper counts per role (n at L40)
    zlab = {'given_first': '名 ', 'surname_first': '、姓 ', 'initial': '、首字母 '}
    elab = {'given_first': 'given name ', 'surname_first': ', surname ', 'initial': ', initial '}
    order = ['given_first', 'surname_first', 'initial']
    for i, run in enumerate(order):
        zp = zs + r'[^' + ze + r']*?' + ''.join(re.escape(zlab[r]) + r'[\d,]+' for r in order[:i]) + re.escape(zlab[run]) + '#'
        ep = es + r'[^' + ee + r']*?' + ''.join(re.escape(elab[r]) + r'[\d,]+' for r in order[:i]) + re.escape(elab[run]) + r'(?P<v>\d,\d{3})(?![\d])'
        A('B3-%s-%s-n' % (v, run), '措辞 B v3 %s：%s 篇数' % (v, RUNS[run]), csv(PDL, 'n', run=run, layer=40, version=v), '计数（L40 行 n）', '—', 0, [zp, ep], sign=False)

# conclusion sentence and the compact deck slide 72 form
W0 = dict(run='surname_first', layer=40, version='V0'); WP = dict(run='surname_first', layer=40, version='Vpd'); W5 = dict(run='surname_first', layer=40, version='V5x0')
for tag, W, pe in [('conc-V0', W0, [r'姓在 L24–L48 不显著（L40 ', r'surname is not significant at L24–L48 \(L40 ', r'surname n\.s\. \(L40 ']),
                   ('conc-Vpd', WP, [r'姓从 L24 起为正（L40 ', r'surname is positive from L24 \(L40 ', r'surname \+ from L24 \(L40 ']),
                   ('deck-V5x0', W5, [r'5-title mean \(leaky, sensitivity only\): surname L40 '])]:
    A('B3-%s' % tag, '措辞 B v3 结论句 / 第 72 页：姓 L40（%s）' % W['version'], csv(PDL, 'tc', **W), VDESC[W['version']] + '；' + COMP, '—', 3, [p + '#' for p in pe])
    A('B3-%s-lo' % tag, '同上下限', csv(PDL, 'tc_lo', **W), COMP, '—', 3, [p + NUM + r' \[#' for p in pe])
    A('B3-%s-hi' % tag, '同上上限', csv(PDL, 'tc_hi', **W), COMP, '—', 3, [p + NUM + r' \[' + NUM + r', #\]' for p in pe])
A('B3-deck-n-giv', '第 72 页：预注册版名的篇数', csv(PDL, 'n', run='given_first', layer=40, version='V0'), '计数', '—', 0, [r'pre-registered \(false_0; #'], sign=False)
A('B3-deck-n-sur', '第 72 页：预注册版姓的篇数', csv(PDL, 'n', run='surname_first', layer=40, version='V0'), '计数', '—', 0, [r'pre-registered \(false_0; [\d,]+ / #'], sign=False)
A('B3-deck-n-pd', '第 72 页：逐个排除版姓的篇数', csv(PDL, 'n', run='surname_first', layer=40, version='Vpd'), '计数', '—', 0, [r'per-donor \(post hoc, D1; #'], sign=False)
# RQ1 lower bound (int6, aa_all) — the 0.108 correction
A('RQ1-int6-lo', 'C-2 / D13-1 代理 int6 RQ1 下限', csv('381_stage13/c13_C2_followup/c2_followup_proxy.csv', 'rq1_team_lo', version='aa_all', endpoint='int6'),
  'c2_followup_proxy.csv aa_all int6 rq1_team_lo（团队 bootstrap）', '200 篇', 3, [r'RQ1 \+0\.130 \[#'], sign=False)

# version labels for claims_v8_post.py: label regex -> version key(s) in perdonor_by_run_layer.csv / c3b_role_layer.csv
VERSION_LABELS = [(r'V0\b|预注册版|pre-registered|只减 false_0|false_0 only|只用 false_0', 'V0'),
                  (r'Vpd|逐个(?:假标题)?排除|per-donor', 'Vpd'),
                  (r'V5x0(?!_)|5 个假标题平均"?版|"mean of 5 false titles"|5-title mean', 'V5x0'),
                  (r'C-3b', 'V5x0_noexcl'), (r'(?<!与 )C-3(?!b)', 'V0_noexcl')]
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
