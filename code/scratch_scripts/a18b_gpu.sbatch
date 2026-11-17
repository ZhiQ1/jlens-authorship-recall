#!/bin/bash
#SBATCH -J a18b
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/a18b/gpu_%x_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 18b GPU worker (2026-11-17). env: ITEM (1..6), SHARDS (e.g. 0 or 1-23), MAXMIN (default 40), EXTRA (extra args).
# Skips finished units; stops itself before the time limit; checks are WARN only; exit != 0 only on a code crash.
# Submit: EX=$(~/conda-envs/jlens/bin/python ~/jlens_work/killguard.py exclude --name a18b_i$ITEM --minutes 45); sbatch $EX -J a18b_i$ITEM --export=ALL,ITEM=..,SHARDS=.. this_file
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) a18b item ${ITEM} job $SLURM_JOB_ID on $(hostname) SHARDS=${SHARDS:-all}"
nvidia-smi --query-gpu=name,memory.total --format=csv || echo "WARN nvidia-smi failed"
cd /home/zhang.zhiqi2/jlens_work/13_stage13
T0=$(date +%s)
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u a18b_item${ITEM}.py work --shards "${SHARDS:-all}" --max-minutes "${MAXMIN:-40}" ${EXTRA}; RC=$?
echo "$(date -Is) work exit $RC elapsed_s=$(( $(date +%s) - T0 ))"; exit $RC
