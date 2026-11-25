#!/bin/bash
#SBATCH -J fab_ed
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 08:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/%x_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# slide 125 post-hoc: edit distance of not-in-data fabricated names to cohort authors (CPU only)
~/conda-envs/jlens/bin/python ~/jlens_work/14_groups/fabricated_editdist_20261125.py
