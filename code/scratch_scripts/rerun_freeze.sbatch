#!/bin/bash
#SBATCH -J g391_rerun_freeze
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:20:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/rerun_freeze_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/14_groups && ~/conda-envs/jlens/bin/python rerun_gpu.py freeze
