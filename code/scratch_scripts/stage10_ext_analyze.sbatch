#!/bin/bash
# Stage 10 analysis after the extension: keep a copy of the main-round outputs, then rerun analyze + analyze-title
# (they pick up every complete readout/layer, so the new layers are added next to the main ones).
#SBATCH --job-name=s10x_analyze
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=04:00:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/analyze_%x_%j.log
set -e
export PYTHONDONTWRITEBYTECODE=1
ROOT=/scratch/$USER/jlens/351_stage10; PY=~/conda-envs/jlens/bin/python; S=~/jlens_work/10_stage10/351_stage10.py
SNAP=$ROOT/snapshot_main_round
if [ ! -d $SNAP ]; then mkdir $SNAP; for d in summary reports figures; do [ -d $ROOT/$d ] && cp -a $ROOT/$d $SNAP/; done; fi
$PY $S audit --quick
$PY $S analyze
$PY $S analyze-title
