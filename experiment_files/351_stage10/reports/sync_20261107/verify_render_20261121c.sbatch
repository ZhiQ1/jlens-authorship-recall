#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:30:00
#SBATCH -J deck20261121c
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/expl_20261121/verify_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
cd /scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107
echo '== verify c'; ~/conda-envs/jlens/bin/python verify_20261121c_fx.py
echo '== chromium'; ~/conda-envs/jlens/bin/python check_20261121b.py
echo '== shots'; FORCE=1 ~/conda-envs/jlens/bin/python shots_20261121.py /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/expl_20261121/shots 59:81:86:95
