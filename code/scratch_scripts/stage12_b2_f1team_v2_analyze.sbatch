#!/bin/bash
#SBATCH -J b2c_f1t2_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_v2_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-2 v2: D12-2 hard check (exit 2) then analysis
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /home/zhang.zhiqi2/jlens_work/12_stage12
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage12_b2_f1team_v2.py hardcheck || exit 2
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage12_b2_f1team_v2.py analyze
