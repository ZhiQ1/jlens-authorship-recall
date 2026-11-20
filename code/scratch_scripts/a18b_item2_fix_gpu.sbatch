#!/bin/bash
#SBATCH -J a18b_i2fix
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/a18b/gpu_%x_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# a18b item 2 step-2 FIX worker (2026-11-19). env: CMD (work | parity), SHARDS (e.g. 0 or 1-6), MAXMIN (default 40).
# Skips finished units; stops itself before the time limit; checks WARN only; exit != 0 only on a code crash.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) a18b item 2 fix ${CMD:-work} job $SLURM_JOB_ID on $(hostname) SHARDS=${SHARDS:-all}"
nvidia-smi --query-gpu=name,memory.total --format=csv || echo "WARN nvidia-smi failed"
cd /home/zhang.zhiqi2/jlens_work/13_stage13
T0=$(date +%s)
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u a18b_item2_fix.py ${CMD:-work} --shards "${SHARDS:-all}" --max-minutes "${MAXMIN:-40}"; RC=$?
echo "$(date -Is) ${CMD:-work} exit $RC elapsed_s=$(( $(date +%s) - T0 ))"; exit $RC
