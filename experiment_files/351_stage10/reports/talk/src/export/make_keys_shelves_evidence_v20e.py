"""2026-11-07 c copy of make_keys_shelves_evidence_v20.py: pages from the lossless deck v20e (three parts), tables v29_en (H1 colon ratio, H3 R² ≤ 0.009, all-author X2). Output downloads/keys_and_shelves_evidence_v20e.pdf."""
"""2026-11-06 b: 'Keys and shelves 证据页' (short deck for talks) = deck v20 slides matching v16 slides 48, 8, 4, 7, 9, 16, 30, 18, 37, 38, 35, 36, 27, 28, 29
(in this order; mapping from reports/talk/v16_to_v20_page_map.csv, direct counterparts only, not the 'new in v17' method pages) + the three
English hypothesis-table images v28 (stage1_11/src/hyp_table_png_v28_en.py). Pages are taken from downloads/Stage1-13_deck_v20b_slides.pdf
(v20 b = v20 with slides 72/75/81 updated; none of the selected slides changed). Output: downloads/keys_and_shelves_evidence_v20.pdf (1280x720 landscape)."""
import csv, sys
from pathlib import Path
import fitz
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'
V16 = [48, 8, 4, 7, 9, 16, 30, 18, 37, 38, 35, 36, 27, 28, 29]
M = {}
for r in csv.DictReader(open(R / 'talk/v16_to_v20_page_map.csv', encoding='utf-8')):
    if r['v20'].isdigit(): M.setdefault(int(r['v16']), []).append((int(r['v20']), r['title (v20)']))
missing = [v for v in V16 if v not in M]; assert not missing, ('no v20 counterpart', missing)
assert all(len(M[v]) == 1 for v in V16), {v: M[v] for v in V16 if len(M[v]) != 1}
src = fitz.open()
for f in ['Stage1-13_deck_v20e_slides_part1of3_p1-27.pdf', 'Stage1-13_deck_v20e_slides_part2of3_p28-55.pdf', 'Stage1-13_deck_v20e_slides_part3of3_p56-82.pdf']:
    src.insert_pdf(fitz.open(D / f))
assert len(src) == 82
out = fitz.open(); W, H = src[0].rect.width, src[0].rect.height
for v in V16:
    n, t = M[v][0]; out.insert_pdf(src, from_page=n - 1, to_page=n - 1); print(f'v16 {v:>2} -> v20 {n:>2}  {t}')
for k in ['tableonly', 'slide', 'wide']:
    img = D / f'Stage13_hypotheses_table_v29_en_{k}.png'; pix = fitz.Pixmap(str(img))
    pg = out.new_page(width=W, height=H); s = min((W - 60) / pix.width, (H - 60) / pix.height)
    w, h = pix.width * s, pix.height * s; pg.insert_image(fitz.Rect((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2), filename=str(img)); print('image', img.name)
o = D / 'keys_and_shelves_evidence_v20e.pdf'; out.save(o, deflate=True, garbage=3); print('saved', o, len(out), 'pages')
for i in (0, 6, 15, 17):
    out[i].get_pixmap(dpi=50).save(str(R / f'talk/src/export/shots/v20e/ks_p{i + 1:02d}.png'))
