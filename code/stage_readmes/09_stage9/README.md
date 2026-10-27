# Stage 9 — Jacobian-lens fitting reliability (Fit A / Fit B / holdout)

**Question.** Can we fit our own J-Lenses reproducibly on generic text (WikiText-103)?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage9.py` | prepare | audit | preflight | fit: frozen WikiText-103 split 100/100/100, guarded fit, checkpoint audit |
| `stage9_runner.py` | seed | run | compare | check: immutable fitting runner |
| `stage9_fullfit.py` | plan | run | check: bounded, resumable full fits of A / B |
| `stage9_A_recover.py` | check | run: recovery of the Fit A run |
| `stage9_a_repair.py` | inspect | prepare | check | run: Fit A repair — jlens.fit skipped 1 of the 100 frozen prompts; one vetted 128-token WikiText-103 replacement appended → 100 valid of 101 (`full_A_repair_101_100valid/`) |
| `351_stage9_README.md` | original stage notes |
| `old_versions/` | superseded scripts |

## Run order

1. `351_stage9.py prepare` → `audit` → `preflight`
2. `stage9_fullfit.py run --half A|B` (GPU)
3. `stage9_a_repair.py inspect` → `prepare` → `check` → `run`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage9/` (lens used later: `runner_runs/full_A_repair_101_100valid/lens.pt`). **These are backup copies: the canonical scripts run from `/scratch/zhang.zhiqi2/jlens/`** (they load each other by absolute path). Fit B stopped at 66/100.

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
