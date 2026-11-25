#!/bin/bash
#SBATCH -J a33_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a33/gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Gate (written rule): all frozen shards + check shard 999 must have meta_XXX.json. Missing -> resubmit only the missing
# shards (array, <= 4 tasks) + a new gate, at most 4 rounds; complete -> analyze; round 4 still missing -> stop (mail).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
D=~/jlens_work/26_x4confirm; R=${ROUND:-1}; PY=~/conda-envs/jlens/bin/python
MISS=$($PY - <<'PY'
import json; from pathlib import Path
G=Path('/scratch/zhang.zhiqi2/jlens/391_groups'); fz=json.load(open(G/'raw/a33_freeze/freeze.json'))
need=fz['shards']+[999]; print(','.join(str(k) for k in need if not (G/f'raw/a33/meta_{k:03d}.json').exists()))
PY
)
echo "round $R missing: [$MISS]"
if [ -z "$MISS" ]; then
  $PY $D/a33_x4confirm.py analyze && echo "GATE: analysis done"; exit $?
fi
if [ "$R" -ge 4 ]; then echo "GATE STOP: shards still missing after 4 rounds: $MISS"; exit 1; fi
N=$(echo $MISS | tr ',' '\n' | wc -l); T=$(( N < 4 ? N : 4 ))
J=$(sbatch --parsable --array=0-$((T-1)) --export=ALL,MISSING=$MISS,NT=$T $D/a33_gpu_missing.sbatch) || { echo "sbatch failed; check squeue"; exit 1; }
sbatch --dependency=afterany:$J --export=ALL,ROUND=$((R+1)) $D/a33_gate.sbatch
echo "GATE: resubmitted $N shards as $J, next gate round $((R+1))"
