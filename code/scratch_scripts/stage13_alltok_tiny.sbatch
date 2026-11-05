#!/bin/bash
#SBATCH -J s13_alltok_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/alltok_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 9 tiny whole pipeline: GPU data code on a random 64-layer Qwen3 (CPU, 2 shards) -> probe (all runs; layers 24,40) -> report
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
set -e
$PY -u stage13_alltok_gpu.py --tiny --shards 0,1 --max-minutes 70
$PY -u stage13_alltok_probe.py --tiny --layers 24,40
$PY -u stage13_alltok_report.py --tiny
