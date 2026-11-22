#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:30:00
#SBATCH -J deck20261122b
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/v53_20261122/verify_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
cd /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107
echo '== chromium'; ~/conda-envs/jlens/bin/python check_20261122b.py
echo '== shots'; FORCE=1 ~/conda-envs/jlens/bin/python shots_20261121.py /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/v53_20261122/shots 68:82:84:93
