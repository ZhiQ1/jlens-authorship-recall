#!/bin/bash
#SBATCH -J export_hb_n3
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/export_hb_20261112n3_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-12 round n (3): handbook PDF only (overwrite Stage1-13_methods_handbook_A4.v20261108c.pdf).
set -e
export PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
R=/scratch/zhang.zhiqi2/jlens/351_stage10/reports
~/conda-envs/jlens/bin/python $R/methods/export_pdf_20261108c.py $R/downloads/Stage1-13_methods_handbook_A4.v20261108c.pdf
