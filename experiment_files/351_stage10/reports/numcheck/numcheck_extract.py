"""Step 1: pull every number out of every current document.

Output: out/extracted.csv (one row per kept number) and out/skipped.csv (numbers not treated as results, with the reason).
Visible text only: <script>/<style>/<svg>/<head> and data: URIs are dropped (logged as skipped blocks); table cells keep table/row/column.
Deck: each <section class="slide"> = one slide; slide text from the HTML (slides.json text if the section has no text),
plus the Chinese notes (notes_zh.json) and English notes (slides.json 'notes').
"""
import csv, html, json, re, sys
from html.parser import HTMLParser
from numcheck_common import OUT, documents, NUM_RE, parse_num

SKIP_TAGS = {'script', 'style', 'svg', 'head', 'noscript', 'template'}
BLOCK = {'p', 'div', 'li', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'section', 'table', 'ul', 'ol', 'pre',
         'blockquote', 'figcaption', 'caption', 'dt', 'dd', 'details', 'summary', 'article', 'aside', 'header', 'footer', 'hr'}
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'col', 'area', 'base', 'wbr', 'source'}


class TextLoc(HTMLParser):
    """Collects visible text; for each text piece records (start offset, location label)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buf, self.n = [], 0
        self.marks = []                         # (offset, loc)
        self.skip = 0
        self.heads = {}                         # level -> text
        self.cur_h = None; self.h_text = []
        self.last_id = ''
        self.tables = []                        # stack of [table_no, row, col]
        self.ntab = 0
        self.skipped_blocks = 0

    def loc(self):
        hs = ' > '.join(self.heads[k] for k in sorted(self.heads) if self.heads[k])
        s = hs[-160:] if hs else '(文档开头)'
        if self.last_id:
            s = '#' + self.last_id + ' | ' + s
        if self.tables:
            t = self.tables[-1]
            s += ' | 表%d 行%d 列%d' % (t[0], t[1], t[2])
            hd = t[3].get(t[2], '') if t[1] > 1 else ''
            rl = t[4] if t[2] > 1 else ''
            if hd or rl:
                s += ' [表头: %s; 行首: %s]' % (hd[:50], rl[:50])
        return s

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            if tag not in VOID:
                self.skip += 1; self.skipped_blocks += 1
            return
        if self.skip:
            return
        a = dict(attrs)
        if a.get('id'):
            self.last_id = a['id'][:60]
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.cur_h = int(tag[1]); self.h_text = []
        if tag == 'table':
            self.ntab += 1; self.tables.append([self.ntab, 0, 0, {}, '', []])
        elif tag == 'tr' and self.tables:
            self.tables[-1][1] += 1; self.tables[-1][2] = 0; self.tables[-1][4] = ''
        elif tag in ('td', 'th') and self.tables:
            self.tables[-1][2] += 1
        if tag in BLOCK:
            self._add(' \n ')

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            if tag not in VOID:
                self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in ('h1', 'h2', 'h3', 'h4') and self.cur_h:
            lvl = self.cur_h
            self.heads[lvl] = re.sub(r'\s+', ' ', ''.join(self.h_text)).strip()[:70]
            for k in list(self.heads):
                if k > lvl:
                    del self.heads[k]
            self.cur_h = None
        if tag == 'table' and self.tables:
            self.tables.pop()
        if tag in BLOCK:
            self._add(' \n ')

    def handle_data(self, data):
        if self.skip:
            return
        if self.cur_h:
            self.h_text.append(data)
        if self.tables and data.strip():
            t = self.tables[-1]
            if t[1] == 1:
                t[3][t[2]] = (t[3].get(t[2], '') + ' ' + data.strip()).strip()
            if t[2] == 1:
                t[4] = (t[4] + ' ' + data.strip()).strip()
        self.marks.append((self.n, self.loc()))
        self._add(data)

    def _add(self, s):
        self.buf.append(s); self.n += len(s)

    def result(self):
        return ''.join(self.buf), self.marks


def html_text(h):
    h = re.sub(r'data:[a-z/+\-]+;base64,[A-Za-z0-9+/=]+', 'data:', h)
    p = TextLoc(); p.feed(h); p.close()
    return p.result()


def md_text(t):
    """Markdown: location = current heading path + line number."""
    marks, heads, off = [], {}, 0
    for i, line in enumerate(t.splitlines(keepends=True), 1):
        m = re.match(r'(#{1,4})\s+(.*)', line)
        if m:
            lvl = len(m.group(1)); heads[lvl] = m.group(2).strip()[:70]
            for k in list(heads):
                if k > lvl:
                    del heads[k]
        hs = ' > '.join(heads[k] for k in sorted(heads))
        marks.append((off, (hs[-160:] or '(文档开头)') + ' | 第%d行' % i))
        off += len(line)
    return t, marks


# ------------------------------------------------------------------ classification of each digit run
def classify(t, s, e):
    """Return (skip_reason or None, info dict). t = full text, [s, e) = the digit run."""
    tok = NUM_RE.match(t, s).group(0) if NUM_RE.match(t, s) else t[s:e]
    pre = t[max(0, s - 12):s]
    post = t[e:e + 12]
    c0 = t[s - 1] if s > 0 else ' '
    c1 = t[e] if e < len(t) else ' '
    # whole whitespace-delimited token
    a = s
    while a > 0 and not t[a - 1].isspace() and t[a - 1] not in '（(〔[，,；;：“"\'、' and s - a < 120:
        a -= 1
    b = e
    while b < len(t) and not t[b].isspace() and t[b] not in '）)〕]，；;：”"\'、' and b - e < 120:
        b += 1
    word = t[a:b]
    if re.search(r'/|\\|_|\.(csv|json|md|parquet|py|pt|jsonl|html|png|pdf|pptx|sh|log)\b', word):
        return 'path/identifier', None
    if re.search(r'https?:|artifact/', t[max(0, s - 60):s]) and not re.search(r'\s', t[max(0, s - 30):s]):
        return 'url', None
    if re.search(r'((\.(py|md|csv|json|sh|sbatch|txt|log|yaml|html))|(?<![A-Za-z])[A-Z]{1,3}\d{2}|行|lines?|line no\.?)\s?[:：]?\s?(\d+\s?[–\-]\s?\d+\s?,\s?|\d+\s?,\s?)*$', pre) \
            and not re.search(r'\.\d', t[s:e]):
        return 'code/file line reference (file:line)', None
    if tok in ('95', '90', '99') and re.match(r'\s?%\s?(CI|区间|置信|bootstrap|confidence|的区间|interval|置信区间)', t[e:e + 16], re.I):
        return 'CI level (95% CI)', None
    if re.search(r'layers?\w*\s*[=:]?\s*[\[(（{]\s*(\d+\s*[,，–\-]\s*)*$', pre + '', re.I) and '.' not in tok:
        return 'layer index', None
    if re.fullmatch(r'\d{1,2}\.\d[A-E]?', tok) and re.search(r'(Stage|阶段)\s?' + re.escape(tok) + r'(?!\d)', t[max(0, s - 20):e + 20]):
        return 'stage/experiment number', None
    if c0 == 'L' or (c0 in '–-~' and re.search(r'L\d{1,2}$', t[max(0, s - 4):s - 1])):
        return 'layer index', None
    if re.search(r'(?:layers?|层|block)\s?$', pre, re.I) and '.' not in tok:
        return 'layer index', None
    if re.fullmatch(r'\d{1,2}', tok) and re.match(r'\s?层', post):
        return 'layer index', None
    if c0.isalpha() and c0.isascii():
        return 'identifier (letter+digits, e.g. E1/X3/U28/v19)', None
    if re.match(r'[0-9a-f]*[a-f][0-9a-f]*', t[e:e + 8]) and re.fullmatch(r'[0-9a-f]{6,}', re.split(r'[^0-9a-fA-F]', t[s:s + 40])[0] or 'x'):
        return 'sha/hex', None
    if re.fullmatch(r'[0-9a-f]{7,64}', word.strip('`').lower()) and re.search(r'[a-f]', word.lower()):
        return 'sha/hex', None
    if c1.isalpha() and c1.isascii() and not re.match(r'(pp|e[\-−+]?\d)', t[e:e + 4]):
        if re.match(r'[A-E](?![a-z])', c1):
            return 'stage/experiment id (e.g. 8D, 7.1B)', None
        return 'identifier/unit (digits+letters, e.g. 32B, 80GB, 3x)', None
    if re.match(r'\d{4}-\d{1,2}-\d{1,2}', t[s:s + 10]) or re.search(r'\d{4}-\d{1,2}-$', t[max(0, s - 8):s]) \
            or re.search(r'\d{4}-$', t[max(0, s - 5):s]):
        return 'date', None
    if re.match(r'\d{1,2}:\d{2}', t[s:s + 5]) or re.search(r'\d:$', t[max(0, s - 3):s]) and re.fullmatch(r'\d{2}', tok):
        return 'time of day', None
    if re.match(r'\d{1,2}\s?月', t[s:s + 4]) or re.match(r'\d{1,2}\s?日', t[s:s + 4]) or re.match(r'\s?年', post):
        return 'date', None
    if re.fullmatch(r'(19|20)\d\d', tok) and not re.search(r'(B\s*=|bootstrap|draw|次|篇|个|位|author|paper|token|prompt|对|条)', t[max(0, s - 25):e + 12], re.I):
        return 'year', None
    if re.fullmatch(r'1[01]\d{6}', tok):
        return 'job id', None
    if re.search(r'(作业|job|jobs|array|sbatch)\s*[#:]?\s*$', pre, re.I):
        return 'job id', None
    if re.search(r'(Stage|stage|阶段|Exp\.?|实验|Experiment|Line|线)\s*$', pre):
        return 'stage/experiment number', None
    if re.search(r'(§\s?|第\s*|slide\s*|Slide\s*|slides\s*|p\.\s*|page\s*|页码\s*|pp\.\s*|(?<![A-Za-z])p)$', pre):
        return 'slide/section/item number', None
    if re.match(r'(\.\d+){2,}', t[e:e + 8]) or re.search(r'\d\.\d+\.$', t[max(0, s - 6):s]):
        return 'version/section number (a.b.c)', None
    if re.search(r'\d-$', t[max(0, s - 6):s]) or (c1 == '-' and re.match(r'-\d', t[e:e + 2])):
        return 'range label without spaces (e.g. citation bin 0-2, 513-1024)', None
    if re.search(r'[×x]\s?$', t[max(0, s - 2):s]) or re.match(r'\s?[×x]\s?\d', t[e:e + 3]):
        if re.search(r'1920|1080|1280|720|A4', t[max(0, s - 10):e + 10]):
            return 'image size', None
    if re.match(r'[.)、]\s', t[e:e + 2]) and re.search(r'(^|\n)\s*$', t[max(0, s - 4):s]):
        return 'list numbering', None
    if re.search(r'(seed|种子|随机种子)\s*=?\s*$', pre, re.I):
        return None, {'note': 'seed (config value)'}
    return None, {}


def extract_from_text(doc, file, t, marks, rows, skipped, loc_prefix=''):
    import bisect
    offs = [m[0] for m in marks]
    i = 0
    for m in NUM_RE.finditer(t):
        s, e = m.span()
        if s > 0 and (t[s - 1].isdigit() or t[s - 1] == '.' and s > 1 and t[s - 2].isdigit()):
            continue
        tok = m.group(0).rstrip(',.')
        e = s + len(tok)
        k = bisect.bisect_right(offs, s) - 1
        loc = loc_prefix + (marks[k][1] if k >= 0 else '')
        ctx = re.sub(r'\s+', ' ', t[max(0, s - 80):e + 80]).strip()
        reason, info = classify(t, s, e)
        if reason:
            skipped.append({'文档': doc, '文件': file, '位置': loc, '数字': tok, '原因': reason, '上下文': ctx})
            continue
        try:
            v, dec = parse_num(tok)
        except ValueError:
            skipped.append({'文档': doc, '文件': file, '位置': loc, '数字': tok, '原因': 'unparsable', '上下文': ctx}); continue
        # sign
        sign = ''
        j = s - 1
        while j >= 0 and t[j] == ' ' and s - j < 3:
            j -= 1
        if j >= 0 and t[j] in '+−-':
            before = t[j - 1] if j > 0 else ' '
            if t[j] == '+' or not (before.isdigit() or before.isalpha()):
                sign = '+' if t[j] == '+' else '-'
        if sign == '-':
            v = -v
        post = t[e:e + 6]
        pct = bool(re.match(r'\s?%', post)) or bool(re.match(r'\s?[–\-~到至]\s?[\d.]+\s?%', post))
        pp = bool(re.match(r'\s?pp\b', post)) or bool(re.match(r'\s?[–\-~到至]\s?[\d.]+\s?pp', t[e:e + 14]))
        frac = None
        mfr = re.match(r'/(\d{1,2})(?!\d|/|[A-Za-z_])', t[e:e + 4])
        if mfr and dec == 0 and v <= 20 and not re.search(r'[A-Za-z_/]', t[max(0, s - 1):s]):
            frac = float(mfr.group(1))
        approx = bool(re.search(r'(≈|~|约|大约|左右|about|around|roughly|近|≲|≳|<|>|≤|≥)\s?[+−-]?\s?$', t[max(0, s - 8):s]))
        pre_w = re.sub(r'\s+', ' ', t[max(0, s - 300):s - (1 if sign else 0)]); post_w = re.sub(r'\s+', ' ', t[e:e + 300])
        rows.append({'doc': doc, 'file': str(file), 'loc': loc, 'num_str': (('+' if sign == '+' else '−' if sign == '-' else '') + tok
                                                                           + ('%' if re.match(r'\s?%', post) else '')
                                                                           + (' pp' if re.match(r'\s?pp\b', post) else '')
                                                                           + ('/%d' % frac if frac else '')),
                     'value': v if not frac else v / frac, 'decimals': dec if not frac else -1, 'pct': int(pct), 'pp': int(pp),
                     'frac': int(bool(frac)), 'approx': int(approx), 'note': (info or {}).get('note', ''),
                     'ctx': ctx, 'pre': pre_w, 'post': post_w, 'offset': s})


def main():
    rows, skipped, blocks = [], [], []
    for doc, kind, path, extra in documents():
        if kind == 'html':
            t, marks = html_text(path.read_text(encoding='utf-8', errors='replace'))
            extract_from_text(doc, path, t, marks, rows, skipped)
        elif kind == 'md':
            t, marks = md_text(path.read_text(encoding='utf-8', errors='replace'))
            extract_from_text(doc, path, t, marks, rows, skipped)
        elif kind == 'deck':
            h = path.read_text(encoding='utf-8', errors='replace')
            secs = re.split(r'(?=<section class="slide)', h)[1:]
            secs[-1] = secs[-1].split('</section>')[0] + '</section>'
            meta = json.loads(extra['slides'].read_text()); notes = json.loads(extra['notes'].read_text())
            if len(meta) != len(secs):
                print('WARN: deck has %d sections but slides.json has %d entries' % (len(secs), len(meta)), file=sys.stderr)
            for k, sec in enumerate(secs, 1):
                t, marks = html_text(sec)
                if len(re.sub(r'\s+', '', t)) < 15 and k <= len(meta) and meta[k - 1].get('text'):
                    t = meta[k - 1]['text']; marks = [(0, 'slides.json 文本')]
                extract_from_text(doc, path, t, [(o, '正文 ' + l) for o, l in marks], rows, skipped, loc_prefix='第%d页 ' % k)
                nz = notes.get(str(k), {})
                if nz.get('text'):
                    extract_from_text(doc, extra['notes'], nz['text'], [(0, '备注（中文）')], rows, skipped, loc_prefix='第%d页 ' % k)
                if k <= len(meta) and meta[k - 1].get('notes'):
                    extract_from_text(doc, extra['slides'], meta[k - 1]['notes'], [(0, '备注（英文）')], rows, skipped,
                                      loc_prefix='第%d页 ' % k)
    for i, r in enumerate(rows):
        r['nid'] = i
    cols = ['nid', 'doc', 'file', 'loc', 'num_str', 'value', 'decimals', 'pct', 'pp', 'frac', 'approx', 'note', 'ctx', 'pre', 'post', 'offset']
    with open(OUT / 'extracted.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
    with open(OUT / 'skipped.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['文档', '文件', '位置', '数字', '原因', '上下文']); w.writeheader(); w.writerows(skipped)
    from collections import Counter
    print('kept', len(rows), 'skipped', len(skipped))
    print(Counter(r['doc'] for r in rows))
    print(Counter(r['原因'] for r in skipped))


if __name__ == '__main__':
    main()
