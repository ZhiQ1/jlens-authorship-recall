#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=96G
#SBATCH -t 03:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/%x_%j.out
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python groups_build.py
