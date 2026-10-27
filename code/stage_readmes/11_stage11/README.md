# Stage 11 — causal and context follow-ups (patching, knockout, title position, author chain)

**Question.** Is the author information formed late, or read from the title earlier and only made readable late?

Overview of all stages: `~/jlens_work/STAGES.md`.

## Scripts

| File | Role |
|---|---|
| `361_stage11.py` | freeze | preflight | smoke | work | remaining | analyze. Units: patch (E1), knockout (E2), patch_title (E1t), knockout_name (E2n), titlepos + probe_vocab (E4), chain (E3) |
| `stage11_analyze.py` | CPU analysis → `summary/E*.csv`, `reports/stage11_report.md` |
| `stage11_cpu_realcheck.py/.sbatch` | pre-GPU check with the real weights on CPU |
| `stage11_work.sbatch` | GPU worker (claims units; first one runs the smoke gate) |
| `stage11_keeper.py/.sbatch` | keeps A100 slots filled while units remain |
| `stage11_analyze.sbatch` | analysis gate: waits for all units, then analyses |

## Run order

1. `361_stage11.py freeze` → `preflight`
2. `stage11_cpu_realcheck.sbatch`
3. `stage11_keeper.sbatch` → `stage11_work.sbatch` (GPU; smoke, then work)
4. `stage11_analyze.sbatch`

## Outputs

`/scratch/zhang.zhiqi2/jlens/361_stage11/`: `config/` (protocol, sample, amendment 1), `raw/`, `smoke/`, `summary/`, `summary_r0/`, `reports/stage11_report.md`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
