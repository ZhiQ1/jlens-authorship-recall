#!/bin/bash
# Stage 11 analysis gate (CPU): waits until every unit exists, then runs the analysis. Resubmits itself near the limit (<= 4 rounds).
#SBATCH --job-name=s11_analyze
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --time=1-23:50:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --signal=B:USR1@600
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/361_stage11/logs/analyze_%j.log
ROUND=${ROUND:-1}; D=~/jlens_work/11_stage11; export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1
trap '[ "$ROUND" -lt 4 ] && sbatch --export=ALL,ROUND=$((ROUND+1)) $D/stage11_analyze.sbatch; exit 0' USR1
while true; do
  out=$(~/conda-envs/jlens/bin/python $D/361_stage11.py remaining 2>&1 | tail -1); echo "$(date -Is) $out"
  case "$out" in 0\ of*) break;; esac
  sleep 600 & wait $!
done
~/conda-envs/jlens/bin/python -u $D/361_stage11.py analyze
