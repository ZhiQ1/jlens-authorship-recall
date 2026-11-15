#!/bin/bash
#SBATCH -J e1x6x
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/e1x6_extra_20261114_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# E1 + X6 at L41-47, 49, 51 (+ overlap 40, 48, 50, 52, 54, 56) - stage13_e1x6_extra_20261114.py work.
# env: TITLES (comma list, e.g. false_0 or false_1,false_2), SHARDS (e.g. 0-23 or 0,5,7), SAMPLE (s11 default | U0, optional).
# Skips finished units; stops itself before the time limit (budget = min(40, time left - 4) min); checks are WARN only.
# Submit with killguard: EX=$(~/conda-envs/jlens/bin/python ~/jlens_work/killguard.py exclude --name e1x6x --minutes 45); sbatch $EX --export=ALL,TITLES=...,SHARDS=... this_file
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) e1x6x $SLURM_JOB_ID on $(hostname) TITLES=${TITLES:-all} SHARDS=${SHARDS:-all} SAMPLE=${SAMPLE:-s11}"
nvidia-smi --query-gpu=name,memory.total --format=csv || echo "WARN nvidia-smi failed"
CMD=(/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_e1x6_extra_20261114.py work
     --sample "${SAMPLE:-s11}" --shards "${SHARDS:-all}" --max-minutes 40)
[ -n "$TITLES" ] && CMD+=(--titles "$TITLES")
if [ "${DRYRUN:-0}" = 1 ]; then echo "DRYRUN: ${CMD[*]}"; exit 0; fi
"${CMD[@]}"; RC=$?
echo "$(date -Is) work exit $RC"; exit $RC
