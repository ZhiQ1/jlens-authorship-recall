"""claims_defs v21 (2026-11-15 c24): v20 (unchanged file) + the C24 option-B numbers (post-hoc generation-time confidence check, C24
downgraded to undecided (exploratory), user-approved 2026-11-15) written into report / handbook / advisor / Stage 13 script / talk pages /
process report / deck: confidence baseline, mean log-prob alone, combined (= corrected 2026-11-14 baseline), combined + confidence,
probe − (combined + confidence) at the 7 layers, regeneration identity and replay |Δ| median.
Sources: 381_stage13/summary_c24_optB_20261114/c24_optB_table.csv (= report.md table; layer-independent baselines read at layer 48)
and c24_optB_regen.json. New ids 'A21-'.  Run with:  CLAIMS_DEFS=claims_defs_v21 bash claims_run.sh"""
from claims_defs_v20 import *          # noqa: F401,F403
from claims_defs_v20 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, jsn


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A21-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
TB = '381_stage13/summary_c24_optB_20261114/c24_optB_table.csv'
RG = '381_stage13/summary_c24_optB_20261114/c24_optB_regen.json'
CP = 'C24 选项 B（事后，探索性）：生成时置信度，target 论文论文内 AUROC，518 篇 / 3,388 对，团队整群 bootstrap 2,000 次；'


def T(cid, stmt, col, layer, labs, sign):
    A(cid, stmt, csv(TB, col, layer=layer), CP, '518 / 3,388', 3, [l + '#(?= \\[)' for l in labs], sign=sign)
    A(cid + '-lo', stmt + '（下限）', csv(TB, col + '_lo', layer=layer), CP, '518 / 3,388', 3, [l + NUM + r' \[#' for l in labs], sign=sign)
    A(cid + '-hi', stmt + '（上限）', csv(TB, col + '_hi', layer=layer), CP, '518 / 3,388', 3, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=sign)


# layer-independent baselines (same value at every layer): read at L48
T('c24b-conf3', 'C24 置信度基线（名字平均对数概率、首 token 对数概率、−熵三项拟合）', 'conf3', 48,
  [r'三项拟合）AUROC ', r'−entropy\) ', r'置信度基线 '], sign=False)
A('c24b-conf3-pt', 'C24 置信度基线 AUROC（不带区间）', csv(TB, 'conf3', layer=48), CP, '518 / 3,388', 3,
  [r'置信度基线 AUROC #', r'baseline AUROC #', r'输出置信度解释（基线 #', r'output confidence \(baseline #'], sign=False)
T('c24b-lpm', 'C24 只用名字平均对数概率', 'conf_lp_mean', 48, [r'只用平均对数概率 ', r'mean log-prob alone '], sign=False)
T('c24b-comb', 'C24 合并基线（排位 + 名字特征 + 名气，频率排除本论文）', 'comb_new', 48,
  [r'合并基线（排位 \+ 名字特征 \+ 名气）', r'、合并基线 ', r'combined \(position \+ name features \+ fame\) ', r'name features 0\.\d+ \[[^\]]*\], combined '], sign=False)
T('c24b-cc', 'C24 合并 + 置信度', 'comb_conf', 48, [r'合并 \+ 置信度 ', r'combined \+ confidence '], sign=False)

# probe − (combined + confidence), 7 layers (lists "L16 … L24 … L56" after the label)
HEAD = r'(?:probe −（合并 \+ 置信度）：|[Pp]robe − \(combined \+ confidence\): )'
PREV = r'(?:L\d\d ' + NUM + r' \[' + NUM + ', ' + NUM + r'\](?:、|, ))*'
for L in (16, 24, 32, 40, 48, 52, 56):
    labs = [HEAD + PREV + 'L%d ' % L]
    if L == 48:
        labs += [r'L48：', r'L48: ', r'L40–L52（L48 ', r'L40–L52 \(L48 ']
    T('c24b-pmcc%d' % L, 'C24 probe −（合并 + 置信度）L%d' % L, 'probe_minus_comb_conf', L, labs, sign=True)

# regeneration identity and replay difference
A('c24b-regen-pap', 'C24 重新生成逐字相同的论文数', jsn(RG, ['regen', 'papers_identical']), '计数', '—', 0,
  [r'逐字相同（#(?= / )', r'identical (?:to the stored text )?\(#(?= / )', r'identical #(?=/)'], sign=False)
A('c24b-regen-tok', 'C24 重新生成逐字相同的 token 数', jsn(RG, ['regen', 'positions_common_prefix']), '计数', '—', 0,
  [r'篇，#(?= 个 token)', r'papers, #(?= tokens)'], sign=False)
A('c24b-dlp-med', 'C24 重放与生成时名字平均对数概率之差 |Δ| 中位数', jsn(RG, ['regen', 'd_lp_mean_median']), '中位数', '31,561 个名字', 4,
  [r'中位数 #(?=（> 0\.01）)', r'median \|Δ\| #'], sign=False)
