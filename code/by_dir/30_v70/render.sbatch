#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:30:00
#SBATCH -J v70render
#SBATCH -o /home/zhang.zhiqi2/jlens_work/30_v70/render/render_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
~/conda-envs/jlens/bin/python /home/zhang.zhiqi2/jlens_work/hc_pass_20261123/render_png.py /home/zhang.zhiqi2/jlens_work/30_v70/deck_v70.html /home/zhang.zhiqi2/jlens_work/30_v70/render "$1"
