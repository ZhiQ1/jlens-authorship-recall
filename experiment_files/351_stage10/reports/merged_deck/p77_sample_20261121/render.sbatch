#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:15:00
#SBATCH -J p77render
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/p77_sample_20261121/render_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw
~/conda-envs/jlens/bin/python /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/p77_sample_20261121/render.py /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/p77_sample_20261121/p77_sample.html /scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/p77_sample_20261121
