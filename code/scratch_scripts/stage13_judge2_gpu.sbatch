#!/bin/bash
#SBATCH --job-name=s13_judge2
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/judge2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_judge2.py --run
