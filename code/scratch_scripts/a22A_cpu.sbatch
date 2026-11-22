#!/bin/bash
#SBATCH -J a22A_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a22A/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch a22A_cpu.sbatch "freeze" "precheck" "tiny --root DIR"
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
set -e
for step in "$@"; do echo "== $step"; ~/conda-envs/jlens/bin/python ~/jlens_work/17_ladder/a22_partA.py $step; done
