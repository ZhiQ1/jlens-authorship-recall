#!/bin/bash
#SBATCH -J h2fict_gen3
#SBATCH -p gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:h200:1
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v3/logs/h2fict_gen3_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# H2 fictitious titles v3 generation (Stage 11 subset 1,186; user decision 2026-11-19). ROUND=0|1|2 via --export=ALL,ROUND=n
# Rounds 1-2 only regenerate papers without a passing candidate; exits before loading the model if none.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/15_h2fict
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python h2fict_gen_v3.py --round ${ROUND:?} --out ${OUTDIR:-/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v3}
