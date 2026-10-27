#!/bin/bash
# Stage 12 CPU job: name-prior analyses A/B/C and probe controls (see stage12_cpu.py).
#SBATCH --job-name=s12_cpu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/371_stage12/logs/cpu_%j.log
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
~/conda-envs/jlens/bin/python -u ~/jlens_work/12_stage12/stage12_cpu.py
