"""claims_defs v32 (2026-11-22): v31 + (1) X1 authors − year L48: accept the all-author test value (x1__all.csv) as consistent
(the deck now shows +0.024; first-author value 0.019 stays the selected source for older first-author text); (2) addendum 24 and
addendum 22 Part A numbers in the new H2 wording. New ids 'A32-'.  Run with:  CLAIMS_DEFS=claims_defs_v32 bash claims_run.sh"""
from claims_defs_v31 import *          # noqa: F401,F403
from claims_defs_v31 import C, csv, MANUAL
from claims_defs_v5 import A as _A5

X1ALL = '381_stage13/summary_b1_xall/x1__all.csv'
for c in C:
    for suf, col in (('', 'a_minus_year'), ('-lo', 'a_minus_year_lo'), ('-hi', 'a_minus_year_hi')):
        if c.get('id') == 'A5-X1-amy48' + suf:
            c['alt'] = list(c.get('alt') or []) + [('all-author test (x1__all.csv)', csv(X1ALL, col, split='test', layer=48), '一致')]

X2ALL = '381_stage13/summary_b1_xall/x2_curves_new__all.csv'
for c in C:
    if c.get('id') == 'A5-X2-idRS':
        c['alt'] = list(c.get('alt') or []) + [('all-author X2 (x2_curves_new__all.csv)', csv(X2ALL, 'value', split='test', arm='carry', S='id', layer=40, stratum='all'), '一致')]
    if c.get('id') == 'A5-X2-authfull':
        c['alt'] = list(c.get('alt') or []) + [('all-author X2 (x2_curves_new__all.csv)', csv(X2ALL, 'value', split='test', arm='carry', S='full', layer=48, stratum='all'), '一致')]

def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A32-' + cid; MANUAL[-1] = c['id']

R24 = '391_groups/summary_a24/a24_results.csv'
CF24 = '补充 24（锁定），target 418 篇，团队整群 bootstrap；'
A('a24-Ra', '补充 24：只换罕见词损失 R̄（target）', csv(R24, 'est', group='target', quantity='Rbar_a'), CF24, '418 篇', 3,
  [r'只替换这些词损失 R̄ = #', r'replacing only those words loses R̄ = #', r'只换罕见词损失 R̄ #', r'只换罕见词损失 R̄_a = #'], sign=False)
A('a24-Rb', '补充 24：只换常见词损失 R̄（target）', csv(R24, 'est', group='target', quantity='Rbar_b'), CF24, '418 篇', 3,
  [r'只替换常见词损失 #', r'vs #(?= for common words)', r'只换常见词 #(?= \[0\.019)', r'只换常见词损失 R̄_b = #'], sign=False)
A('a24-D', '补充 24：差 D（target）', csv(R24, 'est', group='target', quantity='D = Rbar_a - Rbar_b'), CF24, '418 篇', 3,
  [r'差 \+?#(?= \[0\.115)', r'差 D = #(?= \[0\.115)'])
K = '391_groups/summary_a22_partA/contrasts.csv'
CFK = '补充 22 Part A（锁定），1,083 篇；'
A('K4c48', '补充 22A：K4c L48', csv(K, 'est', contrast='K4c', layer=48), CFK, '1,083 篇', 3, [r'L48 #(?= \[Holm −0\.166)', r'到 L48 #(?=，Holm)'])
A('K4-24', '补充 22A：K4 L24（未校正）', csv(K, 'est', contrast='K4', layer=24), CFK, '1,083 篇', 3, [r'L24 未校正 #(?= \[0\.001)', r'只有 L24 未校正 #'])
