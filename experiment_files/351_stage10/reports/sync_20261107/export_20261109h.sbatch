#!/bin/bash
#SBATCH -J export_0109h
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/export_20261109h_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-09 h: hypotheses PNGs v30 (H3 partly supported) + deck slide-65 image, pptx v21 (pptx_text_fix_20261109h.py), report v30 / handbook 20261108c / page + talk-doc PDFs (overwrite).
set -e
export PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
PY=~/conda-envs/jlens/bin/python; D=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads; R=/scratch/zhang.zhiqi2/jlens/351_stage10/reports
$PY $R/sync_20261107/export_pdfs_20261108c.py png
$PY $R/talk/src/export/pptx_text_fix_20261109h.py $D/Stage1-13_deck_v21_editable.pptx.before_20261109h2 $D/Stage1-13_deck_v21_editable.pptx
base64 -w0 $D/Stage1-13_deck_v21_editable.pptx > $D/Stage1-13_deck_v21_editable.pptx.b64.txt
$PY $R/sync_20261107/export_pdfs_20261108c.py pdf
