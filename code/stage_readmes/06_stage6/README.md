# Stage 6 — full-name conditional readout trajectories (Pilot50)

**Question.** How does every name token of every author read out layer by layer, by group?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage6.py` | GPU + CPU: every name token of 227 paper-author instances, teacher forcing, JMRR by paper / layer / bin; reuses Stage 5 pilot50_v1 and (after consistency checks) Stage 4 readouts; `audit-reuse` re-check |
| `351_stage6.tar.gz` | archived results |

## Run order

1. `351_stage6.py` (see `--help`)
2. `351_stage6.py audit-reuse` (read-only re-check)

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage6/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
