#!/bin/bash
#SBATCH -p short --account=cs7980.202710 -c 4 --mem=48G -t 04:00:00
#SBATCH -J teamci_s1012
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/teamci_s10_12_%x_%j.log
#SBATCH --mail-type=END,FAIL --mail-user=zhang.zhiqi2@northeastern.edu
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
cd /scratch/zhang.zhiqi2/jlens
~/conda-envs/jlens/bin/python -u ~/jlens_work/13_stage13/stage13_teamci_s10_12.py $PART
