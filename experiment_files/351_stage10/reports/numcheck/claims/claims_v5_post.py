"""Post-processing for a claims_defs_v5 run (read-only on documents; writes only new files into the given out_ dir).
Usage:  ~/conda-envs/jlens/bin/python claims_v5_post.py <out_dir>
Writes into <out_dir>:
  v5_scope_summary.csv        counts 一致 / 写法不统一 / 舍入写法不同 / 不一致 for the advisor page and the in-scope deck slides
  v5_scope_non_ok.csv         every non-一致 occurrence in scope (document, location, text, source value, proposed form)
  v5_definition_issues.csv    occurrences whose number matches its source but whose wording / definition does not (口径)
  v5_bounds.csv               bound statements (<=, >=, <) checked against the source
  v5_scope_unregistered.csv   result-like numbers in scope still not covered by any claim (with category)
  v5_scope_slides.csv         which slides were included and why
  v5_new_claims.csv           the claims added in v5 (registry rows)
"""
import csv, re, sys, os
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
os.environ.setdefault('CLAIMS_DEFS', 'claims_defs_v5')
import importlib
D = importlib.import_module(os.environ['CLAIMS_DEFS'])
from claims_lib import select, fmt, parse_written
from claims_docs import units

out = Path(sys.argv[1])
occ = pd.read_csv(out / 'claims_check.csv', encoding='utf-8-sig', dtype=str).fillna('')
reg = pd.read_csv(out / 'claims_registry.csv', encoding='utf-8-sig', dtype=str).fillna('')
oth = pd.read_csv(out / 'non_conclusion_numbers.csv', encoding='utf-8-sig', dtype=str).fillna('')


def slide_of(loc):
    m = re.search(r'第(\d+)页', loc)
    return int(m.group(1)) if m else None


def in_scope(doc, loc):
    if doc.startswith('导师页'):
        return True
    if doc.startswith('PPT'):
        return slide_of(loc) in D.SCOPE_SLIDES
    return False


def scope_label(doc, loc):
    if doc.startswith('导师页'):
        return '导师页 advisor/index.html'
    return 'PPT v20 第%d页 %s' % (slide_of(loc), '备注' if '备注' in loc else '正文')


FARM = getattr(D, 'FAR_IS_MISMATCH', set())
if FARM and (out / 'pattern_hits_far_from_source.csv').stat().st_size:
    far = pd.read_csv(out / 'pattern_hits_far_from_source.csv', encoding='utf-8-sig', dtype=str).fillna('')
    far = far[far.claim_id.isin(FARM)].drop_duplicates(['doc', 'location', 'context'])
    regi = reg.set_index('claim_id')
    add_rows = []
    for _, r in far.iterrows():
        g = regi.loc[r.claim_id]
        add_rows.append(dict(claim_id=r.claim_id, doc=r.doc, file='', location=r.location, text_as_written=r.written, context=r.context, status='不一致',
                             source_at_written_decimals=g.canonical, canonical=g.canonical, note='远离源值的命中按不一致计（FAR_IS_MISMATCH）', statement=g.statement,
                             source_file=g.source_file, selector=g.selector, computation=g.computation, n=g.n, value_from_source=g.value_from_source))
    occ = pd.concat([occ, pd.DataFrame(add_rows).astype(str)], ignore_index=True)
occ['in_scope'] = [in_scope(d, l) for d, l in zip(occ.doc, occ.location)]
ALLS = []
for d, g in list(occ.groupby('doc', sort=False)) + [('合计（全部文档）', occ)]:
    c = g.status.value_counts()
    ALLS.append(dict(文档=d, **{k: int(c.get(k, 0)) for k in ['一致', '写法不统一', '舍入写法不同', '不一致', '源值读取失败']}, 合计=len(g)))
pd.DataFrame(ALLS).to_csv(out / 'v6_all_docs_summary.csv', index=False, encoding='utf-8-sig')
S = occ[occ.in_scope].copy()
S['part'] = [scope_label(d, l) for d, l in zip(S.doc, S.location)]
STS = ['一致', '写法不统一', '舍入写法不同', '不一致', '源值读取失败']
rows = []
for part, g in list(S.groupby(S.part.str.replace(r' (正文|备注)$', '', regex=True))) + [('合计（范围内）', S)]:
    c = g.status.value_counts()
    rows.append(dict(范围=part, **{s: int(c.get(s, 0)) for s in STS}, 合计=len(g), 涉及结论数=g.claim_id.nunique()))
pd.DataFrame(rows).to_csv(out / 'v5_scope_summary.csv', index=False, encoding='utf-8-sig')


def proposed(r):
    try:
        v = float(r['value_from_source'])
    except ValueError:
        return ''
    w = r['text_as_written'].rstrip('%')
    _, d = parse_written(w)
    scale = 100 if r['text_as_written'].endswith('%') or 'pp' in r['context'][90:110] else 1
    regrow = reg[reg.claim_id == r['claim_id']]
    if len(regrow):
        try:
            canon = regrow.canonical.iloc[0]
        except Exception:
            canon = ''
    if r['status'] == '写法不统一':
        return r['canonical']
    c = next((c for c in D.C if c['id'] == r['claim_id']), None)
    sc = c['scale'] if c else 1
    return fmt(v * sc, d, c['sign'] if c else True) + ('%' if r['text_as_written'].endswith('%') else '')


bad = S[S.status != '一致'].copy()
bad['proposed_form'] = [proposed(r) for _, r in bad.iterrows()]
cols = ['part', 'location', 'claim_id', 'statement', 'text_as_written', 'status', 'value_from_source', 'source_at_written_decimals', 'proposed_form', 'canonical',
        'note', 'context', 'source_file', 'selector', 'computation']
bad[cols].to_csv(out / 'v5_scope_non_ok.csv', index=False, encoding='utf-8-sig')
AB = occ[occ.status != '一致'].copy()
AB['proposed_form'] = [r['canonical'] if r['status'] in ('写法不统一',) or r['claim_id'] in FARM else proposed(r) for _, r in AB.iterrows()]
AB['in_scope'] = [in_scope(d, l) for d, l in zip(AB.doc, AB.location)]
AB[['doc', 'location', 'in_scope', 'claim_id', 'statement', 'text_as_written', 'status', 'value_from_source', 'proposed_form', 'note', 'context', 'source_file', 'selector']] \
    .to_csv(out / 'v6_all_non_ok.csv', index=False, encoding='utf-8-sig')

# ---------------------------------------------------------------- definition (口径) issues
DEF = []
ALLOCC = occ.copy()
for _, r in ALLOCC.iterrows():
    cid, ctx = r['claim_id'], r['context']
    if cid in ('A5-E4b5-sur', 'A5-E4b5-sur-lo', 'A5-E4b5-sur-hi', 'A5-E4b5-smi') and re.search(r'减 5 个假标题平均|five false titles|5 个假标题（', ctx) and '1.5' not in ctx:
        DEF.append(dict(r, issue='写作“5 个假标题平均 / five false titles”，但该值是 Vpd：保留论文平均只用 1.50 个假标题（V5 五个都可用的规则保留 0 篇）',
                        proposed='写明“逐个假标题排除（Vpd），平均 1.5 个假标题”；严格 5 个假标题平均的最接近版本是 V5x0（false_0 剔除规则，1,395 篇）L40 +0.072 [0.061, 0.084]'))
    if cid.startswith('A5-X4rec-first') or cid.startswith('A5-X4rec-all'):
        DEF.append(dict(r, issue='区间不含 0 的是全部 1,178 对（tune + test 合并）；按预注册规则（tune 选层、test 确认），测试集 L8 为 +0.023 [−0.001, +0.048]，未确认（V42）',
                        proposed='加注“全部 1,178 对，未在测试集确认（测试集 L8 +0.023 [−0.001, +0.048]）”'))
    if cid in ('E4b-all-L40', 'E4b-all-L56', 'E4b-all-L24') :
        DEF.append(dict(r, issue='全样本标准化旧版（e4b_split_compare.md）；训练折标准化新版 L40 +0.061、L56 +0.075（e4b_trainstd_compare.md，§6.11 采用）',
                        proposed='改为训练折标准化值或注明“全样本标准化旧版”'))
    if cid in ('E4b-all-L24', 'E4b-all-L40', 'E4b-all-L56') and not re.search(r'普通 probe|ordinary probe|X1|对照管线|controls', ctx):
        DEF.append(dict(r, issue='该值是 X1 对照管线“普通 probe”（全部保留的 1,863 篇，全样本标准化）；文中标作 E4b',
                        proposed='标为“X1 对照管线普通 probe，1,863 篇”，或改用 E4b（1,395 篇，训练折标准化）+0.050 / +0.061 / +0.075'))
    if cid == 'A5-E4b5-e4b':
        DEF.append(dict(r, issue='“原 E4b 第一个 token +0.066”是 Vpd（4,654 篇）的第一个 token；原 E4b（V0，false_0，1,395 篇）L40 为 +0.061',
                        proposed='“第一个 token（Vpd）+0.066；原 E4b +0.061（1,395 篇）”'))
    if cid == 'A5-PR-recip':
        DEF.append(dict(r, issue='“约 1/3”：源比值 0.087 ÷ 0.247 = 0.35；同一页备注写“= 0.35”', proposed='可写“约 0.35（约三分之一）”'))
    if cid == 'A5-M2-field':
        DEF.append(dict(r, issue='领域准确率 L16–L60 为 0.698–0.722；“约 0.70”只对应 L16', proposed='“约 0.70–0.72”'))
    if cid == 'A5-N2-share':
        DEF.append(dict(r, issue='N2 纯名字先验占比 19%，与 A 部分“名字先验约 1/3（0.35）”定义不同（A_prior_decomposition 的“删去标题”先验）', proposed='两处各注明先验的定义'))
for _, r in ALLOCC[ALLOCC.context.str.contains('认得出的论文在 L8–L40 更高', regex=False)].drop_duplicates(['doc', 'location']).iterrows():
    pass
for u in units():
    for m in re.finditer(r'认得出的论文在 L8–L40 更高', u[3]):
        DEF.append(dict(claim_id='(无数字)', doc=u[0], location=u[2] or '', text_as_written='认得出的论文在 L8–L40 更高', status='—',
                        value_from_source='', context=u[3][max(0, m.start() - 90):m.end() + 60],
                        issue='无数字的定性结论；依据是全部 1,178 对的 Recognition 表（全部作者 L8 +0.031 到 L40 +0.052）；按预注册在测试集确认的版本（V42，第一作者）L8 +0.023 [−0.001, +0.048]，未确认',
                        proposed='改为“在全部 1,178 对上更高（未在测试集确认）”或补上测试集数字'))
dd = pd.DataFrame(DEF)
if len(dd):
    dd['in_scope'] = [in_scope(d, l) for d, l in zip(dd.doc, dd.location)]
    dd = dd[['in_scope', 'doc', 'location', 'claim_id', 'text_as_written', 'status', 'value_from_source', 'issue', 'proposed', 'context']]
dd.to_csv(out / 'v5_definition_issues.csv', index=False, encoding='utf-8-sig')

# ---------------------------------------------------------------- bounds
B = []
U = units()
for bid, where, sel, opx, thr, desc in D.BOUNDS:
    v, _ = select(sel)
    ok = {'<=': v <= thr, '>=': v >= thr, '<': v < thr, '>': v > thr}[opx]
    hits = []
    for u in U:
        for m in re.finditer(where, u[3]):
            loc = u[2]
            hits.append('%s %s' % (u[0], loc))
    B.append(dict(bound_id=bid, statement=desc, source_value='%.6g' % v, rule='%s %s' % (opx, thr), holds='是' if ok else '否',
                  n_occurrences=len(hits), where=' | '.join(sorted(set(hits)))[:600]))
pd.DataFrame(B).to_csv(out / 'v5_bounds.csv', index=False, encoding='utf-8-sig')

# ---------------------------------------------------------------- unregistered result numbers in scope
oth['in_scope'] = [in_scope(d, l) for d, l in zip(oth.doc, oth.location)]
O = oth[oth.in_scope].copy()
O['part'] = [scope_label(d, l) for d, l in zip(O.doc, O.location)]
O[['part', 'location', 'number', 'category', 'has_source_citation', 'context']].to_csv(out / 'v5_scope_unregistered.csv', index=False, encoding='utf-8-sig')
pd.DataFrame([dict(slide=k, why=v) for k, v in D.SCOPE_SLIDES.items()]).to_csv(out / 'v5_scope_slides.csv', index=False, encoding='utf-8-sig')
reg[reg.claim_id.str.startswith('A5-')].to_csv(out / 'v5_new_claims.csv', index=False, encoding='utf-8-sig')
print(pd.DataFrame(rows).to_string())
print('non-ok in scope', len(bad), '| definition issues', len(dd), '(in scope %d)' % (dd.in_scope.sum() if len(dd) else 0))
print('bounds', [(b['bound_id'], b['holds'], b['n_occurrences']) for b in B])
print('unregistered in scope by category'); print(O.category.value_counts().to_string())
