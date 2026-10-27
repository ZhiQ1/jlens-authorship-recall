# Stage 7.1 — first token vs continuation (CPU re-analysis of Stage 6); 7.1B terminal readout

**Question.** Does the advantage arise before the name starts, or after a prefix is given?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage7.py` | CPU: decomposes Stage 6 full-name JMRR into first token vs continuation |
| `351_stage7_1B_terminal.py` | freeze | run | check: terminal (final-layer) readout for Stage 7.1B |
| `351_stage7_1_results.zip` | archived results |

## Run order

1. `351_stage7.py`
2. `351_stage7_1B_terminal.py freeze` → `run` → `check`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage7_1/`, `351_stage7_1B_terminal/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
