#!/bin/bash
#SBATCH -J b2gnb_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b (draft addendum 15, unlocked): matcher examples + H3 parity + tiny full pipeline (random 4-layer model, CPU) + cost numbers
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /home/zhang.zhiqi2/jlens_work/13_stage13
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage13_b2_gennames_b_pipeline.py tiny --root /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b_tiny/run_$SLURM_JOB_ID
