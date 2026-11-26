#!/bin/bash
#SBATCH -J todo_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/todo_gate_%x_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# ITEM=e1u0|a27|a28|a29 sbatch --export=ALL todo_gate.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
echo "gate ITEM=$ITEM"
~/conda-envs/jlens/bin/python ~/jlens_work/19_todo/todo_gate.py
