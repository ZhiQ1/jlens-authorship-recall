#!/bin/bash
#SBATCH -J s13_posctrl
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/posctrl_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/13_stage13
EXCLUDE_TEAM=0 ~/conda-envs/jlens/bin/python stage13_x4_textbase.py || echo "X4TEXT FAILED"
