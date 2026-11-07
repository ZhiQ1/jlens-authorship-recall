"""2026-11-06 b (user request): merge the two advisor progress reports into ONE current page.
Base = advisor/index.html (= https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs, already carrying the 2026-11-06 update box and flags from
edit_pages_20261106b.py). Brought in from the talk doc progress_report_for_advisor_zh.html (= https://claude.ai/artifact/8XcY8CRpz3AAjfDE4n6V6e):
its section 七 "自查中发现并修正的问题" table and section 九 "待确认" + "可能的下一步" (verbatim; superseded items flagged, nothing renumbered).
The talk doc gets a prominent "superseded" line at the top (content otherwise unchanged). Backups *.before_merge_20261106b.*.
Usage: python merge_advisor_20261106b.py [--pdf]"""
import re, shutil, sys
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); H = R / 'pages_20261106b'
A = R / 'advisor/index.html'; T = R / 'talk_docs/progress_report_for_advisor_zh.html'
def bk(p):
    b = p.with_name(p.stem + '.before_merge_20261106b' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)
FLAG = lambda t: f'<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：{t}；见页首更新框〕</span>'
SRC = lambda t: f'<span style="color:#8a8f98;font-size:.8em">（{t}）</span>'

a = bk(A); t = bk(T)
assert '2026-11-06 更新：答辩后的重做计划' in a, 'run edit_pages_20261106b.py first'
# --- pieces from the talk doc
i = t.index('<h2>七、自查中发现并修正的问题</h2>'); j = t.index('</div>', i) + 6
tab = t[t.index('<table>', i):t.index('</table>', i) + 8]
tab = re.sub(r'\s*\n\s*', '', tab)
tab = tab.replace('<td>X6、X7 补做，结论成立</td>', '<td>X6、X7 补做，结论成立' + FLAG('X7 已按 5 个假标题平均重判，三组都成立') + '</td>')
i9 = t.index('<p><strong>待确认</strong>：</p>'); j9 = t.index('<hr>', i9)
nxt = t[i9:j9].strip()
nxt = rep(nxt, '<li>补完 Fit B，加固读出工具的稳定性证据。</li>', '<li>补完 Fit B，加固读出工具的稳定性证据。' + FLAG('Fit B 与 holdout 已列入批次 2（补充 12 第 2-1 项），代码已就绪，批次 1 结束后自动开始') + '</li>')
nxt = nxt.replace('<strong>', '<b>').replace('</strong>', '</b>')
# --- merged page
a = rep(a, '数字均可在实验记录 v26 和方法手册中追到出处文件。</p>',
        '数字均可在实验记录 v26 和方法手册中追到出处文件。</p>\n  <p class="meta"><b>2026-11-06 合并更新：</b>本页与讲稿版《给老师的进度汇报》合并为一个当前版本（加入了讲稿版的“自查中发现并修正的问题”表和“下一步”）；答辩后的结果见下方更新框。讲稿版不再单独更新。</p>')
SELF = ('\n  <h3>自查中发现并修正的问题（汇总表，来自讲稿版进度汇报第七节）</h3>\n  <div class="tw">' + tab + '</div>\n'
        '  <p class="small">出处：讲稿版进度汇报（https://claude.ai/artifact/8XcY8CRpz3AAjfDE4n6V6e）第七节；各条的详细记录与出处文件见方法手册附录 G4（V01–V62）和实验全过程汇总（https://claude.ai/artifact/TmqEtZg3gHTz7p7vCkaiB4）第 6 节。本表各行没有逐行列出结果文件。</p>\n')
k = a.index('<h2>复核中发现并改正的问题</h2>'); k2 = a.index('</section>', k)
a = a[:k2] + SELF + a[k2:]
NEXT = ('<section>\n  <h2>待确认与下一步（来自讲稿版进度汇报第九节）</h2>\n  ' + nxt + '\n  <p class="small">“可能的下一步”是建议，没有数据支撑，不是结论。</p>\n</section>\n\n')
a = rep(a, '<section>\n  <h2>材料</h2>', NEXT + '<section>\n  <h2>材料</h2>')
assert a.count('<table>') >= 1 and not re.search('minyan', a, re.I)
A.write_text(a, encoding='utf-8')
# --- superseded talk doc
BAN = ('<div style="border:2px solid #B3261E;background:#FDECEA;color:#B3261E;padding:12px 16px;margin:0 0 16px;font-size:18px;font-weight:700">'
       '本页已过时，最新内容见 <a href="https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs">https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs</a></div>\n')
t2 = rep(t, '<h1>项目进度汇报：Qwen3-32B 在哪一层“记住”论文作者</h1>', BAN + '<h1>项目进度汇报：Qwen3-32B 在哪一层“记住”论文作者</h1>')
T.write_text(t2, encoding='utf-8'); print('merged advisor page and superseded banner written')

if '--pdf' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1000, 'height': 1400})
        for src, name, shots in [(A, 'jlens_progress_report_2026-11-06b_A4.pdf', [('h3:has-text("自查中发现并修正的问题")', 'chk_merged_selfcheck.png'), ('h2:has-text("待确认与下一步")', 'chk_merged_next.png')]),
                                 (T, 'talkdoc_progress_report_for_advisor_zh_20261106b_A4.pdf', [('text=本页已过时', 'chk_talkdoc_superseded.png')])]:
            pg.goto(src.as_uri(), wait_until='networkidle', timeout=120000); pg.wait_for_timeout(800)
            for sel, png in shots:
                pg.locator(sel).first.scroll_into_view_if_needed(); pg.screenshot(path=str(H / png))
            pg.emulate_media(media='print')
            pg.pdf(path=str(R / 'downloads' / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name)
            pg.emulate_media(media='screen')
        br.close()
