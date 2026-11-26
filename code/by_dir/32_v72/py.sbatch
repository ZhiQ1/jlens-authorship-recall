#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:40:00
#SBATCH -J v22w
#SBATCH -o /home/zhang.zhiqi2/jlens_work/32_v72/py_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONPATH=/scratch/zhang.zhiqi2/pylib2
cd /home/zhang.zhiqi2/jlens_work/32_v72
~/conda-envs/jlens/bin/python "$@"
