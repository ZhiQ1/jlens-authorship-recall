# Stage 7.4 — cross-stage consistency and J-Lens increment (CPU)

**Question.** Are the methods consistent across stages, and does J-Lens add information over Vanilla?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage7_4.py` | CPU, read-only: cross-stage correlations on the same 50 papers, same-paper J − V |
| `351_stage7_4_results.zip` | archived results |

## Run order

1. `351_stage7_4.py --source <unpacked experiment parent>`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage7_4/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
