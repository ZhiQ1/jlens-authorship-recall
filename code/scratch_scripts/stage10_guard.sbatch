#!/bin/bash
# Stage 10 guard (CPU): alarm + pause when a GPU job ends within 2 minutes (see stage10_guard.py). Resubmits itself
# near the time limit, at most 6 rounds.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s10_guard
#SBATCH --time=1-23:50:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --signal=B:USR1@600
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/351_stage10/logs/pool/guard_%j.log
ROUND=${ROUND:-1}
DIR=~/jlens_work/10_stage10
handover() {
  kill $PID 2>/dev/null
  [ "$ROUND" -lt 6 ] && sbatch --export=ALL,ROUND=$((ROUND+1)) $DIR/stage10_guard.sbatch
  exit 0
}
trap handover USR1
~/conda-envs/jlens/bin/python -u $DIR/stage10_guard.py &
PID=$!
wait $PID
