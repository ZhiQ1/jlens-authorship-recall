"""Post-processing for a claims_defs_v7 run (after claims_v5_post.py). Read-only on documents; writes new files into <out_dir>:
  v7_scope_unregistered_classified.csv  each remaining result-like number in the advisor scope: design constant (label) or still unregistered
  v7_definition_status.csv              the static definition-issue rows marked resolved / unresolved by a code rule on +-400 chars of current text
  v7_wording_B_held.csv                 occurrences of wording B (held for the user's decision; not errors)
  v7_advisor_counts.csv                 status counts for the advisor page only
Usage: CLAIMS_DEFS=claims_defs_v7 ~/conda-envs/jlens/bin/python claims_v7_post.py <out_dir>"""
import os, re, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
os.environ.setdefault('CLAIMS_DEFS', 'claims_defs_v7')
import importlib
D = importlib.import_module(os.environ['CLAIMS_DEFS'])
from claims_docs import units

out = Path(sys.argv[1])
U = units()
TEXT = {}
for u in U:
    TEXT.setdefault(u[0], []).append(u[3])


def wide(doc, ctx, w=400):
    key = ctx[40:110] if len(ctx) > 110 else ctx
    for t in TEXT.get(doc, []):
        i = t.find(key)
        if i >= 0:
            return t[max(0, i - w):i + len(key) + w]
    return ctx


# 1. classify remaining result-like numbers in scope
un = pd.read_csv(out / 'v5_scope_unregistered.csv', encoding='utf-8-sig', dtype=str).fillna('')
un = un[un.category.str.startswith('结果')].copy()
lab = []
for _, r in un.iterrows():
    l = ''
    for nrx, crx, name in D.NONRESULT:
        if re.search(nrx, r.number) and re.search(crx, r.context):
            l = name; break
    lab.append(l or '仍未登记')
un['classification'] = lab
un.to_csv(out / 'v7_scope_unregistered_classified.csv', index=False, encoding='utf-8-sig')

# 2. definition-issue rows -> resolved / unresolved
RULES = [('N2 纯名字先验占比', r'定义不同|delete-title prior|删标题'),
         ('全样本标准化旧版', r'X1|普通 probe|ordinary probe|对照管线|全样本标准化|full-sample|原来|orig'),
         ('区间不含 0 的是全部 1,178 对', r'0\.023|测试集上|test set|test split'),
         ('该值是 X1 对照管线', r'X1|普通 probe|ordinary probe|对照管线'),
         ('写作“5 个假标题平均', r'1\.5|逐个|per-donor'),
         ('“原 E4b 第一个 token', r'逐个排除版|Vpd|per-donor'),
         ('“约 1/3”', r'0\.35'), ('领域准确率', r'0\.70–0\.72'),
         ('无数字的定性结论', r'0\.023')]
di = pd.read_csv(out / 'v5_definition_issues.csv', encoding='utf-8-sig', dtype=str).fillna('')
st, why = [], []
for _, r in di.iterrows():
    w = wide(r.doc, r.context)
    rule = next((rx for k, rx in RULES if r.issue.startswith(k)), None)
    m = re.search(rule, w) if rule else None
    if not m and r.claim_id == 'E4b-all-L24' and re.search(r'1,395', w):
        st.append('已解决'); why.append('文中标为 E4b（1,395 篇）；L24 两条管线数值相同（E4b 0.0504、X1 0.050），0.050 对两者都对'); continue
    st.append('已解决' if m else ('未解决' if rule else '无规则')); why.append(('当前文本含“%s”' % m.group(0)) if m else '')
di['status_now'] = st; di['evidence'] = why
di.to_csv(out / 'v7_definition_status.csv', index=False, encoding='utf-8-sig')

# 3. wording B (held)
WB = r'按逐个假标题排除、5 个假标题平均|per-donor exclusion, mean of (?:the )?five false titles|five false titles, per-donor exclusion|five false titles \(per-donor|5 false titles, per-donor'
rows = []
for u in U:
    for m in re.finditer(WB, u[3]):
        rows.append(dict(doc=u[0], location=u[2], text=u[3][max(0, m.start() - 40):m.end() + 120], status='held（等用户定措辞 B）'))
pd.DataFrame(rows).to_csv(out / 'v7_wording_B_held.csv', index=False, encoding='utf-8-sig')

# 4. advisor counts
occ = pd.read_csv(out / 'claims_check.csv', encoding='utf-8-sig', dtype=str).fillna('')
a = occ[occ.doc.str.startswith('导师页')]
c = a.status.value_counts()
pd.DataFrame([dict(文档='导师页 advisor/index.html', **{k: int(c.get(k, 0)) for k in ['一致', '写法不统一', '舍入写法不同', '不一致']}, 合计=len(a), 结论数=a.claim_id.nunique())]) \
    .to_csv(out / 'v7_advisor_counts.csv', index=False, encoding='utf-8-sig')
print('unregistered result-like in scope:', len(un), un.classification.value_counts().to_dict())
print('definition rows:', len(di), di.status_now.value_counts().to_dict())
print('wording B held:', len(rows))
print('advisor:', dict(c), 'total', len(a))
