#!/bin/bash
#SBATCH -J b2gnb_confchain
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 30:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_conf_chain_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b POST-HOC confidence replay chain (事后，探索性). Step 1: GPU job for shard 0 only (gate). Step 2 (only if shard 0 replay
# agreement >= 0.99, i.e. no conf/REPLAY_STOP): GPU job(s) for the missing shards 1-47 (one job at a time, 45 min, runner budget).
# Step 3: CPU analysis once. Every GPU submission uses killguard --exclude (DEFER = wait a round) and is recorded in the ledger.
# Stops: REPLAY_STOP (exit 3 of a GPU job) -> stop + mail; a GPU job FAILED/CANCELLED with a code other than signal 9 -> stop;
# signal-9 endings = infrastructure kill: resubmit, counted with killguard kill (cap 3: 4th kill -> review line + stop);
# <= 6 normal GPU jobs. After an sbatch error: squeue/sacct check, accept only ids not yet recorded. State: conf/chain/.
R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b; ST=$R/conf/chain; mkdir -p $ST
GPU=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_conf_gpu.sbatch
ANA=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_conf_analyze.sbatch
KG=/home/zhang.zhiqi2/jlens_work/killguard.py; PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; ORCH=b2gnb_confchain; UNIT=2-11b-conf
SLEEP=${SLEEP:-300}; ROUNDS=${ROUNDS:-340}; MAXJOBS=6; NAME=b2gnb_conf
log() { echo "$(date -Is) $*"; }
done_k() { [ -f $R/conf/shard_$(printf %03d $1).parquet ] && [ -f $R/conf/replay_$(printf %03d $1).json ]; }
missing() { local out=""; for k in $(seq 1 47); do done_k $k || out="$out,$k"; done; echo ${out#,}; }
qname() { local i o; for i in 1 2 3; do o=$(squeue -u zhang.zhiqi2 -h -n $1 -o %i 2>/dev/null) && { echo "$o"; return 0; }; sleep 20; done; return 1; }
submit() {  # $1 = shard list
  local EX o q
  EX=$($PY $KG exclude --name $NAME --minutes 45 2>/dev/null)
  [ "$EX" = DEFER ] && { log "killguard DEFER for shards $1: wait"; return; }
  o=$(sbatch -J $NAME $EX $GPU "$1" 2>&1); log "submit shards $1 ${EX:-(no exclude)}: $o"
  case "$o" in Submitted*) q=$(echo $o | awk '{print $4}'); echo $q >> $ST/gpu.jobs; $PY $KG record --jid $q --name $NAME --unit $UNIT --orch $ORCH --excl "$EX" 2>/dev/null; return;; esac
  sleep 30
  for q in $(squeue -u zhang.zhiqi2 -h -n $NAME -o %i 2>/dev/null) $(sacct -u zhang.zhiqi2 -X -n -S now-10minutes --name=$NAME -o JobID 2>/dev/null); do
    q=$(echo $q | tr -d ' '); grep -qx "$q" $ST/gpu.jobs 2>/dev/null && continue
    log "submitted despite error: $q"; echo $q >> $ST/gpu.jobs; $PY $KG record --jid $q --name $NAME --unit $UNIT --orch $ORCH --excl "$EX" 2>/dev/null; break
  done
}
for round in $(seq 1 $ROUNDS); do
  [ -f $R/conf/REPLAY_STOP ] && { log "REPLAY_STOP present: replay check < 0.99 - stop (report to the coordinator)"; cat $R/conf/REPLAY_STOP; exit 3; }
  for j in $(cat $ST/gpu.jobs 2>/dev/null); do
    grep -qx "$j" $ST/seen 2>/dev/null && continue
    r=$(sacct -j $j -X -n -P -o State,ExitCode 2>/dev/null | head -1); s=${r%%|*}; ec=${r##*|}
    case "$s" in ""|PENDING|RUNNING|REQUEUED|CONFIGURING|COMPLETING) continue;; esac
    echo $j >> $ST/seen
    case "$s" in
      COMPLETED|TIMEOUT*) log "job $j ended $s $ec";;
      *) if [ "${ec##*:}" = 9 ]; then n=$($PY $KG kill --orch $ORCH --unit $UNIT --jid $j 2>/dev/null); log "job $j ended $s $ec: signal-9 kill #$n"; echo $j >> $ST/infra
           if [ "${n:-0}" -gt 3 ]; then $PY $KG review --orch $ORCH --unit $UNIT --msg "conf replay job $j: kill #$n" 2>/dev/null; log "kill cap reached: stop"; exit 4; fi
         elif [ "${ec%%:*}" = 3 ]; then log "job $j ended $s $ec: replay check stop"; exit 3
         else log "job $j ended $s $ec: real failure: stop"; exit 2; fi;;
    esac
  done
  QG=$(qname $NAME) || { log "round $round: squeue failed 3x - no submission this round"; sleep $SLEEP; continue; }
  if [ -z "$QG" ]; then
    ntot=$(cat $ST/gpu.jobs 2>/dev/null | wc -w); ninf=$(cat $ST/infra 2>/dev/null | wc -w)
    if ! done_k 0; then
      [ $((ntot-ninf)) -ge $MAXJOBS ] && { log "shard 0 not done after $ntot jobs: stop"; exit 5; }
      submit 0
    else
      M=$(missing)
      if [ -n "$M" ]; then
        [ $((ntot-ninf)) -ge $MAXJOBS ] && { log "shards $M still missing after $ntot jobs: stop"; exit 5; }
        submit "$M"
      else
        if [ ! -s $ST/analyze.jobs ]; then
          q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_confana -o %i | head -1)
          if [ -z "$q" ]; then o=$(sbatch $ANA 2>&1); log "all 48 conf shards done; analysis: $o"
            case "$o" in Submitted*) echo $o | awk '{print $4}' > $ST/analyze.jobs;; *) sleep 30; q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_confana -o %i | head -1); [ -n "$q" ] && echo $q > $ST/analyze.jobs;; esac
          else echo $q > $ST/analyze.jobs; fi
        fi
        [ -s $ST/analyze.jobs ] && { log "analysis job $(cat $ST/analyze.jobs) submitted: chain done"; exit 0; }
      fi
    fi
  fi
  for m in $($PY $KG refresh 2>/dev/null | tr ' ' '_'); do log "killguard refresh: $m"; done
  log "round $round: queued/running $NAME: ${QG:-none}; shard0 $(done_k 0 && echo done || echo missing); missing rest: $(missing | tr ',' ' ' | wc -w)"
  sleep $SLEEP
done
log "$ROUNDS rounds reached: stop"; exit 6
