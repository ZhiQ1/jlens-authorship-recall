#!/bin/bash
#SBATCH -J g391_rerun_tinyana
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/rerun_tinyana_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups
RERUN_OUT=${ROOT:-/scratch/zhang.zhiqi2/jlens/391_groups/test_rerun_tiny2} RERUN_TINY=${TINY:-1} ~/conda-envs/jlens/bin/python rerun_analyze.py
