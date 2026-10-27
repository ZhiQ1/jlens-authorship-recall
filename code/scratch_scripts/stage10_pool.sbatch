#!/bin/bash
# Stage 10 queue pool dispatcher (CPU, see stage10_pool.py). Resubmits itself at the time limit, at most 6 rounds.
#   sbatch --export=ALL,EXT_PARITY=<jobid> stage10_pool.sbatch
#SBATCH --job-name=s10_pool
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=1-23:50:00
#SBATCH --signal=B:USR1@600
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/pool/dispatcher_%j.log
ROUND=${ROUND:-1}; DIR=~/jlens_work/10_stage10
export PYTHONDONTWRITEBYTECODE=1
resubmit() {
  kill $PID 2>/dev/null; wait $PID 2>/dev/null   # stop this dispatcher before the next one starts
  echo handover > /scratch/$USER/jlens/351_stage10/logs/pool/dispatcher.lock
  if [ "$ROUND" -ge 6 ]; then echo "STOP: 6 rounds"; exit 1; fi
  sbatch --export=ALL,ROUND=$((ROUND+1)),EXT_PARITY=$EXT_PARITY $DIR/stage10_pool.sbatch; exit 0
}
trap resubmit USR1
~/conda-envs/jlens/bin/python -u $DIR/stage10_pool.py &
PID=$!; wait $PID; exit $?
