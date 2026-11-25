#!/bin/bash
#SBATCH -J a23_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a23/gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 23 gate: shard list read from the freeze (not hard-coded). All markers present -> analysis. Otherwise resubmit
# missing shards (4 per GPU job, <= 7 jobs) and requeue itself afterany; at most 4 rounds, then stop and mail.
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
D=/scratch/zhang.zhiqi2/jlens/391_groups; ST=$D/logs/a23/gate_state.txt; W=~/jlens_work/18_h1lock; PY=~/conda-envs/jlens/bin/python
round=$(cat $ST 2>/dev/null || echo 0); round=$((round+1)); echo $round > $ST
missing=($($PY -c "import json,os;f=json.load(open('$D/raw/a23_freeze/freeze.json'));print(' '.join(str(k) for k in f['shards'] if not os.path.exists('$D/raw/a23/shard_%03d.json'%k)))"))
echo "$(date -Is) round $round missing ${#missing[@]}: ${missing[*]:-none}"
if [ ${#missing[@]} -eq 0 ]; then $PY $W/a23_h1lock.py analyze && echo "ANALYSIS DONE $D/summary_a23"; exit $?; fi
if [ $round -gt 4 ]; then echo "STOP: still missing after 4 rounds"; exit 1; fi
deps=""
for ((i=0; i<${#missing[@]}; i+=4)); do
  s=$(IFS=,; echo "${missing[*]:i:4}")
  j=$(SHARDS=$s sbatch --parsable --export=ALL $W/a23_gpu.sbatch) || { echo "STOP: sbatch failed for $s (check squeue/sacct)"; exit 1; }
  echo "submitted $s -> $j"; deps="$deps:$j"; [ $(( i/4 + 1 )) -ge 7 ] && break
done
g=$(sbatch --parsable --dependency=afterany$deps $W/a23_gate.sbatch) || { echo "STOP: gate requeue failed"; exit 1; }
echo "gate requeued -> $g"
