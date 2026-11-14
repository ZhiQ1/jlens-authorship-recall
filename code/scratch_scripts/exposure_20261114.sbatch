#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 02:00:00
#SBATCH -J expo1114
#SBATCH -o /home/zhang.zhiqi2/jlens_work/14_groups/logs/%x_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# exploratory (探索性), post hoc. Usage: sbatch [--export=ALL,GROUPS_NB=50,EXPO_OUT=...] exposure_20261114.sbatch
export HF_HUB_OFFLINE=1 HF_HOME=/scratch/zhang.zhiqi2/hf
cd /home/zhang.zhiqi2/jlens_work/14_groups
~/conda-envs/jlens/bin/python exposure_20261114.py
