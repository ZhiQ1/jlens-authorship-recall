# Pre-registration addendum 32 — LOCKED 2026-11-22: Geva-style single-layer edge knockout sweep

Status: LOCKED 2026-11-22 under the standing rule (new GPU experiment ≤ 5 GPU-h, user informed 2026-11-22). Written before any data of this design. Code: ~/jlens_work/24_gpubatch/a32_sweep.py (imports the frozen addendum 18b item 2 code by path, with the window-assignment fix of a18b_item2_fix.py; frozen files unchanged).

## 1. Question
Addendum 18b item 2 cut one attention edge inside 4-layer windows (rule met for name ← title in L44–L55; each cut ≤ 3.5% of S). Here: at which SINGLE layers does each edge carry information (cf. Geva et al., EMNLP 2023, attention-edge knockouts by layer)?

## 2. Design
Same as 18b item 2 (600-paper subsample, seed 1817; 5 false titles; S = true − mean of 5 false at the final output, paper means of log10(1/rank); loss = S(none) − S(config); all heads of an edge cut). Windows = single layers L40, L42, …, L56 (9). Edges: name ← title, name ← tail, tail ← title, ":" ← title, name ← ":". 46 configs (45 + none) per batch.

## 3. Rules (fixed before data)
(a) Per (layer, edge): loss with team-bootstrap CI (2,000, the 18b Boot); two-sided bootstrap p; **Holm over the 45 cells**. "Carries information" = loss > 0 with Holm p < 0.05; "reversed" = loss < 0 with Holm p < 0.05.
(b) Per layer, the frozen 18b dominance rule (largest-loss edge CI > 0 and paired difference to every other edge CI > 0) — reported per layer.

| Reading | Condition |
|---|---|
| Single-layer route located | ≥ 1 cell carries information |
| No single layer matters alone | no cell carries information (information spread over layers) |
| Reversed cells | any cell reversed (reported with the reading) |

## 4. Cost and checks
≈ 1.6 GPU-h (scaled from 18b step-2, 56 configs ≈ 2.0 GPU-h). Tiny random-model test (each config blocks exactly its single layer; skip-if-done) → shard 0 trial → rest under a CPU gate over all 24 shards. The frozen 18b checks (unblocked ranks vs stored E1) are WARN only.

## 5. Limitations
Single layer cuts are lower bounds (other layers can carry the same information); all heads at once; 600-paper subsample.
