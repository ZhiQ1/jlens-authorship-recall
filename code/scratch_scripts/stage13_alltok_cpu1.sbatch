#!/bin/bash
#SBATCH -J s13_alltok_cpu1
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/alltok_cpu1_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 9: (a) real vocab rows from safetensors (CPU); (b) tiny whole-code-path test of the GPU data script on a random 64-layer Qwen3 (2 shards)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
$PY -u stage13_alltok_vocab.py
$PY -u stage13_alltok_gpu.py --tiny --shards 0,1 --max-minutes 70
