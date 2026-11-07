#!/bin/bash
#SBATCH -J deck_v20e_full
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/export_v20e_full/export_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-07 (user): deck v20b PDFs WITHOUT JPEG compression (PNG slides), each split into two files (slides 1-41, 42-82).
# 2026-11-07 ~03:10 copy: label v20e (H1 cell on slide 65), three parts each.
set -e
E=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src/export; O=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/export_v20e_full
D=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads; PY=~/conda-envs/jlens/bin/python
cd $E
export PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
NOTES_H=1620 PARTS=1-27,28-55,56-82 $PY export_deck_v20d_split3.py $D /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html v20e
ls -la $D/Stage1-13_deck_v20e_*_part*.pdf
