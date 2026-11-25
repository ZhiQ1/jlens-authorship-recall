# Pre-registration addendum 34 — LOCKED: H1 format locking with a shared answer ending ("Answer:")

Locked 2026-11-25 18:01 EST (UTC−05:00), user-approved; nothing has been run on real-model data.
Status: LOCKED 2026-11-25, written before any data of this test (no pilot, no tiny test, no GPU job). The user approved the
text and resolved all open choices (section 15). The prompt format and (only under rule 4.2) the measure are selected by the
pre-lock pilot of section 4, by the selection rule fixed in this text; the selected format, field lexicon and sink set are
recorded in the pilot freeze file before any main-sample data. Lock file: `prereg_addendum34.md.sha256`.
Draft history: `prereg_addendum34_DRAFT.md` (unchanged).
Supplements addendum 23 (locked, done) and its exploratory supplement (summary_a23_supp); does not change their results.

## 1. Question and hypotheses
Problem with addendum 23: its prompts end in "Authors:" / "Year:" / "Field:". Under that ending, writing names is the
default answer type (names carry 0.81 of the first-token class mass under the authors prompt, but also 0.28 under the year
and 0.19 under the field prompt; year / field baseline type accuracy 0.63 / 0.11 (first-token measure) and 0.80 / 0.05
(first content token)). A flip of the answer type therefore cannot be seen cleanly, and the locked L56 result came from a
knockout that also cut the attention sink (position 0).

Question: with three prompts that end in exactly the same tokens ("Answer:"), so that the answer type is set only by the
question words, from which layer is the answer type fixed at the "Answer:" positions, so that later layers no longer re-read
it from the question words?

- H1-lock (main): there is a layer Λ from which replacing the "Answer:" states of a prompt with those of another question
  (same paper) flips the answer type to the donor's type, at every later tested layer.
- H1-early-copy (secondary): with the attention sink kept, blocking the "Answer:" positions from the question words from
  layer l on leaves the answer type intact from some layer X_g on.
- Sink artefact (secondary, confirms the a23 supplement): the a23 dip at L24–L40 came from cutting the sink, i.e. "sink kept,
  everything else cut" retains the type better than "everything cut" at L24–L40.
Current H1 wording (canonical_matrix.md): "downgraded: ':' follows the question; the format layer is not pinned down".

## 2. Prompts (wording fixed now; format chosen by the pilot, section 4)
Question strings (equal token length, 7 tokens each including the "?" token, checked for all 9,108 cohort titles in both
formats F1/F2: 0 titles give unequal lengths; median prompt length 31 tokens, max 92):
- authors: `who are the authors of it?`
- year: `in what year was it published?`
- field: `in what research field is it?`
(The user's example "who are the authors?" is 2 tokens shorter than the other two; with unequal lengths the swapped states
would sit 2 positions away from their original position. "of it" is added only to equalise length; decision D2, section 15.)

Candidate formats, tried in this order (raw text, no chat template, no BOS — as in addenda 23/26):
- F1 (user's option A): `Paper: "{t}". Question: {q}\nAnswer:`
- F2 (user's option B, question directly before the final label on the same line): `Paper: "{t}".\nQuestion: {q} Answer:`
- F3 = F1 with the instruction line `Answer with a short phrase only.\n` in front
- F4 = F2 with the same instruction line in front
- F5 = F1 preceded by a balanced 3-shot block: one solved example per question type (authors / year / field), three exemplar
  papers from the cohort that are in neither the pilot nor the main sample (`group == 'guard'`, fixed by seed 34 at freeze),
  exemplar order rotated over the 6 permutations by paper index mod 6; exemplar answers = cohort ground truth (authors as in
  the Stage 10 name format, year from `year`, field = cohort `field` label). The block is identical for the three questions
  of a paper, so donor and recipient share it.
{t} = true title, no year. Same format for all three questions of a paper; only {q} differs.

## 3. Token positions (real Qwen3-32B tokenisation, rev 9216db57, checked on CPU 2026-11-25)
Example (title "Deep Residual Learning for Image Recognition"), F1 authors, T = 22 with the equal-length wording:
`Paper | : | ␠" | Deep | ␠Res | idual | ␠Learning | ␠for | ␠Image | ␠Recognition | ". | ␠Question | : | ␠who | ␠are | ␠the |
␠authors | ␠of | ␠it | ?\n | Answer | :`. In F1 "?" and the line break merge into one token "?\n"; the last two tokens are
always `Answer`, `:`. F2: `... ".\n | Question | : | ␠who ... ␠it | ? | ␠Answer | :` (last two always `␠Answer`, `:`).
F3/F4 add 7 tokens in front (`Answer | ␠with | ␠a | ␠short | ␠phrase | ␠only | .\n`).
- Answer span A = the last two positions {T−2, T−1} ("Answer", ":"), identical tokens in all three prompts; aligned from the
  end (with the equal-length wording the absolute positions are also identical).
- Final colon = T−1 (note: position 1 is also a ":" token, after "Paper"; it is never meant by ":" in this addendum).
- Question words Q = every token overlapping the character span of {q} (7 tokens: from "who"/"in" up to and including the
  "?\n" (F1) or "?" (F2) token). The "Question:" label and everything before {q} cannot see {q} (causal attention), so they
  carry no question information; the only positions after Q are A. Blocking A → Q therefore removes every route by which
  question information reaches A after layer l.
- Title tokens = tokens overlapping the title span (as addendum 23; about 26% of titles end in a token that merges the last
  title character with `".`, this token counts as title).
- Sink set = {0} (first prompt token: "Paper" in F1/F2, "Answer" of the instruction line in F3/F4, first exemplar token in
  F5), unless the pilot attention diagnostic (section 4) finds another key with mean attention from ":" ≥ 0.30 at ≥ 3 of
  the tested layers; then that key is added. Fixed before lock.
Freeze asserts per paper: the three prompts have equal length, identical last two tokens, |Q| identical across questions.

## 4. Pre-lock pilot (feasibility; sample disjoint from the main sample)
Sample: 150 papers from the `tune` split of `381_stage13/config/pairs.parquet` (the addendum 23 sampling frame; the main
sample is the `test` split), 75 target + 75 control, stratified by field, seed 34. Never used in the main analysis.
Per format F1–F5 and question: unpatched greedy answer (both measures of section 7), the "no question" floor (A blocked from
Q from layer 0, sink kept; shows whether a default type remains), and for the first passing format an eager-attention sink
diagnostic on 10 papers (mean attention from ":" to each key at L0–L63). One GPU job for all five formats.
Stopping rule (applied by a CPU gate, written now):
1. Primary measure (section 7.1): select the first format in the order F1 → F5 whose correct-type rate is ≥ 0.90 for all
   three questions (point estimate on the 150 pilot papers). Stop there.
2. If no format passes: apply the same rule with the sensitivity measure (section 7.2). If a format passes, it is selected
   and the candidate-scoring measure becomes primary (the first-content-word measure becomes the sensitivity); this switch
   is written into the locked text.
3. If neither passes: stop, no main run; report the pilot table to the user. New formats beyond F1–F5 need user approval
   (one more pilot round at most).
Reported, not part of the rule: per-format rates with Wilson CIs, "other" share, the no-question floor (if one type takes
≥ 0.80 of the floor, flag a strong default and read direction asymmetries with that caveat), mean prompt length, cost/paper.
The field lexicon of section 7.1 is frozen from the pilot answers before lock.

## 5. Main test: swap of the "Answer:" states
Recipient prompt q, donor prompt d ≠ q, same paper, same format. At layer l, replace the recipient's block-l output at both
positions of A with the donor's block-l output at the same (end-aligned) positions; layers after l run normally, so the
recipient's A positions can still read the recipient's own question words. All 6 ordered pairs (authors←year,
year←authors, authors←field, field←authors, year←field, field←year; notation "q←d" = q receives d's state; addendum 23's
"q>d" means the same). Layers L_swap = {4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60}.
Per paper and layer the answer type τ ∈ {name, year, field, other} (section 7). Denominator: papers whose unpatched
recipient AND unpatched donor answers have the correct type (excluded share reported; all papers = sensitivity).
- Flip rate S_{q←d}(l) = share with τ = type(d).
- Retention R_{q←d}(l) = share with τ = type(q); other O(l) = 1 − S − R.
- ΔF(l) (continuous, from the scoring measure) = [ln s_q − ln s_d](patched) − [ln s_q − ln s_d](base).
Lock rule (per ordered pair): Λ_{q←d} = the smallest l in L_swap such that for every l′ ≥ l in L_swap:
 (a) R(l′) ≤ 0.10 with the upper bound of the Bonferroni-adjusted interval ≤ 0.20 (the user's "S(l) below threshold" read as
     "the recipient's own type no longer survives the swap"), and
 (b) S(l′) ≥ 0.80 with the adjusted lower bound ≥ 0.70 (the swap transfers the donor type, not just breaks the output), and
 (c) both controls of section 5.1 change the type in ≤ 0.10 of papers at l′.
Interval level 1 − 0.05/6 (Bonferroni over the 6 ordered pairs; percentiles 0.42 / 99.58 of the team bootstrap).
If (a) holds but (b) fails at some l′ ≥ l: "lock without clean transfer" (output broken, O high) for that pair.
Λ is also recomputed in every bootstrap draw → percentile interval of Λ and of the asymmetry Λ_{q←d} − Λ_{d←q}.
Sensitivity (same rule, reported): swap of the final ":" only (comparable with addendum 23), at L_swap ∩ {4, 8, 16, 24, 32,
40, 48, 56}.

### 5.1 Controls (should not flip)
- Same-question swap: A states taken from a different paper under the SAME question (donor paper = the next paper in the
  frozen order within the same group and field). Type-change rate C_same(l) = share with τ ≠ type(q). Expected ≈ 0.
- Random-state swap: recipient A state + a Gaussian random vector rescaled, per layer and position, to ‖donor_d − recipient‖
  (d = the year question for authors/field recipients, authors for year recipients); seed 34. C_rand(l) as above.
- Layers: {8, 16, 24, 32, 40, 48, 56}; for (c) at layers without a control value the nearest lower control layer is used.

## 6. Secondary test: gentle knockout and sink control
From layer l to L63, change only the attention of the A queries (both positions), all heads; additive mask as in addendum 23.
Arms (per question q):
- K_gentle: A cannot attend to Q; sink, title, prefix, "Question:" label and A itself stay visible.
- K_sinkonly: A attends only to the sink set and to A (causal) — the user's "keep the sink, cut everything else".
- K_iso: A attends only to A (sink cut too) — the addendum 23 primary knockout, now on the new format.
Layers L_ko = {0, 4, 8, 16, 24, 32, 40, 48, 56} plus 64 (= explicit mask, nothing blocked). K_arm(l) = share keeping
τ = type(q) (denominator: papers with correct unpatched type). l = 0 = the "no question" floor.
- Early-copy layer X_g(q) = smallest l in L_ko with K_gentle(l′) ≥ 0.95 and adjusted lower bound ≥ 0.90 for every
  l′ ≥ l (addendum 23 rule; interval level 1 − 0.05/3, Bonferroni over 3 questions).
- Sink effect (confirmatory, Holm over the 3 questions, one-sided α = 0.05): D_sink(q) = mean over l ∈ {24, 32, 40} of
  [K_sinkonly(l) − K_iso(l)] > 0; bootstrap p = share of draws ≤ 0.

## 7. Measurement (one fixed now as primary; pilot rule 4.2 may switch it, nothing else may)
### 7.1 Primary (recommended): first content word of the greedy answer
Greedy continuation after "Answer:" (no KV cache, as a23_supp), up to 8 new tokens, stop early once classified. Decoded text
→ words; skip leading words from a fixed list (the, a, an, this, it, its, paper, article, was, is, are, were, published,
written, by, in, on, the field, field, of, year, research, authors, author, answer, and punctuation / quotes). First
remaining word w:
- year: w starts with a digit;
- name: w is an initial (`^[A-Z]\.$`, `^[A-Z]\.[A-Z]\.$`, `^[A-Z]$` followed by "."), or w is in the name lexicon (every
  given name and surname in the cohort author lists, case-sensitive) and not in the field lexicon;
- field: w (lower-cased) is in the field lexicon = words of the 8 cohort labels + the first words of the pilot's field
  answers that are not digits and not in the name lexicon (frozen before lock, listed in the freeze file);
- other: anything else (counts as wrong type).
Reason for recommending it: it is what the model would actually write (the user's question "does the answer type flip"),
it does not depend on whether the model knows the paper's true answer (so target and control are measured the same way),
and it is already implemented and tested in a23_supp (`gen_first_content`). Weak point: lead-in sentences and the field
lexicon; the pilot measures both ("other" share).
### 7.2 Sensitivity: candidate scoring, maximum over the three types
Candidates per paper = the first 3 tokens of the model's own unpatched greedy answer to each of the three questions (same
paper, same format), so all candidates have equal length and none needs ground truth. Score s_c = sum of teacher-forced
log-probabilities of candidate c after the (patched) prompt; τ = type of argmax_c s_c (never "other"). Gives the continuous
ΔF. Weak point: baseline accuracy is close to 1 by construction (own greedy path), so the baseline check rests on 7.1.
### 7.3 Ground truth (descriptive only; not needed for τ)
Year = cohort `papers.parquet` column `year` (OpenAlex publication year frozen in the cohort); field = cohort `field` (8
OpenAlex top-level labels); authors = cohort author list. Reported: unpatched content accuracy (year exact and ±1; field
label word match; any true surname in the first 8 tokens), per group.
Baseline type accuracy (both measures, per question, with CIs) is reported on the main sample; a question with main-sample
primary accuracy < 0.90 makes every pair involving it "not interpretable" (as addendum 23).

## 8. Sample, layers, groups
Main sample: the 582 addendum 23 papers (`pairs.parquet` split = test; 288 target, 294 control), same shard order (shards of
50), so results line up with a23/a26 paper by paper. Precision from a23 (same papers, same bootstrap): S near 0.5 had a 95%
half-width of 0.042 (0.509 [0.467, 0.551]), near 0.95 of 0.016 (0.955 [0.939, 0.971]); design effect vs binomial ≈ 1.07.
With Bonferroni over 6 pairs (z 2.64) the half-widths become ≈ 0.057 at 0.5 and ≈ 0.034 at 0.10 / 0.90, well inside the
margins of the lock rule (0.10 vs 0.20; 0.80 vs 0.70). Target − control differences: half-width ≈ 0.06–0.08 at 0.5, so
only differences ≥ 0.10 are detectable; target vs control is reported descriptively (pooled for all rules).
The extension by the 446 tune papers not used by the pilot (n = 1,028) is NOT part of this test (decision D5).
Layers: L_swap (15), L_ko (9 + 64), control layers (7) as above.

## 9. Statistics and multiplicity
Team-cluster bootstrap (team ids from pairs.parquet), 2,000 draws, seed 34, percentile intervals. Families:
- M (main): lock rule for the 6 ordered pairs — interval rule with Bonferroni 1 − 0.05/6 (Holm cannot be applied to an
  interval rule; Bonferroni is Holm's first step and conservative).
- S1 (secondary): D_sink for 3 questions — Holm, one-sided α = 0.05.
- S2 (secondary): X_g for 3 questions — Bonferroni 1 − 0.05/3 intervals.
- S3 (secondary): asymmetry Λ_{q←d} − Λ_{d←q} for the 3 unordered pairs — Holm on bootstrap two-sided p (share of draws on
  the other side of 0, ×2).
Everything else (":"-only swap, all-paper denominator, ΔF curves, target vs control, content accuracy) is descriptive.

## 10. Decision table (per ordered pair, then overall)
| result | reading | effect on H1 wording |
|---|---|---|
| pilot fails (no format/measure ≥ 0.90) | not testable with these formats | unchanged; report the pilot |
| question with main-sample accuracy < 0.90, or a control > 0.10 at Λ | not interpretable for the pairs involved | unchanged for those pairs |
| Λ ≤ 16 | type fixed early at "Answer:" | upgrade candidate: "the answer position takes on the asked format from early layers (≤ L16)" — user decides |
| 20 ≤ Λ ≤ 40 | fixed in the middle layers | upgrade candidate closest to the original H1 ("middle layers fix what is asked") — user decides |
| 44 ≤ Λ ≤ 60 | fixed only late | stays downgraded, layer pinned down: "the format is fixed at the answer position only from L Λ" |
| no Λ: R stays > 0.10 up to L60 | no locking layer: the type keeps being re-read from the question words until the last layers | stays downgraded, sharpened: "':' follows the question throughout; no layer fixes the format there" |
| (a) holds, (b) fails | swap breaks the output without transferring the type ("lock without clean transfer") | unchanged; reported as a limitation |
| Λ differs across pairs | type-specific locking (e.g. year later than authors) | wording per type; S3 says whether the asymmetry is real |
Joint reading with the knockout: X_g ≈ Λ (within one tested step) → clean lock at Λ; X_g ≪ Λ → the type is already copied
early but still re-read until Λ (redundant reading); X_g missing while Λ exists → contradictory, reported, no verdict.
D_sink > 0 (Holm) → the a23 dip is confirmed as a sink artefact on the new format; otherwise the a23 supplement reading is
not reproduced and the a23 L56 result is reported without the artefact explanation.
If Λ ≠ 56, addendum 26 (run with X = 56) is not re-run automatically; a re-run would be a new request to the user.
Any upgrade of H1 needs the user (CLAUDE.md rule 5); downgrades / limitations follow the autonomous sync rule.

## 11. Hard checks (WARN only, never stop the queue; numbers and thresholds kept; only code crashes stop)
1. β = 0 / no intervention: the hooked path with every hook at zero strength (random-state swap scaled by 0; explicit mask
   with nothing blocked) reproduces the plain forward: identical greedy tokens for ≥ 0.99 of prompts, max |Δ logit| ≤ 1.0
   (|logit| 32–64 → bf16 spacing 0.25, so ≥ 4 units of tolerance).
2. Self-swap (recipient with its own A states at every l) = base: identical τ for 1.00, max |Δ logit| ≤ 1.0.
3. K(64) with explicit mask = no mask: identical τ for ≥ 0.99.
4. Pilot vs main (no paper overlap by design): the main-sample base type rates of the selected format lie within ±0.05 of
   the pilot rates (WARN otherwise).
5. Token layout asserts (section 3) — these are code checks and do stop the freeze if violated.
6. Tiny model (random 3-layer Qwen3, real tokenizer): swap at the last layer of the final ":" reproduces the donor's
   logits exactly (≤ 1e-4); self-swap ≤ 1e-4; skip-if-done works; pipeline end-to-end on 3 papers.

## 12. Cost estimate and order (A100-80GB, shards ≤ 45 min)
Measured anchors: addendum 23 = 83 s per 50 papers (≈ 1.7 s/paper, ≈ 106 forward rows of ~31 tokens per paper, 0.5–0.6 min
model load); a23 supplement ≈ 1.0 s/paper (greedy first content token, GEN_MAX 4); addendum 26 ≈ 2.4 s/paper.
This test, per paper ≈ 274 rows (3 base + 90 swap + 48 ":"-only + 42 controls + 90 knockouts + 1 self-check), each with a
short greedy continuation (≈ 3 steps on average) plus one scoring pass → ≈ 55k token positions per paper ≈ 9–27 s/paper.
- pilot: 150 papers × 5 formats, base + floor + scoring + 10-paper attention diagnostic ≈ 0.2–0.3 GPU-h (1 job);
- main: 582 papers ≈ 1.5–4.4 GPU-h, point estimate ≈ 2.5 GPU-h; 12 shards of 50 papers, ≈ 8–23 min each (max-minutes 38).
- total ≈ 2–4.7 GPU-h (point ≈ 2.8). The 1-shard measurement is binding: if it projects > 5 GPU-h, stop and ask the user
  (CLAUDE.md rule 5) before the remaining shards; cost lever = scoring pass only at the 8 addendum-23 layers.
Order: CPU freeze + token asserts → tiny random-model test → pilot job → CPU pilot gate (rule 4) → user lock → 1 real shard
(cost + hard checks) → remaining shards with a CPU gate (resubmits missing shards ≤ 4 rounds, then analysis). Every job
--mail-type=END,FAIL; skip-if-done per shard.
No sample extension (decision D5).

## 13. Deviations policy
Changes after lock are recorded in `prereg_addendum34_deviations.md` (D34-1, …) with date, reason and whether any data of
the affected part had been seen; interpretation of conflicting clauses as in D23-1. Check misses are WARN (section 11), not
deviations. Formats or measures not listed here, or a change of thresholds, after any main-sample data = deviation that
makes the affected result exploratory.

## 14. Planned file layout (new files only; nothing existing is edited)
- locked text: `391_groups/config/prereg_addendum34.md` + `prereg_addendum34.md.sha256`; draft history `prereg_addendum34_DRAFT.md`
- code: `~/jlens_work/18_h1lock/a34_h1swap.py` (freeze / pilot / pilot_gate / tiny / work / analyze; imports frozen Stage
  10/11 scripts and a23_supp helpers read-only), `a34_cpu.sbatch`, `a34_pilot_gpu.sbatch`, `a34_gpu.sbatch`,
  `a34_gate.sbatch`; user-facing summary `~/jlens_work/35_h1lock2/draft_summary_zh.md`
- data: `391_groups/raw/a34_pilot_freeze/`, `raw/a34_pilot/`, `raw/a34_freeze/` (freeze.parquet, lexicons.json,
  freeze.json), `raw/a34/shard_KKK.{npz,json}`; summaries `391_groups/summary_a34_pilot/`, `summary_a34/`;
  logs `391_groups/logs/a34/`.

## 15. Decisions (user 2026-11-25; all recommended options approved)
- D1 primary measure: first content word of the greedy answer (7.1); three-candidate scoring, maximum over types (7.2) =
  sensitivity analysis (the switch of rule 4.2 remains the only way the roles can change).
- D2 question wording: equal-length "who are the authors of it?" / "in what year was it published?" / "in what research
  field is it?".
- D3 option B = F2: the question followed by " Answer:" on the same line. The strict reading (question words ending directly
  at ":" with no shared label) is not used.
- D4 lock rule as in section 5: recipient type kept in R ≤ 0.10 (adjusted upper ≤ 0.20) AND flip to the donor type
  S ≥ 0.80 (adjusted lower ≥ 0.70), both controls ≤ 0.10.
- D5 sample: the 582 addendum 23 papers only (no tune extension).
- D6 swap span: both "Answer" and ":" positions (primary); ":" only = sensitivity.

## 16. Limitations stated in advance
Single model; raw-text prompts without chat template; answer type from a rule-based classifier with an "other" category;
the format is chosen on pilot data (disjoint papers, rule fixed now); only the "Answer:" positions are swapped or blocked;
swaps can push states off-distribution (controlled by the random-state swap); layer resolution 4.
