"""claims_defs v26 (2026-11-19): v25 (unchanged file) + addendum 18b (shelf map, locked 2026-11-17, sha256 9104c351…; 600-paper subsample):
item 4 (L57-L61 mean ablation), item 2 (windowed attention blocking), item 6 (MLP lookup), item 3 (per-cell patching),
item 5 (title-token importance), item 1 (readout map).
Sources: 381_stage13/summary_a18b_item{1..6}/*.csv.  New ids 'A26-'.  Run with:  CLAIMS_DEFS=claims_defs_v26 bash claims_run.sh"""
from claims_defs_v25 import *          # noqa: F401,F403
from claims_defs_v25 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A26-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'


def tri3(cid, stmt, f, est, lo, hi, comp, n, dec, lead, sign=True, **w):
    """value [lo, hi] written after one of the lead regexes."""
    A(cid, stmt, csv(f, est, **w), comp, n, dec, [l + '#(?= \\[)' for l in lead], sign=sign)
    A(cid + '-lo', stmt + '（下限）', csv(f, lo, **w), comp, n, dec, [l + SN + r' \[#(?=, )' for l in lead], sign=False)
    A(cid + '-hi', stmt + '（上限）', csv(f, hi, **w), comp, n, dec, [l + SN + r' \[' + SN + r', #\]' for l in lead], sign=False)


R = '381_stage13/summary_a18b_item'
N6 = '600 篇子样本'
# ------------------------------------------------------------------ item 4
C4 = '补充 18b 第 4 项：L57–L61 一层一部件均值消融，S = 真 − 5 个假标题平均，loss = S(none) − S(config)，团队整群 bootstrap 2,000 次（配对）；'
F4 = R + '4/item4_criterion.csv'
tri3('i4-mean', '18b-4：MLP − 注意力损失，5 层平均', F4, 'mlp_minus_attn_loss', 'lo', 'hi', C4, N6, 3,
     [r'MLP − 注意力 ', r'MLP − attention ', r'平均多 ', r'锁定判据成立，'], layer='mean')
A('i4-min', '18b-4：每层 MLP − 注意力（最小）', csv(F4, 'mlp_minus_attn_loss', 'min', layer=[57, 58, 59, 60, 61]), C4, N6, 3,
  [r'#(?= 到 \+0\.046)', r'#(?= to \+0\.046)'])
A('i4-max', '18b-4：每层 MLP − 注意力（最大）', csv(F4, 'mlp_minus_attn_loss', 'max', layer=[57, 58, 59, 60, 61]), C4, N6, 3,
  [r'\+0\.037 到 #', r'\+0\.037 to #'])
tri3('i4-tc', '18b-4：差的 target − control', F4, 'tc', 'tc_lo', 'tc_hi', C4, N6, 3, [r'更大（target − control ', r'target − control of the difference '], layer='mean')
T4 = R + '4/item4_table.csv'
A('i4-attn', '18b-4：注意力消融损失（最大）', csv(T4, 'all', 'max', quantity=['loss_attn%d' % l for l in range(57, 62)]), C4, N6, 4,
  [r'注意力消融损失 ≤ #', r'attention losses ≤ #', r'注意力消融 ≤ #'], sign=False)
A('i4-shmin', '18b-4：MLP 消融占 S(none)（最小）', csv(T4, 'share_of_S', 'min', quantity=['loss_mlp%d' % l for l in range(57, 62)]), C4, N6, 0,
  [r'(?<![\d.])#(?=–14%)'], sign=False, scale=100)
A('i4-shmax', '18b-4：MLP 消融占 S(none)（最大）', csv(T4, 'share_of_S', 'max', quantity=['loss_mlp%d' % l for l in range(57, 62)]), C4, N6, 0,
  [r'11–#(?=%)'], sign=False, scale=100)
# ------------------------------------------------------------------ item 2
C2 = '补充 18b 第 2 项：4 层窗口内只断开一条边，S 损失，团队整群 bootstrap 2,000 次；'
F2 = R + '2/item2_table.csv'
for w, lead in [('L44-47', [r'名字←标题[^\d]{0,30}', r'name ← title \(', r'名字←标题这条边（']),
                ('L48-51', [r'\+0\.0063 \[0\.0046, 0\.0079\]、']), ('L52-55', [r'\+0\.0112 \[0\.0084, 0\.0138\]、'])]:
    tri3('i2-' + w, '18b-2：%s 名字←标题损失' % w, F2, 'loss', 'lo', 'hi', C2, N6, 4, lead, window=w, edge='name<-title')
A('i2-share', '18b-2：单边损失占 S（最大）', csv(F2, 'share_of_S', 'max'), C2, N6, 1, [r'最多(?:只)?(?:是|占|去掉)[^\d]{0,25}#(?=%)', r'at most #(?=% of S)', r'≤ #(?=% of S|% 的 S|%）)'], sign=False, scale=100)
# ------------------------------------------------------------------ item 6
C6 = '补充 18b 第 6 项：真 → 假替换 MLP / 注意力输出（全部 / 对齐 512 维 / 正交 / 随机），恢复比例五标题平均，团队整群 bootstrap 2,000 次；'
F6 = R + '6/item6_patch_mean5.csv'
L5 = [52, 53, 54, 55, 56]
for kind, zh in [('mlp_full', r'(?:每层恢复 |recovers )'), ('attn_full', r'(?:注意力 |attention )'), ('mlp_aligned', r'(?:只恢复 |recovers only )'),
                 ('mlp_rand', r'(?:子空间（|512 dims )'), ('mlp_orth', r'(?:正交部分（|正交部分 |orthogonal \()')]:
    A('i6-%s-min' % kind, '18b-6：%s 恢复（最小）' % kind, csv(F6, 'recovery', 'min', kind=kind, layer=L5), C6, N6, 3, [zh + r'#(?=–)'], sign=False)
    A('i6-%s-max' % kind, '18b-6：%s 恢复（最大）' % kind, csv(F6, 'recovery', 'max', kind=kind, layer=L5), C6, N6, 3, [zh + SN + '–#'], sign=False)
tri3('i6-m52', '18b-6：L52 整个 MLP 恢复', F6, 'recovery', 'lo', 'hi', C6, N6, 3, [r'（L52 '], config='mlp_full@52')
tri3('i6-m54', '18b-6：L54 整个 MLP 恢复', F6, 'recovery', 'lo', 'hi', C6, N6, 3, [r'，L54 '], config='mlp_full@54')
N6f = R + '6/item6_neurons.csv'
A('i6-jw-min', '18b-6：同论文 Jaccard（最小）', csv(N6f, 'jaccard_within', 'min'), C6, N6, 3, [r'Jaccard #(?=–)'], sign=False)
A('i6-jw-max', '18b-6：同论文 Jaccard（最大）', csv(N6f, 'jaccard_within', 'max'), C6, N6, 3, [r'Jaccard ' + SN + '–#'], sign=False)
# ------------------------------------------------------------------ item 3
C3 = '补充 18b 第 3 项：逐格替换，恢复比例五标题平均，团队整群 bootstrap 2,000 次；'
F3 = R + '3/item3_mean5.csv'
for k3, (g, L, lead) in enumerate([('names', 40, r'(?<![\d.])#(?=（L40）→)'), ('names', 48, r'0\.176（L40）→ #'), ('names', 52, r'0\.605（L48）→ #'), ('names', 56, r'0\.835（L52）→ #'),
                   ('colon', 48, r'(?:来得晚：|晚到（)L48 #(?= → L52)'), ('colon', 52, r'L48 0\.073 → L52 #'),
                   ('whole_tail', 40, r'整个尾部 #(?=（L40）)'), ('whole_tail', 48, r'0\.292（L40）、#'), ('whole_tail', 52, r'0\.804（L48）、#')]):
    A('i3-%s-%d-%d' % (g, L, k3), '18b-3：%s L%d 恢复' % (g, L), csv(F3, 'recovery', group=g, layer=L), C3, N6, 3, [lead], sign=False)
A('i3-p5max', '18b-3：p5 最高', csv(F3, 'recovery', 'max', group='p5'), C3, N6, 3, [r'最高 #(?=）|，| 后)', r'peaks at #'], sign=False)
A('i3-small', '18b-3：p9 与其余尾部（最大）', csv(F3, 'recovery', 'max', group=['p9', 'other_tail']), C3, N6, 3, [r'其余尾部(?:都)? ≤ #'], sign=False)
A('i3-tcmin', '18b-3：整个尾部 T − C L40–L50（离 0 最近）', csv(F3, 't_minus_c', 'max', group='whole_tail', layer=list(range(40, 51))), C3, N6, 3, [r'L40–L50 target − control #(?= 到)'])
A('i3-tcmax', '18b-3：整个尾部 T − C L40–L50（最负）', csv(F3, 't_minus_c', 'min', group='whole_tail', layer=list(range(40, 51))), C3, N6, 3, [r'L40–L50 target − control ' + SN + ' 到 #'])
# ------------------------------------------------------------------ item 5
C5 = '补充 18b 第 5 项：标题词替换，最终输出 loss = 真 − 变体，团队整群 bootstrap 2,000 次；'
F5 = R + '5/item5_table.csv'
tri3('i5-rand', '18b-5：内容词随机替换损失', F5, 'est', 'lo', 'hi', C5, '600 篇', 3, [r'随机 token 损失 ', r'random tokens costs '], readout='final', quantity='loss_content_rand')
tri3('i5-syn', '18b-5：内容词同义替换损失', F5, 'est', 'lo', 'hi', C5, '596 篇', 3, [r'同义词只损失 ', r'synonyms only '], readout='final', quantity='loss_content_syn')
tri3('i5-diff', '18b-5：同义 − 随机', F5, 'est', 'lo', 'hi', C5, '596 篇', 3, [r'差 ', r'difference '], readout='final', quantity='syn_minus_rand_loss_content')
# ------------------------------------------------------------------ item 1
C1 = '补充 18b 第 1 项：读出地图，满足锁定规则的格子的 target − control；'
M1 = R + '1/item1_map.csv'

# 18b item-6 text "（L52 +0.177 [0.168, 0.187]" must not be read by the older P1 ':' / P1-confounder patterns
for c in C:
    if c['id'] in ('G-P1-conf', 'A18-p1-colon52'):
        c['excl'] = r'整个 MLP 输出每层恢复|full MLP output'
