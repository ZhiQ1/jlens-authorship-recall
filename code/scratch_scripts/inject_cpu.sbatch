#!/bin/bash
#SBATCH -J a21_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a21/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch inject_cpu.sbatch "freeze" | "precheck" | "tiny --root DIR"
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
set -e
for step in "$@"; do
  echo "== $step"; ~/conda-envs/jlens/bin/python ~/jlens_work/16_inject/inject_main.py $step
done
