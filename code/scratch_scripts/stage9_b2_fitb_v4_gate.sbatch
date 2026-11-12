#!/bin/bash
#SBATCH -J b2c_fitb4gate
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v4_gate_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D12-1 gate v4 (D12-5, 2026-11-12): part (b) compared in fp32 as jlens.fit logged it; everything else as v3. Full 45 min, no
# --time-min; submitted / resubmitted after 0:9 epilog kills (max 3) by stage9_b2_fitb_v4_watch.py (killguard --exclude).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2c_fitb4gate $SLURM_JOB_ID on $(hostname) limit=$(squeue -h -j $SLURM_JOB_ID -o %l)"
free -g | head -2
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_v4.py gate
