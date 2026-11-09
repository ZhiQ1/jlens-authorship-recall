#!/bin/bash
#SBATCH -J b2gnb_lockst
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_lockstats_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# addendum 15 lock statistics on stored texts (two-name items, true names ending in 'and', P due to it)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd /home/zhang.zhiqi2/jlens_work/13_stage13
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage13_b2_gennames_b_lockstats.py --out /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b/summary/lock_stats.json
