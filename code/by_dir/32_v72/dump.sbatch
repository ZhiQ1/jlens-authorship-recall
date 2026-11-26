#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:20:00
#SBATCH -J v22wdump
#SBATCH -o /home/zhang.zhiqi2/jlens_work/32_v72/dump_%j.log
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
~/conda-envs/jlens/bin/python /home/zhang.zhiqi2/jlens_work/32_v72/pptx_dump.py /scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/jlens_1113_pre_v22v.pptx 21,56
