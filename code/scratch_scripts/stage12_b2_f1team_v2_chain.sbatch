#!/bin/bash
#SBATCH -J b2c_f1t2_chain
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 47:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_v2_chain_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-2 resume chain (2026-11-10, see stage12_b2_f1team_v2_chain.py): one CPU driver; GPU jobs 45 min without --time-min,
# killguard --exclude, kill cap 3 per unit, controller-reset cancels not counted. Safe to resubmit (state in summary/chain22).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/12_stage12
~/conda-envs/jlens/bin/python -u stage12_b2_f1team_v2_chain.py
