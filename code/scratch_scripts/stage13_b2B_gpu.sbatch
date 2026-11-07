#!/bin/bash
#SBATCH -J b2B_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2B_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 2 group B GPU (2-4 e1noise, 2-8 e1t5, 2-3 x3tok, 2-10 m3tok).
# MODE=gate (default): one real shard per item (e1noise 0, e1t5 false_0_check 0 + false_1 0, x3tok 0, m3tok 0) + gate checks
#   (HARD: exit 3 -> nothing else runs). MODE=all: every remaining unit (claims, skip-if-exists, stops ~6 min before the limit;
#   refuses to run if summary_b2B/gate.json says FAIL). TYPES=e1t5,m3tok (optional subset).
# AUTO=1: resubmit itself while units remain (only if work exited 0 and the gate is PASS; ROUND <= 8); when nothing remains,
#   submit stage13_b2B_analyze.sbatch.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv
cd $D
if [ "${MODE:-gate}" = all ]; then A="--all"; else A="--gate"; fi
[ -n "$TYPES" ] && A="$A --types $TYPES"
$PY stage13_b2B_gpu.py work $A --max-minutes 38; RC=$?
echo "work exit $RC"
LEFT=$($PY stage13_b2B_gpu.py remaining | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
G=$(grep -o '"status": "[A-Z]*"' /scratch/zhang.zhiqi2/jlens/381_stage13/summary_b2B/gate.json 2>/dev/null | tail -1)
ROUND=${ROUND:-1}; echo "left=$LEFT gate=$G round=$ROUND"
if [ "$RC" = 0 ] && [ "$AUTO" = 1 ] && [ "${LEFT:-0}" -gt 0 ] && [[ "$G" == *PASS* ]] && [ "$ROUND" -lt 8 ]; then
  for i in 1 2 3; do sbatch --export=ALL,MODE=all,AUTO=1,ROUND=$((ROUND+1)) $D/stage13_b2B_gpu.sbatch && break; sleep 20; squeue -u $USER -n b2B_gpu -h | grep -q . && break; done
elif [ "$RC" = 0 ] && [ "$AUTO" = 1 ] && [ "${LEFT:-1}" = 0 ]; then
  sbatch $D/stage13_b2B_analyze.sbatch
fi
exit $RC
