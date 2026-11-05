#!/bin/bash
#SBATCH -J s12_f1sh_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=24G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/f1split_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/12_stage12
~/conda-envs/jlens/bin/python stage12_f1_splithalf.py tiny --root /scratch/zhang.zhiqi2/jlens/371_stage12/test_f1split
