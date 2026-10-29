#!/bin/bash
#SBATCH -J s13_m3
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 08:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/m3_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
cd ~/jlens_work/13_stage13
# rule 1: whole pipeline on 3 shards / 2 layers first; the full run only if the test finishes
~/conda-envs/jlens/bin/python stage13_m3_analyze.py --test && ~/conda-envs/jlens/bin/python stage13_m3_analyze.py
