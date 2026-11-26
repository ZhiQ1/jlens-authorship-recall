#!/bin/bash
#SBATCH -J a25unlock
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a25_unlock_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONUNBUFFERED=1
~/conda-envs/jlens/bin/python ~/jlens_work/21_tablegpu/a25_unlock.py ${TINY:+--tiny}
