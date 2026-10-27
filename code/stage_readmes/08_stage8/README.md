# Stage 8 — independent validation on 200 new papers (8A–8D)

**Question.** Does the title signal hold on new papers, with L56 pre-specified?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage8.py` | freeze | audit | budget (CPU): 200 new papers / 100 A/B pairs (Low/Mid/High 25/50/25), analysis plan frozen (8A) |
| `351_stage8B.py` | freeze | audit (CPU): wrong-author and wrong-title controls (8B) |
| `351_stage8C.py` | audit | run (GPU): true / wrong title first-token readout (8C) |
| `351_stage8D.py` | audit | analyze (CPU): frozen analysis (8D) |
| `351_stage8D_supplement.py` | CPU: endpoints of the frozen plan that 8D did not compute |
| `351_stage8_PROTOCOL.md, 351_stage8_README.md` | protocol and original notes |
| `0001-Review-fixes-…patch` | review patch for the 8D supplement |

## Run order

1. `351_stage8.py freeze` → `audit`
2. `351_stage8B.py freeze` → `audit`
3. `351_stage8C.py audit` → `run` (GPU)
4. `351_stage8D.py audit` → `analyze`
5. `351_stage8D_supplement.py`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage8/` (8D under `stage8D/`)

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
