"""Shared settings and helpers for the jlens number check (numcheck_*.py).

Nothing here edits any document or result file. Outputs go only to numcheck/out/.
"""
import re
from pathlib import Path

JL = Path('/scratch/zhang.zhiqi2/jlens')
REP = JL / '351_stage10/reports'
HERE = Path(__file__).resolve().parent
import os
OUT = Path(os.environ.get('NUMCHECK_OUT', HERE / 'out'))
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- documents
def documents():
    """(doc_name, kind, path, extra) for every document to check. Re-evaluated on every run, so new files are picked up."""
    d = []
    d.append(('报告 stage1_11_report', 'html', REP / 'stage1_11/stage1_11_report.html', None))
    d.append(('PPT merged deck v20', 'deck', REP / 'merged_deck/stage1_11_deck.html',
              {'slides': REP / 'talk/src/export/slides.json', 'notes': REP / 'talk/src/export/notes_zh.json'}))
    d.append(('方法手册 methods_handbook', 'html', REP / 'methods/methods_handbook.html', None))
    for p in sorted((REP / 'talk_docs').glob('*.html')):
        if '.before_' in p.name:
            continue
        d.append(('讲稿 ' + p.stem, 'html', p, None))
    rd = sorted((p for p in (REP / 'github').glob('README_draft_*.md') if '.before_' not in p.name), key=lambda p: p.stat().st_mtime)
    if rd:
        d.append(('README 草稿', 'md', rd[-1], None))
    plans = sorted((p for p in (REP / 'plan').glob('plan_*.md') if '.before_' not in p.name), key=lambda p: p.stat().st_mtime)
    if plans:                                   # newest plan only (older dated plans are superseded)
        d.append(('计划 ' + plans[-1].stem, 'md', plans[-1], None))
    pg = REP / 'pages_20261106b'
    if pg.exists():
        for p in sorted(pg.rglob('*')):
            if p.suffix in ('.html', '.md') and '.before_' not in p.name:
                nm = p.parent.name if p.stem == 'index' else p.stem
                d.append(('页面 ' + nm, 'html' if p.suffix == '.html' else 'md', p, None))
    return [x for x in d if x[2].exists()]

# ---------------------------------------------------------------- result sources
SOURCE_DIRS = ['351_stage10', '361_stage11', '371_stage12', '381_stage13', '391_groups',
               '351_all', '351_stage4_artifacts', '351_stage5_crossed_v2', '351_stage6', '351_stage7_1', '351_stage7_1B_terminal',
               '351_stage7_2', '351_stage7_3', '351_stage7_4', '351_stage8', '351_stage9', '351_provenance_audit',
               '351_self100_split_half', '351_self100_validation', '351_self100_gold_false', '361_stage11_realcheck',
               'labels_20261015', 'public_neuronpedia']   # audit_20261105 left out: it copies numbers from the documents
# paths (relative to JL) that are documents or scratch, not results
EXCLUDE_RE = re.compile(r'(^|/)(raw|reports/(stage1_11|talk|talk_docs|methods|merged_deck|downloads|github|plan|numcheck|advisor|'
                        r'process_report|method_figs|tools|pages_\d+\w*)|__pycache__|\.git)(/|$)'
                        r'|(^|/)partial(/|$)|tiny|unittest|smoke|(^|[/_])test(_|/|\.|$)|\.before_|SUPERSEDED|backup|_bak|\.bak', re.I)

# ---------------------------------------------------------------- features
CN_MAP = [('目标', 'target'), ('对照', 'control'), ('护栏', 'guard'), ('全部', 'all'), ('输出', 'final'), ('最终', 'final'),
          ('真标题', 'true'), ('假标题', 'false'), ('无标题', 'delete'), ('删去标题', 'delete'), ('恢复', 'recovery'), ('替换', 'patch'),
          ('阻断', 'knockout'), ('敲除', 'knockout'), ('斜率', 'slope'), ('先验', 'prior'), ('姓', 'surname'), ('首字母', 'initial'),
          ('名字先验', 'prior'), ('引用档', 'bin'), ('档内', 'within'), ('区间', 'ci'), ('相关', 'spearman'), ('注意力', 'attn'),
          ('名字位置', 'names'), ('冒号', 'colon'), ('第一作者', 'first'), ('年份', 'year'), ('领域', 'field'), ('标题特异', 'spec'),
          ('主题', 'topic'), ('总量', 'total'), ('命中', 'top10'), ('前 10', 'top10'), ('前10', 'top10'), ('名次', 'rank'),
          ('分子', 'num'), ('分母', 'den'), ('团队', 'team'), ('未写出', 'unwritten'), ('写出', 'written'), ('积分', 'integrated'),
          ('配对', 'pair'), ('逐对', 'pair'), ('随机', 'random'), ('文本基线', 'text'), ('检索', 'retrieval'), ('探针', 'probe')]
WORD_ALIASES = {'vanilla': 'logit', 'jacobian': 'jlens', 'j-lens': 'jlens', 'jlens': 'jlens', 'output': 'final', 'mlp': 'mlp',
                'attention': 'attn', 'surnames': 'surname', 'recover': 'recovery', 'recovered': 'recovery', 'ρ': 'spearman',
                'rho': 'spearman', 'knock': 'knockout', 'patching': 'patch', 'patched': 'patch', 'targets': 'target',
                'controls': 'control', 'initials': 'initial', 'titles': 'title', 'papers': 'papers', 'fita': 'fita',
                'self100': 'self100', 'public': 'public', 'probe': 'probe', 'ridge': 'probe'}
EXP_RE = re.compile(r'(?<![A-Za-z0-9])(E[1-4]b?|P[1-3]|N[12]|F[12]|M[1-5][bc]?|X[1-7][a-z]?|C[1-5]b?|B[12][A-C]?|RQ[1-3]|R[0-2]|U0|8[A-E]|'
                    r'7\.[1-4]B?|Exp\s?\d)(?![A-Za-z0-9])')
STAGE_RE = re.compile(r'(?:Stage|stage|阶段)\s?(\d{1,2}(?:\.\d)?[A-E]?)')
LAYER_RE = re.compile(r'(?<![A-Za-z0-9])L(\d{1,2})(?![0-9])')
WORD_RE = re.compile(r'[a-zA-Z][a-zA-Z0-9]{2,}')
PATH_RE = re.compile(r'((?:\d{3}_[A-Za-z0-9_]+|labels_\d+)(?:/[A-Za-z0-9_.\-]+)+)')
STOP = {'the', 'and', 'for', 'with', 'from', 'csv', 'json', 'md', 'parquet', 'summary', 'reports', 'report', 'mean', 'diff', 'not', 'are',
        'that', 'this', 'all_', 'html', 'data', 'per', 'its', 'was', 'were', 'has', 'have', 'than', 'into', 'only'}


def text_feats(t):
    """Feature tokens of a piece of document text or a source label."""
    f = set()
    for m in LAYER_RE.finditer(t):
        f.add('l%d' % int(m.group(1)))
    for m in EXP_RE.finditer(t):
        f.add('x:' + m.group(1).replace(' ', '').lower())
    for m in STAGE_RE.finditer(t):
        f.add('stage' + m.group(1).lower().split('.')[0].rstrip('abcde'))
    for cn, en in CN_MAP:
        if cn in t:
            f.add(en)
    tl = t.lower()
    for w in WORD_RE.findall(tl):
        if w in STOP:
            continue
        f.add(WORD_ALIASES.get(w, w))
    if 'j-lens' in tl or 'jacobian' in tl:
        f.add('jlens')
    if 'final' in f:
        f.add('l63')
    return f


def path_feats(rel):
    """Feature tokens of a result file path (relative to JL)."""
    f = set()
    m = re.search(r'\d{3}_stage(\d+)', rel)
    if m:
        f.add('stage' + m.group(1).split('_')[0])
    if rel.startswith('391_groups'):
        f.add('groups')
    stem = rel.rsplit('/', 1)[-1]
    for part in re.split(r'[/_.\-]+', rel):
        p = part.lower()
        if len(p) >= 3 and p not in STOP and not p.isdigit():
            f.add(WORD_ALIASES.get(p, p))
        if re.fullmatch(r'(e[1-4]b?|p[1-3]|n[12]|f[12]|m[1-5][bc]?|x[1-7][a-z]?|c[1-5]b?|b[12][a-c]?|rq[1-3]|r[0-2]|8[a-e])', p):
            f.add('x:' + p)
    m = re.search(r'stage(7)_(\d)', rel)
    if m:
        f.add('x:7.' + m.group(2))
    m = re.search(r'stage8([A-E])', rel)
    if m:
        f.add('x:8' + m.group(1).lower())
    return f


def col_feats(c):
    f = set()
    cl = str(c).lower()
    for part in re.split(r'[^a-z0-9]+', cl):
        if len(part) >= 3 and part not in STOP:
            f.add(WORD_ALIASES.get(part, part))
        if part in ('lo', 'low', 'lower', 'hi', 'high', 'upper'):
            f.add('ci')
    m = re.match(r'l(\d{1,2})$', cl)
    if m:
        f.add('l%d' % int(m.group(1)))
    return f


# ---------------------------------------------------------------- numbers
NUM_RE = re.compile(r'\d[\d,]*(?:\.\d+)?(?:[eE][\-−+]?\d+)?')


def parse_num(s):
    """'9,108' -> (9108.0, 0); '+0.207' handled by caller; returns (value, decimals)."""
    s2 = s.replace(',', '').replace('−', '-')
    v = float(s2)
    if 'e' in s2.lower():
        return v, None
    dec = len(s2.split('.')[1]) if '.' in s2 else 0
    return v, dec
