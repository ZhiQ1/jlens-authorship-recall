#!/bin/bash
#SBATCH -J h2fict_gen
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/logs/h2fict_gen_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# H2 fictitious titles, quality sample (exploratory, not preregistered). 60 papers x K=4 candidates.
# Resumable: skips papers already in candidates.jsonl. Usage: sbatch [--export=ALL,LIMIT=2] h2fict_gen.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/15_h2fict
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python h2fict_gen.py --mode gen --limit ${LIMIT:-0} --bs ${BS:-20}
