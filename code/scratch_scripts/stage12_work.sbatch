#!/bin/bash
# Stage 12 GPU worker (see 371_stage12.py work). FIT=1: first continue the author-lens fit, then ordinary units.
#SBATCH --job-name=s12w
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/371_stage12/logs/work_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) s12 worker $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION fit=${FIT:-0}"
F=""; [ "${FIT:-0}" = "1" ] && F="--fit"
~/conda-envs/jlens/bin/python -u ~/jlens_work/12_stage12/371_stage12.py work --max-minutes ${BUDGET:-80} $F
