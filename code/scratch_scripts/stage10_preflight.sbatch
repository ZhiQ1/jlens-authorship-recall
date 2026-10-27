#!/bin/bash
# CPU preflight for Stage 10 pool jobs: every check before the GPU load (see stage10_preflight.py).
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s10_preflight
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/351_stage10/logs/preflight_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
~/conda-envs/jlens/bin/python -u ~/jlens_work/10_stage10/stage10_preflight.py
