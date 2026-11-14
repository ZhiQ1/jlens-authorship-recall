#!/bin/bash
#SBATCH -J a16_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a16_tiny_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 16 B/D whole pipeline on a random 64-layer tiny Qwen3 (CPU, real tokenizer, real frozen samples: 2 papers per group,
# 2 shards per item): units -> teacher forcing -> generation -> matching -> parity code -> save -> skip-if-exists; parity row
# alignment tested on stored Stage 10 values (exact) and a perturbed copy (WARN).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python prereg16_a16.py tiny --root /scratch/zhang.zhiqi2/jlens/391_groups/test_a16_tiny_$SLURM_JOB_ID
