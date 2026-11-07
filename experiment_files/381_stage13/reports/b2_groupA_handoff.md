# Batch 2, group A handoff (2026-11-06): addendum 11 A (name-position probe), addendum 12 items 2-7 and 2-9

Helper A. No GPU job was submitted. Nothing was deleted or cancelled. No frozen file was edited. The plans are checked by sha256 at run time (addendum 11 `prereg_addendum11.json.sha256`, addendum 12 `prereg_addendum12.json.sha256`).

## 1. Files (all new, in `~/jlens_work/13_stage13/`)

| file | role |
|---|---|
| `stage13_b2A_cols.py` | Column module (rule 4) for these items: layers, conditions, run/role names, raw keys, result columns, tolerances. No project-wide column module existed, so this one covers only the new group-A files. |
| `stage13_b2A_checks.py` | Pure hard-check functions: rel-norm, table-vs-table, scalar, combine. |
| `stage13_b2A_hcunit.py` / `.sbatch` | Unit tests for every hard check, on real published data. |
| `stage13_b2_np_gpu.py` / `_gpu.sbatch` | Add. 11 A GPU step. Records residuals at L32/40/48/52/56 at every name-predicting position (j=0 is ':'), for true + false_0..4, all 72 shards. Recomputes true-title L63 (HARD 1). Also stores logit-lens ranks for a WARN check against Stage 10. |
| `stage13_b2_np_lens.py` / `_lens.sbatch` | Lens comparison input (Stage 10 logit + public J-lens, same tokens) + HARD 2. CPU only. |
| `stage13_b2_np_probe.py` / `_probe.sbatch` (array 0-4 = layers) | Ridge probe per layer × run (colon_first, initial, given_first, given_cont, surname_first, surname_cont). Also computes the controls, title-reuse flags and ceiling. |
| `stage13_b2_np_report.py` / `_report.sbatch` | Writes `reports/b2_np_report.md` and `summary_b2_np/np_*.csv`. Exits 3 if HARD 1 or HARD 2 failed or is missing. |
| `stage13_b2_np_tiny.sbatch` | Whole-pipeline tiny test for add. 11 A. |
| `stage13_b2_ps_gpu.py` / `_gpu.sbatch` | 2-7 + 2-9 GPU step. X4 patchscope (batch 7, as published) with the source at title / ':' / every name-predicting position. Output is per answer token. |
| `stage13_b2_ps_analyze.py` / `_analyze.sbatch` | Analysis: 2-7 D tables, earliest layer, recognition, text baseline; 2-9 x4tok at all layers for title / colon / name_all; hard checks. `ARGS=--partial` runs the one-shard gate. |
| `stage13_b2_ps_tiny.sbatch` | Whole-pipeline tiny test for 2-7 / 2-9. |

Outputs:
- `raw/b2_npprobe/<cond>/shard_XXX.npz`, `summary_b2_np/{checks,probe}/`, `reports/b2_np_report.md`
- `raw/b2_pscope/{shard,none}_XXX.parquet`, `summary_b2_ps/`, `reports/b2_ps_report.md`, `reports/b2_ps_partial_check.md`
- Claims are in `logs/claims_b2_{np,ps}/`.

## 2. Tests run (CPU, short)

| job | what | result |
|---|---|---|
| 11682908 b2np_tiny | Random 64-layer Qwen3 (same seed/config as the add. 9 tiny model), real shards 0-1, 6 conditions → lens → probe at 5 layers → report | COMPLETED, all steps ran. HARD 1 PASS (rel 0.019 ≤ 0.05, see D9). HARD 2 PASS 20/20. Report written. R-check WARN as expected (random model). |
| 11682909 b2ps_tiny | Random 2-layer model, 3 real papers | GPU code 8/8 checks PASS. Title/colon/none match the frozen `do_pscope` to 9e-16. Per-token author title matches the frozen `x4tok` (b7) exactly. Analysis hard-check path PASS against the frozen `x1x4_analyze.x4` run on frozen outputs. |
| 11682911 b2np_lens | **Real** lens table + HARD 2 (all 9,108 papers) | **PASS 28/28.** Group means of `A_group_layer.csv` (all / surname_first; logit / J-lens; L40, L48) and target+control role means all match. Per-paper max diff vs `paper_title_contrasts` is 2.7e-15. Outputs: `summary_b2_np/lens_perpaper.parquet`, `hardcheck2.json` (usable as is). |
| 11689896 b2A_hcunit | Hard-check unit tests | **17/17 OK.** Identical input → PASS, perturbed input → FAIL for each check. The new estimators reproduce the published `x4_decodability.csv` from raw/pscope (D and CI to 1e-16; test/author/title/L8 = 0.04646) and `x4_rolesplit.csv` from x4tok2 (8e-17). |

Earlier I also ran quick debug runs of `np_lens --tiny` and `ps_gpu/ps_analyze --tiny` interactively on my srun node (seconds, tiny model). They left `b2_ps_tiny/raw/b2_pscope_dbg1` and `b2_ps_tiny/ref_dbg1`.

## 3. Cost estimate

**Add. 11 A GPU:**
- 432 units (6 conditions × 72 shards).
- Add. 9 measured about 30 s per shard and condition on an A100; with 5 layers plus logit ranks, expect about 35–45 s.
- Total about 4.5–5.5 GPU-h: about 8 jobs of 45 min (about 55 units each), 4 in parallel → about 1.5–2 h wall time.
- Storage: 149,999 rows × 5 layers × 5,120 × 2 B × 6 ≈ **46 GB** fp16. The plan said about 55 GB.
- /scratch: 273 TB free on the filesystem; I use 128 GB. `quota` is not readable (Operation not permitted), so no per-user limit is visible.

**Probe (CPU):** 5 array tasks of about 0.5–1 h each (16 cores, 64 GB).

**2-7 / 2-9 GPU:**
- 24 shards. Per paper: (2 + Σ(len−1) ≈ 14.8 sources) × 3 targets × 2 (self/partner) forwards of batch 7, at about 0.077 s each (measured from X4).
- That gives about 6–7 min per shard, about 2.6 GPU-h in total: about 4–5 jobs.
- Output under 0.2 GB.

## 4. Submit commands (from `~/jlens_work/13_stage13`, after batch 1 has finished)

(a) One real shard gate each:
```
sbatch --export=ALL,SHARDS=0 stage13_b2_np_gpu.sbatch      # 6 units of shard 0, ~5 min
sbatch --export=ALL,SHARDS=0 stage13_b2_ps_gpu.sbatch      # sample shard 0, ~8 min
# after the ps gate job ends:
sbatch --export=ALL,ARGS=--partial --dependency=afterok:<ps_gate_jobid> stage13_b2_ps_analyze.sbatch
```

Gate criteria:
- **np gate:**
  - log line `true shard 000 ... HARD1 PASS` (expected rel_max ≈ 0 and bitexact ≈ 1 on the same A100 code path; hard limit 0.05);
  - `summary_b2_np/checks/*_shard_000.json`: R_match_L* ≥ 0.95 for all 6 conditions (WARN only: if it is lower, note the value and continue);
  - fp16_status OK;
  - no `logs/b2_np_error_*`.
- **ps gate:**
  - `summary_b2_ps/hardcheck_partial.json` status PASS: the shard-level title D for every answer × layer, and the x4tok L8/L40 role means, are within 0.005 of the published raw on the same papers;
  - `reports/b2_ps_partial_check.md` per-paper exact share ≈ 1;
  - check json `pscope_max_abs` / `x4tok_max_abs` ≈ 0.

(b) The rest (skip-if-exists + claims, so resubmitting is safe; each job stops about 5–6 min before 45 min):
```
for i in 1 2 3; do sbatch --export=ALL,SHARDS=--all stage13_b2_np_gpu.sbatch; done   # resubmit until 432 npz exist
for i in 1 2;   do sbatch --export=ALL,SHARDS=--all stage13_b2_ps_gpu.sbatch; done   # until 24 shard parquet exist
# when ls raw/b2_npprobe/*/shard_*.npz | wc -l == 432:
P=$(sbatch --parsable stage13_b2_np_probe.sbatch); sbatch --dependency=afterok:$P stage13_b2_np_report.sbatch
# when 24 ps shards exist:
sbatch stage13_b2_ps_analyze.sbatch          # full hard checks vs published CSVs; exit 3 = FAIL
```

Notes:
- HARD 2 is already done (job 11682911). Re-running `stage13_b2_np_lens.sbatch` is optional.
- The probe refuses to run if any of the 432 units is missing.
- `HARD_CHECK1_FAILED` in `summary_b2_np/` stops all later np jobs, the probe and the report.

## 5. Deviations / interpretations (written down, not silent)

- **D1** ':' position = the token_index-0 rows (each author's first name token is predicted at ':'). The ':' residual is identical for all authors of a paper, so these rows are duplicates within a paper. They are kept per row as in the plan's position set.
- **D2** Permutation controls are scored per position. The plan's "gold tokens of a random other paper" has no per-position mapping, so each prediction row of paper m is scored against every role-r gold token of the permuted paper, and the scores are averaged. The permutation is drawn as in `stage13_b1_e4b5_probe` (default_rng(3712), over the run's paper list, then within field).
- **D3** HARD 2 is checked two ways: (a) against the published `A_group_layer.csv` group means (all tokens and surname_first, the subsets Stage 10 published); (b) target+control means per role against the published per-paper `paper_title_contrasts` columns. given_cont and the ':' run have no published Stage 10 value, so they are not part of HARD 2.
- **D4** 2-7 source prompt: the source is the X4 authors prompt (no year anywhere), not the Stage 10 prompt with the year. With the year in the source, the year target would be read off the prompt.
- **D5** 2-7 partner source at name positions: partner B's title followed by **A's** author tokens. This keeps the positions aligned, and the gold first-author tokens seen by the source cancel in self − partner.
- **D6** 2-7 layers: all 7 X4 layers (L8–L56) are patched in one batch of 7, as published, because the batch configuration changes ranks (x4tok audit). The plan lists L16–L56; L8 is extra and needed for the hard check.
- **D7** The 2-7 hard check covers all 63 title-source cells (stricter than the single named value), and also the named value test/author/L8 0.046. Colon-source cells are compared too, but WARN only.
- **D8** The text baseline (X4 v2) is the stored per-paper file. It does not depend on the source position and is not recomputed.
- **D9** The tiny HARD 1 was not bit-exact (rel 0.019). The CPU bf16 tiny model ran on a different node from the add. 9 tiny run. On the real A100 the code path is identical to add. 9, so near-exact agreement is expected; the plan tolerance is 0.05.
- **D10** The H3 contrast "lens smaller than probe" is applied literally, but it compares a full-vocabulary rank with a rank within the 9,137 name tokens. The report flags this and shows the CI criterion beside it.
- **D11** Expect the 5-donor exclusion to leave fewer than 1,000 target+control papers (batch 1: 0). V5x0 (false_0-only exclusion) is then shown beside V5 by the plan rule, and the group split uses it.

## 6. Open questions / requests

- rm, only if the main session or user approves: `381_stage13/b2_ps_tiny/` (debug + tiny raw, < 5 MB) and `381_stage13/b2_np_tiny/` (about 30 MB). Both are harmless to keep.
- Rule 4: is a project-wide column module wanted? Groups B and C may have made their own.
- GPU numbers above are estimates. The gate logs give the real per-unit time; adjust the number of `--all` jobs to match.
