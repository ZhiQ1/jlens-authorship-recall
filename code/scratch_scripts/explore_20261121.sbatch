#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -J expl1121
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/explore_20261121_%j.out
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
PY=~/conda-envs/jlens/bin/python
$PY ~/jlens_work/13_stage13/explore_citesplit_probes_20261121.py "$@" || echo "TASK1 FAILED"
$PY ~/jlens_work/13_stage13/explore_dir_overlap_20261121.py "$@" || echo "TASK2 FAILED"
