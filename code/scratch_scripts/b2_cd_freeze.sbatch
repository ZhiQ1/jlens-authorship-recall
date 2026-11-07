#!/bin/bash
#SBATCH -J b2cd_freeze
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b2_cd_freeze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 B: freeze the C / D paper lists (CPU; refuses to overwrite existing lists)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python b2_cd.py freeze
