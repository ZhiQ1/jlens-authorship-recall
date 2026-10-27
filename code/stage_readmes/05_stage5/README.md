# Stage 5 — title-specific first-token controlled pilot (Pilot50)

**Question.** Does the score depend on the title–author correspondence?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage5.py` | prepare | run | analyze: 2 titles × 2 authors crossed on Pilot50 (A20/B20/C7/D3, 20 A/B pairs); gold vs false first token from the same logits. **Shared readout helper**: Stage 6, 7.1B, 7.2 and 7.3 import it (symlinks `~/351_stage5.py`, `07_2_*/351_stage5.py`, `07_3_*/351_stage5.py` — do not delete) |
| `351_stage5_crossed_v2.zip` | archived results |

## Run order

1. `351_stage5.py prepare`
2. `351_stage5.py run` (GPU)
3. `351_stage5.py analyze`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage5_crossed_v2/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
