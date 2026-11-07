#!/bin/bash
#SBATCH -J b2ps_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_ps_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Items 2-7 / 2-9 GPU. SHARDS="0" (gate, one Stage 11 sample shard, ~8 min) or SHARDS="--all" (claim mode, skip-if-exists,
# stops ~6 min before the limit). Hard checks run in the analysis (stage13_b2_ps_analyze.sbatch; ARGS=--partial for the gate).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv || true
if [ "${SHARDS:-0}" = "--all" ]; then ARGS="--all"; else ARGS="--shards ${SHARDS:-0}"; fi
~/conda-envs/jlens/bin/python -u stage13_b2_ps_gpu.py $ARGS --max-minutes 40
