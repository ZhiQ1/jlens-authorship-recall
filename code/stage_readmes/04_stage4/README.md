# Stage 4 — exploratory multi-author gold readout (Benchmark20)

**Question.** Is the mean first-token readout pulled up by a few papers?

Overview of all stages: `~/jlens_work/STAGES.md`.

**Do not edit the scripts here.** They are byte-identical to the archived originals (sha256 list `notes/reorg_sha256.txt`) and later stages check their hashes, so the stage is named in this README and in the file names (`351_stageN…`), not by editing the script headers.

## Scripts

| File | Role |
|---|---|
| `351_stage4_readout.py` | GPU: Qwen3-32B bf16 + public Neuronpedia J-Lens + Vanilla + final logits; first-listed author first token at ":" for 20 papers; per-paper JSONL, resumable |
| `351_stage4_audit.py` | CPU: audit of the saved Stage 4 results (no model), per-paper contributions |

## Run order

1. `351_stage4_readout.py` (GPU)
2. `351_stage4_audit.py` (CPU)

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_all/351_stage4_artifacts/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
