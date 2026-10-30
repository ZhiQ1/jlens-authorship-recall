#!/bin/bash
# CPU: E4b + 6.12 probe controls with training-fold standardisation (tiny run). Script: stage13_e4b_trainstd.py
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_e4bstd_tiny
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/e4bstd_tiny_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 TINY=1
P=~/conda-envs/jlens/bin/python; D=~/jlens_work/13_stage13

$P -u $D/stage13_e4b_trainstd.py
