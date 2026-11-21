#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -J pca_np
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/explore_pca_np_%j.out
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/explore_pca_np_20261120.py "$@"
