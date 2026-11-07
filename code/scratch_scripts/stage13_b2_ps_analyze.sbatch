#!/bin/bash
#SBATCH -J b2ps_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_ps_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Items 2-7 / 2-9 analysis + hard checks. ARGS="--partial" = one-shard gate. Exit 3 = hard check failed.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b2_ps_analyze.py ${ARGS:-}
