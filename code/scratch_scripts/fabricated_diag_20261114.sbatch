#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 03:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/%x_%j.out
# exploratory (探索性), post hoc. usage: sbatch [--export=ALL,FAB_TINY=1,FAB_NB=200,FAB_R=2,FAB_OUT=...] fabricated_names_20261114.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python fabricated_diag_20261114.py
