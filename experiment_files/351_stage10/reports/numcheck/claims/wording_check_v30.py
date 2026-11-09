"""Wording check for report v30 / deck v21 / handbook 2026-11-08 c and the pages that repeat them (read-only on documents).
Source of the conclusions: ~/jlens_work/conclusions_v30_draft.md (C01-C23, L01-L14) and conclusions_v30_checks.md.
For every conclusion / limitation K:
  DETECT[K]  : regexes; a document "states" K if any matches anywhere in its visible text (claims_docs.units(), same text as the
               strict number checker, document list = claims_defs_v9 list incl. process_report/draft_zh.md);
  REQUIRE[K] : (label, regex) that must also occur in a document that states K (key number or qualifier) -> 'missing qualifier';
  PAIR       : (label, trigger, partner, window): every trigger must have the partner within +-window chars -> 'missing qualifier (local)';
  STALE      : (label, regex, allowed-context regex or None): phrases that must no longer occur (allowed if the allowed-context
               regex matches within 160 chars before / 80 after, e.g. "原 32 篇时为 0.464") -> 'stale phrase'.
Output: <out>/wording_v30_rows.csv (one row per finding), wording_v30_by_doc.csv (per document: stated / consistent / stale / missing),
<out>/wording_v30_summary.txt.  Usage: ~/conda-envs/jlens/bin/python wording_check_v30.py <out_dir>"""
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import claims_defs_v12 as D12        # noqa: F401  (v9 patches claims_docs.doc_list: + process_report/draft_zh.md)
from claims_docs import units, locate

OUT = Path(sys.argv[1]) / 'wording_v30'
OUT.mkdir(parents=True, exist_ok=True)

ALT = lambda *a: '(?:' + '|'.join(a) + ')'
DETECT = {
    'C01': [r'(?<!“)L24–L48 约为 0(?!”)', r'\+0\.207 \[0\.195', r'title-specific signal.{0,40}L63'],
    'C02': [r'E1.{0,60}L48.{0,40}0\.825', r'L48 已?恢复 ?0\.825', r'recovers? 0\.825'],
    'C03': [r'E2.{0,80}L52.{0,40}0\.007', r'阻断.{0,40}从 L52 起'],
    'C04': [r'P1 / P2 用 5 个假标题', r'P1/P2 五个假标题', r'P1 / P2 五个假标题', r'P1 / P2 with five false titles', r'P1 / P2 用 5 个假标题重算'],
    'C05': [r'A − B.{0,60}\+0\.200', r'\+0\.200 \[0\.188'],
    'C06': [r'M3.{0,60}(?:不高于|not above|no higher than) L4', r'T − T\(L4\)'],
    'C07': [r'Stage 8.{0,120}(?:RQ1|RQ2)', r'CPU 代理.{0,60}RQ1', r'CPU proxy.{0,60}RQ1'],
    'C08': [r'C / D 组补全', r'C 组未写出作者 462', r'groups? C / D', r'C completed to 462', r'C 462 papers'],
    'C09': [r'E4b'],
    'C10': [r'补充 9', r'addendum 9'],
    'C11': [r'① 预注册版', r'① pre-registered'],
    'C12': [r'作者 − 年份', r'author − year'],
    'C13': [r'M2.{0,60}R²'],
    'C14': [r'X3.{0,80}(?:改写|paraphras)'],
    'C15': [r'X4.{0,80}(?:第一作者|first author).{0,40}L8'],
    'C16': [r'F2.{0,80}L62', r'作者提示 lens'],
    'C17': [r'写对 − 没写对', r'written − missed'],
    'C18': [r'C-1.{0,120}Pilot50', r'Pilot50.{0,80}\+0\.244'],
    'C19': [r'姓在 L24–L48 不显著', r'surname is not significant', r'姓的证据弱'],
    'C20': [r'首字母在个别层为正', r'initial.{0,40}inconsistent'],
    'C21': [r'X4.{0,120}(?:认得出|recogni[sz]ed)'],
    'C22': [r'X2.{0,80}(?:子空间|subspace)'],
    'C23': [r'4\.7 倍', r'4\.7×'],
    'L01': [r'L25–L31', r'L33–L39'],
    'L02': [r'0\.25 ?(?:→|放宽到|to) ?0\.5'],
    'L03': [r'1,186 ?(?:篇)?(?: / |of )9,108', r'9,108 篇中的 1,186'],
    'L04': [r'分母效应', r'denominator effects?'],
    'L05': [r'M5 B 部分', r'M5 part B'],
    'L06': [r'64\.5%'],
    'L07': [r'3-3.{0,40}(?:停止|stopped)', r'D14-1'],
    'L08': [r'U28'],
    'L09': [r'数字核对', r'number checker'],
    'L10': [r'2-11'],
    'L11': [r'D（33 篇）', r'D \(33 papers\)', r'D 33 篇'],
    'L12': [r'V5x0', r'C-3b'],
    'L13': [r'Fit B'],
    'L14': [r'事后改动'],
}
REQUIRE = {
    'C01': [('输出层 +0.207', r'0\.207')],
    'C02': [('L48 0.825', r'0\.825'), ('L52 ≈ 1（0.996 / 0.99x）', r'0\.99\d|1\.00')],
    'C04': [('mean5 L48 +0.821', r'0\.821'), ('mean5 为主结果 / five-title mean primary', ALT(r'5 个假标题平均为主结果', r'five-title mean primary', r'makes the five-title mean primary', r'5 个假标题平均为主')),
            ('区间都含 0 / CI includes 0', ALT(r'区间都含 0', r'CI includes 0', r'interval includes 0', r'CIs? includes? 0')),
            ('p9 694–711 篇', r'694–711')],
    'C07': [('D13-1', r'D13-1'), ('前提 ① 首 token 64.5% 是首字母', r'64\.5%'), ('前提 ③ U28', r'U28'),
            ],   # int6 qualifier is checked locally (PAIR) where +0.130 is written
    'C08': [('C 462 篇', r'462'), ('同档 258 篇', r'258'), ('C 分母 0.559', r'0\.559'), ('时间点与 A 相同 / same timing as A', ALT(r'时间点与 A 相同', r'same timing as A')),
            ('D 只作描述', ALT(r'D（33 篇）[^。]{0,20}只作描述', r'D 33 篇[^。]{0,10}只作描述', r'D \(33 papers\) descriptive', r'D 33 / R2-unwritten 28 papers → descriptive', r'D 33 篇按补充 11 只作描述', r'D（33 篇）按补充 11 只作描述', r'\(33\) descriptive'))],
    'C15': [('L8 / L40', r'L40')],
    'C21': [('不再作为 H2 的证据 / no longer H2 evidence', ALT(r'不再作为 H2 的证据', r'no longer counted as H2 evidence', r'X4 recognition gap no longer counted', r'no longer (?:counted|H2)')),
            ('测试集不显著 / test n.s.', ALT(r'测试集(?:上)?不显著', r'not significant\)', r'not significant on the test', r'test.{0,20}n\.s\.', r'测试集 target − control 为 \+0\.023'))],
    'L01': [('没有补层计划 / no plan', ALT(r'没有补层计划', r'no plan to fill', r'补层计划里没有')), ('L33–L40', r'L33–L40')],
    'L02': [('主轮最大差 0.367', r'0\.367'), ('已用到 / was used', ALT(r'只有按 0\.5 才通过', r'用到', r'was (?:actually )?used', r'passes only at 0\.5')),
            ('round d：主轮 25 个中 10 个超出 0.25', ALT(r'有 10 个超出', r'10 of (?:the )?25')), ('round d：事后修改', ALT(r'事后修改', r'post-hoc change'))],
    'L03': [('1,186 / 9,108', r'1,186'), ('9,108', r'9,108')],
    'L04': [('C 0.559 vs A 0.407', r'0\.559'), ('A 0.407', r'0\.407')],
    'L05': [('只用 false_0', ALT(r'只用 false_0', r'false_0 only')), ('没有计划 / no plan', ALT(r'没有(?:补做)?计划', r'no plan'))],
    'L06': [('首字母 / initials', ALT(r'首字母', r'initials?'))],
    'L07': [('D14-1', r'D14-1')],
    'L08': [('原因 / 改动者待查', ALT(r'改动者和依据仍未查清', r'改动人和理由待查', r'原因待查', r'by whom and why', r'unknown', r'未查清'))],
    'L09': [('680', r'680'), ('4,307', r'4,307'), ('约 1,024', r'1,024')],
    'L10': [('0.880 < 0.90', r'0\.880'), ('2-11b', r'2-11b')],
    'L12': [('泄漏 / leak', ALT(r'泄漏', r'leak'))],
}
# (label, trigger, partner, window): partner must be within +-window characters of every trigger
PAIR = [('round e：“约 79%”须带姓的篇数限定（姓的 1,395 篇 / 姓 4,402 / 5,580 / surname set）', ALT(r'约 79% 本应剔除', r'about 79% of false_1\.\.4'), ALT(r'姓的 1,395 篇', r'姓 4,402 / 5,580', r'surname set'), 120),
        ('round e：新句须写“原观察未被重现”', r'补全前（C 组 36 篇）曾观察到 C 略晚', r'原观察未被重现', 260),
        ('round d：L02 的 10 个超出须带 0.367', ALT(r'有 10 个超出', r'10 of (?:the )?25'), r'0\.367', 200),
        ('round d：3-3 99.81% 须注明按 0.25', r'99\.81%', r'0\.25', 120),
        ('B/A false_0 0.78–0.99 须与 5 个假标题版 0.72–0.87 并列', r'0\.78–0\.99', r'0\.72–0\.87', 160),
        ('int6 RQ1 +0.130 须注明 int6 / 6 层（不是锁定的 7 层终点）', r'RQ1 \+0\.130', ALT(r'int6', r'6 层平均', r'6-layer mean', r'6 层'), 220),
        ('L56 RQ2 +0.064 须与 D13-1 / 规则触发同句', r'RQ2 \+0\.064', ALT(r'D13-1', r'触发', r'triggered'), 400),
        ('X4 认得出更高 须带“不再作为 H2 的证据”', ALT(r'认得出的论文(?:第一作者 D )?(?:方向上)?更高', r'X4 中认得出的论文更高'), ALT(r'不再作为 H2 的证据', r'不再作为证据'), 400),]
STALE = [
    ('P1/P2 五个假标题还在运行', ALT(r'P1 ?/ ?P2 ?(?:用 )?(?:五|5) ?个假标题[^。；]{0,12}还在运行', r'P1 / P2 with five false titles still running', r'Batch 1, running', r'批次 1 只剩 P1', r'第 3 项还在运行', r'only P1 / P2 with five false titles still running'), None),
    ('结果经用户确认后补入', ALT(r'结果经用户确认后补入', r'result after approval'), None),
    ('C 只有 32 / 36 篇（作为现状）', ALT(r'C 只有 3[26] 篇', r'C 32 / D 5', r'C 32 篇、D 5 篇、R2', r'C（R1 × 认得出，描述）', r'C  ?R1 × recognised \(descriptive\)'), r'原|只有 C 32 篇、D 5 篇；D 按|original'),
    ('冻结的多层终点 … RQ1 和 RQ2 都成立（无前提）', ALT(r'冻结的多层终点[^。]{0,140}都成立', r'frozen multi-layer (?:endpoint|conclusion)', r'→ both hold', r'RQ2 \+0\.054 multi-layer'), None),
    ('X4 作为 H2 的支持（无“不再作为 H2 的证据”）', ALT(r'L8–L40 (?:高 )?\+0\.04 到 \+0\.06，区间都?不含 0', r'H2[^。]{0,60}(?:支持|support)[^。]{0,60}X4(?:(?!不再|no longer|相反|opposite|不显著|没能|未能|不能|not)[^。]){0,80}。'), None),
    ('C 分母写 0.464（作为现状）', r'(?<![\d.])0\.464(?![\d])', r'原|32 篇时|when C had 32|original|\+0\.464\[|Stage 11 样本 32'),
    ('“5 个假标题平均 +0.076”（E4b 逐个排除版的旧标签）', ALT(r'5 个假标题平均[^。；]{0,20}\+0\.076', r'mean of 5 false titles[^.;]{0,20}\+0\.076'), None),
    ('C 的 E1 表行仍为 32 篇旧值', ALT(r'\+0\.721 \[\+0\.650, \+0\.806\]; n = 32', r'\+0\.996 \[\+0\.968, \+1\.026\]; n = 32'), None),
    ('B/A 只写 false_0 0.78–0.99（无 5 个假标题版）', r'B/A 0\.78–0\.99\)?(?!.{0,6}(?:with|5 个))', r'0\.72–0\.87'),
    ('当前版本标签过时（v29 / v20 作为当前）', ALT(r'当前为? ?(?:第 29 版|v29)', r'当前(?:为)? ?v20', r'current(?:ly)? (?:report )?v29', r'report v29, 2026-11-07', r'v29 prepared', r'v20 prepared', r'当前 v29', r'当前 v20'), None),
    ('批次状态过时（代码已就绪 / 自动开始，未写已在运行）', ALT(r'代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始', r'code ready, after batch 2', r'代码已就绪，第二批之后开始', r'starts automatically after batch 1', r'code ready, queued'), None),
    ('数字核对：第 30 版新数字“尚待登记”（v9 已登记）', ALT(r'尚待登记', r'not yet registered', r'yet to be registered', r'第 30 版新放回或新增的数字（D13-1'), None),
    ('D13-1 段落中的旧版本号', r'报告 v29 和 PPT v20', None),
    ('round f：M2 五个假标题数字未与 false_0 并列', r'(?:R²|year|donor 年份 R²|引用数|log citations|log 引用|citations\|year|领域准确率|field acc|年份 L16|L52) (?:0\.527|0\.507|0\.491|0\.712|0\.341|0\.529)(?![\d])(?!（false_0 版|（5 个假标题| \(false_0)', None),
    ('round f：M2 仍被列为只用 false_0 / 待做', ALT(r'M2 的假标题运行也只用 false_0', r'M2 with five titles needs CPU only', r'M2[^。；]{0,40}只需 CPU', r'M2[^。；]{0,40}是否做待定', r'M2[^.;]{0,40}decision pending'), None),
    ('round f：H2 状态不是“部分支持但未确立”', ALT(r'H2(?:：| )?(?:成立|已确立|得到支持)', r'H2 (?:is )?(?:supported|established)'), r'未确立|not established|不成立|部分支持|预测|predict|若|if'),
    ('round e：“C 略晚 / 略慢”只能出现在新句（补全前（C 组 36 篇）曾观察到 C 略晚 … 原观察未被重现）', ALT(r'略晚', r'略慢', r'slightly later', r'slightly slower'), r'补全前（C 组 36 篇）曾观察到 C 略晚|before completion'),
    ('round e：旧的“补全后未确认”标记', ALT(r'补全后[^。]{0,20}未确认', r'“略晚”[^。]{0,40}(?:未|没有)得到确认', r'C[^。]{0,40}(?:未|没有)得到确认'), r'X4'),
]


def raw_line(path, ctx):
    """1-based line in the raw file where the matched text (or its longest findable prefix) occurs; '' if not found."""
    try:
        raw = Path(path).read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''
    for L in (24, 16, 10, 6):
        k = ctx[:L]
        if len(k) < 4:
            break
        i = raw.find(k)
        if i >= 0:
            return raw[:i].count('\n') + 1
    return ''


U = units()
DOCS = []
for u in U:
    if u[0] not in DOCS:
        DOCS.append(u[0])
by_doc = defaultdict(list)
for u in U:
    by_doc[u[0]].append(u)
rows = []
summ = []
DOCREQ = {   # round d: qualifiers that must now be present in a specific document
    'PPT': [('p9 694–711', r'p9: 694–711'), ('258 of 462', r'258 of 462'), ('6 bins', r'6 bins'), ('L01 consequences L33–L40', r'L33–L40'), ('2-11 0.880 < 0.90', r'0\.880 < 0\.90'),
            ('L02 10 of 25', r'10 of 25 pairs')],
    'PPT 备注 notes_zh.json': [('note 82 没有补做计划', r'没有补做计划'), ('note 82 L33–L40', r'L33–L40'), ('note 82 L02 10 个超出', r'10 个超出'), ('note 82 99.81%', r'99\.81%')],
    '讲稿 progress_report_for_advisor_zh': [('C04 B/A 0.72–0.87', r'0\.72–0\.87'), ('C04 p9 694–711', r'694–711'), ('C08 462', r'462 篇'), ('C08 258', r'258 篇'),
                                            ('C08 D 只作描述', r'D 33 篇按补充 11 只作描述'), ('2-11 0.880', r'0\.880')],
    'README 草稿 b': [('X4 test L8 +0.023 [−0.001, +0.048] not significant', r'test set L8 \+0\.023 \[−0\.001, \+0\.048\], not significant')],
    '导师页 advisor': [('PPT 当前为 v21', r'当前为 v21')],
}
H2RX = ALT(r'H2 部分支持', r'H2 partly supported', r'H2[：:] ?部分支持', r'H2 partially supported')
H2OK = ALT(r'部分支持但未确立', r'partly supported but not established', r'partially supported but not established')
SKIP = {'计划 b'}          # plan document of 2026-11-06 b: not part of the v30 document set
for doc in DOCS:
    if doc in SKIP:
        continue
    us = by_doc[doc]
    full = '\n'.join(u[3] for u in us)
    stated = [k for k, rx in DETECT.items() if any(re.search(r, full) for r in rx)]
    miss = []
    for k in stated:
        for lab, rx in REQUIRE.get(k, []):
            if not re.search(rx, full):
                miss.append((k, lab))
                rows.append(dict(doc=doc, kind='missing qualifier', item=k, label=lab, location='(whole document)', line='', text=''))
    for lab, rx in DOCREQ.get(doc, []):
        if not re.search(rx, full):
            miss.append(('round d', lab))
            rows.append(dict(doc=doc, kind='missing qualifier', item='round d', label=lab, location='(whole document)', line='', text=''))
    for u in us:
        for m in re.finditer(H2RX, u[3]):
            if not re.match(r'.{0,30}?' + H2OK, u[3][m.start():m.start() + 80]):
                miss.append(('round f', 'H2 状态须为“部分支持但未确立”'))
                rows.append(dict(doc=doc, kind='missing qualifier (local)', item='H2', label='H2 状态须为“部分支持但未确立”', location=locate(u, m.start()),
                                 line=raw_line(u[1], u[3][m.start():m.start() + 30]) if u[2] == '' else u[2], text=u[3][max(0, m.start() - 60):m.end() + 100]))
    local = []
    for lab, trig, partner, win in PAIR:
        for u in us:
            t = u[3]
            for m in re.finditer(trig, t):
                if not re.search(partner, t[max(0, m.start() - win):m.end() + win]):
                    local.append(lab)
                    rows.append(dict(doc=doc, kind='missing qualifier (local)', item='', label=lab, location=locate(u, m.start()), line=raw_line(u[1], t[m.start():m.start() + 30]) if u[2] == '' else u[2],
                                     text=t[max(0, m.start() - 80):m.end() + 80]))
    stale = []
    for lab, rx, allow in STALE:
        for u in us:
            t = u[3]
            for m in re.finditer(rx, t):
                if allow and re.search(allow, t[max(0, m.start() - 160):m.end() + 80]):
                    continue
                stale.append(lab)
                rows.append(dict(doc=doc, kind='stale phrase', item='', label=lab, location=locate(u, m.start()),
                                 line=(raw_line(u[1], t[m.start():m.start() + 30]) if u[2] == '' else u[2]), text=t[max(0, m.start() - 80):m.end() + 80]))
    ok = [k for k in stated if not any(x[0] == k for x in miss)]
    summ.append(dict(doc=doc, stated=len(stated), consistent=len(ok), stated_ids=' '.join(stated),
                     missing=' ; '.join('%s: %s' % x for x in miss), local_missing=len(local), stale=len(stale)))
with open(OUT / 'wording_v30_rows.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, ['doc', 'kind', 'item', 'label', 'location', 'line', 'text']); w.writeheader(); w.writerows(rows)
with open(OUT / 'wording_v30_by_doc.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, list(summ[0].keys())); w.writeheader(); w.writerows(summ)
lines = ['%s | stated %d, consistent %d | local-missing %d | stale %d | missing: %s' % (s['doc'], s['stated'], s['consistent'], s['local_missing'], s['stale'], s['missing'] or '—') for s in summ]
lines += ['', 'findings:'] + ['%s | %s | %s %s | %s | line %s | %s' % (r['doc'], r['kind'], r['item'], r['label'], r['location'][:60], r['line'], re.sub(r'\s+', ' ', r['text'])[:200]) for r in rows if r['kind'] != 'missing qualifier']
(OUT / 'wording_v30_summary.txt').write_text('\n'.join(lines), encoding='utf-8')
print('\n'.join(lines))
print('out', OUT)
