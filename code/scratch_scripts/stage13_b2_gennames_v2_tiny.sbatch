#!/bin/bash
#SBATCH -J b2c_gn2_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_v2_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D12-3 selftest + tiny
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /home/zhang.zhiqi2/jlens_work/13_stage13
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage13_b2_gennames_v2.py selftest || exit 1
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage13_b2_gennames_v2.py tiny --root /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_v2tiny_$SLURM_JOB_ID
