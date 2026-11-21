#!/bin/bash
#SBATCH -J l4audit
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/l4audit_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch explore_l4audit_20261121.sbatch [--test]
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/explore_l4audit_20261121.py "$@"
