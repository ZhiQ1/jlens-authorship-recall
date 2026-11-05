#!/bin/bash
#SBATCH -J s13_x2tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x2tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# X2 whole pipeline on a random 2-layer Qwen3 with the real tokenizer: fit -> GPU code on CPU -> save -> reload -> analyse
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
$PY stage13_x2_fit.py --tiny && $PY stage13_x2.py --tiny && $PY stage13_x2_analyze.py --tiny
