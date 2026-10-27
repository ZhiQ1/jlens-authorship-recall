# Stage 7.3 — gold advantage after a wrong-title background (Pilot50 × 20 wrong titles)

**Question.** Does the gold advantage remain after subtracting the wrong-title background?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage7_3.py` | freeze | audit (CPU): 20 metadata-matched wrong titles per paper (7.3A) |
| `351_stage7_3_score.py` | audit | run (GPU) | analyze: shuffled-title scores and empirical null, Title Advantage (7.3B/C) |
| `351_stage5.py` | symlink to `../05_stage5/351_stage5.py` — do not delete |
| `351_stage7_3_full.tar.gz` | archived results |

## Run order

1. `351_stage7_3.py freeze` → `audit`
2. `351_stage7_3_score.py audit` → `run` → `analyze`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage7_3/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
