#!/bin/bash
#SBATCH -J b2c_gn_probe
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_probe_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-11 probe (CPU): logistic probes per layer x position, controls, report -> 381_stage13/reports/b2_gennames_report.md
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b2_gennames.py probe
