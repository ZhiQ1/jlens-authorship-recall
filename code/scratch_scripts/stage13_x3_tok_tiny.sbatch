#!/bin/bash
#SBATCH -J s13_x3tok_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x3tok_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_x3_tok_gpu.py tiny --root /scratch/zhang.zhiqi2/jlens/381_stage13/test_x3tok
