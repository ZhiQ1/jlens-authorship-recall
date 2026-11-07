#!/bin/bash
#SBATCH -J b1e4b5_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1_e4b5_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 item 4 tiny whole pipeline: GPU data code on a random 64-layer Qwen3 (CPU, 2 shards, all 6 conditions) -> probe (all runs; L24, L40) -> report
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
set -e
$PY -u stage13_b1_e4b5_gpu.py --tiny --conds true,false_0,false_1,false_2,false_3,false_4 --shards 0,1
$PY -u stage13_b1_e4b5_probe.py --tiny --layers 24,40
$PY -u stage13_b1_e4b5_report.py --tiny
