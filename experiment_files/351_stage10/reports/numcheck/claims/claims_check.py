"""Strict claims check (read-only on documents and results). Outputs only into claims/out_<timestamp>/ (never overwrites).

1. registry: for every claim in claims_defs.C read the source value with its explicit selector.
2. occurrences: every regex of the claim run on every document unit (claims_docs.units()); kept only if the claim's
   anchor words occur within +-250 chars (stops a pattern like "L54 #" from catching unrelated numbers), and only if the
   written value is within 25% (or 2 units at its decimals) of the source value; farther hits go to pattern_hits_far_from_source.csv.
3. status per occurrence: 一致 (written = source rounded half-up at the written decimals and written exactly as the
   proposed canonical form) / 写法不统一 (numerically 一致 but written differently from the canonical form: fewer
   decimals, missing sign, …) / 舍入写法不同 (equals the source only under half-even, truncation or double rounding) /
   不一致 (anything else).
4. other numbers: every number in every document not covered by an occurrence, classified (no CI needed; says so).
5. conclusions without data: sentences in the report's conclusion sections with no number and no source path.
"""
import csv, html, re, sys, time, json, traceback
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from claims_lib import select, sel_text, sel_files, compare, fmt, parse_written, SelErr
from claims_docs import units, locate
import os, importlib
claims_defs = importlib.import_module(os.environ.get('CLAIMS_DEFS', 'claims_defs'))   # CLAIMS_DEFS=claims_defs_v2 for v2

OUT = HERE / ('out_' + time.strftime('%Y%m%d_%H%M%S'))
OUT.mkdir()

ANCHOR = [('S10-L63', r'目标|target|对照|control|A − B|输出|output|L63|0\.207'), ('S10-', r'目标|target|对照|control|A ?− ?B|C ?− ?[AB]|R0|R1|lens|L5\d|L6\d'),
          ('X3-', r'X3|Jacobian|J-lens|lens|L62'), ('X1c', r'X1_cond|前 10|top 10|top10|容易|easier'), ('X1-', r'X1|首字母|initial|名开头|given|名的|姓'),
          ('X2-', r'X2|引用|citation|Spearman'), ('A-bin', r'引用档|citation|0-2|4097'), ('E1-', r'E1|替换|patch|恢复|recover'),
          ('E2-', r'E2|阻断|knock|屏蔽|block'), ('P1-', r'P1|逐位置|per-position|名字位置|name positions|单个|single'),
          ('X7-', r'X7|S\(L5|论文特有|paper-specific|control 593|对照'), ('X6-', r'X6|false_0–false_4|5 个假标题|5 false titles|R\(L52\)'),
          ('E4b', r'E4b|probe'), ('AT-', r'补充 9|addendum 9|alltok|全部名字 token|all-token|surname|姓|首字母|initial|名的第一个|given'),
          ('PR-', r'先验|prior'), ('G-', r'P1|P2|P3|E1|分组|group|R2|mc_team_a|识别|认得出|recogn'),
          ('S7', r'Stage 7|7\.[134]|Pilot|J-Lens|Vanilla|JMRR|token'), ('S8', r'Stage 8|8D|RQ|200 篇|200 new|J-Lens|Vanilla|对'),
          ('N-', r'组|group|target|control|篇|papers|R0|R1|识别'), ('M2', r'M2|BERT|Qwen|R²|AUROC')]
CANON_OVERRIDE = {}
TOL_REL = 0.25   # a regex hit counts as an occurrence only if within 25% (or 2 units at the written decimals) of the source;
                 # farther hits are a different number caught by a loose pattern and are listed in pattern_hits_far_from_source.csv


def anchor_for(cid):
    for p, a in ANCHOR:
        if cid.startswith(p):
            return re.compile(a)
    return None


def main():
    U = units()
    N = claims_defs.N
    reg_rows, occ_rows, covered, far = [], [], defaultdict(set), []   # covered[(unit index)] = set of char offsets
    for c in claims_defs.C:
        try:
            v, wh = select(c['sel'])
            err = ''
        except (SelErr, Exception) as e:
            v, wh, err = None, '', 'SELECTOR ERROR: %s' % e
        canon = c['canon'] or (fmt(v * c['scale'], c['dec'], c['sign']) if v is not None else '')
        reg = dict(claim_id=c['id'], statement=c['stmt'], source_file=' + '.join(sel_files(c['sel'])), selector=sel_text(c['sel']) + ((' → ' + wh) if wh else ''),
                   computation=c['comp'], n=c['n'], decimals_shown=c['dec'], value_from_source=('%.6g' % v) if v is not None else err,
                   canonical=canon, report_location=c['where'], note=c['note'], n_occ=0, n_docs=0, worst='')
        reg_rows.append(reg)
        anc = anchor_for(c['id'])
        seen = set()
        for pat in c['occ']:
            near, win = None, 0
            if isinstance(pat, tuple):
                pat, near, win = pat
            rx = re.compile(pat.replace('#', N))
            nrx = re.compile(near) if near else None
            for ui, u in enumerate(U):
                t = u[3]
                for m in rx.finditer(t):
                    s, e = m.span('v')
                    if (ui, s) in seen:
                        continue
                    ctxw = t[max(0, s - 250):e + 250]
                    if nrx and not nrx.search(t[s:e + win]):          # near-words must follow the number (its own source note)
                        continue
                    if c.get('excl') and re.search(c['excl'], t[max(0, s - 120):e + 120]):
                        continue
                    if anc and not anc.search(ctxw):
                        continue
                    w = m.group('v')
                    post = t[e:e + 3]
                    scale = c['scale']
                    if post.startswith('%') and scale == 1 and v is not None and abs(v) <= 1.5:
                        scale = 100
                    if v is not None:
                        wv, wd = parse_written(w)
                        if abs(wv - v * scale) > max(TOL_REL * abs(v * scale), 2 * 10 ** -wd):
                            far.append(dict(claim_id=c['id'], doc=u[0], location=locate(u, s), written=w, value_from_source=reg['value_from_source'],
                                            pattern=pat, context=re.sub(r'\s+', ' ', t[max(0, s - 90):e + 60])))
                            continue
                    seen.add((ui, s))
                    covered[ui].add(s)
                    onote = ''
                    if v is None:
                        st, exp = '源值读取失败', None
                    else:
                        st, exp, d = compare(v, w, scale)
                        onote = ''
                        if st != '一致':
                            for alt in c.get('alt', []):
                                lab, asel = alt[0], alt[1]
                                ast = alt[2] if len(alt) > 2 else '写法不统一'
                                try:
                                    av, _ = select(asel)
                                except Exception as ex:
                                    continue
                                if compare(av, w, scale)[0] == '一致':
                                    st, onote = ast, ('与另一结果文件一致：%s = %.6g；选定源为 %s' % (lab, av, reg['source_file'])
                                                      + ('（旧版 / 已被取代，按不一致列出）' if ast == '不一致' else ''))
                                    break
                        wn = w.replace('-', '−')
                        if st == '一致' and wn.lstrip('+') != canon.lstrip('+'):   # a leading '+' is treated as formatting, not a different number
                            st = '写法不统一'
                            onote = '数值对，写法与建议标准写法 %s 不同（%s）' % (canon, '位数较少' if d < c['dec'] else '位数较多' if d > c['dec'] else '符号/格式')
                    occ_rows.append(dict(claim_id=c['id'], doc=u[0], file=str(u[1]), location=locate(u, s), text_as_written=w + (post[0] if post[:1] in '%' else ''),
                                         context=re.sub(r'\s+', ' ', t[max(0, s - 90):e + 60]), status=st,
                                         source_at_written_decimals=('' if exp is None else ('%g' % exp)), canonical=canon, note=onote,
                                         statement=c['stmt'], source_file=reg['source_file'], selector=reg['selector'], computation=c['comp'], n=c['n'],
                                         value_from_source=reg['value_from_source']))
    # claim-level summary
    by = defaultdict(list)
    for o in occ_rows:
        by[o['claim_id']].append(o)
    order = ['不一致', '舍入写法不同', '写法不统一', '一致']
    for r in reg_rows:
        os_ = by[r['claim_id']]
        r['n_occ'] = len(os_); r['n_docs'] = len({o['doc'] for o in os_})
        r['worst'] = min((o['status'] for o in os_), key=lambda s: order.index(s) if s in order else -1) if os_ else ('未在文中找到' if r['value_from_source'][:1] != 'S' else 'SELECTOR ERROR')
        # 写法不统一 across documents: several different written forms at the same decimals
        forms = Counter(o['text_as_written'].replace('-', '−').lstrip('+') for o in os_)
        r['written_forms'] = ' / '.join('%s×%d' % kv for kv in forms.most_common())
    write_csv(OUT / 'claims_registry.csv', reg_rows)
    write_csv(OUT / 'claims_check.csv', occ_rows)
    write_csv(OUT / 'pattern_hits_far_from_source.csv', far)
    # ---------------- other numbers
    other = classify_others(U, covered)
    write_csv(OUT / 'non_conclusion_numbers.csv', other)
    # ---------------- conclusions without data
    nod = no_data_conclusions(U)
    for r in nod:
        j = next((v for k, v in claims_defs.NODATA_REVIEW.items() if r['sentence'].startswith(k)), ('未人工复核（新出现的句子）', ''))
        r['judgement'], r['data_that_could_support_it'] = j
    write_csv(OUT / 'conclusions_without_data.csv', nod)
    # ---------------- summaries
    summ = []
    docs = sorted({o['doc'] for o in occ_rows}, key=lambda d: [x[0] for x in U].index(d) if d in [x[0] for x in U] else 99)
    sts = ['一致', '写法不统一', '舍入写法不同', '不一致', '源值读取失败']
    for d in docs + ['合计']:
        cnt = Counter(o['status'] for o in occ_rows if d == '合计' or o['doc'] == d)
        summ.append(dict(文档=d, **{s: cnt.get(s, 0) for s in sts}, 合计=sum(cnt.values())))
    write_csv(OUT / 'summary_by_doc.csv', summ)
    mism = [o for o in occ_rows if o['status'] in ('不一致', '舍入写法不同', '源值读取失败') or o.get('note', '').startswith('与另一结果文件')]
    write_csv(OUT / 'mismatches_for_user.csv', mism)
    oc = Counter(o['category'] for o in other)
    oc_src = Counter((o['category'], o['has_source_citation']) for o in other)
    render_html(reg_rows, occ_rows, summ, mism, other, oc, oc_src, nod)
    print('claims', len(reg_rows), 'occurrences', len(occ_rows), Counter(o['status'] for o in occ_rows))
    print('selector errors', [r['claim_id'] + ': ' + r['value_from_source'] for r in reg_rows if r['value_from_source'].startswith('SEL')])
    print('claims not found in any doc', [r['claim_id'] for r in reg_rows if r['n_occ'] == 0])
    print('out', OUT)


def write_csv(p, rows):
    if not rows:
        p.write_text(''); return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(p, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)


# ------------------------------------------------------------------ non-conclusion numbers
NUMRX = re.compile(r'(?<![\w.])[+−\-]?\d[\d,]*(?:\.\d+)?%?')
PATHRX = re.compile(r'\d{3}_[A-Za-z0-9_]+/|labels_2026|\.csv|\.md\b|\.json|\.parquet|\.py')
CATS = [('代码行号 / 文件内位置', r'(?:\.py|\.md|\.csv|\.json|\.sh)[: ]\s?$|行 ?$|lines? ?$|:\s?$'),
        ('作业号', r'(?:作业|job|jobs|array)\s*#?\s*$'),
        ('日期 / 时间', None), ('版本 / 编号（Stage、补充、§、页、图、表）', r'(?:Stage|补充|addendum|§|第|页|图|表|Fig\.?|Table|slide|v|版|U|X|M|E|P|C|R|批次|item|#)\s?$'),
        ('层号', r'(?:L|层|layer|layers)\s?$'),
        ('计算资源 / 用时', r'^\s?(?:秒|s\b|小时|h\b|分钟|min\b|GiB|GB|张 ?(?:GPU|A100)|个?节点|天)'),
        ('配置 / 设计常数（种子、阈值、K、折数、bootstrap 次数等）', r'(?:seed|种子|阈值|threshold|K ?=|alpha|α|折|fold|bootstrap|次重抽|draws|上限|tolerance|容差|top ?-?\d|dim|batch|max|min_)'),
        ('样本 / 计数（篇、位、个、对、token、行）', r'^\s?(?:篇|位|个|对|条|行|token|tokens|papers|authors|pairs|名|组|档|层|次|contexts|ids|unit)'),
        ]


def classify_one(t, s, e):
    pre = t[max(0, s - 14):s]; post = t[e:e + 14]
    tok = t[s:e]
    if re.match(r'\d{4}-\d{2}-\d{2}', t[s:s + 10]) or re.match(r'\d{1,2}:\d{2}', t[s:s + 5]) or re.search(r'\d{4}-\d{2}-$|\d{4}-$', t[max(0, s - 8):s]) \
            or re.match(r'\s?(?:月|日|年)', post) or re.fullmatch(r'20[12]\d', tok):
        return '日期 / 时间'
    if re.search(r'[A-Za-z_/]$', t[max(0, s - 1):s]) or re.match(r'[A-Za-z_/]', post[:1] or ' ') and not re.match(r'\s?(?:pp|e-)', post):
        return '标识符 / 路径 / 编号中的数字'
    if re.fullmatch(r'1[01]\d{6}', tok.lstrip('+')):
        return '作业号'
    for cat, rx in CATS:
        if rx is None:
            continue
        if cat.startswith('计算资源'):
            if re.match(rx, post, re.I):
                return cat
        elif cat.startswith('配置'):
            if re.search(rx, t[max(0, s - 30):e + 12], re.I):
                return cat
        elif cat.startswith('样本'):
            if re.match(rx, post, re.I):
                return cat
        elif re.search(rx, pre, re.I):
            return cat
    if '.' in tok or tok.startswith(('+', '−', '-')) or tok.endswith('%'):
        return '结果数字（不在结论清单内：表格、正文细节、图注；本轮未逐条核对）'
    return '其他整数（计数、编号、说明）'


def classify_others(U, covered):
    rows = []
    for ui, u in enumerate(U):
        t = u[3]
        for m in NUMRX.finditer(t):
            s, e = m.span()
            if s in covered[ui] or (s + 1) in covered[ui] or (s - 1) in covered[ui]:
                continue
            cat = classify_one(t, s, e)
            ctx = t[max(0, s - 160):e + 160]
            rows.append(dict(doc=u[0], location=locate(u, s), number=m.group(0), category=cat,
                             has_source_citation='有' if PATHRX.search(ctx) else '无',
                             needs_CI='否（非结论数字）' if not cat.startswith('结果') else '视用途：若用作结论需补登记',
                             context=re.sub(r'\s+', ' ', t[max(0, s - 60):e + 40])))
    return rows


# ------------------------------------------------------------------ conclusions without data
CONC_SECTIONS = [r'主要结论', r'§7结论|Conclusions', r'§1摘要', r'综合：四条线', r'三种口径并列', r'结论上变了什么', r'三个主要发现', r'Stage \d+[A-D]? ?结论|结论$']


def no_data_conclusions(U):
    u = U[0]                          # the report
    t, marks = u[3], u[4]
    rows = []
    offs = [o for o, _ in marks] + [len(t)]
    for (o, l), e in zip(marks, offs[1:]):
        if not any(re.search(p, l.split(' | ')[-1] if ' | ' in l else l) for p in CONC_SECTIONS):
            continue
        seg = t[o:e]
        for sm in re.finditer(r'[^。！？\n]{12,}?[。！？]', seg):
            snt = sm.group(0).strip()
            if re.search(r'[A-Za-z]{4,} [a-z]{3,} [a-z]{3,}', snt) and not re.search(r'[一-鿿]', snt):
                continue                     # English duplicate of a Chinese sentence
            has_num = re.search(r'(?<![A-Za-z§])\d', re.sub(r'L\d{1,2}|Stage ?\d+(?:\.\d)?|R[012]|§\d+(?:\.\d+)?|补充 ?\d+|[EPXMNCF]\d[a-z]?|\d{4}-\d{2}-\d{2}', '', snt))
            has_src = PATHRX.search(snt) or re.search(r'见(?:第|上|下|§)|详见|（第[一二三四五]部分）|§\d', snt)
            if not has_num and not has_src:
                rows.append(dict(doc=u[0], location=locate(u, o + sm.start()), sentence=snt[:300]))
    # dedupe
    seen, out = set(), []
    for r in rows:
        if r['sentence'] not in seen:
            seen.add(r['sentence']); out.append(r)
    return out


# ------------------------------------------------------------------ html
STCLS = {'一致': 'ok', '写法不统一': 'var', '舍入写法不同': 'rnd', '不一致': 'bad', '源值读取失败': 'bad'}


def render_html(reg, occ, summ, mism, other, oc, oc_src, nod):
    e = html.escape
    H = []
    H.append('<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             '<title>Claims Check</title><style>'
             ':root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--ln:#ddd;--ok:#e7f5ea;--var:#fff6d6;--rnd:#fde9d4;--bad:#fbd9d9;--hd:#f3f3f3}'
             '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161616;--fg:#eee;--mut:#aaa;--ln:#333;--ok:#173a22;--var:#3a3315;--rnd:#40291a;--bad:#4a1c1c;--hd:#222}}'
             ':root[data-theme="dark"]{--bg:#161616;--fg:#eee;--mut:#aaa;--ln:#333;--ok:#173a22;--var:#3a3315;--rnd:#40291a;--bad:#4a1c1c;--hd:#222}'
             'body{background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,"PingFang SC","Noto Sans CJK SC",sans-serif;margin:0;padding:12px 16px}'
             'h1{font-size:19px}h2{font-size:16px;margin-top:22px}table{border-collapse:collapse;width:100%;font-size:12.5px}'
             'td,th{border:1px solid var(--ln);padding:3px 5px;vertical-align:top;text-align:left}th{background:var(--hd);position:sticky;top:0}'
             '.wrap{overflow-x:auto;max-width:100%}.ok{background:var(--ok)}.var{background:var(--var)}.rnd{background:var(--rnd)}.bad{background:var(--bad)}'
             '.mut{color:var(--mut);font-size:12px}details{margin:6px 0}summary{cursor:pointer;font-weight:600}'
             '@media (max-width:700px){td,th{font-size:11.5px}.hide-s{display:none}}</style></head><body>')
    H.append('<h1>结论数字严格核对（claims check）</h1><p class="mut">生成于 %s · 代码 claims_check.py / claims_defs.py · 只读文档与结果文件；不修改任何文档。'
             '“是否一致”：一致 = 按文中位数四舍五入后等于源值且写法与建议标准写法相同；写法不统一 = 数值对、写法与标准写法不同（位数更少、少了正号等）；'
             '舍入写法不同 = 只在银行家舍入 / 截断 / 两次舍入下相等；不一致 = 其他。</p>' % time.strftime('%F %T'))
    H.append('<h2>1. 汇总（按文档 × 状态）</h2><div class="wrap"><table><tr>' + ''.join('<th>%s</th>' % e(k) for k in summ[0]) + '</tr>')
    for r in summ:
        H.append('<tr>' + ''.join('<td>%s</td>' % e(str(v)) for v in r.values()) + '</tr>')
    H.append('</table></div>')
    H.append('<h2>2. 给用户的不一致清单（%d 处；只提建议，不改文档）</h2><div class="wrap"><table><tr><th>文档</th><th>位置</th><th>结论</th><th>文中数字</th>'
             '<th>源文件数字（按文中位数）</th><th>建议统一写法</th><th>是否一致</th><th class="hide-s">上下文</th></tr>' % len(mism))
    for o in mism:
        H.append('<tr class="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="hide-s mut">%s</td></tr>' % (
            STCLS[o['status']], e(o['doc']), e(o['location'][:90]), e(o['claim_id'] + ' ' + o['statement']), e(o['text_as_written']),
            e(o['source_at_written_decimals']), e(o['canonical']), e(o['status'] + ('；' + o['note'] if o.get('note') else '')), e(o['context'])))
    H.append('</table></div>')
    H.append('<h2>3. 结论登记表（%d 条结论数字）</h2><div class="wrap"><table><tr><th>ID</th><th>结论</th><th>源文件</th><th>列/行</th><th>计算方法</th><th>样本量</th>'
             '<th>源文件数字</th><th>建议标准写法</th><th>出现</th><th>各处写法</th><th>最差状态</th></tr>' % len(reg))
    for r in reg:
        cls = STCLS.get(r['worst'], 'var')
        H.append('<tr class="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d 处 / %d 文档</td><td>%s</td><td>%s</td></tr>' % (
            cls, e(r['claim_id']), e(r['statement']) + ('<br><span class="mut">%s</span>' % e(r['note']) if r['note'] else ''), e(r['source_file']), e(r['selector']),
            e(r['computation']), e(r['n']), e(r['value_from_source']), e(r['canonical']), r['n_occ'], r['n_docs'], e(r['written_forms']), e(r['worst'])))
    H.append('</table></div>')
    H.append('<h2>4. 每一处出现（%d 处）</h2>' % len(occ))
    byc = defaultdict(list)
    for o in occ:
        byc[o['claim_id']].append(o)
    for r in reg:
        os_ = byc[r['claim_id']]
        if not os_:
            continue
        H.append('<details><summary>%s · %s · 源 %s · %d 处</summary><div class="wrap"><table><tr><th>文档</th><th>位置</th><th>文中数字</th><th>源文件数字</th><th>是否一致</th><th class="hide-s">上下文</th></tr>' % (
            e(r['claim_id']), e(r['statement']), e(r['value_from_source']), len(os_)))
        for o in os_:
            H.append('<tr class="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="hide-s mut">%s</td></tr>' % (
                STCLS[o['status']], e(o['doc']), e(o['location'][:100]), e(o['text_as_written']), e(o['source_at_written_decimals']), e(o['status']), e(o['context'])))
        H.append('</table></div></details>')
    H.append('<h2>5. 结论里没有数据支撑的句子（报告结论段自动筛出：句中既无数字也无出处路径；%d 句，已逐句判定）</h2><div class="wrap"><table><tr><th>文档</th><th>位置</th><th>句子</th><th>判定</th><th>可支撑的数据</th></tr>' % len(nod))
    for r in nod:
        cls = '' if r['judgement'].startswith(('标题句', '不是')) else ' class="var"'
        H.append('<tr%s><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (cls, e(r['doc']), e(r['location'][:80]), e(r['sentence']), e(r['judgement']), e(r['data_that_could_support_it'])))
    H.append('</table></div>')
    H.append('<h2>6. 其余数字的分类（不是结论，不需要置信区间；%d 个）</h2><div class="wrap"><table><tr><th>类别</th><th>个数</th><th>附近有出处路径</th><th>附近无出处</th></tr>' % len(other))
    for cat, k in oc.most_common():
        H.append('<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (e(cat), k, oc_src.get((cat, '有'), 0), oc_src.get((cat, '无'), 0)))
    H.append('</table></div><p class="mut">逐条清单见 non_conclusion_numbers.csv。“结果数字（不在结论清单内）”是表格、细节和图注里的结果，不是本页登记的结论；若某个被当作结论使用，需要先补进 claims_defs.py。</p>')
    H.append('</body></html>')
    (OUT / 'claims_check.html').write_text('\n'.join(H), encoding='utf-8')


if __name__ == '__main__':
    main()
