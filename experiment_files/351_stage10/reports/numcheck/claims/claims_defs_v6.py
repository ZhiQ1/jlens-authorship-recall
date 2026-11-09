"""claims_defs v6 (2026-11-07 ~21:00): v5 (unchanged file) + the user's decision of 2026-11-07 20:40 on the E4b / X1 / X4 numbers.
New ids start with 'A6-'. Earlier claims are re-labelled IN MEMORY only (claims_defs*.py v1-v5 are not edited):
  E4b-ts-*      : n = target + control 1,395 (not 1,863)
  E4b-ts-rmax   : alternative = orig standardisation with corrected labels (L56 0.0755), not the mislabelled 0.0802
  E4b-all-L24/40/56 : these are the X1-controls pipeline "ordinary probe" on all 1,863 retained papers
  A5-E4b-tsmax  : corrected max |new - orig| over 36 cells = 0.0007 (trainstd_orig_corrected_fix.py logic), not 0.0075
  A5-X4rec-*    : source = original X4 report table (summary_x1x4/x4_recognition.csv), all 1,178 pairs
Claims listed in FAR_IS_MISMATCH: a pattern hit that is farther than 25 % from the source (e.g. "1,863" where the source is 1,395, or
"0.0075" where the source is 0.0007) is a mismatch, not an unrelated number; claims_v5_post.py moves those hits into the change list.
Run with:  CLAIMS_DEFS=claims_defs_v6 bash claims_run.sh ;  then  CLAIMS_DEFS=claims_defs_v6 python claims_v5_post.py <out_dir>"""
import functools
import numpy as np
import pandas as pd
from claims_defs_v5 import *          # noqa: F401,F403
from claims_defs_v5 import C, add, csv, md, JL, A as _A5, tri as _tri5, py, SCOPE_SLIDES, BOUNDS, MANUAL, DEF_VPD, PDL

FIX = '381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py'
P0F = '381_stage13/summary_cpu_group/perpaper_probe_spec.parquet'
PPF = '381_stage13/summary_cpu_trainstd/perpaper_probe_spec.parquet'
META = '351_stage10/cohort/papers.parquet'
FILES = [P0F, PPF, META, FIX]
LAYERS = [16, 24, 32, 40, 44, 48, 52, 56, 60]


@functools.lru_cache(None)
def _fix():
    """Same computation as trainstd_orig_corrected_fix.py (means only, no bootstrap): orig = full-sample standardisation with the
    corrected E4b labels (first row per paper & config, target + control only); new = training-fold standardisation (source == 'E4b')."""
    P0 = pd.read_parquet(JL / P0F); PP = pd.read_parquet(JL / PPF)
    meta = pd.read_parquet(JL / META, columns=['paper_id', 'group_tight']).set_index('paper_id')
    P0['g'] = P0.paper_id.map(meta.group_tight)
    cc = P0.groupby(['split', 'excl', 'layer', 'control', 'paper_id']).cumcount()
    P0['buggy'] = np.where(cc == 0, 'E4b', 'X1'); P0.loc[P0.control != 'probe (as in Stage 11)', 'buggy'] = 'X1'
    P0['fixed'] = np.where((P0.buggy == 'E4b') & P0.g.isin(['target', 'control']), 'E4b', 'X1')

    def ap(P, src, l, s, e):
        g = P[(P[src] == 'E4b') & (P.split == s) & (P.excl == e) & (P.layer == l)]
        v = g.spec.to_numpy(float); keep = ~np.isnan(v) & ~(g.dropped.to_numpy() & (e == 'title-reuse'))
        return float(v[keep].mean()), int(keep.sum())
    rows = []
    for s in ('group', 'paper'):
        for e in ('none', 'title-reuse'):
            for l in LAYERS:
                o, no = ap(P0, 'fixed', l, s, e); n, nn = ap(PP, 'source', l, s, e)
                rows.append(dict(s=s, e=e, l=l, orig=o, new=n, diff=round(n, 4) - round(o, 4), n_o=no, n_n=nn))
    return pd.DataFrame(rows)


def F(fn, desc):
    return py(fn, desc + '（按 ' + FIX + ' 的计算，只算均值）', FILES)


def cell(col, l, s='group', e='title-reuse'):
    def f():
        d = _fix()
        return float(d[(d.s == s) & (d.e == e) & (d.l == l)][col].iloc[0])
    return f


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A6-' + cid; MANUAL[-1] = c['id']
COMP_TS = 'E4b 第一个名字 token probe，团队分折 + 剔除标题复用 + 训练折内标准化；目标 + 对照（剔除后 1,395 篇）'

# 1. E4b first-token probe L24/L40/L56 and its paper count (1,395); "1,863" next to these values is a mismatch
for L in (24, 40, 56):
    A('E4b-ts-L%d' % L, 'E4b（训练折标准化）全部论文标题特异信号 L%d' % L, F(cell('new', L), 'new 列 group/title-reuse L%d' % L),
      COMP_TS, '1,395 篇', 3, [], note='值同 E4b-ts-*；只登记，出现处由 v2 的 E4b-ts-* / E4b-s1-* 检查')
A('E4b-ts-n', 'E4b（训练折标准化）L40 计入的论文数', F(cell('n_n', 40), 'new 计入篇数 group/title-reuse L40'), '计数：target + control，剔除标题复用后', '—', 0,
  [r'全部 #(?= 篇；论文 bootstrap 95% CI；381_stage13/reports/e4b_trainstd_compare\.md)',
   r'all #(?= papers; paper bootstrap 95% CI; 381_stage13/reports/e4b_trainstd_compare)',
   r'全部 #(?= 篇，L24–L60；381_stage13/reports/e4b_trainstd)', r'all #(?= papers, L24–L60; 381_stage13/reports/e4b_trainstd)',
   r'按团队分折并剔除标题复用（#(?= 篇），论文 bootstrap 95% CI；381_stage13/reports/e4b_trainstd)',
   r'训练折内标准化，全部 #(?= 篇)'], sign=False,
  note='用户决定 2026-11-07 20:40：E4b 训练折标准化值 +0.050/+0.061/+0.075 的样本是目标 + 对照 1,395 篇；与这些值并列写“全部 1,863 篇”为不一致')
# 4. report p91 range L16-L60 (new column, 1,395)
A('E4b-ts-r16min', 'E4b（训练折标准化）L16–L60 最小', F(lambda: float(_fix().query("s=='group' and e=='title-reuse'").new.min()), 'new 列 group/title-reuse L16–L60 取最小'),
  COMP_TS, '1,395 篇', 3, [r'L16–L60 #(?= 到 \+0\.0[78]\d)'])
A('E4b-ts-r16max', 'E4b（训练折标准化）L16–L60 最大', F(lambda: float(_fix().query("s=='group' and e=='title-reuse'").new.max()), 'new 列 group/title-reuse L16–L60 取最大'),
  COMP_TS, '1,395 篇', 3, [r'L16–L60 \+0\.042 到 #'], note='报告 p91 写 +0.080（全样本标准化 / X1 管线的 L56），训练折标准化 1,395 篇为 +0.075')
# 3. standardisation difference, corrected
A('std-maxdiff', 'E4b 训练折标准化 vs 全样本标准化（修正标签后）36 格最大 |new − orig|', F(lambda: float(_fix()['diff'].abs().max()), '36 格 diff 取 |·| 最大'),
  'round(new,4) − round(orig,4)，split × excl × 9 层', '36 格', 4,
  [r'(?<![\d.])(?<!−)(?<!\[)(?P<v>0\.0075)(?!\d)'], sign=False,
  note='用户决定 2026-11-07 20:40：e4b_trainstd_compare.md 的 0.0075 来自标签错误（把 X1 管线行当成 E4b）；修正后为 0.0007')
A('std-maxdiff-3L', '同上，只看 L24/L40/L56', F(lambda: float(_fix().query('l in [24, 40, 56]')['diff'].abs().max()), 'L24/L40/L56 的 diff 取 |·| 最大'), '同上', '12 格', 4, [], sign=False)
# 2. X1 controls pipeline "ordinary probe" on 1,863 papers (the old E4b-all-* claims, re-labelled)
byid = {c['id']: c for c in C}
for L in (24, 40, 56):
    c = byid['E4b-all-L%d' % L]
    c['stmt'] = 'X1 对照管线“普通 probe”（probe (as in Stage 11)），全部保留的 1,863 篇，L%d（全样本标准化）' % L
    c['comp'] = 'e4b_split_compare.md “Controls” 表 group / dropped 列（stage12_cpu.probe_controls 输出）；不是 E4b 的 1,395 篇训练折标准化值'
    c['n'] = '1,863 篇（含 excluded 433、guard 35）'
    c['note'] = '用户决定 2026-11-07 20:40：+0.050/+0.066/+0.080 是 X1 对照管线普通 probe（1,863 篇）；E4b（1,395 篇，训练折标准化）为 +0.050/+0.061/+0.075'
for cid in [k for k in byid if k.startswith('E4b-ts-') or k.startswith('E4b-s1-')]:
    byid[cid]['n'] = '目标 + 对照 1,395 篇（剔除标题复用后；不是 1,863）'
byid['E4b-ts-rmax']['alt'] = [('修正标签后的 orig（全样本标准化，1,395 篇）L24–L60 最大 = L56 0.0755',
                               F(lambda: float(_fix().query("s=='group' and e=='title-reuse' and l>=24").orig.max()), 'orig_fixed 列 L24–L60 取最大'), '不一致')]
byid['E4b-ts-rmax']['note'] = '+0.080 / 0.0802 是 X1 管线（1,863 篇）的值；E4b 修正标签后全样本标准化为 0.0755，训练折标准化为 0.0753'
t = byid['A5-E4b-tsmax']
t['sel'] = F(lambda: float(_fix()['diff'].abs().max()), '36 格 diff 取 |·| 最大'); t['dec'] = 4
t['stmt'] = 'E4b 标准化新旧最大变化（修正标签后，36 格）'; t['note'] = '0.0075 来自标签错误；修正后 0.0007'
# 5. Vpd first token: label "原 E4b" (flagged in post); original E4b = V0 e4b_parity L40 on 1,395
A('E4b-V0-L40', '原 E4b（V0，false_0，1,395 篇）L40', csv(PDL, 'spec', run='e4b_parity', layer=40, version='V0'), '真标题 − false_0，false_0 剔除规则', '1,395 篇', 3, [])
# 6. X4 recognition: original X4 report table (all 1,178 pairs, first author) and v42 test value
X4R = '381_stage13/summary_x1x4/x4_recognition.csv'
for cid in ('A5-X4rec-first-min', 'A5-X4rec-first-max'):
    agg = 'min' if cid.endswith('min') else 'max'
    byid[cid]['sel'] = csv(X4R, 'target_minus_control', agg, answer='author', pos='title', layer=[8, 16, 24, 32, 40])
    byid[cid]['stmt'] = 'X4 识别（target − control，第一作者，x4_report.md Recognition 表，全部 1,178 对）L8–L40 ' + ('最小' if agg == 'min' else '最大')
A('X4rec-rep-first-min3', '同上 3 位写法最小', csv(X4R, 'target_minus_control', 'min', answer='author', pos='title', layer=[8, 16, 24, 32, 40]), '同上', '1,178 对', 3, [])

t['occ'] = []   # every 0.0075 is caught by A6-std-maxdiff instead
FAR_IS_MISMATCH = {'A6-E4b-ts-n', 'A6-std-maxdiff'}
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
