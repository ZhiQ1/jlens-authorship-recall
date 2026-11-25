#!/bin/bash
#SBATCH -J a33_gpm
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 4
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a33/gpu_%A_%a.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
nvidia-smi --query-gpu=name,memory.total --format=csv
S=$(echo $MISSING | tr "," "\n" | awk -v t=$SLURM_ARRAY_TASK_ID -v n=$NT "(NR-1)%n==t" | paste -sd,); A="--shards $S"
~/conda-envs/jlens/bin/python ~/jlens_work/26_x4confirm/a33_x4confirm.py work $A --max-minutes 38
