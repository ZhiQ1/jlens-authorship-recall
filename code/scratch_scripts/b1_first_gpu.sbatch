#!/bin/bash
#SBATCH -J b1_x7p12_first
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b1_first_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 items 2 + 3, first real GPU job (no chaining): hard check (a) re-runs of false_0 shard 0 + ONE real shard each
#   X7: false_0_check:0 + false_1:0 ; P1/P2: patch_comp + patch_pos false_0_check:0 + false_1:0
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python
nvidia-smi --query-gpu=name,memory.total --format=csv
cd ~/jlens_work/13_stage13 && $PY stage13_b1_x7f.py work --check --units false_1:0 --max-minutes 12
cd ~/jlens_work/14_groups && $PY b1_p12f.py work --check --units patch_comp:false_1:0,patch_pos:false_1:0 --max-minutes 25
