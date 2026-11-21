#!/bin/bash
#SBATCH -J a21_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a21/gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 21 gate (written rule): runs after the GPU jobs (afterany). If all 24 shard metas exist -> run the analysis.
# Otherwise resubmit the missing shards (3 per GPU job, at most 7 jobs so the 8-job QOS limit holds with this gate),
# then requeue itself afterany on them. At most 4 rounds; on round 5 or any sbatch failure it stops and mails.
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
D=/scratch/zhang.zhiqi2/jlens/391_groups; ST=$D/logs/a21/gate_state.txt; W=~/jlens_work/16_inject
round=$(cat $ST 2>/dev/null || echo 0); round=$((round+1)); echo $round > $ST
missing=(); for k in $(seq 0 23); do f=$(printf "$D/raw/a21/meta/shard_%03d.json" $k); [ -e "$f" ] || missing+=($k); done
echo "$(date -Is) round $round missing ${#missing[@]}: ${missing[*]:-none}"
if [ ${#missing[@]} -eq 0 ]; then
  ~/conda-envs/jlens/bin/python $W/inject_analyze.py --raw $D/raw/a21 --out $D/summary_a21 && echo "ANALYSIS DONE $D/summary_a21"
  exit $?
fi
if [ $round -gt 4 ]; then echo "STOP: still missing after 4 rounds"; exit 1; fi
deps=""
for ((i=0; i<${#missing[@]}; i+=3)); do
  s=$(IFS=,; echo "${missing[*]:i:3}")
  j=$(SHARDS=$s sbatch --parsable --export=ALL $W/inject_gpu.sbatch) || { echo "STOP: sbatch failed for $s (check squeue/sacct)"; exit 1; }
  echo "submitted $s -> $j"; deps="$deps:$j"
  [ $(( i/3 + 1 )) -ge 7 ] && break
done
g=$(sbatch --parsable --dependency=afterany$deps $W/a21_gate.sbatch) || { echo "STOP: gate requeue failed"; exit 1; }
echo "gate requeued -> $g"
