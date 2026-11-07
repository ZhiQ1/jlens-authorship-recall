"""Export methods_handbook.html to A4 PDF (2026-11-06 b header). usage: export_pdf_20261106b.py OUT.pdf"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
SRC = Path(__file__).parent / 'methods_handbook.html'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    pg.goto(SRC.as_uri(), wait_until='networkidle', timeout=300000); pg.emulate_media(media='print'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1500)
    hdr = '<div style="font-size:8px;color:#5B6474;width:100%;padding:0 12mm;display:flex;justify-content:space-between"><span>Stage 1–13 方法手册 · 2026-11-06 b</span><span></span></div>'
    ftr = '<div style="font-size:8px;color:#5B6474;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
    pg.pdf(path=sys.argv[1], format='A4', print_background=True, scale=0.8, display_header_footer=True, header_template=hdr, footer_template=ftr,
           margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm'))
    b.close()
print('wrote', sys.argv[1])
