#!/bin/bash
#SBATCH -J s13_v56
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=40G
#SBATCH -t 04:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/v56_retrieval_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/13_stage13
# rule 1: whole pipeline on 600 papers / 2 layers first; the full run only if the test finishes
~/conda-envs/jlens/bin/python stage13_v56_retrieval.py --test && ~/conda-envs/jlens/bin/python stage13_v56_retrieval.py
