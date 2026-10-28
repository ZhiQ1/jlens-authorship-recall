"""Export the combined Stage 1-11 report (report/stage1_11_report.html) to an A4 portrait PDF with print rules:
each part and each major section starts on a new page; tables, figures and boxes are not split; backgrounds and the
red/green review markers keep their colours; header = version + export date, footer = page numbers."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent; SRC = HERE.parent / 'report/stage1_11_report.html'; OUT = Path(sys.argv[1]); VER = sys.argv[2]; DATE = sys.argv[3]
PRINT_CSS = '''
@media print {
  html, body { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body { background: #fff !important; }
  .partbar { break-before: page; }
  .p19 > main > section, .p1011 > main > section, .p1011 > section, .ov h2 { break-before: page; }
  .p19 > main > section:first-child, .p1011 > main > section:first-child, .ov h2:first-child { break-before: auto; }
  table, figure, .tbl, .tw, .fig, .bx, .finding, .pair, img, svg, pre, .files { break-inside: avoid; }
  h1, h2, h3, h4 { break-after: avoid; }
  .tw, .tbl, .fig { overflow: visible !important; }
  table { min-width: 0 !important; width: 100% !important; table-layout: auto; }
  .fig svg { min-width: 0 !important; width: 100% !important; max-width: 100% !important; height: auto !important; }
  .p1011, .p1011 main, .p1011 section, .p1011 .pair, .p1011 figure, .p19, .p19 main, .p19 section, .wrap { min-width: 0 !important; max-width: 100% !important; }
  .p1011, .p1011 main { grid-template-columns: minmax(0, 1fr) !important; }
  th, td { white-space: normal !important; overflow-wrap: anywhere; }
  .p1011 .files, .p1011 .mono, .mono { overflow-wrap: anywhere; word-break: break-all; }
}'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1000, 'height': 1400})
    pg.goto(SRC.as_uri(), wait_until='networkidle', timeout=180000)
    pg.add_style_tag(content=PRINT_CSS); pg.emulate_media(media='print'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
    print('fonts', pg.evaluate("[...new Set([...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family))]"), flush=True)
    hdr = f'<div style="font-family:\'Droid Sans Fallback\',sans-serif;font-size:8px;color:#5B6474;width:100%;padding:0 12mm;display:flex;justify-content:space-between"><span>Stage 1–11 实验报告 · 第 {VER} 版</span><span>导出日期 {DATE}</span></div>'
    ftr = '<div style="font-family:\'Droid Sans Fallback\',sans-serif;font-size:8px;color:#5B6474;width:100%;text-align:center">第 <span class="pageNumber"></span> / <span class="totalPages"></span> 页</div>'
    pg.pdf(path=str(OUT), format='A4', print_background=True, scale=0.74, display_header_footer=True, header_template=hdr, footer_template=ftr,
           margin=dict(top='16mm', bottom='14mm', left='12mm', right='12mm'))
    b.close()
print('wrote', OUT)
