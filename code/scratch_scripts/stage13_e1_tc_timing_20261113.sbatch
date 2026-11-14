#!/bin/bash
#SBATCH -p short --account=cs7980.202710 -c 2 --mem=24G -t 00:40:00
#SBATCH -J e1tc1113 -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/e1_tc_timing_20261113_%j.log
#SBATCH --mail-type=END,FAIL --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/stage13_e1_tc_timing_20261113.py
