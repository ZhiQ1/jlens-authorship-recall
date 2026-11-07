#!/bin/bash
#SBATCH -J b2np_rep
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_report_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 A report (reports/b2_np_report.md). Exit 3 = a hard check (1: GPU L63, 2: lens vs Stage 10) missing or failed.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b2_np_report.py
