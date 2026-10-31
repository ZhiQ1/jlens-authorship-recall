#!/bin/bash
#SBATCH -J s13_x1vsC
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:15:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x1_vsC_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_x1_vsC.py
