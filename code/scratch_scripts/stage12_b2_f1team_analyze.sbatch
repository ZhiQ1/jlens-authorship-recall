#!/bin/bash
#SBATCH -J b2c_f1t_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-2 analysis (CPU): hard check (again; exit 2 on FAIL), then matrices / top-10 / F2 per lens -> 381_stage13/reports/b2_f1team_report.md
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/12_stage12
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py hardcheck || exit 2
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py analyze
