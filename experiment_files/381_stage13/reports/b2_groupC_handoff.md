# Batch 2, group C: handoff (items 2-1, 2-2, 2-11 of addendum 12; C-3b of addendum 13)

Written 2026-11-06 by the group-C helper. **No GPU job was submitted.** No file was edited, deleted or cancelled; only new files were written.
Plans: `config/prereg_addendum12.json` (sha256 checked by every script at start), `config/prereg_addendum13.json` (be6d2c98...).

## 0. Column module (fixed rule 4)

There was no shared column module for Stage 13 (checked: none in `~/jlens_work`). New: `~/jlens_work/13_stage13/b2c_columns.py`. Every group-C script
imports it and calls `check(df, NAME)` before writing a result table. **Open question:** if helpers A/B made their own module, the main
session may want to merge them.

## 1. C-3b (CPU, DONE for real)

- Script `13_stage13/stage13_b2_c3b.py`, sbatch `stage13_b2_c3b.sbatch` (MODE=selftest|tiny|full).
- Jobs: selftest 11682460 (identical -> PASS, perturbed +1e-4 -> FAIL, missing row -> FAIL: OK); tiny 11682462 PASS; full **11682562 COMPLETED**.
- **Hard check PASS**: the published exclusion versions (Vpd, V5x0, V0; `summary_b1_e4b5/perdonor_by_run_layer.csv`) were recomputed here.
  Result: 189 rows x 14 columns, max |diff| 1.0e-16 (tol 1e-9). Primary V5x0/V0 cells equal `summary_b1_e4b5/primary_L40.csv` (no WARN).
- Without any exclusion, Vpd and V5x0 are the same quantity: true minus the mean of all 5 false titles. Both code paths agree.
  This version includes the title-reuse leakage, so it is a sensitivity check only.
- Result, L40, all 6,841 target+control papers (n differs by run):
  - surname_first **+0.077 [+0.071, +0.084]**. Published: Vpd +0.076 (n 4,654), V5x0 +0.072 (n 1,395).
  - initial **+0.034 [+0.029, +0.039]**. Published: Vpd +0.043, V5x0 +0.035.
  - surname - initial **+0.043 [+0.035, +0.051]**, paired +0.035 [+0.028, +0.042]. Published V5x0: +0.037 / +0.038.
- All-paper signal is positive (CI > 0) for every run x layer, the same as with exclusion.
- Target - control within bin turns CI > 0 at almost every run x layer, including the early and middle layers. The exceptions are initial L16 and given_cont L44.
  - With exclusion it was n.s. in many cells, mostly because n dropped to about 1,400.
  - Examples: surname_first L16 +0.021 [+0.010, +0.033], L40 +0.035 [+0.022, +0.048]. e4b_parity L40 +0.031 [+0.020, +0.043].
  - This repeats the C-3 pattern (first-token version). The flag list is in the report.
- Outputs: `summary_c13/c3b/{c3b_role_layer,c3b_primary_L40,c3b_hardcheck}.csv`, report `reports/c13_C3b.md` (the only report written).

## 2. Item 2-1: Stage 9 Fit B resume + holdout + Stage 10 signal (GPU; NOT submitted)

Files (`~/jlens_work/09_stage9/`): `stage9_b2_fitb.py`, `stage9_b2_fitb_{tiny,backup,gpu,analyze}.sbatch`. Root `381_stage13/b2_fitb/`.

- **Frozen path:** the resume runs `python /scratch/.../jlens/stage9_fullfit.py run --half B --confirm-fit` unchanged, under `timeout`.
  - Reason for `timeout`: the frozen code runs until 100/100 or the job is killed. jlens writes the checkpoint atomically after every prompt.
  - After the run, the frozen `check --half B` must pass.
  - The script refuses to start if the /scratch Stage 9 scripts differ from the `09_stage9/` copies.
- **Backup DONE** (job 11689934): `b2_fitb/checkpoint_B066.pt` + json, sha256 1318b7b9... = source, n_done 66.
  - Needed because the resume overwrites `checkpoint.pt` in place. The resume refuses to start without this backup.
- Hard checks:
  1. **Gate** (`UNIT=gate`, 1 GPU job, about 15 min).
     - Recompute prompt 66's Jacobian with the frozen loader (55 GiB GPU cap + CPU offload, the same `from_pretrained` arguments).
     - Compare max||J||/sqrt(d) (logged 4.367) and the running-mean change built from the backup sum (logged 1.08e-01).
     - Rule: |diff| <= half the last logged digit + 1e-3 relative. The seq_len must also match.
     - exit 2 on FAIL; the resume refuses to start without a PASS gate.
  2. **Plan hard check, literal** (`UNIT=recompute66`, then `hardcheck66` on CPU).
     - Refit prompts 1-66 in `b2_fitb/recompute66/`.
     - Compare S/66 with the backup, per-layer rel. Frobenius <= 1e-3.
     - exit 2 and `HARD_CHECK_FAILED`, which blocks the analysis. Costs about 6.2 GPU-h (see open question 1).
- tiny 11689919 **PASS** (8/8).
  - Covered: gate identical -> PASS / perturbed log -> FAIL; 66-check identical -> PASS / 1% -> FAIL.
  - The real frozen `check` reports done 66/100.
  - Holdout + read + analysis ran on real rows.
  - selftest OK.
- Holdout: 100 frozen holdout prompts (disjoint from fit_A, fit_B and the repair prompt). Per layer: KL(final||lens), top-1 / top-10 vs final, A vs B top-10.
- Stage 10 signal: 1,186-paper sample, 7 conditions, fitA and fitB in one forward, layers 16-62.
  - Reported: spec / total / topic, target, control, target - control, fitB - fitA paired.
  - Parity: our fitA ranks vs the stored Stage 10 `jlens_fitA` ranks, WARN if fewer than 95% equal.

## 3. Item 2-2: F1 split-half by author team (GPU; NOT submitted)

Files (`~/jlens_work/12_stage12/`): `stage12_b2_f1team.py`, `stage12_b2_f1team_{tiny,split,gpu,analyze}.sbatch`. Outputs under `371_stage12/`:
`config/b2_f1team_split.parquet`, `alens_team_{A,B}/`, `raw/alens_team_read/`, `summary/b2_f1team_*`. Report: `381_stage13/reports/b2_f1team_report.md`.

- Split: archived team ids, unique teams permuted with seed 1206, greedy fill of A to 20. Within each half the frozen fit order is kept. Split frozen by job 11690961: 40 distinct teams, A = 20 (15 target / 5 control), B = 20 (16 / 4).
- Fit: the Stage 12 F1 call unchanged (FIT_LAYERS 8 layers, dim_batch 1, max_seq_len 128, skip_first 16, checkpoint every prompt).
- **Hard check, deviation D2-2a:** J_all = (S_A + S_B)/40 from the two half checkpoints vs the stored F1 `lens.pt`, rel. Frobenius <= 1e-3 per layer.
  - jlens accumulates a plain sum, so this is the 40-prompt refit by the new wrapper up to summation order.
  - A literal third fit is implemented (`fit --half ALL`, about 3 GPU-h) and is compared too if it exists.
  - FAIL -> `B2_F1TEAM_HARD_CHECK_FAILED`, exit 2, no read unit starts.
- Read: teamA, teamB and the full F1 lens in one forward.
  - The full lens gives a parity check against the stored F2 ranks (WARN below 95% equal).
  - Top-10 ids are stored for the true condition, for the top-10 agreement.
- tiny: 11682581 FAILED (`s10.R10` attribute, fixed). 11682708 FAILED on two things, both fixed:
  - the resume tolerance was absolute 1e-4. It is now rel. Frobenius 1e-3; resume vs fresh 2.3e-4 (CPU fp32), and the old split-half tiny showed the same.
  - a path bug in the parity step.
- 11689897 **PASS** (7/7; hard check identical -> PASS, 1% -> FAIL; selftest OK).

## 4. Item 2-11: model-generated names (GPU; NOT submitted)

Files (`~/jlens_work/13_stage13/`): `stage13_b2_gennames.py`, `stage13_b2_gennames_{tiny,build,gpu,analyze}.sbatch`. Root `381_stage13/b2_gennames/`. Report: `reports/b2_gennames_report.md`.

- Data: the label package has `open_results.jsonl` (generated_text, names, m, h) but **no per-name M/H** (NameMatcher / elm are not on the cluster).
  - Deviation D2-11a: per-name labels are rebuilt with the Stage 10 R0/R1 matcher (`words`/`same` copied verbatim; generated-name side).
  - Only papers whose rebuilt counts equal the package m and h are kept.
- Prompt: system + user text verbatim from `step1_README.md`, put through `apply_chat_template(..., add_generation_prompt=True, enable_thinking=False)`, then the stored text. Tokenised with add_special_tokens=False (as judge2).
- Hard check: greedy (batch 1) reproduces the stored text up to the end of the first name for >= 90% of 50 papers (rng 1211).
  - It runs in the first GPU job before any shard. exit 2 + `HARD_CHECK_FAILED` on a miss.
- tiny 11689969 FAILED (bug in the bootstrap `np.unique` order, fixed). Rerun 11690954 **PASS** (7/7; selftest OK). Real CPU build 11690976 submitted (pending at handoff; writes `b2_gennames/build.json` with the kept/dropped counts).
- Tiny build on 400 papers: 399 kept, 2,120 names, **M 39 / H 2,081**, all M in target papers. Expect roughly 600-700 M names in total (open question 4).

## 5. Submit commands (main session; after batch 1)

```bash
# 2-11 (cheapest; ~0.7 GPU-h)
cd ~/jlens_work/13_stage13
b=$(sbatch --parsable stage13_b2_gennames_build.sbatch)                                   # CPU build
g=$(sbatch --parsable --dependency=afterok:$b --export=ALL,SHARD=0 stage13_b2_gennames_gpu.sbatch)   # gate: hard check + shard 0
# after the gate: check summary/repro_check.json (PASS >= 0.90) and raw/resid/shard_000.npz, then:
sbatch --export=ALL,ALL=1 stage13_b2_gennames_gpu.sbatch     # x2 if wanted; repeat until 48/48 shards
sbatch stage13_b2_gennames_analyze.sbatch                     # CPU probe + report, when 48/48

# 2-2 (~5 GPU-h)
cd ~/jlens_work/12_stage12
sbatch --export=ALL,UNIT=fit:A stage12_b2_f1team_gpu.sbatch   # gate: one fit chunk (~7 prompts); check progress.json, log
# then (A and B can run in parallel; repeat until both lens.pt exist; the hard check runs automatically):
sbatch --export=ALL,ALL=1 stage12_b2_f1team_gpu.sbatch ; sbatch --export=ALL,ALL=1 stage12_b2_f1team_gpu.sbatch
# after summary/b2_f1team_hardcheck.json = PASS: one read unit as a gate, then ALL=1 until 144/144, then
sbatch --export=ALL,UNIT=read:true:0 stage12_b2_f1team_gpu.sbatch
sbatch stage12_b2_f1team_analyze.sbatch

# 2-1 (~3.5 GPU-h + 6.2 GPU-h for the literal hard check)
cd ~/jlens_work/09_stage9
sbatch --export=ALL,UNIT=gate stage9_b2_fitb_gpu.sbatch       # gate (exit 2 on FAIL)
# after summary/gate.json = PASS: resume (repeat until fit_status.json exists, about 5 jobs; ONE at a time, same checkpoint)
sbatch --export=ALL,UNIT=resume stage9_b2_fitb_gpu.sbatch
# literal plan hard check, independent of the resume (repeat until 66/66; the last job runs hardcheck66):
sbatch --export=ALL,UNIT=recompute66 stage9_b2_fitb_gpu.sbatch
# after Fit B 100/100: holdout gate, then the rest
sbatch --export=ALL,UNIT=holdout stage9_b2_fitb_gpu.sbatch ; sbatch --export=ALL,ALL=1 stage9_b2_fitb_gpu.sbatch
sbatch stage9_b2_fitb_analyze.sbatch                          # SKIP_HC66=1 only if the literal check is waived
```

Gate criteria (each one checked by hand before submitting the rest):

| Item | Gate passes when |
|---|---|
| 2-11 | repro_check PASS; shard 0 names = names.parquet rows of shard 0; no non-finite values |
| 2-2 fit | progress.json advanced; log shows prompt times ≈ 270 s |
| 2-2 read | hardcheck PASS; read shard has the teamA/teamB/full keys; full vs stored F2 parity WARN-free or explained |
| 2-1 | gate PASS; resume: `check` OK and next_idx increased; holdout file written |

Do not run two resume jobs at the same time: the frozen code has no claim on its checkpoint.

## 6. Shard counts and GPU estimates (A100-80GB, 45-min jobs)

| Item | Units | Estimate |
|---|---|---|
| 2-11 | 48 paper shards (~143 papers), plus the 50-paper greedy check | ≈ 0.7 GPU-h, 1-2 jobs |
| 2-2 fit | 2 halves x 20 prompts at ≈ 270 s per prompt | ≈ 3 GPU-h, ≈ 5-6 jobs (2 in parallel) |
| 2-2 read | 6 conditions x 24 shards = 144 units at ≈ 40-60 s | ≈ 2 GPU-h |
| 2-1 gate | 1 prompt + load | ≈ 0.25 GPU-h |
| 2-1 resume | 34 prompts at ≈ 330 s, ≈ 7 prompts per job | ≈ 3.2 GPU-h, 5 jobs |
| 2-1 recompute66 | 66 prompts | ≈ 6.2 GPU-h, ≈ 9-10 jobs |
| 2-1 holdout + read | 1 + 7 conditions x 24 shards | ≈ 1.5 GPU-h |

## 7. Deviations (written down)

- **D2-2a.** The F1 "refit on all 40" hard check is the two-part accumulation (S_A + S_B)/40. A literal refit is optional (+3 GPU-h).
- **D2-11a.** Per-name M/H labels are rebuilt with the Stage 10 matcher, because the package has counts only. Papers with a count mismatch are dropped and the count is reported.
- **D2-1a.** The resume is stopped by `timeout` at the job budget, because the frozen code has no stop. A leftover `checkpoint.pt.tmp.*` is only reported, never deleted. The gate (prompt-66 check against the log) is an extra early check.
- **D2-1b.** The holdout and Stage 10 readouts use the Stage 10 fast loader (whole model on the GPU), not the Stage 9 offload loader. The fits themselves use the Stage 9 loader.
- **D2-1c.** CIs use the paper bootstrap (stage12_analyze.boot/strat), the scheme of the original Stage 10/F2 items. For 2-11 the CIs use the team bootstrap.
- **D2-2b.** The F2 CIs use the paper bootstrap, as published F2.
- **D2-11b.** The C for 2-11 is chosen by held-out log loss on fold 0, grid {0.001, 0.01, 0.1, 1}.

## 8. Open questions

1. Run the literal 66-prompt hard check (6.2 GPU-h)? The plan says yes. The cheap gate is the alternative.
2. Should the F1 literal 40-prompt refit be added (+3 GPU-h)?
3. Column module: merge `b2c_columns.py` with any module groups A/B created?
4. 2-11 has few M names (about 2% of written names, almost all in target R1 papers). Control AUROC will be undefined or very noisy (control has about 34 R1 papers). Report the pooled and target results as primary?
5. Wanted deletions (not done, ask the user): test roots `371_stage12/test_b2_f1team_*`, `381_stage13/b2_fitb_tiny_*`, `381_stage13/b2_gennames_tiny_*`, `summary_c13/c3b_tiny/`.

## 9. Addendum (after the report was handed back): 2-11 real CPU build 11690976 COMPLETED
- `b2_gennames/build.json`: 6,717 of 6,841 target + control papers kept; 35,027 written names; **M 686 / H 34,341**
  (target M 646 / H 23,353; control M 40 / H 10,988). Dropped: no names 40, rebuilt-count mismatch 13, name span not found verbatim 71, token map 0.
- Control has only 40 M names, so its AUROC CI will be wide; pooled and target are the informative subsets (open question 4).
- `names.parquet` / `papers.parquet` exist, so the GPU gate can be submitted without the build step: `sbatch --export=ALL,SHARD=0 stage13_b2_gennames_gpu.sbatch`.

## 10. VERSION 2 after the user's decisions (prereg_addendum12_deviations.json, sha256 c4c79365..., checked at every start). SUPERSEDES the v1 hard checks / analysis above.

New files beside v1. The v1 scripts are kept and imported by path:
- `09_stage9/stage9_b2_fitb_v2.py` + `_v2_{tiny,gpu,analyze}.sbatch`
- `12_stage12/stage12_b2_f1team_v2.py` + `_v2_{tiny,gpu,analyze}.sbatch`
- `13_stage13/stage13_b2_gennames_v2.py` + `_v2_{tiny,build,gpu,probe}.sbatch`
- Columns: `b2c_columns.py` gained GN2_* (additive).

**D12-1 (2-1).** Gate unit `gate_v2` (1 GPU job, about 25 min). Both parts must pass:
- (a) Fit A prompts 1-3 refitted with the loader of the stored runs and jlens.fit (layers 48 and 56). The result must be **bitwise** (`torch.equal`) identical to every stored Fit A prefix state:
  - A_n0001 (prompt 1, L56)
  - benchmark_A1_7layers (prompt 1, L48/L56)
  - A_n0002 (prompts 1-2)
  - fresh_A3 and resume_A3 (prompts 1-3)
- These prefix checkpoints are the only per-prompt quantities stored for Fit A. On disk, A_n0001 L56 == benchmark_A1 L56 and fresh_A3 == resume_A3 are already bitwise, so the stored states are reproducible across runs.
- (b) Fit B prompt 66 vs the log (v1 gate).
- Any miss -> `HARD_CHECK_FAILED`, exit 2. `resume` refuses to start unless gate_v2 is PASS. recompute66 is disabled.

**D12-2 (2-2).** Nothing per-prompt was stored for F1. Stored are only `alens/checkpoint.pt` (fp32 sum at 40/40, no skips), `lens.pt` = fp16(sum/40), and progress.json. Closest bit-exact comparison, at no extra GPU cost:
- The two half fits run as ONE pass over the 40 prompts in the original F1 order, with jlens' `jacobian_for_prompt` and the same fp32 `+=` accumulation. Each J goes to S_all and to S_A or S_B.
- (a) S_all must be **bitwise** equal to the stored sum, and fp16(S_all/40) bitwise equal to the stored lens.pt (k = 40 original prompts).
- (b) (S_A+S_B)/40 vs lens.pt, rel. Frobenius <= 1e-3.
- Any miss = FAIL. Fit jobs are sequential: one at a time, enforced by a claim.

**D12-3 (2-11).**
- (a) Rebuilt per-paper M/H/U must equal the package m/h/u (u = n_authors - m holds for 9,108/9,108). Papers that differ are excluded and counted.
- (b) Primary = target papers with at least 1 M and at least 1 H: within-paper AUROC (pairs within paper), team-cluster bootstrap with 2,000 draws.
- (c) Baselines: position (index, relative index) and string (length, log cohort full-name frequency). Signal = both difference CIs > 0.
- (d) Control is descriptive only (no CI). The pooled AUROC is kept as a reference.
- Root `381_stage13/b2_gennames_v2/`.

### v2 submit commands (main session; no GPU job submitted by me)
```bash
# 2-11  (build 11691150 = CPU, already submitted; gate = greedy check + shard 0)
cd ~/jlens_work/13_stage13
sbatch --export=ALL,UNIT=0 stage13_b2_gennames_v2_gpu.sbatch      # gate: repro_check.json PASS (>=0.90), raw/resid/shard_000.npz
sbatch --export=ALL,ALL=1 stage13_b2_gennames_v2_gpu.sbatch       # rest, until 48/48
sbatch stage13_b2_gennames_v2_probe.sbatch                         # CPU, report reports/b2_gennames_report.md
# 2-2
cd ~/jlens_work/12_stage12
sbatch --export=ALL,UNIT=fit stage12_b2_f1team_v2_gpu.sbatch       # gate: ~7 prompts; check log "joint fit prompt k/40", per-prompt ~270 s
sbatch --export=ALL,UNIT=fit stage12_b2_f1team_v2_gpu.sbatch       # repeat ONE AT A TIME until 40/40 (~5 jobs); hard check runs at 40 (exit 2 on FAIL)
sbatch --export=ALL,UNIT=read:true:0 stage12_b2_f1team_v2_gpu.sbatch   # read gate (after hardcheck PASS)
sbatch --export=ALL,ALL=1 stage12_b2_f1team_v2_gpu.sbatch          # rest of 144 read units (2 jobs in parallel OK)
sbatch stage12_b2_f1team_v2_analyze.sbatch
# 2-1
cd ~/jlens_work/09_stage9
sbatch --export=ALL,UNIT=gate_v2 stage9_b2_fitb_v2_gpu.sbatch      # gate (D12-1 a+b), exit 2 on FAIL
sbatch --export=ALL,UNIT=resume stage9_b2_fitb_v2_gpu.sbatch       # after gate_v2 PASS; ONE AT A TIME until fit_status.json (~5 jobs)
sbatch --export=ALL,UNIT=holdout stage9_b2_fitb_v2_gpu.sbatch ; sbatch --export=ALL,ALL=1 stage9_b2_fitb_v2_gpu.sbatch
sbatch stage9_b2_fitb_v2_analyze.sbatch
```
GPU estimates under v2 (A100-80GB):

| Item | Estimate |
|---|---|
| 2-11 | about 0.7 h (1-2 jobs) |
| 2-2 | joint fit about 3 h, sequential (5 jobs) + read about 2 h |
| 2-1 | gate_v2 about 0.4 h + resume about 3.2 h (5 jobs) + holdout/read about 1.5 h |
| Total | about 11 A100-h (v1 with the literal checks would have been about 20 h) |

### v2 tests: PENDING at handoff (short partition queue, Priority). Check these before any v2 GPU submission:
- 11691147 `b2c_fitb2_tiny`, log `381_stage13/logs/b2_fitb_v2_tiny_<id>.log`: needs "SELFTEST v2 ... OK" and "TINY v2 PASS". The test covers the chunked refit == stored prefix states bitwise, and a one-ulp change -> FAIL.
- 11691148 `b2c_f1t2_tiny`, log `371_stage12/logs/b2_f1team_v2_tiny_<id>.log`: needs "TINY v2 PASS". The test covers the joint 40-prompt fit in 2 chunks being bitwise equal to the stored jlens.fit, (b) PASS, a one-ulp stored sum -> FAIL, and read + analyze.
- 11691149 `b2c_gn2_tiny`, log `381_stage13/logs/b2_gennames_v2_tiny_<id>.log`: needs "TINY v2 PASS".
- 11691150 `b2c_gn2_build` (real CPU build): writes `b2_gennames_v2/build.json`, which holds the D12-3(a) exclusion count. Expected about 13 count mismatches, based on the v1 build.

Risk to read before trusting the tiny bitwise checks. On CPU, the v1 tiny showed resumed vs fresh fits differing by a relative 2.3e-4, while fresh vs fresh was 0. The v2 tinies set `torch.use_deterministic_algorithms(True)` and 1 thread.
- If a v2 tiny still fails only on bitwise equality, that is a CPU-test artefact, not a code bug: the GPU evidence (A_n0001 == benchmark_A1, fresh_A3 == resume_A3) is bitwise.
- Even so, under D12-1/D12-2 a real GPU miss is a hard FAIL.

### v2 tests DONE: 11691147 (2-1), 11691148 (2-2), 11691149 (2-11) all "TINY v2 PASS"
- The bitwise prefix refits in the tiny runs were identical.
- One-ulp changes -> FAIL.
- The 2-2 joint fit in 2 chunks was bitwise equal to jlens.fit.

Orchestrator:
- `status` subcommand in each v2 script: fast, stdlib only, via `13_stage13/b2c_status.py`.
- Items file: `13_stage13/b2_orch_items_c.json`.
- 2-11 real build 11691150 was running at writing; `status` says wait_tests until build.json exists.
- The 2-11 gate uses `UNIT=0` (passed to `--shard`).
