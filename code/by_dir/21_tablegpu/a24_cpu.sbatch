#!/bin/bash
#SBATCH -J a24_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a24/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch a24_cpu.sbatch "freeze" "tiny --root DIR" | "analyze"
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
set -e
for step in "$@"; do echo "== $step"; ~/conda-envs/jlens/bin/python ~/jlens_work/21_tablegpu/a24_rareword.py $step; done
