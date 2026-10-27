#!/bin/bash
# Stage 10 CPU analysis.  MODE=main -> crosscheck + analyze (true title);  MODE=title -> analyze-title (all 7 conditions)
#SBATCH --job-name=s10_analyze
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/analyze_%x_%j.log
export PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; S=~/jlens_work/10_stage10/351_stage10.py
$PY $S audit --quick
if [ "${MODE:-main}" = title ]; then $PY $S analyze-title; else $PY $S crosscheck; $PY $S analyze; fi
