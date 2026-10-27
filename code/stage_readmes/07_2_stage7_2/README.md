# Stage 7.2 — gold vs 100 false names (Pilot50)

**Question.** Does the gold first token beat many real false names?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage7_2.py` | CPU: frozen candidate set, gold + 100 false authors (50 matched + 50 random) per paper; tokenizer only |
| `351_stage7_2_score.py` | audit | run (GPU) | analyze: first-token Gold Win Rate |
| `351_stage5.py` | symlink to `../05_stage5/351_stage5.py` (shared readout) — do not delete |
| `*.tar.gz` | archived candidates and results |

## Run order

1. `351_stage7_2.py`
2. `351_stage7_2_score.py audit` → `run` → `analyze`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage7_2/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
