# Addendum 33 (LOCKED 2026-11-23) — X4 surname signal: confirmatory test of the paper-specific part beyond topic

Status: DRAFT 2026-11-23, amended 2026-11-23 (user: lock and run after checking four requirements — topic-matched controls, text-only baseline, target − control, a sample size that can decide). Amendments marked [A1]–[A5]. Number assigned at lock (next free addendum, ≥ 33). Nothing has been run.

## Why
X4 (decode the first author from the title state, patchscope-style) shows a surname signal from L8. Three exploratory/locked
results bound it: literal overlap explains ≈ 0 (exploratory, 2026-11-21); Qwen exceeds a text-only BERT baseline (+0.104
[0.029, 0.180], exploratory, weak baseline); with a topic-matched partner the topic share is P = 0.25 [−0.07, 0.49] and the
residual D_topic = +0.016 [−0.004, +0.036] (addendum 28, locked, verdict "mixed", 1,178 papers — underpowered).
The question for a confirmatory test: is there a surname signal at the title position that is specific to THIS paper beyond
(a) the topic, (b) literal overlap and (c) what a text-only model reads from the same title?

## Sample (fresh — no paper of addendum 28 or the Stage 11 sample)
[A1] N = ALL eligible cohort papers outside the Stage 11 sample (≈ 7,900 before exclusions; exact counts frozen and reported
before any run), both groups (target = recognised, control = not recognised), seed 33. The earlier 4,000-paper plan was too small.
Exclusions fixed now (applied at freeze, counts reported): (i) any author surname appears in the title; (ii) the first author's
surname-first Qwen token occurs among the title tokens; (iii) eponym-like capitalised title word (same rule as the 2026-11-21
source check).
[A2] Precision, from the addendum 28 CIs at n = 1,178 (surname_first, L8): D_topic half-width 0.0197; T − C of D_topic
half-width 0.039. Scaled by √(1,178 / n): at n ≈ 7,000 → D_topic ± 0.008, T − C ± 0.016. (The draft's "SE ≈ 0.005 at
n = 4,000 in the target group" was wrong: 2,000 target papers give ± 0.015.) So T1 and T2 can decide effects of about the
addendum 28 point estimate (+0.016); T3 can only decide target − control differences of about ≥ 0.02 — stated in advance; the
whole cohort is the ceiling.
## Partners (frozen with the sample)
- topic partner (primary): same field, nearest title under all-mpnet-base-v2, other author team, no shared surname;
- topic partner (sensitivity): same under bert-base-uncased mean-pooled;
- random same-field partner (published X4 rule: same field, same title token count, no shared surname).

## Measurement (identical to addendum 28 / published X4)
Source = last title token of the X4 authors prompt (no year); injected at the X placeholder of the PS_TARGETS prompts at
L ∈ {8, 16, 24, 32, 40, 48, 56}; score = per-token log10(1/rank) of A's first-author surname-first tokens (primary) and all
first-author tokens, year, field (secondary).
D_s(l) = paper mean of [score(A's answer | A's state) − score(A's answer | source s)].
Text-only baseline (primary): the same contrast computed with bert-base-uncased (the 2026-11-21 baseline code) on the same pairs.
[A3] Second baseline (secondary, in-model, no context): the same contrast with the source state taken at L0 (embeddings only)
— what the title tokens give before any contextual processing. BERT is a weak baseline (stated as a limitation); no stronger
text model is cached offline and none will be downloaded for this test.

## Primary tests (team bootstrap 2,000 over author teams, seed 33; Holm over the three primaries)
- T1 paper-specific beyond topic: D_topic_mpnet(surname_first, L8), all papers, CI > 0.
- T2 beyond a text-only model: [D_topic_mpnet]_Qwen − [D_topic_mpnet]_BERT (surname_first, L8, all papers), CI > 0.
- [A4] T3 recognition: target − control of D_topic_mpnet(surname_first, L8), compared within the 13 citation bins
  (bin-weighted by the pooled bin sizes, the usual Stage 10 rule), CI > 0.
[A5] Smallest effect of interest δ = 0.010 nlr (≈ 60% of the addendum 28 point estimate) for T1/T2, δ = 0.020 for T3.
| reading | condition |
|---|---|
| paper-specific surname signal confirmed | T1 and T2 both Holm CI > 0 |
| beyond topic, but not beyond a text model | T1 > 0, T2 CI includes 0 |
| topic prior explains it (decided) | T1 Holm CI includes 0 AND lies within (−δ, +δ) |
| inconclusive | T1 CI includes 0 but extends beyond ±δ |
| reversed | T1 CI entirely < 0 |
| recognition-specific | T3 Holm CI > 0 |
| no recognition difference ≥ 0.02 | T3 CI within (−0.02, +0.02) |
| recognition: inconclusive | otherwise |
Secondary (descriptive): P = ΣD_topic/ΣD_random; layer profile L8–L56; bert-topic sensitivity; the L0 in-model baseline;
the three exclusion counts and the result with exclusions lifted.
## Checks (WARN only, never stop)
Self-source scores vs stored X4 protocol on a 50-paper overlap: exact-rank share ≥ 0.75, mean |Δ| ≤ 0.05.

## Cost (estimate; measured on 1 shard before the rest)
Addendum 28: ≈ 0.54 GPU-h for 1,178 papers (4 sources × 3 targets × 7 layers). Here ≈ 7,000 papers × 4 sources + the L0 baseline
≈ 3.2 GPU-h + self-state forwards ≈ 0.3 → ≈ 3.5 GPU-h (range 2.8–4.6). Cap: if the 1-shard measurement projects > 5 GPU-h, stop
after that shard and ask the user. BERT baseline: CPU.

## Limitations stated in advance
Single model; topic similarity approximated by two text models; X4 asks for the first author by design; title source only.
