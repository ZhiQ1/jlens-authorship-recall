#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:30:00
#SBATCH -J deck20261120a
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/render_20261120a_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-20a: slide-27 n-line fix: byte verify + Chromium checks
cd /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107
echo '== verify'; ~/conda-envs/jlens/bin/python verify_20261120a_deck.py
echo '== chromium'; bash render_20261120a.sh
