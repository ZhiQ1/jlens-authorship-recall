#!/bin/bash
#SBATCH -J b1x_gpu
#SBATCH -p gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1xall_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# addendum 10 item 1 GPU: SHARDS="0" (first real shard) or "--all" (skip-if-exists per component and shard; stops before the limit)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
if [ "${SHARDS:-0}" = "--all" ]; then ARGS="--all"; else ARGS="--shards ${SHARDS:-0}"; fi
~/conda-envs/jlens/bin/python stage13_b1_xall.py $ARGS --max-minutes 40
