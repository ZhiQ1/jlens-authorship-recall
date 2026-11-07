#!/bin/bash
#SBATCH -J s13_b1x7f_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1_x7f_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 item 2: whole pipeline on a random 64-layer tiny Qwen3 (CPU): Stage 11 E1/E2 + X6 + X7 false_0..4 -> analysis
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_b1_x7f.py tiny --root /scratch/zhang.zhiqi2/jlens/381_stage13/b1_x7f_tiny
