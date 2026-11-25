#!/bin/bash
#SBATCH -J a3x_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a3x/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch cpu.sbatch "a30_h5.py freeze" "a30_h5.py precheck" "a30_h5.py tiny --root DIR" ...
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
cd /home/zhang.zhiqi2/jlens_work/24_gpubatch; rc=0
for step in "$@"; do echo "== $step"; /home/zhang.zhiqi2/conda-envs/jlens/bin/python $step || { echo "STEP FAILED: $step"; rc=1; }; done
exit $rc
