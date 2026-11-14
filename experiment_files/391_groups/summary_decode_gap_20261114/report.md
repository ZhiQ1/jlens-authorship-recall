# Decode-gap check for group A (post hoc, descriptive, 2026-11-14)

**Status: post hoc and descriptive.** This analysis is not in any preregistered plan. It uses stored Stage 10 data only (CPU, no GPU).

- Script: ~/jlens_work/14_groups/decode_gap_20261114.py (+ .sbatch).
- Full run: job 11866766 (2000 team-bootstrap draws).
- Tiny test: job 11866759 (50 draws; output in 391_groups/test_decode_gap_20261114_tiny/).

## What was measured
- **Position:** the first generation decision. The prompt is `...titled "<title>" (<year>)?\nAuthors:`, a plain completion with no chat template. The scored token is the first author's first name token.
- **Readout:** the final output (L63), with teacher forcing.
  - rank = 1 + the number of logits strictly greater than the gold logit. Ties favour the gold token.
  - Only top-1 was stored, so the winning token is the stored top1.
- **Conditions:** the true title, 5 false titles, and delete (title removed).
- **Groups:** from papers_used.csv (Addendum 7). The main rows use papers whose first author was not written. This covers all of A, B and U0. C has 310 such papers; the 197 with a written first author are reported separately.
- **Name format:** the role of the gold token (the Stage 10 X1_by_format classification): initial_first (the gold token is a single letter) or given_first.
- **CIs:** 95% team-cluster bootstrap (archived folds_own9108_k5s13 teams, 2000 draws, seed 391).
- **Self-check:** rank==1 matches top1==gold in 99.4% of papers; the 55 disagreements are ties.

## T1. Rank of the true first-author first token, first author unwritten (true title)
| group | n | r1 | 2-5 | 6-20 | 21-100 | >100 | r<=5 [CI] | median |
|---|---|---|---|---|---|---|---|---|
| A | 4104 | .080 | .217 | .343 | .232 | .127 | .298 [.283,.312] | 13 |
| B | 2183 | .069 | .180 | .338 | .232 | .182 | .249 [.230,.267] | 15 |
| C (1st unwritten) | 310 | .061 | .213 | .326 | .281 | .119 | .274 [.226,.327] | 13.5 |
| U0 | 2001 | .073 | .205 | .354 | .212 | .155 | .278 [.257,.299] | 13 |
| D (1st unwritten) | 25 | .120 | .120 | .200 | .400 | .160 | .240 (n<30) | 28 |
| C (1st written, ref) | 197 | .198 | .335 | .284 | .157 | .025 | .533 | 5 |
| R2s (1st written, ref) | 189 | .312 | .407 | .212 | .063 | .005 | .720 | 3 |

## T2. By name format (first author unwritten)
| group | format | n | r1 | 2-5 | 6-20 | 21-100 | >100 | r<=5 [CI] | median |
|---|---|---|---|---|---|---|---|---|---|
| A | initial | 3120 | .095 | .266 | .408 | .218 | .013 | .361 [.344,.378] | 9 |
| A | given | 964 | .034 | .064 | .133 | .282 | .487 | .099 [.078,.118] | 96 |
| B | initial | 1507 | .098 | .239 | .435 | .218 | .011 | .336 [.313,.359] | 9 |
| B | given | 664 | .006 | .045 | .122 | .264 | .563 | .051 [.035,.068] | 137.5 |

## T2b. Share at rank <= 5 by condition
| group | format | true | false (mean) | delete | true-false [CI] |
|---|---|---|---|---|---|
| A | all | .298 | .209 | .269 | .089 [.077,.101] |
| A | initial | .361 | .263 | .343 | .097 [.082,.113] |
| A | given | .099 | .035 | .037 | .063 [.045,.082] |
| B | all | .249 | .219 | .237 | .029 [.015,.044] |
| B | initial | .336 | .298 | .326 | .038 [.019,.056] |
| B | given | .051 | .042 | .038 | .009 [-.004,.025] |

- In A, 450 of the 892 papers with gold rank 2-5 are also at rank <= 5 with the title deleted.
- Only 265 of the 4104 A papers (6.5%) are at rank <= 5 with the true title and above rank 5 under all 5 false titles.

## T3. What beats the gold token at rank 2-5 (A, n = 892)
- **Another initial:** 53.6%. ' M' alone is 227 of the 829 initial_first cases.
- **Another name-like word:** 19.3%. These are mostly common given names such as David, John and James.
- **A true co-author's first token:** 16.5% (B 9.2%, C 33%).
- **A word starting with the gold letter:** 6.5%. This is often the full given name; the category is a heuristic and also catches non-names such as " Mass".
- **The true first author's surname token:** 3.5%.
- **Punctuation or whitespace:** < 1%.

Two more facts about these winners:
- 70% are among the 20 most frequent author-initial tokens in the cohort (B 84%).
- Only 15% are the model's own top-1 with the title deleted.

The median gold logprob is -3.4 (p ≈ 0.03).

## T4. A - B in the share at rank <= 5 (first author unwritten)
- **Raw:** +.049 [.026, .072].
- **Within each format:**
  - initial_first +.024 [-.005, .055]
  - given_first +.047 [.021, .073]
- **Format-standardised:** +.029 [.006, .052], so format accounts for about 41% of the raw gap.
- **Within citation bin:** +.063 [.038, .089].
- **Within citation bin x format:** +.047 [.022, .072], so format accounts for about 25% of the within-bin gap.

Format matters because B has more given_first first authors (30.4% vs 23.5%), and those rarely reach rank 5.

## T5. Caveat: A papers with the gold token already at rank 1
- **Count:** 329 of 4104 (8.0%): 296 initial_first and 33 given_first.
- **Without the title:** 8.1% are at rank 1 with the title deleted, so these are mostly the name prior, not knowledge of the paper.
- **Comparison groups:** B 6.9%, U0 7.3%.

Few A papers are at rank 1, so the teacher-forced first step does not contradict R0. This does not show that the label run's prompt matches Stage 10.

## Answer
**H_dec is not supported as the main explanation.**
- **The rank 2-5 band is mostly the name prior.** It is about as common in B and U0 and with the title deleted. It consists mostly of single-letter initials, and the tokens that beat the gold token are common initials and given names.
- **The title-driven part is small.** It adds about 9 percentage points to the share at rank <= 5 against false titles and about 3 against delete. Overall, about 5-10% of A papers fit H_dec.
- **Some H_dec-like cases exist.** In 16.5% of the A cases at rank 2-5 the winner is a true co-author's token, and in 6.5% it is a word starting with the gold letter. These look like knowledge choosing the wrong author or form first.
- **For full given names, the knowledge is weak.** Median rank is 96 and 49% are above rank 100. There is still a clear title effect that B lacks.

**The A > B gap is about 5 points.** Name format accounts for about 25-40% of it.

## Caveats
- **Different generation run.** The labels come from another run (prompt, sampling and thinking mode unknown).
- **Initials are cheap.** A single-letter initial near the top says little.
- **First author and first token only.** Ranks use bf16 logits and ties favour the gold token.
- **Top-k was not stored.** A full recompute would take 9,108 prompts x 7 conditions, one forward pass each at the last position: about 1-2 A100-80GB GPU hours (not run).
- **Heuristic categories.** The winner categories are heuristics.
- **No multiplicity correction.**
