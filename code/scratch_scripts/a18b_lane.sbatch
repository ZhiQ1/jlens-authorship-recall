#!/bin/bash
#SBATCH -J a18b_lane
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
# Addendum 18b self-resubmitting GPU lane (2026-11-17). env: ITEM, SHARDS (lane's shard set), ROUND (default 1).
# Runs a18b_item$ITEM.py work on the lane's shards (skip finished units, budget = min(40, time left - 4) min).
# Then: work exit != 0 (code crash) -> stop the lane (no resubmit). Lane units left and ROUND < 12 -> resubmit itself (killguard
# exclude + record). No unit of the item left at all -> submit the CPU analysis once (atomic mkdir lock).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; D=/home/zhang.zhiqi2/jlens_work/13_stage13; ROUND=${ROUND:-1}
echo "$(date -Is) a18b lane item ${ITEM} shards ${SHARDS} round ${ROUND} job $SLURM_JOB_ID on $(hostname)"
nvidia-smi --query-gpu=name,memory.total --format=csv || echo "WARN nvidia-smi failed"
cd $D; T0=$(date +%s)
$PY -u a18b_item${ITEM}.py work --shards "$SHARDS" --max-minutes 40; RC=$?
echo "$(date -Is) work exit $RC elapsed_s=$(( $(date +%s) - T0 ))"
LEFT_LANE=$($PY a18b_item${ITEM}.py remaining --shards "$SHARDS" | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
LEFT_ALL=$($PY a18b_item${ITEM}.py remaining | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
echo "left_lane=$LEFT_LANE left_all=$LEFT_ALL"
$PY $D/a18b_progress.py "lane item $ITEM shards $SHARDS round $ROUND job $SLURM_JOB_ID: work exit $RC, elapsed $(( $(date +%s) - T0 )) s, left lane $LEFT_LANE / item $LEFT_ALL"
if [ "$RC" != 0 ]; then echo "CRASH: lane stopped"; exit $RC; fi
if [ "${LEFT_LANE:-1}" -gt 0 ] && [ "$ROUND" -lt 12 ]; then
  EX=$($PY /home/zhang.zhiqi2/jlens_work/killguard.py exclude --name a18b_i$ITEM --minutes 45 --ignore $SLURM_JOB_ID | tail -1)
  [ "$EX" = DEFER ] && EX=""
  for i in 1 2 3; do
    OUT=$(sbatch --parsable $EX -J a18b_i$ITEM --comment="lane_${ITEM}_${SHARDS}" --export=ALL,ITEM=$ITEM,SHARDS="$SHARDS",ROUND=$((ROUND+1)) $D/a18b_lane.sbatch 2>&1) && break
    sleep 30; squeue -u zhang.zhiqi2 -h -n a18b_i$ITEM -o %k | grep -qx "lane_${ITEM}_${SHARDS}" && { OUT="(already queued)"; break; }
  done
  echo "resubmitted: $OUT"; $PY /home/zhang.zhiqi2/jlens_work/killguard.py record --jid "${OUT%%;*}" --name a18b_i$ITEM --minutes 45 --orch a18b 2>/dev/null
elif [ "${LEFT_ALL:-1}" = 0 ]; then
  if mkdir /scratch/zhang.zhiqi2/jlens/381_stage13/logs/a18b/.analyze_submitted_item$ITEM 2>/dev/null; then
    J=$(sbatch --parsable -J a18b_an$ITEM --export=ALL,ITEM=$ITEM,CMD=analyze $D/a18b_cpu.sbatch); echo "analysis submitted $J"
    $PY $D/a18b_progress.py "item $ITEM: all GPU units done; analysis job $J"
  fi
fi
