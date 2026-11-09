"""claims_defs v12 (2026-11-09 f): v11 (unchanged file) + the M2 five-false-title numbers of documents round f
(sync_20261108c_manifest.md "round f"). New ids 'A12-'. Sources: 381_stage13/summary_m2_f5/M2_f5_mean.csv (position = title rows:
false_mean5 / false_0 / min5 / max5; max |true − false| over the 36 title rows; rows whose team-CI lower bound is above null for all 5 titles)
and summary_m2_f5/exclusion_audit.csv (exclusion rows a / b / b2 / d; c_donor_as_target_in_train for group = all, written rounded to tens).
Run with:  CLAIMS_DEFS=claims_defs_v12 bash claims_run.sh"""
import pandas as pd
from claims_defs_v11 import *          # noqa: F401,F403
from claims_defs_v11 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, py
from claims_lib import JL


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A12-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
MF = '381_stage13/summary_m2_f5/M2_f5_mean.csv'
EA = '381_stage13/summary_m2_f5/exclusion_audit.csv'
COMP = 'M2 用 5 个假标题（团队分折，标题位置）；M2_f5_mean.csv'
F0Z = r'(?=（false_0 版|\s?\(false_0)'
F0P = r'(?:（false_0 版 | \(false_0 (?:version )?)'


def mf(L, tgt, col):
    return csv(MF, col, position='title', layer=L, target=tgt)


ITEMS = [('y48', 48, 'year', [r'L48 读借出论文的年份 R² ', r'L48 year ', r'L48 donor 年份 R² ', r'L48 donor year R² ', r'L48 year R² ']),
         ('c48', 48, 'log citations', [r'(?<!去掉年份后的)引用数 ', r'log citations ', r'log 引用 ']),
         ('cy48', 48, 'log citations | year removed', [r'去掉年份后的引用数 ', r'citations\|year ', r'citations \| year ']),
         ('f48', 48, 'field', [r'领域准确率 ', r'field acc(?:uracy)? ']),
         ('y16', 16, 'year', [r'年份 L16 ', r'year L16 ']),
         ('y52', 52, 'year', [r'L52 '])]
for cid, L, tgt, labs in ITEMS:
    A('M2f5-%s' % cid, 'M2 五个假标题平均：L%d %s' % (L, tgt), mf(L, tgt, 'false_mean5'), COMP + ' false_mean5', '9,108 篇', 3,
      [l + '#' + (F0Z if cid != 'cy48' else r'(?=（5 个假标题|（false_0 版|\s?\(false_0)') for l in labs], sign=False)
    A('M2f5-%s-f0' % cid, 'M2 五个假标题：L%d %s 的 false_0 值' % (L, tgt), mf(L, tgt, 'false_0'), COMP + ' false_0', '9,108 篇', 3,
      [l + NUM + F0P + '#' for l in labs] + ([r'去掉年份后的引用数 ' + NUM + r'（5 个假标题 ' + NUM + '–' + NUM + '；false_0 版 #'] if cid == 'cy48' else []), sign=False)
A('M2f5-cy48-min', 'M2：L48 去掉年份后的引用数，5 个假标题最小', mf(48, 'log citations | year removed', 'min5'), COMP + ' min5', '9,108 篇', 3, [r'（5 个假标题 #–'], sign=False)
A('M2f5-cy48-max', 'M2：同上最大', mf(48, 'log citations | year removed', 'max5'), COMP + ' max5', '9,108 篇', 3, [r'（5 个假标题 ' + NUM + '–#'], sign=False)


def _t():
    d = pd.read_csv(JL / MF); return d[d.position == 'title']


A('M2f5-maxdiff', 'M2：标题位置各行 |真 − 5 个假标题平均| 最大', py(lambda: _t().true_minus_mean5.abs().max(), 'M2_f5_mean.csv title 行 |true_minus_mean5| 最大', [MF]), COMP, '36 行', 3,
  [r'最大差 #(?=（false_0 版)', r'max(?:imum)? \|true − false\| #'], sign=False)
A('M2f5-maxdiff-f0', 'M2：同上 false_0 版', py(lambda: _t().true_minus_false_0.abs().max(), 'M2_f5_mean.csv title 行 |true_minus_false_0| 最大', [MF]), COMP, '36 行', 3,
  [r'最大差 ' + NUM + r'（false_0 版 #'], sign=False)
A('M2f5-above', 'M2：5 个假标题都高于随机的标题位置行数', py(lambda: int((_t().titles_lo_team_above_null == _t().n_titles).sum()), 'title 行中 titles_lo_team_above_null == n_titles 的行数', [MF]), '计数', '36 行', 0,
  [r'# 个标题位置的行对 5 个假标题都高于随机', r'# / 36 (?:title-position )?rows'], sign=False)
A('M2f5-rows', 'M2：标题位置行数', py(lambda: len(_t()), 'title 行数', [MF]), '计数', '—', 0, [r'36 / # (?:title-position )?rows'], sign=False)


def _ea():
    return pd.read_csv(JL / EA)


A('M2f5-excl', 'M2：标题复用 / 供体在训练折的排除行数（每个假标题，最大）',
  py(lambda: _ea()[['a_title_reuse', 'b_donor_label_in_train', 'b2_donor_team_in_train', 'd_true_title_in_train']].to_numpy().max(), 'exclusion_audit.csv 列 a / b / b2 / d 的最大值', [EA]), '计数', '—', 0,
  [r'(?:都|均)为 # 行', r'exclusion is # rows'], sign=False)
A('M2f5-ctr-min', 'M2：供体论文以 target 行出现在训练折的行数（每个假标题最小，取整到十位）',
  py(lambda: round(_ea().query("group == 'all'").c_donor_as_target_in_train.min(), -1), 'exclusion_audit.csv group = all，c_donor_as_target_in_train 最小（7,237），取整到十位', [EA]), '计数（约）', '—', 0,
  [r'约 #–7,3\d0 行', r'about #–7,3\d0 rows'], sign=False, note='文中写“约”，按十位取整比较')
A('M2f5-ctr-max', 'M2：同上最大（7,373），取整到十位',
  py(lambda: round(_ea().query("group == 'all'").c_donor_as_target_in_train.max(), -1), 'exclusion_audit.csv group = all，c_donor_as_target_in_train 最大，取整到十位', [EA]), '计数（约）', '—', 0,
  [r'约 7,2\d0–# 行', r'about 7,2\d0–# rows'], sign=False, note='文中写“约”，按十位取整比较')
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
