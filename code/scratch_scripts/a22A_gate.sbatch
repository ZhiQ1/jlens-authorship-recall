#!/bin/bash
#SBATCH -J a22A_gate
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a22A/gate_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 22 Part A gate (written rule): runs afterany on the GPU jobs. Missing shards = the FREEZE's full shard list
# (a22_partA.py remaining) minus done markers. None missing -> run the analysis. Otherwise resubmit missing shards
# (3 per GPU job, at most 7 jobs) and requeue itself afterany on them; at most 4 rounds; round 5 or sbatch failure -> stop.
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
D=/scratch/zhang.zhiqi2/jlens/391_groups; ST=$D/logs/a22A/gate_state.txt; W=~/jlens_work/17_ladder; PY=~/conda-envs/jlens/bin/python
round=$(cat $ST 2>/dev/null || echo 0); round=$((round+1)); echo $round > $ST
miss=$($PY $W/a22_partA.py remaining | tail -1)
IFS=',' read -ra missing <<< "$miss"
echo "$(date -Is) round $round missing ${#missing[@]}: ${miss:-none}"
if [ -z "$miss" ]; then
  $PY $W/a22_partA_analyze.py && echo "ANALYSIS DONE $D/summary_a22_partA"; exit $?
fi
if [ $round -gt 4 ]; then echo "STOP: still missing after 4 rounds"; exit 1; fi
deps=""
for ((i=0; i<${#missing[@]}; i+=3)); do
  s=$(IFS=,; echo "${missing[*]:i:3}")
  if [ $(( (i/3) % 2 )) -eq 0 ]; then SB=$W/a22A_gpu_h200.sbatch; else SB=$W/a22A_gpu.sbatch; fi   # alternate H200 / A100-80GB
  j=$(SHARDS=$s sbatch --parsable --export=ALL $SB) || { echo "STOP: sbatch failed for $s (check squeue/sacct)"; exit 1; }
  echo "submitted $s -> $j"; deps="$deps:$j"
  [ $(( i/3 + 1 )) -ge 7 ] && break
done
g=$(sbatch --parsable --dependency=afterany$deps $W/a22A_gate.sbatch) || { echo "STOP: gate requeue failed"; exit 1; }
echo "gate requeued -> $g"
