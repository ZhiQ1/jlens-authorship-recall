#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:40:00
#SBATCH -J v72probe
#SBATCH -o /home/zhang.zhiqi2/jlens_work/32_v72/probe_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
~/conda-envs/jlens/bin/python /home/zhang.zhiqi2/jlens_work/32_v72/relayout_probe.py /home/zhang.zhiqi2/jlens_work/32_v72/deck_v72_stage1.html /home/zhang.zhiqi2/jlens_work/32_v72/relayout.json
