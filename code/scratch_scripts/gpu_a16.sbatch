#!/bin/bash
#SBATCH -J a16_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a16_gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 16 B/D GPU worker. Usage: sbatch $(killguard exclude) gpu_a16.sbatch ITEM SHARDS   (e.g. B 0 ; D 0 ; B 1,2,3)
# Shards skip if done (meta file = marker); stops ~1.3 shard-times before 40 min. Self-checks are WARN only.
# No automatic resubmission (the remaining shards are submitted only after the cost check / user decision).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
nvidia-smi --query-gpu=name,memory.total --format=csv
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python prereg16_a16.py work --item ${1:?item} --shards ${2:?shards} --max-minutes 40
