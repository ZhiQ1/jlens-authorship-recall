#!/bin/bash
#SBATCH -J tg_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/tablegpu_gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Gate for addenda 24 / 25 (written rule). EXP=a24|a25 via --export=ALL.
# 1) full shard list from the experiment's freeze (never a hard-coded range); 2) done marker per shard;
# 3) budget: projected GPU-h = mean measured job time per shard x missing shards; a24 <= 1.0 h, a25 <= 3.0 h, else STOP + mail;
# 4) resubmit missing shards (a24: 12 per job, a25: 6 per job; <= 2 GPU jobs per round so the 8-job QOS holds), requeue itself afterany; <= 4 rounds;
# 5) all done -> analysis.
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
W=~/jlens_work/21_tablegpu; G=/scratch/zhang.zhiqi2/jlens/391_groups; PY=~/conda-envs/jlens/bin/python
ST=$G/logs/${EXP}_gate_state.txt; round=$(cat $ST 2>/dev/null || echo 0); round=$((round+1)); echo $round > $ST
read -r -d '' CODE <<'EOF'
import json, os, glob, sys, pandas as pd
G = '/scratch/zhang.zhiqi2/jlens/391_groups'; e = os.environ['EXP']
if e == 'a24':
    sh = sorted(pd.read_parquet(f'{G}/raw/a24_freeze/variants.parquet').shard.unique())
    done = lambda k: all(os.path.exists(f'{G}/raw/a24_score/{v}/shard_{k:03d}.npz') for v in 'ab')
    secs = [json.loads(__import__('numpy').load(f, allow_pickle=True)['meta'].item())['seconds'] for f in glob.glob(f'{G}/raw/a24_score/a/shard_*.npz') + glob.glob(f'{G}/raw/a24_score/b/shard_*.npz')]
    per = (sum(secs) / max(1, len(secs))) * 2 if secs else 600; budget = 1.0
else:
    sh = sorted(pd.read_parquet(f'{G}/raw/a21_freeze/freeze.parquet').shard.unique())
    done = lambda k: os.path.exists(f'{G}/raw/a25/meta/shard_{k:03d}.json')
    secs = [json.load(open(f))['seconds'] for f in glob.glob(f'{G}/raw/a25/meta/shard_*.json')]
    per = (sum(secs) / max(1, len(secs))) if secs else 300; budget = 3.0
miss = [int(k) for k in sh if not done(k)]
proj = (per * len(miss) + 300 * ((len(miss) + 2) // 3)) / 3600
print(json.dumps(dict(n_shards=len(sh), missing=miss, sec_per_shard=per, projected_gpu_h=proj, budget=budget)))
EOF
OUTJ=$(EXP=$EXP $PY -c "$CODE"); echo "$(date -Is) round $round $OUTJ"
MISS=$(echo "$OUTJ" | $PY -c "import json,sys; print(' '.join(map(str, json.load(sys.stdin)['missing'])))")
PROJ=$(echo "$OUTJ" | $PY -c "import json,sys; d=json.load(sys.stdin); print(int(d['projected_gpu_h'] > d['budget']))")
if [ -z "$MISS" ]; then
  if [ "$EXP" = "a24" ]; then $PY $W/a24_rareword.py analyze; else $PY $W/a25_probeinject.py analyze; fi
  echo "ANALYSIS DONE $EXP"; exit 0
fi
if [ "$PROJ" = "1" ]; then echo "STOP: projected GPU-h above budget"; exit 1; fi
if [ $round -gt 4 ]; then echo "STOP: still missing after 4 rounds"; exit 1; fi
PER=6; [ "$EXP" = "a24" ] && PER=12
set -- $MISS; deps=""; n=0
while [ $# -gt 0 ] && [ $n -lt 2 ]; do
  s="$1"; shift; c=1; while [ $# -gt 0 ] && [ $c -lt $PER ]; do s="$s,$1"; shift; c=$((c+1)); done
  j=$(SHARDS=$s sbatch --parsable --export=ALL $W/${EXP}_gpu.sbatch) || { echo "STOP: sbatch failed ($s); check squeue/sacct"; exit 1; }
  echo "submitted $s -> $j"; deps="$deps:$j"; n=$((n+1))
done
g=$(EXP=$EXP sbatch --parsable --export=ALL --dependency=afterany$deps $W/gate.sbatch) || { echo "STOP: gate requeue failed"; exit 1; }
echo "gate requeued -> $g"
