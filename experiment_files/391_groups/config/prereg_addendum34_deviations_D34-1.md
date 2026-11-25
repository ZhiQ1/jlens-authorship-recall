# Addendum 34 — deviations record D34-1 (written 2026-11-25, user-approved; before any data)

Locked plan: `prereg_addendum34.md`, sha256 `0ad42d04cd32e96d75b311d80532fdb5cdd797c0f3449c282fbd3345aa5222bb` (unchanged; this record does not edit it).

## D34-1 · Order of lock and pilot
- **Locked text (section 12, line "Order:")**: "CPU freeze + token asserts → tiny random-model test → pilot job → CPU pilot gate (rule 4) → user lock → 1 real shard".
- **What actually happens**: the plan was locked FIRST (2026-11-25 18:01 EST, user-approved), before the pilot. The order is therefore: user lock → CPU freeze + token asserts → tiny random-model test → pilot job → CPU pilot gate (rule 4) → 1 real shard → remaining shards.
- **Why**: the user approved all open choices (D1–D6) before any run and asked to lock immediately; runs wait until after the presentation.
- **Effect on the decision rules: none.** Every decision rule, threshold, measure, sample, layer set, control and multiplicity family was fixed in the locked text before any real-model data existed (no pilot, shard or analysis has run). The pilot's own choices (prompt format among the listed candidates, field word list, attention-sink position) are made by the rule already written in the locked text (section on the pilot gate) and are written into the pilot freeze file before any main-sample data are seen. Nothing chosen after the lock can change how the main test is judged.
- **What still holds from section 12**: the pilot sample stays disjoint from the 582 main papers; the pilot gate rule (≥ 0.90 correct answer type per question, format order as listed) is applied unchanged; the 5 GPU-h stop after the first measured shard is unchanged.
