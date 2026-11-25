#!/bin/bash
#SBATCH -J a33_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a33/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch a33_cpu.sbatch freeze text tiny   |  sbatch a33_cpu.sbatch analyze
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
set -e
for step in "$@"; do echo "== $step $(date)"; ~/conda-envs/jlens/bin/python ~/jlens_work/26_x4confirm/a33_x4confirm.py $step; done
echo "== done $(date)"
