#!/bin/bash
# CPU: E4b + 6.12 probe controls, per-paper vs author-team folds.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_cmp
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/cmp_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 SPLIT=group
P=~/conda-envs/jlens/bin/python; D=~/jlens_work/13_stage13

$P -u $D/stage13_split_compare.py
