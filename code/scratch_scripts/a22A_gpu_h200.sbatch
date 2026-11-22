#!/bin/bash
#SBATCH -J a22A_h200
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:h200:1
#SBATCH --exclude=d1028
#SBATCH -c 4
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a22A/gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: SHARDS=0,1,2 sbatch --export=ALL a22A_gpu.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python ~/jlens_work/17_ladder/a22_partA.py work --shards "${SHARDS:-0}" --max-minutes 38
