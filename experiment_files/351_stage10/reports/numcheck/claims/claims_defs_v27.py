"""claims_defs v27 (2026-11-19 b): v26 (unchanged file) + the user's exact bottleneck-C sentence
"about half are not in the data, the same as the shuffled baseline (50.4% vs 50.5%); co-authors are only 4.0% (chance 1.3%)"
(Chinese: 约一半不在数据中，与打乱基线相同（50.4% vs 50.5%）；是合作者的只有 4.0%（随机 1.3%）).
Sources: 391_groups/summary_fabricated_20261114/class_shares_by_group.csv, chance_baselines.csv.  New ids 'A27-'.
Run with:  CLAIMS_DEFS=claims_defs_v27 bash claims_run.sh"""
from claims_defs_v26 import *          # noqa: F401,F403
from claims_defs_v26 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A27-' + cid; MANUAL[-1] = c['id']


FB = '391_groups/summary_fabricated_20261114/'
CC = '编造名分类（探索性，事后），姓 + 首字母键，全部 8,872 篇 / 40,219 个名字，团队整群 bootstrap 2,000 次；用户 2026-11-19 定的句子；'
SH = dict(keys='si', group='all')
A('c-nid', '瓶颈 C：不在数据中（用户句）', csv(FB + 'class_shares_by_group.csv', 'share', cls='not_in_data', **SH), CC, '8,872 篇', 1,
  [r'（#(?=% vs [\d.]+%）)', r'\(#(?=% vs [\d.]+%\))'], sign=False, scale=100)
A('c-nid-shuf', '瓶颈 C：打乱基线的不在数据中比例（用户句）', csv(FB + 'chance_baselines.csv', 'share', keys='si', baseline='perm_fab_field', group='all', cls='not_in_data'),
  CC + '同领域内打乱，20 次平均', '—', 1, [r'[\d.]+% vs #(?=%[）)])'], sign=False, scale=100)
A('c-co', '瓶颈 C：合作者（用户句）', csv(FB + 'class_shares_by_group.csv', 'share', cls='coauthor', **SH), CC, '8,872 篇', 1,
  [r'是合作者的只有 #(?=%)', r'co-authors are only #(?=%)'], sign=False, scale=100)
A('c-co-shuf', '瓶颈 C：合作者随机基线（用户句）', csv(FB + 'chance_baselines.csv', 'share', keys='si', baseline='perm_fab_field', group='all', cls='coauthor'),
  CC + '同领域内打乱，20 次平均', '—', 1, [r'（随机 #(?=%）)', r'\(chance #(?=%\))'], sign=False, scale=100)
