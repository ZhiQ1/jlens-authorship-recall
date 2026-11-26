#!/bin/bash
#SBATCH -J a28_gpu
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 4
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a28/gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: SHARDS=0 sbatch --export=ALL a28_gpu.sbatch   |  ALL=1 sbatch --export=ALL a28_gpu.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
nvidia-smi --query-gpu=name,memory.total --format=csv
if [ "${ALL:-0}" = 1 ]; then A="--all"; else A="--shards ${SHARDS:-0}"; fi
~/conda-envs/jlens/bin/python ~/jlens_work/19_todo/a28_x4topic.py work $A --max-minutes 38
