#!/bin/bash
#SBATCH -p short --account=cs7980.202710 -c 2 --mem=16G -t 00:40:00
#SBATCH -J dgap1114 -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/decode_gap_20261114_%j.out
#SBATCH --mail-type=END,FAIL --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python decode_gap_20261114.py
