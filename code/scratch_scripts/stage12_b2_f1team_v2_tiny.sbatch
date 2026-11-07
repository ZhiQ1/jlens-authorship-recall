#!/bin/bash
#SBATCH -J b2c_f1t2_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_v2_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D12-2 selftest + tiny (joint 40-prompt fit bitwise vs stored, (S_A+S_B)/40)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /home/zhang.zhiqi2/jlens_work/12_stage12
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage12_b2_f1team_v2.py selftest || exit 1
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage12_b2_f1team_v2.py tiny --root /scratch/zhang.zhiqi2/jlens/371_stage12/test_b2_f1team_v2_$SLURM_JOB_ID
