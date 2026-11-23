# Pre-registration addendum 29 — LOCKED 2026-11-22: Stage 10 readouts at the never-measured layers L25–L38 (TODO #11)

Status: LOCKED 2026-11-22 (user approval 2026-11-22: "锁定并提交 #9、#3、#6、#11"). Written before any run at these layers.
Code: ~/jlens_work/19_todo/a29_layerfill.py, a wrapper around the frozen batch-3 Stage 10 wrapper
13_stage13/stage13_b3_s10_gpu.py (items 3-1 / 3-2, addendum 14), imported by path and not edited.

## Question
C01 states that the within-bin target − control title-specific signal at the name positions is ≈ 0 before L50 (logit lens) and
does not lead in the middle layers (public J-lens). L0–L24, L32, L40–L63 were measured; L25–L31 and L33–L39 never were.
Does any of the missing layers show an earlier onset?

## Design (reduced version; the full 14-layer fill would exceed 5 GPU-h)
Layers L25, L26, L28, L30, L34, L36, L38 (+ L24 and L48 recomputed in the same forward as hard-check layers vs stored Stage 10).
Papers: the within-bin analysis set only — citation bins with ≥ 30 target and ≥ 30 control papers (5,916 papers: 3,734 target,
2,182 control). Conditions true and false_0..4 ('delete' skipped). Readouts logit lens and public J-lens. Everything else is
the Stage 10 fast path unchanged (one forward per author context, every name token, rank over the vocabulary, bf16 logits).

## Measure and rule (team bootstrap 2,000 over author teams, seed 29)
Per paper spec = mean over name tokens of [log10(1/rank_true) − mean_k log10(1/rank_false_k)]; within-bin target − control
(weights n_t·n_c/(n_t+n_c), bins with ≥ 30 per group), per readout × filled layer.
| reading | condition |
|---|---|
| "≈ 0 before L50" holds | every filled layer: CI includes 0 or |estimate| ≤ 0.01 |
| an earlier onset | some filled layer: CI > 0 and estimate > 0.01 (reported; C01 wording would change) |
| reversed (reported, does not change C01) | some filled layer: CI < 0 and estimate < −0.01 (as J-lens L41–L55) |

## Checks
Hard check of the frozen wrapper at L24 / L48 vs stored Stage 10 (gate mode on shard 0; the wrapper's own rule). Any tolerance miss
is reported as WARN with numbers.

## Cost
3-1 (10 layers, 6,841 papers, 7 conditions) took 4.9 GPU-h; this design (9 layers, 5,916 papers, 6 conditions) ≈ 3.2–3.8 GPU-h by
scaling, to be confirmed by the 1-shard trial. If the measured cost exceeds the remaining budget of the user's 5 GPU-h for
items #9/#3/#6/#11, the item stops after the trial and is reported (no partial reading).

## Limitations stated in advance
Reduced paper set (within-bin set only, as used by C01); odd layers L27–L37 not filled except L25.
