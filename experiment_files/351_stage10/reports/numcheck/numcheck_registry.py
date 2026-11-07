"""Step 2: build the registry of result quantities, read from the result files themselves (no value is typed by hand).

Sources: CSV / JSON / small parquet / analysis-written .md under the stage output folders (numcheck_common.SOURCE_DIRS),
excluding document folders and tiny/test/smoke/SUPERSEDED/backup copies (logged in out/registry_log.csv).

Entry kinds
  csv     one numeric cell (or a number inside a text cell such as "3417 / 2148"); selector = column + the row's key columns
  json    one numeric leaf; selector = JSON path
  md      one number in an analysis-written markdown report (second-hand: the md was written by an analysis script)
  derived computed here from the raw tables: row counts of every table, value counts of small categorical columns
          (e.g. label package group_tight), number of unique paper ids
How each file was computed (column 计算方法) comes from numcheck_methods.py (prose per file pattern, no numbers).

Outputs: out/numcheck_registry_full.csv.gz (all entries; numcheck_match.py writes out/numcheck_registry.csv = entries used by the table), out/registry.pkl (for matching), out/registry_log.csv.
"""
import csv, json, math, os, pickle, re, sys
import numpy as np
import pandas as pd
from numcheck_common import JL, OUT, SOURCE_DIRS, EXCLUDE_RE, NUM_RE, path_feats, col_feats, text_feats
from numcheck_methods import method_for

MAX_CSV_BYTES = 25e6
MAX_CELL_ROWS = 4000          # tables with more rows are per-paper/per-token data: only derived entries
MAX_JSON_BYTES = 8e6
MAX_PARQUET_BYTES = 300e6
MAX_PARQUET_CELL_ROWS = 300   # parquet files are mostly raw per-unit data
PER_UNIT = re.compile(r'per_?paper|paper_values|paper_layer|paper_null|paper_scores|shuffled_titles|_pairs\.csv|textbase_gap|'
                      r'per_?token|per_?author|context_level|candidate_pairwise|shuffle_context', re.I)

entries = []                  # (file_id, row_id, col_id, value, kind)
files, rows_, cols_ = [], [], []
fidx, ridx, cidx = {}, {}, {}
log = []


def _id(lst, idx, key):
    if key not in idx:
        idx[key] = len(lst); lst.append(key)
    return idx[key]


def add(rel, row, col, v, kind):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return
    if not math.isfinite(v):
        return
    entries.append((_id(files, fidx, rel), _id(rows_, ridx, row), _id(cols_, cidx, col), v, kind))


TS_RE = re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}|[0-9a-f]{8,}', re.I)
SKIP_KEY = re.compile(r'(^|_)(id|ids|sha|sha256|hash|path|file|created|written|time|date|started|finished|host|node|job|cmd|'
                      r'command|version|rev|revision|seed_str|url)($|_)|paper_id|_id$', re.I)


def nums_in_text(s):
    out = []
    if TS_RE.search(s) and len(TS_RE.sub('', s)) < len(s) * 0.5:
        return out
    for m in NUM_RE.finditer(s):
        a = m.start()
        if a > 0 and (s[a - 1].isalpha() or s[a - 1] in '_.'):
            continue
        tok = m.group(0).rstrip(',.')
        b = a + len(tok)
        if b < len(s) and (s[b].isalpha() or s[b] in '_:'):
            continue
        try:
            v = float(tok.replace(',', '').replace('−', '-'))
        except ValueError:
            continue
        if a > 0 and s[a - 1] in '-−' and (a == 1 or not s[a - 2].isalnum()):
            v = -v
        out.append(v)
    return out


KEYLIKE = re.compile(r'(layer|^l$|bin|group|readout|lens|cond|condition|role|contrast|version|question|mode|metric|stat|kind|'
                     r'name|type|label|set|split|subset|key|level|pos|position|component|comp|which|variant|model|target|'
                     r'task|order|n_mc|mc|tier|field|rank|stage|exp|measure|estimand|estimator|sample|scope|what|row|item)', re.I)


def do_table(rel, df, kind='csv'):
    n = len(df)
    add(rel, '(整表)', 'n_rows (行数)', n, 'derived')
    for c in df.columns:
        if re.search(r'paper_id|^pid$|paper$', str(c), re.I):
            try:
                add(rel, '(整表)', 'n_unique(%s)' % c, df[c].nunique(), 'derived')
            except Exception:
                pass
        if df[c].dtype == object or str(df[c].dtype) in ('category', 'bool', 'string'):
            try:
                vc = df[c].astype(str).value_counts()
            except Exception:
                continue
            if 1 < len(vc) <= 15:
                for k, cnt in vc.items():
                    add(rel, '%s=%s' % (c, k), 'count (计数)', cnt, 'derived')
    if n > (MAX_PARQUET_CELL_ROWS if kind == 'parquet' else MAX_CELL_ROWS) or PER_UNIT.search(rel):
        log.append((rel, 'cells skipped: %d rows (per-paper/per-token/raw table); only row/value counts' % n))
        return
    keycols = [c for c in df.columns if df[c].dtype == object or str(df[c].dtype) in ('bool', 'category', 'string')
               or (KEYLIKE.search(str(c)) and pd.api.types.is_integer_dtype(df[c]) and df[c].nunique() <= 80)]
    keycols = keycols[:8]
    for i, r in enumerate(df.itertuples(index=False)):
        rd = dict(zip(df.columns, r))
        sel = '; '.join('%s=%s' % (k, str(rd[k])[:60]) for k in keycols) or 'row %d' % (i + 1)
        for c in df.columns:
            v = rd[c]
            if isinstance(v, (bool, np.bool_)):
                continue
            if isinstance(v, (int, float, np.integer, np.floating)):
                if c in keycols and not pd.api.types.is_float_dtype(df[c]):
                    continue
                add(rel, sel, str(c), v, kind)
            elif isinstance(v, str) and re.search(r'\d', v) and len(v) < 300 and not re.search(r'[/\\]|\.csv|\.json', v) \
                    and not SKIP_KEY.search(str(c)):
                for x in nums_in_text(v)[:12]:
                    add(rel, sel, str(c) + ' (文本单元格内)', x, kind)


def walk_json(rel, o, path='$', depth=0):
    if depth > 12:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            walk_json(rel, v, path + '.' + str(k), depth + 1)
    elif isinstance(o, list):
        if len(o) > 400:
            add(rel, path, 'len (列表长度)', len(o), 'derived'); return
        if o and all(isinstance(x, dict) for x in o[:5]):
            # list of records: label by a key-like field when present
            for i, x in enumerate(o):
                lab = next((('%s=%s' % (k, x[k])) for k in x if isinstance(x[k], str) and KEYLIKE.search(k)), str(i))
                walk_json(rel, x, '%s[%s]' % (path, lab), depth + 1)
        else:
            for i, x in enumerate(o):
                walk_json(rel, x, '%s[%d]' % (path, i), depth + 1)
    elif isinstance(o, bool):
        return
    elif isinstance(o, (int, float)):
        add(rel, path.rsplit('.', 1)[0] if '.' in path else path, path.rsplit('.', 1)[-1], o, 'json')
    elif isinstance(o, str) and re.search(r'\d', o) and len(o) < 400 and not re.search(r'[/\\]|sha|[0-9a-f]{12}', o) \
            and not SKIP_KEY.search(path.rsplit('.', 1)[-1]):
        for x in nums_in_text(o)[:12]:
            add(rel, path.rsplit('.', 1)[0] if '.' in path else path, path.rsplit('.', 1)[-1] + ' (字符串内)', x, 'json')


def do_md(rel, text):
    heads = {}
    for ln, line in enumerate(text.splitlines(), 1):
        m = re.match(r'(#{1,4})\s+(.*)', line)
        if m:
            lvl = len(m.group(1)); heads[lvl] = m.group(2).strip()[:60]
            for k in list(heads):
                if k > lvl:
                    del heads[k]
            continue
        if not re.search(r'\d', line) or len(line) > 3000:
            continue
        hs = ' > '.join(heads[k] for k in sorted(heads))
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.strip().startswith('|') else [line]
        for ci, cell in enumerate(cells):
            for m in NUM_RE.finditer(cell):
                a = m.start()
                if a > 0 and (cell[a - 1].isalpha() or cell[a - 1] in '_./'):
                    continue
                tok = m.group(0).rstrip(',.')
                try:
                    v = float(tok.replace(',', ''))
                except ValueError:
                    continue
                if a > 0 and cell[a - 1] in '-−' and (a == 1 or not cell[a - 2].isalnum()):
                    v = -v
                ctxt = (line if len(cells) == 1 else ' | '.join(cells))
                lo = max(0, (a if len(cells) == 1 else 0) - 70)
                add(rel, '%s | 第%d行: %s' % (hs, ln, re.sub(r'\s+', ' ', ctxt[lo:lo + 160])), 'md 第%d行' % ln, v, 'md')


def main():
    nfiles = 0
    for d in SOURCE_DIRS:
        root = JL / d
        if not root.exists():
            log.append((d, 'source dir missing')); continue
        for dp, dns, fns in os.walk(root):
            reld = os.path.relpath(dp, JL)
            if EXCLUDE_RE.search(reld + '/'):
                log.append((reld, 'dir excluded (document/tiny/test/backup)')); dns[:] = []; continue
            for fn in fns:
                rel = reld + '/' + fn
                ext = fn.rsplit('.', 1)[-1].lower()
                if ext not in ('csv', 'json', 'md', 'parquet', 'tsv'):
                    continue
                if EXCLUDE_RE.search(rel):
                    log.append((rel, 'file excluded (tiny/test/backup/SUPERSEDED)')); continue
                p = root.parent / rel
                sz = p.stat().st_size
                try:
                    if ext in ('csv', 'tsv'):
                        if sz > MAX_CSV_BYTES:
                            log.append((rel, 'csv too large %.0f MB: skipped' % (sz / 1e6))); continue
                        do_table(rel, pd.read_csv(p, sep='\t' if ext == 'tsv' else ',', low_memory=False))
                    elif ext == 'parquet':
                        if sz > MAX_PARQUET_BYTES:
                            import pyarrow.parquet as pq
                            add(rel, '(整表)', 'n_rows (行数)', pq.ParquetFile(p).metadata.num_rows, 'derived')
                            log.append((rel, 'parquet large: row count only')); continue
                        do_table(rel, pd.read_parquet(p), 'parquet')
                    elif ext == 'json':
                        if sz > MAX_JSON_BYTES:
                            log.append((rel, 'json too large: skipped')); continue
                        walk_json(rel, json.loads(p.read_text(encoding='utf-8', errors='replace')))
                    elif ext == 'md':
                        do_md(rel, p.read_text(encoding='utf-8', errors='replace'))
                    nfiles += 1
                except Exception as ex:   # a bad file never stops the build
                    log.append((rel, 'WARN read error: %r' % (ex,)))
    # label-package jsonl files: line counts only
    lp = JL / 'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15'
    for p in sorted(lp.glob('*.jsonl')):
        with open(p, 'rb') as f:
            add(os.path.relpath(p, JL), '(整表)', 'n_lines (行数)', sum(1 for _ in f), 'derived')
    print('files read', nfiles, 'entries', len(entries))
    # ------------- save
    E = np.array([(a, b, c) for a, b, c, _, _ in entries], dtype=np.int32)
    V = np.array([e[3] for e in entries], dtype=np.float64)
    K = np.array([e[4] for e in entries])
    ffeat = [frozenset(path_feats(f)) for f in files]
    rfeat = [frozenset(text_feats(r.replace('=', ' ').replace('_', ' ')) | _layer_from_row(r)) for r in rows_]
    cfeat = [frozenset(col_feats(c)) for c in cols_]
    meth = [method_for(f) for f in files]
    with open(OUT / 'registry.pkl', 'wb') as f:
        pickle.dump({'E': E, 'V': V, 'K': K, 'files': files, 'rows': rows_, 'cols': cols_, 'ffeat': ffeat, 'rfeat': rfeat,
                     'cfeat': cfeat, 'meth': meth}, f, protocol=4)
    import gzip
    with gzip.open(OUT / 'numcheck_registry_full.csv.gz', 'wt', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['eid', '源文件', '类型', '列', '行/选择器', '源文件数字', '计算方法'])
        for i, (a, b, c, v, k) in enumerate(entries):
            w.writerow([i, files[a], k, cols_[c], rows_[b], repr(v), meth[a]])
    with open(OUT / 'registry_log.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['path', 'note']); w.writerows(log)


def _layer_from_row(r):
    f = set()
    for m in re.finditer(r'(?:^|; )(?:layer|l|src_layer|layer_idx)=(\d{1,2})(?:\.0)?(?:;|$)', r):
        f.add('l%d' % int(m.group(1)))
    if re.search(r'readout=final|=final(;|$)', r):
        f.add('l63')
    return f


if __name__ == '__main__':
    main()
