#!/bin/bash
#SBATCH -J s13_v42m3
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 06:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/v42_m3_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/13_stage13
# rule 1: whole pipeline on 1,500 papers / 3 layers first; the full run only if the test finishes
~/conda-envs/jlens/bin/python stage13_v42_m3_paperboot.py --test && ~/conda-envs/jlens/bin/python stage13_v42_m3_paperboot.py
