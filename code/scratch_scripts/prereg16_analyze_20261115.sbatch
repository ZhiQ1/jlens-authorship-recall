#!/bin/bash
#SBATCH -p short --account=cs7980.202710 -c 2 --mem=32G -t 00:50:00
#SBATCH -J a16anal -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/prereg16_analyze_20261115_%j.out
#SBATCH --mail-type=END,FAIL --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 16 B/D pre-registered analysis (CPU). Extra args passed through, e.g. --shards-B 0,1 --shards-D 0,1 --out DIR
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
~/conda-envs/jlens/bin/python prereg16_analyze_20261115.py "$@"
