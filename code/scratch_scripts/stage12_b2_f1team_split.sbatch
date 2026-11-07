#!/bin/bash
#SBATCH -J b2c_f1t_split
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:15:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_split_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-2: freeze the 20 + 20 author-team split (seed 1206) -> 371_stage12/config/b2_f1team_split.parquet (refuses to change an existing one)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/12_stage12
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py split
