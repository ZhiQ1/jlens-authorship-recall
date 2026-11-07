#!/bin/bash
#SBATCH -J b2np_probe
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 04:00:00
#SBATCH --array=0-4
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_probe_%A_%a.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 A probe, one array task per layer (32, 40, 48, 52, 56); needs all 432 GPU units; skip-if-exists per (run, layer).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
cd ~/jlens_work/13_stage13
LAYERS=(32 40 48 52 56)
~/conda-envs/jlens/bin/python -u stage13_b2_np_probe.py --layer ${LAYERS[$SLURM_ARRAY_TASK_ID]}
