#!/bin/bash
# CPU check of the Stage 11 GPU code with the real Qwen3-32B weights and the real public lens (see stage11_cpu_realcheck.py).
#SBATCH --job-name=s11_realcheck
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/361_stage11/logs/realcheck_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
lscpu | grep -E "Model name|Flags" | cut -c1-200 | grep -oE "Model name.*|avx512_bf16|amx_bf16" | sort -u
~/conda-envs/jlens/bin/python -u ~/jlens_work/11_stage11/stage11_cpu_realcheck.py /scratch/$USER/jlens/361_stage11_realcheck
