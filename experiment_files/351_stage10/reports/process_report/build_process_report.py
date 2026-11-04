"""Build the process report page (index.html) from draft_zh.md: headings, tables, lists, quotes, bold, code,
and 【source】 tags shown as small provenance text. Usage: python build_process_report.py"""
import html, re
from pathlib import Path

D = Path(__file__).parent
txt = (D / 'draft_zh.md').read_text(encoding='utf-8')
for a, b in [('advisor 页', '进度汇报页'), ('### 附：本稿未能找到出处或刻意未写的内容', '### 附：没有找到出处的内容'), ('（素材稿，2026-11-04）', '')]:
    txt = txt.replace(a, b)
md = [l for l in txt.splitlines() if not l.startswith('> 用途：')]


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'【([^】]+)】', r'<span class="src">\1</span>', t)
    return t


out, toc, i, n2 = [], [], 0, 0
while i < len(md):
    line = md[i]
    if line.startswith('# '):
        i += 1; continue                      # page title is written by hand below
    if line.startswith('## '):
        n2 += 1; title = line[3:].strip(); aid = f's{n2}'
        toc.append((aid, title)); out.append(f'<h2 id="{aid}">{inline(title)}</h2>'); i += 1; continue
    if line.startswith('### '):
        out.append(f'<h3>{inline(line[4:].strip())}</h3>'); i += 1; continue
    if line.strip() == '---':
        i += 1; continue
    if line.startswith('|'):
        rows = []
        while i < len(md) and md[i].startswith('|'):
            rows.append([c.strip() for c in md[i].strip().strip('|').split('|')]); i += 1
        head, body = rows[0], [r for r in rows[1:] if not all(set(c) <= set('-: ') for c in r)]
        t = '<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
        t += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table></div>'
        out.append(t); continue
    if line.startswith('> '):
        out.append(f'<p class="note">{inline(line[2:])}</p>'); i += 1; continue
    m = re.match(r'^(\s*)(- |\d+\. )', line)
    if m:
        ordered = m.group(2)[0].isdigit(); items = []
        while i < len(md):
            mm = re.match(r'^(\s*)(- |\d+\. )(.*)$', md[i])
            if not mm: break
            depth = len(mm.group(1)) // 2
            items.append((depth, mm.group(3))); i += 1
        tag = 'ol' if ordered else 'ul'
        h, cur = [f'<{tag}>'], 0
        for depth, txt in items:
            while depth > cur: h.append('<ul>'); cur += 1
            while depth < cur: h.append('</ul>'); cur -= 1
            # "日期｜问题｜原因｜处理｜影响" rows become a labelled block
            if '｜' in txt and txt.count('｜') >= 3:
                p = txt.split('｜'); lab = ['', '问题', '原因', '处理', '对结果的影响']
                body = f'<span class="date">{inline(p[0])}</span> <b>{inline(p[1])}</b>'
                for k in range(2, len(p)):
                    body += f'<br><span class="lab">{lab[k] if k < len(lab) else ""}</span>{inline(p[k])}'
                h.append(f'<li class="issue">{body}</li>')
            else:
                h.append(f'<li>{inline(txt)}</li>')
        while cur > 0: h.append('</ul>'); cur -= 1
        h.append(f'</{tag}>'); out.append(''.join(h)); continue
    if line.strip():
        out.append(f'<p>{inline(line)}</p>')
    i += 1

CSS = (D / 'style.css').read_text(encoding='utf-8')
navs = ''.join(f'<li><a href="#{a}">{inline(t)}</a></li>' for a, t in toc)
page = f'''<title>jlens 实验全过程汇总</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;700&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<main>
<header>
  <p class="eyebrow">jlens · Qwen3-32B 作者记忆 · 过程汇总</p>
  <h1>实验全过程汇总：数据、步骤、HPC 实操、问题与调整</h1>
  <p class="meta">截至 2026-11-04（Stage 1–13 全部完成，git tag defense-2026-11）。每条后面的灰色小字是出处：P = PROGRESS.md 条目日期，S§ = STATUS.md 节号，H = HANDOFF.md，手册 = 方法手册的节，V/U = 手册附录编号。数字照抄来源，没有重算。</p>
</header>
<nav aria-label="目录"><p class="eyebrow">目录</p><ul class="toc">{navs}</ul></nav>
{chr(10).join(out)}
</main>
'''
(D / 'index.html').write_text(page, encoding='utf-8'); print('written', len(page), 'chars;', len(toc), 'sections')
