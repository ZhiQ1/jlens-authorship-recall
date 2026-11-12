#!/bin/bash
#SBATCH -J b2c_fitb4chain
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH --kill-on-invalid-dep=yes
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v4_chain_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Item 2-1 continuation under the locked D12-5 record + v4 gate PASS (from stage9_b2_fitb_v3c_chain.sbatch; root 381_stage13/b2_fitb_d125,
# all work via stage9_b2_fitb_v4.py = unchanged v2/v1 code with --root). Started/resubmitted by stage9_b2_fitb_v4_watch.py.
# Each job: (1) require `stage9_b2_fitb_v4.py verify` (record locked + sha256, gate files unchanged); (2) ask `status`;
#   resume            -> stage9_b2_fitb_v2.py gpu --unit resume   (frozen Stage 9 command, skips finished prompts via checkpoint)
#   holdout_and_rest  -> stage9_b2_fitb_v2.py gpu --all           (holdout + 168 read units, skip-if-exists, claims)
#   analyze           -> submit stage9_b2_fitb_v2_analyze.sbatch (CPU, writes the item report) and end the chain
#   done              -> end; anything else (failed/gate/wait) -> stop (exit 3)
# Stop on: python exit != 0 (crash or hard check), 12 rounds in the same phase, a round without progress twice in a row.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/09_stage9; ROOT=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_fitb_d125
CLOG=$ROOT/chain_v4.log; ROUND=${ROUND:-1}; PHASE=${PHASE:-}; STALL=${STALL:-0}; CAP=12
cd $D
note() { echo "$(date -Is) job=$SLURM_JOB_ID round=$ROUND $*" | tee -a $CLOG; }
note "start on $(hostname) phase_in=${PHASE:-none} stall=$STALL limit=$(squeue -h -j $SLURM_JOB_ID -o %l 2>/dev/null)"
V=$($PY $D/stage9_b2_fitb_v4.py verify 2>&1 | tail -1)
if [[ "$V" != "VERIFY True"* ]]; then note "STOP: $V"; exit 3; fi
st() { $PY $D/stage9_b2_fitb_v4.py status 2>/dev/null | tail -1; }
S0=$(st); NXT=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['next'])" "$S0" 2>/dev/null); P0=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['progress'])" "$S0" 2>/dev/null)
note "status $S0"
case "$NXT" in
  resume)           A="--unit resume" ;;
  holdout_and_rest) A="--all" ;;
  analyze)          J=$(sbatch --parsable $D/stage9_b2_fitb_v4_analyze.sbatch 2>&1); note "GPU work complete; analyze job: $J"; exit 0 ;;
  done)             note "2-1 done"; exit 0 ;;
  *)                note "STOP: next step '$NXT' not handled by the chain"; exit 3 ;;
esac
[ "$NXT" != "$PHASE" ] && { ROUND=1; STALL=0; }
if [ "$ROUND" -gt "$CAP" ]; then note "STOP: $CAP rounds in phase $NXT reached"; exit 3; fi
$PY -u $D/stage9_b2_fitb_v4.py gpu $A --minutes 42; RC=$?
S1=$(st); P1=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['progress'])" "$S1" 2>/dev/null); N1=$($PY -c "import json,sys;print(json.loads(sys.argv[1])['next'])" "$S1" 2>/dev/null)
note "phase $NXT rc=$RC progress $P0 -> $P1 next=$N1"
if [ $RC -ne 0 ]; then note "STOP: python exit $RC (crash or hard check)"; exit $RC; fi
if [ "$P1" = "$P0" ] && [ "$N1" = "$NXT" ]; then STALL=$((STALL+1)); else STALL=0; fi
if [ $STALL -ge 2 ]; then note "STOP: no progress in 2 consecutive rounds"; exit 3; fi
case "$N1" in resume|holdout_and_rest|analyze|done) ;; *) note "STOP: next step '$N1' after this round"; exit 3 ;; esac
NR=$ROUND; [ "$N1" = "$NXT" ] && NR=$((ROUND+1)) || NR=1
KG=~/jlens_work/killguard.py
for t in 1 2 3; do
  EX=$($PY $KG exclude --name b2c_fitb4chain --minutes 45 --ignore $SLURM_JOB_ID 2>/dev/null); [ "$EX" = DEFER ] && EX=""
  J=$(sbatch --parsable $EX --dependency=afterok:$SLURM_JOB_ID --export=ALL,ROUND=$NR,PHASE=$N1,STALL=$STALL $D/stage9_b2_fitb_v4_chain.sbatch 2>&1)
  [[ "$J" =~ ^[0-9]+$ ]] && $PY $KG record --jid $J --name b2c_fitb4chain --unit "2-1:v4chain:$N1:round$NR" --orch fitb_v4 --excl "$EX" 2>/dev/null
  if [[ "$J" =~ ^[0-9]+$ ]]; then note "next chain job $J (round $NR, phase $N1)"; exit 0; fi
  note "sbatch error: $J"; sleep 60
  Q=$(squeue -h -u $USER -n b2c_fitb4chain -o %i 2>/dev/null | grep -v "^$SLURM_JOB_ID$")
  if [ -n "$Q" ]; then note "a chain job is already queued ($Q): not resubmitting"; exit 0; fi
done
note "HANDOFF round=$NR phase=$N1 stall=$STALL (GPU submit refused 3 times; the watchdog submits it)"; exit 0
