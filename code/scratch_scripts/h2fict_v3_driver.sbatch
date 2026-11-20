#!/bin/bash
#SBATCH -J h2fict_drv3
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 2-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v3/logs/h2fict_drv3_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# H2 fictitious v3 driver (CPU), Stage 11 subset (1,186). For round 0..2: submit the GPU job (retry every 3 min while the
# GPU QOS submit limit is full; one GPU job at a time; resubmit while papers of the round remain, max 6 jobs per round),
# then the CPU check here; later rounds only for papers without a passing candidate; then final + sample100 table.
# Resumable (finished rounds skipped). Crash or a GPU job ending other than COMPLETED -> stop (mail).
set -u
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false H2F_SAMPLE=s11
O=/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v3; P=~/conda-envs/jlens/bin/python
cd ~/jlens_work/15_h2fict
log(){ echo "[$(date '+%F %T')] $*"; }
remaining(){ $P - <<PY
import json, pandas as pd, sys
sys.path.insert(0, '.')
from h2fict_gen_v3 import todo_papers
from pathlib import Path
o = Path('$O'); r, _ = todo_papers(o, $1); f = o / 'candidates_r$1.jsonl'
done = {json.loads(l)['paper_id'] for l in f.open()} if f.exists() else set()
print(len(set(r.paper_id) - done))
PY
}
for R in 0 1 2; do
  if [ -f $O/round${R}_status.csv ]; then log "round $R already checked"; continue; fi
  n=0
  while :; do
    rem=$(remaining $R); log "round $R: $rem papers remaining"
    [ "$rem" = "0" ] && break
    n=$((n+1)); [ $n -gt 6 ] && { log "round $R: more than 6 GPU jobs; stopping"; exit 1; }
    jid=""
    while [ -z "$jid" ]; do
      out=$(sbatch --parsable --export=ALL,ROUND=$R,H2F_SAMPLE=s11 h2fict_gen_v3.sbatch 2>&1); rc=$?
      if [ $rc -eq 0 ] && [[ "$out" =~ ^[0-9]+ ]]; then jid=${out%%;*}; break; fi
      sleep 20; jid=$(squeue -u $USER -h -n h2fict_gen3 -o %i 2>/dev/null | head -1); [ -n "$jid" ] && break
      log "sbatch round $R not accepted (${out//$'\n'/ }); retry in 3 min"; sleep 180
    done
    log "round $R GPU job $jid"; echo "$(date '+%F %T') [H2 fictitious v3] round $R GPU job $jid" >> $O/jobs.txt
    while :; do
      st=$(sacct -j $jid -n -X -o State 2>/dev/null | head -1 | tr -d ' ')
      case "$st" in COMPLETED) break;; FAILED*|CANCELLED*|TIMEOUT*|OUT_OF_ME*|NODE_FAIL*) log "GPU job $jid ended $st"; [ "$st" = "TIMEOUT" ] && break; exit 1;; esac
      sleep 60
    done
  done
  log "round $R generation complete; checking"
  $P h2fict_check_v3.py --round $R --out $O || { log "check round $R crashed"; exit 1; }
done
$P h2fict_check_v3.py --final --out $O && $P h2fict_v3_sample100.py $O > /dev/null && log "final done"
