#!/bin/bash
# Stage 10 extension worker: stage10_worker.sbatch with READOUTS/LAYERS passed to run/remaining and its own analysis locks.
#   sbatch --export=ALL,SHARDS=0-35,READOUTS=jlens_public,logit,LAYERS=50,...  --job-name=s10x_w0 stage10_ext_worker.sbatch
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

[ -e /scratch/$USER/jlens/351_stage10/logs/.pool_active ] && { echo "pool manages the extension; nothing to do"; exit 0; }
CONDITIONS=${CONDITIONS:-true,false_0,false_1,false_2,false_3,false_4,delete}
SHARDS=${SHARDS:?set SHARDS, e.g. 0-35}; READOUTS=${READOUTS:?}; LAYERS=${LAYERS:?}
ROOT=/scratch/$USER/jlens/351_stage10; DIR=~/jlens_work/10_stage10
PY=~/conda-envs/jlens/bin/python; S=$DIR/351_stage10_fix1.py; F="--readouts $READOUTS --layers $LAYERS"
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) ext worker $SLURM_JOB_NAME job $SLURM_JOB_ID shards $SHARDS conditions $CONDITIONS $F on $(hostname)"
nvidia-smi --query-gpu=name,memory.total --format=csv
$PY -u $S run $F --condition $CONDITIONS --shards $SHARDS --max-minutes 440 || { echo "run failed (exit $?) - not requeueing"; exit 1; }

left=$($PY $S remaining $F --condition $CONDITIONS --shards $SHARDS)
echo "$(date -Is) missing files in my shards: $left"
if [ "$left" -gt 0 ]; then
  sbatch --export=ALL,SHARDS=$SHARDS,CONDITIONS=$CONDITIONS,READOUTS=$READOUTS,LAYERS=$LAYERS --job-name=$SLURM_JOB_NAME $DIR/stage10_ext_worker.sbatch
  exit 0
fi
all=$($PY $S remaining $F --condition $CONDITIONS)
echo "missing overall (ext): $all"
if [ "$all" -eq 0 ] && mkdir $ROOT/logs/.analyze_ext_submitted 2>/dev/null; then
  sbatch --export=ALL --job-name=s10x_analyze $DIR/stage10_ext_analyze.sbatch; fi
