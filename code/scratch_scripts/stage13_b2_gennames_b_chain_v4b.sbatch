#!/bin/bash
#SBATCH -J b2gnb_chain4b
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 47:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_chain4b_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b chain v4b (2026-11-09) = v4 with GPU jobs on the hash runner (gpu_multi_v3.sbatch: run id + gen hash in every per-shard file) and the analysis behind the verify step (analyze_verified.sbatch). v4 = v3 + no double run on a failed squeue: if squeue for a group (or the active count) fails,
# that group is skipped this round instead of being treated as "nothing queued" (v2/v3 hid squeue's exit code). Start like v3.
# --- v3 header follows ---
# 2-11b chain v3 (2026-11-09, killguard; continues chain v2 with the SAME state dir summary/chain2/, so all counters carry over).
# Changes vs v2 (everything else identical): (1) every group job gets --exclude of the nodes running our jobs (killguard.py; DEFER
# = no A100-80GB node free of our jobs -> that group waits a round; relaxed rule after 2 h); pending group jobs are re-pointed
# each round (killguard refresh, ledger ids only); (2) signal-9 kills capped per group at 3 (v2: 6, whole chain stopped): a
# group killed a 4th time is STOPPED alone (summary/chain2/gN.stopped + a line in review_queue.md), the other groups continue;
# the analysis is submitted only when all 48 shards exist; (3) every round, a queued b2gnb_gN job missing from gN.jobs is adopted
# into it (v2 lost g1 job 11760447 after an "Unexpected message" sbatch error). Start: sbatch --dependency=afterany:<v2 job> this.sbatch <v2 job id>; it
# runs only if v2 ended TIMEOUT / exit 4 / exit 5 / CANCELLED (exit 0 = done, 2/3 = v2 stop rules -> v3 exits at once).
# --- v2 header follows ---
# 2-11b chain v2 (replaces stage13_b2_gennames_b_chain.sbatch, whose jobs ran only the first shard of each group because the shard
# list went through --export and sbatch split it on commas). Shard list now passed as the job-script ARGUMENT of
# stage13_b2_gennames_b_gpu_multi_v2.sbatch; only the still-missing shards of a group are passed. Groups g1..g8 as before
# (job names b2gnb_g1..g8, so an older pending b2gnb_gN job blocks a new one for that group: no double run).
# At most 2 b2gnb_g* jobs pending/running. Stops on HARD_CHECK_FAILED or a group job ending FAILED/OOM/CANCELLED/NODE_FAIL with
# an exit code other than signal 9; signal-9 endings (x:9, epilog pkill, HANDOFF "Cluster gotchas") = infrastructure: resubmit,
# counted in gN.infra (<= 6 per group). <= 4 normal jobs per group. After an sbatch error: squeue/sacct check, accept only ids not
# already recorded. When all 48 shards exist: submits the analysis once, exits. State in summary/chain2/ (safe to rerun).
R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b; ST=$R/summary/chain2; mkdir -p $ST
GPU=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi_v3.sbatch
ANA=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_analyze_verified.sbatch
MAXACTIVE=2; MAXSUB=4; MAXINFRA=3; KG=/home/zhang.zhiqi2/jlens_work/killguard.py; PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; SLEEP=${SLEEP:-600}; ROUNDS=${ROUNDS:-270}
grp() { local g=$1; local s=$(( (g-1)*6+1 )); local e=$(( s+5 )); [ $e -gt 47 ] && e=47; seq $s $e; }
missing_list() { local out=""; for k in $(grp $1); do [ -f $R/raw/shard_$(printf %03d $k).npz ] || out="$out,$k"; done; echo ${out#,}; }
active() { local o; o=$(squeue -u zhang.zhiqi2 -h -o %j 2>/dev/null) || { echo 99; return; }; echo "$o" | grep -c '^b2gnb_g[0-9]$'; }
qgrp() { local i o; for i in 1 2 3; do o=$(squeue -u zhang.zhiqi2 -h -n b2gnb_g$1 -o %i 2>/dev/null) && { echo "$o"; return 0; }; sleep 20; done; return 1; }
log() { echo "$(date -Is) $*"; }
V2=$1
if [ -n "$V2" ]; then
  r=$(sacct -j $V2 -X -n -P -o State,ExitCode 2>/dev/null | head -1); s2=${r%%|*}; e2=${r##*|}; e2=${e2%%:*}
  case "$s2" in TIMEOUT*|CANCELLED*) ;; FAILED*) case "$e2" in 4|5) ;; *) log "chain v2 $V2 ended $r: its stop rule stands, v3 exits"; exit 0;; esac;;
    COMPLETED*) log "chain v2 $V2 ended $r (done): v3 exits"; exit 0;; *) log "chain v2 $V2 state '$r': v3 exits"; exit 0;; esac
  log "chain v2 $V2 ended $r: v3 takes over (state $ST)"
fi
for round in $(seq 1 $ROUNDS); do
  [ -f $R/HARD_CHECK_FAILED ] && { log "HARD_CHECK_FAILED present: stop"; exit 2; }
  for g in 1 2 3 4 5 6 7 8; do
    [ -f $ST/g$g.jobs ] || continue
    for j in $(cat $ST/g$g.jobs); do
      grep -qx "$j" $ST/g$g.seen 2>/dev/null && continue
      r=$(sacct -j $j -X -n -P -o State,ExitCode 2>/dev/null | head -1); s=${r%%|*}; ec=${r##*|}
      case "$s" in ""|PENDING|RUNNING|REQUEUED|CONFIGURING|COMPLETING) continue;; esac
      echo $j >> $ST/g$g.seen
      case "$s" in
        COMPLETED|TIMEOUT) log "job $j (g$g) ended $s $ec";;
        *) if [ "${ec##*:}" = 9 ]; then log "job $j (g$g) ended $s $ec: infrastructure kill (signal 9), resubmit"; echo $j >> $ST/g$g.infra
           else log "job $j (g$g) ended $s $ec: real failure: stop"; exit 3; fi;;
      esac
    done
  done
  for m in $($PY $KG refresh 2>/dev/null | tr ' ' '_'); do log "killguard refresh: $m"; done
  todo=0; nstop=0
  for g in 1 2 3 4 5 6 7 8; do
    S=$(missing_list $g); [ -z "$S" ] && continue; todo=$((todo+1))
    [ -f $ST/g$g.stopped ] && { nstop=$((nstop+1)); continue; }
    QG=$(qgrp $g) || { log "round $round g$g: squeue failed 3x - group skipped this round (no double run)"; continue; }
    for q in $QG; do
      [ -f $ST/g$g.jobs ] && grep -qx "$q" $ST/g$g.jobs && continue; log "g$g: adopting queued job $q (not in g$g.jobs)"; echo $q >> $ST/g$g.jobs; done
    q=$(echo "$QG" | head -1); [ -n "$q" ] && continue
    ntot=$(cat $ST/g$g.jobs 2>/dev/null | wc -w); ninf=$(cat $ST/g$g.infra 2>/dev/null | wc -w); nsub=$((ntot-ninf))
    [ $nsub -ge $MAXSUB ] && { log "group g$g still missing $S after $nsub normal jobs: stop"; exit 4; }
    if [ $ninf -gt $MAXINFRA ]; then
      log "group g$g: $ninf signal-9 kills (> $MAXINFRA): group STOPPED, other groups continue"; date -Is > $ST/g$g.stopped
      $PY $KG review --orch b2gnb_chain3 --unit "2-11b:g$g" --msg "group g$g (shards $S still missing) jobs $(cat $ST/g$g.infra | tr '\n' ' ')" 2>/dev/null
      nstop=$((nstop+1)); continue
    fi
    [ $(active) -ge $MAXACTIVE ] && continue
    EX=$($PY $KG exclude --name b2gnb_g$g --minutes 45 2>/dev/null)
    [ "$EX" = DEFER ] && { log "round $round g$g: killguard DEFER (no A100-80GB node free of our jobs)"; continue; }
    o=$(sbatch -J b2gnb_g$g $EX $GPU "$S" 2>&1); log "round $round g$g shards $S ${EX:-(no exclude)}: $o"
    case "$o" in Submitted*) J=$(echo $o | awk '{print $4}'); echo $J >> $ST/g$g.jobs; $PY $KG record --jid $J --name b2gnb_g$g --unit "2-11b:g$g" --orch b2gnb_chain3 --excl "$EX" 2>/dev/null; continue;; esac
    sleep 30
    for q in $(squeue -u zhang.zhiqi2 -h -n b2gnb_g$g -o %i 2>/dev/null) $(sacct -u zhang.zhiqi2 -X -n -S now-10minutes --name=b2gnb_g$g -o JobID 2>/dev/null); do
      q=$(echo $q | tr -d ' '); [ -f $ST/g$g.jobs ] && grep -qx "$q" $ST/g$g.jobs && continue
      [ "$(sacct -j $q -X -n -o Submit -P 2>/dev/null | head -1)" \< "$(date -d '-15 minutes' +%Y-%m-%dT%H:%M:%S)" ] && continue
      log "g$g submitted despite error: $q"; echo $q >> $ST/g$g.jobs; break
    done
  done
  if [ $todo -gt 0 ] && [ $todo -eq $nstop ] && [ $(active) -eq 0 ]; then log "only STOPPED groups left ($nstop): no analysis; chain ends"; exit 4; fi
  if [ $todo -eq 0 ]; then
    if [ ! -s $ST/analyze.jobs ]; then
      q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_analyze -o %i | head -1)
      if [ -z "$q" ]; then o=$(sbatch $ANA 2>&1); log "all 48 shards present; analysis: $o"
        case "$o" in Submitted*) echo $o | awk '{print $4}' > $ST/analyze.jobs;; *) sleep 30; q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_analyze -o %i | head -1); [ -n "$q" ] && echo $q > $ST/analyze.jobs;; esac
      else echo $q > $ST/analyze.jobs; fi
    fi
    [ -s $ST/analyze.jobs ] && { log "analysis job $(cat $ST/analyze.jobs) submitted: chain done"; exit 0; }
  fi
  log "round $round: groups with missing shards $todo, active $(active)"
  sleep $SLEEP
done
log "$ROUNDS rounds reached: stop"; exit 5
