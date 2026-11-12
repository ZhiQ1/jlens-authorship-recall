#!/bin/bash
#SBATCH -J b2c_fitb4watch
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 2-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v4_watch_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-1 v4 watchdog (CPU, D12-5, 2026-11-12): gate v4 then chain v4, one GPU job at a time, kill cap 3. See stage9_b2_fitb_v4_watch.py.
#   sbatch stage9_b2_fitb_v4_watch.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_v4_watch.py
