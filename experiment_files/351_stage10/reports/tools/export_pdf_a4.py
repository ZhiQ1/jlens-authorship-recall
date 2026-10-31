"""HTML -> A4 PDF with Chromium (playwright). Usage: python export_pdf_a4.py in.html out.pdf"""
import sys, os
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    pg.goto('file://' + os.path.abspath(src)); pg.wait_for_timeout(3000)
    pg.emulate_media(media='print')
    pg.pdf(path=out, format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm'))
    b.close()
import fitz; d = fitz.open(out); print(out, d.page_count, 'pages', round(os.path.getsize(out) / 1e6, 1), 'MB')
