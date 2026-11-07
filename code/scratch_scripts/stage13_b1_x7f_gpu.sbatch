#!/bin/bash
#SBATCH -J s13_b1x7f
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b1_x7f_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 10 item 2 GPU units (skip-if-exists). Env: CHECK=1 (false_0 shard-0 re-run + hard check a), UNITS=<spec>,
# AUTO=1 resubmit itself while units remain (only if hard check a PASSED; at most ROUND <= 6; a crash stops the chain).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/13_stage13
nvidia-smi --query-gpu=name,memory.total --format=csv
cd $D
ARGS=""; [ -n "$CHECK" ] && ARGS="--check"; [ -n "$UNITS" ] && ARGS="$ARGS --units $UNITS"
$PY stage13_b1_x7f.py work $ARGS --max-minutes 38; RC=$?
echo "work exit $RC"
LEFT=$($PY stage13_b1_x7f.py remaining | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
HC=$(grep -o '"status": "[A-Z]*"' /scratch/zhang.zhiqi2/jlens/381_stage13/summary_b1_x7f/hardcheck_a_rerun.json 2>/dev/null | tail -1)
ROUND=${ROUND:-1}
echo "left=$LEFT hardcheck_a=$HC round=$ROUND"
if [ "$RC" = 0 ] && [ "$AUTO" = 1 ] && [ "${LEFT:-0}" -gt 0 ] && [[ "$HC" == *PASS* ]] && [ "$ROUND" -lt 6 ]; then
  for i in 1 2 3; do sbatch --export=ALL,CHECK=,UNITS=,AUTO=1,ROUND=$((ROUND+1)) $D/stage13_b1_x7f_gpu.sbatch && break; sleep 20; squeue -u $USER -n s13_b1x7f -h | grep -q . && break; done
elif [ "$RC" = 0 ] && [ "${LEFT:-1}" = 0 ]; then
  sbatch $D/stage13_b1_x7f_analyze.sbatch
fi
