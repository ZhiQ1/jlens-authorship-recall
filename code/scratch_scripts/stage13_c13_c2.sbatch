#!/bin/bash
#SBATCH -J c13_c2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c13_c2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 13 C2. TINY=1 -> small subset into summary_c13/c2_tiny. Skip if the report already exists.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
R=/scratch/zhang.zhiqi2/jlens/381_stage13
if [ -n "$TINY" ]; then F=$R/summary_c13/c2_tiny/c13_C2.md; else F=$R/reports/c13_C2.md; fi
[ -s "$F" ] && { echo "exists: $F (skip)"; exit 0; }
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_c13_c2.py ${TINY:+--tiny}
