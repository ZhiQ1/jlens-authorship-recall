#!/bin/bash
# Stage 10 extension gate (CPU). Waits until the main round is fully done (all 7 conditions written, both analysis
# jobs finished OK), then submits ext parity and two ext workers (afterok). Rules:
#  - main analysis job FAILED -> stop and mail (do not start the extension);
#  - still waiting at the time limit -> resubmit itself, at most ROUND<=4 times, then stop and mail.
#SBATCH --job-name=s10x_wait
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=23:50:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/ext_wait_%j.log
ROUND=${ROUND:-1}
READOUTS=${READOUTS:-jlens_public,logit}; LAYERS=${LAYERS:-50,51,52,53,54,55,57,58,59,60,61}
ROOT=/scratch/$USER/jlens/351_stage10; DIR=~/jlens_work/10_stage10
PY=~/conda-envs/jlens/bin/python; S=$DIR/351_stage10.py
ALL=true,false_0,false_1,false_2,false_3,false_4,delete
mail_stop() { echo "STOP: $1"; echo "$1" | mail -s "s10x_wait stopped: $1" zhang.zhiqi2@northeastern.edu 2>/dev/null; exit 1; }
end=$(( $(date +%s) + 23*3600 + 20*60 ))
echo "$(date -Is) ext wait round $ROUND, then $READOUTS @ $LAYERS"
while [ $(date +%s) -lt $end ]; do
  left=$($PY $S remaining --condition $ALL 2>/dev/null || echo err)
  # state of the main analysis jobs (by name, newest first)
  st_main=$(sacct -u $USER -n -X -S 2026-10-23 --name=s10_analyze_main -o State 2>/dev/null | tail -1 | tr -d ' ')
  st_title=$(sacct -u $USER -n -X -S 2026-10-23 --name=s10_analyze_title -o State 2>/dev/null | tail -1 | tr -d ' ')
  echo "$(date -Is) main missing=$left analyze_main=${st_main:-none} analyze_title=${st_title:-none}"
  case "$st_main$st_title" in *FAIL*|*CANCEL*|*TIMEOUT*|*OUT_OF_ME*) mail_stop "main analysis job not OK ($st_main / $st_title)";; esac
  if [ "$left" = 0 ] && [ "$st_main" = COMPLETED ] && [ "$st_title" = COMPLETED ]; then
    p=$(sbatch --parsable --export=ALL,READOUTS=$READOUTS,LAYERS=$LAYERS $DIR/stage10_ext_parity.sbatch) || mail_stop "sbatch parity failed"
    w0=$(sbatch --parsable --dependency=afterok:$p --export=ALL,SHARDS=0-35,READOUTS=$READOUTS,LAYERS=$LAYERS --job-name=s10x_w0 $DIR/stage10_ext_worker.sbatch)
    w1=$(sbatch --parsable --dependency=afterok:$p --export=ALL,SHARDS=36-71,READOUTS=$READOUTS,LAYERS=$LAYERS --job-name=s10x_w1 $DIR/stage10_ext_worker.sbatch)
    echo "ext parity=$p worker0=$w0 worker1=$w1 readouts=$READOUTS layers=$LAYERS" | tee $ROOT/logs/chain_ext_$(date +%m%d_%H%M).txt
    exit 0
  fi
  sleep 1200
done
[ "$ROUND" -ge 4 ] && mail_stop "main round still not finished after $ROUND days"
sbatch --export=ALL,ROUND=$((ROUND+1)) $DIR/stage10_ext_wait.sbatch
