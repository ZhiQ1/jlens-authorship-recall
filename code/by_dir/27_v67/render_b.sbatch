#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:20:00
#SBATCH -J v67Brender
#SBATCH -o /home/zhang.zhiqi2/jlens_work/27_v67/render_b/render_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
~/conda-envs/jlens/bin/python /home/zhang.zhiqi2/jlens_work/hc_pass_20261123/render_png.py /home/zhang.zhiqi2/jlens_work/27_v67/test_part34.html /home/zhang.zhiqi2/jlens_work/27_v67/render_b "$1"
