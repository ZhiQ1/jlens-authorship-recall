#!/bin/bash
# CPU: R0/R1 stratified analysis of Stage 10 + 11 outputs (see stage10_extra_r0r1.py).
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s10_r0r1
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/351_stage10/logs/r0r1_%j.log
export PYTHONDONTWRITEBYTECODE=1
~/conda-envs/jlens/bin/python -u ~/jlens_work/10_stage10/stage10_extra_r0r1.py
