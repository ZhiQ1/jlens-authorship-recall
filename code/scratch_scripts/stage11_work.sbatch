#!/bin/bash
# Stage 11 GPU worker: claims E1/E2/E3 units (see 361_stage11.py work). The first worker also runs the smoke gate.
#SBATCH --job-name=s11w
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/361_stage11/logs/work_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) s11 worker $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION budget=${BUDGET}min"
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python -u ~/jlens_work/11_stage11/361_stage11.py work --max-minutes $BUDGET
