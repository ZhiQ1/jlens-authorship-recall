#!/bin/bash
#SBATCH -J new12
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/summary_tables_20261122/new12_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
~/conda-envs/jlens/bin/python ~/jlens_work/20_tables/new12_analysis.py
