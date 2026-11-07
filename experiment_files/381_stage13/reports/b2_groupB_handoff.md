# Batch 2, group B: handoff (addendum 11 B; addendum 12 items 2-3, 2-4, 2-8, 2-10)

Written 2026-11-06 by the group-B helper. **No GPU job was submitted.** Only new files were written. No existing file was edited, nothing was deleted, and nothing was cancelled. Both plan files pass their sha256 check: prereg_addendum11.json (58e76160…) and prereg_addendum12.json (c97533d5…).

## 1. Files (all new)

| file | role |
|---|---|
| `~/jlens_work/13_stage13/b2_groupB_cols.py` | **The column module (rule 4) for group B.** Holds the raw npz keys, result-CSV columns and token roles; `write_csv` refuses a frame with missing declared columns. No project-wide column module existed before, so this one covers group B only (see open question 1). |
| `~/jlens_work/14_groups/b2_cd.py` | Item 1 (addendum 11 B): freeze / tiny / work (`--gate` / `--all`) / check / remaining / analyze / unittest. It loads `rerun_gpu.py` by path and calls `FUN['patch']` / `FUN['knockout']` (the frozen `s11.do_patch` / `do_knockout`) without changes. The analysis loads `rerun_analyze.py` by path. |
| `~/jlens_work/14_groups/b2_cd_{freeze,tiny,gpu,analyze}.sbatch` | freeze (CPU, **already run**), tiny + unittest (CPU), gpu (MODE=gate or all, AUTO chain), analyze (CPU; re-runs the hard check first and exits 3 on FAIL). |
| `~/jlens_work/13_stage13/stage13_b2B_gpu.py` | GPU units for 2-4 `e1noise`, 2-8 `e1t5`, 2-3 `x3tok`, 2-10 `m3tok`, plus the gate checks. Frozen code is loaded by path: `361_stage11` via `rerun_gpu`, and `381_stage13` / `stage13_x3_tok_gpu`. |
| `~/jlens_work/13_stage13/stage13_b2B_analyze.py` | Analyses `e1noise`, `e1t5`, `x3role`, `m3tok`; also `hardcheck_e1t5` (CPU), `unittest` and `tiny`. Exit code 3 means a hard check failed. |
| `~/jlens_work/13_stage13/stage13_b2B_{tiny,gpu,analyze}.sbatch` | tiny (CPU), gpu (MODE=gate or all, optional TYPES, AUTO chain), analyze (ITEMS=…; each item runs; exit 3 if any hard check fails). |

Every sbatch file mails on END,FAIL. The GPU files request gpu-short,gpu-interactive, a100@80g, 45 min (budget 38 min, minus a 6-min safety margin), claims plus skip-if-exists, and atomic saves. A failed logging step never kills a job. A unit crash is treated as a code crash: the job exits non-zero and the chain stops.

## 2. Outputs

- **Item 1:** `391_groups/b2_cd/{raw/<patch|knockout>/<C|D>/, check/, claims/, summary/}` and the report `391_groups/reports/b2_cd_report.md`.
  - Frozen lists, written by job 11682518: `391_groups/config/b2_cd_C.parquet` (475 papers, 10 shards, sha 2d832a6b…), `b2_cd_D.parquet` (29 papers, 1 shard, sha 1f5a33fe…), and `b2_cd_freeze.json`.
  - The tiny job re-froze both lists into its own test root and got byte-identical sha256 values.
- **Items 2-x:**
  - raw data in `381_stage13/raw/b2_{e1noise,e1t5/<false_k>,x3tok,m3tok}/`;
  - summaries in `381_stage13/summary_b2B/` (gate.json, hardcheck_*.json, CSVs);
  - reports `381_stage13/reports/b2_{e1noise,e1t5,x3role,m3tok}.md`.

## 3. Submit commands (main session; GPU only after batch 1)

```
# Item 1: one-real-shard gate (Stage 11 shard 0 re-run E1+E2 = hard check, then C shard 0 E1+E2)
cd ~/jlens_work/14_groups && sbatch --export=ALL,MODE=gate b2_cd_gpu.sbatch
# Inspect the log + 391_groups/b2_cd/summary/hardcheck_rerun.json; if PASS:
sbatch --export=ALL,MODE=all,AUTO=1 b2_cd_gpu.sbatch        # self-chains (<= 4 rounds), then submits b2_cd_analyze.sbatch

# Items 2-4 / 2-8 / 2-3 / 2-10: one real shard each
cd ~/jlens_work/13_stage13 && sbatch --export=ALL,MODE=gate stage13_b2B_gpu.sbatch
# Inspect 381_stage13/summary_b2B/gate.json + log; if PASS (or only WARN):
sbatch --export=ALL,MODE=all,AUTO=1 stage13_b2B_gpu.sbatch  # self-chains (<= 8 rounds), then submits stage13_b2B_analyze.sbatch
# Optional: run 2 jobs in parallel (claims prevent duplicate units): submit the MODE=all line twice, or once with TYPES=e1t5 and once with TYPES=e1noise,x3tok,m3tok.
```

## 4. Gate criteria

**Item 1** (hard, as in addendum 8):
- The re-run of Stage 11 shard 0 must reproduce the stored `361_stage11/raw/{patch,knockout}/shard_000.npz`: identical rows, and the shard-level E1 recovery and E2 loss at every layer within |diff| ≤ 0.005.
- If it fails, the job exits 3 and no new unit is run.
- A rank-equality share below 1 is only a WARN.

**Items 2-x** (`gate.json`):
- **HARD:** the e1noise original-batch arms must reproduce stored `raw/patch` shard 0. Rows must be identical and the recovery at every layer within 0.005.
- **HARD:** the e1t5 false_0 re-run must reproduce stored `raw/patch_title` shard 0, with the false baseline taken from the L63 element.
- **Gross-mismatch guard (exit 3):** for x3tok and m3tok shard 0, mean |d| > 0.1 against the stored per-author scores stops the job. A value in 0.005–0.1 is a WARN and the run continues; ≤ 0.005 is a PASS.
- MODE=all refuses to run if `gate.json` says FAIL.

**Plan hard checks in the analyses** (exit 3 on failure):
- **1:** re-checked before the analysis runs.
- **2-8:** the false_0 arm must reproduce the published `E1t_recovery.csv` (threshold 0.005). In addition, the frozen `patch_section` re-run must match the published values including CIs (threshold 1e-9).
- **2-3:** first author, role ALL must reproduce the published `x3_behaviour.csv` / `x3_recovery.csv` (threshold 0.005).
- **2-10 (updated 2026-11-06 evening, main-session decision):** the HARD check now uses `m3_first_exact`. This is the first author's first token scored by the exact published path, one extra prompt-only batch-1 forward per paper (`do_task`: last-block state at ':' → unembed). It must reproduce the `author_first_nlr` cells of `m3_scores_summary.csv` (group means plus the four target − control values; threshold 0.005). The in-sequence first token (`m3_first_first`) is compared with the same cells as a **WARN-only** number (value + threshold 0.005). Per-paper agreement of both arms is WARN only. The gate guard for m3tok shard 0 also uses the exact arm.
- **2-4:** the original arms must reproduce the stored shards 0 and 6.

## 5. Tiny tests and unit tests (CPU, short)

| job | result |
|---|---|
| 11682518 b2cd_freeze | real lists frozen (C 475 / 10 shards, D 29 / 1 shard; Stage 11 overlap 36 / 5 excluded) |
| 11682519 b2cd_tiny | crashed: `np.savez` got `meta` twice (test-harness bug, fixed) |
| 11682593 b2cd_tiny | **all 10 tiny checks PASS** (freeze counts, driver re-run identical to the frozen path, hard check identical → PASS / perturbed → FAIL, skip-if-exists, remaining, analysis, column module). **Unittest on stored shard 0:** identical → PASS, E1 perturbed → FAIL, E2 row order perturbed → FAIL. |
| 11682874 b2B_tiny | **GPU-part 14/14 PASS**: noise shards by rule = [0, 6]; L63 of the 15-batch equals true; e1t5 false_0 through the driver is bit-identical to the frozen path; FALSE_FOR_PATCH is restored; x3tok mean equals the frozen `score_tf`; gate identical → PASS / perturbed → FAIL. **Analysis 8/8 PASS.** **Unit tests 8/8**: identical → PASS and perturbed → FAIL for each of 2-4, 2-8, 2-3 and 2-10. **Real CPU hard check 2-8 PASS**: point max |diff| 1e-16 over 36/36 cells; the frozen re-run including CIs has diff 0. |

The tiny `gate.json` shows FAIL for x3tok / m3tok. This is expected: it compares random-model scores with the stored real-model scores. It was written only inside the tiny root.

## 6. Shard counts and GPU time (A100-80GB)

| item | units | estimate |
|---|---|---|
| 1 C/D E1+E2 | 2 check + 11 shards × 2 | E1 ≈ 60–85 s and E2 ≈ 20–25 s per shard (addendum-8 logs) → **≈ 25 min**: gate job ≈ 6 min + one `all` job |
| 2-4 e1noise | 2 (shards 0, 6) | ≈ 5 min/shard (E1 plus 3 batch-1 and 2 batch-15 extra forwards) → ≈ 10 min |
| 2-8 e1t5 | 1 check + 96 | ≈ 60–70 s/unit → **≈ 1.8 h** |
| 2-3 x3tok | 24 | ≈ 30 s/shard (b1_xall para: 448 forwards in 27 s) → ≈ 12 min |
| 2-10 m3tok | 72 | 33,811 author forwards + 9,108 exact prompt-only forwards, batch 1, about 60 ms each → ≈ 45 min |

Total ≈ **3.4 A100-hours**. That is about 1 job for item 1 and about 6–7 jobs of 38 min for items 2-x; the gate job takes about 15 min.

## 7. Deviations (explicit)

1. **Item 1 shard count:** the plan says "10 shards of 50". With 475 + 29 papers there are 11: C has 10 and D has 1, because the two lists are kept separate, 50 papers per shard as in Stage 11 / addendum 8.
2. **Item 1 hard-check tolerance:** addendum 8 checked "within bf16 batch noise" and only warned. Here the check is hard, with |diff| ≤ 0.005 on the shard estimand (the batch-1 tolerance). Rank equality below 1 is a WARN.
3. **Item 1 within-bin bin rules:** C − A uses bins with ≥ 10 C and ≥ 10 A papers (addendum 7 P2). D − B uses ≥ 1 D and ≥ 10 B and is descriptive. C − D uses ≥ 1 / ≥ 1 and is descriptive. Plain differences are reported beside every within-bin value.
4. **2-4, unpatched runs:** the original unpatched true / false_0 runs used batch 1, so for them "original batch size" already means batch 1. The comparison arm is therefore 15 identical copies in one batch, element 0, matching the size of the patched batch. Whether all 15 copies agree is stored.
5. **2-4, shard choice:** "target-heavy" and "control-heavy" are implemented as the lowest-index shard with the highest target share (6, 100% target) and the lowest-index shard with the highest control share (0, 100% control).
6. **2-8 intervals:** the main CI uses the original E1t scheme (paper bootstrap, 2,000 draws, rng 3611), with one index draw shared by all titles so the comparison is paired. This follows the addendum-12 rule "unless the original item used another scheme". The team-cluster CI (seed 391) is given beside it.
7. **2-3 author aggregation:** "all authors" means the mean over the paper's authors of the per-author role means, as in the batch-1 strata. Pairs with no token of a role drop out of that role. Recovery cells with O − D < 0.05 are flagged under the addendum-4 gap rule.
8. **2-10 primary score:** the primary paper score is the token mean over all authors' name tokens (Stage 10 averaging). The author-mean variant and the other variants are given beside it.
   - The first token is scored inside the prompt+name forward. The original prompt-only forward was batch 1 and shorter, so bf16 differences per paper are possible.
   - For that reason the hard check is on the published summary numbers, and per-paper agreement is a WARN.
10. **2-10 extra forward:** one prompt-only forward per paper is added beside the plan's all-token runs. It serves only the hard check, so that check compares like with like (main-session decision).
9. **2-3 / 2-10 gate guard:** the plan has no shard-level check for these items. I added a gross-mismatch stop at mean |d| > 0.1 to guard against code errors. It is not a tolerance hard check.

## 8. Open questions

1. **Rule 4:** decided by the main session: keep one column module per group (`b2_groupB_cols.py` for group B); no merge.
2. **2-3 / 2-10:** both items need GPU, because the per-token scores were never stored. `raw/b1_xall/para` holds only per-author means, `raw/para_tok` (V51) was never run, and `raw/task` holds only the first author's first token. Neither item can be done on CPU alone.
3. ~~2-10 exact forward~~ **decided (main session): added.** Raw npz keys `exact_paper_id` / `exact_first_rank` (column module updated). Re-tested in **11689951 b2B_tiny: all PASS**. The new tiny check shows that on the fp32 tiny model the exact prompt-only first-token rank equals the in-sequence rank (causal). Unit tests: 8/8 (2-10 identical → PASS, +0.01 → FAIL on the exact column). The 2-8 real hard check PASSES again.

## 9. Wanted deletions (not done; ask the user)

- Tiny test roots (also `381_stage13/b2B_tiny_11689951`):
  - `391_groups/test_b2_cd_tiny_11682519` (the crashed run)
  - `391_groups/test_b2_cd_tiny_11682593`
  - `381_stage13/b2B_tiny_11682874`
- Unit-test outputs: `381_stage13/summary_b2B/unittest/` (can be kept as evidence).
