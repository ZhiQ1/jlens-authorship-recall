#!/bin/bash
# Stage 10 CPU job: name-format follow-up (stage10_extra_format.py / stage10_extra_cond_role.py).
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s10_extra_fmt
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/351_stage10/logs/extra_fmt_%j.log
export PYTHONDONTWRITEBYTECODE=1
~/conda-envs/jlens/bin/python -u ~/jlens_work/10_stage10/stage10_extra_format.py
