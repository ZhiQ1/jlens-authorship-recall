#!/bin/bash
#SBATCH -J a21_synth
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a21/synth_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONUNBUFFERED=1
~/conda-envs/jlens/bin/python ~/jlens_work/16_inject/inject_analyze.py --synthetic /scratch/zhang.zhiqi2/jlens/391_groups/raw/a21_test_synth
