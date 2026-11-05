#!/bin/bash
#SBATCH -J s13_alltok_rep
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/alltok_report_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_alltok_report.py ${TINY:+--tiny}
