#!/bin/bash
#SBATCH -J a22B
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a22/partB_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch a22_partB.sbatch "<args for a22_partB.py>" ["<args>" ...]
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
set -e
for s in "$@"; do echo "== $s"; ~/conda-envs/jlens/bin/python ~/jlens_work/17_ladder/a22_partB.py $s; done
