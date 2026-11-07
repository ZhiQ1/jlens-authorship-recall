#!/bin/bash
#SBATCH -J b2cd_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b2_cd_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 B analysis (CPU): hard check again (exit 3 on FAIL), then groups / contrasts / report
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups
PY=~/conda-envs/jlens/bin/python
$PY b2_cd.py check || exit 3
$PY b2_cd.py analyze
