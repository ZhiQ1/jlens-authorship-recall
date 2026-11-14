#!/bin/bash
#SBATCH -J c24conf
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c24_conf_20261114_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# C24 follow-up 1a/1b/1c (CPU, post-hoc). plan_batch_20261114b item 1.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
echo "$(date -Is) c24conf $SLURM_JOB_ID on $(hostname)"
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_c24_conf_20261114.py
