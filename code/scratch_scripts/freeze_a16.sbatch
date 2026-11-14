#!/bin/bash
#SBATCH -J a16_freeze
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a16_freeze_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 16 B/D sample freeze (CPU). DRY=1: writes into 391_groups/test_a16_freeze_dry (A16_CFG) and runs the precheck there.
# Real run (DRY unset): writes config/prereg16_sample_{B,D}.parquet + .sha256 + prereg16_freeze.json (refuses to overwrite), then precheck.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups
PY=~/conda-envs/jlens/bin/python
[ "$DRY" = 1 ] && export A16_CFG=/scratch/zhang.zhiqi2/jlens/391_groups/test_a16_freeze_dry
$PY prereg16_a16.py freeze && $PY prereg16_a16.py precheck
