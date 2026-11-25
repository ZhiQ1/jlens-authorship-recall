#!/bin/bash
#SBATCH -J conf_resid
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=48G
#SBATCH -t 08:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b/logs_predfirst_split/%x_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# post-hoc: confidence residualised on name features (CPU only)
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 HF_HUB_OFFLINE=1
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/stage13_b2_gennames_b_conf_resid_20261125.py
