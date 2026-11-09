"""2026-11-08 c (v30): copy of hyp_table_png_v29_en.py; H2 cell and overall judgement add that the X4 recognition gap is no longer H2 evidence; header report v30. Earlier: 2026-11-07 (v29): ENGLISH versions (H3 cell: author subspace can hardly decode authors, held-out R² ≤ 0.009, all-author refit moves 0.032 ≈ 7% of full patching; header report v29, 2026-11-07). Earlier docstring: 2026-11-06 b: ENGLISH versions of the report's 'three hypotheses' table (v28 content = the table rendered by hyp_table_png_v28.py).
Only a Chinese version existed; this is a sentence-by-sentence English translation of the same cells (same numbers, nothing added),
rendered in three variants like the v22 images: tableonly, slide (title + table + overall judgement, 16:9), wide (title + table, wide page).
Outputs: downloads/Stage13_hypotheses_table_v28_en_{tableonly,slide,wide}.png. The source cells are asserted to be unchanged."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
REP = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html')
OUT = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads')
s = REP.read_text(encoding='utf-8'); i = s.index('<h3>三种假设及其预测</h3>'); j = s.index('</table>', i)
src = re.sub(r'<span class="src">.*?</span>', '', s[i:j])
for frag in ['在 “:” 和名字位置成立；在 L4–L40，“:” 位置换问法时的移动是换论文时的 3–5 倍（L48 为 2.2 倍，L56–L63 为 1.3–1.5 倍）', '目前结果（第 30 版，2026-11-08）', 'X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。', 'BERT +0.088 ≥ Qwen L8 +0.018', 'X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足', '<b>X2 不支持。</b>']:
    assert frag in src, frag          # translation below was made from exactly this table
H = ['Hypothesis', 'M1: top word of the lens in middle layers', 'M2: probe reads non-name attributes', 'M3: change-of-task control', 'Current result (report v30, 2026-11-08)']
ROWS = [
 ['<b>H1 task / format:</b> the middle layers represent “output an author list”', 'mostly “author”, punctuation, common name starts; unrelated to the title',
  'paper attributes not readable or very weak', 'the same title under different questions separates early in the middle layers', 'holds at “:” and name positions; at L4–L40, “:” moves 3–5× more when the question changes than when the paper changes (2.2× at L48, 1.3–1.5× at L56–L63)'],
 ['<b>H2 paper identity:</b> the middle layers represent “which paper this is”', 'title-related words (copied from the title); change with a false title',
  'field, year (inferred from the title), citations and recognition all readable, and earlier than the names',
  'the same paper under different questions is close in the middle layers and separates by task only late<br><b>Result:</b> not above the L4 text level, not supported',
  '<b>M3 does not support it; X3 shows a semantic representation beyond wording in the middle layers, but it cannot be separated from paper identity; H2 currently rests on M2 and X1, and M2’s Qwen-over-BERT advantage is reference only (addendum 2).</b> Also, the earliest decodable order in X4 is first author (L8) before year (L40), opposite to the H2 prediction; the X4 recognised − control difference in first-author D (not significant on test) is no longer counted as H2 evidence (text-only BERT baseline +0.088 not weaker than Qwen L8 +0.018). <b>X2 does not support it.</b>'],
 ['<b>H3 author information already there, just not in vocabulary directions</b>', 'not necessarily', 'the authors’ first token readable by the probe, not by the lens',
  'an author-trained probe transfers across tasks; an author-specific lens (M4) reads names in the middle layers',
  '<b>Text baseline not weaker than Qwen, a text explanation cannot be excluded: insufficient evidence</b> (X4: on the given-name first token BERT +0.088 ≥ Qwen L8 +0.018; the L8 signal sits mainly on the surname, see X4); <b>X2 passes by rule, but the author subspace can hardly decode authors (held-out R² ≤ 0.009; refit on all authors it moves 0.032, about 7% of full patching): still insufficient</b>']]
JUDGE = ('<b>Overall (2026-11-03): H2 partly supported but not established; H3 insufficient evidence.</b> H2 support comes from M2 (paper attributes readable at the title) and X1 (replacement effect independent of the question); '
         'M3 does not support it, X3 cannot separate meaning from paper identity, the X4 order is opposite to the H2 prediction, X2 does not support it (2026-11-05). v30: the X4 recognition gap is no longer counted as H2 evidence (text-only BERT baseline +0.088 not weaker than Qwen L8 +0.018). H3: X2 passes by rule, but the author subspace hardly decodes authors, so the evidence is still insufficient.')
assert '总体判断（2026-11-03）：H2 部分支持但未确立，H3 证据不足。' in s
NOTE = 'English translation of the report table (Stage 1–13 report v30, 2026-11-08, part 4 “三种假设及其预测”); numbers unchanged. Sources: 381_stage13/reports/m3_report.md, x1_report.md, x3_report.md, x4_report.md, x4_textbase2.md, x2_report.md, b1_xall_report.md, x1_similarity.md (colon table).'
CSS = ('body{margin:0;background:#fff;font-family:"Source Sans 3","Noto Sans",system-ui,sans-serif;color:#1B2433}'
       '.wrap{padding:28px 32px}h1{font-size:30px;margin:0 0 14px}table{border-collapse:collapse;width:100%;font-size:17px;line-height:1.42}'
       'th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid #D9DEE6}th{font-weight:700;border-bottom:2px solid #1B2433}'
       'td:first-child{width:17%}td:nth-child(5){width:32%}p{font-size:16px;line-height:1.45;margin:14px 0 0}.n{color:#8a8f98;font-size:13px}')
def page(title, judge, width):
    th = ''.join(f'<th>{c}</th>' for c in H); tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in ROWS)
    t = f'<h1>{title}</h1>' if title else ''
    return (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;700&display=swap"><style>{CSS}</style>'
            f'<div class="wrap" id="w" style="width:{width}px">{t}<table id="t"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'
            + (f'<p>{JUDGE}</p>' if judge else '') + f'<p class="n">{NOTE}</p></div>')
tmp = OUT.parent / 'stage1_11' / 'src' / '_hyp_en_tmp_v30.html'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1500, 'height': 1000}, device_scale_factor=2)
    for name, title, judge, w, sel in [('tableonly', '', False, 1380, '#t'), ('slide', 'Three hypotheses and their predictions', True, 1380, '#w'),
                                       ('wide', 'Three hypotheses and their predictions', False, 1460, '#w')]:
        tmp.write_text(page(title, judge, w), encoding='utf-8'); pg.goto(tmp.as_uri(), wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        o = OUT / f'Stage13_hypotheses_table_v30_en_{name}.png'; pg.locator(sel).screenshot(path=str(o)); print(o.name)
    b.close()
tmp.unlink()
