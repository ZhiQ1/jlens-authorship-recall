#!/bin/bash
#SBATCH -J c13_c5_rep
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:20:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c13_c5_report_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONDONTWRITEBYTECODE=1
[ -s /scratch/zhang.zhiqi2/jlens/381_stage13/reports/c13_C5.md ] && { echo exists; exit 0; }
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_c13_c5_report.py
