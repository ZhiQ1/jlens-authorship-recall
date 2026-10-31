#!/bin/bash
# Stage 12 P2 hook check (U40): CPU tiny test of the whole pipeline (64-layer random tiny Qwen3, real tokenizer, 3 papers).
#SBATCH -J s12hk_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/hookcheck_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/12_stage12 && ~/conda-envs/jlens/bin/python -u stage12_p2_hookcheck.py --tiny
