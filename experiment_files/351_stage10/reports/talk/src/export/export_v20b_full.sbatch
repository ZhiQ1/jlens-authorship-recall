#!/bin/bash
#SBATCH -J deck_v20b_full
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/export_v20b_full/export_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-07 (user): deck v20b PDFs WITHOUT JPEG compression (PNG slides), each split into two files (slides 1-41, 42-82).
set -e
E=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src/export; O=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/export_v20b_full
D=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads; PY=~/conda-envs/jlens/bin/python
cd $E
NOTES_H=1620 PARTS=1-41,42-82 $PY export_deck_v20b_split.py $D /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html v20b
ls -la $D/Stage1-13_deck_v20b_*_part*.pdf
