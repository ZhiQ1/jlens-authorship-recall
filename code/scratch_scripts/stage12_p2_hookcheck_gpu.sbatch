#!/bin/bash
# Stage 12 P2 hook check (U40): ONE real shard (SHARD, default 0) of P2 with positive / negative controls, Qwen3-32B bf16.
#SBATCH --job-name=s12hk
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 02:00:00
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/371_stage12/logs/hookcheck_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) s12 hookcheck $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION shard=${SHARD:-0}"
cd ~/jlens_work/12_stage12 && ~/conda-envs/jlens/bin/python -u stage12_p2_hookcheck.py --real
