"""Render the report's three-hypotheses table (v29, 2026-11-07: H3 cell with R² ≤ 0.009 and the all-author X2 refit; date 第 29 版) to PNG: downloads/Stage13_hypotheses_table_v29_tableonly.png (zh)."""
from playwright.sync_api import sync_playwright
SRC = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html'
OUT = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/Stage13_hypotheses_table_v29_tableonly.png'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2)
    pg.goto('file://' + SRC, wait_until='load', timeout=180000); pg.emulate_media(color_scheme='light'); pg.wait_for_timeout(1500)
    el = pg.locator('h3:has-text("三种假设及其预测") + div.tw table').first
    el.screenshot(path=OUT); print(el.bounding_box())
    b.close()
