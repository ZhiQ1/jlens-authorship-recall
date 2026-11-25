#!/bin/bash
#SBATCH -J a3x_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a3x/gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/zhang.zhiqi2/jlens_work/24_gpubatch && /home/zhang.zhiqi2/conda-envs/jlens/bin/python gate.py
