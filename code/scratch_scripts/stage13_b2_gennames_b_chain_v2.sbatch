#!/bin/bash
#SBATCH -J b2gnb_chain2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 47:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_chain2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b chain v2 (replaces stage13_b2_gennames_b_chain.sbatch, whose jobs ran only the first shard of each group because the shard
# list went through --export and sbatch split it on commas). Shard list now passed as the job-script ARGUMENT of
# stage13_b2_gennames_b_gpu_multi_v2.sbatch; only the still-missing shards of a group are passed. Groups g1..g8 as before
# (job names b2gnb_g1..g8, so an older pending b2gnb_gN job blocks a new one for that group: no double run).
# At most 2 b2gnb_g* jobs pending/running. Stops on HARD_CHECK_FAILED or a group job ending FAILED/OOM/CANCELLED/NODE_FAIL with
# an exit code other than signal 9; signal-9 endings (x:9, epilog pkill, HANDOFF "Cluster gotchas") = infrastructure: resubmit,
# counted in gN.infra (<= 6 per group). <= 4 normal jobs per group. After an sbatch error: squeue/sacct check, accept only ids not
# already recorded. When all 48 shards exist: submits the analysis once, exits. State in summary/chain2/ (safe to rerun).
R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b; ST=$R/summary/chain2; mkdir -p $ST
GPU=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi_v2.sbatch
ANA=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_analyze.sbatch
MAXACTIVE=2; MAXSUB=4; MAXINFRA=6; SLEEP=${SLEEP:-600}; ROUNDS=${ROUNDS:-270}
grp() { local g=$1; local s=$(( (g-1)*6+1 )); local e=$(( s+5 )); [ $e -gt 47 ] && e=47; seq $s $e; }
missing_list() { local out=""; for k in $(grp $1); do [ -f $R/raw/shard_$(printf %03d $k).npz ] || out="$out,$k"; done; echo ${out#,}; }
active() { squeue -u zhang.zhiqi2 -h -o %j 2>/dev/null | grep -c '^b2gnb_g[0-9]$'; }
log() { echo "$(date -Is) $*"; }
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
  todo=0
  for g in 1 2 3 4 5 6 7 8; do
    S=$(missing_list $g); [ -z "$S" ] && continue; todo=$((todo+1))
    q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_g$g -o %i 2>/dev/null | head -1); [ -n "$q" ] && continue
    ntot=$(cat $ST/g$g.jobs 2>/dev/null | wc -w); ninf=$(cat $ST/g$g.infra 2>/dev/null | wc -w); nsub=$((ntot-ninf))
    [ $nsub -ge $MAXSUB ] && { log "group g$g still missing $S after $nsub normal jobs: stop"; exit 4; }
    [ $ninf -gt $MAXINFRA ] && { log "group g$g: $ninf infrastructure kills: stop"; exit 4; }
    [ $(active) -ge $MAXACTIVE ] && continue
    o=$(sbatch -J b2gnb_g$g $GPU "$S" 2>&1); log "round $round g$g shards $S: $o"
    case "$o" in Submitted*) echo $o | awk '{print $4}' >> $ST/g$g.jobs; continue;; esac
    sleep 30
    for q in $(squeue -u zhang.zhiqi2 -h -n b2gnb_g$g -o %i 2>/dev/null) $(sacct -u zhang.zhiqi2 -X -n -S now-10minutes --name=b2gnb_g$g -o JobID 2>/dev/null); do
      q=$(echo $q | tr -d ' '); grep -qx "$q" $ST/g$g.jobs 2>/dev/null && continue
      [ "$(sacct -j $q -X -n -o Submit -P 2>/dev/null | head -1)" \< "$(date -d '-15 minutes' +%Y-%m-%dT%H:%M:%S)" ] && continue
      log "g$g submitted despite error: $q"; echo $q >> $ST/g$g.jobs; break
    done
  done
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
