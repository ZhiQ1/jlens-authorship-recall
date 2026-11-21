#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:20:00
#SBATCH -J shots1121
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/narr_20261121/shots_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
cd /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107
~/conda-envs/jlens/bin/python shots_20261121.py "$DECK" "$OUTD" "$NS"
