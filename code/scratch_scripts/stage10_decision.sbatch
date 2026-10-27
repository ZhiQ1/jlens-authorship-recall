#!/bin/bash
# Stage 10 release gate (CPU): ends OK as soon as reports/parity.json has overall status PASS. Every queued GPU chunk
# depends afterok on this job, so nothing reaches a GPU while the parity gate is FAIL (2026-10-25: all 20 queued jobs
# started at midnight and died at the gate). Gives up after ~2 days (exit 1; its dependents are then dropped).
#SBATCH --job-name=s10_decision
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=1-23:55:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/decision_%j.log
PR=/scratch/$USER/jlens/351_stage10/reports/parity.json
echo "$(date -Is) waiting for parity PASS"
while true; do
  st=$(~/conda-envs/jlens/bin/python -c "import json;print(json.load(open('$PR'))['status'])" 2>/dev/null)
  [ "$st" = PASS ] && { echo "$(date -Is) parity PASS - releasing"; exit 0; }
  sleep 60
done
