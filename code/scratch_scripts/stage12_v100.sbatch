#!/bin/bash
# Stage 12 prior units on 3 x V100-SXM2-32GB (see stage12_v100.py). MODE=smoke or work.
#SBATCH --job-name=s12v
#SBATCH --account=cs7980.202710
#SBATCH --partition=gpu-short
#SBATCH --time=02:00:00
#SBATCH --gres=gpu:v100-sxm2:3
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/371_stage12/logs/v100_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) s12 V100 $SLURM_JOB_ID on $(hostname) mode=${MODE:-work}"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
~/conda-envs/jlens/bin/python -u ~/jlens_work/12_stage12/stage12_v100.py ${MODE:-work} ${BUDGET:-105}
