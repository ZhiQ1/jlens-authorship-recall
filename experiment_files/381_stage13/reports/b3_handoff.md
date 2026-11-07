# Batch 3 handoff (addendum 14: items 3-1, 3-2, 3-3; 3-4 / 3-5 not run)

Written 2026-11-06 by the batch-3 helper. **No GPU job was submitted.** Only new files were written: no existing file was edited, nothing was deleted, and nothing was cancelled. Plan `381_stage13/config/prereg_addendum14.json` (sha256 795185e9…47bf26); every b3 script checks it at start and stops on any change.

## 1. Files (all new, in `~/jlens_work/13_stage13/`)

| file | role |
|---|---|
| `stage13_b3_cols.py` | **Column module (rule 4)** for every b3 file: paths, layer lists, readouts, conditions, raw npz keys, CSV columns, thresholds. `write_csv` refuses a frame with missing or extra columns. |
| `stage13_b3_checks.py` | Pure check and estimator functions: bf16 distance to the stored rank, the rank-match rule, paper means / spec / within-bin point estimate, team-cluster bootstrap, onset rule. |
| `stage13_b3_s10_gpu.py` | **3-1 / 3-2 wrapper** with a layer list per item (`--item 3-1` = L41–47, 49; `--item 3-2` = L0–23; both + L24, L48). It uses `351_stage10_fix1.load_model` and the frozen `351_stage10` functions `verify`, `readout_plan`, `open_lenses`, `condition_prompts`, `fast_readout` and `score` unchanged. Commands: `run` (gate `--shards 0` / `--all`), `gate-check`, `remaining`, `chain`, `tiny-root`, `tiny-ref`. |
| `stage13_b3_s10_analyze.py` | 3-1 / 3-2 full hard check on all 504 units, then the report. |
| `stage13_b3_71b_gpu.py` | **3-3**: 7.1B on the fast path (`run --gate` / `--all`, `gate-check`, `remaining`, `chain`, `tiny-ref`). |
| `stage13_b3_71b_analyze.py` | 3-3 hard check re-run, coverage check, 7.1B estimands, report. |
| `stage13_b3_unittest.py` | Unit tests of every hard check on real stored data (identical → PASS, perturbed → FAIL), plus the P1 prediction for 3-3. `pert` mode checks that a perturbed gate exits 3. |
| `stage13_b3_s10_gpu.sbatch` | GPU (gpu-short,gpu-interactive; a100@80g; 45 min; python budget 38 min). Env: `ITEM`, `MODE=gate|all`, `SHARDS`, `AUTO`, `ROUND`, `MAX_ROUNDS` (16). |
| `stage13_b3_s10_analyze.sbatch` | CPU short, 3 h. Env: `ITEM`; `NEXT_GATE=1` (with ITEM=3-1) submits the 3-2 gate after a PASS. |
| `stage13_b3_71b_gpu.sbatch`, `stage13_b3_71b_analyze.sbatch` | 3-3 GPU (`MODE=gate|all`, `AUTO`, `HC33_POLICY`) and CPU analysis. |
| `stage13_b3_tiny.sbatch`, `stage13_b3_unittest.sbatch`, `stage13_b3_tiny71warn.sbatch` | CPU tiny whole pipeline (16 steps), the unit tests alone, and the 3-3 warn-policy path. |

Every sbatch file mails on END,FAIL. All GPU work uses claims, skip-if-exists and atomic saves. A failed log line or report write is only a WARNING. A unit crash exits non-zero, so the chain stops.

**Outputs.**
- 3-1: `381_stage13/raw/b3_s10_3_1/<cond>/shard_XXX.npz`, `summary_b3_s10_3_1/` (gate.json, hardcheck.csv, rank_match.csv, layer_signal.csv, layer_tc.csv, onset.csv), report `reports/b3_3_1_report.md`.
- 3-2: the same names with `3_2`. The 3-2 report includes the 3-1 layers once those are complete.
- 3-3: `raw/b3_71b/paper_<id>.npz`, `summary_b3_71b/` (gate.json, hardcheck_rank_match.csv, hardcheck_rows.parquet, author/paper/group/pair_effects.csv), report `reports/b3_3_3_report.md`.
- Unit tests: `summary_b3_unittest/`. Tiny roots: `381_stage13/b3_tiny/`, `b3_tiny_pert/`.

## 2. Submit commands (main session, after batches 1 and 2; plan: afterany between batches, afterok within an item)

```
cd ~/jlens_work/13_stage13
# ---- 3-1: gate = all 7 conditions of shard 0 (+ hard check), ~10 min
sbatch --export=ALL,ITEM=3-1,MODE=gate stage13_b3_s10_gpu.sbatch
#   check: log lines "GATE ... PASS" and summary_b3_s10_3_1/gate.json status PASS; then the rest (self-chaining, then analysis):
sbatch --export=ALL,ITEM=3-1,MODE=all,AUTO=1 stage13_b3_s10_gpu.sbatch
#   optional 2nd/3rd parallel worker (claims prevent duplicates; only one job chains per round):
sbatch --export=ALL,ITEM=3-1,MODE=all stage13_b3_s10_gpu.sbatch
#   the last job submits stage13_b3_s10_analyze.sbatch (ITEM=3-1) by itself; by hand:
sbatch --export=ALL,ITEM=3-1,NEXT_GATE=1 stage13_b3_s10_analyze.sbatch      # NEXT_GATE=1 -> 3-2 gate on PASS
# ---- 3-2 (after the 3-1 analysis PASS): gate, then the rest
sbatch --export=ALL,ITEM=3-2,MODE=gate stage13_b3_s10_gpu.sbatch
sbatch --export=ALL,ITEM=3-2,MODE=all,AUTO=1 stage13_b3_s10_gpu.sbatch       # + 1-2 parallel MODE=all workers
# ---- 3-3 (independent of 3-1/3-2): gate = 7 papers with the 1,166 old contexts, then 43 papers
sbatch --export=ALL,MODE=gate stage13_b3_71b_gpu.sbatch
sbatch --export=ALL,MODE=all,AUTO=1 stage13_b3_71b_gpu.sbatch               # only if gate.json PASS (see section 3 and Q1)
```
After any sbatch error: check `squeue -u zhang.zhiqi2` and `sacct` before resubmitting (the chain step already prints squeue after an error).

## 3. Gate criteria

**3-1 / 3-2 (`summary_b3_s10_<item>/gate.json`; exit 3 on FAIL; `MODE=all` refuses unless PASS):**
- HARD: the L24 and L48 per-token ranks (logit and jlens_public, all 7 conditions, pooled) are exact on ≥ 99% of tokens.
- HARD: every other token is within 4 bf16 units. The unit is the shift of the gold logit, in bf16 units of the gold logit, that turns the new rank into the stored rank; it is computed in the job from the new logits.
- HARD: the paper-level title-specific signal at L48 (spec_mean_nlr) on the gate papers: the target mean and the control mean of the new values minus the published per-paper values (`paper_title_contrasts`) must be within 0.005.
- WARN: the share of papers within 0.005 should be ≥ 0.99.

**Full check in the analysis (exit 3 + `HARD_CHECK_FAILED` marker; the report is still written, with a FAIL banner):**
- the same rank rule on all 504 units;
- L48 target mean, control mean and target − control within bin vs the published `A_group_layer.csv` / `B_spec_target_vs_control_within_bin.csv`, |diff| ≤ 0.005, both readouts;
- per-pair and per-paper values are WARN only.

Expected: Stage 10 stored ranks were all made by this exact code (script sha 9107c80b, torch 2.11.0+cu128, A100-SXM4-80GB for all 72 shards of L24/L48 in every condition). On the same hardware, identical results are expected. The tiny CPU run reproduced the frozen `351_stage10.run` bit for bit (49,252 / 49,252 tokens).

**3-3 (`summary_b3_71b/gate.json`):**
- HARD (plan): the rank match over all scores of the 1,166 old 7.1B contexts must be ≥ 0.99 (7 papers, about 1,380 targets × 15 readouts).
- INFO, not in the plan: the share that is exact or within 4 bf16 units, the maximum |Δlogprob|, and a per-readout table.
- With `HC33_POLICY=plan` (the default), a FAIL exits 3 and `MODE=all` refuses to start.

**WARNING, predicted FAIL:** unit test P1 compared the Stage 10 fast-path ranks (stored, GPU) with the old 7.1B shuffle-0 rows for the same contexts (92 targets × 13 readouts; L16 is not stored in Stage 10). Only **93.5%** of ranks match exactly. By readout: logit 94.6%, J-lens 87–98%, final 97.8%. Ranks ≤ 41 match in 93–100% of cases.
- The same gap shows in `351_stage10/reports/crosscheck_stage6.csv` (fast path vs Stage 6: 77–95%) and in the Stage 10 parity runs (GPU fast path vs GPU per-prefix: about 90% at 52 positions, 1–1.5 bf16 units).
- The old 7.1B also ran layers 29–63 on the CPU.
- So the plan's 99% exact-rank criterion is very likely to fail on bf16 rounding alone, not because of a code error. See Q1.

## 4. Tests run (CPU, short)

All three jobs ran on CPU on the short partition. Tiny model = random 64-layer Qwen3 (same config and seed as the b2 tiny model), real tokenizer, random 64×64 lens, **real** cohort rows / prompts / conditions / 7.1B tasks.

| job | what | result |
|---|---|---|
| 11691113 b3_tiny (25 min) | full pipeline, 16 steps | Real-data unit tests: 22/23. The one failure was a test bug (U1 float32 rounding in the test itself), fixed and re-run in 11691544. The other 15 steps behaved as expected; details below. |
| 11691544 b3_unit | unit tests on real stored data | **25/25 OK**; details below. |
| 11691656 b3_tiny71w | 3-3 `HC33_POLICY=warn` path | Gate FAIL is recorded as WARN (exit 0). `--all` computed 2 more papers. Analysis exit 0: group tables written; the pair table is empty because the tiny papers contain no A–B pair. |

**11691113, steps after the unit tests:**
- tiny root built.
- The **frozen `351_stage10.run`** on the tiny model wrote the L24/L48 reference (shard 0, 7 conditions).
- **3-1 gate PASS:**
  - wrapper vs frozen path: 49,252 / 49,252 tokens bit-exact, 0 mismatches;
  - L48 paper-level |diff| = 0;
  - ~53 s per unit on CPU.
- Skip-if-exists: a re-run did 0 of 7 units.
- `remaining` printed 497.
- `chain --dry` gave the correct round-2 command.
- **Perturbed copy → gate-check exit 3; unperturbed → exit 0.**
- 3-1 analysis: report and CSVs written.
- **3-2 gate PASS** (52 pairs, ~100–130 s per unit on CPU). The 3-2 analysis also includes the 3-1 layers.
- **3-3:**
  - The old per-prefix 7.1B path (frozen Stage 5 `helper.readout`, sha-checked) on the tiny model gave the reference for 40 contexts.
  - The fast-path gate scored 885/885 reference scores, rank match **0.880 → FAIL → exit 3**.
  - `--all` refused (marker present), as designed.
  - The analysis exited 3 with a FAIL banner.
- So even on the same CPU and the same model, fast path vs per-prefix gives about 88% exact ranks. In the tiny model all mismatches fall in one title condition, with near-uniform, heavily tied logits, so the 4-unit distance is inf.

**11691544, unit tests on real stored data:**
- U1: bf16 distance function (numpy = torch; distance reaches the target rank; unit at 40 is 0.25; tie → inf).
- U2: rank rule:
  - identical → PASS;
  - 2% mismatches → FAIL;
  - 0.5% within 4 units → PASS;
  - 4.5 units → FAIL;
  - NaN → FAIL.
- **U3 (real, 6,841 papers):** stored Stage 10 L48 ranks through the b3 functions reproduce the published per-paper `spec_mean_nlr` (max 3.6e-15) and the published group means and within-bin t−c (≤ 1e-16) → PASS. Ranks ×1.03 → FAIL (|diff| 0.015–0.042).
- U4: `rank_rows` on stored ranks of shards 0–1 (94,444 tokens) → PASS; 3% perturbed at 9 units → FAIL.
- U5: the 1,166 old 7.1B contexts: identical → PASS; 2% perturbed → FAIL (0.980).
- U6: onset rule.
- **P1** (prediction, not a test): see section 3. Rank-exact share 0.935 → `summary_b3_unittest/p1_prediction_3_3.csv`.

One bug was found and fixed after the tiny run: `chain --dry` created the round marker. It now only prints. No other code change after the tests.

## 5. Shard counts, GPU time, storage

| item | units | per unit (A100, estimated from the Stage 10 logs) | GPU time | jobs (45 min) |
|---|---|---|---|---|
| 3-1 | 504 = 7 conditions × 72 shards (target + control rows, ~75% of each shard); 20 readout-layers | ~35 s (Stage 10: 46 s for 22 pairs on full shards) | ~5 h compute + ~5 min load per job → **~6.5 GPU-h** | gate (~10 min) + ~9 `all` jobs |
| 3-2 | 504; 52 readout-layers | ~50–60 s (tiny CPU: 2.5× the 3-1 unit time) | ~7–8 h → **~9 GPU-h** | gate + ~13 `all` jobs |
| 3-3 | 50 papers (7 gate + 43); 21 conditions × 227 authors = 4,767 forwards × 15 readouts | ~10–20 s per paper | **~0.5 GPU-h** | gate + 1 `all` job |

- Total ≈ 16 A100-hours. MAX_ROUNDS is 16 for 3-1/3-2 (≥ 13 needed for 3-2) and 4 for 3-3.
- Wall time drops about 3× with 3 parallel `MODE=all` workers. QOS allows 4 running and 8 queued.
- Storage: 3-1 ≈ 0.3 GB, 3-2 ≈ 0.7 GB, 3-3 < 0.05 GB. /scratch has 271 TB free (83% used); no per-user quota is visible.
- Estimates: the gate logs print the real seconds per unit (`gate.json` → `unit_seconds`).

## 6. Deviations / interpretations (explicit)

1. **D1 — no Stage 10 parity gate for the new layers.** `351_stage10.run` refuses readout-layers without a parity PASS. The wrapper does not call `run()`; it calls the same functions. The plan's L24/L48 reproduction check is the gate instead.
2. **D2 — unit layout.** One npz per (condition, shard) holds all readout-layers of the item, with rows = target + control contexts only (row_id stored). This differs from Stage 10's one file per (readout, layer, shard); the values are the same.
3. **D3 — the "4 bf16 units" rule.** It is applied to the gold logit's distance to the stored rank, as in section 3. Stage 10 never stored logits, so a direct logit comparison is impossible. |Δlogprob| is stored beside it (INFO).
4. **D4 — scope of the hard check.** It is pooled over L24 + L48, both readouts and 7 conditions (the plan's wording "of tokens"). Per pair it is WARN.
   - The paper-level check uses the published summary values: target, control and within-bin target − control at L48, for both readouts.
   - Per-paper agreement is a WARN (threshold 0.99 of papers within 0.005).
   - The gate uses shard-0 papers' group means against the published per-paper values.
5. **D5 — report CIs.** These are team-cluster bootstrap (archived team ids, 2,000 draws, seed 1414, one draw set for all cells). The published Stage 10 CIs were paper bootstraps, so stored-layer CIs differ from the published ones, but the point estimates are identical (U3: 1e-15).
   - "Onset" is literal: the first grid layer whose CI excludes 0, either sign. The first layer with lo > 0 and the sustained onset are given beside it.
   - Positions: first = token_index 0, later = token_index ≥ 1. Roles are the Stage 10 roles.
6. **D6 — layer grid.** The grid is L0–L24 (after 3-2), L32, L40–L62 and final L63. L25–L31 and L33–L39 are not in the plan, so they are never computed; the report states the grid.
7. **D7 — 3-3 fast path.**
   - One forward per (paper, condition, author). Contexts shared by two authors (e.g. the empty prefix) are scored in each author's own forward.
   - The lens is the Stage 10 registry `public` entry (sha 0af5ccf2, the 7.1B lens). Readouts map 7.1B `jlens` → `jlens_public` and `vanilla` → `logit`.
   - The 7.1B frozen files are verified with the frozen `verify()` (sources, task hashes, 15,519 tasks, 227 authors).
8. **D8 — 3-3 estimands.**
   - The plan.json estimand: true − mean of the 20 wrong titles, at the same prefix and next token.
   - Aggregation and pairing follow `351_stage7.py`: token → author (first / continuation / all) → paper, rr (JMRR) as the main metric, plus log10(1/rank) and logprob. Matched A − B uses the 20 Stage 5 pairs with the `351_stage7.ci` pair bootstrap (10,000 draws, seed 35171 + layer + len(metric); for the integrated rows, len(mode)). The 7-layer integral is also given.
   - Group means use a paper bootstrap (2,000 draws). All of this is labelled post hoc.
9. **D9 — `HC33_POLICY=warn`.** This option is not in the plan and is off by default. It lets 3-3 continue after a FAIL (recorded as WARN with its value and threshold), per the standing rule "a tolerance miss never stops GPU work". It may be used only if the user approves (Q1).

## 7. Open questions

1. **Q1 (3-3 hard check):** the P1 prediction is 93.5% < 99%, so the 3-3 gate will most likely FAIL on bf16 noise.
   - Options:
     - (a) keep the plan: the gate stops and 3-3 is not completed;
     - (b) the user approves `HC33_POLICY=warn` and the result is reported with the miss;
     - (c) the user replaces the criterion with the 3-1 rule ("exact or within 4 bf16 units on ≥ 99%"), which is already computed as INFO in gate.json.
   - The gate itself costs ~10 min, so it can be run first and the decision made on its numbers.
2. **Q2:** should the 3-1 analysis automatically submit the 3-2 gate (`NEXT_GATE=1`), or does the main session submit it by hand?
3. **Q3:** 3-1 and 3-3 can run in parallel (independent); 3-2 waits for 3-1. Confirm the order.
4. **Q4:** the 3-3 A − B pair table was not exercised in the tiny test (the tiny papers contain no pair). If that CPU step crashes, it can be re-run from the saved npz without the GPU (`stage13_b3_71b_analyze.sbatch`).

## 8. Wanted deletions (not done; ask the user)

- `381_stage13/b3_tiny/` (tiny Stage-10 root copy ~16 MB + tiny outputs)
- `381_stage13/b3_tiny_pert/` (perturbed copy for the exit-3 test)
- `381_stage13/summary_b3_unittest/` (can be kept as evidence)
