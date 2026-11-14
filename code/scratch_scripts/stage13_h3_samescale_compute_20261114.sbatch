#!/bin/bash
#SBATCH -J h3ss_comp
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=80G
#SBATCH -t 03:00:00
#SBATCH --array=0-5
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/summary_h3_samescale_20261114/logs/compute_%A_%a.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Plan 2026-11-14b item 2, H3 same-scale (post hoc, strengthening 2, descriptive). CPU only. Array task = title condition.
# TINY=1 -> --tiny (shard 0, L40). skip-if-exists.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
CONDS=(true false_0 false_1 false_2 false_3 false_4)
EXTRA=""; [ "${TINY:-0}" = 1 ] && EXTRA="--tiny"
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_h3_samescale_compute_20261114.py --cond ${CONDS[$SLURM_ARRAY_TASK_ID]} $EXTRA
