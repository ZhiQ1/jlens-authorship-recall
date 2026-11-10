#!/bin/bash
#SBATCH -J b2c_fitb3c_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v3c_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-1 analysis in the D12-4 continuation root (stage9_b2_fitb_v3c.py analyze = v2 analyze --root b2_fitb_d124; needs the verified record)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /home/zhang.zhiqi2/jlens_work/09_stage9
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage9_b2_fitb_v3c.py analyze
