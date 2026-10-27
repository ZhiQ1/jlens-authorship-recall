#!/bin/bash
# Stage 10 main-worker gate (CPU): the gpu partition is at its 8-job submit limit, so wait for free slots and submit
# s10_w0 / s10_w1 (afterok on parity P while it is queued). Checks every 30 s; stops after 2 days (FAIL mail) or if
# parity P failed.
#   sbatch --export=ALL,P=<parity job id> stage10_main_gate.sbatch
#SBATCH --job-name=s10_main_gate
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=1-23:50:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/main_gate_%j.log
DIR=~/jlens_work/10_stage10; ROOT=/scratch/$USER/jlens/351_stage10
todo="0-35:s10_w0 36-71:s10_w1"
while [ -n "$todo" ]; do
  st=$(sacct -j $P -n -X -o State 2>/dev/null | head -1 | tr -d ' ')
  case "$st" in FAILED*|CANCEL*|TIMEOUT*|OUT_OF*|NODE_FAIL*) echo "$(date -Is) STOP: parity $P $st"; exit 1;; esac
  dep=""; [ "$st" != COMPLETED ] && dep="--dependency=afterok:$P"
  n=$(squeue -u $USER -p gpu -h 2>/dev/null | wc -l)
  if [ "$n" -lt 8 ]; then
    item=${todo%% *}; sh=${item%%:*}; name=${item##*:}
    if squeue -u $USER -n $name -h 2>/dev/null | grep -q .; then echo "$(date -Is) $name already queued"; todo=${todo#"$item"}; todo=${todo# }; continue; fi
    out=$(sbatch --parsable $dep --export=ALL,SHARDS=$sh --job-name=$name $DIR/stage10_worker.sbatch 2>&1)
    sleep 20
    if squeue -u $USER -n $name -h 2>/dev/null | grep -q .; then   # sbatch can report failure yet submit
      echo "$(date -Is) submitted $name shards $sh: $(squeue -u $USER -n $name -h -o %i)" | tee -a $ROOT/logs/chain_main_fix1.txt
      todo=${todo#"$item"}; todo=${todo# }
    else echo "$(date -Is) sbatch $name: $out"; fi
  fi
  sleep 30
done
echo "$(date -Is) both workers queued"
