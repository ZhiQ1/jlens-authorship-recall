#!/bin/bash
#SBATCH -J export_0108b
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/export_20261108b_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2026-11-08 b: pptx v20h, report/handbook/page PDFs (20261108b, v29h). Deck PDFs: separate job export_v20h_full.sbatch.
export PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
PY=~/conda-envs/jlens/bin/python; D=/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads
$PY /scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src/export/pptx_text_fix_20261108b.py $D/Stage1-13_deck_v20g_editable.pptx $D/Stage1-13_deck_v20h_editable.pptx || echo "WARN pptx fix failed"
$PY /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/export_pdfs_20261108b.py
ls -la $D | grep -E "v29h|v20h|20261108b|2026-11-08b"
