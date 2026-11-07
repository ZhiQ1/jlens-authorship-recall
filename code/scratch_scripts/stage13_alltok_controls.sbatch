#!/bin/bash
#SBATCH -J s13_alltok_ctrl
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 02:00:00
#SBATCH --array=0-6
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/alltok_ctrl_%A_%a.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 9 follow-up: permutation controls for the all-token probe (CPU; skip-if-exists)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
RUNS=(e4b_parity first_alltok initial given_first given_cont surname_first surname_cont)
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_alltok_controls.py --runs ${RUNS[$SLURM_ARRAY_TASK_ID]} ${EXTRA}
