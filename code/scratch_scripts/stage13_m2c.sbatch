#!/bin/bash
# CPU: Stage 13 M1 (lens top-1 classes) and M2 (probes for non-name content) on existing Stage 10/11 outputs.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_m2c
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/cpu_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16
~/conda-envs/jlens/bin/python -u ~/jlens_work/13_stage13/stage13_m2c.py
