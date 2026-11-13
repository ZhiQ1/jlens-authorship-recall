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
import claims_defs_v17 as D17        # noqa: F401  (v9 patches claims_docs.doc_list: + process_report/draft_zh.md)
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
    'L10': [r'2-11(?!b)'],
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
    'C15': [('L8 / L40', r'L40'), ('round o：C15 补“全作者版本同样从 L8 起可解码（测试集 +0.048 [0.039, 0.058]）”', ALT(r'全作者版本同样从 L8 起可解码', r'all-author version (?:is )?also (?:decodable )?from L8', r'all authors also from L8'))],
    'C21': [('不再作为 H2 的证据 / no longer H2 evidence', ALT(r'不再作为 H2 的证据', r'no longer counted as H2 evidence', r'X4 recognition gap no longer counted', r'no longer (?:counted|H2)')),
            ('测试集不显著 / test n.s.', ALT(r'测试集(?:上)?不显著', r'not significant\)', r'not significant on the test', r'test.{0,20}n\.s\.', r'测试集 target − control 为 \+0\.023'))],
    'L01': [('没有补层计划 / no plan', ALT(r'没有补层计划', r'no plan to fill', r'补层计划里没有')), ('L33–L40', r'L33–L40'),
            ('round i：L41–L47、L49 已由 3-1 补齐', ALT(r'3-1 已补 L41–L47、L49', r'L41–L47、L49 已由 3-1 补齐', r'L41–L47, L49 filled by 3-1', r'3-1 Stage 10 补 L41–L47、L49：已完成')),
            ('round i：L0–L23 运行中（3-2）', ALT(r'3-2 补 L0–L23，运行中', r'3-2 补 L0–L23：运行中', r'L0–L23:? running', r'3-2[^。；]{0,20}运行中'))],
    'C16': [('round i：C16 前提（2-2 对半拆分）', ALT(r'F1 对半拆分', r'对半拆分', r'split-half', r'2-2 已完成'))],
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
C24T = ALT(r'Qwen3-32B 自己写作者名单时', r'when Qwen3-32B writes the author list itself')
PST = ALT(r'Patchscope（批次 2 第 2-7、2-9 项，补充 12；只作描述）：', r'Patchscope \(2-7, 2-9; descriptive only\):', r'用名字位置作源时，第一作者')
LIM1T = ALT(r'仍为首 token / 第一作者的分析', r'Analyses still on the first token')
B2STAT_ = ALT(r'批次 1 结束后已由编排作业开始运行', r'Batch 2 \(addenda 11, 12\): running', r'Batch 2 \(addenda 11–12\): running', r'批次 2（补充 11、12[^）]*）已开始', r'running \(C / D done')
PAIR = [('round n：“仍为首 token / 第一作者”须列 Stage 4–8 / W', LIM1T, r'Stage 4–8（含 Stage 8 的 W）|Stages? 4–8', 900),
        ('round n：“仍为首 token / 第一作者”须列 X4 / x4tok / 2-7', LIM1T, r'X4 认得出对比、x4tok、2-7|X4[^.;]{0,30}x4tok[^.;]{0,20}2-7', 900),
        ('round n：“仍为首 token / 第一作者”须列 Stage 11 E4', LIM1T, r'Stage 11 E4 lens|Stage 11 E4', 900),
        ('round n：“仍为首 token / 第一作者”须列 E4b X1 对照流程', LIM1T, r'E4b 的 X1 对照流程|X1-controls pipeline|X1 control pipeline', 900),
        ('round n：“仍为首 token / 第一作者”须列 理由：存储的数据只有首 token', LIM1T, r'存储的数据只有|stored data hold only|only the first-token', 900),
        ('round n：“仍为首 token / 第一作者”须列 理由：提示按设计问第一作者', LIM1T, r'按设计问第一作者|by design', 900),
        ('round n：“仍为首 token / 第一作者”须列 理由：E4 需要 GPU', LIM1T, r'全部 token 需要 GPU|need[s]? GPU', 900),
        ('round l：C24 须带“补充 15 预注册”', C24T, ALT(r'补充 15 预注册', r'addendum 15'), 400),
        ('round l：C24 须带“名字写出之后”', C24T, ALT(r'名字写出之后', r'on the written name tokens'), 200),
        ('round l：C24 须带“写出之前…读不出”', C24T, ALT(r'名字写出之前的位置读不出', r'positions before the name is written do not'), 900),
        ('round l：C24 须带“输出置信度 … 尚未排除”', C24T, ALT(r'输出置信度”这一替代解释尚未排除', r'output confidence not yet excluded'), 1500),
        ('round l：C24 名气基线须标“事后，探索性”', C24T, ALT(r'事后，探索性', r'post-hoc fame baseline \(exploratory\)'), 1800),
        ('round l：C24 须带“与 H3 的关系未预注册”', C24T, ALT(r'与 H3 的关系未预注册', r'no relation to H3', r'not H3 evidence'), 2200),
        ('round l：Patchscope 须标“预注册要求报告、无判定规则”', PST, ALT(r'预注册要求报告、无判定规则', r'pre-registered to report, no decision rule'), 900),
        ('round l：Patchscope 须标“探索性”', PST, ALT(r'探索性', r'exploratory'), 900),
        ('round l：Patchscope 须写“不据此讨论 H3”', PST, ALT(r'不据此讨论 H3', r'no H3 argument', r'not used for H3'), 1000),
        ('round i：批次 2 状态须写 2-2 已完成', B2STAT_, ALT(r'2-2）已完成', r'2-2 已完成', r'2-2, 2-3', r'名字位置 probe、2-2 已完成', r'2-2：已完成'), 900),
        ('round i：批次 2 状态须写 2-1 停止（D12-1）', B2STAT_, ALT(r'2-1 停止（D12-1', r'2-1 stopped \(D12-1'), 900),
        ('round l：批次 2 状态须写 Patchscope 已完成、只作描述', B2STAT_, ALT(r'Patchscope（2-7、2-9）已完成，只作描述', r'Patchscope 已完成（只作描述）', r'Patchscope 已完成（描述）', r'Patchscope \(2-7, 2-9\) done \(descriptive only\)', r'2-7/2-9'), 900),
        ('round l：批次 2 状态须写 2-11b 已完成（C24）', B2STAT_, ALT(r'预注册判定在 7 层都成立（见 C24）', r'pre-registered verdict passes at all 7 layers \(C24\)'), 900),
        ('round h：H3 判词须带“lens 的区间同样不含 0”', ALT(r'按补充 11 预注册判据', r'By the addendum-11 pre-registered criterion'), ALT(r'lens 的区间同样不含 0', r'lens intervals also exclude 0'), 500),
        ('round h：H3 判词须带“尺度不同”', ALT(r'按补充 11 预注册判据', r'By the addendum-11 pre-registered criterion'), ALT(r'尺度不同', r'scales differ'), 600),
        ('round h：H3 判词须写后续 token 在 L40 对 J-lens 不满足判据', ALT(r'按补充 11 预注册判据', r'By the addendum-11 pre-registered criterion'), ALT(r'后续 token 在 L40 与 J-lens 比较时不满足判据', r'continuation tokens do not meet the criterion at L40 against the J-lens'), 700),
        ('round h：首字母须写“约一半信号不是论文特有的”', ALT(r'首字母的对照行', r'For initials the control row'), ALT(r'约一半信号不是论文特有的', r'about half of it is not paper-specific'), 200),
        ('round h：同档 T − C 须标“预注册要求报告、无判定规则”', r'只作描述：同一引用档内 target − control', r'预注册要求报告、无判定规则', 60),
        ('round h：行为分组须标“预注册要求报告、无判定规则”', r'按行为分组，A − B', r'预注册要求报告、无判定规则', 120),
        ('round h：lens T − C 须标“探索性”', r'(?<!J-)lens 的 target − control', r'探索性', 30),
        ('round h：逐层峰值须标“探索性”', r'逐层峰值和逐层上升', r'探索性', 30),
        ('round g：E1t 探索性句须带“探索性”', r'恢复比例 target − control 为负', r'探索性', 200),
        ('round g：E1t 探索性句须带“分母效应”', r'恢复比例 target − control 为负', r'分母效应', 200),
        ('round g：M3 全部 token（U46）须带“不作为 H2 证据”', r'\+0\.234 \[\+0\.215', ALT(r'不作为 H2 证据', r'not H2 evidence', r'not counted as H2 evidence'), 600),
        ('round g：M3 全部 token（U46）须带“C06 不变”', r'\+0\.234 \[\+0\.215', ALT(r'C06 不变', r'C06 unchanged'), 600),
        ('round e：“约 79%”须带姓的篇数限定（姓的 1,395 篇 / 姓 4,402 / 5,580 / surname set）', ALT(r'约 79% 本应剔除', r'about 79% of false_1\.\.4'), ALT(r'姓的 1,395 篇', r'姓 4,402 / 5,580', r'surname set'), 120),
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
    ('round o：“全作者版本…未做调参/测试拆分”接在可解码性上', r'(?:可解码|decodab)[^。.]{0,80}(?:没有做|未做|no) ?调参 ?/ ?测试拆分|(?:全作者|全部作者|all-author)版本[^。]{0,40}(?:没有做|未做)调参 ?/ ?测试拆分[^。]{0,60}可解码', r'认得出|recogni'),
    ('round o：标题位置 T − C 主数字仍为旧版 +0.03 到 +0.08（不在“旧版”括号内）', ALT(r'目标组比对照组高 \+0\.03 到 \+0\.08', r'target 比 control 高 \+0\.03 到 \+0\.08', r'target exceeds control by \+0\.03 to \+0\.08'), r'旧版|old first-token'),
    ('round n：标题位置 probe 首 token 旧值作为主数字（不在“旧版”括号内）', ALT(r'\+0\.050 / \+0\.061 / \+0\.075', r'L24 \+0\.050[，、] ?L40 \+0\.061', r'L40 (?:为 )?\+0\.061 \[0\.047, 0\.076\]', r'L24 约 \+?0\.05，L40 约 \+?0\.06', r'about \+0\.05 at L24'),
     r'旧版|old first-token|1,863|X1 对照流程|X1-controls|原 E4b|原版|硬检查|一致性检查|复现已发表|hard check|e4b_parity|V0（1,395 篇）\+0\.061'),
    ('round n：X1 主 R 仍为第一作者旧值', ALT(r'R ≈ 0\.99 \(L24\)', r'L24 约 0\.99，L40 约 0\.92', r'L24 约 0\.99、L40 0\.92', r'R 0\.99 at L24'), r'旧版|old first-author|原 X1'),
    ('round n：X3 主数字仍为第一作者旧值', ALT(r'保留约 90% 的第一作者偏好', r'≈ 90% of the first-author preference', r'恢复比例 0\.90 \[0\.86, 0\.94\]，测试集'), r'旧版|old first-author'),
    ('round n：M3 主数字仍为第一作者首 token', ALT(r'(?<!旧版只看)第一作者首 token \+0\.147', r'(?<!old )first-author first token \+0\.147'), r'旧版|old first-author'),
    ('round l：旧状态“2-11b 结论待定 / Patchscope 结果待写入”', ALT(r'已完成，结论待定', r'结果待写入', r'conclusion pending', r'results to be written'), None),
    ('round l：C24 被当作 H3 证据或写进假设判定', ALT(r'C24[^。；]{0,60}(?:支持 H3|H3 的证据(?!；)|supports H3|H3 evidence(?! \(discussion))', r'H3[^。；]{0,40}(?:由|依据|rests on)[^。；]{0,20}C24'), r'不作为|not H3 evidence|未预注册|no relation'),
    ('round l：Patchscope 被用来论证 H3', r'Patchscope[^。]{0,200}(?:支持 H3|H3 (?:成立|部分支持)|supports H3)', r'不据此讨论 H3|不讨论 H3|no H3'),
    ('round k：D14-1 引文“通过率 99.81%”后缺 2026-11-12 更正', r'通过率 99\.81%(?![^。〕]{0,6}〔?更正)(?!。〔更正)', None),
    ('round i：2-2 / F1 对半拆分仍写进行中', ALT(r'2-2(?:（[^）]*）)?[^。；，,]{0,12}(?:进行中|运行中|running|queued)', r'F1 对半拆分[^。；]{0,12}(?:进行中|排队)', r'对半拆分 2-2 进行中'), r'已完成|done'),
    ('round i：L41–L47、L49 仍写排队 / 未补', ALT(r'补充 14 只补 L41–L47、L49 和 L0–L23', r'L41–L47、L49 由 3-1 补，排队中', r'L41–L47, L49[^.;]{0,30}queued', r'3-1[^。；]{0,30}(?:排队|编排作业已提交)', r'也没有 L41–L47'), None),
    # round i rule 'Patchscope / 2-11b 写出了结果数字' retired in round l (C24 and the Patchscope table are now written by design)
    ('round i：2-1 仍写重跑 / 运行中', ALT(r'2-1[^。；，]{0,12}(?:门槛重跑|gate re-run|进行中|运行中)', r'Fit B[^。；]{0,12}(?:已在运行|重跑中)'), r'停止|stopped'),
    ('round h：H3 总体判断仍写“证据不足”', ALT(r'H3 ?(?:仍|仍然)?证据(?:仍)?不足', r'H3[：:] ?(?:X\d[^。；]{0,60})?证据(?:仍)?不足', r'H3 (?:has |had )?insufficient evidence', r'H3[:：] insufficient', r'H3 (?:still )?insufficient', r'H3 \(hidden author knowledge\)[:：]? insufficient'),
     r'单看 X[24]|X[24] alone|原为|此前|had insufficient|改为部分支持|H3 部分支持|now partly supported|H3 partly supported|partly supported by the name-position|11-03|V57|措辞记录|历史'),
    ('round h：重复从句', ALT(r'(单看 X\d，)\1', r'(X\d alone[,:] )\2', r'单看 X2，单看 X2'), None),
    ('round g：+0.0215 不是 L40 的标注', r'(?<!L40 )\+0\.0215', None),
    ('round g：X3 “不能按角色拆分”仍作为未解决局限', ALT(r'无法按角色拆分', r'按 token 角色报告做不到', r'cannot be (?:split|reported) by (?:token )?role', r'X3 按 token 角色（V51）尚未'), r'已由补充 12|已完成|2026-11-09|done in addendum 12|已用批次 1'),
    ('round g：2-3 / 2-4 / 2-8 / 2-10 仍写进行中', r'(?:2-3|2-4|2-8|2-10)(?:（[^）]*）)?[^。；，,]{0,12}(?:进行中|运行中|running|queued|排队)', r'已完成|done'),
    ('round g：旧的批次 2 状态句', ALT(r'名字位置 probe 等其余各项进行中，没有可报告的结果', r'只跑第 0 个分片，排队中', r'shard 0 only, queued', r'2-11b shard 0 queued'), None),
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
SKIP = {'计划 b'}
H3PART = ALT(r'H3 部分支持', r'H3 partly supported', r'H3 \(hidden author knowledge\)[:：]? partly supported', r'H3 改为部分支持', r'H3[：:] ?partly supported')
B2DONE = ALT(r'2-3、2-4、2-8、2-10 已完成', r'X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成', r'2-3, 2-4, 2-8, 2-10 done', r'2-3[,、] 2-4[,、] 2-5[^;；]{0,60}?2-8[,、] 2-10 (?:done|已完成)')
B2STAT = ALT(r'批次 1 结束后已由编排作业开始运行', r'Batch 2 \(addenda 11, 12\): running', r'Batch 2 \(addenda 11–12\): running', r'批次 2（补充 11、12[^）]*）已开始', r'running \(C / D done')          # plan document of 2026-11-06 b: not part of the v30 document set
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
    for u in us:
        for m in re.finditer(B2STAT, u[3]):
            if not re.search(B2DONE, u[3][m.start():m.end() + 700]):
                miss.append(('round g', '批次 2 状态须列 2-3/2-4/2-8/2-10 已完成'))
                rows.append(dict(doc=doc, kind='missing qualifier (local)', item='B2', label='批次 2 状态须列 2-3/2-4/2-8/2-10 已完成', location=locate(u, m.start()),
                                 line=raw_line(u[1], u[3][m.start():m.start() + 30]) if u[2] == '' else u[2], text=u[3][m.start():m.end() + 300]))
    if re.search(H3PART, full):
        for lab, rx in [('round h：H3 部分支持须带“按补充 11 预注册判据”', ALT(r'按补充 11 预注册判据', r'addendum-11 pre-registered criterion', r'criterion met for the surname', r'meets the pre-registered criterion', r'按补充 11 判据', r'meets the addendum-11 criterion', r'L40/L48 按判据满足')),
                        ('round h：H3 部分支持须带“lens 的区间同样不含 0”', ALT(r'lens 的区间同样不含 0', r'lens intervals also exclude 0', r'lens 区间也不含 0')),
                        ('round h：H3 部分支持须带“尺度不同”', ALT(r'尺度不同', r'scales differ', r'scales cannot be compared'))]:
            if not re.search(rx, full):
                miss.append(('round h', lab)); rows.append(dict(doc=doc, kind='missing qualifier', item='H3', label=lab, location='(whole document)', line='', text=''))
    for u in us:
        if u[0].startswith('PPT') and u[2].startswith('第24页'):
            for m in re.finditer(ALT(r'first author', r'第一作者', r'只给每位作者名字的第一个 token 打分'), u[3]):
                rows.append(dict(doc=doc, kind='stale phrase', item='24', label='round n：第 24 页 / 备注 24 的 E4b 仍写第一作者 / 只打首 token', location=u[2], line=u[2], text=u[3][max(0, m.start() - 80):m.end() + 80]))
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
