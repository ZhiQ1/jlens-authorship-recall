#!/bin/bash
#SBATCH -J a21_gpu
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 4
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a21/gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: SHARDS=0 sbatch --export=ALL inject_gpu.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python ~/jlens_work/16_inject/inject_main.py work --shards "${SHARDS:-0}" --max-minutes 38
