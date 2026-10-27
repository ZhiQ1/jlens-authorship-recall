# Stage 10 — full-cohort layer-wise readout of every author name

**Question.** At which layer does Qwen3-32B hold a paper's authors (9,108 papers, 149,999 name tokens, 7 title conditions)?

Overview of all stages: `~/jlens_work/STAGES.md`.

## Scripts

| File | Role |
|---|---|
| `351_stage10.py` | FROZEN, sha256-checked — never edit. freeze | freeze-conditions | audit | register-lens | parity | run | remaining | crosscheck | analyze | analyze-title |
| `351_stage10_fix1.py` | GPU entry point (same CLI): hf_device_map fix for transformers 5.x + weight prefetch |
| `stage10_parity.sbatch, stage10_decision.sbatch` | parity gate (GPU) and release gate (CPU) |
| `stage10_worker.sbatch, stage10_main_gate.sbatch` | self-requeueing GPU workers and their submit gate |
| `stage10_pool.py/.sbatch, stage10_pool_job.sbatch, stage10_steal.py` | queue pool: dispatcher, one chunk per job, work stealing; hands over to Stage 11 / Stage 12 when nothing is left |
| `stage10_preflight.py/.sbatch` | CPU preflight of everything a pool job checks before the GPU |
| `stage10_guard.py/.sbatch` | alarm + hold when a GPU job ends within 2 min |
| `stage10_ext_wait / ext_parity / ext_worker / ext_analyze .sbatch` | extension: public lens + logit lens at L50–55, 57–61 |
| `stage10_analyze.sbatch` | CPU analysis (MODE=main / title) |
| `stage10_extra.py/.sbatch` | CPU extras X1–X3 (report §6.7–6.9) |
| `stage10_extra_format.py, stage10_extra_cond_role.py (+ .sbatch)` | name-format follow-ups (§6.7) |
| `stage10_extra_r0.py` | Stage 10 + 11 R0-only sensitivity (report §6.13) |

## Run order

1. `351_stage10.py freeze` → `audit` → `freeze-conditions`
2. `stage10_parity.sbatch` (GPU) → `stage10_decision.sbatch`
3. workers / pool: `351_stage10_fix1.py run` per condition × shard (GPU)
4. `stage10_analyze.sbatch` MODE=main, then MODE=title
5. extension: `stage10_ext_wait` → `ext_parity` → `ext_worker` → `ext_analyze`
6. `stage10_extra.sbatch`, `stage10_extra_format.sbatch`, `stage10_extra_r0.py`

## Outputs

`/scratch/zhang.zhiqi2/jlens/351_stage10/`: `config/`, `cohort/`, `raw/` (1.2 GB), `summary/`, `summary_title/`, `summary_extra/`, `summary_r0/`, `reports/` (`stage10_report.md`, `stage10_title_summary.md`, `parity.json`, `stage10_report_bilingual.html`, `talk/`), `snapshot_main_round/`

Python: `~/conda-envs/jlens/bin/python`; set `HF_HOME=/scratch/zhang.zhiqi2/hf` and `HF_HUB_OFFLINE=1`. GPU steps run through sbatch on A100-80GB.
