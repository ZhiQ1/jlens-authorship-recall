#!/bin/bash
#SBATCH -J s13_x7
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x7_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_x7_analyze.py
