#!/bin/bash
#SBATCH -J g391_b1p12f_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b1_p12f_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 item 3: whole pipeline on a random 64-layer tiny Qwen3 (CPU): P1/P2 false_0..4 -> analysis
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python b1_p12f.py tiny --root /scratch/zhang.zhiqi2/jlens/391_groups/test_b1_p12f_tiny
