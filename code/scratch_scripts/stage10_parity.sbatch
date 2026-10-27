#!/bin/bash
# Stage 10 parity gate: fast one-forward readout vs per-prefix JacobianLens.apply, same GPU layout as the run array.
#SBATCH --job-name=s10_parity
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=01:00:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/parity_%j.log
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "parity on $(hostname) gpus=$CUDA_VISIBLE_DEVICES"; nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python -u ~/jlens_work/10_stage10/351_stage10_fix1.py parity --n ${N:-12}
