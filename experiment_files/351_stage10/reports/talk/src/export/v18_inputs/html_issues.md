# HTML slides of deck v17: source tags, issues

html_tags.json: 97 entries on 34 slides (1, 3, 4, 6, 7, 13–20, 23, 29, 31–34, 39, 41, 42, 45, 46, 49, 51, 52, 57–63).
All entries apply cleanly with deck_tools.apply (each `old` is unique in its section). Every changed slide was rendered and checked. Nothing overflows or overlaps.
Tags start with a zero-width space so that the line can break before "(".

## Method SVG pages (class "mf")
On slides 6, 16, 19, 20, 23, 34, 45, 46, 61, 62 and 63 the source is a small grey footnote `<text class="src">` at the bottom of the SVG, not an inline tspan. Inline tspans would collide with the drawing (right-aligned values, values inside boxes, rank tables). Each footnote names every data value on its page. Slide 46: the footnote is moved to x=390 so it does not hit the formula box.
Checked directly in the raw data:
- The Coifman ranks on slides 19 and 34 match 351_stage10/raw/[cond_*/]final/L63 and raw/logit/L*/shard_011.npz, rows 25025–25031. "Co" is row 25029. The values: 37,675 / 3,979 / 44,676 / 120,750 / 23,169 / 9,811 / 120 / 61.
- Slide 62, word overlap 0.222 / 0.143: config/x3_lexical_neighbour_j2.csv (paper 28578a60…).
- Slide 23, M2 year R² 0.383 / 0.561: summary_cpu_teamci/M2_teamci.csv.
- Slide 45, X6 R values: x6_report.md "all" table, average column.
- Slide 46, X7 S values: x7_report.md "all" table.
- Slide 61, X1 R values: x1_report.md, test table.
Slide 5 (the legend) and slide 26 have no tags. Slide 26 was left out on request: it is being changed to schematic numbers, and post-defence 391_groups numbers are not tagged.

## Not tagged (not data values)
- Settings and thresholds: slide 8 (model and hardware settings); seeds; the 0.5 / 0.1 guards; "≤10% floor"; "< 30: dropped"; "2,000 draws"; "20,000 bootstrap draws"; "R ≥ 0.5 / ≥ 0.95" on slide 65.
- Layer names used as places; slides 2, 5, 12, 30, 40, 50, 64 and 65 (65 holds only layer ranges and thresholds; its numbers are in the X5 image).

## E4b (probe on the title position)
- Slide 39: the tag says "E4b, scores only the first name token".
- Slide 23: the footnote says "probe scores ONLY THE FIRST NAME TOKEN".
- Slide 58 ("probe … from L24") has no number, so no tag.

## Mismatches
1. FIXED, slide 42: the 7.2 seven-layer interval read [−0.012, +0.228]. The original interval had no source file. The recomputed value in 351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv is [−0.012, +0.229], which the report and the handbook use. The slide now says +0.229, tagged "recomputed 10-30".
2. NOT FIXED (text, not a number), slide 18: "Scripts not yet archived: not a completed experiment" is out of date. Report v27 §8E says 8E was recomputed in full from raw logits on 2026-10-30. The scripts are in ~/jlens_work/08_stage8/recompute_2026-10-30/ and the results in 351_stage8/recompute_2026-10-30/ (s8_8E_weighting_by_paper.csv, s8_unsourced_intervals.csv). Suggest changing the line to "recomputed 2026-10-30 from raw logits".
3. Rounding only, all consistent with the sources:
   - Slide 13: L62 +1.08 [0.36, 1.82] (file: 1.077 [0.363, 1.816]).
   - Slide 31: Top-10 overlap 0.36 (file: 0.355).
   - Slide 29: +0.21 [0.20, 0.22] (file: 0.207 [0.195, 0.220]).
   - Slide 14: the "+9.3 pp [4.7, 13.9]" interval is the 2026-10-30 recompute ([+4.77, +14.00]). The original interval had no source file.

## Sources not found
None. Every tagged number was traced to a file, or to a report-v27 / handbook passage that names the file.
Slide 33, the figcaption "Fit A 4/100, Fit B 0/100" is tagged "351_stage9 checkpoints". The report lists this checkpoint in appendix B with a sha256, but I did not open the checkpoint file itself.
