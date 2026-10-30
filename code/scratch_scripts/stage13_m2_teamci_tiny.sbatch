#!/bin/bash
# CPU: Stage 13 M2 team-cluster bootstrap CIs (prereg addendum 2 "intervals", U45). tiny run.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_m2tci_tiny
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/m2teamci_tiny_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 SPLIT=group TINY=1
~/conda-envs/jlens/bin/python -u ~/jlens_work/13_stage13/stage13_m2_teamci.py
