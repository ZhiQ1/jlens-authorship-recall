#!/bin/bash
#SBATCH -J b2c_f1t_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-2: hard-check selftest + tiny whole-pipeline CPU test (tiny random Qwen3 config, real fit prompts / sample rows).
# Uses a FRESH root each time (the tiny root is never reused: ROOT must not exist).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
ROOT=/scratch/zhang.zhiqi2/jlens/371_stage12/test_b2_f1team_$SLURM_JOB_ID
cd ~/jlens_work/12_stage12
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py selftest || exit 1
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py tiny --root $ROOT
