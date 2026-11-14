#!/bin/bash
#SBATCH -J h3ss_anal
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/summary_h3_samescale_20261114/logs/analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Plan 2026-11-14b item 2, H3 same-scale analysis (post hoc, strengthening 2, descriptive). CPU only. TINY=1 -> --tiny.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
EXTRA=""; [ "${TINY:-0}" = 1 ] && EXTRA="--tiny"
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_h3_samescale_analyze_20261114.py $EXTRA
