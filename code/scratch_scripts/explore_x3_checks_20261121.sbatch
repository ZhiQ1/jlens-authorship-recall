#!/bin/bash
#SBATCH -J x3chk
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x3chk_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8
set -e
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/explore_x3_checks_20261121.py --limit 60 --out /scratch/zhang.zhiqi2/jlens/381_stage13/summary_explore_x3_checks_20261121_tiny
echo TINY OK
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/explore_x3_checks_20261121.py
