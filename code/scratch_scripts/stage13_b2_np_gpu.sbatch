#!/bin/bash
#SBATCH -J b2np_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 A GPU data step. SHARDS="0" (gate: all 6 title conditions of shard 0, ~4 min) or SHARDS="--all" (claim mode,
# skip-if-exists, stops ~5 min before the limit). Exit 3 = HARD CHECK 1 failed (summary_b2_np/HARD_CHECK1_FAILED).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv || true
if [ "${SHARDS:-0}" = "--all" ]; then ARGS="--all"; else ARGS="--shards ${SHARDS:-0}"; fi
~/conda-envs/jlens/bin/python -u stage13_b2_np_gpu.py $ARGS --max-minutes 40
