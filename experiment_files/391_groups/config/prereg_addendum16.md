# Addendum 16 (locked 2026-11-14): the model recognises the paper but cannot say the authors — where is the bottleneck?

Status: LOCKED. sha256 in prereg_addendum16.md.sha256. Written before any B or D result exists. Items C and F are exploratory (CPU, existing data) and are not confirmatory tests of this addendum. Bottlenecks A (prior competition / title-contrastive decoding) and E (middle-layer re-ranking) are NOT run under this addendum (deferred; E largely done in prior work, Inside-Out, Gekhman et al. 2025).

## 0. Background (known before locking)
- Group A = recognised (multiple-choice pass, mc_team_outcome_tight strong) but no correct author written (R0), 4,110 papers. Their unwritten authors carry more output-level title-specific signal than group B (+0.200 [0.188, 0.213]), but there is no middle-layer lead.
- Step 0 (decode gap, post hoc, 391_groups/summary_decode_gap_20261114/, jobs 11866759 / 11866766): rank of the first author's first name token at the final output right after "Authors:", true title. Rank ≤ 5: A 0.298 [0.283, 0.312], B 0.249; median 13 vs 15. Initial-first A 0.361 (median 9), given-first A 0.099 (median 96, 49% beyond 100). Only 6.5% of A papers are at rank ≤ 5 with the true title and beyond 5 under all 5 false titles. Tokens that beat a rank 2–5 true token: another initial 53.6%, common given name 19.3%, a true co-author's first token 16.5%; 70% are among the 20 most frequent first tokens. A near-miss decoding explanation covers at most ~5–10% of A.
- F (exposure, exploratory, 391_groups/summary_exposure_20261114/, job 11866815): recognition reaches 50% at ~40 citations [36, 44]; recall (≥ 1 correct author) stays < 0.05 up to 64 citations and is 0.574 at 4097+; output spec target − control ≈ +0.19 already in the lowest bins.
- Related work: related_work_bottlenecks_20261114.md (B, D open; C, F partly done).

## 1. Common settings
- Model Qwen3-32B bf16, Stage 10 prompt: 'Who are the authors of the paper titled "{title}" ({year})?\nAuthors:' (351_stage10.py line 29), with the format change only where a condition says so.
- Scoring unit: ALL authors, ALL name tokens; author score = mean log10(1/rank) of the author's name tokens under teacher forcing (score_tf, as addenda 9 / 10); paper score = mean over scored authors. First-author first-token version reported beside it.
- Title-specific: every internal score also as true title − mean of the 5 matched false titles (Stage 10 false titles); deleted-title version reported.
- Samples (drawn once, before any run, numpy default_rng(1114)), within citation bin in proportion to the Stage 11 sample's bin distribution (config/sample.parquet): A 600, B 600, C 300 papers (C: only unwritten authors are scored). D uses papers with ≥ 3 authors (same quotas; if a bin has too few, take all and give the rest to the other bins proportionally). Sample lists are frozen in config/prereg16_sample_{B,D}.parquet with sha256 before the first GPU job.
- Generation: greedy, max 80 new tokens, stop at the first newline after the list or at end of turn, thinking disabled, same chat formatting as Stage 10 (plain prompt, no system message). Matching: existing matcher (surname + first initial, both orders); surname-only matching where a condition asks only for surnames.
- Intervals: archived author-team cluster bootstrap, 2,000 draws (381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz team); every difference on the same draws. n < 30 cells: descriptive only.
- Multiplicity: Holm over the confirmatory main comparisons of B (4 conditions) and D (1), i.e. 5 tests.
- Process: CPU precheck → tiny-model whole-pipeline test → 1 real shard per item to measure cost → the rest; GPU jobs ≤ 45 min; killguard exclusions; in-job self-checks are WARN only (parity misses never stop GPU work).

## 2. B format lock (confirmatory)
Hypothesis: the first token the format forces the model to write (a given name or an initial) carries little paper-specific information, so generation goes wrong at the first step.
Conditions (same papers, prompt suffix changed):
- F0 original: '…\nAuthors:'
- F1 surname first: '…\nAuthors (surname, given name):'
- F2 surnames only: '…\nAuthor surnames:'
- F3 first author's surname only: '…\nFirst author\'s surname:'
- F4 initial completion: '…\nAuthors: K.' where K is the TRUE first author's first initial; the model completes the first author (and may continue the list).
Outcomes (paper level):
- F0, F1: ≥ 1 true author matched (full matcher); also first author matched.
- F2: ≥ 1 true surname matched; also first author's surname matched.
- F3, F4: first author's surname matched.
Chance baseline (all conditions): for each sample paper a control paper is fixed in advance (same field, author count within ±1, drawn with default_rng(1114); for F4 a same-field paper whose first author has the same first initial if one exists, else any same-field paper). The model's output for the sample paper is matched against the control paper's true authors with the same rule. Chance-corrected outcome = true match rate − chance match rate.
Main comparison: for each c in {F1, F2, F3, F4}, Δ_A(c) = chance-corrected rate of group A under c − chance-corrected rate of group A under F0 on the comparable outcome (F1: ≥ 1 author; F2: ≥ 1 surname vs F0 ≥ 1 surname-matched author; F3 and F4: first-author surname vs F0 first-author surname); and the difference-in-differences DiD(c) = Δ_A(c) − Δ_B(c).
Decision rule: B is supported if for at least one c both Δ_A(c) > 0 and DiD(c) > 0 with Holm-adjusted 95% CIs excluding 0; otherwise not supported (stated as a result). Fabricated-name rates are reported beside every condition; if a condition raises fabrication more than it raises chance-corrected recall, its result is reported as not interpretable.
Pre-specified split: every outcome reported separately by the TRUE first author's first-token type (initial-first vs given-name-first) within A, B and C; the split is descriptive, the decision uses the pooled main comparison.
Teacher-forced part: true authors written in each format, all-token score_tf and the first-token rank under that format; spec = true − mean of 5 false titles.

## 3. D name chain (confirmatory, two-sided)
Hypothesis (two-sided, because prior work has both directions): a true name given first changes recall of the other authors of the same paper.
Conditions (teacher forcing after 'Authors:' then a prefix of k names, k = 1 main, k = 2 secondary):
- P_true(k): the first k true authors.
- P_other(k): the first k authors of a fixed same-field control paper (real names, wrong paper).
- P_none: no prefix.
- P_shuffle: k true authors drawn from the non-scored positions in a fixed random order (order check).
- P_reverse: true authors 2..n as prefix; only the first author is scored (direction check).
- each in true-title, mean-of-5-false-titles and deleted-title versions.
CONFIRMED: the prefix authors are never scored. In P_true(k), P_other(k), P_none and P_shuffle the scored set is identical: this paper's authors k+1..n (all name tokens); in P_reverse only the first author is scored.
Main comparison: G_A(1) = score(P_true(1)) − score(P_other(1)) on the scored set, group A, true title; two-sided. Secondary: G_A(1) − G_B(1); G(2); title-specific version (true − false-title mean); deleted-title version (does a true co-author replace the title?); P_reverse vs forward.
Decision rule: a chain effect is supported if the Holm-adjusted 95% CI of G_A(1) excludes 0; its sign gives the direction (helps / hinders). Secondary comparisons descriptive.
Optional generation check (secondary): given the true vs the control first author, greedy generation of the rest; recall of authors 2..n.

## 4. C neighbour confusion (exploratory, CPU)
Fabricated names in the open answers classified (first match wins): co-author of a true author / same-field real author / other real author in the dataset / not in the dataset; against a random-author baseline; by target / control and citation bin; team CI. Descriptive only.

## 5. F exposure threshold (exploratory, CPU)
Done before locking (see §0); may be extended descriptively.

## 6. Cost (to be measured on 1 shard each before the rest)
B ≈ 3–4 A100-80GB GPU h (1,500 papers × 5 conditions generation + teacher forcing); D ≈ 2 GPU h. If the 1-shard measurement implies > 5 GPU h for an item, ask the user before running the rest.

## 7. Limits (stated in advance)
Behavioural labels come from another generation run (label package; prompt, sampling and thinking settings not on the cluster); F0 calibrates our prompt against it. Teacher-forced scores are preferences, not generation. Greedy decoding only. Citation counts are only a proxy for training exposure. Bottlenecks can co-exist; each decision says only whether that one contributes.
