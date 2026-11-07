"""Load the visible text of every document checked by the strict claims check.
Read-only. Each unit = (doc, file, unit_prefix, text, marks); marks = [(offset, location label)].
Text is whitespace-normalised (runs of whitespace -> one space) so that regexes match across line breaks;
mark offsets are remapped accordingly."""
import json, re, sys, bisect
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from numcheck_extract import html_text, md_text          # reuse the first checker's text extraction (visible text only)

JL = Path('/scratch/zhang.zhiqi2/jlens')
REP = JL / '351_stage10/reports'

def doc_list():
    d = [('报告', 'html', REP / 'stage1_11/stage1_11_report.html'),
         ('PPT', 'deck', REP / 'merged_deck/stage1_11_deck.html'),
         ('方法手册', 'html', REP / 'methods/methods_handbook.html')]
    for p in sorted((REP / 'talk_docs').glob('*.html')):
        if '.before_' not in p.name:
            d.append(('讲稿 ' + p.stem, 'html', p))
    d += [('导师页 advisor', 'html', REP / 'advisor/index.html'),
          ('过程报告 process_report', 'html', REP / 'process_report/index.html'),
          ('打分审计 scoring_audit', 'html', JL / 'audit_20261105/scoring_audit.html'),
          ('方法补遗 methods_addendum', 'html', REP / 'pages_20261106b/methods_addendum/index.html'),
          ('README 草稿 b', 'md', REP / 'github/README_draft_20261106b.md'),
          ('计划 b', 'md', REP / 'plan/plan_master_queue_20261106b.md')]
    return [x for x in d if x[2].exists()]

def _norm(t, marks):
    """collapse whitespace; remap mark offsets."""
    out, mp, n = [], [], 0
    for m in re.finditer(r'\s+|\S+', t):
        s = m.group(0)
        if s[0].isspace():
            if out and out[-1] != ' ':
                out.append(' '); n += 1
            mp.append((m.start(), n))
        else:
            mp.append((m.start(), n)); out.append(s); n += len(s)
    keys = [a for a, _ in mp]
    nm = []
    for o, l in marks:
        k = bisect.bisect_right(keys, o) - 1
        base = mp[k][1] + (o - mp[k][0] if k >= 0 and not t[mp[k][0]].isspace() else 0) if k >= 0 else 0
        nm.append((base, l))
    return ''.join(out), nm

def units():
    U = []
    for doc, kind, path in doc_list():
        if kind == 'html':
            t, m = html_text(path.read_text(encoding='utf-8', errors='replace'))
            U.append((doc, path, '', *_norm(t, m)))
        elif kind == 'md':
            t, m = md_text(path.read_text(encoding='utf-8', errors='replace'))
            U.append((doc, path, '', *_norm(t, m)))
        else:
            h = path.read_text(encoding='utf-8', errors='replace')
            secs = re.split(r'(?=<section class="slide)', h)[1:]
            secs[-1] = secs[-1].split('</section>')[0] + '</section>'
            notes_p = REP / 'talk/src/export/notes_zh.json'
            notes = json.loads(notes_p.read_text())
            for k, sec in enumerate(secs, 1):
                t, m = html_text(sec)
                U.append((doc, path, '第%d页 正文' % k, *_norm(t, [(o, '') for o, l in m[:1]] or [(0, '')])))
                nz = notes.get(str(k), {})
                if nz.get('text'):
                    U.append((doc + ' 备注 notes_zh.json', notes_p, '第%d页 备注' % k, *_norm(nz['text'], [(0, '')])))
    return U

def locate(unit, off):
    doc, path, pre, t, marks = unit
    offs = [o for o, _ in marks]
    k = bisect.bisect_right(offs, off) - 1
    l = marks[k][1] if k >= 0 else ''
    l = re.sub(r'Stage 1–13 实验报告大模型在哪一层“记住”论文作者 > |Stage 1–13 方法手册 > ', '', l)
    return (pre + ' ' + l).strip()

if __name__ == '__main__':
    out = Path(sys.argv[1])
    out.mkdir(exist_ok=True)
    for u in units():
        fn = re.sub(r'[^\w]+', '_', u[0])[:40] + '.txt'
        with open(out / fn, 'a') as f:
            f.write('\n\n#### ' + u[2] + '\n' + u[3])
    print('ok')
