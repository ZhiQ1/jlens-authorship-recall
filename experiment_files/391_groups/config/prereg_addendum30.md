# Pre-registration addendum 30 — LOCKED 2026-11-22: direction asymmetry (H5, "reversal curse") for paper authors

Status: LOCKED 2026-11-22 under the standing rule (new GPU experiment ≤ 5 GPU-h, user informed 2026-11-22). Written before any data of this design. Code: ~/jlens_work/24_gpubatch/a30_h5.py. Numbers 27–29 are in use.

## 1. Question

H5: Qwen3-32B stores the author–paper association mainly in the direction it appears in pre-training text (citations: "Authors (Year). Title."), i.e. author → title. Recalling authors from a title runs against that direction, which would explain "recognised but not said": the multiple-choice test gives the names (names → paper, the stored direction), open recall starts from the title (reverse direction).

Background: Berglund et al., "The Reversal Curse: LLMs trained on 'A is B' fail to learn 'B is A'", ICLR 2024 (arXiv 2309.12288) — fine-tuned and real-world examples; not paper authors, not Qwen, no layer-level mechanism. Our step beyond it: a natural pre-training-frequency association (authors ↔ titles) at scale (1,200 papers with recognition labels), both directions scored on the same papers, with the layer-level contrasts already measured for the reverse direction.

## 2. Sample

The addendum 16 B sample (391_groups/config/prereg16_sample_B.parquet, sha 117a9127…): A = 600 (R0 × recognised), B = 600 (R0 × not recognised). Exclusions fixed now: papers with > 10 authors are written with the first 10 + "et al." (same rule both directions); titles > 40 tokens truncated for scoring only (reported).

## 3. Conditions (Qwen3-32B, bf16, no chat template, as Stage 10)

| Direction | Prompt | Score |
|---|---|---|
| **Forward (stored direction under H5)** | citation prefix in the cohort's author format: `"{Surname1}, {I1}., {Surname2}, {I2}., … ({Year}). "` then the title | (i) teacher-forced mean log-prob per title token of the TRUE title; (ii) the same for each of the 5 matched false titles (Stage 10 false_0..4) after the same prefix → **F_spec = lp(true) − mean_k lp(false_k)**; (iii) greedy generation (max 48 new tokens, stop at "." + newline or EOS): exact match (normalised), token-F1 to the true title |
| Forward, mismatched-author control | same, but the prefix lists the authors of another paper in the same field and citation bin (seed 30) | F_spec_mis; **F_id = F_spec − F_spec_mis** (title-specific gain from the true authors beyond field) |
| Reverse (existing) | Stage 10 F0 prompt title → authors | Stage 10 spec (true − 5 false), final L63, all authors; addendum 16 F0 generation any_full |
| Names → paper (existing) | multiple-choice labels | mc_team_a, p_true |

## 4. Primary quantities and decision rule (fixed before data)

- **R1 (forward knowledge depends on recognition):** within-citation-bin target − control (A − B) of F_id; team bootstrap 2,000, seed 30. Supported if the 95% CI > 0.
- **R2 (asymmetry in group A):** forward generation success (token-F1 ≥ 0.8) rate vs reverse generation success (any_full, a16 F0) rate on the same A papers; paired difference forward − reverse; supported if the CI > 0.
- **R3 (forward explains recognition):** among A papers, F_id predicts mc_team_p_true beyond log citations (standardised slope, CI > 0) — secondary, reported with R1/R2.

| Reading | Condition |
|---|---|
| **H5 supported** (asymmetry, recognition-linked) | R1 and R2 both supported |
| Asymmetry without recognition link | R2 supported, R1 not |
| Recognition-linked but symmetric | R1 supported, R2 not (forward no easier than reverse) |
| Not supported | neither R1 nor R2 |
| Reversed | R2's CI < 0 (reverse easier than forward) |
| Borderline | R1 or R2 met only without the correction for the two primary tests (Holm over R1, R2) |

## 5. Alternatives this separates

- H4 topic association predicts F_spec_mis ≈ F_spec (any same-field author list helps equally) → F_id ≈ 0.
- H9 MC bias predicts R1 ≈ 0 (recognition label not tied to any stored association).
- H7 first-token bottleneck predicts the forward direction is not easier for titles than reverse is for names (R2 not supported) if the bottleneck is generic to generation.

## 6. Checks (WARN only)

Prefix tokenisation identical across true/false titles; the title start position aligned; base reverse scores reproduce Stage 10 for ≥ 0.75 of rows (bf16 batch shapes).

## 7. Cost (estimate; measured in a tiny test and a 1-shard trial before the rest)

1,200 papers × (1 true + 5 false + 1 mismatched-true + 5 mismatched-false) teacher-forced forwards ≈ 14,400 short sequences (~70 tokens) + 1,200 greedy generations (≤ 48 tokens). From a16 (0.35 s per generation at batch 16, H200) and a21 timings: ≈ 0.4–0.7 GPU-h incl. model loading. CPU precheck → tiny random-model test → 1 shard (50 papers) → rest + gate over the freeze's full shard list.

## 8. Limitations stated in advance

Single model; the citation format is one of several in pre-training data; greedy decoding; exact-match title generation is strict (token-F1 is the primary generation score); the MC direction uses existing labels (distractors: same field, similar team size, citation bin and year — real teams of 3 other papers).

## 9. Implementation details fixed at lock (2026-11-22)

- Citation prefix: each author "Given Middle Surname" → "Surname, G. M."; authors joined by ", "; > 10 authors → first 10 + ", et al."; then " (Year)." (no trailing space). The title continuation is encoded as " " + title (separately from the prefix; the share of papers where this equals the joint tokenisation is reported, WARN only). Titles truncated to 40 tokens for scoring.
- Teacher forcing: the 12 sequences of a paper (true prefix × {true, false_0..4}; mismatched prefix × {true, false_0..4}) in one right-padded batch; lp = mean log-prob over the title tokens.
- Generation: greedy, max 48 new tokens, newline stop (a16 generate with stop_nl); generated title = text up to the first newline, then up to the first ". " (period + space), quotes stripped; token-F1 on lower-case alphanumeric words; success = F1 ≥ 0.8.
- Reverse success: stored a16 F0 generation any_full (raw/a16_B/gen_v2), same papers.
- Bootstrap: multinomial over a16 teams, 2,000 draws, seed 30; R1 within-bin weights n_A n_B / (n_A + n_B); two-sided bootstrap p; Holm over R1 and R2 (adjusted CIs at α/(m − rank)); R3 by weighted least squares per draw.
- Shards: the a16 shard ids (30); tiny random-model test, then shard 0 as the real-model trial (cost measured), then the rest under a CPU gate that checks every shard in the freeze.
