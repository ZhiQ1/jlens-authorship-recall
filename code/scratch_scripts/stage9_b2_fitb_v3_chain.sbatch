#!/bin/bash
#SBATCH -J b2c_fitb3chain
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH --kill-on-invalid-dep=yes
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v3_chain_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Item 2-1 after the D12-1 gate (2026-11-09). Self-resubmitting chain, ONE job at a time, full 45 min (never --time-min).
# First job: sbatch --dependency=afterok:<gate job> stage9_b2_fitb_v3_chain.sbatch   (gate FAIL -> exit 2 -> dependency invalid ->
# Slurm removes this job: nothing else runs). The b2 orchestrator keeps 2-1 'stopped' (state.json), so it never submits 2-1.
# Each job: (1) require summary/gate_v2.json PASS and no HARD_CHECK_FAILED; (2) ask `status` for the next step;
#   resume            -> stage9_b2_fitb_v2.py gpu --unit resume   (frozen Stage 9 command, skips finished prompts via checkpoint)
#   holdout_and_rest  -> stage9_b2_fitb_v2.py gpu --all           (holdout + 168 read units, skip-if-exists, claims)
#   analyze           -> submit stage9_b2_fitb_v2_analyze.sbatch (CPU, writes the item report) and end the chain
#   done              -> end; anything else (failed/gate/wait) -> stop (exit 3)
# Stop on: python exit != 0 (crash or hard check), 12 rounds in the same phase, a round without progress twice in a row.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/09_stage9; ROOT=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb
CLOG=$ROOT/chain_v3.log; ROUND=${ROUND:-1}; PHASE=${PHASE:-}; STALL=${STALL:-0}; CAP=12
cd $D
note() { echo "$(date -Is) job=$SLURM_JOB_ID round=$ROUND $*" | tee -a $CLOG; }
note "start on $(hostname) phase_in=${PHASE:-none} stall=$STALL limit=$(squeue -h -j $SLURM_JOB_ID -o %l 2>/dev/null)"
G=$($PY -c "import json;print(json.load(open('$ROOT/summary/gate_v2.json'))['status'])" 2>/dev/null)
if [ "$G" != "PASS" ] || [ -e $ROOT/HARD_CHECK_FAILED ]; then note "STOP: gate_v2.json status='$G' or HARD_CHECK_FAILED present"; exit 3; fi
st() { $PY $D/stage9_b2_fitb_v2.py status 2>/dev/null | tail -1; }
S0=$(st); NXT=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['next'])" "$S0" 2>/dev/null); P0=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['progress'])" "$S0" 2>/dev/null)
note "status $S0"
case "$NXT" in
  resume)           A="--unit resume" ;;
  holdout_and_rest) A="--all" ;;
  analyze)          J=$(sbatch --parsable $D/stage9_b2_fitb_v2_analyze.sbatch 2>&1); note "GPU work complete; analyze job: $J"; exit 0 ;;
  done)             note "2-1 done"; exit 0 ;;
  *)                note "STOP: next step '$NXT' not handled by the chain"; exit 3 ;;
esac
[ "$NXT" != "$PHASE" ] && { ROUND=1; STALL=0; }
if [ "$ROUND" -gt "$CAP" ]; then note "STOP: $CAP rounds in phase $NXT reached"; exit 3; fi
$PY -u $D/stage9_b2_fitb_v2.py gpu $A --minutes 42; RC=$?
S1=$(st); P1=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['progress'])" "$S1" 2>/dev/null); N1=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['next'])" "$S1" 2>/dev/null)
note "phase $NXT rc=$RC progress $P0 -> $P1 next=$N1"
if [ $RC -ne 0 ]; then note "STOP: python exit $RC (crash or hard check)"; exit $RC; fi
if [ "$P1" = "$P0" ] && [ "$N1" = "$NXT" ]; then STALL=$((STALL+1)); else STALL=0; fi
if [ $STALL -ge 2 ]; then note "STOP: no progress in 2 consecutive rounds"; exit 3; fi
case "$N1" in resume|holdout_and_rest|analyze|done) ;; *) note "STOP: next step '$N1' after this round"; exit 3 ;; esac
NR=$ROUND; [ "$N1" = "$NXT" ] && NR=$((ROUND+1)) || NR=1
# 2026-11-09 killguard: --exclude the nodes of our other running jobs (this job is ignored: the successor starts after it ends);
# DEFER (no A100-80GB node free of our jobs) -> submit without --exclude here, the 2-1 watchdog's refresh re-points it while pending.
KG=~/jlens_work/killguard.py
for t in 1 2 3; do
  EX=$($PY $KG exclude --name b2c_fitb3chain --minutes 45 --ignore $SLURM_JOB_ID 2>/dev/null); [ "$EX" = DEFER ] && EX=""
  J=$(sbatch --parsable $EX --dependency=afterok:$SLURM_JOB_ID --export=ALL,ROUND=$NR,PHASE=$N1,STALL=$STALL $D/stage9_b2_fitb_v3_chain.sbatch 2>&1)
  [[ "$J" =~ ^[0-9]+$ ]] && $PY $KG record --jid $J --name b2c_fitb3chain --unit "2-1:chain:$N1:round$NR" --orch fitb_chain --excl "$EX" 2>/dev/null
  if [[ "$J" =~ ^[0-9]+$ ]]; then note "next chain job $J (round $NR, phase $N1)"; exit 0; fi
  note "sbatch error: $J"; sleep 60
  Q=$(squeue -h -u $USER -n b2c_fitb3chain -o %i 2>/dev/null | grep -v "^$SLURM_JOB_ID$")
  if [ -n "$Q" ]; then note "a chain job is already queued ($Q): not resubmitting"; exit 0; fi
done
H=$(sbatch --parsable --export=ALL,GATE=$SLURM_JOB_ID,ROUND=$NR,PHASE=$N1,STALL=$STALL $D/stage9_b2_fitb_v3_chain_starter.sbatch 2>&1)
note "GPU submit cap full after 3 tries: CPU starter $H will submit round $NR when a slot frees"; exit 0
