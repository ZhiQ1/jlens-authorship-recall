#!/bin/bash
#SBATCH -J b2c_fitb_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-1: hard-check selftest + tiny whole-pipeline CPU test (fresh root per job; read-only frozen `check` on the real Fit B run).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb.py selftest || exit 1
~/conda-envs/jlens/bin/python -u stage9_b2_fitb.py tiny --root /scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb_tiny_$SLURM_JOB_ID
