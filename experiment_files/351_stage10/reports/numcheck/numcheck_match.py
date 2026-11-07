"""Step 3: match every extracted document number to registry entries and compare at the displayed number of decimals.

Score of a candidate entry (higher = the entry is more likely the quantity the text talks about):
  +8 the file is cited right after the number (same bracket) / +4 cited elsewhere within ±300 chars
  layer: +3 same layer as the nearest layer mention (or L63 for "output/final"), -5 different layer
  experiment id (E1, P1, X3, RQ2, 8D, 7.3 ...): +3 per shared id (max 6), -2 if both name ids but none shared
  stage number: +1.5 shared, -1.5 different; group/contrast (target/control/all, A−B, C−A ...): +1.5 shared, -1 different
  readout (logit/public/self100/fitA/final/probe): +1.5 shared, -1 different
  CI position: number is a lower/upper bound "[a, b]" and the column is lo/hi: +2; bound vs point-estimate column: -1.5
  counts: "篇/papers/n =" and a count column: +1.5; shared other words: +0.4 each (max 3)
  md (second-hand analysis report): -1; match only after dropping the sign: -2; percent view (x100) without a %/pp sign: -1.5
Status
  一致            value matches at the displayed decimals and score >= 8 (>= 10 if the number has only 1 significant digit)
  一致（不确定）    value matches but score 3..8: plausible source, not certain (not counted as 一致)
  舍入写法不同      no exact match with score >= 6, but a well-matched entry (score >= 9) is within 1.5 units of the
                  last shown digit (wrong rounding direction, truncation, or a different copy of the number);
                  only for numbers with >= 2 significant digits and a decimal point or %
  不一致           the number cites a file right after it (same bracket), that file has no entry with this value, and the
                  best-matching entry there (score >= 11, same layer / experiment / CI position, same sign, within 20%, not a count column)
                  has a different value; nearest value shown. Integers are never more than 不一致（不确定）
  不一致（不确定）   same with score 6..11, or an integer
  paths with snapshot/archive/partial/superseded get -2; shared words in file/row/column names +0.4/+0.5 each (capped)
  未找到出处        nothing with score >= 3 has this value
"""
import csv, html, json, math, pickle, re, sys
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from numcheck_common import OUT, PATH_RE, LAYER_RE, EXP_RE, STAGE_RE, text_feats

R = pickle.load(open(OUT / 'registry.pkl', 'rb'))
E, V, K = R['E'], R['V'], R['K']
files, rows_, cols_ = R['files'], R['rows'], R['cols']
ffeat, rfeat, cfeat, meth = R['ffeat'], R['rfeat'], R['cfeat'], R['meth']
NE = len(V)
FID, RID, CID = E[:, 0], E[:, 1], E[:, 2]

# ------------------------------------------------------------ entry codes
EXP_IDS = sorted({f for s in ffeat + rfeat + cfeat for f in s if f.startswith('x:')})
EXPBIT = {x: i for i, x in enumerate(EXP_IDS[:63])}
GROUPS = ['target', 'control', 'guard', 'a-b', 'c-a', 'c-b', 'd-b', 'b-a']
READ = ['logit', 'public', 'self100', 'fita', 'probe', 'final']


def codes(fs):
    lay = [int(f[1:]) for f in fs if re.fullmatch(r'l\d{1,2}', f)]
    ex = 0
    for f in fs:
        if f in EXPBIT:
            ex |= 1 << EXPBIT[f]
    st = [f for f in fs if re.fullmatch(r'stage\d+', f)]
    g = sum(1 << i for i, x in enumerate(GROUPS) if x in fs)
    r = sum(1 << i for i, x in enumerate(READ) if x in fs)
    return lay, ex, st, g, r


def build_codes(feats):
    L = np.full(len(feats), -1, np.int16); X = np.zeros(len(feats), np.uint64); S = np.full(len(feats), -1, np.int16)
    G = np.zeros(len(feats), np.uint16); RD = np.zeros(len(feats), np.uint16)
    for i, fs in enumerate(feats):
        lay, ex, st, g, r = codes(fs)
        if len(lay) == 1:
            L[i] = lay[0]
        elif len(lay) > 1:
            L[i] = -2                      # several layers named: ambiguous
        X[i] = ex; S[i] = int(st[0][5:]) if st else -1; G[i] = g; RD[i] = r
    return L, X, S, G, RD


fL, fX, fS, fG, fR = build_codes(ffeat)
rL, rX, rS, rG, rR = build_codes(rfeat)
cL, cX, cS, cG, cR = build_codes(cfeat)
# readout=final rows: final; group from row only (file names like target_vs_control name both groups)
eL = np.where(rL[RID] != -1, rL[RID], np.where(cL[CID] != -1, cL[CID], fL[FID]))
eX = fX[FID] | rX[RID] | cX[CID]
eS = fS[FID]
eG = np.where(rG[RID] > 0, rG[RID], np.where(cG[CID] > 0, cG[CID], 0)).astype(np.uint16)
eR = np.where(rR[RID] > 0, rR[RID], cR[CID]).astype(np.uint16)
colname = np.array([c.lower() for c in cols_])
ckind = np.zeros(len(cols_), np.int8)       # 0 point, 1 lo, 2 hi, 3 count
for i, c in enumerate(colname):
    if re.search(r'(^|_)(lo|low|lower|ci_lo|ci_low|q025|p2\.5|lb)($|_)', c) or c.endswith('_lo'):
        ckind[i] = 1
    elif re.search(r'(^|_)(hi|high|upper|ci_hi|ci_high|q975|p97\.5|ub)($|_)', c) or c.endswith('_hi'):
        ckind[i] = 2
    elif re.search(r'(^n$|^n_|_n$|count|n_rows|rows|n_papers|n_authors|n_unique|n_lines|len \()', c):
        ckind[i] = 3
eC = ckind[CID]
isMD = (K == 'md')
OLD = np.array([bool(re.search(r'snapshot|archive|partial|_old|superseded|before_|prelim', x, re.I)) for x in files])
# sorted views
ORD = {}
for name, arr in (('raw', V), ('abs', np.abs(V)), ('pct', V * 100), ('abspct', np.abs(V) * 100)):
    o = np.argsort(arr, kind='stable'); ORD[name] = (o, arr[o])
basename = defaultdict(list)
for i, f in enumerate(files):
    basename[f.rsplit('/', 1)[-1].lower()].append(i)
BASE_RE = re.compile(r'([A-Za-z0-9_\-]+\.(?:csv|json|md|parquet))')


def cited(pre, post):
    """file ids cited right after the number (strong) and elsewhere in the wide context (weak)."""
    strong, weak = set(), set()
    m = re.search(r'[）)〕\]](?![^（(〔\[]*[）)〕])', post)       # first closing bracket that closes something opened before
    cut = m.start() if m else 0
    for part, tgt in ((post[:cut], strong), (post[cut:], weak), (pre, weak)):
        for p in set(PATH_RE.findall(part)) | set(BASE_RE.findall(part)):
            p = p.rstrip('.,;）)')
            hits = [i for i, f in enumerate(files) if f.endswith(p)] if '/' in p else basename.get(p.lower(), [])
            if not hits and '/' in p:                 # cited a directory
                hits = [i for i, f in enumerate(files) if f.startswith(p.rstrip('/') + '/')][:400]
            tgt.update(hits)
    return strong, weak - strong


def doc_codes(r):
    pre, post = r['pre'], r['post']
    m = re.search(r'\[表头: (.*?); 行首: (.*?)\]$', r['loc'])
    tab = (m.group(1) + ' ' + m.group(2)) if m else ''
    near = pre[-120:] + ' # ' + post[:60]
    fs = text_feats(near + ' # ' + tab)
    # nearest layer: last mention before (within 90 chars), else first after (within 25)
    lay = -1
    ms = list(LAYER_RE.finditer(pre[-90:]))
    if ms:
        lay = int(ms[-1].group(1))
    else:
        m = LAYER_RE.search(post[:25])
        if m:
            lay = int(m.group(1))
    if lay == -1 and tab:
        ms = list(LAYER_RE.finditer(tab))
        if len({x.group(1) for x in ms}) == 1:
            lay = int(ms[0].group(1))
    if lay == -1 and re.search(r'(final|output|输出|最终)', pre[-60:] + ' ' + tab, re.I):
        lay = 63
    ex = 0
    for f in fs:
        if f in EXPBIT:
            ex |= 1 << EXPBIT[f]
    st = [int(f[5:]) for f in fs if re.fullmatch(r'stage\d+', f)]
    g = sum(1 << i for i, x in enumerate(GROUPS) if x in fs)
    for m in re.finditer(r'(?<![A-Za-z])([ABCD])\s?[−\-–]\s?([ABCD])(?![A-Za-z])', near):
        k = (m.group(1) + '-' + m.group(2)).lower()
        if k in GROUPS:
            g |= 1 << GROUPS.index(k)
    rd = sum(1 << i for i, x in enumerate(READ) if x in fs)
    brk = 0
    if re.search(r'\[\s*[+−\-]?$', pre[-3:] + ''):
        brk = 1
    elif re.search(r'\[\s*[+−\-]?[\d.]+\s*,\s*[+−\-]?$', pre[-25:]):
        brk = 2
    cnt = bool(re.match(r'\s?(篇|位|个|对|条|papers|authors|tokens|contexts|pairs)', post) or re.search(r'n\s?=\s?$', pre[-5:]))
    words = {f for f in fs if not f.startswith(('x:', 'stage')) and not re.fullmatch(r'l\d+', f)}
    return lay, ex, st, g, rd, brk, cnt, words


def popcount(a):
    a = a.astype(np.uint64)
    c = np.zeros(a.shape, np.int64)
    while np.any(a):
        c += (a & np.uint64(1)).astype(np.int64); a = a >> np.uint64(1)
    return c


def score(idx, dc, strong, weak, absm=False):
    lay, ex, st, g, rd, brk, cnt, words = dc
    s = np.zeros(len(idx))
    f = FID[idx]
    if strong:
        s += 8 * np.isin(f, list(strong))
    if weak:
        s += 4 * np.isin(f, list(weak))
    el = eL[idx]
    if lay >= 0:
        s += np.where(el == lay, 3, np.where(el >= 0, -5, 0))
    x = eX[idx]
    if ex:
        sh = popcount(x & np.uint64(ex))
        s += np.minimum(3 * sh, 6) - 2 * ((sh == 0) & (x > 0))
    if st:
        es = eS[idx]; s += np.where(np.isin(es, st), 1.5, np.where(es >= 0, -1.5, 0))
    eg = eG[idx]
    if g:
        s += np.where((eg & g) > 0, 1.5, np.where(eg > 0, -1, 0))
    er = eR[idx]
    if rd:
        s += np.where((er & rd) > 0, 1.5, np.where(er > 0, -1, 0))
    ec = eC[idx]
    if brk:
        s += np.where(ec == brk, 2, np.where(ec == 0, -1.5, 0))
    else:
        s += np.where((ec == 1) | (ec == 2), -1.5, 0)
    if cnt:
        s += np.where(ec == 3, 1.5, 0)
    s -= 1 * isMD[idx]
    if absm:
        s -= 2
    # shared words, per unique file / row / column
    if words:
        uf, inv = np.unique(f, return_inverse=True)
        wf = np.array([min(3, 0.4 * len(words & ffeat[u])) for u in uf])
        s += wf[inv]
        ur, inv = np.unique(RID[idx], return_inverse=True)
        if len(ur) <= 60000:
            s += np.array([min(2, 0.5 * len(words & rfeat[u])) for u in ur])[inv]
        uc, inv = np.unique(CID[idx], return_inverse=True)
        s += np.array([min(1.5, 0.5 * len(words & cfeat[u])) for u in uc])[inv]
    s -= 2 * OLD[f]
    return s


def window(name, lo, hi):
    o, a = ORD[name]
    i, j = np.searchsorted(a, lo, 'left'), np.searchsorted(a, hi, 'right')
    return o[i:j]


def sig_digits(numstr):
    s = re.sub(r'[^\d.]', '', numstr.split('/')[0]).lstrip('0').replace('.', '').lstrip('0')
    return len(s.rstrip('0')) if '.' not in numstr else len(s)


def fmt(v):
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return ('%.6g' % v)


def entry_label(i):
    return files[FID[i]], '%s | %s' % (cols_[CID[i]], rows_[RID[i]])


def main():
    X = pd.read_csv(OUT / 'extracted.csv', keep_default_na=False, dtype={'pre': str, 'post': str})
    import os
    if os.environ.get('NUMCHECK_LIMIT'):
        X = X.sample(int(os.environ['NUMCHECK_LIMIT']), random_state=0).sort_values('nid')
    out, used = [], set()
    MAXC = 150000
    for r in X.to_dict('records'):
        x = float(r['value']); d = r['decimals']
        d = int(d) if str(d) not in ('', 'nan') else None
        strong, weak = cited(r['pre'], r['post'])
        dc = doc_codes(r)
        if r['frac']:
            u = 0.05; h = 0.04
        elif d is None:
            u = abs(x) * 0.05; h = abs(x) * 0.005
        else:
            u = 10.0 ** (-d); h = 0.5 * u * (1 + 1e-6)
        pct = r['pct'] or r['pp']
        # a %/pp later in the same list ("+6.83 / +4.75 / +4.38 pp") also counts; otherwise pct view with a penalty
        pct_list = bool(re.match(r'^(\s?[/、,，]\s?[+−\-]?[\d.]+)+\s?(%|pp)', r['post'][:60]))
        pct = pct or pct_list
        views = (['pct', 'raw'] if pct else ['raw', 'pct?'])
        best = {'exact': (None, -99, ''), 'near': (None, -99, '')}
        alts = {}
        sd = sig_digits(r['num_str'])
        wins = [('exact', x - h, x + h)]
        if sd >= 2 and (d is None or d >= 1 or pct) and not r['frac']:
            wins.append(('near', x - 1.5 * u, x + 1.5 * u))
        for kind, lo, hi in wins:
            for vw in views:
                for sign_drop in (False, True):
                    if sign_drop and x < 0:
                        continue
                    vw0 = vw
                    vw = vw.rstrip('?')
                    nm = ('abs' + vw if vw == 'pct' else 'abs') if sign_drop else vw
                    if sign_drop and nm == 'abspct':
                        pass
                    idx = window(nm, lo, hi)
                    if sign_drop:                       # only entries that are negative (positive ones already seen)
                        idx = idx[V[idx] < 0]
                    if len(idx) == 0:
                        continue
                    if len(idx) > MAXC:
                        keep = np.isin(FID[idx], list(strong | weak)) if (strong or weak) else np.zeros(len(idx), bool)
                        idx = np.concatenate([idx[keep], idx[~keep][:: max(1, len(idx) // MAXC)]])
                    sc = score(idx, dc, strong, weak, absm=sign_drop)
                    if vw0 == 'pct?':
                        sc = sc - 1.5
                    if kind == 'near':
                        vv = (V[idx] * (100 if vw == 'pct' else 1)); vv = np.abs(vv) if sign_drop else vv
                        sc = np.where((vv >= x - h) & (vv <= x + h), -99, sc)   # exclude exact hits
                    k = int(np.argmax(sc))
                    if kind == 'exact':
                        top = np.argsort(-sc)[:40]
                        for j in top:
                            fj = int(FID[idx[j]])
                            if sc[j] > -50 and (fj not in alts or sc[j] > alts[fj]):
                                alts[fj] = float(sc[j])
                    if sc[k] > best[kind][1]:
                        best[kind] = (int(idx[k]), float(sc[k]), vw + ('（去符号）' if sign_drop else ''))
        # best entry in cited files regardless of value (for 不一致)
        bad = (None, -99, '')
        if strong:
            idx = np.nonzero(np.isin(FID, list(strong)))[0]
            if len(idx):
                sc = score(idx, dc, strong, weak)
                top = sc.max()
                cand = idx[sc >= top - 0.01]
                vv = V[cand] * (100 if pct else 1)
                k = int(np.argmin(np.abs(vv - x)))
                i0 = int(cand[k])
                ctxm = (dc[0] >= 0 and eL[i0] == dc[0]) or (int(eX[i0]) & dc[1]) > 0 or (eC[i0] == dc[5] and dc[5] > 0)
                close = abs(vv[k] - x) <= 0.2 * max(abs(x), abs(vv[k])) and np.sign(vv[k]) == np.sign(x) \
                    and not (d not in (0, None) and eC[i0] == 3)
                bad = (i0, float(top), 'pct' if pct else 'raw', bool(ctxm and close), float(vv[k]))
        hi_bar = 10 if sd <= 1 else 8
        if 'near' not in best:
            best['near'] = (None, -99, '')
        be, se, ve = best['exact']; bn, sn, vn = best['near']
        note = []
        if be is not None and se >= hi_bar:
            st, pick, ps, pv = '一致', be, se, ve
        elif bn is not None and sn >= 9 and se < 6:
            st, pick, ps, pv = '舍入写法不同', bn, sn, vn
        elif be is not None and se >= 3:
            st, pick, ps, pv = '一致（不确定）', be, se, ve
            if sd <= 1:
                note.append('只有 1 位有效数字')
        elif bad[0] is not None and bad[1] >= 6 and sd >= 2 and bad[3]:
            st = '不一致' if (bad[1] >= 11 and d not in (0, None)) else '不一致（不确定）'
            pick, ps, pv = bad[:3]
            note.append('源值 = 引用文件中上下文最吻合的条目里最接近的值')
        else:
            st, pick, ps, pv = '未找到出处', (be if be is not None else bn), max(se, sn), (ve or vn)
            if strong and bad[0] is not None:
                note.append('文中引用的文件里没有这个值（上下文最吻合条目的最接近值 %s）' % fmt(bad[4]))
            if pick is not None:
                note.append('只有低得分的数值巧合候选，不算出处')
        if r['approx']:
            note.append('文中为约数')
        if r['frac']:
            note.append('分数写法，按 ±0.04 比较')
        if re.search(r'(÷|比值|ratio|占|约\s?1/|[\d,]+\s?/\s?[\d,]+\s?=\s?$|[\d.]+\s?[−\-–]\s?[(（]?[+−\-]?[\d.]+[)）]?\s?=\s?$)', r['pre'][-40:] + ' ' + r['post'][:20]):
            note.append('可能是由两个数相除得到')
        if pv and 'pct' in pv:
            note.append('按百分比比较（源值×100）')
        if pv and '去符号' in pv:
            note.append('源值为负，文中未写负号')
        if r['note']:
            note.append(r['note'])
        if pick is not None:
            used.add(pick)
            sf, sel = entry_label(pick)
            sv = fmt(V[pick])
            mth = meth[FID[pick]]
        else:
            sf = sel = sv = mth = ''
        alt = sorted(((sc_, f_) for f_, sc_ in alts.items() if pick is None or f_ != FID[pick]), reverse=True)[:2]
        alt_s = '；'.join('%s (%.1f)' % (files[f_], sc_) for sc_, f_ in alt if sc_ >= 3)
        if st == '一致' and alt and alt[0][0] >= ps - 1:
            note.append('另有得分相近的其他出处（数值同样一致）')
        if strong:
            note.append('文中引用：' + '、'.join(sorted({files[i].rsplit('/', 1)[-1] for i in strong}))[:120])
        out.append({'文档': r['doc'], '位置': r['loc'], '上下文': r['ctx'], '文中数字': r['num_str'], '源文件': sf, '列/行': sel,
                    '计算方法': mth, '源文件数字': sv, '是否一致': st, '得分': round(ps, 1) if pick is not None else '',
                    '说明': '；'.join(note), '其他候选出处（得分）': alt_s, 'eid': pick if pick is not None else '', 'nid': r['nid']})
    T = pd.DataFrame(out)
    T.to_csv(OUT / 'numcheck_table.csv', index=False, encoding='utf-8-sig')
    # registry rows actually used
    with open(OUT / 'numcheck_registry.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['eid', '源文件', '类型', '列', '行/选择器', '源文件数字', '计算方法'])
        for i in sorted(used):
            w.writerow([i, files[FID[i]], K[i], cols_[CID[i]], rows_[RID[i]], repr(float(V[i])), meth[FID[i]]])
    summarize(T)


ORDER = ['一致', '一致（不确定）', '舍入写法不同', '不一致', '不一致（不确定）', '未找到出处']


def summarize(T):
    piv = T.pivot_table(index='文档', columns='是否一致', values='nid', aggfunc='count', fill_value=0)
    piv = piv.reindex(columns=[c for c in ORDER if c in piv.columns]); piv['合计'] = piv.sum(axis=1)
    piv.loc['合计'] = piv.sum()
    piv.to_csv(OUT / 'summary_by_doc.csv', encoding='utf-8-sig')
    # same source quantity written differently across documents
    M = T[T['是否一致'].isin(['一致', '舍入写法不同', '一致（不确定）']) & (T['eid'] != '')].copy()
    M['norm'] = M['文中数字'].str.replace(r'[+%]| pp', '', regex=True)
    multi = []
    for eid, g in M.groupby('eid'):
        if g['文档'].nunique() < 2:
            continue
        forms = g.groupby('文档')['文中数字'].agg(lambda s: ' / '.join(sorted(set(s))))
        if g['norm'].nunique() > 1 or (g['是否一致'] == '舍入写法不同').any():
            multi.append({'源文件': g['源文件'].iloc[0], '列/行': g['列/行'].iloc[0], '源文件数字': g['源文件数字'].iloc[0],
                          '各文档写法': ' ‖ '.join('%s: %s' % (k, v) for k, v in forms.items()),
                          '含舍入写法不同': '是' if (g['是否一致'] == '舍入写法不同').any() else '',
                          '最高得分': g['得分'].max(), '出现次数': len(g)})
    MU = pd.DataFrame(multi)
    if len(MU):
        MU = MU.sort_values(['含舍入写法不同', '最高得分'], ascending=[False, False])
    MU.to_csv(OUT / 'cross_doc_variants.csv', index=False, encoding='utf-8-sig')
    NF = T[T['是否一致'] == '未找到出处']
    NF.to_csv(OUT / 'not_found.csv', index=False, encoding='utf-8-sig')
    BAD = T[T['是否一致'].isin(['不一致', '不一致（不确定）', '舍入写法不同'])]
    BAD.to_csv(OUT / 'mismatches.csv', index=False, encoding='utf-8-sig')
    write_html(T, piv, MU, BAD)
    print(piv.to_string())


def write_html(T, piv, MU, BAD):
    e = lambda s: html.escape(str(s))
    cls = {'一致': 'ok', '一致（不确定）': 'un', '舍入写法不同': 'rd', '不一致': 'bd', '不一致（不确定）': 'bu', '未找到出处': 'nf'}
    rows = []
    for r in T.itertuples(index=False):
        rows.append('<tr class="%s" data-d="%s"><td>%s</td><td>%s</td><td class="cx">%s</td><td><b>%s</b></td><td class="p">%s</td>'
                    '<td class="p">%s</td><td>%s</td><td>%s</td><td class="st">%s</td><td>%s</td><td>%s</td></tr>' % (
                        cls[r.是否一致], e(r.文档), e(r.文档), e(r.位置), e(r.上下文), e(r.文中数字), e(r.源文件), e(r._5)[:300],
                        e(r.计算方法), e(r.源文件数字), e(r.是否一致), e(r.得分), e(r.说明)))
    docs = sorted(T['文档'].unique())
    ph = piv.to_html(classes='s', border=0)
    mu = MU.head(400).to_html(classes='s', border=0, index=False) if len(MU) else '<p>无</p>'
    bad = BAD[['文档', '位置', '文中数字', '源文件数字', '是否一致', '源文件', '列/行', '上下文']].head(600).to_html(classes='s', border=0, index=False)
    H = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>数字核对表</title><style>
:root{--bg:#F6F7F9;--sf:#fff;--ink:#1B2433;--mu:#5A6577;--ru:#D9DEE6;--cd:#EEF1F5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12161D;--sf:#1A2029;--ink:#E6EAF0;--mu:#A2ACBB;--ru:#2E3642;--cd:#232A35}}
:root[data-theme="dark"]{--bg:#12161D;--sf:#1A2029;--ink:#E6EAF0;--mu:#A2ACBB;--ru:#2E3642;--cd:#232A35}
body{margin:0;background:var(--bg);color:var(--ink);font:13px/1.5 system-ui,"Noto Sans SC",sans-serif}main{padding:16px;max-width:100%%}
table{border-collapse:collapse;background:var(--sf)}td,th{border-bottom:1px solid var(--ru);padding:4px 6px;vertical-align:top;text-align:left}
th{background:var(--cd);position:sticky;top:0}.cx{max-width:420px}.p{max-width:260px;overflow-wrap:anywhere;font-size:12px}
.ok .st{color:#2E7D4F}.un .st{color:#7a6a00}.rd .st{color:#A35A00}.bd .st{color:#B3261E;font-weight:700}.bu .st{color:#B3261E}.nf .st{color:#666}
.tw{overflow-x:auto}.s td,.s th{font-size:12px}select,input{font:inherit;margin:4px}
</style></head><body><main>
<h1>数字核对表</h1><p>生成：numcheck_run.sh。规则见 numcheck_match.py 开头。“一致（不确定）”不算一致。共 %d 个数字。</p>
<h2>按文档和状态计数</h2><div class="tw">%s</div>
<h2>不一致 / 舍入写法不同（前 600 条，完整见 mismatches.csv）</h2><div class="tw">%s</div>
<h2>同一源数字在不同文档中写法不同（前 400 条，完整见 cross_doc_variants.csv）</h2><div class="tw">%s</div>
<h2>全部数字</h2>
<p>文档 <select id="fd"><option value="">全部</option>%s</select> 状态 <select id="fs"><option value="">全部</option>%s</select>
搜索 <input id="fq" placeholder="上下文/文件"> <span id="nshow"></span></p>
<div class="tw"><table id="T"><thead><tr><th>文档</th><th>位置</th><th>上下文</th><th>文中数字</th><th>源文件</th><th>列/行</th><th>计算方法</th>
<th>源文件数字</th><th>是否一致</th><th>得分</th><th>说明</th></tr></thead><tbody>%s</tbody></table></div>
<script>
const fd=document.getElementById('fd'),fs=document.getElementById('fs'),fq=document.getElementById('fq'),rows=[...document.querySelectorAll('#T tbody tr')];
function f(){let n=0;const d=fd.value,s=fs.value,q=fq.value.toLowerCase();for(const r of rows){const ok=(!d||r.dataset.d===d)&&(!s||r.querySelector('.st').textContent===s)&&(!q||r.textContent.toLowerCase().includes(q));r.style.display=ok&&n<3000?'':'none';if(ok)n++;}document.getElementById('nshow').textContent=n+' 条（最多显示 3000）';}
fd.onchange=fs.onchange=f;fq.oninput=f;f();
</script></main></body></html>""" % (len(T), ph, bad, mu, ''.join('<option>%s</option>' % e(d) for d in docs),
                                      ''.join('<option>%s</option>' % s for s in ORDER), ''.join(rows))
    (OUT / 'numcheck_table.html').write_text(H, encoding='utf-8')


if __name__ == '__main__':
    main()
