#!/bin/bash
# Stage 10 self-requeueing GPU worker (GPU QOS allows only 8 queued / 4 running jobs / 4 GPUs per user).
# One model load per job; processes CONDITIONS in order over shards SHARDS; at the time budget it stops cleanly and
# resubmits itself. When nothing is left anywhere, the last worker submits the CPU analysis jobs (once, via lock dir).
#   sbatch --export=ALL,SHARDS=0-35  --job-name=s10_w0 stage10_worker.sbatch
#   sbatch --export=ALL,SHARDS=36-71 --job-name=s10_w1 stage10_worker.sbatch
# Gate: parity PASS (run refuses otherwise). A crash does NOT requeue (mail FAIL instead).
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/worker_%x_%j.log

CONDITIONS=${CONDITIONS:-true,false_0,false_1,false_2,false_3,false_4,delete}
SHARDS=${SHARDS:?set SHARDS, e.g. 0-35}
ROOT=/scratch/$USER/jlens/351_stage10; DIR=~/jlens_work/10_stage10
PY=~/conda-envs/jlens/bin/python; S=$DIR/351_stage10_fix1.py
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) worker $SLURM_JOB_NAME job $SLURM_JOB_ID shards $SHARDS conditions $CONDITIONS on $(hostname)"
nvidia-smi --query-gpu=name,memory.total --format=csv
$PY -u $S run --condition $CONDITIONS --shards $SHARDS --max-minutes 440 || { echo "run failed (exit $?) - not requeueing"; exit 1; }

left=$($PY $S remaining --condition $CONDITIONS --shards $SHARDS)
echo "$(date -Is) missing files in my shards: $left"
if [ "$left" -gt 0 ]; then
  sbatch --export=ALL,SHARDS=$SHARDS,CONDITIONS=$CONDITIONS --job-name=$SLURM_JOB_NAME $DIR/stage10_worker.sbatch
  exit 0
fi
all_true=$($PY $S remaining --condition true); all=$($PY $S remaining --condition $CONDITIONS)
echo "missing overall: true=$all_true all=$all"
if [ "$all_true" -eq 0 ] && mkdir $ROOT/logs/.analyze_main_submitted 2>/dev/null; then
  sbatch --export=ALL,MODE=main --job-name=s10_analyze_main $DIR/stage10_analyze.sbatch; fi
if [ "$all" -eq 0 ] && mkdir $ROOT/logs/.analyze_title_submitted 2>/dev/null; then
  sbatch --export=ALL,MODE=title --job-name=s10_analyze_title $DIR/stage10_analyze.sbatch; fi
