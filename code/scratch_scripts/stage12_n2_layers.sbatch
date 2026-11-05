#!/bin/bash
#SBATCH -J s12_n2lay
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/n2_layers_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/13_stage13
# CPU only, reads saved ranks; outputs are new files (timestamp suffix if they exist). Self-check final@63 vs Stage 12 (WARN only).
~/conda-envs/jlens/bin/python stage12_n2_layers.py
