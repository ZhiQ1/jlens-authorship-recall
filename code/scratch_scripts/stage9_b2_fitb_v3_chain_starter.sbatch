#!/bin/bash
#SBATCH -J b2c_fitb3start
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 1-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v3_starter_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# CPU helper (2026-11-09): submits the FIRST (or, when a chain job could not resubmit itself, the NEXT) 2-1 chain job (stage9_b2_fitb_v3_chain.sbatch) as soon as the GPU QOS submit cap (8)
# has a free slot. GATE=<gate job id>. While the gate is pending/running -> --dependency=afterok:GATE. If the gate already ended:
# submit (no dependency) only if it COMPLETED and summary/gate_v2.json is PASS; otherwise stop, nothing runs.
# GATE may also be the previous chain job (ROUND/PHASE/STALL are passed through the environment with --export=ALL).
# After every sbatch error: check squeue for an already queued chain job before trying again. Polls every 2 min, gives up after 23 h.
GATE=${GATE:?set GATE}; D=~/jlens_work/09_stage9; ROOT=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb; CLOG=$ROOT/chain_v3.log
note() { echo "$(date -Is) starter=$SLURM_JOB_ID $*" | tee -a $CLOG; }
note "start, gate=$GATE round=${ROUND:-} phase=${PHASE:-} stall=${STALL:-}"
for i in $(seq 1 690); do
  if [ -n "$(squeue -h -u $USER -n b2c_fitb3chain -o %i 2>/dev/null | grep -v "^$GATE$")" ]; then note "a chain job is already queued: done"; exit 0; fi
  GS=$(squeue -h -j $GATE -o %T 2>/dev/null)
  if [ -n "$GS" ]; then DEP="--dependency=afterok:$GATE"
  else
    GS=$(sacct -n -X -j $GATE -o State -P 2>/dev/null | head -1)
    case "$GS" in
      COMPLETED) G=$(~/conda-envs/jlens/bin/python -c "import json;print(json.load(open('$ROOT/summary/gate_v2.json'))['status'])" 2>/dev/null)
                 if [ "$G" != "PASS" ]; then note "STOP: gate COMPLETED but gate_v2.json status='$G'"; exit 3; fi; DEP="" ;;
      PENDING|RUNNING|"") sleep 120; continue ;;            # squeue/sacct hiccup: retry
      *) note "STOP: gate job $GATE ended $GS - nothing else runs"; exit 3 ;;
    esac
  fi
  J=$(sbatch --parsable --export=ALL $DEP $D/stage9_b2_fitb_v3_chain.sbatch 2>&1)
  if [[ "$J" =~ ^[0-9]+$ ]]; then note "first chain job $J submitted ($DEP)"; exit 0; fi
  [ $((i % 15)) -eq 1 ] && note "sbatch refused (gate $GS): $(echo $J | tr '\n' ' ' | cut -c1-120)"
  sleep 120
done
note "STOP: no free GPU submit slot within 23 h"; exit 4
