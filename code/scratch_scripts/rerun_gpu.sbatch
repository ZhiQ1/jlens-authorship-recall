#!/bin/bash
#SBATCH -J g391_rerun
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/rerun_gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 8 GPU re-runs. Env: CHECK=<stage11 shard> (optional: re-run one original Stage 11 shard, E1+E2, WARN only);
# UNITS=<exp:group:shards,...> (skip-if-exists; the job stops before its time limit).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python
nvidia-smi --query-gpu=name,memory.total --format=csv
cd ~/jlens_work/14_groups
ARGS=""; if [ -n "$CHECK" ]; then ARGS="--check $CHECK"; fi
if [ -n "$UNITS" ]; then ARGS="$ARGS --units $UNITS"; fi
$PY rerun_gpu.py work $ARGS --max-minutes 40
$PY rerun_gpu.py remaining
