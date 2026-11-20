#!/bin/bash
#SBATCH -J h2fict_drv2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v2/logs/h2fict_drv2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# H2 fictitious v2 driver (CPU): for round 0..2: submit the GPU generation job (retry every 3 min while the GPU QOS
# submit limit is full; one GPU job at a time), wait for it, run the CPU check in this job; skip later rounds when
# no paper needs regeneration; then final selection + sample20 table. Resumable: finished rounds are skipped.
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
O=/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v2; P=~/conda-envs/jlens/bin/python
cd ~/jlens_work/15_h2fict
log(){ echo "[$(date '+%F %T')] $*"; }
for R in 0 1 2; do
  if [ -f $O/round${R}_status.csv ]; then log "round $R already checked"; continue; fi
  if [ $R -gt 0 ]; then
    need=$($P -c "import pandas as pd;print(int((pd.read_csv('$O/round$((R-1))_status.csv').n_ok==0).sum()))")
    log "round $R: $need papers need regeneration"
    if [ "$need" = "0" ]; then : > $O/candidates_r${R}.jsonl; $P h2fict_check_v2.py --round $R --out $O; continue; fi
  fi
  jid=""
  while [ -z "$jid" ]; do
    out=$(sbatch --parsable --export=ALL,ROUND=$R h2fict_gen_v2.sbatch 2>&1); rc=$?
    if [ $rc -eq 0 ] && [[ "$out" =~ ^[0-9]+ ]]; then jid=${out%%;*}; break; fi
    # sbatch error: check whether it was submitted anyway
    sleep 20; jid=$(squeue -u $USER -h -n h2fict_gen2 -o %i 2>/dev/null | head -1)
    [ -n "$jid" ] && break
    log "sbatch round $R not accepted ($out); retry in 3 min"; sleep 180
  done
  log "round $R GPU job $jid"
  echo "$(date '+%F %T') [H2 fictitious v2] round $R GPU job $jid submitted by driver" >> $O/jobs.txt
  while :; do
    st=$(sacct -j $jid -n -X -o State 2>/dev/null | head -1 | tr -d ' ')
    case "$st" in COMPLETED) break;; FAILED*|CANCELLED*|TIMEOUT*|OUT_OF_ME*|NODE_FAIL*) log "GPU job $jid ended $st; stopping"; exit 1;; esac
    sleep 60
  done
  log "round $R GPU done; checking"
  $P h2fict_check_v2.py --round $R --out $O || { log "check round $R crashed"; exit 1; }
done
$P h2fict_check_v2.py --final --out $O && $P h2fict_v2_sample20.py $O > /dev/null && log "final done"
