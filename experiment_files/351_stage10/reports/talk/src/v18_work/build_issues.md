# build_v18 — source tags on the image pages (deck pages from build_v18.py)

Source: copy of build_v17_readonly.py -> build_v18.py (the original build.py was not touched).
Runner: run_build_v18.py (HERE = talk/src for charts; paper.png and talk_v18.pptx written only into DIR).
Render: render_v18.sh (build -> soffice PDF -> PyMuPDF 1920x1080 JPEG q88).

## Helper changes (old call signatures unchanged)
- New `_run()`/`_runs()` used by text(), note(), box(): a run whose option dict has `'src': True` is drawn as a
  source tag (Patrick Hand, 11 pt by default, colour 8A8F98, not bold). Plain strings and old run lists work as before.
- `S(text, size=11)` makes a tag run " (text)". `caveat()` draws the one-line red probe caveat.
- `PROBE_CAVEAT` = "Probe scores only the first name token (mostly an initial); all-token, by-role version (addendum 9) in progress."

## Counts
- 47 grey tag runs on 21 pages; 2 visible caveat lines; caveat sentence appended to 2 English notes (no other note changed;
  checked by diffing all new_slide() strings).
- Pages changed (deck page = slides.json `deck`): 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27.
- Not changed: 1–3 (not used as kind=deck images in the HTML deck), 15 (Limits: only layer names / experiment ids, no data values),
  16 (divider), 25 (no numbers on the slide; numbers are only in the chart).

## Numbers checked against result files (all match the slide text)
- p6: public lens L62 title-specific target 0.560 / control 0.235 (351_stage10/summary_title/A_group_layer.csv).
- p10 (notes/graph): E1 recovery L40 0.291, L48 0.825, L52 0.996; E1t 0.12–0.15; E2 loss L0 0.831, L32 0.372, L48 0.064, L52 0.007;
  E2n L0 0.153 (361_stage11/summary/E1_recovery.csv, E1t_recovery.csv, E2_knockout.csv, E2n_knockout.csv).
- p12: tc_prior +0.087, tc_topic −0.047, tc_spec +0.207, surname-first prior +0.022 / spec +0.423 (371_stage12/summary_cpu/A_prior_decomposition.csv);
  rho prior 0.085, spec 0.329, n 8,894 (B_prior_vs_recognition.csv).
- p13: A−B +0.199, C−B +0.372 (C 391 / B 885), C−A +0.110 (485 / 3,204); probe R0 view +0.018…+0.038 (351_stage10/reports/r0_r1_analysis.md §1, §E4b).
- p20: written − missed +0.199 (495 papers), no title +0.097 (351_stage10/summary_r0r1/R1_author_written_minus_missed.csv).
- p4: 79% strict tier = 35,898 / 45,540 (351_stage10/config/conditions_manifest.json tier_summary).
- p5: n_prompts 557 / 100 / 100 (351_stage10/config/lenses.json).
- Others (p7, p8, p11, p17–p19, p21–p24, p26, p27) via the report v27 English source tags (scratchpad/tags/S2–S4.json) and §6.x.

## Unsourced numbers
- None on the slides. Approximations to note: p18 "rank ~10" at L62 (logit −0.93 ≈ rank 8.5, tagged with −0.93);
  p17 "~1e-5" (crosscheck median gap 3e-6 to 6.6e-5).

## Mismatches
- None found that needed fixing. Note: p13 "probe R0 view +0.02 to +0.04" (speaker note) comes from the original Stage 11 E4
  probe (r0_r1_analysis.md §E4b), not from the Stage 13 re-check; slide text itself does not show this number.

## Layout fixes after looking at the renders
- p11: note text size 18 -> 16 (tags made the note overflow its bottom edge). Caveat placed under the chart at y = 6.1.
- p14: row y positions [1.45, 2.32, 3.19, 4.30, 5.17, 6.04] instead of 1.45 + i*0.92 (row "No lens lead" now 3 lines).
- p5: caption tag at 10 pt; p11 subtitle tag at 10 pt.
- p21: caveat placed under the chart at y = 6.3.
- All 21 changed pages viewed after the final build: no overlap or overflow.

## Outputs
- build_v18.py, run_build_v18.py, render_v18.sh, patch_v18.py (edit list), talk_v18.pptx, render/talk_v18.pdf, pages_v18/p01–p27.jpg, paper.png (background copy).
