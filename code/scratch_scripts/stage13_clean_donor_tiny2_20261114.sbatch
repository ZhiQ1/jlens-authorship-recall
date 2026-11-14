#!/bin/bash
#SBATCH -J clean_donor_tiny2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/clean_donor_tiny2_20261114_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# plan 2026-11-14b item 3, tiny/parity: surname_first L40 only, 200 draws, test output dir
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_clean_donor_20261114.py --runs surname_first --layers 40 --nb 200 --out /scratch/zhang.zhiqi2/jlens/381_stage13/clean_donor_tiny2_20261114
