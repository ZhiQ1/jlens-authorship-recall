#!/bin/bash
#SBATCH -J a20_ana
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 04:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a20/analyze_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 20 analysis (CPU). Env: ARGS (e.g. "--synthetic --out DIR" for the test; empty = the real analysis -> summary_a20/).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/15_h2fict
~/conda-envs/jlens/bin/python -u h2_main_analyze.py $ARGS
echo "ANALYSIS EXIT $?"
