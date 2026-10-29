#!/bin/bash
#SBATCH -J s13_text2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 04:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/text2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python stage13_x4_textbase2.py || echo "X4TEXT2 FAILED"
