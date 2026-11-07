#!/bin/bash
#SBATCH -J b1e4b5_gpu
#SBATCH -p gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1_e4b5_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 item 4 GPU data step: title-last / ':' residuals for false_1..4 (CONDS, SHARDS env); skip-if-exists; stops before 40 min.
# First real job: CONDS=false_0,false_1,false_2,false_3,false_4 SHARDS=0 (false_0 = hard check vs stored Stage 11 residuals)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python -u stage13_b1_e4b5_gpu.py --conds "${CONDS:-false_1,false_2,false_3,false_4}" --shards "${SHARDS:-0}" --max-minutes 40
