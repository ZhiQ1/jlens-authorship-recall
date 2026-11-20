#!/bin/bash
#SBATCH -J a20_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a20/tiny_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 20: full-pipeline tiny test (random 64-layer Qwen3-shaped model on CPU, 3 papers, all units + parity + skip check),
# then the analysis on synthetic inputs (TEST root).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python
cd ~/jlens_work/15_h2fict
ROOT=/scratch/zhang.zhiqi2/jlens/391_groups/raw/a20_test_tiny_$SLURM_JOB_ID
$PY -u h2_main_gpu.py tiny --root $ROOT; echo "TINY GPU-PIPELINE EXIT $?"
if [ -f h2_main_analyze.py ]; then $PY -u h2_main_analyze.py --synthetic --out /scratch/zhang.zhiqi2/jlens/391_groups/raw/a20_test_synth_$SLURM_JOB_ID; echo "SYNTH ANALYSIS EXIT $?"; fi
