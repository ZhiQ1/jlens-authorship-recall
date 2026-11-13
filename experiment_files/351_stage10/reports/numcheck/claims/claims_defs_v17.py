"""claims_defs v17 (2026-11-12 n / n(2) / n(3)): v16 (unchanged file) + the all-token / all-author main numbers of documents round n and the
old first-token / first-author values now written in "（旧版只打首 token：…）" / "（旧版只看第一作者：…）" parentheses, each checked against its
OLD source (selectors copied from the existing claims). New ids 'A17-'. Sources: 381_stage13/reports/e4b_alltok.md role tables (all tokens,
V0), summary_b1_xall/x1__all.csv (X1 all authors, test), summary_b1_xall/x3_recovery__all.csv (X3 all authors), reports/b2_m3tok.md (M3);
old: reports/e4b_trainstd_compare.md "all papers" (E4b first token), summary_x1x4/x1_recovery.csv via claim A5-X1-R*, summary_x3/x3_recovery.csv
via claim A7-X3-beh, reports/m3_scores.md / b2_m3tok.md first-author first-token row.
Collisions: AT-giv-L40 and A5-X1-R24 also caught the new chain / all-author forms -> excluded there (EXCL17).
Run with:  CLAIMS_DEFS=claims_defs_v17 bash claims_run.sh"""
import copy
from claims_defs_v16 import *          # noqa: F401,F403
from claims_defs_v16 import C, csv, md, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A17-' + cid; MANUAL[-1] = c['id']


BY = {c['id']: c for c in C}
SEL = lambda cid: copy.deepcopy(BY[cid]['sel'])
NUM = r'[+−\-]?\d\.\d+'
CI_ = r' \[' + NUM + ', ' + NUM + r'\]'
AT = '381_stage13/reports/e4b_alltok.md'
COL = 'title-specific, all papers [team CI]'
CA = '补充 9 全部作者、全部名字 token、按角色，预注册版 V0（只减 false_0），1,395–1,706 篇，团队聚类 95% CI；e4b_alltok.md 角色表；'
ROLES = [('given_first', [r'名的第一个 token ', r'given-name first token ']), ('surname_first', [r'姓的第一个 token ', r'surname first token ']), ('initial', [r'首字母 ', r'initial '])]
for role, labs in ROLES:
    for k, L in enumerate([24, 40, 56]):
        pats = [r'(?:(?<=[：，:,])|(?<=[：，:,] ))' + l + ''.join(NUM + ' / ' for _ in range(k)) + '#' + (r'(?= / )' if k < 2 else r'(?![\d.])') for l in labs]
        A('at-%s-L%d' % (role, L), 'E4b 主数字（补充 9）：%s L%d' % (role, L), md(AT, r'^### ' + role, col=COL, row={'layer': 'L%d' % L}), CA, '1,395–1,706 篇', 3, pats)
# short forms "L40 名首 token +0.124、姓首 token +0.071、首字母 +0.044"
for role, lab in [('given_first', r'L40 名首 token '), ('surname_first', r'名首 token \+0\.\d+、姓首 token '), ('initial', r'姓首 token \+0\.\d+、首字母 ')]:
    A('at-short-%s' % role, 'E4b 主数字（简写）：%s L40' % role, md(AT, r'^### ' + role, col=COL, row={'layer': 'L40'}), CA, '—', 3, [lab + '#'])
# old first-token values (must still match the old source: e4b_trainstd_compare.md "all papers", new = training-fold standardisation)
OLD = r'(?:旧版只打首 token：|old first-token version:? (?:\(E4b\) )?|old first-token: )'
V3 = r'(?P<v>[+]?0\.\d{3})(?!\d)'
for L, cid in [(24, 'E4b-s1-L24'), (40, 'E4b-ts-L40'), (56, 'E4b-ts-L56')]:
    k = [24, 40, 56].index(L)
    lead = OLD + r'L24 ' + ''.join(NUM + r'[，、]L%d ' % LL for LL in [40, 56][:k])
    pats = [lead + V3,
            OLD + r'L24 约 \+0\.0\d，L40 约 \+0\.0\d，L56 约 \+0\.0\d（' + ''.join(NUM + ' / ' for _ in range(k)) + '#',
            OLD + r'about \+0\.0\d at L24, \+0\.0\d at L40 and \+0\.0\d at L56, ' + ''.join(NUM + ' / ' for _ in range(k)) + '#']
    if L == 40:
        pats += [OLD + r'L40 #(?= \[)', OLD + r'#(?=​?\()', r'\(old first-token: #\)']
    A('old-e4b-L%d' % L, 'E4b 旧版（只打首 token）L%d' % L, SEL(cid), BY[cid]['comp'], BY[cid]['n'], 3, pats)
    A('old-e4b-L%d-2' % L, 'E4b 旧版 L%d（“约”两位写法）' % L, SEL(cid), BY[cid]['comp'], BY[cid]['n'], 2,
      [OLD + r'L24 约 ' + ''.join(r'[+]?0\.0\d(?:，到|，)L%d 约 ' % LL for LL in [40, 56][:k]) + r'(?P<v>[+]?0\.\d{2})(?!\d)',
       OLD + r'L24 约 [+]?0\.0\d，到 L56 约 (?P<v>[+]?0\.\d{2})(?!\d)' if L == 56 else r'(?!x)x',
       OLD + r'about ' + ''.join(r'\+0\.0\d at L%d, ' % LL for LL in [24, 40][:k]) + r'(?P<v>\+0\.\d{2})(?= at L%d)' % L])
for cid, suf, rx in [('A5-E4b-tsL40ci-lo', '-lo', OLD + r'L40 ' + NUM + r' \[#'), ('A5-E4b-tsL40ci-hi', '-hi', OLD + r'L40 ' + NUM + r' \[' + NUM + ', #\]')]:
    A('old-e4b-L40' + suf, 'E4b 旧版 L40' + suf, SEL(cid), BY[cid]['comp'], '1,395 篇', 3, [rx], sign=False)
A('old-e4b-rmin', 'E4b 旧版 L24–L60 最小（两位）', SEL('E4b-ts-rmin'), BY['E4b-ts-rmin']['comp'], '—', 2, [OLD + r'#(?= 到 \+0\.0\d)'])
A('old-e4b-rmax', 'E4b 旧版 L24–L60 最大（两位）', SEL('E4b-ts-rmax'), BY['E4b-ts-rmax']['comp'], '—', 2, [OLD + r'\+0\.0\d 到 #'])
# X1 all authors (main) and old first-author values
X1A = '381_stage13/summary_b1_xall/x1__all.csv'
CX = '补充 10 第 1 项 X1 全部作者，测试集 582 对，作者问法来源 R_authors；x1__all.csv；'
for L, z in [(24, [r'R ≈ #(?= \(L24\))', r'全部作者 L24 约 #', r'在 L24 约 #(?=、L40 0\.93)', r'all authors R #(?= at L24)', r'L24 \+#(?= \+0\.990)']),
             (40, [r'#(?= \(L40\), 0\.455)', r'全部作者 L24 约 0\.996，L40 约 #', r'L40 #(?=、L48 0\.455)', r'0\.996 at L24, #(?= at L40)', r'L40 \+#(?= \+0\.928)']),
             (48, [r'0\.933 \(L40\), #(?= \(L48\))', r'L40 约 0\.933，L48 约 #', r'L40 0\.933、L48 #', r'L48 \+#(?= \+0\.431)'])]:
    A('x1all-R%d' % L, 'X1 全部作者 R(L%d)' % L, csv(X1A, 'R_authors', split='test', layer=L), CX, '582 对', 3, z, sign=False)
for L, cid, z in [(24, 'A5-X1-R24', [r'旧版只看第一作者：L24 约 #', r'(?:old first-author version: |旧版只看第一作者：)#(?= / 0\.9)', r'old first-author version: #(?=, 0\.92)']),
                  (40, 'A5-X1-R40', [r'旧版只看第一作者：L24 约 0\.99，L40 约 #', r'(?:old first-author version: |旧版只看第一作者：)0\.99 / #', r'old first-author version: 0\.99, #']),
                  (48, 'A5-X1-R48', [r'旧版只看第一作者：L24 约 0\.99，L40 约 0\.92，L48 约 #', r'(?:old first-author version: |旧版只看第一作者：)0\.99 / 0\.92 / #'])]:
    A('old-x1-R%d' % L, 'X1 旧版（只看第一作者）R(L%d)' % L, SEL(cid), BY[cid]['comp'], BY[cid]['n'], 2, z, sign=False)
# X3 all authors (main) and old first-author values
X3A = '381_stage13/summary_b1_xall/x3_recovery__all.csv'
XW = dict(set='primary', subset='all', split='test', false='lexical_neighbour_D')
LX = [r'全部作者、全部名字 token ', r'全部作者全部 token ', r'all authors, all tokens ']
A('x3all', 'X3 全部作者全部 token 恢复比', csv(X3A, 'ratio', group='all', **XW), '补充 10 第 1 项；x3_recovery__all.csv', '552 篇', 3, [l + '#(?= \\[)' for l in LX], sign=False)
A('x3all-lo', '同上下限', csv(X3A, 'lo', group='all', **XW), 'x3_recovery__all.csv', '552 篇', 3, [l + NUM + r' \[#' for l in LX], sign=False)
A('x3all-hi', '同上上限', csv(X3A, 'hi', group='all', **XW), 'x3_recovery__all.csv', '552 篇', 3, [l + NUM + r' \[' + NUM + ', #\]' for l in LX], sign=False)
A('x3all-pct', 'X3 全部作者保留的作者偏好（百分数）', csv(X3A, 'ratio', group='all', **XW), 'x3_recovery__all.csv', '552 篇', 0, [r'保留约 #(?=% 的作者偏好)', r'keeps ≈ #(?=% of the author preference)', r'对 D 约 #(?=%（Stage 13 X3 行为恢复比例，全部作者)'], sign=False, scale=100)
T3 = r'全部作者、全部名字 token ' + NUM + CI_ + r'，target − control '
A('x3all-tc', 'X3 全部作者 target − control', csv(X3A, 'ratio', group='target_minus_control', **XW), 'x3_recovery__all.csv', '552 篇', 3, [T3 + '#'])
A('x3all-tc-lo', '同上下限', csv(X3A, 'lo', group='target_minus_control', **XW), 'x3_recovery__all.csv', '552 篇', 3, [T3 + NUM + r' \[#'])
A('x3all-tc-hi', '同上上限', csv(X3A, 'hi', group='target_minus_control', **XW), 'x3_recovery__all.csv', '552 篇', 3, [T3 + NUM + r' \[' + NUM + ', #\]'])
O3 = r'(?:旧版只看第一作者：(?:全部 )?|old first-author version )'
A('old-x3', 'X3 旧版（只看第一作者）恢复比', SEL('A7-X3-beh'), BY['A7-X3-beh']['comp'], '552 篇', 2, [O3 + r'#(?= \[)'], sign=False)
for part, suf in [('lo', '-lo'), ('hi', '-hi')]:
    s = SEL('A7-X3-beh'); s['col'] = part
    A('old-x3' + suf, 'X3 旧版恢复比' + suf, s, 'x3_recovery.csv（旧版，第一作者）', '552 篇', 2, [O3 + NUM + r' \[#' if part == 'lo' else O3 + NUM + r' \[' + NUM + ', #\]'], sign=False)
# M3 all tokens (main) and old first-author first-token value
M3 = '381_stage13/reports/b2_m3tok.md'; H = r'Target - control within citation bin'; CO = 'all cohort target/control'
m3 = lambda score, col, part='est': md(M3, H, col=col, part=part, row={'score': score, 'papers': CO})
LM = [r'全部作者全部名字 token ', r'all authors, all name tokens ']
A('m3all', 'M3 全部作者全部名字 token（主数字）', m3('m3_alltok', 'estimate'), 'b2_m3tok.md', '10 档', 3, [l + '#' for l in LM])
A('m3all-lo', '同上下限', m3('m3_alltok', 'team CI', 'est'), 'team CI', '10 档', 3, [l + NUM + r'(?: \[|〔补充 12 第 2-10 项，\[)#' for l in LM])
A('m3all-hi', '同上上限', m3('m3_alltok', 'team CI', 'lo'), 'team CI', '10 档', 3, [l + NUM + r'(?: \[|〔补充 12 第 2-10 项，\[)' + NUM + ', #\]' for l in LM])
OM = r'(?:旧版只看第一作者首 token：|old first-author first-token version )'
A('old-m3', 'M3 旧版（只看第一作者首 token）', m3('m3_first_exact', 'estimate'), 'b2_m3tok.md m3_first_exact（= m3_scores.md 第 3 节）', '10 档', 3, [OM + '#'])
A('old-m3-lo', '同上下限', m3('m3_first_exact', 'team CI', 'est'), 'team CI', '10 档', 3, [OM + NUM + r'(?: \[|〔\[)#'])
A('old-m3-hi', '同上上限', m3('m3_first_exact', 'team CI', 'lo'), 'team CI', '10 档', 3, [OM + NUM + r'(?: \[|〔\[)' + NUM + ', #\]'])
# round o: C15 addition, X4 all-author decodability from L8 (tune-selected layer, confirmed on test)
XE = '381_stage13/summary_b1_xall/x4_earliest__all.csv'
XEW = dict(answer='author', pos='title', stratum='all')
LO = [r'全作者版本同样从 L8 起可解码[（：]测试集 ', r'all-author version also from L8, test ', r'all authors also from L8: ', r'all-author version is (?:also )?decodable from L8 \(test ', r'all authors[^.;]{0,30}from L8 \(test ']
CO_ = '补充 10 第 1 项 X4 全部作者，调参集选层 L8、测试集确认；x4_earliest__all.csv（= b1_xall_report.md 第 179、203 行）；'
A('x4all-L8', 'X4 全部作者 L8 测试集 D', csv(XE, 'D_test', **XEW), CO_, '测试集 582 对', 3, [l + '#' for l in LO])
A('x4all-L8-lo', '同上下限', csv(XE, 'lo_test', **XEW), CO_, '582 对', 3, [l + NUM + r' \[#' for l in LO])
A('x4all-L8-hi', '同上上限', csv(XE, 'hi_test', **XEW), CO_, '582 对', 3, [l + NUM + r' \[' + NUM + ', #\]' for l in LO])
# round o: old first-token target − control range "+0.03 到 +0.08" and signal range "+0.05 到 +0.08" inside the 旧版 parentheses (old sources)
OLD2 = r'(?:旧版只打首 token：|old first-token version: )'
A('old-e4b-tcmin', 'E4b 旧版目标−对照 L24–L60 最小（两位）', SEL('E4b-tc-ts-min'), BY['E4b-tc-ts-min']['comp'], '—', 2,
  [OLD2 + r'[^）)]{0,40}?(?:target 比 control 高|目标组比对照组高|target exceeds control by) #(?= (?:到|to))'])
A('old-e4b-tcmax', 'E4b 旧版目标−对照 L24–L60 最大（两位）', SEL('E4b-tc-max'), BY['E4b-tc-max']['comp'], '—', 2,
  [OLD2 + r'[^）)]{0,40}?(?:target 比 control 高|目标组比对照组高|target exceeds control by) \+0\.0\d (?:到|to) #'])
A('old-e4b-smin', 'E4b 旧版信号 L24–L60 最小（两位）', SEL('E4b-ts-rmin'), BY['E4b-ts-rmin']['comp'], '—', 2, [OLD2 + r'(?:从 L24 起 )?#(?= (?:到|to) \+0\.08)'])
A('old-e4b-smax', 'E4b 旧版信号 L24–L60 最大（两位）', SEL('E4b-ts-rmax'), BY['E4b-ts-rmax']['comp'], '—', 2, [OLD2 + r'(?:从 L24 起 )?\+0\.05 (?:到|to) #'])
EXCL17 = {'AT-giv-L40': r'L24 / L40 / L56|at L24 / L40 / L56', 'A5-X1-R24': r'0\.996|全部作者 L24|for all authors'}
for c in C:
    if c['id'] in EXCL17:
        c['excl'] = EXCL17[c['id']] if not c.get('excl') else c['excl'] + '|' + EXCL17[c['id']]
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
