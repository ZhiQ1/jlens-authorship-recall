#!/bin/bash
#SBATCH -J s11_e1noise_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=24G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/361_stage11/logs/e1noise_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/11_stage11
~/conda-envs/jlens/bin/python stage11_e1_batchnoise.py tiny --root /scratch/zhang.zhiqi2/jlens/361_stage11/test_e1noise
~/conda-envs/jlens/bin/python stage11_e1_batchnoise.py analyze --root /scratch/zhang.zhiqi2/jlens/361_stage11/test_e1noise
