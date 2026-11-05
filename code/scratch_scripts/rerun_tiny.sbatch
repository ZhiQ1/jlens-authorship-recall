#!/bin/bash
#SBATCH -J g391_rerun_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/rerun_tiny_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups
ROOT=/scratch/zhang.zhiqi2/jlens/391_groups/test_rerun_tiny2
~/conda-envs/jlens/bin/python rerun_gpu.py tiny --root $ROOT || exit 1
if [ -f rerun_analyze.py ]; then RERUN_OUT=$ROOT RERUN_TINY=1 ~/conda-envs/jlens/bin/python rerun_analyze.py; fi
