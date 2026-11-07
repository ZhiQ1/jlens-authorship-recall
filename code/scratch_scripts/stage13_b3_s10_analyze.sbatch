#!/bin/bash
#SBATCH -J b3s10_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 03:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_s10_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 items 3-1 / 3-2 analysis (CPU): full hard check on all 504 units (exit 3 = FAIL) + report reports/b3_3_<n>_report.md.
#   ITEM=3-1|3-2. NEXT_GATE=1 with ITEM=3-1: on PASS submit the 3-2 gate job (plan: 3-2 after 3-1).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
ITEM=${ITEM:-3-1}
$PY -u stage13_b3_s10_analyze.py --item "$ITEM"
rc=$?
echo "analyze exit $rc (0 PASS, 2 incomplete, 3 hard check FAILED)"
if [ $rc -eq 0 ] && [ "$ITEM" = "3-1" ] && [ "${NEXT_GATE:-0}" = "1" ]; then
  sbatch --export=ALL,ITEM=3-2,MODE=gate stage13_b3_s10_gpu.sbatch || { echo "sbatch error; squeue:"; squeue -u zhang.zhiqi2 -o '%i %j %T' || true; }
fi
exit $rc
