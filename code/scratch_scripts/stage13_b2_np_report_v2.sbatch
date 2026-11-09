#!/bin/bash
#SBATCH -J b2np_rep2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_report_v2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 A report v2 = deviation D11-1 (per-donor exclusion primary; V0 and V5x0 beside) -> reports/b2_np_report_v2.md.
# Exit 3 = a hard check (1: GPU L63, 2: lens vs Stage 10) missing or failed; any other non-zero = crash / D11-1 record changed.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b2_np_report_v2.py
