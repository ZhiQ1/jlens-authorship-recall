#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/%x_%j.out
# usage: sbatch --export=ALL,STEP=groups_analysis.py[,GROUPS_NB=..,GROUPS_OUT=..,GROUPS_DATA=..] groups_step.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python $STEP
