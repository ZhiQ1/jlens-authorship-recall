"""2026-11-06 b: batch-1 status / results (user-confirmed wording, as report v29 b) in the talk documents that mention batch 1.
progress_report_for_advisor_zh.html: redo-programme sentence and the E4b limitation line; stage13_script_zh_en.html: one box (zh + en) with X1-X4 all authors
and E4b five false titles. The other four talk docs do not mention batch 1 and are unchanged. Backups *.before_20261106b.html (always the input).
Grey source tag (file name) after each conclusion. PDFs: python edit_talkdocs_20261106b.py --pdf -> downloads/talkdoc_*_20261106b_A4.pdf"""
import shutil, sys, re
from pathlib import Path
D = Path(__file__).parent
S = lambda t: f'<span class="src">（{t}）</span>'
SE = lambda t: f'<span class="src">({t})</span>'
OLD_REDO = ('重做计划（补充 10–13，规则都在看结果前写定）进行中：已完成 X7 五个假标题、补充 9 全部名字 token 的 probe、CPU 项 C-1 到 C-5；'
            'X1–X4 全部作者、P1/P2 五个假标题、E4b 减 5 个假标题还在运行（批次 1）；Stage 9 Fit B 与 holdout 等在批次 2（补充 11、12）。')
NEW_REDO = ('重做计划（补充 10–14，规则都在看结果前写定）进行中：已完成 X7 五个假标题' + S('b1_x7f_report.md') + '、补充 9 全部名字 token 的 probe' + S('e4b_alltok.md')
            + '、CPU 项 C-1 到 C-5' + S('c13_C1.md–c13_C5.md') + '；批次 1 的 X1–X4 全部作者（结论都不变）' + S('b1_xall_report.md')
            + '和 E4b 减 5 个假标题（L40 姓首 token +0.076 [0.068, 0.083]，4,654 篇）' + S('b1_e4b5_report.md') + '也已完成，C-3b 只作敏感性分析' + S('c13_C3b.md')
            + '；P1/P2 五个假标题还在运行（194 个单元已完成 116 个）。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）代码和测试已完成，批次 1 结束后自动开始；批次 3（补充 14）代码在写。')
E4B5_ZH = ('E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题）：L40 姓首 token +0.076 [0.068, 0.083]，姓 − 首字母 +0.033 [0.023, 0.042]，原 E4b 第一个 token +0.066；置换对照首字母仍 +0.018，其余 ≈ 0；硬检查 E4b L40 +0.0609 PASS'
           + S('补充 10 第 4 项；381_stage13/reports/b1_e4b5_report.md') + '。按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正（L40 +0.030，L56 +0.058）；只用 false_0、样本较小时，L56 前不显著' + S('同上，per-donor target − control 表') + '。')
XALL_ZH = ('X1–X4 改为给全部作者打分（全部名字 token），并按作者排位分层。结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]）；X3 改写标题保留约 90% 的作者偏好，target 与 control 一样；X4 从 L8 起可解码出作者，各作者排位相同，认得出的论文在 L8–L40 更高；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释。X2 用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009），H3 仍证据不足'
           + S('补充 10 第 1 项，硬检查 PASS；381_stage13/reports/b1_xall_report.md') + '。')
XALL_EN = ('Batch 1 (2026-11-06): X1–X4 re-scored on all authors and all name tokens, stratified by author position — conclusions unchanged (X1 task-independent, small L48 author − year +0.024 [0.019, 0.030]; X3 keeps about 90%; X4 from L8; X2 with an all-author subspace moves 0.032 but still decodes almost nothing, held-out R² ≤ 0.009, so H3 stays insufficient)'
           + SE('b1_xall_report.md') + '. E4b minus five false titles (per-donor exclusion, 4,654 papers): surname first token at L40 +0.076 [0.068, 0.083], surname − initial +0.033; surname target − control positive from L24 (L40 +0.030, L56 +0.058)'
           + SE('b1_e4b5_report.md') + '. P1 / P2 with five false titles still running.')
EDITS = {
 'progress_report_for_advisor_zh.html': [(OLD_REDO, NEW_REDO),
   ('减 5 个假标题平均的版本还在运行。</li>', '减 5 个假标题平均的版本（2026-11-06 完成）：' + E4B5_ZH + '</li>')],
 'stage13_script_zh_en.html': [],
}
if __name__ == '__main__':
    for fn, eds in EDITS.items():
        p = D / fn; b = D / fn.replace('.html', '.before_20261106b.html')
        if not b.exists(): shutil.copy2(p, b)
        s = b.read_text(encoding='utf-8')
        for a, c in eds:
            n = s.count(a); assert n == 1, (fn, n, a[:50]); s = s.replace(a, c)
        if fn == 'stage13_script_zh_en.html':
            a = '<p class="upd">Addendum 9'; i = s.index(a); j = s.index('</p>', i) + 4
            s = s[:j] + '\n<p class="upd">2026-11-06（批次 1）：' + XALL_ZH + E4B5_ZH + 'P1/P2 五个假标题还在运行。</p>\n<p class="upd">' + XALL_EN + '</p>' + s[j:]
        assert not re.search('minyan', s, re.I) and '.upd{' in s
        p.write_text(s, encoding='utf-8'); print('updated', fn)
    if '--pdf' in sys.argv:
        from playwright.sync_api import sync_playwright
        out = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads')
        with sync_playwright() as pw:
            br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 1000, 'height': 1400})
            for fn in EDITS:
                pg.goto((D / fn).as_uri(), wait_until='networkidle', timeout=120000); pg.emulate_media(media='print'); pg.wait_for_timeout(800)
                o = out / ('talkdoc_' + fn.replace('.html', '_20261106b_A4.pdf'))
                pg.pdf(path=str(o), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', o.name)
                pg.emulate_media(media='screen')
                el = pg.locator('p.upd:has-text("2026-11-06（批次 1）"), li:has-text("2026-11-06 完成")').last
                el.screenshot(path=str(D / ('chk_20261106b_' + fn.replace('.html', '.png'))));
                if fn.startswith('progress'): pg.locator('p:has-text("重做计划（补充 10–14")').first.screenshot(path=str(D / 'chk_20261106b_progress_redo.png'))
            br.close()
