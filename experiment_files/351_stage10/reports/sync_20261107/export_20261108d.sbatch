#!/bin/bash
#SBATCH -J export_0108d
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/export_20261108d_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-08 d (round d after checks): re-export report v30, handbook 20261108c, page + talk-doc PDFs 20261108c (overwrite). pptx v21 done by hand (pptx_text_fix_20261108d.py).
# Deck PDFs: talk/src/export/export_v21_full.sbatch (submitted with --dependency=afterok on this job, because it needs the slide-65 image).
set -e
export PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
PY=~/conda-envs/jlens/bin/python; D=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads; R=/scratch/zhang.zhiqi2/jlens/351_stage10/reports
$PY $R/sync_20261107/export_pdfs_20261108c.py pdf
ls -la $D | grep -E "v30|v21|20261108c|2026-11-08c"
