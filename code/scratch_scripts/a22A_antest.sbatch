#!/bin/bash
#SBATCH -J a22A_antest
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a22A/antest_%j.out
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONUNBUFFERED=1 A22A_RAW=/scratch/zhang.zhiqi2/jlens/391_groups/raw/a22A_test_tiny A22A_SUMMARY=/scratch/zhang.zhiqi2/jlens/391_groups/raw/a22A_test_tiny/summary A22A_SHARDS=0,1
~/conda-envs/jlens/bin/python ~/jlens_work/17_ladder/a22_partA_analyze.py
