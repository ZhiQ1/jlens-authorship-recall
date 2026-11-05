#!/bin/bash
#SBATCH -J s13_alltok
#SBATCH -p gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/alltok_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 9 GPU data step: L63 residual at every name-token-predicting position (true title, Stage 10 contexts).
# SHARDS="0" (first real shard) or e.g. "1-35"; skips existing shards; stops before 40 min.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python -u stage13_alltok_gpu.py --shards "${SHARDS:-0}" --max-minutes 40
