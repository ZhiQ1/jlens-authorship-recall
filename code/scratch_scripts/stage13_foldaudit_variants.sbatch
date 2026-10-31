#!/bin/bash
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_fvar
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/foldaudit_2026-10-30/logs/fvar_%N_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
lscpu | grep -E "Model name|avx512f" | cut -c1-120 | head -2; grep -o -m1 avx512f /proc/cpuinfo
cd /tmp && ~/conda-envs/jlens/bin/python -u ~/jlens_work/13_stage13/stage13_foldaudit_variants.py
