#!/bin/bash
#SBATCH -J a18b_keeper
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 2-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/a18b/keeper_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 18b queue keeper (2026-11-17): a18b_keeper.py run (polls every 5 min, <= 4 GPU jobs pending+running, item order 4,1,6,5,2,3,(2s)).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd /home/zhang.zhiqi2/jlens_work/13_stage13
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u a18b_keeper.py run
