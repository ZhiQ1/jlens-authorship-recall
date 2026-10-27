# Stage 12 — follow-ups to Stage 11 and name-prior measurements (running)

**Question.** Which post-title token carries the paper, attention or MLP, would an author-prompt lens read it earlier, and how large is the name prior?

Overview of all stages: `~/jlens_work/STAGES.md`.

## Scripts

| File | Role |
|---|---|
| `371_stage12.py` | freeze | work | remaining | analyze. GPU units: patch_pos (P1, single positions), patch_comp (P2, attention vs MLP output), prior_mc (N1, MC options without / with title), prior_pure (N2, no-paper prompt), alens_read (F2); F1 author-prompt lens fit (resumable, any job may take it) |
| `stage12_analyze.py/.sbatch` | analysis gate → `reports/stage12_report.md` |
| `stage12_cpu.py/.sbatch` | CPU: name-prior A/B/C, probe controls X1 → `summary_cpu/`, `reports/stage12_cpu_report.md` |
| `stage12_work.sbatch` | GPU worker (FIT=1 starts with the lens fit) |
| `stage12_keeper.py/.sbatch` | fills A100 slots with 90-min workers, keeps one s12fit queued |

## Run order

1. `371_stage12.py freeze`
2. `stage12_cpu.sbatch` (CPU, done)
3. `stage12_keeper.sbatch` → `stage12_work.sbatch` (GPU)
4. `stage12_analyze.sbatch`

## Outputs

`/scratch/zhang.zhiqi2/jlens/371_stage12/`: `config/`, `raw/<unit>/`, `alens/` (lens checkpoint), `logs/` (claims, broken_*.json, fit_error_*.json), `summary/`, `summary_cpu/`, `reports/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
