#!/bin/bash
#SBATCH -J b2c_fitb3watch
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 2-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v3b_watch_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-1 watchdog (CPU, see stage9_b2_fitb_v3b_watch.py): (re)submits the D12-1 gate and the resume/holdout/read chain after node-epilog
# SIGKILLs (sacct 0:9), max 6 each; stops on gate FAIL, any other failure, or a chain stop rule. Args: previous gate job ids.
#   sbatch stage9_b2_fitb_v3b_watch.sbatch 11746631
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_v3b_watch.py "$@"
