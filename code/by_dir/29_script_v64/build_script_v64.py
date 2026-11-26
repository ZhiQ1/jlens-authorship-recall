#!/usr/bin/env python3
"""Build ~/jlens_work/script_stage1_13_v64.md (main speaker script) in the HTML v68 order.
A = spoken (EN line, ZH line), from A_p01..A_p06.py (user-approved style, 2026-11-23).
B = 备查: the previous script's full page text (verbatim, incl. every 【】 note, kept on the same slide) or,
for new v68 pages, the slide's full visible text + the number-source file.
Version / maintenance notes go to the changelog, not into pages."""
import json, re, sys, importlib.util, os
W = '/home/zhang.zhiqi2/jlens_work/'
V = W + '27_v67/'
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, W + 'tools')
from prepublish_check import html_slides, visible_text

DOCNOTES = json.load(open(D + 'doc_only_notes.json', encoding='utf-8'))
A = {}
for k in range(1, 7):
    spec = importlib.util.spec_from_file_location('a%d' % k, D + 'A_p%02d.py' % k)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); A.update(m.A)

deck = html_slides('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')   # live HTML v70 (161 slides)
m67 = json.load(open(V + 'renumber_map.json'))['v66_to_v67']
m68 = json.load(open(V + 'renumber_map_v68.json'))['v67_to_v68']
inv = {}
for a, b in m67.items():
    c = m68.get(str(b))
    if c: inv[int(c)] = int(a)
pmap = json.load(open(V + 'pptx_map_v22t_v68.json'))   # v22s->v22t (v22u keeps v22t numbering)
pu = json.load(open(V + 'pptx_map_v22u_v70.json'))
pfirst = pu['v70_to_v22u_first']; pall = pu.get('v70_to_v22u_all', {})

old = open(W + 'script_stage1_13_v63.md', encoding='utf-8').read()
parts = re.split(r'(?m)^(## .*)$', old)
pages = {}
extra_after = {}      # old P -> list of (heading, body) pptx-only blocks that followed it
overview = None
lastp = None
for j in range(1, len(parts) - 1, 2):
    m = re.match(r'## P(\d+) ', parts[j])
    if m:
        lastp = int(m.group(1)); pages[lastp] = (parts[j], parts[j + 1])
    elif parts[j].startswith('## pptx S'):
        extra_after.setdefault(lastp, []).append((parts[j], parts[j + 1]))
    elif parts[j].startswith('## 总览'):
        overview = (parts[j], parts[j + 1])
spec = importlib.util.spec_from_file_location('ap', D + 'A_pptx.py')
mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp); AP = mp.A
s2t = pmap['v22s_to_v22t']

toc, part_of, part_names = {}, {}, []
cur = None
for l in open(V + 'toc_v68.md', encoding='utf-8'):
    l = l.rstrip('\n')
    if l.startswith('## '):
        cur = l[3:].strip(); part_names.append(cur)
    m = re.match(r'(\d+)\. (.*)$', l.strip())
    if m:
        n = int(m.group(1)); toc[n] = re.sub(r'\s+\(v67 p\d+\)$', '', m.group(2)).replace('★ ', '')
        part_of[n] = cur
toc[161] = 'Backup B23 · Earlier evidence-matrix layouts (superseded)'; part_of[161] = part_of.get(160)

def numbers_file(n):
    if n in (38, 51, 52, 53, 54, 55) or 77 <= n <= 83: return '27_v67/fragments/part34_numbers.md'
    if n == 84 or 104 <= n <= 109 or 124 <= n <= 127: return '27_v67/fragments/part56_numbers.md'
    if 130 <= n <= 139: return '27_v67/fragments/part7_numbers.md'
    if n == 34: return 'same fit as slide 24 (exposure test)'
    return None

def pptx_ref(n):
    s = pall.get(str(n)) or ([pfirst[str(n)]] if str(n) in pfirst else [])
    if not s: return 'pptx — (v22u pending)'
    s = sorted(set(int(x) for x in s))
    return 'pptx S%s (v22u)' % (str(s[0]) if len(s) == 1 else '%d–S%d' % (s[0], s[-1]) if s[-1] - s[0] == len(s) - 1 else ', S'.join(map(str, s)))

out = ['# Qwen3-32B 把论文作者放在哪里？—— Stage 1–13 逐页讲稿（按 HTML deck 新顺序）', '',
       '每页两块：**要说的话**（念出来，一句英文一句中文，约 1 分钟）和 **备查（不念）**（完整数字、CI、n、公式、证据强度、出处、内部编号；上一版讲稿的全文和当时各检验的判定原样保留在这里）。'
       '用户本人的方括号笔记逐字保留在原来那张幻灯片的页里。版本与维护说明见修改日志。', '',
       '比喻全程只用一套：索书号（这是哪一篇论文）vs 书脊上的主题（标题的意思）；编造标题 = 一张写着同样主题、但不属于这本书的卡片。', '']
if overview:
    out += [overview[0] + '（上一版讲稿开头的总览，备查，不念）', overview[1].rstrip('\n'), '']
missing = []
lastpart = None
for i, key, s, ti in deck:
    if part_of.get(i) != lastpart:
        lastpart = part_of.get(i); out += ['', '# ' + (lastpart or ''), '']
    title = toc.get(i, ti or key)
    out.append('## P%d · HTML v70 p%d · %s — %s' % (i, i, pptx_ref(i), title))
    out.append('')
    if str(i) in DOCNOTES:
        out.append('**你在讲稿 doc 里写的批注（从 doc 原样搬来，原在上一版本页的标题下面）：**')
        out.append('')
        out.append(DOCNOTES[str(i)])
        out.append('')
    out.append('**要说的话（一句英文一句中文）**')
    if i not in A: missing.append(i)
    for en, zh in A.get(i, []):
        out.append(en); out.append(zh)
    out.append('')
    o = inv.get(i)
    if o:
        body = pages[o][1].strip('\n')
        out.append('**备查（不念）· 上一版讲稿本页全文（原第 P%d 页；其中的判定是当时那项检验的锁定判定，用户的方括号笔记原样保留）：**' % o)
        out.append('')
        out.append(body)
    else:
        vt = re.sub(r'\s+', ' ', visible_text(s)).strip()
        out.append('**备查（不念）· 本页幻灯片全文（数字、CI、n、公式、证据强度）：**')
        out.append('')
        out.append(vt)
        nf = numbers_file(i)
        if nf: out.append(''); out.append('数字出处：' + nf)
    out.append('')
    for h, b in (extra_after.get(o, []) if o else []):
        code = re.match(r'## pptx (S\d+)', h).group(1)
        b2 = b
        mcur = re.search(r'（主 pptx 当前页码：S(\d+)；HTML deck 无对应页。）', b2)
        if mcur:
            newp = s2t.get(mcur.group(1))
            b2 = b2.replace(mcur.group(0), '（主 pptx 当前页码：S%s；HTML deck 无对应页。）' % newp, 1)
        out.append(h.rstrip())
        out.append('')
        out.append('**要说的话（一句英文一句中文）**')
        for en, zh in AP.get(code, []):
            out.append(en); out.append(zh)
        out.append('')
        out.append('**备查（不念）· 上一版讲稿本页全文（用户的方括号笔记原样保留）：**')
        out.append(b2.strip('\n'))
        out.append('')
open(W + 'script_stage1_13_v64.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('pages', len(deck), 'A missing', missing)
