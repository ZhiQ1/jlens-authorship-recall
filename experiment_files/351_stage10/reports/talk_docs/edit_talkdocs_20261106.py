"""2026-11-06: update the six talk documents (redo programme, addenda 9-13; same approved wording as report v29). Backups *.before_20261106.html
(edits always start from them). Grey source tags (class src) on every new number. Then export each to PDF: python edit_talkdocs_20261106.py --pdf"""
import shutil, sys, re
from pathlib import Path
D = Path(__file__).parent
CSS = '<style>.src{color:#8a8f98;font-size:.78em;font-weight:400}.upd{border-left:4px solid #2F7D3B;padding:6px 12px;margin:10px 0;background:rgba(47,125,59,.06)}</style>'
S = lambda t: f'<span class="src">（{t}）</span>'
SE = lambda t: f'<span class="src">({t})</span>'
R13 = '381_stage13/reports/'
AT_ZH = ('补充 9（答辩后新增，分析计划在看结果前写定）把这个 probe 扩展到每位作者的全部名字 token 并按角色分开：L40 姓的第一个 token +0.071 [0.058, 0.085]'
         + S('目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；' + R13 + 'e4b_alltok.md') + '，高于首字母 +0.044 [0.030, 0.057]' + S('1,590 篇') + '；名的第一个 token 最强（L40 +0.124、L56 +0.163'
         + S('1,706 篇') + '）。原 E4b 只打分第一个 token（多半是首字母），所以低估了标题位置携带的名字信息。')
AT_EN = ('Addendum 9 (post-defence, plan fixed before the results) extends the probe to every name token by role: surname first token at L40 +0.071 [0.058, 0.085]'
         + SE('1,395 papers; e4b_alltok.md') + ', above the initial +0.044 [0.030, 0.057]; the given-name first token is strongest (L40 +0.124, L56 +0.163). E4b scored only the first token, mostly an initial, so it underestimated the name information at the title.')
X7_ZH = ('2026-11-06：X7 补做了另外 4 个假标题，按 5 个平均判定，target、control 和全部论文都满足预注册判据（S(L52) 分别为 +0.022、+0.042、+0.028，均 ≤ 0.05）'
         + S('补充 10 第 2 项；' + R13 + 'b1_x7f_report.md') + '；原来对照组只用 false_0 时为 0.051，属于单个假标题的波动。')
REDO = ('重做计划（补充 10–13，规则都在看结果前写定）进行中：已完成 X7 五个假标题、补充 9 全部名字 token 的 probe、CPU 项 C-1 到 C-5；'
        'X1–X4 全部作者、P1/P2 五个假标题、E4b 减 5 个假标题还在运行（批次 1）；Stage 9 Fit B 与 holdout 等在批次 2（补充 11、12）。')

EDITS = {
 'experiment_walkthrough_methods_zh.html': [
  ('配合 PPT v16 和报告 v26 使用。', '配合 PPT v20 和报告 v29 使用（2026-11-06 更新：补充 9、X7 五个假标题等重做结果已加入）。'),
  ('target 比 control 高 +0.04 到 +0.08；两个置换对照', 'target 比 control 高 +0.03 到 +0.08；两个置换对照'),
  ('而且只打分了第一个 token（73% 是首字母）、只减了 false_0，是辅助证据。</p>', '而且只打分了第一个 token（73% 是首字母）、只减了 false_0，是辅助证据。</p>\n<p class="upd">' + AT_ZH + '</p>'),
  ('L52 起挡 target 0.018、control 0.051；L56 起都是 0。</p>', 'L52 起挡 target 0.018、control 0.051；L56 起都是 0。</p>\n<p class="upd">' + X7_ZH + '</p>')],
 'experiment_walkthrough_zh.html': [
  ('数字都是定稿版（报告 v26）。', '数字都是定稿版（报告 v26）；2026-11-06 起与报告 v29 一致，重做计划的新结果用绿色框标出。'),
  ('target 比 control 高 +0.04 到 +0.08。换成别的论文', 'target 比 control 高 +0.03 到 +0.08。换成别的论文'),
  ('所以它是辅助证据，主要证据还是替换实验。</p>', '所以它是辅助证据，主要证据还是替换实验。</p>\n<p class="upd">' + AT_ZH + '</p>')],
 'keys_and_shelves_script_zh_en.html': [
  ('target 比 control 高 +0.04 到 +0.08。原版标准化', 'target 比 control 高 +0.03 到 +0.08。原版标准化'),
  ('target exceeds control by +0.04 to +0.08;', 'target exceeds control by +0.03 to +0.08;'),
  ('而且主要来自首字母这种信息量很少的 token。</p>', '而且主要来自首字母这种信息量很少的 token。' + AT_ZH + '</p>')],
 'methods_handbook_guide_plain_zh.html': [
  ('<td>X2 只替换子空间</td>\n<td>暂停</td>\n<td>“答辩前不做”</td>',
   '<td>X2 只替换子空间</td>\n<td>2026-11-05 已完成（补充 6）：H3 按规则通过、H2 不支持，但作者子空间几乎解码不出作者，搬动量只有完整替换的约 4%' + S(R13 + 'x2_report.md') + '</td>\n<td>“X2 不能作为 H3 的有力证据”</td>'),
  ('<td>停在 66/100，不补做</td>', '<td>停在 66/100；已列入重做计划（补充 12 第 2-1 项，批次 2）</td>'),
  ('<td>Stage 9B 留出集比较、9C 影响因素分析</td>\n<td>没做</td>\n<td>“列入计划但未执行”</td>',
   '<td>Stage 9B 留出集比较、9C 影响因素分析</td>\n<td>9B 列入重做计划（补充 12 第 2-1 项，批次 2）</td>\n<td>“列入重做计划，尚未运行”</td>'),
  ('<td>M5</td>\n<td>没做</td>\n<td>“部分由 X4 覆盖，其余放弃”</td>',
   '<td>M5</td>\n<td>能用已有数据回答的部分 2026-11-05 已在 CPU 上做完；名字位置的 probe / patchscope 列入补充 11、12</td>\n<td>“CPU 部分已完成，GPU 部分在重做计划里”</td>'),
  ('<li>只打分第一个 token，而 73% 的作者第一个 token 是首字母，首字母几乎不带标题特异信号。所以它测的是信号最弱的那部分。</li>',
   '<li>只打分第一个 token，而 73% 的作者第一个 token 是首字母，首字母几乎不带标题特异信号。所以它测的是信号最弱的那部分。' + AT_ZH + '</li>')],
 'progress_report_for_advisor_zh.html': [
  ('<td>实验记录 v26（主报告）</td>', '<td>实验报告（主报告；当前 v29，2026-11-06）</td>'),
  ('<td>汇报 PPT v16（54 页）</td>', '<td>汇报 PPT（当前 v20，82 页）</td>'),
  ('Stage 9 只完成 Fit A；Stage 13 完成 M1–M4、X1、X3–X7，X2 暂停，M5 并入 X4。</p>',
   'Stage 9 只完成 Fit A（Fit B 与 holdout 已列入重做计划）；Stage 13 完成 M1–M4、X1–X7（X2 于 2026-11-05 完成），M5 的 CPU 部分已完成。' + REDO + '</p>'),
  ('target 比 control 高 +0.04 到 +0.08。原版标准化', 'target 比 control 高 +0.03 到 +0.08。原版标准化'),
  ('<li>局限：只给每位作者的第一个名字 token 打分（73% 是首字母），只减了一个假标题。</li>',
   '<li>局限：只给每位作者的第一个名字 token 打分（73% 是首字母），只减了一个假标题。' + AT_ZH + '减 5 个假标题平均的版本还在运行。</li>'),
  ('<li>读出工具的拟合稳定性只有 Stage 9 Fit A 一份证据，Fit B 未完成。</li>', '<li>读出工具的拟合稳定性只有 Stage 9 Fit A 一份证据；Fit B 与 holdout 已列入重做计划（补充 12，批次 2），尚未运行。</li>')],
 'stage13_script_zh_en.html': [],
}

if __name__ == '__main__':
    for fn, eds in EDITS.items():
        p = D / fn; b = D / fn.replace('.html', '.before_20261106.html')
        if not b.exists(): shutil.copy2(p, b)
        s = b.read_text(encoding='utf-8')
        for a, c in eds:
            n = s.count(a); assert n == 1, (fn, n, a[:50]); s = s.replace(a, c)
        if fn == 'stage13_script_zh_en.html':
            i = s.index('不能作为 H3 的有力证据。'); j = s.index('</p>', i) + 4
            s = s[:j] + '\n<p class="upd">' + AT_ZH + X7_ZH + '</p>\n<p class="upd">' + AT_EN + '</p>' + s[j:]
        s = s.replace('</style>', '</style>' + CSS, 1)
        assert not re.search('minyan', s, re.I)
        p.write_text(s, encoding='utf-8'); print('updated', fn)
    if '--pdf' in sys.argv:
        from playwright.sync_api import sync_playwright
        out = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads')
        with sync_playwright() as pw:
            br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1000, 'height': 1400})
            for fn in EDITS:
                pg.goto((D / fn).as_uri(), wait_until='networkidle', timeout=120000); pg.emulate_media(media='print'); pg.wait_for_timeout(800)
                o = out / ('talkdoc_' + fn.replace('.html', '_20261106_A4.pdf'))
                pg.pdf(path=str(o), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', o.name)
            br.close()
