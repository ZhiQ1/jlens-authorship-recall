"""Strict claims check: selector engine + comparison rules. Read-only on documents and result files.

Selectors (every source value is read by code; nothing typed by hand):
  csv / parquet : {'t':'csv','f':rel_path,'where':{col: value or [values]},'col':col,'agg':None|'min'|'max'|'mean'|'sum'|'count'}
                  without agg the filter must match exactly one row (else the claim is marked SELECTOR ERROR).
  json          : {'t':'json','f':rel_path,'path':[k1,k2,...]}
  mdcell        : {'t':'mdcell','f':rel_path,'head':regex of the heading the table follows,'row':{header: cell text},
                   'col':header,'part':'est'|'lo'|'hi','agg':...}   (first table after that heading; 'cols' = list for agg over columns)
  mdre          : {'t':'mdre','f':rel_path,'re':regex with one group,'nth':0}  (regex on the raw markdown text)
  op            : {'t':'op','op':'div'|'sub'|'add'|'mul','a':sel,'b':sel}
  py            : {'t':'py','fn':callable,'desc':text}  (small documented computation on a result file)
"""
import json, re, math
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
from pathlib import Path
import pandas as pd

JL = Path('/scratch/zhang.zhiqi2/jlens')
_cache = {}


class SelErr(Exception):
    pass


def _df(rel):
    if rel not in _cache:
        p = JL / rel
        _cache[rel] = pd.read_parquet(p) if p.suffix == '.parquet' else pd.read_csv(p)
    return _cache[rel]


def _match(series, v):
    if isinstance(v, (list, tuple)):
        return series.astype(str).isin([str(x) for x in v])
    if isinstance(v, (int, float)) and not isinstance(v, bool) and pd.api.types.is_numeric_dtype(series):
        return (series - v).abs() < 1e-9
    return series.astype(str) == str(v)


def _agg(vals, agg):
    vals = [float(x) for x in vals]
    if not vals:
        raise SelErr('no rows')
    if agg is None:
        if len(vals) != 1:
            raise SelErr('%d rows match (need exactly 1)' % len(vals))
        return vals[0]
    return {'min': min, 'max': max, 'sum': sum, 'mean': lambda x: sum(x) / len(x), 'count': len}[agg](vals)


def md_tables(text):
    """[(heading_line_index, header_cells, rows)] for every markdown table; heading = last '#' line before it."""
    lines = text.splitlines()
    out, i, head = [], 0, -1
    while i < len(lines):
        if lines[i].startswith('#'):
            head = i
        if lines[i].startswith('|') and i + 1 < len(lines) and re.match(r'^\|\s*:?-', lines[i + 1]):
            hdr = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].startswith('|'):
                rows.append((j + 1, [c.strip() for c in lines[j].strip().strip('|').split(' | ')]))
                j += 1
            out.append((head, i, hdr, rows))
            i = j
            continue
        i += 1
    return lines, out


NUMTOK = re.compile(r'[+\-−]?\d+(?:\.\d+)?')


def cell_part(cell, part):
    nums = [float(x.replace('−', '-')) for x in NUMTOK.findall(cell.replace(',', ''))]
    k = {'est': 0, 'lo': 1, 'hi': 2}[part or 'est']
    if len(nums) <= k:
        raise SelErr('cell %r has no %s' % (cell, part))
    return nums[k]


def select(s):
    """Return (value, where_text) for a selector."""
    t = s['t']
    if t in ('csv', 'parquet'):
        d = _df(s['f'])
        m = pd.Series(True, index=d.index)
        for k, v in s.get('where', {}).items():
            if k not in d.columns:
                raise SelErr('column %s not in %s' % (k, s['f']))
            m &= _match(d[k], v)
        if s['col'] not in d.columns:
            raise SelErr('column %s not in %s' % (s['col'], s['f']))
        rows = d.loc[m, s['col']].dropna()
        return _agg(rows.tolist(), s.get('agg')), '%d 行' % m.sum()
    if t == 'json':
        x = json.loads((JL / s['f']).read_text())
        for k in s['path']:
            x = x[k]
        return float(x), ''
    if t == 'mdcell':
        txt = (JL / s['f']).read_text()
        lines, tabs = md_tables(txt)
        hre = re.compile(s['head'])
        cand = [tb for tb in tabs if tb[0] >= 0 and hre.search(lines[tb[0]])]
        if not cand:
            raise SelErr('heading %r not found' % s['head'])
        head, ti, hdr, rows = cand[s.get('nth', 0)]
        cols = s.get('cols') or [s['col']]
        idx = []
        for c in cols:
            if isinstance(c, int):
                idx.append(c)
            elif c in hdr:
                idx.append(hdr.index(c))
            else:
                raise SelErr('column %r not in header %r' % (c, hdr))
        vals, lns = [], []
        for ln, cells in rows:
            ok = all(cells[hdr.index(k)] == v if not isinstance(v, (list, tuple)) else cells[hdr.index(k)] in v
                     for k, v in s.get('row', {}).items())
            if ok:
                for j in idx:
                    vals.append(cell_part(cells[j], s.get('part'))); lns.append(ln)
        return _agg(vals, s.get('agg')), '第%s行' % ','.join(str(x) for x in sorted(set(lns)))
    if t == 'mdre':
        txt = (JL / s['f']).read_text()
        ms = list(re.finditer(s['re'], txt, re.M))
        if not ms:
            raise SelErr('regex not found')
        m = ms[s.get('nth', 0)]
        return float(m.group(1).replace('−', '-').replace(',', '')), '第%d行' % (txt[:m.start()].count('\n') + 1)
    if t == 'op':
        a, _ = select(s['a']); b, _ = select(s['b'])
        return {'div': a / b, 'sub': a - b, 'add': a + b, 'mul': a * b}[s['op']], ''
    if t == 'py':
        return float(s['fn']()), ''
    raise SelErr('unknown selector ' + t)


def sel_text(s):
    """Human-readable selector (column / row filter)."""
    t = s['t']
    if t in ('csv', 'parquet'):
        w = '; '.join('%s=%s' % (k, '|'.join(map(str, v)) if isinstance(v, (list, tuple)) else v) for k, v in s.get('where', {}).items())
        return '列 %s；行 %s%s' % (s['col'], w or '(全部)', ('；取 %s' % s['agg']) if s.get('agg') else '')
    if t == 'json':
        return 'JSON ' + ''.join('["%s"]' % k for k in s['path'])
    if t == 'mdcell':
        c = s.get('cols') or [s['col']]
        r = '; '.join('%s=%s' % (k, '|'.join(v) if isinstance(v, (list, tuple)) else v) for k, v in s.get('row', {}).items())
        return 'md 表（标题 /%s/ 之后第 %d 张）列 %s；行 %s；取%s%s' % (s['head'], s.get('nth', 0) + 1, ', '.join(map(str, c)), r,
                                                         {'est': '估计', 'lo': '下限', 'hi': '上限'}[s.get('part') or 'est'],
                                                         ('；%s' % s['agg']) if s.get('agg') else '')
    if t == 'mdre':
        return 'md 正则 /%s/ 第 %d 处' % (s['re'], s.get('nth', 0) + 1)
    if t == 'op':
        return '(%s) %s (%s)' % (sel_text(s['a']), {'div': '÷', 'sub': '−', 'add': '+', 'mul': '×'}[s['op']], sel_text(s['b']))
    if t == 'py':
        return s['desc']
    return '?'


def sel_files(s):
    if s['t'] == 'op':
        return sel_files(s['a']) + [f for f in sel_files(s['b']) if f not in sel_files(s['a'])]
    if s['t'] == 'py':
        return s.get('files', [])
    return [s['f']]


# ------------------------------------------------------------------ comparison
def parse_written(txt):
    """'+0.207' / '−0.04' / '9,108' / '82%' / '+9.3 pp' -> (value, decimals)."""
    s = txt.replace('−', '-').replace(',', '').replace('，', '').strip()
    m = re.match(r'([+\-]?)\s*(\d+(?:\.\d+)?)', s)
    v = float(m.group(1) + m.group(2))
    dec = len(m.group(2).split('.')[1]) if '.' in m.group(2) else 0
    return v, dec


def rnd(x, d, mode=ROUND_HALF_UP):
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(x)).quantize(q, rounding=mode))


def compare(src, written, scale=1.0):
    """status for one written number vs the source value. scale: 100 for % or pp."""
    w, d = parse_written(written)
    x = src * scale
    exp = rnd(x, d)
    if abs(w - exp) < 1e-9 or (abs(w) < 10 ** -d / 2 and abs(exp) < 10 ** -d / 2):
        return '一致', exp, d
    for mode in (ROUND_HALF_EVEN, ROUND_DOWN):
        if abs(w - rnd(x, d, mode)) < 1e-9:
            return '舍入写法不同', exp, d
    # double rounding (rounded to one more decimal first)
    if abs(w - rnd(rnd(x, d + 1), d)) < 1e-9:
        return '舍入写法不同', exp, d
    return '不一致', exp, d


def fmt(x, d, sign=True):
    v = rnd(x, d)
    s = ('%.' + str(d) + 'f') % abs(v)
    if d == 0 and abs(v) >= 1000:
        s = '{:,}'.format(int(round(abs(v))))
    if v < 0 and float(s.replace(',', '')) != 0:
        return '−' + s
    return ('+' if sign and v >= 0 else '') + s
