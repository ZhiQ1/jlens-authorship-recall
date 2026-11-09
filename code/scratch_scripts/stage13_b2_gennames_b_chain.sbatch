#!/bin/bash
#SBATCH -J b2gnb_chain
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 47:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_chain_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b chain: submits the 8 shard-group GPU jobs (b2gnb_g1..g8, 6 shards each, shards 1-47) keeping at most 2 of them
# pending/running; stops on HARD_CHECK_FAILED or any group job ending FAILED/OUT_OF_MEMORY/NODE_FAIL/CANCELLED (TIMEOUT = WARN,
# group resubmitted, at most 3 times per group); after all 48 shard files exist submits the CPU analysis (b2gnb_analyze) once
# and exits. Every attempt is logged; after an sbatch error it checks squeue/sacct before retrying. State in $ST (safe to rerun).
R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b; ST=$R/summary/chain; mkdir -p $ST
GPU=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi.sbatch
ANA=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_analyze.sbatch
MAXACTIVE=2; MAXSUB=4
grp() { local g=$1; local s=$(( (g-1)*6+1 )); local e=$(( s+5 )); [ $e -gt 47 ] && e=47; seq -s, $s $e; }
missing() { local n=0; for k in $(echo $1 | tr , ' '); do [ -f $R/raw/shard_$(printf %03d $k).npz ] || n=$((n+1)); done; echo $n; }
active() { squeue -u zhang.zhiqi2 -h -o %j 2>/dev/null | grep -c '^b2gnb_g[0-9]$'; }
log() { echo "$(date -Is) $*"; }
for round in $(seq 1 270); do
  [ -f $R/HARD_CHECK_FAILED ] && { log "HARD_CHECK_FAILED present: stop"; exit 2; }
  # inspect finished group jobs
  for f in $ST/g*.jobs; do
    [ -f "$f" ] || continue
    for j in $(cat $f); do
      s=$(sacct -j $j -X -n -o State 2>/dev/null | head -1 | tr -d ' ')
      case "$s" in FAILED|OUT_OF_ME*|NODE_FAIL|CANCELLED*|BOOT_FAIL|DEADLINE) log "job $j ($(basename $f .jobs)) ended $s: stop"; exit 3;; esac
    done
  done
  todo=0
  for g in 1 2 3 4 5 6 7 8; do
    S=$(grp $g); m=$(missing $S); [ $m -eq 0 ] && continue; todo=$((todo+1))
    q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_g$g -o %i 2>/dev/null | head -1); [ -n "$q" ] && continue
    nsub=$(cat $ST/g$g.jobs 2>/dev/null | wc -w)
    [ $nsub -ge $MAXSUB ] && { log "group g$g still missing $m shards after $nsub jobs: stop"; exit 4; }
    [ $(active) -ge $MAXACTIVE ] && continue
    o=$(sbatch -J b2gnb_g$g --export=ALL,SHARDS=$S $GPU 2>&1); log "round $round g$g shards $S: $o"
    case "$o" in Submitted*) echo $o | awk '{print $4}' >> $ST/g$g.jobs; continue;; esac
    sleep 30; q=$(squeue -u zhang.zhiqi2 -h -n b2gnb_g$g -o %i 2>/dev/null | head -1)
    [ -z "$q" ] && q=$(sacct -u zhang.zhiqi2 -X -n -S now-10minutes --name=b2gnb_g$g -o JobID 2>/dev/null | head -1 | tr -d ' ')
    if [ -n "$q" ]; then log "g$g submitted despite error: $q"; echo $q >> $ST/g$g.jobs; fi
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
  sleep 600
done
log "270 rounds reached: stop"; exit 5
