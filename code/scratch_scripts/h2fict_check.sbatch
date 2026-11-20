#!/bin/bash
#SBATCH -J h2fict_check
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/logs/h2fict_check_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# CPU checks for H2 fictitious titles. Usage: sbatch [--export=ALL,OUTDIR=...,EXTRA=--no-ext] h2fict_check.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
cd ~/jlens_work/15_h2fict
~/conda-envs/jlens/bin/python h2fict_check.py ${OUTDIR:-/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious} ${EXTRA:-}
