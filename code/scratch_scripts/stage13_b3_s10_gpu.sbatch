#!/bin/bash
#SBATCH -J b3s10_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_s10_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 items 3-1 / 3-2 (addendum 14) GPU step: Stage 10 fast path at new layers, target + control, 7 conditions.
#   ITEM=3-1|3-2   MODE=gate (SHARDS, default 0: all 7 conditions of shard 0, then the hard check; exit 3 = FAIL)
#                  MODE=all  (claims + skip-if-exists; refuses unless summary_b3_s10_<item>/gate.json is PASS)
#   AUTO=1 (with MODE=all): resubmit itself while units remain (ROUND, MAX_ROUNDS default 16), then submit the analysis once.
# Budget: python stops starting units ~1.5 unit-times before 38 min (limit 45 min, >= 6 min safety incl. model load).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
ITEM=${ITEM:-3-1}; MODE=${MODE:-gate}
nvidia-smi --query-gpu=name,memory.total --format=csv || true
df -h /scratch | tail -1 || true
if [ "$MODE" = "all" ]; then ARGS="--all"; else ARGS="--shards ${SHARDS:-0}"; fi
$PY -u stage13_b3_s10_gpu.py run --item "$ITEM" $ARGS --max-minutes 38
rc=$?
echo "run exit $rc (0 ok, 3 hard check failed / refused, other = crash)"
if [ $rc -eq 0 ] && [ "$MODE" = "all" ] && [ "${AUTO:-0}" = "1" ]; then
  $PY -u stage13_b3_s10_gpu.py chain --item "$ITEM" || echo "WARNING: chain step failed (resubmit by hand)"
fi
exit $rc
