#!/bin/bash
#SBATCH -J b2c_orig66
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_orig66_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-1: Fit B prompt 66 re-run with the ORIGINAL frozen fullfit code path (stage9_b2_fitb_orig66.py). Full 45 min, no --time-min.
# Submitted / resubmitted (sacct 0:9 epilog kill, max 3) by stage9_b2_fitb_d124_decide.py.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2c_orig66 $SLURM_JOB_ID on $(hostname) limit=$(squeue -h -j $SLURM_JOB_ID -o %l)"
nvidia-smi --query-gpu=name,driver_version,memory.used,memory.total --format=csv || true
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_orig66.py
