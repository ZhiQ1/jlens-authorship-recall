# Pre-registration addendum 27 — LOCKED 2026-11-22: why does amplifying the arrived information hurt? (TODO #3, follow-up of addendum 21)

Status: LOCKED 2026-11-22 (user approval 2026-11-22: "锁定并提交 #9、#3、#6、#11"). Written before any real-model run of this design.
Code: ~/jlens_work/19_todo/a27_inject_followup.py; reuses 16_inject/inject_main.py (addendum 21) by import, not edited.

## Background (exploratory, stored addendum 21 outputs; seen before this lock)
Group A, β = 4: correct writing any_full base 0.038 → own 0.032 / mismatched 0.018 / random 0.033 (L48); empty answers 0.003 →
0.015–0.032; teacher-forced output rank of the true names falls about equally for own and mismatched (own − mismatched L52 β4
+0.012 [−0.002, +0.026]). Reading then: generic off-distribution damage, not paper-specific help.

## Question
Is the damage caused by (a) the extra norm along the state's own direction, (b) adding any direction at fixed norm along h, and
does the paper's own component help when added right before the late MLP writer (L57–L61, C29)?

## Sample, prompt, positions (identical to addendum 21)
addendum 16 B sample, A 600 (R0 × recognised) / B 600 (R0 × not recognised), frozen raw/a21_freeze/freeze.parquet (30 shards); the
Stage 10 F0 authors prompt with the true title; the aligned post-title tail (m_i positions); additive hook on the block-l output
during prefill only.

## Sources (per position p, norm ‖Δ_i(l,p)‖; β ∈ {1, 2, 4})
own Δ_i = h_true − mean_k h_false_k; mis = donor's Δ_j renormalised (addendum 21 donor); scale = ‖Δ_i‖·h/‖h‖ (pure norm increase
along h); orth = Δ_i projected orthogonal to h, renormalised to ‖Δ_i‖. Layers: L48 (scale, orth), L56 and L57 (own, mis, scale,
orth). Plus base and the β = 0 hook check (zero).

## Outcomes
Primary: teacher-forced log10(1/rank) of every true name token at the output (all authors), paper mean.
Secondary: open generation (a16 F0) for base, zero, own at L56/L57 (β 1/2/4) and scale at L57 β4: any_full, first_sur, empty rate.

## Primary contrasts and rule (group A; team bootstrap 2,000 over a16 teams, seed 27; Holm within each family)
- N(l, β) = TF(scale) − TF(base), l ∈ {48, 56, 57}: norm damage (family of 9 cells).
- O(l, β) = TF(orth) − TF(base), l ∈ {48, 56, 57}: direction damage at fixed norm along h (9 cells).
- P(l, β) = TF(own) − TF(mis), l ∈ {56, 57}: paper-specific help just before the writer (6 cells).
| reading | condition |
|---|---|
| damage is norm-driven | some cell with N Holm-significant < 0 where O is not |
| damage is direction-driven | some cell with O Holm-significant < 0 where N is not |
| both | N and O Holm-significant < 0 in the same cell |
| no damage from either | no Holm-significant N or O < 0 |
| paper-specific help near the writer | some P Holm-significant > 0 |
| reversed | some P Holm-significant < 0 (own hurts more than mismatched) |
Several rows can apply; all are reported. Group B: same contrasts, descriptive. Also reported: own − base, mis − base at L56/L57.

## Checks (WARN only, never stop)
β = 0 hook == base (exact ids); norms equal across sources (≤ 1e-3 rel.); orth ⟂ h (|cos| < 1e-3); base TF vs stored Stage 10
ranks (exact share ≥ 0.75, mean |Δlog10 rank| ≤ 0.05); base generations vs stored a16 F0 (≥ 0.95 same outcome).

## Cost
32 teacher-forced conditions per paper, 9 generations; estimate 1.0–1.5 GPU-h (1-shard trial measures it). CPU tiny test → 1 shard → rest + gate.

## Limitations stated in advance
Single model; TF-only primary; scale and orth are two of many decompositions; injection only at the prompt tail.
