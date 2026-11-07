#!/bin/bash
#SBATCH -J b1x_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1xall_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# addendum 10 item 1, whole pipeline on a random 2-layer Qwen3 (real tokenizer): S_auth refit -> GPU code on CPU (author 0
# compared with the frozen functions) -> analysis (hard-check code path against the frozen functions' output)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
export B1_TAG=$SLURM_JOB_ID
$PY stage13_b1_xall_fit.py --tiny && $PY stage13_b1_xall.py --tiny && $PY stage13_b1_xall_analyze.py --tiny
