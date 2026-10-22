# Stage 5 · Pilot50 v1 Controlled Readout

Status: 50/50 completed; same-first-token (non-discriminable): 0.

## Research question
Does the title-specific gold-versus-false first-token readout differ across frozen A/B/C/D behavioral groups?

## Protocol
Model Qwen3-32B BF16; Public Neuronpedia Jacobian Lens; L16/24/32/40/48/56/62; final L63 reference.
Two model contexts per paper: true paper title and crossed-source matched paper title.
Each context scores the first token of the frozen gold and false author from the SAME logits.
Title-specific advantage = (gold−false under true title) − (gold−false under shuffled title).
First-token ties excluded from author-discriminative analysis but always counted and retained.

## Cohort and control quality
Original frozen group labels preserved. Completed groups: {'A': 20, 'B': 20, 'C': 7, 'D': 3}.
Frozen exact citation-bin+field A/B pairs: 20; paired summaries in matched_ab_summary.csv.
False author validated by name against provided paper author list; external author identity collision not independently checked.
This is a RESOURCE-CONSTRAINED PILOT, not a confirmatory result. Stage4 first-token/teacher-forced results are separate.

## Layer-level J-Lens results
|Layer|n discriminable|Mean title-specific advantage|95% bootstrap CI|
|---|---:|---:|---|
|L16|50|0.0626171875|[-0.0603125, 0.19109375]|
|L24|50|-0.0163623046875|[-0.1510302734375, 0.0990869140625]|
|L32|50|-0.041279296875|[-0.176376953125, 0.0991259765625]|
|L40|50|0.178125|[0.040625, 0.341875]|
|L48|50|0.0946875|[-0.1246875, 0.334375]|
|L56|50|1.166787109375|[0.533466796875, 1.837578125]|
|L62|50|1.0765625|[0.3625, 1.81625]|

## A/B matched-pair inference (exploratory)
All seven fixed layers included in predeclared integrated endpoint; bootstrap resamples matched pairs.
|Mode|Layer|n complete pairs|Mean A-B|95% CI|
|---|---|---:|---:|---|
|jlens|16|20|-0.20244140625|[-0.46796875, 0.04765625]|
|jlens|24|20|-0.21290283203125|[-0.51656494140625, 0.04134521484375]|
|jlens|32|20|-0.11357421875|[-0.380908203125, 0.162548828125]|
|jlens|40|20|0.053125|[-0.2484375, 0.3890625]|
|jlens|48|20|0.1875|[-0.33828125, 0.73359375]|
|jlens|56|20|0.2534912109375|[-1.23203125, 1.87890625]|
|jlens|62|20|0.60234375|[-0.684375, 2.1875]|
|jlens|integrated|20|0.08107735770089285|[-0.4264997209821429, 0.6475376674107143]|

## First-token collisions by original group
|Group|Completed|Collision|Rate|
|---|---:|---:|---:|
|A|20|0|0.0|
|B|20|0|0.0|
|C|7|0|0.0|
|D|3|0|0.0|

## Interpretation limits
Differences are first-token candidate discrimination, NOT full-name factual recognition.
Title shuffling may alter topic/length/other prompt characteristics even with field/bin matching.
No causal knowledge conclusion. C/D have small sample sizes. Multiple testing not corrected.
These are descriptive bootstrap intervals and must not be treated as confirmatory discovery.

## Artifacts
Raw: raw/pilot50_results.jsonl; frozen samples: cohort/pilot50_v1.csv; controls: controls/pilot50_controls.csv.
Summary: summary/paper_layer_contrasts.csv, layer_summary.csv, matched_pair_contrasts.csv, matched_ab_summary.csv, first_token_collision_audit.csv.
Figures: figures/*.png and *.pdf, regenerate with analyze subcommand.
Future full-cohort work MUST reuse the exact pilot50_v1 IDs and frozen control mappings, including non-discriminable cases.
