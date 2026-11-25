# Addendum 23 — exploratory supplement (post hoc; the locked result stays unchanged)

582 test papers (288 target, 294 control), the locked freeze, prompts and class vocabularies; team bootstrap 2,000, seed 23.
Code ~/jlens_work/18_h1lock/a23_supp.py; jobs 12071684 (tiny), 12078209 (shard 0 + attention diagnostic), 12078376 (shards 1–11), 12079049 (analysis).
GPU ≈ 0.25 h.

## 1. Sink set (fixed from the shard-0 diagnostic before shards 1–11)
Mean attention of the ":" query to position 0 (the first token of the prompt), averaged over heads: L0 0.01, L8 0.83, L16 0.73,
L24 0.80, L32 0.78, L40 0.63, L48 0.62, L56 0.92. Position 0 is the top key at L8, L24, L32, L40 and L48. Sink set = {0}.

## 2. Gentle knockout and sink-only control (authors question; first-token class measure as in the locked test)
| from layer l | 4 | 8 | 16 | 24 | 32 | 40 | 48 | 56 | none |
|---|---|---|---|---|---|---|---|---|---|
| locked test A, ":" isolated (sink cut) | 0.10 | 0.01 | 1.00 | 0.43 | 0.34 | 0.13 | 0.81 | 0.96 | 1.00 |
| locked secondary, question positions blocked (position 0 also blocked) | 0.56 | 0.58 | 0.66 | 0.65 | 0.75 | 0.89 | 0.98 | 0.99 | 1.00 |
| **gentle: question words blocked, title + sink visible** | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| **sink-only: ":" sees itself + position 0** | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
Target and control are identical within 0.01 at every layer.

Reading: the drops in the locked test A (L24–L40) and the low early values of the locked secondary knockout come from cutting
the attention sink at position 0, not from the format still being read from the question words. With the sink kept, blocking
the question words (or even everything except the sink) from L4 on leaves the names format intact. By the locked rule applied to
these curves, the authors format would count as "fixed early" (by L4). Caveat: the names class is the default answer type (it
also carries 28% of the first-token mass under the year question and 19% under the field question, see 4), so "intact names
format" partly reflects a strong default rather than a question-specific setting.

## 3. Year / field with the first content token after the line break
Baseline accuracy: authors 0.985 [0.974, 0.993], year 0.804 [0.770, 0.837], field 0.053 [0.036, 0.073]. Year and field stay
below 0.90, so stage 2 (gentle knockout + patching with the content measure) was not run, as specified. The year and field
knockout curves (first-token measure) are in a23_supp_table.csv; they are not interpretable (baseline < 0.90; K above the
unblocked value at several layers).

## 4. Explanations for the locked result
(a) Non-monotonic K and L56. Locked rule: X = the smallest layer l with K(l′) ≥ 0.95 (CI lower ≥ 0.90) for EVERY l′ ≥ l.
K(L16) = 1.00 does not qualify because K falls again at L24 (0.43), L32 (0.34) and L40 (0.13); L48 = 0.81 also fails; L56 = 0.96
[0.94, 0.97] and "none" = 1.00 both pass, so X = L56. Section 2 shows the dip is the sink cut.
(b) Direction naming of test B. In "q>d" the recipient prompt is q and the donor colon state comes from d (same paper):
- authors>year = authors prompt receiving the year-question ":" state: S(L48) 0.51, S(L56) 0.78;
- year>authors = year prompt receiving the authors ":" state: S = 1.00 from L48;
- field>authors = field prompt receiving the authors ":" state: switch from L40.
(c) The L48 asymmetry (1.00 vs 0.51). Mean first-token class masses at ":" without intervention:
| prompt | name | year | field |
|---|---|---|---|
| authors | 0.810 | 0.007 | 0.0001 |
| year | 0.276 | 0.349 | 0.0001 |
| field | 0.188 | 0.018 | 0.074 |
Names are a strong competitor even under the year and field questions, while the year class never gets much mass under the
authors question. Moving the year prompt to names only needs to tip 0.28 over 0.35; moving the authors prompt to year has to
overcome 0.81. The asymmetry therefore largely reflects this class-mass imbalance (names as the default answer type), not a
difference in when each format is fixed.

## 5. Bottom line (exploratory)
With the attention sink kept, the authors format at ":" survives blocking of the question words from L4 on; the locked "fixed
only late (L56)" reflects the destructive isolated-colon knockout. Year and field remain not interpretable with either measure.
