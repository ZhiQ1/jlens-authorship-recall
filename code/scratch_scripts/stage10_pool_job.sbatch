#!/bin/bash
# One Stage 10 pool chunk: run CONDITION over SHARDS for READOUTS@LAYERS on 1xA100-80GB. Submitted by stage10_pool.py,
# which sets --partition/--time/--job-name/--output/--dependency; lists use ':' (sbatch --export splits on ',').
# Does not requeue itself: unfinished shards go back to the pool.
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) pool job $SLURM_JOB_NAME $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION cond=$CONDITION shards=$SHARDS readouts=$READOUTS layers=$LAYERS budget=${BUDGET}min"
nvidia-smi --query-gpu=name,memory.total --format=csv
~/conda-envs/jlens/bin/python -u ~/jlens_work/10_stage10/351_stage10_fix1.py run --condition $CONDITION --shards ${SHARDS//:/,} \
  --readouts ${READOUTS//:/,} --layers ${LAYERS//:/,} --max-minutes $BUDGET
