#!/bin/bash
#SBATCH -J b3_71b_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_71b_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 item 3-3 analysis (CPU): hard check re-run (exit 3 = FAIL under HC33_POLICY=plan), coverage, 7.1B estimands, report.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b3_71b_analyze.py
rc=$?; echo "analyze exit $rc"; exit $rc
